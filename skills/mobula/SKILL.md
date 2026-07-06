---
name: mobula
displayName: Mobula - Crypto Market Data & Wallet Intelligence
description: >
  Real-time crypto market data, wallet portfolio tracking, and token
  analytics across 88+ blockchains. Use when the user wants to check
  any token price (by name, symbol, or contract address), look up wallet
  balances and holdings across all chains, get historical price data,
  track portfolio PnL, monitor whale wallets, find new tokens, or get
  oracle-grade pricing. Requires free API key from mobula.io.
version: 1.0.1
author: Mobula
category: crypto
tags:
  - crypto
  - market-data
  - wallet
  - portfolio
  - defi
  - blockchain
  - price-api
  - token-analytics
  - multi-chain
  - real-time
requiredEnvVars:
  - MOBULA_API_KEY
homepage: https://mobula.io
docs: https://docs.mobula.io
repository: https://github.com/Flotapponnier/Crypto-date-openclaw
---

# Mobula - Multi-Chain Crypto Data Intelligence

Real-time crypto market data, wallet tracking, and on-chain analytics across **88+ blockchains**. Oracle-grade pricing trusted by Chainlink, Supra, and API3.

## When to Use This Skill

**USE WHEN** the user:
- Asks about any token price, volume, market cap, or price change
- Wants to check a wallet's holdings or portfolio value
- Needs historical price data for charts or analysis
- Mentions a contract address and wants token info
- Asks about tokens on specific chains (Base, Arbitrum, Solana, etc.)
- Wants cross-chain portfolio overview
- Needs batch data on multiple tokens at once
- Asks about token liquidity, ATH, ATL, or trading volume
- Wants to track whale wallets or monitor significant transactions
- Needs to find new tokens matching specific criteria

**DON'T USE WHEN**:
- User wants to execute trades (use bankr skill instead)
- User wants DEX swap quotes (use defi skill)
- User wants exchange-specific data (use okx/binance skills)

---

## Core Capabilities

### 1. Market Data (`mobula_market_data`)

**Endpoint:** `GET https://api.mobula.io/api/1/market/data`

Get real-time price, volume, market cap, and liquidity for any token across all supported chains.

**Parameters:**
- `asset` (required): Token name, symbol, or contract address
  - Examples: "Bitcoin", "ETH", "0x532f27101965dd16442e59d40670faf5ebb142e4"
- `blockchain` (optional): Specific chain to query
  - Examples: "base", "arbitrum", "ethereum", "solana", "polygon"

**Returns:**
- Current price (USD)
- Price changes: 1h, 24h, 7d, 30d (percentage and absolute)
- Volume (24h)
- Market cap
- Fully diluted valuation
- Liquidity
- All-time high (ATH) and all-time low (ATL) with dates
- Total supply, circulating supply

**Usage examples:**
- "What's the price of Bitcoin?"
- "Show me BRETT's market data on Base"
- "Get data for contract 0x532f27101965dd16442e59d40670faf5ebb142e4"
- "Is ETH pumping or dumping right now?"
- "What's the market cap of PEPE?"

**When to use:**
- User asks for price of any token
- User wants to know if something is pumping/dumping
- Analyzing token fundamentals (mcap, liquidity, volume)
- Comparing tokens
- Setting up price alerts

---

### 2. Wallet Portfolio (`mobula_wallet_portfolio`)

**Endpoint:** `GET https://api.mobula.io/api/1/wallet/portfolio`

Get complete portfolio for any wallet across all 88 chains in a single call.

**Parameters:**
- `wallet` (required): Wallet address
  - Format: "0x..." or ENS name (e.g., "vitalik.eth")
- `blockchains` (optional): Comma-separated list to filter specific chains
  - Default: all chains
- `cache` (optional): Use cached data (faster, slightly less fresh)

**Returns:**
- All tokens held with:
  - Token name, symbol, address
  - Balance (amount and USD value)
  - Current price
  - Price change 24h
  - Estimated profit/loss
  - Chain
- Total portfolio value (USD)
- Portfolio allocation by token (percentages)
- NFTs (if present)

**Usage examples:**
- "Show the portfolio for wallet 0x123..."
- "What tokens does vitalik.eth hold?"
- "Check my wallet balance"
- "What's the total value of this wallet?"
- "Show me the top 5 holdings in this wallet"

**When to use:**
- Portfolio tracking
- Wallet analysis
- Checking holdings before/after trades
- Monitoring allocation
- Setting up portfolio alerts

