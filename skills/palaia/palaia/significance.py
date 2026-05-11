"""Significance tagging with auto-detection (Issue #70).

Standard taxonomy of significance tags for memory entries.
Heuristic detection via keyword and pattern matching.
"""

from __future__ import annotations

import re

# Canonical significance tags
SIGNIFICANCE_TAGS: tuple[str, ...] = (
    "decision",
    "lesson",
    "surprise",
    "commitment",
    "correction",
    "preference",
    "fact",
)

# Patterns per category: list of (compiled_regex, weight).
# Weight is unused for now but allows future ranking.
_PATTERNS: dict[str, list[tuple[re.Pattern[str], float]]] = {
    "decision": [
        (re.compile(r"\b(decided|decision|entschieden|entscheidung|chose|chosen|we\s+went\s+with)\b", re.I), 1.0),
        (re.compile(r"\b(will\s+use|going\s+with|picked|selected|opted\s+for)\b", re.I), 0.8),
        (re.compile(r"\b(wir\s+nehmen|wir\s+nutzen|festgelegt|beschlossen)\b", re.I), 0.9),
        (re.compile(r"\bADR\b", re.I), 1.0),
    ],
    "lesson": [
        (re.compile(r"\b(learned|lesson|takeaway|erkenntnis|gelernt|learning)\b", re.I), 1.0),
        (re.compile(r"\b(never\s+again|next\s+time|in\s+future|in\s+zukunft)\b", re.I), 0.9),
        (re.compile(r"\b(mistake\s+was|fehler\s+war|turned\s+out|stellte\s+sich\s+heraus)\b", re.I), 0.8),
        (re.compile(r"\b(insight|einsicht|realization)\b", re.I), 0.8),
    ],
    "surprise": [
        (re.compile(r"\b(surprising|unexpected|unerwartet|überraschend|didn't\s+expect)\b", re.I), 1.0),
        (re.compile(r"\b(turns\s+out|it\s+seems|actually|tatsächlich)\b", re.I), 0.6),
        (re.compile(r"\b(plot\s+twist|who\s+knew|wow)\b", re.I), 0.7),
    ],
    "commitment": [
        (re.compile(r"\b(promise|commit|commitment|versprechen|zusage|verpflichtung)\b", re.I), 1.0),
        (re.compile(r"\b(will\s+do|must\s+do|agreed\s+to|zugesagt|vereinbart)\b", re.I), 0.8),
        (re.compile(r"\b(deadline|due\s+by|bis\s+zum|fällig)\b", re.I), 0.7),
        (re.compile(r"\b(i\s+will|we\s+will|ich\s+werde|wir\s+werden)\b", re.I), 0.5),
    ],
    "correction": [
        (re.compile(r"\b(correction|corrected|korrektur|korrigiert|was\s+wrong|war\s+falsch)\b", re.I), 1.0),
        (re.compile(r"\b(fix|fixed|gefixt|behoben|actually\s+it's|eigentlich\s+ist)\b", re.I), 0.7),
        (re.compile(r"\b(retract|widerrufen|update:\s|nachtrag)\b", re.I), 0.8),
        (re.compile(r"\b(nicht\s+wie\s+gedacht|not\s+as\s+expected)\b", re.I), 0.8),
    ],
    "preference": [
        (re.compile(r"\b(prefer|preference|bevorzug|präferenz|like\s+better|lieber)\b", re.I), 1.0),
        (re.compile(r"\b(favorite|favourit|lieblings|my\s+go-to)\b", re.I), 0.8),
        (re.compile(r"\b(always\s+use|immer\s+nutzen|standard\s+is|default\s+ist)\b", re.I), 0.7),
        (re.compile(r"\b(i\s+like|i\s+don't\s+like|mag\s+ich|mag\s+ich\s+nicht)\b", re.I), 0.6),
    ],
    "fact": [
        (re.compile(r"\b(fact|tatsache|note\s+to\s+self|merke|remember\s+that)\b", re.I), 1.0),
        (re.compile(r"\b(config|konfiguration|password|passwort|token)\b", re.I), 0.8),
        (re.compile(r"api[_\s-]?key", re.I), 0.8),
        (re.compile(r"\b(located\s+at|zu\s+finden|ip\s+address|version\s+is)\b", re.I), 0.7),
        (re.compile(r"\b(specification|spezifikation|requirement|anforderung)\b", re.I), 0.7),
    ],
}


def detect_significance(text: str) -> list[str]:
    """Detect significance tags from text content.

    Uses keyword and pattern matching. Returns a list of matching
    significance tag names (may be empty).

    Args:
        text: The text content to analyze.

    Returns:
        List of significance tag strings, e.g. ["decision", "lesson"].
    """
    if not text or not text.strip():
        return []

    detected: list[str] = []
    for tag, patterns in _PATTERNS.items():
        for regex, _weight in patterns:
            if regex.search(text):
                detected.append(tag)
                break  # One match per category is enough

    return detected


def significance_weight(tags: list[str] | None) -> float:
    """Calculate GC significance weight from tags.

    Entries with significance tags get a higher weight (survive GC longer).
    Formula: 1.0 + 0.2 * count_of_significance_tags_present

    Args:
        tags: List of entry tags (may include non-significance tags).

    Returns:
        Weight >= 1.0. Higher = more important for GC retention.
    """
    if not tags:
        return 1.0
    sig_set = set(SIGNIFICANCE_TAGS)
    count = sum(1 for t in tags if t in sig_set)
    return 1.0 + 0.2 * count
