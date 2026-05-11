---
name: moralis-data-api
description: Query Web3 blockchain data from Moralis API. Use when user asks about wallet data (balances, tokens, NFTs, transaction history, profitability, net worth), token data (prices, metadata, DEX pairs, analytics, security scores), NFT data (metadata, transfers, traits, rarity, floor prices), DeFi positions, entity/label data for exchanges and funds, or block and transaction data. Supports EVM chains (Ethereum, Polygon, BSC, Arbitrum, Base, Optimism, Avalanche, etc.) and Solana. NOT for real-time streaming - use moralis-streams-api instead.
version: 1.3.1
license: MIT
compatibility: Requires curl for API calls. Requires MORALIS_API_KEY env var for authentication.
metadata:
  author: MoralisWeb3
  homepage: https://docs.moralis.com
  repository: https://github.com/MoralisWeb3/onchain-skills
  openclaw:
    requires:
      env:
        - MORALIS_API_KEY
      bins:
        - curl
    primaryEnv: MORALIS_API_KEY
allowed-tools: Bash Read Grep Glob
---

## CRITICAL: Read Rule Files Before Implementing

**The #1 cause of bugs is not reading the endpoint rule file before writing code.**

For EVERY endpoint:

1. Read `rules/{EndpointName}.md`
2. Find "Example Response" section
3. Copy the EXACT JSON structure
4. Note field names (snake_case), data types, HTTP method, path, wrapper structure

**Reading Order:**

1. This SKILL.md (core patterns)
2. Endpoint rule file in `rules/`
3. Pattern references in `references/` (for edge cases only)

---

## Setup

### API Key (optional)

**Never ask the user to paste their API key into the chat.** Instead:

1. Check if `MORALIS_API_KEY` is set in the environment (try running `[ -n "$MORALIS_API_KEY" ] && echo "API key is set" || echo "API key is NOT set"`).
2. If not set, offer to create the `.env` file with an empty placeholder: `MORALIS_API_KEY=`
3. Tell the user to open the `.env` file and paste their key there themselves.
4. Let them know: without the key, you won't be able to test or call the Moralis API on their behalf.

If they don't have a key yet, point them to [admin.moralis.com/register](https://admin.moralis.com/register) (free, no credit card).

### Environment Variable Discovery

The `.env` file location depends on how skills are installed:

Create the `.env` file in the project root (same directory the user runs Claude Code from). Make sure `.env` is in `.gitignore`.

### Verify Your Key

```bash
curl "https://deep-index.moralis.io/api/v2.2/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045/balance?chain=0x1" \
  -H "X-API-Key: $MORALIS_API_KEY"
```

---

## Base URLs

| API    | Base URL                                 |
| ------ | ---------------------------------------- |
| EVM    | `https://deep-index.moralis.io/api/v2.2` |
| Solana | `https://solana-gateway.moralis.io`      |

## Authentication

All requests require: `X-API-Key: $MORALIS_API_KEY`

---

## Quick Reference: Most Common Patterns

### Data Type Rules

| Field          | Reality                          | NOT               |
| -------------- | -------------------------------- | ----------------- |
| `block_number` | Decimal `12386788`               | Hex `0xf2b5a4`    |
| `timestamp`    | ISO `"2021-05-07T11:08:35.000Z"` | Unix `1620394115` |
| `balance`      | String `"1000000000000000000"`   | Number            |
| `decimals`     | String or number                 | Always number     |

### Block Numbers (always decimal)

```typescript
block_number: 12386788; // number - use directly
block_number: "12386788"; // string - parseInt(block_number, 10)
```

### Timestamps (usually ISO strings)

```typescript
"2021-05-07T11:08:35.000Z"; // → new Date(timestamp).getTime()
```

### Balances (always strings unless its a property named "formatted" eg. balanceFormatted, BigInt)

```typescript
balance: "1000000000000000000";
// → (Number(BigInt(balance)) / 1e18).toFixed(6)
```

### Response Patterns

| Pattern                              | Example Endpoints                             |
| ------------------------------------ | --------------------------------------------- |
| Direct array `[...]`                 | getWalletTokenBalancesPrice, getTokenMetadata |
| Wrapped `{ result: [] }`             | getWalletNFTs, getWalletTransactions          |
| Paginated `{ page, cursor, result }` | getWalletHistory, getNFTTransfers             |

