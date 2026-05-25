---
name: subscription-revenue-tracker
description: >
  SaaS and subscription business revenue intelligence. Track MRR/ARR, calculate churn rate,
  net revenue retention (NRR), customer lifetime value (LTV), cohort analysis, and payback periods.
  Connects to Stripe, Chargebee, or CSV exports for automated metric computation.
  Outputs investor-ready dashboards, board decks, and QBO journal entries for deferred revenue.
  Use when: building SaaS financial models, calculating subscription KPIs, preparing investor
  updates, analyzing cohort retention, or booking deferred revenue correctly in the GL.
  NOT for: one-time transaction businesses, ecommerce without subscriptions, crypto revenue
  (use defi-position-tracker), QBO data entry (use qbo-automation), or payroll processing.
metadata:
  category: finance
  tags: [saas, mrr, arr, churn, retention, cohort, stripe, subscription, ltv, revenue]
  requires:
    optional_bins: [stripe, python3, node, jq, curl]
    apis: [Stripe API, Chargebee API, QuickBooks Online API]
---

# Subscription Revenue Tracker

Track MRR/ARR, churn, NRR, cohort retention, and LTV for SaaS and subscription businesses. Produces investor-grade metrics and clean GL entries.

---

## Core Metrics Defined

| Metric | Formula | Why It Matters |
|--------|---------|----------------|
| MRR | Sum of all active recurring monthly revenue | Pulse of the business |
| ARR | MRR × 12 | Annualized scale metric for investors |
| New MRR | Revenue from new customers this month | Growth engine |
| Expansion MRR | Upgrades / upsells from existing customers | Efficiency signal |
| Contraction MRR | Downgrades from existing customers | Negative signal |
| Churned MRR | Revenue lost from cancellations | Retention health |
| Net New MRR | New + Expansion − Contraction − Churned | Net growth |
| Gross Churn Rate | Churned MRR / Beginning MRR | Revenue decay rate |
| Net Revenue Retention (NRR) | (Beginning + Expansion − Contraction − Churned) / Beginning | Growth from existing base |
| LTV | ARPU / Gross Churn Rate | Customer economic value |
| CAC | Sales + Marketing Spend / New Customers | Acquisition cost |
| LTV:CAC | LTV / CAC | Unit economics health (target: >3x) |
| Payback Period | CAC / (ARPU × Gross Margin) | Months to recover acquisition cost |

---

## Workflows

### 1. Pull MRR from Stripe

```bash
# List all active subscriptions with their amounts
stripe subscriptions list \
  --status=active \
  --limit=100 \
  --expand[]=data.items.data \
  2>&1 | jq '
    .data[] | {
      id: .id,
      customer: .customer,
      status: .status,
      current_period_start: (.current_period_start | strftime("%Y-%m-%d")),
      mrr: (.items.data[0].price.unit_amount / 100 * 
            (if .items.data[0].price.recurring.interval == "year" then 1/12 else 1 end))
    }
  '
```

**Get MRR summary via Stripe API (no CLI):**
```bash
curl "https://api.stripe.com/v1/subscriptions?status=active&limit=100&expand[]=data.items.data" \
  -u sk_live_YOUR_KEY: | jq '
  [.data[] | 
    (.items.data[0].price.unit_amount / 100) * 
    (if .items.data[0].price.recurring.interval == "year" then 1/12 else 1 end)
  ] | add
  '
```

