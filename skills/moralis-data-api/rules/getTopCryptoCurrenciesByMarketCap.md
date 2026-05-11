# Get top crypto currencies by market cap

Get cryptocurrencies by their market cap.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/market-data/global/market-cap`

## Response Example

Status: 200

Returns the top crypto currencies by market cap

```json
[]
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/market-data/global/market-cap" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
