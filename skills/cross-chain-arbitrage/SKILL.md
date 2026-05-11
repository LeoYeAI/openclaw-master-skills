---
name: cross-chain-arbitrage
description: >-
  Find and execute cross-chain arbitrage opportunities. Scans prices across all
  chains, evaluates profitability after all costs (gas, bridge fees, slippage),
  assesses risk, and executes if profitable. Uses ERC-7683 for cross-chain
  settlement. Supports scan-only mode for research without execution.
model: opus
allowed-tools:
  - Task(subagent_type:opportunity-scanner)
  - Task(subagent_type:risk-assessor)
  - Task(subagent_type:cross-chain-executor)
  - Task(subagent_type:portfolio-analyst)
  - mcp__uniswap__check_safety_status
  - mcp__uniswap__get_agent_balance
---

# Cross-Chain Arbitrage

## Overview

This skill automates the discovery and execution of cross-chain arbitrage opportunities -- finding price differences for the same token across Uniswap deployments on different chains and profiting from the spread. It handles the entire pipeline: scanning prices across 11 chains, calculating all-in costs, risk assessment, cross-chain execution via ERC-7683, and profit reporting.

**Why this is 10x better than doing it manually:**

1. **Simultaneous multi-chain price scanning**: Manually checking ETH prices on Ethereum, Base, Arbitrum, Optimism, Polygon, and 6 other chains takes significant effort. The opportunity-scanner does this across all supported chains in seconds.
2. **All-in cost calculation**: The most common arbitrage mistake is ignoring costs. This skill itemizes every cost component (source gas, bridge fee, destination gas, slippage on both sides) and only presents opportunities that are profitable *after* all costs.
3. **Time-sensitivity awareness**: Arbitrage opportunities are ephemeral -- they can disappear in seconds. The skill warns about this throughout and moves quickly, but honestly flags when an opportunity may have closed by the time the user confirms.
4. **Risk-gated execution**: Before any capital moves, the risk-assessor evaluates bridge risk, execution risk, and liquidity. A VETO stops the pipeline.
5. **Scan-only mode**: Not ready to execute? Use scan-only mode to just see what opportunities exist without committing capital.

## When to Use

Activate when the user says anything like:

- "Find ETH arbitrage across chains"
- "Cross-chain arb opportunities"
- "Are there any price differences for WETH across chains?"
- "Profit from price differences"
- "Scan for arbitrage on Base vs Ethereum"
- "Is there an arb opportunity for USDC?"
- "Cross-chain arbitrage with $5K"
- "Just scan for arb -- don't execute" (scan-only mode)

**Do NOT use** when the user wants a same-chain swap (use `execute-swap`), wants to bridge without arbitrage (use `bridge-tokens`), or wants general LP yield opportunities (use `scan-opportunities` or `find-yield`).

## Parameters

| Parameter     | Required | Default         | How to Extract                                                  |
| ------------- | -------- | --------------- | --------------------------------------------------------------- |
| token         | No       | Top 5 tokens    | Token to check: "WETH", "USDC", or scan top tokens by default  |
| chains        | No       | all             | Chains to scan: "all", or specific list like "ethereum, base"   |
| minProfit     | No       | 0.5%            | Minimum net profit threshold after ALL costs                    |
| maxAmount     | No       | --              | Maximum capital to deploy per opportunity                       |
| riskTolerance | No       | moderate        | "conservative", "moderate", "aggressive"                        |
| mode          | No       | execute         | "execute" (full pipeline) or "scan" (scan-only, no execution)   |

If `mode` is "scan" or the user says "just scan" / "don't execute" / "show me opportunities", skip Steps 3-4 and only present the opportunity report.

## Workflow

