#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/asr_ops.py"
API_KEY = os.getenv("VECTCUT_API_KEY", "")

def run_action(action, payload):
    out = subprocess.check_output([sys.executable, str(SCRIPT), action, json.dumps(payload, ensure_ascii=False)], text=True)
    print(f"{action.upper()} => {out.strip()}")
    data = json.loads(out)
    if action == "asr_basic":
        utterances = (((data.get("result") or {}).get("raw") or {}).get("result") or {}).get("utterances") or []
        print(f"{action.upper()} parsed utterances={len(utterances)}")
    else:
        segments = data.get("segments") or []
        print(f"{action.upper()} parsed segments={len(segments)}")

def main():
    media_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com/demo.mp4"
    known_content = sys.argv[2] if len(sys.argv) > 2 else ""

    if not API_KEY:
        print("ERROR: VECTCUT_API_KEY is required")
        raise SystemExit(1)

    payload = {"url": media_url}
    if known_content.strip():
        payload["content"] = known_content

    run_action("asr_llm", payload)
    run_action("asr_nlp", payload)
    run_action("asr_basic", payload)

if __name__ == "__main__":
    main()