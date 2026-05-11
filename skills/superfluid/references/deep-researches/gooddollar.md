---
title: GoodDollar Protocol
date: 2026-03-10
tags: [gooddollar, ubi, pure-super-token, celo, reserve, bonding-curve, governance]
sources:
  - https://www.gooddollar.org/
  - https://docs.gooddollar.org/
  - https://whitepaper.gooddollar.org/
  - https://discourse.gooddollar.org/
  - https://github.com/GoodDollar
  - https://medium.com/gooddollar
  - https://forum.celo.org/
  - https://celoscan.io/
  - https://www.goodlabsfoundation.org/
---

# GoodDollar Protocol

Permissionless, non-profit protocol minting and distributing free crypto UBI via G$. Reserve-backed bonding curve generates yield from DeFi-staked assets, converts to G$ distributed daily to verified claimers. **710K+ members, 181+ countries, 3.4B+ G$ distributed.** Founded by eToro CEO Yoni Assia (2018), launched September 2020.

---

## Identity

| Attribute | Value |
|---|---|
| Founded | 2018 (concept: November 2008 whitepaper) |
| Launch | September 7, 2020 (V1) |
| Founder | Yoni Assia (Chairman; CEO of eToro) |
| Executive Director | Anna Stone |
| Tech Lead | Hadar Rottenberg ("sirpy") |
| Legal entities | Good Dollar Ltd. (Cayman Islands), Good Labs Foundation |
| Initial funding | $1M from eToro (2018) |
| Chains | Ethereum, Celo (primary), Fuse, XDC |
| Token model | Zero founder allocation, no pre-mint, no TGE |

---

## G$ Token

### Cross-chain deployments

| Chain | Address | Decimals | Standard | Streaming |
|---|---|---|---|---|
| Ethereum | `0x67C5870b4A41D4Ebef24d2456547A03F1f3e094B` | **2** | ERC-20 + ERC-677 | No |
| Fuse | `0x495d133B938596C9984d462F007B676bDc57eCEC` | **2** | ERC-20 + ERC-677 | No |
| Celo | `0x62B8B11039FcfE5aB0C56E502b1C372A3d2a9c7A` | **18** | ERC-20/677/777 + **SuperToken** | **Yes** |
| XDC | `0xEC2136843a983885AebF2feB3931F73A8eBEe50c` | — | ERC-20 | No |

### Supply

- Max cap: **2.2 trillion G$**
- Inflationary via expansion rate: **15% annual reserve ratio decline** (V3+)
- Minted only via GoodReserve; burned on sell-back
- Price: augmented bonding curve (modified Bancor V1 formula)
- Approx. price: ~$0.0001107 (March 2026)

### Bridging

- Unified bridge: `0xa3247276dbcc76dd7705273f766eb3e8a5ecf4a5` (same address all chains)
- Protocols: Axelar + LayerZero (GIP-15, July 2023)
- V4 reversed direction — Celo is primary G$ source

---

## G$ as Pure Super Token on Celo

**Contract:** `SuperGoodDollar.sol` (UUPS proxy)
**Implementation:** `0x880c4641702d5e12d6a881bb6d8fc425e98cb398`

`getUnderlyingToken()` returns `address(0)` — no underlying ERC-20 to wrap/unwrap.

### Dual proxy architecture

`GoodDollarProxy` dispatches calls to **two logic contracts** via delegatecall:
1. Canonical Superfluid SuperToken logic (upgradeable by Superfluid governance)
2. GoodDollarCustom logic (upgradeable by GoodDollar governance)

Renamed UUPS methods avoid naming clashes between upgrade paths.

### Key state

- `feeRecipient`, `formula` (IFeesFormula), `identity` (IIdentity), `cap`, `disableHostOperations`
- Roles: `MINTER_ROLE`, `PAUSER_ROLE`, `DEFAULT_ADMIN_ROLE`
- `_processFees` applies on each streamed drip — receiver gets `flowRate – feeRate`

### Ecosystem use of streaming

- UBI distribution itself is **daily epoch claim**, not streaming
- Streaming powers: GoodCollective recurring donations, P2P payments, payroll, ecosystem dApps

### Audit

- Sayfer, January 2023 (5 findings, none critical)

