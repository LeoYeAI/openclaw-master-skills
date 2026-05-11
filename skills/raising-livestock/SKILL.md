---
name: raising-livestock
description: >-
  Practical small livestock management starting with chickens and progressing to goats. Use when someone wants to raise chickens for eggs, keep goats for milk or meat, or is evaluating whether livestock fits their situation.
metadata:
  category: skills
  tagline: >-
    Start with chickens, scale to goats -- practical small livestock for eggs, milk, meat, and land management on a quarter-acre or more.
  display_name: "Raising Livestock"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install raising-livestock"
---

# Raising Livestock

This skill is tiered: chickens first, then goats. Start with chickens. They're cheap, legal in most suburbs, require 15 minutes a day, and produce eggs within 6 months. If you can keep chickens alive and healthy for a year, you've learned 80% of what livestock management requires -- daily routine, feed economics, predator management, and health monitoring. Goats are the next step and a significant escalation in time, cost, and fencing requirements. Both animals are practical, productive, and manageable on small acreage. But both are also daily commitments with no days off, and this skill will be honest about that before helping you get started.

```agent-adaptation
# Localization note -- livestock care principles are universal. Regulations, breeds,
# and climate considerations vary.
# Agent must follow these rules when working with non-US users:
- Animal husbandry principles (housing, feeding, health) are universal.
- Zoning and livestock regulations vary significantly:
  US: municipal codes, county regulations, HOA restrictions
  UK: DEFRA regulations, APHA registration, CPH number required for goats
  AU: state DPI regulations, council bylaws
  EU: varies by country -- registration, movement tracking, welfare standards
  Agent MUST advise checking local regulations before acquiring any animals.
- Breed availability varies by region:
  US breeds listed here are widely available. Local equivalents exist everywhere.
  UK: common layers include Leghorn, Sussex, Maran; goats include Saanen, Toggenburg
  AU: common layers include Isa Brown, Australorp; goats include Saanen, British Alpine
  Agent should suggest locally available breeds when working outside the US.
- Feed products:
  Layer feed, goat feed, and mineral supplements are available globally
  but brand names differ. Agent should recommend the feed TYPE rather
  than specific brands.
- Veterinary care:
  "Large animal vet" or "farm vet" or "livestock vet" -- terminology
  and availability vary. In rural areas, vets may be scarce.
  Agent should advise establishing a vet relationship BEFORE getting animals.
- Measurement units:
  US: pounds, ounces, Fahrenheit, square feet
  UK/AU/EU: kilograms, grams, Celsius, square meters
  Agent must convert when working with non-US users.
- Slaughter/butchering regulations:
  US: on-farm slaughter of own animals is generally legal
  UK: strict regulations, must comply with welfare at slaughter legislation
  AU: varies by state
  Agent must check local regulations before advising on home butchering.
```

## Sources & Verification

