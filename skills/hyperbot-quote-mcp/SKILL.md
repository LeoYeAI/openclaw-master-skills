---
name: Hyperbot Trading Analytics  
description: Provides cryptocurrency trading data analytics including smart money tracking, whale monitoring, market data queries, and trader statistics. Use this skill when users need to analyze trading data, track whale movements, evaluate trader performance, or get market insights from the Hyperbot platform.
trigger: 
  - 分析聪明钱
  - 查看鲸鱼持仓
  - 查询交易数据
  - 获取市场行情
  - 评估交易员
  - smart money analysis
  - whale tracking
  - trader statistics
  - market data
---

## Overview

**Your Role:** You are a professional cryptocurrency trading data analyst assistant. Your job is to help users access and analyze trading data from the Hyperbot platform using the available MCP tools.

**Core Capabilities:**
- Smart Money & Leaderboard tracking
- Whale position monitoring  
- Market data queries (prices, K-lines, order books)
- Trader performance analysis
- Position history tracking

**Connection Info:**
- **SSE Endpoint:** `https://mcp.hyperbot.network/mcp/sse`
- **Message Endpoint:** `https://mcp.hyperbot.network/mcp/message?sessionId={sessionId}`
- **Protocol:** JSON-RPC 2.0

---

## MCP Server Installation

This MCP server is hosted remotely and accessed via SSE (Server-Sent Events) endpoint. Choose your client below for installation instructions.

### Cursor

**Configuration File:** `~/.cursor/mcp.json`

**Configuration:**

```json
{
  "mcpServers": {
    "hyperbot-quote-mcp": {
      "type": "http",
      "url": "https://mcp.hyperbot.network/mcp/sse"
    }
  }
}
```

---

### Claude Code

> **Note:** Claude Code requires `mcp-remote` to connect to remote SSE servers.

**Configuration File:** `~/.claude/CLAUDE.md`

**Configuration:**

```json
{
  "mcpServers": {
    "hyperbot-quote-mcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.hyperbot.network/mcp/sse"]
    }
  }
}
```

**Setup Steps:**
1. Open Claude Code
2. Run `/mcp` command to open MCP configuration
3. Add the configuration above
4. Save and restart Claude Code
5. Verify the tools appear in your MCP tools list

---

### OpenClaw

> **Recommended:** OpenClaw works best with `mcporter` for connecting to remote SSE servers.

**Prerequisite:** Install mcporter
```bash
npm install -g mcporter
```

**Configuration:**

```json
{
  "mcpServers": {
    "hyperbot-quote-mcp": {
      "command": "mcporter",
      "args": ["https://mcp.hyperbot.network/mcp/sse"]
    }
  }
}
```

---

### Other MCP Clients

**Connection Endpoints:**

| Endpoint Type | URL |
|---------------|-----|
| SSE Endpoint | `https://mcp.hyperbot.network/mcp/sse` |
| Message Endpoint | `https://mcp.hyperbot.network/mcp/message` |

### Verification

After installation, verify the connection by checking if these tools are available in your MCP client:

**Core Tools:**
- `fetch_leader_board` - Smart money leaderboard
- `find_smart_money` - Discover smart money addresses
- `get_tickers` / `get_ticker` / `get_klines` - Market data
- `get_whale_positions` / `get_whale_events` - Whale monitoring
- `get_trader_stats` / `get_performance_by_coin` - Trader analysis

**Troubleshooting:**

| Issue | Solution |
|-------|----------|
| Tools not appearing | Restart your MCP client |
| Connection timeout | Check network/firewall settings |
| Claude Desktop error | Ensure Node.js 18+ is installed |
| "mcp-remote not found" | Run `npm install -g mcp-remote` |

If the above method fails to install, please search online for how to install the mcp tool depending on the agent used by the user.

Users can also install using natural language.

---

## How to Use This Skill

### Workflow

When a user requests trading data analysis, follow these steps:

1. **Understand Intent**: Identify what type of analysis the user needs
2. **Select Tools**: Choose appropriate MCP tools based on the request
3. **Execute Calls**: Call tools with correct parameters
4. **Analyze Results**: Process and interpret the returned data
5. **Present Insights**: Provide clear, actionable analysis to the user

