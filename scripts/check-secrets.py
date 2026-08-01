#!/usr/bin/env python3
"""Report credentials hardcoded in executable files under skills/.

Why this exists: cann-review shipped a live GitCode token as a literal in five
scripts while its own README told users to export GITCODE_API_TOKEN. Nothing in
the weekly run looked at file contents for credentials, so installing the
collection handed every user the author's key.

Report-only, by design. These are third-party skills mirrored from upstream;
rewriting an author's code on a schedule is Leo's call, not the weekly run's.
The run should surface new occurrences so they get triaged before publish.

Scope is deliberately narrow to keep the signal usable:
  - executable extensions only, since a key in a README is a lesser problem
    than one baked into code that runs
  - assignment to a credential-named variable
  - value must look like a credential, not a placeholder or an env reference

Known-benign shapes are filtered: 0x blockchain addresses, Hardhat's published
test key, HTTP header-name constants, and secret-scanner test fixtures.

Values are never printed. Each finding shows a length and a short fingerprint so
two occurrences can be matched without exposing the secret.
"""
import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / 'skills'

EXEC_EXT = {'.py', '.sh', '.bash', '.js', '.mjs', '.cjs', '.ts', '.rb', '.go', '.php'}

ASSIGN = re.compile(
    r'(?i)\b([A-Z0-9_]*(?:API[_-]?KEY|SECRET|TOKEN|PASSWORD|PASSWD|'
    r'ACCESS[_-]?KEY|PRIVATE[_-]?KEY|CREDENTIAL)[A-Z0-9_]*)\s*'
    r'(?::\s*[A-Za-z\[\]]+\s*)?=\s*'
    r'(["\'])([^"\'\n]{12,})\2')

PLACEHOLDER = re.compile(
    r'(?i)(your|example|sample|placeholder|dummy|fake|test|demo|mock|xxx|\.\.\.|'
    r'<|\{\{|\$|%s|%\(|process\.env|os\.environ|getenv|ENV\[|REDACTED|INSERT|'
    r'here|changeme|todo|none|null|abc|123456|0{4,}|f{4,}|'
    r'password|secret|token|key$|/|\s|[\u4e00-\u9fff])')

# Hardhat account #0 private key, published in its docs; appears in many test
# suites and is not a secret.
HARDHAT_KEY = ('0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')

# Files whose whole purpose is to carry example secrets.
FIXTURE = re.compile(
    r'(?i)(/__tests__/|/tests?/|[._-]test\.|test[._-]|\.spec\.|'
    r'secret[_-]?patterns|secret[_-]?detector|secret[_-]?scanner|red-team)')


# Lowercase identifier / filename / label, e.g. regex_fallback,
# credentials.enc, fine_grained_pat, change-this-in-production. Real
# credentials in this corpus are longer and mixed-case, so the length cap keeps
# the exemption from swallowing them.
IDENTIFIER = re.compile(r'[a-z][a-z0-9]*([_.\-][a-z0-9]+)*')


def is_benign(name, val):
    if val.startswith('0x'):
        # Contract addresses (42) and hashes/keys (66) are public identifiers.
        return True
    if val.lower() == HARDHAT_KEY:
        return True
    if re.fullmatch(r'[A-Z][A-Za-z0-9-]*(-[A-Za-z0-9]+)*', val) and '-' in val:
        # HTTP header names: Authorization, X-Sdk-Content-Sha256.
        return True
    if ',' in val:
        # Lists of example values: "key1,key2,key3".
        return True
    if re.search(r'[{}]', val):
        # f-string / template interpolation, not a literal value.
        return True
    if len(val) <= 32 and IDENTIFIER.fullmatch(val):
        return True
    if not re.search(r'[0-9]', val) and not re.search(r'[a-z]', val):
        return True
    if not re.search(r'[A-Za-z]', val):
        return True
    return False


def main():
    findings = []
    fixtures = 0
    scanned = 0

    for f in sorted(SKILLS.rglob('*')):
        if not f.is_file() or f.suffix.lower() not in EXEC_EXT:
            continue
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        if len(text) > 1_000_000:
            continue
        scanned += 1
        rel = f.relative_to(REPO_ROOT)
        for m in ASSIGN.finditer(text):
            name, val = m.group(1), m.group(3)
            if PLACEHOLDER.search(val) or is_benign(name, val):
                continue
            if FIXTURE.search(str(rel)):
                fixtures += 1
                continue
            line = text.count('\n', 0, m.start()) + 1
            fp = hashlib.sha1(val.encode()).hexdigest()[:8]
            findings.append((str(rel), line, name, len(val), fp))

    print(f'scanned {scanned} executable files under skills/')
    print(f'hardcoded credentials: {len(findings)} '
          f'({fixtures} test fixtures excluded)')
    for rel, line, name, n, fp in findings:
        print(f'  {rel}:{line}  {name}  [{n} chars, fp {fp}]')
    if findings:
        print('\nReport-only: these are upstream authors\' files. Triage before '
              'publish; do not rewrite third-party code automatically.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
