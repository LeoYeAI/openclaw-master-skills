---
name: security-audit
description: "Use when scanning repos and environments for leaked secrets, exposed credentials, vulnerable dependencies, and common security misconfigurations."
version: 1.0.0
author: Papi
license: MIT
metadata:
  hermes:
    tags: [security, audit, secrets, credentials, vulnerabilities, scanning]
    related_skills: [github-code-review, docker-ops]
---

# Security Audit

## Overview

Scan codebases, repos, and environments for security issues: leaked secrets, exposed credentials, vulnerable dependencies, and common misconfigurations. This is the enforcement arm of SOUL.md Rule 3: no keys, tokens, IPs, or credentials in any chat channel.

## When to Use

- Before committing code or opening a PR
- Scanning a repo for leaked secrets or credentials
- Checking dependency vulnerabilities
- Auditing Docker images or compose files for misconfigurations
- Reviewing .env or config files for exposed secrets
- Post-incident: checking what got leaked

Don't use for:
- Penetration testing (this is defensive scanning)
- Compliance auditing (SOC2, HIPAA — that's a different level)

## Scan Types

### 1. Secret Scanning

Find leaked keys, tokens, and credentials in code and git history.

```bash
# Using gitleaks (install: go install github.com/gitleaks/gitleaks/v8@latest)
gitleaks detect --source . --verbose

# Scan a specific repo
gitleaks detect --source /path/to/repo --report-format json --report-path leaks.json

# Scan git history (not just current state)
gitleaks detect --source . --log-opts="--all"

# Using trufflehog (pip install trufflehog)
trufflehog filesystem /path/to/repo
trufflehog github --org myorg --token $GITHUB_TOKEN

# Quick manual check — grep for common patterns
grep -rn --include="*.py" --include="*.js" --include="*.ts" --include="*.yaml" --include="*.yml" --include="*.env" \
  -E '(password|secret|api_key|apikey|token|private_key)\s*[:=]\s*["\x27]?[A-Za-z0-9_\-]{16,}' .
```

### 2. Dependency Vulnerability Scan

Check for known CVEs in dependencies.

```bash
# Python
pip audit                  # From PyPA
safety check               # From safetycli
pip-audit -r requirements.txt

# Node.js
npm audit
npm audit fix              # Auto-fix where possible
npx better-npm-audit audit # More configurable

# Go
nancy sleuth < go.sum
govulncheck ./...

# Ruby
bundle audit check --update

# General: OSV scanner (supports many ecosystems)
# Install: go install github.com/google/osv-scanner/cmd/osv-scanner@latest
osv-scanner --lockfile=requirements.txt
osv-scanner --lockfile=package-lock.json
osv-scanner -r /path/to/repo
```

### 3. Docker Image Scan

```bash
# Using trivy (install: apt install trivy or download binary)
trivy image myapp:latest
trivy image --severity HIGH,CRITICAL myapp:latest
trivy image --format json --output report.json myapp:latest

# Scan a Dockerfile for misconfigurations
trivy config Dockerfile
trivy config docker-compose.yml

# Using docker scout (built into Docker Desktop)
docker scout cves myapp:latest
docker scout recommendations myapp:latest
```

### 4. Infrastructure-as-Code Scan

```bash
# Terraform, CloudFormation, K8s manifests, Docker Compose
trivy config /path/to/infra/

# Checkov (pip install checkov)
checkov -d /path/to/terraform/
checkov -f docker-compose.yml
checkov --framework dockerfile --check CKV_DOCKER_*

# tfsec (for Terraform specifically)
tfsec /path/to/terraform/
```

### 5. Git History Deep Scan

Even if secrets are removed from current code, they may persist in git history.

```bash
# Search git history for secrets
git log --all --full-history -p -- "*.env" "*secret*" "*credential*"
git log --all -S "api_key" --oneline
git log --all -S "password" --oneline

# Remove secrets from git history (NUCLEAR — use with caution)
# git filter-repo (install: pip install git-filter-repo)
git filter-repo --invert-paths --path .env
git filter-repo --replace-text <(echo 'OLD_SECRET==>REDACTED')
```

### 6. Config File Audit

Common misconfigurations to check:

```bash
# .env files should NOT be committed
ls -la .env* && git ls-files .env*

# .gitignore should exclude secrets
cat .gitignore | grep -E '(env|secret|key|credential|token)'

# Docker Compose: check for hardcoded passwords
grep -rn 'POSTGRES_PASSWORD\|MYSQL_ROOT_PASSWORD\|REDIS_PASSWORD' docker-compose*.yml

# Check file permissions
find . -name "*.env" -o -name "*secret*" -o -name "*key*" | xargs ls -la
# .env files should be 600, not world-readable
```

## Pre-Commit Security Gate

Add to CI or run before every push:

```bash
#!/bin/bash
# security-gate.sh — Run before pushing

set -e

echo "=== Secret Scan ==="
gitleaks detect --source . --no-git --verbose

echo "=== Dependency Audit ==="
pip-audit -r requirements.txt 2>/dev/null || npm audit --audit-level=high 2>/dev/null || true

echo "=== Docker Scan ==="
if [ -f Dockerfile ]; then
  trivy config Dockerfile
fi

echo "=== Compose Scan ==="
if [ -f docker-compose.yml ]; then
  trivy config docker-compose.yml
fi

echo "=== Git Tracked Secrets ==="
if git ls-files .env* 2>/dev/null | grep -q .; then
  echo "FAIL: .env files are tracked by git!"
  exit 1
fi

echo "=== Security Gate PASSED ==="
```

## What to Do When Secrets Are Leaked

1. **Rotate immediately.** The secret is compromised. Generate a new one.
2. **Revoke the old one.** Invalidate the leaked credential.
3. **Remove from git history.** Use `git filter-repo` if needed.
4. **Force push.** Rewrite the branch history (coordinate with team).
5. **Scan for reuse.** Check if the same secret is used elsewhere.
6. **Document.** What leaked, how, when it was rotated.

## Secret Patterns to Watch For

| Type | Pattern |
|---|---|
| AWS Access Key | `AKIA[0-9A-Z]{16}` |
| AWS Secret Key | `[A-Za-z0-9/+=]{40}` |
| GitHub Token | `gh[ps]_[A-Za-z0-9_]{36}` |
| Slack Token | `xox[baprs]-[A-Za-z0-9-]+` |
| Generic API Key | `(api_key\|apikey\|token)\s*[:=]\s*["'][A-Za-z0-9]{20,}` |
| Private Key | `-----BEGIN (RSA\|EC\|DSA)? ?PRIVATE KEY-----` |
| JWT | `eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+` |
| Database URL | `(postgres\|mysql\|mongodb)://[^\s]+:[^\s]+@` |

## Working Grep Patterns

Complex regex patterns with single quotes and backticks break in bash eval contexts (e.g., hermes terminal tool). Use simpler patterns and chain with grep -v:

```bash
# GOOD: Simple pattern, chained exclusions
grep -rn --include="*.py" --include="*.js" --include="*.ts" --include="*.yaml" \
  -E "api_key|apikey|secret_key|private_key|AUTH_TOKEN|ACCESS_TOKEN" /path/to/repo \
  | grep -v node_modules | grep -v venv/ | grep -v ".git/" \
  | grep -v "example" | grep -v "placeholder" | grep -v "TODO"

# BAD: Overly complex single-pattern with inline quantifiers
# These break in bash eval and produce "unexpected EOF" errors
grep -rn -E '(password|secret|api_key)\s*[:=]\s*["\x27]?[A-Za-z0-9_\-]{16,}' /path
```

## Redacting Secrets in Output

When displaying scan results, ALWAYS redact actual secret values. Show location + type only:

```python
import re
# Replace actual values after delimiters like = : or quotes
redacted = re.sub(r'([:=]\s*["\x27]?)\S{16,}', r'\1[REDACTED]', line)
```

## WSL Cross-Filesystem Scanning

Scanning repos under `/mnt/c/` is 3-5x slower than Linux filesystem. For large repos:
- Increase timeout (30s+ per repo on /mnt/c/)
- Use `--include=` to limit file types
- Exclude `venv/`, `node_modules/`, `.git/` aggressively
- Consider copying large repos to Linux fs before scanning: `cp -r /mnt/c/Users/name/repo ~/scan-target`

## Dependency Scanning Fallbacks

pip-audit and npm audit may not be installed. Graceful fallback chain:

```bash
# Python
pip-audit -r requirements.txt 2>/dev/null || \
  safety check -r requirements.txt 2>/dev/null || \
  echo "SKIP: No Python dependency scanner available"

# Node.js
npm audit --audit-level=high 2>/dev/null || \
  echo "SKIP: npm not available or no package.json"
```

## Common Pitfalls

1. **Only scanning current code.** Git history is forever. A secret committed 2 years ago and removed is still in history.

2. **Ignoring .env.example.** .env.example is fine to commit, but make sure it has placeholder values, not real ones.

3. **False confidence from clean scans.** Scanners have blind spots. A clean gitleaks scan doesn't mean you're safe. Review manually too.

4. **Rotating but not revoking.** Generating a new key doesn't help if the old one still works. Always revoke.

5. **Docker images with secrets baked in.** Never COPY .env into a Docker image. Use runtime env vars or Docker secrets instead.

6. **Committing security scan reports.** The report itself may contain snippets of leaked secrets. Add `leaks.json`, `report.json` to .gitignore.

7. **Complex regex breaking in bash eval.** Multi-quote patterns with \x27 and {16,} quantifiers break in hermes terminal and similar bash eval contexts. Use simple OR patterns and chain grep -v for exclusions.

8. **Scanning venv/ and node_modules/.** These generate massive noise (library code references to api_key, token, etc.). Always exclude them. The stealth-browser-mcp venv produced 50+ false positives from authlib alone.

9. **WSL /mnt/c/ timeout on large repos.** Repos with thousands of files on the Windows filesystem will time out at default 30s. Either increase timeout or copy to Linux fs first.

## Verification Checklist

- [ ] Secret scanning tool run (gitleaks/trufflehog)
- [ ] Dependency vulnerability audit completed
- [ ] Docker images scanned (if applicable)
- [ ] Git history checked for previously committed secrets
- [ ] .env files not tracked by git
- [ ] No hardcoded passwords in compose files
- [ ] File permissions on secret files are restrictive (600/700)
- [ ] Pre-commit security gate in place or planned
