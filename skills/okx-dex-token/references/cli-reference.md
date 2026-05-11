# Onchain OS DEX Token — CLI Command Reference

Detailed parameter tables, return field schemas, and usage examples for all 10 token commands.

## 1. onchainos token search

Search for tokens by name, symbol, or contract address.

```bash
onchainos token search --query <query> [--chains <chains>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--query` | Yes | - | Keyword: token name, symbol, or contract address |
| `--chains` | No | `"1,501"` | Chain names or IDs, comma-separated (e.g., `"ethereum,solana"` or `"196,501"`) |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `tokenContractAddress` | String | Token contract address |
| `tokenSymbol` | String | Token symbol (e.g., `"ETH"`) |
| `tokenName` | String | Token full name |
| `tokenLogoUrl` | String | Token logo image URL |
| `chainIndex` | String | Chain identifier |
| `decimal` | String | Token decimals (e.g., `"18"`) |
| `price` | String | Current price in USD |
| `change` | String | 24-hour price change percentage |
| `marketCap` | String | Market capitalization in USD |
| `liquidity` | String | Liquidity in USD |
| `holders` | String | Number of token holders |
| `explorerUrl` | String | Block explorer URL for the token |
| `tagList.communityRecognized` | Boolean | `true` = listed on Top 10 CEX or community verified |

## 2. onchainos token info

Get token basic info (name, symbol, decimals, logo).

