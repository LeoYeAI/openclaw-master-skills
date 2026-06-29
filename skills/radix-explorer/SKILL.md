---
name: emily-radix-assistant
description: "Query Radix DLT blockchain data including wallet balances and performance, token prices and market movers, validator staking info, transaction history, network statistics, ecosystem news, DeFi yield pools, XRD trading venues, dApp directory, and developer resources. Use when users ask about Radix, XRD, wallets starting with account_rdx, tokens starting with resource_rdx, staking, DeFi on Radix, .xrd domains, Attos Earn, or buying/bridging XRD."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔮",
        "requires": { "bins": ["mcporter"] },
        "install":
          [
            {
              "id": "mcporter",
              "kind": "node",
              "package": "mcporter",
              "bins": ["mcporter"],
              "label": "Install mcporter CLI (npm)",
            },
          ],
      },
  }
---

# Emily Your Personal Radix Assistant

Query the Radix DLT blockchain for wallet balances, token prices, network stats, validators, transactions, ecosystem news, DeFi yield data, trading venues, dApps, and developer resources.

Free to use. No API key required. Mainnet data only.

## Setup (auto-configured)

**On first use**, check if the `emily-radix-assistant` server is already registered:

```bash
mcporter list emily-radix-assistant
```

If not found, register it (URL is the only required argument):

```bash
mcporter config add emily-radix-assistant https://www.ineedemily.com/api/mcp/mcp
```

Verify with a quick test:

```bash
mcporter call emily-radix-assistant.network_stats
```

To see all available tools and their schemas:

```bash
mcporter list emily-radix-assistant --schema --all-parameters
```

## Address Formats

- **Wallet addresses** start with `account_rdx` (66 characters total)
- **Token addresses** start with `resource_rdx` (67 characters total)
- **RNS domains** end with `.xrd` (e.g. `alice.xrd`)
- All addresses are **mainnet only** (Babylon network)

## Available Tools (35 total)

### Wallet Tools (7)

| Tool                      | Description                            | Required Params                | Optional Params                                                                                                |
| ------------------------- | -------------------------------------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| `tokens_in_wallet`        | All tokens with prices, 24H/7D changes | `address`                      | -                                                                                                              |
| `performance_of_wallet`   | Total USD value, 24H/7D performance    | `address`                      | -                                                                                                              |
| `distribution_of_wallet`  | Portfolio breakdown by %               | `address`                      | `limit` (1-20, default 5), `minUSDValue`                                                                       |
| `historical_wallet_value` | Wallet value on a past date            | `address`, `date` (YYYY-MM-DD) | -                                                                                                              |
| `latest_transactions`     | Most recent transactions               | `address`                      | `until` (ISO date)                                                                                             |
| `search_transactions`     | Filter transaction history             | `address`                      | `resourceAddress`, `startDate`, `endDate`, `transactionType` (swap/stake/unstake/claim/deposit/withdrawal/all) |
| `check_owned_rns_domains` | RNS (.xrd) domains owned               | `address`                      | -                                                                                                              |

### Token Tools (7)

