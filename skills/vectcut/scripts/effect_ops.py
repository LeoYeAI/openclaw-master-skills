#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")
ROOT = Path(__file__).resolve().parents[1]
CHAR_ENUM = Path(os.getenv("CHAR_ENUM", str(ROOT / "references/enums/character_effect_types.json")))
SCENE_ENUM = Path(os.getenv("SCENE_ENUM", str(ROOT / "references/enums/scene_effect_types.json")))

ACTION_ENDPOINT = {
    "add": "add_effect",
    "modify": "modify_effect",
    "remove": "remove_effect",
}

def fail(error, output=None, hint=None):
    data = {"success": False, "error": error, "output": output if output is not None else ""}
    if hint:
        data["hint"] = hint
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)

def load_enum_names(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {item.get("name") for item in data.get("items", []) if isinstance(item, dict) and item.get("name")}
    except Exception as e:
        fail(f"Failed to load enum file: {path}", {"exception": str(e)})

def parse_payload(raw):
    try:
        return json.loads(raw)
    except Exception as e:
        fail("Invalid JSON payload", {"payload": raw, "exception": str(e)})

def parse_json_response(raw_text):
    try:
        return json.loads(raw_text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": raw_text})

def known_error_hint(msg):
    if "Unknown scene effect type" in msg:
        return "effect_type 非法，检查 references/enums/scene_effect_types.json"
    if "Unknown character effect type" in msg:
        return "effect_type 非法，检查 references/enums/character_effect_types.json"
    if "New segment overlaps with existing segment" in msg:
        m = re.search(r"start:\s*(\d+),\s*end:\s*(\d+)", msg)
        if m:
            return f"时间片段冲突(us): start={m.group(1)}, end={m.group(2)}；可更换 track_name 或调整 start/end"
        return "时间片段冲突；可更换 track_name 或调整 start/end"
    return None

def ensure_effect_type_valid(payload):
    effect_type = payload.get("effect_type")
    if not effect_type:
        return
    effect_category = payload.get("effect_category")
    char_names = load_enum_names(CHAR_ENUM)
    scene_names = load_enum_names(SCENE_ENUM)

    if effect_category == "character":
        if effect_type not in char_names:
            fail(f"Unknown character effect type: {effect_type}")
        return
    if effect_category == "scene":
        if effect_type not in scene_names:
            fail(f"Unknown scene effect type: {effect_type}")
        return
    if effect_type not in char_names and effect_type not in scene_names:
        fail(f"Unknown effect type: {effect_type}")

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
        hint = known_error_hint(error_msg if isinstance(error_msg, str) else "")
        fail(error_msg if error_msg else "Business error", output=output, hint=hint)

    if output is None and endpoint != "remove_effect":
        fail("Missing key field: output", {"response": data})

    print(json.dumps(data, ensure_ascii=False))

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <add|modify|remove> '<json_payload>'")
        sys.exit(1)

    action = sys.argv[1]
    raw_payload = sys.argv[2]
    endpoint = ACTION_ENDPOINT.get(action)
    if not endpoint:
        print(f"Usage: {sys.argv[0]} <add|modify|remove> '<json_payload>'")
        sys.exit(1)

    payload = parse_payload(raw_payload)

    if action in {"add", "modify"}:
        ensure_effect_type_valid(payload)

    call_api(endpoint, payload)

if __name__ == "__main__":
    main()