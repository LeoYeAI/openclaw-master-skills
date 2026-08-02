#!/usr/bin/env python3
"""Validate the hand-maintained "Skill | Description" tables in the READMEs.

Why this exists: README.md / README.zh-CN.md carry a curated 2-column table that
collect.sh never rewrites, so nothing caught these defects for months:

  - 27 rows whose description was a bare YAML block indicator (`>`, `|`, `>-`),
    copied straight out of a skill's frontmatter (`ai-humanizer`, `edge-tts`, ...)
  - `clawsec` with an empty description cell
  - `skill-finder-cn` whose description contains unescaped `|`, silently turning
    that row into 4 columns and breaking the table render
  - 48 rows that were appended rather than inserted, so they sat outside any
    table: 46 after a blank line mid-body (which closes a table in GFM) and 2
    stranded past `## License` at end of file. Each row was individually well
    formed, which is why row-by-row validation passed them for months, while
    GitHub rendered them as a paragraph of literal `| [`slug`](path) | ... |`.

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
# "## 📦 Skill Index (388 curated skills)" / "## 📦 技能索引 (339 个精选技能)".
# The number is the only part that has to be right, so the surrounding words are
# left free for each translation.
INDEX_HEADER_RE = re.compile(r'^## .*?\((\d+)[^)]*\)\s*$')
SECTION_RE = re.compile(r'^### (.+?) \((\d+)\)\s*$')
SEPARATOR_RE = re.compile(r'^\|-+\|-+\|\s*$')
MIN_DESC = 12


def check_rows_in_tables(path: Path, lines: list[str]) -> list[str]:
    """Every skill row must sit inside a live table body.

    A blank line terminates a table in GitHub-flavoured markdown. Rows after one
    have no header row or separator above them, so GitHub renders them as a
    paragraph of literal pipe text rather than table rows -- 48 rows in
    README.md shipped that way.

    The row regex matches such a line perfectly, so this is the only check that
    can see the defect: track whether a separator has opened a table, and treat
    any blank line as closing it again.
    """
    problems: list[str] = []
    in_table = False
    for lineno, line in enumerate(lines, 1):
        if SEPARATOR_RE.match(line):
            in_table = True
            continue
        if SECTION_RE.match(line) or line.strip() == '':
            in_table = False
            continue
        m = ROW_RE.match(line)
        if m and not in_table:
            problems.append(
                f'{path.name}:{lineno} [{m.group(1)}] row is outside any table '
                f'(no header/separator above it); GitHub renders it as literal '
                f'text, not a table row')
    return problems


def check_counts(path: Path, lines: list[str]) -> list[str]:
    """The index header and per-section counts must match the rows present.

    Nothing regenerates these numbers, so they rot silently: the header claimed
    561 skills against 388 rows in README.md and 560 against 339 in
    README.zh-CN.md. The per-section counts happened to be right, but only by
    luck, so both are checked.
    """
    problems: list[str] = []
    header_claim = header_line = None
    sections: list[tuple[str, int, int, int]] = []   # title, claimed, actual, lineno
    cur: list | None = None

    for lineno, line in enumerate(lines, 1):
        if header_claim is None:
            m = INDEX_HEADER_RE.match(line)
            if m:
                header_claim, header_line = int(m.group(1)), lineno
                continue
        m = SECTION_RE.match(line)
        if m:
            if cur:
                sections.append(tuple(cur))
            cur = [m.group(1), int(m.group(2)), 0, lineno]
            continue
        if ROW_RE.match(line) and cur:
            cur[2] += 1
    if cur:
        sections.append(tuple(cur))

    total = sum(s[2] for s in sections)
    for title, claimed, actual, lineno in sections:
        if claimed != actual:
            problems.append(f'{path.name}:{lineno} section {title!r} claims '
                            f'{claimed} skills but has {actual} rows')
    if header_claim is None:
        problems.append(f'{path.name}: no "## ... (N skills)" index header found')
    elif header_claim != total:
        problems.append(f'{path.name}:{header_line} index header claims '
                        f'{header_claim} skills but the table has {total} rows')
    return problems


def check(path: Path) -> list[str]:
    problems: list[str] = []
    rows = 0
    lines = path.read_text(encoding='utf-8').split('\n')
    for lineno, line in enumerate(lines, 1):
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
        else:
            # A row that keeps the previous row's link still points at a real
            # directory, so the existence check above passes and the README
            # quietly sends readers to the wrong skill. The row label and the
            # link have to name the same directory.
            linked = link.rstrip('/').split('/')[-1]
            if linked != slug:
                problems.append(f'{where} row is labelled `{slug}` but links to '
                                f'{link} (expected skills/{slug}/)')

    if rows == 0:
        problems.append(f'{path.name}: no skill rows matched — table format changed?')
    else:
        problems.extend(check_counts(path, lines))
        problems.extend(check_rows_in_tables(path, lines))
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
