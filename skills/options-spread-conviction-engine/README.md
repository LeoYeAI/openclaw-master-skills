# Options Spread Conviction Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://clawhub.com)

**Multi-regime options spread analysis engine with Kelly Criterion Position Sizing, Multi-Leg Strategies, and Quantitative Scanning.**

A comprehensive scoring system for options traders that analyzes market conditions and provides actionable conviction scores (0-100) for seven strategies including vertical spreads, iron condors, butterflies, and calendar spreads. Features mathematically-rigorous Kelly criterion position sizing integrated directly into the conviction engine.

## 🎯 What It Does

Analyzes any stock ticker and scores **seven** options strategies across directional and non-directional setups:

| Strategy | Type | Philosophy | Ideal Setup |
|----------|------|------------|-------------|
| **bull_put** | Credit | Mean Reversion | Bullish trend + oversold dip |
| **bear_call** | Credit | Mean Reversion | Bearish trend + overbought rip |
| **bull_call** | Debit | Breakout | Strong bullish momentum |
| **bear_put** | Debit | Breakout | Strong bearish momentum |
| **iron_condor** | Credit | Premium Selling | IV Rank >70, range-bound |
| **butterfly** | Debit | Pinning Play | Vol compression, low trend |
| **calendar** | Debit | Theta Harvest | Inverted IV term structure |

### Key Features

- **Kelly Criterion Position Sizing**: Mathematically optimal position sizing based on edge, win probability, and account constraints. Half-Kelly default for options volatility, with 25% bankroll cap and full edge case handling.
- **Multi-Leg Strategy Support**: Iron condors, butterflies, and calendar spreads with IV term structure analysis.
- **Quantitative Scanners**: Monte Carlo POP simulation and expected value optimization.
- **Volume Multiplier**: Rewards breakouts with high volume, penalizes low-volume fakeouts.
- **Dynamic Strike Suggestions**: Auto-calculates recommended strikes based on 1-sigma/2-sigma Bollinger levels.

## 📊 Scoring Methodology

### Vertical Spreads (Credit/Debit)

Weights vary by strategy type:

#### Credit Spreads (bull_put, bear_call)
| Indicator | Weight | Purpose |
|-----------|--------|---------|
| Ichimoku Cloud | 25 pts | Trend structure & equilibrium |
| RSI | 20 pts | Entry timing (mean-reversion) |
| MACD | 15 pts | Momentum confirmation |
| Bollinger Bands | 25 pts | Volatility regime |
| ADX | 15 pts | Trend strength validation |

#### Debit Spreads (bull_call, bear_put)
| Indicator | Weight | Purpose |
|-----------|--------|---------|
| Ichimoku Cloud | 20 pts | Trend confirmation |
| RSI | 10 pts | Directional momentum |
| MACD | 30 pts | Breakout acceleration |
| Bollinger Bands | 25 pts | Bandwidth expansion |
| ADX | 15 pts | Trend strength validation |

### Multi-Leg Strategies

#### Iron Condor (Range-Bound)
| Component | Weight | Rationale |
|-----------|--------|-----------|
| IV Rank | 25 pts | Rich premiums to sell |
| RSI Neutrality | 20 pts | No directional momentum |
| ADX Range-Bound | 20 pts | Weak trend = range structure |
| Price Position | 20 pts | Centered in range |
| MACD Neutrality | 15 pts | No acceleration |

#### Butterfly (Volatility Compression)
| Component | Weight | Rationale |
|-----------|--------|-----------|
| BB Squeeze | 30 pts | Vol compression signal |
| RSI Neutrality | 25 pts | Price at equilibrium |
| ADX Weakness | 20 pts | No trend |
| Price Centering | 15 pts | At middle strike |
| MACD Flatness | 10 pts | No momentum |

#### Calendar Spread (Theta Harvest)
| Component | Weight | Rationale |
|-----------|--------|-----------|
| IV Term Structure | 30 pts | Front IV > Back IV |
| Price Stability | 20 pts | Near strike stability |
| RSI Neutrality | 20 pts | No directional drift |
| ADX Moderate | 15 pts | Some structure |
| MACD Neutrality | 15 pts | No acceleration |

**Total: 100 points for all strategies**

## 🎚️ Conviction Tiers

| Score | Tier | Action |
|-------|------|--------|
| 80-100 | **EXECUTE** | High conviction — Enter the spread |
| 60-79 | **PREPARE** | Favorable — Size the trade |
| 40-59 | **WATCH** | Interesting — Add to watchlist |
| 0-39 | **WAIT** | Poor conditions — Avoid / No setup |

## 💰 Kelly Criterion Position Sizing

