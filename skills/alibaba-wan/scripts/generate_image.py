#!/usr/bin/env python3
"""
Atlas Cloud & Google AI Studio - Image Generation & Editing Script
Supports text-to-image, image editing, and local file upload.
Two providers: Atlas Cloud (async, polling) and Google AI Studio (synchronous, base64).
Zero external dependencies - uses only Python standard library.

Network calls:
  Atlas Cloud provider (api.atlascloud.ai):
    - GET  /api/v1/models              — validate model ID (no auth required)
    - POST /api/v1/model/generateImage — submit image generation request
    - GET  /api/v1/model/prediction/*  — poll for generation result
    - POST /api/v1/model/uploadMedia   — upload local file (only via "upload" command)
  Google AI Studio provider (generativelanguage.googleapis.com):
    - POST /v1beta/models/*/generateContent — synchronous image generation

Credentials (read from environment variables only, never hardcoded):
  - ATLASCLOUD_API_KEY: required for Atlas Cloud provider
  - GEMINI_API_KEY: required for Google AI Studio provider

Usage:
  # Atlas Cloud — text-to-image
  python generate_image.py generate --model "alibaba/wan-2.6/text-to-image" --prompt "Sunset"

  # Atlas Cloud — image editing
  python generate_image.py generate --model "google/nano-banana-2/edit" --prompt "Change sky" --images "https://..."

  # Google AI Studio — text-to-image
  python generate_image.py generate --provider google --prompt "Sunset" aspect_ratio=16:9 image_size=2K

  # Google AI Studio — image editing (with local file)
  python generate_image.py generate --provider google --prompt "Change sky" --image ./photo.png

  # Upload local file to Atlas Cloud (for editing)
  python generate_image.py upload ./photo.jpg

  # List available Atlas Cloud models
  python generate_image.py list-models
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.atlascloud.ai/api/v1"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-3.1-flash-image-preview"
UA = "AtlasCloud-Skill/1.0"


# ---------------------------------------------------------------------------
# Provider detection
# ---------------------------------------------------------------------------

def detect_provider():
    """Auto-detect provider based on available API keys."""
    has_atlas = bool(os.environ.get("ATLASCLOUD_API_KEY"))
    has_gemini = bool(os.environ.get("GEMINI_API_KEY"))
    if has_atlas and has_gemini:
        print("Note: Both API keys found. Defaulting to Atlas Cloud. Use --provider google to switch.")
        return "atlas"
    if has_atlas:
        return "atlas"
    if has_gemini:
        return "google"
    print("Error: No API key found. Set ATLASCLOUD_API_KEY or GEMINI_API_KEY.", file=sys.stderr)
    print("  Atlas Cloud: https://www.atlascloud.ai", file=sys.stderr)
    print("  Google AI Studio: https://aistudio.google.com/apikey", file=sys.stderr)
    sys.exit(1)


def get_atlas_key():
    key = os.environ.get("ATLASCLOUD_API_KEY")
    if not key:
        print("Error: ATLASCLOUD_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your API key at: https://www.atlascloud.ai", file=sys.stderr)
        sys.exit(1)
    return key


def get_gemini_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your API key at: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)
    return key


# ---------------------------------------------------------------------------
# Atlas Cloud implementation
# ---------------------------------------------------------------------------

def atlas_api_request(method, endpoint, data=None):
    url = f"{API_BASE}{endpoint}"
    headers = {"Authorization": f"Bearer {get_atlas_key()}", "User-Agent": UA}
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
    try:
        url = f"{API_BASE}/models"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = data.get("data", [])
        for m in models:
            if m.get("model") == model_id:
                return True
        print(f"Error: Model '{model_id}' not found on Atlas Cloud.", file=sys.stderr)
        keyword = model_id.split("/")[0] if "/" in model_id else model_id
        similar = [m["model"] for m in models if keyword.lower() in m.get("model", "").lower()]
        if similar:
            print("Similar models:", file=sys.stderr)
            for s in similar[:10]:
                print(f"  - {s}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Warning: Could not validate model (will try anyway): {e}", file=sys.stderr)
        return True


def list_models(model_type=None):
    try:
        url = f"{API_BASE}/models"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = data.get("data", [])
        if model_type:
            models = [m for m in models if m.get("type", "").lower() == model_type.lower()]
        print(f"Available {'image ' if model_type else ''}models ({len(models)}):\n")
        for m in models:
            price = m.get("price", {}).get("actual", {}).get("base_price", "N/A")
            print(f"  {m.get('model', 'unknown'):50s}  ${price}")
    except Exception as e:
        print(f"Error listing models: {e}", file=sys.stderr)
        sys.exit(1)


def atlas_submit(model_id, params):
    validate_model(model_id)
    payload = {"model": model_id, **params}
    print(f"Submitting image generation (Atlas Cloud): {model_id}")
    result = atlas_api_request("POST", "/model/generateImage", data=payload)
    prediction_id = result.get("data", {}).get("id")
    if not prediction_id:
        print(f"Error: No prediction ID: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)
    print(f"Prediction ID: {prediction_id}")
    return prediction_id


def atlas_poll(prediction_id, timeout=120, interval=3):
    endpoint = f"/model/prediction/{prediction_id}"
    start = time.time()
    while True:
        elapsed = int(time.time() - start)
        if elapsed >= timeout:
            print(f"Error: Timeout after {timeout}s.", file=sys.stderr)
            sys.exit(1)
        result = atlas_api_request("GET", endpoint)
        data = result.get("data", {})
        status = data.get("status", "unknown")
        if status in ("completed", "succeeded"):
            print(f"Completed in {elapsed}s")
            return data.get("outputs", [])
        if status == "failed":
            print(f"Generation failed: {data.get('error', 'Unknown')}", file=sys.stderr)
            sys.exit(1)
        print(f"  {status}... ({elapsed}s)")
        time.sleep(interval)


def atlas_generate(model_id, params, output_dir, timeout):
    get_atlas_key()
    prediction_id = atlas_submit(model_id, params)
    outputs = atlas_poll(prediction_id, timeout)
    if not outputs:
        print("Warning: No output files returned.", file=sys.stderr)
        return []
    saved = []
    for url in outputs:
        saved.append(download_file(url, output_dir))
    return saved


# ---------------------------------------------------------------------------
# Google AI Studio implementation
# ---------------------------------------------------------------------------

def gemini_generate(prompt, params, output_dir, image_path=None):
    get_gemini_key()
    print(f"Submitting image generation (Google AI Studio): {GEMINI_MODEL}")

    # Build content parts
    parts = []
    if prompt:
        parts.append({"text": prompt})

    # If editing with a local image file
    if image_path:
        if image_path.startswith(("http://", "https://")):
            print("Error: Google AI Studio requires local file for editing, not URL.", file=sys.stderr)
            print("Use --provider atlas for URL-based editing.", file=sys.stderr)
            sys.exit(1)
        if not os.path.exists(image_path):
            print(f"Error: File not found: {image_path}", file=sys.stderr)
            sys.exit(1)
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime = mime_map.get(ext, "image/png")
        parts.append({"inline_data": {"mime_type": mime, "data": img_b64}})

    # Build image config
    image_config = {}
    if "aspect_ratio" in params:
        image_config["aspectRatio"] = params.pop("aspect_ratio")
    if "image_size" in params:
        image_config["imageSize"] = params.pop("image_size")

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
        },
    }
    if image_config:
        payload["generationConfig"]["imageConfig"] = image_config

    url = f"{GEMINI_API_BASE}/models/{GEMINI_MODEL}:generateContent"
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "x-goog-api-key": get_gemini_key(),
        "Content-Type": "application/json",
        "User-Agent": UA,
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"Google API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    # Parse response — extract base64 images
    saved = []
    candidates = result.get("candidates", [])
    if not candidates:
        print("Error: No candidates in response.", file=sys.stderr)
        sys.exit(1)

    content_parts = candidates[0].get("content", {}).get("parts", [])
    img_count = 0
    for part in content_parts:
        if "text" in part:
            print(f"Model response: {part['text']}")
        elif "inline_data" in part:
            img_count += 1
            mime = part["inline_data"].get("mime_type", "image/png")
            ext = ".png" if "png" in mime else ".jpg" if "jpeg" in mime else ".webp" if "webp" in mime else ".png"
            filename = f"gemini_output_{int(time.time())}_{img_count}{ext}"
            output_path = os.path.join(output_dir, filename)

            img_data = base64.b64decode(part["inline_data"]["data"])
            with open(output_path, "wb") as f:
                f.write(img_data)
            size_kb = len(img_data) / 1024
            print(f"Saved: {output_path} ({size_kb:.1f} KB)")
            saved.append(output_path)

    if not saved:
        print("Warning: No images in response.", file=sys.stderr)
    return saved


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def download_file(url, output_dir="."):
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename or "." not in filename:
        filename = f"output_{int(time.time())}.png"
    output_path = os.path.join(output_dir, filename)
    base, ext = os.path.splitext(output_path)
    counter = 1
    while os.path.exists(output_path):
        output_path = f"{base}_{counter}{ext}"
        counter += 1
    print(f"Downloading: {filename}")
    urllib.request.urlretrieve(url, output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Saved: {output_path} ({size_kb:.1f} KB)")
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
        "Authorization": f"Bearer {get_atlas_key()}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": UA,
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
        print(f"Error: No download URL: {json.dumps(result, indent=2)}", file=sys.stderr)
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Image Generation & Editing (Atlas Cloud + Google AI Studio)",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-models", help="List available Atlas Cloud image models")

    gen = subparsers.add_parser("generate", help="Generate or edit an image")
    gen.add_argument("--provider", choices=["atlas", "google"], help="Provider (auto-detect if omitted)")
    gen.add_argument("--model", "-m", help="Atlas Cloud model ID (required for atlas provider)")
    gen.add_argument("--prompt", "-p", help="Text prompt")
    gen.add_argument("--negative-prompt", help="Negative prompt (atlas only)")
    gen.add_argument("--image", help="Input image: URL for atlas, local path for google")
    gen.add_argument("--images", help="Comma-separated image URLs (atlas only)")
    gen.add_argument("--output", "-o", default=".", help="Output directory (default: current dir)")
    gen.add_argument("--timeout", default=120, type=int, help="Polling timeout in seconds (default: 120)")
    gen.add_argument("extra", nargs="*", help="Extra params as key=value (e.g. aspect_ratio=16:9)")

    up = subparsers.add_parser("upload", help="Upload a local image to Atlas Cloud")
    up.add_argument("file", help="Path to local image file")
    up.add_argument("--yes", "-y", action="store_true", help="Skip upload confirmation prompt")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list-models":
        list_models("Image")
        return

    if args.command == "upload":
        get_atlas_key()
        upload_file(args.file, skip_confirm=args.yes)
        return

    # --- generate ---
    provider = args.provider or detect_provider()

    # Parse extra key=value params
    extra_params = {}
    for item in args.extra:
        if "=" not in item:
            print(f"Warning: Ignoring '{item}' (expected key=value)", file=sys.stderr)
            continue
        key, value = item.split("=", 1)
        extra_params[key] = parse_value(value)

    os.makedirs(args.output, exist_ok=True)

    if provider == "google":
        saved = gemini_generate(args.prompt, extra_params, args.output, image_path=args.image)
    else:
        if not args.model:
            print("Error: --model is required for Atlas Cloud provider.", file=sys.stderr)
            sys.exit(1)
        params = {}
        if args.prompt:
            params["prompt"] = args.prompt
        if args.negative_prompt:
            params["negative_prompt"] = args.negative_prompt
        if args.image:
            params["images"] = [args.image]
        if args.images:
            params["images"] = [u.strip() for u in args.images.split(",")]
        params.update(extra_params)
        saved = atlas_generate(args.model, params, args.output, args.timeout)

    if saved:
        print(f"\nDone! {len(saved)} image(s) saved.")


if __name__ == "__main__":
    main()
