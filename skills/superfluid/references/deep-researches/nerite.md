---
title: Nerite Protocol
date: 2026-03-19
tags: [superfluid, cdp, stablecoin, custom-super-token, pure-super-token, CFA, GDA, arbitrum]
sources:
  - https://www.nerite.org
  - https://docs.nerite.org/docs/user-docs/general
  - https://www.nerite.org/writing/lite-paper
  - https://www.nerite.org/writing/hello-nerite
  - https://www.nerite.org/writing/liquity-v2-differences
  - https://github.com/NeriteOrg/nerite
  - https://github.com/NeriteOrg
  - https://arbiscan.io/token/0x4ecf61a6c2fab8a047ceb3b3b263b401763e9d49
  - https://defillama.com/protocol/nerite
  - https://tokens.superfluid.org/
  - https://app.aragon.org/#/daos/arbitrum/0x108f48e558078c8ef2eb428e0774d7ecd01f6b1d/dashboard
  - https://www.liquity.org/forks
  - https://dune.com/niftyteam/nerite
---

# Nerite Protocol

Decentralized CDP protocol on Arbitrum, friendly fork of Liquity V2 with an exclusive license from Liquity AG. Issues **USND (US Nerite Dollar)**, the first natively streamable, redeemable stablecoin -- a Custom Pure Super Token requiring no wrapping. **8 collateral types, 500 USND minimum debt, immutable core contracts.**

---

## Identity

| Attribute | Value |
|---|---|
| Founder | Joseph Schiarizzi (CupOJoseph) |
| Legal entities | Nifty Chess, Inc. (US); Nerite DAO LLC (Marshall Islands, via MIDAO) |
| Chain | Arbitrum One (exclusively) |
| Funding | 100% self-funded; Arbitrum Foundation grant for audit; "Go Slow" NFT sale for audits |
| Governance | Aragon DAO |
| License | BUSL-1.1 |

The founder is Education Lead at ETH Denver, an Arbitrum DAO delegate, and previously co-founded Nifty Chess / Treasure Chess.

---

## USND -- Custom Pure Super Token

USND (`0x4ecf61a6c2FaB8A047CEB3B3B263B401763e9D49` on Arbitrum) is a **Custom Pure Super Token** -- the deepest possible Superfluid integration level. `getUnderlyingToken()` returns `address(0)` -- no underlying ERC-20 to wrap/unwrap.

### Token Contract Architecture

