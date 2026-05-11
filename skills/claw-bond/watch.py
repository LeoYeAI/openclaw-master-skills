#!/usr/bin/env python3
"""
claw-bond — Live Monitor  (watch.py)
======================================
Real-time dashboard showing connected peers, active commitments,
pending proposals, overdue alerts, and the last 10 ledger events
across all sessions.

Usage:
  python3 ~/.openclaw/workspace/skills/claw-bond/watch.py
  python3 watch.py --workspace /path/to/workspace   # custom workspace root
  python3 watch.py --interval 5                      # refresh every 5 seconds (default: 3)
  python3 watch.py --once                            # print once and exit (no loop)
"""

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path

# ── ANSI ───────────────────────────────────────────────────────────────────
G  = "\033[92m"; R  = "\033[91m"; Y  = "\033[93m"
B  = "\033[94m"; C  = "\033[96m"; DIM = "\033[2m"
W  = "\033[0m";  BD = "\033[1m"

CLEAR = "\033[2J\033[H"

# ── Paths ──────────────────────────────────────────────────────────────────

def skill_dir(ws: str) -> Path:
    return Path(ws) / "skills" / "claw-bond"

def peers_path(ws: str) -> Path:
    return skill_dir(ws) / "peers.json"

def ledger_path(ws: str) -> Path:
    return skill_dir(ws) / "ledger.json"


# ── Data Loaders ──────────────────────────────────────────────────────────

def load_peers(ws: str) -> list[dict]:
    p = peers_path(ws)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text()).get("peers", [])
    except Exception:
        return []


def load_sessions(ws: str) -> list[dict]:
    p = ledger_path(ws)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text()).get("sessions", [])
    except Exception:
        return []


# ── Formatters ─────────────────────────────────────────────────────────────

def fmt_time(iso: str) -> str:
    """Format ISO8601 → human-readable local time."""
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        local = dt.astimezone()
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - dt.replace(tzinfo=datetime.timezone.utc) if dt.tzinfo else now - dt
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s ago"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds()//60)}m ago"
        elif delta.days == 0:
            return f"{int(delta.total_seconds()//3600)}h ago"
        else:
            return local.strftime("%b %d %H:%M")
    except Exception:
        return iso[:16] if iso else "?"


def fmt_deadline(iso: str) -> str:
    """Format deadline with colour — red if past, yellow if <24h, green otherwise."""
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = dt.replace(tzinfo=datetime.timezone.utc) - now
        local = dt.astimezone()
        formatted = local.strftime("%b %d %H:%M")
        if delta.total_seconds() < 0:
            return f"{R}OVERDUE{W} (was {formatted})"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() // 3600)
            return f"{Y}{formatted} ({hours}h left){W}"
        else:
            days = delta.days
            return f"{G}{formatted} ({days}d left){W}"
    except Exception:
        return iso[:16] if iso else "?"


EVENT_ICONS = {
    "PROPOSED":  "📤",
    "COUNTERED": "↩️ ",
    "ACCEPTED":  "✅",
    "COMMITTED": "🔒",
    "REJECTED":  "❌",
    "CANCELLED": "🚫",
}


# ── Dashboard Renderer ────────────────────────────────────────────────────

