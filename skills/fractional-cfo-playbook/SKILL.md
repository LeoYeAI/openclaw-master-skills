---
name: fractional-cfo-playbook
description: >
  Complete operational playbook for Fractional CFO engagements. Covers client onboarding financial
  assessment, monthly close cadence, board-ready reporting packages, cash flow management, strategic
  financial advisory, and engagement scope templates. Use when setting up or running a Fractional CFO
  service, onboarding a new client, preparing monthly CFO deliverables, or advising on financial
  strategy as an outsourced finance executive.
  NOT for: building financial models from scratch (use startup-financial-model), bookkeeping or
  transaction recording (use qbo-automation), tax filing preparation (PTIN-required service), or
  one-time financial analysis without an ongoing advisory context.
version: 1.0.0
author: PrecisionLedger
tags:
  - fractional-cfo
  - advisory
  - finance
  - reporting
  - strategy
  - client-management
---

# Fractional CFO Playbook

The complete operating guide for running Fractional CFO engagements — from first call to ongoing
monthly value delivery. This skill encodes PrecisionLedger's methodology for outsourced finance
executive services.

---

## When to Use This Skill

**Trigger phrases:**
- "Set up fractional CFO engagement for [client]"
- "What should I deliver as fractional CFO this month?"
- "Prepare the monthly CFO package for [client]"
- "New fractional CFO client — what do we need?"
- "Client wants board-ready financials"
- "CFO advisory scope for [stage/industry]"
- "Cash flow is tight — what does the CFO do?"

**NOT for:**
- Building a full 3-statement model from scratch → use `startup-financial-model`
- Bookkeeping, reconciliation, or data entry → use `qbo-automation`
- Tax return preparation or filings → PTIN-required, escalate to Irfan
- One-time financial analysis without CFO context → use `financial-analysis-agent`
- Cap table and equity management → use `cap-table-manager`

---

## Engagement Tiers

Define scope before starting. Three standard tiers:

| Tier | Hours/Month | Deliverables | Price Range | Best For |
|---|---|---|---|---|
| **Starter** | 5–8 hrs | Monthly close review, cash flow report, 1 strategy call | $1,500–$2,500/mo | Pre-revenue to $500K ARR |
| **Growth** | 12–20 hrs | Full reporting package, KPI dashboard, board prep, 2 calls | $3,500–$6,000/mo | $500K–$5M ARR |
| **Executive** | 20–40 hrs | All of Growth + fundraising support, audit prep, team mgmt | $6,000–$15,000/mo | $5M+ ARR or fundraising |

---

## Phase 1: Client Onboarding (Week 1–2)

### Financial Assessment Checklist

```
□ ACCOUNTING SYSTEMS
  □ Access to QBO / Xero / NetSuite granted
  □ Chart of accounts reviewed — gaps or misclassifications noted
  □ Bank feeds connected and reconciled YTD
  □ Historical period reviewed (12–24 months minimum)

□ FINANCIAL HEALTH SNAPSHOT
  □ Trailing 12-month P&L reviewed
  □ Balance sheet reviewed — any red flags?
  □ Cash flow statement reviewed (or reconstructed if missing)
  □ AR aging report pulled — any collection issues?
  □ AP aging report pulled — any payables over 60 days?

□ COMPLIANCE & STRUCTURE
  □ Entity structure confirmed (LLC, C-corp, S-corp?)
  □ Tax returns reviewed (last 2 years if available)
  □ Active contracts list obtained (leases, debt, subscriptions)
  □ Payroll provider confirmed (Gusto, ADP, etc.)
  □ Bank accounts and signers list obtained

□ METRICS & BENCHMARKS
  □ Gross margin calculated and benchmarked to industry
  □ Burn rate established (if pre-profit)
  □ Revenue concentration — top 5 clients as % of revenue?
  □ Key financial KPIs identified and baseline set
```

### Onboarding Output: Financial Diagnostic Report

Produce a 1-page diagnostic for the client:

```
FINANCIAL DIAGNOSTIC SUMMARY
Client: [Name] | Date: [Date] | Prepared by: PrecisionLedger / Sam Ledger

FINANCIAL HEALTH SCORE: [Red/Yellow/Green per category]

Category          Status    Notes
────────────────────────────────────────────────
Cash Position     🟡 Yellow  $180K — 4 months runway at current burn
Revenue           🟢 Green   $42K MRR, growing 8% MoM
Gross Margin      🔴 Red     38% — below SaaS benchmark of 60–70%
AR Aging          🟡 Yellow  $28K over 60 days — 3 accounts to address
AP/Payables       🟢 Green   Current, no overdue
Bookkeeping       🟡 Yellow  2 months behind — catching up underway
Compliance        🟢 Green   Tax returns current, payroll compliant

TOP 3 PRIORITIES THIS QUARTER:
1. Improve gross margin: audit COGS, renegotiate vendor contracts
2. Accelerate AR collections: implement net-30 enforcement + follow-up workflow
3. Extend runway: reduce discretionary spend by ~$15K/month

UPCOMING DEADLINES:
• March 15 — Q4 estimated tax payment
• April 15 — Annual tax filing or extension
• May 1 — Lease renewal decision required
```

---

## Phase 2: Monthly Close Cadence

### Close Calendar (Standard Timeline)

```
Day 1–3 (after month end):
  □ Bank reconciliation completed for all accounts
  □ Credit card transactions categorized
  □ Payroll entries posted and reconciled

Day 4–7:
  □ Revenue recognized per schedule
  □ Prepaid expense amortization entries posted
  □ Accounts receivable invoices confirmed sent
  □ Accruals posted (liabilities incurred but not invoiced)

Day 8–10:
  □ Unadjusted trial balance reviewed
  □ Intercompany eliminations (if applicable)
  □ Depreciation/amortization posted

Day 11–15:
  □ Final trial balance locked
  □ Financial statements drafted
  □ Flux analysis completed (month-over-month variance review)
  □ CFO package assembled and reviewed

Day 15–20:
  □ CFO package delivered to client
  □ Monthly strategy call scheduled
  □ Prior month action items reviewed
```

### Month-End Flux Analysis

Review every line item variance > 10% or > $5K:

```
FLUX ANALYSIS TEMPLATE

Account           Prior Mo    Current Mo    $ Change    % Change    Explanation
────────────────────────────────────────────────────────────────────────────────
Revenue           $95,000     $103,000      +$8,000     +8.4%       New client Jan 15
COGS              $32,000     $39,000       +$7,000     +21.9%      ⚠️ Investigate
Payroll           $48,000     $53,000       +$5,000     +10.4%      New hire Feb 1
Software Tools    $4,200      $6,800        +$2,600     +61.9%      ⚠️ New subscriptions
```

Flag any unexplained variance > 15% for discussion on the monthly call.

---

## Phase 3: Monthly CFO Package

### Standard Deliverables

Every month, deliver a client-ready package containing:

#### 1. Executive Summary (1 page)
```
[CLIENT NAME] — MONTHLY CFO BRIEF
Month: [Month Year] | Prepared: [Date]

HEADLINE NUMBERS
  Revenue:      $103,000  (+8.4% vs prior month)
  Gross Profit: $64,000   (62% margin — on target)
  Net Income:   ($12,000) (investing in growth)
  Cash Balance: $285,000  (6.2 months runway)

WINS THIS MONTH
  • Closed largest deal to date — $12K MRR contract
  • COGS margin improved 3 points after AWS renegotiation
  • Collected $18K of aged AR

CONCERNS / WATCH ITEMS
  • Software spend up 62% — conducting audit next week
  • Two invoices 45+ days overdue — escalating collections
  • Runway tightening — fundraise timeline decision needed by Q2

ACTION ITEMS FOR NEXT MONTH
  □ Software audit — identify and cancel unused tools [CFO]
  □ Collections call on Acme Corp $8,200 invoice [Ops]
  □ Series A readiness checklist review [Founder + CFO]
```

#### 2. Financial Statements (3 pages)
- Income Statement: Month + YTD, vs. prior month, vs. budget
- Balance Sheet: Current month vs. prior month
- Cash Flow Statement: Simplified operating/investing/financing

#### 3. KPI Dashboard
```
METRIC                 CURRENT    PRIOR MO    TARGET    STATUS
──────────────────────────────────────────────────────────────
MRR                    $103,000   $95,000     $100,000  🟢 Ahead
MRR Growth (MoM)       8.4%       6.2%        7%        🟢 On Track
Gross Margin           62%        58%         65%       🟡 Improving
Customer Count         47         43          50        🟡 Close
Cash Runway (months)   6.2        7.1         6+        🟡 Watch
AR Days Outstanding    38 days    31 days     30 days   🟡 Watch
Burn Rate (net)        $12,000    $8,000      <$15,000  🟢 OK
Payroll as % Rev       51%        50%         <55%      🟢 OK
```

