---
name: Prediction Stack Setup
description: "Interactive setup wizard for the OpenClaw Prediction Market Trading Stack. Detects installed skills, walks through API key configuration, creates cron jobs for automated scanning and alerts, enables heartbeat for ambient awareness, and tests iMessage delivery. Wires the 10-skill stack into a connected, proactive trading system in under 5 minutes. Run this after installing the stack — or anytime you need to reconfigure schedules, delivery targets, or alert thresholds."
---

# Prediction Stack Setup — One-Command System Activation

## Overview

<!-- CODEX: reconciled setup docs with the 10-skill stack and the public Anthropic-backed reference path. -->
This skill wires the 10-skill OpenClaw Prediction Market Trading Stack into a connected, proactive system. Without setup, skills work individually when you ask for them. After setup, the runtime skills run autonomously — scanning markets, detecting edges, monitoring positions, and delivering intelligence to your phone on a schedule.

**What it does:**
1. Detects which stack skills are installed
2. Configures API keys and credentials
3. **Validates all APIs before creating jobs** (prevents silent failures)
4. Creates scheduled jobs (cron) for each skill
5. Enables heartbeat for ambient awareness
6. Sets up iMessage delivery
7. Tests the full pipeline end-to-end

**Time to complete:** Under 5 minutes

## When to Use This Skill

- You just installed the Prediction Market Trading Stack (all 8 skills or any subset)
- You just installed the Prediction Market Trading Stack (all 10 skills or any subset)
- You want to activate automated scanning and alerts
- You need to change your delivery target (new phone, new email handle)
- You want to adjust scan schedules or alert thresholds
- You're migrating from a previous setup or starting fresh
- Something broke and you want to rewire from scratch

## Prerequisites

### Required
- **OpenClaw** installed and running (gateway active)
- **At least one stack skill** installed (any of the 10)
- **Kalshi account** with API credentials (free at kalshi.com)
- **Anthropic API key** (for Claude Sonnet estimation in Kalshalyst)

### Optional (Enhances the Stack)
- **Polygon.io API key** (free tier — adds news context to Kalshalyst)
- **Ollama + Qwen** installed locally (free — adds offline fallback + Xpulse materiality gate)
- **BlueBubbles** running on your Mac (required for iMessage delivery)

## Setup Procedure

### Phase 1: Skill Detection

First, check which stack skills are installed. Run this command:

```bash
openclaw skills list | grep -E "kalshalyst|kalshi-command|polymarket-command|prediction-market-arbiter|xpulse|portfolio-drift|market-morning-brief|personality-engine"
```

**The 10 stack skills:**

| Skill | Role | Required For |
|-------|------|-------------|
| Kalshalyst | Edge detection engine | Edge alerts, Morning Brief edges section |
| Kalshi Command Center | Trade execution | Executing on Kalshalyst recommendations |
| Polymarket Command Center | Market data | Arbiter comparisons, Morning Brief Polymarket section |
| Prediction Market Arbiter | Cross-platform divergences | Arbitrage alerts, Morning Brief divergences section |
| Xpulse | Social signal scanner | Signal alerts, Morning Brief X signals section |
| Portfolio Drift Monitor | Position monitoring | Drift alerts between briefs |
| Market Morning Brief | Daily digest | Consolidated morning/evening intelligence |
| Personality Engine | Agent behavior | Consistent voice across all output |
| Prediction Stack Orchestrator | Premium/experimental pipeline manager | Validation and execution routing |
| Prediction Stack Setup | Setup wizard | Validation, scheduling, delivery wiring |

**Minimum viable stack:** Kalshalyst + Kalshi Command Center + Market Morning Brief. These three give you edge detection, execution, and daily digest. Everything else enriches the system.

**Full stack:** All 10 skills. Morning Brief pulls from every cache and the orchestrator adds a premium/experimental automation path on top.

Install missing skills:
```bash
clawhub install <skill-name>
```

### Phase 2: API Key Configuration

Create or update `~/.openclaw/config.yaml`:

