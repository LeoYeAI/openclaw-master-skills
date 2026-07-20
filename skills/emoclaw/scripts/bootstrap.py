#!/usr/bin/env python3
"""Full bootstrap pipeline: extract -> label -> prepare -> train.

Runs the complete pipeline from identity/memory files to a trained
emotion model. Requires ANTHROPIC_API_KEY for the labeling step.

Usage:
    python scripts/bootstrap.py
    python scripts/bootstrap.py --config path/to/emoclaw.yaml
    python scripts/bootstrap.py --skip-label    # Skip API labeling (use existing labels)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent


def run_step(name: str, cmd: list[str]) -> bool:
    """Run a pipeline step and return success."""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}\n")

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))

    if result.returncode != 0:
        print(f"\nERROR: {name} failed (exit code {result.returncode})")
        return False

    print(f"\n  {name} completed successfully.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap emotion model from scratch")
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to emoclaw.yaml config file",
    )
    parser.add_argument(
        "--skip-label", action="store_true",
        help="Skip the API labeling step (use existing labeled data)",
    )
    parser.add_argument(
        "--skip-extract", action="store_true",
        help="Skip extraction (use existing extracted passages)",
    )
    parser.add_argument(
        "--label-model", type=str, default="claude-sonnet-4-20250514",
        help="Claude model for labeling",
    )
    args = parser.parse_args()

    if args.config:
        os.environ["EMOCLAW_CONFIG"] = args.config

    python = sys.executable
    config_args = ["--config", args.config] if args.config else []

    print("Emotion Model Bootstrap Pipeline")
    print(f"  Python: {python}")
    print(f"  Repo root: {REPO_ROOT}")
    if args.config:
        print(f"  Config: {args.config}")

    # Step 1: Extract passages
    if not args.skip_extract:
        extract_cmd = [python, str(SCRIPT_DIR / "extract.py")] + config_args
        if not run_step("Step 1: Extract Passages", extract_cmd):
            sys.exit(1)
    else:
        print("\n  Skipping extraction (--skip-extract)")

    # Step 2: Auto-label with Claude API
    if not args.skip_label:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("\nERROR: ANTHROPIC_API_KEY not set. Set it or use --skip-label.")
            sys.exit(1)

        label_cmd = [
            python, str(SCRIPT_DIR / "label.py"),
            "--model", args.label_model,
            "--review",
        ] + config_args
        if not run_step("Step 2: Auto-Label Passages", label_cmd):
            sys.exit(1)
    else:
        print("\n  Skipping labeling (--skip-label)")

    # Step 3: Prepare dataset (train/val split)
    prepare_cmd = [python, "-m", "emotion_model.scripts.prepare_dataset"]
    if not run_step("Step 3: Prepare Dataset", prepare_cmd):
        sys.exit(1)

    # Step 4: Train
    train_cmd = [python, "-m", "emotion_model.scripts.train"]
    if not run_step("Step 4: Train Model", train_cmd):
        sys.exit(1)

    # Step 5: Diagnostics
    diag_cmd = [python, "-m", "emotion_model.scripts.diagnose"]
    if not run_step("Step 5: Run Diagnostics", diag_cmd):
        print("  (Diagnostics failed but model may still be usable)")

    print(f"\n{'=' * 60}")
    print("  Bootstrap Complete!")
    print(f"{'=' * 60}")
    print("\nNext steps:")
    print("  1. Review diagnostics output above")
    print("  2. Check the review worksheet: emotion_model/data/labeling_review.md")
    print("  3. Start the daemon: bash scripts/daemon.sh start")
    print("  4. Or import directly: from emotion_model.inference import EmotionEngine")


if __name__ == "__main__":
    main()
