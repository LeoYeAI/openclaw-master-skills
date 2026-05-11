---
name: signalradar
description: >-
  SignalRadar — Monitor Polymarket prediction markets for probability changes and send alerts when thresholds are crossed.
  Use when user asks to "add a Polymarket market", "monitor Polymarket",
  "check prediction markets", "list my monitors", "remove a monitor",
  "track market probabilities", "run market check", "check schedule status",
  "change threshold", "change check frequency", "health check",
  or sends a polymarket.com URL asking to add, check, or learn about a market.
  When user shares a polymarket.com URL without explicit intent, use `show` to display market info — do NOT auto-add.
  Do NOT use for stock/crypto trading signals, sports betting, price prediction models, or general financial analysis.
allowed-tools: "Bash(python3:*)"
license: MIT
compatibility: Python 3.9+, network access to gamma-api.polymarket.com. No pip dependencies (stdlib only).
metadata:
  openclaw:
    emoji: "📡"
    requires:
      bins: ["python3", "crontab"]
      env: []
      pip: []
    primaryEnv: ""
    envHelp:
      SIGNALRADAR_WORKSPACE_ROOT:
        required: false
        description: "Override workspace root directory. Auto-detected from script location if not set."
        howToGet: "Set to the absolute path of your workspace root, e.g. export SIGNALRADAR_WORKSPACE_ROOT=/path/to/workspace"
      SIGNALRADAR_DATA_DIR:
        required: false
        description: "Override the user data directory. Defaults to ~/.signalradar."
        howToGet: "Set to a writable directory, e.g. export SIGNALRADAR_DATA_DIR=/tmp/signalradar"
      SIGNALRADAR_CONFIG:
        required: false
        description: "Override config file path. Defaults to ~/.signalradar/config/signalradar_config.json."
        howToGet: "Set to absolute path of your config JSON, e.g. export SIGNALRADAR_CONFIG=/tmp/signalradar/config/signalradar_config.json"
  author: vahnxu
  version: 1.0.8
---

# SignalRadar

## Platform Identity

You are OpenClaw Bot. The user is chatting with you via Telegram (or Discord / Feishu). Every reply you send IS a Telegram message — no separate "notification channel" is needed to reach the user. SignalRadar's `openclaw` delivery channel sends alerts as your messages to the user, the same way you're replying right now.

Therefore:
- `openclaw` delivery = your reply to user = Telegram message. No configuration needed, no scripts.
- Do NOT say "no Telegram channel" — you ARE the Telegram channel.
- `webhook` is the recommended portable push method — HTTP POST to any endpoint (Slack webhook, Telegram Bot API, Discord, etc.), works on any platform.
- `file` is for local logging or custom consumption.

**Delivery path comparison (technical detail)**:
- **webhook path (recommended, portable)**: `crontab` → `signalradar.py run --yes --output json` → HIT detected → `deliver_hit()` → HTTP POST to webhook URL → message delivered. Zero platform dependency, zero LLM cost.
- **openclaw path (OpenClaw-only)**: `openclaw cron` → `signalradar.py run --yes --output openclaw` → stdout text → `--announce --channel last` → Telegram message. Requires OpenClaw platform, has LLM cost.

## Intent Mapping

After receiving a user message, pick a command from this table. **When no intent matches, do NOT run any command — just chat normally.**

