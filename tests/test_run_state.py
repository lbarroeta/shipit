"""Exercise run preparation/recovery against disposable local Git repositories."""

import importlib.util
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
    PR_BODY = "\n## PR Preparation\n\nShows updated text.\n\n## Validation\n\n`git diff --check` exit 0\n"

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
        artifact.write_text(f"{stage} evidence\n" + (self.PR_BODY if stage == "sync_after" else ""))
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

    def delivered(self):
        state = self.implemented()
        self.git(self.repo, "add", "product.txt")
        self.git(self.repo, "commit", "-m", "Delivered fixture change")
        self.git(self.repo, "push", "-u", "origin", "codex/42-product")
        return self.checkpoint(state, "handoff", self.result(state, "handoff", delivery_status="completed"))

    def baseline(self):
        """Record a current sync baseline on main, as sync on the main checkout does after a run."""
        for name in (".shipit/stack.md", ".shipit/conventions.md"):
            (self.seed / name).write_text(f"# {name}\n")
        (self.seed / ".shipit/config.json").write_text(json.dumps(self.config))
        self.git(self.seed, "add", ".shipit")
        self.git(self.seed, "commit", "-m", "Contract")
        inventory = self.directory / "inventory.json"
        inventory.write_text(json.dumps({"managed": [".shipit/config.json", ".shipit/stack.md",
                                                     ".shipit/conventions.md"], "unresolved": []}))
        result = subprocess.run([sys.executable, str(ROOT / "skills/sync/scripts/context_state.py"),
                                 "--repo", str(self.seed), "record", "--inventory", str(inventory)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.git(self.seed, "add", ".shipit/sync-state.json")
        self.git(self.seed, "commit", "-m", "Record context baseline")
        self.git(self.seed, "push")

    def worktree(self):
        """Move the fixture into a linked worktree, as a separate session would; return the main checkout."""
        main, self.repo = self.repo, self.directory / "session"
        self.git(main, "worktree", "add", "--detach", str(self.repo))
        return main

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

    def test_refused_main_update_returns_to_the_previous_branch(self):
        self.git(self.repo, "switch", "-c", "old-task")
        (Path(self.git(self.repo, "rev-parse", "--absolute-git-dir")) / "info/exclude").write_text("build.log\n")
        (self.repo / "build.log").write_text("local, ignored\n")
        (self.seed / "build.log").write_text("tracked upstream\n")
        self.git(self.seed, "add", "build.log")
        self.git(self.seed, "commit", "-m", "Track the log")
        self.git(self.seed, "push")
        self.assertIn("git merge", self.begin(success=False)["reason"])
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "old-task")
        self.assertEqual((self.repo / "build.log").read_text(), "local, ignored\n")

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

    def test_linked_worktree_branches_from_upstream_and_leaves_main_alone(self):
        (self.seed / "product.txt").write_text("latest remote\n")
        self.git(self.seed, "commit", "-am", "Remote update")
        self.git(self.seed, "push")
        main = self.worktree()
        local_main = self.git(main, "rev-parse", "main")
        (main / "product.txt").write_text("user edit in main\n")
        state = self.begin(sync=False)
        self.assertEqual(state["base_sha"], self.git(self.seed, "rev-parse", "HEAD"))
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "codex/42-product")
        self.assertEqual((self.repo / "product.txt").read_text(), "latest remote\n")
        self.assertEqual(self.git(main, "rev-parse", "main"), local_main)
        self.assertEqual((main / "product.txt").read_text(), "user edit in main\n")
        self.assertEqual(state["worktree"]["main"], str(main.resolve()))
        self.owned(state, "pause", "--reason", "fixture pause")
        status = self.call("status", "--issue-key", self.task["key"], repo=main)
        self.assertEqual(Path(status["repo"]), self.repo.resolve())
        self.assertIn(f"continue it with --repo {self.repo.resolve()}", self.begin(success=False, repo=main)["reason"])

    def test_several_cards_run_at_once_in_worktrees_the_helper_creates(self):
        first = self.call("worktree", "--name", "ENG-412")
        path = self.directory / "worktrees/repo/eng-412"
        self.assertEqual(first, {"path": str(path.resolve()), "created": True})
        self.assertEqual(self.call("worktree", "--name", "ENG-412")["created"], False)  # a repeated run reuses it
        second = Path(self.call("worktree", "--name", "ENG 413!")["path"])
        self.assertEqual(second.name, "eng-413")
        one = self.call("begin", "--provider", "openai", "--task-file", str(self.task_file),
                        "--branch", "codex/42-product", repo=path)
        other = dict(self.task, key="github-issues:fixture/repo:43", id="43")
        other_file = self.directory / "other.json"
        other_file.write_text(json.dumps(other))
        two = self.call("begin", "--provider", "openai", "--task-file", str(other_file),
                        "--branch", "codex/43-other", repo=second)
        self.assertEqual((one["status"], two["status"]), ("active", "active"))  # both hold their locks at once
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "main")  # the main checkout never moves
        self.assertIn("main checkout", self.call("worktree", "--name", "ENG-414", success=False, repo=path)["reason"])
        (self.directory / "worktrees/repo/eng-415").mkdir()
        self.assertIn("not a worktree", self.call("worktree", "--name", "ENG-415", success=False)["reason"])

    def test_worktree_receives_ignored_env_files_without_overwrite(self):
        (self.repo / ".gitignore").write_text(
            ".env*\n!.env.example\nvendor/\nshared\ngraph-out/\n/config/master.key\n")
        (self.repo / ".env.example").write_text("TOKEN=\n")
        (self.repo / "config").mkdir()
        (self.repo / "config/credentials.yml.enc").write_text("encrypted\n")
        self.config["worktree"] = {"link": ["shared", "missing", "loose"], "share_graph": True}
        self.config["graph"] = {"out": "graph-out"}
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        self.git(self.repo, "add", ".gitignore", ".env.example", "config/credentials.yml.enc", ".shipit/config.json")
        self.git(self.repo, "commit", "-m", "Ignore local files")
        self.git(self.repo, "push")
        for name, text in {".env": "TOKEN=main\n", "apps/web/.env.local": "PORT=3000\n", "vendor/.env": "vendored\n",
                           "shared": "key\n", "loose": "visible\n", "graph-out/graph.json": "{}\n",
                           "config/master.key": "secret\n"}.items():
            (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / name).write_text(text)
        (self.repo / ".env").chmod(0o600)
        main = self.worktree()
        (self.repo / "apps/web").mkdir(parents=True)
        (self.repo / "apps/web/.env.local").write_text("PORT=3001\n")
        prepared = self.begin(sync=False)["worktree"]
        self.assertEqual(prepared["copied"], [".env"])
        self.assertEqual(prepared["linked"], ["shared", "graph-out"])
        self.assertEqual(prepared["skipped"], [
            {"path": "missing", "reason": "missing in the main checkout"},
            {"path": "loose", "reason": "not ignored in this worktree"},
            {"path": "config/master.key", "reason": "Rails credentials key not in worktree.link"}])
        self.assertEqual((self.repo / ".env").read_text(), "TOKEN=main\n")
        self.assertEqual((self.repo / ".env").stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.repo / "apps/web/.env.local").read_text(), "PORT=3001\n")
        self.assertFalse((self.repo / "vendor/.env").exists())
        self.assertTrue((self.repo / "shared").is_symlink())
        self.assertTrue((self.repo / "graph-out").is_symlink())
        self.assertFalse(os.path.lexists(self.repo / "loose"))
        self.assertEqual(self.git(self.repo, "status", "--porcelain", "--untracked-files=all"), "")
        # A file main does not ignore stays visible there: only already-ignored paths get an exact exclude.
        self.assertIn("?? loose", self.git(main, "status", "--porcelain"))

    def test_worktree_links_rails_credentials_key_when_listed(self):
        (self.repo / ".gitignore").write_text("/config/credentials/*.key\n")
        (self.repo / "config/credentials").mkdir(parents=True)
        (self.repo / "config/credentials/test.yml.enc").write_text("encrypted\n")
        self.config["worktree"] = {"link": ["config/credentials/test.key"], "credentials": "link"}
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        self.git(self.repo, "add", ".gitignore", "config", ".shipit/config.json")
        self.git(self.repo, "commit", "-m", "Rails credentials")
        self.git(self.repo, "push")
        (self.repo / "config/credentials/test.key").write_text("secret\n")
        self.worktree()
        prepared = self.begin(sync=False)["worktree"]
        self.assertEqual(prepared["linked"], ["config/credentials/test.key"])
        self.assertEqual(prepared["skipped"], [])
        self.assertEqual((self.repo / "config/credentials/test.key").read_text(), "secret\n")

    DATABASE_YML = ("default: &default\n  adapter: postgresql\n\n"
                    "development:\n  <<: *default\n  database: app_development\n\n"
                    "test:\n  <<: *default\n  database: app_test\n\n"
                    "production:\n  <<: *default\n  database: app_production\n")

    def localized_worktree(self):
        self.config["worktree"] = {"database": "per_worktree"}
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        (self.repo / "config").mkdir()
        (self.repo / "config/database.yml").write_text(self.DATABASE_YML)
        self.git(self.repo, "add", ".shipit/config.json", "config/database.yml")
        self.git(self.repo, "commit", "-m", "Rails database")
        self.git(self.repo, "push")
        return self.worktree()

    def test_worktree_database_is_localized_and_never_committed(self):
        main = self.localized_worktree()
        state = self.delivered()
        text = (self.repo / "config/database.yml").read_text()
        self.assertIn("database: app_development_session\n", text)
        self.assertIn("database: app_test_session\n", text)
        self.assertIn("database: app_production\n", text)
        self.assertEqual((main / "config/database.yml").read_text(), self.DATABASE_YML)
        self.assertEqual(self.git(self.repo, "show", "HEAD:config/database.yml") + "\n", self.DATABASE_YML)
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")
        # main changes the same file: update merges the committed one and leaves it shared until delivered.
        self.git(self.seed, "pull")
        (self.seed / "config/database.yml").write_text(self.DATABASE_YML.replace("postgresql", "postgresql\n  pool: 5"))
        self.git(self.seed, "add", "config/database.yml")
        self.git(self.seed, "commit", "-m", "Pool size")
        self.git(self.seed, "push")
        state = self.owned(state, "update", "--reason", "PR conflicts with main")
        self.assertEqual(state["stage"], "implement")
        self.assertIn("pool: 5", (self.repo / "config/database.yml").read_text())
        self.assertNotIn("_session", (self.repo / "config/database.yml").read_text())
        self.assertFalse(self.git(self.repo, "ls-files", "-v", "config/database.yml").startswith("S "))

    def test_update_localizes_database_again_when_main_left_it_alone(self):
        self.localized_worktree()
        state = self.delivered()
        self.git(self.seed, "pull")
        (self.seed / "other.txt").write_text("from main\n")
        self.git(self.seed, "add", "other.txt")
        self.git(self.seed, "commit", "-m", "Another card merged")
        self.git(self.seed, "push")
        self.assertEqual(self.owned(state, "update", "--reason", "Keep up with main")["stage"], "implement")
        self.assertIn("database: app_test_session\n", (self.repo / "config/database.yml").read_text())
        self.assertTrue(self.git(self.repo, "ls-files", "-v", "config/database.yml").startswith("S "))

    def test_blocked_begin_keeps_worktree_databases_localized(self):
        self.localized_worktree()
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        self.owned(state, "pause", "--reason", "fixture pause")
        (self.repo / "product.txt").write_text("changed while paused\n")
        self.assertIn("Run-owned files changed", self.begin(success=False)["reason"])
        self.assertIn("database: app_test_session\n", (self.repo / "config/database.yml").read_text())
        self.assertTrue(self.git(self.repo, "ls-files", "-v", "config/database.yml").startswith("S "))

    def test_hidden_edit_to_localized_database_blocks_implementation(self):
        self.localized_worktree()
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        path = self.repo / "config/database.yml"
        path.write_text(path.read_text() + "  pool: 10\n")
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        self.assertIn("localized for this worktree", self.checkpoint(state, "implement", result, success=False)["reason"])
        # Resuming leaves the hidden edit in place instead of restoring the committed file over it.
        self.git(self.repo, "checkout", "--", "product.txt")
        self.owned(state, "pause", "--reason", "fixture pause")
        self.begin(sync=False)
        self.assertIn("pool: 10", path.read_text())

    def test_main_checkout_keeps_a_developers_own_skip_worktree_database(self):
        self.config["worktree"] = {"database": "per_worktree"}
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        (self.repo / "config").mkdir()
        (self.repo / "config/database.yml").write_text(self.DATABASE_YML)
        self.git(self.repo, "add", ".shipit/config.json", "config/database.yml")
        self.git(self.repo, "commit", "-m", "Rails database")
        self.git(self.repo, "push")
        local = self.DATABASE_YML.replace("app_development", "my_local_db")
        (self.repo / "config/database.yml").write_text(local)
        self.git(self.repo, "update-index", "--skip-worktree", "--", "config/database.yml")
        self.assertIsNone(self.begin(sync=False)["worktree"])
        self.assertEqual((self.repo / "config/database.yml").read_text(), local)

    def test_suffix_database_names_touches_only_development_and_test(self):
        spec = importlib.util.spec_from_file_location("run_state", HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        text = ("development:\n<% if ENV[\"PRIMARY\"] %>\n  primary:\n    database: \"app_dev\"  # main\n<% end %>\n  cache:\n"
                "    database: <%= ENV.fetch(\"CACHE_DB\") { \"app_cache\" } %>\n"
                "test:\n  database: storage/test.sqlite3\n  other: \n    database: ':memory:'\n"
                "production:\n  database: app_production\n")
        self.assertEqual(module.suffix_database_names(text, "_wt"), text
                         .replace('"app_dev"', '"app_dev_wt"')
                         .replace('} %>\n', '} %>_wt\n'))

    def test_checkout_lock_names_its_worktree_for_the_metrics_hook(self):
        main = self.worktree()
        self.begin(sync=False)
        locks = Path(self.git(main, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "shipit/locks"
        [checkout] = locks.glob("checkout-*.json")
        self.assertEqual(json.loads(checkout.read_text())["repo"], self.git(self.repo, "rev-parse", "--show-toplevel"))

    def test_context_skips_sync_before_when_baseline_is_current(self):
        self.config["commands"] = {"test_one": "git diff --check {path}"}
        self.baseline()
        state = self.begin(sync=False)
        self.assertEqual(state["stage"], "sync_before")
        state = self.owned(state, "context")
        self.assertTrue(state["context"]["skipped"])
        self.assertEqual(state["stage"], "plan")
        self.assertTrue(Path(state["artifacts"]["sync_before"]["path"]).is_file())
        self.assertEqual(state["agents"][-1], {"stage": "sync_before", "agent_id": None, "requested": None,
                                               "effective": None, "skipped": "context unchanged"})
        self.assertIn("only applicable before planning", self.owned(state, "context", success=False)["reason"])
        self.assertEqual(self.checkpoint(state, "plan", self.result(state, "plan"))["stage"], "implement")

    def test_context_dispatches_sync_without_baseline_or_after_source_changes(self):
        state = self.begin(sync=False)
        checked = self.owned(state, "context")
        self.assertFalse(checked["context"]["skipped"])
        self.assertIn("uninitialized", checked["context"]["reason"])
        self.assertEqual(checked["stage"], "sync_before")
        self.assertEqual(self.synced(checked)["stage"], "plan")
        self.owned(checked, "pause", "--reason", "fixture")
        self.baseline()
        (self.seed / "product.txt").write_text("changed on main\n")
        self.git(self.seed, "commit", "-am", "Another card merged")
        self.git(self.seed, "push")
        self.task["key"] = "github-issues:fixture/repo:43"
        self.task_file.write_text(json.dumps(self.task))
        state = self.call("begin", "--provider", "openai", "--task-file", str(self.task_file),
                          "--branch", "codex/43-product")
        checked = self.owned(state, "context")
        self.assertFalse(checked["context"]["skipped"])
        self.assertIn("context changed", checked["context"]["reason"])
        self.assertEqual(checked["context"]["inspect"]["source_changes"], ["product.txt"])

    def test_context_dispatches_sync_when_a_configured_executable_is_missing(self):
        self.config["commands"] = {"lint": "no-such-tool-7f3a --check"}
        self.baseline()
        state = self.begin(sync=False)
        checked = self.owned(state, "context")
        self.assertFalse(checked["context"]["skipped"])
        self.assertEqual(checked["context"]["reason"], "executables missing: no-such-tool-7f3a")
        self.assertEqual(checked["stage"], "sync_before")

    def test_update_merges_main_and_blocks_unresolved_conflicts(self):
        state = self.delivered()
        (self.seed / "product.txt").write_text("main changed too\n")
        (self.seed / "other.txt").write_text("from main\n")
        self.git(self.seed, "add", "product.txt", "other.txt")
        self.git(self.seed, "commit", "-m", "Another card merged")
        self.git(self.seed, "push")
        state = self.owned(state, "update", "--reason", "PR conflicts with main")
        self.assertEqual(state["stage"], "implement")
        self.assertEqual(state["updates"][-1]["conflicts"], ["product.txt"])
        self.assertEqual(set(state["artifacts"]), {"sync_before", "plan"})
        files = ["other.txt", "product.txt"]
        result = self.result(state, "implement", files=files,
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        self.assertIn("Unresolved merge conflict", self.checkpoint(state, "implement", result, success=False)["reason"])
        (self.repo / "product.txt").write_text("updated and main changed too\n")
        state = self.synced(self.checkpoint(state, "implement", result))
        self.owned(state, "verify")
        self.git(self.repo, "add", "--", *files)
        self.git(self.repo, "commit", "-m", "Merge main into the task branch")
        state = self.checkpoint(state, "handoff", self.result(state, "handoff", delivery_status="completed"))
        self.assertEqual(state["stage"], "qa")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD^2"), self.git(self.seed, "rev-parse", "HEAD"))
        self.assertIn("already contains", self.owned(state, "update", "--reason", "Again", success=False)["reason"])

    def test_update_refuses_when_remote_task_branch_moved(self):
        state = self.delivered()
        self.git(self.seed, "fetch", "origin", "codex/42-product")
        self.git(self.seed, "switch", "-c", "elsewhere", "FETCH_HEAD")
        (self.seed / "remote.txt").write_text("pushed elsewhere\n")
        self.git(self.seed, "add", "remote.txt")
        self.git(self.seed, "commit", "-m", "Branch updated on the remote")
        self.git(self.seed, "push", "origin", "HEAD:codex/42-product")
        self.git(self.seed, "switch", "main")
        (self.seed / "other.txt").write_text("from main\n")
        self.git(self.seed, "add", "other.txt")
        self.git(self.seed, "commit", "-m", "Another card merged")
        self.git(self.seed, "push")
        self.assertIn("remote task branch", self.owned(state, "update", "--reason", "Stale", success=False)["reason"])
        self.assertFalse((Path(self.git(self.repo, "rev-parse", "--absolute-git-dir")) / "MERGE_HEAD").exists())

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

    def test_final_sync_rejects_a_report_that_is_not_a_template_pr_body(self):
        state = self.begin()
        state = self.checkpoint(state, "plan", self.result(state, "plan"))
        (self.repo / "product.txt").write_text("updated\n")
        result = self.result(state, "implement", files=["product.txt"],
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        state = self.reviewed(self.checkpoint(state, "implement", result))
        result = self.result(state, "sync_after", files=["product.txt"], context_status="current",
                             requires_revalidation=False,
                             validation=[{"command": "git diff --check", "exit_code": 0}])
        report = Path(state["state_path"]).parent / "sync_after.md"
        for body, reason in (
                ("## Summary\n\nDone.\n\n## Files Changed\n\n- product.txt\n", "PR Preparation"),
                ("## PR Preparation\n\nDone.\n\n**Validation:** passes\n", "## Validation"),
                ("## PR Preparation\n\nDone.\n\n## Validation\n\nok\n\n## QA\n\n1. Open\n", "report sections")):
            report.write_text(f"# Report\n\n{body}")
            self.assertIn(reason, self.checkpoint(state, "sync_after", result, success=False)["reason"])
        report.write_text(f"# Report\n{self.PR_BODY}")
        self.assertEqual(self.checkpoint(state, "sync_after", result)["stage"], "handoff")

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
        report.write_text(f"# Report\n\n{qa}\n\n## Plan\n\nplan.md\n{self.PR_BODY}")
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
