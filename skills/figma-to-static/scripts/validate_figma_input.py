#!/usr/bin/env python3
"""Validate Figma link/file accessibility and estimate whether target is a full page.

Usage examples:
  python3 scripts/validate_figma_input.py --figma-url "https://www.figma.com/design/FILEKEY/Name?node-id=0-1"
  FIGMA_TOKEN=xxx python3 scripts/validate_figma_input.py --figma-url "..." --check-api
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://api.figma.com/v1"


def parse_figma_url(url: str):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must start with http/https")

    host = parsed.netloc.lower()
    if "figma.com" not in host:
        raise ValueError("Not a figma.com URL")

    # Expected: /design/{fileKey}/..., /file/{fileKey}/...
    m = re.search(r"/(?:design|file)/([A-Za-z0-9]+)", parsed.path)
    if not m:
        raise ValueError("Cannot parse fileKey from URL path")

    file_key = m.group(1)
    q = urllib.parse.parse_qs(parsed.query)
    raw_node = (q.get("node-id") or [None])[0]
    node_id = raw_node.replace("-", ":") if raw_node else None

    return {
        "fileKey": file_key,
        "nodeId": node_id,
        "rawNodeId": raw_node,
        "host": host,
        "path": parsed.path,
    }


def req(url: str, token: str):
    r = urllib.request.Request(url, headers={"X-Figma-Token": token})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read())


def classify_full_page(node: dict):
    """Heuristic full-page classifier.

    Returns (is_full_like: bool, reason: str)
    """
    ntype = (node or {}).get("type", "")
    bbox = (node or {}).get("absoluteBoundingBox") or {}
    w = bbox.get("width")
    h = bbox.get("height")

    # If no geometry, keep conservative
    if w is None or h is None:
        if ntype in {"CANVAS", "FRAME", "SECTION"}:
            return True, f"type={ntype}, no bbox (likely page/container)"
        return False, f"type={ntype}, no bbox"

    # Practical heuristic for landing/full-screen-ish artboards
    # Most real full pages are tall and not tiny cards.
    if ntype in {"CANVAS", "SECTION"}:
        return True, f"type={ntype}, bbox={int(w)}x{int(h)}"

    if ntype == "FRAME":
        if h >= 1200 and w >= 320:
            return True, f"type=FRAME, bbox={int(w)}x{int(h)}"
        return False, f"type=FRAME, bbox={int(w)}x{int(h)} seems partial/component"

    return False, f"type={ntype}, bbox={int(w)}x{int(h)} seems component"


def main():
    p = argparse.ArgumentParser(description="Validate figma link + file/node status")
    p.add_argument("--figma-url", required=True, help="Figma URL from user")
    p.add_argument("--check-api", action="store_true", help="Use FIGMA_TOKEN to verify file/node via REST API")
    p.add_argument("--token", default=None, help="Optional FIGMA_TOKEN override")
    args = p.parse_args()

    try:
        parsed = parse_figma_url(args.figma_url)
    except ValueError as e:
        print(f"INVALID_URL: {e}")
        sys.exit(2)

    print("URL_OK")
    print(f"fileKey={parsed['fileKey']}")
    print(f"nodeId={parsed['nodeId'] or '(none)'}")

    if not args.check_api:
        if not parsed["nodeId"]:
            print("PAGE_HINT: no node-id provided; default target is whole file/page (likely full page).")
        else:
            print("PAGE_HINT: node-id provided; run --check-api to verify whether it's full page or component.")
        return

    token = args.token or os.environ.get("FIGMA_TOKEN")
    if not token:
        print("API_CHECK_SKIPPED: FIGMA_TOKEN missing (set env or --token)")
        return

    # Check file accessible
    try:
        file_meta = req(f"{API}/files/{parsed['fileKey']}?depth=1", token)
    except Exception as e:
        print(f"FILE_INVALID_OR_UNAUTHORIZED: {e}")
        sys.exit(3)

    name = file_meta.get("name", "(unknown)")
    print(f"FILE_OK: {name}")

    if not parsed["nodeId"]:
        print("FULL_PAGE_ASSESSMENT: likely full file/page (no node-id).")
        return

    nid = parsed["nodeId"]
    ids = urllib.parse.quote(nid, safe=":,")
    try:
        node_data = req(f"{API}/files/{parsed['fileKey']}/nodes?ids={ids}", token)
    except Exception as e:
        print(f"NODE_CHECK_FAILED: {e}")
        sys.exit(4)

    node_doc = (node_data.get("nodes") or {}).get(nid) or {}
    node = node_doc.get("document")
    if not node:
        print("NODE_INVALID: node not found in this file")
        sys.exit(5)

    full_like, reason = classify_full_page(node)
    if full_like:
        print(f"FULL_PAGE_ASSESSMENT: likely full-page target ({reason})")
    else:
        print(f"FULL_PAGE_ASSESSMENT: likely partial/component ({reason})")
        print("SUGGESTION: ask user for page-level FRAME/SECTION/CANVAS node-id or remove node-id for whole page.")


if __name__ == "__main__":
    main()
