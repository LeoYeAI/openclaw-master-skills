# OpenClaw Sub-Agents Reference

## Table of Contents

- [Overview](#overview)
- [Slash Commands](#slash-commands)
- [Tool: sessions_spawn](#tool-sessions_spawn)
- [Spawn Behavior](#spawn-behavior)
- [Thread-Bound Sessions](#thread-bound-sessions)
- [Nested Sub-Agents](#nested-sub-agents)
- [Authentication](#authentication)
- [Announce Mechanism](#announce-mechanism)
- [Tool Policy](#tool-policy)
- [Concurrency](#concurrency)
- [Auto-Archive](#auto-archive)
- [Stopping & Cascade](#stopping--cascade)
- [Configuration](#configuration)
- [Limitations](#limitations)

## Overview

Sub-agents are isolated sessions spawned from the main agent to parallelize research, long tasks, or slow tool calls without blocking the main run. They run inside the Pi runtime (internal), unlike [ACP agents](acp_agents.md) which run external runtimes.

Design goals:
- Parallelize work without blocking the main run
- Keep sub-agents isolated (session separation + optional sandboxing)
- Keep the tool surface hard to misuse (no session tools by default)
- Support configurable nesting depth for orchestrator patterns

## Slash Commands

### Core Sub-agent Commands

| Command | Description |
|---|---|
| `/subagents list` | List active sub-agent sessions |
| `/subagents kill <id\|#\|all>` | Stop a sub-agent (or all) |
| `/subagents log <id\|#> [limit] [tools]` | View sub-agent transcript |
| `/subagents info <id\|#>` | Detailed sub-agent info |
| `/subagents send <id\|#> <message>` | Send message to sub-agent |
| `/subagents steer <id\|#> <message>` | Nudge sub-agent without replacing context |
| `/subagents spawn <agentId> <task>` | Spawn new sub-agent (one-shot `mode: "run"`) |

Options for `/subagents spawn`:
- `--model <model>` — override model
- `--thinking <level>` — override thinking level

### Thread & Focus Commands

| Command | Description |
|---|---|
| `/focus <target>` | Bind current thread to a sub-agent/session target |
| `/unfocus` | Remove thread binding |
| `/agents` | List active runs and binding state (`thread:<id>` or `unbound`) |
| `/session idle <duration\|off>` | Set/inspect inactivity auto-unfocus |
| `/session max-age <duration\|off>` | Set/inspect hard cap age |

## Tool: sessions_spawn

The programmatic equivalent of `/subagents spawn`. Called by the agent as a tool.

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `task` | string | *required* | Task description for the sub-agent |
| `label` | string | — | Human label for the session |
| `agentId` | string | current | Target agent (if allowed by `allowAgents`) |
| `runtime` | enum | `"subagent"` | `"subagent"` or `"acp"` |
| `model` | string | inherited | Override model; invalid values are skipped with warning |
| `thinking` | string | inherited | Override thinking level |
| `runTimeoutSeconds` | number | config/0 | Abort after N seconds (0 = no timeout) |
| `thread` | boolean | `false` | Request thread binding |
| `mode` | enum | `"run"` | `"run"` (one-shot) or `"session"` (persistent, requires `thread: true`) |
| `cleanup` | enum | `"keep"` | `"delete"` archives immediately after announce |
| `sandbox` | enum | `"inherit"` | `"require"` rejects spawn if target runtime is not sandboxed |
| `attachments` | array | — | Inline files (subagent only) |
| `attachAs` | string | — | Attachment mode |

### Mode Behavior

| Mode | Thread | Description |
|---|---|---|
| `"run"` | `false` | One-shot: run task → announce → done |
| `"run"` | `true` | One-shot + thread binding (auto-unbinds) |
| `"session"` | `true` | Persistent thread-bound session (follow-ups routed) |

**Note**: `mode: "session"` requires `thread: true`.

### Return Value

Always non-blocking:
```json
{ "status": "accepted", "runId": "...", "childSessionKey": "agent:<id>:subagent:<uuid>" }
```

### Inheritance Priority

| Setting | Priority (highest first) |
|---|---|
| Model | `sessions_spawn.model` → `agents.list[].subagents.model` → `agents.defaults.subagents.model` → caller's model |
| Thinking | `sessions_spawn.thinking` → `agents.list[].subagents.thinking` → `agents.defaults.subagents.thinking` → caller's thinking |
| Timeout | `sessions_spawn.runTimeoutSeconds` → `agents.defaults.subagents.runTimeoutSeconds` → `0` |

### Requirements

- `sessions_spawn` does not accept channel-delivery params (`target`, `channel`, `to`, `threadId`, `replyTo`, `transport`)
- For delivery from a sub-agent, use `message`/`sessions_send` tools from within the spawned run
- Use `agents_list` to check which agent IDs are allowed for `sessions_spawn`

## Spawn Behavior

1. `sessions_spawn` / `/subagents spawn` is **non-blocking** — returns immediately
2. On completion, the sub-agent runs an **announce step** (summarizes results back to requester)
3. Delivery is resilient:
   - OpenClaw tries direct agent delivery first with a stable idempotency key
   - Falls back to queue routing if direct fails
   - Retried with short exponential backoff before final give-up

### Completion Handoff

The announce contains:
- **Result**: assistant reply text (or latest toolResult if reply is empty)
- **Status**: `completed successfully` / `failed` / `timed out` / `unknown`
- **Runtime stats**: runtime duration, token usage (input/output/total), estimated cost
- **Session info**: `sessionKey`, `sessionId`, transcript path
- **Delivery instruction**: tells requester agent to rewrite in normal assistant voice

Status is derived from **runtime outcome signals**, not inferred from model output.

## Thread-Bound Sessions

### How It Works

1. Spawn with `sessions_spawn` using `thread: true` (and optionally `mode: "session"`)
2. OpenClaw creates or binds a thread to that session target in the active channel
3. Replies and follow-up messages in that thread route to the bound session
4. Use `/session idle` / `/session max-age` to control expiry
5. Use `/unfocus` to detach manually

### Thread-Supporting Channels

| Channel | Support |
|---|---|
| **Discord** | ✅ Full support |
| Others | Not yet supported |

Discord config:
```json5
{
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,      // 0 = no hard expiry
        spawnSubagentSessions: true,
      },
    },
  },
}
```

Global defaults:
```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
}
```

### Agent Targeting

- `agents.list[].subagents.allowAgents`: list of agent IDs allowed via `agentId`
- `["*"]` allows any agent
- Default: only the requester agent
- **Sandbox guard**: if requester session is sandboxed, `sessions_spawn` rejects unsandboxed targets

## Nested Sub-Agents

### How to Enable

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2,         // allow sub-agents to spawn children (default: 1)
        maxChildrenPerAgent: 5,   // max active children per agent session (default: 5)
        maxConcurrent: 8,         // global concurrency lane cap (default: 8)
        runTimeoutSeconds: 900,   // default timeout (0 = no timeout)
      },
    },
  },
}
```

### Depth Levels

| Depth | Session Key | Tool Access |
|---|---|---|
| 0 (main) | `agent:<id>:main` | Full tools |
| 1 (orchestrator, `maxSpawnDepth >= 2`) | `agent:<id>:subagent:<uuid>` | Gets `sessions_spawn`, `subagents`, `sessions_list`, `sessions_history` |
| 1 (leaf, `maxSpawnDepth == 1`) | `agent:<id>:subagent:<uuid>` | No session tools |
| 2 (leaf worker) | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | No session tools; `sessions_spawn` always denied |

### Announce Chain

1. Depth-2 worker finishes → announces to its parent (depth-1 orchestrator)
2. Depth-1 orchestrator synthesizes results, finishes → announces to main
3. Main agent delivers to the user

### Cascade Stop

- `/stop` in main chat stops all depth-1 agents and cascades to depth-2 children
- `/subagents kill <id>` stops a specific sub-agent and cascades to its children
- `/subagents kill all` stops all sub-agents and cascades

## Authentication

- Sub-agent session key: `agent:<agentId>:subagent:<uuid>`
- Auth store loaded from that agent's `agentDir`
- Main agent's auth profiles merged as fallback; agent profiles override on conflicts

## Announce Mechanism

The announce step runs **inside the sub-agent session** (not the requester session).

- If sub-agent replies exactly `ANNOUNCE_SKIP`, nothing is posted
- Otherwise, the announce reply is posted to the requester chat channel via a follow-up agent call (`deliver=true`)
- Announce replies preserve thread/topic routing when available

### Announce Context Block

| Field | Description |
|---|---|
| source | `subagent` or `cron` |
| child session key/id | Sub-agent session identity |
| announce type + task label | What was spawned |
| status | Derived from runtime outcome (success/error/timeout/unknown) |
| result content | From announce step (or `(no output)` if missing) |
| follow-up instruction | When to reply vs. stay silent |
| runtime | Duration (e.g., `runtime 5m12s`) |
| token usage | input/output/total |
| estimated cost | When model pricing is configured |

Internal metadata is for orchestration only; user-facing replies should be rewritten in normal assistant voice.

## Tool Policy

Sub-agents have restricted session tools by default:

- `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn` — **denied by default**
- When `maxSpawnDepth >= 2`: depth-1 orchestrators get `sessions_spawn`, `subagents`, `sessions_list`, `sessions_history`
- At depth 2: `sessions_spawn` is always denied

### Custom Tool Policy

```json5
{
  agents: {
    defaults: {
      subagents: { maxConcurrent: 1 },
    },
  },
  tools: {
    subagents: {
      tools: {
        deny: ["gateway", "cron"],              // deny wins
        // allow: ["read", "exec", "process"]   // if set, becomes allow-only
      },
    },
  },
}
```

## Concurrency

- Lane name: `subagent`
- Limit: `agents.defaults.subagents.maxConcurrent` (default: **8**)
- Per-agent limit: `maxChildrenPerAgent` (default: **5**, range: 1–20)

## Auto-Archive

- Sessions archived after `agents.defaults.subagents.archiveAfterMinutes` (default: **60**)
- Archive uses `sessions.delete` and renames transcript to `*.deleted.<timestamp>`
- `cleanup: "delete"` archives immediately after announce (still keeps transcript via rename)
- Auto-archive is best-effort; pending timers lost if Gateway restarts
- `runTimeoutSeconds` only stops the run; doesn't auto-archive (session remains until auto-archive)
- Auto-archive applies equally to depth-1 and depth-2 sessions

## Stopping & Cascade

| Action | Effect |
|---|---|
| `/stop` in requester chat | Aborts requester + stops all spawned sub-agents → cascades to nested children |
| `/subagents kill <id>` | Stops specific sub-agent → cascades to children |
| `/subagents kill all` | Stops all sub-agents → cascades |

## Configuration

### Full Config Example

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2,
        maxChildrenPerAgent: 5,
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
        model: "anthropic/claude-sonnet-4-5",     // optional default model
        thinking: "medium",                        // optional default thinking
      },
    },
    list: [{
      id: "main",
      subagents: {
        allowAgents: ["research", "coding"],      // restrict target agents
        // model, thinking overrides per-agent
      },
    }],
  },
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  tools: {
    subagents: {
      tools: {
        deny: ["gateway", "cron"],
      },
    },
  },
}
```

## Limitations

- Announce is **best-effort** — if Gateway restarts, pending "announce back" work is lost
- Sub-agents share Gateway process resources; treat `maxConcurrent` as a safety valve
- `sessions_spawn` always returns `{ status: "accepted" }` immediately (non-blocking)
- Sub-agent context only injects `AGENTS.md` + `TOOLS.md` (no `SOUL.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`)
- Maximum nesting depth: **5** (`maxSpawnDepth` range: 1–5). Depth 2 recommended
- `maxChildrenPerAgent`: range 1–20, default 5

## See Also

- [ACP Agents](acp_agents.md) — external runtime agents (Codex, Claude, Gemini CLI)
- [Sessions](sessions.md) — session management and key mapping
- [Tools](tools.md) — sessions_spawn tool parameters
