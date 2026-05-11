---
name: phy-ssrf-audit
description: Server-Side Request Forgery (SSRF) vulnerability scanner (OWASP A10:2021). Detects URL-fetching sinks in Python/Java/Node.js/PHP/Go/Ruby that accept user-controlled URLs without validation. Flags cloud metadata endpoint access (AWS IMDS 169.254.169.254, GCP metadata.google.internal, Azure IMDS), DNS rebinding exposure, missing allowlist checks. Outputs CWE-918 findings with HTTP taint analysis and per-framework fix snippets. Zero competitors on ClawHub.
license: Apache-2.0
tags:
  - security
  - ssrf
  - owasp
  - cloud-security
  - python
  - java
  - nodejs
  - php
  - go
  - ruby
metadata:
  author: PHY041
  version: "1.0.0"
---

# phy-ssrf-audit

Static scanner for **OWASP A10:2021 — Server-Side Request Forgery (SSRF)** vulnerabilities. Finds all URL-fetching sinks in your codebase, traces HTTP input to those sinks, and checks for missing allowlist/blocklist guards. Flags hardcoded cloud metadata endpoint access as CRITICAL. Zero external API calls, zero dependencies beyond Python 3 stdlib.

## Why SSRF Matters in 2026

SSRF lets attackers force your server to fetch internal URLs, bypassing firewalls and reaching:
- **AWS IMDS** (`169.254.169.254`) → steal IAM credentials, account ID, region
- **GCP metadata** (`metadata.google.internal`) → steal service account tokens
- **Azure IMDS** (`169.254.169.254/metadata/instance`) → steal managed identity tokens
- **Internal services** → Redis, Elasticsearch, Kubernetes API without auth
- **Private network scanning** → map internal topology via timing side-channels

Real-world examples: Capital One breach (2019), GitLab SSRF (CVE-2021-22214), Confluence SSRF (CVE-2022-26134 adjacent).

## What It Detects

### Python
| Sink | Severity | Notes |
|------|----------|-------|
| `requests.get/post/put/delete/head(user_url)` | HIGH | Most common SSRF vector |
| `urllib.request.urlopen(user_url)` | HIGH | stdlib fetch |
| `httpx.get/post(user_url)` | HIGH | async-first HTTP client |
| `aiohttp.ClientSession().get(user_url)` | HIGH | async |
| `socket.create_connection((user_host, port))` | HIGH | raw socket SSRF |
| `subprocess.*("curl", user_url)` | CRITICAL | SSRF + command injection |
| `open(user_url)` where URL is http:// | HIGH | Python 2 urllib alias |

### Java
| Sink | Severity | Notes |
|------|----------|-------|
| `new URL(userInput).openConnection()` | CRITICAL | Direct Java SSRF |
| `new URL(userInput).openStream()` | CRITICAL | Direct Java SSRF |
| `RestTemplate.getForObject(userInput, ...)` | HIGH | Spring REST |
| `RestTemplate.exchange(userInput, ...)` | HIGH | Spring REST |
| `WebClient.get().uri(userInput)` | HIGH | Spring WebFlux |
| `HttpClient.newHttpClient().send(HttpRequest.newBuilder(URI.create(userInput)))` | CRITICAL | Java 11+ HTTP client |
| `OkHttpClient().newCall(Request.Builder().url(userInput))` | HIGH | OkHttp |

### Node.js / TypeScript
| Sink | Severity | Notes |
|------|----------|-------|
| `http.get(req.*.url)` / `https.get(req.*.url)` | HIGH | Node.js stdlib |
| `fetch(req.*.url)` / `fetch(req.*.target)` | HIGH | Fetch API |
| `axios.get(req.*.url)` / `axios.post(req.*.url)` | HIGH | Axios |
| `got(req.*.url)` / `got.get(req.*.url)` | HIGH | got client |
| `node-fetch(req.*.url)` | HIGH | node-fetch |
| `superagent.get(req.*.url)` | HIGH | SuperAgent |
| `needle.get(req.*.url)` | HIGH | Needle |
| `request(req.*.url, ...)` | HIGH | request (deprecated) |

