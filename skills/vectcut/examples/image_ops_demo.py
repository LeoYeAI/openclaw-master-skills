#!/usr/bin/env python3
import json
import os
import random
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/image_ops.py"
BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying").rstrip("/")
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def load_items(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return [x["name"] for x in data.get("items", []) if isinstance(x, dict) and x.get("name")]


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
    out = subprocess.check_output(
        [sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True
    )
    print(f"{action} => {out.strip()}")
    return json.loads(out)


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        sys.exit(1)

    create_res = create_draft()
    draft_id = ((create_res.get("output") or {}).get("draft_id")) if isinstance(create_res, dict) else None
    if not draft_id:
        print("No draft_id, stop.")
        sys.exit(1)

    intro_animation_types = load_items(
        ROOT / "references/enums/intro_animation_types.json")
    if not intro_animation_types:
        print("No intro_animation types found in enum files.")
        sys.exit(1)

    outro_animation_types = load_items(
        ROOT / "references/enums/outro_animation_types.json")
    if not outro_animation_types:
        print("No outro_animation types found in enum files.")
        sys.exit(1)

    combo_animation_types = load_items(
        ROOT / "references/enums/combo_animation_types.json")
    if not combo_animation_types:
        print("No combo_animation types found in enum files.")
        sys.exit(1)

    mask_types = load_items(
        ROOT / "references/enums/mask_types.json")
    if not mask_types:
        print("No mask types found in enum files.")
        sys.exit(1)

    intro_animation_type = random.choice(intro_animation_types)
    print(f"Use intro_animation: {intro_animation_type}")
    outro_animation_type = random.choice(outro_animation_types)
    print(f"Use outro_animation: {outro_animation_type}")
    combo_animation_type = random.choice(combo_animation_types)
    print(f"Use combo_animation: {combo_animation_type}")
    mask_type = random.choice(mask_types)
    print(f"Use mask_type: {mask_type}")

    add_payload = {
        "image_url": "https://pic1.imgdb.cn/item/68ba8fc058cb8da5c8801ab0.png",
        "start": 0,
        "end": 5,
        "width": 1920,
        "height": 1080,
        "draft_id": draft_id,
        "transform_x": 0.2,
        "transform_y": 0.2,
        "scale_x": 1,
        "scale_y": 1,
        "track_name": "video_main",
        "relative_index": 99,
        "intro_animation": intro_animation_type,
        "intro_animation_duration": 0.5,
        "outro_animation": outro_animation_type,
        "outro_animation_duration": 0.5,
        "combo_animation": combo_animation_type,
        "combo_animation_duration": 0.5,
        "mask_type": mask_type,
        "mask_center_x": 0.5,
        "mask_center_y": 0.5,
        "mask_size": 0.7,
        "mask_rotation": 45,
        "mask_feather": 2,
        "mask_invert": True,
        "mask_rect_width": 8,
        "mask_round_corner": 10
    }
    add_res = run_action("add_image", add_payload)
    material_id = ((add_res.get("output") or {}).get("material_id")) if isinstance(add_res, dict) else None
    if not material_id:
        print("No material_id, stop.")
        sys.exit(1)

    modify_payload = {
        "material_id": material_id,
        "draft_id": draft_id,
        "image_url": "https://pic1.imgdb.cn/item/68ba8fc058cb8da5c8801ab0.png",
        "start": 1,
        "end": 4.5,
        "scale_x": 0.9,
        "scale_y": 0.9,
        "transform_x": 0.1,
        "transform_y": 0.1,
        "outro_animation": outro_animation_type,
        "alpha": 0.85,
        "rotation": 10
    }
    run_action("modify_image", modify_payload)

    remove_payload = {"draft_id": draft_id, "material_id": material_id}
    run_action("remove_image", remove_payload)


if __name__ == "__main__":
    main()
