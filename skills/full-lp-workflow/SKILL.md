---
name: full-lp-workflow
description: >-
  Full LP workflow from opportunity scanning to position entry. Autonomously
  finds the best LP opportunity, designs a strategy, assesses risk, executes
  any needed swaps, enters the position, and reports portfolio impact. Use when
  user has capital and wants end-to-end LP management. Most complex multi-agent
  orchestration in the system.
model: opus
allowed-tools:
  - Task(subagent_type:opportunity-scanner)
  - Task(subagent_type:lp-strategist)
  - Task(subagent_type:risk-assessor)
  - Task(subagent_type:trade-executor)
  - Task(subagent_type:liquidity-manager)
  - Task(subagent_type:portfolio-analyst)
  - mcp__uniswap__check_safety_status
  - mcp__uniswap__get_agent_balance
---

# Full LP Workflow

## Overview

This is the most complex multi-agent orchestration in the system. It turns a single intent -- "I have $20K, find me the best yield" -- into a fully researched, risk-assessed, optimally-structured LP position through a 6-agent pipeline.

**Why this is 10x better than calling agents individually:**

1. **End-to-end automation**: Manually, you'd need to scan opportunities, research pools, design a strategy, assess risk, potentially swap tokens, add liquidity, and verify -- each requiring different tools and expertise. This does it all in one command.
2. **Intelligent pipeline with compound context**: Each agent builds on all prior agents' findings. The lp-strategist doesn't just get a token pair -- it gets the opportunity-scanner's full analysis of why this pool is optimal. The risk-assessor evaluates the actual strategy designed by the lp-strategist, not a generic assessment.
3. **Two user confirmation points**: Before spending any money (swap) and before committing capital (LP entry), the skill pauses for explicit user approval. You stay in control.
4. **Conditional swap step**: If you don't hold the right tokens for the LP position, the skill automatically handles the token swap -- but only after showing you exactly what it plans to do.
5. **Portfolio impact reporting**: After entering the position, the portfolio-analyst shows you exactly how your portfolio changed, with ongoing monitoring instructions.
6. **Failure recovery at every stage**: If any agent fails mid-pipeline, you see what was accomplished and get recovery suggestions.

## When to Use

Activate when the user says anything like:

- "I have $20K, find the best LP opportunity and enter"
- "Autonomous LP: find yield and enter position"
- "Full LP workflow with $10,000"
- "Find me the best yield and set up a position"
- "I want to LP but don't know where -- find the best option"
- "Put $5K to work in Uniswap -- find the best opportunity"
- "End-to-end LP: scan, strategize, and enter"
- "What's the best LP opportunity right now? Set it up for me"

**Do NOT use** when the user already knows which pool they want (use `manage-liquidity` instead), just wants strategy comparison without execution (use `lp-strategy`), or just wants to scan without entering (use `scan-opportunities`).

## Parameters

| Parameter       | Required | Default    | How to Extract                                                     |
| --------------- | -------- | ---------- | ------------------------------------------------------------------ |
| capital         | Yes      | --         | Total capital to deploy: "$20,000", "10 ETH", "$5K"               |
| chain           | No       | all        | Target chain or "all" for cross-chain scan                         |
| riskTolerance   | No       | moderate   | "conservative", "moderate", "aggressive"                           |
| pairPreference  | No       | --         | Optional token pair preference: "ETH/USDC", "stablecoin pairs"    |
| excludeTokens   | No       | --         | Tokens to exclude: "PEPE, SHIB" (avoid memecoins, etc.)           |
| capitalToken    | No       | auto-detect| What token the capital is in: "USDC", "ETH", auto-detect from wallet |

If the user doesn't provide capital amount, **ask for it** -- never guess how much to deploy.

## Workflow