### PHP
| Sink | Severity | Notes |
|------|----------|-------|
| `curl_setopt($ch, CURLOPT_URL, $_GET[...])` | CRITICAL | Direct SSRF |
| `file_get_contents($_GET[...])` | CRITICAL | PHP wrapper SSRF + LFI |
| `file_get_contents($_POST[...])` | CRITICAL | |
| `curl_setopt($ch, CURLOPT_URL, $url)` where `$url` from request | HIGH | Indirect |
| `fopen($_GET[...], 'r')` | HIGH | Remote file open |

### Go
| Sink | Severity | Notes |
|------|----------|-------|
| `http.Get(r.FormValue("url"))` | CRITICAL | Direct SSRF |
| `http.Get(r.URL.Query().Get("url"))` | CRITICAL | Direct SSRF |
| `http.NewRequest("GET", userURL, nil)` | HIGH | |
| `http.Client{}.Do(req)` where URL is user-controlled | HIGH | |
| `http.Post(userURL, ...)` | HIGH | |

### Ruby
| Sink | Severity | Notes |
|------|----------|-------|
| `Net::HTTP.get(URI(params[:url]))` | CRITICAL | Direct SSRF |
| `URI.open(params[:url])` / `open(params[:url])` | CRITICAL | Also code execution risk |
| `HTTP.get(params[:url])` | HIGH | http gem |
| `Faraday.new(params[:url])` | HIGH | Faraday |
| `RestClient.get(params[:url])` | HIGH | rest-client |
| `HTTParty.get(params[:url])` | HIGH | HTTParty |

## Cloud Metadata Endpoint Patterns (CRITICAL)

Regardless of HTTP input taint, flag any hardcoded or constructed URL containing:

| Endpoint | Cloud Provider | Risk |
|---------|----------------|------|
| `169.254.169.254` | AWS/GCP/Azure/Alibaba | IAM credentials, instance metadata |
| `metadata.google.internal` | GCP | Service account tokens |
| `169.254.170.2` | AWS ECS | Task metadata + credentials |
| `fd00:ec2::254` | AWS IPv6 IMDS | IPv6 IMDSv2 |
| `100.100.100.200` | Alibaba Cloud IMDS | RAM credentials |
| `169.254.169.254/metadata/instance` | Azure IMDS | Managed identity tokens |
| `169.254.0.1` | Oracle Cloud IMDS | Instance credentials |
| `kubernetes.default.svc` | Kubernetes | API server auth bypass |
| `etcd.kube-system.svc` | Kubernetes | etcd direct access |

**Note:** Even legitimate server-side proxy features must validate against a metadata blocklist. No exceptions.

## Missing Guard Detection

After finding a sink, the scanner checks if a validation guard exists within ±50 lines:

**Python guards (safe if present):**
```python
# Allowlist check
if urlparse(url).netloc not in ALLOWED_HOSTS:
    raise ValueError("blocked")

# Private IP check (requests-ssrf / ssrf-filter libraries)
import ssrf_filter
ssrf_filter.validate_url(url)

# ipaddress check
addr = socket.gethostbyname(host)
if ipaddress.ip_address(addr).is_private:
    raise ValueError("blocked")
```

**Node.js guards (safe if present):**
```javascript
// URL allowlist
const { hostname } = new URL(url);
if (!ALLOWED_HOSTS.includes(hostname)) throw new Error("blocked");

// ssrf-req-filter / ssrf-check libraries
import ssrfCheck from 'ssrf-req-filter';
await ssrfCheck(url);
```

**Go guards (safe if present):**
```go
// IP range check
ip := net.ParseIP(host)
if ip.IsLoopback() || ip.IsPrivate() { ... }

// Allowlist
if !slices.Contains(allowedHosts, parsedURL.Host) { ... }
```

## Implementation

