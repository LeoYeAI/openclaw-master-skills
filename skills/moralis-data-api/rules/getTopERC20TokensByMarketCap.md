# Get top ERC20 tokens by market cap

List the top ERC20 tokens ranked by market cap. Currently only supports Ethereum. For more flexibility, we recommend to use getFilteredTokens.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/market-data/erc20s/top-tokens`

## Response Example

Status: 200

Returns the top ERC20 tokens by market cap

```json
[]
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/market-data/erc20s/top-tokens" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
