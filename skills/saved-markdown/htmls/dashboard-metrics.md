# Dashboard / Metrics — HTML Reference

## When to Use This Template

- User asks for an HTML dashboard, KPI overview, or metrics snapshot
- User explicitly requests HTML format for analytics or scorecard content
- User wants styled KPI cards, progress bars, and color-coded status indicators

---

## Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Dashboard Title}</title>
  <style>
    :root {
      --accent: #2563eb;
      --accent-light: #dbeafe;
      --success: #16a34a;
      --success-light: #dcfce7;
      --warning: #d97706;
      --warning-light: #fef3c7;
      --danger: #dc2626;
      --danger-light: #fee2e2;
      --text: #1e293b;
      --text-muted: #64748b;
      --bg: #ffffff;
      --bg-alt: #f8fafc;
      --border: #e2e8f0;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: var(--text);
      background: var(--bg-alt);
      line-height: 1.6;
    }

    .container {
      max-width: 960px;
      margin: 2rem auto;
      padding: 0 1rem;
    }

    header {
      background: var(--bg);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    header h1 { font-size: 1.6rem; margin-bottom: 0.25rem; }
    header .subtitle { color: var(--text-muted); font-size: 0.95rem; }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .kpi-card {
      background: var(--bg);
      border-radius: 10px;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      border-left: 4px solid var(--accent);
    }

    .kpi-card.success { border-left-color: var(--success); }
    .kpi-card.warning { border-left-color: var(--warning); }
    .kpi-card.danger { border-left-color: var(--danger); }

    .kpi-label { font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi-value { font-size: 2rem; font-weight: 700; margin: 0.25rem 0; }
    .kpi-delta { font-size: 0.85rem; }
    .kpi-delta.up { color: var(--success); }
    .kpi-delta.down { color: var(--danger); }

    .panel {
      background: var(--bg);
      border-radius: 10px;
      padding: 1.5rem 2rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .panel h2 { font-size: 1.15rem; margin-bottom: 1rem; }

    table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
    th { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }
    td { padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); }
    tr:nth-child(even) td { background: var(--bg-alt); }

    .status-dot {
      display: inline-block;
      width: 10px; height: 10px;
      border-radius: 50%;
      margin-right: 0.4rem;
      vertical-align: middle;
    }

    .status-dot.green { background: var(--success); }
    .status-dot.yellow { background: var(--warning); }
    .status-dot.red { background: var(--danger); }

    .progress-bar {
      background: var(--border);
      border-radius: 999px;
      height: 8px;
      overflow: hidden;
      margin-top: 0.3rem;
    }

    .progress-bar .fill {
      height: 100%;
      border-radius: 999px;
      background: var(--accent);
    }

    .progress-bar .fill.success { background: var(--success); }
    .progress-bar .fill.warning { background: var(--warning); }
    .progress-bar .fill.danger { background: var(--danger); }

    footer {
      text-align: center;
      padding: 1rem;
      font-size: 0.82rem;
      color: var(--text-muted);
    }

    @media (max-width: 640px) {
      .kpi-grid { grid-template-columns: 1fr 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>{Dashboard Title}</h1>
      <div class="subtitle">Period: {date range} · Generated: {date}</div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card success">
        <div class="kpi-label">{Metric Name}</div>
        <div class="kpi-value">{Value}</div>
        <div class="kpi-delta up">+{X}% vs last period</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">{Metric Name}</div>
        <div class="kpi-value">{Value}</div>
        <div class="kpi-delta down">-{X}% vs last period</div>
      </div>
      <!-- More KPI cards -->
    </div>

    <div class="panel">
      <h2>{Section Title}</h2>
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>{Column}</th>
            <th>{Column}</th>
            <th>Progress</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><span class="status-dot green"></span> Active</td>
            <td>{data}</td>
            <td>{data}</td>
            <td>
              <div class="progress-bar"><div class="fill success" style="width:85%"></div></div>
            </td>
          </tr>
          <!-- More rows -->
        </tbody>
      </table>
    </div>

    <footer>Dashboard generated on {date} · Data source: {source}</footer>
  </div>
</body>
</html>
```

---

## Styling Guidelines

- **KPI cards grid**: Use `auto-fit, minmax(200px, 1fr)` for responsive card layout — 4 across on desktop, stacks on mobile
- **Border-left color coding**: `.success`, `.warning`, `.danger` modifier classes on `.kpi-card` for at-a-glance status
- **Status dots**: Small colored circles (`<span class="status-dot green">`) next to row labels — scannable status
- **Progress bars**: Pure CSS `<div class="progress-bar"><div class="fill" style="width:75%">` — no JS needed
- **Alternating table rows**: `tr:nth-child(even) td { background: var(--bg-alt) }` for readability
- **Delta indicators**: `.kpi-delta.up` (green) and `.kpi-delta.down` (red) for trend direction

---

## CSS Alternatives to Charts

Since HTML mode has no chart widgets, use these CSS-only visual elements:

| Instead of... | Use... |
|--------------|--------|
| Pie chart (proportions) | Stacked horizontal bar or KPI cards with % |
| Line chart (trends) | Delta arrows in KPI cards ("+12% vs last month") |
| Bar chart (comparisons) | Progress bars with numeric labels |
| Scatter chart | Styled table with color-coded status dots |

---

## Professional Tips

1. **KPI cards first** — Lead with the 3-6 most important numbers. Make them large and scannable.
2. **Color means something** — Green = on track, yellow = attention, red = problem. Use consistently.
3. **Delta context always** — Never show a number alone. Add "vs last period", "vs target", or a percentage change.
4. **Progress bars for targets** — Show completion % visually. Color the fill green (>80%), yellow (50-80%), red (<50%).
5. **Limit to 4-6 KPI cards** — More than 6 dilutes focus. Group secondary metrics in tables below.
6. **Minimal text** — Dashboards are visual. Use short labels, not paragraphs.

---

## Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SaaS Metrics Dashboard — February 2026</title>
  <style>
    :root {
      --accent: #2563eb; --accent-light: #dbeafe;
      --success: #16a34a; --success-light: #dcfce7;
      --warning: #d97706; --warning-light: #fef3c7;
      --danger: #dc2626; --danger-light: #fee2e2;
      --text: #1e293b; --text-muted: #64748b;
      --bg: #ffffff; --bg-alt: #f8fafc; --border: #e2e8f0;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: var(--text); background: var(--bg-alt); line-height: 1.6; }
    .container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
    header { background: var(--bg); border-radius: 12px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    header h1 { font-size: 1.6rem; margin-bottom: 0.25rem; }
    header .subtitle { color: var(--text-muted); font-size: 0.95rem; }
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .kpi-card { background: var(--bg); border-radius: 10px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 4px solid var(--accent); }
    .kpi-card.success { border-left-color: var(--success); }
    .kpi-card.warning { border-left-color: var(--warning); }
    .kpi-card.danger { border-left-color: var(--danger); }
    .kpi-label { font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi-value { font-size: 2rem; font-weight: 700; margin: 0.25rem 0; }
    .kpi-delta { font-size: 0.85rem; }
    .kpi-delta.up { color: var(--success); }
    .kpi-delta.down { color: var(--danger); }
    .panel { background: var(--bg); border-radius: 10px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    .panel h2 { font-size: 1.15rem; margin-bottom: 1rem; }
    table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
    th { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }
    td { padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); }
    tr:nth-child(even) td { background: var(--bg-alt); }
    .status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 0.4rem; vertical-align: middle; }
    .status-dot.green { background: var(--success); }
    .status-dot.yellow { background: var(--warning); }
    .status-dot.red { background: var(--danger); }
    .progress-bar { background: var(--border); border-radius: 999px; height: 8px; overflow: hidden; margin-top: 0.3rem; }
    .progress-bar .fill { height: 100%; border-radius: 999px; background: var(--accent); }
    .progress-bar .fill.success { background: var(--success); }
    .progress-bar .fill.warning { background: var(--warning); }
    .progress-bar .fill.danger { background: var(--danger); }
    footer { text-align: center; padding: 1rem; font-size: 0.82rem; color: var(--text-muted); }
    @media (max-width: 640px) { .kpi-grid { grid-template-columns: 1fr 1fr; } }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>SaaS Metrics Dashboard</h1>
      <div class="subtitle">Period: February 2026 · Generated: 2026-03-01</div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card success">
        <div class="kpi-label">Monthly Active Users</div>
        <div class="kpi-value">15,200</div>
        <div class="kpi-delta up">+10.1% vs Jan</div>
      </div>
      <div class="kpi-card danger">
        <div class="kpi-label">Churn Rate</div>
        <div class="kpi-value">4.2%</div>
        <div class="kpi-delta down">+0.7pp vs Jan</div>
      </div>
      <div class="kpi-card warning">
        <div class="kpi-label">Revenue</div>
        <div class="kpi-value">$892K</div>
        <div class="kpi-delta up">+6.8% vs Jan</div>
      </div>
      <div class="kpi-card success">
        <div class="kpi-label">NPS Score</div>
        <div class="kpi-value">72</div>
        <div class="kpi-delta up">+4 vs Jan</div>
      </div>
    </div>

    <div class="panel">
      <h2>Revenue by Plan</h2>
      <table>
        <thead>
          <tr><th>Plan</th><th>Revenue</th><th>% of Total</th><th>Target Progress</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Pro</strong></td><td>$385K</td><td>43%</td>
            <td><div class="progress-bar"><div class="fill success" style="width:96%"></div></div></td>
          </tr>
          <tr>
            <td><strong>Enterprise</strong></td><td>$245K</td><td>28%</td>
            <td><div class="progress-bar"><div class="fill warning" style="width:70%"></div></div></td>
          </tr>
          <tr>
            <td><strong>Starter</strong></td><td>$180K</td><td>20%</td>
            <td><div class="progress-bar"><div class="fill success" style="width:90%"></div></div></td>
          </tr>
          <tr>
            <td><strong>Add-ons</strong></td><td>$82K</td><td>9%</td>
            <td><div class="progress-bar"><div class="fill success" style="width:82%"></div></div></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="panel">
      <h2>Feature Adoption</h2>
      <table>
        <thead>
          <tr><th>Status</th><th>Feature</th><th>Users</th><th>Adoption</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><span class="status-dot green"></span> Healthy</td>
            <td>Dashboard v2</td><td>12,400</td>
            <td><div class="progress-bar"><div class="fill success" style="width:82%"></div></div></td>
          </tr>
          <tr>
            <td><span class="status-dot yellow"></span> Growing</td>
            <td>API Integrations</td><td>6,800</td>
            <td><div class="progress-bar"><div class="fill warning" style="width:45%"></div></div></td>
          </tr>
          <tr>
            <td><span class="status-dot red"></span> Low</td>
            <td>Custom Reports</td><td>2,100</td>
            <td><div class="progress-bar"><div class="fill danger" style="width:14%"></div></div></td>
          </tr>
        </tbody>
      </table>
    </div>

    <footer>Dashboard generated on 2026-03-01 · Data source: Analytics DB</footer>
  </div>
</body>
</html>
```
