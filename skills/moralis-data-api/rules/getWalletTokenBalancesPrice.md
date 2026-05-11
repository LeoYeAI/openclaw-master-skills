# Get token balances with prices by wallet address

Fetch ERC20 and native token balances for a given wallet address, including their USD prices. Each token returned includes on-chain metadata, as well as off-chain metadata, logos, spam status and more. Additional options to exclude spam tokens, low-liquidity tokens and inactive tokens.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/tokens`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address from which token balances will be checked | \`0xcB1C1FdE09f811B294172696404e88E658659905\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| to_block | number | No | The block number up to which the balances will be checked. | - |
| token_addresses | array | No | The addresses to get balances for (optional) | - |
| exclude_spam | boolean | No | Exclude spam tokens from the result | - |
| exclude_unverified_contracts | boolean | No | Exclude unverified contracts from the result | - |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page). | - |
| limit | number | No | The desired page size of the result. | - |
| exclude_native | boolean | No | Exclude native balance from the result | - |
| max_token_inactivity | number | No | Exclude tokens inactive for more than the given amount of days | - |
| min_pair_side_liquidity_usd | number | No | Exclude tokens with liquidity less than the specified amount in USD. This parameter refers to the liquidity on a single side of the pair. | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.
- **cursor**: The cursor returned in the previous response (used for getting the next page).

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns token balances with prices for a specific address

```json
{
  "page": "2",
  "page_size": "100",
  "block_number": "13680123",
  "cursor": "cursor_example",
  "result": [
    {
      "token_address": "token_address_example",
      "name": "name_example",
      "symbol": "symbol_example",
      "logo": "logo_example",
      "thumbnail": "thumbnail_example",
      "decimals": 0,
      "balance": "balance_example",
      "possible_spam": true,
      "verified_contract": true,
      "usd_price": "usd_price_example",
      "usd_price_24hr_percent_change": "usd_price_24hr_percent_change_example",
      "usd_price_24hr_usd_change": "usd_price_24hr_usd_change_example",
      "usd_value_24hr_usd_change": "usd_value_24hr_usd_change_example",
      "usd_value": 0,
      "portfolio_percentage": 0,
      "balance_formatted": "balance_formatted_example",
      "native_token": true,
      "total_supply": "total_supply_example",
      "total_supply_formatted": "total_supply_formatted_example",
      "percentage_relative_to_total_supply": 0
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xcB1C1FdE09f811B294172696404e88E658659905/tokens?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
