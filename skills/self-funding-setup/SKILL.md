---
name: self-funding-setup
description: >-
  Set up a complete self-funding agent lifecycle in one command. Orchestrates
  5 agents to take an agent from zero to self-sustaining: provisions wallet,
  optionally deploys token with V4 pool, configures treasury management,
  registers identity on ERC-8004, and sets up x402 micropayments. Use when
  user wants to make their agent self-funding, earn and manage its own
  revenue, or configure autonomous agent operations end-to-end.
model: opus
allowed-tools:
  - Task(subagent_type:wallet-provisioner)
  - Task(subagent_type:token-deployer)
  - Task(subagent_type:treasury-manager)
  - Task(subagent_type:identity-verifier)
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - mcp__uniswap__get_supported_chains
  - mcp__uniswap__get_agent_balance
  - mcp__uniswap__check_safety_status
---

# Self-Funding Setup

## Overview

The most complex composite skill in the system. Orchestrates 5 specialized agents in sequence to take an agent from zero infrastructure to a fully self-sustaining economic entity -- wallet, optional token, treasury management, on-chain identity, and payment acceptance -- in a single command.

**Why this is 10x better than setting up each component manually:**

1. **5 domains compressed into 1 command**: Wallet provisioning, token deployment, treasury management, identity registration, and payment configuration each require different expertise and tooling. Manually coordinating these takes hours and requires deep knowledge of Privy/Turnkey APIs, Uniswap V4 pool creation, DCA strategies, ERC-8004 registries, and x402 protocol. This skill handles all five.
2. **Context flows between stages**: Each agent receives the output of all prior agents. The treasury-manager knows the wallet address from Step 1 and the token address from Step 2. The identity-verifier registers the wallet from Step 1 with the capabilities demonstrated by Steps 2-3. Without this skill, you'd manually copy-paste addresses and configuration between five separate tools.
3. **Conditional pipeline**: Token deployment (Step 2) is optional -- skip it for agents that earn through services rather than token economics. The skill adapts the remaining steps based on which revenue model is selected.
4. **Rollback awareness**: If Step 3 fails, Steps 1 and 2 are still valid and preserved. The skill reports exactly which steps succeeded and which failed, so you can fix the issue and re-run from the failure point rather than starting over.
5. **Progressive output**: You see each stage complete in real-time with a running summary. By the end, you have a complete "agent identity card" showing every component of the self-funding infrastructure.

## When to Use

Activate when the user says anything like:

- "Set up my agent to be self-funding"
- "Make my agent earn and manage its own revenue"
- "Configure autonomous agent operations end-to-end"
- "I want my agent to be self-sustaining"
- "Set up the full agent economy stack"
- "Bootstrap my agent's financial infrastructure"
- "Create a self-funding agent from scratch"
- "Full agent setup: wallet, token, treasury, identity, payments"

**Do NOT use** when the user only wants one component (use the individual skills: `setup-agent-wallet`, `deploy-agent-token`, `manage-treasury`, `verify-agent`, or `configure-x402` respectively), or when the agent is already partially set up and only needs one missing piece.

## Parameters

| Parameter        | Required | Default | How to Extract                                                          |
| ---------------- | -------- | ------- | ----------------------------------------------------------------------- |
| walletProvider   | No       | privy   | "privy" (dev), "turnkey" (production), or "safe" (max security)         |
| deployToken      | No       | false   | Whether to deploy an agent token: "yes", "with token", "launch token"   |
| tokenName        | If token | --      | Token name if deploying: "AgentCoin", "MyBot Token"                     |
| tokenSymbol      | If token | --      | Token symbol if deploying: "AGENT", "BOT"                               |
| chains           | No       | base    | Operating chains: "base", "ethereum", "base,ethereum"                   |
| revenueModel     | No       | x402    | "x402" (micropayments), "token-fees" (swap fees), "lp-fees", or "all"  |
| environment      | No       | dev     | "dev" (development), "staging", or "production"                         |
| initialFunding   | No       | --      | Initial funding amount: "$100", "0.1 ETH"                              |

If the user says "with token" or "launch a token", set `deployToken=true` and ask for `tokenName` and `tokenSymbol` if not provided.

## Workflow

