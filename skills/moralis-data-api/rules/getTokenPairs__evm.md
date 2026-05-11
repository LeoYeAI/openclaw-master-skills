# Get token pairs by address

List supported trading pairs for a specific ERC20 token. Each pair returned includes price, liquidity, volume and more.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/erc20/:token_address/pairs`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| token_address | string | Yes | The address of the token | \`0x6982508145454ce325ddbe47a25d4ec3d2311933\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | Yes | The chain to query | \`eth\` |
| limit | number | No | The number of results to return | - |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page) | - |

## Cursor/Pagination

- **limit**: The number of results to return
- **cursor**: The cursor returned in the previous response (used for getting the next page)

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns the supported pairs for the token.

```json
{
  "pairs": [
    {
      "exchange_address": "exchange_address_example",
      "exchange_name": "exchange_name_example",
      "exchange_logo": "exchange_logo_example",
      "pair_label": "pair_label_example",
      "pair_address": "pair_address_example",
      "usd_price": 0,
      "usd_price_24hr": 0,
      "usd_price_24hr_percent_change": 0,
      "usd_price_24hr_usd_change": 0,
      "liquidity_usd": 0,
      "inactive_pair": true,
      "base_token": "base_token_example",
      "quote_token": "quote_token_example",
      "volume_24h_native": 0,
      "volume_24h_usd": 0,
      "pair": [
        {
          "token_address": "token_address_example",
          "token_name": "token_name_example",
          "token_symbol": "token_symbol_example",
          "token_logo": "token_logo_example",
          "token_decimals": "token_decimals_example",
          "pair_token_type": "pair_token_type_example",
          "liquidity_usd": "liquidity_usd_example"
        }
      ]
    }
  ],
  "cursor": "cursor_example",
  "page_size": "50",
  "page": "2"
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/erc20/0x6982508145454ce325ddbe47a25d4ec3d2311933/pairs?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
