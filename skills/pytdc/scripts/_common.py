#!/usr/bin/env python3
"""Shared, standard-library-only helpers for the bundled PyTDC CLIs."""

from __future__ import annotations

import importlib
import json
import math
import os
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Iterable, Sequence


class CliError(ValueError):
    """A user-facing command-line validation error."""


def bounded_int(minimum: int, maximum: int):
    """Return an argparse converter for a bounded integer."""

    def convert(value: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise ValueError(f"expected an integer, got {value!r}") from exc
        if not minimum <= parsed <= maximum:
            raise ValueError(
                f"expected an integer from {minimum} through {maximum}, got {parsed}"
            )
        return parsed

    return convert


def canonical_name(query: str, choices: Iterable[str], label: str) -> str:
    """Resolve a name case-insensitively without fuzzy matching."""

    lookup = {str(choice).casefold(): str(choice) for choice in choices}
    try:
        return lookup[query.casefold()]
    except KeyError as exc:
        preview = ", ".join(sorted(lookup.values())[:20])
        suffix = "" if len(lookup) <= 20 else ", ..."
        raise CliError(f"unknown {label} {query!r}; available: {preview}{suffix}") from exc


def safe_relative_path(
    raw_path: str,
    *,
    label: str,
    allow_workspace_root: bool = False,
) -> Path:
    """Resolve a relative path while preventing writes outside the workspace."""

    supplied = Path(raw_path)
    if supplied.is_absolute() or raw_path.startswith("~"):
        raise CliError(f"{label} must be a relative path inside the current workspace")

    workspace = Path.cwd().resolve()
    resolved = (workspace / supplied).resolve(strict=False)
    if resolved != workspace and workspace not in resolved.parents:
        raise CliError(f"{label} escapes the current workspace")
    if resolved == workspace and not allow_workspace_root:
        raise CliError(f"{label} must not be the workspace root")
    return resolved


def safe_directory(
    raw_path: str,
    *,
    label: str,
    create: bool = False,
    must_exist: bool = False,
) -> Path:
    """Validate a workspace-contained directory."""

    path = safe_relative_path(raw_path, label=label)
    if path.exists() and (path.is_symlink() or not path.is_dir()):
        raise CliError(f"{label} is not a regular directory: {raw_path}")
    if must_exist and not path.is_dir():
        raise CliError(f"{label} does not exist: {raw_path}")
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def safe_input_file(raw_path: str, *, max_bytes: int, label: str) -> Path:
    """Validate a bounded, workspace-contained input file."""

    path = safe_relative_path(raw_path, label=label)
    if path.is_symlink() or not path.is_file():
        raise CliError(f"{label} is not a regular file: {raw_path}")
    size = path.stat().st_size
    if size > max_bytes:
        raise CliError(f"{label} is {size} bytes; limit is {max_bytes} bytes")
    return path


def validate_fractions(values: Sequence[float]) -> tuple[float, float, float]:
    """Validate train/validation/test fractions."""

    if len(values) != 3:
        raise CliError("--frac requires exactly three values")
    fractions = tuple(float(value) for value in values)
    if any(not math.isfinite(value) or value < 0 for value in fractions):
        raise CliError("split fractions must be finite and non-negative")
    if not math.isclose(sum(fractions), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise CliError("split fractions must sum to 1")
    if fractions[0] <= 0:
        raise CliError("the training fraction must be greater than zero")
    return fractions  # type: ignore[return-value]


def load_pytdc_metadata() -> tuple[Any, str]:
    """Lazily import bundled package metadata without instantiating a dataset."""

    try:
        metadata = importlib.import_module("tdc.metadata")
        package_version = version("PyTDC")
    except (ImportError, PackageNotFoundError) as exc:
        raise CliError(
            "PyTDC is unavailable; install the pinned snapshot with "
            "`uv pip install \"setuptools==80.9.0\" \"PyTDC==1.1.15\"`"
        ) from exc
    return metadata, package_version


def truncate_value(value: Any, *, max_string: int = 160) -> Any:
    """Convert common scientific values to bounded JSON-compatible values."""

    if isinstance(value, Path):
        return str(value)
    if isinstance(value, str):
        if len(value) <= max_string:
            return value
        return value[:max_string] + f"...[{len(value) - max_string} chars omitted]"
    if isinstance(value, dict):
        return {
            str(key): truncate_value(item, max_string=max_string)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [truncate_value(item, max_string=max_string) for item in value]
    if isinstance(value, set):
        return sorted(truncate_value(item, max_string=max_string) for item in value)
    if hasattr(value, "item"):
        try:
            return truncate_value(value.item(), max_string=max_string)
        except (TypeError, ValueError):
            pass
    if hasattr(value, "tolist"):
        try:
            return truncate_value(value.tolist(), max_string=max_string)
        except (TypeError, ValueError):
            pass
    return value


def read_json_file(path: Path) -> Any:
    """Read strict JSON, rejecting non-standard constants such as NaN."""

    def reject_constant(value: str) -> None:
        raise CliError(f"non-standard JSON constant is not allowed: {value}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle, parse_constant=reject_constant)
    except json.JSONDecodeError as exc:
        raise CliError(f"invalid JSON in {path.name}: {exc}") from exc


def emit_json(payload: Any, output: str | None, *, force: bool = False) -> None:
    """Print JSON or atomically write it to a safe relative path."""

    serializable = truncate_value(payload)
    text = json.dumps(serializable, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if output is None:
        print(text, end="")
        return

    destination = safe_relative_path(output, label="output path")
    if destination.exists() and (destination.is_symlink() or destination.is_dir()):
        raise CliError(f"output path is not a regular file: {output}")
    if destination.exists() and not force:
        raise CliError(f"output already exists: {output}; pass --force to replace it")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(text)
            temporary_name = handle.name
        os.replace(temporary_name, destination)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
