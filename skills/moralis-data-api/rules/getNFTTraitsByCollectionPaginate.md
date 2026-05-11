# Get NFT traits by collection paginate

Fetch NFT traits for a contract with pagination for efficient navigation of large collections.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/nft/:address/traits/paginate`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address of the NFT contract | \`0x524cab2ec69124574082676e6f654a18df49a048\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page). | - |
| limit | number | No | The desired page size of the result. | - |
| order | string (ASC, DESC) | No | The order of the result, in ascending (ASC) or descending (DESC) | \`DESC\` |

## Cursor/Pagination

- **limit**: The desired page size of the result.
- **cursor**: The cursor returned in the previous response (used for getting the next page).

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns the traits

```json
{
  "page": "2",
  "page_size": "100",
  "cursor": "cursor_example",
  "result": [
    {
      "trait_type": "Background",
      "trait_value": "Lavendar",
      "count": 18593,
      "percentage": 85.8,
      "rarity_label": "Top 4% trait"
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/nft/0x524cab2ec69124574082676e6f654a18df49a048/traits/paginate?chain=eth&order=DESC" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
