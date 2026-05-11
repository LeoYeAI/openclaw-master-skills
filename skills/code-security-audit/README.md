# Code Security Audit

Unified security audit toolkit for comprehensive code security analysis.

## Features

- **OWASP Top 10 Detection** - All 10 vulnerability categories with code patterns
- **Dependency Vulnerability Scanning** - npm, pip, cargo, go modules
- **Secret Detection** - 70+ API key patterns, credentials, private keys, crypto wallets
- **SSL/TLS Verification** - Certificate validation, cipher suite checks
- **AI Agent Security** (NEW) - Numeric risks, prompt injection, crypto wallet safety
- **Security Scoring** - Quantified 0-100 security score
- **Multi-Language Support** - JS/TS, Python, Go, Java, Rust, PHP, Ruby, Solidity

## Quick Start

```bash
# Full security audit with scoring
./scripts/security-audit.sh --full

# Quick scan (secrets + dependencies only)
./scripts/security-audit.sh --quick

# OWASP Top 10 check
./scripts/security-audit.sh --owasp

# AI Agent security check (NEW)
./scripts/security-audit.sh --ai

# SSL/TLS verification
./scripts/security-audit.sh --ssl example.com

# Generate report
./scripts/security-audit.sh --full --output report.md
```

## Security Score

| Score | Risk Level |
|-------|------------|
| 90-100 | ✅ Low |
| 70-89 | ⚠️ Medium |
| 50-69 | 🔶 High |
| 0-49 | 🚨 Critical |

## AI Agent Security (v2.1.0)

Inspired by the Lobstar Wilde incident (Feb 2026) where an AI agent accidentally transferred $250,000 due to numeric parsing errors.

**Detection Categories:**
- Numeric handling risks (floating-point, unit conversion)
- Prompt injection patterns
- Cryptocurrency/wallet security
- Amount validation
- Human-in-the-loop mechanism
- API response validation

## CI/CD Integration

See `templates/` directory for GitHub Actions and GitLab CI templates.

## License

MIT
