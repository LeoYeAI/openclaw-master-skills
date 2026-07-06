"""File I/O utilities for AnyGen — validation, encoding, read/write helpers."""

import base64
import json
from pathlib import Path

def validate_file(file_path):
    """Validate file path before upload. Returns (Path, error_msg)."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return None, f"File not found: {file_path}"
    if not path.is_file():
        return None, f"Not a regular file: {file_path}"
    return path, None


def read_file_bytes(file_path):
    """Validate and read file contents. Returns (filename, bytes, size) or raises ValueError."""
    path, err = validate_file(file_path)
    if err:
        raise ValueError(err)
    with open(path, "rb") as f:
        content = f.read()
    return path.name, content, len(content)


def encode_file(file_path):
    """Encode file to base64 for legacy upload."""
    path, err = validate_file(file_path)
    if err:
        raise ValueError(err)

    with open(path, "rb") as f:
        content = f.read()

    suffix = path.suffix.lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".txt": "text/plain",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    mime_type = mime_types.get(suffix, "application/octet-stream")

    return {
        "file_name": path.name,
        "file_type": mime_type,
        "file_data": base64.b64encode(content).decode("utf-8"),
    }


def read_json(file_path):
    """Read and parse a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def write_json(file_path, data):
    """Write data to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_bytes(file_path, content):
    """Write binary content to a file."""
    with open(file_path, "wb") as f:
        f.write(content)
