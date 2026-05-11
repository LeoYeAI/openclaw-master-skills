---
name: phy-jwt-auth-audit
description: JWT and OAuth/OIDC security auditor. Decodes any JWT token (without verification) to inspect alg/exp/iss/aud/scope claims, detects the "alg:none" bypass vulnerability, expired or no-expiry tokens, overly broad OAuth scopes, JWT stored in localStorage (XSS theft risk), JWT in URL parameters (log leakage), missing issuer/audience validation in source code, hardcoded tokens in .env files, and weak HMAC secrets. Also scans source files for insecure token handling patterns: Bearer token logged, token compared with ==, auth bypass via role:admin in payload. Generates a severity-ranked report with exact code locations and fixes. Zero external API — pure local analysis. Triggers on "JWT audit", "token security", "auth security", "alg none", "OAuth scopes", "bearer token", "token expiry", "/jwt-audit".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - security
    - jwt
    - oauth
    - authentication
    - token-security
    - static-analysis
    - developer-tools
    - owasp
    - api-security
    - compliance
---

# JWT & Auth Auditor

A developer pastes a JWT into a debug log. The logger ships it to Datadog. An attacker finds it in the logs 6 months later. The token never expires.

This skill decodes JWTs without verifying them (which is the point — you need to inspect them even when you don't have the secret), checks their claims against security best practices, scans your codebase for insecure token handling, and finds the OAuth scopes that give more access than necessary.

**Zero external API — all analysis runs locally. Works with any JWT/OAuth provider.**

---

## Trigger Phrases

- "JWT audit", "token security check"
- "auth security", "authentication review"
- "alg:none vulnerability", "JWT algorithm"
- "OAuth scopes", "bearer token check"
- "token expiry", "no exp claim"
- "JWT in localStorage", "token in URL"
- "/jwt-audit"

---

## How to Provide Input

```bash
# Option 1: Decode and audit a specific JWT token
/jwt-audit eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Option 2: Audit source code for insecure token handling
/jwt-audit --scan src/

# Option 3: Audit .env files for hardcoded tokens
/jwt-audit --env-scan

# Option 4: Audit a specific auth file
/jwt-audit src/middleware/auth.ts

# Option 5: Full audit (token decode + code scan + env scan)
/jwt-audit eyJhbG... --scan . --env-scan

# Option 6: Check OAuth scopes in API calls
/jwt-audit --check-scopes

# Option 7: CI mode (exit 1 on critical findings)
/jwt-audit --scan src/ --ci --max-critical 0
```

---

## Step 1: Decode and Analyze JWT Claims

```python
import base64
import json
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class JwtFinding:
    severity: str       # CRITICAL / HIGH / MEDIUM / LOW / INFO
    claim: str          # which claim is affected
    issue: str
    detail: str
    fix: str


def decode_jwt_unsafe(token: str) -> tuple[dict, dict, str]:
    """
    Decode a JWT token WITHOUT verifying the signature.
    Returns (header, payload, signature_b64).
    Safe for inspection purposes — never use for auth decisions.
    """
    parts = token.strip().split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid JWT format: expected 3 parts, got {len(parts)}")

    def b64_decode(s: str) -> dict:
        # JWT uses URL-safe base64 without padding
        padding = 4 - len(s) % 4
        if padding != 4:
            s += '=' * padding
        raw = base64.urlsafe_b64decode(s)
        return json.loads(raw)

    header = b64_decode(parts[0])
    payload = b64_decode(parts[1])
    signature = parts[2]

    return header, payload, signature


def analyze_jwt_claims(token: str) -> list[JwtFinding]:
    """Full security analysis of a JWT token's claims and header."""
    findings = []

    try:
        header, payload, sig = decode_jwt_unsafe(token)
    except Exception as e:
        return [JwtFinding(
            severity='CRITICAL', claim='format',
            issue='Invalid JWT format', detail=str(e),
            fix='Ensure token is a valid JWT (3 base64url parts separated by dots)'
        )]

    now = int(time.time())

    # ── Algorithm checks ─────────────────────────────────────────────────────

    alg = header.get('alg', '')

    if alg.lower() == 'none':
        findings.append(JwtFinding(
            severity='CRITICAL', claim='alg',
            issue='Algorithm "none" — signature verification disabled',
            detail=(
                'alg:none means the JWT has no signature. Any payload can be crafted '
                'and will be accepted by a vulnerable server. This is CVE-2015-9235.'
            ),
            fix=(
                'Server must reject tokens with alg:none. '
                'In jsonwebtoken: jwt.verify(token, secret, { algorithms: ["HS256"] })'
            ),
        ))

    elif alg.startswith('HS') and len(sig) < 32:
        findings.append(JwtFinding(
            severity='HIGH', claim='alg',
            issue=f'Algorithm {alg} with suspiciously short signature',
            detail='Short signature may indicate a weak or guessable HMAC secret.',
            fix='Use a minimum 256-bit (32-byte) random secret for HMAC-SHA256',
        ))

    elif alg == 'RS256' or alg == 'ES256':
        findings.append(JwtFinding(
            severity='INFO', claim='alg',
            issue=f'Algorithm: {alg} (asymmetric — good)',
            detail='RSA/ECDSA signature — cannot be forged without the private key.',
            fix='Ensure public key is loaded from a trusted source, not from the JWT header itself.',
        ))

    # Algorithm confusion: HS256 when server expects RS256
    if alg == 'HS256':
        findings.append(JwtFinding(
            severity='MEDIUM', claim='alg',
            issue='HS256 — verify server rejects RS256→HS256 algorithm confusion',
            detail=(
                'If the server also supports RS256, an attacker may forge tokens using '
                'the public key as the HMAC secret (CVE-2016-10555 pattern).'
            ),
            fix=(
                'Explicitly specify allowed algorithms on verify: '
                'jwt.verify(token, secret, { algorithms: ["HS256"] })'
            ),
        ))

    # ── Expiry checks ────────────────────────────────────────────────────────

    exp = payload.get('exp')
    iat = payload.get('iat')
    nbf = payload.get('nbf')

    if exp is None:
        findings.append(JwtFinding(
            severity='HIGH', claim='exp',
            issue='No expiry (exp) claim — token is valid forever',
            detail=(
                'Without exp, a stolen token can be used indefinitely. '
                'OWASP API Security Top 10 A2: Broken Authentication.'
            ),
            fix='Add exp claim: { exp: Math.floor(Date.now()/1000) + (60*60) } // 1 hour',
        ))
    else:
        ttl = exp - now
        if ttl < 0:
            findings.append(JwtFinding(
                severity='HIGH', claim='exp',
                issue=f'Token EXPIRED {abs(ttl)//3600}h {(abs(ttl)%3600)//60}m ago',
                detail=f'exp={exp}, current time={now}. Using an expired token is a security risk.',
                fix='Generate a fresh token. Check if your token refresh logic is working.',
            ))
        elif ttl > 86400 * 30:  # > 30 days
            findings.append(JwtFinding(
                severity='MEDIUM', claim='exp',
                issue=f'Token expires in {ttl//86400} days — very long-lived',
                detail='Long-lived tokens increase the window of exposure after theft.',
                fix=(
                    'Use short-lived access tokens (≤1 hour) + refresh tokens. '
                    'For JWTs: exp should be 15min–1hr for sensitive endpoints.'
                ),
            ))
        else:
            findings.append(JwtFinding(
                severity='INFO', claim='exp',
                issue=f'Token expires in {ttl//3600}h {(ttl%3600)//60}m',
                detail=f'exp={exp}',
                fix='',
            ))

    # ── Issuer / Audience ────────────────────────────────────────────────────

    iss = payload.get('iss')
    aud = payload.get('aud')

    if not iss:
        findings.append(JwtFinding(
            severity='MEDIUM', claim='iss',
            issue='Missing issuer (iss) claim',
            detail='Without iss, tokens from different issuers (auth providers) are indistinguishable.',
            fix='Add iss claim and validate it on the server: verify(token, key, { issuer: "https://auth.myapp.com" })',
        ))

    if not aud:
        findings.append(JwtFinding(
            severity='MEDIUM', claim='aud',
            issue='Missing audience (aud) claim',
            detail=(
                'Without aud, a token issued for service A can be used against service B. '
                'This enables cross-service replay attacks.'
            ),
            fix='Add aud claim and validate: verify(token, key, { audience: "api.myapp.com" })',
        ))

    # ── Sensitive data in payload ─────────────────────────────────────────────

    SENSITIVE_KEYS = ['password', 'secret', 'credit_card', 'ssn', 'cvv', 'private_key']
    for key in SENSITIVE_KEYS:
        if key in payload:
            findings.append(JwtFinding(
                severity='CRITICAL', claim=key,
                issue=f'Sensitive field "{key}" in JWT payload',
                detail=(
                    'JWT payloads are base64-encoded, NOT encrypted. '
                    'Anyone with the token can decode and read this value.'
                ),
                fix=f'Remove "{key}" from JWT payload. Use JWE (JSON Web Encryption) if the data must be in the token.',
            ))

    # ── Scope analysis ────────────────────────────────────────────────────────

    scope = payload.get('scope', payload.get('scp', ''))
    if isinstance(scope, str):
        scopes = scope.split()
    elif isinstance(scope, list):
        scopes = scope
    else:
        scopes = []

    OVERLY_BROAD_SCOPES = {
        'admin', 'root', 'superuser', '*', 'all', 'write:*', 'read:*',
        'openid email profile address phone offline_access',  # too many OIDC scopes
    }
    for s in scopes:
        if s in OVERLY_BROAD_SCOPES or s.endswith(':*'):
            findings.append(JwtFinding(
                severity='HIGH', claim='scope',
                issue=f'Overly broad scope: "{s}"',
                detail='This scope grants more access than most operations need (principle of least privilege violation).',
                fix='Issue tokens with minimal scopes needed for each operation.',
            ))

    # ── Role escalation risk ─────────────────────────────────────────────────

    role = payload.get('role', payload.get('roles', payload.get('groups', [])))
    if isinstance(role, str):
        role = [role]
    if isinstance(role, list):
        for r in role:
            if str(r).lower() in ('admin', 'superadmin', 'root', 'super_admin'):
                findings.append(JwtFinding(
                    severity='MEDIUM', claim='role',
                    issue=f'Admin role in JWT payload: role="{r}"',
                    detail=(
                        'If the server trusts the role claim from the JWT without '
                        'verifying against a database, any token can be forged to role:admin.'
                    ),
                    fix='Validate roles from the database, not from the JWT payload claims.',
                ))

    return findings, header, payload
```

---

## Step 2: Scan Source Code for Insecure Token Handling

```python
import re
import glob
from pathlib import Path

SKIP_DIRS = {'node_modules', '.git', 'dist', 'build', '__pycache__',
             '.next', 'vendor', 'venv', '.venv'}

# Source code anti-patterns
CODE_PATTERNS = [

    # JWT decoded but alg not validated
    {
        'name': 'JWT_NO_ALG_VALIDATION',
        'pattern': re.compile(r'jwt\.(verify|decode)\s*\([^,)]+,\s*[^,)]+\)', re.I),
        'check': lambda line, ctx: 'algorithm' not in ctx and 'algorithms' not in ctx,
        'severity': 'HIGH',
        'message': 'jwt.verify() without algorithms option — vulnerable to alg:none and algorithm confusion',
        'fix': 'Add algorithms option: jwt.verify(token, secret, { algorithms: ["HS256"] })',
    },

    # Token stored in localStorage
    {
        'name': 'LOCALSTORAGE_TOKEN',
        'pattern': re.compile(
            r'localStorage\.(setItem|getItem)\s*\(["\'](?:token|auth|jwt|access_token|bearer)["\']',
            re.I
        ),
        'check': lambda line, ctx: True,
        'severity': 'HIGH',
        'message': 'Token stored in localStorage — vulnerable to XSS theft',
        'fix': 'Store tokens in httpOnly cookies (inaccessible to JavaScript): Set-Cookie: token=X; HttpOnly; Secure; SameSite=Strict',
    },

    # Token in URL / query parameter
    {
        'name': 'TOKEN_IN_URL',
        'pattern': re.compile(
            r'[\?&](token|access_token|jwt|auth_token|bearer)\s*=',
            re.I
        ),
        'check': lambda line, ctx: True,
        'severity': 'HIGH',
        'message': 'Token in URL query parameter — appears in server logs, browser history, Referer headers',
        'fix': 'Pass token in Authorization header: Authorization: Bearer <token>',
    },

    # Bearer token logged
    {
        'name': 'TOKEN_LOGGED',
        'pattern': re.compile(
            r'(console\.|logger\.|log\.|print\()[^;)]*(?:token|bearer|jwt|auth)',
            re.I
        ),
        'check': lambda line, ctx: True,
        'severity': 'CRITICAL',
        'message': 'Auth token may be logged — enables credential theft from log systems',
        'fix': 'Never log tokens. Log: { has_token: !!token } instead.',
    },

    # Token compared with == (timing attack)
    {
        'name': 'TIMING_ATTACK',
        'pattern': re.compile(
            r'(?:token|secret|hmac)\s*[=!]=\s*|===\s*(?:token|secret|hmac)',
            re.I
        ),
        'check': lambda line, ctx: True,
        'severity': 'MEDIUM',
        'message': 'Token/secret compared with == — vulnerable to timing attacks',
        'fix': 'Use constant-time comparison: crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b))',
    },

    # Missing Bearer prefix check
    {
        'name': 'MISSING_BEARER_CHECK',
        'pattern': re.compile(
            r'req\.headers\.authorization\s*\|\|\s*req\.headers\[.authorization.\]',
            re.I
        ),
        'check': lambda line, ctx: 'split' not in ctx and 'Bearer' not in ctx,
        'severity': 'MEDIUM',
        'message': 'Authorization header accessed without validating "Bearer " prefix',
        'fix': (
            "const [scheme, token] = req.headers.authorization?.split(' ') ?? [];\n"
            "if (scheme !== 'Bearer') throw new Error('Invalid auth scheme');"
        ),
    },

    # Python: PyJWT decode without verification
    {
        'name': 'PYJWT_NO_VERIFY',
        'pattern': re.compile(r'jwt\.decode\s*\([^)]*options\s*=.*verify_signature.*False', re.I),
        'check': lambda line, ctx: True,
        'severity': 'CRITICAL',
        'message': 'PyJWT decode with verify_signature=False — signature is NOT checked',
        'fix': 'Remove options={"verify_signature": False} unless you explicitly need unsigned inspection',
    },

    # Hardcoded JWT secret
    {
        'name': 'HARDCODED_JWT_SECRET',
        'pattern': re.compile(
            r'(jwt_secret|JWT_SECRET|jwtSecret|secret)\s*[=:]\s*["\'](?!process\.|os\.|getenv)[^"\']{4,}["\']',
            re.I
        ),
        'check': lambda line, ctx: True,
        'severity': 'CRITICAL',
        'message': 'Hardcoded JWT secret in source code — anyone with repo access can forge tokens',
        'fix': 'Load from environment: process.env.JWT_SECRET or os.getenv("JWT_SECRET")',
    },
]


def scan_auth_code(src_dir: str = '.') -> list[dict]:
    findings = []

    for ext in ['.js', '.ts', '.jsx', '.tsx', '.py', '.go', '.java', '.rb']:
        for fpath in glob.glob(f'{src_dir}/**/*{ext}', recursive=True):
            if any(skip in fpath for skip in SKIP_DIRS):
                continue
            try:
                content = Path(fpath).read_text(errors='replace')
                lines = content.splitlines()
            except Exception:
                continue

            for i, line in enumerate(lines, 1):
                for p in CODE_PATTERNS:
                    if p['pattern'].search(line):
                        ctx_start = max(0, i - 5)
                        ctx_end = min(len(lines), i + 10)
                        context = '\n'.join(lines[ctx_start:ctx_end])
                        if p['check'](line, context):
                            findings.append({
                                'file': fpath,
                                'line': i,
                                'code': line.strip()[:120],
                                'name': p['name'],
                                'severity': p['severity'],
                                'message': p['message'],
                                'fix': p['fix'],
                            })

    return findings
```

---

## Step 3: Scan .env Files for Hardcoded Tokens

```python
import os
import re
from pathlib import Path

# JWT-like patterns (3 base64 parts) and API key patterns
JWT_PATTERN = re.compile(
    r'[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'
)

SHORT_LIVED_ENV_KEYS = re.compile(
    r'(jwt_secret|access_token|bearer_token|auth_token|api_key|private_key)',
    re.I
)

WEAK_SECRETS = ['secret', 'password', '123456', 'your-secret', 'changeme',
                'test', 'dev', 'development', 'supersecret', 'mysecret']


def scan_env_files(root: str = '.') -> list[dict]:
    """Scan .env files for hardcoded tokens and weak secrets."""
    findings = []

    env_files = []
    for pattern in ['.env', '.env.local', '.env.production', '.env.*']:
        env_files.extend(glob.glob(f'{root}/{pattern}'))

    for env_path in env_files:
        if not os.path.exists(env_path):
            continue
        # Skip .env.example files
        if 'example' in env_path.lower() or 'sample' in env_path.lower():
            continue

        try:
            lines = Path(env_path).read_text(errors='replace').splitlines()
        except Exception:
            continue

        for i, line in enumerate(lines, 1):
            if line.startswith('#') or '=' not in line:
                continue

            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"\'')

            # JWT token value in .env
            if JWT_PATTERN.match(value):
                findings.append({
                    'file': env_path,
                    'line': i,
                    'key': key,
                    'issue': 'JWT token hardcoded in .env file',
                    'severity': 'HIGH',
                    'fix': 'Generate dynamic tokens at runtime. Store only the signing secret, not a token.',
                })

            # Weak secret values
            if SHORT_LIVED_ENV_KEYS.search(key) and value.lower() in WEAK_SECRETS:
                findings.append({
                    'file': env_path,
                    'line': i,
                    'key': key,
                    'issue': f'Weak JWT secret: "{value}"',
                    'severity': 'CRITICAL',
                    'fix': (
                        'Generate a strong 256-bit secret:\n'
                        '  node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"\n'
                        '  python3 -c "import secrets; print(secrets.token_hex(32))"'
                    ),
                })

    return findings
```

---

## Step 4: Output Report

```markdown
## JWT & Auth Security Audit
Token analyzed: eyJhbGci... | Source scan: src/ | .env scan: .

---

### Token Analysis

**Decoded Header:**
```json
{ "alg": "HS256", "typ": "JWT" }
```

**Decoded Payload:**
```json
{
  "sub": "user_12345",
  "email": "alice@example.com",
  "role": "admin",
  "scope": "read:* write:* admin",
  "iat": 1710000000,
  "exp": 1741536000
}
```

---

### Token Findings

| # | Severity | Claim | Issue |
|---|----------|-------|-------|
| 1 | 🔴 HIGH | `scope` | Wildcard scopes `read:* write:* admin` — principle of least privilege violation |
| 2 | 🔴 HIGH | `exp` | Token expires in 365 days — too long-lived |
| 3 | 🟠 MEDIUM | `role` | `role:admin` in payload — if trusted without DB check, forgeable |
| 4 | 🟠 MEDIUM | `aud` | Missing audience claim |
| 5 | 🟡 MEDIUM | `alg` | HS256 — confirm server rejects RS256→HS256 confusion |

---

### Code Scan Findings (src/)

**🔴 CRITICAL — Bearer token logged**

`src/middleware/auth.ts:23`
```ts
logger.debug(`Auth header: ${req.headers.authorization}`)
```
This logs the full Bearer token to your logging system. Anyone with log access can steal tokens.

Fix:
```ts
logger.debug('Auth header present', { has_token: !!req.headers.authorization })
```

---

**🔴 CRITICAL — Hardcoded JWT secret**

`src/config/jwt.ts:5`
```ts
const JWT_SECRET = 'mysecret'
```
This secret is in version control. Anyone with repo access can forge JWTs for any user.

Fix:
```ts
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) throw new Error('JWT_SECRET env var required');
```

---

**🔴 HIGH — jwt.verify() without algorithms**

`src/auth/verify.ts:14`
```ts
const payload = jwt.verify(token, secret)
```
Vulnerable to alg:none bypass and algorithm confusion attack.

Fix:
```ts
const payload = jwt.verify(token, secret, { algorithms: ['HS256'] })
```

---

**🟠 HIGH — Token in localStorage**

`src/auth/login.ts:45`
```ts
localStorage.setItem('token', response.data.access_token)
```
Token in localStorage is readable by any JavaScript, including injected XSS payloads.

Fix:
```ts
// Server should set: Set-Cookie: token=X; HttpOnly; Secure; SameSite=Strict
// Client reads from cookie automatically — no JavaScript access needed
```

---

### .env Findings

`.env:3` — `JWT_SECRET=mysecret` — **CRITICAL: Weak secret**

Generate a strong replacement:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# → a7f3e2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1
```

