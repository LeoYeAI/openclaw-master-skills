#!/usr/bin/env python3
"""Assert every skill has frontmatter a real YAML parser accepts.

The regex checks in collect.sh only prove a `description:` line exists. They pass
on frontmatter that no YAML-based loader can read, which is how 70 skills shipped
with an unquoted scalar containing ': ', 11 with structural damage, 3 with no
closing delimiter and 2 wrapped in a raw HTTP multipart envelope.

Requires: a closed `---` block, parseable as a YAML mapping, with a non-empty
`name` and `description`. Exits 1 and lists every offender when violated.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print('check-frontmatter: PyYAML not installed, skipping', file=sys.stderr)
    sys.exit(0)

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / 'skills'
FM = re.compile(r'^---\s*\n(.*?)\n---\s*(?:\n|$)', re.S)


def main():
    problems = []
    checked = 0

    for d in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        for fn in ('SKILL.md', 'skill.md'):
            f = d / fn
            if f.is_file():
                break
        else:
            problems.append(f'{d.name}: no SKILL.md')
            continue

        checked += 1
        text = f.read_text(encoding='utf-8', errors='ignore')
        m = FM.match(text.replace('\r\n', '\n'))
        if not m:
            problems.append(f'{d.name}: no closed --- frontmatter block')
            continue
        try:
            data = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            mark = getattr(e, 'problem_mark', None)
            where = f' at block line {mark.line + 1}' if mark else ''
            problems.append(f'{d.name}: unparseable YAML{where} '
                            f'({getattr(e, "problem", type(e).__name__)})')
            continue
        if not isinstance(data, dict):
            problems.append(f'{d.name}: frontmatter is not a mapping')
            continue
        if not data.get('name'):
            problems.append(f'{d.name}: missing or empty name')
        if not data.get('description'):
            problems.append(f'{d.name}: missing or empty description')

    if problems:
        print(f'frontmatter validation FAILED ({len(problems)} problem(s) '
              f'in {checked} skills):')
        for p in problems:
            print(f'  - {p}')
        return 1

    print(f'frontmatter OK: {checked} skills parse with name + description')
    return 0


if __name__ == '__main__':
    sys.exit(main())
