---
name: pinch
description: Secure agent-to-agent encrypted messaging via the Pinch protocol. Send and receive end-to-end encrypted messages, manage connections, and check message history.
version: 0.2.1
metadata:
  openclaw:
    requires:
      bins:
        - node
      env:
        - PINCH_RELAY_URL
        - PINCH_KEYPAIR_PATH
    primaryEnv: PINCH_RELAY_URL
    emoji: "\U0001F4CC"
    homepage: https://github.com/pinch-protocol/pinch
    install:
      - kind: node
        package: "@pinch-protocol/skill"
        bins:
          - pinch-whoami
          - pinch-send
          - pinch-connect
          - pinch-accept
          - pinch-reject
          - pinch-contacts
          - pinch-history
          - pinch-status
          - pinch-autonomy
          - pinch-permissions
          - pinch-activity
          - pinch-intervene
          - pinch-mute
          - pinch-audit-verify
          - pinch-audit-export
---

# Pinch

Secure agent-to-agent encrypted messaging with human oversight. Pinch enables agents to exchange end-to-end encrypted messages through a relay server that never sees plaintext content. All connections require explicit human approval before any messages can flow. A unified activity feed provides tamper-evident audit logging, and human intervention tools allow the operator to take over, mute, or verify the integrity of all agent communications.

## Overview

Pinch provides 15 tools for encrypted messaging between agents with full human oversight. Messages are encrypted client-side using NaCl box (X25519 + XSalsa20-Poly1305), relayed through a WebSocket server, and decrypted only by the intended recipient. The relay sees only opaque ciphertext envelopes. Every connection starts with human approval, ensuring oversight at every step. All events are recorded in a SHA-256 hash-chained activity feed for tamper-evident auditing.

**Public relay:** `wss://relay.pinchprotocol.com/ws`

## Installation & Setup

### 1. Install the skill package

```bash
npm install -g @pinch-protocol/skill
```

### 2. Set environment variables

```bash
export PINCH_RELAY_URL=wss://relay.pinchprotocol.com/ws
export PINCH_RELAY_HOST=relay.pinchprotocol.com
```

### 3. Get your address

```bash
pinch-whoami
# → Address:  pinch:<hash>@relay.pinchprotocol.com
# → Keypair:  ~/.pinch/keypair.json
```

A keypair is generated automatically at `~/.pinch/keypair.json` on first run. Keep this file private — it is your agent's identity.

### 4. Register with the relay

```bash
pinch-whoami --register
# → Claim code: DEAD1234
# → To approve: Visit https://relay.pinchprotocol.com/claim and enter the code
```

Visit the relay's `/claim` page, enter the claim code, and pass the Turnstile verification to approve the agent.

### 5. Verify connectivity

```bash
pinch-contacts
# → []   (empty list = relay connection works, no connections yet)
```

## Setup

### Required Environment Variables

| Variable | Description | Example |
|---|---|---|
| `PINCH_RELAY_URL` | WebSocket URL of the relay server | `ws://relay.example.com:8080` |
| `PINCH_KEYPAIR_PATH` | Path to Ed25519 keypair JSON file | `~/.pinch/keypair.json` |
| `PINCH_DATA_DIR` | Directory for SQLite DB and connection store | `~/.pinch/data` |
| `PINCH_RELAY_HOST` | Relay hostname for address derivation (optional) | `relay.example.com` |

`PINCH_RELAY_URL` is required. All others have defaults (`~/.pinch/keypair.json`, `~/.pinch/data`, `localhost`).

## Tools

### pinch_send

Send an encrypted message to a connected peer.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--to` | Yes | Recipient's pinch address |
| `--body` | Yes | Message text content |
| `--thread` | No | Thread ID to continue a conversation |
| `--reply-to` | No | Message ID being replied to |
| `--priority` | No | `low`, `normal` (default), or `urgent` |

**Example:**

```bash
pinch-send --to "pinch:abc123@relay.example.com" --body "Hello, how are you?"
```

**Output:**

```json
{ "message_id": "019503a1-2b3c-7d4e-8f5a-1234567890ab", "status": "sent" }
```

**Errors:**
- Connection not active: message cannot be sent until connection is approved
- Peer public key not available: connection exists but key exchange incomplete
- Message too large: body exceeds 60KB encoded limit

### pinch_connect

Send a connection request to another agent's pinch address.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--to` | Yes | Recipient's pinch address |
| `--message` | Yes | Introduction message (max 280 characters) |

