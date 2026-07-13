---
name: revenue-tracker
description: >
  Live revenue tracking system for autonomous agents. Tracks MRR, assets,
  trades, acquisition channels, and learning metrics in real time. Generates
  visual ASCII dashboards, progress charts, and an auto-refreshing HTML
  dashboard. After every revenue event, outputs structured instructions for
  the agent to update Google Sheets (via gog), Notion (via virtual-desktop),
  or falls back to local HTML. The agent sends Telegram alerts on milestones
  and anomalies via its own Telegram integration.
  Use when the agent needs to record revenue events, track progress toward
  financial goals, generate visual reports, or monitor all income streams
  simultaneously.
version: 1.1.0
author: Wesley Armando (Georges Andronescu)
license: MIT
metadata:
  openclaw:
    emoji: "📈"
    security_level: L2
    always: false
    required_paths:
      read:
        - /workspace/revenue/data/revenue_state.json
        - /workspace/revenue/data/events.jsonl
        - /workspace/revenue/data/assets.json
        - /workspace/revenue/data/goals.json
        - /workspace/revenue/reports/
        - /workspace/.learnings/LEARNINGS.md
      write:
        - /workspace/revenue/data/revenue_state.json
        - /workspace/revenue/data/events.jsonl
        - /workspace/revenue/data/assets.json
        - /workspace/revenue/data/goals.json
        - /workspace/revenue/reports/dashboard.html
        - /workspace/revenue/reports/
        - /workspace/.learnings/LEARNINGS.md
        - /workspace/AUDIT.md
    network_behavior:
      makes_requests: false
      uses_agent_telegram: true
      telegram_note: >
        The agent (not this script) sends Telegram alerts when milestones
        or anomalies are detected. The script outputs structured dashboard
        update instructions — the agent reads them and sends alerts via
        its own Telegram integration.
    requires:
      bins:
        - python3
      skills:
        - ceo-master
      optional_skills:
        - wesley-web-operator
        - virtual-desktop
---

# Revenue Tracker — Live Financial Intelligence

> "What gets measured gets managed." — Peter Drucker
> "Revenue is a fact. Everything else is an opinion." — Agent principle

This skill is the financial nervous system of the agent ecosystem.
Every euro that comes in — or should have come in — is tracked,
visualized, and analyzed. The agent never flies blind on revenue.

---

## Why This Skill Exists

```
WITHOUT this skill:
  CEO-master asks "what's our MRR?" → Agent guesses
  A trading strategy underperforms for 3 weeks → Nobody notices
  Acquisition channel ROI drops → Invisible until it's too late
  Principal asks for progress → Agent can't show a chart

WITH this skill:
  Every revenue event logged the moment it happens
  Visual progress toward every financial goal
  Automatic anomaly detection across all income streams
  Weekly HTML report with charts and metrics
  Telegram alert the moment a milestone is crossed
```

---

## Revenue Streams Tracked

```
STREAM 1 — Subscriptions / SaaS
  Monthly recurring revenue from products and services
  Tracks: MRR, ARR, new subs, churn, expansion, NRR

STREAM 2 — Trading (Crypto + Polymarket)
  Realized PnL from all automated trading activity
  Tracks: daily PnL, win rate, best strategy, drawdown

STREAM 3 — Content / Digital Products
  One-time and recurring revenue from content, courses, signals
  Tracks: Gumroad sales, newsletter revenue, product launches

STREAM 4 — Services / Consulting
  B2B project revenue, one-time invoices
  Tracks: project revenue, average deal size, pipeline value

STREAM 5 — Affiliate / Referral
  Commission revenue from referred products or services
  Tracks: clicks, conversions, commission earned
```

---

## Core Operations

### RECORD — Log a revenue event

```
Triggers (automatic — called by other skills):
  → acquisition-master closes a sale
  → crypto-executor closes a profitable trade
  → content post generates a Gumroad sale
  → invoice paid for a service project

Command:
  python3 revenue_tracker.py record \
    --stream subscriptions \
    --amount 97 \
    --currency EUR \
    --description "New subscriber — Jean Dupont — VIP signals" \
    --client-id "jean-dupont" \
    --type new_mrr

Streams: subscriptions | trading | content | services | affiliate
Types:   new_mrr | churn | expansion | one_time | trade_win |
         trade_loss | refund | affiliate_commission
```

### DASHBOARD — Visual ASCII dashboard

```
Triggers:
  → Every Monday morning before CEO weekly report
  → On-demand: "show me the revenue dashboard"
  → After any significant revenue event

Command:
  python3 revenue_tracker.py dashboard
```

### REPORT — Generate HTML visual report

```
Triggers:
  → Weekly (sent to Telegram as summary + link)
  → Monthly (full report with charts)
  → On-demand from principal

Command:
  python3 revenue_tracker.py report \
    --period week    (or: month | quarter | all)
  python3 revenue_tracker.py report \
    --period month --format html
```

### GOAL — Track progress toward financial targets

```
Command:
  python3 revenue_tracker.py goal \
    --set "mrr_10k" --target 10000 --deadline "2026-06-30"

  python3 revenue_tracker.py goal --list
```

