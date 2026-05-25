---
name: consulting-report-search
description: >-
  Consulting and industry report search and QA skill that prioritizes iResearch
  free reports. Use for consulting report search, industry report QA, iResearch
  report lookup, and market research report search.
---

# Consulting Report Search

## Description

Search and question-answering skill for consulting reports, industry reports, and market research reports. By default, it prioritizes free iResearch reports, uses the iResearch list API for primary recall, then uses QuestMobile public reports as the secondary source. Results must always show iResearch first and QuestMobile second. The search workflow now supports deeper QuestMobile pagination and grouped output rendering, so mixed-source results can be shown as fixed source sections with iResearch first.

Within each source, the default ranking mode is now newest-first, then relevance. The default sort direction is descending, so newer reports appear before older ones. If needed, agents can switch to relevance-first with an explicit CLI flag, or override the direction explicitly. If the user query itself contains a year such as `2024`, `2025`, or `2026`, ranking should instead prioritize year signals in the report title first, then report relevance, then publication time, and all three dimensions should be treated in descending order.

## Activation Keywords

- 咨询报告搜索
- 行业报告问答
- 艾瑞报告
- 艾瑞咨询
- 市场研究报告
- iresearch report
- report search
- market research report

## Tools Used

- exec: Run the bundled script to fetch iResearch and QuestMobile search results and detail pages
- read: Load the skill reference file for source behavior, encoding notes, and parsing rules
- write: Save search results or answer drafts when needed
- browser or web search tools: Use browser-based or available web-search capability when both primary sources fail to return reports

## Installation

No extra third-party packages are required. The script uses only the Python standard library.

For iResearch specifically, the logical default `pageSize` is 100 items. However, the current live public endpoint can fail when asked for 100 items in a single backend call, so the bundled script transparently splits large iResearch fetches into multiple smaller requests while still preserving the user-facing default of 100.

### Prerequisites

- Network access to https://www.iresearch.com.cn/ and https://report.iresearch.cn/
- Network access to https://www.questmobile.com.cn/research/reports/
- Python 3.10+ to run the script

## Usage Patterns

### Search Reports

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  search "AI营销" --pages 8 --limit 20 --sort-by recency --sort-order desc --grouped --format markdown
```

Fetch multiple pages from the iResearch free report feed, then pull multiple QuestMobile pages from its public article-list API only as fallback coverage. The default search depth is now 8 pages of iResearch results with a logical page size of 100, so the script starts from a much larger newest-first window before falling back. If the initial iResearch window still does not produce enough relevant matches, the script now automatically expands the iResearch search deeper, up to 20 logical pages in total, before QuestMobile is allowed to fill remaining slots. Final ranking must still keep all iResearch matches ahead of QuestMobile matches, and grouped output should render iResearch as the first section and QuestMobile as the second section.

By default, results are sorted by publish time first and relevance second within each source. The default sort direction is `desc`. Use `--sort-by relevance` only when the user explicitly prefers stronger keyword matching over freshness.

If the query contains a year, override the normal within-source sort and use: title year, then relevance, then publication time. All three are descending. This helps queries like `2025 AI营销` or `2024 飞行汽车` prefer reports whose titles explicitly carry the requested year.

Markdown output also shows the active sort mode and any active `--since` filter at the top of the result block.

Every returned report should explicitly include a report link. This is a hard requirement. In structured output, use the `report_link` field. In Markdown output, show a `Report Link` line for each report. If a source item does not have a valid public report link, it should be dropped from list/search output instead of being returned as a bare title.

When both sources have matches, the mixed-source search now tries to fill the requested result window with as many relevant iResearch reports as possible first. If the initial newest window is not enough, it automatically keeps paging deeper into iResearch before QuestMobile is used. QuestMobile should only fill the remaining slots when iResearch alone still cannot satisfy the requested result count.

If the user explicitly wants only iResearch, use `--iresearch-only`. This is the preferred flag for pure iResearch report collection workflows; `--no-questmobile` remains available as a lower-level compatibility switch.

### Fetch Report Details

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  detail freport.4694 --pages 8 --include-images --format markdown
```

