# OpenClaw ACP Agents Reference

## Table of Contents

- [Overview](#overview)
- [ACP vs Sub-Agents](#acp-vs-sub-agents)
- [Fast Operator Flow](#fast-operator-flow)
- [ACP Controls](#acp-controls)
- [ACP Command Cookbook](#acp-command-cookbook)
- [Thread-Bound Sessions](#thread-bound-sessions)
- [Session Target Resolution](#session-target-resolution)
- [Supported Harnesses](#supported-harnesses)
- [Required Config](#required-config)
- [Plugin Setup](#plugin-setup)
- [Permission Configuration](#permission-configuration)
- [Troubleshooting](#troubleshooting)
- [ACP CLI Bridge](#acp-cli-bridge-openclaw-acp)

## Overview

ACP (Agent Communication Protocol) agents allow OpenClaw to spawn and manage external AI agent runtimes (Codex, Claude Code, Gemini CLI, OpenCode, etc.) as persistent or one-shot sessions, with thread-bound routing and live controls.

Natural-language triggers:
- "Start a persistent Codex session in a thread and keep it focused."
- "Run this as a one-shot Claude Code ACP session and summarize the result."
- "Use Gemini CLI for this task in a thread, then keep follow-ups in that same thread."

## ACP vs Sub-Agents

| Feature | ACP (`runtime: "acp"`) | Sub-agents (`runtime: "subagent"`) |
|---|---|---|
| Session key | `agent:<agentId>:acp:<uuid>` | `agent:<agentId>:subagent:<uuid>` |
| Slash commands | `/acp ...` | `/subagents ...` |
| Tool call | `sessions_spawn` with `runtime:"acp"` | `sessions_spawn` with `runtime:"subagent"` |
| External runtime | Yes (via acpx harness) | No (internal Pi) |
| Thread binding | Supported | Supported |
| Persistent sessions | Yes | One-shot or persistent |

## Fast Operator Flow

```
/acp spawn codex --mode persistent --thread auto   # 1. Spawn session
# Work in the bound thread...
/acp status                                          # 2. Check state
/acp model <provider/model>                          # 3. Tune model
/acp permissions <profile>                           # 4. Set permissions
/acp timeout <seconds>                               # 5. Set timeout
/acp steer tighten logging and continue              # 6. Nudge without replacing context
/acp cancel                                          # 7. Stop current turn
/acp close                                           # 8. Close session + remove bindings
```

## ACP Controls

| Command | Description |
|---|---|
| `/acp spawn` | Create new ACP session |
| `/acp cancel` | Stop current turn |
| `/acp steer` | Nudge active session without replacing context |
| `/acp close` | Close session + remove bindings |
| `/acp status` | Runtime state summary |
| `/acp set-mode` | Change execution mode (e.g., `plan`) |
| `/acp set <key> <value>` | Generic runtime option override |
| `/acp cwd <path>` | Update working directory |
| `/acp permissions <profile>` | Set permission profile |
| `/acp timeout <seconds>` | Set timeout |
| `/acp model <id>` | Change model |
| `/acp reset-options` | Clear all runtime overrides |
| `/acp sessions` | List active ACP sessions |
| `/acp doctor` | Diagnose ACP setup |
| `/acp install` | Install ACP dependencies |

### Runtime Options Mapping

| `/acp` Command | Runtime Config Key |
|---|---|
| `/acp model <id>` | `model` |
| `/acp permissions <profile>` | `approval_policy` |
| `/acp timeout <seconds>` | `timeout` |
| `/acp cwd <path>` | cwd override |
| `/acp set <key> <value>` | generic path (`key=cwd` uses cwd path) |

## ACP Command Cookbook

```
/acp spawn codex --mode persistent --thread auto --cwd /repo
/acp cancel agent:codex:acp:<uuid>
/acp steer --session support inbox prioritize failing tests
/acp close
/acp status
/acp set-mode plan
/acp set model openai/gpt-5.4
/acp cwd /Users/user/Projects/repo
/acp permissions strict
/acp timeout 120
/acp model anthropic/claude-opus-4-6
/acp reset-options
/acp sessions
/acp doctor
/acp install
```

## Thread-Bound Sessions

Thread binding works across channels:

1. OpenClaw binds a thread to a target ACP session
2. Follow-up messages in that thread route to the bound ACP session
3. ACP output is delivered back to the same thread
4. Unfocus/close/archive/idle-timeout or max-age expiry removes the binding

**Spawn thread modes** (`--thread`):

| Mode | Behavior |
|---|---|
| `auto` | Create thread if channel supports it |
| `here` | Bind to current thread |
| `off` | No thread binding |

### Required Config for Thread Binding

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

## Session Target Resolution

When a `/acp` command refers to a target session, resolution order:

1. Explicit target argument (or `--session` for `/acp steer`)
   - tries key → UUID-shaped session id → label
2. Current thread binding (if thread is bound to ACP session)
3. Current requester session fallback

## Supported Harnesses

| Harness | Agent ID |
|---|---|
| Pi (OpenClaw internal) | `pi` |
| Claude Code | `claude` |
| Codex | `codex` |
| OpenCode | `opencode` |
| Gemini CLI | `gemini` |
| Kimi | `kimi` |

Custom agents can be added with `--agent <command>`.

## Required Config

```json5
{
  acp: {
    enabled: true,
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: ["pi", "claude", "codex", "opencode", "gemini", "kimi"],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

## Plugin Setup

### Install acpx Backend

```bash
# Quick install
openclaw plugins install acpx

# From registry (full name)
openclaw plugins install @openclaw/acpx
openclaw config set plugins.entries.acpx.enabled true

# From source
openclaw plugins install ./extensions/acpx

# Verify
/acp doctor
```

## Permission Configuration

### permissionMode

| Mode | Behavior |
|---|---|
| `approve-all` | Auto-approve all permission prompts |
| `approve-reads` | Auto-approve read-only, prompt for writes |
| `deny-all` | Deny all permission prompts |

### nonInteractivePermissions

| Mode | Behavior |
|---|---|
| `fail` | Throw `AcpRuntimeError` on permission prompt |
| `deny` | Silently deny permission |

### Configure

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

**Recommended for non-interactive**: `permissionMode=approve-reads` + `nonInteractivePermissions=fail`.

## Troubleshooting

| Error | Fix |
|---|---|
| `ACP runtime backend is not configured` | Run `/acp doctor`, install acpx plugin |
| `ACP is disabled by policy (acp.enabled=false)` | Set `acp.enabled=true` |
| `ACP dispatch is disabled by policy` | Set `acp.dispatch.enabled=true` |
| `ACP agent "<id>" is not allowed by policy` | Add `agentId` to `acp.allowedAgents` |
| `Unable to resolve session target: ...` | Check `/acp sessions` for active sessions |
| `--thread here requires running inside an active thread` | Use `--thread auto` or `off` |
| `Only <user-id> can rebind this thread` | Original spawner must rebind |
| `Thread bindings are unavailable for <channel>` | Use `--thread off` or enable thread bindings |
| `AcpRuntimeError: Permission prompt unavailable` | Set `permissionMode` to `approve-all` |

---

## ACP CLI Bridge (`openclaw acp`)

> Source: https://docs.openclaw.ai/cli/acp

The `openclaw acp` command runs an ACP-compatible stdio bridge, letting external IDE agents (Codex, Claude Code, Zed, etc.) send prompts into an OpenClaw Gateway session.

### Usage

```bash
# Default (local Gateway)
openclaw acp

# Remote Gateway
openclaw acp --url wss://gateway-host:18789 --token <token>

# Remote Gateway (token from file — preferred for process safety)
openclaw acp --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# Attach to an existing session key
openclaw acp --session agent:main:main

# Attach by label (must already exist)
openclaw acp --session-label "support inbox"

# Reset the session key before the first prompt
openclaw acp --session agent:main:main --reset-session
```

### ACP Client (Debug Mode)

```bash
# Default
openclaw acp client

# Point the spawned bridge at a remote Gateway
openclaw acp client --server-args --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# Override the server command (default: openclaw)
openclaw acp client --server "node" --server-args openclaw.mjs acp --url ws://127.0.0.1:19001
```

### Security Notes (Auto-Approval)

- Auto-approval is **allowlist-based** and only applies to trusted core tool IDs.
- `read` auto-approval is scoped to the current working directory (`--cwd` when set).
- Unknown/non-core tool names, out-of-scope reads, and dangerous tools always require explicit prompt approval.
- Server-provided `toolCall.kind` is treated as **untrusted metadata** (not an authorization source).

### Selecting Agents

```bash
openclaw acp --session agent:main:main      # Main agent, main session
openclaw acp --session agent:design:main    # Design agent
openclaw acp --session agent:qa:bug-123     # QA agent, specific issue
```

### Session Mapping

| Flag | Description |
|---|---|
| `--session <key>` | Use a specific Gateway session key |
| `--session-label <label>` | Resolve an existing session by label |
| `--reset-session` | Mint a fresh session id for that key (same key, new transcript) |
| `--require-existing` | Fail if the session key/label does not exist |

JSON meta equivalent:
```json
{
  "_meta": {
    "sessionKey": "agent:main:main",
    "sessionLabel": "support inbox",
    "resetSession": true
  }
}
```

### Options

#### `openclaw acp` Options

| Flag | Description |
|---|---|
| `--url <url>` | Gateway WebSocket URL (defaults to `gateway.remote.url`) |
| `--token <token>` | Gateway auth token |
| `--token-file <path>` | Read auth token from file (preferred) |
| `--password <password>` | Gateway auth password |
| `--password-file <path>` | Read auth password from file |
| `--session <key>` | Default session key |
| `--session-label <label>` | Default session label to resolve |
| `--require-existing` | Fail if session doesn't exist |
| `--reset-session` | Reset session before first use |
| `--no-prefix-cwd` | Do not prefix prompts with working directory |
| `--verbose, -v` | Verbose logging to stderr |

#### `acp client` Options

| Flag | Description |
|---|---|
| `--cwd <dir>` | Working directory for the ACP session |
| `--server <command>` | ACP server command (default: `openclaw`) |
| `--server-args <args...>` | Extra arguments passed to the ACP server |
| `--server-verbose` | Enable verbose logging on the ACP server |
| `--verbose, -v` | Verbose client logging |

### Auth Resolution

- **`--token`/`--password`** can be visible in local process listings — prefer `--token-file`/`--password-file` or env vars.
- **Local mode**: env (`OPENCLAW_GATEWAY_*`) → `gateway.auth.*` → `gateway.remote.*` fallback
- **Remote mode**: `gateway.remote.*` with env/config fallback per remote precedence rules
- **`--url` is override-safe**: does not reuse implicit config/env credentials; pass explicit `--token`/`--password`

### Environment

- ACP runtime backend processes receive `OPENCLAW_SHELL=acp`.
- `openclaw acp client` sets `OPENCLAW_SHELL=acp-client` on the spawned bridge process.

### Use from acpx (Codex, Claude, Other ACP Clients)

```bash
# One-shot request into your default OpenClaw ACP session
acpx openclaw exec "Summarize the active OpenClaw session state."

# Persistent named session for follow-up turns
acpx openclaw sessions ensure --name codex-bridge
acpx openclaw -s codex-bridge --cwd /path/to/repo \
  "Ask my OpenClaw work agent for recent context relevant to this repo."
```

#### acpx Config (`~/.acpx/config.json`)

```json
{
  "agents": {
    "openclaw": {
      "command": "env OPENCLAW_HIDE_BANNER=1 OPENCLAW_SUPPRESS_NOTES=1 openclaw acp --url ws://127.0.0.1:18789 --token-file ~/.openclaw/gateway.token --session agent:main:main"
    }
  }
}
```

### Zed Editor Setup

Add to `~/.config/zed/settings.json`:

```json
{
  "agent_servers": {
    "OpenClaw ACP": {
      "type": "custom",
      "command": "openclaw",
      "args": ["acp"],
      "env": {}
    }
  }
}
```

Remote with specific agent:
```json
{
  "agent_servers": {
    "OpenClaw ACP": {
      "type": "custom",
      "command": "openclaw",
      "args": [
        "acp",
        "--url", "wss://gateway-host:18789",
        "--token", "<token>",
        "--session", "agent:design:main"
      ],
      "env": {}
    }
  }
}
```

### How to Use This

1. Ensure the Gateway is running (local or remote).
2. Configure the Gateway target (config or flags):
   ```bash
   openclaw config set gateway.remote.url wss://gateway-host:18789
   openclaw config set gateway.remote.token <token>
   ```
3. Point your IDE to run `openclaw acp` over stdio.

