---
name: quality-report
description: Generates quality daily, weekly, or monthly reports from key figures and events. Outputs both Excel and PPT (or content for both). If the user has no data, generates realistic mock data. Use for 品质日报/周报/月报, quality KPI summaries, or management quality reports.
triggers:
  - quality daily report
  - quality weekly report
  - quality monthly report
  - 品质日报
  - 品质周报
  - 品质月报
  - quality report
  - quality KPI report
  - 质量日报
  - 质量周报
  - 质量月报
  - 日报
  - 周报
  - 月报
  - 简单周报
  - 复杂周报
  - 简单月报
  - 复杂月报
  - simple weekly report
  - complex monthly report
---

# Quality Daily / Weekly / Monthly Report

Generates **quality reports** for a chosen period (day, week, or month). You provide the report type, period, and key data; the skill outputs **both Excel and PPT** (or content ready for both). If the user provides **no data**, the skill generates **realistic mock data** so the report is complete and usable as a template. Output includes metrics, issues and actions, highlights, and next-period focus. Suitable for quality teams, production quality, and management reporting.

---

## Report type and focus

| Type | Focus | Typical length |
|------|--------|-----------------|
| **Daily** | Operational: output, yield, defect count, line stops, today’s issues, tomorrow’s focus | Short (1–2 pages) |
| **Weekly** | Trend summary: yield/PPM/Cpk vs last week, major issues and actions, customer complaints, next week focus | Simple 1 page / Complex 2–3 pages |
| **Monthly** | Strategic: KPI vs target, trends, major projects, customer quality summary, next month focus | Simple 1–2 pages / Complex 3–5 pages |

---

## Report variant: Simple vs Complex (周报 / 月报)

For **weekly** and **monthly** reports only, offer two variants. Ask the user which they need when they choose weekly or monthly.

| Variant | 周报 | 月报 | Use when |
|---------|------|------|----------|
| **Simple 简单版** | One page: 3–5 KPIs, 1–2 issues, next focus. No or one chart. | 1–2 pages: KPI table, main issues, next focus. Minimal charts. | Line/team internal, email to manager, quick read. |
| **Complex 复杂版** | 2–3 pages: full metrics table, trend chart, Pareto, issues table, complaints table, highlights, action tracker. | 3–5 pages: multi-dimension KPI, trend/Pareto/cost of quality, detailed issues and 8D status, projects, customer summary, appendix. | Quality department, management meeting, customer/OEM, multi-site. |

- **Daily report**: No variant; use the single daily template.
- If the user does not specify variant for weekly/monthly, **first show "请选择模板"** (see below) and wait for the user to choose 1, 2, or 3; do not assume Simple or Complex without showing the menu.

---

## 请选择模板 (Template selection) — must display for 周报/月报

When the user asks for a **weekly** or **monthly** report, **you must first output** the following template selection in the same language as the user (e.g. 中文). Wait for the user to reply with 1, 2, 3, or 4 (or the corresponding keyword) before proceeding.

**Copy the following block to the conversation (adjust language if user uses English):**

```
请选择模板

1. 简单模板：一页摘要，核心 KPI（良率、PPM、客诉）+ 1～2 条主要问题 + 下阶段重点。适合产线/班组内、邮件汇报。

2. 完整过程模板：从封面到「谢谢浏览」的完整周报/月报，含封面与编号、质量状况综述（市场反馈、成品管理、外检、过程、计量、体系）、总体不良率与客户工程/客户市场、客户投诉统计、质量信息跟进、成品抽样与批量不良、外协抽检及分布图、装配/焊涂各线下线统计与趋势图、外检进货、外协主要问题及饼图、计量与体系、下周/下月工作计划。适合质量部正式汇报、管理层、PPT 全文。

3. 三地/多工厂汇总模板：多工厂（如工厂A、工厂B、工厂C）数据汇总，含三地投诉总次数与闭环率、各工厂分项、客户工程/客户市场退回责任划分。适合集团或三地工厂品质周报。

4. 首检送检制程模板：按目录五模块（首检合格率及不良分析、送检合格率及不良分析、制程质量异常状况、来料质量状况、出货合格率），**须含图表**：首检/送检每日表+趋势图（折线图）、周对比柱状图、调机员/操作员合格率柱状图、首检/送检不良项目饼图、制程异常周对比图、来料合格率柱状图/趋势图（不得仅输出表格）。适合制程/产线品质周报（机加工、CNC、调机员与操作员维度）。

请回复 1、2、3 或 4（或说明「简单」「完整过程」「三地」「首检送检」）。
```

