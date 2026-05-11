---
name: dnsrobot
description: "Run DNS, email security, SSL, WHOIS, and network tools via dnsrobot.net API — no API key required"
version: 1.0.0
metadata.openclaw.requires.bins: [curl]
emoji: 🌐
homepage: https://dnsrobot.net
---

# DNS Robot — DNS & Network Tools

[DNS Robot](https://dnsrobot.net) provides 53 free online DNS, domain, email security, and network tools. This skill gives you access to 19 API endpoints — no API key, no rate limits, no signup.

**Base URL**: `https://dnsrobot.net`

All endpoints accept and return JSON. Domains are auto-cleaned (strips `http://`, `https://`, `www.`, trailing paths).

---

## DNS Tools

### dns_lookup

Look up DNS records for any domain using a specific DNS server.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name (e.g. `example.com`) |
| `recordType` | string | yes | `A`, `AAAA`, `CNAME`, `MX`, `NS`, `TXT`, `SOA`, `PTR`, `SRV`, `CAA`, `DNSKEY`, or `DS` |
| `dnsServer` | string | yes | DNS server IPv4 (e.g. `8.8.8.8`) |
| `timeout` | number | no | Timeout in ms (1000–10000, default 5000) |

```bash
curl -s -X POST https://dnsrobot.net/api/dns-query \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com","recordType":"A","dnsServer":"8.8.8.8"}'
```

Response:
```json
{
  "status": "success",
  "domain": "example.com",
  "recordType": "A",
  "dnsServer": "8.8.8.8",
  "responseTime": 42,
  "resolvedIPs": ["93.184.216.34"]
}
```

**When to use**: Check how a domain resolves from a specific DNS server. Useful for DNS propagation debugging, verifying records, or comparing responses across providers.

---

### ns_lookup

Find all authoritative nameservers for a domain, including their IPs and providers.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |
| `dnsServer` | string | no | DNS server ID |

```bash
curl -s -X POST https://dnsrobot.net/api/ns-lookup \
  -H "Content-Type: application/json" \
  -d '{"domain":"github.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "github.com",
  "summary": {
    "totalNameservers": 8,
    "primaryProvider": "DNS Made Easy",
    "allProviders": ["DNS Made Easy"],
    "averageResponseTime": 15
  },
  "nameservers": [
    {
      "nameserver": "dns1.p08.nsone.net",
      "ipAddresses": ["198.51.44.8"],
      "responseTime": 12,
      "provider": "DNS Made Easy"
    }
  ]
}
```

**When to use**: Identify who hosts a domain's DNS, check nameserver redundancy, or debug delegation issues.

---

### mx_lookup

Find mail exchange (MX) records and identify the email provider.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |
| `dnsServer` | string | no | DNS server ID |

```bash
curl -s -X POST https://dnsrobot.net/api/mx-lookup \
  -H "Content-Type: application/json" \
  -d '{"domain":"google.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "google.com",
  "summary": {
    "totalRecords": 5,
    "primaryProvider": "Gmail",
    "allProviders": ["Gmail"],
    "lowestPriority": 10
  },
  "mxRecords": [
    {
      "exchange": "smtp.google.com",
      "priority": 10,
      "ipAddresses": ["142.250.152.26"],
      "provider": "Gmail"
    }
  ]
}
```

**When to use**: Find which email provider a domain uses, verify MX record configuration, or troubleshoot email delivery.

---

### cname_lookup

Trace the full CNAME chain for a domain, detecting circular references.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |
| `dnsServer` | string | no | DNS server ID |

```bash
curl -s -X POST https://dnsrobot.net/api/cname-lookup \
  -H "Content-Type: application/json" \
  -d '{"domain":"www.github.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "www.github.com",
  "hasCNAME": true,
  "summary": {
    "chainLength": 1,
    "hasCircularReference": false,
    "finalHostname": "github.github.io",
    "message": "CNAME chain resolved successfully"
  },
  "chain": [
    { "hostname": "www.github.com", "target": "github.github.io", "isCircular": false, "depth": 1 }
  ],
  "finalDestination": {
    "hostname": "github.github.io",
    "ipv4": ["185.199.108.153"],
    "ipv6": []
  }
}
```

**When to use**: Debug CDN or load balancer configurations, find the actual server behind a CNAME, or detect circular references.

---

### reverse_dns

Perform a reverse DNS (PTR) lookup on an IP address.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ip` | string | yes | IPv4 or IPv6 address |
| `dnsServer` | string | no | DNS server ID |

```bash
curl -s -X POST https://dnsrobot.net/api/reverse-dns \
  -H "Content-Type: application/json" \
  -d '{"ip":"8.8.8.8"}'
```

Response:
```json
{
  "success": true,
  "ip": "8.8.8.8",
  "ipVersion": "IPv4",
  "hostnames": ["dns.google"],
  "ptrRecord": "dns.google",
  "responseTime": 28,
  "hostnameCount": 1
}
```

**When to use**: Identify the hostname associated with an IP, verify PTR records for email deliverability, or investigate unknown IPs.

---

### domain_to_ip

Resolve a domain to all its IP addresses with CDN detection and geolocation.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |
| `dnsServer` | string | no | DNS server ID |

```bash
curl -s -X POST https://dnsrobot.net/api/domain-ip \
  -H "Content-Type: application/json" \
  -d '{"domain":"cloudflare.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "cloudflare.com",
  "summary": {
    "totalIPs": 4,
    "ipv4Count": 2,
    "ipv6Count": 2,
    "hasCDN": true,
    "cdnProviders": ["Cloudflare"],
    "hasIPv6": true
  },
  "ipAddresses": [
    {
      "ip": "104.16.132.229",
      "cdnProvider": "Cloudflare",
      "country": "US",
      "asn": "AS13335"
    }
  ]
}
```

**When to use**: Find all IPs behind a domain, check CDN usage, verify IPv6 support, or identify hosting provider.

---

## Domain Tools

### whois_lookup

Get WHOIS/RDAP registration data for a domain — registrar, dates, contacts, nameservers.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |

```bash
curl -s -X POST https://dnsrobot.net/api/whois \
  -H "Content-Type: application/json" \
  -d '{"domain":"github.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "github.com",
  "registeredOn": "2007-10-09T18:20:50Z",
  "expiresOn": "2026-10-09T18:20:50Z",
  "registrar": {
    "name": "MarkMonitor Inc.",
    "url": "http://www.markmonitor.com"
  },
  "nameServers": ["dns1.p08.nsone.net", "dns2.p08.nsone.net"],
  "status": ["clientDeleteProhibited", "clientTransferProhibited"],
  "age": "18 years",
  "source": "RDAP"
}
```

**When to use**: Check domain ownership, expiration dates, registrar info, or investigate a domain's history.

---

### domain_health

Run a comprehensive health check on a domain — DNS, SSL, email security, HTTP, and performance.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |

```bash
curl -s -X POST https://dnsrobot.net/api/domain-health \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "example.com",
  "overallScore": 78,
  "checks": [
    {
      "name": "SSL Certificate",
      "category": "Security",
      "status": "pass",
      "score": 15,
      "maxScore": 15,
      "details": "Valid SSL certificate, expires in 245 days"
    }
  ],
  "categoryScores": [
    { "category": "DNS", "score": 20, "maxScore": 20, "percentage": 100, "grade": "A" },
    { "category": "Security", "score": 25, "maxScore": 30, "percentage": 83, "grade": "B" }
  ]
}
```

**When to use**: Get a quick overall assessment of a domain's configuration, security posture, and email authentication setup. This is the best starting point for a full domain audit.

---

### subdomain_finder

Discover subdomains using Certificate Transparency logs. Returns results as an NDJSON stream.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |

```bash
curl -s -X POST https://dnsrobot.net/api/subdomain-finder \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com"}'
```

Response (NDJSON — one JSON object per line):
```
{"type":"subdomains","names":["www.example.com","mail.example.com"]}
{"type":"dns","results":[{"subdomain":"www.example.com","ip":"93.184.216.34","isActive":true}]}
{"type":"enrichment","data":{"93.184.216.34":{"provider":"Edgecast","country":"US"}}}
{"type":"complete","domain":"example.com","total":15,"activeCount":12,"inactiveCount":3}
```

**When to use**: Discover all known subdomains for security audits, attack surface mapping, or infrastructure analysis.

> **Note**: This is a streaming endpoint. Each line is a separate JSON object. Parse line by line.

---

## Email Security Tools

### spf_check

Validate SPF (Sender Policy Framework) records with full include tree resolution.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |

```bash
curl -s -X POST https://dnsrobot.net/api/spf-checker \
  -H "Content-Type: application/json" \
  -d '{"domain":"google.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "google.com",
  "found": true,
  "rawRecord": "v=spf1 include:_spf.google.com ~all",
  "mechanisms": [
    { "type": "include", "qualifier": "pass", "value": "_spf.google.com", "description": "Include SPF record from _spf.google.com" }
  ],
  "lookupCount": 4,
  "score": 85,
  "grade": "B+",
  "isValid": true,
  "warnings": ["Using ~all (softfail) instead of -all (hardfail)"]
}
```

**When to use**: Validate SPF configuration, check DNS lookup count (max 10 per RFC 7208), or debug email authentication failures.

---

### dkim_check

Validate DKIM (DomainKeys Identified Mail) records. Auto-detects the selector if not provided.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |
| `selector` | string | no | DKIM selector (auto-tries 65+ common selectors if omitted) |

```bash
curl -s -X POST https://dnsrobot.net/api/dkim-checker \
  -H "Content-Type: application/json" \
  -d '{"domain":"google.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "google.com",
  "selector": "20230601",
  "found": true,
  "rawRecord": "v=DKIM1; k=rsa; p=MIIBIjAN...",
  "tags": [
    { "tag": "v", "value": "DKIM1", "description": "DKIM version" },
    { "tag": "k", "value": "rsa", "description": "Key type" }
  ],
  "score": 90,
  "grade": "A",
  "keyType": "rsa",
  "keySize": 2048,
  "isValid": true
}
```

**When to use**: Verify DKIM is configured, check key size and type, or find the active DKIM selector for a domain.

---

### dmarc_check

Validate DMARC (Domain-based Message Authentication) records and policy strength.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |

```bash
curl -s -X POST https://dnsrobot.net/api/dmarc-checker \
  -H "Content-Type: application/json" \
  -d '{"domain":"google.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "google.com",
  "found": true,
  "rawRecord": "v=DMARC1; p=reject; rua=mailto:mailauth-reports@google.com",
  "policy": "reject",
  "subdomainPolicy": "reject",
  "tags": [
    { "tag": "p", "value": "reject", "description": "Policy for domain" }
  ],
  "score": 95,
  "grade": "A",
  "isValid": true
}
```

**When to use**: Check if a domain has DMARC protection, verify policy strength (none/quarantine/reject), or find reporting addresses.

---

### bimi_check

Check BIMI (Brand Indicators for Message Identification) records for logo display in email.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |

```bash
curl -s -X POST https://dnsrobot.net/api/bimi-checker \
  -H "Content-Type: application/json" \
  -d '{"domain":"cnn.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "cnn.com",
  "found": true,
  "rawRecord": "v=BIMI1; l=https://amplify.valimail.com/bimi/...; a=https://amplify.valimail.com/bimi/.../a.pem",
  "logoUrl": "https://amplify.valimail.com/bimi/.../logo.svg",
  "authorityUrl": "https://amplify.valimail.com/bimi/.../a.pem",
  "isValid": true
}
```

**When to use**: Check if a domain has BIMI configured for brand logo display in email clients like Gmail.

---

### smtp_test

Test SMTP connectivity, STARTTLS support, and server capabilities.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `hostname` | string | yes | Mail server hostname or IP |
| `port` | number | no | SMTP port (default 25; use 465 for implicit TLS, 587 for submission) |

```bash
curl -s -X POST https://dnsrobot.net/api/smtp-test \
  -H "Content-Type: application/json" \
  -d '{"hostname":"smtp.google.com","port":587}'
