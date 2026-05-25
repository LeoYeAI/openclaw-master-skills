---
name: saas-churn-analysis
description: >
  SaaS churn and retention analysis: cohort-based churn rates, retention curves, revenue churn vs logo churn,
  at-risk customer identification, expansion vs contraction MRR, churn recovery playbooks, and net revenue
  retention (NRR) benchmarking. Produces investor-ready retention charts and actionable recovery plans.
  Use when: analyzing why customers are churning, building cohort retention tables, calculating NRR/GRR,
  identifying at-risk accounts before they cancel, or presenting retention data to investors/board.
  NOT for: executing churn recovery outreach (use CRM/email tools), real-time subscription billing changes
  (use billing platform APIs), general SaaS KPI dashboards (use saas-metrics-dashboard), or revenue
  forecasting without churn context (use startup-financial-model).
version: 1.0.0
author: PrecisionLedger
tags:
  - saas
  - churn
  - retention
  - cohort
  - nrr
  - subscription
  - metrics
  - investors
---

# SaaS Churn Analysis Skill

Deep-dive churn and retention analysis for SaaS businesses. Build cohort tables, calculate NRR/GRR, identify at-risk accounts, and produce investor-ready retention metrics with actionable recovery playbooks.

---

## When to Use This Skill

**Trigger phrases:**
- "Why are customers churning?"
- "What's our retention rate?"
- "Build a cohort analysis"
- "Show me net revenue retention"
- "Which accounts are at risk of canceling?"
- "Investor wants to see our logo churn"
- "What's our gross/net dollar retention?"
- "Analyze our expansion vs contraction MRR"

**NOT for:**
- Executing recovery outreach (emails, calls) — use CRM/email tools
- Billing changes, refunds, or cancellation processing — use billing platform
- General MRR tracking — use `saas-metrics-dashboard` or `subscription-revenue-tracker`
- Revenue forecasting — use `startup-financial-model`
- Customer success management — use a CS platform skill

---

## Core Churn Definitions

### Logo Churn (Customer Churn)
```
Logo Churn Rate (monthly) = Customers Lost / Customers at Start of Period

Example:
  Start of month: 200 customers
  Canceled: 5
  Logo churn rate: 5/200 = 2.5%
```

### Revenue Churn
```
Gross Revenue Churn Rate = MRR Lost to Cancellations / MRR at Start of Period

Example:
  Start MRR: $100,000
  Churned MRR: $4,000 (from cancellations)
  Gross churn: 4%
```

### Net Revenue Retention (NRR / NDR)
```
NRR = (Beginning MRR + Expansion MRR - Contraction MRR - Churned MRR) / Beginning MRR × 100

Components:
  + Expansion MRR: upsells, upgrades, seat additions from existing customers
  - Contraction MRR: downgrades, reduced seats
  - Churned MRR: cancellations

Example:
  Beginning MRR: $100,000
  Expansion: +$8,000
  Contraction: -$2,000
  Churn: -$4,000
  NRR = ($100,000 + $8,000 - $2,000 - $4,000) / $100,000 = 102%
```

**NRR Benchmarks (SaaS industry):**
| NRR | Signal |
|-----|--------|
| >120% | Elite (enterprise, product-led) |
| 110–120% | Strong — expansion > churn |
| 100–110% | Healthy |
| 90–100% | Adequate — watch churn trends |
| <90% | Red flag — structural problem |

### Gross Revenue Retention (GRR)
```
GRR = (Beginning MRR - Contraction MRR - Churned MRR) / Beginning MRR × 100
     (excludes expansion — pure retention, no upsell credit)

Healthy GRR benchmarks:
  Enterprise SaaS: >90%
  Mid-market: >85%
  SMB SaaS: >75%
```

---

## Cohort Analysis

### Building a Cohort Retention Table

Track customers by their **acquisition month** and measure % remaining in each subsequent month:

```python
import pandas as pd
from datetime import datetime

def build_cohort_table(subscriptions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a cohort retention table from subscription data.
    
    Input DataFrame columns:
        - customer_id: str
        - signup_date: datetime
        - cancel_date: datetime | None (None = still active)
    
    Returns:
        Pivot table: rows = cohort month, columns = months_since_signup,
        values = retention percentage
    """
    df = subscriptions_df.copy()
    df['cohort_month'] = df['signup_date'].dt.to_period('M')
    df['active_through'] = df['cancel_date'].fillna(pd.Timestamp.now())
    
    rows = []
    for cohort, group in df.groupby('cohort_month'):
        cohort_size = len(group)
        for month_offset in range(0, 25):  # 0–24 months
            cutoff = cohort.to_timestamp() + pd.DateOffset(months=month_offset)
            active = group[group['active_through'] >= cutoff].shape[0]
            retention = active / cohort_size * 100
            rows.append({
                'cohort': str(cohort),
                'month': month_offset,
                'cohort_size': cohort_size,
                'active': active,
                'retention_pct': round(retention, 1)
            })
    
    result = pd.DataFrame(rows)
    pivot = result.pivot(index='cohort', columns='month', values='retention_pct')
    return pivot
```

**Example cohort table output:**
```
Cohort     | M0    | M1    | M3    | M6    | M12
-----------|-------|-------|-------|-------|------
2025-01    | 100%  | 91%   | 81%   | 72%   | 58%
2025-02    | 100%  | 93%   | 84%   | 76%   | —
2025-03    | 100%  | 89%   | 79%   | —     | —
2025-04    | 100%  | 94%   | —     | —     | —
```

### Revenue Cohort (Dollar Retention)

Track MRR retained and expanded per cohort:

```python
def revenue_cohort_table(mrr_events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Revenue cohort analysis tracking MRR per acquisition cohort.
    
    Input DataFrame columns:
        - customer_id: str
        - event_date: datetime
        - event_type: str  # 'signup', 'expansion', 'contraction', 'churn'
        - mrr_change: float
    
    Returns:
        Cohort revenue retention table (% of original MRR retained+expanded)
    """
    # Group by signup cohort
    signups = mrr_events_df[mrr_events_df['event_type'] == 'signup'].copy()
    signups['cohort_month'] = signups['event_date'].dt.to_period('M')
    
    # For each cohort, track MRR over time
    # NRR by cohort = sum(all MRR changes for cohort customers) / initial MRR
    pass
```

### Churn Curve Analysis

Identify when in the customer lifecycle churn peaks:

```
Early churn (M1-M3): Onboarding failure, value not delivered
  → Diagnosis: activation rate, time-to-first-value, support tickets
  
Mid-term churn (M4-M12): Competitive displacement, budget cuts
  → Diagnosis: NPS trends, feature adoption, renewal engagement
  
Late churn (M12+): Strategic shifts, contract terms, enterprise competition
  → Diagnosis: executive sponsor changes, usage trends, renewal conversations
```

**Churn by tenure bucket:**
```python
def churn_by_tenure(subscriptions_df: pd.DataFrame) -> dict:
    """Calculate churn rate for different tenure buckets."""
    buckets = {
        '0-3mo': (0, 90),
        '3-6mo': (90, 180),
        '6-12mo': (180, 365),
        '12-24mo': (365, 730),
        '24mo+': (730, float('inf'))
    }
    
    results = {}
    for bucket_name, (min_days, max_days) in buckets.items():
        mask = (
            (subscriptions_df['tenure_days'] >= min_days) &
            (subscriptions_df['tenure_days'] < max_days)
        )
        bucket_df = subscriptions_df[mask]
        if len(bucket_df) == 0:
            continue
        churned = bucket_df[bucket_df['cancel_date'].notna()].shape[0]
        results[bucket_name] = {
            'total_customers': len(bucket_df),
            'churned': churned,
            'churn_rate_pct': round(churned / len(bucket_df) * 100, 1)
        }
    return results
```

---

## At-Risk Customer Identification

### Churn Risk Scoring

Score each active customer by leading indicators:

```python
CHURN_RISK_WEIGHTS = {
    'days_since_last_login': 0.25,       # Usage drop
    'feature_adoption_pct': -0.20,       # Inverse: more features = lower risk
    'support_tickets_30d': 0.15,         # Escalations
    'nps_score': -0.15,                  # Inverse: high NPS = lower risk
    'days_to_renewal': -0.10,            # Closer renewal = higher urgency
    'billing_failures_90d': 0.15,        # Payment issues
}

def churn_risk_score(customer: dict) -> float:
    """
    Calculate 0-100 churn risk score for a customer.
    Higher = more likely to churn.
    
    Inputs:
        customer: dict with keys matching CHURN_RISK_WEIGHTS
    
    Returns:
        Risk score 0-100 (>70 = high risk, 40-70 = medium, <40 = low)
    """
    raw_score = 0
    for factor, weight in CHURN_RISK_WEIGHTS.items():
        if factor in customer:
            # Normalize each factor to 0-100 scale first
            normalized = normalize_factor(factor, customer[factor])
            raw_score += normalized * weight
    
    # Scale to 0-100
    return max(0, min(100, raw_score * 100 + 50))

def get_at_risk_accounts(customers: list, threshold: float = 70.0) -> list:
    """Return customers with churn risk score above threshold, sorted by MRR."""
    at_risk = [
        {**c, 'risk_score': churn_risk_score(c)}
        for c in customers
    ]
    return sorted(
        [c for c in at_risk if c['risk_score'] >= threshold],
        key=lambda x: x.get('mrr', 0),
        reverse=True  # Highest MRR first — prioritize by revenue impact
    )
```

### Early Warning Signals

**Usage-based signals (product telemetry):**
```
🔴 High risk:
  - No login in 14+ days (was weekly user)
  - DAU/MAU ratio dropped >50% MoM
  - Core feature not used in 30 days
  - Below 20% feature adoption vs peers

🟡 Medium risk:
  - Login frequency dropped >30% MoM
  - Support ticket with "cancel" or "refund" keyword
  - NPS score ≤ 6 (detractor)
  - Seat count reduced

🟢 Healthy signals:
  - Expanded seats or upgraded tier
  - Used 3+ core features this month
  - NPS ≥ 9 (promoter)
  - Referred another customer
```

**Financial signals:**
```
🔴 High risk:
  - Payment failure (retry in progress)
  - Requested invoice-based payment shift (budget freeze)
  - Contract not opened with 30 days to renewal

🟡 Medium risk:
  - Asked about pricing alternatives
  - Billing contact changed
  - Discount request submitted
```

---

## MRR Movement Analysis

### MRR Bridge

Decompose monthly MRR change into components:

```
MRR Bridge: January → February

Beginning MRR:     $100,000
+ New Business:      +$8,500   (23 new customers × $370 avg)
+ Expansion:         +$3,200   (upgrades + seat additions)
- Contraction:       -$1,100   (downgrades + seat reductions)
- Churn:             -$4,300   (11 cancellations × $390 avg)
= Ending MRR:      $106,300

Net New MRR:        +$6,300
MoM Growth:          6.3%
```

**Python MRR bridge calculation:**
```python
from dataclasses import dataclass

@dataclass
class MRRBridge:
    period: str
    beginning_mrr: float
    new_mrr: float           # New customers
    expansion_mrr: float     # Upsells/upgrades
    contraction_mrr: float   # Downgrades (negative or positive — store as positive)
    churned_mrr: float       # Cancellations (store as positive)
    
    @property
    def ending_mrr(self) -> float:
        return self.beginning_mrr + self.new_mrr + self.expansion_mrr - self.contraction_mrr - self.churned_mrr
    
    @property
    def net_new_mrr(self) -> float:
        return self.ending_mrr - self.beginning_mrr
    
    @property
    def growth_rate_pct(self) -> float:
        return self.net_new_mrr / self.beginning_mrr * 100 if self.beginning_mrr else 0
    
    @property
    def quick_ratio(self) -> float:
        """SaaS Quick Ratio = (New + Expansion) / (Contraction + Churn). >4 = healthy."""
        numerator = self.new_mrr + self.expansion_mrr
        denominator = self.contraction_mrr + self.churned_mrr
        return numerator / denominator if denominator else float('inf')
    
    def to_summary(self) -> str:
        return (
            f"MRR Bridge ({self.period})\n"
            f"  Beginning: ${self.beginning_mrr:,.0f}\n"
            f"  + New:       ${self.new_mrr:,.0f}\n"
            f"  + Expansion: ${self.expansion_mrr:,.0f}\n"
            f"  - Contraction: ${self.contraction_mrr:,.0f}\n"
            f"  - Churn:     ${self.churned_mrr:,.0f}\n"
            f"  = Ending:  ${self.ending_mrr:,.0f}\n"
            f"  Growth: {self.growth_rate_pct:.1f}% | Quick Ratio: {self.quick_ratio:.1f}x"
        )
```

