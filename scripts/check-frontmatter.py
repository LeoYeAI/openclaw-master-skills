#!/usr/bin/env python3
"""Assert every skill has frontmatter a real YAML parser accepts.

The regex checks in collect.sh only prove a `description:` line exists. They pass
on frontmatter that no YAML-based loader can read, which is how 70 skills shipped
with an unquoted scalar containing ': ', 11 with structural damage, 3 with no
closing delimiter and 2 wrapped in a raw HTTP multipart envelope.

Requires: valid UTF-8 with no BOM, a closed `---` block, parseable as a YAML
mapping, with a non-empty `name` and `description` that is not unedited scaffold
text. Exits 1 and lists every offender when violated.

The encoding check exists because every read in this repo used
errors='ignore', which discards undecodable bytes instead of reporting them:
`avoid-ai-writing` shipped 13 cp1252 em dashes that way, so '### P0 - Credibility
killers' published as '### P0  Credibility killers' with the dash gone.

The placeholder check is deliberately frontmatter-only. Scanning bodies for the
same phrasings produced 144 hits of which nearly all were legitimate: "Replace
with" appears in rewrite tables (`avoid-ai-writing`, `content-humanizer`) and
"One-line description" in output templates the skill asks the agent to fill in.
A description, by contrast, is shipped prose -- it is what the index displays
and what a user's request is matched against, so scaffold text there is always
a defect. `template-skill` shipped in the curated index described as "Replace
with description of the skill and when Claude should use it."
"""

import codecs
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

# Imperative phrasings addressed to the skill's author. Bare `todo`/`xxx` are
# excluded on purpose: they are trigger keywords in notion-im-helper's
# description and redactions in sls-trace-analysis's prose examples.
PLACEHOLDER = re.compile(
    r'(replace (with|this)\b|your (skill|description|name) here\b'
    r'|insert (instructions|description|your \w+) (below|here)\b'
    r'|describe what this (skill|does)\b|lorem ipsum'
    r'|brief description of (the |this )?skill|one[- ]line description'
    r'|short description of (the |this )?skill'
    r'|(todo|fixme|fill in|change me)\s*[:\uff1a]\s*(add|write|describe|replace))',
    re.I)


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
        raw = f.read_bytes()

        # Encoding first: every read below uses errors='ignore', which silently
        # discards undecodable bytes. avoid-ai-writing shipped 13 cp1252 em
        # dashes that way -- '### P0 - Credibility killers' rendered as
        # '### P0  Credibility killers', the dash simply gone from the published
        # file, and no gate said a word.
        if raw.startswith(codecs.BOM_UTF8):
            problems.append(f'{d.name}: starts with a UTF-8 BOM; a loader that '
                            f'does not strip it sees no frontmatter')
            continue
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError as e:
            line = raw[:e.start].count(b'\n') + 1
            problems.append(f'{d.name}: not valid UTF-8 at byte {e.start} '
                            f'(line {line}): {e.reason}')
            continue

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

        for field in ('name', 'description'):
            v = data.get(field)
            if isinstance(v, str):
                ph = PLACEHOLDER.search(v)
                if ph:
                    problems.append(f'{d.name}: unedited placeholder text in '
                                    f'{field} ({ph.group(0)!r})')

    if problems:
        print(f'frontmatter validation FAILED ({len(problems)} problem(s) '
              f'in {checked} skills):')
        for p in problems:
            print(f'  - {p}')
        return 1

    print(f'frontmatter OK: {checked} skills parse with a real '
          f'name + description')
    return 0


if __name__ == '__main__':
    sys.exit(main())
