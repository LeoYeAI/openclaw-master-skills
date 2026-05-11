# Torch Domain Auction Bot -- Design Document

> Domains become tokens. Tokens become collateral. Top holder controls the domain. Version 2.0.1.

## Overview

The Torch Domain Auction Bot is a single-package kit that implements a domain lending protocol on Torch Market. Domains are launched as tokens via bonding curves, permanently linked after migration, and backed by a built-in lending market. The top token holder controls the domain. Holders can borrow SOL against their tokens, but if they're liquidated, the domain lease rotates to the new top holder.

The kit runs the keeper infrastructure: domain discovery (scraper), token launching, lending market scanning, risk scoring, vault-routed liquidation, and automatic lease rotation. Everything ships as one npm package (`torch-domain-auction-bot`).

Built on `torchsdk@3.7.23`. Targets the Torch Market program (`8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`).

---

## The Domain Lending Model

This is the core idea the architecture serves:

```
DOMAIN → TOKEN → COLLATERAL → LOAN → LIQUIDATION → ROTATION
```

1. A domain is launched as a Torch Market token (bonding curve)
2. After migration, the token is permanently linked to the domain
3. The top token holder controls the domain (perpetual lease)
4. Any holder can lock tokens as collateral and borrow SOL
5. If a loan goes underwater (LTV > 65%), it gets liquidated
6. Liquidation moves collateral → top holder changes → domain rotates

The consequence of liquidation is not just financial -- you lose the domain. This creates natural incentives for healthy lending positions and gives the domain market real dynamics.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KIT PACKAGE (packages/kit)                      │
│                                                                    │
│  src/scraper/    Domain Discovery                                  │
│    providers/expired-domains.ts → scrape registrar feeds           │
│    providers/availability.ts    → check domain availability        │
│    evaluator.ts                 → score domain quality             │
│    ticker.ts                    → generate token symbols           │
│    scanner.ts                   → orchestrate the pipeline         │
│                                     │ domain candidates            │
│                                     ▼                              │
│  src/            Bot Core                                          │
│    main()                                                          │
│      ├── loadConfig()              → validate env, load keypair    │
│      ├── getVault()                → vault must exist              │
│      ├── getVaultForWallet()       → agent must be linked          │
│      └── runMonitor()                                              │
│           │                                                        │
│           ├── scanForLendingMarkets()                               │
│           │    ├── getTokens({ status: 'migrated' })               │
│           │    ├── getToken(mint) + getLendingInfo(mint)            │
│           │    └── discoverBorrowers() via getHolders + getLoanPos  │
│           │                                                        │
│           ├── updateLeases()                                       │
│           │    ├── expire stale leases                             │
│           │    ├── checkTopHolder(mint) for each domain token      │
│           │    └── create/rotate lease if holder changed           │
│           │                                                        │
│           └── for each token with active loans:                    │
│                ├── update price history                            │
│                ├── WalletProfiler.profile(borrower)                │
│                │    ├── verifySaid(address)                        │
│                │    └── analyzeTradeHistory(address)               │
│                ├── scoreLoan(token, borrower, position, profile)   │
│                │    ├── LTV proximity     (35%)                    │
│                │    ├── price momentum    (25%)                    │
│                │    ├── wallet reputation (20%)                    │
│                │    └── interest burden   (20%)                    │
│                └── Liquidator.tryLiquidate(connection, scored)     │
│                     ├── check: liquidatable? above threshold?      │
│                     ├── buildLiquidateTransaction(vault=creator)   │
│                     ├── partialSign(agentKeypair)                  │
│                     └── sendRawTransaction → confirmTransaction    │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      torchsdk v3.7.23                              │
│                                                                    │
│  Read queries: getTokens, getToken, getLendingInfo, getHolders,    │
│                getLoanPosition, getVault, getVaultForWallet         │
│  Builders:     buildLiquidateTransaction, buildCreateTokenTx       │
│  Identity:     verifySaid                                          │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│               Solana RPC + Raydium + Torch Program                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### Bot Core (`src/`)

