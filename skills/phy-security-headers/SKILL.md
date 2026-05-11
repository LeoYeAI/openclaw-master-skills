---
name: phy-security-headers
description: HTTP security header auditor that fetches response headers from any URL and grades them against OWASP, Mozilla Observatory, and Google standards. Checks Content-Security-Policy (detects unsafe-inline, wildcard sources, missing directives), HSTS (max-age, includeSubDomains, preload), X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, CORP/COEP/COOP isolation headers. Assigns A/B/C/F grade per header, generates a one-command nginx/Apache/Next.js fix for every gap. Works against any live URL or local dev server via curl. Zero external cloud account. Triggers on "security headers", "CSP audit", "HSTS missing", "clickjacking", "content security policy", "mozilla observatory", "/sec-headers".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - security
    - http-headers
    - csp
    - hsts
    - owasp
    - web-security
    - developer-tools
    - frontend
    - devops
    - compliance
---

# Security Headers Auditor

Your site passes all the security scanners until someone iframes it, injects a script through an open CDN source in your CSP, or steals credentials from a page with no HSTS preload.

This skill fetches your response headers, grades each security header against OWASP and Mozilla Observatory standards, and gives you the exact config line to add to nginx, Apache, Next.js, or Cloudflare Workers.

**Works against any URL via curl. Zero external API.**

---

## Trigger Phrases

- "security headers", "check my headers", "http headers audit"
- "CSP audit", "content security policy"
- "HSTS missing", "HSTS preload"
- "clickjacking protection", "X-Frame-Options"
- "mozilla observatory", "OWASP headers"
- "Permissions-Policy", "CORP COEP COOP"
- "/sec-headers"

---

## How to Provide Input

```bash
# Option 1: Audit a live URL
/sec-headers https://myapp.com

# Option 2: Audit local dev server
/sec-headers http://localhost:3000

# Option 3: Audit specific path
/sec-headers https://myapp.com/dashboard

# Option 4: Audit with custom port
/sec-headers https://staging.myapp.com:8443

# Option 5: Grade only (no fix suggestions)
/sec-headers https://myapp.com --grade-only

# Option 6: Generate nginx config snippet
/sec-headers https://myapp.com --output nginx

# Option 7: Generate Next.js headers config
/sec-headers https://myapp.com --output nextjs
```

---

## Step 1: Fetch Headers

```bash
# Fetch all response headers
URL="https://myapp.com"

curl -sI "$URL" \
  --max-time 10 \
  --user-agent "SecurityHeaderAuditor/1.0" \
  -L  # follow redirects

# Also check www redirect behavior
curl -sI "http://$URL" 2>/dev/null | head -5

# Save raw headers for parsing
HEADERS=$(curl -sI "$URL" --max-time 10 -L 2>/dev/null)
echo "$HEADERS"
```

---

## Step 2: Grade Each Header

