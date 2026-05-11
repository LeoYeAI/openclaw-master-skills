# Get detailed profit and loss by wallet address

Get a detailed profit and loss breakdown by token for a given wallet, over a specified timeframe (`days`). Optionally filter by `token_addresses` for specific tokens.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/profitability`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The wallet address for which profitability is to be retrieved. | \`0xcB1C1FdE09f811B294172696404e88E658659905\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| days | string | No | Timeframe in days for which profitability is calculated, Options include 'all', '7', '30', '60', '90' default is 'all'. | - |
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| token_addresses | array | No | The token addresses list to filter the result with | - |

## Response Example

Status: 200

Successful response with profitability data.

```json
{
  "result": [
    {
      "token_address": "token_address_example",
      "avg_buy_price_usd": "avg_buy_price_usd_example",
      "avg_sell_price_usd": "avg_sell_price_usd_example",
      "total_usd_invested": "total_usd_invested_example",
      "total_tokens_sold": "total_tokens_sold_example",
      "total_tokens_bought": "total_tokens_bought_example",
      "total_sold_usd": "total_sold_usd_example",
      "avg_cost_of_quantity_sold": "avg_cost_of_quantity_sold_example",
      "count_of_trades": 0,
      "realized_profit_usd": "realized_profit_usd_example",
      "realized_profit_percentage": 0,
      "total_buys": 0,
      "total_sells": 0,
      "name": "name_example",
      "symbol": "symbol_example",
      "decimals": "decimals_example",
      "logo": "logo_example",
      "possible_spam": true
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xcB1C1FdE09f811B294172696404e88E658659905/profitability?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
