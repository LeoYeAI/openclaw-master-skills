---
name: kalshi-trading
description: Trade prediction markets on Kalshi using the kalshi-cli command-line tool. Use when the user wants to trade event contracts, browse prediction markets, place orders, manage positions, stream live prices, or view candlestick charts. Also use when they mention "prediction market," "event contract," "kalshi," "YES/NO," "order book," "limit order," "market order," "hedge," "arbitrage," or "liquidity rewards."
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins: ["kalshi-cli"]
    homepage: "https://github.com/6missedcalls/kalshi-cli"
    repository: "https://github.com/lacymorrow/openclaw-kalshi-trading-skill"
    install:
      - id: "brew-kalshi-cli"
        kind: "brew"
        formula: "kalshi-cli"
        bins: ["kalshi-cli"]
        label: "Install Kalshi CLI (Homebrew)"
---

# Kalshi Trading Skill

Trade CFTC-regulated prediction markets on Kalshi through the `kalshi-cli` command-line tool. Browse markets, place limit and market orders, manage positions, stream real-time prices, and view ASCII candlestick charts — all from the terminal.

Kalshi is fully legal in the US. No crypto wallets, no blockchain, no gas fees — everything settles in USD.

## Installation

### macOS / Linux (Homebrew)
```bash
brew install 6missedcalls/tap/kalshi-cli
```

### Go Install (requires Go 1.25+)
```bash
go install github.com/6missedcalls/kalshi-cli/cmd/kalshi-cli@latest
```

### Build from Source
```bash
git clone https://github.com/6missedcalls/kalshi-cli.git
cd kalshi-cli
go build -o kalshi-cli ./cmd/kalshi-cli
```

## Authentication

### Interactive Login (Recommended first time)
```bash
kalshi-cli auth login
```

Follow the prompts to:
1. Copy the displayed public key
2. Add it to your Kalshi account at https://kalshi.com/account/api-keys
3. Enter the API Key ID when prompted

Credentials are stored securely in your OS keyring (macOS Keychain, GNOME Keyring, or Windows Credential Manager).

### Non-Interactive Login (Bots / CI)
```bash
# Via flags
kalshi-cli auth login --api-key-id YOUR_KEY_ID --private-key-file /path/to/key.pem

# Via PEM content
kalshi-cli auth login --api-key-id YOUR_KEY_ID --private-key "$(cat /path/to/key.pem)"

# Via environment variables
export KALSHI_API_KEY_ID=your-key-id
export KALSHI_PRIVATE_KEY="$(cat /path/to/key.pem)"
kalshi-cli auth login
```

### Config File
Add to `~/.kalshi/config.yaml`:
```yaml
api_key_id: your-key-id
private_key_path: /path/to/key.pem
```

Credentials are resolved in order: config file, environment variables, OS keyring.

### Demo vs Production

| | Demo (default) | Production |
|--|------|-----------|
| Flag | (default) | `--prod` |
| API | `demo-api.kalshi.co` | `api.elections.kalshi.com` |
| Money | Fake/test | Real USD |

**The CLI defaults to demo mode.** You must pass `--prod` to trade with real money. This is a safety feature.

## Overview

You are an expert in using `kalshi-cli` for prediction market trading on Kalshi. Your goal is to help users trade event contracts efficiently while emphasizing safety and risk awareness.

## How to Use This Skill

1. **Safety First**: The CLI defaults to demo mode. Only use `--prod` when the user explicitly wants real trading.
2. **Verify Before Trading**: Always show the exact command and confirm with the user before executing trades.
3. **Check Prerequisites**: Confirm auth is set up (`auth status`), exchange is active (`exchange status`), and sufficient balance exists.
4. **Use JSON Output**: For scripting and automation, use `--json` for machine-readable output.
5. **Understand Tickers**: Markets use structured tickers like `KXBTC-26FEB12-B97000`. Events group related markets.

## When to Use This Skill

Use this skill when the user wants to:
- Browse or search prediction markets (politics, crypto, sports, economics, weather)
- Place bets (limit orders, market orders) on event contracts
- Check market prices, spreads, and order books
- View ASCII candlestick charts
- Stream live price updates via WebSocket
- View or manage open orders
- Check portfolio positions and P/L
- Cancel or amend orders
- Monitor trade fills and settlements
- Use batch orders for market-making strategies

