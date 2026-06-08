#!/usr/bin/env python3
import re
import tempfile
from pathlib import Path

BASE = (Path(tempfile.gettempdir()) / 'openclaw-desktop-agent').resolve()
TASK_ID_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$')


def ensure_base_dir():
    BASE.mkdir(parents=True, exist_ok=True)
    return BASE


def validate_task_id(task_id):
    if not isinstance(task_id, str):
        raise ValueError('invalid_task_id')
    normalized = task_id.strip()
    if not normalized:
        raise ValueError('invalid_task_id')
    if normalized in {'.', '..'}:
        raise ValueError('invalid_task_id')
    if not TASK_ID_PATTERN.fullmatch(normalized):
        raise ValueError('invalid_task_id')
    return normalized


def resolve_task_dir(task_id):
    safe_task_id = validate_task_id(task_id)
    base_dir = ensure_base_dir()
    task_dir = (base_dir / safe_task_id).resolve()
    if task_dir.parent != base_dir:
        raise ValueError('invalid_task_id')
    return task_dir
