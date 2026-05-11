# Get new tokens by exchange

List newly added tokens on a specific exchange. Currently only supports tama.meme on Ronin.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/erc20/exchange/:exchangeName/new`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| exchangeName | string | Yes | The name of the exchange | \`tama.meme\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | Yes | The chain to query | \`eth\` |
| limit | number | No | The maximum number of items to return | - |
| cursor | string | No | The cursor to use for pagination | - |

## Cursor/Pagination

- **limit**: The maximum number of items to return
- **cursor**: The cursor to use for pagination

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns the new tokens for the specified exchange.

```json
{
  "total": 10,
  "page": 1,
  "page_size": 100,
  "cursor": "<cursor_from_previous_response>",
  "result": [
    {
      "tokenAddress": "0x6b175474e89094c44da98b954eedeac495271d0f",
      "name": "Test Token",
      "symbol": "TEST",
      "logo": "https://example.com/logo.png",
      "decimals": 18,
      "priceNative": "0.5",
      "priceUsd": "2.0",
      "liquidity": "500000",
      "fullyDilutedValuation": "2000000",
      "createdAt": "2023-01-20T09:39:55.818Z"
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/erc20/exchange/tama.meme/new?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