**Common trigger phrases:**
- "What prediction markets are open on Kalshi?"
- "Buy YES on Bitcoin above 100k"
- "Show me the order book"
- "Stream live prices for this market"
- "Show me a candlestick chart"
- "Cancel all my orders"
- "Check my positions"
- "Place a limit order at 50 cents"
- "What's my balance?"

**When NOT to use this skill:**
- User wants to trade stocks/ETFs/options (use Alpaca trading skill)
- User wants to trade on Polymarket (use Polymarket trading skill)
- User wants financial advice (provide tools, not recommendations)

## Key Concepts

### Tickers
Markets use structured tickers: `KXBTC-26FEB12-B97000`
- `KXBTC` = series (Bitcoin)
- `26FEB12` = date (Feb 12, 2026)
- `B97000` = strike ($97,000)

### Events vs Markets
An **event** groups related markets. For example, "Bitcoin price on Feb 12" is an event containing markets at different strike prices ($90K, $95K, $100K, etc.).

### Contracts
Kalshi trades **event contracts** priced 1-99 cents, settling to $1 or $0. All values are in **cents**.

### Subaccounts
Up to 32 subaccounts per user for multi-strategy isolation.

### Order Groups
Cap total fills across multiple orders — useful for market-making where you don't want both sides filled.

## Global Flags

Every command accepts these flags:

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--json` | | `false` | Output as JSON for scripts |
| `--plain` | | `false` | Plain text for piping |
| `--yes` | `-y` | `false` | Skip all confirmation prompts |
| `--prod` | | `false` | Use production API (real money) |
| `--verbose` | `-v` | `false` | Debug output |
| `--config` | | `~/.kalshi/config.yaml` | Config file path |

## Core Commands

### Authentication

```bash
kalshi-cli auth login                        # interactive login
kalshi-cli auth login --api-key-id ID --private-key-file /path/to/key.pem  # non-interactive
kalshi-cli auth logout                       # remove stored credentials
kalshi-cli auth status                       # check auth status + environment
kalshi-cli auth keys list                    # list API keys
kalshi-cli auth keys create --name "my-bot"  # create new API key
kalshi-cli auth keys delete KEY_ID           # delete API key
```

### Market Discovery

**List markets:**
```bash
kalshi-cli markets list --status open --limit 20
kalshi-cli markets list --series KXBTC --json
```

Flags: `--status` (open/closed/settled), `--series` (filter by series ticker), `--limit` (default 50).

**Get market details:**
```bash
kalshi-cli markets get KXBTC-26FEB12-B97000
```

**View order book:**
```bash
kalshi-cli markets orderbook KXBTC-26FEB12-B97000
kalshi-cli markets orderbook KXBTC-26FEB12-B97000 --json
```

**View recent trades:**
```bash
kalshi-cli markets trades KXBTC-26FEB12-B97000 --limit 20
```

**View candlestick chart:**
```bash
kalshi-cli markets candlesticks KXBTC-26FEB12-B97000 --series KXBTC
kalshi-cli markets candlesticks KXBTC-26FEB12-B97000 --series KXBTC --period 1d
# Periods: 1m, 1h, 1d
```

**Browse series (categories of markets):**
```bash
kalshi-cli markets series list --category Economics
kalshi-cli markets series list --category Crypto
kalshi-cli markets series list --category Politics
kalshi-cli markets series get KXBTC
```

### Events

**List events:**
```bash
kalshi-cli events list --limit 20
kalshi-cli events list --status active
```

Flags: `--status` (active/closed/settled), `--limit`, `--cursor`.

**Get event details:**
```bash
kalshi-cli events get KXBTC-26FEB12
```

**Event candlestick chart:**
```bash
kalshi-cli events candlesticks KXINXU-26FEB11H1600 --period 1h \
  --start 2026-02-10T00:00:00Z --end 2026-02-11T23:00:00Z