```python
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HeaderCheck:
    name: str
    present: bool
    value: Optional[str]
    grade: str       # A / B / C / F / MISSING
    issues: list[str]
    fixes: list[str]
    severity: str    # CRITICAL / HIGH / MEDIUM / LOW / INFO


def fetch_headers(url: str) -> dict[str, str]:
    """Fetch HTTP response headers from URL."""
    result = subprocess.run(
        ['curl', '-sI', url, '--max-time', '10', '-L',
         '--user-agent', 'SecurityHeaderAuditor/1.0'],
        capture_output=True, text=True
    )
    headers = {}
    for line in result.stdout.splitlines():
        if ':' in line and not line.startswith('HTTP/'):
            key, _, value = line.partition(':')
            headers[key.strip().lower()] = value.strip()
    return headers


# ── Content-Security-Policy ──────────────────────────────────────────────────

def check_csp(value: Optional[str]) -> HeaderCheck:
    issues = []
    fixes = []
    grade = 'A'

    if not value:
        return HeaderCheck(
            name='Content-Security-Policy',
            present=False, value=None, grade='F',
            issues=['CSP header is missing — XSS attacks have no browser-level mitigation'],
            fixes=[
                "Add to nginx: add_header Content-Security-Policy "
                "\"default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self';\" always;",
                "Next.js (next.config.js headers): { key: 'Content-Security-Policy', value: \"default-src 'self'...\" }",
            ],
            severity='CRITICAL',
        )

    directives = {d.split()[0].lower(): d for d in value.split(';') if d.strip()}

    # unsafe-inline in script-src — CRITICAL
    script_src = directives.get('script-src', directives.get('default-src', ''))
    if "'unsafe-inline'" in script_src:
        grade = 'F'
        issues.append("'unsafe-inline' in script-src — negates XSS protection entirely")
        fixes.append("Replace 'unsafe-inline' with a nonce: script-src 'nonce-{random}' 'strict-dynamic'")

    # unsafe-eval
    if "'unsafe-eval'" in script_src:
        grade = 'C' if grade == 'A' else grade
        issues.append("'unsafe-eval' allows eval() — enables second-order XSS")
        fixes.append("Remove 'unsafe-eval'; refactor code using eval() to use Function() alternatives")

    # Wildcard source
    for directive_name, directive_val in directives.items():
        if re.search(r'\bhttps?://\*\b|^\*$', directive_val):
            grade = 'C' if grade == 'A' else grade
            issues.append(f"Wildcard source (*) in {directive_name} — allows loading from any domain")
            fixes.append(f"Replace * in {directive_name} with explicit trusted domains")

    # Missing object-src
    if 'object-src' not in directives and 'default-src' not in directives:
        grade = 'B' if grade == 'A' else grade
        issues.append("Missing object-src — allows Flash/plugin injection if default-src not set")
        fixes.append("Add: object-src 'none'")

    # Missing base-uri
    if 'base-uri' not in directives:
        issues.append("Missing base-uri — allows <base> tag injection to hijack relative URLs")
        fixes.append("Add: base-uri 'self'")

    # report-uri / report-to
    if 'report-uri' not in directives and 'report-to' not in directives:
        issues.append("No CSP violation reporting configured — violations are silent")
        fixes.append("Add: report-to /csp-violations  (or use report-uri https://yoursite.com/csp-report)")

    return HeaderCheck(
        name='Content-Security-Policy', present=True, value=value,
        grade=grade, issues=issues, fixes=fixes, severity='CRITICAL' if grade == 'F' else 'HIGH'
    )


# ── HSTS ─────────────────────────────────────────────────────────────────────

def check_hsts(value: Optional[str], is_https: bool = True) -> HeaderCheck:
    if not value:
        return HeaderCheck(
            name='Strict-Transport-Security', present=False, value=None, grade='F',
            issues=['HSTS missing — browser allows HTTP downgrade attacks'],
            fixes=[
                "nginx: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\" always;",
                "Apache: Header always set Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\"",
            ],
            severity='HIGH',
        )

    issues = []
    fixes = []
    grade = 'A'

    # max-age
    max_age_match = re.search(r'max-age=(\d+)', value, re.I)
    if max_age_match:
        max_age = int(max_age_match.group(1))
        if max_age < 2592000:  # 30 days
            grade = 'C'
            issues.append(f"max-age={max_age} is too short (< 30 days) — not eligible for preload list")
            fixes.append("Set max-age=31536000 (1 year) minimum for preload eligibility")
        elif max_age < 31536000:
            grade = 'B'
            issues.append(f"max-age={max_age} — recommend 31536000 (1 year) for preload eligibility")
    else:
        grade = 'F'
        issues.append("max-age directive missing from HSTS header")
        fixes.append("Add max-age=31536000 to HSTS header")

    # includeSubDomains
    if 'includesubdomains' not in value.lower():
        grade = 'B' if grade == 'A' else grade
        issues.append("Missing includeSubDomains — subdomains can be downgraded to HTTP")
        fixes.append("Add includeSubDomains directive")

    # preload
    if 'preload' not in value.lower():
        issues.append("Missing preload directive — site not eligible for HSTS preload list")
        fixes.append("Add preload directive and submit to hstspreload.org")

    return HeaderCheck(
        name='Strict-Transport-Security', present=True, value=value,
        grade=grade, issues=issues, fixes=fixes, severity='HIGH' if grade != 'A' else 'INFO'
    )


# ── X-Frame-Options ──────────────────────────────────────────────────────────

def check_xfo(value: Optional[str], csp_value: Optional[str] = None) -> HeaderCheck:
    # If CSP has frame-ancestors, XFO is redundant (CSP takes precedence)
    if csp_value and 'frame-ancestors' in csp_value.lower():
        return HeaderCheck(
            name='X-Frame-Options', present=bool(value), value=value, grade='A',
            issues=[], fixes=["frame-ancestors in CSP supersedes X-Frame-Options (modern browsers)"],
            severity='INFO'
        )

    if not value:
        return HeaderCheck(
            name='X-Frame-Options', present=False, value=None, grade='F',
            issues=['Missing — site is vulnerable to clickjacking attacks'],
            fixes=[
                "nginx: add_header X-Frame-Options \"DENY\" always;",
                "Or add to CSP: frame-ancestors 'none'  (preferred — supports more granular rules)",
            ],
            severity='HIGH',
        )

    val_upper = value.strip().upper()
    if val_upper == 'DENY':
        return HeaderCheck(name='X-Frame-Options', present=True, value=value, grade='A',
                           issues=[], fixes=[], severity='INFO')
    elif val_upper == 'SAMEORIGIN':
        return HeaderCheck(name='X-Frame-Options', present=True, value=value, grade='B',
                           issues=["SAMEORIGIN allows framing from same origin — DENY is stronger"],
                           fixes=["Change to DENY unless you deliberately embed the page in an iframe"],
                           severity='LOW')
    else:
        return HeaderCheck(name='X-Frame-Options', present=True, value=value, grade='C',
                           issues=[f"Non-standard value: {value}"],
                           fixes=["Use DENY or SAMEORIGIN"], severity='MEDIUM')


# ── X-Content-Type-Options ────────────────────────────────────────────────────

def check_xcto(value: Optional[str]) -> HeaderCheck:
    if not value:
        return HeaderCheck(
            name='X-Content-Type-Options', present=False, value=None, grade='F',
            issues=['Missing — browser may MIME-sniff responses enabling content injection'],
            fixes=["nginx: add_header X-Content-Type-Options \"nosniff\" always;"],
            severity='MEDIUM',
        )
    if value.strip().lower() == 'nosniff':
        return HeaderCheck(name='X-Content-Type-Options', present=True, value=value,
                           grade='A', issues=[], fixes=[], severity='INFO')
    return HeaderCheck(name='X-Content-Type-Options', present=True, value=value,
                       grade='C', issues=[f"Unexpected value: {value} (expected nosniff)"],
                       fixes=["Set to nosniff"], severity='LOW')


# ── Referrer-Policy ──────────────────────────────────────────────────────────

SAFE_REFERRER_POLICIES = {
    'no-referrer', 'no-referrer-when-downgrade',
    'same-origin', 'strict-origin', 'strict-origin-when-cross-origin'
}

def check_referrer_policy(value: Optional[str]) -> HeaderCheck:
    if not value:
        return HeaderCheck(
            name='Referrer-Policy', present=False, value=None, grade='C',
            issues=['Missing — browser defaults to no-referrer-when-downgrade (leaks full URL to same-HTTPS origins)'],
            fixes=["nginx: add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;"],
            severity='LOW',
        )
    if value.strip().lower() in SAFE_REFERRER_POLICIES:
        return HeaderCheck(name='Referrer-Policy', present=True, value=value,
                           grade='A', issues=[], fixes=[], severity='INFO')
    if value.strip().lower() in ('unsafe-url', 'origin-when-cross-origin'):
        return HeaderCheck(name='Referrer-Policy', present=True, value=value, grade='F',
                           issues=[f"'{value}' leaks full URL or origin to cross-origin requests"],
                           fixes=["Change to strict-origin-when-cross-origin"],
                           severity='MEDIUM')
    return HeaderCheck(name='Referrer-Policy', present=True, value=value, grade='B',
                       issues=[], fixes=[], severity='INFO')


# ── Permissions-Policy ───────────────────────────────────────────────────────

SENSITIVE_FEATURES = ['camera', 'microphone', 'geolocation', 'payment', 'usb',
                       'fullscreen', 'accelerometer', 'gyroscope', 'magnetometer',
                       'ambient-light-sensor', 'battery', 'screen-wake-lock']

def check_permissions_policy(value: Optional[str]) -> HeaderCheck:
    if not value:
        return HeaderCheck(
            name='Permissions-Policy', present=False, value=None, grade='C',
            issues=['Missing — browser APIs (camera, mic, geolocation) may be accessible to injected scripts'],
            fixes=[
                "nginx: add_header Permissions-Policy "
                "\"camera=(), microphone=(), geolocation=(), payment=(), usb=()\" always;",
            ],
            severity='LOW',
        )
    issues = []
    directives = {d.split('=')[0].strip().lower(): d for d in value.split(',') if d.strip()}
    unconstrained = [f for f in SENSITIVE_FEATURES if f not in directives]
    if unconstrained:
        issues.append(f"Sensitive features not explicitly disabled: {', '.join(unconstrained)}")
    return HeaderCheck(
        name='Permissions-Policy', present=True, value=value,
        grade='A' if not unconstrained else 'B',
        issues=issues,
        fixes=[f"Add {f}=() to Permissions-Policy to disable it" for f in unconstrained[:3]],
        severity='LOW' if issues else 'INFO'
    )


# ── Cross-Origin Isolation (CORP / COEP / COOP) ──────────────────────────────

def check_cross_origin_isolation(headers: dict) -> list[HeaderCheck]:
    checks = []

    coep = headers.get('cross-origin-embedder-policy')
    coop = headers.get('cross-origin-opener-policy')
    corp = headers.get('cross-origin-resource-policy')

    if not coep:
        checks.append(HeaderCheck(
            name='Cross-Origin-Embedder-Policy', present=False, value=None, grade='C',
            issues=['Missing COEP — cross-origin isolation not achievable (needed for SharedArrayBuffer)'],
            fixes=["add_header Cross-Origin-Embedder-Policy \"require-corp\" always;"],
            severity='LOW'
        ))
    else:
        checks.append(HeaderCheck(
            name='Cross-Origin-Embedder-Policy', present=True, value=coep,
            grade='A', issues=[], fixes=[], severity='INFO'
        ))

    if not coop:
        checks.append(HeaderCheck(
            name='Cross-Origin-Opener-Policy', present=False, value=None, grade='C',
            issues=['Missing COOP — page may be accessible from cross-origin windows (Spectre risk)'],
            fixes=["add_header Cross-Origin-Opener-Policy \"same-origin\" always;"],
            severity='LOW'
        ))
    else:
        checks.append(HeaderCheck(
            name='Cross-Origin-Opener-Policy', present=True, value=coop,
            grade='A', issues=[], fixes=[], severity='INFO'
        ))

    return checks


def audit_security_headers(url: str) -> list[HeaderCheck]:
    """Run full security header audit against a URL."""
    headers = fetch_headers(url)
    is_https = url.startswith('https')

    csp_val = headers.get('content-security-policy')
    results = [
        check_csp(csp_val),
        check_hsts(headers.get('strict-transport-security'), is_https),
        check_xfo(headers.get('x-frame-options'), csp_val),
        check_xcto(headers.get('x-content-type-options')),
        check_referrer_policy(headers.get('referrer-policy')),
        check_permissions_policy(headers.get('permissions-policy')),
    ]
    results.extend(check_cross_origin_isolation(headers))
    return results
```

