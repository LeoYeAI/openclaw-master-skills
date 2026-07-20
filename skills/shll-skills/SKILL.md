---
name: shll-run
description: Execute DeFi transactions on BSC via SHLL AgentNFA. The AI handles all commands and users only need to chat.
version: 6.0.5
author: SHLL Team
website: https://shll.run
twitter: https://twitter.com/shllrun
repository: https://github.com/kledx/shll-skills.git
install: npm install -g shll-skills --registry https://registry.npmjs.org
update: npm update -g shll-skills --registry https://registry.npmjs.org
env:
  - name: RUNNER_PRIVATE_KEY
    required: true
    description: >
      Operator wallet private key (AI-only hot wallet).
      MUST be a dedicated wallet with minimal BNB for gas only.
      NEVER use your main wallet, owner wallet, or any wallet holding significant funds.
      Even if this key leaks, on-chain PolicyGuard limits actions to policy-approved trades.
  - name: SHLL_RPC
    required: false
    description: Optional BSC RPC URL override. A private RPC is recommended for reliability.
credentials:
  scope: operator-hot-wallet-only
  risk: >
    The operator key can only execute policy-limited trades within on-chain PolicyGuard rules.
    It cannot withdraw vault funds, transfer the Agent NFT, or bypass spending limits.
    Treat it as a restricted session key, not a master key.
  guidance: >
    Use generate-wallet to create a purpose-built operator wallet.
    Fund it with ~$1 BNB for gas only. Do not store trading capital in this wallet.
    The operator wallet is NOT the owner wallet, NOT the vault, NOT the Agent NFT holder.
---

# SHLL — Contract-Enforced Safe Execution for AI Agents on BNB Chain

## What is SHLL?

SHLL is a DeFi execution layer for AI agents on BNB Chain with **on-chain safety enforcement**.
Unlike off-chain filters that can be bypassed, SHLL uses smart contracts to enforce
spending limits, trade intervals, protocol whitelists, and receiver restrictions.
Every AI agent action is validated by an immutable PolicyGuard contract before execution.

