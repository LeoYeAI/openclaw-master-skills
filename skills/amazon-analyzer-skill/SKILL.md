---
name: apiclaw-analysis
version: 1.1.3
description: >
  Find winning Amazon products with 14 battle-tested selection strategies
  & 6-dimension risk assessment. Backed by 200M+ product database.
  Use when user asks about: product selection, finding products to sell, ASIN lookup,
  BSR analysis, competitor lookup, market opportunity, risk assessment, category research,
  pricing strategy, review analysis, listing optimization, or any Amazon seller data needs.
  Powered by APIClaw API (requires APICLAW_API_KEY).
author: SerendipityOneInc
homepage: https://github.com/SerendipityOneInc/Amazon-analysis-skill
metadata: {"openclaw": {"requires": {"env": ["APICLAW_API_KEY"]}, "primaryEnv": "APICLAW_API_KEY"}}
---

# APIClaw — Amazon Seller Data Analysis

> AI-powered Amazon product research. From market discovery to daily operations.
>
> **Language rule**: Always respond in the user's language. If the user asks in Chinese, reply in Chinese. If in English, reply in English. The language of this skill document does not affect output language.
> All API calls go through `scripts/apiclaw.py` — one script, 5 endpoints, built-in error handling.

## Credentials

- Required: `APICLAW_API_KEY`
- Scope: used only for `https://api.apiclaw.io`
- Resolution order:
  1. **Environment variable** `APICLAW_API_KEY` (preferred, most secure)
  2. **Config file** `config.json` in the skill root directory (fallback)

```json
{ "api_key": "hms_live_xxxxxx" }
```

When user provides a Key, write it to `config.json`. New keys may need 3-5 seconds to activate — if first call returns 403, wait 3 seconds and retry (max 2 retries).

**⚠️ Data persistence notice:** When you provide an API Key, the skill saves it to `config.json` in the skill directory for persistent access across sessions. This file is local-only and listed in `.gitignore` to prevent accidental commits. If you prefer not to store the key on disk, use the environment variable method (`export APICLAW_API_KEY=...`) instead — no file will be created.