---

## Step 3: Calculate Grade

```python
GRADE_WEIGHTS = {
    'Content-Security-Policy':           3,   # Most impactful
    'Strict-Transport-Security':         2,
    'X-Frame-Options':                   2,
    'X-Content-Type-Options':            1,
    'Referrer-Policy':                   1,
    'Permissions-Policy':                1,
    'Cross-Origin-Embedder-Policy':      0.5,
    'Cross-Origin-Opener-Policy':        0.5,
}

GRADE_SCORE = {'A': 100, 'B': 75, 'C': 50, 'F': 0, 'MISSING': 0}


def overall_grade(checks: list) -> tuple[str, int]:
    """Compute weighted average score and letter grade."""
    total_weight = 0
    weighted_score = 0
    for check in checks:
        w = GRADE_WEIGHTS.get(check.name, 1)
        score = GRADE_SCORE.get(check.grade, 0)
        weighted_score += score * w
        total_weight += w

    pct = int(weighted_score / total_weight) if total_weight else 0

    if pct >= 90:   letter = 'A'
    elif pct >= 75: letter = 'B'
    elif pct >= 50: letter = 'C'
    elif pct >= 25: letter = 'D'
    else:           letter = 'F'

    return letter, pct
```

---

## Step 4: Generate Config Fixes

