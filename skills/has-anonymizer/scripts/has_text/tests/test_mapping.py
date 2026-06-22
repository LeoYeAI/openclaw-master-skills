#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for mapping.py — tag parsing, mapping merge, normalization, and I/O."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from collections import OrderedDict

import pytest

from ..mapping import (
    find_composite_entries,
    find_tags,
    has_tags,
    is_composite_tag,
    load_mapping,
    merge_mappings,
    normalize_mapping_dict,
    parse_json_tolerant,
    save_mapping,
)


# ---------------------------------------------------------------------------
# find_tags / has_tags
# ---------------------------------------------------------------------------


class TestFindTags:
    def test_no_tags(self):
        assert find_tags("Hello, world!") == []

    def test_single_tag(self):
        tags = find_tags("我是<人名[1].个人.姓名>，住在北京。")
        assert tags == ["<人名[1].个人.姓名>"]

    def test_multiple_tags(self):
        text = "<人名[1].个人.姓名>和<人名[2].个人.姓名>在<地址[1].城市.区域>见面。"
        tags = find_tags(text)
        assert len(tags) == 3
        assert "<人名[1].个人.姓名>" in tags
        assert "<人名[2].个人.姓名>" in tags
        assert "<地址[1].城市.区域>" in tags

    def test_english_tags(self):
        tags = find_tags("Contact <person[1].personal.name> at <phone[1].contact.mobile>.")
        assert len(tags) == 2

    def test_no_match_for_malformed(self):
        assert find_tags("<incomplete") == []
        assert find_tags("<no_bracket.a.b>") == []
        assert find_tags("<typ[x].a.b>") == []  # non-numeric index


class TestHasTags:
    def test_true_when_present(self):
        assert has_tags("<人名[1].个人.姓名>") is True

    def test_false_when_absent(self):
        assert has_tags("No tags here.") is False

    def test_false_for_empty(self):
        assert has_tags("") is False


# ---------------------------------------------------------------------------
# is_composite_tag / find_composite_entries
# ---------------------------------------------------------------------------


class TestCompositeTag:
    def test_atomic(self):
        assert is_composite_tag("<人名[1].个人.姓名>") is False

    def test_composite(self):
        assert is_composite_tag("<职务[3].职务.职务名称><人名[1].中文姓名.姓名>") is True

    def test_find_composite_entries(self):
        mapping = {
            "<人名[1].个人.姓名>": ["张三"],
            "<职务[3].职务.职务名称><人名[1].中文姓名.姓名>": ["总经理张三"],
            "<地址[1].城市.区域>": ["北京朝阳"],
        }
        atomic, composite = find_composite_entries(mapping)
        assert len(atomic) == 2
        assert len(composite) == 1
        assert "<职务[3].职务.职务名称><人名[1].中文姓名.姓名>" in composite


# ---------------------------------------------------------------------------
# merge_mappings
# ---------------------------------------------------------------------------


class TestMergeMappings:
    def test_disjoint_merge(self):
        base = {"<人名[1].a.b>": ["张三"]}
        new = {"<地址[1].c.d>": ["北京"]}
        merged = merge_mappings(base, new)
        assert len(merged) == 2
        assert merged["<人名[1].a.b>"] == ["张三"]
        assert merged["<地址[1].c.d>"] == ["北京"]

    def test_overlapping_merge_deduplicates(self):
        base = {"<人名[1].a.b>": ["张三"]}
        new = {"<人名[1].a.b>": ["张三", "三张"]}
        merged = merge_mappings(base, new)
        assert merged["<人名[1].a.b>"] == ["张三", "三张"]

    def test_base_not_mutated(self):
        base = {"<人名[1].a.b>": ["张三"]}
        original = dict(base)
        merge_mappings(base, {"<人名[1].a.b>": ["李四"]})
        assert base == original

    def test_empty_base(self):
        merged = merge_mappings({}, {"<人名[1].a.b>": ["张三"]})
        assert merged == {"<人名[1].a.b>": ["张三"]}

    def test_empty_new(self):
        base = {"<人名[1].a.b>": ["张三"]}
        merged = merge_mappings(base, {})
        assert merged == base


# ---------------------------------------------------------------------------
# normalize_mapping_dict
# ---------------------------------------------------------------------------