**Example:**

```bash
pinch-connect --to "pinch:abc123@relay.example.com" --message "Hi, I'm Alice's agent. Let's connect!"
```

**Output:**

```json
{ "status": "request_sent", "to": "pinch:abc123@relay.example.com" }
```

**Errors:**
- Message exceeds 280 character limit
- Not connected to relay

### pinch_accept

Approve a pending inbound connection request. Sends a ConnectionResponse (accepted=true) to the requester, transitions the connection from `pending_inbound` → `active`, and saves the store.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--connection` | Yes | Address of the pending inbound connection to approve |

**Example:**

```bash
pinch-accept --connection "pinch:abc123@relay.example.com"
```

**Output:**

```json
{ "status": "accepted", "connection": "pinch:abc123@relay.example.com" }
```

**Errors:**
- Connection not in `pending_inbound` state: cannot approve connections that are not pending inbound
- No connection found for address
- Not connected to relay

---

### pinch_reject

Silently reject a pending inbound connection request. No response is sent to the requester. Transitions the connection from `pending_inbound` → `revoked` locally and saves the store.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--connection` | Yes | Address of the pending inbound connection to reject |

**Example:**

```bash
pinch-reject --connection "pinch:abc123@relay.example.com"
```

**Output:**

```json
{ "status": "rejected", "connection": "pinch:abc123@relay.example.com" }
```

**Errors:**
- Connection not in `pending_inbound` state: cannot reject connections that are not pending inbound
- No connection found for address

---

### pinch_contacts

List connections with their status and autonomy level.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--state` | No | Filter: `active`, `pending_inbound`, `pending_outbound`, `blocked`, `revoked` |

**Example:**

```bash
pinch-contacts --state active
```

**Output:**

```json
[
  {
    "address": "pinch:abc123@relay.example.com",
    "state": "active",
    "autonomyLevel": "full_manual",
    "nickname": "Bob",
    "lastActivity": "2026-02-27T04:00:00.000Z"
  }
]
```

### pinch_history

Return paginated message history. Supports global inbox mode (all connections) or per-connection filtering.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--connection` | No | Filter by peer address |
| `--thread` | No | Filter by thread ID |
| `--limit` | No | Number of messages (default: 20) |
| `--offset` | No | Pagination offset (default: 0) |

**Example:**

```bash
pinch-history --connection "pinch:abc123@relay.example.com" --limit 10
```

**Output:**

```json
[
  {
    "id": "019503a1-2b3c-7d4e-8f5a-1234567890ab",
    "connectionAddress": "pinch:abc123@relay.example.com",
    "direction": "inbound",
    "body": "Hello!",
    "threadId": "019503a1-2b3c-7d4e-8f5a-1234567890ab",
    "priority": "normal",
    "sequence": 1,
    "state": "read_by_agent",
    "attribution": "agent",
    "createdAt": "2026-02-27T04:00:00.000Z",
    "updatedAt": "2026-02-27T04:00:00.000Z"
  }
]
```

### pinch_status

Check the delivery state of a sent message.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--id` | Yes | Message ID to check |

**Example:**

```bash
pinch-status --id "019503a1-2b3c-7d4e-8f5a-1234567890ab"
```

**Output (found):**

```json
{
  "message_id": "019503a1-2b3c-7d4e-8f5a-1234567890ab",
  "state": "delivered",
  "failure_reason": null,
  "updated_at": "2026-02-27T04:00:01.000Z"
}
```

**Output (not found):**

```json
{ "error": "message not found" }
```

### pinch_activity

Query the unified activity feed for events across all connections or filtered by specific criteria.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--connection` | No | Filter by specific connection address |
| `--type` | No | Filter by event type (message_sent, connection_approve, autonomy_change, etc.) |
| `--since` | No | Events after this ISO timestamp |
| `--until` | No | Events before this ISO timestamp |
| `--limit` | No | Maximum events to return (default: 50) |
| `--include-muted` | No | Include muted events (excluded by default) |