**If the user uses English**, show the same four options in English, e.g. add: "4. First-inspection & submission & process template: Five sections (first inspection, submission inspection, process anomaly, incoming material, outgoing) with adjuster/operator pass rates and defect pie charts. Reply with 1, 2, 3, or 4."

**Mapping:**
- User replies **1** or 简单 → use **Simple** template (Weekly/Monthly Simple in this SKILL).
- User replies **2** or 完整 / 完整过程 → use **完整过程** template: Complex content + full structure from `{baseDir}/examples/sample-full-process-weekly.md` (cover → 质量状况综述 → 不良率与客户工程/市场 → 客诉表 → 跟进表 → 成品抽样与批量不良 → 外协抽检与饼图 → 装配/焊涂统计与推移图 → 外检进货 → 外协主要问题与饼图 → 计量体系 → 工作计划 → 谢谢浏览). Generate Excel/PPT with one sheet/slide per major section.
- User replies **3** or 三地 / 多工厂 → use **三地/多工厂汇总** template: structure from `{baseDir}/examples/sample-san-di-weekly.md` (三地投诉表、客户工程/市场责任划分、各工厂 KPI 可选、下阶段重点).
- User replies **4** or 首检送检 / 制程来料 → use **首检送检制程** template: structure from `{baseDir}/examples/sample-shoujian-songjian-weekly.md` (目录五模块；**必须输出图表**：首检/送检合格率趋势图（折线图）、周对比柱状图、调机员/操作员合格率柱状图、不良项目饼图、制程异常周对比图、来料合格率柱状图/趋势图；除表格外每节须带 Mermaid 或图表数据规格).

---

## Workflow (fixed order)

1. **Choose report type and period**
   - Ask: "Which report do you need: **daily**, **weekly**, or **monthly**? And for which date/period?" (e.g. 2025-03-14, Week 11, March 2025.)
2. **Show template selection (weekly / monthly only)**
   - If the user chose **weekly** or **monthly**, **output the "请选择模板" block** above (in the user’s language). Wait for the user to choose **1**, **2**, **3**, or **4** (or 简单 / 完整过程 / 三地 / 首检送检). Then use the corresponding template: 1 → Simple; 2 → 完整过程 (see `examples/sample-full-process-weekly.md`); 3 → 三地汇总 (see `examples/sample-san-di-weekly.md`); 4 → 首检送检制程 (see `examples/sample-shoujian-songjian-weekly.md`).
3. **Scope (optional)**
   - Ask if the report is for a specific **site**, **product line**, or **department** (e.g. "Production quality – Line A", "Incoming quality"). If not specified, use a generic scope or placeholder.
4. **Gather data**
   - Ask for key figures the user has. Typical inputs: **Metrics** (output, yield, defect count, PPM, Cpk, complaints), **Events** (defects, complaints, containments), **Highlights** (projects, improvements).
   - **If the user has no data** (says "no data", "use sample", "fill with mock data", or does not provide any figures): generate **realistic mock data** for all sections (see "Mock data when user has none" below). Do not leave tables empty or use only `[To be filled]`. Add a clear note in the report: **"※ 本报告使用模拟数据，仅作格式演示 / This report uses sample data for template demonstration only — replace with actual data."**
   - If the user provides partial data: fill those; for missing items use mock data and mark the note above, or use placeholders only for the missing cells.
