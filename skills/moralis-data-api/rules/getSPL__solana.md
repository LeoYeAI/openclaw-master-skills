# Gets token balances owned by the given address

Gets token balances owned by the given address

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/account/:network/:address/tokens`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`kXB7FfzdrfZpAZEW3TZcp8a8CwQbsowa6BdfAHZ4gVs\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| excludeSpam | boolean | No | Should exclude spam tokens | - |

## Response Example

Status: 200

```json
[
  {
    "associatedTokenAddress": "associatedTokenAddress_example",
    "mint": "mint_example",
    "name": "name_example",
    "symbol": "symbol_example",
    "tokenStandard": 0,
    "score": 0,
    "amount": "amount_example",
    "amountRaw": "amountRaw_example",
    "decimals": 0,
    "logo": "logo_example",
    "isVerifiedContract": true,
    "possibleSpam": true
  }
]
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/account/mainnet/kXB7FfzdrfZpAZEW3TZcp8a8CwQbsowa6BdfAHZ4gVs/tokens" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
