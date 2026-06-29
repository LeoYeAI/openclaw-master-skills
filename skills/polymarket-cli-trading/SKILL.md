---
name: polymarket-trading
description: Trade prediction markets on Polymarket using the official polymarket CLI. Use when the user wants to browse prediction markets, place bets, manage orders, check positions, view order books, or trade on market outcomes. Also use when they mention "prediction market," "bet," "polymarket," "YES/NO," "order book," "CLOB," "limit order," "market order," "hedge," "arbitrage," "liquidity rewards," or "conditional tokens."
metadata:
  openclaw:
    emoji: "🔮"
    requires:
      bins: ["polymarket"]
    homepage: "https://github.com/Polymarket/polymarket-cli"
    repository: "https://github.com/lacymorrow/openclaw-polymarket-trading-skill"
    install:
      - id: "brew-polymarket"
        kind: "brew"
        formula: "polymarket"
        bins: ["polymarket"]
        label: "Install Polymarket CLI (Homebrew)"
---

# Polymarket Trading Skill

Trade prediction markets on Polymarket through the official `polymarket` CLI. Browse markets, place limit and market orders, manage positions, check rewards, and interact with conditional tokens — all from the terminal.

## Installation

### macOS / Linux (Homebrew)
```bash
brew tap Polymarket/polymarket-cli https://github.com/Polymarket/polymarket-cli
brew install polymarket
```

### Shell script
```bash
curl -sSL https://raw.githubusercontent.com/Polymarket/polymarket-cli/main/install.sh | sh
```

### Build from source (Rust)
```bash
git clone https://github.com/Polymarket/polymarket-cli
cd polymarket-cli
cargo install --path .
```

### Wallet Setup
```bash
# Guided first-time setup
polymarket setup

# Or manually:
polymarket wallet create
polymarket approve set  # needs MATIC for gas on Polygon
```

### Configuration

Private key is resolved in order:
1. CLI flag: `--private-key 0xabc...`
2. Environment variable: `POLYMARKET_PRIVATE_KEY=0xabc...`
3. Config file: `~/.config/polymarket/config.json`

Signature types: `proxy` (default), `eoa`, `gnosis-safe`. Override with `--signature-type`.

## Overview

You are an expert in using the `polymarket` CLI for prediction market trading. Your goal is to help users trade on Polymarket efficiently while emphasizing safety, position management, and risk awareness.

## How to Use This Skill

1. **Safety First**: Start with small positions. Polymarket trades are real money on Polygon mainnet.
2. **Verify Before Trading**: Always show the exact command and confirm with the user before executing trades.
3. **Check Prerequisites**: Confirm wallet is set up, approvals are granted, and sufficient USDC balance exists.
4. **Use JSON Output**: For scripting and automation, use `-o json` for machine-readable output.
5. **Understand Token IDs**: Each market outcome (YES/NO) has a unique token ID. Get it from market details or order book commands.

## When to Use This Skill

Use this skill when the user wants to:
- Browse or search prediction markets
- Place bets (limit orders, market orders)
- Check market prices, spreads, and order books
- View or manage open orders
- Check portfolio positions and P/L
- Cancel orders
- Redeem winnings from resolved markets
- Check liquidity rewards and earnings
- Monitor market activity and leaderboards
- Hedge positions across markets

**Common trigger phrases:**
- "What prediction markets are trending?"
- "Buy YES on Bitcoin above 100k"
- "Show me the order book"
- "What's the spread on this market?"
- "Cancel all my orders"
- "Check my positions"
- "How much have I earned in rewards?"
- "Place a limit order at 0.45"
- "Hedge my position"

**When NOT to use this skill:**
- User wants to trade stocks/ETFs/options (use Alpaca trading skill)
- User wants financial advice (provide tools, not recommendations)
- User wants to use the Polymarket web UI

## Core Commands

### Market Discovery (No wallet needed)

**List markets:**
```bash
polymarket markets list --limit 10
polymarket markets list --active true --order volume_num
polymarket markets list --closed false --limit 50 --offset 25
```

**Get market details:**
```bash
polymarket markets get 12345
polymarket markets get will-trump-win  # by slug
```

**Search markets:**
```bash
polymarket markets search "bitcoin" --limit 5
```

**List events (groups of related markets):**
```bash
polymarket events list --limit 10
polymarket events list --tag politics --active true
polymarket events get 500
```

**Browse tags and categories:**
```bash
polymarket tags list
polymarket tags get politics
polymarket tags related politics
```

**Sports markets:**
```bash
polymarket sports list
polymarket sports market-types
polymarket sports teams --league NFL --limit 32
```

### Order Book & Prices (No wallet needed)

