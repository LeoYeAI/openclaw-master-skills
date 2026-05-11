---
name: hygiene-without-infrastructure
description: >-
  Maintaining hygiene and sanitation when normal infrastructure fails. Use when someone faces a water outage, sewer backup, extended power outage, camping without facilities, or any situation where normal plumbing and sanitation are unavailable.
metadata:
  category: skills
  tagline: >-
    What to do when the water stops or the sewer backs up -- water purification, emergency toilets, handwashing, and field hygiene.
  display_name: "Hygiene & Sanitation Without Infrastructure"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install hygiene-without-infrastructure"
---

# Hygiene & Sanitation Without Infrastructure

When the water stops flowing or the sewer backs up, you have about 72 hours before hygiene becomes a health emergency. Diarrheal disease from contaminated water kills more people globally than violence. That's not a developing-world statistic -- it's what happens anywhere when sanitation fails and people don't know the basics. This skill covers what to do when you can't flush, can't turn on the tap, and can't count on the systems you normally take for granted. The information is practical, tested, and drawn from disaster response and field sanitation protocols used worldwide.

```agent-adaptation
# Localization note -- hygiene principles are universal. Water treatment standards and product
# availability vary by region.
# Agent must follow these rules when working with non-US users:
- Water purification techniques (boiling, filtration, chemical treatment) are universal.
- Bleach concentration varies by country:
  US: household bleach is typically 6-8.25% sodium hypochlorite
  UK/EU: household bleach concentration varies (check label for % sodium hypochlorite)
  Adjust dosing accordingly: the target is 8 drops (0.5 mL) per gallon for 6% bleach.
  For higher concentrations, use fewer drops. For lower, use more.
  Formula: (6 / actual_percentage) x 8 drops per gallon of clear water
- Water quality standards:
  US: EPA drinking water standards
  UK: Drinking Water Inspectorate (DWI)
  EU: EU Drinking Water Directive 2020/2184
  WHO: Guidelines for Drinking-water Quality (universal baseline)
- Product availability:
  Sawyer/LifeStraw filters: widely available globally via Amazon
  Berkey filters: primarily US/UK/AU, alternatives exist elsewhere
  SteriPEN: available globally, check voltage for charging
- Waste disposal regulations vary by jurisdiction.
  Agent must advise checking local rules for human waste disposal,
  greywater use, and emergency sanitation during declared emergencies.
- Emergency services: US 911, UK 999, AU 000, EU 112.
```

## Sources & Verification

