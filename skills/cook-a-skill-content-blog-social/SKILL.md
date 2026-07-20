---
name: auto-content-blog
description: >
  Full end-to-end SEO + GEO content creation pipeline for crypto/Web3 teams.
  Trigger this skill when the user wants to: write a blog post or article, research
  keywords, generate a content brief or outline, mine community comments for UGC insights,
  optimize content for SEO or AI search engines (GEO), score or audit an existing article,
  or check if writing sounds AI-generated.
  Also trigger automatically at the start of every new session to scan X for trending
  topics relevant to the user's project spec — propose hot keywords before the user asks.
  Accepts a project spec .md file as primary input. Also works with plain keyword or topic.
  Run all stages in sequence when starting from scratch. Enter mid-pipeline if user
  provides an existing draft or only asks for one stage.
---

# Auto Content blog

End-to-end pipeline: trending topic → keyword research → brief → UGC enrichment → human-style draft → visual & link enrichment → SEO + GEO optimization → scored QA report.

## Pipeline

```
[0]   X TREND MONITOR   → auto-run on session start, propose hot keywords
[1]   KEYWORD RESEARCH  → scored, data-backed selection
[2]   CONTENT BRIEF     → outline + keyword map + UGC insertion points
[3]   UGC ENRICHMENT    → mine comments → ready-to-paste blog sections
[4]   DRAFT             → human-style, data-backed, zero AI patterns
[4.5] VISUAL & LINKS    → data charts (matplotlib) + inline hyperlinks on every citation
[5]   SEO + GEO         → on-page checklist + AI-bot-friendly formatting
[6]   QA REPORT         → rubric score + publish verdict
```

Enter at any stage. Run all stages from scratch. Start at Stage 5 for existing drafts.

**Quick commands:**
- `run full pipeline` → Stage 0 → Stage 6
- `start from stage [N]` → enter at any stage
- `score my draft` → Stage 5 → Stage 6
- `enrich my draft` → Stage 4.5 only (charts + links on existing draft)

**Reference files** (read when detail is needed):
- `references/scoring-rubrics.md` — all scoring tables (trend, keyword, UGC, SEO, GEO)
- `references/ai-patterns-blacklist.md` — full list of AI phrases to never write
- `references/output-templates.md` — exact output format for each stage
- `references/example-run.md` — real example: keyword "what is liquid staking"

---

## Inputs

Required: `project_spec` (.md) + `keyword_or_topic`
Optional: `ugc_urls` (skip Stage 3 if absent), `blog_draft`, `language` (default: English), `word_count` (default: 1500–2000), `tone` (default: auto-detect from spec)

If `project_spec` is missing: stop and ask for it before starting.

---

## Stage 0 — X Trend Monitor

**Run automatically at the start of every new session, before the user says anything.**

1. Parse `project_spec.md` → extract: domain/niche, audience, product themes, competitor names
2. Run web searches (fill in values from spec):
   - `site:x.com [domain keyword] -filter:replies`
   - `[domain keyword] trending twitter 2025`
   - `[domain keyword] discussion OR debate twitter`
   - `[competitor name] twitter sentiment 2025`
   - `crypto twitter trending today`
   - `[domain keyword] CT crypto twitter discussion`
3. Score each topic → see `references/scoring-rubrics.md` Stage 0
4. Keep top 3. Output Trend Alert before any user message → see `references/output-templates.md` Stage 0

Fallback if web search off: skip, say "Stage 0 unavailable. Provide a keyword to start Stage 1."
Fallback if no trends found: list 3 evergreen topics from spec context.

---

## Stage 1 — Keyword Research

1. Generate 8–12 seed keywords: head terms, mid-tail, long-tail question variants
2. For each seed, run:
   - `google trends [keyword] 2025` → direction
   - `site:x.com [keyword]` + `[keyword] trending twitter 2025` → buzz + debate angle
   - `[keyword] search volume 2025` + `ubersuggest [keyword]` → volume estimate
   - Search `[keyword]` → extract People Also Ask + Related Searches