```python
def generate_nginx_config(checks: list) -> str:
    """Generate a complete nginx add_header block for all failing headers."""
    lines = ["# Security Headers — generated by phy-security-headers", ""]

    NGINX_TEMPLATES = {
        'Content-Security-Policy': (
            "add_header Content-Security-Policy "
            "\"default-src 'self'; script-src 'self' 'nonce-REPLACE_WITH_NONCE'; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; "
            "upgrade-insecure-requests;\" always;"
        ),
        'Strict-Transport-Security':
            "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\" always;",
        'X-Frame-Options':
            "add_header X-Frame-Options \"DENY\" always;",
        'X-Content-Type-Options':
            "add_header X-Content-Type-Options \"nosniff\" always;",
        'Referrer-Policy':
            "add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;",
        'Permissions-Policy':
            "add_header Permissions-Policy \"camera=(), microphone=(), geolocation=(), payment=(), usb=()\" always;",
        'Cross-Origin-Embedder-Policy':
            "add_header Cross-Origin-Embedder-Policy \"require-corp\" always;",
        'Cross-Origin-Opener-Policy':
            "add_header Cross-Origin-Opener-Policy \"same-origin\" always;",
        'Cross-Origin-Resource-Policy':
            "add_header Cross-Origin-Resource-Policy \"same-origin\" always;",
    }

    for check in checks:
        if check.grade in ('F', 'C', 'MISSING') and check.name in NGINX_TEMPLATES:
            lines.append(NGINX_TEMPLATES[check.name])

    return '\n'.join(lines)


def generate_nextjs_config(checks: list) -> str:
    """Generate Next.js next.config.js headers() array."""
    lines = [
        "// next.config.js — Security Headers",
        "const securityHeaders = [",
    ]
    NEXTJS_TEMPLATES = {
        'Content-Security-Policy': (
            "  { key: 'Content-Security-Policy', "
            "value: \"default-src 'self'; script-src 'self'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none';\" },"
        ),
        'Strict-Transport-Security':
            "  { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains; preload' },",
        'X-Frame-Options':
            "  { key: 'X-Frame-Options', value: 'DENY' },",
        'X-Content-Type-Options':
            "  { key: 'X-Content-Type-Options', value: 'nosniff' },",
        'Referrer-Policy':
            "  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },",
        'Permissions-Policy':
            "  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },",
    }
    for check in checks:
        if check.grade in ('F', 'C', 'MISSING') and check.name in NEXTJS_TEMPLATES:
            lines.append(NEXTJS_TEMPLATES[check.name])
    lines.extend([
        "];",
        "",
        "module.exports = {",
        "  async headers() {",
        "    return [{ source: '/(.*)', headers: securityHeaders }];",
        "  },",
        "};",
    ])
    return '\n'.join(lines)
```

