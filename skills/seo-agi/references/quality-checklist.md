# Content Quality Checklist

SEO-AGI validates every page against this checklist before final output.
Each item is scored pass/fail. Pages scoring below 80% get flagged with
specific items to fix.

## Title Tag (10 points)

- [ ] Contains target keyword (or close variant)
- [ ] Under 60 characters
- [ ] Unique and compelling (not just "[Keyword] | [Brand]")
- [ ] Includes a differentiating element (year, number, qualifier)
- [ ] Not duplicating another page's title on the same site

## Meta Description (10 points)

- [ ] Under 155 characters
- [ ] Contains target keyword naturally
- [ ] Includes a call-to-action or value proposition
- [ ] Not a copy of the first paragraph
- [ ] Would make someone click vs competitors in the SERP

## Heading Structure (15 points)

- [ ] Exactly one H1
- [ ] H1 closely matches or mirrors title tag
- [ ] Logical H2 > H3 hierarchy (no skipped levels)
- [ ] H2 count within competitive range (see analysis)
- [ ] Headings are descriptive (not "Section 1" or "More Info")

## Content Depth (25 points)

- [ ] Word count within competitive range (not arbitrarily long or short)
- [ ] Answers at least 3 People Also Ask questions
- [ ] Includes specific data, statistics, or concrete examples
- [ ] Covers topics that appear in 2+ competitor pages
- [ ] No thin sections (every H2 has 150+ words of substance)

## Search Intent Match (15 points)

- [ ] Page type matches detected intent (informational/commercial/transactional)
- [ ] Content format matches SERP expectations (list vs guide vs comparison)
- [ ] Addresses the primary user need within the first 200 words
- [ ] If commercial intent: includes pricing or comparison elements
- [ ] If informational intent: includes step-by-step or explanatory depth

## Technical SEO (15 points)

- [ ] JSON-LD schema markup included and matches page type
- [ ] Schema uses correct types (see schema-patterns.md)
- [ ] Image alt text suggestions included
- [ ] At least 2 internal link suggestions with context
- [ ] No orphaned sections (every section connects to the page's topic)

## Readability (10 points)

- [ ] No keyword stuffing (target keyword appears naturally, not forced)
- [ ] Paragraphs are scannable (no walls of text)
- [ ] Uses formatting aids where appropriate (bold key terms, tables for comparisons)
- [ ] Transitions between sections are logical
- [ ] Reads like it was written by a subject matter expert, not a content mill

## Scoring

| Score | Rating | Action |
|---|---|---|
| 90-100 | Exceptional | Ship it |
| 80-89 | Strong | Minor tweaks optional |
| 70-79 | Acceptable | Fix flagged items before publishing |
| 60-69 | Below standard | Significant revision needed |
| <60 | Rewrite | Start over with revised brief |

## Red Flags (automatic fail)

These issues override the score and require fixing regardless:

- Duplicate title tag matching another page on the site
- Missing H1 or multiple H1 tags
- Zero data/statistics in the entire page
- Word count more than 50% below competitive median
- No FAQ or PAA coverage
- Missing schema markup entirely
- Keyword density above 3% (stuffing)
