# Get aggregated token pair statistics by address

Get aggregated statistics across supported pairs of a token.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/:address/pairs/stats`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`So11111111111111111111111111111111111111112\` |

## Response Example

Status: 200

```json
{
  "totalLiquidityUsd": 0,
  "totalActivePairs": 0,
  "totalActiveDexes": 0,
  "totalSwaps": {
    "5min": 0,
    "1h": 0,
    "4h": 0,
    "24h": 0
  },
  "totalVolume": {
    "5min": 0,
    "1h": 0,
    "4h": 0,
    "24h": 0
  },
  "totalBuyVolume": {
    "5min": 0,
    "1h": 0,
    "4h": 0,
    "24h": 0
  },
  "totalSellVolume": {
    "5min": 0,
    "1h": 0,
    "4h": 0,
    "24h": 0
  },
  "totalBuyers": {
    "5min": 0,
    "1h": 0,
    "4h": 0,
    "24h": 0
  },
  "totalSellers": {
    "5min": 0,
    "1h": 0,
    "4h": 0,
    "24h": 0
  }
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/So11111111111111111111111111111111111111112/pairs/stats" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
