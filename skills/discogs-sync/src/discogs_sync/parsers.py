"""CSV and JSON input file parsing and validation."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .exceptions import ParseError
from .models import InputRecord

# Format normalization map
FORMAT_SYNONYMS: dict[str, str] = {
    "lp": "Vinyl",
    "record": "Vinyl",
    '12"': "Vinyl",
    "12 inch": "Vinyl",
    "vinyl": "Vinyl",
    "compact disc": "CD",
    "cd": "CD",
    "tape": "Cassette",
    "mc": "Cassette",
    "cassette": "Cassette",
}

REQUIRED_FIELDS = {"artist", "album"}
VALID_FIELDS = {"artist", "album", "format", "year", "notes"}


def normalize_format(fmt: str | None) -> str | None:
    """Normalize format synonyms to canonical names."""
    if not fmt:
        return None
    normalized = FORMAT_SYNONYMS.get(fmt.strip().lower())
    if normalized:
        return normalized
    # Return original if not a known synonym (e.g., "Vinyl", "CD" already canonical)
    return fmt.strip()


def extract_artist_from_data(data: dict) -> str:
    """Extract artist name from Discogs API release data.

    The API provides artists as a list of dicts with 'name' and 'join' keys.
    Artist names may include disambiguation suffixes like '(4)' which are stripped.
    """
    import re

    artists = data.get("artists", [])
    if not artists or not isinstance(artists, list):
        return ""
    parts = []
    for i, a in enumerate(artists):
        if not isinstance(a, dict):
            continue
        name = a.get("anv") or a.get("name", "")
        # Strip Discogs disambiguation suffix, e.g. "John Williams (4)" -> "John Williams"
        name = re.sub(r"\s*\(\d+\)$", "", name)
        parts.append(name)
        if i < len(artists) - 1:
            join = a.get("join", "").strip()
            if join and join != ",":
                parts.append(f" {join} ")
            elif join == ",":
                parts.append(", ")
            else:
                parts.append(", ")
    return "".join(parts)


def parse_file(filepath: str | Path) -> list[InputRecord]:
    """Parse an input file (CSV or JSON) and return validated records.

    Auto-detects format by file extension.
    """
    path = Path(filepath)
    if not path.exists():
        raise ParseError(f"File not found: {path}")

    ext = path.suffix.lower()
    if ext == ".csv":
        return parse_csv(path)
    elif ext == ".json":
        return parse_json(path)
    else:
        raise ParseError(f"Unsupported file format: {ext}. Use .csv or .json")


def parse_csv(path: Path) -> list[InputRecord]:
    """Parse a CSV file into InputRecords."""
    errors: list[dict] = []
    records: list[InputRecord] = []

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise ParseError(f"Failed to read file: {e}") from e

    reader = csv.DictReader(text.splitlines())

    if reader.fieldnames is None:
        raise ParseError("CSV file is empty or has no header row")

    # Normalize header names to lowercase
    field_map = {f.strip().lower(): f for f in reader.fieldnames}

    # Check required fields
    missing = REQUIRED_FIELDS - set(field_map.keys())
    if missing:
        raise ParseError(f"CSV missing required columns: {', '.join(sorted(missing))}")

    for line_num, row in enumerate(reader, start=2):  # line 1 is header
        # Normalize keys
        normalized = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}
        record, error = _validate_row(normalized, line_num)
        if error:
            errors.append(error)
        else:
            records.append(record)

    total = len(records) + len(errors)
    if total == 0:
        raise ParseError("CSV file contains no data rows")

    if errors and len(errors) > total * 0.5:
        raise ParseError(
            f"Too many invalid rows ({len(errors)}/{total}). Aborting.",
            errors=errors,
        )

    if errors:
        # Report errors but continue with valid records
        from .output import print_warning

        for e in errors:
            print_warning(f"Line {e['line']}: {e['message']}")

    return records


def parse_json(path: Path) -> list[InputRecord]:
    """Parse a JSON file into InputRecords."""
    errors: list[dict] = []
    records: list[InputRecord] = []

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise ParseError(f"Failed to read file: {e}") from e

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ParseError(f"Invalid JSON: {e}") from e

    if not isinstance(data, list):
        raise ParseError("JSON input must be an array of objects")

    if not data:
        raise ParseError("JSON file contains no records")

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append({"line": idx + 1, "message": "Item is not an object"})
            continue

        normalized = {k.strip().lower(): (str(v).strip() if v is not None else "") for k, v in item.items()}
        record, error = _validate_row(normalized, idx + 1)
        if error:
            errors.append(error)
        else:
            records.append(record)

    total = len(records) + len(errors)
    if errors and len(errors) > total * 0.5:
        raise ParseError(
            f"Too many invalid records ({len(errors)}/{total}). Aborting.",
            errors=errors,
        )

    if errors:
        from .output import print_warning

        for e in errors:
            print_warning(f"Record {e['line']}: {e['message']}")

    return records


def _validate_row(row: dict[str, str], line_number: int) -> tuple[InputRecord | None, dict | None]:
    """Validate a single row and return (record, error)."""
    artist = row.get("artist", "").strip()
    album = row.get("album", "").strip()

    if not artist:
        return None, {"line": line_number, "message": "Missing required field: artist"}
    if not album:
        return None, {"line": line_number, "message": "Missing required field: album"}

    fmt = normalize_format(row.get("format"))

    year = None
    year_str = row.get("year", "").strip()
    if year_str:
        try:
            year = int(year_str)
            if year < 1900 or year > 2030:
                return None, {"line": line_number, "message": f"Year out of range: {year}"}
        except ValueError:
            return None, {"line": line_number, "message": f"Invalid year: {year_str}"}

    notes = row.get("notes", "").strip() or None

    return InputRecord(
        artist=artist,
        album=album,
        format=fmt,
        year=year,
        notes=notes,
        line_number=line_number,
    ), None
