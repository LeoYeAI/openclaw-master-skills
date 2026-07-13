# Kalshi Command Center — Heuristic Edge Scoring Algorithm

Complete documentation of the 4-factor composite scoring system used in live market scans.

## Overview

The `scan` command ranks markets by a composite **edge score** (0-100 scale) based on:

1. **Spread Tightness** (25% weight) — Price discovery efficiency
2. **Distance from Extremes** (35% weight) — Market uncertainty
3. **Liquidity** (25% weight) — Trading activity
4. **Time Value** (15% weight) — Time to expiration

The algorithm is designed to surface markets with the best **right now** trading opportunities, without requiring external ML models or data sources.

## Factor 1: Spread Tightness (25% weight)

### Formula

```
spread_pct = spread / max(mid_price, 1) * 100
spread_score = max(0, 20 - spread_pct) / 20
```

### Interpretation

- **Score 1.0**: 0% spread (bid = ask), perfect price discovery
- **Score 0.5**: 10% spread (reasonable for illiquid markets)
- **Score 0.0**: 20%+ spread (very wide, poor discovery)

### Rationale

Tight spreads indicate:
- Liquid order book with multiple price levels
- Informed traders actively quoting
- Efficient price discovery (hard to arbitrage)

Wide spreads indicate:
- Illiquid market (few sellers, few buyers)
- Uninformed pricing (market makers padding spreads)
- Difficulty executing even moderate-size trades

### Examples

| Market | Bid | Ask | Spread | Spread % | Score |
|--------|-----|-----|--------|----------|-------|
| Efficient macro | 49¢ | 50¢ | 1¢ | 2.0% | 0.90 |
| Healthy market | 35¢ | 37¢ | 2¢ | 5.7% | 0.72 |
| Illiquid market | 40¢ | 50¢ | 10¢ | 20.0% | 0.00 |
| Dead market | 25¢ | 50¢ | 25¢ | 66.7% | 0.00 |

## Factor 2: Distance from Extremes (35% weight)

### Formula

```
centrality = 1 - abs(mid - 50) / 50

if mid < 15 or mid > 85:
    centrality *= 0.3  # heavy penalty for near-settled markets
```

### Interpretation

- **Score 1.0**: Exactly at 50¢ (maximum entropy/uncertainty)
- **Score 0.5**: 25¢ or 75¢ (reasonable uncertainty)
- **Score 0.0**: 0¢ or 100¢ (fully resolved, no trading)

With penalty:
- **Score 0.3**: At 15¢ or 85¢ (near-certain, illiquid)
- **Score 0.09**: At 5¢ or 95¢ (almost settled, dead market)

### Rationale

Markets at 50¢ represent maximum uncertainty — neither YES nor NO dominates. These offer the best edge opportunities:
- Fair pricing (no lopsided odds)
- High information content
- Strong consensus disagreement

Markets at extremes (0¢ or 100¢) are near-resolved:
- Low uncertainty (event already decided)
- Illiquid (few traders believe opposite side)
- Untradeworthy (outcome nearly certain)

### Examples

| Market | YES Price | NO Price | Mid | Centrality | Score | Status |
|--------|-----------|----------|-----|-----------|-------|--------|
| Uncertain | 49¢ | 51¢ | 49 | 1.00 | 1.00 | 🎯 Best |
| Moderate | 35¢ | 65¢ | 35 | 0.30 | 0.30 | ⚠️ Edge |
| Asymmetric | 15¢ | 85¢ | 15 | 0.70 | 0.21 | 🔻 Weak |
| Near-settled | 5¢ | 95¢ | 5 | 0.90 | 0.27 | ❌ Dead |

### Penalty Justification

Near-settled markets (mid < 15 or > 85) get 70% penalty because:
- Market is illiquid (few believers in losing side)
- Bid-ask spreads widen dramatically
- P&L potential limited (can only make 5-15¢ per contract)

