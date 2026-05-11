# Get the global metadata for a given contract

Gets the contract level metadata (mint, standard, name, symbol, metaplex) for the given contract

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/nft/:network/:address/metadata`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`So11111111111111111111111111111111111111112\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| mediaItems | boolean | No | Should return media items | - |

## Response Example

Status: 200

```json
{
  "mint": "mint_example",
  "address": "address_example",
  "standard": "standard_example",
  "name": "name_example",
  "symbol": "symbol_example",
  "tokenStandard": 0,
  "description": "description_example",
  "imageOriginalUrl": "imageOriginalUrl_example",
  "externalUrl": "externalUrl_example",
  "metadataOriginalUrl": "metadataOriginalUrl_example",
  "totalSupply": "totalSupply_example",
  "metaplex": {
    "metadataUri": "metadataUri_example",
    "masterEdition": true,
    "isMutable": true,
    "primarySaleHappened": 0,
    "sellerFeeBasisPoints": 0,
    "updateAuthority": "updateAuthority_example"
  },
  "attributes": [
    {
      "traitType": "traitType_example",
      "value": {}
    }
  ],
  "contract": {
    "type": "type_example",
    "name": "name_example",
    "symbol": "symbol_example"
  },
  "collection": {
    "collectionAddress": "collectionAddress_example",
    "name": "name_example",
    "description": "description_example",
    "imageOriginalUrl": "imageOriginalUrl_example",
    "externalUrl": "externalUrl_example",
    "metaplexMint": "metaplexMint_example",
    "sellerFeeBasisPoints": 0
  },
  "firstCreated": {
    "mintTimestamp": 0,
    "mintBlockNumber": 0,
    "mintTransaction": "mintTransaction_example"
  },
  "creators": [
    {
      "address": "address_example",
      "share": 0,
      "verified": true
    }
  ],
  "properties": {},
  "possibleSpam": true
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/nft/mainnet/So11111111111111111111111111111111111111112/metadata" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
