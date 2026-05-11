# Get top NFT collections by market cap

Get top NFT collections by their current market cap. Currently only supports Ethereum.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/market-data/nfts/top-collections`

## Response Example

Status: 200

Returns the top NFT collections by market cap

```json
[]
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/market-data/nfts/top-collections" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
