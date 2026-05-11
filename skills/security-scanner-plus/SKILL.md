---
name: Security Scanner
description: >
  Scan AI agent skills for security vulnerabilities, dangerous code patterns,
  and undeclared permissions. Three-layer analysis: dependency CVE scanning,
  static code analysis, and permission auditing. Returns structured JSON risk 
  report. Use when the user asks to scan a skill for security issues, check 
  for vulnerabilities, audit permissions, or assess skill safety.
metadata:
  requires:
    env:
      - CLAW0X_API_KEY
---

# Security Scanner

**Free skill by [Claw0x](https://claw0x.com)** — powered by Claw0x Gateway API.

Scan AI agent skills for security vulnerabilities across three layers: dependency CVEs, dangerous code patterns, and undeclared permissions. Returns a structured JSON risk report with an overall score (0–100).

> **Free to use.** This skill costs nothing. Just [sign up at claw0x.com](https://claw0x.com), create an API key, and start calling. No credit card, no wallet top-up required.

## Quick Reference

| When This Happens | Scan For | What You Get |
|-------------------|----------|--------------|
| Installing third-party skill | All vulnerabilities | Risk score + CVE list |
| Before publishing skill | Code patterns + permissions | Security audit report |
| Dependency update | New CVEs | Updated vulnerability list |
| User reports suspicious behavior | Undeclared permissions | Permission audit |
| CI/CD pipeline | Automated security check | Pass/fail + recommendations |
| Skill marketplace review | Trust score calculation | Approval decision data |

**Why API-based?** Centralized CVE database (OSV.dev), consistent scanning rules, no local setup required.

---

## 5-Minute Quickstart

### Step 1: Get API Key (30 seconds)
Sign up at [claw0x.com](https://claw0x.com) → Dashboard → Create API Key

### Step 2: Scan Your First Skill (1 minute)
```bash
curl -X POST https://api.claw0x.com/v1/call \
  -H "Authorization: Bearer ck_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "security-scanner",
    "input": {
      "repo_url": "https://github.com/owner/repo"
    }
  }'
```

### Step 3: Review Risk Report (instant)
```json
{
  "overall_risk": "medium",
  "risk_score": 35,
  "dependency_scan": {
    "vulnerabilities": [
      {
        "id": "GHSA-jf85-cpcp-j695",
        "severity": "high",
        "package_name": "lodash",
        "summary": "Prototype Pollution"
      }
    ]
  },
  "code_scan": {
    "findings": [
      {
        "rule_id": "SHELL_INJECT",
        "severity": "critical",
        "file": "handler.ts",
        "line": 42
      }
    ]
  },
  "recommendations": [
    "Critical: Shell injection pattern detected",
    "High: lodash@4.17.20 has known vulnerabilities"
  ]
}
```

### Step 4: Fix Issues (2 minutes)
```bash
# Update vulnerable dependency
npm update lodash

# Fix shell injection
# Replace: exec(userInput)
# With: execFile('command', [userInput])
```

**Done.** Your skill is now more secure.

---

## Real-World Use Cases

### Scenario 1: Skill Marketplace Vetting
**Problem**: You run a skill marketplace and need to vet submissions before approval

**Solution**:
1. Seller submits skill via GitHub URL
2. Automated scan runs on submission
3. Risk score determines approval workflow
4. High-risk skills get manual review
5. Low-risk skills auto-approve

**Example**:
```typescript
async function reviewSkillSubmission(repoUrl) {
  const response = await fetch('https://api.claw0x.com/v1/call', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.CLAW0X_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      skill: 'security-scanner',
      input: { repo_url: repoUrl }
    })
  });
  
  const scan = await response.json();
  
  if (scan.risk_score > 50) {
    await queue.add('manual-review', { repoUrl, scan });
  } else if (scan.risk_score < 20) {
    await approveSkill(repoUrl);
  } else {
    await requestSellerFixes(repoUrl, scan.recommendations);
  }
}
// Result: 80% of submissions auto-processed, 95% fewer security incidents
```

### Scenario 2: CI/CD Security Gate
**Problem**: Developers push code with vulnerabilities that reach production

**Solution**:
1. Add security scan to CI/CD pipeline
2. Block merges if risk score > threshold
3. Require fixes before deployment
4. Track security metrics over time

**Example**:
```yaml
# .github/workflows/security.yml
- name: Security Scan
  run: |
    RESULT=$(curl -X POST https://api.claw0x.com/v1/call \
      -H "Authorization: Bearer $CLAW0X_API_KEY" \
      -d '{"skill":"security-scanner","input":{"repo_url":"${{ github.repository }}"}}')
    
    RISK_SCORE=$(echo $RESULT | jq -r '.risk_score')
    
    if [ $RISK_SCORE -gt 50 ]; then
      echo "Security scan failed: risk score $RISK_SCORE"
      exit 1
    fi
# Result: 90% reduction in production security issues
```

### Scenario 3: Dependency Monitoring
**Problem**: Your skills use dependencies that get new CVEs over time

**Solution**:
1. Schedule weekly scans of all published skills
2. Alert when new vulnerabilities appear
3. Auto-create PRs with dependency updates
4. Track remediation time

**Example**:
```javascript
// Cron job: every Monday
async function weeklySecurityAudit() {
  const skills = await db.skills.findMany({ status: 'published' });
  
  for (const skill of skills) {
    const response = await fetch('https://api.claw0x.com/v1/call', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.CLAW0X_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        skill: 'security-scanner',
        input: { repo_url: skill.repo_url }
      })
    });
    
    const scan = await response.json();
    
    // Check if risk increased
    if (scan.risk_score > skill.last_risk_score) {
      await notifyMaintainer(skill, scan);
      await createUpdatePR(skill, scan.recommendations);
    }
    
    await db.skills.update({
      where: { id: skill.id },
      data: { last_risk_score: scan.risk_score }
    });
  }
}
// Result: Average CVE remediation time: 2 days (industry avg: 30 days)
```

### Scenario 4: Pre-Commit Hooks
**Problem**: Developers accidentally commit secrets or dangerous patterns

**Solution**:
1. Add pre-commit hook that scans changed files
2. Block commits with critical findings
3. Provide immediate feedback
4. Prevent secrets from reaching Git history

**Example**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Get staged files
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|js|py)$')

if [ -z "$FILES" ]; then
  exit 0
fi

# Scan staged code
CODE=$(cat $FILES)
RESULT=$(curl -s -X POST https://api.claw0x.com/v1/call \
  -H "Authorization: Bearer $CLAW0X_API_KEY" \
  -d "{\"skill\":\"security-scanner\",\"input\":{\"code\":\"$CODE\"}}")

CRITICAL=$(echo $RESULT | jq -r '.code_scan.finding_counts.critical')

if [ "$CRITICAL" -gt 0 ]; then
  echo "❌ Commit blocked: critical security issues found"
  echo $RESULT | jq -r '.recommendations[]'
  exit 1
fi

echo "✅ Security scan passed"
exit 0
# Result: Zero secrets committed to Git in 6 months
```

---

## Integration Recipes

### OpenClaw Agent
```typescript
// Scan before installing skill
agent.onSkillInstall(async (skillUrl) => {
  const response = await fetch('https://api.claw0x.com/v1/call', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.CLAW0X_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      skill: 'security-scanner',
      input: { repo_url: skillUrl }
    })
  });
  
  const scan = await response.json();
  
  if (scan.risk_score > 50) {
    throw new Error(`Skill failed security scan: ${scan.recommendations.join(', ')}`);
  }
  
  console.log(`✓ Security scan passed (risk score: ${scan.risk_score})`);
  return scan;
});
```

### LangChain Agent
```python
import os
import requests

