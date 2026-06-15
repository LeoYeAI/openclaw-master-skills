#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "sticker_ops.py")
BASE_URL = os.getenv("VECTCUT_BASE_URL",
                     "https://open.vectcut.com/cut_jianying").rstrip("/")
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def create_draft():
    url = f"{BASE_URL}/create_draft"
    req = urllib.request.Request(
        url=url,
        data=json.dumps({"name": "demo", "width": 1080,
                        "height": 1920}, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))


def run_action(action, payload):
    out = subprocess.check_output([sys.executable, SCRIPT, action, json.dumps(
        payload, ensure_ascii=False)], text=True)
    print(f"{action} => {out.strip()}")
    return out


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        sys.exit(1)

    print("=== DEMO CATEGORY: sticker ===")

    create_res = create_draft()
    print('CREATE => ' + json.dumps(create_res, ensure_ascii=False))
    draft_id = ((create_res.get('output') or {}).get('draft_id')
                ) if isinstance(create_res, dict) else None
    if not draft_id:
        print('No draft_id, stop.')
        sys.exit(1)

    payload = {
        "keywords": "生日快乐",
        "count": 3,
        "offset": 2
    }
    run_action("search_sticker", payload)

    payload = {
        "sticker_id": "7132097333466025252",
        "start": 0,
        "end": 5,
        "draft_id": "__DRAFT_ID__",
        "transform_y": 0,
        "transform_x": 0,
        "alpha": 1,
        "flip_horizontal": false,
        "flip_vertical": false,
        "rotation": 0,
        "scale_x": 1,
        "scale_y": 1,
        "track_name": "sticker_main",
        "relative_index": 0,
        "width": 1080,
        "height": 1920
    }
    payload['draft_id'] = draft_id
    run_action("add_sticker", payload)


if __name__ == '__main__':
    main()
