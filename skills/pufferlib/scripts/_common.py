#!/usr/bin/env python3
"""Shared safety and strict-JSON helpers for bundled PufferLib CLIs."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

MAX_JSON_BYTES = 1_048_576
MAX_STEPS = 1_000_000_000
MAX_ENVS = 65_536
MAX_WORKERS = 256
MAX_EVAL_EPISODES = 10_000

STABLE_SDIST_SHA256 = (
    "7df3a3e3f5f894d78d2a1f5374097890aec01473183e748abefe4f3faa10eaa9"
)
SOURCE_4_COMMIT = "25647630e1b15330bb3153a5a0d3ff8d234c3acf"

LOGGER_CREDENTIAL_ENV = {
    "none": None,
    "wandb": "WANDB_API_KEY",
    "neptune": "NEPTUNE_API_TOKEN",
}

_SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SECRET_KEY = re.compile(
    r"(?:^|_)(?:api_?key|token|secret|password|credential|"
    r"private_?key|authorization)(?:$|_)",
    re.IGNORECASE,
)


class UserInputError(ValueError):
    """Raised for bounded, user-correctable input errors."""


def bounded_int(value: str | int, *, name: str, minimum: int, maximum: int) -> int:
    """Parse an integer while rejecting bools and out-of-range values."""
    if isinstance(value, bool):
        raise UserInputError(f"{name} must be an integer, not bool")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise UserInputError(f"{name} must be an integer") from exc
    if not minimum <= parsed <= maximum:
        raise UserInputError(f"{name} must be between {minimum} and {maximum}")
    return parsed


def validate_slug(value: str, *, name: str = "name") -> str:
    """Accept a local identifier, never a dotted import path."""
    if not isinstance(value, str) or not _SLUG.fullmatch(value):
        raise UserInputError(
            f"{name} must match {_SLUG.pattern!r}; dotted import paths are not accepted"
        )
    return value


def validate_sha256(value: str, *, name: str = "sha256") -> str:
    """Validate a lowercase SHA-256 digest."""
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise UserInputError(f"{name} must be 64 lowercase hexadecimal characters")
    return value


def _reject_constant(value: str) -> None:
    raise UserInputError(f"non-finite JSON number is not allowed: {value}")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise UserInputError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _assert_finite_json(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise UserInputError(f"{path} contains a non-finite number")
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_finite_json(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_finite_json(item, f"{path}[{index}]")


def strict_json_loads(text: str) -> Any:
    """Load JSON with duplicate-key and non-finite-number rejection."""
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise UserInputError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    _assert_finite_json(value)
    return value


def strict_json_dumps(value: Any, *, pretty: bool = True) -> str:
    """Serialize deterministic JSON and reject NaN or Infinity."""
    _assert_finite_json(value)
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    )


def emit_json(value: Any, *, pretty: bool = True) -> None:
    print(strict_json_dumps(value, pretty=pretty))


def resolve_local_path(
    value: str | Path,
    *,
    root: str | Path,
    must_exist: bool = True,
    reject_symlink: bool = True,
) -> Path:
    """Resolve a path beneath an explicit root without directory traversal."""
    root_path = Path(root).expanduser().resolve(strict=True)
    raw_path = Path(value).expanduser()
    candidate = raw_path if raw_path.is_absolute() else root_path / raw_path
    if reject_symlink and candidate.is_symlink():
        raise UserInputError(f"symlinks are not accepted: {candidate}")
    try:
        resolved = candidate.resolve(strict=must_exist)
    except OSError as exc:
        raise UserInputError(f"cannot resolve path: {candidate}") from exc
    try:
        resolved.relative_to(root_path)
    except ValueError as exc:
        raise UserInputError(f"path escapes root {root_path}: {candidate}") from exc
    return resolved


def load_json_object(
    path: str | Path,
    *,
    root: str | Path,
    max_bytes: int = MAX_JSON_BYTES,
) -> dict[str, Any]:
    """Read one explicitly named, bounded UTF-8 JSON object."""
    resolved = resolve_local_path(path, root=root, must_exist=True)
    size = resolved.stat().st_size
    if size > max_bytes:
        raise UserInputError(f"JSON file exceeds {max_bytes} bytes: {resolved}")
    try:
        text = resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise UserInputError(f"cannot read UTF-8 JSON file: {resolved}") from exc
    value = strict_json_loads(text)
    if not isinstance(value, dict):
        raise UserInputError("top-level JSON value must be an object")
    return value


def secret_key_paths(value: Any, path: str = "$") -> list[str]:
    """Return key paths that look like credential-bearing configuration."""
    matches: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")
            child_path = f"{path}.{key}"
            if _SECRET_KEY.search(normalized):
                matches.append(child_path)
            matches.extend(secret_key_paths(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            matches.extend(secret_key_paths(item, f"{path}[{index}]"))
    return matches


def require_keys(
    mapping: dict[str, Any],
    *,
    allowed: set[str],
    required: set[str],
    path: str,
) -> list[str]:
    """Return schema errors for missing and unknown mapping keys."""
    errors = [f"{path}.{key} is required" for key in sorted(required - mapping.keys())]
    errors.extend(f"{path}.{key} is not allowed" for key in sorted(mapping.keys() - allowed))
    return errors
