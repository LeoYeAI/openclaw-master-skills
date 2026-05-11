---
name: torch-prediction-market-bot
version: "2.0.3"
description: Autonomous vault-based prediction market bot for Torch Market on Solana. Creates binary prediction markets as Torch tokens — the bonding curve provides price discovery, the treasury accumulates value from trading fees, and the vault manages positions. Each market has an oracle (price feed or manual) and resolves at a deadline. The agent keypair is generated in-process -- disposable, holds nothing of value. All SOL routes through the vault. The human principal creates the vault, funds it, links the agent, and retains full control. Built on torchsdk v3.7.23 and the Torch Market protocol.
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
      - id: torch-prediction-market-kit
        kind: npm
        package: torch-prediction-market-kit@^2.0.2
        flags: []
        label: "Install Torch Prediction Market Kit (npm, optional -- SDK is bundled in lib/torchsdk/ and bot source is bundled under lib/kit on clawhub)"
  author: torch-market
  version: "2.0.3"
  clawhub: https://clawhub.ai/mrsirg97-rgb/torch-prediction-market-kit
  kit-source: https://github.com/mrsirg97-rgb/torch-prediction-market-kit
  website: https://torch.market
  program-id: 8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT
  keywords:
    - solana
    - defi
    - prediction-market
    - bonding-curve
    - vault-custody
    - ai-agents
    - agent-wallet
    - agent-safety
    - oracle
    - price-feed
    - token-2022
    - community-treasury
    - solana-agent-kit
    - escrow
    - anchor
    - pda
    - on-chain
    - autonomous-agent
    - torch-market
    - binary-market
    - market-resolution
  categories:
    - solana-protocols
    - defi-primitives
    - prediction-markets
    - agent-infrastructure
    - custody-solutions
compatibility: >-
  REQUIRED: SOLANA_RPC_URL (HTTPS Solana RPC endpoint)
  REQUIRED: VAULT_CREATOR (vault creator pubkey).
  OPTIONAL: SOLANA_PRIVATE_KEY -- the kit generates a fresh disposable keypair in-process if not provided. The agent wallet holds nothing of value (~0.01 SOL for gas). All token creation and seed liquidity SOL routes through the vault. The vault can be created and funded entirely by the human principal.
  This skill sets disable-model-invocation: true -- it must not be invoked autonomously without explicit user initiation.
  The Torch SDK is bundled in lib/torchsdk/ -- all source included for full auditability. No API server dependency.
  Oracle resolution uses CoinGecko public API (read-only, no key required). The vault can be created and funded entirely by the human principal -- the agent never needs access to funds.
---

# Torch Prediction Market Kit

You're here because you want to run prediction markets on Torch Market -- and you want to do it safely.

Every prediction market is a Torch token. The bonding curve is the AMM -- no LP setup, deterministic pricing, instant liquidity. The 10% treasury accumulates fees from every buy. Users buy the token to bet YES (price goes up), sell to bet NO (price goes down). At the deadline, the oracle checks the outcome and the bot records it.

**Settlement model: token-as-signal.** No payout mechanism. The token price IS the prediction. The bonding curve and treasury do the work.

That's where this bot comes in.

It reads your `markets.json` file, creates Torch tokens for pending markets, seeds them with initial liquidity from your vault, monitors price and volume, and resolves them at the deadline using an oracle (CoinGecko price feed or manual). All value routes through your vault. The agent wallet that signs transactions holds nothing.

**This is not a read-only scanner.** This is a fully operational market maker that generates its own keypair, verifies vault linkage, creates tokens, seeds liquidity, and resolves markets autonomously in a continuous loop.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                   MARKET CYCLE LOOP                       │
│                                                          │
│  1. Load market definitions from markets.json            │
│  2. For each pending market:                             │
│     → buildCreateTokenTransaction(name, symbol, uri)     │
│     → sign + submit + confirm                            │
│     → buildBuyTransaction(vault, mint, seed SOL)         │
│     → sign + submit + confirm                            │
│     → update status to 'active', save mint address       │
│  3. For each active market:                              │
│     → getToken(mint) — snapshot price, volume, holders   │
│     → if deadline passed:                                │
│        → checkOracle(oracle) — price feed or manual      │
│        → update status to 'resolved', record outcome     │
│  4. Save updated markets.json                            │
│  5. Sleep SCAN_INTERVAL_MS, repeat                       │
│                                                          │
│  All SOL comes from vault. Agent wallet holds nothing.   │
│  Vault is the boundary.                                  │
└─────────────────────────────────────────────────────────┘
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