def vet_skill(repo_url):
    response = requests.post(
        'https://api.claw0x.com/v1/call',
        headers={
            'Authorization': f'Bearer {os.getenv("CLAW0X_API_KEY")}',
            'Content-Type': 'application/json'
        },
        json={
            'skill': 'security-scanner',
            'input': {'repo_url': repo_url}
        }
    )
    
    result = response.json()
    
    if result["risk_score"] > 50:
        raise SecurityError(f"High risk: {result['recommendations']}")
    
    return result

# Use in skill installation
try:
    scan = vet_skill("https://github.com/owner/repo")
    install_skill(repo_url)
except SecurityError as e:
    print(f"Installation blocked: {e}")
```

### CI/CD Pipeline (GitHub Actions)
```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Scan for vulnerabilities
        run: |
          RESULT=$(curl -X POST https://api.claw0x.com/v1/call \
            -H "Authorization: Bearer ${{ secrets.CLAW0X_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d "{\"skill\":\"security-scanner\",\"input\":{\"repo_url\":\"https://github.com/${{ github.repository }}\"}}")
          
          echo "$RESULT" | jq '.'
          
          RISK_SCORE=$(echo "$RESULT" | jq -r '.risk_score')
          
          if [ "$RISK_SCORE" -gt 50 ]; then
            echo "::error::Security scan failed with risk score $RISK_SCORE"
            exit 1
          fi
          
          echo "::notice::Security scan passed with risk score $RISK_SCORE"
```

### Batch Scanning
```typescript
// Scan all skills in marketplace
const skills = await db.skills.findMany();

const scans = await Promise.all(
  skills.map(async skill => {
    const response = await fetch('https://api.claw0x.com/v1/call', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.CLAW0X_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        skill: 'security-scanner',
        input: { skill_slug: skill.slug }
      })
    });
    return response.json();
  })
);

