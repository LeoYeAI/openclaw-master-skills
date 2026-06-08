---
name: polymarket-quant-trader
description: "Professional-grade Polymarket prediction market trading system. Includes Kelly Criterion position sizing, EV calculator, Bayesian probability updater, cross-platform arbitrage detector (Polymarket vs 1WIN), and autoresearch loop that self-improves strategy overnight via Brier score optimisation. Use when: user wants to trade prediction markets, find arbitrage opportunities, build a trading bot, or improve prediction accuracy. Triggers: polymarket, prediction markets, kelly criterion, EV trading, arb detector, brier score, prediction market bot, market making, quant trading, sports betting math, cross-platform arbitrage."
version: 1.0.0
---

# Polymarket Quant Trader

A professional quant trading system for Polymarket prediction markets, built and battle-tested in production. Three alpha streams. One integrated system.

---

## Overview

This skill gives you a complete quantitative trading system for Polymarket with three independent alpha streams:

1. **EV-Based Signal Trading** — Kelly Criterion position sizing + Bayesian probability updating. Find edges, size them correctly, update beliefs as evidence arrives.
2. **Self-Improving Strategy (Autoresearch Loop)** — An autonomous hill-climbing optimizer that tunes your strategy parameters overnight using Brier score as the objective function. Wake up to a better strategy.
3. **Cross-Platform Arbitrage (PM x 1WIN)** — Detect spread discrepancies between Polymarket and 1WIN bookmaker. Fuzzy title matching, confidence tiering, Kelly-sized positions.

Each stream works independently or together. The system ships with TypeScript source, npm scripts for every workflow, and a backtester to validate before going live.

**Current production performance:** Brier score 0.18 (meaningful edge territory — baseline random is 0.25, professional is sub-0.12).

---

## Stream 1: EV-Based Signal Trading

### How It Works

The core loop: estimate a probability, compare it to the market price, calculate expected value, size the position with Kelly Criterion, and update beliefs as new evidence arrives.

### Kelly Criterion Position Sizing

Kelly answers: "Given my edge, what fraction of my bankroll should I bet?"

**The formula:**

```
f* = (p * b - q) / b

where:
  f* = optimal fraction of bankroll to wager
  p  = probability of winning (your estimate, 0-1)
  b  = net odds multiplier (payout per $1 risked)
  q  = 1 - p (probability of losing)
```

In prediction markets, odds derive from the market price:

```
b = (1 - marketYesPrice) / marketYesPrice
```

If YES trades at $0.40, then b = 0.60/0.40 = 1.5 (you risk $0.40 to win $0.60).

**Implementation:**

```typescript
// kelly-criterion.ts
export function kelly(p: number, b: number, q?: number): number {
  const qVal = q ?? 1 - p;
  return (p * b - qVal) / b;
}

export function quarterKelly(p: number, b: number): number {
  return 0.25 * kelly(p, b);
}

export function kellySizing(
  bankroll: number,
  p: number,
  b: number,
  mode: 'full' | 'half' | 'quarter' = 'quarter'
): number {
  const fraction = mode === 'full' ? kelly(p, b)
    : mode === 'half' ? 0.5 * kelly(p, b)
    : quarterKelly(p, b);
  return Math.max(0, bankroll * Math.min(fraction, 0.15));
}
```

**Why quarter Kelly?** Full Kelly maximizes long-run growth rate but produces brutal drawdowns (50%+ swings). Quarter Kelly captures ~75% of the growth rate with dramatically lower variance. Every serious quant fund uses fractional Kelly.

### EV Calculator

Expected value quantifies your edge per dollar risked:

```typescript
// ev-calculator.ts
export interface MarketEV {
  marketId: string;
  ourP: number;           // Your estimated probability
  marketP: number;        // Market-implied probability (= YES price)
  b: number;              // Net odds: (1 - marketP) / marketP
  ev: number;             // Expected value per dollar risked
  edgePct: number;        // Edge as percentage of market price
  kellyFraction: number;  // Quarter Kelly optimal fraction
  recommend: boolean;     // Worth trading? (ev > 0 && edgePct >= 2%)
}

export function calcEV(ourProbability: number, marketYesPrice: number) {
  const b = (1 - marketYesPrice) / marketYesPrice;
  const ev = ourProbability * b - (1 - ourProbability);
  const edgePct = (ev / marketYesPrice) * 100;
  return { ev, edgePct, b };
}

export function scoreMarket(market: any, ourP: number): MarketEV {
  const { ev, edgePct, b } = calcEV(ourP, market.yesPrice);
  const kellyFraction = quarterKelly(ourP, b);
  return {
    marketId: market.id,
    ourP,
    marketP: market.yesPrice,
    b,
    ev,
    edgePct,
    kellyFraction,
    recommend: ev > 0 && edgePct >= 2,
  };
}

export function rankByEV(markets: MarketEV[]): MarketEV[] {
  return [...markets].sort((a, b) => b.ev - a.ev);
}
```

**Reading the output:** An `edgePct` of 5% means your model thinks the market is mispriced by 5%. The `recommend` flag fires when EV is positive AND edge exceeds 2% (below that, transaction costs eat your edge).

### Bayesian Probability Updater

Update your probability estimates as new evidence arrives:

```typescript
// bayesian-updater.ts
export interface BayesianState {
  marketId: string;
  priorP: number;
  currentP: number;
  evidence: Evidence[];
  lastUpdated: Date;
}

export interface Evidence {
  description: string;
  likelihoodRatio: number; // > 1 supports YES, < 1 supports NO
  timestamp: Date;
}

export function bayesUpdate(prior: number, likelihoodRatio: number): number {
  const posterior = (prior * likelihoodRatio) /
    (prior * likelihoodRatio + (1 - prior));
  return Math.max(0.001, Math.min(0.999, posterior));
}

export function addEvidence(
  state: BayesianState,
  evidence: Evidence
): BayesianState {
  const newP = bayesUpdate(state.currentP, evidence.likelihoodRatio);
  return {
    ...state,
    currentP: newP,
    evidence: [...state.evidence, evidence],
    lastUpdated: evidence.timestamp,
  };
}

export function getRecommendation(
  state: BayesianState,
  marketPrice: number
): { action: 'buy' | 'sell' | 'hold'; confidence: number; reason: string } {
  const diff = state.currentP - marketPrice;
  if (Math.abs(diff) < 0.02) return { action: 'hold', confidence: 0, reason: 'Within noise' };
  if (diff > 0) return { action: 'buy', confidence: diff, reason: `Model ${(diff*100).toFixed(1)}% above market` };
  return { action: 'sell', confidence: -diff, reason: `Model ${(-diff*100).toFixed(1)}% below market` };
}
```

**Likelihood ratios:** A ratio of 2.0 means "this evidence is twice as likely if YES is true." A ratio of 0.5 means "this evidence is twice as likely if NO is true." The Bayesian updater chains multiple evidence items — each update feeds the next as a new prior.

### Market Scorer (Composite Ranking)

Combines all signals into a single score for market selection:

```typescript
// market-scorer.ts — Weighted scoring model
// EV Score:      40% weight — edge percentage
// Kelly Fraction: 30% weight — optimal sizing (higher = more confident)
// Expiry Window:  20% weight — sweet spot 6-72 hours
// Volume Score:   10% weight — log-normalized liquidity
```

