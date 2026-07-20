#!/usr/bin/env python3
"""Pretty-print the current emotional state.

Reads the persisted state JSON, applies time-based decay, and
displays all dimensions with labels and visual indicators.

Usage:
    python scripts/status.py
    python scripts/status.py --config path/to/emoclaw.yaml
    python scripts/status.py --raw         # Print raw JSON
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Show current emotional state")
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to emoclaw.yaml config file",
    )
    parser.add_argument(
        "--raw", action="store_true",
        help="Print raw JSON state instead of formatted output",
    )
    args = parser.parse_args()

    if args.config:
        os.environ["EMOCLAW_CONFIG"] = args.config

    from emotion_model import config
    from emotion_model.state import load_state

    state = load_state(config.STATE_PATH)
    now = datetime.now(timezone.utc)

    if args.raw:
        data = {
            "emotion_vector": state.emotion_vector,
            "decayed_vector": state.get_decayed_emotion(now),
            "last_updated": state.last_updated,
            "last_message_time": state.last_message_time,
            "message_count": state.message_count,
        }
        print(json.dumps(data, indent=2))
        return

    # Calculate decayed state
    decayed = state.get_decayed_emotion(now)
    hours_since = state.seconds_since_last_message(now) / 3600.0

    print(f"\n  Emotional State — {config.AGENT_NAME}")
    print(f"  {'─' * 50}")

    if state.last_updated:
        print(f"  Last updated: {state.last_updated}")
        print(f"  Time elapsed: {hours_since:.1f} hours")
    else:
        print("  No state recorded yet (using baselines)")

    print(f"  Messages this session: {state.message_count}")
    print()

    # Display each dimension
    for i, dim_name in enumerate(config.EMOTION_DIMS):
        val = decayed[i]
        baseline = config.BASELINE_EMOTION[i]
        low, high = config.DIM_DESCRIPTORS[dim_name]

        # Visual bar (20 chars wide)
        bar_pos = int(val * 20)
        bar = "░" * bar_pos + "█" + "░" * (20 - bar_pos)

        # Label based on value
        if val < 0.35:
            label = low
        elif val > 0.65:
            label = high
        else:
            label = "balanced"

        # Show deviation from baseline
        delta = val - baseline
        delta_str = f"+{delta:.2f}" if delta >= 0 else f"{delta:.2f}"

        print(f"  {dim_name:>14s}: {val:.2f} [{bar}] ({label}) Δ{delta_str}")

    # Summary
    from emotion_model.summary import generate_summary
    summary = generate_summary(decayed)
    print(f"\n  This feels like: {summary}")
    print()


if __name__ == "__main__":
    main()
