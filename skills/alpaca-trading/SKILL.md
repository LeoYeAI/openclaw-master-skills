---
name: alpaca-trading
description: Execute trades, analyze markets, and manage portfolios using apcacli command-line tool for Alpaca's Trading API. Use when the user wants to trade stocks, ETFs, options, crypto, check market data, view positions, manage orders, or analyze their portfolio. Also use when they mention "buy," "sell," "trade," "market data," "stock price," "portfolio," "account balance," or "alpaca trading."
metadata:
  openclaw:
    emoji: "📈"
    requires:
      bins: ["apcacli"]
      env: ["APCA_API_KEY_ID", "APCA_API_SECRET_KEY"]
    homepage: "https://github.com/d-e-s-o/apcacli"
    repository: "https://github.com/lacymorrow/openclaw-alpaca-trading-skill"
    install:
      - id: "brew-rustup"
        kind: "brew"
        formula: "rustup"
        bins: ["rustup"]
        label: "Install Rust toolchain (Homebrew)"
---

# Alpaca Trading Skill

Execute trades and manage portfolios through the `apcacli` command-line tool for Alpaca's Trading API.

## Installation

`apcacli` is a Rust CLI. Install it cross-platform:

### macOS (Homebrew)
```bash
brew install rustup
rustup-init -y
source "$HOME/.cargo/env"
cargo install apcacli
```

### Linux
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
cargo install apcacli
```

### Windows
1. Download and run [rustup-init.exe](https://rustup.rs)
2. Open a new terminal, then: `cargo install apcacli`

### Environment Variables
```bash
export APCA_API_KEY_ID='your-key-id'
export APCA_API_SECRET_KEY='your-secret-key'
# For live trading (default is paper):
# export APCA_API_BASE_URL='https://api.alpaca.markets'
```

## Overview

You are an expert in using `apcacli` for command-line stock trading. Your goal is to help users trade stocks, ETFs, options, and crypto efficiently through Alpaca's API while emphasizing safety and best practices.

## How to Use This Skill

When helping users with trading tasks:

1. **Safety First**: Always recommend paper trading for new users or when testing
2. **Verify Commands**: Show the exact command before executing trades
3. **Check Prerequisites**: Confirm market hours, account balance, and valid symbols
4. **Explain Order Types**: Help users choose the right order type for their needs
5. **Risk Management**: Suggest stop losses and position sizing

---

## What This Skill Does

`apcacli` is a Rust-based CLI for interacting with Alpaca's trading platform. It provides:
- **Trading**: Submit, modify, and cancel orders for stocks, ETFs, options, and crypto
- **Portfolio Management**: View positions, P/L, and account information
- **Market Data**: Access asset information and market clock status
- **Account Activity**: Track trading history and account changes
- **Real-time Streaming**: Monitor account and trade events

## When to Use This Skill

Use this skill when the user wants to:
- Execute trades (buy/sell stocks, ETFs, options, crypto)
- Check portfolio positions and performance
- View or manage orders (open, filled, cancelled)
- Get account balance and buying power
- Access market data and asset information
- Monitor account activity and events
- Check if the market is open
- Set up stop losses or trailing stops
- Automate trading workflows with scripts

**Common trigger phrases:**
- "Buy 10 shares of AAPL"
- "Show my open positions"
- "What's my account balance?"
- "List all my orders"
- "Cancel order [ID]"
- "Is the market open?"
- "Show my portfolio performance"
- "Set a stop loss on my position"
- "Close all my positions"

**When NOT to use this skill:**
- User wants GUI-based trading (direct them to web interface)
- User asks for financial advice (you provide tools, not recommendations)
- User wants to trade instruments not supported by Alpaca
- User doesn't have apcacli installed (help them install it first)

## Installation & Setup

### Install apcacli

```bash
# Using Cargo (Rust package manager)
cargo install apcacli

