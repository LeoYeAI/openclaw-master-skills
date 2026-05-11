#!/usr/bin/env python3
"""
test_integration.py — Smoke test the full Hummingbot dev stack.

Tests:
  1. Hummingbot API health
  2. Local hummingbot source active in API env
  3. Gateway health
  4. API → Gateway connectivity
  5. Connectors list accessible
  6. Gateway wallet endpoint accessible

Usage:
  python scripts/test_integration.py
  python scripts/test_integration.py --json
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

API_URL = os.environ.get("HUMMINGBOT_API_URL", "http://localhost:8000")
GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:15888")
API_USER = os.environ.get("API_USER") or os.environ.get("API_USER", "admin")
API_PASS = os.environ.get("API_PASS") or os.environ.get("API_PASS", "admin")

# Load .env file (first match wins)
_ENV_PATHS = [
    "hummingbot-api/.env",
    os.path.expanduser("~/.hummingbot/.env"),
    ".env",
]
for _p in _ENV_PATHS:
    if os.path.exists(_p):
        with open(_p) as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    k, _, v = _line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        break

API_URL = os.environ.get("HUMMINGBOT_API_URL", API_URL)
API_USER = os.environ.get("API_USER") or os.environ.get("API_USER", USERNAME)
API_PASS = os.environ.get("API_PASS") or os.environ.get("API_PASS", PASSWORD)


def http_get(url, auth=None, timeout=5):
    """Simple HTTP GET. Returns (status_code, body_str) or raises."""
    req = urllib.request.Request(url)
    if auth:
        import base64
        creds = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {creds}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


def check_hummingbot_source():
    """Check if local hummingbot source is active in hummingbot-api conda env."""
    hb_dir = os.environ.get("HUMMINGBOT_DIR", os.path.expanduser("~/Documents/hummingbot"))
    try:
        result = subprocess.run(
            ["conda", "run", "-n", "hummingbot-api", "python", "-c",
             "import hummingbot; print(hummingbot.__file__)"],
            capture_output=True, text=True, timeout=10
        )
        path = result.stdout.strip()
        if path and path.startswith(hb_dir):
            return True, path
        elif path:
            return False, f"Using PyPI version: {path}"
        else:
            return False, "Could not determine hummingbot source"
    except Exception as e:
        return False, str(e)


def run_tests(json_output=False):
    results = []

    def test(name, ok, detail=""):
        results.append({"name": name, "ok": ok, "detail": detail})
        if not json_output:
            icon = "✓" if ok else "✗"
            msg = f"  {icon} {name}"
            if detail:
                msg += f": {detail}"
            print(msg)

    # 1. API health
    status, body = http_get(f"{API_URL}/health")
    test("API health", status == 200, f"{API_URL}" if status == 200 else f"HTTP {status} — {body[:80]}")

    # 2. Local hummingbot source
    local_ok, local_detail = check_hummingbot_source()
    test("Local hummingbot source", local_ok, local_detail[:80] if local_ok else local_detail)

    # 3. Gateway health
    status, body = http_get(f"{GATEWAY_URL}/")
    test("Gateway health", status == 200, f"{GATEWAY_URL}" if status == 200 else f"HTTP {status} — start with: pnpm start --passphrase=hummingbot --dev")

    # 4. API → Gateway connectivity
    status, body = http_get(f"{API_URL}/gateway/status", auth=(API_USER, API_PASS))
    gw_connected = status in (200, 503)  # 503 = gateway not available (API reached though)
    if status == 200:
        try:
            d = json.loads(body)
            gw_connected = True
            detail = "connected"
        except Exception:
            detail = f"HTTP {status}"
    elif status == 503:
        gw_connected = False
        detail = "API running but Gateway unreachable — check GATEWAY_URL in .env"
    else:
        detail = f"HTTP {status}"
    test("API → Gateway", status == 200, detail)

    # 5. Connectors list
    status, body = http_get(f"{API_URL}/connectors/", auth=(API_USER, API_PASS))
    if status == 200:
        try:
            connectors = json.loads(body)
            count = len(connectors) if isinstance(connectors, list) else "?"
            test("Connectors list", True, f"{count} connectors available")
        except Exception:
            test("Connectors list", True, "accessible")
    else:
        test("Connectors list", False, f"HTTP {status}")

    # 6. Gateway wallets endpoint
    status, body = http_get(f"{API_URL}/accounts/gateway/wallets", auth=(API_USER, API_PASS))
    test("Gateway wallets endpoint", status in (200, 503), f"HTTP {status}")

    all_ok = all(r["ok"] for r in results)

    if json_output:
        print(json.dumps({"tests": results, "all_ok": all_ok}, indent=2))
    else:
        print()
        if all_ok:
            print("✓ All tests passed — full dev stack is operational")
        else:
            failed = [r["name"] for r in results if not r["ok"]]
            print(f"✗ {len(failed)} test(s) failed: {', '.join(failed)}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hummingbot dev stack smoke tests")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if not args.json:
        print("Integration Tests")
        print("=================")

    sys.exit(run_tests(json_output=args.json))
