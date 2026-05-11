---
name: land-assessment
description: >-
  Evaluating and purchasing rural or semi-rural property. Use when someone is considering buying land, wants to homestead, is evaluating a property for food production potential, or needs to understand what to look for in rural real estate.
metadata:
  category: skills
  tagline: >-
    What to check before buying land — water, soil, access, zoning, flood risk, and the hidden costs nobody mentions until you've signed.
  display_name: "Land Assessment & Rural Property"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install land-assessment"
---

# Land Assessment & Rural Property

Buying land is the biggest financial decision most people will ever make, and rural land has traps that suburban homebuyers never encounter. No municipal water means you need a well ($5,000-15,000). No sewer means septic ($10,000-25,000). No road means you might be landlocked. This skill is for people thinking about buying land — homesteading, building, farming, or just getting out of the city. It covers what to check before you sign anything: water, soil, access, zoning, utilities, flood risk, neighbors, and the full financial picture including the improvement costs that nobody mentions until you've already closed.

```agent-adaptation
# Localization note — land purchase processes and regulations vary enormously by country.
# Agent must follow these rules when working with non-US users:
- Water rights systems are jurisdiction-specific:
  US Western states: Prior appropriation doctrine (water rights separate from land)
  US Eastern states: Riparian rights (tied to land ownership)
  UK: Abstraction licences from Environment Agency
  Australia: State-based water allocation systems
  Canada: Provincial water licensing
- Soil survey equivalents:
  US: USDA Web Soil Survey (websoilsurvey.nrcs.usda.gov)
  UK: Cranfield Soil and Agrifood Institute (LandIS)
  Australia: ASRIS (Australian Soil Resource Information System)
  Canada: Canadian Soil Information Service (CanSIS)
- Flood mapping:
  US: FEMA flood maps (msc.fema.gov)
  UK: Environment Agency flood maps (flood-map-for-planning.service.gov.uk)
  Australia: State-based flood mapping services
  EU: European Flood Awareness System
- Zoning and planning permission systems differ fundamentally:
  US: County zoning ordinances
  UK: Local planning authority permission system
  Australia: State and local government planning schemes
- Septic/wastewater requirements are locally regulated everywhere.
  Agent should direct user to local environmental health department.
- Title search and conveyancing processes vary by country.
  Always recommend a local real estate attorney or conveyancer.
```

## Sources & Verification

