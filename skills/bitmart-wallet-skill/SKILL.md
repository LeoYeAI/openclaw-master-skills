---
name: bitmart-wallet-ai
description: "BitMart Web3 Wallet Skills (12 endpoints): Token Search, Chain Details, Token Info, K-Line Chart, Hot Token Ranking, xStock Ranking, Smart Money P&L Ranking, Smart Money Address Analysis/Holdings/Transaction History, Address Balance, Address Recent Transactions, Swap Quote, Batch Price. All APIs do not require API Key. Use when users ask about token prices, market data, smart money tracking, asset queries, recent transactions, or token swap quotes."
homepage: "https://www.bitmart.com"
metadata: {"author":"bitmart","version":"2026.3.17","updated":"2026-03-17"}
---

# BitMart Web3 Wallet AI Skills

This document describes the BitMart Web3 Wallet capabilities exposed as AI skills.

## Supported Chains

| chainId | Chain | Native Coin Symbol |
|---------|-------|-------------------|
| 2001 | Solana | SOL |
| 2002 | BSC (BNB Smart Chain) | BNB |
| 2003 | Ethereum | ETH |
| 2004 | Arbitrum | ETH |
| 2007 | Base | ETH |

## API Overview

- **Base URL**: `https://api-cloud.bitmart.com`
- **Authentication**: No API Key required, send HTTP requests directly
- **Request Method**: POST, JSON body
- **Response Format**: `{ "success": bool, "code": "string", "message": "string", "data": ... }`
- **Request Limit**: 15 requests per second per IP，or you would be rate limited

| Endpoint | Path | Description |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------------ |
| token-search | `/web3/chain-web3-base-data-maintainer/v1/token/search` | Fuzzy search tokens by name or symbol |
| chain-detail | `/web3/chain-web3-base-data-maintainer/v1/chain/by-chainId` | Query chain details by platform chain ID |
| token-info | `/web3/chain-web3-base-data-maintainer/v1/token/query/by/token-id` | Get token details by platform token ID |
| kline | `/web3/chain-web3-market/v1/api/market/kline/history` | Token K-line data (Solana only) |
| hot-ranking | `/web3/chain-web3-market/v1/api/market/trending/hot` | Hot token trending ranking |
| xstock-ranking | `/web3/chain-web3-market/v1/api/market/rank/xstocks` | US stock mapped token ranking |
| smart-money-rank | `/web3/chain-web3-smart-money/v1/api/smart-money/list` | Smart money 7-day P&L ranking |
| smart-money-info | `/web3/chain-web3-smart-money/v1/api/smart-money/info` | Smart money address analysis, holdings and transaction history |
| address-balance | `/web3/chain-web3-assetmanager/v1/eoa/balance/list` | Address token balance list |
| address-recent | `/web3/chain-web3-data-platform/evm/v2/transaction/address-recent` | Address recent transactions (grouped by date) |
| swap-quote | `/web3/chain-web3-price/api/v1/token/price/swap-quote` | Token Swap quote (quote only) |
| batch-price | `/web3/chain-web3-price/api/v1/token/price/batch` | Batch query token prices |

---

## Core Rules

### 1. Token Chain Dependency Rule

Tokens with the same symbol on different chains are **different tokens** (e.g., USDT-ETH ≠ USDT-BSC ≠ USDT-SOL), with different contract addresses, liquidity pools, and markets.

### 2. Swap Compatibility Rule

Two tokens can be swapped only if:
- Both tokens are on the **same chain**
- Or one is the native token and the other is a contract token on the same chain

**Cross-chain Swap is not supported.**

### 3. Token Resolution Workflow

All endpoints requiring token details must first get parameters through the following workflow:

```
User Input → token-search → token-info → Target Endpoint
```

**Never hardcode or guess token addresses, chainId, or decimal places.**

### 4. Native Token Address Handling (Important)

This is how different endpoints handle native token addresses:

#### contract field returned by token-info

