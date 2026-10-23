#!/usr/bin/env python3
"""Prepare frozen planning inputs; verify a run left them unchanged. No model calls."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES = ("localized", "cross-layer", "permissions", "ambiguity")
PLUGIN_PATHS = (
    "skills/code-plan",
    "skills/task-next/references/readiness-policy.md",
    "references/lean-ladder.md",
)


def hashes(directory):
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(directory).parts
        and "__pycache__" not in path.relative_to(directory).parts
        and not path.relative_to(directory).as_posix().startswith("docs/plans/")
    }


def git(repo, *args):
    env = os.environ.copy()
    # Isolate fixtures from signing, hooks, author identity and global Git config.
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME="Plan eval", GIT_AUTHOR_EMAIL="eval@example.invalid",
               GIT_COMMITTER_NAME="Plan eval", GIT_COMMITTER_EMAIL="eval@example.invalid",
               GIT_AUTHOR_DATE="2026-01-01T00:00:00+00:00",
               GIT_COMMITTER_DATE="2026-01-01T00:00:00+00:00")
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "core.hooksPath=/dev/null",
         "-c", "commit.gpgsign=false", *args],
        env=env, check=True, capture_output=True, text=True,
    ).stdout.strip()


def prepare(case, destination):
    if destination.exists():
        raise ValueError(f"Destination must not exist: {destination}")
    destination.mkdir(parents=True)
    repo = destination / "repo"
    shutil.copytree(HERE / "fixture", repo, ignore=shutil.ignore_patterns("__pycache__"))
    request = (HERE / "cases" / f"{case}.md").read_text()
    (repo / "REQUEST.md").write_text(request)
    plugin = destination / "plugin"
    for relative in PLUGIN_PATHS:
        source, target = ROOT / relative, plugin / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
    git(repo, "init", "--initial-branch=main")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Frozen planning fixture")
    if case == "localized":
        path = repo / "app/labels.py"
        path.write_text(path.read_text().replace(
            'return " ".join(value.split()).casefold()',
            'return " ".join(value.split()).casefold() if value is not None else ""',
        ))
    prompt = (
        "Work in repo/. Read plugin/skills/code-plan/SKILL.md and its required references, "
        "then plan repo/REQUEST.md. Treat the relevant dirty edit as user-owned. "
        "Use read/search/local-shell tools and write only the plan artifact. "
        "No network, tracker, delegation, implementation, or delivery. "
        "Report the artifact path and any blocker.\n"
    )
    (destination / "prompt.md").write_text(prompt)
    manifest = {
        "case": case,
        "revision": git(repo, "rev-parse", "HEAD"),
        "dirty_status": git(repo, "status", "--short"),
        "repo_sha256": hashes(repo),
        "plugin_sha256": hashes(plugin),
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "tool_profile": {
            "read": True, "search": True, "local_shell": True,
            "write": "repo/docs/plans/ only", "network": False,
            "tracker": False, "delegation": False, "graph": "absent",
        },
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def verify(destination):
    manifest = json.loads((destination / "manifest.json").read_text())
    mismatches = []
    for name, directory in (("repo_sha256", "repo"), ("plugin_sha256", "plugin")):
        actual = hashes(destination / directory)
        expected = manifest[name]
        mismatches.extend(f"{directory}/{path}" for path in sorted(set(actual) | set(expected))
                          if actual.get(path) != expected.get(path))
    if git(destination / "repo", "rev-parse", "HEAD") != manifest["revision"]:
        mismatches.append("repo HEAD")
    if git(destination / "repo", "status", "--short") != manifest["dirty_status"]:
        mismatches.append("repo staged/unstaged state")
    if hashlib.sha256((destination / "prompt.md").read_bytes()).hexdigest() != manifest["prompt_sha256"]:
        mismatches.append("prompt.md")
    return {"unchanged_inputs": not mismatches, "mismatches": mismatches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("prepare")
    create.add_argument("case", choices=CASES)
    create.add_argument("destination", type=Path)
    check = sub.add_parser("verify")
    check.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args.case, args.destination.resolve())
        else:
            result = verify(args.destination.resolve())
        print(json.dumps(result, indent=2))
        if result.get("unchanged_inputs") is False:
            raise SystemExit(1)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()
