# Get DeFi positions of a wallet

Get a concise overview of a wallet’s DeFi positions across all protocols.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/defi/positions`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | Wallet address | \`0xd100d8b69c5ae23d6aa30c6c3874bf47539b95fd\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |

## Response Example

Status: 200

Returns all defi positions for the wallet address.

```json
[
  {
    "protocol_name": "Uniswap v2",
    "protocol_id": "uniswap-v2",
    "protocol_url": "https://app.uniswap.org/pools/v2",
    "protocol_logo": "https://cdn.moralis.io/defi/uniswap.png",
    "position": {
      "label": "liquidity",
      "tokens": [],
      "address": "0x06012c8cf97bead5deae237070f9587f8e7a266d",
      "balance_usd": "1000000",
      "total_unclaimed_usd_value": "1000000"
    }
  }
]
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xd100d8b69c5ae23d6aa30c6c3874bf47539b95fd/defi/positions?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
