# Get token price

Gets the token price (usd and native) for a given contract address and network.

## Method

POST

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/prices`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |

## Body

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| addresses | array | No | - | \`\` |

## Response Example

Status: default

```json
[
  {
    "tokenAddress": "tokenAddress_example",
    "pairAddress": "pairAddress_example",
    "nativePrice": {
      "value": "value_example",
      "decimals": 0,
      "name": "name_example",
      "symbol": "symbol_example"
    },
    "usdPrice": 0,
    "exchangeAddress": "exchangeAddress_example",
    "exchangeName": "exchangeName_example",
    "logo": "logo_example",
    "name": "name_example",
    "symbol": "symbol_example",
    "score": 0,
    "usdPrice24h": 0,
    "usdPrice24hrUsdChange": 0,
    "usdPrice24hrPercentChange": 0,
    "isVerifiedContract": true
  }
]
```

## Example (curl)

```bash
curl -X POST "https://solana-gateway.moralis.io/token/mainnet/prices" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "addresses": []
}'
```
