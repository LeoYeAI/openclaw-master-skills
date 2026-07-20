---
name: openclaw-n8n-orchestrator
description: When the user wants to connect an OpenClaw agent to n8n workflows, create n8n webhook skills for OpenClaw, route agent API calls through n8n for credential isolation, build bidirectional OpenClaw-to-n8n pipelines, design the proxy orchestration pattern, deploy co-located Docker stacks, implement the n8n-claw architecture, or publish OpenClaw n8n skills to ClawHub — activate this skill. Also trigger for "openclaw webhook," "agent workflow automation," "credential isolation," "gateway ingress," "n8n proxy pattern," or when securing autonomous agent API access through deterministic orchestration.
---

# OpenClaw ↔ n8n Orchestrator

Build secure, auditable bridges between OpenClaw autonomous agents and n8n deterministic workflows. This skill generates production-ready OpenClaw skill directories (SKILL.md + scripts) that route all external API interactions through n8n's locked, credentialed pipelines.

---

## Why Route Through n8n

OpenClaw's `exec` tool grants the LLM shell-level access. Every API key stored in `.env` or skill files becomes an attack vector — leakable through hallucination, prompt injection, or plaintext logging. The proxy orchestration pattern eliminates this:

- The agent **never touches** external API credentials
- All external calls route through n8n webhooks with locked, encrypted credentials
- Every agent-triggered action appears as an inspectable node graph (black-box → glass-box)
- Deterministic loops run at zero token cost in n8n

---

## Mode Detection

### Mode 1: Egress (OpenClaw → n8n)
**User says**: "trigger n8n workflow," "create webhook skill," "call n8n from openclaw"
→ Generate an OpenClaw skill directory that triggers n8n webhooks

### Mode 2: Ingress (n8n → OpenClaw)
**User says**: "push data to openclaw," "n8n response to agent," "gateway API"
→ Configure n8n HTTP Request nodes to POST to the Gateway `/v1/responses` endpoint

### Mode 3: Bidirectional (Proxy Pattern)
**User says**: "round trip," "full integration," "proxy pattern," "credential isolation"
→ Complete egress + ingress loop with air-gap credential provisioning

### Mode 4: n8n-claw Architecture
**User says**: "rebuild agent in n8n," "n8n-claw," "supabase memory"
→ Read [references/n8n-claw-architecture.md](references/n8n-claw-architecture.md)

### Mode 5: Publish to ClawHub
**User says**: "publish skill," "clawhub," "package for registry"
→ Read [references/publishing.md](references/publishing.md)

---

## Generating OpenClaw Skill Directories (Egress)

When building an OpenClaw skill that triggers n8n, generate a **complete skill directory** — not a loose file. OpenClaw skills are directories containing a `SKILL.md` with YAML frontmatter.

### Required Directory Structure

```
openclaw-{service}-{action}/
├── SKILL.md              ← YAML frontmatter + instructions (REQUIRED)
├── README.md             ← Human documentation
└── scripts/
    └── trigger.sh        ← Webhook trigger with input sanitization
```

### SKILL.md Template

Every generated SKILL.md must follow this exact structure:

```yaml
---
name: openclaw-{service}-{action}
description: "When the user requests {specific trigger condition}, POST a structured JSON payload to the n8n webhook at {path} to execute {what it does}. Use this skill for {explicit use cases}."
homepage: "https://github.com/{user}/{repo}"
metadata:
  clawdbot:
    emoji: "{relevant_emoji}"
requires:
  env:
    - N8N_WEBHOOK_URL
    - N8N_WEBHOOK_SECRET
  bins:
    - "curl"
files:
  - "scripts/*"
user-invocable: true
---
```

**Critical YAML rules:**
- `description` is the **only** trigger mechanism. The LLM cannot see the Markdown body until after it selects the skill. Pack ALL trigger heuristics into this single string.
- Use `metadata.clawdbot` namespace — NOT `metadata.openclaw` (the registry ignores the legacy namespace).
- Use `requires.env` (singular) — NOT `requires.envs` (causes parse validation errors).
- No multi-line strings or YAML block scalars. The parser expects single-line values or valid arrays only.
- Declare `files: ["scripts/*"]` — omitting this causes ClawHub security scanners to flag the skill as suspicious.