---

## Step 5: Output Report

```markdown
## Security Headers Audit
URL: https://myapp.com | Checked: 2026-03-19 09:22 UTC

---

### Overall Grade: C (54/100)

| Header | Grade | Status | Key Issue |
|--------|-------|--------|-----------|
| Content-Security-Policy | F | 🔴 FAIL | 'unsafe-inline' in script-src |
| Strict-Transport-Security | B | 🟡 REVIEW | max-age=86400 too short, no preload |
| X-Frame-Options | A | ✅ PASS | DENY |
| X-Content-Type-Options | A | ✅ PASS | nosniff |
| Referrer-Policy | C | 🟠 WARN | Missing |
| Permissions-Policy | C | 🟠 WARN | Missing |
| Cross-Origin-Embedder-Policy | C | 🟠 WARN | Missing |
| Cross-Origin-Opener-Policy | C | 🟠 WARN | Missing |

---

### 🔴 CRITICAL — Content-Security-Policy

**Found:** `default-src 'self' 'unsafe-inline' https://cdn.example.com`

**Issue 1:** `'unsafe-inline'` in default-src — completely negates XSS protection.
Any injected `<script>` will execute. This is as bad as no CSP.

**Fix:**
```html
<!-- Replace unsafe-inline with nonce-based CSP -->
<!-- In your HTML template, add nonce to every script tag: -->
<script nonce="{{CSP_NONCE}}">...</script>

<!-- Set header with matching nonce: -->
Content-Security-Policy: default-src 'self';
  script-src 'self' 'nonce-ABC123' 'strict-dynamic';
  object-src 'none';
  base-uri 'self';
  frame-ancestors 'none';
```

