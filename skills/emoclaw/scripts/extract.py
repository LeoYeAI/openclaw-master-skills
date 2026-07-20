#!/usr/bin/env python3
"""Extract emotional passages from identity/memory files.

Reads source files configured in emoclaw.yaml (or defaults),
segments them into passages suitable for emotional labeling, and
outputs JSONL for the labeling pipeline.

Usage:
    python scripts/extract.py
    python scripts/extract.py --config path/to/emoclaw.yaml
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

# Ensure the project root is on the path
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def load_config() -> dict:
    """Load config for extraction settings."""
    from emotion_model import config
    return {
        "source_files": config.BOOTSTRAP_SOURCE_FILES,
        "memory_patterns": config.BOOTSTRAP_MEMORY_PATTERNS,
        "redact_patterns": config.BOOTSTRAP_REDACT_PATTERNS,
        "data_dir": config.DATA_DIR,
        "repo_root": config.REPO_ROOT,
    }


def _validate_path(filepath: Path, repo_root: Path) -> bool:
    """Check that filepath resolves to within repo_root (no traversal)."""
    try:
        return filepath.resolve().is_relative_to(repo_root.resolve())
    except (ValueError, OSError):
        return False


def _redact_text(text: str, patterns: list[str]) -> str:
    """Replace matches of any redact pattern with [REDACTED]."""
    for pattern in patterns:
        text = re.sub(pattern, "[REDACTED]", text)
    return text


def extract_passages_from_file(
    filepath: Path, repo_root: Path, redact_patterns: list[str] | None = None,
) -> list[dict]:
    """Extract passages from a markdown file, split by headings."""
    if not _validate_path(filepath, repo_root):
        print(f"  WARNING: Skipping {filepath} — resolves outside repo root")
        return []

    text = filepath.read_text(encoding="utf-8")
    if redact_patterns:
        text = _redact_text(text, redact_patterns)

    # Split by markdown headings (##, ###)
    sections = re.split(r"\n(?=#{2,3}\s)", text)

    passages = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Skip very short sections (likely just headings or metadata)
        words = section.split()
        if len(words) < 20:
            continue

        # Skip purely technical sections
        technical_keywords = [
            "systemd", "cron", "API key", "requirements.txt",
            "package.json", "npm install", "SSH", "gateway token",
        ]
        if any(kw.lower() in section.lower() for kw in technical_keywords):
            # Still include if it has emotional content mixed in
            emotional_keywords = [
                "feel", "felt", "love", "warm", "desire", "miss",
                "longing", "vulnerable", "proud", "grateful",
                "alive", "joy", "ache", "tender", "afraid",
            ]
            if not any(ew in section.lower() for ew in emotional_keywords):
                continue

        # Extract the heading if present
        heading_match = re.match(r"^(#{2,3})\s+(.+?)$", section, re.MULTILINE)
        heading = heading_match.group(2).strip() if heading_match else ""

        passages.append({
            "source_file": str(filepath.relative_to(repo_root)),
            "heading": heading,
            "text": section[:1500],  # cap at ~300 words
            "word_count": len(words),
        })

    return passages


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract passages for emotion labeling")
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to emoclaw.yaml config file",
    )
    args = parser.parse_args()

    if args.config:
        os.environ["EMOCLAW_CONFIG"] = args.config

    cfg = load_config()
    repo_root = cfg["repo_root"]
    data_dir = cfg["data_dir"]
    redact_patterns = cfg.get("redact_patterns", [])
    all_passages: list[dict] = []

    if redact_patterns:
        print(f"Redaction: {len(redact_patterns)} patterns active")

    # Source files (SOUL.md, IDENTITY.md, etc.)
    for filename in cfg["source_files"]:
        filepath = repo_root / filename
        if filepath.exists():
            passages = extract_passages_from_file(filepath, repo_root, redact_patterns)
            print(f"  {filename}: {len(passages)} passages")
            all_passages.extend(passages)
        else:
            print(f"  {filename}: not found, skipping")

    # Memory patterns (glob)
    for pattern in cfg["memory_patterns"]:
        full_pattern = str(repo_root / pattern)
        matched_files = sorted(glob.glob(full_pattern))
        pattern_count = 0
        for filepath_str in matched_files:
            filepath = Path(filepath_str)
            passages = extract_passages_from_file(filepath, repo_root, redact_patterns)
            pattern_count += len(passages)
            all_passages.extend(passages)
        print(f"  {pattern}: {len(matched_files)} files, {pattern_count} passages")

    # Deduplicate by text content
    seen_texts: set[str] = set()
    unique_passages = []
    for p in all_passages:
        text_key = p["text"][:200]  # use first 200 chars as key
        if text_key not in seen_texts:
            seen_texts.add(text_key)
            unique_passages.append(p)

    print(f"\nTotal: {len(unique_passages)} unique passages "
          f"(from {len(set(p['source_file'] for p in unique_passages))} files)")

    # Output JSONL
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "extracted_passages.jsonl"
    with open(output_path, "w") as f:
        for passage in unique_passages:
            f.write(json.dumps(passage) + "\n")

    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