When the bot creates and seeds a market:
- **Token creation** — agent signs as creator, no SOL cost beyond gas
- **Seed liquidity** — SOL comes from the vault via `buildBuyTransaction(vault=creator)`
- **Tokens purchased** — go to the vault's associated token account (ATA)

The human principal retains full control:
- `withdrawVault()` — pull SOL at any time
- `withdrawTokens(mint)` — pull market tokens at any time
- `unlinkWallet(agent)` — revoke agent access instantly

If the agent keypair is compromised, the attacker gets dust and vault access that you revoke in one transaction.

---

## Getting Started

### 1. Install

```bash
npm install torch-prediction-market-kit@2.0.2
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

// Fund vault with SOL for market creation + seed liquidity
const { transaction: depositTx } = await buildDepositVaultTransaction(connection, {
  depositor: authorityPubkey,
  vault_creator: authorityPubkey,
  amount_sol: 5_000_000_000, // 5 SOL
});
// sign and submit with authority wallet...
```

### 3. Define Markets

Create `markets.json`:

```json
[
  {
    "id": "sol-200-mar",
    "question": "Will SOL be above $200 by March 1, 2026?",
    "symbol": "SOL200M",
    "name": "SOL Above 200 March",
    "oracle": {
      "type": "price_feed",
      "asset": "solana",
      "condition": "above",
      "target": 200
    },
    "deadline": 1740787200,
    "initialLiquidityLamports": 100000000,
    "metadataUri": "https://arweave.net/placeholder"
  }
]
```

### 4. Run the Bot

```bash
VAULT_CREATOR=<your-vault-creator-pubkey> SOLANA_RPC_URL=<rpc-url> npx torch-prediction-market-bot
```

On first run, the bot prints the agent keypair and instructions to link it. Link it from your authority wallet, then restart.

### 5. Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SOLANA_RPC_URL` | **Yes** | -- | Solana RPC endpoint (HTTPS). Fallback: `RPC_URL` |
| `VAULT_CREATOR` | **Yes** | -- | Vault creator pubkey |
| `SOLANA_PRIVATE_KEY` | No | -- | Disposable controller keypair (base58 or JSON byte array). If omitted, generates fresh keypair on startup (recommended) |
| `SCAN_INTERVAL_MS` | No | `60000` | Milliseconds between market cycles (min 5000) |
| `LOG_LEVEL` | No | `info` | `debug`, `info`, `warn`, `error` |
| `MARKETS_PATH` | No | `./markets.json` | Path to market definitions file |

---

## Architecture

```
packages/kit/src/
├── index.ts      — entry point: keypair generation, vault verification, market cycle loop
├── config.ts     — loadConfig(): validates SOLANA_RPC_URL, VAULT_CREATOR, MARKETS_PATH, etc.
├── types.ts      — Market, Oracle, MarketSnapshot, BotConfig interfaces
├── markets.ts    — loadMarkets(), saveMarkets(), createMarket(), snapshotMarket(), resolveMarket()
├── oracle.ts     — checkPriceFeed(), checkOracle() — CoinGecko price resolution
└── utils.ts      — sol(), createLogger(), decodeBase58(), withTimeout()
```

The bot is ~280 lines of TypeScript across 6 modules. It does three things: create markets, monitor them, and resolve them through the vault.

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@solana/web3.js` | 1.98.4 | Solana RPC, keypair, transaction |
| `torchsdk` | 3.7.23 | Token queries, token creation, buy builder, vault queries |

Two runtime dependencies. Both pinned to exact versions. No `^` or `~` ranges.

---

## Market Lifecycle

```
pending ──→ active ──→ resolved
              │
              └──→ cancelled