```
                     CROSS-CHAIN ARBITRAGE PIPELINE
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │  Step 1: SCAN (opportunity-scanner)                                 │
  │  ├── Compare token prices across all chains                         │
  │  ├── Calculate gross profit for each discrepancy                    │
  │  ├── Itemize ALL costs (gas, bridge, slippage)                      │
  │  ├── Filter: only net profit > minProfit                            │
  │  └── Output: Ranked Arbitrage Opportunities                         │
  │          │                                                          │
  │          ▼                                                          │
  │  ┌───────────────────────────────────────────────────┐              │
  │  │  SCAN-ONLY MODE?                                  │              │
  │  │  Yes → Present report, STOP.                      │              │
  │  │  No  → Continue to Step 2.                        │              │
  │  └───────────────────────────────────────────────────┘              │
  │          │                                                          │
  │          ▼ USER SELECTION                                           │
  │  ┌───────────────────────────────────────────────────┐              │
  │  │  Present opportunities to user.                   │              │
  │  │  User picks which opportunity to execute.         │              │
  │  │  WARN: "Opportunity may expire before execution." │              │
  │  └───────────────────────────────────────────────────┘              │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 2: RISK CHECK (risk-assessor)                                 │
  │  ├── Evaluate bridge risk (mechanism, settlement time)              │
  │  ├── Evaluate execution risk (slippage, speed)                      │
  │  ├── Evaluate liquidity on both chains                              │
  │  ├── Decision: APPROVE / VETO / HARD_VETO                          │
  │  └── Output: Risk Assessment                                        │
  │          │                                                          │
  │          ▼ CONDITIONAL GATE                                         │
  │  ┌───────────────────────────────────────────────────┐              │
  │  │  APPROVE → Proceed with confirmation              │              │
  │  │  VETO / HARD_VETO → STOP with report              │              │
  │  └───────────────────────────────────────────────────┘              │
  │          │                                                          │
  │          ▼ USER CONFIRMATION                                        │
  │  ┌───────────────────────────────────────────────────┐              │
  │  │  "Execute this arb? Opportunity may have shifted  │              │
  │  │   since scan. Confirm to proceed."                │              │
  │  └───────────────────────────────────────────────────┘              │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 3: EXECUTE (cross-chain-executor)                             │
  │  ├── Buy on cheaper chain                                           │
  │  ├── Bridge to expensive chain via ERC-7683                         │
  │  ├── Monitor bridge settlement                                      │
  │  ├── (Sell on expensive chain if needed)                            │
  │  └── Output: Execution Report                                       │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 4: REPORT (portfolio-analyst)                                 │
  │  ├── Calculate actual profit/loss after all costs                   │
  │  ├── Compare to projected profit                                    │
  │  └── Output: P&L Report                                             │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

### Step 0: Pre-Flight

Before starting:

1. Check safety status via `mcp__uniswap__check_safety_status`.
2. Check wallet balances via `mcp__uniswap__get_agent_balance` on relevant chains.
3. If wallet has no funds, stop and inform the user.

### Step 1: Scan Opportunities (opportunity-scanner)

Delegate to `Task(subagent_type:opportunity-scanner)` with:

```
Scan for cross-chain arbitrage opportunities:
- Token: {token or "top 5 tokens by volume: WETH, USDC, USDT, WBTC, DAI"}
- Chains: {chains or "all supported chains"}
- Type: "arb" (arbitrage only)
- Minimum net profit: {minProfit}%

For each price discrepancy found, calculate and itemize:
1. Gross price difference (%)
2. Source chain gas cost (USD)
3. Bridge fee (USD)
4. Destination chain gas cost (USD)
5. Slippage estimate on both sides (USD)
6. NET profit after ALL costs (USD and %)

Only include opportunities where net profit > {minProfit}% after all costs.
Rank by net profit. Include time sensitivity assessment for each opportunity.
```

**Present to user:**

```text
Step 1: Arbitrage Scan Complete

  Token: WETH
  Chains scanned: 8 (Ethereum, Base, Arbitrum, Optimism, Polygon, BNB, Avalanche, Blast)

  Opportunities found: 2 (after filtering by {minProfit}% min net profit)

  #  Route                     Gross    Costs         Net Profit  Time Sensitivity
  1  WETH: Arbitrum → Optimism  0.8%    $12 total     $33 (0.66%) EPHEMERAL
     ├── Source gas:   $0.50
     ├── Bridge fee:   $2.00
     ├── Dest gas:     $0.50
     └── Slippage:     $9.00 (both sides)

  2  WETH: Base → Polygon       0.6%    $8 total      $22 (0.44%) EPHEMERAL
     ├── Source gas:   $0.10
     ├── Bridge fee:   $3.00
     ├── Dest gas:     $1.50
     └── Slippage:     $3.40 (both sides)

  WARNING: Arbitrage opportunities are ephemeral. These prices were captured at
  {timestamp} and may change by the time you confirm execution. The actual profit
  may differ from the estimates above.

  No opportunities found for: USDC, USDT, WBTC, DAI (spreads < {minProfit}% after costs)
```

**If mode is "scan"**, stop here:

```text
Arbitrage Scan Report (scan-only mode)

  {same opportunity table as above}

  To execute an opportunity, run: "Cross-chain arb, execute opportunity #1"
  Note: Opportunities are time-sensitive and may no longer be available.
```

**If mode is "execute"**, ask the user which opportunity to pursue.

### Step 2: Risk Assessment (risk-assessor)

Delegate to `Task(subagent_type:risk-assessor)` with the selected opportunity:

```
Evaluate risk for this cross-chain arbitrage:

Operation: cross-chain arbitrage
Token: {token}
Source chain: {source_chain}
Destination chain: {dest_chain}
Amount: {amount or maxAmount}
Risk tolerance: {riskTolerance}

