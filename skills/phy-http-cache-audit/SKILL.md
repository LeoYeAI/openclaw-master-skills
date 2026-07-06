---
name: phy-http-cache-audit
description: HTTP caching header analyzer that checks Cache-Control directives, ETag/Last-Modified freshness, Vary correctness, CDN cache status (X-Cache, CF-Cache-Status, Age), and stale-while-revalidate opportunities for any URL or local dev server. Identifies assets that should be cached but aren't, misconfigured max-age values, cache poisoning risks (dangerous Vary headers), and missing immutable flags on hashed static files. Supports nginx, Apache, Cloudflare, Fastly, and Next.js config generation. Zero external API — uses only curl. Triggers on "cache headers", "caching audit", "cache-control", "CDN cache miss", "no-cache no-store", "etag missing", "immutable assets", "/cache-audit".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - performance
    - http-caching
    - cache-control
    - cdn
    - web-performance
    - developer-tools
    - nginx
    - cloudflare
    - frontend
---

# HTTP Cache Audit

Your Lighthouse score says "Serve static assets with an efficient cache policy." You have `Cache-Control: no-store` on your 2MB vendor.js because you copied an API middleware header.

This skill fetches response headers for your URLs, classifies each resource's caching behavior, identifies what should be cached but isn't, and generates the exact config lines for nginx/Apache/Cloudflare/Next.js.

**Works against any URL via curl. Zero external API.**

---

## Trigger Phrases

- "cache headers", "caching audit", "cache issues"
- "cache-control check", "max-age wrong"
- "CDN cache miss", "cache hit rate"
- "ETag missing", "Last-Modified"
- "immutable assets", "static files not cached"
- "stale-while-revalidate"
- "/cache-audit"

---

## How to Provide Input

```bash
# Option 1: Audit a single URL
/cache-audit https://myapp.com/static/app.abc123.js

# Option 2: Audit multiple asset types for a site
/cache-audit https://myapp.com --scan-assets

# Option 3: Audit local dev server
/cache-audit http://localhost:3000/api/users

# Option 4: Check specific resource type
/cache-audit https://myapp.com/api/products  # Should be short-lived
/cache-audit https://myapp.com/logo.png      # Should be immutable

# Option 5: Generate config for missing cache headers
/cache-audit https://myapp.com --output nginx
/cache-audit https://myapp.com --output cloudflare

# Option 6: Audit all resources loaded by a page (via HAR analysis)
/cache-audit https://myapp.com --har-file network.har
```

---

## Step 1: Fetch and Parse Cache Headers

