# Market Morning Brief

Daily morning and evening intelligence digest for prediction market traders. Scannable in 30 seconds.

## Install

```bash
clawhub install market-morning-brief
```

## Quick Start

1. Preview it immediately: `python scripts/morning_brief.py`
2. Optional: add Kalshi credentials in `~/.openclaw/config.yaml` to replace the portfolio preview with your live P&L
3. Optional: run `python scripts/evening_brief.py --mode market`

## What You Get

| Section | Source | Required |
|---------|--------|----------|
| **Portfolio P&L** | Kalshi API | Yes |
| **Polymarket Trending** | Public API | No (free) |
| **Edges** | Kalshalyst cache | Optional |
| **Divergences** | Arbiter cache | Optional |
| **X Signals** | Xpulse cache | Optional |
| **Crypto Prices** | Coinbase API | Optional |

Works standalone. First run shows a useful preview even before credentials are configured. Each additional skill adds a new section automatically.

## Evening Brief

Two modes: `--mode market` (lightweight activity summary) or `--mode news` (AI-filtered news digest with two-stage Qwen materiality gate).

## Full Documentation

See [SKILL.md](SKILL.md) for complete documentation including configuration, evening briefing pipeline, cache integration, and troubleshooting.

## Part of the OpenClaw Prediction Market Trading Stack

```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

**Author**: KingMadeLLC
