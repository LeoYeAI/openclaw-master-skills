#!/usr/bin/env python3
"""Fail when a SKILL.md invokes ./script but the script ships non-executable.

The upstream archive stores every one of its 274208 files as mode 100644, so no
imported skill ever arrives with an exec bit. That is invisible until a document
tells the agent to run `./setup.sh`, at which point the kernel refuses the execve
with EACCES. Verified with a real subprocess rather than assumed:

    644 via ./setup.sh      OSError: Permission denied (errno 13)
    644 via sh setup.sh     exit 0
    755 via ./setup.sh      exit 0

So the mode only matters for the `./x` form. `bash x.sh` and `python3 x.py` work
at 644, which is why this check is narrow instead of "every script needs +x".

Three conditions must all hold before a file is reported:

  1. A #! first line. Without one the file is data, not a program.
  2. The owning skill's own SKILL.md invokes it in command position: first token
     on a line (optionally after a `$ ` or `> ` prompt), or straight after a
     shell operator. Markdown link targets like [x](./scripts/x.sh) are stripped
     first -- an early pass counted those and inflated 215 to 274.
  3. git records mode 100644. git's mode is what a fresh clone gets; the local
     filesystem mode is irrelevant to what ships.

Enforced rather than report-only, unlike the duplicate and secret scanners. Those
would delete or rename published content, which is Leo's call. This changes a
permission bit, touches no byte of content, and the count is currently zero, so
enforcing it can only catch a regression.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / 'skills'

CANDIDATES = ('SKILL.md', 'skill.md', 'Skill.md')

# ./x at the start of a line, after a prompt marker, or after a shell operator.
CMD = re.compile(r'(?:^\s*(?:[$>]\s+)?|[|&;(]\s*|`\s*)\./([\w][\w./-]*)')
INLINE_LINK = re.compile(r'\[[^\]]*\]\([^)]*\)')
LINK_TARGET = re.compile(r'\]\(\s*\./')


def git_modes():
    out = subprocess.run(['git', 'ls-files', '-s', 'skills'],
                         cwd=REPO_ROOT, capture_output=True, text=True,
                         check=True).stdout
    modes = {}
    for line in out.splitlines():
        meta, _, path = line.partition('\t')
        modes[path] = meta.split()[0]
    return modes


def has_shebang(path):
    try:
        with path.open('rb') as fh:
            return fh.read(2) == b'#!'
    except OSError:
        return False


def main():
    if not (REPO_ROOT / '.git').exists():
        print('not a git repository; skipping exec-bit check')
        return 0

    modes = git_modes()
    findings = []
    scanned = 0

    for d in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        doc = next((d / n for n in CANDIDATES if (d / n).is_file()), None)
        if doc is None:
            continue
        scanned += 1
        try:
            text = doc.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            # check-line-endings.py owns that failure.
            continue
        seen = set()
        for raw in text.replace('\r\n', '\n').split('\n'):
            line = INLINE_LINK.sub('', raw)
            if LINK_TARGET.search(line):
                continue
            for ref in CMD.findall(line):
                rel = f'skills/{d.name}/{ref}'
                if rel in seen:
                    continue
                if modes.get(rel) != '100644':
                    continue
                if not has_shebang(REPO_ROOT / rel):
                    continue
                seen.add(rel)
                findings.append((rel, raw.strip()[:70]))

    print(f'scanned {scanned} skills for ./script invocations')
    if findings:
        skills = {p.split('/')[1] for p, _ in findings}
        print(f'FAIL: {len(findings)} script(s) across {len(skills)} skill(s) are '
              f'invoked as ./x but ship non-executable')
        for rel, ctx in findings[:20]:
            print(f'  {rel}')
            print(f'      {ctx}')
        if len(findings) > 20:
            print(f'  ... {len(findings) - 20} more')
        print('\nfix: git update-index --chmod=+x <path>')
        return 1

    print('OK: every ./-invoked script with a shebang is executable')
    return 0


if __name__ == '__main__':
    sys.exit(main())
