# Guardian Angel Plugin Specification

**Version:** 1.0.0-draft  
**Status:** DRAFT  
**Date:** 2026-02-07  
**Author:** Leo Linbeck III & Reginald Jeeves

---

## Overview

This specification defines an OpenClaw plugin that enforces the Guardian Angel virtue-based moral framework at the tool execution layer. The plugin acts as the **final gate** before any tool executes, evaluating actions through the lens of Thomistic virtue ethics.

### Design Goals

1. **Atomic enforcement** — Evaluation happens immediately before tool execution, eliminating TOCTOU vulnerabilities
2. **Escalation with approval** — Ambiguous/high-stakes actions can be blocked pending user confirmation
3. **One-time approvals** — Approved actions are bound to specific parameters and expire quickly
4. **Tamper detection** — Startup diagnostic warns if other hooks could override GA decisions
5. **Virtue integration** — Evaluation uses the existing GA v3.0 framework, not rules

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TOOL CALL FLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Agent Request → [other hooks] → GUARDIAN ANGEL → Tool Execution   │
│                                      │                              │
│                            ┌─────────┴─────────┐                    │
│                            │                   │                    │
│                         ALLOW              BLOCK                    │
│                            │                   │                    │
│                            ▼                   ▼                    │
│                       Execute           Return blockReason          │
│                                                │                    │
│                                                ▼                    │
│                                    Agent asks user for approval     │
│                                                │                    │
│                                                ▼                    │
│                                    User approves (or denies)        │
│                                                │                    │
│                                                ▼                    │
│                                    Agent calls ga_approve tool      │
│                                                │                    │
│                                                ▼                    │
│                                    Agent retries original tool      │
│                                                │                    │
│                                                ▼                    │
│                                    GA sees valid approval → ALLOW   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Plugin Structure

```
~/.openclaw/workspace/.openclaw/extensions/guardian-angel/
├── openclaw.plugin.json      # Plugin manifest
├── index.ts                  # Entry point
├── package.json              # Dependencies
└── src/
    ├── hook.ts               # before_tool_call implementation
    ├── evaluate.ts           # Virtue-based evaluation logic
    ├── approve-tool.ts       # ga_approve tool implementation
    ├── store.ts              # Nonce storage (file-based)
    ├── diagnostics.ts        # Startup hook priority check
    ├── types.ts              # TypeScript types
    └── constants.ts          # Priority, timeouts, etc.
```

---

## Plugin Manifest

**File:** `openclaw.plugin.json`

```json
{
  "id": "guardian-angel",
  "name": "Guardian Angel",
  "version": "1.0.0",
  "description": "Virtue-based moral conscience for AI agents. Evaluates tool calls through Thomistic ethics and blocks/escalates high-stakes actions.",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "enabled": {
        "type": "boolean",
        "default": true
      },
      "logLevel": {
        "type": "string",
        "enum": ["debug", "info", "warn", "error"],
        "default": "info"
      },
      "escalationThreshold": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "default": 36,
        "description": "Clarity × Stakes score above which to escalate"
      },
      "pendingTimeoutMs": {
        "type": "integer",
        "minimum": 60000,
        "maximum": 600000,
        "default": 300000,
        "description": "How long a blocked action awaits approval (5 min default)"
      },
      "approvalWindowMs": {
        "type": "integer",
        "minimum": 10000,
        "maximum": 120000,
        "default": 30000,
        "description": "How long after approval the retry must occur (30s default)"
      },
      "storePath": {
        "type": "string",
        "description": "Path to nonce store file (default: workspace/.ga-state.json)"
      },
      "alwaysBlock": {
        "type": "array",
        "items": { "type": "string" },
        "default": [],
        "description": "Tool names that always require explicit approval"
      },
      "neverBlock": {
        "type": "array",
        "items": { "type": "string" },
        "default": ["memory_search", "memory_get", "session_status"],
        "description": "Tool names exempt from GA evaluation"
      }
    }
  },
  "uiHints": {
    "enabled": {
      "label": "Enable Guardian Angel",
      "help": "Master toggle for virtue-based tool evaluation"
    },
    "escalationThreshold": {
      "label": "Escalation Threshold",
      "help": "Clarity × Stakes score (1-100) above which actions require approval"
    },
    "pendingTimeoutMs": {
      "label": "Pending Timeout (ms)",
      "advanced": true
    },
    "approvalWindowMs": {
      "label": "Approval Window (ms)",
      "advanced": true
    },
    "alwaysBlock": {
      "label": "Always Require Approval",
      "help": "Tool names that always need explicit user confirmation"
    },
    "neverBlock": {
      "label": "Exempt Tools",
      "help": "Tool names that bypass GA evaluation"
    }
  }
}
```

