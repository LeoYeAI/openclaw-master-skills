#!/usr/bin/env python3
r"""Report shipped code that hardcodes another user's home directory.

Same family as the CRLF shebangs and the missing exec bits: correct on the
machine it was written on, broken for everyone who installs it. A script holding

    ROOT="/home/clawd/.openclaw/skills/brainx-v5"

fails for every user who is not clawd, and no reader is expected to edit it.

Precision is the whole problem here. A first pass matching any /home/<name> or
/Users/<name> reported 78 skills, and most were legitimate:

  * `/Users/xxx/MyApp/src` in a usage string is a placeholder to adapt
  * `/Users/joe/Documents/research.pdf` in an example prompt is illustrative
  * `/home/pi/xgoPictures/` in xgorobot is correct: the target *is* a Raspberry Pi

The distinction that matters is not markdown-vs-code, it is whether the value is
bound to a name the program then dereferences. So a finding requires all of:

  1. a shipped code file, not SKILL.md prose
  2. the path on the right-hand side of an assignment
  3. a username that is not an obvious placeholder (you, user, xxx, <name>, ...)

A first pass over assignments alone matched 13 skills. Three are not defects and
are filtered out below, which is worth recording because each would otherwise
return every week:

  * xgorobot -- /home/pi is the stock Raspberry Pi account and the skill ships
    for XGO robot-dog hardware, which runs Raspberry Pi OS
  * ai-powered-literature-review-skills -- /home/researcher is a container
    service account defined by its own docker-compose.yml
  * feishu-doc -- the match sits inside a cached fetched document, not code

That leaves 10 skills, 35 occurrences.

Report-only, like the duplicate, secret, reference and case-collision checks.
Fixing these means choosing a path policy for someone else's code -- $HOME, a
config value, an argument default -- and guessing wrong breaks a skill that
currently works for its author. Leo's call, not the weekly run's.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

NAMED_HOME = re.compile(r'(?:/home/|/Users/)([A-Za-z0-9._-]+)')

# Usernames that are deliberately generic.
PLACEHOLDER_USER = re.compile(
    r'^(you|user|users|username|me|xxx+|yyy+|zzz+|name|your\w*|demo|example|'
    r'sample|test|foo|bar|<[^>]*>|\{\{?[^}]*\}?\}|\$\w+|%\w+%)$', re.I)

# A path bound to a name: const X = "...", X=..., X: "...", default="..."
ASSIGN = re.compile(
    r'(?:^|\s)(?:const|let|var|export|readonly|final|local)?\s*'
    r'[A-Za-z_][A-Za-z0-9_.\[\]\'"-]*\s*(?:=|:=|:)\s*'
    r'[rbfu]?["\'`]?\s*((?:/home/|/Users/)[^"\'`\s,;)]+)')

CODE_EXT = {'.sh', '.bash', '.zsh', '.py', '.js', '.ts', '.mjs', '.cjs',
            '.rb', '.pl', '.go', '.java', '.yaml', '.yml', '.toml'}

# Paths that are correct for their target rather than accidental.
KNOWN_GOOD = {
    # /home/pi is the stock Raspberry Pi account and xgorobot ships for XGO
    # robot-dog hardware, which runs Raspberry Pi OS.
    'pi',
    # Container images define their own service account.
    'node', 'researcher',
}

# Cache directories hold fetched third-party content, not shipped code.
SKIP_DIR_PARTS = {'cache', 'node_modules', '.git', 'fixtures', '__pycache__'}


def real_user(fragment):
    m = NAMED_HOME.match(fragment)
    if not m:
        return None
    user = m.group(1)
    if PLACEHOLDER_USER.match(user) or user in KNOWN_GOOD:
        return None
    return user


def main():
    if not (REPO_ROOT / '.git').exists():
        print('not a git repository; skipping absolute-path check')
        return 0

    tracked = subprocess.run(['git', 'ls-files', 'skills'], cwd=REPO_ROOT,
                             capture_output=True, text=True,
                             check=True).stdout.split('\n')

    findings = {}
    scanned = 0

    for rel in tracked:
        if not rel:
            continue
        p = Path(rel)
        if p.suffix.lower() not in CODE_EXT:
            continue
        if SKIP_DIR_PARTS & set(p.parts):
            continue
        try:
            text = (REPO_ROOT / rel).read_bytes().decode('utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        skill = p.parts[1] if len(p.parts) > 1 else '?'

        for i, line in enumerate(text.replace('\r\n', '\n').split('\n'), 1):
            if '/home/' not in line and '/Users/' not in line:
                continue
            m = ASSIGN.search(line)
            if not m:
                continue
            user = real_user(m.group(1))
            if not user:
                continue
            findings.setdefault(skill, []).append((rel, i, user,
                                                   line.strip()[:96]))

    total = sum(len(v) for v in findings.values())
    print(f'scanned {scanned} shipped code files under skills/')
    print(f'hardcoded home paths: {total} in {len(findings)} skills')

    for skill, hits in sorted(findings.items()):
        users = sorted({u for _, _, u, _ in hits})
        print(f'  {skill}  (user{"s" if len(users) > 1 else ""}: '
              f'{", ".join(users)})')
        for rel, ln, _u, txt in hits[:3]:
            print(f'      {rel}:{ln}')
            print(f'        {txt}')
        if len(hits) > 3:
            print(f'      ... {len(hits) - 3} more in this skill')

    if findings:
        print('\nReport-only: each fix means choosing a path policy for someone '
              "else's code ($HOME, a config value, an argument default), and "
              'guessing wrong breaks a skill that works for its author.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