```

| Status | Description |
|--------|-------------|
| **pending** | Market defined in `markets.json`, no token created yet |
| **active** | Torch token created on bonding curve, users can trade |
| **resolved** | Deadline passed, oracle checked, outcome recorded (yes/no) |
| **cancelled** | Market removed before resolution (manual edit) |

### Market Definition

```typescript
interface MarketDefinition {
  id: string                  // unique market identifier
  question: string            // human-readable question
  symbol: string              // token symbol (max 10 chars)
  name: string                // token name (max 32 chars)
  oracle: Oracle              // how the market resolves
  deadline: number            // unix timestamp (seconds)
  initialLiquidityLamports: number  // SOL to seed bonding curve (in lamports, max 10 SOL)
  metadataUri: string         // token metadata URI (allowlisted domains only)
}
```

### Input Validation

All pending markets are validated on load. Markets with invalid inputs are rejected before any on-chain action.

| Field | Constraint | Rejected Example |
|-------|-----------|-----------------|
| `id` | Must be unique across all markets | Duplicate `"sol-200-mar"` |
| `metadataUri` | Domain must be in allowlist: `arweave.net`, `gateway.irys.xyz`, `ipfs.io`, `cloudflare-ipfs.com`, `nftstorage.link`, `dweb.link` | `https://evil.com/payload.json` |
| `initialLiquidityLamports` | Max 10 SOL (10,000,000,000 lamports), non-negative | `50000000000` (50 SOL) |
| `oracle.asset` | Must be in allowlist of known CoinGecko IDs (solana, bitcoin, ethereum, etc.) | `"arbitrary-string"` |

These constraints ensure a compromised `markets.json` cannot trigger arbitrary URI fetches, drain the vault, or make unintended API calls.

---

## Oracle Resolution

### Price Feed Oracle (CoinGecko)

The primary oracle. Fetches the current price of an asset and compares it against a target.

```json
{
  "type": "price_feed",
  "asset": "solana",
  "condition": "above",
  "target": 200
}
```

- **`asset`** — CoinGecko asset ID (e.g. `"solana"`, `"bitcoin"`, `"ethereum"`)
- **`condition`** — `"above"` or `"below"`
- **`target`** — USD price threshold
- **Resolution:** if condition is `"above"`, outcome is `"yes"` when price > target, `"no"` otherwise

### Manual Oracle

Fallback for markets that can't be resolved by a price feed.

```json
{
  "type": "manual",
  "source": "Twitter announcement from @torch_market"
}
```

Resolution: edit `markets.json` directly — set `"status": "resolved"` and `"outcome": "yes"` or `"no"`.

---

## Vault Safety Model

The same seven guarantees from the Torch Market vault apply here:

| Property | Guarantee |
|----------|-----------|
| **Full custody** | Vault holds all SOL and all market tokens. Agent wallet holds nothing. |
| **Closed loop** | Seed liquidity SOL comes from vault, purchased tokens go to vault ATA. No leakage to agent. |
| **Authority separation** | Creator (immutable PDA seed) vs Authority (transferable admin) vs Controller (disposable signer). |
| **One link per wallet** | Agent can only belong to one vault. PDA uniqueness enforces this on-chain. |
| **Permissionless deposits** | Anyone can top up the vault. Hardware wallet deposits, agent creates markets. |
| **Instant revocation** | Authority can unlink the agent at any time. One transaction. |
| **Authority-only withdrawals** | Only the vault authority can withdraw SOL or tokens. The agent cannot extract value. |

### The Closed Economic Loop for Market Creation

| Direction | Flow |
|-----------|------|
| **SOL out** | Vault → Bonding curve (seed liquidity buy) |
| **Tokens in** | Bonding curve → Vault ATA (purchased tokens) |
| **Treasury** | 10% of each buy accumulates in token treasury |

The vault's seed tokens remain on the bonding curve. Users trade against the curve. Treasury grows from fees. The authority can withdraw vault tokens or SOL at any time.

---

## SDK Functions Used

The bot uses a focused subset of the Torch SDK:

| Function | Purpose |
|----------|---------|
| `getVault(connection, creator)` | Verify vault exists on startup |
| `getVaultForWallet(connection, wallet)` | Verify agent is linked to vault |
| `buildCreateTokenTransaction(connection, params)` | Build token creation transaction for new market |
| `buildBuyTransaction(connection, params)` | Build vault-routed buy to seed initial liquidity |
| `getToken(connection, mint)` | Get token price, volume, status for market snapshots |
| `getHolders(connection, mint)` | Get holder count for market snapshots |
| `confirmTransaction(connection, sig, wallet)` | Confirm transaction on-chain via RPC (verifies signer, checks Torch instructions) |

### buildCreateTokenTransaction Parameters

