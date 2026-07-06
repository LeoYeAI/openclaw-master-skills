#!/usr/bin/env python3
"""Run a read-only smoke test for the Poetize OpenClaw skill runtime contract."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from manage_blog import build_url
from publish_post import normalize_base_url, request_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Poetize OpenClaw skill wiring with a read-only API call."
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("POETIZE_BASE_URL"),
        help="Poetize base URL. Defaults to POETIZE_BASE_URL.",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("POETIZE_API_KEY"),
        help="Poetize API key. Defaults to POETIZE_API_KEY.",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=1,
        help="How many articles to request in the read-only list call.",
    )
    parser.add_argument(
        "--search-key",
        help="Optional search filter passed to list-articles.",
    )
    return parser.parse_args()


def die(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def extract_records(response: dict[str, Any]) -> list[dict[str, Any]]:
    data = response.get("data")
    if isinstance(data, dict):
        records = data.get("records")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
    return []


def main() -> None:
    args = parse_args()
    base_url = normalize_base_url(str(args.base_url or ""))
    api_key = str(args.api_key or "").strip()

    if not base_url:
        die("Missing --base-url or POETIZE_BASE_URL.")
    if not api_key:
        die("Missing --api-key or POETIZE_API_KEY.")

    params: dict[str, Any] = {"current": 1, "size": args.size}
    if args.search_key:
        params["searchKey"] = args.search_key

    checked_endpoint = build_url(base_url, "/api/api/article/list", params)
    response = request_json(
        "GET",
        checked_endpoint,
        api_key,
    )
    if response.get("code") != 200:
        die(
            "Smoke test API call did not return code 200:\n"
            + json.dumps(response, ensure_ascii=False, indent=2)
        )

    records = extract_records(response)
    summary = {
        "status": "ok",
        "checkedEndpoint": checked_endpoint,
        "baseUrl": base_url,
        "recordsReturned": len(records),
        "responseCode": response.get("code"),
        "responseMessage": response.get("message"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
