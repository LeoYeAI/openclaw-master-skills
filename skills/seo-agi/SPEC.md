# SEO-AGI Technical Specification

## Overview

seo-agi is a Claude Code skill that writes and rewrites SEO-optimized pages
using live competitive data from DataForSEO and Google Search Console.
It bridges the gap between "SEO audit tools" and "content generation" by
making the data the input to the writing, not a separate workflow.

## Architecture

```
User prompt ("write a page for airport parking JFK")
  │
  ▼
SKILL.md (orchestrator)
  │
  ├── scripts/research.py        ← DataForSEO SERP + keyword data
  │     └── lib/dataforseo.py    ← API client
  │     └── lib/serp_analyze.py  ← Content extraction + gap analysis
  │     └── lib/paa.py           ← People Also Ask extraction
  │
  ├── scripts/gsc_pull.py        ← Google Search Console data
  │     └── lib/gsc_client.py    ← GSC API client
  │     └── lib/cannibalization.py ← Query overlap detection
  │
  ├── scripts/setup.py           ← First-run config + dependency install
  │
  └── references/
        ├── page-templates.md    ← Structural templates by page type
        ├── schema-patterns.md   ← JSON-LD patterns by content type
        └── quality-checklist.md ← Scoring rubric for output validation
```

## Data Flow

### Write Flow

```
1. RESEARCH
   Input:  keyword string, optional location/language
   Action: DataForSEO SERP API → top 10 results
           DataForSEO Keywords API → related keywords + volumes
           DataForSEO PAA → People Also Ask questions
           (optional) GSC → existing pages for cannibalization check
   Output: research.json saved to ~/.local/share/seo-agi/research/

2. ANALYZE
   Input:  research.json
   Action: Extract competitor content structure (headings, word count, topics)
           Identify content gaps (topics competitors cover that you'd miss)
           Score keyword difficulty vs. content depth required
           Detect search intent (informational, commercial, transactional, navigational)
   Output: analysis object passed to Claude context

3. BRIEF
   Input:  analysis object
   Action: Claude generates content brief using analysis + page template
   Output: brief.md saved to ~/Documents/SEO-AGI/briefs/

4. WRITE
   Input:  brief + analysis + research data
   Action: Claude writes full page following brief constraints
           Validates against quality checklist
           Generates schema markup
   Output: page.md saved to ~/Documents/SEO-AGI/pages/
```

### Rewrite Flow

```
1. INGEST
   Input:  URL or file path
   Action: Fetch/read existing content
           Extract: title, meta, headings, word count, structure
           Identify target keyword (from title/H1 or user input)
   Output: existing_page object

2. RESEARCH (same as Write flow, using detected keyword)

3. GAP ANALYSIS
   Input:  existing_page + research data
   Action: Compare existing page against top 3 SERP competitors
           Identify: missing sections, thin areas, outdated claims
           (optional) GSC: actual query performance, CTR, position trends
   Output: gap_report object

4. REWRITE
   Input:  existing_page + gap_report + research data
   Action: Claude rewrites following gap report
           Produces change summary (what changed and why)
           Updates schema markup
   Output: rewritten_page.md + changes.md saved to ~/Documents/SEO-AGI/rewrites/
```

## DataForSEO API Endpoints Used

| Endpoint | Purpose | Used In |
|---|---|---|
| `/v3/serp/google/organic/live/advanced` | Live SERP results | research.py |
| `/v3/serp/google/organic/task_post` | Async SERP (batch) | research.py (future) |
| `/v3/dataforseo_labs/google/related_keywords/live` | Related keywords | research.py |
| `/v3/dataforseo_labs/google/keyword_suggestions/live` | Keyword ideas | research.py |
| `/v3/serp/google/organic/live/advanced` (with PAA) | People Also Ask | research.py |
| `/v3/on_page/content_parsing/live` | Competitor content | serp_analyze.py |

## Google Search Console API Usage

| Method | Purpose | Used In |
|---|---|---|
| `searchanalytics.query()` | Query performance data | gsc_pull.py |
| `sitemaps.list()` | Indexed pages | gsc_pull.py (future) |

## Configuration

All config stored in `~/.config/seo-agi/`:

```
~/.config/seo-agi/
├── .env              # API credentials
├── config.json       # User preferences (default location, language, site URL)
└── sites.json        # GSC verified sites cache
```

### config.json schema

```json
{
  "default_location": 2840,
  "default_language": "en",
  "default_site": "https://example.com",
  "serp_depth": 10,
  "save_research": true,
  "output_dir": "~/Documents/SEO-AGI"
}
```

## Output Schema

### research.json

```json
{
  "keyword": "airport parking JFK",
  "timestamp": "2026-03-17T14:30:00Z",
  "location": 2840,
  "serp": [
    {
      "position": 1,
      "url": "https://...",
      "title": "...",
      "description": "...",
      "word_count": 2400,
      "headings": ["H1: ...", "H2: ...", "H2: ..."],
      "topics_covered": ["pricing", "shuttle service", "terminal maps"]
    }
  ],
  "related_keywords": [
    {"keyword": "JFK long term parking", "volume": 4400, "difficulty": 45},
    {"keyword": "cheap parking near JFK", "volume": 2900, "difficulty": 38}
  ],
  "paa_questions": [
    "How much does parking cost at JFK?",
    "Is there free parking at JFK airport?",
    "What is the cheapest way to park at JFK?"
  ],
  "intent": "commercial",
  "avg_word_count": 1850,
  "content_gaps": ["shuttle frequency", "EV charging", "real-time availability"]
}
```

### page.md frontmatter

```yaml
---
title: "Airport Parking at JFK: Pricing, Lots & Shuttle Guide [2026]"
meta_description: "Compare JFK airport parking options from $8/day. Official lots, off-site alternatives, shuttle times, and terminal-specific tips."
target_keyword: "airport parking JFK"
secondary_keywords: ["JFK long term parking", "cheap parking near JFK"]
word_count: 2200
page_type: "service-location"
schema_type: "FAQPage, LocalBusiness"
created: "2026-03-17"
research_file: "~/.local/share/seo-agi/research/airport-parking-jfk-20260317.json"
---
```

## Testing

```bash
# Run with mock fixtures (no API calls)
python3 scripts/research.py "test keyword" --mock

# Run tests
python3 -m pytest tests/
```

Fixtures in `fixtures/` provide sample API responses for offline development.