---

## Hook Implementation

### Priority

```typescript
const GA_PRIORITY = -10000;
```

**Rationale:** Ensures GA runs last among all `before_tool_call` hooks. Standard hooks default to 0; security-critical hooks should use large negative values.

### Registration

```typescript
// index.ts
import type { OpenClawPluginApi } from "openclaw/plugin-types";
import { createBeforeToolCallHandler } from "./src/hook.js";
import { createApprovalTool } from "./src/approve-tool.js";
import { createStore } from "./src/store.js";
import { runStartupDiagnostics } from "./src/diagnostics.js";

export default function register(api: OpenClawPluginApi) {
  const config = api.pluginConfig as GuardianAngelConfig;
  const store = createStore(config, api);
  
  // Register the before_tool_call hook (runs LAST)
  api.on(
    "before_tool_call",
    createBeforeToolCallHandler(config, store, api.logger),
    { priority: GA_PRIORITY }
  );
  
  // Register the approval tool
  api.registerTool(createApprovalTool(store, api.logger));
  
  // Run startup diagnostics
  api.on("gateway_start", () => runStartupDiagnostics(api), { priority: 0 });
  
  api.logger.info("Guardian Angel active (priority: -10000)");
}
```

---

## Hook Logic

### `before_tool_call` Handler

```typescript
// src/hook.ts
import type {
  PluginHookBeforeToolCallEvent,
  PluginHookBeforeToolCallResult,
  PluginHookToolContext,
} from "openclaw/plugin-types";
import { evaluate } from "./evaluate.js";
import type { Store } from "./store.js";
import type { GuardianAngelConfig } from "./types.js";

export function createBeforeToolCallHandler(
  config: GuardianAngelConfig,
  store: Store,
  logger: PluginLogger
) {
  return async (
    event: PluginHookBeforeToolCallEvent,
    ctx: PluginHookToolContext
  ): Promise<PluginHookBeforeToolCallResult | void> => {
    const { toolName, params } = event;
    
    // 1. Check exemptions
    if (config.neverBlock?.includes(toolName)) {
      logger.debug?.(`[GA] ${toolName}: exempt, allowing`);
      return; // Allow
    }
    
    // 2. Check if this call has a valid approval
    const paramsHash = store.hashParams(toolName, params);
    const approval = store.consumeApproval(paramsHash);
    if (approval) {
      logger.info(`[GA] ${toolName}: approved via nonce ${approval.nonce}`);
      return; // Allow (approval consumed)
    }
    
    // 3. Check alwaysBlock list
    if (config.alwaysBlock?.includes(toolName)) {
      return escalate(toolName, params, paramsHash, store, logger,
        `Tool '${toolName}' requires explicit approval per configuration.`);
    }
    
    // 4. Run virtue-based evaluation
    const result = await evaluate(toolName, params, ctx, config, logger);
    
    switch (result.decision) {
      case "allow":
        logger.debug?.(`[GA] ${toolName}: virtues aligned, allowing`);
        return; // Allow
        
      case "block":
        // Intrinsic evil or hard block — no approval possible
        logger.warn(`[GA] ${toolName}: BLOCKED (${result.reason})`);
        return {
          block: true,
          blockReason: `GUARDIAN_ANGEL_BLOCK|${result.reason}`,
        };
        
      case "escalate":
        return escalate(toolName, params, paramsHash, store, logger, result.reason);
    }
  };
}

function escalate(
  toolName: string,
  params: Record<string, unknown>,
  paramsHash: string,
  store: Store,
  logger: PluginLogger,
  reason: string
): PluginHookBeforeToolCallResult {
  // Generate and store nonce
  const nonce = store.createPending(paramsHash, toolName, params);
  
  logger.info(`[GA] ${toolName}: escalating (nonce: ${nonce})`);
  
  // Return structured block reason the agent can parse
  return {
    block: true,
    blockReason: `GUARDIAN_ANGEL_ESCALATE|${nonce}|${reason}`,
  };
}
```

---

## Evaluation Logic

### Virtue-Based Evaluation

