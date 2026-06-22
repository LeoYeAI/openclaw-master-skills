#!/usr/bin/env python3
"""
register-crons.py — Register cron jobs for an agi-farm team.

Reads team.json, detects timezone from OpenClaw config, registers the
orchestrator heartbeat + standup + specialist crons for every agent in
the roster. Skips any cron that already exists by name.

Usage:
    python3 register-crons.py [--team-json PATH] [--dry-run]
"""

import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_timezone() -> str:
    """Read timezone from openclaw.json, fall back to UTC."""
    cfg_path = Path.home() / ".openclaw/openclaw.json"
    try:
        cfg = json.loads(cfg_path.read_text())
        tz = cfg.get("session", {}).get("timezone") or \
             cfg.get("timezone") or \
             cfg.get("settings", {}).get("timezone")
        if tz:
            return tz
    except Exception:
        pass
    # Try system timezone
    try:
        tz = subprocess.run(
            ["openssl", "rand", "-hex", "1"],  # dummy
            capture_output=True
        )
        import time
        return datetime.now(timezone.utc).astimezone().tzname() or "UTC"
    except Exception:
        pass
    return "UTC"


def existing_cron_names() -> set:
    try:
        r = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=8
        )
        names = set()
        for line in r.stdout.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 2:
                names.add(parts[1])
        return names
    except Exception:
        return set()


def cron_add(args: list, dry_run: bool) -> bool:
    cmd = ["openclaw", "cron", "add"] + args
    if dry_run:
        print(f"  [dry-run] {' '.join(cmd)}")
        return True
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return r.returncode == 0
    except Exception:
        return False


def register_all(team: dict, tz: str, dry_run: bool):
    agent_ids  = {a["id"] for a in team["agents"]}
    team_lower = team["team_name"].lower().replace(" ", "-")
    existing   = existing_cron_names()

    # ── Core orchestrator jobs ──────────────────────────────────────────────
    CORE_JOBS = [
        {
            "name":    f"{team_lower}-heartbeat",
            "agent":   "main",
            "cron":    "*/30 * * * *",
            "message": "Heartbeat: verify all agents available, flag stuck tasks, update HEARTBEAT.md.",
            "timeout": "60",
            "flags":   ["--no-deliver"],
        },
        {
            "name":    f"{team_lower}-morning-standup",
            "agent":   "main",
            "cron":    "0 8 * * *",
            "message": "Morning standup: read TASKS.json, check agent status, plan the day. Report key items.",
            "timeout": "120",
            "flags":   [],
        },
    ]

    # ── Specialist jobs — only if agent in roster ───────────────────────────
    SPECIALIST_JOBS = {
        "vigil": {
            "name":    f"{team_lower}-vigil-heartbeat",
            "cron":    "*/30 * * * *",
            "message": "Heartbeat: check AGENT_STATUS.json for stuck agents, TASKS.json for overdue tasks, broadcast.md for alerts. Update DASHBOARD.md. Pull next IMPROVEMENT_BACKLOG item if queue empty.",
            "timeout": "90",
            "flags":   ["--no-deliver"],
        },
        "cipher": {
            "name":    f"{team_lower}-cipher-synthesis",
            "cron":    "0 */6 * * *",
            "message": "Knowledge synthesis: read agent outboxes, extract learnings, update MEMORY.md (≤200 lines), update SHARED_KNOWLEDGE.json, update FAILURES.md if needed.",
            "timeout": "120",
            "flags":   [],
        },
        "nova": {
            "name":    f"{team_lower}-nova-digest",
            "cron":    "0 9 * * 1",
            "message": "Weekly R&D digest: summarize active experiments, publish findings to broadcast.md, update EXPERIMENTS.json.",
            "timeout": "120",
            "flags":   [],
        },
        "evolve": {
            "name":    f"{team_lower}-evolve-scan",
            "cron":    "0 2 * * *",
            "message": "Daily process scan: review TASKS.json failure patterns, update IMPROVEMENT_BACKLOG.json, propose process improvements if same failure occurred 3+ times.",
            "timeout": "120",
            "flags":   ["--no-deliver"],
        },
    }

    results = {"registered": [], "skipped": [], "failed": []}

    for job in CORE_JOBS:
        if job["name"] in existing:
            print(f"  ⏭  skip (exists): {job['name']}")
            results["skipped"].append(job["name"])
            continue
        args = [
            "--name",            job["name"],
            "--agent",           job["agent"],
            "--cron",            job["cron"],
            "--tz",              tz,
            "--session",         "isolated",
            "--message",         job["message"],
            "--timeout-seconds", job["timeout"],
        ] + job.get("flags", [])
        ok = cron_add(args, dry_run)
        if ok:
            print(f"  ✅ registered: {job['name']}")
            results["registered"].append(job["name"])
        else:
            print(f"  ❌ failed:     {job['name']}")
            results["failed"].append(job["name"])

    for aid, job in SPECIALIST_JOBS.items():
        if aid not in agent_ids:
            continue
        if job["name"] in existing:
            print(f"  ⏭  skip (exists): {job['name']}")
            results["skipped"].append(job["name"])
            continue
        args = [
            "--name",            job["name"],
            "--agent",           aid,
            "--cron",            job["cron"],
            "--tz",              tz,
            "--session",         "isolated",
            "--message",         job["message"],
            "--timeout-seconds", job["timeout"],
        ] + job.get("flags", [])
        ok = cron_add(args, dry_run)
        if ok:
            print(f"  ✅ registered: {job['name']} ({aid})")
            results["registered"].append(job["name"])
        else:
            print(f"  ❌ failed:     {job['name']} ({aid})")
            results["failed"].append(job["name"])

    print(f"\n  Summary: {len(results['registered'])} registered, "
          f"{len(results['skipped'])} skipped, {len(results['failed'])} failed")
    return results


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--team-json", default=str(
        Path.home() / ".openclaw/workspace/agi-farm-bundle/team.json"))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    team = read_json(args.team_json)
    if not team:
        print(f"❌ team.json not found: {args.team_json}")
        return

    tz = get_timezone()
    print(f"🕐 Timezone: {tz}")
    print(f"👥 Team: {team['team_name']} ({len(team['agents'])} agents)")
    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Registering crons...\n")

    register_all(team, tz, args.dry_run)


if __name__ == "__main__":
    main()
