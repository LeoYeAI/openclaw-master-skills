#!/usr/bin/env python3
"""Regenerate skill_index.md from the skills/ tree.

The index was last written by hand at v0.7.0 and rotted: 540 of its 560 rows
carried "name: <slug>" as the description (a broken frontmatter parse) and
~1940 skills were missing entirely. This uses the same description extraction
rules as scripts/collect.sh so the two stay consistent.

With --check, compares the committed file against a fresh build and exits 1 on
any difference instead of writing. collect.sh regenerates the index every run,
but commits made outside that path can leave it stale -- editing the parsing in
this script without rebuilding is enough -- and a published index that disagrees
with the skills it describes is exactly the failure v0.7.0 shipped.
"""

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / 'skills'
INDEX_FILE = REPO_ROOT / 'skill_index.md'
MAX_DESC = 110


def first_paragraph(content: str) -> str:
    """Fallback for skills with no YAML frontmatter.

    ~20 skills (agent-memory, browser, ...) open straight into markdown, so the
    frontmatter parse yields nothing. Their first real paragraph is a perfectly
    good one-line summary.

    Some write the heading and the prose in one block:

        ## Description
        专业 AI 提示词生成工具 ...

    so headings are stripped line-by-line rather than skipping the whole block.
    """
    for block in re.split(r'\n\s*\n', content):
        if block.lstrip().startswith(('---', '```', '|', '<')):
            continue
        kept = [
            ln.strip() for ln in block.splitlines()
            if ln.strip() and not ln.lstrip().startswith(('#', '>', '|', '<', '```'))
        ]
        if not kept:
            continue
        # Skip metadata slabs like "**Tier:** POWERFUL / **Category:** ...",
        # which read as noise in an index (api-design-reviewer et al).
        if all(re.match(r'^[-*]{0,2}\s*\*{0,2}[A-Za-z][\w /]{0,24}\*{0,2}\s*:', ln) for ln in kept):
            continue
        text = ' '.join(' '.join(kept).split())
        if len(text) >= 20:
            return text
    return ''


def read_skill_md(skill_dir: Path, limit: int = 5000) -> str:
    """Read SKILL.md, tolerating the lowercase spelling (e.g. clawsec/skill.md).

    The limit caps how much body text is read for the first_paragraph fallback.
    Pass limit=None when the whole frontmatter block is needed: 5 skills
    (lumi-diary at 14011 chars, agent-bom, doubao-asr, judge-human,
    research-swarm) have frontmatter longer than 5000 chars, and a parser that
    needs the closing --- would silently fall back to body prose for them.
    """
    for name in ('SKILL.md', 'skill.md'):
        path = skill_dir / name
        if path.is_file():
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                return ''
            return text if limit is None else text[:limit]
    return ''


FRONTMATTER_RE = re.compile(
    r'^\ufeff?\s*---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)', re.S)


def frontmatter_description(content: str):
    """Description via a real YAML parse, or None if that is not possible.

    This used to be a regex that stripped the outer quotes by hand. It got the
    answer wrong two ways, both of which shipped:

      * it never unescaped the scalar, so a quoted value containing an escaped
        quote rendered as a literal \\" in the table (5 rows, e.g.
        agent-anti-false-completion, qr-code-generator);
      * its lookahead for the next key was `\\n[a-zA-Z_]+:`, which does not match
        a hyphenated key, so the description swallowed everything up to the next
        underscored key -- "user-invocable: true",
        "disable-model-invocation: ...", even a trailing `# comment` (11 rows,
        e.g. x-twitter, btpanel, tushare-finance).

    A YAML loader gets block scalars, quoting and key boundaries right for free.
    Returns None on unparseable frontmatter so the caller keeps its old
    behaviour; check-frontmatter.py is the gate that makes that case fatal.
    """
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    desc = data.get('description')
    if not isinstance(desc, str):
        return None
    return ' '.join(dequote(desc).split())


def dequote(desc: str) -> str:
    """Drop quoting that wraps the description text itself.

    Two skills write the value as "\\"real text\\"...", so a correct YAML parse
    yields text whose first character is a literal quote. That is faithful to
    the file but reads as a defect in the table, and the old regex path hid it
    by stripping leading quotes unconditionally.

    Handled in two steps:
      * a matched outer pair is removed (agent-anti-false-completion, where the
        quote closes at the very end);
      * otherwise a lone leading quote is dropped only when the text contains a
        later closing quote (verified-capability-evolver, where the quoted span
        ends mid-description and unbalanced prose follows).
    A description that merely opens a quoted phrase and never closes it keeps
    its quote.
    """
    desc = desc.strip()
    pairs = (('"', '"'), ("'", "'"), ('“', '”'), ('‘', '’'))
    for open_q, close_q in pairs:
        if len(desc) > 2 and desc.startswith(open_q) and desc.endswith(close_q):
            inner = desc[len(open_q):-len(close_q)].strip()
            if inner:
                return inner
    for open_q, close_q in pairs:
        if desc.startswith(open_q) and close_q in desc[len(open_q):]:
            inner = desc[len(open_q):].strip()
            if inner:
                return inner
    return desc


