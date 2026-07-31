#!/usr/bin/env python3
"""Validate the version history in RELEASES.md and CHANGELOG.md.

Nothing used to check these files, so eight consecutive weekly entries all
shipped labelled v0.13.0 while the git tag for each of those dates carried a
distinct version. The duplicate labels also make the publish path ambiguous:
it resolves the release version by taking the first "## [vX.Y.Z]" match in
CHANGELOG.md, which silently picks one of several entries when a version
repeats.

Checks per file:
  * every entry header parses as "## [vX.Y.Z] - YYYY-MM-DD"
  * no version number appears twice (the literal 'untagged' placeholder is
    exempt: two historical runs were never tagged, so no real number exists
    for them)
  * entries are ordered newest-first by date
  * the version the publish path would resolve appears exactly once

Exits non-zero with the offending lines on failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS = ['CHANGELOG.md', 'RELEASES.md']

# Matches the headers both files use. CHANGELOG.md brackets the version
# ('## [v0.22.0] — 2026-07-30'), RELEASES.md does not ('## v0.22.0 — ...'), and
# both hyphen and em dash have been used as the separator over time.
HEADER_RE = re.compile(
    r'^## \[?(v[0-9]+\.[0-9]+\.[0-9]+|untagged)\]?\s*[-—–]\s*(\d{4}-\d{2}-\d{2})\s*$')
# Any line that looks like an entry header, so malformed ones are reported rather
# than skipped by the stricter pattern above. Must also catch the 'untagged'
# placeholder, or entries missing a version number would be silently ignored.
LOOSE_RE = re.compile(r'^## \[?(?:v[0-9]|untagged)')
PLACEHOLDER = 'untagged'


def check(path: Path) -> list[str]:
    problems: list[str] = []
    entries: list[tuple[str, str, int]] = []

    for lineno, line in enumerate(path.read_text(encoding='utf-8').split('\n'), 1):
        if not LOOSE_RE.match(line):
            continue
        m = HEADER_RE.match(line)
        if not m:
            problems.append(
                f'{path.name}:{lineno} malformed entry header: {line.strip()!r} '
                f'(expected "## [vX.Y.Z] — YYYY-MM-DD")')
            continue
        # Normalise 'v0.22.0' -> '0.22.0' so the placeholder stays distinct.
        ver = m.group(1)
        entries.append((ver[1:] if ver.startswith('v') else ver,
                        m.group(2), lineno))

    if not entries:
        return [f'{path.name}: no version entries found']

    seen: dict[str, int] = {}
    for ver, _date, lineno in entries:
        if ver == PLACEHOLDER:
            continue
        if ver in seen:
            problems.append(
                f'{path.name}:{lineno} v{ver} already used at line {seen[ver]}; '
                f'each release needs its own version number')
        else:
            seen[ver] = lineno

    for i in range(len(entries) - 1):
        (_, d1, l1), (_, d2, l2) = entries[i], entries[i + 1]
        if d1 < d2:
            problems.append(
                f'{path.name}:{l2} entry dated {d2} comes after {d1} '
                f'(line {l1}); entries must be newest-first')

    # publish_release() resolves the version by first match in CHANGELOG.md.
    # If that version repeats, the tag and release notes can disagree.
    if path.name == 'CHANGELOG.md':
        first = entries[0][0]
        if first == PLACEHOLDER:
            problems.append(
                f'{path.name}:{entries[0][2]} newest entry has no version number; '
                f'the publish step cannot resolve a release version')
        elif [v for v, _, _ in entries].count(first) > 1:
            problems.append(
                f'{path.name}: newest version v{first} appears more than once; '
                f'the publish step would pick one arbitrarily')

    print(f'{path.name}: {len(entries)} entries, '
          f'{len(seen)} distinct versions, newest first')
    return problems


def main() -> int:
    problems: list[str] = []
    for name in TARGETS:
        path = REPO_ROOT / name
        if not path.exists():
            problems.append(f'{name}: missing')
            continue
        problems.extend(check(path))

    if problems:
        print()
        for p in problems:
            print(f'  {p}')
        print(f'\nversion history invalid: {len(problems)} problem(s)')
        return 1

    print('version history OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
