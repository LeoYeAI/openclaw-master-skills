#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/text_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    draft_id = sys.argv[1] if len(sys.argv) > 1 else ""
    if not draft_id:
        print("Usage: text_ops_demo.py <draft_id>")
        raise SystemExit(1)

    add_payload = {
        "text": "你好!Hello",
        "start": 0,
        "end": 5,
        "draft_id": draft_id,
        "font": "文轩体",
        "font_color": "#FF0000",
        "font_size": 8.0,
        "track_name": "text_main",
        "intro_animation": "向下飞入",
        "intro_duration": 0.5,
        "outro_animation": "向下滑动",
        "outro_duration": 0.5,
    }

    add_out = subprocess.check_output([sys.executable, str(SCRIPT), "add_text", json.dumps(add_payload, ensure_ascii=False)], text=True)
    print(f"ADD_TEXT => {add_out.strip()}")
    add_data = json.loads(add_out)
    material_id = ((add_data.get("output") or {}).get("material_id")) if isinstance(add_data, dict) else ""
    if not material_id:
        print("No material_id from add_text, stop")
        raise SystemExit(1)

    modify_payload = dict(add_payload)
    modify_payload.update({"draft_id": draft_id, "material_id": material_id, "text": "你好!Hello(已修改)", "track_name": "text_main_2"})
    modify_out = subprocess.check_output([sys.executable, str(SCRIPT), "modify_text", json.dumps(modify_payload, ensure_ascii=False)], text=True)
    print(f"MODIFY_TEXT => {modify_out.strip()}")

    remove_payload = {"draft_id": draft_id, "material_id": material_id}
    remove_out = subprocess.check_output([sys.executable, str(SCRIPT), "remove_text", json.dumps(remove_payload, ensure_ascii=False)], text=True)
    print(f"REMOVE_TEXT => {remove_out.strip()}")


if __name__ == "__main__":
    main()