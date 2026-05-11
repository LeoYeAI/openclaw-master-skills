# Phase 1: Pre-Visit Scan

## Purpose

Check URL before visiting or using for SSRF attacks and suspicious patterns.

## Activation

Execute this phase always when:
- Agent receives URL to visit
- Agent receives command with URL (curl, wget, fetch)
- Agent parses URL from user input

## Procedure

### Step 1: Extract domain/host from URL

```bash
# Example extraction
url="https://example.com/path/to/resource"
host=$(echo "$url" | sed -E 's|https?://([^/]+).*|\1|' | cut -d: -f1)
```

### Step 2: Check for SSRF patterns

Use `config/ssrf-blocklist.yaml` for checking:

| Pattern | Category | Action |
|---------|----------|---------|
| `169.254.169.254` | Cloud Metadata | **BLOCK** |
| `127.0.0.1` | Localhost | **BLOCK** |
| `localhost` | Localhost | **BLOCK** |
| `10.x.x.x` | Private Network | **BLOCK** |
| `172.16-31.x.x` | Private Network | **BLOCK** |
| `192.168.x.x` | Private Network | **BLOCK** |
| `metadata.google.internal` | Cloud Metadata | **BLOCK** |
| `metadata.azure.com` | Cloud Metadata | **BLOCK** |
| `0.0.0.0` | Any Address | **BLOCK** |

### Step 3: Check against blocklist

Load `config/ssrf-blocklist.yaml` and check host against list:

```yaml
# Blocked categories (action BLOCK):
- cloud_metadata: All known cloud metadata endpoints
- local_network: Private IP ranges
- internal_services: Local services (DB, admin panels)

# Warning categories (action WARN):
- suspicious_domains: URL shorteners, redirectors
- testing_tools: Local debugging ports
```

### Step 4: Make decision

| Result | Action | Message |
|--------|--------|---------|
| **BLOCK** | Reject URL immediately | "URL blocked: SSRF pattern detected (category: X)" |
| **WARN** | Show user | "Suspicious URL: domain matches pattern X. Continue?" |
| **ALLOW** | Continue normally | — |

## Flowchart

```
┌─────────────────┐
│  Received URL   │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Extract host    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Cloud Metadata? │───YES───► BLOCK
└────────┬────────┘
    NO
         ▼
┌─────────────────┐
│ Private Network?│───YES───► BLOCK
└────────┬────────┘
    NO
         ▼
┌─────────────────┐
│ Internal Serv?  │───YES───► BLOCK
└────────┬────────┘
    NO
         ▼
┌─────────────────┐
│ Suspicious Dom? │───YES───► WARN
└────────┬────────┘
    NO
         ▼
      ALLOW
```

## Examples

### Example 1: AWS Metadata SSRF
```
URL: http://169.254.169.254/latest/meta-data/
Host: 169.254.169.254
Category: cloud_metadata
Result: BLOCK
```

### Example 2: Localhost Admin Panel
```
URL: http://localhost:8080/admin
Host: localhost:8080
Category: internal_services
Result: BLOCK
```

### Example 3: Safe External URL
```
URL: https://api.github.com/users
Host: api.github.com
Category: safe
Result: ALLOW
```

### Example 4: URL Shortener
```
URL: https://bit.ly/abc123
Host: bit.ly
Category: suspicious_domains
Result: WARN (show to user)
```

## Tools

- IP check: `host <domain>` or `dig <domain>`
- URL check: `curl -I --connect-timeout 5 <url>` (only for safe URLs)
- Blocklist: `config/ssrf-blocklist.yaml`

## FAQ

**Q: What if URL contains IP instead of domain?**
A: Check IP directly against blocklist. IP in URL is a red flag.

**Q: How to handle URL with port?**
A: Extract both host and port. Check both against blocklist (e.g., localhost:8080).

**Q: What if URL is encoded?**
A: Decode URL before checking: `python3 -c "from urllib.parse import unquote; print(unquote('$url'))"`

**Q: Can I ignore WARN and continue?**
A: No - with WARN always show user and request confirmation.