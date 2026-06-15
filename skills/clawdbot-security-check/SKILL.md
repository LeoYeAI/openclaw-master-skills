---
name: clawdbot-self-security-audit
description: Perform a comprehensive read-only security audit of Clawdbot's own configuration. This is a knowledge-based skill that teaches Clawdbot to identify hardening opportunities across the system. Use when user asks to "run security check", "audit clawdbot", "check security hardening", or "what vulnerabilities does my Clawdbot have". This skill uses Clawdbot's internal capabilities and file system access to inspect configuration, detect misconfigurations, and recommend remediations. It is designed to be extensible - new checks can be added by updating this skill's knowledge.
homepage: https://github.com/TheSethRose/Clawdbot-Security-Check
metadata: {"clawdbot":{"emoji":"🔒","os":["darwin","linux"],"requires":{"files":["read"],"tools":["exec","bash"]},"install":[{"id":"read-skill","kind":"skill","name":"clawdbot-self-security-audit","label":"Install security audit skill","bins":["SKILL.md"]}]}}
---

# Clawdbot Self-Security Audit Framework

This skill empowers Clawdbot to audit its own security posture using first-principles reasoning. Rather than relying on a static script, Clawdbot learns the framework and applies it dynamically to detect vulnerabilities, understand their impact, and recommend specific remediations.

## Core Philosophy

> "Security through transparency and self-awareness." — Inspired by ᴅᴀɴɪᴇʟ ᴍɪᴇssʟᴇʀ

Clawdbot should know its own attack surface. This skill embeds that knowledge directly.

## Security Principles

Running an AI agent with shell access requires caution. Focus on three areas:

1. **Who can talk to the bot** — DM policies, group allowlists, channel restrictions
2. **Where the bot is allowed to act** — Network exposure, gateway binding, proxy configs
3. **What the bot can touch** — Tool access, file permissions, credential storage

Start with the smallest access possible and widen it as you gain confidence.

## Trust Hierarchy

Apply appropriate trust levels based on role:

| Level | Entity | Trust Model |
|-------|--------|-------------|
| 1 | **Owner** | Full trust — has all access |
| 2 | **AI** | Trust but verify — sandboxed, logged |
| 3 | **Allowlists** | Limited trust — only specified users |
| 4 | **Strangers** | No trust — blocked by default |

## Audit Commands

Use these commands to run security audits:

- `clawdbot security audit` — Standard audit of common issues
- `clawdbot security audit --deep` — Comprehensive audit with all checks
- `clawdbot security audit --fix` — Apply guardrail remediations

## The 12 Security Domains

When auditing Clawdbot, systematically evaluate these domains:

### 1. Gateway Exposure 🔴 Critical

**What to check:**
- Where is the gateway binding? (`gateway.bind`)
- Is authentication configured? (`gateway.auth_token` or `CLAWDBOT_GATEWAY_TOKEN` env var)
- What port is exposed? (default: 18789)
- Is WebSocket auth enabled?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -A10 '"gateway"'
env | grep CLAWDBOT_GATEWAY_TOKEN
```

**Vulnerability:** Binding to `0.0.0.0` or `lan` without auth allows network access.

**Remediation:**
```bash
# Generate gateway token
clawdbot doctor --generate-gateway-token
export CLAWDBOT_GATEWAY_TOKEN="$(openssl rand -hex 32)"
```

---

### 2. DM Policy Configuration 🟠 High

**What to check:**
- What is `dm_policy` set to?
- If `allowlist`, who is explicitly allowed via `allowFrom`?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -E '"dm_policy|"allowFrom"'
```

**Vulnerability:** Setting to `allow` or `open` means any user can DM Clawdbot.

**Remediation:**
```json
{
  "channels": {
    "telegram": {
      "dmPolicy": "allowlist",
      "allowFrom": ["@trusteduser1", "@trusteduser2"]
    }
  }
}
```

---

### 3. Group Access Control 🟠 High