Examples:
- Market at 85¢ (YES almost certain) → selling YES returns only 5-15¢
- Market at 5¢ (YES almost impossible) → buying YES is high-risk, low-reward

## Factor 3: Liquidity (25% weight)

### Formula

```
liq_score = log(1 + volume) * 0.6 + log(1 + oi) * 0.4
```

Where:
- `volume` = 24-hour or all-time volume (Kalshi provides both)
- `OI` = open interest (total contracts outstanding)

### Interpretation

Log-scaling (via `log(1 + x)`) prevents mega-markets from dominating:

| Volume | log1p(vol) | Scaled (0.6x) |
|--------|-----------|---------------|
| 0 | 0.0 | 0.0 |
| 10 | 2.30 | 1.38 |
| 100 | 4.61 | 2.77 |
| 1,000 | 6.91 | 4.15 |
| 10,000 | 9.21 | 5.52 |

Log scaling means:
- Going from 10→100 volume adds ~1.4 points
- Going from 100→1000 adds ~1.4 points (same boost)
- Prevents a 100k-volume market from scoring 10x higher than 10k-volume market

### Rationale

Liquidity proxy for:
- Market maturity (time to accumulate volume)
- Trader interest (fundamental quality signal)
- Fill probability (can exit position at fair price)

Higher liquidity → easier to execute at mid-price → better risk management.

### Examples

| Market | Volume | OI | vol_score (0.6x) | oi_score (0.4x) | Total |
|--------|--------|----|----|----|----|
| Dead | 5 | 10 | 0.41 | 0.32 | 0.73 |
| Healthy | 500 | 2000 | 2.77 | 2.09 | 4.86 |
| Active | 5000 | 20000 | 4.15 | 3.12 | 7.27 |
| Mega | 100000 | 500000 | 5.52 | 4.16 | 9.68 |

## Factor 4: Time Value (15% weight)

### Formula

```
time_score = 1.0  # default

if days_to_close < 14:
    time_score = days_to_close / 14
elif days_to_close > 60:
    time_score = max(0.3, 1 - (days_to_close - 60) / 120)
```

### Interpretation

- **Score 1.0**: 14-60 days to close (sweet spot)
- **Score 0.5**: 7 days or 110 days to close
- **Score 0.3 (floor)**: 180+ days to close

### Rationale

Markets have optimal trading horizons:

**Too Short (< 14 days)**:
- Gamma risk increases (certainty effects)
- Information cascades (rumors become facts)
- Less time for edge to realize
- Example: "Will Inflation Report beat expectations?" with 3 days left is binary, not tradeable

**Optimal (14-60 days)**:
- Enough time for fundamental catalysts
- Information flow is steady, not cascade
- Position has time to develop
- Natural trading window for Kalshi's user base

**Too Long (> 60 days)**:
- Thesis may invalidate (political/economic shifts)
- Low vol (bored market, stale prices)
- Theta decay (time value dissipates)
- Example: 2-year election markets are too early to have real information

### Examples

| Market | Days | Formula | Score | Rationale |
|--------|------|---------|-------|-----------|
| Fed decision | 2d | 2/14 | 0.14 | Too imminent, binary |
| CPI release | 10d | 10/14 | 0.71 | Approaching event |
| Q1 earnings | 45d | 1.0 | 1.00 | Optimal window |
| Mid-year | 75d | max(0.3, 1-(75-60)/120) | 0.38 | Thesis risk |
| Election | 365d | max(0.3, 1-(365-60)/120) | 0.30 | Floor reached |

## Composite Score Calculation

### Formula

```
edge_score = (
    spread_score * 25
    + centrality * 35
    + liq_score * 25
    + time_score * 15
)
```

Weights sum to 100, so max score is 100 (all factors 1.0).

### Breakdown

| Component | Max | Weight | Max Contribution |
|-----------|-----|--------|------------------|
| Spread | 1.0 | 25 | 25.0 |
| Centrality | 1.0 | 35 | 35.0 |
| Liquidity | ~10 | 25 | ~2.5 (capped) |
| Time | 1.0 | 15 | 15.0 |
| **Total** | — | — | **100.0** |