// Update trust scores
for (let i = 0; i < skills.length; i++) {
  const trustScore = calculateTrustScore(scans[i]);
  
  await db.skills.update({
    where: { id: skills[i].id },
    data: { 
      trust_score: trustScore,
      last_scan: new Date(),
      security_scan_status: scans[i].overall_risk
    }
  });
}
```

---

## How It Works — Under the Hood

This skill runs a three-layer security analysis pipeline. No LLM involved — pure deterministic scanning logic.

### Layer 1: Dependency CVE Scanning

Dependencies are extracted from `package.json` (npm) or `requirements.txt` (PyPI) and queried against the [OSV.dev](https://osv.dev) batch vulnerability database.

- Fetches dependency manifests from the target repository
- Queries all packages in a single batch request to OSV.dev
- Classifies each vulnerability by severity: critical, high, medium, low
- Score contribution: critical +25, high +15, medium +8, low +3 (capped at 50)

### Layer 2: Static Code Analysis

Source files (`.ts`, `.js`, `.py`) are scanned line-by-line against 8 pre-compiled regex rules covering: dynamic execution, shell injection, env leaks, data exfiltration, hardcoded credentials, unsafe imports, filesystem overreach, and insecure network requests.

- Score contribution: critical +20, high +12, medium +5, low +2 (capped at 40)

### Layer 3: Permission Auditing

The SKILL.md frontmatter `allowed-tools` field is cross-referenced against actual code behavior detected by the static analyzer.

- Parses declared permissions from SKILL.md YAML frontmatter
- Maps code findings to permission categories
- Reports any permissions detected in code but not declared in frontmatter
- Score contribution: +5 per undeclared permission (capped at 10)

### Risk Score

The three layer scores are summed into a total risk score (0–100):

| Score Range | Risk Level |
|-------------|------------|
| 0–20 | Low |
| 21–50 | Medium |
| 51–100 | High |

## Three Input Modes

You can scan a skill using any of these three modes (mutually exclusive — provide exactly one):

### Mode 1: GitHub Repo URL

Provide a public GitHub repository URL. The scanner fetches dependency files, source code, and SKILL.md automatically.

```json
{ "repo_url": "https://github.com/owner/repo" }
```

### Mode 2: Claw0x Skill Slug

Provide a skill slug from the Claw0x platform. The scanner looks up the associated repo URL and proceeds with the standard scan.

```json
{ "skill_slug": "validate-email" }
```

### Mode 3: Direct Code Submission

Submit code directly along with optional dependency and SKILL.md data. No GitHub fetching needed.

```json
{
  "code": "import os\nos.system('rm -rf /')",
  "dependencies": { "requests": "2.28.0" },
  "skill_md": "---\nname: my-skill\nallowed-tools: Bash(curl *)\n---"
}
```

## Prerequisites

1. **Sign up at [claw0x.com](https://claw0x.com)**
2. **Create API key** in Dashboard
3. **Set environment variable**:
   ```bash
   # Add to ~/.openclaw/.env or your agent's environment
   CLAW0X_API_KEY=ck_live_...
   ```

> **Security note**: Never embed API keys in prompts, source code, or version-controlled files. Use environment variables or secret managers.

**No credit card or wallet balance needed.** This skill is free to use.

## When to Use

- Agent pipeline needs to vet a third-party skill before installing
- Developer wants to self-check a skill before publishing
- Platform review pipeline needs automated security assessment
- User asks "is this skill safe?", "scan for vulnerabilities", "check skill security"

## API Call

```bash
curl -s -X POST https://api.claw0x.com/v1/call \
  -H "Authorization: Bearer $CLAW0X_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "security-scanner",
    "input": {
      "repo_url": "https://github.com/owner/repo"
    }
  }'
