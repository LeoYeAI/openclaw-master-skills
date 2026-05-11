"""Utility functions for Weiyun Skills."""

import os
import hashlib
from datetime import datetime


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size string.

    Args:
        size_bytes: File size in bytes.

    Returns:
        Human-readable size string like '2.50 MB'.
    """
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"


def get_file_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file.

    Args:
        file_path: Path to the file.

    Returns:
        MD5 hex digest string.
    """
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest()


def parse_cookies_str(cookies_str: str) -> dict:
    """Parse cookies string into a dictionary.

    Args:
        cookies_str: Cookie string from browser, e.g. 'key1=val1; key2=val2'.

    Returns:
        Dictionary of cookie key-value pairs.
    """
    cookies = {}
    if not cookies_str:
        return cookies
    for item in cookies_str.split(";"):
        item = item.strip()
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


def cookies_dict_to_str(cookies_dict: dict) -> str:
    """Convert cookies dictionary back to string.

    Args:
        cookies_dict: Dictionary of cookies.

    Returns:
        Cookie string like 'key1=val1; key2=val2'.
    """
    return "; ".join(f"{k}={v}" for k, v in cookies_dict.items())


def get_timestamp() -> str:
    """Get current timestamp string.

    Returns:
        Timestamp string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_dir(path: str) -> None:
    """Ensure the directory for a file path exists.

    Args:
        path: File path whose parent directory should exist.
    """
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)


def build_response(success: bool, data=None, message: str = "ok",
                   error_code: str = None) -> dict:
    """Build a standardized response dict.

    Args:
        success: Whether the operation succeeded.
        data: Response data payload.
        message: Response message.
        error_code: Error code string if failed.

    Returns:
        Standardized response dictionary.
    """
    resp = {"success": success, "data": data, "message": message}
    if error_code:
        resp["error_code"] = error_code
    return resp