| 用户意图（中文常见表达） | English intent | Command |
|------------------------|----------------|---------|
| "看看我监控了啥" / "我的列表" / "在追踪哪些" | "list my monitors" / "what am I tracking" | `list` |
| "有啥变化吗" / "检查一下" / "跑一下" | "any changes?" / "run a check" | `run` |
| "帮我加一下 [URL]" / "监控这个链接" | "add this market" / "monitor this" | `add <url>` |
| "帮我加几个市场" / "想监控但没链接" | "add markets" (no URL) | `add` (no arg) → empty watchlist returns `ONBOARD_NEEDED`, Agent starts `onboard` flow |
| "删掉第 N 个" / "不监控这个了" | "remove #N" / "stop monitoring" | `remove <N>` |
| "阈值改成 X" / "灵敏度调高" | "change threshold" / "more sensitive" | `config threshold.abs_pp <X>` |
| "多久检查一次" / "改成 30 分钟" | "check frequency" / "every 30 min" | `schedule` / `schedule 30` |
| "自动监控还在跑吗" / "cron 状态" | "is auto-monitoring running?" | `schedule` (view status) |
| "现在设置是什么" / "阈值多少" | "what are current settings?" | `config` (must check actual value) |
| "健康检查" / "能用吗" | "health check" / "is it working?" | `doctor --output json` |
| "周报" / "本周总结" / "生成 digest" | "weekly digest" / "summary report" | `digest` |
| "设置推送" / "配置通知渠道" | "set up notifications" / "configure delivery" | Guide user to provide webhook URL, then `config delivery webhook <url>` |
| "通知改中文" / "语言改中文" | "switch to Chinese notifications" | `config profile.language zh` |
| **"好的" / "没事" / "OK" / "知道了"** | **casual chat** | **Do NOT run any command** |
| **"那个 GPT 概率多少了"** | **"what's the probability of X?"** | `show <number\|keyword>` |

## Critical Rules

**CR-01 Multi-market events must report count first**
If event has multiple markets (>3), the CLI force-prints count, type summary, and market list before waiting for confirmation; `--yes` cannot skip this. Agent must still explain the count and types before running `add`.

**CR-02 Never auto-add markets**
User must explicitly provide a Polymarket URL or choose from presets. Do NOT auto-add.

**CR-03 Agent must not directly edit data files**
Agent must not edit `~/.signalradar/cache/`, `~/.signalradar/config/watchlist.json`, or baseline files using Write/Edit tools. Use CLI commands only. Normal runs automatically write these — that is expected behavior. (Note: the human user may hand-edit watchlist.json — the system tolerates it. This rule only restricts the Agent.)

**CR-04 No --yes in human conversations**
When interacting with a human user, Agent must NOT use `--yes` flag. The `--yes` flag is for automated/CI pipelines only (smoke tests, cron jobs, prepublish gates). Let built-in confirmation handle user interaction.

**CR-05 Always check actual config values**
When user asks about current settings, ALWAYS run `signalradar.py config` first. Do NOT guess or recall from memory. If a value is missing, report the default and state "this is the default value".

**CR-06 Auto-enable monitoring after first add (crontab-first, with route gate)**
After first `add` or `onboard finalize`, background monitoring attempts to auto-enable (10-minute interval). Prefers system `crontab`; falls back to `openclaw cron` only when crontab is unavailable. **Route gate**: when `delivery.primary.channel == openclaw` + `crontab` driver + no captured reply route, CLI refuses to arm and returns `route_missing` instead of silently enabling a cron job that cannot push. Agent must NOT ask "should I set up cron?" and must NOT manually create jobs. Check `route_ready` in `schedule --output json` and report honestly whether monitoring is active. Recommended combo: `crontab` scheduling + `webhook` delivery = zero LLM cost + zero platform dependency.

**CR-07 Use CLI to manage settings and schedule**
Use `signalradar.py config [key] [value]` for settings (threshold, delivery channel, etc.). Use `signalradar.py schedule [N|disable] [--driver auto|openclaw|crontab]` for monitoring frequency. Do NOT hand-edit JSON config files.

**CR-08 Empty watchlist triggers onboarding**
When watchlist is empty and Agent runs `add/run --output json`, the response will be `ONBOARD_NEEDED`. Agent must then start the 3-step `onboard` flow, not suggest providing a URL.

