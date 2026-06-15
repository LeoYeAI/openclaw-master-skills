---
name: financial-analysis-agent
description: 'Financial analysis skill for AI agents. Covers variance analysis, cash flow forecasting, month-end close automation, CFO commentary generation, 13-week cash flow dashboards, budget vs actual analysis, and financial statement review. Built by accounting professionals for agents that need to produce defensible financial outputs. Do NOT use for tax preparation, audit opinions, or regulatory filings — those require specialized compliance skills.'
license: MIT
metadata:
  openclaw:
    emoji: '💰'
---

# Financial Analysis Agent

A comprehensive financial analysis skill that enables AI agents to produce defensible, CFO-ready financial outputs. Every technique here is grounded in standard accounting practice (US GAAP / IFRS compatible) and designed for agents operating on real financial data.

## When to Use

- Monthly/quarterly financial close cycles
- Variance analysis on budget vs actual results
- Cash flow forecasting and 13-week rolling dashboards
- Generating CFO commentary and board-ready narratives
- Ratio analysis for lending covenants or investor reporting
- AR/AP aging analysis and collections prioritization
- Bank reconciliation pattern matching

## When NOT to Use

- Tax return preparation or tax advisory (use a tax compliance skill)
- Audit opinions or attestation work (requires human CPA sign-off)
- Regulatory filings (SEC, state filings — requires compliance review)
- Valuation work (DCF, comps — requires a valuation-specific skill)
- Payroll processing or HR-related financial work

---

## 1. Variance Analysis Methodology

Variance analysis decomposes the difference between budget and actual into **price**, **volume**, and **mix** components.

### Price Variance

Measures the impact of actual price differing from budgeted price, holding volume constant.

```
Price Variance = (Actual Price - Budget Price) × Actual Volume
```

**Example:**
```
Budget: 1,000 units @ $50 = $50,000
Actual: 1,000 units @ $53 = $53,000
Price Variance = ($53 - $50) × 1,000 = $3,000 Unfavorable (cost) or Favorable (revenue)
```

### Volume Variance

Measures the impact of actual volume differing from budgeted volume, at budgeted price.

```
Volume Variance = (Actual Volume - Budget Volume) × Budget Price
```

**Example:**
```
Budget: 1,000 units @ $50 = $50,000
Actual: 1,100 units @ $50 = $55,000
Volume Variance = (1,100 - 1,000) × $50 = $5,000 Favorable (revenue)
```

### Mix Variance

When multiple products exist, mix variance isolates the impact of selling a different proportion than planned.

```
Mix Variance = (Actual Mix% - Budget Mix%) × Actual Total Volume × Budget Margin
```

### Three-Way Reconciliation

Always reconcile: `Total Variance = Price Variance + Volume Variance + Mix Variance`

If the three don't sum to the total, you have a calculation error. Never present unreconciled variances.

### Materiality Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Revenue line item | >5% or >$10K | Requires written explanation |
| Expense line item | >10% or >$5K | Requires written explanation |
| Net income impact | >2% | Requires CFO commentary |
| Balance sheet item | >$25K | Requires reconciliation |

Adjust thresholds based on entity size. A $2M company uses different thresholds than a $200M company.

---

## 2. Cash Flow Forecasting (13-Week Rolling)

The 13-week cash flow forecast is the standard tool for liquidity management. It covers one full quarter on a weekly basis.

### Structure

```
Week →           W1      W2      W3      W4    ...   W13     Total
─────────────────────────────────────────────────────────────────
Opening Cash     100K    112K    108K    95K          XXK     100K

INFLOWS
  Collections    50K     45K     55K     40K          XXK     XXX
  Other Income   2K      1K      3K      2K           XXK     XXX
Total Inflows    52K     46K     58K     42K          XXK     XXX

OUTFLOWS
  Payroll        (20K)   —       (20K)   —            XXK     XXX
  Rent           (5K)    —       —       —            XXK     XXX
  Vendors        (10K)   (12K)   (8K)    (15K)        XXK     XXX
  Debt Service   —       (5K)    —       —            XXK     XXX
  Other          (5K)    (3K)    (3K)    (4K)         XXK     XXX
Total Outflows   (40K)   (20K)   (31K)   (19K)        XXK     XXX

Net Cash Flow    12K     (4K)    (13K)   23K          XXK     XXX
Closing Cash     112K    108K    95K     118K         XXK     XXX

Min Balance Req  50K     50K     50K     50K          50K     50K
Surplus/(Deficit)62K     58K     45K     68K          XXK     XXX
```

