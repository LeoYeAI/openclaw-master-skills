# Get top crypto currencies by trading volume

Get cryptocurrencies with the highest 24 hour trading volume.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/market-data/global/volume`

## Response Example

Status: 200

Returns the top crypto currencies by trading volume

```json
[]
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/market-data/global/volume" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
