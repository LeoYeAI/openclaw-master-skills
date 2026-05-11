# Get ERC20 token categories

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/tokens/categories`

## Response Example

Status: 200

Returns a list of ERC20 token categories, such as stablecoin, meme, governance, and more. Use this endpoint to explore available token categories for filtering or analytics.

```json
[
  {
    "categories": [
      {
        "name": "Stablecoin",
        "id": "stablecoin"
      }
    ]
  }
]
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/tokens/categories" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
