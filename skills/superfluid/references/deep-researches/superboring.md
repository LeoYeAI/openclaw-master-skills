---
title: SuperBoring
date: 2026-03-19
tags: [superfluid, dca, dex, CFA, GDA, super-app, torex, base, optimism]
sources:
  - https://docs.superboring.xyz/docs/faq
  - https://docs.superboring.xyz/docs/boring
  - https://docs.superboring.xyz/docs/
  - https://app.superboring.xyz/en
  - https://github.com/superfluid-finance/averagex-contracts-cloned
  - https://github.com/superfluid-finance/torex-basic-liquidity-mover
  - https://audits.sherlock.xyz/contests/360
  - https://dune.com/superfluid_hq/superboring-overview
  - https://paragraph.com/@superboring
  - https://www.suplabs.org/
---

# SuperBoring

Streaming decentralized exchange (DEX) that automates on-chain dollar-cost averaging (DCA) using Superfluid money streams. Users stream a "sell" Super Token into a TOREX contract and receive back a "buy" token via GDA distributions. Internal codename: **averageX**. First-party product of **Superfluid Labs / SUP Labs**, not a third-party integration. **$4M+ volume on Base, ~1,000 DAU.**

---

## Identity

| Attribute | Value |
|---|---|
| Entity | Super Boring Technology Inc. (MIT license); Superfluid, Ltd. (docs) |
| Team | Superfluid Labs / SUP Labs (8 builders, London + Tallinn) |
| CTO | ZhiCheng "Miao" Miao (hellwolf) -- co-founder and CTO of Superfluid; "primarily responsible for SuperBoring's smart contract" |
| CEO | Francesco George Renzi (Superfluid co-founder) |
| COO | Michele D'Alessi (Superfluid co-founder) |
| Chains | Base (primary), Optimism; Arbitrum pending |
| Predecessor | Ricochet Exchange (community-built DCA on Polygon, IDA-based) |

---

## Products

### Streaming DCA via TOREX

**TOREX** = **T(WAP) OR(acle) EX(change)**. Core smart contract engine converting accumulated in-tokens to out-tokens.

| Property | Detail |
|---|---|
| Directionality | Each TOREX is one-directional (one per trading direction) |
| Oracle | Uniswap V3 TWAP |
| Fee | 0.5% on in-tokens |
| Custody model | Non-custodial |
| Superfluid input | CFA streams |
| Superfluid output | GDA Instant Distributions |

### DCA Mechanism

1. **User opens CFA stream** of sell Super Token to a TOREX contract at chosen flow rate
2. **In-tokens accumulate** in the TOREX contract
3. **Liquidity Movers** (external actors) execute swaps when profitable; TOREX validates price against Uniswap V3 TWAP oracle
4. **Out-tokens distributed via GDA** to all active streamers proportional to each user's streaming contribution
5. **Automatic closure** when Super Token balance depletes (Superfluid TOGA liquidation)

The companion contract **`SuperBoring.sol`** acts as the core entry point and coordination layer.

### Markets (Base)

Initial markets: DEGEN, TN100x, HIGHER, BUILD, AERO, ETH. Later added MFER.

---

## Superfluid Integration

SuperBoring is the **canonical example** of a production DCA system built on Superfluid. It exercises three core primitives in concert:

- **CFA (input side):** Users create CFA streams to TOREX. TOREX likely implements SuperApp callbacks (`afterAgreementCreated`, `afterAgreementUpdated`, `afterAgreementTerminated`)
- **GDA / Instant Distributions (output side):** Liquidity Movers distribute swapped out-tokens to all active streamers via GDA
- **Distribution Pools (BORING emissions):** Token emissions use Superfluid Distribution Pools with member units (shares) via quadratic staking formula

All tokens must be Super Tokens (USDCx, ETHx, DAIx, etc.).

---

## BORING Token

| Property | Detail |
|---|---|
| Token name | SuperBoring |
| Ticker | BORING |
| Fixed initial supply | 100,000,000 |
| Launch | July 2, 2024 |
| Tradability | Not currently enabled |
| Ethereum mainnet | `0x0Bc4dF77353ae96f31bC82bC2536bb23B2009919` |
| Base (bridged) | `0x2112b92A4f6496B7b2f10850857FfA270464d054` |
| Optimism (bridged) | `0xd9bfb8A24c8E1889787Ea0f99D77C952a82Bfe50` |

