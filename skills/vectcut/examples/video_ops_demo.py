#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "video_ops.py")
BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying").rstrip("/")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

def create_draft():
    url = f"{BASE_URL}/create_draft"
    req = urllib.request.Request(
        url=url,
        data=json.dumps({"name": "demo", "width": 1080, "height": 1920}, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))

def run_action(action, payload):
    out = subprocess.check_output([sys.executable, SCRIPT, action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action} => {out.strip()}")
    return out

def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        sys.exit(1)

    print("=== DEMO CATEGORY: video ===")

    payload = {
        "video_url": "https://player.install-ai-guider.top/example/VID_20260120_211842.mp4",
        "draft_id": draft_id,
        "start": 0,
        "end": 10,
        "target_start": 0,
        "track_name": "video_main"
    }
    add_raw = run_action("add_video", payload)
    add_res = json.loads(add_raw)
    material_id = ((add_res.get("output") or {}).get("material_id")) if isinstance(add_res, dict) else None
    if not material_id:
        print("No material_id, stop.")
        sys.exit(1)

    modify_payload = {
        "draft_id": draft_id,
        "material_id": material_id,
        "video_url": "https://player.install-ai-guider.top/example/VID_20260120_211842.mp4",
        "start": 0,
        "end": 8,
        "transform_x": 0.2,
        "transform_y": 0.2,
        "scale_x": 1.05,
        "scale_y": 1.05,
        "target_start": 1
    }
    run_action("modify_video", modify_payload)

    remove_payload = {"draft_id": draft_id, "material_id": material_id}
    run_action("remove_video", remove_payload)

if __name__ == '__main__':
    main()
