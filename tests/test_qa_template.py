import functools
import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "skills/qa/assets/qa-template.py"
CACHE = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or
             Path.home() / ("Library/Caches" if os.uname().sysname == "Darwin" else ".cache") / "ms-playwright")
CHECKS = '''
def AC1(page):
    """Orders list shows its heading"""
    page.goto("/")
    expect(page.get_by_role("heading", name="Orders")).to_be_visible()


def AC2(page):
    """Export says it is done"""
    page.goto("/")
    page.get_by_role("button", name="Export").click()
    expect(page.get_by_text("Export done")).to_be_visible(timeout=1000)


CHECKS = [AC1, AC2]
MANUAL = {"AC3": "needs a real email inbox"}
'''


@unittest.skipUnless(shutil.which("uv") and any(CACHE.glob("chromium*")), "needs uv and Playwright's Chromium")
class QaTemplateTests(unittest.TestCase):
    def test_records_each_criterion_and_reports_pass_fail_manual(self):
        with tempfile.TemporaryDirectory() as tmp:
            site, out = Path(tmp, "site"), Path(tmp, "out")
            site.mkdir()
            (site / "index.html").write_text(
                "<!doctype html><title>Orders</title><h1>Orders</h1>"
                "<button onclick=\"document.querySelector('p').hidden=false\">Export</button><p hidden>Export ready</p>")
            server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(SimpleHTTPRequestHandler, directory=site))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)

            source = TEMPLATE.read_text()
            start, end = source.index("# --- fill from here"), source.index("# --- to here")
            script = Path(tmp, "qa.py")
            script.write_text(source[:source.index("\n", start) + 1] + CHECKS + "\n" + source[end:])

            subprocess.run(["uv", "run", "--quiet", str(script), str(out), f"http://127.0.0.1:{server.server_port}"],
                           check=True, capture_output=True, timeout=300)

            results = {row["ac"]: row for row in json.loads((out / "results.json").read_text())}
            self.assertEqual({ac: row["outcome"] for ac, row in results.items()},
                             {"AC1": "pass", "AC2": "fail", "AC3": "manual"})
            self.assertIn("Export done", results["AC2"]["error"])
            for name in ("AC1.webm", "AC2.webm", "AC1-trace.zip", "AC2-trace.zip", "AC2.png"):
                self.assertGreater((out / name).stat().st_size, 0, name)
            self.assertFalse((out / "AC1.png").exists())
            self.assertEqual(sorted(p.name for p in out.glob("*.webm")), ["AC1.webm", "AC2.webm"])


if __name__ == "__main__":
    unittest.main()
