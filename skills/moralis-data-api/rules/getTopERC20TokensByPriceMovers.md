# Get top ERC20 tokens by price movements (winners and losers)

Get top ERC20 tokens by price movements (winners and losers). Currently only supports Ethereum. For more flexibility, we recommend to use getFilteredTokens or getTopGainersTokens and getTopLosersTokens.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/market-data/erc20s/top-movers`

## Response Example

Status: 200

Returns an a list of ERC20 tokens with their price change

```json
{
  "gainers": [
    {
      "rank": 1,
      "token_name": "Wrapped Ether",
      "token_symbol": "WETH",
      "token_logo": "https://cdn.moralis.io/coins/images/2518/large/weth.png?1595348880",
      "token_decimals": "18",
      "contract_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
      "price_usd": "0.0285",
      "price_24h_percent_change": "0.0285",
      "price_7d_percent_change": "0.0285",
      "market_cap_usd": "0.0285"
    }
  ],
  "losers": [
    {
      "rank": 1,
      "token_name": "Wrapped Ether",
      "token_symbol": "WETH",
      "token_logo": "https://cdn.moralis.io/coins/images/2518/large/weth.png?1595348880",
      "token_decimals": "18",
      "contract_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
      "price_usd": "0.0285",
      "price_24h_percent_change": "0.0285",
      "price_7d_percent_change": "0.0285",
      "market_cap_usd": "0.0285"
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/market-data/erc20s/top-movers" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
