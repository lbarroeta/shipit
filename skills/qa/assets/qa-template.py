# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.64.1"]
# ///
"""shipit qa: each acceptance criterion in its own headless browser session, recorded.

    uv run [--env-file <ignored env file>] qa.py <out-dir> <base-url>

Headless: nothing opens on screen, so the machine stays free while it runs.
Writes <AC>.webm, <AC>-trace.zip, <AC>.png on failure, and results.json.
"""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import expect, sync_playwright

# --- fill from here: one function per criterion, named by its ID, in order ---


def login(page):
    page.goto("/login")
    page.get_by_label("Email").fill(os.environ["QA_USER"])
    page.get_by_label("Password").fill(os.environ["QA_PASSWORD"])
    page.get_by_role("button", name="Log in").click()


def AC1(page):
    """<the criterion, in the ticket's words>"""
    login(page)
    page.goto("/orders")
    expect(page.get_by_role("heading", name="Orders")).to_be_visible()


CHECKS = [AC1]
MANUAL = {}  # "AC3": "why a browser cannot prove it", e.g. "needs a real email inbox"

# --- to here; the runner below stays as is ---

SIZE = {"width": 1280, "height": 720}


def main(out, base_url):
    out.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(slow_mo=300)  # slowed so a person can follow the video
        for check in CHECKS:
            name = check.__name__
            result = {"ac": name, "criterion": (check.__doc__ or "").strip(), "outcome": "pass"}
            context = browser.new_context(base_url=base_url, viewport=SIZE,
                                          record_video_dir=out, record_video_size=SIZE)
            context.tracing.start(screenshots=True, snapshots=True)
            page = context.new_page()
            try:
                check(page)
            except (AssertionError, PlaywrightError) as error:  # anything else is a broken script: let it raise
                # one line with the call log, which names the locator; the page snapshot is in the trace
                message = str(error).split("Aria snapshot:")[0] or type(error).__name__
                result.update(outcome="fail", url=page.url, error=" ".join(message.split())[:500])
                page.screenshot(path=out / f"{name}.png")
                result["screenshot"] = f"{name}.png"
            page.wait_for_timeout(1000)  # hold the final state on the last frames of the video
            context.tracing.stop(path=out / f"{name}-trace.zip")
            context.close()
            Path(page.video.path()).replace(out / f"{name}.webm")
            results.append({**result, "video": f"{name}.webm", "trace": f"{name}-trace.zip"})
        browser.close()
    results += [{"ac": ac, "outcome": "manual", "reason": reason} for ac, reason in MANUAL.items()]
    (out / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), sys.argv[2])
