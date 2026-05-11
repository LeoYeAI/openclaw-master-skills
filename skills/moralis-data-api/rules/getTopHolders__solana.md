# Get paginated top holders for a given token.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/:address/top-holders`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\` |

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
  "result": [
    {
      "balance": "balance_example",
      "balanceFormatted": "balanceFormatted_example",
      "isContract": true,
      "ownerAddress": "ownerAddress_example",
      "usdValue": "usdValue_example",
      "percentageRelativeToTotalSupply": 0
    }
  ],
  "cursor": "cursor_example",
  "page": 0,
  "pageSize": 0,
  "totalSupply": "totalSupply_example"
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/top-holders" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
