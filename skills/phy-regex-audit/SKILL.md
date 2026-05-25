---
name: phy-regex-audit
description: Static ReDoS (Regular Expression Denial of Service) vulnerability scanner and regex quality auditor for codebases. Walks all source files to extract regex literals, detects catastrophic backtracking patterns (nested quantifiers, overlapping alternation, unbounded repetition on complex groups), severity-ranks each finding as CRITICAL/HIGH/MEDIUM, reports file and line number with the dangerous sub-pattern highlighted, identifies high-risk call sites (HTTP request handlers, form validators, URL parsers), and suggests safe rewrites using atomic groups or simplified alternatives. Also detects hardcoded locale assumptions (character classes assuming ASCII), overly permissive patterns, and regexes missing anchors. Supports JS/TS, Python, Go, Java, Ruby, PHP, Rust. Zero external API — pure static analysis. Triggers on "regex security", "ReDoS", "catastrophic backtracking", "regex audit", "slow regex", "regex vulnerability", "/regex-audit".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - security
    - regex
    - redos
    - performance
    - static-analysis
    - developer-tools
    - javascript
    - python
    - denial-of-service
---

# ReDoS & Regex Quality Auditor

One regex. One crafted input. Your Node.js server hangs for 30 seconds.

ReDoS (Regular Expression Denial of Service) is real, underestimated, and embarrassingly fixable. This skill walks every source file in your project, extracts regex literals, identifies catastrophic backtracking patterns, and tells you exactly which ones are dangerous and how to fix them.

**Supports JS/TS, Python, Go, Java, Ruby, PHP, Rust. Zero external API.**

---

## Trigger Phrases

- "regex security", "ReDoS", "catastrophic backtracking"
- "regex audit", "slow regex", "regex vulnerability"
- "check my regexes", "regex denial of service"
- "is this regex safe", "regex performance"
- "hardcoded locale regex", "missing anchor"
- "/regex-audit"

---

## How to Provide Input

```bash
# Option 1: Audit current directory (auto-detect all source files)
/regex-audit

# Option 2: Specific directory or file
/regex-audit src/
/regex-audit lib/validators.js

# Option 3: Focus on specific language
/regex-audit --lang js
/regex-audit --lang python

# Option 4: Show only CRITICAL and HIGH severity
/regex-audit --min-severity high

# Option 5: Check a single regex pattern for safety
/regex-audit --pattern "^(a+)+"

# Option 6: Focus on HTTP handler files (highest risk)
/regex-audit --high-risk-only

# Option 7: Output machine-readable JSON for CI
/regex-audit --json
```

---

## Step 1: Discover Source Files

```bash
python3 -c "
import glob, os
from pathlib import Path

# Language file patterns
patterns = {
    'JavaScript/TypeScript': ['**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx', '**/*.mjs'],
    'Python':    ['**/*.py'],
    'Go':        ['**/*.go'],
    'Java':      ['**/*.java'],
    'Ruby':      ['**/*.rb'],
    'PHP':       ['**/*.php'],
    'Rust':      ['**/*.rs'],
}

skip_dirs = {'node_modules', '.git', 'dist', 'build', '.next', 'vendor', '__pycache__', '.venv', 'venv'}

all_files = []
for lang, file_patterns in patterns.items():
    lang_files = []
    for p in file_patterns:
        for f in glob.glob(p, recursive=True):
            parts = set(Path(f).parts)
            if not parts & skip_dirs:
                lang_files.append(f)
    if lang_files:
        print(f'{lang}: {len(lang_files)} files')
        all_files.extend(lang_files)

print(f'\\nTotal: {len(all_files)} source files to scan')
"
```

---

## Step 2: Extract Regex Literals

