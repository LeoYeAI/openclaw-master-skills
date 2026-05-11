# Get token price

Gets the token price (usd and native) for a given contract address and network.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/:address/price`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`So11111111111111111111111111111111111111112\` |

## Response Example

Status: default

```json
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
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/So11111111111111111111111111111111111111112/price" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