#### 4. Cash Flow Forecast (13-week)
```
13-WEEK CASH FLOW FORECAST
Week   Start Cash   Inflows    Outflows   End Cash    Notes
─────────────────────────────────────────────────────────────
Wk 1   $285,000     $35,000    $42,000    $278,000    Payroll Fri
Wk 2   $278,000     $18,000    $8,000     $288,000    AR collect
Wk 3   $288,000     $22,000    $15,000    $295,000
...
Wk 13  $XXX,000     ...        ...        $XXX,000    Projected
```

---

## Phase 4: Strategic Advisory Functions

### Cash Flow Management

**Weekly cash flow discipline:**
```
1. Monitor bank balance every Monday
2. Review AP due this week — approve payment run
3. Flag any AR 30+ days overdue for follow-up
4. Update 13-week forecast if assumptions change
5. Escalate if projected cash < 3 months runway
```

**Cash flow levers (when runway is tight):**
```
ACCELERATE INFLOWS:
  □ Offer early payment discount (2/10 net 30) for key AR
  □ Move to upfront/annual billing for new clients
  □ Collect deposits on new projects
  □ Line of credit draw if available

DEFER OUTFLOWS:
  □ Negotiate extended terms with vendors (net 60–90)
  □ Defer non-critical hiring 30–60 days
  □ Pause discretionary spend categories
  □ Renegotiate SaaS contracts to annual prepay for discount

BRIDGE OPTIONS:
  □ Revenue-based financing (Clearco, Pipe, Arc)
  □ SBIC / SBA loan for established businesses
  □ Convertible note bridge from existing investors
  □ Founder personal bridge (document properly)
```

### Fundraising Support

When a client is raising capital:

```
FUNDRAISING READINESS CHECKLIST (CFO Role)

□ FINANCIAL DATA ROOM
  □ 3 years historical financials (audited if available)
  □ Current YTD financials (within 30 days)
  □ 3-year financial model (base/bear/bull)
  □ Unit economics summary (LTV, CAC, payback period)
  □ Revenue cohort analysis
  □ Cap table (current + pro forma post-raise)

□ METRICS PACKAGE
  □ MRR/ARR waterfall (12 months)
  □ Gross margin trend
  □ Burn and runway calculation
  □ Net Revenue Retention
  □ Customer count and churn

□ DILIGENCE SUPPORT
  □ Bank statements (12–24 months)
  □ Payroll records
  □ Material contracts list
  □ IP and asset register
  □ Outstanding liabilities schedule

□ INVESTOR NARRATIVE
  □ Financial story: how does the business make money?
  □ Why the numbers look the way they do
  □ What this raise funds and for how long
  □ Key milestones unlocked by this capital
```

### Board Meeting Preparation

Monthly or quarterly board package:

```
BOARD PACKAGE STRUCTURE

1. EXECUTIVE SUMMARY (1 page)
   - Revenue, growth, margin, cash — vs. prior period and budget
   - Top 3 wins, top 3 challenges

2. FINANCIAL STATEMENTS (3 pages)
   - P&L with budget variance column
   - Balance sheet
   - Cash flow summary

3. KPI SCORECARD (1 page)
   - All agreed board-level KPIs in one table
   - Red/Yellow/Green status

4. BUDGET VS. ACTUAL (1 page)
   - Month and YTD variance
   - Explanation for significant variances

5. UPDATED FORECAST (1 page)
   - Revised full-year projection
   - Key assumption changes since last board meeting

6. APPENDIX
   - Department-level P&L breakdowns
   - Headcount report
   - Pipeline/bookings summary (if available from sales)
```

---

## Engagement Management

### Scope of Work Template

