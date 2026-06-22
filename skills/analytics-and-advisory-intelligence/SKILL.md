---
name: analytics-and-advisory-intelligence
description: Cross-client analytics for Greek accounting firms. Surfaces trends, anomalies, and risks across financial data. Read-only, outputs to /data/reports/.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "analytics", "advisory", "trends", "benchmarking"]
metadata: {"openclaw": {"requires": {"bins": ["jq"], "env": ["OPENCLAW_DATA_DIR"]}, "notes": "Instruction-only skill. Analyzes financial data from OPENCLAW_DATA_DIR to generate trend reports and advisory insights. No external services or credentials required."}}
---

# Analytics and Advisory Intelligence

The previous 17 skills process, file, store, and protect. This skill thinks. It reads across all the data the system has built up and asks: what does this mean? What should the accountant know that they have not thought to ask?

An accountant managing 40 clients cannot spot a VAT liability trend building across one client's 12 months of data while simultaneously processing another client's payroll and preparing a third client's annual tax return. This skill does the cross-sectional, longitudinal reading that busy humans cannot. It surfaces the finding. The accountant decides what to do with it.

This skill is purely advisory. It reads, analyses, and reports. It never takes action, never modifies client records, and never submits anything. Every insight it surfaces is a prompt for human judgement, not a trigger for automated action.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
which jq || sudo apt install jq
```

No external credentials required. Analyzes financial data from local files to generate trend reports and advisory insights.


## Core Philosophy

- **Proactive, Not Reactive**: The system already handles reactive work. This skill looks ahead — identifying problems before they become crises and opportunities before they are missed
- **Cross-Client Vision**: No single-client skill can see patterns that span the portfolio. This skill aggregates anonymised data across clients to detect sector trends, identify outliers, and benchmark clients against peers
- **Plain English Findings**: Every output is written for accounting assistants. No statistical jargon, no unexplained numbers. Finding + evidence + suggested action
- **Confidence-Rated**: Every finding carries a confidence level. A pattern with three data points is labelled differently from one with 18. The accountant knows how much weight to give each insight
- **Read-Only Always**: This skill reads from all data sources but writes only to /data/reports/analytics/. It has no write access to /data/clients/, /data/compliance/, or any operational directory
- **Overnight Operation**: Heavy analysis runs outside business hours. Lightweight queries run on demand but are bounded by pre-computed daily outputs

---

## OpenClaw Commands

### Portfolio-Level Analysis
```bash
openclaw analytics portfolio-health --all-clients --period 2026-01
openclaw analytics portfolio-health --all-clients --period 2026-01 --rank-by risk
openclaw analytics compliance-risk --all-clients --period 2026-01
openclaw analytics compliance-risk --all-clients --flag-high-risk
openclaw analytics compliance-risk --sector retail --compare-to-sector
openclaw analytics workload --all-clients --period 2026-01 --by-accountant
openclaw analytics workload --forecast --next-quarter
openclaw analytics benchmark --afm EL123456789 --vs-sector retail --period 2026-01
openclaw analytics benchmark --afm EL123456789 --vs-sector retail --last 6-months
```

### Client-Level Analysis
```bash
openclaw analytics client-risk --afm EL123456789
openclaw analytics client-risk --afm EL123456789 --verbose
openclaw analytics trends --afm EL123456789 --metric vat-liability --last 12-months
openclaw analytics trends --afm EL123456789 --metric gross-margin --last 6-months
openclaw analytics trends --afm EL123456789 --all-metrics --period 2025
openclaw analytics anomalies --afm EL123456789 --period 2026-01
openclaw analytics anomalies --afm EL123456789 --last 6-months --flag-significant
openclaw analytics cashflow-forecast --afm EL123456789 --horizon 3-months
openclaw analytics cashflow-forecast --afm EL123456789 --horizon 3-months --include-tax-payments
openclaw analytics tax-planning --afm EL123456789 --year 2026
openclaw analytics tax-planning --afm EL123456789 --year 2026 --include-scenarios
```

### Anomaly Detection
```bash
openclaw analytics supplier-overlap --all-clients --flag-unusual
openclaw analytics supplier-overlap --threshold 5-clients
openclaw analytics expense-anomalies --all-clients --period 2026-01
openclaw analytics expense-anomalies --afm EL123456789 --vs-prior-periods
openclaw analytics vat-rate-check --all-clients --period 2026-01
openclaw analytics vat-rate-check --afm EL123456789 --last 6-months
```

### Scheduled Reports and Advisory
```bash
openclaw analytics morning-advisory --date today
openclaw analytics morning-advisory --date today --high-risk-only
openclaw analytics monthly-report --period 2026-01 --all-clients
openclaw analytics monthly-report --period 2026-01 --format pdf
openclaw analytics quarterly-review --quarter 2026-Q1 --all-clients
openclaw analytics ask --query "which clients have increasing VAT liability over the last 6 months"
openclaw analytics ask --query "which clients are at risk of not meeting their Q2 tax payment"
openclaw analytics ask --query "are there any expense categories that look unusual this month"
```

---

## Analysis Modules

### 1. Compliance Risk Scoring

Every client receives a compliance risk score on a 1-10 scale, computed nightly. Feeds the dashboard portfolio view and morning advisory.

```yaml
Compliance_Risk_Score:
  inputs:
    - Late filings in the last 12 months (weight: 30%)
    - Compliance gaps currently open (weight: 25%)
    - Missing documents pending more than 14 days (weight: 20%)
    - AADE penalty history (weight: 15%)
    - Days until next deadline vs documents received (weight: 10%)

  score_bands:
    1-3: "Low risk — all obligations current, no gaps"
    4-6: "Medium risk — minor gaps or historical delays"
    7-8: "High risk — active gaps or recent penalties"
    9-10: "Critical — immediate attention required"

  output_location: "/data/reports/analytics/{YYYY-MM-DD}_risk-scores.json"
  refreshed: "Nightly at 01:00 Athens time"
