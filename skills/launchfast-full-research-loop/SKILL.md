---
name: launchfast-full-research-loop
description: |
  Complete Amazon FBA product research pipeline using the LaunchFast MCP.
  Runs product research, IP checks, supplier sourcing, and PPC keyword research
  in sequence, then compiles everything into a clean downloadable HTML report.

  USE THIS SKILL FOR:
  - "full research on [keyword]"
  - "research everything about [product]"
  - "give me a complete FBA opportunity report"
  - "run the full loop on [keyword]"

  Requirements:
  - mcp__launchfast__research_products
  - mcp__launchfast__ip_check_manage
  - mcp__launchfast__supplier_research
  - mcp__launchfast__amazon_keyword_research

argument-hint: [product keyword]
---

# LaunchFast Full Research Loop

You are a senior Amazon FBA analyst. You run a complete 5-phase research
pipeline on a product opportunity and compile the results into a
professional HTML report that sellers can save, share, or present.

**Requirements before starting:**
- All four LaunchFast MCP tools available (see above)

---

## STEP 1 — Gather inputs

Ask in one shot if not provided:

```
To run the full research loop, I need:

1. Product keyword(s) to research (e.g. "silicone spatula")
2. Target selling price? (e.g. $24.99)
3. Target first-order quantity for sourcing? (e.g. 500 units)
4. Any competitor ASINs you already know? (optional — for PPC phase)
5. Where to save the report? (default: ~/Downloads/launchfast-report-[keyword]-[date].html)
```

---

## ═══════════════════════════════════════
## PHASE 1 — PRODUCT RESEARCH
## ═══════════════════════════════════════

Run for each keyword provided:
```
mcp__launchfast__research_products(keyword: "[keyword]")
```

**Extract for report:**
- Total products analyzed
- Grade distribution (count per grade tier)
- Revenue range (min/max/median)
- Price range
- Review range
- Top 5 products (grade, revenue, price, reviews)
- Opportunity score (calculate per skill: launchfast-product-research formula)
- Verdict: GO / INVESTIGATE / PASS

Tell user: `✓ Phase 1 complete — [N] products analyzed across [N] keywords`

---

## ═══════════════════════════════════════
## PHASE 2 — IP CHECK
## ═══════════════════════════════════════

For each winning keyword from Phase 1 (score ≥ 40):

```
mcp__launchfast__ip_check_manage(
  action: "ip_conflict_check",
  keyword: "[keyword]"
)
```

Also run targeted trademark search:
```
mcp__launchfast__ip_check_manage(
  action: "trademark_search",
  keyword: "[keyword]",
  statusFilter: "active"
)
```

**Extract for report:**
- Conflict level: LOW / MEDIUM / HIGH
- Active trademarks found (name, owner, status)
- Any patent hits (flag if found)
- Risk assessment: CLEAR / CAUTION / BLOCKED

Tell user: `✓ Phase 2 complete — IP risk: [level]`

---

## ═══════════════════════════════════════
## PHASE 3 — SUPPLIER RESEARCH
## ═══════════════════════════════════════

For the top keyword (highest opportunity score):

```
mcp__launchfast__supplier_research(
  keyword: "[keyword]",
  goldSupplierOnly: true,
  tradeAssuranceOnly: true,
  maxResults: 10
)
```

**Extract top 5 suppliers for report:**
- Company name
- Quality score
- Price range
- MOQ
- Years in business
- Verifications (Gold, Trade Assurance, Assessed, etc.)

Tell user: `✓ Phase 3 complete — [N] suppliers found`

---

## ═══════════════════════════════════════
## PHASE 4 — PPC KEYWORD RESEARCH
## ═══════════════════════════════════════

If competitor ASINs were provided OR if Phase 1 returned any ASINs:

```
mcp__launchfast__amazon_keyword_research(asins: ["B0...", ...])
```

**Extract for report:**
- Total unique keywords found
- Top 20 keywords by search volume
- Top 5 exact-match opportunities (high volume, lower competition)
- Estimated CPCs where available
- Recommended campaign structure

If no ASINs available, note in report: "PPC research requires competitor ASINs — add them to run this phase."

Tell user: `✓ Phase 4 complete — [N] keywords extracted`

---

## ═══════════════════════════════════════
## PHASE 5 — GENERATE HTML REPORT
## ═══════════════════════════════════════

