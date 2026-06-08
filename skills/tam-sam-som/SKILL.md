---
name: market-sizing
description: Produce a rigorous, sourced TAM/SAM/SOM market sizing for any product or business. Use this skill whenever a user asks about market size, total addressable market, SAM, SOM, or market opportunity — across any industry including SaaS, AI tools, consumer brands, F&B, fashion, beauty, packaging, automotive, and more.
version: v2
---

# TAM / SAM / SOM Market Sizing

Produce both a bottom-up and a top-down analysis for every engagement. Both methods are required — they serve different purposes and must be reconciled. The goal is a defensible, sourced output — not a fast estimate.

---

## When to use this skill
Trigger on any prompt that contains:
- "TAM", "SAM", "SOM", or "market size"
- "How big is the market for X"
- "Total addressable market", "serviceable market", "obtainable market"
- "Market sizing for [product/company]"
- Investor deck context requiring market opportunity quantification

---

## Loading examples
Before calculating, check the `examples/` directory for a file matching the product's category. Load the closest match to calibrate data sources, filter logic, and ACV anchors before you begin.

| File | Use when product is... |
|------|----------------------|
| `examples/b2b-saas.md` | Software / AI tool sold to businesses |
| `examples/b2c-consumer-brand.md` | Consumer packaged goods, DTC brands, subscriptions |
| `examples/b2b-physical.md` | Physical goods or materials sold to businesses |

If no exact match exists, load the closest file and adapt.

---

## Pre-flight: Classify the product before doing anything else

Before searching or calculating, classify the product along these two axes. The classification directly determines which data sources to use and which pricing method applies.

### Axis 1 — Business model
| Code | Type | Revenue unit | Pricing anchor |
|------|------|-------------|----------------|
| **B2B-SaaS** | Software sold to businesses | Annual contract (ACV) | 10–20% of economic value created |
| **B2B-Physical** | Physical goods sold to businesses | Per-unit price × annual volume | Gross margin benchmarks by industry |
| **B2C-Brand** | Consumer product (any category) | Revenue per customer per year | Avg. purchase price × purchase frequency |
| **B2C-Subscription** | Consumer subscription | Monthly/annual subscription fee | Stated price or comp pricing |
| **Marketplace/Platform** | Takes % of GMV | Take rate × GMV | Industry take rate benchmarks |

### Axis 2 — Market geography
- **US-only**: Use US Census, NAICS codes, US industry associations
- **Global**: Use global market reports, then apply regional share (US ~25–30% of global GDP; NA ~32%; APAC ~38%)
- **Single city/region**: Use metro area population data + category penetration rates

## Step-by-step workflow (universal)

### Step 0 - Data Gathering
Since accuracy and reliability are key of this task, make sure you collect enough reliable data from reliable sources before the calculation. Limited estimation is fine with enough evidence support, but any kind of data making up or hallucination without evidence during the calculation and output phase is a fraud. 

### STEP 1 — Define the revenue unit
Before any market data search, lock down exactly what the product sells, to whom, and at what price.

**Required inputs:**
- Who is the buyer? (job title / consumer demographic)
- What is the unit of sale? (per seat, per SKU, per kg, per subscription, per transaction)
- What is the price? (stated, or estimated by comp analysis)
- What is the purchase frequency? (one-time, monthly, annual, recurring)

**If price is unknown:** Search `"[product category] average price" OR "[closest competitor] pricing"` and anchor to the median. For B2B-SaaS, also apply the 10–20% value rule: price = 10–20% of annual economic value the product creates for the customer.

**Output of Step 1:** A single sentence — *"The revenue unit is [X] sold to [Y] at [Z]/year."*

### STEP 2 — TAM (Total Addressable Market)

TAM = the maximum theoretical revenue if every potential buyer purchased the product.

#### 2A — Bottom-up method (PREFERRED for all product types)