Integrated mathematically-optimal position sizing using the Kelly criterion, adapted for options trading volatility.

### Formula
```
f* = (p·b − q) / b
```
Where:
- `f*` = optimal fraction of bankroll to risk
- `p` = probability of win (POP)
- `q` = probability of loss (1 − p)
- `b` = win/loss ratio (average win / average loss)

### Safety Adjustments for Options
- **Half-Kelly default**: 0.5× multiplier for options volatility uncertainty
- **25% bankroll cap**: Hard limit to prevent ruin from model error
- **Per-trade limits**: Respects `MAX_RISK_PER_TRADE` constraints
- **Cash buffer**: Maintains minimum cash reserves

### Usage
```python
from options_math import kelly_position_size, KellyResult

result = kelly_position_size(
    account_balance=1000.0,
    pop=0.65,           # 65% probability of profit
    max_profit=40.0,    # $40 credit received
    max_loss=100.0,     # $100 risk per spread
    kelly_multiplier=0.5,  # Half-Kelly for safety
)

print(f"Contracts: {result.recommended_contracts}")
print(f"Risk: ${result.recommended_risk:.2f}")
print(f"Kelly fraction: {result.adjusted_kelly_fraction:.2%}")
```

### Edge Case Handling
- **Negative edge** → 0 contracts (trade rejected)
- **Zero edge** → 0 contracts (no mathematical advantage)
- **High edge** → Capped at 25% of bankroll
- **Insufficient funds** → 0 contracts with explanation

## 🚀 Installation

### Via ClawHub (Recommended)
```bash
clawhub install options-spread-conviction-engine
conviction-engine AAPL --strategy bull_call
```

### Manual Installation
```bash
git clone https://github.com/AdamNaghs/Options-Spread-Conviction-Engine.git
cd Options-Spread-Conviction-Engine
bash scripts/setup-venv.sh
./scripts/conviction-engine AAPL
```

## 📖 Usage

### Vertical Spreads
```bash
# Analyze AAPL with default strategy (bull_put)
conviction-engine AAPL

# Specific strategy
conviction-engine SPY --strategy bear_call
conviction-engine QQQ --strategy bull_call --period 2y
```

### Multi-Leg Strategies
```bash
# Iron Condor — high IV, range-bound
conviction-engine SPY --strategy iron_condor

# Butterfly — volatility compression, pinning play
conviction-engine AAPL --strategy butterfly

# Calendar — inverted IV term structure, theta harvest
conviction-engine TSLA --strategy calendar
```

### Multiple Tickers
```bash
conviction-engine AAPL MSFT GOOGL --strategy bull_put
conviction-engine SPY QQQ IWM --strategy iron_condor
```

### JSON Output (for automation)
```bash
conviction-engine TSLA --strategy bear_call --json
conviction-engine SPY --strategy calendar --json | jq '.[0].iv_term_structure'
```

### Full Options
```bash
conviction-engine <ticker> [ticker...]
  --strategy {bull_put,bear_call,bull_call,bear_put,iron_condor,butterfly,calendar}
  --period {1y,2y,3y,5y}
  --interval {1h,1d,1wk}
  --json
  --verbose
```

## 📈 Example Output

```
======================================================================
  CONVICTION REPORT: AAPL
  Strategy: Bull Call Spread (Debit)
======================================================================
  Price:       $272.19
  Trend:       BULL
  Conviction:  74.0 / 100
  Action Tier: 🟠 PREPARE
----------------------------------------------------------------------
  Strategy: Bull Call Spread (Debit)  (Breakout / Momentum)
  Ideal Setup: Strong bullish momentum + expanding volatility → breakout
  
  Market Trend: BULL | Score: 74.0/100 → PREPARE
  ✅ Trend aligns with bullish strategy
  
  [Ichimoku +18.8/25]
    Price is ABOVE the cloud
    TK Cross: BEARISH (Tenkan 262.17 vs Kijun 266.02)
    Cloud: GREEN, thickness 20.59
  [RSI +15.0/15]
    RSI(14) = 59.1 → STRONG_BULLISH_MOMENTUM (55–70)
  [MACD +17.3/35]
    MACD above Signal (2.4685 vs -0.3866)
    Histogram: 2.8551 (FALLING)
  [Bollinger +22.9/25]
    %B = 0.7886 | Bandwidth = 15.1431
    Bands: [241.05 — 260.79 — 280.54]
======================================================================
```

## 🎓 Academic Foundation

- **Ichimoku Cloud** — Trend structure & equilibrium (Hosoda, 1968)
- **RSI** — Momentum & mean-reversion potential (Wilder, 1978)
- **MACD** — Trend momentum & acceleration (Appel, 1979)
- **Bollinger Bands** — Volatility regime & price envelopes (Bollinger, 2001)

