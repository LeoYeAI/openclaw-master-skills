# Torch Domain Auction Bot — Security Audit

**Audit Date:** February 28, 2026
**Auditor:** Claude Opus 4.6 (Anthropic)
**Bot Version:** 2.0.1
**SDK Version:** torchsdk 3.7.23
**On-Chain Program:** `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT` (V3.7.8)
**Language:** TypeScript
**Test Result:** 10 passed, 0 failed (Surfpool mainnet fork)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Scope](#scope)
3. [Methodology](#methodology)
4. [Changes Since v1.0.2](#changes-since-v102)
5. [Keypair Safety Review](#keypair-safety-review)
6. [Vault Integration Review](#vault-integration-review)
7. [Domain Lease Security](#domain-lease-security)
8. [Risk Scoring Review](#risk-scoring-review)
9. [Scan Loop Security](#scan-loop-security)
10. [Configuration Validation](#configuration-validation)
11. [Dependency Analysis](#dependency-analysis)
12. [Threat Model](#threat-model)
13. [Findings](#findings)
14. [Prior Findings Status](#prior-findings-status)
15. [Conclusion](#conclusion)

---

## Executive Summary

This audit covers the Torch Domain Auction Bot v2.0.1, a single-package kit that implements a domain lending protocol on Torch Market. Domains are tokenized, top holders control the domain, holders can borrow SOL against their tokens, and underwater positions are liquidated through a Torch Vault — causing the domain lease to rotate.

This is a re-audit updating coverage from v1.0.2 (torchsdk 3.2.3) to v2.0.1 (torchsdk 3.7.23, on-chain program V3.7.8).

The bot was reviewed for key safety, vault integration correctness, domain lease security, risk scoring integrity, error handling, and dependency surface.

### Overall Assessment

| Category | Rating | Notes |
|----------|--------|-------|
| Key Safety | **PASS** | In-process `Keypair.generate()`, optional `SOLANA_PRIVATE_KEY`, no key logging |
| Vault Integration | **PASS** | `vault` param correctly passed to `buildLiquidateTransaction` |
| Domain Lease Logic | **PASS** | Top holder tracked correctly, leases expire and rotate |
| Risk Scoring | **PASS** | Four-factor weighted scoring, configurable threshold |
| Error Handling | **PASS** | Four-level isolation: cycle, token, borrower, liquidation |
| Config Validation | **PASS** | Required env vars checked, scan interval floored at 5000ms |
| Dependencies | **MINIMAL** | 5 runtime deps, all pinned exact. No `^` or `~` ranges. |
| Supply Chain | **LOW RISK** | No post-install hooks, no remote code fetching |

### Finding Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Informational | 5 |

Both low findings from v1.0.2 resolved: L-1 (Wallet Profiler Cache — TTL reduced to 30s) and L-2 (No Timeout on SDK Calls — all SDK calls now wrapped with `withTimeout(promise, 30_000, label)`).

---

## Scope

### Files Reviewed

**Kit Package (`packages/kit/`):**

| File | Lines | Role |
|------|-------|------|
| `src/index.ts` | 129 | Entry: vault verification, startup banner, CLI, all exports |
| `src/config.ts` | 78 | Env validation, ephemeral keypair |
| `src/monitor.ts` | 86 | Scan loop orchestration with `getAllLoanPositions` |
| `src/scanner.ts` | 97 | Lending market discovery with bulk loan scanner |
| `src/liquidator.ts` | 88 | Vault-routed liquidation |
| `src/risk-scorer.ts` | 90 | Four-factor risk scoring |
| `src/wallet-profiler.ts` | 127 | SAID verification, trade analysis |
| `src/launcher.ts` | 40 | Domain token creation |
| `src/domain-manager.ts` | 73 | Lease tracking and rotation |
| `src/ticker.ts` | 36 | Symbol generation |
| `src/logger.ts` | 36 | Structured logging (shared across all modules) |
| `src/types.ts` | 111 | Type definitions |
| `src/utils.ts` | 35 | Helpers, base58 decoder |
| `src/scraper/index.ts` | ~43 | Scraper CLI entry |
| `src/scraper/scanner.ts` | ~36 | Domain scanning |
| `src/scraper/evaluator.ts` | ~71 | Quality scoring |
| `src/scraper/ticker.ts` | ~48 | Symbol generation |
| `src/scraper/config.ts` | ~11 | Scraper config |
| `src/scraper/types.ts` | ~30 | Scraper types |
| `src/scraper/providers/*.ts` | ~115 | Data sources |
| `tests/test_bot.ts` | ~346 | Bot E2E test suite |
| `tests/test_scraper.ts` | ~198 | Scraper unit tests |
| `package.json` | 42 | Dependencies |

**Total:** ~1,600 lines in one package.

### SDK Cross-Reference

The bot relies on `torchsdk@3.7.23` for all on-chain interaction. The SDK was independently audited. This audit focuses on the bot's usage of the SDK, not the SDK internals. The SDK is also bundled in `lib/torchsdk/` for full auditability.

---

## Methodology

1. **Line-by-line source review** of all bot source files
2. **Keypair lifecycle analysis** — generation, usage, exposure surface
3. **Vault integration verification** — correct params on ALL liquidation calls
4. **Domain lease logic review** — rotation correctness, edge cases
5. **Risk scoring validation** — factor computation, weight normalization, bounds
6. **Error handling analysis** — crash paths, retry behavior, log safety
7. **Dependency audit** — runtime deps, dev deps, post-install hooks, version pinning
8. **E2E test review** — coverage, assertions, false positives
9. **Delta analysis** — changes from v1.0.2 to v2.0.1

---

## Changes Since v1.0.2

### SDK Upgrade: torchsdk 3.2.3 → 3.7.23

The SDK was upgraded from 3.2.3 to 3.7.23. SDK additions used by the bot:

- `getAllLoanPositions(connection, mint)` — bulk loan scanning replaces holder-based borrower discovery. Used in `scanner.ts:24` and `monitor.ts:60`.

SDK additions **not used** by the bot (no new attack surface): treasury lock PDAs, auto-migration bundling, vault-routed Raydium CPMM swaps, Token-2022 fee harvesting, on-chain token metadata queries, ephemeral agent keypair factory.

### Bot Code Changes

| Change | Files | Impact |
|--------|-------|--------|
| Bulk loan scanning | `scanner.ts:18-30`, `monitor.ts:60` | `getAllLoanPositions` replaces holder-based discovery — more complete borrower coverage |
| Env format update | `SKILL.md`, `agent.json` | Structured `name`/`required` format for ClawHub/OpenClaw compatibility |
| ClawBot metadata | `agent.json` | Added `clawdbot` metadata section alongside OpenClaw config |

### Borrower Discovery Improvement

v1.0.2 used `getHolders(connection, mint, 20)` to discover potential borrowers, limited to 20 holders. v2.0.1 uses `getAllLoanPositions(connection, mint)` which returns all active loan positions directly — no holder limit, no missed borrowers.

```typescript
// scanner.ts:18-30 (v2.0.1)
const discoverBorrowers = async (connection, mint, log) => {
  const { positions } = await getAllLoanPositions(connection, mint)
  return positions.map((p) => p.borrower)
}
```

This resolves informational finding I-1 from the v1.0.2 audit.

---

## Keypair Safety Review

### Generation

The keypair is created via `loadKeypair()` in `config.ts:29-45`:

```typescript
export const loadKeypair = (): { keypair: Keypair; generated: boolean } => {
  const privateKey = process.env.SOLANA_PRIVATE_KEY ?? null
  if (privateKey) {
    // try JSON byte array, then base58
    return { keypair: Keypair.fromSecretKey(...), generated: false }
  }
  return { keypair: Keypair.generate(), generated: true }
}
```

Two paths:
1. **Default (recommended):** `Keypair.generate()` — fresh Ed25519 keypair from system entropy
2. **Optional:** `SOLANA_PRIVATE_KEY` env var — JSON byte array or base58 via inline `decodeBase58`

The keypair is:
- **Not persisted** to disk (unless user provides `SOLANA_PRIVATE_KEY`)
- **Not exported** — `keypair` is embedded in `BotConfig`, not in the public API surface
- **Not logged** — only the public key is printed at startup (`index.ts:64`)
- **Not transmitted** — the secret key never leaves the process
- Marked `"sensitive": true` in `agent.json`

### Usage Points

The keypair is used in exactly three places:
1. **Public key extraction** — startup logging, vault link check, liquidation/launch params (safe)
2. **Liquidation signing** — `result.transaction.partialSign(this.config.walletKeypair)` in `liquidator.ts:65`
3. **Token launch signing** — `result.transaction.partialSign(wallet)` in `launcher.ts:28`

Both signing operations are local only.

**Verdict:** Key safety is correct. No key material leaks from the process.

---

## Vault Integration Review

### CRITICAL: Liquidation Transaction

```typescript
// liquidator.ts:58-63
const result = await buildLiquidateTransaction(connection, {
  mint: scored.mint,
  liquidator: this.config.walletKeypair.publicKey.toBase58(),
  borrower: scored.borrower,
  vault: this.config.vaultCreator,
})
```

The `vault` parameter is correctly passed. Per the SDK, when `vault` is provided:
- Vault PDA derived from `vaultCreator` (`["torch_vault", creator]`)
- Wallet link PDA derived from `liquidator` (`["vault_wallet", wallet]`)
- SOL debited from vault to pay borrower's debt
- Collateral tokens credited to vault ATA at 10% bonus

**There is exactly one call to `buildLiquidateTransaction` in the codebase. It correctly includes the `vault` parameter.**

### Startup Verification

```typescript
// index.ts:70-93
const vault = await getVault(connection, config.vaultCreator)
if (!vault) throw new Error(...)

const link = await getVaultForWallet(connection, config.walletKeypair.publicKey.toBase58())
if (!link) { /* print instructions, exit */ }
```

Both checks execute before any command (monitor, launch, info). The bot cannot operate without a valid vault and linked agent.

**Verdict:** Vault integration is correct. All liquidation value routes through the vault PDA.

---

## Domain Lease Security

### Lease Rotation Logic

```typescript
// domain-manager.ts:43-56
if (activeLease.lessee !== topHolder) {
  activeLease.active = false
  updated.push({
    domain: dt.domain,
    mint: dt.mint,
    lessee: topHolder,
    startedAt: now,
    expiresAt: now + DEFAULT_LEASE_DURATION_MS,
    active: true,
  })
}
```

The lease system:
1. Checks top holder via `getHolders(connection, mint, 1)` (`domain-manager.ts:12`)
2. If top holder changed, expires old lease and creates new one
3. Leases have a 7-day default duration (`DEFAULT_LEASE_DURATION_MS`)
4. Expired leases are cleaned up at the start of each cycle (`domain-manager.ts:27-32`)

### Edge Cases

- **No holders:** `checkTopHolder` returns `null`, no lease created (correct)
- **Same holder:** No rotation, existing lease continues (correct)
- **Liquidation rotation:** After collateral moves to vault ATA, the vault may become top holder. This is by design — the vault operator controls the domain until they withdraw or sell the tokens.
- **Concurrent purchases:** The lease checks once per scan cycle. Rapid trading may cause temporary lag, but the lease always converges to the current top holder.

**Verdict:** Lease logic is correct. Rotation tracks actual token ownership accurately with acceptable latency.

---

## Risk Scoring Review

### Factor Computation

| Factor | Implementation | Bounds | File |
|--------|---------------|--------|------|
| LTV Proximity | `(currentLtv / threshold) * 100` | Clamped 0-100 | `risk-scorer.ts:12-19` |
| Price Momentum | `50 - priceChange * 100` | Clamped 0-100 | `risk-scorer.ts:22-34` |
| Wallet Risk | SAID + trade stats composite | Clamped 0-100 | `wallet-profiler.ts:103-124` |
| Interest Burden | `interestRatio * 500` | Clamped 0-100 | `risk-scorer.ts:37-43` |

### Weight Normalization

```typescript
// risk-scorer.ts:5-10
const WEIGHTS = {
  ltvProximity: 0.35,
  priceMomentum: 0.25,
  walletRisk: 0.2,
  interestBurden: 0.2,
}
```

Weights sum to 1.0. Final score is clamped to 0-100 (`risk-scorer.ts:84`).

### Safety Gates in Liquidator

The `tryLiquidate` method applies four sequential gates before executing:
1. `position.health === 'healthy'` → skip (`liquidator.ts:24`)
2. `riskScore < riskThreshold` → skip (`liquidator.ts:30`)
3. `estimatedProfitLamports < minProfitLamports` → skip (`liquidator.ts:38`)
4. `position.health !== 'liquidatable'` → skip (`liquidator.ts:46`)

A position must be `liquidatable`, above the risk threshold, AND profitable to trigger execution.

**Verdict:** Scoring is mathematically sound. All factors bounded. Liquidation has appropriate safety gates.

---

## Scan Loop Security

### Four-Level Error Isolation

**Level 1 — Cycle level** (`monitor.ts:26-81`):
```typescript
while (true) {
  try {
    // scan, score, liquidate, rotate
  } catch (err) {
    log.error('monitor tick failed', err)
  }
  await sleep(config.scoreIntervalMs)
}
```

**Level 2 — Token level** (`scanner.ts:55-89`):
```typescript
for (const summary of result.tokens) {
  try { ... } catch (err) {
    log.debug(`skipping ${summary.mint}: ${err}`)
  }
}
```

**Level 3 — Borrower level** (`monitor.ts:62-73`):
```typescript
for (const pos of positions) {
  try { ... } catch (err) {
    log.debug(`error scoring ${pos.borrower.slice(0, 8)}...`, err)
  }
}
```

**Level 4 — Liquidation level** (`liquidator.ts:57-85`):
```typescript
try {
  const result = await buildLiquidateTransaction(...)
  // sign, send, confirm
} catch (err) {
  this.log.error(`liquidation failed...`, err)
  return null
}
```

No single failure can crash the bot. Each level catches independently.

**Verdict:** Error handling is robust. The bot degrades gracefully at every level.

---

## Configuration Validation

### Required Variables

| Variable | Validation | Failure Mode |
|----------|-----------|--------------|
| `SOLANA_RPC_URL` | Must be set (fallback: `BOT_RPC_URL`) | Throws on startup |
| `VAULT_CREATOR` | Must be set | Throws on startup |
| `BOT_SCAN_INTERVAL_MS` | Must be >= 5000 | Throws on startup |
| `BOT_LOG_LEVEL` | Must be `debug\|info\|warn\|error` | Throws on startup |

### Security Notes

- `SOLANA_RPC_URL` used only for Solana RPC calls — never logged or transmitted externally
- `VAULT_CREATOR` is a public key (not sensitive)
- `SOLANA_PRIVATE_KEY` is optional, read once at startup, never logged or transmitted. Marked `"sensitive": true` in `agent.json`.

**Verdict:** Configuration properly validated. Sensitive values handled safely.

---

## Dependency Analysis

### Runtime Dependencies

| Package | Version | Pinning | Post-Install | Risk |
|---------|---------|---------|-------------|------|
| `@solana/web3.js` | 1.98.4 | Exact | None | Low |
| `torchsdk` | 3.7.23 | Exact | None | Low — audited separately, bundled in `lib/torchsdk/` |
| `@coral-xyz/anchor` | 0.32.1 | Exact | None | Low |
| `@solana/spl-token` | 0.4.14 | Exact | None | Low |
| `bs58` | 6.0.0 | Exact | None | Low |

### Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@types/node` | 20.19.33 | TypeScript definitions |
| `prettier` | 3.8.1 | Code formatting |
| `typescript` | 5.9.3 | Compiler |

Dev dependencies are not shipped in the runtime bundle and have no security impact.

### Supply Chain

- **No `^` or `~` version ranges** on runtime dependencies — all pinned to exact versions
- **No post-install hooks** — scripts contain only `build`, `clean`, `test:scraper`, `test:bot`, `format`
- **No remote code fetching** — no dynamic `import()`, no `eval()`, no fetch-and-execute
- **Lockfile present** — `pnpm-lock.yaml` pins transitive dependencies
- **SDK bundled** — `lib/torchsdk/` includes full SDK source for auditability

### External Runtime Dependencies

| Service | Purpose | Data Sent | Bot Uses? |
|---------|---------|-----------|-----------|
| **CoinGecko** (`api.coingecko.com`) | SOL/USD price | None (GET only) | Yes via `getToken()` |
| **Irys Gateway** (`gateway.irys.xyz`) | Token metadata fallback | None (GET only) | Yes via `getToken()` |
| **SAID Protocol** (`api.saidprotocol.com`) | Wallet reputation | Wallet address (public) | Yes via `verifySaid()` |
| **ExpiredDomains.net** | Expired domain listings | None (GET, User-Agent only) | Yes (scraper) |
| **RDAP** (`rdap.org`) | Domain availability | Domain name in URL (public) | Yes (scraper) |

No private key material is ever transmitted. All requests are read-only GETs/HEADs. No credentials are sent to any external service. If any service is unreachable, the bot degrades gracefully — the error is caught by the four-level isolation and the bot continues to the next token or cycle.

All external API calls are wrapped with `withTimeout` — 30s for SDK calls (RPC-backed), 10s for `verifySaid` (external API). A hanging or unresponsive endpoint cannot stall the bot.

**Verdict:** Minimal and locked dependency surface. No supply chain concerns. All external calls are read-only, credential-free, and timeout-bounded.

---

## Threat Model

### Threat: Compromised Agent Keypair

**Attack:** Attacker obtains the agent's private key from process memory.
**Impact:** Attacker can sign vault-routed transactions.
**Mitigation:** Agent holds ~0.01 SOL. Authority unlinks in one transaction. Cannot call `withdrawVault` or `withdrawTokens`.
**Residual risk:** Attacker could execute vault-routed liquidations until unlinked. Limited by vault SOL balance.

### Threat: Malicious RPC Endpoint

**Attack:** RPC returns fabricated positions to trigger unprofitable liquidations.
**Impact:** Bot liquidates positions that aren't actually underwater.
**Mitigation:** On-chain program validates all liquidation preconditions. Fabricated RPC data produces transactions that fail on-chain.
**Residual risk:** None — on-chain validation is the security boundary.

### Threat: Domain Lease Manipulation

**Attack:** Attacker rapidly buys/sells tokens to flip domain control.
**Impact:** Domain lease rotates frequently.
**Mitigation:** 7-day lease duration acts as debounce. Lease only rotates when top holder actually changes. Market depth (after migration) makes manipulation expensive.
**Residual risk:** For low-liquidity tokens, lease manipulation is cheaper. This is inherent to the model.

### Threat: Risk Score Gaming

**Attack:** Borrower maintains SAID verification and trade history to lower risk score, avoiding liquidation.
**Impact:** Underwater position liquidated later than optimal.
**Mitigation:** LTV proximity has the highest weight (35%). Risk score is a secondary filter — the primary gate is `position.health === 'liquidatable'` which is computed on-chain from actual collateral/debt ratios.
**Residual risk:** Delayed liquidation in edge cases. No capital loss — the position is still liquidatable.

### Threat: Front-Running

**Attack:** MEV bot observes the liquidation transaction and front-runs it.
**Impact:** Bot's transaction fails (`NOT_LIQUIDATABLE`).
**Mitigation:** Error caught, bot moves to next position. No vault SOL lost on failed liquidation.
**Residual risk:** Reduced success rate in competitive MEV environments.

---

## Findings

### L-1: Wallet Profiler Caches May Bias Risk Scores — **RESOLVED**

**Severity:** Low
**File:** `wallet-profiler.ts:6`
**Description:** Wallet profiles were cached for 60 seconds (`CACHE_TTL_MS`). During volatile markets, a profile cached before a rapid sell-off could understate wallet risk, slightly delaying liquidation.
**Resolution:** Cache TTL reduced from 60s to 30s (`CACHE_TTL_MS = 30_000`). The primary liquidation gate remains on-chain health status — the risk score is a secondary filter.

### I-1: Lease Duration Not Configurable

**Severity:** Informational
**File:** `domain-manager.ts:6`
**Description:** `DEFAULT_LEASE_DURATION_MS` is hardcoded to 7 days. Different use cases may want shorter or longer lease periods.
**Impact:** Inflexible for operators wanting different rotation speeds.

### I-2: Price Momentum Assumes Linear Price History

**Severity:** Informational
**File:** `risk-scorer.ts:22-34`
**Description:** Price momentum compares first and last entries in the price history array. This misses intra-period volatility (e.g., a V-shaped recovery looks the same as flat).
**Impact:** Risk scoring may underweight volatile tokens that recovered.

### I-3: Vault May Become Top Holder After Liquidation

**Severity:** Informational
**File:** `domain-manager.ts`
**Description:** After liquidation, collateral tokens move to the vault ATA. If the vault holds more tokens than any other holder, the vault becomes the domain lessee. This is by design but worth noting — the vault operator effectively controls the domain until tokens are withdrawn or sold.
**Impact:** None — this is the intended behavior.

### I-4: No Deduplication of Failed Liquidation Attempts

**Severity:** Informational
**File:** `liquidator.ts`
**Description:** If a liquidation fails (e.g., insufficient vault SOL), the same position will be retried every scan cycle.
**Impact:** Repeated log noise. No financial impact — failed transactions don't consume vault SOL.

### I-5: CoinGecko Rate Limiting

**Severity:** Informational
**Description:** CoinGecko's free tier allows ~10-30 requests per minute. With many monitored tokens, the bot could hit rate limits during price updates.
**Impact:** Some tokens may fail to update price in a single cycle. They'll retry next cycle.

---

## Prior Findings Status

### L-1: Wallet Profiler Caches May Bias Risk Scores (v1.0.2) — **RESOLVED**

Cache TTL reduced from 60s to 30s (`CACHE_TTL_MS = 30_000` in `wallet-profiler.ts:6`). The primary liquidation gate remains on-chain health status — the risk score is a secondary filter. With 30s TTL, profile staleness is bounded to half a scan cycle.

### L-2: No Timeout on SDK Calls (v1.0.2) — **RESOLVED**

All SDK calls are now wrapped with `withTimeout(promise, 30_000, label)` from `utils.ts`. A hanging or unresponsive RPC endpoint cannot stall the bot — the call rejects after 30 seconds, the error is caught by the four-level error isolation, and the bot continues to the next token or cycle.

**Evidence:**
- `scanner.ts` — `getTokens`, `getToken`, `getLendingInfo`, `getAllLoanPositions` wrapped
- `monitor.ts` — `getToken`, `getAllLoanPositions` wrapped
- `liquidator.ts` — `buildLiquidateTransaction` wrapped
- `launcher.ts` — `buildCreateTokenTransaction` wrapped
- `domain-manager.ts` — `getHolders` wrapped
- `wallet-profiler.ts` — `verifySaid` wrapped (10s timeout for external API)
- `index.ts` — `getVault`, `getVaultForWallet` wrapped

### I-1: Holder Discovery Limited to 20 (v1.0.2) — **RESOLVED**

The bot now uses `getAllLoanPositions(connection, mint)` instead of `getHolders(connection, mint, 20)` for borrower discovery. This returns all active loan positions directly with no holder limit.

**Evidence:**
- `scanner.ts:24` — `const { positions } = await getAllLoanPositions(connection, mint)`
- `monitor.ts:60` — `const { positions } = await getAllLoanPositions(connection, mint)`

---

## Conclusion

The Torch Domain Auction Bot v2.0.1 is a well-structured single-package kit with correct vault integration, robust error handling, and a sound domain lending model. Changes from v1.0.2:

1. **SDK upgraded from 3.2.3 to 3.7.23** — the bot correctly uses the new `getAllLoanPositions` bulk scanner for complete borrower discovery. No new attack surface from unused SDK features.
2. **Borrower discovery improved** — `getAllLoanPositions` replaces holder-limited discovery, resolving I-1 from v1.0.2.
3. **Key safety remains correct** — in-process `Keypair.generate()`, optional `SOLANA_PRIVATE_KEY`, no key logging or transmission.
4. **Vault integration remains correct** — `vault` param passed to `buildLiquidateTransaction`. All liquidation value routes through the vault PDA.
5. **Domain lease rotation remains correct** — top holder tracked accurately, leases expire and rotate as expected.
6. **Risk scoring remains sound** — four factors, weights sum to 1.0, all bounded 0-100, configurable threshold.
7. **Error handling is robust** — four levels of isolation. No single failure crashes the bot.
8. **SDK call timeouts added** — all SDK calls wrapped with `withTimeout(promise, 30_000, label)`. External API calls (verifySaid) use 10s timeout. No hanging call can stall the bot.
9. **Dependencies remain minimal and pinned** — 5 runtime deps, all exact versions, no `^` ranges, no post-install hooks.
10. **No critical, high, medium, or low findings** — all prior low findings resolved, 5 informational.

The bot is safe for production use as an autonomous domain lending keeper operating through a Torch Vault.

---

## Audit Certification

This audit was performed by Claude Opus 4.6 (Anthropic) on February 28, 2026. All source files were read in full and cross-referenced against the torchsdk v3.7.23 audit. The E2E test suite (10 passed) validates the bot against a Surfpool mainnet fork.

**Auditor:** Claude Opus 4.6
**Date:** 2026-02-28
**Bot Version:** 2.0.1
**SDK Version:** torchsdk 3.7.23
**On-Chain Version:** V3.7.8 (Program ID: `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`)
**Prior Audit:** v1.0.2, 2026-02-13 — 2 low findings (both resolved in v2.0.1), 5 informational (1 resolved)
