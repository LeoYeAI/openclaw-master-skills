# Quantitative Options Scanner

A mathematically-rigorous options scanner built from first principles, replacing the technical-indicator-heavy conviction engine with options-first analysis.

## Overview

This scanner analyzes options chains, volatility surfaces, and multi-leg strategies to find optimal trades for small accounts.

### Key Features

1. **Options-First Analysis**
   - Fetches live options chains from Yahoo Finance
   - Analyzes implied volatility, skew, and term structure
   - Calculates Black-Scholes Greeks (Delta, Gamma, Theta, Vega, Rho)

2. **Multi-Leg Strategy Optimization**
   - Automatically discovers optimal vertical spreads
   - Iron condors (planned)
   - Optimizes for: max POP, max expected value, min max-loss

3. **Mathematical Scoring System**
   - Probability of Profit (POP) via Black-Scholes/Monte Carlo
   - Expected Value = (POP × max_profit) - ((1-POP) × max_loss)
   - Risk-adjusted return (Sharpe-like metric)
   - Greeks balance for income plays

4. **Account-Aware Filtering**
   - Hard constraints: $390 account, $100 max loss per trade, $150 cash buffer
   - Auto-filters spreads that don't fit
   - Suggests optimal width given account size

## Account Constraints (Hard-Coded)

- **Total Account:** $390
- **Max Risk Per Trade:** $100
- **Min Cash Buffer:** $150
- **Available Capital:** $240
- **Preferred DTE:** 7-45 days
- **Spread Width:** $2-5 to fit account

## Modules

### `options_math.py`
Core mathematical functions:
- `BlackScholes`: Option pricing and Greeks calculation
- `ProbabilityCalculator`: POP calculations for various strategies
- `VolatilityAnalyzer`: IV rank, percentile, skew analysis
- Account constraint functions

### `chain_analyzer.py`
Options chain fetching and parsing:
- `ChainFetcher`: Fetches from Yahoo Finance with rate limiting
- `ChainAnalyzer`: Analyzes liquidity, finds ATM/OTM options
- Caching for performance

### `leg_optimizer.py`
Multi-leg strategy optimization:
- `LegOptimizer`: Finds optimal vertical spreads and iron condors
- `MultiLegStrategy`: Strategy container with metrics
- Scoring system for different modes (POP, EV, income, earnings)

### `quant_scanner.py`
Main CLI interface:
- Scan single or multiple tickers
- Multiple scanning modes
- JSON output for automation

## Usage

```bash
# Scan single ticker, maximize POP
./quant-scanner SPY --mode pop

# Scan multiple tickers
./quant-scanner AAPL TSLA NVDA --mode ev

# Income mode (theta-focused)
./quant-scanner QQQ --mode income --min-dte 14 --max-dte 45

# JSON output for automation
./quant-scanner SPY --mode pop --json
```

## Scanning Modes

- `--mode pop`: Maximize probability of profit
- `--mode ev`: Maximize expected value
- `--mode income`: Maximize theta with delta neutrality
- `--mode earnings`: Pre-earnings vol crush plays

## Example Output

```
STRATEGY #1: PUT_CREDIT_SPREAD

  LEGS:
    SELL PUT  @ $ 265.00 | Premium: $4.25 | DTE: 1
    BUY  PUT  @ $ 262.50 | Premium: $2.64 | DTE: 1

  P&L PROFILE:
    Max Profit:     $ 161.00
    Max Loss:       $  89.00 ✓ FITS
    Breakeven(s):   $263.39

  PROBABILITY & VALUE:
    Probability of Profit (POP):  38.2%
    Expected Value (EV):         $+6.57
    Risk-Adjusted Return:        +26.95

  GREEKS (Per Contract):
    Delta: +0.156
    Theta: $-0.10/day
```

## Math Breakdown Example

**Trade:** AAPL Put Credit Spread
- **Legs:** Sell $265 Put @ $4.25, Buy $262.50 Put @ $2.64
- **Net Credit:** $1.61 per share = $161 per contract
- **Width:** $265 - $262.50 = $2.50
- **Max Loss:** ($2.50 - $1.61) × 100 = $89
- **POP Calculation:** Using Black-Scholes with 1 DTE, 20% IV
  - Breakeven: $265 - $1.61 = $263.39
  - P(S_T > $263.39) = 38.2%
- **Expected Value:** (0.382 × $161) - (0.618 × $89) = $6.57

## Files

- `quant_scanner.py` - Main CLI
- `options_math.py` - Mathematical core
- `chain_analyzer.py` - Data fetching
- `leg_optimizer.py` - Strategy optimization
- `quant-scanner` - CLI symlink

## Future Enhancements

1. Iron condor optimization
2. Calendar spread analysis
3. Butterfly strategies
4. Earnings calendar integration
5. Realized volatility tracking
6. IV rank vs historical
