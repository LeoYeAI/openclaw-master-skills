# Dashboard / Metrics Reference

## When to Use This Template

- User asks for a dashboard, KPI overview, metrics snapshot, or scorecard
- Keywords: dashboard, KPIs, metrics, scorecard, performance overview, stats, analytics summary
- Output is a data-dense overview with multiple metrics and visualizations
- Periodic snapshots (daily, weekly, monthly) of key business or system metrics

---

## Structure Template

```markdown
# {Dashboard Title}

**Last updated:** {YYYY-MM-DD HH:MM UTC}
**Period:** {date range}
**Source:** {data source or system}

---

## At a Glance

| Metric | Current | Previous | Change |
|--------|---------|----------|--------|
| {Primary KPI} | **{value}** | {prev value} | {↑↓} {X%} |
| {Secondary KPI} | **{value}** | {prev value} | {↑↓} {X%} |
| {Third KPI} | **{value}** | {prev value} | {↑↓} {X%} |
| {Fourth KPI} | **{value}** | {prev value} | {↑↓} {X%} |

---

## {Primary Metric} Trend

{Context sentence: what this metric measures and why it matters.}

{chart-line widget}

**Status:** {On track / At risk / Off track} — {one sentence interpretation}

---

## {Category Breakdown}

{chart-bar or chart-pie widget}

| Category | Value | % of Total |
|----------|-------|------------|
| {Cat 1} | {val} | {%} |
| {Cat 2} | {val} | {%} |
| {Cat 3} | {val} | {%} |

---

## {Secondary Metric} Trend

{chart-line widget}

---

## {Distribution / Composition}

{chart-pie widget}

---

## Anomalies & Notes

- ⚠️ {Anomaly or data quality note}
- ℹ️ {Context or caveat}
- 📌 {Action item or follow-up}

---

*Dashboard generated {timestamp}. Next update: {schedule}.*
```

---

## Styling Guidelines

- **At a Glance table is mandatory** — This is the dashboard's hero section. Bold the current values. Use ↑/↓ arrows with color indicators.
- **Change indicators**: `↑ 12%` for positive, `↓ 8%` for negative. Context determines whether up/down is good or bad (e.g., churn ↓ is good).
- **Status labels**: Use "On track" / "At risk" / "Off track" after each major metric chart.
- **Timestamp everything** — Dashboards without timestamps are untrustworthy.
- **Dense layout** — Dashboards should feel packed with information, not spacious. Minimize prose between charts.
- **Footer with schedule** — Tell the reader when the next update will be.

---

## Chart Recommendations

Dashboards are the **most chart-dense** content type. Use 3-6 charts.

**Trend line chart** (most common — show metric over time):
```
```markdown-ui-widget
chart-line
title: Daily Active Users (Last 14 Days)
Date,DAU
"Mar 1",4200
"Mar 3",4350
"Mar 5",4100
"Mar 7",4500
"Mar 9",4680
"Mar 11",4450
"Mar 13",4720
"Mar 15",4890
```
```

**Multi-metric line chart** (compare related metrics):
```
```markdown-ui-widget
chart-line
title: Signups vs Activations vs Paying
Week,Signups,Activated,Paying
W1,520,340,85
W2,580,365,92
W3,610,400,105
W4,650,425,118
```
```

**Breakdown bar chart** (category comparisons):
```
```markdown-ui-widget
chart-bar
title: Support Tickets by Priority
Priority,Open,Resolved
Critical,8,42
High,24,89
Medium,56,134
Low,32,98
```
```

**Composition pie chart** (distribution of a whole):
```
```markdown-ui-widget
chart-pie
title: Traffic by Channel
Channel,Sessions
Organic,4200
Direct,2800
Paid,1900
Social,850
Referral,620
```
```

**Scatter chart** (correlation between two metrics):
```
```markdown-ui-widget
chart-scatter
title: Feature Usage vs Retention
"Usage Score","Retention %"
12,45
28,62
35,58
48,71
55,74
62,78
75,85
88,91
```
```

---

## Professional Tips

1. **Most important metric first** — Lead with the KPI the audience cares about most
2. **Always include comparison periods** — A number without context is meaningless. Show vs. last period, vs. target, or vs. benchmark.
3. **Use ↑↓ arrows consistently** — Up arrow for increases, down arrow for decreases. Let context determine if it's good (revenue ↑) or bad (churn ↑).
4. **Keep it scannable** — If someone can't get the story in 10 seconds from the At a Glance table, the dashboard has failed
5. **Chart + table pairing** — Charts show trends and patterns; tables provide exact numbers. Use both for important metrics.
6. **Flag anomalies explicitly** — Don't let the reader wonder why there's a spike. Call it out in the Notes section.
7. **Consistent time periods** — Don't mix daily and weekly data in the same chart. Keep time scales uniform.
8. **Limit to 6 charts max** — More than 6 charts in a single page becomes overwhelming. Prioritize ruthlessly.

---

## Example

```markdown
# Platform Health Dashboard

**Last updated:** 2026-03-15 14:00 UTC
**Period:** March 8–15, 2026
**Source:** Internal analytics + Stripe

---

## At a Glance

| Metric | Current | Previous Week | Change |
|--------|---------|---------------|--------|
| Daily Active Users | **4,890** | 4,350 | ↑ 12.4% |
| Revenue (Weekly) | **$18.2K** | $17.1K | ↑ 6.4% |
| Churn Rate | **3.1%** | 3.5% | ↓ 0.4pp |
| Avg Response Time | **142ms** | 156ms | ↓ 9.0% |
| Error Rate | **0.08%** | 0.12% | ↓ 33.3% |

---

## User Growth Trend

```markdown-ui-widget
chart-line
title: Daily Active Users (4 Weeks)
Week,DAU,Target
W10,3900,4000
W11,4200,4100
W12,4350,4200
W13,4890,4300
```

**Status:** On track — DAU exceeded target for 3 consecutive weeks. Growth driven by organic search improvements.

---

## Revenue by Plan

```markdown-ui-widget
chart-pie
title: Weekly Revenue by Plan
Plan,Revenue
Pro,8400
Enterprise,5800
Starter,2600
"Add-ons",1400
```

| Plan | Revenue | % of Total | WoW Change |
|------|---------|------------|------------|
| Pro | $8,400 | 46.2% | ↑ 8% |
| Enterprise | $5,800 | 31.9% | ↑ 3% |
| Starter | $2,600 | 14.3% | ↑ 5% |
| Add-ons | $1,400 | 7.7% | ↑ 12% |

---

## API Performance

```markdown-ui-widget
chart-line
title: API Response Time (ms) — P50 vs P99
Day,P50,P99
Mon,95,420
Tue,102,385
Wed,98,410
Thu,88,350
Fri,92,380
Sat,85,310
Sun,82,295
```

**Status:** On track — P99 latency below 500ms SLA target all week.

---

## Anomalies & Notes

- ⚠️ DAU spike on Mar 13 (+8% single-day) traced to HackerNews front page mention
- ℹ️ Churn decrease partly seasonal — March historically has lower churn
- 📌 Action: investigate Add-ons revenue jump (+12%) — may indicate pricing page A/B test working

---

*Dashboard generated 2026-03-15T14:00:00Z. Next update: 2026-03-22.*
```