# Verify installation
apcacli --help
```

**Requirements:**
- Rust 1.71 or newer
- Alpaca account (paper or live trading)
- Alpaca API credentials

### Configure Environment Variables

**For Paper Trading (Recommended for testing):**
```bash
export APCA_API_KEY_ID='your_paper_key_id'
export APCA_API_SECRET_KEY='your_paper_secret_key'
# Paper trading is the default, no need to set APCA_API_BASE_URL
```

**For Live Trading:**
```bash
export APCA_API_BASE_URL='https://api.alpaca.markets'
export APCA_API_KEY_ID='your_live_key_id'
export APCA_API_SECRET_KEY='your_live_secret_key'
```

**Get API Credentials:**
1. Sign up at https://alpaca.markets/
2. Navigate to your dashboard
3. Generate API keys (paper or live)
4. Export the environment variables

## Core Commands

### Account Information

**View account details:**
```bash
apcacli account get
```
Shows account status, cash balance, buying power, equity, and margin information.

**View account activity:**
```bash
apcacli account activity
```
Displays recent account activity including trades, dividends, and transfers.

**Update account configuration:**
```bash
apcacli account config <options>
```
Modify account settings (use `--help` for available options).

### Order Management

**Submit a market order:**
```bash
# Buy with dollar amount
apcacli order submit buy AAPL --value 1000

# Buy specific quantity
apcacli order submit buy AAPL --quantity 10

# Sell shares
apcacli order submit sell TSLA --quantity 5
```

**Submit a limit order:**
```bash
# Buy at specific price
apcacli order submit buy MSFT --quantity 10 --limit-price 420

# Sell at specific price
apcacli order submit sell NVDA --quantity 20 --limit-price 850
```

**Submit advanced orders:**
```bash
# Stop order
apcacli order submit sell AAPL --quantity 10 --stop-price 180

# Stop-limit order
apcacli order submit sell TSLA --quantity 5 --stop-price 800 --limit-price 795

# Trailing stop order (percentage)
apcacli order submit sell NVDA --quantity 10 --trail-percent 5
```

**List all orders:**
```bash
apcacli order list
```
Shows all orders with their status (open, filled, cancelled, etc.).

**Get specific order details:**
```bash
apcacli order get <ORDER_ID>
```
Displays comprehensive order information including timestamps, pricing, and status.

**Cancel an order:**
```bash
apcacli order cancel <ORDER_ID>
```
Cancels a pending order by its ID.

**Cancel all orders:**
```bash
apcacli order cancel-all
```
Cancels all open orders.

### Position Management

**List all open positions:**
```bash
apcacli position list
```
Shows all open positions with:
- Quantity and entry price
- Current market value
- Daily P/L (with percentage)
- Total P/L (with percentage)
- Color-coded profit/loss

**Get specific position:**
```bash
apcacli position get <SYMBOL>
```
Displays detailed information for a specific position.

**Close a position:**
```bash
# Close entire position
apcacli position close <SYMBOL>

# Close partial position
apcacli position close <SYMBOL> --quantity 5
```

**Close all positions:**
```bash
apcacli position close-all
```
Closes all open positions.

### Asset Information

**List available assets:**
```bash
apcacli asset list
```
Shows all tradeable assets.

**Get asset details:**
```bash
apcacli asset get <SYMBOL>
```
Displays asset information including exchange, class, and tradability status.

**Search for assets:**
```bash
apcacli asset search <QUERY>
```
Searches for assets matching the query.

### Market Data

**Check market clock:**
```bash
apcacli market clock
```
Shows current market status (open/closed), next open time, and next close time.

### Streaming (Real-time Events)

**Stream account updates:**
```bash
apcacli stream account
```
Monitors real-time account events including order updates and fills.

**Stream trade updates:**
```bash
apcacli stream trades
```
Monitors real-time trade events for your positions.

## Best Practices

### Safety & Risk Management

1. **Start with Paper Trading** - Always test strategies with paper trading first
2. **Use Limit Orders** - Avoid market orders in volatile conditions for better price control
3. **Verify Symbols** - Double-check ticker symbols before executing trades
4. **Review Before Executing** - Use `apcacli order get` to verify order details
5. **Set Stop Losses** - Protect positions with stop orders
6. **Check Account Balance** - Ensure sufficient buying power before trading
7. **Monitor Positions** - Regularly review P/L with `apcacli position list`

### Effective Usage

1. **Check help for any command** - Use `apcacli <command> --help` for detailed options
2. **Save order IDs** - Store returned order IDs to track and manage orders later
3. **Use environment variables** - Keep credentials secure in environment variables, never hardcode
4. **Verify market hours** - Check `apcacli market clock` before placing orders
5. **Review activity regularly** - Monitor account activity for unexpected changes

### Common Workflows

**Simple stock purchase:**
```bash
# 1. Check account balance
apcacli account get

