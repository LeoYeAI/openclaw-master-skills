#!/usr/bin/env python3
"""Shared bounded, local-only helpers for the NeuroKit2 skill CLIs."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import stat
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

NEUROKIT2_VERSION = "0.2.13"
PINNED_INSTALL = 'uv pip install "neurokit2==0.2.13"'
MAX_CSV_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_OUTPUT_BYTES = 128 * 1024 * 1024
MAX_ROWS = 500_000
MAX_CHANNELS = 64
MAX_SELECTED_COLUMNS = 16
MAX_CELL_CHARS = 4096
MISSING_TOKENS = {"", "na", "n/a", "nan", "none", "null"}


class CliError(ValueError):
    """An expected command-line validation error."""


def _reject_constant(value: str) -> None:
    raise CliError(f"non-standard JSON constant is not allowed: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CliError(f"duplicate JSON key is not allowed: {key!r}")
        result[key] = value
    return result


def _reject_url(value: str) -> None:
    lowered = value.strip().lower()
    if "://" in lowered or lowered.startswith(
        ("http:", "https:", "ftp:", "s3:", "gs:", "file:")
    ):
        raise CliError("URLs are not accepted; provide a bounded local path")
    if "\x00" in value:
        raise CliError("paths must not contain a NUL byte")


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _reject_symlink_components(path: Path) -> None:
    absolute = _absolute_lexical(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        try:
            if current.is_symlink():
                raise CliError(f"symlink paths are not accepted: {current.name!r}")
        except OSError as exc:
            raise CliError(
                f"cannot inspect path component {current.name!r}: {exc}"
            ) from exc


def checked_root(value: str | os.PathLike[str]) -> Path:
    """Return an existing, non-symlink directory used as an I/O boundary."""

    raw = os.fspath(value)
    _reject_url(raw)
    supplied = _absolute_lexical(Path(raw).expanduser())
    if supplied.is_symlink():
        raise CliError("root directory must not itself be a symlink")
    try:
        root = supplied.resolve(strict=True)
        info = root.stat()
    except OSError as exc:
        raise CliError(f"cannot access root directory: {exc}") from exc
    if not stat.S_ISDIR(info.st_mode):
        raise CliError("root must be an existing directory")
    _reject_symlink_components(root)
    return root


def _within_root(candidate: Path, root: Path) -> None:
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise CliError("path escapes the declared root directory") from exc


def _suffix_matches(path: Path, suffixes: Iterable[str]) -> bool:
    lowered = path.name.lower()
    return any(lowered.endswith(suffix.lower()) for suffix in suffixes)


def checked_input_file(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    suffixes: Iterable[str],
    max_bytes: int,
) -> Path:
    """Return a bounded regular local file within root, rejecting symlinks."""

    raw = os.fspath(value)
    _reject_url(raw)
    root_path = checked_root(root)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = root_path / path
    path = _absolute_lexical(path)
    if path.is_symlink():
        raise CliError(f"input must not be a symlink: {path.name!r}")
    try:
        resolved = path.resolve(strict=True)
        info = resolved.stat()
    except OSError as exc:
        raise CliError(f"cannot access input file {path.name!r}: {exc}") from exc
    _within_root(resolved, root_path)
    _reject_symlink_components(resolved)
    if not stat.S_ISREG(info.st_mode):
        raise CliError(f"input is not a regular file: {path.name!r}")
    if info.st_size > max_bytes:
        raise CliError(
            f"input {path.name!r} is {info.st_size} bytes; limit is {max_bytes}"
        )
    if not _suffix_matches(resolved, suffixes):
        allowed = ", ".join(sorted({suffix.lower() for suffix in suffixes}))
        raise CliError(f"input suffix must be one of: {allowed}")
    return resolved


def checked_output_file(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    suffixes: Iterable[str],
    force: bool = False,
) -> Path:
    """Return a local output path within root without following symlinks."""

    raw = os.fspath(value)
    _reject_url(raw)
    root_path = checked_root(root)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = root_path / path
    path = _absolute_lexical(path)
    if path.name in {"", ".", ".."}:
        raise CliError("output must name a file")
    if not _suffix_matches(path, suffixes):
        allowed = ", ".join(sorted({suffix.lower() for suffix in suffixes}))
        raise CliError(f"output suffix must be one of: {allowed}")
    if path.is_symlink() or path.parent.is_symlink():
        raise CliError("output and its parent must not be symlinks")
    try:
        parent = path.parent.resolve(strict=True)
        parent_info = parent.stat()
    except OSError as exc:
        raise CliError(f"cannot access output parent: {exc}") from exc
    _within_root(parent, root_path)
    _reject_symlink_components(parent)
    if not stat.S_ISDIR(parent_info.st_mode):
        raise CliError("output parent must be an existing directory")
    destination = parent / path.name
    if destination.exists():
        if not destination.is_file():
            raise CliError("output exists and is not a regular file")
        if not force:
            raise CliError(f"refusing to overwrite existing output: {path.name!r}")
    return destination


def atomic_write_bytes(
    destination: str | os.PathLike[str],
    payload: bytes,
    *,
    root: str | os.PathLike[str] = ".",
    suffixes: Iterable[str],
    force: bool = False,
) -> Path:
    """Atomically write a private, bounded file."""

    if len(payload) > MAX_OUTPUT_BYTES:
        raise CliError(f"output is {len(payload)} bytes; limit is {MAX_OUTPUT_BYTES}")
    destination_path = checked_output_file(
        destination, root=root, suffixes=suffixes, force=force
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
        dir=destination_path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        if destination_path.exists() and not force:
            raise CliError(
                f"refusing to overwrite existing output: {destination_path.name!r}"
            )
        os.replace(temporary, destination_path)
    finally:
        temporary.unlink(missing_ok=True)
    return destination_path


def strict_json_bytes(document: Any) -> bytes:
    """Serialize deterministic RFC-compatible JSON."""

    try:
        payload = (
            json.dumps(
                document,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CliError(f"report is not strict JSON: {exc}") from exc
    if len(payload) > MAX_OUTPUT_BYTES:
        raise CliError(f"report is {len(payload)} bytes; limit is {MAX_OUTPUT_BYTES}")
    return payload


def emit_json(
    document: Any,
    *,
    output: str | os.PathLike[str] | None = None,
    root: str | os.PathLike[str] = ".",
    force: bool = False,
) -> None:
    """Print strict JSON or atomically write it with private permissions."""

    payload = strict_json_bytes(document)
    if output is None:
        print(payload.decode("utf-8"), end="")
        return
    atomic_write_bytes(
        output,
        payload,
        root=root,
        suffixes={".json"},
        force=force,
    )


def load_json_object(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    max_bytes: int = MAX_JSON_BYTES,
) -> dict[str, Any]:
    """Load a bounded strict JSON object."""

    path = checked_input_file(
        value,
        root=root,
        suffixes={".json"},
        max_bytes=max_bytes,
    )
    try:
        with path.open("r", encoding="utf-8") as handle:
            document = json.load(
                handle,
                parse_constant=_reject_constant,
                object_pairs_hook=_unique_object,
            )
    except CliError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CliError(f"cannot read valid JSON from {path.name!r}: {exc}") from exc
    if not isinstance(document, dict):
        raise CliError("JSON root must be an object")
    return document


def validate_keys(
    value: Mapping[str, Any],
    *,
    allowed: Iterable[str],
    required: Iterable[str] = (),
    context: str,
) -> None:
    allowed_set = set(allowed)
    required_set = set(required)
    unknown = sorted(set(value) - allowed_set)
    missing = sorted(required_set - set(value))
    if unknown:
        raise CliError(f"{context} has unknown keys: {', '.join(unknown)}")
    if missing:
        raise CliError(f"{context} is missing keys: {', '.join(missing)}")


def bounded_int(
    value: Any,
    *,
    name: str,
    minimum: int,
    maximum: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CliError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise CliError(f"{name} must be between {minimum} and {maximum}")
    return value


def finite_float(
    value: Any,
    *,
    name: str,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CliError(f"{name} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise CliError(f"{name} must be finite")
    if minimum is not None and number < minimum:
        raise CliError(f"{name} must be at least {minimum}")
    if maximum is not None and number > maximum:
        raise CliError(f"{name} must be at most {maximum}")
    return number


def parse_name_list(value: str | None, *, name: str) -> list[str]:
    if value is None:
        return []
    names = [item.strip() for item in value.split(",")]
    if not names or any(not item for item in names):
        raise CliError(f"{name} must be a comma-separated list of nonempty names")
    if len(names) != len(set(names)):
        raise CliError(f"{name} must not contain duplicates")
    return names


def require_deidentified(confirmed: bool) -> None:
    if not confirmed:
        raise CliError(
            "local participant data require --deidentified; remove direct identifiers "
            "and review quasi-identifiers before use"
        )


def _read_header(reader: Any) -> list[str]:
    try:
        header = next(reader)
    except StopIteration as exc:
        raise CliError("CSV is empty") from exc
    if not header or any(not name.strip() for name in header):
        raise CliError("CSV header names must be nonempty")
    header = [name.strip() for name in header]
    if len(header) != len(set(header)):
        raise CliError("CSV header names must be unique")
    if len(header) > MAX_CHANNELS:
        raise CliError(f"CSV has {len(header)} columns; limit is {MAX_CHANNELS}")
    return header


def read_numeric_columns(
    path: Path,
    columns: Sequence[str],
    *,
    max_rows: int = MAX_ROWS,
    allow_missing: bool = False,
) -> tuple[dict[str, list[float | None]], list[str], int]:
    """Read selected numeric CSV columns after bounded structural validation."""

    if not 1 <= max_rows <= MAX_ROWS:
        raise CliError(f"max_rows must be between 1 and {MAX_ROWS}")
    if not columns or len(columns) > MAX_SELECTED_COLUMNS:
        raise CliError(f"select between 1 and {MAX_SELECTED_COLUMNS} numeric columns")
    if len(columns) != len(set(columns)):
        raise CliError("selected columns must be unique")
    selected: dict[str, list[float | None]] = {name: [] for name in columns}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = _read_header(reader)
            missing = [name for name in columns if name not in header]
            if missing:
                raise CliError(f"CSV is missing columns: {', '.join(missing)}")
            positions = {name: header.index(name) for name in columns}
            row_count = 0
            for row_count, row in enumerate(reader, start=1):
                if row_count > max_rows:
                    raise CliError(f"CSV exceeds the row limit of {max_rows}")
                if len(row) != len(header):
                    raise CliError(
                        f"CSV row {row_count + 1} has {len(row)} cells; "
                        f"expected {len(header)}"
                    )
                for name, position in positions.items():
                    cell = row[position].strip()
                    if len(cell) > MAX_CELL_CHARS:
                        raise CliError(
                            f"CSV cell in column {name!r} exceeds "
                            f"{MAX_CELL_CHARS} characters"
                        )
                    if cell.lower() in MISSING_TOKENS:
                        if allow_missing:
                            selected[name].append(None)
                            continue
                        raise CliError(
                            f"column {name!r} contains a missing value at data row "
                            f"{row_count}; segment or apply a documented bounded "
                            "imputation policy before processing"
                        )
                    try:
                        number = float(cell)
                    except ValueError as exc:
                        raise CliError(
                            f"column {name!r} contains non-numeric data at data row "
                            f"{row_count}"
                        ) from exc
                    if not math.isfinite(number):
                        raise CliError(
                            f"column {name!r} contains a non-finite value at data row "
                            f"{row_count}"
                        )
                    selected[name].append(number)
    except CliError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise CliError(f"cannot read bounded CSV: {exc}") from exc
    if row_count == 0:
        raise CliError("CSV has a header but no data rows")
    return selected, header, row_count


def _format_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return format(value, ".12g")
    item = getattr(value, "item", None)
    if callable(item):
        converted = item()
        if converted is not value:
            return _format_csv_value(converted)
    text = str(value)
    if len(text) > MAX_CELL_CHARS:
        raise CliError("output CSV cell is too large")
    return text


def csv_bytes(columns: Sequence[str], rows: Iterable[Sequence[Any]]) -> bytes:
    """Serialize a deterministic UTF-8 CSV with Unix newlines."""

    if not columns or len(columns) > MAX_CHANNELS:
        raise CliError(f"CSV output must have 1 to {MAX_CHANNELS} columns")
    if len(columns) != len(set(columns)):
        raise CliError("CSV output columns must be unique")
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(columns)
    count = 0
    for count, row in enumerate(rows, start=1):
        if count > MAX_ROWS:
            raise CliError(f"CSV output exceeds the row limit of {MAX_ROWS}")
        values = list(row)
        if len(values) != len(columns):
            raise CliError("CSV output row length does not match columns")
        writer.writerow([_format_csv_value(value) for value in values])
        if buffer.tell() > MAX_OUTPUT_BYTES:
            raise CliError(f"CSV output exceeds {MAX_OUTPUT_BYTES} bytes")
    if count == 0:
        raise CliError("refusing to write a CSV without data rows")
    payload = buffer.getvalue().encode("utf-8")
    if len(payload) > MAX_OUTPUT_BYTES:
        raise CliError(f"CSV output exceeds {MAX_OUTPUT_BYTES} bytes")
    return payload


def write_csv(
    destination: str | os.PathLike[str],
    columns: Sequence[str],
    rows: Iterable[Sequence[Any]],
    *,
    root: str | os.PathLike[str] = ".",
    force: bool = False,
) -> bytes:
    payload = csv_bytes(columns, rows)
    atomic_write_bytes(
        destination,
        payload,
        root=root,
        suffixes={".csv"},
        force=force,
    )
    return payload


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def json_number(value: Any) -> float | int | None:
    """Return a finite JSON scalar from Python or NumPy numeric input."""

    item = getattr(value, "item", None)
    if callable(item):
        value = item()
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def dataframe_rows(frame: Any) -> Iterable[Sequence[Any]]:
    """Yield rows without importing pandas at module import time."""

    return frame.itertuples(index=False, name=None)


def run_cli(function: Any) -> int:
    """Run a CLI body with concise expected-error handling."""

    try:
        function()
    except CliError as exc:
        print(f"error: {exc}", file=os.sys.stderr)
        return 2
    except ModuleNotFoundError as exc:
        package = exc.name or "a required package"
        print(
            f"error: missing dependency {package!r}; install the pinned environment "
            f"with: {PINNED_INSTALL}",
            file=os.sys.stderr,
        )
        return 2
    except ImportError as exc:
        print(f"error: optional dependency unavailable: {exc}", file=os.sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("error: interrupted", file=os.sys.stderr)
        return 130
    return 0
