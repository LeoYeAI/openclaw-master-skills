# Get wallet net worth

Calculate the total net worth of a wallet in USD, with options to exclude spam tokens for accuracy. Options to query cross-chain using the `chains` parameter, as well as additional options to exclude spam tokens, low-liquidity tokens and inactive tokens.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/net-worth`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The wallet address | \`0xcB1C1FdE09f811B294172696404e88E658659905\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chains | array | No | The chains to query | - |
| exclude_spam | boolean | No | Exclude spam tokens from the result | \`true\` |
| exclude_unverified_contracts | boolean | No | Exclude unverified contracts from the result | \`true\` |
| max_token_inactivity | number | No | Exclude tokens inactive for more than the given amount of days | \`1\` |
| min_pair_side_liquidity_usd | number | No | Exclude tokens with liquidity less than the specified amount in USD. This parameter refers to the liquidity on a single side of the pair. | \`1000\` |

## Response Example

Status: 200

Returns the net worth of a wallet in USD

```json
{
  "total_networth_usd": "3879851.41",
  "chains": [
    {
      "chain": "eth",
      "native_balance": "1085513807021271641379",
      "native_balance_formatted": "1085.513807021271641379",
      "native_balance_usd": "3158392.48",
      "token_balance_usd": "721458.93",
      "networth_usd": "3879851.41"
    }
  ],
  "unsupported_chain_ids": [],
  "unavailable_chains": [
    {
      "chain_id": "0x1"
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xcB1C1FdE09f811B294172696404e88E658659905/net-worth?exclude_spam=true&exclude_unverified_contracts=true&max_token_inactivity=1&min_pair_side_liquidity_usd=1000" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
