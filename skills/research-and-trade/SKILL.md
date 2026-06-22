---
name: research-and-trade
description: >-
  Research a token and execute a trade if it passes due diligence. Autonomous
  research-to-trade pipeline: researches the token, evaluates risk, and only
  trades if the risk assessment approves. Stops and reports if risk is too high.
  Use when user wants "research X and buy if it looks good" or "due diligence
  then trade."
model: opus
allowed-tools:
  - Task(subagent_type:token-analyst)
  - Task(subagent_type:pool-researcher)
  - Task(subagent_type:risk-assessor)
  - Task(subagent_type:trade-executor)
  - mcp__uniswap__check_safety_status
---

# Research and Trade

## Overview

This is the autonomous research-to-execution pipeline. Instead of manually calling four different agents and wiring their outputs together, this skill runs the full expert workflow in one command: research a token, find the best pool, assess risk, and -- only if the risk assessment approves -- execute the trade.

**Why this is 10x better than calling agents individually:**

1. **Compound context**: Each agent receives the accumulated findings from all prior agents. The risk-assessor doesn't just evaluate a swap in isolation -- it sees the token-analyst's liquidity warnings, the pool-researcher's depth analysis, and the exact trade size, enabling a far richer risk assessment than standalone invocation.
2. **Automatic risk gating**: A VETO at any stage short-circuits the pipeline immediately. No wasted gas, no wasted time, and you get a full explanation of why.
3. **Single command for a 4-step expert workflow**: Manually coordinating token research, pool selection, risk evaluation, and trade execution takes significant time and expertise. This compresses it into one natural-language request.
4. **Progressive disclosure**: You see each stage's findings as they complete, not just a final result. If the pipeline stops at risk assessment, you still get the full research report.

## When to Use

Activate when the user says anything like:

- "Research UNI and buy if it looks good"
- "Due diligence on AAVE then trade"
- "Investigate and trade ARB"
- "Should I buy LINK? If so, do it"
- "Is PEPE safe to trade? Buy $500 worth if yes"
- "Research X, assess risk, and swap if it passes"
- "Autonomous trade: research then execute"
- "Check out TOKEN and buy some if the risk is acceptable"

**Do NOT use** when the user just wants research without trading (use `research-token` instead) or just wants to execute a swap without research (use `execute-swap` instead).

## Parameters

| Parameter     | Required | Default    | How to Extract                                                     |
| ------------- | -------- | ---------- | ------------------------------------------------------------------ |
| token         | Yes      | --         | Token to research and potentially buy: "UNI", "AAVE", or 0x addr  |
| amount        | Yes      | --         | Trade size: "$500", "1 ETH worth", "0.5 ETH"                      |
| chain         | No       | ethereum   | Target chain: "ethereum", "base", "arbitrum"                       |
| riskTolerance | No       | moderate   | "conservative", "moderate", "aggressive"                           |
| action        | No       | buy        | "buy" (swap into token) or "sell" (swap out of token)              |
| payWith       | No       | WETH       | Token to spend: "WETH", "USDC", etc.                              |

If the user doesn't provide an amount, **ask for it** -- never guess a trade size.

## Workflow

```
                          RESEARCH-AND-TRADE PIPELINE
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │  Step 1: RESEARCH (token-analyst)                                   │
  │  ├── Token metadata, liquidity, volume, risk factors                │
  │  ├── Cross-chain presence                                           │
  │  └── Output: Token Research Report                                  │
  │          │                                                          │
  │          ▼ (feeds into Step 2)                                      │
  │                                                                     │
  │  Step 2: POOL ANALYSIS (pool-researcher)                            │
  │  ├── Find all pools for {token}/{payWith} on {chain}                │
  │  ├── Rank by fee APY, depth, utilization                            │
  │  ├── Analyze depth at trade size (can it handle $X?)                │
  │  └── Output: Pool Research Report + Best Pool Selection             │
  │          │                                                          │
  │          ▼ (feeds into Step 3 with COMPOUND CONTEXT)                │
  │                                                                     │
  │  Step 3: RISK ASSESSMENT (risk-assessor)                            │
  │  ├── Receives: token risks + pool risks + trade size + slippage     │
  │  ├── Evaluates: slippage, liquidity, smart contract, token risk     │
  │  ├── Decision: APPROVE / CONDITIONAL_APPROVE / VETO / HARD_VETO    │
  │  └── Output: Risk Assessment Report                                 │
  │          │                                                          │
  │          ▼ CONDITIONAL GATE                                         │
  │  ┌───────────────────────────────────────────────────┐              │
  │  │  APPROVE         → Proceed to Step 4              │              │
  │  │  COND. APPROVE   → Show conditions, ask user      │              │
  │  │  VETO            → STOP. Show research + reason.  │              │
  │  │  HARD VETO       → STOP. Non-negotiable.          │              │
  │  └───────────────────────────────────────────────────┘              │
  │          │ (only if APPROVE or user confirms CONDITIONAL)           │
  │          ▼                                                          │
  │                                                                     │
  │  Step 4: USER CONFIRMATION                                          │
  │  ├── Present: research summary + risk score + swap quote            │
  │  ├── Ask: "Proceed with this trade?"                                │
  │  └── User must explicitly confirm                                   │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 5: EXECUTE (trade-executor)                                   │
  │  ├── Execute swap through safety-guardian pipeline                  │
  │  ├── Monitor transaction confirmation                               │
  │  └── Output: Trade Execution Report                                 │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

### Step 1: Research (token-analyst)

Delegate to `Task(subagent_type:token-analyst)` with:

- Token symbol or address
- Target chain
- Request: full due diligence report

**What to pass to the agent:**

```
Research this token for a potential trade:
- Token: {token}
- Chain: {chain}
- Trade size: {amount}

