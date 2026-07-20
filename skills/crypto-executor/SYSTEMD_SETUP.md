# Systemd Setup for Crypto Executor v2.3 - PRODUCTION READY

**Run crypto-executor as a professional systemd service**

Auto-start on boot · Auto-restart on crash · Centralized logs · Easy control

---

## 🎯 Why Use Systemd?

**systemd makes your trading bot run like a professional service:**

✅ **Auto-starts** when server boots  
✅ **Auto-restarts** if bot crashes  
✅ **Centralized logs** (journalctl)  
✅ **Easy control** (start/stop/restart)  
✅ **Runs in background** (no SSH needed)  
✅ **Resource limits** (memory, CPU)  

**Perfect for 24/7 trading — Wesley can start/stop/monitor without touching SSH.**

---

## 📋 Prerequisites

- Linux server (Ubuntu, Debian, CentOS — Hostinger VPS supported)
- Root/sudo access
- crypto-executor v2.3 installed and tested (see CONFIGURATION.md)
- websocket-client installed:
  ```bash
  pip install websocket-client --break-system-packages
  # Why: enables sub-100ms WebSocket streams
  # Without it: bot falls back to REST 1s (still works, but slower)
  # On VPS/standard server: prefer virtualenv instead:
  # python3 -m venv venv && source venv/bin/activate && pip install websocket-client
  ```

---

## 🚀 Installation

### **Step 1: Create Service File**

```bash
sudo nano /etc/systemd/system/crypto-executor.service
```

**Paste this content:**

```ini
[Unit]
Description=Crypto Executor v2.3 PRODUCTION READY - Autonomous Trading Bot
Documentation=https://github.com/georges91560/crypto-executor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=your_username
Group=your_username
WorkingDirectory=/workspace/skills/crypto-executor

# Credentials — loaded from secure file (see Security section below)
# Create /etc/crypto-executor/credentials.env first (chmod 600, root-owned)
EnvironmentFile=/etc/crypto-executor/credentials.env

# Execution
ExecStart=/usr/bin/python3 /workspace/skills/crypto-executor/executor.py

# Restart Policy
Restart=on-failure
RestartSec=10
StartLimitInterval=200
StartLimitBurst=5

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=crypto-executor

# Resource Limits
MemoryMax=2G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

**Important — Replace these values:**

- `User=your_username` → Your Linux username (e.g., `ubuntu`)
- `Group=your_username` → Usually same as User
- `WorkingDirectory=` → Full path to bot folder

**⚠️ Credentials:** Do NOT put API keys directly in this file. Use `EnvironmentFile=` (see Security section below) — credentials stay in a root-owned chmod 600 file and are never exposed in `systemctl status` or `ps aux`.

**Save:** Ctrl+X, Y, Enter

---

### **Step 2: Reload systemd**

```bash
sudo systemctl daemon-reload
# Why: tells systemd to read the new service file
```

---

### **Step 3: Enable Auto-Start**

```bash
sudo systemctl enable crypto-executor
# Why: creates a symlink so the bot starts automatically on every server reboot
```

**Output:**
```
Created symlink /etc/systemd/system/multi-user.target.wants/crypto-executor.service → /etc/systemd/system/crypto-executor.service
```

✅ Bot will start automatically on server boot!

---

### **Step 4: Start Service**

```bash
sudo systemctl start crypto-executor
```

---

### **Step 5: Verify Running**

```bash
sudo systemctl status crypto-executor
```

**Expected output:**

```
● crypto-executor.service - Crypto Executor v2.3 PRODUCTION READY
   Loaded: loaded (/etc/systemd/system/crypto-executor.service; enabled)
   Active: active (running) since Thu 2026-02-28 15:00:00 UTC; 5s ago
 Main PID: 12345 (python3)
   Memory: 89.2M
   
Feb 28 15:00:00 systemd[1]: Started Crypto Executor v2.3 PRODUCTION READY.
Feb 28 15:00:01 crypto-executor[12345]: [OK] Credentials validated
Feb 28 15:00:01 crypto-executor[12345]: [WS] Started 10 streams (WebSocket)
Feb 28 15:00:02 crypto-executor[12345]: [MEMORY] Loaded learned_config.json
Feb 28 15:00:03 crypto-executor[12345]: [FEATURES] Kelly ✓ Trailing ✓ Reports ✓
```

**Key indicators:**
- ✅ `Active: active (running)` — Bot is running
- ✅ `enabled` — Will restart on boot
- ✅ `[WS] Started 10 streams (WebSocket)` — Real-time feeds active
- ✅ `[MEMORY] Loaded learned_config.json` — Bot memory restored

---

## 📊 Daily Operations

### **View Live Logs**

```bash
sudo journalctl -u crypto-executor -f
# Press Ctrl+C to exit
```

**What you'll see:**
```
[SCAN] Completed in 0.48s
[TRADE] BUY 0.11 BTCUSDT (Kelly: $540)
[OCO] Created: SELL 0.11 BTCUSDT
[TRAIL] BTCUSDT trailing stop → $45,000.00
[CLOSED] BTCUSDT via OCO | PnL: +$12.40 (+0.28%)
[PORTFOLIO] $10,543.00 | Drawdown: 1.2%
```

---

### **View Recent Logs**

```bash
# Last 100 lines
sudo journalctl -u crypto-executor -n 100

