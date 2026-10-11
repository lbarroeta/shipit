import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import release_version as release


class ReleaseVersionTests(unittest.TestCase):
    def test_semantic_levels(self):
        self.assertEqual(release.commit_level("fix: correct plan output"), 1)
        self.assertEqual(release.commit_level("feat(run): support resume"), 2)
        self.assertEqual(release.commit_level("feat!: remove old command"), 3)
        self.assertEqual(release.commit_level("fix: change API\n\nBREAKING CHANGE: old form removed"), 3)
        self.assertEqual(release.commit_level("update some text"), 0)

    def test_breaking_before_and_after_one_point_zero(self):
        self.assertEqual(release.next_version((0, 11, 0), 3), (0, 12, 0))
        self.assertEqual(release.next_version((1, 11, 0), 3), (2, 0, 0))
        self.assertEqual(release.next_version((0, 11, 2), 2), (0, 12, 0))
        self.assertEqual(release.next_version((0, 11, 2), 1), (0, 11, 3))

    def test_public_entrypoint_rename_is_breaking(self):
        changes = [("R", "skills/code-plan/SKILL.md", "skills/plan/SKILL.md")]
        self.assertEqual(release.change_level(changes, []), 3)

    def test_new_skill_is_minor(self):
        self.assertEqual(release.change_level([("A", "skills/status/SKILL.md", None)], []), 2)

    def test_untyped_content_change_is_patch(self):
        self.assertEqual(release.change_level([("M", "skills/run/references/orchestration.md", None)], []), 1)

    def test_frontmatter_name_change_is_breaking(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "skills" / "run" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text("---\nname: new-run\n---\n")
            with patch.object(release, "ROOT", root), patch.object(release, "git", return_value="---\nname: run\n---\n"):
                self.assertEqual(release.change_level([("M", "skills/run/SKILL.md", None)], [], "v0.1.0"), 3)

    def test_docs_only_commits_do_not_raise_release_level(self):
        def fake_git(*args):
            return "README.md" if args[0] == "diff-tree" else "feat: edit docs"

        with patch.object(release, "git", side_effect=fake_git):
            self.assertEqual(release.change_level([("M", "skills/run/references/orchestration.md", None)], ["abc"]), 1)

    def test_write_keeps_all_three_versions_in_sync(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative, key in release.VERSION_FILES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({key: "0.11.0", "keep": True}) + "\n")
            with patch.object(release, "ROOT", root):
                release.write_versions("0.12.0")
            for relative, key in release.VERSION_FILES:
                self.assertEqual(json.loads((root / relative).read_text()), {key: "0.12.0", "keep": True})

    def test_cli_bumps_committed_fix_and_writes_all_versions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = root / "scripts" / "release_version.py"
            script.parent.mkdir(parents=True)
            shutil.copyfile(release.__file__, script)
            for relative, key in release.VERSION_FILES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({key: "0.11.0"}) + "\n")
            skill = root / "skills" / "run" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: run\n---\nOriginal\n")

            def git(*arguments):
                subprocess.run(("git", *arguments), cwd=root, check=True, capture_output=True)

            git("init")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.com")
            git("add", ".")
            git("commit", "-m", "initial")
            git("tag", "v0.11.0")
            skill.write_text("---\nname: run\n---\nFixed\n")
            git("commit", "-am", "fix: correct run instructions")

            result = subprocess.run((sys.executable, str(script), "--write"), cwd=root,
                                    check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(result.stdout)["version"], "0.11.1")
            for relative, key in release.VERSION_FILES:
                self.assertEqual(json.loads((root / relative).read_text())[key], "0.11.1")


if __name__ == "__main__":
    unittest.main()
