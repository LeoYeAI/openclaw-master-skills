# Example: B2B SaaS / AI Tool

**Use this file when the product is:** software or an AI tool sold to businesses on a subscription or per-seat basis. Includes: vertical SaaS, horizontal SaaS, AI copilots, workflow automation tools, API platforms, data products.

---

## Worked case: BuildFlow AI
*AI-powered invoicing automation for HVAC and Electrical subcontractors — United States*

### Product classification
- **Model:** B2B-SaaS
- **Buyer:** Operations manager / owner at specialty trade subcontractor firm
- **Revenue unit:** Annual SaaS subscription per firm
- **Geography:** US-only

---

### Step 1 — Revenue unit definition

The revenue unit is a SaaS subscription sold to an HVAC or Electrical subcontractor firm at $7,500–$18,000 ACV/year depending on firm size.

**Pricing derivation (value-based):**
- Core value proposition: recover ~5% of annual revenue lost to unbilled materials and invoice rejection errors
- For a firm doing $1.5M/year: recoverable value = $75,000/yr
- SaaS pricing at 10–20% of value created = $7,500–$15,000 ACV (SME tier)
- For mid-market firms ($5M+ revenue): recoverable value = $250,000+; ACV = $20,000–$30,000
- Comp check: Siteline (subcontractor billing SaaS) charges $500–$1,500/month = $6,000–$18,000 ACV ✓

---

### Step 2 — TAM (Bottom-up)

**Universe identification via NAICS:**
- NAICS 238220 (HVAC contractors): 88,738 US firms — source: siccode.com / US Census
- NAICS 238210 (Electrical contractors): 55,951 US firms — source: siccode.com / US Census
- Total universe: 144,689 firms

**Gross TAM filter (obvious non-buyers only):**
- ~45% of firms are residential-only (no GC-facing invoicing workflow) → remove
- GC-facing pool: 144,689 × 55% = **79,579 firms**

**TAM calculation:**
```
HVAC SME (82% of 48,806):       40,021 × $7,500   = $300M
HVAC mid-market (18%):           8,785 × $24,000   = $211M
Electrical SME (82% of 30,773): 25,234 × $10,000   = $252M
Electrical mid-market (18%):     5,539 × $24,000   = $133M
                                               TAM = ~$896M (base)

Value-based ceiling:
Total GC-facing revenue pool: 79,579 avg $1.75M = $139B
5% leakage = $6.95B recoverable
SaaS capture 10–20% = $695M–$1.39B
Blended midpoint with mid-market uplift ≈ $1.87B
```

**TAM: $1.87B** (range: $1.5B–$2.2B)

---

### Step 3 — TAM (Top-down cross-check)

**Source:** Precedence Research, *Construction Accounting Software Market*, 2025

```
Global construction accounting software market: $2.64B
× US share (76%):                                $2.0B
× AP/AR segment (54.4% of category):             $1.09B  ← Top-down TAM
× Specialty trade sub-share (~28%):               $305M
× HVAC + Electrical only (~50%):                  $152M   ← Top-down SAM
```

**Top-down TAM: $1.09B**

**Divergence note:** Bottom-up ($1.87B) > Top-down ($1.09B) because top-down counts only existing software spend. BuildFlow AI also targets firms currently using paper/spreadsheets — a large segment with real willingness to pay but no current software budget. Bottom-up is preferred.

---

### Step 4 — SAM

**Filters applied to 79,579 GC-facing firms:**

| Filter | Rate | Remaining | Source |
|---|---|---|---|
| Remove residential-only | −40% | 47,748 | SBA, IBISWorld industry mix |
| Remove solo/owner-only operators | −35% | 31,037 | Census nonemployer statistics |
| Remove cloud/tech-unready | −25% | 23,278 | Construction tech adoption surveys 2024 |

**Blended ACV:**
```
SME tier (70% weight):        $7,500  × 0.70 = $5,250
Mid-market tier (30% weight): $18,000 × 0.30 = $5,400
Blended ACV:                                  = $10,650/yr
```

**SAM: $560M** (range: $430M–$690M)

---

### Step 5 — SOM

**Penetration benchmark:** 1.5–3% of SAM by Year 3 (a.H./OpenView benchmarks for new B2B SaaS in an established category)

| Year | Penetration | ARR | Customers |
|---|---|---|---|
| Year 1 | 0.27% | ~$1.5M | ~140 |
| Year 2 | 0.85% | ~$4.8M | ~450 |
| Year 3 | 1.5–3.0% | $8.4M–$16.8M | 790–1,580 |

**Comp validation:**
- **Payra** — AP automation for construction subcontractors; raised $15M (Edison Partners) at a similar ARR milestone
- **Siteline** — subcontractor billing/SOV management; raised $18M Series A with comparable ICP
- **Adaptive Construction Solutions** — construction AR automation; bootstrapped to ~$5M ARR in 3 years

**SOM (Year 3): $8.4M–$16.8M ARR**

---

### Key assumptions to validate

1. **55% GC-facing rate** — estimated from SBA data; validate with a 50-firm contractor survey
2. **5% revenue leakage** — industry estimate; validate with CFMA benchmarker or customer interviews
3. **Blended ACV $10,650** — based on value-based pricing logic; validate with willingness-to-pay interviews before pricing finalisation
4. **23,278 SAM firm count** — cloud-readiness filter (75%) is the most sensitive; check against construction tech adoption surveys annually

---

## B2B SaaS general notes

### Preferred data sources
- **Firm counts:** US Census NAICS lookup, siccode.com, Census Bureau Economic Census
- **Revenue/margin benchmarks:** CFMA (construction), MGMA (healthcare), SBA size standards
- **Market size cross-check:** Gartner, IDC, Forrester, Precedence Research, Grand View Research
- **ACV benchmarks:** OpenView SaaS Benchmarks, Stripe Atlas pricing guides, G2 competitor profiles
- **SOM comps:** Crunchbase, TechCrunch funding announcements, company press releases

### ACV benchmarks for B2B SaaS
| Firm size | Typical ACV |
|---|---|
| 1–10 employees | $1,200–$6,000/yr |
| 10–50 employees | $6,000–$15,000/yr |
| 50–200 employees | $15,000–$40,000/yr |
| 200–1,000 employees | $40,000–$120,000/yr |
| 1,000+ employees | $120,000–$500,000+/yr |

### Penetration rate guidance
- **Greenfield category (no incumbent software):** Year 3 SOM can reach 5–10% of SAM — buyers are looking for something
- **Established category (Excel → SaaS replacement):** 1.5–3% Year 3 is standard
- **Entrenched category (displacing existing SaaS):** 0.5–1.5% Year 3; assume long sales cycles

### Common B2B SaaS TAM/SAM errors
- Using employee headcount as proxy for firm count (will overstate by 10–20×)
- Including enterprise firms the product cannot serve (no enterprise sales motion)
- Forgetting that NAICS codes include inactive/dormant registrations — apply a ~10% "active and operating" discount for very small firm pools
