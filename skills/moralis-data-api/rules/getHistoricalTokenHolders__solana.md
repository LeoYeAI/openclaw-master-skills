# Get token holders overtime for a given tokens

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/holders/:address/historical`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| cursor | string | No | The cursor to the next page | - |
| timeFrame | string | Yes | The interval of the holders data | - |
| fromDate | string | Yes | The starting date (format in seconds or datestring accepted by momentjs) | - |
| toDate | string | Yes | The ending date (format in seconds or datestring accepted by momentjs) | - |
| limit | number | No | The limit per page depending on the plan | - |

## Cursor/Pagination

- **limit**: The limit per page depending on the plan
- **cursor**: The cursor to the next page

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

```json
{
  "cursor": "cursor_example",
  "result": [
    {
      "timestamp": "2025-02-25T00:00:00Z",
      "totalHolders": 2000,
      "netHolderChange": 50,
      "holderPercentChange": 2.5,
      "newHoldersByAcquisition": {
        "swap": 150,
        "transfer": 50,
        "airdrop": 20
      },
      "holdersIn": {
        "whales": 5,
        "sharks": 12,
        "dolphins": 20,
        "fish": 100,
        "octopus": 50,
        "crabs": 200,
        "shrimps": 1000
      },
      "holdersOut": {
        "whales": 5,
        "sharks": 12,
        "dolphins": 20,
        "fish": 100,
        "octopus": 50,
        "crabs": 200,
        "shrimps": 1000
      }
    }
  ],
  "page": 0
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/holders/6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN/historical" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
