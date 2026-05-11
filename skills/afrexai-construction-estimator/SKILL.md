---
name: afrexai-construction-estimator
description: "Complete construction estimating and cost management system. Use when preparing project estimates, bid proposals, cost breakdowns, value engineering, change order management, or construction budget tracking. Covers residential, commercial, and infrastructure projects. Trigger on 'estimate', 'construction cost', 'bid', 'takeoff', 'cost breakdown', 'change order', 'value engineering', 'construction budget', 'unit pricing', 'RSMeans'."
---

# Construction Estimator Pro

> Complete construction estimating methodology — from quantity takeoff to bid submission. Zero dependencies.

---

## Phase 1: Project Classification & Estimate Type

### Estimate Type Decision Matrix

| Project Stage | Estimate Type | Accuracy | Basis | Use Case |
|---|---|---|---|---|
| Concept | Order of Magnitude | -30% to +50% | SF/unit costs | Go/no-go decisions |
| Schematic | Conceptual/Budget | -15% to +30% | Assembly costs | Budget approval |
| Design Dev | Detailed | -10% to +15% | Quantity takeoff | GMP/bid preparation |
| Construction Docs | Definitive/Bid | -5% to +10% | Full QTO + subs | Lump sum bid |
| Construction | Control | Actual costs | Committed + forecast | Cost management |

### Project Brief YAML

```yaml
project:
  name: ""
  number: ""
  type: residential | commercial | industrial | infrastructure | renovation
  delivery: design-bid-build | design-build | CM-at-risk | IPD
  location:
    city: ""
    state: ""
    zip: ""
    location_factor: 1.00  # RSMeans city cost index / national average
  owner: ""
  architect: ""
  
scope:
  gross_sf: 0
  stories: 0
  site_acres: 0
  description: ""
  
schedule:
  bid_date: ""
  construction_start: ""
  substantial_completion: ""
  duration_months: 0
  
estimate:
  type: order-of-magnitude | conceptual | detailed | definitive
  base_date: ""  # Date costs are based on
  escalation_rate: 0.04  # Annual construction cost escalation
  
assumptions:
  - ""
exclusions:
  - ""
allowances:
  - item: ""
    amount: 0
```

### Project Type Quick Reference

| Type | Key Considerations | Typical $/SF Range (2024-2026) |
|---|---|---|
| Single Family Residential | Foundation type, finishes grade, energy code | $150-$400/SF |
| Multi-Family | Unit mix, parking ratio, amenities | $200-$450/SF |
| Office (Class A) | Curtain wall, MEP density, TI allowance | $250-$550/SF |
| Retail | Shell vs TI, storefront, grease traps | $150-$350/SF |
| Healthcare/Hospital | Life safety, med gas, shielding | $400-$900/SF |
| K-12 Education | Prevailing wage, hazmat, phasing | $300-$600/SF |
| Warehouse/Distribution | Clear height, slab flatness, dock count | $80-$180/SF |
| Hotel | Star rating drives finish, FF&E budget | $200-$500/SF |
| Infrastructure (road/mile) | Soil conditions, utilities, traffic control | $2M-$10M/mile |

---

## Phase 2: Quantity Takeoff (QTO)

### CSI MasterFormat Division Structure

Use CSI MasterFormat 2018 for ALL estimates. Every line item maps to a division.

| Division | Name | Typical % of Total |
|---|---|---|
| 01 | General Requirements | 8-12% |
| 02 | Existing Conditions | 1-5% |
| 03 | Concrete | 8-15% |
| 04 | Masonry | 2-6% |
| 05 | Metals (Structural Steel) | 8-15% |
| 06 | Wood, Plastics, Composites | 3-8% |
| 07 | Thermal & Moisture Protection | 4-8% |
| 08 | Openings (Doors/Windows) | 3-7% |
| 09 | Finishes | 8-15% |
| 10 | Specialties | 1-3% |
| 11 | Equipment | 1-5% |
| 12 | Furnishings | 1-5% |
| 13 | Special Construction | 0-3% |
| 14 | Conveying Equipment (Elevators) | 1-4% |
| 21 | Fire Suppression | 2-4% |
| 22 | Plumbing | 4-8% |
| 23 | HVAC | 8-15% |
| 26 | Electrical | 8-15% |
| 27 | Communications | 1-3% |
| 28 | Electronic Safety & Security | 1-3% |
| 31 | Earthwork | 3-8% |
| 32 | Exterior Improvements | 2-6% |
| 33 | Utilities | 2-5% |

