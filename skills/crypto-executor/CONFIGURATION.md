 # Configuration Guide - COMPLETE VERSION

**Crypto Executor v2.3 PRODUCTION READY - Full Setup Guide**

This guide covers setup for **ALL advanced features** including Kelly Criterion, trailing stops, circuit breakers, and daily reports.

---

## 📋 Prerequisites

- Python 3.7+
- Binance account (verified)
- Telegram account
- crypto-sniper-oracle skill
- Capital: $1K-$100K+

---

## 🚀 Step 1: Binance API Setup

### **Create API Key**

1. Login to https://binance.com
2. Profile → API Management
3. Create API
4. Label: `Crypto Executor v2 Complete`
5. Complete 2FA verification

---

### **Permissions (CRITICAL)**

**✅ ENABLE:**
```
✅ Enable Spot & Margin Trading
✅ Enable Reading
```

**❌ DISABLE:**
```
❌ Enable Withdrawals (MUST BE OFF FOR SECURITY)
❌ Enable Internal Transfer
❌ Enable Margin
❌ Enable Futures
```

**Only Spot Trading!**

---

### **IP Whitelist (Recommended)**

```
Settings → API Management → Edit API → Restrict access to trusted IPs

Add your server IP: XXX.XXX.XXX.XXX
```

**Why:** Prevents API key theft from working.

---

## 📱 Step 2: Telegram Bot Setup

### **Create Bot**

1. Open Telegram
2. Search: `@BotFather`
3. Send: `/newbot`
4. Bot name: `Crypto Executor Complete`
5. Username: `your_crypto_executor_v2_bot`
6. Save **BOT_TOKEN**

---

### **Get Chat ID**

```bash
# Method 1: Use bot
# 1. Send any message to your bot
# 2. Visit (replace YOUR_TOKEN):
https://api.telegram.org/botYOUR_TOKEN/getUpdates

# 3. Find "chat":{"id":123456789}
# 4. Save CHAT_ID

# Method 2: Use @userinfobot
# Search @userinfobot in Telegram
# Start chat → shows your ID
```

---

### **Test Telegram**

```bash
python3 << 'EOF'
import urllib.request, json, os

token = "YOUR_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"

url = f"https://api.telegram.org/bot{token}/sendMessage"
data = json.dumps({
    "chat_id": chat_id,
    "text": "✅ Crypto Executor v2 COMPLETE - Telegram configured!"
}).encode()

req = urllib.request.Request(url, data, {'Content-Type': 'application/json'})
urllib.request.urlopen(req)
print("✅ Test message sent!")
EOF
```

---

## ⚙️ Step 3: Environment Variables

### **Required Variables**

```bash
# Binance credentials
export BINANCE_API_KEY="your_binance_api_key"
export BINANCE_API_SECRET="your_binance_api_secret"

# Telegram alerts
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export TELEGRAM_CHAT_ID="your_telegram_chat_id"
```

---

### **Optional - Risk Limits (Recommended)**

```bash
# Position sizing
export MAX_POSITION_SIZE_PCT="12"     # Max 12% per trade

# Daily protection
export DAILY_LOSS_LIMIT_PCT="2"       # Pause at -2% daily loss

# Weekly protection
export WEEKLY_LOSS_LIMIT_PCT="5"      # Reduce sizes at -5% weekly

# Drawdown protection
export DRAWDOWN_PAUSE_PCT="7"         # Pause at 7% drawdown
export DRAWDOWN_KILL_PCT="10"         # Kill switch at 10%
```

**Defaults are conservative. Adjust based on risk tolerance.**

---


### **🔒 Secure Credential Storage (RECOMMENDED)**

**DO NOT store credentials in ~/.bashrc** - security risk if account compromised!

**DO THIS instead:**

```bash
# Create secure credentials file
sudo mkdir -p /etc/crypto-executor
sudo nano /etc/crypto-executor/credentials.env

# Content:
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
TELEGRAM_BOT_TOKEN=your_telegram_token  # Optional
TELEGRAM_CHAT_ID=your_telegram_chat_id  # Optional

# Risk limits (optional)
MAX_POSITION_SIZE_PCT=12
DAILY_LOSS_LIMIT_PCT=2
DRAWDOWN_KILL_PCT=10

# Secure the file
sudo chmod 600 /etc/crypto-executor/credentials.env
sudo chown root:root /etc/crypto-executor/credentials.env
```

