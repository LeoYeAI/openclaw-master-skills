---
name: Spreadsheet & Data Wrangling Master
slug: afrexai-spreadsheet-master
version: 1.0.0
description: "Complete spreadsheet methodology — data cleanup, transformation, analysis, dashboards, automation, and reporting. Works with CSV, Excel, Google Sheets, or any tabular data. Use when the user needs to clean messy data, build reports, create dashboards, automate recurring spreadsheet tasks, or transform data between formats."
tags: spreadsheet, excel, csv, data, cleanup, reporting, dashboard, analytics, automation, google-sheets
---

# Spreadsheet & Data Wrangling Master

> Turn messy data into clean insights, automated reports, and decision-ready dashboards. Platform-agnostic — works with CSV, Excel, Google Sheets, or any tabular format.

---

## Phase 1: Data Intake & Assessment

Before touching any data, assess what you have.

### Quick Health Check (score /20)

```yaml
data_intake:
  source: ""           # file path, URL, API, database, manual entry
  format: ""           # CSV, XLSX, TSV, JSON, clipboard paste
  rows: 0
  columns: 0
  file_size: ""
  encoding: ""         # UTF-8, Latin-1, Windows-1252, etc.
  delimiter: ""        # comma, tab, pipe, semicolon

  health_score:        # rate each 0-4, total /20
    completeness: 0    # 4=<1% missing, 3=<5%, 2=<15%, 1=<30%, 0=>30%
    consistency: 0     # 4=uniform types, 3=minor mixed, 2=significant mixed, 1=chaotic, 0=unusable
    accuracy: 0        # 4=verified, 3=plausible, 2=some outliers, 1=many errors, 0=untrustworthy
    freshness: 0       # 4=real-time, 3=<24h, 2=<7d, 1=<30d, 0=stale/unknown
    structure: 0       # 4=tidy (1 row=1 obs), 3=minor reshaping, 2=pivot needed, 1=multi-header, 0=freeform

  issues_found: []     # list every problem before fixing anything
```

### First 10 Questions to Ask

1. How many rows and columns?
2. What does each row represent? (one customer? one transaction? one day?)
3. Are there header rows? Multiple header rows? Merged cells?
4. What are the data types? (dates, currencies, percentages, IDs, free text)
5. How much is missing? Which columns?
6. Are there duplicates? By which key?
7. Is there a unique identifier column?
8. What date format? (MM/DD/YYYY vs DD/MM/YYYY vs YYYY-MM-DD vs mixed)
9. What currency/number format? (1,000.00 vs 1.000,00 vs 1000)
10. Where did this data come from and how often is it updated?

---

## Phase 2: Data Cleaning Decision Tree

### Step-by-Step Cleaning Protocol

```
START
  │
  ├─ Headers → Normalize (lowercase, snake_case, no spaces/special chars)
  │
  ├─ Duplicates?
  │   ├─ Exact duplicates → Remove, keep first
  │   ├─ Near-duplicates → Flag for review (fuzzy match on name + address)
  │   └─ Intentional duplicates → Leave (e.g., multiple orders same customer)
  │
  ├─ Missing Values?
  │   ├─ <5% of column → Fill (mean for numeric, mode for categorical, forward-fill for time series)
  │   ├─ 5-30% → Flag + fill with "UNKNOWN" or interpolate with justification
  │   ├─ >30% → Consider dropping column or flagging as unreliable
  │   └─ Entire row missing key fields → Remove with log
  │
  ├─ Data Types?
  │   ├─ Dates as text → Parse to date (try multiple formats, log failures)
  │   ├─ Numbers as text → Strip currency symbols, commas, whitespace, convert
  │   ├─ IDs/zips with leading zeros → Keep as text (NEVER convert to number)
  │   ├─ Phone numbers → Text, standardize format
  │   ├─ Mixed types in column → Split or coerce with error log
  │   └─ Boolean variants → Map (Yes/No/True/False/1/0/Y/N → consistent)
  │
  ├─ Outliers?
  │   ├─ Calculate IQR: Q1 - 1.5×IQR to Q3 + 1.5×IQR
  │   ├─ Business logic check (negative revenue? age 200? date in 2099?)
  │   ├─ Decide: fix (typo), cap (winsorize), remove, or keep with flag
  │   └─ ALWAYS log which outliers were modified and why
  │
  ├─ Standardization?
  │   ├─ Text case → Consistent (Title Case for names, UPPER for codes)
  │   ├─ Whitespace → Trim leading/trailing, collapse internal
  │   ├─ Categories → Map variants ("US"/"USA"/"United States" → "US")
  │   ├─ Dates → ISO 8601 (YYYY-MM-DD) internally
  │   ├─ Currency → Consistent symbol placement, decimal precision
  │   └─ Phone/email → Validate format
  │
  └─ Structural Issues?
      ├─ Multi-header rows → Flatten to single header
      ├─ Merged cells → Unmerge + fill down
      ├─ Pivot/crosstab → Unpivot to tidy format (1 row = 1 observation)
      ├─ Multiple tables in one sheet → Split to separate sheets/files
      └─ Metadata rows (totals, notes) → Separate from data rows
```