### QTO Best Practices

1. **Measure twice, price once** — QTO errors cascade through the entire estimate
2. **Use consistent units** — SF for areas, LF for linear, CY for volume, EA for items
3. **Add waste factors by material:**
   - Concrete: 5-8%
   - Masonry: 3-5%
   - Drywall: 10-12%
   - Roofing: 8-10%
   - Flooring (tile): 10-15%
   - Lumber: 8-10%
   - Rebar: 5-7%
   - Paint: 10-15%
4. **Document measurement methodology** — so anyone can verify
5. **Cross-check totals** — SF of drywall ≈ 2.5-3x floor area (both sides of walls + ceilings)

### QTO Line Item Template

```yaml
line_item:
  division: "03"
  spec_section: "03 30 00"
  description: "Cast-in-Place Concrete - Elevated Slabs"
  quantity: 450
  unit: CY
  unit_cost:
    labor: 85.00
    material: 165.00
    equipment: 25.00
    subcontractor: 0.00
  total_unit_cost: 275.00
  extended_cost: 123750.00
  waste_factor: 0.07
  adjusted_quantity: 481.5
  notes: "4500 PSI, #5 rebar @ 12\" OC EW, 6\" slab"
  source: "Sub quote - ABC Concrete (02/15/2026)"
  confidence: high | medium | low
```

### Quantity Verification Cross-Checks

| Check | Formula | Flag If |
|---|---|---|
| Concrete per SF | Total CY ÷ Building SF | >0.15 CY/SF (unless heavy structure) |
| Steel per SF | Total tons ÷ Building SF | >15 PSF (unless high-rise) |
| Drywall SF | Total drywall SF ÷ Floor SF | <2.0 or >4.0 ratio |
| Electrical per SF | Electrical $ ÷ Building SF | >$35/SF (standard office) |
| Plumbing fixtures | Count vs occupancy | Missing fixtures for code compliance |
| Parking spaces | Per local code requirements | Below minimum ratio |

---

## Phase 3: Pricing & Cost Assembly

### Unit Cost Development

**Cost source hierarchy (most reliable first):**
1. **Subcontractor quotes** (3 minimum per trade) — best for bid estimates
2. **Historical project data** — adjusted for location, time, scope
3. **RSMeans/Gordian data** — industry standard reference
4. **Vendor quotes** — for specific materials/equipment
5. **Published cost guides** — Marshall & Swift, Craftsman

### Labor Cost Build-Up

```yaml
labor_rate_build_up:
  trade: "Carpenter"
  base_wage: 42.50
  fringe_benefits: 18.75   # Health, pension, vacation, training
  payroll_taxes: 8.90      # FICA, FUTA, SUTA, workers comp
  total_burden: 27.65
  burdened_rate: 70.15
  
  productivity_factors:
    weather: 1.00           # 1.0 = normal, 1.15 = winter
    overtime: 1.00          # 1.0 = straight time, 1.5 = OT
    height: 1.00            # 1.0 = ground, 1.10 = >30ft
    congestion: 1.00        # 1.0 = open, 1.15 = tight
    shift: 1.00             # 1.0 = day, 1.10 = swing, 1.15 = night
  adjusted_rate: 70.15
```

### Subcontractor Quote Evaluation

Score each sub quote (use minimum 3 per trade):

