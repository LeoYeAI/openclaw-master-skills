#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("VECTCUT_PROCESS_BASE_URL", "https://open.vectcut.com/process")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
ACTION_ENDPOINT = {"extract_audio": "extract_audio", "split_video": "split_video"}


def fail(error, output=None):
    print(
        json.dumps(
            {
                "success": False,
                "error": error,
                "output": output if output is not None else "",
            },
            ensure_ascii=False,
        )
    )
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
    video_url = payload.get("video_url")
    if not isinstance(video_url, str) or not video_url.strip():
        fail("video_url is required")
    if not (video_url.startswith("http://") or video_url.startswith("https://")):
        fail("video_url must start with http:// or https://")

    if action == "split_video":
        start = payload.get("start")
        end = payload.get("end")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            fail("start and end are required")
        if start < 0 or end <= start:
            fail("invalid range: require 0 <= start < end")


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

    if status < 200 or status >= 300:
        fail(f"HTTP non-2xx: {status}", {"raw_response": text})

    data = parse_json_response(text)
    if not isinstance(data, dict):
        fail("JSON response must be an object", {"response": data})
    if data.get("code") != 200:
        fail(data.get("message") or "Business error", data)

    out = data.get("data")
    if not isinstance(out, dict) or not out.get("public_url"):
        fail("Missing key field: data.public_url", {"response": data})

    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <extract_audio|split_video> '<json_payload>'")
        sys.exit(1)

    action = sys.argv[1]
    endpoint = ACTION_ENDPOINT.get(action)
    if not endpoint:
        print(f"Usage: {sys.argv[0]} <extract_audio|split_video> '<json_payload>'")
        sys.exit(1)

    payload = parse_payload(sys.argv[2])
    validate_payload(action, payload)

    req = {"video_url": payload["video_url"]}
    if action == "split_video":
        req["start"] = payload["start"]
        req["end"] = payload["end"]

    request_post(endpoint, req)


if __name__ == "__main__":
    main()