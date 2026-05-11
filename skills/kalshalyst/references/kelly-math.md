# Kelly Criterion Position Sizing — Mathematical Deep Dive

## Classic Kelly Formula

For any gamble with two outcomes:

```
f* = (p × b - q) / b

where:
  f* = fraction of bankroll to wager
  p = probability of winning (0.0-1.0)
  q = probability of losing = 1 - p
  b = decimal odds - 1 = (payout / stake) - 1
```

## Applied to Prediction Markets

### Binary Market Structure

A Kalshi YES contract:
- **Cost:** c cents (1-99)
- **Payout if YES:** 100 cents
- **Payout if NO:** 0 cents
- **Profit if YES:** (100 - c) cents
- **Loss if NO:** c cents

### Deriving Kelly for YES Side

Given:
- Estimated probability: p = 0.65 (we think YES is 65% likely)
- Market price: c = 50 cents (market prices YES at 50%)
- Current bankroll: B = $200

**Step 1: Calculate odds ratio**
```
Profit per winning contract: 100 - 50 = 50 cents
Cost per contract: 50 cents
b = 50 / 50 = 1.0
```

**Step 2: Apply Kelly formula**
```
f* = (p × b - q) / b
   = (0.65 × 1.0 - 0.35) / 1.0
   = (0.65 - 0.35) / 1.0
   = 0.30 / 1.0
   = 0.30 (30% of bankroll)
```

**Step 3: Convert to dollars**
```
Bet size = 0.30 × $200 = $60
```

**Step 4: Convert to contracts**
```
Contracts = $60 / $0.50 per contract = 120 contracts
```

### Kelly for NO Side

If instead we estimate NO is more likely (p_no = 0.70):

**NO contract structure:**
- Cost: (100 - 50) = 50 cents
- Payout if NO: 100 cents
- Profit if NO: 50 cents

**Kelly calculation:**
```
p_no = 0.70, q_no = 0.30, b = 50/50 = 1.0
f* = (0.70 × 1.0 - 0.30) / 1.0 = 0.40 (40% of bankroll)
Bet = 0.40 × $200 = $80 = 160 contracts at 50¢
```

## Why Kelly Works

Kelly maximizes long-run growth:

```
Expected wealth after n bets = B × (1 + f × r)^n

where r = return per bet = (p × payout - q × loss) / stake - 1
```

With Kelly sizing, this grows exponentially without overbetting.

**Full Kelly drawback:** Can lead to large drawdowns (~50% portfolio swings) due to sequence risk. In real trading, you rarely use full Kelly.

## Fractional Kelly (Conservative Approach)

Kalshalyst uses fractional Kelly to reduce variance:

```
Fractional Kelly = f* × α

where α = 0.25 (quarter-Kelly, 75% more conservative than full Kelly)

Expected return: ~0.5× vs full Kelly
Max drawdown: ~50% vs full Kelly, much less likely
```

### With Confidence Discount

Apply a confidence penalty (non-linear):

```
Fractional Kelly = f* × α × (confidence^2)

where confidence = 0.0-1.0 (estimator's confidence level)
      confidence^2 = confidence squared (penalizes low confidence aggressively)
```

**Rationale:** Low-confidence estimates are noisier. Penalize quadratically to drop position size aggressively.

**Examples:**

```
Estimate 1: f* = 0.30, confidence = 0.9, α = 0.25
Fractional = 0.30 × 0.25 × (0.9^2) = 0.30 × 0.25 × 0.81 = 0.061 (6.1%)

Estimate 2: f* = 0.30, confidence = 0.6, α = 0.25
Fractional = 0.30 × 0.25 × (0.6^2) = 0.30 × 0.25 × 0.36 = 0.027 (2.7%)

Estimate 3: f* = 0.30, confidence = 0.3, α = 0.25
Fractional = 0.30 × 0.25 × (0.3^2) = 0.30 × 0.25 × 0.09 = 0.007 (0.7%)
```

Confidence dropped from 0.9 → 0.3, but position size dropped from 6.1% → 0.7% (8.7x reduction).

## Kelly in Practice: Full Example

### Setup
```
Market: "Will a Democrat win the 2028 election?"
Market Price: 48¢ (market implies 48% probability)
Claude Estimate: 62% probability
Confidence: 0.68
Bankroll: $200
Alpha: 0.25 (quarter-Kelly)
```