---

## UBI Distribution

### Daily claim mechanics

- 24-hour epoch; pool of newly minted G$ divided equally among active claimers
- Amount per claimer = daily pool / avg active claimers over past **14 days**
- Unclaimed G$ rolls to next day

### Distribution split

| Allocation | % |
|---|---|
| UBI to claimers | 80% |
| Community Fund (GoodDAO treasury) | 10% |
| G$ Savings (yield for G$ lockers) | 10% |

### Identity / Sybil resistance

- FaceTec ZoOm 3D verification, iBeta/NIST Level 1 & 2 (ISO 30107-3)
- FAR: **1/4.2 million** at <1% FRR
- Facial hash stored anonymously — no link to profile/address
- Periodic re-verification required

### Fishing mechanism

- Users inactive 14+ days can be "fished" by anyone calling `fish(address)` on UBIScheme
- Fisherman receives reward = daily UBI amount

---

## Reserve & Yield

### GoodReserve (Ethereum mainnet)

- AMM minting/burning G$ via **modified Bancor V1 bonding curve**
- Reserve asset: cDAI (Compound)
- Reserve ratio (late 2023): **55.39%**
- Exit contribution: 3% (waived with G$X tokens)

### Yield flow

1. Supporters deposit DAI/USDC → GoodStaking contracts
2. Routed to Compound (DAI→cDAI) and Aave (USDC→aUSDC)
3. GoodFundManager collects interest (permissionless)
4. Interest → GoodReserve → mints G$ (without changing price)
5. Split: staker rewards + bridged to Fuse/Celo for UBI

### Staking contracts (V3, Ethereum)

| Contract | Address | Protocol | Reward |
|---|---|---|---|
| GoodCompoundStaking | `0x7b7246c78e2f900d17646ff0cb2ec47d6ba10754` | Compound | ~138.88 G$/block |
| GoodAaveStaking | `0x3ff2d8eb2573819a9ef7167d2ba6fd6d31b17f4f` | Aave | ~69.44 G$/block |

### G$X tokens

- Earned 1:1 buying G$ from Reserve; burned 1:1 selling
- Waives exit contribution if sufficient balance held

---

## GoodDAO Governance

**GOOD is non-transferable** — cannot be bought/sold, zero market value. 1 GOOD = 1 vote.

| Parameter | Value |
|---|---|
| Initial distribution | 96M GOOD to ~248K addresses |
| Annual proposed mint | 96M GOOD |
| Proposal threshold | 0.25% |
| Quorum | 3% |
| Voting period | 14 days |
| Decay | Inactive voting power halved yearly |
| Model | Compound governance contracts |

### Distribution

- 50% claimers (proportional to G$ claimed)
- 25% supporters (proportional to $ staked)
- 25% G$ holders (proportional to G$ held)

### Guardian

- Foundation retained veto rights (cannot propose, only block harmful proposals)
- Originally set to expire January 1, 2023

### Governance channels

- Discourse: discourse.gooddollar.org
- Snapshot: thegooddao.eth
- Notable GIPs: 0 (framework), 11 (V3), 13 (Celo), 15 (bridges), 19 (voting), 24 (V4), 25 (XDC)

---

## Protocol Versions

| Version | Date | Key Changes |
|---|---|---|
| V1 | Sep 2020 | Ethereum + Fuse, DAI/cDAI via Compound |
| V2 | Jan 2022 | Compound + Aave, direct Reserve buy/sell, GoodDAO + GOOD, G$X, 20% expansion |
| V3 | Nov 2022 | 15% expansion, eliminated staking APY, 10% Community Fund + Savings, Celo (Mar 2023) |
| V4 | Mar 2025 | Celo-primary Reserve via Mento, post-exploit recovery, bridge reversal, exit fees (10%, min 5%) |
| XDC | Oct 2025 | Dual-reserve (Celo + XDC), native XDC minting, $900K grant |

### December 2023 exploit

- 627,328 cDAI drained from GoodReserve
- 14B G$ minted (supply inflated 6B → 20B; 9B frozen)
- Reserve paused, minting disabled until V4

---

## Key Stats