Inherits from:
- **`CustomSuperTokenBase`** -- 32 storage slots padding for Super Token proxy pattern
- **`UUPSProxy`** -- Superfluid's upgradeable proxy standard
- **`IBoldToken`** (Liquity V2's BoldToken interface) -- custom mint/burn controlled by BorrowerOperations, TroveManager, StabilityPool
- **`ERC20Permit`** (EIP-2612) -- gasless approval signatures

Compiled with Solidity **0.8.24**, Cancun EVM, 5 optimizer runs. Implementation address: `0xb0817050fa28a1577d90d441e95779b96a09D263`. After deployment, ownership is **permanently renounced** -- the token is immutable.

### Supported Superfluid Agreements

- **CFA (Constant Flow Agreement):** 1-to-1 continuous streaming for payroll, subscriptions, grants, vesting
- **GDA (General Distribution Agreement):** 1-to-many distributions via Superfluid Pools

No wrapping required. Users interact via `app.superfluid.org` or programmatically via Superfluid SDK.

### What Superfluid Does and Does Not Power

| Mechanism | Uses Superfluid? |
|---|---|
| USND payments (payroll, grants, subscriptions, vesting) | **Yes** -- CFA/GDA |
| Interest accrual on Trove debt | No |
| Stability Pool yield distribution | No |
| Liquidations | No |
| Redemptions | No |

Superfluid streaming is a feature of the USND token itself for external payment use cases. It does not power internal protocol mechanics.

### Streaming Use Cases

Payroll and salary streaming, grants with linear or quadratic vesting, subscriptions, token vesting schedules, usage-based billing, on-chain annuities, streaming donations via Giveth and Flow State.

---

## Superfluid Ecosystem Rewards

**4.7 million SUP tokens** allocated to Nerite users through SPR Season 2 ("Lock funds into the USND stability pool" campaign, 735 members).

---

## Multi-Branch Architecture

1 CollateralRegistry, 1 BoldToken (USND), and **8 independent collateral branches**, each with its own TroveManager, BorrowerOperations, StabilityPool, SortedTroves, and ActivePool.

### Collateral Types

| Collateral | Unique to Nerite (vs Liquity V2) |
|---|---|
| WETH | No |
| wstETH | No |
| rETH | No |
| rsETH (Kelp DAO) | Yes |
| weETH (EtherFi) | Yes |
| ARB (retains delegation) | Yes |
| COMP (retains delegation) | Yes |
| tBTC (Threshold) | Yes |

Collateral types are **immutable** -- no new ones can ever be added.

### Key Protocol Parameters

| Parameter | Value |
|---|---|
| Maximum LTV | 91% (up to 11x leverage) |
| Minimum debt | 500 USND |
| Liquidation penalty | 5% typical, 10% max |
| Revenue split | 75% Stability Pool, 25% governance-directed PLI |
| Interest model | User-set, non-compounding, simple interest |
| Oracle system | Chainlink (push) + API3 (OEV auctions) |

---

## Token Economics and Governance

| Token | Status | Purpose |
|---|---|---|
| **USND** | Live | Over-collateralized stablecoin, Super Token |
| **NERI** | Not yet launched (Mar 2026) | Governance: direct PLI, update debt limits, delegate ARB |
| **Shell Points** | Live | On-chain loyalty tokens, 1M distributed daily |

NERI governance scope is limited by design. NERI stakers can only: direct Protocol Liquidity Incentives, update collateral debt limits, delegate ARB. Cannot: change fee splits, update protocol parameters, mint stablecoins, or control user CDPs.

---

## Key Stats

| Metric | Value |
|---|---|
| TVL | ~$2.6M (peaked ~$7M) |
| USND total supply | ~1.3M |
| USND holders | ~503 |
| Annualized fees | ~$40K |

---

## Key Contract Addresses (Arbitrum)

| Contract | Address |
|---|---|
| USND (BoldToken / Super Token) | `0x4ecf61a6c2FaB8A047CEB3B3B263B401763e9D49` |
| USND Implementation | `0xb0817050fa28a1577d90d441e95779b96a09D263` |
| Nerite DAO (Aragon) | `0x108f48e558078c8ef2eb428e0774d7ecd01f6b1d` |

Per-branch addresses (TroveManager, BorrowerOperations, StabilityPool, etc.) discoverable on-chain via `collateralRegistryAddress` on the USND contract.

---

## Key Relationships

| Partner | Relationship |
|---|---|
| **Superfluid** | Native USND streaming (Custom Super Token); SPR S2 (4.7M SUP) |
| **Liquity AG** | Exclusive V2 code license for Arbitrum |
| **API3** | OEV oracle infrastructure |
| **Aragon** | DAO governance framework |
| **Yearn Finance** | yUSND vault (automates Stability Pool yield) |
| **Spectra** | yUSND yield trading |
| **Balancer** | USND-USDC boosted pool |
| **Camelot** | USND LP pools |
| **Sherlock** | Security audit and ongoing monitoring |
| **Threshold Network** | tBTC collateral support |

---

## Key Repos

| Repo | Description |
|---|---|
| [nerite](https://github.com/NeriteOrg/nerite) | Main repo (Liquity V2 fork, BUSL-1.1) |
| [nerite-gov](https://github.com/NeriteOrg/nerite-gov) | Governance contracts |
| [nerite-starter-repo](https://github.com/NeriteOrg/nerite-starter-repo) | TypeScript starter |
| [shell-points](https://github.com/NeriteOrg/shell-points) | Shell Points contracts |
| [api.nerite.org](https://github.com/NeriteOrg/api.nerite.org) | API server |

No Nerite-specific NPM packages. Standard Superfluid SDK used for programmatic USND streaming.

---

## Notable Incidents

- **February 2025:** Liquity V2 Stability Pool vulnerability disclosed (shared codebase). Users urged to close positions. No funds lost. Liquity V2 redeployed May 19, 2025.
- **September 2025:** yUSND vault suffered 5.2% drawdown (~$25K) from insufficient liquidity during rETH liquidation reward swaps. Yearn fully covered losses by October 11, 2025.
- **No known Nerite-specific exploits.** Core contracts are immutable.
