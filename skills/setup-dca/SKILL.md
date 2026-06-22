---
name: setup-dca
description: >-
  Set up a non-custodial dollar-cost averaging strategy on Uniswap. Use when
  user wants to create recurring swaps, auto-buy ETH/BTC/SOL with USDC on a
  schedule, or build a DCA bot. Covers USDC approval, swap path selection,
  frequency configuration, Gelato keeper automation, and monitoring. Works on
  local testnet for development or mainnet for production.
model: opus
allowed-tools:
  - Task(subagent_type:trade-executor)
  - mcp__uniswap__execute_swap
  - mcp__uniswap__get_quote
  - mcp__uniswap__get_token_price
  - mcp__uniswap__get_agent_balance
  - mcp__uniswap__get_pools_by_token_pair
  - mcp__uniswap__check_safety_status
---

# Setup DCA

## Overview

Sets up a complete non-custodial dollar-cost averaging strategy on Uniswap. Instead of manually executing swaps on a schedule, remembering to check prices, finding optimal routes, and managing approvals, this skill configures the entire DCA lifecycle in one command: validates the strategy, selects the best swap path, configures execution frequency, handles Permit2 approvals, executes the first swap, and sets up ongoing automation.

**Why this is 10x better than doing it manually:**

1. **Optimal path selection**: Automatically discovers the best swap route across all Uniswap pool versions and fee tiers for your token pair. Manual DCA often uses suboptimal routes, losing 0.1-0.5% per execution to unnecessary slippage.
2. **Approval management**: Handles the Permit2 approval flow correctly -- a common source of failed DCA executions. One-time setup that covers all future executions.
3. **Two automation modes**: Self-execute mode (agent triggers swaps) for development and testing, or Gelato keeper mode (on-chain automation) for trustless production execution. Without this skill, setting up Gelato keepers requires understanding task creation, resolver contracts, and fee funding.
4. **Built-in safety**: Every execution routes through the safety pipeline with slippage guards, balance checks, and circuit breakers. Manual DCA has no guardrails -- a misconfigured bot can drain a wallet on a single bad swap.
5. **Cost projection**: Before committing, shows projected total cost including gas, slippage, and keeper fees over the full DCA period. No surprises.

## When to Use

Activate when the user says anything like:

- "Set up dollar-cost averaging on Uniswap"
- "Create a recurring swap"
- "Auto-buy ETH with USDC weekly"
- "Build a DCA bot"
- "DCA into ETH every day with $100"
- "Set up weekly buys of WBTC"
- "Accumulate UNI over the next 3 months"
- "Schedule recurring swaps from USDC to ETH"

**Do NOT use** when the user wants a one-time swap (use `execute-swap` instead), wants to manage an existing DCA (not yet supported -- cancel and recreate), or wants to DCA into LP positions (use `full-lp-workflow` instead).

## Parameters

| Parameter            | Required | Default      | How to Extract                                                                  |
| -------------------- | -------- | ------------ | ------------------------------------------------------------------------------- |
| targetAsset          | Yes      | --           | Token to accumulate: "ETH", "WBTC", "UNI", "SOL", or 0x address               |
| amountPerExecution   | Yes      | --           | Amount per swap: "$100", "100 USDC", "0.1 ETH worth"                           |
| inputToken           | No       | USDC         | Token to spend: "USDC", "USDT", "DAI", "WETH"                                 |
| frequency            | No       | weekly       | "daily", "weekly", "biweekly", "monthly"                                       |
| totalExecutions      | No       | --           | Number of executions: "52 weeks", "12 months", "indefinite"                    |
| chain                | No       | ethereum     | Target chain: "ethereum", "base", "arbitrum"                                   |
| slippageTolerance    | No       | 50 (0.5%)    | Max slippage in basis points per execution                                     |
| keeperMode           | No       | self-execute | "self-execute" (agent-triggered) or "gelato" (on-chain keeper automation)      |
| startImmediately     | No       | true         | Whether to execute the first swap now                                          |

If the user doesn't provide `amountPerExecution` or `targetAsset`, **ask for them** -- never guess a DCA strategy.

## Workflow