```python
# Express.js nonce middleware:
import secrets
app.use((req, res, next) => {
    res.locals.nonce = secrets.token_hex(16)
    res.setHeader('Content-Security-Policy',
        `script-src 'nonce-${res.locals.nonce}' 'strict-dynamic'`)
    next()
})
```

---

### 🟡 REVIEW — Strict-Transport-Security

**Found:** `max-age=86400`

**Issue:** max-age=86400 (1 day) — too short for HSTS preload eligibility (minimum 1 year).
Browser will stop enforcing HTTPS after 24 hours if a user hasn't visited recently.

**Fix:**
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

**Submit to preload list:** After fixing → https://hstspreload.org

---

### 🟠 MISSING — Referrer-Policy

**Fix:**
```nginx
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

### Generated Config Fixes

**nginx (add to server block):**
```nginx
# Security Headers — generated by phy-security-headers
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'nonce-REPLACE_WITH_NONCE'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; upgrade-insecure-requests;" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=()" always;
add_header Cross-Origin-Embedder-Policy "require-corp" always;
add_header Cross-Origin-Opener-Policy "same-origin" always;
```

**Verify after deploy:**
```bash
curl -sI https://myapp.com | grep -i -E "content-security|strict-transport|x-frame|x-content|referrer|permissions"
```

---

### Mozilla Observatory Equivalent Score

This audit maps to Mozilla Observatory (observatory.mozilla.org) scoring:
- CSP with unsafe-inline: -25 pts
- HSTS max-age < 6 months: -5 pts
- Missing Referrer-Policy: -5 pts
- Missing Permissions-Policy: -5 pts

**Estimated Observatory Score: ~45/100 (D)**
Fix the CSP first — it alone accounts for 25 points.
```

---

## Quick Mode Output

```
Security Headers: https://myapp.com

Overall: C (54/100)

🔴 CSP: F — 'unsafe-inline' negates XSS protection (fix: nonce-based CSP)
🟡 HSTS: B — max-age=86400 too short (fix: 31536000 + preload)
✅ X-Frame-Options: A — DENY
✅ X-Content-Type-Options: A — nosniff
🟠 Referrer-Policy: MISSING
🟠 Permissions-Policy: MISSING
🟠 COEP/COOP: MISSING

Priority fix: Replace 'unsafe-inline' with nonce → lifts score to A (89/100)
```