### Cleaning Log Template

```yaml
cleaning_log:
  date: "YYYY-MM-DD"
  source_file: ""
  rows_before: 0
  rows_after: 0
  actions:
    - action: "removed exact duplicates"
      rows_affected: 0
      key_columns: ["email"]
    - action: "filled missing values"
      column: "state"
      method: "mode"
      values_filled: 0
    - action: "removed outliers"
      column: "revenue"
      criteria: "negative values"
      rows_removed: 0
    - action: "standardized dates"
      column: "order_date"
      from_format: "MM/DD/YYYY"
      to_format: "YYYY-MM-DD"
      parse_failures: 0
  notes: ""
```

---

## Phase 3: Transformation Patterns

### 12 Essential Transform Operations

| # | Operation | When to Use | Example |
|---|-----------|-------------|---------|
| 1 | **Filter** | Subset rows by condition | Orders > $1000, Date after 2024-01-01 |
| 2 | **Sort** | Order by column(s) | Revenue descending, then date ascending |
| 3 | **Group + Aggregate** | Summarize by category | Total revenue by region, avg order by customer |
| 4 | **Pivot** | Rows → columns | Monthly columns from date rows |
| 5 | **Unpivot/Melt** | Columns → rows | Month columns back to date rows |
| 6 | **Join/Merge** | Combine datasets | Customer data + order data on customer_id |
| 7 | **Deduplicate** | Remove redundancy | Keep latest record per customer |
| 8 | **Derive** | Calculate new columns | profit = revenue - cost, age = today - birthdate |
| 9 | **Split** | One column → many | "John Smith" → first_name, last_name |
| 10 | **Concatenate** | Many columns → one | city + state + zip → full_address |
| 11 | **Lookup/Map** | Enrich with reference data | state_code → state_name, product_id → category |
| 12 | **Window** | Running calculations | 7-day moving average, rank within group, running total |

### Join Strategy Decision Guide

```
Which join do you need?
│
├─ Need ALL rows from left table → LEFT JOIN
│   (customers who may or may not have orders)
│
├─ Need ONLY matching rows → INNER JOIN
│   (only customers WITH orders)
│
├─ Need ALL rows from both → FULL OUTER JOIN
│   (reconciliation: find mismatches)
│
├─ Need everything NOT in other table → LEFT JOIN + WHERE right IS NULL
│   (customers who NEVER ordered)
│
└─ Need every combination → CROSS JOIN (rare, use carefully)
    (all products × all stores for pricing matrix)

⚠️ ALWAYS check join results:
- Row count: did it explode? (many-to-many join)
- Row count: did it shrink? (keys not matching)
- NULL columns: expected from outer join, unexpected = key mismatch
```

### Formula Reference (Cross-Platform)

