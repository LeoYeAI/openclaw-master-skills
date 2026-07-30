# Xpulse

Real-time X/Twitter social signal scanner for prediction market traders. Zero API cost — scans via DuckDuckGo with two-stage local Qwen AI filtering.
<!-- CODEX: synchronized the documented Ollama model with the runtime default. -->

## Install

```bash
clawhub install xpulse
```

## Quick Start

1. Install Ollama from https://ollama.ai and pull Qwen: `ollama pull qwen3:latest`
2. Get a Kalshi API key at https://kalshi.com (Settings → API)
3. Configure topics and credentials in `~/.openclaw/config.yaml`
4. Run: `python scripts/xpulse.py`

## Pipeline

| Stage | What It Does |
|-------|-------------|
| **Signal Detection** | Scan X via DuckDuckGo, analyze with Qwen for tradeable signals |
| **Materiality Gate** | Compare against 48h history, filter noise and repeats (fail-closed) |
| **Position Matching** | Only alert on signals matching active Kalshi positions |

## Cost

$0. DuckDuckGo is free, Ollama runs locally, Kalshi read-only API is free.

## Full Documentation

See [SKILL.md](SKILL.md) for complete documentation including configuration, materiality gate design, position matching logic, and troubleshooting.

## Part of the OpenClaw Prediction Market Trading Stack

```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

**Author**: KingMadeLLC
