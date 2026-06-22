# Sub-Agent Memory Propagation

## Problem

Sub-agents spawned via `sessions_spawn` do **NOT** receive the full set of bootstrap
files. They only get `AGENTS.md` and `TOOLS.md`. This means BrainX-injected context
(which lives in `MEMORY.md`) never reaches sub-agents.

## Investigation Findings

### What OpenClaw docs confirm

From `docs/concepts/system-prompt.md`:

> Sub-agent sessions only inject `AGENTS.md` and `TOOLS.md` (other bootstrap files
> are filtered out to keep the sub-agent context small).

This is by design — the `promptMode` for sub-agents is set to `minimal`, which:
- **Includes**: Tooling, Safety, Workspace, Sandbox, Current Date & Time, Runtime,
  and injected context (`AGENTS.md` + `TOOLS.md`)
- **Omits**: Skills, Memory Recall, OpenClaw Self-Update, Model Aliases, User Identity,
  Reply Tags, Messaging, Silent Replies, Heartbeats, `SOUL.md`, `IDENTITY.md`,
  `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`, **`MEMORY.md`**

### Available hook event: `agent:bootstrap`

From `docs/automation/hooks.md`:

> **`agent:bootstrap`**: Before workspace bootstrap files are injected
> (hooks may mutate `context.bootstrapFiles`)

The `agent:bootstrap` event fires before bootstrap files are injected and provides
`context.bootstrapFiles` — an array that hooks can **mutate**. The existing
`bootstrap-extra-files` bundled hook already uses this mechanism to inject
additional files.

**However**, there is an important caveat from the `bootstrap-extra-files` docs:

> Subagent allowlist is preserved (`AGENTS.md` and `TOOLS.md` only).

This means the `promptMode=minimal` filtering happens **after** hooks mutate
`bootstrapFiles`. Even if you inject `MEMORY.md` via a hook, it gets filtered
out for sub-agents.

### No `before_prompt_build` event

There is no `before_prompt_build` hook event. The available events are:
- `command:*` (new, reset, stop)
- `agent:bootstrap`
- `gateway:startup`
- `message:*` (received, transcribed, preprocessed, sent)

### `sessions_spawn` task field

The `task` parameter in `sessions_spawn` is injected as the sub-agent's initial
instruction. This is currently the **only reliable mechanism** to pass arbitrary
context to sub-agents.

## Proposed Solutions

### Solution 1: Embed key memories in `task` field (RECOMMENDED — works today)

The parent agent can query BrainX before spawning and include critical memories
directly in the `task` string:

```javascript
// In the parent agent's workflow:
const memories = await brainxInject("relevant query", { limit: 5 });
sessions_spawn({
  task: `## Context from BrainX\n${memories}\n\n## Task\n${actualTask}`,
  label: "worker"
});
```

**Pros**: Works immediately, no code changes needed.
**Cons**: Parent must know what context is relevant; increases task payload size.

### Solution 2: Put critical context in AGENTS.md or TOOLS.md

Since sub-agents DO receive `AGENTS.md` and `TOOLS.md`, the BrainX hook could
write a compact summary section into one of these files instead of (or in
addition to) `MEMORY.md`.

The current `handler.js` already writes to the workspace. It could append a
`<!-- BRAINX:START -->` section to `TOOLS.md` instead of `MEMORY.md`.

**Pros**: Automatic, no parent agent changes needed.
**Cons**: Bloats files that sub-agents always receive; TOOLS.md/AGENTS.md aren't
meant for memory data; risk of hitting `bootstrapMaxChars` truncation.

### Solution 3: Modify the sub-agent bootstrap allowlist (requires OpenClaw change)

Request a config option to extend the sub-agent bootstrap allowlist:

```json5
{
  agents: {
    defaults: {
      subagents: {
        bootstrapFiles: ["AGENTS.md", "TOOLS.md", "MEMORY.md"]
      }
    }
  }
}
```

**Pros**: Clean, configurable solution.
**Cons**: Requires upstream OpenClaw change; may increase sub-agent context size.

### Solution 4: BrainX-aware sub-agent hook

Create an `agent:bootstrap` hook that detects sub-agent sessions and injects a
lightweight BrainX summary into the sub-agent's context via `event.messages.push()`:

```typescript
const handler = async (event) => {
  if (event.type !== 'agent' || event.action !== 'bootstrap') return;

  // Detect if this is a sub-agent session
  const isSubagent = event.sessionKey?.includes(':subagent:');
  if (!isSubagent) return;

  // Query BrainX for top memories
  const summary = await queryBrainXSummary();

  // Push as a message to the sub-agent context
  event.messages.push(`## 🧠 BrainX Context\n${summary}`);
};
```

**Pros**: Automatic; only fires for sub-agents; uses existing hook system.
**Cons**: `event.messages` may not inject into the system prompt (it appends
user-visible messages, not bootstrap context); needs testing to confirm behavior.

## Recommendation

**Short-term (now)**: Use Solution 1. The parent/orchestrator agent should query
BrainX and embed relevant memories in the `task` field when spawning sub-agents.
This is already possible and requires zero changes.

**Medium-term**: Implement Solution 2 — modify the BrainX `handler.js` to also
write a compact BrainX summary section into `TOOLS.md` (under a `<!-- BRAINX -->`
marker). This way sub-agents automatically get top-level memories.

**Long-term**: Request Solution 3 upstream — a configurable `subagents.bootstrapFiles`
list in OpenClaw config would be the cleanest approach.

## References

- OpenClaw docs: `concepts/system-prompt.md` — promptMode minimal behavior
- OpenClaw docs: `tools/subagents.md` — sub-agent context limitations
- OpenClaw docs: `automation/hooks.md` — agent:bootstrap event API
- OpenClaw docs: `concepts/context.md` — what counts toward context window
- BrainX hook: `hook/handler.js` — current MEMORY.md injection logic
