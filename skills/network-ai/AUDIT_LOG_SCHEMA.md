# Audit Log Schema — Network-AI

Network-AI writes a JSONL audit trail during permission management and swarm execution. This document describes every field and event type.

---

## File Location

```
data/audit_log.jsonl
```

One JSON object per line. The file is append-only. Each entry is a complete, self-contained record — no dependencies between lines.

The CLI provides direct access without inspecting the file manually:

```bash
network-ai audit log            # print all entries (add --limit <n> to cap output)
network-ai audit tail           # live-stream new entries as they are appended
network-ai audit clear          # reset the log (irreversible)
network-ai --json audit log     # machine-readable output
```

---

## Envelope (all events)

Every log entry uses the same outer structure:

```json
{
  "timestamp": "2026-02-28T14:32:01.123456+00:00",
  "action":    "<event_type>",
  "details":   { ... }
}
```

| Field | Type | Description |
|---|---|---|
| `timestamp` | ISO 8601 UTC string | When the event occurred |
| `action` | string | Event type — see table below |
| `details` | object | Event-specific payload — see per-event schemas |

---

## Event Types

| `action` | Emitted by | Trigger |
|---|---|---|
| `permission_request` | `check_permission.py` | Agent requests access to a resource |
| `permission_granted` | `check_permission.py` | Request passes weighted scoring; token issued |
| `permission_denied` | `check_permission.py` | Request fails scoring threshold |
| `permission_revoked` | `revoke_token.py` | Token explicitly revoked |
| `ttl_cleanup` | `revoke_token.py` | Expired tokens pruned from active_grants.json |
| `budget_initialized` | `swarm_guard.py` | FederatedBudget ceiling set for a session |
| `handoff_allowed` | `swarm_guard.py` | Agent-to-agent handoff passes all checks |
| `handoff_blocked` | `swarm_guard.py` | Agent-to-agent handoff blocked by guard |
| `safety_shutdown` | `swarm_guard.py` | Swarm halted due to budget ceiling breach |

---

## Per-Event `details` Schemas

### `permission_request`

```json
{
  "agent_id":      "data_analyst",
  "resource_type": "DATABASE",
  "justification": "Need customer order history for Q1 sales report",
  "scope":         "read"
}
```

| Field | Type | Notes |
|---|---|---|
| `agent_id` | string | Requesting agent identifier |
| `resource_type` | string | `DATABASE`, `PAYMENTS`, `API`, `FILESYSTEM`, `EMAIL`, `CUSTOMER_DATA`, `INTERNAL_SERVICES` |
| `justification` | string | Free-text justification, scored before grant |
| `scope` | string \| null | Optional scope restriction (e.g. `read`, `write`) |

---

### `permission_granted`

```json
{
  "token":         "grant_a1b2c3d4e5f67890abcdef1234567890ab",
  "agent_id":      "data_analyst",
  "resource_type": "DATABASE",
  "scope":         "read",
  "expires_at":    "2026-02-28T14:37:01.123456+00:00",
  "restrictions":  ["read-only", "no-schema-changes"],
  "granted_at":    "2026-02-28T14:32:01.123456+00:00"
}
```

| Field | Type | Notes |
|---|---|---|
| `token` | string | `grant_` + 32 hex chars (UUID4, no dashes) |
| `agent_id` | string | Agent the token was issued to |
| `resource_type` | string | Resource access was granted for |
| `scope` | string \| null | Scope restriction, if provided |
| `expires_at` | ISO 8601 UTC | Token expiry (default: 5 minutes from grant) |
| `restrictions` | string[] | Resource-type-specific restrictions applied |
| `granted_at` | ISO 8601 UTC | Same as envelope `timestamp` |

---

### `permission_denied`

```json
{
  "agent_id":      "untrusted_bot",
  "resource_type": "PAYMENTS",
  "reason":        "Combined evaluation score (0.31) below threshold (0.5).",
  "scores": {
    "justification": 0.25,
    "trust":         0.40,
    "risk":          0.90,
    "weighted":      0.31
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `agent_id` | string | Requesting agent |
| `resource_type` | string | Resource that was denied |
| `reason` | string | Human-readable denial reason |
| `scores.justification` | float 0–1 | Justification quality score (40% weight) |
| `scores.trust` | float 0–1 | Agent trust level (30% weight) |
| `scores.risk` | float 0–1 | Resource risk score (30% weight, inverted) |
| `scores.weighted` | float 0–1 | Final combined score; threshold = 0.50 |

---

### `permission_revoked`

```json
{
  "token":    "grant_a1b2c3d4e5f67890abcdef1234567890ab",
  "agent_id": "data_analyst",
  "reason":   "manual revocation"
}
```

---

### `ttl_cleanup`

```json
{
  "removed_tokens": ["grant_abc...", "grant_def..."],
  "count":          2
}
```

---

### `budget_initialized`

```json
{
  "ceiling": 5000,
  "unit":    "tokens"
}
```

---

### `handoff_allowed`

```json
{
  "from_agent": "orchestrator",
  "to_agent":   "implementer",
  "task":       "implement payment service",
  "budget_remaining": 4120
}
```

---

### `handoff_blocked`

```json
{
  "from_agent": "implementer",
  "to_agent":   "orchestrator",
  "reason":     "budget_exceeded",
  "budget_used": 5100,
  "budget_ceiling": 5000
}
```

---

### `safety_shutdown`

```json
{
  "reason":         "budget_ceiling_breached",
  "budget_used":    5100,
  "budget_ceiling": 5000,
  "agent":          "rogue_agent"
}
```

---

## Scoring Reference

Permission decisions use a three-factor weighted score:

| Factor | Weight | Source |
|---|---|---|
| Justification quality | 40% | Scored by `score_justification()` — checks specificity, context, action verbs, structural coherence, 16 prompt-injection patterns |
| Agent trust level | 30% | Lookup in `DEFAULT_TRUST_LEVELS` dict; unknown agents default to 0.5 |
| Resource risk (inverted) | 30% | Base risk per resource type; high-risk resources require higher total score |

**Approval threshold: 0.50.** Requests below this are logged as `permission_denied`.

---

## Node.js Layer (TypeScript package)

When using the `network-ai` npm package directly, the `SecureAuditLogger` class in `security.ts` produces HMAC-SHA256-signed entries with the same envelope format plus a `signature` field. This is separate from the Python script layer described above.

---

## Retention & Privacy

- The log is append-only. There is no built-in rotation — implement log rotation at the infrastructure level (e.g. `logrotate`, S3 lifecycle policy).
- No PII is logged by default. Justification text is logged as-provided — avoid including PII in justification strings.
- No API keys, tokens in cleartext, or sensitive resource content are logged.