```

### 2. Financial Trend Analysis

Reads Skill 15 financial statement outputs across multiple periods to detect directional movement.

```yaml
Financial_Trends:
  metrics_tracked:
    gross_margin:
      calculation: "(Revenue - Cost of Sales) / Revenue"
      alert_threshold: "Drop of more than 5 percentage points vs same period last year"
      finding_template: "{Client} gross margin has fallen from {X}% to {Y}% — {delta}pp decline over {N} months. Primary driver appears to be {top expense category change}."

    vat_liability_trend:
      calculation: "Net VAT payable per period"
      alert_threshold: "Increase of more than 20% vs prior 3-month average"
      finding_template: "{Client} VAT liability has increased {X}% over {N} months. May reflect higher turnover, a change in customer mix, or a classification issue worth reviewing."

    staff_cost_ratio:
      calculation: "Staff costs (EGLS account 64) / Revenue"
      alert_threshold: "Ratio increase of more than 3 percentage points"

    cash_position:
      calculation: "Cash and bank balances (account 38) trend"
      alert_threshold: "Declining for 3 consecutive months"
      finding_template: "{Client} cash position has declined for {N} consecutive months (from EUR {X} to EUR {Y}). With a tax payment of EUR {Z} due on {date}, this warrants a cash flow conversation."

  minimum_periods_required: 3
  preferred_periods: 12
  confidence_note: "Findings with fewer than 6 data points are marked LOW CONFIDENCE"
```

### 3. Anomaly Detection

Values statistically unusual relative to a client's own history and sector peers.

```yaml
Anomaly_Detection:
  methods:
    own_history_comparison:
      description: "Value more than 2 standard deviations from client's own trailing average"
      example: "Electricity costs EUR 4,200 in January vs trailing 12-month average of EUR 1,800"

    sector_peer_comparison:
      description: "Value more than 1.5x or less than 0.5x the sector median for that account"
      note: "Sector medians computed from anonymised aggregates across the portfolio"

    vat_rate_anomaly:
      description: "Transaction classified at incorrect VAT rate based on product/service category"
      example: "Food product invoice at 24% rather than correct 13% reduced rate"
      action: "Flag for accountant review — never auto-correct"

  output_fields:
    - metric: "What was measured"
    - actual_value: "What was found"
    - expected_range: "What is normal for this client / sector"
    - deviation: "How far outside normal"
    - confidence: "HIGH / MEDIUM / LOW"
    - suggested_action: "Plain English recommendation"
    - data_source: "Which files the finding is based on"
