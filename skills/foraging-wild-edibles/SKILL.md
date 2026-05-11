---
name: foraging-wild-edibles
description: >-
  Safe identification and harvesting of common wild edible plants. Use when someone wants to supplement food supply with wild plants, learn plant identification skills, or understand what's safe vs dangerous in their local environment.
metadata:
  category: skills
  tagline: >-
    Identify 15 safe, common wild foods in your region. What to eat, what to never touch, and the one rule that keeps you alive.
  display_name: "Foraging & Wild Edibles"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/foraging-wild-edibles"
---

# Foraging & Wild Edibles

The one rule: if you are not 100% certain of the identification, do not eat it. Not 90%. Not "pretty sure." One hundred percent. That rule kept humans alive for 200,000 years and it still works. With that rule firmly in place, foraging is a practical skill that connects you to your local food system, supplements your groceries, and teaches you to see your environment in a completely different way. This skill covers 15 near-universal wild edibles, the deadly plants to avoid, and how to learn safely in your specific region.

```agent-adaptation
# Localization note — CRITICAL for this skill
- Edible plants vary dramatically by region, climate zone, and hemisphere.
  The 15 plants listed here are chosen for near-global distribution in
  temperate zones. Agent MUST:
  1. Identify the user's climate zone (USDA hardiness zone or Koppen
     climate classification)
  2. Confirm which of the 15 listed plants are present in their region
  3. Substitute region-appropriate alternatives for any that aren't
  4. Add region-specific deadly lookalikes
- Foraging legality varies:
  US: legal on private land with permission, varies on public land
    (National Parks = illegal, National Forests = generally legal
    for personal use, state/city parks = varies by municipality)
  UK: "right to roam" covers foraging for personal use on most land
  AU: varies by state — illegal in many national parks
  EU: varies widely by country (liberal in Scandinavia, restricted
    in some Mediterranean countries)
- Mushroom identification is EXTREMELY region-specific and dangerous
  to learn from text. Always direct to in-person local experts.
- Seasonal availability differs by hemisphere — flip all season
  references for Southern Hemisphere users
```

## Sources & Verification

- **USDA Plants Database** -- plant identification, range maps, and classification. https://plants.usda.gov
- **Samuel Thayer, "The Forager's Harvest" and "Nature's Garden"** -- widely regarded as the most reliable North American foraging references
- **Peterson Field Guides (edible wild plants)** -- standard field identification references
- **State extension office resources** -- local plant identification and foraging guidance. Search "[state] extension office wild plants."
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User wants to learn what's edible growing near them
- User found a plant and wants to know if it's safe to eat
- User wants to start foraging and needs a safe starting point
- User wants to understand which wild plants to avoid
- User is in a wilderness situation and needs to identify food sources
- User wants to supplement their diet with wild foods
- User is interested in connecting with local food systems

## Instructions

### Step 1: Learn the ground rules

**Agent action**: Before identifying any plant, establish these non-negotiable principles. Skip this at your own risk.

```
FORAGING GROUND RULES:

RULE #1: 100% CERTAIN OR DON'T EAT IT.
No exceptions. No "pretty sure." No "it looks like the picture."
100% positive identification or you walk away. The consequences
of getting this wrong range from vomiting to organ failure to death.

RULE #2: USE MULTIPLE IDENTIFICATION FEATURES.
Never identify a plant by a single characteristic. Use at least
3-4 features: leaf shape, leaf arrangement, stem shape, flower
color and structure, smell, habitat, season.

RULE #3: KNOW THE DANGEROUS LOOKALIKES FIRST.
For every edible plant, know what it can be confused with. Learn
the dangerous plants BEFORE learning the edible ones.

RULE #4: START WITH THE EASY ONES.
The 15 plants in this skill were chosen because they're common,
easy to identify, and have no deadly lookalikes (or the lookalikes
are obvious to distinguish). Start here. Stay here until confident.

RULE #5: LEARN FROM A LOCAL EXPERT.
Books and apps get you started. A local foraging walk with an
experienced guide teaches you more in 2 hours than a year of
reading. Find one through: mycological societies, native plant
societies, extension offices, community colleges, local foraging
groups on Facebook/Meetup.

RULE #6: SUSTAINABLE HARVESTING.
- Never take more than 1/3 of a stand of any plant
- Don't harvest rare or protected species
- Don't forage in polluted areas (roadsides, treated lawns,
  industrial runoff zones)
- Don't forage from someone's property without permission
- Check local regulations before foraging on public land
```

### Step 2: The 15 near-universal safe edibles

