---
name: vibetrading-code-gen
description: Generate executable Hyperliquid trading strategy code from natural language prompts. Use when a user wants to create automated trading strategies for Hyperliquid exchange based on their trading ideas, technical indicators, or VibeTrading signals. The skill generates complete Python code with proper error handling, logging, and configuration using actual Hyperliquid API wrappers.
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "requires": { "bins": ["python3"] },
        "min_python_version": "3.6"
      }
  }
---

# VibeTrading Code Generator

Generate executable Hyperliquid trading strategy code from natural language prompts. This skill transforms trading ideas into ready-to-run Python code using actual Hyperliquid API implementations. Generated code includes complete API integration, error handling, logging, and configuration management.

## Quick Start

### Basic Usage

```bash
# Generate a simple RSI strategy
python scripts/strategy_generator.py "Generate a BTC RSI strategy, buy below 30, sell above 70"

# Generate a grid trading strategy
python scripts/strategy_generator.py "BTC grid trading 50000-60000 10 grids 0.01 BTC per grid"

# Generate a signal-following strategy
python scripts/strategy_generator.py "ETH trading strategy based on VibeTrading signals, buy on bullish signals, sell on bearish signals"
```

### Output Structure

The generator creates:
1. **Strategy Python file** - Complete trading strategy class
2. **Configuration file** - Strategy parameters and settings
3. **Usage instructions** - How to run and monitor the strategy
4. **Requirements file** - Python dependencies

## Code Validation System

### Automatic Code Validation

All generated code is automatically validated and fixed using the built-in validation system:

```bash
# Validate generated code
python scripts/code_validator.py generated_strategy.py

# Validate and fix automatically
python scripts/code_validator.py generated_strategy.py --fix

# Validate entire directory
python scripts/code_validator.py strategy_directory/
```

### Validation Steps

The validation system performs these checks:

1. **Syntax Validation** - Python syntax checking
2. **Import Validation** - Module import verification
3. **Compatibility Checks** - Python 3.5+ compatibility
4. **Common Issue Detection** - Missing imports, encoding issues, etc.

### Automatic Fixes

When validation fails, the system automatically fixes common issues:

1. **Add missing imports** - Add typing imports if type annotations are used
2. **Fix encoding declaration** - Add `# -*- coding: utf-8 -*-` if missing
3. **Remove incompatible syntax** - Remove f-strings and type annotations for Python 3.5 compatibility
4. **Fix import paths** - Add sys.path modifications for API wrappers
5. **Fix logger initialization order** - Ensure logger is initialized before API client
6. **Remove pathlib usage** - Replace with os.path for Python 3.4 compatibility
7. **Fix string formatting** - Convert f-strings to .format() method

### Validation Configuration

The validation system can be configured via command-line arguments:

```bash
# Basic validation
python scripts/code_validator.py strategy.py

# Validate and fix automatically
python scripts/code_validator.py strategy.py --fix

# Use specific Python executable
python scripts/code_validator.py strategy.py --python python3.6

# Validate directory with all files
python scripts/code_validator.py strategies/ --fix

# Maximum 5 fix iterations
python scripts/code_validator.py strategy.py --fix --max-iterations 5
```

### Validation Rules

The system enforces these rules for generated code:

1. **Python 3.5+ Compatibility**
   - No f-strings (use `.format()` or `%` formatting)
   - No type annotations (remove or use comments)
   - No pathlib (use `os.path` instead)
   - No typing module imports

2. **Code Quality**
   - Proper encoding declaration (`# -*- coding: utf-8 -*-`)
   - Logger initialized before API client
   - All imports are resolvable
   - No syntax errors

3. **Security**
   - API keys loaded from environment variables
   - No hardcoded credentials
   - Proper error handling for API calls

4. **Performance**
   - Reasonable check intervals (not too frequent)
   - Efficient data fetching
   - Proper resource cleanup

### Validation Workflow

```
User Prompt → Code Generation → Validation → Fixes → Final Code
                    ↓
              If validation fails
                    ↓
            Apply automatic fixes
                    ↓
          Re-validate until success
                    ↓
          Deliver validated code
```

### Validation Failure Handling

When validation fails, the system automatically updates the code with these steps:

1. **Error Analysis** - Identify the specific validation errors
2. **Fix Application** - Apply appropriate fixes based on error type
3. **Re-validation** - Validate again after fixes
4. **Iterative Repair** - Repeat until code is valid (max 3 iterations)
5. **Fallback Strategy** - If automatic fixes fail, provide detailed error report and manual fix instructions

### Automatic Fix Examples

#### Fix 1: Missing Imports
```python
# Before (error: NameError: name 'List' is not defined)
def calculate_prices(prices: List[float]) -> List[float]:

# After (automatic fix)
from typing import List, Dict, Optional
def calculate_prices(prices):
```

#### Fix 2: Encoding Issues
```python
# Before (error: SyntaxError: Non-ASCII character)
# Strategy description: Grid trading

# After (automatic fix)
# -*- coding: utf-8 -*-
# Strategy description: Grid trading
```

#### Fix 3: Python 3.5 Incompatibility
```python
# Before (error: SyntaxError in Python 3.5)
price = f"Current price: {current_price}"

# After (automatic fix)
price = "Current price: {}".format(current_price)
```

#### Fix 4: Import Path Issues
```python
# Before (error: ImportError: No module named 'hyperliquid_api')
from hyperliquid_api import HyperliquidClient

# After (automatic fix)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api_wrappers"))
from hyperliquid_api import HyperliquidClient
```

## Supported Strategy Types

### 1. Technical Indicator Strategies
- **RSI-based**: Oversold/overbought trading
- **MACD-based**: Trend following with MACD crossovers
- **Moving Average**: SMA/EMA cross strategies
- **Bollinger Bands**: Mean reversion strategies

### 2. Advanced Trading Strategies
- **Grid Trading**: Price range trading with multiple orders
- **Mean Reversion**: Statistical arbitrage strategies
- **Trend Following**: Momentum-based strategies
- **Arbitrage**: Spot-perp or cross-exchange arbitrage

### 3. Signal-Driven Strategies
- **VibeTrading Integration**: Follow AI-generated trading signals
- **News-based**: React to market news and sentiment
- **Whale Activity**: Track large wallet movements
- **Funding Rate**: Funding rate arbitrage strategies

## How It Works

### Step 1: Prompt Analysis
The generator analyzes your natural language prompt to identify:
- Trading symbol (BTC, ETH, SOL, etc.)
- Strategy type (grid, RSI, signal-based, etc.)
- Key parameters (price ranges, grid counts, indicator values)
- Risk management preferences

### Step 2: Template Selection
Based on the analysis, the system selects the most appropriate template from:
- `templates/grid_trading.py` - Grid trading strategy template

### Step 3: Code Generation
The generator:
1. Fills template parameters with your values
2. Adds proper error handling and logging
3. Includes configuration management
4. Generates complete runnable code

### Step 4: Code Validation
The generated code is automatically validated and fixed:
1. **Syntax checking** - Ensure valid Python syntax
2. **Import verification** - Check all imports are resolvable
3. **Compatibility testing** - Verify Python 3.5+ compatibility
4. **Automatic fixes** - Apply fixes for common issues
5. **Re-validation** - Validate again after fixes
6. **Error reporting** - If fixes fail, provide detailed error report

### Validation Failure Handling
If validation fails after automatic fixes:
1. **Error Analysis Report** - Detailed breakdown of remaining issues
2. **Manual Fix Instructions** - Step-by-step guidance for manual fixes
3. **Fallback Template** - Option to use a simpler, validated template
4. **Support Contact** - Instructions for getting help

### Step 5: Output Delivery
You receive validated, runnable code including:
1. **Validated Python strategy file** - Fully tested and fixed
2. **Configuration template** - Strategy parameters and settings
3. **Validation report** - Summary of validation results and fixes applied
4. **Usage instructions** - How to run and monitor the strategy
5. **Troubleshooting guide** - Common issues and solutions
6. **Risk warnings** - Important safety information

## API Integration

The generated code uses mature Hyperliquid API implementations that support:

### Trading Operations
- Spot trading (buy/sell with limit/market orders)
- Perpetual contracts (long/short with leverage)
- Order management (cancel, modify, query)
- Position management (reduce, hedge)

### Market Data
- Real-time prices and OHLCV data
- Funding rates and open interest
- Order book depth
- Historical data access

### Account Management
- Balance queries (spot and futures)
- Position tracking
- PNL calculation
- Risk metrics

