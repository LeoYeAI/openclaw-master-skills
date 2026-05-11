# Get Entity Categories

List available categories for blockchain entities.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/entities/categories`

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| limit | number | No | The desired page size of the result. | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.

## Response Example

Status: 200

Returns the entity categories.

```json
{
  "page": "1",
  "page_size": "100",
  "result": [
    {
      "total_entities": 100
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/entities/categories" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
