---
name: report-generator
description: >
  Generate automated financial and business reports with PDF output, chart creation, and distribution.
  Use when: (1) producing recurring financial reports (P&L, balance sheet, cash flow), (2) generating
  client-ready performance summaries, (3) creating board/exec dashboards with charts, (4) automating
  scheduled report distribution via email or messaging, (5) converting raw financial data into
  formatted deliverables. NOT for: one-off ad hoc data queries (use direct analysis), real-time
  dashboards requiring live data push (use dedicated BI tools), or compliance filings with regulatory
  signatures required (those need human review and approval).
metadata:
  openclaw:
    requires:
      bins: []
    tags:
      - finance
      - reporting
      - automation
      - pdf
      - charts
---

# Report Generator Skill

Automates the full report lifecycle: data extraction → formatting → chart generation → PDF rendering → distribution.

---

## Core Capabilities

### 1. Financial Report Types

| Report | Frequency | Primary Audience |
|--------|-----------|-----------------|
| Profit & Loss (Income Statement) | Monthly / Quarterly | CEO, Board |
| Balance Sheet | Monthly / Quarterly | CEO, Investors |
| Cash Flow Statement | Weekly / Monthly | CFO, Ops |
| AR/AP Aging Summary | Weekly | AR Team, Controller |
| Budget vs Actual Variance | Monthly | Department Heads |
| KPI Dashboard | Weekly / Monthly | All Executives |
| Client Profitability Report | Monthly / Quarterly | Partners |
| Payroll Summary | Per-payroll-run | HR, Finance |

### 2. Business Reports

- **Operations Report** — headcount, utilization, productivity metrics
- **Sales Pipeline Report** — funnel stages, conversion rates, projected revenue
- **Expense Analysis** — category breakdowns, trend lines, anomaly flagging
- **Vendor Spend Report** — top vendors, spend trends, contract compliance
- **Project Profitability** — budget vs actuals per engagement

---

## Workflow

### Step 1: Data Collection

Identify the source system and extract the raw data:

```bash
# QuickBooks export (CSV)
# Pull via QBO skill or manual export from client portal
# Source: reports/raw/2026-03-pl-raw.csv

# Google Sheets source
gog sheets read --id SHEET_ID --range "P&L!A1:Z100" > reports/raw/pl-data.json

# SQL/database source
# sqlite3 db.sqlite "SELECT * FROM transactions WHERE period='2026-02'" > raw.csv
```

### Step 2: Data Processing

```python
# scripts/process_pl.py
import csv, json
from collections import defaultdict

def process_pl(input_csv, period):
    """Process P&L raw data into structured format."""
    categories = defaultdict(float)
    
    with open(input_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            categories[row['Category']] += float(row['Amount'] or 0)
    
    revenue = sum(v for k, v in categories.items() if 'Revenue' in k or 'Income' in k)
    cogs = sum(v for k, v in categories.items() if 'COGS' in k or 'Cost of' in k)
    gross_profit = revenue - cogs
    expenses = sum(v for k, v in categories.items() if k not in ['Revenue', 'COGS'])
    net_income = gross_profit - expenses
    
    return {
        'period': period,
        'revenue': revenue,
        'cogs': cogs,
        'gross_profit': gross_profit,
        'gross_margin': (gross_profit / revenue * 100) if revenue else 0,
        'expenses': expenses,
        'net_income': net_income,
        'net_margin': (net_income / revenue * 100) if revenue else 0,
        'categories': dict(categories)
    }
```

### Step 3: Chart Generation

```python
# scripts/generate_charts.py
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

def revenue_trend_chart(data_points, output_path):
    """Generate revenue trend line chart."""
    periods = [d['period'] for d in data_points]
    revenues = [d['revenue'] for d in data_points]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(periods, revenues, 'b-o', linewidth=2, markersize=8)
    ax.fill_between(periods, revenues, alpha=0.1)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_title('Revenue Trend', fontsize=14, fontweight='bold')
    ax.set_xlabel('Period')
    ax.set_ylabel('Revenue')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return output_path

def expense_breakdown_chart(categories, output_path):
    """Generate expense category pie chart."""
    expense_cats = {k: v for k, v in categories.items() 
                    if v > 0 and 'Revenue' not in k and 'Income' not in k}
    
    labels = list(expense_cats.keys())
    values = list(expense_cats.values())
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct='%1.1f%%',
        startangle=90, pctdistance=0.85
    )
    ax.set_title('Expense Breakdown', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return output_path

def variance_bar_chart(budget_vs_actual, output_path):
    """Generate budget vs actual variance chart."""
    categories = list(budget_vs_actual.keys())
    budgets = [budget_vs_actual[c]['budget'] for c in categories]
    actuals = [budget_vs_actual[c]['actual'] for c in categories]
    
    x = np.arange(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, budgets, width, label='Budget', color='steelblue')
    bars2 = ax.bar(x + width/2, actuals, width, label='Actual', color='coral')
    
    ax.set_title('Budget vs Actual', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return output_path
```

