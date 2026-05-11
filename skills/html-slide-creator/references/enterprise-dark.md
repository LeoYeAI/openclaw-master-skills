# Enterprise Dark — Style Reference

Authoritative, precise, and data-ready. Inspired by McKinsey dark decks and Bloomberg Terminal visual language. Every element earns its place.

---

## Colors

```css
:root {
    --bg-primary:   #0d1117;
    --bg-secondary: #161b22;
    --bg-header:    #21262d;
    --border:       #30363d;
    --text-primary: #e6edf3;
    --text-body:    #c9d1d9;
    --text-muted:   #8b949e;
    --accent-blue:  #388bfd;
    --accent-green: #3fb950;   /* positive / up */
    --accent-red:   #f85149;   /* negative / down */
    --accent-amber: #d29922;   /* warning / neutral */
}
```

---

## Background Grid

```css
body {
    background: #0d1117;
}
/* Subtle density grid — adds visual weight without distraction */
body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(48,54,61,0.5) 1px, transparent 1px),
        linear-gradient(90deg, rgba(48,54,61,0.5) 1px, transparent 1px);
    background-size: 24px 24px;
    opacity: 0.03;
    pointer-events: none;
    z-index: 0;
}
```

---

## Typography

```css
/* All text — system fonts, tabular nums for all numeric content */
body {
    font-family: "PingFang SC", "Noto Sans CJK SC", "Segoe UI",
                 -apple-system, system-ui, sans-serif;
    font-feature-settings: "tnum"; /* tabular numbers throughout */
    -webkit-font-smoothing: antialiased;
}

/* Section label */
.ent-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8b949e;
}

/* Slide title */
.ent-title {
    font-size: clamp(1.4rem, 3vw, 2.2rem);
    font-weight: 600;
    color: #e6edf3;
    line-height: 1.2;
}

/* KPI number */
.ent-kpi-number {
    font-size: clamp(2.5rem, 6vw, 5rem);
    font-weight: 800;
    font-feature-settings: "tnum";
    line-height: 1;
}
.ent-kpi-number.positive { color: #3fb950; }
.ent-kpi-number.negative { color: #f85149; }
.ent-kpi-number.neutral  { color: #e6edf3; }

/* KPI label */
.ent-kpi-label {
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8b949e;
    margin-top: 6px;
}
```

---

## KPI Card Component

```css
.ent-kpi-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: clamp(1rem, 2vw, 1.5rem);
    display: flex;
    flex-direction: column;
    gap: 4px;
}

/* KPI grid — 2 or 3 columns */
.ent-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

/* Trend arrow */
.ent-trend {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    font-weight: 600;
}
.ent-trend.up   { color: #3fb950; }
.ent-trend.down { color: #f85149; }
/* Arrow: use ▲ / ▼ characters or inline SVG */
```

---

## Progress Bar

```css
.ent-progress-track {
    height: 2px;
    background: #30363d;
    border-radius: 9999px;
    overflow: hidden;
}
.ent-progress-fill {
    height: 100%;
    background: #388bfd;
    border-radius: 9999px;
    transition: width 0.8s cubic-bezier(0.16,1,0.3,1);
}
```

---

## Table Component

```css
.ent-table {
    width: 100%;
    border-collapse: collapse;
    font-size: clamp(0.75rem, 1.2vw, 0.9rem);
}
.ent-table thead th {
    background: #21262d;
    color: #8b949e;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid #30363d;
}
.ent-table tbody td {
    padding: 10px 12px;
    color: #c9d1d9;
    border-bottom: 1px solid #30363d;
}
.ent-table tbody tr:last-child td { border-bottom: none; }
.ent-table tbody tr:hover td { background: rgba(48,54,61,0.5); }
```

---

## Layout — Consulting Split

```css
/* Left: narrow title/label column. Right: main content */
.ent-split {
    display: grid;
    grid-template-columns: clamp(160px, 22%, 240px) 1fr;
    gap: clamp(1.5rem, 3vw, 3rem);
    height: 100%;
    align-items: start;
    padding-top: clamp(2rem, 4vw, 4rem);
}
.ent-split-label {
    padding-top: 4px;
    border-right: 1px solid #30363d;
    padding-right: 1.5rem;
}
```

---

## Animation

```css
/* Minimal: 300ms fade only. No movement. */
.reveal {
    opacity: 0;
    transition: opacity 0.3s ease;
}
.slide.visible .reveal { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.12s; }
.reveal:nth-child(3) { transition-delay: 0.19s; }
.reveal:nth-child(4) { transition-delay: 0.26s; }
```

---

## Style Preview Checklist

- [ ] Dark `#0d1117` background with faint grid
- [ ] At least one KPI number (48px+) in green or blue
- [ ] `1px #30363d` border on all panels
- [ ] Consulting-style left label column visible

---

## Best For

Quarterly business reviews · Strategy presentations · Investor updates · B2B sales decks · Management consulting · Board materials
