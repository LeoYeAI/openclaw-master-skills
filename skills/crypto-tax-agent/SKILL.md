---
name: crypto-tax-agent
description: 'Crypto tax compliance skill for AI agents. Covers 1099-DA reconciliation, cost basis methods (FIFO/HIFO/SpecID), multi-chain transaction reconstruction via Etherscan V2 API, Form 8949 generation, DEX gap analysis, staking/airdrop classification, bridge handling, and wash sale analysis. Use when an agent needs to handle crypto tax work, analyze transaction history, or generate tax forms.'
license: MIT
metadata:
  openclaw:
    emoji: '📊'
---

# Crypto Tax Agent

Crypto tax compliance skill for AI agents. Handles end-to-end tax workflows for digital asset holders: transaction ingestion, cost basis computation, IRS form generation, 1099-DA reconciliation, and audit defense documentation.

---

## WHEN TO USE

- Client has cryptocurrency, NFT, or DeFi activity and needs tax reporting
- Reconciling 1099-DA forms against actual transaction history
- Reconstructing cost basis for assets transferred between wallets or exchanges
- Classifying staking rewards, airdrops, LP yields, or bridge transactions for tax purposes
- Generating Form 8949, Schedule D, or TXF exports
- Analyzing wash sale opportunities (tax-loss harvesting)
- Preparing audit defense documentation with on-chain proof links
- Evaluating zero-basis disposals flagged by brokers
- Multi-chain transaction extraction (EVM chains, Solana)
- Client received a CP2000 or AUR notice related to crypto

## WHEN NOT TO USE

- Traditional securities (stocks, bonds, options) — use standard tax tooling
- Crypto mining operations requiring Schedule C / business entity analysis — escalate to CPA
- Foreign account reporting (FBAR/FATCA for offshore exchanges) — requires specialized compliance counsel
- Tax planning or entity structuring advice — this skill reports, it does not advise on structure
- Criminal tax matters or voluntary disclosure — escalate to tax attorney immediately
- Clients with OFAC-sanctioned protocol interactions (e.g., Tornado Cash) — stop work, notify client, escalate to counsel
- State-specific crypto tax rules beyond federal — note the gap and flag for CPA review
- NFT creator royalty accounting (1099-NEC territory) — different reporting regime

---

## 1. FORM 1099-DA — BROKER REPORTING

### Phase-In Timeline

| Tax Year | Requirement | Authority |
|---|---|---|
| **2025** (forms due Feb 2026) | Gross proceeds only mandatory. Cost basis voluntary. | IIJA P.L. 117-58; Treasury Decision 10000 (Jul 9, 2024) |
| **2026+** | Gross proceeds + cost basis mandatory for covered securities. | Same |

- **Covered securities** = assets acquired on or after January 1, 2026. Everything acquired before that date is noncovered.
- **IRS Notice 2024-56**: No penalties for 1099-DA failures in the first reporting year (TY 2025).
- **IRS Notice 2024-57**: Defers reporting for wrapping/unwrapping, LP deposits/withdrawals, staking, lending, short sales, and airdrops.

### Who Files 1099-DA

- Centralized exchanges (Coinbase, Kraken, Gemini, Binance.US)
- Digital asset payment processors, kiosk operators, hosted wallets

### Who Does NOT File 1099-DA

- DEXs — **H.J. Res. 25** (signed April 10, 2025) killed the DeFi broker reporting rule
- Non-US exchanges
- Self-custody wallets

### Key Traps

- **NFT double-reporting**: Creator first-sale proceeds should appear in Box 11c only, not Box 1f. Verify before filing.
- **UTC timestamp mismatch**: A December 31 CST sale can appear as January 1 UTC on the 1099-DA. Reconcile timezones against exchange records.
- **Transfer-out = zero basis**: When assets move between wallets/exchanges, the receiving broker has no acquisition cost and may report zero basis. This creates a phantom 100% gain.

---

## 2. COST BASIS METHODS

### IRS-Approved Methods

| Method | Description | Status |
|---|---|---|
| **FIFO** (First In, First Out) | Oldest units sold first | **Default if no election made** |
| **Specific Identification** | Taxpayer designates exact units at time of disposal | Requires contemporaneous documentation |