| File | Role | Lines |
|------|------|-------|
| `index.ts` | Entry point -- vault verification, startup banner, CLI routing, all exports | ~130 |
| `config.ts` | Env validation, ephemeral keypair generation, vault creator loading | ~80 |
| `monitor.ts` | Main scan loop -- scan, score, liquidate, rotate leases | ~83 |
| `scanner.ts` | Lending market discovery, borrower probing | ~107 |
| `liquidator.ts` | Vault-routed liquidation with safety checks | ~89 |
| `risk-scorer.ts` | Four-factor weighted risk scoring | ~89 |
| `wallet-profiler.ts` | SAID verification, trade history, caching | ~127 |
| `launcher.ts` | Domain token creation via `buildCreateTokenTransaction` | ~39 |
| `domain-manager.ts` | Lease tracking, top holder checking, rotation | ~72 |
| `ticker.ts` | Token symbol generation from domain names | ~35 |
| `logger.ts` | Structured logger with child logger support (shared across all modules) | ~35 |
| `types.ts` | All interfaces -- BotConfig, MonitoredToken, ScoredLoan, etc. | ~110 |
| `utils.ts` | sleep, sol, bpsToPercent, clamp, decodeBase58 | ~34 |

### Scraper (`src/scraper/`)

| File | Role |
|------|------|
| `index.ts` | CLI entry, pipeline orchestration |
| `scanner.ts` | Domain scanning orchestrator |
| `evaluator.ts` | Quality scoring (length, TLD, keywords, market signals) |
| `ticker.ts` | Symbol generation |
| `config.ts` | Scraper config (env vars) |
| `types.ts` | Scraper types (re-exports LogLevel from parent) |
| `providers/expired-domains.ts` | Expiring domain feed |
| `providers/availability.ts` | Domain availability checking |

---

## Design Principles

### 1. Domain = Token (Permanent)

After migration, the link between domain and token is immutable. No admin can delist it. No expiry timer. The token IS the domain's on-chain identity. This is the foundation everything else builds on.

### 2. Top Holder = Domain Controller

The `domain-manager.ts` module continuously tracks the top holder for each domain token. When the top holder changes (purchase, liquidation, transfer), the lease rotates. This is checked every scan cycle.

The lease is a 7-day window by default, but the top holder can change at any time. The lease serves as a debounce -- it prevents the domain from flipping on every small trade.

### 3. Vault-First

Every liquidation routes through the Torch Vault. The `vault` parameter is passed to `buildLiquidateTransaction`, causing:
- Vault PDA derived from `vaultCreator` (`["torch_vault", creator]`)
- Wallet link PDA derived from `liquidator` (`["vault_wallet", wallet]`)
- SOL debited from vault, collateral tokens credited to vault ATA

The agent never holds value. The vault is the economic boundary.

### 4. Risk Scoring Over Simple Threshold

The liquidation-kit liquidates every position above the 65% threshold. This bot is more selective -- it scores each position across four factors and only liquidates above a configurable risk threshold. This allows the operator to tune aggressiveness.

### 5. Disposable Keypair

By default, `Keypair.generate()` on every startup. Optionally, `SOLANA_PRIVATE_KEY` (base58 or JSON byte array) persists the agent across restarts. The keypair exists only in runtime memory.

### 6. Fail-Safe Startup

Before entering the scan loop:
1. `getVault(connection, vaultCreator)` -- vault must exist
2. `getVaultForWallet(connection, agentPubkey)` -- agent must be linked

Failure exits with clear instructions. The bot never runs with an invalid vault.

---

## Scan Algorithm

```
scanForLendingMarkets():
  get migrated tokens (getTokens, limit=depth)
  for each token:
    skip if scanned <30s ago
    fetch detail + lending info
    if active_loans > 0:
      probe top 20 holders for loan positions
    build/update MonitoredToken

updateLeases():
  expire leases past duration
  for each domain token:
    check top holder (getHolders, limit=1)
    if holder != current lessee:
      expire old lease, create new

scoring + liquidation:
  for each token with borrowers:
    update price history
    for each borrower:
      get loan position
      profile wallet (SAID + trades, cached 60s)
      score: LTV proximity * 0.35
           + price momentum * 0.25
           + wallet risk    * 0.20
           + interest burden * 0.20
      if liquidatable AND risk >= threshold AND profit >= minimum:
        buildLiquidateTransaction(vault=creator)
        sign + send + confirm
```

### Risk Score Factors

| Factor | Weight | What It Measures | Range |
|--------|--------|-----------------|-------|
| LTV Proximity | 35% | How close current LTV is to 65% threshold | 0-100 |
| Price Momentum | 25% | Recent price trend (drop = higher risk) | 0-100 |
| Wallet Risk | 20% | SAID verification, trade history, win rate | 0-100 |
| Interest Burden | 20% | Accrued interest relative to borrowed amount | 0-100 |

