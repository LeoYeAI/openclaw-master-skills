#!/usr/bin/env python3
"""Guardrail for Claude/Figma MCP auth flows.

Purpose:
- Detect concurrent/stale Claude auth sessions before starting a new flow.
- Refuse fresh login attempts while an auth lock already exists.
- Force agents to stop instead of improvising around multiple active states.

Usage:
  python3 scripts/auth_session_guard.py --mode claude-login
  python3 scripts/auth_session_guard.py --mode figma-mcp

Exit codes:
  0 = clear
  2 = conflict/stale state detected
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "tmp" / "claude-auth-lock.json"
SELF_MARKERS = {
    "pgrep -af claude",
    "auth_session_guard.py",
}


def sh(command: str) -> str:
    return subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    ).stdout


def list_processes() -> List[str]:
    out = sh("pgrep -af claude || true")
    lines = []
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        if any(marker in line for marker in SELF_MARKERS):
            continue
        lines.append(line)
    return lines


def load_lock() -> dict | None:
    if not LOCK_PATH.exists():
        return None
    return json.loads(LOCK_PATH.read_text())


def classify(lines: List[str]) -> dict:
    login_lines = [line for line in lines if "claude auth login" in line]
    repl_lines = [line for line in lines if line not in login_lines]
    return {
        "all": lines,
        "loginProcesses": login_lines,
        "claudeProcesses": repl_lines,
        "loginCount": len(login_lines),
        "claudeCount": len(lines),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Detect conflicting Claude auth sessions")
    p.add_argument("--mode", choices=["claude-login", "figma-mcp"], required=True)
    args = p.parse_args()

    info = classify(list_processes())
    lock = load_lock()
    problems = []
    recommended_action = None

    if args.mode == "claude-login":
        if lock:
            problems.append("active auth lock exists; reuse or clear it before starting another login")
            recommended_action = "reuse-or-clear-lock"
        if info["claudeCount"] >= 1:
            problems.append("an existing Claude process is already active; do not start another login flow")
            recommended_action = recommended_action or "reuse-existing-session"
        if info["loginCount"] > 1:
            problems.append("multiple 'claude auth login' processes detected")
            recommended_action = "kill-stale-sessions"
    else:
        if info["claudeCount"] > 1:
            problems.append("multiple Claude processes detected; keep exactly one live Claude session during MCP auth")
            recommended_action = "kill-stale-sessions"

    status = "AUTH_SESSION_CLEAR" if not problems else "AUTH_SESSION_CONFLICT"
    payload = {
        "status": status,
        "mode": args.mode,
        "problems": problems,
        "recommendedAction": recommended_action,
        "lockPath": str(LOCK_PATH),
        "activeLock": lock,
        "processes": info["all"],
        "loginCount": info["loginCount"],
        "claudeCount": info["claudeCount"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if problems:
        print(
            "ERROR: auth session is not clean. Reuse the locked/current Claude session or clear stale state before continuing.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
