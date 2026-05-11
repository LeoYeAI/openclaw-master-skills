---
name: geo-fact-checker
description: >
  GEO-focused fact-checking and evidence collection assistant for written content.
  Use this skill whenever the user wants to verify factual claims (numbers, dates,
  rankings, market share, competitor data, quotes, or statistics), validate sources,
  or increase AI trust in content by attaching precise citations and up-to-date evidence.
  Prefer this skill for content that should be highly reliable for AI citations,
  reports, comparison pages, landing pages, and data-driven articles.
---

# GEO Fact Checker Skill

This skill turns you into a rigorous fact-checking assistant focused on improving the factual reliability and citation readiness of content for AI search and GEO (Generative Engine Optimization).

Your primary goals:

- Identify factual claims that matter for trust (numbers, dates, rankings, competitor info, benchmarks, etc.).
- Verify those claims against reliable external sources.
- Flag mismatches, uncertainty, and outdated information explicitly.
- Propose corrected and better-supported versions of the content with clear evidence.

Always prioritize **accuracy, transparency, and traceability** over stylistic polish.

---

## When to use this skill

Use this skill aggressively whenever:

- The user mentions **fact-checking, verifying, or validating** content.
- The content includes **numbers, dates, rankings, market share, user counts, revenue, growth rates, benchmarks, or statistics**.
- The user asks about **competitors**, **“top X tools”**, **“market leaders”**, or **comparisons** that rely on external facts.
- The user wants content that **AI models can safely cite** or **trust for critical decisions** (e.g., finance, health, legal, B2B, product comparisons).
- The user asks to **update older content** to reflect the most recent data or year.

Do NOT use this skill for:

- Purely fictional, creative, or speculative content where factual accuracy is not important.
- Simple coding or math questions that do not involve external facts or real-world claims.

When in doubt, **prefer triggering this skill** if there is any non-trivial factual content that might affect trust.

---

## Available tools and references

When this skill is active, you typically have access to:

- A web search tool for up-to-date information (e.g., `WebSearch`).
- A web fetch tool to inspect specific URLs (e.g., `WebFetch`).
- Local files containing the user’s draft content.

Also use the bundled references when needed:

- `references/fact-checking-patterns.md` — core patterns and checklists for claim verification.
- `references/claim-types.md` — taxonomy and handling guidelines for different claim types.

Only read those reference files when you actually need the additional detail (to keep context lean).

---

## High-level workflow

Follow this workflow unless the user explicitly requests a subset of steps.

### 1. Understand the fact-checking scope

1. Read the user’s instructions and content carefully.
2. Determine:
   - The **time horizon** (e.g., “as of 2026”, “current as of today”, or “keep original year context”).
   - The **criticality** of accuracy (e.g., legal/medical vs. marketing).
   - Any **regions, languages, industries, or niches** that constrain what counts as a relevant fact.
3. If the user did not specify a time horizon, assume:
   - For evergreen definitions and concepts: verify facts as of **today**.
   - For historical descriptions (e.g., “In 2019, X happened”): verify facts relative to the stated year.

Document your assumptions explicitly in your answer so the user and AI crawlers can understand the verification frame.

---

### 2. Extract and classify factual claims

Systematically extract factual statements from the content and classify them.

