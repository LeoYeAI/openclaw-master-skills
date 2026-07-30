# Monthly Spending Report

**Month:** {{month_name}} {{year}}

---

## 📊 Overview

| Metric | Amount |
|--------|--------|
| **Total Spent** | ${{total_spent}} |
| **# Transactions** | {{transaction_count}} |
| **Daily Average** | ${{daily_average}} |
| **Biggest Day** | {{biggest_day}} (${{biggest_day_amount}}) |
| **Lightest Day** | {{lightest_day}} (${{lightest_day_amount}}) |
{{#if income}}
| **Income** | ${{income}} |
| **Savings** | ${{savings}} ({{savings_rate}}%) |
{{/if}}

---

## 📂 Full Category Breakdown

| Category | Spent | Budget | Used | vs Last Month | Status |
|----------|-------|--------|------|---------------|--------|
{{#each categories}}
| {{name}} | ${{spent}} | ${{limit}} | {{pct}}% | {{mom_change}} | {{status_emoji}} |
{{/each}}
| **TOTAL** | **${{total_spent}}** | **${{total_budget}}** | **{{total_pct}}%** | **{{total_mom_change}}** | |

---

## 🏆 Top 10 Expenses

| # | Date | Amount | Vendor | Category | Notes |
|---|------|--------|--------|----------|-------|
{{#each top_expenses}}
| {{rank}} | {{date}} | ${{amount}} | {{vendor}} | {{category}} | {{notes}} |
{{/each}}

---

## 📅 Weekly Breakdown

| Week | Spent | # Items | Daily Avg |
|------|-------|---------|-----------|
{{#each weeks}}
| {{label}} | ${{spent}} | {{count}} | ${{daily_avg}} |
{{/each}}

---

## 📈 Month-over-Month Comparison

| Category | {{prev_month_name}} | {{curr_month_name}} | Change | Trend |
|----------|---------------------|---------------------|--------|-------|
{{#each mom_comparison}}
| {{category}} | ${{prev}} | ${{curr}} | {{change}} | {{trend}} |
{{/each}}
| **Total** | **${{prev_total}}** | **${{curr_total}}** | **{{total_change}}** | **{{total_trend}}** |

---

{{#if income}}
## 💵 Savings Rate

| Metric | Amount |
|--------|--------|
| Income | ${{income}} |
| Total Spent | ${{total_spent}} |
| Saved | ${{savings}} |
| Savings Rate | {{savings_rate}}% |
| Target (20%) | ${{savings_target}} |
| vs Target | {{savings_vs_target}} |

{{/if}}

---

## 🔔 Alerts & Notes

{{#each alerts}}
- {{this}}
{{/each}}

{{#if no_alerts}}
✅ All categories within budget this month.
{{/if}}

---

*Generated {{generated_at}}*
