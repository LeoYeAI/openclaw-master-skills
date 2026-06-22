#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mapping management: merge, persist, tag utilities."""

from __future__ import annotations

import json
import re
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

# Tag pattern: <类型[编号].分类.属性>
TAG_PATTERN = re.compile(r"<([^<>\[\]]+)\[(\d+)\]\.([^<>\[\].]+)\.([^<>\[\].]+)>")


def find_tags(text: str) -> List[str]:
    """Find all anonymized tags in text.

    Returns:
        List of tag strings, e.g. ["<人名[1].个人.姓名>", "<地址[1].城市.区域>"]
    """
    return [m.group(0) for m in TAG_PATTERN.finditer(text)]


def has_tags(text: str) -> bool:
    """Check if text contains any anonymized tags."""
    return bool(TAG_PATTERN.search(text))


def is_composite_tag(key: str) -> bool:
    """Check if a mapping key contains multiple tags (composite).

    Example composite: "<职务[3].职务.职务名称><人名[1].中文姓名.姓名>"
    """
    matches = TAG_PATTERN.findall(key)
    return len(matches) > 1


def find_composite_entries(
    mapping: Dict[str, List[str]],
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Separate mapping into atomic and composite entries.

    Returns:
        (atomic_entries, composite_entries)
    """
    atomic = {}
    composite = {}
    for key, values in mapping.items():
        if is_composite_tag(key):
            composite[key] = values
        else:
            atomic[key] = values
    return atomic, composite


def merge_mappings(
    base: Dict[str, List[str]],
    new: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """Merge new mapping into base, deduplicating values.

    Args:
        base: Existing mapping (will not be mutated).
        new: New mapping entries to merge.

    Returns:
        Merged mapping.
    """
    result = OrderedDict()
    # Copy base
    for key, values in base.items():
        result[key] = list(values)
    # Merge new
    for key, values in new.items():
        if key in result:
            for v in values:
                if v not in result[key]:
                    result[key].append(v)
        else:
            result[key] = list(values)
    return dict(result)


def normalize_mapping_dict(data: Any) -> Dict[str, List[str]]:
    """Validate and normalize a mapping dictionary.

    Accepts either string values or arrays of strings and always returns
    ``Dict[str, List[str]]`` with deduplicated, non-empty values.
    """

    if not isinstance(data, dict):
        raise ValueError("Mapping data must be a JSON object")

    normalized: Dict[str, List[str]] = OrderedDict()

    for raw_key, raw_values in data.items():
        key = str(raw_key).strip()
        if not key:
            raise ValueError("Mapping keys must be non-empty strings")
        if not TAG_PATTERN.search(key):
            raise ValueError(f"Mapping key {key!r} is not a valid anonymized tag")

        if isinstance(raw_values, str):
            values_source = [raw_values]
        elif isinstance(raw_values, list):
            values_source = raw_values
        else:
            raise ValueError(
                f"Mapping entry for {key!r} must be a string or an array of strings"
            )

        values: List[str] = []
        for raw_value in values_source:
            value = str(raw_value).strip()
            if not value:
                raise ValueError(f"Mapping entry for {key!r} contains an empty value")
            if value not in values:
                values.append(value)

        if not values:
            raise ValueError(f"Mapping entry for {key!r} must contain at least one value")

        normalized[key] = values

    return dict(normalized)


def load_mapping(path_or_json: str) -> Dict[str, List[str]]:
    """Load mapping from a JSON file or inline JSON string.

    The input can be:
    - A file path to a JSON file
    - An inline JSON string

    The JSON can be either:
    - A raw mapping dict: {"<tag>": ["value"]}
    - A has_text output: {"text": "...", "mapping": {"<tag>": ["value"]}}
    """
    import os

    # Try as file path first
    if os.path.isfile(path_or_json):
        with open(path_or_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # Try as inline JSON string
        try:
            data = json.loads(path_or_json)
        except json.JSONDecodeError:
            raise ValueError(
                f"'{path_or_json}' is neither a valid file path nor a valid JSON string"
            )

    if not isinstance(data, dict):
        raise ValueError("Mapping data must be a JSON object")

    if "mapping" in data:
        if not isinstance(data["mapping"], dict):
            raise ValueError("The 'mapping' field must be a JSON object")
        data = data["mapping"]

    return normalize_mapping_dict(data)


def save_mapping(mapping: Dict[str, List[str]], path: str) -> None:
    """Save mapping to a JSON file with restricted permissions (0600).

    Mapping files are highly sensitive — they can reverse all anonymization.
    """
    import os

    content = json.dumps(mapping, ensure_ascii=False, indent=2)
    # Explicitly tighten permissions after open as well, because the `mode`
    # argument only applies when the file is created and does not fix an
    # existing file that was already too permissive.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, 0o600)
        else:
            os.chmod(path, 0o600)
        f = os.fdopen(fd, "w", encoding="utf-8")
    except Exception:
        os.close(fd)
        raise
    with f:
        f.write(content)


def parse_json_tolerant(text: str) -> Any:
    """Tolerantly parse JSON from model output.

    The model output may have minor formatting issues.
    Tries stripping markdown fences and trailing text.
    """
    text = text.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```)
        lines = lines[1:]
        # Remove last line if it's ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object or array
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue

    return None
