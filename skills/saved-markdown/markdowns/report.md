# Report Reference

## When to Use This Template

- User asks for a report, analysis, summary, findings, or status update
- Keywords: report, analysis, summary, findings, status, metrics, review, audit, assessment
- Output involves data interpretation, trends, or recommendations
- Cron-generated outputs, system summaries, periodic reviews

---

## Structure Template

```markdown
# {Report Title}

**Date:** {YYYY-MM-DD}
**Prepared by:** {author or system}
**Period:** {date range covered}

---

## Executive Summary

{3-5 sentences that tell the complete story. A reader who only reads this section should understand: what was analyzed, what was found, and what should happen next.}

---

## Key Findings

| # | Finding | Impact |
|---|---------|--------|
| 1 | {Most important finding} | {High/Medium/Low + why} |
| 2 | {Second finding} | {Impact} |
| 3 | {Third finding} | {Impact} |

---

## {Data Section 1 Title}

{Context sentence explaining what this data shows.}

{Table or chart here}

**Takeaway:** {One sentence explaining the "so what?" of this data.}

---

## {Data Section 2 Title}

{Context + data + takeaway pattern repeats}

---

## Trends & Patterns

{markdown-ui-widget charts for time-series or comparison data}

---

## Recommendations

| Priority | Action | Expected Impact | Owner |
|----------|--------|-----------------|-------|
| 🔴 High | {Specific action} | {Expected outcome} | {Who} |
| 🟡 Medium | {Specific action} | {Expected outcome} | {Who} |
| 🟢 Low | {Specific action} | {Expected outcome} | {Who} |

---

## Appendix

{Raw data tables, methodology notes, or detailed breakdowns — only if needed}
```

---

## Styling Guidelines

- **Executive Summary stands alone** — Write it so someone who reads ONLY this section gets the full picture
- **Finding → Impact pattern** — Every data point should answer "so what?"
- **Priority indicators** — Use 🔴🟡🟢 for recommendations to make urgency scannable
- **Tables over paragraphs** — Data in tables, not buried in prose
- **Horizontal rules** between major sections for visual separation
- **Bold key numbers** inline — "Revenue grew **34%** to **$2.1M**"

---

## Chart Recommendations

Reports are the **most chart-dense** content type. Use 2-4 charts per report.

**Line chart** — Trends over time (the most common report chart):
```
```markdown-ui-widget
chart-line
title: Monthly Active Users (Q1 2026)
Month,Users,Target
Jan,12400,12000
Feb,13800,13000
Mar,15200,14000
```
```

**Bar chart** — Category comparisons:
```
```markdown-ui-widget
chart-bar
title: Revenue by Product Line
Product,Revenue ($K)
"Core Platform",420
"API Services",285
"Enterprise",190
"Add-ons",95
```
```

**Pie chart** — Distribution/composition:
```
```markdown-ui-widget
chart-pie
title: Support Ticket Categories
Category,Count
"Bug Reports",42
"Feature Requests",28
"How-to Questions",18
"Account Issues",12
```
```

**Multi-series line** — Comparing trends:
```
```markdown-ui-widget
chart-line
title: Signups vs Activations
Month,Signups,Activated
Jan,500,310
Feb,620,405
Mar,780,520
Apr,850,595
May,920,650
```
```

---

## Professional Tips

1. **Most important finding first** — Don't bury the lead. If revenue dropped 20%, say it in sentence one.
2. **"So what?" after every data point** — Raw numbers mean nothing without interpretation. Always add context.
3. **Specific recommendations** — "Improve retention" is useless. "Implement 7-day onboarding email sequence targeting users who haven't completed setup" is actionable.
4. **Compare to something** — Numbers need context: vs. last period, vs. target, vs. industry benchmark
5. **Lead with the chart, follow with the table** — Charts show patterns, tables provide precision. Use both.
6. **One insight per section** — Don't mix unrelated metrics in the same section
7. **Date and period are mandatory** — Every report must state when it was generated and what period it covers
8. **Keep the appendix optional** — Only include raw data if the audience needs to verify or drill down

---

## Example

```markdown
# Monthly SaaS Metrics Report

**Date:** 2026-03-15
**Prepared by:** Analytics Team
**Period:** February 1–28, 2026

---

## Executive Summary

February saw strong user growth with MAU reaching 15,200 (+10.1% MoM), exceeding our Q1 target by 8.6%. However, churn rate increased to 4.2% (from 3.5% in January), primarily driven by annual plan expirations. Revenue grew 6.8% to $892K but missed the $920K target. Immediate focus should be on retention campaigns for expiring annual customers.

---

## Key Findings

| # | Finding | Impact |
|---|---------|--------|
| 1 | Churn spiked to 4.2% from annual plan expirations | 🔴 High — $48K MRR at risk in March |
| 2 | MAU grew 10.1% MoM, beating target | 🟢 Positive — acquisition engine healthy |
| 3 | API usage up 45% but revenue flat | 🟡 Medium — usage-based pricing not capturing value |

---

## Growth Metrics

```markdown-ui-widget
chart-line
title: Monthly Active Users
Month,MAU,Target
Oct,10200,10000
Nov,11400,11000
Dec,12800,12000
Jan,13800,13000
Feb,15200,14000
```

**Takeaway:** Organic growth continues to outpace targets. The product-led growth motion launched in Q4 is delivering consistent 10%+ MoM expansion.

---

## Revenue Breakdown

```markdown-ui-widget
chart-bar
title: Revenue by Plan ($K)
Plan,"Feb Revenue"
Starter,180
Pro,385
Enterprise,245
"Add-ons",82
```

```markdown-ui-widget
chart-pie
title: Revenue Distribution
Plan,Share
Starter,20
Pro,43
Enterprise,28
"Add-ons",9
```

**Takeaway:** Pro plan remains the revenue engine at 43% of total. Enterprise is underperforming — only 3 new enterprise deals closed vs. 7 target.

---

## Recommendations

| Priority | Action | Expected Impact | Owner |
|----------|--------|-----------------|-------|
| 🔴 High | Launch renewal campaign for 142 annual plans expiring in March | Prevent $48K MRR churn | Retention |
| 🔴 High | Revisit API pricing tiers — usage up 45% with flat revenue | Capture $30-50K/mo in underpriced usage | Product |
| 🟡 Medium | A/B test enterprise landing page — conversion at 1.2% vs. 2.5% benchmark | +4 enterprise deals/month | Marketing |
```
