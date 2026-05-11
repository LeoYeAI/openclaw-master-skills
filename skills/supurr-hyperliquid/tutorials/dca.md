# DCA Bot Tutorial

Step-by-step guide to deploying a Dollar-Cost Averaging bot on Hyperliquid.

---

## What is DCA?

A DCA bot opens a base position, then adds to it ("averages in") each time the price moves against you by a set deviation. Once the averaged entry hits your take-profit target, it closes everything and optionally restarts.

**When to use DCA:**

- You have a directional view (bullish or bearish) but uncertain about entry timing
- You want to accumulate during dips (long) or rally fades (short)
- You want automatic position management with defined risk

**When NOT to use DCA:**

- Strong persistent trends against your direction (price keeps falling for long, rising for short)
- You can't afford the max position size at full DCA depth

---

## 1️⃣ Setup Credentials

```bash
supurr init --address 0xYOUR_WALLET --api-wallet 0xYOUR_API_KEY
```

---

## 2️⃣ Understand the DCA Mechanics

DCA works in **cycles**:

```
Trigger Price hit → Base Order → Price drops → DCA Order 1 → Drops more → DCA Order 2 → ... → Take Profit → (restart?)
```

### Key Parameters Explained

| Parameter              | What it Does                          | How to Think About It                                                  |
| ---------------------- | ------------------------------------- | ---------------------------------------------------------------------- |
| `trigger-price`        | Price to start the cycle              | For longs: set at or below current price. For shorts: at or above.     |
| `base-order`           | Initial position size (in base asset) | Your starter position. E.g., 0.001 BTC.                                |
| `dca-order`            | Size of each DCA step                 | Usually same as base order, or slightly larger.                        |
| `max-orders`           | How many DCA steps max                | More orders = deeper averaging but larger total position.              |
| `size-multiplier`      | Multiply DCA size at each step        | `1.0` = flat sizing. `2.0` = each DCA is 2x the previous (aggressive). |
| `deviation`            | Price drop % to trigger first DCA     | `0.01` = 1% drop from entry triggers first DCA.                        |
| `deviation-multiplier` | Widen gaps between DCAs               | `1.0` = equal spacing. `1.5` = each gap 50% wider than previous.       |
| `take-profit`          | % above avg entry to close            | `0.02` = close at 2% profit from averaged entry.                       |
| `stop-loss`            | Absolute PnL to cut losses            | Optional hard stop. Omit to rely only on DCA depth.                    |

### Position Size Planning

Before deploying, calculate your maximum possible position:

```
Max Position = base_order + Σ(dca_order × size_multiplier^i) for i = 0 to max_orders-1
```

**Example with 2x multiplier, 5 max orders:**

- Base: 0.001 BTC
- DCA 1: 0.001 BTC
- DCA 2: 0.002 BTC
- DCA 3: 0.004 BTC
- DCA 4: 0.008 BTC
- DCA 5: 0.016 BTC
- **Total max: 0.032 BTC**

Make sure your account can handle this at max leverage.

---

## 3️⃣ Generate Config

**Example — BTC long DCA, buy dips from $95k:**

```bash
supurr new dca \
  --asset BTC \
  --mode long \
  --trigger-price 95000 \
  --base-order 0.001 \
  --dca-order 0.001 \
  --max-orders 5 \
  --size-multiplier 2.0 \
  --deviation 0.01 \
  --take-profit 0.02 \
  --leverage 5 \
  --restart \
  --cooldown 120 \
  --output btc-dca.json
```

**Example — ETH short DCA, fade rallies:**

```bash
supurr new dca \
  --asset ETH \
  --mode short \
  --trigger-price 4000 \
  --base-order 0.01 \
  --dca-order 0.01 \
  --max-orders 3 \
  --size-multiplier 1.5 \
  --deviation 0.02 \
  --take-profit 0.03 \
  --leverage 3 \
  --output eth-dca-short.json
```

**Example — HYPE spot DCA (no liquidation risk):**

```bash
supurr new dca \
  --asset HYPE \
  --type spot \
  --quote USDC \
  --trigger-price 25 \
  --base-order 10 \
  --dca-order 10 \
  --max-orders 5 \
  --deviation 0.03 \
  --take-profit 0.05 \
  --output hype-dca-spot.json
```

---

## 4️⃣ Deploy

```bash
supurr deploy -c btc-dca.json
```

---

## 5️⃣ Monitor

```bash
supurr monitor --watch
```

DCA bots show one position that grows as DCA orders fill.

---

## Choosing Direction

| Mode    | Direction    | You Expect                  | Trigger Price             |
| ------- | ------------ | --------------------------- | ------------------------- |
| `long`  | Buy dips     | Price to eventually go UP   | At or below current price |
| `short` | Sell rallies | Price to eventually go DOWN | At or above current price |

---

## Restart Behavior

With `--restart`:

- After take-profit, the bot waits `--cooldown` seconds, then starts a new cycle
- Useful for range-bound markets where you want to keep catching bounces

Without `--restart`:

- Bot stops after first take-profit or stop-loss
- Use for one-shot accumulation plays

---

## Tips

- **Start conservative** — use `1.0` size multiplier and `3-5` max orders first
- **2x size multiplier is aggressive** — total position grows exponentially, ensure your margin can handle it
- **Deviation of 1-2%** works well for majors (BTC, ETH). Use 3-5% for higher-volatility assets
- **Always calculate max position** before deploying — the last DCA order is the biggest
- **Use spot for safer DCA** — no liquidation risk, just hold through drawdowns
- **Cooldown of 60-300s** prevents rapid re-entries in choppy markets when using `--restart`
