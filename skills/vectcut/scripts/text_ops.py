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


def validate_time_payload(payload):
    if not isinstance(payload.get("text"), str) or not payload.get("text").strip():
        fail("text is required")
    if not isinstance(payload.get("start"), (int, float)) or not isinstance(payload.get("end"), (int, float)):
        fail("start and end must be numbers")
    if payload.get("end") <= payload.get("start"):
        fail("invalid range: require end > start")


def validate_add_payload(payload):
    for k in ["text", "start", "end"]:
        if k not in payload:
            fail(f"{k} is required")
    validate_time_payload(payload)


def validate_modify_payload(payload):
    for k in ["draft_id", "material_id", "text", "start", "end"]:
        if not payload.get(k):
            fail(f"{k} is required")
    validate_time_payload(payload)


def validate_remove_payload(payload):
    for k in ["draft_id", "material_id"]:
        if not payload.get(k):
            fail(f"{k} is required")


def request_post(endpoint, payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")
    req = urllib.request.Request(
        url=f"{BASE_URL.rstrip('/')}/{endpoint}",
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
    if endpoint == "add_text":
        if not output.get("material_id"):
            fail("Missing key field: output.material_id", {"response": data})
    else:
        if not output.get("draft_id") and not output.get("draft_url"):
            fail("Missing key field: output.draft_id or output.draft_url", {"response": data})

    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <add_text|modify_text|remove_text> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])

    if action == "add_text":
        validate_add_payload(payload)
        request_post("add_text", payload)
        return
    if action == "modify_text":
        validate_modify_payload(payload)
        request_post("modify_text", payload)
        return
    if action == "remove_text":
        validate_remove_payload(payload)
        request_post("remove_text", payload)
        return

    print(f"Usage: {sys.argv[0]} <add_text|modify_text|remove_text> '<json_payload>'")
    sys.exit(1)


if __name__ == "__main__":
    main()