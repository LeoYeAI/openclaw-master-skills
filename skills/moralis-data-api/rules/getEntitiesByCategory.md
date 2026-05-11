# Get Entities By Category

Fetch entities belonging to a specific category. Each entity returns name, logo, description, external links, total addresses and more.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/entities/categories/:categoryId`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| categoryId | string | Yes | The category Id | \`1\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| limit | number | No | The desired page size of the result. | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.

## Response Example

Status: 200

Returns the entities belonging to the category.

```json
{
  "page": "1",
  "page_size": "100",
  "result": [
    {
      "total_addresses": 100
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/entities/categories/1" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
