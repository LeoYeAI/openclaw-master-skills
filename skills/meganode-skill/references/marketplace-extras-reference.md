# Marketplace Extras Reference

## Overview

This document covers additional marketplace APIs available through NodeReal's MegaNode platform. These are smaller stub sections for specialized chains, bundler services, staking APIs, and DEX data queries. Each API must be activated separately in the MegaNode dashboard under Marketplace before use.

For the primary marketplace APIs, see their dedicated reference files: [nftscan-reference.md](nftscan-reference.md), [contracts-api-reference.md](contracts-api-reference.md), [spaceid-reference.md](spaceid-reference.md), [greenfield-reference.md](greenfield-reference.md), [klaytn-reference.md](klaytn-reference.md), and [zksync-reference.md](zksync-reference.md).

## Table of Contents

1. [Covalent API](#1-covalent-api) -- Unified cross-chain blockchain data aggregation
2. [Arbitrum Nova](#2-arbitrum-nova) -- High-throughput, low-cost AnyTrust L2 chain RPC
3. [Avalanche Contract Chain (C-Chain)](#3-avalanche-contract-chain-c-chain) -- EVM-compatible Avalanche RPC
4. [Arbitrum Nitro](#4-arbitrum-nitro) -- Arbitrum One L2 chain RPC with debug trace support
5. [NEAR RPC](#5-near-rpc) -- NEAR Protocol RPC access
6. [BASE RPC](#6-base-rpc) -- Coinbase EVM-compatible L2 chain RPC
7. [COMBO RPC](#7-combo-rpc) -- COMBO chain RPC (mainnet and testnet)
8. [Particle Bundler RPC](#8-particle-bundler-rpc) -- ERC-4337 Account Abstraction bundler service
9. [BNB Chain Staking API](#9-bnb-chain-staking-api) -- BSC staking rewards and delegation data
10. [PancakeSwap GraphQL v2](#10-pancakeswap-graphql-v2) -- DEX data queries for PancakeSwap
11. [Troubleshooting](#troubleshooting) -- Common issues and solutions
12. [Documentation Links](#documentation-links) -- Official documentation references

---

## 1. Covalent API

Unified blockchain data across multiple chains.

- Token balances (all tokens for an address in one call)
- Transaction history with decoded events
- Cross-chain data aggregation

---

## 2. Arbitrum Nova

**Endpoint:** `https://open-platform.nodereal.io/{apiKey}/arbitrum-nova/`

EVM-compatible chain. Supports standard Ethereum JSON-RPC methods (eth_call, eth_getBalance, eth_blockNumber, etc.). Optimized for high-throughput, low-cost transactions using AnyTrust technology.

**Supported Networks:** Arbitrum Nova (mainnet)

---

## 3. Avalanche Contract Chain (C-Chain)

**Endpoint:** `https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/rpc`

EVM-compatible chain. Supports standard Ethereum JSON-RPC methods. Also supports Avalanche-specific AVAX methods -- see [non-evm-chains-reference.md](non-evm-chains-reference.md) for `avax.*` methods.

**Supported Networks:** Avalanche C-Chain (mainnet)

> **Note:** For complete documentation, see [non-evm-chains-reference.md](non-evm-chains-reference.md).

---

## 4. Arbitrum Nitro

**Endpoint:** `https://open-platform.nodereal.io/{apiKey}/arbitrum-nitro/`

EVM-compatible L2 chain. Supports standard Ethereum JSON-RPC methods plus debug_traceTransaction and debug_traceCall with Nitro-specific response formats.

**Supported Networks:** Arbitrum One (mainnet)

---

## 5. NEAR RPC

**Endpoint:** `https://open-platform.nodereal.io/{apiKey}/near/`

NEAR Protocol RPC access. See [non-evm-chains-reference.md](non-evm-chains-reference.md) for full NEAR method documentation including `query`, `block`, `chunk`, `tx`, and network methods.

> **Note:** For complete documentation, see [non-evm-chains-reference.md](non-evm-chains-reference.md).

---

## 6. BASE RPC

**Endpoint:** `https://open-platform.nodereal.io/{apiKey}/base/`

EVM-compatible L2 chain (Coinbase). Supports standard Ethereum JSON-RPC methods.

**Supported Networks:** BASE (mainnet only)

```bash
curl https://open-platform.nodereal.io/{apiKey}/base/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method":"eth_blockNumber","params":[],"id":1,"jsonrpc":"2.0"}'
```

---

## 7. COMBO RPC

**Endpoints:**
- Mainnet: `https://combo-mainnet.nodereal.io/v1/{apiKey}`
- Testnet: `https://combo-testnet.nodereal.io/v1/{apiKey}`

EVM-compatible chain. Supports standard Ethereum JSON-RPC methods.

**Supported Networks:** COMBO (mainnet & testnet)

```bash
curl https://combo-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method":"eth_blockNumber","params":[],"id":1,"jsonrpc":"2.0"}'
```

---

## 8. Particle Bundler RPC

Account Abstraction (ERC-4337) bundler service.

| Method | Description |
|--------|-------------|
| `eth_sendUserOperation` | Submit user operation |
| `eth_estimateUserOperationGas` | Gas estimation |
| `eth_getUserOperationByHash` | Query operation status |
| `eth_supportedEntryPoints` | Get supported entry points |

---

## 9. BNB Chain Staking API

**Endpoint:** `https://open-platform.nodereal.io/{apiKey}/bnb-chain-staking/`

**Supported Networks:** BSC only

### Get daily staking rewards by delegator

```
GET /bnb-chain-staking/bnb-staking-enhance/staking/reward/list/by_delegator/{address}
```

| Parameter | Location | Required | Type | Description |
|-----------|----------|----------|------|-------------|
| address | path | yes | string | Delegator address |
| start | query | yes | integer | Start timestamp |
| end | query | yes | integer | End timestamp |

**Response fields:** `delegator`, `date`, `operator` (validator), `change` (rewards), `balance`, `apr` (Reward / (Balance - Reward) * 365), `type`, `number`

**Example:**
```
https://open-platform.nodereal.io/{apiKey}/bnb-chain-staking/bnb-staking-enhance/staking/reward/list/by_delegator/0xF2B1d86DC7459887B1f7Ce8d840db1D87613Ce7f?start=1727827200&end=1728259200
```

---

## 10. PancakeSwap GraphQL v2

DEX data queries for PancakeSwap (Premium tier). Supports pair data, token statistics, transaction history, and swap events.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `getsourcecode` returns empty | Contract is not verified | Only verified contracts return source code; verify first |
| Marketplace API returns 403 | API not activated in dashboard | Activate the API in MegaNode dashboard under Marketplace |
| NFTScan returns empty results | Wrong chain or address format | Verify `chain_name` parameter and address checksum |
| Contracts API wrong chain | Incorrect chain-network identifier | Use `bsc-mainnet`, `bsc-testnet`, `op-bnb-mainnet`, or `op-bnb-testnet` |
| Greenfield API errors | API requires specific activation | Activate Greenfield APIs separately in the dashboard |
| `verifysourcecode` fails | Compiler version mismatch | Match exact compiler version and optimization settings from deployment |
| SPACE ID returns empty | Name not registered or expired | Verify the name is registered on SPACE ID and has not expired |
| NFTScan pagination stops | Cursor expired or invalid | Re-fetch from the beginning; cursors may expire |

---

## Documentation Links

- **NodeReal Marketplace:** https://nodereal.io/marketplace
- **NFTScan API:** https://docs.nodereal.io/reference/nftscan-api
- **Contracts API:** https://docs.nodereal.io/reference/get-contract-source-code-for-verified-contract-source-codes
- **SPACE ID API:** https://docs.nodereal.io/reference/space-id-universal-name-service-api
- **Greenfield Enhanced API:** https://docs.nodereal.io/reference/greenfield-enhanced-api
- **Greenfield Billing API:** https://docs.nodereal.io/reference/greenfield-billing-api
- **API Reference:** https://docs.nodereal.io/reference
