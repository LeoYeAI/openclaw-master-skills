# Kalshi Trading Skill

> Trade CFTC-regulated prediction markets from your terminal. Browse markets, place orders, stream live prices, and view ASCII candlestick charts — all in USD, fully legal in the US.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Go](https://img.shields.io/badge/go-1.25+-00ADD8.svg)](https://go.dev)
[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-green.svg)](https://clawhub.com)

## Why This Skill?

**For traders who want:**
- Legal US prediction market access (CFTC-regulated)
- USD settlement (no crypto wallets, no blockchain, no gas fees)
- Built-in paper trading (demo mode by default)
- Real-time WebSocket streaming from the terminal
- ASCII candlestick charts
- Bot-friendly JSON output with structured exit codes

**What makes this different:**
This skill wraps `kalshi-cli`, a Go-based CLI that provides full access to Kalshi's exchange — limit orders, market orders, batch operations, order groups, RFQs, subaccounts, and real-time streaming. Demo mode by default means you can't accidentally trade real money.

## Quick Start (5 Minutes)

### Step 1: Install the CLI

```bash
brew install 6missedcalls/tap/kalshi-cli
```

### Step 2: Authenticate

```bash
kalshi-cli auth login
# Follow prompts to add your public key at kalshi.com/account/api-keys
```

### Step 3: Browse Markets (Demo)

```bash
kalshi-cli markets list --status open --limit 10
kalshi-cli markets orderbook KXBTC-26FEB12-B97000
kalshi-cli markets candlesticks KXBTC-26FEB12-B97000 --series KXBTC
```

### Step 4: Place Your First Order (Demo)

```bash
kalshi-cli portfolio balance
kalshi-cli orders create --market KXBTC-26FEB12-B97000 --side yes --qty 10 --price 50
```

### Step 5: Go Live (When Ready)

```bash
kalshi-cli --prod orders create --market KXBTC-26FEB12-B97000 --side yes --qty 10 --price 50
```

## What You Can Do

### Market Research
- Search and browse prediction markets by category (Crypto, Politics, Sports, Economics, Weather)
- View order books with visual bid/ask display
- ASCII candlestick charts with volume sparklines
- Recent trade history

### Trading
- Limit orders (buy/sell YES or NO contracts)
- Market orders for instant execution
- Batch orders from JSON files
- Amend existing orders (price and/or quantity)
- Order groups to cap total fills across multiple orders

### Portfolio Management
- Check balance (available, portfolio value, total)
- View positions with P/L
- Trade fill history
- Settlement payouts from resolved markets
- Subaccount management (up to 32)

### Real-Time Streaming
- Live price ticker via WebSocket
- Orderbook delta streaming
- Public trade feed
- Your order status changes
- Your fill and position notifications

### Block Trading (RFQ)
- Create Requests for Quotes for large orders
- Respond to and accept quotes
- Institutional-grade execution

## Command Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Setup** |
| Install | `brew install 6missedcalls/tap/kalshi-cli` |
| Login | `kalshi-cli auth login` |
| Check status | `kalshi-cli auth status` |
| **Research** |
| List open markets | `kalshi-cli markets list --status open --limit 20` |
| Browse by category | `kalshi-cli markets series list --category Crypto` |
| Get market details | `kalshi-cli markets get TICKER` |
| View order book | `kalshi-cli markets orderbook TICKER` |
| Candlestick chart | `kalshi-cli markets candlesticks TICKER --series SERIES` |
| Recent trades | `kalshi-cli markets trades TICKER --limit 20` |
| **Trading** |
| Buy YES (limit) | `kalshi-cli orders create --market TICKER --side yes --qty 10 --price 50` |
| Buy NO (limit) | `kalshi-cli orders create --market TICKER --side no --qty 10 --price 30` |
| Market order | `kalshi-cli orders create --market TICKER --side yes --qty 10 --type market` |
| Amend order | `kalshi-cli orders amend ORDER_ID --price 55` |
| Cancel order | `kalshi-cli orders cancel ORDER_ID` |
| Cancel all | `kalshi-cli orders cancel-all` |
| Batch orders | `kalshi-cli orders batch-create --file orders.json` |
| **Portfolio** |
| Balance | `kalshi-cli portfolio balance` |
| Positions | `kalshi-cli portfolio positions` |
| Trade fills | `kalshi-cli portfolio fills --limit 50` |
| Settlements | `kalshi-cli portfolio settlements` |
| **Streaming** |
| Live prices | `kalshi-cli watch ticker TICKER` |
| Orderbook | `kalshi-cli watch orderbook TICKER` |
| Your fills | `kalshi-cli watch fills` |
| **Production** |
| Any command, live | `kalshi-cli --prod [command]` |

## Key Concepts

- **Demo by default**: CLI uses fake money unless you pass `--prod`
- **All values in cents**: Prices 1-99, balances in cents ($100 = 10000)
- **Structured tickers**: `KXBTC-26FEB12-B97000` = series + date + strike
- **Events group markets**: One event has multiple strike-level markets
- **Order groups**: Cap total fills across orders (essential for market-making)
- **USD settlement**: No crypto, no wallets, no gas. Just dollars.
- **CFTC-regulated**: Fully legal in the United States

## Fees

| Type | Max at 50/50 odds |
|------|-------------------|
| Taker | 1.75c per contract |
| Maker | ~0.44c per contract |
| Settlement | Free |
| ACH withdrawal | $2 flat |

## Requirements

| Requirement | Details | How to Get |
|-------------|---------|------------|
| **kalshi-cli** | Go-based CLI | `brew install 6missedcalls/tap/kalshi-cli` |
| **Kalshi account** | Free signup | https://kalshi.com |
| **API key** | RSA key pair | Generate at kalshi.com/account/api-keys |

## Installation via ClawHub

```bash
clawhub install kalshi-trading
```

**From source:**
```bash
git clone https://github.com/lacymorrow/openclaw-kalshi-trading-skill.git
cp -r openclaw-kalshi-trading-skill ~/.agents/skills/kalshi-trading
```

## Learn More

- [kalshi-cli](https://github.com/6missedcalls/kalshi-cli) — CLI source
- [Kalshi API Docs](https://docs.kalshi.com/welcome) — API reference
- [Kalshi Fee Schedule](https://kalshi.com/fee-schedule) — Fee details
- [Liquidity Incentive Program](https://help.kalshi.com/incentive-programs/liquidity-incentive-program) — Rewards for market makers

## Disclaimer

**This skill provides tools for trading event contracts. Trading involves risk of loss.**

- This skill is educational and informational only
- Not financial advice — do your own research
- Start with demo mode (the default) to learn risk-free
- Only trade with money you can afford to lose

By using this skill, you acknowledge that trading decisions are your own responsibility.
