# Search Entities, Organizations or Wallets

Find entities, organizations, addresses or wallets linked to blockchain addresses. Results are categorised into 3 arrays: entities, addresses, categories.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/entities/search`

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| query | string | Yes | The search query | \`Doge\` |
| limit | number | No | The desired page size of the result. | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.

## Response Example

Status: 200

Returns the search results.

```json
{
  "page": "1",
  "page_size": "100",
  "result": {
    "entities": [],
    "addresses": [],
    "categories": []
  }
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/entities/search?query=Doge" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
