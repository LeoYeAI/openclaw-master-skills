# Get OHLCV by pair address

Retrieve OHLCV (Open, High, Low, Close, Volume) candlestick data for a token pair.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/pairs/:address/ohlcv`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The pair address | \`0xa43fe16908251ee70ef74718545e4fe6c5ccec9f\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| timeframe | string | Yes | The timeframe | \`1h\` |
| currency | string | Yes | The currency | \`usd\` |
| fromDate | string | Yes | The starting date (format in seconds or datestring accepted by momentjs)
* Provide the param 'fromBlock' or 'fromDate'
* If 'fromDate' and 'fromBlock' are provided, 'fromBlock' will be used.
 | \`2025-01-01T10:00:00.000\` |
| toDate | string | Yes | The ending date (format in seconds or datestring accepted by momentjs)
* Provide the param 'toBlock' or 'toDate'
* If 'toDate' and 'toBlock' are provided, 'toBlock' will be used.
 | \`2025-01-02T10:00:00.000\` |
| limit | number | No | The number of results to return | - |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page) | - |

## Cursor/Pagination

- **limit**: The number of results to return
- **cursor**: The cursor returned in the previous response (used for getting the next page)

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns the OHLCV data.

```json
{
  "cursor": "cursor_example",
  "page": "2",
  "pairAddress": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
  "tokenAddress": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
  "timeframe": "30min",
  "currency": "usd",
  "result": [
    {
      "timestamp": "timestamp_example",
      "open": 0,
      "high": 0,
      "low": 0,
      "close": 0,
      "volume": 0,
      "trades": 0
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/pairs/0xa43fe16908251ee70ef74718545e4fe6c5ccec9f/ohlcv?chain=eth&timeframe=1h&currency=usd&fromDate=2025-01-01T10%3A00%3A00.000&toDate=2025-01-02T10%3A00%3A00.000" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
