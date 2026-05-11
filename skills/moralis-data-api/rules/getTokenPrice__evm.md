# Get ERC20 token price

Retrieve the current or historical price of an ERC20 token in the blockchain’s native currency and USD. Each token returned includes on-chain metadata, as well as off-chain metadata, logos, spam status and more. Additional options to exclude low-liquidity tokens and inactive tokens.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/erc20/:address/price`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address of the token contract | \`0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| exchange | string | No | The factory name or address of the token exchange | - |
| to_block | number | No | The block number from which the token price should be checked | - |
| include | string | No | This parameter is now deprecated as percentage change are included by default | \`-\` |
| max_token_inactivity | number | No | Exclude tokens inactive for more than the given amount of days | - |
| min_pair_side_liquidity_usd | number | No | Exclude tokens with liquidity less than the specified amount in USD. This parameter refers to the liquidity on a single side of the pair. | - |

## Response Example

Status: 200

Returns the price denominated in the blockchain's native token and USD for a given token contract address

```json
{
  "tokenName": "Kylin Network",
  "tokenSymbol": "KYL",
  "tokenLogo": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png",
  "tokenDecimals": "18",
  "usdPrice": 19.722370676,
  "usdPriceFormatted": "19.722370676",
  "24hrPercentChange": "-0.8842730258590583",
  "exchangeAddress": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
  "exchangeName": "Uniswap v3",
  "tokenAddress": "0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c",
  "toBlock": "16314545",
  "possibleSpam": "false",
  "verifiedContract": true,
  "pairAddress": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
  "pairTotalLiquidityUsd": "123.45",
  "usdPrice24h": 1,
  "usdPrice24hrUsdChange": -0.00008615972490000345,
  "usdPrice24hrPercentChange": -0.008615972490000345,
  "securityScore": 1
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/erc20/0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0/price?chain=eth&include=" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