### Collection Assumptions

Build collection curves from historical data:

```
Invoice Terms    Collection Pattern
─────────────────────────────────────
Net 30           Month 1: 15%, Month 2: 70%, Month 3: 12%, Bad debt: 3%
Net 15           Month 1: 80%, Month 2: 17%, Bad debt: 3%
COD              Month 1: 97%, Bad debt: 3%
```

### Forecast Accuracy Tracking

Every week, compare last week's forecast to actual:

```
Forecast Accuracy = 1 - |Actual - Forecast| / |Forecast|
Target: >90% accuracy on 1-week forecast, >80% on 4-week
```

### Red Flags

- Closing cash below minimum balance requirement in any week
- Three consecutive weeks of declining cash
- Collections falling below 85% of forecast
- Concentration: any single customer >25% of weekly inflows

---

## 3. Month-End Close Checklist

A disciplined 10-step close process. Target: complete within 5 business days of month-end.

### The 10 Steps

```
Step  Task                              Owner    Day   Verification
─────────────────────────────────────────────────────────────────────
1     Cut off AR/AP                     AR/AP    D+1   Last invoice # matches
2     Bank reconciliation               Cash     D+1   All items <30 days
3     Record accruals                   GL       D+2   Accrual schedule signed
4     Record depreciation/amortization  GL       D+2   Fixed asset register ties
5     Intercompany eliminations         GL       D+3   IC balances net to zero
6     Revenue recognition review        Rev      D+3   ASC 606 checklist complete
7     Inventory/COGS reconciliation     Ops      D+3   Physical vs book <2%
8     Prepare trial balance             GL       D+4   Debits = Credits
9     Variance analysis                 FP&A     D+4   All material items explained
10    Management review & sign-off      CFO      D+5   Signed close package
```

### Accrual Checklist

Common accruals that get missed:

- [ ] Payroll accrual (days worked but not yet paid)
- [ ] Bonus accrual (pro-rata for period)
- [ ] Interest accrual on debt
- [ ] Utility accruals
- [ ] Professional services received but not invoiced
- [ ] Insurance amortization
- [ ] Prepaid expense amortization
- [ ] Deferred revenue recognition

### Journal Entry Standards

Every journal entry must include:
1. Date
2. Debit account(s) with amount
3. Credit account(s) with amount
4. Description/memo explaining the entry
5. Supporting documentation reference
6. Preparer and approver

```
Example:
Date: 2026-02-28
DR  6100 - Professional Services    $15,000
    CR  2100 - Accrued Expenses              $15,000
Memo: Accrue Feb legal fees per engagement letter #2026-041
Support: Email from counsel confirming Feb activity
Prepared: Agent | Approved: [CFO Name]
```

---

## 4. CFO Commentary Templates

CFO commentary answers three questions: **What changed? Why? What should we do?**

### Revenue Commentary Template

```markdown
## Revenue: $X.XM vs Budget $X.XM (↑/↓ X.X%)

**What changed:**
- [Product/Service line] revenue was $XXK [above/below] budget
- [Volume/Price/Mix] was the primary driver

**Why:**
- [Root cause — be specific: lost customer, delayed deal, new contract, seasonal]
- [Secondary cause if applicable]

**What to do:**
- [Action item 1 with owner and deadline]
- [Action item 2 with owner and deadline]

**Outlook:**
- [Forward-looking statement for next period]
- [Risk/opportunity to flag]
```

### Expense Commentary Template

```markdown
## Operating Expenses: $X.XM vs Budget $X.XM (↑/↓ X.X%)

**What changed:**
- [Expense category] was $XXK [over/under] budget
- [One-time vs recurring classification]

**Why:**
- [Root cause — hiring timing, vendor price increase, project delay, etc.]

**What to do:**
- [If over: mitigation plan or approval to exceed]
- [If under: whether savings are permanent or timing]
```

### Cash Position Commentary

```markdown
## Cash Position: $X.XM (↑/↓ $XXK from prior month)

**Key movements:**
- Operating cash flow: $XXK [positive/negative]
- Collections: $XXK received vs $XXK billed (XX% collection rate)
- Major payments: [List any >$25K individual payments]

**Liquidity outlook:**
- Runway: XX months at current burn rate
- Covenants: [In compliance / approaching threshold]
- Next major cash event: [Date and description]
```