5. **Generate report**
   - Use the template for the chosen type and variant: Daily (single template); Weekly **Simple** or **Complex**; Monthly **Simple** or **Complex**. Fill with user data or mock data. Match language to the user (English or 中文).
6. **Charts and attachments**
   - **Simple** variant: minimal or one chart; **Complex** variant: include trend and Pareto (text/Mermaid or placeholder). Generate from user or mock data when possible.
   - **模板 4（首检送检制程）**：**必须包含图表，不得仅输出表格。** 每节除数据表外须至少提供下列之一：① 对应图表的 **Mermaid 代码**（折线图/柱状图/饼图）；② **图表数据规格**（图表类型、横纵轴、系列、数据点或占比），便于用户导出为 PPT/Excel 图表。必备图表包括：首检合格率**趋势图（折线图）**、送检合格率**趋势图（折线图）**、首检/送检**周对比柱状图**、调机员/操作员合格率**柱状图**、首检/送检不良项目**饼图**、制程异常数量**周对比柱状图**、来料合格率**柱状图或趋势图**。调机员/操作员示例姓名用「人员A」「人员B」等占位，勿用真实姓名。
7. **Output: Excel and PPT together**
   - Produce **both** of the following (see "Excel and PPT output" below):
     - **Excel**: Either (a) generate an `.xlsx` file (e.g. via Python `openpyxl`: one sheet for basic info + metrics, one for issues, one for complaints/focus) and save to the workspace, or (b) output a **CSV** (or multiple CSVs) and a clear "Excel layout" section with tables that the user can paste into Excel. Filename pattern: `Quality-Report-{Daily|Weekly|Monthly}-{date-or-period}.xlsx` or `.csv`.
     - **PPT**: Either (a) generate a `.pptx` file (e.g. via Python `python-pptx`: title slide, summary, metrics table, issues, next focus) and save to the workspace, or (b) output a **slide-by-slide** block (Slide 1: Title, Slide 2: Summary, Slide 3: Metrics table, …) that the user can paste into PowerPoint. Filename pattern: `Quality-Report-{Daily|Weekly|Monthly}-{date-or-period}.pptx`.
   - If the environment allows running Python with `openpyxl` and `python-pptx`, prefer generating real `.xlsx` and `.pptx` files; otherwise deliver structured Markdown/CSV + slide outline so the user can copy into Excel and PPT.

---

## Mock data when user has none

When the user provides **no data** (or explicitly asks for sample/mock data), generate **realistic mock data** so the report is complete. Use plausible values; do not leave metrics or tables empty.

**Metrics (plausible ranges)**:
- **Output**: e.g. 4,200 (daily), 25,000 (weekly), 98,000 (monthly) — adjust by scope (line/site).
- **Yield (%)**: e.g. 97.5–99.2; target e.g. 98.0 or 98.5.
- **Defect count**: consistent with output and yield (e.g. yield 98% → defect rate 2% of output).
- **PPM**: e.g. 15,000–25,000; target e.g. ≤20,000.
- **Cpk**: e.g. 1.2–1.5 (key process).
- **Line stop**: e.g. 0–2 times, 0–15 min.
- **Customer complaints**: e.g. 0–2 (weekly/monthly).

**Issues and events (mock)**:
- Use generic but realistic descriptions, e.g. "Surface scratch on batch XXX – containment 100% inspection; 8D in progress", "Fixture wear caused dimension drift – fixture replaced; re-verification done."
- **Next period focus**: e.g. "Complete 8D for customer A complaint", "Implement new inspection point for Line 2", "Cpk re-validation for process X."

**Report header**: Always add a visible line at the top of the report (and, if possible, in Excel/PPT):  
**"※ 本报告使用模拟数据，仅作格式演示 / This report uses sample data for template demonstration only — replace with actual data."**

---

## Excel and PPT output (dual output)