```python
#!/usr/bin/env python3
"""
phy-ssrf-audit — OWASP A10:2021 SSRF scanner
Usage: python3 audit_ssrf.py [path] [--json] [--ci]
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

CRITICAL, HIGH, MEDIUM, INFO = "CRITICAL", "HIGH", "MEDIUM", "INFO"

CLOUD_METADATA_RE = re.compile(
    r'169\.254\.169\.254|'
    r'metadata\.google\.internal|'
    r'169\.254\.170\.2|'
    r'fd00:ec2::254|'
    r'100\.100\.100\.200|'
    r'kubernetes\.default\.svc|'
    r'etcd\.kube-system\.svc|'
    r'169\.254\.0\.1'
)

@dataclass
class Finding:
    file: str
    line: int
    pattern_name: str
    matched_text: str
    severity: str
    description: str
    fix: str
    has_http_taint: bool = False
    is_metadata_endpoint: bool = False
    guard_detected: bool = False

# ─── Pattern registry ────────────────────────────────────────────────────────
PATTERNS = {
    ".py": [
        ("REQUESTS_FETCH",
         re.compile(r'\brequests\.(get|post|put|delete|head|patch|request)\s*\('),
         HIGH,
         "requests.{method}() with user-controlled URL enables SSRF.",
         "Validate URL against an allowlist of permitted hosts before fetching. "
         "Use ssrf-filter or validate urlparse(url).netloc against ALLOWED_HOSTS."),

        ("URLLIB_URLOPEN",
         re.compile(r'\burllib\.request\.urlopen\s*\(|\burllib2\.urlopen\s*\('),
         HIGH,
         "urllib.request.urlopen() with user-controlled URL enables SSRF.",
         "Validate URL hostname and IP against an allowlist. Block private/loopback IPs."),

        ("HTTPX_FETCH",
         re.compile(r'\bhttpx\.(get|post|put|delete|request|stream)\s*\('),
         HIGH,
         "httpx.{method}() with user-controlled URL enables SSRF.",
         "Validate URL with httpx.URL(url).host against an allowlist before fetching."),

        ("AIOHTTP_FETCH",
         re.compile(r'aiohttp\.ClientSession\s*\(\s*\)'),
         HIGH,
         "aiohttp.ClientSession() — verify URL is validated before any .get()/.post() calls.",
         "Use a custom connector with allowed_hosts or validate URL before request."),

        ("SOCKET_CONNECT",
         re.compile(r'\bsocket\.create_connection\s*\('),
         HIGH,
         "socket.create_connection() with user-controlled host/port enables raw-socket SSRF.",
         "Resolve hostname to IP, check ip.is_private / ip.is_loopback before connecting."),

        ("SUBPROCESS_CURL",
         re.compile(r'\bsubprocess\.(run|call|check_output|Popen)\s*\([^)]*curl\b'),
         CRITICAL,
         "subprocess curl with user-controlled URL: SSRF + command injection risk.",
         "Never shell-out to curl with user input. Use requests library with URL validation."),
    ],
    ".java": [
        ("URL_OPEN_CONNECTION",
         re.compile(r'\bnew\s+URL\s*\([^)]+\)\.openConnection\s*\('),
         CRITICAL,
         "java.net.URL.openConnection() with user input is a classic Java SSRF vector.",
         "Validate URL host against an allowlist before opening connection. "
         "Use an HttpClient configured with a custom HostnameVerifier that blocks private IPs."),

        ("URL_OPEN_STREAM",
         re.compile(r'\bnew\s+URL\s*\([^)]+\)\.openStream\s*\('),
         CRITICAL,
         "URL.openStream() with user input enables SSRF.",
         "Same mitigation as openConnection() — allowlist host validation required."),

        ("REST_TEMPLATE_EXCHANGE",
         re.compile(r'\brestTemplate\.(getForObject|exchange|postForObject|getForEntity)\s*\('),
         HIGH,
         "Spring RestTemplate with user-controlled URI enables SSRF.",
         "Create a UriComponentsBuilder and validate host before passing to RestTemplate."),

        ("WEBCLIENT_URI",
         re.compile(r'WebClient\.(?:create|builder)\s*\([^)]*\)'),
         HIGH,
         "Spring WebClient with user-controlled URI enables SSRF.",
         "Use .filter() with an ExchangeFilterFunction that validates the request URI host."),

        ("JAVA_HTTP_CLIENT",
         re.compile(r'HttpRequest\.newBuilder\s*\(\s*URI\.create\s*\('),
         CRITICAL,
         "Java 11 HttpClient with user-controlled URI enables SSRF.",
         "Validate URI host against allowlist before building request."),
    ],
    ".js": _build_js_ssrf_patterns(),
    ".ts": _build_js_ssrf_patterns(),
    ".php": [
        ("CURL_SETOPT_URL",
         re.compile(r'\bcurl_setopt\s*\([^,]+,\s*CURLOPT_URL\s*,\s*\$(?:_GET|_POST|_REQUEST|_COOKIE)\b'),
         CRITICAL,
         "curl_setopt CURLOPT_URL with $_GET/$_POST input is a direct SSRF vector.",
         "Validate URL hostname against allowlist. Block private IP ranges (RFC 1918). "
         "Set CURLOPT_FOLLOWLOCATION=0 or validate redirect URLs."),

        ("FILE_GET_CONTENTS_INPUT",
         re.compile(r'\bfile_get_contents\s*\(\s*\$(?:_GET|_POST|_REQUEST|_COOKIE)\b'),
         CRITICAL,
         "file_get_contents() with HTTP input URL: SSRF + potential LFI via php:// wrappers.",
         "Never pass user input to file_get_contents for URLs. "
         "Validate against allowlist; disable PHP wrappers with allow_url_fopen=0 in php.ini."),

        ("CURL_SETOPT_VAR",
         re.compile(r'\bcurl_setopt\s*\([^,]+,\s*CURLOPT_URL\s*,'),
         HIGH,
         "curl_setopt CURLOPT_URL — verify URL variable is not user-controlled.",
         "Trace URL origin; validate against allowlist before setting CURLOPT_URL."),
    ],
    ".go": [
        ("HTTP_GET_FORM",
         re.compile(r'\bhttp\.Get\s*\(\s*r\.(FormValue|URL\.Query\(\)\.Get|Form\.Get)\s*\('),
         CRITICAL,
         "http.Get() with form/query value is a direct Go SSRF vector.",
         "Parse URL with url.Parse(), resolve to IP, check net.IP.IsPrivate()/IsLoopback() "
         "before making the request."),

        ("HTTP_NEW_REQUEST",
         re.compile(r'\bhttp\.NewRequest\s*\(\s*"(?:GET|POST|PUT|DELETE)"\s*,'),
         HIGH,
         "http.NewRequest() — verify URL is not user-controlled.",
         "Validate URL hostname; use net.DefaultResolver to resolve and check IP ranges."),

        ("HTTP_CLIENT_DO",
         re.compile(r'\bhttp\.(?:DefaultClient|Client\s*\{[^}]*\})\.Do\s*\('),
         HIGH,
         "http.Client.Do() — verify request URL is not user-controlled.",
         "Implement a custom http.RoundTripper that validates the request URL before forwarding."),
    ],
    ".rb": [
        ("NET_HTTP_GET",
         re.compile(r'\bNet::HTTP\.(?:get|get_response|start)\s*\(\s*URI\s*\('),
         CRITICAL,
         "Net::HTTP with user-controlled URI is a direct Ruby SSRF vector.",
         "Validate URI.host against allowlist; resolve IP and check private ranges."),

        ("OPEN_URL",
         re.compile(r'\b(?:URI|Kernel)?\.?open\s*\(\s*params\['),
         CRITICAL,
         "Kernel#open() with params input: SSRF + code execution risk (if net/http is required).",
         "Use Net::HTTP explicitly (not open()) and validate URL against an allowlist."),

        ("HTTPARTY_GET",
         re.compile(r'\bHTTParty\.(get|post|put|delete)\s*\('),
         HIGH,
         "HTTParty request — verify URL is not user-controlled.",
         "Validate URL before passing to HTTParty. Consider a before_connection_make hook."),

        ("FARADAY_NEW",
         re.compile(r'\bFaraday\.new\s*\('),
         HIGH,
         "Faraday connection — verify base URL is not user-controlled.",
         "Allowlist permitted base URLs; never construct from user input."),
    ],
}

def _build_js_ssrf_patterns():
    return [
        ("FETCH_USER_URL",
         re.compile(r'\bfetch\s*\(\s*req\.[a-zA-Z.[\]'"]+'),
         CRITICAL,
         "fetch() with request parameter URL is a direct SSRF vector.",
         "Validate URL with new URL(userUrl).hostname against allowlist. "
         "Block private IP ranges (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x)."),

        ("AXIOS_USER_URL",
         re.compile(r'\baxios\.(get|post|put|delete|request)\s*\(\s*req\.[a-zA-Z.[\]'"]+'),
         CRITICAL,
         "axios with request parameter URL is a direct SSRF vector.",
         "Validate hostname before axios call. Use axios-ssrf-plugin for automatic blocking."),

        ("HTTP_GET_USER_URL",
         re.compile(r'\bhttps?\.(?:get|request)\s*\(\s*(?:req\.|url|target)[a-zA-Z.[\]'"]*'),
         HIGH,
         "Node.js http/https with user-controlled URL enables SSRF.",
         "Resolve hostname to IP with dns.lookup(), check against private ranges, then request."),

        ("GOT_USER_URL",
         re.compile(r'\bgot\s*\(\s*req\.[a-zA-Z.[\]'"]+|\bgot\.(get|post|put)\s*\(\s*req\.'),
         HIGH,
         "got() with request URL enables SSRF.",
         "Use got's beforeRequest hook to validate URL.hostname against allowlist."),

        ("REQUEST_USER_URL",
         re.compile(r'\brequest\s*\(\s*\{[^}]*url\s*:\s*req\.[^}]+\}'),
         HIGH,
         "request() library with user URL enables SSRF.",
         "Validate URL.hostname before constructing options object."),
    ]

# HTTP input markers (taint source detection)
HTTP_MARKERS = {
    ".py":   re.compile(r'request\.(body|data|json|args|form|GET|POST|files|params)|'
                        r'flask\.request|tornado|fastapi|starlette|aiohttp\.web\.Request'),
    ".java": re.compile(r'HttpServletRequest|@RequestBody|@RequestParam|@PathVariable|'
                        r'getParameter\(|getInputStream\(|@RequestMapping|@GetMapping|@PostMapping'),
    ".php":  re.compile(r'\$_(?:GET|POST|REQUEST|COOKIE|SERVER)|php://input'),
    ".rb":   re.compile(r'\bparams\[|request\.(body|params|query_string)|action_controller'),
    ".js":   re.compile(r'\breq\.(body|params|query|headers)|request\.(body|params)|ctx\.(query|body|params)'),
    ".ts":   re.compile(r'\breq\.(body|params|query|headers)|request\.(body|params)|ctx\.(query|body|params)'),
    ".go":   re.compile(r'r\.(Body|FormValue\(|URL\.Query\(\)|Header\.Get\(|Form\[)'),
}

# SSRF guard patterns — if present near sink, reduce severity
GUARD_PATTERNS = {
    ".py":   re.compile(r'allowlist|allowed_hosts|ALLOWED_HOSTS|is_private|is_loopback|'
                        r'ssrf.filter|ssrf_filter|ipaddress|urlparse.*netloc'),
    ".java": re.compile(r'allowedHosts|isPrivate|isLoopback|isLinkLocal|'
                        r'getAllowedHosts|validateUrl|hostnameVerifier'),
    ".php":  re.compile(r'allowedHosts|filter_var.*FILTER_VALIDATE_URL|CURLOPT_FOLLOWLOCATION.*0'),
    ".rb":   re.compile(r'allowed_hosts|private_address_check|ssrf'),
    ".js":   re.compile(r'ssrf|allowedHosts|ALLOWED_HOSTS|is_private|isPrivate|'
                        r'net\.isIP|dns\.lookup'),
    ".ts":   re.compile(r'ssrf|allowedHosts|ALLOWED_HOSTS|isPrivate|dns\.lookup'),
    ".go":   re.compile(r'IsPrivate\(\)|IsLoopback\(\)|IsLinkLocalUnicast\(\)|'
                        r'allowedHosts|allowList'),
}

SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".venv", "venv",
             "dist", "build", "target", ".gradle", ".mvn", "test", "tests",
             "__tests__", "spec", "fixtures"}

SEV_ORDER = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, INFO: 3}
ICONS = {CRITICAL: "🔴", HIGH: "🟠", MEDIUM: "🟡", INFO: "⚪"}

def scan_file(filepath: Path) -> list[Finding]:
    suffix = filepath.suffix.lower()
    if suffix not in PATTERNS:
        return []
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, PermissionError):
        return []

    full_text = "\n".join(lines)
    findings: list[Finding] = []
    http_marker = HTTP_MARKERS.get(suffix)
    guard_pat = GUARD_PATTERNS.get(suffix)

    for (name, pat, base_sev, desc, fix) in PATTERNS[suffix]:
        for m in pat.finditer(full_text):
            lineno = full_text[:m.start()].count("\n") + 1
            line_text = lines[lineno - 1]

            # Check for cloud metadata endpoint in this line
            is_metadata = bool(CLOUD_METADATA_RE.search(line_text))
            actual_sev = CRITICAL if is_metadata else base_sev

            # Check HTTP taint in ±40 lines
            start = max(0, lineno - 40)
            end = min(len(lines), lineno + 40)
            context = "\n".join(lines[start:end])
            has_http = bool(http_marker and http_marker.search(context))

            # Check for guard in ±50 lines
            guard_start = max(0, lineno - 50)
            guard_end = min(len(lines), lineno + 50)
            guard_context = "\n".join(lines[guard_start:guard_end])
            guard_found = bool(guard_pat and guard_pat.search(guard_context))

            # Downgrade if no HTTP taint and not metadata
            if not has_http and not is_metadata:
                if actual_sev == CRITICAL:
                    actual_sev = HIGH
                elif actual_sev == HIGH:
                    actual_sev = MEDIUM

            # Skip if guard present and not metadata endpoint
            if guard_found and not is_metadata:
                continue

            findings.append(Finding(
                file=str(filepath),
                line=lineno,
                pattern_name=name,
                matched_text=line_text.strip()[:120],
                severity=actual_sev,
                description=desc,
                fix=fix,
                has_http_taint=has_http,
                is_metadata_endpoint=is_metadata,
                guard_detected=guard_found,
            ))

    # Scan all lines for cloud metadata endpoint mentions (regardless of pattern)
    for i, line in enumerate(lines, 1):
        if CLOUD_METADATA_RE.search(line) and "CLOUD_METADATA" not in line:
            if not any(f.line == i and f.is_metadata_endpoint for f in findings):
                findings.append(Finding(
                    file=str(filepath),
                    line=i,
                    pattern_name="CLOUD_METADATA_ENDPOINT",
                    matched_text=line.strip()[:120],
                    severity=CRITICAL,
                    description="Hardcoded cloud metadata endpoint — confirms server-side HTTP access to IMDS.",
                    fix="Block all private IP ranges including 169.254.0.0/16 in your HTTP client configuration.",
                    has_http_taint=True,
                    is_metadata_endpoint=True,
                ))

    return findings

def walk_files(root: Path) -> list[Path]:
    exts = {".py", ".java", ".php", ".rb", ".js", ".ts", ".go"}
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if Path(fname).suffix.lower() in exts:
                results.append(Path(dirpath) / fname)
    return results

def format_report(findings: list[Finding], scanned: int) -> str:
    by_sev = {CRITICAL: [], HIGH: [], MEDIUM: [], INFO: []}
    for f in findings:
        by_sev[f.severity].append(f)

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "  SSRF AUDIT REPORT (OWASP A10:2021 — CWE-918)",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  Scanned:  {scanned} files",
        f"  Findings: {len(by_sev[CRITICAL])} CRITICAL  {len(by_sev[HIGH])} HIGH  {len(by_sev[MEDIUM])} MEDIUM",
        "",
    ]

    for sev in [CRITICAL, HIGH, MEDIUM]:
        group = by_sev[sev]
        if not group:
            continue
        lines.append(f"{ICONS[sev]} {sev} ({len(group)} findings)")
        lines.append("")
        for f in sorted(group, key=lambda x: x.file):
            rel = os.path.relpath(f.file)
            markers = []
            if f.is_metadata_endpoint:
                markers.append("☁️  CLOUD METADATA ENDPOINT")
            if f.has_http_taint:
                markers.append("⚡ HTTP taint confirmed")
            else:
                markers.append("⚠️  HTTP taint unconfirmed — verify source")
            lines += [
                f"  {rel}:{f.line} — {f.pattern_name}",
                f"  Code:  {f.matched_text}",
                f"  {'  '.join(markers)}",
                f"  Risk:  {f.description}",
                f"  CWE-918 (SSRF)",
                f"  Fix:   {f.fix}",
                "",
            ]

    critical_count = len(by_sev[CRITICAL])
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  CI gate: {'exit 1 — CRITICAL SSRF findings present' if critical_count else 'exit 0 — clean'}",
        "  OWASP: https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="OWASP A10:2021 SSRF scanner")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--ci", action="store_true", help="Exit 1 if CRITICAL found")
    args = parser.parse_args()

    files = walk_files(Path(args.path).resolve())
    all_findings: list[Finding] = []
    for f in files:
        all_findings.extend(scan_file(f))
    all_findings.sort(key=lambda x: (SEV_ORDER[x.severity], x.file, x.line))

    if args.json:
        import dataclasses
        print(json.dumps([dataclasses.asdict(f) for f in all_findings], indent=2))
    else:
        print(format_report(all_findings, len(files)))

    if args.ci:
        sys.exit(1 if any(f.severity == CRITICAL for f in all_findings) else 0)

if __name__ == "__main__":
    main()
```

