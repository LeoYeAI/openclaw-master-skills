---
name: options-spread-conviction-engine
description: Multi-regime options spread analysis engine with quantitative rigor. Features regime detection (VIX-based), GARCH volatility forecasting, drawdown-constrained Kelly position sizing, and walk-forward backtesting. Scores vertical spreads (bull put, bear call, bull call, bear put) and multi-leg strategies (iron condors, butterflies, calendar spreads) using Ichimoku, RSI, MACD, Bollinger Bands, and IV term structure analysis.
version: 2.3.0
author: Leonardo Da Pinchy
metadata:
  openclaw:
    emoji: 📊
    requires:
      bins: ["python3"]
    install:
      - id: venv-setup
        kind: exec
        command: "cd {baseDir} && python3 scripts/setup-venv.sh"
        label: "Setup isolated Python environment with dependencies"
---

# Options Spread Conviction Engine

**Multi-regime options spread scoring using technical indicators and IV term structure analysis.**

## Install

```bash
brew install jq
npm install yahoo-finance2
sudo ln -s /opt/homebrew/bin/yahoo-finance /usr/local/bin/yf
```

## Overview

This engine analyzes any ticker and scores **seven** options strategies across two categories:

### Vertical Spreads (Directional)
| Strategy | Type | Philosophy | Ideal Setup |
|----------|------|------------|-------------|
| **bull_put** | Credit | Mean Reversion | Bullish trend + oversold dip |
| **bear_call** | Credit | Mean Reversion | Bearish trend + overbought rip |
| **bull_call** | Debit | Breakout | Strong bullish momentum |
| **bear_put** | Debit | Breakout | Strong bearish momentum |

### Multi-Leg Strategies (Non-Directional / Theta)
| Strategy | Type | Philosophy | Ideal Setup |
|----------|------|------------|-------------|
| **iron_condor** | Credit | Premium Selling | IV Rank >70, RSI neutral, range-bound |
| **butterfly** | Debit | Pinning Play | BB squeeze, RSI center, low ADX |
| **calendar** | Debit | Theta Harvest | Inverted IV term structure (front > back) |

## Scoring Methodology

### Vertical Spreads

Weights vary by strategy type (Credit = Mean Reversion, Debit = Breakout):

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

#### Iron Condor (Credit / Range-Bound)
| Component | Weight | Rationale |
|-----------|--------|-----------|
| IV Rank (BBW %) | 25 pts | Rich premiums to sell |
| RSI Neutrality | 20 pts | No directional momentum |
| ADX Range-Bound | 20 pts | Weak trend = range structure |
| Price Position | 20 pts | Centered in range = safe margins |
| MACD Neutrality | 15 pts | No acceleration in any direction |

**Triggers:**
- IV Rank > 70: Premium-rich environment
- RSI 40-60: Neutral momentum
- ADX < 25: Weak/no trend
- Price near %B center: Max profit zone maximized

**Strike Selection:**
- SELL put at 1-sigma below price (short put)
- BUY put at 2-sigma below (long put — wing)
- SELL call at 1-sigma above price (short call)
- BUY call at 2-sigma above (long call — wing)

**Output:**
- All 4 strikes (put_long, put_short, call_short, call_long)
- Max profit zone (width between short strikes)
- Wing width

#### Butterfly (Debit / Volatility Compression)
| Component | Weight | Rationale |
|-----------|--------|-----------|
| BB Squeeze | 30 pts | Vol compression = narrow range |
| RSI Neutrality | 25 pts | Price at equilibrium |
| ADX Weakness | 20 pts | No directional trend at all |
| Price Centering | 15 pts | At center of range for max profit |
| MACD Flatness | 10 pts | No momentum |

**Triggers:**
- BBW percentile < 25: Squeeze active
- RSI 45-55: Dead-center (tighter than condor)
- ADX < 20: Very weak trend
- MACD histogram near zero
- Price at %B = 0.50

**Strike Selection:**
- BUY 1 call at strike below center (lower wing)
- SELL 2 calls at center strike (body)
- BUY 1 call at strike above center (upper wing)

**Output:**
- 3 strikes (lower_long, middle_short, upper_long)
- Max profit price (= middle strike)
- Profit zone (approximate breakevens)

#### Calendar Spread (Debit / Theta Harvesting)
| Component | Weight | Rationale |
|-----------|--------|-----------|
| IV Term Structure | 30 pts | Front IV > Back IV = theta edge |
| Price Stability | 20 pts | Price stays near strike |
| RSI Neutrality | 20 pts | Not trending away from strike |
| ADX Moderate | 15 pts | Some structure, not trending hard |
| MACD Neutrality | 15 pts | No directional acceleration |

