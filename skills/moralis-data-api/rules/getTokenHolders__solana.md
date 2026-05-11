# Get the summary of holders for a given token token.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/holders/:address`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN\` |

## Response Example

Status: 200

```json
{
  "totalHolders": 5000,
  "holdersByAcquisition": {
    "swap": 150,
    "transfer": 50,
    "airdrop": 20
  },
  "holderChange": {},
  "holderDistribution": {
    "whales": 150,
    "sharks": 150,
    "dolphins": 150,
    "fish": 150,
    "octopus": 150,
    "crabs": 150,
    "shrimps": 150
  },
  "holderSupply": {}
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/holders/6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
