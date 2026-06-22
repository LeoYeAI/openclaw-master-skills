---
name: agent-otc-trade
description: >-
  Facilitate over-the-counter trades between agents using Uniswap as the
  settlement layer. Use when user wants to trade tokens directly with another
  agent, settle an agent-to-agent trade through Uniswap, or execute an OTC
  swap with a specific counterparty agent. Verifies counterparty identity via
  ERC-8004, negotiates terms, and settles through Uniswap pools.
model: opus
allowed-tools:
  - Task(subagent_type:trade-executor)
  - Task(subagent_type:identity-verifier)
  - mcp__uniswap__get_quote
  - mcp__uniswap__get_token_price
  - mcp__uniswap__get_pool_info
  - mcp__uniswap__get_agent_balance
  - mcp__uniswap__execute_swap
  - mcp__uniswap__submit_cross_chain_intent
  - mcp__uniswap__check_safety_status
---

# Agent OTC Trade

## Overview

Facilitates over-the-counter trades between agents using Uniswap as the trustless settlement layer. Instead of agents manually coordinating trades through ad-hoc channels, verifying each other's identity, agreeing on prices, and handling settlement independently, this skill provides a structured pipeline: verify counterparty identity via ERC-8004, agree on terms using Uniswap pool prices as the reference rate, and settle atomically through Uniswap pools.

**Why this is 10x better than manual agent-to-agent trading:**

1. **Counterparty verification**: Before any trade, the counterparty agent's identity is verified via ERC-8004 on-chain registries. Without this, agents trade blindly -- trusting addresses they've never interacted with. The skill checks identity, reputation score, and trust tier, refusing to trade with unverified agents.
2. **Fair pricing via Uniswap oracle**: OTC trades use Uniswap pool prices as the reference rate, preventing either party from proposing unfair terms. The skill shows the current pool price, the proposed OTC price, and the premium/discount so both parties have full transparency.
3. **Atomic settlement**: Trades settle through Uniswap pools in a single transaction. No escrow risk, no counterparty default risk, no partial fills. The pool provides guaranteed liquidity at the agreed price.
4. **Cross-chain support**: For agents on different chains, settlement uses ERC-7683 cross-chain intents. Without this skill, cross-chain OTC trades require manual bridge coordination -- a multi-step process prone to stuck transactions and timing mismatches.
5. **Audit trail**: Every OTC trade is recorded with counterparty identity, agreed terms, settlement transaction, and fees. This creates a verifiable history for reputation building and dispute resolution.

## When to Use

Activate when the user says anything like:

- "Trade tokens directly with another agent"
- "Settle an agent-to-agent trade through Uniswap"
- "Execute an OTC swap with agent 0x..."
- "Buy tokens from agent 0x... using Uniswap"
- "Set up a direct trade with a counterparty agent"
- "OTC trade 1000 USDC for UNI with agent 0x..."
- "Settle a service payment with another agent via Uniswap"

**Do NOT use** when the user wants a regular swap without a specific counterparty (use `execute-swap` instead), wants to provide liquidity (use `manage-liquidity` instead), or wants to find trading opportunities (use `scan-opportunities` instead).

## Parameters

| Parameter           | Required | Default     | How to Extract                                                        |
| ------------------- | -------- | ----------- | --------------------------------------------------------------------- |
| counterpartyAgent   | Yes      | --          | Counterparty address (0x...) or ERC-8004 identity                     |
| tokenSell           | Yes      | --          | Token you are selling: "USDC", "UNI", or 0x address                  |
| tokenBuy            | Yes      | --          | Token you are buying: "ETH", "UNI", or 0x address                    |
| amount              | Yes      | --          | Amount to sell: "1000 USDC", "50 UNI", "$5,000 worth"                |
| chain               | No       | ethereum    | Settlement chain: "ethereum", "base", "arbitrum"                     |
| settlementMethod    | No       | direct-swap | "direct-swap", "intent" (ERC-7683 cross-chain)                      |
| maxPremium          | No       | 1%          | Max acceptable premium/discount vs pool price                        |
| requireVerified     | No       | true        | Require ERC-8004 verified counterparty (true/false)                  |

If the user doesn't provide `counterpartyAgent`, `tokenSell`/`tokenBuy`, or `amount`, **ask for them** -- never guess OTC trade parameters.

## Workflow

