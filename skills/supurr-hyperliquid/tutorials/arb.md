# Arb Bot Tutorial

Step-by-step guide to deploying a spot-perp arbitrage bot on Hyperliquid.

---

## What is Spot-Perp Arbitrage?

A spot-perp arb bot exploits price differences between the **spot** and **perpetual futures** market for the same asset. When spot is cheaper than perp (positive spread), it buys spot and shorts perp. When the spread narrows or reverses, it closes both positions for a profit.

This is a **market-neutral** strategy — you're not betting on price direction, only on the spread between two markets.

**When to use Arb:**

- You want low-risk, market-neutral returns
- The asset has consistent spread between spot and perp
- You have capital to allocate to both spot and perp wallets

**When NOT to use Arb:**

- Very tight spreads (fees eat into profits)
- Low-liquidity spot markets (high slippage on entry/exit)

---

## 1️⃣ Setup Credentials

```bash
supurr init --address 0xYOUR_WALLET --api-wallet 0xYOUR_API_KEY
```

---

## 2️⃣ Check Eligible Markets

Not all assets support arb. You need **both** a spot and perp market on Hyperliquid for the same asset.

### Available Arb Pairs (verified)

**U-prefix tokens** (majors with wrapped spot):

| Asset | Spot Token | Spot Pair  | Perp |
| ----- | ---------- | ---------- | ---- |
| BTC   | UBTC       | UBTC/USDC  | BTC  |
| ETH   | UETH       | UETH/USDC  | ETH  |
| SOL   | USOL       | USOL/USDC  | SOL  |
| ENA   | UENA       | UENA/USDC  | ENA  |
| WLD   | UWLD       | UWLD/USDC  | WLD  |
| MON   | UMON       | UMON/USDC  | MON  |
| MEGA  | UMEGA      | UMEGA/USDC | MEGA |
| ZEC   | UZEC       | UZEC/USDC  | ZEC  |
| XPL   | UXPL       | UXPL/USDC  | XPL  |
| PUMP  | UPUMP      | UPUMP/USDC | PUMP |

**Exact-name tokens** (spot name = perp name):

| Asset | Spot Pair  | Perp  |
| ----- | ---------- | ----- |
| HYPE  | HYPE/USDC  | HYPE  |
| TRUMP | TRUMP/USDC | TRUMP |
| PURR  | PURR/USDC  | PURR  |
| BERA  | BERA/USDC  | BERA  |

> **⚠️ Don't pass the spot name directly.** Always use the **perp ticker** (e.g., `--asset BTC`, not `--asset UBTC`). The CLI resolves the spot counterpart automatically.

---

## 3️⃣ Fund Both Wallets

Arb bots trade on **two sides simultaneously**, so you need USDC in both wallets:

1. **Spot wallet** — for buying the spot token
2. **Perps wallet** — for shorting the perpetual

On Hyperliquid, transfer USDC between wallets via: Portfolio → Transfer → Spot ↔ Perps.

> **Rule of thumb**: Split your allocation roughly 50/50 between spot and perps wallets.

---

## 4️⃣ Generate Config

Understand the key parameters:

| Parameter        | What it Controls                | Guidance                                                                                 |
| ---------------- | ------------------------------- | ---------------------------------------------------------------------------------------- |
| `--amount`       | USDC per leg per trade          | Start small ($50-100). This is per-side, so $100 means $100 spot + $100 perp.            |
| `--open-spread`  | Min spread to open a position   | Higher = fewer but safer trades. `0.003` (0.3%) is a good start.                         |
| `--close-spread` | Spread to close the position    | Can be negative (close at a loss on spread if funding compensates). `-0.001` is typical. |
| `--slippage`     | Max acceptable slippage per leg | Keep tight for liquid assets (`0.001`), wider for illiquid (`0.002`+).                   |
| `--leverage`     | Perp leverage                   | `1x` is safest. Higher leverage = more capital efficient but adds liquidation risk.      |

**Example — BTC arb with $200 per leg:**

```bash
supurr new arb \
  --asset BTC \
  --amount 200 \
  --leverage 1 \
  --open-spread 0.003 \
  --close-spread -0.001 \
  --slippage 0.001 \
  --output btc-arb.json
```

**Example — HYPE arb (smaller, tighter spreads):**

```bash
supurr new arb \
  --asset HYPE \
  --amount 50 \
  --leverage 2 \
  --open-spread 0.005 \
  --close-spread 0.001 \
  --slippage 0.002 \
  --output hype-arb.json
```

---

## 5️⃣ Review Config

Before deploying, review the generated config:

```bash
supurr config btc-arb
```

Verify:

- ✅ Two markets listed (spot + perp)
- ✅ Spot token resolved correctly (e.g., `UBTC` for BTC)
- ✅ Spread thresholds match your expectations
- ✅ Environment is `mainnet` (not `testnet`)

---

## 6️⃣ Deploy

```bash
supurr deploy -c btc-arb.json
```

The bot will start monitoring the spread between spot and perp, and execute trades when the spread exceeds your `--open-spread` threshold.

---

## 7️⃣ Monitor

```bash
supurr monitor --watch
```

Arb bots show **two positions** — one spot (long) and one perp (short). The combined PnL is what matters.

---

## Understanding Spreads

```
Spread = (Perp Price - Spot Price) / Spot Price
```

- **Positive spread** (perp > spot): Bot buys spot, shorts perp → earns when spread narrows
- **Negative spread** (perp < spot): Opposite direction

The `open-spread` threshold prevents trading on tiny, unprofitable spreads. The `close-spread` threshold determines when to take profit.

**Example flow:**

1. Spread hits +0.4% → bot opens (buys UBTC spot, shorts BTC perp)
2. Spread narrows to -0.1% → bot closes both positions
3. Net profit ≈ 0.4% + 0.1% = 0.5% minus fees and slippage

---

## Tips

- **BTC and ETH** have the deepest spot liquidity — best for arb
- **Start with 1x leverage** on perps — arb is about consistency, not big swings
- **Watch spot liquidity** — if the spot order book is thin, slippage can kill profits
- **Funding rates matter** — when you're short perp, you receive/pay funding. Positive funding = bonus income for short perp positions
- **Scale gradually** — start with $50-100 per leg, monitor for a day, then increase
