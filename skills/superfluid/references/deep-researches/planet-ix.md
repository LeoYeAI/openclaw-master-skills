---
title: Planet IX
date: 2026-03-19
tags: [superfluid, gamefi, CFA, super-app, custom-super-token, polygon]
sources:
  - https://superfluid.org/post/leading-nft-game-planet-ix-integrates-superfluid-to-power-premium-currencies
  - https://superfluid.org/post/case-study-how-planetix-is-scaling-their-in-game-payments-with-superfluid
  - https://github.com/ngmachado/Superfluid-PlanetIX
  - https://www.globenewswire.com/news-release/2023/02/02/2600284/0/en/Planet-IX-Expands-Virtual-Economy-With-Premium-Superfluid-Powered-Tokens-in-Tile-Expansion.html
  - https://planetix.gitbook.io/whitepaper/
  - https://gamebook.planetix.com/
  - https://polygonscan.com/token/0xfac83774854237b6e31c4b051b91015e403956d3
  - https://basescan.org/token/0x920e753d8d7d5b598063c89b6f06288803448d06
  - https://ix.foundation/
  - https://www.coingecko.com/en/coins/planet-ix
---

# Planet IX

NFT-based GameFi strategy game built by Nibiru Software AB (Sweden). Superfluid Protocol's first GameFi integration, launched February 2023 on Polygon. Models Earth's surface as 1.6 billion hexagonal land-plot NFTs (PIX). **550K+ cumulative players, 50K+ streaming wallets, 30K+ peak concurrent streamers.**

---

## Identity

| Attribute | Value |
|---|---|
| Developer | Nibiru Software AB (Swedish Aktiebolag) |
| HQ | Strandvägen 1, 114 51 Stockholm, Sweden |
| Founder & CSO | Felix Bengtsson |
| Co-Founders | Christopher Jeansson, Felipe Dunley |
| CEO | Karl Blomsterwall |
| CPO | Lukas Alexandersson |
| Launch | November 2021 (Polygon); Season 2 on Base (2026) |
| Chains | Polygon (Season 1), Base (Season 2) |
| Funding | Self-funded via community token sales; one institutional investor (Zuko) |

---

## Products

### Core Game

Planet IX models Earth as **1.6 billion hexagonal land-plot NFTs (PIX)** on Polygon. Players acquire, merge into territories (Area, Sector, Zone, Domain), stake for token rewards, and manage resource production through Mission Control. In-game corporations (Gravity Grade, Lucky Cat, NetEmpire, NewLands, Global Waste System, EternaLabs, HaveBlue) act as game subsystems.

### Mission Control

Central hub with expandable tile grid. Players place PIX, drones, and facilities on tiles to farm Waste, convert to Energy, and stake for IXT rewards. Tile expansion uses Superfluid streaming rental payments (Contract Tiles in rings A, B, C, D).

### Season 2 (Base, 2026)

Migration from Polygon to Base via Chainlink CCIP. Introduces AIX token (306M supply, replaces IXT), Meteora Credits, Artificial Core NFTs, Mining Pass system (lock AIX to mine Meta Crystals), and AI-enhanced gameplay.

---

## Superfluid Integration

### Overview

Launched **February 2, 2023** with the "Tile Expansion" update. Built by **Nuno Machado** (`ngmachado`), a Web3 Engineer at Superfluid, in approximately two months from concept to deployment. This was Superfluid's **first GameFi integration**.

### Agreement Type

Exclusively **CFA (Constant Flow Agreement)**. No IDA or GDA usage. Flow direction is **many-to-one**: players stream tokens toward Planet IX as continuous subscription payments for renting in-game tiles.

### Custom Super Tokens: AGOLD and ALITE

Planet IX deployed **two custom native Super Tokens** rather than wrapping IXT. This avoided wrap/unwrap friction.

| Token | Contract (Polygon) | Acquisition | Convertible to IXT? |
|---|---|---|---|
| **Astro Gold (AGOLD)** | `0xfac83774854237b6e31c4b051b91015e403956d3` | Swap IXT 1:1 via Astro Cap | Yes (bidirectional) |
| **Astro Gold Lite (ALITE)** | `0x9308A7116106269eB11834dF494eFd00d244cF8e` | Prizes, airdrops, drops | No (one-way) |

AGOLD uses UUPSProxy pattern. ALITE uses custom `GoldLiteProxy` with trusted minter. Both function identically for tile rental streaming. ~1.77M AGOLD in circulation across ~12,179 holders.

### MissionControlStream SuperApp