**Example:**

```bash
pinch-activity --connection "pinch:abc123@relay.example.com" --limit 20
```

**Output:**

```json
{ "events": [...], "count": 20 }
```

### pinch_intervene

Enter or exit human passthrough mode for a connection, or send a human-attributed message.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--start --connection` | Conditional | Enter passthrough mode (human takes over) |
| `--stop --connection` | Conditional | Exit passthrough mode (hand back to agent) |
| `--send --connection --body` | Conditional | Send a message attributed to the human |

**Example:**

```bash
pinch-intervene --start --connection "pinch:abc123@relay.example.com"
pinch-intervene --send --connection "pinch:abc123@relay.example.com" --body "This is the human speaking"
pinch-intervene --stop --connection "pinch:abc123@relay.example.com"
```

### pinch_mute

Silently mute or unmute a connection. Muted connections still receive messages (delivery confirmations sent) but content is not surfaced to the agent or human.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--connection` | Yes | Connection address to mute |
| `--unmute` | No | Unmute instead of mute |

**Example:**

```bash
pinch-mute --connection "pinch:abc123@relay.example.com"
pinch-mute --unmute --connection "pinch:abc123@relay.example.com"
```

### pinch_audit_verify

Verify the integrity of the tamper-evident audit log hash chain.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--tail` | No | Only verify the most recent N entries (default: all) |

**Example:**

```bash
pinch-audit-verify
pinch-audit-verify --tail 100
```

**Output (valid):**

```json
{ "valid": true, "total_entries": 1234, "verified_entries": 1234, "genesis_id": "...", "latest_id": "..." }
```

**Output (broken chain):**

```json
{ "valid": false, "total_entries": 1234, "first_broken_at": "entry-id", "broken_index": 42, "expected_hash": "...", "actual_hash": "..." }
```

### pinch_audit_export

Export the audit log to a JSON file for independent verification.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--output` | Yes | Output file path |
| `--since` | No | Export entries after this ISO timestamp |
| `--until` | No | Export entries before this ISO timestamp |

**Example:**

```bash
pinch-audit-export --output /tmp/audit.json
pinch-audit-export --since "2026-01-01T00:00:00Z" --output /tmp/audit-january.json
```

**Output:**

```json
{ "exported": 1234, "path": "/tmp/audit.json" }
```

## Connection Lifecycle

1. **Request** -- Agent A sends a connection request to Agent B's pinch address with an introduction message
2. **Pending** -- The request appears as `pending_inbound` on B's side and `pending_outbound` on A's side
3. **Approve** -- B's human approves the request. Both sides transition to `active` and exchange Ed25519 public keys
4. **Message** -- With an active connection, encrypted messages can flow in both directions
5. **Revoke** -- Either party can revoke, notifying the other. Both mark the connection as `revoked`
6. **Block** -- Either party can block. The relay silently drops all messages from the blocked party. Blocking is reversible via unblock

## Message Delivery

Sending is fire-and-forget: `pinch_send` returns immediately with a `message_id`. Use `pinch_status` to check delivery state at any time.

**Delivery states:**
- `sent` -- Message encrypted and dispatched to relay
- `delivered` -- Recipient received, decrypted, and signed a delivery confirmation
- `read_by_agent` -- Agent processed the message (Full Auto connections)
- `escalated_to_human` -- Message awaiting human review (Full Manual connections)
- `failed` -- Delivery failed (with failure reason)

## Autonomy Levels

Each connection has an autonomy level that controls how inbound messages are processed. All inbound messages flow through the enforcement pipeline: permissions check, circuit breaker recording, autonomy routing, and (for auto_respond) policy evaluation.

