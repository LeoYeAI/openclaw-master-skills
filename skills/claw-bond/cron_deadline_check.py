#!/usr/bin/env python3
"""
cron_deadline_check.py — Claw Connector proactive deadline alerts (Path A)

Registered by `negotiate.py install` to run every 15 minutes via crontab:
  */15 * * * * python3 {skill_dir}/cron_deadline_check.py >> {skill_dir}/cron.log 2>&1

What it does:
  1. Reads MEMORY.md for all [ACTIVE] commitments
  2. For any commitment whose deadline is within 2 hours: writes a plain-language
     alert to skills/claw-bond/cron_alerts.json
  3. Attempts `openclaw notify "<message>"` — if OpenClaw CLI is in PATH, this
     delivers a real message through the human's active channel (WhatsApp, Telegram,
     etc.) without them needing to open their agent
  4. Falls back gracefully if the CLI is unavailable

Path B fallback: diplomat-heartbeat hook reads cron_alerts.json on every human
message and surfaces any unshown alerts, even without cron.

Security: reads workspace files only, no network calls, no subprocess execution
except `openclaw notify` (which is the declared delivery channel).
"""

from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid

# ─── Workspace detection ──────────────────────────────────────────────────────
def get_workspace_root() -> str:
    root = os.environ.get("DIPLOMAT_WORKSPACE", "")
    if not root:
        # Default OpenClaw workspace path
        root = os.path.expanduser("~/.openclaw/workspace")
    if not os.path.isdir(root):
        # Try cwd as fallback
        root = os.getcwd()
    return root


def get_skill_dir(workspace_root: str) -> str:
    return os.path.join(workspace_root, "skills", "claw-bond")


# ─── MEMORY.md parser ─────────────────────────────────────────────────────────
_ACTIVE_ENTRY_RE = re.compile(
    r"\[ACTIVE\].*?Peer:\s*(?P<peer>[^|]+)\|.*?My:\s*(?P<my>[^|]+)\|.*?"
    r"Due:\s*(?P<due>[^|]+)\|.*?ID:\s*`?(?P<id>[^`\s]+)`?",
    re.IGNORECASE,
)

def parse_active_entries(memory_md: str) -> list[dict]:
    """Extract [ACTIVE] commitment entries from MEMORY.md."""
    entries = []
    in_section = False
    for line in memory_md.splitlines():
        if "## Diplomat Commitments" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and "[ACTIVE]" in line.upper():
            m = _ACTIVE_ENTRY_RE.search(line)
            if m:
                entries.append({
                    "peer":  m.group("peer").strip(),
                    "my":    m.group("my").strip(),
                    "due":   m.group("due").strip(),
                    "id":    m.group("id").strip(),
                })
    return entries


def parse_due(raw: str) -> datetime.datetime | None:
    """Parse 'YYYY-MM-DD HH:MM UTC' or ISO8601 into a UTC datetime."""
    raw = raw.strip()
    for fmt in ("%Y-%m-%d %H:%M UTC", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            continue
    # Try normalising space→T and stripping UTC
    try:
        normalised = raw.replace(" UTC", "Z").replace(" ", "T")
        return datetime.datetime.fromisoformat(normalised.replace("Z", "+00:00"))
    except ValueError:
        return None


# ─── cron_alerts.json writer ──────────────────────────────────────────────────
def load_alerts(alerts_path: str) -> dict:
    try:
        with open(alerts_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"alerts": []}


def save_alerts(alerts_path: str, data: dict) -> None:
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(alerts_path), suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, alerts_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def alert_already_written(existing_alerts: list, commitment_id: str) -> bool:
    """Avoid writing duplicate alerts for the same commitment in the same window."""
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)
    for a in existing_alerts:
        if a.get("commitment_id") == commitment_id:
            try:
                written_at = datetime.datetime.fromisoformat(a["created_at"])
                if written_at > cutoff:
                    return True
            except (KeyError, ValueError):
                continue
    return False


# ─── OpenClaw notify attempt ─────────────────────────────────────────────────
def try_openclaw_notify(message: str) -> bool:
    """
    Attempt to deliver a proactive message through OpenClaw's active messaging
    channel (WhatsApp, Telegram, etc.) via the `openclaw notify` CLI.
    Returns True if the notification was delivered, False if unavailable.
    This is a best-effort call — failure is non-fatal.
    """
    try:
        result = subprocess.run(
            ["openclaw", "notify", message],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


# ─── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    workspace_root = get_workspace_root()
    skill_dir      = get_skill_dir(workspace_root)
    memory_path    = os.path.join(workspace_root, "MEMORY.md")
    alerts_path    = os.path.join(skill_dir, "cron_alerts.json")

    # Read MEMORY.md
    try:
        with open(memory_path) as f:
            memory_md = f.read()
    except FileNotFoundError:
        # No commitments yet — nothing to check
        print("[cron_deadline_check] MEMORY.md not found — nothing to check.")
        return

    entries = parse_active_entries(memory_md)
    if not entries:
        print("[cron_deadline_check] No active commitments found.")
        return

    now        = datetime.datetime.now(datetime.timezone.utc)
    alert_data = load_alerts(alerts_path)
    new_alerts = 0

    for entry in entries:
        deadline = parse_due(entry["due"])
        if deadline is None:
            print(f"[cron_deadline_check] Could not parse deadline for {entry['id']}: {entry['due']}")
            continue

        time_left = deadline - now
        hours_left = time_left.total_seconds() / 3600

        # Alert window: deadline is within 2 hours and hasn't passed yet
        if 0 < hours_left <= 2:
            commitment_id = entry["id"]

            if alert_already_written(alert_data["alerts"], commitment_id):
                print(f"[cron_deadline_check] Alert already written for {commitment_id}, skipping.")
                continue

            h = max(1, round(hours_left))
            message = (
                f"⏰ Heads up — {entry['my']} is due in about {h} hour{'s' if h != 1 else ''}. "
                f"Peer: {entry['peer']}. "
                f"Want me to check in with their agent? "
                f"(/claw-diplomat checkin {commitment_id} done|partial|overdue)"
            )

            # Path A primary: attempt to push through OpenClaw's active channel
            delivered = try_openclaw_notify(message)

            # Always write to cron_alerts.json as well — heartbeat hook picks this up
            alert_data["alerts"].append({
                "id":            str(uuid.uuid4())[:8],
                "commitment_id": commitment_id,
                "message":       message,
                "created_at":    now.isoformat(),
                "shown":         False,  # heartbeat hook marks True after surfacing
                "delivered_via_cli": delivered,
            })
            new_alerts += 1

            status = "delivered via openclaw notify ✓" if delivered else "queued for heartbeat"
            print(f"[cron_deadline_check] Alert for {commitment_id} — {status}")

        elif hours_left <= 0:
            print(f"[cron_deadline_check] {entry['id']} is overdue — heartbeat hook will surface.")

    if new_alerts > 0:
        save_alerts(alerts_path, alert_data)

    print(f"[cron_deadline_check] Done. {new_alerts} new alert(s) written.")


if __name__ == "__main__":
    main()