---

### 3. Historical Price Data (`mobula_market_history`)

**Endpoint:** `GET https://api.mobula.io/api/1/market/history`

Get historical price data for any token with flexible timeframes.

**Parameters:**
- `asset` (required): Token name, symbol, or address
- `from` (optional): Start timestamp (Unix seconds)
- `to` (optional): End timestamp (Unix seconds)
- `period` (optional): Data granularity
  - Options: "1h", "1d", "1w"
  - Default: auto-selected based on timeframe

**Returns:**
- Array of price points with timestamps
- Volume at each point
- Market cap at each point

**Usage examples:**
- "Show me ETH price for the last 30 days"
- "What was this token's price on January 1st?"
- "Has this token been pumping or dumping this week?"
- "Chart the price movement of BTC in the last 7 days"

**When to use:**
- Analyzing trends
- Calculating historical PnL
- Comparing price action across timeframes
- Identifying patterns (breakouts, supports, resistance)

---

### 4. Recent Trades (`mobula_market_trades`)

**Endpoint:** `GET https://api.mobula.io/api/1/market/trades`

Live trade feed for any token across all DEXs and chains.

**Parameters:**
- `asset` (required): Token name, symbol, or address
- `limit` (optional): Number of trades to return (default: 50, max: 300)

**Returns:**
- Array of recent trades with:
  - Timestamp
  - Type (buy/sell)
  - Amount (tokens and USD)
  - Price at trade
  - Wallet address (buyer/seller)
  - DEX and chain
  - Transaction hash

**Usage examples:**
- "Show recent trades for this token"
- "Who's buying PEPE right now?"
- "Any whale movements on this token?"
- "What's the last 10 trades on this token?"

**When to use:**
- Whale watching
- Detecting unusual activity (large buys/sells)
- Volume verification
- Sentiment analysis (more buys vs sells)

---

### 5. Wallet Transaction History (`mobula_wallet_transactions`)

**Endpoint:** `GET https://api.mobula.io/api/1/wallet/transactions`

Full transaction history for any wallet across all chains.

**Parameters:**
- `wallet` (required): Wallet address
- `from` (optional): Start timestamp
- `to` (optional): End timestamp
- `asset` (optional): Filter by specific token
- `limit` (optional): Number of transactions (default: 100)

**Returns:**
- Array of transactions:
  - Type (swap, transfer, mint, burn)
  - Tokens involved (from/to)
  - Amounts
  - USD values at time of transaction
  - Timestamp
  - Chain
  - Transaction hash

**Usage examples:**
- "What did this wallet buy recently?"
- "Show me the last 10 transactions for 0x123..."
- "When did this wallet last sell ETH?"
- "Track this whale's activity"

**When to use:**
- Wallet monitoring
- Whale tracking
- Pattern detection (what they buy/sell)
- Transaction verification

---

### 6. Multi-Asset Data (`mobula_market_multi`)

**Endpoint:** `GET https://api.mobula.io/api/1/market/multi-data`

Get market data for multiple tokens in a single request (batch endpoint).

**Parameters:**
- `assets` (required): Comma-separated list of token names/symbols/addresses
  - Example: "Bitcoin,Ethereum,Solana" or "BTC,ETH,SOL"
  - Max: 500 tokens per request

**Returns:**
- Same data as `mobula_market_data` but for multiple tokens
- Efficient for portfolio analysis, watchlists, market overviews

**Usage examples:**
- "Compare BTC, ETH, and SOL performance today"
- "Show me the top movers from my watchlist"
- "Get prices for these 10 tokens: [list]"

**When to use:**
- Portfolio valuation
- Watchlist updates
- Market overview (top coins)
- Batch price checks

---

### 7. Token Metadata (`mobula_metadata`)

**Endpoint:** `GET https://api.mobula.io/api/1/metadata`

Get detailed metadata for any token.

**Parameters:**
- `asset` (required): Token name, symbol, or address

**Returns:**
- Name, symbol, logo
- Description
- Website, Twitter, Telegram, Discord links
- Contract addresses across all chains
- Launch date
- Categories/tags

**Usage examples:**
- "Tell me about this token"
- "What's the website for this project?"
- "Where can I find their community?"

**When to use:**
- Research on new tokens
- Verifying legitimacy
- Finding official links

---

## Authentication

**Required:** All API requests require authentication via API key.

