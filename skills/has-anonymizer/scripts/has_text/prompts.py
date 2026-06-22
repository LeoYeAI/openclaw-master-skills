#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt template builders for has_text_model's 6 atomic capabilities.

CRITICAL: These templates must be matched character-for-character exactly,
as the model was trained on these precise templates.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


def _types_json(types: List[str]) -> str:
    """Serialize entity types list to JSON array string (no spaces)."""
    return json.dumps(types, ensure_ascii=False, separators=(",", ":"))


# ======================================================================
# NER
# ======================================================================


def build_ner_messages(text: str, types: List[str]) -> List[Dict[str, str]]:
    """Build messages for NER (single turn).

    Args:
        text: The user's complete original input text (may include instructions).
        types: Entity types to recognize, e.g. ["人名", "地址", "组织"].

    Returns:
        Single-message list for chat API.
    """
    content = (
        f"Recognize the following entity types in the text.\n"
        f"Specified types:{_types_json(types)}\n"
        f"<text>{text}</text>"
    )
    return [{"role": "user", "content": content}]


# ======================================================================
# Hide without mapping (hide_without) — two turns
# ======================================================================


def build_hide_without_messages(
    text: str,
    types: List[str],
    ner_result: str,
) -> List[Dict[str, str]]:
    """Build messages for hide_without (two turns).

    Args:
        text: The user's original text.
        types: Entity types to recognize.
        ner_result: The NER output from the model (JSON string).

    Returns:
        Three-message list (user, assistant, user) for chat API.
    """
    turn1_user = (
        f"Recognize the following entity types in the text.\n"
        f"Specified types:{_types_json(types)}\n"
        f"<text>{text}</text>"
    )
    turn2_user = "Replace the above-mentioned entity types in the text."

    return [
        {"role": "user", "content": turn1_user},
        {"role": "assistant", "content": ner_result},
        {"role": "user", "content": turn2_user},
    ]


# ======================================================================
# Hide with mapping (hide_with) — two turns
# ======================================================================


def build_hide_with_messages(
    text: str,
    types: List[str],
    ner_result: str,
    mapping: Dict[str, List[str]],
) -> List[Dict[str, str]]:
    """Build messages for hide_with (two turns).

    Args:
        text: The user's original text.
        types: Entity types to recognize.
        ner_result: The NER output from the model (JSON string).
        mapping: Existing mapping dictionary {tag: [original_values]}.

    Returns:
        Three-message list (user, assistant, user) for chat API.
    """
    turn1_user = (
        f"Recognize the following entity types in the text.\n"
        f"Specified types:{_types_json(types)}\n"
        f"<text>{text}</text>"
    )
    mapping_json = json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))
    turn2_user = (
        f"Replace the above-mentioned entity types in the text "
        f"according to the existing mapping pairs:{mapping_json}"
    )

    return [
        {"role": "user", "content": turn1_user},
        {"role": "assistant", "content": ner_result},
        {"role": "user", "content": turn2_user},
    ]


# ======================================================================
# Pair — extract mapping from original/anonymized pair (single turn)
# ======================================================================


def build_pair_messages(
    original_text: str,
    anonymized_text: str,
) -> List[Dict[str, str]]:
    """Build messages for pair extraction (single turn).

    Args:
        original_text: The original text.
        anonymized_text: The anonymized text containing tags.

    Returns:
        Single-message list for chat API.
    """
    content = (
        f"<original>{original_text}</original>\n"
        f"<anonymized>{anonymized_text}</anonymized>\n"
        f"Extract the mapping from anonymized entities to original entities."
    )
    return [{"role": "user", "content": content}]


# ======================================================================
# Split — split composite anonymized keys (single turn)
# ======================================================================


def build_split_messages(
    composite_mapping: List[Dict[str, List[str]]],
) -> List[Dict[str, str]]:
    """Build messages for split (single turn).

    Args:
        composite_mapping: List of {composite_key: [original_values]}.

    Returns:
        Single-message list for chat API.
    """
    mapping_json = json.dumps(composite_mapping, ensure_ascii=False, separators=(",", ":"))
    content = (
        f"Split each composite anonymized key into atomic keys.\n"
        f"Composite mapping:\n"
        f"{mapping_json}"
    )
    return [{"role": "user", "content": content}]


# ======================================================================
# Seek — restore anonymized text (single turn)
# ======================================================================


def build_seek_messages(
    mapping: Dict[str, List[str]],
    text_with_tags: str,
) -> List[Dict[str, str]]:
    """Build messages for seek restoration (single turn).

    Args:
        mapping: Mapping dictionary {tag: [original_values]}.
        text_with_tags: Anonymized text containing tags to restore.

    Returns:
        Single-message list for chat API.
    """
    mapping_json = json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))
    content = (
        f"The mapping from anonymized entities to original entities:\n"
        f"{mapping_json}\n"
        f"Restore the original text based on the above mapping:\n"
        f"{text_with_tags}"
    )
    return [{"role": "user", "content": content}]
