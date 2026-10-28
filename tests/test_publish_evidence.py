"""Exercise evidence publishing against disposable local Git repositories."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/code-handoff/scripts/publish_evidence.py"


class PublishEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        directory = Path(self.temp.name)
        self.remote = directory / "remote.git"
        self.repo = directory / "repo"
        self.evidence = directory / "evidence"
        self.evidence.mkdir()
        self.git(directory, "init", "--bare", "--initial-branch=main", str(self.remote))
        self.git(directory, "init", "--initial-branch=main", str(self.repo))
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("commit.gpgsign", "false")):
            self.git(self.repo, "config", key, value)
        (self.repo / "product.txt").write_text("work in progress\n")
        self.git(self.repo, "remote", "add", "origin", str(self.remote))

    def git(self, repo, *args):
        result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def publish(self, prefix, success=True):
        result = subprocess.run([sys.executable, str(HELPER), "--repo", str(self.repo),
                                 "--prefix", prefix, "--dir", str(self.evidence)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_publishes_and_appends_without_touching_checkout(self):
        (self.evidence / "ac1.png").write_bytes(b"png-1")
        first = self.publish("ENG-1/run-1")
        self.assertEqual(first["files"], ["ENG-1/run-1/ac1.png"])
        (self.evidence / "ac1.png").write_bytes(b"png-2")
        self.publish("ENG-2/run-1")
        tree = self.git(self.remote, "ls-tree", "-r", "--name-only", "shipit-evidence")
        self.assertEqual(tree.splitlines(), ["ENG-1/run-1/ac1.png", "ENG-2/run-1/ac1.png"])
        self.assertEqual(self.git(self.remote, "show", "shipit-evidence:ENG-1/run-1/ac1.png"), "png-1")
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "?? product.txt")
        self.assertEqual(self.git(self.repo, "branch", "--list"), "")

    def test_rejects_escaping_prefix_and_empty_evidence(self):
        self.assertIn("No evidence", self.publish("ENG-1", success=False)["reason"])
        (self.evidence / "ac1.png").write_bytes(b"png")
        self.assertIn("--prefix", self.publish("../main", success=False)["reason"])


if __name__ == "__main__":
    unittest.main()
