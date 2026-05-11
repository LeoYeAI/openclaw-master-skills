# CLAUDE.md — SignalRadar

## Project Overview

SignalRadar monitors Polymarket prediction markets for probability changes and sends alerts when thresholds are crossed. Users explicitly add markets by URL — no auto-discovery.

## Key Architecture

- **Entry point**: `scripts/signalradar.py` (CLI dispatcher)
- **Core pipeline**: `run_signalradar_job.py` → ingest → decide → deliver
- **Commands**: `doctor`, `add`, `list`, `remove`, `run`, `config`, `schedule`
- **Zero dependencies**: Python 3.9+ stdlib only (no pip packages)
- **Data source**: Polymarket gamma API (`gamma-api.polymarket.com`)
- **Watchlist storage**: `config/watchlist.json` (single source of truth)

## Important Conventions

- All scripts are in `scripts/`. No top-level Python files.
- Config lives in `config/`. User config: `config/signalradar_config.json`. Watchlist: `config/watchlist.json`.
- Baselines stored in `cache/baselines/` (gitignored).
- The `outcomePrices` field from Polymarket API is a JSON-encoded string, not a Python list. Always use `json.loads()` to parse it.
- There are no "modes" — all entries are checked together via `signalradar.py run`.

## Testing

```bash
# Health check
python3 scripts/signalradar.py doctor --output json

# Dry-run (no side effects)
python3 scripts/signalradar.py run --dry-run --output json

# Prepublish gate
python3 scripts/sr_prepublish_gate.py --json
```

## Delivery Adapters

- `openclaw` — OpenClaw platform messaging (default when installed via ClawHub)
- `file` — append alerts to local JSONL file
- `webhook` — HTTP POST to any webhook endpoint (Slack, Discord, etc.)

## Do NOT

- Modify `cache/` or baseline files unless user explicitly asks
- Auto-add markets — wait for user to provide URLs
- Create cron jobs outside of the `schedule` command flow
- Assume `outcomePrices` is a Python list (it's a JSON string)
- Put optional env vars in `requires.env` (use `envHelp` instead)
- Use or mention Notion integration (removed in v0.5.0)
