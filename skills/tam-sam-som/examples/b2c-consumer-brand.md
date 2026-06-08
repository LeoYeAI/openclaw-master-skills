# Example: B2C Consumer Brand

**Use this file when the product is:** a consumer-facing brand sold direct-to-consumer (DTC), through retail, or via subscription. Includes: food & beverage, snacks, beauty, personal care, fashion/apparel, pet products, wellness, supplements, home goods.

---

## Worked case: Premium DTC Dog Food Brand
*Fresh, subscription-based dog meal plans — United States*

### Product classification
- **Model:** B2C-Subscription (DTC)
- **Buyer:** Dog-owning household, skewing urban/suburban, household income $75K+
- **Revenue unit:** Monthly subscription per household dog
- **Geography:** US-only (DTC shipping range)

---

### Step 1 — Revenue unit definition

The revenue unit is a recurring monthly meal subscription sold to a dog-owning household at ~$120/month = **$1,440/yr ACV per household.**

**Pricing derivation:**
- Segment: premium/fresh dog food (not dry kibble)
- Comp pricing: The Farmer's Dog $90–$180/month; Ollie $65–$120/month; Nom Nom $80–$150/month
- Median landed price: ~$120/month for a medium-sized dog
- Purchase frequency: 12×/year (subscription, monthly)

---

### Step 2 — TAM (Bottom-up)

**Universe identification:**
- US dog-owning households: 65.1 million — source: APPA 2023–2024 National Pet Owners Survey
- % who purchase premium/super-premium dog food: ~41% — source: Pet Food Institute 2023 State of the Industry

**TAM calculation:**
```
65.1M dog-owning households
× 41% premium purchasers
= 26.7M premium-oriented households
× $1,440 annual spend
= $38.4B (gross TAM)

Adjustment: not all premium buyers will pay DTC fresh-food prices
× 35% willing to pay fresh/DTC price point (vs. premium dry kibble)
= 9.35M households × $1,440 = $13.5B
```

**TAM: ~$13.5B** (range: $10B–$16B)

> Note: TAM is very sensitive to the "willing to pay fresh-food price" filter. This 35% figure is an estimate — validate with consumer surveys or use the top-down check as a tighter anchor.

---

### Step 3 — TAM (Top-down cross-check)

**Sources:**
- US pet food market total: $50.5B (APPA 2024)
- Premium/super-premium segment: ~28% share = $14.1B
- Fresh/minimally processed sub-segment: ~24% of premium = $3.4B
- DTC channel share within fresh: ~45% = $1.5B

**Top-down TAM: $3.4B** (fresh/premium category)
**Top-down SAM proxy: $1.5B** (DTC channel within fresh)

**Divergence note:** Bottom-up ($13.5B) >> Top-down ($3.4B) because bottom-up counts all potential premium buyers, including those currently buying premium kibble who *could* convert. Top-down reflects only current fresh/premium category spend. For a new entrant, the **top-down figure ($3.4B) is the more conservative and credible TAM** — it represents actual demonstrated willingness to pay at this price tier, not theoretical conversion of dry-food buyers. Use top-down as primary for B2C when the product is in an established premium category.

---

### Step 4 — SAM

**Filters applied to top-down TAM of $3.4B:**

| Filter | Rate | Basis |
|---|---|---|
| DTC-reachable (shipping logistics, no rural dead zones) | −15% | USPS/FedEx DTC reach data |
| Digital-acquisition-reachable (active online, social media) | −20% | Pew Research internet use by demographic |
| Within addressable income tier ($60K+ HHI) | already embedded in premium segment | APPA demographic data |
| Brand new entrant: exclude locked-in subscribers of Farmer's Dog / Ollie | −10% | Est. incumbent loyalty rate |

```
$3.4B × 0.85 × 0.80 × 0.90 = $2.1B
```

**SAM: $2.1B** (range: $1.8B–$2.4B)

---

### Step 5 — SOM