```
                          FULL LP WORKFLOW PIPELINE
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │  Step 1: SCAN (opportunity-scanner)                                 │
  │  ├── Scan LP opportunities across chains                            │
  │  ├── Filter by risk tolerance and capital size                      │
  │  ├── Rank top 3-5 by risk-adjusted yield                           │
  │  └── Output: Ranked Opportunity List                                │
  │          │                                                          │
  │          ▼ USER CHOICE POINT                                        │
  │  ┌───────────────────────────────────────────────────┐              │
  │  │  Present top opportunities to user.               │              │
  │  │  User picks one OR accepts recommendation (#1).   │              │
  │  └───────────────────────────────────────────────────┘              │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 2: STRATEGIZE (lp-strategist)                                 │
  │  ├── Design optimal strategy for chosen opportunity                 │
  │  ├── Version, fee tier, range width, rebalance plan                 │
  │  ├── Conservative/moderate/optimistic APY estimates                 │
  │  └── Output: LP Strategy Recommendation                             │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 3: RISK CHECK (risk-assessor)                                 │
  │  ├── Receives: opportunity data + strategy details                  │
  │  ├── Evaluates: IL, slippage, liquidity, smart contract             │
  │  ├── Decision: APPROVE / CONDITIONAL / VETO / HARD_VETO            │
  │  └── Output: Risk Assessment Report                                 │
  │          │                                                          │
  │          ▼ CONDITIONAL GATE                                         │
  │  ┌───────────────────────────────────────────────────┐              │
  │  │  APPROVE / COND. APPROVE → Continue               │              │
  │  │  VETO / HARD_VETO → STOP with full report         │              │
  │  └───────────────────────────────────────────────────┘              │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 4: SWAP IF NEEDED (trade-executor) -- CONDITIONAL             │
  │  ├── Check wallet balances vs required tokens                       │
  │  ├── If tokens needed: calculate swap amounts                       │
  │  ├── USER CONFIRMATION #1: "Swap X for Y to prepare for LP?"       │
  │  ├── Execute swap(s) if confirmed                                   │
  │  └── Output: Swap result OR "tokens already held"                   │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 5: ENTER POSITION (liquidity-manager)                         │
  │  ├── USER CONFIRMATION #2: "Add liquidity with these params?"      │
  │  ├── Handle approvals (Permit2)                                     │
  │  ├── Add liquidity at recommended range                             │
  │  ├── Wait for transaction confirmation                              │
  │  └── Output: Position ID, amounts deposited, tick range             │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 6: CONFIRM & REPORT (portfolio-analyst)                       │
  │  ├── Verify position was created successfully                       │
  │  ├── Show portfolio impact (before vs after)                        │
  │  ├── Monitoring instructions                                        │
  │  └── Output: Portfolio Report + Next Steps                          │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

### Step 0: Pre-Flight

Before starting the pipeline:

1. Check safety status via `mcp__uniswap__check_safety_status` -- verify spending limits can accommodate the capital amount.
2. Check wallet balance via `mcp__uniswap__get_agent_balance` on the target chain(s) -- verify the wallet has the stated capital.
3. If either check fails, stop and inform the user before wasting agent compute.

### Step 1: Scan Opportunities (opportunity-scanner)

Delegate to `Task(subagent_type:opportunity-scanner)` with:

```
Scan for LP opportunities with these parameters:
- Available capital: {capital}
- Chains: {chain or "all supported chains"}
- Risk tolerance: {riskTolerance}
- Type: "lp" (LP opportunities only)
- Minimum TVL: $50,000
- Top N: 5

Additional filters:
- Pair preference: {pairPreference or "none"}
- Exclude tokens: {excludeTokens or "none"}

Return the top 5 LP opportunities ranked by risk-adjusted yield.
Each opportunity must include fee APY, estimated IL, risk-adjusted yield,
TVL, volume, and risk rating.
```

**Present to user with a choice:**

```text
Step 1/6: Opportunity Scan Complete

  Found 5 LP opportunities (filtered from 200+ pools):

  #  Pool                Chain    Fee APY  Est. IL  Net APY  Risk    TVL
  1  WETH/USDC 0.05%     ETH      21%      -6%      15%     MEDIUM  $332M
  2  WETH/USDC 0.05%     Base     18%      -5%      13%     MEDIUM  $45M
  3  ARB/WETH 0.30%      Arb      35%      -12%     23%     HIGH    $12M
  4  USDC/USDT 0.01%     ETH      8%       -0.1%    7.9%    LOW     $200M
  5  cbETH/WETH 0.05%    Base     12%      -3%      9%      LOW     $28M

  Recommended: #1 (WETH/USDC 0.05% on Ethereum) — best balance of yield and risk

  Which opportunity would you like to pursue? (1-5, or "1" to accept recommendation)