**Get prices:**
```bash
polymarket clob price TOKEN_ID --side buy
polymarket clob midpoint TOKEN_ID
polymarket clob spread TOKEN_ID
```

**Batch price queries:**
```bash
polymarket clob batch-prices "TOKEN1,TOKEN2" --side buy
polymarket clob midpoints "TOKEN1,TOKEN2"
polymarket clob spreads "TOKEN1,TOKEN2"
```

**Order book depth:**
```bash
polymarket clob book TOKEN_ID
polymarket clob books "TOKEN1,TOKEN2"
```

**Price history:**
```bash
polymarket clob price-history TOKEN_ID --interval 1d --fidelity 30
# Intervals: 1m, 1h, 6h, 1d, 1w, max
```

**Market metadata:**
```bash
polymarket clob tick-size TOKEN_ID
polymarket clob fee-rate TOKEN_ID
polymarket clob neg-risk TOKEN_ID
polymarket clob last-trade TOKEN_ID
polymarket clob time
polymarket clob ok       # API health check
polymarket clob geoblock # check if geo-restricted
```

### Trading (Requires wallet)

**Place a limit order:**
```bash
polymarket clob create-order \
  --token TOKEN_ID \
  --side buy --price 0.50 --size 10
```

**Place a market order:**
```bash
polymarket clob market-order \
  --token TOKEN_ID \
  --side buy --amount 5
```

**Place multiple orders at once:**
```bash
polymarket clob post-orders \
  --tokens "TOKEN1,TOKEN2" \
  --side buy \
  --prices "0.40,0.60" \
  --sizes "10,10"
```

**Order types**: `GTC` (default), `FOK`, `GTD`, `FAK`. Add `--post-only` for maker-only limit orders.

**Cancel orders:**
```bash
polymarket clob cancel ORDER_ID
polymarket clob cancel-orders "ORDER1,ORDER2"
polymarket clob cancel-market --market 0xCONDITION_ID
polymarket clob cancel-all
```

**View orders and trades:**
```bash
polymarket clob orders
polymarket clob orders --market 0xCONDITION_ID
polymarket clob order ORDER_ID
polymarket clob trades
```

**Check balances:**
```bash
polymarket clob balance --asset-type collateral
polymarket clob balance --asset-type conditional --token TOKEN_ID
polymarket clob update-balance --asset-type collateral
```

### Rewards & Earnings

```bash
polymarket clob rewards --date 2026-03-01
polymarket clob earnings --date 2026-03-01
polymarket clob earnings-markets --date 2026-03-01
polymarket clob reward-percentages
polymarket clob current-rewards
polymarket clob market-reward 0xCONDITION_ID

# Check if orders are scoring rewards
polymarket clob order-scoring ORDER_ID
polymarket clob orders-scoring "ORDER1,ORDER2"
```

### Portfolio & On-Chain Data (Public, no wallet needed)

```bash
polymarket data positions 0xWALLET_ADDRESS
polymarket data closed-positions 0xWALLET_ADDRESS
polymarket data value 0xWALLET_ADDRESS
polymarket data traded 0xWALLET_ADDRESS
polymarket data trades 0xWALLET_ADDRESS --limit 50
polymarket data activity 0xWALLET_ADDRESS

# Market analytics
polymarket data holders 0xCONDITION_ID
polymarket data open-interest 0xCONDITION_ID
polymarket data volume 12345  # event ID

# Leaderboards
polymarket data leaderboard --period month --order-by pnl --limit 10
```

### Conditional Token Operations (On-chain, needs MATIC)

```bash
# Split $10 USDC into YES/NO tokens
polymarket ctf split --condition 0xCONDITION_ID --amount 10

# Merge YES/NO tokens back to USDC
polymarket ctf merge --condition 0xCONDITION_ID --amount 10

# Redeem winning tokens after resolution
polymarket ctf redeem --condition 0xCONDITION_ID

# Redeem neg-risk positions
polymarket ctf redeem-neg-risk --condition 0xCONDITION_ID --amounts "10,5"

# Calculate IDs (read-only, no wallet needed)
polymarket ctf condition-id --oracle 0xORACLE... --question 0xQUESTION... --outcomes 2
polymarket ctf collection-id --condition 0xCONDITION_ID --index-set 1
polymarket ctf position-id --collection 0xCOLLECTION...
```

### Wallet Management

```bash
polymarket wallet create
polymarket wallet create --force       # overwrite existing
polymarket wallet import 0xKEY...
polymarket wallet address
polymarket wallet show
polymarket wallet reset
```

### Contract Approvals

```bash
polymarket approve check              # check current approvals
polymarket approve set                # approve all contracts (6 txns, needs MATIC)
```

### API Key Management