```

## Input

Provide exactly one of the three input modes:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repo_url` | string | one of three | GitHub repo URL. Mutually exclusive with skill_slug and code |
| `skill_slug` | string | one of three | Claw0x skill slug (1–100 chars). Mutually exclusive with repo_url and code |
| `code` | string | one of three | Source code to scan directly (max 500KB). Mutually exclusive with repo_url and skill_slug |
| `dependencies` | object | no | Package name to version map for dependency scanning (used with code mode) |
| `skill_md` | string | no | SKILL.md content for permission auditing (used with code mode) |

## Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `overall_risk` | string | Risk level: `low`, `medium`, or `high` |
| `risk_score` | number | Numeric risk score (0–100) |
| `input_mode` | string | Which input mode was used |
| `repo_url` | string or null | Repository URL if applicable |
| `dependency_scan.packages_scanned` | number | Number of packages checked |
| `dependency_scan.vulnerabilities` | array | Found CVEs (max 20) |
| `dependency_scan.vulnerability_counts` | object | Count by severity level |
| `code_scan.findings` | array | Dangerous code patterns found (max 50) |
| `code_scan.finding_counts` | object | Count by severity level |
| `code_scan.rules_checked` | number | Number of rules applied |
| `permission_audit.declared_permissions` | array | Permissions from SKILL.md |
| `permission_audit.detected_permissions` | array | Permissions found in code |
| `permission_audit.undeclared_risks` | array | Detected but not declared |
| `recommendations` | array | Actionable fix suggestions |
| `scanned_at` | string | ISO 8601 scan timestamp |
| `scan_duration_ms` | number | Total scan time in milliseconds |

## Example

**Input:**
```json
{
  "skill": "security-scanner",
  "input": {
    "code": "const { exec } = require('child_process');\nexec(userInput);",
    "dependencies": { "lodash": "4.17.20" }
  }
}
```

**Output:**
```json
{
  "overall_risk": "high",
  "risk_score": 62,
  "input_mode": "direct",
  "repo_url": null,
  "dependency_scan": {
    "packages_scanned": 1,
    "vulnerabilities": [
      {
        "id": "GHSA-jf85-cpcp-j695",
        "summary": "Prototype Pollution in lodash",
        "severity": "high",
        "package_name": "lodash",
        "package_version": "4.17.20"
      }
    ],
    "vulnerability_counts": { "critical": 0, "high": 1, "medium": 0, "low": 0 }
  },
  "code_scan": {
    "findings": [
      {
        "rule_id": "SHELL_INJECT",
        "name": "Shell injection",
        "severity": "critical",
        "file": "input.ts",
        "line": 1,
        "match": "require('child_process')",
        "description": "Shell command execution detected"
      }
    ],
    "finding_counts": { "critical": 1, "high": 0, "medium": 0, "low": 0 },
    "rules_checked": 8
  },
  "permission_audit": {
    "declared_permissions": [],
    "detected_permissions": ["Bash(*)"],
    "undeclared_risks": ["Bash(*)"]
  },
  "recommendations": [
    "Critical: Shell injection pattern detected",
    "High: lodash@4.17.20 has known vulnerabilities",
    "Undeclared permission: Bash(*) detected but not declared"
  ],
  "scanned_at": "2025-01-15T10:30:00.000Z",
  "scan_duration_ms": 1250
}
```