| Factor | Weight | 1-5 Score |
|---|---|---|
| Price competitiveness | 30% | |
| Scope completeness (covers all spec sections?) | 25% | |
| Qualifications/exclusions (red flags?) | 20% | |
| Past performance/reputation | 15% | |
| Bond capacity/insurance | 10% | |
| **Weighted Total** | 100% | |

**Red flags in sub quotes:**
- "As needed" or "TBD" line items (scope gap)
- Short validity period (<30 days)
- Unusual exclusions (e.g., electrician excluding wire)
- No reference to spec sections
- Price significantly below others (they missed something)

### Crew Rate Assembly

```
Crew Daily Cost = Σ(Workers × Daily Rate) + Equipment Daily Cost
Crew Daily Output = Units per 8-hour day (from labor standards)
Unit Cost = Crew Daily Cost ÷ Crew Daily Output
```

**Example — Concrete Placement Crew:**
- 1 Foreman @ $75/hr × 8 = $600
- 4 Laborers @ $55/hr × 8 = $1,760
- 1 Vibrator operator @ $60/hr × 8 = $480
- Concrete pump (daily rental) = $1,200
- **Crew Daily Cost = $4,040**
- Daily output: 50 CY
- **Unit Labor+Equipment Cost = $80.80/CY**
- Material (concrete delivered) = $165/CY
- **Total in-place cost = $245.80/CY**

---

## Phase 4: Indirect Costs & Markups

### General Conditions (Division 01) Checklist

