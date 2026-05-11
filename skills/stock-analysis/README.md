# 📈 Stock Analysis v6.1

> AI-powered stock & crypto analysis with portfolio management, watchlists, dividend analysis, and **viral trend detection**.

[![ClawHub Downloads](https://img.shields.io/badge/ClawHub-1500%2B%20downloads-blue)](https://clawhub.ai)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green)](https://openclaw.ai)

## What's New in v6.1

- 🔥 **Hot Scanner** — Find viral stocks & crypto across multiple sources
- 🐦 **Twitter/X Integration** — Social sentiment via bird CLI
- 📰 **Multi-Source Aggregation** — CoinGecko, Google News, Yahoo Finance
- ⏰ **Cron Support** — Daily trend reports

## What's New in v6.0

- 🆕 **Watchlist + Alerts** — Price targets, stop losses, signal change notifications
- 🆕 **Dividend Analysis** — Yield, payout ratio, growth rate, safety score
- 🆕 **Fast Mode** — Skip slow analyses for quick checks
- 🆕 **Improved Commands** — Better OpenClaw/Telegram integration
- 🆕 **Test Suite** — Unit tests for core functionality

## Features

| Feature | Description |
|---------|-------------|
| **8-Dimension Analysis** | Earnings, fundamentals, analysts, momentum, sentiment, sector, market, history |
| **Crypto Support** | Top 20 cryptos with market cap, BTC correlation, momentum |
| **Portfolio Management** | Track holdings, P&L, concentration warnings |
| **Watchlist + Alerts** | Price targets, stop losses, signal changes |
| **Dividend Analysis** | Yield, payout, growth, safety score |
| **Risk Detection** | Geopolitical, earnings timing, overbought, risk-off |
| **Breaking News** | Crisis keyword scanning (last 24h) |

## Quick Start

### Analyze Stocks
```bash
uv run scripts/analyze_stock.py AAPL
uv run scripts/analyze_stock.py AAPL MSFT GOOGL
uv run scripts/analyze_stock.py AAPL --fast  # Skip slow analyses
```

### Analyze Crypto
```bash
uv run scripts/analyze_stock.py BTC-USD
uv run scripts/analyze_stock.py ETH-USD SOL-USD
```

### Dividend Analysis
```bash
uv run scripts/dividends.py JNJ PG KO
```

### Watchlist
```bash
uv run scripts/watchlist.py add AAPL --target 200 --stop 150
uv run scripts/watchlist.py list
uv run scripts/watchlist.py check --notify
```

### Portfolio
```bash
uv run scripts/portfolio.py create "My Portfolio"
uv run scripts/portfolio.py add AAPL --quantity 100 --cost 150
uv run scripts/portfolio.py show
```

### 🔥 Hot Scanner (NEW)
```bash
# Full scan with all sources
python3 scripts/hot_scanner.py

# Fast scan (skip social media)
python3 scripts/hot_scanner.py --no-social

# JSON output for automation
python3 scripts/hot_scanner.py --json
```

## Analysis Dimensions

### Stocks (8 dimensions)
1. **Earnings Surprise** (30%) — EPS beat/miss
2. **Fundamentals** (20%) — P/E, margins, growth, debt
3. **Analyst Sentiment** (20%) — Ratings, price targets
4. **Historical Patterns** (10%) — Past earnings reactions
5. **Market Context** (10%) — VIX, SPY/QQQ trends
6. **Sector Performance** (15%) — Relative strength
7. **Momentum** (15%) — RSI, 52-week range
8. **Sentiment** (10%) — Fear/Greed, shorts, insiders

### Crypto (3 dimensions)
- Market Cap & Category
- BTC Correlation (30-day)
- Momentum (RSI, range)

## Dividend Metrics

| Metric | Description |
|--------|-------------|
| Yield | Annual dividend / price |
| Payout Ratio | Dividend / EPS |
| 5Y Growth | CAGR of dividend |
| Consecutive Years | Years of increases |
| Safety Score | 0-100 composite |
| Income Rating | Excellent → Poor |

## 🔥 Hot Scanner

Find what's trending RIGHT NOW across stocks & crypto.

### Data Sources

| Source | What it finds |
|--------|---------------|
| **CoinGecko Trending** | Top 15 trending coins |
| **CoinGecko Movers** | Biggest gainers/losers (>3%) |
| **Google News** | Breaking finance & crypto news |
| **Yahoo Finance** | Top gainers, losers, most active |
| **Twitter/X** | Social sentiment (requires auth) |

### Output

```
📊 TOP TRENDING (by buzz):
   1. BTC      (6 pts) [CoinGecko, Google News] 📉 bearish (-2.5%)
   2. ETH      (5 pts) [CoinGecko, Twitter] 📉 bearish (-7.2%)
   3. NVDA     (3 pts) [Google News, Yahoo] 📰 Earnings beat...

🪙 CRYPTO HIGHLIGHTS:
   🚀 RIVER    River              +14.0%
   📉 BTC      Bitcoin             -2.5%

📈 STOCK MOVERS:
   🟢 NVDA (gainers)
   🔴 TSLA (losers)

📰 BREAKING NEWS:
   [BTC, ETH] Crypto crash: $2.5B liquidated...
```

### Twitter/X Setup (Optional)

1. Install bird CLI: `npm install -g @steipete/bird`
2. Login to x.com in Safari/Chrome
3. Create `.env` file:
```
AUTH_TOKEN=your_auth_token
CT0=your_ct0_token
```

Get tokens from browser DevTools → Application → Cookies → x.com

### Automation

Set up a daily cron job for morning reports:
```bash
# Run at 8 AM daily
0 8 * * * python3 /path/to/hot_scanner.py --no-social >> /var/log/hot_scanner.log
```

## Risk Detection

- ⚠️ Pre-earnings warning (< 14 days)
- ⚠️ Post-earnings spike (> 15% in 5 days)
- ⚠️ Overbought (RSI > 70 + near 52w high)
- ⚠️ Risk-off mode (GLD/TLT/UUP rising)
- ⚠️ Geopolitical keywords (Taiwan, China, etc.)
- ⚠️ Breaking news alerts

## Performance Options

| Flag | Speed | Description |
|------|-------|-------------|
| (default) | 5-10s | Full analysis |
| `--no-insider` | 3-5s | Skip SEC EDGAR |
| `--fast` | 2-3s | Skip insider + news |

## Data Sources

- [Yahoo Finance](https://finance.yahoo.com) — Prices, fundamentals, movers
- [CoinGecko](https://coingecko.com) — Crypto trending, market data
- [CNN Fear & Greed](https://money.cnn.com/data/fear-and-greed/) — Sentiment
- [SEC EDGAR](https://www.sec.gov/edgar) — Insider trading
- [Google News RSS](https://news.google.com) — Breaking news
- [Twitter/X](https://x.com) — Social sentiment (via bird CLI)

## Storage

| Data | Location |
|------|----------|
| Portfolios | `~/.clawdbot/skills/stock-analysis/portfolios.json` |
| Watchlist | `~/.clawdbot/skills/stock-analysis/watchlist.json` |

## Testing

```bash
uv run pytest scripts/test_stock_analysis.py -v
```

## Limitations

- Yahoo Finance may lag 15-20 minutes
- Short interest lags ~2 weeks (FINRA)
- US markets only

## Disclaimer

⚠️ **NOT FINANCIAL ADVICE.** For informational purposes only. Consult a licensed financial advisor before making investment decisions.

---

Built for [OpenClaw](https://openclaw.ai) 🦞 | [ClawHub](https://clawhub.ai)
