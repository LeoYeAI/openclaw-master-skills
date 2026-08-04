#!/usr/bin/env python3
r"""Fail on shipped scripts that cannot parse.

The strongest member of the "broken as shipped" family, alongside CRLF shebangs
and missing exec bits. A file with a syntax error fails for every user on every
platform no matter how it is invoked, so unlike the hardcoded-home findings
there is nothing to judge and no environment where it happens to work.

Nothing covered this before. check-frontmatter.py rejects a BOM, but only on
SKILL.md; no gate ever parsed a shipped .py or .sh. That is how
skills/bug-fixing/scripts/generate_report_template.py shipped starting with
ef bb bf, which makes python3 refuse the file outright.

Mechanism per language:
  * Python  -- ast.parse, which is the first thing the interpreter does
  * Shell   -- bash -n, which parses without executing

Two exclusions, both of which would otherwise produce false failures:

  * Template files carrying {{placeholders}} or __PLACEHOLDER__ markers are not
    meant to run as-is, so an unparseable template is by design.
  * Python 2 files are reported separately. `print "x"` is a genuine python3
    syntax error and worth surfacing, but the remediation is to port or drop the
    skill, not to fix a typo.

Hard gate. As of the 2026-08 audit three of the five findings are mechanically
fixable and two are upstream data loss, recorded here so they are not
re-diagnosed every week:

  fixable
    bug-fixing/scripts/generate_report_template.py  -- strip the UTF-8 BOM
    contentclaw/scripts/track_engagement.py:122     -- `doesn\\'t` inside a
        single-quoted string; the backslash escapes the backslash, not the quote
    memory-and-context-engineering/scripts/memory_forgetting_mechanism.py:51
        -- a stray `|` between the value and its trailing comment

  upstream truncation, cannot be fixed without inventing code
    vibetrading-code-gen/scripts/code_validator.py:202  -- line is literally
        `if '` with the condition and body missing
    toutiao-publish/publish-toutiao.sh:150 -- a browser act request='{...}'
        heredoc-style block whose JS body was cut mid-string
"""
import ast
import re
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

# ast.parse emits SyntaxWarning for things like invalid escape sequences
# (`\$` in a non-raw string). Those are style problems, not parse failures, and
# thousands of them would bury the actual findings in the run log.
warnings.filterwarnings('ignore', category=SyntaxWarning)

REPO_ROOT = Path(__file__).resolve().parent.parent

TEMPLATE = re.compile(r'\{\{[^}]+\}\}|<<<[A-Z_]+>>>|YOUR_[A-Z_]+_HERE|'
                      r'__[A-Z]+_PLACEHOLDER__|\{%[^%]+%\}')

# Statement-print and old-style `except E, e:` are the reliable python2 tells.
PY2 = re.compile(r'^\s*print\s+["\'{(\w]|except\s+\w+\s*,\s*\w+\s*:', re.M)

# Known upstream truncation: the source is genuinely incomplete, so failing the
# weekly run on them would block every release until someone writes the missing
# code. Reported every run, never fatal. Anything NOT on this list is fatal.
KNOWN_TRUNCATED = {
    'skills/vibetrading-code-gen/scripts/code_validator.py',
    'skills/toutiao-publish/publish-toutiao.sh',
}


def main():
    if not (REPO_ROOT / '.git').exists():
        print('not a git repository; skipping syntax check')
        return 0

    tracked = subprocess.run(['git', 'ls-files', 'skills'], cwd=REPO_ROOT,
                             capture_output=True, text=True,
                             check=True).stdout.split('\n')

    broken, py2, truncated = [], [], []
    templates = 0
    py_n = sh_n = 0

    for rel in tracked:
        if not rel:
            continue
        ext = Path(rel).suffix.lower()
        if ext not in {'.py', '.sh', '.bash'}:
            continue
        try:
            raw = (REPO_ROOT / rel).read_bytes()
            text = raw.decode('utf-8')
        except (OSError, UnicodeDecodeError):
            continue

        err = None
        if ext == '.py':
            py_n += 1
            try:
                ast.parse(text)
            except SyntaxError as e:
                err = (e.lineno or 0, str(e.msg))
            except ValueError as e:
                err = (0, f'{type(e).__name__}: {e}')
        else:
            sh_n += 1
            with tempfile.NamedTemporaryFile('wb', suffix='.sh',
                                             delete=False) as fh:
                fh.write(raw)
                tmp = fh.name
            try:
                r = subprocess.run(['bash', '-n', tmp],
                                   capture_output=True, text=True, timeout=60)
                if r.returncode != 0:
                    msg = ' '.join(r.stderr.strip().split())
                    err = (0, msg.replace(tmp, Path(rel).name)[:150])
            except subprocess.TimeoutExpired:
                err = (0, 'bash -n timed out')
            finally:
                Path(tmp).unlink(missing_ok=True)

        if err is None:
            continue
        if TEMPLATE.search(text):
            templates += 1
        elif rel in KNOWN_TRUNCATED:
            truncated.append((rel, *err))
        elif ext == '.py' and PY2.search(text):
            py2.append((rel, *err))
        else:
            broken.append((rel, *err))

    print(f'checked {py_n} python and {sh_n} shell files under skills/')
    print(f'unparseable: {len(broken)} fatal, {len(truncated)} known-truncated, '
          f'{len(py2)} python2, {templates} templates excluded')

    for label, rows in (('KNOWN-TRUNCATED (upstream, report-only)', truncated),
                        ('PYTHON 2 (port or drop)', py2),
                        ('FAILED', broken)):
        if not rows:
            continue
        print(f'\n{label}:')
        for rel, ln, msg in rows:
            where = f'{rel}:{ln}' if ln else rel
            print(f'  - {where}')
            print(f'      {msg}')

    if broken:
        print(f'\nFAILED: {len(broken)} shipped script(s) cannot be parsed. '
              'Every user who runs one gets a syntax error regardless of '
              'platform or invocation.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
