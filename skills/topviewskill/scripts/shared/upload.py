"""Upload local files to Topview S3 and return fileId.

Used internally by avatar4 and video_gen to auto-upload local paths.
"""

import os
import sys

from .client import TopviewClient

SUPPORTED_FORMATS = {
    "png", "jpg", "jpeg", "bmp", "webp",
    "mp3", "wav", "m4a",
    "mp4", "avi", "mov",
}


def detect_format(file_path: str) -> str:
    """Return file extension if supported, else raise SystemExit."""
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )
    return ext


def upload_file(file_path: str, fmt: str, *, quiet: bool = False,
                client: TopviewClient | None = None) -> dict:
    """Three-step upload: get credential -> PUT to S3 -> verify.

    Returns dict with keys: fileId, fileName, format.
    """
    if client is None:
        client = TopviewClient()

    if not quiet:
        print(f"[1/3] Requesting upload credential (format={fmt})...", file=sys.stderr)

    cred = client.get("/v1/upload/credential", params={
        "format": fmt,
        "needAccelerateUrl": "",
    })

    file_id = cred["fileId"]
    upload_url = cred["uploadUrl"]
    file_name = cred.get("fileName", "")

    if not quiet:
        print(f"[2/3] Uploading {os.path.basename(file_path)} to S3...", file=sys.stderr)

    client.put_file(upload_url, file_path)

    if not quiet:
        print("[3/3] Verifying upload...", file=sys.stderr)

    check = client.get("/v1/upload/check", params={"fileId": file_id})

    if check is not True and str(check) != "true":
        raise RuntimeError("Upload verification failed")

    if not quiet:
        print("Upload complete.", file=sys.stderr)

    return {"fileId": file_id, "fileName": file_name, "format": fmt}


def resolve_local_file(file_ref: str, *, quiet: bool = False,
                       client: TopviewClient | None = None) -> str:
    """If file_ref is a local path, upload it and return fileId. Otherwise pass through."""
    if os.path.isfile(file_ref):
        if not quiet:
            print(f"Detected local file, uploading: {file_ref}", file=sys.stderr)
        fmt = detect_format(file_ref)
        result = upload_file(file_ref, fmt, quiet=quiet, client=client)
        file_id = result["fileId"]
        if not quiet:
            print(f"Uploaded. fileId: {file_id}", file=sys.stderr)
        return file_id
    return file_ref
