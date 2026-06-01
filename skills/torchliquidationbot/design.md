# Torch Liquidation Bot — Design Document

> Autonomous vault-based liquidation keeper for Torch Market lending on Solana. Version 4.0.2.

## Overview

The Torch Liquidation Bot is a single-purpose keeper that scans Torch Market lending positions and liquidates underwater loans through a Torch Vault. It generates a disposable agent keypair in-process, verifies vault linkage, and runs a continuous scan-liquidate loop. All SOL and collateral tokens route through the vault — the agent wallet holds nothing of value.

The bot is built on `torchsdk@3.7.22` and targets the Torch Market on-chain program (`8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`). It uses the SDK's bulk loan scanner (`getAllLoanPositions`) to discover liquidatable positions and the vault-routed `buildLiquidateTransaction` to execute them.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    LIQUIDATION BOT                         │
│                                                           │
│  main()                                                   │
│    ├── loadConfig()         → validate env vars            │
│    ├── Keypair.generate()   → disposable agent keypair     │
│    ├── getVault()           → verify vault exists           │
│    ├── getVaultForWallet()  → verify agent linked to vault  │
│    └── while (true)                                        │
│         └── scanAndLiquidate()                             │
│              ├── getTokens({ status: 'migrated' })         │
│              ├── getAllLoanPositions(mint)                  │
│              │    → returns positions sorted by health      │
│              │    → break at first non-liquidatable         │
│              ├── buildLiquidateTransaction(vault=creator)   │
│              ├── transaction.sign(agentKeypair)             │
│              ├── connection.sendRawTransaction()            │
│              └── confirmTransaction()                      │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    torchsdk v3.7.22                        │
│                                                           │
│  Read-only queries:                                       │
│    getTokens, getAllLoanPositions                          │
│    getVault, getVaultForWallet                             │
│                                                           │
│  Transaction builder:                                     │
│    buildLiquidateTransaction (vault-routed)                │
│                                                           │
│  Confirmation:                                            │
│    confirmTransaction (on-chain via RPC)                   │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│              Solana RPC (mainnet / validator)              │
│                                                           │
│  getProgramAccounts    getAccountInfo    sendTransaction   │
└──────────────────────────────────────────────────────────┘
```

## Module Structure

```
packages/bot/src/
├── index.ts      Entry point — keypair generation, vault verification, scan loop
├── config.ts     loadConfig() — validates SOLANA_RPC_URL, VAULT_CREATOR, SOLANA_PRIVATE_KEY, SCAN_INTERVAL_MS, LOG_LEVEL
├── types.ts      BotConfig, LogLevel interfaces
└── utils.ts      sol(), bpsToPercent(), createLogger()
```

### Dependency Graph

```
index.ts ──→ config.ts ──→ types.ts
         ──→ utils.ts ──→ types.ts
         ──→ torchsdk (external)
         ──→ @solana/web3.js (external)
```

No circular dependencies. `index.ts` is the single entry point. `config.ts` handles environment validation. `utils.ts` provides formatting helpers. All on-chain interaction goes through `torchsdk`.

---

## Design Principles

### 1. Single Purpose

The bot does one thing: find underwater loans and liquidate them through the vault. No trading, no borrowing, no token creation. One loop, one responsibility.

### 2. Vault-First

Every liquidation routes through the Torch Vault. SOL comes from the vault. Collateral tokens go to the vault ATA. The agent wallet never holds value. This is enforced by passing `vault: vaultCreator` to `buildLiquidateTransaction`.

### 3. Disposable Keypair

By default, the agent keypair is generated fresh on every startup with `Keypair.generate()`. Optionally, `SOLANA_PRIVATE_KEY` can be provided (base58 or JSON byte array) to persist the agent wallet across restarts. In both cases, the keypair exists only in runtime memory and is never logged or transmitted.

### 4. Fail-Safe Startup

Before entering the scan loop, the bot verifies:
1. `getVault(connection, vaultCreator)` — vault exists on-chain
2. `getVaultForWallet(connection, agentPubkey)` — agent is linked to the vault

If either check fails, the bot exits with clear instructions. It never enters the scan loop with an invalid vault or unlinked wallet.

### 5. Graceful Error Handling

The scan loop catches all errors at the cycle level. A failed RPC call or a failed liquidation never crashes the bot — it logs the error and moves to the next cycle. Individual token iterations use try/catch to skip tokens where `getAllLoanPositions` fails.

### 6. Minimal Surface

Two runtime dependencies (`@solana/web3.js`, `torchsdk`), both pinned to exact versions. ~187 lines of TypeScript. Four source files. No database, no API server, no indexer, no websockets.

---

## Scan Algorithm

```
for each migrated token:
  positions = getAllLoanPositions(mint)
  skip if positions is empty

  for each position (pre-sorted: liquidatable → at_risk → healthy):
    break if health !== 'liquidatable'

    → buildLiquidateTransaction(vault=creator)
    → sign with agent keypair
    → submit and confirm
    → log result