| Task | Excel | Google Sheets | Python (pandas) |
|------|-------|---------------|-----------------|
| Lookup | `VLOOKUP`, `XLOOKUP` | `VLOOKUP`, `XLOOKUP` | `df.merge()`, `df.map()` |
| Conditional sum | `SUMIFS` | `SUMIFS` | `df.groupby().sum()` |
| Conditional count | `COUNTIFS` | `COUNTIFS` | `df.groupby().count()` |
| Text split | `TEXTSPLIT`, `LEFT/MID/RIGHT` | `SPLIT` | `df.str.split()` |
| Date diff | `DATEDIF`, math | `DATEDIF` | `(df.col2 - df.col1).dt.days` |
| Running total | `SUM($A$1:A1)` | `SUM($A$1:A1)` | `df.cumsum()` |
| Rank | `RANK.EQ` | `RANK` | `df.rank()` |
| Percent of total | `=A1/SUM($A:$A)` | `=A1/SUM($A:$A)` | `df.col / df.col.sum()` |
| Remove duplicates | Data → Remove Duplicates | Data → Remove Duplicates | `df.drop_duplicates()` |
| Pivot | Pivot Table | Pivot Table | `df.pivot_table()` |

---

## Phase 4: Analysis Frameworks

### Quick Analysis Menu

Pick the analysis that matches the question:

**Descriptive (What happened?)**
- Summary statistics: count, mean, median, min, max, std dev, percentiles
- Frequency distributions: how many of each category?
- Time trends: daily/weekly/monthly aggregates over time
- Cross-tabs: category A × category B breakdown

**Diagnostic (Why did it happen?)**
- Drill-down: which segment drove the change?
- Cohort analysis: behavior by signup month
- Correlation: which variables move together?
- Variance analysis: actual vs budget/forecast, by category

**Predictive (What might happen?)**
- Trend projection: linear/exponential fit + confidence
- Moving averages: 7/30/90 day smoothing
- Seasonality: same-period prior year comparison
- Growth rate: MoM, QoQ, YoY percentage changes

**Prescriptive (What should we do?)**
- Pareto (80/20): which 20% of X drives 80% of Y?
- Scenario analysis: best/base/worst case with different assumptions
- Sensitivity: which input variable has biggest impact?
- Break-even: at what point does X cover Y?

### Insight Formula

Every finding MUST follow this structure:
```
INSIGHT: [What you found — one sentence]
EVIDENCE: [The specific numbers]
SO WHAT: [Why it matters to the business]
ACTION: [What to do about it]
CONFIDENCE: [High/Medium/Low + why]
```

Example:
```
INSIGHT: Customer acquisition cost increased 43% in Q3 vs Q2
EVIDENCE: CAC went from $47 to $67, driven by paid search CPC increase (+62%)
SO WHAT: At current LTV of $180, payback period extended from 3.1 to 4.5 months
ACTION: Shift 30% of paid search budget to email/referral channels (CAC $12 and $23 respectively)
CONFIDENCE: High — based on complete Stripe + Google Ads data for full quarter
```

---

## Phase 5: Dashboard & Report Templates

### Executive Summary Dashboard (1-page)

```
┌──────────────────────────────────────────────────┐
│  EXECUTIVE DASHBOARD — [Period]                   │
│                                                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  │ Revenue  │ │ Customers│ │ Margin  │ │  Growth ││
│  │ $XXX,XXX │ │  X,XXX  │ │  XX.X%  │ │ +XX.X%  ││
│  │ ▲ +X.X%  │ │ ▲ +XXX  │ │ ▼ -X.X% │ │ vs LY   ││
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘│
│                                                    │
│  [Trend chart — key metric over 12 months]        │
│                                                    │
│  TOP 3 INSIGHTS:                                  │
│  1. [Insight + action]                            │
│  2. [Insight + action]                            │
│  3. [Insight + action]                            │
│                                                    │
│  ┌──────────────────┐ ┌──────────────────┐        │
│  │ By Segment       │ │ By Channel       │        │
│  │ (table or chart) │ │ (table or chart) │        │
│  └──────────────────┘ └──────────────────┘        │
└──────────────────────────────────────────────────┘
```

### KPI Formatting Rules

