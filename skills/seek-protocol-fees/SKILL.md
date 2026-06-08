---
name: seek-protocol-fees
description: >-
  Analyze TokenJar profitability and optionally execute a Firepit burn-and-claim.
  Autonomous pipeline: checks balances, prices assets, calculates profit vs.
  4,000 UNI burn cost, simulates, and executes if profitable. Default is
  preview-only. Use when user asks "Is the TokenJar profitable?", "Execute a
  burn", or "Claim protocol fees."
model: opus
allowed-tools:
  - Task(subagent_type:protocol-fee-seeker)
  - Task(subagent_type:safety-guardian)
  - mcp__uniswap__get_tokenjar_balances
  - mcp__uniswap__get_firepit_state
  - mcp__uniswap__get_agent_balance
---

# Seek Protocol Fees

## Overview

This is the autonomous burn-and-claim pipeline for Uniswap's protocol fee system. The TokenJar (`0xf38521f130fcCF29dB1961597bc5d2B60F995f85`) accumulates fees from V2, V3, V4, UniswapX, and Unichain. The Firepit (`0x0D5Cd355e2aBEB8fb1552F56c965B867346d6721`) allows anyone to burn 4,000 UNI to release those accumulated assets. When the jar's value exceeds the burn cost plus gas, a profit opportunity exists.

This skill runs the full pipeline in one command: check balances, price assets, calculate profitability, simulate the burn, and -- only if the user explicitly opts in -- execute it.

**Why this is 10x better than calling tools individually:**

1. **9-step workflow compressed to one command**: Without this skill, a user must manually check TokenJar balances, price each token in USD, check the Firepit threshold, calculate UNI burn cost at current prices, estimate gas, determine net profitability, select optimal assets, simulate the burn, and finally execute. This skill does all of it with compound context flowing between each step.
2. **Safety-gated execution**: Default mode is preview-only (`auto-execute: false`). Even when execution is enabled, the pipeline simulates first, validates through `safety-guardian`, and checks nonce freshness for race conditions -- protections that are easy to skip when calling tools manually.
3. **Profitability dashboard**: The output is a structured profitability report, not raw JSON from 6 different tools. You see gross value, burn cost, gas cost, net profit, ROI, and per-asset breakdown in one view.
4. **Post-burn conversion**: Optionally converts received tokens to stablecoins in the same pipeline, calculating the true net profit after conversion slippage.

## When to Use

Activate when the user says anything like:

- "Is the TokenJar profitable to burn?"
- "Check protocol fee profitability"
- "Execute a Firepit burn"
- "Burn UNI and claim protocol fees"
- "How much is in the TokenJar? Is it worth burning?"
- "Claim fees from the TokenJar"
- "Seek protocol fees"
- "Run the burn-and-claim pipeline"

**Do NOT use** when the user just wants to monitor accumulation over time (use `monitor-tokenjar` instead) or wants historical burn analysis (use `analyze-burn-economics` instead).

## Parameters

| Parameter      | Required | Default          | How to Extract                                                        |
| -------------- | -------- | ---------------- | --------------------------------------------------------------------- |
| chain          | No       | ethereum         | Always Ethereum mainnet for TokenJar/Firepit                          |
| auto-execute   | No       | false            | "execute the burn", "claim fees" implies true; "check", "preview" implies false |
| post-burn-swap | No       | false            | "convert to stables", "swap to USDC" implies true                     |
| recipient      | No       | connected wallet | Explicit address if provided, otherwise agent's wallet                |

If the user's intent is ambiguous between preview and execution, **default to preview** and present the profitability report. Let the user explicitly confirm before any UNI is burned.

## Workflow

