# OpenClaw Session Management Reference

## Table of Contents

- [Secure DM Mode](#secure-dm-mode)
- [Where State Lives](#where-state-lives)
- [Session Key Mapping](#session-key-mapping)
- [Session Lifecycle](#session-lifecycle)
- [Send Policy](#send-policy)
- [Session Maintenance](#session-maintenance)
- [Compaction](#compaction)
- [Inspecting Sessions](#inspecting-sessions)
- [Configuration Example](#configuration-example)
- [Session Origin Metadata](#session-origin-metadata)
- [Tips](#tips)

## Secure DM Mode

**Problem**: Without DM isolation, multiple users sharing the same `main` session can leak context across conversations.

**Solution**: Set `session.dmScope` to isolate DMs per sender.

| dmScope Value | Session Key Pattern | Use Case |
|---|---|---|
| `main` (default) | `agent:<agentId>:<mainKey>` | Single-user setups; continuity across channels |
| `per-peer` | `agent:<agentId>:dm:<peerId>` | Multi-user, cross-channel per person |
| `per-channel-peer` | `agent:<agentId>:<channel>:dm:<peerId>` | Multi-user, per channel + per person |
| `per-account-channel-peer` | `agent:<agentId>:<channel>:<accountId>:dm:<peerId>` | Multi-account inboxes |

```json5
{
  session: {
    dmScope: "per-channel-peer",  // Recommended for multi-user
  },
}
```

**When to use secure DM mode**: Multiple pairing approvals, DM allowlist with multiple entries, `dmPolicy: "open"`, or multiple phone numbers/accounts messaging your agent.

**Identity links**: Use `session.identityLinks` to collapse DM sessions for the same person across channels:

```json5
{
  session: {
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
  },
}
```

Verify DM settings with `openclaw security audit`.

## Where State Lives

The **Gateway** is the source of truth (not local machines in remote mode).

| Path | Purpose |
|---|---|
| `~/.openclaw/agents/<agentId>/sessions/sessions.json` | Session store (per agent) |
| `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl` | Transcript files |
| `.../<SessionId>-topic-<threadId>.jsonl` | Telegram topic sessions |

- Store is a map: `sessionKey -> { sessionId, updatedAt, ... }`
- Deleting entries is safe; they are recreated on demand
- Group entries may include `displayName`, `channel`, `subject`, `room`, `space`
- Session entries include `origin` metadata (label + routing hints)
- Token counts come from the gateway's store fields: `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`

## Session Key Mapping

### Direct Messages

Follow `session.dmScope`:

- **`main`**: `agent:<agentId>:<mainKey>` — all DMs share one session
- **`per-peer`**: `agent:<agentId>:dm:<peerId>`
- **`per-channel-peer`**: `agent:<agentId>:<channel>:dm:<peerId>`
- **`per-account-channel-peer`**: `agent:<agentId>:<channel>:<accountId>:dm:<peerId>` (`accountId` defaults to `default`)

### Groups

- Groups: `agent:<agentId>:<channel>:group:<id>`
- Rooms/channels: `agent:<agentId>:<channel>:channel:<id>`
- Telegram forum topics: append `:topic:<threadId>` to group id
- Legacy `group:<id>` keys still recognized for migration

### Other Sources

| Source | Key Pattern |
|---|---|
| Cron jobs | `cron:<job.id>` |
| Webhooks | `hook:<uuid>` (unless explicitly set) |
| Node runs | `node-<nodeId>` |

## Session Lifecycle

### Reset Policy

Sessions are reused until they expire; expiry is evaluated on the next inbound message.

| Reset Mode | Behavior |
|---|---|
| `daily` (default) | Resets at `atHour` (default 4:00 AM local time) |
| `idle` | Resets after `idleMinutes` of inactivity |
| Combined | Both configured → whichever expires first forces new session |

**Per-type overrides**: `resetByType` for `direct`, `group`, and `thread` sessions.

**Per-channel overrides**: `resetByChannel` overrides for a specific channel (takes precedence over `reset`/`resetByType`).

### Reset Triggers

- `/new` or `/reset` — starts a fresh session
- `/new <model>` — reset + set model (accepts alias, `provider/model`, or provider name with fuzzy match)
- If sent alone, OpenClaw runs a short "hello" greeting turn
- Custom triggers via `resetTriggers` array
- Isolated cron jobs always mint a fresh `sessionId` per run

### Manual Reset

Delete specific keys from the store or remove the JSONL transcript; the next message recreates them.

## Send Policy

Optional rules to control which sessions can send outbound messages:

```json5
{
  session: {
    sendPolicy: {
      rules: [
        { action: "deny", match: { channel: "discord", chatType: "group" } },
        { action: "deny", match: { keyPrefix: "cron:" } },
        { action: "deny", match: { rawKeyPrefix: "agent:main:discord:" } },
      ],
      default: "allow",
    },
  },
}
```

Chat overrides:
- `/send on` — allow for this session
- `/send off` — deny for this session
- `/send inherit` — clear override, use config rules

## Session Maintenance

### Defaults

| Setting | Default |
|---|---|
| `session.maintenance.mode` | `warn` |
| `session.maintenance.pruneAfter` | `30d` |
| `session.maintenance.maxEntries` | `500` |
| `session.maintenance.rotateBytes` | `10mb` |
| `session.maintenance.resetArchiveRetention` | `pruneAfter` (30d) |
| `session.maintenance.maxDiskBytes` | unset (disabled) |
| `session.maintenance.highWaterBytes` | 80% of `maxDiskBytes` |

### Mode: `enforce` Cleanup Order

1. Prune stale entries older than `pruneAfter`
2. Cap entry count to `maxEntries` (oldest first)
3. Archive transcript files for removed entries
4. Purge old `*.deleted.<timestamp>` and `*.reset.<timestamp>` archives
5. Rotate `sessions.json` when it exceeds `rotateBytes`
6. If `maxDiskBytes` set, enforce disk budget toward `highWaterBytes`

### Example Configs

```json5
// Time-based maintenance
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "45d",
      maxEntries: 800,
      rotateBytes: "20mb",
      resetArchiveRetention: "14d",
    },
  },
}
```

```json5
// Disk budget enforcement
{
  session: {
    maintenance: {
      mode: "enforce",
      maxDiskBytes: "1gb",
      highWaterBytes: "800mb",
    },
  },
}
```

### CLI

```bash
openclaw sessions cleanup --dry-run       # Preview what would be evicted
openclaw sessions cleanup --dry-run --json # JSON output for automation
openclaw sessions cleanup --enforce        # Apply cleanup
```

### Performance Tips

- Use `mode: "enforce"` in production for bounded growth
- Set both `pruneAfter` + `maxEntries`, not just one
- Set `maxDiskBytes` + `highWaterBytes` for large deployments
- Keep `highWaterBytes` below `maxDiskBytes` (default 80%)
- Use `--active-key` when running manual cleanup

## Compaction

When auto-compaction triggers (Pi runtime), it summarizes older context to free up window space.

Key settings:
- `reserveTokens` — tokens reserved for the summary
- `keepRecentTokens` — recent tokens kept verbatim

Pre-compaction "memory flush": implemented — saves important context to memory before compacting.

Chat command: `/compact` (optional instructions) summarizes older context.

See also: [Session Management Deep Dive](https://docs.openclaw.ai/reference/session-management-compaction)

## Inspecting Sessions

| Method | Command |
|---|---|
| Quick overview | `openclaw status` |
| Full dump | `openclaw sessions --json` |
| Active only | `openclaw sessions --json --active <minutes>` |
| Gateway RPC | `openclaw gateway call sessions.list --params '{}'` |
| Chat: status | Send `/status` as standalone message |
| Chat: context | Send `/context list` or `/context detail` |
| Chat: stop | Send `/stop` to abort current run |
| Chat: compact | Send `/compact` to summarize older context |

**Stop command**: `/stop` (or `stop`, `stop action`, `stop run`, `stop openclaw`) aborts the current run, clears queued followups, and stops sub-agent runs.

## Configuration Example

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main",
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetByChannel: {
      discord: { mode: "idle", idleMinutes: 10080 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    mainKey: "main",
  },
}
```

## Session Origin Metadata

Each session entry includes `origin` fields:
- `label` — human label (from conversation label + group subject/channel)
- `provider` — normalized channel id
- `from`/`to` — raw routing ids from the inbound envelope
- `accountId` — provider account id (multi-account)
- `threadId` — thread/topic id (when channel supports it)

## Tips

- Keep the primary key dedicated to 1:1 traffic; let groups keep their own keys
- When automating cleanup, delete individual keys instead of the whole store
- Verify DM settings with `openclaw security audit`
- Use `session.identityLinks` to unify a person's sessions across channels
