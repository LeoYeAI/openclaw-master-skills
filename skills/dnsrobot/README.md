# 🌐 DNS Robot — OpenClaw Skill

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://dnsrobot.net)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Homepage](https://img.shields.io/badge/homepage-dnsrobot.net-purple)](https://dnsrobot.net)

Give your AI agent DNS, domain, email security, SSL, and network tools — powered by [DNS Robot](https://dnsrobot.net). No API key required.

DNS Robot offers [53 free online tools](https://dnsrobot.net/all-tools) for DNS lookups, domain analysis, email authentication, SSL inspection, and network diagnostics. This OpenClaw skill wraps 19 of those tools so your agent can query them directly.

## Installation

```bash
openclaw install dnsrobot
```

## Available Tools

| Tool | Endpoint | Description |
|------|----------|-------------|
| [DNS Lookup](https://dnsrobot.net/dns-lookup) | `dns_lookup` | Query A, AAAA, CNAME, MX, NS, TXT, SOA, CAA, DNSKEY, DS records from any DNS server |
| [NS Lookup](https://dnsrobot.net/ns-lookup) | `ns_lookup` | Find authoritative nameservers and their hosting providers |
| [MX Lookup](https://dnsrobot.net/mx-lookup) | `mx_lookup` | Find mail exchange records and identify the email provider |
| [CNAME Lookup](https://dnsrobot.net/cname-lookup) | `cname_lookup` | Trace the full CNAME chain with circular reference detection |
| [Reverse DNS](https://dnsrobot.net/reverse-dns-lookup) | `reverse_dns` | PTR lookup — find hostnames for an IP address |
| [Domain to IP](https://dnsrobot.net/domain-to-ip) | `domain_to_ip` | Resolve all IPs with CDN detection and geolocation |
| [WHOIS Lookup](https://dnsrobot.net/whois-lookup) | `whois_lookup` | Domain registration data — registrar, dates, contacts, nameservers |
| [Domain Health](https://dnsrobot.net/domain-health-checker) | `domain_health` | Comprehensive health check (DNS, SSL, email, HTTP — 11 checks) |
| [Subdomain Finder](https://dnsrobot.net/subdomain-finder) | `subdomain_finder` | Discover subdomains via Certificate Transparency logs |
| [SPF Checker](https://dnsrobot.net/spf-checker) | `spf_check` | Validate SPF records with full include tree resolution |
| [DKIM Checker](https://dnsrobot.net/dkim-checker) | `dkim_check` | Validate DKIM records — auto-detects selector from 65+ common names |
| [DMARC Checker](https://dnsrobot.net/dmarc-checker) | `dmarc_check` | Validate DMARC policy and reporting configuration |
| [BIMI Checker](https://dnsrobot.net/bimi-checker) | `bimi_check` | Check BIMI record for email brand logo display |
| [SMTP Test](https://dnsrobot.net/smtp-test) | `smtp_test` | Test SMTP connectivity, STARTTLS, and server capabilities |
| [SSL Checker](https://dnsrobot.net/ssl-checker) | `ssl_check` | Inspect SSL/TLS certificates, cipher suites, and trust chain |
| [IP Lookup](https://dnsrobot.net/ip-lookup) | `ip_lookup` | Geolocation, ISP, ASN, and hostname for any IP |
| [HTTP Headers](https://dnsrobot.net/http-headers-checker) | `http_headers` | Fetch headers and audit security header configuration |
| [Port Checker](https://dnsrobot.net/port-checker) | `port_check` | Check if TCP ports are open with service detection |
| [IP Blacklist](https://dnsrobot.net/ip-blacklist-checker) | `ip_blacklist` | Check 47 DNS blacklists + AbuseIPDB reputation |

## Usage Examples

After installing, just ask your agent naturally:

- **"Look up the DNS records for github.com"** — runs A record query via Google DNS
- **"Check the SSL certificate for stripe.com"** — inspects cert chain, expiry, TLS version
- **"Who owns openai.com?"** — WHOIS lookup with registrar, dates, nameservers
- **"Run a full health check on my-domain.com"** — 11 parallel checks, overall score out of 100
- **"Check if 203.0.113.1 is blacklisted"** — queries 47 DNSBL engines + AbuseIPDB
- **"Find all subdomains of example.com"** — CT log discovery with DNS resolution
- **"Does google.com have SPF, DKIM, and DMARC configured?"** — runs all three email auth checks
- **"Test SMTP connectivity to smtp.office365.com on port 587"** — checks TLS, capabilities

## Other DNS Robot Tools

DNS Robot also provides client-side tools that don't need an API — use them directly at [dnsrobot.net](https://dnsrobot.net):

- [Password Generator](https://dnsrobot.net/password-generator) — generate secure random passwords
- [Password Strength Tester](https://dnsrobot.net/password-strength-tester) — check password entropy and crack time
- [QR Code Generator](https://dnsrobot.net/qr-code-generator) — create QR codes for URLs, text, WiFi, etc.
- [QR Code Scanner](https://dnsrobot.net/qr-code-scanner) — scan QR codes from camera or image upload
- [Morse Code Translator](https://dnsrobot.net/morse-code-translator) — convert text to Morse and back
- [Text to Binary](https://dnsrobot.net/text-to-binary) — convert text to binary, octal, hex, and decimal
- [Small Text Generator](https://dnsrobot.net/small-text-generator) — create superscript, subscript, and small caps text
- [Email Header Analyzer](https://dnsrobot.net/email-header-analyzer) — parse email headers for delivery path and auth results
- [DMARC Generator](https://dnsrobot.net/dmarc-generator) — generate DMARC DNS records with a visual builder
- [MAC Address Generator](https://dnsrobot.net/mac-address-generator) — generate random MAC addresses
- [CMYK to Pantone](https://dnsrobot.net/cmyk-to-pantone) — find the closest Pantone match for CMYK values
- [Username Checker](https://dnsrobot.net/username-checker) — check username availability across 30+ platforms

See all 53 tools at [dnsrobot.net/all-tools](https://dnsrobot.net/all-tools).

## API Details

All API endpoints are free and require no authentication. The base URL is `https://dnsrobot.net`. Endpoints accept JSON request bodies and return JSON responses. Three endpoints (`subdomain_finder`, `ip_blacklist`, `port_check` with multiple ports) stream results as NDJSON (newline-delimited JSON).

For full endpoint documentation with parameters and response schemas, see the [SKILL.md](SKILL.md) file.

## License

[MIT](LICENSE)

## About DNS Robot

[DNS Robot](https://dnsrobot.net) is a free DNS and network tools platform with 53 online utilities for developers, sysadmins, and security researchers. Built with Next.js, deployed at [dnsrobot.net](https://dnsrobot.net). Browse all tools at [dnsrobot.net/all-tools](https://dnsrobot.net/all-tools) or read the [DNS Robot Blog](https://dnsrobot.net/blog) for guides on DNS, email security, and network troubleshooting.