**Setup:**
1. Get a free API key at **https://mobula.io** (100 requests/minute free tier)
2. Set environment variable:
   ```bash
   export MOBULA_API_KEY="your_key_here"
   ```
3. Restart OpenClaw agent

**Header format:**
```
Authorization: ${MOBULA_API_KEY}
```

**If authentication fails (401/403):**
- Verify key is set: `echo $MOBULA_API_KEY`
- Regenerate key at https://mobula.io if expired
- Check rate limits (100 req/min free, upgrade for more)

---

## Privacy & Security

**IMPORTANT - Read Before Using:**

### What This Skill Accesses
- **Public blockchain data only**: Wallet addresses, token prices, transaction history
- **No private keys**: Never provide private keys, seed phrases, or passwords to this skill
- **No sensitive credentials**: Skill only requires Mobula API key (public data access)

### Wallet Address Privacy
- Wallet addresses queried via this skill are sent to Mobula's API (https://api.mobula.io)
- Querying a wallet address reveals its holdings publicly (on-chain data is already public)
- **Only use public wallet addresses** you're comfortable sharing
- **Never enter addresses** you want to keep private or that link to your identity

### API Key Scope
- Mobula API keys provide **read-only** access to public blockchain data
- Keys can be scoped, rotated, and revoked at https://mobula.io
- Free tier: 100 requests/minute
- Consider using a separate API key for testing vs production

### Data Retention
- Mobula may log API requests for analytics and rate limiting
- Refer to Mobula's privacy policy: https://mobula.io/privacy
- Do not query wallets or data you consider sensitive

### Best Practices
1. Use throwaway/test API keys for initial testing
2. Only query public wallet addresses (e.g., vitalik.eth, well-known addresses)
3. Avoid querying your personal wallets if you want privacy
4. Rotate API keys periodically
5. Monitor rate limits and usage at https://mobula.io

---

## Smart Monitoring Patterns with Heartbeat

OpenClaw's heartbeat system checks conditions every ~30 minutes. Use this for proactive monitoring.

### Pattern 1: Portfolio Guardian

Every heartbeat:
1. Fetch user's wallet via `mobula_wallet_portfolio`
2. Calculate allocation percentages
3. Check conditions:
   - Any token >40% of portfolio → suggest rebalancing
   - Any token down >15% in 24h → alert with context
   - Total portfolio changed >10% → notify
4. Store previous values in memory to detect changes
5. Send daily summary at user's preferred time

### Pattern 2: Whale Watching

Every heartbeat:
1. Check transactions for tracked wallets via `mobula_wallet_transactions`
2. If new significant transaction (>$50K):
   - Get token details via `mobula_market_data`
   - Check recent trades via `mobula_market_trades`
   - Cross-check if other tracked whales bought the same token
3. If multiple whales buying → priority alert

### Pattern 3: Token Scout (Autonomous Discovery)

Every 4-6 hours on heartbeat:
1. User defines criteria (store in memory):
   - Chains: Base, Arbitrum
   - Market cap: <$5M
   - Liquidity: >$100K
   - Volume change 24h: >+50%
2. Search/filter tokens via `mobula_market_data` queries
3. For each match:
   - Get 7-day history via `mobula_market_history`
   - Check metadata via `mobula_metadata`
   - Calculate risk score
4. Send top 3 with analysis

### Pattern 4: Smart Price Alerts

Instead of simple "price > X" alerts, create contextual ones:

Example: "Alert me if Bitcoin moves >5% in 1 hour BUT only if volume is 2x above 24h average"

Every heartbeat:
1. Get current price and volume via `mobula_market_data`
2. Compare to price from 1 hour ago (stored in memory)
3. Check if volume condition met
4. Only alert if BOTH conditions true

---

## Combining Multiple Endpoints for Rich Insights

### Example: Full Token Analysis

User asks: "Should I buy this token?"

1. `mobula_market_data` → current price, mcap, volume, liquidity
2. `mobula_market_history` → 7d and 30d trend
3. `mobula_market_trades` → recent activity (accumulation or distribution?)
4. `mobula_metadata` → project info, socials, contract verification

Response format:
```
TOKEN Analysis

Price: $0.042 (down 8% 24h, up 156% 7d)
- Near 7d high, down from $0.051
- Still up 400% from 30d low

Fundamentals:
- Mcap: $2.1M (small cap, high risk/reward)
- Liquidity: $280K (decent for size)
- Volume: $1.2M 24h (healthy)

On-chain:
- Recent trades show buying pressure (3:1 buy/sell ratio)
- 2 large buys ($50K+) in last 2h

Project:
- Contract verified
- Active Twitter (12K followers)

Risk: Small cap, high volatility. Don't ape more than you can lose.
```

