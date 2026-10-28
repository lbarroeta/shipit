#!/usr/bin/env python3
"""Publish QA screenshots to an orphan evidence branch without touching the checkout or index."""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile


class Blocked(Exception):
    pass


def git(repo, *args, env=None):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    if result.returncode:
        raise Blocked(f"git {' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def publish(repo, remote, branch, prefix, directory):
    parts = PurePosixPath(prefix).parts
    if not parts or PurePosixPath(prefix).is_absolute() or ".." in parts:
        raise Blocked("--prefix must be a relative path without '..'.")
    git(repo, "check-ref-format", "--branch", branch)
    files = sorted(path for path in Path(directory).iterdir() if path.is_file() and not path.is_symlink())
    if not files:
        raise Blocked(f"No evidence files in {directory}.")
    ref = f"refs/heads/{branch}"
    # A rejected push means another run published first; rebuild on its tip and retry.
    for _ in range(3):
        parent = None
        if git(repo, "ls-remote", "--heads", remote, ref):
            git(repo, "fetch", "--no-tags", remote, ref)
            parent = git(repo, "rev-parse", "FETCH_HEAD")
        with tempfile.TemporaryDirectory(prefix="shipit-evidence-") as temporary:
            env = {**os.environ, "GIT_INDEX_FILE": str(Path(temporary) / "index")}
            if parent:
                git(repo, "read-tree", parent, env=env)
            for path in files:
                blob = git(repo, "hash-object", "-w", "--", str(path))
                git(repo, "update-index", "--add", "--cacheinfo",
                    f"100644,{blob},{PurePosixPath(prefix, path.name)}", env=env)
            tree = git(repo, "write-tree", env=env)
        commit = git(repo, "commit-tree", tree, *(["-p", parent] if parent else []),
                     "-m", f"evidence: {prefix}")
        try:
            git(repo, "push", "--quiet", remote, f"{commit}:{ref}")
        except Blocked:
            continue
        return {"status": "completed", "branch": branch, "commit": commit,
                "files": [str(PurePosixPath(prefix, path.name)) for path in files]}
    raise Blocked(f"Push to {branch} kept being rejected; another publisher is racing.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="shipit-evidence")
    parser.add_argument("--prefix", required=True, help="Folder on the evidence branch, e.g. ENG-412/run-2")
    parser.add_argument("--dir", required=True, help="Local directory holding the screenshots")
    args = parser.parse_args()
    print(json.dumps(publish(Path(args.repo).resolve(), args.remote, args.branch, args.prefix, args.dir)))


if __name__ == "__main__":
    try:
        main()
    except (Blocked, OSError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        sys.exit(1)