Read the report detail page and return the summary, catalog, chart catalog, online reader link, and image links from the reader page.

The detail workflow should now also return a conservative interpretation, evidence boundary note, and structured outline sections derived from the public introduction, meta description, and public catalog. The interpretation should read like a short answer-oriented summary instead of a raw evidence dump.

QuestMobile detail pages are also supported through full URLs or `qm.<id>` identifiers.

### Answer a Question Against One Report

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  answer freport.4794 "这份报告主要讲什么？" --pages 8 --include-images --format markdown
```

Use `answer` when the user is asking a concrete question about one report rather than requesting a raw detail dump.

The answer mode should:

- fetch the same public detail evidence as `detail`
- generate a conservative answer grounded in public summary, outline sections, and chart catalog
- return explicit evidence snippets
- keep the evidence boundary visible
- include report and online-reading links for manual verification

### Browse Recent Free Reports

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  list --pages 2 --page-size 100 --format markdown
```

Use this to inspect the recent free-report pool before deciding which reports to summarize or use for QA.

### Search Reports with Explicit Source Groups

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  search "AI应用层" --pages 8 --limit 12 --sort-by recency --sort-order desc --since 2025-01-01 --grouped --format json
```

Use grouped output when you need a stable source-layered rendering format. This keeps iResearch and QuestMobile separated instead of interleaving them in a single list.

Use `--since` when the user explicitly wants only recent reports, for example limiting the result window to 2025 and later.

The hidden `--last-id` cursor parameter is deprecated for normal use and should only be used for debugging historical iResearch cursor windows.

## Instructions for Agents

### Step 1: Classify the Request

First determine whether the user wants:

- Report search
- Topic filtering or comparison
- QA grounded in one or more reports
- Lead collection for relevant reports

If the request involves industry status, trends, market size, cases, figures, or charts, start with iResearch by default.

### Step 2: Search iResearch Free Reports First

Always use the bundled script first instead of jumping directly to broad web search:

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  search "<query>" --pages 8 --limit 20 --format json
```

Execution requirements:

- Fetch a deep newest-first iResearch window by default; the current default is 8 logical pages with pageSize 100
- If relevant iResearch matches are still insufficient, automatically expand deeper up to 20 logical pages before falling back to QuestMobile
- Present iResearch matches first in the final answer
- Prefer returning as many relevant iResearch reports as possible before using QuestMobile to fill any remaining slots
- If the query contains a year, prioritize title-year signals first, then relevance, then publication time, all in descending order
- Rank results within each source by newest publication time first, then relevance, with `--sort-order desc` as the default unless the user explicitly asks for a different order
- Include a report link for every returned report; do not return bare titles without a clickable destination
- Treat the report link as a hard requirement; drop linkless items from list/search output and fail detail-style flows if a valid public report link is unavailable
- If the user specifies an industry, add `--industry`
- If the user wants only newer reports, add `--since YYYY-MM-DD`
- Do not use `--last-id` in normal workflows; it is a deprecated debug-only cursor override
- Use QuestMobile only as the secondary source after iResearch results have been gathered
- Use `--iresearch-only` when the user explicitly wants only iResearch reports
- Prefer `--grouped` when the answer contains both iResearch and QuestMobile results

### Step 3: Use QuestMobile as the Secondary Source

If iResearch results are too sparse, or if the user asks for broader coverage, use the same search command without disabling QuestMobile:

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  search "<query>" --pages 8 --limit 8 --sort-by recency --sort-order desc --format json
```

Rules for QuestMobile usage:

- Never place QuestMobile above iResearch in the final result order
- Use QuestMobile to fill gaps or broaden topical coverage only after iResearch results have been exhausted for the requested window
- When both sources match, present them in separate source layers rather than mixing them together
- In mixed-source result lists, keep QuestMobile after all iResearch entries and only use it to fill the remaining slots when iResearch results are insufficient
- Use multiple QuestMobile pages when broader coverage is needed instead of relying on the default landing page only

### Step 4: Pull Detail Evidence for QA

If the user wants a summary, explanation, or grounded answer instead of just report titles, fetch details for the top 1 to 3 candidate reports:

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  detail <report-id-or-url> --pages 8 --include-images --format json
```

