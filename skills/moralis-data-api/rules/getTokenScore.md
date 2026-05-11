# Get token score by token address

Retrieve a score for a specific token along with detailed metrics including price, volume, liquidity, transaction counts, and supply information.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/tokens/:tokenAddress/score`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| tokenAddress | string | Yes | The token address to query | \`0x6982508145454ce325ddbe47a25d4ec3d2311933\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f, solana) | No | The chain to query | \`eth\` |

## Response Example

Status: 200

Successful response

```json
{
  "tokenAddress": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
  "chainId": "0x1",
  "score": 94,
  "updatedAt": "2025-12-03T21:10:28Z",
  "metrics": {
    "usdPrice": 0.00000647147501365255,
    "liquidityUsd": 10890420.9
  }
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/tokens/0x6982508145454ce325ddbe47a25d4ec3d2311933/score?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
