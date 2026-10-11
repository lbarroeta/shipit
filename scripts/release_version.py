#!/usr/bin/env python3
"""Choose the next shipit version from changes since the latest release tag."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILES = (
    (Path(".claude-plugin/plugin.json"), "version"),
    (Path(".codex-plugin/plugin.json"), "version"),
    (Path("skills/init/assets/config-template.json"), "shipit_version"),
)
VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
COMMIT_RE = re.compile(r"^(feat|fix|perf|refactor|revert|docs|chore|build|ci|test)(?:\([^)]+\))?(!)?:", re.I)
PUBLIC_ENTRY = re.compile(r"^(?:skills/[^/]+/SKILL\.md|agents/[^/]+\.md|\.opencode/command/[^/]+\.md)$")


def git(*args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def parse_version(value: str) -> tuple[int, int, int]:
    match = VERSION_RE.fullmatch(value)
    if not match:
        raise ValueError(f"Invalid release version: {value}")
    return tuple(map(int, match.groups()))


def latest_tag() -> tuple[str, tuple[int, int, int]]:
    tags = git("tag", "--merged", "HEAD", "--list", "v*").splitlines()
    releases = [(tag, parse_version(tag)) for tag in tags if VERSION_RE.fullmatch(tag)]
    if not releases:
        raise ValueError("No reachable vMAJOR.MINOR.PATCH release tag")
    return max(releases, key=lambda release: release[1])


def distributed(path: str) -> bool:
    return path.startswith(("skills/", "agents/", ".opencode/command/", "references/")) or path in {
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        ".codex-plugin/plugin.json",
        ".agents/plugins/marketplace.json",
        "scripts/companions.sh",
        "scripts/install-opencode.sh",
    }


def changed_paths(base: str, head: str = "HEAD") -> list[tuple[str, str, str | None]]:
    """Return (status, new/current path, old path for renames)."""
    result = []
    for line in git("diff", "--name-status", "--find-renames", base, head).splitlines():
        fields = line.split("\t")
        status = fields[0][0]
        old = fields[1] if status in {"R", "C"} else None
        path = fields[-1]
        if distributed(path) or (old is not None and distributed(old)):
            result.append((status, path, old))
    return result


def commit_level(message: str) -> int:
    """Return patch=1, minor=2, breaking=3, or 0 for untyped commits."""
    match = COMMIT_RE.match(message)
    if re.search(r"^BREAKING[ -]CHANGE:", message, re.M | re.I) or (match and match.group(2)):
        return 3
    if match and match.group(1).lower() == "feat":
        return 2
    if match and match.group(1).lower() in {"fix", "perf", "refactor", "revert"}:
        return 1
    return 0


def skill_name(content: str) -> str | None:
    match = re.search(r"^name:\s*(.+)$", content, re.M)
    return match.group(1).strip() if match else None


def change_level(changes: list[tuple[str, str, str | None]], commits: list[str], base: str = "HEAD") -> int:
    if not changes:
        return 0
    level = 1  # Published content changed, even if commit title is untyped.
    for status, path, old in changes:
        if status in {"D", "R"} and PUBLIC_ENTRY.fullmatch(old or path):
            level = max(level, 3)
        elif status == "A" and PUBLIC_ENTRY.fullmatch(path):
            level = max(level, 2)
        elif status == "M" and re.fullmatch(r"skills/[^/]+/SKILL\.md", path):
            old_name = skill_name(git("show", f"{base}:{path}"))
            new_name = skill_name((ROOT / path).read_text())
            if old_name != new_name:
                level = max(level, 3)
    for commit in commits:
        paths = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        if any(distributed(path) for path in paths):
            level = max(level, commit_level(git("log", "-1", "--format=%B", commit)))
    return level


def next_version(current: tuple[int, int, int], level: int) -> tuple[int, int, int]:
    major, minor, patch = current
    if level == 3:
        return (major + 1, 0, 0) if major else (0, minor + 1, 0)
    if level == 2:
        return major, minor + 1, 0
    if level == 1:
        return major, minor, patch + 1
    return current


def write_versions(version: str) -> None:
    for relative, key in VERSION_FILES:
        path = ROOT / relative
        content = path.read_text()
        pattern = rf'("{re.escape(key)}"\s*:\s*")\d+\.\d+\.\d+("\s*)'
        updated, count = re.subn(pattern, rf"\g<1>{version}\g<2>", content, count=1)
        if count != 1:
            raise ValueError(f"Missing {key} in {relative}")
        path.write_text(updated)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Update both manifests and the config template")
    parser.add_argument("--github-output", type=Path, help="Append release outputs to this GitHub Actions file")
    args = parser.parse_args()

    tag, version = latest_tag()
    changes = changed_paths(tag)
    commits = git("rev-list", "--no-merges", f"{tag}..HEAD").splitlines()
    level = change_level(changes, commits, tag)
    target = ".".join(map(str, next_version(version, level)))
    if level and args.write:
        write_versions(target)
    result = {"release": bool(level), "version": target, "level": level, "base": tag, "changed_files": len(changes)}
    if args.github_output:
        with args.github_output.open("a") as output:
            output.write(f"release={'true' if level else 'false'}\nversion={target}\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
