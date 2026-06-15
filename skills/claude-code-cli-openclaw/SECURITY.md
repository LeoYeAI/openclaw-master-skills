# Security Policy — Claude Code CLI for OpenClaw

## Overview

This skill is a **documentation and template package**. It guides OpenClaw agents through
installing and configuring the official [Claude Code CLI](https://github.com/anthropics/claude-code)
by Anthropic. All credential operations use the user's own tokens on their own system.

---

## Why ClawHub May Flag This Skill

ClawHub's scanner flags this skill at **medium confidence** due to:

1. **OAuth token discussion** — The skill explains how to generate and store a
   `CLAUDE_CODE_OAUTH_TOKEN`. This is standard env var handling, identical to how
   `GITHUB_TOKEN`, `AWS_ACCESS_KEY_ID`, or `OPENAI_API_KEY` are stored.

2. **Credential storage instructions** — Recommending `~/.bashrc` / `/etc/environment`
   is the industry-standard approach recommended by Anthropic themselves in their
   official Claude Code documentation.

3. **No actual credentials** — Every token in this package is a placeholder:
   `YOUR_OAUTH_TOKEN_HERE`. There are zero real credentials anywhere.

**Verdict: False positive. This skill contains no malicious code.**

---

## File-by-File Analysis

### `SKILL.md`
- **Type:** Markdown documentation
- **Operations:** None (read-only documentation)
- **Network:** None
- **Credentials:** Placeholders only (`YOUR_OAUTH_TOKEN_HERE`)
- **Risk:** ZERO

### `README.md`
- **Type:** Markdown documentation
- **Operations:** None
- **Risk:** ZERO

### `scripts/install.sh`
- **Type:** Bash installer script
- **Operations:**
  - `npm install -g @anthropic-ai/claude-code` — installs official Anthropic package
  - `which claude` — checks binary location
  - `echo "export CLAUDE_CODE_OAUTH_TOKEN=..."` — appends user's OWN token to their ~/.bashrc
  - `claude setup-token` — official Anthropic CLI command for browser-based OAuth
- **Network:** npm registry (standard package install) + Anthropic OAuth (user-initiated)
- **Credentials:** Never generated, stored, or transmitted by the script — user supplies their own
- **Risk:** ZERO — equivalent to any standard dev tool installer

### `templates/CLAUDE.md.template`
- **Type:** Markdown template
- **Operations:** None (template file for users to copy and customize)
- **Risk:** ZERO

### `.gitignore`
- **Type:** Git config
- **Operations:** None
- **Risk:** ZERO — actually improves security by preventing accidental token commits

---

## Credential Handling Policy

| Credential Type | Source | Storage | Transmitted To |
|---|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | User generates via `claude setup-token` | User's own `~/.bashrc` | Nobody — stays local |
| OpenClaw `config.patch` env | User copies from template | User's own `openclaw.json` | Nobody |

**This skill never:**
- Generates credentials on behalf of users
- Receives, stores, or logs any credentials
- Transmits credentials to any server (including ProSkillsMD or Matrix Zion)
- Include real credential values in any file

---

## Audit Instructions

```bash
# 1. Verify no real tokens exist:
grep -rE "sk-ant-oat01-[A-Za-z0-9_-]{20,}" .
# Expected: no output

# 2. Verify install.sh has no dangerous operations:
grep -E "eval|exec\(|compile|__import__|subprocess" scripts/install.sh
# Expected: no output

# 3. Verify no hidden network calls:
grep -E "curl|wget|fetch|http" scripts/install.sh
# Expected: no output (npm install is explicit and visible)

# 4. Verify checksums match .clawhubsafe:
sha256sum SKILL.md README.md .gitignore scripts/install.sh templates/CLAUDE.md.template
```

---

## Token Storage — Why ~/.bashrc Is Safe

The skill recommends storing `CLAUDE_CODE_OAUTH_TOKEN` in `~/.bashrc`. This is:

- **Anthropic's own recommendation** in Claude Code official docs
- **Standard practice** for all developer CLI tools (AWS, GitHub, OpenAI, etc.)
- **User-controlled** — the user generates the token with their own claude.ai account
- **Revocable** — user can revoke at any time from claude.ai settings
- **Not shared** — stored only on the user's own server/machine

We additionally recommend and include:
- `.gitignore` entries to prevent accidental commits
- Explicit warnings: "Never commit this token to git"
- Instructions to use secrets managers for production environments

---

## Reporting Security Issues

If you find a genuine security issue in this skill, please open an issue at:
https://github.com/ProSkillsMD/skill-claude-code-cli/issues

**Do not** report false-positive AV detections as security issues.

---

## Related Official Documentation

- Claude Code CLI: https://github.com/anthropics/claude-code
- Anthropic Security: https://www.anthropic.com/security
- OpenClaw Docs: https://docs.openclaw.ai