---

## 5. Budget vs Actual Analysis

### Report Structure

```
                          Actual    Budget    Var $     Var %    Prior Yr   YoY %
─────────────────────────────────────────────────────────────────────────────────
Revenue
  Product A               450K      500K     (50K)    -10.0%    380K      +18.4%
  Product B               320K      300K      20K      +6.7%    290K      +10.3%
  Services                180K      200K     (20K)    -10.0%    150K      +20.0%
Total Revenue             950K     1,000K    (50K)     -5.0%    820K      +15.9%

COGS                     (380K)    (400K)     20K      -5.0%   (340K)     +11.8%
Gross Profit              570K      600K     (30K)     -5.0%    480K      +18.8%
  Gross Margin           60.0%     60.0%       —         —     58.5%       +1.5pp

Operating Expenses
  Salaries               (250K)    (240K)    (10K)     +4.2%   (200K)     +25.0%
  Marketing               (60K)     (80K)     20K     -25.0%    (50K)     +20.0%
  G&A                     (45K)     (50K)      5K     -10.0%    (40K)     +12.5%
Total OpEx               (355K)    (370K)     15K      -4.1%   (290K)     +22.4%

EBITDA                    215K      230K     (15K)     -6.5%    190K      +13.2%
  EBITDA Margin          22.6%     23.0%    -0.4pp       —     23.2%      -0.6pp
```

### Waterfall Analysis

For board presentations, decompose the variance into a waterfall:

```
Budget EBITDA          $230K
  Revenue shortfall     (50K)   ← Volume: (30K), Price: (15K), Mix: (5K)
  COGS favorability      20K   ← Material costs lower than expected
  Salary overage        (10K)   ← Hired 2 weeks earlier than planned
  Marketing savings      20K   ← Campaign delayed to next month
  G&A savings             5K   ← Office lease negotiation
Actual EBITDA          $215K
```

---

## 6. Ratio Analysis

### Liquidity Ratios

| Ratio | Formula | Healthy Range | Red Flag |
|-------|---------|---------------|----------|
| Current Ratio | Current Assets / Current Liabilities | 1.5 - 3.0 | < 1.0 |
| Quick Ratio | (Cash + Receivables) / Current Liabilities | 1.0 - 2.0 | < 0.5 |
| Cash Ratio | Cash / Current Liabilities | 0.5 - 1.0 | < 0.2 |
| Working Capital | Current Assets - Current Liabilities | Positive | Negative trend |

### Profitability Ratios

| Ratio | Formula | Notes |
|-------|---------|-------|
| Gross Margin | Gross Profit / Revenue | Compare to industry benchmarks |
| Operating Margin | Operating Income / Revenue | Exclude one-time items |
| Net Margin | Net Income / Revenue | After all charges |
| EBITDA Margin | EBITDA / Revenue | Most comparable across companies |
| ROE | Net Income / Avg Equity | Should exceed cost of equity |
| ROA | Net Income / Avg Assets | Asset efficiency measure |

### Leverage Ratios

| Ratio | Formula | Covenant Typical | Warning |
|-------|---------|-------------------|---------|
| Debt/Equity | Total Debt / Total Equity | < 2.0x | > 3.0x |
| Debt/EBITDA | Total Debt / EBITDA | < 3.0x | > 4.0x |
| Interest Coverage | EBITDA / Interest Expense | > 3.0x | < 2.0x |
| Fixed Charge Coverage | (EBITDA - CapEx) / (Interest + Principal) | > 1.2x | < 1.0x |

### Efficiency Ratios

| Ratio | Formula | Target |
|-------|---------|--------|
| DSO (Days Sales Outstanding) | (AR / Revenue) × Days | < Payment terms |
| DPO (Days Payable Outstanding) | (AP / COGS) × Days | Match or exceed DSO |
| DIO (Days Inventory Outstanding) | (Inventory / COGS) × Days | Industry-specific |
| Cash Conversion Cycle | DSO + DIO - DPO | Lower is better |

---

## 7. Aging Analysis

### Accounts Receivable Aging

