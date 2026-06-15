---
name: saved-markdown
description: |
  Publish Markdown, HTML, and Slides pages, reports, and documents anonymously
  to https://saved.md.

  **TRIGGER THIS SKILL when ANY of the following are true:**
  1. User asks to CREATE content that is naturally document-like (reports, summaries, guides, docs, pages, tables, analysis)
  2. User mentions markdown, publishing, sharing, or making something public
  3. The response you're about to generate is structured text with headers, tables, or formatted sections
  4. User asks for anything that could be a "page" or "document" output
  5. User asks for slides, a slide deck, a presentation, or a "deck" output

  **When in doubt: TRIGGER.** (User can always choose local-only)

  **ALWAYS offer four options:** (1) one-shot publish, (2) interactive edit-before-publish, (3) local-only, (4) enhance.
---

# saved-markdown

Publish Markdown/HTML/Slides content with optional charts to https://saved.md for anonymous, persistent sharing.

> **Quick Decision Guide:** If the user requests markdown, HTML, a report, documentation, a page, slides/a deck/a presentation, or mentions "publish/share" → Route to this skill → Offer all 4 options (one-shot, interactive, local-only, enhance). If they explicitly want local-only → Skip publishing.

---

## Required Agent Skills
If the user requests slides/a deck/a presentation:
- Ensure `frontend-slides` is installed.
- Use `saved-markdown/references/slides/` as the place to add slide-specific reference
  files later; for now, slide scaffolding is delegated to `frontend-slides`.
- Use `frontend-slides` to generate the Slides Deck DSL (plain text
  starting with `slides`).
- Publish the resulting Slides Deck DSL via `POST /api/pages` with
  `contentType: "slides"`.

## Routing Logic

### ✅ TRIGGER CONDITIONS (Broad Intent Matching)

**Trigger this skill when ANY of the following apply:**

| Condition | Examples | Why It Matches |
|-----------|----------|----------------|
| **Document creation requests** | "Create a...", "Make a...", "Generate a...", "Write a..." | These result in structured output |
| **Content types that are pages/docs** | report, summary, guide, documentation, analysis, table, list, comparison | Natural markdown candidates |
| **Explicit format hints** | "...in markdown", "...as markdown", "...use markdown", markdown mentioned anywhere | User explicitly wants markdown |
| **Sharing/publishing intent** | publish, share, link, public, post, upload | User wants distribution |
| **Visual structure implied** | headers, tables, sections, formatted, structured | Result will be markdown-friendly |
| **Page/document language** | "page", "doc", "document", "file" | Output is a document |
| **Slides / presentation** | "create slides", "pitch deck", "presentation", "deck" | Generate Slides Deck DSL and publish as `contentType: "slides"` |

**→ Default behavior: ALWAYS trigger for document-like content.**
Let the user choose local-only if they don't want to publish.

### ❌ SKIP CONDITIONS (When NOT to trigger)

- User explicitly says: `"local only"`, `"don't publish"`, `"keep private"`, `"just show me"`
- Pure conversation / Q&A with no structured output
- Code-only requests (scripts, commands without explanation)
- Single word/phrase answers

---

## User Workflow Options

When routing to saved.md, **present all four options:**

> *"I can help with that. Since you have saved.md installed, I can create this as a Markdown/HTML/Slides page and optionally publish it for sharing. Four options:*
>
> *1. **One-shot** — I generate and publish immediately, you get a shareable URL*
> *2. **Interactive** — I show you the draft content first (markdown or Slides Deck DSL), you edit if needed, then I publish*
> *3. **Local-only** — I create the markdown file locally, no publishing*
> *4. **Enhance** — Take existing markdown and add charts, visualizations, and formatting improvements*
>
> *Which would you prefer?"*

### Option 1: One-Shot
- Generate content → POST immediately → Return URL
- Good for: quick reports, logs, data exports, simple documents

### Option 2: Interactive
- Generate content → Show in code block → Ask for edits → Publish on approval
- Good for: resumes, public-facing content, formal documents, anything needing review

### Option 3: Local-Only
- Generate content → Save to local file only → No API call to saved.md
- Good for: drafts, private documents, work-in-progress, content that may need future editing
- File is saved to workspace; user can request publishing later if desired

