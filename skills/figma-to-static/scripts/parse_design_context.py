#!/usr/bin/env python3
"""Parse Figma MCP design-context files and extract/download asset URLs.

Usage:
  python3 scripts/parse_design_context.py \
    --context source/mcp-assets/context-0-6715.txt \
    --assets-dir assets \
    --manifest source/context-assets.json

Features:
- Extracts https://www.figma.com/api/mcp/asset/... URLs from context text
- Downloads assets with type-aware extension correction (svg/png/jpg/webp)
- Normalizes SVGs to avoid stretch issues (preserveAspectRatio="none" -> xMidYMid meet)
- Writes a machine-readable manifest JSON
"""

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ASSET_URL_RE = re.compile(r"https://www\.figma\.com/api/mcp/asset/[^\s\)\]\"']+")


def detect_ext(content_type, blob, fallback="bin"):
    ctype = (content_type or "").lower()
    sig = blob[:16]

    if "svg" in ctype or b"<svg" in blob[:300].lower():
        return "svg"
    if "png" in ctype or sig.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if "jpeg" in ctype or "jpg" in ctype or sig.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if "webp" in ctype or (sig[:4] == b"RIFF" and b"WEBP" in sig):
        return "webp"

    return fallback


def safe_stem_from_url(url):
    path = urlparse(url).path.rstrip("/")
    last = path.split("/")[-1] or "asset"
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", last).strip("-")
    return cleaned or "asset"


def normalize_svg_file(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    orig = text

    # Replace stretch behavior that distorts logos/icons
    text = text.replace('preserveAspectRatio="none"', 'preserveAspectRatio="xMidYMid meet"')

    # Add sane default when missing
    if "<svg" in text and "preserveAspectRatio=" not in text:
        text = re.sub(r"<svg\b", '<svg preserveAspectRatio="xMidYMid meet"', text, count=1)

    changed = text != orig
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def download_asset(url, out_dir):
    req = Request(url, headers={"User-Agent": "figma-to-static/1.0", "Accept": "*/*"})
    with urlopen(req, timeout=60) as resp:
        blob = resp.read()
        ctype = resp.headers.get("Content-Type", "")

    ext = detect_ext(ctype, blob)
    stem = safe_stem_from_url(url)
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    filename = f"{stem}-{digest}.{ext}"

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    path.write_bytes(blob)

    svg_normalized = False
    if ext == "svg":
        svg_normalized = normalize_svg_file(path)

    return {
        "url": url,
        "file": str(path),
        "bytes": len(blob),
        "contentType": ctype,
        "ext": ext,
        "svgNormalized": svg_normalized,
    }


def extract_urls(text):
    urls = ASSET_URL_RE.findall(text)
    # preserve order + dedupe
    seen = set()
    ordered = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    return ordered


def main():
    p = argparse.ArgumentParser(description="Parse MCP design context and download asset URLs")
    p.add_argument("--context", action="append", default=[], help="Path to context-*.txt (repeatable)")
    p.add_argument("--context-glob", action="append", default=[], help="Glob pattern for context files (repeatable)")
    p.add_argument("--assets-dir", default="./assets")
    p.add_argument("--manifest", default="./source/context-assets.json")
    p.add_argument("--no-download", action="store_true", help="Only parse URLs without downloading")
    args = p.parse_args()

    context_files = [Path(x) for x in args.context]
    for pattern in args.context_glob:
        context_files.extend(sorted(Path().glob(pattern)))

    # Dedupe while preserving order
    seen_paths = set()
    ordered = []
    for pth in context_files:
        r = str(pth)
        if r not in seen_paths:
            seen_paths.add(r)
            ordered.append(Path(r))
    context_files = ordered

    if not context_files:
        raise SystemExit("No context files found. Use --context or --context-glob.")
    all_records = []
    total_urls = 0

    for cpath in context_files:
        text = cpath.read_text(encoding="utf-8", errors="ignore")
        urls = extract_urls(text)
        total_urls += len(urls)

        if not urls:
            all_records.append({"context": str(cpath), "assets": []})
            print(f"{cpath}: 0 asset URLs")
            continue

        print(f"{cpath}: {len(urls)} asset URL(s)")
        assets = []
        for u in urls:
            if args.no_download:
                assets.append({"url": u})
                print(f"  URL: {u}")
            else:
                rec = download_asset(u, Path(args.assets_dir))
                assets.append(rec)
                marker = " (svg fixed)" if rec.get("svgNormalized") else ""
                print(f"  saved: {rec['file']} [{rec['bytes']} bytes]{marker}")

        all_records.append({"context": str(cpath), "assets": assets})

    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "contexts": all_records,
        "totalContextFiles": len(context_files),
        "totalAssetUrls": total_urls,
        "downloaded": not args.no_download,
    }

    mpath = Path(args.manifest)
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nManifest saved: {mpath}")


if __name__ == "__main__":
    main()
