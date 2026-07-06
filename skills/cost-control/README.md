# Cost Control System — 3-Tier API Spend Protection
## Prevent runaway API costs. Works for ANY expensive API (GPT-4, Claude Opus, Gemini, cloud services).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)]()

**Cost Control System is a production-grade cost monitoring framework with tiered responses, external watchdog, and kill switch.**

Originally built to prevent catastrophic AI API spend after a real runaway cost incident, now generalized for **any** expensive API that charges per request/token/compute.

---

## The Problem

You're running a system that makes API calls to an expensive service (OpenAI GPT-4, Anthropic Claude Opus, Google Gemini, cloud compute, etc.).

One bug, one infinite loop, one configuration error → **hundreds of dollars burned in minutes**.

**Manual monitoring doesn't work.** You need automated cost controls with failsafes.

---

## The Solution

Cost Control System implements **3-tier protection**:

### Tier 1: Caution Mode (Warning)
When cost velocity exceeds threshold (e.g., $3/15min):
- Slow down check intervals
- Log warnings
- Continue operating but throttled

### Tier 2: Emergency Mode (Stop)
When cost velocity is dangerous (e.g., $5/15min):
- **Stop all API calls**
- Enter maintenance mode
- Preserve existing state
- Alert operator

### Tier 3: Kill Switch (External Watchdog)
Independent process monitors cost separately:
- If Tier 2 fails to stop runaway spend
- **Kill the entire process**
- Prevent restart until manually cleared
- Last line of defense

---

## Quick Start (3 Steps)

### 1. Install
```bash
pip install cost-control-system
# OR copy cost_control.py to your project
```

### 2. Integrate with Your API Client
```python
from cost_control import CostTracker

tracker = CostTracker(
    cost_caution_15min=3.00,      # Warning at $3/15min
    cost_emergency_15min=5.00,    # Emergency at $5/15min
    cost_daily_cap=25.00,         # Hard cap at $25/day
)

# Before each API call, check if allowed
allowed, reason = tracker.is_call_allowed()
if not allowed:
    print(f"API call blocked: {reason}")
    # Handle emergency mode (alert, exit, etc.)
    return

# Make your API call
response = your_expensive_api_call()

# Record actual cost
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
tracker.record_call(input_tokens, output_tokens, request_id="req-123")
```

### 3. Deploy External Watchdog (Optional but Recommended)
```bash
# Run external watchdog every 2 minutes (via cron)
*/2 * * * * cd /your/project && python3 cost_watchdog.py >> logs/watchdog.log 2>&1
```

**Time to integrate: 15-20 minutes.**

---

## Use Cases

### AI API Calls (GPT-4, Claude Opus, Gemini)
Prevent runaway token usage from:
- Infinite loops generating responses
- Misconfigured context windows (100K+ tokens per call)
- Prompt injection causing excessive output

### Cloud Compute (AWS Lambda, GCP Functions, Azure)
Monitor spend on:
- Serverless function invocations
- Compute hours (EC2, VMs)
- Database queries (expensive per-query pricing)

### Third-Party APIs (Stripe, Twilio, SendGrid)
Track costs for:
- SMS/email sends
- Payment processing fees
- Data enrichment APIs

### Research/ML Training
Control costs for:
- GPU compute time
- Model training runs
- Batch inference jobs

**Any API with measurable per-request or per-unit costs benefits from this.**

---

## Architecture

### 3-Tier Response System

```
Normal → Caution (Tier 1) → Emergency (Tier 2) → Kill (Tier 3)
  ↓          ↓                    ↓                  ↓
  OK      Slow down          Stop calls      Kill process
```

### Tier 1: Caution Mode
**Trigger:** 15-minute cost > $3 (configurable)  
**Response:**
- Slow down check intervals (reduce API call frequency)
- Log warnings
- Continue operating

**Exit:** 15-minute cost < $2 for 5 minutes

---

### Tier 2: Emergency Mode
**Trigger:** 15-minute cost > $5 OR daily cost > $25 (configurable)  
**Response:**
- **Block all API calls** (`is_call_allowed()` returns False)
- Write emergency flag file
- Send alerts (Discord, Slack, email, etc.)
- System remains alive but paused

**Exit:** Manual intervention required (`rm state/cost_emergency.flag`)