### Step 4: PDF Generation

```python
# scripts/generate_pdf.py
# Requires: pip install reportlab pillow

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime

def generate_pl_report(data, chart_paths, output_path, company_name="PrecisionLedger Client"):
    """Generate a complete P&L PDF report."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontSize=20, textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#666666'),
        spaceAfter=20, alignment=TA_CENTER
    )
    section_style = ParagraphStyle(
        'Section', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#1a1a2e'),
        spaceBefore=16, spaceAfter=8,
        borderPad=4
    )
    
    story = []
    
    # Header
    story.append(Paragraph(company_name, title_style))
    story.append(Paragraph(
        f"Profit & Loss Statement — {data['period']}", subtitle_style
    ))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y')}", 
        ParagraphStyle('gen_date', parent=styles['Normal'], 
                       fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 0.25*inch))
    
    # Key metrics summary table
    story.append(Paragraph("Executive Summary", section_style))
    
    summary_data = [
        ["Metric", "Amount", "Margin"],
        ["Total Revenue", f"${data['revenue']:,.2f}", "—"],
        ["Cost of Goods Sold", f"${data['cogs']:,.2f}", 
         f"{data['cogs']/data['revenue']*100:.1f}%" if data['revenue'] else "—"],
        ["Gross Profit", f"${data['gross_profit']:,.2f}", 
         f"{data['gross_margin']:.1f}%"],
        ["Total Expenses", f"${data['expenses']:,.2f}", 
         f"{data['expenses']/data['revenue']*100:.1f}%" if data['revenue'] else "—"],
        ["Net Income", f"${data['net_income']:,.2f}", 
         f"{data['net_margin']:.1f}%"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4fd')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (0, -1), 12),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Charts
    if 'revenue_trend' in chart_paths:
        story.append(Paragraph("Revenue Trend", section_style))
        story.append(Image(chart_paths['revenue_trend'], width=6.5*inch, height=3.25*inch))
        story.append(Spacer(1, 0.15*inch))
    
    if 'expense_breakdown' in chart_paths:
        story.append(Paragraph("Expense Breakdown", section_style))
        story.append(Image(chart_paths['expense_breakdown'], width=4*inch, height=4*inch))
    
    # Detailed category breakdown
    story.append(PageBreak())
    story.append(Paragraph("Detailed Breakdown", section_style))
    
    cat_data = [["Category", "Amount", "% of Revenue"]]
    for cat, amount in sorted(data['categories'].items(), key=lambda x: abs(x[1]), reverse=True):
        pct = f"{amount/data['revenue']*100:.1f}%" if data['revenue'] else "—"
        cat_data.append([cat, f"${amount:,.2f}", pct])
    
    cat_table = Table(cat_data, colWidths=[3.5*inch, 2*inch, 1.5*inch])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (0, -1), 12),
    ]))
    story.append(cat_table)
    
    doc.build(story)
    return output_path
```

### Step 5: Distribution

```python
# scripts/distribute_report.py

def distribute_via_email(report_path, recipients, subject, body):
    """Distribute report via email (use gog skill for Gmail)."""
    # Use: gog send --to recipient@email.com --subject "..." --attach report.pdf --body "..."
    # Or use himalaya skill for IMAP/SMTP
    # REQUIRES Irfan approval before sending to external clients
    pass

def distribute_via_telegram(report_path, chat_id):
    """Send report to Telegram channel."""
    # Use message tool: action=sendAttachment, target=chat_id, filePath=report_path
    pass
```

---

## Quick-Start Templates

### Monthly P&L Report (Full Pipeline)