| Element | Rule | Example |
|---------|------|---------|
| Big numbers | Abbreviate with 1 decimal | $1.2M, 14.3K |
| Percentages | 1 decimal, always show direction | ▲ +12.3%, ▼ -4.1% |
| Currency | 2 decimals for <$1000, 0 for larger | $47.50, $12,000 |
| Dates | Consistent format throughout | Jan 2025, not 01/2025 |
| Comparison | Always include baseline | $120K (+15% vs LY) |
| RAG status | Use color + text | 🟢 On Track, 🟡 At Risk, 🔴 Behind |
| Sparklines | Show direction at a glance | ▁▂▃▅▇ (trending up) |

### Chart Selection Guide

```
What are you showing?
│
├─ Change over time → LINE chart (≤5 series) or AREA (stacked composition)
│
├─ Comparison across categories → BAR chart (horizontal for long labels)
│
├─ Part of whole → PIE (≤5 slices) or STACKED BAR (>5 or over time)
│
├─ Distribution → HISTOGRAM or BOX PLOT
│
├─ Relationship between 2 variables → SCATTER PLOT
│
├─ Geographic → MAP (if location data exists)
│
├─ Ranked list → HORIZONTAL BAR sorted descending
│
└─ Single KPI → BIG NUMBER with trend indicator

⚠️ NEVER use:
- 3D charts (distorts perception)
- Dual Y-axes (misleads readers)
- Pie with >7 slices (use bar instead)
- Rainbow colors (use 2-3 colors max + grey)
```

---

## Phase 6: Recurring Report Automation

### Automation Checklist

```yaml
recurring_report:
  name: ""
  frequency: ""          # daily, weekly, monthly, quarterly
  owner: ""
  recipients: []
  
  data_sources:
    - source: ""         # file path, API, database
      refresh: ""        # how data gets updated
      format: ""
  
  processing_steps:
    - step: "load data"
      tool: ""           # Python, Excel macro, Google Apps Script
    - step: "clean"
      rules: []          # reference cleaning protocol
    - step: "transform"
      operations: []
    - step: "analyze"
      calculations: []
    - step: "format"
      template: ""       # dashboard template to populate
    - step: "deliver"
      method: ""         # email, Slack, shared drive, API push
  
  quality_checks:
    - "Row count within expected range (±20%)"
    - "No NULL values in required columns"
    - "Totals reconcile with source system"
    - "Date range matches expected period"
    - "Key metrics pass sanity check (no 10x jumps without explanation)"
  
  error_handling:
    - trigger: "data source unavailable"
      action: "use cached last-good version + alert"
    - trigger: "row count outside range"
      action: "pause + flag for human review"
    - trigger: "metric exceeds 3× historical std dev"
      action: "include anomaly callout in report"
```

### Python Automation Template

```python
"""
Recurring report: [NAME]
Schedule: [FREQUENCY]
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# --- Config ---
INPUT_PATH = Path("data/raw/")
OUTPUT_PATH = Path("data/reports/")
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")

# --- Load ---
df = pd.read_csv(INPUT_PATH / "source.csv", parse_dates=["date"])

# --- Clean ---
df = df.drop_duplicates()
df = df.dropna(subset=["required_column"])
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# --- Transform ---
summary = (
    df.groupby("category")
    .agg(
        total=("amount", "sum"),
        count=("id", "count"),
        avg=("amount", "mean"),
    )
    .sort_values("total", ascending=False)
    .reset_index()
)

# --- Quality Check ---
assert len(df) > 0, "Empty dataset!"
assert df["amount"].isna().sum() / len(df) < 0.05, "Too many missing amounts"

# --- Output ---
output_file = OUTPUT_PATH / f"report-{REPORT_DATE}.csv"
summary.to_csv(output_file, index=False)
print(f"✅ Report saved: {output_file} | {len(summary)} rows")
```

---

## Phase 7: Common Spreadsheet Patterns

### Pattern 1: Financial Model

