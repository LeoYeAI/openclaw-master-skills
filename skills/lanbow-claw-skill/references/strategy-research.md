---
name: ads-strategy-researcher
description: |
  Web-research-driven advertising strategy system that generates executable marketing reports using only web search and web fetch.
  Use when:
  (1) Creating full-funnel e-commerce strategies (Amazon + TikTok + Meta)
  (2) Planning Meta-only advertising campaigns
  (3) Conducting competitor ad analysis via web research (Meta Ad Library, TikTok Creative Center, etc.)
  (4) Building cross-channel marketing plans with budget allocation
  (5) Market research and competitive intelligence gathering
  Triggers: "ads strategy", "advertising plan", "marketing report", "Meta ads", "Amazon strategy", "TikTok strategy", "omni-channel", "competitor research", "market research"
---

# Ads Strategy Researcher

Generate executable marketing strategy reports powered by web research (WebSearch + WebFetch).

## Research Capabilities

This skill relies exclusively on **web search** and **web fetch** for all data gathering:

| Capability | Tool | Use Cases |
|-----------|------|-----------|
| **Web Search** | WebSearch | Market sizing, competitor identification, trend analysis, keyword research, industry benchmarks |
| **Web Fetch** | WebFetch | Scrape competitor websites, read Meta Ad Library pages, fetch landing pages, extract product info from URLs |

### Recommended Research Sources

| Source | URL Pattern | Data Type |
|--------|------------|-----------|
| Meta Ad Library | `facebook.com/ads/library` | Competitor ad copy, formats, active status |
| TikTok Creative Center | `ads.tiktok.com/business/creativecenter` | Trending ads, hashtags, music |
| Amazon | `amazon.com/s?k=` | Listings, BSR, pricing, reviews |
| Google Trends | `trends.google.com` | Search interest, seasonality |
| SimilarWeb (public) | `similarweb.com` | Traffic estimates, channel mix |
| SEMrush/Ahrefs (public) | Search results | Keyword data, backlink insights |

### Research Best Practices

1. **Multiple queries per topic** — use 3-5 varied search queries to triangulate data
2. **Cite sources** — every data point must include `source_type`, `source_year`, `measurement_method`
3. **Cross-validate** — compare data from multiple sources before including in report
4. **Recency bias** — prefer data from last 6 months; flag older data explicitly
5. **WebFetch for depth** — after identifying key pages via search, fetch full page content for detailed extraction

## Strategy Type Selection

| Type | Channels | Use When | Template |
|------|----------|----------|----------|
| **Meta-Only** | Meta (Facebook/Instagram) | Brand advertising, lead generation, app installs | [strategy-meta-only-template.md](strategy-meta-only-template.md) |

## Report Structure Reference