def render(ws: str) -> str:
    lines = []
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    peers   = load_peers(ws)
    sessions = load_sessions(ws)

    # ── Header ──────────────────────────────────────────────────────────
    lines.append(f"{BD}{C}╔══════════════════════════════════════════════════╗{W}")
    lines.append(f"{BD}{C}║          claw-bond  Live Monitor  {DIM}{now_str}{W}{BD}{C}       ║{W}")
    lines.append(f"{BD}{C}╚══════════════════════════════════════════════════╝{W}")
    lines.append("")

    # ── Connected Peers ──────────────────────────────────────────────────
    lines.append(f"{BD}🔗 Connected Peers ({len(peers)}){W}")
    if not peers:
        lines.append(f"  {DIM}No peers connected — run: generate-address and share your token{W}")
    else:
        for p in peers:
            alias     = p.get("alias", "?")
            last_seen = fmt_time(p.get("last_seen", ""))
            pubkey    = p.get("pubkey", "")[:12] + "…"
            stale     = f"  {Y}⚠ stale{W}" if p.get("relay_token_stale") else ""
            relay     = p.get("relay", "").replace("wss://", "").split(".")[0]
            lines.append(f"  {G}●{W} {BD}{alias:<20}{W}  {DIM}key:{pubkey}  via:{relay}  seen:{last_seen}{W}{stale}")
    lines.append("")

    # ── Active Commitments ───────────────────────────────────────────────
    active = [s for s in sessions if s.get("state") == "COMMITTED" and s.get("final_terms")]
    lines.append(f"{BD}📋 Active Commitments ({len(active)}){W}")
    if not active:
        lines.append(f"  {DIM}None{W}")
    else:
        for s in active:
            t       = s.get("final_terms", {})
            sid     = s.get("session_id", "")[:4]
            peer    = s.get("peer_alias", "?")
            my_task = (t.get("my_tasks") or ["?"])[0][:45]
            dl      = fmt_deadline(t.get("deadline", ""))
            lines.append(f"  {BD}[{sid}]{W} with {C}{peer}{W}")
            lines.append(f"        My task : {my_task}")
            lines.append(f"        Deadline: {dl}")
    lines.append("")

    # ── Pending Proposals ────────────────────────────────────────────────
    pending_states = {"PROPOSED", "COUNTERED", "INBOUND_PENDING", "PENDING_SEND"}
    pending = [s for s in sessions if s.get("state") in pending_states]
    lines.append(f"{BD}📨 Pending Proposals ({len(pending)}){W}")
    if not pending:
        lines.append(f"  {DIM}None{W}")
    else:
        for s in pending:
            sid   = s.get("session_id", "")[:4]
            peer  = s.get("peer_alias", "?")
            state = s.get("state", "?")
            by    = s.get("initiated_by", "?")
            icon  = "→" if by == "self" else "←"
            lines.append(f"  {Y}[{sid}]{W} {icon} {peer}  [{state}]")
    lines.append("")

    # ── Overdue ──────────────────────────────────────────────────────────
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    overdue = []
    for s in active:
        try:
            dl_str = s.get("final_terms", {}).get("deadline", "")
            dt = datetime.datetime.fromisoformat(dl_str.replace("Z", "+00:00"))
            if dt.replace(tzinfo=datetime.timezone.utc) < now_utc:
                overdue.append(s)
        except Exception:
            pass
    if overdue:
        lines.append(f"{BD}{R}🚨 Overdue ({len(overdue)}){W}")
        for s in overdue:
            sid  = s.get("session_id", "")[:4]
            peer = s.get("peer_alias", "?")
            t    = s.get("final_terms", {})
            my_task = (t.get("my_tasks") or ["?"])[0][:40]
            lines.append(f"  {R}[{sid}]{W} with {peer} — {my_task}")
            lines.append(f"          → run: checkin {sid} done|partial|overdue")
        lines.append("")

    # ── Recent Events ────────────────────────────────────────────────────
    all_events: list[tuple[str, str, str, str]] = []  # (at, type, by, session_id)
    for s in sessions:
        sid = s.get("session_id", "")[:4]
        peer = s.get("peer_alias", "?")
        for ev in s.get("events", []):
            all_events.append((
                ev.get("at", ""),
                ev.get("type", "?"),
                ev.get("by", "?"),
                sid,
                peer,
            ))
    all_events.sort(key=lambda x: x[0], reverse=True)
    recent = all_events[:10]

    lines.append(f"{BD}📜 Recent Events{W}")
    if not recent:
        lines.append(f"  {DIM}No events yet{W}")
    else:
        for at, etype, by, sid, peer in recent:
            icon  = EVENT_ICONS.get(etype, "•")
            ts    = fmt_time(at)
            actor = "you" if by == "self" else by
            lines.append(f"  {DIM}{ts:>8}{W}  {icon} {BD}{etype:<12}{W}  [{sid}] with {C}{peer}{W}  by {actor}")

    lines.append("")
    lines.append(f"{DIM}Refreshing every few seconds — Ctrl+C to exit   workspace: {ws}{W}")
    return "\n".join(lines)


# ── Entry Point ────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="claw-bond live monitor")
    p.add_argument("--workspace", "-w", default=None,
                   help="Workspace root (default: DIPLOMAT_WORKSPACE env or cwd)")
    p.add_argument("--interval", "-i", type=float, default=3.0,
                   help="Refresh interval in seconds (default: 3)")
    p.add_argument("--once", action="store_true",
                   help="Print once and exit")
    args = p.parse_args()

    ws = args.workspace or os.environ.get("DIPLOMAT_WORKSPACE", os.getcwd())

    if not (Path(ws) / "skills" / "claw-bond").exists():
        print(f"⚠️  claw-bond not set up in: {ws}")
        print("Run: python3 negotiate.py install")
        sys.exit(1)

    if args.once:
        print(render(ws))
        return

    try:
        while True:
            output = render(ws)
            sys.stdout.write(CLEAR)
            sys.stdout.write(output + "\n")
            sys.stdout.flush()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\n{DIM}Monitor stopped.{W}")


if __name__ == "__main__":
    main()
