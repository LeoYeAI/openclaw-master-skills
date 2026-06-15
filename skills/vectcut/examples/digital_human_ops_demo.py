#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/digital_human_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def run(action, payload):
    out = subprocess.check_output(
        [sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)],
        text=True,
    )
    data = json.loads(out)
    print(json.dumps(data, ensure_ascii=False))
    return data


def extract_task_id(data):
    if not isinstance(data, dict):
        return ""
    task_id = data.get("task_id") or data.get("id")
    if isinstance(task_id, str) and task_id.strip():
        return task_id
    output = data.get("output")
    if isinstance(output, dict):
        nested = output.get("task_id") or output.get("id")
        if isinstance(nested, str) and nested.strip():
            return nested
    return ""


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    create_payload = {
        "audio_url": "https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/d0f39150-7b57-4d0d-bfca-730901dca0da-c5ef496b-07b6.mp3",
        "video_url": "https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/VID_20260114_231107.mp4",
    }
    print("=== CREATE_DIGITAL_HUMAN ===")
    create_res = run("create_digital_human", create_payload)
    task_id = extract_task_id(create_res)
    if not task_id:
        print("No task_id returned, stop")
        raise SystemExit(1)

    print("=== DIGITAL_HUMAN_TASK_STATUS ===")
    for _ in range(3):
        status_res = run("digital_human_task_status", {"task_id": task_id})
        status = str(status_res.get("status", "")).lower()
        if status in {"completed", "failed", "failure", "error"}:
            break
        time.sleep(2)


if __name__ == "__main__":
    main()
