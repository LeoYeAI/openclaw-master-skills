---
name: working-capital-optimizer
version: 1.0.0
description: >
  Analyze and optimize working capital for SMBs and growth-stage companies. Calculates DSO (Days Sales
  Outstanding), DPO (Days Payable Outstanding), DIO (Days Inventory Outstanding), and the full Cash
  Conversion Cycle (CCC). Identifies AR aging risks, AP extension opportunities, and inventory carrying
  costs. Produces actionable improvement recommendations with projected cash flow impact. Use when:
  a client has cash flow strain despite profitability, AR is aging, AP terms need renegotiating, or
  a CFO wants to free up working capital without new financing.
  NOT for: tax preparation, payroll, or capital structure decisions (debt vs equity raises). NOT for
  real-time accounting integrations — use qbo-automation for live QBO data pulls. NOT for inventory
  management software configuration (use vendor-specific skill).
license: MIT
author: PrecisionLedger
tags:
  - finance
  - working-capital
  - cash-flow
  - ar
  - ap
  - dso
  - dpo
  - accounting
  - cfo
---

# Working Capital Optimizer

Diagnose and improve the cash conversion cycle for SMBs and growth-stage companies. This skill guides Sam Ledger (or any financial AI agent) through working capital analysis, identifies where cash is trapped, and produces a prioritized action plan with quantified cash release projections.

---

## When to Use This Skill

**Trigger phrases:**
- "Our cash is tight but we're profitable — why?"
- "What's our DSO / DPO / cash conversion cycle?"
- "Help us optimize working capital"
- "How do we free up cash without borrowing?"
- "AR is aging — what should we do?"
- "Can we extend our AP terms?"
- "Inventory is piling up and tying up cash"
- "Working capital analysis for [company]"

**NOT for:**
- Tax filing or compliance — use a compliance workflow
- Equity or debt capital raises — use `startup-financial-model` or `cap-table-manager`
- Real-time accounting system sync — use `qbo-automation` skill
- Payroll or GL reconciliation — use `payroll-gl-reconciliation` skill
- Retail inventory management software — use vendor-specific tooling

---

## Core Metrics

### Cash Conversion Cycle (CCC)

```
CCC = DSO + DIO - DPO

Where:
  DSO = Days Sales Outstanding     (how long to collect from customers)
  DIO = Days Inventory Outstanding (how long inventory sits before sale)
  DPO = Days Payable Outstanding   (how long before you pay suppliers)

Lower CCC = Better (cash returns faster)
Negative CCC = Excellent (paid by customers before paying suppliers — e.g., Amazon)
```

### DSO — Days Sales Outstanding

```
DSO = (Accounts Receivable / Revenue) × Days in Period

Example:
  AR Balance: $150,000
  Revenue (last 90 days): $450,000
  DSO = ($150,000 / $450,000) × 90 = 30 days

Industry benchmarks:
  < 30 days: Excellent
  30-45 days: Acceptable
  45-60 days: Needs attention
  > 60 days: Cash flow risk
```

### DPO — Days Payable Outstanding

```
DPO = (Accounts Payable / COGS) × Days in Period

Example:
  AP Balance: $80,000
  COGS (last 90 days): $270,000
  DPO = ($80,000 / $270,000) × 90 = 26.7 days

Strategy: Maximize DPO (pay as late as allowed) without damaging supplier relationships.
Target: Match or slightly exceed supplier terms (Net 30 → pay day 28-30, not day 5)
```

### DIO — Days Inventory Outstanding

```
DIO = (Inventory / COGS) × Days in Period

Example:
  Inventory: $120,000
  COGS (last 90 days): $270,000
  DIO = ($120,000 / $270,000) × 90 = 40 days

For service businesses: DIO = 0 (no physical inventory)
```

---

## Analysis Workflow

### Step 1: Gather Inputs

Collect from financial statements or QBO export:

```
Balance Sheet (current period):
  □ Accounts Receivable balance
  □ Inventory balance (if applicable)
  □ Accounts Payable balance
  □ Accrued Expenses
  □ Deferred Revenue (if any)

Income Statement (trailing 90 days preferred):
  □ Revenue
  □ Cost of Goods Sold (COGS)

AR Aging Report:
  □ Current (0-30 days)
  □ 31-60 days
  □ 61-90 days
  □ 90+ days (specify amounts)

AP Aging Report:
  □ Current
  □ Overdue amounts
  □ Key supplier names and terms
```

