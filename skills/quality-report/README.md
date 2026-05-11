# Quality Daily / Weekly / Monthly Report (quality-report)

Generates **quality reports** for a chosen period: **daily**, **weekly**, or **monthly**. **Weekly and monthly** can be **Simple** (one-page summary) or **Complex** (full metrics, charts, detailed issues). Outputs **both Excel and PPT** (or content for both). If you have **no data**, the skill generates **realistic mock data**. You provide the report type, variant (for 周报/月报), period, and optional key data; the skill produces Excel + PPT.

## When to use

- Writing 品质日报 / 周报 / 月报 (quality daily / weekly / monthly reports)
- Quality KPI summaries for management
- Operational quality updates (yield, PPM, defects, complaints, actions)

## How to use

In an OpenClaw session, say what you need, for example:

- "写一份品质日报，日期 2025-03-14"
- "Generate a quality weekly report for Week 11"
- "品质月报，3 月份，需要填产量、良率、客诉数"

The agent will ask for report type, period, and key figures (or use placeholders), then generate the report using the appropriate template.

## Contents

| File / folder | Description |
|---------------|-------------|
| `SKILL.md` | Main skill: workflow, **请选择模板** (1 简单 / 2 完整过程 / 3 三地汇总 / 4 首检送检制程), daily/weekly/monthly templates, fill-in hints |
| `reference.md` | What to put in each report type, simple vs complex, common KPI definitions |
| `examples/template-choices-zh.md` | Template selection text (请选择模板) for display to user |
| `examples/sample-full-process-weekly.md` | Full process weekly structure (cover → 谢谢浏览), from real report screenshots |
| `examples/sample-san-di-weekly.md` | Multi-site (三地) weekly summary structure |
| `examples/sample-shoujian-songjian-weekly.md` | 首检/送检/制程/来料/出货 五模块周报结构（目录式） |
| `examples/sample-weekly-snippet.md` | Short weekly format example |
| `clawhub.json` | ClawHub publish metadata |

## Install (from ClawHub)

```bash
clawhub install quality-report
```

Takes effect in a new session.
