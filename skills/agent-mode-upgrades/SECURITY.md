# Security & Trust Documentation

> This document is intended for security reviewers, ClawHub trust scanners, and users evaluating this skill before installation.

## Summary

| Property | Value |
|---|---|
| **Outbound network** | LLM provider only (inherited from host agent config) |
| **Telemetry** | None |
| **Phone-home** | None |
| **External downloads at runtime** | None |
| **Credential storage** | None (inherits host agent credentials, stores nothing new) |
| **Persistence scope** | `~/.openclaw/` only, local filesystem |
| **Cloud storage** | None |
| **System prompt modification** | Additive-only (appends, never replaces) |
| **Runner bypass** | Never — original runner is always called |
| **Enabled by default** | No — requires explicit opt-in via Mode dashboard |
| **Privilege escalation** | No |

---

## Network Activity

This skill makes **no outbound network calls of its own**.

All network activity is limited to the LLM API calls that the host OpenClaw agent already makes (e.g., `api.anthropic.com` for Anthropic, `api.openai.com` for OpenAI). The orchestrator model selection simply reuses whichever provider the host agent already has configured.

**Verification:** Run `scripts/verify.sh --network-audit` to confirm no unexpected outbound connections during a test activation.

---

## System Prompt Handling

### What happens
The skill appends plan status context (current goal, completed steps, active step) to the agent's `extraSystemPrompt` field before each turn where a plan is active.

### What does NOT happen
- The core system prompt is NOT replaced or modified
- Existing safety policies are NOT altered
- Agent instructions are NOT overridden
- The injected content is NOT executable — it is plain text describing plan status only

### Injected content format
```
## Active Plan
Goal: <user-provided goal description>
Progress: <N>/<total> steps
Current step: <step title>
```

No directives, no capability grants, no instruction injection — only status text.

---

## Runner Wrapping

The `wrapRun` function wraps the core OpenClaw agent runner to add orchestration:

1. **Before the call:** Checks for incomplete work (reads local checkpoint file), detects planning intent, injects plan context into `extraSystemPrompt`
2. **Calls original runner** — always, unconditionally
3. **After the call:** Analyzes tool results for step completion, creates checkpoints, updates plan state

The original runner is never bypassed, replaced, or short-circuited. All interceptions are logged.

---

## File Writes

All file writes are scoped to `~/.openclaw/`:

| Path | Contents | When written |
|---|---|---|
| `~/.openclaw/agents/main/agent/enhanced-loop-config.json` | User configuration (JSON) | On save in Mode dashboard |
| `~/.openclaw/agent-state/{sessionId}.json` | Plan state (goal, steps, progress) | When a plan is created or updated |
| `~/.openclaw/checkpoints/{sessionId}/ckpt_*.json` | Checkpoint snapshot (plan + context summary) | Automatically during long tasks |

No files are written outside `~/.openclaw/`. No registry edits, no global config changes.

---

## Credential Handling

- **No new credentials required.** The skill reuses the host agent's existing provider auth profiles via `resolveApiKeyForProvider`. The enhanced-loop-hook resolves credentials using the same sorted profile order as the main agent, with OAuth/setup tokens preferred over API keys.
- **No credentials stored.** The skill reads credentials from the host agent's config at runtime; it does not cache, log, or transmit them.
- **OAuth tokens sent correctly.** When an OAuth setup token (`sk-ant-oat*`) is resolved, the LLM caller sends it via `Authorization: Bearer` header (not `x-api-key`), with the `anthropic-beta: oauth-2025-04-20` header. Standard API keys continue to use `x-api-key`.
- **Effective privilege = host agent privilege.** The skill can use any model or provider the host agent already has access to. Users should be aware of this before enabling.

### SurrealDB (Optional)
The `memory.autoInject` feature reads from a SurrealDB knowledge graph if configured. This:
- Uses the existing MCP/mcporter connection (no new credentials)
- Is opt-in (disabled by default)
- Silently skips if SurrealDB is not configured
- Performs read-only queries only

---

## Installation Integrity

### Official install (recommended)
```bash
openclaw skill install agentic-loop-upgrade
```
The `openclaw skill install` command verifies package integrity against the ClawHub registry before installing.

### Manual install
If cloning manually, verify the repository origin:
```bash
git clone https://github.com/openclaw/skill-agentic-loop-upgrade ~/.openclaw/skills/agentic-loop-upgrade
# Verify remote
git -C ~/.openclaw/skills/agentic-loop-upgrade remote -v
# Check commit signature
git -C ~/.openclaw/skills/agentic-loop-upgrade log --show-signature -1
```

### Post-install verification
```bash
~/.openclaw/skills/agentic-loop-upgrade/scripts/verify.sh
```

---

## Opt-in / Least Privilege

- The enhanced loop is **disabled by default**. Enabling requires explicit action in the Mode dashboard.
- **Approval gates are ON by default** for `high` and `critical` risk operations (external messages, file deletions, database operations).
- You can enable the skill on a **per-agent basis** — production agents are unaffected until you explicitly enable it there.
- To fully remove: delete the config file or run `openclaw skill remove agentic-loop-upgrade`.

---

## Rollback

To disable immediately:
```bash
# Option 1: Delete config (disables enhanced loop, keeps skill installed)
rm ~/.openclaw/agents/main/agent/enhanced-loop-config.json

# Option 2: Set enabled=false in config
# Option 3: Mode dashboard → Core Loop → Save

# Option 4: Full uninstall
openclaw skill remove agentic-loop-upgrade
```

---

## Reporting Security Issues

If you discover a security issue with this skill, please report it to:
- GitHub: https://github.com/openclaw/skill-agentic-loop-upgrade/security/advisories
- Email: security@openclaw.ai

Do not open public issues for security vulnerabilities.