**Excel** — structure to produce (as .xlsx or as CSV + table blocks):

- **Simple** variant: Fewer sheets — e.g. "Info", "Metrics", "NextFocus" (and optionally one row for main issue). Same filename pattern.
- **Complex** variant: Full sheets — "Info", "Metrics", "Issues", "Complaints", "NextFocus". Same as below.

| Sheet / block | Content |
|---------------|---------|
| **Basic info** | Report type, period, scope, reporter, report date. |
| **Metrics** | One table: metric name, value, target, trend/comparison (weekly/monthly). Same as the "Key metrics" section in the report. |
| **Issues & actions** | Table: No., Issue, Action/Owner, Status. (Complex; optional in Simple.) |
| **Complaints** (if any) | Table: Customer, Product, Issue, Status. (Complex; optional in Simple.) |
| **Next focus** | List: action items for next period. |

If generating .xlsx via Python (`openpyxl`), create one workbook with sheets as above. Save as `Quality-Report-{Type}-{Simple|Complex}-{date-or-period}.xlsx` or omit Simple/Complex in name if preferred.

**PPT** — slide outline to produce (as .pptx or as slide-by-slide text):

- **Simple** variant: 3–4 slides — Title, Summary, Metrics, Next focus.
- **Complex** variant: 6 slides — Title, Summary, Metrics, Issues, Complaints, Next focus.

| Slide | Content |
|-------|---------|
| 1 | **Title**: Quality {Daily|Weekly|Monthly} Report — {period}. Subtitle: scope, date. |
| 2 | **Summary**: 2–5 bullet points from executive summary. |
| 3 | **Key metrics**: One table (same as report metrics). |
| 4 | **Major issues and actions**: Bullet or table. (Complex) |
| 5 | **Customer complaints** (if any): Brief list. (Complex) |
| 6 | **Next period focus**: Bullet list. |

If generating .pptx via Python (`python-pptx`), create a presentation with the above slides (fewer for Simple). Save as `Quality-Report-{Type}-{date-or-period}.pptx`. Otherwise output a "PPT slides" block for the user to copy.

---

## Company-specific format (optional)

If the user says their company has a **fixed report format** (e.g. specific section order or Excel template):
- Ask them to paste the **section titles** or attach a sample; then generate the report with that structure, mapping the standard content (metrics, issues, highlights, next focus) into their sections.
- Optional: store format definitions under `{baseDir}/formats/` (e.g. `formats/company-a.md`) and use them when the user names that company — same approach as in the 8D skill.

---

## Template – Daily report (品质日报)

```markdown
# Quality Daily Report

**Report date**: [ Date ]
**Scope**: [ Site / Line / Department ]
**Reporter**: [ Name ]

---

## 1. Summary (one line)

[ One sentence: overall quality status today, e.g. "Yield on target; one line stop due to defect." ]

---

## 2. Key metrics (today)

| Metric | Value | Target | Remark |
|--------|--------|--------|--------|
| Output (pcs) | | | |
| Yield (%) | | | |
| Defect count | | | |
| PPM (if applicable) | | | |
| Line stop (count / min) | | | |

---

## 3. Major issues today

| No. | Issue | Action / Status |
|-----|--------|-----------------|
| 1 | | |
| 2 | | |

---

## 4. Customer complaints / escalations

[ Any complaint or escalation today; if none: "None." ]

---

## 5. Tomorrow focus

- [ ] 
- [ ] 

---

**Attachments** (optional): [Attach: trend or Pareto if needed]
```

---

## Template – Weekly report, Simple (品质周报 简单版)

One-page style: core KPIs, 1–2 issues, next focus. No or one chart.