```python
import subprocess
import re
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CacheAnalysis:
    url: str
    resource_type: str          # js, css, image, font, api, html, other
    cache_control: Optional[str]
    etag: Optional[str]
    last_modified: Optional[str]
    vary: Optional[str]
    age: Optional[int]          # seconds since cached by CDN
    cdn_cache_hit: Optional[str] # HIT / MISS / EXPIRED / BYPASS
    expires: Optional[str]
    pragma: Optional[str]

    # Derived
    max_age: Optional[int] = None
    s_maxage: Optional[int] = None
    is_cacheable: bool = False
    has_validation: bool = False
    grade: str = 'F'            # A/B/C/F
    issues: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)


def fetch_response_headers(url: str) -> dict[str, str]:
    """Fetch HTTP response headers via curl."""
    result = subprocess.run(
        ['curl', '-sI', url, '--max-time', '10', '-L',
         '--user-agent', 'CacheAuditor/1.0',
         '-H', 'Accept-Encoding: gzip, deflate, br'],
        capture_output=True, text=True
    )
    headers = {}
    for line in result.stdout.splitlines():
        if ':' in line and not line.startswith('HTTP/'):
            key, _, value = line.partition(':')
            headers[key.strip().lower()] = value.strip()
    return headers


def detect_resource_type(url: str, content_type: str = '') -> str:
    """Classify resource type from URL path and Content-Type."""
    path = urlparse(url).path.lower()
    ct = content_type.lower()

    if re.search(r'\.(js|mjs|cjs)(\?|$)', path) or 'javascript' in ct:
        return 'js'
    if re.search(r'\.css(\?|$)', path) or 'text/css' in ct:
        return 'css'
    if re.search(r'\.(png|jpg|jpeg|gif|webp|avif|svg|ico)(\?|$)', path) or 'image/' in ct:
        return 'image'
    if re.search(r'\.(woff|woff2|ttf|otf|eot)(\?|$)', path) or 'font' in ct:
        return 'font'
    if re.search(r'\.(html|htm)(\?|$)', path) or 'text/html' in ct:
        return 'html'
    if '/api/' in path or 'json' in ct:
        return 'api'
    return 'other'


def parse_max_age(cc: str) -> Optional[int]:
    """Extract max-age value from Cache-Control header."""
    m = re.search(r'\bmax-age\s*=\s*(\d+)', cc, re.I)
    return int(m.group(1)) if m else None


def parse_s_maxage(cc: str) -> Optional[int]:
    """Extract s-maxage (CDN TTL) from Cache-Control header."""
    m = re.search(r'\bs-maxage\s*=\s*(\d+)', cc, re.I)
    return int(m.group(1)) if m else None


def parse_cdn_cache_status(headers: dict) -> Optional[str]:
    """Detect CDN cache hit/miss from vendor headers."""
    # Cloudflare
    if 'cf-cache-status' in headers:
        return headers['cf-cache-status'].upper()
    # Generic CDN (Fastly, Akamai, AWS CloudFront, Nginx proxy)
    if 'x-cache' in headers:
        val = headers['x-cache'].upper()
        if 'HIT' in val:
            return 'HIT'
        if 'MISS' in val:
            return 'MISS'
    # Nginx proxy_cache
    if 'x-proxy-cache' in headers:
        return headers['x-proxy-cache'].upper()
    return None
```

---

## Step 2: Classify Caching Behavior

