# Get swap transactions by wallet address

List all swap transactions (buy/sell) for a specific wallet. Optionally filter by `tokenAddress` for specific token swaps.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/swaps`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The wallet address token-transactions are to be retrieved for. | \`0xcB1C1FdE09f811B294172696404e88E658659905\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| tokenAddress | string | No | The token address to get transaction for (optional) | - |
| cursor | string | No | The cursor returned in the previous response (used for getting the next page). | - |
| limit | number | No | The desired page size of the result. | - |
| fromBlock | number | No | The minimum block number from which to get the token transactions
* Provide the param 'from_block' or 'from_date'
* If 'from_date' and 'from_block' are provided, 'from_block' will be used.
 | - |
| toBlock | string | No | The block number to get the token transactions from | - |
| fromDate | string | No | The start date from which to get the token transactions (format in seconds or datestring accepted by momentjs)
* Provide the param 'from_block' or 'from_date'
* If 'from_date' and 'from_block' are provided, 'from_block' will be used.
 | - |
| toDate | string | No | The end date from which to get the token transactions (format in seconds or datestring accepted by momentjs)
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |
| order | string (ASC, DESC) | No | The order of the result, in ascending (ASC) or descending (DESC) | \`DESC\` |
| transactionTypes | string | No | Array of transaction types. Allowed values are 'buy', 'sell'. | - |

## Cursor/Pagination

- **limit**: The desired page size of the result.
- **cursor**: The cursor returned in the previous response (used for getting the next page).

The response includes a **cursor** field for pagination. Use this cursor in the next request to get the next page of results.

## Response Example

Status: 200

Returns swap transactions by wallet address.

```json
{
  "page": "2",
  "page_size": "100",
  "cursor": "cursor_example",
  "result": [
    {
      "transactionHash": "0x2bfcba4715774420936669cd0ff2241d70e9abecab76c9db813602015b3134ad",
      "transactionIndex": 1,
      "transactionType": "buy",
      "blockTimestamp": "2022-02-22T00:00:00Z",
      "blockNumber": 21093423,
      "subCategory": "accumulation",
      "walletAddress": "0x2bfcba4715774420936669cd0ff2241d70e9abec",
      "walletAddressLabel": "Murad Wallet",
      "entity": "Murad",
      "entityLogo": "https://entities-logos.s3.us-east-1.amazonaws.com/murad.png",
      "pairAddress": "0x36a46dff597c5a444bbc521d26787f57867d2214",
      "pairLabel": "BRETT/WETH",
      "exchangeAddress": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
      "exchangeName": "Uniswap v2",
      "exchangeLogo": "https://entities-logos.s3.us-east-1.amazonaws.com/uniswap.png",
      "bought": {
        "address": "0x003dde3494f30d861d063232c6a8c04394b686ff",
        "name": "BRETT",
        "symbol": "BRETT",
        "logo": "https://cdn.moralis.io/tokens/0x0000000000085d4780b73119b644ae5ecd22b376.png",
        "amount": "14811.98",
        "usdPrice": 0.078634,
        "usdAmount": 1155.33
      },
      "sold": {
        "address": "0x003dde3494f30d861d063232c6a8c04394b686ff",
        "name": "BRETT",
        "symbol": "BRETT",
        "logo": "https://cdn.moralis.io/tokens/0x0000000000085d4780b73119b644ae5ecd22b376.png",
        "amount": "14811.98",
        "usdPrice": 0.078634,
        "usdAmount": 1155.33
      },
      "baseQuotePrice": "0.00003376480687",
      "totalValueUsd": 1165
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xcB1C1FdE09f811B294172696404e88E658659905/swaps?chain=eth&order=DESC" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
