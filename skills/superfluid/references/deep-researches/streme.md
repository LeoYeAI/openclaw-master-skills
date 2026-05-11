---
title: Streme.fun
date: 2026-03-19
tags: [superfluid, token-launcher, pure-super-token, GDA, base, farcaster]
sources:
  - https://streme.fun
  - https://docs.streme.fun
  - https://docs.streme.fun/staking
  - https://docs.streme.fun/trading-fees
  - https://docs.streme.fun/sup
  - https://github.com/streme-fun/streme-contracts
  - https://github.com/streme-fun/streme-frontend
  - https://ethglobal.com/showcase/streme-fun-4dppy
  - https://basescan.org/address/0xf77bd45dadd933e6b9eb41226a4cef018e75597c
  - https://explorer.superfluid.finance/base-mainnet/pools/0xa040a8564C433970D7919C441104B1d25b9eAa1c
  - https://tokens.superfluid.org/
  - https://warpcast.com/streme
---

# Streme.fun

AI-agent-powered token launcher on Base that deploys meme coins as **Pure (native) Super Tokens** via Superfluid Protocol. Every token is natively streamable per-second with built-in GDA-powered staking rewards. No bonding curve -- 80% of supply goes directly into locked Uniswap V3 LP at launch. Tokens created by mentioning **@streme on Farcaster**. **Top-10 finalist at ETHGlobal "Agentic Ethereum" hackathon (518 projects).**

---

## Identity

| Attribute | Value |
|---|---|
| Primary builder | Mark Carey (@markcarey on GitHub/Farcaster, @mthacks on X) |
| Co-builder | Lee Knowlton (zeni.eth) |
| Origin | ETHGlobal "Agentic Ethereum" hackathon (Jan 31 - Feb 14, 2025) |
| Awards | Top-10 Finalist, Autonome "Best Social Agent" 1st place |
| Chain | Base (exclusively) |
| Legal entity | None identified; indie/hackathon-originated |
| License | MIT |