```yaml
# === REQUIRED ===

kalshi:
  enabled: true
  api_key_id: "YOUR_KALSHI_KEY_ID"
  private_key_file: "~/.openclaw/keys/kalshi-secret.pem"

# === REQUIRED FOR KALSHALYST ===
# Set as environment variable or in config:
# export ANTHROPIC_API_KEY="sk-ant-..."

# === OPTIONAL — ENHANCES EDGE QUALITY ===

polygon:
  api_key: "YOUR_POLYGON_KEY"   # Free tier at polygon.io

ollama:
  enabled: true                  # For Xpulse materiality gate + Kalshalyst fallback
  model: "qwen3:latest"
  timeout_seconds: 60

# === SKILL-SPECIFIC TUNING (sensible defaults shown) ===

kalshalyst:
  enabled: true
  check_interval_minutes: 60
  min_volume: 50
  min_days_to_close: 7
  max_days_to_close: 365
  max_markets_to_analyze: 50
  min_edge_pct: 3.0
  alert_edge_pct: 6.0

xpulse:
  enabled: true
  check_interval_minutes: 30
  topics:
    - "Trump tariff"
    - "Ukraine"
    - "inflation CPI"
    - "Fed rate decision"
  min_confidence: 0.7
  materiality_gate: true
  position_gate: true

portfolio_drift:
  threshold_pct: 5.0
  check_interval_minutes: 60
```

