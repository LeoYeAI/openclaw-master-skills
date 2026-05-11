# Agent-to-Agent Communication — Detailed Reference

This document contains the complete configuration and patterns for inter-agent
communication in OpenClaw. Read this when implementing Phase 6 of the team builder.

---

## The Master Switch: `tools.agentToAgent`

This is a **global config** (not per-agent). It must be explicitly enabled:

```json5
{
  tools: {
    agentToAgent: {
      enabled: true,
      allow: ["planner", "coder", "reviewer", "writer"],
      // List ALL agent IDs that are allowed to communicate
    },
  },
}
```

Without `agentToAgent.enabled: true`, `sessions_send` between agents **will not work**.

---

## Communication Primitive 1: `sessions_send` (Synchronous Conversation)

Use when you want agents to have a direct back-and-forth exchange.

**How it works**:
1. Agent A sends a message to Agent B's session via `sessions_send`
2. Agent B processes and replies
3. OpenClaw can run a reply-back ping-pong (controlled by `maxPingPongTurns`, 0–5)
4. After ping-pong ends, Agent B runs an **announce step** — posting a summary to the channel
5. Agent B can reply `REPLY_SKIP` to stop ping-pong early, `ANNOUNCE_SKIP` to suppress announcement

**Configuration**:

```json5
{
  session: {
    agentToAgent: {
      maxPingPongTurns: 2,  // Allow up to 2 back-and-forth exchanges
    },
  },
}
```

**Targeting**: `sessions_send` requires a `sessionKey`. The pattern is:
- `agent:<agentId>:<mainKey>` for main/DM sessions
- `agent:<agentId>:discord:channel:<channelId>` for Discord group sessions

**Tool requirements**: The sending agent must have `sessions_send` in its tools allow list:

```json5
{
  id: "planner",
  tools: {
    allow: ["sessions_list", "sessions_history", "sessions_send", "session_status"],
  },
}
```

---

## Communication Primitive 2: `sessions_spawn` (Async Task Delegation)

Use when an orchestrator wants to delegate a task to a specialist agent.

**How it works**:
1. Agent A spawns a sub-agent task targeting Agent B
2. Agent B runs in an **isolated session** (`agent:<agentId>:subagent:<uuid>`)
3. Agent B works independently, then **announces** the result back to Agent A's channel
4. Sub-agent sessions auto-archive after `agents.defaults.subagents.archiveAfterMinutes` (default: 60)

**Configuration**:

```json5
{
  agents: {
    list: [
      {
        id: "planner",
        subagents: {
          allowAgents: ["coder", "reviewer", "writer"],
        },
      },
      {
        id: "coder",
        subagents: {
          allowAgents: ["planner"],
        },
      },
    ],
    defaults: {
      subagents: {
        model: "anthropic/claude-sonnet-4-20250514",
        runTimeoutSeconds: 300,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

**Key constraints**:
- Sub-agents **cannot call `sessions_spawn`** (no sub-agent → sub-agent chaining)
- Sub-agents default to full tool set **minus session tools** (configurable via `tools.subagents.tools`)
- Always non-blocking: returns `{ status: "accepted", runId }` immediately

---

## Session Visibility

Controls which sessions an agent can "see" with `sessions_list` and `sessions_history`:

```json5
{
  tools: {
    sessions: {
      visibility: "agent",
      // "self" — only current session
      // "tree" — current + spawned sub-agents (default)
      // "agent" — any session belonging to same agent
      // "all" — all sessions (cross-agent, requires agentToAgent)
    },
  },
}
```

For team collaboration, the orchestrator typically needs `visibility: "all"` while
specialists use the default `"tree"`.

---

## Loop Detection (Safety Net)

Even with ping-pong limits, enable loop detection as a safety net:

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

---

## Recommended Communication Patterns

| Pattern | Mechanism | When to Use |
|---------|-----------|-------------|
| Orchestrator dispatches task | `sessions_spawn` | Planner sends work to Coder |
| Agent asks another for input | `sessions_send` | Coder asks Reviewer for feedback |
| Group @-mention relay | Discord @mention | Visible, human-auditable collaboration |
| Fire-and-forget notification | `sessions_send` with `timeoutSeconds: 0` | Status updates |

---

## Send Policy (Optional Fine-Tuning)

Control where `sessions_send` can deliver messages:

```json5
{
  session: {
    sendPolicy: {
      rules: [
        // Example: deny agent-to-agent sends into Discord groups
        {
          match: { channel: "discord", chatType: "group" },
          action: "deny"
        }
      ],
      default: "allow"
    }
  }
}
```
