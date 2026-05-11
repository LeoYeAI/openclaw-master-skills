#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

from media_request_common import (
    default_config_path,
    default_output_dir,
    failure_hints,
    load_provider,
    merge_extra_json,
    request_exception_hint,
    run_fetch_helper,
)


DEFAULT_PROVIDER = os.environ.get("OPENCLAW_MEDIA_PROVIDER")
DEFAULT_MODEL = os.environ.get("OPENCLAW_MEDIA_VIDEO_MODEL", "video-model")
DEFAULT_CONFIG = str(default_config_path())
DEFAULT_OUT_DIR = str(default_output_dir("videos"))
DEFAULT_HEADERS = ["User-Agent: Mozilla/5.0"]


def parse_args():
    p = argparse.ArgumentParser(description="Call the configured video-generation model, poll if needed, and optionally download the result.")
    p.add_argument("--prompt", required=True, help="Request prompt")
    p.add_argument("--config", default=DEFAULT_CONFIG, help="OpenClaw config path (default: ~/.openclaw/openclaw.json or OPENCLAW_CONFIG env var)")
    p.add_argument("--provider", default=DEFAULT_PROVIDER, help="Provider key inside models.providers (defaults to OPENCLAW_MEDIA_PROVIDER env var or the first provider in config)")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Video generation model id (defaults to OPENCLAW_MEDIA_VIDEO_MODEL env var or a placeholder)")
    p.add_argument("--endpoint", default="/videos", help="Relative API endpoint")
    p.add_argument("--status-endpoint-template", default="/videos/{id}", help="Relative poll endpoint template when only an id is returned")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Directory for downloaded outputs")
    p.add_argument("--prefix", default="generated-video", help="Output filename prefix")
    p.add_argument("--size", help="Optional size, e.g. 720x1280")
    p.add_argument("--duration", help="Optional duration, e.g. 5s or 6")
    p.add_argument("--seconds", type=int, help="Optional duration in whole seconds; overrides --duration normalization when provided")
    p.add_argument("--fps", type=int, help="Optional target fps")
    p.add_argument("--seed", type=int, help="Optional random seed if supported by provider")
    p.add_argument("--image", help="Optional input image path when supported by provider")
    p.add_argument("--mode", choices=["text", "animate", "reference"], default="text", help="Request mode")
    p.add_argument("--image-transport", choices=["auto", "path", "data-url"], default="auto", help="How to serialize --image into JSON")
    p.add_argument("--image-field", choices=["image", "input_image", "first_frame_image", "reference_images"], help="Provider JSON field for the image input")
    p.add_argument("--extra-json", help="Extra JSON object merged into the request body")
    p.add_argument("--extra-json-file", help="Path to a JSON file merged into the request body")
    p.add_argument("--timeout", type=int, default=600, help="HTTP timeout in seconds")
    p.add_argument("--poll-interval", type=float, default=5.0, help="Seconds between poll attempts")
    p.add_argument("--max-polls", type=int, default=60, help="Maximum poll attempts when the job is asynchronous")
    p.add_argument("--download", dest="download", action="store_true", help="Download the returned media URL/path")
    p.add_argument("--no-download", dest="download", action="store_false", help="Only print raw response")
    p.set_defaults(download=True)
    p.add_argument("--print-json", action="store_true", help="Print a JSON summary instead of plain text")
    return p.parse_args()


def normalize_seconds(duration_text):
    if duration_text is None:
        return None
    text = str(duration_text).strip().lower()
    if text.endswith("s"):
        text = text[:-1].strip()
    if not text:
        return None
    try:
        value = int(float(text))
    except ValueError:
        raise SystemExit(f"invalid --duration value: {duration_text}")
    if value <= 0:
        raise SystemExit("duration/seconds must be positive")
    return value


def choose_image_field(args):
    if args.image_field:
        return args.image_field
    if args.mode == "animate":
        return "first_frame_image"
    if args.mode == "reference":
        return "reference_images"
    return "image"


def choose_image_transport(args):
    if args.image_transport != "auto":
        return args.image_transport
    if args.mode in {"animate", "reference"}:
        return "data-url"
    return "path"


def image_to_data_url(image_path: Path):
    mime = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(image_path.read_bytes()).decode("ascii")


def normalize_image_value(image_path: Path, transport: str):
    if transport == "path":
        return str(image_path)
    if transport == "data-url":
        return image_to_data_url(image_path)
    raise SystemExit(f"unsupported image transport: {transport}")


def build_payload(args):
    prompt = args.prompt.strip()
    payload = {"model": args.model, "prompt": prompt}
    seconds = args.seconds if args.seconds is not None else normalize_seconds(args.duration)
    optional = {"size": args.size, "seconds": seconds, "fps": args.fps, "seed": args.seed}
    for key, value in optional.items():
        if value is not None:
            payload[key] = value

    image_meta = {"provided": False, "field": None, "transport": None, "path": None}
    if args.image:
        image_path = Path(args.image)
        if not image_path.exists():
            raise SystemExit(f"image not found: {image_path}")
        image_field = choose_image_field(args)
        image_transport = choose_image_transport(args)
        image_value = normalize_image_value(image_path, image_transport)
        if image_field == "reference_images":
            payload[image_field] = [image_value]
        else:
            payload[image_field] = image_value
        image_meta = {
            "provided": True,
            "field": image_field,
            "transport": image_transport,
            "path": str(image_path),
        }
    elif args.mode != "text":
        raise SystemExit(f"--mode {args.mode} requires --image")

    payload = merge_extra_json(payload, args.extra_json, args.extra_json_file)
    return payload, image_meta, prompt


