"""Offline integration tests: disposable local repositories, no GitHub access."""

import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