```typescript
// Safe extraction
const data = Array.isArray(response) ? response : response.result || [];
```

### Common Field Mappings

```typescript
token_address → tokenAddress
from_address_label → fromAddressLabel
block_number → blockNumber
receipt_status: "1" → success, "0" → failed
possible_spam: "true"/"false" → boolean check
```

---

## Common Pitfalls (Top 5)

1. **Block numbers are decimal, not hex** - Use `parseInt(x, 10)`, not `parseInt(x, 16)`
2. **Timestamps are ISO strings** - Use `new Date(timestamp).getTime()`
3. **Balances are strings** - Use `BigInt(balance)` for math
4. **Response may be wrapped** - Check for `.result` before `.map()`
5. **Path inconsistencies** - Some use `/wallets/{address}/...`, others `/{address}/...`

See [references/CommonPitfalls.md](references/CommonPitfalls.md) for complete reference.

---

## Pagination

Many endpoints use cursor-based pagination:

```bash
# First request
curl "...?limit=100" -H "X-API-Key: $KEY"

# Next page
curl "...?limit=100&cursor=<cursor_from_response>" -H "X-API-Key: $KEY"
```

See [references/Pagination.md](references/Pagination.md) for details.

---

## Testing Endpoints

```bash
ADDRESS="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
CHAIN="0x1"

# Wallet Balance
curl "https://deep-index.moralis.io/api/v2.2/${ADDRESS}/balance?chain=${CHAIN}" \
  -H "X-API-Key: $MORALIS_API_KEY"

# Token Price
curl "https://deep-index.moralis.io/api/v2.2/erc20/0x6B175474E89094C44Da98b954EedeAC495271d0F/price?chain=${CHAIN}" \
  -H "X-API-Key: $MORALIS_API_KEY"

# Wallet Transactions (note result wrapper)
curl "https://deep-index.moralis.io/api/v2.2/${ADDRESS}?chain=${CHAIN}&limit=5" \
  -H "X-API-Key: $MORALIS_API_KEY" | jq '.result'
```

---

## Quick Troubleshooting

| Issue                     | Cause                  | Solution                            |
| ------------------------- | ---------------------- | ----------------------------------- |
| "Property does not exist" | Field name mismatch    | Check snake_case in rule file       |
| "Cannot read undefined"   | Missing optional field | Use `?.` optional chaining          |
| "blockNumber is NaN"      | Parsing decimal as hex | Use radix 10: `parseInt(x, 10)`     |
| "Wrong timestamp"         | Parsing ISO as number  | Use `new Date(timestamp).getTime()` |
| "404 Not Found"           | Wrong endpoint path    | Verify path in rule file            |

---

## Performance & Timeouts

Most endpoints respond quickly under normal conditions. Response times can vary based on wallet activity volume, chain, and query complexity.

**Recommended client timeouts:**
- Simple queries (balance, price, metadata): 10s
- Complex queries (wallet history, DeFi positions): 30s

Large wallets with extensive transaction histories may take longer — use pagination with reasonable `limit` values.

See [references/PerformanceAndLatency.md](references/PerformanceAndLatency.md) for optimization tips.

---

## Default Chain Behavior

**EVM addresses (`0x...`):** Default to Ethereum (`chain=0x1`) unless specified.

**Solana addresses (base58):** Auto-detected and routed to Solana API.

---

## Supported Chains

**EVM (40+ chains):** Ethereum (0x1), Polygon (0x89), BSC (0x38), Arbitrum (0xa4b1), Optimism (0xa), Base (0x2105), Avalanche (0xa86a), and more.

**Solana:** Mainnet, Devnet

See [references/SupportedApisAndChains.md](references/SupportedApisAndChains.md) for full list.

---

## Endpoint Catalog

Complete list of all 136 endpoints (102 EVM + 34 Solana) organized by category.

### Wallet

Balances, tokens, NFTs, transaction history, profitability, and net worth data.