```typescript
const { transaction, mint, mintKeypair } = await buildCreateTokenTransaction(connection, {
  creator: agentPubkey,       // agent wallet (signer + fee payer)
  name: "SOL Above 200 March", // token name (max 32 chars)
  symbol: "SOL200M",           // token symbol (max 10 chars)
  metadata_uri: "https://arweave.net/...",  // token metadata URI
});
```

### buildBuyTransaction Parameters

```typescript
const { transaction, message } = await buildBuyTransaction(connection, {
  mint: mintAddress,            // token to buy
  buyer: agentPubkey,           // agent wallet (signer)
  amount_sol: 100000000,        // 0.1 SOL in lamports
  slippage_bps: 500,            // 5% slippage tolerance
  vault: vaultCreator,          // vault creator pubkey (SOL from vault, tokens to vault ATA)
});
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

All SDK calls are wrapped with a 30-second timeout (`withTimeout` in utils.ts). A hanging or unresponsive RPC endpoint cannot stall the bot indefinitely — the call rejects, the error is caught by the market cycle loop, and the bot continues to the next market or cycle.

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `SOLANA_RPC_URL` / `RPC_URL` | **Yes** | Solana RPC endpoint (HTTPS) |
| `VAULT_CREATOR` | **Yes** | Vault creator pubkey — identifies which vault the bot operates through |
| `SOLANA_PRIVATE_KEY` | No | Optional — if omitted, the bot generates a fresh keypair on startup (recommended) |

### External Runtime Dependencies

The SDK and bot make outbound HTTPS requests to external services. The bot's runtime path contacts **three** of them:

| Service | Purpose | When Called | Bot Uses? |
|---------|---------|------------|-----------|
| **CoinGecko** (`api.coingecko.com`) | Asset price for oracle resolution + SOL/USD display | `checkPriceFeed()` in oracle.ts, `getToken()` in SDK | **Yes** — oracle resolution AND token queries |
| **Irys Gateway** (`gateway.irys.xyz`) | Token metadata fallback (name, symbol, image) | `getToken()` when on-chain metadata URI points to Irys | Yes — via `getToken()` |
| **SAID Protocol** (`api.saidprotocol.com`) | Agent identity verification and trust tier lookup | `verifySaid()` only | **No** — the bot does not call `verifySaid()` |

#### CoinGecko API Details (Oracle)

The oracle module (`oracle.ts`) calls the CoinGecko public API directly:

```
GET https://api.coingecko.com/api/v3/simple/price?ids={asset}&vs_currencies=usd
```

- **No API key required** — uses the free public endpoint
- **Rate limit:** ~10-30 calls/minute on the free tier
- **Data sent:** asset ID only (e.g. `"solana"`) — no wallet, transaction, or agent data
- **Data received:** `{ "solana": { "usd": 87.76 } }`
- **Failure mode:** if CoinGecko is unreachable, `checkPriceFeed()` throws and the market stays unresolved until the next cycle
- **Called once per active market per cycle** that has passed its deadline

**`confirmTransaction()` does NOT contact SAID.** Despite living in the SDK's `said.js` module, it only calls `connection.getParsedTransaction()` (Solana RPC) to verify the transaction succeeded on-chain and determine the event type. No data is sent to any external service.

No credentials are sent to CoinGecko or Irys. All requests are read-only GET. If either service is unreachable, the bot degrades gracefully. No private key material is ever transmitted to any external endpoint.

---

## Log Output

```
=== torch prediction market bot ===
agent wallet: 7xK9...
vault creator: 4yN2...
markets file: ./markets.json
scan interval: 60000ms