- **Storey's Guide to Raising Chickens** by Gail Damerow -- the most comprehensive single reference for backyard chicken keeping. Updated editions cover modern breeds and health practices.
- **Storey's Guide to Raising Dairy Goats** by Jerry Belanger -- the standard reference for small-scale dairy goat management.
- **Backyard Poultry magazine** -- practical articles from experienced keepers. [backyardpoultry.iamcountryside.com](https://backyardpoultry.iamcountryside.com/)
- **State extension office livestock resources** -- university-based research and practical guidance specific to your region. Available through the Cooperative Extension system.
- **USDA Animal and Plant Health Inspection Service (APHIS)** -- federal animal health regulations and disease reporting. [aphis.usda.gov](https://www.aphis.usda.gov/)

## When to Use

- User wants to raise chickens for eggs
- User is considering goats for milk, meat, or land clearing
- User wants to evaluate whether livestock fits their situation, space, and budget
- User has chickens or goats and needs health, feeding, or management guidance
- User is dealing with a specific livestock problem (predators, illness, egg production drop)
- User wants honest cost and time analysis before committing

## Instructions

### Step 1: Reality Check -- Is Livestock Right for You?

**Agent action**: Before any breed or setup discussion, screen for readiness. Livestock is a daily commitment.

```
HONEST QUESTIONS TO ANSWER FIRST:

ZONING:
-> Check your municipal code BEFORE buying anything
-> Most municipalities allow 3-6 hens with no rooster
-> Some ban all poultry. Some require permits. Some have setback
   requirements (coop must be X feet from property line).
-> Goats: fewer municipalities allow them. Rural/agricultural zoning
   is usually required. Some allow "miniature" goats on smaller lots.
-> HOA: if you have one, check the covenants. Many prohibit livestock
   regardless of municipal code.

TIME:
-> Chickens: 15 minutes daily (water, feed, eggs, quick health check)
   + 30 minutes weekly (coop cleaning, deeper checks)
-> Goats: 20-30 minutes daily (water, feed, hay, health check)
   + 15-20 minutes per milking, twice daily for dairy goats
   + periodic hoof trimming, fence checking, vet visits
-> Neither animal takes a day off. You need a plan for vacations
   and emergencies (a neighbor, a farm-sitter, someone reliable).

SPACE:
-> Chickens: 4 sq ft per bird inside the coop + 10 sq ft per bird
   in the run. 6 chickens = 24 sq ft coop + 60 sq ft run.
   This fits in most suburban backyards.
-> Goats: minimum 200 sq ft shelter per goat + half acre pasture
   for 2-3 goats. More is better. Goats need room to browse.

BUDGET (startup):
-> Chickens: $200-500 (coop, feeder, waterer, initial feed, chicks)
-> Goats: $700-3000 (goats themselves $200-500 each, fencing $500-2000,
   shelter $200-500, equipment)

BUDGET (ongoing):
-> Chickens: $15-25/month feed for 6 hens
-> Goats: $30-60/month feed and hay for 2-3 goats + annual vet costs

PREDATORS IN YOUR AREA:
-> Raccoons, foxes, hawks, coyotes, dogs, weasels, rats, snakes
-> If you have predators (you do), your housing must be predator-proof.
   Hardware cloth, not chicken wire. Secure latches. Buried wire.
-> Losing your flock to a raccoon because you used chicken wire
   is a gut punch you can prevent.
```

### Step 2: Tier 1 -- Chickens

**Agent action**: Walk through complete chicken setup from coop to daily routine.

```
CHICKEN SETUP:

COOP REQUIREMENTS:
-> 4 sq ft per bird inside (minimum -- more is better)
-> Roost bars: 8-10 inches per bird, 2+ feet off the floor,
   higher than the nest boxes (chickens roost at the highest point)
-> Nest boxes: 1 box per 3-4 hens, 12x12x12 inches, lined with
   straw or pine shavings, in the darkest part of the coop
-> Ventilation: MORE IMPORTANT THAN INSULATION in most climates.
   Moisture and ammonia kill chickens. Cross-ventilation near the
   roof line (above roost height so birds aren't in a draft).
-> Pop door: small door (12x14 inches) for chicken access to the run
-> Human-sized access: you need to get in to clean it

RUN REQUIREMENTS:
-> 10 sq ft per bird minimum (more = happier, healthier birds)
-> HARDWARE CLOTH (1/2" welded wire), NOT chicken wire
   -> Raccoons reach through chicken wire and pull birds apart
   -> This is not an exaggeration. It happens regularly.
-> Bury wire 12 inches into the ground or bend it outward in an
   L-shape on the ground (stops digging predators)
-> Cover the top (hawks, owls) with hardware cloth or poultry netting
-> Secure all latches: raccoons can open simple hooks and twist latches.
   Use carabiner clips or padlocks.

BREED SELECTION:
-> Best layers (eggs are the priority):
   Rhode Island Red: 250-300 eggs/year, hardy, friendly, the standard
   Leghorn: 280-320 eggs/year, flighty, great layers, less friendly
   Golden Comet/ISA Brown: 300+ eggs/year, bred for production, friendly
-> Dual-purpose (eggs + meat at end of productive life):
   Plymouth Rock (Barred Rock): 200-250 eggs/year, calm, cold-hardy
   Orpington (Buff): 200-250 eggs/year, very friendly, good mothers
   Wyandotte: 200-250 eggs/year, cold-hardy, attractive
-> Cold-hardy: Wyandotte, Australorp, Orpington, Plymouth Rock
   (rose combs and pea combs resist frostbite better than large single combs)
-> Heat-tolerant: Leghorn, Easter Egger, any light-bodied Mediterranean breed
-> For beginners: 4-6 Rhode Island Reds or Plymouth Rocks.
   Hardy, productive, forgiving of mistakes.

GETTING STARTED:
-> Chicks ($3-5 each from feed stores or hatcheries): cheapest,
   but require 4-6 weeks in a brooder (heat lamp, enclosed space,
   temperature management). Eggs at 18-24 weeks old.
-> Pullets/started pullets ($15-25 each): 12-20 weeks old, past the
   fragile stage. Eggs within weeks to months. Best for beginners.
-> You need a MINIMUM of 3 birds. Chickens are flock animals and
   suffer alone. 4-6 is ideal for a small backyard flock.
```

```
DAILY CHICKEN ROUTINE (15 minutes):

MORNING:
1. Open the pop door (let birds into the run)
2. Check and refill water (fresh daily -- dirty water = sick birds)
3. Check feed level in the feeder
4. Quick visual health scan:
   -> Are all birds active and moving?
   -> Any bird sitting puffed up, separated from the flock, or lethargic?
   -> Check for limping, discharge, or abnormal droppings

EVENING:
5. Collect eggs (daily -- eggs left in the nest attract predators
   and encourage egg-eating behavior)
6. Count birds as they go in to roost (confirms everyone is accounted for)
7. Close and secure the pop door (predators are most active at night)

WEEKLY:
8. Clean the coop: remove soiled bedding, replace with fresh shavings
   (pine shavings are standard -- NEVER cedar, the oils are toxic)
9. Check for signs of mites or lice (tiny bugs at the base of feathers,
   especially around the vent)
10. Rinse and scrub waterers
```

```
FEEDING:

LAYER FEED: the staple ($15-20 per 50-lb bag)
-> 16% protein complete feed formulated for laying hens
-> Available at any farm supply store (Tractor Supply, local feed mills)
-> One 50-lb bag feeds 6 hens for approximately 1 month
-> Free-feed (keep the feeder full, they regulate their own intake)

CALCIUM SUPPLEMENT: crushed oyster shell ($8-10 per bag)
-> Free-choice in a separate dish (hens take what they need)
-> Eggshells require calcium. Without it, you get thin-shelled or
   shell-less eggs and eventually a sick hen.

GRIT: small stones for digestion ($5-8 per bag)
-> Chickens don't have teeth. Grit in the gizzard grinds food.
-> Free-range birds pick up grit naturally. Confined birds need it
   supplemented.
-> Free-choice in a separate dish

KITCHEN SCRAPS (supplemental, not a substitute for feed):
-> YES: most vegetables, fruits, grains, cooked rice, cooked pasta,
   mealworms (treat)
-> NO: avocado (toxic), chocolate (toxic), raw dried beans (toxic),
   anything moldy, anything heavily salted, anything with caffeine
-> Scraps should be less than 10% of total diet. Too many treats =
   nutritional imbalance = fewer eggs.

WATER: the most important "feed"
-> Clean, fresh water available at all times
-> Chickens drink 1-2 cups per day per bird (more in heat)
-> Dirty water is the fastest way to a sick flock
-> In freezing weather: heated waterers ($30-40) or bring fresh
   water twice daily
```

```
CHICKEN HEALTH -- COMMON ISSUES:

MITES AND LICE:
-> Signs: feather loss (especially around vent), excessive preening,
   pale comb, drop in egg production
-> Prevention: dust bathing area (dry dirt, sand, or diatomaceous earth
   in a low container). Chickens dust-bathe instinctively to control
   parasites.
-> Treatment: poultry dust or permethrin spray on birds and in coop,
   diatomaceous earth in bedding, clean the coop thoroughly

RESPIRATORY ILLNESS:
-> Signs: sneezing, wheezing, nasal discharge, swollen eyes
-> Isolate the sick bird immediately
-> Keep in a warm, dry, ventilated space
-> Many respiratory infections are viral (no antibiotic cure) but
   bacterial secondary infections can be treated
-> If multiple birds are affected, call a poultry vet

EGG BINDING (egg stuck in the oviduct):
-> Signs: hen straining, sitting in nest box for extended periods,
   penguin-like walking posture, puffed up and lethargic
-> Treatment: warm bath (warm water, keep her calm for 15-20 minutes),
   can help relax muscles. Gently feel for the egg (do not push hard).
-> If the egg doesn't pass within a few hours: call a vet.
   Egg binding can be fatal.

BUMBLEFOOT (staph infection in the foot pad):
-> Signs: dark scab on the bottom of the foot, swelling, limping
-> Cause: usually from landing on hard surfaces from high roosts
-> Treatment: soak foot in warm Epsom salt water, carefully remove
   the scab and kernel of infection, pack with antibiotic ointment,
   wrap with gauze and vet wrap. Repeat every 2 days until healed.
-> Severe cases need veterinary attention.

EGG ECONOMICS (the honest math):
-> 6 hens produce 4-5 eggs/day at peak (spring/summer)
-> Production drops in winter (fewer daylight hours) and as hens age
-> Feed cost: ~$15-20/month for 6 hens
-> Egg production: roughly 10-12 dozen per month at peak
-> Cost per dozen (feed only): $1.50-2.00
-> Cost per dozen (including startup amortized over 3 years, feed,
   bedding, supplements): roughly $2.50-3.50
-> Compare to store-bought pasture-raised eggs: $5-7/dozen
-> You come out ahead AND the eggs are better. But the margins aren't
   huge. You're not doing this to get rich.
```

### Step 3: Tier 2 -- Goats

**Agent action**: Cover goat setup for users who have mastered chickens and have adequate land.

```
GOAT SETUP -- THE NEXT LEVEL:

PREREQUISITE: You should have at least a year of successful chicken
keeping before adding goats. Goats are more work, more expensive,
and less forgiving.

FENCING -- THE #1 CHALLENGE:
-> Goats escape everything. This is not a joke. It's their defining
   characteristic.
-> MINIMUM: 4-foot woven wire field fence (not welded wire -- they
   push through it) with an electric wire on top AND an electric wire
   at nose height on the inside
-> Check fence lines weekly. Goats test fencing constantly.
-> Gates need goat-proof latches. They learn to open simple latches
   with their mouths.
-> Budget $500-2000 for adequate fencing depending on acreage
-> If you won't invest in proper fencing, don't get goats. You'll
   spend your life chasing them through the neighborhood.

SHELTER:
-> 200 sq ft per goat minimum (covered, dry, draft-free)
-> Three-sided shelter facing away from prevailing wind works in
   most climates
-> Goats HATE rain. They will refuse to go outside in the rain.
   Adequate covered area is essential.
-> Bedding: straw or wood shavings, deep bedding method (add fresh
   layers on top, clean out completely 2-4 times per year)

BREED SELECTION:
-> Dairy (milk production):
   Nigerian Dwarf: small (50-75 lbs), 1-2 quarts/day, high butterfat,
   best for small properties, friendly
   Nubian: medium (130-175 lbs), 1-2 gallons/day, high butterfat,
   loud (they yell), long ears
   Saanen: large (130-175 lbs), 1-2 gallons/day, lower butterfat,
   quiet, high volume
   LaMancha: medium-large, 1-2 gallons/day, tiny ears, calm temperament
-> Meat:
   Boer: large (200-300 lbs), fast-growing, good meat quality
   Kiko: medium-large, extremely hardy, parasite-resistant, lower input
-> Fiber:
   Angora: produces mohair fiber (valuable), requires shearing 2x/year
-> For beginners with limited space: Nigerian Dwarf (dairy) or Kiko (meat)
-> ALWAYS keep at least 2 goats. They are herd animals and a single
   goat will be stressed, noisy, and destructive.

GETTING STARTED:
-> Buy from reputable breeders, not auction barns (auction animals
   often carry diseases and parasites)
-> Ask for health records, vaccination history, and test results
   (CAE, CL, Johne's -- serious goat diseases)
-> Budget $200-500 per goat depending on breed and quality
-> Start with 2-3 does (females). Bucks (intact males) smell terrible
   and are aggressive -- if you need breeding, borrow a buck or use AI.
```

```
DAILY GOAT ROUTINE (20-30 minutes, plus milking time):

MORNING:
1. Fresh water (goats are picky about water -- they won't drink dirty
   or stale water, and they tip over water buckets for sport)
2. Hay: 2-4 lbs per goat per day (the staple of their diet)
   -> Good quality grass hay or mixed grass/alfalfa
   -> Alfalfa: higher protein and calcium, good for milkers, too rich
      for dry does and wethers
3. Grain: for milking does only, 1 lb per 3 lbs of milk produced
   -> Textured goat feed or pelleted goat feed
   -> Don't over-grain -- rumen acidosis (grain overload) can kill
4. Loose mineral supplement: goat-specific, free-choice
   -> Copper is critical for goats (unlike sheep -- copper is toxic
      to sheep, do NOT use sheep minerals for goats)
5. Quick health check: bright eyes, firm droppings (goat berries),
   active behavior, clean nose

EVENING:
6. Second hay feeding
7. Fresh water check
8. Head count and secure for the night if predators are a concern

IF MILKING (dairy goats):
-> Twice daily, 12 hours apart (morning and evening), every day
-> This is the biggest time commitment of goat keeping
-> Miss a milking = discomfort for the doe, risk of mastitis,
   drop in production
-> See milking technique below
```

```
MILKING:

HAND MILKING TECHNIQUE:
1. Secure the doe on a milk stand (raised platform with a head catch
   and feed trough -- she eats grain while you milk). $50-100 to build.
2. Clean the udder with warm water and a clean cloth or udder wipes
3. Squirt the first few streams from each teat into a strip cup
   (a small cup with a dark surface -- lets you check for clumps,
   blood, or discoloration that indicates mastitis)
4. Milking grip: wrap thumb and forefinger around the base of the
   teat (trapping milk below). Squeeze downward with middle, ring,
   and pinky fingers in sequence. DO NOT pull down on the teat --
   squeeze only.
5. Alternate hands, rhythmic motion. Takes 5-10 minutes per doe
   once you're practiced.
6. When the udder feels empty (soft and deflated), dip each teat
   in teat dip (iodine-based, $10/bottle) to prevent infection.
7. Strain the milk through a filter immediately.
8. Chill the milk as fast as possible (ice bath or straight to fridge).
   Fast chilling = better taste, longer shelf life.

MILKING YIELD:
-> Nigerian Dwarf: 1-2 quarts/day
-> Nubian: 4-8 quarts/day at peak
-> Saanen: 4-8 quarts/day at peak
-> Production peaks 4-8 weeks after kidding, gradually declines
-> Lactation lasts about 10 months. Then the doe needs to be dried
   off and bred again for the next lactation.
```

```
GOAT HEALTH:

HOOF TRIMMING (every 6-8 weeks):
-> Goat hooves grow continuously like fingernails
-> Overgrown hooves cause lameness and foot rot
-> Tools: hoof shears or hoof trimmers ($10-15)
-> Technique: trim the overgrown wall flush with the sole, trim the
   toe to match the angle of the hairline. Don't trim into the pink
   (quick) -- that's living tissue and will bleed.
-> Have blood-stop powder on hand for nicks.

DEWORMING (CRITICAL -- and changing):
-> Internal parasites (barber pole worm, etc.) are the #1 health
   threat to goats
-> DO NOT blanket deworm on a schedule -- this creates resistant
   parasites that no drug can kill
-> Instead: FAMACHA scoring (check inner eyelid color to assess
   anemia from blood-sucking worms) and fecal testing
   -> Fecal egg count: collect fresh droppings, bring to your vet,
      they count parasite eggs under a microscope ($15-25 per test)
   -> Only deworm animals with high counts or clinical signs
-> Pasture management: rotate pastures (parasites complete their
   lifecycle in the grass), don't graze pastures below 4 inches,
   multi-species grazing breaks parasite cycles

CDT VACCINATION (annual):
-> Covers Clostridium perfringens types C and D plus tetanus
-> The one vaccine every goat should get, period
-> Given annually to adults, at 4 and 8 weeks to kids
-> $8-10 for a 10-dose bottle, given subcutaneously

BREEDING AND KIDDING:
-> Gestation: 145-155 days (about 5 months)
-> Most does kid unassisted -- watch from a distance
-> Know the signs of labor: nesting behavior, pawing, vocalization,
   discharge, visible contractions
-> WHEN TO INTERVENE:
   -> Active labor (pushing) for more than 30 minutes with no kid
   -> Kid presenting wrong (only feet, only head, breech)
   -> Doe is exhausted and stopping
   -> Call your vet. Have a vet's number BEFORE breeding season.
-> Kids need colostrum (first milk) within the first 2 hours of life.
   This is non-negotiable for immune system development.

HONEST COST ANALYSIS:
-> Startup: $700-3000 (2-3 goats + fencing + shelter + equipment)
-> Monthly: $30-60 (hay + grain + minerals)
-> Annual: $100-300 (vet visits, vaccines, hoof care supplies, bedding)
-> Labor: 30-60 minutes daily (more if milking)
-> Goats live 10-15 years. This is a long commitment.
-> If the numbers or the time don't work for your situation, there's
   no shame in sticking with chickens or deciding livestock isn't
   for you. That's a smart decision, not a failure.
```

### Step 4: Butchering (Optional, Honest Section)

**Agent action**: Only provide this section if the user asks about meat production or end-of-life for non-producing animals. Be direct and respectful.

```
PROCESSING ANIMALS FOR MEAT:

This section exists because raising livestock eventually raises this
question. Not everyone will use it. That's fine.

CHICKENS:
-> Older hens that stop laying (3-5 years old) are tough but flavorful.
   Good for stock and slow-cooked dishes (stew, soup), not roasting.
-> Meat birds (Cornish Cross) reach processing weight in 6-8 weeks.
   They are purpose-bred and cannot be kept as long-lived birds.
-> Processing: cervical dislocation or sharp cone method (quick,
   humane when done correctly), scald in 145-150F water for 60 seconds,
   pluck, eviscerate, chill in ice water immediately.
-> First time: find a local experienced keeper or take a poultry
   processing workshop. Watching before doing reduces mistakes.

GOATS:
-> Meat processing is typically done at a USDA-inspected facility
   or a custom-exempt butcher
-> On-farm slaughter regulations vary by jurisdiction -- check local laws
-> For most people, paying a butcher ($50-100 processing fee) is the
   right call

EMOTIONAL REALITY:
-> Butchering an animal you raised is hard. Anyone who says otherwise
   either hasn't done it or isn't being honest.
-> It's okay if you decide this isn't for you.
-> It's also okay if you decide it is. Knowing where your food comes
   from and ensuring the animal lived well is a legitimate and
   respectable choice.
-> Never name an animal you plan to eat. This is practical advice,
   not a joke.
```

## If This Fails

- **Chickens aren't laying?** Check: age (production drops after year 2), daylight (they need 14+ hours -- supplemental light in winter helps), nutrition (are they getting layer feed and calcium?), stress (predator visits, new flock members, moving the coop), molt (annual feather replacement, egg production stops for 2-3 months), and broody behavior (hen sitting on empty nest -- break it by moving her to a wire-bottom cage for 3-5 days).
- **Predator got into the coop?** Determine what it was (tracks, damage pattern, time of day), repair the breach, and upgrade: hardware cloth everywhere, buried wire at the base, secure latches, motion-activated lights for nocturnal predators. For persistent predators: electric fence adds a strong deterrent.
- **Goat is sick and you're not sure what's wrong?** Temperature first: normal is 101.5-103.5F. Above 104F = infection or illness. Below 100F = hypothermia or late-stage illness. Call your vet. Goats go downhill fast -- don't wait to see if they improve on their own.
- **Can't find a livestock vet?** Search "large animal veterinarian" or "farm vet" in your area. State vet associations maintain directories. In rural areas, the farm supply store staff often know who treats goats. Establish a vet relationship BEFORE you have an emergency.
- **Neighbors complaining?** Roosters are the #1 source of conflict (and are banned in most municipalities). Goats that escape into neighboring yards are #2. Proper fencing and no roosters prevent most neighbor issues. Offering fresh eggs can smooth over minor concerns.

## Rules

- Always check zoning before advising on livestock acquisition
- Recommend chickens before goats for any beginner -- the progression matters
- Never minimize the daily time commitment -- underselling this leads to neglected animals
- Emphasize predator-proofing with hardware cloth, not chicken wire
- For goat deworming, always recommend fecal testing over blanket treatment
- Be honest about costs and labor -- romanticizing livestock keeping sets people up for failure
- Link to soil-water-management for pasture improvement and water systems

## Tips

- Start with 4-6 hens, not 20. Scale up after you've figured out the routine and confirmed your setup works.
- A heated waterer (chickens) or heated water bucket (goats) is the single best winter investment. Hauling water twice daily in freezing weather gets old fast.
- Deep litter method in the coop: instead of cleaning weekly, add fresh shavings on top. The bottom layers compost in place, generating warmth in winter. Clean out completely 2-4 times per year and put it straight on the garden.
- Electric poultry netting ($150-250 for 164 feet) lets you move chickens around the yard. Fresh pasture = happier birds, better eggs, natural pest control, and fertilized lawn.
- For goats, a milk stand is not optional for dairy breeds. Build or buy one before your first milking. Trying to milk a goat that's not secured on a stand is a wrestling match you'll lose.
- Nigerian Dwarf goats are the best starter dairy goat for small properties. They're small, friendly, efficient, and their milk has the highest butterfat content of any breed (great for cheese and soap).
- Goat kids (baby goats) are unbelievably cute and will make you question every rational cost analysis you did before getting goats. Be prepared.
- Keep a notebook. Record egg counts, feed purchases, health observations, and vet visits. After a year, you'll have real data on your costs and production instead of guesses.

## Agent State

```yaml
state:
  readiness:
    zoning_checked: false
    zoning_allows_chickens: null
    zoning_allows_goats: null
    hoa_checked: false
    space_available_sqft: null
    existing_experience: null  # none, chickens, goats, both
    vet_identified: false
  chickens:
    keeping: false
    breed: null
    flock_size: null
    coop_built: false
    predator_proofing: null  # none, basic, hardware_cloth
    age_months: null
    laying: null
    daily_egg_count: null
    health_issues: []
    feed_type: null
    calcium_supplemented: false
  goats:
    keeping: false
    breed: null
    herd_size: null
    purpose: null  # dairy, meat, fiber, companion
    fencing_type: null
    fencing_adequate: null
    shelter_built: false
    milking: false
    milking_schedule: null
    health_issues: []
    last_fecal_test: null
    last_hoof_trim: null
    cdt_current: false
  economics:
    monthly_feed_cost: null
    monthly_egg_production: null
    monthly_milk_production: null
    startup_cost_total: null
```

## Automation Triggers

```yaml
triggers:
  - name: zoning_first
    condition: "readiness.zoning_checked IS false AND (chickens.keeping IS false OR goats.keeping IS false)"
    action: "Before we go further, check your local zoning code. Search your city or county name plus 'chicken ordinance' or 'livestock regulations.' If you have an HOA, check those covenants too. Getting animals first and discovering they're not allowed is an expensive mistake."

  - name: predator_proofing_check
    condition: "chickens.keeping IS true AND chickens.predator_proofing IS NOT 'hardware_cloth'"
    action: "Your coop needs hardware cloth, not chicken wire. Raccoons reach through chicken wire and kill birds. It costs a little more upfront but prevents the kind of morning you never want to have."

  - name: goat_fencing_warning
    condition: "goats.keeping IS true AND goats.fencing_adequate IS NOT true"
    action: "Goat fencing needs attention. Goats test fences constantly and escape anything that isn't built right. You need 4-foot woven wire field fence with electric wire -- anything less and you'll be chasing goats through the neighborhood."

  - name: deworming_check
    condition: "goats.keeping IS true AND goats.last_fecal_test IS null"
    schedule: "every 60 days"
    action: "It's time for a fecal egg count on your goats. Don't deworm on a schedule -- test first. Collect fresh droppings and bring them to your vet. Only treat animals with high counts. This prevents drug-resistant parasites."

  - name: egg_production_drop
    condition: "chickens.daily_egg_count IS SET AND chickens.daily_egg_count < (chickens.flock_size * 0.4)"
    action: "Egg production is below 40% of your flock size. Common causes: short daylight hours (winter), molt, age, nutritional deficiency, stress, or illness. Let's work through the possibilities."

  - name: tier_progression
    condition: "chickens.keeping IS true AND chickens.age_months > 12 AND goats.keeping IS false AND readiness.zoning_allows_goats IS true"
    action: "You've kept chickens successfully for over a year. If you're interested in scaling up, goats are the logical next step. Want to evaluate whether goats fit your situation?"
```
