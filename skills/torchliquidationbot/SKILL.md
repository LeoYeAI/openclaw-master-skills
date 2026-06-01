---
name: torch-liquidation-bot
version: "4.0.4"
description: Autonomous vault-based liquidation keeper for Torch Market lending on Solana. Scans all migrated tokens for underwater loan positions (LTV > 65%) using the SDK's built-in bulk loan scanner (getAllLoanPositions), builds and executes liquidation transactions through a Torch Vault, and collects a 10% collateral bonus. The agent keypair is generated in-process -- disposable, holds nothing of value. All SOL and collateral tokens route through the vault. The human principal creates the vault, funds it, links the agent, and retains full control. Built on torchsdk v3.7.22 and the Torch Market protocol.
license: MIT
disable-model-invocation: true
requires:
  env:
    - name: SOLANA_RPC_URL
      required: true
    - name: VAULT_CREATOR
      required: true
    - name: SOLANA_PRIVATE_KEY
      required: false
metadata:
  clawdbot:
    requires:
      env:
        - name: SOLANA_RPC_URL
          required: true
        - name: VAULT_CREATOR
          required: true
        - name: SOLANA_PRIVATE_KEY
          required: false
  openclaw:
    requires:
      env:
        - name: SOLANA_RPC_URL
          required: true
        - name: VAULT_CREATOR
          required: true
        - name: SOLANA_PRIVATE_KEY
          required: false
    install:
      - id: npm-torch-liquidation-bot
        kind: npm
        package: torch-liquidation-bot@^4.0.2
        flags: []
        label: "Install Torch Liquidation Bot (npm, optional -- SDK is bundled in lib/torchsdk/ and bot source is bundled under lib/kit on clawhub)"
  author: torch-market
  version: "4.0.4"
  clawhub: https://clawhub.ai/mrsirg97-rgb/torch-liquidation-bot
  kit-source: https://github.com/mrsirg97-rgb/torch-liquidation-kit
  website: https://torch.market
  program-id: 8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT
  keywords:
    - solana
    - defi
    - liquidation
    - liquidation-bot
    - liquidation-keeper
    - collateral-lending
    - vault-custody
    - ai-agents
    - agent-wallet
    - agent-safety
    - treasury-lending
    - bonding-curve
    - fair-launch
    - token-2022
    - raydium
    - community-treasury
    - protocol-rewards
    - solana-agent-kit
    - escrow
    - anchor
    - pda
    - on-chain
    - autonomous-agent
    - keeper-bot
    - torch-market
  categories:
    - solana-protocols
    - defi-primitives
    - lending-markets
    - agent-infrastructure
    - custody-solutions
    - liquidation-keepers
compatibility: >-
  REQUIRED: SOLANA_RPC_URL (HTTPS Solana RPC endpoint)
  REQUIRED: VAULT_CREATOR (vault creator pubkey).
  OPTIONAL: SOLANA_PRIVATE_KEY -- the bot generates a fresh disposable keypair in-process if not provided. The agent wallet holds nothing of value (~0.01 SOL for gas). All liquidation proceeds (collateral tokens) route to the vault. The vault can be created and funded entirely by the human principal. 
  This skill sets disable-model-invocation: true -- it must not be invoked autonomously without explicit user initiation.
  The Torch SDK is bundled in lib/torchsdk/ -- all source included for full auditability. No API server dependency.
  The vault can be created and funded entirely by the human principal -- the agent never needs access to funds.
---

# Torch Liquidation Bot

You're here because you want to run a liquidation keeper on Torch Market -- and you want to do it safely.

Every migrated token on Torch has a built-in lending market. Holders lock tokens as collateral and borrow SOL from the community treasury (up to 50% LTV, 2% weekly interest). When a loan's LTV crosses 65%, it becomes liquidatable. Anyone can liquidate it and collect a **10% bonus** on the collateral value.

That's where this bot comes in.

