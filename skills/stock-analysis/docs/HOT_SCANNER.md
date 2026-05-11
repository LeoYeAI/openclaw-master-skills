# 🔥 Hot Scanner

Find viral stocks & crypto trends in real-time by aggregating multiple data sources.

## Overview

The Hot Scanner answers one question: **"What's hot right now?"**

It aggregates data from:
- CoinGecko (trending coins, biggest movers)
- Google News (finance & crypto headlines)
- Yahoo Finance (gainers, losers, most active)
- Twitter/X (social sentiment, optional)

## Quick Start

```bash
# Full scan with all sources
python3 scripts/hot_scanner.py

# Skip social media (faster)
python3 scripts/hot_scanner.py --no-social

# JSON output for automation
python3 scripts/hot_scanner.py --json
```

## Output Format

### Console Output

```
============================================================
🔥 HOT SCANNER v2 - What's Trending Right Now?
📅 2026-02-02 10:45:30 UTC
============================================================

📊 TOP TRENDING (by buzz):
   1. BTC      (6 pts) [CoinGecko, Google News] 📉 bearish (-2.5%)
   2. ETH      (5 pts) [CoinGecko, Twitter] 📉 bearish (-7.2%)
   3. NVDA     (3 pts) [Google News, Yahoo] 📰 Earnings beat...

🪙 CRYPTO HIGHLIGHTS:
   🚀 RIVER    River              +14.0%
   📉 BTC      Bitcoin             -2.5%
   📉 ETH      Ethereum            -7.2%

📈 STOCK MOVERS:
   🟢 NVDA (gainers)
   🔴 TSLA (losers)
   📊 AAPL (most active)

🐦 SOCIAL BUZZ:
   [twitter] Bitcoin to $100k prediction...
   [reddit_wsb] GME yolo update...

📰 BREAKING NEWS:
   [BTC, ETH] Crypto crash: $2.5B liquidated...
   [NVDA] Nvidia beats earnings expectations...
```

### JSON Output

```json
{
  "scan_time": "2026-02-02T10:45:30+00:00",
  "top_trending": [
    {
      "symbol": "BTC",
      "mentions": 6,
      "sources": ["CoinGecko Trending", "Google News"],
      "signals": ["📉 bearish (-2.5%)"]
    }
  ],
  "crypto_highlights": [...],
  "stock_highlights": [...],
  "social_buzz": [...],
  "breaking_news": [...]
}
```

## Data Sources

### CoinGecko (No Auth Required)

| Endpoint | Data |
|----------|------|
| `/search/trending` | Top 15 trending coins |
| `/coins/markets` | Top 100 by market cap with 24h changes |

**Scoring:** Trending coins get 2 points, movers with >3% change get 1 point.

### Google News RSS (No Auth Required)

| Feed | Content |
|------|---------|
| Business News | General finance headlines |
| Crypto Search | Bitcoin, Ethereum, crypto keywords |

**Ticker Extraction:** Uses regex patterns and company name mappings.

### Yahoo Finance (No Auth Required)

| Page | Data |
|------|------|
| `/gainers` | Top gaining stocks |
| `/losers` | Top losing stocks |
| `/most-active` | Highest volume stocks |

**Note:** Requires gzip decompression.

### Twitter/X (Auth Required)

Uses [bird CLI](https://github.com/steipete/bird) for Twitter search.

**Searches:**
- `stock OR $SPY OR $QQQ OR earnings`
- `bitcoin OR ethereum OR crypto OR $BTC`

## Twitter/X Setup

### 1. Install bird CLI

```bash
# macOS
brew install steipete/tap/bird

# npm
npm install -g @steipete/bird
```

### 2. Get Auth Tokens

**Option A: Browser cookies (macOS)**
1. Login to x.com in Safari/Chrome
2. Grant Terminal "Full Disk Access" in System Settings
3. Run `bird whoami` to verify

**Option B: Manual extraction**
1. Open x.com in Chrome
2. DevTools (F12) → Application → Cookies → x.com
3. Copy `auth_token` and `ct0` values

### 3. Configure

Create `.env` file in the skill directory:

```bash
# /path/to/stock-analysis/.env
AUTH_TOKEN=your_auth_token_here
CT0=your_ct0_token_here
```

Or export as environment variables:

```bash
export AUTH_TOKEN="..."
export CT0="..."
```

### 4. Verify

```bash
bird whoami
# Should show: 🙋 @YourUsername
```

## Scoring System

Each mention from a source adds points:

| Source | Points |
|--------|--------|
| CoinGecko Trending | 2 |
| CoinGecko Movers | 1 |
| Google News | 1 |
| Yahoo Finance | 1 |
| Twitter/X | 1 |
| Reddit (high score) | 2 |
| Reddit (normal) | 1 |

Symbols are ranked by total points across all sources.

## Ticker Extraction

### Patterns

```python
# Cashtag: $AAPL
r'\$([A-Z]{1,5})\b'

# Parentheses: (AAPL)
r'\(([A-Z]{2,5})\)'

# Stock mentions: AAPL stock, AAPL shares
r'\b([A-Z]{2,5})(?:\'s|:|\s+stock|\s+shares)'
```

### Company Mappings

```python
{
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Nvidia": "NVDA",
    "Bitcoin": "BTC",
    "Ethereum": "ETH",
    # ... etc
}
```

### Crypto Keywords

```python
{
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "dogecoin": "DOGE",
    # ... etc
}
```

## Automation

### Cron Job

```bash
# Daily at 8 AM
0 8 * * * cd /path/to/stock-analysis && python3 scripts/hot_scanner.py --json > cache/daily_scan.json
```

### OpenClaw Integration

```yaml
# Cron job config
name: "🔥 Daily Hot Scanner"
schedule:
  kind: cron
  expr: "0 8 * * *"
  tz: "Europe/Berlin"
payload:
  kind: agentTurn
  message: "Run hot scanner and summarize results"
  deliver: true
sessionTarget: isolated
```

## Caching

Results are saved to:
- `cache/hot_scan_latest.json` — Most recent scan

## Limitations

- **Reddit:** Blocked without OAuth (403). Requires API application.
- **Twitter:** Requires auth tokens, may expire.
- **Yahoo:** Sometimes rate-limited.
- **Google News:** RSS URLs may change.

## Future Enhancements

- [ ] Reddit API integration (PRAW)
- [ ] StockTwits integration
- [ ] Google Trends
- [ ] Historical trend tracking
- [ ] Alert thresholds (notify when score > X)

## Troubleshooting

### Twitter not working

```bash
# Check auth
bird whoami

# Should see your username
# If not, re-export tokens
```

### Yahoo 403 or gzip errors

The scanner handles gzip automatically. If issues persist, Yahoo may be rate-limiting.

### No tickers found

Check that news headlines contain recognizable patterns. The scanner uses conservative extraction to avoid false positives.