**Agent action**: Ask the user's location/climate zone first. Confirm which of these are present in their region before proceeding. All 15 are found across most temperate zones in North America, Europe, and parts of Asia/Oceania.

```
15 SAFE, COMMON WILD EDIBLES:

1. DANDELION (Taraxacum officinale)
   WHERE: everywhere. Lawns, fields, roadsides, cracks in pavement.
   PARTS: entire plant is edible — leaves (salad), flowers (fritters,
     wine), roots (roasted as coffee substitute)
   SEASON: spring for tender leaves, flowers in spring-summer
   ID: rosette of deeply toothed leaves, single hollow stem per
     flower, yellow flower, milky white sap
   LOOKALIKES: cat's ear (Hypochaeris) — also edible, so no risk

2. COMMON PLANTAIN (Plantago major)
   WHERE: lawns, paths, disturbed soil. One of the most common
     "weeds" worldwide.
   PARTS: young leaves (salad or cooked), seeds
   SEASON: spring-fall
   ID: broad oval leaves with parallel veins, grows in a rosette,
     tall flower spike with tiny flowers
   NOTE: not related to the banana-family plantain

3. WHITE CLOVER (Trifolium repens)
   WHERE: lawns, fields, everywhere grass grows
   PARTS: flowers (raw or dried for tea), young leaves
   SEASON: spring-fall
   ID: three round leaflets with white chevron marking, white
     spherical flower heads
   NOTE: red clover (Trifolium pratense) is also edible

4. CHICKWEED (Stellaria media)
   WHERE: gardens, lawns, disturbed soil, shady spots
   PARTS: entire above-ground plant (salad, sandwich green)
   SEASON: early spring and late fall (prefers cool weather)
   ID: small oval leaves in opposite pairs, tiny white flowers with
     deeply split petals (look like 10 petals but actually 5 split),
     single line of hairs along the stem (alternating sides)
   TASTE: mild, like lettuce

5. LAMB'S QUARTERS (Chenopodium album)
   WHERE: gardens, disturbed soil, agricultural edges
   PARTS: young leaves and tips (cooked like spinach — one of the
     most nutritious wild greens)
   SEASON: spring-summer
   ID: diamond-shaped leaves with irregular teeth, white powdery
     coating on young leaves, grooved stem
   NUTRITION: more iron, calcium, and protein than spinach

6. WOOD SORREL (Oxalis species)
   WHERE: forests, gardens, shady areas
   PARTS: leaves, flowers, seed pods (all raw — tart lemon flavor)
   SEASON: spring-fall
   ID: three heart-shaped leaflets that fold along the center crease,
     small 5-petaled flowers (yellow, white, or pink depending on species)
   NOTE: not related to sorrel (Rumex) — different plant family entirely
   CAUTION: high in oxalic acid. Eat in moderation (small amounts fine;
     don't make it your entire diet)

7. BLACKBERRIES / RASPBERRIES (Rubus species)
   WHERE: forest edges, roadsides, disturbed areas, hedgerows
   PARTS: berries (raw, jams, pies), young leaves (tea)
   SEASON: summer-early fall
   ID: thorny canes, compound leaves in groups of 3-5, white flowers,
     aggregate berries. Blackberries = fruit doesn't separate from core.
     Raspberries = fruit is hollow (separates from core).
   NOTE: there are no deadly berry lookalikes in this genus

8. ELDERBERRIES (Sambucus nigra / S. canadensis)
   WHERE: forest edges, stream banks, roadsides
   PARTS: berries (COOKED ONLY — raw are mildly toxic), flowers
     (fritters, cordial, tea)
   SEASON: flowers in spring, berries in late summer
   ID: compound leaves with 5-7 toothed leaflets, flat-topped clusters
     of tiny white flowers, clusters of small dark purple-black berries
   WARNING: raw berries cause nausea. Cook or dry them.
   CRITICAL: do NOT confuse with water hemlock or pokeweed berries

9. CATTAIL (Typha latifolia)
   WHERE: marshes, pond edges, ditches, anywhere with standing water
   PARTS: nearly everything — young shoots (spring, like hearts of palm),
     pollen (flour supplement), rhizomes (starchy, can be processed
     like potato)
   SEASON: year-round depending on part
   ID: tall (4-8 ft), flat strap-like leaves, distinctive brown
     cylindrical seed head ("corn dog on a stick")
   WARNING: do NOT confuse with iris (which grows in similar habitats
     and has similar leaves but no cattail seed head). Iris is toxic.

10. WILD GARLIC / RAMPS (Allium species)
    WHERE: forests, moist woodland, stream banks
    PARTS: leaves, bulbs (use like garlic or onion)
    SEASON: early spring (ramps are one of the first spring greens)
    ID: broad, smooth leaves emerging from a bulb, strong garlic/onion
      smell when crushed
    THE SMELL TEST: if it smells like garlic or onion, it's an Allium.
    If it doesn't smell like garlic/onion, PUT IT DOWN. Lily of the
    valley (deadly) looks similar but has NO onion/garlic smell.

11. PURSLANE (Portulaca oleracea)
    WHERE: gardens, sidewalk cracks, disturbed soil, hot dry areas
    PARTS: stems and leaves (raw in salads or cooked)
    SEASON: summer
    ID: succulent (thick, fleshy) red stems, small paddle-shaped
      fleshy leaves, grows low to ground
    NUTRITION: highest omega-3 fatty acid content of any leafy green
    WARNING: spurge (Euphorbia) looks vaguely similar but has milky
      sap (purslane has clear sap) and thinner, non-succulent leaves

12. ROSE HIPS (Rosa species)
    WHERE: wherever wild roses grow — hedgerows, forest edges, fields
    PARTS: the fruit (the red/orange bulb left after the flower drops)
    SEASON: fall (after first frost they sweeten)
    ID: the small round or oval fruit of any wild rose. If the plant
      had roses, the hips are edible.
    USE: tea (slice open, remove seeds and hairs, steep), jam, syrup
    NUTRITION: extremely high in vitamin C (20x more than oranges
      by weight)

13. ACORNS (Quercus species)
    WHERE: wherever oaks grow (nearly everywhere in temperate zones)
    PARTS: the nut (after processing)
    SEASON: fall
    PROCESSING REQUIRED: acorns contain tannins that are bitter and
      can cause nausea. Leach the tannins: shell acorns, grind or chop,
      soak in water (change water repeatedly until bitterness is gone —
      takes several water changes over 1-2 days, or use running water).
      White oak group acorns have less tannin and leach faster.
    USE: flour (dried and ground), porridge, roasted

14. PINE NEEDLE TEA (Pinus species)
    WHERE: wherever pine trees grow
    PARTS: needles (for tea)
    SEASON: year-round (best in spring when needles are young)
    ID: needle-like leaves in bundles (fascicles). Confirm it's a
      true pine (Pinus genus) — needles come in bundles of 2, 3, or 5.
    AVOID: yew (Taxus — flat needles, not in bundles, red berries —
      EXTREMELY toxic). Norfolk Island pine and Ponderosa pine should
      be avoided by pregnant individuals.
    USE: steep a small handful of fresh needles in hot water 10-15 min.
      High in vitamin C.

15. STINGING NETTLES (Urtica dioica)
    WHERE: moist forest edges, stream banks, disturbed soil
    PARTS: young leaves and tips (COOKED — cooking neutralizes the sting)
    SEASON: early spring (harvest before flowering)
    ID: opposite serrated leaves, square stem, covered in fine
      stinging hairs
    HARVEST: wear gloves. The sting is immediate on bare skin.
    USE: cook like spinach (sauteed, in soups, as tea). Extremely
      nutritious — high in iron, calcium, and protein.
```