```
                     SELF-FUNDING SETUP PIPELINE
  ┌──────────────────────────────────────────────────────────────────────┐
  │                                                                      │
  │  Step 1: WALLET PROVISIONING (wallet-provisioner)                    │
  │  ├── Determine provider: privy (dev) / turnkey (prod) / safe (max)   │
  │  ├── Provision wallet with signing capabilities                      │
  │  ├── Configure spending policies                                     │
  │  ├── Fund with gas (2x estimated need)                               │
  │  └── Output: Wallet address, provider, policies                      │
  │          │                                                           │
  │          ▼ wallet address feeds into all subsequent steps             │
  │                                                                      │
  │  Step 2: TOKEN DEPLOYMENT (token-deployer) [OPTIONAL]                │
  │  ├── Deploy ERC-20 token contract                                    │
  │  ├── Create Uniswap V4 pool with anti-snipe hooks                   │
  │  ├── Bootstrap initial liquidity                                     │
  │  ├── Lock LP tokens (10 years default)                               │
  │  └── Output: Token address, pool address, LP position                │
  │          │                                                           │
  │          ▼ token + pool info feeds into treasury config               │
  │                                                                      │
  │  Step 3: TREASURY MANAGEMENT (treasury-manager)                      │
  │  ├── Configure auto-conversion of earned fees to stablecoins         │
  │  ├── Set up DCA strategy for volatile holdings                       │
  │  ├── Configure yield optimization for idle capital                   │
  │  ├── Set circuit breaker thresholds                                  │
  │  └── Output: Treasury config, burn rate, runway projection           │
  │          │                                                           │
  │          ▼ wallet + capabilities feed into identity registration      │
  │                                                                      │
  │  Step 4: IDENTITY REGISTRATION (identity-verifier)                   │
  │  ├── Register agent on ERC-8004 Identity Registry                    │
  │  ├── Set capabilities metadata (trading, LP, services)               │
  │  ├── Initialize reputation score                                     │
  │  └── Output: ERC-8004 identity, trust tier, registry tx              │
  │          │                                                           │
  │          ▼ identity + wallet feed into payment config                 │
  │                                                                      │
  │  Step 5: PAYMENT CONFIGURATION (direct)                              │
  │  ├── Configure x402 micropayment acceptance                          │
  │  ├── Set per-tool pricing                                            │
  │  ├── Generate .well-known/x402-manifest.json                         │
  │  ├── Verify USDC balance for pay mode                                │
  │  └── Output: x402 config, pricing, manifest                          │
  │                                                                      │
  │  ═══════════════════════════════════════════════════════════          │
  │  FINAL: AGENT IDENTITY CARD                                          │
  │  ├── Wallet, token, treasury, identity, payments -- all linked       │
  │  └── Complete self-funding infrastructure report                     │
  │                                                                      │
  └──────────────────────────────────────────────────────────────────────┘
```

### Step 1: Wallet Provisioning

Delegate to `Task(subagent_type:wallet-provisioner)`:

```
Provision an agent wallet for self-funding operations:
- Provider: {walletProvider}
- Chains: {chains}
- Environment: {environment}
- Spending limit: $10,000/day (default for self-funding agents)
- Initial funding: {initialFunding} (or 2x estimated gas need)

This wallet will be used for:
- Token deployment (if enabled)
- Treasury management (fee conversion, LP)
- x402 payment settlement
- General agent operations

Configure appropriate spending policies for a self-funding agent.
```

**Present to user after completion:**

```text
Step 1/5: Wallet Provisioned

  Address:    0xABCD...1234
  Provider:   Privy (development)
  Chain:      Base (8453)
  Funded:     0.05 ETH ($98.00)
  Policies:   $10,000/day, Router + Permit2 approved

  Proceeding to token deployment...
```

**If wallet already exists**, detect it via `mcp__uniswap__get_agent_balance` and skip to Step 2:

```text
Step 1/5: Wallet Already Configured (skipped)

  Address:    0xABCD...1234
  Balance:    0.12 ETH + 500 USDC
  Status:     Active

  Skipping to next step...
```

### Step 2: Token Deployment (Optional)

**Only execute if `deployToken=true`.** Otherwise, skip to Step 3.

Delegate to `Task(subagent_type:token-deployer)`:

```
Deploy an agent token for self-funding:
- Token name: {tokenName}
- Token symbol: {tokenSymbol}
- Chain: {chains[0]} (primary chain)
- Wallet: {wallet address from Step 1}
- Paired token: WETH
- Hooks: anti-snipe (2-block delay) + revenue-share (5%)
- LP lock: 10 years
- Initial liquidity: {derive from initialFunding or suggest minimum}

This token is part of a self-funding agent setup. The revenue-share hook
directs 5% of swap fees to the agent wallet for treasury management.
```

**Present to user after completion:**

```text
Step 2/5: Token Deployed

  Token:      AgentCoin (AGENT)
  Address:    0x5678...efgh
  Chain:      Base (8453)
  Pool:       AGENT/WETH V4 (0.3%, anti-snipe + revenue-share)
  LP Lock:    10 years (unlocks 2036-02-10)
  Revenue:    5% of swap fees -> agent wallet

  Proceeding to treasury management...
```

**If `deployToken=false`:**

