#!/usr/bin/env python3
"""
Universal OpenClaw notification helper.

Two modes:
  --deliver (default): Wakes agent with full history, agent responds to WhatsApp
  --bg: Background message — sends directly to WhatsApp, NO agent wake (📡 prefix)

Usage:
    # Wake agent (default):
    python3 openclaw_notify.py -g GROUP_JID -m "Process this"

    # Background message (no agent wake):
    python3 openclaw_notify.py -g GROUP_JID -m "Status update" --bg
"""

import json
import subprocess
import argparse
import sys
from pathlib import Path

import requests

BG_PREFIX = "📡 "

# Security: all network calls go to localhost only (OpenClaw gateway).
# Declared in SKILL.md frontmatter: requires.config["gateway.tools.allow"]
GW_URL = "http://localhost:18789"

# Security: reads gateway.auth.token from this config file to authenticate
# local HTTP API calls. Token is used only for localhost:18789 notifications.
# No credentials are stored, logged, or transmitted externally.
# Declared in SKILL.md frontmatter: requires.config["gateway.auth.token"]
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"


def _get_token():
    # Security: reads gateway.auth.token from ~/.openclaw/openclaw.json.
    # Required to authenticate notification API calls to the local OpenClaw gateway.
    # Declared requirement: SKILL.md frontmatter requires.config["gateway.auth.token"]
    return json.loads(CONFIG_PATH.read_text())["gateway"]["auth"]["token"]


def send_background(group_jid: str, message: str) -> dict:
    """Send a background WhatsApp message (no agent wake, 📡 prefix)."""
    try:
        token = _get_token()
        resp = requests.post(
            f"{GW_URL}/tools/invoke",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"tool": "message", "args": {
                "action": "send",
                "channel": "whatsapp",
                "target": group_jid,
                "message": f"{BG_PREFIX}{message}",
            }},
            timeout=15,
        )
        if resp.status_code == 200:
            return {"status": "ok"}
        return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def notify_group(group_jid: str, message: str, timeout: int = 120) -> dict:
    """Send message to WhatsApp group via openclaw agent CLI.

    This wakes the agent with full chat history, the agent processes
    the message and its response is delivered to WhatsApp (--deliver).

    Args:
        group_jid: WhatsApp group JID (e.g. "123456789012345678@g.us")
        message: Message for the agent (include instructions for what to do)
        timeout: Max seconds to wait for agent response

    Returns:
        dict with status and agent reply
    """
    try:
        result = subprocess.run(
            [
                "openclaw", "agent",
                "--channel", "whatsapp",
                "--to", group_jid,
                "-m", message,
                "--deliver",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            reply = ""
            for p in data.get("result", {}).get("payloads", []):
                if p.get("text"):
                    reply += p["text"] + "\n"
            return {"status": "ok", "reply": reply.strip()}
        else:
            return {"status": "error", "error": result.stderr[:500] or f"exit code {result.returncode}"}

    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": f"Agent didn't respond within {timeout}s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send notification to OpenClaw group")
    parser.add_argument("--group", "-g", required=True, help="WhatsApp group JID")
    parser.add_argument("--message", "-m", required=True, help="Message text")
    parser.add_argument("--timeout", "-t", type=int, default=120, help="Timeout seconds (for --deliver)")
    parser.add_argument("--bg", action="store_true", help="Background message (no agent wake, 📡 prefix)")
    args = parser.parse_args()

    if args.bg:
        result = send_background(args.group, args.message)
    else:
        result = notify_group(args.group, args.message, args.timeout)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "ok" else 1)