```

### 4. Cash Flow Forecasting

Projects cash position forward 1-3 months using historical patterns and known upcoming obligations.

```yaml
Cashflow_Forecast:
  inputs:
    known_inflows:
      - Recurring revenue based on trailing 3-month average
      - Outstanding debtor invoices from registry
    known_outflows:
      - Upcoming tax deadlines from cli-deadline-monitor
      - Recurring supplier payments from banking history
      - EFKA contributions due
      - Payroll from prior period data
    uncertainty_ranges:
      - Revenue: +/- 15% based on historical variance
      - Ad-hoc expenses: +/- 20%

  output:
    - Best case / expected / worst case cash position at each month end
    - Months where cash may go negative (flagged HIGH RISK)
    - Specific upcoming payments that may cause strain

  confidence_degradation:
    1_month: "HIGH confidence"
    2_months: "MEDIUM confidence"
    3_months: "LOW confidence — directional only"
```

### 5. Portfolio Intelligence (Cross-Client)

Aggregated across the portfolio. All cross-client aggregation is anonymised.

```yaml
Portfolio_Intelligence:
  sector_benchmarks:
    computed_from: "Anonymised aggregates of all active clients per sector"
    metrics:
      - Median gross margin by sector
      - Median staff cost ratio by sector
      - Median VAT liability as percentage of revenue by sector
    refreshed: "Monthly — after all monthly statements are generated"
    minimum_clients_per_sector: 3

  portfolio_risk_distribution:
    description: "Distribution of risk scores across the full portfolio over time"

  workload_concentration:
    description: "Risk-weighted workload per accountant — alerts if one person carries disproportionate risk"

  common_issues:
    description: "Issues appearing across multiple clients simultaneously"
    examples:
      - "6 retail clients showing declining margins — possible sector-wide trend"
      - "3 clients using the same supplier showing unusual payment patterns"
      - "4 clients with outstanding document requests over 21 days"
```

---

## Morning Advisory Output Format

Pre-computed overnight. Ready by 08:00. Pulled by conversational assistant (Skill 14).

```
MORNING ADVISORY — 19/02/2026
Generated: 19/02/2026 05:47 Athens time

WATCH LIST — 3 clients warrant attention today

1. GAMMA CONSTRUCTIONS AE (EL555444333) — RISK: HIGH (8/10)
   Cash position has declined 3 consecutive months. Current balance EUR 12,400.
   Tax payment of EUR 8,900 due 25/03/2026. Margin is tight.
   Suggest: Review with client before month end.

2. DELTA SERVICES EPE (EL777888999) — RISK: MEDIUM (6/10)
   VAT liability increased 34% vs prior 3-month average. January: EUR 4,100
   vs average of EUR 3,060. Not yet investigated.
   Suggest: Check whether turnover genuinely increased or a classification
   issue exists in the January invoices. Confidence: MEDIUM (4 months data)

3. EPSILON RETAIL OE (EL222333444) — RISK: MEDIUM (5/10)
   Bank statements for January not received. VAT filing due 25/02/2026 in 6 days.
   Suggest: Send document request today.

PORTFOLIO SNAPSHOT
Active clients: 42 | Low risk: 31 | Medium: 8 | High: 3 | Critical: 0
Next high-volume deadline: VAT February 25/02/2026 (6 days, 18 clients affected)

SECTOR NOTE
Retail sector (7 clients): Gross margins down an average of 3.2pp vs Q4 2025.
Pattern appears sector-wide. May be worth raising with retail clients proactively.
Confidence: MEDIUM (7 clients, 3 months of data)
```

---

## File System

```yaml
Analytics_File_Structure:
  owns: "/data/reports/analytics/"

  daily_outputs:
    - "{YYYY-MM-DD}_risk-scores.json"
    - "{YYYY-MM-DD}_morning-advisory.json"
    - "{YYYY-MM-DD}_morning-advisory.txt"
    - "{YYYY-MM-DD}_anomalies.json"

  monthly_outputs:
    - "{YYYY-MM}_portfolio-report.pdf"
    - "{YYYY-MM}_sector-benchmarks.json"
    - "{YYYY-MM}_trend-analysis.json"

  on_demand_outputs:
    - "{YYYY-MM-DD}_{AFM}_risk-detail.json"
    - "{YYYY-MM-DD}_{AFM}_forecast.json"
    - "{YYYY-MM-DD}_{AFM}_trends.json"

  reads_from:
    - "/data/clients/*/financial-statements/"
    - "/data/clients/*/compliance/"
    - "/data/clients/*/correspondence/"
    - "/data/banking/reconciliation/"
    - "/data/efka/"
    - "/data/reports/analytics/"   # Prior outputs for trend continuity

  never_writes_to:
    - "/data/clients/"
    - "/data/compliance/"
    - "/data/banking/"
    - "/data/efka/"
