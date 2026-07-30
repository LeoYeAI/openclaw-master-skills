---
name: thirteen-week-cash-flow
version: 1.0.0
author: PrecisionLedger
description: >
  Build and maintain a rolling 13-week cash flow forecast — the gold standard
  for short-term liquidity management used by CFOs, turnaround advisors, and
  lenders. Produces a week-by-week cash receipts and disbursements model,
  variance tracking against actuals, borrowing base calculations, covenant
  monitoring, and executive cash dashboards. Use when managing tight liquidity,
  preparing for a credit facility, navigating distress, or when the board/lender
  demands weekly cash visibility.
  NOT for: long-range (12-36 month) strategic planning (use startup-financial-model),
  annual budgeting, tax cash flow projections, or real-time bank balance monitoring
  (connect to banking API for that).
tags:
  - cash-flow
  - treasury
  - liquidity
  - forecasting
  - cfo
  - turnaround
  - lender
  - working-capital
---

# 13-Week Cash Flow Forecast Skill

The 13-week cash flow (13WCF) is the operating room monitor of finance — it tells you exactly how much oxygen (cash) you have left, week by week. This skill builds, maintains, and analyzes 13WCFs for any business size.

---

## When to Use This Skill

**Trigger phrases:**
- "Build a 13-week cash flow"
- "How's our short-term liquidity?"
- "Lender is asking for a weekly cash forecast"
- "We need to manage cash tightly"
- "Board wants a cash dashboard"
- "Are we going to make payroll next month?"
- "We're in a cash crunch — model it out"
- "Variance analysis on our cash forecast"

**NOT for:**
- Annual budget models → use a full 3-statement model or `startup-financial-model`
- Long-range (12-36 month) forecasts → use `startup-financial-model`
- Tax cash planning → requires tax-specific skill
- Real-time bank data syncing → connect to banking/QBO APIs
- Accounts payable automation → use `invoice-automation` or `qbo-automation`
- Cap table or equity cash modeling → use `cap-table-manager`

---

## Why 13 Weeks?

The 13-week horizon (one quarter) is the standard because:
- **Lenders require it** during credit facility draws and covenant testing
- **Distressed situations** demand weekly visibility, not monthly guesses
- **Payroll, rent, and debt service** are predictable within this window
- **AR/AP cycles** (30-60-90 day terms) fully play out in 13 weeks
- **Operationally actionable** — you can actually influence week 2-8 outcomes

---

## Model Structure

### Two Approaches

**1. Direct Method (Preferred for Distress / Tight Liquidity)**
Track actual cash in and cash out at the bank — receipts and disbursements.
Most accurate for near-term. Does not reconcile to GAAP net income.

**2. Indirect Method (For Stable Businesses)**
Start from P&L and adjust for non-cash items and working capital changes.
Better for businesses with predictable accrual-to-cash conversion.

For most 13WCF use cases, **use the direct method**.

---

## Direct Method Structure

```
BEGINNING CASH BALANCE
─────────────────────
CASH RECEIPTS:
  + Customer Payments / Collections (AR)
  + Cash Sales
  + Other Receipts (grants, tax refunds, asset sales)
  = Total Cash Receipts

CASH DISBURSEMENTS:
  - Payroll & Payroll Taxes
  - Accounts Payable (vendor payments)
  - Rent / Lease Payments
  - Debt Service (principal + interest)
  - Utilities & Operating Costs
  - Insurance Premiums
  - Tax Payments (estimated quarterly, payroll taxes)
  - Capital Expenditures
  - Other Disbursements
  = Total Cash Disbursements

NET CASH FLOW = Total Receipts - Total Disbursements

ENDING CASH BALANCE = Beginning Cash + Net Cash Flow
─────────────────────────────────────────────────────
CREDIT FACILITY:
  Beginning Revolver Balance
  + Draws
  - Repayments
  = Ending Revolver Balance

LIQUIDITY:
  Available Cash (Ending Balance)
  + Available Revolver Capacity
  = Total Liquidity
```

---

## Week-by-Week Build Process

### Step 1: Anchor on Opening Balance
```
Pull the actual bank balance as of the forecast start date.
Use cleared balance, not book balance (reconcile first).
Note: include all accounts (operating, payroll, reserve).
```

### Step 2: Build Collections Forecast (AR Receipts)

The hardest part — converting AR to cash by week:

```
AR Aging as of today:
  0-30 days: $X → collect at [DSO-adjusted timing]
  31-60 days: $X → collect with risk haircut
  61-90 days: $X → apply collection probability %
  90+ days: $X → apply risk factor (often 50-70% discount)

Collection Timing Model:
  Invoice Date | Invoice Amount | Expected Pay Date | Week # | Amount

For recurring customers:
  Track historical pay timing (e.g., customer pays net 45 on average)
  Apply that pattern forward to open invoices

For new sales / pipeline:
  Week of billing + customer payment terms = collection week
```

**Collections Spreadsheet Template:**
```
Customer | Invoice # | Invoice Date | Due Date | Amount | Probability | Expected Week | Forecasted Receipt
---------|-----------|--------------|----------|--------|-------------|---------------|-------------------
Acme     | INV-1042  | 2026-03-01   | 3/31     | 5,000  | 95%         | Week 3        | 4,750
Beta Co  | INV-1041  | 2026-02-15   | 3/17     | 12,000 | 100%        | Week 1        | 12,000
...
```

### Step 3: Build Disbursements Schedule

Map every known outflow to a specific week:

**Fixed/Recurring (easy to schedule):**
```
Payroll:         Week 2, 4, 6, 8, 10, 12 (bi-weekly example)
Rent:            Week 1 (1st of month)
Debt service:    Week X (per loan schedule)
Insurance:       Week X (monthly or quarterly)
Software subs:   Week X (auto-billing dates)
```

**Variable (AP-driven):**
```
Vendor payments = AP aging + payment terms + cash position management
  - Which vendors can be stretched? (net 45 → pay net 60)
  - Which have early pay discounts? (2/10 net 30)
  - Which are critical suppliers (must pay on time)?

AP Payment Priority Stack:
  Tier 1 (pay on time, always): Payroll, payroll taxes, critical vendors
  Tier 2 (pay per terms): Standard trade payables
  Tier 3 (stretch if needed): Non-critical, relationship-based payables
```

**One-Time / Lumpy:**
```
Tax payments: quarterly estimated taxes (dates known)
CapEx:        per purchase order / contract milestone
Legal:        per retainer or invoice
```

### Step 4: Assemble the 13 Weeks

```
          | Wk 1 | Wk 2 | Wk 3 | Wk 4 | Wk 5 | ... | Wk 13
          |------|------|------|------|------|-----|------
Beg Cash  |  500 |  420 |  385 |  610 |  540 | ... |   X
Receipts  |  200 |  350 |  400 |  180 |  290 | ... |   X
Disbursem | (280)| (385)| (175)| (250)| (310)| ... |  (X)
Net Flow  |  (80)| (35) |  225 |  (70)|  (20)| ... |   X
End Cash  |  420 |  385 |  610 |  540 |  520 | ... |   X
```

### Step 5: Revolver / Credit Line Integration

```
If the company has a revolver or line of credit:

  Minimum cash cushion target: $X (covenant or management decision)
  
  Draw logic:
    If Ending Cash < Minimum → Draw from revolver to cover gap
    If Ending Cash > Minimum + buffer → Repay revolver
  
  Revolver capacity check:
    Borrowing base = AR eligible × advance rate (typically 80%)
    Available = Borrowing Base - Outstanding Balance
    
  Week-by-week:
    Ending Cash (pre-revolver) + Draw - Repayment = Ending Cash (post-revolver)
```

---

## Variance Analysis

The 13WCF is only useful if you track actuals vs. forecast weekly.

### Weekly Variance Report Format

```
Week [X] Variance Analysis — [Date]

RECEIPTS:
  Forecast: $XXX,XXX
  Actual:   $XXX,XXX
  Variance: $X,XXX [F/U] — [explanation]

DISBURSEMENTS:
  Forecast: $XXX,XXX
  Actual:   $XXX,XXX
  Variance: $X,XXX [F/U] — [explanation]

ENDING CASH:
  Forecast: $XXX,XXX
  Actual:   $XXX,XXX
  Variance: $X,XXX [F/U]

KEY VARIANCES:
  1. Collections short $15k — Beta Co delayed payment to next week (confirmed)
  2. Payroll $2k under — headcount timing (one hire pushed to Week 8)
  3. AP $8k over — emergency HVAC repair not in forecast

ROLL-FORWARD NOTE:
  Beta Co $15k pushed to Week [Y]
  Revolver draw increased by $10k to maintain minimum
```