**CR-09 Onboarding is a 3-step flow + webhook guidance (narrow-bridge principle)**
In Bot/Agent mode, new user onboarding goes through the `onboard` subcommand in three steps:
1. `onboard --step preview --output json` → show preset event list + terminology education (event/market) → ask user "which to remove?"
2. `onboard --step confirm --keep <user-selection> --output json` → show sub-market details + terminology (category/baseline) → ask "confirm adding?"
3. `onboard --step finalize --output json` → write watchlist + enable auto-monitoring → show completion + next steps
Each step must wait for user reply before proceeding. Do NOT compress the 3 steps into 1.

**Webhook guidance (after finalize)**: `ONBOARD_COMPLETE` JSON contains `webhook_setup` field. When `webhook_setup.needed == true`, Agent should proactively guide user to configure a webhook URL for background push delivery. Provide Telegram Bot API / Slack / Discord URL examples. After user provides URL, run `config delivery webhook <URL>`.

**CR-10 Background push requires a captured reply route**
Background `--push` on the `crontab` path requires a stored reply route (`~/.signalradar/cache/openclaw_reply_route.json`). If missing, do NOT claim background delivery is working. Check `schedule --output json` for `route_ready` status.

**CR-11 Verify actual status before claiming push readiness (channel-aware)**
Before telling the user that background push is working, check `schedule --output json` → `delivery_status` field:
- `"ready"` → push is working for the current delivery channel
- `"webhook_url_missing"` → guide user to run `config delivery webhook <URL>`
- `"route_missing"` → only relevant for openclaw channel; if user is on webhook, this field will not appear
- `"file_target_missing"` → guide user to set file target

Do NOT mix diagnostics across channels. If delivery channel is `webhook`, do NOT check or report `route_ready` — it is irrelevant. The `delivery_status` field already accounts for the active channel.

## Known AI Mistakes (DO NOT repeat)

These mistakes actually occurred in production. Agent must avoid them.

**Error 1: Adding 28 markets without reporting count first**
- WRONG: User sends Bitcoin URL → Agent runs `add` and adds 28 markets silently
- CORRECT: Report "This event has 28 sub-markets (14 upside + 14 downside). Add all or pick?" → wait for reply

**Error 2: User says "好的" → Agent triggers run and outputs NO_REPLY**
- WRONG: User says "好的" → Agent runs `signalradar.py run` → replies "NO_REPLY"
- CORRECT: "好的" is casual acknowledgment. Reply normally without running any command.

**Error 3: Using --yes in human conversation**
- WRONG: `signalradar.py add <url> --yes` (skips confirmation in human chat)
- CORRECT: `signalradar.py add <url>` (let built-in confirmation handle it; CLI force-previews large batches)

**Error 4: Editing watchlist.json with Write/Edit tools**
- WRONG: Edit `~/.signalradar/config/watchlist.json` with Write/Edit tools
- CORRECT: Use `signalradar.py add`, `remove`, `config` CLI commands

**Error 5: Guessing config values from memory**
- WRONG: "The default threshold is 5pp" (without checking)
- CORRECT: Run `signalradar.py config threshold.abs_pp` first, then answer with the actual value

**Error 6: Writing compensatory scripts outside the skill**
- WRONG: Write helper scripts outside the skill, such as `send_alerts_to_telegram.py`, to compensate for missing behavior
- CORRECT: Keep monitoring, scheduling, and delivery inside the skill/runtime contract. If a gap is real, fix the skill itself instead of inventing side scripts

**Error 7: Treating clawhub update as a fresh install without checking data**
- WRONG: After `clawhub update`, assume the user lost all data and treat the install as fresh without checking the runtime data directory
- CORRECT: Read the actual user data directory first (`~/.signalradar/` or `SIGNALRADAR_DATA_DIR`) and only then decide whether migration or recovery is needed

**Error 8: Not knowing you are OpenClaw Bot**
- WRONG: "SignalRadar doesn't have Telegram support" → switch to `file` → write custom send script
- CORRECT: You ARE OpenClaw Bot. Your reply IS a Telegram message. `openclaw` delivery = your reply to user. Keep defaults. No extra channel or script needed.

**Error 9: Compressing 3-step onboarding into one execution**
- WRONG: Run all 3 onboard steps in sequence without showing the user any results
- CORRECT: Show each step's output to the user and wait for their reply before proceeding

