# Document Writing Standards

## 1. Conclusion-Style Titles

Titles must express a judgment, not a category.

| Status    | Example                                                                                 |
| --------- | --------------------------------------------------------------------------------------- |
| Correct | The core reason for current ad efficiency decline stems from incomplete signal pipeline |
| Wrong   | Internal Analysis                                                                       |
| Correct | TikTok seeding + Amazon harvesting can achieve 30% incremental growth                   |
| Wrong   | Channel Strategy                                                                        |

## 2. Table Numbering Convention

Format: `Table X: Table Title (Descriptive)`

- **X** = Global number (increments throughout document, no duplicates)
- Table must be placed directly below the label line
- **CRITICAL: Always leave a blank line before every table.** Many Markdown renderers (especially PDF converters) require a blank line before the `| Header |` row. Without it, the table will render as plain text with visible pipe characters.

Example:
```markdown
Table 1: SMART Objectives
| Metric | Current Value | Target Value | Time Frame | Measurement Method |
| ------ | ------------- | ------------ | ---------- | ------------------ |

Table 2: Competitor Comparison Matrix
| Competitor | Price | Rating | Review Count | BSR |
| ---------- | ----- | ------ | ------------ | --- |
```

## 3. Data Source Annotation

Every metric field must include:

| Field                | Description  | Examples                                           |
| -------------------- | ------------ | -------------------------------------------------- |
| `source_type`        | Data origin  | web_search / web_fetch / analytics / manual_research / public_report |
| `source_year`        | Year of data | YYYY format (e.g., 2024)                           |
| `measurement_method` | How measured | Web search / Meta Ad Library / Amazon listing scrape / industry report |

Example:
```markdown
- Category Monthly Search Volume: 50,000
  - source_type: web_search
  - source_year: 2024
  - measurement_method: Estimated from Google Trends + Amazon search volume tools
```

## 4. Competitor Ad Analysis Table Format (Web-Research Based)

**CRITICAL**: This format must be used for all competitor ad analysis.

### Required Structure

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
| **Visual Style** | [Description: colors, imagery, layout, models, product placement] |
| **Landing Page** | [URL if available] |
| **Active Since** | [Date range from Ad Library] |
| **Critique** | [Strategic analysis: why it works/fails] |
| **Counter-Strategy** | [How to compete against this approach] |

Source: [URL to Meta Ad Library page or other source]
```

### Research Methods for Competitor Ads

| Method | Tool | What You Get |
|--------|------|-------------|
| Meta Ad Library search | WebFetch | Ad copy, format, active status, start date |
| TikTok Creative Center | WebSearch + WebFetch | Trending ad formats, popular hooks, engagement metrics |
| Google search for case studies | WebSearch | Industry analysis of competitor strategies |
| Competitor website analysis | WebFetch | Landing page copy, offers, funnel structure |
| Industry benchmark reports | WebSearch | CPM/CPC/CTR benchmarks by vertical |

### Rules

1. **One table per ad or ad group** — keep analyses granular and specific
2. **Quote actual ad copy** — use the exact text from the ad in "Primary Hook" and "CTA" fields
3. **Include source URL** — always link to the original source (Ad Library page, Creative Center, etc.)
4. **Describe visuals in text** — since images are not downloaded, describe visual elements thoroughly (colors, composition, models, product placement, text overlays)
5. **Always include Counter-Strategy** — every analysis must be actionable
6. **Required fields** — every table must include: Ad Format, Primary Hook, Critique, Counter-Strategy

### Valid Example

```markdown
Table 3: Levoit — Meta Ad Creative Analysis

| Dimension | Finding |
| :-------- | :------ |
| **Ad Format** | Video (15s) |
| **Platform** | Meta (Facebook Feed + Instagram Reels) |
| **Primary Hook** | "Breathe cleaner air in just 30 minutes" |
| **Value Proposition** | Fast air purification for immediate health benefits |
| **CTA** | "Shop Now — Free Shipping" |
| **Target Audience Signals** | Health-conscious parents, allergy sufferers, pet owners |
| **Visual Style** | Clean white background, product hero shot, before/after particle visualization, soft natural lighting |
| **Landing Page** | https://www.levoit.com/air-purifiers |
| **Active Since** | 2024-08 (ongoing) |
| **Critique** | Strong specificity ("30 minutes") creates urgency. Health angle resonates but lacks social proof. Free shipping CTA is standard — could differentiate with guarantee. |
| **Counter-Strategy** | Lead with clinical/certification proof points. Emphasize unique filtration technology. Add UGC testimonials to build trust layer competitor lacks. |

Source: Meta Ad Library — https://www.facebook.com/ads/library/?q=levoit
```

### Invalid Examples

- Missing source URL — every analysis must be traceable
- Generic critique ("good ad") — must be specific and actionable
- Missing Counter-Strategy — analysis without action recommendations is incomplete
- Combining multiple ads into one table — use separate tables for distinct creatives

## 5. Example Content Labeling

All example content must be explicitly labeled:

```markdown
Example Explanation (can be deleted):
- Correct: The core reason for current ad efficiency decline stems from incomplete signal pipeline
- Wrong: Internal Analysis
```

## 6. References Section

Must be included at document end with this format:

```markdown
## X. References

- [1] Meta Ad Library — [Competitor Ad Data] — https://facebook.com/ads/library/...
- [2] TikTok Creative Center — [Trend Data] — https://ads.tiktok.com/...
- [3] Amazon — [Listing/BSR Data] — https://amazon.com/...
- [4] Google Trends — [Search Interest Data] — https://trends.google.com/...
- [5] Client Provided Materials — [Product Catalog]
- [6] [Industry Report Name] — [Key Findings] — https://...
```

**CRITICAL**: All web sources must include the actual URL. Do not use placeholder URLs.

## 7. System State Analysis Mapping Block

For Meta-only reports, include this mapping block:

```text
# Engineering -> Guideline Mapping
#
# Internal   -> Data pipeline / System state
# External   -> Platform bidding environment / Industry trends
# Customer   -> User media behavior / Decision path
```

---

## Validation Checklist

### General Format
- [ ] Main title is conclusion-style (judgment, not category)
- [ ] All tables use `Table X:` numbering format
- [ ] Table numbers are globally incremented without duplicates
- [ ] All metrics include data source annotations
- [ ] References section exists at document end with URLs

### Competitor Ad Analysis
- [ ] Uses the standard analysis table format (Dimension | Finding)
- [ ] Each analysis includes source URL
- [ ] Visual elements described in text (colors, composition, layout)
- [ ] Each analysis includes Critique and Counter-Strategy
- [ ] Required fields present: Ad Format, Primary Hook, Critique, Counter-Strategy
- [ ] Ad copy is quoted exactly from source

### Data Sources
- [ ] All data gathered via WebSearch or WebFetch
- [ ] Sources are publicly accessible URLs
- [ ] Data recency noted (prefer last 6 months)
- [ ] Multiple sources cross-validated for key claims

### Final Validation
- [ ] Markdown renders correctly in local previewer
- [ ] All external links are valid
- [ ] Document is logically coherent (not copy-pasted fragments)
- [ ] No local filesystem paths in the report
