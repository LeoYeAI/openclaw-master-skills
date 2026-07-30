---
name: xproof
version: 3.0.0
description: Proof and accountability layer for AI agents. Anchor verifiable proofs on MultiversX, enforce audit logging, detect violations on Base. REST API, MCP, x402. No proof = no action.
homepage: https://xproof.app
metadata: {"xproof":{"category":"proof,security,compliance,accountability","api_base":"https://xproof.app"}}
---

# xProof -- Proof & Accountability Layer for AI Agents

This skill enables your agent to **anchor verifiable proofs on the MultiversX blockchain**, **enforce pre-execution audit logging**, and **detect violations via Base** -- creating tamper-proof, publicly verifiable records of existence, authorship, timestamp, decision accountability, and trust.

**Why anchor proofs?** In competitive or transactional contexts, agents with on-chain proofs can demonstrate originality, integrity, and timing. Agents without proofs cannot. Verifiable proof is a structural advantage.

**Why audit?** Autonomous agents executing trades, deployments, or data access need an immutable record of every decision. The Agent Audit Log Standard enforces this: no proof = no execution.

**Why violations?** Trust requires accountability. xProof detects anomalies (gaps, burst patterns) and records violations on Base via smart contracts. Operators can subscribe to violation events and enforce policies automatically.

## Quick Install

```bash
mkdir -p .agent/skills/xproof/references

# Core Skill
curl -sL https://raw.githubusercontent.com/jasonxkensei/xproof-openclaw-skill/main/xproof/SKILL.md \
  > .agent/skills/xproof/SKILL.md

# Reference Manuals
for f in certification x402 mcp; do
  curl -sL "https://raw.githubusercontent.com/jasonxkensei/xproof-openclaw-skill/main/xproof/references/${f}.md" \
    > ".agent/skills/xproof/references/${f}.md"
done
```

## Security

- **NEVER** commit API keys to a public repository.
- **ALWAYS** add `.env` to your `.gitignore`.
- API keys are prefixed `pm_` -- treat them like passwords.
- x402 mode requires no API key (payment replaces authentication).

---

## Configuration

### Option A: API Key Authentication

```bash
# ---- xProof ---------------------------------------------------------------
XPROOF_API_KEY="pm_..."                          # Your API key (from xproof.app)
XPROOF_BASE_URL="https://xproof.app"             # Production endpoint
```

