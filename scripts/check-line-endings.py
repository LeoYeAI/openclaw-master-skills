#!/usr/bin/env python3
r"""Report SKILL.md files with CRLF line endings; fail on CRLF shebangs.

Two findings that look alike and are not.

SKILL.md with CRLF is a portability concern, not a live defect. Verified against
the shapes a consumer might use:

  * this repo's frontmatter regexes (`^\s*---\s*\n`) match CRLF fine
  * PyYAML parses the extracted block correctly
  * a strict `^---$` with re.MULTILINE does NOT match, because the line is `---\r`
  * a loader doing `lines[0] == '---'` also fails, for the same reason

So nothing in this pipeline breaks, but a stricter external loader would see no
frontmatter at all. 140 files are affected, all upstream. Report-only, like the
duplicate, secret and case-collision checks: rewriting 140 third-party files on a
schedule is Leo's call.

A CRLF shebang is a hard failure, because it is not a portability concern at all.
Verified empirically rather than assumed: the kernel takes everything after `#!`
up to the newline as the interpreter path, so `#!/bin/sh\r` resolves to the
literal path `/bin/sh\r` and execution fails with ENOENT. 15 scripts shipped that
way, each invoked by its own skill's instructions, so those skills could not work
at all. All 15 are repaired, which makes zero enforceable.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / 'skills'

SHELL_EXT = {'.sh', '.bash'}
SKILL_NAMES = {'SKILL.md', 'skill.md', 'Skill.md'}


def main() -> int:
    skill_files = []
    shell_files = []
    scanned = 0

    for path in sorted(SKILLS.rglob('*')):
        if not path.is_file():
            continue
        is_skill = path.name in SKILL_NAMES
        is_shell = path.suffix.lower() in SHELL_EXT
        if not (is_skill or is_shell):
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        scanned += 1
        n_crlf = raw.count(b'\r\n')
        if not n_crlf:
            continue
        rel = path.relative_to(REPO_ROOT)
        if is_shell:
            # Only the first line decides whether the script can run at all.
            first = raw.split(b'\n', 1)[0]
            shebang = raw.startswith(b'#!') and first.endswith(b'\r')
            shell_files.append((rel, n_crlf, shebang))
        else:
            n_lf = raw.count(b'\n') - n_crlf
            skill_files.append((rel, n_crlf, n_lf))

    print(f'scanned {scanned} SKILL.md and shell files under skills/')
    print(f'SKILL.md with CRLF: {len(skill_files)} (report-only)')
    broken = [rel for rel, _, shebang in shell_files if shebang]
    print(f'shell scripts with CRLF: {len(shell_files)} '
          f'({len(broken)} with a CRLF shebang)')

    for rel, n_crlf, n_lf in sorted(skill_files, key=lambda r: -r[1])[:10]:
        mixed = f', {n_lf} LF' if n_lf else ''
        print(f'  {n_crlf:>6} CRLF{mixed}  {rel}')
    if len(skill_files) > 10:
        print(f'  ... {len(skill_files) - 10} more')

    for rel, n_crlf, shebang in sorted(shell_files, key=lambda r: -r[1])[:10]:
        mark = '  [CRLF SHEBANG]' if shebang else ''
        print(f'  {n_crlf:>6} CRLF  {rel}{mark}')
    if len(shell_files) > 10:
        print(f'  ... {len(shell_files) - 10} more')

    if skill_files:
        print('\nSKILL.md CRLF is report-only: these parse correctly here (repo '
              'regexes and PyYAML both accept CRLF), but a strict ^---$ loader '
              'sees no frontmatter.')

    if broken:
        print(f'\nFAILED: {len(broken)} shell script(s) have a CRLF shebang and '
              f'cannot execute. The kernel resolves the interpreter path with a '
              f'trailing CR and fails with ENOENT:')
        for rel in broken:
            print(f'  - {rel}')
        print('Strip CR from these files; the skills invoking them are broken.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
