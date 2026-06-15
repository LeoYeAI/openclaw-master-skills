#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
ALLOWED_MODELS = {"veo3.1", "veo3.1-pro", "seedance-1.5-pro", "grok-video-3", "sora2"}
SIZE_RE = re.compile(r"^\d+x\d+$")
MODEL_DURATION = {
    "grok-video-3": {6, 10, 15},
    "sora2": {10, 15},
    "seedance-1.5-pro": {4, 5, 6, 7, 8, 9, 10, 11, 12},
}


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


def request(method, url, payload=None):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    req = urllib.request.Request(url=url, data=body, method=method, headers=headers)
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
    return data


def validate_generate(payload):
    for key in ["prompt", "model", "resolution"]:
        if not isinstance(payload.get(key), str) or not payload.get(key).strip():
            fail(f"{key} is required")
    model = payload["model"]
    if model not in ALLOWED_MODELS:
        fail("model must be one of: veo3.1, veo3.1-pro, seedance-1.5-pro, grok-video-3, sora2")
    if not SIZE_RE.match(payload["resolution"]):
        fail("resolution must match format: <width>x<height>")
    if "reference_image" in payload:
        ref = payload["reference_image"]
        if isinstance(ref, str):
            if not ref.startswith(("http://", "https://")):
                fail("reference_image must start with http:// or https://")
        elif isinstance(ref, list):
            if not ref:
                fail("reference_image array cannot be empty")
            for u in ref:
                if not isinstance(u, str) or not u.startswith(("http://", "https://")):
                    fail("reference_image array must contain valid urls")
        else:
            fail("reference_image must be a string or array<string>")
    if "end_image" in payload:
        end_image = payload["end_image"]
        if not isinstance(end_image, str) or not end_image.startswith(("http://", "https://")):
            fail("end_image must start with http:// or https://")
        if model not in {"veo3.1", "veo3.1-pro", "seedance-1.5-pro"}:
            fail(f"model {model} does not support end_image")
    if "gen_duration" in payload:
        if not isinstance(payload["gen_duration"], int):
            fail("gen_duration must be an integer")
        allowed = MODEL_DURATION.get(model)
        if not allowed:
            fail(f"model {model} does not support gen_duration")
        if payload["gen_duration"] not in allowed:
            fail(f"gen_duration for {model} must be one of: {sorted(allowed)}")


def validate_status(payload):
    if not isinstance(payload.get("task_id"), str) or not payload.get("task_id").strip():
        fail("task_id is required")


def run_generate(payload):
    validate_generate(payload)
    data = request("POST", f"{BASE_URL.rstrip('/')}/generate_ai_video", payload)
    if isinstance(data, dict):
        task_id = data.get("task_id")
        if not task_id and isinstance(data.get("output"), dict):
            task_id = data["output"].get("task_id")
        if not task_id:
            fail("Missing key field: task_id", {"response": data})
    else:
        fail("JSON response must be an object", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def run_status(payload):
    validate_status(payload)
    qs = urllib.parse.urlencode({"task_id": payload["task_id"]})
    data = request("GET", f"{BASE_URL.rstrip('/')}/aivideo/task_status?{qs}")
    if not isinstance(data, dict):
        fail("JSON response must be an object", {"response": data})
    status = str(data.get("status", "")).lower()
    if status == "completed" and not data.get("video_url"):
        fail("Missing key field: video_url", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <generate_ai_video|ai_video_task_status> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action == "generate_ai_video":
        run_generate(payload)
        return
    if action == "ai_video_task_status":
        run_status(payload)
        return
    print(f"Usage: {sys.argv[0]} <generate_ai_video|ai_video_task_status> '<json_payload>'")
    sys.exit(1)


if __name__ == "__main__":
    main()