**SaaS Quick Ratio benchmarks:**
| Quick Ratio | Signal |
|-------------|--------|
| >4 | Elite growth efficiency |
| 2–4 | Healthy |
| 1–2 | Growing but inefficient — churn drag |
| <1 | Shrinking — churn exceeds new + expansion |

---

## Churn Recovery Playbooks

### Playbook 1: Early Churn (Month 1-3)

**Root cause:** Failed onboarding, didn't reach first value moment

**Diagnosis questions:**
```
□ Did they complete onboarding? (activation rate)
□ Did they use the core feature at least once? (activation event)
□ How long did it take to reach first value moment?
□ Did they get a human touchpoint in first 48 hours?
```

**Recovery actions:**
```
Day 1-7:   Personal outreach from CSM — "What would make this a 10/10?"
Day 7-14:  Offer 1:1 onboarding session + extend trial if applicable
Day 14-21: Share customer success story in their industry/use case
Day 21-30: Executive touchpoint if MRR > $500/mo
```

### Playbook 2: Mid-Term Churn (Month 4-12)

**Root cause:** Value plateau, competitive evaluation, budget pressure

**Diagnosis questions:**
```
□ Usage trend: up, flat, or declining in last 60 days?
□ When did they last use the feature most tied to their stated goal?
□ Any support escalations or complaints in the last 90 days?
□ Have they been pitched by a competitor? (ask directly)
□ Is this a budget-driven decision or product-driven?
```

**Recovery actions by root cause:**
```
Budget:
  → Offer pause plan (90-day pause vs cancel)
  → Right-size to smaller plan vs lose them entirely
  → Annual prepay at 20% discount to lock in

Product gaps:
  → Roadmap call with PM — "here's what's coming"
  → Workaround documentation for their specific use case
  → Connect to power-user customer for peer validation

Competitor evaluation:
  → Direct competitive comparison matrix
  → Migration cost analysis (switching is expensive)
  → Win-back offer if they've already left (45-day re-engagement)
```

### Playbook 3: Renewal-at-Risk (30-60 days to renewal)

**Proactive renewal pipeline:**
```
60 days out:
  □ Usage review: send personalized "Your results with [Product]" email
  □ Identify any open issues — resolve before renewal conversation

45 days out:
  □ QBR or check-in call — confirm value, surface upsell opportunity
  □ Flag to AE if NPS < 7 or usage declining

30 days out:
  □ Renewal proposal sent — include current plan + upsell option
  □ Executive sponsor confirmation (for accounts >$1k/mo)

14 days out:
  □ Follow-up if no response — switch to phone
  □ Escalate to manager if no reply

7 days out:
  □ Final decision call — accept reduced terms if needed to retain
```

---

## Output Formats

### Investor-Ready Retention Summary

```json
{
  "period": "Q4 2025",
  "generated_at": "2026-01-15",
  "retention_metrics": {
    "logo_churn_rate_monthly": 2.1,
    "mrr_gross_churn_rate_monthly": 3.8,
    "net_revenue_retention_pct": 108,
    "gross_revenue_retention_pct": 96.2,
    "quick_ratio": 3.2
  },
  "mrr_bridge": {
    "beginning_mrr": 285000,
    "new_mrr": 42000,
    "expansion_mrr": 18500,
    "contraction_mrr": 4200,
    "churned_mrr": 10800,
    "ending_mrr": 330500
  },
  "at_risk_pipeline": {
    "high_risk_count": 8,
    "high_risk_mrr_at_risk": 24600,
    "medium_risk_count": 15,
    "medium_risk_mrr_at_risk": 38200
  },
  "cohort_highlights": {
    "best_cohort": { "month": "2025-03", "m12_retention": 74 },
    "worst_cohort": { "month": "2025-08", "m3_retention": 71 },
    "avg_m12_retention": 68.5
  },
  "benchmarks": {
    "nrr_vs_industry": "above_median",
    "grr_vs_industry": "top_quartile",
    "logo_churn_vs_industry": "median"
  }
}
```

### CSV Export for Spreadsheets

