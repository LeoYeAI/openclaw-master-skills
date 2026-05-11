#!/usr/bin/env python3
"""Interactive Wahoo OAuth2 setup.

Prints the authorization URL, then prompts you to paste back either the
full redirect URL (https://localhost:8080/?code=XXX) or just the code.
Exchanges it for an access_token + refresh_token and writes both to
~/.openclaw/secrets/wahoo_tokens.json.
"""

from __future__ import annotations

import sys
import urllib.parse
from pathlib import Path

# Make the sibling lib/ package importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import wahoo_auth  # noqa: E402


def _extract_code(value: str) -> str:
    value = value.strip()
    if not value:
        raise SystemExit("No input — aborting.")
    if "code=" not in value:
        return value
    parsed = urllib.parse.urlparse(value)
    qs = urllib.parse.parse_qs(parsed.query)
    if "code" in qs:
        return qs["code"][0]
    raise SystemExit(f"Could not find ?code= in {value!r}")


def main() -> None:
    try:
        url = wahoo_auth.authorize_url()
    except wahoo_auth.WahooAuthError as e:
        raise SystemExit(f"❌ {e}")

    print("=" * 72)
    print("Wahoo OAuth2 Setup")
    print("=" * 72)
    print()
    print("1) Open this URL in a browser and approve the requested scopes:")
    print()
    print(f"   {url}")
    print()
    print("2) Wahoo will redirect you to your registered callback URL with")
    print("   ?code=… in the query string. The page itself will fail to load")
    print("   (no server is running there) — that's fine.")
    print()
    print("3) Copy the code from the redirect URL.")
    print()

    raw = input("Paste the redirect URL (or just the code): ")
    code = _extract_code(raw)
    print()
    print(f"Exchanging code ({code[:8]}…) for tokens…")

    try:
        payload = wahoo_auth.exchange_code(code)
    except wahoo_auth.WahooAuthError as e:
        raise SystemExit(f"❌ {e}")

    print("✅ Tokens saved to", wahoo_auth.TOKENS_PATH)
    print()
    print(f"  access_token  : {payload.get('access_token', '')[:16]}…")
    print(f"  refresh_token : {payload.get('refresh_token', '')[:16]}…")
    print(f"  expires_in    : {payload.get('expires_in')} s")
    print(f"  scope         : {payload.get('scope', '')}")


if __name__ == "__main__":
    main()
