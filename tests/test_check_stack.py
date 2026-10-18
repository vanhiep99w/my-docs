"""Offline fixtures for the shared dependency policy."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("check_stack", Path(__file__).resolve().parents[1] / "scripts/check-stack.py")
stack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stack)


class StackTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name)
        self.versions = {name: "1.2.3" for name in stack.SITE_PACKAGES}
        self.manifest = {"dependencies": self.versions.copy(), "peerDependencies": {"react": "^18 || ^19"}}
        self.lock = {"packages": {
            "": {"dependencies": self.versions.copy()},
            **{f"node_modules/{name}": {"version": version} for name, version in self.versions.items()},
        }}

    def check(self):
        (self.path / "package.json").write_text(json.dumps(self.manifest))
        (self.path / "package-lock.json").write_text(json.dumps(self.lock))
        return stack.check_package(self.path, self.versions)

    def test_exact_versions_and_peer_ranges(self):
        self.assertEqual(self.check(), [])

    def test_rejects_range_even_when_lock_matches(self):
        self.manifest["dependencies"]["next"] = "^1.2.3"
        self.lock["packages"][""]["dependencies"]["next"] = "^1.2.3"
        self.assertTrue(any("must be 1.2.3" in error for error in self.check()))

    def test_rejects_stale_resolved_version(self):
        self.lock["packages"]["node_modules/react"]["version"] = "1.2.2"
        self.assertTrue(any("locked react" in error for error in self.check()))

    def test_rejects_stale_lock_manifest(self):
        self.lock["packages"][""]["dependencies"]["next"] = "1.2.2"
        self.assertTrue(any("lockfile manifest differs" in error for error in self.check()))

    def test_accepts_base_ui_alias(self):
        alias = "npm:@fumadocs/base-ui@1.2.3"
        self.manifest["dependencies"]["fumadocs-ui"] = alias
        self.lock["packages"][""]["dependencies"]["fumadocs-ui"] = alias
        self.lock["packages"]["node_modules/fumadocs-ui"]["name"] = "@fumadocs/base-ui"
        self.assertEqual(self.check(), [])

    def test_rejects_wrong_alias_version(self):
        self.manifest["dependencies"]["fumadocs-ui"] = "npm:@fumadocs/base-ui@1.2.2"
        self.assertTrue(any("must be npm:@fumadocs/base-ui@1.2.3" in error for error in self.check()))

    def test_requires_full_site_stack(self):
        del self.manifest["dependencies"]["fumadocs-mdx"]
        self.assertTrue(any("missing fumadocs-mdx" in error for error in self.check()))

    def test_library_dev_dependencies_without_next(self):
        self.manifest = {"devDependencies": {"react": "1.2.3"}, "peerDependencies": {"react": "^18 || ^19"}}
        self.lock["packages"][""] = {"devDependencies": {"react": "1.2.3"}}
        self.assertEqual(self.check(), [])

    def test_requires_lockfile(self):
        (self.path / "package.json").write_text(json.dumps(self.manifest))
        self.assertTrue(any("missing package-lock.json" in error for error in stack.check_package(self.path, self.versions)))


if __name__ == "__main__":
    unittest.main()