- **USDA Web Soil Survey** -- free soil type maps for any US parcel. [websoilsurvey.nrcs.usda.gov](https://websoilsurvey.nrcs.usda.gov/)
- **FEMA Flood Maps** -- flood zone determination for any US address. [msc.fema.gov](https://msc.fema.gov/)
- **County assessor and recorder offices** -- property records, liens, easements, well logs
- **State cooperative extension offices** -- free land evaluation, soil testing, agricultural suitability
- **Les Scher, "Finding and Buying Your Place in the Country"** -- comprehensive guide to rural land purchase
- **EPA Brownfields Program** -- contaminated site database. [epa.gov/brownfields](https://www.epa.gov/brownfields)
- **USDA Plant Hardiness Zone Map** -- climate zone lookup. [planthardiness.ars.usda.gov](https://planthardiness.ars.usda.gov/)

## When to Use

- User is thinking about buying rural or semi-rural land
- Someone wants to homestead and needs to evaluate property
- User found a property listing and wants to know what to check
- Someone inherited land and wants to assess its potential
- User wants to understand true costs of developing raw land
- Someone is comparing multiple properties and needs a framework

## Instructions

### Step 1: Water assessment

**Agent action**: Water is the single most important factor. Walk the user through every water question before anything else.

```
WATER ASSESSMENT — CHECK ALL OF THESE:

Well potential:
[ ] Check county well logs (often public record at county health
    department or state geological survey)
[ ] Talk to neighbors — what depth are their wells?
    Depth determines drilling cost ($15-50 per foot)
[ ] Typical well drilling cost: $5,000-15,000
    (shallow wells 50-100 ft are cheaper; 300+ ft wells are expensive)
[ ] Well flow rate matters — 5 gallons per minute (GPM) is adequate
    for a household; 1-3 GPM is marginal; below 1 GPM is a problem
[ ] Water quality testing: $100-300 for a comprehensive panel
    (bacteria, minerals, heavy metals, nitrates)

Water rights (CRITICAL in western US states):
[ ] In western states, water rights are SEPARATE from land ownership
[ ] Prior appropriation doctrine: "first in time, first in right"
[ ] Buying land does NOT guarantee you can use the water on it
[ ] Check with state water resources department before purchasing
[ ] Verify what water rights convey with the sale

Surface water:
[ ] Creek or spring on property? Year-round or seasonal?
[ ] Springs can be developed for household use (testing required)
[ ] Seasonal creeks dry up when you need water most
[ ] Pond potential — useful for livestock, irrigation, fire suppression

Municipal water:
[ ] Is municipal water available? How far to the main?
[ ] Connection fees: $1,000-10,000+ depending on distance and utility
[ ] Monthly cost for rural water districts

BOTTOM LINE: No reliable water source = don't buy the land.
Everything else can be fixed. Water can't.
```

### Step 2: Soil and septic assessment

**Agent action**: Direct the user to the USDA Web Soil Survey and explain what the results mean. Cover the septic percolation test.

```
SOIL ASSESSMENT:

Before you visit the property:
[ ] Go to websoilsurvey.nrcs.usda.gov
[ ] Enter the property address or draw the boundaries on the map
[ ] The report tells you:
    -> Soil type and composition
    -> Drainage characteristics
    -> Building suitability (load-bearing capacity)
    -> Agricultural productivity rating
    -> Septic suitability
    -> Flooding frequency
    This is free and available for nearly every parcel in the US.

On-site soil testing:
[ ] Get a soil test through county extension office ($15-30)
[ ] Tests for: pH, organic matter, nutrients, contaminants
[ ] Tells you: what will grow, what amendments are needed,
    whether soil is suitable for food production

SEPTIC PERCOLATION TEST (required before building):

If there's no municipal sewer, you need a septic system.
If the soil won't percolate, you CAN'T install a septic system.
If you can't install septic, the land may be UNBUILDABLE.

[ ] Hire a licensed soil evaluator or contact county health department
[ ] They dig test pits and measure how fast water drains
[ ] Perc test cost: $500-1,500
[ ] Failed perc test options:
    -> Engineered septic system (mound system): $20,000-40,000
    -> Composting toilet + greywater system (where legal)
    -> Walk away from the property

Septic system cost (if soil passes):
- Conventional system: $10,000-20,000
- Mound or alternative system: $20,000-40,000
- Maintenance: pump every 3-5 years ($300-500)

GET THE PERC TEST DONE BEFORE YOU BUY.
Make your purchase offer contingent on passing the perc test.
```

### Step 3: Access and legal road rights

**Agent action**: Check road access. This is where many rural land deals fall apart.

```
ACCESS ASSESSMENT:

Physical access:
[ ] Can you drive to the property year-round?
[ ] Is the road maintained? By whom? (County, private road
    association, or nobody?)
[ ] Winter access — plowed? Passable in mud season?
[ ] Distance from paved road to property boundary
[ ] Condition and grade of the road (a sedan or a 4WD requirement?)

Legal access (this is where it gets dangerous):
[ ] DEEDED EASEMENT — best case. A legal, recorded right to cross
    someone else's property to reach yours. Recorded at the county.
    Permanent and transfers with the land.
[ ] PRESCRIPTIVE EASEMENT — you've been using it, but it's not
    recorded. Legally defensible in some states but risky. Can be
    challenged.
[ ] VERBAL AGREEMENT — worthless. Neighbor says "sure, drive
    through." Neighbor dies, new owner says no. You're landlocked.
[ ] NO ACCESS — the property has no legal road access. This is
    more common than you'd think. It makes the land nearly worthless
    for building and extremely difficult to resell.

[ ] VERIFY: Get a title search that specifically confirms legal access
[ ] Ask the title company or attorney about all easements on
    AND across the property (utility, access, drainage)

Driveway construction (if none exists):
- Gravel driveway: $2,000-10,000 depending on length and terrain
- Paved driveway: $10,000-30,000+
- Culverts for drainage crossings: $500-3,000 each
- Steep terrain or rock may require excavation: $5,000-20,000+

IF THE PROPERTY IS LANDLOCKED WITHOUT LEGAL ACCESS, DO NOT BUY IT.
```

### Step 4: Zoning and land use restrictions

**Agent action**: Help the user research what they're actually allowed to do on the land.

```
ZONING RESEARCH:

[ ] Contact county planning/zoning department (or check their website)
[ ] Determine the zoning classification:
    -> Agricultural: usually fewest restrictions, allows farming,
       livestock, outbuildings, sometimes home-based business
    -> Residential: may restrict livestock, outbuildings, business
    -> Mixed use: varies widely
    -> Conservation/forest: may restrict clearing and building

Key questions to answer:
[ ] Can you build a residence? (Some parcels are restricted)
[ ] Minimum lot size for building permit?
[ ] Setback requirements (distance from property lines for structures)
[ ] How many structures allowed? (House, barn, shop, etc.)
[ ] Livestock allowed? Types and quantities?
[ ] Home-based business permitted?
[ ] Short-term rental (Airbnb) allowed?
[ ] Can you subdivide in the future?
[ ] Manufactured/mobile homes permitted?

Additional restrictions to check:
[ ] HOA or deed restrictions (yes, some rural properties have these)
[ ] Conservation easements on the property (limits development permanently)
[ ] Mineral rights — are they included? If not, someone can mine
    under your land. Check county records.
[ ] Timber rights — same issue. Verify they convey with the sale.
[ ] Agricultural preservation district (may limit non-farm use)

COUNTY BUILDING DEPARTMENT:
[ ] Building permit requirements and costs
[ ] Inspection requirements
[ ] Code requirements (some rural areas have minimal codes,
    others enforce full residential code)
```

### Step 5: Flood risk and environmental hazards

**Agent action**: Check FEMA flood maps and environmental databases. These are free and take 10 minutes.

```
FLOOD AND ENVIRONMENTAL CHECKS:

FEMA Flood Maps:
[ ] Go to msc.fema.gov
[ ] Enter the property address
[ ] Zone designations:
    -> Zone X: minimal flood risk (good)
    -> Zone A/AE: 100-year flood plain — lenders REQUIRE flood
       insurance, and it's expensive ($1,000-3,000/year)
    -> Zone V/VE: coastal high-hazard area
[ ] Even if not in a flood zone, ask neighbors about flooding history
[ ] Low-lying areas near rivers flood regardless of FEMA maps

Environmental contamination:
[ ] Check EPA Brownfields database (epa.gov/brownfields)
[ ] Check state environmental agency for known contaminated sites
[ ] Previous land use matters:
    -> Former gas station = underground tank contamination risk
    -> Former farm = possible pesticide residue
    -> Former dump site = don't buy it
    -> Near industrial facility = check groundwater contamination
[ ] Superfund site proximity — check EPA's Envirofacts database

Natural hazards:
[ ] Wildfire risk (check state forestry maps)
[ ] Erosion and landslide risk (steep slopes, clay soils)
[ ] Radon (check EPA radon zone map — testing is $15-150)
[ ] Earthquake fault lines (USGS hazard maps)
```

### Step 6: Utilities and infrastructure

**Agent action**: Calculate the true cost of getting power, internet, and services to the property.

```
UTILITY COST CALCULATION:

ELECTRICITY:
[ ] How far to the nearest power pole?
[ ] Line extension costs: $15-25 per foot from nearest pole
    -> A quarter mile (1,320 ft) = $20,000-33,000
    -> A half mile = $40,000-66,000
[ ] Alternative: solar + battery system ($15,000-30,000 installed)
    May be cheaper than line extension for remote properties
[ ] Confirm with the local utility — get a written estimate

INTERNET:
[ ] Check broadband availability maps for the address
[ ] Options by reliability:
    -> Fiber: best, but rare in rural areas
    -> Cable/DSL: decreasing availability with distance from town
    -> Fixed wireless: available in some areas, variable quality
    -> Starlink: $120/month + $599 hardware, works nearly everywhere
    -> Cell hotspot: depends on coverage, data caps are limiting
[ ] Test cell service ON THE PROPERTY with your carrier before buying

PHONE:
[ ] Cell coverage (check all major carriers on-site)
[ ] Landline availability (copper lines being discontinued in many areas)
[ ] Emergency services — can 911 find the property?

THE 5-MILE RULE — how far to:
[ ] Hospital/urgent care: _____ miles
[ ] Grocery store: _____ miles
[ ] Fire department: _____ miles
[ ] Hardware store: _____ miles
[ ] Fuel station: _____ miles
These distances define your daily life. A beautiful property
45 minutes from the nearest grocery store gets old fast.
```

### Step 7: Financial analysis

**Agent action**: Help the user build a realistic budget that includes all improvement costs.

```
FULL COST WORKSHEET:

PURCHASE:
Land price:                           $________
Closing costs (2-5% of purchase):     $________
Survey (if not recent):               $________  ($500-3,000)
Title insurance:                      $________

IMPROVEMENTS (raw land):
Well drilling:                        $________  ($5,000-15,000)
Septic system:                        $________  ($10,000-25,000)
Power connection/solar:               $________  ($5,000-33,000+)
Driveway construction:                $________  ($2,000-15,000)
Site clearing/grading:                $________  ($2,000-10,000)
                                      ─────────
TOTAL IMPROVEMENT COST:               $________

This is the number people forget. Raw land at $30,000
with $50,000 in improvements is really an $80,000 purchase.

ONGOING ANNUAL COSTS:
Property taxes:                       $________/year
Insurance (if structures):            $________/year
Road maintenance (private road share):$________/year
Well/septic maintenance:              $________/year
                                      ─────────
ANNUAL CARRYING COST:                 $________/year

FINANCING:
- Banks are reluctant to finance raw land (higher risk)
- Expect 20-50% down payment for raw land loans
- Interest rates 1-2% higher than residential mortgages
- Owner financing: common for land sales
  -> Often more flexible terms
  -> Typically higher interest rate
  -> Shorter term (5-15 years vs 30)
  -> Get a real estate attorney to review the contract

IMPROVED VS RAW LAND:
Improved land (has well, septic, power, driveway) costs more
per acre but avoids $30,000-60,000 in improvement costs and
months of permitting and construction delays.
For first-time land buyers, improved land is usually the
smarter financial decision.
```

### Step 8: Neighbor and community research

**Agent action**: One bad neighbor can ruin rural life. Help the user investigate.

```
NEIGHBOR AND COMMUNITY DUE DILIGENCE:

Before buying:
[ ] Visit the property at different times (morning, evening, weekend)
[ ] Walk the boundary lines — what's on the other side?
[ ] Talk to adjacent landowners (show up, introduce yourself,
    ask about the area — people talk)
[ ] Ask about: flooding, road conditions, problem wildlife,
    any ongoing disputes, what the previous owner was like
[ ] Check county court records for disputes involving the property
    or adjacent properties
[ ] Check for nearby nuisances:
    -> Shooting ranges, ATV trails, industrial operations
    -> Confined animal feeding operations (CAFOs) — smell carries miles
    -> Future development plans (check county planning department)

Community assessment:
[ ] Local volunteer fire department? (Response time matters)
[ ] School quality (if applicable)
[ ] Community character — visit the local diner, gas station, post office
[ ] Political and cultural climate (rural communities vary enormously)
[ ] Any community organizations, churches, granges, co-ops?
[ ] How do locals feel about newcomers? (Some areas are welcoming,
    others are not — this is worth knowing before you commit)

TIMBER VALUE:
[ ] If the property is wooded, get a timber cruise (assessment)
    from a registered forester
[ ] Timber can be worth $1,000-10,000+ per acre depending on species,
    age, and access
[ ] Selective harvesting can fund improvements
[ ] VERIFY timber rights convey with the sale
```

## If This Fails

- **Can't find county records or well logs?** Call the county health department directly. They maintain septic and well records. Some counties are still paper-only — you may need to visit in person.
- **FEMA map shows flood zone but property seems high and dry?** FEMA maps have errors. You can challenge the designation with a LOMA (Letter of Map Amendment) if a licensed surveyor confirms the property is above the base flood elevation. Cost: $500-1,500 for the survey, FEMA review is free.
- **Seller won't allow contingencies?** Walk away. A seller who won't let you do a perc test, water test, or title search is hiding something. There is always more land.
- **Owner financing feels sketchy?** Have a real estate attorney review every document. Owner financing is legitimate and common for land, but the terms must protect you. Insist on title insurance and proper recording.
- **Property is perfect but too remote?** Be honest with yourself about your lifestyle needs. The fantasy of isolation and the reality of 45-minute grocery runs are different things. Rent in the area for 6 months before buying if possible.

## Rules

- Always check water first — everything else is secondary to reliable water access
- Never let the user skip the perc test contingency on raw land
- Always recommend a real estate attorney for rural land transactions (not just a title company)
- If the user mentions western US states, flag water rights as a critical issue
- Recommend visiting the property in multiple seasons and at different times before purchasing
- Always calculate full improvement costs, not just the land price

## Tips

- The best rural land deals are never listed online. Tell every local you meet that you're looking. Ask at feed stores, post offices, and churches. The farmer who's ready to sell 10 acres often just wants someone who'll take care of it.
- Make your offer contingent on everything: perc test, water test, survey, title search, environmental assessment. Remove contingencies one at a time as each clears. A good buyer's agent will structure this for you.
- Drive the road to the property in the worst weather you can. A scenic gravel road in July might be an impassable mud pit in March.
- County tax assessor records show what adjacent properties sold for. Use this for price negotiation. Land prices per acre should be roughly comparable for similar parcels in the same area.
- Ask the county about any planned developments, road projects, or rezoning in the area. A future highway or subdivision can change the character of a rural property overnight.
- Rent before you buy if possible. Even a month of living in the area tells you more than a dozen weekend visits.

## Agent State

```yaml
state:
  property:
    address: null
    acreage: null
    asking_price: null
    zoning: null
    current_use: null
  water:
    well_potential_confirmed: false
    water_rights_checked: false
    water_test_done: false
    water_source_type: null
    estimated_well_cost: null
  soil:
    web_soil_survey_checked: false
    soil_test_done: false
    perc_test_done: false
    perc_test_passed: null
    septic_estimated_cost: null
  access:
    legal_access_confirmed: false
    access_type: null
    road_maintained: null
    driveway_exists: false
    driveway_estimated_cost: null
  zoning:
    zoning_checked: false
    building_permitted: null
    livestock_permitted: null
    restrictions_identified: []
  hazards:
    fema_flood_zone: null
    environmental_check_done: false
    contamination_found: false
  utilities:
    power_distance_to_pole: null
    power_estimated_cost: null
    internet_available: null
    cell_service_tested: false
  financial:
    total_improvement_cost: null
    annual_carrying_cost: null
    financing_type: null
  due_diligence:
    neighbors_contacted: false
    multiple_visits_done: false
    attorney_engaged: false
    title_search_done: false
    survey_done: false
```

## Automation Triggers

```yaml
triggers:
  - name: water_first
    condition: "property.address IS SET AND water.well_potential_confirmed = false"
    action: "You've identified a property but haven't checked water yet. Water is the single most important factor — let's check county well logs and water availability before anything else."

  - name: perc_test_reminder
    condition: "soil.web_soil_survey_checked = true AND soil.perc_test_done = false"
    action: "Soil survey is done but you haven't scheduled a perc test. If the soil won't perc, you can't build a septic system and the land may be unbuildable. Make your purchase offer contingent on passing the perc test."

  - name: access_check
    condition: "property.address IS SET AND access.legal_access_confirmed = false"
    action: "Have you confirmed legal road access? This needs to be verified through a title search — verbal agreements and dirt tracks don't count. Landlocked property is a financial disaster."

  - name: full_cost_calculation
    condition: "water.estimated_well_cost IS SET AND soil.septic_estimated_cost IS SET AND utilities.power_estimated_cost IS SET AND financial.total_improvement_cost IS NULL"
    action: "You have individual cost estimates. Let's add them up with the land price to get the true total investment. Raw land costs are deceiving without the full improvement picture."

  - name: attorney_recommendation
    condition: "property.asking_price IS SET AND due_diligence.attorney_engaged = false"
    action: "Before making an offer, engage a real estate attorney who handles rural land transactions. Not a title company — an attorney. They'll catch issues in the deed, easements, and restrictions that title companies miss."
```