```

**Wait for user selection before proceeding.**

### Step 2: Design Strategy (lp-strategist)

Delegate to `Task(subagent_type:lp-strategist)` with the chosen opportunity:

```
Design an optimal LP strategy for this opportunity:

Opportunity details (from opportunity-scanner):
{Full opportunity data from Step 1 for chosen pool}

LP parameters:
- Capital: {capital}
- Risk tolerance: {riskTolerance}
- Chain: {chain of chosen opportunity}

Provide:
1. Recommended version and fee tier (with rationale)
2. Optimal tick range (lower/upper prices, width %)
3. Conservative/moderate/optimistic APY and IL estimates
4. Rebalance strategy (trigger, frequency, estimated cost)
5. Comparison to the next-best alternative
```

**Present to user:**

```text
Step 2/6: Strategy Designed

  Pool:     WETH/USDC 0.05% (V3, Ethereum)
  Range:    $1,700 - $2,300 (±15%, medium width)
  Expected: 15% net APY (moderate estimate)

  Strategy Details:
    Fee APY (moderate): 21%
    Estimated IL: -6%
    Net APY: 15%
    Rebalance: every 2-3 weeks (trigger: price within 10% of boundary)
    Rebalance cost: ~$15/rebalance on Ethereum

  Proceeding to risk assessment...
```

### Step 3: Risk Assessment (risk-assessor)

Delegate to `Task(subagent_type:risk-assessor)` with compound context:

```
Evaluate risk for this LP strategy:

Operation: add liquidity
Token pair: {token0}/{token1}
Pool: {pool address}
Chain: {chain}
Capital: {capital}
Risk tolerance: {riskTolerance}

Strategy context (from lp-strategist):
{Full strategy recommendation from Step 2}

Opportunity context (from opportunity-scanner):
{Key metrics from Step 1: TVL, volume trend, risk rating}

Evaluate: impermanent loss risk, slippage risk (entry/exit), liquidity risk,
smart contract risk. Provide APPROVE/CONDITIONAL_APPROVE/VETO/HARD_VETO.
```

**Conditional gate (same logic as research-and-trade):**

| Decision             | Action                                                                  |
| -------------------- | ----------------------------------------------------------------------- |
| **APPROVE**          | Present risk summary, proceed to Step 4                                 |
| **CONDITIONAL_APPROVE** | Show conditions, ask user if they accept                             |
| **VETO**             | **STOP.** Show opportunity + strategy + veto reason. Suggest fallbacks. |
| **HARD_VETO**        | **STOP.** Show reason. Non-negotiable.                                  |

**Present to user (APPROVE case):**

```text
Step 3/6: Risk Assessment Passed

  Decision: APPROVE
  Composite Risk: MEDIUM
  IL Risk: MEDIUM (8.2% annual estimate for volatile pair)
  Slippage: LOW (deep pool, entry < 0.1% impact)
  Liquidity: LOW (TVL 6,640x your position)
  Smart Contract: LOW (V3, established pool)

  Proceeding to prepare tokens...
```

### Step 4: Swap If Needed (trade-executor) -- Conditional

Check wallet balances against required token amounts for the LP position:

1. The strategy specifies how much of each token is needed (e.g., 50/50 split for a centered range).
2. Check current wallet holdings via `mcp__uniswap__get_agent_balance`.
3. Calculate what swaps are needed (if any).

**If no swaps needed:**

```text
Step 4/6: Token Preparation — Skipped

  You already hold sufficient WETH and USDC for this position.
  No swaps required.
```

**If swaps needed, present and ask USER CONFIRMATION #1:**

```text
Step 4/6: Token Preparation Required

  Your position needs:
    0.5 WETH  (~$980)
    980 USDC  (~$980)

  You currently hold:
    2.0 WETH  ($3,920)
    0 USDC    ($0)

  Proposed swap:
    Sell 0.5 WETH → Buy ~980 USDC
    Estimated slippage: 0.05%
    Gas: ~$8

  Approve this swap to prepare tokens for LP? (yes/no)
