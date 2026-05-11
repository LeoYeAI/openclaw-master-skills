# Get token analytics for a list of token addresses

Fetch analytics for multiple tokens, including buy volume, sell volume, buyers, sellers, transactions, liquidity and FDV trends over time. Accepts an array of up to 200 `tokens`, each requiring `chain` and `tokenAddress`.

## Method

POST

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/tokens/analytics`

## Body

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| tokens | array | No | The tokens to be fetched | \`[object Object],[object Object]\` |

## Response Example

Status: 200

Successful response

```json
{
  "categories": [
    {
      "categoryId": "0x1",
      "totalBuyVolume": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "totalSellVolume": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "totalBuyers": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "totalSellers": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "totalBuys": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "totalSells": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "uniqueWallets": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "pricePercentChange": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "usdPrice": "530",
      "totalLiquidity": "530",
      "totalFullyDilutedValuation": "530"
    }
  ]
}
```

## Example (curl)

```bash
curl -X POST "https://deep-index.moralis.io/api/v2.2/tokens/analytics" \
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
