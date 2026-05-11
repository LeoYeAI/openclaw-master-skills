---
name: torch-domain-auction-bot
version: "2.0.1"
description: Domain lending protocol on Solana. Domains become tokens. Tokens become collateral. Top holder controls the domain. Borrow SOL against your position -- but get liquidated and you lose the domain. Built on torchsdk v3.7.23 and the Torch Market protocol.
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
    primaryEnv: SOLANA_RPC_URL
    install:
      - id: npm-torch-domain-auction-bot
        kind: npm
        package: torch-domain-auction-bot@^2.0.1
        flags: []
        label: "Install Torch Domain Auction Bot (npm, optional -- SDK is bundled in lib/torchsdk/, kit is in lib/kit/)"
  author: torch-market
  version: "2.0.1"
  clawhub: https://clawhub.ai/mrsirg97-rgb/torch-domain-auction-bot
  kit-source: https://github.com/mrsirg97-rgb/torch-domain-auction-bot
  website: https://torch.market
  program-id: 8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT
  keywords:
    - solana
    - defi
    - domains
    - domain-lending
    - domain-collateral
    - domain-lease
    - liquidation
    - vault-custody
    - ai-agents
    - torch-market
  categories:
    - solana-protocols
    - defi-primitives
    - lending-markets
    - domain-services
    - agent-infrastructure
compatibility: >-
  REQUIRED: SOLANA_RPC_URL (HTTPS Solana RPC endpoint)
  REQUIRED: VAULT_CREATOR (vault creator pubkey).
  OPTIONAL: SOLANA_PRIVATE_KEY -- the kit generates a fresh disposable keypair in-process if not provided. The agent wallet holds nothing of value (~0.01 SOL for gas). All token creation and seed liquidity SOL routes through the vault. The vault can be created and funded entirely by the human principal.
  This skill sets disable-model-invocation: true -- it must not be invoked autonomously without explicit user initiation.
  The Torch SDK is bundled in lib/torchsdk/ -- all source included for full auditability. No API server dependency.
  Oracle resolution uses CoinGecko public API (read-only, no key required). The vault can be created and funded entirely by the human principal -- the agent never needs access to funds.
---

# Torch Domain Auction

Domains become tokens. Tokens become collateral. Top holder controls the domain.

---

## The Idea

Every domain has a name. Every name has a price. But who decides that price?

On Torch Market, domains are launched as tokens with bonding curves. The market decides the price. After bonding completes and the token migrates to Raydium, the domain is permanently linked to that token. From that point forward:

- **The top token holder controls the domain.** Buy enough tokens, you get the domain. Someone buys more, they get it.
- **Holders can borrow SOL against their tokens.** Lock your domain tokens as collateral and extract liquidity — up to 50% LTV, 2% weekly interest.
- **Get liquidated, lose the domain.** If your loan goes underwater (LTV > 65%), anyone can liquidate you. Your collateral changes hands. The domain lease rotates to whoever is now the top holder.

This creates something that doesn't exist in traditional domain markets: **a continuously-priced, borrowable, liquid domain asset** with built-in consequences for overleveraging.

The bot in this kit runs the infrastructure side. It discovers promising domains, launches them as tokens, monitors all active lending positions, and liquidates underwater loans through a Torch Vault. When a liquidation happens, the domain automatically rotates.

---

## How Domains Work on Torch

### Phase 1: Launch (Bonding Curve)

A domain is launched as a Torch Market token. The bonding curve creates the initial market — early buyers get a lower price, the curve rises as demand increases. This is the price discovery phase.

```
domain "pixel.art"  →  token PIXEL  →  bonding curve  →  market cap grows
```

Anyone can buy in. The curve sets the price. Trading fees flow to the community treasury.

### Phase 2: Migration (Domain Becomes Permanent)

When the bonding curve completes, the token migrates to a Raydium liquidity pool. At this point, the domain is **permanently linked** to the token. There is no delisting, no expiry, no central authority. The token IS the domain.