| chainId | Chain | contract value |
|---------|-------|----------------|
| 2001 | Solana | `So11111111111111111111111111111111111111111` |
| 2002 | BSC | `""` (empty) |
| 2003 | Ethereum | `""` (empty) |
| 2004 | Arbitrum | `""` (empty) |
| 2007 | Base | `""` (empty) |

#### tokenAddress field returned by address-balance

Native tokens on all chains return `""` (empty string).

#### tokenAddress parameter for swap-quote endpoint

| Chain | Input Method | API Return Value |
|-------|--------------|------------------|
| **Solana** | Must use `So11111111111111111111111111111111111111111` | Kept as is |
| **EVM Chains** (ETH/BSC/ARB/Base) | Pass `""` empty string | Converted to `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` |

**Key Conclusions:**
- When swapping native tokens on EVM chains, pass empty string `""` for `tokenAddress`
- When swapping native tokens on Solana, must pass `So11111111111111111111111111111111111111111` for `tokenAddress`

### 5. Address Balance Query

`chainId` is a **required parameter**. If the user does not specify a chain, must query all supported chains (2001-2004, 2007).

---

## Common Token Address Reference

### Native Tokens

| Chain | Token | Address |
|-------|-------|---------|
| Solana | SOL | `So11111111111111111111111111111111111111111` |
| EVM Chains General | Native Coin | `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` |

### Common Contract Tokens (Testnet)

