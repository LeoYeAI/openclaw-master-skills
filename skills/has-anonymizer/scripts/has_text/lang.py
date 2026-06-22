#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Language detection for determining if two texts are in the same language.

Self-contained implementation using Unicode script heuristics.
No external dependencies (langid, etc.).
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Tuple

# Strip anonymized tags before detecting language
_TAG_RE = re.compile(r"<[^<>\[\]]+\[\d+\]\.[^<>\[\].]+\.[^<>\[\].]+>")


def strip_tags(text: str) -> str:
    """Remove anonymized tags from text."""
    return _TAG_RE.sub("", text or "")


def _script_counts(text: str) -> Dict[str, int]:
    """Count characters by Unicode script."""
    counts = {
        "latin": 0,
        "han": 0,
        "hiragana": 0,
        "katakana": 0,
        "hangul": 0,
        "cyrillic": 0,
        "arabic": 0,
        "devanagari": 0,
    }
    for ch in text:
        code = ord(ch)
        if 65 <= code <= 90 or 97 <= code <= 122:
            counts["latin"] += 1
        elif 0x4E00 <= code <= 0x9FFF:
            counts["han"] += 1
        elif 0x3040 <= code <= 0x309F:
            counts["hiragana"] += 1
        elif 0x30A0 <= code <= 0x30FF:
            counts["katakana"] += 1
        elif 0xAC00 <= code <= 0xD7AF:
            counts["hangul"] += 1
        elif 0x0400 <= code <= 0x04FF:
            counts["cyrillic"] += 1
        elif 0x0600 <= code <= 0x06FF:
            counts["arabic"] += 1
        elif 0x0900 <= code <= 0x097F:
            counts["devanagari"] += 1
    return counts


def detect_script_lang(text: str) -> Tuple[Optional[str], float]:
    """Detect primary language of text using script heuristics.

    Returns:
        (language_code, confidence)
        Language codes: "zh", "ja", "ko", "en", "ru", "ar", "hi", or None
    """
    cleaned = strip_tags(text).strip()
    if not cleaned:
        return None, 0.0

    counts = _script_counts(cleaned)
    total = sum(counts.values()) or 1
    ratios = {k: v / total for k, v in counts.items()}

    # Japanese: significant hiragana/katakana presence
    if ratios["hiragana"] + ratios["katakana"] > 0.15 and ratios["han"] < 0.6:
        return "ja", 0.8

    # Korean: significant hangul
    if ratios["hangul"] > 0.2:
        return "ko", 0.8

    # Chinese: significant han, low Japanese kana
    if ratios["han"] > 0.2 and ratios["hiragana"] + ratios["katakana"] < 0.1:
        return "zh", 0.7

    # Cyrillic-based (Russian, etc.)
    if ratios["cyrillic"] > 0.2:
        return "ru", 0.75

    # Arabic
    if ratios["arabic"] > 0.2:
        return "ar", 0.75

    # Devanagari (Hindi, etc.)
    if ratios["devanagari"] > 0.2:
        return "hi", 0.75

    # Latin-based (English, French, German, etc.)
    if ratios["latin"] > 0.4:
        return "en", 0.6

    return None, 0.0


# Instruction patterns that hint at target language
_HINT_PATTERNS = [
    re.compile(r"翻译(为|成)\s*([\w\u4e00-\u9fff]+)"),
    re.compile(r"请用\s*([\w\u4e00-\u9fff]+)\s*(回答|作答|输出)"),
    re.compile(r"(answer in|reply in|respond in)\s+([A-Za-z]+)", re.IGNORECASE),
    re.compile(r"translate .* to\s+([A-Za-z]+)", re.IGNORECASE),
]

_LANG_HINT_MAP: Dict[str, str] = {
    "中文": "zh", "汉语": "zh", "简体": "zh", "繁体": "zh",
    "Chinese": "zh", "Mandarin": "zh",
    "英文": "en", "英语": "en", "English": "en",
    "日文": "ja", "日语": "ja", "Japanese": "ja",
    "韩文": "ko", "韩语": "ko", "Korean": "ko",
    "法语": "fr", "French": "fr",
    "德语": "de", "German": "de",
    "俄语": "ru", "Russian": "ru",
    "西班牙语": "es", "Spanish": "es",
    "葡萄牙语": "pt", "Portuguese": "pt",
}


def _extract_target_lang_hint(text: str) -> Optional[str]:
    """Extract target language hint from translation instructions in text."""
    for pat in _HINT_PATTERNS:
        match = pat.search(text or "")
        if not match:
            continue
        token = match.group(match.lastindex or 1).strip()
        lang = _LANG_HINT_MAP.get(token) or _LANG_HINT_MAP.get(token.capitalize())
        if lang:
            return lang
    return None


def is_same_language(text_a: str, text_b: str) -> bool:
    """Determine if two texts are in the same language.

    Compares the dominant script/language of both texts.
    Also checks for translation instruction hints in text_a.

    Args:
        text_a: Original/source text (may contain translation instructions).
        text_b: Processed text to compare against.

    Returns:
        True if both texts appear to be in the same language.
    """
    lang_a, conf_a = detect_script_lang(text_a)
    lang_b, conf_b = detect_script_lang(text_b)

    # If either detection is low confidence, assume same language
    # (safer to use Tool-Seek, which has a self-check anyway)
    if lang_a is None or lang_b is None:
        return True

    if conf_a < 0.5 or conf_b < 0.5:
        return True

    # Check if text_a contains a translation instruction
    target_hint = _extract_target_lang_hint(text_a)
    if target_hint and target_hint != lang_a:
        # Source text says "translate to X" — expect text_b to be in X
        # So if text_b IS in X, it's a different language from source
        if lang_b == target_hint:
            return False

    return lang_a == lang_b