```

Response:
```json
{
  "hostname": "smtp.google.com",
  "port": 587,
  "connected": true,
  "banner": "220 smtp.google.com ESMTP",
  "bannerCode": 220,
  "ehloCapabilities": {
    "starttls": true,
    "authMechanisms": ["LOGIN", "PLAIN", "XOAUTH2"],
    "sizeLimit": 35882577,
    "pipelining": true,
    "eightBitMime": true
  },
  "starttlsSupported": true,
  "tlsConnected": true,
  "tlsProtocol": "TLSv1.3",
  "responseTime": 234
}
```

**When to use**: Test if a mail server is reachable, check TLS support, or verify SMTP capabilities before configuring email sending.

---

## Network & Security Tools

### ssl_check

Inspect SSL/TLS certificates, cipher suites, and trust chain for any domain.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Domain name |

```bash
curl -s -X POST https://dnsrobot.net/api/ssl-certificate \
  -H "Content-Type: application/json" \
  -d '{"domain":"github.com"}'
```

Response:
```json
{
  "success": true,
  "domain": "github.com",
  "resolvedIP": "140.82.121.3",
  "serverType": "GitHub.com",
  "tlsInfo": {
    "protocol": "TLSv1.3",
    "cipherName": "TLS_AES_128_GCM_SHA256"
  },
  "leafCertificate": {
    "issuer": "Sectigo ECC Domain Validation Secure Server CA",
    "notBefore": "2024-03-07",
    "notAfter": "2025-03-07",
    "daysToExpire": 120,
    "isValid": true,
    "keySize": 256,
    "alternativeNames": ["github.com", "www.github.com"]
  },
  "certificateChain": [
    { "commonName": "github.com", "daysToExpire": 120 },
    { "commonName": "Sectigo ECC Domain Validation Secure Server CA" }
  ],
  "trustStatus": {
    "isTrusted": true,
    "hasValidChain": true,
    "browserCompatible": true
  }
}
```

**When to use**: Check certificate expiration, verify TLS version and cipher strength, inspect the certificate chain, or debug SSL errors.

---

### ip_lookup

Get geolocation, ISP, and ASN information for an IP address.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ip` | string | yes | IPv4 or IPv6 address |