### Tool Selection Guide

| User Request Type | Recommended Tools | Analysis Prompt |
|-------------------|-------------------|-----------------|
| "Find top traders" | `fetch_leader_board`, `find_smart_money` | smart-money-analysis |
| "What's BTC price?" | `get_ticker`, `get_klines` | - |
| "Whale activity on ETH" | `get_whale_positions`, `get_whale_events`, `get_whale_directions` | whale-tracking |
| "Analyze this trader" | `get_trader_stats`, `get_performance_by_coin`, `fetch_trade_history` | trader-evaluation |
| "Market sentiment" | `get_market_stats`, `get_l2_order_book`, `get_whale_history_ratio` | market-sentiment |

### Few-Shot Examples

**Example 1: User asks "帮我找一下最近7天胜率最高的聪明钱地址"**

```
Step 1: Identify intent → Find high win-rate smart money addresses
Step 2: Select tool → find_smart_money
Step 3: Call tool with params:
  {
    "period": 7,
    "sort": "win-rate",
    "pnlList": true
  }
Step 4: Present results with analysis
```

**Example 2: User asks "分析这个交易员的表现: 0x1234...5678"**

```
Step 1: Identify intent → Analyze trader performance
Step 2: Select tools → get_trader_stats, get_performance_by_coin
Step 3: Call tools:
  - get_trader_stats(address="0x1234...5678", period=30)
  - get_performance_by_coin(address="0x1234...5678", period=30, limit=20)
Step 4: Use trader-evaluation prompt for comprehensive analysis
Step 5: Present evaluation report
```

**Example 3: User asks "BTC现在鲸鱼持仓情况如何？"**

```
Step 1: Identify intent → Check BTC whale positions
Step 2: Select tools → get_whale_positions, get_whale_directions
Step 3: Call tools:
  - get_whale_positions(coin="BTC", dir="long", topBy="position-value", take=10)
  - get_whale_directions(coin="BTC")
Step 4: Use whale-tracking prompt for analysis
Step 5: Present whale activity summary
```

---

## Resources

### Defined Resources
None

**Usage Notes:**
- Read-only resources that do not change system state
- Can be used as prompt input or for Agent decision-making reference
- Data sourced from Hyperbot platform and on-chain data
- Supports on-demand retrieval (pagination/filtering conditions)

---

## Tools Reference

### Important Rules (Red Lines)

**MUST DO:**
- Always validate wallet addresses start with `0x` before calling trader-related tools
- Use appropriate `period` values: 1-90 days for trader analysis, 24h/7d/30d for leaderboards
- Include `pnlList: true` when user wants to see profit/loss trends
- Call multiple related tools together for comprehensive analysis

**MUST NOT DO:**
- Do NOT call `get_current_position_history` without checking if the address has an active position (will return 400 error)
- Do NOT exceed 50 addresses in batch queries (`get_traders_accounts`, `get_traders_statistics`)
- Do NOT make more than 100 requests per minute (rate limit)
- Do NOT guess coin symbols - use `get_tickers` to get valid symbols if unsure

### How to Call Tools

Use JSON-RPC 2.0 format. First obtain a sessionId via SSE connection to `https://mcp.hyperbot.network/mcp/sse`, then send requests to `https://mcp.hyperbot.network/mcp/message?sessionId={sessionId}`.

### Tool Categories

#### Leaderboard & Smart Money Discovery

#### fetch_leader_board
**Function:** Get Hyperbot smart money leaderboard  
**Parameters:**
- `period`: Time period, options: 24h, 7d, 30d
- `sort`: Sort field, options: pnl (profit/loss), winRate (win rate)

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"fetch_leader_board","arguments":{"period":"7d","sort":"pnl"}},"jsonrpc":"2.0","id":1}'
```

#### find_smart_money
**Function:** Discover smart money addresses with multiple sorting and filtering options  
**Parameters:**
- `period`: Period in days, e.g., 7 means last 7 days
- `sort`: Sorting method, options: win-rate, account-balance, ROI, pnl, position-count, profit-count, last-operation, avg-holding-period, current-position
- `pnlList`: Whether to include PnL curve data (true/false)

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"find_smart_money","arguments":{"period":7,"sort":"win-rate","pnlList":true}},"jsonrpc":"2.0","id":2}'
```