### Step 2: Calculate Current State

```python
def calculate_working_capital_metrics(
    ar: float,
    inventory: float,
    ap: float,
    revenue_90d: float,
    cogs_90d: float,
    period_days: int = 90
) -> dict:
    """
    Calculate core working capital metrics.
    
    Args:
        ar: Accounts Receivable balance
        inventory: Inventory balance (0 for service businesses)
        ap: Accounts Payable balance
        revenue_90d: Revenue for the measurement period
        cogs_90d: COGS for the measurement period
        period_days: Length of measurement period (default 90)
    
    Returns:
        Dict with DSO, DIO, DPO, CCC, and working capital amount
    """
    dso = (ar / revenue_90d) * period_days if revenue_90d else 0
    dio = (inventory / cogs_90d) * period_days if cogs_90d and inventory else 0
    dpo = (ap / cogs_90d) * period_days if cogs_90d else 0
    ccc = dso + dio - dpo
    
    working_capital = ar + inventory - ap
    
    return {
        "dso_days": round(dso, 1),
        "dio_days": round(dio, 1),
        "dpo_days": round(dpo, 1),
        "ccc_days": round(ccc, 1),
        "working_capital_usd": working_capital,
        "ar_usd": ar,
        "inventory_usd": inventory,
        "ap_usd": ap,
        "assessment": _assess_ccc(ccc, dso, dpo)
    }

def _assess_ccc(ccc: float, dso: float, dpo: float) -> str:
    if ccc < 0:
        return "excellent"
    elif ccc <= 30:
        return "good"
    elif ccc <= 60:
        return "acceptable"
    elif ccc <= 90:
        return "needs_improvement"
    else:
        return "critical"
```

### Step 3: AR Aging Analysis

```python
def analyze_ar_aging(aging_buckets: dict, total_ar: float) -> dict:
    """
    Analyze AR aging and identify collection risk.
    
    Args:
        aging_buckets: {"0_30": x, "31_60": x, "61_90": x, "90_plus": x}
        total_ar: Total AR balance (validation check)
    
    Returns:
        Risk assessment and recommended actions
    """
    at_risk = aging_buckets.get("61_90", 0) + aging_buckets.get("90_plus", 0)
    at_risk_pct = at_risk / total_ar if total_ar else 0
    
    recommendations = []
    
    if aging_buckets.get("31_60", 0) / total_ar > 0.3:
        recommendations.append({
            "action": "Send reminder notices to 31-60 day balances",
            "priority": "medium",
            "cash_impact": aging_buckets["31_60"],
            "timeline": "within 1 week"
        })
    
    if aging_buckets.get("61_90", 0) > 0:
        recommendations.append({
            "action": "Direct phone outreach to 61-90 day accounts",
            "priority": "high",
            "cash_impact": aging_buckets["61_90"],
            "timeline": "this week"
        })
    
    if aging_buckets.get("90_plus", 0) > 0:
        recommendations.append({
            "action": "Place 90+ day accounts on collections / payment plan",
            "priority": "critical",
            "cash_impact": aging_buckets["90_plus"],
            "timeline": "immediately"
        })
    
    return {
        "at_risk_usd": at_risk,
        "at_risk_pct": round(at_risk_pct * 100, 1),
        "collectible_estimate_usd": at_risk * 0.75,  # 75% recovery assumption
        "risk_level": "critical" if at_risk_pct > 0.20 else "moderate" if at_risk_pct > 0.10 else "low",
        "recommendations": recommendations
    }
```

### Step 4: AP Optimization Analysis

```python
def analyze_ap_optimization(
    ap_balance: float,
    avg_payment_day: float,
    standard_terms_days: int,
    monthly_cogs: float
) -> dict:
    """
    Identify AP extension opportunities.
    
    Strategy: Pay on due date, not early (unless early-pay discount justifies it)
    """
    # Days of additional cash float if paying on terms vs. current practice
    days_to_extend = max(0, standard_terms_days - avg_payment_day)
    daily_cogs = monthly_cogs / 30
    cash_freed = days_to_extend * daily_cogs
    
    # Early pay discount analysis
    # Example: "2/10 Net 30" = 2% discount if paid within 10 days
    # Annualized cost of NOT taking discount = 2% / (30-10) * 365 = 36.5% annualized
    # If cost of capital < 36.5%, TAKE the discount
    
    return {
        "current_avg_payment_day": avg_payment_day,
        "standard_terms_days": standard_terms_days,
        "days_of_extension_available": days_to_extend,
        "estimated_cash_freed_usd": round(cash_freed, 0),
        "recommendation": (
            f"Extend payment timing by {days_to_extend} days to terms. "
            f"Frees ~${cash_freed:,.0f} in working capital."
        ) if days_to_extend > 0 else "Already paying close to terms. Focus on negotiating extended terms with key suppliers."
    }
```

