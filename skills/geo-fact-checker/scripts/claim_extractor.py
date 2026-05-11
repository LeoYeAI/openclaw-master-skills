"""
Claim extraction helper for the geo-fact-checker skill.

This module provides simple utilities to extract and represent factual claims
from a block of text. It is intentionally lightweight so it can be adapted
or extended by higher-level agents as needed.

The skill using this script is responsible for deciding which claims to
prioritize for verification, how to search for evidence, and how to apply
corrections in the user's content.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List
import re


class ClaimType(str, Enum):
    NUMERIC_STATISTIC = "numeric-statistic"
    DATE = "date"
    RANKING = "ranking"
    COMPETITOR_INFO = "competitor-info"
    QUOTE = "quote"
    GENERAL_FACT = "general-fact"


@dataclass
class Claim:
    id: str
    text: str
    claim_type: ClaimType


NUMERIC_PATTERN = re.compile(r"\b\d[\d,]*(?:\.\d+)?\b")
DATE_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
RANKING_PATTERN = re.compile(r"\b(#?\d+|top\s+\d+|number\s+one|no\.\s*\d+)\b", re.IGNORECASE)


def guess_claim_type(sentence: str) -> ClaimType:
    """Heuristic classification of a sentence into a claim type."""
    lowered = sentence.lower()

    if RANKING_PATTERN.search(sentence):
        return ClaimType.RANKING
    if any(word in lowered for word in ["market share", "leader", "largest", "leading"]):
        return ClaimType.RANKING
    if DATE_PATTERN.search(sentence):
        return ClaimType.DATE
    if NUMERIC_PATTERN.search(sentence):
        return ClaimType.NUMERIC_STATISTIC
    if any(word in lowered for word in ["according to", "report", "study", "research"]):
        return ClaimType.QUOTE
    if any(word in lowered for word in ["competitor", "alternative", "vs ", "versus"]):
        return ClaimType.COMPETITOR_INFO
    return ClaimType.GENERAL_FACT


def split_into_sentences(text: str) -> List[str]:
    """
    Very simple sentence splitter based on punctuation.
    This does not handle all edge cases but is sufficient for small helper usage.
    """
    # Replace newlines with spaces to avoid fragmentation
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []

    # Split on ., ?, ! while keeping simple structure
    parts = re.split(r"([\.!?])", cleaned)
    sentences: List[str] = []
    buffer = ""
    for part in parts:
        if part in [".", "?", "!"]:
            buffer += part
            sentence = buffer.strip()
            if sentence:
                sentences.append(sentence)
            buffer = ""
        else:
            buffer += part
    if buffer.strip():
        sentences.append(buffer.strip())
    return sentences


def extract_candidate_claims(text: str, min_length: int = 20) -> List[Claim]:
    """
    Extract a list of candidate claims from a text block.

    This function is intentionally conservative and focuses on sentences
    that are likely to contain non-trivial factual content: numbers,
    dates, rankings, or explicit references to research and reports.
    """
    sentences = split_into_sentences(text)
    claims: List[Claim] = []

    for idx, sentence in enumerate(sentences, start=1):
        s = sentence.strip()
        if len(s) < min_length:
            continue

        # Only keep sentences that contain clear factual markers
        if not (
            NUMERIC_PATTERN.search(s)
            or DATE_PATTERN.search(s)
            or RANKING_PATTERN.search(s)
            or any(
                kw in s.lower()
                for kw in [
                    "according to",
                    "report",
                    "study",
                    "research",
                    "market share",
                    "leader",
                    "largest",
                    "top",
                ]
            )
        ):
            continue

        claim_type = guess_claim_type(s)
        claim_id = f"C{idx}"
        claims.append(Claim(id=claim_id, text=s, claim_type=claim_type))

    return claims


__all__ = [
    "ClaimType",
    "Claim",
    "extract_candidate_claims",
    "split_into_sentences",
    "guess_claim_type",
]

