#!/usr/bin/env python3
"""Classify Claude REPL auth/onboarding terminal state from scraped output.

Purpose:
- Prevent sending auth artifacts to the wrong prompt/state.
- Force an explicit check that the REPL is actually waiting for `code#state`.

Usage:
  python3 scripts/claude_repl_state.py --text "...raw terminal output..."
  cat repl.log | python3 scripts/claude_repl_state.py --stdin

Exit codes:
  0 = state detected successfully
  2 = unknown/ambiguous state
"""

from __future__ import annotations

import argparse
import json
import re
import sys

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

STATES = [
    (
        "waiting-for-code",
        [
            "Paste code here if prompted >",
            "Browser didn't open? Use the url below to sign in",
        ],
        "Safe to ask user for code#state and inject it into this same session.",
    ),
    (
        "login-method-picker",
        [
            "Select login method:",
            "Claude account with subscription",
        ],
        "Select a login method first; do not ask the user for code yet.",
    ),
    (
        "theme-picker",
        [
            "Choose the text style that looks best with your terminal",
            "Dark mode",
        ],
        "Complete first-run theme setup before starting auth.",
    ),
    (
        "welcome-shell",
        [
            "Welcome to Claude Code",
            "Let's get started.",
        ],
        "REPL started but auth prompt is not ready yet.",
    ),
    (
        "signed-in",
        [
            "Bypassing Permissions",
        ],
        "Claude appears signed in and inside a normal session.",
    ),
]


def clean(text: str) -> str:
    text = ANSI_RE.sub("", text)
    text = text.replace("\r", "")
    return text


def classify(text: str) -> dict:
    normalized = clean(text)
    for state, needles, advice in STATES:
        if all(needle in normalized for needle in needles):
            return {
                "status": "OK",
                "state": state,
                "advice": advice,
                "safeForCodeSubmission": state == "waiting-for-code",
            }
    return {
        "status": "UNKNOWN",
        "state": None,
        "advice": "State is ambiguous. Scrape fresh REPL output before asking user for auth data.",
        "safeForCodeSubmission": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Classify Claude REPL auth state from raw terminal output")
    p.add_argument("--stdin", action="store_true", help="Read terminal text from stdin")
    p.add_argument("--text", help="Terminal text to classify")
    args = p.parse_args()

    if args.stdin:
        raw = sys.stdin.read()
    elif args.text is not None:
        raw = args.text
    else:
        p.error("provide --stdin or --text")

    result = classify(raw)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
