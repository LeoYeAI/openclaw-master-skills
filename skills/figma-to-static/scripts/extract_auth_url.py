#!/usr/bin/env python3
"""Extract a full Claude OAuth authorize URL from wrapped terminal/chat text.

Usage:
  cat raw-output.txt | python3 scripts/extract_auth_url.py --stdin
  python3 scripts/extract_auth_url.py --text "...raw claude output..."
"""

from __future__ import annotations

import argparse
import re
import sys


PREFIX = "https://claude.ai/oauth/authorize?"
REQUIRED_KEYS = [
    "client_id=",
    "response_type=",
    "redirect_uri=",
    "scope=",
    "code_challenge=",
    "code_challenge_method=",
    "state=",
]
URL_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=%")


def normalize_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", text)


def take_url_fragment(line: str, must_find_prefix: bool) -> str:
    source = line
    if must_find_prefix:
        idx = source.find(PREFIX)
        if idx == -1:
            return ""
        source = source[idx:]
    else:
        source = source.lstrip()

    buf = []
    for ch in source:
        if ch in URL_CHARS:
            buf.append(ch)
            continue
        if ch.isspace():
            break
        break
    return "".join(buf)


def extract(text: str) -> str | None:
    raw = normalize_ansi(text)
    lines = raw.splitlines()
    pieces: list[str] = []
    started = False

    for line in lines:
        stripped = line.strip()
        if started and (not stripped or stripped.startswith("Paste code here") or stripped.startswith("Esc to cancel")):
            break

        frag = take_url_fragment(line, must_find_prefix=not started)
        if not frag:
            if started:
                break
            continue

        pieces.append(frag)
        started = True

        current = "".join(pieces)
        if current.startswith(PREFIX) and all(key in current for key in REQUIRED_KEYS) and re.search(r"(?:^|[?&])state=[^&\s]+$", current):
            return current

    current = "".join(pieces)
    if current.startswith(PREFIX) and all(key in current for key in REQUIRED_KEYS):
        return current
    return None


def main() -> int:
    p = argparse.ArgumentParser(description="Extract Claude authorize URL")
    p.add_argument("--stdin", action="store_true", help="Read raw text from stdin")
    p.add_argument("--text", help="Raw text containing a wrapped authorize URL")
    args = p.parse_args()

    if args.stdin:
        raw = sys.stdin.read()
    elif args.text:
        raw = args.text
    else:
        p.error("provide --stdin or --text")

    url = extract(raw)
    if not url:
        print("ERROR: no Claude authorize URL found", file=sys.stderr)
        return 2

    if not url.startswith(PREFIX):
        print("ERROR: extracted URL did not match expected prefix", file=sys.stderr)
        return 3

    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
