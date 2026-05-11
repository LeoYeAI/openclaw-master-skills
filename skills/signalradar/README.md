# SignalRadar

> 信号雷达 — Monitor Polymarket prediction markets for probability changes. Get alerts when thresholds are crossed.
>
> 监控 Polymarket 预测市场概率变化，超过阈值时推送通知。

You choose exactly which markets to monitor by providing Polymarket URLs. Zero dependencies (Python stdlib only).

你通过提供 Polymarket 链接来精确选择要监控的市场。零依赖（仅使用 Python 标准库）。

## Quick Start / 快速开始

```bash
git clone https://github.com/vahnxu/signalradar.git
cd signalradar

# 1. Health check / 健康检查
python3 scripts/signalradar.py doctor --output json

# 2. Add markets (guided setup or by URL) / 添加市场（引导式或通过链接）
python3 scripts/signalradar.py add
python3 scripts/signalradar.py add https://polymarket.com/event/gpt5-release-june

# 3. Monitoring auto-starts after first add (every 10 min)
# 首次添加后自动启动监控（每 10 分钟）

# 4. Check schedule status / 查看调度状态
python3 scripts/signalradar.py schedule

# 5. Manual check (dry-run) / 手动检查（试运行）
python3 scripts/signalradar.py run --dry-run --output json
```

First run records baselines. Subsequent runs detect changes and send alerts.
首次运行记录基线。后续运行检测变化并发送警报。

## How It Works / 工作原理

```
User adds URL  --->  SignalRadar  --->  Delivery Adapter
用户添加链接         (detect change)     (alert you)
                     检测变化              通知你
                     threshold check
                     阈值检查
```

1. You add markets by URL (`add`) / 通过链接添加市场
2. SignalRadar fetches live probability from Polymarket API / 从 Polymarket API 获取实时概率
3. Compares against recorded baseline / 与记录的基线对比
4. Sends alert when change exceeds threshold (default: 5 percentage points) / 变化超过阈值时发送警报（默认：5 个百分点）
5. Baseline updates after each alert / 每次警报后基线更新

## Commands / 命令

```bash
# First-time setup (bot mode, 3-step) / 首次设置（bot 模式，3 步）
python3 scripts/signalradar.py onboard --step preview --output json
python3 scripts/signalradar.py onboard --step confirm --keep 1,2,3 --output json
python3 scripts/signalradar.py onboard --step finalize --output json

# Add a market (guided setup or by URL) / 添加市场（引导式或通过链接）
python3 scripts/signalradar.py add                              # Guided setup (terminal) / 引导式（终端）
python3 scripts/signalradar.py add <polymarket-url> [--category AI]

# List all monitored entries / 列出所有监控条目
python3 scripts/signalradar.py list

# Show one monitored market / 查看单个监控市场
python3 scripts/signalradar.py show 2
python3 scripts/signalradar.py show gpt --output json

# Remove an entry by number / 按编号移除条目
python3 scripts/signalradar.py remove 3

# Run a check / 执行检查
python3 scripts/signalradar.py run [--dry-run] [--output json|openclaw]

# View or change settings / 查看或修改设置
python3 scripts/signalradar.py config [key] [value]
python3 scripts/signalradar.py config threshold.abs_pp 8.0

# Manage auto-monitoring schedule / 管理自动监控调度
python3 scripts/signalradar.py schedule [N|disable] [--driver auto|crontab|openclaw]

# Preview or send periodic digest / 预览或发送定期报告
python3 scripts/signalradar.py digest [--dry-run] [--force] [--output text|json|openclaw]

# Health check / 健康检查
python3 scripts/signalradar.py doctor --output json
```

For event URLs that expand to more than 3 markets, `add` now force-shows a market preview (count, type summary, and market list) and requires interactive confirmation. `--yes` is rejected on that large-batch path.

对于展开后超过 3 个市场的事件链接，`add` 现在会强制先展示市场预览（数量、类型摘要、市场列表），并要求交互确认；该大批量路径下 `--yes` 会被拒绝。

## Delivery: Get Alerts Your Way / 推送方式

### Webhook (Recommended / 推荐) — Slack, Discord, Telegram Bot API, etc.

Portable across all platforms (OpenClaw, Claude Code, standalone). Zero LLM cost when paired with `crontab` scheduling.
可跨所有平台使用（OpenClaw、Claude Code、独立部署）。配合 `crontab` 调度，零 LLM 成本。

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