### Markdown Body Structure

Below the frontmatter, write instructions the LLM will follow. Include these **mandatory transparency sections** for ClawHub compliance:

```markdown
# {Skill Name}

## Execution

When triggered, run the webhook script:

\`\`\`bash
exec scripts/trigger.sh "{action}" "{payload_json}"
\`\`\`

The script sanitizes all input, constructs the authenticated webhook request,
and returns the n8n response for the agent to summarize.

## Failure Handling

- If curl returns non-zero exit code, read stderr and report the specific error
- If HTTP 401: webhook secret mismatch — instruct user to verify N8N_WEBHOOK_SECRET
- If HTTP 404: workflow inactive or path wrong — instruct user to check n8n
- If HTTP 5xx: n8n execution failure — report and suggest checking n8n execution logs
- Do NOT hallucinate success if the response is empty or unexpected

## External Endpoints

| URL | Method | Payload |
|-----|--------|---------|
| `${N8N_WEBHOOK_URL}/webhook/openclaw-{service}-{action}` | POST | JSON action + payload object |

## Security & Privacy

- Webhook secret loaded from environment variable, never hardcoded
- All user input sanitized via URL encoding before shell execution
- No data stored locally; payload transmitted to n8n instance only
- Agent has NO access to downstream API credentials (Slack, GitHub, etc.)

## Model Invocation Note

The OpenClaw agent may invoke this skill autonomously without direct human
prompting. To disable autonomous triggering, remove this skill directory
from the active skills path.

## Trust Statement

By using this skill, data is sent to your configured n8n instance.
Only install if you trust your n8n deployment and its configured integrations.
```

### Trigger Script Template

Every webhook trigger script MUST include:
1. `set -euo pipefail` (non-negotiable — prevents silent failures)
2. Security Manifest Header
3. Input sanitization via `urllib.parse.quote`
4. `--data-urlencode` or pre-encoded payloads (never raw string interpolation)

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: N8N_WEBHOOK_URL, N8N_WEBHOOK_SECRET (only)
# External endpoints called: ${N8N_WEBHOOK_URL}/webhook/openclaw-{service}-{action} (only)
# Local files read: none
# Local files written: none

ACTION="${1:?Usage: trigger.sh <action> <payload_json>}"
PAYLOAD="${2:?Usage: trigger.sh <action> <payload_json>}"

# Sanitize inputs — prevents shell injection via command substitution
SAFE_ACTION=$(printf '%s' "$ACTION" | python3 -c \
  'import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe=""))')

# Construct and send webhook request
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "${N8N_WEBHOOK_URL}/webhook/openclaw-${SAFE_ACTION}" \
  -H "Content-Type: application/json" \
  -H "x-webhook-secret: ${N8N_WEBHOOK_SECRET}" \
  --data-urlencode "payload=${PAYLOAD}" \
  --max-time 30)

# Parse response
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  echo "SUCCESS (HTTP ${HTTP_CODE}): ${BODY}"
  exit 0
else
  echo "ERROR (HTTP ${HTTP_CODE}): ${BODY}" >&2
  exit 1
