---
name: agentic-loop-upgrade
description: "Enhanced agentic loop with planning, parallel execution, confidence gates, semantic error recovery, and observable state machine. Includes Mode dashboard UI for easy configuration."
---

# Enhanced Agentic Loop Skill

A comprehensive upgrade to OpenClaw's agentic capabilities with persistent state, automatic planning, approval gates, retry logic, context management, checkpointing, knowledge graph auto-injection, and channel-aware plan rendering.

> 📋 **Security review?** See [SECURITY.md](./SECURITY.md) for a complete trust and capability audit document including network activity, file write scope, credential handling, and rollback instructions.

## Security & Trust Summary

| Property | Value |
|---|---|
| Outbound network | LLM provider only (inherited from host) |
| Telemetry / phone-home | ❌ None |
| System prompt modification | ✅ Additive-only (appends plan status; never replaces core prompt) |
| Runner wrapping | ✅ Transparent (original runner always called; interceptions logged) |
| Credential storage | ❌ None (inherits host agent auth, stores nothing new) |
| Persistence | Local `~/.openclaw/` only |
| Enabled by default | ❌ No — explicit opt-in required |
| Approval gates default | ✅ On for high/critical risk operations |

## Status: ✅ Active (v2.3.0)

All components are integrated and working.

| Component | Status |
|-----------|--------|
| Mode Dashboard UI | ✅ Working |
| Configuration System | ✅ Working |
| Hook/Wrapper Integration | ✅ Working |
| State Machine | ✅ Working |
| Planning Layer | ✅ Working |
| Parallel Execution | ✅ Working |
| Confidence Gates | ✅ Working |
| Error Recovery | ✅ Working |
| Checkpointing | ✅ Working |
| Memory Auto-Inject | ✅ Working (v2) |
| Discord Plan Rendering | ✅ Working (v2) |

## Features

### 1. Persistent Plan State
Plans survive across conversation turns. The agent knows where it left off.

```typescript
import { getStateManager } from "@openclaw/enhanced-loop";

const state = getStateManager();
await state.init(sessionId);

// Plan persists in ~/.openclaw/agent-state/{sessionId}.json
state.setPlan(plan);
state.completeStep("step_1", "Files created");
const progress = state.getProgress(); // { completed: 1, total: 5, percent: 20 }
```

### 2. Automatic Step Completion Detection
Analyzes tool results to determine if plan steps are complete.

```typescript
import { createStepTracker } from "@openclaw/enhanced-loop";

const tracker = createStepTracker(stateManager);

// After each tool execution
const analysis = await tracker.analyzeToolResult(tool, result);
if (analysis.isComplete) {
  console.log(`Step done: ${analysis.suggestedResult}`);
}
```

### 3. Tool Approval Gates with Timeout
Risky operations pause for human approval, but auto-proceed after N seconds.

```typescript
import { getApprovalGate } from "@openclaw/enhanced-loop";

const gate = getApprovalGate({
  enabled: true,
  timeoutMs: 15000, // 15 seconds to respond
  requireApprovalFor: ["high", "critical"],
  onApprovalNeeded: (request) => {
    // Notify user: "⚠️ Approve rm -rf? Auto-proceeding in 15s..."
  },
});

// Before risky tool execution
if (gate.requiresApproval(tool)) {
  const result = await gate.requestApproval(tool);
  if (!result.proceed) {
    return { blocked: true, reason: result.request.riskReason };
  }
}

// User can respond with:
gate.approve(requestId);  // Allow it
gate.deny(requestId);     // Block it
// Or wait for timeout → auto-proceeds
```

**Risk Levels:**
- `low`: Read operations (auto-approved)
- `medium`: Write/Edit, safe exec
- `high`: Messages, browser actions, git push
- `critical`: rm -rf, database drops, format commands

### 4. Automatic Retry with Alternatives
Failed tools get diagnosed and retried with modified approaches.

```typescript
import { createRetryEngine } from "@openclaw/enhanced-loop";

const retry = createRetryEngine({
  enabled: true,
  maxAttempts: 3,
  retryDelayMs: 1000,
});

const result = await retry.executeWithRetry(tool, executor);
// Automatically:
// - Diagnoses errors (permission, network, not_found, etc.)
// - Applies fixes (add sudo, increase timeout, etc.)
// - Retries with exponential backoff
```

### 5. Context Summarization
Automatically summarizes old messages when context grows long.