**F = Favorable (more cash), U = Unfavorable (less cash)**

### Trend Signals to Watch

```
🔴 RED FLAGS:
  - Ending cash below minimum 2+ consecutive weeks
  - Collections consistently 20%+ below forecast
  - Revolver utilization increasing each week (borrowing to fund operations)
  - Weeks where disbursements exceed receipts by >50%

🟡 YELLOW FLAGS:
  - Single-week collection shortfall (customer timing issue)
  - Forecast accuracy below 85% for 2+ weeks
  - Growing AP balance (stretching payables unsustainably)

🟢 GREEN:
  - Forecast accuracy >90%
  - Ending cash growing week-over-week
  - Revolver balance declining
```

---

## Lender / Investor Reporting Package

When submitting 13WCF to lenders, include:

```
Cover Memo:
  - Period covered (13 weeks from X to Y)
  - Opening cash balance (reconciled)
  - Key assumptions (collection timing, payroll dates, AP strategy)
  - Liquidity summary: lowest cash point, when, and amount
  - Borrowing base availability
  - Covenant compliance status

Exhibits:
  1. 13WCF Model (week-by-week table)
  2. AR Aging and Collections Detail
  3. AP Aging and Payment Schedule
  4. Borrowing Base Certificate (if applicable)
  5. Week-over-week variance summary (if rolling update)
```

---

## Covenant Monitoring

Many credit facilities include liquidity covenants. Track weekly:

```
Common Covenants:
  Minimum Liquidity:     Cash + Available Revolver ≥ $X
  Minimum Cash Balance:  Bank balance ≥ $X at week end
  Springing Covenant:    Triggers additional restrictions if cash < $X
  
Covenant Dashboard:
  Covenant            | Threshold | Current | Headroom | Status
  -------------------|-----------|---------|----------|--------
  Min Liquidity       | $500k     | $620k   | $120k    | ✅ Pass
  Min Cash            | $200k     | $385k   | $185k    | ✅ Pass
  Revolver Usage      | ≤85%      | 62%     | 23%      | ✅ Pass
  
Early Warning: Flag when headroom < 25% of threshold
```

---

## Structured JSON Output

When producing 13WCF output for export or integration:

```json
{
  "forecast_meta": {
    "company": "Acme Corp",
    "start_date": "2026-03-16",
    "end_date": "2026-06-07",
    "currency": "USD",
    "opening_cash": 420000,
    "method": "direct",
    "generated": "2026-03-16"
  },
  "weeks": [
    {
      "week_num": 1,
      "week_start": "2026-03-16",
      "week_end": "2026-03-22",
      "beginning_cash": 420000,
      "receipts": {
        "ar_collections": 180000,
        "cash_sales": 15000,
        "other": 0,
        "total": 195000
      },
      "disbursements": {
        "payroll": 0,
        "accounts_payable": 85000,
        "rent": 22000,
        "debt_service": 0,
        "taxes": 0,
        "other": 12000,
        "total": 119000
      },
      "net_cash_flow": 76000,
      "ending_cash_pre_revolver": 496000,
      "revolver_draw": 0,
      "revolver_repayment": 50000,
      "ending_cash": 446000,
      "revolver_balance": 200000,
      "total_liquidity": 846000,
      "covenant_min_liquidity": 500000,
      "covenant_headroom": 346000,
      "covenant_status": "pass"
    }
  ],
  "summary": {
    "lowest_cash_week": 4,
    "lowest_cash_amount": 285000,
    "total_receipts_13wk": 2100000,
    "total_disbursements_13wk": 1850000,
    "ending_cash_week13": 670000,
    "max_revolver_balance": 350000,
    "forecast_accuracy_target": 0.90
  }
}
```

---

## Step-by-Step Workflow

When a user asks for a 13WCF:

### Step 1: Intake
```
□ Opening bank balance (as of today, cleared)
□ AR aging report (all open invoices)
□ AP aging report (all open payables)
□ Payroll schedule (dates and amounts)
□ Loan schedule (debt service dates)
□ Known large one-time items (rent, tax payments, CapEx)
□ Credit facility details (limit, outstanding, borrowing base)
□ Minimum cash threshold (management target or covenant)
□ Any known collection risks (disputed invoices, slow customers)
```

### Step 2: Build Collections
- Map each AR invoice to expected collection week
- Apply probability haircuts for aging invoices
- Add new sales pipeline if known