### Step 3: Deadly plants to know

**Agent action**: These are the ones that kill or seriously injure. Knowing what NOT to eat is more important than knowing what to eat.

```
DEADLY PLANTS TO RECOGNIZE AND AVOID:

WATER HEMLOCK (Cicuta species):
- THE most toxic plant in North America
- Looks like: wild carrot, wild parsnip, elderflower
- Found near water, wet meadows, stream banks
- White umbrella-shaped flower clusters
- DISTINCTIVE: purple-streaked hollow stem, chambered root
  (cross-section shows distinct chambers)
- Lethal dose: one bite of the root can kill an adult
- Causes violent seizures within 15-30 minutes

POISON HEMLOCK (Conium maculatum):
- Killed Socrates
- Looks like: wild carrot (Queen Anne's lace), parsley, fennel
- Purple blotches on smooth hollow stem
- "Mousy" unpleasant smell when crushed (carrots smell like carrots)
- White umbrella-shaped flower clusters
- All parts lethal — causes ascending paralysis

DEADLY NIGHTSHADE (Atropa belladonna):
- Purple-black berries that look tempting (sweet taste)
- Bell-shaped purple flowers
- Found in shady, disturbed areas
- Causes hallucinations, rapid heartbeat, death

DEATH CAMAS (Zigadenus / Anticlea):
- Looks like: wild onion/garlic
- CRITICAL DIFFERENCE: no onion or garlic smell
- If it looks like an onion but doesn't SMELL like one, walk away

FOXGLOVE (Digitalis purpurea):
- Tall spike of purple/pink bell-shaped flowers
- Contains cardiac glycosides — causes heart failure
- Sometimes confused with comfrey (which is also not recommended
  for internal use)

THE RULE OF UMBRELLA FLOWERS:
Plants in the carrot/parsley family (Apiaceae) with umbrella-shaped
white flower clusters include some of the deadliest plants on Earth
AND some common edibles (carrots, parsley, fennel). Unless you are
an experienced forager who can confidently distinguish these species,
AVOID ALL wild plants with umbrella-shaped white flower clusters.
This single rule eliminates the most common fatal foraging mistakes.
```