---

## Response Formatting Guidelines

### Prices
- Always show direction: "up 12.4%" or "down 3.2%"
- Include timeframe: "up 12.4% (24h)"
- Add context: "Price $0.042 (up 12% 24h, down 8% from ATH)"

### Large Numbers
- Format clearly: "$1.23M", "$456K", "$45.6B"
- Not: "$1234567"

### Percentages
- Use for allocations: "ETH: 42% of portfolio"
- Use for changes: "down 15.3% in 24h"

### Context is Key
Don't just say "price is $0.003"
Say: "Price $0.003 (down 8% 24h, down 65% from ATH of $0.089 on Dec 1st, but up 12% from 7d low)"

---

## Common User Requests & How to Handle

### "Set up alerts for [token]"
1. Acknowledge the request
2. Ask for specific conditions (price threshold? percentage move? volume spike?)
3. Confirm you'll monitor via heartbeat
4. Store the alert config in memory
5. Confirm: "I'll check [token] every 30min and alert you on [channel] if [condition]"

### "Track this wallet"
1. Add wallet to monitoring list
2. Ask what to watch for:
   - All activity?
   - Only large trades (>$X)?
   - Specific tokens?
3. Store in memory
4. Confirm monitoring is active

### "Find tokens matching [criteria]"
1. Clarify criteria:
   - Chains?
   - Market cap range?
   - Volume requirements?
   - Liquidity minimum?
2. Set up periodic checks (suggest 4-6h interval)
3. Ask how many results they want
4. Start monitoring on next heartbeat

### "What's happening in crypto right now?"
1. Check major tokens (BTC, ETH, SOL, BNB) via `mobula_market_multi`
2. Identify any major moves (>5% in 24h)
3. Check volume leaders
4. Provide concise overview

---

## Error Handling

### API Key Issues
- **No key set:** "I need a Mobula API key to fetch crypto data. Get one free at https://mobula.io then add it to your environment with `export MOBULA_API_KEY='your_key'`"
- **Invalid key:** "Your API key seems invalid. Please check it at https://mobula.io"
- **Rate limited:** "You've hit the API rate limit. Upgrade your plan at https://mobula.io for higher limits, or I'll retry in a few minutes."

### Token Not Found
- "I couldn't find that token by name. Could you provide the contract address? Or check the spelling?"
- Suggest similar tokens if possible
- Offer to search by contract address

### Wallet Issues
- **Invalid address:** "That doesn't look like a valid wallet address. Should be 0x... (42 characters) or an ENS name like vitalik.eth"
- **No activity:** "This wallet has no activity or balance. Is this the correct address and chain?"

---

## Rate Limits & Best Practices

### Respect Rate Limits
- Free tier: 100 requests/minute
- Use `mobula_market_multi` for batch queries instead of multiple `mobula_market_data` calls
- Cache data in memory when appropriate (metadata doesn't change often)

### Efficient Heartbeat Usage
- Don't call every endpoint on every heartbeat
- Only fetch what's needed based on active monitoring tasks
- Batch requests when possible
- Store previous values to detect changes

---

## Supported Blockchains

88+ chains including: Ethereum, Base, Arbitrum, Optimism, Polygon, BNB Chain, Avalanche, Solana, Fantom, Cronos, and many more.

Full list: https://docs.mobula.io/blockchains

---

## Resources

- **Mobula Website:** https://mobula.io
- **API Documentation:** https://docs.mobula.io
- **Skill Repository:** https://github.com/Flotapponnier/Crypto-date-openclaw
- **Support:** Open an issue on GitHub or visit Mobula Discord

---

## Version History

- **1.0.1** (2024-02-20): Security & clarity improvements
  - Added comprehensive Privacy & Security section
  - Clarified API key requirement (removed confusing "No API key needed for dev/testing")
  - Enhanced authentication documentation
  - Added best practices for API key management
  - Explicit warnings about wallet address privacy

- **1.0.0** (2024-02-20): Initial release
  - 7 core endpoints (market data, portfolio, history, trades, transactions, multi-data, metadata)
  - Heartbeat monitoring patterns
  - Smart alert examples
  - Comprehensive documentation