### Phase 3: Lending (Borrow Against Your Domain)

After migration, Torch's built-in lending market activates. Any holder can lock their tokens as collateral and borrow SOL from the community treasury.

```
holder locks 10,000 PIXEL tokens  →  borrows 0.5 SOL  →  LTV = 40%
```

The loan accrues 2% interest per epoch (~weekly). As long as the loan stays healthy (LTV < 65%), the borrower keeps their position and their domain control.

### Phase 4: Liquidation (Domain Rotates)

If the token price drops or interest accrues enough to push LTV past 65%, the position becomes liquidatable. A keeper (this bot) pays off the debt using vault SOL and receives the borrower's collateral tokens at a 10% discount.

```
PIXEL price drops  →  LTV hits 68%  →  keeper liquidates  →  collateral moves to vault
                                                            →  top holder changes
                                                            →  domain lease rotates
```

The borrower loses their tokens. The domain rotates to whoever is now the largest holder. The keeper's vault profits from the 10% bonus.

**This is the key insight: liquidation has real consequences beyond money.** The borrower doesn't just lose capital — they lose control of the domain. This natural tension makes the lending market meaningful. Borrowers are incentivized to maintain healthy positions because the domain itself is at stake.

---

## What the Bot Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN AUCTION BOT                              │
│                                                                    │
│  DISCOVER                                                          │
│    scrape expiring domains → evaluate quality → generate tickers   │
│                                                                    │
│  LAUNCH                                                            │
│    buildCreateTokenTransaction → bonding curve → domain = token    │
│                                                                    │
│  MONITOR                                                           │
│    for each domain token:                                          │
│      scan lending markets (getLendingInfo)                          │
│      discover borrowers (getHolders → getLoanPosition)             │
│      profile wallets (SAID verification, trade history)            │
│      score risk (LTV proximity, momentum, wallet, interest)        │
│                                                                    │
│  LIQUIDATE                                                         │
│    if position.health === 'liquidatable' && risk > threshold:      │
│      buildLiquidateTransaction(vault = creator)                    │
│      sign with agent keypair → submit → confirm                    │
│                                                                    │
│  ROTATE                                                            │
│    after liquidation or any holder change:                          │
│      check top holder → update domain lease                        │
│                                                                    │
│  All SOL from vault. All collateral to vault. Agent holds nothing. │
└─────────────────────────────────────────────────────────────────┘
```

### The Scan Loop

The bot runs a continuous loop:

1. **Scan** — discover all migrated domain tokens with active lending markets
2. **Score** — for each borrower, compute a risk score across four weighted factors:
   - LTV proximity (35%) — how close to the 65% liquidation threshold
   - Price momentum (25%) — recent token price trend (drops increase risk)
   - Wallet reputation (20%) — SAID verification status and trade history
   - Interest burden (20%) — accrued interest relative to principal
3. **Liquidate** — execute vault-routed liquidation for positions above the risk threshold
4. **Rotate** — check top holders and update domain leases
5. **Sleep** — wait for the next cycle

### The Agent Keypair

The bot generates a fresh `Keypair` in-process on every startup. No private key file needed. The keypair is disposable — it signs transactions but holds nothing of value (~0.01 SOL for gas).

On first run, the bot verifies vault linkage. If the agent isn't linked, it prints instructions:

```
=== torch domain auction bot ===
agent wallet: 7xK9...
vault creator: 4yN2...
scan interval: 60000ms

--- ACTION REQUIRED ---
agent wallet is NOT linked to the vault.
link it by running (from your authority wallet):

  buildLinkWalletTransaction(connection, {
    authority: "<your-authority-pubkey>",
    vault_creator: "4yN2...",
    wallet_to_link: "7xK9..."
  })

