#!/usr/bin/env python3
"""Convert KIPRIS Plus XML response on stdin to JSONL on stdout.

Usage: _xml2jsonl.py [xpath]   (default xpath = body/items/item)
"""
import sys, json, re
import xml.etree.ElementTree as ET

xpath = sys.argv[1] if len(sys.argv) > 1 else "body/items/item"
data = sys.stdin.buffer.read()
if not data:
    sys.exit(0)

try:
    root = ET.fromstring(data)
except ET.ParseError as e:
    print(json.dumps({"_error": f"xml parse: {e}",
                      "_raw_head": data[:300].decode("utf-8", "replace")}))
    sys.exit(1)

hdr = root.find("header")
if hdr is not None:
    success = (hdr.findtext("successYN") or "").upper()
    code = hdr.findtext("resultCode") or ""
    msg = hdr.findtext("resultMsg") or ""
    if success == "N" or code not in ("", "00"):
        print(json.dumps({"_error": msg, "_resultCode": code}, ensure_ascii=False))
        sys.exit(0)


def norm(tag):
    return re.sub(r"^\{[^}]*\}", "", tag)


items = root.findall(xpath)
if not items:
    items = root.findall("body/items/item")
if not items:
    items = root.findall(".//item")
if not items:
    body = root.find("body")
    if body is not None and len(body) > 0:
        items = [body]

for it in items:
    obj = {}
    for child in it:
        tag = norm(child.tag)
        text = (child.text or "").strip()
        if list(child):
            sub = {norm(c.tag): (c.text or "").strip() for c in child}
            obj[tag] = {k: v for k, v in sub.items() if v}
        else:
            obj[tag] = text or None
    print(json.dumps(obj, ensure_ascii=False))