**Python: Full MRR waterfall from Stripe events:**
```python
import stripe
from datetime import datetime, timezone
from collections import defaultdict
from dateutil.relativedelta import relativedelta

stripe.api_key = "sk_live_YOUR_KEY"

def get_mrr_waterfall(year: int, month: int) -> dict:
    """
    Calculate MRR waterfall for a given month.
    Returns: new, expansion, contraction, churned, net_new MRR.
    """
    # Period boundaries
    period_start = datetime(year, month, 1, tzinfo=timezone.utc)
    period_end = period_start + relativedelta(months=1)
    prev_start = period_start - relativedelta(months=1)

    # Get subscriptions active at start of period (denominator)
    beginning_subs = _get_active_subscriptions_at(prev_start)
    ending_subs = _get_active_subscriptions_at(period_end)

    # Categorize by customer
    beginning_customers = {s.customer: _get_mrr(s) for s in beginning_subs}
    ending_customers = {s.customer: _get_mrr(s) for s in ending_subs}

    new_mrr = 0.0
    expansion_mrr = 0.0
    contraction_mrr = 0.0
    churned_mrr = 0.0

    all_customers = set(beginning_customers) | set(ending_customers)

    for cust_id in all_customers:
        begin_val = beginning_customers.get(cust_id, 0.0)
        end_val = ending_customers.get(cust_id, 0.0)
        delta = end_val - begin_val

        if begin_val == 0 and end_val > 0:
            new_mrr += end_val
        elif begin_val > 0 and end_val == 0:
            churned_mrr += begin_val
        elif delta > 0:
            expansion_mrr += delta
        elif delta < 0:
            contraction_mrr += abs(delta)

    beginning_mrr = sum(beginning_customers.values())

    return {
        "period": f"{year}-{month:02d}",
        "beginning_mrr": beginning_mrr,
        "new_mrr": new_mrr,
        "expansion_mrr": expansion_mrr,
        "contraction_mrr": contraction_mrr,
        "churned_mrr": churned_mrr,
        "net_new_mrr": new_mrr + expansion_mrr - contraction_mrr - churned_mrr,
        "ending_mrr": beginning_mrr + new_mrr + expansion_mrr - contraction_mrr - churned_mrr,
        "gross_churn_rate": churned_mrr / beginning_mrr if beginning_mrr else 0,
        "nrr": (beginning_mrr + expansion_mrr - contraction_mrr - churned_mrr) / beginning_mrr if beginning_mrr else 0,
    }

def _get_mrr(subscription) -> float:
    """Extract normalized monthly value from a Stripe subscription."""
    item = subscription.get("items", {}).get("data", [{}])[0]
    price = item.get("price", {})
    amount = price.get("unit_amount", 0) / 100
    qty = item.get("quantity", 1)
    interval = price.get("recurring", {}).get("interval", "month")
    
    if interval == "year":
        return (amount * qty) / 12
    elif interval == "week":
        return (amount * qty) * 4.333
    return amount * qty

def _get_active_subscriptions_at(timestamp: datetime) -> list:
    """Get subscriptions that were active at a given timestamp."""
    ts = int(timestamp.timestamp())
    subs = stripe.Subscription.list(
        status="all",
        created={"lte": ts},
        limit=100
    )
    return [
        s for s in subs.auto_paging_iter()
        if s.current_period_start <= ts <= (s.canceled_at or ts + 1)
    ]
```

### 2. Cohort Analysis

Track retention by signup cohort — the gold standard for understanding retention quality:

```python
import pandas as pd
import numpy as np

def build_cohort_table(subscription_events: pd.DataFrame) -> pd.DataFrame:
    """
    Build monthly cohort retention table.
    
    Input columns: customer_id, event_type (started/churned), event_month (YYYY-MM)
    Output: matrix of cohort × months_since_start → retention percentage
    
    Example output:
    cohort    | M+0  | M+1  | M+2  | M+3  | M+6  | M+12
    2025-01   | 100% | 87%  | 79%  | 74%  | 65%  | 54%
    2025-02   | 100% | 91%  | 83%  | 78%  | --   | --
    """
    # Assign cohort (month of first subscription)
    first_sub = (subscription_events[subscription_events.event_type == "started"]
                 .groupby("customer_id")["event_month"]
                 .min()
                 .reset_index()
                 .rename(columns={"event_month": "cohort"}))
    
    df = subscription_events.merge(first_sub, on="customer_id")
    df["cohort"] = pd.to_datetime(df["cohort"])
    df["event_month"] = pd.to_datetime(df["event_month"])
    df["months_since_start"] = (
        (df["event_month"].dt.year - df["cohort"].dt.year) * 12 +
        (df["event_month"].dt.month - df["cohort"].dt.month)
    )
    
    # Active customers per cohort per month
    active = (df[df.event_type != "churned"]
              .groupby(["cohort", "months_since_start"])["customer_id"]
              .nunique()
              .reset_index()
              .rename(columns={"customer_id": "active_customers"}))
    
    cohort_table = active.pivot(
        index="cohort", 
        columns="months_since_start", 
        values="active_customers"
    )
    
    # Normalize to cohort size (M+0 = 100%)
    cohort_sizes = cohort_table[0]
    retention_table = cohort_table.divide(cohort_sizes, axis=0) * 100
    
    return retention_table.round(1)


def average_retention_curve(cohort_table: pd.DataFrame, min_cohorts: int = 3) -> pd.Series:
    """
    Compute average retention curve across cohorts with enough data.
    Used for LTV projection.
    """
    # Only include cohorts with at least min_cohorts data points per period
    valid_cols = cohort_table.columns[cohort_table.notna().sum() >= min_cohorts]
    return cohort_table[valid_cols].mean()
```