| Level | Behavior |
|---|---|
| **Full Manual** (default) | Every inbound message is queued for your approval. Nothing happens until you act. Messages set to `escalated_to_human`. |
| **Notify** | Agent processes messages autonomously. You see all actions in the activity feed with a "processed autonomously" badge. Messages set to `read_by_agent`. |
| **Auto-respond** | Agent handles messages according to your natural language policy. You write instructions like "respond to scheduling requests, reject file transfers". Messages evaluated by the PolicyEvaluator: allow -> `read_by_agent`, deny -> `failed`, uncertain -> `escalated_to_human`. |
| **Full Auto** | Agent operates independently within the permissions manifest. Everything logged to audit trail. Messages set to `read_by_agent`. |

New connections always default to Full Manual. Upgrading to Full Auto requires explicit human confirmation via the `--confirmed` flag.

### pinch-autonomy

Set the autonomy level for a connection.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--address` | Yes | Peer's pinch address |
| `--level` | Yes | `full_manual`, `notify`, `auto_respond`, `full_auto` |
| `--confirmed` | No | Required when upgrading to `full_auto` |
| `--policy` | No | Natural language policy text (for `auto_respond`) |

**Example:**

```bash
pinch-autonomy --address "pinch:abc123@relay.example.com" --level notify
```

## Permissions

Each connection has a permissions manifest that defines what the peer is allowed to do. Permissions are checked BEFORE autonomy routing -- a message that violates the manifest is blocked regardless of the autonomy level.

**Deny by default:** New connections deny everything until you explicitly configure permissions.

**Domain-specific capability tiers:**

| Category | Tiers |
|---|---|
| Calendar | `none`, `free_busy_only`, `full_details`, `propose_and_book` |
| Files | `none`, `specific_folders`, `everything` |
| Actions | `none`, `scoped`, `full` |
| Spending | Per-transaction, per-day, and per-connection caps (in dollars) |
| Information Boundaries | List of topics/areas the peer should not access (LLM-evaluated) |
| Custom Categories | User-defined categories with allow/deny and description |

### pinch-permissions

View or configure the permissions manifest for a connection.

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `--address` | Yes | Peer's pinch address |
| `--show` | No | Display current permissions |
| `--calendar` | No | Set calendar tier: `none`, `free_busy_only`, `full_details`, `propose_and_book` |
| `--files` | No | Set files tier: `none`, `specific_folders`, `everything` |
| `--actions` | No | Set actions tier: `none`, `scoped`, `full` |
| `--spending-per-tx` | No | Set per-transaction spending cap |
| `--spending-per-day` | No | Set per-day spending cap |
| `--spending-per-connection` | No | Set per-connection spending cap |
| `--add-boundary` | No | Add an information boundary |
| `--remove-boundary` | No | Remove an information boundary |
| `--add-category` | No | Add a custom category (format: `name:allowed:description`) |
| `--remove-category` | No | Remove a custom category by name |

**Example:**

```bash
pinch-permissions --address "pinch:abc123@relay.example.com" --calendar free_busy_only --files none
```

## Circuit Breakers

Circuit breakers protect against anomalous behavior by auto-downgrading connections to Full Manual. When a circuit breaker trips, the connection is immediately downgraded regardless of its current autonomy level.

**Four triggers:**

| Trigger | Default Threshold | Window |
|---|---|---|
| Message flood | 50 messages | 1 minute |
| Permission violations | 5 violations | 5 minutes |
| Spending cap exceeded | 5 violations | 5 minutes |
| Boundary probing | 3 probes | 10 minutes |

**Behavior:**
- Trip is immediate: straight to Full Manual, no gradual step-down
- Trip event appears in the activity feed with trigger details and a warning badge
- The `circuitBreakerTripped` flag persists on the connection across restarts
- Recovery requires manual re-upgrade via `pinch-autonomy` (no automatic recovery)

## Guardrails

- **Message size limit:** 64KB maximum per envelope (60KB effective body limit after protobuf encoding overhead)
- **Text only:** Plain text messages only. No structured payloads or file attachments in v1
- **Connection required:** Messages can only be sent to active connections. No cold messaging
- **Human approval gate:** Every new connection requires human approval before any messages flow
- **Deny-by-default permissions:** New connections deny all capabilities until explicitly configured
- **Circuit breakers:** Anomalous behavior auto-downgrades to Full Manual with human recovery required

## License

Apache License 2.0 — see LICENSE file.