**For B2B products:**
1. Search for the number of firms in the target industry
   - US: Use NAICS code lookup — search `"NAICS [code] number of firms US"` or `site:siccode.com NAICS [code]`
   - Global: Use IBISWorld, Statista, or national business registries
2. Estimate the % that are genuinely relevant (apply product-fit filter at this stage only if very obvious — e.g. residential-only firms for a commercial B2B product)
3. TAM = Total relevant firms × ACV

**For B2C products:**
1. Find the total consumer population in the target geography (US Census, APPA, Statista, trade associations)
2. Find the % in the target demographic/behavioral segment
3. TAM = Segment population × annual spend per person

**Search queries to use:**
- `"[industry] number of [businesses/firms/brands] US 2024"`
- `"NAICS [code] firm count employees revenue"`
- `"[consumer category] number of [households/users/owners] US"`
- `"[category] market size 2024"` (for cross-reference only — not the primary method)

#### 2B — Top-down method (SECONDARY cross-check)
1. Find total category market size from analyst reports (Grand View, IMARC, Mordor, Precedence, IBISWorld)
2. Apply funnel: Total market → relevant segment → product-type share → geography
3. Search: `"[category] software/product market size 2024"` or `"[category] industry revenue US 2024"`

**Rule:** Bottom-up is the primary method. Top-down is the cross-check. Both results should be reported. If they diverge significantly (>2×), explain why (e.g. top-down only counts current spenders; bottom-up counts total potential).

#### TAM output format:
- Single dollar figure (round to nearest $100M for large markets, $10M for mid-size)
- Conservative range (low–high)
- The math shown explicitly: `N firms × $X ACV = $Y` or `N consumers × $Z annual spend = $Y`

### STEP 3 — SAM (Serviceable Addressable Market)

SAM = the subset of TAM that the specific product can actually serve today, given its business model, geography, language, and product fit.

**Universal filter checklist — apply all that are relevant:**

| Filter | Typical reduction | How to estimate |
|--------|------------------|----------------|
| Geography | Varies | If US-only product, filter out non-US. If city-level, apply metro population fraction. |
| Product-fit segment | 30–60% reduction | Remove segments the product doesn't serve (e.g. residential-only for commercial SaaS; solo operators who can't justify the cost) |
| Tech/channel readiness | 10–30% reduction | % of target customers with internet access, cloud tools, or relevant distribution channel access |
| Language/regulatory | Varies | Only relevant for global products |
| Willingness to pay tier | 20–40% reduction | Remove segments priced out of the product's tier |

**Formula:** SAM = TAM × Filter₁ × Filter₂ × ... × Filterₙ

**Blended ACV for SAM:** If there are multiple customer segments (SME vs. mid-market, or mass vs. premium), calculate a weighted average ACV:
`Blended ACV = (Segment_A_ACV × weight_A) + (Segment_B_ACV × weight_B)`

**Search queries for filter data:**
- `"[industry] percentage [commercial/residential/enterprise/SMB]"`
- `"[industry] small business cloud software adoption rate"`
- `"[consumer category] premium vs mass market share"`

#### SAM output format:
- Single dollar figure with conservative range
- Every filter listed with its % reduction and data source
- Blended ACV (if applicable)

### STEP 4 — SOM (Serviceable Obtainable Market)

SOM = the portion of SAM the product can realistically capture in a defined timeframe (typically 3 years / Year 1–3 ramp).

**Penetration rate benchmarks by product type:**

| Product type | Year 1 | Year 3 | Source basis |
|---|---|---|---|
| New B2B SaaS (no category) | 0.1–0.3% of SAM | 1.5–3% of SAM | Andreessen Horowitz, OpenView benchmarks |
| New B2B SaaS (established category) | 0.3–0.8% | 3–7% | Category incumbents' early growth data |
| New B2C consumer brand (retail) | 0.05–0.2% of SAM | 0.5–2% | Nielsen new brand launch data |
| New B2C DTC subscription | 0.1–0.5% | 1–4% | DTC cohort benchmarks |
| New B2B physical product | 0.2–0.5% | 2–5% | Trade distribution ramp benchmarks |

