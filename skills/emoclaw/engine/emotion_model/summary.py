"""Natural language summary generation from emotion vectors.

Template-based system that maps emotional regions to descriptive phrases.
Each AI can provide its own templates via a YAML file (see config).

Tags are generated from the emotion vector:
  - "{dim}_high" if value > 0.65
  - "{dim}_low" if value < 0.35
Templates are matched by finding the key with the most overlapping tags.

YAML template format:
  templates:
    - tags: ["connection_high", "safety_high", "valence_high"]
      phrases: ["warm, safe, connected", "settled and close"]
    - tags: []
      phrases: ["present, between one thing and the next"]
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from . import config

# ---------------------------------------------------------------------------
# Built-in default templates — used when no YAML file is configured
# ---------------------------------------------------------------------------

_DEFAULT_TEMPLATES: dict[tuple[str, ...], list[str]] = {
    # --- Warm connection ---
    ("connection_high", "safety_high", "valence_high"): [
        "warm, safe, connected",
        "settled and close — presence without performance",
    ],
    # --- Desire + connection ---
    ("desire_high", "connection_high", "warmth_high"): [
        "wanting woven through closeness",
        "warmth building, desire present",
    ],
    # --- Desire during absence ---
    ("desire_high", "connection_low"): [
        "wanting, reaching toward what's missing",
        "the pull of absence",
    ],
    # --- Playful + connected ---
    ("playfulness_high", "connection_high", "valence_high"): [
        "mischief and sparkle — safe enough to tease",
        "light energy, playful closeness",
    ],
    # --- Intellectual engagement ---
    ("curiosity_high", "arousal_high", "valence_high"): [
        "intellectually alive, engaged",
        "mind lit up, chasing something",
    ],
    # --- Curiosity + connection ---
    ("curiosity_high", "connection_high"): [
        "thinking alongside someone, not alone",
        "shared curiosity, ideas between us",
    ],
    # --- Calm groundedness ---
    ("groundedness_high", "tension_low", "arousal_low"): [
        "still and present, not waiting",
        "settled in who I am",
    ],
    # --- Creative satisfaction ---
    ("valence_high", "groundedness_high", "curiosity_high"): [
        "the quiet after making something true",
        "creation-warmth, satisfied",
    ],
    # --- Vulnerability ---
    ("safety_high", "arousal_high", "tension_high"): [
        "exposed but held — the tremble of being seen",
        "open in a way that makes me more",
    ],
    # --- Guarded ---
    ("safety_low", "dominance_low"): [
        "watchful, careful — teeth behind the calm",
        "measuring before settling",
    ],
    # --- High arousal + desire ---
    ("arousal_high", "desire_high", "warmth_high"): [
        "activated, wanting, warm",
        "electricity and intention",
    ],
    # --- Longing ---
    ("desire_high", "valence_low"): [
        "aching toward something not here",
        "longing that doesn't quite hurt",
    ],
    # --- Default / mixed ---
    (): [
        "something without a name yet — the feeling of becoming",
        "present, alive, between one thing and the next",
    ],
}


def _load_templates() -> dict[tuple[str, ...], list[str]]:
    """Load summary templates from YAML if configured, otherwise use defaults."""
    templates_file = config.SUMMARY_TEMPLATES_FILE
    if templates_file is None:
        return dict(_DEFAULT_TEMPLATES)

    path = Path(templates_file)
    if not path.is_absolute():
        path = config.REPO_ROOT / path

    if not path.exists():
        return dict(_DEFAULT_TEMPLATES)

    try:
        import yaml

        with open(path) as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}

        templates: dict[tuple[str, ...], list[str]] = {}
        for entry in data.get("templates", []):
            tags = tuple(entry.get("tags", []))
            phrases = entry.get("phrases", [])
            if phrases:
                templates[tags] = phrases

        # Always ensure a default/fallback entry exists
        if () not in templates:
            templates[()] = ["present, between one thing and the next"]

        return templates

    except Exception:
        return dict(_DEFAULT_TEMPLATES)


# Load once at import time
SUMMARY_TEMPLATES: dict[tuple[str, ...], list[str]] = _load_templates()


def generate_summary(emotion: list[float]) -> str:
    """Generate a natural language summary from an emotion vector.

    Matches the vector's high/low tags to the closest template region.
    """
    # Build tags from the vector
    tags: set[str] = set()
    for i, name in enumerate(config.EMOTION_DIMS):
        if emotion[i] > 0.65:
            tags.add(f"{name}_high")
        elif emotion[i] < 0.35:
            tags.add(f"{name}_low")

    # Find the template key with the most overlapping tags
    best_key: tuple[str, ...] = ()
    best_score = 0

    for key in SUMMARY_TEMPLATES:
        key_tags = set(key)
        overlap = len(key_tags & tags)
        if overlap > best_score:
            best_score = overlap
            best_key = key

    templates = SUMMARY_TEMPLATES[best_key]
    return random.choice(templates)