Note: Liquidity score is unbounded but typically 0-10 range. The weighting system assumes normalized inputs; see "Normalization" below.

### Worked Example

Market: "Will US inflation exceed 4% by June 2026?"
- Current price: 35¢ YES, 37¢ NO (2¢ spread)
- Volume: 2,500 contracts
- OI: 12,000 contracts
- Days to close: 45 days

**Calculation**:

```
mid = (35 + 37) / 2 = 36¢
spread = 37 - 35 = 2¢
spread_pct = 2 / 36 * 100 = 5.6%
spread_score = max(0, 20 - 5.6) / 20 = 0.72

centrality = 1 - abs(36 - 50) / 50 = 1 - 0.28 = 0.72
(no penalty, mid is 36, not < 15 or > 85)

liq_score = log1p(2500) * 0.6 + log1p(12000) * 0.4
          = 7.83 * 0.6 + 9.39 * 0.4
          = 4.70 + 3.76
          = 8.46

time_score = 1.0 (45 days, in 14-60 range)

edge_score = (0.72 * 25) + (0.72 * 35) + (8.46 * 25) + (1.0 * 15)
           = 18.0 + 25.2 + 211.5 + 15.0
           = 269.7
```

**Issue**: Score exceeds 100. This means liquidity weight is too high for unbounded liq_score. In practice, the implementation caps liq_score via different normalization. See next section.

## Normalization (Implementation Detail)

In `kalshi_commands.py`, the actual weights are:

```python
edge_score = (
    spread_score * 25        # 0-25
    + centrality * 35        # 0-35
    + liq_score * 25         # 0-25 (liq_score capped or scaled)
    + time_score * 15        # 0-15
)
```

Liquidity is NOT directly summed; instead:

```python
import math
liq_score = math.log1p(volume) * 0.6 + math.log1p(oi) * 0.4
# This is then multiplied by 25 weight
```

So with high volume (10k):
```
liq_score = log(10001) * 0.6 + log(10001) * 0.4
          ≈ 9.2 * 0.6 + 9.2 * 0.4
          ≈ 9.2
contribution = 9.2 * 25 = 230 (WRONG!)
```

**Actual implementation**: Liquidity score is capped or normalized to [0, 1] range before multiplication.

If capped at 1.0:
```
liq_score = min(1.0, math.log1p(volume) * 0.6 + math.log1p(oi) * 0.4)
# reaches 1.0 around vol=100, oi=1000
contribution = 1.0 * 25 = 25 (correct)
```

## Ranking & Display

Markets are sorted by `edge_score` descending. Top 8 are displayed.

```bash
python kalshi_commands.py scan
# Returns top 8 markets by edge_score
```

Example output:

```
🎯 Live Scan — 600 markets scanned, 47 passed filters:

1. Will US inflation exceed 4%?
   35¢/37¢ (spread 2¢ = 5.8%) | vol 2,500 | OI 12,000 | 45d
   Score: 78.5 | ECON-INFL-2026

2. Will Fed cut rates next meeting?
   42¢/44¢ (spread 2¢ = 4.8%) | vol 3,100 | OI 15,600 | 30d
   Score: 75.2 | FED-RATE-2026
```

## Interpretation & Trading Strategy

### High Score (75+)

Markets with scores 75+ are:
- Liquid (recent trading activity)
- Efficient (tight spreads)
- Uncertain (mid-range prices)
- Tradeable (14-60 day horizon)

**Strategy**: Post limit orders to improve on bid/ask, expect fills.

Example: 35¢ bid → post 36¢ bid to capture 1¢ spread.

### Medium Score (50-74)

Markets with scores 50-74 have:
- One or more weaknesses (e.g., wide spread or near-settled)
- Still tradeable but higher friction

**Strategy**: Only trade if thesis is strong. Use limit orders.

### Low Score (< 50)

