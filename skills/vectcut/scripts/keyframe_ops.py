#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
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


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_payload(payload):
    if not isinstance(payload.get("draft_id"), str) or not payload.get("draft_id").strip():
        fail("draft_id is required")
    if "track_name" in payload and (not isinstance(payload.get("track_name"), str) or not payload.get("track_name").strip()):
        fail("track_name must be a non-empty string")

    has_batch = any(k in payload for k in ["property_types", "times", "values"])
    if has_batch:
        for k in ["property_types", "times", "values"]:
            if not isinstance(payload.get(k), list) or not payload.get(k):
                fail(f"{k} must be a non-empty array")
        if not (len(payload["property_types"]) == len(payload["times"]) == len(payload["values"])):
            fail("property_types/times/values length must be equal")
        for x in payload["property_types"]:
            if not isinstance(x, str) or not x.strip():
                fail("property_types must contain non-empty strings")
        for t in payload["times"]:
            if not is_number(t) or t < 0:
                fail("times must contain numbers >= 0")
        for v in payload["values"]:
            if not isinstance(v, (str, int, float)):
                fail("values must contain string or number")
        return

    if "property_type" in payload and (not isinstance(payload.get("property_type"), str) or not payload.get("property_type").strip()):
        fail("property_type must be a non-empty string")
    if "time" in payload and (not is_number(payload.get("time")) or payload.get("time") < 0):
        fail("time must be a number >= 0")
    if "value" in payload and not isinstance(payload.get("value"), (str, int, float)):
        fail("value must be string or number")


def request_post(payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    req = urllib.request.Request(
        url=f"{BASE_URL.rstrip('/')}/add_video_keyframe",
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
    if not output.get("draft_id") and not output.get("draft_url"):
        fail("Missing key field: output.draft_id or output.draft_url", {"response": data})
    if "added_keyframes_count" not in output:
        fail("Missing key field: output.added_keyframes_count", {"response": data})
    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <add_video_keyframe> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action != "add_video_keyframe":
        print(f"Usage: {sys.argv[0]} <add_video_keyframe> '<json_payload>'")
        sys.exit(1)

    has_batch = any(k in payload for k in ["property_types", "times", "values"])
    if not has_batch:
        payload.setdefault("property_type", "alpha")
        payload.setdefault("time", 0.0)
        payload.setdefault("value", "1.0")

    validate_payload(payload)
    request_post(payload)


if __name__ == "__main__":
    main()