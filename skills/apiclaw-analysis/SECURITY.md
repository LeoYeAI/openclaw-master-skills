# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | ✅ Yes    |
| < 1.1   | ❌ No     |

## Reporting a Vulnerability

If you discover a security vulnerability in this skill, please report it responsibly:

1. **Email:** security@srp.one
2. **Subject:** `[SECURITY] Amazon-analysis-skill: <brief description>`
3. **Include:** Steps to reproduce, potential impact, and suggested fix (if any)

**Please do NOT open a public GitHub issue for security vulnerabilities.**

We will acknowledge your report within 48 hours and aim to release a fix within 7 days for critical issues.

## Scope

This security policy covers:
- The `scripts/apiclaw.py` CLI script
- Credential handling (API key storage and transmission)
- Data exposure risks in skill documentation

## Known Security Considerations

- **API Key Storage:** Keys can be stored via environment variable (`APICLAW_API_KEY`, preferred) or `config.json` (fallback). The `config.json` file is listed in `.gitignore` to prevent accidental commits.
- **Network:** The script only communicates with `https://api.apiclaw.io`. No other external endpoints are contacted.
- **No Telemetry:** This skill does not collect or transmit usage data.
