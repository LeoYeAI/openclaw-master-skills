# Get Token metadata

Get the global token metadata for a given network and contract (mint, standard, name, symbol, metaplex).

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/:address/metadata`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`So11111111111111111111111111111111111111112\` |

## Response Example

Status: default

```json
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
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/So11111111111111111111111111111111111111112/metadata" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
