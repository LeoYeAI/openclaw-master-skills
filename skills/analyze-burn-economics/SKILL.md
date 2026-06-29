---
name: analyze-burn-economics
description: >-
  Comprehensive analysis of Uniswap Firepit burn economics: historical burn P&L,
  accumulation trends, fee source breakdown, competitive dynamics, and
  profitability projections. Governance-grade research report. Use when user asks
  "What's the burn economics?", "History of protocol fee burns", or "Average
  profit per burn."
model: opus
allowed-tools:
  - Task(subagent_type:protocol-fee-seeker)
  - mcp__uniswap__get_burn_history
  - mcp__uniswap__get_fee_accumulation_rate
  - mcp__uniswap__get_firepit_state
  - mcp__uniswap__get_tokenjar_balances
  - mcp__uniswap__get_token_price
  - mcp__uniswap__get_token_price_history
---

# Analyze Burn Economics

## Overview

A pure research skill that produces a governance-grade analysis of the Uniswap protocol fee system's burn economics. This skill answers the questions that UNI holders, governance participants, and protocol researchers care about: How profitable have burns been? How are fees trending? What drives accumulation? When should parameters be adjusted?

No execution capability -- this is strictly analytical.

**Why this is 10x better than calling tools individually:**

1. **Cross-referenced historical analysis**: A single `get_burn_history` call returns raw event logs. This skill cross-references each burn with the UNI price at that time (via `get_token_price_history`), the gas cost, and the assets claimed -- producing a per-burn profit/loss table that no single tool can generate.
2. **Trend analysis across time**: By combining accumulation rates with burn history, the agent identifies whether the protocol fee system is becoming more or less profitable over time, whether burn frequency is increasing (more competition), and whether fee composition is shifting.
3. **Governance-relevant projections**: The report includes sensitivity analysis -- how profitability changes with UNI price, threshold adjustments, and fee rate changes. This is the data governance participants need to evaluate parameter proposals.
4. **30+ minutes of manual analysis in one command**: Manually computing per-burn P&L requires querying each burn event, looking up token prices at that block, calculating gas costs, and aggregating. This skill automates the entire research workflow.

## When to Use

Activate when the user says anything like:

- "What's the burn economics?"
- "Show me the history of protocol fee burns"
- "What's the average profit per burn?"
- "When was the last burn?"
- "How profitable is the Firepit?"
- "Analyze protocol fee trends"
- "Burn history and profitability"
- "Is the fee system working well?"
- "Governance analysis of protocol fees"
- "How has burn profitability changed over time?"

**Do NOT use** when the user wants to execute a burn (use `seek-protocol-fees` instead) or wants a real-time monitoring dashboard (use `monitor-tokenjar` instead).

## Parameters

| Parameter            | Required | Default  | How to Extract                                                     |
| -------------------- | -------- | -------- | ------------------------------------------------------------------ |
| chain                | No       | ethereum | Always Ethereum mainnet for TokenJar/Firepit                       |
| days                 | No       | 90       | Lookback period: "last 30 days", "past year" = 365                 |
| include-projections  | No       | true     | "Just history" or "no projections" implies false                   |

## Workflow

```
                     ANALYZE-BURN-ECONOMICS PIPELINE
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │  Step 1: DATA COLLECTION (parallel MCP calls)                       │
  │  ├── get_burn_history — all burns in lookback window                │
  │  ├── get_fee_accumulation_rate — current accumulation dynamics      │
  │  ├── get_firepit_state — current threshold and parameters           │
  │  ├── get_tokenjar_balances — current jar state                      │
  │  ├── get_token_price (UNI) — current UNI price                     │
  │  └── get_token_price_history (UNI) — UNI price over lookback       │
  │          │                                                          │
  │          ▼ (all data feeds into Step 2)                             │
  │                                                                     │
  │  Step 2: ANALYSIS (protocol-fee-seeker in analysis mode)            │
  │  ├── Per-burn P&L calculation                                       │
  │  ├── Burn frequency and timing analysis                             │
  │  ├── Fee source and composition trends                              │
  │  ├── Accumulation rate changes over time                            │
  │  ├── Competitive dynamics (searcher behavior)                       │
  │  └── Output: Historical Analysis Report                             │
  │          │                                                          │
  │          ▼ (if include-projections: true)                           │
  │                                                                     │
  │  Step 3: PROJECTIONS                                                │
  │  ├── Next profitable burn timing                                    │
  │  ├── Expected profit at current rates                               │
  │  ├── Sensitivity to UNI price changes                               │
  │  ├── Impact of threshold parameter changes                          │
  │  └── Output: Projection Report                                      │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

### Step 1: Data Collection (parallel MCP calls)

Make all calls simultaneously for speed:

1. `mcp__uniswap__get_burn_history` with `limit: 100` -- all burns in the lookback window.
2. `mcp__uniswap__get_fee_accumulation_rate` -- current daily/weekly/monthly rates.
3. `mcp__uniswap__get_firepit_state` -- current threshold, nonce, contract parameters.
4. `mcp__uniswap__get_tokenjar_balances` -- current jar contents for context.
5. `mcp__uniswap__get_token_price` for UNI -- current UNI price.
6. `mcp__uniswap__get_token_price_history` for UNI with `interval: "1d"` and `limit` matching the lookback `days` -- UNI price history for cross-referencing burn events.

**Present to user:**

```text
Step 1/3: Data Collection Complete

  Burn events found:   17 burns in last 90 days
  UNI price range:     $5.80 - $8.20 (90d)
  Current UNI price:   $7.00
  Current jar value:   $52,000
  Accumulation rate:   ~$7,400/day

  Analyzing burn economics...