- **HIFO** (Highest In, First Out) and **LIFO** (Last In, First Out) are only valid as implementations of Specific Identification. The taxpayer must identify the specific lots BEFORE the disposal occurs.
- **2025 rule change**: Per-wallet accounting is now required. The universal pool method was terminated effective January 1, 2025.
- **Rev. Proc. 2024-28**: Permitted a one-time basis reallocation to specific wallets by January 1, 2025. This election is irrevocable.

### Interaction with 1099-DA

- **TY 2025**: Brokers report proceeds only. Taxpayer determines their own basis — the agent must compute this.
- **TY 2026+**: Brokers will use their own tracking method for basis. If the taxpayer uses a different method, a Form 8949 adjustment is required. This creates AUR (Automated Underreporter) mismatch risk.

### Per-Wallet Tax Lot Tracking

Every disposal must be traced to a specific tax lot within a specific wallet:

```
Tax Lot = {
  asset,
  units_remaining,
  acquisition_date,
  acquisition_cost_usd,
  cost_per_unit_usd,
  source_transaction,
  wallet_address       // Required since TY 2025
}
```

---

## 3. THE MATCHING PROBLEM

### Zero-Basis Trap

When assets transfer between wallets or exchanges, the receiving platform has no record of the original acquisition cost. The IRS assumes **zero cost basis**, making the entire sale amount a taxable gain.

### Reconstruction Steps

1. **Identify** all noncovered/no-basis disposals (1099-DA Box 9 checked, Box 1g blank)
2. **Reconstruct** acquisition history from source records (exchange CSVs, on-chain data)
3. **Document** the full transfer chain: acquisition -> transfer -> sale
4. **Report** on Form 8949 with adjustment Code **"B"** (short-term, basis not reported) or **"E"** (long-term, basis not reported)
5. **Retain** all records for 3-7 years minimum

### Agent Workflow for Basis Reconstruction

```
For each zero-basis disposal:
  1. Get the asset and wallet where the sale occurred
  2. Trace backwards: find the TRANSFER_IN to that wallet
  3. Match TRANSFER_IN to a TRANSFER_OUT from another wallet (time ± 30min, same asset, same qty ± fees)
  4. At the source wallet, find the original acquisition (BUY, SWAP, INCOME, AIRDROP)
  5. Carry that cost basis forward through the transfer chain
  6. Document the full chain with tx hashes as proof
```

---

## 4. DEFI TRANSACTIONS

### DEX Swaps

- Every token-for-token swap is a **taxable disposition** (IRS Notice 2014-21, FAQ Q17)
- No 1099-DA is issued for DEX activity (H.J. Res. 25)
- Entirely self-reported — full audit exposure if omitted
- Gas fees are added to cost basis of the asset received

### LP (Liquidity Provider) Positions

- **Deposit**: Potentially a taxable exchange (no explicit IRS guidance; conservative position = taxable)
- **LP yield/fees**: Ordinary income at FMV when received
- **Withdrawal**: Taxable event. Impermanent loss creates additional complexity.
- Reporting deferred under IRS Notice 2024-57 — no broker reporting requirement currently, but the taxpayer obligation remains

### Staking Rewards

- **Ordinary income** at fair market value on the date tokens are received
- Authority: **Rev. Rul. 2023-14** (definitive); **CCA 202444009** (Oct 2024)
- Income is recognized when the taxpayer gains "dominion and control" over the reward tokens
- Cost basis of the received tokens = FMV at time of receipt (this becomes the basis for future disposals)

### Airdrops

- **Ordinary income** at FMV when the taxpayer has dominion and control
- If unsolicited and immediately worthless (e.g., spam tokens): potentially zero income, but document the rationale
- Cost basis = FMV at receipt

### Cross-Chain Bridges

- **No explicit IRS guidance** as of March 2026
- **Conservative position**: Taxable exchange (dispose of asset on Chain A, receive equivalent on Chain B)
- **Aggressive position**: Non-taxable transfer (same asset, different representation — analogous to moving between wallets)
- The agent should default to the non-taxable transfer treatment but flag every bridge event for CPA review
- Document everything — this area will be litigated

### Bridge Detection Heuristic

