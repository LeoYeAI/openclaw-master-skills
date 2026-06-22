#!/usr/bin/env python3
"""
Universal (cross-project) validation for Skills content.

This script enforces a *high-confidence* subset of the "cross-project universal" rule:
- It flags obvious project-specific fingerprints like absolute user paths (Windows/macOS/Linux).

It intentionally avoids over-aggressive heuristics that would create many false positives.

Usage:
  python universal_validate.py <path/to/skill-folder>
Exit codes:
  0: no issues found
  1: violations found
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple


def _configure_stdio() -> None:
    """
    Avoid UnicodeEncodeError on Windows consoles (e.g., GBK) by ensuring
    unencodable characters are safely replaced instead of crashing.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            # Some environments replace stdio with objects that don't support reconfigure().
            pass


_configure_stdio()


@dataclass(frozen=True)
class Finding:
    file: Path
    line_no: int
    kind: str
    pattern_name: str
    excerpt: str


def iter_text_files(skill_dir: Path) -> Iterable[Path]:
    # Include Skill entry and common text/reference files.
    include_names = {"SKILL.md"}
    include_suffixes = {".md", ".txt", ".json", ".yaml", ".yml"}

    for p in skill_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.name in include_names or p.suffix.lower() in include_suffixes:
            # Skip huge binary-ish files if any mistakenly match.
            # (We only include common text suffixes; this is just a final guard.)
            yield p


def read_text_lines(path: Path) -> List[str]:
    # Use UTF-8 with BOM support. If a file isn't UTF-8, treat as a violation because
    # cross-platform skills should be portable and readable.
    try:
        return path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        return [
            "UNIVERSAL_VALIDATE_ERROR: file is not UTF-8 decodable; use UTF-8 encoding for portability."
        ]


def scan_lines(lines: List[str]) -> List[Tuple[int, str]]:
    return [(i + 1, line) for i, line in enumerate(lines)]


ERROR_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    # Windows absolute paths: C:\Users\name\..., D:\repo\...
    ("windows_drive_path", re.compile(r"(?i)\b[a-z]:\\[^ \t\r\n]+")),
    # Windows UNC paths: \\server\share\...
    ("windows_unc_path", re.compile(r"\\\\[^ \t\r\n]+")),
    # macOS/Linux user home paths: /Users/name/... or /home/name/...
    ("posix_user_home_path", re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/[^ \t\r\n]*")),
    # Tilde home paths: ~/...
    ("tilde_home_path", re.compile(r"~\/[^ \t\r\n]+")),
    # file:// URIs (often embed local paths)
    ("file_uri", re.compile(r"(?i)\bfile:///[^\s]+")),
]

def is_placeholder_match(match_text: str) -> bool:
    """
    Treat obvious placeholder examples as non-violations.

    We allow patterns like `C:\\...` or `/Users/...` used as generic examples in docs.
    This keeps the validator useful while avoiding self-failing documentation.
    """
    return "..." in match_text


def validate_universal(skill_dir: Path) -> Tuple[bool, List[Finding]]:
    findings: List[Finding] = []

    for file_path in iter_text_files(skill_dir):
        # Skip this skill's own LICENSE file — it is legal text and not part of "skill logic".
        if file_path.name.lower() == "license.txt":
            continue

        lines = read_text_lines(file_path)
        # If file is not decodable, treat as ERROR at line 1.
        if lines and lines[0].startswith("UNIVERSAL_VALIDATE_ERROR:"):
            findings.append(
                Finding(
                    file=file_path,
                    line_no=1,
                    kind="ERROR",
                    pattern_name="non_utf8_file",
                    excerpt=lines[0],
                )
            )
            continue

        for line_no, line in scan_lines(lines):
            for pattern_name, pattern in ERROR_PATTERNS:
                m = pattern.search(line)
                if not m:
                    continue
                if is_placeholder_match(m.group(0)):
                    continue
                excerpt = line.strip()
                if len(excerpt) > 240:
                    excerpt = excerpt[:237] + "..."
                findings.append(
                    Finding(
                        file=file_path,
                        line_no=line_no,
                        kind="ERROR",
                        pattern_name=pattern_name,
                        excerpt=excerpt,
                    )
                )

    ok = not any(f.kind == "ERROR" for f in findings)
    return ok, findings


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python universal_validate.py <skill_directory>")
        return 1

    skill_dir = Path(sys.argv[1]).resolve()
    if not skill_dir.exists() or not skill_dir.is_dir():
        print(f"[ERROR] skill directory not found or not a directory: {skill_dir}")
        return 1

    ok, findings = validate_universal(skill_dir)
    if ok:
        print("[OK] Universal validation passed (no high-confidence project-specific fingerprints found).")
        return 0

    print("[FAIL] Universal validation failed:")
    for f in findings:
        rel = f.file
        try:
            rel = f.file.relative_to(Path.cwd())
        except Exception:
            pass
        print(f"- {f.kind} {f.pattern_name} at {rel}:{f.line_no}: {f.excerpt}")

    print("\nFix guidance:")
    print("- Remove absolute user paths (C:\\..., /Users/..., /home/..., ~/...).")
    print("- Replace them with cross-project, relative, or conceptual descriptions (avoid project placeholders).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