**Kalshi key setup** (if you don't have one yet):
1. Log in at https://kalshi.com
2. Go to Settings → API Keys
3. Generate a new key pair
4. Save the private key:
```bash
mkdir -p ~/.openclaw/keys
# Paste your private key into this file:
nano ~/.openclaw/keys/kalshi-secret.pem
chmod 600 ~/.openclaw/keys/kalshi-secret.pem
```

### Phase 2.5: Validate API Keys

**Before creating cron jobs, verify that all configured APIs are working.** This prevents hours of silent failures where the stack runs but can't reach its data sources.

Run the validation script:

```bash
python ~/skills/prediction-stack-setup/scripts/validate_setup.py
```

**Output Example:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prediction Stack API Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REQUIRED SERVICES (must pass for stack to function)
──────────────────────────────────────────────────────────────────────
✅ PASS Kalshi API             (REQUIRED)       (245ms)
✅ PASS Anthropic (Claude)     (REQUIRED)       (1320ms)

OPTIONAL SERVICES (enhance edge detection and resilience)
──────────────────────────────────────────────────────────────────────
✅ PASS Polygon.io API         (optional)       (180ms)
❌ FAIL Ollama (Qwen)          (optional)       (15ms)
   Error: Ollama not running on localhost:11434
✅ PASS Polymarket API         (optional)       (95ms)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Required: 2/2 passed
Optional: 2/3 passed

✅ All required services validated. Stack is ready to launch.
```

**What each validation tests:**

| Service | Required | Test | Failure Handling |
|---------|----------|------|------------------|
| **Kalshi** | Yes | `get_balance()` call | Blocks setup if auth fails |
| **Claude** | Yes | Simple completion call | Blocks setup if key invalid |
| **Polygon.io** | No | Public market status endpoint | Kalshalyst works without it |
| **Ollama/Qwen** | No | Model availability + inference | Kalshalyst uses Claude fallback |
| **Polymarket** | No | Public API endpoint access | Arbiter works without it |

**If validation fails on REQUIRED services:**

1. **Kalshi fails** — Check error message:
   - "Authentication failed": Verify key ID and private key file are correct at https://kalshi.com/settings/api
   - "Network error": Verify internet connectivity, check Kalshi status at status.kalshi.com
   - "File not found": Verify `private_key_file` path in config.yaml exists and is readable

2. **Claude fails** — Check error message:
   - "Invalid or expired API key": Generate a new key at https://console.anthropic.com/account/keys
   - "Network error": Verify internet connectivity
   - "Rate limited": Wait 60 seconds and retry

3. **Optional services fail** — This is OK. The stack will work but with reduced functionality:
   - Polygon.io missing: Kalshalyst estimates will lack news context
   - Ollama missing: Kalshalyst will use Claude for all estimates (higher cost)
   - Polymarket missing: Arbiter won't find cross-platform divergences

**To validate only specific services:**

```bash
# Test only Kalshi (useful for debugging)
python ~/skills/prediction-stack-setup/scripts/validate_setup.py --kalshi-only

# With detailed output showing live responses
python ~/skills/prediction-stack-setup/scripts/validate_setup.py --verbose
```

### Phase 3: iMessage Delivery Setup

The stack delivers alerts via iMessage through BlueBubbles. This requires:

1. **BlueBubbles** running on your Mac (https://bluebubbles.app)
2. **BlueBubbles password** set in OpenClaw config
3. **Your iMessage email handle** (the email registered with your Apple ID for iMessage)

**Configure BlueBubbles:**
```bash
# Set your BlueBubbles server password
openclaw config set channels.bluebubbles.password "YOUR_BB_PASSWORD"

# Restart gateway to pick up the change
openclaw gateway restart
```

**Test delivery:**
```bash
# Replace with YOUR iMessage email handle
openclaw message send --channel imessage --target "YOUR_IMESSAGE_EMAIL" --message "Prediction Stack is online."
```

If the message arrives on your phone, delivery is working. If not:

**Troubleshooting:**
- Verify BlueBubbles is running (check the app on your Mac)
- Verify Full Disk Access is granted to Terminal (System Settings → Privacy & Security → Full Disk Access)
- On macOS Tahoe+: use email handles, not phone numbers, for proactive sends
- Check gateway logs: `tail -50 ~/.openclaw/logs/gateway.log`
- Run diagnostics: `openclaw doctor`

### Phase 4: Create Scheduled Jobs

**Important:** Complete Phase 2.5 (API validation) before running these commands. Cron jobs will fail silently if APIs are misconfigured.

These cron jobs are the nervous system of the stack — they trigger skills on a schedule and deliver results to your phone. **Replace YOUR_IMESSAGE_EMAIL in every command below.**

```bash
# ═══════════════════════════════════════════════════════
# DAILY BRIEFS — The bookends of your trading day
# ═══════════════════════════════════════════════════════

# Morning Brief — 8:00 AM local time
# Compiles: Portfolio P&L + Kalshalyst edges + Arbiter divergences + Xpulse signals + Polymarket trending
openclaw cron add \
  --name "morning-brief" \
  --cron "0 8 * * *" \
  --tz "America/Los_Angeles" \
  --message "Run the Market Morning Brief skill. Compile the full morning digest — Kalshi portfolio P&L, top edges from Kalshalyst cache, cross-platform divergences from Arbiter cache, X signals from Xpulse cache, Polymarket trending. Format for iMessage (no markdown). Send the brief to the user." \
  --announce \
  --channel imessage \
  --to "YOUR_IMESSAGE_EMAIL" \
  --timeout-seconds 120

# Evening Brief — 6:00 PM local time
# Lighter summary: notable moves, new edges since morning, drift alerts
openclaw cron add \
  --name "evening-brief" \
  --cron "0 18 * * *" \
  --tz "America/Los_Angeles" \
  --message "Run the Market Morning Brief evening mode. Lightweight market summary — notable moves, any new Kalshalyst edges since morning, position drift alerts. Format for iMessage (no markdown). Send to the user." \
  --announce \
  --channel imessage \
  --to "YOUR_IMESSAGE_EMAIL" \
  --timeout-seconds 120

# ═══════════════════════════════════════════════════════
# EDGE SCANNING — Finding mispricings throughout the day
# ═══════════════════════════════════════════════════════

# Kalshalyst Edge Scan — Every 2 hours during market hours (8 AM - 8 PM)
# Only alerts on edges >= 6% with confidence >= 0.6. Writes cache silently otherwise.
openclaw cron add \
  --name "edge-scan" \
  --cron "0 8,10,12,14,16,18,20 * * *" \
  --tz "America/Los_Angeles" \
  --message "Run Kalshalyst edge scan. Only alert the user via iMessage if any market has edge >= 6% with confidence >= 0.6. If nothing meets threshold, write cache silently and do not send a message." \
  --announce \
  --channel imessage \
  --to "YOUR_IMESSAGE_EMAIL" \
  --timeout-seconds 180

# ═══════════════════════════════════════════════════════
# SIGNAL DETECTION — Social signals matched to positions
# ═══════════════════════════════════════════════════════

# Xpulse Social Signal Scan — Every 30 min during waking hours (8 AM - 10 PM)
# Only alerts when signal passes materiality gate AND matches an active position
openclaw cron add \
  --name "xpulse-scan" \
  --cron "*/30 8-22 * * *" \
  --tz "America/Los_Angeles" \
  --message "Run Xpulse scan on configured topics. Only alert the user via iMessage if a signal passes BOTH the materiality gate AND position matching. Silence is correct when nothing fires." \
  --announce \
  --channel imessage \
  --to "YOUR_IMESSAGE_EMAIL" \
  --timeout-seconds 90

# ═══════════════════════════════════════════════════════
# POSITION MONITORING — Catching drift between briefs
# ═══════════════════════════════════════════════════════

# Portfolio Drift Monitor — Hourly during market hours (9 AM - 8 PM)
# Alerts only when a position moves >= 5% since last snapshot
openclaw cron add \
  --name "drift-monitor" \
  --cron "0 9-20 * * *" \
  --tz "America/Los_Angeles" \
  --message "Run Portfolio Drift Monitor. Alert the user via iMessage only if any position has moved >= 5% since last snapshot. No alert if everything is stable." \
  --announce \
  --channel imessage \
  --to "YOUR_IMESSAGE_EMAIL" \
  --timeout-seconds 60

# ═══════════════════════════════════════════════════════
# CROSS-PLATFORM ARBITRAGE — Kalshi vs Polymarket pricing gaps
# ═══════════════════════════════════════════════════════

# Arbiter Cross-Platform Scan — 3x daily (9 AM, 1 PM, 5 PM)
# Alerts on divergences >= 10%. Writes all results to cache for Morning Brief.
openclaw cron add \
  --name "arbiter-scan" \
  --cron "0 9,13,17 * * *" \
  --tz "America/Los_Angeles" \
  --message "Run Prediction Market Arbiter. Scan for Kalshi vs Polymarket divergences. Alert the user via iMessage only if divergence >= 10% on a market with decent volume. Write all results to cache for Morning Brief regardless." \
  --announce \
  --channel imessage \
  --to "YOUR_IMESSAGE_EMAIL" \
  --timeout-seconds 120
```

**Verify all jobs:**
```bash
openclaw cron list
```

You should see 6 jobs: morning-brief, evening-brief, edge-scan, xpulse-scan, drift-monitor, arbiter-scan.

**Quick reference — what fires when:**

| Time | Job | What Happens |
|------|-----|-------------|
| 8:00 AM | morning-brief + edge-scan | Full digest + first edge scan of the day |
| 9:00 AM | drift-monitor + arbiter-scan | Position check + first arbitrage scan |
| 9:30 AM | xpulse-scan | Social signal check |
| 10:00 AM | edge-scan + drift-monitor + xpulse-scan | Edge + drift + signals |
| ... | (continues hourly/half-hourly) | |
| 5:00 PM | arbiter-scan | Last arbitrage scan |
| 6:00 PM | evening-brief | Evening summary |
| 8:00 PM | edge-scan + drift-monitor | Last edge scan + drift check |
| 10:00 PM | xpulse-scan | Last signal scan (then quiet until 8 AM) |

### Phase 5: Enable Heartbeat

Heartbeat gives your agent ambient awareness between scheduled jobs. Every 30 minutes during active hours, the agent checks if anything needs attention.

```bash
openclaw config set agents.defaults.heartbeat.every "30m"
openclaw config set agents.defaults.heartbeat.activeHours.start "08:00"
openclaw config set agents.defaults.heartbeat.activeHours.end "22:00"
openclaw system heartbeat enable
openclaw gateway restart
```

**Optional — configure HEARTBEAT.md** for proactive checks between scans:

Edit `~/.openclaw/workspace/HEARTBEAT.md`:
```markdown
# HEARTBEAT.md

Check for new Kalshalyst edges in cache that haven't been alerted yet.
Check for portfolio drift events that fired since last heartbeat.
If anything is worth telling the user, send it via iMessage. Otherwise, HEARTBEAT_OK.
```

### Phase 6: Verify Everything

```bash
# Check system status
openclaw status

# List all cron jobs
openclaw cron list

# Check heartbeat
openclaw system heartbeat last

# Run a manual test (triggers edge scan immediately)
openclaw cron run edge-scan

# Check gateway logs for errors
tail -20 ~/.openclaw/logs/gateway.log
```

If the manual edge scan delivers results to your phone (or runs silently because nothing met threshold), the stack is fully operational.

## Post-Setup: What to Expect

### First 24 Hours
- **Immediately:** Xpulse fires every 30 min. Most runs will be silent (nothing passes materiality gate). This is correct — silence means the filter is working.
- **Next morning at 8 AM:** First Morning Brief arrives. If other skill caches are empty (first run), sections will show "unavailable" — they'll populate after the first scan cycle.
- **By end of day 1:** All caches populated. Evening Brief will have a full picture.

### Ongoing
- **Most alerts are silence.** This is by design. The stack is built to prevent notification fatigue. You'll get 2-5 actionable alerts per day, not 50.
- **Morning Brief is your daily touchpoint.** 30-second scan of everything that matters.
- **Edge alerts are the money.** When Kalshalyst fires with >= 6% edge, that's your signal to look at the trade.

### Tuning
After a week of operation, you may want to adjust:

**Alert thresholds** (in cron job messages or config.yaml):
- Raise `alert_edge_pct` from 6% to 8% if too many low-quality alerts
- Lower to 4% if you're not seeing enough opportunities
- Adjust drift threshold from 5% to 3% (more sensitive) or 10% (less noise)

**Schedule frequency:**
- Reduce edge-scan to 3x daily if API costs are a concern
- Increase xpulse to every 15 min if you trade breaking news heavily
- Add weekend scanning by changing cron expressions

**Xpulse topics** (in config.yaml):
- Add topics matching your active positions
- Remove topics you're no longer trading

To update a cron job:
```bash
# List jobs to get the ID
openclaw cron list

# Update the schedule or message
openclaw cron update <JOB_ID> --cron "new expression"
```

## Reconfiguration

### Change Delivery Target
```bash
# Update all cron jobs to a new target
openclaw cron list  # get all job IDs
openclaw cron update <ID> --to "new.email@example.com"
# Repeat for each job
```

### Change Timezone
```bash
openclaw cron update <ID> --tz "America/New_York"
# Repeat for each job
```

### Disable a Job Temporarily
```bash
openclaw cron disable <ID>
# Re-enable later:
openclaw cron enable <ID>
```

### Full Reset
```bash
# Remove all cron jobs
openclaw cron list  # note all IDs
openclaw cron remove <ID>  # for each job

# Re-run setup from Phase 4
```

## How the Skills Connect (System Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    SCHEDULED JOBS (Cron)                     │
│  edge-scan → xpulse-scan → drift-monitor → arbiter-scan    │
│  morning-brief (8AM) ←── reads all caches ──→ evening-brief │
└─────────────┬───────────────────────────────────┬───────────┘
              │                                   │
              ▼                                   ▼
┌─────────────────────────┐   ┌───────────────────────────────┐
│    INTELLIGENCE LAYER   │   │      DELIVERY LAYER           │
│                         │   │                               │
│  Kalshalyst             │   │  BlueBubbles → iMessage       │
│    └→ .kalshi_research  │   │  openclaw send → your phone   │
│       _cache.json       │   │                               │
│                         │   │  Heartbeat (30m ambient)      │
│  Arbiter                │   │    └→ checks caches           │
│    └→ .crossplatform    │   │    └→ alerts if needed        │
│       _divergences.json │   │                               │
│                         │   └───────────────────────────────┘
│  Xpulse                 │
│    └→ .x_signal         │   ┌───────────────────────────────┐
│       _cache.json       │   │      EXECUTION LAYER          │
│                         │   │                               │
│  Portfolio Drift        │   │  Kalshi Command Center        │
│    └→ snapshot +        │   │    └→ trade on edges          │
│       threshold alerts  │   │                               │
│                         │   │  Polymarket Command Center    │
│  Morning Brief          │   │    └→ market data for Arbiter │
│    └→ reads all caches  │   │                               │
│    └→ consolidated push │   └───────────────────────────────┘
│                         │
│  Personality Engine     │   ┌───────────────────────────────┐
│    └→ wraps all output  │   │      DATA SOURCES             │
│                         │   │                               │
└─────────────────────────┘   │  Kalshi API (free)            │
                              │  Polymarket Gamma API (free)   │
                              │  Polygon.io (free tier)        │
                              │  DuckDuckGo (free, via Xpulse) │
                              │  Ollama/Qwen (free, local)     │
                              │  Anthropic Claude (paid)        │
                              └───────────────────────────────┘
```

**Data flow:** Skills write JSON cache files. Morning Brief reads them. Cron jobs trigger everything. BlueBubbles delivers to iMessage. No direct dependencies between skills — install any subset and each works standalone.

## Cost Summary

| Component | Cost | Notes |
|-----------|------|-------|
| Kalshi API | Free | Unlimited reads |
| Polymarket API | Free | Public, no auth |
| Polygon.io | Free | Free tier sufficient |
| DuckDuckGo | Free | Via Xpulse |
| Ollama/Qwen | Free | Local inference |
| Claude Sonnet | Variable | Depends on model, prompt size, and scan frequency |
| BlueBubbles | Free | Self-hosted on Mac |
| **Total** | **Variable** | Claude is the only paid dependency in the public reference path |

## Troubleshooting

### No messages arriving
1. Test send: `openclaw message send --channel imessage --target "YOUR_EMAIL" --message "test"`
2. Check BB is running (BlueBubbles app on Mac)
3. Check FDA: System Settings → Privacy & Security → Full Disk Access → Terminal
4. Check gateway: `tail -50 ~/.openclaw/logs/gateway.log`
5. On macOS Tahoe+: use email handles, not phone numbers

### Cron jobs not firing
1. Verify gateway is running: `openclaw status`
2. List jobs: `openclaw cron list` (check "Next" column)
3. Manual trigger: `openclaw cron run <job-name>`
4. Check logs: `~/.openclaw/logs/gateway.log`

### Skills not finding data
1. **First, run the validation script** to catch API issues early:
   ```bash
   python ~/skills/prediction-stack-setup/scripts/validate_setup.py --verbose
   ```
   This will identify which API is misconfigured.

2. Check API keys: verify `~/.openclaw/config.yaml` has valid credentials
3. Test Kalshi: `openclaw message send --channel imessage --target "YOUR_EMAIL" --message "Run Kalshi Command Center: show my portfolio"`
4. Check Ollama (for Xpulse): `ollama list` should show qwen3:latest

### Morning Brief shows "unavailable" sections
This is normal on first run — caches haven't been populated yet. After one full scan cycle (edge-scan + arbiter-scan + xpulse-scan), all caches will exist and Morning Brief will show full data.

## Stack Skills Reference

For detailed documentation on each skill, read its SKILL.md:

- **Kalshalyst** — Contrarian edge detection. The intelligence engine.
- **Kalshi Command Center** — Portfolio, scanning, trade execution, risk management.
- **Polymarket Command Center** — Trending markets, odds, search, watchlists.
- **Prediction Market Arbiter** — Cross-platform divergence scanner.
- **Xpulse** — X/Twitter social signal scanner with materiality gate.
- **Portfolio Drift Monitor** — Position drift alerts.
- **Market Morning Brief** — Daily morning/evening intelligence digest.
- **Personality Engine** — 6-system behavior framework for consistent agent voice.


---

## Feedback & Issues

Found a bug? Have a feature request? Want to share results?

- **GitHub Issues**: [github.com/kingmadellc/openclaw-prediction-stack/issues](https://github.com/kingmadellc/openclaw-prediction-stack/issues)
- **X/Twitter**: [@KingMadeLLC](https://x.com/KingMadeLLC)

Part of the **OpenClaw Prediction Stack** — the first prediction market skill suite on ClawHub.