Generate a complete standalone HTML file. Save to the path specified in Step 1.

### Report design system

Match LaunchFast's design exactly:
- Font: `-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif`
- Text: `#1a1a1a` | Muted: `#666666` | Very muted: `#999999`
- Background: `#fafafa` | Card: `#ffffff`
- Border: `1px solid #e5e5e5` | Border radius: `8px`
- Accent: `border-left: 3px solid #1a1a1a` for callout blocks
- Bullet: 6px circle `background: #1a1a1a; border-radius: 50%`
- Go badge: `background: #dcfce7; color: #166534`
- Investigate badge: `background: #fef9c3; color: #854d0e`
- Pass badge: `background: #fee2e2; color: #991b1b`
- IP LOW badge: `background: #dcfce7; color: #166534`
- IP MEDIUM badge: `background: #fef9c3; color: #854d0e`
- IP HIGH badge: `background: #fee2e2; color: #991b1b`

### HTML report template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>LaunchFast Research Report — [Keyword] — [Date]</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
      background: #fafafa;
      color: #1a1a1a;
      line-height: 1.5;
      padding: 40px 20px;
    }
    .page { max-width: 960px; margin: 0 auto; }

    /* Header */
    .report-header { margin-bottom: 40px; }
    .report-header .brand { font-size: 13px; font-weight: 600; color: #999; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 12px; }
    .report-header h1 { font-size: 32px; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 8px; }
    .report-header .meta { font-size: 14px; color: #666; }

    /* Verdict banner */
    .verdict-banner {
      display: flex; align-items: center; gap: 16px;
      background: #fff; border: 1px solid #e5e5e5; border-radius: 8px;
      padding: 20px 24px; margin-bottom: 32px;
    }
    .verdict-banner .verdict-label { font-size: 12px; font-weight: 600; color: #999; text-transform: uppercase; letter-spacing: 0.06em; }
    .verdict-banner .verdict-value { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; }
    .verdict-banner .divider { width: 1px; height: 40px; background: #e5e5e5; }
    .verdict-banner .stat { }
    .verdict-banner .stat-label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.05em; }
    .verdict-banner .stat-value { font-size: 18px; font-weight: 600; letter-spacing: -0.01em; }

    /* Section */
    .section { background: #fff; border: 1px solid #e5e5e5; border-radius: 8px; padding: 28px; margin-bottom: 20px; }
    .section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #e5e5e5; }
    .section-title { font-size: 16px; font-weight: 600; letter-spacing: -0.01em; }
    .phase-label { font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; letter-spacing: 0.08em; }

    /* Tables */
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th { text-align: left; font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; letter-spacing: 0.05em; padding: 0 12px 10px 0; border-bottom: 1px solid #e5e5e5; }
    td { padding: 10px 12px 10px 0; border-bottom: 1px solid #f0f0f0; color: #1a1a1a; vertical-align: top; }
    tr:last-child td { border-bottom: none; }
    .grade { font-weight: 700; font-size: 15px; }
    .grade-a { color: #166534; }
    .grade-b { color: #1d4ed8; }
    .grade-c { color: #92400e; }
    .grade-d, .grade-f { color: #991b1b; }

    /* Badges */
    .badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.03em; }
    .badge-go { background: #dcfce7; color: #166534; }
    .badge-investigate { background: #fef9c3; color: #854d0e; }
    .badge-pass { background: #fee2e2; color: #991b1b; }
    .badge-low { background: #dcfce7; color: #166534; }
    .badge-medium { background: #fef9c3; color: #854d0e; }
    .badge-high { background: #fee2e2; color: #991b1b; }
    .badge-clear { background: #dcfce7; color: #166534; }
    .badge-caution { background: #fef9c3; color: #854d0e; }
    .badge-blocked { background: #fee2e2; color: #991b1b; }

    /* Callout */
    .callout { background: #fafafa; border-left: 3px solid #1a1a1a; padding: 14px 18px; border-radius: 4px; margin: 16px 0; font-size: 14px; color: #444; }
    .callout strong { color: #1a1a1a; }

    /* Stats grid */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 20px; }
    .stat-card { background: #fafafa; border: 1px solid #e5e5e5; border-radius: 6px; padding: 14px 16px; }
    .stat-card .label { font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .value { font-size: 20px; font-weight: 700; letter-spacing: -0.02em; }
    .stat-card .sub { font-size: 12px; color: #666; margin-top: 2px; }

    /* Supplier score bar */
    .score-bar { display: flex; align-items: center; gap: 8px; }
    .score-bar .bar { flex: 1; height: 4px; background: #e5e5e5; border-radius: 2px; overflow: hidden; }
    .score-bar .fill { height: 100%; background: #1a1a1a; border-radius: 2px; }
    .score-bar .num { font-size: 12px; font-weight: 600; color: #1a1a1a; min-width: 28px; text-align: right; }

    /* Footer */
    .report-footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e5e5; display: flex; justify-content: space-between; align-items: center; }
    .report-footer .brand-mark { font-size: 13px; font-weight: 600; color: #1a1a1a; }
    .report-footer .generated { font-size: 12px; color: #999; }
  </style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div class="report-header">
    <div class="brand">LaunchFast · FBA Research Report</div>
    <h1>[Keyword] Opportunity Report</h1>
    <div class="meta">Generated [Full Date] · [N] keywords · [N] products analyzed</div>
  </div>

  <!-- VERDICT BANNER -->
  <div class="verdict-banner">
    <div class="stat">
      <div class="verdict-label">Overall Verdict</div>
      <div class="verdict-value"><span class="badge badge-[go/investigate/pass]">[GO / INVESTIGATE / PASS]</span></div>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <div class="stat-label">Opp Score</div>
      <div class="stat-value">[N]/100</div>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <div class="stat-label">IP Risk</div>
      <div class="stat-value"><span class="badge badge-[low/medium/high]">[LOW/MEDIUM/HIGH]</span></div>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <div class="stat-label">Suppliers Found</div>
      <div class="stat-value">[N]</div>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <div class="stat-label">PPC Keywords</div>
      <div class="stat-value">[N]</div>
    </div>
  </div>

  <!-- PHASE 1: PRODUCT RESEARCH -->
  <div class="section">
    <div class="section-header">
      <div class="section-title">Product Research</div>
      <div class="phase-label">Phase 1</div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="label">Products Analyzed</div>
        <div class="value">[N]</div>
      </div>
      <div class="stat-card">
        <div class="label">Top Revenue</div>
        <div class="value">$[X]k<span style="font-size:14px;font-weight:500">/mo</span></div>
      </div>
      <div class="stat-card">
        <div class="label">Price Range</div>
        <div class="value">$[X]–$[X]</div>
      </div>
      <div class="stat-card">
        <div class="label">Avg Reviews</div>
        <div class="value">[N]</div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Product</th>
          <th>Grade</th>
          <th>Revenue/mo</th>
          <th>Price</th>
          <th>Reviews</th>
          <th>BSR</th>
        </tr>
      </thead>
      <tbody>
        <!-- Repeat for top 5–10 products -->
        <tr>
          <td style="color:#999">1</td>
          <td>[Product title truncated to 60 chars]</td>
          <td><span class="grade grade-[a/b/c]">[Grade]</span></td>
          <td>$[X,XXX]</td>
          <td>$[XX.XX]</td>
          <td>[X,XXX]</td>
          <td>#[X,XXX]</td>
        </tr>
      </tbody>
    </table>

    <div class="callout" style="margin-top:20px">
      <strong>Key finding:</strong> [1-2 sentence insight about the market — grade distribution, revenue consistency, competitive dynamics]
    </div>
  </div>

  <!-- PHASE 2: IP CHECK -->
  <div class="section">
    <div class="section-header">
      <div class="section-title">IP & Trademark Check</div>
      <div class="phase-label">Phase 2</div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="label">IP Risk Level</div>
        <div class="value"><span class="badge badge-[low/medium/high]">[LOW/MEDIUM/HIGH]</span></div>
      </div>
      <div class="stat-card">
        <div class="label">Active Trademarks</div>
        <div class="value">[N]</div>
      </div>
      <div class="stat-card">
        <div class="label">Patent Hits</div>
        <div class="value">[N]</div>
      </div>
      <div class="stat-card">
        <div class="label">Assessment</div>
        <div class="value"><span class="badge badge-[clear/caution/blocked]">[CLEAR/CAUTION/BLOCKED]</span></div>
      </div>
    </div>

    <!-- If trademarks found, show table -->
    <table>
      <thead>
        <tr><th>Trademark</th><th>Owner</th><th>Status</th><th>Class</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>[Trademark name]</td>
          <td>[Owner]</td>
          <td>[Live/Dead]</td>
          <td>[Class number]</td>
        </tr>
      </tbody>
    </table>

    <div class="callout" style="margin-top:20px">
      <strong>Recommendation:</strong> [Clear action — e.g. "No direct conflicts found. Avoid branding your product as [word] to stay safe." or "HIGH risk — consult an IP attorney before proceeding."]
    </div>
  </div>

  <!-- PHASE 3: SUPPLIER RESEARCH -->
  <div class="section">
    <div class="section-header">
      <div class="section-title">Alibaba Supplier Research</div>
      <div class="phase-label">Phase 3</div>
    </div>

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Supplier</th>
          <th>Score</th>
          <th>Price Range</th>
          <th>MOQ</th>
          <th>Years</th>
          <th>Verified</th>
        </tr>
      </thead>
      <tbody>
        <!-- Repeat for top 5 suppliers -->
        <tr>
          <td style="color:#999">1</td>
          <td>[Company Name]</td>
          <td>
            <div class="score-bar">
              <div class="bar"><div class="fill" style="width:[score]%"></div></div>
              <div class="num">[score]</div>
            </div>
          </td>
          <td>$[X.XX]–$[X.XX]</td>
          <td>[N] units</td>
          <td>[N] yrs</td>
          <td>[Gold · TA · Assessed]</td>
        </tr>
      </tbody>
    </table>

    <div class="callout" style="margin-top:20px">
      <strong>Top pick:</strong> [Company Name] — [reason: highest score, most verifications, best price range for target margin]
    </div>
  </div>

  <!-- PHASE 4: PPC KEYWORDS -->
  <div class="section">
    <div class="section-header">
      <div class="section-title">PPC Keyword Intelligence</div>
      <div class="phase-label">Phase 4</div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="label">Total Keywords</div>
        <div class="value">[N]</div>
      </div>
      <div class="stat-card">
        <div class="label">Tier 1 (Priority)</div>
        <div class="value">[N]</div>
      </div>
      <div class="stat-card">
        <div class="label">Tier 2 (Growth)</div>
        <div class="value">[N]</div>
      </div>
      <div class="stat-card">
        <div class="label">Tier 3 (Discovery)</div>
        <div class="value">[N]</div>
      </div>
    </div>

    <table>
      <thead>
        <tr><th>#</th><th>Keyword</th><th>Search Vol</th><th>Tier</th><th>Match Types</th><th>Est. CPC</th></tr>
      </thead>
      <tbody>
        <!-- Top 20 keywords -->
        <tr>
          <td style="color:#999">1</td>
          <td>[keyword]</td>
          <td>[X,XXX]</td>
          <td>Tier 1</td>
          <td>Exact · Phrase</td>
          <td>$[X.XX]</td>
        </tr>
      </tbody>
    </table>

    <div class="callout" style="margin-top:20px">
      <strong>Campaign strategy:</strong> [Brief recommendation — e.g. "Start with the 12 Tier 1 exact-match keywords at $0.90 bid. Run broad on Tier 3 for discovery data. Revisit in 2 weeks."]
    </div>
  </div>

  <!-- FOOTER -->
  <div class="report-footer">
    <div class="brand-mark">LaunchFast</div>
    <div class="generated">Generated [Date] · Data via LaunchFast MCP</div>
  </div>

</div>
</body>
</html>
```

Fill ALL placeholder values (`[...]`) with real data from the research phases.
Save the complete file to the path from Step 1.

---

## STEP 6 — Summary to user

After saving the file:

```
## Research Complete ✓

Report saved to: [file path]

Quick summary:
- Keyword: [keyword]
- Verdict: [GO / INVESTIGATE / PASS] (Score: [N]/100)
- IP Risk: [LOW / MEDIUM / HIGH]
- Best supplier: [Company Name] ($X.XX–$X.XX/unit, MOQ: N)
- PPC keywords found: [N] (Tier 1: N | Tier 2: N | Tier 3: N)

Next steps:
[If GO]: Ready to contact suppliers? Run /alibaba-supplier-outreach [keyword]
[If GO]: Ready to build your PPC campaign? Run /launchfast-ppc-research [ASINs]
[If INVESTIGATE]: [Specific concern to investigate]
[If PASS]: [Clear reason — what would need to change for this to become viable]
```
