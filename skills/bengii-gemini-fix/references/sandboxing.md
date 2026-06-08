# OpenClaw Sandboxing Reference

## Table of Contents

- [Overview](#overview)
- [What Gets Sandboxed](#what-gets-sandboxed)
- [Modes](#modes)
- [Scope](#scope)
- [Workspace Access](#workspace-access)
- [Custom Bind Mounts](#custom-bind-mounts)
- [Docker Configuration](#docker-configuration)
- [Browser Sandboxing](#browser-sandboxing)
- [Multi-Agent Overrides](#multi-agent-overrides)
- [Tool Policy Integration](#tool-policy-integration)
- [Minimal Enable Example](#minimal-enable-example)
- [Groups Pattern](#groups-pattern)

## Overview

Sandboxing runs agent tool execution (commands, file ops) inside Docker containers, isolating them from the host.

## What Gets Sandboxed

**Sandboxed:**
- Tool execution: `exec`, `read`, `write`, `edit`, `apply_patch`, `process`, `bash`
- Optional browser in sandbox container

**NOT sandboxed (runs on host):**
- The Gateway process itself
- Tools explicitly allowed to run on host (`tools.elevated`)
- Elevated exec bypasses sandboxing

## Modes

Config: `agents.defaults.sandbox.mode`

| Mode | Behavior |
|---|---|
| `"off"` | No sandboxing |
| `"non-main"` | Sandbox only non-main sessions (groups/channels). Main DM session runs on host |
| `"all"` | Every session runs in a sandbox |

> **Note:** `"non-main"` is based on `session.mainKey` (default `"main"`), not agent ID. Group/channel sessions use their own keys, so they are always non-main and will be sandboxed.

## Scope

Config: `agents.defaults.sandbox.scope`

| Scope | Isolation Level |
|---|---|
| `"session"` (default) | One container per session (strongest) |
| `"agent"` | One container per agent |
| `"shared"` | One container shared by all sandboxed sessions |

## Workspace Access

Config: `agents.defaults.sandbox.workspaceAccess`

| Mode | Behavior |
|---|---|
| `"none"` (default) | Tools see sandbox workspace under `~/.openclaw/sandboxes` |
| `"ro"` | Mounts agent workspace read-only at `/agent` (disables write/edit/apply_patch) |
| `"rw"` | Mounts agent workspace read/write at `/workspace` |

## Custom Bind Mounts

Config: `agents.defaults.sandbox.docker.binds`

Format: `"hostPath:containerPath:mode"` (mode = `ro` or `rw`)

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          binds: [
            "/home/user/source:/source:ro",
            "/var/data/myapp:/data:ro",
          ],
        },
      },
    },
    list: [{
      id: "build",
      sandbox: {
        docker: {
          binds: ["/mnt/cache:/cache:rw"],  // Per-agent override
        },
      },
    }],
  },
}
```

**Safety rules:**
- OpenClaw blocks dangerous bind sources: `docker.sock`, `/etc`, `/proc`, `/sys`, `/dev`
- Use `:ro` for sensitive mounts (secrets, SSH keys, credentials)
- Binds bypass sandbox filesystem — they expose host paths directly

## Docker Configuration

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          network: "none",              // Default: no egress (safest)
          // network: "bridge",          // Allow internet access
          readOnlyRoot: true,           // Default
          user: "1000:1000",            // Container user
          setupCommand: "apt-get update && apt-get install -y python3",
          env: {                        // Container environment vars
            MY_VAR: "value",
          },
        },
      },
    },
  },
}
```

**Network:**
- `"none"` (default): no network access (package installs will fail)
- `"bridge"`: allow internet
- `"host"`: **blocked** by OpenClaw
- `"container:<id>"`: **blocked** by default (namespace join risk)

**setupCommand:**
- Runs once per container at creation
- `user` must be root (`"0:0"`) for package installs
- `readOnlyRoot` must be `false` for writes
- Container does NOT inherit `process.env` — use `docker.env` for API keys

## Browser Sandboxing

Config: `agents.defaults.sandbox.browser`

- Auto-starts when browser tool needs it
- Uses dedicated Docker network `openclaw-sandbox-browser`
- noVNC observer access is password-protected
- Optional `cdpSourceRange` for CIDR allowlist (e.g., `172.21.0.1/32`)
- `allowHostControl` lets sandboxed sessions target host browser
- Separate bind mounts via `agents.defaults.sandbox.browser.binds`

## Multi-Agent Overrides

Per-agent sandbox config overrides defaults:

```json5
{
  agents: {
    list: [{
      id: "support",
      sandbox: {
        mode: "all",                    // Override mode
        scope: "session",
        workspaceAccess: "none",
        docker: { binds: [] },
      },
      tools: {
        sandbox: {
          tools: {
            allow: ["group:messaging"],
            deny: ["group:runtime", "group:fs"],
          },
        },
      },
    }],
  },
}
```

## Tool Policy Integration

Sandbox, tool policy, and elevated mode work together:

1. **Tool policy** (`tools.allow`/`tools.deny`) — what tools are available
2. **Sandbox** — where tools execute (host vs container)
3. **Elevated mode** (`tools.elevated`) — host bypass for specific commands

Debug with: `openclaw sandbox explain`

## Minimal Enable Example

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
      },
    },
  },
}
```

## Groups Pattern

Personal DMs on host + groups in sandbox:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",     // Groups are non-main → sandboxed
        scope: "session",
        workspaceAccess: "none",
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: ["group:messaging", "group:sessions"],
        deny: ["group:runtime", "group:fs", "group:ui", "nodes", "cron", "gateway"],
      },
    },
  },
}
```