**Cross-validation method:** Find 2–3 comparable companies (same category, similar stage) and anchor SOM to their reported early ARR/revenue. Search:
`"[similar company] [Series A / early revenue / ARR] raised [year]"`

**Formula:**
- SOM (Year 1) = SAM × Year 1 penetration rate
- SOM (Year 3) = SAM × Year 3 penetration rate
- Customer count = SOM ÷ Blended ACV (sanity check — does this number of customers feel achievable given go-to-market?)

#### SOM output format:
- Year 1 and Year 3 ARR/revenue targets
- Customer count at each stage
- Named comparable company validations
- Penetration rate used (with justification)

### STEP 5 — Reconcile and flag conflicts

After running both methods:

1. **If bottom-up TAM > top-down TAM:** Usually because the product creates new demand (not just shifting existing spend). State this explicitly.
2. **If bottom-up TAM < top-down TAM:** Often because the product is a niche within a large category. State which definition is being used.
3. **Always present a range**, not a single number, for TAM and SAM. Single numbers imply false precision.
4. **Flag the 3 most sensitive assumptions** — the ones where a change of ±20% would materially shift the output. These are the assumptions to validate with primary research.

## Source hierarchy (use in this order, stop when satisfied)

### Tier 1 — Primary/official sources (highest credibility)
- **US Census Bureau** / Economic Census — firm counts, employment, revenue by NAICS code
- **NAICS/SIC code databases** (siccode.com, census.gov) — industry firm counts
- **Industry trade associations** (APPA for pets, CFMA for construction, NMMA for marine, etc.)
- **SEC filings / public company 10-Ks** — addressable market disclosures
- **Government labour/business statistics** (BLS, SBA, ONS)

### Tier 2 — Reputable market research
- IBISWorld, Grand View Research, Mordor Intelligence, IMARC Group, Precedence Research, Statista
- Use these for: category market size, CAGR, segment shares
- Cross-reference at least 2 sources — market research firms often disagree by 20–40%

### Tier 3 — Comparable company evidence
- Funding announcements (TechCrunch, Crunchbase, Construction Dive, etc.)
- Public company revenue disclosures at IPO/Series B
- Use for: SOM cross-validation, ACV benchmarks, growth rate validation

### Tier 4 — Pricing/ACV benchmarks
- Competitor pricing pages (direct)
- G2, Capterra, Trustpilot reviews mentioning price
- Stripe, Monetizely, OpenView pricing guides (for B2B SaaS)

## ACV / pricing benchmarks by product type

| Product type | Typical ACV/ASP | Notes |
|---|---|---|
| SMB B2B SaaS (1–50 employees) | $3,000–$15,000/yr | 10–20% of value created |
| Mid-market B2B SaaS (50–500 employees) | $15,000–$60,000/yr | |
| Enterprise B2B SaaS (500+ employees) | $60,000–$500,000+/yr | |
| Consumer subscription (premium) | $100–$600/yr | |
| Consumer packaged goods (premium) | $30–$150/order, 6–12×/yr | |
| B2B physical product (SMB) | $5,000–$50,000/yr | Depends heavily on industry |
| B2C DTC brand (avg. LTV proxy) | 2–3× first-order value | |

## Common errors — check before finalising

| Error | How to catch it |
|---|---|
| "1% of a $10B market" without proof | Always verify with bottom-up customer count |
| Top-down only, no bottom-up | Always run both methods |
| Using global TAM when product is US-only | Apply geography filter explicitly |
| Including non-buyers in TAM (e.g. residential firms in a commercial B2B) | Apply product-fit filter before TAM finalisation |
| SOM penetration rate not benchmarked | Always cite at least one comp company |
| ACV not grounded in value or comp pricing | Always show the value math or comp reference |
| Treating TAM as "market size from report" uncritically | Check the report's definition matches your product's scope |
| Single number without range | Always show low–high range |