```python
# Recommended cache durations by resource type
RECOMMENDED_MAX_AGE = {
    'js':     31536000,   # 1 year (must use content hash in filename)
    'css':    31536000,   # 1 year (content hash required)
    'image':  2592000,    # 30 days
    'font':   31536000,   # 1 year (fonts rarely change)
    'html':   0,          # no-cache (always revalidate)
    'api':    0,          # no-store or very short
    'other':  86400,      # 1 day default
}

# Hashed filename patterns — these should be immutable
HASH_PATTERN = re.compile(r'[._-][a-f0-9]{6,16}[._](js|css|woff2?|png|jpg)$', re.I)


def analyze_caching(url: str) -> CacheAnalysis:
    """Full cache analysis for a single URL."""
    headers = fetch_response_headers(url)
    cc = headers.get('cache-control', '')
    ct = headers.get('content-type', '')
    resource_type = detect_resource_type(url, ct)
    path = urlparse(url).path

    analysis = CacheAnalysis(
        url=url,
        resource_type=resource_type,
        cache_control=cc or None,
        etag=headers.get('etag'),
        last_modified=headers.get('last-modified'),
        vary=headers.get('vary'),
        age=int(headers['age']) if headers.get('age', '').isdigit() else None,
        cdn_cache_hit=parse_cdn_cache_status(headers),
        expires=headers.get('expires'),
        pragma=headers.get('pragma'),
    )

    if cc:
        analysis.max_age = parse_max_age(cc)
        analysis.s_maxage = parse_s_maxage(cc)

    analysis.has_validation = bool(analysis.etag or analysis.last_modified)

    # ── Check: no-store on cacheable resource ────────────────────────────────
    cc_lower = cc.lower()
    if 'no-store' in cc_lower and resource_type in ('js', 'css', 'image', 'font'):
        analysis.issues.append(
            f"no-store on {resource_type} asset — browser cannot cache, every request re-downloads"
        )
        rec_age = RECOMMENDED_MAX_AGE[resource_type]
        if HASH_PATTERN.search(path):
            analysis.fixes.append(
                f"Filename has content hash → safe to add: "
                f"Cache-Control: public, max-age={rec_age}, immutable"
            )
        else:
            analysis.fixes.append(
                f"Add content hash to filename, then: "
                f"Cache-Control: public, max-age={rec_age}, immutable"
            )

    # ── Check: no-cache without ETag/Last-Modified ───────────────────────────
    elif 'no-cache' in cc_lower and not analysis.has_validation:
        if resource_type not in ('api', 'html'):
            analysis.issues.append(
                "no-cache without ETag or Last-Modified — "
                "revalidation always results in full re-download (no 304)"
            )
            analysis.fixes.append("Add ETag generation or Last-Modified header to enable 304 responses")

    # ── Check: missing Cache-Control entirely ─────────────────────────────────
    elif not cc:
        if resource_type in ('js', 'css', 'image', 'font'):
            analysis.issues.append(
                f"No Cache-Control on {resource_type} — "
                f"browser applies heuristic caching (typically ~10% of Last-Modified age)"
            )
            rec_age = RECOMMENDED_MAX_AGE[resource_type]
            if HASH_PATTERN.search(path):
                analysis.fixes.append(
                    f"Cache-Control: public, max-age={rec_age}, immutable"
                )
            else:
                analysis.fixes.append(
                    f"Cache-Control: public, max-age={rec_age}"
                )

    # ── Check: max-age too short for hashed static assets ────────────────────
    elif analysis.max_age is not None:
        rec_age = RECOMMENDED_MAX_AGE.get(resource_type, 86400)
        if resource_type in ('js', 'css', 'font') and analysis.max_age < 86400:
            analysis.issues.append(
                f"max-age={analysis.max_age}s is very short for {resource_type} "
                f"(recommend {rec_age}s with content hash)"
            )
            if HASH_PATTERN.search(path):
                analysis.fixes.append(
                    f"Filename has content hash → increase to: "
                    f"max-age={rec_age}, immutable"
                )

    # ── Check: missing immutable on hashed assets ────────────────────────────
    if (HASH_PATTERN.search(path) and 'immutable' not in cc_lower
            and resource_type in ('js', 'css', 'font')):
        analysis.issues.append(
            "Filename has content hash but missing 'immutable' directive — "
            "browser may still revalidate during page load"
        )
        analysis.fixes.append("Add immutable: Cache-Control: public, max-age=31536000, immutable")

    # ── Check: Vary header risks ──────────────────────────────────────────────
    vary = (analysis.vary or '').lower()
    if 'user-agent' in vary:
        analysis.issues.append(
            "Vary: User-Agent — CDN creates separate cache entry per user agent string, "
            "effectively disabling CDN caching (thousands of variants)"
        )
        analysis.fixes.append("Remove User-Agent from Vary; use separate URL parameters or paths for device variants")
    if '*' in vary:
        analysis.issues.append("Vary: * — CDN cannot cache this resource at all")
        analysis.fixes.append("Replace Vary: * with specific header names")

    # ── Check: s-maxage missing on cacheable assets ──────────────────────────
    if resource_type in ('js', 'css', 'image') and analysis.max_age and not analysis.s_maxage:
        if analysis.cdn_cache_hit == 'MISS':
            analysis.issues.append(
                "CDN returning MISS — s-maxage not set, CDN may not be caching this resource"
            )
            analysis.fixes.append("Add s-maxage=31536000 to allow CDN caching independently of browser TTL")

    # ── Check: API endpoint with no-store missing ────────────────────────────
    if resource_type == 'api' and cc and 'no-store' not in cc_lower and 'private' not in cc_lower:
        analysis.issues.append(
            "API response missing no-store/private — may be cached by proxy/CDN with user data"
        )
        analysis.fixes.append(
            "Add: Cache-Control: no-store  OR  Cache-Control: private, no-cache"
        )

    # ── Assign grade ─────────────────────────────────────────────────────────
    if not analysis.issues:
        analysis.grade = 'A'
        analysis.is_cacheable = True
    elif len(analysis.issues) == 1:
        analysis.grade = 'B'
    elif len(analysis.issues) == 2:
        analysis.grade = 'C'
    else:
        analysis.grade = 'F'

    return analysis
```

---

## Step 3: Scan Multiple Assets