Provide a full due diligence report: liquidity across all pools, volume profile
(24h/7d/30d), risk factors, and a trading recommendation with maximum trade size
at < 1% price impact.
```

**Present to user after completion:**

```text
Step 1/5: Token Research Complete

  Token: UNI (Uniswap) on Ethereum
  Total Liquidity: $85M across 24 pools
  24h Volume: $15M | 7d Volume: $95M
  Volume Trend: Stable
  Risk Factors: None significant
  Max Trade (< 1% impact): $2.5M

  Proceeding to pool analysis...
```

**Gate check:** If the token-analyst reports critical risk factors (total liquidity < $100K, no pools found, token not verified), present findings and ask the user if they want to continue before proceeding.

### Step 2: Pool Analysis (pool-researcher)

Delegate to `Task(subagent_type:pool-researcher)` with the token research output:

```
Find the best pool for trading {token}/{payWith} on {chain}.

Context from token research:
- Total liquidity: {from Step 1}
- Dominant pool: {from Step 1}
- Risk factors: {from Step 1}

Trade details:
- Trade size: {amount}
- Direction: {action} (buying/selling {token})

Analyze all pools for this pair across fee tiers. For each pool, report:
fee APY, TVL, liquidity depth at the trade size, and price impact estimate.
Recommend the best pool for this specific trade.
```

**Present to user after completion:**

```text
Step 2/5: Pool Analysis Complete

  Best Pool: WETH/UNI 0.3% (V3, Ethereum)
  Pool TVL: $42M
  Price Impact: ~0.3% for your trade size
  Fee Tier: 0.3% (3000 bps)

  Proceeding to risk assessment...
```

### Step 3: Risk Assessment (risk-assessor)

Delegate to `Task(subagent_type:risk-assessor)` with **compound context** from Steps 1 and 2:

```
Evaluate risk for this proposed swap:

Operation: swap {amount} {payWith} for {token}
Pool: {best pool from Step 2}
Chain: {chain}
Risk tolerance: {riskTolerance}

Token research context (from token-analyst):
{Full token research summary from Step 1}

Pool analysis context (from pool-researcher):
{Full pool analysis from Step 2}

Evaluate all applicable risk dimensions: slippage, liquidity, smart contract risk.
Provide a clear APPROVE / CONDITIONAL_APPROVE / VETO / HARD_VETO decision.
```

**Conditional gate logic after risk-assessor returns:**

| Decision             | Action                                                                               |
| -------------------- | ------------------------------------------------------------------------------------ |
| **APPROVE**          | Present risk summary, proceed to Step 4 (user confirmation)                          |
| **CONDITIONAL_APPROVE** | Show conditions (e.g., "split into 2 tranches"). Ask user: "Accept conditions?"   |
| **VETO**             | **STOP.** Show full research report + risk assessment + veto reason. Suggest alternatives. |
| **HARD_VETO**        | **STOP.** Show reason. Non-negotiable -- do not offer to proceed.                    |

**Present to user (APPROVE case):**

```text
Step 3/5: Risk Assessment Complete

  Decision: APPROVE
  Composite Risk: LOW
  Slippage Risk: LOW (0.3% estimated)
  Liquidity Risk: LOW (pool TVL 840x trade size)
  Smart Contract Risk: LOW (V3, 18-month-old pool)

  Ready for your confirmation...
```

**Present to user (VETO case):**

```text
Step 3/5: Risk Assessment -- VETOED

  Decision: VETO
  Reason: Price impact of 4.2% exceeds moderate risk tolerance (max 2%)

  Research Summary:
    Token: SMALLCAP ($180K total liquidity)
    Best Pool: WETH/SMALLCAP 1% (V3, $95K TVL)
    Your trade size ($5,000) represents 5.3% of pool TVL

  Suggestions:
    - Reduce trade size to < $1,000 for acceptable slippage
    - Use a limit order instead: "Submit limit order for SMALLCAP"
    - Try a different chain if more liquidity exists elsewhere

  Pipeline stopped. No trade executed.
```

### Step 4: User Confirmation

Before executing any trade, present a clear summary and ask for explicit confirmation:

```text
Trade Confirmation Required

  Research: UNI — $85M liquidity, stable volume, no risk factors
  Risk: APPROVED (LOW composite risk)

  Swap Details:
    Sell:  0.5 WETH (~$980)
    Buy:   ~28.5 UNI
    Pool:  WETH/UNI 0.3% (V3, Ethereum)
    Impact: ~0.3%
    Gas:   ~$8 estimated

  Proceed with this trade? (yes/no)
