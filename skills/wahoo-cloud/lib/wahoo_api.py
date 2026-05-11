"""Wahoo Cloud API client.

Thin wrapper over /v1/workouts and /v1/user. Auto-refreshes the access
token on 401 (once), and respects rate-limit headers — backs off on 429
using X-RateLimit-Reset.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterator, Optional

# Make sibling modules importable when this file is loaded as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import wahoo_auth  # noqa: E402

API_BASE = "https://api.wahooligan.com"
USER_AGENT = "openclaw-wahoo-skill/0.1.0"


class WahooAPIError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"Wahoo API HTTP {status}: {body[:300]}")
        self.status = status
        self.body = body


def _request(
    method: str,
    path: str,
    *,
    params: Optional[dict] = None,
    body: Optional[bytes] = None,
    token: Optional[str] = None,
    retried: bool = False,
) -> tuple[dict, dict]:
    if token is None:
        token = wahoo_auth.access_token()

    url = f"{API_BASE}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8") or "{}")
            return payload, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        if e.code == 401 and not retried:
            wahoo_auth.refresh()
            return _request(
                method, path, params=params, body=body, retried=True
            )
        if e.code == 429 and not retried:
            reset = int(e.headers.get("X-RateLimit-Reset", "60") or "60")
            wait = max(1, reset - int(time.time())) if reset > 10**9 else reset
            print(f"  ⏳ rate-limited; sleeping {wait}s", flush=True)
            time.sleep(min(wait, 300))
            return _request(
                method, path, params=params, body=body, retried=True
            )
        raise WahooAPIError(e.code, body_text) from None


def get_user() -> dict:
    payload, _ = _request("GET", "/v1/user")
    return payload


def list_workouts(page: int = 1, per_page: int = 30) -> dict:
    payload, _ = _request(
        "GET",
        "/v1/workouts",
        params={"page": page, "per_page": per_page},
    )
    return payload


def iter_workouts(per_page: int = 30, max_pages: int = 200) -> Iterator[dict]:
    """Yield workout summaries (with workout_summary=null per Wahoo's API)."""
    page = 1
    while page <= max_pages:
        payload = list_workouts(page=page, per_page=per_page)
        items = payload.get("workouts", [])
        if not items:
            return
        for item in items:
            yield item
        total = payload.get("total", 0)
        if page * per_page >= total:
            return
        page += 1


def get_workout(workout_id: int) -> dict:
    payload, _ = _request("GET", f"/v1/workouts/{workout_id}")
    return payload


def download_fit(url: str, dest: Path) -> Path:
    """Download a FIT file from Wahoo's CDN. No auth required."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            f.write(chunk)
    return dest


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Wahoo API client")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("user")
    lp = sub.add_parser("list")
    lp.add_argument("--page", type=int, default=1)
    lp.add_argument("--per-page", type=int, default=30)
    gp = sub.add_parser("get")
    gp.add_argument("id", type=int)
    args = p.parse_args()

    if args.cmd == "user":
        print(json.dumps(get_user(), indent=2))
    elif args.cmd == "list":
        print(json.dumps(list_workouts(args.page, args.per_page), indent=2))
    elif args.cmd == "get":
        print(json.dumps(get_workout(args.id), indent=2))


if __name__ == "__main__":
    _cli()
