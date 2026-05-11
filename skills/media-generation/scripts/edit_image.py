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
    failure_hints,
    load_provider,
    request_exception_hint,
    run_fetch_helper,
)


DEFAULT_PROVIDER = os.environ.get("OPENCLAW_MEDIA_PROVIDER")
DEFAULT_MODEL = os.environ.get("OPENCLAW_MEDIA_EDIT_MODEL", "image-edit-model")
DEFAULT_CONFIG = str(default_config_path())
DEFAULT_OUT_DIR = str(default_output_dir("images"))


def parse_args():
    p = argparse.ArgumentParser(description="Call the configured image-edit model and optionally download the result.")
    p.add_argument("--image", required=True, help="Path to the source image")
    p.add_argument("--prompt", required=True, help="Editing prompt")
    p.add_argument("--mask", help="Optional mask image path for localized edits")
    p.add_argument("--config", default=DEFAULT_CONFIG, help="OpenClaw config path (default: ~/.openclaw/openclaw.json or OPENCLAW_CONFIG env var)")
    p.add_argument("--provider", default=DEFAULT_PROVIDER, help="Provider key inside models.providers (defaults to OPENCLAW_MEDIA_PROVIDER env var or the first provider in config)")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Image edit model id (defaults to OPENCLAW_MEDIA_EDIT_MODEL env var or a placeholder)")
    p.add_argument("--endpoint", default="/images/edits", help="Relative API endpoint")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Directory for downloaded outputs")
    p.add_argument("--prefix", default="edited", help="Output filename prefix")
    p.add_argument("--timeout", type=int, default=180, help="HTTP timeout in seconds")
    p.add_argument("--download", dest="download", action="store_true", help="Download the returned media URL/path")
    p.add_argument("--no-download", dest="download", action="store_false", help="Only print raw response")
    p.set_defaults(download=True)
    p.add_argument("--print-json", action="store_true", help="Print a JSON summary instead of plain text")
    return p.parse_args()


def extract_first_ref(payload):
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                for key in ("url", "b64_json", "path"):
                    if first.get(key):
                        return first[key]
        for key in ("url", "path"):
            if payload.get(key):
                return payload[key]
    return None


def download_media(script_dir: Path, response_text: str, origin: str, out_dir: str, prefix: str):
    return run_fetch_helper(script_dir, response_text, out_dir, prefix, origin=origin)


def main():
    args = parse_args()
    config_path = Path(args.config).expanduser()
    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"image not found: {image_path}")
    mask_path = Path(args.mask) if args.mask else None
    if mask_path and not mask_path.exists():
        raise SystemExit(f"mask not found: {mask_path}")

    base_url, api_key, resolved_provider = load_provider(config_path, args.provider)
    url = base_url + args.endpoint
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    if args.model == "image-edit-model":
        print("WARN: using placeholder model 'image-edit-model'. Pass --model or set the OPENCLAW_MEDIA_EDIT_MODEL env var for a real provider model name.", file=sys.stderr)

    try:
        with image_path.open("rb") as f:
            files = {"image": (image_path.name, f, "application/octet-stream")}
            if mask_path:
                with mask_path.open("rb") as mf:
                    files["mask"] = (mask_path.name, mf, "image/png")
                    resp = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, data={"model": args.model, "prompt": args.prompt}, files=files, timeout=args.timeout)
            else:
                resp = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, data={"model": args.model, "prompt": args.prompt}, files=files, timeout=args.timeout)
    except requests.RequestException as e:
        raise SystemExit(request_exception_hint(e))

    raw_text = resp.text
    summary = {
        "status": resp.status_code,
        "ok": resp.ok,
        "model": args.model,
        "provider": resolved_provider,
        "endpoint": url,
        "mask": str(mask_path) if mask_path else None,
        "response": None,
        "downloaded": None,
        "hints": failure_hints(resp.status_code, args.endpoint, "image editing"),
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
        origin = base_url if ref and isinstance(ref, str) and ref.startswith("/") else None
        downloaded = download_media(Path(__file__).resolve().parent, response_text, origin, args.out_dir, args.prefix)
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
