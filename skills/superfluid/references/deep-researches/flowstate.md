---
title: Flow State Network
date: 2026-03-09
tags: [superfluid, public-goods, quadratic-funding, streaming, cooperative, GDA]
sources:
  - https://flowstate.network/
  - https://docs.flowstate.network/
  - https://github.com/flow-state-coop
  - https://x.com/flowstatecoop
---

# Flow State

Streaming money platform and digital cooperative built on Superfluid Protocol.

## Identity

- **Entity**: Flow State Coop — Colorado Limited Cooperative (USA)
- **Tagline**: "Making Impact Common"
- **Focus**: Funding, sustaining, and rewarding impact work via programmable money streams
- **Governance**: Democratically governed; onchain profit distribution across multiple stakeholder classes

## Products

### Streaming Quadratic Funding (SQF)

- Novel QF implementation with streaming architecture (invented at Geo Web protocol)
- Donations = open-ended money flows (not one-off transfers)
- Quadratic matching formula continuously allocates pool funds based on streamed "votes"
- Donors can change streams anytime → matching recalculates in real-time
- Rounds can be open-ended (no periodic round constraint)
- Grantees receive funds immediately and continuously (not after round ends)
- Built on Superfluid GDA (pool-based distribution)
- **Octant Builder Accelerator SQF round**: 25.5+ ETH streamed to builders, 1,300+ concurrent donation streams
- Uses ETHx (Super Token wrapped ETH) for donations
- Deployed on Base (chainId 8453)

### Flow Councils

- Continuous and participatory budget allocation via direct voting strategy
- Forked from BlossomLabs/CouncilHaus
- Repo: [councilhaus](https://github.com/flow-state-coop/councilhaus) (AGPL-3.0)

### Flow Splitters

- Dynamic many-to-many stream splitting for teams, guilds, and communities
- Contract interface: `IFlowSplitter`
- Repo: [flow-splitter](https://github.com/flow-state-coop/flow-splitter) (MIT)

### Flow Caster

- Farcaster-based streaming tips companion app
- Live at: `caster.flowstate.network`
- Repo: [flow-caster](https://github.com/flow-state-coop/flow-caster)

### DocEngine

- Companion web app for "flow rounds"
- Live at: `docengine.flowstate.network`

## Superfluid Integration

- **Core dependency**: All products built on Superfluid Protocol
- **Agreements used**: CFA (Constant Flow Agreement), GDA (General Distribution Agreement)
- **Token type**: Super Tokens (ETHx, USDCx, etc.)
- **SPR Season 1**: Flow State included in Superfluid Streaming Programmatic Rewards campaign (earns SUP)
- **SPR allocation**: Part of the "Public Goods" campaign (5% of S1 = 2,500,000 SUP, shared with Giveth)
- **Supervisual fork**: Forked `kasparkallas/supervisual` for Superfluid stream visualization
- **Uniswap V4 + GDA PoC**: [univ4-gda-poc](https://github.com/flow-state-coop/univ4-gda-poc) — proof of concept combining Uniswap V4 hooks with Superfluid GDA
- **GDA auto-connect**: Active participant in Superfluid DAO governance RFC for GDA auto-connect feature

## npm Package

- **`@flowstate/core`**: Virtualizes Superfluid flow update events into discrete transfer amounts
- Converts continuous streams into daily/weekly/monthly/annual transfer arrays
- Example: stream of 5 USDCx/day for 30 days → 30 daily transfers of 5 USDCx, or 4 weekly of 35, or 1 monthly of 150
- GitHub: [flowstate](https://github.com/Flow-State-Labs/flowstate)

## Key Repos

- [platform](https://github.com/flow-state-coop/platform) — Main platform frontend (TypeScript, MIT)
- [sqf-indexer](https://github.com/flow-state-coop/sqf-indexer) — SQF event indexer (TypeScript, MIT)
- [allo-v2](https://github.com/flow-state-coop/allo-v2) — Allo Protocol V2 fork (Solidity)
- [docs](https://github.com/flow-state-coop/docs) — Documentation site (Docusaurus)

## Key Relationships

- **Superfluid Protocol**: Core infrastructure dependency; SPR participant
- **Octant**: Joint Builder Accelerator SQF round (poolId 63, Base)
- **Gitcoin / Allo Protocol**: SQF as Allo strategy; multiple GG rounds (GG22, GG23)
- **Geo Web**: Origin of SQF concept; uses PCO land market ETH streams
- **Giveth**: Co-participant in SPR Public Goods campaign

## Grants

Funded via Gitcoin GG22/GG23, Allo Builders Advancement, OpenCivics Collaborative Research, Web3 Grants Ecosystem, and Octant Community rounds. Tracked on [Karma GAP](https://gap.karmahq.xyz/project/flow-state-streaming-quadratic-funding).