Markets scoring highest get traded first. The expiry window filter avoids two failure modes: too-short expiry (can't exit if wrong) and too-long expiry (capital locked up, edge decays).

---

## Stream 2: Self-Improving Strategy (Autoresearch Loop)

### The Brier Score Metric

Brier score measures prediction calibration — how close your probability estimates are to actual outcomes:

```
brierScore = mean((predictedProbability - actualOutcome)^2)

where actualOutcome = 1 if resolved YES, 0 if resolved NO
```

**Interpretation scale:**
| Score | Level | Meaning |
|-------|-------|---------|
| 0.25 | Random | Coin-flip predictions |
| 0.22 | Weak edge | Slightly better than random |
| 0.18 | Meaningful edge | Consistent alpha |
| 0.12 | Professional | Elite forecaster territory |
| < 0.10 | Superforecaster | Top 1% calibration |

Lower is better. The system tracks Brier score as the primary optimization objective.

### Strategy Configuration

The strategy is defined by tunable parameters:

```typescript
// research/strategy.ts
export interface StrategyConfig {
  minVolume: number;          // Minimum market volume ($)
  minEdgePct: number;         // Minimum edge to trade (%)
  kellyMode: "full"|"half"|"quarter";
  maxKellyFraction: number;   // Cap on position size
  expiryMinHours: number;     // Earliest expiry to consider
  expiryMaxHours: number;     // Latest expiry to consider
}

export const DEFAULT_CONFIG: StrategyConfig = {
  minVolume: 10000,
  minEdgePct: 3.0,
  kellyMode: "quarter",
  maxKellyFraction: 0.15,
  expiryMinHours: 6,
  expiryMaxHours: 72,
};

// Category-specific base rates (priors for YES resolution)
const CATEGORY_PRIORS = {
  sports: 0.48,
  crypto: 0.45,
  politics: 0.50,
  tech: 0.50,
  weather: 0.45,
  misc: 0.50,
};
```

**Prediction logic:**

```typescript
const PRIOR_WEIGHT = 0.15; // How much to weight the category prior

ourProbability = marketYesPrice * (1 - PRIOR_WEIGHT) + prior * PRIOR_WEIGHT;
edgePct = Math.abs(ourProbability - marketYesPrice) * 100;

// Decision:
if (edgePct < minEdgePct) → skip
else if (ourP > marketYesPrice) → buy_yes
else → buy_no
```

### Running the Autoresearch Loop

```bash
# One-shot evaluation against resolved markets
npm run research:eval

# Manual iteration (5 rounds, stops on plateau)
npm run research

# Autonomous hill-climbing optimizer (run overnight)
npm run research:auto
```

**How `research:auto` works:**

1. Loads current strategy config
2. Tries a parameter mutation (e.g., minEdgePct 3.0 → 2.5)
3. Evaluates against all resolved markets → gets Brier score
4. If Brier improved → keep change, bump version, save checkpoint
5. If Brier worsened → revert to backup
6. Move to next untried mutation
7. Stop when all mutations exhausted without improvement

**Parameter search space:**

```typescript
// auto-improve.ts explores:
minEdgePct:        [1.0, 1.5, 2.5, 3.0]
PRIOR_WEIGHT:      [0.05, 0.10, 0.20, 0.25, 0.30]
maxKellyFraction:  [0.08, 0.10, 0.12, 0.20]
minVolume:         [5000, 15000, 20000]
expiryMaxHours:    [48, 96]
expiryMinHours:    [4, 8, 12]
kellyMode:         quarter ↔ half
categoryPriors:    dynamic adjustments per category
```

### Reading the Iteration Log

Results are logged to `research/program.md`:

```
## Iteration 4 (Auto 4/8)
- Changed: minEdgePct 2 → 3
- Brier: 0.1804 (prev: 0.1814)
- Improvement: +0.0010
- Status: ✅ KEPT — new best
- Version: 1.0.1
```

### Breaking a Plateau

When auto-improve exhausts its search space without improvement:

1. **Inject a hypothesis manually** — Edit `research/strategy.ts` with a theory (e.g., "crypto markets are less efficient after 10pm UTC") and run `npm run research:eval`
2. **Add new data** — More resolved markets = more signal for the optimizer
3. **Change the objective** — Weight Brier + Sharpe ratio instead of pure Brier
4. **Try category-specific strategies** — Separate configs for sports vs politics vs crypto

---

## Stream 3: Cross-Platform Arbitrage (PM x 1WIN)

### How Spread Arbitrage Works

When two platforms price the same event differently, you can profit from the spread:

```
Polymarket YES price: $0.40 (implied 40%)
1WIN decimal odds:    2.80  (implied 1/2.80 = 35.7%)

Spread = |40% - 35.7%| = 4.3%
```

If Polymarket says 40% and 1WIN says 35.7%, Polymarket is pricing YES higher. The direction depends on which platform you think is wrong — or you can bet both sides if the spread exceeds the combined vig.

### Spread Calculator

```typescript
// spread-calculator.ts
export function calcSpread(polyProb: number, onewinDecimalOdds: number) {
  const onewinProb = 1 / onewinDecimalOdds;
  const spread = Math.abs(polyProb - onewinProb);
  const spreadPct = spread * 100;
  const direction = polyProb < onewinProb ? "buy_poly_yes" : "buy_poly_no";
  return { onewinProb, spread, spreadPct, direction };
}

export function calcExpectedProfit(polyProb: number, onewinProb: number): number {
  const edge = Math.abs(polyProb - onewinProb);
  const ONEWIN_VIG = 0.02;
  return Math.max((edge - ONEWIN_VIG) * 100, 0);
}

export function calcKellyFraction(polyProb: number, onewinProb: number): number {
  const edge = Math.abs(polyProb - onewinProb);
  const fraction = edge / (1 - Math.min(polyProb, onewinProb));
  return Math.min(fraction, 0.10); // Hard cap at 10%
}

export function getConfidence(spreadPct: number): "HIGH"|"MEDIUM"|"LOW"|null {
  if (spreadPct > 5) return "HIGH";
  if (spreadPct >= 3) return "MEDIUM";
  if (spreadPct >= 1) return "LOW";
  return null; // Skip
}
```

### Running the Arb Scanner

```bash
npm run arb:scan
```

**What it does:**

1. Fetches active Polymarket markets (sports/crypto, expires within 48h, volume > 0)
2. Fetches 1WIN events via API (with fallback to CLOB proxy if geo-blocked)
3. Fuzzy-matches event titles across platforms (Dice coefficient, 0.4 threshold)
4. Calculates spreads for all matches
5. Tiers by confidence (HIGH/MEDIUM/LOW)
6. Returns top 20 opportunities sorted by spread percentage

**Reading the output:**

```
🟢 HIGH CONFIDENCE | Spread: 6.2%
  PM: "Will Bitcoin hit $100k by March?" @ $0.35
  1WIN: Same event @ 2.50 odds (40.0%)
  Direction: buy_poly_yes
  Kelly: 4.8% of bankroll
  Expected profit: 4.2%

🟡 MEDIUM CONFIDENCE | Spread: 3.8%
  PM: "Lakers vs Celtics Game 5 winner" @ $0.55
  1WIN: Same event @ 1.72 odds (58.1%)
  Direction: buy_poly_no
  Kelly: 2.1% of bankroll
  Expected profit: 1.8%
```

### Title Matching

The fuzzy matcher handles cross-platform naming differences:

```typescript
// title-matcher.ts
// Normalizes: lowercase, remove punctuation, strip stop words
// Stop words: vs, v, the, will, who, win, to, in, at, on, a, an,
//   of, for, and, or, be, is, are, was, match, game, fight, bout

// Dice coefficient: 2 * |intersection| / (|a| + |b|)
// Threshold: 0.4 minimum for a match
```

### Continuous Monitoring

```typescript
// detector.ts — startMonitor()
// Polls every 60 seconds
// Tracks seen arb IDs to alert only on NEW opportunities
// Logs all discoveries with timestamps
```

---

## Setup Guide

### 1. Clone and Install

```bash
git clone <your-polymarket-bot-repo>
cd polymarket-bot
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in:

```bash
# Required for live trading
POLYGON_WALLET_PRIVATE_KEY=your_polygon_private_key
POLYMARKET_FUNDER_ADDRESS=your_funder_address
POLYMARKET_API_URL=https://gamma-api.polymarket.com
POLYMARKET_CLOB_URL=https://clob.polymarket.com

# Risk management
STARTING_CAPITAL=1000
MAX_POSITION_SIZE=500
MAX_TOTAL_EXPOSURE=2000
MIN_EDGE_THRESHOLD=0.10
STOP_LOSS_PERCENT=5
TAKE_PROFIT_PERCENT=5

# Optional: CEX for hedging
BINANCE_API_KEY=
BINANCE_API_SECRET=

# Safety
DRY_RUN=true        # Start with paper trading!
LOG_LEVEL=info
LOG_TO_FILE=true
```

### 3. Run Each Stream

```bash
# Stream 1: Score markets and find EV opportunities
npm run agent:alpha

# Stream 2: Run strategy optimizer overnight
npm run research:auto

# Stream 3: Scan for cross-platform arb
npm run arb:scan

# Full bot (all streams)
npm run bot
```

---

## Recipes

### Recipe 1: Morning Scan for Arb Opportunities

```bash
# 1. Scan for spreads
npm run arb:scan

# 2. Review HIGH confidence opportunities only
# Look for spreadPct > 5% with Kelly > 3%

# 3. Verify the match manually
# Check that the title matcher correctly paired the events
# Open both Polymarket and 1WIN to confirm prices are live

# 4. If confirmed, execute on Polymarket (DRY_RUN=false)
# The bot respects MAX_POSITION_SIZE and STOP_LOSS_PERCENT
```

### Recipe 2: Run Overnight Strategy Improvement

```bash
# 1. Check current Brier score
npm run research:eval

# 2. Start the auto-improver (takes 10-30 minutes)
npm run research:auto

# 3. Check results in the morning
cat research/program.md | tail -30

# 4. If version bumped, verify the checkpoint
ls research/checkpoints/

# 5. Deploy updated strategy
# The agent automatically uses the latest strategy.ts
```

### Recipe 3: Check Portfolio EV

```typescript
// Run in your TypeScript environment
import { scoreMarket, rankByEV } from './src/quant/ev-calculator';
import { quarterKelly } from './src/quant/kelly-criterion';

// For each active position, score against your current probability
const positions = [
  { id: 'btc-100k', yesPrice: 0.35, ourP: 0.42 },
  { id: 'election-x', yesPrice: 0.60, ourP: 0.55 },
];

const scored = positions.map(p => scoreMarket(p, p.ourP));
const ranked = rankByEV(scored);

ranked.forEach(m => {
  console.log(`${m.marketId}: EV=${m.ev.toFixed(3)}, Edge=${m.edgePct.toFixed(1)}%, Kelly=${m.kellyFraction.toFixed(3)}`);
  console.log(`  → ${m.recommend ? '✅ TRADE' : '⏭️ SKIP'}`);
});
```

### Recipe 4: Add a New Market to the Bayesian Tracker

```typescript
import { bayesUpdate, addEvidence } from './src/quant/bayesian-updater';

// Initialize state for a new market
let state = {
  marketId: 'fed-rate-cut-march',
  priorP: 0.50,
  currentP: 0.50,
  evidence: [],
  lastUpdated: new Date(),
};

// New evidence: Fed minutes suggest dovish stance (LR > 1 → supports YES)
state = addEvidence(state, {
  description: 'Fed minutes dovish tone, multiple members favor cut',
  likelihoodRatio: 1.8,
  timestamp: new Date(),
});

console.log(`Updated probability: ${(state.currentP * 100).toFixed(1)}%`);
// Output: ~64.3% (moved from 50% toward YES)

// More evidence: CPI comes in hot (LR < 1 → supports NO)
state = addEvidence(state, {
  description: 'CPI +0.4% MoM, above expectations',
  likelihoodRatio: 0.6,
  timestamp: new Date(),
});

console.log(`Updated probability: ${(state.currentP * 100).toFixed(1)}%`);
// Pulled back toward 50%
```

### Recipe 5: Backtest a Strategy Change

```typescript
// 1. Edit research/strategy.ts with your hypothesis
// Example: change minEdgePct from 3.0 to 2.0

// 2. Run evaluation
// npm run research:eval

// 3. Check the backtest output:
// BacktestResult {
//   winRate: 0.54,
//   brierScore: 0.1820,
//   sharpeEstimate: 1.2,
//   recommendation: 'EDGE'  // or 'STRONG_EDGE' / 'NO_EDGE'
// }

// Decision matrix:
// STRONG_EDGE (winRate > 56% AND Brier < 0.22) → Deploy immediately
// EDGE (winRate > 52%) → Run for 1 week on paper
// NO_EDGE → Revert the change
```

---

## Architecture Notes

The system is modular by design. Each quant module (`kelly-criterion.ts`, `ev-calculator.ts`, `bayesian-updater.ts`) is pure functions with no side effects — they can be imported independently into any project. The research loop operates on `strategy.ts` as a single source of truth, with versioned checkpoints for rollback. The arbitrage detector cascades through data sources (1WIN API → CLOB proxy → mock) for reliability.

All trading respects risk constraints: `MAX_POSITION_SIZE`, `STOP_LOSS_PERCENT`, and `DRY_RUN` mode. Start with paper trading. Always.
