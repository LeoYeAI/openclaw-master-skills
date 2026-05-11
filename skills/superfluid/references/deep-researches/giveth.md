---
title: Giveth
date: 2026-03-19
tags: [superfluid, donations, public-goods, CFA, optimism, base]
sources:
  - https://docs.giveth.io/recurringdonation
  - https://docs.giveth.io/giveconomy
  - https://docs.giveth.io/about-giveth
  - https://github.com/Giveth/giveth-dapps-v2
  - https://github.com/Giveth/impact-graph
  - https://github.com/Giveth/donation-handler-foundry
  - https://forum.giveth.io/t/giveth-superfluid-integration-for-recurring-donations-on-optimism/1160
  - https://superfluid.org/post/how-superfluid-protocol-is-empowering-onchain-builders
  - https://superfluid.org/post/superfluid-streaming-programmatic-rewards-season-1
  - https://blog.giveth.io/recurring-donations-now-come-with-sup-rewards-accb1fa6f18b
  - https://etherscan.io/address/0x900db999074d9277c5da2a43f252d74366230da0
  - https://www.coingecko.com/en/coins/giveth
---

# Giveth

Zero-fee, open-source crypto donation platform built on Ethereum and multiple EVM chains. Uses Superfluid CFA for recurring per-second donations on Optimism and Base. Founded in late 2016 by Griff Green in Barcelona. **7,000+ verified projects, 25,000+ total donors, $1.41M raised in 2025.** Governed by GIV token holders.

---

## Identity

| Attribute | Value |
|---|---|
| Founded | Late 2016 |
| Founder | Griff Green (also co-founded DAppNode, Commons Stack, General Magic, Token Engineering Commons) |
| Location | Barcelona / Catalonia, Spain |
| Team | ~27 people across 4 continents |
| Entity | DAO with Donor Advised Fund (no traditional corporate entity) |
| Governance | Snapshot voting (giv.eth), multisig treasury, sociocracy principles |
| Chains | Ethereum, Gnosis, Optimism, Base, Polygon, Polygon zkEVM, Arbitrum, Celo, ETC, Solana, Stellar |

---

## Products

### Direct Donations

Peer-to-peer with **zero platform fees**. Supports any ERC-20 token on supported chains.

### Quadratic Funding (QF) Rounds

Uses Connection Oriented Cluster Match (COCM) algorithm with Gitcoin Passport for sybil resistance. Matching pools funded by Public Nouns, Octant, Arbitrum, ENS.

### Recurring Donations (Superfluid)

Per-second streaming donations powered by Superfluid CFA on **Optimism and Base**. Launched Q1 2024.

---

## Superfluid Integration

### Agreement Type

Exclusively **CFA (Constant Flow Agreement)** -- one-to-one continuous streams. No GDA usage. Each donor-project pair is an independent CFA stream.

### Architectural Flow

1. Donor selects token (DAI, USDC, ETH, GIV, OP) and deposit amount
2. For ERC-20: two transactions (approve + batch call to upgrade to Super Token and create CFA flow). For ETH: one transaction (ETHx wraps natively)
3. Superfluid CFA streams tokens per-second from donor to project's **Allo Protocol anchor contract**
4. Project owner withdraws accumulated funds from anchor contract at any time
5. Donors can modify flow rate or delete flow anytime via "My Donations" panel

UI abstracts flow rates into **monthly amounts**. Minimum 1-month buffer enforced.

### Supported Super Tokens

| Base Token | Super Token | Transactions |
|---|---|---|
| ETH | ETHx | 1 tx |
| DAI | DAIx | 2 txs |
| USDC | USDCx | 2 txs |
| OP | OPx | 2 txs |
| GIV | GIVx | 2 txs |

### Superfluid Contract Addresses (Optimism)

| Contract | Address |
|---|---|
| Superfluid Host | `0x567c4B141ED61923967cA25Ef4906C8781069a10` |
| CFA V1 | `0x204C6f131bb7F258b2Ea1593f5309911d8E458eD` |
| CFAv1Forwarder | `0xcfA132E353cB4E398080B9700609bb008eceB125` |
| SuperTokenFactory | `0x8276469A443D5C6B7146BED45e2abCaD3B6adad9` |
| ETHx | `0x4ac8bD1bDaE47beeF2D1c6Aa62229509b962Aa0d` |

Frontend uses **CFAv1Forwarder** via `@superfluid-finance/sdk-core` and `@superfluid-finance/metadata`.

### Important Disambiguation

The **GIVstream** (5-year token vesting mechanism) does **NOT** use Superfluid. It is a custom `TokenDistro` smart contract. Only recurring donations use Superfluid.

### SUP Rewards Participation

| Season | Giveth Allocation |
|---|---|
| Season 1 | Included as partner (recurring donations quadrupled) |
| Season 2 | 2.96M SUP |
| Season 3 | Continued |
| Season 4 | 1.226M SUP streamed |

### Limitations