**Triggers:**
- Front-month IV > Back-month IV by > 5%: Inverted term structure
- Low recent volatility: Price stability
- RSI neutral: No directional momentum
- ADX 18-25: Moderate trend structure (not chaos)

**Data Sources:**
- Primary: Live options chain IV from Yahoo Finance
- Fallback: Historical volatility proxy (HV 10-day vs 30-day)

**Strike Selection:**
- ATM strike (rounded to standard interval)
- Front expiry: nearest available
- Back expiry: 25+ days after front

**Output:**
- Single strike (both legs)
- Front and back expiry dates
- IV differential (%)
- Theta advantage description

## Conviction Tiers

| Score | Tier | Action |
|-------|------|--------|
| 80-100 | EXECUTE | High conviction — Enter the spread |
| 60-79 | PREPARE | Favorable — Size the trade |
| 40-59 | WATCH | Interesting — Add to watchlist |
| 0-39 | WAIT | Poor conditions — Avoid / No setup |

## Usage

### Vertical Spreads

```bash
# Basic analysis (auto-detects best strategy)
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
conviction-engine TSLA --strategy butterfly --json
conviction-engine SPY --strategy calendar --json | jq '.[0].iv_term_structure'
```

### Full Options

```bash
conviction-engine <ticker> [ticker...]
  --strategy {bull_put,bear_call,bull_call,bear_put,iron_condor,butterfly,calendar}
  --period {1y,2y,3y,5y}
  --interval {1h,1d,1wk}
  --json
```

## Example Outputs

### Iron Condor

```
================================================================================
SPY — Iron Condor (Credit)
================================================================================
Price: $681.27 | Score: 31.8/100 → WAIT

[IV Rank +2.5/25]
  IV Rank (BBW proxy): 5% (VERY_LOW)
  BBW: 3.17 (1Y range: 2.37 - 18.13)
  Premiums are THIN — poor risk/reward for credit

Strikes:
  BUY  680.0P | SELL 685.0P
  SELL 695.0C | BUY  700.0C
  Max Profit Zone: $685.0 - $695.0
  Wing Width: $5.00
```

### Butterfly

```
================================================================================
SPY — Long Butterfly (Debit)
================================================================================
Price: $681.27 | Score: 64.5/100 → PREPARE

[BB Squeeze +27.0/30]
  Bandwidth: 3.1701 (percentile: 21%)
  SQUEEZE ACTIVE — 19 consecutive bars

Strikes:
  BUY 1x 685.0C | SELL 2x 690.0C | BUY 1x 695.0C
  Max Profit Price: $690.0
  Profit Zone: ~$685.0 - $695.0
```

### Calendar Spread

```
================================================================================
SPY — Calendar Spread (Debit)
================================================================================
Price: $681.27 | Score: 67.2/100 → PREPARE

[IV Term Structure +30.0/30]
  Front IV: 27.5% | Back IV: 19.4%
  Differential: +41.7%
  INVERTED TERM STRUCTURE — calendar opportunity confirmed

Strikes:
  Strike: $680.0
  SELL 2026-02-13 | BUY 2026-03-13
  Theta Advantage: Front IV > Back IV by 41.7%
```

## IV Rank Approximation

IV Rank is approximated using **Bollinger Bandwidth (BBW) percentile** over 252 trading days:

```
IV Rank ≈ (Current BBW - 52wk Low BBW) / (52wk High BBW - 52wk Low BBW) × 100
```

This correlation is well-documented: realized volatility (BBW) and implied volatility rank move with ~0.7-0.8 correlation (Sinclair, "Volatility Trading", 2013).

## IV Term Structure

For calendar spreads, the engine attempts to fetch live ATM implied volatility from Yahoo Finance options chains. If unavailable, it falls back to historical volatility term structure (HV 10-day vs HV 30-day) as a proxy.

## Quantitative Modules (v2.3.0)

The engine now includes four quantitative modules for rigorous strategy validation and optimization:

### 1. Regime Detector (`regime_detector.py`)

Market regime classification using VIX percentiles:
- **CRISIS**: VIX > 80th percentile — favors premium selling (iron condors)
- **HIGH_VOL**: VIX 60-80th — elevated IV benefits credit spreads
- **NORMAL**: VIX 40-60th — balanced environment, all strategies viable
- **LOW_VOL**: VIX 20-40th — cheap options favor debit spreads
- **EUPHORIA**: VIX < 20th — momentum continues, mean reversion brewing