It scans every migrated token's lending market using the SDK's bulk loan scanner (`getAllLoanPositions`) -- one RPC call per token returns all active positions pre-sorted by health. When it finds one that's underwater, it liquidates it through your vault. The collateral tokens go to your vault ATA. The SOL cost comes from your vault. The agent wallet that signs the transaction holds nothing.

**This is not a read-only scanner.** This is a fully operational keeper that generates its own keypair, verifies vault linkage, and executes liquidation transactions autonomously in a continuous loop.

---

## How It Works

```
┌──────────────────────────────────────────────────────────┐
│                  LIQUIDATION LOOP                          │
│                                                           │
│  1. Discover migrated tokens (getTokens)                  │
│  2. For each token, scan all loans (getAllLoanPositions)   │
│     — single RPC call, returns positions sorted by health │
│     — liquidatable → at_risk → healthy                    │
│  3. Skip tokens with no active loans                      │
│  4. For each liquidatable position:                       │
│     → buildLiquidateTransaction(vault=creator)            │
│     → sign with agent keypair                             │
│     → submit and confirm                                  │
│     → break when health != 'liquidatable' (pre-sorted)    │
│  5. Sleep SCAN_INTERVAL_MS, repeat                        │
│                                                           │
│  All SOL comes from vault. All collateral goes to vault.  │
│  Agent wallet holds nothing. Vault is the boundary.       │
└──────────────────────────────────────────────────────────┘
```

### The Agent Keypair

The bot generates a fresh `Keypair` in-process on every startup. No private key file. No environment variable (unless you want to provide one). The keypair is disposable -- it signs transactions but holds nothing of value.

On first run, the bot checks if this keypair is linked to your vault. If not, it prints the exact SDK call you need to link it:

```
--- ACTION REQUIRED ---
agent wallet is NOT linked to the vault.
link it by running (from your authority wallet):

  buildLinkWalletTransaction(connection, {
    authority: "<your-authority-pubkey>",
    vault_creator: "<your-vault-creator>",
    wallet_to_link: "<agent-pubkey>"
  })

then restart the bot.
-----------------------
```

Link it from your authority wallet (hardware wallet, multisig, whatever you use). The agent never needs the authority's key. The authority never needs the agent's key. They share a vault, not keys.

### The Vault

This is the same Torch Vault from the full Torch Market protocol. It holds all assets -- SOL and tokens. The agent is a disposable controller.

