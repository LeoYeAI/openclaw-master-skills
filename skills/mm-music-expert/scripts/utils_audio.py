import binascii
import pathlib
import sys
import time
import requests


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex-encoded audio to bytes."""
    return binascii.unhexlify(hex_str)


def save_bytes(data: bytes, output_path: str) -> str:
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path)


def download_url(url: str, output_path: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=180)
            resp.raise_for_status()
            return save_bytes(resp.content, output_path)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt >= max_retries - 1:
                raise
            backoff = 5 * (2 ** attempt)
            print(
                f"[warning] Download failed, retry {attempt + 1}/{max_retries} "
                f"(backoff {backoff}s)...",
                file=sys.stderr,
            )
            time.sleep(backoff)