```markdown
# Quality Weekly Report (Simple)

**Period**: [ Week X, YYYY-MM-DD ~ YYYY-MM-DD ] | **Scope**: [ Site / Line ] | **Reporter**: [ Name ]

---

## Summary (2–3 lines)

[ Overall quality this week vs last week; one main issue if any; one highlight. ]

---

## Key metrics

| Metric | This week | Last week | Target |
|--------|-----------|-----------|--------|
| Yield (%) | | | |
| PPM | | | |
| Customer complaints | | | |

---

## Main issues (1–2 items)

1. [ Issue + brief action/status ]
2. [ If applicable ]

---

## Next week focus

- [ ] 
- [ ] 
```

---

## Template – Weekly report, Complex (品质周报 复杂版)

Full version: full metrics, trend, Pareto, issues table, complaints, highlights, action list.

```markdown
# Quality Weekly Report (Complex)

**Period**: [ Week X, YYYY-MM-DD ~ YYYY-MM-DD ]
**Scope**: [ Site / Line / Department ]
**Reporter**: [ Name ]

---

## 1. Executive summary

[ 2–3 sentences: overall quality performance this week vs last week; main issues and highlights. ]

---

## 2. Key metrics (week)

| Metric | This week | Last week | Target | Trend |
|--------|-----------|-----------|--------|--------|
| Output (pcs) | | | | |
| Yield (%) | | | | |
| Defect count | | | | |
| PPM | | | | |
| Cpk (key process, if applicable) | | | | |
| Customer complaints (count) | | | | |

**Trend / chart**: [Attach: yield or PPM trend chart] or [Insert: brief text summary of trend].

---

## 3. Major issues and actions

| No. | Issue | Action / owner | Status |
|-----|--------|----------------|--------|
| 1 | | | |
| 2 | | | |

---

## 4. Customer complaints summary (this week)

[ Table: customer, product, issue, status. If none: "None." ]

---

## 5. Highlights / improvements

- 
- 

---

## 6. Next week focus

- [ ] 
- [ ] 

---

**Attachments** (optional): [Attach: trend chart], [Attach: Pareto or defect breakdown].
```

---

## Template – Monthly report, Simple (品质月报 简单版)

1–2 pages: KPI table, main issues, next focus. Minimal charts.

```markdown
# Quality Monthly Report (Simple)

**Period**: [ Month YYYY ] | **Scope**: [ Site / Line ] | **Reporter**: [ Name ]

---

## Summary (3–5 lines)

[ KPI vs target this month; main problem if any; customer quality in one line; next month priority. ]

---

## KPI (month)

| Metric | This month | Target | Last month |
|--------|------------|--------|------------|
| Yield (%) | | | |
| PPM | | | |
| Customer complaints | | | |

---

## Main issues and actions (top 3)

1. [ Issue + action + status ]
2. 
3. 

---

## Next month focus

- [ ] 
- [ ] 
```

---

## Template – Monthly report, Complex (品质月报 复杂版)

Full version: multi-dimension KPI, trend/Pareto/cost of quality, detailed issues and 8D status, projects, customer summary.

```markdown
# Quality Monthly Report (Complex)

**Period**: [ Month YYYY ]
**Scope**: [ Site / Line / Department ]
**Reporter**: [ Name ]

---

## 1. Executive summary

[ 3–5 sentences: KPI vs target this month, main trends, major issues and projects, customer quality summary. ]

---

## 2. KPI overview (month)

| Metric | This month | Target | Last month | YTD / trend |
|--------|------------|--------|------------|-------------|
| Output (pcs) | | | | |
| Yield (%) | | | | |
| PPM | | | | |
| Cpk (key process) | | | | |
| Customer complaints (count) | | | | |
| Cost of quality (if applicable) | | | | |

**Charts**: [Attach: yield/PPM trend for the month], [Attach: Pareto – top defects].

---

## 3. Major issues and corrective actions

[ Table: key deviations, customer complaints, containments, 8D/CAR status, owner. ]

---

## 4. Projects and improvements

- Completed: 
- In progress: 
- Planned: 

---

## 5. Customer quality summary

[ Summary of customer complaints, PPM by customer, or delivery quality. ]

---

## 6. Next month focus

- [ ] 
- [ ] 

---

**Attachments** (optional): [Attach: trend charts], [Attach: Pareto], [Attach: management summary slide ref].
```

