# Agent Runtime & Agent Loop

> Sources:
> - https://docs.openclaw.ai/concepts/agent
> - https://docs.openclaw.ai/concepts/agent-loop
> - https://docs.openclaw.ai/concepts/agent-workspace

## Agent Runtime

### Workspace (Required)

- Set via `agents.defaults.workspace` or `cwd` during `openclaw setup`.
- Config: `~/.openclaw/openclaw.json`.
- Sandbox: `agents.defaults.sandbox` / `agents.defaults.sandbox.workspaceRoot`.

### Bootstrap Files (Injected)

Files injected into `agents.defaults.workspace`:

| File | Purpose |
|---|---|
| `AGENTS.md` | Operating instructions + "memory" |
| `SOUL.md` | Persona, boundaries, tone |
| `TOOLS.md` | User-maintained tool notes (e.g. imsg, sag, conventions) |
| `BOOTSTRAP.md` | One-time first-run ritual (deleted after completion) |
| `IDENTITY.md` | Agent name/vibe/emoji |
| `USER.md` | User profile + preferred address |

- Created by `openclaw setup`.
- Skip bootstrap: `{ agent: { skipBootstrap: true } }`.

### Skills

- Bundled (shipped with the install)
- Managed/local: `~/.openclaw/skills`
- Workspace: `<workspace>/skills`

### pi-mono Integration

- No pi-coding agent runtime.
- No `~/.pi/agent` or `<workspace>/.pi` settings are consulted.

### Sessions

- Stored at: `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

### Steering While Streaming

- `steer` / `followup` / `collect` modes.
- Config: `agents.defaults.blockStreamingDefault: "off"`, `agents.defaults.blockStreamingBreak`, `agents.defaults.blockStreamingChunk`, `agents.defaults.blockStreamingCoalesce`.
- Per-channel: `*.blockStreaming: true`.

### Model Refs

- Config at `agents.defaults.model` / `agents.defaults.models`.
- Use `provider/model` format. If model ID itself contains `/` (OpenRouter-style), include the provider prefix (e.g. `openrouter/moonshotai/kimi-k2`).
- If provider is omitted, OpenClaw treats input as an alias or model for the default provider.

### Minimal Configuration

- `agents.defaults.workspace`
- `channels.whatsapp.allowFrom` (strongly recommended)

---

## Agent Loop

### Entry Points

- Gateway RPC: `agent` and `agent.wait`.
- CLI: `agent` command.

### How It Works (High-Level)

1. `agent` RPC validates params, resolves session (`sessionKey`/`sessionId`), persists session metadata, returns `{ runId, acceptedAt }` immediately.
2. `agentCommand` runs the agent:
   - Resolves model + thinking/verbose defaults
   - Loads skills snapshot
   - Calls `runEmbeddedPiAgent` (pi-agent-core runtime)
   - Emits lifecycle end/error if the embedded loop does not emit one
3. `runEmbeddedPiAgent`:
   - Serializes runs via per-session + global queues
   - Resolves model + auth profile and builds the pi session
   - Subscribes to pi events and streams assistant/tool deltas
   - Enforces timeout → aborts run if exceeded
   - Returns payloads + usage metadata
4. `subscribeEmbeddedPiSession` bridges pi-agent-core events to OpenClaw agent stream:
   - tool events ⇒ `stream: "tool"`
   - assistant deltas ⇒ `stream: "assistant"`
   - lifecycle events ⇒ `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` uses `waitForAgentJob`:
   - Waits for lifecycle end/error for `runId`
   - Returns `{ status: ok|error|timeout, startedAt, endedAt, error? }`

### Queueing + Concurrency

- Runs are serialized per session key (session lane) and optionally through a global lane.
- Prevents tool/session races and keeps session history consistent.
- Messaging channels can choose queue modes (`collect`/`steer`/`followup`).

### Prompt Assembly + System Prompt

- Built from OpenClaw's base prompt, skills prompt, bootstrap context, and per-run overrides.
- Model-specific limits and compaction reserve tokens are enforced.

### Hook Points

#### Internal Hooks (Gateway Hooks)

- `agent:bootstrap`: runs while building bootstrap files before the system prompt is finalized.
- Command hooks: `/new`, `/reset`, `/stop`, and other command events.

#### Plugin Hooks (Agent + Gateway Lifecycle)

| Hook | Description |
|---|---|
| `before_model_resolve` | Pre-session (no messages), override provider/model |
| `before_prompt_build` | Post-session load, inject `prependContext`, `systemPrompt`, etc. |
| `before_agent_start` | Legacy compatibility hook |
| `agent_end` | Inspect final messages and run metadata |
| `before_compaction` / `after_compaction` | Observe/annotate compaction cycles |
| `before_tool_call` / `after_tool_call` | Intercept tool params/results |
| `tool_result_persist` | Transform tool results before session write |
| `message_received` / `message_sending` / `message_sent` | Inbound + outbound message hooks |
| `session_start` / `session_end` | Session lifecycle boundaries |
| `gateway_start` / `gateway_stop` | Gateway lifecycle events |

### Streaming + Partial Replies

- Assistant deltas streamed from pi-agent-core as `assistant` events.
- Block streaming on `text_end` or `message_end`.

### Reply Shaping + Suppression

- `NO_REPLY` is treated as a silent token, filtered from outgoing payloads.
- Messaging tool duplicates are removed from the final payload list.
- If no renderable payloads remain and a tool errored, a fallback tool error reply is emitted.

### Timeouts

- `agent.wait` default: 30s (just the wait). `timeoutMs` param overrides.
- Agent runtime: `agents.defaults.timeoutSeconds` default 600s; enforced in `runEmbeddedPiAgent` abort timer.

### Event Streams

| Stream | Source |
|---|---|
| `lifecycle` | `subscribeEmbeddedPiSession` (and fallback `agentCommand`) |
| `assistant` | Streamed deltas from pi-agent-core |
| `tool` | Streamed tool events from pi-agent-core |

### Where Things Can End Early

- Agent timeout (abort)
- AbortSignal (cancel)
- Gateway disconnect or RPC timeout
- `agent.wait` timeout (wait-only, does not stop agent)

---

## Context Engine

Controls how OpenClaw builds model context for each run.

### Lifecycle Points

1. **Ingest** — stores/indexes new messages
2. **Assemble** — returns ordered messages fitting token budget
3. **Compact** — summarizes older history when context fills
4. **After turn** — persists state, triggers background compaction

### Plugin Registration

Plugins can register custom context engines:

```ts
api.registerContextEngine("my-engine", () => ({
  info: { id: "my-engine", name: "My Context Engine", ownsCompaction: true },
  async ingest({ sessionId, message }) { ... },
  async assemble({ sessionId, messages, tokenBudget }) { ... },
  async compact({ sessionId, force }) { ... },
}));
```

### Configuration

```json5
{
  plugins: {
    slots: { contextEngine: "legacy" }, // or plugin name
  },
}
```

---

## Session Pruning

Removes aged tool outputs before LLM requests. Benefits Anthropic prompt caching.

- Mode: `cache-ttl` — only `toolResult` messages pruned; user/assistant messages preserved
- Defaults: TTL 5 min, keepLastAssistants 3, softTrimRatio 0.3, hardClearRatio 0.5

Separate from compaction (can use both). Pruning is per-request and does not persist changes.
