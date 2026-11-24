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

BEFORE_AFTER = '''
def recon(page):
    page.goto("/")
    look(page, "home", heading=page.get_by_role("heading", name="Orders"), export=page.get_by_role("button", name="Export"))


def AC1(page):
    """The page says new"""
    page.goto("/")
    expect(page.get_by_text("new", exact=True)).to_be_visible(timeout=1000)


def AC2(page):
    """The heading is the same as before"""
    page.goto("/")
    same_as_before("heading", page.get_by_role("heading").inner_text())


CHECKS = [AC1, AC2]
MANUAL = {}
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

    def test_recon_baseline_and_single_criterion_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            site, out = Path(tmp, "site"), Path(tmp, "out")
            site.mkdir()
            page = "<!doctype html><title>Orders</title><h1>Orders</h1><p>%s</p><button>Export</button><button>Export</button>"
            (site / "index.html").write_text(page % "old")
            server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(SimpleHTTPRequestHandler, directory=site))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)

            source = TEMPLATE.read_text()
            start, end = source.index("# --- fill from here"), source.index("# --- to here")
            script = Path(tmp, "qa.py")
            script.write_text(source[:source.index("\n", start) + 1] + BEFORE_AFTER + "\n" + source[end:])

            def run(*extra):
                done = subprocess.run(["uv", "run", "--quiet", str(script), str(out),
                                       f"http://127.0.0.1:{server.server_port}", *extra],
                                      check=True, capture_output=True, text=True, timeout=300)
                return done.stdout

            # recon: two Export buttons, so a check that clicks "Export" would be ambiguous
            self.assertEqual(json.loads(run("--recon"))["matches"], {"heading": 1, "export": 2})
            self.assertGreater((out / "recon/home.png").stat().st_size, 0)
            self.assertIn("Orders", (out / "recon/home.aria.yml").read_text())
            self.assertFalse((out / "results.json").exists())

            run("--baseline")  # the code before the change
            (site / "index.html").write_text(page % "new")
            run()
            results = {row["ac"]: row for row in json.loads((out / "results.json").read_text())}
            # AC1 fails before and passes now: the check sees the change. AC2 holds on both sides.
            self.assertEqual({ac: (row["before"], row["outcome"]) for ac, row in results.items()},
                             {"AC1": ("fail", "pass"), "AC2": ("pass", "pass")})
            self.assertTrue((out / "baseline/AC1.webm").is_file())

            run("AC1")  # one criterion again: its earlier evidence is kept, AC2's result stays
            self.assertTrue((out / "round-1/AC1.webm").is_file())
            self.assertTrue((out / "AC2.webm").is_file())
            self.assertEqual(sorted(row["ac"] for row in json.loads((out / "results.json").read_text())), ["AC1", "AC2"])


if __name__ == "__main__":
    unittest.main()
