# Get ERC20 token transfers by contract address

Get all ERC20 token transfers for a contract, ordered by block number (newest first).

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/erc20/:address/transfers`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address of the token contract | \`0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| from_block | number | No | The minimum block number from which to get the transfers
* Provide the param 'from_block' or 'from_date'
* If 'from_date' and 'from_block' are provided, 'from_block' will be used.
 | - |
| to_block | number | No | The maximum block number from which to get the transfers.
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |
| from_date | string | No | The start date from which to get the transfers (format in seconds or datestring accepted by momentjs)
* Provide the param 'from_block' or 'from_date'
* If 'from_date' and 'from_block' are provided, 'from_block' will be used.
 | - |
| to_date | string | No | Get transfers up until this date (format in seconds or datestring accepted by momentjs)
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |
| limit | number | No | The desired page size of the result. | - |
| order | string (ASC, DESC) | No | The order of the result, in ascending (ASC) or descending (DESC) | \`DESC\` |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page). | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.
- **cursor**: The cursor returned in the previous response (used for getting the next page).

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns a collection of token contract transactions.

```json
{
  "page": "2",
  "page_size": "100",
  "cursor": "cursor_example",
  "result": [
    {
      "token_name": "Tether USD",
      "token_symbol": "USDT",
      "token_logo": "cdn.moralis.io/325/large/Tether-logo.png?1598003707",
      "token_decimals": "6",
      "transaction_hash": "0x2d30ca6f024dbc1307ac8a1a44ca27de6f797ec22ef20627a1307243b0ab7d09",
      "address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
      "block_timestamp": "2021-04-02T10:07:54.000Z",
      "block_number": 12526958,
      "block_hash": "0x0372c302e3c52e8f2e15d155e2c545e6d802e479236564af052759253b20fd86",
      "to_address_entity": "Beaver Build",
      "to_address_entity_logo": "https://beaverbuild.com/favicon.ico",
      "to_address": "0x62AED87d21Ad0F3cdE4D147Fdcc9245401Af0044",
      "to_address_label": "Binance 2",
      "from_address_entity": "Opensea",
      "from_address_entity_logo": "https://opensea.io/favicon.ico",
      "from_address": "0xd4a3BebD824189481FC45363602b83C9c7e9cbDf",
      "from_address_label": "Binance 1",
      "value": 650000000000000000,
      "transaction_index": 12,
      "log_index": 2,
      "possible_spam": "false",
      "verified_contract": "false"
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/erc20/0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0/transfers?chain=eth&order=DESC" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
