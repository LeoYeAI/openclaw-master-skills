# SignalRadar Runtime Protocol Reference

This document describes the runtime-facing contracts that the current CLI
actually emits in v0.9.0. It is not a future schema wishlist.

## Command Result Envelopes

### `run --output json`

Frozen top-level fields:

- `status` — `NO_REPLY | HIT | ERROR | ONBOARD_NEEDED`
- `request_id` — UUID string
- `ts` — UTC ISO-8601 string
- `hits` — list of emitted signal events
- `errors` — list of structured errors

Current extension fields:

- `checked_count`
- `settled_count`
- `observations`
- `delivery` — (v0.9.0) present when `--push` attempted; keys: `attempted`, `sent`, `status`, `error`

Example:

```json
{
  "status": "NO_REPLY",
  "request_id": "2c4c9e18-7eb7-4b5d-92f6-cb4db7b7f0f7",
  "ts": "2026-03-10T12:00:00Z",
  "hits": [],
  "errors": [],
  "checked_count": 4,
  "settled_count": 1,
  "observations": []
}
```

When `--push` is used and there are hits:

```json
{
  "status": "HIT",
  "delivery": {
    "attempted": true,
    "sent": true,
    "status": "delivered",
    "error": ""
  }
}
```

### `run --output openclaw`

Reserved for background platform runs.

- quiet run -> stdout exactly `HEARTBEAT_OK`
- hit run -> stdout is concise user-ready alert text
- digest due -> stdout is human-readable digest text when `delivery.primary.channel == openclaw`

This mode is intended for the `openclaw cron` scheduler path.
If `delivery.primary.channel` is not `openclaw`, this mode stays quiet (`HEARTBEAT_OK`)
and lets the configured adapter handle delivery.

### `onboard --output json`

Three-step guided setup for bot/agent mode. Each step returns a distinct status.

#### `onboard --step preview`

- `status` — `ONBOARD_PREVIEW | ERROR | NO_REPLY`
- `step` — `1`
- `events` — list of preset events with `index`, `title`, `market_count`, `unavailable`, `url`
- `education` — terminology definitions for `event` and `market`
- `message` — user-facing instruction

#### `onboard --step confirm --keep <indices>`

- `status` — `ONBOARD_CONFIRM | ERROR | NO_REPLY`
- `step` — `2`
- `kept_events` — count of kept events
- `total_markets` — count of markets to add
- `markets` — list with `event_title`, `question`, `probability`, `category`, `url`
- `education` — definitions for `category` and `baseline`

#### `onboard --step finalize`

- `status` — `ONBOARD_COMPLETE | ERROR`
- `step` — `3`
- `added` — count of entries added
- `skipped` — count of entries skipped (already in watchlist)
- `schedule` — auto-monitoring setup result
- `route_ready` — boolean, whether background push route is captured
- `warnings` — list of warning strings (e.g. route not yet armed)
- `education` — baseline example and next-steps guidance

### `add --output json` (empty watchlist)

When watchlist is empty and no URL is provided, returns:

- `status` — `ONBOARD_NEEDED`
- `message` — instruction to use `onboard --step preview`

### `digest --output json`

Top-level fields:

- `status` — `OK | NO_REPLY`
- `request_id`
- `ts`
- `digest`

`digest` currently includes:

- `frequency`
- `report_key`
- `due`
- `due_reason`
- `first_report`
- `generated_at`
- `scheduled_local`
- `summary`
- `top_movers`
- `events`
- `new_entries`
- `settled_entries`
- `error_entries`
- `delivery`

Human-readable digest text is intentionally summarized; `events` and entry lists provide structured detail.

On the first automatic digest cycle, `run --output json` may include:

- `due: false`
- `due_reason: "bootstrap_snapshot"`
- `delivery.status: "BOOTSTRAP"`

That means SignalRadar silently initialized `digest_state.json` and will start automatic user-facing digest delivery from the next report cycle.

### `digest --output openclaw`

Reserved for scheduled or platform-routed digest delivery.

- due digest + `delivery.primary.channel == openclaw` -> stdout is digest text
- otherwise -> stdout exactly `HEARTBEAT_OK`

### `add --output json`

Top-level fields:

- `status` — `OK | NO_REPLY | ERROR | ONBOARD_NEEDED`
- `request_id`
- `ts`
- `event_title`
- `added`
- `skipped`

Optional field:

- `schedule` — present when the first successful add attempts auto-monitoring

### `show --output json`

Top-level fields:

- `status` — `OK | ERROR | NO_REPLY`
- `request_id`
- `ts`
- `matches`
- `errors`

`matches` is a read-only snapshot. It does not update baselines and does not send alerts.

### `schedule --output json`

Top-level fields:

- `enabled` — boolean
- `interval` — integer minutes, `0` when disabled
- `driver` — `openclaw | crontab | none`
- `default_driver` — resolved default if user runs `schedule N` without explicit driver
- `next_run`
- `last_run`
- `last_run_status`
- `route_ready` — (v0.9.0) boolean, whether a reply route is stored for background push
- `route_channel` — (v0.9.0) captured route channel type, empty if missing
- `route_captured_at` — (v0.9.0) ISO-8601 timestamp of last route capture
- `last_delivery_status` — (v0.9.0) delivery status from last run
- `last_delivery_error` — (v0.9.0) delivery error from last run

Example:

```json
{
  "enabled": true,
  "interval": 10,
  "driver": "crontab",
  "default_driver": "crontab",
  "next_run": "unknown",
  "last_run": "2026-03-10T12:10:00Z",
  "last_run_status": "NO_REPLY",
  "route_ready": true,
  "route_channel": "telegram",
  "route_captured_at": "2026-03-10T12:05:00Z",
  "last_delivery_status": "delivered",
  "last_delivery_error": ""
}
```

### `doctor --output json`

Top-level fields:

- `status` — `HEALTHY | WARN`
- `data_directory`
- `check_interval_minutes`
- `checks`

`data_directory` reports path, existence, and writability of the runtime data root.

## Observation Rows

`run --output json` and `show --output json` may include observation rows with:

- `entry_id`
- `question`
- `slug`
- `event_title`
- `category`
- `state` — `checked | settled | error`
- `decision` — `BASELINE | SILENT | HIT | SETTLED | SNAPSHOT | ERROR`
- `threshold_abs_pp`
- `url`
- `end_date`

Optional fields:

- `current`
- `market_status`
- `baseline`
- `baseline_ts`
- `abs_pp`
- `reason`
- `error_code`
- `error_message`

## Error Objects

Structured errors currently use:

- `entry_id`
- `code`
- `message`
- `error`

Known runtime codes:

- `SR_VALIDATION_ERROR`
- `SR_SOURCE_UNAVAILABLE`

Upstream/source errors may include more detailed source-specific messages, but the
top-level contract remains `code + message`.

## Signal Events (`hits`)

Each hit row is produced by `decide_threshold.check_entry()` and currently carries:

- `request_id`
- `entry_id`
- `question`
- `current`
- `baseline`
- `abs_pp`
- `reason`
- `ts`

The event text shown to users is derived from these fields.

## Scheduling Semantics

- Default scheduling prefers `crontab` (zero LLM cost) over `openclaw cron`
- Otherwise it falls back to `openclaw cron`
- `schedule disable` removes both `openclaw` and `crontab` jobs when present
- `check_interval_minutes` in config is a display value; the real scheduler is managed by `schedule`

## OpenClaw Delivery Semantics

- interactive chat: the bot reply is the user-facing notification
- scheduled crontab path: `--push` reads stored reply route from `~/.signalradar/cache/openclaw_reply_route.json` and sends via `openclaw message send --channel <type> --target <id>`
- scheduled OpenClaw path: `openclaw cron` announce delivery carries `run --output openclaw` when the primary delivery channel is `openclaw`
- `route_delivery.py` reports `openclaw` as platform-managed, not as a fake direct send
- when `run --output openclaw` and `delivery.primary.channel == openclaw`, the CLI intentionally emits user-ready stdout and skips `deliver_hit()` to avoid duplicate platform delivery
- when `run --output openclaw` and the primary delivery channel is `file` or `webhook`, stdout stays `HEARTBEAT_OK` and the configured adapter remains the only delivery path
- when `digest --output openclaw` and `delivery.primary.channel == openclaw`, the CLI emits digest text to stdout and updates `digest_state.json`
- when digest is due but the caller uses `digest --output text|json` with `delivery.primary.channel == openclaw`, the command stays in preview mode and does not claim delivery
- the first automatic digest triggered from `run` is bootstrap-only: SignalRadar writes `digest_state.json` without emitting digest text, so users are not surprised by an immediate retroactive digest after install/update

## Reply Route Contract (v0.9.0)

- OpenClaw injects `OPENCLAW_REPLY_CHANNEL` and `OPENCLAW_REPLY_TARGET` into foreground skill executions
- SignalRadar persists these to `~/.signalradar/cache/openclaw_reply_route.json` on any CLI invocation
- Background `--push` reads this file for explicit `openclaw message send` routing
- If no route is stored, `--push` reports `route_missing` in delivery outcome, not silent success
- Route persists indefinitely until overwritten by a newer foreground invocation

## last_run.json Contract (v0.9.0)

Fields:

- `ts` — UTC ISO-8601 timestamp of the run
- `status` — `NO_REPLY | HIT | ERROR`
- `checked` — integer count of entries checked
- `hits` — integer count of HIT events
- `delivery_attempted` — (v0.9.0) boolean, whether push was attempted
- `delivery_sent` — (v0.9.0) boolean, whether push succeeded
- `delivery_status` — (v0.9.0) `skipped | delivered | route_missing | send_failed | send_error`
- `delivery_error` — (v0.9.0) error string, empty on success