## Industry-specific data source cheat sheet

| Industry | Best firm-count source | Best market-size source | Key trade association |
|---|---|---|---|
| Construction / Trades | NAICS via siccode.com or Census | IBISWorld, CFMA Benchmarker | CFMA, AGC, NECA |
| Pet / Consumer packaged goods | Census NAICS 311 | APPA, Grand View, IMARC | APPA, PFI |
| Food & Beverage | Census NAICS 311/312 | Mordor, Grand View, Mintel | FMI, GMA |
| Beauty / Personal care | Census NAICS 325620 | Euromonitor, Grand View | PBA, CEW |
| Fashion / Apparel | Census NAICS 315 | McKinsey Fashion Report, Statista | AAFA |
| SaaS / Software | Crunchbase, G2 categories | Gartner, IDC, Forrester | Varies |
| Automotive | NAICS 441/336 | Ward's Auto, IHS Markit | NADA, SEMA |
| B2B Packaging | Census NAICS 322/326 | Grand View, Mordor | PMMI, FPA |

---

## Output format 
The output file is where you calculations are made. After collecting necessary data, make a step-by-step analysis & calculation on the file, finally yielding a summary and a comparison.
Produce a structured markdown document containing:
- Both methods in full, each covering TAM → SAM → SOM completely before moving to the next method. Each method include 3 sections (TAM, SAM, SOM), each with: headline figure + range, full calculation shown line by line, and key assumptions&sources listed
- A standalone section for all used figures' sources & assumptions.
- A summary: table with TAM / SAM / SOM figures (bottom-up and top-down side by side); a method comparison note explaining divergence if bottom-up and top-down differ by >2×

The following is an example markdown output with a structure you should follow: 

