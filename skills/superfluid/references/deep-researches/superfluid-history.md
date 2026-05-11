---
title: Superfluid Protocol History
date: 2026-03-09
tags: [superfluid, history, architecture, security, tokenomics, ecosystem]
sources:
  - https://www.theblock.co/post/278615/ethereum-token-streaming-protocol-superfluid-strategic-funding
  - https://medium.com/superfluid-blog
  - https://rekt.news/superfluid-rekt
  - https://www.halborn.com/blog/post/explained-the-superfluid-hack-february-2022
  - https://defillama.com/protocol/superfluid
  - https://www.coingecko.com/en/coins/superfluid
  - https://icodrops.com/superfluid/
  - https://blog.1inch.io/defi-visions-francesco-renzi/
  - https://theaccountantquits.com/episode-31-michele-daliessi-from-superfluid-on-streaming-payments/
---

# Superfluid Protocol

Real-time token streaming protocol. ERC-20 extension ("Super Tokens") enabling continuous per-second value transfer without repeated transactions.

## Origin

- **Precursor**: rDAI — programmable interest redirection on Compound (interest from cDAI streamed to another wallet). Built by Francesco Renzi and Miao ZhiCheng at Berlin Blockchain Week hackathon (~2019).
- **Vision convergence**: rDAI → real-time finance rail connecting accounts with instantaneous formula-based balance updates.
- **Related prior art**: EIP-2100 (Streaming Token Standard).
- **Bear market founding**: Co-founders quit day jobs mid bear market.

## Founding Team

| Name | Role | Background |
|---|---|---|
| Francesco George Renzi | CEO, Co-founder | decentral.ee (Tallinn), CRIP.TO OÜ. Based in Estonia. |
| ZhiCheng (Miao) Miao | CTO, Co-founder | Principal Architect. Superfluid Security Council. |
| Michele D'Aliessi | COO, Co-founder | Tokenomics, crypto networks analysis since 2015. Previously MakrShakr. |

Team: ~18 people, primarily engineers (as of Feb 2024).

## Corporate Structure