```

**Only proceed to Step 5 if the user explicitly confirms.**

### Step 5: Execute (trade-executor)

Delegate to `Task(subagent_type:trade-executor)` with the full pipeline context:

```
Execute this swap:
- Sell: {amount} {payWith}
- Buy: {token}
- Pool: {best pool address from Step 2}
- Chain: {chain}
- Slippage tolerance: {derived from risk assessment}
- Risk assessment: APPROVED, composite risk {level}

The token has been researched (liquidity: {X}, volume: {Y}) and risk-assessed
(slippage: {Z}, liquidity: {W}). Proceed with execution through the safety pipeline.
```

**Present final result:**

```text
Step 5/5: Trade Executed

  Sold:     0.5 WETH ($980.00)
  Received: 28.72 UNI ($985.50)
  Pool:     WETH/UNI 0.3% (V3, Ethereum)
  Slippage: 0.28% (within tolerance)
  Gas:      $7.20
  Tx:       https://etherscan.io/tx/0x...

  ──────────────────────────────────────
  Pipeline Summary
  ──────────────────────────────────────
  Research:  UNI — $85M liquidity, stable, no risk flags
  Pool:      WETH/UNI 0.3% — best depth for trade size
  Risk:      APPROVED (LOW)
  Execution: Success — 28.72 UNI received
  Total cost: $987.20 (trade + gas)
```

## Output Format

### Successful Pipeline (all 5 steps)

```text
Research and Trade Complete

  Token: {symbol} ({name}) on {chain}
  Research: {1-line summary from token-analyst}
  Pool: {pool pair} {fee}% ({version}, {chain})
  Risk: {decision} ({composite_risk})

  Trade:
    Sold:     {amount} {payWith} (${usd_value})
    Received: {amount} {token} (${usd_value})
    Impact:   {slippage}%
    Gas:      ${gas_cost}
    Tx:       {explorer_link}

  Pipeline: Research -> Pool -> Risk -> Confirm -> Execute (all passed)
```

### Vetoed Pipeline (stopped at risk)

```text
Research and Trade -- Risk Vetoed

  Token: {symbol} ({name}) on {chain}
  Research: {1-line summary}
  Pool: {best pool found}
  Risk: VETOED — {reason}

  Details:
    {risk dimension scores}

  Suggestions:
    - {mitigation 1}
    - {mitigation 2}

  Pipeline: Research -> Pool -> Risk (VETOED) -- No trade executed.
```

## Important Notes

- **This skill always researches first.** It never skips to trading. If the user just wants a quick swap without research, redirect them to `execute-swap`.
- **Risk gating is non-negotiable for HARD_VETO.** If the risk-assessor issues a HARD_VETO (unverified token, pool TVL < $1K, price impact > 10%), the pipeline stops. The user cannot override this.
- **VETO is informational.** For a regular VETO, present the full research and explain why. The user can then choose to use `execute-swap` directly if they want to proceed at their own risk -- but this skill will not do it.
- **Compound context is the key differentiator.** The risk-assessor is dramatically more useful when it has the token-analyst's risk factors and the pool-researcher's depth analysis, compared to calling it standalone with just a swap request.
- **Progressive output keeps the user informed.** Don't wait until the end to show results. After each agent completes, show a brief summary so the user knows what's happening.
- **Amount is required.** Never assume a trade size. If the user says "research and buy UNI" without an amount, ask: "How much would you like to trade?"

## Error Handling

| Error                         | User-Facing Message                                                      | Suggested Action                          |
| ----------------------------- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Token not found               | "Could not find token {X} on {chain}."                                   | Check spelling or provide contract address|
| No pools found                | "No Uniswap pools found for {token}/{payWith} on {chain}."              | Try different pay token or chain          |
| Token-analyst fails           | "Token research failed: {reason}. Cannot proceed without due diligence." | Try again or use research-token directly  |
| Pool-researcher fails         | "Pool analysis failed. Research completed but cannot find optimal pool."  | Try execute-swap with manual pool choice  |
| Risk-assessor VETO            | "Risk assessment vetoed this trade: {reason}."                           | Reduce amount, try different token/pool   |
| Risk-assessor HARD_VETO       | "Trade blocked: {reason}. This cannot be overridden."                    | The trade is unsafe at any size           |
| Trade-executor fails          | "Trade execution failed: {reason}. Research and risk data preserved."    | Check wallet, balance, gas; retry         |
| Safety check fails            | "Safety limits exceeded. Check spending limits with check-safety."       | Wait for limit reset or adjust limits     |
| User declines confirmation    | "Trade cancelled. Research and risk data are shown above for reference." | No action needed                          |
| Wallet not configured         | "No wallet configured. Cannot execute trades."                           | Set up wallet with setup-agent-wallet     |
| Insufficient balance          | "Insufficient {payWith} balance: have {X}, need {Y}."                    | Reduce amount or acquire more tokens      |
