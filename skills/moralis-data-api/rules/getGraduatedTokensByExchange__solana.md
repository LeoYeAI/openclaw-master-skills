# Get graduated tokens by exchange

Get the list of graduated tokens by given exchange.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/exchange/:exchange/graduated`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| exchange | string | Yes | - | - |

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
  "result": [
    {
      "tokenAddress": "tokenAddress_example",
      "name": "name_example",
      "symbol": "symbol_example",
      "logo": "logo_example",
      "decimals": "decimals_example",
      "priceNative": "priceNative_example",
      "priceUsd": "priceUsd_example",
      "liquidity": "liquidity_example",
      "fullyDilutedValuation": "fullyDilutedValuation_example",
      "graduatedAt": "2024-11-28T09:44:55.000Z"
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/exchange/:exchange/graduated" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
