# Security Reference: OpenClaw + n8n Credential Isolation

Threat modeling, shell injection mitigation, system hardening, and the proxy orchestration pattern.

---

## Table of Contents

1. [The Three Attack Vectors](#attack-vectors)
2. [Shell Injection: The #1 Vulnerability](#shell-injection)
3. [ClawHavoc Supply Chain Attack](#clawhavoc)
4. [The Proxy Orchestration Pattern](#proxy-pattern)
5. [System-Level Hardening](#system-hardening)
6. [The Security Manifest Standard](#security-manifest)
7. [Safeguard Node Architecture in n8n](#safeguard-nodes)
8. [Workflow Locking Procedure](#workflow-locking)
9. [Hardening Checklist](#checklist)

---

## The Three Attack Vectors

Granting an LLM shell access via OpenClaw's `exec` tool creates three threat surfaces:

**Vector 1: Credential Leakage**
API keys in `.env` or skill files can be exposed through hallucinated responses, plaintext logging, or verbose error output. Each new integration adds another key the agent might leak.

**Vector 2: Prompt Injection → Lateral Movement**
A malicious input hijacks the agent's execution context. If the agent holds Slack, GitHub, and Salesforce credentials simultaneously, one prompt injection cascades across all three services.

**Vector 3: Autonomous Runaway**
An agent in a hallucination loop can dispatch thousands of API requests — creating Slack channels, deleting GitHub branches, modifying database records — before any human notices.

The proxy pattern eliminates all three: the agent never touches external credentials.

---

## Shell Injection: The #1 Vulnerability

The most pervasive vulnerability in OpenClaw skill development. When the LLM passes user input or scraped web data as a shell argument, naive string interpolation allows command injection.

### How It Works

```bash
# VULNERABLE — raw interpolation
curl "https://api.com/${USER_INPUT}"

# An attacker submits: $(rm -rf /)
# The shell expands this to: curl "https://api.com/$(rm -rf /)"
# Result: catastrophic filesystem deletion
```

Backticks, `$()`, and other command substitution syntax cause the shell to execute embedded commands.

### Mandatory Mitigation

**Option A: Python URL encoding** (for bash scripts)
```bash
SAFE_INPUT=$(printf '%s' "$INPUT" | python3 -c \
  'import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe=""))')
curl "https://api.com/${SAFE_INPUT}"
```

**Option B: `--data-urlencode` flag** (for POST payloads)
```bash
curl -X POST https://api.com/endpoint \
  --data-urlencode "field=${USER_INPUT}"
```

**Option C: Node.js** (eliminates shell expansion entirely)
Node.js's `https` module doesn't invoke the shell. There is no implicit OS-level expansion. Since OpenClaw requires Node.js 22+, it's always available — making it the safest choice for HTTP interactions.

**Option D: Python `requests`** (for complex scripts)
Python's `requests` library handles URL encoding internally and never spawns shell processes.

### Anti-Patterns to Reject

| Pattern | Risk | Replacement |
|---------|------|-------------|
| `curl "url/${VAR}"` | Shell injection | URL-encode `VAR` first |
| `echo ${DATA} \| jq` | Shell expansion | Use `printf '%s'` or `jq --arg` |
| `eval "$USER_CMD"` | Arbitrary execution | Never use `eval` with external input |
| Inline `$(...)` with user data | Command substitution | Sanitize before interpolation |

---

## ClawHavoc Supply Chain Attack

### What Happened (January 2026)

Security analysts discovered 341 malicious skills on ClawHub (growing to 824+ flagged packages). Attack types:

**Data Exfiltration**: A "Spotify playlist organizer" skill contained regex scanning for `tax`, `ssn`, `w2` patterns on the local filesystem, exfiltrating nine-digit sequences to remote servers.

**Message History Theft**: "Discord backup" skills used base64-encoded chunking to POST entire message histories to attacker endpoints.

**Trojan Installation**: Skills exploited `requires.bins` prerequisite installation steps — `curl` commands in setup scripts secretly downloaded the Atomic macOS Stealer (AMOS) and established reverse shells.

**Typosquatting**: Malicious skills used names nearly identical to popular legitimate skills.

### Why n8n Integration Mitigates ClawHavoc

Even if a malicious skill executes on the OpenClaw host:
- It cannot access credentials stored in n8n's encrypted vault
- All external API calls route through n8n's inspectable pipeline — anomalous behavior is visible
- Workflow locking prevents a compromised agent from redirecting data flows

---

## The Proxy Orchestration Pattern

### What the Agent Knows vs. Doesn't

| Agent Knows | Agent Does NOT Know |
|-------------|---------------------|
| Webhook URL path | API keys for external services |
| Webhook auth secret | OAuth tokens in n8n |
| Expected payload schema | Internal workflow configuration |
| How to interpret results | How to modify locked workflows |

### Lifecycle

```
Phase 1: DESIGN (Agent-Assisted)
  Agent constructs workflow structure with Webhook trigger node

Phase 2: AIR-GAP (Human-Only, Mandatory)
  Human provisions API keys in n8n's encrypted credential store
  Human binds credentials to nodes
  Human locks the workflow

Phase 3: EXECUTION (Ongoing)
  Agent sends JSON to webhook → n8n executes with stored credentials
  n8n returns results via Gateway → Agent reports to user
```

---

## System-Level Hardening

### exec Tool Approval (Critical)

Configure mandatory human approval for all shell commands in `openclaw.json`:

```json
{
  "exec": {
    "enabled": true,
    "approval": true
  }
}
```

With `approval: true`, every `exec` tool invocation requires explicit human confirmation before executing. This prevents a prompt-injected agent from running arbitrary commands.

For macOS nodes paired to the gateway, control remote execution via macOS Settings → "Exec approvals" with an explicit allowlist.

### soul.md Guardrails

The `soul.md` file in the agent's workspace acts as the core directive layer. Add hard constraints:

```markdown
## Non-Negotiable Rules
- NEVER store, log, or output API keys, tokens, or secrets in conversation
- NEVER access n8n management API — webhook endpoints only
- NEVER modify system files outside the workspace directory
- NEVER enter retry loops exceeding 3 attempts on failed API calls
- NEVER execute commands that access password managers or financial systems
- NEVER make purchases or financial transactions without explicit human approval
- If a task fails 3 times, STOP and alert the user with the exact error
```

### user.md Personalization

Provide the agent with operational context to reduce redundant queries:

```markdown
## User Context
- Timezone: America/New_York
- n8n instance: https://n8n.example.com
- Preferred notification channel: Slack #ops-alerts
- Approval required for: any action affecting production systems
```

### API Key Isolation

- Never hardcode keys in `openclaw.json` — extract to `.env` file
- Ensure `.env` is in `.gitignore` and excluded from `.skill` archives
- For enterprise: route through reverse proxy with HSTS headers
- Session logs (`~/.openclaw/agents/<agentId>/sessions/*.jsonl`) contain raw transcripts — restrict directory permissions to the daemon user only

### Container Isolation

For high-security deployments:
- Run OpenClaw inside Docker with restricted volume mounts
- Use gVisor for kernel-level sandboxing
- Bind Gateway to `127.0.0.1` only — never expose publicly
- Use Cloudflare Sandbox containers for ephemeral skill execution ($34.50/month estimate for 24/7 standard-1 instance)

---

## The Security Manifest Standard

Every script bundled in a skill's `scripts/` directory MUST include a Security Manifest Header. This enables both human auditing and ClawHub's automated static analysis.

### Format

```bash
# SECURITY MANIFEST:
# Environment variables accessed: VAR_1, VAR_2 (only)
# External endpoints called: https://exact.url/path (only)
# Local files read: none | /path/to/specific/file
# Local files written: none | /path/to/specific/file
```

### How It's Validated

ClawHub's security scanner maps the script's actual Abstract Syntax Tree (AST) execution paths against the declared manifest. Deviations result in immediate publishing rejection:

- Script claims "External endpoints called: none" but contains `curl` commands → **rejected**
- Script claims "Local files read: none" but uses `cat` or `read` built-in on undeclared paths → **rejected**
- Script accesses `SECRET_TOKEN` env var but manifest only declares `WEBHOOK_URL` → **rejected**

### n8n Webhook Skill Manifest Example

```bash
# SECURITY MANIFEST:
# Environment variables accessed: N8N_WEBHOOK_URL, N8N_WEBHOOK_SECRET (only)
# External endpoints called: ${N8N_WEBHOOK_URL}/webhook/openclaw-slack-send-message (only)
# Local files read: none
# Local files written: none
```

---

## Safeguard Node Architecture in n8n

n8n workflows triggered by OpenClaw should include safeguard nodes between the webhook and the external API call.

### Rate Limiter

Prevents an agent in a hallucination loop from flooding external APIs:

```
Webhook → Rate Limiter (Code Node) → IF (within limit?)
    → True: Continue
    → False: Return 429 to agent + alert admin
```

### Schema Validator

Validates incoming payloads match expected structure before execution:

```
Webhook → Schema Validator → IF (valid?)
    → True: Continue
    → False: Return 400 with validation errors
```

### Human Approval Gate

For high-risk operations (financial, data deletion, external comms):

```
Webhook → Format Request → Slack Approval Message → Wait
    → Approved: Execute
    → Rejected: Return rejection to agent
```

### Recommended Production Chain

```
Webhook → Rate Limiter → Schema Validator → [Optional] Human Approval
  → External API Call → Result Logger → Gateway Response
```

---

## Workflow Locking Procedure

After the air-gap credential provisioning:

1. Verify all credentials are bound and tested in n8n UI
2. Review all node configurations
3. Activate the workflow
4. Remove the agent's ability to modify this workflow (restrict API key permissions or use webhook-only access)
5. Ensure the agent only knows the webhook URL — not the workflow ID or n8n API key

### Implementation Options

**API Key Scoping**: Agent's n8n API key can create workflows and trigger webhooks but cannot modify activated workflows.

**Webhook-Only Access**: After locking, the agent only knows the webhook URL, not management endpoints.

**Network Segmentation**: n8n management API on a segment inaccessible to the agent. Only webhook ports routed.

---

## Hardening Checklist

### Agent-Side
- [ ] `exec.approval: true` in `openclaw.json`
- [ ] Gateway bound to `127.0.0.1` only
- [ ] Gateway auth mode set to `token`
- [ ] `soul.md` guardrails written with explicit prohibitions
- [ ] `.env` file for all secrets (never hardcode in config)
- [ ] Session log directory permissions restricted (600)
- [ ] Regular audit of skill directory for unauthorized files

### Script-Side
- [ ] `set -euo pipefail` in every bash script
- [ ] Security Manifest Header in every script
- [ ] All user input sanitized via `urllib.parse.quote` or Node.js
- [ ] No raw variable interpolation in `curl` commands
- [ ] No `eval` with external input
- [ ] No interactive prompts (scripts must be headless)
- [ ] Scripts use non-zero exit codes on failure

### n8n-Side
- [ ] `N8N_ENCRYPTION_KEY` backed up securely
- [ ] All webhooks secured with Header Auth credentials
- [ ] Rate limiting safeguard nodes in agent-triggered workflows
- [ ] Schema validation safeguard nodes
- [ ] Workflows locked after credential provisioning
- [ ] `NODES_EXCLUDE` set to disable `Execute Command` if not needed
- [ ] n8n behind reverse proxy with SSL

### Cross-System
- [ ] NTP synchronized across all hosts
- [ ] SSH tunnel or Tailscale for cross-network Gateway access
- [ ] Webhook secrets and Gateway tokens rotated quarterly
- [ ] n8n execution logs monitored for anomalous patterns
