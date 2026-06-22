#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared CLI utilities for has_text commands.

Contains argument validation, I/O helpers, error handling, and output
formatting used by all three subcommands (hide, restore, scan).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from .mapping import has_tags, load_mapping, save_mapping
from .parallel import DEFAULT_MAX_PARALLEL_REQUESTS, resolve_parallel_workers


# Rough token estimate used only for pre-server slot planning.
# Actual chunking always uses the real tokenizer via HaSClient.count_tokens.
def estimate_tokens_for_planning(text: str) -> int:
    """Conservative character-based estimate, used only before the server starts."""
    if not text:
        return 0
    # ~0.5 tokens per character is conservative for mixed CJK/Latin text.
    return max(1, int(len(text) * 0.5))


# Fallback context size when the default 8K is too small (mapping overflow).
FALLBACK_CONTEXT_PER_SLOT = 16384

SCHEMA_VERSION = "1"


@dataclass(frozen=True)
class CLIError(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return self.message


class StructuredArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that reports machine-readable errors."""

    def error(self, message: str) -> None:
        raise CLIError("invalid_arguments", message)


def emit_json(payload: dict[str, Any], *, stream=None) -> None:
    target = stream or sys.stdout
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), file=target)


def error_payload(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "error": {
            "code": code,
            "message": message,
        },
    }


def fatal(code: str, message: str) -> None:
    raise CLIError(code, message)


def absolute_path(path: Path | str) -> str:
    """Return a stable absolute path string without resolving symlink targets."""
    return str(Path(path).expanduser().absolute())


def read_text(args: argparse.Namespace) -> str:
    """Read input text from --text, --file, or stdin."""
    if hasattr(args, "text") and args.text:
        return args.text
    if hasattr(args, "file") and args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    # Try stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()
    fatal("missing_input", "Provide exactly one input source via --text, --file, --dir, or stdin.")


def parse_types(type_values: Optional[List[str]]) -> List[str]:
    """Parse repeated --type flags into a normalized list."""
    if not type_values:
        fatal("missing_type", "Provide at least one --type value.")

    parsed: List[str] = []
    for raw_value in type_values:
        value = str(raw_value).strip()
        if not value:
            fatal("invalid_type", "--type values must be non-empty strings.")
        if value not in parsed:
            parsed.append(value)
    return parsed


def load_mapping_file(path: str) -> Dict[str, List[str]]:
    mapping_path = Path(path)
    if not mapping_path.is_file():
        fatal("mapping_not_found", f"Mapping file not found: {path}")
    return load_mapping(str(mapping_path))


def output(
    command: str,
    result: dict[str, Any],
    *,
    timing: bool = False,
    elapsed_ms: Optional[int] = None,
) -> None:
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "command": command,
    }
    payload.update(result)
    if timing and elapsed_ms is not None:
        payload["elapsed_ms"] = elapsed_ms
    emit_json(payload)


def parallel_default() -> int:
    """Read the shared parallel request budget from the environment."""
    raw = os.environ.get("HAS_TEXT_MAX_PARALLEL_REQUESTS")
    if raw is None:
        return DEFAULT_MAX_PARALLEL_REQUESTS

    try:
        value = int(raw)
    except ValueError:
        fatal("invalid_env", "HAS_TEXT_MAX_PARALLEL_REQUESTS must be an integer >= 1")

    if value < 1:
        fatal("invalid_env", "HAS_TEXT_MAX_PARALLEL_REQUESTS must be >= 1")

    return value


def required_slots(total_requests: int, max_parallel_requests: int) -> int:
    """Clamp server slots to the actual model work for this command."""
    if total_requests <= 0:
        return 0
    return resolve_parallel_workers(total_requests, max_parallel_requests)


def read_utf8_text_file(path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Read a plaintext file, rejecting binary and non-UTF-8 content."""
    try:
        with path.open("rb") as fh:
            sample = fh.read(8192)
    except OSError as exc:
        return None, str(exc)

    if b"\x00" in sample:
        return None, "binary"

    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "non_utf8"
    except OSError as exc:
        return None, str(exc)


def is_within_directory(path: Path, directory: Path) -> bool:
    """Return whether `path` resolves within `directory`."""
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def collect_text_documents(dir_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Collect immediate plaintext files from a directory."""
    directory = Path(dir_path)
    if not directory.is_dir():
        fatal("invalid_directory", f"Not a directory: {dir_path}")
    directory_root = directory.resolve()

    documents: List[Dict[str, str]] = []
    skipped: List[Dict[str, str]] = []

    for entry in sorted(directory.iterdir()):
        if not entry.is_file():
            continue
        try:
            resolved_entry = entry.resolve()
        except OSError as exc:
            skipped.append({"file": absolute_path(entry), "reason": str(exc)})
            continue
        if not is_within_directory(resolved_entry, directory_root):
            skipped.append({"file": absolute_path(entry), "reason": "symlink_escape"})
            continue
        text, skip_reason = read_utf8_text_file(entry)
        if text is None:
            skipped.append({"file": absolute_path(entry), "reason": skip_reason or "unreadable"})
            continue
        documents.append({"file": absolute_path(entry), "text": text})

    return documents, skipped


def write_text_output(path: Path, text: str) -> None:
    """Write UTF-8 text with restrictive permissions (0600).

    Both anonymized and restored text may contain sensitive information.
    Match the restrictive permissions used by save_mapping.
    """
    import os as _os

    path.parent.mkdir(parents=True, exist_ok=True)
    fd = _os.open(str(path), _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC, 0o600)
    try:
        if hasattr(_os, "fchmod"):
            _os.fchmod(fd, 0o600)
        else:
            _os.chmod(str(path), 0o600)
        f = _os.fdopen(fd, "w", encoding="utf-8")
    except Exception:
        _os.close(fd)
        raise
    with f:
        f.write(text)


def resolve_single_output_path(
    path_value: Optional[str],
    *,
    input_path: Optional[Path] = None,
    input_label: str = "input file",
) -> Optional[Path]:
    """Resolve a single-file output path and refuse obvious clobbers."""
    if not path_value:
        return None

    output_path = Path(path_value)
    if input_path is not None and output_path.resolve(strict=False) == input_path.resolve(strict=False):
        fatal("refusing_overwrite", f"Refusing to overwrite {input_label}: {input_path}")
    return output_path


def default_seek_mapping_dir(dir_path: str) -> Path:
    """Return the default per-file mapping directory for batch restore."""
    return Path(dir_path) / "mappings"


def default_restore_output_dir(dir_path: str) -> Path:
    """Return the default output directory for batch restore.

    If the input directory sits directly under a `.has/` parent
    (e.g. `docs/.has/anonymized/`), place `restored/` as a sibling
    under the same `.has/` tree → `docs/.has/restored/`.
    Otherwise fall back to `<input-dir>/.has/restored/`.
    """
    d = Path(dir_path)
    if d.parent.name == ".has":
        return d.parent / "restored"
    return d / ".has" / "restored"


def seek_mapping_path(mapping_dir: Path, source_path: Path) -> Path:
    """Return the per-file mapping path generated by `hide --dir`."""
    return mapping_dir / f"{source_path.name}.mapping.json"