### ASSET — Track non-revenue assets

```
Command:
  python3 revenue_tracker.py asset \
    --action add \
    --name "Binance Trading Capital" \
    --value 500 \
    --currency USDT

  python3 revenue_tracker.py asset --list
```

### LEARN — Log a revenue learning

```
Triggers:
  → After any campaign result (what worked, what didn't)
  → After a trading strategy review
  → After a milestone reached or missed

Command:
  python3 revenue_tracker.py learn \
    --category acquisition \
    --insight "Cold email to CTOs at Series A gets 14% reply rate" \
    --impact high
```

---

## Visual Dashboard — ASCII Output

```
╔══════════════════════════════════════════════════════════════╗
║          📈 REVENUE DASHBOARD — 2026-03-16                   ║
╠══════════════════════════════════════════════════════════════╣
║  MRR      €4,200  ▲ +35.5% vs last month                    ║
║  ARR      €50,400                                            ║
║  Phase    1 — Proof of Concept                               ║
╠══════════════════════════════════════════════════════════════╣
║  PROGRESS TOWARD GOALS                                       ║
║                                                              ║
║  €10K MRR    ████████████░░░░░░░░░░  42.0%  est. 21 wks     ║
║  €50K MRR    ██░░░░░░░░░░░░░░░░░░░░   8.4%  est. 68 wks     ║
║  €1M ARR     █░░░░░░░░░░░░░░░░░░░░░   5.0%  est. 2+ yrs     ║
╠══════════════════════════════════════════════════════════════╣
║  REVENUE BY STREAM (this month)                              ║
║                                                              ║
║  Subscriptions  ████████████████░░░░  €3,200  76.2%         ║
║  Trading        ████░░░░░░░░░░░░░░░░    €650  15.5%         ║
║  Content        ██░░░░░░░░░░░░░░░░░░    €350   8.3%         ║
║  Services       ░░░░░░░░░░░░░░░░░░░░      €0   0.0%         ║
╠══════════════════════════════════════════════════════════════╣
║  MRR TREND (last 8 weeks)                                    ║
║                                                              ║
║  5K ┤                                              ╭─        ║
║  4K ┤                                         ╭───╯          ║
║  3K ┤                               ╭────────╯              ║
║  2K ┤                   ╭──────────╯                        ║
║  1K ┤       ╭──────────╯                                    ║
║   0 ┼───────┴──────────────────────────────────────         ║
║      w1     w2     w3     w4     w5     w6     w7     w8     ║
╠══════════════════════════════════════════════════════════════╣
║  KEY METRICS                                                 ║
║  CAC €18    LTV €2,061    LTV/CAC 116x    Churn 5.7%        ║
╠══════════════════════════════════════════════════════════════╣
║  TOP LEARNINGS THIS WEEK                                     ║
║  ✅ Cold email to CTOs → 14% reply rate (best ever)         ║
║  ✅ BTC momentum 4h → +3.2% avg (5 trades)                  ║
║  ⚠️  Paid ads negative ROI → stopped                         ║
╚══════════════════════════════════════════════════════════════╝
```

---

## MRR Trend Chart — ASCII Sparkline

The agent generates inline sparklines for Telegram:

```
MRR last 8 weeks: ▁▂▃▄▅▆▇█  (+35.5% this month)
Trading PnL week: ▄▆▃▇▂▅▄▆  (+€127 net)
```

---

## Milestone Alert System

The agent sends a Telegram alert the moment a milestone is crossed.

```
REVENUE MILESTONES (automatic alerts):
  🎯 First €1 earned
  🎯 First €100 MRR
  🎯 First €1,000 MRR
  🎯 First €5,000 MRR
  🎯 First €10,000 MRR  ← Phase 1 → Phase 2
  🎯 First €50,000 MRR  ← Phase 2 → Phase 3
  🎯 First paying customer
  🎯 First 10 paying customers
  🎯 First 100 paying customers

ANOMALY ALERTS (automatic):
  🔴 MRR drops > 10% week over week
  🔴 3+ churns in 24 hours
  🔴 Trading drawdown > 15% of capital
  🟡 No new revenue for 7 days
  🟡 Best acquisition channel ROI drops > 30%

Telegram format:
  "🎯 MILESTONE: First €10K MRR reached! 
   Phase 1 complete → entering Phase 2.
   Time taken: 47 days from first customer."
```

---

## Automatic Integration with Other Skills

```
acquisition-master fires on sale:
  → revenue_tracker.py record --stream subscriptions --type new_mrr

acquisition-master fires on churn:
  → revenue_tracker.py record --stream subscriptions --type churn

crypto-executor fires on trade close:
  → revenue_tracker.py record --stream trading --type trade_win/trade_loss

agent-shark-mindset fires on content sale:
  → revenue_tracker.py record --stream content --type one_time

ceo-master reads for weekly report:
  → revenue_tracker.py dashboard
  → revenue_tracker.py report --period week --format json

memory-manager reads on recall:
  → revenue context loaded per client and per project
```

