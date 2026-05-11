# Usage Guide

Practical examples for using Stock Analysis v6.0 in real scenarios.

## Table of Contents

1. [Basic Stock Analysis](#basic-stock-analysis)
2. [Comparing Stocks](#comparing-stocks)
3. [Crypto Analysis](#crypto-analysis)
4. [Dividend Investing](#dividend-investing)
5. [Portfolio Management](#portfolio-management)
6. [Watchlist & Alerts](#watchlist--alerts)
7. [Performance Tips](#performance-tips)
8. [Interpreting Results](#interpreting-results)

---

## Basic Stock Analysis

### Single Stock

```bash
uv run scripts/analyze_stock.py AAPL
```

**Output:**
```
===========================================================================
STOCK ANALYSIS: AAPL (Apple Inc.)
Generated: 2024-02-01T10:30:00
===========================================================================

RECOMMENDATION: BUY (Confidence: 72%)

SUPPORTING POINTS:
• Beat by 8.2% - EPS $2.18 vs $2.01 expected
• Strong margin: 24.1%
• Analyst consensus: Buy with 12.3% upside (42 analysts)
• Momentum: RSI 58 (neutral)
• Sector: Technology uptrend (+5.2% 1m)

CAVEATS:
• Earnings in 12 days - high volatility expected
• High market volatility (VIX 24)

===========================================================================
DISCLAIMER: NOT FINANCIAL ADVICE.
===========================================================================
```

### JSON Output

For programmatic use:

```bash
uv run scripts/analyze_stock.py AAPL --output json | jq '.recommendation, .confidence'
```

### Verbose Mode

See what's happening under the hood:

```bash
uv run scripts/analyze_stock.py AAPL --verbose
```

---

## Comparing Stocks

### Side-by-Side Analysis

```bash
uv run scripts/analyze_stock.py AAPL MSFT GOOGL
```

Each stock gets a full analysis. Compare recommendations and confidence levels.

### Sector Comparison

Compare stocks in the same sector:

```bash
# Banks
uv run scripts/analyze_stock.py JPM BAC WFC GS

# Tech
uv run scripts/analyze_stock.py AAPL MSFT GOOGL AMZN META
```

---

## Crypto Analysis

### Basic Crypto

```bash
uv run scripts/analyze_stock.py BTC-USD
```

**Crypto-Specific Output:**
- Market cap classification (large/mid/small)
- Category (Smart Contract L1, DeFi, etc.)
- BTC correlation (30-day)
- Momentum (RSI, price range)

### Compare Cryptos

```bash
uv run scripts/analyze_stock.py BTC-USD ETH-USD SOL-USD
```

### Supported Cryptos

```
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, DOT, MATIC,
LINK, ATOM, UNI, LTC, BCH, XLM, ALGO, VET, FIL, NEAR
```

Use `-USD` suffix: `BTC-USD`, `ETH-USD`, etc.

---

## Dividend Investing

### Analyze Dividend Stock

```bash
uv run scripts/dividends.py JNJ
```

**Output:**
```
============================================================
DIVIDEND ANALYSIS: JNJ (Johnson & Johnson)
============================================================

Current Price:    $160.50
Annual Dividend:  $4.76
Dividend Yield:   2.97%
Payment Freq:     quarterly
Ex-Dividend:      2024-02-15

Payout Ratio:     65.0% (moderate)
5Y Div Growth:    +5.8%
Consecutive Yrs:  62

SAFETY SCORE:     78/100
INCOME RATING:    GOOD

Safety Factors:
  • Moderate payout ratio (65%)
  • Good dividend growth (+5.8% CAGR)
  • Dividend Aristocrat (62+ years)

Dividend History:
  2023: $4.52
  2022: $4.36
  2021: $4.24
  2020: $4.04
  2019: $3.80
============================================================
```

### Compare Dividend Stocks

```bash
uv run scripts/dividends.py JNJ PG KO MCD VZ T
```

### Dividend Aristocrats Screen

Look for stocks with:
- Yield > 2%
- Payout < 60%
- Growth > 5%
- Consecutive years > 25

---

## Portfolio Management

### Create Portfolio

```bash
uv run scripts/portfolio.py create "Retirement"
```

### Add Holdings

```bash
# Stocks
uv run scripts/portfolio.py add AAPL --quantity 100 --cost 150.00

# Crypto
uv run scripts/portfolio.py add BTC-USD --quantity 0.5 --cost 40000
```

### View Portfolio

```bash
uv run scripts/portfolio.py show
```

**Output:**
```
Portfolio: Retirement
====================

Assets:
  AAPL     100 shares @ $150.00 = $15,000.00
           Current: $185.00 = $18,500.00 (+23.3%)
  
  BTC-USD  0.5 @ $40,000 = $20,000.00
           Current: $45,000 = $22,500.00 (+12.5%)

Total Cost:    $35,000.00
Current Value: $41,000.00
Total P&L:     +$6,000.00 (+17.1%)
```

### Analyze Portfolio

```bash
# Full analysis of all holdings
uv run scripts/analyze_stock.py --portfolio "Retirement"

# With period returns
uv run scripts/analyze_stock.py --portfolio "Retirement" --period monthly
```

### Rebalance Check

The analysis flags concentration warnings:
```
⚠️ CONCENTRATION WARNINGS:
   • AAPL: 45.1% (>30% of portfolio)
```

---

## Watchlist & Alerts

### Add to Watchlist

```bash
# Basic watch
uv run scripts/watchlist.py add NVDA

# With price target
uv run scripts/watchlist.py add NVDA --target 800

# With stop loss
uv run scripts/watchlist.py add NVDA --stop 600

# Alert on signal change
uv run scripts/watchlist.py add NVDA --alert-on signal

# All options
uv run scripts/watchlist.py add NVDA --target 800 --stop 600 --alert-on signal
```

### View Watchlist

```bash
uv run scripts/watchlist.py list
```

**Output:**
```json
{
  "success": true,
  "items": [
    {
      "ticker": "NVDA",
      "current_price": 725.50,
      "price_at_add": 700.00,
      "change_pct": 3.64,
      "target_price": 800.00,
      "to_target_pct": 10.27,
      "stop_price": 600.00,
      "to_stop_pct": -17.30,
      "alert_on_signal": true,
      "last_signal": "BUY",
      "added_at": "2024-01-15"
    }
  ],
  "count": 1
}
```

### Check Alerts

```bash
# Check for triggered alerts
uv run scripts/watchlist.py check

# Format for notification (Telegram)
uv run scripts/watchlist.py check --notify
```

**Alert Example:**
```
📢 Stock Alerts

🎯 NVDA hit target! $802.50 >= $800.00
🛑 TSLA hit stop! $195.00 <= $200.00
📊 AAPL signal changed: HOLD → BUY
```

### Remove from Watchlist

```bash
uv run scripts/watchlist.py remove NVDA
```

---

## Performance Tips

### Fast Mode

Skip slow analyses for quick checks:

```bash
# Skip insider trading + breaking news
uv run scripts/analyze_stock.py AAPL --fast
```

**Speed comparison:**
| Mode | Time | What's Skipped |
|------|------|----------------|
| Default | 5-10s | Nothing |
| `--no-insider` | 3-5s | SEC EDGAR |
| `--fast` | 2-3s | Insider + News |

### Batch Analysis

Analyze multiple stocks in one command:

```bash
uv run scripts/analyze_stock.py AAPL MSFT GOOGL AMZN META
```

### Caching

Market context is cached for 1 hour:
- VIX, SPY, QQQ trends
- Fear & Greed Index
- VIX term structure
- Breaking news

Second analysis of different stock reuses cached data.

---

## Interpreting Results

### Recommendation Thresholds

| Score | Recommendation |
|-------|----------------|
| > +0.33 | BUY |
| -0.33 to +0.33 | HOLD |
| < -0.33 | SELL |

### Confidence Levels

| Confidence | Meaning |
|------------|---------|
| > 80% | Strong conviction |
| 60-80% | Moderate conviction |
| 40-60% | Mixed signals |
| < 40% | Low conviction |

### Reading Caveats

**Always read the caveats!** They often contain critical information:

```
CAVEATS:
• Earnings in 5 days - high volatility expected    ← Timing risk
• RSI 78 (overbought) + near 52w high              ← Technical risk
• ⚠️ BREAKING NEWS: Fed emergency rate discussion  ← External risk
• ⚠️ SECTOR RISK: China tensions affect tech       ← Geopolitical
```

### When to Ignore the Signal

- **Pre-earnings:** Even BUY → wait until after
- **Overbought:** Consider smaller position
- **Risk-off:** Reduce overall exposure
- **Low confidence:** Do more research

### When to Trust the Signal

- **High confidence + no major caveats**
- **Multiple supporting points align**
- **Sector is strong**
- **Market regime is favorable**

---

## Common Workflows

### Morning Check

```bash
# Check watchlist alerts
uv run scripts/watchlist.py check --notify

# Quick portfolio update
uv run scripts/analyze_stock.py --portfolio "Main" --fast
```

### Research New Stock

```bash
# Full analysis
uv run scripts/analyze_stock.py XYZ

# If dividend stock
uv run scripts/dividends.py XYZ

# Add to watchlist for monitoring
uv run scripts/watchlist.py add XYZ --alert-on signal
```

### Weekly Review

```bash
# Full portfolio analysis
uv run scripts/analyze_stock.py --portfolio "Main" --period weekly

# Check dividend holdings
uv run scripts/dividends.py JNJ PG KO
```

---

## Troubleshooting

### "Invalid ticker"

- Check spelling
- For crypto, use `-USD` suffix
- Non-US stocks may not work

### "Insufficient data"

- Stock might be too new
- ETFs have limited data
- OTC stocks often fail

### Slow Performance

- Use `--fast` for quick checks
- Insider trading is slowest
- Breaking news adds ~2s

### Missing Data

- Not all stocks have analyst coverage
- Some metrics require options chains
- Crypto has no sentiment data
