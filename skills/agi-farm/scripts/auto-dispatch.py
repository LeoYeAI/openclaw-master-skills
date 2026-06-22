#!/usr/bin/env python3
"""
auto-dispatch.py — AGI-Farm Auto-Dispatcher
Part of the AGI-Farm skill (github.com/oabdelmaksoud/AGI-Farm).

Usage:
  python3 auto-dispatch.py [--workspace PATH] [--orchestrator ID] [--execute]

  --workspace PATH    Team workspace directory (default: ~/.openclaw/workspace)
  --orchestrator ID   Orchestrator agent id to skip (default: main)
  --execute           Actually trigger agents (default: dry-run preview only)

Cron (every 1 min, full-auto):
  * * * * * python3 ~/.openclaw/skills/agi-farm/auto-dispatch.py \\
              --workspace ~/.openclaw/workspace --execute \\
              >> ~/.openclaw/workspace/logs/auto-dispatch.log 2>&1

Two jobs per run:
  1. HITL notifications — detect needs_human_decision tasks, push alert to user
  2. Agent dispatch     — fire openclaw agent sessions for pending tasks

Safety rails:
  - Orchestrator never auto-triggered (needs human in loop)
  - 30-min cooldown per agent (no re-trigger spam)
  - All eligible agents run in parallel
  - Blocked agents skipped ([BLOCKED] in outbox)
  - Dependency checking: task only triggers when all depends_on are complete
  - Rate-limit detection + 10-min backoff
  - Stale in-progress auto-reset (>90 min, no outbox activity)
  - HITL re-notify cooldown: 2h per task
  - Full audit log → DISPATCHER_STATE.json
"""

import json
import os
import shutil
import subprocess
import sys
import time
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── openclaw binary resolution ────────────────────────────────────────────────
def _find_openclaw() -> str:
    """Locate the openclaw binary robustly for cron/LaunchAgent environments.

    Search order:
      1. $OPENCLAW_BIN env var (explicit override)
      2. shutil.which() — honours $PATH if available
      3. Common install locations on macOS/Linux
    """
    if os.environ.get("OPENCLAW_BIN"):
        return os.environ["OPENCLAW_BIN"]
    found = shutil.which("openclaw")
    if found:
        return found
    for candidate in (
        "/opt/homebrew/bin/openclaw",   # macOS Apple-silicon Homebrew
        "/usr/local/bin/openclaw",      # macOS Intel Homebrew / Linux
        "/usr/bin/openclaw",            # system-wide Linux installs
        str(Path.home() / ".local/bin/openclaw"),  # user-local pip installs
    ):
        if Path(candidate).is_file():
            return candidate
    return "openclaw"  # last resort — let subprocess raise a clear FileNotFoundError

OPENCLAW_BIN = _find_openclaw()

# ── Constants ─────────────────────────────────────────────────────────────────
COOLDOWN_MINUTES         = 30
HITL_NOTIFY_COOLDOWN_H   = 2
RATE_LIMIT_BACKOFF_MIN   = 10
STALE_INPROGRESS_MINUTES = 90

RATE_LIMIT_SIGNALS = [
    "rate limit", "rate_limit", "429", "too many requests",
    "⚠️ api rate limit", "please try again later",
]

# ── Args (resolved before anything else) ─────────────────────────────────────
def parse_args():
    args = sys.argv[1:]
    workspace    = Path.home() / ".openclaw" / "workspace"
    orchestrator = "main"
    execute      = False

    i = 0
    while i < len(args):
        if args[i] == "--workspace" and i + 1 < len(args):
            workspace = Path(args[i + 1]).expanduser(); i += 2
        elif args[i] == "--orchestrator" and i + 1 < len(args):
            orchestrator = args[i + 1]; i += 2
        elif args[i] == "--execute":
            execute = True; i += 1
        else:
            i += 1

    return workspace, orchestrator, execute

# ── Helpers ───────────────────────────────────────────────────────────────────
def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

def has_inbox_messages(inboxes_dir: Path, agent_id: str) -> bool:
    inbox = inboxes_dir / f"{agent_id}.md"
    if not inbox.exists():
        return False
    content = inbox.read_text(encoding="utf-8")
    return "TASK_ID:" in content or (
        any(l.startswith("## ") for l in content.splitlines())
        and "_No messages_" not in content
        and "No messages" not in content
    )

def is_blocked(outboxes_dir: Path, agent_id: str) -> bool:
    outbox = outboxes_dir / f"{agent_id}.md"
    if not outbox.exists():
        return False
    return "[BLOCKED]" in outbox.read_text(encoding="utf-8")