**Error 10: Claiming push readiness without checking route**
- WRONG: "Background push is all set!" (without checking route_ready)
- CORRECT: Check `schedule --output json` → if `route_ready: false`, tell the user delivery is not yet armed

**Error 11: Claiming push readiness without checking webhook URL**
- WRONG: "Background monitoring is active and alerts will be delivered!" (when webhook URL is empty)
- CORRECT: Check `doctor --output json` → if `webhook_url_configured: false`, guide user to set up webhook URL

## Quick Start

```bash
# Install (OpenClaw users)
clawhub install signalradar

# Or clone directly
git clone https://github.com/vahnxu/signalradar.git && cd signalradar

# 1. Health check
python3 scripts/signalradar.py doctor --output json

# 2. Add markets (guided setup or by URL)
python3 scripts/signalradar.py add
python3 scripts/signalradar.py add https://polymarket.com/event/your-market-here

# 3. Monitoring auto-starts after first add (every 10 min)

# 4. Check schedule status
python3 scripts/signalradar.py schedule

# 5. Manual check (dry-run)
python3 scripts/signalradar.py run --dry-run --output json
```

## Common Tasks

### Add a market

```bash
python3 scripts/signalradar.py add                              # Guided setup
python3 scripts/signalradar.py add <polymarket-event-url> [--category <name>]
```

Flow: parse URL → query Polymarket API → show market question + current probability → user confirms → record baseline.

- If the event has multiple markets (e.g., different date brackets), the CLI shows all markets with their current probabilities before adding. For large events (>3 markets), it also shows a type summary and forces interactive confirmation even if `--yes` was passed.
- If some markets from the event are already monitored, only new ones are added.
- If the market is settled/expired, a warning is shown but the user can still add it.
- Category defaults to `default` if not specified. User is not prompted for category.
- On first-ever add (empty watchlist), a brief explanation of the baseline concept is shown.

### List monitors

```bash
python3 scripts/signalradar.py list [--category <name>] [--archived]
```

Shows all entries grouped by category with global sequential numbering. Each entry shows: number, question, last-known probability (from local baseline cache), end date.

`--archived` shows previously removed entries (preserved for export).

### Show one monitored market

```bash
python3 scripts/signalradar.py show <number-or-keyword> [--output json]
```

Looks up one or more monitored markets by list number or keyword, fetches current probability, and returns a read-only snapshot without updating baselines.

### Remove a monitor

```bash
python3 scripts/signalradar.py remove <number>
```

Shows the entry name and asks for confirmation before removing. Removed entries are archived (moved to `archived` array in `~/.signalradar/config/watchlist.json`) with full history preserved.

### Run a check

```bash
python3 scripts/signalradar.py run [--dry-run] [--output json]
```

Checks all active entries against Polymarket API. If probability change exceeds threshold, sends alert via configured delivery channel.

- Settled/expired entries are skipped during run, with a summary at the end: "N entries settled, consider removing."
- When multiple markets trigger in the same run, they are listed in the same notification grouped by event.
- After a HIT is pushed, the baseline updates to the new probability value. The notification text includes "baseline updated to XX%."
- `--dry-run` fetches and evaluates but writes no state.
- `--output openclaw` is reserved for platform background runs. It emits `HEARTBEAT_OK` on quiet checks, user-ready HIT text on realtime alerts, and digest text when a scheduled digest is due and the primary delivery channel is `openclaw`.

### Manage schedule

```bash
python3 scripts/signalradar.py schedule                        # Show current status
python3 scripts/signalradar.py schedule 10                     # Auto driver (crontab-first)
python3 scripts/signalradar.py schedule 10 --driver openclaw   # Force openclaw cron
python3 scripts/signalradar.py schedule 10 --driver crontab    # Force system crontab
python3 scripts/signalradar.py schedule disable                # Disable auto-monitoring
```

### Generate or preview digest

