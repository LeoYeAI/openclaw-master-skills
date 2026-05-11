import binascii
import pathlib
import requests


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex-encoded audio to bytes."""
    return binascii.unhexlify(hex_str)


def save_bytes(data: bytes, output_path: str) -> str:
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path)


def download_url(url: str, output_path: str) -> str:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return save_bytes(resp.content, output_path)
