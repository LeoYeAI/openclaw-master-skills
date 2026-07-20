#!/usr/bin/env python3
"""Output the [EMOTIONAL STATE] block for system prompt injection.

Reads the persisted state, applies time-based decay, and outputs
the formatted block. No daemon or model loading needed.

Usage:
    python scripts/inject_state.py
    python scripts/inject_state.py --config path/to/emoclaw.yaml

    # In a shell script:
    STATE_BLOCK=$(python scripts/inject_state.py 2>/dev/null)
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate emotional state block")
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to emoclaw.yaml config file",
    )
    args = parser.parse_args()

    if args.config:
        os.environ["EMOCLAW_CONFIG"] = args.config

    from emotion_model import config
    from emotion_model.state import load_state
    from emotion_model.summary import generate_summary

    state = load_state(config.STATE_PATH)
    now = datetime.now(timezone.utc)

    # Get decayed emotion (accounts for time since last message)
    emotion = state.get_decayed_emotion(now)

    # Build the block
    lines = ["[EMOTIONAL STATE]"]

    for i, dim_name in enumerate(config.EMOTION_DIMS):
        val = emotion[i]
        low, high = config.DIM_DESCRIPTORS[dim_name]
        if val < 0.35:
            label = low
        elif val > 0.65:
            label = high
        else:
            label = "balanced"
        lines.append(f"{dim_name.capitalize()}: {val:.2f} ({label})")

    summary = generate_summary(emotion)
    lines.append(f"\nThis feels like: {summary}")
    lines.append("[/EMOTIONAL STATE]")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