"""

# Market Sizing: BuildFlow AI
*AI-powered invoicing automation for HVAC and Electrical subcontractors — United States*

---

## Method 1: Bottom-up

### TAM

| Input | Value | Source |
|---|---|---|
| HVAC firms (NAICS 238220) | 88,738 | siccode.com / US Census |
| Electrical firms (NAICS 238210) | 55,951 | siccode.com / US Census |
| % doing GC-facing commercial work | 55% | SBA subcontractor mix data |
| ACV — HVAC SME tier | $7,500/yr | $1.5M avg. revenue × 0.5%; CFMA 2024 |
| ACV — Electrical SME tier | $10,000/yr | $2.0M avg. revenue × 0.5%; CFMA 2024 |
| ACV — mid-market tier (>$5M rev) | $24,000/yr | Value-based; comp: Siteline pricing |

```
HVAC SME (48,806 × 82%):           40,021 × $7,500  = $300M
HVAC mid-market (48,806 × 18%):     8,785 × $24,000  = $211M
Electrical SME (30,773 × 82%):     25,234 × $10,000  = $252M
Electrical mid-market (30,773×18%): 5,539 × $24,000  = $133M
Value-based ceiling (5% leakage × 10–20% SaaS capture): ~$1.87B
```

**→ TAM: $1.87B (range: $1.5B–$2.2B)**

### SAM

| Filter | Reduction | Remaining | Source |
|---|---|---|---|
| Remove residential-only operators | −40% | 47,748 firms | SBA / IBISWorld industry mix |
| Remove solo / owner-only operators | −35% | 31,037 firms | Census nonemployer statistics |
| Remove cloud / tech-unready firms | −25% | 23,278 firms | Construction tech adoption surveys 2024 |

```
Blended ACV:
  SME tier (70%):     $7,500  × 0.70 = $5,250
  Mid-market (30%):   $18,000 × 0.30 = $5,400
  Blended:                            = $10,650/yr

23,278 firms × $10,650 + mid-market uplift ≈ $560M
```

**→ SAM: $560M (range: $430M–$690M)**

### SOM

| Year | % of SAM | ARR | Customers |
|---|---|---|---|
| Year 1 | 0.27% | ~$1.5M | ~140 |
| Year 2 | 0.85% | ~$4.8M | ~450 |
| Year 3 | 1.5–3.0% | $8.4M–$16.8M | 790–1,580 |

*Benchmark: 1.5–3% of SAM by Year 3 — a.H./OpenView SaaS benchmarks for new B2B entrant in established category*

| Comp | Signal |
|---|---|
| Payra | Raised $15M (Edison Partners); AP automation for construction subcontractors |
| Siteline | Raised $18M Series A; subcontractor billing / SOV management, comparable ICP |
| Adaptive Construction Solutions | Bootstrapped to ~$5M ARR in 3 years; construction AR automation |

**→ SOM: $1.5M ARR (Year 1) / $8.4M–$16.8M ARR (Year 3), ~790–1,580 customers**

---

## Method 2: Top-down

### TAM

```
Global construction accounting software (2025):  $2.64B  [Precedence Research]
× US share (76%):                                 $2.0B
× AP/AR segment (54.4%):                          $1.09B
```

**→ TAM: $1.09B**

### SAM

```
Top-down TAM:                        $1.09B
× Specialty trade sub-share (~28%):  $305M
× HVAC + Electrical only (~50%):     $152M
```

**→ SAM: $152M**

### SOM

```
SAM (top-down):              $152M
× 3% Year 3 penetration:     $4.6M
```

**→ SOM: $0.4M ARR (Year 1) / $4.6M ARR (Year 3)**

---

## Sources

| Input | Value assumed | Source |
|---|---|---|
| HVAC firms (NAICS 238220) | 88,738 | siccode.com / US Census |
| Electrical firms (NAICS 238210) | 55,951 | siccode.com / US Census |
| % GC-facing commercial work | 55% | SBA subcontractor mix data |
| Avg. HVAC subcontractor revenue | $1.5M/yr | CFMA 2024 Benchmarker |
| Avg. Electrical subcontractor revenue | $2.0M/yr | CFMA 2024 Benchmarker |
| Subcontractor net profit margin | 2.2–3.5% | CFMA 2024 Benchmarker |
| Profit lost to unbilled/errors | ~5% of revenue | Industry estimate |
| Global construction accounting software market | $2.64B (2025) | Precedence Research |
| AP/AR segment share | 54.4% | Precedence Research |
| Cloud/tech readiness of small construction firms | ~75% | Construction tech adoption surveys 2024 |
| SaaS penetration benchmark (Year 3) | 1.5–3% of SAM | a.H./OpenView SaaS benchmarks |
| Comp: Payra raise | $15M | Edison Partners announcement |
| Comp: Siteline raise | $18M Series A | Public announcement |

---

## Summary

| | Bottom-up | Top-down |
|---|---|---|
| **TAM** | $1.87B | $1.09B |
| **SAM** | $560M | $152M |
| **SOM — Year 1 / Year 3** | $1.5M / $8.4M–$16.8M ARR | $0.4M / $4.6M ARR |

> Bottom-up preferred — top-down counts only existing software spend and misses the large paper/spreadsheet segment. Use top-down as the floor / downside scenario.
"""

## Quality checklist before delivering output

- [ ] Both bottom-up AND top-down methods calculated
- [ ] Every input number has a named source
- [ ] TAM and SAM shown as ranges, not single numbers
- [ ] Blended ACV used where multiple customer segments exist
- [ ] SOM penetration rate benchmarked against 1–2 comp companies
- [ ] At least 3 sensitivity risks flagged
- [ ] Part 1 markdown follows the Output Example structure exactly
- [ ] Prose narration follows all 6 workflow steps
- [ ] Top-down vs bottom-up divergence explained if >2×