# 2. Verify asset is tradeable
apcacli asset get AAPL

# 3. Check market is open
apcacli market clock

# 4. Submit market order
apcacli order submit buy AAPL --value 1000

# 5. Verify position
apcacli position list
```

**Limit order with monitoring:**
```bash
# 1. Submit limit order
apcacli order submit buy MSFT --quantity 10 --limit-price 420

# 2. Save the returned ORDER_ID
# 3. Check order status
apcacli order get <ORDER_ID>

# 4. If needed, cancel
apcacli order cancel <ORDER_ID>
```

**Portfolio review:**
```bash
# 1. View all positions
apcacli position list

# 2. Check account summary
apcacli account get

# 3. Review recent activity
apcacli account activity
```

**Close position with stop loss:**
```bash
# 1. Check current position
apcacli position get AAPL

# 2. Set trailing stop to protect profits
apcacli order submit sell AAPL --quantity 10 --trail-percent 5

# 3. Monitor the order
apcacli order list
```

## Command Reference Quick Guide

| Task | Command |
|------|---------|
| View account | `apcacli account get` |
| Account activity | `apcacli account activity` |
| Buy stock (market) | `apcacli order submit buy SYMBOL --value AMOUNT` |
| Buy stock (limit) | `apcacli order submit buy SYMBOL --quantity N --limit-price PRICE` |
| Sell stock | `apcacli order submit sell SYMBOL --quantity N` |
| List all orders | `apcacli order list` |
| Get order details | `apcacli order get ORDER_ID` |
| Cancel order | `apcacli order cancel ORDER_ID` |
| Cancel all orders | `apcacli order cancel-all` |
| List positions | `apcacli position list` |
| Get position | `apcacli position get SYMBOL` |
| Close position | `apcacli position close SYMBOL` |
| Close all positions | `apcacli position close-all` |
| List assets | `apcacli asset list` |
| Get asset info | `apcacli asset get SYMBOL` |
| Check market status | `apcacli market clock` |
| Stream account events | `apcacli stream account` |
| Stream trades | `apcacli stream trades` |

## Order Types & Parameters

### Basic Order Parameters

- `--quantity N` - Number of shares to trade
- `--value AMOUNT` - Dollar amount to invest (for market orders)
- `--limit-price PRICE` - Limit price for limit orders
- `--stop-price PRICE` - Stop price for stop orders
- `--trail-percent N` - Trailing stop percentage
- `--trail-amount AMOUNT` - Trailing stop dollar amount

### Order Types

**Market Order** - Executes immediately at current market price
```bash
apcacli order submit buy AAPL --quantity 10
```

**Limit Order** - Executes only at specified price or better
```bash
apcacli order submit buy AAPL --quantity 10 --limit-price 185
```

**Stop Order** - Converts to market order when stop price is reached
```bash
apcacli order submit sell AAPL --quantity 10 --stop-price 180
```

**Stop-Limit Order** - Converts to limit order when stop price is reached
```bash
apcacli order submit sell AAPL --quantity 10 --stop-price 180 --limit-price 179
```

**Trailing Stop** - Stop price follows market by specified percentage or amount
```bash
# Percentage-based
apcacli order submit sell AAPL --quantity 10 --trail-percent 5