## Template System

### Template Structure
Each template includes:
- **Strategy class** with initialization and main logic
- **Configuration section** for easy parameter tuning
- **Error handling** with comprehensive logging
- **Risk management** features
- **Monitoring loop** for continuous operation

### Available Templates

#### Grid Trading Template
- `grid_trading.py` - Grid trading within price ranges (Python 3.5+ compatible)
  - No f-strings
  - No type annotations
  - Proper encoding declaration
  - Logger initialized before API client

## Configuration Management

### Strategy Configuration
Generated strategies include configurable parameters:
```python
STRATEGY_CONFIG = {
    "symbol": "BTC",
    "timeframe": "1h",
    "parameters": {
        "rsi_period": 14,
        "oversold": 30,
        "overbought": 70
    },
    "risk_management": {
        "position_size": 0.01,
        "stop_loss": 0.05,
        "take_profit": 0.10,
        "max_drawdown": 0.20
    }
}
```

### Environment Setup
```bash
# Required environment variables
export HYPERLIQUID_API_KEY="your_api_key_here"
export HYPERLIQUID_ACCOUNT_ADDRESS="your_address_here"
export TELEGRAM_BOT_TOKEN="optional_for_alerts"
```

## Risk Management Features

All generated strategies include:

### 1. Position Sizing
- Fixed percentage of portfolio
- Dynamic position sizing based on volatility
- Maximum position limits

### 2. Stop Loss Mechanisms
- Percentage-based stop loss
- Trailing stops
- Time-based exits

### 3. Risk Controls
- Maximum daily loss limits
- Drawdown protection
- Correlation checks
- Market condition filters

### 4. Monitoring & Alerts
- Real-time position tracking
- Telegram/Slack notifications
- Performance reporting
- Error alerts and recovery

## Integration with VibeTrading Signals

Generated strategies can integrate with VibeTrading Global Signals:

```python
from vibetrading import get_latest_signals

# Get AI-generated signals
signals = get_latest_signals("BTC,ETH")

# Use signals in trading logic
if signals["BTC"]["sentiment"] == "BULLISH":
    strategy.execute_buy("BTC", amount=0.01)
```

## Usage Examples

### Example 1: Simple RSI Strategy
**Prompt**: "Generate a BTC RSI strategy, buy 0.01 BTC when RSI below 30, sell when above 70"

**Generated Code Features**:
- RSI calculation with 14-period default
- Configurable oversold/overbought thresholds
- Proper error handling for API calls
- Logging for all trading actions
- 1-hour check interval

### Example 2: Grid Trading Strategy
**Prompt**: "ETH grid trading strategy, price range 3000-4000, 20 grids, 0.1 ETH per grid"

**Generated Code Features**:
- Automatic grid price calculation
- Order placement and management
- Grid rebalancing logic
- Price monitoring and adjustment
- Comprehensive logging

### Example 3: Signal-Based Strategy
**Prompt**: "SOL trading strategy based on VibeTrading signals, buy on bullish signals, sell on bearish signals, 10 SOL per trade"

**Generated Code Features**:
- VibeTrading API integration
- Signal polling and parsing
- Trade execution based on sentiment
- Position management
- Performance tracking

## Best Practices

### 1. Start with Paper Trading
- Always test strategies in simulation mode first
- Use small position sizes initially
- Monitor performance for at least 1-2 weeks

### 2. Risk Management
- Never risk more than 1-2% per trade
- Use stop losses on all positions
- Diversify across multiple strategies
- Monitor correlation between strategies

### 3. Monitoring & Maintenance
- Regularly review strategy performance
- Adjust parameters based on market conditions
- Keep logs for audit and analysis
- Set up alerts for critical events

### 4. Security
- Store API keys securely (environment variables)
- Use separate accounts for different strategies
- Regularly rotate API keys
- Monitor for unauthorized access

## Troubleshooting

### Common Issues

#### 1. API Connection Errors
```bash
# Check API key and account address
echo $HYPERLIQUID_API_KEY
echo $HYPERLIQUID_ACCOUNT_ADDRESS

# Test API connection
python scripts/test_connection.py
```

#### 2. Strategy Not Executing Trades
- Check balance and available funds
- Verify symbol is correctly specified
- Check order size meets minimum requirements
- Review logs for error messages