## Usage

**Scan current project:**
```bash
python3 audit_ssrf.py
```

**Scan with CI fail-gate:**
```bash
python3 audit_ssrf.py --ci
```

**JSON output for SIEM/ticketing integration:**
```bash
python3 audit_ssrf.py --json | jq '[.[] | select(.severity == "CRITICAL")]'
```

**GitHub Actions:**
```yaml
- name: SSRF Audit
  run: python3 .claude/skills/phy-ssrf-audit/audit_ssrf.py --ci
```

## Sample Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SSRF AUDIT REPORT (OWASP A10:2021 — CWE-918)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scanned:  62 files
  Findings: 3 CRITICAL  2 HIGH  0 MEDIUM

🔴 CRITICAL (3 findings)

  api/proxy.py:78 — REQUESTS_FETCH
  Code:  data = requests.get(request.args.get('url')).json()
  ⚡ HTTP taint confirmed
  Risk:  requests.get() with user-controlled URL enables SSRF.
  CWE-918 (SSRF)
  Fix:   Validate URL against allowlist. Block private IPs (10.x, 172.16-31.x, 192.168.x, 169.254.x).

  functions/fetch.py:34 — CLOUD_METADATA_ENDPOINT
  Code:  resp = requests.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/")
  ☁️  CLOUD METADATA ENDPOINT  ⚡ HTTP taint confirmed
  Risk:  Hardcoded cloud metadata endpoint — confirms server-side HTTP access to IMDS.
  CWE-918 (SSRF)
  Fix:   Block all private IP ranges including 169.254.0.0/16 in your HTTP client configuration.

  src/WebhookController.java:112 — URL_OPEN_CONNECTION
  Code:  conn = (HttpURLConnection) new URL(webhookUrl).openConnection();
  ⚡ HTTP taint confirmed
  Risk:  java.net.URL.openConnection() with user input is a classic Java SSRF vector.
  CWE-918 (SSRF)
  Fix:   Validate URL host against allowlist. Use ValidatingObjectInputStream or custom HostnameVerifier.