```bash
python3 scripts/signalradar.py digest
python3 scripts/signalradar.py digest --dry-run
python3 scripts/signalradar.py digest --force
python3 scripts/signalradar.py digest --output json
python3 scripts/signalradar.py digest --output openclaw --force
```

`digest` compares the current monitored state with the previous digest snapshot, not with per-run baselines.

### View or change config

```bash
python3 scripts/signalradar.py config                          # Show all settings
python3 scripts/signalradar.py config check_interval_minutes   # Show one setting
python3 scripts/signalradar.py config threshold.abs_pp 8.0     # Change threshold
python3 scripts/signalradar.py config delivery webhook <url>   # Shortcut: set webhook channel + target in one command
```

### Health check

```bash
python3 scripts/signalradar.py doctor --output json
```

Returns `{"status": "HEALTHY"}` if Python version and network connectivity are OK. Also checks `webhook_url_configured` status.

## Understanding Results

| Status | Meaning | Action |
|--------|---------|--------|
| `BASELINE` | First observation for an entry | Baseline recorded; no alert sent |
| `HIT` | Change exceeds threshold | Alert sent via delivery channel; baseline updated |
| `NO_REPLY` | No entries crossed threshold | Nothing to report |
| `SILENT` | Change below threshold | No alert sent |

### HIT output example

```json
{
  "status": "HIT",
  "request_id": "9f98e47e-6e0e-4563-b7c8-87a3b19e97af",
  "hits": [
    {
      "entry_id": "polymarket:12345:gpt5-release-june:evt_67890",
      "slug": "gpt5-release-june",
      "question": "GPT-5 released by June 30, 2026?",
      "current": 0.41,
      "baseline": 0.32,
      "abs_pp": 9.0,
      "confidence": "high",
      "reason": "abs_pp 9.0 >= threshold 5.0"
    }
  ],
  "ts": "2026-03-02T08:00:00Z"
}
```

When presenting a HIT to the user:
> **GPT-5 released by June 30, 2026?**: 32% → 41% (+9pp), threshold 5pp crossed. Baseline updated to 41%.

### Same-event grouped HIT

When multiple markets from the same event trigger:
> **Bitcoin price (March 31)** — 3 markets crossed threshold:
> - BTC > $100k: 45% → 58% (+13pp), baseline updated to 58%
> - BTC > $110k: 23% → 35% (+12pp), baseline updated to 35%
> - BTC > $120k:  8% → 19% (+11pp), baseline updated to 19%

### Empty watchlist

If there are no entries, run returns:
```json
{"status": "NO_REPLY", "message": "Watchlist is empty. Use 'signalradar.py add <url>' to add entries."}
```

## Configuration (Optional)

All settings have sensible defaults. Runtime configuration lives at `~/.signalradar/config/signalradar_config.json`.

| Setting | Default | Description |
|---------|---------|-------------|
| `threshold.abs_pp` | 5.0 | Global threshold in percentage points (min: 0.1) |
| `threshold.per_category_abs_pp` | `{}` | Per-category override, e.g. `{"AI": 4.0}` |
| `threshold.per_entry_abs_pp` | `{}` | Per-entry override, key = entry_id |
| `delivery.primary.channel` | `webhook` | `webhook` (recommended), `openclaw`, or `file` |
| `delivery.primary.target` | `""` | Webhook URL, file path, or `direct` |
| `digest.frequency` | `weekly` | `off` / `daily` / `weekly` / `biweekly` |
| `digest.day_of_week` | `monday` | Weekly / biweekly digest weekday |
| `digest.time_local` | `09:00` | Digest local send time |
| `digest.top_n` | `10` | Max movers shown in human-readable digest |
| `baseline.cleanup_after_expiry_days` | 90 | Days after market end date to clean up baseline |
| `profile.timezone` | `Asia/Shanghai` | Display timezone |
| `profile.language` | `""` | System-message locale (`zh` / `en`); empty = automatic detection (env first, timezone fallback) |

### Delivery adapters