Prefer these fields as answer evidence:

- `summary`
- `interpretation`
- `evidence_boundary`
- `outline_sections`
- `catalog`
- `chart_catalog`
- `industry`
- `published_at`
- `online_read_url`
- `source`

If the user asks a direct question about one chosen report, prefer the dedicated answer flow:

```bash
python collection/skills/consulting-report-search/scripts/iresearch_report_search.py \
  answer <report-id-or-url> "<question>" --pages 8 --include-images --format json
```

Prefer these fields from `answer` output when responding:

- `answer`
- `evidence`
- `evidence_boundary`
- `verification_links`
- `report_link`
- `online_read_url`

QuestMobile detail pages can additionally provide:

- article intro text
- section headings
- image URLs from the report body

For iResearch specifically, the preferred interpretation stack is:

1. `summary` from the public report introduction
2. detail-page meta description when it contains a richer synopsis
3. `outline_sections` extracted from the public catalog
4. online reader image links for manual page-level verification when needed

### Step 5: State the Evidence Boundary Clearly

If only the summary, catalog, and chart catalog are available, restrict the answer to:

- What topics the report covers
- The rough research scope and chapter structure
- Which cases, trends, or indicators the report appears to cover

Do not convert the table of contents into claimed report conclusions. If the user asks for exact data points, page-level evidence, or chart-specific content:

- Explicitly say that current evidence comes mainly from the summary and catalog
- Use the `interpretation` field for a conservative reading of what the report is about, but do not treat it as a replacement for page-level evidence
- Use the `answer` mode when the user asks a concrete report-specific question, especially around summary, chapters, chart/data coverage, timing, source, or report links
- Provide the online reader link
- Use reader-page image links for page-by-page verification if needed

### Step 6: Expand Only When iResearch Is Not Enough

Use other sources only when:

- iResearch has no relevant report
- Free-report information is not enough to answer the question
- The user explicitly asks for multi-source comparison

If both iResearch and QuestMobile return no usable reports, switch to web search as the fallback discovery path. Prefer targeted report-page searches such as:

- `site:iresearch.cn/report <query> 报告`
- `site:questmobile.com.cn/research/report <query> 报告`
- `site:iresearch.com.cn <query> 艾瑞 报告`
- `site:questmobile.com.cn <query> QuestMobile 报告`

When web search finds a concrete report page URL, feed that URL back into the normal detail flow when possible instead of summarizing the search snippet alone.

When expanding, present sources in separate layers:

1. iResearch reports
2. QuestMobile reports
3. Web-search discovered report pages
4. Other public sources

Do not mix secondary sources into the first section.

## Context Files

### references/iresearch-api.md

Contains source parameters, pagination behavior, encoding notes, detail-page anchors, and parsing considerations for both iResearch and QuestMobile. Read it only when adjusting the script or debugging extraction issues.

## Error Handling

### Empty Search Results

```text
If search returns no reports:
  1. Increase --pages to confirm the result is not caused by shallow pagination
  2. Relax the query and keep only the core topic words
  3. Check whether QuestMobile has relevant public reports
  4. If both iResearch and QuestMobile still return nothing, switch to web search using report-focused site queries
  5. Prefer concrete report-page URLs over generic articles or landing pages
  6. Tell the user when the final candidates were found through web search fallback rather than the direct source APIs
```

### Garbled Detail Page or Missing Fields

```text
If detail parsing looks garbled:
  1. Confirm the page is decoded as gb18030 instead of forcing UTF-8
  2. For QuestMobile, confirm the page is decoded as UTF-8 and that the public HTML still exposes metadata blocks
  3. Check the HTML anchors documented in references/iresearch-api.md
  4. If only a few fields are missing, return the available fields instead of failing completely
```

