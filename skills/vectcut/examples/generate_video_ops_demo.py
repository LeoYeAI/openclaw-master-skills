#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generate_video_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")

def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action.upper()} => {out.strip()}")
    return json.loads(out)

def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)
    draft_id = sys.argv[1] if len(sys.argv) > 1 else ""
    if not draft_id:
        print("Usage: python examples/generate_video_ops_demo.py <draft_id> [resolution] [framerate]")
        raise SystemExit(1)
    resolution = sys.argv[2] if len(sys.argv) > 2 else "1080P"
    framerate = sys.argv[3] if len(sys.argv) > 3 else "30"

    generate_payload = {"draft_id": draft_id, "resolution": resolution, "framerate": framerate}
    generate_res = run_action("generate_video", generate_payload)
    task_id = ((generate_res.get("output") or {}).get("task_id")) if isinstance(generate_res, dict) else None
    if not task_id:
        print("No task_id, stop.")
        raise SystemExit(1)

    final_res = run_action("render_wait", {"task_id": task_id, "max_poll": 300, "poll_interval": 2})
    result_url = ((final_res.get("output") or {}).get("result")) if isinstance(final_res, dict) else None
    if result_url:
        print(f"PLAY_URL => {result_url}")

if __name__ == "__main__":
    main()