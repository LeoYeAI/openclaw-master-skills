# Get the complete decoded transaction history of a wallet

Get the complete decoded transaction history for a given wallet. All transactions are parsed, decoded, categorized and summarized into human-readable records.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/history`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address of the wallet | \`0xcB1C1FdE09f811B294172696404e88E658659905\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| from_block | number | No | The minimum block number from which to get the transactions
* Provide the param 'from_block' or 'from_date'
* If 'from_date' and 'from_block' are provided, 'from_block' will be used.
 | - |
| to_block | number | No | The maximum block number from which to get the transactions.
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |
| from_date | string | No | The start date from which to get the transactions (format in seconds or datestring accepted by momentjs)
* Provide the param 'from_block' or 'from_date'
* If 'from_date' and 'from_block' are provided, 'from_block' will be used.
 | - |
| to_date | string | No | Get the transactions up to this date (format in seconds or datestring accepted by momentjs)
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |
| include_internal_transactions | boolean | No | If the result should contain the internal transactions. | - |
| nft_metadata | boolean | No | If the result should contain the nft metadata. | - |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page). | - |
| order | string (ASC, DESC) | No | The order of the result, in ascending (ASC) or descending (DESC) | \`DESC\` |
| limit | number | No | The desired page size of the result. | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.
- **cursor**: The cursor returned in the previous response (used for getting the next page).

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns wallet history of a wallet address

```json
{
  "page": "2",
  "page_size": "100",
  "cursor": "cursor_example",
  "result": [
    {
      "hash": "0x1ed85b3757a6d31d01a4d6677fc52fd3911d649a0af21fe5ca3f886b153773ed",
      "nonce": "1848059",
      "transaction_index": "108",
      "from_address_entity": "Opensea",
      "from_address_entity_logo": "https://opensea.io/favicon.ico",
      "from_address": "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0",
      "from_address_label": "Binance 1",
      "to_address_entity": "Beaver Build",
      "to_address_entity_logo": "https://beaverbuild.com/favicon.ico",
      "to_address": "0x003dde3494f30d861d063232c6a8c04394b686ff",
      "to_address_label": "Binance 2",
      "value": "115580000000000000",
      "gas": "30000",
      "gas_price": "52500000000",
      "input": "0x",
      "receipt_cumulative_gas_used": "4923073",
      "receipt_gas_used": "21000",
      "receipt_contract_address": "0x9869524fd160fe3adda6218883b6526c0977d3a5",
      "receipt_status": "1",
      "transaction_fee": "0.00000000000000063",
      "block_timestamp": "2021-05-07T11:08:35.000Z",
      "block_number": "12386788",
      "block_hash": "0x9b559aef7ea858608c2e554246fe4a24287e7aeeb976848df2b9a2531f4b9171",
      "internal_transactions": [
        {
          "transaction_hash": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
          "block_number": 12526958,
          "block_hash": "0x0372c302e3c52e8f2e15d155e2c545e6d802e479236564af052759253b20fd86",
          "type": "CALL",
          "from": "0xd4a3BebD824189481FC45363602b83C9c7e9cbDf",
          "to": "0xa71db868318f0a0bae9411347cd4a6fa23d8d4ef",
          "value": "650000000000000000",
          "gas": "6721975",
          "gas_used": "6721975",
          "input": "0x",
          "output": "0x",
          "error": "Execution reverted"
        }
      ],
      "category": "category_example",
      "contract_interactions": [],
      "possible_spam": "false",
      "method_label": "transfer",
      "summary": "transfer",
      "nft_transfers": [
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
          "transaction_type": "transaction_type_example",
          "log_index": 0,
          "operator": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
          "possible_spam": "false",
          "verified_collection": "false",
          "direction": "outgoing",
          "collection_logo": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png",
          "collection_banner_image": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png"
        }
      ],
      "erc20_transfers": [
        {
          "token_name": "Tether USD",
          "token_symbol": "USDT",
          "token_logo": "https://cdn.moralis.io/images/325/large/Tether-logo.png?1598003707",
          "token_decimals": "6",
          "address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
          "block_timestamp": "2021-04-02T10:07:54.000Z",
          "to_address_entity": "Beaver Build",
          "to_address_entity_logo": "https://beaverbuild.com/favicon.ico",
          "to_address": "0x62AED87d21Ad0F3cdE4D147Fdcc9245401Af0044",
          "to_address_label": "Binance 2",
          "from_address_entity": "Opensea",
          "from_address_entity_logo": "https://opensea.io/favicon.ico",
          "from_address": "0xd4a3BebD824189481FC45363602b83C9c7e9cbDf",
          "from_address_label": "Binance 1",
          "value": 650000000000000000,
          "value_formatted": "1.033",
          "log_index": 2,
          "possible_spam": "false",
          "verified_contract": "false"
        }
      ],
      "native_transfers": [
        {
          "from_address_entity": "Opensea",
          "from_address_entity_logo": "https://opensea.io/favicon.ico",
          "from_address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
          "from_address_label": "Binance 1",
          "to_address_entity": "Beaver Build",
          "to_address_entity_logo": "https://beaverbuild.com/favicon.ico",
          "to_address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
          "to_address_label": "Binance 2",
          "value": "1000000000000000",
          "value_formatted": "0.1",
          "direction": "outgoing",
          "internal_transaction": "false",
          "token_symbol": "ETH",
          "token_logo": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png"
        }
      ],
      "logs": [
        {
          "log_index": "273",
          "transaction_hash": "0xdd9006489e46670e0e85d1fb88823099e7f596b08aeaac023e9da0851f26fdd5",
          "transaction_index": "204",
          "address": "0x3105d328c66d8d55092358cf595d54608178e9b5",
          "data": "0x00000000000000000000000000000000000000000000000de05239bccd4d537400000000000000000000000000024dbc80a9f80e3d5fc0a0ee30e2693781a443",
          "topic0": "0x2caecd17d02f56fa897705dcc740da2d237c373f70686f4e0d9bd3bf0400ea7a",
          "topic1": "0x000000000000000000000000031002d15b0d0cd7c9129d6f644446368deae391",
          "topic2": "0x000000000000000000000000d25943be09f968ba740e0782a34e710100defae9",
          "topic3": null,
          "block_timestamp": "2021-05-07T11:08:35.000Z",
          "block_number": "12386788",
          "block_hash": "0x9b559aef7ea858608c2e554246fe4a24287e7aeeb976848df2b9a2531f4b9171",
          "decoded_event": {
            "signature": "Transfer(address,address,uint256)",
            "label": "Transfer",
            "type": "event",
            "params": [
              {
                "name": "from",
                "value": "0x26C5011483Add49801eA8E3Ee354fE013895aCe5",
                "type": "address"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xcB1C1FdE09f811B294172696404e88E658659905/history?chain=eth&order=DESC" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
