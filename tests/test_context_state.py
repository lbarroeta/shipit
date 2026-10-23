"""Exercise context baselines against real disposable Git repositories."""

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
        (self.repo / "docs/code/rules").mkdir(parents=True)
        (self.repo / "docs/shipit").mkdir()
        self.config = {"paths": {"rules": "docs/code/rules"}, "language": {"plan": "es"}}
        (self.repo / "docs/shipit/config.json").write_text(json.dumps(self.config))
        (self.repo / "docs/code/stack.md").write_text("Stack evidence\n")
        (self.repo / "docs/code/conventions.md").write_text("Conventions evidence\n")
        (self.repo / "source.py").write_text("original = True\n")
        self.git("add", ".")
        self.git("commit", "-m", "Fixture")
        self.inventory = self.root / "inventory.json"
        self.managed = ["docs/shipit/config.json", "docs/code/stack.md", "docs/code/conventions.md"]
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
        state = self.repo / "docs/shipit/sync-state.json"
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
        (self.repo / "docs/code/stack.md").write_text("Human decision\n")
        result = self.call("inspect")
        self.assertEqual(result["source_changes"], ["new.py", "source.py"])
        self.assertEqual(result["edited_managed"], ["docs/code/stack.md"])
        saved = json.loads((self.repo / "docs/shipit/sync-state.json").read_text())
        self.assertEqual(saved["managed"]["docs/code/stack.md"]["base"], "Stack evidence\n")
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
        (self.repo / "docs/shipit/config.json").write_text(json.dumps(self.config))
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

    def test_conflicts_and_omitted_existing_rules_cannot_be_certified(self):
        (self.repo / "docs/code/rules/service.md").write_text("Generated\n")
        self.managed.append("docs/code/rules/service.md")
        self.write_inventory()
        self.call("record")
        state = (self.repo / "docs/shipit/sync-state.json").read_bytes()
        self.write_inventory(["Human conflict"])
        self.assertIn("unresolved", self.call("record", success=False)["reason"])
        self.managed.pop()
        self.write_inventory()
        self.assertIn("omitted", self.call("record", success=False)["reason"])
        self.assertEqual(state, (self.repo / "docs/shipit/sync-state.json").read_bytes())
        (self.repo / "docs/code/rules/service.md").unlink()
        self.assertEqual(self.call("record")["status"], "recorded")

    def test_human_docs_and_shared_contracts_cannot_be_adopted(self):
        (self.repo / "README.md").write_text("Human content\n")
        self.managed.append("README.md")
        self.write_inventory()
        self.assertIn("Not an init/sync-owned", self.call("record", success=False)["reason"])
        self.managed.pop()
        self.write_inventory()
        (self.repo / "docs/code/stack.md").unlink()
        outside = self.root / "shared.md"
        outside.write_text("Shared context\n")
        (self.repo / "docs/code/stack.md").symlink_to(outside)
        self.assertIn("Shared contract", self.call("record", success=False)["reason"])
        self.assertEqual(outside.read_text(), "Shared context\n")

    def test_section_in_human_doc_is_the_only_owned_text(self):
        section = "<!-- shipit:generated -->\nDetected\n<!-- /shipit:generated -->"
        conventions = self.repo / "docs/code/conventions.md"
        conventions.write_text(f"# Team rules\n\n{section}\n")
        self.call("record")
        saved = json.loads((self.repo / "docs/shipit/sync-state.json").read_text())
        self.assertEqual(saved["managed"]["docs/code/conventions.md"]["base"], section)
        conventions.write_text(f"# Team rules, edited\n\n{section}\n")
        result = self.call("inspect")
        self.assertEqual(result["edited_managed"], [])
        self.assertEqual(result["contract_changes"], ["docs/code/conventions.md"])
        conventions.write_text("# Team rules\n\n" + section.replace("Detected", "Human edit") + "\n")
        self.assertEqual(self.call("inspect")["edited_managed"], ["docs/code/conventions.md"])

    def test_legacy_contract_points_to_init(self):
        (self.repo / ".sdd").mkdir()
        (self.repo / "docs/shipit/config.json").rename(self.repo / ".sdd/config.json")
        self.assertIn("/shipit:init", self.call("inspect", success=False)["reason"])

    def test_configured_contract_paths_are_owned(self):
        self.config["paths"]["conventions"] = "docs/conventions.md"
        (self.repo / "docs/shipit/config.json").write_text(json.dumps(self.config))
        (self.repo / "docs/code/conventions.md").rename(self.repo / "docs/conventions.md")
        self.managed[2] = "docs/conventions.md"
        self.write_inventory()
        self.assertEqual(self.call("record")["status"], "recorded")
        (self.repo / "docs/conventions.md").write_text("Edited\n")
        result = self.call("inspect")
        self.assertEqual(result["edited_managed"], ["docs/conventions.md"])
        self.assertEqual(result["source_changes"], [])


if __name__ == "__main__":
    unittest.main()