- **CDC emergency water treatment guidelines** -- US federal guidance on water disinfection methods. [cdc.gov/healthywater](https://www.cdc.gov/healthywater/drinking/travel/emergency_disinfection.html)
- **WHO water sanitation and hygiene (WASH) guidelines** -- the global standard for sanitation in emergency conditions. [who.int/water_sanitation_health](https://www.who.int/teams/environment-climate-change-and-health/water-sanitation-and-health)
- **EPA emergency disinfection** -- EPA guidance on treating water with household chemicals. [epa.gov](https://www.epa.gov/ground-water-and-drinking-water/emergency-disinfection-drinking-water)
- **FEMA sanitation guidance** -- federal emergency management sanitation protocols. [ready.gov](https://www.ready.gov/water)
- **Red Cross emergency hygiene** -- field-tested hygiene protocols for disaster response. [redcross.org](https://www.redcross.org/)

## When to Use

- Water service has been interrupted (main break, contamination notice, natural disaster)
- Sewer system has backed up or is unavailable
- Extended power outage has disabled well pumps or water treatment
- User is camping, hiking, or living without plumbing facilities
- User is preparing for potential infrastructure disruptions
- User needs to maintain hygiene in a field or emergency medical situation
- Boil-water advisory has been issued for the user's area

## Instructions

### Step 1: Water Purification

**Agent action**: Determine the user's situation and provide the appropriate water treatment method, starting with the most reliable.

```
WATER PURIFICATION METHODS (in order of reliability):

METHOD 1: BOILING -- THE GOLD STANDARD
-> Bring water to a rolling boil for 1 minute
-> At elevations above 6,500 feet: boil for 3 minutes
-> Let cool naturally (don't add ice unless the ice was made from
   safe water)
-> Works against: bacteria, viruses, protozoa, parasites -- everything
-> Requires: heat source and a pot
-> Downside: uses fuel, takes time, doesn't improve taste or remove
   chemicals

METHOD 2: FILTRATION
-> Gravity filters (Sawyer, Berkey): $30-100, no pumping required,
   filters thousands of gallons
   -> Removes: bacteria and protozoa
   -> Does NOT remove viruses (adequate for most US/EU water sources;
      in areas where viral contamination is likely, follow filtration
      with chemical or UV treatment)
-> Pump filters (MSR, Katadyn): $50-100, faster than gravity, good
   for small groups
-> Straw filters (LifeStraw): $15-25, drink directly or attach to
   a bottle, good for personal emergency use
-> All filters have a lifespan. Check and replace as specified.
-> Pre-filter visibly cloudy water through a cloth or coffee filter
   first to extend the main filter's life

METHOD 3: CHEMICAL TREATMENT
-> Household bleach (plain unscented, 6-8.25% sodium hypochlorite):
   -> Clear water: 8 drops (1/2 mL) per gallon
   -> Cloudy water: 16 drops (1 mL) per gallon
   -> Stir, wait 30 minutes. Should smell slightly of chlorine.
   -> If no chlorine smell after 30 min, repeat and wait 15 more min.
   -> DO NOT use scented bleach, color-safe bleach, or bleach with
      added cleaners
-> Water purification tablets (Aquatabs, Potable Aqua): $8-15 for 50+
   -> Follow package directions exactly
   -> Effective against bacteria, viruses, and most protozoa
   -> 30-minute wait time typically
-> Iodine: effective but not recommended for pregnant women, people
   with thyroid conditions, or for use beyond a few weeks

METHOD 4: UV TREATMENT
-> SteriPEN ($50-80): 90 seconds per liter, kills bacteria, viruses,
   and protozoa
-> Requires batteries or USB charging
-> Water must be clear (UV can't penetrate turbid water)
-> Pre-filter cloudy water before UV treatment
-> Good backup method, battery-dependent

WATER STORAGE:
-> Store in clean, food-grade containers with tight lids
-> 1 gallon per person per day (drinking + basic cooking)
-> 3-day minimum supply recommended
-> Commercially bottled water is already treated and sealed
-> Stored tap water: rotate every 6 months, or treat with 1/8 tsp
   bleach per gallon for longer storage
```

### Step 2: Emergency Sanitation (Toilet Alternatives)

**Agent action**: Provide practical toilet solutions when the sewer system is unavailable.

```
EMERGENCY TOILET OPTIONS:

OPTION 1: BUCKET TOILET ($0-20)
-> Materials: 5-gallon bucket, heavy-duty trash bags (contractor grade),
   cat litter OR sawdust OR wood ash for odor absorption
-> Setup:
   1. Line the bucket with a heavy-duty trash bag
   2. After each use, cover waste with a handful of cat litter or sawdust
   3. When the bag is half full (DO NOT overfill -- it gets heavy),
      tie it securely and double-bag it
   4. Dispose in regular trash (check local emergency rules -- during
      declared emergencies, many jurisdictions allow this)
   5. Replace the bag and repeat
-> Commercial option: Luggable Loo ($20) -- a toilet seat that snaps
   onto a 5-gallon bucket. More comfortable, same principle.
-> Lime powder: for extended situations, agricultural lime sprinkled
   on waste controls odor and helps decomposition. Available at
   garden centers, $5-10 for a large bag.

OPTION 2: EXISTING TOILET (no water service)
-> Your toilet still works mechanically without running water
-> Pour 1-2 gallons of ANY water directly into the bowl (not the tank)
   quickly -- the force of the pour triggers the siphon flush
-> Sources: pool water, rain barrels, bathtub stored water, creek water
-> This only works if the sewer line is intact. If the sewer has
   backed up, DO NOT flush -- you'll make it worse.

OPTION 3: TRENCH LATRINE (extended outdoor/rural situations)
-> Dig a trench 6-8 inches wide, 1 foot deep, at least 200 feet from
   any water source and downhill from your camp/living area
-> After each use, cover with a few inches of dirt
-> When the trench is within 4 inches of ground level, fill it in
   completely and dig a new one
-> Wash hands after every use (see handwashing section below)

GREYWATER vs BLACKWATER:
-> Greywater: water from sinks, showers, laundry
   -> Can be used to water non-edible plants (trees, shrubs, lawn)
   -> Do NOT use on food gardens (soap and bacteria)
   -> Dispose of greywater away from water sources
-> Blackwater: water from toilets, anything with human waste
   -> Must be contained and disposed of properly
   -> Never dump on the ground, never near water sources
   -> In extended situations: the bucket-and-bag method above
```

### Step 3: Handwashing Without Running Water

**Agent action**: Establish handwashing systems that work without plumbing.

```
HANDWASHING WITHOUT PLUMBING:

PRIORITY ORDER:
1. Soap + ANY water (even non-potable) = best option
2. Hand sanitizer (60%+ alcohol) = good when water is unavailable
3. Nothing = unacceptable risk for disease transmission

Wash hands: after using the toilet, before preparing or eating food,
after handling waste, after caring for a sick person, after blowing
your nose or coughing.

THE TWO-BUCKET METHOD:
-> Bucket 1: soapy water (any water + dish soap or bar soap)
-> Bucket 2: rinse water (any water, preferably cleaner)
-> Wet hands in bucket 1, scrub 20 seconds, rinse in bucket 2
-> Change water in both buckets at least daily
-> Hang a towel nearby (designated hand towel only)

TIPPY-TAP ($0 -- the field standard):
-> Materials: a jug with a cap, string or rope, a stick, a nail
-> Poke a small hole in the cap of the jug
-> Hang the jug from a tree branch or frame with a foot-operated lever
   (a stick tied to the jug handle, stepped on to tip the jug)
-> Tip: the water flows from the hole in the cap when the jug tips
-> Hands-free operation = less cross-contamination
-> Hang a bar of soap on a string next to it
-> Search "tippy tap" for simple construction diagrams

HAND SANITIZER:
-> Must be 60%+ alcohol to be effective
-> Apply enough to cover all surfaces of both hands
-> Rub until dry (20+ seconds)
-> Does NOT work well on visibly dirty or greasy hands -- wash first
   if possible
-> Does NOT kill some common pathogens (norovirus, C. diff, Crypto)
   -- soap and water is always superior
-> Stock sanitizer in your emergency kit, but don't rely on it as
   your only option
```

### Step 4: Food Safety Without Refrigeration

**Agent action**: Help the user manage food safety when power is out and refrigeration is unavailable.

```
FOOD SAFETY WITHOUT REFRIGERATION:

THE 2-HOUR / 4-HOUR RULE:
-> Perishable food at room temperature (above 40F/4C):
   -> Under 2 hours: still safe, refrigerate if possible
   -> 2-4 hours: use immediately, don't try to save it
   -> Over 4 hours: throw it out. No exceptions.
-> These times are cumulative. 1 hour on the counter + 2 hours in
   a cooler that's warmed up = 3 hours.

FOODS THAT LAST WITHOUT REFRIGERATION:
-> Peanut butter (months)
-> Canned goods (years -- but eat promptly once opened)
-> Hard cheeses (waxed/sealed -- weeks, cut off any mold)
-> Cured/dried meats (jerky, salami -- weeks if sealed)
-> Root vegetables (potatoes, carrots, onions -- weeks in cool dark place)
-> Apples (weeks in cool conditions)
-> Bread (3-5 days, longer as toast)
-> Rice, pasta, oats, dried beans (years if dry)
-> Honey (indefinite -- literally thousands of years)
-> Salt, sugar, spices (indefinite)

FOODS THAT SPOIL FAST:
-> Raw meat and poultry (hours)
-> Dairy milk (hours)
-> Soft cheeses (hours)
-> Cut fruit and vegetables (hours)
-> Cooked leftovers (hours)
-> Eggs (weeks if unrefrigerated and unwashed, but US store-bought
   eggs have been washed and must be refrigerated)

WHAT ABOUT YOUR FRIDGE/FREEZER DURING AN OUTAGE?
-> Fridge: stays safe for about 4 hours if you keep the door closed
-> Full freezer: stays safe for about 48 hours
-> Half-full freezer: about 24 hours
-> Don't open the door to check -- you're letting the cold out
-> If food has thawed but still has ice crystals, it can be refrozen
-> If food has thawed completely and been above 40F for over 2 hours,
   throw it out
-> When in doubt, throw it out. Food poisoning without medical access
   can be life-threatening.

COOKING KILLS MOST BACTERIA (but not all toxins):
-> Cook food to proper internal temperatures (165F/74C for poultry,
   160F/71C for ground meat, 145F/63C for whole cuts)
-> Cooking does NOT make spoiled food safe. Bacterial toxins survive
   cooking. If it smells off, looks off, or has been at room temp
   too long, cooking won't save it.
```

### Step 5: Laundry and Personal Hygiene

**Agent action**: Cover practical methods for maintaining cleanliness with minimal resources.

```
LAUNDRY WITHOUT A MACHINE:

BUCKET WASH METHOD:
1. Fill a 5-gallon bucket halfway with water (any temperature works,
   warm is faster)
2. Add a small amount of detergent or soap (a tablespoon is enough)
3. Add clothes -- don't overstuff. Wash in small loads.
4. Agitate: use a clean toilet plunger (dedicated to laundry) or just
   push and knead the clothes by hand for 5-10 minutes
5. Wring each item thoroughly
6. Rinse in clean water (a second bucket), wring again
7. Hang to dry -- sunlight helps disinfect and bleach whites

PRIORITIES (if water is limited):
-> Underwear and socks first (closest to body, most bacteria)
-> Anything worn against skin
-> Outer layers last (can be worn longer between washes)
-> Turning clothes inside out between wearings extends usability
-> Hanging clothes in direct sunlight between wearings kills some
   bacteria even without washing

BODY HYGIENE WITH LIMITED WATER:
-> Sponge bath: 1-2 quarts of water, a washcloth, soap
   -> Wash priority areas: face, underarms, groin, feet, hands
   -> These areas harbor the most bacteria and odor
-> Baby wipes / wet wipes: $3-5/pack, effective for quick cleanup
   when water is scarce. Stock in emergency kits.
-> Dry shampoo (or cornstarch/baking soda rubbed into scalp):
   absorbs oil, extends time between hair washing
-> Oral hygiene: brush with a tiny amount of water, or use a dry
   brush if no water is available. Baking soda works as toothpaste
   in a pinch.

MENSTRUAL HYGIENE:
-> Reusable cloth pads: washable, functional for years
   -> Wash in cold water (hot water sets stains), soap, air dry
-> Menstrual cups ($25-35): reusable for years, requires less water
   to clean than pads, works without any disposable products
   -> Clean between uses: boil for 5-10 minutes if possible,
      or wash with soap and water
   -> Single best option for extended infrastructure disruption
-> If using disposable products: stock a 3-month supply in your
   emergency kit. Don't assume stores will be open.
```

### Step 6: Wound Hygiene in Field Conditions

**Agent action**: Cover basic wound cleaning when clean water and medical supplies are limited. Link to minor-injury-first-response for detailed wound care.

```
WOUND CARE WITHOUT A CLINIC:

THE BASICS:
-> Clean water is the most important wound cleaning tool
-> Irrigation (flushing with clean water under gentle pressure) is
   more effective than dabbing or wiping
-> Use the cleanest water available: purified > boiled and cooled >
   filtered > tap > nothing
-> A clean plastic bag with a pinhole poked in the corner makes a
   field irrigation syringe

CLEANING A WOUND:
1. Wash your hands (see handwashing section)
2. Control bleeding with direct pressure if needed
3. Irrigate the wound with clean water -- flush out dirt and debris
4. Gently remove visible debris with clean tweezers
5. Do NOT use hydrogen peroxide or alcohol directly on wounds --
   they damage tissue and slow healing
6. Apply antibiotic ointment if available
7. Cover with a clean bandage. Change daily or when wet/dirty.
8. Watch for infection: increasing redness, swelling, warmth,
   red streaks, pus, fever

WHEN TO SEEK MEDICAL CARE:
-> Deep wounds that won't stop bleeding
-> Wounds with embedded debris you can't remove
-> Animal bites (infection risk is very high)
-> Signs of infection (above)
-> Any wound in a person with diabetes or immune compromise
-> Puncture wounds (especially from rusty objects -- tetanus risk)

See the minor-injury-first-response skill for detailed wound care,
burn treatment, and when to escalate.
```

## If This Fails

- **Water purification isn't possible (no heat, no filter, no chemicals)?** In a true emergency with no purification option, the priority water sources in order of safety: sealed bottled water > tap water from a known safe system before the outage > rainwater collected in clean containers > clear flowing water from a stream. Risk of illness from untreated water is real, but dehydration kills faster. If there's genuinely no way to treat water, drink the cleanest source available and seek medical attention if symptoms develop.
- **Sewer has backed up into the house?** Stop using all drains immediately. If the backup involves sewage on floors, it's a biohazard -- wear gloves and rubber boots, disinfect with a bleach solution (1/2 cup bleach per gallon of water), and ventilate the area. For significant sewage backup, call a professional remediation service.
- **Situation has lasted more than a week?** Extended infrastructure failure requires community-level response. Connect with local emergency management, mutual aid networks (see neighbor-mutual-aid skill), and relief organizations. Individual resources deplete. Community resources don't.
- **Someone is showing symptoms of waterborne illness (severe diarrhea, vomiting, fever)?** Oral rehydration is the immediate priority: 1 liter clean water + 6 teaspoons sugar + 1/2 teaspoon salt. Sip continuously. Seek medical care as soon as possible -- dehydration from diarrheal disease can kill within 24-48 hours, especially in children and elderly.

## Rules

- Always lead with the most reliable purification method for the user's available resources
- Never suggest untreated water is safe to drink under normal circumstances
- Always include handwashing guidance -- it's the single most effective disease prevention measure
- When addressing food safety, err on the side of "throw it out" -- food poisoning without medical access is dangerous
- Link to minor-injury-first-response for wound care beyond basic cleaning
- Be matter-of-fact about bodily functions -- this is not a topic where squeamishness helps anyone

## Tips

- Fill your bathtub when you know a storm is coming. That's 30-50 gallons of water for flushing toilets and washing, even if it's not purified for drinking.
- Keep two cases of bottled water in a closet at all times. Rotate every 6 months. This is the easiest emergency prep that most people skip.
- A $30 Sawyer Squeeze filter and 10 purification tablets take up less space than a paperback book and can make thousands of gallons of water safe to drink. Keep them in your emergency kit.
- Cat litter is the cheapest and most effective odor control for bucket toilets. Buy an extra bag and store it with your emergency supplies.
- Hand sanitizer stations at every door. During an infrastructure disruption, this is the fastest way to prevent illness from spreading through your household.
- Dark-colored trash bags for waste disposal. Nobody needs to see the contents, and UV light in sunlight helps with decomposition.
- A solar shower bag ($10-15) heats 5 gallons of water in direct sunlight in 2-3 hours. Hang it from a tree or fence for a warm shower with no fuel or electricity.
- Menstrual cups are the single most space-efficient, water-efficient menstrual hygiene solution for emergency kits. One cup replaces years of disposable products.

## Agent State

```yaml
state:
  situation:
    type: null  # water_outage, sewer_backup, power_outage, camping, disaster, preparation
    duration_expected: null
    people_in_household: null
    children_present: false
    elderly_present: false
    medical_conditions: []
  water:
    current_source: null  # municipal, well, stored, surface, rainwater, none
    purification_method: null  # boiling, filter, chemical, uv, none
    daily_supply_gallons: null
    supply_adequate: null
  sanitation:
    toilet_method: null  # bucket, manual_flush, latrine, functioning
    waste_disposal_plan: null
    handwashing_station: false
    supplies_on_hand: []
  food:
    refrigeration_available: false
    hours_since_power_loss: null
    perishables_assessed: false
    cooking_method: null  # gas_stove, camp_stove, grill, fire, none
  hygiene:
    water_for_bathing: null  # adequate, limited, none
    laundry_method: null  # machine, bucket, none
    menstrual_supplies: null
  health:
    anyone_symptomatic: false
    symptoms: []
    wound_care_needed: false
```

## Automation Triggers

```yaml
triggers:
  - name: water_treatment_priority
    condition: "water.current_source IS NOT 'municipal' AND water.purification_method IS null"
    action: "You're using water from a non-municipal source without treatment. Any water that hasn't been commercially bottled or treated by a municipal system needs to be purified before drinking. Let's figure out the best method with what you have available."

  - name: handwashing_setup
    condition: "sanitation.handwashing_station IS false AND situation.type IS SET"
    action: "You need a handwashing setup. Hand hygiene prevents more disease than any other single measure. Even without running water, a two-bucket station or a tippy-tap takes 5 minutes to set up. Let's do that now."

  - name: food_safety_check
    condition: "food.refrigeration_available IS false AND food.hours_since_power_loss > 4 AND food.perishables_assessed IS false"
    action: "Your power has been out for over 4 hours. Perishable food in the fridge may no longer be safe. Let's go through what you have and figure out what to eat now, what to cook immediately, and what to throw out."

  - name: illness_response
    condition: "health.anyone_symptomatic IS true"
    action: "Someone in your household is showing symptoms. Let's make sure they're staying hydrated (oral rehydration solution if diarrhea or vomiting), isolated from food preparation, and we'll assess whether medical care is needed."

  - name: preparation_checklist
    condition: "situation.type IS 'preparation'"
    action: "Good -- preparing before an emergency is the best time. Let's walk through the supplies you should have on hand: water storage, purification tools, sanitation supplies, and hygiene basics. Most of this costs under $50 and stores in a single bin."
```