```

**Only execute the swap if the user explicitly confirms.** If the user declines, stop the pipeline and present what was accomplished (scan + strategy + risk assessment).

### Step 5: Enter Position (liquidity-manager)

Present the full LP entry details and ask USER CONFIRMATION #2:

```text
Step 5/6: Ready to Add Liquidity

  Pool:     WETH/USDC 0.05% (V3, Ethereum)
  Deposit:
    0.5 WETH  (~$980)
    980 USDC  (~$980)
    Total:    ~$1,960

  Range:
    Lower: $1,700 (tick -204714)
    Upper: $2,300 (tick -199514)
    Current: $1,963 — IN RANGE
    Width: ±15% (medium)

  Expected Fee APY: ~15-21% (based on 7d pool data)

  Add liquidity with these parameters? (yes/no)
```

**Only proceed if the user confirms.** Then delegate to `Task(subagent_type:liquidity-manager)`:

```
Add liquidity to this pool:

Pool: {pool address}
Chain: {chain}
Version: {version}
Token0: {token0 address} — Amount: {amount0}
Token1: {token1 address} — Amount: {amount1}
Tick lower: {tick_lower}
Tick upper: {tick_upper}

Strategy context:
- Range strategy: {medium/narrow/wide}
- From lp-strategist recommendation

Execute: handle approvals, simulate, route through safety-guardian, add liquidity,
wait for confirmation. Return position ID and actual amounts deposited.
```

### Step 6: Confirm & Report (portfolio-analyst)

Delegate to `Task(subagent_type:portfolio-analyst)` with the new position:

```
Report on the portfolio impact of this new LP position:

New position:
- Position ID: {position_id from Step 5}
- Pool: {pool_address}
- Chain: {chain}
- Tokens deposited: {amounts}
- Tick range: {lower} to {upper}
- Transaction: {tx_hash}

Wallet address: {wallet_address}

Provide:
1. New position details and current status (in-range confirmation)
2. Portfolio impact (if other positions exist, show before/after composition)
3. Total portfolio value across all chains
4. Monitoring recommendations
```

**Present final result:**

```text
Step 6/6: Position Confirmed & Portfolio Updated

  New Position: #456789
  Pool:     WETH/USDC 0.05% (V3, Ethereum)
  Status:   IN RANGE
  Value:    $1,960

  Deposited:
    0.5 WETH  ($980)
    980 USDC  ($980)

  Range:
    $1,700 — $2,300 (current: $1,963)

  Expected Returns:
    Fee APY: 15-21% (moderate-optimistic)
    Est. IL: -5 to -8% annualized
    Net: 9-15% annualized

  Portfolio Impact:
    Total LP Value:  $1,960 (new) + $45,000 (existing) = $46,960
    LP Allocation:   42% WETH, 35% USDC, 23% other
    Chain Split:     85% Ethereum, 15% Base

  ──────────────────────────────────────
  Pipeline Summary
  ──────────────────────────────────────
  Scan:      5 opportunities found, #1 selected
  Strategy:  V3 0.05%, ±15% range, bi-weekly rebalance
  Risk:      APPROVED (MEDIUM composite)
  Swap:      0.5 WETH → 980 USDC (preparation)
  Position:  #456789 — IN RANGE
  Cost:      $15.20 total gas (swap + LP entry)

  Next Steps:
  - Monitor: "How are my positions doing?"
  - Rebalance when needed: "Rebalance position #456789"
  - Collect fees: "Collect fees from position #456789"
```

## Critical Decision Points

These are the moments where the skill must **stop and ask** rather than assume:

| Situation                             | Action                                                           |
| ------------------------------------- | ---------------------------------------------------------------- |
| Capital amount not specified          | Ask: "How much capital would you like to deploy?"                |
| Multiple good opportunities           | Present top 3-5, let user choose                                 |
| Risk-assessor VETO                    | Stop. Show research + strategy + veto reason.                    |
| Swap needed for token preparation     | USER CONFIRMATION #1: show swap details, ask to proceed          |
| Ready to add liquidity                | USER CONFIRMATION #2: show position details, ask to proceed      |
| Capital exceeds safety spending limit | Stop. Show limit. Suggest reducing amount or adjusting limits.   |
| Wallet doesn't have stated capital    | Stop. Show actual balance. Ask to adjust amount.                 |
| Best opportunity is on a different chain than wallet funds | Explain cross-chain situation, suggest bridge or chain choice |

## Partial Completion Recovery

If the pipeline fails mid-way, report what was accomplished and what remains:

```text
LP Workflow — Partial Completion

  Completed:
    [done] Step 1: Scan — 5 opportunities found, #1 selected
    [done] Step 2: Strategy — V3 0.05%, ±15% range designed
    [done] Step 3: Risk — APPROVED (MEDIUM)
    [FAIL] Step 4: Swap — Transaction reverted (insufficient gas)

  Remaining:
    [ ] Step 5: Add liquidity
    [ ] Step 6: Portfolio report

  Recovery Options:
    - Ensure sufficient ETH for gas and retry: "Continue LP workflow"
    - Add liquidity manually with the strategy above: "Add liquidity to WETH/USDC 0.05%"
    - Start over: "Full LP workflow with $X"
