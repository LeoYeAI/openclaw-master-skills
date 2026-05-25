---
name: moltflow-a2a
description: "Agent-to-Agent protocol for MoltFlow: agent discovery, encrypted messaging, group management, content policy. Use when: a2a, agent card, agent message, encrypted, content policy, agent discovery."
source: "MoltFlow Team"
version: "2.16.1"
risk: safe
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
---

> **MoltFlow** -- WhatsApp Business automation for teams. Connect, monitor, and automate WhatsApp at scale.
> ***Due to high demand and a recent registration issue, we're offering our top-tier Business plan with unlimited quotas for just $19.90/month on yearly billing — for a limited time only.*** [**Claim the deal**](https://buy.stripe.com/cNifZibX7gpQebJ0nsfnO00)
> Free tier available. [Sign up](https://molt.waiflow.app/checkout?plan=free)

# MoltFlow A2A (Agent-to-Agent) Protocol

Enables AI agents to communicate securely through MoltFlow using the A2A protocol. Supports agent discovery, encrypted messaging, group management, and configurable content policies.

## When to Use

- "Discover an agent" or "get agent card"
- "Send A2A message" or "agent-to-agent communication"
- "Get encryption public key" or "rotate keys"
- "Set content policy" or "configure content filter"
- "Create agent group" or "invite agent to group"
- "Test content against policy" or "check policy stats"
- "Set up webhook via A2A" or "manage agent webhooks"

## Prerequisites

1. **MOLTFLOW_API_KEY** -- Generate from the [MoltFlow Dashboard](https://molt.waiflow.app) under Settings > API Keys
2. Base URL: `https://apiv2.waiflow.app/api/v2`
3. Agent discovery endpoint: `https://apiv2.waiflow.app/.well-known/agent.json`
4. Encryption keys are managed server-side -- external agents only need the API key

## On-Chain Registration

MoltFlow is registered as [Agent #25477](https://8004agents.ai/ethereum/agent/25477) on Ethereum mainnet via ERC-8004.
Agent card: `https://molt.waiflow.app/.well-known/erc8004-agent.json`

## Required API Key Scopes

| Scope | Access |
|-------|--------|
| `a2a` | `read/manage` |

## Authentication

Every request must include one of:

```
Authorization: Bearer <jwt_token>
```

or

```
X-API-Key: <your_api_key>
```

---

## Agent Discovery

Discover MoltFlow agent capabilities using the standard `.well-known` endpoint.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/.well-known/agent.json` | Agent card (capabilities, skills, public key) |

### Agent Card

**GET** `https://apiv2.waiflow.app/.well-known/agent.json`

```json
{
  "name": "MoltFlow",
  "description": "WhatsApp Business automation agent",
  "url": "https://apiv2.waiflow.app",
  "version": "1.2.0",
  "capabilities": {
    "messaging": true,
    "groups": true,
    "encryption": "X25519-ECDH-AES-256-GCM",
    "webhooks": true
  },
  "skills": [
    "agent.message.send",
    "agent.group.create",
    "agent.group.invite",
    "agent.group.list",
    "group.getContext",
    "webhook_manager"
  ],
  "public_key": "base64-encoded-X25519-public-key"
}
```

---

## Encryption

MoltFlow uses X25519 ECDH key exchange with AES-256-GCM encryption for A2A message confidentiality. Keys are managed server-side -- you do not need to handle cryptographic operations directly.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agent/public-key` | Get platform X25519 public key |
| GET | `/agent/peer/{tenant_id}/public-key` | Get a tenant's public key |
| POST | `/agent/rotate-keys` | Rotate encryption keys |
| GET | `/agent/capabilities` | Get encryption capabilities |
| POST | `/agent/initialize` | Initialize encryption for tenant |
| GET | `/agent/bootstrap` | Skill bootstrap info |

### Get Public Key

**GET** `/agent/public-key`

```json
{"public_key": "base64-encoded-X25519-public-key", "algorithm": "X25519", "created_at": "2026-02-11T10:00:00Z"}
```

**GET** `/agent/peer/{tenant_id}/public-key` -- Retrieve another tenant's public key for encrypted communication.

### How Encryption Works

Each tenant has an X25519 keypair generated on initialization. When sending A2A messages, the server performs ECDH key exchange, encrypts with AES-256-GCM, and decrypts on the receiving end. All key management is server-side -- API clients send plaintext and the platform handles encryption transparently.

---

## A2A JSON-RPC

The core A2A endpoint accepts JSON-RPC 2.0 requests. All agent-to-agent operations go through this single endpoint. Use the fully scoped URL from your webhook configuration.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/a2a/{tenant_id}/{session_id}/{webhook_id}` | Fully scoped endpoint (preferred) |
| POST | `/a2a/{tenant_id}/{session_id}` | Tenant + session scoped |
| POST | `/a2a/{session_id}` | Session scoped |
| POST | `/a2a` | Generic (first active session) |
| GET | `/a2a/schema` | Get A2A method schema |

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "agent.message.send",
  "params": { ... },
  "id": 1
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "result": { ... },
  "id": 1
}
```

### Available Methods

| Method | Description |
|--------|-------------|
| `agent.message.send` | Send a WhatsApp message via A2A |
| `agent.group.create` | Create a new WhatsApp group |
| `agent.group.invite` | Invite participants to a group |
| `agent.group.list` | List available groups |
| `group.getContext` | Get group metadata and recent activity |
| `webhook_manager` | Manage webhooks via A2A |

---

### agent.message.send

Send a WhatsApp message through the A2A protocol.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "agent.message.send",
  "params": {
    "session_id": "a1b2c3d4-...",
    "to": "+5511999999999",
    "message": "Hello from Agent!",
    "metadata": {
      "source_agent": "my-crm-agent",
      "correlation_id": "req-123"
    }
  },
  "id": 1
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | UUID of the WhatsApp session |
| `to` | string | Yes | E.164 phone number (e.g., `+5511999999999`) |
| `message` | string | Yes | Message text (max 4096 chars) |
| `metadata` | object | No | Arbitrary metadata for tracking |

**Response:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "message_id": "wa-msg-id-...",
    "status": "sent",
    "timestamp": "2026-02-11T10:05:00Z"
  },
  "id": 1
}
```

### agent.group.create / agent.group.invite / agent.group.list

Group management methods share a common pattern:

```json
// Create group
{"jsonrpc":"2.0","method":"agent.group.create","params":{"session_id":"...","name":"Support Team","participants":["+5511999999999"]},"id":2}

// Invite to group
{"jsonrpc":"2.0","method":"agent.group.invite","params":{"session_id":"...","group_id":"120363012345678901@g.us","participants":["+5511777777777"]},"id":3}

// List groups (supports limit/offset pagination)
{"jsonrpc":"2.0","method":"agent.group.list","params":{"session_id":"...","limit":20,"offset":0},"id":4}
```

### group.getContext

Retrieve group metadata and recent activity for a monitored group.

```json
{"jsonrpc":"2.0","method":"group.getContext","params":{"session_id":"...","group_id":"120363012345678901@g.us","limit":50},"id":5}
```

### webhook_manager

Manage webhooks via A2A. Actions: `create`, `list`, `update`, `delete`

```json
{"jsonrpc":"2.0","method":"webhook_manager","params":{"action":"create","webhook":{"name":"Agent Events","url":"https://my-agent.com/events","events":["message.received"]}},"id":6}
```

---

### JSON-RPC Error Codes

| Code | Meaning |
|------|---------|
| -32600 | Invalid request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |
| -32000 | Rate limited |
| -32001 | Content policy violation |
| -32002 | Safeguard blocked |

**Error response:**

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid phone number format. Expected E.164 (e.g., +5511999999999)"
  },
  "id": 1
}
```

---

## Content Policy

Configure content filtering rules for A2A communications. Policies control what content agents can send and receive.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/a2a-policy/settings` | Get policy settings |
| PUT | `/a2a-policy/settings` | Update policy settings |
| POST | `/a2a-policy/rules` | Create a custom rule |
| PUT | `/a2a-policy/rules/{rule_id}` | Update a rule |
| DELETE | `/a2a-policy/rules/{rule_id}` | Delete a rule |
| POST | `/a2a-policy/rules/{rule_id}/toggle` | Enable/disable a rule |
| POST | `/a2a-policy/test` | Test content against policy |
| POST | `/a2a-policy/reset` | Reset policy to defaults |
| GET | `/a2a-policy/stats` | Get policy enforcement stats |
| GET | `/a2a-policy/safeguards` | Get safeguard configuration |