```

**Multivariate events:**
```bash
kalshi-cli events multivariate list --limit 10
kalshi-cli events multivariate get TICKER
```

### Trading

**Place a limit order:**
```bash
kalshi-cli orders create --market KXBTC-26FEB12-B97000 --side yes --qty 10 --price 50
```

**Place a market order:**
```bash
kalshi-cli orders create --market KXBTC-26FEB12-B97000 --side yes --qty 10 --type market
```

**Sell contracts:**
```bash
kalshi-cli orders create --market KXBTC-26FEB12-B97000 --side no --qty 5 --price 30 --action sell
```

**Skip confirmation (for bots):**
```bash
kalshi-cli orders create --market KXBTC-26FEB12-B97000 --side yes --qty 10 --price 50 --yes --json
```

**Production trading (real money):**
```bash
kalshi-cli --prod orders create --market KXBTC-26FEB12-B97000 --side yes --qty 10 --price 50
```

Order flags:

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--market` | Yes | | Market ticker |
| `--side` | Yes | | `yes` or `no` |
| `--qty` | Yes | | Number of contracts |
| `--price` | Yes (limit) | | Price in cents (1-99) |
| `--action` | No | `buy` | `buy` or `sell` |
| `--type` | No | `limit` | `limit` or `market` |

**Amend an order:**
```bash
kalshi-cli orders amend ORDER_ID --price 55
kalshi-cli orders amend ORDER_ID --qty 20
kalshi-cli orders amend ORDER_ID --price 55 --qty 20
```

**Cancel orders:**
```bash
kalshi-cli orders cancel ORDER_ID
kalshi-cli orders cancel-all
kalshi-cli orders cancel-all --market KXBTC-26FEB12-B97000
```

**List and inspect orders:**
```bash
kalshi-cli orders list --status resting
kalshi-cli orders list --market KXBTC-26FEB12-B97000 --json
kalshi-cli orders get ORDER_ID
kalshi-cli orders queue ORDER_ID  # check queue position
```

**Batch create orders from JSON file:**
```bash
kalshi-cli orders batch-create --file orders.json
```

The JSON file format:
```json
[
  { "ticker": "MARKET1", "side": "yes", "action": "buy", "type": "limit", "count": 10, "yes_price": 50 },
  { "ticker": "MARKET2", "side": "no", "action": "buy", "type": "limit", "count": 5, "no_price": 30 }
]
```

### Portfolio

**Check balance:**
```bash
kalshi-cli portfolio balance
kalshi-cli portfolio balance --json
```

All values are in **cents**. Example JSON:
```json
{ "available_balance": 10000, "portfolio_value": 5000, "total_balance": 15000 }
```

**View positions:**
```bash
kalshi-cli portfolio positions
kalshi-cli portfolio positions --market KXBTC-26FEB12-B97000
```

**View trade fills:**
```bash
kalshi-cli portfolio fills --limit 50
```

**View settlements (resolved market payouts):**
```bash
kalshi-cli portfolio settlements --limit 20
```

**Subaccount management:**
```bash
kalshi-cli portfolio subaccounts list
kalshi-cli portfolio subaccounts create
kalshi-cli portfolio subaccounts transfer --from 1 --to 2 --amount 50000  # $500 in cents
```

### Order Groups

Order groups cap total fills across multiple orders — useful for market-making. Alias: `og`.

```bash
kalshi-cli order-groups create --limit 100          # max 100 contracts across group
kalshi-cli order-groups list
kalshi-cli og list --status active                  # alias
kalshi-cli order-groups get GROUP_ID
kalshi-cli order-groups update-limit GROUP_ID --limit 200
kalshi-cli order-groups reset GROUP_ID              # reset filled count
kalshi-cli order-groups trigger GROUP_ID             # execute orders
kalshi-cli order-groups delete GROUP_ID              # cancels all orders in group
```

### RFQ (Request for Quotes / Block Trading)

```bash
kalshi-cli rfq create --market KXBTC-26FEB12-B97000 --qty 1000
kalshi-cli rfq list --status open
kalshi-cli rfq get RFQ_ID
kalshi-cli rfq delete RFQ_ID
```

### Quotes (Respond to RFQs)

```bash
kalshi-cli quotes list --rfq-id RFQ_ID
kalshi-cli quotes create --rfq RFQ_ID --price 65
kalshi-cli quotes accept QUOTE_ID
kalshi-cli quotes confirm QUOTE_ID
```

### Real-Time Streaming (WebSocket)

