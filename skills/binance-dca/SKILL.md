---
name: binance-dca
description: Professional Binance Dollar-Cost Averaging (DCA) tool for automated and manual recurring crypto purchases. Plan DCA strategies with scenario analysis, execute market/limit buys, track history, and manage systematic accumulation schedules for any trading pair. Includes risk management, testnet support, and OpenClaw automation integration. Triggers on requests about DCA, recurring buys, cost averaging, accumulation strategies, or Binance spot purchases.
---

# Binance DCA — Professional Dollar-Cost Averaging Tool

> **Systematic crypto accumulation made simple.**  
> Plan, execute, and track DCA strategies on Binance with confidence.

## What is DCA?

**Dollar-Cost Averaging (DCA)** is an investment strategy where you buy a fixed dollar amount of an asset at regular intervals, regardless of price. This approach:

- ✅ **Reduces timing risk** — no need to predict market tops/bottoms
- ✅ **Smooths volatility** — averages out price fluctuations over time
- ✅ **Removes emotion** — systematic buying, no panic or FOMO
- ✅ **Builds discipline** — consistent accumulation, perfect for long-term holders

**This tool** helps you plan, automate, and track your DCA strategy on Binance spot markets.

---

## Features

- 📊 **DCA Plan Projections** — scenario analysis showing potential outcomes at different price levels
- 💰 **Market & Limit Orders** — flexible execution options
- 📈 **Trade History** — track your accumulation progress
- 🔒 **Secure** — credentials via environment variables only, zero hardcoded secrets
- 🧪 **Testnet Support** — practice on Binance testnet before going live
- 🤖 **OpenClaw Integration** — automate DCA buys via cron jobs with alerts
- 🛡️ **Risk Management** — conservative defaults, validation before execution

---

## Setup

### 1. Get Binance API Keys

