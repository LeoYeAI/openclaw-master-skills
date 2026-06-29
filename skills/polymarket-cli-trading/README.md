# Polymarket Trading Skill

> Trade prediction markets from your terminal. Browse markets, place bets, manage positions, and collect rewards using Polymarket's official CLI.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Rust](https://img.shields.io/badge/rust-stable-orange.svg)](https://www.rust-lang.org)
[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-green.svg)](https://clawhub.com)

## Why This Skill?

**For traders who want:**
- Speed: Place and cancel orders faster than the web UI
- Automation: Script market-making and hedging strategies
- Transparency: See exactly what commands run before execution
- Control: Manage everything from your terminal
- Data: JSON output for programmatic analysis

**What makes this different:**
This skill wraps Polymarket's official Rust CLI, giving you full access to the CLOB (Central Limit Order Book) for limit orders, market orders, batch operations, reward tracking, and on-chain token management — all from the terminal.

## Quick Start (5 Minutes)

### Step 1: Install the CLI

**macOS / Linux (Homebrew):**
```bash
brew tap Polymarket/polymarket-cli https://github.com/Polymarket/polymarket-cli
brew install polymarket
```

**Shell script:**
```bash
curl -sSL https://raw.githubusercontent.com/Polymarket/polymarket-cli/main/install.sh | sh
```

**Build from source:**
```bash
git clone https://github.com/Polymarket/polymarket-cli
cd polymarket-cli
cargo install --path .
```

### Step 2: Browse Markets (No wallet needed)

```bash
# Search for markets
polymarket markets search "bitcoin"

# List trending markets
polymarket markets list --limit 10

# Check an order book
polymarket clob book TOKEN_ID
```

### Step 3: Set Up a Wallet (For trading)

```bash
# Guided setup
polymarket setup

# Or manually
polymarket wallet create
polymarket approve set  # needs MATIC for gas
```

### Step 4: Place Your First Order

```bash
# Check balance
polymarket clob balance --asset-type collateral

# Place a limit order (maker-only = zero fees + rebates)
polymarket clob create-order --token TOKEN_ID --side buy --price 0.50 --size 10 --post-only
```

## What You Can Do

### Market Research
- Search and browse prediction markets
- View order books and price history
- Check spreads, midpoints, and fee rates
- Track market volume and open interest

### Trading
- Place limit orders (maker-only for zero fees)
- Place market orders for instant execution
- Batch multiple orders simultaneously
- Cancel individual orders or all at once

### Portfolio Management
- View positions and P/L
- Check collateral and conditional token balances
- Track trade history
- Redeem winnings from resolved markets

### Rewards & Analytics
- Check daily liquidity rewards and earnings
- Verify orders are scoring rewards
- View leaderboards and whale activity
- Monitor reward percentages by market

### On-Chain Operations
- Split USDC into YES/NO conditional tokens
- Merge tokens back to USDC
- Redeem winning tokens after resolution
- Bridge assets from other chains

## Command Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Market Research** |
| List markets | `polymarket markets list --limit 10` |
| Search markets | `polymarket markets search "query"` |
| Get market details | `polymarket markets get SLUG` |
| View order book | `polymarket clob book TOKEN_ID` |
| Check price/spread | `polymarket clob spread TOKEN_ID` |
| Price history | `polymarket clob price-history TOKEN_ID --interval 1d` |
| **Trading** |
| Limit order | `polymarket clob create-order --token TID --side buy --price 0.50 --size 10` |
| Market order | `polymarket clob market-order --token TID --side buy --amount 5` |
| Batch orders | `polymarket clob post-orders --tokens "T1,T2" --prices "0.4,0.6" --sizes "10,10"` |
| View orders | `polymarket clob orders` |
| Cancel order | `polymarket clob cancel ORDER_ID` |
| Cancel all | `polymarket clob cancel-all` |
| **Portfolio** |
| Check balance | `polymarket clob balance --asset-type collateral` |
| View positions | `polymarket data positions 0xADDRESS` |
| Trade history | `polymarket clob trades` |
| **Rewards** |
| Current rewards | `polymarket clob current-rewards` |
| Earnings | `polymarket clob earnings --date 2026-03-01` |
| Order scoring | `polymarket clob order-scoring ORDER_ID` |
| **On-Chain** |
| Split to tokens | `polymarket ctf split --condition 0xCOND --amount 10` |
| Merge to USDC | `polymarket ctf merge --condition 0xCOND --amount 10` |
| Redeem winnings | `polymarket ctf redeem --condition 0xCOND` |
| **Account** |
| Wallet info | `polymarket wallet show` |
| Approve contracts | `polymarket approve set` |
| API health | `polymarket clob ok` |

## Key Concepts

### Token IDs vs Condition IDs
- **Token ID**: Long numeric string identifying a specific outcome (YES or NO). Used for trading.
- **Condition ID**: Hex string (0x...) identifying a market. Used for on-chain operations.
- Get both from `polymarket markets get SLUG` or `polymarket -o json markets get SLUG`.

### Maker vs Taker
- **Maker orders** (limit orders with `--post-only`): Zero fees, earn daily USDC rebates
- **Taker orders** (market orders): Pay up to ~1.56% fee at 50/50 odds
- Always prefer maker orders unless you need instant execution.

### Rewards
- Liquidity rewards distributed daily at midnight UTC
- Two-sided orders (both YES and NO) earn ~3x single-sided
- Rewards decay quadratically with distance from midpoint
- Use `polymarket clob order-scoring ORDER_ID` to check eligibility

## Safety

- All trades are **real money** on Polygon mainnet — there is no paper trading mode
- Start with small positions to learn the system
- Always use `--post-only` for limit orders to avoid taker fees
- Keep MATIC in your wallet for gas (on-chain operations)
- Never share your private key
- Verify token IDs and amounts before confirming trades

## Requirements

| Requirement | Details | How to Get |
|-------------|---------|------------|
| **polymarket CLI** | Official Rust CLI | `brew install polymarket` |
| **Polygon wallet** | For signing transactions | `polymarket wallet create` |
| **USDC** | Settlement currency | Bridge or transfer to Polygon |
| **MATIC** | Gas for on-chain ops | Bridge or transfer to Polygon |

## Installation via ClawHub

```bash
clawhub install polymarket-trading
```

**From source:**
```bash
git clone https://github.com/lacymorrow/openclaw-polymarket-trading-skill.git
cp -r openclaw-polymarket-trading-skill ~/.agents/skills/polymarket-trading
```

## Learn More

- [Polymarket CLI](https://github.com/Polymarket/polymarket-cli) — Official CLI source
- [Polymarket Docs](https://docs.polymarket.com/) — Platform documentation
- [CLOB API Docs](https://docs.polymarket.com/developers/) — API reference
- [Liquidity Rewards](https://docs.polymarket.com/developers/market-makers/liquidity-rewards) — Reward mechanics
- [Maker Rebates](https://docs.polymarket.com/developers/market-makers/maker-rebates-program) — Fee structure

## Disclaimer

**This skill provides tools for trading on prediction markets. Trading involves risk of loss.**

- This skill is educational and informational only
- Not financial advice — do your own research
- Start with small amounts to learn
- Only trade with money you can afford to lose
- Understand the risks before trading

By using this skill, you acknowledge that trading decisions are your own responsibility.
