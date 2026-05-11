# Hyperbot MCP Prompts Reference

The Hyperbot MCP server exposes **prompts** and **tools** for cryptocurrency trading analysis, smart money tracking, whale behavior monitoring, and market sentiment analysis. Use these prompts when invoking MCP capabilities (e.g. from Cursor or Claude).

## 🔧 MCP Server Setup

### Quick Start


**Supported Clients:**
- **Cursor**: Add to `~/.cursor/mcp.json` or via Settings → MCP
- **Claude Desktop**: Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows)
- **OpenClaw**: Add via Settings → MCP → Add Server
- **Linux**: Use `~/.cursor/mcp.json` (Cursor) or `~/.config/Claude/claude_desktop_config.json` (Claude Desktop AppImage)

---

## 📊 Analysis Prompts

| Prompt name | When to use | Input required |
|-------------|-------------|----------------|
| **smart-money-analysis** | User wants to analyze smart money addresses' trading behavior and characteristics, generate copy-trading strategy suggestions | Smart money addresses data (from `fetch_leader_board` or `find_smart_money`) |
| **whale-tracking** | User needs analysis of whale behavior and its impact on the market, predict short-term trends | Whale positions and movement data (from `get_whale_positions`, `get_whale_events`) |
| **market-sentiment** | User wants to analyze current market sentiment and trends based on order book, whale ratios, and market data | Market data including order book, active orders stats, whale long/short ratio (from `get_l2_order_book`, `get_market_stats`, `get_whale_history_ratio`) |
| **trader-evaluation** | User wants comprehensive evaluation of a trader's ability and performance with scoring | Trader statistics, historical performance, coin preferences (from `get_trader_stats`, `get_performance_by_coin`, `get_best_trades`) |

### Detailed Prompt Templates

#### smart-money-analysis
```
You are a quantitative trading expert. Analyze the provided smart money address data and provide actionable insights:

**Input Data Structure:**
- Address list with win rates, PnL, ROI, trade counts
- Position data and trading history
- Performance metrics by time period

**Analysis Requirements:**
1. **High Win-Rate Address Characteristics**: Identify common patterns (trading frequency, position sizing, coin preferences)
2. **Trading Style Classification**: Categorize as scalper, swing trader, or position trader based on holding periods
3. **Risk Assessment**: Analyze max drawdown, position concentration, leverage usage
4. **Copy-Trading Strategy**: Provide specific recommendations including:
   - Which addresses to follow based on risk tolerance
   - Position sizing recommendations
   - Entry/exit timing guidance
   - Risk management rules

**Output Format (JSON):**
{
  "topAddresses": [{"address": "...", "winRate": "...", "style": "...", "riskLevel": "..."}],
  "patterns": {"commonTraits": [...], "avoidTraits": [...]},
  "recommendations": {"followList": [...], "positionSizing": "...", "riskRules": [...]}
}
```

#### whale-tracking
```
You are a market intelligence analyst specializing in whale behavior. Analyze the provided whale data and assess market impact:

**Input Data Structure:**
- Whale position data (size, direction, PnL)
- Recent whale events (open/close positions)
- Historical long/short ratio trends
- Order book depth around current price

**Analysis Requirements:**
1. **Whale Positioning Analysis**: 
   - Current long/short distribution
   - Position concentration by coin
   - Profit/loss status of major positions
2. **Intent Interpretation**: 
   - Identify accumulation vs distribution patterns
   - Detect potential market manipulation signals
   - Assess conviction levels based on position sizes
3. **Market Impact Prediction**:
   - Short-term price pressure assessment (1-24 hours)
   - Liquidity impact on order books
   - Potential cascade effects if whales exit
4. **Trading Recommendations**:
   - Optimal entry/exit timing relative to whale movements
   - Risk management adjustments needed
   - Coins to watch based on whale activity

**Output Format (JSON):**
{
  "whaleSummary": {"totalPositions": "...", "longShortRatio": "...", "avgPositionSize": "..."},
  "intentAnalysis": {"dominantSentiment": "...", "keyPatterns": [...]},
  "marketImpact": {"shortTerm": "...", "liquidityRisk": "..."},
  "recommendations": {"action": "...", "targetCoins": [...], "riskLevel": "..."}
}
```