1. Log in to [binance.com](https://www.binance.com)
2. Go to **Account** → **API Management**
3. Create a new API key:
   - **Label:** `OpenClaw-DCA` (or similar)
   - **Restrictions:** Enable **Spot & Margin Trading** only
   - **IP Whitelist:** Add your server IP for security (optional but recommended)
4. Save your **API Key** and **Secret Key** securely

⚠️ **Security tips:**
- Never share your secret key
- Enable IP whitelist if your server has a static IP
- Use a separate API key for DCA (easier to revoke if needed)
- Start with small amounts to test

### 2. Set Environment Variables

**Never hardcode credentials.** Always use environment variables:

```bash
export BINANCE_API_KEY="your-api-key-here"
export BINANCE_SECRET_KEY="your-secret-key-here"
```

**Make them permanent** (optional, add to `~/.bashrc` or `~/.zshrc`):

```bash
echo 'export BINANCE_API_KEY="your-api-key-here"' >> ~/.bashrc
echo 'export BINANCE_SECRET_KEY="your-secret-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**For testnet** (recommended for first-time users):

```bash
export BINANCE_BASE_URL="https://testnet.binance.vision"
```

Get testnet API keys at: [testnet.binance.vision](https://testnet.binance.vision/)

### 3. Verify Setup

```bash
# Check balance (should not error)
bash scripts/dca.sh balance USDT

# Check BTC price
bash scripts/dca.sh price BTCUSDT
```

If you see prices/balances, you're ready!

---

## Quick Start Examples

### Example 1: Check Current Price

```bash
bash scripts/dca.sh price BTCUSDT
# Output: BTCUSDT = 95234.50
```

Works for any pair:
```bash
bash scripts/dca.sh price ETHUSDT
bash scripts/dca.sh price SOLUSDT
```

### Example 2: Check Your Balance

```bash
bash scripts/dca.sh balance USDT
# Output: USDT: free=1000.00000000, locked=0.00000000
```

Check any asset:
```bash
bash scripts/dca.sh balance BTC
bash scripts/dca.sh balance ETH
```

### Example 3: Plan a DCA Strategy

**Scenario:** You want to invest $600 over 3 months in BTC.

```bash
# $50 every week for 12 weeks
bash scripts/dca.sh plan 50 7 12 BTCUSDT
```

**Output:**
```
DCA Plan: BTCUSDT
==========================
Buy amount:  $50 per buy
Frequency:   every 7 days
Duration:    12 buys
Current:     95234.50
==========================
Total invest:  $600.00
At cur. price: 0.00630245 BTC
Time span:     84 days (~2.8 months)

Scenario Analysis (if avg price over period is):
  -30% -> avg $ 66,664.15 -> 0.00900000 BTC -> PnL: -$186.00 (-31.0%)
  -20% -> avg $ 76,187.60 -> 0.00787500 BTC -> PnL: -$126.00 (-21.0%)
  -10% -> avg $ 85,711.05 -> 0.00700000 BTC -> PnL: -$63.00 (-10.5%)
   +0% -> avg $ 95,234.50 -> 0.00630245 BTC -> PnL: +$0.00 (+0.0%)
  +10% -> avg $104,757.95 -> 0.00572727 BTC -> PnL: +$63.00 (+10.5%)
  +20% -> avg $114,281.40 -> 0.00525000 BTC -> PnL: +$126.00 (+21.0%)
  +50% -> avg $142,851.75 -> 0.00420000 BTC -> PnL: +$378.00 (+63.0%)
 +100% -> avg $190,469.00 -> 0.00315122 BTC -> PnL: +$630.00 (+105.0%)
```

**What this tells you:**
- If BTC stays flat → break even
- If BTC averages -20% during your buys → you're down ~21% (but you own more BTC)
- If BTC averages +50% → you're up ~63%

Use this to **set realistic expectations** before committing.

### Example 4: Execute Your First DCA Buy

**Market order (instant execution):**

```bash
# Buy $50 worth of BTC at current market price
bash scripts/dca.sh buy BTCUSDT 50
```

**Output:**
```
Placing MARKET buy: BTCUSDT for 50 USDT...
Order #123456789: FILLED
Filled: 0.00052500 BTC
```

**Limit order (wait for your price):**

```bash
# Only buy if BTC drops to $94,000
bash scripts/dca.sh buy BTCUSDT 50 LIMIT 94000
```

**Output:**
```
Placing LIMIT buy: BTCUSDT for 50 USDT...
Order #123456790: NEW
Filled: 0.00000000 BTC
```

(Order will fill when price hits $94,000)

### Example 5: Check Your Trade History

```bash
# Last 10 trades for BTCUSDT
bash scripts/dca.sh history BTCUSDT 10
```

**Output:**
```
Last 10 trades for BTCUSDT:
---
1738752000 | BUY | qty=0.00052500 | price=95238.10 | fee=0.00000053 BNB
1738665600 | BUY | qty=0.00051234 | price=97567.20 | fee=0.00000051 BNB
...
```

---

## Complete Action Reference

### `price [SYMBOL]`

**Get current spot price for a trading pair.**

```bash
bash scripts/dca.sh price BTCUSDT
bash scripts/dca.sh price ETHUSDT
bash scripts/dca.sh price SOLUSDT
```

**Default:** `BTCUSDT` if symbol is omitted.

---

### `balance [ASSET]`

**Check free and locked balance for an asset.**

```bash
bash scripts/dca.sh balance USDT
bash scripts/dca.sh balance BTC
bash scripts/dca.sh balance ETH
```

**Output format:** `ASSET: free=X.XXXXXXXX, locked=Y.YYYYYYYY`

**Default:** `USDT` if asset is omitted.

**Use case:** Check how much capital you have available before placing orders.

---

### `buy SYMBOL AMOUNT [TYPE] [PRICE]`

**Place a buy order.**

**Arguments:**
- `SYMBOL` — Trading pair (e.g., `BTCUSDT`, `ETHUSDT`)
- `AMOUNT` — Amount in **quote currency** (USDT). The tool calculates how much BTC/ETH you get.
- `TYPE` — `MARKET` (default) or `LIMIT`
- `PRICE` — Required for `LIMIT` orders

**Market order examples:**

```bash
# Buy $50 worth of BTC instantly
bash scripts/dca.sh buy BTCUSDT 50

# Buy $100 worth of ETH instantly
bash scripts/dca.sh buy ETHUSDT 100
```

**Limit order examples:**

```bash
# Buy $50 BTC only if price drops to $90,000
bash scripts/dca.sh buy BTCUSDT 50 LIMIT 90000

# Buy $200 ETH only if price hits $3,200
bash scripts/dca.sh buy ETHUSDT 200 LIMIT 3200
```

**Safety features:**
- Amount validation (must be a number)
- API key check before execution
- Order status confirmation in output

---

### `history [SYMBOL] [LIMIT]`

**Show recent trade history.**

```bash
# Last 10 trades for BTCUSDT
bash scripts/dca.sh history BTCUSDT 10

# Last 20 trades for ETHUSDT
bash scripts/dca.sh history ETHUSDT 20

# Last 50 trades for SOLUSDT
bash scripts/dca.sh history SOLUSDT 50
```

**Defaults:** `BTCUSDT`, limit `10`

**Output includes:**
- Timestamp (Unix seconds)
- Side (BUY/SELL)
- Quantity purchased
- Execution price
- Fees paid (and fee asset)

**Use case:** Track your DCA progress over time, calculate average entry price.

---

### `plan [AMOUNT] [FREQ_DAYS] [NUM_BUYS] [SYMBOL]`

**Project a DCA plan with scenario analysis.**

**Arguments:**
- `AMOUNT` — Dollar amount per buy (default: `50`)
- `FREQ_DAYS` — Days between buys (default: `7`)
- `NUM_BUYS` — Number of buys (default: `12`)
- `SYMBOL` — Trading pair (default: `BTCUSDT`)

**Examples:**

```bash
# Default plan: $50 every 7 days, 12 buys
bash scripts/dca.sh plan

# Aggressive: $200 every 3 days, 30 buys
bash scripts/dca.sh plan 200 3 30 BTCUSDT

# Conservative: $25 every 14 days, 24 buys
bash scripts/dca.sh plan 25 14 24 BTCUSDT

# ETH DCA: $100 weekly for 6 months
bash scripts/dca.sh plan 100 7 26 ETHUSDT
```

**What you get:**
- Total investment amount
- BTC/ETH you'd own at current price
- Time span (days + months)
- **Scenario analysis:** PnL at -30%, -20%, -10%, 0%, +10%, +20%, +50%, +100% average prices

**Use this to:**
- Decide on a comfortable budget and frequency
- Understand risk/reward before starting
- Show the math to justify DCA vs. lump sum

---

## DCA Strategy Guide

### When to Use DCA

✅ **Good for:**
- Long-term accumulation (6+ months)
- High-volatility assets (BTC, ETH, altcoins)
- Building positions without timing stress
- Removing emotional decision-making

❌ **Not ideal for:**
- Short-term trading (use manual buys)
- Assets you want to flip quickly
- Low-volatility stablecoins (just buy once)

### Best Practices

1. **Start small** — Test with 1-2% of your budget first
2. **Use testnet** — Practice on `https://testnet.binance.vision` before going live
3. **Set a timeline** — DCA works best over 3-12+ months
4. **Stick to the plan** — Resist urge to stop during dips (that's when DCA shines)
5. **Track progress** — Use `history` to see your average entry price
6. **Adjust if needed** — Life changes, budgets change — recalculate with `plan` and adapt

### Position Sizing Recommendations

**Conservative (1-2% per buy):**
- Portfolio: $10,000 → DCA $100-$200 per buy
- Lower risk, slower accumulation

**Moderate (3-5% per buy):**
- Portfolio: $10,000 → DCA $300-$500 per buy
- Balanced approach, standard for most users

**Aggressive (5-10% per buy):**
- Portfolio: $10,000 → DCA $500-$1,000 per buy
- Higher risk, faster accumulation, requires strong conviction

**Never go above 10% per buy** — leaves no room for unexpected dips or expenses.

### Frequency Guidelines

- **Daily** — For very active traders, high time commitment
- **Every 3 days** — Aggressive, good for short DCA periods (1-3 months)
- **Weekly** — Most popular, good balance (Mondays are common)
- **Bi-weekly** — Aligns with paychecks, moderate pace
- **Monthly** — Long-term HODLers, lowest effort

**Pro tip:** Match DCA frequency to your income schedule (weekly paycheck → weekly DCA).

---

## Automation with OpenClaw

### Manual Cron (Basic)

Run DCA buys automatically via system cron:

```bash
# Every Monday at 9:00 AM UTC, buy $50 BTC
0 9 * * 1 BINANCE_API_KEY=... BINANCE_SECRET_KEY=... /path/to/dca.sh buy BTCUSDT 50
```

**Limitations:**
- No alerts if it fails
- No confirmations
- Silent execution

### OpenClaw Cron (Recommended)

Use OpenClaw for intelligent DCA automation with alerts:

**Example: Weekly BTC DCA with Telegram notifications**

```json
{
  "name": "Weekly BTC DCA",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * 1",
    "tz": "America/New_York"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Execute weekly DCA: buy $50 BTCUSDT via binance-dca skill. After execution, send me a summary: amount bought, price, total BTC accumulated so far (check history). If it fails, alert me immediately.",
    "deliver": true,
    "channel": "telegram"
  }
}
```

**Benefits:**
- ✅ Execution confirmations sent to you
- ✅ Failure alerts
- ✅ Can ask agent to analyze history and report progress
- ✅ Easy to pause/resume via `openclaw cron` commands

**Setup:**

```bash
# Add the cron job (paste JSON above when prompted)
openclaw cron add

# List all jobs
openclaw cron list

# Run manually to test
openclaw cron run <jobId>

# Disable temporarily
openclaw cron update <jobId> --enabled false
```

---

## Troubleshooting

### Error: `BINANCE_API_KEY not set`

**Fix:** Set environment variables before running:

```bash
export BINANCE_API_KEY="your-key"
export BINANCE_SECRET_KEY="your-secret"
bash scripts/dca.sh price
```

---

### Error: `Timestamp for this request is outside of the recvWindow`

**Cause:** Your system clock is out of sync with Binance servers.

**Fix (Linux/macOS):**

```bash
# Sync system time
sudo ntpdate -s time.nist.gov

# Or install/enable NTP
sudo systemctl enable systemd-timesyncd
sudo systemctl start systemd-timesyncd
```

**Fix (Docker):**

Add `--cap-add SYS_TIME` when running container, or sync host clock.

---

### Error: `Signature for this request is not valid`

**Causes:**
- Wrong `BINANCE_SECRET_KEY`
- API key restrictions (IP whitelist mismatch, disabled Spot Trading)

**Fix:**
1. Double-check your secret key (copy-paste from Binance)
2. Verify API key has **Spot & Margin Trading** enabled
3. If using IP whitelist, confirm your server IP is allowed
4. Regenerate API key if uncertain

---

### Error: `API request failed`

**Causes:**
- Network issues
- Wrong `BINANCE_BASE_URL`
- Binance API maintenance

**Fix:**
1. Test network: `curl -I https://api.binance.com`
2. Check Binance status: [binance.com/en/support/announcement](https://www.binance.com/en/support/announcement)
3. If using testnet, confirm: `export BINANCE_BASE_URL="https://testnet.binance.vision"`

---

### Error: `Account has insufficient balance for requested action`

**Cause:** Not enough USDT in your spot account.

**Fix:**
1. Check balance: `bash scripts/dca.sh balance USDT`
2. Deposit USDT to your spot account
3. Reduce DCA amount to match available balance

---

### Order shows `NEW` status (limit order not filling)

**This is normal for limit orders.** Status means:
- `NEW` — Order placed, waiting for price
- `FILLED` — Order executed
- `PARTIALLY_FILLED` — Partial execution
- `CANCELED` — You or system canceled it

**Check order status:**

```bash
# View recent orders to see if it filled later
bash scripts/dca.sh history BTCUSDT 20
```

**Cancel pending limit orders:**

Use Binance web/app → **Orders** → **Open Orders** → Cancel.

---

## FAQ

### Q: Can I DCA into altcoins (not just BTC)?

**A:** Yes! Use any Binance spot pair:

```bash
bash scripts/dca.sh buy ETHUSDT 100
bash scripts/dca.sh buy SOLUSDT 50
bash scripts/dca.sh buy ADAUSDT 25
```

Just replace `BTCUSDT` with your desired pair.

---

### Q: What's the minimum buy amount?

**A:** Binance sets minimums per pair (usually $10-$20). Check Binance docs or test with a small amount on testnet first.

---

### Q: Does this work with Binance.US?

**A:** Not directly. Binance.US has a separate API (`https://api.binance.us`). You'd need to change `BINANCE_BASE_URL` and test. Not officially supported.

---

### Q: Can I sell with this tool?

**A:** Not currently. This is DCA (accumulation) only. For selling, use Binance web/app or modify the script (change `side=BUY` to `side=SELL`).

---

### Q: Is my data stored anywhere?

**A:** No. Zero data storage. All credentials are environment variables. The script makes direct API calls to Binance and exits.

---

### Q: Can I use this on multiple machines?

**A:** Yes, but set up API keys separately on each. Consider using **IP whitelist** on your API key for security.

---

### Q: What if I want to change my DCA amount mid-strategy?

**A:** Just adjust the amount in your next manual/cron execution. DCA is flexible — no commitment to fixed amounts.

Example: Week 1-4 use $50, Week 5+ use $100.

---

### Q: How do I calculate my average entry price?

Run `history` and average the `price` column:

```bash
bash scripts/dca.sh history BTCUSDT 50 | grep BUY | awk '{print $8}' | awk '{s+=$1; n++} END {print s/n}'
```

Or use a spreadsheet: export history, paste prices, `=AVERAGE()`.

---

## Security Best Practices

🔒 **API Key Safety:**
- Use dedicated API key for DCA (label it `DCA-Only`)
- Enable **Spot Trading** only (no Futures, Margin, Withdrawals)
- Set IP whitelist if your server has static IP
- Rotate keys every 3-6 months
- Revoke immediately if compromised

🔒 **Credential Management:**
- Never commit `.env` files with keys to Git
- Use environment variables, not hardcoded strings
- On shared servers, restrict file permissions: `chmod 600 ~/.bashrc`

🔒 **Testnet First:**
- Always test new strategies on testnet before using real funds
- Testnet keys: [testnet.binance.vision](https://testnet.binance.vision/)
- Set: `export BINANCE_BASE_URL="https://testnet.binance.vision"`

🔒 **Start Small:**
- First live DCA: use 10-20% of planned amount
- Verify execution, fees, and confirmations
- Scale up once confident

---

## Advanced Usage

### Dynamic DCA (Market Conditions)

Adjust buy amounts based on price:

**Buy more when BTC dips:**

```bash
# If BTC < $90k, buy $100. Otherwise $50.
CURRENT=$(bash scripts/dca.sh price BTCUSDT | awk '{print $3}')
if (( $(echo "$CURRENT < 90000" | bc -l) )); then
  bash scripts/dca.sh buy BTCUSDT 100
else
  bash scripts/dca.sh buy BTCUSDT 50
fi
```

**Use limit orders to "buy the dip":**

```bash
# Place limit orders 5%, 10%, 15% below current price
PRICE=$(bash scripts/dca.sh price BTCUSDT | awk '{print $3}')
LIMIT_5=$(echo "$PRICE * 0.95" | bc)
LIMIT_10=$(echo "$PRICE * 0.90" | bc)
LIMIT_15=$(echo "$PRICE * 0.85" | bc)

bash scripts/dca.sh buy BTCUSDT 50 LIMIT $LIMIT_5
bash scripts/dca.sh buy BTCUSDT 50 LIMIT $LIMIT_10
bash scripts/dca.sh buy BTCUSDT 50 LIMIT $LIMIT_15
```

### Multi-Asset DCA

DCA into multiple coins:

```bash
# Weekly: $30 BTC, $20 ETH, $10 SOL
bash scripts/dca.sh buy BTCUSDT 30
bash scripts/dca.sh buy ETHUSDT 20
bash scripts/dca.sh buy SOLUSDT 10
```

### Logging for Analysis

Track all DCA buys to a log file:

```bash
#!/bin/bash
LOGFILE="$HOME/dca-log.txt"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

bash scripts/dca.sh buy BTCUSDT 50 | tee -a "$LOGFILE"
echo "[$DATE] DCA executed" >> "$LOGFILE"
```

Then analyze with:

```bash
grep "Filled:" ~/dca-log.txt
```

---

## Contributing

Found a bug? Have a feature idea? Want to add support for other exchanges?

- **GitHub:** (if public repo exists, link here)
- **Issues:** Report via GitHub Issues
- **Pull Requests:** Welcome! Follow existing code style.

---

## License

MIT License — Free to use, modify, and distribute.

**Disclaimer:** This tool is provided as-is. Use at your own risk. The authors are not responsible for trading losses, API issues, or incorrect usage. Always test on testnet first and never invest more than you can afford to lose.

---

## Changelog

### v1.2.0 (2026-02-05)
- 📚 Comprehensive documentation overhaul
- 📋 Added real-world examples for all actions
- 🎓 DCA strategy guide with best practices
- 🔧 Troubleshooting section
- ❓ FAQ with common questions
- 🔒 Security best practices guide
- 🚀 Advanced usage examples
- 🤖 OpenClaw automation guide

### v1.1.0 (2026-02-05)
- Initial public release
- Core DCA functionality: plan, buy, history, price, balance
- Testnet support
- Market and limit orders

---

**Built with ❤️ for long-term crypto accumulation.**

Questions? Feedback? Tag `@fpsjago` on ClawHub or OpenClaw Discord.
