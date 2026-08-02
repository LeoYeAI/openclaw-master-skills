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
  * the "新增 N ... 总计 M" counts are self-consistent, agree between the two
    files, and the newest total matches the skills actually in the tree

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

# '### 🚀 周更：新增 94 个 Skills，总计 2503'. Both numbers are hand-written by the
# weekly run, and nothing recomputed them: one entry claimed 32832 new skills
# against a total of 1209, because 32832 was the number of archive candidates
# scanned that week and no skill was actually added (git shows 1209 directories
# both before and after). Wording varies across historical entries, so only the
# two numbers are pinned.
COUNT_RE = re.compile(r'新增\s*([0-9]+)\s*个\s*Skills?.*?总计\s*([0-9]+)')
SKILLS_DIR = REPO_ROOT / 'skills'


def check_counts(path: Path, lines: list[str]) -> tuple[list[str], dict[str, tuple[int, int, int]]]:
    """Per-entry "+N -> M" claims must hold together and against the tree.

    Three independent assertions, because each catches a different mistake:
      * N <= M, since a week cannot add more skills than exist afterwards.
        This alone catches the 32832 entry.
      * consecutive totals must differ by exactly the newer entry's N, which
        catches a total that was not bumped or was bumped twice.
      * the newest total must equal the number of skill directories, which
        catches a release that ships a stale count.

    The delta check only runs on adjacent entries that both carry counts, so
    prose-only entries (v0.13.0 writes '611 → 1211 个精选 Skills（+600）') break
    the chain rather than producing a false positive.
    """
    problems: list[str] = []
    claims: dict[str, tuple[int, int, int]] = {}   # version -> (new, total, lineno)
    order: list[str] = []
    current: str | None = None

    for lineno, line in enumerate(lines, 1):
        m = HEADER_RE.match(line)
        if m:
            ver = m.group(1)
            current = f"{ver} ({m.group(2)})" if ver == PLACEHOLDER else ver
            order.append(current)
            continue
        m = COUNT_RE.search(line)
        if m and current and current not in claims:
            new, total = int(m.group(1)), int(m.group(2))
            claims[current] = (new, total, lineno)
            if new > total:
                problems.append(
                    f'{path.name}:{lineno} {current} claims {new} new skills but a '
                    f'total of only {total}')

    counted = [v for v in order if v in claims]
    for newer, older in zip(counted, counted[1:]):
        if order.index(older) != order.index(newer) + 1:
            continue        # an entry without counts sits between them
        new, total, lineno = claims[newer]
        _, prev_total, _ = claims[older]
        if total - prev_total != new:
            problems.append(
                f'{path.name}:{lineno} {newer} claims +{new} over {older}\'s '
                f'{prev_total} but reports a total of {total} '
                f'(expected {prev_total + new})')

    if counted and SKILLS_DIR.is_dir():
        actual = sum(1 for p in SKILLS_DIR.iterdir() if p.is_dir())
        _, total, lineno = claims[counted[0]]
        if total != actual:
            problems.append(
                f'{path.name}:{lineno} newest entry {counted[0]} reports a total of '
                f'{total} but the tree holds {actual} skill directories')
    return problems, claims


def check(path: Path) -> tuple[list[str], dict[str, tuple[int, int, int]]]:
    problems: list[str] = []
    entries: list[tuple[str, str, int]] = []
    lines = path.read_text(encoding='utf-8').split('\n')

    for lineno, line in enumerate(lines, 1):
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

    count_problems, claims = check_counts(path, lines)
    problems.extend(count_problems)

    print(f'{path.name}: {len(entries)} entries, '
          f'{len(seen)} distinct versions, {len(claims)} with counts, newest first')
    return problems, claims


def main() -> int:
    problems: list[str] = []
    per_file: dict[str, dict[str, tuple[int, int, int]]] = {}
    for name in TARGETS:
        path = REPO_ROOT / name
        if not path.exists():
            problems.append(f'{name}: missing')
            continue
        file_problems, claims = check(path)
        problems.extend(file_problems)
        per_file[name] = claims

    # The two files restate the same numbers, and the 32832 defect was copied
    # into both, so agreement is necessary but not sufficient — hence the
    # tree comparison above. This catches fixing one file and forgetting the other.
    if len(per_file) == len(TARGETS):
        a, b = TARGETS
        for ver in sorted(set(per_file[a]) & set(per_file[b])):
            new_a, total_a, line_a = per_file[a][ver]
            new_b, total_b, line_b = per_file[b][ver]
            if (new_a, total_a) != (new_b, total_b):
                problems.append(
                    f'{ver}: {a}:{line_a} says +{new_a} -> {total_a} but '
                    f'{b}:{line_b} says +{new_b} -> {total_b}')

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
