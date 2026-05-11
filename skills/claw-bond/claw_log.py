#!/usr/bin/env python3
"""
claw-bond — Session Log Viewer  (claw_log.py)
===============================================
Shows the full negotiation transcript for a session:
every offer, counter, acceptance, and the final committed terms —
so humans can see exactly what was agreed to and how the deal evolved.

Usage:
  python3 claw_log.py                          # list all sessions
  python3 claw_log.py <session-id-prefix>      # show full transcript
  python3 claw_log.py --workspace /path        # custom workspace root
  python3 claw_log.py --json <session-prefix>  # machine-readable output
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

# ── ANSI ───────────────────────────────────────────────────────────────────
G  = "\033[92m"; R  = "\033[91m"; Y  = "\033[93m"
B  = "\033[94m"; C  = "\033[96m"; DIM = "\033[2m"
W  = "\033[0m";  BD = "\033[1m"

# ── Path helpers ──────────────────────────────────────────────────────────

def ledger_path(ws: str) -> Path:
    return Path(ws) / "skills" / "claw-bond" / "ledger.json"


def load_sessions(ws: str) -> list[dict]:
    p = ledger_path(ws)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text()).get("sessions", [])
    except Exception as e:
        print(f"{R}Error reading ledger.json: {e}{W}", file=sys.stderr)
        return []


def fmt_dt(iso: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return iso or "?"


def fmt_deadline(iso: str) -> str:
    try:
        dt   = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        now  = datetime.datetime.now(datetime.timezone.utc)
        delta = dt.replace(tzinfo=datetime.timezone.utc) - now
        local = dt.astimezone().strftime("%Y-%m-%d %H:%M %Z")
        if delta.total_seconds() < 0:
            return f"{R}{local}  ← OVERDUE{W}"
        elif delta.total_seconds() < 86400:
            return f"{Y}{local}  ({int(delta.total_seconds()//3600)}h left){W}"
        else:
            return f"{G}{local}  ({delta.days}d left){W}"
    except Exception:
        return iso or "?"


EVENT_ICONS = {
    "PROPOSED":  (B,  "📤", "Proposal sent"),
    "COUNTERED": (Y,  "↩️ ", "Counter-offer"),
    "ACCEPTED":  (G,  "✅", "Terms accepted"),
    "COMMITTED": (G,  "🔒", "Commitment locked"),
    "REJECTED":  (R,  "❌", "Rejected"),
    "CANCELLED": (DIM,"🚫", "Cancelled"),
}

STATE_COLOURS = {
    "COMMITTED":       G,
    "DONE":            G,
    "PROPOSED":        B,
    "COUNTERED":       Y,
    "INBOUND_PENDING": Y,
    "OVERDUE":         R,
    "PARTIAL":         Y,
    "REJECTED":        R,
    "CANCELLED":       DIM,
    "HANDOFF_RECEIVED": C,
}


# ── Listing ────────────────────────────────────────────────────────────────

def list_sessions(ws: str):
    sessions = load_sessions(ws)
    if not sessions:
        print(f"{DIM}No sessions in ledger.{W}")
        return

    print(f"\n{BD}All Sessions  ({len(sessions)} total){W}\n")
    print(f"  {'ID':>4}  {'Peer':<20}  {'State':<18}  {'Created':<24}  Events")
    print(f"  {'─'*4}  {'─'*20}  {'─'*18}  {'─'*24}  {'─'*6}")

    for s in sorted(sessions, key=lambda x: x.get("created_at", ""), reverse=True):
        sid    = s.get("session_id", "")[:4]
        peer   = s.get("peer_alias", "?")[:20]
        state  = s.get("state", "?")
        col    = STATE_COLOURS.get(state, W)
        created = fmt_dt(s.get("created_at", ""))[:19]
        n_ev   = len(s.get("events", []))
        print(f"  {DIM}[{sid}]{W}  {peer:<20}  {col}{state:<18}{W}  {DIM}{created}{W}  {n_ev}")

    print(f"\n{DIM}Run: claw_log.py <session-id-prefix> to see full transcript{W}\n")


# ── Transcript ────────────────────────────────────────────────────────────

def show_transcript(ws: str, prefix: str, as_json: bool = False):
    sessions = load_sessions(ws)
    matches  = [s for s in sessions if s.get("session_id", "").startswith(prefix)]

    if not matches:
        print(f"{R}No session found with prefix: {prefix!r}{W}")
        print("Run without arguments to list all sessions.")
        sys.exit(1)
    if len(matches) > 1:
        print(f"{Y}Multiple sessions match {prefix!r}. Be more specific:{W}")
        for s in matches:
            print(f"  {s['session_id'][:8]}  {s.get('peer_alias','?')}  {s.get('state','?')}")
        sys.exit(1)

    s = matches[0]

    if as_json:
        print(json.dumps(s, indent=2))
        return

    sid      = s.get("session_id", "?")
    peer     = s.get("peer_alias", "?")
    state    = s.get("state", "?")
    col      = STATE_COLOURS.get(state, W)
    by_me    = s.get("initiated_by", "?") == "self"
    terms    = s.get("final_terms") or {}
    events   = s.get("events", [])
    pending  = s.get("pending_terms")

    print()
    print(f"{BD}{C}╔══════════════════════════════════════════════════╗{W}")
    print(f"{BD}{C}║  Session Transcript                              ║{W}")
    print(f"{BD}{C}╚══════════════════════════════════════════════════╝{W}")
    print()
    print(f"  {BD}Session ID :{W}  {sid}")
    print(f"  {BD}Peer       :{W}  {C}{peer}{W}  {DIM}(pubkey: {s.get('peer_pubkey','?')[:16]}…){W}")
    print(f"  {BD}Direction  :{W}  {'You started this' if by_me else peer + ' started this'}")
    print(f"  {BD}State      :{W}  {col}{BD}{state}{W}")
    print(f"  {BD}Created    :{W}  {fmt_dt(s.get('created_at',''))}")
    if s.get("committed_at"):
        print(f"  {BD}Committed  :{W}  {fmt_dt(s['committed_at'])}")

    # ── Timeline ──────────────────────────────────────────────────────
    print()
    print(f"{BD}── Negotiation Timeline ──────────────────────────────{W}")
    if not events:
        print(f"  {DIM}No events recorded yet.{W}")
    else:
        for i, ev in enumerate(sorted(events, key=lambda e: e.get("at", ""))):
            etype  = ev.get("type", "?")
            at     = fmt_dt(ev.get("at", ""))
            by     = ev.get("by", "?")
            actor  = f"{Y}you{W}" if by == "self" else f"{C}{by}{W}"
            ev_col, icon, label = EVENT_ICONS.get(etype, (W, "•", etype))
            ver    = f"  {DIM}v{ev['terms_version']}{W}" if ev.get("terms_version") else ""
            print(f"  {DIM}{i+1:>2}.{W}  {icon}  {ev_col}{BD}{label:<20}{W}  by {actor}  {DIM}{at}{W}{ver}")

    # ── Final Committed Terms ──────────────────────────────────────────
    if terms:
        print()
        print(f"{BD}── Committed Terms ───────────────────────────────────{W}")
        my_tasks   = terms.get("my_tasks", [])
        peer_tasks = terms.get("your_tasks", []) or terms.get("peer_tasks", [])
        deadline   = terms.get("deadline", "")
        checkin    = terms.get("checkin_at", "")
        version    = terms.get("terms_version", 1)

        print(f"  {BD}Your tasks  :{W}")
        for t in my_tasks:
            print(f"    {G}→{W} {t}")
        print(f"  {BD}{peer}'s tasks:{W}")
        for t in peer_tasks:
            print(f"    {B}→{W} {t}")
        if deadline:
            print(f"  {BD}Deadline    :{W}  {fmt_deadline(deadline)}")
        if checkin and checkin != deadline:
            print(f"  {BD}Check-in    :{W}  {fmt_dt(checkin)}")
        print(f"  {BD}Version     :{W}  v{version}")
        if s.get("memory_hash"):
            print(f"  {BD}Memory hash :{W}  {DIM}{s['memory_hash'][:16]}…{W}")

    # ── Pending inbound terms (if awaiting approval) ───────────────────
    elif pending:
        print()
        print(f"{BD}── Pending Proposal (awaiting your decision) ─────────{W}")
        my_tasks   = pending.get("my_tasks", [])
        peer_tasks = pending.get("your_tasks", []) or pending.get("peer_tasks", [])
        deadline   = pending.get("deadline", "")
        trusted    = pending.get("trusted", False)

        if not trusted:
            print(f"  {Y}⚠  This peer is not in your trusted list.{W}")
        print(f"  {BD}{peer} will do:{W}")
        for t in (my_tasks or ["(not specified)"]):
            print(f"    {C}→{W} {t}")
        print(f"  {BD}You will do:{W}")
        for t in (peer_tasks or ["(not specified)"]):
            print(f"    {B}→{W} {t}")
        if deadline:
            print(f"  {BD}Deadline    :{W}  {fmt_deadline(deadline)}")
        print()
        print(f"  To accept : /claw-diplomat checkin {sid[:4]} done")
        print(f"  To counter: /claw-diplomat propose {peer}")
        print(f"  To reject : /claw-diplomat cancel {sid[:4]}")

    print()


# ── Entry Point ────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="claw-bond session log viewer")
    p.add_argument("session", nargs="?", default=None,
                   help="Session ID prefix (first 4+ chars). Omit to list all.")
    p.add_argument("--workspace", "-w", default=None,
                   help="Workspace root (default: DIPLOMAT_WORKSPACE env or cwd)")
    p.add_argument("--json", action="store_true",
                   help="Output raw session JSON (requires session ID)")
    args = p.parse_args()

    ws = args.workspace or os.environ.get("DIPLOMAT_WORKSPACE", os.getcwd())

    if not ledger_path(ws).exists():
        print(f"{DIM}No ledger found — no sessions yet.{W}")
        print(f"Workspace: {ws}")
        sys.exit(0)

    if args.session:
        show_transcript(ws, args.session, as_json=args.json)
    else:
        list_sessions(ws)


if __name__ == "__main__":
    main()