---

### Summary

| Severity | Count | Must Fix Before Deploy |
|----------|-------|----------------------|
| 🔴 CRITICAL | 2 | YES — hardcoded secret, token logged |
| 🔴 HIGH | 4 | YES — alg check, localStorage, long-lived token |
| 🟠 MEDIUM | 3 | Recommended |

**Priority order:**
1. Rotate JWT_SECRET (it's in plaintext in the repo)
2. Fix jwt.verify() to include algorithms option
3. Move token storage from localStorage to httpOnly cookie
4. Reduce token scope and lifetime
```

---

## Quick Mode Output

```
JWT Audit: eyJhbGci... + src/ scan

Token:
🔴 No aud claim  🟠 role:admin in payload  🟠 expires in 365 days
🔴 Wildcard scopes: read:* write:* admin

Code (src/):
🔴 CRITICAL: JWT_SECRET hardcoded in jwt.ts:5
🔴 CRITICAL: Bearer token logged in auth.ts:23
🔴 HIGH: jwt.verify() without algorithms (alg:none bypass) in verify.ts:14
🟠 HIGH: Token in localStorage in login.ts:45

.env:
🔴 CRITICAL: JWT_SECRET=mysecret (weak secret)

Fix order: 1) Rotate secret 2) Add algorithms to verify() 3) Move to httpOnly cookie
```