[09:15:32] INFO  vault found — authority=8cpW...
[09:15:32] INFO  agent wallet linked to vault — starting market cycle
[09:15:32] INFO  treasury: 5.0000 SOL
[09:15:33] INFO  CREATING | sol-200-mar — "Will SOL be above $200 by March 1, 2026?"
[09:15:35] INFO  CREATED | sol-200-mar — mint=AqAgqKTypS... | seed=0.1000 SOL
[09:16:35] DEBUG SNAPSHOT | sol-200-mar — price=0.000012 SOL | mcap=0.0120 | holders=3
[09:17:35] INFO  RESOLVING | sol-200-mar — deadline reached
[09:17:36] INFO  RESOLVED | sol-200-mar — outcome=no
```

---

## Testing

Requires [Surfpool](https://github.com/txtx/surfpool) running a mainnet fork:

```bash
surfpool start --network mainnet --no-tui
pnpm test
```

**Test result:** 9 passed, 1 informational (Surfpool RPC limitation on `getTokenLargestAccounts` for Token-2022 — works on mainnet).

| Test | What It Validates |
|------|-------------------|
| Connection | RPC reachable |
| loadMarkets | Market file parsing and validation |
| checkPriceFeed | CoinGecko oracle returns valid price data |
| buildCreateTokenTransaction | Token creation transaction builds correctly |
| getTokens | Discovers bonding/migrated tokens |
| getToken | Token metadata, price, status |
| getHolders | Holder enumeration (skips on Surfpool limitation) |
| getVaultForWallet | Vault link returns null for unlinked wallet |
| In-process keypair | No external key required |

---

## Error Codes

- `VAULT_NOT_FOUND`: No vault exists for this creator
- `WALLET_NOT_LINKED`: Agent wallet is not linked to the vault
- `INVALID_MINT`: Token not found
- `BONDING_COMPLETE`: Token has graduated — trade on DEX instead
- `NAME_TOO_LONG`: Token name exceeds 32 characters
- `SYMBOL_TOO_LONG`: Token symbol exceeds 10 characters

---

## Links

- Prediction Market Kit (source): [github.com/mrsirg97-rgb/torch-prediction-market-kit](https://github.com/mrsirg97-rgb/torch-prediction-market-kit)
- Prediction Market Kit (npm): [npmjs.com/package/torch-prediction-market-kit](https://www.npmjs.com/package/torch-prediction-market-kit)
- Torch SDK (bundled): `lib/torchsdk/` -- included in this skill
- Torch SDK (source): [github.com/mrsirg97-rgb/torchsdk](https://github.com/mrsirg97-rgb/torchsdk)
- Torch SDK (npm): [npmjs.com/package/torchsdk](https://www.npmjs.com/package/torchsdk)
- Torch Market (protocol skill): [clawhub.ai/mrsirg97-rgb/torchmarket](https://clawhub.ai/mrsirg97-rgb/torchmarket)
- Whitepaper: [torch.market/whitepaper.md](https://torch.market/whitepaper.md)
- Security Audit: [torch.market/audit.md](https://torch.market/audit.md)
- Website: [torch.market](https://torch.market)
- Program ID: `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`

---

## Changelog

### v2.0.0

- **Upgraded torchsdk from 3.2.3 to 3.7.23.** Major SDK update adds treasury lock PDAs (V27), dynamic Raydium network detection, auto-migration bundling on bonding curve completion (`buildBuyTransaction` now returns optional `migrationTransaction`), vault-routed Raydium CPMM swaps (`buildVaultSwapTransaction`), Token-2022 fee harvesting (`buildHarvestFeesTransaction`, `buildSwapFeesToSolTransaction`), bulk loan scanning (`getAllLoanPositions`), on-chain token metadata queries (`getTokenMetadata`), and ephemeral agent keypair factory (`createEphemeralAgent`).
- **Exported `withTimeout` utility.** The timeout helper used internally by the bot is now a public export of the kit package, available to downstream consumers.
- **Updated env format in skill frontmatter.** Environment variable declarations now use structured `name`/`required` format for compatibility with ClawHub and OpenClaw agent runners.

### v1.0.2

- **Updated kit to point to correct bundled sdk.** The `index.js` file now imports the SDK from the local `lib/torchsdk/` directory instead of the npm package. This ensures that the bot uses the exact bundled SDK version (3.2.3) included in the kit, rather than any potentially different version installed from npm. Addresses audit finding L-3. 

### v1.0.1

- **Timeout on all external calls.** Every SDK, RPC, and API call is now wrapped with a 30-second timeout (10 seconds for CoinGecko). If an RPC endpoint or CoinGecko becomes unresponsive, the call fails fast with a descriptive error instead of stalling the bot indefinitely. Addresses audit finding L-1.
- **Market ID uniqueness validation.** `loadMarkets()` now rejects `markets.json` files containing duplicate market IDs on load, preventing unintended duplicate market creation and wasted vault SOL. Addresses audit finding L-2.

---

This bot exists because prediction markets need infrastructure. Torch bonding curves provide instant liquidity and deterministic pricing without LP setup. The vault makes it safe — all value stays in the escrow, all risk is bounded, and the human principal keeps the keys. The token price IS the prediction.