```typescript
// src/evaluate.ts
import type { PluginHookToolContext } from "openclaw/plugin-types";
import type { GuardianAngelConfig, EvaluationResult } from "./types.js";

// Tools that affect system infrastructure
const INFRASTRUCTURE_TOOLS = [
  "gateway",        // config changes, restarts, updates
  "exec",           // shell commands
  "Write",          // file writes
  "Edit",           // file edits
];

// Tools with external effects
const EXTERNAL_EFFECT_TOOLS = [
  "message",        // sending messages
  "browser",        // web automation
  "cron",           // scheduled tasks
  "nodes",          // device control
];

export async function evaluate(
  toolName: string,
  params: Record<string, unknown>,
  ctx: PluginHookToolContext,
  config: GuardianAngelConfig,
  logger: PluginLogger
): Promise<EvaluationResult> {
  
  // === GATE I: Intrinsic Evil Check ===
  const intrinsicCheck = checkIntrinsicEvil(toolName, params);
  if (intrinsicCheck) {
    return { decision: "block", reason: intrinsicCheck };
  }
  
  // === GATE V: Virtue Evaluation ===
  const clarity = assessClarity(toolName, params);
  const stakes = assessStakes(toolName, params);
  const score = clarity * stakes;
  
  logger.debug?.(`[GA] ${toolName}: clarity=${clarity} stakes=${stakes} score=${score}`);
  
  // Check against threshold
  if (score >= config.escalationThreshold) {
    const reason = buildEscalationReason(toolName, params, clarity, stakes);
    return { decision: "escalate", reason };
  }
  
  // Below threshold — virtues aligned
  return { decision: "allow" };
}

function checkIntrinsicEvil(
  toolName: string,
  params: Record<string, unknown>
): string | null {
  // Check for patterns that indicate intrinsically evil actions
  // This is illustrative; full implementation would be more comprehensive
  
  if (toolName === "message") {
    const content = String(params.message || "").toLowerCase();
    // Deception, calumny, etc.
    if (containsDeceptionPatterns(content)) {
      return "Message appears to contain deliberate deception (violation of truth)";
    }
  }
  
  if (toolName === "exec") {
    const cmd = String(params.command || "").toLowerCase();
    // Destructive commands without clear purpose
    if (cmd.includes("rm -rf /") || cmd.includes(":(){ :|:& };:")) {
      return "Command appears destructive without legitimate purpose";
    }
  }
  
  return null; // No intrinsic evil detected
}

function assessClarity(toolName: string, params: Record<string, unknown>): number {
  // 1 = morally obvious, 10 = deeply ambiguous
  let clarity = 1;
  
  // Infrastructure tools are inherently less clear
  if (INFRASTRUCTURE_TOOLS.includes(toolName)) {
    clarity += 3;
  }
  
  // External effects add uncertainty
  if (EXTERNAL_EFFECT_TOOLS.includes(toolName)) {
    clarity += 2;
  }
  
  // Specific parameter analysis
  if (toolName === "gateway") {
    const action = String(params.action || "");
    if (action === "config.apply" || action === "config.patch") {
      clarity += 3; // Config changes are high-ambiguity
    }
    if (action === "update.run") {
      clarity += 2;
    }
  }
  
  if (toolName === "exec") {
    const cmd = String(params.command || "");
    if (cmd.includes("sudo") || cmd.includes("rm ")) {
      clarity += 2;
    }
  }
  
  return Math.min(clarity, 10);
}

function assessStakes(toolName: string, params: Record<string, unknown>): number {
  // 1 = trivial, 10 = life-altering/irreversible
  let stakes = 1;
  
  // Infrastructure = high stakes (can disable the agent)
  if (INFRASTRUCTURE_TOOLS.includes(toolName)) {
    stakes += 4;
  }
  
  // Specific high-stakes patterns
  if (toolName === "gateway") {
    const action = String(params.action || "");
    if (action === "config.apply" || action === "config.patch") {
      // Check if changing model (could lock out)
      const raw = String(params.raw || "");
      if (raw.includes("model") || raw.includes("defaultModel")) {
        stakes += 3; // Model changes can cause lockout
      }
    }
  }
  
  if (toolName === "exec") {
    const cmd = String(params.command || "");
    if (cmd.includes("rm ") && !cmd.includes("-i")) {
      stakes += 3; // Deletions are high stakes
    }
    if (cmd.includes("kill") || cmd.includes("shutdown") || cmd.includes("reboot")) {
      stakes += 4;
    }
  }
  
  if (toolName === "message") {
    // Sending to contacts has relationship stakes
    stakes += 2;
  }
  
  return Math.min(stakes, 10);
}

function buildEscalationReason(
  toolName: string,
  params: Record<string, unknown>,
  clarity: number,
  stakes: number
): string {
  const parts: string[] = [];
  
  parts.push(`Action: ${toolName}`);
  parts.push(`Risk score: ${clarity * stakes} (clarity=${clarity}, stakes=${stakes})`);
  
  // Add specific concerns
  if (toolName === "gateway" && String(params.action).includes("config")) {
    parts.push("This modifies OpenClaw configuration.");
  }
  if (toolName === "exec") {
    parts.push(`Command: ${String(params.command).slice(0, 100)}`);
  }
  
  return parts.join(" | ");
}

function containsDeceptionPatterns(content: string): boolean {
  // Placeholder — full implementation would use more sophisticated detection
  return false;
}
```