Opportunity details (from opportunity-scanner):
- Gross spread: {gross_pct}%
- Estimated net profit: {net_profit_usd} ({net_pct}%)
- Cost breakdown: {full cost itemization}
- Time sensitivity: ephemeral

Evaluate:
1. Bridge risk (settlement mechanism, historical reliability, available liquidity)
2. Execution risk (can the arb close before we complete? slippage may increase)
3. Liquidity risk (sufficient depth on both chains for the trade size)
4. Smart contract risk (pool ages and versions on both chains)

Key concern: arbitrage opportunities are time-sensitive. Factor in the risk that
the price discrepancy may close during bridge settlement (typically 1-10 minutes).
```

**Conditional gate:**

| Decision        | Action                                                                     |
| --------------- | -------------------------------------------------------------------------- |
| **APPROVE**     | Present risk summary, proceed to user confirmation                         |
| **COND. APPROVE** | Show conditions (e.g., "reduce size"). Ask user.                        |
| **VETO**        | **STOP.** Opportunity too risky at this size/tolerance. Show details.       |
| **HARD_VETO**   | **STOP.** Bridge liquidity insufficient or critical risk. Non-negotiable.  |

**User confirmation (with time-sensitivity warning):**

```text
Step 2: Risk Assessment Passed

  Decision: APPROVE
  Composite Risk: MEDIUM
  Bridge Risk: LOW (ERC-7683, established mechanism)
  Execution Risk: MEDIUM (arb may close during 2-5 min settlement)
  Liquidity: LOW (deep pools on both chains)

  Execute Arbitrage?
    Route:    Buy WETH on Arbitrum → Bridge → (Sell on Optimism)
    Amount:   $5,000
    Est. Profit: $33 (0.66%) after all costs
    Settlement: ~2-5 minutes

    IMPORTANT: This opportunity was scanned at {timestamp} ({N} seconds ago).
    The price discrepancy may have changed. Actual profit may differ from estimate.

  Proceed? (yes/no)
```

### Step 3: Execute (cross-chain-executor)

Delegate to `Task(subagent_type:cross-chain-executor)` with:

```
Execute this cross-chain arbitrage:

Leg 1 (source chain):
- Chain: {source_chain}
- Action: Buy {token} (swap {capital_token} → {token})
- Amount: {amount}
- Pool: {best pool on source chain}

Leg 2 (bridge):
- Bridge {token} from {source_chain} to {dest_chain}
- Mechanism: ERC-7683

Leg 3 (destination chain — if needed):
- Chain: {dest_chain}
- Action: Sell {token} (swap {token} → {capital_token}) — only if the user
  wants to realize profit immediately. Otherwise, hold the {token} on dest chain.

Risk assessment: APPROVED, composite {risk_level}
Time sensitivity: HIGH — execute as quickly as possible.

Monitor bridge settlement and report progress. If bridge takes longer than
expected, warn about potential profit erosion.
```

**Present progress updates during execution:**

```text
Step 3: Executing Arbitrage...

  [1/3] Buying WETH on Arbitrum...
        Bought 2.55 WETH for $5,000 USDC — Tx: 0x...
  [2/3] Bridging WETH to Optimism via ERC-7683...
        Order ID: 0x... — Monitoring settlement...
        Status: PENDING (elapsed: 45s, expected: 2-5 min)
        Status: PENDING (elapsed: 2m 15s)
        Status: SETTLED (elapsed: 3m 02s) — 2.55 WETH received on Optimism
  [3/3] Holding WETH on Optimism (no sell leg — same token, profit realized)
        ✓ Arbitrage complete
```

### Step 4: Report (portfolio-analyst)

Delegate to `Task(subagent_type:portfolio-analyst)` with:

```
Report on the result of this cross-chain arbitrage:

Execution details:
- Token: {token}
- Source: {source_chain} — bought at ${source_price}
- Destination: {dest_chain} — current price ${dest_price}
- Amount: {amount}
- Bridge order: {order_id}
- Transactions: {tx_hashes}

Calculate:
1. Actual gross profit (price difference realized)
2. All actual costs (gas, bridge fees, slippage — from execution receipts)
3. Net profit/loss
4. Comparison to projected profit from scan
5. Portfolio impact
```

**Present final result:**

```text
Step 4: Arbitrage Report

  Route:        WETH: Arbitrum → Optimism
  Amount:       2.55 WETH ($5,000)

  Profit & Loss:
    Gross spread:     $40.00 (0.80%)
    Source gas:        -$0.45
    Bridge fee:        -$1.80
    Dest gas:          -$0.00 (held, no sell)
    Slippage:          -$7.50
    ─────────────────────────
    Net profit:        $30.25 (0.61%)

  vs. Projected:     $33.00 (0.66%) — actual was 8% less due to slippage

  Timing:
    Scan to execution: 45 seconds
    Bridge settlement:  3 min 02 sec
    Total elapsed:      3 min 47 sec

  Portfolio Impact:
    WETH on Optimism:  2.55 WETH ($5,030.25)
    Net gain:          $30.25

  ──────────────────────────────────────
  Pipeline Summary
  ──────────────────────────────────────
  Scan:       2 opportunities found, #1 selected
  Risk:       APPROVED (MEDIUM)
  Execution:  Buy → Bridge → Hold (3 min 47 sec total)
  Result:     +$30.25 net profit (0.61%)