# Dollar-based
apcacli order submit sell AAPL --quantity 10 --trail-amount 10
```

## Important Notes

### Requirements

- **apcacli binary must be installed** - Install via `cargo install apcacli`
- **Environment variables must be set** - `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` are required
- **Alpaca account** - Active paper or live trading account
- **Rust 1.71+** - Required for installation from source

### Trading Limitations

- **Paper vs Live**: Default is paper trading; set `APCA_API_BASE_URL` for live trading
- **Market hours**: Most trades only execute during market hours (9:30 AM - 4:00 PM ET)
- **Pattern Day Trading (PDT)**: Accounts under $25k have PDT restrictions
- **Buying power**: Limited by account equity and margin requirements
- **Order restrictions**: Some order types may not be available for all securities
- **Crypto trading**: May have different rules and trading hours

### Data & Performance

- **API rate limits**: Alpaca has request limits to prevent abuse
- **Real-time data**: May require active data subscription
- **Command output**: Results formatted with color coding for easy reading
- **Order IDs**: Save returned order IDs for tracking and management
- **Network dependency**: Requires internet connection to Alpaca's API

## Troubleshooting

### Environment Variables Not Set
```bash
# Error: "Missing APCA_API_KEY_ID"
# Solution: Export required environment variables
export APCA_API_KEY_ID='your_key'
export APCA_API_SECRET_KEY='your_secret'
```

### Command Not Found
```bash
# Error: "apcacli: command not found"
# Solution: Install apcacli
cargo install apcacli

# Verify installation
which apcacli
```

### API Authentication Failed
- Verify API credentials are correct
- Check if using correct endpoint (paper vs live)
- Ensure API keys haven't been revoked
- Confirm account status is active

### Order Rejected
- Verify market is open (for stocks)
- Check sufficient buying power
- Confirm symbol is valid and tradeable
- Review order parameters (price, quantity)
- Check for any account restrictions

### Position Not Found
- Verify symbol is correct
- Ensure position is actually open
- Check if position was closed previously
- Confirm you're using the right account (paper vs live)

## Advanced Features

### Shell Completion

Generate shell completion for faster command entry:

```bash
# Install completion script
cargo run --bin=shell-complete > apcacli.bash
source apcacli.bash

# Now you can use tab completion
apcacli order <TAB>
```

### Streaming for Monitoring

Use streaming commands to monitor account activity in real-time:

```bash
# Terminal 1: Monitor account events
apcacli stream account

# Terminal 2: Execute trades
apcacli order submit buy AAPL --value 1000
# Watch the fill notification appear in Terminal 1
```

### Scripting & Automation

Combine `apcacli` with shell scripts for automated strategies:

```bash
#!/bin/bash
# Example: Daily portfolio check script

echo "=== Daily Portfolio Report ==="
echo ""
echo "Account Status:"
apcacli account get
echo ""
echo "Open Positions:"
apcacli position list
echo ""
echo "Recent Activity:"
apcacli account activity
```

## Additional Resources

- **apcacli Repository**: https://github.com/d-e-s-o/apcacli
- **Alpaca Documentation**: https://docs.alpaca.markets/
- **Alpaca API Reference**: https://docs.alpaca.markets/reference/
- **Paper Trading Dashboard**: https://app.alpaca.markets/paper/dashboard/overview
- **apca Crate (Underlying Library)**: https://github.com/d-e-s-o/apca

## Safety Reminders

⚠️ **IMPORTANT**:
- Always start with **PAPER TRADING** to test without risk
- Review all order details before execution
- Never share your API credentials
- Use limit orders for better price control
- Set stop losses to manage risk
- Verify environment variables are set correctly (paper vs live)
- Double-check symbols and quantities
- Monitor positions regularly

## Credits

`apcacli` created by d-e-s-o

Built on the `apca` Rust crate for Alpaca API interactions.
