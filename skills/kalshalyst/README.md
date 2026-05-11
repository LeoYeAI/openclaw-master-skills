# Kalshalyst

> **IMPORTANT: This software is for informational and educational purposes only. It is not financial advice. Trading prediction markets involves substantial risk of loss. You may lose some or all of your invested capital. Use at your own risk. See [DISCLAIMER.md](DISCLAIMER.md) and [LICENSE](LICENSE) for full terms.**
<!-- CODEX: aligned README cost language with the public Anthropic-backed reference implementation. -->

Autonomous prediction market trading system for Kalshi. Scans markets, estimates mispricings with Claude, sizes positions with Kelly Criterion, and executes trades — all hands-off.

## Quick Start

1. Preview the scanner immediately: `python3 scripts/kalshalyst.py --dry-run`
2. Optional: add Kalshi credentials in `~/.openclaw/config.yaml` to switch from demo opportunities to live scan results
3. Configure auto-trader in `~/.openclaw/auto_trader_config.json` only if you want execution
4. Auto-trader dry run: `python3 scripts/auto_trader.py --dry-run`
5. Auto-trader live: `python3 scripts/auto_trader.py`

## Pipeline

| Phase | What It Does |
|-------|-------------|
| **1. FETCH** | Pull active Kalshi markets, pre-filter by blocklist, volume, timeframe, and sports |
| **3. ESTIMATE** | Claude contrarian analysis — finds reasons the market is wrong |
| **4. EDGE** | Calculate edge %, filter by minimum threshold |
| **4.5 FILTER** | Market selection filter — SKIP low-quality markets, BOOST high-conviction ones |
| **5. SIZE** | Kelly Criterion position sizing with confidence scaling |
| **6. EXECUTE** | Auto-place orders via Kalshi SDK with 6-layer safety controls |
| **CLEANUP** | Cancel stale resting orders (>60 min) before each scan |

## Safety Controls

The auto-trader includes six layers of protection: config kill switch, daily loss limit, portfolio exposure cap, concurrent position limit, duplicate detection, and per-trade risk check. Set `"enabled": false` in config to stop all trading instantly.

## Scheduling

Designed for hands-off operation via launchd (macOS) or cron. Recommended: 4 scans/day aligned to US news cycles.

## Cost

Reference path: Anthropic-backed Claude estimation plus optional free local Qwen fallback. First run shows demo opportunities if Kalshi credentials are missing so users can preview the scan before setup.

## Full Documentation

See [SKILL.md](SKILL.md) for complete documentation including configuration, contrarian prompts, blocklist management, Brier score tracking, and Kelly Criterion math.

## Part of the OpenClaw Prediction Stack

Built by **KingMade LLC** — [github.com/kingmadellc](https://github.com/kingmadellc)