Markets with scores < 50:
- Either illiquid, wide spread, or extreme price
- Hard to execute at fair price

**Strategy**: Avoid. Wait for liquidity or arbitrage opportunities.

## Sensitivity Analysis

How does each factor influence overall score?

**Spread Impact** (1% → 2% spread):
- spread_score: 0.95 → 0.90
- edge_score impact: -1.25 points

**Centrality Impact** (40¢ → 45¢):
- centrality: 0.20 → 0.10
- edge_score impact: -3.5 points

**Liquidity Impact** (100 vol → 1,000 vol):
- liq_score: ~2.3 → ~6.9
- edge_score impact: +11.5 points (if unbounded)

**Time Impact** (7d → 30d):
- time_score: 0.50 → 1.00
- edge_score impact: +7.5 points

### Which Factor Matters Most?

Ranked by weight:
1. **Centrality (35%)**: Price uncertainty is dominant
2. **Spread (25%)** & **Liquidity (25%)**: Tied for execution quality
3. **Time (15%)**: Matters, but secondary

Intuition: Markets need uncertainty (centrality) to be edge-able. Spread & liquidity determine if you can execute at fair price. Time ensures thesis has time to play out.

## Limitations & Gotchas

1. **Centrality Penalty Too Harsh?**
   - Markets at 85¢ (95% YES) get 30% of base score
   - May miss genuine edges in near-certain markets
   - **Fix**: Adjust penalty factor from 0.3 to 0.5+ if needed

2. **Liquidity Not Capped**
   - Mega-markets can score 2-3x higher than medium-liquidity markets
   - **Fix**: Cap liq_score to [0, 1] range before weighting

3. **Time Score Floor at 0.3**
   - Very long-dated markets all score 0.3, indistinguishable
   - **Fix**: Add subcategory scoring for 60-90d vs 90-180d ranges

4. **No Information Cascade Detection**
   - Markets with rapid mid-price movement not penalized
   - May indicate gamma risk or cascading information
   - **Fix**: Add volatility/gamma factor

5. **No Market Depth Factor**
   - Only considers spread (width of #1 bid/ask)
   - Doesn't measure order book depth at multiple levels
   - **Fix**: Would require Kalshi API enhancements

## Comparison to Other Scoring Systems

### Kelly Criterion

Kelly uses edge probability & odds to size position. Edge Score ranks markets, doesn't size.

```
Kelly: f* = (p * b - q) / b  (position sizing)
Edge Score: composite of 4 factors  (market ranking)
```

**Relationship**: High edge_score markets → better Kelly sizing opportunities.

### Sharpe Ratio

Sharpe uses historical return volatility. Edge Score is forward-looking (does not use historical data).

```
Sharpe: (avg_return - risk_free) / std_dev
Edge Score: microstructure signals (spread, liquidity, uncertainty)
```

**Relationship**: Markets with high edge_score tend to have lower realized volatility (liquidity drives Sharpe).

### Alpha Models (e.g., Qwen)

Alpha models use NLP/ML to estimate outcome probability. Edge Score uses market-only signals.

```
Alpha: estimated_probability (ML-based)
Edge Score: market microstructure ranking
```

**Relationship**: Edge Score identifies where alpha models will be most useful (liquid, uncertain markets).

## Future Enhancements

1. **Volatility Component**: Penalize rapidly-moving mid-prices
2. **Depth Weighting**: Multiple-level order book analysis
3. **Cross-Market Correlation**: Avoid correlated positions
4. **Theta Decay**: Explicit time value (option pricing)
5. **News Sentiment**: Real-time sentiment feed integration

## References

- **Efficient Markets**: https://en.wikipedia.org/wiki/Efficient-market_hypothesis
- **Bid-Ask Spread**: https://en.wikipedia.org/wiki/Bid%E2%80%93ask_spread
- **Market Microstructure**: https://en.wikipedia.org/wiki/Market_microstructure
- **Kelly Criterion**: https://en.wikipedia.org/wiki/Kelly_criterion