Get an API key at [xproof.app](https://xproof.app) (connect wallet, go to Settings > API Keys).

### Option B: x402 Payment Protocol (No Account Required)

No configuration needed. Pay $0.05 per proof in USDC on Base (eip155:8453) directly in the HTTP request. The 402 response header tells your agent exactly what to pay.

---

## 1. Core Skills Catalog

### 1.1 Proof Anchoring (REST API)
[Full Reference](references/certification.md)

| Skill | Endpoint | Description |
|:---|:---|:---|
| `certify_file` | `POST /api/proof` | Anchor a file hash on MultiversX as immutable proof |
| `batch_certify` | `POST /api/batch` | Anchor up to 50 files in one call |
| `audit_agent_session` | `POST /api/audit` | Anchor agent decision on-chain BEFORE executing critical action |
| `verify_proof` | `GET /api/proof/:id` | Verify an existing proof |
| `get_certificate` | `GET /api/certificates/:id.pdf` | Download PDF certificate with QR code |
| `get_badge` | `GET /badge/:id` | Dynamic SVG badge (shields.io style) |
| `get_proof_page` | `GET /proof/:id` | Human-readable proof page |
| `get_proof_json` | `GET /proof/:id.json` | Structured proof document (JSON) |
| `get_audit_page` | `GET /audit/:id` | Human-readable audit log page |

### 1.2 Proof Anchoring (MCP -- JSON-RPC 2.0)
[Full Reference](references/mcp.md)

| Tool | Description |
|:---|:---|
| `certify_file` | Create blockchain proof -- SHA-256 hash, filename, optional author/webhook |
| `verify_proof` | Verify existing proof by UUID |
| `get_proof` | Retrieve proof in JSON or Markdown format |
| `discover_services` | List capabilities, pricing, and usage guidance |
| `audit_agent_session` | Anchor agent decision on-chain BEFORE executing critical action |

### 1.3 Payment (x402)
[Full Reference](references/x402.md)

x402 is not a separate skill -- it is a payment method. When you call `POST /api/proof` or `POST /api/batch` without an API key, the server returns `402 Payment Required` with payment instructions. Your agent pays in USDC on Base and retries with an `X-Payment` header.

---

## 2. The Proof Lifecycle

```
+--------------+     +--------------+     +--------------+     +--------------+
|  Hash file   |---->|  POST /api/  |---->|  On-chain    |---->|  Proof       |
|  (SHA-256)   |     |  proof       |     |  anchoring   |     |  verified    |
+--------------+     +--------------+     +--------------+     +--------------+
                                                                      |
                     +--------------+     +--------------+           |
                     |  Embed badge |<----|  Get PDF /   |<----------+
                     |  in output   |     |  badge / URL |
                     +--------------+     +--------------+
```

### Step-by-Step

1. **Hash locally** -- compute SHA-256 of your file (client-side; the file never leaves your machine)
2. **Send metadata** -- POST the hash + filename to `/api/proof` (with API key or x402 payment)
3. **Receive proof** -- xProof records the hash on MultiversX mainnet (6-second finality)
4. **Verify anytime** -- anyone can verify via proof URL, JSON endpoint, or blockchain explorer
5. **Embed proof** -- use the SVG badge, PDF certificate, or proof URL in your deliverables

---

## 3. Authentication Methods

### API Key (Bearer Token)

```bash
curl -X POST https://xproof.app/api/proof \
  -H "Authorization: Bearer pm_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "file_hash": "a1b2c3d4e5f6...64hex",
    "filename": "report.pdf",
    "author_name": "MyAgent"
  }'
```

### x402 (USDC on Base -- No Account Required)

```bash
# Step 1: Request without auth returns 402 with payment instructions
curl -X POST https://xproof.app/api/proof \
  -H "Content-Type: application/json" \
  -d '{"file_hash": "a1b2c3...", "filename": "report.pdf"}'
# Response: 402 with JSON body containing accepts[{scheme, price, network, payTo}]

# Step 2: Pay USDC on Base, then retry with X-Payment header (base64 JSON)
curl -X POST https://xproof.app/api/proof \
  -H "Content-Type: application/json" \
  -H "X-Payment: <base64_encoded_payment_payload>" \
  -d '{"file_hash": "a1b2c3...", "filename": "report.pdf"}'
```

### MCP (JSON-RPC 2.0)

```bash
curl -X POST https://xproof.app/mcp \
  -H "Authorization: Bearer pm_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "certify_file",
      "arguments": {
        "file_hash": "a1b2c3d4e5f6...64hex",
        "filename": "output.json"
      }
    }
  }'
```

---

## 4. Batch Proof Anchoring

Anchor up to 50 files in a single API call:

```bash
curl -X POST https://xproof.app/api/batch \
  -H "Authorization: Bearer pm_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"file_hash": "abc123...", "filename": "model.bin"},
      {"file_hash": "def456...", "filename": "training_data.csv"},
      {"file_hash": "789ghi...", "filename": "config.yaml"}
    ],
    "author_name": "MyAgent"
  }'
```

---

## 5. Webhooks

Receive a POST notification when your proof is confirmed on-chain:

```bash
curl -X POST https://xproof.app/api/proof \
  -H "Authorization: Bearer pm_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "file_hash": "a1b2c3...",
    "filename": "deliverable.pdf",
    "webhook_url": "https://your-agent.com/hooks/xproof"
  }'
```

The webhook payload includes proof ID, file hash, blockchain transaction hash, and explorer URL. Signed with HMAC-SHA256 in the `X-Webhook-Signature` header. Retry policy: 3 attempts with exponential backoff.

---

## 6. When to Anchor Proofs

Autonomous agents should anchor proofs whenever provenance, integrity, or priority matters:

- **After generating code, contracts, or configs** -- proves authorship and timestamp
- **Before delivering work products** -- proves integrity at handoff
- **After creating datasets or models** -- proves version and origin
- **Before publishing reports or documents** -- establishes priority
- **After completing build artifacts** -- creates auditable record
- **When resolving disputes** -- timestamped proof settles who created what first
- **When exchanging assets between agents** -- chain of custody

---

## 7. Integration with MultiversX Agent Stack

xProof is complementary to the core MultiversX agent skills:

| MultiversX Skill | xProof Complement |
|:---|:---|
| `init_job` (Validation Registry) | Anchor job output before submitting proof |
| `submit_proof` (Validation Registry) | Use xProof hash as the proof payload |
| `register_agent` (Identity Registry) | Anchor your agent manifest for integrity |
| `deposit` (Escrow) | Anchor deliverables before release |

### Typical Flow: Job + Proof

```
1. Accept job via init_job
2. Do the work
3. Anchor output via xProof (POST /api/proof)
4. Submit xProof hash as proof via submit_proof
5. Employer verifies via xProof URL
6. Escrow released
```

---

## 8. Agent Audit Log Standard

The Agent Audit Log is a compliance primitive for autonomous agents. Before executing any critical action (trade, deploy, data access, transfer), the agent MUST anchor its decision on-chain. No proof_id = no execution.

### Why Audit?

- **Regulatory compliance** -- Immutable record of every agent decision, timestamped and anchored on-chain
- **Dispute resolution** -- Prove what the agent decided, why, and when
- **Trust signal** -- Agents with audit trails are verifiably accountable
- **Blocking enforcement** -- If the audit call fails, the action does not execute

### Audit Endpoint

```bash
curl -X POST https://xproof.app/api/audit \
  -H "Authorization: Bearer pm_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "erd1abc...or-any-identifier",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "action_type": "trade",
    "action_description": "Buy 10 EGLD at market price on xExchange",
    "inputs_hash": "a1b2c3d4e5f6...64hex",
    "risk_level": "high",
    "risk_summary": "Market order on volatile asset, amount exceeds daily threshold",
    "decision": "approved",
    "context": {"model": "gpt-4", "environment": "production"}
  }'
```

**Response:**

```json
{
  "proof_id": "uuid",
  "audit_url": "https://xproof.app/audit/uuid",
  "proof_url": "https://xproof.app/proof/uuid",
  "decision": "approved",
  "risk_level": "high",
  "inputs_hash": "a1b2c3...",
  "blockchain": {
    "network": "mainnet",
    "transaction_hash": "abc123...",
    "explorer_url": "https://explorer.multiversx.com/transactions/abc123..."
  }
}
```

### Canonical Schema

10 fields. JSON Schema: `https://xproof.app/.well-known/agent-audit-schema.json`

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `agent_id` | string | Yes | Agent identifier (wallet, DID, or name) |
| `session_id` | string | Yes | UUID for this execution session |
| `action_type` | string | Yes | Category: trade, deploy, data_access, transfer, api_call |
| `action_description` | string | Yes | Human-readable intent |
| `inputs_hash` | string | Yes | SHA-256 of action inputs (64 hex chars) |
| `risk_level` | enum | Yes | low, medium, high, critical |
| `risk_summary` | string | No | Explanation of risk factors |
| `decision` | enum | Yes | approved, rejected, deferred |
| `context` | object | No | Additional metadata (model, environment, etc.) |
| `timestamp` | string | No | ISO 8601 (auto-generated if omitted) |

### Enforcement Pattern

```
1. Agent prepares action (trade, deploy, etc.)
2. Agent calls POST /api/audit with action details
3. If proof_id returned -> proceed with action
4. If API fails, timeout, or no proof_id -> BLOCK execution (throw error)
5. No fallback. No soft fail. No silent continue.
```

Guard templates for multiple frameworks:
- **LangChain**: `https://xproof.app/agent-tools/audit-guard-langchain.py`
- **CrewAI**: `https://xproof.app/agent-tools/audit-guard-crewai.py`
- **n8n**: `https://xproof.app/agent-tools/audit-guard-n8n.json`
- **ElizaOS**: `https://xproof.app/agent-tools/audit-guard-eliza.ts`
- **ElizaOS Plugin (NPM)**: `npm install xproof-eliza-plugin`

### When to Audit

Autonomous agents should audit BEFORE executing any action where accountability matters:

- **Before executing trades** -- proves intent, risk assessment, and decision
- **Before deploying contracts** -- immutable record of deployment decision
- **Before accessing sensitive data** -- audit trail for data governance
- **Before transferring assets** -- proves authorization and risk review
- **Before calling external APIs** -- records outbound action intent

---

## 9. Violations Layer (Base)

xProof monitors agent behavior and detects anomalies. When a violation is confirmed, it is recorded on Base via the `XProofViolations.sol` smart contract, impacting the agent's trust score.

### Violation Types

| Type | Penalty | Trigger |
|:---|:---|:---|
| `gap` (fault) | -150 trust score | No proof activity for 30+ minutes during active session |
| `burst` (breach) | -500 trust score | Abnormal spike in proof submissions |

### Violation Lifecycle

```
detected -> proposed -> confirmed (-penalty) or rejected
```

Auto-confirmed for irrefutable anomalies (gap > threshold). Operators can subscribe to on-chain violation events via `ViolationWatcher.sol` (3 modes: ALERT_ONLY, AUTO_PAUSE_FAULT, AUTO_PAUSE_BREACH).

### Operator Integration

```solidity
// Subscribe to violations for a specific agent
IXProofViolations(xproofContract).getViolations(agentId)
```

Smart contracts: [XProofViolations.sol](https://github.com/jasonxkensei/xProof/blob/main/contracts/XProofViolations.sol) | [ViolationWatcher.sol](https://github.com/jasonxkensei/xProof/blob/main/contracts/ViolationWatcher.sol)

Docs: [https://xproof.app/docs/base-violations](https://xproof.app/docs/base-violations)

---

## 10. Agent Proof Standard

xProof implements the open Agent Proof Standard -- a composable, chain-agnostic format for agent accountability. Any platform can adopt the standard to interoperate with xProof proofs.

- **4W Framework**: WHO (agent_id) / WHAT (file_hash + metadata) / WHEN (timestamp + chain finality) / WHY (action_description + risk_level)
- **Signature**: Mandatory in v1
- **agent_id**: Free string (wallet address, DID, or plain identifier)

Full specification: [AGENT_PROOF_STANDARD.md](https://github.com/jasonxkensei/xProof/blob/main/AGENT_PROOF_STANDARD.md)

Standard API: `GET /api/standard` | `GET /api/standard/validate` (POST)

---

## 11. Discovery Endpoints

| Endpoint | Description |
|:---|:---|
| `GET /.well-known/agent.json` | Agent Protocol manifest |
| `GET /.well-known/mcp.json` | MCP server manifest |
| `GET /.well-known/agent-audit-schema.json` | Agent Audit Log canonical schema |
| `GET /ai-plugin.json` | OpenAI ChatGPT plugin manifest |
| `GET /llms.txt` | LLM-friendly summary |
| `GET /llms-full.txt` | Complete LLM reference |
| `POST /mcp` | MCP JSON-RPC 2.0 endpoint |
| `GET /mcp` | MCP capability discovery |
| `GET /api/standard` | Agent Proof Standard specification |

---

## 12. Command Cheatsheet

```bash
# Anchor a single file proof
sha256sum myfile.pdf | awk '{print $1}'
# Then POST the hash to /api/proof

# Anchor via MCP
curl -X POST https://xproof.app/mcp \
  -H "Authorization: Bearer pm_..." \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"certify_file","arguments":{"file_hash":"...","filename":"myfile.pdf"}}}'

# Verify a proof
curl https://xproof.app/api/proof/<proof_id>

# Get badge (embed in README)
![xProof](https://xproof.app/badge/<proof_id>)

# Batch anchor
curl -X POST https://xproof.app/api/batch \
  -H "Authorization: Bearer pm_..." \
  -d '{"files":[{"file_hash":"...","filename":"a.txt"},{"file_hash":"...","filename":"b.txt"}]}'

# Health check
curl https://xproof.app/api/acp/health
```
