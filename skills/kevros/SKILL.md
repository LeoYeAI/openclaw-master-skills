---
name: kevros
description: "Precision decisioning, agentic trust, and verifiable identity for autonomous agents"
version: 0.3.8
metadata:
  openclaw:
    requires:
      env: []
      bins: []
    primaryEnv: KEVROS_API_KEY
    always: false
    skillKey: kevros
    os:
      - linux
      - macos
      - windows
    install:
      - kind: npm
        package: "@kevros/openclaw-plugin"
        bins: []
---

# Kevros

Cryptographic governance for autonomous agents: precision decisioning, provenance attestation, intent binding, capability delegation, policy analysis, and compliance export.

Every decision gets a signed release token. Every action gets a hash-chained record. Every intent gets a cryptographic binding to its command. Downstream services verify independently — no callbacks, no trust assumptions.

**Base URL:** `https://governance.taskhawktech.com`

## Data Handling

This plugin sends data to the Kevros governance gateway. Understand what is transmitted before installing.

**Before tool execution** (`before_tool_call` hook):
- Tool name and full input payload are sent to `POST /governance/verify` for policy evaluation.
- The gateway hashes raw payloads (SHA-256) on receipt. Only digests are stored in the provenance chain.

**After tool execution** (`after_tool_call` hook):
- Tool name, a **truncated output summary (up to 500 characters)**, and governance metadata (release token, epoch, verification ID) are sent to `POST /governance/attest`.
- If tool output contains sensitive data, the 500-char summary may include it. Review your tool outputs before enabling attestation, or disable post-execution attestation by setting `autoAttest: false` in config.

**Network behavior:**
- All transmissions use HTTPS to `https://governance.taskhawktech.com`.
- If `KEVROS_API_KEY` is not set, the plugin calls `POST /signup` to auto-provision a free-tier key on first use (1,000 calls/month). Set the key explicitly to avoid implicit network signup.
- In `enforce` mode (default), unreachable gateway blocks high-risk tool calls. Use `advisory` mode for evaluation — it logs decisions without blocking.

## Quick Start

Get an API key (free, instant, no payment):

```bash
curl -X POST https://governance.taskhawktech.com/signup \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id"}'
```

Response:

```json
{
  "api_key": "kvrs_...",
  "tier": "free",
  "monthly_limit": 1000,
  "usage": {
    "header": "X-API-Key"
  }
}
```

Use the API key in all subsequent requests via the `X-API-Key` header.

## Precision Decisioning

**POST /governance/verify**

Verify an action against policy bounds before execution. Returns ALLOW, CLAMP, or DENY with a cryptographic release token that any downstream service can verify independently.

Request:

```json
{
  "action_type": "api_call",
  "action_payload": {
    "endpoint": "/deploy",
    "service": "api-v2",
    "replicas": 3
  },
  "agent_id": "your-agent-id",
  "policy_context": {
    "max_values": { "replicas": 5 },
    "forbidden_keys": ["sudo", "force"]
  }
}
```

Response:

```json
{
  "decision": "ALLOW",
  "verification_id": "a1b2c3d4-...",
  "release_token": "f7a8b9c0...",
  "applied_action": {
    "endpoint": "/deploy",
    "service": "api-v2",
    "replicas": 3
  },
  "reason": "All values within policy bounds",
  "epoch": 42,
  "provenance_hash": "e3b0c442...",
  "timestamp_utc": "2026-02-26T12:00:00Z"
}
```

- **ALLOW** — proceed as planned. The `release_token` is proof.
- **CLAMP** — action was adjusted to safe bounds. Use `applied_action` instead of your original.
- **DENY** — action rejected. Do not proceed. `release_token` is null.

Share the `release_token` with collaborating agents so they can independently verify the decision.

## Provenance Attestation

**POST /governance/attest**

Record a completed action in a hash-chained, append-only evidence ledger. Each attestation extends your provenance chain. Your raw payload is SHA-256 hashed — actual data is never stored.

Request:

```json
{
  "agent_id": "your-agent-id",
  "action_description": "Deployed api-v2 with 3 replicas",
  "action_payload": {
    "service": "api-v2",
    "replicas": 3,
    "status": "success"
  },
  "context": {
    "environment": "production",
    "triggered_by": "scheduled"
  }
}
```

Response:

```json
{
  "attestation_id": "b2c3d4e5-...",
  "epoch": 43,
  "hash_prev": "e3b0c442...",
  "hash_curr": "a1b2c3d4...",
  "timestamp_utc": "2026-02-26T12:00:01Z",
  "chain_length": 43
}
```

A longer chain with consistent outcomes builds a higher trust score over time.

## Intent Binding

**POST /governance/bind**

Bind a declared intent to a specific command. Creates a cryptographic link between what you plan to do and the command that does it. Prove later that you did exactly what you said you would.

Request:

```json
{
  "agent_id": "your-agent-id",
  "intent_type": "MAINTENANCE",
  "intent_description": "Scale api-v2 to handle traffic spike",
  "command_payload": {
    "action": "scale",
    "service": "api-v2",
    "replicas": 5
  },
  "goal_state": {
    "replicas": 5,
    "healthy": true
  }
}
```

Response:

```json
{
  "intent_id": "c3d4e5f6-...",
  "intent_hash": "d4e5f6a7...",
  "binding_id": "e5f6a7b8-...",
  "binding_hmac": "a7b8c9d0...",
  "command_hash": "b8c9d0e1...",
  "epoch": 44,
  "timestamp_utc": "2026-02-26T12:00:02Z"
}
```

Save `intent_id` and `binding_id` to verify outcomes later.

## Verify Outcome

**POST /governance/verify-outcome**

Verify whether a bound intent achieved its goal state. Free when used with a prior `bind()` call.

Request:

```json
{
  "agent_id": "your-agent-id",
  "intent_id": "c3d4e5f6-...",
  "binding_id": "e5f6a7b8-...",
  "actual_state": {
    "replicas": 5,
    "healthy": true
  },
  "tolerance": 0.1
}
```

Response:

```json
{
  "verification_id": "f6a7b8c9-...",
  "intent_id": "c3d4e5f6-...",
  "status": "ACHIEVED",
  "achieved_percentage": 100.0,
  "discrepancy": null,
  "evidence_hash": "c9d0e1f2...",
  "timestamp_utc": "2026-02-26T12:00:03Z"
}
```

Status values: `ACHIEVED`, `PARTIALLY_ACHIEVED`, `FAILED`, `BLOCKED`, `TIMEOUT`. Free when used with a prior `bind()` call.

## Compliance Bundle

**POST /governance/bundle** — $0.05 per call

Export your agent's full cryptographic trust record for compliance, auditing, or regulatory review.

Request:

```json
{
  "agent_id": "your-agent-id",
  "time_range_start": "2026-02-25T00:00:00Z",
  "time_range_end": "2026-02-26T12:00:00Z",
  "include_intent_chains": true,
  "include_pqc_signatures": true,
  "include_verification_instructions": true
}
```

Response:

```json
{
  "bundle_id": "d4e5f6a7-...",
  "agent_id": "your-agent-id",
  "record_count": 42,
  "truncated": false,
  "chain_integrity": true,
  "time_range": {"start": "2026-02-25T00:00:00Z", "end": "2026-02-26T12:00:00Z"},
  "records": ["..."],
  "intent_chains": ["..."],
  "pqc_signatures": ["..."],
  "verification_instructions": "Recompute SHA-256...",
  "bundle_hash": "e5f6a7b8...",
  "timestamp_utc": "2026-02-26T12:00:04Z"
}
```

## Batch Operations

**POST /governance/batch**

Execute up to 100 governance operations (verify, attest, bind) in a single call. Each sub-operation is metered individually at standard rates. Use for bulk processing or multi-step workflows.

Request:

```json
{
  "agent_id": "your-agent-id",
  "operations": [
    {
      "type": "verify",
      "params": {
        "action_type": "api_call",
        "action_payload": {"endpoint": "/deploy", "replicas": 3}
      }
    },
    {
      "type": "attest",
      "params": {
        "action_description": "Deployment completed",
        "action_payload": {"status": "success"}
      }
    }
  ],
  "stop_on_deny": false
}
```

