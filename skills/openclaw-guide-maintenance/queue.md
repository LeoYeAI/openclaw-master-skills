# Command Queue

> Source: https://docs.openclaw.ai/concepts/queue

## Why

- Auto-reply runs can be expensive (LLM calls) and can collide when multiple inbound messages arrive close together.
- Serializing avoids competing for shared resources (session files, logs, CLI stdin) and reduces upstream rate limits.

## How It Works

- A lane-aware FIFO queue drains each lane with a configurable concurrency cap (default 1 for unconfigured lanes; `main` defaults to 4, `subagent` to 8).
- `runEmbeddedPiAgent` enqueues by session key (lane `session:<key>`) to guarantee only one active run per session.
- Each session run is then queued into a global lane (`main` by default) so overall parallelism is capped by `agents.defaults.maxConcurrent`.
- Typing indicators still fire immediately on enqueue.

## Queue Modes (Per Channel)

| Mode | Behavior |
|---|---|
| `steer` | Inject immediately into the current run (cancels pending tool calls after the next tool boundary). Falls back to followup if not streaming. |
| `followup` | Enqueue for the next agent turn after the current run ends. |
| `collect` | Coalesce all queued messages into a single followup turn (default). |
| `steer-backlog` | Steer now and preserve the message for a followup turn. |
| `interrupt` (legacy) | Abort the active run for that session, then run the newest message. |
| `queue` (legacy alias) | Same as `steer`. |

## Queue Options

- `debounceMs`: wait for quiet before starting a followup turn (prevents "continue, continue").
- `cap`: max queued messages per session.
- `drop`: overflow policy (`old`, `new`, `summarize`).

Defaults: `debounceMs: 1000`, `cap: 20`, `drop: summarize`.

## Configuration

```json5
{
  messages: {
    queue: {
      mode: "collect",
      debounceMs: 1000,
      cap: 20,
      drop: "summarize",
      byChannel: {
        discord: "collect",
      },
    },
  },
}
```

## Per-Session Overrides

- Send `/queue <mode>` as a standalone command to store the mode for the current session.
- Options can be combined: `/queue collect debounce:2s cap:25 drop:summarize`
- `/queue default` or `/queue reset` clears the session override.
