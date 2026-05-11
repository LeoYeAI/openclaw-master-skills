# Get all swap related transactions (buy, sell)

Get all swap related transactions (buy, sell) for a specific token address.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/:address/swaps`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| address | string | Yes | The address to query | \`So11111111111111111111111111111111111111112\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| limit | number | No | The limit per page | - |
| cursor | string | No | The cursor to the next page | - |
| fromDate | string | No | The starting date (format in seconds or datestring accepted by momentjs) | - |
| toDate | string | No | The ending date (format in seconds or datestring accepted by momentjs) | - |
| order | string | No | The order of the results, in ascending (ASC) or descending (DESC). | \`DESC\` |
| transactionTypes | string | No | Transaction types to fetch. Possible values: 'buy','sell' or both separated by comma | \`buy,sell\` |

## Cursor/Pagination

- **limit**: The limit per page
- **cursor**: The cursor to the next page

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

```json
{
  "page": 1,
  "pageSize": 100,
  "cursor": "<cursor_from_previous_response>",
  "result": [
    {
      "transactionHash": "0xafc66b9b1802618f560be5244395f0fc0b95a1f1fdeee7a206acbb546c9e8a72",
      "transactionIndex": 5,
      "transactionType": "buy",
      "blockNumber": 12345678,
      "blockTimestamp": "2024-11-21T09:22:28.000Z",
      "subCategory": "ACCUMULATION",
      "walletAddress": "0x1c584a6baecb7c5d51caa0ef3a579e08bd49d4e5",
      "pairAddress": "0xdded227d71a096c6b5d87807c1b5c456771aaa94",
      "pairLabel": "USDC/WETH",
      "exchangeAddress": "0x1080ee857d165186af7f8d63e8ec510c28a6d1ea",
      "exchangeName": "Uniswap",
      "exchangeLogo": "https://logo.moralis.io/0xe708_0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f_769a0b766bd3d6d1830f0a95d7b3e313",
      "baseToken": "ETH",
      "quoteToken": "USDT",
      "bought": {
        "address": "0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f",
        "name": "Wrapped Ether",
        "symbol": "SYM",
        "logo": "https://example.com/logo-token1.png",
        "amount": "0.000014332429005002",
        "usdPrice": 3148.1828278180296,
        "usdAmount": 1230,
        "tokenType": "token1"
      },
      "sold": {
        "address": "0x176211869ca2b568f2a7d4ee941e073a821ee1ff",
        "name": "USDC",
        "symbol": "SYM",
        "logo": "https://example.com/logo-token2.png",
        "amount": "1000",
        "usdPrice": 0.9999999999999986,
        "usdAmount": -0.045138999999999936,
        "tokenType": "token0"
      },
      "baseQuotePrice": "0.01",
      "totalValueUsd": 1230
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/So11111111111111111111111111111111111111112/swaps?order=DESC&transactionTypes=buy%2Csell" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
