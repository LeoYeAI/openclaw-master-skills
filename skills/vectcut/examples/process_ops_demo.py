#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/process_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")

def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action.upper()} => {out.strip()}")
    return json.loads(out)

def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)
    video_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com/demo.mp4"
    start = float(sys.argv[2]) if len(sys.argv) > 2 else 3.3
    end = float(sys.argv[3]) if len(sys.argv) > 3 else 5.1

    run_action("extract_audio", {"video_url": video_url})
    run_action("split_video", {"video_url": video_url, "start": start, "end": end})

if __name__ == "__main__":
    main()