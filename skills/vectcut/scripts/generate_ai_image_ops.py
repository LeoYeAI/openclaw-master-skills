#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
ALLOWED_MODELS = {"nano_banana", "nano_banana_2", "nano_banana_pro", "jimeng-4.5"}
SIZE_RE = re.compile(r"^\d+x\d+$")


def fail(error, output=None):
    print(json.dumps({"success": False, "error": error, "output": output if output is not None else ""}, ensure_ascii=False))
    sys.exit(0)


def parse_payload(raw):
    try:
        data = json.loads(raw)
    except Exception as e:
        fail("Invalid JSON payload", {"payload": raw, "exception": str(e)})
    if not isinstance(data, dict):
        fail("Payload must be a JSON object", {"payload": data})
    return data


def validate_payload(payload):
    prompt = payload.get("prompt")
    model = payload.get("model")
    if not isinstance(prompt, str) or not prompt.strip():
        fail("prompt is required")
    if not isinstance(model, str) or model not in ALLOWED_MODELS:
        fail("model must be one of: nano_banana, nano_banana_2, nano_banana_pro, jimeng-4.5")
    if "size" in payload:
        size = payload.get("size")
        if not isinstance(size, str) or not SIZE_RE.match(size):
            fail("size must match format: <width>x<height>")
    if "reference_image" in payload:
        ref = payload.get("reference_image")
        if not isinstance(ref, str) or not (ref.startswith("http://") or ref.startswith("https://")):
            fail("reference_image must start with http:// or https://")
    for key in ["start", "end", "transform_x", "transform_y", "scale_x", "scale_y"]:
        if key in payload and not isinstance(payload.get(key), (int, float)):
            fail(f"{key} must be a number")
    if "start" in payload and "end" in payload and payload["end"] <= payload["start"]:
        fail("invalid range: require end > start")


def request_post(payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    req = urllib.request.Request(
        url=f"{BASE_URL.rstrip('/')}/generate_image",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        fail(f"HTTP error: {e.code}", {"raw_response": e.read().decode("utf-8", errors="replace")})
    except urllib.error.URLError as e:
        fail("Network error", {"reason": str(e.reason)})

    if status < 200 or status >= 300:
        fail(f"HTTP non-2xx: {status}", {"raw_response": text})

    try:
        data = json.loads(text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": text})

    if data.get("success") is False or (isinstance(data.get("error"), str) and data.get("error").strip()):
        fail(data.get("error") or "Business error", data.get("output") if data.get("output") is not None else data)

    output = data.get("output") if isinstance(data.get("output"), dict) else {}
    if not output.get("image_url"):
        fail("Missing key field: output.image_url", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <generate_ai_image> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action != "generate_ai_image":
        print(f"Usage: {sys.argv[0]} <generate_ai_image> '<json_payload>'")
        sys.exit(1)
    validate_payload(payload)
    request_post(payload)


if __name__ == "__main__":
    main()