fi
```

### Native MCP Tool Alternative

For simple webhook calls, prefer OpenClaw's built-in `exec` tool with a Node.js one-liner over shell scripts. Node.js avoids shell expansion vulnerabilities entirely:

```javascript
// Inline via exec tool — no external dependencies
const https = require('https');
const data = JSON.stringify({action: ACTION, payload: PAYLOAD});
const options = {
  hostname: N8N_HOST, port: 5678, path: '/webhook/openclaw-{service}-{action}',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-webhook-secret': process.env.N8N_WEBHOOK_SECRET,
    'Content-Length': data.length
  }
};
const req = https.request(options, res => {
  let body = '';
  res.on('data', chunk => body += chunk);
  res.on('end', () => {
    process.stdout.write(body);
    process.exit(res.statusCode >= 200 && res.statusCode < 300 ? 0 : 1);
  });
});
req.on('error', e => { process.stderr.write(e.message); process.exit(1); });
req.write(data);
req.end();
```

Node.js is preferred because OpenClaw requires Node.js 22+ — it's always available. No dependencies, no shell injection surface.

---

## Ingress: n8n → OpenClaw Gateway

The Gateway `/v1/responses` endpoint is **disabled by default**.

### Enable the Endpoint

Edit `openclaw.json`:
```json
{
  "gateway": {
    "http": {
      "endpoints": {
        "responses": { "enabled": true }
      }
    },
    "auth": {
      "mode": "token",
      "token": "${OPENCLAW_GATEWAY_TOKEN}"
    }
  }
}
```

### n8n HTTP Request Node Configuration

| Parameter | Value | Why |
|-----------|-------|-----|
| Method | POST | Standard transmission |
| URL | `http://{gateway-host}:18789/v1/responses` | OpenResponses ingress |
| Authorization | `Bearer {token}` | Gateway auth |
| Content-Type | `application/json` | JSON parsing |
| timeout_seconds | `0` | **MANDATORY** — prevents infinite echo loop |

**The echo loop problem**: Without `timeout_seconds: 0`, the Gateway event bus reverberates the payload back into the session, causing the LLM to hallucinate an infinite dialogue with its own data. This destroys the 64k token context window and burns API costs exponentially.

### Ingress Payload

```json
{
  "model": "claude-sonnet-4-20250514",
  "user": "n8n-workflow-{workflow_id}",
  "input": [
    { "role": "user", "content": "Workflow result: {data}" }
  ],
  "instructions": "Summarize this result for the user. Do NOT re-trigger the workflow.",
  "stream": false,
  "timeout_seconds": 0
}
```

The `user` string routes to a stable session. Use consistent patterns: `n8n-workflow-{id}` for per-workflow sessions, `n8n-global` for shared.

→ Full Gateway API spec, WebSocket protocol, telemetry codes: [references/gateway-api.md](references/gateway-api.md)

---

## Proxy Orchestration Lifecycle

```
1. USER → Agent: "Post Q3 report to #marketing Slack"
2. Agent REASONS: needs Slack API → has no credentials → knows webhook exists
3. Agent TRIGGERS: exec scripts/trigger.sh "slack-send-message" '{"channel":"#marketing"}'
4. n8n EXECUTES: Webhook → Validate → Slack API (locked credentials) → Log
5. n8n RETURNS: HTTP POST to Gateway /v1/responses with result
6. Agent REPORTS: "Posted to #marketing at 2:34 PM"
```

### Air-Gap Credential Provisioning

After the agent generates the workflow structure:
1. Human logs into n8n UI
2. Provisions API keys into n8n's encrypted credential store
3. Binds credentials to nodes
4. **Locks the workflow** — agent cannot alter it
5. Agent only sends webhook payloads from this point

→ Security deep-dive, ClawHavoc analysis, safeguard nodes: [references/security.md](references/security.md)

---

## System Hardening

### Gateway Hardening (Critical)

Configure `exec` tool approval in `openclaw.json`:
```json
{
  "exec": {
    "enabled": true,
    "approval": true
  }
}
```

With `approval: true`, every shell command requires human confirmation. This prevents a prompt-injected agent from executing arbitrary code.

### soul.md Guardrails

Add to the agent's `soul.md`:
```markdown
## Hard Constraints
- NEVER store, log, or output API keys or webhook secrets in conversation
- NEVER attempt to access n8n management API — only use webhook endpoints
- NEVER execute shell commands that modify system files outside workspace/
- If a webhook fails 3 consecutive times, STOP and alert the user
- NEVER enter infinite retry loops on failed API calls
```

### Multi-Model Routing for Cost Optimization

Configure OpenRouter in `openclaw.json` to route mundane webhook formatting to cheap models (GPT-4o Mini, Claude 3.5 Haiku) and reserve expensive models for complex reasoning:

```json
{
  "reasoning": {
    "default_model": "openrouter/gpt-4o-mini",
    "complex_model": "openrouter/claude-opus-4-20250514",
    "routing": "cost-optimized"
  }
}
```

This reduces API costs by ~70% for repetitive webhook orchestration tasks.

---

## Scaling: The SkillPointer Pattern