Combining orthogonal signals reduces false-positive rate compared to any single-indicator strategy (Pring, 2002; Murphy, 1999).

## ⚙️ Requirements

- Python 3.10+ (Python 3.14+ supported via pure-Python mode)
- Isolated virtual environment (auto-created on first run)
- Internet connection (fetches data from Yahoo Finance)

### Dependencies
- pandas >= 2.0
- pandas_ta >= 0.4.0 (pure Python mode on 3.14+)
- yfinance >= 1.0
- scipy
- tqdm

**Note:** On Python 3.14+, the engine runs without numba (numba doesn't support 3.14 yet). Performance is slightly reduced but all functionality works correctly.

## 🏗️ Architecture

```
skills/options-spread-conviction-engine/
├── SKILL.md                    # Skill documentation
├── README.md                   # This file
├── _meta.json                  # Skill metadata
├── scripts/
│   ├── conviction-engine       # Main CLI wrapper
│   ├── setup-venv.sh          # Environment setup
│   ├── spread_conviction_engine.py  # Core engine (vertical spreads)
│   ├── multi_leg_strategies.py     # Iron condor, butterfly, calendar
│   ├── quant_scanner.py        # Quantitative options scanner (Monte Carlo POP)
│   ├── market_scanner.py       # Technical scanner for EXECUTE plays
│   ├── chain_analyzer.py       # IV surface & skew analysis
│   ├── calculator.py           # Black-Scholes pricing & Greeks
│   ├── position_sizer.py       # Kelly criterion position sizing
│   ├── options_math.py         # Core math: Black-Scholes, Monte Carlo, Kelly
│   └── numba.py               # Python 3.14+ compatibility shim
└── assets/                     # Additional resources
```

## 🧪 Quantitative Options Scanner (Alpha)

The **quant_scanner.py** script provides a mathematically-rigorous alternative to the technical-indicator-heavy conviction engine. It focuses on market microstructure, IV surfaces, and probability distributions.

### Features
- **Options Chain Analysis**: Full chain fetching with IV surface, skew, and term structure analysis.
- **Monte Carlo POP**: Calculates Probability of Profit using 10,000-run Monte Carlo simulations.
- **Expected Value (EV)**: Scores trades based on risk-adjusted mathematical expectancy.
- **Small Account Guardrails**: Hard-coded constraints for accounts under $500 (max $100 risk per trade).

### Usage
```bash
# Maximize POP (Probability of Profit) for SPY
python3 scripts/quant_scanner.py SPY --mode pop

# Find income/theta plays for multiple tickers
python3 scripts/quant_scanner.py AAPL TSLA NVDA --mode income --max-loss 100

# High-expectancy (EV) plays with specific DTE
python3 scripts/quant_scanner.py SPY --mode ev --min-dte 30 --max-dte 45
```

## 🔧 How It Works

1. **Data Fetching** — Downloads OHLCV data from Yahoo Finance
2. **Indicator Computation** — Calculates Ichimoku, RSI, MACD, Bollinger Bands
3. **Strategy-Aware Scoring** — Each indicator scored based on strategy type
4. **Aggregation** — Sums component scores into 0-100 conviction
5. **Tier Classification** — Maps score to actionable tier (WAIT/WATCH/PREPARE/EXECUTE)
6. **Rationale Generation** — Human-readable explanation of the score

## 📝 License

MIT — Part of the Financial Toolkit for OpenClaw

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Backtesting module with historical trade simulation
- Webhook alerts for high-conviction setups
- Additional indicators (ATR, VWAP, Volume Profile)
- Execution API integration (TD Ameritrade, Interactive Brokers)

## 🔄 Version History

- **v2.2.0** (2026-02-13): Kelly Criterion position sizing integrated into options_math.py with full/half Kelly, edge calculation, and position sizing constraints
- **v2.1.0** (2026-02-12): Added market scanner, integrated calculator and position sizer
- **v2.0.0** (2026-02-12): Multi-leg strategies (iron condor, butterfly, calendar) with IV term structure analysis
- **v1.2.1** (2026-02-09): Volume multiplier, dynamic strike suggestions
- **v1.1.0** (2026-02-08): Cross-signal weighting, multi-strategy support
- **v1.0.0** (2026-02-07): Initial bull put spread engine

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Not financial advice. Always do your own due diligence before making investment decisions. Past performance does not guarantee future results.

---

**Built with OpenClaw** | **Authors:** Adam Naghavi & Leonardo Da Pinchy