---

#### Market Data

#### get_tickers
**Function:** Get latest trading prices for all markets  
**Parameters:** None

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_tickers","arguments":{}},"jsonrpc":"2.0","id":3}'
```

#### get_ticker
**Function:** Get latest trading price for a specific coin  
**Parameters:**
- `address`: Coin code, e.g., btc, eth, sol

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_ticker","arguments":{"address":"ETH"}},"jsonrpc":"2.0","id":4}'
```

#### get_klines
**Function:** Get K-line data (with trading volume), supports BTC, ETH, and other coins  
**Parameters:**
- `coin`: Coin code, e.g., btc, eth
- `interval`: K-line interval, options: 1m, 3m, 5m, 15m, 30m, 1h, 4h, 8h, 1d
- `limit`: Maximum number of records to return

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_klines","arguments":{"coin":"BTC","interval":"15m","limit":100}},"jsonrpc":"2.0","id":5}'
```

#### get_market_stats
**Function:** Get active order statistics (long/short count, value, whale order ratio) and market mid price  
**Parameters:**
- `coin`: Coin code, e.g., btc, eth
- `whaleThreshold`: Whale threshold (in USDT)

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_market_stats","arguments":{"coin":"BTC","whaleThreshold":100000}},"jsonrpc":"2.0","id":6}'
```

#### get_l2_order_book
**Function:** Get market information (L2 order book, etc.)  
**Parameters:**
- `coin`: Coin code, e.g., btc, eth

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_l2_order_book","arguments":{"coin":"BTC"}},"jsonrpc":"2.0","id":7}'
```

---

#### Whale Monitoring

#### get_whale_positions
**Function:** Get whale position information  
**Parameters:**
- `coin`: Coin code, e.g., eth, btc
- `dir`: Direction, options: long, short
- `pnlSide`: PnL filter, options: profit, loss
- `frSide`: Funding fee PnL filter, options: profit, loss
- `topBy`: Sorting method, options: position-value, margin-balance, create-time, profit, loss
- `take`: Maximum number of records to return

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_whale_positions","arguments":{"coin":"BTC","dir":"long","pnlSide":"profit","frSide":"profit","topBy":"position-value","take":10}},"jsonrpc":"2.0","id":8}'
```

#### get_whale_events
**Function:** Real-time monitoring of latest whale open/close positions  
**Parameters:**
- `limit`: Maximum number of records to return

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_whale_events","arguments":{"limit":20}},"jsonrpc":"2.0","id":9}'
```

#### get_whale_directions
**Function:** Get whale position long/short count. Can filter by specific coin  
**Parameters:**
- `coin`: Coin code, e.g., eth, btc (optional)

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_whale_directions","arguments":{"coin":"BTC"}},"jsonrpc":"2.0","id":10}'
```

#### get_whale_history_ratio
**Function:** Get historical whale position long/short ratio  
**Parameters:**
- `interval`: Time interval, options: 1h, 1d or hour, day
- `limit`: Maximum number of records to return

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_whale_history_ratio","arguments":{"interval":"1d","limit":30}},"jsonrpc":"2.0","id":11}'
```

---

#### Trader Analysis

#### fetch_trade_history
**Function:** Query historical trade details for a specific wallet address  
**Parameters:**
- `address`: Wallet address starting with 0x

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"fetch_trade_history","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678"}},"jsonrpc":"2.0","id":12}'
```

#### get_trader_stats
**Function:** Get trader statistics  
**Parameters:**
- `address`: User wallet address
- `period`: Period in days

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_trader_stats","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","period":7}},"jsonrpc":"2.0","id":13}'
```

#### get_max_drawdown
**Function:** Get maximum drawdown  
**Parameters:**
- `address`: User wallet address
- `days`: Statistics days, options: 1, 7, 30, 60, 90
- `scope`: Statistics scope, default: perp

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_max_drawdown","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","days":30,"scope":"perp"}},"jsonrpc":"2.0","id":14}'
```