then restart the bot.
-----------------------
```

### The Vault

All economic activity routes through a Torch Vault:

| Direction | What Happens |
|-----------|-------------|
| **Liquidation: SOL out** | Vault SOL pays off the borrower's debt |
| **Liquidation: tokens in** | Borrower's collateral tokens go to vault ATA at 10% discount |
| **Net per liquidation** | Vault receives collateral worth 110% of SOL spent |
| **Domain rotation** | Collateral changes hands → top holder changes → lease rotates |

The human principal retains full control:
- **Withdraw SOL** from the vault at any time
- **Withdraw tokens** (liquidated collateral) at any time
- **Unlink the agent** — revoke bot access in one transaction

If the agent keypair is compromised, the attacker gets dust and vault access you revoke instantly.

---

## Getting Started

### 1. Install

```bash
npm install torch-domain-auction-bot@2.0.1
```

### 2. Create and Fund a Vault

From your authority wallet:

```typescript
import { Connection } from "@solana/web3.js";
import { buildCreateVaultTransaction, buildDepositVaultTransaction } from "torchsdk";

const connection = new Connection(process.env.SOLANA_RPC_URL);

// Create vault
const { transaction: createTx } = await buildCreateVaultTransaction(connection, {
  creator: authorityPubkey,
});
// sign and submit...

// Fund with SOL for liquidations
const { transaction: depositTx } = await buildDepositVaultTransaction(connection, {
  depositor: authorityPubkey,
  vault_creator: authorityPubkey,
  amount_sol: 5_000_000_000, // 5 SOL
});
// sign and submit...
```

### 3. Run

```bash
VAULT_CREATOR=<vault-creator-pubkey> SOLANA_RPC_URL=<rpc-url> npx torch-domain-auction-bot monitor
```

First run prints the agent wallet. Link it from your authority wallet, restart.

### 4. Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SOLANA_RPC_URL` | **Yes** | -- | Solana RPC endpoint. Fallback: `BOT_RPC_URL` |
| `VAULT_CREATOR` | **Yes** | -- | Vault creator pubkey |
| `SOLANA_PRIVATE_KEY` | No | -- | Agent keypair (base58 or JSON). Omit to generate fresh on startup |
| `BOT_SCAN_INTERVAL_MS` | No | `60000` | Scan cycle interval (min 5000) |
| `BOT_SCORE_INTERVAL_MS` | No | `15000` | Score cycle interval |
| `BOT_MIN_PROFIT_LAMPORTS` | No | `10000000` | Min profit to liquidate (0.01 SOL) |
| `BOT_RISK_THRESHOLD` | No | `60` | Min risk score to liquidate (0-100) |
| `BOT_PRICE_HISTORY_DEPTH` | No | `20` | Price snapshots to retain |
| `BOT_LOG_LEVEL` | No | `info` | `debug`, `info`, `warn`, `error` |

---

## Architecture

```
packages/
└── kit/                     Domain auction kit (bot + scraper)
    ├── src/
    │   ├── index.ts           Entry — vault verification, CLI, all exports
    │   ├── config.ts          Env validation, ephemeral keypair
    │   ├── monitor.ts         Scan loop (scan → score → liquidate → rotate)
    │   ├── scanner.ts         Lending market discovery
    │   ├── liquidator.ts      Vault-routed liquidation
    │   ├── risk-scorer.ts     Four-factor risk scoring
    │   ├── wallet-profiler.ts SAID + trade history analysis
    │   ├── launcher.ts        Domain token creation
    │   ├── domain-manager.ts  Lease tracking + rotation
    │   ├── ticker.ts          Symbol generation
    │   ├── logger.ts          Structured logging (shared across all modules)
    │   ├── types.ts           All type definitions
    │   ├── utils.ts           Helpers + base58 decoder
    │   └── scraper/           Domain discovery pipeline
    │       ├── index.ts         CLI entry, pipeline orchestration
    │       ├── scanner.ts       Domain scanning orchestrator
    │       ├── evaluator.ts     Scores domain quality
    │       ├── ticker.ts        Generates token symbols
    │       ├── config.ts        Scraper config
    │       ├── types.ts         Scraper types (re-exports LogLevel from parent)
    │       └── providers/       Data sources (expiring domains, availability)
    └── tests/
        ├── setup.ts           Shared test helpers (Surfpool)
        ├── test_bot.ts        Bot E2E tests
        └── test_scraper.ts    Scraper unit tests

clawhub/
├── agent.json               Manifest
├── SKILL.md                 This file
├── design.md                Architecture and design
├── audit.md                 Security audit
└── lib/
    ├── kit/                 Compiled kit output (tsconfig outDir)
    └── torchsdk/            Bundled SDK source
```