### 3. LTV and Unit Economics

```python
def calculate_ltv(arpu: float, gross_margin: float, monthly_churn_rate: float) -> dict:
    """
    Calculate Customer Lifetime Value and payback metrics.
    
    Args:
        arpu: Average Revenue Per User per month
        gross_margin: Gross margin % (0.0-1.0)
        monthly_churn_rate: Monthly revenue churn rate (0.0-1.0)
    
    Returns:
        LTV, gross profit LTV, and key benchmarks
    """
    if monthly_churn_rate <= 0:
        raise ValueError("Churn rate must be > 0 for LTV calculation")
    
    avg_customer_lifetime_months = 1 / monthly_churn_rate
    ltv_revenue = arpu * avg_customer_lifetime_months
    ltv_gross_profit = ltv_revenue * gross_margin
    
    return {
        "arpu_monthly": arpu,
        "arpu_annual": arpu * 12,
        "monthly_churn_rate": monthly_churn_rate,
        "avg_lifetime_months": avg_customer_lifetime_months,
        "ltv_revenue": ltv_revenue,
        "ltv_gross_profit": ltv_gross_profit,
        "benchmarks": {
            "saas_target_ltv_cac": ">3x",
            "saas_target_payback": "<12 months",
            "saas_target_nrr": ">100%",
        }
    }


def payback_period(cac: float, arpu: float, gross_margin: float) -> dict:
    """
    Calculate CAC payback period in months.
    
    Healthy SaaS: <12 months
    Great SaaS: <6 months
    Struggling: >18 months
    """
    monthly_gross_profit_per_customer = arpu * gross_margin
    if monthly_gross_profit_per_customer <= 0:
        return {"payback_months": float("inf"), "status": "never — negative gross margin"}
    
    months = cac / monthly_gross_profit_per_customer
    
    if months < 6:
        status = "excellent"
    elif months < 12:
        status = "healthy"
    elif months < 18:
        status = "acceptable"
    else:
        status = "concerning"
    
    return {
        "cac": cac,
        "arpu_monthly": arpu,
        "gross_margin": gross_margin,
        "payback_months": round(months, 1),
        "payback_status": status,
    }
```

### 4. CSV Import (Non-Stripe Businesses)

For businesses without Stripe — import from any billing system:

```python
# Expected CSV format:
# customer_id, plan_name, mrr, start_date, end_date (blank if active), currency

import pandas as pd
from datetime import datetime

def load_subscriptions_from_csv(path: str, as_of_date: str = None) -> pd.DataFrame:
    """
    Load subscription data from a CSV export.
    Handles Chargebee, Recurly, Zuora, or manual exports.
    
    Required columns: customer_id, mrr, start_date
    Optional: end_date, plan_name, currency
    """
    df = pd.read_csv(path)
    df["start_date"] = pd.to_datetime(df["start_date"])
    if "end_date" in df.columns:
        df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    
    if as_of_date:
        cutoff = pd.Timestamp(as_of_date)
        # Active = started before cutoff AND (not ended OR ended after cutoff)
        df = df[
            (df["start_date"] <= cutoff) &
            (df.get("end_date", pd.NaT).isna() | (df.get("end_date", pd.NaT) > cutoff))
        ]
    
    # Standardize MRR (handle annual → monthly)
    if "billing_interval" in df.columns:
        df.loc[df.billing_interval == "annual", "mrr"] /= 12
    
    return df


def compute_metrics_from_csv(csv_path: str, period: str) -> dict:
    """
    Full metrics computation from CSV for a given YYYY-MM period.
    """
    year, month = map(int, period.split("-"))
    
    # Current and previous month active subs
    period_end = datetime(year, month, 28)  # safe month-end
    prev_period_end = datetime(year, month - 1 if month > 1 else 12, 28)
    
    current = load_subscriptions_from_csv(csv_path, period_end.strftime("%Y-%m-%d"))
    previous = load_subscriptions_from_csv(csv_path, prev_period_end.strftime("%Y-%m-%d"))
    
    curr_by_cust = current.groupby("customer_id")["mrr"].sum()
    prev_by_cust = previous.groupby("customer_id")["mrr"].sum()
    
    new_customers = curr_by_cust.index.difference(prev_by_cust.index)
    churned_customers = prev_by_cust.index.difference(curr_by_cust.index)
    existing = curr_by_cust.index.intersection(prev_by_cust.index)
    
    expansion = (curr_by_cust[existing] - prev_by_cust[existing]).clip(lower=0).sum()
    contraction = (prev_by_cust[existing] - curr_by_cust[existing]).clip(lower=0).sum()
    
    beginning_mrr = prev_by_cust.sum()
    
    return {
        "period": period,
        "customer_count": len(curr_by_cust),
        "mrr": curr_by_cust.sum(),
        "arr": curr_by_cust.sum() * 12,
        "beginning_mrr": beginning_mrr,
        "new_mrr": curr_by_cust[new_customers].sum(),
        "expansion_mrr": expansion,
        "contraction_mrr": contraction,
        "churned_mrr": prev_by_cust[churned_customers].sum(),
        "net_new_mrr": curr_by_cust.sum() - beginning_mrr,
        "gross_churn_rate": prev_by_cust[churned_customers].sum() / beginning_mrr if beginning_mrr else 0,
        "nrr": (beginning_mrr + expansion - contraction - prev_by_cust[churned_customers].sum()) / beginning_mrr if beginning_mrr else 0,
        "arpu": curr_by_cust.mean(),
    }
```

### 5. Deferred Revenue GL Entries (QBO-Ready)

Subscription revenue must be recognized over the service period (ASC 606 / IFRS 15):

```python
from datetime import date
from dateutil.relativedelta import relativedelta

def deferred_revenue_schedule(
    invoice_date: date,
    invoice_amount: float,
    service_start: date,
    service_end: date,
    description: str
) -> list[dict]:
    """
    Generate monthly revenue recognition journal entries for an annual subscription.
    
    At invoice: Debit A/R, Credit Deferred Revenue
    Monthly: Debit Deferred Revenue, Credit Revenue
    
    Returns list of journal entries ready for QBO import.
    """
    total_days = (service_end - service_start).days
    entries = []
    
    # Initial: recognize deferred revenue liability
    entries.append({
        "date": invoice_date.isoformat(),
        "type": "invoice_booking",
        "description": f"Book deferred revenue — {description}",
        "debit_account": "Accounts Receivable",
        "credit_account": "Deferred Revenue",
        "amount": invoice_amount,
    })
    
    # Monthly recognition
    current_date = date(service_start.year, service_start.month, 1)
    
    while current_date <= service_end:
        # Days in this period
        period_end = min(
            date(current_date.year, current_date.month + 1, 1) - relativedelta(days=1),
            service_end
        )
        period_days = (period_end - max(current_date, service_start)).days + 1
        period_revenue = invoice_amount * (period_days / total_days)
        
        entries.append({
            "date": current_date.isoformat(),
            "type": "revenue_recognition",
            "description": f"Revenue recognition — {description} ({current_date.strftime('%b %Y')})",
            "debit_account": "Deferred Revenue",
            "credit_account": "Subscription Revenue",
            "amount": round(period_revenue, 2),
            "period_days": period_days,
        })
        
        current_date = date(current_date.year, current_date.month, 1) + relativedelta(months=1)
    
    return entries


# Example: $12,000 annual subscription
entries = deferred_revenue_schedule(
    invoice_date=date(2026, 1, 1),
    invoice_amount=12000.00,
    service_start=date(2026, 1, 1),
    service_end=date(2026, 12, 31),
    description="Acme Corp — Enterprise Plan"
)
# → 13 entries: 1 booking + 12 monthly recognition of $1,000 each
```