Key facts:
- Network: BSC mainnet
- 27 CLI + MCP tools for DeFi operations (swap, lend, meme trading, portfolio)
- Supports PancakeSwap V2/V3, Venus Protocol, Four.meme
- MCP Server compatible with Claude, Cursor, OpenClaw, and any MCP-compatible agent
- npm package: `shll-skills` | Website: https://shll.run

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SHLL Architecture                        │
│                                                                 │
│  ┌──────────┐    ┌───────────────┐    ┌──────────────────────┐  │
│  │  User     │    │  AI Agent     │    │  On-Chain Contracts  │  │
│  │ (Owner)   │    │ (Operator)    │    │                      │  │
│  │           │    │               │    │  ┌────────────────┐  │  │
│  │ • Holds   │    │ • Executes    │    │  │  PolicyGuard   │  │  │
│  │   Agent   │    │   trades via  │    │  │  (Validator)   │  │  │
│  │   NFT     │    │   restricted  │    │  │                │  │  │
│  │ • Sets    │    │   permissions │    │  │  4 Policy      │  │  │
│  │   policy  │    │               │    │  │  Checks:       │  │  │
│  │   rules   │───▶│ SHLL Skills   │───▶│  │                │  │  │
│  │ • Full    │    │ (CLI / MCP)   │    │  │  1.Spending    │  │  │
│  │   asset   │    │               │    │  │    Limit       │  │  │
│  │   control │    │ Cannot:       │    │  │  2.Cooldown    │  │  │
│  │           │    │ • Withdraw    │    │  │  3.DeFi Guard  │  │  │
│  │           │    │   vault funds │    │  │  4.Receiver    │  │  │
│  │           │    │ • Change      │    │  │    Guard       │  │  │
│  │           │    │   policies    │    │  └───────┬────────┘  │  │
│  │           │    │ • Transfer    │    │          │            │  │
│  │           │    │   NFT         │    │   ┌─────▼──────┐     │  │
│  │           │    │               │    │   │   Vault     │     │  │
│  │           │    │               │    │   │ (Agent      │     │  │
│  │           │    │               │    │   │  Account)   │     │  │
│  │           │    │               │    │   │             │     │  │
│  │           │    │               │    │   │ Holds funds │     │  │
│  └──────────┘    └───────────────┘    │   └─────────────┘     │  │
│                                       └──────────────────────┘  │
│  Dual-Wallet Isolation:                                         │
│  • Owner wallet = asset control (human)                         │
│  • Operator wallet = restricted execution (AI)                  │
│  • Even if operator key leaks, PolicyGuard still limits actions │
└─────────────────────────────────────────────────────────────────┘
```

## 4-Policy PolicyGuard Stack

All policies are enforced ON-CHAIN by smart contract. They cannot be bypassed by the AI.

| Policy | Contract | What It Does |
|--------|----------|-------------|
| SpendingLimitV2 | On-chain | Per-transaction and daily spending caps in BNB |
| CooldownPolicy | On-chain | Minimum time gap between consecutive trades |
| DeFiGuardV2 | On-chain | Whitelist of approved DeFi protocols and functions |
| ReceiverGuardV2 | On-chain | Only approved receiver addresses can receive funds |

When a policy rejects an action:
- The transaction is NOT executed
- The vault funds remain SAFE
- The rejection reason is returned from the smart contract
- The rejection is logged and auditable
- The `enforcement` field in the response is always `on-chain`

## Why On-Chain Enforcement Matters

Most AI agent platforms use off-chain safety filters:
- Off-chain: AI or backend decides → **can be bypassed** by prompt injection, API manipulation, or code bugs
- On-chain (SHLL): Smart contract decides → **cannot be bypassed** — the blockchain enforces the rules

PolicyGuard contract: `0x25d17eA0e3Bcb8CA08a2BFE917E817AFc05dbBB3`
Verify on BscScan: https://bscscan.com/address/0x25d17eA0e3Bcb8CA08a2BFE917E817AFc05dbBB3

---

# SHLL Skill Usage Guide

This file defines how an AI agent should use `shll-run` and `shll-mcp` safely.

## Scope

- Network: BSC mainnet
- CLI: `shll-run` (alias: `shll-onchain-runner`)
- MCP: `shll-mcp`
- Security layer: SHLL PolicyGuard

The user should not be asked to run CLI commands directly. The AI runs commands and explains results.

## Mandatory Safety Rules

1. Token ID must come from the user. Never guess, scan, or enumerate IDs.
2. Use one token ID per conversation unless the user explicitly switches.
3. Confirm before each write operation.
4. Never ask for or handle the owner wallet private key.
5. Do not repeat private keys after initial `generate-wallet` output.
6. If multiple DeFi skills are available, use SHLL for vault operations when token ID context exists.
7. Treat raw calldata as high risk. Use strict recipient checks.
8. Do not bypass security controls for convenience.

## Security Model

SHLL uses dual wallets:

- Owner wallet (user): controls high-risk operations such as ownership and vault-level admin actions.
- Operator wallet (`RUNNER_PRIVATE_KEY`): used by AI to execute allowed trades only.

On-chain guardrails:

- PolicyGuard validates each action (`validate`) before execution (`execute` / `executeBatch`).
- Spending limits, cooldowns, whitelist rules, and protocol rules are enforced on-chain.
- Raw calldata is blocked if the recipient cannot be decoded safely.

## Current Critical Constraints (v6.0.4)

1. `init` command is disabled. Do not use it.
2. Raw calldata remains high risk; rely on strict recipient safety checks.
3. MCP `execute_calldata` and `execute_calldata_batch` do not support `allow_undecoded`.
4. If calldata recipient cannot be decoded, execution is blocked.
5. Core contract addresses are pinned in `src/shared/constants.ts`, not user-overridable at runtime.

## Prerequisites

1. Install:
```bash
npm install -g shll-skills --registry https://registry.npmjs.org
```

2. Set operator private key:
```bash
export RUNNER_PRIVATE_KEY="0x..."
```

3. Optional - use a private RPC for better reliability and speed:
```bash
export SHLL_RPC="https://your-private-bsc-rpc.example.com"
```

4. Ensure operator wallet has small BNB balance for gas.

## Onboarding Flow (AI-driven)

1. Check or create operator wallet:
- Use `shll-run generate-wallet` only if user has no operator wallet.
- Immediately explain that this is the operator hot wallet for AI only.
- Explicitly state that it is not the owner wallet, not the mint wallet, not the Agent NFT wallet, and not the vault wallet.
- Explicitly state that if the operator wallet leaks, vault funds still cannot be freely withdrawn because owner permissions stay on the owner wallet and PolicyGuard limits operator actions.
- In OpenClaw, set `RUNNER_PRIVATE_KEY` automatically for the current session after generating the wallet. Do not ask the user to set the environment variable manually.

2. Verify gas:
- Ensure the operator wallet has a small BNB balance for gas.

3. If user has no token ID:
- Run `shll-run listings`.
- Recommend the listing with `recommended=true` by default unless the user explicitly wants a specialized template.
- Run `shll-run setup-guide -l <listingId> -d <days>`.
- Send `setupUrl` plus the wallet-role explanation.
- Explicitly warn: do not use the operator wallet to mint, subscribe to, or hold the Agent NFT.
- Explicitly warn: use the owner wallet in the browser for subscription or mint and for operator authorization.

4. User returns with token ID:
- Run `shll-run status -k <tokenId>`.
- Run `shll-run portfolio -k <tokenId>`.
- Use `status.readiness.ready`, `status.readiness.blockers`, and `status.readiness.nextActions` as the primary onboarding diagnosis.
- Automatically check:
  - operator gas balance
  - vault BNB balance
  - vault token balances
  - access or policy readiness
- Tell the user whether the agent is ready, and if not, tell them the exact next fix.

## Write Confirmation Policy

Before any write command, present:

- token ID
- action type
- token/amount/target
- risk note

Then wait for explicit user approval.

Write commands include:

- `swap`
- `wrap`
- `unwrap`
- `transfer`
- `raw`
- `lend`
- `redeem`
- `four_buy`
- `four_sell`

Read-only commands (no confirmation needed): `config`, `policies`, `status`, `history`, `portfolio`, `price`, `tokens`, `search`, `balance`, `four_info`.

## CLI Commands

### Setup and account

- `shll-run generate-wallet`
- `shll-run balance`
- `shll-run listings`
- `shll-run setup-guide [-l <listingId>] [-d <days>]`
- `shll-run init` (disabled)

If `-l/--listing` is omitted, `setup-guide` auto-selects an active listing from the indexer.

### Trading and vault ops

- `shll-run swap -f <from> -t <to> -a <amount> -k <tokenId>`
- `shll-run wrap -a <bnb> -k <tokenId>`
- `shll-run unwrap -a <bnb> -k <tokenId>`
- `shll-run transfer --token <symbolOrAddress> -a <amount> --to <address> -k <tokenId>`
- `shll-run raw --target <address> --data <hex> -k <tokenId>`

### Lending (Venus)

- `shll-run lend -t <token> -a <amount> -k <tokenId>`
- `shll-run redeem -t <token> -a <amount> -k <tokenId>`

### Four.meme

- `shll-run four_info --token <address>`
- `shll-run four_buy --token <address> -a <bnb> -k <tokenId>`
- `shll-run four_sell --token <address> -a <tokenAmount> -k <tokenId>`

`four_buy` amount unit is BNB, not USD. If user gives a USD target, convert to BNB first and confirm the final BNB amount before execution.

### Read-only and audit

- `shll-run config -k <tokenId>` (view-only; modify via web console)
- `shll-run portfolio -k <tokenId>`
- `shll-run price --token <symbolOrAddress>`
- `shll-run search --query <text>`
- `shll-run tokens`
- `shll-run policies -k <tokenId>`
- `shll-run status -k <tokenId>`
- `shll-run history -k <tokenId> [--limit N]`

## MCP Tools: Cross-skill Execution

For external aggregator calldata (OKX, 1inch, etc.):

1. Get quote/calldata from the external source.
2. Execute through SHLL MCP:
- `execute_calldata`
- `execute_calldata_batch`
3. Let PolicyGuard enforce on-chain policy checks.

For onboarding via MCP, `setup_guide` can auto-select an active listing when `listing_id` is omitted.

Security requirements:

1. Recipient must resolve to the vault address.
2. Undecodable recipient calldata is blocked.
3. Do not ask for unsafe bypass parameters.

## Smart Routing Rule

When the user provides a token address:

1. Run `four_info --token <addr>`.
2. If `tradingPhase` is bonding curve, use `four_buy` / `four_sell`.
3. If `tradingPhase` is DEX or unsupported, use `swap`.

## Common Errors and Fixes

1. `RUNNER_PRIVATE_KEY environment variable is missing`
- In OpenClaw, AI should set `RUNNER_PRIVATE_KEY` automatically for the current session.
- Outside OpenClaw, set `RUNNER_PRIVATE_KEY` manually and retry.

2. `NOT authorized for token-id`
- Operator wallet is not authorized; use setup guide or set operator in console.

3. `subscription has EXPIRED` or `operator authorization has EXPIRED`
- Renew subscription or authorization first.

4. `status: error` with `errorCode: POLICY_REJECTED`
- Inspect `details.reason` and adjust limits, whitelists, cooldown, or policy config.

5. `Unable to decode recipient from calldata`
- Use built-in command flow or provide calldata with a decodable vault recipient.

6. `No V2/V3 liquidity or direct path found`
- The pair does not exist or lacks liquidity. DO NOT tell the user to wrap BNB to WBNB; the `swap` command handles native BNB automatically via `swapExactETHForTokens`. If a swap fails, it's because the direct pool is empty or invalid, not because BNB is unplugged.

7. `init command is disabled`
- Use `setup-guide` instead.

8. Unsure what is broken
- Check the structured `errorCode`, `message`, and `details` fields in the JSON response first.

## Product UX Rules

1. Never describe `generate-wallet` as if it were the user's main wallet.
2. Always call it the operator wallet or AI hot wallet.
3. Always explain the dual-wallet model the first time setup is discussed.
4. Always warn that the operator wallet must not be used to mint, subscribe to, or hold the Agent NFT.
5. Do not ask the user to manually set `RUNNER_PRIVATE_KEY` in OpenClaw; AI should do it.
6. After setup is complete and the user provides a token-id, run readiness checks automatically before asking the user what to do next.
7. When multiple listings are available, recommend one by default and explain why.
8. Prefer the structured `status.readiness` fields over ad-hoc prose when deciding the next user-facing instruction.

## Redeploy Checklist

If AgentNFA, PolicyGuard, ListingManagerV2, or default listing changes:

1. Update constants in `src/shared/constants.ts`.
2. Validate ABIs if function signatures changed.
3. Rebuild:
```bash
npx tsc --noEmit
npm run build
```
4. Smoke test:
- `shll-run init` still returns disabled
- raw calldata still blocks undecodable recipients
- basic read commands still work

## Expected Output Format

All runtime responses should stay machine-friendly JSON:

- Success: `{"status":"success", ...}`
- Error: `{"status":"error","errorCode":"...", "message":"...", ...}`

## Links

- Website: https://shll.run
- npm: https://www.npmjs.com/package/shll-skills
- Repo: https://github.com/kledx/shll-skills