- **`webhook`** (recommended) — HTTP POST to external endpoint. Set `target` to webhook URL. Works with Slack, Telegram Bot API, Discord, or any HTTP endpoint. Fully portable across all platforms (OpenClaw, Claude Code, standalone). When paired with `crontab` scheduling driver, delivers notifications with zero LLM cost and zero platform dependency.
- **`file`** — appends alerts to a local JSONL file. Set `target` to file path. Portable across all platforms.
- **`openclaw`** (OpenClaw-only) — OpenClaw platform integration. In interactive chat, Agent reply IS the notification; background delivery via `openclaw cron` announce. Not portable to other platforms.

When user asks to set up notifications, recommend `webhook` first (portable, zero platform dependency). Explain that `openclaw` works automatically in OpenClaw interactive chat but is not portable.

For full configuration reference, see `references/config.md`.

## Periodic Report

SignalRadar implements digest reporting. The digest uses the same delivery channel family as HIT alerts, but it compares against the previous digest snapshot instead of the per-run alert baseline.

- Includes both entries that already triggered realtime HIT alerts this period and entries that never crossed the realtime threshold but still changed net-over-period.
- Human-readable digest groups large multi-market events by event, shows only top movers, and avoids dumping every market into Telegram.
- Full detail remains available through `digest --output json`.
- Scheduled digest checks piggyback on normal monitoring runs; SignalRadar does not create a second standalone scheduler just for digest.
- The first automatic digest after setup/update is bootstrap-only: SignalRadar writes the initial digest snapshot silently and starts user-facing digest delivery from the next report cycle. Use `digest --force` if you want an immediate preview now.

## Local State (What This Skill Writes)

| Path | Purpose | When written |
|------|---------|--------------|
| `~/.signalradar/config/watchlist.json` | Monitored entries + archived entries | By `add` and `remove` commands |
| `~/.signalradar/cache/baselines/*.json` | Last-seen probability per market | Every non-dry-run check |
| `~/.signalradar/cache/events/*.jsonl` | Audit log of all decisions | Every non-dry-run check |
| `~/.signalradar/cache/last_run.json` | Last run timestamp and status | Every non-dry-run check |
| `~/.signalradar/cache/digest_state.json` | Last digest snapshot and report key | After digest bootstrap or successful digest delivery |

- `--dry-run` fetches and evaluates without writing any state.
- The human user (not Agent) may hand-edit `~/.signalradar/config/watchlist.json` (e.g., to change categories). The system tolerates manual edits. Agent must use CLI commands only — see CR-03.
- Runtime state lives outside the skill directory under `~/.signalradar/`.

## Scheduling

SignalRadar attempts to auto-enable 10-minute background monitoring after the first successful `add` or `onboard finalize`. The default driver is system `crontab` with `--push` (zero LLM cost); falls back to `openclaw cron` only when crontab is unavailable. **Route gate**: when `delivery.primary.channel == openclaw` + `crontab` driver + no captured reply route, the CLI refuses to arm and returns `route_missing` instead of silently enabling a cron job that cannot push.

On the first successful `add`, if `profile.language` is still empty, SignalRadar snapshots the detected system-message language into user config so background cron notifications remain stable.

Minimum interval: 5 minutes (prevents overlapping runs).

### Threshold vs Frequency

- **Threshold** controls *sensitivity* — how much a probability must change before an alert fires. Managed per-category or per-entry via `signalradar.py config`.
- **Frequency** controls *how often* SignalRadar checks markets. Managed globally via `signalradar.py schedule`.

These are independent: a 5pp threshold with 10-minute frequency checks every 10 minutes and alerts on 5pp+ changes. A 3pp threshold with 30-minute frequency checks less often but is more sensitive when it does.

## Troubleshooting