```
A transaction pair is a bridge if:
  1. Time correlation: outbound and inbound within ± 30 minutes
  2. Amount correlation: same asset, same quantity ± bridge fees
  3. Contract match: interaction with a known bridge contract
     (Base Bridge, Arbitrum Gateway, Optimism Bridge, Across, Stargate)
  4. Chain difference: source chain != destination chain
```

When a bridge is detected: do NOT count as a disposal. Carry cost basis from the source chain lot to the destination chain lot.

### Privacy / Mixer Red Flags

- **CRITICAL**: OFAC-sanctioned protocols (Tornado Cash) — stop all work, notify client, escalate to counsel
- **WARNING**: Privacy coins (XMR, ZEC shielded transactions) — request written explanation from client before proceeding
- **INFO**: Privacy-preserving DeFi (Aztec) — note in file, proceed with normal treatment

---

## 5. WASH SALE RULES

### Current Status (as of March 2026)

- Cryptocurrency is **NOT** subject to wash sale rules under IRC Section 1091
- Section 1091 applies only to "stock or securities" — crypto is classified as "property" per IRS Notice 2014-21
- Multiple legislative proposals to extend wash sales to crypto have failed
- **Tax-loss harvesting remains fully legal** for crypto assets

### Agent Behavior

- Run wash sale detection as an **informational analysis** (within 30-day window, across all wallets)
- Present results as opportunities, not restrictions
- Flag any pending legislation that could change this treatment
- Note: if future legislation applies retroactively, the analysis will already be documented

---

## 6. TOP 5 AUDIT TRIGGERS

1. **Unreported income** — 1099-DA exists but no corresponding entry on the return
2. **Zero-basis disposals** — transferred assets sold without documenting original acquisition cost
3. **Staking/airdrop omission** — treating reward income as non-taxable (directly contradicts Rev. Rul. 2023-14)
4. **DEX activity not reported** — no 1099-DA does not mean no tax obligation; IRS can see on-chain activity
5. **Inconsistent cost basis methods** — switching between FIFO and SpecID across wallets without proper documentation

---

## 7. MULTI-CHAIN DATA EXTRACTION

### Etherscan V2 Unified API

**Base endpoint**: `https://api.etherscan.io/v2/api`

A single API key covers all major EVM chains:

| Chain | Chain ID |
|---|---|
| Ethereum | 1 |
| Base | 8453 |
| Arbitrum | 42161 |
| Optimism | 10 |
| Polygon | 137 |

**Per wallet, per chain — 5 API calls required:**

| Call | Module/Action | What It Returns |
|---|---|---|
| Normal transactions | `module=account&action=txlist` | ETH/native token transfers, contract calls |
| Internal transactions | `module=account&action=txlistinternal` | Internal ETH movements (contract-to-contract) |
| ERC-20 transfers | `module=account&action=tokentx` | Fungible token transfers |
| ERC-721 transfers | `module=account&action=tokennfttx` | NFT transfers |
| ERC-1155 transfers | `module=account&action=token1155tx` | Multi-token standard transfers |

**Rate limiting**: Free tier allows 5 calls/sec. For 5 wallets across 5 chains: 5 x 5 x 5 = 125 calls, completing in ~25 seconds.

### Solana: Helius Enhanced Transaction API

- **Endpoint**: POST to `/v0/addresses/{address}/transactions`
- Pre-classifies transactions into types: `SWAP`, `TRANSFER`, `NFT_SALE`, `STAKE`, etc.
- Cost: $50/month (shared across clients)

### Historical Price Data

- **CoinGecko API** (free tier): 30 calls/min, sufficient for historical FMV lookups
- Required for: staking reward valuation, airdrop FMV, DEX swap valuation, cost basis at acquisition

---

## 8. DELIVERABLE FORMAT

Every engagement produces the following deliverables:

### Tax Forms

| Deliverable | Description |
|---|---|
| **Form 8949 Part I** | Short-term capital gains/losses (held ≤ 1 year) |
| **Form 8949 Part II** | Long-term capital gains/losses (held > 1 year) |
| **Schedule D** | Summary of capital gains/losses from Form 8949 |
| **TXF Export** | Machine-readable file for import into TurboTax, Drake, Lacerte, ProSeries |

### Supporting Documentation

