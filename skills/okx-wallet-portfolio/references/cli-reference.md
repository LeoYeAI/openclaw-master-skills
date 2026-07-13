# Onchain OS Portfolio — CLI Command Reference

Detailed parameter tables, return field schemas, and usage examples for all 9 portfolio commands.

## 1. onchainos portfolio chains

Get supported chains for balance queries. No parameters required.

```bash
onchainos portfolio chains
```

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `name` | String | Chain name (e.g., `"XLayer"`) |
| `logoUrl` | String | Chain logo URL |
| `shortName` | String | Chain short name (e.g., `"OKB"`) |
| `chainIndex` | String | Chain unique identifier (e.g., `"196"`) |

## 2. onchainos portfolio supported-chains

Get supported chains for portfolio PnL endpoints. No parameters required.

```bash
onchainos portfolio supported-chains
```

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `name` | String | Chain name (e.g., `"Ethereum"`) |
| `logoUrl` | String | Chain logo URL |
| `shortName` | String | Chain short name |
| `chainIndex` | String | Chain unique identifier (e.g., `"1"`) |

## 3. onchainos portfolio total-value

Get total asset value for a wallet address.

```bash
onchainos portfolio total-value --address <address> --chains <chains> [--asset-type <type>] [--exclude-risk <bool>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Wallet address |
| `--chains` | Yes | - | Chain names or IDs, comma-separated (e.g., `"xlayer,solana"` or `"196,501"`) |
| `--asset-type` | No | `"0"` | `0`=all, `1`=tokens only, `2`=DeFi only |
| `--exclude-risk` | No | `true` | `true`=filter risky tokens, `false`=include. Only ETH/BSC/SOL/BASE |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `totalValue` | String | Total asset value in USD |

## 4. onchainos portfolio all-balances

Get all token balances for a wallet address.

```bash
onchainos portfolio all-balances --address <address> --chains <chains> [--exclude-risk <value>] [--filter <value>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Wallet address |
| `--chains` | Yes | - | Chain names or IDs, comma-separated, max 50 |
| `--exclude-risk` | No | `"0"` | `0`=filter out risky tokens (default), `1`=include. Only ETH/BSC/SOL/BASE |
| `--filter` | No | `"0"` | `0`=default (filters risk/custom/passive tokens), `1`=return all tokens including risk tokens. Use `1` when scanning for security risks. |

**Return fields** (per token in `tokenAssets[]`):

| Field | Type | Description |
|---|---|---|
| `chainIndex` | String | Chain identifier |
| `tokenContractAddress` | String | Token contract address |
| `symbol` | String | Token symbol (e.g., `"OKB"`) |
| `balance` | String | Token balance in UI units (e.g., `"10.5"`) |
| `rawBalance` | String | Token balance in base units (e.g., `"10500000000000000000"`) |
| `tokenPrice` | String | Token price in USD |
| `isRiskToken` | Boolean | `true` if flagged as risky |

## 5. onchainos portfolio token-balances

Get specific token balances for a wallet address.

```bash
onchainos portfolio token-balances --address <address> --tokens <tokens> [--exclude-risk <value>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Wallet address |
| `--tokens` | Yes | - | Token list: `"chainIndex:tokenAddress"` pairs, comma-separated. Use empty address for native token (e.g., `"196:"` for native OKB). Max 20 items. |
| `--exclude-risk` | No | `"0"` | `0`=filter out (default), `1`=include |

**Return fields**: Same schema as `all-balances` (`tokenAssets[]`).

## 6. onchainos portfolio overview

Get wallet-level PnL summary and trading behaviour metrics.

```bash
onchainos portfolio overview --address <address> --chain <chain> [--time-frame <frame>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Wallet address |
| `--chain` | Yes | - | Chain name or ID (e.g., `ethereum`, `solana`, `xlayer`) |
| `--time-frame` | No | `7d` | `1d`, `3d`, `7d`, `1m`, `3m` |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `realizedPnlUsd` | String | Realized PnL in USD |
| `unrealizedPnlUsd` | String | Unrealized PnL in USD |
| `totalPnlUsd` | String | Total PnL in USD |
| `totalPnlPercent` | String | Total PnL as a percentage |
| `winRate` | String | Ratio of profitable sells (e.g., `"0.65"` = 65%) |
| `buyTxCount` | String | Number of buy transactions |
| `sellTxCount` | String | Number of sell transactions |
| `preferredMarketCap` | String | Most-traded market cap bucket (`1`-`5`, small->large) |
| `topPnlTokenList[]` | Array | Top performing tokens in the period |

## 7. onchainos portfolio dex-history

Get wallet DEX transaction history with cursor pagination.

```bash
onchainos portfolio dex-history --address <address> --chain <chain> [--limit <n>] [--cursor <cursor>] [--token <address>] [--tx-type <types>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Wallet address |
| `--chain` | Yes | - | Chain name or ID |
| `--limit` | No | `20` | Page size (1-100) |
| `--cursor` | No | - | Pagination cursor from previous response (omit for first page) |
| `--token` | No | - | Filter by token contract address |
| `--tx-type` | No | all | Transaction type(s), comma-separated: `1`=buy, `2`=sell, `3`=transfer-in, `4`=transfer-out, `0`=all |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `cursor` | String | Next-page cursor (empty when no more pages) |
| `historyList[]` | Array | Transaction records |
| `historyList[].type` | String | Transaction type (`1`-`4`) |
| `historyList[].timestamp` | String | Transaction time (Unix ms) |
| `historyList[].tokenContractAddress` | String | Token involved |

## 8. onchainos portfolio recent-pnl

Get paginated list of recent per-token PnL records.

```bash
onchainos portfolio recent-pnl --address <address> --chain <chain> [--limit <n>] [--cursor <cursor>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Wallet address |
| `--chain` | Yes | - | Chain name or ID |
| `--limit` | No | `20` | Page size (1-100) |
| `--cursor` | No | - | Pagination cursor from previous response |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `cursor` | String | Next-page cursor (empty when no more pages) |
| `pnlList[]` | Array | Token PnL records |
| `pnlList[].tokenSymbol` | String | Token symbol |
| `pnlList[].tokenContractAddress` | String | Token contract address |
| `pnlList[].realizedPnl` | String | Realized PnL in USD |
| `pnlList[].unrealizedPnl` | String | Unrealized PnL in USD |
| `pnlList[].totalPnl` | String | Total PnL in USD |
| `pnlList[].buyTxCount` | String | Buy transaction count |
| `pnlList[].sellTxCount` | String | Sell transaction count |
| `pnlList[].tokenBalanceAmount` | String | Current token amount held |
| `pnlList[].lastActiveTimestamp` | String | Last activity timestamp (Unix ms) |

## 9. onchainos portfolio token-pnl

Get latest PnL snapshot for a specific token in a wallet.

```bash
onchainos portfolio token-pnl --address <address> --chain <chain> --token <token>
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Wallet address |
| `--chain` | Yes | - | Chain name or ID |
| `--token` | Yes | - | Token contract address |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `tokenSymbol` | String | Token symbol |
| `tokenContractAddress` | String | Token contract address |
| `realizedPnl` | String | Realized PnL in USD |
| `unrealizedPnl` | String | Unrealized PnL in USD |
| `totalPnl` | String | Total PnL in USD |
| `buyAvgPrice` | String | Average buy price in USD |
| `sellAvgPrice` | String | Average sell price in USD |
| `buyTxCount` | String | Buy transaction count |
| `sellTxCount` | String | Sell transaction count |
| `tokenBalance` | String | Current position value in USD |
| `tokenBalanceAmount` | String | Current token amount (`"0"` = fully closed position) |
| `lastActiveTimestamp` | String | Last activity timestamp (Unix ms) |

## Input / Output Examples

**User says:** "Check my wallet total assets on XLayer and Solana"

```bash
onchainos portfolio total-value --address 0xYourWallet --chains "xlayer,solana"
# -> Display: Total assets $12,345.67
```

**User says:** "Show all tokens in my wallet"

```bash
onchainos portfolio all-balances --address 0xYourWallet --chains "xlayer,solana,ethereum"
# -> Display:
#   OKB:  10.5 ($509.25)
#   USDC: 2,000 ($2,000.00)
#   USDT: 1,500 ($1,500.00)
#   ...
```

**User says:** "Only check USDC and native OKB balances on XLayer"

```bash
onchainos portfolio token-balances --address 0xYourWallet --tokens "196:,196:0x74b7f16337b8972027f6196a17a631ac6de26d22"
# -> Display: OKB: 10.5 ($509.25), USDC: 2,000 ($2,000.00)
```

**User says:** "Show my PnL on Ethereum for the last month"

```bash
onchainos portfolio overview --address 0xYourWallet --chain ethereum --time-frame 1m
# -> Display: Total PnL $+1,234.56 | Win rate: 65% | Buys: 42 | Sells: 28
```

**User says:** "What tokens did I buy on Ethereum recently?"

```bash
onchainos portfolio dex-history --address 0xYourWallet --chain ethereum --tx-type 1 --limit 20
# -> Display: list of buy transactions with token, amount, timestamp
```

**User says:** "How much profit have I made on USDC on Ethereum?"

```bash
onchainos portfolio token-pnl \
  --address 0xYourWallet \
  --chain ethereum \
  --token 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48
# -> Display: Realized PnL $+500.00 | Unrealized $+12.50 | Avg buy $1.00 | Avg sell $1.001
```