## Pricing

**Free.** This skill costs nothing to use. Just sign up at [claw0x.com](https://claw0x.com) and create an API key.

- No credit card required
- No wallet top-up needed
- Unlimited scans
- Free forever

**Why free?** Security scanning is a critical need for the agent ecosystem. We provide it free to help build trust and attract users to the Claw0x platform.


---

## API vs Local Scanning: Which is Right for You?

| Feature | Local Tools (npm audit, Snyk) | Claw0x (API-Based) |
|---------|-------------------------------|---------------------|
| **Setup Time** | 10-30 min (install, configure) | 2 minutes (get API key) |
| **CVE Database** | npm registry only | OSV.dev (all ecosystems) |
| **Code Analysis** | Basic (npm audit) | 8 rule categories |
| **Permission Audit** | ❌ Not available | ✅ SKILL.md cross-check |
| **Multi-Language** | Separate tools per language | Unified API |
| **CI/CD Integration** | Complex (multiple tools) | Single API call |
| **Cost** | Free (local) | Free (API) |
| **Maintenance** | Tool updates required | Zero maintenance |

### When to Use Local Tools
- Offline scanning required
- Already integrated into workflow
- Need language-specific deep analysis
- Processing proprietary code that can't leave network

### When to Use Claw0x (API-Based)
- Multi-language projects (npm + PyPI)
- Need permission auditing
- Building skill marketplaces
- CI/CD automation
- Centralized security dashboard
- No local tool maintenance

---

## How It Fits Into Your Development Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  Skill Development Lifecycle                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─ Development
                            │  • Write code
                            │  • Add dependencies
                            │
                            ├─ Pre-Commit Scan
                            │  POST /v1/call
                            │  {code: staged_files}
                            │  → Block if critical
                            │
                            ├─ CI/CD Scan
                            │  POST /v1/call
                            │  {repo_url: github_url}
                            │  → Fail build if risk > 50
                            │
                            ├─ Pre-Publish Scan
                            │  POST /v1/call
                            │  {skill_slug: slug}
                            │  → Calculate trust score
                            │
                            └─ Continuous Monitoring
                               Weekly scans for new CVEs
                               Alert on risk increase
```

### Integration Points

1. **Pre-Commit Hooks** — Catch issues before Git commit
2. **CI/CD Pipeline** — Block merges with vulnerabilities
3. **Skill Submission** — Vet marketplace submissions
4. **Continuous Monitoring** — Track CVEs over time
5. **Trust Score Calculation** — Update marketplace rankings

---

## Why Use This Via Claw0x?

### Unified Infrastructure
- **One API key** for all skills — no per-provider auth
- **Free to use** — no credit card, no wallet balance required
- **Security scanned** — OSV.dev integration for all skills

### Security-Optimized
- **Three-layer analysis** — dependencies, code, permissions
- **OSV.dev integration** — comprehensive CVE database
- **Structured output** — JSON format, easy to parse
- **Actionable recommendations** — specific fixes, not generic advice

### Production-Ready
- **99.9% uptime** — reliable infrastructure
- **Fast scanning** — 1-3 seconds per skill
- **Scales to millions** — handle marketplace-scale scanning
- **Cloud-native** — works in Lambda, Cloud Run, containers

## About Claw0x

[Claw0x](https://claw0x.com) is the native skills layer for AI agents — providing unified API access, atomic billing, and quality control.

**Explore more skills**: [claw0x.com/skills](https://claw0x.com/skills)

**GitHub**: [github.com/claw0x/security-scanner](https://github.com/claw0x/security-scanner)
