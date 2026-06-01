---
name: onchain-audit
description: |
  On-chain data and contract security analysis.
  Includes Binance API and Bitget API for audit, token info, wallet,
  and contract analysis. CLAWBOT decides which to use based on context.
metadata:
  author: NotevenDe
  version: 1.3.0
---

# On-chain Audit — Contract & On-chain Analysis

Two data sources; CLAWBOT chooses based on context.
Binance and Bitget data can be cross-verified.

---

## 1. Binance API (onchain)

`POST https://crab-skill.opsat.io/api/onchain/*` (requires Crab signature)

Fields: `address` + `chainName` (uppercase: `BSC`/`ETHEREUM`/`BASE`/`SOLANA`)

| Endpoint | Description |
|----------|-------------|
| `/api/onchain/audit` | Contract security audit (Binance + Bitget dual-source) |
| `/api/onchain/token-info` | Token metadata and market dynamics |
| `/api/onchain/wallet` | Wallet positions (BSC/BASE/SOLANA only) |
| `/api/onchain/token-search` | Token search (requires `keyword` instead of `address`) |

---

## 2. Bitget API (onchain-2)

`POST https://crab-skill.opsat.io/api/onchain-2/*` (requires Crab signature)

Fields: `chain` + `contract` (lowercase: `bnb`/`eth`/`base`/`sol`)

> Note: field names and chain format differ from Binance endpoints.

| Endpoint | Description |
|----------|-------------|
| `/api/onchain-2/token-info` | Token details (symbol, name, market cap, etc.) |
| `/api/onchain-2/token-price` | Token price summary |
| `/api/onchain-2/tx-info` | Token transaction statistics |
| `/api/onchain-2/liquidity` | Liquidity pool info |
| `/api/onchain-2/security-audit` | Security audit (risk/warn/low checks) |

---

---

## 3. Onchain Explorer API (explorer)

`POST https://crab-skill.opsat.io/api/explorer/*` (requires Crab signature)

See `API_EXPLORER.md` for full parameter and response details.

### 3a. Contract ABI / Source Code

**Endpoint**: `/api/explorer/contract`

Fields: `chain` (`ETH` or `BSC`) + `address`

| Key field | Description |
|-----------|-------------|
| `verified` | Contract is open-source and verified on Etherscan |
| `contractName` | Contract name |
| `compilerVersion` | Solidity compiler version |
| `optimizationUsed` | Whether optimization was enabled |
| `abi` | Contract ABI array |
| `sourceCode` | Source code (string, or object for multi-file) |
| `licenseType` | License type |
| `proxy` | Is this a proxy contract |
| `implementation` | Implementation address (proxy only) |

Returns `{ verified: false }` for unverified contracts.

### 3b. Token Transfer History

**Endpoint**: `/api/explorer/token-history`

Fields: `chain` (`ETH` / `BSC` / `SOL`) + `address` + optional pagination/filter

- **ETH/BSC**: pagination via `outPageKey` / `inPageKey`; each record has `hash`, `from`, `to`, `value`, `asset`, `category`, `blockNum`, `blockTimestamp`
- **SOL**: filter by `type` (SWAP/TRANSFER/BURN/...) and `source` (JUPITER/RAYDIUM/...); paginate via `before`; each record has `signature`, `timestamp`, `type`, `source`, `fee`, `nativeTransfers`, `tokenTransfers`, `events`

### 3c. SOL Address Overview

**Endpoint**: `/api/explorer/sol-address`

Fields: `address` + optional `txLimit` (default 10)

Returns: native SOL balance (lamports + USD), SPL token list, recent transfer records.

---

## Fallback Behavior

| Scenario                        | Behavior                                    |
|---------------------------------|---------------------------------------------|
| Unknown contract chain          | Skip audit                                  |
| No token search results         | Skip token search                           |
| Wallet chain not supported      | Skip wallet query                           |
| Contract not verified (explorer)| Note as unverified, skip ABI/source display |
| Explorer upstream unavailable   | Skip, continue with other sources           |