| Endpoint | Description |
|----------|-------------|
| [getNativeBalance](rules/getNativeBalance.md) | Get native balance by wallet |
| [getNativeBalancesForAddresses](rules/getNativeBalancesForAddresses.md) | Get native balance for a set of wallets |
| [getWalletActiveChains](rules/getWalletActiveChains.md) | Get active chains by wallet address |
| [getWalletApprovals](rules/getWalletApprovals.md) | Get ERC20 approvals by wallet |
| [getWalletHistory](rules/getWalletHistory.md) | Get the complete decoded transaction history of a wallet |
| [getWalletInsight](rules/getWalletInsight.md) | Get wallet insight metrics |
| [getWalletNetWorth](rules/getWalletNetWorth.md) | Get wallet net worth |
| [getWalletNFTCollections](rules/getWalletNFTCollections.md) | Get NFT collections by wallet address |
| [getWalletNFTs](rules/getWalletNFTs.md) | Get NFTs by wallet address |
| [getWalletNFTTransfers](rules/getWalletNFTTransfers.md) | Get NFT Transfers by wallet address |
| [getWalletProfitability](rules/getWalletProfitability.md) | Get detailed profit and loss by wallet address |
| [getWalletProfitabilitySummary](rules/getWalletProfitabilitySummary.md) | Get profit and loss summary by wallet address |
| [getWalletStats](rules/getWalletStats.md) | Get summary stats by wallet address |
| [getWalletTokenBalancesPrice](rules/getWalletTokenBalancesPrice.md) | Get token balances with prices by wallet address |
| [getWalletTokenTransfers](rules/getWalletTokenTransfers.md) | Get ERC20 token transfers by wallet address |
| [getWalletTransactions](rules/getWalletTransactions.md) | Get native transactions by wallet |
| [getWalletTransactionsVerbose](rules/getWalletTransactionsVerbose.md) | Get decoded transactions by wallet |

### Token

Token prices, metadata, pairs, DEX swaps, analytics, security scores, and sniper detection.

| Endpoint | Description |
|----------|-------------|
| [getAggregatedTokenPairStats](rules/getAggregatedTokenPairStats__evm.md) | Get aggregated token pair statistics by address |
| [getHistoricalTokenScore](rules/getHistoricalTokenScore.md) | Get historical token score by token address |
| [getMultipleTokenAnalytics](rules/getMultipleTokenAnalytics.md) | Get token analytics for a list of token addresses |
| [getPairAddress](rules/getPairAddress.md) | Get DEX token pair address |
| [getPairReserves](rules/getPairReserves.md) | Get DEX token pair reserves |
| [getPairStats](rules/getPairStats__evm.md) | Get stats by pair address |
| [getSnipersByPairAddress](rules/getSnipersByPairAddress__evm.md) | Get snipers by pair address |
| [getSwapsByPairAddress](rules/getSwapsByPairAddress__evm.md) | Get swap transactions by pair address |
| [getSwapsByTokenAddress](rules/getSwapsByTokenAddress__evm.md) | Get swap transactions by token address |
| [getSwapsByWalletAddress](rules/getSwapsByWalletAddress__evm.md) | Get swap transactions by wallet address |
| [getTimeSeriesTokenAnalytics](rules/getTimeSeriesTokenAnalytics.md) | Retrieve timeseries trading stats by token addresses |
| [getTokenAnalytics](rules/getTokenAnalytics.md) | Get token analytics by token address |
| [getTokenBondingStatus](rules/getTokenBondingStatus__evm.md) | Get the token bonding status |
| [getTokenCategories](rules/getTokenCategories.md) | Get ERC20 token categories |
| [getTokenHolders](rules/getTokenHolders__evm.md) | Get a holders summary by token address |
| [getTokenMetadata](rules/getTokenMetadata__evm.md) | Get ERC20 token metadata by contract |
| [getTokenMetadataBySymbol](rules/getTokenMetadataBySymbol.md) | Get ERC20 token metadata by symbols |
| [getTokenOwners](rules/getTokenOwners.md) | Get ERC20 token owners by contract |
| [getTokenPairs](rules/getTokenPairs__evm.md) | Get token pairs by address |
| [getTokenScore](rules/getTokenScore.md) | Get token score by token address |
| [getTokenStats](rules/getTokenStats.md) | Get ERC20 token stats |
| [getTokenTransfers](rules/getTokenTransfers.md) | Get ERC20 token transfers by contract address |

### NFT

NFT metadata, transfers, traits, rarity, floor prices, and trades.

