#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for chunker.py — sentence-boundary-aware text splitting."""

from __future__ import annotations

import pytest

from ..chunker import TextChunk, chunk_text, take_chunk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_tokens_by_chars(text: str) -> int:
    """Simple token counter: 1 token per character (for deterministic testing)."""
    return len(text)


def _count_tokens_by_words(text: str) -> int:
    """Token counter that approximates word-level tokenization."""
    return max(1, len(text.split()))


# ---------------------------------------------------------------------------
# take_chunk
# ---------------------------------------------------------------------------


class TestTakeChunk:
    def test_empty_text_returns_none(self):
        assert take_chunk("", _count_tokens_by_chars, max_tokens=100) is None

    def test_short_text_fits_in_one_chunk(self):
        text = "Hello, world!"
        chunk = take_chunk(text, _count_tokens_by_chars, max_tokens=100)
        assert chunk is not None
        assert chunk.text == text
        assert chunk.index == 0
        assert chunk.start_char == 0
        assert chunk.end_char == len(text)
        assert chunk.token_count == len(text)

    def test_exact_fit_returns_full_text(self):
        text = "12345"
        chunk = take_chunk(text, _count_tokens_by_chars, max_tokens=5)
        assert chunk is not None
        assert chunk.text == text

    def test_split_at_sentence_boundary(self):
        text = "First sentence。Second sentence。Third sentence。"
        chunk = take_chunk(text, _count_tokens_by_chars, max_tokens=20)
        assert chunk is not None
        # Should cut at the first sentence boundary that fits
        assert chunk.text.endswith("。")
        assert len(chunk.text) <= 20

    def test_start_char_offset(self):
        text = "Hello, world!"
        chunk = take_chunk(text, _count_tokens_by_chars, max_tokens=100, start_char=50)
        assert chunk is not None
        assert chunk.start_char == 50
        assert chunk.end_char == 50 + len(text)

    def test_custom_index(self):
        text = "Hello"
        chunk = take_chunk(text, _count_tokens_by_chars, max_tokens=100, index=3)
        assert chunk is not None
        assert chunk.index == 3


# ---------------------------------------------------------------------------
# chunk_text
# ---------------------------------------------------------------------------


class TestChunkText:
    def test_empty_text(self):
        assert chunk_text("", _count_tokens_by_chars) == []

    def test_whitespace_only(self):
        assert chunk_text("   ", _count_tokens_by_chars) == []

    def test_single_chunk(self):
        text = "Short text."
        chunks = chunk_text(text, _count_tokens_by_chars, max_tokens=100)
        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].index == 0

    def test_multiple_chunks_chinese(self):
        # 3 Chinese sentences, each ~10 chars, with max_tokens=15
        text = "第一句话结束。第二句话结束。第三句话结束。"
        chunks = chunk_text(text, _count_tokens_by_chars, max_tokens=10)
        assert len(chunks) >= 2
        # All chunks concatenated should equal original text
        reconstructed = "".join(c.text for c in chunks)
        assert reconstructed == text

    def test_chunk_indices_are_sequential(self):
        text = "A。B。C。D。E。F。G。H。"
        chunks = chunk_text(text, _count_tokens_by_chars, max_tokens=5)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_chunk_offsets_are_contiguous(self):
        text = "First sentence。Second sentence。Third sentence。Fourth sentence。"
        chunks = chunk_text(text, _count_tokens_by_chars, max_tokens=20)
        assert len(chunks) >= 2
        for i in range(1, len(chunks)):
            assert chunks[i].start_char == chunks[i - 1].end_char

    def test_reconstructed_text_matches_original(self):
        text = "这是第一段。\n这是第二段，比较长一些。\n这是第三段！\n第四段也有内容？"
        chunks = chunk_text(text, _count_tokens_by_chars, max_tokens=12)
        reconstructed = "".join(c.text for c in chunks)
        assert reconstructed == text

    def test_newline_boundary_preferred(self):
        text = "First paragraph.\nSecond paragraph.\nThird paragraph."
        chunks = chunk_text(text, _count_tokens_by_chars, max_tokens=20)
        # Should prefer newline as split point
        if len(chunks) >= 2:
            assert chunks[0].text.endswith("\n") or chunks[0].text.endswith(".")

    def test_fallback_to_comma_boundary(self):
        # Long text with only commas as boundaries
        text = "词一，词二，词三，词四，词五，词六，词七，词八"
        chunks = chunk_text(text, _count_tokens_by_chars, max_tokens=10)
        assert len(chunks) >= 2
        reconstructed = "".join(c.text for c in chunks)
        assert reconstructed == text

    def test_hard_cut_when_no_boundaries(self):
        # Continuous text with no punctuation
        text = "a" * 30
        chunks = chunk_text(text, _count_tokens_by_chars, max_tokens=10)
        assert len(chunks) >= 3
        reconstructed = "".join(c.text for c in chunks)
        assert reconstructed == text
