#!/usr/bin/env python3
"""Report SKILL.md instructions to read or run a bundled file that is missing.

A SKILL.md is an instruction sheet for the agent. When it says "run
scripts/analyze.py" and that file is not in the directory, the agent follows the
instruction and fails at runtime. Nothing else in the pipeline notices:
frontmatter validation only parses the YAML block, the README-table check never
opens the body, and the duplicate and secret scanners do not resolve paths.

Precision matters more than recall here, because a noisy report gets ignored. A
first pass that matched any path-shaped token produced 8302 hits, nearly all of
them files the skill creates at runtime or reads from the user's own project
(CLAUDE.md, package.json, pnpm-lock.yaml). Path shape alone cannot separate
those from a genuine broken reference, so two independent signals are required:

  1. The reference lives in a directory the skill actually ships. A skill with a
     scripts/ directory pointing at scripts/missing.py has a real gap; a skill
     with no scripts/ directory is describing the user's project.

  2. The document tells the agent to act on it: an imperative verb on the same
     line, or an interpreter invocation such as `python3 x.py`.

Signal 1 is what makes this usable: it anchors the claim in the skill's own
layout instead of guessing from prose.

Report-only. Most findings are upstream omissions where the file was never
shipped, and fixing those means inventing content. Near-misses whose target
ships under a hyphen/underscore variant are worth correcting by hand; the run
just needs to surface them before publish.
"""
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / 'skills'

EXT = (r'md|markdown|py|sh|bash|js|mjs|cjs|ts|tsx|json|json5|ya?ml|toml|txt|csv|'
       r'sql|html|css|xml|tmpl|template|jinja|jinja2|rb|go|php|ipynb|pdf|R')

PATHLIKE = re.compile(r'^(?:\./)?(?:[\w.\-]+/)+[\w.\-]+\.(?:' + EXT + r')$')

LINK = re.compile(r'!?\[[^\]]*\]\(\s*<?([^)\s>#?]+)>?\s*(?:"[^"]*")?\s*\)')
CODE = re.compile(r'`([^`\n]{2,120})`')
BARE = re.compile(r'(?<![\w`\[(/.])((?:\./)?(?:[\w.\-]+/)+[\w.\-]+\.(?:' + EXT + r'))\b')

VERB = re.compile(
    r'(?i)\b(read|see|refer|reference|consult|review|open|load|check|follow|'
    r'run|execute|exec|invoke|call|use|apply|source|import|详见|参见|请阅读|运行|'
    r'执行|参考|查看|读取)\b')
INTERP = re.compile(
    r'(?i)(python3?|node|bun|deno|bash|sh|zsh|ruby|go run|php|Rscript|npx|uv run)\s+'
    r'(?:-[\w-]+\s+)*([\w.\-/]+\.(?:' + EXT + r'))\b')

SKIP_PREFIX = ('http://', 'https://', 'ftp://', 'mailto:', 'data:', '#', '/',
               '~', 'file://', 'git@', 'ssh://', '$', '<', '{')
SKIP_CONTAINS = ('node_modules/', '.git/', 'site-packages/', '/tmp/', 'C:\\',
                 '%APPDATA%', '$HOME', '${', '*', 'path/to', 'your-',
                 'example.com', 'dist/', 'build/', '.next/', 'venv/',
                 '<name>', '[name]')

# Stand-ins for a user-supplied name; the file is not expected to exist.
PLACEHOLDER = re.compile(
    r'(?i)(^|[/_.-])(xxx|yyy|zzz|foo|bar|baz|some-script|my-track|example|'
    r'YYYY-MM-DD|<[^>]+>)([/_.-]|\.|$)')


def strip_frontmatter(text):
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            return text[end + 4:]
    return text


def line_of(text, pos):
    start = text.rfind('\n', 0, pos) + 1
    end = text.find('\n', pos)
    return text[start:end if end != -1 else len(text)]


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def main():
    total = 0
    missing = []      # never shipped
    nearmiss = []     # ships under another separator/case
    placeholders = 0

    for skill_md in sorted(SKILLS.glob('*/SKILL.md')):
        total += 1
        d = skill_md.parent
        try:
            text = strip_frontmatter(
                skill_md.read_text(encoding='utf-8', errors='ignore'))
        except OSError:
            continue

        try:
            shipped_dirs = {p.name for p in d.iterdir() if p.is_dir()}
        except OSError:
            continue
        if not shipped_dirs:
            continue

        hits = []
        for rx, kind in ((LINK, 'link'), (CODE, 'code'), (BARE, 'bare')):
            for m in rx.finditer(text):
                hits.append((m.group(1).strip(), kind, m.start()))
        for m in INTERP.finditer(text):
            hits.append((m.group(2).strip(), 'run', m.start()))

        seen = set()
        for ref, kind, pos in hits:
            if ref in seen:
                continue
            low = ref.lower()
            if low.startswith(SKIP_PREFIX) or any(s in ref for s in SKIP_CONTAINS):
                continue
            if not PATHLIKE.match(ref):
                continue
            rel = ref[2:] if ref.startswith('./') else ref
            if rel.split('/')[0] not in shipped_dirs:
                continue
            if kind != 'run' and not VERB.search(line_of(text, pos)):
                continue
            seen.add(ref)
            if (d / rel).exists():
                continue

            base = rel.split('/')[-1]
            if PLACEHOLDER.search(base):
                placeholders += 1
                continue

            parent = d / '/'.join(rel.split('/')[:-1])
            match = None
            if parent.is_dir():
                for p in parent.iterdir():
                    if p.is_file() and norm(p.name) == norm(base):
                        match = p.name
                        break
            if match:
                nearmiss.append((d.name, rel, match))
            else:
                missing.append((d.name, rel, kind))

    skills_affected = len({n for n, *_ in missing} | {n for n, *_ in nearmiss})
    print(f'scanned {total} SKILL.md files')
    print(f'broken references: {len(missing) + len(nearmiss)} across '
          f'{skills_affected} skills '
          f'({len(nearmiss)} fixable, {placeholders} placeholders ignored)')

    if nearmiss:
        print('\nfixable: target ships under a different name')
        for name, ref, match in nearmiss:
            print(f'  {name}: {ref}  ->  {match}')
    if missing:
        print('\nnever shipped (upstream omission, report-only)')
        for name, ref, kind in missing:
            print(f'  {name}: {ref}  ({kind})')
        print(f'\nby kind: {Counter(k for *_, k in missing).most_common()}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
