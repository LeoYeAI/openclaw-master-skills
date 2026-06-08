# Cross-Platform Arbitrage: Polymarket x 1WIN

## How It Works

Different platforms price the same event differently due to different user bases, information flow, and market mechanics. When the price gap exceeds transaction costs, you can trade the spread.

## Step-by-Step Mechanics

### Step 1: Find Matching Events

Polymarket lists prediction markets. 1WIN is a traditional bookmaker with decimal odds. The same real-world event appears on both with different names:

```
Polymarket: "Will the Lakers win Game 5?"     → YES @ $0.55
1WIN:       "Lakers vs Celtics - Lakers Win"  → 1.72 decimal odds
```

The system uses fuzzy title matching (Dice coefficient) to pair events:

```
1. Normalize both titles (lowercase, strip punctuation, remove stop words)
2. Compute Dice coefficient: 2 * |shared_tokens| / |total_tokens|
3. Threshold: 0.4 minimum (catches "Lakers Game 5" ↔ "Lakers Celtics Game 5")
```

### Step 2: Convert to Common Probability

```
Polymarket:  YES price $0.55 → implied probability 55.0%
1WIN:        Decimal odds 1.72 → implied probability 1/1.72 = 58.1%
```

### Step 3: Calculate the Spread

```
Spread = |55.0% - 58.1%| = 3.1 percentage points
```

1WIN thinks Lakers are MORE likely to win (58.1%) than Polymarket does (55.0%).

### Step 4: Determine Direction

```
If Polymarket price < 1WIN implied probability:
  → BUY YES on Polymarket (it's cheap relative to 1WIN)

If Polymarket price > 1WIN implied probability:
  → BUY NO on Polymarket (YES is expensive relative to 1WIN)
```

In this example: 55% < 58.1% → Buy YES on Polymarket. The market is underpricing YES relative to the bookmaker's assessment.

### Step 5: Account for Vig

1WIN charges approximately 2% vig (built into their odds). Subtract this from your expected profit:

```
Raw edge:         3.1%
1WIN vig:        -2.0%
Net expected:     1.1%
```

Only trade if net expected profit is positive.

### Step 6: Size with Kelly

```
Kelly fraction = edge / (1 - min(polyProb, onewinProb))
             = 0.031 / (1 - 0.55)
             = 0.069  →  6.9% of bankroll

Capped at 10% maximum (hard limit in code)
```

## Confidence Tiers

| Spread | Tier | Action |
|--------|------|--------|
| > 5% | HIGH | Strong signal — verify match and execute |
| 3-5% | MEDIUM | Good signal — verify carefully |
| 1-3% | LOW | Marginal — likely eaten by vig/slippage |
| < 1% | SKIP | No edge after costs |

## Data Source Cascade

The system tries multiple data sources for resilience:

1. **1WIN API** — Direct odds feed (may be geo-blocked in some regions)
2. **Polymarket CLOB** — Public orderbook API, convert YES prices to synthetic decimal odds
3. **Mock fallback** — Simulated data for testing (clearly labeled as "mock" source)

The output always indicates which source was used so you know if you're trading on live or simulated data.

## Risk Factors

### Title Matching False Positives
A Dice coefficient of 0.4 is intentionally loose to catch variant phrasings. This means occasional false matches. Always verify the match manually before trading — "Lakers Game 5" and "Lakers Game 6" will match but are different events.

### Stale Prices
1WIN odds update less frequently than Polymarket. A spread might exist on paper but disappear by the time you execute. Check both platforms live before trading.

### Geo-Restrictions
1WIN may not be accessible in all regions. If the API is blocked, the system falls back to CLOB-derived synthetic odds, which are less reliable for arb detection (you're comparing Polymarket to itself).

### Execution Risk
You can only trade one side (Polymarket). True arbitrage requires simultaneous execution on both platforms. Since you can't bet on 1WIN programmatically in most cases, you're making a directional bet informed by the cross-platform signal — not a risk-free arb.

## Monitoring Mode

The detector supports continuous monitoring:

```bash
npm run arb:scan
# Polls every 60 seconds
# Alerts on NEW opportunities (deduplicates by arb ID)
# Logs all discoveries with timestamps
```

Use this during high-activity periods (major sports events, crypto volatility, election nights) when spreads are most likely to appear.
