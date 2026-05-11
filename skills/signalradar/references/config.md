# SignalRadar Configuration Reference

## Table of Contents

- [Precedence](#precedence)
- [Config Path Resolution](#config-path-resolution)
- [Full Config Shape](#full-config-shape)
- [Watchlist Storage](#watchlist-storage)
- [Threshold Rules](#threshold-rules)
- [Delivery Adapters](#delivery-adapters)
- [Periodic Report (Digest)](#periodic-report-digest)
- [Baseline Cleanup](#baseline-cleanup)
- [Profile](#profile)

## Precedence (High to Low)

1. CLI args (current run)
2. `~/.signalradar/config/signalradar_config.json` (via `--config` or `SIGNALRADAR_CONFIG`)
3. `DEFAULT_CONFIG` in `scripts/config_utils.py`

## Config Path Resolution

- First: `--config /path/to/signalradar_config.json`
- Then: env `SIGNALRADAR_CONFIG`
- Fallback: `~/.signalradar/config/signalradar_config.json`

Runtime data root:

- Default: `~/.signalradar/`
- Override for testing: `SIGNALRADAR_DATA_DIR=/tmp/signalradar`

## CLI Dotted Keys

The `config` command accepts dotted keys for nested values:

```bash
signalradar.py config threshold.abs_pp
signalradar.py config threshold.abs_pp 8.0
signalradar.py config threshold.per_category_abs_pp.AI 4.0
signalradar.py config profile.timezone Asia/Shanghai
```

- Threshold minimum: `0.1` percentage points
- To change monitoring frequency, use `schedule`, not `config check_interval_minutes`

## Full Config Shape

```json
{
  "profile": {
    "timezone": "Asia/Shanghai",
    "language": ""
  },
  "threshold": {
    "abs_pp": 5.0,
    "per_category_abs_pp": {},
    "per_entry_abs_pp": {}
  },
  "delivery": {
    "primary": {
      "channel": "webhook",
      "target": ""
    }
  },
  "digest": {
    "frequency": "weekly",
    "day_of_week": "monday",
    "time_local": "09:00",
    "top_n": 10
  },
  "baseline": {
    "cleanup_after_expiry_days": 90
  },
  "source": {
    "retries": 2
  }
}
```

## Watchlist Storage

Monitored entries are stored in `~/.signalradar/config/watchlist.json` (not in config.json).

Related runtime paths:

- Baselines: `~/.signalradar/cache/baselines/`
- Audit log: `~/.signalradar/cache/events/signal_events.jsonl`
- Last run metadata: `~/.signalradar/cache/last_run.json`
- Digest snapshot state: `~/.signalradar/cache/digest_state.json`

```json
{
  "entries": [
    {
      "entry_id": "polymarket:12345:grok-5-release:evt_67890",
      "slug": "grok-5-release",
      "question": "Grok 5 released by March 31, 2026?",
      "category": "AI",
      "url": "https://polymarket.com/event/grok-5-release",
      "end_date": "2026-03-31",
      "added_at": "2026-03-03T10:00:00Z"
    }
  ],
  "archived": [
    {
      "entry_id": "polymarket:99999:us-iran-ceasefire:evt_11111",
      "slug": "us-iran-ceasefire",
      "question": "US-Iran ceasefire by March 2, 2026?",
      "category": "default",
      "url": "https://polymarket.com/event/us-iran-ceasefire",
      "end_date": "2026-03-02",
      "added_at": "2026-02-20T08:00:00Z",
      "archived_at": "2026-03-05T10:00:00Z",
      "archive_reason": "user_removed",
      "baseline_history": [
        {"value": 23.0, "ts": "2026-02-20T08:00:00Z"},
        {"value": 41.0, "ts": "2026-02-25T12:00:00Z"}
      ],
      "final_result": "No"
    }
  ]
}
```

- `add` writes to `entries`
- `remove` moves from `entries` to `archived` (with full history)
- `run` reads from `entries`
- `list` displays `entries` (or `archived` with `--archived`)
- Users may hand-edit this file (e.g., to change category). The system tolerates manual edits.

## Threshold Rules

Priority order (highest wins):

1. Per-entry override: `threshold.per_entry_abs_pp.{entry_id}`
2. Per-category override: `threshold.per_category_abs_pp.{category}`
3. Global threshold: `threshold.abs_pp` (default: 5.0)

Minimum allowed threshold: `0.1` percentage points.

Example:

```json
{
  "threshold": {
    "abs_pp": 5.0,
    "per_category_abs_pp": {
      "AI": 4.0,
      "Crypto": 8.0
    },
    "per_entry_abs_pp": {
      "polymarket:12345:gpt5-release:evt_67890": 3.0
    }
  }
}
```

A HIT is triggered when `|current - baseline| >= applicable_threshold`.

## Delivery Adapters

| Channel | Target | Portability | Description |
|---------|--------|-------------|-------------|
| `webhook` (recommended) | `https://...` | All platforms | HTTP POST to any webhook endpoint (Slack, Telegram Bot API, Discord, etc.). Zero platform dependency. |
| `file` | `/path/to/alerts.jsonl` | All platforms | Appends alerts to local JSONL file. |
| `openclaw` | `direct` | OpenClaw only | OpenClaw platform messaging. Not portable to other platforms. Background push requires reply route capture. |

Unsupported channels (for example `telegram`) are rejected by `config` validation and reported by `doctor`.
不支持的通道（例如 `telegram`）会在 `config` 写入时被拒绝，并在 `doctor` 中报告。

### Recommended: webhook

`webhook` is the recommended delivery channel. It works on any platform (OpenClaw, Claude Code, standalone) with zero LLM cost when paired with `crontab` scheduling.

Example for Slack webhook:

```json
{
  "delivery": {
    "primary": {
      "channel": "webhook",
      "target": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    }
  }
}
```

Example for Telegram Bot API:

```json
{
  "delivery": {
    "primary": {
      "channel": "webhook",
      "target": "https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>"
    }
  }
}
```

Example for Discord webhook:

```json
{
  "delivery": {
    "primary": {
      "channel": "webhook",
      "target": "https://discord.com/api/webhooks/YOUR/WEBHOOK/URL"
    }
  }
}
```

The webhook payload includes both `text` (Slack, Telegram, MS Teams) and `content` (Discord) fields for broad compatibility.

### openclaw (OpenClaw platform only)

`openclaw` delivery works automatically in OpenClaw interactive chat (Agent reply IS the notification) and background monitoring (via `openclaw cron` announce). Not portable — depends on OpenClaw platform.

## Periodic Report (Digest)

| Setting | Values | Default |
|---------|--------|---------|
| `digest.frequency` | `off`, `daily`, `weekly`, `biweekly` | `weekly` |
| `digest.day_of_week` | `monday` ... `sunday` | `monday` |
| `digest.time_local` | `HH:MM` 24-hour local time | `09:00` |
| `digest.top_n` | `1` ... `50` | `10` |

- Uses the same delivery channel as HIT alerts.
- Compares against the previous digest snapshot stored in `~/.signalradar/cache/digest_state.json`, not against the per-run alert baseline.
- Includes both entries that already triggered realtime HIT alerts and entries with net-over-period changes that never crossed the realtime threshold.
- Human-readable digest output groups large multi-market events by event and shows top movers only; full detail remains available via `digest --output json`.
- Settled entries are flagged with a recommendation to remove.

## Baseline Cleanup

| Setting | Default | Description |
|---------|---------|-------------|
| `baseline.cleanup_after_expiry_days` | 90 | Days after market `end_date` to clean up baseline files |

Cleanup removes baseline files when the market's end date has passed by more than the configured number of days.

## Profile

| Setting | Default | Description |
|---------|---------|-------------|
| `profile.timezone` | `Asia/Shanghai` | Timezone for user-facing timestamps |
| `profile.language` | `""` (empty) | Controls system-message language only. Use `zh` or `en`; empty uses automatic detection (environment first, timezone fallback). Market titles/questions remain in original English. |

## Removed in v0.5.0

The following config fields are no longer supported:

| Removed Field | Reason |
|---------------|--------|
| `dedup.*` | Dedup removed. Repeated HITs are important signals. |
| `digest.only_important` | WatchLevel concept removed. |
| `rel_pct` / `rel_pct_enabled` | Relative threshold removed for simplicity. |
| Mode-related fields | Mode concept removed. All entries run together. |
| Notion-related fields | Notion integration removed. |

## Scheduling (Auto-Monitoring)

After the first successful `add` or `onboard finalize`, SignalRadar attempts to auto-enable 10-minute background monitoring (v0.9.0). Prefers system `crontab` with `--push` (zero LLM cost, delivers via `openclaw message send`); falls back to `openclaw cron` when crontab is unavailable. **Route gate**: when `delivery.primary.channel == openclaw` + `crontab` driver + no captured reply route, the CLI refuses to arm and returns `route_missing` instead of silently enabling a cron job that cannot push. The actual monitoring frequency is managed by the `schedule` command, not by editing config values.

On the first successful `add` or `onboard finalize`, if `profile.language` is still empty, SignalRadar persists the detected system-message language into the user config so background jobs keep using the same language later.

```bash
signalradar.py schedule              # Show current status (driver, interval, last_run)
signalradar.py schedule 10           # Auto driver (crontab-first)
signalradar.py schedule 10 --driver openclaw  # Force openclaw cron

The first automatic digest is bootstrap-only: SignalRadar records `~/.signalradar/cache/digest_state.json` silently and starts automatic user-facing digest delivery from the next report cycle.
signalradar.py schedule 10 --driver crontab   # Force system crontab
signalradar.py schedule disable      # Disable auto-monitoring completely
```

The `check_interval_minutes` config key is a display value that gets updated automatically when you use `schedule`. Do not edit it directly to change monitoring frequency — use `schedule` instead.

Minimum interval: 5 minutes (prevents overlapping runs).

### Drivers

| Driver | How it works | Cost |
|--------|-------------|------|
| `openclaw` | OpenClaw platform cron, `--session isolated`, announce delivery for OpenClaw background runs | Has model invocation cost |
| `crontab` (preferred) | System crontab, runs shell command directly; uses `--push` to deliver notifications via `openclaw message send` (zero LLM cost) | Zero model cost |

## Notes

- Runtime behavior is controlled by CLI/config; env vars are only used for path overrides.
- `config.example.json` in the repo root shows a minimal working config.
- `config/default_config.json` is the shipped template for first-run initialization.