---

## HTML Report — Visual Output

Weekly HTML report saved to `/workspace/revenue/reports/YYYY-MM-DD.html`.

Contains:
```
- MRR trend line chart (8 weeks)
- Revenue by stream pie chart
- Goal progress bars (all active goals)
- Top 5 clients by revenue
- Top 3 trades by PnL
- Learning log for the week
- Anomalies detected
- Next week forecast (linear extrapolation)
```

The agent can send the report path via Telegram so the principal
can open it directly in a browser.

---

## Learning Log — Revenue Intelligence

Every revenue lesson is logged with impact level and category.

```
/workspace/revenue/data/learnings.jsonl

Format per entry:
{
  "date": "2026-03-16",
  "category": "acquisition",
  "insight": "Cold email to CTOs at Series A gets 14% reply rate",
  "impact": "high",
  "stream": "subscriptions",
  "action": "double cold email volume targeting Series A CTOs"
}

Categories: acquisition | trading | content | retention | pricing | product
Impact:     high | medium | low
```

The agent reviews all learnings every Monday and includes the
top 3 insights in the weekly CEO report.

---

## Auto-Update Dashboard — After Every Revenue Event

Every time the agent records a revenue event, the script automatically:

```
1. Updates /workspace/revenue/reports/dashboard.html
   → Dark-mode visual dashboard with KPI cards, stream bars,
     goal progress bars, and recent events table
   → Auto-refreshes every 60 seconds in the browser
   → Always available — no external dependencies

2. Outputs structured update instructions for the agent
   → Agent executes in priority order:

   PRIORITY 1 — Google Sheets (via wesley-web-operator / gog)
     Sheet: "Veritas Revenue Tracker"
     Tab "Events"    → append new event row
     Tab "Dashboard" → update MRR, ARR, Total, Customers, Phase cells

   PRIORITY 2 — Notion (via virtual-desktop, if Sheets unavailable)
     Database: "Revenue Tracker"
     → Create new entry with event fields
     → Update Summary page KPIs

   PRIORITY 3 — HTML local dashboard (always generated, zero deps)
     File: /workspace/revenue/reports/dashboard.html
     → Automatically updated by the script itself
```

**Google Sheets tab structure** (agent creates on first use):

```
Tab "Events":
  Date | Stream | Type | Amount (€) | Description | MRR after | Total after

Tab "Dashboard":
  B2 = MRR current     B3 = ARR
  B4 = Total all time  B5 = Active customers
  B6 = Current phase   B7 = MRR growth % vs last month

Tab "By Stream":
  One row per stream — MRR contribution + % share

Tab "Goals":
  Goal name | Target | Current | % progress | Deadline | Est. weeks left
```

---

## Weekly Revenue Routine

```
MONDAY 07:00
  1. Run dashboard → parse output
  2. Generate weekly report (HTML)
  3. Extract top 3 revenue learnings
  4. Check for anomalies
  5. Update ceo-master metrics_data.json with fresh revenue data
  6. Send Telegram summary

DAILY (after any revenue event)
  1. Record event immediately
  2. Check if milestone triggered → alert if yes
  3. Check anomalies → alert if detected

FRIDAY 17:00
  1. Weekly reconciliation — cross-check all streams
  2. Log 1 learning per active stream
  3. Update asset valuations (trading capital mark-to-market)
```

---

## Workspace Structure

```
/workspace/revenue/
├── data/
│   ├── revenue_state.json   ← current MRR, totals, last updated
│   ├── events.jsonl         ← append-only log of all revenue events
│   ├── assets.json          ← non-revenue assets (trading capital, etc.)
│   ├── goals.json           ← active financial goals + progress
│   └── learnings.jsonl      ← revenue intelligence log
├── reports/
│   ├── 2026-03-16.html      ← weekly HTML reports
│   └── ...
└── scripts/
    └── revenue_tracker.py   ← CLI tool for all operations
```

---

## Error Handling

```
ERROR: revenue_state.json not found
  Cause:  First run
  Action: Run revenue_tracker.py --init
  Log:    AUDIT.md → "Revenue tracker initialized [date]"

ERROR: events.jsonl corrupted (partial write)
  Cause:  Process killed mid-write
  Action: Truncate last incomplete line, rebuild state from clean events
  Log:    ERRORS.md → "events.jsonl repaired [date]"

ERROR: Negative MRR calculated
  Cause:  More churn events than new MRR (data entry error)
  Action: Flag anomaly, do not update state, alert principal
  Log:    ERRORS.md → "Negative MRR detected — manual review needed"
          Telegram: 🔴 "Revenue anomaly: MRR calculation negative — check data"

ERROR: Goal deadline passed without reaching target
  Cause:  Target missed
  Action: Mark goal as "missed", log lesson, propose new target
  Log:    LEARNINGS.md → "Goal missed: [name] — [reason]"

ERROR: HTML report generation fails
  Cause:  No events in period / empty data
  Action: Generate minimal report with "no data" message
  Log:    AUDIT.md → "Empty report generated [date]"
```