class TestNormalizeMappingDict:
    def test_string_value_becomes_list(self):
        result = normalize_mapping_dict({"<人名[1].a.b>": "张三"})
        assert result == {"<人名[1].a.b>": ["张三"]}

    def test_list_value_preserved(self):
        result = normalize_mapping_dict({"<人名[1].a.b>": ["张三", "李四"]})
        assert result == {"<人名[1].a.b>": ["张三", "李四"]}

    def test_deduplicates_values(self):
        result = normalize_mapping_dict({"<人名[1].a.b>": ["张三", "张三"]})
        assert result == {"<人名[1].a.b>": ["张三"]}

    def test_rejects_non_dict(self):
        with pytest.raises(ValueError, match="must be a JSON object"):
            normalize_mapping_dict([1, 2, 3])

    def test_rejects_invalid_tag_key(self):
        with pytest.raises(ValueError, match="not a valid anonymized tag"):
            normalize_mapping_dict({"not_a_tag": ["value"]})

    def test_rejects_empty_key(self):
        with pytest.raises(ValueError, match="non-empty"):
            normalize_mapping_dict({"": ["value"]})

    def test_rejects_empty_value(self):
        with pytest.raises(ValueError, match="empty value"):
            normalize_mapping_dict({"<人名[1].a.b>": [""]})

    def test_strips_whitespace(self):
        result = normalize_mapping_dict({"  <人名[1].a.b>  ": "  张三  "})
        assert "<人名[1].a.b>" in result
        assert result["<人名[1].a.b>"] == ["张三"]


# ---------------------------------------------------------------------------
# load_mapping / save_mapping
# ---------------------------------------------------------------------------


class TestLoadSaveMapping:
    def test_roundtrip_file(self, tmp_path):
        mapping = {"<人名[1].a.b>": ["张三"], "<地址[1].c.d>": ["北京"]}
        path = str(tmp_path / "mapping.json")
        save_mapping(mapping, path)
        loaded = load_mapping(path)
        assert loaded == mapping

    def test_save_creates_restrictive_permissions(self, tmp_path):
        mapping = {"<人名[1].a.b>": ["张三"]}
        path = str(tmp_path / "mapping.json")
        save_mapping(mapping, path)
        mode = stat.S_IMODE(os.stat(path).st_mode)
        assert mode == 0o600

    def test_load_inline_json(self):
        inline = '{"<人名[1].a.b>": ["张三"]}'
        loaded = load_mapping(inline)
        assert loaded == {"<人名[1].a.b>": ["张三"]}

    def test_load_wrapped_format(self, tmp_path):
        """Load from the {text:..., mapping:...} format produced by hide."""
        wrapped = {
            "text": "anonymized text",
            "mapping": {"<人名[1].a.b>": ["张三"]},
        }
        path = str(tmp_path / "wrapped.json")
        with open(path, "w") as f:
            json.dump(wrapped, f)
        loaded = load_mapping(path)
        assert loaded == {"<人名[1].a.b>": ["张三"]}

    def test_load_invalid_path_and_json(self):
        with pytest.raises(ValueError, match="neither a valid file path nor a valid JSON"):
            load_mapping("/nonexistent/path/to/file.json")

    def test_save_overwrites_existing(self, tmp_path):
        path = str(tmp_path / "mapping.json")
        save_mapping({"<人名[1].a.b>": ["张三"]}, path)
        save_mapping({"<人名[2].a.b>": ["李四"]}, path)
        loaded = load_mapping(path)
        assert "<人名[2].a.b>" in loaded
        assert "<人名[1].a.b>" not in loaded


# ---------------------------------------------------------------------------
# parse_json_tolerant
# ---------------------------------------------------------------------------


class TestParseJsonTolerant:
    def test_plain_json(self):
        assert parse_json_tolerant('{"key": "value"}') == {"key": "value"}

    def test_json_array(self):
        assert parse_json_tolerant("[1, 2, 3]") == [1, 2, 3]

    def test_markdown_fenced_json(self):
        text = '```json\n{"key": "value"}\n```'
        assert parse_json_tolerant(text) == {"key": "value"}

    def test_markdown_fenced_no_lang(self):
        text = '```\n{"key": "value"}\n```'
        assert parse_json_tolerant(text) == {"key": "value"}

    def test_trailing_text_after_json(self):
        text = 'Some intro {"key": "value"} some trailing'
        assert parse_json_tolerant(text) == {"key": "value"}

    def test_returns_none_for_garbage(self):
        assert parse_json_tolerant("not json at all") is None

    def test_empty_string(self):
        assert parse_json_tolerant("") is None

    def test_whitespace_padded(self):
        assert parse_json_tolerant('  {"a": 1}  ') == {"a": 1}
