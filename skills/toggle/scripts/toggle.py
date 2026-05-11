#!/usr/bin/env python3
"""
Fetch Toggle workflow data and print the raw JSON response.
With --persist, also save the data into the memory folder as markdown.
On each run, checks cron status and prints guidance for the agent.
Reads TOGGLE_API_KEY from the environment.
"""

import os
import sys
import json
import re
import argparse
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_BASE = "https://ai-x.toggle.pro/public-openclaw/workflows"
TOGGLE_START = "<!-- toggle-data-start -->"
TOGGLE_END = "<!-- toggle-data-end -->"

CRON_JOB_KEYWORD = "toggle"
CRON_JOBS_PATH = os.path.expanduser("~/.openclaw/cron/jobs.json")

SKILL_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = SKILL_DIR / "state.yaml"


# ---------------------------------------------------------------------------
# State helpers (minimal YAML — key: value, one per line)
# ---------------------------------------------------------------------------

def read_state() -> dict:
    if not STATE_PATH.exists():
        STATE_PATH.write_text(
            "# Toggle skill state — managed by the agent, read by toggle.py\n"
            "# Set cron_disabled to true if the user doesn't want automatic sync\n"
            "cron_disabled: false\n"
        )
        print(f"[toggle] Created default state.yaml at {STATE_PATH}", file=sys.stderr)
        return {"cron_disabled": False}
    state = {}
    for line in STATE_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip()
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        state[key.strip()] = val
    return state


# ---------------------------------------------------------------------------
# Cron check
# ---------------------------------------------------------------------------

def find_toggle_cron() -> dict | None:
    """Return the first cron job whose name contains the keyword, or None."""
    if not os.path.exists(CRON_JOBS_PATH):
        return None
    try:
        with open(CRON_JOBS_PATH) as f:
            data = json.load(f)
        for job in data.get("jobs", []):
            if CRON_JOB_KEYWORD in job.get("name", "").lower():
                return job
    except (json.JSONDecodeError, OSError):
        pass
    return None


def check_cron() -> bool:
    """
    Check cron status and print guidance to stderr.
    Returns True if execution should continue, False if it should stop.
    """
    state = read_state()

    if state.get("cron_disabled") is True:
        print("[toggle] cron_disabled=true in state.yaml — skipping cron check.", file=sys.stderr)
        return True

    job = find_toggle_cron()

    if job is None:
        print(
            "[toggle] NO_CRON: No cron job found for Toggle data sync. Halting.\n"
            "  Ask the user: \"How often do you want to refresh your Toggle data? (default: every hour)\"\n"
            "  Once the cron is created, re-run this skill.\n"
            "  If the user declines a cron, set cron_disabled: true in {skill_dir}/state.yaml and re-run.".format(skill_dir=SKILL_DIR),
            file=sys.stderr,
        )
        return False

    enabled = job.get("enabled", False)
    name = job.get("name", "")
    schedule = job.get("schedule", {}).get("expr", "?")
    last_status = job.get("state", {}).get("lastStatus", "unknown")
    last_error = job.get("state", {}).get("lastError")

    if not enabled:
        print(
            f"[toggle] CRON_DISABLED: Found cron \"{name}\" but it is disabled.\n"
            f"  Ask the user if they want to re-enable it.",
            file=sys.stderr,
        )
    elif last_status == "error":
        print(
            f"[toggle] CRON_ERROR: Cron \"{name}\" (schedule: {schedule}) last run failed.\n"
            f"  Error: {last_error}\n"
            f"  Inform the user and help troubleshoot.",
            file=sys.stderr,
        )
    else:
        print(
            f"[toggle] CRON_OK: \"{name}\" running on schedule {schedule}, last status: {last_status}.",
            file=sys.stderr,
        )
    return True


# ---------------------------------------------------------------------------
# Fetch + persist
# ---------------------------------------------------------------------------

def fetch(api_key: str, from_date: str, to_date: str) -> dict:
    url = f"{API_BASE}?fromDate={from_date}&toDate={to_date}"
    req = Request(url, headers={
        "accept": "application/json",
        "x-openclaw-api-key": api_key,
    })
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"HTTP error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Request failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


def build_toggle_section(day_data: list) -> str:
    return (
        f"{TOGGLE_START}\n"
        f"## Toggle Activity\n\n"
        f"```json\n{json.dumps(day_data, indent=2)}\n```\n"
        f"{TOGGLE_END}"
    )


def persist_day(memory_dir: str, day: str, workflows: list):
    path = os.path.join(memory_dir, f"{day}.md")
    section = build_toggle_section(workflows)

    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        pattern = re.compile(
            rf"{re.escape(TOGGLE_START)}.*?{re.escape(TOGGLE_END)}",
            re.DOTALL,
        )
        if pattern.search(content):
            content = pattern.sub(lambda _: section, content)
        else:
            content = content.rstrip() + "\n\n" + section + "\n"
    else:
        content = f"# {day}\n\n{section}\n"

    with open(path, "w") as f:
        f.write(content)
    print(f"  saved {len(workflows)} workflow(s) → {path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fetch Toggle workflow data")
    today = date.today().isoformat()
    parser.add_argument("--from-date", default=today, help="Start date (YYYY-MM-DD), default: today")
    parser.add_argument("--to-date", default=today, help="End date (YYYY-MM-DD), default: today")
    parser.add_argument(
        "--persist",
        metavar="MEMORY_DIR",
        help="Save data into <MEMORY_DIR>/<date>.md for each day in the response",
    )
    parser.add_argument(
        "--skip-cron-check",
        action="store_true",
        help="Skip the cron status check (useful when invoked by the cron itself)",
    )
    args = parser.parse_args()

    if not args.skip_cron_check:
        if not check_cron():
            sys.exit(1)

    api_key = os.environ.get("TOGGLE_API_KEY")
    if not api_key:
        print("Error: TOGGLE_API_KEY is not set.", file=sys.stderr)
        print("  export TOGGLE_API_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)

    data = fetch(api_key, args.from_date, args.to_date)

    print(json.dumps(data, indent=2))

    if args.persist:
        memory_dir = args.persist
        os.makedirs(memory_dir, exist_ok=True)
        workflows_by_date = data.get("workflowsByDate", {})
        if not workflows_by_date:
            print("No workflow data to persist.", file=sys.stderr)
            return
        for day, workflows in workflows_by_date.items():
            persist_day(memory_dir, day, workflows)


if __name__ == "__main__":
    main()
