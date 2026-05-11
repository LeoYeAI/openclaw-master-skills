"""
Content Claw - Source Bookmarking

Save URLs for later content generation.

Usage:
    uv run bookmark.py add <url> [--note "why this is interesting"]
    uv run bookmark.py list
    uv run bookmark.py remove <url>
"""

import json
import sys
from datetime import datetime
from pathlib import Path

BOOKMARKS_FILE = Path(__file__).parent.parent / "bookmarks.json"


def load_bookmarks() -> list[dict]:
    if BOOKMARKS_FILE.exists():
        return json.loads(BOOKMARKS_FILE.read_text())
    return []


def save_bookmarks(bookmarks: list[dict]):
    BOOKMARKS_FILE.write_text(json.dumps(bookmarks, indent=2))


def add(url: str, note: str = ""):
    bookmarks = load_bookmarks()
    if any(b["url"] == url for b in bookmarks):
        return {"status": "exists", "url": url}
    bookmarks.append({
        "url": url,
        "note": note,
        "added_at": datetime.now().isoformat(),
        "used": False,
    })
    save_bookmarks(bookmarks)
    return {"status": "added", "url": url, "total": len(bookmarks)}


def list_all():
    bookmarks = load_bookmarks()
    return {
        "total": len(bookmarks),
        "unused": len([b for b in bookmarks if not b.get("used")]),
        "bookmarks": bookmarks,
    }


def remove(url: str):
    bookmarks = load_bookmarks()
    before = len(bookmarks)
    bookmarks = [b for b in bookmarks if b["url"] != url]
    save_bookmarks(bookmarks)
    return {"status": "removed" if len(bookmarks) < before else "not_found", "url": url}


def mark_used(url: str):
    bookmarks = load_bookmarks()
    for b in bookmarks:
        if b["url"] == url:
            b["used"] = True
            b["used_at"] = datetime.now().isoformat()
    save_bookmarks(bookmarks)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: bookmark.py add|list|remove <url> [--note text]"}))
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "add requires <url>"}))
            sys.exit(1)
        url = sys.argv[2]
        note = ""
        if "--note" in sys.argv:
            idx = sys.argv.index("--note")
            if idx + 1 < len(sys.argv):
                note = sys.argv[idx + 1]
        print(json.dumps(add(url, note), indent=2))

    elif cmd == "list":
        print(json.dumps(list_all(), indent=2))

    elif cmd == "remove":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "remove requires <url>"}))
            sys.exit(1)
        print(json.dumps(remove(sys.argv[2]), indent=2))

    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))


if __name__ == "__main__":
    main()