### Calculation

**Step 1: Edge**
```
Edge = |0.62 - 0.48| = 0.14 (14% edge)
Direction: YES is underpriced (market at 48%, we think 62%)
Side: BUY YES at 48¢
```

**Step 2: Kelly fraction**
```
p = 0.62 (probability YES wins)
q = 0.38 (probability NO wins)
cost_cents = 48 (cost per contract)
profit_cents = 52 (100 - 48)
b = 52 / 48 = 1.083

f* = (p × b - q) / b
   = (0.62 × 1.083 - 0.38) / 1.083
   = (0.671 - 0.38) / 1.083
   = 0.291 / 1.083
   = 0.269 (26.9% of bankroll)
```

**Step 3: Fractional Kelly with confidence**
```
confidence_discount = 0.68^2 = 0.462
fractional_f = 0.269 × 0.25 × 0.462
            = 0.031 (3.1% of bankroll)
```

**Step 4: Dollar amount**
```
Bet amount = 0.031 × $200 = $6.20
Contracts = $6.20 / $0.48 = 12.9 → 12 contracts (floor)
Actual cost = 12 × $0.48 = $5.76
```

**Step 5: Expected value**
```
If YES wins (our estimate: 62% likely):
  Return: 12 × $0.52 profit = $6.24 profit
  ROI: $6.24 / $5.76 = 8.3% return on capital

If NO wins (our estimate: 38% likely):
  Loss: 12 × $0.48 = -$5.76 loss
  ROI: -100% of position (12 contracts gone)

Expected value per trade:
EV = 0.62 × $6.24 + 0.38 × (-$5.76)
   = $3.87 - $2.19
   = +$1.68 (positive EV, we take it)
```

## Hard Caps (Defense-in-Depth)

Even with Kelly sizing, Kalshalyst enforces hard limits:

```python
MAX_CONTRACTS_PER_TRADE = 100      # Never more than 100 contracts
MAX_COST_PER_TRADE_USD = 25.00     # Never spend > $25 per trade
MAX_PORTFOLIO_EXPOSURE = $100.00   # Never have > $100 at risk total

MIN_EDGE_FOR_SIZING = 0.03         # Edge must be >= 3% to size position
MIN_CONFIDENCE = 0.2               # Confidence must be >= 0.2
```

### Cap Hierarchy

If Kelly sizing says "200 contracts", checks happen in order:

1. **Max contracts cap:** 200 → min(200, 100) = 100
2. **Max cost cap:** 100 × $0.50 = $50 → min($50, $25) = $25 → 50 contracts
3. **Exposure limit:** $25 + $30 current = $55 < $100 ✓ (OK)
4. **Floor:** 50 > MIN_CONTRACTS (1) ✓

**Final:** 50 contracts at $0.50 = $25 cost

## When Kelly Says "Don't Bet"