| Component | Detail |
|---|---|
| **Contract** | `0xb9d70840cca6e6f71d3c884060ee123e13b4c27d` |
| **Pattern** | Transparent Proxy (EIP-1967), upgradeable |
| **Source** | [github.com/ngmachado/Superfluid-PlanetIX](https://github.com/ngmachado/Superfluid-PlanetIX) |
| **License** | GPL-2.0 |

Registered Superfluid SuperApp implementing three CFA callbacks:

- **`afterAgreementCreated`** -- player opens stream, contract registers rented tiles via `IMissionControl`
- **`afterAgreementUpdated`** -- player modifies flow rate, updates tile allocation
- **`afterAgreementTerminated`** -- stream ends, deletes rented tiles from Mission Control

Accepts both AGOLD and ALITE. Includes approve/funds-controller mechanism for authorized token movement.

### Streaming Payment Flow

1. Player acquires AGOLD (swap IXT 1:1 via Astro Cap) or receives ALITE from airdrops/drops
2. Player opens CFA stream to MissionControlStream SuperApp
3. `afterAgreementCreated` callback fires, registering rented tiles
4. Stream flows continuously at **1 AGOLD/ALITE per Contract Tile per month**
5. Player can close stream anytime (single transaction), triggering `afterAgreementTerminated`
6. Funds accumulate in Planet IX wallet automatically -- no claiming transaction needed

Streaming also integrated into the **affiliate program**: commission from AGOLD tile-rental streams flows to a player's "Parent Wallet Address."

### Scale

| Metric | Value |
|---|---|
| Unique streaming wallets | **50,000+** |
| Total tokens streamed | **6M+ IXT equivalent** (in AGOLD) |
| Peak concurrent streamers | **30,000+** |
| Streams opened in first 8 hours | **1,000+** |
| Development timeline | ~2 months concept-to-deployment |

### Current Status

**Uncertain** following migration to Base. AGOLD on Polygon still holds ~1.77M tokens across ~12K holders, but GitHub repo last updated March 2023. No public evidence the streaming integration was migrated to Base or formally deprecated.

---

## Token Economics

### IXT (Polygon, Season 1)

| Property | Value |
|---|---|
| Contract | `0xE06Bd4F5aAc8D0aA337D13eC88dB6defC6eAEefE` |
| Total supply | 153,258,228 IXT |
| Holders | ~231,554 |
| Launch | November 20, 2021 |
| Vesting | 4-year schedule |

Distribution: 17.94% Play-to-Earn, 19.90% Retroactive Airdrop, 15.66% Staking Pool, 15.89% Community/Liquidity, 16.70% Founders/Employees, 8.35% Investors/Advisors, 5.55% Ecosystem.

### AIX (Base, Season 2)

| Property | Value |
|---|---|
| Contract | `0x920e753d8d7d5b598063c89b6f06288803448d06` |
| Max supply | 306,000,000 AIX |
| Migration | IXT to AIX 1:1 via Chainlink CCIP |
| Price (approx. Mar 2026) | ~$0.14, market cap ~$27M |

### Staking

- Single IXT/AIX staking for token rewards
- Territory NFT staking (larger territories = higher rewards)
- Energy staking (Energy NFTs + IXT in 1:1 ratio)
- LP mining pools
- Mining Pass (Season 2, lock AIX for Meta Crystals)
- At peak, **60-70%** of circulating IXT staked; **$14.64M** worth of IXT rewarded to players

---

## Key Contract Addresses (Polygon)

| Contract | Address |
|---|---|
| IXT Token | `0xE06Bd4F5aAc8D0aA337D13eC88dB6defC6eAEefE` |
| PIX Land NFT | `0xB2435253C71FcA27bE41206EB2793E44e1Df6b6D` |
| PIX-A Game Assets | `0xbA6666B118F8303F990f3519DF07e160227CCe87` |
| AGOLD (Super Token) | `0xfac83774854237b6e31c4b051b91015e403956d3` |
| ALITE (Super Token) | `0x9308A7116106269eB11834dF494eFd00d244cF8e` |
| MissionControlStream | `0xb9d70840cca6e6f71d3c884060ee123e13b4c27d` |

---

## Key Stats

| Metric | Value |
|---|---|
| Cumulative unique players | 550,000+ |
| Connected wallets | 260,000+ |
| Peak monthly active wallets | 100,000+ (2023) |
| Total NFTs sold | 400M+ |
| IXT rewarded to players | $14.64M worth |

---

## Key Relationships

| Partner | Relationship |
|---|---|
| **Superfluid** | First GameFi integration; CFA streaming for tile rentals |
| **Chainlink** | BUILD program member; VRF, Automation, CCIP for IXT-to-AIX migration |
| **Polygon** | Original chain; largest game by transactions Q1 2022 |
| **Coinbase / Base** | Season 2 chain |
| **QuickSwap** | DEX partner |

---

## Key Repos

| Repo | Description |
|---|---|
| [Superfluid-PlanetIX](https://github.com/ngmachado/Superfluid-PlanetIX) | MissionControlStream SuperApp contracts (Solidity, GPL-2.0) |

No public GitHub organization for Nibiru Software's core game contracts. No NPM packages associated with Planet IX.

---

## Notable Incidents

- **Polygon network congestion (late 2022/early 2023):** Mission Control launch generated enough transaction volume to measurably slow the Polygon network
- **Crowd1 association (2021):** Planet IX introduced at Crowd1 event; Nibiru has since distanced from Crowd1 and built independent partnerships
- **No known smart contract exploits**