```bash
polymarket clob api-keys           # list API keys
polymarket clob create-api-key     # create new API key
polymarket clob delete-api-key     # delete an API key
```

### Notifications & Account Status

```bash
polymarket clob account-status
polymarket clob notifications
polymarket clob delete-notifications "NOTIF1,NOTIF2"
```

### Bridge (Deposits)

```bash
polymarket bridge deposit 0xWALLET_ADDRESS
polymarket bridge supported-assets
polymarket bridge status 0xDEPOSIT_ADDRESS
```

### Interactive Shell

```bash
polymarket shell
# Launches an interactive REPL with command history.
# All commands work without the `polymarket` prefix:
#   polymarket> markets list --limit 3
#   polymarket> clob book TOKEN_ID
#   polymarket> exit
```

### Utility Commands

```bash
polymarket status     # API health check
polymarket setup      # Guided first-time setup wizard
polymarket upgrade    # Update CLI to latest version
polymarket --version
polymarket --help
```

## Output Formats

All commands support `--output table` (default) and `--output json` (or `-o json`).

```bash
# Human-readable
polymarket markets list --limit 5

# Machine-readable for scripts
polymarket -o json markets list --limit 5
polymarket -o json clob midpoint TOKEN_ID | jq '.mid'
```

## Common Workflows

### Research a market before trading
```bash
# 1. Search for markets
polymarket markets search "bitcoin" --limit 5

# 2. Get market details (note the token IDs for YES/NO outcomes)
polymarket markets get bitcoin-above-100k

# 3. Check the order book
polymarket clob book TOKEN_ID

# 4. Check price history
polymarket clob price-history TOKEN_ID --interval 1d

# 5. Check spread and midpoint
polymarket clob spread TOKEN_ID
polymarket clob midpoint TOKEN_ID
```

### Place a limit order and monitor
```bash
# 1. Check balance
polymarket clob balance --asset-type collateral

# 2. Place limit order (maker-only for zero fees + rebates)
polymarket clob create-order --token TOKEN_ID --side buy --price 0.45 --size 20 --post-only

# 3. Check if order is scoring rewards
polymarket clob orders
polymarket clob order-scoring ORDER_ID

# 4. Cancel if needed
polymarket clob cancel ORDER_ID
```

### Two-sided market making (reward farming)
```bash
# 1. Find a low-competition market
polymarket markets search "niche topic"

# 2. Get YES and NO token IDs from market details
polymarket -o json markets get SLUG | jq '.tokens'

# 3. Place buy orders on both sides
polymarket clob create-order --token YES_TOKEN_ID --side buy --price 0.48 --size 10 --post-only
polymarket clob create-order --token NO_TOKEN_ID --side buy --price 0.48 --size 10 --post-only

# 4. Monitor rewards
polymarket clob current-rewards
polymarket clob order-scoring ORDER_ID
```

### Hedge a position
```bash
# If holding YES, buy NO to reduce risk
# Total cost YES + NO should be <= $1.00 for guaranteed profit

# 1. Check current positions
polymarket data positions 0xYOUR_ADDRESS

# 2. Check NO token price
polymarket clob price NO_TOKEN_ID --side buy

# 3. Buy hedge
polymarket clob create-order --token NO_TOKEN_ID --side buy --price 0.48 --size 10
```

### Redeem winnings after market resolves
```bash
# 1. Check for resolved positions
polymarket data closed-positions 0xYOUR_ADDRESS

# 2. Redeem
polymarket ctf redeem --condition 0xCONDITION_ID
```

### Scripting with JSON output
```bash
# Get all market questions
polymarket -o json markets list --limit 100 | jq '.[].question'

# Check balance programmatically
polymarket -o json clob balance --asset-type collateral | jq '.balance'

# Error handling
if ! result=$(polymarket -o json clob balance --asset-type collateral 2>/dev/null); then
  echo "Failed to fetch balance"
fi
```

## Best Practices

### Safety & Risk
1. **Start small** — Polymarket trades are real money on Polygon mainnet
2. **Use `--post-only`** — Maker orders have zero fees and earn rebates
3. **Check fee rates** — Use `polymarket clob fee-rate TOKEN_ID` before trading
4. **Verify token IDs** — Each YES/NO outcome has a different token ID
5. **Keep MATIC for gas** — On-chain operations (approve, split, merge, redeem) need MATIC
6. **Monitor positions** — Use `polymarket data positions` regularly

### Order Management
1. **Prefer limit orders** — Better price control, zero maker fees
2. **Use `--post-only`** — Ensures your order is a maker order (no taker fees)
3. **Batch when possible** — Use `clob post-orders` to place multiple orders at once
4. **Cancel stale orders** — Orders sitting far from mid are not earning rewards
5. **Check order scoring** — Use `clob order-scoring` to verify reward eligibility

