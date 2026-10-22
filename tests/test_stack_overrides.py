"""Scoped, exact version rollouts must not weaken the shared stack policy."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("check_stack", Path(__file__).resolve().parents[1] / "scripts/check-stack.py")
stack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stack)


class ScopedOverridesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.policy = {name: "1.2.3" for name in stack.SITE_PACKAGES}
        self.policy["siteOverrides"] = {"micro-frontend-learn": {stack.DOCS_KIT: "1.3.0"}}
        (self.root / ".gitmodules").write_text(
            '[submodule "micro-frontend-learn"]\npath = micro-frontend-learn\nbranch = main\n'
            '[submodule "react-learn"]\npath = react-learn\nbranch = main\n')
        for site in ("micro-frontend-learn", "react-learn"):
            path = self.root / site
            path.mkdir()
            (path / ".git").mkdir()
            versions = {name: "1.2.3" for name in stack.SITE_PACKAGES}
            if site == "micro-frontend-learn":
                versions[stack.DOCS_KIT] = "1.3.0"
            (path / "package.json").write_text(json.dumps({"dependencies": versions}))
            (path / "package-lock.json").write_text(json.dumps({"packages": {
                "": {"dependencies": versions},
                **{f"node_modules/{name}": {"version": version} for name, version in versions.items()},
            }}))

    def check(self):
        (self.root / "stack-versions.json").write_text(json.dumps(self.policy))
        return stack.check_collection(self.root)

    def test_override_is_scoped_to_named_site(self):
        self.assertEqual(self.check(), [])

    def test_override_still_checks_exact_lock(self):
        path = self.root / "micro-frontend-learn" / "package-lock.json"
        lock = json.loads(path.read_text())
        lock["packages"][f"node_modules/{stack.DOCS_KIT}"]["version"] = "1.2.3"
        path.write_text(json.dumps(lock))
        self.assertTrue(any("locked " + stack.DOCS_KIT in error for error in self.check()))

    def test_rejects_unknown_site(self):
        self.policy["siteOverrides"]["typo-site"] = {stack.DOCS_KIT: "1.3.0"}
        self.assertTrue(any("Unknown site override" in error for error in self.check()))

    def test_rejects_unknown_package_and_nonexact_version(self):
        for packages in ({"not-a-policy-package": "1.3.0"}, {stack.DOCS_KIT: "^1.3.0"}, {stack.DOCS_KIT: 13}):
            with self.subTest(packages=packages):
                self.policy["siteOverrides"] = {"micro-frontend-learn": packages}
                self.assertTrue(any("invalid exact-version override" in error for error in self.check()))

    def test_rejects_malformed_override_shape(self):
        for value in ([], {"micro-frontend-learn": []}, {"micro-frontend-learn": {}}):
            with self.subTest(value=value):
                self.policy["siteOverrides"] = value
                self.assertTrue(self.check())


if __name__ == "__main__":
    unittest.main()
