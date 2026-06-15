#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/material_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")

def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action.upper()} => {out.strip()}")

def main():
    media_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com/demo.mp4"

    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    payload = {"url": media_url}
    run_action("get_duration", payload)
    run_action("get_resolution", payload)

    detail_payload = {"video_url": media_url}
    run_action("video_detail", detail_payload)

if __name__ == "__main__":
    main()