---

## Approval Tool

### `ga_approve` Tool Definition

```typescript
// src/approve-tool.ts
import { Type } from "@sinclair/typebox";
import type { Store } from "./store.js";

export function createApprovalTool(store: Store, logger: PluginLogger) {
  return {
    name: "ga_approve",
    description: `Approve a Guardian Angel escalation. Use this after the user confirms they want to proceed with a blocked action. The nonce comes from the GUARDIAN_ANGEL_ESCALATE block reason.`,
    parameters: Type.Object({
      nonce: Type.String({
        description: "The escalation nonce from the block reason (e.g., 'a7f3c2')",
      }),
      reason: Type.Optional(Type.String({
        description: "Optional: user's reason for approving",
      })),
    }),
    async execute(
      _id: string,
      params: { nonce: string; reason?: string }
    ) {
      const { nonce, reason } = params;
      
      const result = store.approvePending(nonce);
      
      if (!result.ok) {
        logger.warn(`[GA] Approval failed for nonce ${nonce}: ${result.error}`);
        return {
          content: [{
            type: "text",
            text: `Approval failed: ${result.error}`,
          }],
        };
      }
      
      logger.info(`[GA] Approved nonce ${nonce}${reason ? ` (reason: ${reason})` : ""}`);
      
      return {
        content: [{
          type: "text",
          text: `✓ Approved. You may now retry the action. Approval valid for ${result.windowSeconds}s.`,
        }],
      };
    },
  };
}
```

---

## Nonce Store

### File-Based Storage