#### get_best_trades
**Function:** Get the most profitable trades  
**Parameters:**
- `address`: User wallet address
- `period`: Days
- `limit`: Maximum number of records to return

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_best_trades","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","period":7,"limit":10}},"jsonrpc":"2.0","id":15}'
```

#### get_performance_by_coin
**Function:** Break down win rate and PnL performance by coin for an address  
**Parameters:**
- `address`: User wallet address
- `period`: Days
- `limit`: Maximum number of records to return

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_performance_by_coin","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","period":30,"limit":20}},"jsonrpc":"2.0","id":16}'
```

---

#### Position History

#### get_completed_position_history
**Function:** Get completed position history. Deep analysis of complete historical position data for a coin  
**Parameters:**
- `address`: User wallet address
- `coin`: Coin name, e.g., BTC, ETH

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_completed_position_history","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","coin":"BTC"}},"jsonrpc":"2.0","id":17}'
```

#### get_current_position_history
**Function:** Get current position history. Returns historical data for a specific coin's current position  
**Parameters:**
- `address`: User wallet address
- `coin`: Coin name, e.g., BTC, ETH

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_current_position_history","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","coin":"BTC"}},"jsonrpc":"2.0","id":18}'
```

#### get_completed_position_executions
**Function:** Get completed position execution trajectory  
**Parameters:**
- `address`: User wallet address
- `coin`: Coin name, e.g., BTC, ETH
- `interval`: Time interval, e.g., 4h, 1d
- `startTime`: Start timestamp (milliseconds)
- `endTime`: End timestamp (milliseconds)
- `limit`: Maximum number of records to return

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_completed_position_executions","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","coin":"BTC","interval":"4h","limit":50}},"jsonrpc":"2.0","id":19}'
```

#### get_current_position_pnl
**Function:** Get current position PnL  
**Parameters:**
- `address`: User wallet address
- `coin`: Coin name, e.g., BTC, ETH
- `interval`: Time interval, e.g., 4h, 1d
- `limit`: Maximum number of records to return

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_current_position_pnl","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","coin":"BTC","interval":"4h","limit":20}},"jsonrpc":"2.0","id":20}'
```

---

#### Batch Queries

#### get_traders_accounts
**Function:** Batch query account information, supports up to 50 addresses  
**Parameters:**
- `addresses`: List of addresses, max 50 addresses

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_traders_accounts","arguments":{"addresses":["0x1234567890abcdef1234567890abcdef12345678","0xabcdef1234567890abcdef1234567890abcdef12"]}},"jsonrpc":"2.0","id":21}'
```

#### get_traders_statistics
**Function:** Batch query trader statistics, supports up to 50 addresses  
**Parameters:**
- `period`: Period in days, e.g., 7 means last 7 days
- `pnlList`: Whether to include PnL curve data
- `addresses`: List of addresses, max 50 addresses

**MCP Tool Call Example:**
```bash
curl 'https://mcp.hyperbot.network/mcp/message?sessionId=sessionId obtained via sse' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_traders_statistics","arguments":{"period":7,"pnlList":true,"addresses":["0x1234567890abcdef1234567890abcdef12345678","0xabcdef1234567890abcdef1234567890abcdef12"]}},"jsonrpc":"2.0","id":22}'
```

---

## Analysis Prompts

### When to Use Prompts

Use these prompts when you need to provide structured analysis of trading data:

| Scenario | Prompt to Use |
|----------|---------------|
| Analyzing smart money addresses | `smart-money-analysis` |
| Interpreting whale movements | `whale-tracking` |
| Evaluating overall market conditions | `market-sentiment` |
| Assessing trader performance | `trader-evaluation` |

### Prompt Templates

| Prompt Name | Purpose | Template / Example |
|-------------|--------|------------------|
| smart-money-analysis | Smart money address analysis and trading recommendations | ```You are a quantitative trading expert. Analyze the provided smart money address data and provide actionable insights:

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
}``` |
| whale-tracking | Whale behavior analysis and market impact assessment | ```You are a market intelligence analyst specializing in whale behavior. Analyze the provided whale data and assess market impact:

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
}``` |
| market-sentiment | Market sentiment analysis | ```You are a market sentiment analyst. Analyze the provided market data and determine overall market conditions:

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
}``` |
| trader-evaluation | Trader capability evaluation | ```You are a professional trading performance analyst. Conduct a comprehensive evaluation of the trader based on provided data:

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
}``` |

**Usage Notes:**
- Prompts can be dynamically populated with resources content
- Multiple prompts can be combined to form reasoning chains
- JSON output format is recommended for easy Agent parsing

---

## Complete Usage Examples

### Example Output Format

When presenting analysis results, use this structure:

```markdown
## Analysis Summary

