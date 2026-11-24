#!/usr/bin/env python3
"""Start the local services a QA run needs, and stop only the ones it started.

    services.py up <repo> <attempt folder>   # reads qa.services from <repo>/.shipit/config.json
    services.py down <attempt folder>

`up` leaves a service alone when its url already answers, starts the rest in their
own process group (log: <folder>/<name>.log), waits for every url, and records what
it started in <folder>/services.json. It prints one JSON row per service and exits
non-zero when any is not answering. `down` stops only what services.json records.
Standard library only.
"""
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
DEFAULT_TIMEOUT = 180


def answers(url):
    try:
        urllib.request.urlopen(url, timeout=3).close()
    except urllib.error.HTTPError:
        return True  # any HTTP status means a server is listening
    except (OSError, ValueError):
        return False
    return True


def is_local(url):
    host = urlsplit(url).hostname or ""
    return host in LOCAL_HOSTS or host.endswith(".localhost")


def tail(path, lines=20):
    return path.read_text(errors="replace").splitlines()[-lines:] if path.exists() else []


def up(repo, folder):
    config = json.loads((repo / ".shipit/config.json").read_text())
    services = (config.get("qa") or {}).get("services") or []
    folder.mkdir(parents=True, exist_ok=True)
    rows, started = [], []
    for svc in services:
        name, url = svc["name"], svc["url"]
        row = {"name": name, "url": url}
        rows.append(row)
        if answers(url):
            row["status"] = "already_running"
        elif not is_local(url):
            row["status"] = "not_local"  # never started: checks would write to a shared environment
        elif not svc.get("start"):
            row["status"] = "no_start_command"
        else:
            log = folder / f"{name}.log"
            proc = subprocess.Popen(svc["start"], shell=True, cwd=(repo / svc.get("cwd", ".")).resolve(),
                                    stdout=log.open("ab"), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                    start_new_session=True)
            started.append({"name": name, "pid": proc.pid})
            row.update(status="starting", log=str(log), proc=proc,
                       deadline=time.monotonic() + svc.get("timeout", DEFAULT_TIMEOUT))
    (folder / "services.json").write_text(json.dumps(started, indent=2) + "\n")

    waiting = [r for r in rows if r["status"] == "starting"]
    while waiting:
        for row in list(waiting):
            if answers(row["url"]):
                row["status"] = "started"
            elif row["proc"].poll() is not None:
                row.update(status="exited", exit=row["proc"].returncode, log_tail=tail(Path(row["log"])))
            elif time.monotonic() > row["deadline"]:
                row.update(status="timeout", log_tail=tail(Path(row["log"])))
            else:
                continue
            waiting.remove(row)
        if waiting:
            time.sleep(2)
    for row in rows:
        row.pop("proc", None)
        row.pop("deadline", None)
    print(json.dumps(rows, indent=2))
    return 0 if all(r["status"] in ("already_running", "started") for r in rows) else 1


def down(folder):
    record = folder / "services.json"
    started = json.loads(record.read_text()) if record.exists() else []
    for svc in started:
        try:
            os.killpg(svc["pid"], signal.SIGTERM)
        except ProcessLookupError:
            continue
        for _ in range(20):
            time.sleep(0.5)
            try:
                os.killpg(svc["pid"], 0)
            except ProcessLookupError:
                break
        else:
            os.killpg(svc["pid"], signal.SIGKILL)
    record.write_text("[]\n")
    print(json.dumps([s["name"] for s in started]))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "up":
        sys.exit(up(Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()))
    if len(sys.argv) == 3 and sys.argv[1] == "down":
        sys.exit(down(Path(sys.argv[2]).resolve()))
    sys.exit(__doc__)
