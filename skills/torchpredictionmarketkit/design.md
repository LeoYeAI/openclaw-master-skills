# Torch Prediction Market Kit — Design Document

> Autonomous vault-based prediction market bot for Torch Market on Solana. Version 2.0.1.

## Overview

The Torch Prediction Market Kit is a single-purpose bot that creates binary prediction markets as Torch tokens, monitors them, and resolves them at deadline using an oracle. It generates a disposable agent keypair in-process, verifies vault linkage, and runs a continuous market cycle loop. All SOL routes through the vault — the agent wallet holds nothing of value.

**Settlement model: token-as-signal.** No payout mechanism. The token price IS the prediction. Buying = betting YES, selling = betting NO. At resolution, the bot records the outcome. The bonding curve and treasury do the work.

The bot is built on `torchsdk@3.7.23` and targets the Torch Market on-chain program (`8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`). It uses the SDK's `buildCreateTokenTransaction` and `buildBuyTransaction` for market creation, `getToken` and `getHolders` for monitoring, and CoinGecko for oracle resolution.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│               PREDICTION MARKET BOT                       │
│                                                           │
│  main()                                                   │
│    ├── loadConfig()           → validate env vars          │
│    ├── Keypair.generate()     → disposable agent keypair   │
│    ├── getVault()             → verify vault exists         │
│    ├── getVaultForWallet()    → verify agent linked         │
│    ├── loadMarkets()          → load market definitions     │
│    └── while (true)                                        │
│         └── marketCycle()                                  │
│              ├── createPendingMarkets()                    │
│              │    ├── buildCreateTokenTransaction()        │
│              │    └── buildBuyTransaction(vault)           │
│              ├── snapshotActiveMarkets()                   │
│              │    ├── getToken(mint)                       │
│              │    └── getHolders(mint)                     │
│              └── resolveExpiredMarkets()                   │
│                   └── checkOracle() → record outcome       │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    torchsdk v3.7.22                        │
│                                                           │
│  Read-only: getTokens, getToken, getHolders, getVault     │
│  Builders:  buildCreateTokenTransaction, buildBuyTransaction│
│  Confirm:   confirmTransaction                            │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│              Solana RPC (mainnet / validator)              │
└──────────────────────────────────────────────────────────┘
```

## Module Structure

```
packages/kit/src/
├── index.ts        Entry point — keypair, vault verification, market cycle loop
├── config.ts       loadConfig() — validates env vars
├── types.ts        Market, Oracle, Snapshot, Config interfaces
├── markets.ts      Market CRUD — create token, seed liquidity, snapshot, resolve
├── oracle.ts       Resolution logic — price feed checks (CoinGecko)
└── utils.ts        Helpers — sol(), createLogger(), decodeBase58()
```

### Dependency Graph

```
index.ts ──→ config.ts ──→ types.ts
         ──→ markets.ts ──→ types.ts
         │                ──→ oracle.ts ──→ types.ts
         ──→ utils.ts ──→ types.ts
         ──→ torchsdk (external)
         ──→ @solana/web3.js (external)
```

No circular dependencies. `index.ts` is the single entry point. `config.ts` handles environment validation. `markets.ts` manages the full market lifecycle. `oracle.ts` handles price feed resolution. `utils.ts` provides formatting helpers.

---

## Design Principles

### 1. Single Purpose

The bot does three things: create markets, monitor them, and resolve them. No trading strategy, no arbitrage, no portfolio management. One loop, three responsibilities.

### 2. Vault-First

Every market creation and liquidity seed routes through the Torch Vault. SOL comes from the vault. Purchased tokens go to the vault ATA. The agent wallet never holds value. This is enforced by passing `vault: vaultCreator` to `buildBuyTransaction`.

### 3. Disposable Keypair

By default, the agent keypair is generated fresh on every startup with `Keypair.generate()`. Optionally, `SOLANA_PRIVATE_KEY` can be provided (base58 or JSON byte array) to persist the agent wallet across restarts. In both cases, the keypair exists only in runtime memory and is never logged or transmitted.

### 4. Markets as Tokens

Each prediction market = a Torch token. The bonding curve provides deterministic pricing. No LP setup needed. Price = sentiment. The 10% treasury accumulates value from every buy.

### 5. File-Based State

`markets.json` is the source of truth. No database, no indexer, no API server. The bot reads the file, creates pending markets, updates status, and writes back.

### 6. Oracle Simplicity

Two oracle types: price feed (CoinGecko public API) and manual (edit JSON). No complex oracle networks, no Chainlink, no Pyth. Simple is better.

### 7. Fail-Safe Startup

Before entering the market cycle loop, the bot verifies:
1. `getVault(connection, vaultCreator)` — vault exists on-chain
2. `getVaultForWallet(connection, agentPubkey)` — agent is linked to the vault

If either check fails, the bot exits with clear instructions.

### 8. Graceful Error Handling

The market cycle catches all errors at the cycle level. A failed RPC call, a missing token, or a failed creation never crashes the bot — it logs the error and moves to the next market. Individual market iterations use try/catch to skip unavailable data.

---

## Market Lifecycle

```
pending ──→ active ──→ resolved
              │
              └──→ cancelled