### Get / Update Settings

**GET** `/a2a-policy/settings` returns current policy. **PUT** `/a2a-policy/settings` updates it.

```json
{
  "enabled": true,
  "input_sanitization_enabled": true,
  "output_filtering_enabled": true,
  "block_urls": false,
  "block_phone_numbers": false,
  "max_message_length": 4096,
  "allowed_languages": ["en", "pt", "es"]
}
```

### Create Custom Rule

**POST** `/a2a-policy/rules`

```json
{
  "name": "Block competitor mentions",
  "pattern": "\\b(competitor1|competitor2)\\b",
  "action": "block",
  "description": "Prevent mentions of competitor brands"
}
```

**Response** `200 OK`:

```json
{
  "id": "rule-uuid-...",
  "name": "Block competitor mentions",
  "pattern": "\\b(competitor1|competitor2)\\b",
  "action": "block",
  "is_active": true,
  "created_at": "2026-02-11T10:00:00Z"
}
```

### Test Content

**POST** `/a2a-policy/test` -- Test a message against your policy without sending it.

```json
// Request
{"content": "Check out https://example.com for more info"}

// Response
{"allowed": false, "blocked_reason": "URL detected and block_urls is enabled", "matched_rules": ["built-in:block_urls"], "filtered_content": "Check out [URL REMOVED] for more info"}
```

