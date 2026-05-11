# Prediction Stack Setup

Interactive setup wizard for the [OpenClaw Prediction Market Trading Stack](https://github.com/kingmadellc/openclaw-prediction-stack).

<!-- CODEX: reconciled stack size and cost language with the public reference implementation. -->
Turns the 10-skill stack into a connected, proactive trading system. Creates scheduled scans, enables iMessage delivery, configures API keys, and tests the full pipeline — in under 5 minutes.

The runtime path is the eight core operational skills. `prediction-stack-orchestrator` is documented in the stack as a premium/experimental automation layer.

## Quick Start

1. Install the stack skills you want (minimum: Kalshalyst + Kalshi Command Center + Market Morning Brief)
2. Install this skill: `clawhub install prediction-stack-setup`
3. Tell your agent: **"Set up my prediction stack"**
4. Follow the interactive wizard

## What It Creates

- **6 scheduled jobs**: morning brief, evening brief, edge scan, social signal scan, drift monitor, arbitrage scan
- **Heartbeat config**: 30-minute ambient awareness during waking hours
- **iMessage delivery**: All alerts route to your phone via BlueBubbles
- **Unified config**: Single `config.yaml` with all API keys and thresholds

## Files

- `SKILL.md` — Complete setup procedure and system documentation
- `config.example.yaml` — Configuration template with sensible defaults

## Cost

The reference implementation assumes Anthropic API spend for Claude-based Kalshalyst runs, with local Qwen handling Xpulse and fallback inference. Everything else is free-tier or local.