### Staking Mechanics

Users stake BORING into specific TOREXes to earn a share of that TOREX's 0.5% in-token fees. More BORING staked on a TOREX = more BORING emissions from the global distribution pool.

Emission formula is **quadratic**: `torexShares = (sum of sqrt(stakedAmount(i)))^2` for all stakers `i`. Incentivizes broad participation over whale concentration.

### SUP Rewards

SuperBoring users earn **SUP tokens** through Streaming Programmatic Rewards (SPR) program, proportional to DCA volume on Base or Optimism.

---

## Chain Deployments

| Chain | Status | Notes |
|---|---|---|
| **Base** | Live (primary) | Launched July 2024 |
| **Optimism** | Live | Secondary chain |
| **Arbitrum** | Pending | Bridge proposal submitted May 2025 |
| **Ethereum mainnet** | Token only | BORING token deployed; no DCA functionality |

---

## Key Stats

| Metric | Value |
|---|---|
| Volume processed | $4M+ on Base |
| Daily active users | ~1,000 |
| Money streamed (all SUP Labs apps) | $10M |

---

## Security and Audits

- **Sherlock Contest #360** -- $28,500 USDC prize pool covering TOREX, BORING staking, referrals, fee distribution
- Underlying Superfluid Protocol audits: Halborn, Trail of Bits, PeckShield
- Active Immunefi bug bounty program
- Contracts are **non-custodial** -- do not hold funds themselves; TOREX accumulates in-tokens only temporarily between Liquidity Mover executions
- No known exploits or security incidents

---

## Key Repos

| Repo | Description |
|---|---|
| [averagex-contracts-cloned](https://github.com/superfluid-finance/averagex-contracts-cloned) | Core contracts (Solidity 56.6%, TypeScript 42.2%, MIT) |
| [torex-basic-liquidity-mover](https://github.com/superfluid-finance/torex-basic-liquidity-mover) | Reference Liquidity Mover implementation |
| [automation-subgraphs](https://github.com/superfluid-finance/automation-subgraphs) | Automation subgraphs |

No SuperBoring-specific NPM packages. Depends on `@superfluid-finance/ethereum-contracts`, `@superfluid-finance/sdk-core`, `@superfluid-finance/sdk-redux`.

---

## Key Relationships

| Partner | Relationship |
|---|---|
| **Superfluid Labs** | First-party product; built by the Superfluid team |
| **Uniswap V3** | TWAP oracle for price validation |
| **Sherlock** | Audit provider |
| **Ricochet Exchange** | Spiritual predecessor (Polygon, IDA-based community DCA) |

---

## Ecosystem Context

SuperBoring is Superfluid Labs' reference pattern for building streaming-based exchange protocols. The evolution from Ricochet Exchange (IDA-based, Polygon) to SuperBoring (GDA-based, Base/Optimism) mirrors the protocol's progression toward GDA as the preferred distribution primitive. The TOREX architecture with competitive Liquidity Movers and TWAP oracle validation represents the canonical streaming DEX design.

For detailed TOREX protocol mechanics (discount model, back adjustments, TWAP observer, liquidity mover implementations, Twin TOREX) see `torex.md`.

---

## Timeline

| Date | Event |
|---|---|
| Pre-2024 | Ricochet Exchange operates on Polygon as earlier Superfluid DCA concept |
| Feb 2024 | SuperBoring Twitter account created |
| Jun 28, 2024 | "Introducing SuperBoring & $BORING Airdrop 0" |
| Jul 2, 2024 | $BORING token launched (100M fixed supply) |
| Jul 5, 2024 | Launches on Base with DEGEN, TN100x, HIGHER, BUILD, AERO, ETH markets |
| Oct 2024 | $MFER pair added |
| Nov 2024 | Referral program (5% BORING commission) |
| 2024 | Sherlock audit completed |
| May 2025 | Arbitrum bridge proposal submitted |
