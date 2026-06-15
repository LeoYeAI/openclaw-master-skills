#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generate_speech_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")


def main():
    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    text = sys.argv[1] if len(sys.argv) > 1 else "今天的视频，就给大家带来一个福利。"
    payload = {
        "text": text,
        "provider": "minimax",
        "model": "speech-2.6-turbo",
        "voice_id": "audiobook_male_1",
        "volume": 10,
        "target_start": 3,
        "effect_type": "麦霸",
        "effect_params": [45, 80],
    }

    out = subprocess.check_output(
        [sys.executable, str(SCRIPT), "generate_speech", json.dumps(payload, ensure_ascii=False)],
        text=True,
    )
    print(f"GENERATE_SPEECH => {out.strip()}")

    file_url = sys.argv[2] if len(sys.argv) > 2 else ""
    if file_url:
        clone_payload = {"file_url": file_url, "title": "demo_clone_voice"}
        clone_out = subprocess.check_output(
            [sys.executable, str(SCRIPT), "fish_clone", json.dumps(clone_payload, ensure_ascii=False)],
            text=True,
        )
        print(f"FISH_CLONE => {clone_out.strip()}")

    assets_payload = {"limit": 100, "offset": 0, "provider": "fish"}
    assets_out = subprocess.check_output(
        [sys.executable, str(SCRIPT), "voice_assets", json.dumps(assets_payload, ensure_ascii=False)],
        text=True,
    )
    print(f"VOICE_ASSETS => {assets_out.strip()}")


if __name__ == "__main__":
    main()