### Step 5: Generate Action Plan

Structure recommendations by cash impact and implementation speed:

```python
def generate_action_plan(metrics: dict, ar_analysis: dict, ap_analysis: dict) -> dict:
    """
    Produce prioritized working capital improvement plan.
    """
    quick_wins = []      # < 30 days, low friction
    medium_term = []     # 30-90 days
    strategic = []       # 90+ days, structural changes
    
    total_cash_release_estimate = 0
    
    # AR Quick Wins
    if ar_analysis["at_risk_usd"] > 0:
        quick_wins.append({
            "lever": "AR Collections",
            "action": f"Collect 61-90 day and 90+ day balances (${ar_analysis['at_risk_usd']:,.0f} at risk)",
            "cash_impact_usd": ar_analysis["collectible_estimate_usd"],
            "timeline_days": 30,
            "effort": "medium"
        })
        total_cash_release_estimate += ar_analysis["collectible_estimate_usd"]
    
    # AP Extension
    if ap_analysis["estimated_cash_freed_usd"] > 0:
        quick_wins.append({
            "lever": "AP Extension",
            "action": ap_analysis["recommendation"],
            "cash_impact_usd": ap_analysis["estimated_cash_freed_usd"],
            "timeline_days": 14,
            "effort": "low"
        })
        total_cash_release_estimate += ap_analysis["estimated_cash_freed_usd"]
    
    # DSO Reduction
    if metrics["dso_days"] > 45:
        dso_target = 35
        daily_revenue = metrics["ar_usd"] / metrics["dso_days"] if metrics["dso_days"] else 0
        cash_from_dso = (metrics["dso_days"] - dso_target) * daily_revenue
        medium_term.append({
            "lever": "Invoice Terms",
            "action": f"Shorten payment terms from Net {int(metrics['dso_days'])} to Net {dso_target}. Offer early-pay incentive (1% Net 10).",
            "cash_impact_usd": round(cash_from_dso, 0),
            "timeline_days": 60,
            "effort": "medium"
        })
    
    # Structural AP Terms Negotiation
    strategic.append({
        "lever": "AP Terms Renegotiation",
        "action": "Renegotiate key supplier terms from Net 30 to Net 45/60",
        "cash_impact_usd": None,  # Depends on negotiation outcome
        "timeline_days": 90,
        "effort": "high"
    })
    
    return {
        "total_estimated_cash_release_usd": total_cash_release_estimate,
        "quick_wins": quick_wins,
        "medium_term": medium_term,
        "strategic": strategic,
        "summary": f"Estimated ${total_cash_release_estimate:,.0f} in working capital can be freed within 30-60 days through focused collection and AP timing improvements."
    }
```

---

## Industry Benchmarks

| Industry | DSO Target | DPO Target | CCC Target |
|---|---|---|---|
| SaaS / Software | 30-45 days | 30-45 days | 0-30 days |
| Professional Services | 30-45 days | 30-45 days | 15-45 days |
| Manufacturing | 40-55 days | 40-60 days | 40-80 days |
| Distribution / Wholesale | 35-50 days | 35-55 days | 30-60 days |
| Retail | 3-7 days | 30-45 days | -20 to 20 days |
| Construction | 45-75 days | 30-45 days | 45-90 days |
| Healthcare / Medical | 45-65 days | 30-45 days | 45-75 days |

---

## Output Format

### Executive Summary (for client delivery)