Response:

```json
{
  "batch_id": "g7h8i9j0-...",
  "agent_id": "your-agent-id",
  "total": 2,
  "executed": 2,
  "results": [
    {"index": 0, "type": "verify", "status": "ok", "result": {"decision": "ALLOW", "...": "..."}},
    {"index": 1, "type": "attest", "status": "ok", "result": {"attestation_id": "...", "...": "..."}}
  ],
  "summary": {"allow": 1, "clamp": 0, "deny": 0, "attest": 1, "bind": 0, "error": 0},
  "batch_hash": "a1b2c3d4..."
}
```

If `stop_on_deny` is true, processing halts on the first DENY decision.

## Capability Delegation

**POST /governance/delegate**

Grant scoped, time-limited capabilities to another agent. The delegation is HMAC-signed and recorded in the provenance chain. Supports hierarchical sub-delegation with restrictive scope intersection.

Request:

```json
{
  "delegator_agent_id": "your-agent-id",
  "delegatee_agent_id": "helper-agent-42",
  "scope": {
    "allowed_endpoints": ["verify", "attest"],
    "policy_overrides": {"max_values": {"replicas": 3}},
    "max_calls": 100
  },
  "ttl_seconds": 3600,
  "description": "Handle deployment verification",
  "allow_subdelegation": false
}
```

Response:

```json
{
  "delegation_id": "h8i9j0k1-...",
  "delegation_token": "f7a8b9c0...",
  "delegator_agent_id": "your-agent-id",
  "delegatee_agent_id": "helper-agent-42",
  "scope": {"allowed_endpoints": ["verify", "attest"], "max_calls": 100},
  "expires_utc": "2026-02-26T13:00:00Z",
  "provenance_hash": "b8c9d0e1...",
  "chain_depth": 1
}
```

The delegatee passes the `delegation_token` as `X-Delegate-Token` header when acting on behalf of the delegator.

**GET /governance/delegations/{agent_id}** — list active delegations for an agent.

**DELETE /governance/delegations/{delegation_id}** — revoke an active delegation.

## Reversibility Check

**POST /governance/check-reversibility**

Check whether an intent chain can be reversed. Pre-abort safety check for multi-step workflows.

Request:

```json
{
  "intent_id": "c3d4e5f6-...",
  "include_children": true
}
```

Returns reversibility status, constraints, time elapsed, and child dependency analysis.

## Policy Replay

**POST /governance/replay**

Replay provenance records through an alternative policy. Deterministic "what-if" analysis: "What would have happened if we'd used policy X instead?"

Request:

```json
{
  "agent_id": "your-agent-id",
  "template_id": "strict_safety",
  "limit": 50
}
```

Response:

```json
{
  "total_replayed": 50,
  "replay_policy": {"max_values": {"speed": 3.0}},
  "changes": {"upgraded": 5, "downgraded": 12, "unchanged": 33},
  "results": [
    {
      "epoch": 42,
      "agent_id": "your-agent-id",
      "action_type": "motor_command",
      "original_decision": "ALLOW",
      "replayed_decision": "CLAMP",
      "change": "more_restrictive"
    }
  ]
}
```

Use for policy regression testing before deploying new policies, or forensic investigation.

## Counterfactual Analysis

**POST /governance/counterfactual**

Simulate an action against multiple policies simultaneously. Returns a decision matrix showing how each policy handles the same action.

Request:

```json
{
  "action_payload": {"endpoint": "/deploy", "replicas": 10},
  "action_type": "api_call",
  "policies": [
    {"label": "conservative", "template_id": "strict_safety"},
    {"label": "permissive", "policy_context": {"max_values": {"replicas": 20}}},
    {"label": "deny-all", "policy_context": {"forbidden_keys": ["replicas"]}}
  ],
  "include_historical": true,
  "agent_id": "your-agent-id"
}
```

Response includes consensus analysis (do all policies agree?), decision distribution, and optional historical comparison.

## Intent Navigation