```
FRACTIONAL CFO ENGAGEMENT — SCOPE OF WORK

Client: [Client Name]
Effective Date: [Date]
Tier: Growth ($4,500/month, 15 hours/month)

MONTHLY DELIVERABLES:
1. Monthly financial close oversight (Days 1–15)
2. Financial statements (P&L, Balance Sheet, Cash Flow)
3. KPI dashboard update
4. 13-week cash flow forecast
5. Monthly CFO brief (executive summary)
6. Two 60-minute strategy calls per month

QUARTERLY DELIVERABLES:
7. Updated 12-month financial model
8. Board package preparation
9. Quarterly business review presentation

ANNUAL DELIVERABLES:
10. Annual budget and operating plan
11. Year-end close support and audit readiness
12. Annual financial strategy review

OUT OF SCOPE (separate engagement or referral):
• Tax return preparation and filing
• Bookkeeping and daily transaction recording
• Payroll processing
• Legal or HR services
• Audit or attest services

COMMUNICATION:
• Primary contact: [Name]
• Response SLA: 24 hours (business days)
• Emergency escalation: [method]
• Monthly call: [recurring time]

FEES:
• Monthly retainer: $4,500 (billed 1st of month)
• Overage: $250/hour above 15 hours (pre-approved)
• Out-of-pocket expenses billed at cost with receipts
```

### Client Health Scorecard

Track engagement health monthly:

```
CLIENT: [Name] | MONTH: [Month]

Relationship Health
  □ Monthly call completed?          Y/N
  □ Deliverables on time?            Y/N
  □ Client responsive to requests?   Y/N
  □ Open action items > 30 days old? Y/N

Financial Health Indicators
  □ Bookkeeping current?             Y/N
  □ Cash > 3 months runway?          Y/N
  □ No undisclosed liabilities?      Y/N
  □ Compliance deadlines on track?   Y/N

Engagement Risk
  □ Scope creep this month?          Y/N
  □ Hours within budget?             Y/N
  □ Any relationship concerns?       Y/N
  
OVERALL STATUS: 🟢 Healthy / 🟡 Watch / 🔴 Escalate
```

---

## Industry-Specific Benchmarks

### SaaS
```
Gross Margin:          65–80%  (below 60% = cost problem)
S&M as % Revenue:      20–40%  (early stage) / 15–25% (mature)
R&D as % Revenue:      15–25%
G&A as % Revenue:      8–15%
Rule of 40:            ≥40 (Growth % + EBITDA Margin %)
NRR (Net Rev Retention): >100% excellent, 80–100% ok, <80% problem
LTV:CAC:               ≥3:1 minimum, 5:1+ healthy
```

### Professional Services / Consulting
```
Gross Margin:          50–70%  (revenue minus direct labor)
Utilization Rate:      65–75%  (billable hours / available hours)
Revenue per Employee:  $150K–$350K (varies by specialty)
Client Concentration:  No single client >25% of revenue
AR Days:               <35 days ideal
```

### E-commerce / Retail
```
Gross Margin:          30–60%  (depends on category)
Inventory Turnover:    6–12x per year
CAC:LTV:               ≥3:1
Return Rate:           <5% ideal
COGS % Revenue:        40–70%
```

---

## Integration Points

- **`startup-financial-model`** — Build 3-statement models for fundraising prep or annual planning
- **`kpi-alert-system`** — Automate threshold alerts for KPIs tracked in monthly CFO package
- **`qbo-automation`** — Pull actuals from QuickBooks for close and reporting
- **`ar-collections-agent`** — Manage AR follow-up workflow surfaced in CFO package
- **`cap-table-manager`** — Handle equity and dilution modeling during fundraising support
- **`thirteen-week-cash-flow`** — Generate detailed 13-week cash flow forecast
- **`budget-vs-actual`** — Produce variance analysis for board packages
- **`investor-memo-generator`** — Convert CFO financial narrative into investor documents

---

## Quick Reference: CFO Monthly Checklist

```
WEEK 1 (Days 1–7)
  □ Bank reconciliations complete
  □ Payroll reconciled
  □ Revenue recognition entries posted
  □ AR invoices verified sent

WEEK 2 (Days 8–14)
  □ Accruals and adjusting entries
  □ Trial balance reviewed
  □ Flux analysis completed
  □ Statements drafted

WEEK 3 (Days 15–20)
  □ CFO package finalized
  □ Package delivered to client
  □ Monthly strategy call held
  □ Action items documented

WEEK 4 (Days 21–31)
  □ Next month prep (budget check, upcoming deadlines)
  □ 13-week cash forecast updated
  □ Compliance calendar reviewed
  □ Client health scorecard updated
```
