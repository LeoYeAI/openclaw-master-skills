#!/usr/bin/env python3
"""Auto-label extracted passages using the Claude API.

Reads extracted passages and asks Claude to score each on every
configured emotion dimension. Outputs labeled JSONL for training.

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Usage:
    python scripts/label.py
    python scripts/label.py --config path/to/emoclaw.yaml
    python scripts/label.py --review          # Generate human review worksheet
    python scripts/label.py --dry-run         # Show prompt without calling API
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def load_config() -> dict:
    """Load config for labeling."""
    from emotion_model import config
    return {
        "data_dir": config.DATA_DIR,
        "emotion_dims": config.EMOTION_DIMS,
        "dim_descriptors": config.DIM_DESCRIPTORS,
        "baseline_emotion": config.BASELINE_EMOTION,
    }


def build_labeling_prompt(cfg: dict) -> str:
    """Build the system prompt for emotion labeling."""
    dim_lines = []
    for i, name in enumerate(cfg["emotion_dims"]):
        low, high = cfg["dim_descriptors"][name]
        baseline = cfg["baseline_emotion"][i]
        dim_lines.append(f"  - {name}: {low}(0.0) <-> {high}(1.0), baseline={baseline}")

    dims_text = "\n".join(dim_lines)

    return f"""You are an expert at analyzing emotional content in text passages.

For each passage, score it on the following emotion dimensions from 0.0 to 1.0.
The baseline values indicate the neutral/resting state — scores should deviate
from baseline when the passage clearly expresses that emotion.

Dimensions:
{dims_text}

Respond with a JSON object containing:
- "labels": a dict mapping each dimension name to a float score (0.0-1.0)
- "summary": a brief phrase describing the emotional quality (5-15 words)
- "confidence": "high", "medium", or "low" — how clear the emotional content is

Example response:
{{"labels": {{"valence": 0.7, "arousal": 0.4, ...}}, "summary": "warm and contemplative", "confidence": "high"}}

IMPORTANT: Return ONLY the JSON object, no other text."""


def label_passage(
    client,
    passage: dict,
    system_prompt: str,
    model: str = "claude-sonnet-4-20250514",
) -> dict | None:
    """Label a single passage using the Claude API."""
    user_msg = f"""Score this passage on all emotion dimensions:

Source: {passage.get('source_file', 'unknown')}
Heading: {passage.get('heading', '')}

---
{passage['text'][:1200]}
---"""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )

        result_text = response.content[0].text.strip()

        # Parse JSON from response (handle markdown code blocks)
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        return json.loads(result_text)

    except json.JSONDecodeError as e:
        print(f"  Warning: Failed to parse response as JSON: {e}")
        return None
    except Exception as e:
        print(f"  Warning: API call failed: {e}")
        return None


def generate_review_worksheet(
    passages: list[dict],
    labels: list[dict],
    output_path: Path,
    cfg: dict,
) -> None:
    """Generate a human-readable review worksheet."""
    lines = [
        "# Emotion Labeling Review",
        "",
        "Review and correct auto-generated labels. Edit scores that seem wrong.",
        "",
    ]

    for i, (passage, label) in enumerate(zip(passages, labels), 1):
        lines.extend([
            f"## Passage {i} — {passage.get('heading', passage.get('source_file', ''))}",
            f"*Source: {passage.get('source_file', 'unknown')}* | "
            f"Confidence: {label.get('confidence', 'unknown')}",
            "",
            "```",
            passage["text"][:600],
            "```",
            "",
            f"**Summary:** {label.get('summary', '')}",
            "",
            "| Dimension | Score | OK? |",
            "|-----------|-------|-----|",
        ])

        for dim_name in cfg["emotion_dims"]:
            score = label.get("labels", {}).get(dim_name, "?")
            if isinstance(score, float):
                score = f"{score:.2f}"
            lines.append(f"| {dim_name} | {score} | |")

        lines.extend(["", "---", ""])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-label passages with Claude API")
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to emoclaw.yaml config file",
    )
    parser.add_argument(
        "--review", action="store_true",
        help="Generate a human review worksheet after labeling",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show the prompt without calling the API",
    )
    parser.add_argument(
        "--yes", "-y", action="store_true",
        help="Skip the consent prompt (for automation)",
    )
    parser.add_argument(
        "--model", type=str, default="claude-sonnet-4-20250514",
        help="Claude model to use for labeling",
    )
    parser.add_argument(
        "--input", type=str, default=None,
        help="Input JSONL file (default: data/extracted_passages.jsonl)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output JSONL file (default: data/passage_labels.jsonl)",
    )
    args = parser.parse_args()

    if args.config:
        os.environ["EMOCLAW_CONFIG"] = args.config

    cfg = load_config()
    data_dir = cfg["data_dir"]

    input_path = Path(args.input) if args.input else data_dir / "extracted_passages.jsonl"
    output_path = Path(args.output) if args.output else data_dir / "passage_labels.jsonl"

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("Run extract.py first to generate passages.")
        sys.exit(1)

    # Load passages
    passages = []
    with open(input_path) as f:
        for line in f:
            if line.strip():
                passages.append(json.loads(line))

    print(f"Loaded {len(passages)} passages from {input_path}")

    system_prompt = build_labeling_prompt(cfg)

    if args.dry_run:
        print("\n--- System Prompt ---")
        print(system_prompt)
        print("\n--- Sample User Message ---")
        if passages:
            print(f"Score this passage on all emotion dimensions:\n\n"
                  f"Source: {passages[0].get('source_file', 'unknown')}\n"
                  f"Heading: {passages[0].get('heading', '')}\n\n---\n"
                  f"{passages[0]['text'][:400]}\n---")
        return

    # --- Consent prompt ---
    total_chars = sum(len(p["text"]) for p in passages)
    source_files = sorted(set(p.get("source_file", "unknown") for p in passages))

    print(f"\n{'=' * 60}")
    print(f"  Passages to label:  {len(passages)}")
    print(f"  Total characters:   {total_chars:,}")
    print(f"  Source files ({len(source_files)}):")
    for sf in source_files:
        print(f"    - {sf}")
    print(f"\n  These passages will be sent to the Anthropic API")
    print(f"  for emotional labeling (model: {args.model}).")
    print(f"{'=' * 60}")

    if not args.yes:
        try:
            answer = input("\nContinue? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = ""
        if answer not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Get your key from https://console.anthropic.com/")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("Error: anthropic package not installed.")
        print("Install with: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Label passages
    labels = []
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for i, passage in enumerate(passages, 1):
            print(f"  [{i}/{len(passages)}] {passage.get('heading', '')[:50]}...", end=" ")

            result = label_passage(client, passage, system_prompt, model=args.model)

            if result is None:
                print("FAILED")
                continue

            print(f"OK (confidence: {result.get('confidence', '?')})")

            # Merge passage info with labels
            labeled = {
                "text": passage["text"],
                "source_file": passage.get("source_file", ""),
                "heading": passage.get("heading", ""),
                "labels": result.get("labels", {}),
                "summary": result.get("summary", ""),
                "confidence": result.get("confidence", ""),
            }

            f.write(json.dumps(labeled) + "\n")
            labels.append(result)

            # Rate limiting — be gentle with the API
            time.sleep(0.5)

    print(f"\nLabeled {len(labels)}/{len(passages)} passages")
    print(f"Output: {output_path}")

    if args.review:
        review_path = data_dir / "labeling_review.md"
        generate_review_worksheet(passages[:len(labels)], labels, review_path, cfg)
        print(f"Review worksheet: {review_path}")


if __name__ == "__main__":
    main()
