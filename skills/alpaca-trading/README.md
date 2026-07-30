# 📈 Alpaca Trading Skill

> **Command-line trading made simple.** Execute trades, monitor positions, and manage your portfolio directly from your terminal using Alpaca's powerful API.

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Rust 1.71+](https://img.shields.io/badge/rust-1.71%2B-orange.svg)](https://www.rust-lang.org)
[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-green.svg)](https://clawhub.com)

---

## Why This Skill?

**For developers and traders who want:**
- ✅ **Speed**: Execute trades faster than clicking through a web interface
- ✅ **Automation**: Script your trading strategies with simple shell commands
- ✅ **Transparency**: See exactly what commands are being run
- ✅ **Control**: Manage everything from your terminal without context switching
- ✅ **Safety**: Test with paper trading before risking real money

**What makes this different:**
Unlike GUI-based trading platforms, `apcacli` gives you programmatic access to your Alpaca account through a clean, efficient command-line interface. Perfect for developers, algorithmic traders, and terminal enthusiasts.

---

## Quick Start (5 Minutes)

### Step 1: Install apcacli

`apcacli` is a Rust CLI — you'll need the Rust toolchain first.

**macOS (Homebrew):**
```bash
brew install rustup
rustup-init -y
source "$HOME/.cargo/env"
cargo install apcacli
```

**Linux:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
cargo install apcacli
```

**Windows:**
1. Download and run [rustup-init.exe](https://rustup.rs)
2. Open a new terminal, then run: `cargo install apcacli`

**Verify it works:**
```bash
apcacli --help
```

### Step 2: Get Your API Keys (Free)

1. **Sign up** at [Alpaca Markets](https://alpaca.markets/) (free account)
2. **Navigate** to your dashboard
3. **Generate** paper trading API keys (no credit card required)
4. **Copy** your `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY`

### Step 3: Configure Environment

```bash
# For Paper Trading (start here - it's free and safe!)
export APCA_API_KEY_ID='your_paper_key_id'
export APCA_API_SECRET_KEY='your_paper_secret_key'

# Add to your shell profile for persistence
echo "export APCA_API_KEY_ID='your_paper_key_id'" >> ~/.zshrc
echo "export APCA_API_SECRET_KEY='your_paper_secret_key'" >> ~/.zshrc
```

### Step 4: Try Your First Command

```bash
# Check your account
apcacli account get

# See if the market is open
apcacli market clock

# You're ready to trade! 🎉
```

---

## What You Can Do

### 💰 Trading Operations
- Execute market, limit, stop, and trailing-stop orders
- Buy and sell stocks, ETFs, options, and crypto
- Cancel orders individually or in bulk
- Close positions partially or completely

### 📊 Portfolio Management
- View all open positions with real-time P/L
- Check account balance and buying power
- Track daily and total profit/loss (color-coded!)
- Review position history

### 📈 Market Data
- Get asset information and availability
- Check market clock and trading hours
- Search for symbols
- Access real-time quotes through Alpaca's API

### 🔔 Real-time Monitoring
- Stream account events (orders, fills, updates)
- Monitor trade executions live
- Track portfolio changes in real-time

### ⚡ Advanced Features
- Shell completion for faster command entry
- Scriptable automation for strategies
- Session management for multiple accounts
- Output formatting (JSON, colored text)

---

## Example Workflows

### Buy Your First Stock

```bash
# 1. Check your buying power
apcacli account get

# 2. Verify the market is open
apcacli market clock

# 3. Buy $1000 worth of AAPL at market price
apcacli order submit buy AAPL --value 1000

# 4. Confirm your position
apcacli position list
```

**What just happened?**
- You checked your account had funds available
- You verified the market was open (trades only execute during market hours)
- You submitted a market order for $1000 worth of Apple stock
- You confirmed the position appeared in your portfolio

### Set a Limit Order

```bash
# Buy 10 shares of Microsoft, but only if price drops to $420
apcacli order submit buy MSFT --quantity 10 --limit-price 420

# Check if your order is still open
apcacli order list

# Cancel it if you change your mind
apcacli order cancel <ORDER_ID>
```

**Why limit orders?**
Market orders execute immediately at current price (fast but unpredictable). Limit orders only execute at your specified price or better (slower but controlled).

### Protect Your Position with a Stop Loss

```bash
# You own 10 shares of AAPL and want to protect gains
# Set a trailing stop 5% below the current price
apcacli order submit sell AAPL --quantity 10 --trail-percent 5

# If AAPL drops 5% from its peak, your shares auto-sell
# But if it keeps rising, the stop price rises with it
```

**Risk management 101:**
Never hold a position without a stop loss. Trailing stops let you capture upside while limiting downside.

### Daily Portfolio Check

```bash
#!/bin/bash
# Save as ~/check-portfolio.sh

echo "📊 Daily Portfolio Report - $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "💰 Account Status"
apcacli account get
echo ""

echo "📈 Open Positions"
apcacli position list
echo ""

echo "📝 Recent Activity"
apcacli account activity | head -10
```

```bash
# Make it executable
chmod +x ~/check-portfolio.sh

# Run daily
~/check-portfolio.sh
```

---

## Command Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Account & Balance** |
| View account details | `apcacli account get` |
| Check account activity | `apcacli account activity` |
| **Market Data** |
| Check if market is open | `apcacli market clock` |
| Get asset info | `apcacli asset get SYMBOL` |
| Search for symbol | `apcacli asset search QUERY` |
| **Trading** |
| Buy with $ amount | `apcacli order submit buy SYMBOL --value AMOUNT` |
| Buy X shares at market | `apcacli order submit buy SYMBOL --quantity X` |
| Buy with limit price | `apcacli order submit buy SYMBOL --quantity X --limit-price PRICE` |
| Sell shares | `apcacli order submit sell SYMBOL --quantity X` |
| Set trailing stop | `apcacli order submit sell SYMBOL --quantity X --trail-percent 5` |
| **Order Management** |
| List all orders | `apcacli order list` |
| Get order details | `apcacli order get ORDER_ID` |
| Cancel an order | `apcacli order cancel ORDER_ID` |
| Cancel all orders | `apcacli order cancel-all` |
| **Portfolio** |
| List positions | `apcacli position list` |
| Get position details | `apcacli position get SYMBOL` |
| Close position | `apcacli position close SYMBOL` |
| Close all positions | `apcacli position close-all` |
| **Monitoring** |
| Stream account events | `apcacli stream account` |
| Stream trades | `apcacli stream trades` |

---

## Safety First ⚠️

**ALWAYS start with paper trading:**
- Paper trading uses fake money - perfect for learning
- You get $100,000 virtual cash to experiment with
- All features work exactly like live trading
- Zero risk, full learning

**Before going live:**
- [ ] Test all commands with paper trading
- [ ] Understand order types (market vs limit vs stop)
- [ ] Know the risks of trading
- [ ] Never invest money you can't afford to lose
- [ ] Set stop losses on every position
- [ ] Double-check symbols and quantities

**Security:**
- Never share your API keys
- Store keys in environment variables, never in code
- Use paper keys for testing, live keys only for real trading
- Verify `APCA_API_BASE_URL` is correct before trading

---

## Installation via ClawHub

```bash
# Install the skill
clawhub install alpaca-trading

# Install Rust (if not already installed)
# macOS: brew install rustup && rustup-init -y
# Linux: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Install the CLI tool
source "$HOME/.cargo/env"
cargo install apcacli

# Set up API keys
export APCA_API_KEY_ID='your_key'
export APCA_API_SECRET_KEY='your_secret'
```

**From source (GitHub):**
```bash
git clone https://github.com/lacymorrow/openclaw-alpaca-trading-skill.git
cp -r openclaw-alpaca-trading-skill ~/.agents/skills/alpaca-trading
```

---

## Requirements

| Requirement | Details | How to Get |
|-------------|---------|------------|
| **apcacli** | The CLI tool itself | `cargo install apcacli` |
| **Rust 1.71+** | Required to install apcacli | [rustup.rs](https://rustup.rs) |
| **Alpaca account** | Free paper or funded live | [alpaca.markets](https://alpaca.markets) |
| **API keys** | `APCA_API_KEY_ID` + `APCA_API_SECRET_KEY` | Generate in Alpaca dashboard |

---

## Troubleshooting

### "apcacli: command not found"
**Solution:** Install apcacli with `cargo install apcacli`. Make sure `~/.cargo/bin` is in your PATH.

### "Missing APCA_API_KEY_ID"
**Solution:** Export your environment variables:
```bash
export APCA_API_KEY_ID='your_key'
export APCA_API_SECRET_KEY='your_secret'
```

### Orders not executing
**Possible causes:**
- Market is closed (check `apcacli market clock`)
- Insufficient buying power (check `apcacli account get`)
- Invalid symbol (verify with `apcacli asset get SYMBOL`)
- Account restrictions

### How do I switch from paper to live?
```bash
# Paper (default - no URL needed)
export APCA_API_KEY_ID='pk_...'
export APCA_API_SECRET_KEY='sk_...'

# Live (set URL to production)
export APCA_API_BASE_URL='https://api.alpaca.markets'
export APCA_API_KEY_ID='LIVE_KEY'
export APCA_API_SECRET_KEY='LIVE_SECRET'
```

⚠️ **Double-check the URL!** Wrong URL = trading with wrong account.

---

## Learn More

### Resources
- **[apcacli Repository](https://github.com/d-e-s-o/apcacli)** - Full documentation and source code
- **[Alpaca Docs](https://docs.alpaca.markets/)** - Trading platform documentation
- **[API Reference](https://docs.alpaca.markets/reference/)** - Complete API specifications
- **[Paper Trading Dashboard](https://app.alpaca.markets/paper/dashboard/overview)** - Web interface for your paper account
- **[apca Rust Crate](https://github.com/d-e-s-o/apca)** - The underlying library powering apcacli

### Community & Support
- **apcacli issues:** [GitHub Issues](https://github.com/d-e-s-o/apcacli/issues)
- **Alpaca support:** support@alpaca.markets
- **Alpaca community:** [Alpaca Forum](https://forum.alpaca.markets/)

---

## About This Skill

**Skill Type:** CLI Tool Integration
**Tool:** apcacli (Rust-based Alpaca CLI)
**Created for:** [ClawHub](https://clawhub.com) / [OpenClaw](https://openclaw.ai)
**License:** GPL-3.0 (following apcacli's license)

**Credits:**
- `apcacli` created by [d-e-s-o](https://github.com/d-e-s-o)
- Built on the `apca` Rust crate for Alpaca API interactions
- Skill documentation by the OpenClaw community
- **Source:** https://github.com/lacymorrow/openclaw-alpaca-trading-skill
- **ClawHub:** https://clawhub.com

---

## Disclaimer

**This skill provides tools for trading financial instruments. Trading involves substantial risk of loss.**

- This skill is educational and informational only
- Not financial advice - do your own research
- Start with paper trading to learn risk-free
- Only trade with money you can afford to lose
- Understand the risks before trading real money

By using this skill, you acknowledge that trading decisions are your own responsibility.

---

**Ready to start?** Install apcacli and get your free paper trading account today! 🚀