| Metric | Value | ~Date |
|---|---|---|
| G$ price | ~$0.0001107 | Mar 2026 |
| Total members | **712K+** | Mar 2024 |
| Monthly active users (peak) | **114,300** | Mar 2024 |
| Daily claimers | ~**50,000** | Ongoing |
| Total G$ distributed | **3.4B** | Mar 2024 |
| Countries | 181+ | 2024 |
| P2P transactions | 2M+ total | Feb 2024 |
| Top countries | Indonesia, Bangladesh, Nigeria, Vietnam, India, Brazil | |

---

## GoodCollective

Open-source smart contracts + dApp on Celo for segmented UBI and direct digital payments. Built by GoodLabs + Appropriate Design. Funded by Climate Collective grant.

### Pool types

1. **Segmented Basic Income** — distribute by demographics (age, gender, location) via GoodID
2. **Results-Based Financing** — payment triggered by verified action (NFT minted → smart contract pays)
3. **Community Funds** — admin adds recipients directly

Donations: one-time or **streaming via Superfluid**.

### Pilots

| Pilot | Location | Partners | Results |
|---|---|---|---|
| Waste upcycling (Feb 2023) | Coroadinho, Brazil | Neduc, DeTrash | 48 women, 2,000 kg recycled, $700 paid |
| Tree cultivation | Kakamega Forest, Kenya | Silvi | 39 onboarded, ~70K trees, 16 sites |
| Red Tent (Nov 2024) | Nigeria + Colombia | — | 1,000 women target, first GoodOffers pilot |

---

## GoodOffers & GoodID

Segmented basic income using **GoodID** (decentralized identity). Amazon Rekognition for age + gender prediction, IP/phone for location. Opt-in required. Users can claim from multiple pools with same verified wallet.

---

## Ecosystem Integrations

- **GoodCollective** — segmented UBI & direct digital payments (Superfluid streaming)
- **HaloFi** — gamified G$ savings challenges
- **Fonbnk** — buy/sell mobile airtime with G$
- **Uniswap on Celo**, **Voltage Finance on Fuse** — DEX swaps
- **Opera MiniPay**, **Valora** — wallet integrations
- **impactMarket** — micro-credit
- **Kotani Pay** — cash-in/cash-out

---

## Key Partnerships

| Partner | Relationship |
|---|---|
| **eToro** | Founding sponsor, $1M seed, $1M staked |
| **Celo Foundation** | 500K cUSD grant; GoodDollar = 67% Celo DAU (Q3 2023) |
| **Mento Labs** | V4 Reserve (G$/cUSD exchange) |
| **Superfluid** | Pure SuperToken, SPR S1 (1.3M SUP), Wave Pool co-sponsor |
| **Flow State** | GoodBuilders S3 streaming grants |
| **FaceTec** | Biometric verification |

---

## GoodBuilders Program

$250K ecosystem fund (announced March 2025). Three Gitcoin Grants rounds + $20K mentor rewards per round. Season 3 uses Flow State streaming for continuous Superfluid-powered funding.

---

## Technical Architecture

### Core contracts

- Ethereum: Reserve, staking, FundManager
- Fuse + Celo: UBIScheme, Identity, FirstClaimPool
- All chains: DAO + token contracts
- Pattern: UUPS upgradeable proxy (EIP-1967), Solidity 0.8.16

### Key repos

| Repo | Description |
|---|---|
| [GoodDAPP](https://github.com/GoodDollar/GoodDAPP) | Wallet (React Native Web) |
| [GoodProtocol](https://github.com/GoodDollar/GoodProtocol) | V2+ smart contracts |
| [GoodCollective](https://github.com/GoodDollar/GoodCollective) | Segmented UBI / direct payments |
| [GoodServer](https://github.com/GoodDollar/GoodServer) | Backend API |
| [GoodBootstrap](https://github.com/GoodDollar/GoodBootstrap) | Dev environment |

### SDKs

- NPM: `@gooddollar/web3sdk-v2`, `@gooddollar/goodprotocol`, `@gooddollar/goodlogin-sdk`, `@goodsdks/citizen-sdk`
- G$ Streaming: standard Superfluid SDK (Pure SuperToken, no wrap/unwrap needed)
- Docs: [docs.gooddollar.org](https://docs.gooddollar.org/)