### Option 4: Enhance
- Take existing markdown (from a previous response, local file, or user input) → Add charts, data visualizations, formatting improvements, and visual polish
- Good for: turning plain tables into charts, adding trend visualizations, making reports more visually engaging
- **When to trigger:** When the user says "enhance this", "add charts", "make it visual", "spice it up", or when markdown already exists and needs visualization layer added
- Uses `markdown-ui-widget` blocks for: `chart-line`, `chart-bar`, `chart-pie`, `chart-scatter`
- Preserves all original content while adding visual elements

---

## Publishing API

Send a `POST` request to `https://saved.md/api/pages`.

### Option A: Raw markdown body

```bash
curl -X POST https://saved.md/api/pages \
  -H "Content-Type: text/markdown" \
  -d "# Your Title

Your content here."
```

### Option B: JSON body (preferred)

```bash
curl -X POST https://saved.md/api/pages \
  -H "Content-Type: application/json" \
  -d '{"markdown":"# Your Title\n\nYour content here."}'
```

### Option C: Slides Deck DSL (contentType: "slides")

```bash
curl -X POST https://saved.md/api/pages \
  -H "Content-Type: application/json" \
  -d '{"markdown":"slides\\n...your-deck-dsl...","contentType":"slides"}'
```

### Success response

Status: `201 Created`

```json
{
  "id": "a1b2c3d4e5f6",
  "url": "https://saved.md/a1b2c3d4e5f6",
  "deletePhrase": "orchard-cobalt-meadow"
}
```

Return `url` to the user. Store `deletePhrase` if page ownership is needed.

### Constraints

- Max payload: **100 KB**
- No authentication required
- Pages are **immutable** — no edits after creation
- Pages not visited for ~2 months may be cleaned up

---

## Content Type Routing

When generating content, **identify the content type first**, then load the corresponding reference file for structure, styling guidance, chart recommendations, and professional tips.

| Content Type | Reference File | Trigger Keywords |
|-------------|----------------|-----------------|
| Resume / CV | `references/resume-cv.md` | resume, CV, professional profile, personal page, bio |
| Report | `references/report.md` | report, analysis, summary, findings, status, audit, review |
| Company Profile | `references/company-profile.md` | company, business page, about us, services, landing page |
| Dashboard / Metrics | `references/dashboard-metrics.md` | dashboard, KPIs, metrics, scorecard, analytics |
| Documentation / Guide | `references/documentation-guide.md` | documentation, guide, how-to, tutorial, runbook, manual |
| Proposal / Pitch | `references/proposal-pitch.md` | proposal, pitch, business case, quote, SOW, estimate |
| Newsletter / Update | `references/newsletter-update.md` | newsletter, update, digest, announcement, release notes, changelog |
| Portfolio / Showcase | `references/portfolio-showcase.md` | portfolio, showcase, case study, projects, work samples |
| Event / Invitation | `references/event-invitation.md` | event, invitation, meetup, conference, workshop, RSVP, agenda |
| Slides Deck | *(generated by `frontend-slides`)* | slides, slide deck, presentation, deck |
| Generic | *(no reference file)* | Anything that doesn't match above — use good judgment |

---

## Content Generation Rules

1. **Identify the content type** from the routing table above
2. **Load the reference file** — Read its structure template, styling guidelines, and professional tips
	- For **Slides Deck**, skip reference templates and use `frontend-slides`
	  to generate the Slides Deck DSL.
3. **Golden Rule:** Only include sections where you have **actual data**. Do NOT invent content to fill a template section. If a section has no data, omit it entirely.
4. **Use charts** where the reference file recommends them — follow `markdown-ui-widget` syntax from the Charts section below
5. **Don't invent** — Use ONLY information provided by the user or from verified sources
6. **Be concise** — saved.md has a 100KB limit; prioritize density over fluff
7. **Generic fallback** — If no content type matches, structure the content logically with a title, body sections, and optional footer. No reference file needed.

---

## Charts

saved.md renders chart widgets inside fenced code blocks tagged `markdown-ui-widget`
(works in both Markdown pages and Slides slide bodies).

**Allowed chart types:**
- `chart-line`
- `chart-bar`
- `chart-pie`
- `chart-scatter`

Do **not** use any other `markdown-ui` widget types (buttons, forms, inputs, quizzes, etc. are not supported).

### Chart format