### Only Summary and Catalog Are Available

```text
If the user asks for exact findings but only summary/catalog are available:
  1. Explain the current evidence boundary
  2. Provide the online reader link or image-page links
  3. Give a conservative answer grounded in visible evidence instead of inventing findings
```

## Configuration

### Optional Parameters

```bash
--pages 8
--page-size 100
--limit 5
--industry 广告营销
--sort-by recency
--sort-order desc
--since 2025-01-01
--include-images
--no-questmobile
--iresearch-only
--grouped
--format json
```

## Limitations

- This skill prioritizes iResearch free reports and uses QuestMobile public reports as secondary coverage
- It does not cover private content that requires login or payment
- iResearch detail pages reliably expose the summary, catalog, chart catalog, and online reader entry point
- The hidden `--last-id` override can intentionally force older iResearch windows, so it should be treated as a debug-only compatibility flag
- QuestMobile search coverage depends on the public `article-list` API remaining stable
- The online reader is an image stream rather than structured text, so page-by-page verification is more expensive

## Best Practices

1. Search first, then answer. Do not give industry conclusions before locating reports.
2. Put iResearch results in the first section and QuestMobile in the second section. Use grouped output when both sources are present.
3. Ground factual claims in the summary, catalog, chart catalog, or article intro instead of over-inferring.
4. When recommending several reports, rank iResearch first, then rank within each source by recency and relevance by default. Keep `--sort-order desc` unless the user explicitly wants the oldest reports first. Use `--sort-by relevance` only when freshness is less important than lexical match.
5. If both built-in sources fail, do not stop at "no results". Run a web-search fallback with `site:` constraints to recover concrete report pages.

## Examples

### Example 1: Search for AI Marketing Reports

```text
User: Help me find several consulting reports about AI marketing, prioritizing iResearch.

Agent Process:
1. Run the search subcommand against the iResearch free-report pool for "AI营销"
2. Keep QuestMobile enabled as the secondary source
3. Return the top relevant reports with iResearch first and QuestMobile second
4. Use grouped output so the source boundary is obvious

Agent: I will search the iResearch free-report pool first, then use QuestMobile as secondary coverage if needed. Results will still be presented with iResearch first in a grouped layout.
```

### Example 3: Fall Back to Web Search When Built-in Sources Miss

```text
User: Help me find reports about a niche topic, but the direct source search returns nothing.

Agent Process:
1. Search iResearch first
2. Search QuestMobile second
3. If both return no usable reports, switch to web search with report-focused site constraints
4. Prefer concrete report detail URLs over homepages or generic news pages
5. If a valid report URL is found, pass it back through the detail workflow or present it as a fallback-discovered report

Agent: The direct source APIs did not return a usable report for this query, so I will fall back to web search using report-focused site filters and return any concrete report pages I can verify.
```

### Example 2: Answer a Question Grounded in a Report

```text
User: According to iResearch reports, which application directions does AI marketing mainly cover?

Agent Process:
1. Search for "AI营销"
2. Run detail on the most relevant report
3. If iResearch evidence is insufficient, inspect one QuestMobile report as a secondary source
4. Summarize application directions from the summary, catalog, and available detail evidence
5. State which parts come from iResearch and which parts come from QuestMobile

Agent: Based on the summary and catalog of iResearch's "2024 China AI Applications in Marketing Industry Report," the currently supported application directions include data-driven decision support, content production, organizational and process transformation, and benchmark case analysis. QuestMobile can be used as a secondary source to extend public narrative coverage, but iResearch remains the primary evidence layer.
```

## Resources

- https://www.iresearch.com.cn/report.shtml
- https://www.iresearch.com.cn/api/products/GetReportList
- https://www.questmobile.com.cn/research/reports/
- ./references/iresearch-api.md

## Related Skills

- arxiv-search: Handles academic paper search rather than consulting or industry reports
- news-search: Handles news search and can be used as background supplementation