Mark Carey has built on Superfluid since 2021 ("rockstar builder" per Superfluid's 2021 year-in-review). Has committed code to the Superfluid protocol monorepo. Serves as a **Superfluid DAO delegate**. Previous projects: TokenVesting, DegenDogs.

---

## Superfluid Integration

Streme uses Superfluid at two fundamental levels: **token creation** (Pure Super Tokens) and **reward distribution** (GDA pools).

### Every Token is a Pure Super Token

Streme tokens are **native/pure Super Tokens** created by cloning `PureSuperToken.sol` via minimal proxy. Not standard ERC-20s wrapped into Super Tokens. Every token natively supports CFA flows, GDA distributions, and batch calls without wrapping.

Implementation contract on Base: `0x49828c61a923624E22CE5b169Be2Bd650Abc9bC8`

Streme's `SuperTokenFactory.sol` handles cloning and pre-minting 100% of supply to the master `Streme.sol` contract.

### GDA Pools Power Staking Rewards

For **each token deployment**, `StakingFactory.sol` creates:
1. A dedicated **SuperfluidPool** (GDA pool) with the launched token as distribution token
2. A **StakedToken** contract (e.g., stCOIN) -- 1:1 receipt token tracking pool membership

Staking rewards allocation (20% of supply in Season One) is streamed into the GDA pool at a **constant linear rate over 365 days**. For a 100B-supply token: ~634,195 tokens/second.

**Stakers receive units (shares)** proportional to their staked deposit. `StakedToken.sol` calls `updateMemberUnits()` on every transfer (mints/burns), automatically adjusting proportional share of streaming rewards.

### Staking Transactions

1. **Approve** -- ERC-20 approval for StakedToken contract
2. **Stake** -- transfers COIN, mints stCOIN 1:1, calls `updateMemberUnits()` on GDA pool
3. **Connect** -- one-time `connectPool()` on Superfluid GDA pool; enables real-time balance updates

### Flow of Funds

```
Token Deployment (100B supply)
  80% (80B) -> Uniswap V3 single-sided LP (locked in LpLockerv2)
    Trading fees -> 40% deployer / 60% Streme protocol
  20% (20B) -> Staking rewards allocation
    Streamed via Superfluid GDA pool -> stakers (365-day linear distribution)
```

### What Superfluid Features Are NOT Used

Streme does **not** use CFA for direct peer-to-peer flows. Streaming is exclusively through **GDA flow-distribute** into pools. However, since every token is a Pure Super Token, users can independently create CFA flows outside Streme's contracts.

---

## No Bonding Curve

Unlike pump.fun or similar launchers, Streme deploys 80% of supply directly into a locked Uniswap V3 position at launch. Tokens are instantly tradeable at market-determined price from block one. No graduation threshold, no migration transaction.

---

## Smart Contract Architecture

Modular 4-step deployment pipeline orchestrated by master contract:

```
Streme.sol (Master)
  Step 1: SuperTokenFactory.sol   -- deploy Pure Super Token, mint supply
  Step 2: StakingFactory.sol      -- deploy GDA pool + StakedToken (Post Deploy Hook)
  Step 3: LPFactory.sol           -- create Uniswap V3 pool + LP position, lock it
  Step 4: (unused in Season One)  -- Post LP Hook slot
```

### Contract Addresses (Base Mainnet, Season One)

| Contract | Address |
|---|---|
| **Streme.sol** | `0xF77bD45DadD933E6B9Eb41226a4CEF018E75597c` |
| **PureSuperToken.sol** | `0x49828c61a923624E22CE5b169Be2Bd650Abc9bC8` |
| **SuperTokenFactory.sol** | `0xcd26DE432EBF832c654176A807b495d966a3E69C` |
| **StakedToken.sol** | `0x2a6cdcB9384FA02AA99D141fa37019Cda284250e` |
| **StakingFactory.sol** | `0x293A5d47f5D76244b715ce0D0e759E0227349486` |
| **LpLockerv2.sol** | `0xc54cb94E91c767374a2F23f0F2cEd698921AE22a` |
| **LPFactory.sol** | `0xfF65a5f74798EebF87C8FdFc4e56a71B511aB5C8` |

### $STREME Flagship Token

| Asset | Address |
|---|---|
| $STREME token | `0x3b3cd21242ba44e9865b066e5ef5d1cc1030cc58` |
| stSTREME staking | `0x93419f1c0f73b278c73085c17407794a6580deff` |
| GDA rewards pool | `0xa040a8564C433970D7919C441104B1d25b9eAa1c` |
| Uniswap V3 pool | `0x9187c24a3a81618f07a9722b935617458f532737` |

LP Factory and LP Locker contracts are **modified from Clanker's open-source code**.

---

## V2 and Seasons Model

V2 introduced customizable deployment parameters. Season One used fixed parameters; V2 makes supply, staking allocation, lock duration, airdrop, prebuy, and fee split configurable.

### $WOOF Case Study (Degen Dogs Migration)

January 2026: Degen Dogs NFT project deployed **$WOOF** (`0x3e5c4FA0cAA794516eD0DF77f31daA534918d492`) via Streme V2 as a Pure Super Token. 10% staking, 10% streaming airdrop, 30-day lock, 2.6 ETH prebuy. DOG NFT holders receive streams from two Superfluid pools per Dog (one $WOOF, one $SUP).

---

## Farcaster + AI Agent

Primary (and currently only) token creation method: mention `@streme` in a Farcaster cast. AI agent deploys token and replies with a Farcaster Frame for sharing, buying, and staking.

| Component | Technology |
|---|---|
| LLM | OpenAI |
| Blockchain | Coinbase AgentKit |
| Agent hosting | Autonome |
| Farcaster webhooks | Neynar |
| Backend | Google Firebase Functions |
| Frontend | Next.js on Vercel |
| Wallet | Privy |
| Swap routing | 0x Protocol |

---

## SUP Rewards

Streme listed on Superfluid's ecosystem page at tokens.superfluid.org as "Token Launchpad." Trading any Streme-deployed Pure Super Token earns **$SUP rewards** through SPR program (announced July 8, 2025). Degen Dogs allocated **1.9M SUP** in SPR Season 4.

---

## Key Relationships

| Partner | Relationship |
|---|---|
| **Superfluid** | Pure Super Tokens + GDA pools; Mark Carey is DAO delegate; SPR rewards |
| **Clanker** | LP code heritage (forked open-source LP locker/factory) |
| **Uniswap V3** | LP positions for all launched tokens |
| **Degen Dogs** | $WOOF migration case study (V2) |
| **Farcaster / Neynar** | Primary creation interface |

---

## Key Repos

| Repo | Description |
|---|---|
| [streme-contracts](https://github.com/streme-fun/streme-contracts) | Public, MIT, Solidity + JS, 263 commits |
| [streme-frontend](https://github.com/streme-fun/streme-frontend) | Public, TypeScript/Next.js |
| streme-server | Referenced but appears private |

No public SDK or NPM packages.

---

## Comparison with Clanker and pump.fun

| Feature | Streme.fun | Clanker | pump.fun |
|---|---|---|---|
| Chain | Base | Base | Solana |
| Token type | Pure Super Token | Standard ERC-20 | SPL token |
| Streaming | Native per-second | None | None |
| Staking | Built-in GDA rewards | None | None |
| Price discovery | Immediate Uniswap V3 LP | Uniswap V3 LP | Bonding curve then Raydium |
| Creation | Farcaster AI agent | Farcaster AI agent | Web UI |
| Fee model | 40% deployer / 60% protocol | ~1% LP fees to creator | 1% tx fee |