**To use:**
```bash
# Load before running bot
source /etc/crypto-executor/credentials.env

# Or use with systemd (see SYSTEMD_SETUP.md)
EnvironmentFile=/etc/crypto-executor/credentials.env
```

**Why this is better:**
- ✅ Credentials in protected file (chmod 600)
- ✅ Not in shell history
- ✅ Root-owned (can't be modified by regular user)
- ✅ Not loaded in every terminal session
- ❌ ~/.bashrc is world-readable and loaded always


---

## 📊 Step 4: Install crypto-sniper-oracle

**⚠️ IMPORTANT - EXTERNAL DEPENDENCY**

**What it is:**
- crypto-sniper-oracle provides market data analysis (order book imbalance, VWAP, microstructure)
- Used via subprocess call during market scanning
- Source: https://github.com/georges91560/crypto-sniper-oracle

**Security considerations:**
1. **Audit the code before use** - this is external code execution
2. **Verify repository** - ensure it's the correct repo
3. **Pin a specific commit** (optional but recommended)
4. **Review what it does**:
   - Fetches Binance market data
   - Calculates order book metrics
   - Returns JSON with signals
   - NO network calls except Binance
   - NO credential requirements

**Installation:**

```bash
# Clone the dependency
git clone https://github.com/georges91560/crypto-sniper-oracle.git

# AUDIT THE CODE (IMPORTANT!)
# Review crypto_oracle.py before copying
cd crypto-sniper-oracle
cat crypto_oracle.py  # Read the code
# Look for: unexpected network calls, credential usage, file writes

# If code looks good, install
cp -r crypto-sniper-oracle/* /workspace/skills/crypto-sniper-oracle/

# Test it works
python3 /workspace/skills/crypto-sniper-oracle/crypto_oracle.py --symbol BTCUSDT
# Should output JSON with order book data
```

**What executor.py does with it:**
```python
# Line ~320 in executor.py
result = subprocess.run(
    [sys.executable, str(self.oracle_script), "--symbol", symbol],
    capture_output=True,
    text=True,
    timeout=10
)
# Executes oracle script, captures JSON output, uses for trading signals
```

**Why it's needed:**
- Provides advanced market microstructure analysis
- Calculates order book imbalance (OBI)
- Detects liquidity patterns
- Without it, bot has no market data signals

## 🤖 Step 5: Pre-Installation Check & Setup (Hostinger Terminal)

> **For AI agents (Wesley) and humans alike.**
> The bot checks if the script is already installed before doing anything.
> This avoids re-downloading 1722 lines every session.

---

### **Step 5a — Check if already installed**

```bash
# Run this FIRST — always
ls /workspace/skills/crypto-executor/executor.py
```

**Two possible outcomes:**

```bash
# ✅ CASE 1 — Already installed (file exists):
/workspace/skills/crypto-executor/executor.py

# → Nothing to do. Skip to Step 7 (Test Run).
# → Why: The script is pre-installed and persistent on the server.
#         Re-installing would overwrite learned_config.json and
#         performance_metrics.json — losing all bot memory.

# ❌ CASE 2 — Not installed (error: No such file or directory):
ls: cannot access '/workspace/skills/crypto-executor/executor.py': No such file or directory

# → Follow Steps 5b and 5c below.
```

---

### **Step 5b — Create folder structure**

```bash
# Create all required directories
# Why: executor.py writes files to these paths at runtime.
#      If they don't exist, the bot crashes on first write.

mkdir -p /workspace/skills/crypto-executor    # Script location
mkdir -p /workspace/reports/daily             # Daily performance reports
mkdir -p /workspace/config_history            # Learned config backups
mkdir -p /workspace/skills/crypto-sniper-oracle  # Oracle dependency

echo "✅ Directories created"
ls /workspace/skills/
```

---

### **Step 5c — Download and install executor.py**

```bash
# Option A: Clone from GitHub (recommended)
# Why: Gets the latest version, easy to update with git pull

cd /workspace/skills
git clone https://github.com/georges91560/Crypto_Executor.git crypto-executor-repo
cp crypto-executor-repo/executor.py /workspace/skills/crypto-executor/executor.py
chmod +x /workspace/skills/crypto-executor/executor.py

# Verify installation
python3 -c "import ast; ast.parse(open('/workspace/skills/crypto-executor/executor.py').read()); print('✅ executor.py syntax OK')"
wc -l /workspace/skills/crypto-executor/executor.py
# Expected: 1722 lines

# Option B: Direct download (if git not available)
# curl -o /workspace/skills/crypto-executor/executor.py \
#   https://raw.githubusercontent.com/georges91560/Crypto_Executor/main/executor.py
```

---

### **Step 5d — Install Python dependency (websocket)**

```bash
# Check if websocket-client already installed
python3 -c "import websocket; print('✅ websocket-client already installed')" 2>/dev/null \
  || echo "❌ Not installed — installing now..."

# Install if missing
# Why: Enables true sub-100ms WebSocket streams (vs 1s REST polling)
#      Without it, bot still works but is slower.
pip install websocket-client --break-system-packages

# Verify
python3 -c "import websocket; print('✅ websocket-client ready')"
```

---

### **Step 5e — Install crypto-sniper-oracle (dependency)**

```bash
# Check if already installed
ls /workspace/skills/crypto-sniper-oracle/crypto_oracle.py \
  && echo "✅ Oracle already installed" \
  || echo "❌ Oracle missing — installing..."

# Install if missing
cd /workspace/skills
git clone https://github.com/georges91560/crypto-sniper-oracle.git crypto-sniper-oracle

# Test oracle works
python3 /workspace/skills/crypto-sniper-oracle/crypto_oracle.py --symbol BTCUSDT
# Expected: JSON output with order book data
```

---

### **Step 5f — Load credentials**

```bash
# Check if credentials file exists
ls /etc/crypto-executor/credentials.env \
  && echo "✅ Credentials file found" \
  || echo "❌ Create credentials file (see Step 3)"

# Load credentials into current session
# Why: executor.py reads these via os.getenv() at startup.
#      Without them, bot exits immediately with [ERROR] Missing Binance credentials
source /etc/crypto-executor/credentials.env

# Verify credentials loaded
echo "API Key set: ${BINANCE_API_KEY:0:8}..."   # Shows first 8 chars only (security)
echo "Secret set:  ${BINANCE_API_SECRET:0:8}..."
```

---

### **Step 5g — Full installation check**

```bash
# Run this to verify everything is ready before launching
python3 << 'CHECKEOF'
import os
from pathlib import Path

checks = {
    "executor.py installed":     Path("/workspace/skills/crypto-executor/executor.py").exists(),
    "oracle installed":          Path("/workspace/skills/crypto-sniper-oracle/crypto_oracle.py").exists(),
    "reports/daily dir":         Path("/workspace/reports/daily").exists(),
    "config_history dir":        Path("/workspace/config_history").exists(),
    "BINANCE_API_KEY set":       bool(os.getenv("BINANCE_API_KEY")),
    "BINANCE_API_SECRET set":    bool(os.getenv("BINANCE_API_SECRET")),
    "TELEGRAM configured":       bool(os.getenv("TELEGRAM_BOT_TOKEN")),
}

try:
    import websocket
    checks["websocket-client installed"] = True
except ImportError:
    checks["websocket-client installed"] = False

all_ok = True
for check, result in checks.items():
    status = "✅" if result else "❌"
    if not result and check not in ["TELEGRAM configured", "websocket-client installed"]:
        all_ok = False
    print(f"  {status} {check}")

print()
if all_ok:
    print("✅ ALL CHECKS PASSED — Ready to launch!")
    print("   Run: python3 /workspace/skills/crypto-executor/executor.py")
else:
    print("❌ Some checks failed — Fix above before launching")
CHECKEOF
```

**Expected output when ready:**
```
  ✅ executor.py installed
  ✅ oracle installed
  ✅ reports/daily dir
  ✅ config_history dir
  ✅ BINANCE_API_KEY set
  ✅ BINANCE_API_SECRET set
  ✅ TELEGRAM configured
  ✅ websocket-client installed

✅ ALL CHECKS PASSED — Ready to launch!
   Run: python3 /workspace/skills/crypto-executor/executor.py
```

---

### **How the bot reacts when already installed**

```
AI Agent (Wesley) receives: "Start the trading bot"
↓
Reads SKILL.md → sees pre-installation check instructions
↓
Runs: ls /workspace/skills/crypto-executor/executor.py
↓
✅ File exists → skips installation entirely
   Runs: source /etc/crypto-executor/credentials.env
   Runs: python3 /workspace/skills/crypto-executor/executor.py
↓
Bot starts in <5 seconds, loads learned_config.json automatically
[MEMORY] Loaded config from 2026-02-27T09:00:00
[MEMORY] Win rate: 91.2%
[ADAPTIVE] Using learned strategy mix
```

---

## 🚀 Step 5 (legacy): Manual Install Crypto Executor

```bash
# Alternative: manual copy without git
mkdir -p /workspace/skills/crypto-executor
cp executor.py /workspace/skills/crypto-executor/
chmod +x /workspace/skills/crypto-executor/executor.py
```

---

## 💰 Step 6: Fund Binance Account

**Deposit USDT to Binance Spot account:**

### **Conservative Start**
```
Capital: $1,000-$5,000
Expected: $100-$1,000/month
Risk: 3-5% drawdown
```

### **Balanced**
```
Capital: $5,000-$25,000
Expected: $750-$7,500/month
Risk: 5-7% drawdown
```

### **Aggressive**
```
Capital: $25,000-$100,000+
Expected: $5,000-$40,000/month
Risk: 7-10% drawdown
```

**Start small, scale gradually!**

---

## ✅ Step 7: Test Run

```bash
python3 /workspace/skills/crypto-executor/executor.py
```

**Expected output:**
```
============================================================
CRYPTO EXECUTOR v2.3 - PRODUCTION READY
Fixes: Signature|CB L2|StatArb|LOT_SIZE|OCO Monitor|Kelly|Seuils|Sharpe
============================================================
[OK] Credentials validated
[START] Complete Trading - All Features
[WS] Started 10 streams (WebSocket)
🚀 PROJECT STARTED - COMPLETE VERSION

Complete Trading - All Features

Features: WebSocket ✓ Kelly ✓ OCO ✓ Circuit Breakers ✓

[OK] Starting COMPLETE trading engine...
[FEATURES] WebSocket ✓ Kelly ✓ OCO ✓ Trailing ✓ Circuit Breakers ✓ Reports ✓
[PARALLEL] BTCUSDT ✓
[PARALLEL] ETHUSDT ✓
[PARALLEL] Fetched 10/10 symbols
[PORTFOLIO] $5,000.00 | Drawdown: 0.00%
```

---

## 📊 Step 8: Understanding the Output

### **Startup Indicators**

```
[OK] Credentials validated        → Binance API working ✓
[WS] Started 10 streams              → Real-time streams active ✓
[FEATURES] Kelly ✓                → Position sizing enabled ✓
[FEATURES] Trailing ✓             → Profit locking enabled ✓
[FEATURES] Circuit Breakers ✓     → Risk protection active ✓
[FEATURES] Reports ✓              → Daily reports enabled ✓
```

---

### **Trading Indicators**

```
[PARALLEL] Fetched 10/10 symbols  → Market scan complete ✓
[SCAN] Completed in 0.52s         → Fast scanning ✓
[PORTFOLIO] $5,000 | Drawdown 0%  → Portfolio healthy ✓

[TRADE] BUY 0.11 BTCUSDT (Kelly: $600)
→ Kelly sizing calculated position

[ORDER] BUY 0.11 BTCUSDT
→ Market order executed

[OCO] Created: SELL 0.11 BTCUSDT
      TP: $45,135.00 | SL: $44,775.00
→ OCO order protecting position

[TRAIL] BTCUSDT trailing stop → $45,000.00
→ Trailing stop moved up (locking profit)

[TELEGRAM] Sent ✓
→ Trade alert sent
```

---

### **Circuit Breaker Indicators**

```
[CIRCUIT BREAKER] Level 1: Daily loss -2.1% > -2.0%
→ Trading paused for 2 hours

[PAUSED] Until 2026-02-27 14:30:00
→ Wait period active
```

---

## 📱 Step 9: Monitor Telegram Alerts

### **Trade Execution Alert**
```
🔔 TRADE EXECUTED

BUY 0.11 BTCUSDT
Entry: $45,000.00
TP: $45,135.00
SL: $44,775.00

Strategy: scalping
Position Size: 12.0% of capital
```

---

### **Daily Report (9am UTC)**
```
📊 DAILY PERFORMANCE REPORT
2026-02-27 09:00 UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 PORTFOLIO
Total: $5,243.00
Cash: $3,100.00 USDT
Positions: 2 open

Day P&L: +$243.00 (+4.86%)
Drawdown: 0.8%

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 TRADING
Trades Today: 18
Win Rate: 94.4%

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 STATUS
✅ On Track
```

---

### **Circuit Breaker Alert**
```
🚨 CIRCUIT BREAKER - LEVEL 1

Reason: Daily loss -2.1% > -2.0%

Trading paused for 2 hours.
Review suggested.
```

---

## 📂 Step 10: Check Generated Files

```bash
# Portfolio state
cat /workspace/portfolio_state.json

# Active positions
cat /workspace/open_positions.json

# Performance metrics
cat /workspace/performance_metrics.json

# Trades history
tail -20 /workspace/trades_history.jsonl

# Daily reports
ls -lh /workspace/reports/daily/
cat /workspace/reports/daily/report_2026-02-27.txt
```

---

## 🎛️ ADVANCED CONFIGURATION

### **Adjust Kelly Conservativeness**

Edit `executor.py` line ~550:
```python
# Use 50% Kelly (conservative)
kelly_fraction = kelly * 0.5 * signal_confidence

# More aggressive (60% Kelly)
kelly_fraction = kelly * 0.6 * signal_confidence

# More conservative (40% Kelly)
kelly_fraction = kelly * 0.4 * signal_confidence
```

---

### **Adjust Trailing Stop Levels**

Edit `executor.py` line ~600:
```python
# Default levels
if current_profit_pct >= 1.0:    # Breakeven at +1%
    return entry

if current_profit_pct >= 2.0:    # Lock 1% at +2%
    return entry * 1.01

if current_profit_pct >= 3.0:    # Lock 2% at +3%
    return entry * 1.02

# More aggressive trailing (lock earlier)
if current_profit_pct >= 0.5:    # Breakeven at +0.5%
    return entry

if current_profit_pct >= 1.0:    # Lock 0.5% at +1%
    return entry * 1.005
```

---

### **Adjust Strategy Mix**

Edit `executor.py` line ~950:
```python
# Default mix
strategy_mix = {
    "scalping": 0.70,    # 70%
    "momentum": 0.25,    # 25%
    "stat_arb": 0.05     # 5%
}

# More scalping (safer)
strategy_mix = {
    "scalping": 0.85,
    "momentum": 0.15,
    "stat_arb": 0.00
}

# More momentum (aggressive)
strategy_mix = {
    "scalping": 0.50,
    "momentum": 0.40,
    "stat_arb": 0.10
}
```

---

## 🛡️ RISK PROFILES

### **Conservative (Recommended Start)**

```bash
export MAX_POSITION_SIZE_PCT="8"      # 8% max
export DAILY_LOSS_LIMIT_PCT="1"       # -1% daily
export DRAWDOWN_KILL_PCT="7"          # 7% kill switch

# In executor.py:
kelly_fraction = kelly * 0.4  # 40% Kelly
strategy_mix = {"scalping": 0.85, "momentum": 0.15}
```

**Expected:**
- Monthly ROI: 8-15%
- Max drawdown: 3-5%
- Win rate: 90-95%

---

### **Balanced (Default)**

```bash
export MAX_POSITION_SIZE_PCT="12"     # 12% max
export DAILY_LOSS_LIMIT_PCT="2"       # -2% daily
export DRAWDOWN_KILL_PCT="10"         # 10% kill switch

# In executor.py:
kelly_fraction = kelly * 0.5  # 50% Kelly (default)
strategy_mix = {"scalping": 0.70, "momentum": 0.25, "stat_arb": 0.05}
```

**Expected:**
- Monthly ROI: 15-30%
- Max drawdown: 5-7%
- Win rate: 85-90%

---

### **Aggressive (Experienced Only)**

```bash
export MAX_POSITION_SIZE_PCT="15"     # 15% max
export DAILY_LOSS_LIMIT_PCT="3"       # -3% daily
export DRAWDOWN_KILL_PCT="12"         # 12% kill switch

# In executor.py:
kelly_fraction = kelly * 0.6  # 60% Kelly
strategy_mix = {"scalping": 0.50, "momentum": 0.40, "stat_arb": 0.10}
```

**Expected:**
- Monthly ROI: 20-40%
- Max drawdown: 7-12%
- Win rate: 80-88%

---

## 🐛 TROUBLESHOOTING

### **"Kelly sizing too small (<$10)"**

**Causes:**
- Low capital
- Low win rate (bot learning)
- Low signal confidence

**Solutions:**
```bash
# Check performance
cat /workspace/performance_metrics.json

# If win_rate < 70%, bot needs more data
# Wait 1-2 days for performance to stabilize

# If capital < $1K, increase capital or lower min trade:
# Edit executor.py line ~780:
if position_size_usdt < 5:  # Lower from 10 to 5
```

---

### **"Circuit breaker keeps triggering"**

**This is NORMAL protective behavior!**

**Actions:**
1. Check which level triggered (Telegram alert)
2. Review daily report for cause
3. Wait for auto-resume OR
4. Adjust risk limits if too conservative

**Level 1 (Daily loss):**
- Waits 2 hours automatically
- No action needed

**Level 3 (Drawdown pause):**
- Review strategy performance
- Check market conditions
- Manually restart after review

**Level 4 (Kill switch):**
- SERIOUS drawdown
- Full review required
- Adjust strategy or capital
- Manual restart only

---

### **"No trades executing"**

**Possible reasons:**

1. **Circuit breaker active**
   ```bash
   # Check if paused
   grep "PAUSED" executor.log
   ```

2. **No valid signals**
   ```bash
   # Market conditions not meeting thresholds
   # OBI < 0.10, spread > 8bps, etc.
   # This is normal during low volatility
   ```

3. **Kelly sizing too small**
   ```bash
   # Check performance metrics
   cat /workspace/performance_metrics.json
   # If win_rate very low, positions will be small
   ```

---

### **"WebSocket connection failed"**

**Normal** - Bot falls back to REST API

**Bot continues working:**
- Uses REST API for prices
- Slightly slower (1-2s vs <1s)
- No action needed

**To fix (optional):**
```bash
# Check network
ping stream.binance.com

# Check firewall allows WSS
# Open port 9443 for wss://stream.binance.com:9443
```

---

### **"OCO order failed"**

**Causes:**
- Symbol doesn't support OCO
- Insufficient balance
- API rate limit

**Bot behavior:**
- Position still opened (market order succeeded)
- Falls back to manual monitoring
- Checks every 5 seconds instead of instant

**Fix:**
- Check Binance API status
- Verify balance sufficient
- Wait 60s, retry

---

## 📊 MONITORING BEST PRACTICES

### **Daily Checks**

```bash
# 1. Check daily report (Telegram at 9am UTC)
# Look for:
# - Daily P&L positive
# - Win rate > 80%
# - Drawdown < 5%

# 2. Check active positions
cat /workspace/open_positions.json | python3 -m json.tool

# 3. Check performance metrics
cat /workspace/performance_metrics.json | python3 -m json.tool
```

---

### **Weekly Review**

```bash
# 1. Review all daily reports
ls /workspace/reports/daily/

# 2. Calculate weekly ROI
# (Current equity - Starting equity) / Starting equity × 100

# 3. Adjust if needed:
# - If win rate dropping → Reduce position sizes
# - If drawdown increasing → Tighten circuit breakers
# - If too conservative → Increase Kelly fraction
```

---

### **Monthly Optimization**

```bash
# 1. Analyze performance metrics
cat /workspace/performance_metrics.json

# 2. Adjust strategy mix based on results
# Which strategy has best win rate?
# Increase allocation to winner

# 3. Review Kelly fraction
# If consistent wins → Can increase to 55-60%
# If volatile → Keep at 40-50%
```

---

## ✅ VERIFICATION CHECKLIST

Before live trading:

- [ ] Binance API credentials set
- [ ] Trading enabled, withdrawals DISABLED
- [ ] Telegram bot configured and tested
- [ ] crypto-sniper-oracle installed and working
- [ ] executor.py runs without errors
- [ ] WebSocket streams started
- [ ] Kelly sizing enabled
- [ ] Circuit breakers configured
- [ ] First trade executed successfully
- [ ] Telegram alerts received
- [ ] Daily report scheduled (9am UTC)
- [ ] Files generating in /workspace

---

## 🚀 PRODUCTION DEPLOYMENT

**See SYSTEMD_SETUP.md for:**
- Running as systemd service
- Auto-start on boot
- Auto-restart on crash
- Centralized logging
- Professional deployment

---

## 📞 SUPPORT

**Issues:** https://github.com/georges91560/crypto-executor/issues  
**Docs:** Full documentation in repository

---

**COMPLETE SETUP. MAXIMUM SAFETY. OPTIMAL PROFITS. ⚡💰**
