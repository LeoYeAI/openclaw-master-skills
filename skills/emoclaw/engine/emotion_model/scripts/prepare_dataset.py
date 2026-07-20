"""Prepare training dataset from labeled data.

Combines labeled passages, scenario expansions, and anchor examples
into train/val JSONL files ready for training.

Usage:
    python -m emotion_model.scripts.prepare_dataset
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from emotion_model import config

DATA_DIR = Path(__file__).parent.parent / "data"

# Dimension names — derived from config, not hardcoded
DIM_NAMES = config.EMOTION_DIMS


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file, returning empty list if not found."""
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def validate_example(ex: dict) -> bool:
    """Check that an example has required fields and valid values."""
    if "message_text" not in ex and "text" not in ex:
        return False
    if "emotion_vector" not in ex:
        return False

    vec = ex["emotion_vector"]
    if len(vec) != config.NUM_EMOTION_DIMS:
        return False
    if not all(0.0 <= v <= 1.0 for v in vec):
        return False

    return True


def normalize_example(ex: dict) -> dict:
    """Normalize field names across data sources."""
    normalized = {
        "message_text": ex.get("message_text") or ex.get("text", ""),
        "emotion_vector": ex["emotion_vector"],
        "sender": ex.get("sender", "primary"),
        "channel": ex.get("channel", "chat"),
        "summary": ex.get("summary", ""),
        "source": ex.get("source", "unknown"),
    }

    # Optional fields
    if "prev_emotion" in ex:
        normalized["prev_emotion"] = ex["prev_emotion"]
    if "context" in ex:
        normalized["context"] = ex["context"]

    return normalized


def main() -> None:
    all_examples: list[dict] = []

    # Load all data sources
    sources = {
        "labeled_passages": DATA_DIR / "labeled_passages.jsonl",
        "scenario_labels": DATA_DIR / "scenario_labels.jsonl",
        "anchor_examples": DATA_DIR / "anchor_examples.jsonl",
        "active_annotations": DATA_DIR / "active_annotations.jsonl",
    }

    for source_name, path in sources.items():
        examples = load_jsonl(path)
        for ex in examples:
            ex["source"] = source_name
            if validate_example(ex):
                all_examples.append(normalize_example(ex))
            else:
                print(f"  Skipping invalid example from {source_name}: {str(ex)[:80]}")
        if examples:
            print(f"  {source_name}: {len(examples)} examples")

    print(f"\nTotal valid examples: {len(all_examples)}")

    if len(all_examples) < 10:
        print("Too few examples to create a dataset. Need at least 10.")
        print("Run the labeling process first (see data/labeling_worksheet.md).")
        return

    # Shuffle and split 80/20
    random.seed(42)
    random.shuffle(all_examples)

    split_idx = int(len(all_examples) * 0.8)
    train = all_examples[:split_idx]
    val = all_examples[split_idx:]

    # Write output
    for name, data in [("train", train), ("val", val)]:
        path = DATA_DIR / f"{name}.jsonl"
        with open(path, "w") as f:
            for ex in data:
                f.write(json.dumps(ex) + "\n")
        print(f"  {name}: {len(data)} examples -> {path}")


if __name__ == "__main__":
    main()