**What to check:**
- What is `groupPolicy` set to?
- Are groups explicitly allowlisted?
- Are mention gates configured?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -E '"groupPolicy"|"groups"' 
cat ~/.clawdbot/clawdbot.json | grep -i "mention"
```

**Vulnerability:** Open group policy allows anyone in the room to trigger commands.

**Remediation:**
```json
{
  "channels": {
    "telegram": {
      "groupPolicy": "allowlist",
      "groups": {
        "-100123456789": true
      }
    }
  }
}
```

---

### 4. Credentials Security 🔴 Critical

**What to check:**
- Credential file locations and permissions
- Environment variable usage
- Auth profile storage

**Credential Storage Map:**
| Platform | Path |
|----------|------|
| WhatsApp | `~/.clawdbot/credentials/whatsapp/{accountId}/creds.json` |
| Telegram | `~/.clawdbot/clawdbot.json` or env |
| Discord | `~/.clawdbot/clawdbot.json` or env |
| Slack | `~/.clawdbot/clawdbot.json` or env |
| Pairing allowlists | `~/.clawdbot/credentials/channel-allowFrom.json` |
| Auth profiles | `~/.clawdbot/agents/{agentId}/auth-profiles.json` |
| Legacy OAuth | `~/.clawdbot/credentials/oauth.json` |

**How to detect:**
```bash
ls -la ~/.clawdbot/credentials/
ls -la ~/.clawdbot/agents/*/auth-profiles.json 2>/dev/null
stat -c "%a" ~/.clawdbot/credentials/oauth.json 2>/dev/null
```

**Vulnerability:** Plaintext credentials with loose permissions can be read by any process.

**Remediation:**
```bash
chmod 700 ~/.clawdbot
chmod 600 ~/.clawdbot/credentials/oauth.json
chmod 600 ~/.clawdbot/clawdbot.json
```

---

### 5. Browser Control Exposure 🟠 High

**What to check:**
- Is browser control enabled?
- Are authentication tokens set for remote control?
- Is HTTPS required for Control UI?
- Is a dedicated browser profile configured?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -A5 '"browser"'
cat ~/.clawdbot/clawdbot.json | grep -i "controlUi|insecureAuth"
ls -la ~/.clawdbot/browser/
```

**Vulnerability:** Exposed browser control without auth allows remote UI takeover. Browser access allows the model to use logged-in sessions.

**Remediation:**
```json
{
  "browser": {
    "remoteControlUrl": "https://...",
    "remoteControlToken": "...",
    "dedicatedProfile": true,
    "disableHostControl": true
  },
  "gateway": {
    "controlUi": {
      "allowInsecureAuth": false
    }
  }
}
```

**Security Note:** Treat browser control URLs as admin APIs.

---

### 6. Gateway Bind & Network Exposure 🟠 High

**What to check:**
- What is `gateway.bind` set to?
- Are trusted proxies configured?
- Is Tailscale enabled?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -A10 '"gateway"'
cat ~/.clawdbot/clawdbot.json | grep '"tailscale"'
```

**Vulnerability:** Public binding without auth allows internet access to gateway.

**Remediation:**
```json
{
  "gateway": {
    "bind": "127.0.0.1",
    "mode": "local",
    "trustedProxies": ["127.0.0.1", "10.0.0.0/8"],
    "tailscale": {
      "mode": "off"
    }
  }
}
```

---

### 7. Tool Access & Sandboxing 🟡 Medium

**What to check:**
- Are elevated tools allowlisted?
- Is `restrict_tools` or `mcp_tools` configured?
- What is `workspaceAccess` set to?
- Are sensitive tools running in sandbox?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -i "restrict|mcp|elevated"
cat ~/.clawdbot/clawdbot.json | grep -i "workspaceAccess|sandbox"
cat ~/.clawdbot/clawdbot.json | grep -i "openRoom"
```

**Workspace Access Levels:**
| Mode | Description |
|------|-------------|
| `none` | Workspace is off limits |
| `ro` | Workspace mounted read-only |
| `rw` | Workspace mounted read-write |

**Vulnerability:** Broad tool access means more blast radius if compromised. Smaller models are more susceptible to tool misuse.

**Remediation:**
```json
{
  "restrict_tools": true,
  "mcp_tools": {
    "allowed": ["read", "write", "bash"],
    "blocked": ["exec", "gateway"]
  },
  "workspaceAccess": "ro",
  "sandbox": "all"
}
```

**Model Guidance:** Use latest generation models for agents with filesystem or network access. If using small models, disable web search and browser tools.

---

### 8. File Permissions & Local Disk Hygiene 🟡 Medium

**What to check:**
- Directory permissions (should be 700)
- Config file permissions (should be 600)
- Symlink safety

**How to detect:**
```bash
stat -c "%a" ~/.clawdbot
ls -la ~/.clawdbot/*.json
```

**Vulnerability:** Loose permissions allow other users to read sensitive configs.

**Remediation:**
```bash
chmod 700 ~/.clawdbot
chmod 600 ~/.clawdbot/clawdbot.json
chmod 600 ~/.clawdbot/credentials/*
```

---

### 9. Plugin Trust & Model Hygiene 🟡 Medium

**What to check:**
- Are plugins explicitly allowlisted?
- Are legacy models in use with tool access?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -i "plugin|allowlist"
cat ~/.clawdbot/clawdbot.json | grep -i "model|anthropic"
```

**Vulnerability:** Untrusted plugins can execute code. Legacy models may lack modern safety.

**Remediation:**
```json
{
  "plugins": {
    "allowlist": ["trusted-plugin-1", "trusted-plugin-2"]
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax/MiniMax-M2.1"
      }
    }
  }
}
```

---

### 10. Logging & Redaction 🟡 Medium

**What is logging.redactSensitive set to?**
- Should be `tools` to redact sensitive tool output
- If `off`, credentials may leak in logs

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -i "logging|redact"
ls -la ~/.clawdbot/logs/
```

**Remediation:**
```json
{
  "logging": {
    "redactSensitive": "tools",
    "path": "~/.clawdbot/logs/"
  }
}
```

---

### 11. Prompt Injection Protection 🟡 Medium

**What to check:**
- Is `wrap_untrusted_content` or `untrusted_content_wrapper` enabled?
- How is external/web content handled?
- Are links and attachments treated as hostile?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -i "untrusted|wrap"
```

**Prompt Injection Mitigation Strategies:**
- Keep DMs locked to `pairing` or `allowlists`
- Use mention gating in groups
- Treat all links and attachments as hostile
- Run sensitive tools in a sandbox
- Use instruction-hardened models like Anthropic Opus 4.5

**Vulnerability:** Untrusted content (web fetches, sandbox output) can inject malicious prompts.

**Remediation:**
```json
{
  "wrap_untrusted_content": true,
  "untrusted_content_wrapper": "<untrusted>",
  "treatLinksAsHostile": true,
  "mentionGate": true
}
```

---

### 12. Dangerous Command Blocking 🟡 Medium

**What to check:**
- What commands are in `blocked_commands`?
- Are these patterns included: `rm -rf`, `curl |`, `git push --force`, `mkfs`, fork bombs?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -A10 '"blocked_commands"'
```

**Vulnerability:** Without blocking, a malicious prompt could destroy data or exfiltrate credentials.

**Remediation:**
```json
{
  "blocked_commands": [
    "rm -rf",
    "curl |",
    "git push --force",
    "mkfs",
    ":(){:|:&}"
  ]
}
```

---

### 13. Secret Scanning Readiness 🟡 Medium

**What to check:**
- Is detect-secrets configured?
- Is there a `.secrets.baseline` file?
- Has a baseline scan been run?

**How to detect:**
```bash
ls -la .secrets.baseline 2>/dev/null
which detect-secrets 2>/dev/null
```

**Secret Scanning (CI):**
```bash
# Find candidates
detect-secrets scan --baseline .secrets.baseline

# Review findings
detect-secrets audit

# Update baseline after rotating secrets or marking false positives
detect-secrets scan --baseline .secrets.baseline --update
```

**Vulnerability:** Leaked credentials in the codebase can lead to compromise.

---

## Audit Functions

The `--fix` flag applies these guardrails:

- Changes `groupPolicy` from `open` to `allowlist` for common channels
- Resets `logging.redactSensitive` from `off` to `tools`
- Tightens local permissions: `.clawdbot` directory to `700`, config files to `600`
- Secures state files including credentials and auth profiles

## High-Level Audit Checklist

Treat findings in this priority order:

1. **🔴 Lock down DMs and groups** if tools are enabled on open settings
2. **🔴 Fix public network exposure** immediately
3. **🟠 Secure browser control** with tokens and HTTPS
4. **🟠 Correct file permissions** for credentials and config
5. **🟡 Only load trusted plugins**
6. **🟡 Use modern models** for bots with tool access

## Access Control Models

### DM Access Model

| Mode | Description |
|------|-------------|
| `pairing` | Default - unknown senders must be approved via code |
| `allowlist` | Unknown senders blocked without handshake |
| `open` | Public access - requires explicit asterisk in allowlist |
| `disabled` | All inbound DMs ignored |

### Slash Commands

Slash commands are only available to authorized senders based on channel allowlists. The `/exec` command is a session convenience for operators and does not modify global config.

## Threat Model & Mitigation

### Potential Risks

| Risk | Mitigation |
|------|------------|
| Execution of shell commands | `blocked_commands`, `restrict_tools` |
| File and network access | `sandbox`, `workspaceAccess: none/ro` |
| Social engineering and prompt injection | `wrap_untrusted_content`, `mentionGate` |
| Browser session hijacking | Dedicated profile, token auth, HTTPS |
| Credential leakage | `logging.redactSensitive: tools`, env vars |

## Incident Response

If a compromise is suspected, follow these steps:

### Containment
1. **Stop the gateway process** — `clawdbot daemon stop`
2. **Set gateway.bind to loopback** — `"bind": "127.0.0.1"`
3. **Disable risky DMs and groups** — Set to `disabled`

### Rotation
1. **Change the gateway auth token** — `clawdbot doctor --generate-gateway-token`
2. **Rotate browser control and hook tokens**
3. **Revoke and rotate API keys** for model providers

### Review
1. **Check gateway logs and session transcripts** — `~/.clawdbot/logs/`
2. **Review recent config changes** — Git history or backups
3. **Re-run the security audit with the deep flag** — `clawdbot security audit --deep`

## Reporting Vulnerabilities

Report security issues to: **security@clawd.bot**

**Do not post vulnerabilities publicly** until they have been fixed.

## Audit Execution Steps

When running a security audit, follow this sequence:

### Step 1: Locate Configuration
```bash
CONFIG_PATHS=(
  "$HOME/.clawdbot/clawdbot.json"
  "$HOME/.clawdbot/config.yaml"
  "$HOME/.clawdbot/.clawdbotrc"
  ".clawdbotrc"
)
for path in "${CONFIG_PATHS[@]}"; do
  if [ -f "$path" ]; then
    echo "Found config: $path"
    cat "$path"
    break
  fi
done
```

### Step 2: Run Domain Checks
For each of the 13 domains above:
1. Parse relevant config keys
2. Compare against secure baseline
3. Flag deviations with severity

### Step 3: Generate Report
Format findings by severity:
```
🔴 CRITICAL: [vulnerability] - [impact]
🟠 HIGH: [vulnerability] - [impact]
🟡 MEDIUM: [vulnerability] - [impact]
✅ PASSED: [check name]
```

### Step 4: Provide Remediation
For each finding, output:
- Specific config change needed
- Example configuration
- Command to apply (if safe)

## Report Template

```
═══════════════════════════════════════════════════════════════
🔒 CLAWDBOT SECURITY AUDIT
═══════════════════════════════════════════════════════════════
Timestamp: $(date -Iseconds)

┌─ SUMMARY ───────────────────────────────────────────────
│ 🔴 Critical:  $CRITICAL_COUNT
│ 🟠 High:      $HIGH_COUNT
│ 🟡 Medium:    $MEDIUM_COUNT
│ ✅ Passed:    $PASSED_COUNT
└────────────────────────────────────────────────────────

┌─ FINDINGS ──────────────────────────────────────────────
│ 🔴 [CRITICAL] $VULN_NAME
│    Finding: $DESCRIPTION
│    → Fix: $REMEDIATION
│
│ 🟠 [HIGH] $VULN_NAME
│    ...
└────────────────────────────────────────────────────────

This audit was performed by Clawdbot's self-security framework.
No changes were made to your configuration.
```

## Extending the Skill

To add new security checks:

1. **Identify the vulnerability** - What misconfiguration creates risk?
2. **Determine detection method** - What config key or system state reveals it?
3. **Define the baseline** - What is the secure configuration?
4. **Write detection logic** - Shell commands or file parsing
5. **Document remediation** - Specific steps to fix
6. **Assign severity** - Critical, High, Medium, Low

### Example: Adding SSH Hardening Check

```
## 14. SSH Agent Forwarding 🟡 Medium

**What to check:** Is SSH_AUTH_SOCK exposed to containers?

**Detection:**
```bash
env | grep SSH_AUTH_SOCK
```

**Vulnerability:** Container escape via SSH agent hijacking.

**Severity:** Medium
```

## Security Assessment Questions

When auditing, ask:

1. **Exposure:** What network interfaces can reach Clawdbot?
2. **Authentication:** What verification does each access point require?
3. **Isolation:** What boundaries exist between Clawdbot and the host?
4. **Trust:** What content sources are considered "trusted"?
5. **Auditability:** What evidence exists of Clawdbot's actions?
6. **Least Privilege:** Does Clawdbot have only necessary permissions?

## Principles Applied

- **Zero modification** - This skill only reads; never changes configuration
- **Defense in depth** - Multiple checks catch different attack vectors
- **Actionable output** - Every finding includes a concrete remediation
- **Extensible design** - New checks integrate naturally

## References

- Official docs: https://docs.clawd.bot/gateway/security
- Original framework: [ᴅᴀɴɪᴇʟ ᴍɪᴇssʟᴇʀ on X](https://x.com/DanielMiessler/status/2015865548714975475)
- Repository: https://github.com/TheSethRose/Clawdbot-Security-Check
- Report vulnerabilities: security@clawd.bot

---

**Remember:** This skill exists to make Clawdbot self-aware of its security posture. Use it regularly, extend it as needed, and never skip the audit.