**New users:** Get API Key at [apiclaw.io/api-keys](https://apiclaw.io/api-keys).

## File Map

| File | When to Load |
|------|-------------|
| `SKILL.md` (this file) | Start here — covers 80% of tasks |
| `scripts/apiclaw.py` | **Execute** for all API calls (do NOT read into context) |
| `references/reference.md` | Need exact field names or filter parameter details |
| `references/scenarios-composite.md` | Comprehensive recommendations (2.10) or Chinese seller cases (3.4) |
| `references/scenarios-eval.md` | Product evaluation, risk assessment, review analysis (4.x) |
| `references/scenarios-pricing.md` | Pricing strategy, profit estimation, listing reference (5.x) |
| `references/scenarios-ops.md` | Market monitoring, competitor tracking, anomaly alerts (6.x) |
| `references/scenarios-expand.md` | Product expansion, trends, discontinuation decisions (7.x) |
| `references/scenarios-listing.md` | Listing writing, optimization, content creation (8.x) |

**Don't guess field names** — if uncertain, load `reference.md` first.

---

## Execution Mode

| Task Type | Mode | Behavior |
|-----------|------|----------|
| Single ASIN lookup, simple data query | **Quick** | Execute command, return key data. Skip evaluation criteria and output standard block. |
| Market analysis, product selection, competitor comparison, risk assessment | **Full** | Complete flow: command → analysis → evaluation criteria → output standard block. |

**Quick mode trigger:** User asks for a single specific data point ("B09XXX monthly sales?", "how many brands in cat litter?") — no decision analysis needed.

---

## Execution Standards

**Prioritize script execution for API calls.** The script includes:
- Parameter format conversion (e.g. topN auto-converted to string)
- Retry logic (429/timeout auto-retry)
- Standardized error messages
- `_query` metadata injection (for query traceability)

**Fallback:** If script fails and can't be quickly fixed, use curl directly. Note "using curl direct call" in output.

---

## Script Usage

All commands output JSON. Progress messages go to stderr.

### categories — Category tree lookup

```bash
python3 scripts/apiclaw.py categories --keyword "pet supplies"
python3 scripts/apiclaw.py categories --parent "Pet Supplies"
```

Common fields: `categoryName` (not `name`), `categoryPath`, `productCount`, `hasChildren`

### market — Market-level aggregate data

```bash
python3 scripts/apiclaw.py market --category "Pet Supplies,Dogs" --topn 10
```

Key output fields: `sampleAvgMonthlySales`, `sampleAvgPrice`, `topSalesRate` (concentration), `topBrandSalesRate`, `sampleNewSkuRate`, `sampleFbaRate`, `sampleBrandCount`

### products — Product selection with filters

```bash
# Preset mode (14 built-in)
python3 scripts/apiclaw.py products --keyword "yoga mat" --mode beginner

# Explicit filters
python3 scripts/apiclaw.py products --keyword "yoga mat" --sales-min 300 --reviews-max 50

# Mode + overrides (overrides win)
python3 scripts/apiclaw.py products --keyword "yoga mat" --mode beginner --price-max 30
```

Available modes: `fast-movers`, `emerging`, `single-variant`, `high-demand-low-barrier`, `long-tail`, `underserved`, `new-release`, `fbm-friendly`, `low-price`, `broad-catalog`, `selective-catalog`, `speculative`, `beginner`, `top-bsr`

**Keyword matching:** Default is `fuzzy` (matches brand names too — e.g. "smart ring" matches "Smart Color Art" pens). Use `--keyword-match-type exact` or `phrase` for precise results. Always combine with `--category` when possible to reduce noise.

**Category path with commas:** Some category names contain commas (e.g. "Pacifiers, Teethers & Teething Relief"). Use ` > ` separator instead of `,` to avoid parsing errors:
```bash
# ❌ Wrong — comma in name breaks parsing
--category "Baby Products,Baby Care,Pacifiers, Teethers & Teething Relief"
# ✅ Correct — use ' > ' separator
--category "Baby Products > Baby Care > Pacifiers, Teethers & Teething Relief"
```

### competitors — Competitor lookup

```bash
python3 scripts/apiclaw.py competitors --keyword "wireless earbuds"
python3 scripts/apiclaw.py competitors --asin B09V3KXJPB
```

**Easily confused fields (products/competitors shared)**:

| ❌ Wrong | ✅ Correct | Note |
|----------|-----------|------|
| `reviewCount` | `ratingCount` | Review count |
| `bsr` | `bsrRank` | BSR ranking (integer, only in products/competitors) |
| `monthlySales` / `salesMonthly` | `atLeastMonthlySales` | Monthly sales (lower bound estimate, NOT in realtime/product) |
| `bestsellersRank` | `bsrRank` | `bestsellersRank` is realtime/product only (array format); use `bsrRank` for products/competitors |
| `price` (in realtime) | `buyboxWinner.price` | realtime/product nests price inside buyboxWinner object |
| `profitMargin` (in realtime) | ❌ N/A | realtime/product does NOT return profitMargin; use products/competitors |

> Complete field list: `reference.md` → Shared Product Object

### product — Single ASIN real-time detail

```bash
python3 scripts/apiclaw.py product --asin B09V3KXJPB
```

Returns: title, brand, rating, ratingBreakdown, features, topReviews, specifications, variants, bestsellersRank, buyboxWinner

### report — Full market analysis (composite)

```bash
python3 scripts/apiclaw.py report --keyword "pet supplies"
```

Runs: categories → market → products (top 50) → realtime detail (top 1).

**Note:** The realtime detail section has a different field structure than products (no sales/revenue/profitMargin). It provides review details, seller info, and listing content as qualitative supplement.

### opportunity — Product opportunity discovery (composite)

```bash
python3 scripts/apiclaw.py opportunity --keyword "pet supplies" --mode fast-movers
```

Runs: categories → market → products (filtered) → realtime detail (top 3).

**Note:** Same as `report` — realtime detail provides qualitative data only (reviews, features, seller). Sales/revenue come from the products step.

---

## ⚠️ Interface Data Differences

The 3 types of interfaces return **different fields**. Do NOT assume they share the same structure.

| Data | `market` | `products` / `competitors` | `realtime/product` |
|------|----------|---------------------------|-------------------|
| Monthly Sales | `sampleAvgMonthlySales` | ✅ `atLeastMonthlySales` | ❌ **Not available** |
| Revenue | `sampleAvgMonthlyRevenue` | `salesRevenue` | ❌ **Not available** |
| Price | `sampleAvgPrice` | `price` | `buyboxWinner.price` |
| BSR | `sampleAvgBsr` | `bsrRank` (integer) | `bestsellersRank` (array of {category, rank}) |
| Rating | `sampleAvgRating` | `rating` | `rating` |
| Review Count | `sampleAvgReviewCount` | `ratingCount` | `ratingCount` |
| Review Details | ❌ | ❌ | ✅ `topReviews` + `ratingBreakdown` |
| Seller | ❌ | `buyboxSeller` (string) | `buyboxWinner` (object with price, fulfillment, seller) |
| Profit Margin | ❌ | `profitMargin` | ❌ **Not available** |
| FBA Fee | ❌ | `fbaFee` | ❌ **Not available** |
| Seller Count | ❌ | `sellerCount` | ❌ **Not available** |
| Features/Bullets | ❌ | ❌ | ✅ `features` |
| Variants | ❌ | `variantCount` (integer) | `variants` (full list) |

**Usage rule:**
- Use `products` / `competitors` for **sales, pricing, and competition data**
- Use `realtime/product` for **review details, listing content, and seller info**
- Use `market` for **category-level aggregate metrics**
- For reports: combine `products`/`competitors` (quantitative) + `realtime/product` (qualitative) as evidence

## Data Structure Reminder

All interfaces return `.data` as an **array**. Use `.data[0]` to get the first record, NOT `.data.fieldName`.

---

## Intent Routing

| User Says | Run This | Scenario File? |
|-----------|----------|----------------|
| "which category has opportunity" | `market` + `categories` | No |
| "check B09XXX" / "analyze ASIN" | `product --asin XXX` | No |
| "Chinese seller cases" | `competitors --keyword XXX --page-size 50` | `scenarios-composite.md` → 3.4 |
| "pain points" / "negative reviews" | `product --asin XXX` | `scenarios-eval.md` → 4.2 |
| "compare products" | `competitors` or multiple `product` | `scenarios-eval.md` → 4.3 |
| "risk assessment" / "can I do this" | `product` + `market` + `competitors` | `scenarios-eval.md` → 4.4 |
| "monthly sales" / "estimate sales" | `competitors --asin XXX` | `scenarios-eval.md` → 4.5 |
| "help me select products" / "find products" | `products --mode XXX` (see mode table) | No |
| "comprehensive recommendations" / "what should I sell" | `products` (multi-mode) + `market` | `scenarios-composite.md` → 2.10 |
| "pricing strategy" / "how much to price" | `market` + `products` | `scenarios-pricing.md` → 5.1 |
| "profit estimation" | `competitors` | `scenarios-pricing.md` → 5.2 |
| "listing reference" | `product --asin XXX` | `scenarios-pricing.md` → 5.3 |
| "market changes" / "recent changes" | `market` + `products` | `scenarios-ops.md` → 6.1 |
| "competitor updates" | `competitors --brand XXX` | `scenarios-ops.md` → 6.2 |
| "anomaly alerts" | `market` + `products` | `scenarios-ops.md` → 6.4 |
| "what else can I sell" / "related products" | `categories` + `market` | `scenarios-expand.md` → 7.1 |
| "trends" | `products --growth-min 0.2` | `scenarios-expand.md` → 7.3 |
| "should I delist" | `competitors --asin XXX` + `market` | `scenarios-expand.md` → 7.4 |
| "write listing" / "generate bullet points" / "write title" | `product --asin XXX` (competitors) | `scenarios-listing.md` → 8.2 |
| "analyze competitor listing" / "their selling points" | `product --asin XXX` (multiple) | `scenarios-listing.md` → 8.1 |
| "optimize my listing" / "listing diagnosis" | `product --asin XXX` + `competitors` | `scenarios-listing.md` → 8.3 |
| Need exact filters or field names | — | Load `reference.md` |

**Product Selection Mode Mapping (14 types)**:

| User Intent | Mode | Key Filters |
|-------------|------|-------------|
| "beginner friendly" / "new seller" | `--mode beginner` | Sales≥300, growth≥3%, $15-60, FBA, ≤1yr, excl. red ocean keywords |
| "fast turnover" / "hot selling" | `--mode fast-movers` | Sales≥300, growth≥10% |
| "emerging" / "rising" | `--mode emerging` | Sales≤600, growth≥10%, ≤180d |
| "single variant" / "small but beautiful" | `--mode single-variant` | Growth≥20%, variants=1, ≤180d |
| "high demand low barrier" / "easy entry" | `--mode high-demand-low-barrier` | Sales≥300, reviews≤50, ≤180d |
| "long tail" / "niche" | `--mode long-tail` | Sales≤300, BSR 10K-50K, ≤$30, sellers≤1 |
| "underserved" / "has pain points" | `--mode underserved` | Sales≥300, rating≤3.7, ≤180d |
| "new products" / "new release" | `--mode new-release` | Sales≤500, NR tag, FBA+FBM |
| "FBM" / "self-fulfillment" / "low stock" | `--mode fbm-friendly` | Sales≥300, FBM, ≤180d |
| "low price" / "cheap" | `--mode low-price` | ≤$10 |
| "broad catalog" / "cast wide net" | `--mode broad-catalog` | BSR growth≥99%, reviews≤10, ≤90d |
| "selective catalog" | `--mode selective-catalog` | BSR growth≥99%, ≤90d |
| "speculative" / "piggyback" | `--mode speculative` | Sales≥600, sellers≥3, ≤180d |
| "top sellers" / "best sellers" | `--mode top-bsr` | Sub-category BSR≤1000 |

---

## Quick Evaluation Criteria

### Market Viability (from `market` output)

| Metric | Good | Medium | Warning |
|--------|------|--------|---------|
| Market value (avgRevenue × skuCount) | > $10M | $5–10M | < $5M |
| Concentration (topSalesRate, topN=10) | < 40% | 40–60% | > 60% |
| New SKU rate (sampleNewSkuRate) | > 15% | 5–15% | < 5% |
| FBA rate (sampleFbaRate) | > 50% | 30–50% | < 30% |
| Brand count (sampleBrandCount) | > 50 | 20–50 | < 20 |

### Product Potential (from `product` output)

| Metric | High | Medium | Low |
|--------|------|--------|-----|
| BSR | Top 1000 | 1000–5000 | > 5000 |
| Reviews | < 200 | 200–1000 | > 1000 |
| Rating | > 4.3 | 4.0–4.3 | < 4.0 |
| Negative reviews (1-2★ %) | < 10% | 10–20% | > 20% |

### Sales Estimation Fallback

When `atLeastMonthlySales` is null: **Monthly sales ≈ 300,000 / BSR^0.65**

---

## Output Standards (Full Mode Only)

**MUST include data source block after every Full-mode analysis:**

```markdown
---
**Data Source & Conditions**
| Item | Value |
|----|-----|
| Data Source | APIClaw API |
| Interface | [interfaces used] |
| Category | [category path] |
| Time Range | [dateRange] |
| Sampling | [sampleType] |
| Top N | [topN value] |
| Sort | [sortBy + sortOrder] |
| Filters | [specific parameter values] |

**Data Notes**
- Monthly sales are **lower bound estimates** (Amazon displays "10,000+ bought"), actual may be higher
- Database data has ~T+1 delay; realtime/product is current real-time data
- Concentration metrics based on Top N sample; different topN → different results
```

**✅ Completed Example (yoga mat market analysis):**

```markdown
---
**Data Source & Conditions**
| Item | Value |
|----|-----|
| Data Source | APIClaw API |
| Interface | categories, markets/search, products/search |
| Category | Sports & Outdoors > Exercise & Fitness > Yoga > Yoga Mats |
| Time Range | 30d |
| Sampling | by_sale_100 |
| Top N | 10 |
| Sort | atLeastMonthlySales desc |
| Filters | monthlySalesMin: 300, reviewCountMax: 50 |

**Data Notes**
- Monthly sales are **lower bound estimates** (Amazon displays "10,000+ bought"), actual may be higher
- Database data has ~T+1 delay; realtime/product is current real-time data
```

**Rules**:
1. Every Full-mode analysis MUST end with this block
2. Filter conditions MUST list specific parameter values
3. If multiple interfaces used, list each one
4. If data has limitations, proactively explain

---

## Limitations

### What This Skill Cannot Do

- Keyword research / reverse ASIN / ABA data
- Traffic source analysis
- Historical sales trends (14-month curves)
- Historical price / BSR charts
- AI review sentiment analysis (use topReviews + ratingBreakdown manually)

### API Coverage Boundaries

| Scenario | Coverage | Suggestion |
|----------|----------|------------|
| Market data: Popular keywords | ✅ Has data | Use `--keyword` directly |
| Market data: Niche/long-tail keywords | ⚠️ May be empty | Use `--category` instead |
| Product data: Active ASIN | ✅ Has data | — |
| Product data: Delisted/variant ASIN | ❌ No data | Try parent ASIN or realtime |
| Real-time data: US site | ✅ Full support | — |
| Real-time data: Non-US sites | ⚠️ Partial | Core fields OK, sales may be null |

---

## Error Handling

HTTP errors (401/402/403/404/429) are handled by the script, returning structured JSON with `error.message` and `error.action`.

Self-check: `python3 scripts/apiclaw.py check` — tests 4/5 endpoints, reports availability.

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot index array with string` | `.data` is array | Use `.data[0].fieldName` |
| Empty `data: []` | Keyword no match | Use `categories` to confirm category exists |
| `atLeastMonthlySales: null` | Missing sales data | BSR estimate: 300,000 / BSR^0.65 |
| `realtime/product` slow | Real-time scraping | Normal 5-30s, be patient |
