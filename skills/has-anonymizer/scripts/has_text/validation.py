#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validation helpers for model outputs."""

from __future__ import annotations

from typing import Any, Dict, List


def normalize_entity_map(data: Any, *, context: str) -> Dict[str, List[str]]:
    """Validate and normalize NER output into ``Dict[str, List[str]]``."""

    if not isinstance(data, dict):
        raise RuntimeError(f"{context} did not return a JSON object")

    normalized: Dict[str, List[str]] = {}

    for raw_key, raw_values in data.items():
        key = str(raw_key).strip()
        if not key:
            raise RuntimeError(f"{context} returned an empty entity type")

        if isinstance(raw_values, str):
            values_source = [raw_values]
        elif isinstance(raw_values, list):
            values_source = raw_values
        else:
            raise RuntimeError(
                f"{context} returned an invalid value for entity type {key!r}"
            )

        values: List[str] = []
        for raw_value in values_source:
            value = str(raw_value).strip()
            if value and value not in values:
                values.append(value)

        normalized[key] = values

    return normalized