def find_first_value(obj, keys):
    if isinstance(obj, dict):
        for key in keys:
            if key in obj and obj[key] not in (None, ""):
                return obj[key]
        for value in obj.values():
            found = find_first_value(value, keys)
            if found not in (None, ""):
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_first_value(item, keys)
            if found not in (None, ""):
                return found
    return None


def has_media_ref(obj):
    return find_first_value(obj, {"url", "path", "video_url", "result_url", "output_url", "b64_json"})


def extract_job_id(obj):
    for key in ("id", "job_id", "task_id", "request_id", "prediction_id"):
        found = find_first_value(obj, {key})
        if found:
            return found
    return None


def extract_status_url(obj):
    return find_first_value(obj, {"status_url", "poll_url", "result_url", "retrieve_url"})


def extract_status_text(obj):
    return find_first_value(obj, {"status", "state"})


def poll_until_ready(base_url, api_key, initial_payload, endpoint_template, interval, max_polls, timeout):
    payload = initial_payload
    if has_media_ref(payload):
        return payload
    status_url = extract_status_url(payload)
    job_id = extract_job_id(payload)
    if not status_url and job_id:
        status_url = base_url + endpoint_template.format(id=job_id)
    if not status_url:
        return payload
    if status_url.startswith("/"):
        status_url = base_url + status_url
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    last_payload = payload
    for _ in range(max_polls):
        try:
            resp = requests.get(status_url, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise SystemExit(request_exception_hint(e))
        text = resp.text
        try:
            polled = resp.json()
        except Exception:
            polled = {"raw": text}
        last_payload = polled
        if has_media_ref(polled):
            return polled
        status = str(extract_status_text(polled) or "").lower()
        if status in {"failed", "error", "cancelled", "canceled"}:
            return polled
        time.sleep(interval)
    return last_payload


def redact_request_for_summary(payload):
    def _redact(value):
        if isinstance(value, dict):
            redacted = {}
            for k, v in value.items():
                if k in {"image", "input_image", "first_frame_image"} and isinstance(v, str) and v.startswith("data:"):
                    redacted[k] = "data:..."
                elif k == "reference_images" and isinstance(v, list):
                    redacted[k] = ["data:..." if isinstance(item, str) and item.startswith("data:") else item for item in v]
                else:
                    redacted[k] = _redact(v)
            return redacted
        if isinstance(value, list):
            return [_redact(item) for item in value]
        return value

    return _redact(payload)


def main():
    args = parse_args()
    config_path = Path(args.config).expanduser()
    base_url, api_key, resolved_provider = load_provider(config_path, args.provider)
    url = base_url + args.endpoint
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    payload, image_meta, final_prompt = build_payload(args)
    if args.model == "video-model":
        print("WARN: using placeholder model 'video-model'. Pass --model or set the OPENCLAW_MEDIA_VIDEO_MODEL env var for a real provider model name.", file=sys.stderr)
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Accept": "application/json"},
            json=payload,
            timeout=args.timeout,
        )
    except requests.RequestException as e:
        raise SystemExit(request_exception_hint(e))

    raw_text = resp.text
    try:
        parsed = resp.json()
    except Exception:
        parsed = {"raw": raw_text}

    summary = {
        "status": resp.status_code,
        "ok": resp.ok,
        "model": args.model,
        "provider": resolved_provider,
        "endpoint": url,
        "mode": args.mode,
        "image": image_meta,
        "prompt": final_prompt,
        "request": redact_request_for_summary(payload),
        "response": parsed,
        "resolved": None,
        "downloaded": None,
        "hints": failure_hints(resp.status_code, args.endpoint, "video generation"),
    }

    if not resp.ok:
        if args.print_json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"STATUS: {resp.status_code}")
            print(raw_text)
            for hint in summary["hints"]:
                print(f"HINT: {hint}")
        raise SystemExit(1)

    resolved = poll_until_ready(base_url, api_key, parsed, args.status_endpoint_template, args.poll_interval, args.max_polls, args.timeout)
    summary["resolved"] = resolved
    status = str(extract_status_text(resolved) or "").lower()
    if status in {"failed", "error", "cancelled", "canceled"}:
        if args.print_json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(summary, ensure_ascii=False))
            print("HINT: the provider accepted the request but the async job finished in a failed state")
        raise SystemExit(1)

    if args.download:
        ref = has_media_ref(resolved)
        response_text = json.dumps(resolved, ensure_ascii=False)
        origin = base_url if isinstance(ref, str) and ref.startswith("/") else None
        if ref:
            downloaded = run_fetch_helper(Path(__file__).resolve().parent, response_text, args.out_dir, args.prefix, origin=origin, headers=DEFAULT_HEADERS)
            summary["downloaded"] = downloaded

    if args.print_json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"STATUS: {resp.status_code}")
        print(json.dumps(summary, ensure_ascii=False))
        if summary["downloaded"]:
            print(f"DOWNLOADED: {summary['downloaded']}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else str(e)
        print(f"ERROR: download helper failed: {stderr}", file=sys.stderr)
        raise
