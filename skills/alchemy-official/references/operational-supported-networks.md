---
id: references/operational-supported-networks.md
name: 'Supported Networks'
description: 'Alchemy supports multiple EVM and Solana networks. Always verify network availability in the dashboard for each product.'
tags:
  - alchemy
  - operational
  - operations
related:
  - node-json-rpc.md
  - solana-rpc.md
updated: 2026-02-05
---
# Supported Networks

## Summary
Alchemy supports multiple EVM and Solana networks. Always verify network availability in the dashboard for each product.

## Guidance
- Use chain-specific base URLs (e.g., `eth-mainnet`, `polygon-mainnet`).
- Use testnets for QA.
- Not all products are available on every chain.


## Spec-Derived Network Enums (Partial)
These lists are pulled directly from the repo's OpenAPI specs and may not be exhaustive. Always confirm in the dashboard.

### Notify API Networks (Uppercase)
```text
ETH_MAINNET
ETH_SEPOLIA
ETH_HOLESKY
ARB_MAINNET
ARB_SEPOLIA
ARBNOVA_MAINNET
MATIC_MAINNET
MATIC_MUMBAI
OPT_MAINNET
OPT_GOERLI
BASE_MAINNET
BASE_SEPOLIA
ZKSYNC_MAINNET
ZKSYNC_SEPOLIA
LINEA_MAINNET
LINEA_SEPOLIA
GNOSIS_MAINNET
GNOSIS_CHIADO
FANTOM_MAINNET
FANTOM_TESTNET
METIS_MAINNET
BLAST_MAINNET
BLAST_SEPOLIA
SHAPE_MAINNET
SHAPE_SEPOLIA
ZETACHAIN_MAINNET
ZETACHAIN_TESTNET
WORLDCHAIN_MAINNET
WORLDCHAIN_SEPOLIA
BNB_MAINNET
BNB_TESTNET
AVAX_MAINNET
AVAX_FUJI
SONEIUM_MAINNET
SONEIUM_MINATO
GEIST_POLTER
GEIST_MAINNET
STARKNET_MAINNET
STARKNET_SEPOLIA
STARKNET_GOERLI
INK_MAINNET
INK_SEPOLIA
ROOTSTOCK_MAINNET
ROOTSTOCK_TESTNET
SCROLL_MAINNET
SCROLL_SEPOLIA
MONAD_TESTNET
SONIC_MAINNET
SONIC_TESTNET
SETTLUS_SEPTESTNET
APECHAIN_MAINNET
APECHAIN_CURTIS
```

### Data API Networks (Lowercase)
```text
eth-mainnet
eth-sepolia
eth-holesky
avax-mainnet
avax-fuji
zksync-mainnet
opt-mainnet
polygon-mainnet
polygon-amoy
arb-mainnet
arb-sepolia
blast-mainnet
blast-sepolia
base-mainnet
base-sepolia
soneium-mainnet
soneium-minato
scroll-mainnet
scroll-sepolia
shape-mainnet
shape-sepolia
lens-mainnet
lens-sepolia
starknet-mainnet
starknet-sepolia
rootstock-mainnet
rootstock-testnet
linea-mainnet
linea-sepolia
settlus-septestnet
abstract-mainnet
abstract-testnet
apechain-mainnet
```

## Related Files
- `node-json-rpc.md`
- `solana-rpc.md`

## Official Docs
- [Supported Chains](https://www.alchemy.com/docs/reference/node-supported-chains)
- [Chain APIs Overview](https://www.alchemy.com/docs/reference/chain-apis-overview)