Save as `~/.signalradar/config/signalradar_config.json`. / 保存为 `~/.signalradar/config/signalradar_config.json`。

### File (local JSONL log) / 文件（本地 JSONL 日志）

```json
{
  "delivery": {
    "primary": {
      "channel": "file",
      "target": "/path/to/alerts.jsonl"
    }
  }
}
```

### OpenClaw (platform messaging / 平台消息 — OpenClaw only)

Default when installed via ClawHub. Not portable to other platforms. See [OpenClaw install](#openclaw-install) below.
通过 ClawHub 安装时为默认选项。不可移植到其他平台。见下方 [OpenClaw 安装](#openclaw-install)。

## Auto-Monitoring / 自动监控

SignalRadar attempts to auto-enable 10-minute background monitoring after the first successful `add` or `onboard finalize` (v0.9.0). Prefers system `crontab` with `--push` (zero LLM cost); falls back to `openclaw cron` when crontab is unavailable.

**Route gate (OpenClaw users):** When using `openclaw` delivery with `crontab` scheduling, auto-monitoring requires a captured reply route (`~/.signalradar/cache/openclaw_reply_route.json`). If no route is stored, the CLI **refuses to arm** the cron job and returns `route_missing` — it will not silently enable a schedule that cannot push. The route is automatically captured during any foreground bot interaction. Use `schedule --output json` to check `route_ready` status.

SignalRadar 在首次 `add` 或 `onboard finalize` 成功后尝试自动启用 10 分钟后台监控（v0.9.0）。默认优先使用系统 `crontab` + `--push`（零 LLM 成本）；仅在 crontab 不可用时回退到 `openclaw cron`。**Route gate**：当推送通道为 `openclaw` + `crontab` 驱动 + 尚无已捕获的 reply route 时，CLI 拒绝启用 cron 任务并返回 `route_missing`，不会静默启用一个无法推送的调度。Route 在任意前台 bot 交互时自动捕获。用 `schedule --output json` 检查 `route_ready` 状态。

If `profile.language` is still empty on the first successful `add`, SignalRadar snapshots the detected system-message language into user config so background notifications stay consistent.
如果首次 `add` 成功时 `profile.language` 仍为空，SignalRadar 会把检测到的系统文案语言写入用户配置，避免后台通知再依赖瞬时环境猜测。

```bash
signalradar.py schedule              # Show current status / 显示当前状态
signalradar.py schedule 30           # Auto driver (crontab-first) / 自动选择驱动（优先 crontab）
signalradar.py schedule 10 --driver openclaw  # Force OpenClaw cron / 强制使用 OpenClaw cron
signalradar.py schedule 10 --driver crontab   # Force system crontab / 强制使用系统 crontab
signalradar.py schedule disable      # Disable auto-monitoring / 禁用自动监控
```

## Runtime Data Directory / 运行数据目录

SignalRadar stores user data outside the skill directory so `clawhub update` will not wipe your watchlist or baselines.

SignalRadar 将用户数据存放在 skill 目录外，避免 `clawhub update` 覆盖监控列表和基线。

- Default data root / 默认数据目录：`~/.signalradar/`
- Config / 配置：`~/.signalradar/config/signalradar_config.json`
- Watchlist / 监控列表：`~/.signalradar/config/watchlist.json`
- Baselines / 基线：`~/.signalradar/cache/baselines/`
- Audit log / 审计日志：`~/.signalradar/cache/events/signal_events.jsonl`
- Last run metadata / 最近运行状态：`~/.signalradar/cache/last_run.json`
- Digest snapshot state / 周报快照状态：`~/.signalradar/cache/digest_state.json`

For local testing, override with `SIGNALRADAR_DATA_DIR=/tmp/signalradar`.
本地测试可使用 `SIGNALRADAR_DATA_DIR=/tmp/signalradar` 覆盖默认目录。

### Threshold vs Frequency / 阈值 vs 频率

- **Threshold / 阈值** — how much probability must change before an alert fires. Use `config` to adjust.
  概率需要变化多少才触发警报。用 `config` 调整。
- **Frequency / 频率** — how often SignalRadar checks markets. Use `schedule` to adjust.
  SignalRadar 多久检查一次市场。用 `schedule` 调整。

## Understanding Results / 理解运行结果

| Status | Meaning / 含义 |
|--------|----------------|
| `BASELINE` | First observation. Baseline recorded, no alert. / 首次观测，记录基线，不发警报。 |
| `SILENT` | Change below threshold. No alert. / 变化低于阈值，不发警报。 |
| `HIT` | Threshold crossed. Alert sent. Baseline updated. / 超过阈值，发送警报，基线更新。 |
| `NO_REPLY` | No markets crossed threshold. / 无市场超过阈值。 |

Example HIT / HIT 示例：
```
GPT-5 release by June 2026: 32% -> 41% (+9pp), crossing 5pp threshold. Baseline updated to 41%.
GPT-5 在 2026 年 6 月前发布：32% -> 41%（+9pp），超过 5pp 阈值。基线已更新至 41%。
```

## Configuration / 配置

All optional. Works out of the box with defaults.
全部可选。开箱即用，默认配置即可运行。

| Setting / 设置 | Default / 默认值 | Description / 说明 |
|----------------|-------------------|---------------------|
| `threshold.abs_pp` | 5.0 | Alert threshold in percentage points / 警报阈值（百分点） |
| `threshold.per_category_abs_pp` | `{}` | Per-category override / 按分类覆盖阈值 |
| `delivery.primary.channel` | `webhook` | Supported: `webhook` (recommended), `openclaw`, `file` / 支持的推送通道 |
| `digest.frequency` | `weekly` | `off`, `daily`, `weekly`, `biweekly` / 定期报告频率 |
| `digest.day_of_week` | `monday` | Weekly digest weekday / 定期报告星期 |
| `digest.time_local` | `09:00` | Local send time for digest / 定期报告本地发送时间 |
| `digest.top_n` | `10` | Top movers shown in human digest / 周报文本中展示的最大变化条目数 |
| `baseline.cleanup_after_expiry_days` | 90 | Baseline cleanup after market ends / 市场到期后清理基线天数 |
| `profile.language` | `""` | System-message locale (`zh` / `en`), empty = automatic detection (env first, timezone fallback) / 系统文案语言 |

See [`references/config.md`](references/config.md) for full reference. / 完整参考请查看 `references/config.md`。

`run --output json` keeps the frozen fields (`status`, `request_id`, `ts`, `hits`, `errors`) and may include an `observations` array for agent-side filtering.

`run --output openclaw` is reserved for platform scheduling. It prints `HEARTBEAT_OK` on quiet runs, user-ready alert text on HIT runs, and digest text when a scheduled digest is due and the primary delivery channel is `openclaw`.

`add --output json` returns structured `added` / `skipped` results and includes a `schedule` object when the first successful `add` attempts auto-monitoring (the object is present even when route gate blocks arming, with `auto_enabled: false`). `onboard --step finalize --output json` returns its own `ONBOARD_COMPLETE` payload with a separate `schedule` field.

`digest --output json` returns a structured digest preview/snapshot. Human-readable digest text groups large multi-market events by event and shows top movers instead of dumping every market.

## Digest / 定期报告

SignalRadar v0.8.3 includes a periodic digest. It compares the current monitored state against the previous digest snapshot, not against the per-run alert baseline.

SignalRadar v0.8.3 已包含定期报告功能。它比较的是“当前监控状态”和“上一份周报快照”，而不是单次运行的告警基线。

- Includes both markets that already triggered realtime HIT alerts and markets with net-over-period changes that never crossed the realtime threshold.
  同时包含“已触发实时 HIT 的市场”和“虽然没触发实时阈值、但周期净变化依然明显的市场”。
- Uses grouped event summaries for large multi-market events.
  对大量子市场的事件使用按事件分组的摘要展示。
- Full detail remains available via `digest --output json`.
  完整明细通过 `digest --output json` 提供。
- The first automatic digest is bootstrap-only: SignalRadar records the initial digest snapshot silently, then starts user-facing automatic digest delivery from the next report cycle. Use `digest --force` if you want an immediate preview.
  首次自动周报只做静默建快照：SignalRadar 会先记录初始周报快照，从下一个周期开始才自动向用户发送周报。如需立即预览，请使用 `digest --force`。

## OpenClaw Install / OpenClaw 安装

If you use [OpenClaw](https://clawhub.com), install directly from the marketplace:
如果你使用 [OpenClaw](https://clawhub.com)，可以直接从市场安装：

```bash
clawhub install signalradar
```

## Requirements / 运行要求

- Python 3.9+
- Network access to `gamma-api.polymarket.com` / 需要网络访问 `gamma-api.polymarket.com`
- No pip dependencies (stdlib only) / 无 pip 依赖（仅标准库）

## License / 许可

MIT
