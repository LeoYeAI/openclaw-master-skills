# Gateway Pairing Reference

> Source: https://docs.openclaw.ai/gateway/pairing

## Overview

Gateway-owned pairing controls which nodes (iOS, Android, macOS companion apps) can connect to the Gateway. Nodes must be explicitly approved before they can interact.

## Concepts

| Term | Meaning |
|---|---|
| **Pending request** | A node asked to join; requires approval |
| **Paired node** | Approved node with an issued auth token |
| **Transport** | Gateway WS endpoint forwards requests but does not decide membership |

## How Pairing Works

1. A node connects to the Gateway WS and requests pairing.
2. The Gateway stores a pending request and emits `node.pair.requested`.
3. You approve or reject the request (CLI or UI).
4. On approval, the Gateway issues a **new token** (tokens are rotated on re-pair).
5. The node reconnects using the token and is now "paired".

## CLI Workflow (Headless Friendly)

```bash
openclaw nodes pending                               # List pending requests
openclaw nodes approve <requestId>                   # Approve
openclaw nodes reject <requestId>                    # Reject
openclaw nodes status                                # Show all paired nodes
openclaw nodes rename --node <id|name|ip> --name "Living Room iPad"  # Rename
```

## API Surface (Gateway Protocol)

### Events
| Event | When |
|---|---|
| `node.pair.requested` | New pending request created |
| `node.pair.resolved` | Request approved/rejected/expired |

### RPC Methods
| Method | Purpose |
|---|---|
| `node.pair.request` | Create or reuse a pending request (idempotent per node) |
| `node.pair.list` | List pending + paired nodes |
| `node.pair.approve` | Approve pending request (issues token) |
| `node.pair.reject` | Reject pending request |
| `node.pair.verify` | Verify `{ nodeId, token }` |

### Important
- `node.pair.request` is idempotent: repeated calls return the same pending request.
- Approval always generates a **fresh** token; no token is ever returned from `node.pair.request`.
- Requests may include `silent: true` as a hint for auto-approval flows.

## Auto-Approval (macOS App)

The macOS app auto-approves when:
- The request is marked `silent`, AND
- The app can verify an SSH connection to the gateway host using the same user.

## Storage (Local, Private)

Located under `~/.openclaw/` (or `OPENCLAW_STATE_DIR`):

| File | Purpose |
|---|---|
| `~/.openclaw/nodes/paired.json` | Paired nodes with tokens (**sensitive**) |
| `~/.openclaw/nodes/pending.json` | Pending requests |

- **Tokens are secrets**: treat `paired.json` as sensitive.
- Rotating a token requires re-approval (or deleting the node entry).

## Transport Behavior

- Transport is **stateless**; it does not store membership.
- If the Gateway is offline or pairing is disabled, nodes cannot pair.
- If the Gateway is in remote mode, pairing happens against the remote Gateway's store.

## See Also

- [gateway_internals.md](gateway_internals.md) — Network model, lock, health
- [nodes.md](nodes.md) — iOS, Android, macOS companion apps
- [presence_discovery.md](presence_discovery.md) — Discovery mechanisms