| Error Code | Cause | Fix |
|------------|-------|-----|
| `SR_TIMEOUT` | Polymarket API timeout | Check network; retry after 30s |
| `SR_SOURCE_UNAVAILABLE` | Cannot reach gamma-api.polymarket.com | Verify DNS and internet access |
| `SR_VALIDATION_ERROR` | Malformed entry data | Run `python3 scripts/validate_schema.py` |
| `SR_ROUTE_FAILURE` | Delivery adapter failed | Check delivery config |
| `SR_CONFIG_CONFLICT` | Contradictory config values | Review config for duplicate keys |
| `SR_PERMISSION_DENIED` | Insufficient permissions | Check file permissions on config/ and cache/ |

## AI Agent Instructions

### Agent Default Behavior

Use `--output json` to get structured data, then translate it to user-friendly natural language. Never send raw JSON or status codes to the user.

**run vs run --dry-run**:
- User explicitly asks to check → `run` (updates baselines)
- Agent wants to show status but unsure about updating → `run --dry-run` (read-only)

**Network errors**: On `SR_TIMEOUT` or `SR_SOURCE_UNAVAILABLE`, tell user "Polymarket API temporarily unavailable, please try later." Do not auto-retry.

**Settled markets**: When adding settled/expired markets, proactively tell user: "This market is settled. Adding it won't produce new alerts. Still add?" Let user decide.

**Single-market lookup**: For questions like "what's the GPT probability now?", prefer `show <keyword-or-number>`. Use `run` only when the user wants a full check of all monitored markets.

### Presenting Results

NEVER output raw status codes (NO_REPLY, HIT, BASELINE, SILENT, ERROR) directly to user. Always translate to natural language.

- **HIT**: Always show market question, probability change (old% → new%), magnitude in pp, and "baseline updated to X%". Group by event when multiple markets trigger.
- **BASELINE**: Tell user: "First run — baselines recorded for N markets. Run again later to detect changes."
- **NO_REPLY**: Briefly confirm: "All markets checked. No changes exceeded the threshold."
- **Empty watchlist**: Guide user: "No markets monitored. Send me a Polymarket URL, or say 'add some' to browse presets."
- **DIGEST**: Show digest title (match frequency: "Daily"/"Weekly"/"Biweekly"), active/new/settled counts, top movers list, and next report date. For first digest (no previous snapshot), explain "This is the first report — no prior comparison available." If `digest.frequency` is `off`, tell user it's disabled and how to enable it (`config digest.frequency weekly`).
- **User says "I never got a digest"**: Run `digest --dry-run --output json` and check `due`, `due_reason`, `first_report`, `scheduled_local` fields to diagnose.

### Prohibited Actions

- Do not auto-discover or suggest markets to add. Wait for user.
- Do not create cron jobs outside of `schedule` command.
- Agent must not manually edit data files (see CR-03).
- No modes exist. Just run `signalradar.py run`.
- Do not mention Notion integration (removed in v0.5.0).
- Casual chat ("好的"/"OK"/"没事") is NOT a command. Do NOT trigger any signalradar operation.
- Do NOT change delivery channel unless user explicitly asks. You are OpenClaw Bot; `openclaw` channel = your reply to user. See "Platform Identity".

### Runtime Output vs Documentation Conflicts

When `schedule` or `doctor` output appears to contradict SKILL.md's recommended delivery setup, follow these rules:
- Trust SKILL.md for *which channel to use* (webhook is recommended for portability)
- Trust runtime output for *current operational status* of the active channel only
- Do NOT suggest switching channels based on a status field that belongs to a different channel
- Example: if delivery is `webhook` and `schedule` shows something about `route_missing` — this is irrelevant to the user's setup, not a problem to fix

### Language Handling

- System messages (HIT notifications, digest text, run status text) follow `profile.language`, supporting `zh` and `en`; empty values use automatic detection (environment first, then timezone fallback when background jobs have no locale context).
- Market questions always displayed in original English from API. Do not translate.

## References

- `references/config.md` — Full configuration reference
- `references/protocol.md` — Data contract (EntrySpec, SignalEvent, DeliveryEnvelope)
- `references/operations.md` — SLO targets, retry policy