```
Sheet structure:
├── Assumptions    → All editable inputs in ONE place (highlighted cells)
├── Revenue        → Formulas reference Assumptions
├── Costs          → Formulas reference Assumptions  
├── P&L            → Pulls from Revenue + Costs
├── Cash Flow      → Derived from P&L + working capital
├── Balance Sheet  → Derived from Cash Flow
├── Scenarios      → Best/Base/Worst toggle that feeds Assumptions
└── Dashboard      → Charts + KPIs pulling from P&L/Cash Flow

Rules:
- Inputs = blue font or yellow background (pick one, be consistent)
- Formulas = black font, never hardcode numbers in formula cells
- Every formula traces back to Assumptions or raw data
- No circular references
- Include version number + last-updated date
```

### Pattern 2: CRM / Contact Tracker

```
Required columns:
- id (auto-increment or UUID)
- name, email, phone, company
- source (how they found us)
- status (lead → contacted → qualified → proposal → won/lost)
- last_contact_date
- next_action + next_action_date
- deal_value
- notes

Derived columns:
- days_since_last_contact = TODAY() - last_contact_date
- pipeline_stage_days = TODAY() - stage_entry_date
- is_stale = days_since_last_contact > 14

Dashboard metrics:
- Pipeline value by stage
- Conversion rate stage-to-stage
- Average days in each stage
- Stale leads count (action needed)
```

### Pattern 3: Inventory / Stock Tracker

```
Required columns:
- sku, name, category
- quantity_on_hand, reorder_point, reorder_quantity
- unit_cost, unit_price
- last_received_date, last_sold_date
- supplier

Derived columns:
- stock_value = quantity_on_hand × unit_cost
- margin = (unit_price - unit_cost) / unit_price
- days_of_supply = quantity_on_hand / avg_daily_sales
- needs_reorder = quantity_on_hand <= reorder_point

Alerts:
- 🔴 Below reorder point
- 🟡 Within 7 days of stockout (based on velocity)
- ⚪ Dead stock (no sales in 90 days)
```

### Pattern 4: Project / Task Tracker

```
Required columns:
- task_id, task_name, description
- assignee, priority (P0-P3)
- status (backlog → in_progress → review → done)
- start_date, due_date, completed_date
- estimated_hours, actual_hours

Derived columns:
- days_remaining = due_date - TODAY()
- is_overdue = due_date < TODAY() AND status != "done"
- effort_variance = actual_hours - estimated_hours
- completion_rate = done_tasks / total_tasks

Dashboard:
- Burndown chart (remaining vs time)
- Status distribution pie
- Overdue tasks list
- Team workload (tasks per assignee)
```

### Pattern 5: Budget vs Actual

```
Structure:
- Rows: expense categories + revenue lines
- Columns: Budget | Actual | Variance | Variance %
- Group by: month or quarter

Key formulas:
- variance = actual - budget
- variance_pct = (actual - budget) / budget
- YTD_budget = SUM of months through current
- Run_rate = (YTD_actual / months_elapsed) × 12

Conditional formatting:
- Green: favorable variance (revenue over, cost under)
- Red: unfavorable variance (revenue under, cost over)
- Threshold: flag if |variance| > 10%
```

---

## Phase 8: Data Quality Rules

### Validation Checklist (run before any analysis)

```yaml
validation:
  structural:
    - "No duplicate column names"
    - "No completely empty columns"
    - "No completely empty rows (except intentional separators)"
    - "Consistent column count across all rows"
    - "Headers in row 1 (no multi-row headers without handling)"
  
  type_integrity:
    - "Date columns parse as valid dates"
    - "Numeric columns contain no text (except headers)"
    - "ID columns are unique where expected"
    - "Email columns match basic email pattern"
    - "Phone columns are consistent format"
  
  business_rules:
    - "Revenue >= 0 (or explain negative = refund)"
    - "Dates within expected range (not in future for historical data)"
    - "Percentages between 0-100 (or 0-1, consistently)"
    - "Status values match allowed list"
    - "Foreign keys exist in reference table"
  
  completeness:
    - "Required columns have <5% missing"
    - "No orphan records (child without parent)"
    - "Date ranges are continuous (no gaps in daily data)"
```

### Data Quality Score (0-100)

