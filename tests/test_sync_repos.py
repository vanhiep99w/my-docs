"""Offline integration tests: disposable local repositories, no GitHub access."""

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("sync_repos", Path(__file__).resolve().parents[1] / "scripts/sync-repos.py")
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


def git(path, *args):
    result = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def identity(path):
    git(path, "config", "user.name", "Sync Test")
    git(path, "config", "user.email", "sync-test@example.invalid")


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="my-docs-sync-test-")
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.remote = base / "remote.git"
        self.remote.mkdir()
        git(self.remote, "init", "--bare", "--initial-branch=main")
        self.producer = base / "producer"
        git(base, "clone", str(self.remote), str(self.producer))
        identity(self.producer)
        self.advance()
        self.root = base / "root"
        self.root.mkdir()
        git(self.root, "init", "--initial-branch=main")
        identity(self.root)
        # Fixture-only opt-in for file:// submodule transport.
        git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", "-b", "main", str(self.remote), "child")
        self.child = self.root / "child"
        identity(self.child)
        git(self.root, "commit", "-am", "Initial collection")

    def advance(self):
        content = self.producer / "lesson.md"
        content.write_text((content.read_text() if content.exists() else "") + "lesson\n")
        git(self.producer, "add", "lesson.md")
        git(self.producer, "commit", "-m", "Add lesson")
        git(self.producer, "push", "origin", "main")
        return git(self.producer, "rev-parse", "HEAD")

    def run_sync(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return sync.synchronize(self.root, **kwargs)

    def add_child(self, name="other"):
        git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", "-b", "main", str(self.remote), name)
        child = self.root / name
        identity(child)
        git(self.root, "commit", "-am", f"Add {name}")
        return child

    def test_check_reports_stale_without_changing_head_or_index(self):
        previous = git(self.child, "rev-parse", "HEAD")
        self.advance()
        self.assertTrue(self.run_sync(check_only=True))
        self.assertEqual(git(self.child, "rev-parse", "HEAD"), previous)
        self.assertEqual(git(self.root, "status", "--porcelain"), "")

    def test_sync_commits_exact_remote_tip_and_is_idempotent(self):
        target = self.advance()
        self.assertTrue(self.run_sync(commit=True))
        self.assertEqual(git(self.child, "rev-parse", "HEAD"), target)
        self.assertEqual(git(self.root, "rev-parse", "HEAD:child"), target)
        self.assertEqual(git(self.root, "status", "--porcelain"), "")
        root_tip = git(self.root, "rev-parse", "HEAD")
        self.assertFalse(self.run_sync(commit=True))
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), root_tip)

    def test_check_detects_stale_root_pin_even_when_child_is_current(self):
        target = self.advance()
        git(self.child, "pull", "--ff-only", "origin", "main")
        self.assertTrue(self.run_sync(check_only=True))
        self.assertNotEqual(git(self.root, "rev-parse", "HEAD:child"), target)
        self.assertTrue(self.run_sync(commit=True))
        self.assertEqual(git(self.root, "rev-parse", "HEAD:child"), target)

    def test_detached_submodule_returns_to_main(self):
        git(self.child, "checkout", "--detach")
        target = self.advance()
        self.run_sync()
        self.assertEqual(git(self.child, "branch", "--show-current"), "main")
        self.assertEqual(git(self.child, "rev-parse", "HEAD"), target)

    def test_refuses_dirty_child_without_discarding_work(self):
        self.advance()
        path = self.child / "lesson.md"
        path.write_text("local unfinished work\n")
        with self.assertRaisesRegex(sync.SyncError, "uncommitted changes"):
            self.run_sync()
        self.assertEqual(path.read_text(), "local unfinished work\n")

    def test_refuses_diverged_child_without_reset(self):
        (self.child / "local.md").write_text("local commit\n")
        git(self.child, "add", "local.md")
        git(self.child, "commit", "-m", "Local only")
        tip = git(self.child, "rev-parse", "HEAD")
        self.advance()
        with self.assertRaisesRegex(sync.SyncError, "ahead/diverged"):
            self.run_sync()
        self.assertEqual(git(self.child, "rev-parse", "HEAD"), tip)

    def test_refuses_unrelated_root_changes_when_committing(self):
        (self.root / "unrelated.md").write_text("do not commit\n")
        with self.assertRaisesRegex(sync.SyncError, "unrelated changes"):
            self.run_sync(commit=True)
        self.assertEqual(git(self.root, "diff", "--cached", "--name-only"), "")

    def test_refuses_wrong_branch(self):
        git(self.child, "switch", "-c", "work-in-progress")
        with self.assertRaisesRegex(sync.SyncError, "switch to main explicitly"):
            self.run_sync()

    def test_refuses_uninitialized_submodule(self):
        git(self.root, "submodule", "deinit", "-f", "child")
        with self.assertRaisesRegex(sync.SyncError, "not initialized"):
            self.run_sync()

    def test_scoped_commit_only_fetches_and_pins_selected_repo(self):
        other = self.add_child()
        other_pin = git(self.root, "rev-parse", "HEAD:other")
        (other / "local.md").write_text("local commit\n")
        git(other, "add", "local.md")
        git(other, "commit", "-m", "Unpushed work")
        other_tip = git(other, "rev-parse", "HEAD")
        (other / "lesson.md").write_text("unfinished work\n")
        git(other, "remote", "set-url", "origin", str(self.root / "unreachable.git"))
        target = self.advance()
        self.assertTrue(self.run_sync(repos=["child"], commit=True))
        self.assertEqual(git(self.root, "rev-parse", "HEAD:child"), target)
        self.assertEqual(git(self.root, "rev-parse", "HEAD:other"), other_pin)
        self.assertEqual(git(other, "rev-parse", "HEAD"), other_tip)
        self.assertEqual((other / "lesson.md").read_text(), "unfinished work\n")
        self.assertEqual(git(self.root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"), "child")
        self.assertEqual(git(self.root, "diff", "--cached", "--name-only"), "")

    def test_scoped_sync_ignores_uninitialized_unselected_repo(self):
        self.add_child()
        git(self.root, "submodule", "deinit", "-f", "other")
        target = self.advance()
        self.assertTrue(self.run_sync(repos=["child"], commit=True))
        self.assertEqual(git(self.root, "rev-parse", "HEAD:child"), target)
        with self.assertRaisesRegex(sync.SyncError, "not initialized"):
            self.run_sync()

    def test_unknown_or_empty_scope_fails_before_fetch(self):
        with patch.object(sync, "git", wraps=sync.git) as calls:
            for repos in (["missing"], [], ["../child"]):
                with self.subTest(repos=repos), self.assertRaises(sync.SyncError):
                    self.run_sync(repos=repos)
            self.assertFalse(any("fetch" in call.args for call in calls.call_args_list))

    def test_repeated_repo_selection_fetches_once_with_timeout_and_progress(self):
        output = io.StringIO()
        original = sync.git
        fetches = []

        def track(path, *args, **kwargs):
            if args[0] == "fetch":
                self.assertIn("[1/1] child: fetching origin/main (timeout 7s)", output.getvalue())
                self.assertIn("--no-recurse-submodules", args)
                self.assertEqual(kwargs["timeout"], 7)
                fetches.append(path)
            return original(path, *args, **kwargs)

        with patch.object(sync, "git", side_effect=track), contextlib.redirect_stdout(output):
            self.assertFalse(sync.synchronize(self.root, repos=["child", "child"], fetch_timeout=7))
        self.assertEqual(fetches, [self.child])
        self.assertIn("child: fetched in", output.getvalue())

    def test_selected_dirty_checkout_stops_before_any_fetch(self):
        other = self.add_child()
        (other / "lesson.md").write_text("unfinished work\n")
        with patch.object(sync, "git", wraps=sync.git) as calls:
            with self.assertRaisesRegex(sync.SyncError, "uncommitted changes"):
                self.run_sync(repos=["child", "other"])
            self.assertFalse(any("fetch" in call.args for call in calls.call_args_list))

    def test_failed_second_fetch_does_not_move_first_checkout_or_stage_pointers(self):
        other = self.add_child()
        previous = git(self.child, "rev-parse", "HEAD")
        self.advance()
        git(other, "remote", "set-url", "origin", str(self.root / "unreachable.git"))
        with self.assertRaisesRegex(sync.SyncError, "other: git fetch"):
            self.run_sync(repos=["child", "other"], commit=True)
        self.assertEqual(git(self.child, "rev-parse", "HEAD"), previous)
        self.assertEqual(git(self.root, "status", "--porcelain"), "")

    def test_invalid_fetch_timeout_is_rejected_before_git(self):
        with patch.object(sync, "git") as calls:
            for timeout in (0, -1, float("inf"), float("nan")):
                with self.subTest(timeout=timeout), self.assertRaisesRegex(sync.SyncError, "positive finite"):
                    self.run_sync(fetch_timeout=timeout)
            calls.assert_not_called()

    @unittest.skipIf(os.name == "nt", "POSIX shell and process-group cleanup")
    def test_timeout_stops_git_and_its_helper_even_with_check_false(self):
        sentinel = self.root / "helper-survived"
        alias = f"!sleep 0.5; echo survived > {shlex.quote(str(sentinel))}"
        started = time.monotonic()
        with self.assertRaisesRegex(sync.SyncError, "child: git .* timed out after 0.05s"):
            sync.git(self.child, "-c", f"alias.wait={alias}", "wait", timeout=0.05, check=False)
        self.assertLess(time.monotonic() - started, 2)
        time.sleep(0.6)
        self.assertFalse(sentinel.exists(), "Git's helper must not survive a timeout")

    def test_git_disables_interactive_credential_prompts(self):
        with patch.dict(os.environ, {"GIT_TERMINAL_PROMPT": "1"}), patch.object(sync.subprocess, "Popen", wraps=subprocess.Popen) as spawn:
            sync.git(self.child, "status", "--porcelain")
            self.assertEqual(spawn.call_args.kwargs["env"]["GIT_TERMINAL_PROMPT"], "0")
            self.assertEqual(os.environ["GIT_TERMINAL_PROMPT"], "1")


class CommandLineTests(unittest.TestCase):
    def test_repeatable_repo_timeout_and_check_exit_status(self):
        argv = ["sync-repos.py", "--check", "--repo", "first", "--repo", "second", "--fetch-timeout", "12"]
        with patch.object(sys, "argv", argv), patch.object(sync, "synchronize", return_value=True) as run:
            self.assertEqual(sync.main(), 1)
            run.assert_called_once_with(
                Path(sync.__file__).resolve().parents[1], check_only=True, commit=False,
                repos=["first", "second"], fetch_timeout=12,
            )

    def test_default_full_scope_and_commit_exit_status(self):
        with patch.object(sys, "argv", ["sync-repos.py", "--commit"]), patch.object(sync, "synchronize", return_value=True) as run:
            self.assertEqual(sync.main(), 0)
            self.assertIsNone(run.call_args.kwargs["repos"])
            self.assertEqual(run.call_args.kwargs["fetch_timeout"], 30)

    def test_timeout_and_interrupt_have_clear_exit_codes(self):
        for error, code, message in [(sync.SyncError("fetch timed out"), 2, "Sync stopped"), (KeyboardInterrupt(), 130, "Sync cancelled")]:
            with self.subTest(code=code), patch.object(sys, "argv", ["sync-repos.py"]), patch.object(sync, "synchronize", side_effect=error):
                output = io.StringIO()
                with contextlib.redirect_stderr(output):
                    self.assertEqual(sync.main(), code)
                self.assertIn(message, output.getvalue())


if __name__ == "__main__":
    unittest.main()
