# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.64.1"]
# ///
"""shipit qa: each acceptance criterion in its own headless browser session, recorded.

    uv run [--env-file <ignored env file>] qa.py <out-dir> <base-url> [--recon | --baseline] [AC ...]

Headless: nothing opens on screen, so the machine stays free while it runs.
--recon     runs recon() only: what each screen shows and how many elements each locator matches.
--baseline  runs the checks against the code before the change, into <out-dir>/baseline/.
AC ...      runs only those criteria; the earlier evidence of each moves to round-N/.
Writes <AC>.webm, <AC>-trace.zip, <AC>.png on failure, and results.json.
"""
import json
import os
import shutil
import sys
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import expect, sync_playwright

# --- fill from here: recon first, then one function per criterion, named by its ID, in order ---


def login(page):
    page.goto("/login")
    page.get_by_label("Email").fill(os.environ["QA_USER"])
    page.get_by_label("Password").fill(os.environ["QA_PASSWORD"])
    page.get_by_role("button", name="Log in").click()


def recon(page):
    """Each screen the criteria name, with the locators the checks will use."""
    login(page)
    page.goto("/orders")
    look(page, "orders", heading=page.get_by_role("heading", name="Orders"))


def AC1(page):
    """<the criterion, in the ticket's words>"""
    login(page)
    page.goto("/orders")
    expect(page.get_by_role("heading", name="Orders")).to_be_visible()


CHECKS = [AC1]
MANUAL = {}  # "AC3": "why a browser cannot prove it", e.g. "needs a real email inbox"

# --- to here; the runner below stays as is ---

SIZE = {"width": 1280, "height": 720}
FLAGS = {arg for arg in sys.argv[1:] if arg.startswith("--")}
ARGS = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
ROOT = Path(ARGS[0]).resolve()
BASELINE = "--baseline" in FLAGS
OUT = ROOT / "baseline" if BASELINE else ROOT


def look(page, name, **locators):
    """Recon: keep what a screen shows and how many elements each locator matches. A check needs exactly 1."""
    folder = ROOT / "recon"
    folder.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=folder / f"{name}.png", full_page=True)
    (folder / f"{name}.aria.yml").write_text(page.locator("body").aria_snapshot())
    matches = {label: locator.count() for label, locator in locators.items()}
    print(json.dumps({"screen": name, "url": page.url, "matches": matches}, ensure_ascii=False))


def same_as_before(key, value):
    """For "unchanged" criteria: the --baseline run records value, the real run must find the same."""
    path = ROOT / "baseline" / f"{key}.json"
    value = json.loads(json.dumps(value))
    if BASELINE:
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        return
    assert path.is_file(), f"no baseline for {key}: run with --baseline on the base commit first"
    before = json.loads(path.read_text())
    assert before == value, f"{key} changed: before {before}, now {value}"


def keep_previous_round(names):
    """A rerun never overwrites evidence: the earlier files of these criteria move to round-N/."""
    old = [path for name in names for pattern in (f"{name}.*", f"{name}-trace.zip") for path in OUT.glob(pattern)]
    if not old:
        return
    folder = OUT / f"round-{len(list(OUT.glob('round-*'))) + 1}"
    folder.mkdir()
    for path in old:
        path.replace(folder / path.name)
    if (OUT / "results.json").is_file():
        shutil.copy(OUT / "results.json", folder / "results.json")


def main(base_url, only):
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        if "--recon" in FLAGS:
            browser = playwright.chromium.launch()
            recon(browser.new_context(base_url=base_url, viewport=SIZE).new_page())
            browser.close()
            return
        checks = [check for check in CHECKS if not only or check.__name__ in only]
        keep_previous_round([check.__name__ for check in checks])
        results = []
        browser = playwright.chromium.launch(slow_mo=300)  # slowed so a person can follow the video
        for check in checks:
            name = check.__name__
            result = {"ac": name, "criterion": (check.__doc__ or "").strip(), "outcome": "pass"}
            known = set(OUT.glob("*.webm"))
            context = browser.new_context(base_url=base_url, viewport=SIZE,
                                          record_video_dir=OUT, record_video_size=SIZE)
            context.tracing.start(screenshots=True, snapshots=True)
            page = context.new_page()
            try:
                check(page)
            except (AssertionError, PlaywrightError) as error:  # anything else is a broken script: let it raise
                # one line with the call log, which names the locator; the page snapshot is in the trace
                message = str(error).split("Aria snapshot:")[0] or type(error).__name__
                result.update(outcome="fail", url=page.url, error=" ".join(message.split())[:500])
                page.screenshot(path=OUT / f"{name}.png")
                result["screenshot"] = f"{name}.png"
            page.wait_for_timeout(1000)  # hold the final state on the last frames of the video
            context.tracing.stop(path=OUT / f"{name}-trace.zip")
            context.close()
            Path(page.video.path()).replace(OUT / f"{name}.webm")
            extra = sorted(set(OUT.glob("*.webm")) - known - {OUT / f"{name}.webm"})
            for index, video in enumerate(extra, start=2):  # a check that opened more tabs keeps each one's video
                video.replace(OUT / f"{name}-tab{index}.webm")
            results.append({**result, "video": f"{name}.webm", "trace": f"{name}-trace.zip"})
        browser.close()
    path = OUT / "results.json"
    rows = {row["ac"]: row for row in (json.loads(path.read_text()) if path.is_file() else [])}
    rows.update({row["ac"]: row for row in results})  # criteria this run skipped keep their last result
    before = ROOT / "baseline" / "results.json"
    if not BASELINE and before.is_file():  # a pass that also passed before the change proves nothing new
        outcomes = {row["ac"]: row["outcome"] for row in json.loads(before.read_text())}
        for row in rows.values():
            row["before"] = outcomes.get(row["ac"])
    results = [rows[check.__name__] for check in CHECKS if check.__name__ in rows]
    results += [{"ac": ac, "outcome": "manual", "reason": reason} for ac, reason in MANUAL.items()]
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(ARGS[1], ARGS[2:])
