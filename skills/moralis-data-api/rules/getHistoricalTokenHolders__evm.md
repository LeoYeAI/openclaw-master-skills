# Get timeseries holders data

Track changes in the holder base of an ERC20 token over time. Supports timeseries data for total holders as well as change metrics such as holder distribution and holder acquisition.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/erc20/:tokenAddress/holders/historical`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| tokenAddress | string | Yes | The token address | \`0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| fromDate | string | Yes | The starting date (format in seconds or datestring accepted by momentjs)
 | \`2025-01-01T10:00:00\` |
| toDate | string | Yes | The ending date (format in seconds or datestring accepted by momentjs)
 | \`2025-02-01T11:00:00\` |
| limit | number | No | The number of results to return | - |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page) | - |
| timeFrame | string | Yes | The time frame to group the data by | \`1d\` |

## Cursor/Pagination

- **limit**: The number of results to return
- **cursor**: The cursor returned in the previous response (used for getting the next page)

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns token

```json
{
  "page": "1",
  "pageSize": "100",
  "cursor": "cursor_example",
  "result": [
    {
      "timestamp": "2021-05-07T11:08:35.000Z",
      "totalHolders": "100",
      "netHolderChange": 0,
      "holderPercentChange": 0,
      "newHoldersByAcquisition": {
        "swap": "10",
        "transfer": "10",
        "airdrop": "10"
      },
      "holdersIn": {
        "whales": "100",
        "sharks": "100",
        "dolphins": "100",
        "fish": "100",
        "octopus": "100",
        "crabs": "100",
        "shrimps": "100"
      },
      "holdersOut": {
        "whales": "100",
        "sharks": "100",
        "dolphins": "100",
        "fish": "100",
        "octopus": "100",
        "crabs": "100",
        "shrimps": "100"
      }
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/erc20/0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0/holders/historical?chain=eth&fromDate=2025-01-01T10%3A00%3A00&toDate=2025-02-01T11%3A00%3A00&timeFrame=1d" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