| Tool                       | Description                                       | Required Params                                  | Optional Params                                                                                                                                                                                                                         |
| -------------------------- | ------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tokens_on_radix`          | Search/list tokens (top by volume when no search) | -                                                | `search`, `limit` (default 10), `includeAddress`, `includePrice`, `includeVolume`, `includeSupply`, `includePriceChanges`, `includeTvl`, `includeType`, `includePriceXRD`, `includeDescription`, `includeInfoUrl`, `includeExplorerUrl` |
| `token_gainers_and_losers` | Top/bottom performers                             | -                                                | `sortBy` (gained/lost/volume_high/volume_low/market_cap_high/market_cap_low), `timePeriod` (24h/7d), `currency` (USD/XRD), `limit` (1-100, default 5)                                                                                   |
| `wrapped_assets`           | Bridged assets (xUSDC, xETH, xwBTC...)            | -                                                | `limit` (1-50, default 10), `sortBy` (volume/tvl/marketCap/name), `includePrice`, `includeVolume`, `includeSupply`, `includePriceChanges`, `includeTvl`                                                                                 |
| `token_details`            | On-chain metadata for a specific token            | `address` (resource_rdx...)                      | `includeTopHolders` (0-100)                                                                                                                                                                                                             |
| `tokens_on_cmc`            | Search CoinMarketCap listings                     | -                                                | `search`, `limit` (1-300, default 10), `includePrice`, `sortBy` (rank/name/symbol)                                                                                                                                                      |
| `token_details_from_cmc`   | Detailed CMC data by IDs                          | `tokenIds` (array of ints)                       | -                                                                                                                                                                                                                                       |
| `historical_token_data`    | Token price on a specific date                    | `address` (resource_rdx...), `date` (YYYY-MM-DD) | -                                                                                                                                                                                                                                       |

### Network Tools (3)

| Tool             | Description                                  | Required Params            | Optional Params      |
| ---------------- | -------------------------------------------- | -------------------------- | -------------------- |
| `network_stats`  | XRD price, staking %, DEX volume, TVL, epoch | -                          | -                    |
| `all_validators` | Validators with stake amounts and APY        | -                          | `limit` (default 50) |
| `rns_to_address` | Resolve .xrd domain to wallet address        | `address` (e.g. alice.xrd) | -                    |

### Ecosystem & News (8)

| Tool                     | Description                                                                     | Required Params                     | Optional Params                                                   |
| ------------------------ | ------------------------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------- |
| `today_update`           | Today's ecosystem update (launches, protocol updates, market moves)             | -                                   | -                                                                 |
| `recent_daily_updates`   | Daily summaries for recent days                                                 | -                                   | `days` (1-30, default 7)                                          |
| `weekly_updates`         | Weekly ecosystem summaries                                                      | -                                   | `weeks` (1-12, default 4)                                         |
| `monthly_updates`        | Monthly ecosystem summaries with growth metrics and milestones                  | -                                   | `months` (1-12, default 3)                                        |
| `specific_date_range`    | Ecosystem summaries for a custom date range (auto-selects daily/weekly/monthly) | `startDate`, `endDate` (YYYY-MM-DD) | -                                                                 |
| `specific_month`         | Ecosystem summary for a specific month                                          | `year` (e.g. 2025), `month` (1-12)  | -                                                                 |
| `official_announcements` | Latest official announcements from the Radix Telegram channel                   | -                                   | -                                                                 |
| `ecosystem_summary`      | Comprehensive summary across timeframes                                         | -                                   | `timeframe` (daily/weekly/monthly), `period` (e.g. "last 7 days") |

### Glossary, dApps & Community (6)

| Tool                        | Description                                                                             | Required Params | Optional Params                                                |
| --------------------------- | --------------------------------------------------------------------------------------- | --------------- | -------------------------------------------------------------- |
| `radix_glossary`            | Radix terminology (Cerberus, Scrypto, Xi'an, Radix Engine, etc.)                        | -               | `themes` (array of theme names; omit for available list)       |
| `radix_core_concepts`       | Core blockchain and Radix technical concepts (sharding, consensus, atomic transactions) | -               | `concepts` (array of concept names; omit for available list)   |
| `radix_dapps`               | Discover dApps in the ecosystem                                                         | -               | `name`, `tags` (array), `category` (DeFi/NFT/Utility/Meme/Dao) |
| `radix_developer_resources` | Developer docs, SDKs, tools, and learning resources                                     | -               | -                                                              |
| `xrd_trading_venues`        | Where to buy, trade, bridge, or leverage XRD                                            | -               | `type` (leverage/onramp/bridge/spot), `all` (boolean)          |
| `radix_socials`             | Community channels, official accounts, developer chats                                  | -               | `category` (community/official/resources/developer/market)     |

### Attos Earn - DeFi Yield (4)

| Tool                      | Description                                                    | Required Params | Optional Params                                                                                                                                                         |
| ------------------------- | -------------------------------------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `attos_earn_pools`        | Liquidity pools with TVL, volume, APR/bonuses                  | -               | `sortBy` (tvl/volume_24h/volume_7d/bonus_24h/bonus_7d), `limit` (default 10)                                                                                            |
| `attos_earn_strategies`   | Yield strategies: lending, staking, liquidation with APR rates | -               | `strategyType` (Lending/Staking/Liquidation), `provider` (Weft Finance/Root Finance/Defiplaza/Flux), `sortBy` (bonus_value/total_stake/deposited), `limit` (default 10) |
| `attos_earn_lp_positions` | LP positions for a wallet with PnL data                        | `walletAddress` | `sortBy` (invested/investedXrd/currentValue/pnlPercentage)                                                                                                              |
| `attos_earn_stats`        | Platform overview: total pools and strategies count            | -               | -                                                                                                                                                                       |

### CoinMarketCap Workflow (2 steps)

To get detailed market data for any cryptocurrency:

1. **Search first** with `tokens_on_cmc` to get CMC IDs
2. **Then query details** with `token_details_from_cmc` using those IDs

```bash
mcporter call emily-radix-assistant.tokens_on_cmc search=Bitcoin limit=1
# Returns tokenId, e.g. 1
mcporter call emily-radix-assistant.token_details_from_cmc --args '{"tokenIds": [1]}'
```

## Usage Examples

**Wallet analysis:**

- "What tokens are in account_rdx16x..." → `tokens_in_wallet`
- "How is this wallet performing?" → `performance_of_wallet`
- "Show portfolio breakdown for account_rdx..." → `distribution_of_wallet`
- "What was this wallet worth on 2024-06-15?" → `historical_wallet_value`
- "Show recent swaps for account_rdx..." → `search_transactions` with `transactionType=swap`

**Token research:**

- "Top 10 tokens on Radix by volume" → `tokens_on_radix`
- "Biggest gainers this week" → `token_gainers_and_losers` with `sortBy=gained`, `timePeriod=7d`
- "Show me wrapped assets on Radix" → `wrapped_assets`
- "Who are the top holders of HUG?" → `token_details` with `includeTopHolders=10`
- "What was XRD price on 2024-01-01?" → `historical_token_data`

**Network & staking:**

- "Radix network stats" → `network_stats`
- "Top 10 validators by APY" → `all_validators` with `limit=10`
- "Resolve alice.xrd" → `rns_to_address`

**DeFi yield:**

- "Best pools by APR on Attos Earn" → `attos_earn_pools` with `sortBy=bonus_24h`
- "Show lending strategies" → `attos_earn_strategies` with `strategyType=Lending`
- "My LP positions" → `attos_earn_lp_positions` with wallet address
- "Attos Earn overview" → `attos_earn_stats`

**Ecosystem & news:**

- "What happened in the Radix ecosystem today?" → `today_update`
- "Weekly updates from the last month" → `weekly_updates` with `weeks=4`
- "What happened in June 2025?" → `specific_month` with `year=2025`, `month=6`
- "Ecosystem news from Jan to March 2025" → `specific_date_range`
- "Latest official announcements" → `official_announcements`
- "Monthly ecosystem summaries" → `monthly_updates`

**Knowledge & community:**

- "Explain Cerberus consensus" → `radix_glossary` with `themes=["cerberus"]`
- "What is sharding?" → `radix_core_concepts` with `concepts=["sharding"]`
- "Find DeFi dApps" → `radix_dapps` with `category="DeFi"`
- "Where can I buy XRD?" → `xrd_trading_venues` with `type="onramp"`
- "Radix Discord and Telegram links" → `radix_socials`

**Multi-tool workflows:**

- Resolve an RNS domain, then check wallet tokens: `rns_to_address` → `tokens_in_wallet`
- Research a token on Radix, then compare to CMC data: `token_details` → `tokens_on_cmc` → `token_details_from_cmc`
- Full wallet analysis: `tokens_in_wallet` + `performance_of_wallet` + `distribution_of_wallet` + `latest_transactions`
- DeFi overview: `attos_earn_stats` + `attos_earn_pools` + `attos_earn_strategies`

## Data Sources & Freshness

- **Token prices**: Astrolescent API, cached up to 24 hours, updated hourly via cron
- **Wallet data**: Radix Gateway API (Babylon mainnet), real-time
- **CoinMarketCap**: Live API queries
- **Ecosystem updates**: Aggregated daily/weekly/monthly from Telegram channels and official sources
- **Validators**: Radix Gateway API, real-time
- **dApps directory**: Curated dataset, periodically updated
- **Attos Earn**: Live API queries to earn-api.attos.world (Beta)
- **Trading venues & socials**: Curated static datasets

## Rate Limits

60 requests per minute per IP. Returns HTTP 429 with `Retry-After` header when exceeded.

## About

Powered by [Emily](https://www.ineedemily.com) - an AI assistant for the Radix DLT ecosystem.
Data sourced from the [Radix Gateway API](https://docs.radixdlt.com/docs/network-apis), [Astrolescent](https://astrolescent.com), [CoinMarketCap](https://coinmarketcap.com), and [Attos Earn](https://earn.attos.world).