```bash
# Detect current regime
python3 scripts/regime_detector.py

# Get regime-adjusted weights for specific strategy
python3 scripts/regime_detector.py --strategy iron_condor --json
```

**Integration:**
```python
from regime_detector import RegimeDetector

detector = RegimeDetector()
regime, confidence = detector.detect_regime()
weights = detector.get_regime_weights(regime)
adjusted_score, reasoning = detector.regime_aware_score(75, regime, 'bull_put')
```

### 2. Volatility Forecaster (`vol_forecaster.py`)

GARCH-based realized volatility forecasting with VRP analysis:
- Fits GARCH(1,1) to historical returns
- Forecasts realized volatility over configurable horizon
- Calculates volatility risk premium (IV - RV forecast)
- Provides conviction adjustments based on VRP

```bash
# Analyze AAPL volatility
python3 scripts/vol_forecaster.py AAPL

# Compare IV = 25% vs forecast RV
python3 scripts/vol_forecaster.py SPY --iv 0.25 --horizon 5
```

**Interpretation:**
- VRP > 5%: Favorable for selling premium (credit spreads)
- VRP < -5%: Favorable for buying premium (debit spreads)
- VRP near 0: No volatility edge, focus on directional setup

**Integration:**
```python
from vol_forecaster import VolatilityForecaster

forecaster = VolatilityForecaster("AAPL")
params = forecaster.fit_garch()  # Returns omega, alpha, beta
forecast = forecaster.forecast_vol(horizon=5)
vrp, strength, rec = forecaster.vol_risk_premium(iv=0.25, rv_forecast=forecast.annualized_vol)
adjusted_score, reasoning = forecaster.add_to_conviction(70, vrp_signal, 'bull_put')
```

### 3. Enhanced Kelly Sizer (`enhanced_kelly.py`)

Drawdown-constrained, correlation-aware position sizing:
- Full Kelly criterion calculation
- Drawdown constraint: f_dd = f_kelly × (1 - target_dd / max_dd)
- Conviction-based Kelly scaling:
  - 90-100: Half Kelly
  - 80-89: Quarter Kelly
  - 60-79: Eighth Kelly
  - <60: No position
- Correlation penalty for portfolio context

```bash
# Calculate position with $390 account
python3 scripts/enhanced_kelly.py --loss 80 --win 40 --pop 0.65 --conviction 85

# Include correlation with existing position
python3 scripts/enhanced_kelly.py --loss 80 --win 40 --pop 0.65 --conviction 85 --correlation 0.3
```

**Integration:**
```python
from enhanced_kelly import EnhancedKellySizer

sizer = EnhancedKellySizer(account_value=390, max_drawdown=0.20)
result = sizer.calculate_position(
    spread_cost=80,
    max_loss=80,
    win_amount=40,
    conviction=85,
    pop=0.65,
    existing_correlation=0.0
)
# Returns: contracts, total_risk, kelly_fraction, recommendation
```

### 4. Backtest Validator (`backtest_validator.py`)

Walk-forward validation of conviction scores:
- Simulates historical trades across ticker universe
- Validates tier separation (EXECUTE vs WAIT performance)
- Statistical tests (t-tests, ANOVA)
- Tier separation scoring (0-1)
- Weight calibration suggestions

```bash
# Backtest bull_put on AAPL, MSFT, SPY (2022-2024)
python3 scripts/backtest_validator.py --tickers AAPL MSFT SPY --start 2022-01-01 --end 2024-01-01 --strategy bull_put

# JSON output for analysis
python3 scripts/backtest_validator.py --tickers SPY --json
```

**Output Metrics:**
- Win rate per tier
- Expectancy per tier: (win_rate × avg_win) - (loss_rate × avg_loss)
- Sharpe ratio per tier
- P-values for tier differences
- Separation score (0-1, higher = better discrimination)

**Integration:**
```python
from backtest_validator import BacktestValidator

validator = BacktestValidator(engine, "2022-01-01", "2024-01-01")
results_df = validator.run_walk_forward(["AAPL", "MSFT"], hold_days=5)
report = validator.validate_tiers(results_df)
print(f"Separation score: {report.tier_separation_score:.2f}")
print(f"EXECUTE vs WAIT p-value: {report.p_values['execute_vs_wait']:.4f}")
```

### 5. Quantitative Integration (`quantitative_integration.py`)

Unified interface combining all quantitative modules:

```bash
# Full quantitative analysis with regime and VRP
python3 scripts/quantitative_integration.py AAPL --regime-aware --vol-aware

# With Kelly sizing
python3 scripts/quantitative_integration.py SPY --regime-aware --pop 0.65 --max-loss 80 --win-amount 40

# Run backtest validation
python3 scripts/quantitative_integration.py --backtest SPY QQQ --start 2022-01-01 --end 2024-01-01
```

**Integration:**
```python
from quantitative_integration import QuantConvictionEngine

engine = QuantConvictionEngine(account_value=390, max_drawdown=0.20)

# Analyze with regime and VRP adjustments
result = engine.analyze("AAPL", "bull_put", regime_aware=True, vol_aware=True)
print(f"Final score: {result.final_score}")
print(f"Regime: {result.regime}")
print(f"VRP: {result.vrp_signal.vrp if result.vrp_signal else 'N/A'}")

# Calculate position size
sizing = engine.calculate_position(result, pop=0.65, max_loss=80, win_amount=40)
print(f"Contracts: {sizing['contracts']}")

# Run backtest validation
report = engine.run_backtest(["SPY", "QQQ"], "2022-01-01", "2024-01-01")
print(f"Recommendation: {report.recommendation}")
```

## Academic Foundation

- **Ichimoku Cloud** — Trend structure (Hosoda, 1968)
- **RSI** — Momentum oscillator (Wilder, 1978)
- **MACD** — Trend momentum (Appel, 1979)
- **Bollinger Bands** — Volatility envelopes (Bollinger, 2001)
- **IV Rank / Term Structure** — Options market microstructure (Sinclair, 2013)

Combining orthogonal signals reduces false-positive rate compared to single-indicator strategies (Pring, 2002; Murphy, 1999).

## Architecture

```
conviction-engine/
├── scripts/
│   ├── conviction-engine              # CLI wrapper (bash)
│   ├── spread_conviction_engine.py    # Core engine (vertical spreads)
│   ├── multi_leg_strategies.py        # Multi-leg extensions
│   ├── quantitative_integration.py    # Unified quantitative interface
│   ├── regime_detector.py             # VIX-based regime classification
│   ├── vol_forecaster.py              # GARCH volatility forecasting
│   ├── enhanced_kelly.py              # Drawdown-constrained Kelly sizing
│   ├── backtest_validator.py          # Walk-forward validation
│   ├── quant_scanner.py               # Quantitative options scanner
│   ├── market_scanner.py              # Technical market scanner
│   ├── calculator.py                  # Black-Scholes & POP calculator
│   ├── position_sizer.py              # Kelly position sizing
│   ├── chain_analyzer.py              # IV surface analyzer
│   ├── options_math.py                # Core mathematical models
│   └── setup-venv.sh                  # Environment setup
├── tests/                             # Unit tests
│   ├── test_regime_detector.py
│   ├── test_vol_forecaster.py
│   ├── test_enhanced_kelly.py
│   ├── test_backtest_validator.py
│   └── run_tests.py
└── SKILL.md                           # This documentation
```

### Module Separation

- **spread_conviction_engine.py**: Vertical spreads, shared infrastructure (data fetching, indicator computation)
- **multi_leg_strategies.py**: Iron condors, butterflies, calendars (imports from main engine)
- **quantitative_integration.py**: Unified interface for regime/vol/Kelly/backtest modules
- **regime_detector.py**: Market regime classification using VIX percentiles
- **vol_forecaster.py**: GARCH-based realized volatility forecasting
- **enhanced_kelly.py**: Drawdown-constrained, correlation-aware position sizing
- **backtest_validator.py**: Walk-forward validation of conviction scores

This separation keeps concerns clean while avoiding duplication.

## Limitations & Assumptions

### IV Data
- **Yahoo Finance Limitations**: Options chains may be unavailable after market hours or for low-volume tickers
- **Fallback**: Historical volatility (HV) proxy is less accurate than live IV but provides signal
- **IV Rank**: Approximated from BBW; actual IV Rank requires options chain data

### Strike Selection
- **Approximation**: Strikes derived from Bollinger Band levels (1-sigma / 2-sigma)
- **Rounding**: Rounded to standard option strike intervals based on stock price
- **No Live Pricing**: Does not fetch live option premiums; strike selection is structural, not value-optimized

### Data Quality
- Minimum 180 trading days required for full Ichimoku cloud population
- Multi-leg strategies require options chains (calendar spreads especially)
- After-hours analysis may have reduced data quality

### Market Assumptions
- Assumes normal options market conditions (not extreme volatility events)
- Strike intervals assume US equity options conventions
- Not tested on futures, commodities, or non-US markets

## Requirements

