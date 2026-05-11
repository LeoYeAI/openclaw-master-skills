# Pagination

Cursor-based pagination for endpoints that return multiple results.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | number | Number of results per page (typically 1-100) |
| `cursor` | string | Cursor from previous response to get next page |

## Pattern

Each response returns a `cursor` value. Use that cursor in the next request to get the next page of results. When the cursor is empty or null, there are no more results.

```bash
# First request
curl "https://deep-index.moralis.io/api/v2.2/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045/nft?chain=0x1&limit=100" \
  -H "X-API-Key: $MORALIS_API_KEY"

# Response includes: {"cursor": "<cursor_value>", ...}

# Next page (use cursor from response)
curl "https://deep-index.moralis.io/api/v2.2/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045/nft?chain=0x1&limit=100&cursor=<cursor_from_previous_response>" \
  -H "X-API-Key: $MORALIS_API_KEY"
```

## Implementation Example (bash)

```bash
#!/usr/bin/env bash

API_KEY="$MORALIS_API_KEY"
ADDRESS="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
CHAIN="0x1"
LIMIT=100
cursor=""

while true; do
  if [ -z "$cursor" ]; then
    url="https://deep-index.moralis.io/api/v2.2/${ADDRESS}/nft?chain=${CHAIN}&limit=${LIMIT}"
  else
    url="https://deep-index.moralis.io/api/v2.2/${ADDRESS}/nft?chain=${CHAIN}&limit=${LIMIT}&cursor=${cursor}"
  fi

  response=$(curl -s "$url" -H "X-API-Key: $API_KEY")
  cursor=$(echo "$response" | jq -r '.cursor // empty')

  # Process results here
  echo "$response" | jq '.result'

  # Check if we've reached the end
  if [ -z "$cursor" ] || [ "$cursor" = "null" ]; then
    break
  fi
done
```

## Notes

- The `limit` parameter can only be set in the initial call
- Cursor value is returned in the response body
- Pagination continues until `cursor` is empty string or null