```bash
# Discover all assets loaded by a page using curl + grep
URL="https://myapp.com"

# Method 1: Scan common static asset paths
PATHS=(
  "/static/js/main.js"
  "/static/css/main.css"
  "/favicon.ico"
  "/logo.png"
  "/api/health"
  "/api/users"
)

for path in "${PATHS[@]}"; do
  echo "=== $URL$path ==="
  curl -sI "$URL$path" | grep -iE "cache-control|etag|last-modified|vary|cf-cache|x-cache|age"
  echo ""
done

# Method 2: From a saved HAR file (browser DevTools → Network → Save as HAR)
python3 -c "
import json, sys
har = json.load(open('network.har'))
urls = [e['request']['url'] for e in har['log']['entries']
        if e['response']['status'] == 200]
for url in urls[:50]:
    print(url)
"
```

---

## Step 4: Output Report

```markdown
## HTTP Cache Audit
Site: https://myapp.com | Resources checked: 23

---

### Summary

| Grade | Count | Examples |
|-------|-------|---------|
| 🔴 F (uncacheable/misconfigured) | 8 | vendor.abc123.js, app.def456.js |
| 🟠 C (partially correct) | 5 | logo.png, hero.webp |
| 🟡 B (minor issues) | 4 | fonts/inter.woff2 |
| ✅ A (correctly cached) | 6 | favicon.ico, og-image.png |

**Estimated cache performance impact: ~2.4MB re-downloaded on every page load**

---

### 🔴 Critical Issues

**vendor.abc123.js** — `Cache-Control: no-store`
- URL has content hash `abc123` → safe for long-term caching
- Every visitor re-downloads this 847KB file on every page load

**Fix:**
```nginx
location ~* \.[a-f0-9]{8,}\.(js|css)$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
    expires 1y;
}
```

---

**app.def456.js** — No Cache-Control header
- Heuristic caching applied (browser guesses ~2 hours based on Last-Modified)
- CDN returning MISS on every request

**Fix:** Same nginx location block above.

---

### 🟠 Suboptimal Caching

**logo.png** — `Cache-Control: max-age=3600, public`
- 1 hour TTL is very short for an infrequently-changing image
- This creates 24+ CDN misses per day per CDN edge node

**Fix:** `Cache-Control: public, max-age=2592000` (30 days)
Use filename versioning (`logo-v2.png`) if you need instant invalidation.

---

**fonts/inter.woff2** — `Cache-Control: public, max-age=604800`
- 7 days — fonts almost never change, should be 1 year
- Missing `immutable` directive

**Fix:** `Cache-Control: public, max-age=31536000, immutable`

---

### ⚠️ Vary Header Warning

**/api/users** — `Vary: User-Agent, Accept-Encoding`
- `User-Agent` in Vary creates thousands of cache variants in CDN
- Cloudflare/Fastly will not cache this endpoint effectively

**Fix:** Remove `User-Agent` from Vary: `Vary: Accept-Encoding`

---

### Generated nginx Config

```nginx
# Static assets with content hash — immutable 1 year
location ~* \.[a-f0-9]{6,16}\.(js|css|woff2?)(\?.*)?$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
    add_header Vary "Accept-Encoding";
    expires 1y;
}

# Images — 30 days
location ~* \.(png|jpg|jpeg|webp|avif|gif|svg|ico)$ {
    add_header Cache-Control "public, max-age=2592000";
    add_header Vary "Accept-Encoding";
    expires 30d;
}

# HTML — always revalidate
location ~* \.(html?)$ {
    add_header Cache-Control "no-cache";
}

# API — never cache
location /api/ {
    add_header Cache-Control "no-store";
}
```

**Verify:**
```bash
curl -sI https://myapp.com/static/js/vendor.abc123.js | grep -i cache
# Should return: cache-control: public, max-age=31536000, immutable
# Should return: cf-cache-status: HIT (after Cloudflare warms up)
```
```

---

## Quick Mode Output

```
Cache Audit: https://myapp.com (23 resources)

🔴 8 resources with no-store or no Cache-Control on hashed static files
   → ~2.4MB re-downloaded every page load
🟠 5 resources with max-age too short (< 1 week for static assets)
✅ 6 resources correctly configured

Top fix: Add `Cache-Control: public, max-age=31536000, immutable` to hashed JS/CSS
→ Estimated improvement: 2.4MB cached, ~600ms faster repeat visits

CDN status: 8 MISS, 6 HIT (Cloudflare)
Vary issues: /api/users has Vary: User-Agent (prevents CDN caching)
```
