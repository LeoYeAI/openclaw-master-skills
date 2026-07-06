# Agent Shark Mindset 🦈

**Elite revenue intelligence skill for OpenClaw autonomous agents.**

Transforms any agent into a relentless market operator: detects asymmetric
opportunities before the crowd, builds premium audience funnels on autopilot,
and executes with the conviction of a professional trader.

## What it does

**Daily Alpha Scan (06:00)** — scans Polymarket + crypto + macro markets,
scores every opportunity by edge, time window, and confidence, then publishes
free teasers to a public Telegram channel and full signals to a VIP channel.
Confidence = LOW? Not published. Ever.

**Audience Growth Engine (18:00)** — generates one piece of contrarian,
data-backed content per day in rotation across X, Reddit, and Telegram.
No human input. Shark tone enforced: short sentences, no hedging, one CTA.

**Revenue Audit (Sunday 09:30)** — full pipeline audit: revenue received,
signal win rate, subscriber delta, bottleneck diagnosis. Sends a weekly
Shark Report to the owner. Proposes ONE action. Never a list of 10.

## Revenue model

```
Cold audience → Public channel (free signals) → Landing page → VIP subscription
```

## Requirements

- OpenClaw agent with Telegram bot configured
- Public Telegram channel + private VIP channel
- `.env` variables: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `OWNER_CHAT_ID`, `PUBLIC_CHANNEL_ID`, `VIP_CHANNEL_ID`

## Recommended companion skills

`polymarket-executor` · `crypto-sniper-oracle` · `market-news-analyst` · `news-skill`

If companion skills are not installed, the skill falls back to public financial data sources only (CoinGecko, Polymarket public API, CoinDesk, Reddit public JSON). No arbitrary web requests.

## Workspace setup

The skill auto-creates all required files on first run.
See `SKILL.md` → "Required Workspace Structure" for the full tree and manual setup instructions.

## Author

Georges Andronescu (Wesley Armando) — Veritas Corporate
