---
name: content-refresher
version: "4.1.0"
description: 'Refresh old blog posts and outdated content with current statistics, new information, and freshness signals to restore search rankings. Use when the user asks to "update old content", "refresh content", "content is outdated", "improve declining rankings", "revive old blog posts", "traffic is declining on this page", "rankings dropped for this article", or "this post is outdated". For writing new content from scratch, see seo-content-writer. For auditing without rewriting, see on-page-seo-auditor.'
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
metadata:
  author: aaron-he-zhu
  version: "4.1.0"
  geo-relevance: "medium"
  tags:
    - seo
    - geo
    - content refresh
    - content update
    - outdated content
    - content decay
    - ranking recovery
    - content optimization
    - content-update
    - content-decay
    - evergreen-content
    - content-freshness
    - content-revival
    - refresh-content
    - update-statistics
    - republishing
    - content-lifecycle
  triggers:
    - "update old content"
    - "refresh content"
    - "content is outdated"
    - "improve declining rankings"
    - "revive old blog posts"
    - "content decay"
    - "ranking dropped"
    - "this post is outdated"
    - "traffic is declining on this page"
    - "rankings dropped for this article"
---

# Content Refresher


> **[SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills for SEO + GEO · [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)

<details>
<summary>Browse all 20 skills</summary>

**Research** · [keyword-research](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/SKILL.md) · [competitor-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/competitor-analysis/SKILL.md) · [serp-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/serp-analysis/SKILL.md) · [content-gap-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/SKILL.md)

**Build** · [seo-content-writer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/seo-content-writer/SKILL.md) · [geo-content-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md) · [meta-tags-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/SKILL.md) · [schema-markup-generator](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/schema-markup-generator/SKILL.md)

**Optimize** · [on-page-seo-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/on-page-seo-auditor/SKILL.md) · [technical-seo-checker](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/SKILL.md) · [internal-linking-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/internal-linking-optimizer/SKILL.md) · **content-refresher**

**Monitor** · [rank-tracker](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/rank-tracker/SKILL.md) · [backlink-analyzer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/backlink-analyzer/SKILL.md) · [performance-reporter](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/performance-reporter/SKILL.md) · [alert-manager](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/alert-manager/SKILL.md)

**Cross-cutting** · [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md) · [domain-authority-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/domain-authority-auditor/SKILL.md) · [entity-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/SKILL.md) · [memory-management](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md)

</details>

This skill helps identify and revitalize outdated content to reclaim lost rankings and traffic. It analyzes content freshness, identifies update opportunities, and guides the refresh process for maximum SEO and GEO impact.

## When to Use This Skill

- Content has lost rankings or traffic over time
- Statistics and information are outdated
- Competitors have published better content
- Content needs updating for a new year
- Industry changes require content updates
- Adding new sections to existing content
- Converting old content for GEO optimization

## What This Skill Does

1. **Freshness Analysis**: Identifies outdated content needing updates
2. **Performance Tracking**: Finds content with declining traffic
3. **Gap Identification**: Spots missing information competitors have
4. **Update Prioritization**: Ranks content by refresh potential
5. **Refresh Recommendations**: Provides specific update guidance
6. **GEO Enhancement**: Updates content for AI citation potential
7. **Republishing Strategy**: Advises on date and promotion tactics

## How to Use

### Identify Content to Refresh

```
Find content on [domain] that needs refreshing
```

```
Which of my blog posts have lost the most traffic?
```

### Refresh Specific Content

```
Refresh this article for [current year]: [URL/content]
```

```
Update this content to outrank [competitor URL]: [your URL]
```

### Content Refresh Strategy

```
Create a content refresh strategy for [domain/topic]
```

## Data Sources

> See [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md) for tool category placeholders.

**With ~~analytics + ~~search console + ~~SEO tool connected:**
Claude can automatically pull historical traffic trends from ~~analytics, fetch impression and ranking data from ~~search console, retrieve keyword position history from ~~SEO tool, and identify content with declining performance. This enables data-driven refresh prioritization.

**With manual data only:**
Ask the user to provide:
1. Traffic data or screenshots showing performance trends
2. Ranking screenshots or history for key pages
3. Content publish dates and last update dates
4. List of pages the user suspects need refreshing

Proceed with the analysis using provided data. Note in the output which findings are from automated data vs. manual review.

## Instructions

When a user requests content refresh help:

1. **CORE-EEAT Quick Score — Identify Weak Dimensions**

   Before refreshing, run a quick CORE-EEAT assessment to focus effort on the weakest areas. Reference: [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)

   ```markdown
   ### CORE-EEAT Quick Assessment

   **Content**: [title or URL]
   **Content Type**: [type]

   Rapidly score each dimension (estimate 0-100):

   | Dimension | Quick Score | Key Weakness | Refresh Priority |
   |-----------|-----------|--------------|-----------------|
   | C — Contextual Clarity | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | O — Organization | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | R — Referenceability | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | E — Exclusivity | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | Exp — Experience | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | Ept — Expertise | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | A — Authority | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | T — Trust | [X]/100 | [main issue] | 🔴/🟡/🟢 |

   **Weakest Dimensions** (focus refresh here):
   1. [Dimension] — [what needs fixing]
   2. [Dimension] — [what needs fixing]

   **Refresh Strategy**: Focus on 🔴 dimensions first, then 🟡.

   _For full 80-item audit, use [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md)_
   ```

2. **Identify Content Refresh Candidates**

   ```markdown
   ## Content Refresh Analysis
   
   ### Refresh Candidate Identification
   
   **Criteria for Content Refresh**:
   - Published more than 6 months ago
   - Contains dated information (years, statistics)
   - Declining traffic trend
   - Lost keyword rankings
   - Outdated references or broken links
   - Missing topics competitors now cover
   - No GEO optimization
   
   ### Content Audit Results
   
   | Content | Published | Last Updated | Traffic Trend | Priority |
   |---------|-----------|--------------|---------------|----------|
   | [Title 1] | [date] | [date] | ↓ -45% | 🔴 High |
   | [Title 2] | [date] | Never | ↓ -30% | 🔴 High |
   | [Title 3] | [date] | [date] | ↓ -20% | 🟡 Medium |
   | [Title 4] | [date] | [date] | → 0% | 🟡 Medium |
   
   ### Refresh Prioritization Matrix
   
   ```
   High Traffic + High Decline = 🔴 Refresh Immediately
   High Traffic + Low Decline = 🟡 Schedule Refresh
   Low Traffic + High Decline = 🟡 Evaluate & Decide
   Low Traffic + Low Decline = 🟢 Low Priority
   ```
   ```

3. **Analyze Individual Content for Refresh**

   ```markdown
   ## Content Refresh Analysis: [Title]
   
   **URL**: [URL]
   **Published**: [date]
   **Last Updated**: [date]
   **Word Count**: [X]
   
   ### Performance Metrics
   
   | Metric | 6 Mo Ago | Current | Change |
   |--------|----------|---------|--------|
   | Organic Traffic | [X]/mo | [X]/mo | [+/-X]% |
   | Avg Position | [X] | [X] | [+/-X] |
   | Impressions | [X] | [X] | [+/-X]% |
   | CTR | [X]% | [X]% | [+/-X]% |
   
   ### Keywords Analysis
   
   | Keyword | Old Position | Current Position | Change |
   |---------|--------------|------------------|--------|
   | [kw 1] | [X] | [X] | ↓ [X] |
   | [kw 2] | [X] | [X] | ↓ [X] |
   | [kw 3] | [X] | [X] | ↓ [X] |
   
   ### Why This Content Needs Refresh
   
   1. **Outdated information**: [specific examples]
   2. **Competitive gap**: [what competitors added]
   3. **Missing topics**: [new subtopics to cover]
   4. **SEO issues**: [current optimization problems]
   5. **GEO potential**: [AI citation opportunities]
   ```

4. **Identify Specific Updates Needed**

   ```markdown
   ## Refresh Requirements
   
   ### Outdated Elements
   
   | Element | Current | Update Needed |
   |---------|---------|---------------|
   | Year references | "[old year]" | Update to [current year] |
   | Statistics | "[old stat]" | Find current data |
   | Tool mentions | "[old tool]" | Add newer tools |
   | Links | [X] broken | Fix or replace |
   | Screenshots | Outdated UI | Recapture |
   
   ### Missing Information
   
   **Topics competitors now cover that you don't**:
   
   | Topic | Competitor Coverage | Words Needed | Priority |
   |-------|---------------------|--------------|----------|
   | [Topic 1] | 3/5 competitors | ~300 words | High |
   | [Topic 2] | 2/5 competitors | ~200 words | Medium |
   | [Topic 3] | 4/5 competitors | ~400 words | High |
   
   ### SEO Updates Needed
   
   - [ ] Update title tag with current year
   - [ ] Refresh meta description
   - [ ] Add new H2 sections for [topics]
   - [ ] Update internal links to newer content
   - [ ] Add FAQ section for featured snippets
   - [ ] Refresh images and add new alt text
   
   ### GEO Updates Needed
   
   - [ ] Add clear definition at start
   - [ ] Include quotable statistics with sources
   - [ ] Add Q&A formatted sections
   - [ ] Update sources with current citations
   - [ ] Create standalone factual statements
   ```

5. **Create Refresh Plan** — Structural changes, content additions, statistics/links/images to update

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the full refresh plan template (Step 5).

6. **Write Refresh Content** — Updated introduction, new sections, refreshed statistics, new FAQ section

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the refresh content writing template (Step 6).

7. **Optimize for GEO During Refresh** — Clear definitions, quotable statements, Q&A sections, updated citations

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the GEO enhancement template (Step 7).

8. **Generate Republishing Strategy** — Date strategy (update/add "last updated"/keep original), technical implementation, promotion plan

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the republishing strategy template (Step 8).

9. **Create Refresh Report** — Summary of changes, updates completed, expected outcomes, next review date

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the refresh report template (Step 9).

## Validation Checkpoints

### Input Validation
- [ ] Target content URL or title clearly identified
- [ ] Historical performance data available (traffic trends, rankings)
- [ ] Content publish/update dates known
- [ ] If comparing to competitors, competitor URLs provided

### Output Validation
- [ ] Every recommendation cites specific data points (not generic advice)
- [ ] Outdated elements identified with specific examples and replacement data
- [ ] All suggested additions include word counts and section locations
- [ ] Source of each data point clearly stated (~~analytics data, ~~search console, ~~SEO tool, user-provided, or estimated)

## Example

> **Reference**: See [references/refresh-example.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-example.md) for a full worked example (cloud hosting refresh) and the comprehensive content refresh checklist.

## Tips for Success

1. **Prioritize by ROI** - Refresh high-potential content first
2. **Don't just add dates** - Make substantial improvements
3. **Beat competitors** - Add what they have and more
4. **Track results** - Monitor ranking changes post-refresh
5. **Schedule regular audits** - Check content health quarterly
6. **Optimize for GEO** - Every refresh is a GEO opportunity

> **Reference data**: For content decay signal taxonomy, lifecycle stages, refresh vs. rewrite decision framework, and update strategy by content type, see [references/content-decay-signals.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/content-decay-signals.md).

## Reference Materials

- [Content Decay Signals](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/content-decay-signals.md) — Decay indicators, lifecycle stages, and refresh triggers by content type
- [Refresh Templates](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) — Detailed output templates for steps 5-9 (refresh plan, content writing, GEO enhancement, republishing, report)
- [Refresh Example & Checklist](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-example.md) — Full worked example and pre/post-refresh checklist

## Related Skills

- [content-gap-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/SKILL.md) — Find what to add
- [seo-content-writer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/seo-content-writer/SKILL.md) — Write new sections
- [geo-content-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md) — Enhance for AI
- [on-page-seo-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/on-page-seo-auditor/SKILL.md) — Audit refreshed content
- [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md) — Full 80-item CORE-EEAT audit