```

## Output Format

### Successful Execution

```text
Cross-Chain Arbitrage Complete

  Route:    {token}: {source_chain} -> {dest_chain}
  Amount:   ${amount}
  Net P&L:  +${net_profit} ({net_pct}%)
  Time:     {total_elapsed}

  Cost Breakdown:
    Gas: ${gas}  Bridge: ${bridge_fee}  Slippage: ${slippage}

  Pipeline: Scan -> Risk -> Execute -> Report (all passed)
```

### Scan-Only Report

```text
Cross-Chain Arbitrage Scan

  Scanned: {n_tokens} tokens across {n_chains} chains
  Found: {n_opportunities} opportunities (> {minProfit}% net profit)

  {opportunity table}

  To execute: "Cross-chain arb, execute opportunity #N"
```

### Vetoed

```text
Cross-Chain Arbitrage -- Risk Vetoed

  Opportunity: {token} {source} -> {dest} ({gross_spread}% gross)
  Risk: VETOED — {reason}

  {risk dimension details}

  Pipeline: Scan -> Risk (VETOED) -- No execution.
```

## Important Notes

- **Arbitrage opportunities are ephemeral.** By the time the user reads the scan results and confirms, the price discrepancy may have closed. The skill warns about this prominently and does not guarantee profits.
- **All-in cost calculation is critical.** Never present gross spread as profit. Always itemize and subtract: source gas, bridge fee, destination gas, slippage on both sides. An opportunity showing 0.8% gross might be 0.2% net (or even negative).
- **Bridge settlement time is the main risk.** During the 1-10 minute bridge settlement, the price on the destination chain can move, eliminating or even reversing the profit. The risk-assessor factors this in.
- **Scan-only mode is the safe default.** If unsure whether the user wants to execute, default to scan-only. They can always say "execute #1" afterward.
- **Not every scan will find opportunities.** Well-arbitraged tokens (WETH, USDC) rarely have spreads > 0.5% after costs. Set expectations accordingly.
- **Gas costs matter more for small amounts.** A $100 arb with $15 in total costs is barely profitable. Warn about this for small trade sizes.
- **This is NOT risk-free.** Despite the word "arbitrage," cross-chain arb carries real risk: bridge failure, price movement during settlement, smart contract risk. Always present it as a risky activity.

## Error Handling

| Error                            | User-Facing Message                                                              | Suggested Action                          |
| -------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------- |
| No opportunities found           | "No arb opportunities above {minProfit}% net profit across {chains}."            | Lower minProfit or try different tokens   |
| Opportunity expired              | "Price discrepancy has closed since scan. Opportunity no longer profitable."      | Re-scan for fresh opportunities           |
| Risk-assessor VETO               | "Risk assessment vetoed: {reason}."                                              | Try smaller amount or different route     |
| Risk-assessor HARD_VETO          | "Blocked: {reason}. Bridge liquidity may be insufficient."                       | Cannot proceed with this opportunity      |
| Bridge failed                    | "Bridge operation failed. Funds should remain on {source_chain}."                | Check source wallet balance               |
| Bridge stuck                     | "Bridge settlement delayed ({elapsed} vs {expected}). Monitoring..."             | Wait or check order ID manually           |
| Source chain swap failed          | "Failed to buy {token} on {source_chain}: {reason}."                            | Check balance and gas                     |
| Insufficient balance             | "Not enough {token} on {source_chain}: have ${X}, need ${Y}."                   | Reduce amount or bridge funds first       |
| Safety limit exceeded            | "Trade amount exceeds safety spending limits."                                   | Reduce amount or adjust limits            |
| Wallet not configured            | "No wallet configured for transactions."                                         | Set up wallet with setup-agent-wallet     |
| User declines confirmation       | "Arbitrage cancelled. Scan results shown above for reference."                   | No action needed                          |
| Profit less than projected       | "Actual profit (${X}) was less than projected (${Y}) due to price movement."     | Expected for ephemeral opportunities      |
| Negative profit (loss)           | "This trade resulted in a loss of ${X} due to price movement during settlement." | Inherent risk of cross-chain arbitrage    |