| Dimension | Weight | Score 0-4 | Criteria |
|-----------|--------|-----------|----------|
| Completeness | 25% | | % of non-null values in required fields |
| Uniqueness | 15% | | % of rows with valid unique keys |
| Consistency | 20% | | % of values matching expected format/type |
| Accuracy | 20% | | % passing business rule validation |
| Timeliness | 10% | | Data freshness vs expected refresh |
| Conformity | 10% | | % matching standard formats (dates, phones, emails) |

**Score = Σ(weight × score/4 × 100)**

- 90-100: Production-ready
- 75-89: Minor fixes needed
- 50-74: Significant cleanup required
- <50: Re-collect or restructure before use

---

## Phase 9: Format Conversion & Interop

### Conversion Decision Matrix

| From → To | Best Method | Watch Out For |
|-----------|-------------|---------------|
| CSV → Excel | pandas + openpyxl | Encoding, date parsing, leading zeros |
| Excel → CSV | pandas or openpyxl | Multiple sheets, formulas lost, merged cells |
| JSON → CSV | pandas json_normalize | Nested objects need flattening |
| CSV → JSON | pandas to_json | Choose records vs columns orientation |
| Excel → Google Sheets | Upload directly | Macros stripped, some formulas differ |
| Google Sheets → Excel | Download as .xlsx | IMPORTRANGE breaks, custom functions lost |
| PDF table → CSV | Tabula, pdfplumber | Layout detection, merged cells, multi-page |
| HTML table → CSV | pandas read_html | Multiple tables, nested tables, encoding |

### Encoding Survival Guide

```
Garbled text? Try these encodings in order:
1. UTF-8 (default, handles all languages)
2. UTF-8-BOM (Windows exports often add BOM)
3. Latin-1 / ISO-8859-1 (Western European)
4. Windows-1252 (Windows "ANSI")
5. Shift-JIS (Japanese)
6. GB2312 / GBK (Chinese)

Python: pd.read_csv("file.csv", encoding="utf-8-sig")
Detection: chardet or charset-normalizer library
```

---

## Phase 10: Performance & Scale

### Size Thresholds

| Rows | Tool Recommendation |
|------|-------------------|
| <10K | Any tool (Excel, Sheets, pandas) |
| 10K-100K | Excel (careful) or pandas |
| 100K-1M | pandas with chunking, or DuckDB |
| 1M-10M | DuckDB, Polars, or database |
| >10M | Database (PostgreSQL, BigQuery) |

### Performance Tips

- **Read only needed columns**: `pd.read_csv(file, usecols=["col1","col2"])`
- **Specify dtypes upfront**: Prevents inference overhead
- **Use chunking for large files**: `pd.read_csv(file, chunksize=50000)`
- **Categoricals for low-cardinality**: `df["status"] = df["status"].astype("category")`
- **Avoid iterrows**: Use vectorized operations or `.apply()`
- **DuckDB for SQL on files**: `duckdb.sql("SELECT * FROM 'file.csv' WHERE x > 100")`

---

## Phase 11: Edge Cases & Gotchas

### The Dirty Dozen (most common data problems)

1. **Mixed date formats** — US (MM/DD) vs EU (DD/MM) vs ISO (YYYY-MM-DD) in same column
2. **Excel date serial numbers** — 44927 instead of 2023-01-01
3. **Leading zeros stripped** — ZIP code 01234 becomes 1234
4. **Scientific notation** — ID 1234567890123 becomes 1.23457E+12
5. **Hidden characters** — Non-breaking spaces, zero-width chars, BOM markers
6. **Merged cells** — Only top-left has value, rest are empty
7. **Number-as-text** — "100" (text) vs 100 (number), looks identical
8. **Locale-dependent decimals** — 1,234.56 vs 1.234,56
9. **Empty string vs NULL** — "" and NaN behave differently
10. **Trailing whitespace** — "New York " ≠ "New York"
11. **Excel 1904 date system** — Mac-origin files, dates off by 4 years
12. **Formula results vs formulas** — Copy-paste values loses formulas silently

### Multi-Currency Handling