| Chain | Token | Address |
|-------|-------|---------|
| Solana | USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| Solana | USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` |
| BSC | USDT | `0x55d398326f99059ff775485246999027b3197955` |
| BSC | USDC | `0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d` |
| Arbitrum | USDC | `0xaf88d065e77c8cc2239327c5edb3a432268e5831` |
| Base | USDC | `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913` |

---

## API Details

### token-search

Fuzzy search tokens by name or symbol.

**Request:**
```json
{
    "keyword": "TRUMP",
    "chainId": 2002
}
```

| Parameter | Type | Required | Description |
| ------- | ------ | -------- | --------------------------------------------------------- |
| keyword | string | Yes | Search keyword, matches token symbol and name |
| chainId | integer | No | Platform internal chain ID (2001=Solana, 2002=BSC, 2003=Ethereum, etc.)|

**Response Key Fields:**
- `tokenId`: Platform internal token ID (required by downstream endpoints)
- `chainId`: Platform internal chain ID
- `contract`: Token contract address
- `symbol`: Token symbol
- `tokenDecimal`: Token decimal places
- `isDeposit`/`isWithdraw`: Whether deposit/withdrawal is supported

---

### token-info

Get complete token details by platform internal token ID.

**Prerequisite:** First get `tokenId` from `token-search`.

**Request:**
```json
{
    "tokenId": "224987722"
}
```

| Parameter | Type | Required | Description |
| ------- | ------ | -------- | --------------------------------------- |
| tokenId | string | Yes | Internal token ID (from token-search) |

**Response Key Fields:**
- `tokenId`: Platform internal token ID
- `chainId`: Platform internal chain ID
- `contract`: Token contract address
- `tokenDecimal`: Token decimal places
- `isNativeToken`: Whether it's a native token (1=yes)
- `type`: Token type (e.g., spl-token)
- `name`: Token name
- `symbol`: Token symbol
- `tokenIcon`: Token icon URL
- `isWithdraw`: Whether withdrawal is supported (1=yes)
- `isDeposit`: Whether deposit is supported (1=yes)
- `status`: Token status
- `gasLimit`: Gas limit
- `contractOwner`: Contract owner address
- `source`: Token source (e.g., pump_dot_fun)
- `createdAt`: Token creation time (ISO 8601)
- `createTime`: Token creation timestamp (milliseconds)

---

### address-balance

Get token balance list for an address.

**Limitations:**
- Only supports platform-managed addresses and EOA wallet addresses
- Does not support external addresses or smart contract wallets
- Response does not contain symbol or balance_usd

**Request:**
```json
{
    "address": "0x4396e479fe8270487f301b7c5cc92e8cd59ef91a",
    "chainId": 2002,
    "pageIndex": 0,
    "pageSize": 100
}
```

| Parameter | Type | Required | Description |
| ------------ | ------- | -------- | --------------------------------------------- |
| address | string | Yes | Wallet address |
| chainId | integer | **Yes** | Platform internal chain ID (must iterate 2001-2004, 2007 for complete info) |
| pageIndex | integer | No | Page number, starting from 0 |
| pageSize | integer | No | Page size |

---

### address-recent

Get recent transactions for an address, grouped by date.

**Limitations:**
- Only supports platform-managed addresses and EOA wallet addresses
- Does not support external addresses or smart contract wallets

**Request:**
```json
{
    "addressChainPairs": [
        {
            "address": "2h4hhjuWxEo4uyzGAxzWvpdSotAozchjpfyefvVWvi8R",
            "tokenAddress": null,
            "chainId": "2001"
        }
    ],
    "tradeType": 0,
    "limit": "50"
}
```

| Parameter | Type | Required | Description |
| ------------ | ------- | -------- | --------------------------------------------- |
| addressChainPairs | array | **Yes** | Array of address-chain pairs to query |
| addressChainPairs[].address | string | **Yes** | Wallet address |
| addressChainPairs[].tokenAddress | string \| null | No | Token contract address filter. Pass `null` to query **all tokens** under the address (filtered by chainId). Pass a specific token address to filter for that token only. |
| addressChainPairs[].chainId | string | **Yes** | Platform internal chain ID (as string, e.g., "2001") |
| tradeType | integer | No | Trade type filter: 0=all, 1=send, 2=receive, 3=trade |
| limit | string | No | Max transactions per date group (e.g., "50") |

**Important Notes:**
- When `tokenAddress` is `null`, the API returns transactions for **all tokens** associated with the address on the specified chain.
- The API returns up to **the most recent 6 months** of data by default. There is no parameter to specify a custom date range.
- `chainId` is **required** for each address-chain pair. If the user does not specify a chain, the agent **must enumerate all supported chains** (2001–2004, 2007) and query each one separately.

**Response — Top-level:**

Array of date groups, each containing:

| Field | Description |
| ----------------- | -------------------------- |
| date | Date string (YYYY-MM-DD) |
| transactionList | Array of transactions for this date |

**Response — Transaction Fields (transactionList[]):**

| Field | Description |
| -------------- | -------------------------- |
| blockNumber | Block number |
| chainId | Platform internal chain ID |
| txHash | Transaction hash |
| transactionType | `"send"`, `"receive"`, or `"trade"` |
| txTime | Transaction timestamp (milliseconds) |
| from | Array of sender entries |
| to | Array of receiver entries |
| txStatus | `"success"` or `"fail"` |
| txFee | Transaction fee |
| txFeeUsd | Transaction fee (USD) |
| amountUsd | Transaction amount (USD) |
| confirmBlockNumber | Confirmation block number |
| orderId | Order ID |

**Response — Address Entry Fields (from[] / to[]):**

| Field | Description |
| -------------- | -------------------------- |
| address | Wallet address |
| amount | Token amount |
| amountUsd | Amount (USD) |
| asset | Token asset object (null if not applicable) |

**Response — Asset Fields (asset):**

| Field | Description |
| -------------- | -------------------------- |
| symbol | Token symbol |
| tokenAddress | Token contract address |
| tokenIcon | Token icon URL |
| chainIcon | Chain icon URL |

---

### swap-quote

Get token Swap price quote. **Quote only, does not execute transaction.**

**Prerequisite:** Get tokenId, contract, tokenDecimal, and chainId for both tokens from the token resolution workflow.

**Request:**
```json
{
    "tokenInAddress": "",
    "tokenOutAddress": "0x55d398326f99059ff775485246999027b3197955",
    "tokenInId": "2002",
    "tokenOutId": "1169983",
    "amountIn": 1,
    "tokenInDecimals": 18,
    "tokenOutDecimals": 18,
    "slippage": 0.1,
    "fromChainId": 2002,
    "toChainId": 2002
}
```

| Parameter | Type | Required | Description |
| ---------------- | ------- | -------- | --------------------------------------- |
| tokenInAddress | string | Yes | Source token contract address (see native token address handling rules) |
| tokenOutAddress | string | Yes | Target token contract address |
| tokenInId | string | Yes | Source token platform internal ID |
| tokenOutId | string | Yes | Target token platform internal ID |
| amountIn | number | Yes | Swap amount (defaults to 100 if not specified by user) |
| tokenInDecimals | integer | Yes | Source token decimal places |
| tokenOutDecimals | integer | Yes | Target token decimal places |
| slippage | number | Yes | Slippage tolerance (e.g., 0.1 = 10%) |
| fromChainId | integer | Yes | Source chain platform internal chain ID |
| toChainId | integer | Yes | Target chain platform internal chain ID (must be same as fromChainId) |

**Response Key Fields:**
- `amountIn`: Input amount
- `amountOut`: Expected output amount
- `tokenInPrice`: Source token price (USD)
- `tokenOutPrice`: Target token price (USD)
- `fee`: Transaction fee

> **Note:** If the swap-quote API returns an error, the possible reasons are: (1) the token pair or chain is not supported / no liquidity found, or (2) the API is rate-limited. In case of rate limiting, recommend the user to try again after 5 minutes.

---

### batch-price

Batch query token prices.

**Note:**
- For native tokens (e.g., SOL, BNB, ETH, ARB, BASE), use chain IDs (e.g., 2001, 2002, 2003, 2004, 2007) as `tokenIds`
- For contract tokens, use the specific tokenId (obtained via token-search first)

**Request:**
```json
{
    "tokenIds": [2001, 2002, 2003, 2004, 2007],
    "latestOnly": true
}
```

| Parameter | Type | Required | Description |
| ------------ | ------- | -------- | --------------------------------------------- |
| tokenIds | array | Yes | Platform internal chain ID array (2001=Solana, 2002=BSC, 2003=Ethereum, 2004=Arbitrum, 2007=Base) |
| latestOnly | boolean | No | Whether to return only latest price, default true |

**Response Key Fields:**
- `tokenId`: Platform internal chain ID
- `chainId`: Platform internal chain ID
- `baseToken`: Base token symbol
- `quoteToken`: Quote token (USD)
- `price`: Price (USD)
- `priceUsd`: Price (USD)
- `generateTime`: Price generation time

**Supported Tokens:**

| tokenId | chainId | Token Symbol | Token Name |
|---------|---------|--------------|------------|
| 2001 | 2001 | SOL | Solana |
| 2002 | 2002 | BNB | BNB |
| 2003 | 2003 | ETH | Ethereum |
| 2004 | 2004 | ARB | Arbitrum |
| 2007 | 2007 | BASE | Base |

---

### chain-detail

Query chain details by platform internal chain ID.

**Request:**
```json
{
    "chainId": 2001
}
```

| Parameter | Type | Required | Description |
| ------- | ------- | -------- | -------------------------- |
| chainId | integer | Yes | Platform internal chain ID |

**Response Contains Fields:**

| Field | Description |
| --------------------- | ------------------------------------------------------------ |
| chainId | Platform internal chain ID |
| networkChainId | Industry standard blockchain network chain ID (e.g., 501=Solana, 56=BSC, 1=Ethereum) |
| chainSeries | Chain series (e.g., SVM, EVM) |
| chainName | Full chain name |
| shortName | Chain short name (e.g., SOL) |
| exploreUrl | Block explorer URL |
| txUrl | Transaction explorer URL |
| addressUrl | Address explorer URL |
| depositConfirmations | Required deposit confirmations |
| withdrawConfirmations | Required withdrawal confirmations |
| status | Chain status |

---

### kline

Get token historical K-line data. **Only supports Solana chain tokens.**

**Request:**
```json
{
    "interval": "5m",
    "tokenAddress": "Cz5YvHHpU1e3dqDQJHVdjVi7VSqvhu21A1GvxcTHMpLM",
    "startTime": "1773307582",
    "endTime": "1773393982"
}
```

| Parameter | Type | Required | Description |
| ------------ | ------ | -------- | ------------------------------------------------------------ |
| interval | string | Yes | Candlestick period: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d |
| tokenAddress | string | Yes | Token contract address |
| startTime | string | Yes | Start timestamp (seconds) |
| endTime | string | Yes | End timestamp (seconds) |

---

### hot-ranking / xstock-ranking

Get hot token / US stock mapped token ranking.

**Request:**
```json
{
    "queryFields": [],
    "timezone": "5"
}
```

| Parameter | Type | Required | Description |
| ----------- | ------ | -------- | ---------------------------------------------------- |
| queryFields | array | No | Query field filter |
| timezone | string | Yes | Time window: 1=1min, 2=5min, 3=1hour, 4=4hours, 5=24hours |

**Response (each token in data.list[]):**

| Field | Description |
| -------------- | ----------------------------- |
| tokenId | Platform internal token ID |
| tokenSymbol | Token symbol |
| tokenName | Token name |
| tokenAddress | Token contract address |
| tokenIconUrl | Token icon URL |
| chainId | Platform internal chain ID |
| price | Current price (USD) |
| priceChange | Price change rate |
| priceChange24h | 24-hour price change rate |
| marketcap | Market cap |
| volume | Trading volume |
| liquidity | Liquidity |
| holders | Number of holder addresses |
| buy | Buy count |
| sell | Sell count |
| rank | Rank position |
| createAt | Token creation time |
| check | Audit/check status |
| source | Data source |
| prices | Historical price points array |

---

### smart-money-rank

Get smart money 7-day P&L ranking.

**All parameters are optional.** If omitted, returns default ranking.

**Request:**
```json
{
    "current": 1,
    "size": 20,
    "orderBy": "profit7d",
    "order": "desc",
    "filters": {
        "profitMin": 5,
        "profitMax": 50,
        "profitRateMin": 5,
        "profitRateMax": 50,
        "winRateMin": 50,
        "winRateMax": 100,
        "tradeCountMin": 10,
        "tradeCountMax": 200,
        "totalTradeAmountMin": 1000,
        "totalTradeAmountMax": 100000
    }
}
```

| Parameter | Type | Required | Description |
| --------------------------- | ------- | -------- | ------------------------------------------------------------ |
| current | integer | No | Page number, default 1 |
| size | integer | No | Page size, max 100 |
| orderBy | string | No | Sort field: profit7d, winRate7d, profitRate7d, tradeCount, totalTradeAmount, lastTradeTime |
| order | string | No | Sort direction: desc / asc |
| filters.profitMin | number | No | Minimum 7-day profit amount |
| filters.profitMax | number | No | Maximum 7-day profit amount |
| filters.profitRateMin | number | No | Minimum 7-day profit rate (%) |
| filters.profitRateMax | number | No | Maximum 7-day profit rate (%) |
| filters.winRateMin | number | No | Minimum 7-day win rate (%) |
| filters.winRateMax | number | No | Maximum 7-day win rate (%) |
| filters.tradeCountMin | integer | No | Minimum trade count |
| filters.tradeCountMax | integer | No | Maximum trade count |
| filters.totalTradeAmountMin | number | No | Minimum total trade amount (USD) |
| filters.totalTradeAmountMax | number | No | Maximum total trade amount (USD) |

**Response (each address in data.records[]):**

| Field | Description |
| -------------------- | ------------------------------------------------------------ |
| walletAddress | Smart money wallet address |
| rank | Rank position |
| profit7d | 7-day profit amount |
| profitRate7d | 7-day profit rate (%) |
| winRate7d | 7-day win rate (%) |
| tradeCount | Total trade count |
| buyCount | Buy count |
| sellCount | Sell count |
| totalTradeAmount | Total trade amount (USD) |
| avgBuyAmount | Average buy amount |
| lastTradeTime | Last trade timestamp |
| latestTradeToken | Latest trade token address |
| latestTradeTokenName | Latest trade token name |
| profitTrend7d | 7-day profit trend array (dailyProfit, dailyProfitRate per day) |
| bestProfitToken | Best profit token array (address, name, profitRate, profit) |
| chainId | Platform internal chain ID |
| follow | Whether current user follows this address |
| walletRemark | Wallet remark/tag |
| updateTime | Last update time |
| createTime | Record creation time |
| notify | Whether notifications are enabled |

---

### smart-money-info

Get smart money address analysis, holdings, and transaction history.

**Limitation:** walletAddress must be provided by the user.

**Request:**
```json
{
    "walletAddress": "As7HjL7dzzvbRbaD3WCun47robib2kmAKRXMvjHkSMB5"
}
```

| Parameter | Type | Required | Description |
| ------------- | ------ | -------- | -------------------------------------------------- |
| walletAddress | string | Yes | Smart money wallet address (must be provided by user) |

**Response — Top-level Fields:**

| Field | Description |
| ------------------ | ----------------------------------------- |
| walletAddress | Wallet address |
| walletBalance | Total wallet balance (USD) |
| walletSolBalance | SOL balance |
| follow | Whether current user follows this address |
| walletRemark | Wallet remark/tag |
| marketDistribution | Market distribution data |

**Response — Address Analysis Fields (profitInfo):**

| Field | Description |
| --------------------------------- | ------------------------ |
| profitInfo.profit7d | 7-day profit |
| profitInfo.profitRate7d | 7-day profit rate |
| profitInfo.winRate7d | 7-day win rate |
| profitInfo.tradeInfo | Trade info summary |
| profitInfo.topProfit | Top profit details |
| profitInfo.profitRateDistribution | Profit rate distribution |
| profitInfo.profitTrend7d | 7-day profit trend array |

**Response — Holdings Fields (proportion[]):**

| Field | Description |
| ----------------- | -------------------------- |
| tokenAddress | Token contract address |
| tokenName | Token name |
| tokenIcon | Token icon URL |
| tokenId | Platform internal token ID |
| chainId | Platform internal chain ID |
| quantity | Holding quantity |
| balance | Holding value (USD) |
| price | Current price |
| holdingPercentage | Holding percentage |
| priceChangeRate | Price change rate |

**Response — Transaction History Fields (tradeHistory[]):**

| Field | Description |
| -------------- | -------------------------- |
| tokenAddress | Token contract address |
| tokenSymbol | Token symbol |
| tokenIcon | Token icon |
| tokenId | Platform internal token ID |
| chainId | Platform internal chain ID |
| tradeDirection | BUY or SELL |
| tradeTime | Trade timestamp |
| quantity | Trade quantity |
| totalUSD | Trade amount (USD) |
| price | Execution price |
| txHash | Transaction hash |
| profit | Trade profit |

---

## About Tokens with Same Name

When the user-specified token is ambiguous and there are multiple tokens with exactly matching names, **you must ask the user** to confirm which token. Clearly state each token's chain name and token type.

---

## Other Rules

- Token Price Query: Query hot-ranking and batch-price endpoints sequentially. Use the first result that returns an exact match (symbol or name,chainId(if valid),tokenId(if valid) matches exactly). If neither returns an exact match, inform the user that the token price is not currently available.
- Must verify chainId matches before calling swap-quote
- If user does not specify swap amount, default amountIn = 100
- K-line data only supports Solana tokens
- Response data only includes platform-managed tokens and addresses