```

## Output Format

### Successful Pipeline (all 6 steps)

```text
Full LP Workflow Complete

  Opportunity: {pool_pair} {fee}% on {chain}
  Strategy:    {version}, {range_width} range, {rebalance_frequency} rebalance
  Risk:        {decision} ({composite_risk})
  Position:    #{position_id} — {status}
  Value:       ${total_value}

  Returns (moderate estimate):
    Fee APY: {fee_apy}%
    Est. IL: {il}%
    Net APY: {net_apy}%

  Cost: ${total_gas} gas across {n} transactions

  Pipeline: Scan -> Strategy -> Risk -> Swap -> Enter -> Confirm (all passed)
```

## Important Notes

- **This is the most complex skill.** It orchestrates 6 agents with 2 user confirmation points and a conditional swap step. Each agent receives compound context from all predecessors.
- **Two explicit confirmations**: Before any swap and before adding liquidity. The user must say "yes" at both gates.
- **Conditional swap**: Step 4 only executes if the user doesn't already hold the right tokens. If they do, it's skipped entirely.
- **Chain considerations**: If scanning "all" chains, the best opportunity might be on a chain where the user's funds aren't located. The skill should flag this and suggest bridging or narrowing the chain filter.
- **Gas budget**: On Ethereum, the full pipeline (swap + LP) costs $15-50 in gas. For small positions (< $1K), warn that gas costs significantly eat into returns.
- **Never auto-execute**: Despite being an "autonomous" workflow, every spend of user capital requires explicit confirmation.

## Error Handling

| Error                              | User-Facing Message                                                        | Suggested Action                        |
| ---------------------------------- | -------------------------------------------------------------------------- | --------------------------------------- |
| No opportunities found             | "No LP opportunities match your criteria on {chain}."                      | Broaden chain filter or lower minTVL    |
| Opportunity-scanner fails          | "Opportunity scan failed. Cannot identify LP targets."                     | Try scan-opportunities directly         |
| LP-strategist fails                | "Strategy design failed for {pool}. Scan results preserved."               | Try lp-strategy or optimize-lp directly |
| Risk-assessor VETO                 | "Risk assessment vetoed: {reason}. Strategy: {summary}."                   | Pick a different opportunity or reduce size |
| Risk-assessor HARD_VETO            | "Strategy blocked: {reason}. This cannot be overridden."                   | Choose a lower-risk opportunity         |
| Insufficient balance for swap      | "Not enough {token} to prepare for LP. Have {X}, need {Y}."               | Reduce capital or acquire tokens        |
| Swap execution fails               | "Token swap failed: {reason}. Strategy and risk data preserved."           | Retry or swap manually                  |
| Liquidity add fails                | "Failed to add liquidity: {reason}. Tokens are still in your wallet."      | Retry or use manage-liquidity directly  |
| Position not confirmed             | "Position created but not yet confirmed on-chain. Check back in a moment." | Wait and check with track-performance   |
| Safety spending limit exceeded     | "Capital of ${X} exceeds spending limit of ${Y}."                          | Reduce amount or adjust safety config   |
| Wallet not configured              | "No wallet configured. Cannot execute transactions."                       | Set up wallet with setup-agent-wallet   |
| User declines swap confirmation    | "Token swap cancelled. Strategy preserved — you can proceed manually."     | Use manage-liquidity with manual prep   |
| User declines LP confirmation      | "LP entry cancelled. All prior research is shown above."                   | Adjust parameters and retry             |