```typescript
// src/store.ts
import { createHash, randomBytes } from "node:crypto";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import type { GuardianAngelConfig, PendingEscalation, ApprovedAction } from "./types.js";

export interface Store {
  hashParams(toolName: string, params: Record<string, unknown>): string;
  createPending(paramsHash: string, toolName: string, params: Record<string, unknown>): string;
  approvePending(nonce: string): { ok: true; windowSeconds: number } | { ok: false; error: string };
  consumeApproval(paramsHash: string): { nonce: string } | null;
  cleanup(): void;
}

interface StoreState {
  pending: Record<string, PendingEscalation>;
  approved: Record<string, ApprovedAction>;
}

export function createStore(config: GuardianAngelConfig, api: OpenClawPluginApi): Store {
  const storePath = config.storePath || api.resolvePath(".ga-state.json");
  const pendingTimeoutMs = config.pendingTimeoutMs || 300000;
  const approvalWindowMs = config.approvalWindowMs || 30000;
  
  function load(): StoreState {
    if (!existsSync(storePath)) {
      return { pending: {}, approved: {} };
    }
    try {
      return JSON.parse(readFileSync(storePath, "utf-8"));
    } catch {
      return { pending: {}, approved: {} };
    }
  }
  
  function save(state: StoreState): void {
    writeFileSync(storePath, JSON.stringify(state, null, 2));
  }
  
  function hashParams(toolName: string, params: Record<string, unknown>): string {
    const normalized = JSON.stringify({ toolName, params }, Object.keys(params).sort());
    return createHash("sha256").update(normalized).digest("hex").slice(0, 16);
  }
  
  function createPending(paramsHash: string, toolName: string, params: Record<string, unknown>): string {
    const state = load();
    const nonce = randomBytes(4).toString("hex"); // 8 hex chars
    
    state.pending[nonce] = {
      nonce,
      paramsHash,
      toolName,
      params,
      createdAt: Date.now(),
      expiresAt: Date.now() + pendingTimeoutMs,
    };
    
    save(state);
    return nonce;
  }
  
  function approvePending(nonce: string): { ok: true; windowSeconds: number } | { ok: false; error: string } {
    const state = load();
    const pending = state.pending[nonce];
    
    if (!pending) {
      return { ok: false, error: "Nonce not found or already used" };
    }
    
    if (Date.now() > pending.expiresAt) {
      delete state.pending[nonce];
      save(state);
      return { ok: false, error: "Escalation expired. Please retry the original action." };
    }
    
    // Move from pending to approved
    delete state.pending[nonce];
    state.approved[pending.paramsHash] = {
      nonce,
      paramsHash: pending.paramsHash,
      toolName: pending.toolName,
      approvedAt: Date.now(),
      expiresAt: Date.now() + approvalWindowMs,
    };
    
    save(state);
    return { ok: true, windowSeconds: Math.round(approvalWindowMs / 1000) };
  }
  
  function consumeApproval(paramsHash: string): { nonce: string } | null {
    const state = load();
    const approved = state.approved[paramsHash];
    
    if (!approved) {
      return null;
    }
    
    if (Date.now() > approved.expiresAt) {
      delete state.approved[paramsHash];
      save(state);
      return null;
    }
    
    // Consume (one-time use)
    delete state.approved[paramsHash];
    save(state);
    
    return { nonce: approved.nonce };
  }
  
  function cleanup(): void {
    const state = load();
    const now = Date.now();
    
    let changed = false;
    for (const [nonce, pending] of Object.entries(state.pending)) {
      if (now > pending.expiresAt) {
        delete state.pending[nonce];
        changed = true;
      }
    }
    for (const [hash, approved] of Object.entries(state.approved)) {
      if (now > approved.expiresAt) {
        delete state.approved[hash];
        changed = true;
      }
    }
    
    if (changed) save(state);
  }
  
  // Cleanup on load
  cleanup();
  
  return {
    hashParams,
    createPending,
    approvePending,
    consumeApproval,
    cleanup,
  };
}
```

---

## Startup Diagnostics

### Hook Priority Check

```typescript
// src/diagnostics.ts
import type { OpenClawPluginApi } from "openclaw/plugin-types";
import { GA_PRIORITY } from "./constants.js";

export async function runStartupDiagnostics(api: OpenClawPluginApi): Promise<void> {
  // Access the hook registry (this would need OpenClaw to expose it)
  // For now, this is a specification of what we WANT to check
  
  const logger = api.logger;
  
  logger.info("[GA] Running startup diagnostics...");
  
  // Ideally: check if any other before_tool_call hook has lower priority
  // This requires OpenClaw to expose hook introspection
  
  // Placeholder implementation:
  // We would query: api.runtime.hooks?.list?.("before_tool_call")
  // And check if any have priority < GA_PRIORITY
  
  // For now, log a note about the limitation
  logger.info(`[GA] Registered at priority ${GA_PRIORITY}. ` +
    `Hooks with lower priority could override decisions. ` +
    `This is a known limitation pending OpenClaw hook introspection API.`);
  
  // Future implementation:
  /*
  const hooks = api.runtime.hooks?.list?.("before_tool_call") ?? [];
  const lowerPriorityHooks = hooks.filter(h => 
    h.pluginId !== "guardian-angel" && 
    (h.priority ?? 0) < GA_PRIORITY
  );
  
  if (lowerPriorityHooks.length > 0) {
    logger.warn(
      `[GA] ⚠️ SECURITY WARNING: ${lowerPriorityHooks.length} hook(s) registered ` +
      `with lower priority than Guardian Angel. These could override GA decisions:\n` +
      lowerPriorityHooks.map(h => `  - ${h.pluginId} (priority: ${h.priority})`).join("\n")
    );
  } else {
    logger.info("[GA] ✓ No hooks registered below Guardian Angel priority.");
  }
  */
}
```

---

## Types

```typescript
// src/types.ts

export interface GuardianAngelConfig {
  enabled?: boolean;
  logLevel?: "debug" | "info" | "warn" | "error";
  escalationThreshold?: number;
  pendingTimeoutMs?: number;
  approvalWindowMs?: number;
  storePath?: string;
  alwaysBlock?: string[];
  neverBlock?: string[];
}

export interface EvaluationResult {
  decision: "allow" | "block" | "escalate";
  reason?: string;
}

export interface PendingEscalation {
  nonce: string;
  paramsHash: string;
  toolName: string;
  params: Record<string, unknown>;
  createdAt: number;
  expiresAt: number;
}

export interface ApprovedAction {
  nonce: string;
  paramsHash: string;
  toolName: string;
  approvedAt: number;
  expiresAt: number;
}
```