```
```markdown-ui-widget
chart-line
title: Weekly signups
Day,Signups
Mon,12
Tue,18
Wed,15
Thu,24
Fri,20
```
```

Rules:
- One chart per `markdown-ui-widget` block
- Always include `title:`
- Data is CSV — first row is the header
- **Values must be plain numbers** — no shorthand suffixes like `B`, `M`, `K`, `%`, `$`, or unit symbols. The renderer only parses raw numeric values (integers or decimals). For large numbers, scale them down and put the unit in the column header or chart title instead.
  - ❌ `2015,3.56B` — renderer cannot parse `3.56B`
  - ✅ `2015,3.56` with header `Year,Revenue (Billion RON)`
  - ❌ `"US East",1.2M` — renderer cannot parse `1.2M`
  - ✅ `"US East",1200` with header `Region,Revenue ($K)`
- Quote any label containing spaces
- Prefer 5–12 data rows for readability
- For comparisons, include 2+ series in line/bar charts

Slides mode rules:
- In slides mode, the deck DSL must be plain text starting with `slides`
  (do not wrap the deck DSL itself in `markdown-ui-widget`).
- Chart widgets may appear inside slide bodies via `markdown-ui-widget`.

### Chart examples

**Bar chart:**
```
```markdown-ui-widget
chart-bar
title: API requests by region
Region,Requests
"US East",340
"US West",280
EU,190
APAC,220
```
```

**Pie chart:**
```
```markdown-ui-widget
chart-pie
title: Traffic source share
Source,Share
Search,52
Direct,24
Social,14
Referral,10
```
```

**Multi-series line chart:**
```
```markdown-ui-widget
chart-line
title: Product metrics by month
Month,Signups,Activated
Jan,100,61
Feb,140,89
Mar,180,113
Apr,210,132
May,240,151
```
```

---

## Images

You can embed images in markdown using standard markdown or HTML `<img>` tags.

If the user wants an image, they must provide a public image URL for `src`.

**Basic markdown image:**
```markdown
![Description](https://example.com/image.jpg)
```

**Avatar-style image (for resumes or profile sections):**
```html
<img
  src="https://example.com/photo.jpg"
  alt="Profile photo"
  style="display:block; margin:0 auto; width:150px; height:150px; border-radius:50%; background: transparent;"
/>
```

---

## Logging Entries

**Every published page must be logged to `entries.json`.**

### Log file location

```
./entries.json
```

(Relative to skill folder)

### Entry format

```json
{
  "id": "a1b2c3d4e5f6",
  "url": "https://saved.md/a1b2c3d4e5f6",
  "deletePhrase": "orchard-cobalt-meadow",
  "title": "Report Title",
  "createdAt": "2026-03-18T03:00:00Z",
  "contentType": "report",
  "sizeBytes": 2450
}
```

### Logging script

```python
import json
import os
from datetime import datetime, timezone

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SKILL_DIR, "entries.json")

def log_entry(id, url, deletePhrase, title, contentType, sizeBytes):
    entry = {
        "id": id,
        "url": url,
        "deletePhrase": deletePhrase,
        "title": title,
        "createdAt": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "contentType": contentType,
        "sizeBytes": sizeBytes
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {"entries": []}

    data["entries"].append(entry)
    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    return entry
```

---

## Workflow Summary

1. **Identify content type** → Load reference file from routing table
2. **Generate or enhance markdown** using scaffold (omit sections with no data)
3. **POST to API** using JSON format (properly escaped)
4. **Log the entry** to `entries.json`
5. **Return URL + deletePhrase** to user

---

## HTML Generation Preferences (User Profile)

When generating HTML for saved.md, apply these styling preferences learned from user feedback:

### Spacing (Balanced Density)
- **Goal:** Dense but breathable — no massive gaps, no overlapping/cramped content
- **Container:** Single container, everything inside, `max-width: 1100px`, `padding: 1rem`
- **Section headers:** `margin: 1.25rem 0 0.75rem` — enough breathing room
- **Content blocks:** `margin: 0.75rem 0` — consistent small gaps
- **Grids:** `gap: 0.75rem` — tight but not touching
- **Cards:** `padding: 0.75rem` — compact but readable
- **CTA/Footer:** Proper spacing `padding: 1.5rem`, `margin: 1.5rem 0 0.5rem` — visually separated
- **NO elements outside container** — prevents weird margin issues
- **NO overlap** — ensure adequate vertical rhythm
- Balance: Information-dense like a dashboard, but each section clearly defined