```
                        SEEK-PROTOCOL-FEES PIPELINE
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │  Step 1: PRE-FLIGHT (direct MCP calls)                              │
  │  ├── get_tokenjar_balances — what's in the jar?                     │
  │  ├── get_firepit_state — threshold, nonce, readiness                │
  │  ├── get_agent_balance — does agent have enough UNI?                │
  │  └── Gate: if jar empty or no UNI → STOP immediately               │
  │          │                                                          │
  │          ▼ (all pre-flight data feeds into Step 2)                  │
  │                                                                     │
  │  Step 2: PROFITABILITY ANALYSIS (protocol-fee-seeker)               │
  │  ├── Price all TokenJar assets in USD                               │
  │  ├── Calculate: burn cost + gas cost vs. jar value                  │
  │  ├── Select optimal assets to claim                                 │
  │  ├── Determine net profit and ROI                                   │
  │  └── Output: Profitability Report                                   │
  │          │                                                          │
  │          ▼ PROFITABILITY GATE                                       │
  │  ┌───────────────────────────────────────────────────┐              │
  │  │  PROFITABLE     → Present report, proceed         │              │
  │  │  NOT PROFITABLE → Present report, STOP            │              │
  │  │  MARGINAL       → Present report, warn user       │              │
  │  └───────────────────────────────────────────────────┘              │
  │          │ (only if profitable)                                     │
  │          ▼                                                          │
  │                                                                     │
  │  Step 3: USER CONFIRMATION                                          │
  │  ├── If auto-execute: false → present report, ask user              │
  │  ├── If auto-execute: true → present report, proceed                │
  │  └── User must explicitly confirm before UNI is burned              │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 4: SIMULATE + EXECUTE (protocol-fee-seeker)                   │
  │  ├── execute_burn(simulate=true) — dry run                          │
  │  ├── safety-guardian validates transaction                          │
  │  ├── Nonce freshness check (race condition protection)              │
  │  ├── execute_burn(simulate=false) — broadcast                       │
  │  └── Wait for confirmation                                          │
  │          │                                                          │
  │          ▼                                                          │
  │                                                                     │
  │  Step 5: POST-BURN REPORT                                           │
  │  ├── Show received tokens with USD values                           │
  │  ├── If post-burn-swap: convert to stablecoins                      │
  │  ├── Calculate final net profit after all costs                     │
  │  └── Recommend next burn timing                                     │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

### Step 1: Pre-Flight (direct MCP calls)

Make three parallel MCP calls to quickly assess feasibility before invoking the agent:

1. Call `mcp__uniswap__get_tokenjar_balances` to get current jar contents.
2. Call `mcp__uniswap__get_firepit_state` to get threshold, nonce, and wallet readiness.
3. Call `mcp__uniswap__get_agent_balance` to check the agent's UNI balance.

**Gate checks** (stop immediately if any fail):

| Check                        | Condition                                   | Action if Failed                                                    |
| ---------------------------- | ------------------------------------------- | ------------------------------------------------------------------- |
| TokenJar empty               | All balances are zero                       | "TokenJar is empty. No fees to claim."                              |
| Agent lacks UNI              | UNI balance < threshold (4,000 UNI)         | "Insufficient UNI: have {X}, need {threshold}. Acquire UNI first." |
| Firepit not ready            | Contract state indicates unavailability      | "Firepit contract is not ready: {reason}."                          |

**Present to user after pre-flight:**

```text
Step 1/5: Pre-Flight Complete

  TokenJar: 6 tokens detected (WETH, USDC, USDT, DAI, WBTC, UNI)
  Firepit: Threshold 4,000 UNI | Nonce: 42
  Agent UNI Balance: 5,200 UNI (sufficient)

  Analyzing profitability...
```

### Step 2: Profitability Analysis (protocol-fee-seeker)

Delegate to `Task(subagent_type:protocol-fee-seeker)` with all pre-flight data:

```
Analyze the profitability of a Firepit burn-and-claim.

Pre-flight data:
- TokenJar balances: {from Step 1 — full balance data}
- Firepit state: threshold={threshold} UNI, nonce={nonce}
- Agent UNI balance: {balance}

Tasks:
1. Price every TokenJar asset in USD using get_token_price.
2. Calculate UNI burn cost: {threshold} UNI * current UNI price.
3. Estimate gas cost for the burn transaction using get_gas_price.
4. Calculate net profit: total_jar_value - (UNI_cost + gas_cost).
5. Select optimal assets to claim (highest value, exclude LP tokens, up to maxReleaseLength).
6. Provide a clear PROFITABLE / NOT_PROFITABLE / MARGINAL verdict.