---

## Constants

```typescript
// src/constants.ts

/** Guardian Angel hook priority. Lower = runs later. -10000 ensures we run last. */
export const GA_PRIORITY = -10000;

/** Default escalation threshold (Clarity × Stakes) */
export const DEFAULT_ESCALATION_THRESHOLD = 36;

/** Default pending timeout: 5 minutes */
export const DEFAULT_PENDING_TIMEOUT_MS = 300000;

/** Default approval window: 30 seconds */
export const DEFAULT_APPROVAL_WINDOW_MS = 30000;
```

---

## Block Reason Protocol

### Format

The plugin uses a structured block reason format that the agent can parse:

```
GUARDIAN_ANGEL_BLOCK|<reason>
GUARDIAN_ANGEL_ESCALATE|<nonce>|<reason>
```

### Agent Handling

When the agent receives a block reason starting with `GUARDIAN_ANGEL_`:

1. **BLOCK**: Action is prohibited. Explain to user why it cannot be done.
2. **ESCALATE**: Action requires confirmation.
   - Parse nonce from second field
   - Present reason to user
   - If user approves: call `ga_approve({ nonce })`, then retry original tool
   - If user denies: acknowledge and do not retry

### Example Agent Response (Escalation)

```
Guardian Angel has paused this action for your review:

**Action:** gateway config.apply
**Concern:** This modifies OpenClaw configuration. Risk score: 42 (clarity=6, stakes=7)

This could affect system stability. Do you want to proceed?

(Approval ref: a7f3c21b)
```

---

## Configuration Example

```json5
{
  plugins: {
    entries: {
      "guardian-angel": {
        enabled: true,
        config: {
          logLevel: "info",
          escalationThreshold: 36,
          pendingTimeoutMs: 300000,
          approvalWindowMs: 30000,
          alwaysBlock: [
            "gateway"  // All gateway actions require approval
          ],
          neverBlock: [
            "memory_search",
            "memory_get",
            "session_status",
            "Read"
          ]
        }
      }
    }
  }
}
```

---

## Integration with SKILL.md

The plugin enforces the framework defined in `SKILL.md`. The evaluation logic (`evaluate.ts`) should:

1. **Apply Gate I** (Intrinsic Evil) — Hard block, no approval possible
2. **Apply Gate V** (Virtue Evaluation) — Calculate Clarity × Stakes
3. **Use threshold from config** — Default 36 maps to "Pause" in SKILL.md

The plugin does NOT replace the agent's internal virtue disposition. It acts as an enforcement layer that:
- Catches actions the agent might not have fully evaluated
- Provides a second check at execution time
- Enables user override for legitimate edge cases

---

## Security Considerations

### Threat Model

**In scope:**
- Agent being manipulated via prompt injection
- Agent misunderstanding user intent
- Accidental harmful actions

**Out of scope:**
- Attacker with ability to install plugins (full system compromise)
- Attacker with access to OpenClaw config
- Attacker who can modify plugin source code

### Startup Warning

The diagnostic check warns if other hooks could override GA. This is defense-in-depth, not a guarantee. If an attacker can install plugins, they have full system access.

### Nonce Security

- Nonces are 8 hex characters (32 bits of entropy)
- Nonces are one-time use
- Pending nonces expire after 5 minutes
- Approved actions expire after 30 seconds
- Approval is bound to exact parameter hash

---

## Future Enhancements

1. **Hook introspection API** — Request OpenClaw expose hook registry for startup diagnostics
2. **Irrevocable blocks** — Request OpenClaw make `block: true` non-overridable by later hooks
3. **Signed approvals** — Use HMAC to prevent approval token forgery
4. **Audit log** — Persistent log of all escalations and approvals
5. **Learning mode** — Track which escalations are approved to tune thresholds

---

## Changelog

### 1.0.0-draft (2026-02-07)
- Initial specification
- before_tool_call hook with priority -10000
- ga_approve tool for escalation flow
- File-based nonce storage
- Startup diagnostic for hook priority
- Integration with GA v3.0 virtue framework