**GET /governance/intents/{intent_id}/children**

Return all direct child intents of a parent intent. Audit multi-agent delegation hierarchies.

**GET /governance/intents/{intent_id}/ancestry**

Walk up the intent hierarchy from leaf to root. Full authorization chain for auditing.

**GET /governance/intents/{intent_id}/tree**

Return the full delegation tree rooted at an intent. Accepts optional `max_depth` query parameter (default 10).

## Policy Templates

**GET /governance/policy-templates** — free, no API key required

List available named policy templates. Use template IDs with verify, replay, and counterfactual endpoints instead of inline policy definitions.

## Export

**POST /governance/export/csv** — export provenance records as CSV.

**POST /governance/export/sarif** — export provenance in SARIF format (Static Analysis Results Interchange Format) for security tooling integration.

**POST /governance/export/merkle** — export provenance as a Merkle tree with root hash and leaf hashes for independent integrity verification.

All export endpoints accept optional `agent_id`, `time_range_start`, `time_range_end`, and `limit` parameters.

## Health and Audit

**GET /governance/health-score** — overall gateway health score including agent count, healthy agent count, and chain integrity rate.

**GET /governance/audit-summary** — aggregate statistics across all provenance: total records, total agents, decision distribution, and chain integrity status.

**GET /governance/agent-compliance/{agent_id}** — compliance profile for a specific agent: compliance score, chain integrity, total decisions, and outcome success rate.

## Media Attestation

**POST /media/attest** — $0.05 per call

Attest media files (photos, videos, audio, documents) with SHA-256 hashing and provenance chain inclusion.

Request:

```json
{
  "agent_id": "your-agent-id",
  "media_hash": "a1b2c3d4e5f6...64-char-hex-sha256",
  "media_type": "PHOTO",
  "media_size_bytes": 2048576,
  "capture_timestamp_utc": "2026-02-26T12:00:00Z",
  "description": "Generated report screenshot"
}
```

Required fields: `agent_id`, `media_hash` (64-char hex SHA-256), `media_type` (PHOTO | VIDEO | AUDIO | DOCUMENT), `media_size_bytes`, `capture_timestamp_utc`.

Optional fields: `description`, `tags`, `capture_location` (lat/lng), `device_info`, `frame_hashes` (for video).

Response:

```json
{
  "attestation_id": "e5f6a7b8-...",
  "certificate_id": "mca_abc123",
  "media_hash": "a1b2c3d4e5f6...",
  "media_type": "PHOTO",
  "epoch": 45,
  "hash_prev": "...",
  "hash_curr": "b8c9d0e1...",
  "verification_url": "https://governance.taskhawktech.com/media/verify/mca_abc123",
  "chain_length": 45,
  "timestamp_utc": "2026-02-26T12:00:05Z"
}
```

## Media Verify

**POST /media/verify** — free, no API key required

Verify that media content matches a specific attestation certificate.

Request:

```json
{
  "media_hash": "a1b2c3d4e5f6...64-char-hex-sha256",
  "certificate_id": "mca_abc123"
}
```

Response:

```json
{
  "verified": true,
  "certificate_id": "mca_abc123",
  "media_hash_match": true,
  "chain_integrity": true,
  "pqc_signature_valid": true,
  "reason": "Media hash matches certificate, chain intact"
}
```

## Media Verify Lookup

**GET /media/verify/{certificate_id}** — free, no API key required

Look up a specific media attestation by its certificate ID. Returns the full attestation record including attesting agent, epoch, and chain integrity.

## Passport

All Passport endpoints are free and require no authentication.

**GET /passport/{agent_id}**

Returns an agent's trust passport including score, tier, badges, and activity stats.

```json
{
  "agent_id": "your-agent-id",
  "trust_score": 0.95,
  "tier": "gold",
  "badges": ["verified", "consistent", "high_volume"],
  "stats": {
    "total_decisions": 1250,
    "attestations": 890,
    "bindings": 340,
    "outcomes_achieved": 310,
    "chain_intact": true,
    "active_days": 45,
    "current_streak": 12
  }
}
```

**GET /passport/{agent_id}/badge.svg**

