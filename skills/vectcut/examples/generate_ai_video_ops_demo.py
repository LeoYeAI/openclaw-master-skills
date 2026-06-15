#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generate_ai_video_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def run(action, payload):
    out = subprocess.check_output(
        [sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)],
        text=True,
    )
    data = json.loads(out)
    print(json.dumps(data, ensure_ascii=False))
    return data


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    generate_payload = {
        "model": "veo3.1",
        "prompt": "特写镜头下，两人凝视着墙上一幅神秘图案，火把光芒忽明忽暗摇曳。",
        "resolution": "1280x720",
    }
    print("=== GENERATE_AI_VIDEO ===")
    create_res = run("generate_ai_video", generate_payload)
    task_id = create_res.get("task_id") or ((create_res.get("output") or {}).get("task_id"))
    if not task_id:
        print("No task_id returned, stop")
        raise SystemExit(1)

    print("=== AI_VIDEO_TASK_STATUS (single query) ===")
    run("ai_video_task_status", {"task_id": task_id})

    print("=== AI_VIDEO_TASK_STATUS (poll sample) ===")
    for _ in range(3):
        status_res = run("ai_video_task_status", {"task_id": task_id})
        if str(status_res.get("status", "")).lower() in {"completed", "failed", "failure"}:
            break
        time.sleep(2)


if __name__ == "__main__":
    main()
