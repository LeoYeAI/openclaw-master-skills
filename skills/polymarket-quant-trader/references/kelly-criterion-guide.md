# Kelly Criterion Deep Dive for Prediction Markets

## The Core Idea

The Kelly Criterion answers: "Given my edge, what fraction of my bankroll should I bet to maximize long-run wealth growth?"

Bet too small and you leave money on the table. Bet too large and a losing streak wipes you out. Kelly finds the mathematically optimal middle ground.

## The Formula

```
f* = (p * b - q) / b

where:
  f* = fraction of bankroll to wager
  p  = probability of winning (your model's estimate)
  q  = 1 - p (probability of losing)
  b  = net odds (profit per $1 risked)
```

### In Prediction Markets

Polymarket prices shares between $0.01 and $0.99. The YES price IS the market-implied probability:

```
Market YES price = $0.40
Market-implied probability = 40%
Net odds (b) = (1 - 0.40) / 0.40 = 1.5

If your model says 50% (p = 0.50):
f* = (0.50 * 1.5 - 0.50) / 1.5
f* = (0.75 - 0.50) / 1.5
f* = 0.167  →  Bet 16.7% of bankroll
```

### Fractional Kelly

Full Kelly is mathematically optimal but emotionally brutal. Drawdowns regularly exceed 50%. Professional quant funds universally use fractional Kelly:

| Mode | Formula | Growth Rate | Max Drawdown |
|------|---------|-------------|--------------|
| Full Kelly | f* | 100% | Very high (50%+) |
| Half Kelly | 0.5 * f* | 75% of full | ~25% |
| Quarter Kelly | 0.25 * f* | ~56% of full | ~12% |

**Quarter Kelly is the default.** You capture over half the growth rate while cutting drawdowns to manageable levels.

## Edge Cases and Clamps

### Negative Kelly
If `f*` is negative, your model says the market is right (or better than you). Don't bet. The implementation clamps to 0.

### Extreme Probabilities
Probabilities near 0 or 1 produce degenerate Kelly fractions. The system clamps probabilities to [0.001, 0.999] and caps Kelly fraction at 0.15 (15% of bankroll) regardless of computed optimal.

### Why Cap at 15%?

Even with quarter Kelly, a single market can sometimes compute to 20%+ of bankroll. The 15% cap prevents concentration risk — no single prediction should represent more than 15% of your capital, regardless of how confident you are.

## Practical Application

### Step 1: Estimate Your Edge
```
Your probability estimate: 55%
Market YES price: $0.45 (45%)
Edge = 55% - 45% = 10 percentage points
```

### Step 2: Calculate Kelly
```
b = (1 - 0.45) / 0.45 = 1.222
f* = (0.55 * 1.222 - 0.45) / 1.222 = 0.182
Quarter Kelly = 0.25 * 0.182 = 0.0455 (4.55%)
```

### Step 3: Size the Position
```
Bankroll: $10,000
Position size = $10,000 * 0.0455 = $455
```

### Step 4: Validate
- Is $455 under MAX_POSITION_SIZE? (default $500) Yes.
- Is total exposure under MAX_TOTAL_EXPOSURE? Check.
- Is edge above MIN_EDGE_THRESHOLD? 10% > 10%. Yes.

## Common Mistakes

1. **Using full Kelly** — Guaranteed to blow up eventually. Use quarter.
2. **Ignoring the vig** — Polymarket charges fees. Subtract before calculating edge.
3. **Correlated bets** — Kelly assumes independent bets. If you bet on 5 crypto markets that all depend on Bitcoin, you're effectively making one oversized bet.
4. **Overconfident probabilities** — If your model consistently says 70% but outcomes happen 55% of the time, Kelly will oversize every bet. Track your Brier score.
5. **Ignoring liquidity** — Kelly says bet $2,000 but the order book only has $500 of depth? You'll move the market against yourself.

## Further Reading

- Kelly, J.L. (1956). "A New Interpretation of Information Rate"
- Thorp, E.O. (2006). "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market"
- See `references/brier-score-explained.md` for calibrating the probability estimates that feed Kelly.