---

## The Domain Lending Primitive

This kit demonstrates a composable pattern using Torch Market:

```
             ┌──────────────┐
             │   DOMAIN     │
             │  (pixel.art) │
             └──────┬───────┘
                    │ launch
                    ▼
             ┌──────────────┐
             │  TOKEN       │
             │  (PIXEL)     │    ← bonding curve → migration → permanent
             └──────┬───────┘
                    │ hold
                    ▼
             ┌──────────────┐
             │  COLLATERAL  │
             │  (lock tokens)│   ← borrow SOL against domain position
             └──────┬───────┘
                    │ borrow
                    ▼
             ┌──────────────┐
             │  LOAN        │
             │  (SOL debt)  │    ← 2% weekly interest, 65% liquidation threshold
             └──────┬───────┘
                    │ if underwater
                    ▼
             ┌──────────────┐
             │  LIQUIDATION │
             │  (keeper bot)│    ← vault pays debt, receives collateral at 10% bonus
             └──────┬───────┘
                    │ collateral moves
                    ▼
             ┌──────────────┐
             │  ROTATION    │
             │  (new holder)│    ← top holder changes → domain lease updates
             └──────────────┘
```

Each step uses a different piece of Torch's infrastructure:
- **Bonding curves** for price discovery
- **Raydium migration** for permanent liquidity
- **Community treasury** for lending capital
- **Lending markets** for collateral-based borrowing
- **Vaults** for safe autonomous operation
- **Liquidation** for market health + domain rotation

Other builders can use this pattern for any asset class — not just domains. NFTs, real-world assets, prediction markets, governance tokens. The pattern is: **tokenize → lend → liquidate → rotate control**.

---

## Vault Safety

| Property | Guarantee |
|----------|-----------|
| **Full custody** | Vault holds all SOL and collateral. Agent holds nothing. |
| **Closed loop** | Liquidation SOL from vault, collateral tokens to vault. No leakage. |
| **Authority separation** | Creator (PDA seed) vs Authority (admin) vs Controller (disposable signer). |
| **Instant revocation** | Authority unlinks agent in one transaction. |
| **Authority-only withdrawals** | Agent cannot extract value from the vault. |

---

## Lending Parameters

| Parameter | Value |
|-----------|-------|
| Max LTV | 50% |
| Liquidation Threshold | 65% |
| Interest Rate | 2% per epoch (~weekly) |
| Liquidation Bonus | 10% |
| Utilization Cap | 50% of treasury |
| Min Borrow | 0.1 SOL |

---

## SDK Functions Used

| Function | Purpose |
|----------|---------|
| `getTokens({ status: 'migrated' })` | Discover domain tokens |
| `getToken(mint)` | Token detail (price, metadata) |
| `getLendingInfo(mint)` | Lending market state |
| `getHolders(mint)` | Token holders (potential borrowers) |
| `getLoanPosition(mint, wallet)` | Loan health check |
| `getVault(creator)` | Verify vault exists |
| `getVaultForWallet(wallet)` | Verify agent linked |
| `buildLiquidateTransaction(params)` | Vault-routed liquidation |
| `buildCreateTokenTransaction(params)` | Launch domain token |
| `verifySaid(wallet)` | Borrower reputation check |