Return a structured profitability report with per-asset breakdown.
```

**Present to user after completion:**

```text
Step 2/5: Profitability Analysis Complete

  TokenJar Value:  $52,000
  ┌─────────────────────────────────────────────┐
  │  WETH     7.20    $18,000   (34.6%)         │
  │  USDC     15,000  $15,000   (28.8%)         │
  │  USDT     8,500   $8,500    (16.3%)         │
  │  WBTC     0.08    $6,400    (12.3%)         │
  │  DAI      4,100   $4,100    (7.9%)          │
  └─────────────────────────────────────────────┘

  Burn Cost:
    UNI burn:  4,000 UNI ($28,000)
    Gas:       ~$45
    Total:     $28,045

  Net Profit:  $23,955
  ROI:         85.4%
  Verdict:     PROFITABLE
```

**If NOT_PROFITABLE:**

```text
Step 2/5: Profitability Analysis Complete

  TokenJar Value:  $18,000
  Burn Cost:       $28,045 (4,000 UNI + gas)
  Net Profit:      -$10,045
  Verdict:         NOT PROFITABLE

  The TokenJar value ($18,000) does not cover the burn cost ($28,045).
  Estimated time to profitability: ~1.4 days (at $7,400/day accumulation rate).

  Pipeline stopped. No burn executed.
```

### Step 3: User Confirmation

If the burn is profitable and `auto-execute` is `false` (default), present the full profitability report and ask for explicit confirmation:

```text
Burn Confirmation Required

  TokenJar Value:  $52,000 (5 assets)
  Burn Cost:       $28,045 (4,000 UNI + $45 gas)
  Net Profit:      $23,955 (85.4% ROI)

  Assets to Claim: WETH, USDC, USDT, WBTC, DAI
  Post-Burn Swap:  {Yes — convert to USDC | No — keep as received}

  This will permanently burn 4,000 UNI. Proceed? (yes/no)
```

**Only proceed to Step 4 if the user explicitly confirms.** If `auto-execute` is `true`, still present the report but proceed without waiting.

### Step 4: Simulate + Execute (protocol-fee-seeker)

Delegate to `Task(subagent_type:protocol-fee-seeker)` for the execution pipeline:

```
Execute the Firepit burn-and-claim.

Profitability analysis (from Step 2):
{Full profitability report}

Selected assets: {asset list from Step 2}
Nonce at analysis time: {nonce from Step 1}

Execute the following sequence:
1. Simulate: execute_burn(simulate=true) with the selected assets.
2. If simulation succeeds, delegate to safety-guardian for transaction validation.
3. Nonce freshness check: re-read Firepit state. If nonce has changed, ABORT (race condition).
4. Execute: execute_burn(simulate=false) to broadcast.
5. Wait for transaction confirmation.

If any step fails, report the failure point and do not proceed.
```

**Present to user during execution:**

```text
Step 4/5: Executing Burn

  Simulation:     SUCCESS
  Safety Check:   APPROVED by safety-guardian
  Nonce Check:    Fresh (42 — unchanged)
  Broadcasting... confirmed in block 19,500,000

  Tx: https://etherscan.io/tx/0xabcd...1234
```

**If race condition detected:**

```text
Step 4/5: Execution ABORTED — Race Condition

  Nonce changed: was 42, now 43.
  Another searcher burned before us. TokenJar balances have changed.

  Returning to profitability analysis with fresh data...
```

### Step 5: Post-Burn Report

**Present final result:**

```text
Step 5/5: Burn Complete

  Burned:    4,000 UNI ($28,000)
  Gas:       $45
  Received:
    WETH     7.20    $18,000
    USDC     15,000  $15,000
    USDT     8,500   $8,500
    WBTC     0.08    $6,400
    DAI      4,100   $4,100

  Gross Value:  $52,000
  Total Cost:   $28,045
  Net Profit:   $23,955 (85.4% ROI)
  Tx:           https://etherscan.io/tx/0xabcd...1234

  ──────────────────────────────────────
  Next Burn Estimate
  ──────────────────────────────────────
  Accumulation Rate: ~$7,400/day
  Est. Next Profitable Burn: ~3.8 days
