#!/usr/bin/env python3
"""Call Craftsman Agent OneKey Router to generate a LEGO build plan."""

import argparse
import json
import os
import sys
from urllib import request, parse, error

ENDPOINT = "https://agent.deepnlp.org/agent_router"
UNIQUE_ID = "craftsman-agent/craftsman-agent"
API_ID = "generate_lego_build_plan"
ENV_KEY = "DEEPNLP_ONEKEY_ROUTER_ACCESS"
ONEKEY_HEADER = "X-OneKey"


def die_missing_key():
    sys.stderr.write(
        "DEEPNLP_ONEKEY_ROUTER_ACCESS is not set. "
        "Set it before running this script.\n"
    )
    sys.stderr.write("Set with: export DEEPNLP_ONEKEY_ROUTER_ACCESS=YOUR_API_KEY\n")
    return

def validate_image_urls(urls):
    for url in urls:
        parsed = parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid ref image URL scheme: {url}")

def build_payload(prompt, images, mode):
    return {
        "unique_id": UNIQUE_ID,
        "api_id": API_ID,
        "data": {
            "prompt": prompt,
            "images": images,
            "mode": mode,
        },
    }


def post_json(url, payload, api_key):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", ONEKEY_HEADER: api_key},
        method="POST",
    )
    with request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, body


def main():
    parser = argparse.ArgumentParser(description="Generate LEGO build plan via Craftsman Agent")
    parser.add_argument("--prompt", required=True, help="Text prompt for the build")
    parser.add_argument(
        "--images",
        action="append",
        default=[],
        help="Reference image URL (repeatable)",
    )
    parser.add_argument("--mode", default="basic", help="demo|basic|standard|advanced")
    args = parser.parse_args()

    api_key = os.getenv(ENV_KEY)
    if not api_key:
        die_missing_key()
        api_key = ""

    url = ENDPOINT
    try:
        validate_image_urls(args.images)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(2)

    payload = build_payload(args.prompt, args.images, args.mode)

    try:
        status, body = post_json(url, payload, api_key)
    except error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        sys.stderr.write(f"HTTP {e.code}: {error_body}\n")
        sys.exit(1)
    except error.URLError as e:
        sys.stderr.write(f"Network error: {e.reason}\n")
        sys.exit(1)

    try:
        parsed = json.loads(body)
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        print(body)


if __name__ == "__main__":
    main()
