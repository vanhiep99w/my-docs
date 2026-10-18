#!/usr/bin/env python3
"""Check shared exact versions in child manifests and npm lockfiles, without network/writes."""

import configparser
import json
from pathlib import Path
import sys


SECTIONS = ("dependencies", "devDependencies")
SITE_PACKAGES = ("next", "react", "react-dom", "fumadocs-core", "fumadocs-ui", "fumadocs-mdx")


def check_package(path: Path, versions: dict[str, str]) -> list[str]:
    manifest = json.loads((path / "package.json").read_text())
    lock_path = path / "package-lock.json"
    if not lock_path.exists():
        return [f"{path.name}: missing package-lock.json"]
    lock = json.loads(lock_path.read_text()).get("packages", {})
    locked_manifest = lock.get("", {})
    errors = []
    dependencies = {key: value for section in SECTIONS for key, value in manifest.get(section, {}).items()}
    if "next" in dependencies:
        for name in SITE_PACKAGES:
            if name not in dependencies:
                errors.append(f"{path.name}: missing {name}")
    for section in SECTIONS:
        for name, spec in manifest.get(section, {}).items():
            if name not in versions:
                continue
            target = versions[name]
            alias = name == "fumadocs-ui" and spec.startswith("npm:@fumadocs/base-ui@")
            expected = f"npm:@fumadocs/base-ui@{target}" if alias else target
            if spec != expected:
                errors.append(f"{path.name}: {name} must be {expected}, found {spec}")
            if locked_manifest.get(section, {}).get(name) != spec:
                errors.append(f"{path.name}: lockfile manifest differs for {name}")
            installed = lock.get(f"node_modules/{name}", {})
            if installed.get("version") != target:
                errors.append(f"{path.name}: locked {name} must be {target}, found {installed.get('version')}")
            if alias and installed.get("name") != "@fumadocs/base-ui":
                errors.append(f"{path.name}: lockfile lost base-ui alias")
    return errors


def check_collection(root: Path) -> list[str]:
    versions = json.loads((root / "stack-versions.json").read_text())
    modules = configparser.ConfigParser()
    modules.read(root / ".gitmodules")
    errors = []
    for section in modules.sections():
        relative = modules[section]["path"]
        path = root / relative
        if path.is_symlink() or path.resolve().parent != root.resolve():
            errors.append(f"Invalid child path: {relative}")
            continue
        if not (path / ".git").exists():
            errors.append(f"{relative}: initialize submodules before checking")
        elif (path / "package.json").exists():
            errors.extend(check_package(path, versions))
    return errors


def main() -> int:
    try:
        errors = check_collection(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, configparser.Error) as error:
        print(f"Stack check failed: {error}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("All child manifests and lockfiles match stack-versions.json (peer ranges preserved).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