```
                        AGENT OTC TRADE PIPELINE
  ┌──────────────────────────────────────────────────────────────────────┐
  │                                                                      │
  │  Step 1: VERIFY COUNTERPARTY                                         │
  │  ├── Check ERC-8004 identity registry                                │
  │  ├── Query reputation score                                          │
  │  ├── Determine trust tier (unverified/basic/verified/trusted)        │
  │  └── Output: Identity report + trust decision                        │
  │          │                                                           │
  │          ▼ IDENTITY GATE                                             │
  │  ┌───────────────────────────────────────────┐                       │
  │  │  trusted/verified  -> Proceed              │                       │
  │  │  basic             -> Warn, ask user       │                       │
  │  │  unverified        -> STOP (if required)   │                       │
  │  └───────────────────────────────────────────┘                       │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 2: PRICE DISCOVERY                                             │
  │  ├── Get current Uniswap pool price for the token pair               │
  │  ├── Get quote at the OTC trade size                                 │
  │  ├── Calculate fair OTC price (pool price + spread)                  │
  │  └── Output: Reference price + OTC terms                             │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 3: TERMS AGREEMENT                                             │
  │  ├── Present terms to user: price, amounts, fees, settlement method  │
  │  ├── Compare OTC price vs pool price (premium/discount)              │
  │  ├── Show total cost including gas and slippage                      │
  │  └── User must explicitly confirm                                    │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 4: SETTLEMENT                                                  │
  │  ├── Check wallet balance and approvals                              │
  │  ├── Execute swap via trade-executor (or cross-chain intent)         │
  │  ├── Verify settlement on-chain                                      │
  │  └── Output: Settlement confirmation + tx hash                       │
  │          │                                                           │
  │          ▼                                                           │
  │                                                                      │
  │  Step 5: RECORD & REPORT                                             │
  │  ├── Record trade in OTC history                                     │
  │  ├── Log counterparty, terms, settlement tx                          │
  │  └── Output: Full OTC trade report                                   │
  │                                                                      │
  └──────────────────────────────────────────────────────────────────────┘
```

### Step 1: Verify Counterparty

Delegate to `Task(subagent_type:identity-verifier)`:

```
Verify the identity and reputation of this agent:
- Agent address: {counterpartyAgent}
- Chain: {chain}

Check the ERC-8004 Identity Registry, Reputation Registry, and Validation
Registry. Return the trust tier (unverified/basic/verified/trusted),
reputation score, registration date, and any flags.
```

**Present to user:**

```text
Step 1/5: Counterparty Verification

  Agent:       0x1234...abcd
  ERC-8004:    Registered (verified tier)
  Reputation:  78/100 (good)
  Registered:  2025-11-15 (87 days ago)
  Trades:      142 completed, 0 disputes
  Trust Tier:  VERIFIED

  Proceeding to price discovery...
```

**Identity gate logic:**

| Trust Tier   | Action                                                                        |
| ------------ | ----------------------------------------------------------------------------- |
| **trusted**  | Proceed to Step 2 automatically                                               |
| **verified** | Proceed to Step 2 automatically                                               |
| **basic**    | Warn user: "Counterparty has basic verification only. Proceed?" Ask to confirm. |
| **unverified** | If `requireVerified=true`: **STOP.** Show reason. Suggest verifying first.  |
|              | If `requireVerified=false`: Warn strongly, ask for explicit confirmation.     |

### Step 2: Price Discovery

1. Call `mcp__uniswap__get_token_price` for both tokens to establish USD values.
2. Call `mcp__uniswap__get_pool_info` for the token pair to get the current pool price.
3. Call `mcp__uniswap__get_quote` at the OTC trade size to determine actual execution price including slippage.

```text
Step 2/5: Price Discovery

  Token Pair:    USDC / UNI
  Pool Price:    1 UNI = $7.10 (USDC/UNI 0.3% V3)
  Pool TVL:      $42M
  Quote at Size: 1000 USDC -> 140.65 UNI (impact: 0.08%)

  OTC Reference Rate: $7.10 per UNI
  Your Trade:         1000 USDC -> ~140.85 UNI

  Proceeding to terms agreement...
```

### Step 3: Terms Agreement

Present the complete trade terms for user confirmation:

```text
OTC Trade Terms

  You Sell:     1,000 USDC
  You Receive:  ~140.85 UNI ($999.90)
  Counterparty: 0x1234...abcd (VERIFIED, rep: 78/100)

  Pricing:
    Pool Rate:  $7.10 per UNI
    OTC Rate:   $7.10 per UNI (0.00% premium)
    Slippage:   ~0.08%
    Gas Est:    ~$5.00

  Settlement:
    Method:     Direct swap via Uniswap V3
    Chain:      Ethereum
    Pool:       USDC/UNI 0.3%

  Proceed with this OTC trade? (yes/no)
```

**Only proceed to Step 4 if the user explicitly confirms.**

If the OTC price deviates from the pool price by more than `maxPremium`, warn the user:

```text
  WARNING: OTC rate ($7.25/UNI) is 2.1% above pool rate ($7.10/UNI).
  This exceeds your max premium of 1%. Proceed anyway? (yes/no)
```

### Step 4: Settlement

Delegate to `Task(subagent_type:trade-executor)`:

**For direct-swap settlement:**

```
Execute this OTC trade settlement:
- Sell: {amount} {tokenSell}
- Buy: {tokenBuy}
- Chain: {chain}
- Slippage tolerance: based on OTC terms
- Context: This is an OTC trade with counterparty {counterpartyAgent}
  (ERC-8004 verified, reputation {score}/100). Settle through the
  {fee}% pool.
```

**For cross-chain intent settlement:**