```

---

## Scheduling

```yaml
Analytics_Schedule:
  nightly_run:
    time: "01:30 Athens time (after backup and integrity check)"
    operations:
      - "Compute risk scores for all active clients"
      - "Run anomaly detection across all clients with new data"
      - "Update trend analysis for clients with new financial statements"
      - "Generate morning advisory"
    duration_estimate: "10-30 minutes depending on portfolio size"

  monthly_run:
    trigger: "After all monthly statements generated (typically 5th-10th of following month)"
    operations:
      - "Recompute sector benchmarks"
      - "Generate portfolio monthly report"
      - "Run 12-month trend analysis for all clients with sufficient history"

  on_demand:
    available_during: "Business hours"
    rate_limit: "Maximum 10 on-demand requests per hour"
    bounded_by: "Pre-computed daily outputs where possible"
```

---

## Integration Points

```yaml
Upstream_Skills_Read:
  greek-financial-statements:   "P&L, balance sheet, VAT summary — primary financial data"
  client-data-management:       "Compliance history, document registry, correspondence log"
  greek-banking-integration:    "Reconciliation data, cash position, transaction patterns"
  efka-api-integration:         "Payroll costs, employee counts, contribution history"
  cli-deadline-monitor:         "Upcoming deadlines — feeds cash flow forecast"
  greek-compliance-aade:        "Filing history, penalty records"
  client-communication-engine:  "Correspondence patterns — identifies chronic document requesters"

Downstream_Skills_Feed:
  conversational-ai-assistant:  "Answers analytics queries; morning advisory pulled via chat"
  dashboard-greek-accounting:   "Risk scores, portfolio snapshot, watch list"
  client-communication-engine:  "Advisory findings can prompt draft letters (human initiates)"
```

---

## Memory Integration (Phase 4 — Skill 19 hooks)

```yaml
Memory_Integration:
  log_episodes: true
  episode_types:
    - morning_advisory_generated
    - anomaly_detected_and_surfaced
    - risk_score_computed
    - forecast_generated

  log_failures: true
  failure_types:
    - insufficient_data_for_analysis
    - sector_benchmark_too_small
    - financial_statements_missing

  useful_patterns_to_detect:
    - "Anomaly types consistently dismissed by accountants — thresholds may be too sensitive"
    - "Risk score bands that consistently predict actual compliance problems — calibration quality"
    - "Clients where forecasts are consistently wrong in one direction — systematic bias"

  rate_limit_group: "analytics_operations"
```

---

## Error Handling

```yaml
Error_Responses:

  insufficient_history:
    output: "{Client} has only {N} periods of data — trend analysis requires at least 3. Showing available data with LOW CONFIDENCE marker."
    action: "Produce what is possible, clearly labelled. Do not refuse to show anything."

  sector_too_small:
    output: "Sector benchmark for {sector} cannot be computed — only {N} clients (minimum 3 required). Showing own-history analysis only."

  missing_statements:
    output: "Financial trend analysis for {client} requires Skill 15 outputs for {period}. Statements not yet generated."
    action: "Show analysis based on available periods. Note the gap explicitly."

  on_demand_rate_limit:
    output: "On-demand analysis limit reached (10/hour). Pre-computed morning advisory is available now. Full analysis available after {time}."
    action: "Direct to pre-computed outputs. Never drop the request silently."
```

---

## Success Metrics

A successful deployment of this skill should achieve:
- Morning advisory ready every business day before 08:00 Athens time
- Risk scores computed for 100% of active clients nightly
- Anomaly detection surfaces at least one actionable finding per week across the portfolio
- Cash flow forecasts accurate within 15% for the 1-month horizon (measured retrospectively)
- Zero false positives that cause unnecessary client alarm — confidence ratings are accurate
- All findings in plain English that an accounting assistant can act on immediately
- Read-only confirmed — no writes to any operational directory, ever

Remember: This skill is the difference between an accounting system that processes the past and one that helps the firm prepare for the future. The value is not in the data it holds — the value is in what it notices that humans would have missed.
