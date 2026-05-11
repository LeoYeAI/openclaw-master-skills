# Supported Chains Reference

## Overview

MegaNode supports 25+ blockchain networks with varying levels of feature support. This reference provides the complete chain support matrix.

---

## Table of Contents

1. [Chain Support Matrix](#chain-support-matrix) -- full chain list with feature flags
2. [Endpoint URL Patterns](#endpoint-url-patterns) -- URL templates and chain identifiers
3. [Feature Availability by Chain](#feature-availability-by-chain) -- feature tiers by chain
4. [MegaFuel Support](#megafuel-support-gasless-transactions) -- gasless transaction availability
5. [Direct Route Support](#direct-route-support-mev-protection) -- MEV protection availability
6. [Notes](#notes) -- important caveats and limitations

---

## Chain Support Matrix

| Chain | Mainnet | Testnet | Archive Node | Enhanced APIs | Chain ID |
|-------|---------|---------|--------------|---------------|----------|
| BNB Smart Chain (BSC) | Yes | Yes | Yes | Yes | 56 / 97 |
| Ethereum | Yes | Yes (Sepolia) | Yes | Yes | 1 / 11155111 |
| Optimism | Yes | — | Yes | Partial | 10 |
| opBNB | Yes | Yes | — | Partial | 204 / 5611 |
| Aptos | Yes | Yes | — | — | — |
| Arbitrum One | Yes | — | — | — | 42161 |
| Arbitrum Nova | Yes | — | — | — | 42170 |
| Polygon | Yes | — | Yes | — | 137 |
| Avalanche C-Chain | Yes | — | — | — | 43114 |
| Fantom | Yes | — | — | — | 250 |
| Klaytn | Yes | — | — | — | 8217 |
| NEAR | Yes | — | — | — | — |
| Cronos | Yes | — | — | — | 25 |
| Gnosis | Yes | — | — | — | 100 |
| Moonbeam | Yes | — | — | — | 1284 |
| PlatON | Yes | — | — | — | 210425 |
| zkSync | Yes | — | — | — | 324 |
| BASE | Yes | — | — | — | 8453 |
| Algorand | Yes | — | — | — | — |
| COMBO | Yes | — | — | — | — |
| BNB Greenfield | Yes | — | — | — | — |
| ETH Beacon Chain | Yes | — | — | — | — |

---

## Endpoint URL Patterns

### EVM Chains

```
HTTPS: https://{chain-identifier}-{network}.nodereal.io/v1/{API-key}
WSS:   wss://{chain-identifier}-{network}.nodereal.io/ws/v1/{API-key}
```

### Common Chain Identifiers

| Chain | Identifier | Mainnet URL Example |
|-------|-----------|-------------------|
| BNB Smart Chain | `bsc` | `https://bsc-mainnet.nodereal.io/v1/{key}` |
| BNB Smart Chain Testnet | `bsc` | `https://bsc-testnet.nodereal.io/v1/{key}` |
| Ethereum | `eth` | `https://eth-mainnet.nodereal.io/v1/{key}` |
| Ethereum Sepolia | `eth` | `https://eth-sepolia.nodereal.io/v1/{key}` |
| Optimism | `opt` | `https://opt-mainnet.nodereal.io/v1/{key}` |
| opBNB | `opbnb` | `https://opbnb-mainnet.nodereal.io/v1/{key}` |
| opBNB Testnet | `opbnb` | `https://opbnb-testnet.nodereal.io/v1/{key}` |
| Arbitrum One | `arb` | `https://arb-mainnet.nodereal.io/v1/{key}` |
| Polygon | `polygon` | `https://polygon-mainnet.nodereal.io/v1/{key}` |
| BASE | `base` | `https://base-mainnet.nodereal.io/v1/{key}` |

---

## Feature Availability by Chain

### Full Feature Support (RPC + Enhanced APIs + Archive + WebSocket)

- **BNB Smart Chain** — Flagship chain with all features
- **Ethereum** — Full support including Enhanced APIs

### Standard RPC + Archive

- **Optimism** — RPC + Archive, partial Enhanced APIs
- **Polygon** — RPC + Archive

### Standard RPC Only

- Arbitrum One/Nova, Avalanche C-Chain, Fantom, Klaytn, Cronos, Gnosis, Moonbeam, PlatON, zkSync, BASE

### Non-EVM Chains

- **Aptos** — REST API (not JSON-RPC)
- **NEAR** — JSON-RPC with NEAR-specific methods

---

## MegaFuel Support (Gasless Transactions)

| Chain | Mainnet | Testnet |
|-------|---------|---------|
| BNB Smart Chain | Yes | Yes |
| opBNB | Yes | Yes |

## Direct Route Support (MEV Protection)

| Chain | Support |
|-------|---------|
| BNB Smart Chain | Yes |

---

## Notes

- BNB Beacon Chain is **NOT** supported
- Testnet archive nodes are **NOT** available
- Enhanced APIs are primarily available on BSC and Ethereum
- WebSocket (WSS) is available on BSC, Ethereum, and Optimism
- API key works across all supported chains — no per-chain configuration needed
- Check [NodeReal documentation](https://docs.nodereal.io) for the latest chain additions
