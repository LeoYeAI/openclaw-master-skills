# Quality Report Reference

This document supplements the "Quality Daily / Weekly / Monthly Report" skill with what to include in each report type and common KPI definitions.

---

## Report type at a glance

| Type | Purpose | Main content |
|------|---------|--------------|
| **Daily** | Operational visibility: what happened today, any escalation | Output, yield, defect count, line stops, today’s issues, tomorrow’s focus |
| **Weekly** | Trend and actions: how the week looked vs last week | Week metrics, major issues and actions, complaints, highlights, next week focus |
| **Monthly** | Management summary: KPI vs target, projects, customer quality | Month KPI, issues and CARs, projects, customer summary, next month focus |

---

## Simple vs Complex (周报 / 月报 简单版 vs 复杂版)

For **weekly** and **monthly** reports, the skill offers two variants:

| Variant | 周报 | 月报 | Typical use |
|---------|------|------|-------------|
| **Simple 简单版** | One page: 3–5 KPIs, 1–2 issues, next focus. Little or one chart. | 1–2 pages: KPI table, main issues, next focus. Minimal charts. | Line/team internal, email to manager, quick read. |
| **Complex 复杂版** | 2–3 pages: full metrics, trend chart, Pareto, issues table, complaints table, highlights, action list. | 3–5 pages: multi-dimension KPI, trend/Pareto/cost of quality, detailed issues and 8D status, projects, customer summary. | Quality department, management meeting, customer/OEM, multi-site. |

- **Excel/PPT**: Simple = fewer sheets/slides (e.g. Info, Metrics, Next focus); Complex = full sheets/slides (Info, Metrics, Issues, Complaints, Next focus).
- When the user asks for 周报 or 月报, the skill **first shows "请选择模板"** with four options (1 简单 / 2 完整过程 / 3 三地多工厂汇总 / 4 首检送检制程); see SKILL.md and `examples/template-choices-zh.md`. After the user chooses 1–4, the corresponding template is used. Option 4 follows the 目录五模块 structure (首检、送检、制程异常、来料、出货); see `examples/sample-shoujian-songjian-weekly.md`. **Template 4 must include charts** (趋势图、柱状图、饼图), not only tables—output Mermaid or chart data spec per section.
- If the user does not specify, **show the template menu**; do not assume Simple without displaying it.

---

## Common KPIs (definitions for fill-in)

| KPI | Meaning | Typical unit |
|-----|---------|--------------|
| **Output** | Quantity produced (or inspected) in the period | pcs |
| **Yield** | Good quantity / total quantity (or first-pass yield) | % |
| **Defect count** | Number of defectives in the period | count |
| **PPM** | Defects per million (opportunities or pieces) | PPM |
| **Cpk** | Process capability index (key process) | — |
| **Line stop** | Count or total minutes of line stoppage due to quality | count / min |
| **Customer complaints** | Number of complaints (or CARs opened) in the period | count |
| **Cost of quality** | Internal/external failure cost or total COQ (if tracked) | currency |

Use these when the user mentions "yield", "PPM", "Cpk", etc., and place them in the correct table.

---

## What to put in each section

- **Summary / Executive summary**: One (daily) or a few (weekly/monthly) sentences: overall quality status, main problem if any, main highlight.
- **Key metrics**: Table with actual, target, and optionally last period or trend. Weekly and monthly: include comparison to last period.
- **Major issues and actions**: List or table: issue description, action taken or owner, status. Link to 8D/CAR if applicable.
- **Customer complaints**: Count and brief summary (customer, product, issue, status). Monthly: can add PPM by customer or delivery quality summary.
- **Highlights / Improvements**: Projects completed, process improvements, recognitions. More detail in monthly.
- **Next period focus**: Action items or priorities for the next day/week/month.

---

## Charts and attachments

- **Daily**: Optional trend or Pareto if there was a notable defect; usually not required.
- **Weekly**: Recommended: yield or PPM trend (this week vs last weeks); optional Pareto for top defects.
- **Monthly**: Recommended: yield/PPM trend for the month, Pareto for top defects; optional Cpk trend or management summary slide.

When the user provides time-series or defect-by-category data, the skill can generate a short text trend or table; otherwise use placeholders and remind to attach charts when exporting to Excel or PPT.

---

## Mock data (when user has no data)

When the user provides no data, the skill generates **realistic mock data** so the report is complete and usable as a template. Use plausible ranges:

- **Yield**: e.g. 97.5–99.2%; target 98.0 or 98.5%.
- **PPM**: e.g. 15,000–25,000; target ≤20,000.
- **Output**: Scale by period (daily ~4k, weekly ~25k, monthly ~98k) and scope.
- **Defect count**: Consistent with output and yield (e.g. 2% defect rate if yield 98%).
- **Customer complaints**: 0–2 for week/month; 0 for day unless specified.
- **Issues**: Generic but realistic (e.g. "Surface scratch – containment and 8D in progress", "Fixture wear – replaced and re-verified").

Always add a clear disclaimer in the report and, if possible, in Excel/PPT: "This report uses sample data for template demonstration only — replace with actual data."

---

## Excel and PPT output

The skill outputs **both**:

- **Excel**: Workbook with sheets (or CSV/table block): Basic info, Metrics, Issues, Complaints, Next focus. Filename: `Quality-Report-{Type}-{period}.xlsx` or `.csv`.
- **PPT**: Presentation (or slide-by-slide text): Title, Summary, Metrics, Issues, Complaints, Next focus. Filename: `Quality-Report-{Type}-{period}.pptx`.

When the environment allows, the agent may generate real `.xlsx` and `.pptx` files via Python (`openpyxl`, `python-pptx`); otherwise it provides structured content for copy-paste into Excel and PowerPoint.

---

## Company-specific format

If the company has a fixed report layout (e.g. specific section order, Excel template, or internal system), the user can paste section titles or attach a sample. The skill then maps the standard content (metrics, issues, highlights, next focus) into that structure. Optional: store format definitions under `formats/` (see SKILL.md) for reuse.

---

*This reference is used together with SKILL.md; report generation follows the workflow and templates in SKILL.md.*