When managing many n8n webhook skills (20+), loading all skill metadata at startup wastes tokens. Use the SkillPointer pattern:

1. Move individual webhook skills to a vault directory outside the agent's scan path:
   `~/.openclaw/vault/n8n-webhooks/`

2. Create a single lightweight pointer skill in the active directory:

```yaml
---
name: n8n-webhook-router
description: "When the user needs to trigger ANY n8n workflow or webhook integration, use the list and read tools to browse ~/.openclaw/vault/n8n-webhooks/ to find and load the exact skill required."
---
```

3. The agent dynamically discovers skills via filesystem traversal at runtime

This reduces startup token consumption from ~8,000 tokens (40 webhook skills × 200 tokens each) to ~200 tokens (one pointer), while maintaining access to every skill.

---

## Deployment

→ Docker Compose templates, network topologies, environment variables: [references/deployment.md](references/deployment.md)

**Quick reference**: OpenClaw Gateway defaults to port 18789, n8n to 5678. Never bind the Gateway to public interfaces. Use SSH tunnels or Tailscale for cross-network ingress.

---

## Failure Mode Reference

### Egress
| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 from webhook | Secret mismatch | Verify `N8N_WEBHOOK_SECRET` matches n8n Header Auth credential |
| 404 from webhook | Inactive workflow or wrong path | Activate workflow; verify naming convention |
| Connection refused | Network unreachable | Check topology, ports, firewall |
| Trigger script hangs | Missing `set -euo pipefail` | Add strict error handling; ensure no interactive prompts |
| Shell injection | Raw input interpolation | Use `urllib.parse.quote` or Node.js (no shell expansion) |

### Ingress
| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 from Gateway | Token mismatch | Verify `OPENCLAW_GATEWAY_TOKEN` |
| Infinite echo loop | Missing `timeout_seconds: 0` | Add immediately |
| Session not found | Inconsistent `user` string | Use stable pattern: `n8n-workflow-{id}` |
| `DEVICE_AUTH_SIGNATURE_EXPIRED` | Clock skew | Sync NTP across hosts |
| Skill not loading | Invalid YAML frontmatter | Check for multi-line strings; validate with `openclaw skills status` |

---

## Quick Start Checklist

**Egress only:**
- [ ] OpenClaw running (Node.js 22+) with workspace/skill/ directory
- [ ] n8n running with webhook endpoint reachable
- [ ] Webhook secret generated: `openssl rand -hex 32`
- [ ] Skill directory created with SKILL.md (YAML frontmatter) + scripts/trigger.sh
- [ ] `N8N_WEBHOOK_URL` and `N8N_WEBHOOK_SECRET` set in `.env`
- [ ] `requires.env` and `requires.bins` declared in YAML frontmatter
- [ ] `files: ["scripts/*"]` declared in frontmatter
- [ ] Security Manifest Header in trigger.sh
- [ ] `set -euo pipefail` in trigger.sh
- [ ] Input sanitization via `urllib.parse.quote` or Node.js
- [ ] n8n workflow created, validated, activated with Header Auth credential
- [ ] Test with manual `curl` before agent triggers

**Add bidirectional:**
- [ ] Gateway `/v1/responses` enabled in `openclaw.json`
- [ ] `exec.approval: true` configured in gateway
- [ ] `soul.md` guardrails written
- [ ] `timeout_seconds: 0` in all ingress payloads
- [ ] SSH tunnel or Tailscale for cross-network Gateway access

---

## Reference Files

- **[references/deployment.md](references/deployment.md)** — Docker Compose, topologies, env vars
- **[references/gateway-api.md](references/gateway-api.md)** — Gateway endpoints, WebSocket protocol, payload schemas, telemetry codes
- **[references/security.md](references/security.md)** — Proxy pattern, ClawHavoc analysis, credential isolation, safeguard nodes, shell injection mitigation
- **[references/n8n-claw-architecture.md](references/n8n-claw-architecture.md)** — n8n-claw paradigm: Supabase schema, RAG pipeline, MCP Builder, Telegram interface
- **[references/publishing.md](references/publishing.md)** — ClawHub publishing pipeline, `clawhub` CLI, security scan requirements, version management