def extract_description(skill_dir: Path) -> str:
    content = read_skill_md(skill_dir, limit=None)
    if not content:
        return ''
    if not content.lstrip().startswith('---'):
        return clip(first_paragraph(content[:5000]))
    desc = frontmatter_description(content)
    if not desc:
        return clip(first_paragraph(content[:5000]))
    # A description that just restates the name is noise, not information.
    if re.match(r'^name:', desc):
        return clip(first_paragraph(content[:5000]))
    # Same for ones that merely title-case the slug ("API Design Reviewer").
    if restates_slug(desc, skill_dir.name):
        return clip(first_paragraph(content[:5000]) or desc)
    return clip(desc)


def restates_slug(desc: str, slug: str) -> bool:
    """True when the description carries no more information than the slug.

    Covers exact restatements ("API Design Reviewer") and decorated ones
    ("Incident Commander Skill", "RAG Architect - POWERFUL"), where the slug is
    just padded with filler. Length-capped so real prose is never discarded.
    """
    if len(desc) >= 40:
        return False
    # Non-ASCII text is never a slug restatement: slugs are ASCII, so stripping
    # CJK collapsed "自动化 Web 任务执行服务。" to "web", which matched inside
    # "ai-web-automation" and threw away a perfectly good description.
    if any(ord(ch) > 127 for ch in desc):
        return False
    filler = r'(skill|powerful|tier|cs)'
    norm = lambda s: re.sub(filler, '', re.sub(r'[^a-z0-9]', '', s.lower()))
    d, s = norm(desc), norm(slug)
    if not d or not s:
        return False
    return d == s or d in s or s in d


def clip(desc: str) -> str:
    if not desc:
        return ''
    desc = desc.replace('|', '\\|')
    if len(desc) > MAX_DESC:
        desc = desc[:MAX_DESC].rstrip() + '…'
    return desc


def main() -> int:
    check_only = '--check' in sys.argv
    if not SKILLS_DIR.is_dir():
        print(f'skills dir not found: {SKILLS_DIR}', file=sys.stderr)
        return 1

    rows = []
    missing = 0
    for path in sorted(SKILLS_DIR.iterdir(), key=lambda p: p.name):
        if not path.is_dir():
            continue
        desc = extract_description(path)
        if not desc:
            missing += 1
            desc = '_(no description)_'
        rows.append((path.name, desc))

    lines = [
        '# Skill Index',
        '',
        f'{len(rows)} skills. Generated by `scripts/build-index.py` — do not edit by hand.',
        '',
        '| Skill | Description |',
        '|---|---|',
    ]
    lines += [f'| [`{slug}`](skills/{slug}/) | {desc} |' for slug, desc in rows]
    content = '\n'.join(lines) + '\n'

    if check_only:
        # collect.sh regenerates the index every run, but any commit made outside
        # that path can leave it stale -- editing this script's parsing without
        # rebuilding is enough to do it, and the result is a published index that
        # disagrees with the skills it describes. Compare without writing so the
        # weekly run can fail instead of shipping the mismatch.
        current = (INDEX_FILE.read_text(encoding='utf-8')
                   if INDEX_FILE.is_file() else '')
        if current == content:
            print(f'skill_index.md is up to date ({len(rows)} rows)')
            return 0
        if not current:
            print(f'{INDEX_FILE.name} is missing; run scripts/build-index.py')
            return 1

        old = current.splitlines()
        new = content.splitlines()
        print(f'{INDEX_FILE.name} is stale: '
              f'{len(old)} lines committed vs {len(new)} regenerated')
        shown = 0
        for i, (a, b) in enumerate(zip(old, new), 1):
            if a != b:
                print(f'  line {i}:')
                print(f'    committed:   {a[:120]}')
                print(f'    regenerated: {b[:120]}')
                shown += 1
                if shown == 5:
                    break
        if len(old) != len(new):
            print(f'  ...and a length difference of {abs(len(old) - len(new))} lines')
        print('run scripts/build-index.py and commit the result')
        return 1

    INDEX_FILE.write_text(content, encoding='utf-8')

    print(f'skill_index.md: {len(rows)} rows ({missing} without a usable description)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
