#!/usr/bin/env python3
import json
import os
import random
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/filter_ops.py"
BASE_URL = os.getenv("VECTCUT_BASE_URL", "https://open.vectcut.com/cut_jianying")
API_KEY = os.getenv("VECTCUT_API_KEY", "")

def load_items(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return [x["name"] for x in data.get("items", []) if isinstance(x, dict) and x.get("name")]

def create_draft():
    url = f"{BASE_URL.rstrip('/')}/create_draft"
    req = urllib.request.Request(
        url=url,
        data=json.dumps({"name": "filter_demo", "width": 1080, "height": 1920}, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))

def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action.upper()} => {out.strip()}")
    return json.loads(out)

def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        sys.exit(1)

    names = load_items(ROOT / "references/enums/filter_types.json")
    if not names:
        print("No filter types found in enum file.")
        sys.exit(1)

    filter_type = random.choice(names)
    print(f"Use filter_type: {filter_type}")

    try:
        create_res = create_draft()
    except urllib.error.HTTPError as e:
        print(f"CREATE => HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"CREATE => failed: {e}")
        sys.exit(1)

    print("CREATE => " + json.dumps(create_res, ensure_ascii=False))
    draft_id = ((create_res.get("output") or {}).get("draft_id")) if isinstance(create_res, dict) else None
    if not draft_id:
        print("No draft_id, stop.")
        sys.exit(1)

    add_payload = {
        "draft_id": draft_id,
        "filter_type": filter_type,
        "start": 0,
        "end": 3,
        "track_name": "filter_1",
        "relative_index": 1,
        "intensity": 86,
    }
    add_res = run_action("add", add_payload)
    material_id = ((add_res.get("output") or {}).get("material_id")) if isinstance(add_res, dict) else None
    if not material_id:
        print("No material_id, skip modify/remove.")
        return

    mod_payload = {
        "draft_id": draft_id,
        "material_id": material_id,
        "filter_type": filter_type,
        "start": 1,
        "end": 4,
        "track_name": "filter_1",
        "relative_index": 1,
        "intensity": 45,
    }
    run_action("modify", mod_payload)

    rm_payload = {"draft_id": draft_id, "material_id": material_id}
    run_action("remove", rm_payload)

if __name__ == "__main__":
    main()