```text
Step 2/5: Token Deployment (skipped)

  No token deployment requested.
  Revenue model: {revenueModel} (no token economics)

  Proceeding to treasury management...
```

### Step 3: Treasury Management

Delegate to `Task(subagent_type:treasury-manager)`:

```
Configure treasury management for a self-funding agent:
- Wallet: {wallet address from Step 1}
- Chains: {chains}
- Action: assess + configure (initial setup, not full operations)

Revenue sources:
{if deployToken: "- Token swap fees (5% revenue share from AGENT/WETH pool)"}
{if revenueModel includes x402: "- x402 micropayments (USDC on Base)"}
{if revenueModel includes lp-fees: "- LP fee earnings"}

Configure:
- Auto-convert non-stablecoin earnings to USDC
- Conversion threshold: $10 minimum
- DCA enabled for large conversions
- Circuit breaker: halt if treasury drops below $100
- Operating reserve: 30 days of estimated burn rate
```

**Present to user after completion:**

```text
Step 3/5: Treasury Configured

  Treasury Value: $98.00 (initial funding)
  Auto-Convert:   Enabled (non-stables -> USDC, threshold: $10)
  DCA:            Enabled for conversions > 0.1% pool TVL
  Circuit Breaker: $100 minimum (INACTIVE -- above threshold)
  Burn Rate:      ~$0/day (no operations yet)
  Runway:         Indefinite (no burn rate established)

  Proceeding to identity registration...
```

### Step 4: Identity Registration

Delegate to `Task(subagent_type:identity-verifier)`:

```
Register this agent on ERC-8004:
- Agent address: {wallet address from Step 1}
- Chain: ethereum (ERC-8004 registries are on mainnet)

Capabilities to register:
{if deployToken: "- Token deployment and pool management"}
{if revenueModel includes x402: "- x402 service provider"}
- Uniswap trading and LP management
- Treasury management

After registration, query the trust tier to confirm.
```

**Present to user after completion:**

```text
Step 4/5: Identity Registered

  ERC-8004:    Registered on Identity Registry
  Address:     0xABCD...1234
  Trust Tier:  BASIC (new registration)
  Reputation:  0/100 (initial -- builds with activity)
  Registry Tx: https://etherscan.io/tx/0x...

  Proceeding to payment configuration...
```

### Step 5: Payment Configuration

Configure x402 micropayment acceptance directly (no agent needed):

1. Verify the wallet has USDC on the settlement chain (Base recommended).
2. Write `.uniswap/x402-config.json` with payment configuration.
3. Write `.well-known/x402-manifest.json` for service discovery.

```text
Step 5/5: Payments Configured

  Mode:         Accept (x402 micropayments)
  Chain:        Base (8453)
  Wallet:       0xABCD...1234
  Facilitator:  Auto-selected

  Pricing:
    Price quotes:       $0.001/call
    Pool analytics:     $0.003/call
    Route optimization: $0.005/call
    Simulation:         $0.010/call
    Execution:          $0.050/call

  Config Files:
    .uniswap/x402-config.json
    .well-known/x402-manifest.json
```

## Output Format

### Full Setup (with token)

```text
Self-Funding Agent Setup Complete

  ══════════════════════════════════════════════
  AGENT IDENTITY CARD
  ══════════════════════════════════════════════

  Wallet:
    Address:     0xABCD...1234
    Provider:    Privy (development)
    Chain:       Base (8453)
    Balance:     0.05 ETH + 0 USDC

  Token:
    Name:        AgentCoin (AGENT)
    Address:     0x5678...efgh
    Pool:        AGENT/WETH V4 (0.3%)
    Hooks:       Anti-snipe + Revenue Share (5%)
    LP Lock:     10 years

  Treasury:
    Auto-Convert: Enabled (-> USDC)
    Circuit Break: $100 minimum
    Burn Rate:    ~$0/day (initial)
    Runway:       Indefinite

  Identity:
    ERC-8004:    Registered (BASIC tier)
    Reputation:  0/100 (builds with activity)
    Registry:    0x7177...09A

  Payments:
    x402:        Accepting micropayments
    Settlement:  USDC on Base
    Pricing:     $0.001 - $0.050 per call

  ══════════════════════════════════════════════

  Pipeline: Wallet -> Token -> Treasury -> Identity -> Payments
  Status:   ALL 5 STEPS COMPLETE

  Next Steps:
    1. Fund the wallet with USDC for x402 pay mode
    2. Share your x402 manifest for service discovery
    3. Start operations to build reputation (rep: 0 -> basic -> verified)
    4. Monitor treasury health with /manage-treasury
```

### Setup Without Token

