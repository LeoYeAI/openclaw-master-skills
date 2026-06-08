#!/usr/bin/env python3
"""
Atlas Cloud API - Video Generation Script
Supports text-to-video, image-to-video, video-to-video, and local file upload.
Zero external dependencies - uses only Python standard library.

Network calls (all to api.atlascloud.ai):
  - GET  /api/v1/models              — validate model ID before submission (no auth required)
  - POST /api/v1/model/generateVideo — submit video generation request
  - GET  /api/v1/model/prediction/*  — poll for generation result
  - POST /api/v1/model/uploadMedia   — upload local file (only when user runs "upload" command)

Credentials:
  - Reads ATLASCLOUD_API_KEY from environment variable only, never hardcoded.
  - Key is sent via Authorization header over HTTPS.

Usage:
  # Text-to-video
  python generate_video.py generate --model "alibaba/wan-2.6/text-to-video" --prompt "A cat playing" duration=5

  # Image-to-video
  python generate_video.py generate --model "alibaba/wan-2.6/image-to-video" --image "https://example.com/photo.jpg" --prompt "Animate" resolution=1080p

  # Video-to-video
  python generate_video.py generate --model "alibaba/wan-2.6/video-to-video" --video "https://example.com/clip.mp4" --prompt "Transform character1 into anime"

  # Upload local file first, then use
  python generate_video.py upload ./photo.jpg
  python generate_video.py generate --model "alibaba/wan-2.6/image-to-video" --image "https://...uploaded-url..." --prompt "Animate"
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.atlascloud.ai/api/v1"


def get_api_key():
    key = os.environ.get("ATLASCLOUD_API_KEY")
    if not key:
        print("Error: ATLASCLOUD_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your API key at: https://www.atlascloud.ai", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(method, endpoint, data=None):
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "User-Agent": "AtlasCloud-Skill/1.0",
    }

    body = None
    if data is not None and method == "POST":
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def validate_model(model_id):
    """Check if model exists on Atlas Cloud. Prints available alternatives if not found."""
    try:
        url = f"{API_BASE}/models"
        req = urllib.request.Request(url, headers={"User-Agent": "AtlasCloud-Skill/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = data.get("data", [])
        for m in models:
            if m.get("model") == model_id:
                return True
        # Model not found — show similar models
        print(f"Error: Model '{model_id}' not found on Atlas Cloud.", file=sys.stderr)
        keyword = model_id.split("/")[0] if "/" in model_id else model_id
        similar = [m["model"] for m in models if keyword.lower() in m.get("model", "").lower()]
        if similar:
            print(f"Similar models:", file=sys.stderr)
            for s in similar[:10]:
                print(f"  - {s}", file=sys.stderr)
        else:
            print("Use --list-models to see all available models.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # If validation fails (network issue etc.), proceed anyway
        print(f"Warning: Could not validate model (will try anyway): {e}", file=sys.stderr)
        return True


def list_models(model_type=None):
    """List available models, optionally filtered by type."""
    try:
        url = f"{API_BASE}/models"
        req = urllib.request.Request(url, headers={"User-Agent": "AtlasCloud-Skill/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = data.get("data", [])
        if model_type:
            models = [m for m in models if m.get("type", "").lower() == model_type.lower()]
        print(f"Available {'video ' if model_type else ''}models ({len(models)}):\n")
        for m in models:
            price = m.get("price", {}).get("actual", {}).get("base_price", "N/A")
            print(f"  {m.get('model', 'unknown'):50s}  ${price}")
    except Exception as e:
        print(f"Error listing models: {e}", file=sys.stderr)
        sys.exit(1)


def submit(model_id, params):
    validate_model(model_id)
    payload = {"model": model_id, **params}
    print(f"Submitting video generation: {model_id}")
    result = api_request("POST", "/model/generateVideo", data=payload)

    prediction_id = result.get("data", {}).get("id")
    if not prediction_id:
        print(f"Error: No prediction ID in response: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    print(f"Prediction ID: {prediction_id}")
    return prediction_id


def poll(prediction_id, timeout=300, interval=5):
    endpoint = f"/model/prediction/{prediction_id}"
    start = time.time()

    while True:
        elapsed = int(time.time() - start)
        if elapsed >= timeout:
            print(f"Error: Timeout after {timeout}s. Prediction ID: {prediction_id}", file=sys.stderr)
            sys.exit(1)

        result = api_request("GET", endpoint)
        data = result.get("data", {})
        status = data.get("status", "unknown")

        if status in ("completed", "succeeded"):
            outputs = data.get("outputs", [])
            print(f"Completed in {elapsed}s")
            return outputs

        if status == "failed":
            error = data.get("error", "Unknown error")
            print(f"Generation failed: {error}", file=sys.stderr)
            sys.exit(1)

        print(f"  {status}... ({elapsed}s)")
        time.sleep(interval)


def download(url, output_dir="."):
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename or "." not in filename:
        filename = f"output_{int(time.time())}.mp4"

    output_path = os.path.join(output_dir, filename)
    base, ext = os.path.splitext(output_path)
    counter = 1
    while os.path.exists(output_path):
        output_path = f"{base}_{counter}{ext}"
        counter += 1

    print(f"Downloading: {filename}")
    urllib.request.urlretrieve(url, output_path)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Saved: {output_path} ({size_mb:.2f} MB)")
    return output_path


def upload_file(file_path, skip_confirm=False):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    if not skip_confirm:
        size_kb = os.path.getsize(file_path) / 1024
        print(f"About to upload '{file_path}' ({size_kb:.1f} KB) to Atlas Cloud (api.atlascloud.ai).")
        confirm = input("Proceed? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Upload cancelled.")
            sys.exit(0)
    url = f"{API_BASE}/model/uploadMedia"
    filename = os.path.basename(file_path)
    boundary = f"----AtlasCloudBoundary{int(time.time() * 1000)}"

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: application/octet-stream\r\n\r\n"
    body += file_data
    body += f"\r\n--{boundary}--\r\n".encode()

    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "AtlasCloud-Skill/1.0",
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"Upload Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)

    download_url = result.get("data", {}).get("download_url")
    if not download_url:
        print(f"Error: No download URL in response: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    print(f"Uploaded: {filename}")
    print(f"URL: {download_url}")
    return download_url


def parse_value(value):
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.startswith(("[", "{")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    return value


def main():
    parser = argparse.ArgumentParser(description="Atlas Cloud - Video Generation")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-models", help="List available video models")

    gen = subparsers.add_parser("generate", help="Generate a video")
    gen.add_argument("--model", "-m", required=True, help="Model ID (e.g. alibaba/wan-2.6/text-to-video)")
    gen.add_argument("--prompt", "-p", help="Text prompt")
    gen.add_argument("--negative-prompt", help="Negative prompt")
    gen.add_argument("--image", help="Input image URL (for image-to-video)")
    gen.add_argument("--video", help="Input video URL (for video-to-video)")
    gen.add_argument("--videos", help="Comma-separated video URLs")
    gen.add_argument("--audio", help="Audio URL (for audio-guided generation)")
    gen.add_argument("--output", "-o", default=".", help="Output directory (default: current dir)")
    gen.add_argument("--timeout", default=300, type=int, help="Polling timeout in seconds (default: 300)")
    gen.add_argument("extra", nargs="*", help="Extra model params as key=value (e.g. duration=5 resolution=1080p)")

    up = subparsers.add_parser("upload", help="Upload a local file to Atlas Cloud")
    up.add_argument("file", help="Path to local file")
    up.add_argument("--yes", "-y", action="store_true", help="Skip upload confirmation prompt")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list-models":
        list_models("Video")
        return

    # Pre-check API key
    get_api_key()

    if args.command == "upload":
        upload_file(args.file, skip_confirm=args.yes)
        return

    params = {}
    if args.prompt:
        params["prompt"] = args.prompt
    if args.negative_prompt:
        params["negative_prompt"] = args.negative_prompt
    if args.image:
        params["image"] = args.image
    if args.video:
        params["videos"] = [args.video]
    if args.videos:
        params["videos"] = [u.strip() for u in args.videos.split(",")]
    if args.audio:
        params["audio"] = args.audio

    for item in args.extra:
        if "=" not in item:
            print(f"Warning: Ignoring '{item}' (expected key=value)", file=sys.stderr)
            continue
        key, value = item.split("=", 1)
        params[key] = parse_value(value)

    os.makedirs(args.output, exist_ok=True)

    prediction_id = submit(args.model, params)
    outputs = poll(prediction_id, args.timeout)

    if not outputs:
        print("Warning: No output files returned.", file=sys.stderr)
        return

    saved = []
    for url in outputs:
        saved.append(download(url, args.output))

    print(f"\nDone! {len(saved)} video(s) saved.")


if __name__ == "__main__":
    main()
