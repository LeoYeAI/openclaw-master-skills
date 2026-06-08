# OpenClaw Elevated Mode Reference

## Overview

Elevated mode (`/elevated` directives) allows sandboxed agents to temporarily execute commands on the gateway host, with configurable approval controls.

## Directive Forms

| Directive | Behavior |
|---|---|
| `/elevated on` | Run on gateway host, keep exec approvals |
| `/elevated ask` | Same as `on` (alias) |
| `/elevated full` | Run on gateway host, auto-approve exec (skip approvals) |
| `/elevated off` | Disable elevated mode |

Short form: `/elev on|off|ask|full`

## What It Controls

- **Host execution**: Forces exec onto the gateway host (only matters when agent is sandboxed)
- **Approvals**: `full` skips exec approvals; `on`/`ask` honor allowlist/ask rules
- **No-op for unsandboxed agents**: Only affects gating, logging, and status
- **Tool policy still applies**: If exec is denied by tool policy, elevated cannot be used
- **Separate from `/exec`**: `/exec` adjusts per-session defaults for authorized senders

## Resolution Order

1. Inline directive on the message (applies only to that message)
2. Session override (set by sending a directive-only message)
3. Global default (`agents.defaults.elevatedDefault` in config)

## Setting a Session Default

- Send a message that is only the directive, e.g. `/elevated full`
- Confirmation reply: "Elevated mode set to full..." / "Elevated mode disabled."
- If unavailable, returns actionable error without changing state
- Send `/elevated` with no argument to see current level

## Group Chat Behavior

- Elevated directives only honored when the agent is **mentioned**
- Command-only messages that bypass mention requirements are treated as mentioned

## Availability + Allowlists

### Feature Gate

```json5
{
  tools: {
    elevated: {
      enabled: true,          // Global baseline
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["user-id-123"],
      },
    },
  },
}
```

### Per-Agent Gate

```json5
{
  agents: {
    list: [{
      id: "restricted",
      tools: {
        elevated: {
          enabled: false,      // Can only further restrict (both must allow)
          allowFrom: { ... },  // Sender must match BOTH global + per-agent
        },
      },
    }],
  },
}
```

### Allowlist Matching

- Unprefixed entries match sender-scoped identity only (SenderId, SenderE164, From)
- Mutable sender metadata requires explicit prefixes:
  - `name:<value>` → SenderName
  - `username:<value>` → SenderUsername
  - `tag:<value>` → SenderTag
  - `id:<value>`, `from:<value>`, `e164:<value>` → explicit identity

### Discord Fallback

If `tools.elevated.allowFrom.discord` is omitted, `channels.discord.allowFrom` is used as fallback. Set `tools.elevated.allowFrom.discord` (even `[]`) to override.

## Logging + Status

- Elevated exec calls logged at info level
- Session status includes elevated mode (e.g. `elevated=ask`, `elevated=full`)
