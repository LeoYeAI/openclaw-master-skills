# Retrieve timeseries trading stats by token addresses

Fetch timeseries buy volume, sell volume, liquidity and FDV for multiple tokens. Accepts an array of up to 200 `tokens`, each requiring `chain` and `tokenAddress`.

## Method

POST

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/tokens/analytics/timeseries`

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| timeframe | string | Yes | The timeframe to query | \`1d\` |

## Body

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| tokens | array | No | The tokens to be fetched | \`[object Object],[object Object]\` |

## Response Example

Status: 200

Successful response

```json
{
  "result": [
    {
      "chainId": "0x1",
      "tokenAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7",
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
  ]
}
```

## Example (curl)

```bash
curl -X POST "https://deep-index.moralis.io/api/v2.2/tokens/analytics/timeseries?timeframe=1d" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "tokens": [
    {
      "chain": "0x1",
      "tokenAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7"
    },
    {
      "chain": "solana",
      "tokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    }
  ]
}'
```
