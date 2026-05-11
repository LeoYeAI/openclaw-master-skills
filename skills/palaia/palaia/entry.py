"""Memory entry parsing and creation (ADR-006, ADR-012)."""

from __future__ import annotations

import hashlib
import os
import re
import uuid
from datetime import datetime, timezone

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

# Entry class types (ADR-012)
VALID_TYPES = {"memory", "process", "task"}
DEFAULT_TYPE = "memory"

# Task-specific structured fields (ADR-012)
VALID_STATUSES = {"open", "in-progress", "done", "wontfix"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}


def _parse_yaml_simple(text: str) -> dict:
    """Minimal YAML-like parser for frontmatter. No dependency needed.


    Handles: key: value, key: [a, b, c], quoted strings.
    """
    result = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        # Only split on the FIRST colon to preserve colons in values (URLs, timestamps, etc.)
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # List
        if value.startswith("[") and value.endswith("]"):
            items = value[1:-1].split(",")
            result[key] = [i.strip().strip("'\"") for i in items if i.strip()]
        # Number (int)
        elif value.isdigit():
            result[key] = int(value)
        # Float
        elif re.match(r"^\d+\.\d+$", value):
            result[key] = float(value)
        # Quoted string
        elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            result[key] = value[1:-1]
        else:
            result[key] = value
    return result


def _to_yaml_simple(data: dict) -> str:
    """Minimal dict → YAML-like frontmatter string."""
    lines = []
    for k, v in data.items():
        if isinstance(v, list):
            items = ", ".join(str(i) for i in v)
            lines.append(f"{k}: [{items}]")
        elif isinstance(v, float):
            lines.append(f"{k}: {v}")
        elif isinstance(v, int):
            lines.append(f"{k}: {v}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)


def extract_title_from_content(body: str, max_length: int = 80) -> str | None:
    """Extract a title from the first non-empty line of content.

    Strips markdown header prefixes (e.g. '# ', '## ').
    Truncates at ~max_length characters.
    Returns None if no usable title can be extracted.
    """
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # Strip markdown header prefixes (e.g. '# Title', '## Section')
        title = re.sub(r"^#{1,6}\s*", "", stripped)
        title = title.strip()
        if not title:
            continue
        if len(title) > max_length:
            title = title[:max_length].rsplit(" ", 1)[0] + "..."
        return title
    return None


def content_hash(text: str) -> str:
    """SHA-256 hash of content body."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_entry_type(entry_type: str | None) -> str:
    """Validate and return entry type, defaulting to 'memory'."""
    if entry_type is None:
        return DEFAULT_TYPE
    entry_type = entry_type.strip().lower()
    if entry_type not in VALID_TYPES:
        raise ValueError(f"Invalid entry type: '{entry_type}'. Valid: {', '.join(sorted(VALID_TYPES))}")
    return entry_type


def validate_status(status: str | None) -> str | None:
    """Validate task status."""
    if status is None:
        return None
    status = status.strip().lower()
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: '{status}'. Valid: {', '.join(sorted(VALID_STATUSES))}")
    return status


def validate_priority(priority: str | None) -> str | None:
    """Validate task priority."""
    if priority is None:
        return None
    priority = priority.strip().lower()
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority: '{priority}'. Valid: {', '.join(sorted(VALID_PRIORITIES))}")
    return priority


def _resolve_instance() -> str | None:
    """Resolve instance name from PALAIA_INSTANCE env var.

    Note: CLI layer resolves instance from config file (palaia instance set).
    This function is the low-level fallback for programmatic use.
    """
    return os.environ.get("PALAIA_INSTANCE") or None


def create_entry(
    body: str,
    scope: str = "team",
    agent: str | None = None,
    tags: list[str] | None = None,
    title: str | None = None,
    project: str | None = None,
    entry_type: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    assignee: str | None = None,
    due_date: str | None = None,
    instance: str | None = None,
) -> str:
    """Create a full memory entry string with frontmatter."""
    now = datetime.now(timezone.utc).isoformat()
    entry_type = validate_entry_type(entry_type)

    meta = {
        "id": str(uuid.uuid4()),
        "type": entry_type,
        "scope": scope,
        "created": now,
        "accessed": now,
        "access_count": 1,
        "decay_score": 1.0,
        "content_hash": content_hash(body),
    }
    if agent:
        meta["agent"] = agent
    # Session identity (ADR-012)
    resolved_instance = instance or _resolve_instance()
    if resolved_instance:
        meta["instance"] = resolved_instance
    if tags:
        meta["tags"] = tags
    # Auto-extract title from content if not explicitly provided
    effective_title = title if title else extract_title_from_content(body)
    if effective_title:
        meta["title"] = effective_title
    if project:
        meta["project"] = project

    # Task-specific fields (only for type: task)
    if entry_type == "task":
        meta["status"] = validate_status(status) or "open"
        if priority:
            meta["priority"] = validate_priority(priority)
        if assignee:
            meta["assignee"] = assignee
        if due_date:
            meta["due_date"] = due_date

    fm = _to_yaml_simple(meta)
    return f"---\n{fm}\n---\n\n{body}\n"


def parse_entry(text: str) -> tuple[dict, str]:
    """Parse a memory entry into (metadata, body)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text.strip()
    meta = _parse_yaml_simple(m.group(1))
    body = text[m.end() :].strip()
    return meta, body


def update_access(meta: dict) -> dict:
    """Update access metadata (timestamp, count, score)."""
    from palaia.decay import days_since, decay_score

    meta["accessed"] = datetime.now(timezone.utc).isoformat()
    meta["access_count"] = meta.get("access_count", 0) + 1
    days_since(meta.get("created", meta["accessed"]))
    meta["decay_score"] = decay_score(0, meta["access_count"])
    return meta


def serialize_entry(meta: dict, body: str) -> str:
    """Serialize metadata and body back to entry format."""
    fm = _to_yaml_simple(meta)
    return f"---\n{fm}\n---\n\n{body}\n"