---

## Fill-in hints (when user does not provide data)

| Report type | Suggest |
|-------------|---------|
| Daily | "Please provide today’s output, yield, defect count, and any major issue or line stop. **If you have no data, I’ll generate mock data** so you get a complete Excel + PPT report as a template." |
| Weekly (Simple) | "Need **simple** (one-page) or **complex** (full) weekly report? Please provide this week’s yield, PPM, complaint count and 1–2 main issues — or I’ll use **mock data** and output Excel + PPT." |
| Weekly (Complex) | "Please provide this week’s key metrics (yield, PPM, complaint count) and last week’s for comparison, plus major issues and actions. **If you have no data, I’ll use mock data** and output both Excel and PPT (complex version)." |
| Monthly (Simple) | "Need **simple** (1–2 page) or **complex** (full) monthly report? Please provide this month’s KPI and main issues — or I’ll use **mock data** and output Excel + PPT." |
| Monthly (Complex) | "Please provide this month’s KPI vs target, main issues and projects, and customer quality summary. **If you have no data, I’ll fill with mock data** and produce Excel and PPT (complex version)." |

- If the user provides **no data**: Generate **mock data** for all sections (see "Mock data when user has none"); output both Excel and PPT (or content for both). Add the sample-data disclaimer in the report.
- If the user provides **numbers only** (e.g. yield 98.5%, 3 complaints): Fill the metrics table; use short mock or one-line text for narrative sections if needed.
- If the user provides **events only** (e.g. "one customer complaint about scratch"): Put that in issues/complaints; generate mock metrics consistent with the event.

---

## Output requirements

1. **Dual output**: Always produce **both Excel and PPT** (or content ready for both). Prefer generating real `.xlsx` and `.pptx` files when Python with `openpyxl` and `python-pptx` is available; otherwise provide CSV/table block for Excel and slide-by-slide block for PPT.
2. **Mock data**: When the user has no data, fill the report with **realistic mock data**; do not leave tables empty. Add the disclaimer: "※ 本报告使用模拟数据，仅作格式演示 / This report uses sample data for template demonstration only."
3. **Language**: Match the user (e.g. 中文 for 品质日报/周报/月报, English otherwise).
4. **Charts**: From user or mock data, add a short text trend or Mermaid/table when possible; otherwise use `[Attach: trend chart]` and remind to attach when exporting. **模板 4（首检送检制程）**：必须输出趋势图（折线图）、柱状图、饼图等，可为每图提供 Mermaid 代码或「图表类型 + 轴/系列 + 数据」规格，不得仅输出文字表格。
5. **Filenames**: Suggest or generate `Quality-Report-{Daily|Weekly|Monthly}-{date-or-period}.xlsx` and `Quality-Report-{Daily|Weekly|Monthly}-{date-or-period}.pptx` (and optionally a .md summary).

---

## References

- What to put in each report type and common KPI definitions: `{baseDir}/reference.md` (if present).
- **Template selection text (请选择模板)**: `{baseDir}/examples/template-choices-zh.md` (if present).
- **完整过程 template structure** (option 2): `{baseDir}/examples/sample-full-process-weekly.md` — cover to 谢谢浏览, all sections.
- **三地/多工厂 template structure** (option 3): `{baseDir}/examples/sample-san-di-weekly.md` — multi-site complaint and responsibility summary.
- **首检送检制程 template structure** (option 4): `{baseDir}/examples/sample-shoujian-songjian-weekly.md` — 目录五模块（首检、送检、制程异常、来料、出货）；**必须含图表**：首检/送检趋势图（折线）、周对比与调机员/操作员柱状图、不良饼图、来料合格率柱状图/趋势图；输出时每节除表格外须带 Mermaid 图或图表数据规格。
- Other example snippets: `{baseDir}/examples/` (if present).
