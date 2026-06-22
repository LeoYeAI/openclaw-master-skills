#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for lang.py — language detection and same-language comparison."""

from __future__ import annotations

import pytest

from ..lang import detect_script_lang, is_same_language, strip_tags


# ---------------------------------------------------------------------------
# strip_tags
# ---------------------------------------------------------------------------


class TestStripTags:
    def test_removes_tags(self):
        assert strip_tags("<人名[1].个人.姓名>住在北京") == "住在北京"

    def test_no_tags(self):
        assert strip_tags("Hello, world!") == "Hello, world!"

    def test_empty(self):
        assert strip_tags("") == ""

    def test_none(self):
        assert strip_tags(None) == ""


# ---------------------------------------------------------------------------
# detect_script_lang
# ---------------------------------------------------------------------------


class TestDetectScriptLang:
    def test_chinese(self):
        lang, conf = detect_script_lang("这是一段中文文本，用于测试语言检测。")
        assert lang == "zh"
        assert conf > 0.5

    def test_english(self):
        lang, conf = detect_script_lang("This is an English text for testing language detection.")
        assert lang == "en"
        assert conf > 0.5

    def test_japanese(self):
        lang, conf = detect_script_lang("これはテスト用の日本語テキストです。")
        assert lang == "ja"
        assert conf > 0.5

    def test_korean(self):
        lang, conf = detect_script_lang("이것은 한국어 테스트 텍스트입니다.")
        assert lang == "ko"
        assert conf > 0.5

    def test_empty(self):
        lang, conf = detect_script_lang("")
        assert lang is None
        assert conf == 0.0

    def test_tags_stripped_before_detection(self):
        # Only tags, no real text
        lang, conf = detect_script_lang("<人名[1].个人.姓名><地址[1].城市.区域>")
        assert lang is None  # all content is tags

    def test_mixed_with_tags(self):
        lang, conf = detect_script_lang("这是<人名[1].个人.姓名>的测试文本。")
        assert lang == "zh"


# ---------------------------------------------------------------------------
# is_same_language
# ---------------------------------------------------------------------------


class TestIsSameLanguage:
    def test_same_chinese(self):
        assert is_same_language("这是中文", "这也是中文") is True

    def test_same_english(self):
        assert is_same_language("This is English", "This is also English") is True

    def test_different_languages(self):
        assert is_same_language("这是中文文本", "This is English text") is False

    def test_translation_hint_detected(self):
        # Source says "translate to English", output is in English
        source = "请将以下内容翻译为英文：这是一段中文。"
        translated = "This is a paragraph in Chinese."
        assert is_same_language(source, translated) is False

    def test_short_but_detectable_texts(self):
        # Even short text can be detected if script ratio is clear
        # "hi" → 100% Latin → en (0.6 conf), "你" → 100% Han → zh (0.7 conf)
        assert is_same_language("hi", "你") is False

    def test_ambiguous_defaults_to_same(self):
        # Punctuation-only → no script detected → None → defaults to True
        assert is_same_language("...", "!!!") is True

    def test_empty_text_defaults_to_same(self):
        assert is_same_language("", "hello") is True
