# Enrichment Reference

Enrichments add detailed data fields to fetch results and consume additional credits.
**Max 3 enrichment types per single enrich call.** Chain multiple calls for more.

## Business Enrichments (`enrich-business` command)

| Enrichment Type | Data Provided | Notes |
|---|---|---|
| `enrich-business-firmographics` | Name, description, website, HQ location, industry, employee count, revenue range | Basic company profile — usually the first enrichment |
| `enrich-business-technographics` | Complete tech stack (products + categories) | Identifies what software the company uses |
| `enrich-business-company-ratings` | Employee satisfaction, culture scores, Glassdoor-style ratings | |
| `enrich-business-financial-metrics` | Revenue, margins, EPS, EBITDA, market cap | **Public companies only**. Requires `--date YYYY-MM-DD` (the reporting period) |
| `enrich-business-funding-and-acquisitions` | Funding rounds, investors, total raised, IPO details, acquisitions | Includes round type (Seed/Series A-E/PE/etc.) |
| `enrich-business-challenges` | Business risks, strategic challenges from SEC 10-K filings | **Public companies only** |
| `enrich-business-competitive-landscape` | Competitors, market positioning from SEC filings | **Public companies only** |
| `enrich-business-strategic-insights` | Strategic focus, value propositions, key initiatives from SEC filings | **Public companies only** |
| `enrich-business-workforce-trends` | Dept headcount breakdown, hiring velocity, YoY growth by department | |
| `enrich-business-linkedin-posts` | Recent company LinkedIn posts, engagement metrics (likes, comments, shares) | |
| `enrich-business-website-changes` | Website content changes detected over time, summary of updates | |
| `enrich-business-website-keywords` | Whether specific keywords appear on company website | Requires `--keywords kw1,kw2` |
| `enrich-business-webstack` | Web-specific tech: CDN, analytics platforms, CMS, chat widgets | More granular than technographics for web layer |
| `enrich-business-company-hierarchies` | Parent company, subsidiaries, org tree structure | Output is nested JSON |

## Prospect Enrichments (`enrich-prospects` command)

| Enrichment Type | Data Provided | Notes |
|---|---|---|
| `enrich-prospects-contacts` | Professional email, personal email, direct phone, mobile phone | Use `--contact-types email,phone` to limit scope; `email` only is cheaper |
| `enrich-prospects-profiles` | Full name, demographics, current & past work history, education, LinkedIn URL | |

## Common Enrichment Combinations

| Use Case | Enrichments |
|---|---|
| Basic company profile | `enrich-business-firmographics` |
| Tech stack + company info | `enrich-business-firmographics,enrich-business-technographics` |
| Investor/VC targeting | `enrich-business-firmographics,enrich-business-funding-and-acquisitions` |
| Website intelligence | `enrich-business-website-changes,enrich-business-webstack` |
| Workforce growth signals | `enrich-business-workforce-trends,enrich-business-firmographics` |
| Full contact list | `enrich-prospects-contacts,enrich-prospects-profiles` |
| Email-only list (cheaper) | `enrich-prospects-contacts` + `--contact-types email` |
| All company intel (chain 2 calls) | Call 1: `enrich-business-firmographics,enrich-business-technographics,enrich-business-funding-and-acquisitions` → Call 2: `enrich-business-workforce-trends,enrich-business-linkedin-posts` |

## Critical Rules

1. **Always use `enriched_table_name`** from the enrich response in all subsequent operations (export, further enrich, events). The enriched table is a new table — do not use the original fetch table name.
2. **Chain enrichments sequentially**: Each enrich call returns a new `enriched_table_name`; pass it as `--table-name` to the next enrich call.
3. **Public company enrichments** (`financial-metrics`, `challenges`, `competitive-landscape`, `strategic-insights`) return empty data for private companies — use `is_public_company: true` filter when these are the goal.
4. **Re-present sample** to the user after enrichment before asking about export.