All watch commands require auth. Press `Ctrl+C` to stop. Auto-reconnects with exponential backoff.

```bash
kalshi-cli watch ticker KXBTC-26FEB12-B97000       # live price updates
kalshi-cli watch orderbook KXBTC-26FEB12-B97000     # orderbook deltas
kalshi-cli watch trades                              # all public trades
kalshi-cli watch trades --market KXBTC-26FEB12-B97000  # trades for one market
kalshi-cli watch orders                              # your order status changes
kalshi-cli watch fills                               # your fill notifications
kalshi-cli watch positions                           # your position changes

# JSON output for programmatic consumption
kalshi-cli watch ticker KXBTC-26FEB12-B97000 --json
```

### Exchange Info

```bash
kalshi-cli exchange status         # exchange status, trading active?
kalshi-cli exchange schedule       # trading schedule
kalshi-cli exchange announcements  # latest announcements
```

### Configuration

```bash
kalshi-cli config show                      # all settings
kalshi-cli config get output.format         # get a setting
kalshi-cli config set output.format json    # change default output
kalshi-cli config set defaults.limit 100    # change default list limit
```

Config file: `~/.kalshi/config.yaml`

### Utility Commands

```bash
kalshi-cli version                 # print version
kalshi-cli completion bash         # shell autocompletion
kalshi-cli completion zsh
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `KALSHI_API_KEY_ID` | API Key ID |
| `KALSHI_PRIVATE_KEY` | Private key PEM content |
| `KALSHI_PRIVATE_KEY_FILE` | Path to private key PEM file |
| `KALSHI_API_PRODUCTION` | `true` for production |
| `KALSHI_API_TIMEOUT` | HTTP timeout (e.g., `60s`) |
| `KALSHI_OUTPUT_FORMAT` | Default output format |

## Output Formats

All commands support `--json`, `--plain`, and default table output.

```bash
# Human-readable table (default)
kalshi-cli markets list --limit 5

# Machine-readable JSON
kalshi-cli --json markets list --limit 5

# Plain text for piping
kalshi-cli --plain portfolio balance
```

Exit codes: 0=success, 1=general error, 2=auth error, 3=validation error, 4=API error, 5=network error.

## Common Workflows

### Browse markets and research
```bash
# 1. Browse by category
kalshi-cli markets series list --category Crypto

# 2. List open markets in a series
kalshi-cli markets list --series KXBTC --status open

# 3. Get market details
kalshi-cli markets get KXBTC-26FEB12-B97000

# 4. Check the order book
kalshi-cli markets orderbook KXBTC-26FEB12-B97000

# 5. View candlestick chart
kalshi-cli markets candlesticks KXBTC-26FEB12-B97000 --series KXBTC --period 1h

# 6. View recent trades
kalshi-cli markets trades KXBTC-26FEB12-B97000 --limit 10
```

### Place a limit order and monitor
```bash
# 1. Check balance
kalshi-cli portfolio balance

# 2. Place limit order (demo mode)
kalshi-cli orders create --market KXBTC-26FEB12-B97000 --side yes --qty 10 --price 50

# 3. Check order status
kalshi-cli orders list --status resting

# 4. Check queue position
kalshi-cli orders queue ORDER_ID

# 5. Amend if needed
kalshi-cli orders amend ORDER_ID --price 52

# 6. Or cancel
kalshi-cli orders cancel ORDER_ID
```

### Market making with order groups
```bash
# 1. Create an order group (cap total fills)
kalshi-cli order-groups create --limit 50

# 2. Place orders on both sides
kalshi-cli orders create --market TICKER --side yes --action buy --qty 10 --price 45 --yes
kalshi-cli orders create --market TICKER --side yes --action sell --qty 10 --price 55 --yes

# 3. Monitor fills
kalshi-cli watch fills
```

### Bot automation (market-making script)
```bash
#!/bin/bash
MARKET="KXBTC-26FEB12-B97000"
BOOK=$(kalshi-cli markets orderbook $MARKET --json)
BEST_BID=$(echo $BOOK | jq '.yes_bids[0].price // 0')
BEST_ASK=$(echo $BOOK | jq '.yes_asks[0].price // 100')

