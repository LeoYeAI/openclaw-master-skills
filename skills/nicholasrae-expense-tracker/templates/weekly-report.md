# Weekly Spending Report

**Week of:** {{week_start}} – {{week_end}}

---

## 📊 Summary

| Metric | Amount |
|--------|--------|
| **Total Spent** | ${{total_spent}} |
| **# Transactions** | {{transaction_count}} |
| **Daily Average** | ${{daily_average}} |
| **Largest Expense** | ${{largest_amount}} at {{largest_vendor}} |

---

## 📂 By Category

| Category | Spent | # Items | % of Total |
|----------|-------|---------|------------|
{{#each categories}}
| {{name}} | ${{spent}} | {{count}} | {{pct}}% |
{{/each}}

---

## 🏆 Top 5 Expenses

| # | Date | Amount | Vendor | Category |
|---|------|--------|--------|----------|
{{#each top_expenses}}
| {{rank}} | {{date}} | ${{amount}} | {{vendor}} | {{category}} |
{{/each}}

---

## 💰 Budget Status

| Category | Spent | Budget | Used | Status |
|----------|-------|--------|------|--------|
{{#each budget_status}}
| {{category}} | ${{spent}} | ${{limit}} | {{pct}}% | {{status_emoji}} |
{{/each}}

---

## 📈 Week-over-Week Trend

| Metric | Last Week | This Week | Change |
|--------|-----------|-----------|--------|
| Total | ${{prev_total}} | ${{curr_total}} | {{wow_change}} |
| Transactions | {{prev_count}} | {{curr_count}} | {{wow_count_change}} |
| Daily Avg | ${{prev_daily_avg}} | ${{curr_daily_avg}} | {{wow_daily_change}} |

{{#if wow_note}}
> {{wow_note}}
{{/if}}

---

*Generated {{generated_at}}*
