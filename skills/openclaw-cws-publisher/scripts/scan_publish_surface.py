from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import abs_path, dump_json, dump_text, markdown_table, run


PATTERNS = {
    "absolute-path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "localhost-url": re.compile(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?"),
    "websocket-url": re.compile(r"ws://[^\s\"')]+"),
    "token-shaped": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{12,}|sk_[A-Za-z0-9]{12,})\b"),
    "google-client-id": re.compile(r"\b\d{10,}-[a-z0-9]{16,}\.apps\.googleusercontent\.com\b"),
}

REDACTION_LABELS = {
    "absolute-path": "<redacted:absolute-path>",
    "localhost-url": "<redacted:local-url>",
    "websocket-url": "<redacted:websocket-url>",
    "token-shaped": "<redacted:token>",
    "google-client-id": "<redacted:google-client-id>",
}

TEXT_EXTENSIONS = {
    ".cjs",
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


def tracked_files(root: Path) -> list[Path]:
    result = run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        timeout=15,
    )
    if result.returncode != 0:
        return [path for path in root.rglob("*") if path.is_file()]
    return [root / path for path in result.stdout.split("\0") if path]


def scan(root: Path) -> list[dict]:
    findings: list[dict] = []
    for path in tracked_files(root):
        if not path.exists() or not path.is_file():
            continue
        if path.name == "scan_publish_surface.py":
            continue
        if path.suffix and path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for kind, pattern in PATTERNS.items():
                match = pattern.search(line)
                if not match:
                    continue
                findings.append(
                    {
                        "kind": kind,
                        "path": str(path.relative_to(root)),
                        "line": line_number,
                        "excerpt": redacted_excerpt(kind, line),
                    }
                )
    return findings


def redacted_excerpt(kind: str, line: str) -> str:
    pattern = PATTERNS[kind]
    label = REDACTION_LABELS[kind]
    return pattern.sub(label, line.strip())[:220]


def render_markdown(findings: list[dict]) -> str:
    rows = [
        [finding["kind"], finding["path"], str(finding["line"]), finding["excerpt"]]
        for finding in findings
    ]
    return "\n".join(
        [
            "# Publish Surface Audit",
            "",
            f"Findings: **{len(findings)}**",
            "",
            markdown_table(["Kind", "Path", "Line", "Excerpt"], rows) if rows else "No findings.",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan a repo for obvious publish-surface leaks.")
    parser.add_argument("--root", required=True, help="Repo root to scan.")
    parser.add_argument("--json-out", required=True, help="JSON output path.")
    parser.add_argument("--markdown-out", required=True, help="Markdown output path.")
    args = parser.parse_args()

    findings = scan(abs_path(args.root))
    dump_json(args.json_out, {"count": len(findings), "findings": findings})
    dump_text(args.markdown_out, render_markdown(findings))
    print(f"Found {len(findings)} publish-surface findings")


if __name__ == "__main__":
    main()
