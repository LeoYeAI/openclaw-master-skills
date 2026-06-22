#!/usr/bin/env python3
"""
Search installed Skills by keyword/regex.

This is a helper for the "Skill discovery protocol" (reuse-first).
It scans for SKILL.md files under a root directory, parses YAML
frontmatter when present, and ranks results by match score.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


@dataclass(frozen=True)
class SkillHit:
    score: int
    name: str
    skill_dir: Path
    skill_file: Path
    description: str
    first_match: Optional[Tuple[int, str]]  # (1-based line number, line text)


def _read_text(path: Path) -> str:
    # utf-8-sig handles BOM transparently.
    return path.read_text(encoding="utf-8-sig", errors="replace")


def _split_frontmatter(text: str) -> Tuple[Optional[str], str]:
    """
    Returns (frontmatter_yaml, body).
    Only supports the common '---' delimiter at the file start.
    """
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :])
            return fm, body
    return None, text


def _parse_frontmatter(fm: Optional[str]) -> Dict[str, Any]:
    if not fm:
        return {}
    if yaml is None:
        return {"__raw_frontmatter__": fm}
    try:
        data = yaml.safe_load(fm) or {}
        return data if isinstance(data, dict) else {"__raw_frontmatter__": fm}
    except Exception:
        return {"__raw_frontmatter__": fm}


def _compile_query(query: str, is_regex: bool) -> re.Pattern[str]:
    pattern = query if is_regex else re.escape(query)
    return re.compile(pattern, re.IGNORECASE)


def _count_matches(rx: re.Pattern[str], s: str) -> int:
    return len(rx.findall(s))


def _first_matching_line(rx: re.Pattern[str], text: str) -> Optional[Tuple[int, str]]:
    for idx, line in enumerate(text.splitlines(), start=1):
        if rx.search(line):
            return idx, line.strip()
    return None


def _shorten(s: str, max_len: int = 140) -> str:
    s = " ".join(s.split())
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _iter_skill_files(root: Path) -> Iterable[Path]:
    # Only scan SKILL.md files; ignore common cache dirs.
    for p in root.rglob("SKILL.md"):
        if any(part in {"__pycache__", ".git", "node_modules"} for part in p.parts):
            continue
        yield p


def _make_hit(rx: re.Pattern[str], skill_md: Path) -> Optional[SkillHit]:
    text = _read_text(skill_md)
    fm, body = _split_frontmatter(text)
    meta = _parse_frontmatter(fm)

    name = str(meta.get("name") or skill_md.parent.name)
    desc = str(meta.get("description") or "")

    name_hits = _count_matches(rx, name)
    desc_hits = _count_matches(rx, desc)
    body_hits = _count_matches(rx, body)

    score = name_hits * 5 + desc_hits * 3 + body_hits
    if score <= 0:
        return None

    first = _first_matching_line(rx, text)
    return SkillHit(
        score=score,
        name=name,
        skill_dir=skill_md.parent,
        skill_file=skill_md,
        description=desc,
        first_match=first,
    )


def search_skills(root: Path, query: str, is_regex: bool) -> List[SkillHit]:
    rx = _compile_query(query, is_regex)
    hits: List[SkillHit] = []
    for skill_md in _iter_skill_files(root):
        hit = _make_hit(rx, skill_md)
        if hit:
            hits.append(hit)
    hits.sort(key=lambda h: (-h.score, h.name.lower(), str(h.skill_file).lower()))
    return hits


def main(argv: Optional[List[str]] = None) -> int:
    # Avoid UnicodeEncodeError on Windows consoles using legacy encodings (e.g., cp936/gbk).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Search installed Skills by keyword/regex.")
    ap.add_argument("query", help="Keyword (default) or regex (when --regex).")
    ap.add_argument(
        "--root",
        default=".claude/skills",
        help="Root directory to scan (default: .claude/skills).",
    )
    ap.add_argument("--regex", action="store_true", help="Treat query as regex.")
    ap.add_argument("--max", type=int, default=20, help="Max results to print.")
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.exists():
        print(f"[ERROR] Root not found: {root}", file=sys.stderr)
        return 2

    hits = search_skills(root, args.query, args.regex)
    print(f'Found {len(hits)} matching skills under "{root}" for query "{args.query}".')
    for h in hits[: max(0, args.max)]:
        print(f"- [{h.score:>3}] {h.name} ({h.skill_dir.as_posix()})")
        if h.description:
            print(f"      desc: {_shorten(h.description)}")
        if h.first_match:
            ln, line = h.first_match
            print(f"     match: SKILL.md:{ln}: {_shorten(line)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