---

## External API Calls

The kit makes outbound HTTPS requests to the following services. The bot's runtime path contacts **five** of them. No credentials are sent to any external service. All requests are read-only GETs/HEADs. No private key material is ever transmitted to any external endpoint. If any service is unreachable, the bot degrades gracefully (catches errors, continues to next token or cycle).

### Scraper (direct)

| Service | URL | Purpose | Data Sent |
|---------|-----|---------|-----------|
| **ExpiredDomains.net** | `https://www.expireddomains.net/domain-name-search/` | Scrape expiring domain listings | None (GET, User-Agent header only) |
| **RDAP** | `https://rdap.org/domain/{name}.{tld}` | Check domain availability (404 = available) | Domain name in URL (public) |

### Via torchsdk (transitive)

| Service | URL | Purpose | Data Sent |
|---------|-----|---------|-----------|
| **Solana RPC** | User-provided `SOLANA_RPC_URL` | All on-chain reads and transaction submission | Public keys, signed transactions |
| **CoinGecko** | `https://api.coingecko.com/api/v3/simple/price` | SOL/USD price for token valuations | None (GET only) |
| **SAID Protocol** | `https://api.saidprotocol.com/api/verify/{wallet}` | Wallet reputation / trust verification | Wallet address (public key, not sensitive) |
| **Irys Gateway** | `https://gateway.irys.xyz/...` | Token metadata retrieval (fallback) | None (GET only) |

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

---

## Testing

Requires [Surfpool](https://github.com/nicholasgasior/surfpool) mainnet fork:

```bash
surfpool start --network mainnet --no-tui
cd packages/kit && pnpm test:bot
cd packages/kit && pnpm test:scraper
```

Bot tests (10 passing): borrower creation, scanner, wallet profiler, risk scorer, liquidator (skip healthy), price history, lending info, cleanup. Scraper tests: ticker generation, domain evaluation, scanner integration with mock providers.

---

## Why This Matters

Traditional domain markets are opaque. Prices are set by registrars or private negotiation. There's no liquidity — you buy a domain and it sits in your account until you sell it.

This kit turns domains into liquid, borrowable, continuously-priced assets. The market sets the price. Anyone can buy in. Holders can extract liquidity without selling. And if they overleverage, the domain rotates to someone who values it more.

That's the power of composing Torch's primitives: bonding curves, lending markets, vaults, and liquidation keepers — working together as a single coherent system.

---

## Links

- Kit source: [github.com/mrsirg97-rgb/torch-domain-auction-bot](https://github.com/mrsirg97-rgb/torch-domain-auction-bot)
- Torch SDK (bundled): `lib/torchsdk/`
- Torch SDK (npm): [npmjs.com/package/torchsdk](https://www.npmjs.com/package/torchsdk)
- Torch Market: [torch.market](https://torch.market)
- Program ID: `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`

---

## Changelog

### v2.0.1

- **Upgraded torchsdk from 3.2.3 to 3.7.23.** Major SDK update adds treasury lock PDAs (V27), dynamic Raydium network detection, auto-migration bundling on bonding curve completion (`buildBuyTransaction` now returns optional `migrationTransaction`), vault-routed Raydium CPMM swaps (`buildVaultSwapTransaction`), Token-2022 fee harvesting (`buildHarvestFeesTransaction`, `buildSwapFeesToSolTransaction`), bulk loan scanning (`getAllLoanPositions`), on-chain token metadata queries (`getTokenMetadata`), and ephemeral agent keypair factory (`createEphemeralAgent`).
- **Updated env format in skill frontmatter.** Environment variable declarations now use structured `name`/`required` format for compatibility with ClawHub and OpenClaw agent runners.
- **Added clawdbot metadata section.** ClawBot runner now has explicit env requirements alongside OpenClaw.