```
WORKING CAPITAL ANALYSIS — [Company] — [Date]

CURRENT STATE:
  DSO: [X] days | Target: [Y] days | Gap: [Z] days
  DIO: [X] days (N/A for services)
  DPO: [X] days | Target: [Y] days
  CCC: [X] days | Status: [Good/Acceptable/Needs Improvement/Critical]

  Working Capital: $[X]
  AR at Risk (60+ days): $[X] ([Y]% of AR)

KEY FINDINGS:
  1. [Most important issue — quantified]
  2. [Second issue — quantified]
  3. [Third issue — quantified]

PRIORITIZED ACTION PLAN:
  QUICK WINS (0-30 days, ~$[X] cash release):
    □ [Action 1] → $[impact]
    □ [Action 2] → $[impact]

  MEDIUM-TERM (30-90 days, ~$[X] additional):
    □ [Action 3]
    □ [Action 4]

  STRATEGIC (90+ days):
    □ [Action 5]

NEXT STEP: [Single most important immediate action]
```

### Structured JSON Output

```json
{
  "company": "Acme Corp",
  "analysis_date": "2026-03-15",
  "period": "Q1 2026 (Jan-Mar)",
  "metrics": {
    "dso_days": 52,
    "dio_days": 0,
    "dpo_days": 24,
    "ccc_days": 28,
    "working_capital_usd": 185000,
    "assessment": "needs_improvement"
  },
  "ar_aging": {
    "current_0_30": 90000,
    "days_31_60": 45000,
    "days_61_90": 22000,
    "days_90_plus": 18000,
    "total": 175000,
    "at_risk_pct": 22.9,
    "risk_level": "critical"
  },
  "action_plan": {
    "total_estimated_cash_release_usd": 62500,
    "quick_wins": [
      {
        "lever": "AR Collections",
        "action": "Collect 61-90 and 90+ day balances ($40,000 at risk)",
        "cash_impact_usd": 30000,
        "timeline_days": 30
      },
      {
        "lever": "AP Extension",
        "action": "Extend payment timing by 6 days to terms. Frees ~$12,500.",
        "cash_impact_usd": 12500,
        "timeline_days": 14
      }
    ]
  }
}
```

---

## Example Usage

**User:** "Our QBO shows $175k AR, $70k AP, $2M in revenue last year. We're profitable but always feel cash-strapped. What's going on?"

**Sam's response:**

```
Working Capital Snapshot:

  Revenue run rate: $2M/yr → ~$500k/quarter
  AR: $175,000
  AP: $70,000

  DSO = ($175,000 / $500,000) × 90 = 31.5 days ← borderline, worth watching
  DPO = ($70,000 / estimated COGS) × 90 = need COGS to confirm
  CCC = approx 25-35 days

Potential issues despite good DSO:
  1. Revenue recognition vs cash: if billing is end-of-month heavy, AR spikes temporarily
  2. AP payment behavior: if you're paying invoices early (day 5 of Net 30 terms), you're 
     giving suppliers a 25-day float for free — roughly $58k in "gifted" working capital
  3. High AR concentration: if 20% of customers account for 80% of AR, one slow payer 
     tanks your cash position

Next step: Pull AR aging report from QBO. If 30+ day buckets are > 15% of AR, 
that's your primary fix. Also check when you're actually paying AP.
```

---

## Integration Points

- **`qbo-automation`** — Pull AR aging, AP aging, and balance sheet data directly from QuickBooks Online
- **`ar-collections-agent`** — Execute collection workflows on identified aging accounts
- **`thirteen-week-cash-flow`** — Feed working capital metrics into 13-week rolling cash forecast
- **`kpi-alert-system`** — Set DSO/DPO threshold alerts for ongoing monitoring
- **`vendor-payment-optimizer`** — Detailed AP vendor-by-vendor payment term analysis
- **`financial-analysis-agent`** — Full financial health assessment including working capital context
- **`budget-vs-actual`** — Compare working capital targets vs actuals over time

---

## Quick Reference Formulas

```
DSO = (AR / Revenue) × Period Days
DPO = (AP / COGS) × Period Days
DIO = (Inventory / COGS) × Period Days
CCC = DSO + DIO - DPO

Working Capital = Current Assets - Current Liabilities
Net Working Capital = AR + Inventory - AP (operating focus)

Current Ratio = Current Assets / Current Liabilities  (target ≥ 1.5)
Quick Ratio   = (Cash + AR) / Current Liabilities     (target ≥ 1.0)

Annual Cash Impact of 1-Day DSO Reduction = Annual Revenue / 365
Annual Cash Impact of 1-Day DPO Extension = Annual COGS / 365
```
