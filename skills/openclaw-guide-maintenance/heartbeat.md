# Heartbeat Reference

> Source: https://docs.openclaw.ai/gateway/heartbeat

## Overview

Heartbeat is a recurring, agent-driven background task. The Gateway fires a heartbeat prompt at a configurable interval, letting the agent check for pending work, follow up on tasks, or send health check-ins.

## Quick Start

1. Leave heartbeats enabled (default: `30m`, or `1h` for Anthropic OAuth/setup-token).
2. Create a `HEARTBEAT.md` checklist in the agent workspace (optional but recommended).
3. Set `target: "last"` to route heartbeat replies to the last contact (default: `"none"` — no delivery).
4. Optional: enable reasoning delivery for transparency.
5. Optional: use `lightContext: true` for minimal bootstrap context.
6. Optional: restrict to active hours (local time).

## Config

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",                    // default: 30m (0m disables)
        model: "anthropic/claude-opus-4-6",
        includeReasoning: false,         // deliver separate Reasoning: message
        lightContext: false,             // true: only HEARTBEAT.md from bootstrap
        target: "last",                  // none | last | <channel id>
        to: "+15551234567",              // optional channel-specific override
        accountId: "ops-bot",            // optional multi-account channel id
        directPolicy: "allow",          // "allow" (default) or "block"
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,                // max chars after HEARTBEAT_OK
        // activeHours: { start: "08:00", end: "24:00" },
      },
    },
  },
}
```

### Defaults
- **Interval**: `30m` (or `1h` for Anthropic OAuth). Use `0m` to disable.
- **Prompt body** (configurable via `agents.defaults.heartbeat.prompt`):
  > "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."
- **Active hours** (`heartbeat.activeHours`) checked in configured timezone. Outside window, heartbeats are skipped.

## Response Contract

- If nothing needs attention: reply with `HEARTBEAT_OK`.
- Gateway treats `HEARTBEAT_OK` as an ack when it appears at start/end of reply. Token is stripped; reply dropped if remaining content ≤ `ackMaxChars` (default: 300).
- If `HEARTBEAT_OK` appears mid-reply, not treated specially.
- For alerts: do **not** include `HEARTBEAT_OK`; return only alert text.

## Delivery Behavior

- Heartbeats run in agent's main session by default (`agent:<id>:<mainKey>`), or `global` when `session.scope = "global"`.
- `session` affects run context; delivery is controlled by `target` and `to`.
- With `target: "last"`: delivery goes to last external channel for that session.
- `directPolicy: "block"` suppresses direct-target sends while still running heartbeat turn.
- If main queue is busy: heartbeat is skipped and retried later.
- Heartbeat-only replies **do not** keep session alive; `updatedAt` is restored so idle expiry behaves normally.

## Visibility Controls

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false       # Hide HEARTBEAT_OK (default)
      showAlerts: true     # Show alert messages (default)
      useIndicator: true   # Emit indicator events (default)
  telegram:
    heartbeat:
      showOk: true         # Show OK acks on Telegram
  whatsapp:
    accounts:
      work:
        heartbeat:
          showAlerts: false # Suppress alerts for this account
```

### What Each Flag Does
| Flag | Default | Behavior |
|---|---|---|
| `showOk` | `false` | Whether to deliver `HEARTBEAT_OK` acks to the channel |
| `showAlerts` | `true` | Whether to deliver alert messages |
| `useIndicator` | `true` | Emit heartbeat indicator events |

## Per-Agent Heartbeats

Override per agent via `agents.list[].heartbeat`:
```json5
{
  agents: {
    list: [
      {
        id: "ops",
        heartbeat: {
          every: "15m",
          target: "last",
          prompt: "Check server metrics and alert if anything is critical.",
        },
      },
    ],
  },
}
```

## HEARTBEAT.md (Optional)

Create `HEARTBEAT.md` in the agent workspace with a checklist:
```markdown
## Tasks
- [ ] Check unread emails
- [ ] Review calendar for today
- [ ] Check monitoring dashboard
```

The agent can update `HEARTBEAT.md` itself (e.g., checking off tasks) if the workspace is writable.

## Manual Wake (On-Demand)

```bash
openclaw system heartbeat now           # Trigger immediately
openclaw system heartbeat last          # Show last heartbeat info
```

## Cost Awareness

Each heartbeat is a full agent run (system prompt + HEARTBEAT.md + user prompt). With `lightContext: true`, only `HEARTBEAT.md` is included from bootstrap files, reducing token cost significantly.

## See Also

- [automation.md](automation.md) — Cron jobs (scheduled triggers)
- [sessions.md](sessions.md) — Session lifecycle and idle expiry
- [agent_runtime.md](agent_runtime.md) — Agent loop and hooks