Returns an embeddable SVG trust badge. Use in agent descriptions, documentation, or dashboards.

**GET /passport/{agent_id}/history**

Returns full decision history for an agent.

**GET /passport/leaderboard**

Returns top trusted agents by trust score. Accepts optional `limit` query parameter (1-200, default 50).

Response:

```json
{
  "agents": [
    { "agent_id": "top-agent", "trust_score": 0.98, "tier": "gold" }
  ],
  "total": 150
}
```

**POST /passport/{agent_id}/claim** — requires API key

Link an agent's passport to your operator account. Must provide `X-API-Key` header.

Response:

```json
{
  "agent_id": "your-agent-id",
  "claimed": true,
  "profile": { "...passport profile..." }
}
```

Returns 409 if already claimed by another operator, 404 if no passport exists yet.

## Agent Discovery

**GET /.well-known/agent.json**

Returns the A2A protocol agent card. No authentication required.

```bash
curl https://governance.taskhawktech.com/.well-known/agent.json
```

Returns capabilities, supported skills, SDK references, and free-tier signup details.

## MCP

For MCP-native agents, connect directly via streamable-http transport:

```
https://governance.taskhawktech.com/mcp/
```

360 tools, 2 resources, 2 prompts. Auto-provisions a free-tier key on first tool call if no API key is provided.

## Python SDK

```bash
pip install kevros
# or
uv pip install kevros
```

```python
from kevros_governance import GovernanceClient

client = GovernanceClient(agent_id="your-agent-id")
result = client.verify(
    action_type="api_call",
    action_payload={"endpoint": "/deploy"},
    agent_id="your-agent-id",
)
print(result.decision)  # ALLOW, CLAMP, or DENY
```

## Enforcement Modes

Every operator key has an enforcement mode that controls how decisions are applied:

- **enforce** (default) — fail-closed. DENY means DENY. Release tokens are only issued for ALLOW/CLAMP.
- **advisory** — shadow mode. DENY decisions are logged but overridden to ALLOW. No release token is issued for would-be denials. Use for testing policies before enforcing them.
- **gated** — human-in-the-loop. DENY decisions are held for operator approval. Poll `/governance/gated/{request_id}` for status.
- **deny** — kill-switch. ALL requests are blocked regardless of policy evaluation. Use for emergency shutdown.

The `enforcement_mode` field is returned in every verify response. Use `/enforcement` to check your current mode.

Enforcement mode changes require admin-level access and are not available through the plugin. Contact your administrator or use the admin API directly.

## Decision Approach

When collaborating with another agent:

1. **Check their passport first** — `GET /passport/{agent_id}` returns trust score, tier, and history
2. **Embed badges** — Use `GET /passport/{agent_id}/badge.svg` in your agent's description to show your trust level
3. **Trust thresholds:**
   - **Gold tier (score >= 90%)** — proceed with normal collaboration
   - **Silver tier (score 50-89%)** — verify their actions before relying on results
   - **Bronze tier (score < 50%)** — require bound intents with outcome verification
   - **No history** — start with small, low-risk interactions and build trust incrementally
4. **Verify before you rely** — Use `/governance/verify-token` to independently confirm any release token a peer shares with you

## Pricing

**Subscriptions:**
- **Free tier:** 1,000 calls/month, instant signup, no payment required
- **Scout:** $29/mo — 5,000 calls
- **Sentinel:** $149/mo — 50,000 calls
- **Sovereign:** $499/mo — 500,000 calls

**Per-call (via x402 USDC, no subscription required):**
- Verify: $0.01
- Attest: $0.02
- Bind: $0.02
- Media Attest: $0.05
- Compliance Bundle: $0.05
- Batch: each sub-operation metered individually
- Verify Outcome: free with Bind
- Delegation, Replay, Counterfactual, Export, Health, Audit: metered per call
- Passport, Media Verify, Reputation, Verify Token, Policy Templates: free

Subscription calls are metered against your monthly allowance. x402 per-call pricing applies when paying per-call without a subscription.

Upgrade at `https://www.taskhawktech.com/pricing`
