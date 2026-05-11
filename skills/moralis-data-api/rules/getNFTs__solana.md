# Gets NFTs owned by the given address

Gets NFTs owned by the given address

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/account/:network/:address/nft`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`kXB7FfzdrfZpAZEW3TZcp8a8CwQbsowa6BdfAHZ4gVs\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| nftMetadata | boolean | No | Should return the full NFT metadata | - |
| mediaItems | boolean | No | Should return media items | - |
| excludeSpam | boolean | No | Should exclude spam NFTs | - |
| includeFungibleAssets | boolean | No | Should include fungible assets (tokenStandard:1) | - |

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
    "amount": "amount_example",
    "amountRaw": "amountRaw_example",
    "decimals": 0,
    "possibleSpam": true,
    "totalSupply": "totalSupply_example",
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
    "properties": {}
  }
]
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/account/mainnet/kXB7FfzdrfZpAZEW3TZcp8a8CwQbsowa6BdfAHZ4gVs/nft" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