---

### Tier 3: Kill Switch (External Watchdog)
**Trigger:** Hourly cost > $12 OR daily cost > $30 (configurable, higher than Tier 2)  
**Response:**
- **Kill the entire process** (SIGTERM → SIGKILL)
- Write emergency flag (prevents restart)
- Independent of main process (can't be bypassed)

**Purpose:** Catch cases where Tier 2 fails (e.g., bug in cost tracker itself)

---

## Configuration

### Basic Config (Minimal Setup)
```python
from cost_control import CostTracker

tracker = CostTracker(
    # Tier 1 (Caution)
    cost_caution_15min=3.00,
    
    # Tier 2 (Emergency)
    cost_emergency_15min=5.00,
    cost_daily_cap=25.00,
    
    # State persistence
    state_dir="./state",
)
```

### Advanced Config (All Options)
```python
tracker = CostTracker(
    # Thresholds
    cost_caution_15min=3.00,
    cost_emergency_15min=5.00,
    cost_daily_cap=25.00,
    max_cost_per_call=0.50,           # Single-call sanity check
    
    # Recovery
    caution_recovery_threshold=2.00,  # Exit caution when <$2/15min
    caution_recovery_duration=300,    # Must stay below for 5 min
    
    # State
    state_dir="./state",
    cost_log_file="cost_log.jsonl",
    
    # Alerting
    alert_callback=my_alert_function,
)
```

### Pricing Config (Your API)
```python
# Define your API's pricing
tracker.set_pricing(
    input_price_per_unit=15.00,   # e.g., $15 per million input tokens
    output_price_per_unit=75.00,  # e.g., $75 per million output tokens
    unit_size=1_000_000,          # e.g., per million tokens
)

# For non-token APIs (e.g., per-request pricing):
tracker.set_pricing(
    fixed_cost_per_call=0.01,     # $0.01 per API call
)
```

See [config_example.py](./config_example.py) for complete examples.

---

## API Reference

### Core Methods

#### `record_call(input_units, output_units, request_id=None)`
Record an API call with actual usage.

**Args:**
- `input_units` (int): Input units consumed (e.g., tokens, requests)
- `output_units` (int): Output units consumed
- `request_id` (str, optional): Identifier for logging

**Returns:** `True` if within limits, `False` if emergency triggered

---

#### `is_call_allowed()`
Check if API calls are currently allowed.

**Returns:** `(allowed: bool, reason: str)`
- `allowed=True, reason="ok"` → Safe to call API
- `allowed=False, reason="cost_emergency_mode"` → Blocked

**Usage:**
```python
allowed, reason = tracker.is_call_allowed()
if not allowed:
    handle_emergency(reason)
    return
```

---

#### `get_stats()`
Get current cost statistics.

**Returns:** Dict with keys:
```python
{
    "cost_5min": 0.45,
    "cost_15min": 1.23,
    "cost_1hour": 3.45,
    "cost_daily": 12.34,
    "calls_1hour": 23,
    "calls_session": 156,
    "caution_mode": False,
    "emergency_mode": False,
}
```

---

#### `clear_emergency()`
Clear emergency mode (manual intervention).

**Usage:**
```python
tracker.clear_emergency()
# Or: rm state/cost_emergency.flag
```

---

### Properties

- **`caution_mode`** (bool) — Whether in Tier 1 caution
- **`emergency_mode`** (bool) — Whether in Tier 2 emergency
- **`cost_15min`** (float) — Rolling 15-minute cost
- **`cost_daily`** (float) — Total cost today (UTC)

---

## External Watchdog Setup

### 1. Copy Watchdog Script
```bash
cp cost_watchdog.py /your/project/
```

### 2. Configure Watchdog
Edit `cost_watchdog.py`:
```python
KILL_THRESHOLD_HOURLY = 12.00  # $12/hour (higher than Tier 2)
KILL_THRESHOLD_DAILY = 30.00   # $30/day (higher than Tier 2)
```

### 3. Deploy via Cron
```bash
crontab -e

# Add this line (run every 2 minutes)
*/2 * * * * cd /your/project && python3 cost_watchdog.py >> logs/watchdog.log 2>&1
```

### 4. Verify Watchdog is Running
```bash
tail -f logs/watchdog.log
# Should see entries every 2 minutes
```

---

## Kill Switch Usage

### Manual Kill Switch (Immediate Stop)
```bash
python3 kill_switch.py enable
# Stops all API calls immediately
```

### Check Status
```bash
python3 kill_switch.py status
```

### Resume After Emergency
```bash
python3 kill_switch.py disable
rm state/cost_emergency.flag  # Clear emergency flag
# Restart your application
```

---

## Testing

### Unit Tests
```bash
pytest tests/test_cost_control.py
```

### Integration Test (Simulate Runaway)
```python
from cost_control import CostTracker

tracker = CostTracker(
    cost_emergency_15min=1.00,  # Low threshold for testing
)

# Simulate 50 expensive calls
for i in range(50):
    allowed, reason = tracker.is_call_allowed()
    if not allowed:
        print(f"Blocked after {i} calls: {reason}")
        break
    
    # Simulate $0.10 per call
    tracker.record_call(10000, 50000, request_id=f"test-{i}")
    # Should trigger emergency after ~10 calls

# Verify emergency mode
assert tracker.emergency_mode
print("✅ Emergency mode triggered successfully")
```

---

## Limitations

See [LIMITATIONS.md](./LIMITATIONS.md) for details, including:
- Clock skew between system and API
- Delayed cost reporting (API quotas update hourly)
- Watchdog reliability (cron timing jitter)
- Multi-process coordination

---

## Performance

### Memory
- ~100 bytes per recorded call
- Rolling window of last 5000 calls ≈ 500KB memory
- Daily total persists across restarts

### CPU
- Cost calculation: O(1) per call
- Threshold checks: O(1)
- Rolling window: O(N) where N = calls in window (typically <500)

### I/O
- State saves: atomic writes on emergency only
- Cost log: append-only, rotates at 10K entries

---

## Troubleshooting

### Problem: Emergency mode triggered but spend seems normal
**Cause:** Clock skew — system time doesn't match API billing time  
**Fix:** Sync system clock with NTP (`ntpdate` or `chrony`)

---

### Problem: Watchdog doesn't kill runaway process
**Cause:** Cron not running or watchdog script errors  
**Fix:** Check cron logs (`/var/log/syslog`), verify script permissions

---

### Problem: Frequent caution mode cycling
**Cause:** Threshold too low for your use case  
**Fix:** Raise `cost_caution_15min` to match normal usage peaks

---

## Real-World Example: Runaway API Burn Incident

**What happened:**
- A trading bot had dozens of orphaned positions
- Each position triggered an expensive AI API call every few minutes
- Costs compounded rapidly — over $100/hour burn rate
- Ran for over an hour before manual discovery = **$150+ burn**

**How Cost Control would have stopped it:**
1. **Tier 1 (~5 min):** Caution at velocity threshold → slow down checks
2. **Tier 2 (~8 min):** Emergency at higher threshold → stop all API calls
3. **Tier 3 (~10 min):** Watchdog kill at hourly cap → process terminated

**Result:** Max damage $5-8 instead of $150+

---

## Migration Guide

### From No Cost Tracking
1. Calculate baseline cost (1 day of normal usage)
2. Set `cost_caution_15min` = 2x baseline peak
3. Set `cost_emergency_15min` = 3x baseline peak
4. Set `cost_daily_cap` = acceptable daily budget
5. Deploy watchdog with higher thresholds (2x emergency)
6. Run parallel for 1-2 days (log only, no blocking)
7. Enable blocking once validated

### From Manual Monitoring
1. Export historical cost data to CSV
2. Analyze 95th percentile cost per 15-minute window
3. Set thresholds based on percentiles
4. Integrate tracker with existing alerting
5. Gradually enable tiers (start with Tier 1 only)

---

## Contributing

Cost Control System is **open source** and **community-maintained**.

### Report Issues
- Bugs, false positives, performance problems
- Integration confusion
- Feature requests (multi-currency, better alerting, etc.)

### Submit Improvements
- Additional API pricing examples
- Watchdog reliability improvements
- Dashboard/visualization tools

**Contribution guidelines:** Open an issue or PR on GitHub. We review everything.

---

## Philosophy: Why Open Source?

Cost Control solves a **universal infrastructure problem** — preventing runaway API spend. This affects everyone building on paid APIs.

This is a **goodwill project** to:
1. Prevent the $153 incident from happening to others
2. Prove the **vibe coding methodology** (adaptive systems that heal themselves)
3. Build reputation for future paid Shadow Rose products

---

## Support & Community

### Get Help
- 📖 **Documentation:** You're reading it
- 💬 **Discord:** https://discord.com/invite/clawd (OpenClaw community)
- 🐦 **Twitter:** https://x.com/TheShadowyRose
- 🐛 **Issues:** [GitHub link]

### Support Development
Cost Control is free, but if it saved you money:

☕ **Ko-fi:** https://ko-fi.com/theshadowrose

Donations support ongoing testing, docs, and new features.

---

## License

MIT License — use freely, credit appreciated.

Copyright © 2026 Shadow Rose

See [LICENSE](./LICENSE) for details.

---

## What's Next?

### Planned Features
- **Multi-currency support** — Track costs in multiple currencies
- **Budget forecasting** — Predict end-of-day/month spend
- **Granular alerting** — Per-endpoint or per-user cost tracking
- **Dashboard** — Web UI for real-time cost monitoring

**Want to work on these?** Open an issue or reach out on Discord.

---

## Credits

**Created by:** Shadow Rose  
**Extracted from:** Production trading bot (battle-tested in live operation)  
**Philosophy:** Vibe coding — infrastructure that protects itself  
**License:** MIT

Built from a real runaway cost incident — learned the hard way so you don't have to.

---

## Final Thought

Every system that calls expensive APIs will eventually have a runaway cost incident.

The question is: **does your system detect and stop it in 5 minutes, or do you find out when the $1000 bill arrives?**

Cost Control ensures you find out in 5 minutes.

Ship it. Break it. Tell us what you find.

— Shadow Rose  
February 2026

---

☕ Support: https://ko-fi.com/theshadowrose  
🐦 Follow: https://x.com/TheShadowyRose  
💬 Community: https://discord.com/invite/clawd


---

## ⚠️ Disclaimer

This software is provided "AS IS", without warranty of any kind, express or implied.

**USE AT YOUR OWN RISK.**

- The author(s) are NOT liable for any damages, losses, or consequences arising from 
  the use or misuse of this software — including but not limited to financial loss, 
  data loss, security breaches, business interruption, or any indirect/consequential damages.
- This software does NOT constitute financial, legal, trading, or professional advice.
- Users are solely responsible for evaluating whether this software is suitable for 
  their use case, environment, and risk tolerance.
- No guarantee is made regarding accuracy, reliability, completeness, or fitness 
  for any particular purpose.
- The author(s) are not responsible for how third parties use, modify, or distribute 
  this software after purchase.

By downloading, installing, or using this software, you acknowledge that you have read 
this disclaimer and agree to use the software entirely at your own risk.


**TRADING DISCLAIMER:** This software is a tool, not a trading system. It does not 
make trading decisions for you and does not guarantee profits. Trading cryptocurrency, 
stocks, or any financial instrument carries significant risk of loss. You can lose 
some or all of your investment. Past performance of any system or methodology is not 
indicative of future results. Never trade with money you cannot afford to lose. 
Consult a qualified financial advisor before making investment decisions.
---

## Support & Links

| | |
|---|---|
| 🐛 **Bug Reports** | TheShadowyRose@proton.me |
| ☕ **Ko-fi** | [ko-fi.com/theshadowrose](https://ko-fi.com/theshadowrose) |
| 🛒 **Gumroad** | [shadowyrose.gumroad.com](https://shadowyrose.gumroad.com) |
| 🐦 **Twitter** | [@TheShadowyRose](https://twitter.com/TheShadowyRose) |
| 🐙 **GitHub** | [github.com/TheShadowRose](https://github.com/TheShadowRose) |
| 🧠 **PromptBase** | [promptbase.com/profile/shadowrose](https://promptbase.com/profile/shadowrose) |

*Built with [OpenClaw](https://github.com/openclaw/openclaw) — thank you for making this possible.*

---

🛠️ **Need something custom?** Custom OpenClaw agents & skills starting at $500. If you can describe it, I can build it. → [Hire me on Fiverr](https://www.fiverr.com/s/jjmlZ0v)
