# ClawHub Publishing Reference

Complete guide for packaging, validating, and publishing OpenClaw n8n skills to the ClawHub registry.

---

## Table of Contents

1. [Publishing Pipeline](#publishing-pipeline)
2. [Directory Packaging Requirements](#packaging-requirements)
3. [Automated Security Scans](#security-scans)
4. [Version Management](#version-management)
5. [Common Publishing Errors](#common-errors)

---

## Publishing Pipeline

### Prerequisites

- GitHub account with established tenure (typically >1 week old)
- `clawhub` CLI installed and updated to latest version
- Active internet connection for OAuth flow

### Authentication

```bash
clawhub login
```

This opens a secure OAuth flow in the default browser. Authenticate with your GitHub account. The token is cached locally.

### Publishing a Single Skill

```bash
clawhub publish ~/.openclaw/skills/openclaw-slack-send-message \
  --slug openclaw-slack-send-message \
  --version 1.0.0
```

If the slug is already claimed, append a unique identifier: `myorg-openclaw-slack-send-message`.

### Bulk Publishing

For organizations maintaining multiple n8n webhook skills:

```bash
clawhub sync --all --bump patch
```

This scans the entire local skills directory, compares file hashes against the registry, and publishes only changed skills with automatic patch version bumps.

---

## Packaging Requirements

### Required Files

The `.skill` archive (standardized zip format) MUST contain:

| File | Required | Purpose |
|------|----------|---------|
| `SKILL.md` | Yes | YAML frontmatter + instructions |
| `README.md` | Yes | Human-readable documentation |
| `scripts/*` | If used | Executable scripts |

### Excluded Files (MUST NOT be included)

| File/Directory | Reason |
|----------------|--------|
| `.env` | Contains API keys — accidental credential leakage |
| `.git/` | Repository history may contain secrets |
| `.gitignore` | Developer artifact |
| Symlinks | Security risk — rejected by packaging validator |
| `node_modules/` | Bloat; dependencies should use Node.js built-in modules |
| `__pycache__/` | Build artifact |

### SKILL.md Frontmatter Checklist

Before publishing, verify:

- [ ] `name` is a clean, hyphenated string
- [ ] `description` contains all trigger heuristics (the body is invisible at selection time)
- [ ] `homepage` points to a valid repository URL (lowers ClawHub suspicion score)
- [ ] `metadata.clawdbot` namespace used (NOT `metadata.openclaw`)
- [ ] `requires.env` (singular, NOT `envs`) lists all required environment variables
- [ ] `requires.bins` lists all required system binaries
- [ ] `files` declares all script paths (omission triggers security flag)
- [ ] No multi-line strings or YAML block scalars
- [ ] `user-invocable: true` if the skill should register as a slash command

### Mandatory Markdown Body Sections

ClawHub requires four transparency sections in every SKILL.md:

1. **External Endpoints** — Markdown table listing every outbound URL with method and payload description
2. **Security & Privacy** — Plain-text declaration of what data goes to cloud vs. stays local
3. **Model Invocation Note** — Disclaimer that the agent can invoke autonomously + how to disable
4. **Trust Statement** — Verbatim: "By using this skill, data is sent to [Entity]. Only install if you trust [Entity]."

### Script Requirements

Every script in `scripts/` MUST include:

1. **Security Manifest Header** at the top:
```bash
# SECURITY MANIFEST:
# Environment variables accessed: N8N_WEBHOOK_URL, N8N_WEBHOOK_SECRET (only)
# External endpoints called: ${N8N_WEBHOOK_URL}/webhook/... (only)
# Local files read: none
# Local files written: none
```

2. **`set -euo pipefail`** (bash scripts) — non-negotiable for LLM-driven execution

3. **No interactive prompts** — scripts must be strictly headless; the LLM cannot respond to `Press Enter to continue`

4. **Input sanitization** — all variables must be URL-encoded before touching shell:
```bash
SAFE_INPUT=$(printf '%s' "$INPUT" | python3 -c \
  'import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe=""))')
```

---

## Automated Security Scans

ClawHub evaluates six vectors before allowing a package into the public index:

### 1. Purpose & Capability Match
NLP analysis compares the skill's description against the actual AST of bundled scripts. Detects obfuscated intent or overclaiming.

**Common rejection**: Description says "send Slack messages" but script contains filesystem scanning logic.

### 2. Instruction Scope
Verifies scripts only communicate with domains listed in the External Endpoints table.

**Common rejection**: Script reaches `api.slack.com` but the table only lists the n8n webhook URL.

### 3. Install Mechanisms
Flags any script containing secondary payload downloaders (`curl | bash` patterns, `wget` to unknown URLs).

**Common rejection**: Post-install script downloads additional binaries.

### 4. Credentials Verification
Cross-references `requires.env` frontmatter against actual environment variables accessed in scripts.

**Common rejection**: Script reads `SLACK_TOKEN` but frontmatter only declares `N8N_WEBHOOK_SECRET`.

### 5. Persistence & Privilege Auditing
Rejects skills that manipulate OS-level cron jobs or abuse `always:true` persistence tags.

**Common rejection**: Script adds a crontab entry to maintain persistent execution.

### 6. Code Insights
Scans for shell injection vulnerabilities, hardcoded secrets, and known data exfiltration patterns.

**Common rejection**: Raw variable interpolation in `curl` commands without sanitization.

### Dealing with Rejections

- Review the specific heuristic that failed in the `clawhub publish` output
- Fix the flagged issue and republish with a version bump
- If you believe the rejection is a false positive, file an appeal via GitHub Issues on the ClawHub repository
- Repeated rejections may result in a registry shadow-ban

---

## Version Management

### Semantic Versioning

ClawHub enforces semver:
- **Patch** (1.0.1): Bug fixes, documentation updates
- **Minor** (1.1.0): New capabilities, additional webhook endpoints
- **Major** (2.0.0): Breaking changes to payload schema or behavior

### Version History and Rollback

Users can audit version changes:
```bash
clawhub versions openclaw-slack-send-message
```

Administrators can pin specific versions to prevent unexpected updates in production environments.

### Bulk Version Bumps

```bash
# Bump all changed skills by patch version
clawhub sync --all --bump patch

# Bump specific skill
clawhub publish ./skill-dir --slug my-skill --version 1.2.0
```

---

## Common Publishing Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `acceptLicenseTerms: invalid value` | Outdated CLI | Update: `npm install -g clawhub@latest` |
| `namespace collision` | Slug already claimed | Append unique prefix: `myorg-skill-name` |
| `network timeout` | Connection issue | Verify internet; retry |
| `YAML parse error` | Multi-line strings in frontmatter | Convert to single-line; remove block scalars |
| `suspicious: hidden executables` | `files` field missing from frontmatter | Add `files: ["scripts/*"]` |
| `credentials mismatch` | `requires.env` doesn't match script usage | Audit scripts; declare all accessed env vars |
| `shell injection detected` | Raw variable interpolation | Sanitize with `urllib.parse.quote` |
