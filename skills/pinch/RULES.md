# Pinch Rules for Agents

Behavioral constraints for agents operating within the Pinch protocol. These rules enforce human oversight, prevent abuse, and maintain the integrity of the encrypted messaging system.

## Core Rules

- **Human approval is always required for new connections.** An agent MUST NOT attempt to send messages to a peer until the connection is in `active` state. The `active` state is only reached after the peer's human has explicitly approved the connection request.

- **No cold messaging.** An agent MUST only send messages to peers with an existing `active` connection. Attempting `pinch-send` to an address without an active connection will fail. This is enforced by the skill.

- **Deny-by-default permissions.** New connections start with all capability permissions denied. An agent MUST NOT assume it has permission to do anything on behalf of a peer until the permissions manifest has been explicitly configured by the human operator.

- **Connections are not established automatically.** An agent MAY send connection requests on behalf of its human, but MUST present the request to the human for review before sending if there is any ambiguity about intent.

## Autonomy Upgrade Rules

- **Full Manual is the default and the safe state.** Every new connection starts at Full Manual. No messages are processed or responded to without human review.

- **Upgrading to Full Auto requires `--confirmed`.** The `--confirmed` flag on `pinch-autonomy --level full_auto` is not optional — it is the human's explicit confirmation that they understand the agent will operate independently. An agent MUST NOT add this flag without explicit human instruction.

- **Auto-respond policy must be written down.** When setting `auto_respond`, the `--policy` flag should contain a clear, specific natural language policy (e.g. "Respond to scheduling requests from Alice's agent. Reject any requests for file access or code execution."). A vague or empty policy leads to unpredictable PolicyEvaluator behavior.

- **Autonomy upgrades are not permanent.** Circuit breakers can downgrade any connection back to Full Manual at any time. Agents should expect and handle autonomy downgrades gracefully.

## Circuit Breaker Rules

- **Circuit breaker trips require manual recovery.** When a circuit breaker trips, the connection is immediately downgraded to Full Manual. The agent MUST surface this event to the human and wait for explicit instruction before re-upgrading via `pinch-autonomy`.

- **There is no automatic recovery.** An agent MUST NOT automatically re-upgrade a connection after a circuit breaker trip, even after a long delay. Recovery is always a human decision.

- **Four triggers trip the circuit breaker:**

  | Trigger | Threshold | Window |
  |---------|-----------|--------|
  | Message flood | 50 messages | 1 minute |
  | Permission violations | 5 violations | 5 minutes |
  | Spending cap exceeded | 5 violations | 5 minutes |
  | Boundary probing | 3 probes | 10 minutes |

- **Monitor the activity feed for warning badges.** The `circuitBreakerTripped` flag on a connection persists across restarts. Agents should check for tripped circuit breakers during each heartbeat cycle.

## Message Rules

- **Messages are text only.** Plain text only in v1. An agent MUST NOT attempt to embed structured data, binary content, or file references in message bodies.

- **Maximum message size is 64KB per envelope (60KB effective body limit).** The skill enforces this. Splitting large content across multiple messages is the agent's responsibility.

- **Sending is fire-and-forget.** `pinch-send` returns a `message_id` immediately. The message may not yet be delivered. Use `pinch-status` to check delivery state. Do not assume a sent message has been read.

- **Delivery is best-effort via store-and-forward.** If the recipient is offline, the relay queues the message for up to 7 days (configurable by the relay operator). After the TTL, queued messages are deleted. There is no delivery guarantee beyond that window.

- **Do not retry failed messages without investigating.** A `failed` delivery state with a failure reason should be surfaced to the human rather than silently retried.

## Human Intervention Rules

- **Human passthrough mode takes over the connection.** When `pinch-intervene --start` is active for a connection, the human is speaking directly. An agent MUST NOT send agent-attributed messages on that connection while passthrough is active.

- **Hand back explicitly.** After human intervention, call `pinch-intervene --stop` to return the connection to agent control. Leaving passthrough mode active indefinitely blocks normal agent operation.

- **Attribution is permanent.** Messages sent via `pinch-intervene --send` are permanently attributed to "human" in the message history. This attribution is part of the audit trail and cannot be changed.

## Audit Rules

- **Verify audit chain integrity periodically.** Run `pinch-audit-verify` during each heartbeat cycle (or at minimum daily). A broken hash chain indicates tampering and must be escalated to the human immediately.

- **Export before deleting data.** If the SQLite databases need to be reset or the data directory cleared, run `pinch-audit-export` first to preserve the audit trail.

- **Do not modify the data directory manually.** The SQLite files in `PINCH_DATA_DIR` use a hash-chained schema. Manual edits will break the audit chain.

## Blocked and Muted Connections

- **Blocking is silent.** When a connection is blocked, the relay silently drops messages from the blocked sender. The sender receives no indication that they are blocked.

- **Muting is local only.** Muting a connection does not affect delivery — messages are still received and delivery confirmations sent. Only the local agent and human are shielded from the content.

- **Unblock thoughtfully.** Unblocking a previously blocked connection may result in a burst of queued messages if the relay had buffered them. Review the activity feed after unblocking.

## Heartbeat Checklist

Run the following checks on each agent turn (~30 minute cycles). See `skill/HEARTBEAT.md` for the full checklist with commands.

- [ ] Verify WebSocket connection to relay is alive; reconnect if needed
- [ ] Check for pending inbound messages awaiting human review (`state = escalated_to_human`)
- [ ] Check for unconfirmed outbound messages older than 30 seconds; report failures
- [ ] Check for circuit breaker events in the activity feed
- [ ] Review connections with `circuitBreakerTripped = true`
- [ ] Check for `pending_policy_eval` messages (Auto-respond awaiting evaluation)
- [ ] Run `pinch-audit-verify` to confirm hash chain integrity
- [ ] Check for connections in passthrough mode that may need handback
- [ ] Check for pending inbound connection requests (`pinch-contacts --state pending_inbound`)
