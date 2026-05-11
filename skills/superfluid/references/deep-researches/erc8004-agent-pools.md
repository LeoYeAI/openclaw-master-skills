---
title: ERC-8004 Agent Pools
date: 2026-03-11
tags: [superfluid, erc-8004, ai-agents, GDA, agent-identity, base]
sources:
  - https://eips.ethereum.org/EIPS/eip-8004
  - https://github.com/erc-8004/erc-8004-contracts
  - https://github.com/superfluid-org/8004-demo
  - https://8004-demo.superfluid.org/
  - https://8004scan.io
  - https://8004classifier.pilou.work/
---

# ERC-8004 Agent Pools

Integration of ERC-8004 (Trustless Agent Identity) with Superfluid GDA pools for
proportional token distribution to registered AI agents on Base.

## ERC-8004 Standard

- **EIP**: 8004 — "Trustless Agents" (Draft status, Standards Track: ERC)
- **Created**: 2025-08-13, mainnet launch 2026-01-29
- **Authors**: Marco De Rossi (MetaMask), Davide Crapis (Ethereum Foundation), Jordan Ellis (Google), Erik Reppel (Coinbase)
- **License**: CC0 (Public Domain)
- **Requires**: EIP-155, EIP-712, EIP-721, EIP-1271
- **Design philosophy**: Intentionally lean — payments excluded (handled by x402), trust modeled as pluggable tiers (reputation → staking → cryptographic proofs)
- **Three singleton registries** per chain: Identity, Reputation, Validation

### Identity Registry

- ERC-721 NFT per agent with auto-incrementing `agentId`
- Global identifier: `{namespace}:{chainId}:{identityRegistry}` (e.g. `eip155:8453:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`)
- Three `register()` overloads: with URI + metadata, with URI only, bare (URI added later)
- `agentURI` resolves to JSON registration file (IPFS, HTTPS, or `data:` URI) with `type`, `name`, `description`, `image`, `services` array, `x402Support` flag
- Agents can prove endpoint domain control via `.well-known/agent-registration.json`

**agentWallet lifecycle:**
- `agentWallet` metadata key is **reserved** — cannot be set via `setMetadata()` or during `register()`
- On registration → automatically set to registering owner's address
- To change → owner calls `setAgentWallet(agentId, newWallet, deadline, signature)` — EIP-712 for EOAs, ERC-1271 for contract wallets
- On NFT transfer → **automatically cleared** (reset to zero address); new owner must re-verify
- To explicitly clear → `unsetAgentWallet(agentId)`
- Read → `getAgentWallet(agentId) → address`

**On-chain metadata** (arbitrary key-value, beyond reserved `agentWallet`):
- `setMetadata(agentId, key, value)` / `getMetadata(agentId, key) → bytes`

### Reputation Registry

- Structured feedback with Sybil-awareness
- `giveFeedback(agentId, value, valueDecimals, tag1, tag2, endpoint, feedbackURI, feedbackHash)` — submitter must NOT be agent owner (self-feedback prevention)
- `revokeFeedback(agentId, feedbackIndex)` — 1-indexed per client-agent pair
- `appendResponse(agentId, clientAddress, feedbackIndex, responseURI, responseHash)` — callable by anyone (agent refutation, spam flagging)
- **Sybil-aware reads**: `getSummary(agentId, clientAddresses[], tag1, tag2)` requires caller-supplied client list — forces consumers to curate trusted sources
- Feedback value is signed fixed-point `int128` with `uint8` decimals (0–18)

| tag1 | Measures | Example value |
|---|---|---|
| starred | Quality rating (0–100) | 87 (decimals: 0) |
| reachable | Endpoint up (binary) | 1 (decimals: 0) |
| uptime | Endpoint uptime (%) | 9977 (decimals: 2) = 99.77% |
| responseTime | Latency (ms) | 560 (decimals: 0) |

### Validation Registry

- Still under active development with the TEE community
- Generic request/response hooks for independent validator checks
- `validationRequest(validatorAddress, agentId, requestURI, requestHash)`
- `validationResponse(requestHash, response, responseURI, responseHash, tag)` — response 0–100 (0=failed, 100=passed), supports progressive validation
- Self-validation prevented

## Deployed Addresses

All ERC-8004 contracts use vanity deployment (addresses start with `0x8004`).

| Network | Contract | Address |
|---|---|---|
| Ethereum Mainnet | IdentityRegistry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Ethereum Mainnet | ReputationRegistry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Base Mainnet | IdentityRegistry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Base Mainnet | ReputationRegistry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| ETH Sepolia | IdentityRegistry | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| ETH Sepolia | ReputationRegistry | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |
| Base Sepolia | IdentityRegistry | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| Base Sepolia | ReputationRegistry | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |

## AgentPoolDistributor — Superfluid Integration

The `AgentPoolDistributor` contract bridges ERC-8004 identity to Superfluid GDA pools for SUP distribution.

- **Source**: [superfluid-org/8004-demo](https://github.com/superfluid-org/8004-demo) (`packages/contracts/src/AgentPoolDistributor.sol`)
- **Base Mainnet**: `0x15dcC5564908a3A2C4C7b4659055d0B9e1489A70`
- **Base Sepolia**: `0xefeC3A3C466709E17899d852BEEd916a198d34e3`

### How it works

```
register() → joinPool(agentId) → stream flows in → claimSUP()
```

1. **Register**: Mint ERC-8004 agent identity via IdentityRegistry (through 8004scan.io/create or directly)
2. **joinPool(agentId)**: Verifies ERC-721 ownership, assigns `UNITS_PER_AGENT = 10` units in the GDA pool, collects ETH fee
3. **Stream flows in**: Anyone streams SUP into the pool; Superfluid splits proportionally (`memberFlowRate = poolFlowRate × memberUnits / totalUnits`)
4. **claimSUP()**: Collects accumulated SUP (free, no ETH fee)
5. **leavePool(agentId)**: Sets agent's pool units to zero

### Pool configuration

- `distributionFromAnyAddress: true` — anyone can stream/distribute to the pool
- `transferabilityForUnitsOwner: false` — pool units are non-transferable
- Members are **disconnected by default** — tokens accumulate and must be claimed via `claimSUP()`; alternatively connect via `GDAv1Forwarder.connectPool()` for real-time balance
- `UNITS_PER_AGENT = 10` (constant) — all agents get equal weight

### Fee mechanics

- Join fee in ETH, scales per user: `cost = joinFee × (agentCountByUser + 1)`
- Second agent costs 2x, third costs 3x, etc.
- Fee forwarded to `feeCollector` address
- Admin can update via `setJoinFee()` and `setFeeCollector()`

### Key gotchas

- Pool units go to `agentWallet` (from Identity Registry), not `msg.sender` — same at registration but diverge on NFT transfer
- `leavePool` does NOT auto-claim pending tokens — call `claimSUP()` first
- If `agentWallet` is zero (NFT transferred), `leavePool` falls back to `msg.sender`

For GDA pool mechanics, see `references/contracts/GDAv1Forwarder.abi.yaml` and `references/contracts/SuperfluidPool.abi.yaml`. For SUP token details, see `references/guides/sup-and-dao.md`.

## Demo App

Live at **https://8004-demo.superfluid.org/** on Base mainnet. Built by 0xPilou (Superfluid contributor).

### Tiered pools

| Pool | Eligibility | Description |
|---|---|---|
| Legend | Top 5% agent score | Highest stream rate |
| Maestro | Top 10% agent score | Mid-tier stream rate |
| Common | All registered agents | Base-level earnings |

- Agent score determined by **8004classifier** at https://8004classifier.pilou.work/
- Each tier is a separate GDA pool with its own stream rate
- Staging deployment at `sf8004.pilou.work` on Base Sepolia

## Building Opportunities

- **Reputation-weighted earnings**: Scale pool units by ReputationRegistry scores via `getSummary()` + `updateMemberUnits()` instead of flat 10 per agent
- **Validation-gated access**: Require passing ValidationRegistry checks before `joinPool()`
- **Agent DAOs / guilds**: Collective pool membership governance
- **Direct agent-to-agent streams**: CFA streams bypassing pools for 1:1 payments
- **Event-driven bounties**: Instant GDA distributions for task completion
- **Staking/slashing**: Reduce units for poor validation performance, redistribute to good actors

## Ecosystem Context

ERC-8004 sits in a three-layer architecture for the agentic economy:

- **Communication**: MCP (Anthropic), A2A (Google → Linux Foundation), OASF
- **Trust & Identity**: ERC-8004 for discovery, reputation, validation
- **Payments**: x402 (Coinbase + Cloudflare) for HTTP-native micropayments, ERC-8183 for conditional job payments

## Ecosystem Tools

- **8004scan.io** — Agent registry explorer and registration UI (built by AltLayer)
- **8004classifier** — Agent scoring/classification for pool tier eligibility (built by 0xPilou)
- **awesome-erc8004** — Curated resource list at `github.com/sudeepb02/awesome-erc8004`
- No official SDK yet — interact via standard Viem/Ethers.js with ABIs from `erc-8004/erc-8004-contracts`

## Key Repos

- [8004-demo](https://github.com/superfluid-org/8004-demo) — AgentPoolDistributor + Next.js frontend (Superfluid)
- [erc-8004-contracts](https://github.com/erc-8004/erc-8004-contracts) — Reference registry implementations (Hardhat 3, Viem, TypeScript)
