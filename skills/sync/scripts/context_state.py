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


CONFIG = "docs/shipit/config.json"
STATE = "docs/shipit/sync-state.json"
PATHS = {"stack": "docs/code/stack.md", "conventions": "docs/code/conventions.md",
         "rules": "docs/code/rules", "design_system": "docs/design-system/contract.md",
         "plans": "docs/plans", "tasks": "docs/tasks"}
SECTION = ("<!-- shipit:generated -->", "<!-- /shipit:generated -->")


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


def owned(path):
    """Shipit's marked section of a human doc, else the whole file: (fingerprint, text)."""
    if path.is_symlink() or not path.is_file():
        return fingerprint(path), None
    text = path.read_text()
    start = text.find(SECTION[0])
    end = text.find(SECTION[1], start)
    if start == -1 or end == -1:
        return fingerprint(path), text
    section = text[start:end + len(SECTION[1])]
    return {"kind": "section", "sha256": hashlib.sha256(section.encode()).hexdigest()}, section


def configured(config, key):
    return relative(config.get("paths", {}).get(key, PATHS[key]))


def under(name, prefix):
    return name == prefix or name.startswith(prefix.rstrip("/") + "/")


def source_snapshot(repo, config):
    excluded = ["docs/shipit", "graphify-out", *(configured(config, key) for key in PATHS)]
    graph = config.get("graph") or {}
    excluded.append(graph.get("out", "graphify-out"))
    names = set(filter(None, git(repo, "ls-files", "--cached", "--others",
                                "--exclude-standard", "-z").split("\0")))
    # Hashes only: no source content, credentials or environment values in state.
    return {name: fingerprint(repo / name) for name in sorted(names)
            if not any(under(name, prefix) for prefix in excluded) and os.path.lexists(repo / name)}


def contract_snapshot(repo, config):
    rules = configured(config, "rules")
    names = {CONFIG, *(configured(config, key) for key in ("stack", "conventions", "design_system"))}
    root = repo / rules
    if root.exists():
        names.update(p.relative_to(repo).as_posix() for p in root.rglob("*.md"))
    return {name: fingerprint(repo / name) for name in sorted(names)}


def changed(previous, current):
    return sorted(name for name in previous.keys() | current.keys()
                  if previous.get(name) != current.get(name))


def inspect(repo, config, baseline):
    sources = source_snapshot(repo, config)
    contracts = contract_snapshot(repo, config)
    modified = []
    for name, entry in baseline.get("managed", {}).items():
        if owned(repo / relative(name))[0] != entry["fingerprint"]:
            modified.append(name)
    return {"status": "uninitialized" if not baseline else "changed" if (
                sources != baseline.get("sources") or contracts != baseline.get("contracts")
                or modified) else "unchanged",
            "source_changes": changed(baseline.get("sources", {}), sources),
            "contract_changes": changed(baseline.get("contracts", {}), contracts),
            "edited_managed": sorted(modified),
            "head_changed": bool(baseline) and baseline.get("head") != git(repo, "rev-parse", "HEAD"),
            "baseline": STATE,
            "sources": sources, "contracts": contracts}


def record(repo, config, inventory, baseline):
    managed = inventory.get("managed")
    if not isinstance(managed, list) or any(not isinstance(name, str) for name in managed):
        raise ValueError("Inventory needs a managed list of reviewed generated paths.")
    if inventory.get("unresolved") != []:
        raise ValueError("Do not record a current baseline with unresolved conflicts.")
    rules = configured(config, "rules")
    required = {CONFIG, configured(config, "stack"), configured(config, "conventions")}
    entries = {}
    for raw in managed:
        name = relative(raw)
        allowed = name in required or (
            under(name, rules) and name.endswith(".md") and name != f"{rules}/design.md")
        if not allowed:
            raise ValueError(f"Not an init/sync-owned contract: {name}")
        path = repo / name
        # Do not adopt shared/symlinked contracts or read their targets as generated content.
        if any(parent.is_symlink() for parent in [path, *path.parents] if parent != repo):
            raise ValueError(f"Shared contract requires reconciliation in its owning checkout: {name}")
        current, text = owned(path)
        if text is None:
            raise ValueError(f"Managed contract is missing: {name}")
        entries[name] = {"fingerprint": current, "base": text}
    if not required <= entries.keys():
        raise ValueError("Inventory must include config, stack and conventions.")
    for name in baseline.get("managed", {}).keys() - entries.keys():
        if os.path.lexists(repo / name):
            raise ValueError(f"Existing managed file omitted from inventory: {name}")
    value = {"version": 1, "head": git(repo, "rev-parse", "HEAD"),
             "sources": source_snapshot(repo, config), "contracts": contract_snapshot(repo, config),
             "managed": entries}
    # No date churn, including after a commit that changed no relevant content.
    if all(value[key] == baseline.get(key) for key in ("version", "sources", "contracts", "managed")):
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
        raise ValueError("Legacy .sdd/ contract; run /shipit:init to migrate it to docs/.")
    config = read_json(repo / CONFIG)
    baseline = read_json(repo / STATE) if (repo / STATE).exists() else {}
    if baseline and baseline.get("version") != 1:
        raise ValueError("Unsupported sync baseline version; do not overwrite it.")
    if args.command == "inspect":
        result = inspect(repo, config, baseline)
        result.pop("sources")
        result.pop("contracts")
    else:
        result = record(repo, config, read_json(Path(args.inventory)), baseline)
    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        sys.exit(1)