def is_rate_limited(agent_id: str, state: dict, now: datetime) -> bool:
    rl = state.get("rate_limited_until", {}).get(agent_id)
    if not rl:
        return False
    try:
        return now < datetime.fromisoformat(rl)
    except Exception:
        return False

def deps_satisfied(task: dict, task_index: dict) -> tuple[bool, list]:
    blocking = [
        dep for dep in task.get("depends_on", [])
        if task_index.get(dep, {}).get("status") != "complete"
    ]
    return len(blocking) == 0, blocking

def detect_rate_limit(text: str) -> bool:
    low = text.lower()
    return any(sig in low for sig in RATE_LIMIT_SIGNALS)

def trigger_agent(agent_id: str, task_title: str) -> tuple[bool, str, bool]:
    msg = (
        f"You have pending work in your inbox. "
        f"Please read comms/inboxes/{agent_id}.md and begin work on your "
        f"highest-priority pending task now. Task: {task_title}"
    )
    try:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", delete=False, prefix=f"dispatch_{agent_id}_"
        )
        tmp.close()
        tmp_path = Path(tmp.name)
        proc = subprocess.Popen(
            [OPENCLAW_BIN, "agent", "--agent", agent_id, "--message", msg],
            stdout=open(tmp_path, "w"), stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            early_exit = proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            early_exit = None
            
        try:
            output = tmp_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            output = ""
        try:
            tmp_path.unlink()
        except Exception:
            pass
        if detect_rate_limit(output):
            proc.terminate()
            return False, "rate_limit", True
        if early_exit is not None and early_exit != 0:
            return False, f"exited rc={early_exit}: {output.strip()[:200]}", False
        return True, f"pid={proc.pid}", False
    except Exception as e:
        return False, str(e), False

def send_hitl_notification(orchestrator: str, hitl_tasks: list) -> tuple[bool, str]:
    lines = [f"• {t['id']}: {t['title']}" for t in hitl_tasks]
    msg = (
        f"🚨 HITL Required — {len(hitl_tasks)} task(s) need your decision:\n\n"
        + "\n".join(lines)
        + "\n\nPlease reply so I can unblock the team. "
        "(Dashboard Tasks tab → 🚨 HITL filter for full context.)"
    )
    try:
        proc = subprocess.Popen(
            [OPENCLAW_BIN, "agent", "--agent", orchestrator, "--message", msg, "--deliver"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        time.sleep(1)
        return True, f"pid={proc.pid}"
    except Exception as e:
        return False, str(e)

# ── Job 0: Stale In-Progress Reset ───────────────────────────────────────────
def reset_stale_tasks(tasks: list, tasks_file: Path, outboxes_dir: Path, now: datetime):
    reset_ids = []
    for t in tasks:
        if t.get("status") != "in-progress":
            continue
        agent_id = t.get("assigned_to", "")
        started  = t.get("started_at") or t.get("decision_at")
        if not started:
            continue
        try:
            age_min = (now - datetime.fromisoformat(
                started.replace("Z", "+00:00"))).total_seconds() / 60
        except Exception:
            continue
        if age_min < STALE_INPROGRESS_MINUTES:
            continue
        outbox = outboxes_dir / f"{agent_id}.md"
        if outbox.exists():
            mtime = datetime.fromtimestamp(outbox.stat().st_mtime, tz=timezone.utc)
            if mtime > datetime.fromisoformat(started.replace("Z", "+00:00")):
                continue
        t["status"] = "pending"
        t["note"]   = f"Auto-reset: in-progress >{STALE_INPROGRESS_MINUTES}m with no outbox activity"
        t.pop("started_at", None)
        reset_ids.append(t["id"])
        print(f"[stale-reset] ⟳ {t['id']} ({agent_id}) — reset to pending")

    if reset_ids:
        try:
            raw = read_json(tasks_file)
            if isinstance(raw, dict):
                raw["tasks"] = tasks
                raw.setdefault("meta", {})["last_updated"] = now.isoformat()
                write_json(tasks_file, raw)
        except Exception as e:
            print(f"[stale-reset] ❌ persist failed: {e}")
    return tasks, reset_ids

# ── Job 1: HITL Notifications ─────────────────────────────────────────────────
def run_hitl_notifications(tasks: list, state: dict, now: datetime, orchestrator: str) -> dict:
    hitl_tasks  = [t for t in tasks if t.get("status") == "needs_human_decision"]
    notified_at = state.get("hitl_notified_at", {})
    to_notify   = []

    for t in hitl_tasks:
        tid  = t.get("id", "")
        last = notified_at.get(tid)
        if last:
            try:
                elapsed_h = (now - datetime.fromisoformat(last)).total_seconds() / 3600
                if elapsed_h < HITL_NOTIFY_COOLDOWN_H:
                    print(f"[hitl] ⏭  {tid} cooldown ({elapsed_h:.1f}h/{HITL_NOTIFY_COOLDOWN_H}h)")
                    continue
            except Exception:
                pass
        to_notify.append(t)

    if not to_notify:
        print(f"[hitl] ok ({len(hitl_tasks)} HITL tasks, all within cooldown)")
        return notified_at

    print(f"[hitl] 🚨 notifying for {[t['id'] for t in to_notify]}")
    ok, info = send_hitl_notification(orchestrator, to_notify)
    if ok:
        for t in to_notify:
            notified_at[t["id"]] = now.isoformat()
        print(f"[hitl] ✅ sent ({info})")
    else:
        print(f"[hitl] ❌ failed: {info}")
    return notified_at

# ── Job 2a: Dry-Run Preview ───────────────────────────────────────────────────
def dry_run_dispatch(tasks: list, state: dict, now: datetime,
                     skip_agents: set, inboxes_dir: Path, outboxes_dir: Path):
    pending    = [t for t in tasks if isinstance(t, dict) and t.get("status") == "pending"]
    last_trig  = state.get("last_triggered", {})
    task_index = {t["id"]: t for t in tasks if isinstance(t, dict)}
    would_trigger, would_skip = [], []

    seen: dict = {}
    for task in pending:
        aid = task.get("assigned_to")
        if aid and aid not in seen:
            seen[aid] = task

    for aid, task in seen.items():
        title = task.get("title", "")
        if aid in skip_agents:
            would_skip.append({"agent": aid, "reason": "orchestrator"})
        elif is_rate_limited(aid, state, now):
            would_skip.append({"agent": aid, "reason": "rate_limited"})
        elif (lt := last_trig.get(aid)) and \
             (now - datetime.fromisoformat(lt)).total_seconds() < COOLDOWN_MINUTES * 60:
            remaining = int((COOLDOWN_MINUTES * 60 - (now - datetime.fromisoformat(lt)).total_seconds()) / 60)
            would_skip.append({"agent": aid, "reason": f"cooldown ({remaining}m)"})
        elif not (sat := deps_satisfied(task, task_index))[0]:
            would_skip.append({"agent": aid, "reason": f"waiting for {sat[1]}"})
        elif is_blocked(outboxes_dir, aid):
            would_skip.append({"agent": aid, "reason": "BLOCKED"})
        elif not has_inbox_messages(inboxes_dir, aid):
            would_skip.append({"agent": aid, "reason": "empty inbox"})
        else:
            would_trigger.append({"agent": aid, "task_id": task.get("id"), "title": title})
            print(f"[dry-run] → would trigger {aid}: {task.get('id')} — {title[:55]}")

    for s in would_skip:
        print(f"[dry-run] → would skip   {s['agent']}: {s['reason']}")

    return would_trigger, would_skip

# ── Job 2b: Live Dispatch ─────────────────────────────────────────────────────
def run_dispatch(tasks: list, state: dict, now: datetime,
                 skip_agents: set, inboxes_dir: Path, outboxes_dir: Path):
    pending    = [t for t in tasks if isinstance(t, dict) and t.get("status") == "pending"]
    last_trig  = state.get("last_triggered", {})
    rate_lim   = state.get("rate_limited_until", {})
    task_index = {t["id"]: t for t in tasks if isinstance(t, dict)}
    triggered, skipped = [], []

    seen: dict = {}
    for task in pending:
        aid = task.get("assigned_to")
        if aid and aid not in seen:
            seen[aid] = task

    for aid, task in seen.items():
        if aid in skip_agents:
            skipped.append({"agent": aid, "reason": "orchestrator"})
            continue
        if is_rate_limited(aid, state, now):
            skipped.append({"agent": aid, "reason": f"rate_limited until {rate_lim.get(aid)}"})
            print(f"[dispatch] ⏸  {aid} rate-limited")
            continue
        if (lt := last_trig.get(aid)):
            elapsed = (now - datetime.fromisoformat(lt)).total_seconds()
            if elapsed < COOLDOWN_MINUTES * 60:
                remaining = int((COOLDOWN_MINUTES * 60 - elapsed) / 60)
                skipped.append({"agent": aid, "reason": f"cooldown ({remaining}m)"})
                continue
        satisfied, blocking = deps_satisfied(task, task_index)
        if not satisfied:
            skipped.append({"agent": aid, "reason": f"waiting for {blocking}"})
            print(f"[dispatch] ⏳ {aid}/{task['id']} blocked by {blocking}")
            continue
        if is_blocked(outboxes_dir, aid):
            skipped.append({"agent": aid, "reason": "BLOCKED"})
            continue
        if not has_inbox_messages(inboxes_dir, aid):
            skipped.append({"agent": aid, "reason": "empty inbox"})
            continue

        title = task.get("title", task.get("id", "pending task"))
        ok, info, rl_hit = trigger_agent(aid, title)

        if rl_hit:
            until = (now + timedelta(minutes=RATE_LIMIT_BACKOFF_MIN)).isoformat()
            rate_lim[aid] = until
            skipped.append({"agent": aid, "reason": f"rate_limit → backoff until {until}"})
            print(f"[dispatch] ⚠️  {aid} hit rate limit — backing off {RATE_LIMIT_BACKOFF_MIN}m")
        elif ok:
            last_trig[aid] = now.isoformat()
            triggered.append({"agent": aid, "task_id": task.get("id"), "title": title, "at": now.isoformat()})
            print(f"[dispatch] ✅ triggered {aid} → {title[:60]}")
        else:
            skipped.append({"agent": aid, "reason": f"failed: {info}"})
            print(f"[dispatch] ❌ failed   {aid} → {info[:80]}")

    return triggered, skipped, last_trig, rate_lim

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    workspace, orchestrator, execute = parse_args()

    tasks_file   = workspace / "TASKS.json"
    state_file   = workspace / "DISPATCHER_STATE.json"
    inboxes_dir  = workspace / "comms" / "inboxes"
    outboxes_dir = workspace / "comms" / "outboxes"
    skip_agents  = {orchestrator}

    if not execute:
        print(f"[auto-dispatch] DRY-RUN — workspace={workspace} orchestrator={orchestrator}")
        print("[auto-dispatch] Pass --execute to trigger agents\n")

    now   = datetime.now(timezone.utc)
    state = read_json(state_file) or {}

    tasks_data = read_json(tasks_file)
    tasks = tasks_data.get("tasks", []) if isinstance(tasks_data, dict) else (tasks_data or [])

    # ── Job 0: Stale reset ────────────────────────────────────────────────────
    tasks, reset_ids = reset_stale_tasks(tasks, tasks_file, outboxes_dir, now)
    if reset_ids:
        print(f"[stale-reset] reset: {reset_ids}")

    # ── Job 1: HITL notifications ─────────────────────────────────────────────
    if execute:
        notified_at = run_hitl_notifications(tasks, state, now, orchestrator)
    else:
        notified_at = state.get("hitl_notified_at", {})

    # ── Job 2: Dispatch ───────────────────────────────────────────────────────
    if not execute:
        would_trigger, would_skip = dry_run_dispatch(
            tasks, state, now, skip_agents, inboxes_dir, outboxes_dir)
        print(f"\n[dry-run] Would trigger: {[t['agent'] for t in would_trigger]}")
        print(f"[dry-run] Would skip:    {[s['agent']+' ('+s['reason']+')' for s in would_skip]}")
        print(f"\nRun with --execute to apply.")
        return

    triggered, skipped, last_trig, rate_lim = run_dispatch(
        tasks, state, now, skip_agents, inboxes_dir, outboxes_dir)

    # ── Persist state ─────────────────────────────────────────────────────────
    history = state.get("history", [])
    run_summary = {
        "run_at":        now.isoformat(),
        "workspace":     str(workspace),
        "pending_count": sum(1 for t in tasks if t.get("status") == "pending"),
        "hitl_count":    sum(1 for t in tasks if t.get("status") == "needs_human_decision"),
        "triggered":     triggered,
        "skipped":       skipped,
    }
    history.append(run_summary)
    if len(history) > 200:
        history = history[-200:]

    write_json(state_file, {
        "last_run":           now.isoformat(),
        "last_triggered":     last_trig,
        "rate_limited_until": rate_lim,
        "hitl_notified_at":   notified_at,
        "last_summary":       run_summary,
        "history":            history,
    })

    print(
        f"[auto-dispatch] {now.strftime('%H:%M UTC')} workspace={workspace.name} — "
        f"{run_summary['pending_count']} pending · {run_summary['hitl_count']} HITL · "
        f"triggered {len(triggered)} · skipped {len(skipped)}"
    )
    for s in skipped:
        print(f"  ↳ skip {s['agent']}: {s['reason']}")

if __name__ == "__main__":
    main()
