import json
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/qa/scripts/services.py"
sys.path.insert(0, str(SCRIPT.parent))
from services import answers  # noqa: E402


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class QaServicesTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=60)

    def write_config(self, repo, services):
        (repo / ".shipit").mkdir()
        (repo / ".shipit/config.json").write_text(json.dumps({"qa": {"services": services}}))

    def test_leaves_a_running_service_alone_and_stops_only_its_own(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, folder = Path(tmp, "repo"), Path(tmp, "attempt")
            repo.mkdir()
            serve = [sys.executable, "-m", "http.server", "--bind", "127.0.0.1"]
            ours, theirs = free_port(), free_port()
            external = subprocess.Popen([*serve, str(theirs)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.addCleanup(external.wait)
            self.addCleanup(external.kill)
            for _ in range(50):
                if answers(f"http://127.0.0.1:{theirs}"):
                    break
                time.sleep(0.1)
            self.write_config(repo, [
                {"name": "api", "url": f"http://127.0.0.1:{theirs}", "start": "false"},
                {"name": "web", "url": f"http://127.0.0.1:{ours}", "start": " ".join([*serve, str(ours)]), "timeout": 30},
            ])
            result = self.run_script("up", str(repo), str(folder))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual({r["name"]: r["status"] for r in json.loads(result.stdout)},
                             {"api": "already_running", "web": "started"})

            self.assertEqual(json.loads(self.run_script("down", str(folder)).stdout), ["web"])
            self.assertFalse(answers(f"http://127.0.0.1:{ours}"))
            self.assertTrue(answers(f"http://127.0.0.1:{theirs}"))
            self.assertIsNone(external.poll())

    def test_up_reports_and_down_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, folder = Path(tmp, "repo"), Path(tmp, "attempt")
            repo.mkdir()
            port = free_port()
            self.write_config(repo, [{"name": "web", "url": f"http://127.0.0.1:{port}",
                                      "start": f"{sys.executable} -m http.server --bind 127.0.0.1 {port}", "timeout": 30}])
            result = self.run_script("up", str(repo), str(folder))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)[0]["status"], "started")
            self.assertEqual(json.loads(self.run_script("down", str(folder)).stdout), ["web"])
            again = self.run_script("up", str(repo), str(folder))  # stopped → started again, not already running
            self.assertEqual(json.loads(again.stdout)[0]["status"], "started")
            self.run_script("down", str(folder))

    def test_never_starts_a_non_local_service_and_reports_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, folder = Path(tmp, "repo"), Path(tmp, "attempt")
            repo.mkdir()
            self.write_config(repo, [
                {"name": "staging", "url": "http://staging.invalid", "start": "touch started"},
                {"name": "broken", "url": f"http://127.0.0.1:{free_port()}", "start": "echo boom; exit 3"},
            ])
            result = self.run_script("up", str(repo), str(folder))
            self.assertEqual(result.returncode, 1)
            rows = {r["name"]: r for r in json.loads(result.stdout)}
            self.assertEqual(rows["staging"]["status"], "not_local")
            self.assertFalse((repo / "started").exists())
            self.assertEqual((rows["broken"]["status"], rows["broken"]["exit"]), ("exited", 3))
            self.assertIn("boom", rows["broken"]["log_tail"])


if __name__ == "__main__":
    unittest.main()