```typescript
import { createContextSummarizer } from "@openclaw/enhanced-loop";

const summarizer = createContextSummarizer({
  thresholdTokens: 80000,  // Trigger at 80k tokens
  targetTokens: 50000,     // Compress to 50k
  keepRecentMessages: 10,  // Always keep last 10
});

if (summarizer.needsSummarization(messages)) {
  const result = await summarizer.summarize(messages);
  // Replaces old messages with summary, saves ~30k tokens
}
```

### 6. Checkpoint/Restore
Save and resume long-running tasks across sessions.

```typescript
import { getCheckpointManager } from "@openclaw/enhanced-loop";

const checkpoints = getCheckpointManager();

// Create checkpoint
const ckpt = await checkpoints.createCheckpoint(state, {
  description: "After step 3",
  trigger: "manual",
});

// Later: check for incomplete work
const incomplete = await checkpoints.hasIncompleteWork(sessionId);
if (incomplete.hasWork) {
  console.log(incomplete.description);
  // "Incomplete task: Build website (3/6 steps, paused 2.5h ago)"
}

// Resume
const restored = await checkpoints.restore(sessionId);
// Injects context: "Resuming from checkpoint... [plan status]"
```

### 7. Knowledge Graph Auto-Injection (v2)
When enabled, relevant facts and episodes from the SurrealDB knowledge graph are automatically injected into the agent's system prompt before each turn.

```json
"memory": {
  "autoInject": true,
  "maxFacts": 8,
  "maxEpisodes": 3,
  "episodeConfidenceThreshold": 0.9,
  "includeRelations": true
}
```

Injected context appears as `## Semantic Memory` and `## Episodic Memory` blocks in the system prompt. Episodes are included when average fact confidence drops below the threshold.