```

**If `post-burn-swap: true`, append conversion details:**

```text
  Post-Burn Conversions:
    WETH  → 17,950 USDC  (0.28% slippage)
    WBTC  → 6,380 USDC   (0.31% slippage)
    USDT  → 8,495 USDC   (0.06% slippage)
    DAI   → 4,098 USDC   (0.05% slippage)

  Final USDC Balance: 51,923 USDC
  Conversion Costs:   $77
  True Net Profit:    $23,878 (after all costs)
```

## Output Format

### Preview Mode (default)

```text
Protocol Fee Analysis

  TokenJar Value:  ${total_value} ({num_assets} assets)
  ┌──────────────────────────────────────┐
  │  {token}  {balance}  ${value}  ({%}) │
  │  ...                                 │
  └──────────────────────────────────────┘

  Burn Cost:   ${uni_cost} ({threshold} UNI) + ${gas} gas = ${total_cost}
  Net Profit:  ${net_profit}
  ROI:         {roi}%
  Verdict:     {PROFITABLE | NOT_PROFITABLE | MARGINAL}

  {if profitable: "Ready to execute. Say 'burn it' to proceed."}
  {if not profitable: "Est. time to profitability: {days} days."}
```

### Execution Mode

```text
Protocol Fee Burn Complete

  Burned:     {threshold} UNI (${uni_cost})
  Gas:        ${gas_cost}
  Received:   {num_assets} assets worth ${gross_value}
  Net Profit: ${net_profit} ({roi}% ROI)
  Tx:         {explorer_link}

  Pipeline: Pre-flight -> Analysis -> Confirm -> Simulate -> Execute (all passed)
```

## Important Notes

- **Default is preview-only.** The skill never burns UNI unless the user explicitly enables execution. This is a destructive, irreversible action -- 4,000 UNI is sent to the dead address.
- **Ethereum mainnet only.** The TokenJar and Firepit contracts are deployed on Ethereum mainnet. The `chain` parameter exists for forward compatibility but currently only `ethereum` is valid.
- **Race conditions are real.** Other searchers monitor the same TokenJar. The nonce freshness check before execution is critical. If another burn happens between analysis and execution, the pipeline aborts safely.
- **UNI is permanently burned.** Unlike a swap where you can swap back, the UNI burn is irreversible. The skill makes this very clear in the confirmation step.
- **Gas costs matter on mainnet.** Ethereum gas can significantly impact profitability. The agent factors current gas prices into the analysis and may recommend waiting for lower gas if the margin is thin.
- **LP tokens are excluded by default.** Some TokenJar assets may be LP tokens that require additional redemption. The agent excludes these unless specifically instructed to handle them.

## Error Handling

| Error                        | User-Facing Message                                                          | Suggested Action                          |
| ---------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------- |
| TokenJar empty               | "TokenJar is empty. No fees to claim."                                       | Wait for fees to accumulate               |
| Insufficient UNI             | "Insufficient UNI: have {X}, need {threshold}."                              | Acquire UNI or wait for price drop        |
| Not profitable               | "Burn is not profitable. Jar value ${X} < burn cost ${Y}."                   | Wait for more accumulation                |
| Simulation failed            | "Burn simulation failed: {reason}."                                          | Check Firepit state, try again            |
| Safety check failed          | "Safety validation rejected the burn: {reason}."                             | Review safety configuration               |
| Race condition               | "Another searcher burned first. Nonce changed from {X} to {Y}."             | Re-run to analyze with fresh data         |
| Transaction reverted         | "Burn transaction reverted: {reason}."                                       | Check gas, nonce, and Firepit state       |
| Wallet not configured        | "No wallet configured. Cannot execute burns."                                | Set up wallet with setup-agent-wallet     |
| Post-burn swap failed        | "Burn succeeded but token conversion failed for {token}: {reason}."          | Manually swap via execute-swap            |
| Gas price spike              | "Gas prices elevated (${gas}). Burn is marginally profitable."               | Wait for lower gas or accept lower profit |
