#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/keyframe_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    draft_id = sys.argv[1] if len(sys.argv) > 1 else ""
    track_name = sys.argv[2] if len(sys.argv) > 2 else "video_main"
    if not draft_id:
        print("Usage: keyframe_ops_demo.py <draft_id> [track_name]")
        raise SystemExit(1)

    single_payload = {
        "draft_id": draft_id,
        "track_name": track_name,
        "property_type": "alpha",
        "time": 0.0,
        "value": "1.0",
    }
    single_out = subprocess.check_output(
        [sys.executable, str(SCRIPT), "add_video_keyframe", json.dumps(single_payload, ensure_ascii=False)],
        text=True,
    )
    print(f"SINGLE_KEYFRAME => {single_out.strip()}")

    batch_payload = {
        "draft_id": draft_id,
        "track_name": track_name,
        "property_types": ["alpha", "scale_x", "transform_x"],
        "times": [0.0, 1.2, 2.4],
        "values": ["1.0", "1.2", "0.15"],
    }
    batch_out = subprocess.check_output(
        [sys.executable, str(SCRIPT), "add_video_keyframe", json.dumps(batch_payload, ensure_ascii=False)],
        text=True,
    )
    print(f"BATCH_KEYFRAME => {batch_out.strip()}")


if __name__ == "__main__":
    main()