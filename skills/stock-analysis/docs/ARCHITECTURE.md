# Technical Architecture

How Stock Analysis v6.0 works under the hood.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Stock Analysis v6.0                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    CLI Interface                              │   │
│  │  analyze_stock.py | dividends.py | watchlist.py | portfolio.py│   │
│  └────────────────────────────┬─────────────────────────────────┘   │
│                               │                                      │
│  ┌────────────────────────────▼─────────────────────────────────┐   │
│  │                   Analysis Engine                             │   │
│  │                                                               │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │   │
│  │  │Earnings │ │Fundmtls │ │Analysts │ │Historical│            │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘            │   │
│  │       │           │           │           │                   │   │
│  │  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐            │   │
│  │  │ Market  │ │ Sector  │ │Momentum │ │Sentiment│            │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘            │   │
│  │       │           │           │           │                   │   │
│  │       └───────────┴───────────┴───────────┘                   │   │
│  │                          │                                    │   │
│  │                    [Synthesizer]                              │   │
│  │                          │                                    │   │
│  │                    [Signal Output]                            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                               │                                      │
│  ┌────────────────────────────▼─────────────────────────────────┐   │
│  │                    Data Sources                               │   │
│  │                                                               │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │   │
│  │  │ Yahoo   │ │  CNN    │ │   SEC   │ │ Google  │            │   │
│  │  │ Finance │ │Fear/Grd │ │ EDGAR   │ │  News   │            │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Data Fetching (`fetch_stock_data`)

```python
def fetch_stock_data(ticker: str, verbose: bool = False) -> StockData | None:
    """Fetch stock data from Yahoo Finance with retry logic."""
```

**Features:**
- 3 retries with exponential backoff
- Graceful handling of missing data
- Asset type detection (stock vs crypto)

**Returns:** `StockData` dataclass with:
- `info`: Company fundamentals
- `earnings_history`: Past earnings
- `analyst_info`: Ratings and targets
- `price_history`: 1-year OHLCV

### 2. Analysis Modules

Each dimension has its own analyzer:

| Module | Function | Returns |
|--------|----------|---------|
| Earnings | `analyze_earnings_surprise()` | `EarningsSurprise` |
| Fundamentals | `analyze_fundamentals()` | `Fundamentals` |
| Analysts | `analyze_analyst_sentiment()` | `AnalystSentiment` |
| Historical | `analyze_historical_patterns()` | `HistoricalPatterns` |
| Market | `analyze_market_context()` | `MarketContext` |
| Sector | `analyze_sector_performance()` | `SectorComparison` |
| Momentum | `analyze_momentum()` | `MomentumAnalysis` |
| Sentiment | `analyze_sentiment()` | `SentimentAnalysis` |

### 3. Sentiment Sub-Analyzers

Sentiment runs 5 parallel async tasks:

```python
results = await asyncio.gather(
    get_fear_greed_index(),      # CNN Fear & Greed
    get_short_interest(data),    # Yahoo Finance
    get_vix_term_structure(),    # VIX Futures
    get_insider_activity(),      # SEC EDGAR
    get_put_call_ratio(data),    # Options Chain
    return_exceptions=True
)
```

**Timeout:** 10 seconds per indicator
**Minimum:** 2 of 5 indicators required

### 4. Signal Synthesis

```python
def synthesize_signal(
    ticker, company_name,
    earnings, fundamentals, analysts, historical,
    market_context, sector, earnings_timing,
    momentum, sentiment,
    breaking_news, geopolitical_risk_warning, geopolitical_risk_penalty
) -> Signal:
```

**Scoring:**
1. Collect available component scores
2. Apply normalized weights
3. Calculate weighted average → `final_score`
4. Apply adjustments (timing, overbought, risk-off)
5. Determine recommendation threshold

**Thresholds:**
```python
if final_score > 0.33:
    recommendation = "BUY"
elif final_score < -0.33:
    recommendation = "SELL"
else:
    recommendation = "HOLD"
```

---

## Caching Strategy

### What's Cached

| Data | TTL | Key |
|------|-----|-----|
| Market Context | 1 hour | `market_context` |
| Fear & Greed | 1 hour | `fear_greed` |
| VIX Structure | 1 hour | `vix_structure` |
| Breaking News | 1 hour | `breaking_news` |

### Cache Implementation

```python
_SENTIMENT_CACHE = {}
_CACHE_TTL_SECONDS = 3600  # 1 hour

def _get_cached(key: str):
    if key in _SENTIMENT_CACHE:
        value, timestamp = _SENTIMENT_CACHE[key]
        if time.time() - timestamp < _CACHE_TTL_SECONDS:
            return value
    return None

def _set_cache(key: str, value):
    _SENTIMENT_CACHE[key] = (value, time.time())
```

### Why This Matters

- First stock: ~8 seconds (full fetch)
- Second stock: ~4 seconds (reuses market data)
- Same stock again: ~4 seconds (no stock-level cache)

---

## Data Flow

### Single Stock Analysis