```

1. **Pending** — Market defined in `markets.json`, no token created yet
2. **Active** — Token created on Torch, users can trade on bonding curve
3. **Resolved** — Deadline passed, oracle checked, outcome recorded (yes/no)
4. **Cancelled** — Market removed before resolution (manual only)

## Market Cycle Algorithm

```
for each market in markets file:

  if status === 'pending':
    → buildCreateTokenTransaction(name, symbol, metadata_uri)
    → sign + submit + confirm
    → buildBuyTransaction(vault, mint, initialLiquidityLamports)
    → sign + submit + confirm
    → update status to 'active', save mint address

  if status === 'active':
    → getToken(mint) for price, volume, holders
    → log snapshot
    → if now >= deadline:
        → checkOracle(market.oracle)
        → update status to 'resolved', record outcome

  if status === 'resolved':
    → skip (already settled)
```

---

## Oracle Resolution

### Price Feed Oracle

Fetches current price from CoinGecko public API:

```
GET https://api.coingecko.com/api/v3/simple/price?ids={asset}&vs_currencies=usd
```

- No API key required
- Compares against target: `above` checks price > target, `below` checks price < target
- Rate limited to 1 call per market per cycle
- If CoinGecko is unreachable, market stays unresolved until next cycle

### Manual Oracle

Outcome set manually by editing markets.json. Bot detects the change and records it. Returns `'unresolved'` until manually set.

---

## Configuration

```typescript
interface BotConfig {
  rpcUrl: string           // SOLANA_RPC_URL env var, fallback RPC_URL (required)
  vaultCreator: string     // VAULT_CREATOR env var (required)
  privateKey: string | null // SOLANA_PRIVATE_KEY env var (optional)
  scanIntervalMs: number   // SCAN_INTERVAL_MS env var (default 60000, min 5000)
  logLevel: LogLevel       // LOG_LEVEL env var (default 'info')
  marketsPath: string      // MARKETS_PATH env var (default './markets.json')
}
```

### Validation

- `SOLANA_RPC_URL` must be set, fallback `RPC_URL` (throws on missing)
- `VAULT_CREATOR` must be set (throws on missing)
- `SCAN_INTERVAL_MS` must be >= 5000 (prevents RPC rate limiting)
- `LOG_LEVEL` must be one of `debug`, `info`, `warn`, `error`

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@solana/web3.js` | 1.98.4 | Connection, Keypair, Transaction, sendRawTransaction |
| `torchsdk` | 3.7.22 | Token queries, token creation, buy builder, vault queries, confirmation |

| Dev Package | Version | Purpose |
|-------------|---------|---------|
| `@types/node` | 20.19.33 | TypeScript node types |
| `prettier` | 3.8.1 | Code formatting |
| `typescript` | 5.9.3 | Compilation |

---

## E2E Test Coverage

Tests run against a Surfpool mainnet fork:

| Test | What It Validates |
|------|-------------------|
| Connection | RPC reachable, Solana version |
| loadMarkets | Market file parsing and validation |
| checkPriceFeed | CoinGecko oracle returns valid data |
| buildCreateTokenTransaction | Token creation builds correctly |
| getTokens | Discovers bonding/migrated tokens |
| getToken | Token metadata, price, status |
| getHolders | Holder enumeration |
| getVaultForWallet | Returns null for unlinked wallet |
| In-process keypair | Keypair.generate() works, no external key |

**Result:** 9 passed, 1 informational (Surfpool `getTokenLargestAccounts` limitation for Token-2022).
