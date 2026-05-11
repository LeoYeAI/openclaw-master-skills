# Get native transactions by wallet

Get raw native transactions ordered by block number in descending order.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/:address`

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
| cursor | string | No | The cursor returned in the previous response (used for getting the next page). | - |
| order | string (ASC, DESC) | No | The order of the result, in ascending (ASC) or descending (DESC) | \`DESC\` |
| limit | number | No | The desired page size of the result. | - |
| include | string (internal_transactions) | No | If the result should contain the internal transactions. | \`-\` |

## Cursor/Pagination

- **limit**: The desired page size of the result.
- **cursor**: The cursor returned in the previous response (used for getting the next page).

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns a collection of native transactions.

```json
{
  "cursor": "cursor_example",
  "page": "2",
  "page_size": "100",
  "result": [
    {
      "hash": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
      "nonce": 326595425,
      "transaction_index": 25,
      "from_address_entity": "Opensea",
      "from_address_entity_logo": "https://opensea.io/favicon.ico",
      "from_address": "0xd4a3BebD824189481FC45363602b83C9c7e9cbDf",
      "from_address_label": "Binance 1",
      "to_address_entity": "Beaver Build",
      "to_address_entity_logo": "https://beaverbuild.com/favicon.ico",
      "to_address": "0xa71db868318f0a0bae9411347cd4a6fa23d8d4ef",
      "to_address_label": "Binance 2",
      "value": 650000000000000000,
      "gas": 6721975,
      "gas_price": 20000000000,
      "input": "input_example",
      "receipt_cumulative_gas_used": 1340925,
      "receipt_gas_used": 1340925,
      "receipt_contract_address": "0x1d6a4cf64b52f6c73f201839aded7379ce58059c",
      "receipt_root": "receipt_root_example",
      "receipt_status": 1,
      "transaction_fee": "0.00034",
      "block_timestamp": "2021-04-02T10:07:54.000Z",
      "block_number": 12526958,
      "block_hash": "0x0372c302e3c52e8f2e15d155e2c545e6d802e479236564af052759253b20fd86",
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
      ]
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/0xcB1C1FdE09f811B294172696404e88E658659905?chain=eth&order=DESC&include=" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
