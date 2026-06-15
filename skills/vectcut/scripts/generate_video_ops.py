#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

ACTION_ENDPOINT = {
    "generate_video": "generate_video",
    "task_status": "task_status",
    "render_wait": "generate_video",
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

def parse_json_response(text):
    try:
        return json.loads(text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": text})

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
    if data.get("success") is False or (isinstance(data.get("error"), str) and data.get("error").strip()):
        fail(data.get("error") or "Business error", data.get("output") if data.get("output") is not None else data)
    return data

def ensure_generate_payload(payload):
    draft_id = payload.get("draft_id")
    if not isinstance(draft_id, str) or not draft_id.strip():
        fail("draft_id is required")
    if "resolution" in payload and not isinstance(payload.get("resolution"), str):
        fail("resolution must be a string")
    if "framerate" in payload and not isinstance(payload.get("framerate"), str):
        fail("framerate must be a string")

def ensure_status_payload(payload):
    task_id = payload.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        fail("task_id is required")

def call_generate(payload):
    ensure_generate_payload(payload)
    data = request_post("generate_video", {k: v for k, v in payload.items() if k in {"draft_id", "resolution", "framerate"}})
    output = data.get("output")
    task_id = output.get("task_id") if isinstance(output, dict) else None
    if not task_id:
        fail("Missing key field: output.task_id", {"response": data})
    return data

def call_status(payload):
    ensure_status_payload(payload)
    data = request_post("task_status", {"task_id": payload.get("task_id")})
    output = data.get("output")
    status = output.get("status") if isinstance(output, dict) else None
    if not status:
        fail("Missing key field: output.status", {"response": data})
    return data

def call_render_wait(payload):
    task_id = payload.get("task_id")
    if isinstance(task_id, str) and task_id.strip():
        task_id = task_id.strip()
    else:
        generate_res = call_generate(payload)
        task_id = (generate_res.get("output") or {}).get("task_id")

    max_poll = int(payload.get("max_poll", 30))
    poll_interval = float(payload.get("poll_interval", 2))
    last = None
    for _ in range(max_poll):
        status_res = call_status({"task_id": task_id})
        last = status_res
        output = status_res.get("output") or {}
        status = output.get("status")
        if status == "SUCCESS":
            if not output.get("result"):
                fail("Missing key field: output.result", {"response": status_res})
            print(json.dumps(status_res, ensure_ascii=False))
            return
        if status in {"FAILURE", "FAILED"} or output.get("success") is False:
            fail("Render failed", {"task_id": task_id, "response": status_res})
        time.sleep(poll_interval)
    fail("Render polling timeout", {"task_id": task_id, "last_status": last})

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <generate_video|task_status|render_wait> '<json_payload>'")
        sys.exit(1)
    action = sys.argv[1]
    payload = parse_payload(sys.argv[2])
    if action not in ACTION_ENDPOINT:
        print(f"Usage: {sys.argv[0]} <generate_video|task_status|render_wait> '<json_payload>'")
        sys.exit(1)
    if action == "generate_video":
        print(json.dumps(call_generate(payload), ensure_ascii=False))
        return
    if action == "task_status":
        print(json.dumps(call_status(payload), ensure_ascii=False))
        return
    call_render_wait(payload)

if __name__ == "__main__":
    main()