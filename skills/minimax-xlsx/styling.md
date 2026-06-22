---
name: styling
description: "Visual styling reference for the minimax-xlsx skill. Contains theme palettes (grayscale/financial/verdant/dusk), conditional formatting recipes, and cover page layout specifications. Read this before writing openpyxl styling code."
---

<neutral_palette>
## Grayscale Theme (Standard Default)

### Color Discipline (Strictly Enforced)

**Foundation tones (only these three):**
- **White (#FEFEFE)** — backgrounds, data regions
- **Black (#1A1A1A)** — body text, primary headers
- **Grey (multiple shades)** — structural elements, borders, secondary labels

**Sole accent: Blue**
- For any emphasis, differentiation, or callout, use **blue** at varying intensity
- No green, red, orange, purple, or other hues (exception: region-specific financial indicators)

### Absolute Restrictions

- Avoid extra hue families (green/red/orange/purple/yellow/pink) unless a market-specific finance convention explicitly requires them
- No rainbow or multi-hue schemes
- No saturated/vibrant tones except blue accents
- No gradients crossing multiple color families

### Implementation Palette

```python
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

# Foundation tones
tone_bg = "FEFEFE"
tone_subtle = "F2F3F4"
tone_stripe = "F6F7F8"

tone_primary = "1A1A1A"
tone_header = "2C2C2C"
tone_text = "1A1A1A"
tone_rule = "CBCBCB"

# Blue accent spectrum
accent_deep = "1565C0"
accent_mid = "5B8DB8"
accent_wash = "E3EDF7"

ws.sheet_view.showGridLines = False

hdr_fill = PatternFill(start_color=tone_header, end_color=tone_header, fill_type="solid")
hdr_font = Font(color="FEFEFE", bold=True)
for cell in ws['B2:F2'][0]:
    cell.fill = hdr_fill
    cell.font = hdr_font
```
</neutral_palette>

<fiscal_palette>
## Financial Theme (Monetary/Fiscal Tasks Only)

Activate this palette when the task involves: equities, GDP, compensation, revenue, margins, budgeting, ROI, government finance, or similar fiscal domains.

### Regional Price-Movement Colors (non-negotiable)

In mainland China markets, rising prices are conventionally shown in **red** and falling prices in **green**. For all other markets this convention is reversed: **green** for gains, **red** for losses.

### Implementation Palette

```python
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

fin_bg = "E8EEF2"
fin_text = "1A1A1A"
fin_accent = "FFF8E1"
fin_header = "1B3A5C"
fin_loss = "E53935"

ws.sheet_view.showGridLines = False

fh_fill = PatternFill(start_color=fin_header, end_color=fin_header, fill_type="solid")
fh_font = Font(color="FEFEFE", bold=True)
fh_mark = PatternFill(start_color=fin_accent, end_color=fin_accent, fill_type="solid")
for cell in ws['B2:F2'][0]:
    cell.fill = fh_fill
    cell.font = fh_font
```

</fiscal_palette>

<verdant_palette>
## Verdant Theme (Ecology / Education / Humanities)

Activate this palette when the task involves: environmental analysis, education metrics, agriculture, healthcare, sustainability reporting, life sciences, or general research that benefits from a warm organic tone.

### Color Discipline

**Foundation tones:**
- **Mist white (#F0F5F1)** — backgrounds, data regions
- **Forest dark (#1A2E22)** — body text, primary headers
- **Sage grey (multiple shades)** — structural elements, borders, secondary labels

**Sole accent: Gold**
- For emphasis, differentiation, or callouts, use **warm gold** at varying intensity
- No blue, red, purple, or other hues

### Implementation Palette

```python
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

# Foundation tones
vrd_bg = "F0F5F1"
vrd_subtle = "E8F0EA"
vrd_stripe = "EDF2EE"

vrd_primary = "1A2E22"
vrd_header = "1B4332"
vrd_text = "1A2E22"
vrd_rule = "B5C7B9"

# Gold accent spectrum
vrd_accent_deep = "9E7C20"
vrd_accent_mid = "C9A84C"
vrd_accent_wash = "F5F0DC"

ws.sheet_view.showGridLines = False

vh_fill = PatternFill(start_color=vrd_header, end_color=vrd_header, fill_type="solid")
vh_font = Font(color="F0F5F1", bold=True)
vh_mark = PatternFill(start_color=vrd_accent_wash, end_color=vrd_accent_wash, fill_type="solid")
for cell in ws['B2:F2'][0]:
    cell.fill = vh_fill
    cell.font = vh_font
```
</verdant_palette>

<dusk_palette>
## Dusk Theme (Technology / Creative / Scientific)

Activate this palette when the task involves: technology metrics, product analytics, engineering reports, creative industry analysis, scientific data, or presentation-grade deliverables that need a modern aesthetic.

### Color Discipline

**Foundation tones:**
- **Soft lavender (#F7F3FA)** — backgrounds, data regions
- **Dark grape (#221429)** — body text, primary headers
- **Iris grey (multiple shades)** — structural elements, borders, secondary labels

**Sole accent: Copper**
- For emphasis, differentiation, or callouts, use **warm copper** at varying intensity
- No blue, green, or other hues

### Implementation Palette

```python
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

# Foundation tones
dsk_bg = "F7F3FA"
dsk_subtle = "F0ECF5"
dsk_stripe = "F3F0F7"

dsk_primary = "221429"
dsk_header = "3C1742"
dsk_text = "221429"
dsk_rule = "C4B8CE"

# Copper accent spectrum
dsk_accent_deep = "A0522D"
dsk_accent_mid = "C4724A"
dsk_accent_wash = "FAF0EB"

ws.sheet_view.showGridLines = False

dh_fill = PatternFill(start_color=dsk_header, end_color=dsk_header, fill_type="solid")
dh_font = Font(color="F7F3FA", bold=True)
dh_mark = PatternFill(start_color=dsk_accent_wash, end_color=dsk_accent_wash, fill_type="solid")
for cell in ws['B2:F2'][0]:
    cell.fill = dh_fill
    cell.font = dh_font
```
</dusk_palette>

<conditional_rules>

## Conditional Formatting — Apply Proactively

Apply conditional formatting deliberately to improve scanability and analytical readability.

| Content Type | Technique | Sample Code |
|---|---|---|
| Raw numbers | **Data Bars** | `DataBarRule(start_type='min', end_type='max', color='5B8DB8', showValue=True)` |
| Spread/range | **Color Scales** | `ColorScaleRule(start_type='min', start_color='FEFEFE', end_type='max', end_color='5B8DB8')` |
| Status indicators | **Icon Sets** | `IconSetRule(icon_style='3Arrows', type='percent', values=[0,25,75])` |
| Boundary triggers | **Cell Highlights** | `CellIsRule(operator='greaterThan', formula=['50000'], fill=accent_fill)` |
| Top performers | **Rank-based** | `FormulaRule(formula=['RANK(A2,$A$2:$A$100)<=10'], fill=gold_fill)` |

**Available icon styles**: `3Arrows` (directional), `3TrafficLights1` (circle indicators), `3Symbols` (check/dash/cross), `5Rating` (star)

**Theme-specific palettes:**
- Grayscale: Data bars `5B8DB8`, Scale `F2F3F4->ABABAB->2C2C2C`
- Financial: Positive `81C784`, Negative `E57373`, Neutral `FFD54F`
- Verdant: Data bars `C9A84C`, Scale `F0F5F1->8BAF7E->1B4332`
- Dusk: Data bars `C4724A`, Scale `F7F3FA->9E7CAD->3C1742`

```python
from openpyxl.formatting.rule import DataBarRule, ColorScaleRule, IconSetRule, CellIsRule

# Horizontal bars
ws.conditional_formatting.add('D3:D200', DataBarRule(start_type='min', end_type='max', color='5B8DB8', showValue=True))

# Tri-color gradient
ws.conditional_formatting.add('E3:E200', ColorScaleRule(start_type='min', start_color='E57373', mid_type='percentile', mid_value=50, mid_color='FFD54F', end_type='max', end_color='81C784'))

# Directional arrows
ws.conditional_formatting.add('F3:F200', IconSetRule(icon_style='3Arrows', type='percent', values=[0, 25, 75], showValue=True))
```

**Usage tips**: Apply to 2-4 key columns per sheet; maintain consistent color semantics; layer Data Bars + Icons for maximum impact.

</conditional_rules>

<cover_layout>

**A cover sheet is mandatory as the very first worksheet in every deliverable.**

## Layout Specification

| Rows | Purpose | Formatting |
|------|---------|------------|
| 3-4 | **Document title** | 18-20pt, bold, center-aligned |
| 6 | Tagline or scope description | 12pt, grey text |
| 8-16 | **Headline metrics** | Tabular layout with key figures highlighted |
| 18-21 | **Worksheet directory** | Sheet names mapped to brief descriptions |
| 23+ | Disclaimers, usage notes | Small font, grey |

## Required Elements

**1. Document title** — clear, descriptive name for the workbook

**2. Headline metrics** — 3-6 most significant numbers or findings

**3. Worksheet directory** — navigation aid:
```
| Sheet Name | Description |
|------------|-------------|
| Raw Data | Original dataset (100 rows) |
| Analysis | Sales breakdown by region |
| Pivot Summary | Interactive pivot analysis |
```

**4. PivotTable notice** (required when the workbook includes PivotTables):
```
After opening, update the PivotTable cache:
  * On Windows: select any cell inside the PivotTable, press Alt+F5
  * On macOS: go to the PivotTable Analyze ribbon, click Refresh All
  * Shortcut for both platforms: Ctrl+Alt+F5
```

## Cover Page Visual Standards

- **Background**: White or light grey (#F2F3F4)
- **Title row height**: 30-40pt for prominence
- **No gridlines**: Suppress gridlines on cover for a clean presentation
- **Column span**: Merge cells A-G for the title block
- **Color scheme**: Match the workbook's chosen theme (grayscale or financial)

## Gridline Note
Always keep the cover sheet gridlines hidden

</cover_layout>