| Endpoint | Description |
|----------|-------------|
| [getContractNFTs](rules/getContractNFTs.md) | Get NFTs by contract address |
| [getMultipleNFTs](rules/getMultipleNFTs.md) | Get Metadata for NFTs |
| [getNFTBulkContractMetadata](rules/getNFTBulkContractMetadata.md) | Get metadata for multiple NFT contracts |
| [getNFTByContractTraits](rules/getNFTByContractTraits.md) | Get NFTs by traits |
| [getNFTCollectionStats](rules/getNFTCollectionStats.md) | Get summary stats by NFT collection |
| [getNFTContractMetadata](rules/getNFTContractMetadata.md) | Get NFT collection metadata |
| [getNFTContractSalePrices](rules/getNFTContractSalePrices.md) | Get NFT sale prices by collection |
| [getNFTContractTransfers](rules/getNFTContractTransfers.md) | Get NFT transfers by contract address |
| [getNFTFloorPriceByContract](rules/getNFTFloorPriceByContract.md) | Get NFT floor price by contract |
| [getNFTFloorPriceByToken](rules/getNFTFloorPriceByToken.md) | Get NFT floor price by token |
| [getNFTHistoricalFloorPriceByContract](rules/getNFTHistoricalFloorPriceByContract.md) | Get historical NFT floor price by contract |
| [getNFTMetadata](rules/getNFTMetadata__evm.md) | Get NFT metadata |
| [getNFTOwners](rules/getNFTOwners.md) | Get NFT owners by contract address |
| [getNFTSalePrices](rules/getNFTSalePrices.md) | Get NFT sale prices by token |
| [getNFTTokenIdOwners](rules/getNFTTokenIdOwners.md) | Get NFT owners by token ID |
| [getNFTTrades](rules/getNFTTrades.md) | Get NFT trades by collection |
| [getNFTTradesByToken](rules/getNFTTradesByToken.md) | Get NFT trades by token |
| [getNFTTradesByWallet](rules/getNFTTradesByWallet.md) | Get NFT trades by wallet address |
| [getNFTTraitsByCollection](rules/getNFTTraitsByCollection.md) | Get NFT traits by collection |
| [getNFTTraitsByCollectionPaginate](rules/getNFTTraitsByCollectionPaginate.md) | Get NFT traits by collection paginate |
| [getNFTTransfers](rules/getNFTTransfers.md) | Get NFT transfers by token ID |
| [getTopNFTCollectionsByMarketCap](rules/getTopNFTCollectionsByMarketCap.md) | Get top NFT collections by market cap |

### DeFi

DeFi protocol positions, liquidity, and exposure data.

| Endpoint | Description |
|----------|-------------|
| [getDefiPositionsByProtocol](rules/getDefiPositionsByProtocol.md) | Get detailed DeFi positions by protocol for a wallet |
| [getDefiPositionsSummary](rules/getDefiPositionsSummary.md) | Get DeFi positions of a wallet |
| [getDefiSummary](rules/getDefiSummary.md) | Get the DeFi summary of a wallet |

### Entity

Labeled addresses including exchanges, funds, protocols, and whales.

| Endpoint | Description |
|----------|-------------|
| [getEntity](rules/getEntity.md) | Get Entity Details By Id |
| [getEntityCategories](rules/getEntityCategories.md) | Get Entity Categories |

### Price

Token and NFT prices, OHLCV candlestick data.

| Endpoint | Description |
|----------|-------------|
| [getMultipleTokenPrices](rules/getMultipleTokenPrices__evm.md) | Get Multiple ERC20 token prices |
| [getPairCandlesticks](rules/getPairCandlesticks.md) | Get OHLCV by pair address |
| [getPairPrice](rules/getPairPrice.md) | Get DEX token pair price |
| [getTokenPrice](rules/getTokenPrice__evm.md) | Get ERC20 token price |

### Blockchain

Blocks, transactions, date-to-block conversion, and contract functions.

| Endpoint | Description |
|----------|-------------|
| [getBlock](rules/getBlock.md) | Get block by hash |
| [getDateToBlock](rules/getDateToBlock.md) | Get block by date |
| [getLatestBlockNumber](rules/getLatestBlockNumber.md) | Get latest block number |
| [getTransaction](rules/getTransaction.md) | Get transaction by hash |
| [getTransactionVerbose](rules/getTransactionVerbose.md) | Get decoded transaction by hash |