**Penetration benchmark:** 1–2% of SAM by Year 3 for new DTC subscription brand (Nielsen new brand benchmarks; DTC cohort data from Klaviyo/Triple Whale)

| Year | Penetration of SAM | Revenue | Customers |
|---|---|---|---|
| Year 1 | 0.1–0.2% | $2.1M–$4.2M | 1,460–2,900 HH |
| Year 2 | 0.4–0.6% | $8.4M–$12.6M | 5,800–8,750 HH |
| Year 3 | 0.8–1.5% | $16.8M–$31.5M | 11,700–21,900 HH |

**Comp validation:**
- **The Farmer's Dog** — raised $49M Series B at ~$50M ARR (approx. 3 years post-launch)
- **Ollie** — raised $35M at ~$30M ARR within first 4 years
- **Sundays for Dogs** — bootstrapped; reached $10M ARR Year 3 as a lean DTC operation
- Implies Year 3 SOM of $15M–$30M ARR is achievable with proper CAC/LTV management

**SOM (Year 3): $16.8M–$31.5M revenue**

---

### Key assumptions to validate

1. **41% premium buyer rate** — from APPA; validate with a 200-person consumer survey segmented by income and pet spending habits
2. **35% willing to pay fresh-food price point** — most sensitive assumption; a ±10% shift moves TAM by $4B
3. **$120/month ACV** — validate against competitor pricing at time of launch; fresh food pricing has been falling as category matures
4. **1–2% Year 3 penetration** — requires CAC <$150 and LTV >$900 (6+ month retention); validate with 90-day cohort before scaling spend

---

## B2C Consumer Brand general notes

### When to use top-down vs. bottom-up as primary
- **Use top-down as primary** when: the product is in an established premium category (fresh pet food, luxury skincare, craft spirits) — actual category spend is a better proxy for TAM than population × theoretical spend
- **Use bottom-up as primary** when: the product creates a new category or new price tier that doesn't yet have reported market data

### Preferred data sources by sub-category

| Category | Population source | Market size source | Spend data |
|---|---|---|---|
| Pet products | APPA National Pet Owners Survey | APPA, Grand View Research | APPA annual spend data |
| Food & Beverage | US Census, USDA | Mintel, Euromonitor, SPINS | Nielsen retail scan data |
| Beauty / Skincare | US Census (adult pop.) | Euromonitor, Grand View, Statista | NPD Group, Circana |
| Fashion / Apparel | US Census | McKinsey Fashion Report, Statista | NPD, US Census retail sales |
| Snacks / Beverages | US Census (adult pop.) | SPINS, IRI/Circana, Mintel | Nielsen, SPINS panel data |
| Supplements / Wellness | US Census | Grand View, IBIS | CRN annual survey |

### ACV / ASP benchmarks for B2C
| Tier | Annual spend per customer |
|---|---|
| Mass-market CPG | $50–$200/yr |
| Premium CPG / specialty retail | $200–$600/yr |
| DTC subscription (consumable) | $400–$1,800/yr |
| Luxury / high-end (fashion, beauty) | $500–$3,000+/yr |

### SAM filter guidance for B2C
Key filters and how to quantify them:
- **Income filter:** Use US Census income distribution; for premium products, typically target top 40–60% income bracket
- **Age/demographic filter:** Pew Research demographic surveys, Nielsen demographic indices
- **Channel filter (DTC vs. retail):** ~35–45% of US consumers make regular DTC online purchases; Statista / eMarketer
- **Geographic filter (if local/regional):** Nielsen DMA data, metro area census population

### Common B2C TAM/SAM errors
- Using total category revenue as TAM without filtering for your price tier (e.g. using "total dog food market $16B" when you're premium DTC — the mass market is not your TAM)
- Ignoring channel constraints — not all premium buyers will buy DTC (some only buy at Whole Foods or PetSmart)
- Assuming 100% of premium buyers will convert — always apply a realistic conversion filter based on comp brand penetration rates
- Conflating household count with individual count for pet/baby categories (one household may have multiple pets but is one subscription)