```
Customer        Current   1-30     31-60    61-90    90+      Total    % of AR
──────────────────────────────────────────────────────────────────────────────
Acme Corp       25,000    10,000   5,000    —        —        40,000   26.7%
Beta LLC        15,000    8,000    —        3,000    —        26,000   17.3%
Gamma Inc       20,000    —        —        —        12,000   32,000   21.3%
All Others      30,000    15,000   5,000    2,000    —        52,000   34.7%
──────────────────────────────────────────────────────────────────────────────
Total           90,000    33,000   10,000   5,000    12,000   150,000  100%
% of Total      60.0%     22.0%    6.7%     3.3%     8.0%     100%
Reserve Rate    0%        0%       5%       25%      50%
Reserve Amount  —         —        500      1,250    6,000    7,750
```

### Collection Priority Matrix

| Bucket | Action | Frequency | Escalation |
|--------|--------|-----------|------------|
| Current | Thank-you / relationship | Monthly | None |
| 1-30 past due | Friendly reminder email | Weekly | None |
| 31-60 past due | Phone call + formal letter | 2x/week | AR Manager |
| 61-90 past due | Demand letter + payment plan | Daily | Controller |
| 90+ past due | Legal review + reserve | Daily | CFO |

### Accounts Payable Aging

Mirror the AR structure but optimize for:
- Early payment discounts (2/10 Net 30 = 36.7% annualized return)
- Cash flow timing (pay on last day of terms, not before)
- Vendor relationship management (strategic vendors get priority)

---

## 8. Bank Reconciliation Patterns

### Standard Reconciliation Format

```
Bank Balance per Statement (2/28/2026)           $125,432.18

ADD: Deposits in Transit
  2/27 - Customer payment #4521                     8,500.00
  2/28 - Wire transfer (pending)                   15,000.00
                                                   23,500.00

LESS: Outstanding Checks
  Check #3041 (1/15) - Vendor payment              (2,300.00)
  Check #3055 (2/20) - Rent                        (5,000.00)
  Check #3058 (2/25) - Supplies                      (450.00)
                                                   (7,750.00)

LESS: Bank Errors
  (None this period)                                     0.00

Adjusted Bank Balance                             $141,182.18

Book Balance per GL (2/28/2026)                   $141,682.18

LESS: Bank Charges
  Monthly service fee                                 (35.00)
  Wire fee                                            (25.00)

ADD: Interest Earned
  February interest                                    12.00

LESS: NSF Checks
  Customer ABC - returned check                     (452.00)

Adjusted Book Balance                             $141,182.18

DIFFERENCE                                              $0.00  ✓ RECONCILED
```

### Stale Items Investigation

Any reconciling item older than 30 days requires investigation:

| Age | Item Type | Action |
|-----|-----------|--------|
| 30-60 days | Outstanding check | Contact payee, confirm receipt |
| 60-90 days | Outstanding check | Void and reissue if needed |
| 90+ days | Outstanding check | Void, reverse entry, escheatment review |
| 30+ days | Deposit in transit | Investigate with bank, possible misposting |

---

## 9. Financial Statement Review Checklist

Before releasing any financial statement, verify:

### Balance Sheet

- [ ] Assets = Liabilities + Equity (must balance to the penny)
- [ ] Cash ties to bank reconciliation
- [ ] AR ties to aging report and subledger
- [ ] AP ties to aging report and subledger
- [ ] Fixed assets tie to depreciation schedule
- [ ] Debt balances tie to loan statements
- [ ] Retained earnings = Prior RE + Net Income - Dividends
- [ ] Intercompany balances eliminate to zero

### Income Statement

- [ ] Revenue recognized per ASC 606 / IFRS 15 criteria
- [ ] COGS matches inventory movement
- [ ] Depreciation/amortization matches fixed asset schedule
- [ ] Interest expense matches debt schedule
- [ ] Tax provision is reasonable (effective rate within expected range)
- [ ] No below-the-line items without disclosure
- [ ] Period-over-period comparison is sensible (no sign errors)

### Cash Flow Statement

- [ ] Operating + Investing + Financing = Change in Cash
- [ ] Change in cash ties to balance sheet cash movement
- [ ] Non-cash items properly excluded from operating section
- [ ] CapEx in investing ties to fixed asset additions
- [ ] Debt proceeds/payments tie to balance sheet debt movement
- [ ] Supplemental disclosures (interest paid, taxes paid) are accurate

### Analytical Review

- [ ] Gross margin is within 2pp of prior period (or explained)
- [ ] Revenue growth is consistent with known business activity
- [ ] No expense line items with >25% unexplained variance
- [ ] Ratios (current, quick, leverage) are within covenant requirements
- [ ] Month-over-month trends are logical
- [ ] YTD figures match sum of monthly figures
