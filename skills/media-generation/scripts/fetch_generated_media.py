#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import uuid
from pathlib import Path
from urllib.parse import urlparse

import requests


def parse_args():
    p = argparse.ArgumentParser(description="Extract a generated media URL/path from model output and download it.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--response-text", help="Raw response text containing HTML, markdown, or direct media URLs")
    src.add_argument("--response-file", help="Path to a text file containing the raw response")
    p.add_argument("--origin", help="Prefix to use when the extracted media path is relative")
    p.add_argument("--out-dir", required=True, help="Directory to save the downloaded file into")
    p.add_argument("--prefix", default="generated", help="Output filename prefix")
    p.add_argument("--timeout", type=int, default=600, help="HTTP timeout in seconds")
    p.add_argument("--header", action="append", default=[], help="Extra header in 'Key: Value' format; repeatable")
    return p.parse_args()


def load_text(args):
    if args.response_text is not None:
        return args.response_text
    with open(args.response_file, "r", encoding="utf-8") as f:
        return f.read()


def extract_b64_json(text):
    try:
        payload = json.loads(text)
    except Exception:
        payload = None

    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("b64_json"):
                    return item["b64_json"]
        if payload.get("b64_json"):
            return payload["b64_json"]

    m = re.search(r'"b64_json"\s*:\s*"([A-Za-z0-9+/=\\n\\r]+)"', text)
    if m:
        return re.sub(r'\s+', '', m.group(1))
    return None


def extract_media_ref(text):
    preferred = [
        r'src=\\?"([^"]+generated_video\.mp4)\\?"',
        r'https?://[^\s"\'\\]+generated_video\.mp4',
        r'!\[video\]\(([^)]+)\)',
        r'!\[image\]\(([^)]+)\)',
        r'data:(image|video)/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=]+',
    ]
    for pat in preferred:
        m = re.search(pat, text)
        if m:
            ref = m.group(0) if pat.startswith('data:') else (m.group(1) if m.groups() else m.group(0))
            return ref.rstrip('\\').strip()

    fallback = [
        r'https?://[^\s"\'\\]+(?:\.jpg|\.jpeg|\.png|\.webp|\.gif|\.mp4|\.webm|\.mov)(?:\?[^\s"\'\\]*)?',
        r'/v1/files/[^\s"\')<]+',
    ]
    for pat in fallback:
        m = re.search(pat, text)
        if m:
            ref = m.group(1) if m.groups() else m.group(0)
            return ref.rstrip('\\').strip()
    return None


def parse_data_url(ref):
    m = re.match(r'data:([^;,]+);base64,(.+)', ref, re.DOTALL)
    if not m:
        raise SystemExit('invalid data URL')
    return m.group(1).strip().lower(), base64.b64decode(re.sub(r'\s+', '', m.group(2)))


def build_url(ref, origin):
    if ref.startswith('http://') or ref.startswith('https://'):
        return ref.rstrip('\\')
    if ref.startswith('data:'):
        return ref
    if not origin:
        raise SystemExit(f"relative media path found but --origin was not provided: {ref}")
    return origin.rstrip('/') + '/' + ref.lstrip('/')


def parse_headers(header_args):
    headers = {}
    for item in header_args:
        if ':' not in item:
            raise SystemExit(f"invalid --header value: {item}")
        k, v = item.split(':', 1)
        headers[k.strip()] = v.strip()
    return headers


def guess_extension(url, content_type):
    ct = (content_type or '').split(';', 1)[0].strip().lower()
    by_ct = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/webp': '.webp',
        'image/gif': '.gif',
        'video/mp4': '.mp4',
        'video/webm': '.webm',
        'video/quicktime': '.mov',
    }
    if ct in by_ct:
        return by_ct[ct]
    if url and not url.startswith('data:'):
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext:
            return ext
    return mimetypes.guess_extension(ct) or '.bin'


def save_bytes(out_dir, prefix, ext, content):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(out_dir) / f"{prefix}_{uuid.uuid4().hex[:8]}{ext}"
    out_path.write_bytes(content)
    return str(out_path)


def main():
    args = parse_args()
    text = load_text(args)

    b64_json = extract_b64_json(text)
    if b64_json:
        content = base64.b64decode(re.sub(r'\s+', '', b64_json))
        out_path = save_bytes(args.out_dir, args.prefix, '.png', content)
        print(out_path)
        return

    ref = extract_media_ref(text)
    if not ref:
        raise SystemExit('no media reference found in response')

    url = build_url(ref, args.origin)
    if url.startswith('data:'):
        content_type, content = parse_data_url(url)
        ext = guess_extension(url, content_type)
        out_path = save_bytes(args.out_dir, args.prefix, ext, content)
        print(out_path)
        return

    headers = parse_headers(args.header)
    resp = requests.get(url, headers=headers, timeout=args.timeout)
    resp.raise_for_status()

    ext = guess_extension(url, resp.headers.get('content-type'))
    out_path = save_bytes(args.out_dir, args.prefix, ext, resp.content)
    print(out_path)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise
