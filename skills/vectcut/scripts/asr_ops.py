#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/llm")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

ACTION_ENDPOINT = {
    "asr_basic": "asr_basic",
    "asr_nlp": "asr_nlp",
    "asr_llm": "asr_llm",
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

def validate_payload(payload):
    url = payload.get("url")
    if not isinstance(url, str) or not url.strip():
        fail("url is required")
    if not (url.startswith("http://") or url.startswith("https://")):
        fail("url must start with http:// or https://")

    content = payload.get("content")
    if content is not None and not isinstance(content, str):
        fail("content must be a string")
    if isinstance(content, str):
        payload["content"] = content.strip()

def parse_json_response(raw_text):
    try:
        return json.loads(raw_text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": raw_text})

def validate_response_shape(endpoint, data):
    if endpoint == "asr_basic":
        result = data.get("result")
        utterances = None
        if isinstance(result, dict):
            raw = result.get("raw")
            if isinstance(raw, dict):
                raw_result = raw.get("result")
                if isinstance(raw_result, dict):
                    utterances = raw_result.get("utterances")
        if not isinstance(result, dict) or not isinstance(utterances, list):
            fail("Missing key field: result.raw.result.utterances", {"response": data})
        return

    segments = data.get("segments")
    if not isinstance(segments, list):
        fail("Missing key field: segments", {"response": data})

    if endpoint == "asr_nlp":
        if segments and not isinstance(segments[0], dict):
            fail("Invalid field: segments[]", {"response": data})
        return

    if endpoint == "asr_llm":
        if segments and not isinstance(segments[0], dict):
            fail("Invalid field: segments[]", {"response": data})
        return

def call_api(endpoint, payload):
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
    except Exception as e:
        fail("Request failed", {"exception": str(e)})

    if status < 200 or status >= 300:
        fail(f"HTTP non-2xx: {status}", {"raw_response": text})

    data = parse_json_response(text)
    if not isinstance(data, dict):
        fail("JSON response must be an object", {"response": data})

    if data.get("success") is False or (isinstance(data.get("error"), str) and data.get("error").strip()):
        fail(data.get("error") or "Business error", data)

    validate_response_shape(endpoint, data)

    print(json.dumps(data, ensure_ascii=False))

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <asr_basic|asr_nlp|asr_llm> '<json_payload>'")
        sys.exit(1)

    action = sys.argv[1]
    endpoint = ACTION_ENDPOINT.get(action)
    if not endpoint:
        print(f"Usage: {sys.argv[0]} <asr_basic|asr_nlp|asr_llm> '<json_payload>'")
        sys.exit(1)

    payload = parse_payload(sys.argv[2])
    validate_payload(payload)
    call_api(endpoint, payload)

if __name__ == "__main__":
    main()