A score of 60+ (default threshold) with the position being `liquidatable` triggers a liquidation attempt.

---

## Domain Lifecycle

```
┌─────────┐     ┌────────────┐     ┌───────────┐
│ DISCOVER │ ──→ │  EVALUATE  │ ──→ │  LAUNCH   │
│ (scraper)│     │ (quality)  │     │ (bonding) │
└─────────┘     └────────────┘     └─────┬─────┘
                                         │
                                    bonding completes
                                         │
                                         ▼
                                   ┌───────────┐
                                   │  MIGRATE  │
                                   │ (raydium) │
                                   └─────┬─────┘
                                         │
                              domain permanently linked
                                         │
                    ┌────────────────────┼──────────────────────┐
                    │                    │                      │
                    ▼                    ▼                      ▼
              ┌───────────┐      ┌────────────┐        ┌────────────┐
              │   TRADE   │      │   LEND     │        │   LEASE    │
              │ (buy/sell)│      │ (borrow)   │        │ (top holder│
              └───────────┘      └──────┬─────┘        │  controls) │
                                        │              └──────┬─────┘
                                   if underwater              │
                                        │                     │
                                        ▼                     │
                                 ┌────────────┐               │
                                 │ LIQUIDATE  │───────────────┘
                                 │ (keeper)   │  collateral moves
                                 └────────────┘  → holder changes
                                                 → lease rotates
```

---

## Vault Integration

### Liquidation Transaction

```typescript
const result = await buildLiquidateTransaction(connection, {
  mint: scored.mint,
  liquidator: this.config.walletKeypair.publicKey.toBase58(),
  borrower: scored.borrower,
  vault: this.config.vaultCreator,
})
```

### Safety Checks in Liquidator

The `tryLiquidate` method checks four conditions before executing:
1. Position health is `liquidatable` (not `healthy` or `warning`)
2. Risk score exceeds configured threshold
3. Estimated profit exceeds minimum
4. Position is not already healthy (redundant safety check)

Only after all four pass does it build and submit the transaction.

---

## Configuration

```typescript
interface BotConfig {
  rpcUrl: string            // SOLANA_RPC_URL (required)
  walletKeypair: Keypair    // generated or loaded from SOLANA_PRIVATE_KEY
  vaultCreator: string      // VAULT_CREATOR (required)
  scanIntervalMs: number    // BOT_SCAN_INTERVAL_MS (default 60000, min 5000)
  scoreIntervalMs: number   // BOT_SCORE_INTERVAL_MS (default 15000)
  minProfitLamports: number // BOT_MIN_PROFIT_LAMPORTS (default 10000000)
  riskThreshold: number     // BOT_RISK_THRESHOLD (default 60)
  priceHistoryDepth: number // BOT_PRICE_HISTORY_DEPTH (default 20)
  logLevel: LogLevel        // BOT_LOG_LEVEL (default 'info')
}
```

---

## Dependencies

All pinned to exact versions. No `^` or `~` ranges.

| Package | Version | Purpose |
|---------|---------|---------|
| `@solana/web3.js` | 1.98.4 | Solana RPC, keypair, transaction |
| `torchsdk` | 3.7.23 | Torch Market SDK |
| `@coral-xyz/anchor` | 0.32.1 | Anchor program interaction |
| `@solana/spl-token` | 0.4.14 | Token-2022 operations |
| `bs58` | 6.0.0 | Base58 encoding |

| Dev Package | Version | Purpose |
|-------------|---------|---------|
| `@types/node` | 20.19.33 | TypeScript types |
| `prettier` | 3.8.1 | Code formatting |
| `typescript` | 5.9.3 | Compilation |

---

## Why This Architecture

The domain lending model composes five Torch primitives that already exist:

1. **Bonding curves** -- price discovery for new domains
2. **Raydium migration** -- permanent liquidity after bonding
3. **Lending markets** -- borrow against domain token positions
4. **Vaults** -- safe custody for autonomous keeper operations
5. **Liquidation** -- market health enforcement + domain rotation

None of these were designed specifically for domains. They're general-purpose DeFi primitives. This kit shows how they compose into something new: a domain lending protocol where token position equals domain control, and liquidation has consequences beyond capital loss.

The same pattern works for any asset class. Replace "domain" with "NFT" or "governance seat" or "bandwidth allocation" and the architecture is identical. The bot is the keeper. The vault is the treasury. The token is the key. The lending market is the mechanism. Liquidation is the enforcement.