```bash
curl -s -X POST https://dnsrobot.net/api/ip-info \
  -H "Content-Type: application/json" \
  -d '{"ip":"1.1.1.1"}'
```

Response:
```json
{
  "query": "1.1.1.1",
  "hostname": "one.one.one.one",
  "city": "Los Angeles",
  "region": "California",
  "country": "US",
  "timezone": "America/Los_Angeles",
  "isp": "Cloudflare, Inc.",
  "org": "APNIC and Cloudflare DNS Resolver project",
  "as": "AS13335 Cloudflare, Inc.",
  "lat": 34.0522,
  "lon": -118.2437,
  "anycast": true
}
```

**When to use**: Geolocate an IP address, identify the hosting provider or ISP, or look up ASN information.

---

### http_headers

Fetch HTTP response headers and analyze security header configuration.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | yes | Full URL including protocol (e.g. `https://example.com`) |

```bash
curl -s -X POST https://dnsrobot.net/api/http-headers \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com"}'
```

Response:
```json
{
  "success": true,
  "url": "https://github.com",
  "statusCode": 200,
  "statusText": "OK",
  "responseTime": 185,
  "headers": {
    "content-type": "text/html; charset=utf-8",
    "strict-transport-security": "max-age=31536000",
    "x-frame-options": "deny",
    "content-security-policy": "default-src 'none'; ..."
  },
  "headerCount": 24,
  "security": {
    "grade": "A",
    "score": 90,
    "checks": [
      { "name": "HSTS", "present": true, "value": "max-age=31536000", "severity": "high" }
    ]
  }
}
```