Use `mcp__uniswap__submit_cross_chain_intent` with:
- `tokenIn`: tokenSell on source chain
- `tokenOut`: tokenBuy on destination chain
- `sourceChain`: your chain
- `destinationChain`: counterparty's chain

### Step 5: Record & Report

```text
Step 5/5: OTC Trade Complete

  Settlement:
    Sold:       1,000 USDC
    Received:   140.85 UNI ($999.90)
    Slippage:   0.07%
    Gas:        $4.80
    Tx:         https://etherscan.io/tx/0x...

  Counterparty:
    Agent:      0x1234...abcd
    Trust:      VERIFIED (78/100)

  OTC Terms vs Market:
    Pool Rate:  $7.10/UNI
    Actual:     $7.10/UNI (0.00% premium)
```

## Output Format

### Successful OTC Trade

```text
Agent OTC Trade Complete

  Trade:
    Sold:         1,000 USDC
    Received:     140.85 UNI ($999.90)
    Counterparty: 0x1234...abcd (VERIFIED)
    Settlement:   Direct swap via USDC/UNI 0.3% (V3)
    Chain:        Ethereum
    Tx:           https://etherscan.io/tx/0x...

  Pricing:
    Pool Rate:    $7.10/UNI
    Actual Rate:  $7.10/UNI
    Premium:      0.00%
    Slippage:     0.07%
    Gas:          $4.80

  Counterparty Verification:
    ERC-8004:     Registered, VERIFIED tier
    Reputation:   78/100
    Trade History: 142 completed, 0 disputes
```

### Blocked by Identity Check

```text
Agent OTC Trade -- Blocked

  Counterparty: 0x5678...efgh
  ERC-8004:     NOT REGISTERED
  Trust Tier:   UNVERIFIED

  Trade blocked: Counterparty is not ERC-8004 verified.
  Your policy requires verified counterparties (requireVerified=true).

  Suggestions:
    - Ask the counterparty to register on ERC-8004
    - Use /verify-agent to check their status
    - Set requireVerified=false to trade with unverified agents (not recommended)
```

## Important Notes

- **Counterparty verification is the key safety feature.** ERC-8004 identity checks prevent trading with malicious or unknown agents. The default `requireVerified=true` is strongly recommended.
- **Settlement happens through Uniswap pools, not peer-to-peer.** Both agents interact with the Uniswap pool independently. This means the trade is atomic and trustless -- neither party can default.
- **The counterparty does not need to be online simultaneously.** Since settlement is through a pool, your agent executes its side of the trade independently. The "OTC" aspect is the agreed-upon terms and counterparty verification, not a literal peer-to-peer atomic swap.
- **Price reference prevents unfair terms.** The Uniswap pool price serves as an objective reference rate. The `maxPremium` parameter (default 1%) prevents accepting trades at significantly worse-than-market rates.
- **Cross-chain OTC trades use ERC-7683 intents.** For agents on different chains, the skill uses `submit_cross_chain_intent` for settlement. This adds bridge latency but enables cross-chain agent commerce.
- **All OTC trades are logged.** Trade details (counterparty, terms, settlement tx) are recorded for reputation building and audit purposes.
- **This skill settles YOUR side of the trade.** The counterparty agent is responsible for their own execution. In practice, both agents use this skill independently to settle their respective sides through the same Uniswap pool.

## MCP server dependency

This skill relies on Uniswap MCP tools for pricing, pool data, quotes, balances, and cross-chain intents.
When used in isolation (for example, from a skills catalog), ensure the Agentic Uniswap MCP server is running:

- Repo: [`Agentic-Uniswap` MCP server](https://github.com/wpank/Agentic-Uniswap/tree/main/packages/mcp-server)
- Package: `@agentic-uniswap/mcp-server`

## Error Handling

| Error                     | User-Facing Message                                                       | Suggested Action                                |
| ------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------- |
| Counterparty unverified   | "Counterparty agent is not ERC-8004 verified."                            | Ask counterparty to register, or disable check  |
| Counterparty not found    | "Could not find agent at address {addr}."                                 | Verify the address is correct                   |
| No pool for pair          | "No Uniswap pool found for {tokenSell}/{tokenBuy} on {chain}."           | Try a different chain or intermediate token      |
| Premium too high          | "OTC rate deviates {X}% from pool rate, exceeding {maxPremium}% limit."  | Renegotiate terms or increase maxPremium        |
| Insufficient balance      | "Insufficient {tokenSell} balance: have {X}, need {Y}."                  | Fund wallet or reduce trade amount              |
| Settlement failed         | "OTC settlement via Uniswap failed: {reason}."                           | Check liquidity, gas, and retry                 |
| Cross-chain intent failed | "Cross-chain settlement failed: {reason}."                               | Check bridge status and retry                   |
| Safety check failed       | "Trade exceeds safety limits."                                           | Check spending limits with check-safety         |
| Wallet not configured     | "No wallet configured. Cannot execute OTC trades."                       | Set up wallet with setup-agent-wallet           |
| Identity service down     | "ERC-8004 registry unreachable. Cannot verify counterparty."             | Retry later or proceed with caution             |