```
cohort_retention_csv_template:
Cohort,Size,M1,M2,M3,M6,M9,M12,M18,M24
2025-01,45,91%,84%,81%,73%,67%,61%,55%,49%
2025-02,52,93%,87%,83%,—,—,—,—,—
...
```

---

## Step-by-Step Workflow

### Full Churn Audit

**Step 1: Data collection**
```
□ Customer list with signup date and cancel date (if churned)
□ MRR per customer per month (last 12 months)
□ Usage data: logins, feature events (from product analytics)
□ NPS scores if available
□ Cancellation reason codes (from offboarding flow)
```

**Step 2: Calculate headline metrics**
- Logo churn rate (monthly and annualized)
- Gross and net revenue retention
- Quick ratio
- Churn by tenure bucket

**Step 3: Build cohort table**
- M0–M12 retention by acquisition cohort
- Identify best and worst cohorts — find what's different

**Step 4: MRR bridge (last 6 months)**
- New vs expansion vs contraction vs churn
- Trend analysis: is churn improving or worsening?

**Step 5: At-risk identification**
- Score all active customers by churn risk signals
- Prioritize by MRR at risk (highest first)
- Output: top 10 at-risk accounts with reasons

**Step 6: Root cause analysis**
- What's driving churn? (onboarding failure, competition, budget, product gaps)
- Which segments have highest churn? (plan size, industry, use case, acquisition channel)

**Step 7: Recommend playbook**
- Match root cause to recovery playbook
- Estimate MRR at stake if intervention succeeds (recovery potential)
- Prioritize actions by expected ROI

---

## Churn by Segment Analysis

Segment churn to find structural patterns:

```python
def churn_by_segment(subscriptions_df: pd.DataFrame, segment_col: str) -> pd.DataFrame:
    """
    Calculate churn rate by customer segment.
    
    Args:
        segment_col: column name to segment by (e.g., 'plan', 'industry', 'company_size')
    
    Returns:
        DataFrame with churn rate per segment, sorted by MRR impact
    """
    results = []
    for segment, group in subscriptions_df.groupby(segment_col):
        total = len(group)
        churned = group[group['cancel_date'].notna()].shape[0]
        total_mrr = group['mrr'].sum()
        churned_mrr = group[group['cancel_date'].notna()]['mrr'].sum()
        
        results.append({
            'segment': segment,
            'total_customers': total,
            'churned_customers': churned,
            'logo_churn_pct': round(churned / total * 100, 1),
            'total_mrr': total_mrr,
            'churned_mrr': churned_mrr,
            'mrr_churn_pct': round(churned_mrr / total_mrr * 100, 1) if total_mrr else 0
        })
    
    return pd.DataFrame(results).sort_values('churned_mrr', ascending=False)
```

**Key segments to analyze:**
- By plan tier (free trial → paid → enterprise)
- By acquisition channel (organic, paid, referral)
- By company size (SMB, mid-market, enterprise)
- By industry vertical
- By geographic region
- By sales rep / CSM (is one rep's book churning faster?)

---

## Integration Points

- **`saas-metrics-dashboard`** — Display NRR, GRR, and churn rate KPIs in dashboard
- **`kpi-alert-system`** — Trigger alerts when monthly churn exceeds threshold
- **`startup-financial-model`** — Feed churn rate assumptions into revenue forecasts
- **`subscription-revenue-tracker`** — MRR bridge data source for churn calculations
- **`crypto-tax-agent`** — N/A (different domain)

---

## Key Formulas Cheat Sheet

```
Logo Churn Rate (monthly)  = Customers Lost / Customers at Start × 100
Annual Logo Churn          = 1 - (1 - monthly_churn)^12 × 100
Gross Revenue Retention    = (BOM MRR - Contraction - Churn) / BOM MRR × 100
Net Revenue Retention      = (BOM MRR + Expansion - Contraction - Churn) / BOM MRR × 100
Quick Ratio                = (New MRR + Expansion MRR) / (Contraction MRR + Churned MRR)
LTV (with churn)           = ARPU / Monthly Churn Rate
Avg Customer Lifetime      = 1 / Monthly Churn Rate (in months)

Rule of Thumb:
  2% monthly logo churn  = ~21% annual churn (B2B SMB benchmark)
  0.5% monthly logo churn = ~6% annual churn (enterprise benchmark)
  NRR >100% means you grow from existing base alone — key investor signal
```