```bash
onchainos token info --address <address> [--chain <chain>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Token contract address |
| `--chain` | No | `ethereum` | Chain name |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `tokenName` | String | Token full name |
| `tokenSymbol` | String | Token symbol (e.g., `"ETH"`) |
| `tokenLogoUrl` | String | Token logo image URL |
| `decimal` | String | Token decimals (e.g., `"18"`) |
| `tokenContractAddress` | String | Token contract address |
| `tagList.communityRecognized` | Boolean | `true` = listed on Top 10 CEX or community verified |

## 3. onchainos token price-info

Get detailed price info including market cap, liquidity, volume, and multi-timeframe price changes.

```bash
onchainos token price-info --address <address> [--chain <chain>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Token contract address |
| `--chain` | No | `ethereum` | Chain name |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `price` | String | Current price in USD |
| `time` | String | Timestamp (Unix milliseconds) |
| `marketCap` | String | Market capitalization in USD |
| `liquidity` | String | Total liquidity in USD |
| `circSupply` | String | Circulating supply |
| `holders` | String | Number of token holders |
| `tradeNum` | String | 24-hour trade count |
| `priceChange5M` | String | Price change percentage — last 5 minutes |
| `priceChange1H` | String | Price change percentage — last 1 hour |
| `priceChange4H` | String | Price change percentage — last 4 hours |
| `priceChange24H` | String | Price change percentage — last 24 hours |
| `volume5M` | String | Trading volume (USD) — last 5 minutes |
| `volume1H` | String | Trading volume (USD) — last 1 hour |
| `volume4H` | String | Trading volume (USD) — last 4 hours |
| `volume24H` | String | Trading volume (USD) — last 24 hours |
| `txs5M` | String | Transaction count — last 5 minutes |
| `txs1H` | String | Transaction count — last 1 hour |
| `txs4H` | String | Transaction count — last 4 hours |
| `txs24H` | String | Transaction count — last 24 hours |
| `maxPrice` | String | 24-hour highest price |
| `minPrice` | String | 24-hour lowest price |

## 4. onchainos token trending

Get trending / top tokens by various criteria.

```bash
onchainos token trending [--chains <chains>] [--sort-by <sort>] [--time-frame <frame>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--chains` | No | `"1,501"` | Chain names or IDs, comma-separated |
| `--sort-by` | No | `"5"` | Sort: `2`=price change, `5`=volume, `6`=market cap |
| `--time-frame` | No | `"4"` | Window: `1`=5min, `2`=1h, `3`=4h, `4`=24h |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `tokenSymbol` | String | Token symbol |
| `tokenContractAddress` | String | Token contract address |
| `tokenLogoUrl` | String | Token logo image URL |
| `chainIndex` | String | Chain identifier |
| `price` | String | Current price in USD |
| `change` | String | Price change percentage (for selected time frame) |
| `volume` | String | Trading volume in USD (for selected time frame) |
| `marketCap` | String | Market capitalization in USD |
| `liquidity` | String | Total liquidity in USD |
| `holders` | String | Number of token holders |
| `uniqueTraders` | String | Number of unique traders (for selected time frame) |
| `txsBuy` | String | Buy transaction count (for selected time frame) |
| `txsSell` | String | Sell transaction count (for selected time frame) |
| `txs` | String | Total transaction count (for selected time frame) |
| `firstTradeTime` | String | First trade timestamp (Unix milliseconds) |

## 5. onchainos token holders

Get token holder distribution (top 100), with optional tag filter.

```bash
onchainos token holders --address <address> [--chain <chain>] [--tag-filter <n>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Token contract address |
| `--chain` | No | `ethereum` | Chain name |
| `--tag-filter` | No | - | Filter by holder tag: 1=KOL, 2=Developer, 3=Smart Money, 4=Whale, 5=Fresh Wallet, 6=Insider, 7=Sniper, 8=Suspicious Phishing, 9=Bundler |

**Return fields** (top 100 holders):

| Field | Type | Description |
|---|---|---|
| `holderWalletAddress` | String | Holder wallet address |
| `holdAmount` | String | Token amount held |
| `holdPercent` | String | Percentage of total supply held |
| `nativeTokenBalance` | String | Native token (mainnet) balance |
| `boughtAmount` | String | Total buy quantity |
| `avgBuyPrice` | String | Average buy price (USD) |
| `totalSellAmount` | String | Total sell quantity |
| `avgSellPrice` | String | Average sell price (USD) |
| `totalPnlUsd` | String | Total PnL (USD) |
| `realizedPnlUsd` | String | Realized PnL (USD) |
| `unrealizedPnlUsd` | String | Unrealized PnL (USD) |
| `fundingSource` | String | Source of funding for the wallet |

## 6. onchainos token liquidity

Get top 5 liquidity pools for a token.

```bash
onchainos token liquidity --address <address> [--chain <chain>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Token contract address |
| `--chain` | No | `ethereum` | Chain name (e.g., `ethereum`, `base`, `bsc`) |

**Return fields** (array of pool objects):

| Field | Type | Description |
|---|---|---|
| `pool` | String | Pool name (e.g., `"Punch/SOL"`) |
| `protocolName` | String | Protocol name |
| `liquidityUsd` | String | Liquidity value in USD |
| `liquidityAmount` | Array | Liquidity amounts |
| `liquidityAmount[].tokenAmount` | String | Token amount in the liquidity pool |
| `liquidityAmount[].tokenSymbol` | String | Token symbol in the liquidity pool |
| `liquidityProviderFeePercent` | String | Liquidity provider fee percentage |
| `poolAddress` | String | Pool contract address |
| `poolCreator` | String | Pool creator address |

## 7. onchainos token hot-tokens

Get hot token list ranked by trending score or X/Twitter mentions (max 100 results).

```bash
onchainos token hot-tokens [--ranking-type <type>] [--chain <chain>] [--rank-by <field>] [--time-frame <frame>] [options]
```

**Core parameters**:

| Param | Required | Default | Description |
|---|---|---|---|
| `--ranking-type` | Yes | `"4"` | `4`=Trending (token score), `5`=Xmentioned (Twitter mentions) |
| `--chain` | No | all chains | Chain name (e.g., `solana`, `ethereum`). Omit for all chains |
| `--rank-by` | No | - | Sort field: `1`=price, `2`=price change, `3`=txs, `4`=unique traders, `5`=volume, `6`=market cap, `7`=liquidity, `8`=created time, `9`=OKX search count, `10`=holders, `11`=mention count, `12`=social score, `14`=net inflow, `15`=token score |
| `--time-frame` | No | - | Window: `1`=5min, `2`=1h, `3`=4h, `4`=24h |

**Filter parameters** (all optional):

| Param | Description |
|---|---|
| `--risk-filter` | Hide risky tokens (`true`/`false`, default: `true`) |
| `--stable-token-filter` | Filter stable coins (`true`/`false`, default: `true`) |
| `--project-id` | Protocol ID filter, comma-separated (e.g., `120596` for Pump.fun) |
| `--price-change-min` / `--price-change-max` | Price change % range (supports negative values, e.g., `--price-change-min -5`) |
| `--volume-min` / `--volume-max` | Volume range in USD |
| `--market-cap-min` / `--market-cap-max` | Market cap range in USD |
| `--liquidity-min` / `--liquidity-max` | Liquidity range in USD |
| `--transaction-min` / `--transaction-max` | Trade amount (tradeAmount) range |
| `--txs-min` / `--txs-max` | Transaction count (txs) range |
| `--unique-trader-min` / `--unique-trader-max` | Unique trader count range |
| `--holders-min` / `--holders-max` | Holder count range |
| `--inflow-min` / `--inflow-max` | Net inflow USD range |
| `--fdv-min` / `--fdv-max` | Fully diluted valuation range in USD |
| `--mentioned-count-min` / `--mentioned-count-max` | Mention count range (for Xmentioned ranking) |
| `--social-score-min` / `--social-score-max` | Social score range |
| `--top10-hold-percent-min` / `--top10-hold-percent-max` | Top-10 holder % range |
| `--dev-hold-percent-min` / `--dev-hold-percent-max` | Dev holding % range |
| `--bundle-hold-percent-min` / `--bundle-hold-percent-max` | Bundle holding % range |
| `--suspicious-hold-percent-min` / `--suspicious-hold-percent-max` | Suspicious holding % range |
| `--is-lp-burnt` | LP burned filter (`true`/`false`) |
| `--is-mint` | Mintable filter (`true`/`false`) |
| `--is-freeze` | Freeze filter (`true`/`false`) |

**Return fields** (array of token objects):

| Field | Type | Description |
|---|---|---|
| `chainIndex` | String | Chain identifier |
| `tokenSymbol` | String | Token symbol |
| `tokenLogoUrl` | String | Token logo image URL |
| `tokenContractAddress` | String | Token contract address |
| `marketCap` | String | Market capitalization in USD |
| `volume` | String | Trading volume in USD |
| `firstTradeTime` | String | First trade timestamp (Unix ms) |
| `change` | String | Price change percentage (for selected time frame) |
| `liquidity` | String | Total liquidity in USD |
| `price` | String | Current price in USD |
| `holders` | String | Number of token holders |
| `uniqueTraders` | String | Number of unique traders |
| `txsBuy` | String | Buy transaction count |
| `txsSell` | String | Sell transaction count |
| `txs` | String | Total transaction count |
| `inflowUsd` | String | Net inflow in USD |
| `riskLevelControl` | String | Risk control level |
| `devHoldPercent` | String | Developer holding percentage |
| `top10HoldPercent` | String | Top-10 holders combined percentage |
| `insiderHoldPercent` | String | Insider holding percentage |
| `bundleHoldPercent` | String | Bundle holding percentage |
| `vibeScore` | String | Vibe score |
| `mentionsCount` | String | X/Twitter mention count |

## 8. onchainos token advanced-info

Get advanced token info including risk level, creator details, dev stats, and holder concentration.

```bash
onchainos token advanced-info --address <address> [--chain <chain>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Token contract address |
| `--chain` | No | `ethereum` | Chain name |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `riskControlLevel` | String | Risk control level |
| `totalFee` | String | Total fee collected |
| `lpBurnedPercent` | String | Percentage of LP tokens burned |
| `isInternal` | Boolean | Whether the token is internal |
| `protocolId` | String | Protocol identifier |
| `progress` | String | Token progress (e.g., bonding curve %) |
| `tokenTags` | Array\<String\> | Active tag labels for the token. Possible values: `honeypot`, `dexBoost`, `lowLiquidity`, `communityRecognized`, `devHoldingStatusSell`, `devHoldingStatusSellAll`, `devHoldingStatusBuy`, `initialHighLiquidity`, `smartMoneyBuy`, `devAddLiquidity`, `devBurnToken`, `volumeChangeRateHoldersPlunge`, `holdersChangeRateHoldersSurge`, `dexScreenerTokenCommunityTakeOver`, `dexScreenerPaid` |
| `createTime` | String | Token creation timestamp |
| `creatorAddress` | String | Creator wallet address |
| `devRugPullTokenCount` | String | Number of tokens by dev that were rug pulls |
| `devCreateTokenCount` | String | Total tokens created by dev |
| `devLaunchedTokenCount` | String | Number of tokens by dev that launched |
| `top10HoldPercent` | String | Top 10 holders combined percentage |
| `devHoldingPercent` | String | Developer holding percentage |
| `bundleHoldingPercent` | String | Bundle holding percentage |
| `suspiciousHoldingPercent` | String | Suspicious holding percentage |
| `sniperHoldingPercent` | String | Sniper holding percentage |
| `snipersClearAddressCount` | String | Number of sniper addresses that cleared |
| `snipersTotal` | String | Total sniper count |

## 9. onchainos token top-trader

Get top traders (profit addresses) for a token.

```bash
onchainos token top-trader --address <address> [--chain <chain>] [--tag-filter <n>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Token contract address |
| `--chain` | No | `ethereum` | Chain name |
| `--tag-filter` | No | - | Filter by trader tag: 1=KOL, 2=Developer, 3=Smart Money, 4=Whale, 5=Fresh Wallet, 6=Insider, 7=Sniper, 8=Suspicious Phishing, 9=Bundler |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `holderWalletAddress` | String | Trader wallet address |
| `holdAmount` | String | Token amount held |
| `holdPercent` | String | Percentage of total supply held |
| `nativeTokenBalance` | String | Native token balance |
| `boughtAmount` | String | Total amount bought |
| `avgBuyPrice` | String | Average buy price (USD) |
| `soldAmount` | String | Total amount sold |
| `avgSellPrice` | String | Average sell price (USD) |
| `totalPnlUsd` | String | Total PnL (USD) |
| `realizedPnlUsd` | String | Realized PnL (USD) |
| `unrealizedPnlUsd` | String | Unrealized PnL (USD) |
| `fundingSource` | String | Funding source of the wallet |

## 10. onchainos token trades

Get token DEX trade history with optional tag and wallet address filters.

```bash
onchainos token trades --address <address> [--chain <chain>] [--limit <n>] [--tag-filter <n>] [--wallet-filter <addrs>]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--address` | Yes | - | Token contract address |
| `--chain` | No | `ethereum` | Chain name |
| `--limit` | No | `100` | Number of trades (max 500) |
| `--tag-filter` | No | - | Filter by trader tag: `1`=KOL, `2`=Developer, `3`=Smart Money, `4`=Whale, `5`=Fresh Wallet, `6`=Insider, `7`=Sniper, `8`=Suspicious Phishing, `9`=Bundler |
| `--wallet-filter` | No | - | Wallet address filter, comma-separated (max 10 addresses) |

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `id` | String | Trade ID |
| `type` | String | Trade direction: `buy` or `sell` |
| `price` | String | Trade price in USD |
| `volume` | String | Trade volume in USD |
| `time` | String | Trade timestamp (Unix milliseconds) |
| `dexName` | String | DEX name where trade occurred |
| `txHashUrl` | String | Transaction hash explorer URL |
| `userAddress` | String | Wallet address of the trader |
| `isFiltered` | String | `"1"` if this trade matched the tag/wallet filter, `"0"` otherwise |
| `poolLogoUrl` | String | Pool logo URL |
| `changedTokenInfo` | Array | Token change details for the trade |
| `changedTokenInfo[].tokenSymbol` | String | Token symbol |
| `changedTokenInfo[].tokenAddress` | String | Token contract address |
| `changedTokenInfo[].tokenLogoUrl` | String | Token logo URL |
| `changedTokenInfo[].amount` | String | Token amount changed |

## Input / Output Examples

**User says:** "Search for xETH token on XLayer"

```bash
onchainos token search --query xETH --chains xlayer
# -> Display:
#   xETH (0xe7b0...) - XLayer
#   Price: $X,XXX.XX | 24h: +X% | Market Cap: $XXM | Liquidity: $XXM
#   Community Recognized: Yes
```

**User says:** "What's trending on Solana by volume?"

```bash
onchainos token trending --chains solana --sort-by 5 --time-frame 4
# -> Display top tokens sorted by 24h volume:
#   #1 SOL  - Vol: $1.2B | Change: +3.5% | MC: $80B
#   #2 BONK - Vol: $450M | Change: +12.8% | MC: $1.5B
#   ...
```

**User says:** "Who are the top holders of this token?"

```bash
onchainos token holders --address 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee --chain xlayer
# -> Display top 100 holders with amounts and addresses
```
