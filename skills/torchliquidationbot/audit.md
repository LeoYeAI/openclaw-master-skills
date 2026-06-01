# Torch Liquidation Bot — Security Audit

**Audit Date:** February 27, 2026
**Auditor:** Claude Opus 4.6 (Anthropic)
**Bot Version:** 4.0.2
**Kit Version:** 2.0.0
**SDK Version:** torchsdk 3.7.22
**On-Chain Program:** `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT` (V3.7.7, 27 instructions)
**Language:** TypeScript
**Test Result:** 9 passed, 0 failed (Surfpool mainnet fork)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Scope](#scope)
3. [Methodology](#methodology)
4. [What Changed (v3.0.2 → v4.0.0)](#what-changed-v302--v400)
5. [Keypair Safety Review](#keypair-safety-review)
6. [Vault Integration Review](#vault-integration-review)
7. [Scan Loop Security](#scan-loop-security)
8. [Configuration Validation](#configuration-validation)
9. [Dependency Analysis](#dependency-analysis)
10. [Threat Model](#threat-model)
11. [Findings](#findings)
12. [Resolved Findings from v3.0.2](#resolved-findings-from-v302)
13. [Conclusion](#conclusion)

---

## Executive Summary

This audit covers the Torch Liquidation Bot v4.0.0, an autonomous keeper that scans Torch Market lending positions and liquidates underwater loans through a Torch Vault. The bot was reviewed for key safety, vault integration correctness, error handling, and dependency surface.

The major change in v4.0.0 is the replacement of the N+1 scan pattern (`getLendingInfo` → `getHolders` → per-holder `getLoanPosition`) with a single `getAllLoanPositions()` call per token. This reduces RPC calls from 2 + N per token to 1 per token, eliminates the 20-holder discovery ceiling from the previous version, and leverages the SDK's pre-sorted output to break early once all liquidatable positions are processed.

The bot remains **vault-first** (all value routes through the vault PDA), **disposable-key** (agent keypair generated in-process, holds nothing), and **single-purpose** (scan and liquidate only — no trading, borrowing, or token creation).

### Overall Assessment

| Category | Rating | Notes |
|----------|--------|-------|
| Key Safety | **PASS** | In-process `Keypair.generate()`, no key files, no key logging |
| Vault Integration | **PASS** | `vault` param correctly passed to `buildLiquidateTransaction` |
| Error Handling | **PASS** | Cycle-level catch, per-token try/catch, per-liquidation try/catch, 30s RPC timeout |
| Config Validation | **PASS** | Required env vars checked, scan interval floored at 5000ms |
| Dependencies | **MINIMAL** | 2 runtime deps, both pinned exact |
| Supply Chain | **LOW RISK** | No post-install hooks, no remote code fetching |

### Finding Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 (1 resolved) |
| Informational | 2 |

---

## Scope

### Files Reviewed

| File | Lines | Role |
|------|-------|------|
| `packages/bot/src/index.ts` | 192 | Entry point: keypair load/generate, vault check, scan loop |
| `packages/bot/src/config.ts` | 36 | Environment variable validation |
| `packages/bot/src/types.ts` | 13 | BotConfig and LogLevel interfaces |
| `packages/bot/src/utils.ts` | 58 | Formatting helpers, logger, base58 decoder, RPC timeout |
| `packages/bot/tests/test_e2e.ts` | 248 | E2E test suite |
| `packages/bot/package.json` | 37 | Dependencies and scripts |
| `packages/bot/tsconfig.json` | 20 | TypeScript configuration |
| **Total** | **~604** | |

### SDK Cross-Reference

The bot relies on `torchsdk@3.7.22` for all on-chain interaction. The SDK was independently audited (see [Torch SDK Audit](https://torch.market/audit.md)). This audit focuses on the bot's usage of the SDK, not the SDK internals.

Key SDK changes since v3.2.3:
- `getAllLoanPositions()` added in v3.7.17 — bulk loan scanning via `getProgramAccounts`
- V33 buyback removal (v3.7.22) — `buildAutoBuybackTransaction` deleted
- Lending utilization cap increased 50% → 70% (v3.7.22)
- Protocol fee split changed to 90% treasury / 10% dev (V32)
- IDL updated to v3.7.7 (27 instructions, down from 28)

---

## Methodology

1. **Line-by-line source review** of all 4 bot source files
2. **Delta analysis** against v3.0.2 audit — focused review of changed code paths
3. **Keypair lifecycle analysis** — generation, usage, exposure surface
4. **Vault integration verification** — correct params passed to SDK
5. **Error handling analysis** — crash paths, retry behavior, log safety
6. **Dependency audit** — runtime deps, dev deps, post-install hooks
7. **E2E test review** — coverage, assertions, sort order validation
8. **Configuration attack surface** — environment variable handling

---

## What Changed (v3.0.2 → v4.0.0)

### Scan Pattern Rewrite

The core scan loop was rewritten to use `getAllLoanPositions()`:

**Before (v3.0.2):**
```
getTokens → for each token:
  getLendingInfo     → skip if no active loans
  getHolders         → get up to 20 holders
  getLoanPosition    → check each holder individually
  buildLiquidateTransaction → if liquidatable
```

**After (v4.0.0):**
```
getTokens → for each token:
  getAllLoanPositions → all active loans, sorted by health
  break              → stop at first non-liquidatable (pre-sorted)
  buildLiquidateTransaction → for each liquidatable
```

### Import Changes

**Removed:** `getLendingInfo`, `getHolders`, `getLoanPosition`, `type LendingInfo`, `type LoanPositionInfo`
**Added:** `getAllLoanPositions`, `type LoanPositionWithKey`

### Impact

| Metric | v3.0.2 | v4.0.0 |
|--------|--------|--------|
| RPC calls per token | 2 + N (lending + holders + per-holder position) | 1 (`getAllLoanPositions`) |
| Max discoverable borrowers | 20 (`getTokenLargestAccounts` limit) | Unlimited (scans all LoanPosition PDAs) |
| Source lines (index.ts) | 210 | 187 |
| SDK imports | 10 | 7 |
| Error isolation levels | 4 (cycle, token, holder, liquidation) | 3 (cycle, token, liquidation) |

The reduction from 4 to 3 error isolation levels is correct — the holder level is no longer needed because `getAllLoanPositions` returns positions directly.

---

## Keypair Safety Review

### Generation

Unchanged from v3.0.2. The keypair is created in `main()` via one of two paths:

1. **Default (recommended):** `Keypair.generate()` — fresh Ed25519 keypair from system entropy
2. **Optional:** `SOLANA_PRIVATE_KEY` env var — loaded as JSON byte array or base58, decoded via `Keypair.fromSecretKey()`

```typescript
// index.ts:137-153 — load or generate agent keypair
let agentKeypair: Keypair
if (config.privateKey) {
  // try JSON byte array, then base58
  agentKeypair = Keypair.fromSecretKey(...)
} else {
  agentKeypair = Keypair.generate()
}
```

The keypair is:

- **Not persisted** — exists only in runtime memory (unless user provides `SOLANA_PRIVATE_KEY`)
- **Not exported** — `agentKeypair` is local to `main()`, not in the public API
- **Not logged** — only the public key is printed (`agentKeypair.publicKey.toBase58()`)
- **Not transmitted** — the secret key never leaves the process

### Usage

The keypair is used in exactly two places:

1. **Public key extraction** (startup logging, vault link check, liquidation params) — safe, public key only
2. **Transaction signing** (`transaction.sign(agentKeypair)` at index.ts:86) — local signing only

### Risk Assessment

The keypair holds ~0.01 SOL for gas. If the process memory is dumped, the attacker gets:
- A disposable key with dust
- Vault access that the authority revokes in one transaction

**Verdict:** Key safety is correct. No key material leaks from the process. Unchanged from v3.0.2.

---

## Vault Integration Review

### Startup Verification

Unchanged from v3.0.2:

```typescript
const vault = await getVault(connection, config.vaultCreator)  // index.ts:142
if (!vault) throw new Error(...)

const link = await getVaultForWallet(connection, agentKeypair.publicKey.toBase58())  // index.ts:149
if (!link) { /* print instructions, exit */ }
```

The bot verifies both vault existence and agent linkage before entering the scan loop. If either fails, the process exits with clear instructions.

### Liquidation Transaction

```typescript
const { transaction, message } = await buildLiquidateTransaction(connection, {
  mint: token.mint,
  liquidator: agentKeypair.publicKey.toBase58(),
  borrower: position.borrower,   // now from getAllLoanPositions result
  vault: vaultCreator,            // index.ts:83
})
```

The `vault` parameter is correctly passed. The `borrower` field now comes from `LoanPositionWithKey.borrower` (returned by `getAllLoanPositions`) instead of `holder.address` (from `getHolders`). Both are base58 public key strings — the type is unchanged.

Per the SDK audit, the `vault` param causes:
- Vault PDA derived from `vaultCreator` (`["torch_vault", creator]`)
- Wallet link PDA derived from `liquidator` (`["vault_wallet", wallet]`)
- SOL debited from vault, collateral tokens credited to vault ATA

**Verdict:** Vault integration is correct. All value routes through the vault PDA.

---

## Scan Loop Security

### Error Isolation

**Cycle level** — never crashes the loop (unchanged):
```typescript
while (true) {
  try {
    await scanAndLiquidate(connection, log, config.vaultCreator, agentKeypair)
  } catch (err: any) {
    log('error', `scan cycle error: ${err.message}`)
  }
  await new Promise(resolve => setTimeout(resolve, config.scanIntervalMs))
}
```

**Token level** — skip tokens where `getAllLoanPositions` fails:
```typescript
for (const token of tokens) {
  let positions: LoanPositionWithKey[]
  try {
    const result = await getAllLoanPositions(connection, token.mint)
    positions = result.positions
  } catch {
    continue  // lending not enabled for this token
  }

  if (positions.length === 0) continue
```

**Liquidation level** — each liquidation attempt is individually caught:
```typescript
try {
  const { transaction, message } = await buildLiquidateTransaction(...)
  transaction.sign(agentKeypair)
  const signature = await connection.sendRawTransaction(transaction.serialize())
  await confirmTransaction(...)
  log('info', `LIQUIDATED | ...`)
} catch (err: any) {
  log('warn', `LIQUIDATION FAILED | ...`)
}
```

### Break Optimization

```typescript
// index.ts:67-68
for (const position of positions) {
  if (position.health !== 'liquidatable') break
```

This is correct because `getAllLoanPositions` returns positions sorted by health: `liquidatable → at_risk → healthy`. Once the first non-liquidatable position is encountered, all remaining positions are also non-liquidatable. The E2E test (test_e2e.ts:159-174) independently validates this sort order.

**Verdict:** Error handling is robust. The bot degrades gracefully at every level. The break optimization is correct and validated by tests.

---

## Configuration Validation

Unchanged from v3.0.2.

### Required Variables

| Variable | Validation | Failure Mode |
|----------|-----------|--------------|
| `SOLANA_RPC_URL` | Must be set (fallback: `RPC_URL`) | Throws on startup |
| `VAULT_CREATOR` | Must be set | Throws on startup |
| `SCAN_INTERVAL_MS` | Must be >= 5000 | Throws on startup |
| `LOG_LEVEL` | Must be `debug\|info\|warn\|error` | Throws on startup |

### Defaults

| Variable | Default |
|----------|---------|
| `SCAN_INTERVAL_MS` | 30000 |
| `LOG_LEVEL` | `info` |

### Security Notes

- `SOLANA_RPC_URL` is used only for Solana RPC calls — never logged, transmitted externally, or stored
- `VAULT_CREATOR` is a public key (not sensitive)
- `SOLANA_PRIVATE_KEY` is optional — if provided, it is read once at startup and used to derive the keypair via `Keypair.fromSecretKey()`. The raw string is never logged or transmitted. If omitted, the bot generates a fresh keypair with `Keypair.generate()` (recommended).

**Verdict:** Configuration is properly validated. Sensitive `SOLANA_PRIVATE_KEY` is handled safely when provided.

---

## Dependency Analysis

### Runtime Dependencies

| Package | Version | Pinning | Post-Install | Risk |
|---------|---------|---------|-------------|------|
| `@solana/web3.js` | 1.98.4 | Exact | None | Low — standard Solana |
| `torchsdk` | 3.7.22 | Exact | None | Low — audited separately |

### Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@types/node` | 20.19.33 | TypeScript types |
| `prettier` | 3.8.1 | Code formatting |
| `typescript` | 5.9.3 | Compilation |

### Supply Chain

- **No `^` or `~` version ranges** — all dependencies pinned to exact versions
- **No post-install hooks** — `"scripts"` contains only `build`, `clean`, `test`, `format`
- **No remote code fetching** — no dynamic `import()`, no `eval()`, no fetch-and-execute
- **Lockfile present** — `pnpm-lock.yaml` pins transitive dependencies

### External Runtime Dependencies

The SDK contains functions that make outbound HTTPS requests. The bot's runtime path contacts **two** external services:

| Service | Purpose | When Called | Bot Uses? |
|---------|---------|------------|-----------|
| **CoinGecko** (`api.coingecko.com`) | SOL/USD price for display | Token queries via `getTokens()` | Yes |
| **Irys Gateway** (`gateway.irys.xyz`) | Token metadata fallback | `getTokens()` when metadata URI points to Irys | Yes |
| **SAID Protocol** (`api.saidprotocol.com`) | Agent identity verification | `verifySaid()` only | **No** — bot does not call `verifySaid()` |

**Important:** `confirmTransaction()` does NOT contact SAID Protocol. Despite residing in the SDK's `said.js` module, it only calls `connection.getParsedTransaction()` (Solana RPC) to verify the transaction succeeded on-chain. No transaction data or agent identifiers are sent to any external reputation service.

Data transmitted to external services:
- **CoinGecko:** Read-only GET for SOL/USD price. No wallet, transaction, or agent data sent.
- **Irys:** Read-only GET for token metadata (name, symbol, image). No wallet or transaction data sent.

No credentials are sent. If either service is unreachable, the SDK degrades gracefully. No private key material is ever transmitted to any external endpoint.

**Verdict:** Minimal and locked dependency surface. No supply chain concerns. External network calls are read-only, non-critical, and transmit no sensitive data.

---

## Threat Model

### Threat: Compromised Agent Keypair

**Attack:** Attacker obtains the agent's private key from process memory.
**Impact:** Attacker can sign transactions as the agent.
**Mitigation:** The agent keypair holds ~0.01 SOL. The vault's value is controlled by the authority, who can unlink the compromised wallet in one transaction. The attacker cannot call `withdrawVault` or `withdrawTokens`.
**Residual risk:** Attacker could execute vault-routed trades until unlinked. Limited by vault SOL balance.

### Threat: Malicious RPC Endpoint

**Attack:** RPC returns fabricated loan positions to trick the bot into unprofitable liquidations.
**Impact:** The bot liquidates positions that aren't actually underwater, losing vault SOL.
**Mitigation:** The on-chain program validates all liquidation preconditions. A fabricated RPC response would produce a transaction that fails on-chain.
**Residual risk:** None — on-chain validation is the actual security boundary.

### Threat: Fabricated getAllLoanPositions Results

**Attack:** A compromised or malicious RPC returns positions with `health: 'liquidatable'` for loans that are actually healthy.
**Impact:** Bot builds liquidation transactions that fail on-chain (program checks LTV).
**Mitigation:** Same as above — on-chain program enforces liquidation threshold. The `health` field from `getAllLoanPositions` is a client-side convenience; the program independently verifies collateral value vs debt. A failed liquidation costs only the transaction fee (~0.000005 SOL).
**Residual risk:** Wasted gas on failed transactions. No vault SOL lost on failed liquidations.

### Threat: RPC Rate Limiting / DDoS

**Attack:** Overwhelming the bot with slow/failed RPC responses.
**Impact:** Bot can't discover or liquidate positions.
**Mitigation:** `SCAN_INTERVAL_MS` floor of 5000ms. Each scan cycle is independent. Bot recovers on next cycle.
**Residual risk:** Missed liquidation opportunities during outage.

### Threat: Front-Running

**Attack:** MEV bot observes the liquidation transaction in mempool and front-runs it.
**Impact:** Bot's transaction fails (`NOT_LIQUIDATABLE` — position already liquidated).
**Mitigation:** The bot catches the error and moves to the next position. No vault SOL is lost on a failed liquidation.
**Residual risk:** Reduced liquidation success rate in competitive MEV environments.

---

## Findings

### L-1: No Timeout on SDK Calls — RESOLVED in v4.0.1

**Severity:** Low
**File:** `utils.ts:12-21`, `index.ts` (all SDK call sites)
**Description:** SDK calls (`getTokens`, `getAllLoanPositions`, `buildLiquidateTransaction`, `confirmTransaction`, `getVault`, `getVaultForWallet`) previously had no explicit timeout. A hanging RPC endpoint could block the scan loop indefinitely.
**Resolution:** All 6 SDK calls are now wrapped with `withTimeout(promise, label)` which races against a 30-second deadline via `Promise.race`. Timeouts in the scan loop are caught by existing try/catch layers — the bot logs the timeout and continues. Startup timeouts surface as a FATAL error (correct behavior — if RPC is unreachable at startup, the bot should not silently hang).
**Status:** Resolved in v4.0.1.

### I-1: No Deduplication Across Cycles

**Severity:** Informational
**Description:** The bot checks all tokens and all positions on every cycle. If a liquidation fails (e.g., insufficient vault SOL), the same position will be retried on every cycle.
**Impact:** Repeated log noise for positions that can't be liquidated. No security impact.

### I-2: getAllLoanPositions Uses getProgramAccounts

**Severity:** Informational
**Description:** `getAllLoanPositions` internally calls `getProgramAccounts` with discriminator + mint filters to find all LoanPosition accounts. Some RPC providers rate-limit or restrict `getProgramAccounts`. The bot falls back gracefully (the `catch` block skips the token), but tokens may be silently skipped if the RPC provider blocks this call.
**Impact:** Missed liquidation opportunities on restrictive RPC providers. No security impact. The previous `getHolders` approach (`getTokenLargestAccounts`) had the same class of issue.
**Recommendation:** Use an RPC provider that supports `getProgramAccounts` without restrictions (Helius, Triton, QuickNode, or a private validator).

---

## Resolved Findings from v3.0.2

### L-1 (v3.0.2): Agent Keypair Regenerated on Every Restart

**Status:** Resolved in v3.0.2. Optional `SOLANA_PRIVATE_KEY` env var allows persisting the agent wallet. Still resolved in v4.0.0.

### I-1 (v3.0.2): Holder Discovery Limited to 20

**Status:** Resolved in v4.0.0. The bot no longer calls `getHolders` / `getTokenLargestAccounts`. `getAllLoanPositions` scans all LoanPosition PDAs directly via `getProgramAccounts` with no holder count ceiling.

### I-3 (v3.0.2): Log Level Filter Uses String Comparison

**Status:** Still present, still informational. For a bot with 30-second cycle intervals, this is irrelevant.

### I-4 (v3.0.2): Surfpool getTokenLargestAccounts Limitation

**Status:** Resolved in v4.0.0. The bot no longer calls `getHolders` / `getTokenLargestAccounts`. The E2E test no longer depends on this Surfpool-limited RPC method.

---

## Conclusion

The Torch Liquidation Bot v4.0.2 is a cleaner, more efficient keeper with correct vault integration and robust error handling. Key findings:

1. **Key safety is correct** — in-process `Keypair.generate()` by default, optional `SOLANA_PRIVATE_KEY` for persistence. No key logging, no key transmission. Unchanged from v3.0.2.
2. **Vault integration is correct** — `vault` param passed to `buildLiquidateTransaction`, SOL from vault, collateral to vault ATA. Unchanged from v3.0.2.
3. **Scan pattern improved** — `getAllLoanPositions` replaces the N+1 holder scan. One RPC call per token, no 20-holder ceiling, pre-sorted results with early break. Two v3.0.2 findings (I-1, I-4) are resolved by this change.
4. **Error handling is robust** — three levels of isolation (cycle, token, liquidation) plus 30-second RPC timeouts on all SDK calls. A hanging RPC cannot stall the bot.
5. **Dependency surface is minimal** — 2 runtime deps, both pinned exact, no post-install hooks. SDK upgraded from 3.2.3 to 3.7.22.
6. **No critical, high, medium, or low findings** — L-1 (no timeout) resolved in v4.0.1. 2 informational issues remain.

The bot is safe for production use as an autonomous liquidation keeper operating through a Torch Vault.

---

## Audit Certification

This audit was performed by Claude Opus 4.6 (Anthropic) on February 27, 2026. All source files were read in full and cross-referenced against the torchsdk v3.7.22 audit. The E2E test suite (9 passed, 0 failed) validates the bot against a Surfpool mainnet fork, including sort order verification for `getAllLoanPositions`.

**Auditor:** Claude Opus 4.6
**Date:** 2026-02-27
**Bot Version:** 4.0.2
**Kit Version:** 2.0.0
**SDK Version:** torchsdk 3.7.22
**On-Chain Version:** V3.7.7 (Program ID: `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`, 27 instructions)
