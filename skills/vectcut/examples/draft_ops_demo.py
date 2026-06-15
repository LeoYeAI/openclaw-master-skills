#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/draft_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")

def run_action(action, payload):
    out = subprocess.check_output(
        [sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)],
        text=True
    )
    print(f"{action.upper()} => {out.strip()}")
    return json.loads(out)

def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    create_payload = {"width": 1080, "height": 1920, "name": "draft_ops_demo_py"}
    create_res = run_action("create", create_payload)

    draft_id = ((create_res.get("output") or {}).get("draft_id")) if isinstance(create_res, dict) else None
    if not draft_id:
        print("No draft_id, stop.")
        return

    modify_payload = {"draft_id": draft_id, "name": "draft_ops_demo_py_updated"}
    run_action("modify", modify_payload)

    query_payload = {"draft_id": draft_id}
    run_action("query", query_payload)

    remove_payload = {"draft_id": draft_id}
    run_action("remove", remove_payload)

if __name__ == "__main__":
    main()