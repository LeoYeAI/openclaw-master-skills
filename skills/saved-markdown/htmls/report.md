# Report — HTML Reference

## When to Use This Template

- User asks for an HTML report, analysis, or summary
- User explicitly requests HTML format for findings, status updates, or reviews
- User wants styled callout boxes, priority badges, and accent-bordered sections

---

## Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Report Title}</title>
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
      line-height: 1.7;
    }

    .container {
      max-width: 820px;
      margin: 2rem auto;
      background: var(--bg);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    header {
      padding: 2.5rem;
      border-bottom: 3px solid var(--accent);
    }

    header h1 { font-size: 1.7rem; margin-bottom: 0.5rem; }

    .meta-row {
      display: flex;
      gap: 2rem;
      font-size: 0.88rem;
      color: var(--text-muted);
      flex-wrap: wrap;
    }

    .meta-row strong { color: var(--text); }

    main { padding: 2.5rem; }

    .callout {
      background: var(--accent-light);
      border-left: 4px solid var(--accent);
      border-radius: 0 8px 8px 0;
      padding: 1.25rem 1.5rem;
      margin-bottom: 2rem;
      font-size: 0.95rem;
    }

    .callout h2 {
      font-size: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--accent);
      margin-bottom: 0.5rem;
    }

    section { margin-bottom: 2.5rem; }

    h2 {
      font-size: 1.2rem;
      border-bottom: 2px solid var(--border);
      padding-bottom: 0.4rem;
      margin-bottom: 1rem;
    }

    h3 { font-size: 1.05rem; margin-bottom: 0.5rem; }

    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; margin: 1rem 0; }
    th { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }
    td { padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); }
    tr:nth-child(even) td { background: var(--bg-alt); }

    .badge {
      display: inline-block;
      padding: 0.15rem 0.6rem;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
    }

    .badge.high { background: var(--danger-light); color: var(--danger); }
    .badge.medium { background: var(--warning-light); color: var(--warning); }
    .badge.low { background: var(--success-light); color: var(--success); }

    .accent-box {
      border-left: 4px solid var(--accent);
      padding: 1rem 1.25rem;
      background: var(--bg-alt);
      border-radius: 0 8px 8px 0;
      margin: 1rem 0;
      font-size: 0.92rem;
    }

    .accent-box strong { display: block; margin-bottom: 0.25rem; }

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
      padding: 1.5rem 2.5rem;
      background: var(--bg-alt);
      font-size: 0.85rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
    }

    @media (max-width: 640px) {
      .meta-row { flex-direction: column; gap: 0.3rem; }
      header, main { padding: 1.5rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>{Report Title}</h1>
      <div class="meta-row">
        <div><strong>Date:</strong> {YYYY-MM-DD}</div>
        <div><strong>Prepared by:</strong> {Author}</div>
        <div><strong>Period:</strong> {Date range}</div>
      </div>
    </header>

    <main>
      <div class="callout">
        <h2>Executive Summary</h2>
        <p>{3-5 sentences covering: what was analyzed, what was found, what should happen next.}</p>
      </div>

      <section>
        <h2>Key Findings</h2>
        <table>
          <thead>
            <tr><th>#</th><th>Finding</th><th>Impact</th></tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>{Finding}</td>
              <td><span class="badge high">High</span> {Why}</td>
            </tr>
            <tr>
              <td>2</td>
              <td>{Finding}</td>
              <td><span class="badge medium">Medium</span> {Why}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section>
        <h2>{Data Section}</h2>
        <p>{Context for this data.}</p>
        <!-- Table or styled data here -->
        <div class="accent-box">
          <strong>Takeaway</strong>
          {One sentence: the "so what?" of this section.}
        </div>
      </section>

      <section>
        <h2>Recommendations</h2>
        <table>
          <thead>
            <tr><th>Priority</th><th>Action</th><th>Expected Impact</th><th>Owner</th></tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="badge high">High</span></td>
              <td>{Action}</td>
              <td>{Outcome}</td>
              <td>{Who}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>

    <footer>
      Generated on {date} · {Confidentiality note or source attribution}
    </footer>
  </div>
</body>
</html>
```

---

## Styling Guidelines

- **Accent border on header**: 3px bottom border in `var(--accent)` — brands the report
- **Callout box for Executive Summary**: Light background + left border makes it stand out from body text
- **Priority badges**: Pill-shaped `<span class="badge high/medium/low">` — replaces emoji indicators from markdown
- **Accent boxes for takeaways**: Left-bordered boxes after data sections — draws the eye to the insight
- **Alternating table rows**: `nth-child(even)` background — easier to scan data-heavy tables
- **Progress bars**: Use for completion metrics, target progress, or budget utilization

---

## CSS Alternatives to Charts

| Instead of... | Use... |
|--------------|--------|
| Line chart (trends) | Table with delta badges ("badge high" for increases, "badge low" for decreases) |
| Bar chart (comparisons) | Progress bars with numeric labels next to them |
| Pie chart (proportions) | Table with percentage column + stacked horizontal bar |
| Multi-series chart | Multiple accent-boxes with key numbers highlighted in bold |

---

## Professional Tips

1. **Executive Summary in a callout** — The callout box ensures it's visually distinct. Never skip this section.
2. **Badges for priority** — `high` (red), `medium` (yellow), `low` (green) — replaces emoji for cleaner look
3. **Takeaway after every data section** — Use `.accent-box` to answer "so what?" after tables/data
4. **One insight per section** — Don't mix unrelated metrics
5. **Meta row in header** — Date, author, and period are mandatory. Use the flex meta row.
6. **Footer for context** — Attribution, confidentiality, or data source info in the footer

---

## Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Monthly SaaS Metrics Report — February 2026</title>
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
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: var(--text); background: var(--bg-alt); line-height: 1.7; }
    .container { max-width: 820px; margin: 2rem auto; background: var(--bg); border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    header { padding: 2.5rem; border-bottom: 3px solid var(--accent); }
    header h1 { font-size: 1.7rem; margin-bottom: 0.5rem; }
    .meta-row { display: flex; gap: 2rem; font-size: 0.88rem; color: var(--text-muted); flex-wrap: wrap; }
    .meta-row strong { color: var(--text); }
    main { padding: 2.5rem; }
    .callout { background: var(--accent-light); border-left: 4px solid var(--accent); border-radius: 0 8px 8px 0; padding: 1.25rem 1.5rem; margin-bottom: 2rem; font-size: 0.95rem; }
    .callout h2 { font-size: 1rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--accent); margin-bottom: 0.5rem; }
    section { margin-bottom: 2.5rem; }
    h2 { font-size: 1.2rem; border-bottom: 2px solid var(--border); padding-bottom: 0.4rem; margin-bottom: 1rem; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; margin: 1rem 0; }
    th { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }
    td { padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); }
    tr:nth-child(even) td { background: var(--bg-alt); }
    .badge { display: inline-block; padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }
    .badge.high { background: var(--danger-light); color: var(--danger); }
    .badge.medium { background: var(--warning-light); color: var(--warning); }
    .badge.low { background: var(--success-light); color: var(--success); }
    .accent-box { border-left: 4px solid var(--accent); padding: 1rem 1.25rem; background: var(--bg-alt); border-radius: 0 8px 8px 0; margin: 1rem 0; font-size: 0.92rem; }
    .accent-box strong { display: block; margin-bottom: 0.25rem; }
    .progress-bar { background: var(--border); border-radius: 999px; height: 8px; overflow: hidden; margin-top: 0.3rem; }
    .progress-bar .fill { height: 100%; border-radius: 999px; }
    .progress-bar .fill.success { background: var(--success); }
    .progress-bar .fill.warning { background: var(--warning); }
    .progress-bar .fill.danger { background: var(--danger); }
    footer { padding: 1.5rem 2.5rem; background: var(--bg-alt); font-size: 0.85rem; color: var(--text-muted); border-top: 1px solid var(--border); }
    @media (max-width: 640px) { .meta-row { flex-direction: column; gap: 0.3rem; } header, main { padding: 1.5rem; } }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Monthly SaaS Metrics Report</h1>
      <div class="meta-row">
        <div><strong>Date:</strong> 2026-03-01</div>
        <div><strong>Prepared by:</strong> Analytics Team</div>
        <div><strong>Period:</strong> February 1–28, 2026</div>
      </div>
    </header>

    <main>
      <div class="callout">
        <h2>Executive Summary</h2>
        <p>February saw strong user growth with MAU reaching 15,200 (+10.1% MoM), exceeding our Q1 target by 8.6%. However, churn rate increased to 4.2% (from 3.5% in January), primarily driven by annual plan expirations. Revenue grew 6.8% to $892K but missed the $920K target. Immediate focus should be on retention campaigns for expiring annual customers.</p>
      </div>

      <section>
        <h2>Key Findings</h2>
        <table>
          <thead>
            <tr><th>#</th><th>Finding</th><th>Impact</th></tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>Churn spiked to 4.2% from annual plan expirations</td>
              <td><span class="badge high">High</span> $48K MRR at risk in March</td>
            </tr>
            <tr>
              <td>2</td>
              <td>MAU grew 10.1% MoM, beating target</td>
              <td><span class="badge low">Positive</span> Acquisition engine healthy</td>
            </tr>
            <tr>
              <td>3</td>
              <td>API usage up 45% but revenue flat</td>
              <td><span class="badge medium">Medium</span> Usage pricing not capturing value</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section>
        <h2>Revenue by Plan</h2>
        <table>
          <thead>
            <tr><th>Plan</th><th>Revenue</th><th>% Total</th><th>vs Target</th></tr>
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
        <div class="accent-box">
          <strong>Takeaway</strong>
          Pro plan remains the revenue engine at 43% of total. Enterprise is underperforming — only 3 new deals closed vs. 7 target. Prioritize enterprise sales pipeline.
        </div>
      </section>

      <section>
        <h2>Recommendations</h2>
        <table>
          <thead>
            <tr><th>Priority</th><th>Action</th><th>Expected Impact</th><th>Owner</th></tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="badge high">High</span></td>
              <td>Launch renewal campaign for 142 annual plans expiring in March</td>
              <td>Prevent $48K MRR churn</td>
              <td>Retention</td>
            </tr>
            <tr>
              <td><span class="badge high">High</span></td>
              <td>Revisit API pricing tiers — usage up 45% with flat revenue</td>
              <td>Capture $30-50K/mo in underpriced usage</td>
              <td>Product</td>
            </tr>
            <tr>
              <td><span class="badge medium">Medium</span></td>
              <td>A/B test enterprise landing page — conversion at 1.2% vs 2.5% benchmark</td>
              <td>+4 enterprise deals/month</td>
              <td>Marketing</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>

    <footer>
      Generated on 2026-03-01 · Internal use only — Analytics Team
    </footer>
  </div>
</body>
</html>
```
