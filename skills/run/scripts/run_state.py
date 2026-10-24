#!/usr/bin/env python3
"""Local Git preparation and durable checkpoints for shipit:run. No shell execution."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid


class Blocked(Exception):
    pass


def git(repo, *args, env=None):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, env=env
    )
    if result.returncode:
        raise Blocked(f"git {' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.rstrip("\n")


def read_json(path):
    try:
        value = json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        raise Blocked(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Blocked(f"JSON object required in {path}.")
    return value


def read_result(path):
    result = read_json(path)
    for field in ("status", "artifact"):
        if not isinstance(result.get(field), str) or not result[field].strip():
            raise Blocked(f"Subagent result needs a non-empty {field} string.")
    for field in ("requested", "effective"):
        if field in result:
            route = result[field]
            if not isinstance(route, dict):
                raise Blocked(f"Subagent {field} must be an object.")
            for key, value in route.items():
                if key not in {"model", "effort"} or (value is not None and (
                        not isinstance(value, str) or not value.strip())):
                    raise Blocked(f"Subagent {field} needs model/effort strings or null values.")
    if "validation" in result:
        checks = result["validation"]
        if not isinstance(checks, list) or any(
            not isinstance(check, dict) or not isinstance(check.get("command"), str)
            or not check["command"].strip() or type(check.get("exit_code")) is not int
            for check in checks
        ):
            raise Blocked("Subagent validation needs command strings and integer exit codes.")
    if "files" in result and (not isinstance(result["files"], list) or any(
            not isinstance(name, str) or not name for name in result["files"])):
        raise Blocked("Subagent files manifest must be a list of non-empty path strings.")
    if "delivery_status" in result and not isinstance(result["delivery_status"], str):
        raise Blocked("Subagent delivery_status must be a string.")
    return result


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    os.replace(temporary, path)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def locations(repo, key):
    common = Path(git(repo, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = repo / common
    root = common.resolve() / "shipit"
    run_dir = root / "runs" / digest(key)
    locks = [root / "locks" / f"issue-{digest(key)}.json",
             root / "locks" / f"checkout-{digest(str(repo))}.json"]
    return run_dir, locks


def acquire(locks, owner):
    acquired = []
    try:
        for path in locks:
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError as exc:
                raise Blocked(f"Run already active: {path}. Inspect it; never remove an active lock.") from exc
            acquired.append(path)
            with os.fdopen(fd, "w") as stream:
                json.dump({"owner": owner}, stream)
    except BaseException:
        for path in acquired:
            path.unlink()
        raise


def require_owner(state, locks, owner):
    if state.get("owner") != owner or not all(
        path.exists() and read_json(path).get("owner") == owner for path in locks
    ):
        raise Blocked("This coordinator does not own both run locks.")


def release(locks, owner):
    for path in locks:
        if path.exists() and read_json(path).get("owner") == owner:
            path.unlink()


def require_branch(repo, state):
    if git(repo, "branch", "--show-current") != state["branch"]:
        raise Blocked(f"Resume in branch {state['branch']} at {state['repo']}; main must not be reset.")


def require_clean(repo):
    dirty = git(repo, "status", "--porcelain", "--untracked-files=all")
    if dirty:
        raise Blocked(f"Pending changes; no stash, reset or branch switch was performed:\n{dirty}")


def config_at(repo):
    if not (repo / ".shipit/config.json").exists() and (repo / ".sdd/config.json").exists():
        raise Blocked("Legacy .sdd/ contract; run /shipit:init to migrate it to .shipit/.")
    config = read_json(repo / ".shipit/config.json")
    if not isinstance(config, dict):
        raise Blocked(".shipit/config.json must be an object; run /shipit:init first.")
    return config


def routes(repo, provider):
    defaults = read_json(Path(__file__).resolve().parents[1] / "assets/models.json")
    selected = defaults[provider].copy()
    run_config = config_at(repo).get("run", {})
    if not isinstance(run_config, dict) or not isinstance(run_config.get("models", {}), dict):
        raise Blocked("run and run.models must be objects.")
    overrides = run_config.get("models", {}).get(provider, {})
    if not isinstance(overrides, dict) or set(overrides) - set(selected):
        raise Blocked("run.models must contain only sync, plan, implement and handoff routes.")
    selected.update(overrides)
    for stage, route in selected.items():
        if (not isinstance(route, dict) or set(route) != {"model", "effort"}
                or not isinstance(route["model"], str) or not route["model"].strip()
                or route["effort"] not in {"low", "medium", "high", "xhigh", "max", "ultra"}):
            raise Blocked(f"Invalid model/effort pair for {provider}.{stage}.")
    return {"provider": provider, "routes": selected}


ALLOW_DEFAULT = ["branch", "commit", "push", "pr_body", "pr_ready", "tracker_status"]


def read_task(path):
    task = read_json(path)
    for field in ("key", "id", "url", "title", "description"):
        if not isinstance(task.get(field), str) or not task[field].strip():
            raise Blocked(f"Resolved task needs non-empty {field}.")
    if (not isinstance(task.get("acceptance_criteria"), list) or not task["acceptance_criteria"]
            or any(not isinstance(item, str) or not item.strip() for item in task["acceptance_criteria"])):
        raise Blocked("Task lacks acceptance criteria; clarify before preparing Git.")
    return task


def source_digest(task):
    return digest({key: task[key] for key in (
        "key", "id", "url", "title", "description", "acceptance_criteria")})


def require_branch_allowed(repo, message):
    if "branch" not in config_at(repo).get("handoff", {}).get("allow", ALLOW_DEFAULT):
        raise Blocked(message)


def new_state(repo, task, args, owner):
    require_branch_allowed(repo, "Preparing a task branch requires branch in handoff.allow.")
    if not args.branch or args.branch == "main":
        raise Blocked("A task branch distinct from main is required.")
    git(repo, "check-ref-format", "--branch", args.branch)
    if git(repo, "branch", "--list", args.branch):
        raise Blocked("Task branch already exists without a run record; inspect it before adopting it.")
    return {"version": 2, "issue_key": task["key"], "issue_url": task["url"],
            "repo": str(repo), "branch": args.branch, "source_digest": source_digest(task),
            "provider": args.provider, "routes": routes(repo, args.provider)["routes"],
            "owner": owner, "stage": "preparing", "status": "active",
            "base_sha": None, "artifacts": {}, "agents": [], "qa": []}


def resume(repo, state, task, args, run_dir):
    """Restore a saved run on its branch, optionally replanning; mutates state."""
    if (state["stage"] != "done" or args.replan_reason) and git(repo, "branch", "--show-current") != state["branch"]:
        require_clean(repo)
        git(repo, "switch", "--no-overwrite-ignore", state["branch"])
    if args.replan_reason:
        verify_pending(repo, state)
        reset_plan(state, args.replan_reason)
        state["source_digest"] = source_digest(task)
        write_json(run_dir / "task.json", task)
    if state["stage"] != "done":
        state["routes"] = routes(repo, args.provider)["routes"]
    verify_artifacts(state)
    verify_pending(repo, state)
    state["status"] = "active"


def prepare(repo, state, args, path):
    """Sync main and create the task branch; also finishes an interrupted preparation."""
    require_clean(repo)
    if state["base_sha"] is None:
        git(repo, "show-ref", "--verify", "refs/heads/main")
        upstream = git(repo, "for-each-ref", "--format=%(upstream:remotename) %(upstream:remoteref)",
                       "refs/heads/main").split()
        if len(upstream) != 2 or upstream[1] != "refs/heads/main":
            raise Blocked("main needs an upstream tracking a remote main branch.")
        git(repo, "fetch", "--", upstream[0])
        incoming = git(repo, "rev-parse", "main@{upstream}")
        local = git(repo, "rev-parse", "refs/heads/main")
        if git(repo, "merge-base", local, incoming) != local:
            raise Blocked("main has local commits absent from upstream or has diverged; "
                          "no switch, merge or reset was performed.")
        # shortcut: a merge refused by --no-overwrite-ignore still leaves the checkout on main; switch back if that bites.
        git(repo, "switch", "--no-overwrite-ignore", "main")
        git(repo, "merge", "--ff-only", "--no-overwrite-ignore", incoming)
        state["base_sha"] = incoming
        write_json(path, state)
    require_branch_allowed(repo, "Updated contract withholds branch in handoff.allow.")
    state["routes"] = routes(repo, args.provider)["routes"]
    if git(repo, "branch", "--list", state["branch"]):
        if git(repo, "rev-parse", state["branch"]) != state["base_sha"]:
            raise Blocked("An interrupted preparation left an unexpected task branch tip.")
        git(repo, "switch", "--no-overwrite-ignore", state["branch"])
    else:
        git(repo, "switch", "--no-overwrite-ignore", "-c", state["branch"], state["base_sha"])
    state.update(version=2, stage="sync_before", status="active")


def begin(repo, args):
    task = read_task(args.task_file)
    run_dir, locks = locations(repo, task["key"])
    path = run_dir / "state.json"
    owner = uuid.uuid4().hex
    acquire(locks, owner)
    state = None
    try:
        state = read_json(path) if path.exists() else None
        if state and state["repo"] != str(repo):
            raise Blocked(f"Run belongs to checkout {state['repo']}.")
        if state and state["source_digest"] != source_digest(task) and not args.replan_reason:
            raise Blocked("Task scope changed. Reconcile the saved plan with the user before resuming.")
        if (state and state.get("version", 1) < 2 and state["stage"] not in {"qa", "done", "preparing"}
                and not args.replan_reason):
            raise Blocked("Legacy run lacks sync checkpoints. Reconcile existing delivery effects, then resume with --replan-reason.")
        if state:
            state.update(owner=owner, provider=args.provider)
            if state["stage"] != "preparing":
                resume(repo, state, task, args, run_dir)
                write_json(path, state)
                output = {"mode": "resume", "state_path": str(path), **state}
                if state["stage"] in {"qa", "done"}:
                    output["qa_guide"] = qa_guide(state)
                return output
            if args.replan_reason:
                state["source_digest"] = source_digest(task)
                write_json(run_dir / "task.json", task)
        else:
            state = new_state(repo, task, args, owner)
            write_json(run_dir / "task.json", task)
            write_json(path, state)
        prepare(repo, state, args, path)
        write_json(path, state)
        return {"mode": "new", "state_path": str(path), **state}
    except BaseException:
        try:
            if state and state.get("owner") == owner:
                state["status"] = "blocked"
                write_json(path, state)
        finally:
            release(locks, owner)
        raise


def verify_artifacts(state):
    for artifact in state["artifacts"].values():
        if file_digest(Path(artifact["path"])) != artifact["sha256"]:
            raise Blocked(f"Saved artifact changed or is missing: {artifact['path']}")


def verify_pending(repo, state):
    pending = state.get("pending")
    if not pending and state["stage"] in {"plan", "implement", "sync_after"} and "owned_files" in state:
        owned = state["owned_files"]
        if changed_paths(repo) != set(owned) or any(file_digest(repo / name) != value for name, value in owned.items()):
            raise Blocked("Run-owned files changed since the last checkpoint; reconcile before resuming.")
    if pending:
        if file_digest(Path(pending["artifact"])) != pending["sha256"]:
            raise Blocked("Incomplete run report changed; reconcile ownership before resuming.")
        if (changed_paths(repo) != set(pending["files"])
                or any(file_digest(repo / name) != value for name, value in pending["files"].items())):
            raise Blocked("Incomplete run files changed; do not adopt user changes as run-owned.")


def capture_pending(repo, state, result_file):
    result = read_result(result_file)
    artifact = Path(result["artifact"]).resolve()
    files = result.get("files")
    if (result["status"] not in {"blocked", "failed"} or not artifact.is_file()
            or not isinstance(files, list) or set(files) != changed_paths(repo)):
        raise Blocked("Incomplete result needs a report and verified full run-owned manifest.")
    state["pending"] = {"artifact": str(artifact), "sha256": file_digest(artifact),
                        "files": {name: file_digest(repo / name) for name in files}}


def reset_plan(state, reason):
    state.setdefault("revisions", []).append({
        "reason": reason, "artifacts": state["artifacts"],
        "source_digest": state["source_digest"],
        "owned_files": state.get("pending", {}).get("files", state.get("owned_files", state.get("validated_files", {})))})
    state["artifacts"] = {}
    state.pop("pending", None)
    state["stage"] = "sync_before"
    state["version"] = 2
    for key in ("validated_files", "validated_head", "validated_diff", "validated_tree", "delivery_files"):
        state.pop(key, None)


def changed_paths(repo):
    tracked = git(repo, "diff", "--name-only", "--no-renames", "-z", "HEAD")
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    return set(filter(None, tracked.split("\0") + untracked.split("\0")))


def proposed_tree(repo, files, base=None):
    index = Path(git(repo, "rev-parse", "--git-path", "index"))
    if not index.is_absolute():
        index = repo / index
    with tempfile.TemporaryDirectory(prefix="shipit-index-") as directory:
        temporary = Path(directory) / "index"
        env = {**os.environ, "GIT_INDEX_FILE": str(temporary)}
        if base is not None:
            git(repo, "read-tree", base, env=env)
        elif index.exists():
            shutil.copy2(index, temporary)
        else:
            git(repo, "read-tree", "HEAD", env=env)
        indexed = set(git(repo, "ls-files", "--cached", "-z", env=env).split("\0"))
        stage_paths = sorted(name for name in files if name in indexed or os.path.lexists(repo / name))
        if stage_paths:
            git(repo, "--literal-pathspecs", "add", "--all", "--", *stage_paths, env=env)
        return git(repo, "write-tree", env=env)


def verify_validation(repo, state):
    for name, expected in state.get("validated_files", {}).items():
        if file_digest(repo / name) != expected:
            raise Blocked(f"Validated file changed: {name}. Return to implementation.")
    if changed_paths(repo) - set(state.get("validated_files", {})):
        raise Blocked("Unvalidated paths appeared after the builder finished.")
    if not state.get("validated_tree"):
        raise Blocked("Validated tree snapshot missing. Return to implementation.")
    delivery_files = state.get("delivery_files", state["validated_files"])
    staged = set(filter(None, git(repo, "diff", "--cached", "--name-only", "-z").split("\0")))
    if staged - set(delivery_files):
        raise Blocked("Excluded or unvalidated paths are staged; do not commit them.")
    base = state["validated_head"] if "delivery_files" in state else None
    if proposed_tree(repo, delivery_files, base) != state["validated_tree"]:
        raise Blocked("Validated tree changed. Return to implementation.")
    if git(repo, "rev-parse", "HEAD") == state.get("validated_head"):
        if digest(git(repo, "diff", "--binary", "HEAD")) != state.get("validated_diff"):
            raise Blocked("Validated diff changed. Return to implementation.")
    else:
        if git(repo, "merge-base", state["validated_head"], "HEAD") != state["validated_head"]:
            raise Blocked("HEAD no longer contains the validated commit; history was rewritten. Reconcile delivery.")
        if git(repo, "rev-parse", "HEAD^{tree}") != state["validated_tree"]:
            raise Blocked("Committed tree differs from the validated manifest. Reconcile delivery.")


def qa_guide(state):
    """QA sections of the final delivery report, so a delivered run never reruns to find them."""
    artifact = state["artifacts"].get("sync_after") or state["artifacts"].get("implement")
    if not artifact:
        return None
    path = Path(artifact["path"])
    lines, keep = [], False
    for line in path.read_text().splitlines() if path.is_file() else []:
        if line.startswith("## "):
            keep = line[3:].strip().upper().startswith("QA")
        if keep:
            lines.append(line)
    return {"report": str(path), "steps": "\n".join(lines).strip() or None}


def checkpoint(repo, state, args):
    expected = {"sync_before": "plan", "plan": "implement", "implement": "sync_after",
                "sync_after": "handoff", "handoff": "qa"}
    if state["stage"] != args.stage:
        raise Blocked(f"Expected stage {state['stage']}, received {args.stage}.")
    result = read_result(args.result_file)
    if result.get("status") != "completed":
        raise Blocked("A blocked/failed subagent cannot advance the workflow.")
    artifact = Path(result.get("artifact", "")).resolve()
    if not artifact.is_file():
        raise Blocked("The subagent must write its artifact before reporting completion.")
    requested = result.get("requested", {})
    effective = result.get("effective", {})
    if not requested.get("model") or not requested.get("effort"):
        raise Blocked("Record the requested model and effort.")
    if requested != state["routes"]["sync" if args.stage.startswith("sync_") else args.stage]:
        raise Blocked("Requested model/effort differs from this run's configured route.")
    if effective.get("model") and effective["model"] != requested["model"]:
        raise Blocked("Effective model differs from the configured route.")
    if effective.get("effort") and effective["effort"] != requested["effort"]:
        raise Blocked("Effective effort differs from the configured route.")
    if args.stage in {"sync_before", "plan", "sync_after"} and result.get("blockers") != []:
        raise Blocked("The stage must explicitly report no unresolved blockers.")
    if args.stage == "sync_after" and str(artifact) == state["artifacts"]["implement"]["path"]:
        raise Blocked("Final sync must write a separate delivery report; preserve builder evidence.")
    if args.stage.startswith("sync_"):
        if result.get("context_status") not in {"current", "updated"}:
            raise Blocked("Sync needs current or updated context; partial/unknown context cannot advance.")
        if result.get("requires_revalidation") is not False:
            raise Blocked("Sync must resolve required revalidation before advancing.")
        if result.get("files") is None or set(result["files"]) != changed_paths(repo):
            raise Blocked("Sync manifest must exactly match current changes, including prior run-owned files.")
        checks = result.get("validation", [])
        if not checks or any(check["exit_code"] != 0 for check in checks):
            raise Blocked("Sync needs successful executed context validation.")
    if args.stage in {"implement", "sync_after"}:
        checks = result.get("validation", [])
        if not checks or any(check["exit_code"] != 0 for check in checks):
            raise Blocked("Implementation needs executed validation commands with exit code 0.")
        files = result.get("files")
        if files is None:
            raise Blocked("Implementation result needs a files manifest.")
        if set(files) != changed_paths(repo):
            raise Blocked("Implementation manifest must exactly match the current diff and untracked files.")
        state["validated_files"] = {name: file_digest(repo / name) for name in files}
        state["validated_head"] = git(repo, "rev-parse", "HEAD")
        state["validated_diff"] = digest(git(repo, "diff", "--binary", "HEAD"))
        plans = [state["artifacts"].get("plan", {})] + [
            revision["artifacts"].get("plan", {}) for revision in state.get("revisions", [])]
        plan_paths = {Path(plan["path"]).resolve() for plan in plans if plan.get("path")}
        state["delivery_files"] = [name for name in files if (repo / name).resolve() not in plan_paths]
        state["validated_tree"] = proposed_tree(repo, state["delivery_files"], state["validated_head"])
    if args.stage == "handoff" and result.get("delivery_status") not in {"completed", "skipped"}:
        raise Blocked("A partial/blocked delivery remains at handoff for reconciliation.")
    if args.stage.startswith("sync_"):
        state["routes"] = routes(repo, state["provider"])["routes"]
    if args.stage != "handoff":
        state["owned_files"] = {name: file_digest(repo / name) for name in changed_paths(repo)}
    state["artifacts"][args.stage] = {"path": str(artifact), "sha256": file_digest(artifact)}
    state.pop("pending", None)
    state["agents"].append({"stage": args.stage, "agent_id": result.get("agent_id"),
                            "requested": requested, "effective": effective or None})
    state["stage"] = expected[args.stage]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    commands = parser.add_subparsers(dest="command", required=True)
    route = commands.add_parser("routes")
    route.add_argument("--provider", choices=["anthropic", "openai"], required=True)
    start = commands.add_parser("begin")
    start.add_argument("--task-file", required=True)
    start.add_argument("--branch")
    start.add_argument("--provider", choices=["anthropic", "openai"], required=True)
    start.add_argument("--replan-reason", help="Explicitly reconcile an approved scope/artifact correction")
    status = commands.add_parser("status")
    status.add_argument("--issue-key", required=True)
    for command in ("checkpoint", "pause", "qa", "verify", "replan", "repair"):
        sub = commands.add_parser(command)
        sub.add_argument("--issue-key", required=True)
        sub.add_argument("--owner", required=True)
        if command == "checkpoint":
            sub.add_argument("--stage", choices=["sync_before", "plan", "implement", "sync_after", "handoff"], required=True)
            sub.add_argument("--result-file", required=True)
        elif command in {"pause", "replan", "repair"}:
            sub.add_argument("--reason", required=True)
            if command in {"pause", "repair", "replan"}:
                sub.add_argument("--result-file", help="Save a verified incomplete child's report and owned files", required=command == "repair")
        elif command == "qa":
            sub.add_argument("--outcome", choices=["pass", "fail", "blocked"], required=True)
            sub.add_argument("--feedback", required=True)
    args = parser.parse_args()
    repo = Path(git(Path(args.repo).resolve(), "rev-parse", "--show-toplevel"))
    if args.command == "routes":
        output = routes(repo, args.provider)
    elif args.command == "begin":
        output = begin(repo, args)
    else:
        run_dir, locks = locations(repo, args.issue_key)
        state_path = run_dir / "state.json"
        if args.command == "status" and not state_path.exists():
            print(json.dumps({"mode": "new", "issue_key": args.issue_key}))
            return
        state = read_json(state_path)
        if state["repo"] != str(repo):
            raise Blocked(f"Run belongs to checkout {state['repo']}.")
        if args.command != "status":
            require_owner(state, locks, args.owner)
            if args.command == "pause":
                if args.result_file:
                    capture_pending(repo, state, args.result_file)
                state.update(status="paused", reason=args.reason)
            else:
                require_branch(repo, state)
                if args.command == "replan":
                    if args.result_file:
                        capture_pending(repo, state, args.result_file)
                    verify_pending(repo, state)
                    reset_plan(state, args.reason)
                else:
                    verify_artifacts(state)
                if args.command == "repair":
                    if state["stage"] != "sync_after":
                        raise Blocked("Repair is only applicable after implementation sync failed.")
                    capture_pending(repo, state, args.result_file)
                    state.setdefault("repairs", []).append({"reason": args.reason,
                        "artifacts": {key: state["artifacts"][key] for key in ("implement", "sync_after") if key in state["artifacts"]}})
                    for key in ("implement", "sync_after", "handoff"):
                        state["artifacts"].pop(key, None)
                    state["stage"] = "implement"
                elif args.command == "verify":
                    if state["stage"] not in {"sync_after", "handoff"}:
                        raise Blocked("Validation verification is only applicable before delivery.")
                    verify_validation(repo, state)
                elif args.command == "checkpoint":
                    if args.stage == "handoff":
                        verify_validation(repo, state)
                    checkpoint(repo, state, args)
                elif args.command == "qa":
                    if state["stage"] != "qa":
                        raise Blocked("Human QA can only be recorded after handoff.")
                    state["qa"].append({"outcome": args.outcome, "feedback": args.feedback})
                    if args.outcome == "pass":
                        state["stage"] = "done"
                    elif args.outcome == "fail":
                        if state.get("version", 1) < 2:
                            reset_plan(state, "Legacy QA repair requires synchronized context")
                        else:
                            state["stage"] = "implement"
                        state["owned_files"] = {name: file_digest(repo / name) for name in changed_paths(repo)}
                        for stage in ("implement", "sync_after", "handoff"):
                            state["artifacts"].pop(stage, None)
            write_json(state_path, state)
            if args.command == "pause":
                release(locks, args.owner)
        output = {"state_path": str(state_path), **state}
        if state["stage"] in {"qa", "done"}:
            output["qa_guide"] = qa_guide(state)
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (Blocked, OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False))
        sys.exit(1)
