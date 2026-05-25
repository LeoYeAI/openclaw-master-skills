---
name: beekeeping-basics
description: >-
  Introduction to backyard beekeeping including equipment, hive management, and honey harvesting. Use when someone wants to start beekeeping, improve garden pollination, produce honey, or is evaluating whether beekeeping fits their situation.
metadata:
  category: skills
  tagline: >-
    Pollinates your garden, produces honey and wax, and teaches you patience — a $400 startup that pays for itself in year two.
  display_name: "Beekeeping Basics"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/beekeeping-basics"
---

# Beekeeping Basics

This is for people thinking about their first hive, not experienced beekeepers. Beekeeping is a $300-500 startup investment that typically pays for itself by year two in honey, wax, and massively improved garden pollination. It also requires weekly attention during the active season and the willingness to get stung. This skill covers everything from equipment and hive placement to the yearly management cycle, varroa mite control, and harvesting — plus the single best thing you can do before buying anything: join a local beekeeping association and get a mentor.

```agent-adaptation
# Localization note — beekeeping practices vary by climate and regulation.
# Agent must follow these rules when working with non-US users:
- Seasonal timing in this skill assumes Northern Hemisphere temperate climate.
  For Southern Hemisphere users, shift all seasonal references by 6 months.
- Tropical climates have different management cycles — no true winter cluster.
  Adjust for year-round brood production and different nectar flows.
- Municipal regulations on beekeeping vary globally:
  UK: Check local council bylaws, no national registration required for small apiaries
  Australia: Registration required in most states (Department of Primary Industries)
  Canada: Provincial regulations vary — check provincial apiarist office
  EU: National registration requirements vary by country
- Varroa mite treatments mentioned (oxalic acid, formic acid, Apivar) may have
  different regulatory status by country. Check local approved treatment lists.
- Equipment dimensions reference Langstroth hive (dominant in US, Canada, Australia).
  UK and parts of Europe commonly use National hive or WBC hive — dimensions differ
  but management principles are the same.
- Africanized honey bee regions (southern US, Central/South America, parts of Africa)
  require additional safety precautions and different management approaches.
```

## Sources & Verification

