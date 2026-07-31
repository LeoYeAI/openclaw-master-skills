#!/usr/bin/env python3
"""Validate the hand-maintained "Skill | Description" tables in the READMEs.

Why this exists: README.md / README.zh-CN.md carry a curated 2-column table that
collect.sh never rewrites, so nothing caught these defects for months:

  - 27 rows whose description was a bare YAML block indicator (`>`, `|`, `>-`),
    copied straight out of a skill's frontmatter (`ai-humanizer`, `edge-tts`, ...)
  - `clawsec` with an empty description cell
  - `skill-finder-cn` whose description contains unescaped `|`, silently turning
    that row into 4 columns and breaking the table render

Exits non-zero with a per-row report so a bad edit fails the weekly run instead
of shipping to GitHub and ClawHub.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS = ['README.md', 'README.zh-CN.md']

ROW_RE = re.compile(r'^\| \[`([^`]+)`\]\(([^)]+)\) \| (.*)$')
ARTIFACT_RE = re.compile(r'^[>|][-+]?$')
MIN_DESC = 12


def check(path: Path) -> list[str]:
    problems: list[str] = []
    rows = 0
    for lineno, line in enumerate(path.read_text(encoding='utf-8').split('\n'), 1):
        m = ROW_RE.match(line)
        if not m:
            continue
        rows += 1
        slug, link, rest = m.groups()
        where = f'{path.name}:{lineno} [{slug}]'

        # Unescaped pipes add phantom columns.
        if line.count(' | ') != 1:
            problems.append(f'{where} row has {line.count(" | ") + 1} columns; escape "|" in the description as "\\|"')

        desc = rest.rstrip().rstrip('|').strip()
        if not desc:
            problems.append(f'{where} empty description')
        elif ARTIFACT_RE.match(desc):
            problems.append(f'{where} description is a bare YAML block indicator ({desc!r})')
        elif len(desc) < MIN_DESC:
            problems.append(f'{where} description too short ({len(desc)} chars): {desc!r}')

        if not (REPO_ROOT / link.rstrip('/')).is_dir():
            problems.append(f'{where} link points at missing directory: {link}')

    if rows == 0:
        problems.append(f'{path.name}: no skill rows matched — table format changed?')
    else:
        print(f'{path.name}: {rows} rows checked')
    return problems


def main() -> int:
    problems: list[str] = []
    for name in TARGETS:
        path = REPO_ROOT / name
        if not path.is_file():
            problems.append(f'{name}: missing')
            continue
        problems.extend(check(path))

    if problems:
        print(f'\nREADME table validation FAILED ({len(problems)} problem(s)):')
        for p in problems:
            print(f'  - {p}')
        return 1
    print('README tables OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
