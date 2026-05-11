# Get multiple token metadata

Get multiple global token metadata for a given network and contract (mint, standard, name, symbol, metaplex).

## Method

POST

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/metadata`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |

## Body

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| addresses | array | No | - | \`So11111111111111111111111111111111111111112\` |

## Response Example

Status: default

```json
[
  {
    "mint": "mint_example",
    "standard": "standard_example",
    "name": "name_example",
    "symbol": "symbol_example",
    "logo": "logo_example",
    "decimals": "decimals_example",
    "tokenStandard": 0,
    "score": 0,
    "totalSupply": "totalSupply_example",
    "totalSupplyFormatted": "totalSupplyFormatted_example",
    "fullyDilutedValue": "fullyDilutedValue_example",
    "marketCap": "marketCap_example",
    "circulatingSupply": "circulatingSupply_example",
    "metaplex": {
      "metadataUri": "metadataUri_example",
      "masterEdition": true,
      "isMutable": true,
      "primarySaleHappened": 0,
      "sellerFeeBasisPoints": 0,
      "updateAuthority": "updateAuthority_example"
    },
    "links": {},
    "description": "description_example",
    "isVerifiedContract": true,
    "possibleSpam": true
  }
]
```

## Example (curl)

```bash
curl -X POST "https://solana-gateway.moralis.io/token/mainnet/metadata" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "addresses": [
    "So11111111111111111111111111111111111111112"
  ]
}'
```