### Market Making
1. **Two-sided orders earn ~3x rewards** — Place on both YES and NO
2. **Stay close to midpoint** — Rewards decay quadratically with distance from mid
3. **Low-competition markets** — Larger share of the reward pool
4. **Monitor spread** — Tighter spreads earn more rewards but increase fill risk
5. **Rebalance regularly** — Cancel and replace orders as midpoint moves

## Command Reference

| Task | Command |
|------|---------|
| List markets | `polymarket markets list --limit 10` |
| Search markets | `polymarket markets search "query"` |
| Get market details | `polymarket markets get SLUG_OR_ID` |
| List events | `polymarket events list --limit 10` |
| Check price | `polymarket clob price TOKEN_ID --side buy` |
| Check midpoint | `polymarket clob midpoint TOKEN_ID` |
| Check spread | `polymarket clob spread TOKEN_ID` |
| View order book | `polymarket clob book TOKEN_ID` |
| Price history | `polymarket clob price-history TOKEN_ID --interval 1d` |
| Place limit order | `polymarket clob create-order --token TOKEN_ID --side buy --price 0.50 --size 10` |
| Place market order | `polymarket clob market-order --token TOKEN_ID --side buy --amount 5` |
| Batch orders | `polymarket clob post-orders --tokens "T1,T2" --side buy --prices "0.4,0.6" --sizes "10,10"` |
| View orders | `polymarket clob orders` |
| Cancel order | `polymarket clob cancel ORDER_ID` |
| Cancel all | `polymarket clob cancel-all` |
| Check balance | `polymarket clob balance --asset-type collateral` |
| View positions | `polymarket data positions 0xADDRESS` |
| Check rewards | `polymarket clob current-rewards` |
| Check earnings | `polymarket clob earnings --date 2026-03-01` |
| Split USDC to tokens | `polymarket ctf split --condition 0xCOND --amount 10` |
| Merge tokens to USDC | `polymarket ctf merge --condition 0xCOND --amount 10` |
| Redeem winnings | `polymarket ctf redeem --condition 0xCOND` |
| Wallet info | `polymarket wallet show` |
| Approve contracts | `polymarket approve set` |
| API health | `polymarket clob ok` |
| Geo-restriction check | `polymarket clob geoblock` |
| Account status | `polymarket clob account-status` |
| List API keys | `polymarket clob api-keys` |
| CTF condition ID | `polymarket ctf condition-id --oracle 0xORA --question 0xQ --outcomes 2` |
| Interactive shell | `polymarket shell` |
| Update CLI | `polymarket upgrade` |
| Guided setup | `polymarket setup` |

## Important Notes

- **Token IDs** are long numeric strings (e.g., `48331043336612883...`). Get them from market details or order book.
- **Condition IDs** are hex strings (e.g., `0xABC...`). Used for on-chain operations and market-level queries.
- **USDC** is the settlement currency. All amounts are in USDC.
- **MATIC** is needed for gas on Polygon for on-chain operations (approve, split, merge, redeem).
- **Maker orders** (limit orders with `--post-only`) have zero fees and earn daily rebates.
- **Taker orders** pay fees up to ~1.56% at 50/50 odds.
- **Rewards** are distributed daily at midnight UTC. Two-sided orders earn ~3x single-sided.

## Troubleshooting

### Wallet not configured
```bash
# Run guided setup
polymarket setup
# Or create wallet manually
polymarket wallet create
```

### Approvals not set
```bash
polymarket approve check  # see what's missing
polymarket approve set    # approve all (needs MATIC)
```

### Insufficient balance
```bash
polymarket clob balance --asset-type collateral
# Fund via bridge or direct USDC transfer to your Polygon wallet
polymarket bridge deposit 0xYOUR_ADDRESS
```

### Order rejected
- Check balance: `polymarket clob balance --asset-type collateral`
- Verify token ID is correct
- Check fee rate: `polymarket clob fee-rate TOKEN_ID`
- Ensure approvals are set: `polymarket approve check`

### Command not found
```bash
# Reinstall
brew tap Polymarket/polymarket-cli https://github.com/Polymarket/polymarket-cli
brew install polymarket
# Or: cargo install --path . (from source)
```

## Additional Resources

- **Polymarket CLI**: https://github.com/Polymarket/polymarket-cli
- **Polymarket Docs**: https://docs.polymarket.com/
- **CLOB API Docs**: https://docs.polymarket.com/developers/
- **Liquidity Rewards**: https://docs.polymarket.com/developers/market-makers/liquidity-rewards
- **Maker Rebates**: https://docs.polymarket.com/developers/market-makers/maker-rebates-program
