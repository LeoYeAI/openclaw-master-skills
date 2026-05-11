# Data Story — Style Reference

Clear, precise, and persuasive. Numbers are the hero. Inspired by Figma Annual Report, Stripe Annual Report, and Bloomberg Businessweek data visualizations. Zero external chart libraries — pure CSS + SVG only.

---

## Colors

```css
/* Dark variant (default) */
:root {
    --bg:              #0f1117;
    --bg-card:         #1a1f2e;
    --border:          #2d3748;
    --text:            #e2e8f0;
    --text-muted:      #64748b;
    --positive:        #00d4aa;   /* up / good */
    --negative:        #ff6b6b;   /* down / bad */
    --neutral:         #e2e8f0;
    --chart-primary:   #3b82f6;
    --chart-secondary: #8b5cf6;
    --chart-tertiary:  #10b981;
    --grid-line:       #1e293b;
    --axis-line:       #334155;
}

/* Light variant */
:root.ds-light {
    --bg:           #f8f9fc;
    --bg-card:      #ffffff;
    --border:       #e2e8f0;
    --text:         #0f172a;
    --text-muted:   #64748b;
    --grid-line:    #e2e8f0;
    --axis-line:    #cbd5e1;
}
```

---

## Typography

```css
body {
    font-family: "Inter", "Noto Sans SC", "PingFang SC", system-ui, sans-serif;
    font-variant-numeric: tabular-nums;   /* CRITICAL: all numbers align */
    -webkit-font-smoothing: antialiased;
}

/* KPI hero number */
.ds-kpi {
    font-size: clamp(3rem, 8vw, 6rem);
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    letter-spacing: -0.02em;
}
.ds-kpi.positive { color: var(--positive); }
.ds-kpi.negative { color: var(--negative); }
.ds-kpi.neutral  { color: var(--neutral); }

/* KPI label */
.ds-kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    margin-top: 8px;
}

/* Trend comparison */
.ds-trend {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    font-weight: 600;
    margin-top: 6px;
}
.ds-trend.up   { color: var(--positive); }
.ds-trend.down { color: var(--negative); }
/* Use ▲ ▼ characters */
```

---

## KPI Card Components

```css
/* Single KPI card */
.ds-kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: clamp(1rem, 2vw, 1.5rem);
    display: flex;
    flex-direction: column;
}

/* KPI grid */
.ds-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%,160px),1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}
```

---

## Layout Templates

### 1. Hero Number (full-screen single KPI)

```css
.ds-hero-slide {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: clamp(0.5rem, 1.5vw, 1rem);
    padding: clamp(2rem, 5vw, 5rem);
}
/* The KPI number occupies center stage */
/* Supporting context below in small text */
```

### 2. KPI Row + Chart (two columns)

```css
.ds-split-layout {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: clamp(1rem, 3vw, 2.5rem);
    height: 100%;
    align-items: center;
    padding: clamp(2rem, 4vw, 4rem);
}
/* Left: stack of KPI cards */
/* Right: SVG line or bar chart */
```

### 3. Full-screen Bar Chart + Insight

```css
.ds-chart-layout {
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: 1rem;
    padding: clamp(1.5rem, 3vw, 3rem);
    height: 100%;
}
/* Row 1: slide title */
/* Row 2: SVG bar chart */
/* Row 3: insight pullquote */
```

### 4. 2×2 Comparison Matrix

```css
.ds-matrix {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: clamp(0.5rem, 1.5vw, 1rem);
    flex: 1;
}
.ds-matrix-cell {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
    display: flex; flex-direction: column; justify-content: center;
}
/* Label each axis externally (row/column headers) */
```

---

## SVG Chart Styles (zero library, pure SVG)

```css
/* Axis lines */
.ds-axis { stroke: var(--axis-line); stroke-width: 1; fill: none; }

/* Grid lines */
.ds-grid { stroke: var(--grid-line); stroke-width: 1; stroke-dasharray: 4 4; fill: none; }

/* Bar chart */
.ds-bar {
    fill: var(--chart-primary);
    rx: 4px;   /* rounded top corners */
}
.ds-bar.secondary { fill: var(--chart-secondary); }

/* Line chart */
.ds-line { stroke: var(--chart-primary); stroke-width: 2.5; fill: none; stroke-linecap: round; }

/* Area fill (under line) */
.ds-area { fill: var(--chart-primary); opacity: 0.10; }

/* Data point dot */
.ds-dot { fill: var(--chart-primary); r: 4; }
```

### Minimal SVG Bar Chart Example

```html
<svg viewBox="0 0 400 160" class="ds-chart-svg">
  <!-- Grid lines -->
  <line x1="40" y1="0" x2="40" y2="140" class="ds-axis"/>
  <line x1="40" y1="140" x2="400" y2="140" class="ds-axis"/>
  <line x1="40" y1="30" x2="400" y2="30" class="ds-grid"/>
  <line x1="40" y1="70" x2="400" y2="70" class="ds-grid"/>
  <line x1="40" y1="110" x2="400" y2="110" class="ds-grid"/>
  <!-- Bars (heights represent values) -->
  <rect x="60"  y="60" width="40" height="80" rx="4" class="ds-bar"/>
  <rect x="120" y="40" width="40" height="100" rx="4" class="ds-bar"/>
  <rect x="180" y="20" width="40" height="120" rx="4" class="ds-bar"/>
  <rect x="240" y="50" width="40" height="90" rx="4" class="ds-bar"/>
  <rect x="300" y="10" width="40" height="130" rx="4" class="ds-bar"/>
  <!-- Labels -->
  <text x="80"  y="158" text-anchor="middle" class="ds-axis-label">Q1</text>
  <text x="140" y="158" text-anchor="middle" class="ds-axis-label">Q2</text>
  <text x="200" y="158" text-anchor="middle" class="ds-axis-label">Q3</text>
  <text x="260" y="158" text-anchor="middle" class="ds-axis-label">Q4</text>
  <text x="320" y="158" text-anchor="middle" class="ds-axis-label">Q5</text>
</svg>
```

```css
.ds-chart-svg { width: 100%; height: auto; }
.ds-axis-label {
    font-family: inherit;
    font-size: 10px;
    fill: var(--text-muted);
    font-variant-numeric: tabular-nums;
}
```

---

## Insight Pullquote

```css
.ds-insight {
    border-left: 3px solid var(--chart-primary);
    padding: 0.75rem 1rem;
    background: rgba(59,130,246,0.08);
    border-radius: 0 6px 6px 0;
    font-size: clamp(0.8rem, 1.3vw, 1rem);
    line-height: 1.5;
    color: var(--text);
}
.ds-insight strong { color: var(--chart-primary); }
```

---

## Animation

```css
/* Numbers animate via CSS counter-like approach */
/* Use JS for counting-up effect if desired: */
/* element.textContent changes from 0 to value over 1s */

.reveal {
    opacity: 0;
    transform: translateY(12px);
    transition: opacity 0.5s ease, transform 0.5s ease;
}
.slide.visible .reveal { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] At least one KPI number at 48px+ visible
- [ ] An SVG chart element (bars or line) present
- [ ] `font-variant-numeric: tabular-nums` applied
- [ ] Positive/negative color coding shown (green up, red down)
- [ ] `--grid-line` dashed grid lines visible in chart area

---

## Best For

Quarterly business reviews · Growth reporting · Analyst briefings · Data product demos · KPI dashboards presented as slides · Any talk where the numbers tell the story
