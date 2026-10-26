"""Exercise run preparation/recovery against disposable local Git repositories."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/run/scripts/run_state.py"


class RunStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.remote = self.directory / "remote.git"
        self.seed = self.directory / "seed"
        self.repo = self.directory / "repo"
        self.git(self.directory, "init", "--bare", "--initial-branch=main", str(self.remote))
        self.git(self.directory, "init", "--initial-branch=main", str(self.seed))
        self.identity(self.seed)
        (self.seed / ".shipit").mkdir()
        self.config = {"handoff": {
            "allow": ["branch", "commit", "push", "pr_body"]}}
        (self.seed / ".shipit/config.json").write_text(json.dumps(self.config))
        (self.seed / "product.txt").write_text("initial\n")
        self.git(self.seed, "add", ".shipit/config.json", "product.txt")
        self.git(self.seed, "commit", "-m", "Initial fixture")
        self.git(self.seed, "remote", "add", "origin", str(self.remote))
        self.git(self.seed, "push", "-u", "origin", "main")
        self.git(self.directory, "clone", str(self.remote), str(self.repo))
        self.identity(self.repo)
        self.task = {"key": "github-issues:fixture/repo:42", "id": "42",
                     "url": "https://github.com/fixture/repo/issues/42",
                     "title": "Change the product", "description": "Show updated text.",
                     "acceptance_criteria": ["Updated text is visible"]}
        self.task_file = self.directory / "task.json"
        self.task_file.write_text(json.dumps(self.task))

    def git(self, repo, *args):
        result = subprocess.run(["git", "-C", str(repo), *args],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.rstrip("\n")

    def identity(self, repo):
        self.git(repo, "config", "user.name", "Run fixture")
        self.git(repo, "config", "user.email", "fixture@example.invalid")
        self.git(repo, "config", "commit.gpgsign", "false")

    def call(self, *args, success=True, repo=None):
        result = subprocess.run([sys.executable, str(HELPER), "--repo", str(repo or self.repo), *args],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def begin(self, success=True, repo=None, sync=True):
        state = self.call("begin", "--provider", "openai", "--task-file", str(self.task_file),
                          "--branch", "codex/42-product", success=success, repo=repo)
        if success and sync and state["stage"] == "sync_before":
            mode = state["mode"]
            state = self.synced(state)
            state["mode"] = mode
        return state

    def reviewed(self, state):
        return self.checkpoint(state, "review", self.result(state, "review"))

    def synced(self, state):
        if state["stage"] == "review":
            state = self.reviewed(state)
        files = sorted(filter(None, (self.git(self.repo, "diff", "--name-only", "--no-renames", "HEAD")
                       + "\n" + self.git(self.repo, "ls-files", "--others", "--exclude-standard")).splitlines()))
        result = self.result(state, state["stage"], files=files, context_status="current",
                             requires_revalidation=False,
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        return self.checkpoint(state, state["stage"], result)

    def owned(self, state, command, *args, success=True):
        return self.call(command, "--issue-key", self.task["key"], "--owner", state["owner"],
                         *args, success=success)

    def result(self, state, stage, **extra):
        directory = Path(state["state_path"]).parent
        artifact = directory / f"{stage}.md"
        artifact.write_text(f"{stage} evidence\n")
        result = {"status": "completed", "artifact": str(artifact),
                  "requested": state["routes"]["sync" if stage.startswith("sync_") else stage], "effective": {"model": None, "effort": None},
                  "blockers": []}
        result.update(extra)
        path = directory / f"{stage}-result.json"
        path.write_text(json.dumps(result))
        return path

    def checkpoint(self, state, stage, result, success=True):
        return self.owned(state, "checkpoint", "--stage", stage, "--result-file", str(result),
                          success=success)

    def implemented(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("updated\n")
        self.git(self.repo, "diff", "--check")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        return self.synced(self.checkpoint(state, "implement", result))

    def test_new_task_pulls_main_before_branching(self):
        self.git(self.repo, "switch", "-c", "old-task")
        (self.seed / "product.txt").write_text("latest remote\n")
        self.git(self.seed, "commit", "-am", "Remote update")
        self.git(self.seed, "push")
        state = self.begin()
        self.assertEqual(state["base_sha"], self.git(self.seed, "rev-parse", "HEAD"))
        self.assertEqual((self.repo / "product.txt").read_text(), "latest remote\n")
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "codex/42-product")
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")

    def test_dirty_checkout_is_preserved_and_lock_released(self):
        self.git(self.repo, "switch", "-c", "user-task")
        (self.repo / "product.txt").write_text("user-owned\n")
        self.assertIn("Pending changes", self.begin(success=False)["reason"])
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "user-task")
        self.assertEqual((self.repo / "product.txt").read_text(), "user-owned\n")
        (self.repo / "product.txt").write_text("initial\n")
        self.assertEqual(self.begin()["stage"], "plan")

    def test_missing_upstream_blocks_before_switch(self):
        self.git(self.repo, "branch", "--unset-upstream", "main")
        self.git(self.repo, "switch", "-c", "user-task")
        self.assertIn("upstream", self.begin(success=False)["reason"])
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "user-task")

    def test_divergence_and_local_only_main_commits_are_not_reset(self):
        (self.repo / "local.txt").write_text("local\n")
        self.git(self.repo, "add", "local.txt")
        self.git(self.repo, "commit", "-m", "Local-only commit")
        original = self.git(self.repo, "rev-parse", "HEAD")
        self.git(self.repo, "switch", "-c", "user-task")
        self.assertIn("local commits", self.begin(success=False)["reason"])
        self.assertEqual(self.git(self.repo, "rev-parse", "main"), original)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "user-task")
        (self.seed / "remote.txt").write_text("remote\n")
        self.git(self.seed, "add", "remote.txt")
        self.git(self.seed, "commit", "-m", "Remote-only commit")
        self.git(self.seed, "push")
        self.assertIn("diverged", self.begin(success=False)["reason"])
        self.assertEqual(self.git(self.repo, "rev-parse", "main"), original)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "user-task")

    def test_withheld_branch_does_not_mutate_git(self):
        self.config["handoff"]["allow"] = []
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        self.git(self.repo, "commit", "-am", "Restrict fixture")
        self.assertIn("handoff.allow", self.begin(success=False)["reason"])
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "main")

    def test_duplicate_issue_and_other_issue_in_same_checkout_are_locked(self):
        state = self.begin()
        self.assertIn("already active", self.begin(success=False)["reason"])
        second = dict(self.task, key="github-issues:fixture/repo:43", id="43")
        self.task_file.write_text(json.dumps(second))
        self.assertIn("already active", self.begin(success=False)["reason"])
        self.task_file.write_text(json.dumps(self.task))
        self.owned(state, "pause", "--reason", "fixture pause")
        self.assertEqual(self.begin()["mode"], "resume")

    def test_issue_lock_is_shared_between_worktrees(self):
        state = self.begin()
        other = self.directory / "worktree"
        self.git(self.repo, "worktree", "add", "-b", "other-task", str(other), "main")
        self.assertIn("already active", self.begin(success=False, repo=other)["reason"])
        self.owned(state, "pause", "--reason", "fixture pause")

    def test_resume_does_not_pull_main_again(self):
        state = self.begin()
        self.owned(state, "pause", "--reason", "fixture pause")
        (self.seed / "product.txt").write_text("new main\n")
        self.git(self.seed, "commit", "-am", "Later remote update")
        self.git(self.seed, "push")
        resumed = self.begin()
        self.assertEqual(resumed["base_sha"], state["base_sha"])
        self.assertEqual((self.repo / "product.txt").read_text(), "initial\n")

    def test_clean_resume_restores_branch_but_scope_change_blocks(self):
        state = self.begin()
        self.owned(state, "pause", "--reason", "fixture pause")
        self.git(self.repo, "switch", "main")
        resumed = self.begin()
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), state["branch"])
        self.owned(resumed, "pause", "--reason", "fixture pause")
        self.task["description"] = "Changed requirements"
        self.task_file.write_text(json.dumps(self.task))
        self.assertIn("scope changed", self.begin(success=False)["reason"])

    def test_acceptance_criteria_only_change_requires_explicit_reconciliation(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        self.owned(state, "pause", "--reason", "fixture pause")
        self.task["acceptance_criteria"] = ["A different result is visible"]
        self.task_file.write_text(json.dumps(self.task))
        self.assertIn("scope changed", self.begin(success=False)["reason"])
        resumed = self.call("begin", "--provider", "openai", "--task-file", str(self.task_file),
                            "--replan-reason", "User approved updated acceptance criteria")
        self.assertEqual(resumed["stage"], "sync_before")
        snapshot = json.loads((Path(resumed["state_path"]).parent / "task.json").read_text())
        self.assertEqual(snapshot["acceptance_criteria"], self.task["acceptance_criteria"])
        self.assertEqual(resumed["artifacts"], {})

    def test_resume_cannot_switch_over_dirty_other_branch(self):
        state = self.begin()
        self.owned(state, "pause", "--reason", "fixture pause")
        self.git(self.repo, "switch", "main")
        (self.repo / "product.txt").write_text("user change\n")
        self.assertIn("Pending changes", self.begin(success=False)["reason"])
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "main")

    def test_status_of_unknown_task_does_not_touch_git(self):
        before = self.git(self.repo, "rev-parse", "HEAD")
        self.assertEqual(self.call("status", "--issue-key", self.task["key"])["mode"], "new")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), before)

    def test_same_issue_resumes_after_another_task(self):
        first = self.begin()
        self.owned(first, "pause", "--reason", "Waiting for task context")
        other = dict(self.task, key="github-issues:fixture/repo:43", id="43")
        self.task_file.write_text(json.dumps(other))
        second = self.call("begin", "--provider", "openai", "--task-file", str(self.task_file),
                           "--branch", "codex/43-other")
        self.call("pause", "--issue-key", other["key"], "--owner", second["owner"],
                  "--reason", "Pause second task")
        self.task_file.write_text(json.dumps(self.task))
        resumed = self.begin()
        self.assertEqual(resumed["branch"], first["branch"])
        self.assertEqual(resumed["base_sha"], first["base_sha"])

    def test_resume_resolves_routes_after_restoring_task_branch(self):
        state = self.begin()
        self.owned(state, "pause", "--reason", "fixture pause")
        self.git(self.repo, "switch", "-c", "other-route", "main")
        other_config = dict(self.config, run={"models": {"openai": {
            "plan": {"model": "other-branch-only", "effort": "high"}}}})
        (self.repo / ".shipit/config.json").write_text(json.dumps(other_config))
        self.git(self.repo, "commit", "-am", "Other branch routes")
        resumed = self.begin()
        self.assertEqual(resumed["routes"]["plan"]["model"], "gpt-6-astra")
        self.assertEqual(resumed["routes"], self.call("routes", "--provider", "openai")["routes"])

    def test_owner_token_is_required_for_mutation(self):
        state = self.begin()
        before = Path(state["state_path"]).read_text()
        self.assertIn("does not own", self.call("pause", "--issue-key", self.task["key"],
                                               "--owner", "other", "--reason", "Steal lock",
                                               success=False)["reason"])
        self.assertEqual(Path(state["state_path"]).read_text(), before)

    def test_stage_gate_rejects_failed_result_wrong_route_and_substitution(self):
        state = self.begin()
        for extra, message in (
            ({"status": "failed"}, "blocked/failed"),
            ({"requested": {"model": "other", "effort": "high"}}, "configured route"),
            ({"effective": {"model": "other", "effort": "high"}}, "Effective model"),
            ({"blockers": ["Missing business rule"]}, "blockers"),
        ):
            with self.subTest(extra=extra):
                result = self.result(state, "plan", **extra)
                self.assertIn(message, self.checkpoint(state, "plan", result, success=False)["reason"])
        self.assertEqual(self.call("status", "--issue-key", self.task["key"])["stage"], "plan")

    def test_failed_validation_and_incomplete_manifest_block_delivery(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("updated\n")
        for checks, files, message in (
            ([{"command": "test", "exit_code": 1}], ["product.txt"], "validation"),
            ([{"command": "test", "exit_code": False}], ["product.txt"], "validation"),
            ([{"command": "test", "exit_code": 0}], [], "manifest"),
        ):
            result = self.result(state, "implement", validation=checks, files=files)
            self.assertIn(message, self.checkpoint(state, "implement", result, success=False)["reason"])

    def test_malformed_child_results_return_blocked_json_without_state_change(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        result = self.result(state, "implement", files=[],
                             validation=[{"command": "test", "exit_code": 0}])
        valid = json.loads(result.read_text())
        before = Path(state["state_path"]).read_text()
        for invalid in (
            [], None, dict(valid, effective=None), dict(valid, requested=[]),
            dict(valid, validation=[None]), dict(valid, validation={"command": "test"}),
            dict(valid, validation=[{"command": [], "exit_code": 0}]),
            dict(valid, artifact=None), dict(valid, files=[[]]),
        ):
            with self.subTest(invalid=invalid):
                result.write_text(json.dumps(invalid))
                response = self.checkpoint(state, "implement", result, success=False)
                self.assertEqual(response["status"], "blocked")
                self.assertEqual(Path(state["state_path"]).read_text(), before)

    def test_malformed_incomplete_result_preserves_state_and_locks(self):
        state = self.begin()
        result = self.result(state, "plan")
        before = Path(state["state_path"]).read_text()
        for invalid in ([], None, {"status": "blocked", "artifact": None, "files": []}):
            with self.subTest(invalid=invalid):
                result.write_text(json.dumps(invalid))
                response = self.owned(state, "pause", "--reason", "Invalid child",
                                      "--result-file", str(result), success=False)
                self.assertEqual(response["status"], "blocked")
                self.assertEqual(Path(state["state_path"]).read_text(), before)
        self.owned(state, "pause", "--reason", "Valid pause still owns locks")

    def test_validate_detects_content_drift_and_extra_paths(self):
        state = self.implemented()
        self.owned(state, "verify")
        (self.repo / "product.txt").write_text("unvalidated\n")
        self.assertIn("Validated file changed", self.owned(state, "verify", success=False)["reason"])
        (self.repo / "product.txt").write_text("updated\n")
        (self.repo / "extra.txt").write_text("unowned\n")
        self.assertIn("Unvalidated paths", self.owned(state, "verify", success=False)["reason"])

    def test_verify_rejects_unrelated_committed_paths(self):
        state = self.implemented()
        (self.repo / ".shipit/config.json").write_text("{}\n")
        self.git(self.repo, "add", "product.txt", ".shipit/config.json")
        self.git(self.repo, "commit", "-m", "Validated and unrelated changes")
        self.assertEqual(self.owned(state, "verify", success=False)["status"], "blocked")

    def test_verify_rejects_committed_mode_drift(self):
        state = self.implemented()
        (self.repo / "product.txt").chmod(0o755)
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Unvalidated executable mode")
        self.assertEqual(self.owned(state, "verify", success=False)["status"], "blocked")

    def test_verify_accepts_exact_delivery_with_new_and_deleted_files(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").unlink()
        (self.repo / "new.txt").write_text("validated new file\n")
        (self.repo / "new.txt").chmod(0o755)
        (self.repo / "link.txt").symlink_to("missing-target.txt")
        result = self.result(state, "implement", files=["product.txt", "new.txt", "link.txt"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        state = self.synced(self.checkpoint(state, "implement", result))
        index = Path(self.git(self.repo, "rev-parse", "--absolute-git-dir")) / "index"
        index_before = index.read_bytes()
        self.owned(state, "verify")
        self.assertEqual(index.read_bytes(), index_before)
        self.assertEqual(self.git(self.repo, "diff", "--cached", "--name-only"), "")
        self.git(self.repo, "add", "--all", "--", "product.txt", "new.txt", "link.txt")
        self.git(self.repo, "commit", "-m", "Exact delivery fixture")
        self.owned(state, "verify")

    def test_delivery_keeps_current_and_archived_plans_local(self):
        first = self.repo / ".shipit/plans/first plan.md"
        first.parent.mkdir(parents=True)
        first.write_text("Previously committed plan\n")
        self.git(self.repo, "add", ".shipit/plans/first plan.md")
        self.git(self.repo, "commit", "-m", "Existing plan fixture")
        self.git(self.repo, "push")
        state = self.begin()
        first.write_text("Revised local plan\n")
        state = self.checkpoint(state, "plan", self.result(state, "plan", artifact=str(first)))
        state = self.owned(state, "replan", "--reason", "Correct the plan fixture")
        state = self.synced(state)
        current = first.with_name("next-plan.md")
        current.write_text("Replacement local plan\n")
        state = self.checkpoint(state, "plan", self.result(state, "plan", artifact=str(current)))
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement",
                             files=["product.txt", ".shipit/plans/first plan.md", ".shipit/plans/next-plan.md"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        state = self.synced(self.checkpoint(state, "implement", result))
        self.assertEqual(state["delivery_files"], ["product.txt"])
        self.owned(state, "verify")
        first.write_text("Unvalidated archived plan edit\n")
        self.assertIn("Validated file changed", self.owned(state, "verify", success=False)["reason"])
        first.write_text("Revised local plan\n")
        self.git(self.repo, "add", ".shipit/plans/next-plan.md")
        staged_before = self.git(self.repo, "diff", "--cached", "--binary")
        self.assertIn("paths are staged", self.owned(state, "verify", success=False)["reason"])
        self.assertEqual(self.git(self.repo, "diff", "--cached", "--binary"), staged_before)
        self.git(self.repo, "restore", "--staged", "--", ".shipit/plans/next-plan.md")
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Deliver product only")
        self.owned(state, "verify")
        self.assertEqual(self.git(self.repo, "show", "HEAD:.shipit/plans/first plan.md"),
                         "Previously committed plan")
        self.assertNotIn(".shipit/plans/next-plan.md", self.git(self.repo, "ls-tree", "-r", "--name-only", "HEAD"))
        self.assertEqual(first.read_text(), "Revised local plan\n")
        self.assertEqual(current.read_text(), "Replacement local plan\n")
        self.git(self.repo, "add", ".shipit/plans/next-plan.md")
        self.git(self.repo, "commit", "-m", "Incorrectly commit a generated plan")
        self.assertIn("Committed tree differs", self.owned(state, "verify", success=False)["reason"])

    def test_verify_rejects_broken_symlink_target_drift(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        link = self.repo / "link.txt"
        link.symlink_to("missing-one.txt")
        result = self.result(state, "implement", files=["link.txt"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        state = self.synced(self.checkpoint(state, "implement", result))
        self.owned(state, "verify")
        link.unlink()
        link.symlink_to("missing-two.txt")
        self.git(self.repo, "add", "link.txt")
        self.git(self.repo, "commit", "-m", "Unvalidated symlink target")
        self.assertIn("Validated tree changed", self.owned(state, "verify", success=False)["reason"])

    def test_verify_names_rewritten_history(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "setup.txt").write_text("setup\n")
        self.git(self.repo, "add", "setup.txt")
        self.git(self.repo, "commit", "-m", "Earlier commit on the task branch")
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "check", "exit_code": 0}])
        state = self.synced(self.checkpoint(state, "implement", result))
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Delivered")
        self.owned(state, "verify")
        self.git(self.repo, "reset", "--soft", state["base_sha"])
        self.git(self.repo, "commit", "-m", "Squashed delivery")
        self.assertIn("history was rewritten", self.owned(state, "verify", success=False)["reason"])

    def test_snapshot_preserves_racy_index_detection(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        self.git(self.repo, "config", "core.trustctime", "false")
        product = self.repo / "product.txt"
        cached_time = product.stat().st_mtime_ns
        index = Path(self.git(self.repo, "rev-parse", "--absolute-git-dir")) / "index"
        os.utime(index, ns=(cached_time, cached_time))
        product.write_text("updated\n")
        os.utime(product, ns=(cached_time, cached_time))
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        state = self.synced(self.checkpoint(state, "implement", result))
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Racy timestamp fixture")
        self.owned(state, "verify")

    def test_artifact_drift_blocks_resume_and_explicit_replan_invalidates_stages(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        Path(state["artifacts"]["plan"]["path"]).write_text("edited plan\n")
        self.owned(state, "pause", "--reason", "fixture pause")
        self.assertIn("artifact changed", self.begin(success=False)["reason"])

    def test_replan_archives_prior_checkpoints(self):
        state = self.implemented()
        state = self.owned(state, "replan", "--reason", "Missing edge case")
        self.assertEqual(state["stage"], "sync_before")
        self.assertEqual(state["artifacts"], {})
        self.assertIn("implement", state["revisions"][0]["artifacts"])

    def test_incomplete_builder_ownership_is_saved_and_checked(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("incomplete\n")
        result = self.result(state, "implement", status="blocked", files=["product.txt"])
        self.owned(state, "pause", "--reason", "Failing fixture", "--result-file", str(result))
        resumed = self.begin()
        self.assertEqual(resumed["pending"]["files"].keys(), {"product.txt"})
        self.owned(resumed, "pause", "--reason", "fixture pause")
        (self.repo / "product.txt").write_text("user changed incomplete work\n")
        self.assertIn("Incomplete run files changed", self.begin(success=False)["reason"])

    def test_ignored_user_file_is_not_overwritten_by_main_switch(self):
        (self.repo / "ignored.txt").write_text("tracked main content\n")
        self.git(self.repo, "add", "ignored.txt")
        self.git(self.repo, "commit", "-m", "Main fixture file")
        self.git(self.repo, "push")
        self.git(self.repo, "switch", "-c", "user-task")
        self.git(self.repo, "rm", "ignored.txt")
        self.git(self.repo, "commit", "-m", "Remove fixture file")
        (self.repo / ".git/info/exclude").write_text("ignored.txt\n")
        (self.repo / "ignored.txt").write_text("ignored user content\n")
        self.assertIn("switch --no-overwrite-ignore main", self.begin(success=False)["reason"])
        self.assertEqual((self.repo / "ignored.txt").read_text(), "ignored user content\n")

    def test_ignored_user_file_is_not_overwritten_by_main_update(self):
        (self.repo / ".git/info/exclude").write_text("ignored.txt\n")
        (self.repo / "ignored.txt").write_text("ignored user content\n")
        original = self.git(self.repo, "rev-parse", "HEAD")
        (self.seed / "ignored.txt").write_text("incoming main content\n")
        self.git(self.seed, "add", "ignored.txt")
        self.git(self.seed, "commit", "-m", "Track incoming fixture file")
        self.git(self.seed, "push")
        self.assertEqual(self.begin(success=False)["status"], "blocked")
        self.assertEqual((self.repo / "ignored.txt").read_text(), "ignored user content\n")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)
        self.assertEqual(self.git(self.repo, "branch", "--list", "codex/42-product"), "")

    def test_completed_result_does_not_require_saved_branch(self):
        state = self.implemented()
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Complete fixture")
        state = self.checkpoint(state, "handoff", self.result(state, "handoff", delivery_status="completed"))
        state = self.owned(state, "qa", "--outcome", "pass", "--feedback", "Human tested all steps")
        self.owned(state, "pause", "--reason", "Completed")
        self.git(self.repo, "switch", "main")
        self.assertEqual(self.begin()["stage"], "done")
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "main")

    def test_delivery_checkpoint_and_human_qa_repair_cycle(self):
        state = self.implemented()
        partial = self.result(state, "handoff", delivery_status="partial")
        self.assertIn("partial/blocked", self.checkpoint(state, "handoff", partial, success=False)["reason"])
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Delivered fixture change")
        delivered = self.result(state, "handoff", delivery_status="completed")
        state = self.checkpoint(state, "handoff", delivered)
        self.assertEqual(state["stage"], "qa")
        state = self.owned(state, "qa", "--outcome", "fail", "--feedback", "Step 1 failed")
        self.assertEqual(state["stage"], "implement")
        self.assertEqual(set(state["artifacts"]), {"sync_before", "plan"})
        self.assertEqual(state["qa"][0]["outcome"], "fail")

    def test_delivered_run_returns_qa_steps_from_final_report(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        state = self.reviewed(self.checkpoint(state, "implement", result))
        self.assertNotIn("qa_guide", state)
        result = self.result(state, "sync_after", files=["product.txt"], context_status="current",
                             requires_revalidation=False,
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        report = Path(state["state_path"]).parent / "sync_after.md"
        qa = "## QA Handoff\n\nEnvironment: staging\n\n## QA Steps For Non-Developer\n\n1. Open the page\n   - Expected: updated text"
        report.write_text(f"# Report\n\n{qa}\n\n## Plan\n\nplan.md\n")
        state = self.checkpoint(state, "sync_after", result)
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Delivered fixture change")
        state = self.checkpoint(state, "handoff", self.result(state, "handoff", delivery_status="completed"))
        self.assertEqual(state["qa_guide"], {"report": str(report), "steps": qa})
        self.owned(state, "pause", "--reason", "Waiting for human QA")
        self.assertEqual(self.call("status", "--issue-key", self.task["key"])["qa_guide"]["steps"], qa)
        self.assertEqual(self.begin()["qa_guide"]["steps"], qa)

    def test_sync_stages_cannot_be_skipped_and_changes_reach_delivery(self):
        state = self.begin(sync=False)
        self.assertEqual(state["stage"], "sync_before")
        result = self.result(state, "plan")
        self.assertIn("Expected stage", self.checkpoint(state, "plan", result, success=False)["reason"])
        (self.repo / ".shipit/stack.md").write_text("Initial context\n")
        state = self.synced(state)
        self.assertIn(".shipit/stack.md", state["owned_files"])
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement", files=["product.txt", ".shipit/stack.md"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        state = self.checkpoint(state, "implement", result)
        self.assertEqual(state["stage"], "review")
        state = self.reviewed(state)
        builder = Path(state["artifacts"]["implement"]["path"]).read_bytes()
        self.owned(state, "verify")
        result = self.result(state, "handoff", delivery_status="completed")
        self.assertIn("Expected stage", self.checkpoint(state, "handoff", result, success=False)["reason"])
        (self.repo / ".shipit/stack.md").write_text("Final context\n")
        state = self.synced(state)
        self.assertEqual(state["stage"], "handoff")
        self.assertEqual(builder, Path(state["artifacts"]["implement"]["path"]).read_bytes())
        self.assertIn(".shipit/stack.md", state["delivery_files"])
        self.owned(state, "verify")

    def test_sync_conflicts_and_pending_validation_block_advancement(self):
        state = self.begin(sync=False)
        for extra in ({"context_status": "partial"}, {"requires_revalidation": True},
                      {"blockers": ["Human preference conflicts with source"]},
                      {"validation": [{"command": "check", "exit_code": 1}]}):
            data = dict(files=[], context_status="current", requires_revalidation=False,
                        validation=[{"command": "check", "exit_code": 0}])
            data.update(extra)
            result = self.result(state, "sync_before", **data)
            self.assertEqual(self.checkpoint(state, "sync_before", result, success=False)["status"], "blocked")
        self.assertEqual(self.call("status", "--issue-key", self.task["key"])["stage"], "sync_before")

    def test_sync_owned_edits_are_protected_on_resume(self):
        state = self.begin(sync=False)
        (self.repo / ".shipit/stack.md").write_text("Synced context\n")
        state = self.synced(state)
        self.owned(state, "pause", "--reason", "Interrupted before planning")
        (self.repo / ".shipit/stack.md").write_text("New user edit\n")
        self.assertIn("Run-owned files changed", self.begin(success=False)["reason"])

    def test_failed_post_sync_returns_to_builder_and_repeats_sync(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "check", "exit_code": 0}])
        state = self.reviewed(self.checkpoint(state, "implement", result))
        failed = self.result(state, "sync_after", status="blocked", files=["product.txt"],
                             blockers=["New required check failed"])
        state = self.owned(state, "repair", "--reason", "New check", "--result-file", str(failed))
        self.assertEqual(state["stage"], "implement")
        self.assertNotIn("implement", state["artifacts"])
        self.assertEqual(set(state["artifacts"]), {"sync_before", "plan"})
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "new check", "exit_code": 0}])
        state = self.checkpoint(state, "implement", result)
        self.assertEqual(state["stage"], "review")

    def built(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "check", "exit_code": 0}])
        return self.checkpoint(state, "implement", result)

    def test_review_must_fix_returns_to_builder_once_then_needs_the_user(self):
        state = self.built()
        self.assertEqual(state["stage"], "review")
        failed = self.result(state, "review", status="blocked", files=["product.txt"],
                             blockers=["Must fix: empty input crashes"])
        self.assertEqual(self.checkpoint(state, "review", failed, success=False)["status"], "blocked")
        state = self.owned(state, "repair", "--reason", "Must fix", "--result-file", str(failed))
        self.assertEqual(state["stage"], "implement")
        self.assertEqual(set(state["artifacts"]), {"sync_before", "plan"})
        (self.repo / "product.txt").write_text("fixed\n")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "check", "exit_code": 0}])
        state = self.checkpoint(state, "implement", result)
        failed = self.result(state, "review", status="blocked", files=["product.txt"],
                             blockers=["Must fix: still crashes"])
        reason = self.owned(state, "repair", "--reason", "Again", "--result-file", str(failed),
                            success=False)["reason"]
        self.assertIn("--user-decision", reason)
        state = self.owned(state, "repair", "--reason", "Again", "--result-file", str(failed),
                           "--user-decision", "User asked for one more round")
        self.assertEqual(state["stage"], "implement")
        self.assertEqual(state["repairs"][-1]["user_decision"], "User asked for one more round")

    def test_review_cannot_approve_changed_code(self):
        state = self.built()
        (self.repo / "product.txt").write_text("reviewer edit\n")
        result = self.result(state, "review")
        self.assertIn("Validated file changed", self.checkpoint(state, "review", result, success=False)["reason"])

    def test_human_qa_failure_invalidates_review(self):
        state = self.implemented()
        self.assertIn("review", state["artifacts"])
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Delivered fixture change")
        state = self.checkpoint(state, "handoff", self.result(state, "handoff", delivery_status="completed"))
        state = self.owned(state, "qa", "--outcome", "fail", "--feedback", "Step 1 failed")
        self.assertNotIn("review", state["artifacts"])
        self.assertNotIn("review_repairs", state)

    def test_legacy_active_run_requires_explicit_reconciliation(self):
        state = self.begin()
        self.owned(state, "pause", "--reason", "Upgrade fixture")
        path = Path(state["state_path"])
        saved = json.loads(path.read_text())
        saved["version"] = 1
        saved["artifacts"].pop("sync_before")
        path.write_text(json.dumps(saved))
        self.assertIn("Legacy run", self.begin(success=False)["reason"])
        state = self.call("begin", "--provider", "openai", "--task-file", str(self.task_file),
                          "--replan-reason", "Reconciled old run")
        self.assertEqual(state["stage"], "sync_before")
        self.assertEqual(state["version"], 2)

    def test_post_sync_replan_preserves_new_context_ownership(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "check", "exit_code": 0}])
        state = self.reviewed(self.checkpoint(state, "implement", result))
        (self.repo / ".shipit/stack.md").write_text("New evidence\n")
        result = self.result(state, "sync_after", status="blocked",
                             files=["product.txt", ".shipit/stack.md"], blockers=["Plan conflict"])
        state = self.owned(state, "replan", "--reason", "Approved plan correction",
                           "--result-file", str(result))
        self.assertEqual(state["stage"], "sync_before")
        self.assertEqual(set(state["revisions"][-1]["owned_files"]), {"product.txt", ".shipit/stack.md"})
        state = self.synced(state)
        self.assertEqual(state["stage"], "plan")

    def test_sync_route_override_is_independent_of_builder(self):
        self.config["run"] = {"models": {"openai": {
            "sync": {"model": "custom-sync", "effort": "high"},
            "implement": {"model": "custom-builder", "effort": "medium"}}}}
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        routes = self.call("routes", "--provider", "openai")["routes"]
        self.assertEqual(routes["sync"]["model"], "custom-sync")
        self.assertEqual(routes["implement"]["model"], "custom-builder")

    def test_default_routes_and_complete_override(self):
        default = self.call("routes", "--provider", "openai")["routes"]
        self.assertEqual(default, {
            "sync": {"model": "gpt-6.1-sol", "effort": "medium"},
            "plan": {"model": "gpt-6-astra", "effort": "high"},
            "implement": {"model": "gpt-6.1-sol", "effort": "high"},
            "review": {"model": "gpt-6-astra", "effort": "high"},
            "handoff": {"model": "gpt-6-luna", "effort": "medium"},
        })
        self.assertEqual(self.call("routes", "--provider", "anthropic")["routes"], {
            "sync": {"model": "claude-sonnet-5-5", "effort": "medium"},
            "plan": {"model": "claude-opus-5-5", "effort": "high"},
            "implement": {"model": "claude-sonnet-5-5", "effort": "high"},
            "review": {"model": "claude-opus-5-5", "effort": "high"},
            "handoff": {"model": "claude-haiku-5-5", "effort": "medium"},
        })
        self.config["run"] = {"models": {"openai": {"plan": {"model": "custom", "effort": "high"}}}}
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        self.assertEqual(self.call("routes", "--provider", "openai")["routes"], {
            **default, "plan": {"model": "custom", "effort": "high"},
        })
        self.config["run"]["models"]["openai"]["plan"] = {"model": "custom"}
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        self.assertIn("Invalid model/effort", self.call("routes", "--provider", "openai", success=False)["reason"])

    def test_legacy_contract_points_to_init(self):
        (self.repo / ".shipit").rename(self.repo / ".sdd")
        self.assertIn("/shipit:init", self.call("routes", "--provider", "openai", success=False)["reason"])


if __name__ == "__main__":
    unittest.main()
