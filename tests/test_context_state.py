"""Exercise context baselines against real disposable Git repositories."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "skills/sync/scripts/context_state.py"


class ContextStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "--initial-branch=main")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.git("config", "commit.gpgsign", "false")
        (self.repo / ".shipit/rules").mkdir(parents=True)
        self.config = {"paths": {"rules": ".shipit/rules"}, "language": {"plan": "es"}}
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        (self.repo / ".shipit/stack.md").write_text("Stack evidence\n")
        (self.repo / ".shipit/conventions.md").write_text("Conventions evidence\n")
        (self.repo / "source.py").write_text("original = True\n")
        self.git("add", ".")
        self.git("commit", "-m", "Fixture")
        self.inventory = self.root / "inventory.json"
        self.managed = [".shipit/config.json", ".shipit/stack.md", ".shipit/conventions.md"]
        self.write_inventory()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True,
                                       stderr=subprocess.DEVNULL).strip()

    def write_inventory(self, unresolved=None):
        self.inventory.write_text(json.dumps({"managed": self.managed, "unresolved": unresolved or []}))

    def call(self, command, success=True):
        args = [sys.executable, str(HELPER), "--repo", str(self.repo), command]
        if command == "record":
            args.extend(["--inventory", str(self.inventory)])
        result = subprocess.run(args, text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_read_only_legacy_inspection_and_idempotent_baseline(self):
        self.assertEqual(self.call("inspect")["status"], "uninitialized")
        state = self.repo / ".shipit/sync-state.json"
        self.assertFalse(state.exists())
        self.assertEqual(self.call("record")["status"], "recorded")
        before = state.read_bytes(), state.stat().st_mtime_ns
        self.assertEqual(self.call("inspect")["status"], "unchanged")
        self.assertEqual(self.call("record")["status"], "unchanged")
        self.assertEqual(before, (state.read_bytes(), state.stat().st_mtime_ns))
        self.git("add", ".")
        self.git("commit", "-m", "Save contract")
        self.assertEqual(self.call("inspect")["status"], "unchanged")
        self.assertEqual(self.call("record")["status"], "unchanged")

    def test_added_deleted_and_changed_sources_and_human_edit(self):
        self.call("record")
        (self.repo / "source.py").unlink()
        (self.repo / "new.py").write_text("new = True\n")
        (self.repo / ".shipit/stack.md").write_text("Human decision\n")
        result = self.call("inspect")
        self.assertEqual(result["source_changes"], ["new.py", "source.py"])
        self.assertEqual(result["edited_managed"], [".shipit/stack.md"])
        saved = json.loads((self.repo / ".shipit/sync-state.json").read_text())
        self.assertEqual(saved["managed"][".shipit/stack.md"]["base"], "Stack evidence\n")
        self.assertNotIn("original = True", json.dumps(saved))

    def test_modes_and_symlink_targets_are_evidence(self):
        (self.repo / "link").symlink_to("missing-a")
        self.call("record")
        (self.repo / "source.py").chmod(0o755)
        (self.repo / "link").unlink()
        (self.repo / "link").symlink_to("missing-b")
        self.assertEqual(self.call("inspect")["source_changes"], ["link", "source.py"])

    def test_rules_design_and_custom_paths_without_plan_churn(self):
        self.config["paths"].update(rules="rules", plans="plans", tasks="drafts")
        (self.repo / ".shipit/config.json").write_text(json.dumps(self.config))
        for directory in ("rules", "plans", "drafts", "graphify-out"):
            (self.repo / directory).mkdir()
        (self.repo / "rules/service.md").write_text("Generated rule\n")
        self.managed.append("rules/service.md")
        self.write_inventory()
        self.call("record")
        for name in ("plans/task.md", "drafts/task.md", "graphify-out/graph.json"):
            (self.repo / name).write_text("ephemeral\n")
        self.assertEqual(self.call("inspect")["status"], "unchanged")
        (self.repo / "rules/design.md").write_text("User-owned design\n")
        self.assertEqual(self.call("inspect")["contract_changes"], ["rules/design.md"])
        self.managed.append("rules/design.md")
        self.write_inventory()
        self.assertIn("Not an init/sync-owned", self.call("record", success=False)["reason"])

    def test_product_docs_are_reported_but_never_adopted(self):
        self.call("record")
        (self.repo / ".shipit/product").mkdir()
        (self.repo / ".shipit/product/prd.md").write_text("H1 (built)\n")
        (self.repo / ".shipit/backlog.md").write_text("T1\n")
        self.assertEqual(self.call("inspect")["contract_changes"],
                         [".shipit/backlog.md", ".shipit/product/prd.md"])
        self.managed.append(".shipit/product/prd.md")
        self.write_inventory()
        self.assertIn("Not an init/sync-owned", self.call("record", success=False)["reason"])

    def test_conflicts_and_omitted_existing_rules_cannot_be_certified(self):
        (self.repo / ".shipit/rules/service.md").write_text("Generated\n")
        self.managed.append(".shipit/rules/service.md")
        self.write_inventory()
        self.call("record")
        state = (self.repo / ".shipit/sync-state.json").read_bytes()
        self.write_inventory(["Human conflict"])
        self.assertIn("unresolved", self.call("record", success=False)["reason"])
        self.managed.pop()
        self.write_inventory()
        self.assertIn("omitted", self.call("record", success=False)["reason"])
        self.assertEqual(state, (self.repo / ".shipit/sync-state.json").read_bytes())
        (self.repo / ".shipit/rules/service.md").unlink()
        self.assertEqual(self.call("record")["status"], "recorded")

    def test_human_docs_and_shared_contracts_cannot_be_adopted(self):
        (self.repo / "README.md").write_text("Human content\n")
        self.managed.append("README.md")
        self.write_inventory()
        self.assertIn("Not an init/sync-owned", self.call("record", success=False)["reason"])
        self.managed.pop()
        self.write_inventory()
        (self.repo / ".shipit/stack.md").unlink()
        outside = self.root / "shared.md"
        outside.write_text("Shared context\n")
        (self.repo / ".shipit/stack.md").symlink_to(outside)
        self.assertIn("Shared contract", self.call("record", success=False)["reason"])
        self.assertEqual(outside.read_text(), "Shared context\n")

    def test_baseline_hashes_only_uncommitted_sources_and_reads_legacy(self):
        (self.repo / "draft.py").write_text("draft = True\n")
        self.call("record")
        state = self.repo / ".shipit/sync-state.json"
        saved = json.loads(state.read_text())
        self.assertEqual((saved["version"], list(saved["dirty"])), (2, ["draft.py"]))
        self.assertNotIn("source.py", json.dumps(saved))
        (self.repo / "source.py").write_text("committed = True\n")
        self.git("commit", "-am", "Change source")
        self.assertEqual(self.call("inspect")["source_changes"], ["source.py"])
        (self.repo / "source.py").write_text("original = True\n")
        self.assertEqual(self.call("inspect")["source_changes"], [])
        self.git("add", "draft.py")
        self.git("commit", "-m", "Commit the draft unchanged")
        self.assertEqual(self.call("inspect")["status"], "unchanged")
        self.assertEqual(self.call("record")["status"], "unchanged")
        legacy = {key: saved[key] for key in ("head", "contracts", "managed")}
        legacy.update(version=1, sources={"source.py": saved["dirty"]["draft.py"] | {
            "sha256": hashlib.sha256(b"original = True\n").hexdigest()}})
        state.write_text(json.dumps(legacy))
        self.assertEqual(self.call("inspect")["source_changes"], ["draft.py"])
        self.assertEqual(self.call("record")["status"], "recorded")
        self.assertEqual(json.loads(state.read_text())["version"], 2)

    def test_legacy_contract_points_to_init(self):
        (self.repo / ".shipit").rename(self.repo / ".sdd")
        self.assertIn("/shipit:init", self.call("inspect", success=False)["reason"])


if __name__ == "__main__":
    unittest.main()
