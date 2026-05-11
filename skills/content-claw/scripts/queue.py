"""
Content Claw - Content Queue

Indexes all generated content across runs. Shows unpublished, published, and pending items.

Usage:
    uv run queue.py [--brand <name>] [--status unpublished|published|all]
"""

import json
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent


def scan_runs(brand_filter: str | None = None) -> list[dict]:
    """Scan all content run directories and build a queue index."""
    content_dir = BASE / "content"
    if not content_dir.exists():
        return []

    items = []
    for d in sorted(content_dir.iterdir(), reverse=True):
        if not d.is_dir() or d.name.startswith("."):
            continue

        # Load metadata
        meta_file = d / "metadata.json"
        meta = {}
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
            except json.JSONDecodeError:
                pass

        # Filter by brand
        if brand_filter and meta.get("brand", "").lower() != brand_filter.lower():
            continue

        # Load publish records
        records_file = d / "publish_records.json"
        publish_records = []
        if records_file.exists():
            try:
                publish_records = json.loads(records_file.read_text())
            except json.JSONDecodeError:
                pass

        # Find content files
        text_files = list(d.glob("*.md"))
        spec_files = list(d.glob("*-spec.json"))
        image_files = list(d.glob("*.png")) + list(d.glob("*.jpg"))

        # Determine publish status
        published_platforms = set()
        for r in publish_records:
            if r.get("status") in ("published", "submitted"):
                published_platforms.add(r.get("platform", ""))

        # Determine available platforms from specs
        available_platforms = set()
        for sf in spec_files:
            try:
                spec = json.loads(sf.read_text())
                if "platform" in spec:
                    available_platforms.add(spec["platform"])
            except json.JSONDecodeError:
                pass

        unpublished_platforms = available_platforms - published_platforms

        item = {
            "run_dir": str(d),
            "run_name": d.name,
            "recipe": meta.get("recipe", d.name.split("_", 1)[-1] if "_" in d.name else "unknown"),
            "brand": meta.get("brand"),
            "timestamp": meta.get("timestamp", ""),
            "blocks": len(text_files) + len(image_files),
            "text_files": [f.name for f in text_files],
            "image_files": [f.name for f in image_files],
            "published_to": list(published_platforms),
            "unpublished_for": list(unpublished_platforms),
            "status": "published" if published_platforms and not unpublished_platforms else "partial" if published_platforms else "unpublished",
        }

        # Get text preview
        if text_files:
            item["preview"] = text_files[0].read_text()[:150].replace("\n", " ")

        items.append(item)

    return items


def main():
    brand = None
    status_filter = "all"

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--brand" and i + 1 < len(args):
            brand = args[i + 1]
            i += 2
        elif args[i] == "--status" and i + 1 < len(args):
            status_filter = args[i + 1]
            i += 2
        else:
            i += 1

    items = scan_runs(brand)

    if status_filter != "all":
        items = [it for it in items if it["status"] == status_filter]

    output = {
        "scanned_at": datetime.now().isoformat(),
        "total": len(items),
        "unpublished": len([i for i in items if i["status"] == "unpublished"]),
        "published": len([i for i in items if i["status"] == "published"]),
        "partial": len([i for i in items if i["status"] == "partial"]),
        "items": items,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
