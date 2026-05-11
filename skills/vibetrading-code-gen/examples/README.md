# VibeTrading Strategy Examples

This directory contains example trading strategies to help you understand different trading approaches.

## 📁 Directory Structure

```
examples/
├── README.md                    # This file
├── grid_trading_example.py      # Grid trading strategy example
├── rsi_strategy_example.py      # RSI mean reversion example
└── configs/                     # Example configurations
    ├── grid_config.json         # Grid trading configuration
    └── rsi_config.json          # RSI strategy configuration
```

## 🚀 Running Examples

### Grid Trading Example
```bash
cd /Users/bitinterfc/.openclaw/workspace/skills/vibetrading-code-gen
python examples/grid_trading_example.py
```

### RSI Strategy Example
```bash
cd /Users/bitinterfc/.openclaw/workspace/skills/vibetrading-code-gen
python examples/rsi_strategy_example.py
```

## 📚 Example Strategies

### 1. Grid Trading Strategy
**Concept**: Place multiple buy and sell orders at predefined price levels within a range.

**Key Features**:
- Multiple price levels (grids) within a range
- Buy low, sell high within the range
- Works best in sideways/consolidating markets
- Automated position management

**Use Case**: When you expect an asset to trade within a specific range for a period.

**Example Parameters**:
- Symbol: HYPE
- Price Range: $28.00 - $34.00
- Grid Count: 10 levels
- Grid Size: 10 HYPE per level

### 2. RSI Mean Reversion Strategy
**Concept**: Use Relative Strength Index (RSI) to identify overbought/oversold conditions.

**Key Features**:
- RSI calculation (0-100 scale)
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)
- Mean reversion principle

**Use Case**: When prices tend to revert to their mean/average.

**Example Parameters**:
- RSI Period: 14
- Oversold Threshold: 30
- Overbought Threshold: 70
- Position Size: 10 HYPE

## 🔧 Configuration Examples

### Grid Trading Configuration (`configs/grid_config.json`)
```json
{
  "lower_bound": 28.0,
  "upper_bound": 34.0,
  "grid_count": 10,
  "grid_size": 10
}
```

### RSI Strategy Configuration (`configs/rsi_config.json`)
```json
{
  "rsi_period": 14,
  "oversold_threshold": 30,
  "overbought_threshold": 70,
  "position_size": 10
}
```

## 💡 Learning Objectives

Each example demonstrates:

### Grid Trading
1. **Grid Calculation**: How to calculate evenly spaced price levels
2. **Signal Generation**: When to buy/sell at each grid level
3. **Position Management**: Tracking active positions
4. **Profit Calculation**: Calculating P&L for each trade
5. **Risk Management**: Position sizing and exit strategies

### RSI Strategy
1. **RSI Calculation**: Mathematical formula and implementation
2. **Signal Interpretation**: Understanding RSI values
3. **Trading Rules**: Entry and exit conditions
4. **Backtesting**: Simulating strategy performance
5. **Parameter Optimization**: Finding optimal RSI settings

## 🎯 How to Use These Examples

### 1. Study the Code
Read through the examples to understand:
- Trading logic implementation
- Configuration management
- Risk control mechanisms
- Performance tracking

### 2. Run Simulations
Execute the examples to see:
- Real-time trading decisions
- Position management in action
- Profit/loss calculations
- Strategy performance metrics

### 3. Modify Parameters
Experiment with:
- Different parameter values
- Alternative entry/exit conditions
- Additional risk controls
- New trading rules

### 4. Integrate with Real Data
Once comfortable:
- Replace simulated data with real market data
- Integrate with Hyperliquid API
- Add real order execution
- Implement live monitoring

## 📊 Strategy Comparison

| Aspect | Grid Trading | RSI Strategy |
|--------|--------------|--------------|
| **Best Market** | Sideways/Ranging | Ranging/Slightly Trending |
| **Key Concept** | Price range trading | Mean reversion |
| **Complexity** | Medium | Low-Medium |
| **Trade Frequency** | High | Medium |
| **Risk** | Moderate | Moderate |
| **Capital Required** | High (for multiple grids) | Medium |

## 🔄 Next Steps

1. **Understand the basics** by running both examples
2. **Experiment with parameters** to see how they affect performance
3. **Study the generated strategies** in `generated_strategies/` directory
4. **Create your own variations** based on these examples
5. **Integrate with the generator** to automate strategy creation

## ⚠️ Important Notes

- These are **educational examples** only
- Always test strategies thoroughly before live trading
- Past performance does not guarantee future results
- Cryptocurrency trading involves significant risk
- Start with small positions and paper trading

## 📞 Need Help?

- Review the main `SKILL.md` documentation
- Check generated strategies for real implementations
- Run examples with `--help` flag for usage instructions
- Modify examples to suit your trading style

---
*Examples last updated: 2026-02-13*