| Item | Duration-Based? | Typical Range |
|---|---|---|
| Project Manager | Yes | $12K-$18K/month |
| Superintendent | Yes | $10K-$16K/month |
| Project Engineer | Yes | $8K-$12K/month |
| Field Office (trailer) | Yes | $1K-$3K/month |
| Temporary utilities | Yes | $2K-$5K/month |
| Temporary toilets | Yes | $200-$500/month each |
| Dumpsters/waste removal | Yes | $1K-$4K/month |
| Safety equipment/supplies | Yes | $500-$2K/month |
| Small tools & consumables | Lump | 1-2% of labor |
| Final cleaning | Lump | $0.15-$0.50/SF |
| Permits (building) | Lump | Varies by jurisdiction |
| Insurance (Builder's Risk) | Lump | 0.5-1.5% of cost |
| Performance/Payment Bond | Lump | 1-3% of contract |
| Testing & inspection | Lump | 0.5-1.5% of cost |
| As-built documentation | Lump | $5K-$25K |
| Commissioning support | Lump | $10K-$50K |

**Rule of thumb:** General conditions = 8-15% of direct costs (lower for large projects, higher for small/complex).

### Markup Stack

```yaml
markup_calculation:
  direct_costs: 2500000
  
  general_conditions:
    percentage: 0.10
    amount: 250000
    
  subtotal_1: 2750000
  
  overhead:
    percentage: 0.05     # Home office overhead
    amount: 137500
    
  subtotal_2: 2887500
  
  profit:
    percentage: 0.05     # Varies by market/risk
    amount: 144375
    
  subtotal_3: 3031875
  
  contingency:
    design_contingency: 0.05    # For incomplete drawings
    construction_contingency: 0.03  # For unforeseen conditions
    amount: 242550
    
  bond:
    percentage: 0.015
    amount: 49118
    
  escalation:
    rate: 0.04           # Annual
    months_to_midpoint: 8
    amount: 88536
    
  total_estimate: 3412079
  cost_per_sf: 341.21    # For 10,000 SF building
```

### Contingency Guide

| Estimate Type | Design Contingency | Construction Contingency |
|---|---|---|
| Order of Magnitude | 15-25% | 10-15% |
| Conceptual | 10-15% | 5-10% |
| Detailed | 3-8% | 3-5% |
| Definitive/Bid | 0-3% | 2-3% |

**Contingency is NOT profit padding.** Track and justify every contingency draw.

---

## Phase 5: Bid Preparation & Strategy

### Bid/No-Bid Decision Scorecard

Score 1-5 for each (minimum 30 to bid):

| Factor | Weight | Score |
|---|---|---|
| Project type experience | 3x | |
| Client relationship/history | 2x | |
| Current workload capacity | 3x | |
| Geographic fit | 2x | |
| Profit potential | 3x | |
| Competition level (fewer = better) | 2x | |
| Risk profile (lower = better) | 3x | |
| Schedule feasibility | 2x | |
| Bonding capacity available | 2x | |
| **Weighted Total** | /110 | |

### Bid Day Checklist

**48 hours before:**
- [ ] All sub quotes received (minimum 3 per trade)
- [ ] All material quotes current (check expiration dates)
- [ ] Addenda reviewed and incorporated (ALL of them)
- [ ] Scope gaps identified and plugged
- [ ] Math verified (independent check)

**Day of bid:**
- [ ] Final sub quotes plugged in
- [ ] Markup/profit decision finalized
- [ ] Alternates priced if required
- [ ] Unit prices calculated if required
- [ ] Bid bond secured
- [ ] Bid form completed correctly (every blank filled)
- [ ] Acknowledge ALL addenda on bid form
- [ ] Authorized signature
- [ ] Delivered before deadline (allow 1+ hour buffer)

### Competitive Bid Strategy

**Market conditions affect markup:**
- Hot market (lots of work): Markup 8-12% (O&P combined)
- Normal market: Markup 6-10%
- Slow market: Markup 3-6%
- Must-win/strategic: Markup 2-4% (minimum to cover overhead)

**Bid spread analysis** (track your results):
```
Bid Spread = (Your Bid - Low Bid) ÷ Low Bid × 100
```
- Consistently >10% high → Your costs are inflated or productivity assumptions too conservative
- Consistently <2% from low → You might be leaving money on the table
- Target: Within 3-5% of winning bid

---

## Phase 6: Value Engineering (VE)

### VE Opportunity Matrix

| System | VE Opportunity | Typical Savings | Risk Level |
|---|---|---|---|
| Structural | Steel vs concrete frame | 5-15% of structure | Medium |
| Foundations | Spread vs mat vs piles | 10-30% of foundation | High (geotech dependent) |
| Envelope | Curtain wall vs storefront | 15-30% of facade | Low-Medium |
| Roofing | TPO vs modified bitumen | 10-20% of roofing | Low |
| Mechanical | VAV vs VRF | 10-25% of HVAC | Medium |
| Electrical | LED fixtures, panel optimization | 5-15% of electrical | Low |
| Finishes | Material substitutions | 10-40% of finishes | Low |
| Site | Reduce import/export of soil | 10-30% of sitework | Medium |

### VE Proposal Template

```yaml
ve_item:
  number: VE-001
  description: "Substitute VRF system for conventional VAV"
  division: "23"
  
  original:
    description: "VAV air handling system with ductwork"
    cost: 850000
    
  proposed:
    description: "Variable Refrigerant Flow (VRF) with DOAS"
    cost: 680000
    
  savings: 170000
  savings_pct: 20%
  
  impact:
    schedule: "Reduces mechanical rough-in by 2 weeks"
    quality: "Better zone control, lower operating cost"
    maintenance: "Higher per-unit cost but less ductwork"
    code_compliance: "Meets ASHRAE 90.1, verify local amendments"
    
  risk: medium
  recommendation: accept | reject | modify
  requires_redesign: yes | no
  redesign_cost: 15000
  net_savings: 155000
```

### VE Decision Rules

1. **Never VE life safety** — fire protection, structural integrity, egress
2. **Calculate lifecycle cost** — cheap upfront ≠ cheap over 20 years
3. **Get architect/engineer sign-off** before bidding VE alternates
4. **Document everything** — VE that isn't documented becomes a scope gap
5. **Owner decides** — present options with data, let them choose

---

## Phase 7: Change Order Management

### Change Order Pricing Rules

**Contractor markup on changes (typical):**
| Tier | Self-Performed Work | Subcontractor Work |
|---|---|---|
| Overhead | 10% | 5% |
| Profit | 10% | 5% |
| Bond | Add actual % | Add actual % |

**Time & Material (T&M) documentation requirements:**
- Daily time sheets signed by owner's rep
- Material invoices with delivery tickets
- Equipment logs with hours
- Photos of work in progress

### Change Order YAML Template

```yaml
change_order:
  number: CO-001
  date: ""
  description: ""
  
  reason:
    type: owner-directed | unforeseen-condition | design-error | code-change | scope-clarification
    rfi_number: ""
    
  cost_breakdown:
    labor:
      hours: 0
      rate: 0
      total: 0
    material:
      items: []
      total: 0
    equipment:
      items: []
      total: 0
    subcontractor:
      items: []
      total: 0
    direct_cost: 0
    markup: 0.15
    total_cost: 0
    
  schedule_impact:
    days: 0
    critical_path: yes | no
    explanation: ""
    
  status: pending | approved | rejected | negotiating
```

### Change Order Negotiation Tips

1. **Price it immediately** — delay weakens your position
2. **Submit with backup** — labor rates, material quotes, productivity analysis
3. **Separate time from money** — negotiate schedule impact independently
4. **Track cumulative impact** — 20 small changes = major schedule disruption (even if each is "0 days")
5. **Constructive acceleration** — if owner delays approval but expects same completion, document it
6. **Unit price book** — agree on unit prices at contract start for common change types

---

## Phase 8: Cost Control During Construction

### Earned Value Management (EVM)

```
Budget at Completion (BAC) = Total budget
Planned Value (PV) = Budgeted cost of work scheduled
Earned Value (EV) = Budgeted cost of work performed
Actual Cost (AC) = Actual cost of work performed

Schedule Performance Index (SPI) = EV / PV
  >1.0 = ahead of schedule
  <1.0 = behind schedule

Cost Performance Index (CPI) = EV / AC
  >1.0 = under budget
  <1.0 = over budget

Estimate at Completion (EAC) = BAC / CPI
Variance at Completion (VAC) = BAC - EAC
```

### Monthly Cost Report Template

```yaml
cost_report:
  project: ""
  period: ""
  report_date: ""
  
  summary:
    original_contract: 0
    approved_changes: 0
    pending_changes: 0
    current_budget: 0
    committed_cost: 0      # Subcontracts + POs
    actual_cost_to_date: 0
    forecast_to_complete: 0
    estimate_at_completion: 0
    variance: 0
    contingency_remaining: 0
    
  schedule:
    percent_complete: 0
    spi: 0
    cpi: 0
    days_ahead_behind: 0
    
  cash_flow:
    billed_to_date: 0
    collected_to_date: 0
    retention_held: 0
    
  risk_items:
    - description: ""
      potential_cost: 0
      probability: high | medium | low
      mitigation: ""
```

### Cost Control Red Flags

| Signal | What It Means | Action |
|---|---|---|
| CPI < 0.95 in first 25% | Systemic cost overrun | Root cause analysis NOW |
| Contingency burn > schedule % | Burning contingency too fast | Tighten change management |
| >5 pending COs unsigned | Cash flow risk, scope dispute | Escalate to PM/owner |
| Sub invoices > committed | Sub performing extra work | Verify scope, issue CO or stop work |
| Retainage release requests early | Sub cash flow problems | Monitor closely, check lien waivers |

---

## Phase 9: Specialty Estimate Types

### Renovation/Remodel Estimating

**Add these factors to renovation estimates:**
- Selective demolition: Price item-by-item (never lump sum)
- Hazmat survey: Asbestos ($3-5K), lead paint ($2-4K) — MANDATORY before bid
- Abatement: 2-5x removal cost vs new construction equivalent
- Protection of existing: Dust barriers, floor protection, HVAC isolation
- Working hours: Occupied buildings = nights/weekends = premium labor
- Discovery allowance: 10-15% for hidden conditions behind walls
- Temporary facilities: HVAC, power, restrooms during renovation
- Phasing/sequencing: Adds 15-30% management overhead

### Sitework Estimating

**Critical factors:**
```yaml
sitework_checklist:
  geotechnical:
    - Soil bearing capacity
    - Water table depth  
    - Rock depth (blasting vs mechanical?)
    - Contamination (Phase I/II ESA results)
    
  earthwork:
    cut_cy: 0
    fill_cy: 0
    import_export: 0    # Net CY to haul
    haul_distance_miles: 0
    compaction_required: standard | proctor_95 | proctor_98
    
  utilities:
    water_tap_fee: 0
    sewer_tap_fee: 0
    fire_line: 0
    storm_detention: required | not_required
    
  paving:
    asphalt_sy: 0
    concrete_sy: 0
    curb_lf: 0
    striping_lf: 0
    
  landscape:
    sod_sf: 0
    trees_ea: 0
    irrigation: yes | no
    erosion_control: silt_fence | inlet_protection | retention_pond
```

### MEP (Mechanical/Electrical/Plumbing) Quick Checks

| System | $/SF Benchmark (Commercial Office) | Flag If |
|---|---|---|
| HVAC | $25-$50/SF | >$55 or <$20 |
| Plumbing | $12-$25/SF | >$30 or <$8 |
| Fire Protection | $4-$8/SF | >$10 or <$3 |
| Electrical (power) | $18-$35/SF | >$40 or <$12 |
| Low voltage/data | $5-$12/SF | >$15 or <$3 |
| **Total MEP** | **$64-$130/SF** | **>$150 or <$46** |

---

## Phase 10: Escalation & Location Adjustments

### Construction Cost Escalation

```
Future Cost = Current Cost × (1 + Annual Rate) ^ (Months to Midpoint ÷ 12)
```

**Recent escalation trends (US):**
- 2020-2022: 8-15% annually (pandemic/supply chain)
- 2023-2024: 4-6% annually (normalizing)
- 2025-2026 forecast: 3-5% annually
- Long-term average: 3-4% annually

**Always escalate to the MIDPOINT of construction**, not the start.

### Location Factor Application

```
Local Cost = National Average Cost × City Cost Index
```

**Sample RSMeans City Cost Indices (100 = national average):**

| City | Index | | City | Index |
|---|---|---|---|---|
| New York, NY | 130-145 | | Dallas, TX | 88-95 |
| San Francisco, CA | 125-140 | | Atlanta, GA | 90-97 |
| Boston, MA | 115-130 | | Phoenix, AZ | 88-94 |
| Chicago, IL | 110-120 | | Denver, CO | 95-105 |
| Seattle, WA | 108-118 | | Nashville, TN | 88-95 |
| Washington, DC | 100-110 | | Charlotte, NC | 85-92 |
| Miami, FL | 92-100 | | Houston, TX | 85-93 |
| Minneapolis, MN | 105-112 | | Rural areas | 70-85 |

---

## Phase 11: Estimate Quality Review

### 100-Point Estimate Quality Rubric

| Dimension | Weight | Criteria |
|---|---|---|
| **Scope completeness** | 20 | All spec sections priced, no gaps, exclusions documented |
| **Quantity accuracy** | 20 | QTO verified, cross-checks pass, waste factors applied |
| **Pricing basis** | 15 | 3+ sub quotes per trade, current material prices, documented sources |
| **Indirect costs** | 10 | GCs detailed (not lump), schedule-based items tied to duration |
| **Markup appropriateness** | 10 | Market-competitive, risk-adjusted, contingency justified |
| **Documentation** | 10 | Assumptions listed, basis of estimate narrative, organized by division |
| **Adjustments** | 10 | Location factor applied, escalation to midpoint, seasonal factors |
| **Presentation** | 5 | Professional format, clear summary, alternates separated |

**Grading:** 90+ = Bid-ready | 75-89 = Needs refinement | 60-74 = Major gaps | <60 = Redo

### Peer Review Checklist

- [ ] All addenda acknowledged and incorporated?
- [ ] Spec sections cross-referenced to QTO? (no orphan specs)
- [ ] Sub quotes match scope of work? (read exclusions!)
- [ ] General conditions duration matches schedule?
- [ ] Bond premium calculated on TOTAL including markups?
- [ ] Sales tax applied correctly? (varies by state, some exempt)
- [ ] Prevailing wage rates used if required? (Davis-Bacon, state)
- [ ] Owner-furnished items excluded from pricing?
- [ ] Alternates priced separately and clearly?
- [ ] Math checked independently? (not just formula check — spot-check quantities)

---

## Phase 12: Common Mistakes & Edge Cases

### 10 Estimate-Killing Mistakes

| # | Mistake | Prevention |
|---|---|---|
| 1 | Missing addenda | Checklist: log every addendum, initial when incorporated |
| 2 | Incomplete sub scope | Write scope sheets with inclusions AND exclusions |
| 3 | Wrong labor rates | Verify union vs open shop, prevailing wage, location |
| 4 | No escalation | ALWAYS escalate to construction midpoint |
| 5 | Lump sum general conditions | Detail every line item tied to schedule |
| 6 | Ignoring phasing | Multi-phase = mobilize/demobilize multiple times |
| 7 | Missing temporary work | Shoring, dewatering, winter protection, dust control |
| 8 | Under-priced site conditions | Get geotech report BEFORE estimating foundations |
| 9 | Scope gaps between trades | Who installs the backing for the TV mount? |
| 10 | Not reading the fine print | Liquidated damages, retainage, payment terms |

### Edge Cases

**Occupied building renovation:**
- Work hours restriction → labor premium 15-40%
- Dust/noise control → add $2-5/SF
- Security/escort requirements → add supervision cost
- Existing condition discovery → 10-15% allowance minimum

**Remote/rural project:**
- Travel/per diem for crews → $150-$250/worker/day
- Material delivery premium → 5-15% depending on distance
- Limited sub market → fewer quotes, less competitive pricing
- Equipment mobilization → long haul costs for cranes, excavators

**Fast-track schedule:**
- Overtime premium → plan 20-30% labor cost increase
- Acceleration costs → additional supervision, equipment
- Out-of-sequence work → productivity losses 10-25%
- Premium material delivery → expediting fees

**Public/government work:**
- Prevailing wages → 20-40% labor cost increase
- DBE/MBE/WBE goals → subcontracting requirements, good faith effort
- Buy American/Buy America → material cost premium 10-30%
- Bid protest risk → ensure perfect compliance with ITB

**Design-Build:**
- Design contingency higher (incomplete docs at pricing)
- Self-perform vs sub trade-offs
- Design liability insurance (professional liability)
- Allowances for owner decisions not yet made

---

## Natural Language Commands

| Command | Action |
|---|---|
| "Estimate this project" | Run full estimate workflow from Phase 1 |
| "Price [division/trade]" | Develop unit costs for specific trade |
| "Check my quantities" | Run QTO verification cross-checks |
| "Value engineer [system]" | Generate VE alternatives with savings |
| "Write change order for [scope]" | Generate CO with pricing and backup |
| "Compare sub quotes for [trade]" | Score and compare subcontractor bids |
| "Monthly cost report" | Generate EVM-based cost report |
| "Bid/no-bid analysis for [project]" | Run decision scorecard |
| "Location adjust to [city]" | Apply RSMeans location factor |
| "Escalate costs to [date]" | Calculate escalation to future midpoint |
| "Review my estimate" | Run 100-point quality rubric |
| "Generate bid summary" | Format estimate for bid submission |