```bash
# 1. Set up output dirs
mkdir -p reports/{raw,charts,output}

# 2. Extract data (QBO/Sheets/CSV)
# → reports/raw/2026-02-pl.csv

# 3. Process + generate
python scripts/process_pl.py reports/raw/2026-02-pl.csv "February 2026" > reports/raw/pl-data.json

# 4. Generate charts
python scripts/generate_charts.py reports/raw/pl-data.json reports/charts/

# 5. Generate PDF
python scripts/generate_pdf.py reports/raw/pl-data.json reports/charts/ reports/output/PL-Feb2026.pdf

# 6. Review (ALWAYS before distribution)
open reports/output/PL-Feb2026.pdf
```

### KPI Dashboard (Quick Summary)

```python
# scripts/kpi_dashboard.py
# Generates a one-page KPI card PDF

KPI_DEFINITIONS = {
    'Gross Margin': {'target': 0.65, 'format': 'percent'},
    'Net Margin': {'target': 0.20, 'format': 'percent'},
    'Revenue Growth MoM': {'target': 0.05, 'format': 'percent'},
    'AR Days Outstanding': {'target': 30, 'format': 'days', 'lower_is_better': True},
    'Cash Runway': {'target': 6, 'format': 'months'},
    'Billable Utilization': {'target': 0.80, 'format': 'percent'},
}
```

### Variance Report (Budget vs Actual)

```python
# Compare budget to actuals and flag variances > threshold
VARIANCE_THRESHOLD = 0.10  # 10% triggers flag

def flag_variances(budget_vs_actual, threshold=VARIANCE_THRESHOLD):
    flags = []
    for category, values in budget_vs_actual.items():
        if values['budget'] > 0:
            variance_pct = (values['actual'] - values['budget']) / values['budget']
            if abs(variance_pct) > threshold:
                direction = 'over' if variance_pct > 0 else 'under'
                flags.append({
                    'category': category,
                    'budget': values['budget'],
                    'actual': values['actual'],
                    'variance_pct': variance_pct,
                    'direction': direction,
                    'severity': 'HIGH' if abs(variance_pct) > 0.25 else 'MEDIUM'
                })
    return sorted(flags, key=lambda x: abs(x['variance_pct']), reverse=True)
```

---

## Report Naming Conventions

```
reports/
├── raw/           ← source data (CSV, JSON exports)
├── charts/        ← generated chart images (PNG)
├── output/        ← final PDFs
│   ├── PL-YYYY-MM-{ClientCode}.pdf
│   ├── BS-YYYY-MM-{ClientCode}.pdf
│   ├── CF-YYYY-MM-{ClientCode}.pdf
│   ├── KPI-YYYY-MM-{ClientCode}.pdf
│   └── BVA-YYYY-MM-{ClientCode}.pdf  ← Budget vs Actual
└── templates/     ← reusable layout templates
```

---

## Dependencies

```bash
# Python packages
pip install reportlab matplotlib pillow pandas numpy

# Verify
python -c "import reportlab, matplotlib, pandas; print('OK')"
```

---

## Safety & Compliance Rules

1. **Never distribute to external parties without Irfan's explicit approval**
2. **Always review PDF before sending** — no automated external distribution
3. **Client data stays in `reports/raw/` only** — never commit to git
4. **Watermark drafts** — add "DRAFT" overlay until final review
5. **Audit trail** — log every distribution: `reports/distribution-log.json`
6. **PII handling** — redact employee SSNs, salaries from any shared reports

---

## Integration Points

| System | How to Connect | Direction |
|--------|---------------|-----------|
| QuickBooks Online | QBO skill / CSV export | Read only |
| Google Sheets | `gog sheets` skill | Read / Write summary |
| Email (Gmail) | `gog mail` / himalaya skill | Send (with approval) |
| Telegram | `message` tool | Send PDF |
| File System | Direct path | Read/Write reports/ |

---

## When NOT to Use This Skill

- **Real-time BI dashboards** — Use Looker, Power BI, or Tableau instead
- **Regulatory/tax filings** — These require human sign-off and certified software
- **Live transaction streams** — This skill works on batch/period-end data
- **Ad hoc data questions** — Just run a direct financial analysis, don't generate a full report
- **Data entry or corrections** — This is output-only; never write back to source systems