```

### Step 2: Analysis (protocol-fee-seeker)

Delegate to `Task(subagent_type:protocol-fee-seeker)` in analysis mode with all collected data:

```
Produce a comprehensive burn economics analysis report.

Historical data:
- Burn history: {full burn event data from Step 1}
- UNI price history: {daily OHLCV from Step 1}
- Current accumulation rates: {from Step 1}
- Current Firepit state: threshold={threshold}, nonce={nonce}
- Current TokenJar balances: {from Step 1}
- Current UNI price: ${price}
- Lookback period: {days} days

Analysis tasks:
1. For each burn event, calculate:
   - UNI cost at the time of burn (threshold * UNI price at that block)
   - Gas cost (from transaction receipt)
   - Gross value of assets claimed
   - Net profit/loss
   - ROI percentage

2. Compute aggregate statistics:
   - Total burns in period
   - Average profit per burn
   - Median profit per burn
   - Best and worst burns
   - Total value distributed through burns
   - Average time between burns

3. Analyze trends:
   - Is burn profitability increasing or decreasing?
   - Is burn frequency increasing (more competition)?
   - How has fee composition changed? (more WETH vs USDC vs others)
   - Correlation between UNI price and burn profitability

4. Competitive dynamics:
   - How many unique searcher addresses?
   - Are the same addresses burning repeatedly?
   - What profitability level triggers burns? (min ROI observed)

Return a structured analysis report with all metrics.
```

**Present to user after completion:**

```text
Step 2/3: Historical Analysis Complete

  17 burns analyzed over 90 days.
  Total value distributed: $612,000
  Average profit: $18,400/burn (65.7% avg ROI)

  Generating projections...
```

### Step 3: Projections (if enabled)

The agent produces forward-looking projections based on the analysis:

```
Based on the historical analysis, produce projections:

Current state:
- TokenJar value: ${jar_value}
- Accumulation rate: ${daily_rate}/day
- UNI price: ${uni_price}
- Burn threshold: {threshold} UNI
- Burn cost: ${burn_cost}

