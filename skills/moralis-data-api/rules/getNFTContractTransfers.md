# Get NFT transfers by contract address

Get NFT transfers for a contract, with options to filter by date, token, or other parameters.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/nft/:address/transfers`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address of the NFT contract | \`0x306b1ea3ecdf94ab739f1910bbda052ed4a9f949\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| from_block | number | No | The minimum block number from where to get the transfers
* Provide the param 'from_block' or 'from_date'
* If 'from_date' and 'from_block' are provided, 'from_block' will be used.
 | - |
| to_block | number | No | The maximum block number from where to get the transfers.
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |
| from_date | string | No | The date from where to get the transfers (format in seconds or datestring accepted by momentjs)
* Provide the param 'from_block' or 'from_date'
* If 'from_date' and 'from_block' are provided, 'from_block' will be used.
 | - |
| to_date | string | No | Get transfers up until this date (format in seconds or datestring accepted by momentjs)
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |
| format | string | No | The format of the token ID | \`decimal\` |
| include_prices | boolean | No | Should NFT last sale prices be included in the result? | - |
| limit | number | No | The desired page size of the result. | - |
| order | string (ASC, DESC) | No | The order of the result, in ascending (ASC) or descending (DESC) | \`DESC\` |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page). | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.
- **cursor**: The cursor returned in the previous response (used for getting the next page).

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns a collection of NFT transfers

```json
{
  "page": "2",
  "page_size": "100",
  "cursor": "cursor_example",
  "result": [
    {
      "token_address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
      "token_id": "15",
      "token_name": "Tether USD",
      "token_symbol": "USDT",
      "from_address_entity": "Opensea",
      "from_address_entity_logo": "https://opensea.io/favicon.ico",
      "from_address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
      "from_address_label": "Binance 1",
      "to_address_entity": "Beaver Build",
      "to_address_entity_logo": "https://beaverbuild.com/favicon.ico",
      "to_address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
      "to_address_label": "Binance 2",
      "value": "1000000000000000",
      "amount": "1",
      "contract_type": "ERC721",
      "block_number": "88256",
      "block_timestamp": "2021-06-04T16:00:15",
      "block_hash": "block_hash_example",
      "transaction_hash": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
      "transaction_type": "transaction_type_example",
      "transaction_index": 0,
      "log_index": 0,
      "operator": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
      "possible_spam": "false",
      "verified_collection": "false",
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
  ],
  "block_exists": true,
  "index_complete": true
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/nft/0x306b1ea3ecdf94ab739f1910bbda052ed4a9f949/transfers?chain=eth&format=decimal&order=DESC" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
