#!/usr/bin/env python3
"""Fast-forward initialized child repositories to origin/main, then optionally pin them."""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


DEFAULT_FETCH_TIMEOUT = 30.0


class SyncError(RuntimeError):
    pass


def git(
    root: Path, *args: str, check: bool = True, timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    command = ["git", "-C", str(root), *args]
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        start_new_session=os.name != "nt",
    )

    def stop() -> None:
        # Kill the transport/credential helper too, not just its parent Git process.
        try:
            if os.name == "nt":
                process.kill()
            else:
                os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()

    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop()
        raise SyncError(
            f"{root.name}: git {' '.join(args)} timed out after {timeout:g}s; "
            "check connectivity/authentication or increase --fetch-timeout."
        ) from None
    except BaseException:
        stop()
        raise
    result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if check and result.returncode:
        raise SyncError(f"{root.name}: git {' '.join(args)}\n{result.stderr.strip()}")
    return result


def modules(root: Path, repos: list[str] | None = None) -> list[tuple[str, Path]]:
    config = git(root, "config", "--file", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$")
    configured = []
    seen = set()
    for line in config.stdout.splitlines():
        key, relative = line.split(None, 1)
        name = key[len("submodule."):-len(".path")]
        target = root / relative
        # Only immediate child checkouts: never reach outside the collection or follow links.
        if target.is_symlink() or target.resolve().parent != root.resolve() or relative in seen:
            raise SyncError(f"Invalid or duplicate submodule path: {relative}")
        seen.add(relative)
        configured.append((name, relative, target))
    if repos is not None:
        if not repos:
            raise SyncError("Select at least one --repo, or omit --repo to sync all")
        unknown = set(repos) - seen
        if unknown:
            raise SyncError(f"Unknown repository path(s): {', '.join(sorted(unknown))}")
    selected = set(repos) if repos is not None else seen
    entries = []
    for name, relative, target in configured:
        if relative not in selected:
            continue
        branch = git(root, "config", "--file", ".gitmodules", "--get", f"submodule.{name}.branch").stdout.strip()
        if branch != "main":
            raise SyncError(f"{relative}: expected branch = main, found {branch!r}")
        if not (target / ".git").exists():
            raise SyncError(f"{relative}: not initialized; run git submodule update --init (without --recursive)")
        actual = Path(git(target, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
        if actual != target.resolve():
            raise SyncError(f"{relative}: not an independent Git checkout")
        entries.append((relative, target))
    return entries


def clean_child(path: Path) -> None:
    if git(path, "status", "--porcelain", "--untracked-files=normal").stdout.strip():
        raise SyncError(f"{path.name}: uncommitted changes; commit or stash explicitly before syncing")
    for state in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD"):
        state_path = Path(git(path, "rev-parse", "--git-path", state).stdout.strip())
        if not state_path.is_absolute():
            state_path = path / state_path
        if state_path.exists():
            raise SyncError(f"{path.name}: unfinished Git operation ({state})")
    branch = git(path, "branch", "--show-current").stdout.strip()
    if branch not in ("", "main"):
        raise SyncError(f"{path.name}: on branch {branch!r}; switch to main explicitly")


def synchronize(
    root: Path, *, check_only: bool = False, commit: bool = False,
    repos: list[str] | None = None, fetch_timeout: float = DEFAULT_FETCH_TIMEOUT,
) -> bool:
    if check_only and commit:
        raise SyncError("--check and --commit cannot be combined")
    if not math.isfinite(fetch_timeout) or fetch_timeout <= 0:
        raise SyncError("--fetch-timeout must be a positive finite number of seconds")
    if commit:
        if git(root, "branch", "--show-current").stdout.strip() != "main":
            raise SyncError("Root must be on main to commit synchronized pointers")
        if git(root, "status", "--porcelain", "--ignore-submodules=all").stdout.strip():
            raise SyncError("Root has unrelated changes; commit them before --commit")
        if git(root, "diff", "--cached", "--name-only").stdout.strip():
            raise SyncError("Root index is not empty; refusing to include staged work")

    entries = modules(root, repos)
    scope = "selected" if repos is not None else "all"
    print(f"Preflight: checking {len(entries)} {scope} repositories...", flush=True)
    # Check every selected checkout before updating any working tree. Unselected
    # repos are never fetched, switched, merged or staged. No reset/clean/stash.
    for _, path in entries:
        clean_child(path)
    updates = []
    for index, (relative, path) in enumerate(entries, 1):
        print(f"[{index}/{len(entries)}] {relative}: fetching origin/main (timeout {fetch_timeout:g}s)...", flush=True)
        started = time.monotonic()
        git(path, "fetch", "--no-tags", "--no-recurse-submodules", "origin",
            "+refs/heads/main:refs/remotes/origin/main", timeout=fetch_timeout)
        print(f"[{index}/{len(entries)}] {relative}: fetched in {time.monotonic() - started:.1f}s", flush=True)
        current = git(path, "rev-parse", "HEAD").stdout.strip()
        target = git(path, "rev-parse", "origin/main").stdout.strip()
        if current != target:
            ancestor = git(path, "merge-base", "--is-ancestor", current, target, check=False)
            if ancestor.returncode:
                raise SyncError(f"{relative}: local HEAD is ahead/diverged from origin/main; reconcile explicitly")
        local_main = git(path, "rev-parse", "--verify", "refs/heads/main", check=False)
        if local_main.returncode == 0 and local_main.stdout.strip() != current:
            raise SyncError(f"{relative}: local main differs from checkout HEAD; reconcile explicitly")
        pinned = git(root, "rev-parse", f"HEAD:{relative}").stdout.strip()
        updates.append((relative, path, current, target, pinned))

    stale = [relative for relative, _, current, target, pinned in updates if current != target or pinned != target]
    if check_only:
        for relative, _, current, target, pinned in updates:
            status = "STALE" if current != target or pinned != target else "OK"
            print(f"{relative}: {status} (main {target[:12]}, root pin {pinned[:12]})", flush=True)
        return bool(stale)

    for relative, path, current, target, _ in updates:
        if git(path, "branch", "--show-current").stdout.strip() != "main":
            local_main = git(path, "show-ref", "--verify", "--quiet", "refs/heads/main", check=False)
            if local_main.returncode == 0:
                git(path, "switch", "main")
            else:
                git(path, "switch", "--create", "main", "--track", "origin/main")
        if current != target:
            git(path, "merge", "--ff-only", target)
        print(f"{relative}: main @ {target[:12]}", flush=True)

    if commit:
        git(root, "add", "--", *(relative for relative, _ in entries))
        changed = git(root, "diff", "--cached", "--name-only").stdout.strip()
        if changed:
            git(root, "commit", "-m", "chore: sync documentation repositories with main")
            print("Committed updated submodule pointers. Push root main when ready.", flush=True)
        else:
            print("Selected submodule pointers are already current.", flush=True)
    return bool(stale)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fetch/check tips without changing working trees; exit 1 if stale")
    mode.add_argument("--commit", action="store_true", help="sync and commit only root submodule pointer changes; never push")
    parser.add_argument("--repo", action="append", metavar="PATH", help="sync only this immediate child path; repeat for multiple repos (default: all)")
    parser.add_argument("--fetch-timeout", type=float, default=DEFAULT_FETCH_TIMEOUT, metavar="SECONDS", help="timeout per fetch in seconds (default: %(default)g)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        stale = synchronize(root, check_only=args.check, commit=args.commit, repos=args.repo, fetch_timeout=args.fetch_timeout)
        return 1 if args.check and stale else 0
    except SyncError as error:
        print(f"Sync stopped: {error}", file=sys.stderr, flush=True)
        return 2
    except KeyboardInterrupt:
        print("Sync cancelled; no work was discarded. Check git status before retrying.", file=sys.stderr, flush=True)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
