# Get all swap related transactions (buy, sell, add liquidity & remove liquidity)

Get all swap related transactions (buy, sell, add liquidity & remove liquidity) for a specific pair address.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/pairs/:pairAddress/swaps`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| pairAddress | string | Yes | The address of the pair to query | \`Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| limit | number | No | The limit per page | - |
| cursor | string | No | The cursor to the next page | - |
| order | string | No | The order of items | - |
| fromDate | string | No | The starting date (format in seconds or datestring accepted by momentjs) | - |
| toDate | string | No | The ending date (format in seconds or datestring accepted by momentjs) | - |
| transactionTypes | string | No | Transaction types to fetch. Possible values: 'buy', 'sell', 'addLiquidity' or 'removeLiquidity' separated by comma | \`buy,sell,addLiquidity,removeLiquidity\` |

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
  "exchangeName": "Raydium AMM v4",
  "exchangeLogo": "https://entities-logos.s3.amazonaws.com/raydium.png",
  "exchangeAddress": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
  "pairLabel": "BREAD/SOL",
  "pairAddress": "ALeyWh7zN979ZHUWY6YTMJC8wWowzdYqi8RRPRyB3LAd",
  "baseToken": {
    "address": "madHpjRn6bd8t78Rsy7NuSuNwWa2HU8ByPobZprHbHv",
    "name": "MAD",
    "symbol": "MAD",
    "logo": "https://ipfs.io/ipfs/QmeCR6o1FrYjczPdDDDm4623usKksjj9BQLu89WqV8jFZW?filename=MAD.jpg",
    "decimals": "18"
  },
  "quoteToken": {
    "address": "madHpjRn6bd8t78Rsy7NuSuNwWa2HU8ByPobZprHbHv",
    "name": "MAD",
    "symbol": "MAD",
    "logo": "https://ipfs.io/ipfs/QmeCR6o1FrYjczPdDDDm4623usKksjj9BQLu89WqV8jFZW?filename=MAD.jpg",
    "decimals": "18"
  },
  "result": [
    {
      "transactionHash": "3o9NfCBWaDEb8JLJGdp8tfWwXURNokanCvUJf9A9f5nFqmZkRvWcfhkek4t47UhRDSGKHsSzi8MBusin8H7x7YYD",
      "transactionType": "sell",
      "transactionIndex": 250,
      "subCategory": "sellAll",
      "blockTimestamp": "2024-11-28T09:44:55.000Z",
      "blockNumber": 304108120,
      "walletAddress": "A8GVZWGMxRAouFQymPoMKx527JhHKrBRuqFx7NET4j22",
      "baseTokenAmount": "199255.444466200",
      "quoteTokenAmount": "0.007374998",
      "baseTokenPriceUsd": 0.000008794,
      "quoteTokenPriceUsd": 237.60336565,
      "baseQuotePrice": "0.0000000370127",
      "totalValueUsd": 1.752324346
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/pairs/Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE/swaps?transactionTypes=buy%2Csell%2CaddLiquidity%2CremoveLiquidity" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