```

### Token Discovery

`getTokens(connection, { status: 'migrated', sort: 'volume', limit: 50 })` returns the top 50 migrated tokens by volume. Only migrated tokens have active lending markets.

### Loan Scanning

`getAllLoanPositions(connection, mint)` scans all LoanPosition PDAs for a token via `getProgramAccounts` with discriminator + mint filters. Returns all active positions (borrowed_amount > 0) pre-sorted by health: `liquidatable → at_risk → healthy`. Fetches the Raydium pool price once per call (not per position).

### Loan Health

The SDK computes a `health` field for each position: `'healthy'`, `'at_risk'`, `'liquidatable'`, or `'none'`. The bot only acts on `'liquidatable'` — positions where LTV exceeds the 65% threshold. Because positions are pre-sorted, the bot breaks at the first non-liquidatable position.

---

## Vault Integration

### Liquidation Transaction

```typescript
const { transaction, message } = await buildLiquidateTransaction(connection, {
  mint: token.mint,
  liquidator: agentKeypair.publicKey.toBase58(),
  borrower: position.borrower,
  vault: vaultCreator,
})
```

When `vault` is provided:
- Vault PDA derived from `vaultCreator` (`["torch_vault", creator]`)
- Wallet link PDA derived from `liquidator` (`["vault_wallet", wallet]`)
- SOL for the liquidation comes from the vault
- Collateral tokens go to the vault's ATA for the token mint

### Safety Model

| Property | Implementation |
|----------|---------------|
| Full custody | `vault` param routes all value through vault PDA |
| No extraction | Agent cannot call `withdrawVault` or `withdrawTokens` |
| Instant revocation | Authority calls `unlinkWallet` — bot's next tx fails with `WALLET_NOT_LINKED` |
| Closed loop | SOL out → vault, tokens in → vault ATA |

---

## Configuration

```typescript
interface BotConfig {
  rpcUrl: string           // SOLANA_RPC_URL env var, fallback RPC_URL (required)
  vaultCreator: string     // VAULT_CREATOR env var (required)
  privateKey: string | null // SOLANA_PRIVATE_KEY env var (optional)
  scanIntervalMs: number   // SCAN_INTERVAL_MS env var (default 30000, min 5000)
  logLevel: LogLevel       // LOG_LEVEL env var (default 'info')
}
```

### Validation

- `SOLANA_RPC_URL` must be set, fallback `RPC_URL` (throws on missing)
- `VAULT_CREATOR` must be set (throws on missing)
- `SCAN_INTERVAL_MS` must be >= 5000 (prevents RPC rate limiting)
- `LOG_LEVEL` must be one of `debug`, `info`, `warn`, `error`

---

## Logging

The bot uses a structured logger with level filtering:

```
[HH:MM:SS.mmm] LEVEL message
```

| Level | Purpose |
|-------|---------|
| `debug` | Scan cycle boundaries, token counts, skipped tokens |
| `info` | Vault status, liquidatable positions found, successful liquidations |
| `warn` | Failed liquidation attempts |
| `error` | Scan cycle errors |

---

## E2E Test Coverage

Tests run against a Surfpool mainnet fork:

| Test | What It Validates |
|------|-------------------|
| Connection | RPC reachable, Solana version |
| getTokens | Discovers migrated tokens via discriminator filter |
| getLendingInfo | Reads lending state (rates, thresholds, active loans) |
| getAllLoanPositions | Bulk scans active loans, verifies sort order (liquidatable first) |
| getToken | Token metadata, price, status |
| getVaultForWallet | Returns null for unlinked wallet |
| In-process keypair | Keypair.generate() works, no external key |

**Result:** 9 passed, 0 failed.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@solana/web3.js` | 1.98.4 | Connection, Keypair, Transaction, sendRawTransaction |
| `torchsdk` | 3.7.22 | Token queries, bulk loan scanning, vault queries, liquidation builder, confirmation |

| Dev Package | Version | Purpose |
|-------------|---------|---------|
| `@types/node` | 20.19.33 | TypeScript node types |
| `prettier` | 3.8.1 | Code formatting |
| `typescript` | 5.9.3 | Compilation |

---

## Version History

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial read-only lending scanner. No wallet, no transactions, no state changes. |
| 2.0.0 | Added vault queries (`getVault`, `getVaultForWallet`). Still read-only. |
| 3.0.0 | **Fully operational vault-based liquidation keeper.** In-process keypair generation. Vault-routed `buildLiquidateTransaction`. Continuous scan-liquidate loop. Startup vault and link verification. Updated to `torchsdk@3.2.3`. Kit version 1.0.0. |
| 3.0.2 | Optional `SOLANA_PRIVATE_KEY` support (base58 or JSON byte array) for persistent agent wallet. Inline base58 decoder (no bs58 dependency). `SOLANA_RPC_URL` as primary env var with `RPC_URL` fallback. `VAULT_CREATOR` added to manifest `requires.env`. ClawHub audit consistency fixes. |
| 4.0.0 | **Bulk loan scanning via `getAllLoanPositions`.** Replaces N+1 scan pattern (`getLendingInfo` → `getHolders` → per-holder `getLoanPosition`) with single RPC call per token. Positions pre-sorted by health with early break. Updated to `torchsdk@3.7.22` (V33 buyback removal, 70% utilization cap). Kit version 2.0.0. |
| 4.0.1 | **RPC timeout via `withTimeout`.** Address L-1 Vulnerability with Denial-of-Service.
| 4.0.2 | **Torchsdk Version Bump** update to latest sdk v3.7.23