kalshi-cli orders create --market $MARKET --side yes --action buy  --qty 10 --price $((BEST_BID + 1)) --yes --json
kalshi-cli orders create --market $MARKET --side yes --action sell --qty 10 --price $((BEST_ASK - 1)) --yes --json
```

### Stream live prices
```bash
# Terminal display
kalshi-cli watch ticker KXBTC-26FEB12-B97000

# Pipe JSON to a script
kalshi-cli watch ticker KXBTC-26FEB12-B97000 --json | while read line; do
  PRICE=$(echo $line | jq '.yes_price')
  echo "Current price: $PRICE"
done
```

### Portfolio review
```bash
kalshi-cli portfolio balance --json | jq '{available: .available_balance, total: .total_balance}'
kalshi-cli portfolio positions --json | jq '.[] | {ticker, position, pnl}'
kalshi-cli portfolio fills --limit 10
kalshi-cli portfolio settlements --limit 10
```

### Go live (production)
```bash
# Verify you're on demo first
kalshi-cli auth status

# Switch to production for a single command
kalshi-cli --prod orders create --market KXBTC-26FEB12-B97000 --side yes --qty 10 --price 50

# Or set globally
export KALSHI_API_PRODUCTION=true
```

## Best Practices

### Safety
1. **Demo first** — the CLI defaults to demo mode. Test everything before going live.
2. **Confirm before `--prod`** — always verify with `kalshi-cli auth status` before trading real money.
3. **Use `--yes` carefully** — it skips all confirmations. Only use in tested bot scripts.
4. **Set position limits** — use order groups to cap maximum exposure.
5. **Monitor positions** — use `kalshi-cli watch positions` for real-time tracking.

### Order Management
1. **Prefer limit orders** — better price control, lower fees.
2. **Use order groups for market-making** — prevents both sides from filling simultaneously.
3. **Amend instead of cancel/replace** — native `orders amend` is atomic and faster.
4. **Batch when possible** — use `orders batch-create` with a JSON file for multiple orders.
5. **Check queue position** — use `orders queue` to see where your resting order sits.

### Bot Development
1. **Use `--json --yes`** — machine-parseable output, no interactive prompts.
2. **Check exit codes** — 0=success, 2=auth error, 4=API error, 5=network error.
3. **Handle rate limits** — Basic: 10 writes/sec, 20 reads/sec. Apply for higher tiers if needed.
4. **Use WebSocket for live data** — `watch ticker` is more efficient than polling.
5. **Store credentials securely** — use env vars or keyring, never hardcode.

## Command Reference

| Task | Command |
|------|---------|
| **Auth** |
| Login | `kalshi-cli auth login` |
| Check status | `kalshi-cli auth status` |
| List API keys | `kalshi-cli auth keys list` |
| **Markets** |
| List markets | `kalshi-cli markets list --status open --limit 20` |
| Get market | `kalshi-cli markets get TICKER` |
| Order book | `kalshi-cli markets orderbook TICKER` |
| Recent trades | `kalshi-cli markets trades TICKER --limit 20` |
| Candlestick chart | `kalshi-cli markets candlesticks TICKER --series SERIES --period 1h` |
| Browse series | `kalshi-cli markets series list --category Crypto` |
| **Events** |
| List events | `kalshi-cli events list --status active --limit 20` |
| Get event | `kalshi-cli events get EVENT_TICKER` |
| Event chart | `kalshi-cli events candlesticks EVENT_TICKER --period 1h` |
| **Trading** |
| Limit order (buy YES) | `kalshi-cli orders create --market TICKER --side yes --qty 10 --price 50` |
| Market order | `kalshi-cli orders create --market TICKER --side yes --qty 10 --type market` |
| Sell contracts | `kalshi-cli orders create --market TICKER --side no --qty 5 --price 30 --action sell` |
| Amend order | `kalshi-cli orders amend ORDER_ID --price 55` |
| Cancel order | `kalshi-cli orders cancel ORDER_ID` |
| Cancel all | `kalshi-cli orders cancel-all` |
| Batch create | `kalshi-cli orders batch-create --file orders.json` |
| List resting orders | `kalshi-cli orders list --status resting` |
| Queue position | `kalshi-cli orders queue ORDER_ID` |
| **Portfolio** |
| Balance | `kalshi-cli portfolio balance` |
| Positions | `kalshi-cli portfolio positions` |
| Fills | `kalshi-cli portfolio fills --limit 50` |
| Settlements | `kalshi-cli portfolio settlements` |
| **Subaccounts** |
| List | `kalshi-cli portfolio subaccounts list` |
| Create | `kalshi-cli portfolio subaccounts create` |
| Transfer | `kalshi-cli portfolio subaccounts transfer --from 1 --to 2 --amount 50000` |
| **Order Groups** |
| Create group | `kalshi-cli order-groups create --limit 100` |
| List groups | `kalshi-cli og list` |
| Update limit | `kalshi-cli order-groups update-limit GROUP_ID --limit 200` |
| Delete group | `kalshi-cli order-groups delete GROUP_ID` |
| **Block Trading** |
| Create RFQ | `kalshi-cli rfq create --market TICKER --qty 1000` |
| List RFQs | `kalshi-cli rfq list` |
| Create quote | `kalshi-cli quotes create --rfq RFQ_ID --price 65` |
| Accept quote | `kalshi-cli quotes accept QUOTE_ID` |
| **Streaming** |
| Live prices | `kalshi-cli watch ticker TICKER` |
| Orderbook deltas | `kalshi-cli watch orderbook TICKER` |
| Public trades | `kalshi-cli watch trades` |
| Your orders | `kalshi-cli watch orders` |
| Your fills | `kalshi-cli watch fills` |
| Your positions | `kalshi-cli watch positions` |
| **Exchange** |
| Exchange status | `kalshi-cli exchange status` |
| Schedule | `kalshi-cli exchange schedule` |
| Announcements | `kalshi-cli exchange announcements` |
| **Config** |
| Show config | `kalshi-cli config show` |
| Set value | `kalshi-cli config set output.format json` |

## Important Notes

- **All values in cents** — prices are 1-99, balances are in cents ($100 = 10000 cents).
- **Demo by default** — use `--prod` flag for real trading.
- **Tickers are structured** — `KXBTC-26FEB12-B97000` = series + date + strike.
- **Events group markets** — browse events to find related markets at different strike levels.
- **Order groups** cap total fills — essential for market-making strategies.
- **Rate limits** — Basic: 10 writes/sec, 20 reads/sec. Apply for higher tiers via Kalshi.
- **RSA-PSS auth** — private key never leaves your machine. No passwords, no sessions to manage.
- **USD settlement** — no crypto, no wallets, no gas fees.
- **CFTC-regulated** — fully legal in the United States.

## Fees

| Type | Formula | Max at 50/50 |
|------|---------|--------------|
| Taker | `roundup(0.07 * C * P * (1-P))` | 1.75c/contract |
| Maker | `roundup(0.0175 * C * P * (1-P))` | ~0.44c/contract |
| S&P/Nasdaq markets | Half the normal rate | ~0.88c taker |

Lower fees for orders near the extremes (close to 0 or 100). No settlement or withdrawal fees (ACH).

## Troubleshooting

### Not authenticated
```bash
kalshi-cli auth status  # check status
kalshi-cli auth login   # re-authenticate
```

### Wrong environment (demo vs prod)
```bash
kalshi-cli auth status  # shows current environment
# Use --prod for production, omit for demo
```

### Order rejected
- Check balance: `kalshi-cli portfolio balance`
- Verify market is open: `kalshi-cli markets get TICKER`
- Check exchange status: `kalshi-cli exchange status`
- Price must be 1-99 cents

### Rate limited
- Basic tier: 10 writes/sec, 20 reads/sec
- Apply for Advanced/Premier tier at Kalshi for higher limits
- Use batch operations where possible

## Additional Resources

- **kalshi-cli**: https://github.com/6missedcalls/kalshi-cli
- **Kalshi API Docs**: https://docs.kalshi.com/welcome
- **Kalshi Fee Schedule**: https://kalshi.com/fee-schedule
- **Liquidity Incentive Program**: https://help.kalshi.com/incentive-programs/liquidity-incentive-program
- **Kalshi Python SDK**: https://pypi.org/project/kalshi-python/
- **Kalshi TypeScript SDK**: https://www.npmjs.com/package/kalshi-typescript