#### 3. Performance Issues
- Adjust check intervals (too frequent may cause rate limiting)
- Optimize data fetching (cache where possible)
- Review market conditions (low liquidity periods)

#### 4. Integration Issues with VibeTrading
- Verify VibeTrading API is accessible
- Check signal availability for your symbols
- Review signal parsing logic

#### 5. Validation Errors
```bash
# Common validation errors and solutions:

# Error: "SyntaxError: invalid syntax"
# Solution: Check for f-strings or type annotations
python scripts/code_validator.py strategy.py --fix

# Error: "ImportError: No module named 'typing'"
# Solution: Remove typing imports (Python 3.4 compatibility)
sed -i '' 's/from typing import.*//g' strategy.py

# Error: "SyntaxError: Non-ASCII character"
# Solution: Add encoding declaration
echo -e '# -*- coding: utf-8 -*-\n' | cat - strategy.py > temp && mv temp strategy.py

# Error: "NameError: name 'List' is not defined"
# Solution: Remove type annotations or add typing import
sed -i '' 's/: List//g; s/: Dict//g; s/: Optional//g' strategy.py

# Manual validation check
python -m py_compile strategy.py
```

#### 6. Code Generation Failures
- Check prompt clarity (be specific about parameters)
- Ensure template exists for requested strategy type
- Verify Python version compatibility (3.5+ recommended)
- Check available disk space for output files

## Advanced Features

### Custom Template Creation
You can create custom templates in `templates/custom/`:

1. Create a new template file
2. Define template variables with `{{variable_name}}`
3. Add to template registry in `scripts/template_registry.py`
4. Test with the generator

### Strategy Backtesting
While this generator focuses on live trading, you can:
1. Export generated code to backtesting frameworks
2. Use historical data for strategy validation
3. Add performance metrics and analysis

### Multi-Strategy Management
For running multiple strategies:
1. Generate separate strategy files
2. Use different configuration files
3. Monitor overall portfolio risk
4. Implement strategy allocation logic

## Support & Updates

### Getting Help
- Review generated code comments
- Check example strategies in `examples/`
- Consult Hyperliquid API documentation
- Review VibeTrading signal documentation

### Updates
This skill will be updated with:
- New strategy templates
- Improved prompt understanding
- Additional risk management features
- Integration with more data sources

## Backtesting Integration

### Backtest Evaluation Feature

After generating a strategy, you can now evaluate its performance using our integrated backtesting system:

```bash
# Generate a strategy
python scripts/strategy_generator.py "BTC grid trading 50000-60000 10 grids 0.01 BTC per grid"

# Run backtest on the generated strategy
python scripts/backtest_runner.py generated_strategies/btc_grid_trading_strategy.py

# Run backtest with custom parameters
python scripts/backtest_runner.py generated_strategies/btc_grid_trading_strategy.py \
  --start-date 2025-01-01 \
  --end-date 2025-03-01 \
  --initial-balance 10000 \
  --interval 1h
```

### Backtest Features

The backtesting system provides:

1. **Historical Data Simulation** - Uses historical price data for realistic testing
2. **Performance Metrics** - Calculates key metrics:
   - Total Return (%)
   - Maximum Drawdown (%)
   - Sharpe Ratio
   - Win Rate (%)
   - Total Trades
   - Average Trade Duration

3. **Risk Analysis** - Evaluates strategy risk characteristics
4. **Visual Reports** - Generates charts and performance reports
5. **Comparative Analysis** - Compares strategy performance against benchmarks

### Backtest Configuration

You can configure backtests with these parameters:

```python
BACKTEST_CONFIG = {
    "start_date": "2025-01-01",
    "end_date": "2025-03-01",
    "initial_balance": 10000,  # USDC
    "interval": "1h",  # 1m, 5m, 15m, 30m, 1h, 4h, 1d
    "symbols": ["BTC", "ETH"],  # Trading symbols
    "commission_rate": 0.001,  # 0.1% trading commission
    "slippage": 0.001,  # 0.1% slippage
}
```

### Backtest Results Example

