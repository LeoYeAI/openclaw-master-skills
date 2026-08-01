#!/usr/bin/env python3
"""Report paths that collide when the filesystem ignores case.

Why this exists: the repo is authored and validated on Linux, which is
case-sensitive, and git records both spellings without complaint. A clone on
macOS (APFS, case-insensitive by default) or Windows cannot create two entries
in one directory whose names differ only by case. The second write lands on top
of the first, the working tree is dirty the moment cloning finishes, and
`git status` reports a modification the user has no way to resolve.

Nothing in the pipeline looked at this. The collection carries 2503 skill
directories imported from an archive spanning thousands of independent
publishers, so `SKILL.md` alongside `skill.md` is a matter of time, and 16 such
pairs across 11 skills are already shipping.

Files and directories share one namespace on those filesystems, so both are
bucketed together per parent directory.

Report-only. 15 of the 16 known pairs hold genuinely different content --
`skills/payment/` ships two unrelated skills as SKILL.md and skill.md, and
`siyuan-notes-skill/docs/` an English and a Chinese reference under the same
name. Resolving those means deciding which document survives, which deletes
shipped content and can change what an installed skill loads. That is Leo's
call, not the weekly run's. The run's job is to surface new ones before they
reach users.
"""
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Managed by git itself; never part of a clone's working tree in a way that
# could collide.
SKIP_DIRS = {'.git'}


def digest(path: Path) -> str:
    try:
        return hashlib.sha1(path.read_bytes()).hexdigest()
    except OSError:
        return ''


def main() -> int:
    collisions = []
    entries_scanned = 0

    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        buckets = defaultdict(list)
        for name in list(dirnames) + list(filenames):
            entries_scanned += 1
            buckets[name.lower()].append(name)

        for names in buckets.values():
            if len(names) < 2:
                continue
            parent = Path(dirpath)
            rel = parent.relative_to(REPO_ROOT)
            # Identical content is mechanical to resolve; differing content is a
            # judgement call. Say which, so the report is actionable.
            digests = {n: digest(parent / n) for n in sorted(names)}
            same = len(set(digests.values())) == 1 and '' not in digests.values()
            collisions.append((str(rel) if str(rel) != '.' else '.',
                               sorted(names), same))

    identical = sum(1 for *_, same in collisions if same)
    print(f'scanned {entries_scanned} entries under {REPO_ROOT.name}/')
    print(f'case-insensitive collisions: {len(collisions)} '
          f'({identical} byte-identical, {len(collisions) - identical} differing)')

    for rel, names, same in collisions:
        kind = 'identical' if same else 'DIFFERING content'
        print(f'  {rel}/  {" vs ".join(names)}  [{kind}]')

    if collisions:
        print('\nA clone on macOS or Windows cannot check out both spellings; '
              'the working tree will be dirty on arrival.')
        print('Report-only: resolving a differing pair deletes shipped content '
              'and can change what an installed skill loads.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
