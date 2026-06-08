# Brier Score: Measuring Prediction Calibration

## What Is It?

The Brier score measures how close your probability estimates are to actual outcomes. It's the mean squared error of your predictions:

```
Brier = (1/N) * SUM((predicted_probability - actual_outcome)^2)

where:
  predicted_probability = your estimate (0 to 1)
  actual_outcome = 1 if YES resolved, 0 if NO resolved
  N = number of predictions
```

## Why It Matters for Trading

In prediction markets, your probability estimates directly determine position sizing (via Kelly) and trade selection (via EV). If your estimates are miscalibrated, you'll systematically overbet or underbet. Brier score is the single best metric for calibration quality.

## Interpretation Scale

| Brier Score | Level | What It Means |
|-------------|-------|---------------|
| 0.250 | Random baseline | Predicting 50% for everything |
| 0.220 | Weak edge | Slightly better than a coin flip |
| 0.200 | Novice edge | Detectable but small alpha |
| 0.180 | Meaningful edge | Consistent, tradeable alpha |
| 0.150 | Strong edge | Top-tier amateur forecaster |
| 0.120 | Professional | Elite territory |
| < 0.100 | Superforecaster | Top 1% of all forecasters globally |

**Lower is better.** A perfect predictor scores 0.0 (every prediction is exactly right). The worst possible score is 1.0 (every prediction is maximally wrong).

## Brier Score in the Polymarket System

### How It's Calculated

```typescript
// From research/evaluate.ts
const brierScore = predictions.reduce((sum, p) => {
  const outcome = p.resolvedYes ? 1 : 0;
  return sum + Math.pow(p.ourProbability - outcome, 0.2);
}, 0) / predictions.length;
```

Only "active" predictions count — markets where the strategy decided to trade (not skip). This means Brier score measures the quality of your TRADING decisions, not your ability to predict markets you wisely avoided.

### Current Performance

The production system achieves Brier 0.18 (meaningful edge). This was reached through the autoresearch loop starting from ~0.22 (weak edge) and iteratively optimizing parameters.

### How Auto-Improve Uses It

The autoresearch loop (`research/auto-improve.ts`) treats Brier score as the loss function:

1. Current Brier = 0.1804 (baseline)
2. Try mutation: minEdgePct 3.0 → 2.5
3. Evaluate: new Brier = 0.1820 (worse)
4. Revert mutation
5. Try next mutation: PRIOR_WEIGHT 0.15 → 0.20
6. Evaluate: new Brier = 0.1798 (better!)
7. Keep mutation, save checkpoint

## Decomposition

Brier score can be decomposed into three components:

```
Brier = Uncertainty - Resolution + Reliability

Uncertainty: inherent unpredictability of outcomes (can't control)
Resolution:  ability to separate likely from unlikely events (higher = better)
Reliability: how close predictions are to observed frequencies (lower = better)
```

For trading purposes, focus on **reliability** — when you say 70%, events should resolve YES about 70% of the time.

## Calibration Checks

Create a calibration plot by binning predictions:

```
Bin [0.0-0.1]: Predicted avg 5%, Actual 3%   → well calibrated
Bin [0.1-0.2]: Predicted avg 15%, Actual 12%  → slightly overconfident
Bin [0.2-0.3]: Predicted avg 25%, Actual 30%  → slightly underconfident
...
```

If you're consistently overconfident (predicting higher than outcomes), increase PRIOR_WEIGHT to pull estimates toward base rates. If underconfident, decrease it.

## Relationship to Kelly

Brier score directly impacts Kelly sizing quality:

- **Good Brier (0.15)**: Probability estimates are accurate → Kelly sizes positions correctly → growth
- **Bad Brier (0.25)**: Estimates are noise → Kelly oversizes losers and undersizes winners → drawdown

This is why the autoresearch loop optimizes Brier first. Everything else (win rate, Sharpe, PnL) follows from well-calibrated probabilities.