### Discovery

Trending tokens, blue chips, market movers, and token discovery.

| Endpoint | Description |
|----------|-------------|
| [getDiscoveryToken](rules/getDiscoveryToken.md) | Get token details |
| [getTimeSeriesVolume](rules/getTimeSeriesVolume.md) | Retrieve timeseries trading stats by chain |
| [getTimeSeriesVolumeByCategory](rules/getTimeSeriesVolumeByCategory.md) | Retrieve timeseries trading stats by category |
| [getTopCryptoCurrenciesByMarketCap](rules/getTopCryptoCurrenciesByMarketCap.md) | Get top crypto currencies by market cap |
| [getTopCryptoCurrenciesByTradingVolume](rules/getTopCryptoCurrenciesByTradingVolume.md) | Get top crypto currencies by trading volume |
| [getTopERC20TokensByMarketCap](rules/getTopERC20TokensByMarketCap.md) | Get top ERC20 tokens by market cap |
| [getTopERC20TokensByPriceMovers](rules/getTopERC20TokensByPriceMovers.md) | Get top ERC20 tokens by price movements (winners and losers) |
| [getTopGainersTokens](rules/getTopGainersTokens.md) | Get tokens with top gainers |
| [getTopLosersTokens](rules/getTopLosersTokens.md) | Get tokens with top losers |
| [getTopProfitableWalletPerToken](rules/getTopProfitableWalletPerToken.md) | Get top traders for a given ERC20 token |
| [getTrendingTokens](rules/getTrendingTokens.md) | Get trending tokens |
| [getVolumeStatsByCategory](rules/getVolumeStatsByCategory.md) | Get trading stats by categories |
| [getVolumeStatsByChain](rules/getVolumeStatsByChain.md) | Get trading stats by chain |

### Other

Utility endpoints including API version, endpoint weights, and address resolution.

| Endpoint | Description |
|----------|-------------|
| [getBondingTokensByExchange](rules/getBondingTokensByExchange__evm.md) | Get bonding tokens by exchange |
| [getEntitiesByCategory](rules/getEntitiesByCategory.md) | Get Entities By Category |
| [getFilteredTokens](rules/getFilteredTokens.md) | Returns a list of tokens that match the specified filters and criteria |
| [getGraduatedTokensByExchange](rules/getGraduatedTokensByExchange__evm.md) | Get graduated tokens by exchange |
| [getHistoricalTokenHolders](rules/getHistoricalTokenHolders__evm.md) | Get timeseries holders data |
| [getNewTokensByExchange](rules/getNewTokensByExchange__evm.md) | Get new tokens by exchange |
| [getUniqueOwnersByCollection](rules/getUniqueOwnersByCollection.md) | Get unique wallet addresses owning NFTs from a contract. |
| [resolveAddress](rules/resolveAddress.md) | ENS lookup by address |
| [resolveAddressToDomain](rules/resolveAddressToDomain.md) | Resolve Address to Unstoppable domain |
| [resolveDomain](rules/resolveDomain.md) | Resolve Unstoppable domain |
| [resolveENSDomain](rules/resolveENSDomain.md) | ENS lookup by domain |
| [reSyncMetadata](rules/reSyncMetadata.md) | Resync NFT metadata |
| [searchEntities](rules/searchEntities.md) | Search Entities, Organizations or Wallets |
| [searchTokens](rules/searchTokens.md) | Search for tokens based on contract address, pair address, token name or token symbol. |

### Solana Endpoints

Solana-specific endpoints (24 native + 10 EVM variants that support Solana chain = 34 total).

