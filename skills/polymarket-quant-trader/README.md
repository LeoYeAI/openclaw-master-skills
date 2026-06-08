# Polymarket Quant Trader

Professional-grade prediction market trading system with 3 alpha streams: EV signal trading, self-improving strategy, and cross-platform arbitrage.

## Quick Install

1. Purchase the skill on [clawhub.com](https://clawhub.com)
2. Install via OpenClaw CLI:

```bash
openclaw skill install polymarket-quant-trader
```

3. Clone the polymarket-bot repo (included with purchase):

```bash
git clone <repo-url-provided-after-purchase>
cd polymarket-bot
npm install
cp .env.example .env
```

4. Configure your `.env` with wallet keys and risk parameters (see SKILL.md Setup Guide)

## Quick Start

```bash
# Paper trade first (DRY_RUN=true by default)
npm run agent:alpha          # EV signal trading
npm run research:auto        # Self-improving strategy
npm run arb:scan             # Cross-platform arbitrage
```

## What's Included

- **SKILL.md** — Complete trading system guide (3 alpha streams, 5 copy-paste recipes)
- **references/kelly-criterion-guide.md** — Deep dive on Kelly Criterion math for prediction markets
- **references/brier-score-explained.md** — Brier score theory and calibration targets
- **references/arb-mechanics.md** — Step-by-step cross-platform arbitrage mechanics

## Trigger Phrases

This skill activates when you mention: polymarket, prediction markets, kelly criterion, EV trading, arb detector, brier score, prediction market bot, quant trading, cross-platform arbitrage.

## Requirements

- Node.js 18+
- Polygon wallet with USDC (for live trading)
- TypeScript (tsx for script execution)

## Support

Built by Henry (Supermolt / Orion). For issues, open a ticket on clawhub.com.