# Since today
sudo journalctl -u crypto-executor --since today

# Since specific time
sudo journalctl -u crypto-executor --since "2026-02-28 10:00:00"

# Only errors
sudo journalctl -u crypto-executor -p err
```

---

### **Control Service**

```bash
# Stop trading
sudo systemctl stop crypto-executor

# Start trading
sudo systemctl start crypto-executor

# Restart (reload config)
sudo systemctl restart crypto-executor

# Check if running
sudo systemctl is-active crypto-executor
# Output: "active" or "inactive"
```

---

### **Disable Auto-Start**

```bash
# Disable boot auto-start (keeps running now)
sudo systemctl disable crypto-executor

# Re-enable
sudo systemctl enable crypto-executor
```

---

## 🔧 Troubleshooting

### **Service Won't Start**

```bash
# Check for errors
sudo systemctl status crypto-executor

# View detailed logs
sudo journalctl -u crypto-executor -n 50
```

**Common issues:**

1. **Wrong User/Group**
   ```bash
   whoami   # find your username
   sudo nano /etc/systemd/system/crypto-executor.service
   # Update User= and Group=
   ```

2. **Wrong WorkingDirectory**
   ```bash
   ls /workspace/skills/crypto-executor/executor.py
   # Update WorkingDirectory= if path differs
   ```

3. **Wrong Python Path**
   ```bash
   which python3
   # Update ExecStart= with correct path
   ```

4. **Missing Credentials**
   ```bash
   sudo nano /etc/systemd/system/crypto-executor.service
   # Verify all Environment= lines are filled
   ```

---

### **Service Keeps Crashing**

```bash
sudo journalctl -u crypto-executor -n 100 | grep ERROR
```

**Check dependencies:**
```bash
# Verify executor installed
ls /workspace/skills/crypto-executor/executor.py

# Verify oracle installed
ls /workspace/skills/crypto-sniper-oracle/crypto_oracle.py

# Test oracle
python3 /workspace/skills/crypto-sniper-oracle/crypto_oracle.py --symbol BTCUSDT

# Verify websocket-client
python3 -c "import websocket; print('✅ websocket-client OK')"
```

---

### **Circuit Breaker Triggered**

**Normal behavior — bot protecting capital.**

```bash
# Check reason
sudo journalctl -u crypto-executor | grep "CIRCUIT BREAKER"
# Example: [CIRCUIT BREAKER] Level 1: Daily loss -2.1% > -2.0%
# Example: [PAUSED] Until 2026-02-28 17:00:00

# Bot auto-resumes after pause period
# OR manually restart:
sudo systemctl restart crypto-executor
```

---

### **High Memory Usage**

```bash
systemctl status crypto-executor | grep Memory

# If > 1.5GB:
sudo nano /etc/systemd/system/crypto-executor.service
# Change: MemoryMax=1G
sudo systemctl daemon-reload
sudo systemctl restart crypto-executor
```

---

## 🔒 Security — Protect Credentials

**Use EnvironmentFile instead of inline Environment= (recommended):**

```bash
# Create credentials file
sudo mkdir -p /etc/crypto-executor
sudo nano /etc/crypto-executor/credentials.env

# Content:
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_id
MAX_POSITION_SIZE_PCT=12
DAILY_LOSS_LIMIT_PCT=2
DRAWDOWN_KILL_PCT=10

# Protect — only root can read
sudo chmod 600 /etc/crypto-executor/credentials.env
sudo chown root:root /etc/crypto-executor/credentials.env
```

**Edit service file — replace all Environment= lines with one line:**

```bash
sudo nano /etc/systemd/system/crypto-executor.service
# Replace all Environment= lines with:
EnvironmentFile=/etc/crypto-executor/credentials.env

