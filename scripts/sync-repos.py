#!/usr/bin/env python3
"""Fast-forward initialized child repositories to origin/main, then optionally pin them."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


class SyncError(RuntimeError):
    pass


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True,
    )
    if check and result.returncode:
        raise SyncError(f"{root.name}: git {' '.join(args)}\n{result.stderr.strip()}")
    return result


def modules(root: Path) -> list[tuple[str, Path]]:
    config = git(root, "config", "--file", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$")
    entries = []
    seen = set()
    for line in config.stdout.splitlines():
        key, relative = line.split(None, 1)
        name = key[len("submodule."):-len(".path")]
        target = root / relative
        # Only immediate child checkouts: never reach outside the collection or follow links.
        if target.is_symlink() or target.resolve().parent != root.resolve() or relative in seen:
            raise SyncError(f"Invalid or duplicate submodule path: {relative}")
        seen.add(relative)
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


def synchronize(root: Path, *, check_only: bool = False, commit: bool = False) -> bool:
    if check_only and commit:
        raise SyncError("--check and --commit cannot be combined")
    if commit:
        if git(root, "branch", "--show-current").stdout.strip() != "main":
            raise SyncError("Root must be on main to commit synchronized pointers")
        if git(root, "status", "--porcelain", "--ignore-submodules=all").stdout.strip():
            raise SyncError("Root has unrelated changes; commit them before --commit")
        if git(root, "diff", "--cached", "--name-only").stdout.strip():
            raise SyncError("Root index is not empty; refusing to include staged work")

    entries = modules(root)
    # Preflight every checkout before updating any working tree. No reset, clean, stash or force push.
    for _, path in entries:
        clean_child(path)
    updates = []
    for relative, path in entries:
        git(path, "fetch", "--no-tags", "origin", "+refs/heads/main:refs/remotes/origin/main")
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
            print(f"{relative}: {status} (main {target[:12]}, root pin {pinned[:12]})")
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
        print(f"{relative}: main @ {target[:12]}")

    if commit:
        git(root, "add", "--", *(relative for relative, _ in entries))
        changed = git(root, "diff", "--cached", "--name-only").stdout.strip()
        if changed:
            git(root, "commit", "-m", "chore: sync documentation repositories with main")
            print("Committed updated submodule pointers. Push root main when ready.")
        else:
            print("All submodule pointers are already current.")
    return bool(stale)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fetch/check tips without changing working trees; exit 1 if stale")
    mode.add_argument("--commit", action="store_true", help="sync and commit only root submodule pointer changes; never push")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        stale = synchronize(root, check_only=args.check, commit=args.commit)
        return 1 if args.check and stale else 0
    except SyncError as error:
        print(f"Sync stopped: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
