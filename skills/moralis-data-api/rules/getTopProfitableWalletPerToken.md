# Get top traders for a given ERC20 token

List the most profitable wallets that have traded a specific ERC20 token.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/erc20/:address/top-gainers`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The ERC20 token address. | \`0x6982508145454ce325ddbe47a25d4ec3d2311933\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| days | string | No | Timeframe in days for which profitability is calculated, Options include 'all', '7', '30' default is 'all'. | - |
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |

## Response Example

Status: 200

Successful response with top profitable wallets.

```json
{
  "name": "Kylin Network",
  "symbol": "KYL",
  "decimals": 18,
  "logo": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png",
  "possible_spam": "false",
  "result": [
    {
      "avg_buy_price_usd": "avg_buy_price_usd_example",
      "avg_cost_of_quantity_sold": "avg_cost_of_quantity_sold_example",
      "avg_sell_price_usd": "avg_sell_price_usd_example",
      "count_of_trades": 0,
      "realized_profit_percentage": 0,
      "realized_profit_usd": "realized_profit_usd_example",
      "total_sold_usd": "total_sold_usd_example",
      "total_tokens_bought": "total_tokens_bought_example",
      "total_tokens_sold": "total_tokens_sold_example",
      "total_usd_invested": "total_usd_invested_example",
      "address": "address_example"
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/erc20/0x6982508145454ce325ddbe47a25d4ec3d2311933/top-gainers?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