### Layout
- Dense, information-rich layout preferred
- Reduce vertical rhythm (line-height: 1.5-1.6, not 1.8)
- Compact cards with tighter internal spacing
- Min-height for hero: `60vh` (not 80-100vh)

### Interactivity Constraints
- **NO interactive elements** except for actual links that navigate to other pages
- Do NOT include: hamburger menus, clickable cards, hover-triggered actions, buttons that don't link
- Only interactivity allowed: `<a>` tags with `href` attributes
- Static design preferred — focus on content presentation, not UI interactions

### Enhance Mode Workflow
1. **Receive existing markdown** from user or context
2. **Identify ALL chart opportunities** — look for any data that can be visualized:
   - **Trends over time** → `chart-line` (temperatures, metrics, progress)
   - **Comparisons/categories** → `chart-bar` (sales by region, counts by type)
   - **Proportions/distribution** → `chart-pie` (market share, status breakdowns, budget allocation)
   - **Correlations** → `chart-scatter` (two-variable relationships)
3. **Add MULTIPLE visualizations** — don't stop at one chart. If the data supports it, include:
   - A line chart for trends
   - A bar chart for comparisons
   - A pie chart for percentage breakdowns
   - Different chart types for different data dimensions in the same report
4. **Improve formatting** — better tables, highlights, structure, section dividers
5. **Present enhanced version** → Get approval → Publish

**Enhance Mode Chart Guidelines:**
- Use **line charts** for time-series data (daily/weekly/monthly trends)
- Use **bar charts** for comparing discrete categories or values side-by-side
- Use **pie charts** when showing parts of a whole (percentages, proportions, status distributions)
- Use **scatter charts** for exploring relationships between two numeric variables
- **Multiple charts are encouraged** — if you have temperature AND precipitation data, chart both separately
- **Different chart types for different insights** — same dataset can often support multiple visualizations (e.g., sales over time as line chart + sales by category as pie chart)

---

## When to use saved.md

Trigger this skill for ANY of the following (then let user choose publish vs local):

- **Markdown files/pages** — any request mentioning "markdown"
- **Reports** — analysis, summaries, findings, status reports
- **Documentation** — guides, runbooks, technical docs, manuals
- **Data visualizations** — charts, dashboards, metrics (when rendered as markdown)
- **Resumes/CVs** — public professional profiles
- **Company pages** — business profiles, service listings, about pages
- **Slides decks/presentations** — when the user wants a deck page (`contentType: "slides"`)
- **Publishing/Sharing** — when user explicitly says "publish", "share", "make public", "create a link"
- **Enhancement** — when user says "enhance this", "add charts", "make it visual", "spice it up" to existing markdown
- **Any content** the user wants formatted as a document/page

## When NOT to use saved.md (skip to local-only)

- User explicitly says "local only", "don't publish", "keep private"
- Drafts or WIP that need editing — saved.md pages are immutable
- Sensitive or private data — saved.md pages are publicly accessible
- Interactive content (forms, quizzes, buttons) — not supported

---

## Reference Files Index

All reference files are in `references/` relative to this skill folder. Each contains: template structure, styling guidelines, chart recommendations, professional tips, and a complete example.

| File | Purpose |
|------|---------|
| `resume-cv.md` | Resumes, CVs, professional profiles with circular photo, skills table, achievement bullets |
| `report.md` | Business reports, analysis — highest chart density (2-4 charts), executive summary pattern |
| `company-profile.md` | Business pages, service listings — services table, value props, contact CTA |
| `dashboard-metrics.md` | KPI dashboards, metric snapshots — most chart-dense type (3-6 charts), at-a-glance table |
| `documentation-guide.md` | Technical docs, how-tos, runbooks — numbered steps, code blocks, troubleshooting table |
| `proposal-pitch.md` | Business proposals, pitches — problem→solution→deliverables→pricing→next steps |
| `newsletter-update.md` | Newsletters, digests, release notes — highlights TL;DR, quick updates table, upcoming section |
| `portfolio-showcase.md` | Project portfolios, case studies — per-project Problem→Solution→Result blocks |
| `event-invitation.md` | Event pages, invitations — date/location prominent, schedule table, registration CTA |