3. Score using rubric → see `references/scoring-rubrics.md` Stage 1
4. Select top 1 = primary, next 5–8 = secondary/LSI. Label volume as `[estimated]`.
5. Ask once: "Do you have an Ahrefs or SEMrush API key?" Use if provided.
6. Output → see `references/output-templates.md` Stage 1

Edge cases: keyword too broad → suggest 3–5 long-tail alternatives. Doesn't match spec → warn + confirm.

---

## Stage 2 — Content Brief & Outline

1. Pick flow pattern:
   - Problem → Solution | What → Why → How | Comparison | Journey | Argument
2. Map every long-tail keyword to H2, H3, or FAQ entry. No section without a keyword anchor.
3. Flag UGC insertion points: `← UGC: community counterpoints` / `← UGC: case studies` / `← UGC: FAQ`
4. Output brief + outline → see `references/output-templates.md` Stage 2
5. Ask: "Does this outline look good?" Wait for confirmation before Stage 3.

FAQ section: minimum 5 entries. Mandatory for GEO.

---

## Stage 3 — UGC Enrichment

Skip if no `ugc_urls`. Note "UGC: Missing" in QA report.

Why it matters: Reddit ~21% of Google AI Overview citations. Real UGC = 2–3x AI search visibility. E-E-A-T "Experience" signal = cannot be faked by AI content.

For each URL:
1. `web_fetch` → extract post body + all comments with engagement metrics
   - Fallback if login wall: "Paste comment text directly"
2. Quality-score each comment → see `references/scoring-rubrics.md` Stage 3
3. Classify into 3 categories:
   - **Category A — Counter-Arguments**: challenges original post, edge cases, "Yeah but..." → 150–300 word prose paragraph
   - **Category B — Real-World FAQs**: direct questions from comments, especially upvoted or repeated → 3–6 Q&A pairs
   - **Category C — Personal Experiences**: first-person accounts with specific numbers/outcomes → 2–4 mini case studies, 50–100 words each, paraphrased but never fabricated
4. Viral pattern analysis for comments scoring ≥7: identify top 3 trigger types, output 2 writing tips
5. Map each UGC block to its insertion point from Stage 2 outline
6. Output → see `references/output-templates.md` Stage 3

Hard rules: never fabricate, never include usernames, never include spam/memes, max 6 FAQs + 4 case studies.

Edge cases: <10 comments → warn "limited data". All score <3 → "No high-value comments, try different URL."

---

## Stage 4 — Draft Writing

Write full article: follow Stage 2 outline exactly, insert Stage 3 UGC blocks at flagged points.

**Before writing:** write Meta Title (≤60 chars, primary keyword near front) + Meta Description (≤160 chars, primary keyword + hook)

**Intro:** specific fact or bold claim opener. Primary keyword within first 100 words. Write featured snippet candidate block (40–60 words, direct definition or numbered steps) — place within first H2.

**Body:** answer-first each H2 (1–2 sentence direct answer before elaboration). Min 1 data point per major section. Find real stats first: search `[topic] statistics 2025`. If unavailable: `[DATA NEEDED: search "[query]"]`. Source format: `stat — Source, Year`. UGC blocks at exact insertion points.

**Data minimum:** 3 data points total per article. Never invent statistics.

**Paragraphs:** 3–4 lines max. Define technical terms inline on first use.

**AI patterns:** never write any phrase from `references/ai-patterns-blacklist.md`. If caught: stop, rewrite with fact or direct claim.

**Conclusion:** synthesize 2–3 takeaways. Do not restate all H2s as bullet points. Specific CTA.

**Internal links:** suggest 2–3, anchor text uses secondary keywords.

Output format → see `references/output-templates.md` Stage 4

---

## Stage 4.5 — Visual & Link Enrichment

**Runs automatically after Stage 4 is complete. Cannot be skipped — required for publish-ready output.**

### Why This Stage Exists
- Data charts are 3× more likely to be cited by AI search engines than the same data in plain text
- Inline hyperlinks on every source citation signal editorial credibility to Google and AI crawlers
- Every unlinked `— Source, Year` is a missed E-E-A-T trust signal

---

### Step 1 — Identify Chart Opportunities

Scan the draft for data points that meet **at least one** of these criteria:

| Criterion | Example |
|---|---|
| Change over time (2+ periods) | "TVL grew from $2B to $8B in 6 months" |
| Compares 2+ assets or metrics | "Lido APY 3.8% vs solo staking 3.2%" |
| Inflow / outflow trend | "$1.2B ETF inflows in Q1 2025" |
| Index or score over time | "Fear & Greed Index: 12/100" |
| Ratio that changed | "ETH staking ratio: 18% → 27% in 12 months" |
| 3+ data points in a series | Monthly DEX volume figures |

**Chart types by data shape:**

| Data type | Chart type |
|---|---|
| Performance over time | Line chart with fill-under |
| Inflows / outflows | Bar chart — green positive, red negative |
| Index or score over time | Bar chart with color-coded zones |
| Ratio or comparison over time | Line or area chart |
| Single-point comparison | Horizontal bar or stat callout box |

**Chart design standards (apply to every chart):**
- Background: `#F7F7F7` (light gray), no heavy gridlines
- Primary color: `#E8650A` (orange, default for crypto/Web3 — adjust to project brand if spec defines one)
- Remove top + right spine
- Annotate key data points directly on chart (peak, trough, threshold)
- Source line at bottom-left: gray italic — `Source: [Name] | [Notes]`
- Font: DejaVu Sans (matplotlib default)
- Resolution: 150 DPI minimum
- Always generate alt text for every chart

**Maximum 6 charts per article.** More than 6 slows page load. Excess data points → stat callout boxes instead.

If no qualifying data points found: output a styled stat callout box for that statistic instead of a chart.

---

### Step 2 — Generate Charts

Use Python + matplotlib. Execute in the computing environment.

For each chart, produce:
1. PNG image embedded in the output
2. Caption (1–2 sentences): `Chart [N]: [What it shows]. [Time period]. Sources: [Name].`
3. Alt text string for CMS upload: `[Chart type] showing [metric] from [start] to [end]. [Key finding in one sentence].`

Place each chart **immediately after** the paragraph that first introduces its data. Never stack two charts back-to-back without body text between them.

---

### Step 3 — Convert All Source Citations to Hyperlinks

Scan the entire draft for every inline source citation. Patterns to find:

| Pattern | Example |
|---|---|
| `— [Source, Year]` | `— CoinDesk, Jan 2025` |
| `per [Source]` | `per DeFiLlama` |
| `according to [Source]` | `according to Messari` |
| `[Source] reports` | `Dune Analytics reports` |
| `([Source])` | `(CoinGecko)` |

**For each citation:**
1. Run web search: `[publication] [topic] [approximate date]`
2. Verify URL resolves
3. Replace plain-text source with inline hyperlink — anchor text = source name
4. If exact article not found: link to publication homepage + flag `[VERIFY URL]`
5. If citation is vague ("analysts say"): flag `[SOURCE NEEDED]` — never invent a source

**Link rules:**
- Prefer original publisher over aggregators
- No paywalled links if a free version exists
- All external links: open in new tab in HTML output
- Do not add links to unattributed claims

---

### Step 4 — Output Summary

Append this block to the enriched draft:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STAGE 4.5 — VISUAL & LINK ENRICHMENT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Charts generated:      [N] / [max 6]
  - Chart 1: [title] → placed after [section name]
  - Chart 2: [title] → placed after [section name]

Source links resolved: [N] / [total citations found]
  - [Source name] → [URL] ✅
  - [Source name] → [URL] ⚠️ [VERIFY URL — linked to homepage]

Unlinked citations flagged: [N]
  - "[claim]" → [SOURCE NEEDED]

Alt text strings:
  Chart 1: "[alt text]"
  Chart 2: "[alt text]"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Stage 5 — SEO + GEO Optimization

### SEO Checklist
- [ ] Meta title: 50–60 chars, primary keyword near front
- [ ] Meta description: 150–160 chars, primary keyword, hook
- [ ] H1 contains primary keyword (only one H1)
- [ ] H2s use secondary keywords or question variants
- [ ] Primary keyword in first 100 words and in conclusion
- [ ] Keyword density: 1–1.5%
- [ ] Paragraphs ≤4 lines
- [ ] 2+ internal link suggestions (anchor text = secondary keywords)
- [ ] 1–2 external authoritative sources noted
- [ ] Image alt text recommendations (min 2)
- [ ] FAQ present → FAQPage schema | How-to steps → HowTo schema

