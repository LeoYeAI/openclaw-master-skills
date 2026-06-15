#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

ACTION_ENDPOINT = {
    "create": "create_draft",
    "modify": "modify_draft",
    "remove": "remove_draft",
    "query": "query_script",
}

def fail(error, output=None):
    data = {"success": False, "error": error, "output": output if output is not None else ""}
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)

def parse_payload(raw):
    try:
        data = json.loads(raw)
    except Exception as e:
        fail("Invalid JSON payload", {"payload": raw, "exception": str(e)})
    if not isinstance(data, dict):
        fail("Payload must be a JSON object", {"payload": data})
    return data

def validate_payload(action, payload):
    draft_id = payload.get("draft_id")
    if action in {"modify", "remove", "query"}:
        if not isinstance(draft_id, str) or not draft_id.strip():
            fail("draft_id is required")

    if action == "modify":
        name = payload.get("name")
        cover = payload.get("cover")
        has_name = isinstance(name, str) and name.strip()
        has_cover = isinstance(cover, str) and cover.strip()
        if not has_name and not has_cover:
            fail("modify requires at least one of name or cover")

def parse_json_response(raw_text):
    try:
        return json.loads(raw_text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": raw_text})

def call_api(endpoint, payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")

    url = f"{BASE_URL.rstrip('/')}/{endpoint}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        fail(f"HTTP error: {e.code}", {"raw_response": text})
    except urllib.error.URLError as e:
        fail("Network error", {"reason": str(e.reason)})
    except Exception as e:
        fail("Request failed", {"exception": str(e)})

    if status < 200 or status >= 300:
        fail(f"HTTP non-2xx: {status}", {"raw_response": text})

    data = parse_json_response(text)
    if not isinstance(data, dict):
        fail("JSON response must be an object", {"response": data})

    success = data.get("success")
    error_msg = data.get("error")
    output = data.get("output")

    if success is False or (isinstance(error_msg, str) and error_msg.strip()):
        fail(error_msg if error_msg else "Business error", output if output is not None else "")

    if endpoint in {"create_draft", "modify_draft"}:
        draft_id = output.get("draft_id") if isinstance(output, dict) else None
        if draft_id is None:
            fail("Missing key field: output.draft_id", {"response": data})

    if endpoint == "query_script":
        if output is None or (isinstance(output, str) and not output.strip()):
            fail("Missing key field: output", {"response": data})

    print(json.dumps(data, ensure_ascii=False))

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <create|modify|remove|query> '<json_payload>'")
        sys.exit(1)

    action = sys.argv[1]
    raw_payload = sys.argv[2]
    endpoint = ACTION_ENDPOINT.get(action)
    if not endpoint:
        print(f"Usage: {sys.argv[0]} <create|modify|remove|query> '<json_payload>'")
        sys.exit(1)

    payload = parse_payload(raw_payload)
    validate_payload(action, payload)
    call_api(endpoint, payload)

if __name__ == "__main__":
    main()