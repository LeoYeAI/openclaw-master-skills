#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")


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
    req = urllib.request.Request(
        url=url,
        data=body,
        method=method,
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
    return data


def validate_create(payload):
    for key in ["audio_url", "video_url"]:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(f"{key} is required")
        if not value.startswith(("http://", "https://")):
            fail(f"{key} must start with http:// or https://")


def validate_status(payload):
    task_id = payload.get("task_id")
    if task_id is not None and (not isinstance(task_id, str) or not task_id.strip()):
        fail("task_id must be a non-empty string")


def extract_task_id(data):
    if not isinstance(data, dict):
        return ""
    task_id = data.get("task_id") or data.get("id")
    if isinstance(task_id, str) and task_id.strip():
        return task_id
    output = data.get("output")
    if isinstance(output, dict):
        nested = output.get("task_id") or output.get("id")
        if isinstance(nested, str) and nested.strip():
            return nested
    return ""


def run_create(payload):
    validate_create(payload)
    body = {k: v for k, v in payload.items() if k in {"audio_url", "video_url", "license_key"}}
    data = request("POST", f"{BASE_URL.rstrip('/')}/digital_human/create", body)
    if not extract_task_id(data):
        fail("Missing key field: task_id or id", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def run_status(payload):
    validate_status(payload)
    query = {}
    if payload.get("task_id"):
        query["task_id"] = payload["task_id"]
    url = f"{BASE_URL.rstrip('/')}/digital_human/task_status"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"
    data = request("GET", url)
    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <create_digital_human|digital_human_task_status> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action == "create_digital_human":
        run_create(payload)
        return
    if action == "digital_human_task_status":
        run_status(payload)
        return
    print(f"Usage: {sys.argv[0]} <create_digital_human|digital_human_task_status> '<json_payload>'")
    sys.exit(1)


if __name__ == "__main__":
    main()
