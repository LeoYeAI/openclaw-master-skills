# Kalshi Command Center

Complete Kalshi trading command interface for OpenClaw — portfolio P&L, live market scanning, trade execution, and risk management.

## Install

```bash
clawhub install kalshi-command-center
```

## Quick Start

1. Get a Kalshi API key at https://kalshi.com (Settings → API)
2. Set environment variables: `KALSHI_KEY_ID` and `KALSHI_KEY_PATH`
3. Run commands through your OpenClaw agent: `portfolio`, `scan`, `execute`, `market`

## Commands

| Command | Description |
|---------|-------------|
| `portfolio` | View positions with real-time P&L |
| `scan` | Scan 600+ markets with heuristic edge scoring |
| `execute` | Place trades with built-in risk limits |
| `market` | Get detailed market data by ticker |

## Safety

Built-in risk limits: $25 max trade, 100 contract cap, $50 daily loss cutoff. All configurable.

## Full Documentation

See [SKILL.md](SKILL.md) for complete documentation including configuration, API reference, and troubleshooting.

## Part of the OpenClaw Prediction Market Trading Stack

```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

**Author**: KingMadeLLC
