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
INTRO_ANIMATION_ENUM = Path(os.getenv("INTRO_ANIMATION_ENUM", str(ROOT / "references/enums/intro_animation_types.json")))
OUTRO_ANIMATION_ENUM = Path(os.getenv("OUTRO_ANIMATION_ENUM", str(ROOT / "references/enums/outro_animation_types.json")))
COMBO_ANIMATION_ENUM = Path(os.getenv("COMBO_ANIMATION_ENUM", str(ROOT / "references/enums/combo_animation_types.json")))
MASK_TYPE_ENUM = Path(os.getenv("MASK_TYPE_ENUM", str(ROOT / "references/enums/mask_types.json")))


ACTION_ENDPOINT = {
    "add_image": "add_image",
    "modify_image": "modify_image",
    "remove_image": "remove_image",
}


def fail(error, output=None, hint=None):
    data = {"success": False, "error": error, "output": output if output is not None else ""}
    if hint:
        data["hint"] = hint
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)

def load_enum_names(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {item.get("name") for item in data.get("items", []) if isinstance(item, dict) and item.get("name")}
    except Exception as e:
        fail(f"Failed to load enum file: {path}", {"exception": str(e)})

def parse_payload(raw):
    try:
        data = json.loads(raw)
    except Exception as e:
        fail("Invalid JSON payload", {"payload": raw, "exception": str(e)})
    if not isinstance(data, dict):
        fail("Payload must be a JSON object", {"payload": data})
    return data


def parse_json_response(raw_text):
    try:
        return json.loads(raw_text)
    except Exception:
        fail("Response is not valid JSON", {"raw_response": raw_text})

def known_error_hint(msg):
    if not msg:
        return None
    if "Unknown intro" in msg or "intro_animation" in msg and "Unknown" in msg:
        return "intro_animation 非法，检查 references/enums/intro_animation_types.json"
    if "Unknown outro" in msg or "outro_animation" in msg and "Unknown" in msg:
        return "outro_animation 非法，检查 references/enums/outro_animation_types.json"
    if "Unknown combo" in msg or "combo_animation" in msg and "Unknown" in msg:
        return "combo_animation 非法，检查 references/enums/combo_animation_types.json"
    if "Unknown mask" in msg or "mask_type" in msg and "Unknown" in msg:
        return "mask_type 非法，检查 references/enums/mask_types.json"
    if "New segment overlaps with existing segment" in msg:
        m = re.search(r"start:\s*(\d+),\s*end:\s*(\d+)", msg)
        if m:
            return f"时间片段冲突(us): start={m.group(1)}, end={m.group(2)}；可更换 track_name 或调整 start/end"
        return "时间片段冲突；可更换 track_name 或调整 start/end"
    return None

def ensure_required_fields(endpoint, payload):
    if endpoint == "add_image":
        if not payload.get("image_url"):
            fail("Missing required fields for add_image: image_url", {"payload": payload})
        return
    if endpoint == "modify_image":
        if not payload.get("draft_id") or not payload.get("material_id"):
            fail("Missing required fields for modify_image: draft_id/material_id", {"payload": payload})
        return
    if endpoint == "remove_image":
        if not payload.get("draft_id") or not payload.get("material_id"):
            fail("Missing required fields for remove_image: draft_id/material_id", {"payload": payload})
        return

def ensure_image_enums_valid(endpoint, payload):
    if endpoint == "remove_image":
        return

    intro_animation = payload.get("intro_animation")
    outro_animation = payload.get("outro_animation")
    combo_animation = payload.get("combo_animation")
    mask_type = payload.get("mask_type")

    if intro_animation:
        names = load_enum_names(INTRO_ANIMATION_ENUM)
        if intro_animation not in names:
            fail(f"Unknown intro animation: {intro_animation}", hint="检查 references/enums/intro_animation_types.json")
    if outro_animation:
        names = load_enum_names(OUTRO_ANIMATION_ENUM)
        if outro_animation not in names:
            fail(f"Unknown outro animation: {outro_animation}", hint="检查 references/enums/outro_animation_types.json")
    if combo_animation:
        names = load_enum_names(COMBO_ANIMATION_ENUM)
        if combo_animation not in names:
            fail(f"Unknown combo animation: {combo_animation}", hint="检查 references/enums/combo_animation_types.json")
    if mask_type:
        names = load_enum_names(MASK_TYPE_ENUM)
        if mask_type not in names:
            fail(f"Unknown mask type: {mask_type}", hint="检查 references/enums/mask_types.json")

def call_api(endpoint, payload):
    if not API_KEY:
        fail("VECTCUT_API_KEY is required")

    ensure_required_fields(endpoint, payload)
    ensure_image_enums_valid(endpoint, payload)

    url = f"{BASE_URL.rstrip('/')}/{endpoint}"
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        url=url,
        data=body,
        method='POST',
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode('utf-8', errors='replace')
            status = resp.status
    except urllib.error.HTTPError as e:
        text = e.read().decode('utf-8', errors='replace')
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
        hint = known_error_hint(error_msg if isinstance(error_msg, str) else None)
        fail(error_msg if error_msg else "Business error", output if output is not None else "", hint=hint)

    out = output if isinstance(output, dict) else None
    draft_id = out.get("draft_id") if out else None
    draft_url = out.get("draft_url") if out else None
    if not draft_id or not draft_url:
        fail("Missing key fields: output.draft_id/output.draft_url", {"response": data})

    print(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) < 3:
        print("Usage: image_ops.py <add_image|modify_image|remove_image> '<json_payload>'")
        sys.exit(1)

    action = sys.argv[1]
    raw_payload = sys.argv[2]
    endpoint = ACTION_ENDPOINT.get(action)
    if not endpoint:
        print("Usage: image_ops.py <add_image|modify_image|remove_image> '<json_payload>'")
        sys.exit(1)

    payload = parse_payload(raw_payload)
    call_api(endpoint, payload)


if __name__ == "__main__":
    main()