**When to use**: Audit security headers, check HSTS/CSP/X-Frame-Options configuration, or debug HTTP response issues.

> **Important**: The `url` parameter must include the protocol (`https://` or `http://`).

---

### port_check

Check if a TCP port is open on a host. Single port uses GET, multiple ports use POST (NDJSON stream).

**Single port (GET):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `host` | query string | yes | Hostname or IP |
| `port` | query string | yes | Port number (1–65535) |

```bash
curl -s "https://dnsrobot.net/api/port-check?host=github.com&port=443"
```

Response:
```json
{
  "host": "github.com",
  "port": 443,
  "status": "open",
  "service": "HTTPS",
  "ms": 42
}
```

**Multiple ports (POST) — NDJSON stream:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `host` | string | yes | Hostname or IP |
| `ports` | number[] | yes | Array of ports (max 30) |

```bash
curl -s -X POST https://dnsrobot.net/api/port-check \
  -H "Content-Type: application/json" \
  -d '{"host":"github.com","ports":[22,80,443]}'
```

Response (NDJSON):
```
{"type":"start","host":"github.com","total":3}
{"type":"port","port":22,"service":"SSH","status":"open","ms":45}
{"type":"port","port":80,"service":"HTTP","status":"open","ms":42}
{"type":"port","port":443,"service":"HTTPS","status":"open","ms":41}
{"type":"done","host":"github.com","total":3,"open":3,"closed":0}
```