- **Superfluid Finance** (`superfluid-finance` on GitHub): Original development entity. Estonia-linked. Builds and maintains the protocol monorepo, dashboard, automation contracts, and peripheral tooling.
- **Superfluid Foundation** (`superfluid-org` on GitHub): Cayman Islands foundation company. Long-term protocol stewardship, governance facilitation. Adopted SUP token Feb 2025. Manages protocol monorepo, SDK, and skills.
- **Superfluid Labs** (`@superfluid_labs`, [suplabs.org](https://www.suplabs.org/)): Independent product studio. Consumer apps on top of the protocol.

## Funding

| Date | Round | Amount | Lead/Notable Investors |
|---|---|---|---|
| Jul 2021 | Seed | $9M | Multicoin Capital, Delphi Digital, DeFiance Capital, Fabric Ventures, Metacartel Ventures, The LAO, White Star Capital, Taavet Hinrikus, Sten Tamkivi, Ryan Selkis, Anthony Sassano |
| Late 2023 (announced Feb 2024) | Strategic | $5.1M | Fabric Ventures (lead), Multicoin Capital, Circle Ventures, Safe Foundation, The LAO, Taavet+Sten |
| Aug 2025 | Public token sale | $2M | — |
| **Total** | | **~$16.1M** | |

Structure: equity with token warrants (seed and strategic).

## Protocol Architecture

### Core Concept: "Fat Token"

Super Tokens extend ERC-20 with agreement logic baked into the token itself. All inflows/outflows netted in real-time per block. No capital locked. Balance = `f(time)` — calculated on read, not written per second.

### Agreement Classes (Primitives)

| Agreement | Type | Description |
|---|---|---|
| **CFA** (Constant Flow Agreement) | 1-to-1 streaming | Sender→Receiver at constant flow rate (tokens/second). Either party can cancel. |
| **IDA** (Instant Distribution Agreement) | 1-to-many instant | Publisher distributes to N subscribers proportional to units. **Deprecated** — superseded by GDA. |
| **GDA** (General Distribution Agreement) | 1-to-many streaming+instant | Pools with proportional unit-based distribution. Supports both instant and flow distributions. Pool is an ERC-20 contract (units = balance). |

### Key Contracts

- **Host** (`Superfluid.sol`): Orchestrates composable agreement calls in single tx. Manages serialized context (`ctx`).
- **Super Token**: ERC-20 + streaming/distribution capabilities. Types: Wrapper (wrap existing ERC-20), Native Asset (ETH/MATIC), Pure (no underlying).
- **Forwarders** (immutable, same address all chains): `CFAv1Forwarder`, `GDAv1Forwarder` — simplified off-chain interaction points. Recommended over direct Host calls.
- **Super App Framework**: Contracts that react to agreement callbacks (stream created/updated/deleted).
- **TOGA**: Manages liquidation incentives.
- **Automation**: VestingScheduler, FlowScheduler.
- **MacroForwarder / EIP712MacroBase**: Gasless meta-transaction system for relayed operations (EIP-712 Clear Signing).
- **SuperfluidPool**: Created via GDA. ERC-20 where units = balance. Admin manages units, anyone can distribute (if allowed). 256 pool connections per account per token limit.

### Semantic Money Library

GDA built on formal mathematical foundation (denotational semantics). `TokenMonad` abstract contract + `SemanticMoney` library for provably correct payment semantics. ([Miao's blog — GDA math](https://miaozc.me/2022-08-18-superfluid-gda.html))

## SDK Generations

| Generation | Package | Status | Notes |
|---|---|---|---|
| Gen 1 | `@superfluid-finance/js-sdk` | Deprecated | Truffle/Web3.js based. `sf.user` abstraction. |
| Gen 2 | `@superfluid-finance/sdk-core` | Legacy | Framework-agnostic. ethers.js. `Framework.create()` pattern. |
| Gen 2+ | `@superfluid-finance/sdk-redux` | Legacy | React state management, caching, hooks. |
| Gen 3 | `@sfpro/sdk` | Current | viem/wagmi native. Type-safe. Subpaths: `/abi`, `/action`, `/hook`, `/util`. |

## Network Deployments

| Network | Approx. Date | Notes |
|---|---|---|
| Polygon | 2021 (launch) | First production network. Highest early usage. |
| Gnosis Chain (xDAI) | 2021 | |
| Arbitrum | ~2021–2022 | |
| Optimism | Mar 2022 | |
| Avalanche | ~2021–2022 | |
| BNB Smart Chain | ~2021–2022 | |
| Celo | ~2022 | |
| Base | Jul 2023 | SUP token primary chain. |
| Ethereum Mainnet | Feb 2023 (early access) | ENS first user (Public Goods Scholarships). |
| Scroll | ~2024 | |
| Degen Chain | ~2024 | |

Supported testnets: Sepolia, Base Sepolia, Scroll Sepolia, Optimism Sepolia, Avalanche Fuji.

## Security

### Feb 8, 2022 Exploit

- **Chain**: Polygon only.
- **Loss**: ~$8.7M drained; some sources report up to $13–20M in token value.
- **Vulnerability**: Serialized context (`ctx`) injection in Host contract. Attacker crafted fake `ctx` with spoofed `msg.sender` via `callAgreement`. Trusted Host contract did not validate `ctx` from calldata — only external callers were checked via `isCtxValid`.
- **Technique**: Used IDA to create distribution indexes spoofing accounts holding Super Tokens on Polygon.
- **Affected projects**: QiDao (QI −65%), Stacker Ventures (STACK), Stake DAO (SDT), Museum of Crypto Art (MOCA).
- **Stolen assets**: 11K MATIC, 1.5M MOCA, 28 ETH, 39K sdam3CRV, 19.4M QI, 44.6K SDT, 23.7K STACK, 563K USDC.
- **Response**: Patch deployed same day (~3:40pm UTC). Protocol upgrade temporarily blocked all agreement invocations. $1M bounty offered. Most affected accounts refunded.
- **Attacker funds**: Sourced from Tornado Cash. Remained in attacker wallet (2,700+ ETH).

### Post-Exploit Security

- **Bug Bounty**: Immunefi program launched Feb 15, 2022. Up to $200K bounties.
- **Audits**: Halborn (June 2022, no vulnerabilities found), additional third-party audits.
- **Tooling**: Trail of Bits tools for fuzzing & static analysis, GitHub Actions CI, Foundry tests.

## SUP Token

| Property | Value |
|---|---|
| Launch date | Feb 19, 2025 |
| Chain | Base |
| Total supply | 1,000,000,000 (1B) |
| Community | 60% |
| DAO Treasury + Foundation | 35% |
| Development team | 25% (3-year lockup stream, 1-year cliff) |
| Early backers/investors | 15% (3-year lockup stream, 1-year cliff) |
| Early supporters | 5% |
| Inflation | Determined by DAO |
| Initial transferability | Non-transferable at launch |
| TGE (transferable) | Nov 22, 2025 |
| Circulating | ~240M SUP |
| Exchanges | Coinbase Exchange, Uniswap V3 (Base), MEXC |
| Claim portal | claim.superfluid.org |

### Streaming Programmatic Rewards (SPR)

Distribution mechanism for SUP. Combines points-system flexibility with continuous streamed payouts. Season 1 began Feb 19, 2025. 50M SUP (5% of supply) allocated for Season 1. At least 2 years of distribution planned. Recipients choose time preference via "Reserves" — longer lock = bigger bonus (up to 12 months).

SPR Season 1 campaigns: AlfaFrens, SuperBoring, GoodDollar, Giveth/Octant/flows.wtf, Flowstate, Community Activations, salary/rewards stream recipients.

## Superfluid Labs Products

Independent product studio ([suplabs.org](https://www.suplabs.org/)). GitHub org: `superfluid-finance`. Internal codenames: `friendX` (AlfaFrens), `averageX` (SuperBoring).

- **AlfaFrens** (shut down Aug 2025): SocialFi subscription app on Farcaster/Base. Per-second streamed DEGEN payments, ERC-4337 smart accounts. Peak: 89% of UserOps on Base (May 2024).
- **SuperBoring** ([app.superboring.xyz](https://app.superboring.xyz/en)): Streaming DCA DEX on Base/Optimism. TOREX engine for continuous swaps. $BORING token earned while DCA'ing. Included in SPR Season 1.
- **Other**: Banger (viral post betting), Labs NFT (mystery card game with streamed cashback).

## Developer Programs

Superfluid sponsored multiple ETHGlobal hackathons (HackMoney 2021/2022, NFT Hack, Scaling Ethereum, ETHOnline, ETHMexico) with pool prizes distributed to all Superfluid projects. Wave Pool (Sep 2022) ran as a continuous hackathon with monthly prizes. Builder Grants targeted specific chain deployments. Superfluid Reactor served as an accelerator program.

## Key Integrations & Users

- **Optimism Foundation**: RPGF3 & RPGF4 grant distribution (30M OP tokens, ~$110M).
- **ENS DAO**: Public Goods Scholarships (first Ethereum mainnet user, Feb 2023). Later: $5.4M developer grants to 9 teams over 1.5 years via open-ended streams + forwarding to Safe multisig.
- **Gitcoin Allo Protocol**: Streaming Quadratic Funding (SQF).
- **MakerDAO**: Salary streaming (since late 2021).
- **The Graph**: Subgraph support for indexing streams.
- **Safe (Gnosis Safe)**: Native integration as Safe App.

## Ecosystem Projects (Selection)

- **Ricochet Exchange**: DCA via streaming into DeFi strategies. Predecessor to SuperBoring.
- **Flowstate**: Streaming Quadratic Funding platform. SPR Season 1 partner.
- **GoodDollar**: Non-profit streaming UBI protocol. SPR Season 1 partner.
- **AdLands**: Farcaster ad space rental via streams.
- **MadFi**: Lens Protocol creator subscriptions.
- **ChannelX**: Subscription-gated Farcaster channels.
- **Geoweb + Gitcoin**: Streaming Quadratic Funding.

## Protocol Stats (Approximate)

| Metric | Value | Date |
|---|---|---|
| Total value streamed | >$1B | ~2025 |
| Wallets | >1M | ~2025 |
| MAUs | ~90K | ~2025 |
| Projects built | 850+ | Mid 2024 |
| Daily streaming volume | ~$1.6M/day | Feb 2024 |
| Base streams | 577,985 | May 2024 |
| Optimism streams | 31,769 | May 2024 |

## V2 Development

- **ZK-powered solvency**: Partnership with Boundless (formerly RISC Zero) exploring Steel ZK coprocessor for offchain solvency proofs, reducing onchain gas for stream liquidation checks.
- **Streams are perpetual and not fully collateralized** (like credit cards) — solvency enforcement is a core V2 challenge.
- **V2 funding**: Subject to DAO vote.

## Timeline Summary

| Date | Event |
|---|---|
| ~2019 | rDAI project at Berlin Blockchain Week (Renzi + Miao) |
| 2019 | Superfluid founded, bear market. Co-founders quit jobs. |
| 2021 | Protocol V1 launched. First deployments: Polygon, Gnosis Chain. |
| Jul 2021 | $9M seed round |
| Late 2021 | MakerDAO begins salary streaming. |
| Feb 8, 2022 | Polygon exploit ($8.7M). Patch same day. |
| Feb 15, 2022 | Immunefi bug bounty launched |
| Mar 2022 | Live on Optimism |
| Jun 2022 | Halborn audit completed (no vulnerabilities) |
| Sep 2022 | Wave Pool continuous hackathon launched |
| Feb 2023 | Ethereum Mainnet early access (ENS first user) |
| Jul 2023 | Live on Base |
| Late 2023 | $5.1M strategic round closed |
| ~Feb 2024 | AlfaFrens launched on Base/Farcaster (Superfluid Labs) |
| May 2024 | AlfaFrens generates 89% of UserOps on Base |
| 2024 | GDA fully replaces IDA. Scroll deployment. 850+ projects. SuperBoring launches. |
| Feb 19, 2025 | SUP token launched on Base. SPR Season 1. |
| Aug 2025 | $2M public token sale. AlfaFrens enters withdraw-only mode (shut down). |
| Nov 22, 2025 | SUP TGE (transferability enabled) |