```
                           DCA SETUP PIPELINE
  ┌──────────────────────────────────────────────────────────────────────┐
  │                                                                      │
  │  Step 1: VALIDATE & ANALYZE                                          │
  │  ├── Check wallet balance (enough for at least 3 executions)         │
  │  ├── Verify target asset exists on chain                             │
  │  ├── Get current price of target asset                               │
  │  └── Output: Balance check + current price baseline                  │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 2: FIND OPTIMAL SWAP PATH                                      │
  │  ├── Discover all pools for inputToken/targetAsset                   │
  │  ├── Get quotes across fee tiers at DCA amount                       │
  │  ├── Select path with lowest price impact at execution size          │
  │  └── Output: Best route + expected slippage per execution            │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 3: COST PROJECTION                                             │
  │  ├── Estimate gas cost per execution                                 │
  │  ├── Calculate total cost over full DCA period                       │
  │  ├── Project keeper fees (if Gelato mode)                            │
  │  ├── Compare DCA vs lump-sum at current price                        │
  │  └── Output: Full cost breakdown + projection                        │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 4: USER CONFIRMATION                                           │
  │  ├── Present: strategy summary + cost projection                     │
  │  ├── Ask: "Proceed with this DCA strategy?"                          │
  │  └── User must explicitly confirm                                    │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 5: CONFIGURE & EXECUTE                                         │
  │  ├── Check/set Permit2 approval for inputToken                       │
  │  ├── If startImmediately: execute first swap via trade-executor      │
  │  ├── If gelato: create Gelato task with resolver + fund keeper       │
  │  ├── If self-execute: write DCA config to .uniswap/dca-config.json  │
  │  └── Output: Configuration + first execution result                  │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 6: MONITORING SETUP                                            │
  │  ├── Record baseline: price, balance, execution count                │
  │  ├── Set up execution tracking                                       │
  │  └── Output: DCA dashboard with next execution time                  │
  │                                                                      │
  └──────────────────────────────────────────────────────────────────────┘
```

### Step 1: Validate & Analyze

Check prerequisites before committing to a strategy:

1. Call `mcp__uniswap__get_agent_balance` to verify the wallet has sufficient `inputToken` balance for at least 3 executions (safety buffer).
2. Call `mcp__uniswap__get_token_price` for the `targetAsset` to establish a price baseline.
3. Call `mcp__uniswap__check_safety_status` to verify spending limits can accommodate the DCA.

**Present to user:**

```text
Step 1/6: Validation

  Wallet Balance: 5,200 USDC on Ethereum
  DCA Budget:     $100/week x 52 weeks = $5,200 total
  Balance Check:  PASS (covers full DCA period)

  Target Asset:   ETH at $1,960.00
  Per Execution:  ~0.051 ETH per $100

  Proceeding to path selection...
```

**Gate check:** If the wallet balance covers fewer than 3 executions, warn the user and ask if they want to proceed with a shorter DCA period.

### Step 2: Find Optimal Swap Path

1. Call `mcp__uniswap__get_pools_by_token_pair` for `inputToken`/`targetAsset` on the target chain.
2. Call `mcp__uniswap__get_quote` at the `amountPerExecution` size for the top 2-3 pools to compare price impact.
3. Select the route with the lowest price impact at the DCA execution size.

**Present to user:**

```text
Step 2/6: Path Selection

  Best Route: USDC -> WETH via 0.05% pool (V3, Ethereum)
  Pool TVL:   $285M
  Impact:     ~0.01% per $100 execution
  Alternative: 0.3% pool (0.02% impact -- slightly worse)

  Proceeding to cost projection...
```

### Step 3: Cost Projection

Calculate the full cost of the DCA strategy:

```text
Step 3/6: Cost Projection

  DCA Strategy: $100 USDC -> ETH weekly for 52 weeks

  Per Execution:
    Swap Amount:   $100.00
    Est. Slippage: ~$0.01 (0.01%)
    Gas Cost:      ~$2.50 (at current gas)
    Net Purchase:  ~$97.49 of ETH

  Full Period (52 weeks):
    Total Spent:   $5,200.00
    Est. Gas:      ~$130.00 (2.5%)
    Est. Slippage: ~$0.52 (0.01%)
    Net Invested:  ~$5,069.48

  At Current Price ($1,960/ETH):
    Lump Sum Now:  2.653 ETH for $5,200
    DCA Estimate:  ~2.587 ETH (varies with price)

  Ready for your confirmation...
```

### Step 4: User Confirmation

Present the full strategy summary and ask for explicit confirmation:

```text
DCA Strategy Confirmation

  Buy:        ETH with USDC
  Amount:     $100 per execution
  Frequency:  Weekly (every 7 days)
  Duration:   52 executions
  Chain:      Ethereum
  Route:      USDC/WETH 0.05% (V3)
  Slippage:   0.5% max
  Mode:       Self-execute (agent-triggered)
  Start:      Immediately (first swap now)
  Total Cost: ~$5,200 + ~$130 gas

  Proceed with this DCA strategy? (yes/no)
```

**Only proceed to Step 5 if the user explicitly confirms.**

### Step 5: Configure & Execute

Delegate the first execution to `Task(subagent_type:trade-executor)`:

```
Execute this swap as the first DCA execution:
- Sell: {amountPerExecution} {inputToken}
- Buy: {targetAsset}
- Chain: {chain}
- Slippage tolerance: {slippageTolerance} bps
- Context: This is execution 1 of {totalExecutions} in a DCA strategy.
  Route through the {fee}% pool for optimal execution at this size.
```

After execution, write the DCA configuration:

**For self-execute mode**, write `.uniswap/dca-config.json`:

```json
{
  "strategy": "dca",
  "inputToken": "USDC",
  "targetAsset": "WETH",
  "amountPerExecution": "100000000",
  "frequency": "weekly",
  "nextExecution": "2026-02-17T00:00:00Z",
  "totalExecutions": 52,
  "completedExecutions": 1,
  "chain": "ethereum",
  "chainId": 1,
  "route": {
    "pool": "0x...",
    "fee": 500,
    "version": "v3"
  },
  "slippageTolerance": 50,
  "status": "active",
  "createdAt": "2026-02-10T00:00:00Z",
  "executionHistory": []
}
```