🟠 HIGH (2 findings)

  routes/api.js:45 — FETCH_USER_URL
  Code:  const result = await fetch(req.query.target);
  ⚡ HTTP taint confirmed
  Risk:  fetch() with request parameter URL is a direct SSRF vector.
  CWE-918 (SSRF)
  Fix:   Validate URL hostname against allowlist. Block private IP ranges.

  internal/importer.go:89 — HTTP_NEW_REQUEST
  Code:  req, _ := http.NewRequest("GET", sourceURL, nil)
  ⚠️  HTTP taint unconfirmed — verify source
  Risk:  http.NewRequest() — verify URL is not user-controlled.
  CWE-918 (SSRF)
  Fix:   Validate URL hostname; use net.DefaultResolver to resolve and check IP ranges.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CI gate: exit 1 — CRITICAL SSRF findings present
  OWASP: https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_(SSRF)/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Defense-in-Depth Recommendations

### Immediate (per finding)
1. **Allowlist** — only permit fetches to known, necessary external hosts
2. **IP blocklist** — block RFC 1918 (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), loopback (127.0.0.0/8), link-local (169.254.0.0/16), and ::1
3. **DNS resolution validation** — resolve hostname → IP, then check IP against blocklist (prevents DNS rebinding)
4. **Disable redirects** — or re-validate the redirect URL against allowlist

### Architecture
- **Dedicated egress proxy** — route all outbound HTTP through a proxy that enforces allowlist
- **AWS IMDSv2** — enforce token-based IMDS access (IMDSv2) to limit SSRF impact
- **Network segmentation** — block EC2 metadata endpoint from application subnets where not needed

## Companion Skills

| Skill | Use Together For |
|-------|-----------------|
| `phy-deserialization-audit` | Full input-handling security sweep (OWASP A08 + A10) |
| `phy-cors-audit` | Network boundary + origin security |
| `phy-jwt-auth-audit` | What attackers can do after SSRF + credential theft |
| `phy-security-headers` | Defense-in-depth headers that limit SSRF blast radius |
