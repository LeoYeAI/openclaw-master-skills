"""Robust JSON parsing utilities for Qwen/Ollama responses.

Handles multiple output formats:
1. Raw JSON: {"key": "value"}
2. Markdown code blocks: ```json\n{"key": "value"}\n```
3. Wrapped JSON: Some text... {"key": "value"} ...more text
4. Fallback: Extract key-value pairs manually

This prevents silent failures when Qwen outputs JSON in unexpected formats.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

_log = logging.getLogger(__name__)

# Sentinel value to distinguish "no fallback provided" from "fallback is None"
_SENTINEL = object()


def _extract_json_by_braces(text: str) -> Optional[str]:
    """Extract JSON string by matching braces, handling nested structures properly.

    Finds the first '{' and matches it with the corresponding '}', accounting for
    escaped quotes and nested braces.

    Args:
        text: Text potentially containing JSON

    Returns:
        Extracted JSON string, or None if no valid JSON object found
    """
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i in range(start, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == "\\" and in_string:
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if not in_string:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]

    return None


def safe_parse_json(
    text: str,
    fallback: Any = _SENTINEL,
    logger_prefix: str = "",
) -> Optional[dict]:
    """Parse JSON from text with multiple fallback strategies.

    Attempts in order:
    1. Direct json.loads()
    2. Extract from markdown code blocks (```json ... ```)
    3. Extract JSON object using regex (finds {...})
    4. Manual key-value pair extraction (last resort)

    Args:
        text: Text potentially containing JSON
        fallback: Default value if all strategies fail.
                  If not provided, defaults to empty dict {}.
                  Can be explicitly set to None to get None on failure.
        logger_prefix: Prefix for debug logs to identify the caller

    Returns:
        Parsed dict, or fallback value if all strategies fail
    """
    # Handle fallback: use empty dict if not provided
    if fallback is _SENTINEL:
        fallback = {}

    if not text or not isinstance(text, str):
        _log.debug(f"{logger_prefix} safe_parse_json: input is empty or not string")
        return fallback

    text = text.strip()

    # Strategy 1: Direct json.loads()
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            _log.debug(f"{logger_prefix} safe_parse_json: success via direct json.loads()")
            return result
    except json.JSONDecodeError:
        _log.debug(f"{logger_prefix} safe_parse_json: direct json.loads() failed")
    except Exception as e:
        _log.debug(f"{logger_prefix} safe_parse_json: direct json.loads() error: {e}")

    # Strategy 2: Extract from markdown code blocks
    # Patterns: ```json ... ```, ```JSON ... ```, or generic ``` ... ```
    json_block_match = re.search(
        r'```(?:json|JSON)?\s*\n?(.*?)\n?```',
        text,
        re.DOTALL
    )
    if json_block_match:
        json_text = json_block_match.group(1).strip()
        try:
            result = json.loads(json_text)
            if isinstance(result, dict):
                _log.debug(f"{logger_prefix} safe_parse_json: success via markdown code block extraction")
                return result
        except json.JSONDecodeError as e:
            _log.debug(f"{logger_prefix} safe_parse_json: markdown block extraction failed: {e}")

    # Strategy 3: Use brace-matching to find JSON object
    # This handles nested structures by counting braces
    json_text = _extract_json_by_braces(text)
    if json_text:
        try:
            result = json.loads(json_text)
            if isinstance(result, dict):
                _log.debug(f"{logger_prefix} safe_parse_json: success via brace-matching extraction")
                return result
        except json.JSONDecodeError as e:
            _log.debug(f"{logger_prefix} safe_parse_json: brace-matching extraction failed: {e}")

    # Strategy 4: Manual key-value pair extraction (last resort)
    # Try to find quoted key-value pairs: "key": value or "key": "value"
    manual_result = _extract_key_values(text)
    if manual_result:
        _log.debug(f"{logger_prefix} safe_parse_json: success via manual key-value extraction")
        return manual_result

    # All strategies failed
    _log.warning(
        f"{logger_prefix} safe_parse_json: all strategies failed, raw text:\n{text[:200]}"
    )
    return fallback


def _extract_key_values(text: str) -> Optional[dict]:
    """Manually extract key-value pairs from text (last-resort parser).

    Looks for patterns like:
    - "key": "value"
    - "key": true/false
    - "key": 123
    - "key": [...]

    Returns:
        Dict with extracted pairs, or None if nothing found
    """
    result = {}

    # Pattern: "key": value (with quotes around key, any value)
    # This handles strings, booleans, numbers, arrays, objects
    pattern = r'"([^"]+)"\s*:\s*([^,}]+)'

    matches = re.findall(pattern, text)
    for key, value in matches:
        key = key.strip()
        value = value.strip()

        # Try to parse the value
        parsed_value: Any = value
        if value.lower() == "true":
            parsed_value = True
        elif value.lower() == "false":
            parsed_value = False
        elif value.lower() == "null":
            parsed_value = None
        elif value.startswith('"') and value.endswith('"'):
            # String value
            parsed_value = value[1:-1]
        elif value.startswith('[') or value.startswith('{'):
            # Array or object — try to parse
            try:
                parsed_value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                parsed_value = value
        else:
            # Try to parse as number
            try:
                if '.' in value:
                    parsed_value = float(value)
                else:
                    parsed_value = int(value)
            except (ValueError, TypeError):
                parsed_value = value

        result[key] = parsed_value

    return result if result else None
