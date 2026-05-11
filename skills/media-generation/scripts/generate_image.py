#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

from media_request_common import (
    default_config_path,
    default_output_dir,
    extract_first_ref,
    failure_hints,
    load_provider,
    merge_extra_json,
    request_exception_hint,
    run_fetch_helper,
)


DEFAULT_PROVIDER = os.environ.get("OPENCLAW_MEDIA_PROVIDER")
DEFAULT_MODEL = os.environ.get("OPENCLAW_MEDIA_IMAGE_MODEL", "image-model")
DEFAULT_CONFIG = str(default_config_path())
DEFAULT_OUT_DIR = str(default_output_dir("images"))


def parse_args():
    p = argparse.ArgumentParser(description="Call the configured image-generation model and optionally download the result.")
    p.add_argument("--prompt", required=True, help="Generation prompt")
    p.add_argument("--config", default=DEFAULT_CONFIG, help="OpenClaw config path (default: ~/.openclaw/openclaw.json or OPENCLAW_CONFIG env var)")
    p.add_argument("--provider", default=DEFAULT_PROVIDER, help="Provider key inside models.providers (defaults to OPENCLAW_MEDIA_PROVIDER env var or the first provider in config)")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Image generation model id (defaults to OPENCLAW_MEDIA_IMAGE_MODEL env var or a placeholder)")
    p.add_argument("--endpoint", default="/images/generations", help="Relative API endpoint")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Directory for downloaded outputs")
    p.add_argument("--prefix", default="generated", help="Output filename prefix")
    p.add_argument("--size", help="Optional size, e.g. 1024x1024")
    p.add_argument("--quality", help="Optional provider-specific quality")
    p.add_argument("--style", help="Optional provider-specific style")
    p.add_argument("--background", help="Optional background mode, e.g. transparent")
    p.add_argument("--n", type=int, help="Optional number of outputs")
    p.add_argument("--seed", type=int, help="Optional random seed if supported by provider")
    p.add_argument("--extra-json", help="Extra JSON object merged into the request body")
    p.add_argument("--extra-json-file", help="Path to a JSON file merged into the request body")
    p.add_argument("--timeout", type=int, default=300, help="HTTP timeout in seconds")
    p.add_argument("--download", dest="download", action="store_true", help="Download the returned media URL/path")
    p.add_argument("--no-download", dest="download", action="store_false", help="Only print raw response")
    p.set_defaults(download=True)
    p.add_argument("--print-json", action="store_true", help="Print a JSON summary instead of plain text")
    return p.parse_args()


def build_payload(args):
    payload = {"model": args.model, "prompt": args.prompt}
    optional = {
        "size": args.size,
        "quality": args.quality,
        "style": args.style,
        "background": args.background,
        "n": args.n,
        "seed": args.seed,
    }
    for key, value in optional.items():
        if value is not None:
            payload[key] = value
    return merge_extra_json(payload, args.extra_json, args.extra_json_file)


def main():
    args = parse_args()
    config_path = Path(args.config).expanduser()
    base_url, api_key, resolved_provider = load_provider(config_path, args.provider)
    url = base_url + args.endpoint
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    payload = build_payload(args)
    if args.model == "image-model":
        print("WARN: using placeholder model 'image-model'. Pass --model or set the OPENCLAW_MEDIA_IMAGE_MODEL env var for a real provider model name.", file=sys.stderr)
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=args.timeout,
        )
    except requests.RequestException as e:
        raise SystemExit(request_exception_hint(e))

    raw_text = resp.text
    summary = {
        "status": resp.status_code,
        "ok": resp.ok,
        "model": args.model,
        "provider": resolved_provider,
        "endpoint": url,
        "request": payload,
        "response": None,
        "downloaded": None,
        "hints": failure_hints(resp.status_code, args.endpoint, "image generation"),
    }

    parsed = None
    try:
        parsed = resp.json()
        summary["response"] = parsed
    except Exception:
        summary["response"] = raw_text

    if not resp.ok:
        if args.print_json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"STATUS: {resp.status_code}")
            print(raw_text)
            for hint in summary["hints"]:
                print(f"HINT: {hint}")
        raise SystemExit(1)

    if args.download:
        ref = extract_first_ref(parsed) if parsed is not None else None
        response_text = json.dumps(parsed, ensure_ascii=False) if parsed is not None else raw_text
        origin = base_url if isinstance(ref, str) and ref.startswith("/") else None
        downloaded = run_fetch_helper(Path(__file__).resolve().parent, response_text, args.out_dir, args.prefix, origin=origin)
        summary["downloaded"] = downloaded

    if args.print_json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"STATUS: {resp.status_code}")
        if parsed is not None:
            print(json.dumps(parsed, ensure_ascii=False))
        else:
            print(raw_text)
        if summary["downloaded"]:
            print(f"DOWNLOADED: {summary['downloaded']}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else str(e)
        print(f"ERROR: download helper failed: {stderr}", file=sys.stderr)
        raise