### Step 4: The universal edibility test (last resort only)

**Agent action**: Include this for completeness but emphasize it's a survival-only protocol, not a foraging technique.

```
UNIVERSAL EDIBILITY TEST — SURVIVAL SITUATIONS ONLY

This is NOT a foraging method. This is a last-resort protocol for
wilderness survival when you have no knowledge of local plants.
It takes 24+ hours and may still fail for some toxins.

DO NOT USE THIS IF:
- You have any other food source
- You're within reach of civilization
- The plant has any of the "avoid" characteristics below

AVOID ENTIRELY (do not test):
- Umbrella-shaped white flower clusters (potential hemlock family)
- Plants with milky or discolored sap
- Beans, bulbs, or seeds from unknown plants
- Plants with an almond scent in leaves or bark (cyanide)
- Grain heads with pink, purple, or black spurs (ergot)
- Plants with three-leaflet growth pattern (potential poison ivy/oak)

THE TEST (8-hour minimum per plant part):
1. Test only one plant part at a time (leaf, stem, root, fruit)
2. Smell: crush and smell. Bitter almond = discard. Strong chemical
   smell = discard.
3. Skin contact: rub on inner wrist. Wait 8 hours. Any reaction
   (rash, redness, burning, numbness) = discard.
4. Lip test: touch to your lip for 15 minutes. Any tingling, burning,
   or numbness = discard.
5. Tongue test: place on your tongue for 15 minutes. Do not swallow.
   Any bad reaction = spit, rinse, discard.
6. Chew test: chew and hold in mouth 15 minutes. Do not swallow.
   Any bad reaction = spit, rinse, discard.
7. Swallow test: eat a small amount. Wait 8 hours. No negative
   effects = probably safe for that plant part.
8. Eat a larger portion. Wait another 8 hours.
```

### Step 5: How to learn locally

**Agent action**: The 15-plant list is a starting point. Real foraging competency comes from local knowledge. Help the user find local resources.

```
BUILDING LOCAL FORAGING KNOWLEDGE:

FIND A LOCAL GUIDE:
- Search "[your area] foraging walk" or "wild plant walk"
- Mycological societies (mushroom clubs) often do plant walks too
- Native plant societies
- State/county extension offices often host free workshops
- Community colleges and adult education programs
- Local Facebook groups and Meetup.com foraging groups
- Cost: free to $30 per walk, well worth it

GET FIELD GUIDES FOR YOUR REGION:
- General: Peterson Field Guide to Edible Wild Plants (your region)
- North America: Samuel Thayer's books ("The Forager's Harvest,"
  "Nature's Garden," "Incredible Wild Edibles")
- UK: "Food for Free" by Richard Mabey
- General: "Edible Wild Plants" by John Kallas
- Cost: $15-25 per book

USE APPS AS A SUPPLEMENT (never sole identification):
- iNaturalist (free) — community-verified plant ID, excellent for
  learning. Submit photos and experts confirm.
- PlantNet (free) — AI-assisted ID. Good starting point but NEVER
  trust an app alone for edibility decisions.
- PictureThis — similar AI-based ID, subscription model

A NOTE ON MUSHROOMS:
This skill does NOT cover mushroom foraging in detail on purpose.
Mushroom identification requires hands-on learning from an experienced
local mycologist. The consequences of misidentification are severe
(liver failure, death). Some common edibles have deadly lookalikes
that differ by subtle features impossible to convey in text.
If you want to forage mushrooms:
1. Join a local mycological society
2. Learn from an expert in the field, not from photos
3. Start with species that have no dangerous lookalikes
   (chicken of the woods, morels — and even these have caveats)
4. Get every identification confirmed by an experienced forager
   until you have years of practice
```

### Step 6: Seasonal availability and planning

**Agent action**: Ask the user's region and provide a seasonal calendar. This example is for temperate Northern Hemisphere.