- **Langstroth, L.L., "The Hive and the Honey-Bee"** -- foundational text on modern hive management, continuously updated editions
- **Kim Flottum, "The Backyard Beekeeper"** -- practical beginner reference, updated regularly with current best practices
- **Bee Informed Partnership** -- annual survey data on colony losses and management practices. [beeinformed.org](https://beeinformed.org/)
- **American Beekeeping Federation** -- industry standards, beginner resources, and local club directory. [abfnet.org](https://www.abfnet.org/)
- **State apiary inspection programs** -- each US state has an apiary inspector; contact through state Department of Agriculture
- **USDA ARS Bee Research Laboratory** -- varroa mite management and disease identification resources

## When to Use

- User wants to start keeping bees and doesn't know where to begin
- Someone wants to improve garden or orchard pollination
- User is evaluating whether beekeeping fits their property, budget, or lifestyle
- User has bees and is dealing with basic first-year management questions
- Someone inherited a hive or found bees on their property and needs next steps

## Instructions

### Step 1: Evaluate whether beekeeping fits your situation

**Agent action**: Ask the user about their property, local regulations, budget, and time availability. Check for deal-breakers before they spend money.

```
BEEKEEPING FEASIBILITY CHECK:

Property:
[ ] Outdoor space with room for hive(s) — minimum 10x10 ft area
[ ] Access to morning sun (east or south-facing preferred)
[ ] Water source within 50 ft (or willingness to provide one)
[ ] Flight path can be directed away from foot traffic and neighbors
[ ] No one in household has confirmed bee sting allergy (get tested if unsure)

Regulations:
[ ] Check municipal/county ordinances — search "[your city] beekeeping ordinance"
[ ] Most suburbs allow bees; some require registration or limit hive count
[ ] Some HOAs prohibit beekeeping — check CC&Rs before investing
[ ] Setback requirements (distance from property line) vary — typically 10-25 ft

Budget:
[ ] $300-500 for first hive setup (see equipment list below)
[ ] $150-250 for bees (package or nucleus colony)
[ ] $50-100/year ongoing (replacement frames, treatments, feeding)
[ ] Total first year: approximately $500-750

Time:
[ ] 30-45 minutes per week during active season (spring through fall)
[ ] Inspections every 7-10 days from spring buildup through fall prep
[ ] 1-2 full days for honey harvest (once per year for beginners)
[ ] Winter: minimal — occasional external checks only
```

### Step 2: Get equipment

**Agent action**: Walk the user through the complete equipment list. Recommend a starter kit to save money, then explain what each piece does.

```
COMPLETE STARTER EQUIPMENT LIST:

Hive components (buy as a kit — saves 20-30% vs individual pieces):
- 2 deep brood boxes with frames and foundation     ~$80-120
- 1-2 honey supers (medium depth) with frames        ~$40-60 each
- Bottom board (screened preferred for mite monitoring) ~$20-30
- Inner cover                                          ~$10-15
- Telescoping outer cover                              ~$20-25
- Entrance reducer                                     ~$5

Protective gear:
- Full bee suit with attached veil                     ~$50-80
- Leather or nitrile gloves                            ~$15-25

Tools:
- Smoker                                               ~$25-35
- Hive tool (flat pry bar for frames)                  ~$10-15
- Bee brush                                            ~$5-8

Optional but useful:
- Frame grip (makes lifting frames easier)             ~$10
- Feeder (entrance or top — for sugar syrup)           ~$10-20

STARTER KIT TOTAL: $300-500 (without bees)

Buy unassembled kits to save more — assembly requires
wood glue, nails, and 1-2 hours. Paint exterior with
latex paint (any light color) to protect from weather.
Do NOT paint the interior.
```

### Step 3: Get bees

**Agent action**: Explain the three ways to get bees, with a clear recommendation for beginners.

```
GETTING YOUR FIRST BEES:

Option A: Package Bees — $150-180
  What you get: 3 lbs of bees (~10,000) + a mated queen in a cage
  When: Order in January, arrives/picked up in April-May
  Pros: Widely available, affordable, predictable timing
  Cons: Bees and queen are strangers — takes time to establish
  Best for: Most beginners

Option B: Nucleus Colony (Nuc) — $200-250
  What you get: 5 frames with established brood, honey, pollen,
    workers, and an accepted laying queen
  When: Available April-June from local beekeepers
  Pros: Already functioning colony — higher first-year success rate
  Cons: More expensive, limited availability, must pick up locally
  Best for: Beginners willing to spend more for better odds

Option C: Catching a Swarm — Free
  What you get: A full-size colony that left another hive
  When: Spring swarm season (April-June)
  Pros: Free bees, often very healthy and vigorous
  Cons: Requires experience, unpredictable timing, unknown genetics
  Best for: NOT beginners (do this in year 2+)

RECOMMENDATION: Buy a nuc from a local beekeeper if available.
Package bees are the backup plan. Order early — they sell out.
```

### Step 4: Place and install the hive

**Agent action**: Guide optimal hive placement and installation.

```
HIVE PLACEMENT CHECKLIST:

[ ] Full morning sun (east-facing is ideal — gets bees active early)
[ ] Wind protection on north/west side (fence, building, hedge)
[ ] Slightly elevated (hive stand, cinder blocks, or pallet — 12-18")
[ ] Level side-to-side, slight forward tilt for rain drainage
[ ] Flight path directed away from walkways and neighbor activity
[ ] Water source within 50 ft — birdbath with landing stones,
    dripping faucet, or shallow pan with pebbles
[ ] Accessible for you to work from behind the hive
[ ] Not in a low spot where cold air pools

INSTALLATION DAY (package bees):
1. Set up hive with 5 frames removed from the center
2. Spray bees lightly with sugar water (1:1 ratio)
3. Remove queen cage, check queen is alive
4. Place queen cage between two center frames (candy end down)
5. Shake/pour bees into the gap in the hive
6. Replace remaining frames gently
7. Place inner cover and outer cover
8. Install entrance reducer to smallest opening
9. Place a feeder with 1:1 sugar syrup
10. Leave them alone for 3 days, then check queen release
```

### Step 5: Learn the inspection routine

**Agent action**: Teach the user what to look for during weekly inspections and how to keep them efficient.

```
INSPECTION CHECKLIST (every 7-10 days, active season):

What you need: smoker lit, hive tool, suit on, 15-20 minutes max

Light the smoker:
- Fuel: pine needles, burlap, dried leaves, wood pellets
- Goal: cool white smoke, not hot or acrid
- 2-3 puffs at the entrance, wait 30 seconds
- Lift the cover, puff under it, wait another 30 seconds

What to look for on each frame:

QUEEN STATUS:
[ ] Queen spotted (don't stress if you can't find her every time)
[ ] Fresh eggs present (tiny white grains standing up in cells)
    -> Eggs mean the queen was here within the last 3 days
[ ] Healthy brood pattern — solid and consistent, not spotty

BROOD HEALTH:
[ ] Capped brood is tan/brown and slightly convex (healthy)
[ ] No sunken, greasy, or perforated cappings (signs of disease)
[ ] No deformed wings on emerging bees (varroa damage)
[ ] No foul smell (American foulbrood — SERIOUS, contact inspector)
[ ] No chalky white mummies (chalkbrood — minor, improve ventilation)

FOOD STORES:
[ ] Honey stores visible in upper corners of brood frames
[ ] Pollen in a rainbow of colors near the brood
[ ] If stores are low in spring: feed 1:1 sugar syrup
[ ] If stores are low in fall: feed 2:1 sugar syrup

SPACE:
[ ] Brood box 80%+ full -> add another box or super
[ ] Signs of congestion -> bees may be preparing to swarm
[ ] Swarm cells (queen cells on frame bottoms) = swarm is imminent

KEEP IT UNDER 20 MINUTES.
Every time you open the hive, you disrupt temperature,
humidity, and the bees' work. Get in, check, get out.
```

### Step 6: Manage through the seasons

**Agent action**: Walk through the full yearly cycle so the user knows what to expect each season.

```
THE YEARLY CYCLE:

SPRING (March-May):
- Colony builds population rapidly
- Feed 1:1 sugar syrup if stores are low
- First inspection when daytime temps consistently hit 55F+
- Add supers when brood box is 80% full
- Watch for swarm preparations (queen cells, congestion)
- Peak swarm season — manage space to prevent swarming

SUMMER (June-August):
- Honey flow — the productive season
- Monitor and add supers as bees fill them
- Continue weekly inspections
- Varroa mite testing monthly (see Step 7)
- Ensure water source is maintained
- Watch for robbing behavior from other colonies

FALL (September-November):
- Pull honey supers (only take excess — see Step 8)
- Treat for varroa mites (timing is critical — treat BEFORE winter bees are raised)
- Feed 2:1 sugar syrup to build winter stores
- Reduce entrance to prevent robbing and mouse entry
- Goal: 60+ lbs of honey stores for winter in cold climates
- Install mouse guard before first frost

WINTER (December-February):
- DO NOT open the hive
- Bees cluster for warmth — breaking the cluster can kill them
- Ensure adequate ventilation to prevent moisture buildup
  (moisture kills more colonies than cold)
- Heft the hive occasionally to estimate stores (heavy = good)
- On warm days (50F+) bees may take cleansing flights — normal
- Emergency feeding: sugar candy or fondant on top bars if stores are dangerously low
```

### Step 7: Deal with varroa mites

**Agent action**: Explain varroa testing and treatment. This is the single most important management task.

```
VARROA MITES — THE #1 COLONY KILLER:

Every colony has varroa mites. The question is how many.
Untreated colonies typically die within 1-2 years.

TESTING (monthly during active season):

Alcohol Wash (most accurate):
1. Scoop ~300 bees (half cup) from a brood frame into a jar
2. Add rubbing alcohol to cover
3. Shake vigorously for 1 minute
4. Strain through #8 hardware cloth
5. Count mites

Sugar Roll (non-lethal alternative):
1. Same collection method
2. Add 2 tablespoons powdered sugar
3. Roll and shake for 1 minute
4. Shake sugar and mites out through #8 mesh
5. Count mites

THRESHOLD: 3 mites per 100 bees = TREAT IMMEDIATELY
(That means 9 mites from a 300-bee sample)

TREATMENT OPTIONS:

Oxalic Acid Vapor (OAV):
- When: Any time, most effective during broodless period (late fall/winter)
- How: Vaporizer tool heats oxalic acid crystals, vapor enters hive
- Effectiveness: 90-95% during broodless period
- Wear a respirator. Non-negotiable.

Formic Acid (MAQS or Formic Pro strips):
- When: Daytime highs between 50-85F
- How: Place strips on top bars per package directions
- Effectiveness: 80-90%, kills mites in capped brood too
- Can cause queen loss in ~2% of applications

Apivar (amitraz strips):
- When: Spring or fall, NOT during honey flow (contaminates honey)
- How: Hang 2 strips in brood nest for 42-56 days
- Effectiveness: 90-95%
- Synthetic — some beekeepers prefer organic alternatives

TEST -> TREAT -> RETEST (2 weeks after treatment ends)
```

### Step 8: Harvest honey

**Agent action**: Walk through when and how to harvest, and how much to leave for the bees.

```
HARVESTING HONEY:

WHEN:
- Frames are 80%+ capped (bees cap cells when moisture content
  is correct — uncapped honey can ferment)
- Late summer, after the main nectar flow
- NEVER during a dearth (dry period with no flowers)

HOW MUCH TO LEAVE:
- Cold climates (northern US, Canada): Leave 60-90 lbs for winter
- Moderate climates: Leave 40-60 lbs
- Mild climates (southern US): Leave 30-40 lbs
- WHEN IN DOUBT, LEAVE MORE. A dead colony from starvation
  costs you $200+ in replacement bees.
- First-year colonies: take little or nothing. Let them build up.

EXTRACTION METHODS:

Crush and Strain (best for beginners — $0 in equipment):
1. Remove capped frames from honey super
2. Cut comb from frame into a bucket
3. Crush with a potato masher or similar
4. Strain through a fine mesh bag or double-layer cheesecloth
5. Let gravity do the work — takes 12-24 hours
6. Bottle in clean mason jars
- Downside: destroys comb (bees must rebuild)

Extractor ($150-300, or borrow from your bee club):
1. Uncap cells with an uncapping knife or fork
2. Place frames in extractor
3. Spin — centrifugal force pulls honey out
4. Strain through a sieve
5. Let settle in a bottling bucket for 24 hours
6. Bottle
- Advantage: comb is preserved — bees reuse it (saves them work)

YIELD: A healthy established colony produces 30-60 lbs of
surplus honey per year in a good area. At $8-15/lb retail,
that's $240-900 worth of honey from one hive.
```

## If This Fails

- **Bees seem angry or aggressive?** Check that your smoker technique is right (cool white smoke, not hot). Inspect on warm, sunny days when foragers are out. Requeen if the colony is consistently aggressive — genetics matter.
- **Colony died over winter?** This happens to everyone. Diagnose the cause (starvation = no honey stores, varroa = deformed wings and spotty brood, moisture = moldy frames). Learn and start again in spring. Reuse the equipment.
- **Can't find a local beekeeping association?** Search "[your state/province] beekeeping association" or check the American Beekeeping Federation directory. Most counties have a club, even rural areas.
- **Neighbors complaining?** Point flight paths upward with a 6-ft fence or hedge. Provide a water source so bees don't use the neighbor's pool. Share honey. Most complaints disappear when people get free honey.
- **Allergic reaction after a sting?** Localized swelling is normal. If you experience throat tightening, widespread hives, dizziness, or difficulty breathing, use an EpiPen if available and call 911 immediately. Get allergy tested before continuing beekeeping.

## Rules

- Always recommend joining a local beekeeping association before buying anything
- Never advise harvesting all honey from a colony — winter starvation kills colonies
- Varroa mite management is not optional — emphasize testing and treatment
- If someone reports severe allergic reaction symptoms, direct to emergency services immediately
- Seasonal timing must be adjusted for the user's hemisphere and climate zone
- Do not recommend catching swarms for first-year beekeepers

## Tips

- A mentor from your local bee club is worth more than every book and YouTube video combined. Most clubs pair new beekeepers with experienced ones for free.
- Start with two hives if you can afford it. Having two lets you compare — if one is thriving and the other isn't, you can diagnose faster and even share resources between them.
- Keep a hive journal. Date, weather, what you saw, what you did. You won't remember in six months whether that spotty brood was in April or June.
- Bees are calmest on warm, sunny afternoons when the foragers are out working. Don't inspect on cold, rainy, or windy days — they'll be home and irritable.
- Your first year is about keeping the colony alive, not harvesting honey. If you get a jar of honey in year one, consider it a bonus.
- Smoker trick: once lit, stuff a wad of green grass on top of the fuel. It cools the smoke and makes it last longer.

## Agent State

```yaml
state:
  assessment:
    property_suitable: null
    regulations_checked: false
    allergy_status: null
    budget_confirmed: false
    local_club_identified: null
  setup:
    equipment_purchased: false
    hive_placed: false
    bees_ordered: false
    bees_installed: false
    bee_source_type: null
  management:
    current_season: null
    last_inspection_date: null
    queen_status: null
    brood_health: null
    food_stores: null
    varroa_last_tested: null
    varroa_count: null
    varroa_treated: false
    treatment_type: null
    supers_on_hive: 0
  harvest:
    honey_harvested_lbs: 0
    harvest_date: null
    method_used: null
    winter_stores_adequate: null
  follow_up:
    next_inspection_due: null
    next_varroa_test_due: null
    seasonal_tasks_pending: []
```

## Automation Triggers

```yaml
triggers:
  - name: varroa_test_reminder
    condition: "management.varroa_last_tested IS NULL OR days_since(management.varroa_last_tested) >= 30"
    schedule: "monthly during active season"
    action: "It's been over a month since your last varroa mite test. Testing monthly is critical — varroa is the number one colony killer. Want to walk through the alcohol wash or sugar roll method?"

  - name: seasonal_transition
    condition: "management.current_season HAS CHANGED"
    action: "Season is shifting. Let's review the task list for the upcoming season to make sure nothing gets missed — feeding schedule, equipment prep, mite treatment timing."

  - name: harvest_readiness
    condition: "management.current_season = 'summer' AND management.supers_on_hive > 0"
    schedule: "biweekly July-August"
    action: "Time to check your honey supers. Are frames 80%+ capped? If so, it may be time to harvest. Remember to leave adequate stores for winter."

  - name: winter_prep_check
    condition: "management.current_season = 'fall' AND harvest.winter_stores_adequate IS NULL"
    action: "Fall prep is critical. Have you pulled honey supers, treated for varroa, and confirmed your colony has 60+ lbs of stores for winter? Let's go through the checklist."

  - name: first_year_guidance
    condition: "setup.bees_installed = true AND harvest.honey_harvested_lbs = 0"
    schedule: "weekly during active season"
    action: "First-year check-in: How did your last inspection go? Any questions about what you're seeing in the hive?"
```