```text
Self-Funding Agent Setup Complete

  ══════════════════════════════════════════════
  AGENT IDENTITY CARD
  ══════════════════════════════════════════════

  Wallet:
    Address:     0xABCD...1234
    Provider:    Privy (development)
    Chain:       Base (8453)
    Balance:     0.05 ETH

  Token:         Not deployed (service-based revenue model)

  Treasury:
    Auto-Convert: Enabled (-> USDC)
    Circuit Break: $100 minimum
    Revenue:      x402 micropayments

  Identity:
    ERC-8004:    Registered (BASIC tier)
    Reputation:  0/100

  Payments:
    x402:        Accepting micropayments
    Settlement:  USDC on Base

  ══════════════════════════════════════════════

  Pipeline: Wallet -> (Token skipped) -> Treasury -> Identity -> Payments
  Status:   ALL STEPS COMPLETE (4/5, token skipped)
```

### Partial Failure

```text
Self-Funding Agent Setup -- Partial

  Step 1: Wallet       COMPLETE  (0xABCD...1234)
  Step 2: Token        COMPLETE  (AGENT at 0x5678...efgh)
  Step 3: Treasury     FAILED    (Could not configure auto-convert)
  Step 4: Identity     SKIPPED   (depends on Step 3)
  Step 5: Payments     SKIPPED   (depends on Step 4)

  Error at Step 3: "Insufficient USDC balance for initial DCA configuration."

  What's preserved:
    - Wallet is provisioned and funded (Step 1)
    - Token is deployed with pool and locked LP (Step 2)

  To resume:
    1. Fund wallet with USDC: send USDC to 0xABCD...1234
    2. Re-run: "Set up self-funding" (will detect existing wallet + token)
```

## Important Notes

- **This is the most complex composite skill.** It orchestrates 5 agents sequentially, each feeding context to the next. Expect the full pipeline to take 2-5 minutes depending on chain conditions and whether token deployment is included.
- **Token deployment is irreversible.** Once a token is deployed and the pool is created, it cannot be undone. The skill simulates everything via safety-guardian before execution, but make sure the token name, symbol, and parameters are correct before confirming.
- **The pipeline is resumable.** If a step fails, prior steps are preserved. Re-running the skill detects existing wallet and token, skipping completed steps automatically.
- **ERC-8004 registration is on Ethereum mainnet.** Even if your agent operates on Base, the identity registry is on Ethereum. This requires a small amount of ETH on mainnet for the registration transaction.
- **Reputation starts at 0.** The initial trust tier is BASIC. Building reputation requires completing trades, providing liquidity, and receiving positive feedback from counterparties. Use the agent actively to progress from basic -> verified -> trusted.
- **x402 payments settle on Base by default.** Base has ~200ms settlement and low gas costs, making it ideal for micropayments. The wallet must hold USDC on Base to accept payments.
- **Revenue model affects treasury configuration.** "x402" mode configures for micropayment income. "token-fees" mode configures for swap fee revenue. "lp-fees" mode configures for LP earnings. "all" enables all three.
- **Development vs production providers.** Privy is recommended for development (fast setup, easy testing). Turnkey or Safe is recommended for production (TEE-backed signing, hardware security). The skill selects based on the `environment` parameter.

## Error Handling

| Error                         | User-Facing Message                                                            | Suggested Action                                  |
| ----------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------- |
| Wallet provisioning failed    | "Could not provision wallet: {reason}."                                        | Check provider credentials and retry              |
| Wallet already exists         | "Agent wallet already configured. Skipping to next step."                      | Proceeds automatically with existing wallet       |
| Token deployment failed       | "Token deployment failed at step: {reason}. Wallet is preserved."              | Fix the issue and re-run (wallet will be reused)  |
| Token already deployed        | "Token {symbol} already deployed. Skipping to treasury."                       | Proceeds automatically with existing token        |
| Treasury config failed        | "Treasury configuration failed: {reason}. Wallet and token preserved."         | Fund wallet and re-run                            |
| ERC-8004 registration failed  | "Could not register on ERC-8004: {reason}. Prior steps preserved."             | Check ETH balance on mainnet and retry            |
| x402 config failed            | "Could not write x402 configuration: {reason}."                               | Check file permissions and retry                  |
| Insufficient funding          | "Wallet needs at least {X} ETH for gas. Current: {Y} ETH."                    | Fund the wallet before proceeding                 |
| Chain not supported           | "{chain} does not support all required features."                              | Use Base or Ethereum for full feature support     |
| Partial pipeline failure      | "Setup completed partially. Failed at step {N}: {reason}."                     | Fix the failed step and re-run from that point    |
| Provider not configured       | "Wallet provider '{provider}' requires credentials not found in environment."  | Set required env vars (PRIVY_APP_ID, etc.)        |
