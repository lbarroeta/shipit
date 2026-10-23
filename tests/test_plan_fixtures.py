"""Check reproducible planning inputs and mutation detection, not model quality."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "plan_fixtures", ROOT / "evals/plan-consistency/prepare.py")
FIXTURES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURES)


class PlanFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_repeats_have_identical_inputs_and_runnable_baselines(self):
        for case in FIXTURES.CASES:
            with self.subTest(case=case):
                first, second = self.root / f"{case}-a", self.root / f"{case}-b"
                a = FIXTURES.prepare(case, first)
                b = FIXTURES.prepare(case, second)
                self.assertEqual(a, b)
                self.assertEqual(a["dirty_status"], "M app/labels.py" if case == "localized" else "")
                result = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                    cwd=first / "repo", capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(FIXTURES.verify(first)["unchanged_inputs"])

    def test_preserves_actual_bug_and_relevant_user_edit(self):
        destination = self.root / "localized"
        FIXTURES.prepare("localized", destination)
        result = subprocess.run(
            [sys.executable, "-c", "import json; from app.labels import normalize_label, search_key; "
             "print(json.dumps([normalize_label('  Big\\t CAT '), normalize_label('Straße'), search_key(None)]))"],
            cwd=destination / "repo", capture_output=True, text=True, check=True,
        )
        self.assertEqual(json.loads(result.stdout), ["big\t cat", "straße", ""])

    def test_allows_plan_but_detects_code_and_index_mutations(self):
        destination = self.root / "permissions"
        FIXTURES.prepare("permissions", destination)
        repo = destination / "repo"
        plans = repo / "docs/plans"
        plans.mkdir()
        (plans / "plan.md").write_text("Plan output\n")
        self.assertTrue(FIXTURES.verify(destination)["unchanged_inputs"])
        source = repo / "app/policy.py"
        original = source.read_text()
        source.write_text(original + "# Implementation is forbidden\n")
        self.assertIn("repo/app/policy.py", FIXTURES.verify(destination)["mismatches"])
        FIXTURES.git(repo, "add", "app/policy.py")
        source.write_text(original)
        self.assertIn("repo staged/unstaged state", FIXTURES.verify(destination)["mismatches"])

    def test_rejects_existing_destination_and_detects_plugin_drift(self):
        destination = self.root / "ambiguity"
        FIXTURES.prepare("ambiguity", destination)
        with self.assertRaises(ValueError):
            FIXTURES.prepare("ambiguity", destination)
        skill = destination / "plugin/skills/code-plan/SKILL.md"
        skill.write_text(skill.read_text() + "Changed instructions\n")
        self.assertIn("plugin/skills/code-plan/SKILL.md", FIXTURES.verify(destination)["mismatches"])


if __name__ == "__main__":
    unittest.main()