```python
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class RegexMatch:
    file: str
    line: int
    pattern: str
    raw_context: str      # the surrounding code line
    language: str
    in_handler: bool      # is this in an HTTP handler / validator?

# Language-specific regex extraction patterns
EXTRACTORS = {
    'js': [
        # Regex literals: /pattern/flags
        re.compile(r'(?<![=!<>])\/([^\/\n\r]{3,}?)\/([gimsuy]*)'),
        # new RegExp("pattern")
        re.compile(r'new\s+RegExp\(["\']([^"\']{3,})["\']'),
        # .test(), .match(), .exec() with string literal
        re.compile(r'\.(?:test|match|exec|replace|search)\(["\'/]([^"\'\/\n]{3,})["\'/]'),
    ],
    'python': [
        # re.compile(r"pattern")
        re.compile(r're\.(?:compile|match|search|fullmatch|findall|finditer|sub|subn|split)\(["\']([^"\']{3,})["\']'),
        re.compile(r're\.(?:compile|match|search|fullmatch|findall|finditer|sub|subn|split)\(r["\']([^"\']{3,})["\']'),
    ],
    'go': [
        # regexp.MustCompile(`pattern`)
        re.compile(r'regexp\.(?:MustCompile|Compile|Match|MatchString)\(["`]([^"`]{3,})["`]'),
    ],
    'java': [
        # Pattern.compile("pattern")
        re.compile(r'Pattern\.compile\(["\']([^"\']{3,})["\']'),
        re.compile(r'\.matches\(["\']([^"\']{3,})["\']'),
    ],
    'ruby': [
        # /pattern/ or Regexp.new("pattern")
        re.compile(r'\/([^\/\n]{3,})\/'),
        re.compile(r'Regexp\.new\(["\']([^"\']{3,})["\']'),
    ],
    'php': [
        # preg_match('/pattern/', ...)
        re.compile(r'preg_(?:match|replace|split|grep)\(["\']([^"\']{3,})["\']'),
    ],
    'rust': [
        # Regex::new(r"pattern")
        re.compile(r'Regex::new\([r]?["\']([^"\']{3,})["\']'),
    ],
}

# Keywords that indicate high-risk call sites
HIGH_RISK_CONTEXTS = [
    'app.get', 'app.post', 'app.put', 'app.delete',
    'router.', 'express', 'fastify', 'koa',
    'validate', 'validator', 'sanitize',
    'request.body', 'req.body', 'req.params', 'req.query',
    'process.argv', 'sys.argv',
    'input(', 'readline(',
    'url.parse', 'new URL(',
    '@app.route', 'flask.request',
    'r.URL.Query', 'r.FormValue',
]

LANG_MAP = {
    '.js': 'js', '.jsx': 'js', '.ts': 'js', '.tsx': 'js', '.mjs': 'js',
    '.py': 'python',
    '.go': 'go',
    '.java': 'java',
    '.rb': 'ruby',
    '.php': 'php',
    '.rs': 'rust',
}


def extract_regexes_from_file(fpath: str) -> list[RegexMatch]:
    """Extract all regex literals from a source file."""
    ext = Path(fpath).suffix.lower()
    lang = LANG_MAP.get(ext)
    if not lang or lang not in EXTRACTORS:
        return []

    try:
        lines = Path(fpath).read_text(encoding='utf-8', errors='replace').splitlines()
    except Exception:
        return []

    results = []
    for line_num, line in enumerate(lines, 1):
        # Check if this line is in a high-risk context (look at surrounding 5 lines)
        context_window = '\n'.join(lines[max(0, line_num-5):line_num+5])
        in_handler = any(kw in context_window for kw in HIGH_RISK_CONTEXTS)

        for extractor in EXTRACTORS[lang]:
            for m in extractor.finditer(line):
                pattern = m.group(1)
                if len(pattern) >= 3:
                    results.append(RegexMatch(
                        file=fpath,
                        line=line_num,
                        pattern=pattern,
                        raw_context=line.strip(),
                        language=lang,
                        in_handler=in_handler,
                    ))

    return results
```

---

## Step 3: Detect ReDoS Patterns

```python
from enum import Enum

class Severity(Enum):
    CRITICAL = 4   # Exponential backtracking — proven DoS vector
    HIGH = 3       # Polynomial backtracking — slow on long inputs
    MEDIUM = 2     # Potentially slow — context-dependent
    LOW = 1        # Style/quality issue

@dataclass
class ReDoSFinding:
    regex_match: RegexMatch
    severity: Severity
    vulnerability_type: str
    dangerous_subpattern: str
    description: str
    attack_input_example: str
    fix_suggestion: str


# ReDoS pattern signatures
REDOS_PATTERNS = [

    # ===== CRITICAL: Exponential Backtracking =====

    {
        'name': 'NESTED_QUANTIFIERS',
        'severity': Severity.CRITICAL,
        'detector': re.compile(r'\(([^()]{1,30}\+[^()]{0,10})\)\+|\(([^()]{1,30}\*[^()]{0,10})\)\+'),
        'description': 'Nested quantifiers (a+)+ or (a*)+ create exponential backtracking.',
        'attack_shape': 'Long string of matching chars followed by one non-matching char',
        'example_attack': '"aaaaaaaaaaaaaaaaaaaaaaaaaX"',
        'fix': 'Use atomic group (?>...) or possessive quantifier — rewrite to remove nesting.',
    },
    {
        'name': 'NESTED_STAR_PLUS',
        'severity': Severity.CRITICAL,
        'detector': re.compile(r'\(([^()]{1,30})\)\*\+|\(([^()]{1,30})\)\+\*'),
        'description': 'Nested star/plus combination enables exponential path explosion.',
        'attack_shape': 'Repeated matching chars followed by failure',
        'example_attack': '"aaaaaaaaaaaX"',
        'fix': 'Flatten quantifiers or use possessive quantifiers.',
    },

    # ===== HIGH: Polynomial Backtracking =====

    {
        'name': 'ALTERNATION_OVERLAP',
        'severity': Severity.HIGH,
        'detector': re.compile(r'\(([a-zA-Z]{1,5})\|([a-zA-Z]{1,5})\)\+|\(([a-zA-Z]{1,5})\|([a-zA-Z]{1,5})\)\*'),
        'description': 'Overlapping alternation with quantifier: (ab|a)+ causes polynomial backtracking.',
        'attack_shape': 'Long string that partially matches both alternatives',
        'example_attack': '"ababababababababX"',
        'fix': 'Reorder alternatives longest-first; avoid overlapping prefixes. Use (?>a(?:b)?)+ instead of (ab|a)+',
    },
    {
        'name': 'GREEDY_DOTSTAR_ANCHORED',
        'severity': Severity.HIGH,
        'detector': re.compile(r'\.\*.*\.\*'),
        'description': 'Multiple .* in sequence causes O(n²) backtracking on non-matching inputs.',
        'attack_shape': 'Long string that partially matches then fails at the end',
        'example_attack': '"a" * 10000 + "X"',
        'fix': 'Use [^\\n]* instead of .* when newlines are impossible; add anchors.',
    },

    # ===== MEDIUM: Potentially Slow =====

    {
        'name': 'UNBOUNDED_REPETITION_COMPLEX',
        'severity': Severity.MEDIUM,
        'detector': re.compile(r'\([^()]{5,}\)\{[0-9,]+\}'),
        'description': 'Large repetition count on complex group — can be slow on long non-matching inputs.',
        'attack_shape': 'Input that triggers maximum iterations before failing',
        'example_attack': 'Input matching N-1 repetitions but failing on last character',
        'fix': 'Add possessive quantifier or reduce repetition scope.',
    },
    {
        'name': 'MISSING_ANCHORS',
        'severity': Severity.MEDIUM,
        'detector': None,  # Checked separately
        'description': 'Regex without ^ or $ anchors on email/URL patterns causes full-text search instead of match.',
        'attack_shape': 'Input containing valid pattern embedded in garbage',
        'example_attack': '"evil.com/redirect?to=legit.com"',
        'fix': 'Add ^ at start and $ at end: /^pattern$/',
    },
]


def analyze_regex_for_redos(rm: RegexMatch) -> list[ReDoSFinding]:
    """Check a single regex for ReDoS vulnerabilities."""
    findings = []
    pattern = rm.pattern

    for sig in REDOS_PATTERNS:
        if sig['detector'] is None:
            continue
        match = sig['detector'].search(pattern)
        if match:
            findings.append(ReDoSFinding(
                regex_match=rm,
                severity=sig['severity'],
                vulnerability_type=sig['name'],
                dangerous_subpattern=match.group(0),
                description=sig['description'],
                attack_input_example=sig.get('example_attack', ''),
                fix_suggestion=sig['fix'],
            ))

    # Check for missing anchors on patterns that look like email/URL/phone validators
    looks_like_validator = any(
        kw in rm.raw_context.lower()
        for kw in ['email', 'url', 'phone', 'validate', 'isValid', 'check']
    )
    if looks_like_validator and not (pattern.startswith('^') or pattern.endswith('$')):
        findings.append(ReDoSFinding(
            regex_match=rm,
            severity=Severity.MEDIUM,
            vulnerability_type='MISSING_ANCHORS',
            dangerous_subpattern=pattern[:40],
            description='Validator regex lacks ^ and $ anchors — matches anywhere in string.',
            attack_input_example='"garbage_validinput_garbage"',
            fix_suggestion=f'Add anchors: /^{pattern[:40]}$/',
        ))

    return findings


def check_locale_assumptions(rm: RegexMatch) -> Optional[ReDoSFinding]:
    """Detect ASCII-only character classes that should be locale-aware."""
    ASCII_ONLY_HINTS = [
        (re.compile(r'\[a-zA-Z\]|\[a-z\]|\[A-Z\]'), 'Matches only ASCII letters — fails on é, ü, ñ, etc.'),
        (re.compile(r'\[0-9\]'), 'Use \\d or [0-9] explicitly; be aware \\d matches Unicode digits in some engines'),
    ]
    for detector, msg in ASCII_ONLY_HINTS:
        if detector.search(rm.pattern):
            return ReDoSFinding(
                regex_match=rm,
                severity=Severity.LOW,
                vulnerability_type='LOCALE_ASSUMPTION',
                dangerous_subpattern=detector.search(rm.pattern).group(0),
                description=f'ASCII-only character class: {msg}',
                attack_input_example='"Ångström" or "naïve"',
                fix_suggestion='Use \\p{L} (Unicode letter) if your regex engine supports it, or explicitly list the characters you need.',
            )
    return None
```

---

## Step 4: Run Full Scan

```python
import os
import glob

def run_regex_audit(target_dir='.', min_severity=Severity.LOW, high_risk_only=False):
    """Full scan: discover files, extract regexes, analyze, report."""

    # Discover files
    all_files = []
    for ext in ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.py', '.go', '.java', '.rb', '.php', '.rs']:
        pattern = f'{target_dir}/**/*{ext}'
        for f in glob.glob(pattern, recursive=True):
            if not any(skip in f for skip in ['node_modules', '.git', 'dist', 'build', '.next', 'vendor']):
                all_files.append(f)

    # Extract and analyze
    all_findings = []
    total_regexes = 0

    for fpath in all_files:
        regexes = extract_regexes_from_file(fpath)
        total_regexes += len(regexes)

        for rm in regexes:
            if high_risk_only and not rm.in_handler:
                continue

            findings = analyze_regex_for_redos(rm)
            locale_finding = check_locale_assumptions(rm)
            if locale_finding:
                findings.append(locale_finding)

            for f in findings:
                if f.severity.value >= min_severity.value:
                    all_findings.append(f)

    # Sort by severity desc, then file
    all_findings.sort(key=lambda x: (-x.severity.value, x.regex_match.file, x.regex_match.line))

    return all_findings, total_regexes, len(all_files)
```

---

## Step 5: Output Report

```markdown
## ReDoS & Regex Security Audit
Project: my-app | Files scanned: 847 | Regexes found: 214

---

### Summary

| Severity | Count | Description |
|----------|-------|-------------|
| 🔴 CRITICAL | 2 | Exponential backtracking — proven DoS vector |
| 🟠 HIGH | 4 | Polynomial backtracking — slow on long inputs |
| 🟡 MEDIUM | 7 | Potentially slow or logic error |
| ⚪ LOW | 11 | Style/locale issues |

**⚠️ 3 findings are in HTTP request handlers — prioritize these.**

---

### 🔴 CRITICAL — Exponential Backtracking

**#1 — src/middleware/auth.js:47**
```js
// Context: JWT token format validator in Express middleware
app.use('/api', (req, res, next) => {
    const token = req.headers.authorization
    if (!/^([a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+$/.test(token)) { ... }
```

**Dangerous pattern:** `([a-zA-Z0-9_-]+\.)+`
**Vulnerability:** NESTED_QUANTIFIERS — the inner `+` and outer `+` create exponential backtracking.
**Attack input:** `"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"` (no dot — triggers backtracking)
**DoS potential:** Input of length 30 takes ~2 seconds on Node.js. Length 50 takes minutes.
**In HTTP handler:** ⚠️ YES — any unauthenticated request can trigger this.

**Fix:**
```js
// Before (vulnerable):
/^([a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+$/

// After (safe):
// Option 1: Possessive quantifier (not supported in JS — use atomic group via lookbehind trick)
// Option 2: Rewrite without nested quantifiers:
/^[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+$/
// This eliminates the nested quantifier — the outer group cannot backtrack
// into positions already consumed by the inner match.
```

---

**#2 — src/utils/email-validator.ts:12**
```ts
const EMAIL_RE = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@/
```

**Dangerous pattern:** `([^<>...]+(\.[^<>...]+)*)`
**Vulnerability:** NESTED_QUANTIFIERS inside alternation
**Attack input:** `"a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a.a@"` (missing domain after @)
**Fix:**
```ts
// Use a proven safe email regex:
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
// For strict RFC 5322: use the validator.js library (pre-audited, safe)
// npm install validator → isEmail(str)
```

---

### 🟠 HIGH — Polynomial Backtracking

**#3 — src/api/search.js:89**
```js
// URL parameter parser
const queryRe = /.*id=.*&.*/
```

**Vulnerability:** GREEDY_DOTSTAR_ANCHORED — `.*...*` is O(n²)
**Attack input:** 10,000-char query string with no `id=` → scans 10,000 × 10,000 positions
**In HTTP handler:** ⚠️ YES — `req.query` passed directly

**Fix:**
```js
// Before:
/.*id=.*&.*/
// After (anchored, no double .* scan):
/(?:^|&)id=([^&]+)/
```

---

### 🟡 MEDIUM — Missing Anchors

**#5 — src/validation/phone.ts:3**
```ts
const PHONE_RE = /\+?[0-9]{10,15}/   // used in: validatePhone(userInput)
```

**Issue:** No `^` or `$` anchor — matches `+15551234567` embedded in `"Call +15551234567 for support"`.
**Attack scenario:** Attacker bypasses phone validation by embedding valid number in malicious input.

**Fix:**
```ts
const PHONE_RE = /^\+?[0-9]{10,15}$/
```

---

### ⚪ LOW — Locale Assumptions

**#8 — src/utils/slugify.ts:7**
```ts
.replace(/[^a-zA-Z0-9-]/g, '-')
```

**Issue:** `[a-zA-Z]` excludes ñ, é, ü, ç, ș — slugs for non-English content will be all dashes.
**Fix:** Normalize Unicode first: `str.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9-]/gi, '-')`

---

### CI Integration

Add to your test suite or pre-commit hook:

```bash
# One-liner scan — exits non-zero if CRITICAL or HIGH found
python3 -c "
import re, sys, glob

NESTED_Q = re.compile(r'\(([^()]{1,30}\+[^()]{0,10})\)\+|\(([^()]{1,30})\)\*\+')
DOUBLE_STAR = re.compile(r'\.\*[^)]{0,10}\.\*')

found = []
for fpath in glob.glob('src/**/*.{js,ts,py}', recursive=True):
    lines = open(fpath, errors='replace').readlines()
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'/((?:[^/\\]|\\.){3,})/', line):
            pat = m.group(1)
            if NESTED_Q.search(pat) or DOUBLE_STAR.search(pat):
                found.append(f'{fpath}:{i}: {pat[:60]}')

if found:
    print(f'FAIL: {len(found)} ReDoS-vulnerable regex(es) found:')
    for f in found: print(' ', f)
    sys.exit(1)
else:
    print(f'PASS: No ReDoS patterns detected')
"
```

---

### Resources

- **safe-regex** npm package: `npx safe-regex "your-pattern"` — quick single-pattern check
- **vuln-regex-detector**: more comprehensive, uses fuzzing
- **OWASP ReDoS prevention**: https://owasp.org/www-community/attacks/ReDoS
- **Cloudflare outage 2019**: caused by a single ReDoS regex in a WAF rule
- **Stack Overflow outage 2016**: caused by `\s*` nested inside `\s+` in a markdown parser
```

---

## Quick Mode Output

```
ReDoS Audit: my-app (847 files, 214 regexes)

🔴 CRITICAL (2): 2 exponential-backtracking patterns in HTTP handlers
  src/middleware/auth.js:47  — ([a-zA-Z0-9_-]+\.)+ nested quantifiers
  src/utils/email-validator.ts:12 — complex email regex, nested groups

🟠 HIGH (4): polynomial backtracking
  src/api/search.js:89 — double .* in query parser (in HTTP handler ⚠️)
  src/parsers/csv.ts:23, src/lib/url.js:15, src/routes/user.ts:88

🟡 MEDIUM (7): missing anchors (5), unbounded complex groups (2)
⚪ LOW (11): locale assumptions in character classes

Priority: Fix auth.js:47 first — it's in unauthenticated middleware, CRITICAL severity
Quick win: s/([a-zA-Z0-9_-]+\.)+/[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+/ → safe in 30 seconds
```
