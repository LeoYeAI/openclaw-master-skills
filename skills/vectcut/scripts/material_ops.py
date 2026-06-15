#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

CUT_BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
LLM_BASE_URL = os.getenv("VECTCUT_LLM_BASE_URL", "https://open.vectcut.com/llm")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

ACTION_ENDPOINT = {
    "get_duration": "get_duration",
    "get_resolution": "get_resolution",
    "video_detail": "video_detail",
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

def _clean_text(v):
    return v.strip().strip("`").strip() if isinstance(v, str) else v

def validate_payload(action, payload):
    raw_url = payload.get("video_url") if action == "video_detail" else payload.get("url")
    if raw_url is None:
        raw_url = payload.get("url") or payload.get("video_url")
    url = _clean_text(raw_url)
    if not isinstance(url, str) or not url:
        fail("url/video_url is required")
    if not (url.startswith("http://") or url.startswith("https://")):
        fail("url/video_url must start with http:// or https://")

    if action == "video_detail":
        payload["video_url"] = url
        payload.pop("url", None)
    else:
        payload["url"] = url
        payload.pop("video_url", None)

def parse_json_response(raw_text):
    try:
        return json.loads(raw_text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": raw_text})

def call_api(endpoint, payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")

    base_url = LLM_BASE_URL if endpoint == "video_detail" else CUT_BASE_URL
    url = f"{base_url.rstrip('/')}/{endpoint}"
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

    if endpoint == "get_duration":
        duration = output.get("duration") if isinstance(output, dict) else None
        if duration is None:
            fail("Missing key field: output.duration", {"response": data})
    if endpoint == "get_resolution":
        width = output.get("width") if isinstance(output, dict) else None
        height = output.get("height") if isinstance(output, dict) else None
        if width is None or height is None:
            fail("Missing key field: output.width/output.height", {"response": data})
    if endpoint == "video_detail":
        if not isinstance(output, dict):
            fail("Missing key field: output", {"response": data})
        if output.get("vlm_result") is None and output.get("video_detail") is None and data.get("result") is None:
            fail("Missing key field: output.vlm_result/video_detail/result", {"response": data})

    print(json.dumps(data, ensure_ascii=False))

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <get_duration|get_resolution|video_detail> '<json_payload>'")
        sys.exit(1)

    action = sys.argv[1]
    raw_payload = sys.argv[2]
    endpoint = ACTION_ENDPOINT.get(action)
    if not endpoint:
        print(f"Usage: {sys.argv[0]} <get_duration|get_resolution|video_detail> '<json_payload>'")
        sys.exit(1)

    payload = parse_payload(raw_payload)
    validate_payload(action, payload)
    call_api(endpoint, payload)

if __name__ == "__main__":
    main()