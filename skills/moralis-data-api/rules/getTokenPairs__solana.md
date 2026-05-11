# Get token pairs by address

Get the supported pairs for a specific token address.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/:address/pairs`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`So11111111111111111111111111111111111111112\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| cursor | string | No | The cursor to the next page | - |
| limit | number | No | The limit per page | - |

## Cursor/Pagination

- **limit**: The limit per page
- **cursor**: The cursor to the next page

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

```json
{
  "cursor": "cursor_example",
  "pageSize": 0,
  "page": 0,
  "pairs": [
    {
      "exchangeAddress": "exchangeAddress_example",
      "exchangeName": "exchangeName_example",
      "exchangeLogo": "exchangeLogo_example",
      "pairAddress": "pairAddress_example",
      "pairLabel": "pairLabel_example",
      "usdPrice": 0,
      "usdPrice24hrPercentChange": 0,
      "usdPrice24hrUsdChange": 0,
      "volume24hrNative": 0,
      "volume24hrUsd": 0,
      "liquidityUsd": 0,
      "inactivePair": true,
      "baseToken": "baseToken_example",
      "quoteToken": "quoteToken_example",
      "pair": [
        {
          "tokenAddress": "tokenAddress_example",
          "tokenName": "tokenName_example",
          "tokenSymbol": "tokenSymbol_example",
          "tokenLogo": "tokenLogo_example",
          "tokenDecimals": "tokenDecimals_example",
          "pairTokenType": "pairTokenType_example",
          "liquidityUsd": 0
        }
      ]
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/So11111111111111111111111111111111111111112/pairs" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
