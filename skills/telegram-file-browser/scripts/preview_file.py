#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh", ".zsh", ".html", ".css", ".xml"
}


def looks_textual(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    try:
        chunk = path.read_bytes()[:1024]
    except Exception:
        return False
    return b"\x00" not in chunk


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--max-lines", type=int, default=80)
    ap.add_argument("--max-chars", type=int, default=4000)
    args = ap.parse_args()

    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        raise SystemExit(json.dumps({"ok": False, "error": f"Not found: {path}"}, ensure_ascii=False))

    if path.is_dir():
        print(json.dumps({
            "ok": True,
            "kind": "directory",
            "path": str(path),
            "message": "Target is a directory"
        }, ensure_ascii=False, indent=2))
        return

    if not looks_textual(path):
        stat = path.stat()
        print(json.dumps({
            "ok": True,
            "kind": "binary",
            "path": str(path),
            "size": stat.st_size,
            "message": "Binary or unsupported file; prefer metadata/path output"
        }, ensure_ascii=False, indent=2))
        return

    text = path.read_text(errors="replace")
    lines = text.splitlines()
    clipped_lines = lines[:args.max_lines]
    clipped_text = "\n".join(clipped_lines)
    truncated = False
    if len(lines) > args.max_lines:
        truncated = True
    if len(clipped_text) > args.max_chars:
        clipped_text = clipped_text[:args.max_chars]
        truncated = True

    print(json.dumps({
        "ok": True,
        "kind": "text",
        "path": str(path),
        "preview": clipped_text,
        "lineCount": len(lines),
        "truncated": truncated
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