| Endpoint | Description |
|----------|-------------|
| [balance](rules/balance__solana.md) | Gets native balance owned by the given address |
| [getAggregatedTokenPairStats](rules/getAggregatedTokenPairStats__solana.md) | Get aggregated token pair statistics by address |
| [getBondingTokensByExchange](rules/getBondingTokensByExchange__solana.md) | Get bonding tokens by exchange |
| [getCandleSticks](rules/getCandleSticks__solana.md) | Get candlesticks for a pair address |
| [getGraduatedTokensByExchange](rules/getGraduatedTokensByExchange__solana.md) | Get graduated tokens by exchange |
| [getHistoricalTokenHolders](rules/getHistoricalTokenHolders__solana.md) | Get token holders overtime for a given tokens |
| [getMultipleTokenMetadata](rules/getMultipleTokenMetadata__solana.md) | Get multiple token metadata |
| [getMultipleTokenPrices](rules/getMultipleTokenPrices__solana.md) | Get token price |
| [getNFTMetadata](rules/getNFTMetadata__solana.md) | Get the global metadata for a given contract |
| [getNFTs](rules/getNFTs__solana.md) | Gets NFTs owned by the given address |
| [getNewTokensByExchange](rules/getNewTokensByExchange__solana.md) | Get new tokens by exchange |
| [getPairStats](rules/getPairStats__solana.md) | Get stats for a pair address |
| [getPortfolio](rules/getPortfolio__solana.md) | Gets the portfolio of the given address |
| [getSPL](rules/getSPL__solana.md) | Gets token balances owned by the given address |
| [getSnipersByPairAddress](rules/getSnipersByPairAddress__solana.md) | Get snipers by pair address. |
| [getSwapsByPairAddress](rules/getSwapsByPairAddress__solana.md) | Get all swap related transactions (buy, sell, add liquidity & remove liquidity) |
| [getSwapsByTokenAddress](rules/getSwapsByTokenAddress__solana.md) | Get all swap related transactions (buy, sell) |
| [getSwapsByWalletAddress](rules/getSwapsByWalletAddress__solana.md) | Get all swap related transactions (buy, sell) for a specific wallet address. |
| [getTokenBondingStatus](rules/getTokenBondingStatus__solana.md) | Get Token Bonding Status |
| [getTokenHolders](rules/getTokenHolders__solana.md) | Get the summary of holders for a given token token. |
| [getTokenMetadata](rules/getTokenMetadata__solana.md) | Get Token metadata |
| [getTokenPairs](rules/getTokenPairs__solana.md) | Get token pairs by address |
| [getTokenPrice](rules/getTokenPrice__solana.md) | Get token price |
| [getTopHolders](rules/getTopHolders__solana.md) | Get paginated top holders for a given token. |
| [getDiscoveryToken](rules/getDiscoveryToken__solana.md) | **Solana variant:** Get token details |
| [getHistoricalTokenScore](rules/getHistoricalTokenScore__solana.md) | **Solana variant:** Get historical token score by token address |
| [getTimeSeriesVolume](rules/getTimeSeriesVolume__solana.md) | **Solana variant:** Retrieve timeseries trading stats by chain |
| [getTimeSeriesVolumeByCategory](rules/getTimeSeriesVolumeByCategory__solana.md) | **Solana variant:** Retrieve timeseries trading stats by category |
| [getTokenAnalytics](rules/getTokenAnalytics__solana.md) | **Solana variant:** Get token analytics by token address |
| [getTokenScore](rules/getTokenScore__solana.md) | **Solana variant:** Get token score by token address |
| [getTopGainersTokens](rules/getTopGainersTokens__solana.md) | **Solana variant:** Get tokens with top gainers |
| [getTopLosersTokens](rules/getTopLosersTokens__solana.md) | **Solana variant:** Get tokens with top losers |
| [getTrendingTokens](rules/getTrendingTokens__solana.md) | **Solana variant:** Get trending tokens |
| [getVolumeStatsByCategory](rules/getVolumeStatsByCategory__solana.md) | **Solana variant:** Get trading stats by categories |

## Reference Documentation

- [references/CommonPitfalls.md](references/CommonPitfalls.md) - Complete pitfalls reference
- [references/DataTransformations.md](references/DataTransformations.md) - Type conversion reference
- [references/FilteredTokens.md](references/FilteredTokens.md) - Token discovery metrics, timeframes, filters, and examples
- [references/PerformanceAndLatency.md](references/PerformanceAndLatency.md) - Response time guidance, timeout recommendations, caching
- [references/ResponsePatterns.md](references/ResponsePatterns.md) - Pagination patterns
- [references/SupportedApisAndChains.md](references/SupportedApisAndChains.md) - Chains and APIs

---

## See Also

- Endpoint rules: `rules/*.md` files
- Streams API: @moralis-streams-api for real-time events