**For Gelato mode**, create a Gelato Automate task with:
- Resolver: check if `block.timestamp >= nextExecution`
- Executor: swap via Universal Router with the configured route
- Fund the Gelato task with ETH for keeper fees

### Step 6: Monitoring Setup

```text
Step 6/6: DCA Active

  First Execution:
    Sold:     100 USDC
    Received: 0.0510 WETH ($99.96)
    Gas:      $2.30
    Tx:       https://etherscan.io/tx/0x...

  Schedule:
    Next:     2026-02-17 (7 days)
    Remaining: 51 executions
    Mode:     Self-execute

  Config: .uniswap/dca-config.json
```

## Output Format

### Successful Setup

```text
DCA Strategy Active

  Strategy:
    Buy:        ETH with USDC
    Amount:     $100 per execution
    Frequency:  Weekly
    Duration:   52 executions (~1 year)
    Chain:      Ethereum
    Route:      USDC/WETH 0.05% (V3)
    Mode:       Self-execute

  First Execution:
    Sold:       100 USDC
    Received:   0.0510 WETH ($99.96)
    Slippage:   0.04%
    Gas:        $2.30
    Tx:         https://etherscan.io/tx/0x...

  Projections:
    Total Budget:    $5,200 + ~$130 gas
    Est. ETH:        ~2.59 ETH (at current prices)
    Next Execution:  2026-02-17

  Config: .uniswap/dca-config.json
  Status: ACTIVE -- 1/52 executions complete
```

### Setup Without Immediate Execution

```text
DCA Strategy Configured (Not Started)

  Strategy:
    Buy:        ETH with USDC
    Amount:     $100 per execution
    Frequency:  Weekly
    Chain:      Ethereum
    Route:      USDC/WETH 0.05% (V3)
    Mode:       Self-execute

  First Execution: 2026-02-17 (scheduled)
  Config: .uniswap/dca-config.json
  Status: CONFIGURED -- awaiting first execution
```

## Important Notes

- **DCA is a long-term strategy.** This skill sets up the configuration and optionally executes the first swap. Subsequent executions depend on the keeper mode: self-execute requires the agent to be running, Gelato mode runs autonomously on-chain.
- **Self-execute mode requires the agent to be online.** If the agent is offline when an execution is due, it will execute on the next run. Gelato mode is fully autonomous and does not require the agent.
- **Gas costs matter for small DCA amounts.** At $2-5 per swap on Ethereum mainnet, a $10/week DCA loses 20-50% to gas. The skill warns if gas exceeds 5% of the execution amount and suggests Base or Arbitrum for cheaper execution.
- **Slippage is typically negligible for DCA.** DCA amounts are usually small relative to pool TVL, so price impact is minimal. The skill still enforces the slippage tolerance as a safety guard.
- **The DCA config file is the source of truth.** The `.uniswap/dca-config.json` file tracks execution history, next execution time, and strategy parameters. Deleting it effectively cancels the DCA.
- **To cancel a DCA**, delete the config file or set `status` to `"cancelled"`. For Gelato mode, the Gelato task must also be cancelled on-chain.
- **L2 chains are recommended for small DCA amounts.** Base and Arbitrum have gas costs 10-100x lower than Ethereum mainnet, making small DCA strategies viable.

## Error Handling

| Error                      | User-Facing Message                                                                | Suggested Action                                      |
| -------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Insufficient balance       | "Wallet has {X} {inputToken} but DCA needs at least {Y} for 3 executions."        | Fund wallet or reduce amount per execution            |
| Target asset not found     | "Could not find {targetAsset} on {chain}."                                         | Check spelling or provide contract address            |
| No pools found             | "No Uniswap pools found for {inputToken}/{targetAsset} on {chain}."                | Try a different chain or token pair                   |
| Gas too high               | "Gas cost (~${X}) exceeds 5% of execution amount (${Y}). Consider using Base."    | Switch to an L2 chain for cheaper execution           |
| Safety check failed        | "Safety limits would be exceeded by this DCA strategy."                            | Adjust spending limits or reduce DCA amount           |
| Approval failed            | "Could not approve {inputToken} for Permit2: {reason}."                            | Check wallet permissions and retry                    |
| First execution failed     | "First DCA execution failed: {reason}. Strategy configured but not started."       | Fix the issue and manually trigger first execution    |
| Gelato setup failed        | "Could not create Gelato automation task: {reason}."                               | Use self-execute mode instead                         |
| Config write failed        | "Could not write DCA configuration: {reason}."                                     | Check file permissions                                |
| Wallet not configured      | "No wallet configured. Cannot execute DCA."                                        | Set up wallet with setup-agent-wallet                 |
| Spending limit exceeded    | "DCA total (${X}) exceeds daily spending limit (${Y})."                            | Adjust spending limits or reduce DCA frequency/amount |
