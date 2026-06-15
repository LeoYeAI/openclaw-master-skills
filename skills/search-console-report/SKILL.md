---
name: search-console-report
description: Generate comprehensive SEO analysis reports from Google Search Console data with PDF export. Use when the user wants to analyze search performance, get SEO insights, view traffic trends, top pages, top keywords, country/device distribution, or generate a professional PDF report for one or more websites using Google Search Console API. Requires a Google Cloud Service Account JSON key with Search Console read access.
---

# Search Console SEO Report Generator

Generate professional, chart-rich PDF reports from Google Search Console data. Covers traffic trends, top pages, top keywords, country/device distribution, growth analysis, and actionable SEO recommendations.

## Prerequisites

Before running this skill, verify these requirements:

### 1. Service Account Key File

You need a Google Cloud Service Account JSON key file with access to the Search Console properties. The file looks like:

```json
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "xxx@project.iam.gserviceaccount.com",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

Ask the user for the path to their key file. Common locations: `~/Downloads/*.json`, project directory.

If the user doesn't have one yet, guide them through:
1. Create a Service Account in Google Cloud Console (IAM & Admin > Service Accounts)
2. Create a JSON key for it (Keys tab > Add Key > JSON)
3. Add the service account email as a user in Search Console (Settings > Users and permissions > Add user, "Restricted" permission is sufficient)
4. Enable the "Google Search Console API" in the project's API Library

### 2. Python Environment

The script requires these packages: `pyjwt`, `cryptography`, `requests`, `matplotlib`, `pandas`, `reportlab`.

Set up a virtual environment to avoid system conflicts:

```bash
python3 -m venv /tmp/sc-env
/tmp/sc-env/bin/pip install pyjwt cryptography requests matplotlib pandas reportlab
```

**IMPORTANT**: Always use `/tmp/sc-env/bin/python` to run scripts, not the system Python.

**Timeout warning**: Package installation and first matplotlib import can be slow (60-120s). Set bash timeout to 180000ms for these operations.

### 3. Chinese Font for PDF (macOS)

The PDF uses STHeiti for proper CJK + Latin + symbol rendering. Register it like this:

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('CNFont', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('CNFontLight', '/System/Library/Fonts/STHeiti Light.ttc', subfontIndex=0))
pdfmetrics.registerFontFamily('CNFont', normal='CNFontLight', bold='CNFont')
```

**CRITICAL font rules:**
- Do NOT use `UnicodeCIDFont('STSong-Light')` — it causes English letter spacing to be too narrow and Unicode symbols like `•` (U+2022) to render as garbage characters (e.g. "煉").
- Always use TrueType fonts registered via `TTFont` for proper mixed CJK/Latin rendering.
- On non-macOS systems, find an available CJK TTF font: `fc-list :lang=zh file` or look for Noto Sans CJK / WenQuanYi.

## Step-by-Step Instructions

### Step 1: Gather Input from User

Ask for or determine:
- **Key file path**: Path to the Service Account JSON key file
- **Site URLs**: One or more Search Console property URLs (format: `https://www.example.com/`)
- **Date range**: Default to last 90 days. The user may request a custom range.
- **Output path**: Where to save the PDF and data files. Default to project directory.
- **Language**: Report can be in Chinese (default) or English — match the user's language.

### Step 2: Authenticate with Google API

Use JWT-based Service Account authentication. Here is the exact authentication code:

```python
import json, time, jwt, requests

def get_access_token(key_file):
    with open(key_file) as f:
        creds = json.load(f)
    
    now = int(time.time())
    payload = {
        "iss": creds["client_email"],
        "scope": "https://www.googleapis.com/auth/webmasters.readonly",
        "aud": creds["token_uri"],
        "iat": now,
        "exp": now + 3600,
    }
    signed_jwt = jwt.encode(payload, creds["private_key"], algorithm="RS256")
    
    resp = requests.post(creds["token_uri"], data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": signed_jwt,
    })
    resp.raise_for_status()
    return resp.json()["access_token"]
```

**Error handling**: If authentication fails with 403, the API may not be enabled or the service account may not have Search Console access. Tell the user which to check.

### Step 3: Fetch Data from Search Console API

Use the Search Analytics API endpoint for each site. The base query function:

```python
import datetime

END_DATE = datetime.date.today() - datetime.timedelta(days=3)  # Data has ~3 day lag
START_DATE = END_DATE - datetime.timedelta(days=89)

def query_sc(token, site_url, dimensions, start=None, end=None, row_limit=100):
    """Query Search Console Search Analytics API.
    
    Args:
        token: OAuth2 access token
        site_url: Full property URL, e.g. "https://www.example.com/"
        dimensions: List of dimensions. Valid values:
            - "date"    — daily breakdown
            - "query"   — search keywords
            - "page"    — page URLs
            - "country" — ISO 3166-1 alpha-3 country codes (lowercase)
            - "device"  — "DESKTOP", "MOBILE", "TABLET"
            - "searchAppearance" — rich result types
            Can combine: ["query", "page"] for keyword-page matrix
        start: Start date (datetime.date). Defaults to START_DATE.
        end: End date (datetime.date). Defaults to END_DATE.
        row_limit: Max rows (max 25000).
    
    Returns:
        List of row dicts with keys: "keys" (list), "clicks", "impressions", "ctr", "position"
        Note: "ctr" is a decimal (0.05 = 5%), multiply by 100 for display.
    """
    url = f"https://www.googleapis.com/webmasters/v3/sites/{requests.utils.quote(site_url, safe='')}/searchAnalytics/query"
    body = {
        "startDate": (start or START_DATE).isoformat(),
        "endDate": (end or END_DATE).isoformat(),
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body)
    resp.raise_for_status()
    return resp.json().get("rows", [])
```

For each site, fetch ALL of the following data (this is the complete list — do not skip any):

| # | Query | Dimensions | row_limit | Purpose |
|---|-------|-----------|-----------|---------|
| 1 | Daily traffic trend | `["date"]` | 25000 | Time series for charts |
| 2 | Top pages | `["page"]` | 50 | Most visited pages |
| 3 | Top queries | `["query"]` | 50 | Most searched keywords |
| 4 | Country distribution | `["country"]` | 30 | Geographic breakdown |
| 5 | Device distribution | `["device"]` | 10 | Desktop/Mobile/Tablet split |
| 6 | Search appearance | `["searchAppearance"]` | 20 | Rich result types |
| 7 | Query-page combos | `["query", "page"]` | 100 | Which keywords drive which pages |
| 8 | Period comparison (first half) | `["page"]` with first-half dates | 500 | Growth analysis |
| 9 | Period comparison (second half) | `["page"]` with second-half dates | 500 | Growth analysis |

**Period comparison logic**: Split the date range in half. For each page URL, compare clicks between the two halves. Categorize pages as:
- **Growing**: clicks increased (sort by change descending)
- **Declining**: clicks decreased (sort by change ascending)
- **New**: appeared only in the second half
- **Lost**: appeared only in the first half

### Step 4: Calculate Summary Statistics

For each site, compute:

```python
daily = site_data["daily_trend"]
total_clicks = sum(d["clicks"] for d in daily)
total_impressions = sum(d["impressions"] for d in daily)
avg_ctr = sum(d["ctr"] for d in daily) / len(daily)  # Already *100 if you stored it that way
avg_position = sum(d["position"] for d in daily) / len(daily)

# Trend: compare last 30 days vs first 30 days
if len(daily) >= 60:
    first_30_clicks = sum(d["clicks"] for d in daily[:30])
    last_30_clicks = sum(d["clicks"] for d in daily[-30:])
    click_trend_pct = ((last_30_clicks - first_30_clicks) / max(first_30_clicks, 1)) * 100
    # Same for impressions
```

### Step 5: Save Raw Data as JSON

Save all fetched data to `sc_detailed_data.json` for reproducibility:

```python
with open(f"{output_dir}/sc_detailed_data.json", "w") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
```

### Step 6: Generate Charts with Matplotlib

**IMPORTANT**: Always set `matplotlib.use('Agg')` BEFORE importing pyplot (no display server available).

Generate these charts (save as PNG, dpi=150):

#### Chart 1: Combined Traffic Trend (all sites)
- 2-row subplot: top = daily clicks, bottom = daily impressions
- One line per site, color-coded
- X-axis: dates formatted as `%m-%d`, rotated 45 degrees
- Legend in upper-left

#### Chart 2: Per-site Detail (one per site with enough data)
- 2-row subplot: top = daily clicks with 7-day moving average, bottom = average position (inverted Y-axis — lower is better)
- Fill area under clicks line with alpha=0.3

```python
# 7-day moving average calculation
if len(clicks) >= 7:
    ma7 = [sum(clicks[max(0,i-6):i+1]) / min(7, i+1) for i in range(len(clicks))]
```

#### Chart 3: Device Distribution
- 1-row, N-column pie charts (one per site)
- Show percentage labels

#### Chart 4: Country Distribution (horizontal bar, for sites with significant traffic)
- Top 10 countries by clicks
- Map country codes to readable names using this mapping:

```python
COUNTRY_NAMES = {
    'idn': 'Indonesia', 'hkg': 'Hong Kong', 'mac': 'Macau', 'kor': 'South Korea',
    'usa': 'United States', 'jpn': 'Japan', 'sgp': 'Singapore', 'mys': 'Malaysia',
    'twn': 'Taiwan', 'tha': 'Thailand', 'phl': 'Philippines', 'ind': 'India',
    'vnm': 'Vietnam', 'gbr': 'United Kingdom', 'deu': 'Germany', 'fra': 'France',
    'aus': 'Australia', 'can': 'Canada', 'bra': 'Brazil', 'mex': 'Mexico',
    'chn': 'China', 'pak': 'Pakistan', 'bgd': 'Bangladesh', 'lka': 'Sri Lanka',
    'mmr': 'Myanmar', 'khm': 'Cambodia', 'npl': 'Nepal', 'are': 'UAE',
    'sau': 'Saudi Arabia', 'tur': 'Turkey', 'egy': 'Egypt', 'nga': 'Nigeria',
    'ken': 'Kenya', 'zaf': 'South Africa', 'col': 'Colombia', 'arg': 'Argentina',
    'per': 'Peru', 'chl': 'Chile', 'nzl': 'New Zealand', 'ita': 'Italy',
    'esp': 'Spain', 'nld': 'Netherlands', 'rus': 'Russia', 'pol': 'Poland',
}
```

### Step 7: Generate PDF Report

Use reportlab with A4 page size. The report has 7 sections:

#### PDF Structure

```
Cover Page
  - Report title (in user's language)
  - Subtitle: "Google Search Console Data Analysis & Recommendations"
  - Report date, data range, data source, covered sites

Section 1: Executive Summary
  - Summary table (all sites: clicks, impressions, avg CTR, avg position, trends)
  - Key findings (5-6 bullet points highlighting most important insights)

Section 2: Traffic Trends
  - Combined traffic trend chart (all sites)
  - Per-site detail charts (clicks + position)

Section 3: Top Pages (TOP 10)
  - Table per site: rank, page path, clicks, impressions, CTR, position
  - Shorten long URLs: if > 45 chars, truncate with "..."

Section 4: Top Keywords (TOP 15)
  - Table per site: rank, keyword, clicks, impressions, CTR, position

Section 5: Country & Device Distribution
  - Device pie charts
  - Country bar charts (for major sites)
  - Country tables (all sites, top 10)

Section 6: Growth Analysis
  - Per site: growing pages table (green header), declining pages table (red header)
  - New page count, lost page count

Section 7: Recommendations & Action Plan
  - AI-generated recommendations based on the data (see analysis guidelines below)
  - Priority action table (P0/P1/P2)
```

#### PDF Style Configuration

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, PageBreak, HRFlowable)
from reportlab.lib import colors as rl_colors

doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

# Define styles — use 'CNFont' (the registered STHeiti font)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CNTitle', fontName='CNFont', fontSize=22,
                          alignment=TA_CENTER, spaceAfter=6*mm, leading=28))
styles.add(ParagraphStyle(name='CNSubtitle', fontName='CNFont', fontSize=12,
                          alignment=TA_CENTER, textColor=rl_colors.grey, spaceAfter=10*mm))
styles.add(ParagraphStyle(name='CNHeading1', fontName='CNFont', fontSize=16,
                          spaceAfter=4*mm, spaceBefore=8*mm, leading=22,
                          textColor=rl_colors.HexColor('#1a73e8')))
styles.add(ParagraphStyle(name='CNHeading2', fontName='CNFont', fontSize=13,
                          spaceAfter=3*mm, spaceBefore=5*mm, leading=18,
                          textColor=rl_colors.HexColor('#333333')))
styles.add(ParagraphStyle(name='CNBody', fontName='CNFont', fontSize=10,
                          spaceAfter=2*mm, leading=16))
styles.add(ParagraphStyle(name='CNSmall', fontName='CNFont', fontSize=8,
                          textColor=rl_colors.grey, leading=12))
styles.add(ParagraphStyle(name='CNBullet', fontName='CNFont', fontSize=10,
                          spaceAfter=1.5*mm, leading=16, leftIndent=10*mm,
                          bulletIndent=5*mm))
```

#### Table Style Template

Use this consistent style for all data tables:

```python
table_style = TableStyle([
    ('FONTNAME', (0,0), (-1,-1), 'CNFont'),
    ('FONTSIZE', (0,0), (-1,-1), 7),        # Small font for dense data
    ('BACKGROUND', (0,0), (-1,0), rl_colors.HexColor('#1a73e8')),  # Blue header
    ('TEXTCOLOR', (0,0), (-1,0), rl_colors.white),
    ('ALIGN', (2,0), (-1,-1), 'RIGHT'),     # Numbers right-aligned
    ('ALIGN', (0,0), (0,-1), 'CENTER'),     # Rank column centered
    ('GRID', (0,0), (-1,-1), 0.5, rl_colors.HexColor('#dddddd')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [rl_colors.white, rl_colors.HexColor('#f8f9fa')]),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
])
```

#### Bullet Points

Use Unicode bullet character `\u2022` (•) for list items:

```python
story.append(Paragraph(f"\u2022 {text}", styles['CNBullet']))
```

This renders correctly with STHeiti font. Do NOT use other bullet approaches.

### Step 8: Generate SEO Recommendations

Analyze the data and generate recommendations following these guidelines:

#### Analysis Framework

1. **CTR Analysis**: If average CTR < 5%, recommend Title/Description optimization.
2. **Position Opportunities**: Find keywords ranking 5-15 (page 1-2 boundary) — these are low-hanging fruit for optimization.
3. **Country Focus**: Identify the #1 traffic country and recommend localized content.
4. **Growth Momentum**: Sites with click growth > 100% are in "breakout" phase — recommend increasing content investment.
5. **New Sites**: Sites with < 30 days of data need basic SEO foundations (Sitemap submission, internal linking).
6. **Declining Pages**: If many pages have declining clicks, recommend content quality audit.
7. **Device Split**: If mobile > 60%, emphasize mobile optimization and Core Web Vitals.
8. **Technical SEO**: Always recommend hreflang for multi-region sites, 404 fixes, and page speed optimization.

#### Priority Classification

- **P0** (Do immediately): CTR optimization, fixing unindexed pages
- **P1** (Do this month): Content localization, keyword optimization for positions 5-15
- **P2** (Plan for next quarter): hreflang implementation, Core Web Vitals, Sitemap tuning

### Step 9: Present Results

After generating the PDF:

1. Confirm the PDF file path to the user
2. Provide a summary in chat covering:
   - Report structure (sections and page count)
   - Key highlights per site (1-2 sentences each)
   - Top 3 priority recommendations
3. Mention the raw data JSON file path for further analysis
4. Offer next steps (e.g., "Do you want me to analyze a specific page or keyword in more detail?")

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `403 Forbidden` on API call | Service account not added to Search Console | Add the service account email as a user in Search Console settings |
| `403 Google Search Console API has not been enabled` | API not enabled | Enable it at https://console.cloud.google.com/apis/library/searchconsole.googleapis.com |
| Empty `rows` in response | No data for that site/date range | Check if the site URL exactly matches the Search Console property (trailing slash matters!) |
| `jwt.encode` error | Missing `cryptography` package | `pip install cryptography` |
| PDF shows garbled Chinese | Wrong font | Use TTFont with STHeiti, NOT UnicodeCIDFont with STSong-Light |
| Matplotlib timeout on first run | Building font cache | Set bash timeout to 180000ms; this only happens once |
| `MPLCONFIGDIR` warning | No write access to `~/.matplotlib` | Harmless; matplotlib creates a temp cache automatically |

## Example Usage

**User**: "Help me generate an SEO report for my websites using Search Console"
→ Ask for key file path and site URLs, then run the full pipeline.

**User**: "Analyze search performance for example.com over the last 90 days and export to PDF"
→ Run with default 90-day range, generate full report.

**User**: "Compare search traffic between my 3 sites"
→ Run for all 3 sites, emphasize the comparison aspects in the summary table and trends chart.

## Output Files

| File | Description |
|------|-------------|
| `sc_detailed_data.json` | Raw API data for all sites (reproducible) |
| `report_charts/*.png` | Generated chart images |
| `search_console_report.pdf` | Final PDF report |