```
📊 Backtest Results for BTC Grid Trading Strategy
================================================
📅 Period: 2025-01-01 to 2025-03-01 (60 days)
💰 Initial Balance: $10,000.00
💰 Final Balance: $11,234.56

📈 Performance Metrics:
  • Total Return: +12.35%
  • Max Drawdown: -5.67%
  • Sharpe Ratio: 1.45
  • Win Rate: 58.3%
  • Total Trades: 120
  • Avg Trade Duration: 12.5 hours

📋 Trade Analysis:
  • Winning Trades: 70
  • Losing Trades: 50
  • Largest Win: +$245.67
  • Largest Loss: -$123.45
  • Avg Win: +$89.12
  • Avg Loss: -$56.78

⚠️ Risk Assessment:
  • Risk-Adjusted Return: Good
  • Drawdown Control: Acceptable
  • Consistency: Moderate
```

### Backtest Integration in Generated Code

Generated strategies now include backtest compatibility:

```python
# Generated strategy includes backtest method
strategy = GridTradingStrategy(api_key, account_address, config)

# Run backtest
backtest_results = strategy.run_backtest(
    start_date="2025-01-01",
    end_date="2025-03-01",
    initial_balance=10000
)

# Generate backtest report
strategy.generate_backtest_report(backtest_results)
```

### Backtest Data Sources

The backtesting system uses:
- **Historical price data** from Hyperliquid API
- **Realistic order execution** with configurable slippage
- **Accurate commission modeling** based on exchange fees
- **Market impact simulation** for large orders

### Backtest Limitations

**Important Notes**:
1. **Past performance ≠ future results** - Historical success doesn't guarantee future profits
2. **Data quality** - Results depend on historical data accuracy
3. **Market conditions** - Past market conditions may differ from future
4. **Execution assumptions** - Assumes perfect order execution (configurable slippage)
5. **Liquidity assumptions** - Assumes sufficient market liquidity

**Best Practices**:
1. Always backtest with multiple time periods
2. Test different market conditions (bull, bear, sideways)
3. Use realistic commission and slippage settings
4. Start with small position sizes in live trading
5. Monitor strategy performance and adjust as needed

## Code Validation Disclaimer

**Validation Limitations**: While the code validation system automatically fixes common issues, it cannot guarantee:
1. **Trading logic correctness** - Validation checks syntax, not trading logic
2. **Financial performance** - No guarantee of profitability
3. **API compatibility** - Hyperliquid API changes may break generated code
4. **Security vulnerabilities** - Manual security review is recommended
5. **Edge case handling** - All possible error conditions may not be covered

**Validation Success Criteria**: Code is considered "valid" when:
1. No syntax errors
2. All imports are resolvable
3. Python 3.6+ compatible
4. Basic structure is correct

**Not Validated**:
- Trading logic accuracy
- Risk management effectiveness
- Financial calculations
- Market condition handling
- Performance optimization

## Quick Reference

### Python Version Requirements
```bash
# Check Python version
python scripts/check_python_version.py

# Minimum: Python 3.6+ (for f-string support)
```

### Basic Usage
```bash
# Generate strategy
python scripts/strategy_generator.py "BTC grid trading 50000-60000 10 grids"

# Run backtest
python scripts/backtest_runner.py generated_strategies/btc_grid_trading_strategy.py
```

### Key Features
1. **Python 3.6+ Compatibility** - Modern Python features including f-strings
2. **Automatic Backtest Integration** - Evaluate strategies before live trading
3. **Comprehensive Validation** - Syntax and compatibility checking
4. **Risk Management** - Built-in risk controls in all strategies

## Trading Disclaimer

**Important**: Trading cryptocurrencies involves significant risk. Generated strategies should be thoroughly tested before use with real funds. Past performance is not indicative of future results. Always use proper risk management and never trade with money you cannot afford to lose.

The code generator provides tools for strategy creation, but ultimate responsibility for trading decisions and risk management lies with the user.

**Validation is not a substitute for**:
1. **Thorough testing** - Always test in simulation first
2. **Code review** - Have experienced developers review generated code
3. **Security audit** - Check for vulnerabilities before deployment
4. **Performance testing** - Test under various market conditions
5. **Risk assessment** - Evaluate strategy risks independently

**Backtesting Limitations**:
1. **Historical data quality** - Results depend on data accuracy
2. **Market condition changes** - Past conditions may differ from future
3. **Execution assumptions** - Assumes perfect order execution
4. **Liquidity assumptions** - Assumes sufficient market liquidity
5. **No guarantee of future performance** - Past success ≠ future profits