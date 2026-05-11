---
name: yahoo-finance
description: Get stock prices, quotes, fundamentals, earnings, options, dividends, and analyst ratings using Yahoo Finance. Uses yfinance library - no API key required.
---

# Yahoo Finance CLI

A Python CLI for fetching comprehensive stock data from Yahoo Finance using yfinance.

## Requirements

- Python 3.11+
- uv (for inline script dependencies)

## Installing uv

The script requires `uv` - an extremely fast Python package manager. Check if it's installed:

```bash
uv --version
```

If not installed, install it using one of these methods:

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### macOS (Homebrew)
```bash
brew install uv
```

### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### pip (any platform)
```bash
pip install uv
```

After installation, restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc on macOS
```

## Installation

The `yf` script uses PEP 723 inline script metadata - dependencies are auto-installed on first run.

```bash
# Make executable
chmod +x /path/to/skills/yahoo-finance/yf

# Optionally symlink to PATH for global access
ln -sf /path/to/skills/yahoo-finance/yf /usr/local/bin/yf
```

First run will install dependencies (yfinance, rich) to uv's cache. Subsequent runs are instant.

## Commands

### Price (quick check)
```bash
yf AAPL              # shorthand for price
yf price AAPL
```

### Quote (detailed)
```bash
yf quote MSFT
```

### Fundamentals
```bash
yf fundamentals NVDA
```
Shows: PE ratios, EPS, market cap, margins, ROE/ROA, analyst targets.

### Earnings
```bash
yf earnings TSLA
```
Shows: Next earnings date, EPS estimates, earnings history with surprises.

### Company Profile
```bash
yf profile GOOGL
```
Shows: Sector, industry, employees, website, address, business description.

### Dividends
```bash
yf dividends KO
```
Shows: Dividend rate/yield, ex-date, payout ratio, recent dividend history.

### Analyst Ratings
```bash
yf ratings AAPL
```
Shows: Buy/hold/sell distribution, mean rating, recent upgrades/downgrades.

### Options Chain
```bash
yf options SPY
```
Shows: Near-the-money calls and puts with strike, bid/ask, volume, OI, IV.

### History
```bash
yf history GOOGL 1mo     # 1 month history
yf history TSLA 1y       # 1 year
yf history BTC-USD 5d    # 5 days
```
Ranges: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

### Compare
```bash
yf compare AAPL,MSFT,GOOGL
yf compare RELIANCE.NS,TCS.NS,INFY.NS
```
Side-by-side comparison with price, change, 52W range, market cap.

### Search
```bash
yf search "reliance industries"
yf search "bitcoin"
yf search "s&p 500 etf"
```

## Symbol Format

- **US stocks:** AAPL, MSFT, GOOGL, TSLA
- **Indian NSE:** RELIANCE.NS, TCS.NS, INFY.NS
- **Indian BSE:** RELIANCE.BO, TCS.BO
- **Crypto:** BTC-USD, ETH-USD
- **Forex:** EURUSD=X, GBPUSD=X
- **ETFs:** SPY, QQQ, VOO

## Examples

```bash
# Quick price check
yf AAPL

# Get valuation metrics
yf fundamentals NVDA

# Next earnings date + history
yf earnings TSLA

# Options chain for SPY
yf options SPY

# Compare tech giants
yf compare AAPL,MSFT,GOOGL,META,AMZN

# Find Indian stocks
yf search "infosys"

# Dividend info for Coca-Cola
yf dividends KO

# Analyst ratings for Apple
yf ratings AAPL
```

## Troubleshooting

### "command not found: uv"
Install uv using the instructions above.

### Rate limiting / connection errors
Yahoo Finance may rate limit excessive requests. Wait a few minutes and try again.

### "No data" for a symbol
- Verify the symbol exists: `yf search "company name"`
- Some data (options, dividends) isn't available for all securities

## Technical Notes

- Uses PEP 723 inline script metadata for uv dependencies
- Rich library provides colored, formatted tables
- First run installs deps to uv cache (~5 seconds)
- Subsequent runs are instant (cached environment)
- Handles NaN/None values gracefully with fallbacks
