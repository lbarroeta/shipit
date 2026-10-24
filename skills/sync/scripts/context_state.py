#!/usr/bin/env python3
"""Inspect context drift or record a reviewed baseline. Never edits source files."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid


CONFIG = ".shipit/config.json"
STATE = ".shipit/sync-state.json"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).rstrip("\n")


def read_json(path):
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object: {path}")
    return value


def relative(name):
    path = Path(name)
    if not isinstance(name, str) or not name or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Expected a repository-relative path: {name}")
    return path.as_posix()


def fingerprint(path):
    if path.is_symlink():
        return {"kind": "symlink", "target": os.readlink(path)}
    if not path.exists():
        return None
    if not path.is_file():
        return {"kind": "directory"}
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return {"kind": "file", "sha256": sha.hexdigest(),
            "executable": bool(path.stat().st_mode & 0o111)}


def under(name, prefix):
    return name == prefix or name.startswith(prefix.rstrip("/") + "/")


def excluded(config):
    paths = config.get("paths", {})
    graph = config.get("graph") or {}
    return [".shipit", "graphify-out", paths.get("plans", ".shipit/plans"),
            paths.get("tasks", ".shipit/tasks"), paths.get("rules", ".shipit/rules"),
            graph.get("out", "graphify-out")]


def relevant(name, config):
    return not any(under(name, prefix) for prefix in excluded(config))


def untracked(repo):
    return set(filter(None, git(repo, "ls-files", "--others", "--exclude-standard", "-z").split("\0")))


def dirty_snapshot(repo, config):
    # Hashes of uncommitted work only; committed content is reachable from `head`.
    tracked = git(repo, "diff", "--name-only", "--no-renames", "-z", "HEAD").split("\0")
    return {name: fingerprint(repo / name) for name in sorted(set(filter(None, tracked)) | untracked(repo))
            if relevant(name, config)}


def source_changes(repo, config, baseline):
    """Paths whose working tree differs from the baseline: its commit plus the dirty files recorded then."""
    dirty = baseline.get("dirty", baseline.get("sources", {}))  # version 1 hashed every file here
    try:
        committed = set(filter(None, git(repo, "diff", "--name-only", "--no-renames", "-z",
                                         baseline["head"]).split("\0")))
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"Baseline commit {baseline['head']} is unknown here; re-record the baseline.") from exc
    return sorted(name for name in committed | untracked(repo) | dirty.keys()
                  if relevant(name, config)
                  and (dirty[name] != fingerprint(repo / name) if name in dirty else True))


def contract_snapshot(repo, config):
    rules = relative(config.get("paths", {}).get("rules", ".shipit/rules"))
    names = {CONFIG, ".shipit/stack.md", ".shipit/conventions.md", ".shipit/design-system.md"}
    root = repo / rules
    if root.exists():
        names.update(p.relative_to(repo).as_posix() for p in root.rglob("*.md"))
    return {name: fingerprint(repo / name) for name in sorted(names)}


def changed(previous, current):
    return sorted(name for name in previous.keys() | current.keys()
                  if previous.get(name) != current.get(name))


def inspect(repo, config, baseline):
    contracts = changed(baseline.get("contracts", {}), contract_snapshot(repo, config))
    modified = sorted(name for name, entry in baseline.get("managed", {}).items()
                      if fingerprint(repo / relative(name)) != entry["fingerprint"])
    sources = source_changes(repo, config, baseline) if baseline else []
    return {"status": "uninitialized" if not baseline else "changed" if (
                sources or contracts or modified) else "unchanged",
            "source_changes": sources, "contract_changes": contracts,
            "edited_managed": modified, "baseline": STATE}


def record(repo, config, inventory, baseline):
    managed = inventory.get("managed")
    if not isinstance(managed, list) or any(not isinstance(name, str) for name in managed):
        raise ValueError("Inventory needs a managed list of reviewed generated paths.")
    if inventory.get("unresolved") != []:
        raise ValueError("Do not record a current baseline with unresolved conflicts.")
    rules = relative(config.get("paths", {}).get("rules", ".shipit/rules"))
    entries = {}
    for raw in managed:
        name = relative(raw)
        allowed = name in {CONFIG, ".shipit/stack.md", ".shipit/conventions.md"} or (
            under(name, rules) and name.endswith(".md") and name != f"{rules}/design.md")
        if not allowed:
            raise ValueError(f"Not an init/sync-owned contract: {name}")
        path = repo / name
        # Do not adopt shared/symlinked contracts or read their targets as generated content.
        if any(parent.is_symlink() for parent in [path, *path.parents] if parent != repo):
            raise ValueError(f"Shared contract requires reconciliation in its owning checkout: {name}")
        text = path.read_text()
        entries[name] = {"fingerprint": fingerprint(path), "base": text}
    required = {CONFIG, ".shipit/stack.md", ".shipit/conventions.md"}
    if not required <= entries.keys():
        raise ValueError("Inventory must include config, stack and conventions.")
    for name in baseline.get("managed", {}).keys() - entries.keys():
        if os.path.lexists(repo / name):
            raise ValueError(f"Existing managed file omitted from inventory: {name}")
    value = {"version": 2, "head": git(repo, "rev-parse", "HEAD"),
             "dirty": dirty_snapshot(repo, config), "contracts": contract_snapshot(repo, config),
             "managed": entries}
    # No churn after a commit that changed no relevant content; the old head stays a valid base.
    if (baseline.get("version") == 2 and not source_changes(repo, config, baseline)
            and all(value[key] == baseline.get(key) for key in ("contracts", "managed"))):
        return {"status": "unchanged", "baseline": STATE}
    destination = repo / STATE
    if destination.is_symlink() or destination.parent.is_symlink():
        raise ValueError("Refusing to write a shared context baseline from this checkout.")
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    os.replace(temporary, destination)
    return {"status": "recorded", "baseline": STATE}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect")
    save = commands.add_parser("record")
    save.add_argument("--inventory", required=True)
    args = parser.parse_args()
    repo = Path(git(Path(args.repo).resolve(), "rev-parse", "--show-toplevel"))
    if not (repo / CONFIG).exists() and (repo / ".sdd/config.json").exists():
        raise ValueError("Legacy .sdd/ contract; run /shipit:init to migrate it to .shipit/.")
    config = read_json(repo / CONFIG)
    baseline = read_json(repo / STATE) if (repo / STATE).exists() else {}
    if baseline and baseline.get("version") not in {1, 2}:
        raise ValueError("Unsupported sync baseline version; do not overwrite it.")
    if args.command == "inspect":
        result = inspect(repo, config, baseline)
    else:
        result = record(repo, config, read_json(Path(args.inventory)), baseline)
    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        sys.exit(1)
