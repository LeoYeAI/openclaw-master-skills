#!/usr/bin/env python3
"""Validate Claude OAuth callback data against the active authorize state.

Usage:
  python3 scripts/parse_claude_oauth_callback.py \
    --auth-url "https://.../oauth/authorize?...&state=..." \
    --callback-url "https://platform.claude.com/oauth/code/callback?code=...&state=..."

  python3 scripts/parse_claude_oauth_callback.py \
    --auth-url "https://.../oauth/authorize?...&state=..." \
    --code-state "code#state"
"""

import argparse
import json
import sys
from urllib.parse import parse_qs, urlparse


def get_param(url: str, key: str):
    qs = parse_qs(urlparse(url).query)
    values = qs.get(key) or []
    return values[0] if values else None


def parse_code_state(value: str):
    text = (value or "").strip()
    if "#" not in text:
        return None, None
    code, state = text.split("#", 1)
    return (code.strip() or None), (state.strip() or None)


def main():
    p = argparse.ArgumentParser(description="Validate Claude OAuth callback data")
    p.add_argument("--auth-url", required=True, help="Authorize URL printed by Claude login flow")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--callback-url", help="Callback URL user pasted after auth")
    group.add_argument("--code-state", help="Authentication Code in code#state format")
    args = p.parse_args()

    auth_state = get_param(args.auth_url, "state")
    auth_redirect = get_param(args.auth_url, "redirect_uri")

    if args.callback_url:
        input_kind = "callback-url"
        cb_state = get_param(args.callback_url, "state")
        cb_code = get_param(args.callback_url, "code")
    else:
        input_kind = "code-state"
        cb_code, cb_state = parse_code_state(args.code_state)

    result = {
        "inputKind": input_kind,
        "authState": auth_state,
        "callbackState": cb_state,
        "stateMatch": bool(auth_state and cb_state and auth_state == cb_state),
        "hasCode": bool(cb_code),
        "callbackCodePreview": (cb_code[:6] + "...") if cb_code else None,
        "authRedirectUri": auth_redirect,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result["hasCode"]:
        print("ERROR: callback data missing code", file=sys.stderr)
        sys.exit(2)
    if not result["stateMatch"]:
        print("ERROR: callback state mismatch (stale/invalid callback)", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