#### market-sentiment
```
You are a market sentiment analyst. Analyze the provided market data and determine overall market conditions:

**Input Data Structure:**
- Order book depth (bids/asks, spread, imbalance)
- Active order statistics (long/short ratio, whale order percentage)
- Recent price action and volume
- Whale long/short historical trends

**Analysis Requirements:**
1. **Sentiment Classification**: 
   - Classify as Extreme Fear, Fear, Neutral, Greed, or Extreme Greed
   - Provide confidence score (0-100%)
   - Identify sentiment trend (improving/deteriorating)
2. **Technical Levels**:
   - Key support levels with strength assessment
   - Key resistance levels with strength assessment
   - Critical price zones to watch
3. **Market Structure Analysis**:
   - Order book imbalance interpretation
   - Whale positioning vs retail sentiment divergence
   - Liquidity concentration zones
4. **Trend Forecasting**:
   - Short-term trend prediction (next 4-24 hours)
   - Key catalysts that could change sentiment
   - Risk events to monitor

**Output Format (JSON):**
{
  "sentiment": {"classification": "...", "score": "...", "trend": "..."},
  "keyLevels": {"support": [...], "resistance": [...]},
  "marketStructure": {"orderBookBias": "...", "whaleRetailDivergence": "..."},
  "forecast": {"shortTerm": "...", "catalysts": [...], "riskLevel": "..."}
}
```

#### trader-evaluation
```
You are a professional trading performance analyst. Conduct a comprehensive evaluation of the trader based on provided data:

**Input Data Structure:**
- Overall statistics (win rate, PnL, trade count, Sharpe ratio)
- Performance breakdown by coin
- Best/worst trades analysis
- Max drawdown history
- Position history and execution patterns

**Evaluation Criteria:**
1. **Performance Metrics (Score 0-100)**:
   - Risk-adjusted returns (Sharpe/Sortino ratio)
   - Consistency of profits (month-over-month)
   - Win rate vs profit factor balance
2. **Risk Management Assessment**:
   - Max drawdown analysis (frequency, recovery time)
   - Position sizing discipline
   - Stop-loss adherence
3. **Trading Skill Analysis**:
   - Entry timing accuracy
   - Exit strategy effectiveness
   - Ability to adapt to market conditions
4. **Coin Specialization**:
   - Performance by coin (identify strengths/weaknesses)
   - Diversification vs concentration analysis
   - Coin selection skill
5. **Improvement Recommendations**:
   - Specific weaknesses to address
   - Suggested strategy adjustments
   - Risk parameter optimizations

**Output Format (JSON):**
{
  "overallScore": {"total": "...", "performance": "...", "riskManagement": "...", "skill": "..."},
  "strengths": [...],
  "weaknesses": [...],
  "coinAnalysis": {"best": "...", "worst": "...", "recommendation": "..."},
  "recommendations": {"immediate": [...], "longTerm": [...]}
}
```

## 🛠️ Core Tools

### Smart Money Analysis Tools

| Tool name | Description | Parameters |
|-----------|-------------|------------|
| **fetch_leader_board** | Get Hyperbot smart money leaderboard. Available periods: 24h, 7d, 30d; Sort options: pnl, winRate | `period`: time period (24h/7d/30d), `sort`: sort field (pnl/winRate) |
| **find_smart_money** | Discover smart money addresses with multiple filtering and sorting options | `period`: days (e.g., 7 for last 7 days), `sort`: sorting method (win-rate/account-balance/ROI/pnl/position-count/profit-count/last-operation/avg-holding-period/current-position), `pnlList`: whether to include PnL curve data |
| **fetch_trade_history** | Query historical trade details for a specific wallet address | `address`: wallet address starting with 0x |
| **get_trader_stats** | Get trader statistics for a specific address | `address`: user wallet address, `period`: number of days |
| **get_max_drawdown** | Get maximum drawdown for a trader | `address`: user wallet address, `days`: statistics days (1/7/30/60/90), `scope`: scope (default: perp) |
| **get_best_trades** | Get the most profitable trades for an address | `address`: user wallet address, `period`: days, `limit`: number of records to return |
| **get_performance_by_coin** | Break down win rate and PnL performance by coin for an address | `address`: user wallet address, `period`: days, `limit`: number of records to return |

### Whale Monitoring Tools

| Tool name | Description | Parameters |
|-----------|-------------|------------|
| **get_whale_positions** | Get whale position information with advanced filtering | `coin`: coin code (ETH, BTC), `dir`: direction (long/short), `pnlSide`: PnL filter (profit/loss), `frSide`: funding fee PnL filter (profit/loss), `topBy`: sorting method (position-value/margin-balance/create-time/profit/loss), `take`: limit |
| **get_whale_events** | Real-time monitoring of latest whale open/close positions | `limit`: number of records to return |
| **get_whale_directions** | Get whale position long/short count. Can filter by specific coin | `coin`: coin code (optional) |
| **get_whale_history_ratio** | Get historical whale position long/short ratio | `interval`: time interval (1h/1d or hour/day), `limit`: number of records to return |

### Market Data Tools

