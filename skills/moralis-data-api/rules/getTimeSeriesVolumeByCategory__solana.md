# Retrieve timeseries trading stats by category

**Solana variant:** Fetch timeseries buy volume, sell volume, liquidity and FDV for a specific category. Optionally filter by `chain`.

This EVM endpoint supports Solana via the `chain=solana` parameter.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/volume/timeseries/:categoryId`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| categoryId | string | Yes | The category id | \`1\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f, solana) | No | The chain to query | \`solana\` |
| timeframe | string | Yes | The timeframe to query | \`1d\` |

## Response Example

Status: 200

Successful response

```json
{
  "timeseries": [
    {
      "timestamp": "2022-02-22T00:00:00Z",
      "buyVolume": 4565,
      "sellVolume": 4565,
      "liquidityUsd": 4565,
      "fullyDilutedValuation": 4565
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/volume/timeseries/1?chain=solana&timeframe=1d" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