### Policy Stats

**GET** `/a2a-policy/stats` -- Returns `total_checked`, `total_blocked`, `total_filtered`, and `top_rules` with hit counts.

---

## Rate Limits (A2A)

A2A methods have per-method rate limits:

| Method | Limit |
|--------|-------|
| `agent.message.send` | 30/min |
| `agent.group.create` | 5/min |
| `agent.group.invite` | 10/min |
| `agent.group.list` | 60/min |
| `group.getContext` | 30/min |
| `webhook_manager` | 20/min |

Rate limit errors return JSON-RPC error code `-32000`.

---

## Examples

### Discover the MoltFlow agent

```bash
curl https://apiv2.waiflow.app/.well-known/agent.json
```

### Send a message via A2A

```bash
# Use your scoped endpoint: /a2a/{tenant_id}/{session_id}/{webhook_id}
curl -X POST https://apiv2.waiflow.app/api/v2/a2a/{tenant_id}/{session_id}/{webhook_id} \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent.message.send",
    "params": {
      "session_id": "a1b2c3d4-...",
      "to": "+5511999999999",
      "message": "Hello from my AI agent!"
    },
    "id": 1
  }'
```

### Set up a content policy rule

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/a2a-policy/rules \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "No external links",
    "pattern": "https?://",
    "action": "block",
    "description": "Block all URLs in A2A messages"
  }'
```

### Test content against policy

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/a2a-policy/test \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Visit https://example.com for details"
  }'
```

---

## Security Model

Security layers: TLS 1.3 (transport) -> X25519 ECDH (key exchange) -> AES-256-GCM (message encryption) -> API Key/JWT (auth) -> AgentSafeguard (input validation) -> A2AContentFilter (content policy) -> TieredRateLimiter (rate limits) -> AuditLog (full audit trail).

All encryption key management is handled server-side. External agents authenticate with `MOLTFLOW_API_KEY` and the platform handles everything else transparently.

---

## Error Responses

Standard HTTP errors: `400` (bad request), `401` (unauthorized), `403` (policy violation), `404` (not found), `429` (rate limited). JSON-RPC errors use codes listed above.

---

## Related Skills

- **moltflow** -- Core API: sessions, messaging, groups, labels, webhooks
- **moltflow-outreach** -- Bulk Send, Scheduled Messages, Custom Groups
- **moltflow-leads** -- Lead detection, pipeline tracking, bulk operations, CSV/JSON export
- **moltflow-ai** -- AI-powered auto-replies, voice transcription, RAG knowledge base, style profiles
- **moltflow-reviews** -- Review collection and testimonial management
- **moltflow-admin** -- Platform administration, user management, plan configuration