```
User Input: "AAPL"
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. FETCH DATA (yfinance)                                    │
│    - Stock info, earnings, price history                    │
│    - ~2 seconds                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PARALLEL ANALYSIS                                        │
│                                                             │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐                  │
│    │ Earnings │ │Fundmtls  │ │ Analysts │  ... (sync)      │
│    └──────────┘ └──────────┘ └──────────┘                  │
│                                                             │
│    ┌────────────────────────────────────┐                  │
│    │ Market Context (cached or fetch)   │  ~1 second       │
│    └────────────────────────────────────┘                  │
│                                                             │
│    ┌────────────────────────────────────┐                  │
│    │ Sentiment (5 async tasks)          │  ~3-5 seconds    │
│    │  - Fear/Greed (cached)             │                  │
│    │  - Short Interest                  │                  │
│    │  - VIX Structure (cached)          │                  │
│    │  - Insider Trading (slow!)         │                  │
│    │  - Put/Call Ratio                  │                  │
│    └────────────────────────────────────┘                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SYNTHESIZE SIGNAL                                        │
│    - Combine scores with weights                            │
│    - Apply adjustments                                      │
│    - Generate caveats                                       │
│    - ~10 ms                                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. OUTPUT                                                   │
│    - Text or JSON format                                    │
│    - Include disclaimer                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Risk Detection

### Geopolitical Risk

```python
GEOPOLITICAL_RISK_MAP = {
    "taiwan": {
        "keywords": ["taiwan", "tsmc", "strait"],
        "sectors": ["Technology", "Communication Services"],
        "affected_tickers": ["NVDA", "AMD", "TSM", ...],
        "impact": "Semiconductor supply chain disruption",
    },
    # ... china, russia_ukraine, middle_east, banking_crisis
}
```

**Process:**
1. Check breaking news for keywords
2. If keyword found, check if ticker in affected list
3. Apply confidence penalty (30% direct, 15% sector)

### Breaking News

```python
def check_breaking_news(verbose: bool = False) -> list[str] | None:
    """Scan Google News RSS for crisis keywords (last 24h)."""
```

**Crisis Keywords:**
```python
CRISIS_KEYWORDS = {
    "war": ["war", "invasion", "military strike", ...],
    "economic": ["recession", "crisis", "collapse", ...],
    "regulatory": ["sanctions", "embargo", "ban", ...],
    "disaster": ["earthquake", "hurricane", "pandemic", ...],
    "financial": ["emergency rate", "bailout", ...],
}
```

---

## File Structure

```
stock-analysis/
├── scripts/
│   ├── analyze_stock.py      # Main analysis engine (2500+ lines)
│   ├── portfolio.py          # Portfolio management
│   ├── dividends.py          # Dividend analysis
│   ├── watchlist.py          # Watchlist + alerts
│   └── test_stock_analysis.py # Unit tests
├── docs/
│   ├── CONCEPT.md            # Philosophy & ideas
│   ├── USAGE.md              # Practical guide
│   └── ARCHITECTURE.md       # This file
├── SKILL.md                  # OpenClaw skill definition
├── README.md                 # Project overview
└── .clawdhub/                # ClawHub metadata
```

---

## Data Storage

### Portfolio (`portfolios.json`)

```json
{
  "portfolios": [
    {
      "name": "Retirement",
      "created_at": "2024-01-01T00:00:00Z",
      "assets": [
        {
          "ticker": "AAPL",
          "quantity": 100,
          "cost_basis": 150.00,
          "type": "stock",
          "added_at": "2024-01-01T00:00:00Z"
        }
      ]
    }
  ]
}
```

### Watchlist (`watchlist.json`)

```json
[
  {
    "ticker": "NVDA",
    "added_at": "2024-01-15T10:30:00Z",
    "price_at_add": 700.00,
    "target_price": 800.00,
    "stop_price": 600.00,
    "alert_on_signal": true,
    "last_signal": "BUY",
    "last_check": "2024-01-20T08:00:00Z"
  }
]
```

---

## Dependencies

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "yfinance>=0.2.40",      # Stock data
#     "pandas>=2.0.0",         # Data manipulation
#     "fear-and-greed>=0.4",   # CNN Fear & Greed
#     "edgartools>=2.0.0",     # SEC EDGAR filings
#     "feedparser>=6.0.0",     # RSS parsing
# ]
# ///
```

**Why These:**
- `yfinance`: Most reliable free stock API
- `pandas`: Industry standard for financial data
- `fear-and-greed`: Simple CNN F&G wrapper
- `edgartools`: Clean SEC EDGAR access
- `feedparser`: Robust RSS parsing

---

## Performance Optimization

### Current

| Operation | Time |
|-----------|------|
| yfinance fetch | ~2s |
| Market context | ~1s (cached after) |
| Insider trading | ~3-5s (slowest!) |
| Sentiment (parallel) | ~3-5s |
| Synthesis | ~10ms |
| **Total** | **5-10s** |

### Fast Mode (`--fast`)

Skips:
- Insider trading (SEC EDGAR)
- Breaking news scan

**Result:** 2-3 seconds

### Future Optimizations

1. **Stock-level caching** — Cache fundamentals for 24h
2. **Batch API calls** — yfinance supports multiple tickers
3. **Background refresh** — Pre-fetch watchlist data
4. **Local SEC data** — Avoid EDGAR API calls

---

## Error Handling

### Retry Strategy

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        # fetch data
    except Exception as e:
        wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
        time.sleep(wait_time)
```

### Graceful Degradation

- Missing earnings → Skip dimension, reweight
- Missing analysts → Skip dimension, reweight
- Missing sentiment → Skip dimension, reweight
- API failure → Return None, continue with partial data

### Minimum Requirements

- At least 2 of 8 dimensions required
- At least 2 of 5 sentiment indicators required
- Otherwise → HOLD with low confidence