### Key Findings
- Finding 1
- Finding 2
- Finding 3

### Detailed Data
[Present relevant tool output]

### Recommendations
- Recommendation 1
- Recommendation 2
```

### Example 1: Discover and Analyze Smart Money Addresses

**Scenario:** User wants to find and analyze top-performing traders

**Execution Steps:**
1. Call Tool: `find_smart_money(period=7, sort="win-rate", pnlList=true)`
2. Get list of high win-rate smart money addresses
3. Use Prompt: `smart-money-analysis` to analyze characteristics
4. Generate analysis report with copy-trading recommendations

**Expected Output:**
```markdown
## Smart Money Analysis Report

### Top Performers (7 Days)
| Address | Win Rate | PnL | Trading Style |
|---------|----------|-----|---------------|
| 0x... | 75% | +$50K | Swing Trader |

### Key Patterns
- High win-rate addresses tend to hold positions 2-5 days
- Most profitable traders focus on BTC and ETH
- Risk management: avg 2-3x leverage

### Copy-Trading Recommendations
- Follow addresses with >60% win rate and consistent PnL
- Position size: 10-20% of their typical position
- Entry timing: Within 1 hour of their open position
```

---

### Example 2: Whale Behavior Monitoring

**Scenario:** User wants to understand whale activity on BTC

**Execution Steps:**
1. Call Tool: `get_whale_events(limit=20)` - latest whale movements
2. Call Tool: `get_whale_directions(coin="BTC")` - BTC long/short ratio
3. Call Tool: `get_whale_positions(coin="BTC", topBy="position-value", take=10)`
4. Use Prompt: `whale-tracking` for analysis

---

### Example 3: In-depth Trader Analysis

**Scenario:** User wants to evaluate a specific trader

**Execution Steps:**
1. Call Tool: `get_trader_stats(address, period=30)` - basic stats
2. Call Tool: `get_performance_by_coin(address, period=30, limit=20)` - coin breakdown
3. Call Tool: `get_completed_position_history(address, coin="BTC")` - position history
4. Use Prompt: `trader-evaluation` for comprehensive report

---

### Example 4: Market Sentiment Analysis

**Scenario:** User wants overall market sentiment

**Execution Steps:**
1. Call Tool: `get_l2_order_book("BTC")` - order book depth
2. Call Tool: `get_market_stats("BTC", whaleThreshold=100000)` - active orders
3. Call Tool: `get_whale_history_ratio(interval="1d", limit=30)` - historical ratio
4. Use Prompt: `market-sentiment` for sentiment report

---

## Important Notes

### MCP Call Instructions

**Request Format (JSON-RPC 2.0):**
```json
{
  "method": "tools/call",
  "params": {
    "name": "<tool_name>",
    "arguments": { /* tool parameters */ }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

**Key Points:**
- **sessionId**: Obtain via SSE connection to `https://mcp.hyperbot.network/mcp/sse`
- **method**: Always `tools/call` for tool invocation
- **params.name**: The tool name (e.g., `fetch_leader_board`, `get_ticker`)
- **params.arguments**: Tool-specific parameters as key-value pairs

### Rate Limiting
- Single IP request frequency limit: 100 requests/minute
- Batch interfaces support maximum 50 addresses

### Data Update Frequency
| Data Type | Update Frequency |
|-----------|------------------|
| Market data | Real-time |
| Smart money leaderboard | Hourly |
| Whale positions | Real-time |
| Trader statistics | Every 5 minutes |

### Error Handling Guide

| Error | Cause | Solution |
|-------|-------|----------|
| 400 Bad Request | Invalid parameters | Check parameter types and ranges |
| 400 (current position) | No active position | Skip this tool, use completed position history instead |
| 429 Too Many Requests | Rate limit exceeded | Wait and retry |
| Connection failed | Network issue | Check SSE connection |
