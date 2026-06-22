---
name: charts
description: "Chart creation and verification guide for the minimax-xlsx skill. Read this document when the task requires embedded Excel charts or data visualizations."
---

**Path note**: Relative paths in this document (e.g., `./scripts/`) are anchored to the skill directory that contains this file.

<embedded_objects>

## Charts Must Be Real Embedded Objects

**Proactive stance on visualization:**
- If the user asks for charts or visuals, generate them immediately — don't wait for per-dataset instructions
- When a workbook has multiple data tables, each table should have at least one chart unless the user says otherwise
- If any dataset lacks a chart, explain why and confirm before shipping

**What you must NOT do:**
- Output a helper-only "chart dataset" tab and ask the user to insert charts manually
- Mark chart work complete while expecting end users to finish chart insertion
- Mark "Add visual charts" as completed without embedding actual chart objects

**What you must do:**
- Build embedded charts inside the .xlsx via openpyxl by default
- Standalone image exports (PNG/JPG) only when explicitly requested

</embedded_objects>

<creation_sequence>

**Mandatory sequence:**
```
1. Construct the workbook with openpyxl (data, styling)
2. Insert charts using openpyxl.chart classes
3. Save the file
4. Run chart to confirm charts have data and detect overlaps
5. If exit code is 1 → fix empty/malformed charts
6. If overlaps reported → reposition charts (see overlap fixing below)
```

</creation_sequence>

<code_samples>

**Imports:**
```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
```

**Bar chart walkthrough:**
```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

wb = Workbook()
ws = wb.active

rows = [
    ['Region', 'Revenue'],
    ['East', 480],
    ['West', 320],
    ['North', 560],
    ['South', 410],
]
for r in rows:
    ws.append(r)

ch = BarChart()
ch.type = "col"
ch.style = 10
ch.title = "Revenue by Region"
ch.y_axis.title = 'Revenue'
ch.x_axis.title = 'Region'

vals = Reference(ws, min_col=2, min_row=1, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)

ch.add_data(vals, titles_from_data=True)
ch.set_categories(cats)
ch.shape = 4

ws.add_chart(ch, "E2")

wb.save('output.xlsx')
```

### Chart Type Selection

| Data Pattern | Chart Class | Key Config |
|---|---|---|
| Vertical comparison | `BarChart()` | `type="col"` (vertical) or `type="bar"` (horizontal) |
| Temporal trend | `LineChart()` | `style=10`, optional markers |
| Proportional split | `PieChart()` | No axes needed |
| Cumulative spread | `AreaChart()` | `grouping="standard"` |

### Line Chart Sample
```python
from openpyxl.chart import LineChart, Reference

ch = LineChart()
ch.title = "Trend Analysis"
ch.style = 13
ch.y_axis.title = 'Value'
ch.x_axis.title = 'Month'

vals = Reference(ws, min_col=2, min_row=1, max_row=13, max_col=3)
ch.add_data(vals, titles_from_data=True)
cats = Reference(ws, min_col=1, min_row=2, max_row=13)
ch.set_categories(cats)

ws.add_chart(ch, "E2")
```

### Pie Chart Sample
```python
from openpyxl.chart import PieChart, Reference

pie = PieChart()
pie.title = "Market Share"

vals = Reference(ws, min_col=2, min_row=1, max_row=5)
labels = Reference(ws, min_col=1, min_row=2, max_row=5)

pie.add_data(vals, titles_from_data=True)
pie.set_categories(labels)

ws.add_chart(pie, "E2")
```

</code_samples>

<post_check>

**Post-generation check (non-negotiable):**
```bash
./scripts/MiniMaxXlsx chart output.xlsx -v
```
Exit code 1 means broken charts — they must be fixed. No rationalizations — if chart fails, the chart IS defective regardless of how data was embedded.

</post_check>

<collision_handling>

### Overlap Detection and Resolution

`chart` automatically detects chart collisions on each sheet. When overlaps are reported, reposition charts before delivery.

**Overlap report fields**: `ChartA`, `ChartB`, `SheetName`, `RangeA`, `RangeB`, `OverlapRegion`, `OverlapPercentage`

**Repositioning guidelines:**
- **Vertical stacking** (preferred): Place charts below each other with **2 empty rows** between
- **Side-by-side**: When sheet width allows, place horizontally with **1 empty column** gap
- **Consistent sizing**: Keep charts on the same sheet at uniform dimensions (default: 10 columns wide x 15 rows tall)
- Use position data from `-v` output to calculate non-overlapping anchors

**Overlap fix example:**
```python
# chart reported: chart1 at E2:N17, chart2 at E15:N30 (overlap at E15:N17)
# Fix: stack vertically with 2-row gap
from openpyxl import load_workbook

wb = load_workbook('output.xlsx')
ws = wb['SheetName']

for i, chart in enumerate(ws._charts):
    chart.anchor = f'E{2 + i * 17}'  # 15 rows height + 2 rows gap

wb.save('output.xlsx')
```

After repositioning, re-run `chart -v` to confirm zero overlaps.

**Theme-appropriate chart colors:**
- Grayscale: `2C2C2C`, `6B6B6B`, `1565C0`, `5B8DB8`
- Financial: `1B3A5C`, `2A6496`, `5B9BD5`, `8FBCD8`

**Chart type decision guide:**
| Data Scenario | Chart | Use Case |
|---|---|---|
| Temporal progression | Line | Time series |
| Category comparison | Column/Bar | Side-by-side metrics |
| Part-of-whole | Pie/Doughnut | Percentages (6 items max) |
| Data spread | Histogram | Distribution shape |
| Variable relationships | Scatter | Correlation analysis |

</collision_handling>