```yaml
currency_rules:
  - Store amount AND currency code in separate columns
  - Never mix currencies in a single column without code
  - Use ISO 4217 codes (USD, GBP, EUR, BTC)
  - Store exchange rate and rate date used for conversion
  - Keep original amount + converted amount as separate columns
  - Specify: is this the rate at transaction time or current rate?
```

### Time Zone Handling

```yaml
timezone_rules:
  - Store timestamps in UTC internally
  - Record the source timezone
  - Convert to local time only for display
  - "End of day" = 23:59:59 in the business timezone, not UTC
  - Daylight saving transitions can cause 23h or 25h days
  - Aggregate daily data in business timezone, not UTC
```

---

## Phase 12: Quality Scoring Rubric (0-100)

| Dimension | Weight | 0 (Fail) | 1 (Poor) | 2 (Fair) | 3 (Good) | 4 (Excellent) |
|-----------|--------|----------|----------|----------|----------|----------------|
| **Data Cleanliness** | 20% | Raw dump, untouched | Some cleaning, inconsistent | Most issues addressed | Clean with documented process | Spotless + automated validation |
| **Structure** | 15% | Unstructured mess | Basic tabular, issues | Proper structure, minor gaps | Tidy data, good schema | Perfect normalization + relationships |
| **Analysis Depth** | 20% | No analysis | Basic counts/sums | Segmented analysis | Multi-dimensional + insights | Predictive + prescriptive + actions |
| **Visualization** | 15% | No charts | Wrong chart types | Adequate charts | Clear, well-labeled charts | Publication-quality dashboards |
| **Documentation** | 10% | None | Minimal notes | Column descriptions | Full data dictionary + methodology | Reproducible + versioned |
| **Automation** | 10% | Manual everything | Some formulas | Template-based | Scripted pipeline | Fully automated + monitored |
| **Accuracy** | 10% | Unverified | Spot-checked | Sample-validated | Cross-referenced with source | Reconciled + audit trail |

**Grading: 90+** = Production analytics, **75-89** = Solid work, **60-74** = Needs improvement, **<60** = Redo

---

## Natural Language Commands

```
"Clean this CSV"           → Run Phase 2 cleaning protocol, output clean file + log
"Analyze this data"        → Phase 1 assessment → Phase 4 analysis → insights
"Build a dashboard"        → Phase 5 template → populate with data
"Convert this to Excel"    → Phase 9 conversion with quality preservation
"Find duplicates"          → Dedup analysis with exact + fuzzy matching
"What's wrong with this data?" → Phase 1 health check + Phase 8 validation
"Create a monthly report"  → Phase 6 automation template
"Compare these two files"  → Join + variance analysis
"Summarize by category"    → Group + aggregate + Pareto analysis
"Make this data tidy"      → Unpivot/reshape to 1-row-per-observation
"Set up a budget tracker"  → Phase 7 Pattern 5 template
"Profile this dataset"     → Full Phase 1 + Phase 8 quality score
```

---

## Related AfrexAI Skills

- `afrexai-data-analyst` — Advanced analytical methodology (DICE framework, statistical analysis)
- `afrexai-fpa-engine` — Financial planning & analysis with spreadsheet models
- `afrexai-budget-tracker` — Personal/business budget management
- `afrexai-business-automation` — Automate recurring spreadsheet workflows

---

⚡ **Level up your data game** → [AfrexAI Context Packs ($47)](https://afrexai-cto.github.io/context-packs/) — industry-specific data templates, KPI frameworks, and reporting automations for SaaS, Fintech, Manufacturing, Ecommerce, and more.

🔗 **More free skills by AfrexAI:**
- `afrexai-data-analyst` — Complete data analysis methodology
- `afrexai-business-automation` — Workflow automation frameworks
- `afrexai-seo-content-engine` — SEO-optimized content creation
- `afrexai-customer-success` — Customer retention & health scoring
- `afrexai-devops-engine` — DevOps & platform engineering

📦 Browse all: [AfrexAI Storefront](https://afrexai-cto.github.io/context-packs/)