For overall report format and section structure, refer to [strategy-template.md](strategy-template.md) which defines:
- Executive Summary (Top 3 Insights, Top 3 Next Moves, Channel Focus)
- Market & Competitive Patterns (Pattern Library, Gap Map)
- Brand Messaging System (Key Message Architecture, Tone, Key Look)
- Touchpoint Strategy (Full-funnel Map, Message Mapping)
- Media Strategy (Channel Roles, Mix Hypothesis, Validation Plan)
- Growth Strategy Options (What's working, Constraints, Options)
- Action Waves (Immediate/Strategic/Scale phases)
- Copy & Creative Pack (Rewrites, Ad Angles)
- Controls (Metrics, Guardrails, Alert Rules)

**CRITICAL: NO preamble sections.** The report MUST start directly from the Executive Summary. Do NOT include any of the following before the main content:
- Cover pages, report metadata, or version information
- Data source descriptions or methodology sections
- Confidence assessments or disclaimer sections
- Report usage instructions or "how to read this report"
- Report limitations sections
- Input summaries or analysis scope descriptions

## Core Workflow

```
Step 1: Intake & Validation
    | Confirm: product, market, competitors, assets
Step 2: Web Research & Data Collection
    | WebSearch + WebFetch -> structured findings
Step 3: Channel-Specific Analysis
    | Analyze findings per channel priority
Step 4: Cross-Channel Integration (if applicable)
    | Traffic loops, attribution, budget allocation
Step 5: Chapter-Based Report Writing (CRITICAL - see below)
    | Write each section as a SEPARATE markdown file in output/chapters/
Step 6: Format Validation
    | Check all quality requirements per chapter
Step 7: Generate chapters_index.json
    | List all chapter files in order
```

### Step 2 Detail: Web Research Protocol

For each analysis area, follow this research pattern:

```
1. Define research questions (3-5 per topic)
2. Execute WebSearch queries (varied phrasings)
3. Identify high-value pages from results
4. WebFetch key pages for detailed data extraction
5. Structure findings into analysis-ready format
6. Document all sources with citations
```

**Competitor Ad Research (replaces local ad downloads):**

Instead of downloading ad creatives locally, research competitor ads through:

1. **Meta Ad Library** — WebFetch `facebook.com/ads/library/?active_status=active&ad_type=all&q={competitor}` to get ad copy, format descriptions, and active status
2. **TikTok Creative Center** — WebSearch for trending competitor content and ad patterns
3. **WebSearch** — `"{competitor}" site:facebook.com/ads/library` or `"{competitor}" ad creative strategy`
4. **Industry reports** — Search for ad benchmark reports and case studies

Document competitor ads as **text-based analysis** (ad copy, format, hook, CTA, audience signals) rather than image-based forensics.

## CRITICAL: Chapter-Based Output (Prevents Timeout)

**The report MUST be written as separate chapter files, NOT as a single report.md.**

Writing the entire report as one file causes LLM output timeouts. Instead:

1. **Write each major section as a separate file** in `output/chapters/` directory
2. **Generate `output/chapters_index.json`** listing all chapters in order
3. The orchestrator will automatically merge chapters into the final `report.md`

### Chapter File Naming Convention

Files must be named with a 2-digit numeric prefix for ordering:

```
output/chapters/
├── 01_executive_summary.md
├── 02_market_and_competitive_patterns.md
├── 03_brand_messaging_system.md
├── 04_touchpoint_strategy.md
├── 05_media_strategy.md
├── 06_growth_strategy_options.md
├── 07_action_waves.md
├── 08_copy_and_creative_pack.md
├── 09_controls.md
├── 10_references.md
└── ... (additional sections as needed, e.g., 05_amazon_strategy.md for omni-channel)
```

### chapters_index.json Format

After writing all chapters, create `output/chapters_index.json`:

```json
{
  "title": "[Report Title - Conclusion-style]",
  "chapters": [
    { "file": "01_executive_summary.md", "title": "Executive Summary" },
    { "file": "02_market_and_competitive_patterns.md", "title": "Market & Competitive Patterns" }
  ]
}
```

### Writing Rules

- **Write each chapter immediately** after its content is ready (don't wait until all sections are complete)
- **Each chapter file starts with its section heading** (e.g., `## 1. Executive Summary`)
- **The first chapter (01_executive_summary.md)** should start with the report's H1 title: `# [Conclusion-Style Title]`, followed by the executive summary content
- **NO cover or preamble chapter** — do NOT create `00_cover_and_context.md` or any similar preamble file
- **Table numbering** must still be globally incremented across all chapters
- **Do NOT write a single report.md** — the system will merge chapters automatically

## Competitor Analysis Format (Web-Research Based)

Since competitor ad creatives are researched via web search rather than downloaded locally, use the following **text-based** format for competitor ad analysis:

### Competitor Ad Analysis Table

```markdown
Table X: [Competitor Name] — Ad Creative Analysis

| Dimension | Finding |
| :-------- | :------ |
| **Ad Format** | [Static / Carousel / Video / Reels] |
| **Platform** | [Meta / TikTok / YouTube / Google] |
| **Primary Hook** | "[Exact ad copy or hook text]" |
| **Value Proposition** | [Core promise in the ad] |
| **CTA** | [Call to action text] |
| **Target Audience Signals** | [Inferred from ad targeting/copy] |
| **Visual Style** | [Description: colors, imagery, layout] |
| **Landing Page** | [URL if available] |
| **Active Since** | [Date range from Ad Library] |
| **Critique** | [Strategic analysis: why it works/fails] |
| **Counter-Strategy** | [How to compete against this approach] |

Source: [Meta Ad Library / TikTok Creative Center / URL]
```

### Format Rules

1. **One table per ad or ad group** — keep analyses granular
2. **Quote actual ad copy** — use exact text from the ad in "Primary Hook" and "CTA"
3. **Include source URL** — link to the Ad Library page or source
4. **Visual descriptions** — describe visual elements in text (colors, composition, models, product placement)
5. **Always include Counter-Strategy** — make analysis actionable

## Key Output Requirements

1. **Conclusion-style titles**: Express judgment, not category
2. **Numbered tables**: `Table X: [Title]` format, globally incremented
3. **Data source annotations**: Include `source_type`, `source_year`, `measurement_method`
4. **Text-based competitor analysis**: Detailed written analysis with source citations (see format above)
5. **References section**: Always include at document end with URLs
6. **NO local file paths**: Never include local filesystem paths in the final report

## Quick Start Examples

### Omni-Channel E-commerce
```
User: Help me plan the omni-channel strategy for [Brand]
      PDF: product-catalogue.pdf
      Store: amazon.com/stores/xxx
      Main products: [products]
      Target market: North America
      Key channels: Amazon + TikTok

Action: Read omni-channel-template.md -> Execute 8-step workflow
        Use WebSearch/WebFetch for all competitive research
```

### Meta-Only Campaign
```
User: Help me plan the Meta advertising strategy for [Brand]
      Website: example.com
      Target market: [Region]
      Competitors: [competitors]

Action: Read meta-only-template.md -> Execute 6-step workflow
        Use WebSearch/WebFetch for competitor ad research via Meta Ad Library
```

## Document Standards

See [strategy-document-standards.md](strategy-document-standards.md) for:
- Conclusion-style title requirements
- Table numbering conventions
- Data source annotation format
- Competitor ad analysis table structure (text-based)
- Validation checklist

## File Organization

```
output/
├── chapters/                # Chapter-based report output (REQUIRED)
│   ├── 01_executive_summary.md
│   ├── 02_market_and_competitive.md
│   ├── ...
│   └── chapters_index.json  # Chapter ordering manifest
├── extracted/               # Content extraction output
├── research/                # Web research notes and raw data
└── images/                  # Image assets (if any, from URLs)
```

## CRITICAL: No Local File Paths in Report

**The final report must NOT contain any local filesystem paths.** This includes:

- Absolute paths like `/app/workspace/xxx/output/file.md`
- Paths referencing internal directories like `/tmp/`, `/home/`, etc.
- Any path that would be meaningless to the end user

**What to do instead:**
- For Appendices: Summarize the content or key findings, do not list file paths
- For intermediate artifacts: These are for internal processing only, not for the final report
- If referencing analysis documents: Inline the key insights into the report body

**Allowed paths:**
- External URLs: `https://example.com` (public references)
- Relative image paths: `./images/xxx.jpg` (only if images are included in deliverable)
