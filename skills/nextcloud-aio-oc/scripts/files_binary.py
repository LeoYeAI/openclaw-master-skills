#!/usr/bin/env python3
"""
Binary file transfer companion for the nextcloud-aio-oc skill.

The main nextcloud.js handles text-based file operations. This script
handles binary files (ODT, DOCX, PDF, images, etc.) that cannot be
safely round-tripped as text strings.

Reads credentials from environment variables (same as nextcloud.js):
  NEXTCLOUD_URL   - e.g. https://cloud.example.com
  NEXTCLOUD_USER  - username
  NEXTCLOUD_TOKEN - app password / token

Usage:
  python3 files_binary.py download <nc_path> <local_path>
  python3 files_binary.py upload   <local_path> <nc_path>
  python3 files_binary.py exists   <nc_path>
  python3 files_binary.py list     [<nc_path>]
"""

import base64
import os
import sys
import argparse
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET

# MIME types for common binary document formats
MIME_TYPES: dict[str, str] = {
    ".odt": "application/vnd.oasis.opendocument.text",
    ".ods": "application/vnd.oasis.opendocument.spreadsheet",
    ".odp": "application/vnd.oasis.opendocument.presentation",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def _config() -> tuple[str, str, str]:
    url = os.environ.get("NEXTCLOUD_URL", "").rstrip("/")
    user = os.environ.get("NEXTCLOUD_USER", "")
    token = os.environ.get("NEXTCLOUD_TOKEN", "")
    if not (url and user and token):
        print(
            "ERROR: NEXTCLOUD_URL, NEXTCLOUD_USER, and NEXTCLOUD_TOKEN must be set.",
            file=sys.stderr,
        )
        sys.exit(1)
    return url, user, token


def _dav_url(nc_path: str, url: str, user: str) -> str:
    nc_path = nc_path.lstrip("/")
    encoded = urllib.parse.quote(nc_path, safe="/")
    return f"{url}/remote.php/dav/files/{user}/{encoded}"


def _auth(user: str, token: str) -> dict:
    creds = base64.b64encode(f"{user}:{token}".encode()).decode()
    return {"Authorization": f"Basic {creds}"}


def _mime_for(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return MIME_TYPES.get(ext, "application/octet-stream")


def cmd_download(nc_path: str, local_path: str) -> None:
    url, user, token = _config()
    dav_url = _dav_url(nc_path, url, user)
    req = urllib.request.Request(dav_url, headers=_auth(user, token))
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
        os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)
        print(f"OK downloaded {len(data):,} bytes: {nc_path} -> {local_path}")
    except urllib.error.HTTPError as e:
        print(f"ERROR HTTP {e.code}: {e.reason} — {dav_url}", file=sys.stderr)
        sys.exit(1)


def cmd_upload(local_path: str, nc_path: str) -> None:
    url, user, token = _config()
    dav_url = _dav_url(nc_path, url, user)
    with open(local_path, "rb") as f:
        data = f.read()
    headers = {
        **_auth(user, token),
        "Content-Type": _mime_for(nc_path),
    }
    req = urllib.request.Request(dav_url, data=data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
        print(f"OK uploaded {len(data):,} bytes: {local_path} -> {nc_path} (HTTP {status})")
    except urllib.error.HTTPError as e:
        print(f"ERROR HTTP {e.code}: {e.reason} — {dav_url}", file=sys.stderr)
        sys.exit(1)


def cmd_exists(nc_path: str) -> None:
    url, user, token = _config()
    dav_url = _dav_url(nc_path, url, user)
    req = urllib.request.Request(
        dav_url,
        headers={**_auth(user, token), "Depth": "0"},
        method="PROPFIND",
    )
    try:
        with urllib.request.urlopen(req):
            pass
        print(f"EXISTS {nc_path}")
        sys.exit(0)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"NOT_FOUND {nc_path}")
            sys.exit(1)
        print(f"ERROR HTTP {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(2)


def cmd_list(nc_path: str = "/") -> None:
    url, user, token = _config()
    dav_url = _dav_url(nc_path, url, user)
    body = (
        b'<?xml version="1.0"?>'
        b'<d:propfind xmlns:d="DAV:">'
        b"<d:prop><d:displayname/><d:resourcetype/><d:getcontenttype/><d:getcontentlength/></d:prop>"
        b"</d:propfind>"
    )
    headers = {
        **_auth(user, token),
        "Depth": "1",
        "Content-Type": "application/xml",
    }
    req = urllib.request.Request(dav_url, data=body, headers=headers, method="PROPFIND")
    try:
        with urllib.request.urlopen(req) as resp:
            xml_data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"ERROR HTTP {e.code}: {e.reason} — {dav_url}", file=sys.stderr)
        sys.exit(1)

    ns = {"d": "DAV:"}
    root = ET.fromstring(xml_data)
    entries = []
    for response in root.findall("d:response", ns):
        name = response.findtext("d:propstat/d:prop/d:displayname", namespaces=ns) or ""
        ctype = response.findtext("d:propstat/d:prop/d:getcontenttype", namespaces=ns) or ""
        size = response.findtext("d:propstat/d:prop/d:getcontentlength", namespaces=ns) or ""
        rtype_el = response.find("d:propstat/d:prop/d:resourcetype/d:collection", ns)
        kind = "dir" if rtype_el is not None else "file"
        if name:
            size_str = f"  {int(size):,} bytes" if size and kind == "file" else ""
            entries.append(f"[{kind}] {name}{size_str}")
    for entry in sorted(entries):
        print(entry)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Binary file transfer for NextCloud (companion to nextcloud.js)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("download", help="Download a binary file from NextCloud")
    p.add_argument("nc_path", help="NextCloud path, e.g. /Documents/report.odt")
    p.add_argument("local_path", help="Local destination path, e.g. /tmp/report.odt")

    p = sub.add_parser("upload", help="Upload a binary file to NextCloud")
    p.add_argument("local_path", help="Local file path")
    p.add_argument("nc_path", help="NextCloud destination path")

    p = sub.add_parser("exists", help="Check if a path exists (exit 0=yes, 1=no)")
    p.add_argument("nc_path", help="NextCloud path to check")

    p = sub.add_parser("list", help="List files in a NextCloud directory")
    p.add_argument("nc_path", nargs="?", default="/", help="Directory path (default: /)")

    args = parser.parse_args()

    if args.cmd == "download":
        cmd_download(args.nc_path, args.local_path)
    elif args.cmd == "upload":
        cmd_upload(args.local_path, args.nc_path)
    elif args.cmd == "exists":
        cmd_exists(args.nc_path)
    elif args.cmd == "list":
        cmd_list(args.nc_path)


if __name__ == "__main__":
    main()
