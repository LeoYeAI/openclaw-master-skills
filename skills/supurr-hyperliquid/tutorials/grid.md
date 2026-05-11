# Grid Bot Tutorial

Step-by-step guide to deploying a grid trading bot on Hyperliquid.

---

## What is Grid Trading?

A grid bot places a series of buy and sell orders at fixed price intervals (the "grid"), profiting from price oscillations within a range. It earns on every bounce between grid levels — the more the price oscillates, the more it earns.

**When to use Grid:**

- You expect the price to range-bound (move sideways within a band)
- You want passive, automated trading without directional bias
- You want to profit from volatility, not direction

**When NOT to use Grid:**

- Strong trending markets (price breaks out of your grid range)
- Very low volatility (few grid fills = low returns)

---

## 1️⃣ Setup Credentials

```bash
# First time only — saves to ~/.supurr/credentials.json
supurr init --address 0xYOUR_WALLET --api-wallet 0xYOUR_API_KEY
```

> Your API wallet must be registered on Hyperliquid first. Go to Hyperliquid → Settings → API Wallets.

---

## 2️⃣ Choose Your Market

Grid supports 4 market types. Pick based on what you want to trade:

| Market Type     | When to Use                                 | Example                                 |
| --------------- | ------------------------------------------- | --------------------------------------- |
| **Native Perp** | Most liquid markets (BTC, ETH, SOL)         | `--asset BTC`                           |
| **Spot**        | You want spot exposure, no liquidation risk | `--asset HYPE --type spot --quote USDC` |
| **HIP-3**       | Sub-DEX perps (stocks, alt tokens)          | `--asset BTC --type hip3 --dex hyna`    |

---

## 3️⃣ Generate Config

Pick your grid parameters:

| Parameter                       | How to Think About It                                                                                      |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `--start-price` / `--end-price` | The range you expect price to stay in. Check recent support/resistance.                                    |
| `--levels`                      | More levels = more orders = smaller profit per fill but more frequent fills. 10-30 is typical.             |
| `--investment`                  | Total USDC to allocate. Split across all grid levels.                                                      |
| `--leverage`                    | Higher = more capital efficient but higher liquidation risk. Start with 2-5x.                              |
| `--mode`                        | `long` (buy-heavy), `short` (sell-heavy), `neutral` (balanced). Use `long` if bullish, `short` if bearish. |

**Example — BTC range trading between $90k-$100k:**

```bash
supurr new grid \
  --asset BTC \
  --start-price 90000 \
  --end-price 100000 \
  --levels 20 \
  --investment 500 \
  --leverage 5 \
  --mode neutral \
  --output btc-grid.json
```

---

## 4️⃣ Backtest (Recommended)

Before deploying real money, test against historical data:

```bash
supurr backtest -c btc-grid.json -s 2026-01-28 -e 2026-02-01
```

**What to look for in results:**

- **Total PnL** — is the strategy profitable in this range?
- **Number of fills** — more fills = grid is active, few fills = range might be wrong
- **Max drawdown** — can you stomach this risk?

Adjust parameters and re-run until you're satisfied.

---

## 5️⃣ Deploy

```bash
# Deploy from main wallet
supurr deploy -c btc-grid.json

# Or from a subaccount (recommended for isolation)
supurr deploy -c btc-grid.json -s 0xYOUR_SUBACCOUNT

# Or from a vault
supurr deploy -c btc-grid.json -v 0xYOUR_VAULT
```

The CLI will output a Bot ID and Pod Name on success.

---

## 6️⃣ Monitor & Manage

```bash
# Live monitoring (refreshes every 2s)
supurr monitor --watch

# Stop when done
supurr stop --id <bot_id>
```

---

## Tips

- **Tighter range + more levels** = more fills but risk of breakout
- **Wider range + fewer levels** = safer but less frequent fills
- **Use subaccounts** to isolate grid bot funds from your main trading
- **Watch funding rates** on perps — if you're net long/short, funding can eat into profits
- Start with small `--investment` to validate your range, then scale up