### GEO Rules (apply all 7)

GEO = Generative Engine Optimization. Goal: easy for Perplexity, Google SGE, ChatGPT Search to parse and cite.

1. **Answer-first every H2** — 1–2 sentence direct answer before elaboration
2. **Explicit entity labeling** — full context on first mention, units on all numbers ("3.2% APY"), explicit dates ("as of Q1 2025")
3. **FAQ mandatory (min 5)** — each answer self-contained, 50–150 words, direct answer first
4. **Featured snippet block** — 40–60 words, placed within first H2, paragraph OR numbered list (not mixed)
5. **Citation-friendly** — each factual claim on its own sentence, data formatted `number unit — Source, Year`, no pronoun ambiguity
6. **Secondary keywords in internal link anchor text**
7. **UGC sections present** — confirms E-E-A-T "Experience" signal

GEO output block → see `references/output-templates.md` Stage 5
Scoring rubric → see `references/scoring-rubrics.md` Stage 5

---

## Stage 6 — QA Scoring Report

Score using 100-point rubric → see `references/scoring-rubrics.md` Stage 6

Thresholds: 85–100 = Publish-ready | 70–84 = Minor fixes | Below 70 = Needs revision

Output format → see `references/output-templates.md` Stage 6

---

## Edge Cases

| Case | Action |
|---|---|
| `project_spec` missing | Stop. Ask for spec before starting. |
| Keyword too broad | Stop. Suggest 3–5 long-tail alternatives. Wait for choice. |
| Keyword doesn't match spec | Warn. Ask for confirmation. |
| Deep technical content | Flag `[SME REVIEW]`. Never fabricate. |
| User requests Vietnamese | Switch all output to Vietnamese. Same formats. |
| Word count <500 or >5000 | Warn. Recommend 800–2500. |
| SEO score below 70 | List specific fixes with section references. |
| Web search unavailable | Skip Stage 0. Flag affected stages. Fall back to training knowledge, label `[estimated]`. |
| UGC URL behind login wall | Skip URL. Ask: "Paste comment text directly." |
| No high-value UGC comments | "No high-value comments. Try a different URL." |
| No ugc_urls provided | Skip Stage 3. Mark UGC = Missing in QA. |
| Stage 0 finds no trends | List 3 evergreen topics from spec context. |
| User enters mid-pipeline | Start at appropriate stage. Ask what they have. |
| Stage 4.5: no chart-worthy data | Output stat callout boxes for all key numbers. Flag: "No time-series or comparison data found — consider adding benchmark data in Stage 4 revision." |
| Stage 4.5: more than 6 chart-worthy points | Prioritize: (1) comparisons, (2) trends, (3) index scores. Remainder → stat callout boxes. |
| Stage 4.5: all source URLs paywalled | Link to publisher homepages. Flag every instance `[VERIFY URL]`. List all in enrichment summary. |
| Stage 4.5: source article not found | Link to publication homepage + flag `[SOURCE NEEDED — could not verify]`. |
| Stage 4.5: citation is vague ("analysts say") | Flag `[SOURCE NEEDED]`. Never invent a source. |
| Stage 4.5: web search unavailable | Skip link resolution. Flag all citations `[HYPERLINK NEEDED — web search off]`. Charts still generated from in-draft data. |

---

## Limitations

- Stage 0: simulated X monitoring via web search, not live X API
- Keyword volume: estimated unless user provides API key
- No CMS auto-publishing, no image generation (editorial)
- Stage 4.5 generates data charts from in-draft data via matplotlib — does NOT generate decorative or editorial images
- `[VERIFY]`, `[DATA NEEDED]`, `[SOURCE NEEDED]`, and `[VERIFY URL]` flags require human review before publishing
- SEO/GEO scores: internal rubric, not third-party tool scores
- UGC mining: public pages only