### Step 3: Build Disbursement Schedule
- Fixed: map every recurring payment to exact week
- Variable: apply AP aging + payment priority to determine pay weeks
- One-time: calendar all known lumpy items

### Step 4: Assemble Model
- Week-by-week table: beginning cash → receipts → disbursements → ending cash
- Add revolver mechanics if applicable
- Calculate total liquidity and covenant positions

### Step 5: Stress Test
- What if collections are 20% lower than forecast?
- What if a large customer (>15% of receipts) delays 2 weeks?
- What if payroll increases 10% (bonus, new hire)?
- Identify the "cliff" week — when does cash hit the minimum?

### Step 6: Management Actions
Based on the forecast, identify levers:
```
If cash tight in Week 3-4:
  - Accelerate collections: offer 2% early pay discount
  - Stretch AP Tier 2 vendors by 2 weeks
  - Draw $50k from revolver
  - Defer non-critical CapEx

If cash comfortable:
  - Repay revolver to reduce interest
  - Build minimum cash cushion
  - Pre-pay Tier 1 vendors for relationship / discount
```

### Step 7: Deliver
- Formatted weekly table
- Variance actuals block (if rolling update)
- Covenant dashboard
- Top 3 risks and management actions

---

## Example Usage

**User:** "We need a 13-week cash flow. We have $380k in the bank, $210k in AR (mostly net 30), payroll of $85k bi-weekly, rent $18k first of month, and a $500k revolver at 60% drawn. Minimum cash covenant is $150k."

**Sam's response:**

```
13-Week Cash Flow — Starting Week of 3/16/2026
Opening Cash: $380,000 | Revolver: $300k drawn / $200k available | Covenant: $150k minimum

QUICK SNAPSHOT:
  Lowest cash point: Week 3 (pre-payroll week) at ~$195k — $45k above covenant
  Revolver: Recommend drawing $50k at Week 3 to build cushion to $245k
  Collections: $210k AR should convert ~$180k over weeks 1-4 (net 30 timing)

WEEKLY SUMMARY:
  Wk 1: Beg $380k | Receipts $95k | Disb ($88k) | End $387k
  Wk 2: Beg $387k | Receipts $60k | Disb ($108k) | End $339k  ← payroll + rent
  Wk 3: Beg $339k | Receipts $85k | Disb ($90k)  | End $334k
  Wk 4: Beg $334k | Receipts $55k | Disb ($108k) | End $281k  ← payroll + rent
  ...
  Wk 13: Projected ending ~$310k | Revolver same or better

KEY RISKS:
  1. If top customer (accounts for ~$80k AR) delays 2 weeks → Week 4 cash drops to ~$195k, barely above covenant
  2. Any unexpected >$30k expense in weeks 2-4 hits covenant
  
RECOMMENDED ACTIONS:
  - Call top AR customer now — confirm payment timing
  - Pre-approve $75k revolver draw to trigger if needed (don't draw yet)
  - Hold AP Tier 2 payments in weeks 2-4 until AR clears

Want me to build out all 13 weeks in full detail with the complete disbursement schedule?
```

---

## Integration Points

- **`startup-financial-model`** — Long-range context for the 13WCF (is the business structurally viable?)
- **`kpi-alert-system`** — Set automated alerts when ending cash < covenant + $50k buffer
- **`qbo-automation`** — Pull AR/AP aging and bank balances directly from QuickBooks
- **`ar-collections-agent`** — Coordinate with collections workflow to improve receipt timing
- **`report-generator`** — Format 13WCF into lender-ready PDF package

---

## Reference: Key Formulas

```
Net Cash Flow         = Total Receipts - Total Disbursements
Ending Cash           = Beginning Cash + Net Cash Flow ± Revolver Activity
Total Liquidity       = Ending Cash + Available Revolver Capacity
Covenant Headroom     = Total Liquidity - Covenant Minimum
Borrowing Base        = Eligible AR × Advance Rate (typically 80%)
Available Revolver    = Borrowing Base - Outstanding Balance
Collection Efficiency = Actual Collections / Forecasted Collections × 100
DSO (Days Sales Out.) = AR Balance / (Revenue / 90 days)
DPO (Days Pay. Out.)  = AP Balance / (COGS / 90 days)
Cash Conversion Cycle = DSO + DIO - DPO
```
