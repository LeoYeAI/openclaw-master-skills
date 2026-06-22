---
name: pivot
description: "Operational playbook for building PivotTables with the MiniMaxXlsx CLI. Treat this as the source of truth before invoking the pivot subcommand."
---

# Pivot Operations Manual

Use this guide when a workbook needs grouped aggregation, cross-axis summaries, or interactive drilldown.

## 1) Decision Gate

Choose PivotTable mode when one or more conditions are true:

- The request explicitly asks for a pivot table
- The dataset is large enough that formula-only summaries become hard to maintain
- The user needs category-by-category totals, count splits, or two-dimensional breakdowns
- The output must support manual filtering and regrouping inside Excel

Do not force PivotTable mode for trivial one-line totals. Use formulas for simple, static math.

## 2) Input Readiness Contract

Before running any pivot command, confirm:

- Header row exists and every header is unique
- Source block has no merged cells
- No blank row breaks inside the data block
- Aggregation fields are numeric where required
- Workbook formulas already passed structural checks

Recommended preflight sequence:

```bash
./scripts/MiniMaxXlsx refcheck working.xlsx
./scripts/MiniMaxXlsx info working.xlsx --pretty
```

`info` output is authoritative. Never guess sheet names or ranges manually.

## 3) Seven-Checkpoint Flow

Follow this exact flow to avoid broken files:

1. **Assemble base workbook** with openpyxl (cover, raw data, helper sheets)
2. **Save once** and run `refcheck`
3. **Inspect metadata** using `info --pretty`
4. **Draft pivot command** from inspected headers and ranges
5. **Run pivot as final write operation**
6. **Run structural validation** with `check`
7. **Deliver without reopening output in openpyxl**

Why checkpoint 7 matters: a second openpyxl save can repackage XML relationships and invalidate pivot internals.

## 4) Command Surface

### Required arguments

| Argument | Meaning | Example |
|---|---|---|
| `input.xlsx` | Source workbook to read | `working.xlsx` |
| `output.xlsx` | New workbook to generate | `deliverable.xlsx` |
| `--source` | Full source range with sheet prefix | `"RevenueLog!B3:H920"` |
| `--location` | Pivot anchor cell | `"PivotBoard!C4"` |
| `--values` | Metric + reducer list | `"NetAmount:sum,OrderNo:count"` |

### Optional arguments

| Argument | Meaning | Example |
|---|---|---|
| `--rows` | Row grouping fields | `"Region,Channel"` |
| `--cols` | Column grouping fields | `"Quarter"` |
| `--filters` | Page filters | `"Year,Owner"` |
| `--name` | Pivot object name | `"QuarterlyMix"` |
| `--style` | Theme (`monochrome` / `finance`) | `"monochrome"` |
| `--chart` | Companion chart (`bar` / `line` / `pie`) | `"line"` |

Supported reducers: `sum`, `count`, `avg`, `average`, `min`, `max`.

## 5) Parameter Assembly Pattern

Build parameters in this order to reduce mistakes:

1. `--location` (destination first)
2. `--values` (what to aggregate)
3. `--source` (where data comes from)
4. `--rows` / `--cols` / `--filters` (how to slice)
5. `--name` / `--style` / `--chart` (presentation)

This ordering is intentional: start from reporting target, then metric intent, then data origin.

## 6) Fresh Example Set

### Scenario A: Operations latency rollup

```bash
./scripts/MiniMaxXlsx pivot \
    ops_raw.xlsx ops_pivot.xlsx \
    --location "OpsPivot!B5" \
    --values "LatencyMs:avg,RequestId:count" \
    --source "ApiEvents!A1:G1800" \
    --rows "Service,Cluster" \
    --filters "ReleaseTag" \
    --name "LatencyOverview" \
    --style "monochrome" \
    --chart "line"
```

### Scenario B: Clinic visit mix by month

```bash
./scripts/MiniMaxXlsx pivot \
    clinic_daily.xlsx clinic_report.xlsx \
    --location "VisitSummary!A4" \
    --values "VisitFee:sum,VisitId:count" \
    --source "VisitLog!A1:F2400" \
    --rows "Department" \
    --cols "VisitMonth" \
    --name "DeptVisitMix" \
    --style "finance" \
    --chart "bar"
```

### Scenario C: Warehouse damage composition

```bash
./scripts/MiniMaxXlsx pivot \
    warehouse_events.xlsx warehouse_dashboard.xlsx \
    --location "LossShare!D3" \
    --values "LossCost:sum" \
    --source "DamageRecords!A1:E460" \
    --rows "LossType" \
    --filters "Warehouse" \
    --name "LossStructure" \
    --chart "pie"
```

## 7) Validation and Release Rule

Run:

```bash
./scripts/MiniMaxXlsx check deliverable.xlsx
```

- Exit code `0`: release candidate
- Non-zero: do not patch the xlsx in place; regenerate from corrected source flow

## 8) Failure Playbook

| Symptom | Likely Cause | Action |
|---|---|---|
| Pivot shows no records | Source range clipped | Re-run `info`, expand `--source` to full block |
| "Field not found" | Header mismatch or typo | Copy header text directly from `info` output |
| Validation fails on pivot nodes | Damaged pivot relationships | Rebuild from base workbook, run pivot once as final step |
| CLI execution fails unexpectedly | Workbook locked by another app | Close Excel/WPS process and retry |

## 9) Hard Prohibitions

- Do not manually construct pivot XML
- Do not run pivot before all openpyxl sheet edits are complete
- Do not open and save pivot output with openpyxl
- Do not deliver files that fail `check`

If any prohibition is violated, regenerate the workbook end-to-end.
