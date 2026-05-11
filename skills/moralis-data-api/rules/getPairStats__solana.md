# Get stats for a pair address

Gets the stats for a specific pair address

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/pairs/:pairAddress/stats`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| pairAddress | string | Yes | The address of the pair to query | \`Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE\` |

## Response Example

Status: 200

```json
{
  "tokenAddress": "tokenAddress_example",
  "tokenName": "tokenName_example",
  "tokenSymbol": "tokenSymbol_example",
  "tokenLogo": "tokenLogo_example",
  "pairCreated": "pairCreated_example",
  "pairLabel": "pairLabel_example",
  "pairAddress": "pairAddress_example",
  "exchange": "exchange_example",
  "exchangeAddress": "exchangeAddress_example",
  "exchangeLogo": "exchangeLogo_example",
  "exchangeUrl": "exchangeUrl_example",
  "currentUsdPrice": "currentUsdPrice_example",
  "currentNativePrice": "currentNativePrice_example",
  "totalLiquidityUsd": "totalLiquidityUsd_example"
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/pairs/Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE/stats" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