Kelly fraction can be **negative** (don't bet this side):

```
f* = (p × b - q) / b

If p × b < q, then f* < 0 (negative fractional Kelly)
```

**Example:**
```
Estimate: 45% probability YES
Market price: 60¢ (market implies 60%)

p = 0.45, q = 0.55
b = 40 / 60 = 0.667
f* = (0.45 × 0.667 - 0.55) / 0.667
   = (0.300 - 0.55) / 0.667
   = -0.250 / 0.667
   = -0.375 (negative)
```

**Interpretation:** Kelly says "don't bet YES at this price; the odds don't justify it."

Kalshalyst filters these out (zero contracts).

## Relationship to Edge

**Edge = estimated prob - market prob**

Kelly is proportional to edge for small edges:

```
Edge ≈ 1% → f* ≈ 0.01
Edge ≈ 5% → f* ≈ 0.05
Edge ≈ 10% → f* ≈ 0.10
```

More formally, for small edges and α ≈ odds near 1:

```
f* ≈ edge × b
Fractional ≈ edge × b × α × confidence^2
```

**Implication:** Doubling your edge → Kelly wants to double your position size.

## Kelly in Prediction Markets vs Traditional Betting

### Prediction Markets (Kalshi)

- **Bet structure:** "Will X happen?" YES or NO contract
- **Odds:** Binary (50 cents per dollar) — fixed odds structure
- **Margin:** Spreads 1-3 cents (tight)
- **Liquidity:** Varies (politics liquid, niche events illiquid)
- **Kelly formula:** Works directly (binary outcome)

### Traditional Betting (Sports)

- **Bet structure:** Moneyline, point spread, over/under
- **Odds:** Vary (ML: -110 standard, can be -150 to +500)
- **Margin:** Vig/juice (built into odds)
- **Kelly formula:** Requires odds conversion (American → decimal)

Kalshalyst is optimized for prediction market structure.

## Practical Calibration

### Aggressive Settings (High Risk, High Return)

```python
alpha = 0.5            # Half-Kelly (2× normal position)
min_edge = 0.02        # 2% minimum edge (vs 3%)
min_confidence = 0.3   # Lower threshold
max_contracts = 200    # Larger positions
max_cost_usd = 50.0
max_exposure = $500.0  # Higher portfolio risk
```

**Use when:** You're confident in your estimates (Brier < 0.15) and have capital.

### Conservative Settings (Low Risk, Steady Growth)

```python
alpha = 0.15           # 15% Kelly (1.5x more conservative)
min_edge = 0.05        # 5% minimum edge (vs 3%)
min_confidence = 0.6   # High threshold
max_contracts = 50
max_cost_usd = 10.0
max_exposure = $50.0   # Low portfolio risk
```

**Use when:** You're new to prediction markets or Brier is high.

## Monitoring Kelly Effectiveness

### Metrics to Track

1. **Win rate on Kelly-sized trades**
   ```
   Trades with edge >= 4% and kelly-sized:
   Win rate: 55% expected (if well-calibrated)
   If actual: < 45% → recalibrate
   If actual: > 65% → can be more aggressive
   ```

2. **Return on capital**
   ```
   Total profit / (Average capital deployed)
   Target: ~10-20% annual (depends on alpha, frequency)
   If < 5% → alpha too conservative
   If > 40% → might be luck, not skill (monitor volatility)
   ```

3. **Maximum drawdown**
   ```
   Worst peak-to-trough decline in portfolio
   Target: < 30% (depends on risk tolerance)
   If > 50% → alpha too aggressive
   ```

## References

### Classic Kelly Papers

- **Original (1956):** Kelly, J. L. (1956). "A new interpretation of information rate." *Bell System Technical Journal*.
  - Derives Kelly as the strategy maximizing long-run exponential growth
  - Includes ruin probability tables

- **Modern applications:** MacLean, L. C., Thorp, E. O., & Ziemba, W. T. (Eds.). (2011). *The Kelly Capital Growth Investment Criterion*.
  - Practical applications in investing and betting
  - Discussion of fractional Kelly and risk management

### Relevant Probability Papers

- **Calibration:** Lichtendahl Jr, K. C., Grushka-Cockayne, Y., & Pfeifer, P. E. (2013). "The accuracy of probability judgments in forecasting competitions".
  - Why experts are often overconfident
  - How to improve calibration through feedback

- **Brier scoring:** Murphy, A. H. (1971). "A note on the ranked probability score".
  - Formalization of Brier score
  - Decomposition into reliability and resolution

## Implementation Notes

Kalshalyst uses:
- **Default α = 0.25** (quarter-Kelly) — empirically good for LLM-derived estimates with ~0.15-0.20 Brier
- **Confidence^2 penalty** — non-linear, aggressively penalizes low-confidence
- **Hard caps** — prevent bankruptcy, even if Kelly overestimates edge

Tuning recommendations:
1. **Start with α = 0.25** — most traders are overconfident, need conservative cap
2. **Monitor Brier score** — if < 0.15, can increase α to 0.5
3. **Check win rate on high-edge trades** — target 55-60%
4. **Adjust caps quarterly** based on portfolio performance and volatility

Kalshalyst will output detailed Kelly results:

```
Kelly={kelly_fraction:.3f} | frac={fractional:.3f} (α=0.25, conf=0.68) |
12x @ 48¢ = $5.76 (2.9% of bankroll) | capped=False
```

Read this as: "Full Kelly says 26.9%, but after fractional (α=0.25) and confidence discount (0.68^2), we size 3.1% of bankroll → 12 contracts"