- Recurring donations limited to **Optimism and Base only**
- Projects must deploy an Allo Protocol anchor contract
- If donor's Super Token balance runs out, all recurring donations using that token stop
- Two-transaction UX for ERC-20 tokens adds friction

---

## GIV Token

| Property | Value |
|---|---|
| Launch | December 24, 2021 |
| Total supply | 1,000,000,000 GIV (hard cap, no minting) |
| Initial liquid | 100M GIV (10%) |
| GIVstream vesting | 900M over 5 years (ends December 23, 2026) |
| Funding | No presales, no VC |

### Distribution

| Allocation | % |
|---|---|
| GIVgarden common pool | 33% |
| Future contributors / rGIV DAO / roadmap | 26.95% |
| GIVdrop (airdrop) | 17.05% |
| GIVbacks (donor rewards) | 13% |
| GIVfarm (liquidity mining) | 10% |

### GIV Addresses

| Chain | Address |
|---|---|
| Ethereum | `0x900db999074d9277c5da2a43f252d74366230da0` |
| Gnosis | `0x4f4F9b8D5B4d0Dc10506e5551B0513B61fD59e75` |
| Optimism | `0x528CDc92eAB044E1E39FE43B9514bfdAB4412B98` |
| Polygon zkEVM | `0xddAFB91475bBf6210a151FA911AC8fdA7dE46Ec2` |

### GIVbacks

Donors to verified projects receive GIV rewards. Transitioned to **raffle format at Round 77** (~mid-2024). Each $5+ donation earns a raffle entry; one winner per address per round for up to 1M GIV.

### GIVpower

Stake and lock GIV to receive GIVpower (veToken model). Boost verified projects to influence rankings and GIVbacks percentages.

---

## Key Stats

| Metric | Value |
|---|---|
| Donations in 2025 | 395,312 totaling $1.41M |
| New donors in 2025 | 7,520 |
| Verified projects | 7,000+ |
| Total donors | 25,000+ |

---

## Key Multisig Wallets

| Purpose | Address |
|---|---|
| Giveth Multisig (giv.eth) | `0x4D9339dd97db55e3B9bCBE65dE39fF9c04d1C2cd` |
| Multisig Liquidity | `0xf924fF0f192f0c7c073161e0d62CE7635114e74f` |

---

## Key Relationships

| Partner | Relationship |
|---|---|
| **Superfluid** | Recurring donations infrastructure; SUP Seasons participant |
| **Gitcoin** | QF round hosting, shared Passport for sybil resistance |
| **Octant** | Matching pool funding |
| **Gnosis Chain** | Deep historical integration |
| **Optimism** | Growth experiment grants; Griff Green is top delegate |
| **Arbitrum** | QF rounds with 150,000 ARB matching pools |
| **Commons Stack / General Magic** | Sister organizations (Griff Green co-founded) |
| **Blockscout** | Explorer integration |
| **Flow State** | Co-participant in SPR Public Goods campaign |

---

## Key Repos

| Repo | Description |
|---|---|
| [giveth-dapps-v2](https://github.com/Giveth/giveth-dapps-v2) | Main frontend (Next.js/TypeScript) |
| [impact-graph](https://github.com/Giveth/impact-graph) | Backend GraphQL API (TypeGraphQL/PostgreSQL) |
| [giv-token-contracts](https://github.com/Giveth/giv-token-contracts) | GIV token, TokenDistro, staking contracts |
| [donation-handler-foundry](https://github.com/Giveth/donation-handler-foundry) | Donation handler contracts (Foundry) |
| [giveth-v6-fe](https://github.com/Giveth/giveth-v6-fe) | Giveth v6 frontend (active development, Mar 2026) |
| [giveth-v6-core](https://github.com/Giveth/giveth-v6-core) | Giveth v6 core backend (active development, Mar 2026) |

Superfluid integration lives within `giveth-dapps-v2` (frontend) and `impact-graph` (backend) -- no dedicated Superfluid-specific repo.

---

## Timeline

| Date | Event |
|---|---|
| Late 2016 | Founded by Griff Green in Barcelona |
| 2017-2022 | Giveth TRACE (v1) -- Liquid Pledging on Rinkeby |
| ~2020-2021 | Giveth.io (v2) launched |
| Dec 24, 2021 | GIVeconomy launched (GIV token, GIVbacks, GIVfarm, GIVstream, GIVgarden) |
| Aug 2023 | Superfluid integration work begins (GitHub issue #3089) |
| Q1 2024 | Recurring donations via Superfluid go live on Optimism |
| Mar 7, 2024 | GIVgarden deprecated; governance to Snapshot |
| Mid-2024 | GIVbacks transitions to raffle format (Round 77) |
| 2025 | Base support for recurring donations; SUP Seasons 1-4; Solana + Stellar support |
| Sep 2025 | "Causes" feature -- AI-powered smart funding pools |
| Mar 2026 | Giveth v6 in active development |
| Dec 23, 2026 | GIVstream vesting ends (scheduled) |

No major publicly documented exploits or security breaches. Bug bounty via Hats Finance.