sudo systemctl daemon-reload
sudo systemctl restart crypto-executor
```

**Why this is better:**
- ✅ Credentials not visible in `systemctl status` output
- ✅ File protected chmod 600 (root only)
- ✅ Not exposed in process list (`ps aux`)
- ✅ Shared with manual runs: `source /etc/crypto-executor/credentials.env`

---

## 📈 Monitoring

### **Check Resource Usage**

```bash
systemctl status crypto-executor | grep -E "Memory|CPU|Tasks"
```

**Normal values:**
```
Tasks: 22 (limit: 4915)
Memory: 89.1M
CPU: 2.4s
```
- Memory: 50-150MB
- CPU: 1-5% average
- Tasks: 15-30 threads

---

### **Monitor Trading Activity**

```bash
# Live trades
tail -f /workspace/trades_history.jsonl

# Count trades today
cat /workspace/trades_history.jsonl | grep $(date +%Y-%m-%d) | wc -l

# Active positions
cat /workspace/open_positions.json | python3 -m json.tool

# Performance metrics (win rate, Kelly, Sharpe)
cat /workspace/performance_metrics.json | python3 -m json.tool

# Bot memory — what it learned
cat /workspace/learned_config.json | python3 -m json.tool
# Shows: current strategy mix, win rates, last adjustment date

# Positions closed by OCO (v2.3)
grep "CLOSED" /workspace/trades_history.jsonl | tail -10
```

---

### **Monitor Daily Reports**

```bash
# Today's report
cat /workspace/reports/daily/report_$(date +%Y-%m-%d).txt

# List all reports
ls -lh /workspace/reports/daily/

# Last 3 reports
ls /workspace/reports/daily/ | tail -3 | xargs -I {} cat /workspace/reports/daily/{}
```

---

## ✅ Verification Checklist

After installation:

- [ ] `systemctl status crypto-executor` shows "active (running)"
- [ ] `systemctl is-enabled crypto-executor` shows "enabled"
- [ ] Logs show bot activity: `journalctl -u crypto-executor -n 20`
- [ ] WebSocket streams started (10 streams)
- [ ] `[MEMORY] Loaded learned_config.json` in startup logs
- [ ] Kelly sizing active
- [ ] No error messages
- [ ] Telegram alerts working
- [ ] Can restart: `sudo systemctl restart crypto-executor`
- [ ] Auto-restart works: Kill PID, wait 10s, check new PID
- [ ] Files generating in /workspace

---

## 🚀 Test Auto-Restart

**Verify bot restarts automatically on crash:**

```bash
# Get PID
systemctl status crypto-executor | grep "Main PID"

# Simulate crash
sudo kill -9 <PID>

# Wait 10 seconds
sleep 10

# Verify new PID — bot restarted automatically
sudo systemctl status crypto-executor
```

✅ New PID + "active (running)" = systemd working correctly!

---

## 🎯 Quick Reference

```bash
# START
sudo systemctl start crypto-executor

# STOP
sudo systemctl stop crypto-executor

# RESTART
sudo systemctl restart crypto-executor

# STATUS
sudo systemctl status crypto-executor

# LOGS (real-time)
sudo journalctl -u crypto-executor -f

# LOGS (last 100)
sudo journalctl -u crypto-executor -n 100

# ENABLE boot auto-start
sudo systemctl enable crypto-executor

# DISABLE boot auto-start
sudo systemctl disable crypto-executor

# CHECK if running
sudo systemctl is-active crypto-executor

# CHECK if enabled
sudo systemctl is-enabled crypto-executor

# VIEW resource usage
systemctl status crypto-executor | grep -E "Memory|CPU"

# VIEW bot memory
cat /workspace/learned_config.json | python3 -m json.tool
```

---

## 💡 Pro Tips

### **Run Multiple Instances**

```bash
# Create second service — e.g. conservative profile
sudo cp /etc/systemd/system/crypto-executor.service \
       /etc/systemd/system/crypto-executor-conservative.service

sudo nano /etc/systemd/system/crypto-executor-conservative.service
# Change: Description, MAX_POSITION_SIZE_PCT=8, DAILY_LOSS_LIMIT_PCT=1

sudo systemctl daemon-reload
sudo systemctl enable crypto-executor-conservative
sudo systemctl start crypto-executor-conservative
```

---

### **Schedule Restarts**

```bash
# Weekly restart every Sunday at 2am
sudo crontab -e
# Add:
0 2 * * 0 systemctl restart crypto-executor
# Why: clears memory leaks, reloads learned_config.json fresh
```

---

### **Export Logs**

```bash
# Last 24h
sudo journalctl -u crypto-executor --since "24 hours ago" > executor_24h.log

# Specific date
sudo journalctl -u crypto-executor --since "2026-02-28" --until "2026-03-01" > executor_feb28.log
```

---

**Your crypto-executor v2.3 now runs 24/7 professionally! 🔥💰**

**PRODUCTION READY — auto-start, auto-restart, full monitoring. ⚡**