| Deliverable | Description |
|---|---|
| **1099-DA Reconciliation Memo** | Line-by-line comparison of broker-reported proceeds vs. agent-computed values, with explanations for every discrepancy |
| **Complete Transaction Log** | CSV of all transactions across all chains/exchanges, normalized to a single schema |
| **Tax Position Summary** | 1-page overview: total proceeds, total basis, net gain/loss, ordinary income from staking/airdrops, carryover losses |
| **Audit Defense Notes** | On-chain proof links (block explorer URLs) for every material transaction, transfer chain documentation, basis reconstruction methodology |

### Form 8949 Adjustment Codes

| Code | Use Case |
|---|---|
| **B** | Short-term, basis NOT reported to IRS on 1099-DA |
| **E** | Long-term, basis NOT reported to IRS on 1099-DA |
| **O** | Other adjustment (used for bridge reclassification, gas fee basis adjustment) |

---

## 9. TRANSACTION CLASSIFICATION SCHEMA

The agent normalizes all transactions into these types:

| Type | Tax Treatment | Income Type |
|---|---|---|
| `BUY` | Not taxable (establishes cost basis) | — |
| `SELL` | Capital gain/loss | Capital |
| `SWAP` | Taxable disposition + acquisition | Capital |
| `TRANSFER_IN` | Not taxable (basis carries over) | — |
| `TRANSFER_OUT` | Not taxable (basis carries over) | — |
| `BRIDGE` | Not taxable (basis carries over, flag for review) | — |
| `INCOME` | Ordinary income at FMV | Ordinary |
| `AIRDROP` | Ordinary income at FMV | Ordinary |
| `STAKE` | Not taxable (locks existing asset) | — |
| `UNSTAKE` | Not taxable (unlocks existing asset) | — |
| `LP_ADD` | Potentially taxable (flag for CPA review) | Capital |
| `LP_REMOVE` | Potentially taxable (flag for CPA review) | Capital |
| `NFT_MINT` | Cost basis = mint price + gas | — |
| `NFT_SALE` | Capital gain/loss | Capital |
| `WRAP` | Not taxable (deferred per Notice 2024-57) | — |
| `UNWRAP` | Not taxable (deferred per Notice 2024-57) | — |
| `BORROW` | Not taxable | — |
| `REPAY` | Not taxable | — |

---

## 10. COMPLIANCE VERIFICATION CHECKLIST

Before finalizing any deliverable, the agent must verify:

1. Gross proceeds computed ≥ all 1099-DA reported amounts (no under-reporting)
2. Cost basis ≤ actual acquisition price (no inflated basis)
3. Holding period is verifiable on-chain (short-term vs. long-term classification)
4. Wash sale detection has been run across all wallets (informational, not restrictive)
5. Bridge transactions are not double-counted as disposals
6. Staking rewards are classified as ordinary income (Rev. Rul. 2023-14)
7. Gas fees are properly allocated to cost basis of the received asset
8. All 1099-DA discrepancies are documented in the reconciliation memo
9. Every Form 8949 line with a basis adjustment includes the correct Code (B, E, or O)
10. Audit defense notes include block explorer links for transactions over $10,000

---

## IRS Authority Reference

| Citation | Topic |
|---|---|
| IRS Notice 2014-21 | Crypto is "property" for tax purposes; general tax treatment |
| IIJA P.L. 117-58 | Infrastructure law mandating broker reporting (1099-DA) |
| Treasury Decision 10000 (Jul 2024) | Final rules implementing 1099-DA |
| IRS Notice 2024-56 | First-year penalty relief for 1099-DA |
| IRS Notice 2024-57 | Deferred reporting for wraps, LPs, staking, lending |
| Rev. Proc. 2024-28 | One-time basis reallocation to per-wallet accounting |
| Rev. Rul. 2023-14 | Staking rewards are ordinary income at receipt |
| CCA 202444009 (Oct 2024) | Confirms staking income treatment |
| H.J. Res. 25 (Apr 2025) | Killed DeFi broker reporting rule |
| IRC Section 1091 | Wash sale rules (does NOT apply to crypto) |
| IRC Section 1221/1222 | Capital asset definition, holding periods |
| Form 8949 Instructions | Reporting codes B, E, O for basis adjustments |
