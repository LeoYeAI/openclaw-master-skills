#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import List, Dict


def normalize(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()


def is_within_root(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def list_entries(root: Path, current: Path) -> List[Path]:
    if not current.exists() or not current.is_dir():
        raise FileNotFoundError(f"Directory not found: {current}")
    if not is_within_root(root, current):
        raise PermissionError(f"Path escapes root: {current}")
    return sorted(current.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))


def build_items(entries: List[Path], prefix: str, start_index: int = 1) -> List[Dict[str, str]]:
    items = []
    for i, entry in enumerate(entries, start=start_index):
        items.append({
            "id": f"{prefix}{i}",
            "name": entry.name,
            "path": str(entry),
            "type": "dir" if entry.is_dir() else "file"
        })
    return items


def paginate(entries: List[Path], page: int, page_size: int) -> tuple[List[Path], int, int]:
    total = len(entries)
    total_pages = max(1, (total + page_size - 1) // page_size)
    safe_page = max(1, min(page, total_pages))
    start = (safe_page - 1) * page_size
    end = start + page_size
    return entries[start:end], safe_page, total_pages


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("current")
    ap.add_argument("--prefix", default="i")
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--page-size", type=int, default=12)
    args = ap.parse_args()

    root = normalize(args.root)
    current = normalize(args.current)
    entries = list_entries(root, current)
    page_entries, safe_page, total_pages = paginate(entries, args.page, args.page_size)
    items = build_items(page_entries, args.prefix)
    out = {
        "root": str(root),
        "path": str(current),
        "page": safe_page,
        "pageSize": args.page_size,
        "totalItems": len(entries),
        "totalPages": total_pages,
        "hasPrev": safe_page > 1,
        "hasNext": safe_page < total_pages,
        "items": items
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