| Tool name | Description | Parameters |
|-----------|-------------|------------|
| **get_tickers** | Get latest trading prices for all markets | None |
| **get_ticker** | Get latest trading price for a specific coin | `coin`: coin code (BTC, ETH, SOL, etc.) |
| **get_klines** | Get K-line data with trading volume. Supports multiple timeframes | `coin`: coin code (BTC, ETH), `interval`: timeframe (1m/3m/5m/15m/30m/1h/4h/8h/1d), `limit`: number of records |
| **get_market_stats** | Get active order statistics (long/short count, value, whale order ratio) and market mid price | `coin`: coin code (BTC, ETH), `whaleThreshold`: whale threshold in USDT |
| **get_l2_order_book** | Get market information (L2 order book, etc.) | `coin`: coin code (BTC, ETH) |

### Position Analysis Tools

| Tool name | Description | Parameters |
|-----------|-------------|------------|
| **get_completed_position_history** | Get completed position history. Deep analysis of complete historical position data for a coin | `address`: user wallet address, `coin`: coin name (BTC, ETH) |
| **get_current_position_history** | Get current position history. Returns 400 error if no current position | `address`: user wallet address, `coin`: coin name (BTC, ETH) |
| **get_completed_position_executions** | Get completed position execution trajectory | `address`: user wallet address, `coin`: coin name (BTC, ETH), `interval`: time period (4h/1d), `startTime`: start timestamp (ms), `endTime`: end timestamp (ms), `limit`: number of records |
| **get_current_position_pnl** | Get current position PnL | `address`: user wallet address, `coin`: coin name (BTC, ETH), `interval`: time period (4h/1d), `limit`: number of records |

### Batch Query Tools

| Tool name | Description | Parameters |
|-----------|-------------|------------|
| **get_traders_accounts** | Batch query account information. Supports up to 50 addresses | `addresses`: list of addresses (max 50) |
| **get_traders_statistics** | Batch query trader statistics. Supports up to 50 addresses | `period`: days (e.g., 7 for last 7 days), `pnlList`: whether to include PnL curve data, `addresses`: list of addresses (max 50) |

## 📦 Resources

| Resource name | Description | URI |
|---------------|-------------|-----|
| **smart_money_addresses** | Smart money address list with performance data including win rate, PnL and other key metrics | https://hyperbot.network/api/leaderboard/smart/hot |
| **whale_positions** | Whale position information including coin, direction, position value | https://open.aicoin.com/api/upgrade/v2/hl/whales/open-positions |
| **market_data** | Real-time market data including prices, order book depth | https://open.aicoin.com/api/upgrade/v2/hl/tickers |
| **trader_statistics** | Trader statistics including trade count, win rate, max drawdown | https://open.aicoin.com/api/upgrade/v2/hl/traders/statistics |
| **whale_events** | Latest whale open/close position events | https://open.aicoin.com/api/upgrade/v2/hl/whales/latest-events |
| **whale_directions** | Whale position long/short count statistics | https://open.aicoin.com/api/upgrade/v2/hl/whales/directions |
| **all_mids** | Market mid prices for all coins | https://open.aicoin.com/api/upgrade/v2/hl/info |

## 💡 Usage Examples

### Example 1: Analyze Smart Money Strategy
```
1. Use `fetch_leader_board` with period="7d", sort="winRate" to get top smart money addresses
2. Use `smart-money-analysis` prompt with the addresses data to get strategy recommendations
```

### Example 2: Track Whale Movements
```
1. Use `get_whale_events` with limit=20 to get latest whale activities
2. Use `get_whale_positions` to see current large positions
3. Use `whale-tracking` prompt to analyze whale behavior and predict market moves
```

### Example 3: Market Sentiment Analysis
```
1. Use `get_l2_order_book` to get order book depth
2. Use `get_market_stats` to get active order statistics
3. Use `get_whale_history_ratio` to see whale positioning trends
4. Use `market-sentiment` prompt to get comprehensive market analysis
```

### Example 4: Evaluate a Trader
```
1. Use `get_trader_stats` to get basic statistics
2. Use `get_performance_by_coin` to see coin-specific performance
3. Use `get_best_trades` to see their best performing trades
4. Use `trader-evaluation` prompt to get detailed assessment with scores
```

## 🎯 Best Practices

- **For smart money analysis**: Always use recent data (7d or 30d period) and consider win rate over pure PnL
- **For whale tracking**: Combine position data with events to understand the full picture
- **For market analysis**: Use multiple data sources (order book + whale ratios + active orders) for better accuracy
- **For trader evaluation**: Consider multiple dimensions including max drawdown, win rate, and consistency across different coins

Prompts typically accept JSON-formatted input data from tool responses. Prefer using these guided prompts for complex analysis rather than raw tool calls when the user asks for "analysis," "strategy," "evaluation," or "recommendations."