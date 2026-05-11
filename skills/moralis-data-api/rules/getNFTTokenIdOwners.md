# Get NFT owners by token ID

List wallets owning a specific NFT, defined by its contract and token ID.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/nft/:address/:token_id/owners`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address of the NFT contract | \`0x524cab2ec69124574082676e6f654a18df49a048\` |
| token_id | string | Yes | The ID of the token | \`1\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| format | string | No | The format of the token ID | \`decimal\` |
| limit | number | No | The desired page size of the result. | - |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page). | - |
| normalizeMetadata | boolean | No | Should normalized metadata be returned? | - |
| media_items | boolean | No | Should preview media data be returned? | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.
- **cursor**: The cursor returned in the previous response (used for getting the next page).

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns a collection of NFTs with their respective owners.

```json
{
  "status": "SYNCING",
  "page": "2",
  "page_size": "100",
  "cursor": "cursor_example",
  "result": [
    {
      "token_address": "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB",
      "token_id": "15",
      "contract_type": "ERC721",
      "owner_of": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
      "block_number": "88256",
      "block_number_minted": "88256",
      "token_uri": "token_uri_example",
      "metadata": "metadata_example",
      "amount": "1",
      "name": "CryptoKitties",
      "symbol": "RARI",
      "token_hash": "502cee781b0fb40ea02508b21d319ced",
      "rarity_rank": 21669,
      "rarity_percentage": 98,
      "rarity_label": "Top 98%",
      "last_token_uri_sync": "2021-02-24T00:47:26.647Z",
      "last_metadata_sync": "2021-02-24T00:47:26.647Z",
      "possible_spam": "false",
      "verified_collection": "false",
      "floor_price": "12345",
      "floor_price_usd": "12345.4899",
      "floor_price_currency": "eth",
      "last_sale": {
        "transaction_hash": "0x19e14f34b8f120c980f7ba05338d64c00384857fb9c561e2c56d0f575424a95c",
        "block_timestamp": "2023-04-04T15:59:11.000Z",
        "buyer_address": "0xcb1c1fde09f811b294172696404e88e658659905",
        "seller_address": "0x497a7dee2f13db161eb2fec060fa783cb041419f",
        "price": "7300000000000000",
        "price_formatted": "0.0073",
        "usd_price_at_sale": "13.61",
        "current_usd_value": "15.53",
        "token_address": "0xe8778996e096b39705c6a0a937eb587a1ebbda17",
        "token_id": "170",
        "payment_token": {
          "token_name": "Ether",
          "token_symbol": "ETH",
          "token_logo": "https://cdn.moralis.io/eth/0x.png",
          "token_decimals": "18",
          "token_address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        }
      }
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/nft/0x524cab2ec69124574082676e6f654a18df49a048/1/owners?chain=eth&format=decimal" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
