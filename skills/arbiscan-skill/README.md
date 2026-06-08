# ArbiScan — Cross-Exchange Crypto Scanner & Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**12 scan types across Binance, OKX, Bybit, and Bitget. Arbitrage, monitoring, and signals — all from public APIs, no keys needed.**

ArbiScan is an [OpenClaw Skill](https://clawhub.ai) and standalone CLI that scans major crypto exchanges for arbitrage opportunities, market anomalies, and trading signals. It covers 100 trading pairs across 4 exchanges. You decide whether to act — ArbiScan only watches.

## Scan Types

### Arbitrage (find price/rate discrepancies)

| Type | What it does | Data Source |
|------|-------------|-------------|
| **Funding Rate Arb** | Compares perpetual funding rates across exchanges | Funding rate endpoints |
| **Basis Arb** | Spots premium/discount between spot and futures | Spot + futures tickers |
| **Spot Spread** | Finds bid/ask gaps across exchanges | Order book top-of-book |
| **Futures Spread** | Finds perpetual contract price gaps across exchanges | Futures tickers |

### Monitoring (track market conditions)

| Type | What it does | Data Source |
|------|-------------|-------------|
| **Stablecoin Depeg** | Monitors USDC/DAI/FDUSD/TUSD deviation from $1 | Stablecoin tickers |
| **Open Interest** | Tracks OI distribution, flags concentration on one exchange | OI endpoints |
| **Funding Extreme** | Alerts when funding rate exceeds ±0.1% (10x normal) | Funding rate endpoints |
| **Price Movers** | 24h top gainers and losers | 24hr tickers |
| **Volume Anomaly** | Detects unusual volume concentration or spikes | 24hr volume data |

### Signals (identify trading signals)

| Type | What it does | Data Source |
|------|-------------|-------------|
| **Funding Trend** | Finds symbols with ≥5 consecutive same-direction funding rates | Historical funding rates |
| **Long/Short Ratio** | Flags extreme positioning (>65% one-sided) | Binance + Bybit ratio endpoints |
| **New Listing** | Tokens on some exchanges but not others — premium potential | Exchange pair lists |

## Quick Start

### As an OpenClaw Skill

Install from ClawHub and let your AI agent scan:

```
"Scan for funding rate arbitrage opportunities with APY > 10%"
"Which coins have extreme funding rates right now?"
"Show me the biggest price movers in the last 24 hours"
"Are any stablecoins depegging?"
"Find tokens listed on Binance but not on OKX"
```

### Standalone (Python)

```bash
cd scripts/
pip install -r requirements.txt

# Run everything
python scanner.py --all

# Run by category
python scanner.py --type arbitrage      # all 4 arbitrage scans
python scanner.py --type monitor        # all 5 monitoring scans
python scanner.py --type signals        # all 3 signal scans

# Individual scans
python scanner.py --type funding --min-apy 10
python scanner.py --type price_movers
python scanner.py --type long_short
python scanner.py --type new_listing

# Output formats
python scanner.py --type funding --format markdown
python scanner.py --type price_movers --format json
```

## Sample Output

```
  Funding Rate Arbitrage
================================================================================
Symbol     Long (低费率)         Short (高费率)        Rate Diff   Est. APY%   Risk    Window
---------  -------------------  --------------------  ----------  ----------  ------  --------
FILUSDT    Binance -0.0799%     Bitget -0.0104%       0.0695%     76.1%       HIGH    ~8h
SEIUSDT    Binance -0.0317%     OKX -0.0026%          0.0291%     31.9%       MEDIUM  ~8h
BTCUSDT    Binance -0.0027%     OKX 0.0064%           0.0091%     10.0%       LOW     ~8h
```

```
  24h Price Movers (Gainers & Losers)
================================================================================
Symbol     Exchange    Price        24h Change%    24h Volume (USDT)    Direction
---------  ----------  -----------  -------------  -------------------  ---------
ARBUSDT    Binance     $0.1017      -2.59%         $41,804,011          DUMP
SOLUSDT    OKX         $87.9300     -1.15%         $11,760,759          DUMP
SEIUSDT    Bybit       $0.0664      +0.54%         $15,798,499          PUMP
```

## Composable with Exchange Skills

ArbiScan is designed to work alongside exchange trading skills:

1. **ArbiScan** scans and identifies opportunities (this skill)
2. **Binance/Bybit/Bitget Skills** can execute trades if you decide to act
3. **TradeOS** can manage the full workflow

```
"Use ArbiScan to find opportunities, then use Binance skill to execute the best one"
```

## How It Works

- Fetches data from **public API endpoints only** — no API keys, no authentication
- Built-in rate limiting (200ms between requests) to respect exchange limits
- Covers **Top 30 trading pairs** by default (expandable on request) by market cap
- **12 scan types** across 3 categories (arbitrage, monitoring, signals)
- Risk scoring based on APY magnitude and coin category

## Covered Exchanges

| Exchange | Spot | Futures | Funding Rate | Open Interest | Long/Short Ratio |
|----------|------|---------|--------------|---------------|-----------------|
| Binance  | ✅   | ✅      | ✅           | ✅            | ✅              |
| Bybit    | ✅   | ✅      | ✅           | ✅            | ✅              |
| OKX      | ✅   | ✅      | ✅           | ✅            | —               |
| Bitget   | ✅   | ✅      | ✅           | ✅            | —               |

## Disclaimer

ArbiScan is for **informational purposes only**. It does not constitute financial advice. Opportunities shown are theoretical — actual execution requires considering:

- Gas/withdrawal fees
- Transfer times between exchanges
- Slippage and liquidity
- Exchange counterparty risk
- Regulatory compliance

Always do your own research before trading.

## License

MIT