### 6. Investor-Ready Output

```python
def generate_investor_summary(metrics_history: list[dict]) -> dict:
    """
    Generate board/investor MRR summary from 12 months of metrics.
    
    Returns formatted dict suitable for pitch deck tables or Sheets export.
    """
    if len(metrics_history) < 2:
        raise ValueError("Need at least 2 months of data for growth calculations")
    
    latest = metrics_history[-1]
    prev_month = metrics_history[-2]
    twelve_months_ago = metrics_history[0] if len(metrics_history) >= 12 else None
    
    mom_growth = (latest["mrr"] - prev_month["mrr"]) / prev_month["mrr"] if prev_month["mrr"] else 0
    
    yoy_growth = None
    if twelve_months_ago and twelve_months_ago["mrr"]:
        yoy_growth = (latest["mrr"] - twelve_months_ago["mrr"]) / twelve_months_ago["mrr"]
    
    # Rule of 40: YoY Revenue Growth % + EBITDA Margin % >= 40 is healthy SaaS
    # (requires EBITDA margin input from financial model)
    
    return {
        "as_of": latest["period"],
        "mrr": f"${latest['mrr']:,.0f}",
        "arr": f"${latest['arr']:,.0f}",
        "mrr_mom_growth": f"{mom_growth:.1%}",
        "mrr_yoy_growth": f"{yoy_growth:.1%}" if yoy_growth is not None else "N/A",
        "nrr": f"{latest['nrr']:.1%}",
        "gross_churn": f"{latest['gross_churn_rate']:.2%}",
        "customer_count": latest["customer_count"],
        "arpu": f"${latest['arpu']:,.0f}",
        "new_mrr": f"${latest['new_mrr']:,.0f}",
        "expansion_mrr": f"${latest['expansion_mrr']:,.0f}",
        "churned_mrr": f"${latest['churned_mrr']:,.0f}",
        "net_new_mrr": f"${latest['net_new_mrr']:,.0f}",
        "benchmarks": {
            "nrr_status": "elite" if latest["nrr"] > 1.20 else "strong" if latest["nrr"] > 1.10 else "healthy" if latest["nrr"] > 1.00 else "concerning",
            "churn_status": "excellent" if latest["gross_churn_rate"] < 0.01 else "healthy" if latest["gross_churn_rate"] < 0.02 else "high",
        }
    }
```

---

## Benchmark Reference

### SaaS Health Benchmarks (2025)

| Metric | Best in Class | Healthy | Watch |
|--------|--------------|---------|-------|
| MoM MRR Growth | >15% | 5-15% | <5% |
| Gross Churn (monthly) | <0.5% | 0.5-2% | >2% |
| NRR | >120% | 100-120% | <100% |
| LTV:CAC | >5x | 3-5x | <3x |
| CAC Payback | <6 mo | 6-12 mo | >12 mo |
| Rule of 40 | >40 | 20-40 | <20 |

### Revenue Recognition (ASC 606)

- **Annual prepaid subscriptions:** Recognize monthly (1/12 per month)
- **Multi-year contracts:** Recognize over full term
- **Usage-based billing:** Recognize as consumed
- **Setup fees:** Recognize ratably with subscription unless distinct performance obligation

---

## Integration with Other Skills

- **startup-financial-model:** Feed MRR history and projections as revenue driver
- **kpi-alert-system:** Alert when churn > threshold or NRR drops below 100%
- **qbo-automation:** Import deferred revenue journal entries automatically
- **investor-memo-generator:** Pull MRR waterfall data for Section 3 (Financial Performance)
- **report-generator:** Generate monthly board report with cohort retention tables

---

## Not For This Skill

- **Executing Stripe API write operations** (refunds, subscription changes) — use a billing management skill
- **QBO data entry** — use qbo-automation after generating journal entries here
- **Crypto/DeFi revenue** — use defi-position-tracker
- **One-time product sales** without subscription component — use financial-analysis-agent
- **Payroll or employee compensation** — use payroll tools
- **Tax filing or 1099 generation** — use crypto-tax-agent or consult a CPA
- **on-chain-payroll or qbo-to-tax-bridge** — PTIN-backed Moltlaunch services, not ClawHub
