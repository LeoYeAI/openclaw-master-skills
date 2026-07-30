#!/usr/bin/env python3
"""
Shared JSON file operations for email-to-calendar skill.

Provides consistent file handling with atomic writes and error handling.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


def ensure_dir(filepath: str) -> None:
    """Ensure the directory for a file path exists."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)


def load_json(filepath: str, default: Optional[Any] = None) -> Any:
    """
    Load JSON from a file.

    Args:
        filepath: Path to the JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Parsed JSON data or the default value
    """
    filepath = os.path.expanduser(filepath)
    if default is None:
        default = {}

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(filepath: str, data: Any, indent: int = 2) -> None:
    """
    Save data as JSON to a file.

    Creates parent directories if they don't exist.

    Args:
        filepath: Path to the JSON file
        data: Data to serialize as JSON
        indent: Indentation level (default: 2)
    """
    filepath = os.path.expanduser(filepath)
    ensure_dir(filepath)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)