- Python 3.10+ (Python 3.14+ supported via pure-python mode)
- Isolated virtual environment (auto-created on first run)
- Internet connection (fetches data from Yahoo Finance)

## Installation

```bash
clawhub install options-spread-conviction-engine
```

The skill automatically creates a virtual environment and installs:
- pandas >= 2.0
- pandas_ta >= 0.4.0 (pure Python mode on 3.14+)
- yfinance >= 1.0
- scipy, tqdm

**Note:** On Python 3.14+, the engine runs in pure Python mode without numba. Performance is slightly reduced but all functionality works correctly.

## Market Scanners

The engine includes two distinct scanning tools for different trading philosophies:

### 1. Technical Scanner (market_scanner.py)
Automates the search for high-conviction plays across entire stock universes using technical indicators (Ichimoku, RSI, MACD, BB).

#### Features
- Scans S&P 500, Nasdaq 100, or custom ticker lists.
- Filters for EXECUTE tier (conviction ≥80).
- Runs position sizing to ensure trades fit account guardrails.

#### Usage
```bash
# Scan S&P 500 for high-conviction technical setups
python3 scripts/market_scanner.py --universe sp500
```

### 2. Quantitative Scanner (quant_scanner.py)
A mathematically-rigorous scanner that ignores technical indicators in favor of market microstructure and probability.

#### Features
- **IV Surface Analysis**: Analyzes skew and term structure.
- **Monte Carlo POP**: 10,000-run simulations for true Probability of Profit.
- **EV Optimization**: Finds trades with the highest risk-adjusted mathematical expectancy.
- **Account-Aware**: Enforces small-account constraints ($100 max risk).

#### Usage
```bash
# Maximize POP (Probability of Profit) for SPY
python3 scripts/quant_scanner.py SPY --mode pop

# High-expectancy (EV) plays with specific DTE
python3 scripts/quant_scanner.py AAPL TSLA --mode ev --min-dte 30
```

## Calculator & Position Sizer

The integrated toolchain includes:

### calculator.py
Black-Scholes options pricing with support for:
- Single options: calls, puts
- Vertical spreads: bull call, bear put
- Multi-leg: iron condors, butterflies
- Greeks calculation (delta, gamma, theta, vega, rho)
- Monte Carlo POP simulation

### position_sizer.py
Kelly criterion position sizing adapted for small accounts:
- Full Kelly and fractional Kelly (default 0.25)
- Account guardrails ($390 default, $100 max risk)
- Trade screening and ranking
- Strike adjustment suggestions

```python
from position_sizer import calculate_position

result = calculate_position(
    account_value=390,
    max_loss_per_spread=80,
    win_amount=40,
    pop=0.65,
)
# Returns: contracts, total_risk, recommendation, reason
```

## Files

- `scripts/conviction-engine` — Main CLI wrapper for conviction engine
- `scripts/spread_conviction_engine.py` — Core engine (vertical spreads)
- `scripts/multi_leg_strategies.py` — Multi-leg extensions (v2.0.0)
- `scripts/market_scanner.py` — Automated market scanner for EXECUTE plays
- `scripts/calculator.py` — Black-Scholes pricing, Greeks, Monte Carlo POP
- `scripts/position_sizer.py` — Kelly criterion position sizing
- `scripts/setup-venv.sh` — Environment setup
- `data/sp500_tickers.txt` — S&P 500 constituents
- `data/ndx100_tickers.txt` — Nasdaq 100 constituents
- `assets/` — Documentation and examples

## Version History

- **v2.3.0** (2026-02-13): Quantitative rigor upgrade
  - Regime Detector: VIX-based market regime classification
  - Volatility Forecaster: GARCH-based RV forecasting with VRP analysis
  - Enhanced Kelly Sizer: Drawdown-constrained, correlation-aware position sizing
  - Backtest Validator: Walk-forward validation with tier separation testing
  - Quantitative Integration: Unified interface for all quantitative modules
  - Comprehensive unit test suite for all new modules
- **v2.2.0** (2026-02-13): Kelly Criterion position sizing with full/half Kelly, edge calculation, and account-aware contract sizing
- **v2.1.0** (2026-02-12): Added market scanner, integrated calculator and position sizer
- **v2.0.0** (2026-02-12): Added multi-leg strategies (iron condor, butterfly, calendar)
- **v1.2.1** (2026-02-09): Volume multiplier, dynamic strike suggestions
- **v1.1.0** (2026-02-08): Cross-signal weighting, multi-strategy support
- **v1.0.0** (2026-02-07): Initial bull put spread engine

## License

MIT — Part of the Financial Toolkit for OpenClaw