**When to use**: Check if specific services are reachable, verify firewall rules, or scan common ports on a server.

---

### ip_blacklist

Check if an IP is listed on any DNS blacklists (DNSBL). Returns results as an NDJSON stream.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ip` | query string | yes | IPv4 address |

```bash
curl -s "https://dnsrobot.net/api/ip-blacklist?ip=1.2.3.4"
```

Response (NDJSON — one JSON object per line):
```
{"type":"init","ip":"1.2.3.4","engines":[{"name":"Spamhaus ZEN","category":"spam"},{"name":"Barracuda","category":"spam"}]}
{"type":"engine","result":{"engine":"Spamhaus ZEN","detected":false,"category":"spam","responseTimeMs":45}}
{"type":"engine","result":{"engine":"Barracuda","detected":false,"category":"spam","responseTimeMs":52}}
{"type":"abuseipdb","data":{"abuse_confidence":0,"total_reports":0,"country":"US","isp":"Example ISP"}}
{"type":"complete","summary":{"detections":0,"engines_count":47,"detection_rate":"0%","reputation_score":100,"risk_level":"low"}}
```

**When to use**: Check if an IP is blacklisted for spam or abuse, assess IP reputation before sending email, or investigate suspicious IPs.

> **Note**: This is a streaming endpoint (NDJSON). Parse line by line. Checks ~47 DNSBL engines in parallel.

---

## Decision Tree: Which Tool Should I Use?

Use this to pick the right endpoint:

- **"Look up DNS records"** → `dns_lookup` (specify record type + DNS server)
- **"What are the nameservers?"** → `ns_lookup`
- **"What email provider does this domain use?"** → `mx_lookup`
- **"Where does this CNAME point?"** → `cname_lookup`
- **"What hostname is this IP?"** → `reverse_dns`
- **"What IPs does this domain resolve to?"** → `domain_to_ip`
- **"Who owns this domain?"** → `whois_lookup`
- **"Is this domain configured correctly?"** → `domain_health` (runs 11 checks in one call)
- **"Find subdomains"** → `subdomain_finder` (streaming)
- **"Check SPF/DKIM/DMARC/BIMI"** → use the specific checker
- **"Is the mail server working?"** → `smtp_test`
- **"Check SSL certificate"** → `ssl_check`
- **"Where is this IP located?"** → `ip_lookup`
- **"Check security headers"** → `http_headers` (URL must include `https://`)
- **"Is this port open?"** → `port_check`
- **"Is this IP blacklisted?"** → `ip_blacklist` (streaming, IPv4 only)
- **"Full domain audit"** → start with `domain_health`, then drill into specific tools

## Important Notes

1. **No API key required.** All endpoints are free and public.
2. **Streaming endpoints** (`subdomain_finder`, `ip_blacklist`, `port_check` POST) return NDJSON — one JSON object per line. Parse line by line, not as a single JSON document.
3. **Error format**: All endpoints return `{"error": "message"}` with appropriate HTTP status codes (400 for validation errors, 500 for server errors).
4. **Domain auto-cleaning**: Endpoints that accept `domain` automatically strip `http://`, `https://`, `www.`, and trailing paths. You can pass `https://www.example.com/path` and it will query `example.com`.
5. **DNS server for dns_lookup**: This parameter is required. Common choices: `8.8.8.8` (Google), `1.1.1.1` (Cloudflare), `9.9.9.9` (Quad9).
6. **http_headers URL**: Must include the protocol (`https://example.com`, not just `example.com`).
7. **ip_blacklist**: IPv4 only. Does not support IPv6.
8. **port_check**: Single port = GET with query params. Multiple ports = POST with JSON body (NDJSON stream response, max 30 ports).
