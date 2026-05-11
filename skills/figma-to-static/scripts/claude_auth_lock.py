#!/usr/bin/env python3
"""Manage a single active Claude OAuth handoff lock.

Purpose:
- Persist the one active Claude login state across chat/tool turns.
- Refuse stale code/callback submissions that do not match the active state.

Usage:
  python3 scripts/claude_auth_lock.py status
  python3 scripts/claude_auth_lock.py acquire --session-id abc --auth-url "https://claude.ai/oauth/authorize?...&state=..."
  python3 scripts/claude_auth_lock.py verify-code --code-state "code#state"
  python3 scripts/claude_auth_lock.py verify-callback --callback-url "https://platform.claude.com/oauth/code/callback?code=...&state=..."
  python3 scripts/claude_auth_lock.py clear
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent.parent
LOCK_DIR = ROOT / "tmp"
LOCK_PATH = LOCK_DIR / "claude-auth-lock.json"
AUTHORIZE_PREFIX = "https://claude.ai/oauth/authorize?"


def get_param(url: str, key: str) -> str | None:
    values = parse_qs(urlparse(url).query).get(key) or []
    return values[0] if values else None


def parse_code_state(text: str) -> tuple[str | None, str | None]:
    value = (text or "").strip()
    if "#" not in value:
        return None, None
    code, state = value.split("#", 1)
    code = code.strip() or None
    state = state.strip() or None
    return code, state


def load_lock() -> dict | None:
    if not LOCK_PATH.exists():
        return None
    return json.loads(LOCK_PATH.read_text())


def save_lock(payload: dict) -> None:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_status(_: argparse.Namespace) -> int:
    lock = load_lock()
    if not lock:
        print_json({"status": "NO_ACTIVE_LOCK", "lockPath": str(LOCK_PATH)})
        return 0
    print_json({"status": "ACTIVE_LOCK", "lockPath": str(LOCK_PATH), "lock": lock})
    return 0


def cmd_clear(_: argparse.Namespace) -> int:
    lock = load_lock()
    if LOCK_PATH.exists():
        LOCK_PATH.unlink()
    print_json({"status": "LOCK_CLEARED", "hadLock": bool(lock), "lockPath": str(LOCK_PATH)})
    return 0


def cmd_acquire(args: argparse.Namespace) -> int:
    auth_state = get_param(args.auth_url, "state")
    if not args.auth_url.startswith(AUTHORIZE_PREFIX) or not auth_state:
        print("ERROR: auth-url must be a Claude authorize URL with state", file=sys.stderr)
        return 2

    existing = load_lock()
    if existing and not args.force:
        print_json(
            {
                "status": "LOCK_CONFLICT",
                "reason": "active lock already exists",
                "lockPath": str(LOCK_PATH),
                "existing": existing,
            }
        )
        return 3

    now = int(time.time())
    payload = {
        "phase": args.phase,
        "sessionId": args.session_id,
        "pid": args.pid,
        "authUrl": args.auth_url,
        "authState": auth_state,
        "createdAt": now,
        "updatedAt": now,
    }
    save_lock(payload)
    print_json({"status": "LOCK_ACQUIRED", "lockPath": str(LOCK_PATH), "lock": payload})
    return 0


def cmd_verify_code(args: argparse.Namespace) -> int:
    lock = load_lock()
    if not lock:
        print_json({"status": "NO_ACTIVE_LOCK", "lockPath": str(LOCK_PATH)})
        return 2

    code, state = parse_code_state(args.code_state)
    result = {
        "status": "CODE_STATE_CHECK",
        "lockPath": str(LOCK_PATH),
        "hasCode": bool(code),
        "inputState": state,
        "expectedState": lock.get("authState"),
        "stateMatch": bool(code and state and state == lock.get("authState")),
        "sessionId": lock.get("sessionId"),
    }
    print_json(result)
    if not code:
        print("ERROR: expected input format code#state", file=sys.stderr)
        return 3
    if not result["stateMatch"]:
        print("ERROR: code#state does not match active auth state", file=sys.stderr)
        return 4
    return 0


def cmd_verify_callback(args: argparse.Namespace) -> int:
    lock = load_lock()
    if not lock:
        print_json({"status": "NO_ACTIVE_LOCK", "lockPath": str(LOCK_PATH)})
        return 2

    cb_state = get_param(args.callback_url, "state")
    cb_code = get_param(args.callback_url, "code")
    result = {
        "status": "CALLBACK_CHECK",
        "lockPath": str(LOCK_PATH),
        "hasCode": bool(cb_code),
        "inputState": cb_state,
        "expectedState": lock.get("authState"),
        "stateMatch": bool(cb_code and cb_state and cb_state == lock.get("authState")),
        "sessionId": lock.get("sessionId"),
    }
    print_json(result)
    if not cb_code:
        print("ERROR: callback URL missing code", file=sys.stderr)
        return 3
    if not result["stateMatch"]:
        print("ERROR: callback URL state does not match active auth state", file=sys.stderr)
        return 4
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Persist and validate the active Claude auth state")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("status")
    sub.add_parser("clear")

    acquire = sub.add_parser("acquire")
    acquire.add_argument("--session-id", required=True)
    acquire.add_argument("--auth-url", required=True)
    acquire.add_argument("--phase", default="claude-login")
    acquire.add_argument("--pid", type=int)
    acquire.add_argument("--force", action="store_true")

    verify_code = sub.add_parser("verify-code")
    verify_code.add_argument("--code-state", required=True)

    verify_cb = sub.add_parser("verify-callback")
    verify_cb.add_argument("--callback-url", required=True)

    return p


COMMANDS = {
    "status": cmd_status,
    "clear": cmd_clear,
    "acquire": cmd_acquire,
    "verify-code": cmd_verify_code,
    "verify-callback": cmd_verify_callback,
}


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return COMMANDS[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