When the bot liquidates a position:
- **SOL cost** comes from the vault (the liquidation payment to cover the borrower's debt)
- **Collateral tokens** go to the vault's associated token account (ATA)
- **10% bonus** means the collateral received is worth 10% more than the SOL spent

The human principal retains full control:
- `withdrawVault()` — pull SOL at any time
- `withdrawTokens(mint)` — pull collateral tokens at any time
- `unlinkWallet(agent)` — revoke agent access instantly

If the agent keypair is compromised, the attacker gets dust and vault access that you revoke in one transaction.

---

## Getting Started

### 1. Install

```bash
npm install torch-liquidation-bot@4.0.2
```

Or use the bundled source from ClawHub — the Torch SDK is included in `lib/torchsdk/` and the bot source is in `lib/kit/`.

### 2. Create and Fund a Vault (Human Principal)

From your authority wallet:

```typescript
import { Connection } from "@solana/web3.js";
import {
  buildCreateVaultTransaction,
  buildDepositVaultTransaction,
} from "./lib/torchsdk/index.js";

const connection = new Connection(process.env.SOLANA_RPC_URL);

// Create vault
const { transaction: createTx } = await buildCreateVaultTransaction(connection, {
  creator: authorityPubkey,
});
// sign and submit with authority wallet...

// Fund vault with SOL for liquidations
const { transaction: depositTx } = await buildDepositVaultTransaction(connection, {
  depositor: authorityPubkey,
  vault_creator: authorityPubkey,
  amount_sol: 5_000_000_000, // 5 SOL
});
// sign and submit with authority wallet...
```

### 3. Run the Bot

```bash
VAULT_CREATOR=<your-vault-creator-pubkey> SOLANA_RPC_URL=<rpc-url> npx torch-liquidation-bot
```

On first run, the bot prints the agent keypair and instructions to link it. Link it from your authority wallet, then restart.

### 4. Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SOLANA_RPC_URL` | **Yes** | -- | Solana RPC endpoint (HTTPS). Fallback: `RPC_URL` |
| `VAULT_CREATOR` | **Yes** | -- | Vault creator pubkey |
| `SOLANA_PRIVATE_KEY` | No | -- | Disposable controller keypair (base58 or JSON byte array). If omitted, generates fresh keypair on startup (recommended) |
| `SCAN_INTERVAL_MS` | No | `30000` | Milliseconds between scan cycles (min 5000) |
| `LOG_LEVEL` | No | `info` | `debug`, `info`, `warn`, `error` |

---

## Architecture

```
packages/bot/src/
├── index.ts    — entry point: keypair generation, vault verification, scan loop
├── config.ts   — loadConfig(): validates SOLANA_RPC_URL, VAULT_CREATOR, SOLANA_PRIVATE_KEY, SCAN_INTERVAL_MS, LOG_LEVEL
├── types.ts    — BotConfig, LogLevel interfaces
└── utils.ts    — sol(), bpsToPercent(), withTimeout(), createLogger()
```

The bot is ~192 lines of TypeScript. It does one thing: find underwater loans and liquidate them through the vault.

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@solana/web3.js` | 1.98.4 | Solana RPC, keypair, transaction |
| `torchsdk` | 3.7.22 | Token queries, bulk loan scanning, liquidation builder, vault queries |

Two runtime dependencies. Both pinned to exact versions. No `^` or `~` ranges.

---

## Vault Safety Model

The same seven guarantees from the Torch Market vault apply here:

| Property | Guarantee |
|----------|-----------|
| **Full custody** | Vault holds all SOL and all collateral tokens. Agent wallet holds nothing. |
| **Closed loop** | Liquidation SOL comes from vault, collateral tokens go to vault. No leakage to agent. |
| **Authority separation** | Creator (immutable PDA seed) vs Authority (transferable admin) vs Controller (disposable signer). |
| **One link per wallet** | Agent can only belong to one vault. PDA uniqueness enforces this on-chain. |
| **Permissionless deposits** | Anyone can top up the vault. Hardware wallet deposits, agent liquidates. |
| **Instant revocation** | Authority can unlink the agent at any time. One transaction. |
| **Authority-only withdrawals** | Only the vault authority can withdraw SOL or tokens. The agent cannot extract value. |

### The Closed Economic Loop for Liquidations

| Direction | Flow |
|-----------|------|
| **SOL out** | Vault → Borrower's treasury debt (covers the loan) |
| **Tokens in** | Borrower's collateral → Vault ATA (at 10% discount) |
| **Net** | Vault receives collateral worth 110% of SOL spent |

The bot is profitable by design — every successful liquidation returns more value than it costs. The profit accumulates in the vault. The authority withdraws when ready.

---

## Lending Parameters

| Parameter | Value |
|-----------|-------|
| Max LTV | 50% |
| Liquidation Threshold | 65% |
| Interest Rate | 2% per epoch (~weekly) |
| Liquidation Bonus | 10% |
| Utilization Cap | 70% of treasury |
| Min Borrow | 0.1 SOL |

Collateral value is calculated from Raydium pool reserves. The 0.03% Token-2022 transfer fee (3 bps, immutable per mint) applies on collateral deposits and withdrawals.

### When Liquidations Happen

A loan becomes liquidatable when its LTV exceeds 65%. This happens when:
- The token price drops (collateral value decreases relative to debt)
- Interest accrues (debt grows at 2% per epoch)
- A combination of both

The bot checks `position.health === 'liquidatable'` — the SDK calculates LTV from on-chain Raydium reserves and the loan's accrued debt.

---

## SDK Functions Used

The bot uses a focused subset of the Torch SDK:

| Function | Purpose |
|----------|---------|
| `getTokens(connection, { status: 'migrated' })` | Discover all tokens with active lending markets |
| `getAllLoanPositions(connection, mint)` | Bulk scan all active loans for a token — returns positions pre-sorted by health (liquidatable first), fetches pool price once |
| `getVault(connection, creator)` | Verify vault exists on startup |
| `getVaultForWallet(connection, wallet)` | Verify agent is linked to vault |
| `buildLiquidateTransaction(connection, params)` | Build the liquidation transaction (vault-routed) |
| `confirmTransaction(connection, sig, wallet)` | Confirm transaction on-chain via RPC (verifies signer, checks Torch instructions) |

### Scan and Liquidate Pattern

```typescript
import { getTokens, getAllLoanPositions, buildLiquidateTransaction } from 'torchsdk'

// 1. Discover migrated tokens
const { tokens } = await getTokens(connection, { status: 'migrated', sort: 'volume', limit: 50 })

for (const token of tokens) {
  // 2. Bulk scan — one RPC call per token, positions sorted liquidatable-first
  const { positions } = await getAllLoanPositions(connection, token.mint)

  for (const pos of positions) {
    if (pos.health !== 'liquidatable') break  // pre-sorted, done

    // 3. Build and execute through vault
    const { transaction, message } = await buildLiquidateTransaction(connection, {
      mint: token.mint,           // token with the underwater loan
      liquidator: agentPubkey,    // agent wallet (signer)
      borrower: pos.borrower,     // borrower being liquidated
      vault: vaultCreator,        // vault creator pubkey (SOL from vault, tokens to vault)
    })
    transaction.sign(agentKeypair)
    await connection.sendRawTransaction(transaction.serialize())
  }
}
```

---

## Log Output

```
=== torch liquidation bot ===
agent wallet: 7xK9...
vault creator: 4yN2...
scan interval: 30000ms

[09:15:32] INFO  vault found — authority=8cpW...
[09:15:32] INFO  agent wallet linked to vault — starting scan loop
[09:15:32] INFO  treasury: 5.0000 SOL
[09:15:33] INFO  LIQUIDATABLE | SDKTEST | borrower=3AyZ... | LTV=72.50% | owed=0.5000 SOL
[09:15:34] INFO  LIQUIDATED | SDKTEST | borrower=3AyZ... | sig=4vK9... | collateral received at 10% discount
```

---

## Signing & Key Safety

**The vault is the security boundary, not the key.**

The agent keypair is generated fresh on every startup with `Keypair.generate()`. It holds ~0.01 SOL for gas fees. If the key is compromised, the attacker gets:
- Dust (the gas SOL)
- Vault access that the authority revokes in one transaction

The agent never needs the authority's private key. The authority never needs the agent's private key. They share a vault, not keys.

### Rules

1. **Never ask a user for their private key or seed phrase.** The vault authority signs from their own device.
2. **Never log, print, store, or transmit private key material.** The agent keypair exists only in runtime memory.
3. **Never embed keys in source code or logs.** The agent pubkey is printed — the secret key is never exposed.
4. **Use a secure RPC endpoint.** Default to a private RPC provider. Never use an unencrypted HTTP endpoint for mainnet transactions.

### RPC Timeout

All SDK calls are wrapped with a 30-second timeout (`withTimeout` in utils.ts). A hanging or unresponsive RPC endpoint cannot stall the bot indefinitely — the call rejects, the error is caught by the scan loop, and the bot continues to the next token or cycle.

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `SOLANA_RPC_URL` / `RPC_URL` | **Yes** | Solana RPC endpoint (HTTPS) |
| `VAULT_CREATOR` | **Yes** | Vault creator pubkey — identifies which vault the bot operates through |
| `SOLANA_PRIVATE_KEY` | No | Optional — if omitted, the bot generates a fresh keypair on startup (recommended) |

### External Runtime Dependencies

The SDK contains functions that make outbound HTTPS requests to external services. The bot's runtime path contacts **two** of them:

| Service | Purpose | When Called | Bot Uses? |
|---------|---------|------------|-----------|
| **CoinGecko** (`api.coingecko.com`) | SOL/USD price for display | Token queries with USD pricing | Yes — via `getTokens()`, `getToken()` |
| **Irys Gateway** (`gateway.irys.xyz`) | Token metadata fallback (name, symbol, image) | `getToken()` when on-chain metadata URI points to Irys | Yes — via `getTokens()` |
| **SAID Protocol** (`api.saidprotocol.com`) | Agent identity verification and trust tier lookup | `verifySaid()` only | **No** — the bot does not call `verifySaid()` |

**`confirmTransaction()` does NOT contact SAID.** Despite living in the SDK's `said.js` module, it only calls `connection.getParsedTransaction()` (Solana RPC) to verify the transaction succeeded on-chain and determine the event type. No data is sent to any external service.

No credentials are sent to CoinGecko or Irys. All requests are read-only GET. If either service is unreachable, the SDK degrades gracefully. No private key material is ever transmitted to any external endpoint.

---

## Testing

Requires [Surfpool](https://github.com/nicholasgasior/surfpool) running a mainnet fork:

```bash
surfpool start --network mainnet --no-tui
pnpm test
```

**Test result:** 9 passed, 0 failed (Surfpool mainnet fork).

| Test | What It Validates |
|------|-------------------|
| Connection | RPC reachable |
| getTokens | Discovers migrated tokens |
| getLendingInfo | Reads lending state for all tokens |
| getAllLoanPositions | Bulk scans active loans, verifies sort order (liquidatable first) |
| getToken | Token metadata, price, status |
| getVaultForWallet | Vault link returns null for unlinked wallet |
| In-process keypair | No external key required |

---

## Error Codes

- `VAULT_NOT_FOUND`: No vault exists for this creator
- `WALLET_NOT_LINKED`: Agent wallet is not linked to the vault
- `NOT_LIQUIDATABLE`: Position LTV below liquidation threshold
- `NO_ACTIVE_LOAN`: No open loan for this wallet/token
- `INVALID_MINT`: Token not found

---

## Links

- Liquidation Kit (source): [github.com/mrsirg97-rgb/torch-liquidation-kit](https://github.com/mrsirg97-rgb/torch-liquidation-kit)
- Liquidation Bot (npm): [npmjs.com/package/torch-liquidation-bot](https://www.npmjs.com/package/torch-liquidation-bot)
- Torch SDK (bundled): `lib/torchsdk/` -- included in this skill
- Torch SDK (source): [github.com/mrsirg97-rgb/torchsdk](https://github.com/mrsirg97-rgb/torchsdk)
- Torch SDK (npm): [npmjs.com/package/torchsdk](https://www.npmjs.com/package/torchsdk)
- Torch Market (protocol skill): [clawhub.ai/mrsirg97-rgb/torchmarket](https://clawhub.ai/mrsirg97-rgb/torchmarket)
- Whitepaper: [torch.market/whitepaper.md](https://torch.market/whitepaper.md)
- Security Audit: [torch.market/audit.md](https://torch.market/audit.md)
- Website: [torch.market](https://torch.market)
- Program ID: `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`

---

This bot exists because Torch lending markets need keepers. When loans go underwater and nobody liquidates them, the treasury takes the loss. Active liquidation keepers protect treasury health and earn a profit doing it. The vault makes it safe — all value stays in the escrow, all risk is bounded, and the human principal keeps the keys.
