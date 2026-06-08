# OpenClaw Hooks Reference

## Table of Contents

- [Overview](#overview)
- [Two Systems: Internal Hooks vs HTTP Webhooks](#two-systems-internal-hooks-vs-http-webhooks)
- [Internal Hooks](#internal-hooks)
  - [Architecture](#architecture)
  - [Event Types](#event-types)
  - [Hook Directory Structure](#hook-directory-structure)
  - [HOOK.md Metadata](#hookmd-metadata)
  - [handler.ts Implementation](#handlerts-implementation)
  - [Bundled Hooks](#bundled-hooks)
  - [Hook Packs](#hook-packs)
  - [CLI Commands](#cli-commands)
  - [Configuration](#configuration)
  - [Custom Hook Authoring](#custom-hook-authoring)
- [HTTP Webhooks](#http-webhooks)
  - [Enable](#enable)
  - [Endpoints](#endpoints)
  - [Auth](#auth)
  - [Session Key Policy](#session-key-policy)
  - [Security](#security)
- [Use Cases & Patterns](#use-cases--patterns)
- [Troubleshooting](#troubleshooting)

---

## Overview

OpenClaw's **Hooks** system provides an extensible, event-driven mechanism for automating actions in response to agent commands, lifecycle events, and external triggers — all **without modifying core code**.

There are **two distinct systems** both referred to as "hooks":

1. **Internal Hooks** — local event handlers running inside the Gateway process
2. **HTTP Webhooks** — inbound HTTP endpoints allowing external systems to trigger OpenClaw

---

## Two Systems: Internal Hooks vs HTTP Webhooks

| Aspect | Internal Hooks | HTTP Webhooks |
|---|---|---|
| **Direction** | Inside-out: respond to internal events | Outside-in: external HTTP calls trigger OpenClaw |
| **Runtime** | Execute within Gateway process | Gateway exposes HTTP endpoints |
| **Language** | TypeScript (`handler.ts`) | Any HTTP client (curl, GitHub, Stripe, n8n) |
| **Auth** | N/A (trusted local execution) | Requires `gateway.auth.token` or `gateway.auth.password` |
| **Config key** | Managed via `openclaw hooks` CLI | `gateway.webhooks.enabled` / `hooks.enabled` + `hooks.token` |
| **Use cases** | Audit logging, session memory, bootstrap injection | GitHub webhooks, Stripe events, external automation |

---

## Internal Hooks

### Architecture

Internal hooks are small TypeScript scripts that execute when specific events fire within the OpenClaw Gateway. They are:

- **Automatically discovered** from designated directories
- **Managed via CLI** (enable/disable/install)
- **Event-driven** — each hook subscribes to one or more event types
- **Scoped** — workspace hooks override managed hooks, which override bundled hooks

### Event Types

#### Command Events

| Event | Trigger |
|---|---|
| `command` | Any command event (wildcard listener) |
| `command:new` | User issues `/new` command |
| `command:reset` | User issues `/reset` command |
| `command:stop` | User issues `/stop` command |

#### Agent Events

| Event | Trigger |
|---|---|
| `agent:bootstrap` | Before workspace bootstrap files are injected; hooks can modify `context.bootstrapFiles` |

#### Gateway Events

| Event | Trigger |
|---|---|
| `gateway:startup` | After channels have started and hooks are loaded |

#### Message Events

| Event | Trigger |
|---|---|
| `message` | Any message event (wildcard listener) |
| `message:received` | Inbound message received from any channel (early pipeline) |
| `message:transcribed` | Message fully processed, including audio transcription |
| `message:preprocessed` | After all media and link understanding is complete |

#### Future Events (Planned)

| Event | Trigger |
|---|---|
| `session:start` | When a new session begins |
| `session:end` | When a session concludes |
| `agent:error` | When an agent encounters an error |

### Hook Directory Structure

Hooks are discovered from three directories, processed in **precedence order**:

| Priority | Location | Scope |
|---|---|---|
| 1 (highest) | `<workspace>/hooks/` | Per-agent workspace hooks |
| 2 | `~/.openclaw/hooks/` | User-managed hooks, shared across workspaces |
| 3 (lowest) | `<openclaw>/dist/hooks/bundled/` | Bundled hooks shipped with OpenClaw |

Each hook is a **directory** containing:

```
my-hook/
├── HOOK.md        # Metadata + documentation (required)
└── handler.ts     # Hook logic (required, can also be index.ts)
```

Additional directories can be specified via configuration (see [Configuration](#configuration)).

### HOOK.md Metadata

The `HOOK.md` file contains YAML frontmatter for metadata, followed by Markdown documentation.

```markdown
---
metadata:
  openclaw:
    name: session-memory
    description: Save session context to memory on /new
    emoji: 🧠
    events:
      - command:new
    requires:
      bins: []
      env: []
---

# Session Memory Hook

This hook automatically saves the current session context to the agent's
workspace memory when the user issues the `/new` command, preserving
conversation continuity across sessions.
```

**Frontmatter fields** (under `metadata.openclaw`):

| Field | Type | Description |
|---|---|---|
| `name` | string | Hook identifier (used in CLI commands) |
| `description` | string | Short description |
| `emoji` | string | Display emoji |
| `events` | string[] | List of event types this hook subscribes to |
| `requires.bins` | string[] | Required binaries (hook won't activate if missing) |
| `requires.env` | string[] | Required environment variables |

### handler.ts Implementation

The `handler.ts` file exports a `HookHandler` function that receives an event object.

```typescript
import type { HookHandler } from "openclaw/hooks";

export const handler: HookHandler = async (event) => {
  // event.type — the event type string (e.g. "command:new")
  // event.context — contextual data (varies by event type)
  // event.config — per-hook configuration

  if (event.type === "command:new") {
    // Save session context to memory file
    const sessionData = event.context.sessionSummary;
    // ... write to workspace memory ...
    console.log("[session-memory] Saved session context");
  }
};
```

**Event object properties** (vary by event type):

| Property | Description |
|---|---|
| `event.type` | The event type string |
| `event.context` | Rich context object (session data, bootstrap files, message content, etc.) |
| `event.config` | Per-hook custom configuration |

For `agent:bootstrap` events, hooks can modify `event.context.bootstrapFiles` to inject additional files into the workspace.

### Bundled Hooks

OpenClaw ships with several pre-built hooks:

| Hook | Events | Description |
|---|---|---|
| `session-memory` | `command:new` | Saves session context to agent workspace memory on `/new` |
| `command-logger` | `command` | Logs all command events to `~/.openclaw/logs/commands.log` for audit |
| `boot-md` | `gateway:startup` | Runs the `BOOT.md` file when Gateway starts |
| `bootstrap-extra-files` | `agent:bootstrap` | Injects additional workspace files based on configured glob patterns |

### Hook Packs

Hook packs are **distributable bundles** containing one or more hooks. They support:

- **Local installation**: from a folder or archive
- **npm distribution**: standard npm packages

```bash
# Install from local folder
openclaw hooks install ./my-hook-pack

# Install from npm
openclaw hooks install @myorg/openclaw-hooks-audit

# Update installed hook packs (npm only)
openclaw hooks update
```

When installed, hook packs are placed in `~/.openclaw/hooks/<id>/` and their hooks are automatically enabled.

**Creating a hook pack** for npm distribution:

```json
{
  "name": "@myorg/openclaw-hooks-audit",
  "version": "1.0.0",
  "openclaw": {
    "type": "hook-pack"
  }
}
```

### CLI Commands

```bash
# List all discovered hooks (workspace, managed, bundled)
openclaw hooks list
openclaw hooks list --eligible          # Only hooks meeting requirements
openclaw hooks list --verbose           # Include missing requirements detail
openclaw hooks list --json              # Machine-readable output

# Get detailed info about a hook
openclaw hooks info <name>

# Check eligibility status for all hooks
openclaw hooks check

# Enable / disable a hook
openclaw hooks enable <name>
openclaw hooks disable <name>

# Install hook packs
openclaw hooks install <path-or-spec>

# Update installed hook packs (npm)
openclaw hooks update
```

### Configuration

**In `~/.openclaw/openclaw.json`:**

```json5
{
  hooks: {
    // Enable webhook HTTP endpoints (separate from internal hooks)
    enabled: true,

    // Shared secret for webhook authentication
    token: "your-webhook-token",

    // Custom webhook path prefix (default: /hooks)
    path: "/hooks",

    // Load hooks from additional directories
    dirs: [
      "/path/to/custom/hooks",
      "~/my-project/hooks",
    ],
  },
}
```

**Per-hook configuration** can be specified in the hook's `HOOK.md` frontmatter or through the main config file, and is accessible via `event.config` in the handler.

**After enabling/disabling hooks**, restart the Gateway for changes to take effect:

```bash
openclaw gateway restart
```

### Custom Hook Authoring

**Step-by-step guide to create a custom hook:**

1. **Choose location**:
   - `<workspace>/hooks/` — per-agent, highest precedence
   - `~/.openclaw/hooks/` — shared across workspaces

2. **Create directory**:
   ```bash
   mkdir -p ~/.openclaw/hooks/my-custom-hook
   ```

3. **Create `HOOK.md`**:
   ```markdown
   ---
   metadata:
     openclaw:
       name: my-custom-hook
       description: Notifies Slack when a session ends
       emoji: 🔔
       events:
         - command:new
         - command:reset
       requires:
         bins: []
         env:
           - SLACK_WEBHOOK_URL
   ---

   # My Custom Hook

   Posts a notification to Slack whenever a session is reset or a new one starts.
   ```

4. **Create `handler.ts`**:
   ```typescript
   import type { HookHandler } from "openclaw/hooks";

   export const handler: HookHandler = async (event) => {
     const webhookUrl = process.env.SLACK_WEBHOOK_URL;
     if (!webhookUrl) return;

     const message = event.type === "command:new"
       ? "🆕 New session started"
       : "🔄 Session reset";

     await fetch(webhookUrl, {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ text: message }),
     });
   };
   ```

5. **Enable and test**:
   ```bash
   openclaw hooks enable my-custom-hook
   openclaw hooks info my-custom-hook
   openclaw gateway restart
   ```

---

## HTTP Webhooks

HTTP webhooks are **inbound HTTP endpoints** exposed by the Gateway, allowing external systems to trigger agent work.

> Note: For detailed webhook configuration, also see [automation.md](automation.md).

### Enable

```json5
{
  gateway: {
    webhooks: { enabled: true },
  },
}
```

### Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `POST /hooks/wake` | POST | Trigger a wake/heartbeat cycle |
| `POST /hooks/agent` | POST | Send a prompt, run a dedicated agent turn |
| `POST /hooks/<name>` | POST | Custom-named endpoints via `gateway.webhooks.map` |

**`/hooks/agent` payload options:**

| Field | Description |
|---|---|
| `message` | The prompt to send |
| `name` | Optional display name |
| `agentId` | Route to a specific agent |
| `sessionKey` | Identify the agent's session |
| `wakeMode` | Wake behavior control |
| `model` | Override model |
| `thinking` | Override thinking level |
| `delivery` | Delivery options (channel, target) |

### Auth

Webhooks require `gateway.auth.token` or `gateway.auth.password`. Pass via:

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Check server status"}'
```

### Session Key Policy

- Default: each webhook call gets a fresh `hook:<uuid>` session key
- Override with `sessionKey` in the request body for persistent sessions

### Security

- Always use auth tokens
- Bind to loopback (`127.0.0.1`) or use Tailscale/VPN
- Webhooks inherit the agent's tool permissions
- Never expose webhook endpoints to the public internet without auth

---

## Use Cases & Patterns

### 1. Session Memory Preservation
**Hook**: `session-memory` (bundled)
**Event**: `command:new`
**Pattern**: Auto-save session summary before starting a new one, preventing context loss.

### 2. Audit Logging
**Hook**: `command-logger` (bundled)
**Event**: `command` (all)
**Pattern**: Log every command with timestamp and user identity to `~/.openclaw/logs/commands.log` for compliance/audit trails.

### 3. Custom Bootstrap Injection
**Hook**: `bootstrap-extra-files` (bundled)
**Event**: `agent:bootstrap`
**Pattern**: Inject project-specific files (`.cursorrules`, `CONVENTIONS.md`, etc.) into the workspace at agent startup.

### 4. External Notifications
**Event**: `command:new`, `command:reset`
**Pattern**: Send Slack/Discord/email notifications when sessions change, useful for team monitoring.

### 5. GitHub → Agent Pipeline
**Type**: HTTP Webhook
**Pattern**: GitHub sends push/PR webhooks to `/hooks/agent`, OpenClaw runs code review or deployment checks.

### 6. Stripe → Agent Processing
**Type**: HTTP Webhook
**Pattern**: Stripe payment events trigger agent runs for order confirmation, refund processing, or subscription management.

### 7. Scheduled Maintenance via Cron + Hooks
**Pattern**: Cron job triggers a heartbeat; internal hook on `gateway:startup` ensures environment is clean.

### 8. Message Filtering / Preprocessing
**Event**: `message:received`, `message:preprocessed`
**Pattern**: Custom hooks that filter spam, redact PII, or enrich messages before they reach the agent.

### 9. Multi-Agent Event Bus
**Pattern**: Hooks function as an event bus, allowing one agent's actions to trigger hooks that affect other agents in multi-agent setups.

### 10. Gateway Startup Initialization
**Hook**: `boot-md` (bundled)
**Event**: `gateway:startup`
**Pattern**: Execute a `BOOT.md` instruction file to set up the agent's identity, load configurations, or run startup tasks.

---

## Troubleshooting

| Problem | Diagnosis | Fix |
|---|---|---|
| Hook not firing | `openclaw hooks list --verbose` — check if eligible | Ensure required bins/env are present, then `openclaw hooks enable <name>` |
| Hook enabled but no effect | Check Gateway logs (`openclaw logs --follow`) | Restart Gateway after enabling: `openclaw gateway restart` |
| Webhook returns 401 | Auth token mismatch | Verify `gateway.auth.token` matches `Authorization` header |
| Webhook returns 404 | Webhooks not enabled or wrong path | Set `gateway.webhooks.enabled: true`, check `hooks.path` |
| Hook from plugin not appearing | Plugin may not be loaded | Check `openclaw plugins list`, ensure plugin is enabled |
| Custom hook directory not scanned | Extra dirs not configured | Add path to `hooks.dirs` in config |
| Hook pack install fails | Network or permissions issue | Check npm access, try local install path instead |
