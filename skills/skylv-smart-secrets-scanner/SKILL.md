---
description: Intelligent secrets detection and prevention — scan code, configs, and git history for exposed API keys, passwords, tokens, and credentials
keywords: openclaw, skill, automation, ai-agent, secrets, scanner, security, credential, api-key, token-detection, leak-prevention
name: smart-secrets-scanner
triggers: secrets scanner, credential leak, API key detection, token exposure, security scan, secret detection
---

# smart-secrets-scanner

> Intelligent secrets detection — scan code, configs, and git history for exposed API keys, passwords, tokens, and credentials before they leak.

## Skill Metadata

- **Slug**: smart-secrets-scanner
- **Version**: 1.0.0
- **Description**: Intelligent secrets and credential scanner for codebases. Detects exposed API keys, passwords, tokens, private keys, and credentials in source code, config files, environment variables, and git commit history. Provides auto-remediation suggestions.
- **Category**: security
- **Trigger Keywords**: `secrets scanner`, `credential leak`, `API key detection`, `token exposure`, `security scan`, `secret detection`, `git secret`

---

## Capabilities

### 1. Scan Current Project
\`\`\`bash
node scanner.js scan ./src
node scanner.js scan ./ --include "*.js,*.json,*.yaml,*.env*"
\`\`\`
Detects 50+ patterns: AWS keys, GitHub tokens, Slack webhooks, database URLs, private keys, JWTs, etc.

### 2. Scan Git History
\`\`\`bash
node scanner.js git-scan --depth 50
node scanner.js git-scan --since "2024-01-01"
\`\`\`
Finds secrets that were committed and later removed (still in git history).

### 3. Pre-commit Hook
\`\`\`bash
node scanner.js hook --install
# Now every commit is scanned automatically
\`\`\`

### 4. Auto-Redact
\`\`\`bash
node scanner.js redact ./src/config.js --replace-with "[REDACTED]"
\`\`\`
Replace detected secrets with placeholder values.

---

## Detection Patterns

| Category | Examples |
|----------|----------|
| Cloud Keys | AWS_ACCESS_KEY, GCP_SERVICE_ACCOUNT, AZURE_CLIENT_SECRET |
| API Tokens | GitHub, Slack, Stripe, OpenAI, Anthropic, Google Maps |
| Database | MongoDB URI, PostgreSQL URL, Redis password |
| Crypto | RSA private key, SSH key, certificate |
| App Secrets | JWT secret, session key, encryption key |
| Config Files | .env, .npmrc, .pypirc, credentials.json |

## Use Cases

1. **CI/CD Pipeline**: Block deployments with exposed secrets
2. **Pre-commit**: Prevent secrets from entering git history
3. **Audit**: Scan existing codebase for leaked credentials
4. **Compliance**: SOC2, GDPR requirement for credential management
5. **Education**: Teach developers about secret management

## Output Format

\`\`\`json
{
  "findings": [
    {
      "file": "src/config.js",
      "line": 12,
      "type": "AWS_ACCESS_KEY",
      "severity": "CRITICAL",
      "matched": "AKIAIOSFODNN7EXAMPLE",
      "suggestion": "Move to environment variable or secrets manager"
    }
  ],
  "summary": { "critical": 1, "high": 0, "medium": 2, "low": 5 }
}
\`\`\`