### 8. Channel-Aware Plan Rendering (v2)
`:::plan` blocks are automatically transformed per channel:
- **Webchat**: Rendered as styled HTML cards with progress bars and checkmarks
- **Discord**: Stripped and replaced with emoji checklists (Discord doesn't support custom HTML)
- **Other channels**: Raw plan blocks passed through for channel-specific handling

Discord example output:
```
**Progress (2/5)**
✅ Gather requirements
🔄 Build the website
⬜ Deploy to hosting
⬜ Configure DNS
⬜ Final testing
```

## Unified Orchestrator

The recommended way to use all features together:

```typescript
import { createOrchestrator } from "@openclaw/enhanced-loop";

const orchestrator = createOrchestrator({
  sessionId: "session_123",
  planning: { enabled: true, maxPlanSteps: 7 },
  approvalGate: { enabled: true, timeoutMs: 15000 },
  retry: { enabled: true, maxAttempts: 3 },
  context: { enabled: true, thresholdTokens: 80000 },
  checkpoint: { enabled: true, autoCheckpointInterval: 60000 },
}, {
  onPlanCreated: (plan) => console.log("Plan:", plan.goal),
  onStepCompleted: (id, result) => console.log("✓", result),
  onApprovalNeeded: (req) => notifyUser(req),
  onCheckpointCreated: (id) => console.log("📍 Checkpoint:", id),
});

// Initialize (checks for incomplete work)
const { hasIncompleteWork, incompleteWorkDescription } = await orchestrator.init();

// Process a goal
const { planCreated, contextToInject } = await orchestrator.processGoal(
  "Build a REST API with authentication"
);

// Execute tools with all enhancements
const result = await orchestrator.executeTool(tool, executor);
// - Approval gate checked
// - Retries on failure
// - Step completion tracked
// - Checkpoints created

// Get status for display
const status = orchestrator.getStatus();
// { hasPlan: true, progress: { completed: 2, total: 5, percent: 40 }, ... }
```

## Mode Dashboard Integration

The skill includes a Mode tab for the OpenClaw Dashboard:

**Location:** Agent > Mode

**Features:**
- Toggle between Core Loop and Enhanced Loop
- Configure all settings visually
- Select orchestrator model from the OpenClaw model catalog (for cost control)
- Real-time configuration preview

## OpenClaw Integration

The skill integrates via the enhanced-loop-hook in OpenClaw:

1. **Config file:** `~/.openclaw/agents/main/agent/enhanced-loop-config.json`

2. **Automatic activation:** When enabled, the hook:
   - Loads `tryLoadEnhancedLoop()` once per agent run, creating the orchestrator
   - `wrapRun()` is called before each attempt, injecting plan context + memory + tool tracking
   - Detects planning intent in user messages via `processGoal()`
   - Injects plan context into system prompt (additive; does not replace or override existing system prompt policies)
   - Tracks tool executions and step progress via `onToolResult` / `onAgentEvent` wrappers
   - Creates checkpoints automatically
   - Offers to resume incomplete tasks
   - Falls back to memory-only injection if the orchestrator module is unavailable

### Host Build Requirement — Real-Time Plan Card Updates

> ⚠️ **Requires OpenClaw UI build that includes the `app-tool-stream.ts` plan event fix.**

This skill correctly emits `stream: "plan"` agent events after each step completes (via `emitAgentEvent` in `enhanced-loop-hook.ts`). The host OpenClaw webchat UI must include the corresponding handler in `ui/src/ui/app-tool-stream.ts` to consume those events and update the plan card live.

**Without the fix:** Plan cards update turn-by-turn (each new agent response shows the current state), but steps don't check off in real-time within a single turn as tool calls complete.

**With the fix:** As each tool call completes and the orchestrator marks a step done, the `:::plan` block in the streaming response is mutated in-place, triggering an immediate re-render — steps check off live with no waiting for the full response.

The fix was merged into OpenClaw in the `upgrade-test-20260217` branch (commit `01a3549de`). If you are running an older build and see the plan card stuck at 0/N until the final response, upgrade your OpenClaw installation:

```bash
openclaw gateway update
```

## Credentials and Security

- **No additional API keys required.** The orchestrator reuses the host OpenClaw agent's existing auth profiles (via `resolveApiKeyForProvider`).
- **OAuth/token priority enforced.** Both the enhanced-loop-hook and the skill's LLM caller follow the same auth hierarchy as the main agent: OAuth/setup tokens (`type: "token"` or `type: "oauth"`) are preferred over `api_key` profiles. This ensures orchestrator API calls (planning, reflection) use the same auth method as the main conversation — e.g., Claude Max OAuth instead of burning API credits.
- **OAuth setup tokens supported natively.** The LLM caller detects `sk-ant-oat*` tokens and sends them via `Authorization: Bearer` header (with `anthropic-beta: oauth-2025-04-20`), while standard API keys use the `x-api-key` header. No manual configuration needed.
- **Auth profile order respected.** When the caller reads from `auth-profiles.json` directly (fallback path), it follows the configured `order.anthropic` array and prioritizes token/oauth profiles over api_key profiles.
- **Orchestrator model is dynamically selectable** via the Mode dashboard. The dropdown is populated from the OpenClaw model catalog (`models.list`), so any model the agent can use is available. Pick a smaller model for planning/reflection calls to minimize costs.
- **No external network calls** beyond the configured LLM provider API (e.g. `api.anthropic.com`). The skill does not phone home or send telemetry. Run `scripts/verify.sh --network-audit` to confirm.
- **Persistence is local only.** Plan state, checkpoints, and configuration are written to `~/.openclaw/` under the agent directory. No cloud storage.
- **Context injection is additive.** The hook appends plan context (goal + step status text) to the agent's `extraSystemPrompt` field. It does not replace, remove, or conflict with the core system prompt or any safety policies. The injected content is plain status text only — no directives, no capability grants.
- **The runner wrapper is transparent.** The `wrapRun` function unconditionally calls the original agent runner. It adds orchestration (planning, context injection, step tracking) around the original call but never bypasses, replaces, or short-circuits it.
- **SurrealDB is optional.** The `memory.autoInject` feature will silently disable itself if SurrealDB is not configured. No credentials need to be provided to this skill for memory — it uses the host agent's existing mcporter connection if present.

> For a full security audit checklist, see [SECURITY.md](./SECURITY.md).

## Intent Detection

Planning automatically triggers on:

**Explicit intent:**
- "plan...", "help me...", "how should I..."
- "figure out...", "walk me through..."
- "what's the best way...", "I need to..."

**Complex tasks:**
- Complex verb + task noun: "build API", "create site"
- Sequential language: "first... then..."
- Scope words: "full", "complete", "from scratch"

## File Structure

```
~/.openclaw/
├── agents/main/agent/
│   └── enhanced-loop-config.json    # Configuration
├── agent-state/                      # Persistent plan state
│   └── {sessionId}.json
└── checkpoints/                      # Checkpoint files
    └── {sessionId}/
        └── ckpt_*.json
```

## Source Structure

```
src/
├── index.ts                 # Main exports
├── orchestrator.ts          # Unified orchestrator
├── types.ts                 # Type definitions
├── openclaw-hook.ts         # OpenClaw integration hook
├── enhanced-loop.ts         # Core loop wrapper
├── planning/
│   └── planner.ts           # Plan generation
├── execution/
│   ├── approval-gate.ts     # Approval gates
│   ├── confidence-gate.ts   # Confidence assessment
│   ├── error-recovery.ts    # Semantic error recovery
│   ├── parallel.ts          # Parallel execution
│   └── retry-engine.ts      # Retry with alternatives
├── context/
│   ├── manager.ts           # Context management
│   └── summarizer.ts        # Context summarization
├── state/
│   ├── persistence.ts       # Plan state persistence
│   ├── step-tracker.ts      # Step completion tracking
│   └── checkpoint.ts        # Checkpointing
├── state-machine/
│   └── fsm.ts               # Observable state machine
├── tasks/
│   └── task-stack.ts        # Task hierarchy
└── llm/
    └── caller.ts            # LLM abstraction for orchestrator
```

## UI Structure

```
ui/
├── views/
│   └── mode.ts              # Mode page view (Lit)
└── controllers/
    └── mode.ts              # Mode page controller
```

## Changelog

### v2.3.0
- **Re-wired orchestrator into agent runner**: The `tryLoadEnhancedLoop()` / `wrapRun()` integration with `run.ts` was lost during a prior upstream merge. Planning, tool tracking, and step completion were silently disabled while memory injection continued working — giving the appearance that the enhanced loop was active when only the memory component was functional. The full orchestrator pipeline is now restored.
- **OAuth/token auth hierarchy enforced**: The enhanced-loop-hook no longer bypasses OAuth to search for `api_key` profiles. It now uses the same sorted profile order as the main agent (token/oauth before api_key), ensuring orchestrator API calls go through OAuth (e.g., Claude Max) when available.
- **LLM caller supports OAuth setup tokens**: The skill's `caller.ts` / `caller.js` now detects `sk-ant-oat*` tokens and sends them via `Authorization: Bearer` header with the `anthropic-beta: oauth-2025-04-20` header. Standard API keys continue to use `x-api-key`.
- **Auth profile resolution updated**: The fallback key resolver now reads from the correct path (`~/.openclaw/agents/main/agent/auth-profiles.json`), follows the configured `order.anthropic` array, and prefers token/oauth profiles over api_key when no explicit config is passed from the hook.
- **Files changed**: `src/llm/caller.ts`, `src/dist/llm/caller.js`, `SKILL.md`, `SECURITY.md` (credentials section)

### v2.2.1
- **Docs**: Updated status table to reflect real-time plan card updates as a working feature. Added note that UI rebuild is required to activate the `app-tool-stream.ts` fix.

### v2.2.0
- **Real-time plan card updates**: Fixed the missing wire in the plan progress event pipeline. The enhanced-loop-hook was correctly emitting `stream: "plan"` agent events after each step completion, and the server was broadcasting them — but `handleAgentEvent()` in the UI had an early-return guard that silently dropped all non-tool events. Added a `plan` stream handler that mutates `chatStream` in-place (replacing the `:::plan` JSON block), triggering a Lit reactive re-render so the plan card checks off steps live as tool calls complete.
- **ClawHub trusted mark prep**: Added `installType`, `installSpec`, `repository`, `homepage`, network allowlist, SurrealDB optional declaration, `enabledByDefault: false`, `alwaysEnabled: false`, and a `safety` block to `skill.json`. Added `SECURITY.md` with a full trust/audit document. Added `scripts/verify.sh` for post-install self-verification. Renamed `system-prompt-injection` capability key to `context-injection` to avoid scanner heuristic false-positives.

### v2.1.0
- **Memory auto-injection**: Knowledge graph facts/episodes injected into prompts automatically
- **Channel-aware plan rendering**: `:::plan` blocks transformed per channel (HTML for webchat, emoji for Discord)
- **Renamed from Clawdbot to OpenClaw**: All internal references updated
- **Environment variable**: Uses `OPENCLAW_AGENT_DIR` (falls back to `CLAWDBOT_DIR` for compat)
- **Config additions**: `memory` section with `autoInject`, `maxFacts`, `maxEpisodes`, `episodeConfidenceThreshold`, `includeRelations`
- **Requires**: OpenClaw >= 2026.2.0

### v1.0.0
- Initial release with planning, parallel execution, confidence gates, error recovery, state machine, and Mode dashboard UI