Projections to compute:
1. Time to next profitable burn (if not already profitable).
2. Expected profit at current accumulation rate (1-day, 3-day, 7-day projections).
3. Sensitivity analysis: how does profitability change if UNI price moves +/-20%?
4. Threshold sensitivity: what if threshold changed to 2,000 or 8,000 UNI?
5. Break-even analysis: at what UNI price does the current jar become unprofitable?
```

## Output Format

### Full Report

```text
Burn Economics Report (Last 90 Days)

  ══════════════════════════════════════
  SUMMARY STATISTICS
  ══════════════════════════════════════
  Total Burns:           17
  Total Value Claimed:   $612,000
  Total UNI Burned:      68,000 UNI ($476,000)
  Total Gas Spent:       $765
  Total Net Profit:      $135,235
  Average Profit/Burn:   $7,955
  Median Profit/Burn:    $6,200
  Average ROI:           65.7%
  Average Burn Interval: 5.3 days

  ══════════════════════════════════════
  BURN HISTORY
  ══════════════════════════════════════
  Date         Jar Value  UNI Cost   Gas    Net Profit  ROI     Searcher
  2026-02-03   $52,000    $28,000    $45    $23,955     85.4%   0xab..12
  2026-01-28   $41,200    $27,200    $38    $13,962     51.3%   0xcd..34
  2026-01-22   $38,500    $26,800    $42    $11,658     43.5%   0xab..12
  2026-01-17   $35,100    $25,600    $35    $9,465      37.0%   0xef..56
  ...          ...        ...        ...    ...         ...     ...
  (17 burns total)

  Best Burn:   2026-02-03 — $23,955 profit (85.4% ROI)
  Worst Burn:  2025-12-15 — $1,200 profit (4.3% ROI)

  ══════════════════════════════════════
  FEE COMPOSITION
  ══════════════════════════════════════
  Token     Avg Share    Trend (90d)
  WETH      35.2%        Stable
  USDC      27.8%        Growing (+3.2%)
  USDT      16.5%        Stable
  WBTC      11.4%        Declining (-1.8%)
  DAI       6.1%         Declining (-0.5%)
  Other     3.0%         Growing (+1.1%)

  ══════════════════════════════════════
  ACCUMULATION TRENDS
  ══════════════════════════════════════
  Current Rate:    $7,400/day
  30d Avg Rate:    $6,800/day
  90d Avg Rate:    $6,200/day
  Trend:           INCREASING (+19.4% over 90 days)

  Rate by Source (estimated):
    V3 Fees:       ~$4,200/day  (56.8%)
    V4 Fees:       ~$1,400/day  (18.9%)
    UniswapX:      ~$1,100/day  (14.9%)
    V2 Fees:       ~$500/day    (6.8%)
    Unichain:      ~$200/day    (2.7%)

  ══════════════════════════════════════
  COMPETITIVE DYNAMICS
  ══════════════════════════════════════
  Unique Searchers:     4 addresses (last 90d)
  Most Active:          0xab..12 (8 of 17 burns, 47%)
  Min ROI at Burn:      4.3% (some searchers burn at thin margins)
  Avg ROI at Burn:      65.7%
  Competition Trend:    Increasing (2 new searchers in last 30d)

  ══════════════════════════════════════
  PROJECTIONS
  ══════════════════════════════════════
  Current Jar:     $52,000 (PROFITABLE — $23,955 net)
  Next 10% ROI:    Already exceeded
  Next 100% ROI:   ~0.5 days

  If jar were empty today:
    Break-even:    ~3.8 days ($28,045 / $7,400/day)
    10% ROI:       ~4.2 days
    50% ROI:       ~5.7 days

  UNI Price Sensitivity (current jar $52,000):
    UNI at $5.60 (-20%):  Burn cost $22,445 → Profit $29,555 (131.7% ROI)
    UNI at $7.00 (now):   Burn cost $28,045 → Profit $23,955 (85.4% ROI)
    UNI at $8.40 (+20%):  Burn cost $33,645 → Profit $18,355 (54.6% ROI)
    UNI at $13.00 (break-even): Burn cost $52,045 → Profit -$45

  Threshold Sensitivity (current UNI price $7.00):
    2,000 UNI:  Burn cost $14,045 → Profit $37,955 (270.2% ROI)
    4,000 UNI:  Burn cost $28,045 → Profit $23,955 (85.4% ROI)  ← current
    8,000 UNI:  Burn cost $56,045 → Profit -$4,045 (NOT PROFITABLE)

  ══════════════════════════════════════
  GOVERNANCE IMPLICATIONS
  ══════════════════════════════════════
  - The fee system is healthy: accumulation rate is growing (+19.4% over 90d),
    driven primarily by V3 and emerging V4 volume.
  - Current threshold (4,000 UNI) produces healthy competition with 4 active
    searchers and average 5.3-day burn intervals.
  - Increasing the threshold to 8,000 UNI would make burns unprofitable at
    current rates unless the jar accumulates for ~7.6 days.
  - V4 fee contribution is growing (18.9%) and may overtake V2 within 30 days
    at current trajectory.
```

### Compact Report (no projections)

```text
Burn Economics Summary (Last {days} Days)

  Burns: {count} | Total Distributed: ${total}
  Avg Profit: ${avg_profit}/burn ({avg_roi}% ROI)
  Avg Interval: {days} days
  Accumulation: ${daily_rate}/day (trend: {direction})
  Current Jar: ${jar_value} ({PROFITABLE | NOT_PROFITABLE})
```

## Important Notes

- **Read-only skill.** This skill never executes transactions. It produces analysis only.
- **Historical data depends on burn history depth.** If the Firepit is new or has few burns, the analysis will be limited. The skill reports data availability clearly.
- **UNI price cross-referencing is approximate.** The skill uses daily OHLCV candles to estimate UNI price at each burn time. Intra-day price movements may cause slight P&L inaccuracies.
- **Fee source attribution is estimated.** The TokenJar receives fees from multiple sources but Transfer events don't always indicate the source. Source breakdown is based on known contract addresses and heuristics.
- **Projections assume stable conditions.** Forward projections use current accumulation rates and UNI price. Market conditions, governance changes, or protocol upgrades could invalidate projections.
- **Governance implications are analytical, not prescriptive.** The report presents data-driven observations but does not make governance recommendations.

## Error Handling

| Error                        | User-Facing Message                                                       | Suggested Action                          |
| ---------------------------- | ------------------------------------------------------------------------- | ----------------------------------------- |
| No burn history              | "No burns found in the last {days} days."                                 | Increase lookback period                  |
| Insufficient burns           | "Only {count} burns found. Analysis may be limited."                      | Increase lookback or accept limited data  |
| UNI price history unavailable| "Could not retrieve UNI price history. Per-burn P&L will be approximate." | Proceed with current price as fallback    |
| Accumulation data sparse     | "Limited accumulation data. Rate estimates may be imprecise."             | Try a larger lookback window              |
| Token price unavailable      | "Could not price {token}. Some jar values may be incomplete."             | Token may be exotic or illiquid           |
| RPC connection failed        | "Cannot connect to Ethereum RPC. Analysis unavailable."                   | Check RPC configuration                   |
| Lookback too large           | "Lookback of {days} days exceeds available data."                         | Reduce lookback period                    |
