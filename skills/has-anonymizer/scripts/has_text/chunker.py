#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Text chunking with sentence-boundary awareness.

Splits long text into chunks that fit within the model's context window,
ensuring cuts happen at sentence boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Optional

# Default max tokens per chunk (conservative, leaves room for prompt overhead + output)
DEFAULT_MAX_CHUNK_TOKENS = 3000

# Sentence boundary pattern: split on Chinese/English sentence-ending punctuation
# Priority: paragraph break > period/exclamation/question > semicolon > comma
_SENTENCE_BOUNDARIES = re.compile(
    r"(?<=[\n])"           # newline (paragraph break)
    r"|(?<=[。！？!?])"    # Chinese/English sentence enders
    r"|(?<=[；;])"         # semicolons
)

# Fallback: split on any punctuation including commas
_FALLBACK_BOUNDARIES = re.compile(
    r"(?<=[，,。！？!?；;：:\n])"
)


@dataclass
class TextChunk:
    """A chunk of text with its position metadata."""
    text: str
    index: int          # 0-based chunk index
    start_char: int     # character offset in original text
    end_char: int       # character offset end (exclusive)
    token_count: int    # estimated token count


def take_chunk(
    text: str,
    count_tokens: Callable[[str], int],
    max_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    *,
    index: int = 0,
    start_char: int = 0,
) -> Optional[TextChunk]:
    """Return the next chunk from text that fits within max_tokens."""
    if not text:
        return None

    total_tokens = count_tokens(text)
    if total_tokens <= max_tokens:
        return TextChunk(
            text=text,
            index=index,
            start_char=start_char,
            end_char=start_char + len(text),
            token_count=total_tokens,
        )

    # Estimate character position for max_tokens
    # Use ratio: chars_per_token ≈ len(text) / total_tokens
    chars_per_token = len(text) / total_tokens
    estimated_chars = int(max_tokens * chars_per_token)
    # Add a small buffer to search around the boundary
    search_end = min(estimated_chars + 50, len(text))
    search_text = text[:search_end]

    # Find the best split point
    split_pos = _find_split_point(search_text, count_tokens, max_tokens)

    if split_pos <= 0:
        # Emergency: hard cut at estimated position
        split_pos = max(1, estimated_chars)

    chunk_text_str = text[:split_pos]
    chunk_tokens = count_tokens(chunk_text_str)

    return TextChunk(
        text=chunk_text_str,
        index=index,
        start_char=start_char,
        end_char=start_char + split_pos,
        token_count=chunk_tokens,
    )


def chunk_text(
    text: str,
    count_tokens: Callable[[str], int],
    max_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
) -> List[TextChunk]:
    """Split text into chunks that fit within max_tokens.

    Strategy:
    1. If the entire text fits, return as single chunk.
    2. Otherwise, find the last sentence boundary before max_tokens.
    3. If no sentence boundary found, fall back to punctuation boundary.
    4. If still no boundary, hard-cut at max_tokens worth of characters.

    Args:
        text: The text to chunk.
        count_tokens: Function that returns token count for a string.
        max_tokens: Maximum tokens per chunk.

    Returns:
        List of TextChunk objects.
    """
    if not text or not text.strip():
        return []

    chunks: List[TextChunk] = []
    remaining = text
    offset = 0
    chunk_idx = 0

    while remaining:
        chunk = take_chunk(
            remaining,
            count_tokens,
            max_tokens,
            index=chunk_idx,
            start_char=offset,
        )
        if chunk is None:
            break

        chunks.append(chunk)
        offset = chunk.end_char
        remaining = remaining[len(chunk.text):]
        chunk_idx += 1

    return chunks


def _find_split_point(
    text: str,
    count_tokens: Callable[[str], int],
    max_tokens: int,
) -> int:
    """Find the best split point in text that stays within max_tokens.

    Tries sentence boundaries first, then fallback punctuation.

    Returns:
        Character position to split at, or 0 if no good split found.
    """
    # Find all sentence boundaries
    boundaries = [m.start() for m in _SENTENCE_BOUNDARIES.finditer(text)]

    # Try sentence boundaries (from right to left)
    best = _try_boundaries(boundaries, text, count_tokens, max_tokens)
    if best > 0:
        return best

    # Fallback: try punctuation boundaries
    boundaries = [m.start() for m in _FALLBACK_BOUNDARIES.finditer(text)]
    best = _try_boundaries(boundaries, text, count_tokens, max_tokens)
    if best > 0:
        return best

    return 0


def _try_boundaries(
    boundaries: List[int],
    text: str,
    count_tokens: Callable[[str], int],
    max_tokens: int,
) -> int:
    """Try split points from rightmost boundary, return first that fits."""
    for pos in reversed(boundaries):
        if pos <= 0:
            continue
        candidate = text[:pos]
        if count_tokens(candidate) <= max_tokens:
            return pos
    return 0