```
SEASONAL FORAGING CALENDAR (temperate Northern Hemisphere):

EARLY SPRING (March-April):
- Ramps/wild garlic (emerging leaves)
- Nettles (young tips, before flowering)
- Dandelion greens (most tender now)
- Chickweed
- Clover (young leaves)

LATE SPRING (May-June):
- Elder flowers
- Dandelion flowers
- Wood sorrel
- Lamb's quarters (begins)
- Pine needles (young, bright green tips)

SUMMER (July-August):
- Blackberries and raspberries
- Purslane
- Lamb's quarters (peak)
- Cattail pollen
- Wood sorrel

EARLY FALL (September-October):
- Elderberries
- Acorns
- Rose hips
- Late blackberries
- Cattail rhizomes

LATE FALL - WINTER:
- Rose hips (improved after frost)
- Cattail rhizomes
- Pine needle tea (year-round)
- Dandelion roots (fall/winter harvest for roasting)
- Most foraging is limited — this is the season for processing
  and using preserved harvests

SOUTHERN HEMISPHERE:
Shift all seasons by 6 months. March = early fall. September = early spring.
```

## If This Fails

- Can't positively identify a plant: Don't eat it. Photograph it from multiple angles (whole plant, close-up of leaf, stem, flower, habitat) and submit to iNaturalist for community identification. Wait for expert confirmation.
- Ate something and feeling sick: Call Poison Control immediately. US: 1-800-222-1222. UK: 111. AU: 13 11 26. Keep a sample of what you ate. Note the time of ingestion and symptoms.
- No local foraging groups: Check iNaturalist for active users in your area — message them. Look for native plant societies. Ask at your local library. Extension offices sometimes connect you with local experts.
- Plants in your area aren't on this list: These 15 were chosen for global distribution, but your region has dozens of edibles not listed here. A regional field guide and a local foraging walk are the best next steps.

## Rules

- 100% identification certainty or you don't eat it. This rule has no exceptions.
- Never forage from areas treated with pesticides, herbicides, or near heavy traffic (lead and pollutant absorption).
- Never trust a plant identification app as your sole source. Use it as a starting point, then confirm with field guide features and ideally a local expert.
- Take only what you need and never more than 1/3 of any stand. Sustainable harvesting means the patch is there next year.
- Do not forage mushrooms based on this skill file alone. Mushroom identification requires in-person training with a local expert.
- Know your local foraging laws before harvesting on public land.

## Tips

- The "smell test" for the Allium family (garlic, onion) is the single most useful safety check in foraging. If it looks like wild garlic/onion and smells like garlic/onion, it's safe. If there's no smell, it might be lily of the valley or death camas. Walk away.
- The three easiest first forages: dandelion (you already know what it looks like), blackberries (obvious and delicious), and clover (in every lawn). Start with these to build confidence.
- Foraging near your home is better than foraging in the wilderness. You can observe the same patches through seasons, watch them grow, and learn their full life cycle. This builds real identification skill.
- Young plants and early growth are almost always more tender, more flavorful, and easier to prepare than mature plants. Dandelion in March vs July is two completely different eating experiences.
- A single foraging walk with a local expert will teach you more than 6 months of book learning. The sensory experience of touching, smelling, and seeing plants in context is irreplaceable.

## Agent State

```yaml
foraging:
  user_location: null
  climate_zone: null
  hemisphere: null
  experience_level: null
  plants_confidently_identified: []
  plants_learning: []
  local_guide_found: false
  field_guide_owned: false
  seasons_foraged: []
safety:
  knows_ground_rules: false
  knows_deadly_plants: false
  knows_umbrella_flower_rule: false
  knows_allium_smell_test: false
  poison_control_number_saved: false
```

## Automation Triggers

```yaml
triggers:
  - name: location_required
    condition: "foraging.user_location IS null"
    action: "Before we talk about foraging, I need your location (state/province or climate zone). Edible plants vary dramatically by region, and I need to confirm which species are relevant to your area."

  - name: safety_first
    condition: "foraging.experience_level == 'beginner' AND safety.knows_ground_rules IS false"
    action: "You're new to foraging. Before we identify anything, let's cover the ground rules — especially the deadly plants in your region. Knowing what to avoid matters more than knowing what to eat."

  - name: seasonal_foraging_prompt
    condition: "foraging.user_location IS SET AND foraging.experience_level IS SET"
    schedule: "monthly during growing season"
    action: "New foraging month. Based on your location and the current season, here's what's available now and what to look for. Want a seasonal checklist?"

  - name: mushroom_safety_redirect
    condition: "user_query CONTAINS 'mushroom' OR user_query CONTAINS 'fungi'"
    action: "Mushroom identification is outside the scope of text-based guidance — the risks are too high. I can help you find a local mycological society or foraging group where you can learn hands-on from an expert. That's the only safe way to start."
```