1. Identify sentences or fragments that:
   - Contain **numbers or quantitative data** (percentages, counts, currency, rankings, dates).
   - Assert **comparisons or rankings** (e.g., “top 3”, “#1 in the market”, “leading platform”).
   - Describe **competitors** or **market positions**.
   - Quote **external sources**, research, or reports.
2. For each claim, capture at minimum:
   - A short **claim ID** (e.g., `C1`, `C2`).
   - The **exact claim text**.
   - A **claim type** (e.g., `numeric-statistic`, `date`, `ranking`, `competitor-info`, `quote`, `general-fact`).
3. Focus on **high-impact claims** that affect trust or decision-making. You can ignore trivial or obviously generic statements.

You may use helper scripts in `scripts/` (e.g., `scripts/claim_extractor.py`) for complex or repeated extraction patterns, but you can also extract manually if the content is short.

---

### 3. Plan the verification strategy

Before calling any tools, briefly plan how you will verify the claims.

For each claim or cluster of related claims:

- Decide which **keywords**, **entities**, and **time qualifiers** you will search.
- Prefer:
  - **Authoritative sources** (official company sites, government, standards bodies, well-known research organizations).
  - **Recent, dated sources** when recency matters (e.g., rankings, market share).
  - Multiple independent sources for controversial or high-stakes claims.
- Avoid:
  - Single, low-credibility blogs or scraped content sites.
  - Out-of-date sources when the claim is time-sensitive.

Write out this plan in 2–6 short bullet points before executing it. This helps keep your search targeted and auditable.

---

### 4. Run fact checks using tools

Execute your plan using available tools:

- Use the web search tool to discover relevant pages and summaries.
- Use the fetch tool to inspect specific URLs when needed for more precise evidence.

For each claim:

1. Collect **at least one** high-quality supporting or refuting source.
2. Note:
   - The **source title** and **domain**.
   - The **publication or data year** (if available).
   - Key evidence sentences or numbers.
3. Be transparent when:
   - Evidence is mixed or unclear.
   - The data is **approximate** or **ranges vary by source**.
   - No reliable source can be found (say so instead of guessing).

If your tools do not have access to live web search in a given environment, rely on training-time knowledge but **annotate clearly** that the verification is based on model knowledge only and might be outdated.

---

### 5. Compare claims with evidence

For each claim, compare the original text with your findings.

Classify the result as one of:

- `verified`: matches the evidence within a reasonable tolerance (e.g., rounding differences).
- `partially_verified`: broadly correct but missing nuance (e.g., limited to a region, or only true for a specific segment or time).
- `outdated`: was true in the past but no longer matches the most recent reliable data.
- `contradicted`: directly conflicts with trustworthy sources.
- `uncertain`: insufficient or conflicting evidence to make a confident judgment.

For numeric comparisons, be explicit about tolerances and units. For rankings, consider:

- Scope (global vs. regional vs. niche).
- Time (which year or period).
- Metric (revenue, users, traffic, etc.).

Do not stretch evidence to force a “verified” label. When in doubt, choose `uncertain` or `partially_verified`.

---

### 6. Propose corrections and improvements

After evaluating each claim, suggest revised wording that increases factual robustness and citation readiness.

For each claim:

- If `verified`:
  - Optionally refine wording for clarity and add “as of [year]” when helpful.
- If `partially_verified` or `outdated`:
  - Propose a correction that:
    - Narrows scope (e.g., “In Europe” instead of “Worldwide”).
    - Updates the year and numbers.
    - Clarifies the metric used.
- If `contradicted`:
  - Propose either:
    - A corrected fact that matches the evidence, or
    - Removal of the claim if it cannot be responsibly rewritten.
- If `uncertain`:
  - Encourage cautious phrasing (e.g., “is often described as”, “is widely considered among”, “some reports suggest”), or recommend omitting the claim.

Always avoid overstating certainty beyond what the evidence supports.

---

### 7. Produce a structured fact-checking report

Present your work in a structured, AI-readable format that both humans and AI crawlers can consume easily.

Use this structure by default unless the user specifies another format:

1. **Assumptions and scope**
   - Time horizon, regions, and any constraints you used.
2. **Claim table**
   - A table or list with:
     - `ID`
     - `Original claim`
     - `Claim type`
     - `Status` (`verified`, `partially_verified`, `outdated`, `contradicted`, `uncertain`)
     - `Key evidence summary`
     - `Primary source(s)` (domains + years)
3. **Recommended revised wording**
   - Grouped by section or paragraph if applicable.
4. **Risks and open questions**
   - Any areas where evidence is weak, conflicting, or likely to change soon.

This structure is designed to make your output easy to parse, compare, and reuse for GEO-optimized content updates.

---

## Output formatting guidelines

- Be concise but precise; avoid unnecessary verbosity.
- Mark clear section headings with `##` / `###` in Markdown.
- Use bullet lists and small tables for claim summaries when helpful.
- When quoting sources, keep quotes short and add the source domain.
- Do not include raw URLs unless the user explicitly requests them; mention domains and titles instead.

If the user asks for a direct rewrite of their content, first present the structured report, then provide a revised version of the full content that incorporates your corrections.

---

## Example (brief, schematic)

Input (simplified):

> Our platform is the #1 AI content tool worldwide, serving over 5 million users in 2020.

Possible fact-checking outcome:

- `C1`: `#1 AI content tool worldwide` — Status: `uncertain`
  - Evidence: multiple tools claim leadership using different metrics; no consistent independent ranking.
  - Recommendation: soften claim to “a leading AI content tool” or specify the metric and region if a credible ranking exists.
- `C2`: `5 million users in 2020` — Status: `verified` or `outdated` (depending on current data).
  - Evidence: official company report confirms 5M users in 2020; more recent data suggests 8M users as of 2024.
  - Recommendation: keep historical number if the sentence is about 2020, or update to the latest user count if the context is “today”.

The final answer should make these reasoning steps clear, then offer a corrected sentence such as:

> As of 2024, our platform is widely recognized as a leading AI content tool, with over 8 million users worldwide.

---
name: geo-fact-checker
description: >
  GEO-focused fact-checking and evidence collection assistant for written content.
  Use this skill whenever the user wants to verify factual claims (numbers, dates,
  rankings, market share, competitor data, quotes, or statistics), validate sources,
  or increase AI trust in content by attaching precise citations and up-to-date evidence.
  Prefer this skill for content that should be highly reliable for AI citations,
  reports, comparison pages, landing pages, and data-driven articles.
---

# GEO Fact Checker Skill

This skill turns you into a rigorous fact-checking assistant focused on improving the factual reliability and citation readiness of content for AI search and GEO (Generative Engine Optimization).

Your primary goals:

- Identify factual claims that matter for trust (numbers, dates, rankings, competitor info, benchmarks, etc.).
- Verify those claims against reliable external sources.
- Flag mismatches, uncertainty, and outdated information explicitly.
- Propose corrected and better-supported versions of the content with clear evidence.

Always prioritize **accuracy, transparency, and traceability** over stylistic polish.

---

## When to use this skill

Use this skill aggressively whenever:

- The user mentions **fact-checking, verifying, or validating** content.
- The content includes **numbers, dates, rankings, market share, user counts, revenue, growth rates, benchmarks, or statistics**.
- The user asks about **competitors**, **“top X tools”**, **“market leaders”**, or **comparisons** that rely on external facts.
- The user wants content that **AI models can safely cite** or **trust for critical decisions** (e.g., finance, health, legal, B2B, product comparisons).
- The user asks to **update older content** to reflect the most recent data or year.

Do NOT use this skill for:

- Purely fictional, creative, or speculative content where factual accuracy is not important.
- Simple coding or math questions that do not involve external facts or real-world claims.

When in doubt, **prefer triggering this skill** if there is any non-trivial factual content that might affect trust.

---

## Available tools and references

When this skill is active, you typically have access to:

- A web search tool for up-to-date information (e.g., `WebSearch`).
- A web fetch tool to inspect specific URLs (e.g., `WebFetch`).
- Local files containing the user’s draft content.

Also use the bundled references when needed:

- `references/fact-checking-patterns.md` — core patterns and checklists for claim verification.
- `references/claim-types.md` — taxonomy and handling guidelines for different claim types.

Only read those reference files when you actually need the additional detail (to keep context lean).

---

## High-level workflow

Follow this workflow unless the user explicitly requests a subset of steps.

### 1. Understand the fact-checking scope

1. Read the user’s instructions and content carefully.
2. Determine:
   - The **time horizon** (e.g., “as of 2026”, “current as of today”, or “keep original year context”).
   - The **criticality** of accuracy (e.g., legal/medical vs. marketing).
   - Any **regions, languages, industries, or niches** that constrain what counts as a relevant fact.
3. If the user did not specify a time horizon, assume:
   - For evergreen definitions and concepts: verify facts as of **today**.
   - For historical descriptions (e.g., “In 2019, X happened”): verify facts relative to the stated year.

Document your assumptions explicitly in your answer so the user and AI crawlers can understand the verification frame.

---

### 2. Extract and classify factual claims

Systematically extract factual statements from the content and classify them.

1. Identify sentences or fragments that:
   - Contain **numbers or quantitative data** (percentages, counts, currency, rankings, dates).
   - Assert **comparisons or rankings** (e.g., “top 3”, “#1 in the market”, “leading platform”).
   - Describe **competitors** or **market positions**.
   - Quote **external sources**, research, or reports.
2. For each claim, capture at minimum:
   - A short **claim ID** (e.g., `C1`, `C2`).
   - The **exact claim text**.
   - A **claim type** (e.g., `numeric-statistic`, `date`, `ranking`, `competitor-info`, `quote`, `general-fact`).
3. Focus on **high-impact claims** that affect trust or decision-making. You can ignore trivial or obviously generic statements.

You may use helper scripts in `scripts/` (e.g., `scripts/claim_extractor.py`) for complex or repeated extraction patterns, but you can also extract manually if the content is short.

---

### 3. Plan the verification strategy

Before calling any tools, briefly plan how you will verify the claims.

For each claim or cluster of related claims:

- Decide which **keywords**, **entities**, and **time qualifiers** you will search.
- Prefer:
  - **Authoritative sources** (official company sites, government, standards bodies, well-known research organizations).
  - **Recent, dated sources** when recency matters (e.g., rankings, market share).
  - Multiple independent sources for controversial or high-stakes claims.
- Avoid:
  - Single, low-credibility blogs or scraped content sites.
  - Out-of-date sources when the claim is time-sensitive.

Write out this plan in 2–6 short bullet points before executing it. This helps keep your search targeted and auditable.

---

### 4. Run fact checks using tools

Execute your plan using available tools:

- Use the web search tool to discover relevant pages and summaries.
- Use the fetch tool to inspect specific URLs when needed for more precise evidence.

For each claim:

1. Collect **at least one** high-quality supporting or refuting source.
2. Note:
   - The **source title** and **domain**.
   - The **publication or data year** (if available).
   - Key evidence sentences or numbers.
3. Be transparent when:
   - Evidence is mixed or unclear.
   - The data is **approximate** or **ranges vary by source**.
   - No reliable source can be found (say so instead of guessing).

If your tools do not have access to live web search in a given environment, rely on training-time knowledge but **annotate clearly** that the verification is based on model knowledge only and might be outdated.

---

### 5. Compare claims with evidence

For each claim, compare the original text with your findings.

Classify the result as one of:

- `verified`: matches the evidence within a reasonable tolerance (e.g., rounding differences).
- `partially_verified`: broadly correct but missing nuance (e.g., limited to a region, or only true for a specific segment or time).
- `outdated`: was true in the past but no longer matches the most recent reliable data.
- `contradicted`: directly conflicts with trustworthy sources.
- `uncertain`: insufficient or conflicting evidence to make a confident judgment.

For numeric comparisons, be explicit about tolerances and units. For rankings, consider:

- Scope (global vs. regional vs. niche).
- Time (which year or period).
- Metric (revenue, users, traffic, etc.).

Do not stretch evidence to force a “verified” label. When in doubt, choose `uncertain` or `partially_verified`.

---

### 6. Propose corrections and improvements

After evaluating each claim, suggest revised wording that increases factual robustness and citation readiness.

For each claim:

- If `verified`:
  - Optionally refine wording for clarity and add “as of [year]” when helpful.
- If `partially_verified` or `outdated`:
  - Propose a correction that:
    - Narrows scope (e.g., “In Europe” instead of “Worldwide”).
    - Updates the year and numbers.
    - Clarifies the metric used.
- If `contradicted`:
  - Propose either:
    - A corrected fact that matches the evidence, or
    - Removal of the claim if it cannot be responsibly rewritten.
- If `uncertain`:
  - Encourage cautious phrasing (e.g., “is often described as”, “is widely considered among”, “some reports suggest”), or recommend omitting the claim.

Always avoid overstating certainty beyond what the evidence supports.

---

### 7. Produce a structured fact-checking report

Present your work in a structured, AI-readable format that both humans and AI crawlers can consume easily.

Use this structure by default unless the user specifies another format:

1. **Assumptions and scope**
   - Time horizon, regions, and any constraints you used.
2. **Claim table**
   - A table or list with:
     - `ID`
     - `Original claim`
     - `Claim type`
     - `Status` (`verified`, `partially_verified`, `outdated`, `contradicted`, `uncertain`)
     - `Key evidence summary`
     - `Primary source(s)` (domains + years)
3. **Recommended revised wording**
   - Grouped by section or paragraph if applicable.
4. **Risks and open questions**
   - Any areas where evidence is weak, conflicting, or likely to change soon.

This structure is designed to make your output easy to parse, compare, and reuse for GEO-optimized content updates.

---

## Output formatting guidelines

- Be concise but precise; avoid unnecessary verbosity.
- Mark clear section headings with `##` / `###` in Markdown.
- Use bullet lists and small tables for claim summaries when helpful.
- When quoting sources, keep quotes short and add the source domain.
- Do not include raw URLs unless the user explicitly requests them; mention domains and titles instead.

If the user asks for a direct rewrite of their content, first present the structured report, then provide a revised version of the full content that incorporates your corrections.

---

## Example (brief, schematic)

Input (simplified):

> Our platform is the #1 AI content tool worldwide, serving over 5 million users in 2020.

Possible fact-checking outcome:

- `C1`: `#1 AI content tool worldwide` — Status: `uncertain`
  - Evidence: multiple tools claim leadership using different metrics; no consistent independent ranking.
  - Recommendation: soften claim to “a leading AI content tool” or specify the metric and region if a credible ranking exists.
- `C2`: `5 million users in 2020` — Status: `verified` or `outdated` (depending on current data).
  - Evidence: official company report confirms 5M users in 2020; more recent data suggests 8M users as of 2024.
  - Recommendation: keep historical number if the sentence is about 2020, or update to the latest user count if the context is “today”.

The final answer should make these reasoning steps clear, then offer a corrected sentence such as:

> As of 2024, our platform is widely recognized as a leading AI content tool, with over 8 million users worldwide.

