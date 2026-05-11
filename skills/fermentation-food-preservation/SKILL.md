---
name: fermentation-food-preservation
description: >-
  Food preservation techniques including fermentation, pickling, canning, drying, and smoking. Use when someone wants to preserve harvests, extend food shelf life, reduce waste, make fermented foods (kimchi, sauerkraut, yogurt, bread), or build food resilience.
metadata:
  category: skills
  tagline: >-
    Pickle, ferment, can, dry, and smoke. Turn a week of food into months of food — with techniques humans used for 10,000 years.
  display_name: "Fermentation & Food Preservation"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/fermentation-food-preservation"
---

# Fermentation & Food Preservation

Humans preserved food for 10,000 years before refrigeration existed. Fermentation, drying, salting, smoking, and canning are not quaint hobbies — they're core survival technology. A $5 head of cabbage and a tablespoon of salt becomes sauerkraut that lasts 6 months. A bushel of cucumbers becomes 30 jars of pickles. A sourdough starter lives forever and costs nothing after day one. This skill covers the practical methods, starting with the easiest (lacto-fermentation, which needs only salt and a jar) and progressing to canning and dehydration. Safety rules for each method are included because botulism is real and preventable.

```agent-adaptation
# Localization note
- Canning standards:
  US: USDA Complete Guide to Home Canning (nchfp.uga.edu)
  UK: MAFF guidelines
  AU: CSIRO food preservation guidelines
  CA: Health Canada home canning safety
- Altitude affects canning: boiling point decreases with elevation.
  Above 1,000 ft (305m), processing times and pressures must be adjusted.
  Agent must ask user's altitude for any canning guidance.
- Temperature units: Fahrenheit (US) vs Celsius (everywhere else).
  Provide both for all temperature references.
- Measurement: US cups/tablespoons vs metric grams/mL.
  Fermentation ratios by weight (grams) are more reliable than by volume.
- Local food safety authorities vary — swap USDA for equivalent
- Jar types: Mason/Ball jars (US/CA), Kilner jars (UK), Le Parfait (EU),
  Weck (DE). Two-piece lid systems are standard for water bath canning.
```

## Sources & Verification

- **USDA Complete Guide to Home Canning** -- the definitive US reference for safe canning procedures. https://nchfp.uga.edu/publications/publications_usda.html
- **National Center for Home Food Preservation (NCHFP)** -- research-based preservation guidance from the University of Georgia. https://nchfp.uga.edu
- **Sandor Katz, "The Art of Fermentation"** -- comprehensive reference on fermentation techniques worldwide
- **Ball Blue Book of Preserving** -- practical canning recipes and procedures, updated regularly
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User wants to make sauerkraut, kimchi, pickles, or other fermented foods
- User has a garden harvest and needs to preserve it
- User wants to start a sourdough bread starter
- User wants to learn water bath canning (jams, pickles, tomatoes)
- User wants to dehydrate foods (jerky, fruit leather, herbs)
- User wants to reduce food waste by extending shelf life
- User wants to understand food preservation safety (especially botulism prevention)
- User is building food resilience and self-sufficiency

## Instructions

### Step 1: Start with lacto-fermentation (the easiest method)

**Agent action**: This is the entry point for everyone. It requires no equipment, no heat, no special skills. Just salt, vegetables, and a jar.

```
LACTO-FERMENTATION — how it works:

THE SCIENCE (simple version):
Lactobacillus bacteria are already on your vegetables. Salt creates
an environment where Lactobacillus thrives and harmful bacteria can't
survive. The bacteria convert sugars into lactic acid, which preserves
the food, creates the sour flavor, and makes it probiotic.

YOU NEED:
- A glass jar (quart/liter Mason jar is ideal)
- Fresh vegetables
- Non-iodized salt (kosher salt, sea salt, or pickling salt —
  iodized table salt can inhibit fermentation)
- Water (if making a brine — unchlorinated; if your tap water is
  chlorinated, let it sit uncovered for 24 hours or use filtered)

THE UNIVERSAL RATIO:
- For dry-salted ferments (sauerkraut, kimchi): 2% salt by weight
  of the vegetables. For 1 kg (2.2 lbs) cabbage, use 20g salt
  (about 1 tablespoon).
- For brine ferments (pickles, vegetables in liquid): 3-5% brine.
  For 1 liter water, use 30-50g salt (2-3 tablespoons).

BASIC SAUERKRAUT (your first ferment):

Ingredients:
- 1 medium head green cabbage (about 2 lbs / 900g)
- 1 tablespoon (18g) non-iodized salt

Method:
1. Remove outer leaves (save one). Quarter cabbage, remove core.
2. Slice thin (1/8 inch / 3mm). A knife works. A mandoline is faster.
3. Put sliced cabbage in a large bowl. Add salt.
4. Massage and squeeze the cabbage with your hands for 5-10 minutes.
   The salt draws water out of the cells. You're making your own brine.
   Keep going until the cabbage is limp and there's liquid pooling
   in the bottom of the bowl.
5. Pack cabbage tightly into a clean quart jar, pushing down hard
   with your fist or a wooden spoon. The brine should rise above
   the cabbage. Leave 1-2 inches of headspace.
6. Place the saved outer leaf on top as a "cap" to keep shreds
   submerged. Weight it down (a small jar filled with water works,
   or a zip-lock bag of brine).
7. Cover loosely (the jar will off-gas CO2 — don't seal airtight
   or pressure builds. A loose lid, cloth, or airlock all work).
8. Leave at room temperature (65-75F / 18-24C), out of direct sunlight.
9. Check daily. Push cabbage down if it rises above the brine.
   Skim any white scum (kahm yeast — harmless but ugly).
10. Taste after 3 days. It's "done" when you like the sourness.
    Most people prefer 1-3 weeks.
11. Once it tastes right, seal and refrigerate. It lasts 6+ months
    in the fridge.

YIELD: 1 medium cabbage = 1 quart (1 liter) sauerkraut

COST: ~$2-3 per quart (vs $5-8 store-bought for inferior product)
```

### Step 2: Fermented pickles and kimchi

**Agent action**: Once the user has made sauerkraut, these are natural next steps using the same principles.

```
FERMENTED DILL PICKLES (brine method):

Ingredients:
- 2 lbs (900g) small pickling cucumbers (Kirby or similar)
- 4 cups (1L) water
- 2 tablespoons (36g) non-iodized salt
- 4 cloves garlic, smashed
- 2 tablespoons dill seed (or a few heads of fresh dill)
- 1 teaspoon black peppercorns
- 1 grape leaf, oak leaf, or bay leaf (tannins keep pickles crunchy)

Method:
1. Dissolve salt in water to make brine.
2. Cut 1/16 inch off the blossom end of each cucumber (contains an
   enzyme that makes pickles soft). Stem end is fine to leave.
3. Pack cucumbers vertically in a half-gallon jar.
4. Add garlic, dill, peppercorns, and leaf.
5. Pour brine over cucumbers. All cucumbers must be submerged.
6. Weight down. Cover loosely.
7. Room temperature, 3-7 days. Taste daily starting at day 3.
   Half-sours: 3-4 days. Full sours: 5-7 days.
8. Refrigerate when they taste right. Last 2-3 months.

YIELD: 2 lbs cucumbers = half-gallon jar of pickles
COST: ~$3-4 per half gallon (vs $6-8 store-bought)

---

BASIC KIMCHI:

Ingredients:
- 1 medium napa cabbage (about 2 lbs / 900g)
- 1/4 cup (72g) non-iodized salt
- 1 tablespoon grated fresh ginger
- 4 cloves garlic, minced
- 2-4 tablespoons gochugaru (Korean red pepper flakes —
  available at Asian grocery stores; regular red pepper flakes
  work but taste different)
- 1 tablespoon fish sauce (or soy sauce for vegan version)
- 1 teaspoon sugar
- 4 scallions, cut into 1-inch pieces
- 1 medium daikon radish or carrots, julienned (optional)

Method:
1. Quarter cabbage, cut into 2-inch pieces.
2. Toss with salt in a large bowl. Let sit 1-2 hours, tossing
   occasionally. Cabbage will wilt and release water.
3. Rinse cabbage 3 times under cold water to remove excess salt.
   Squeeze out water.
4. Mix ginger, garlic, gochugaru, fish sauce, and sugar into a paste.
5. Combine cabbage, paste, scallions, and radish/carrots.
   Mix thoroughly with gloved hands (gochugaru stains and burns).
6. Pack into a jar. Press down until brine covers vegetables.
7. Leave 2 inches headspace (kimchi is active — it bubbles a lot).
8. Room temperature 2-5 days. Burp the jar daily (open lid to
   release CO2).
9. Taste at day 2. Refrigerate when tangy enough for your taste.
10. Gets more sour over weeks in the fridge. Lasts 3-6 months.

YIELD: 1 cabbage = 1 quart kimchi
COST: ~$4-5 per quart (vs $8-12 store-bought)
```

### Step 3: Water bath canning (high-acid foods)

**Agent action**: This is where safety becomes critical. Botulism prevention rules are non-negotiable. Ask the user's altitude before providing processing times.

```
WATER BATH CANNING — for HIGH-ACID foods only

WHAT YOU CAN SAFELY WATER-BATH CAN:
- Fruits and fruit jams/jellies (naturally high acid)
- Pickles in vinegar (vinegar provides the acid)
- Tomatoes with added acid (2 tablespoons lemon juice per quart)
- Salsa (tested recipe only — acid balance matters)
- Fruit butters and chutneys

WHAT YOU CANNOT SAFELY WATER-BATH CAN:
- Vegetables without vinegar (green beans, corn, peas)
- Meat or fish
- Soups or stews
- Anything low-acid without added vinegar
- These REQUIRE pressure canning at 240F/116C to kill botulism
  spores. Water bath canning only reaches 212F/100C.

EQUIPMENT ($30-50 total):
[ ] Large pot with lid (deep enough to cover jars by 1-2 inches
    of boiling water) — or a dedicated canner with rack ($20-30)
[ ] Mason jars with two-piece lids (jar + band + flat lid)
    Jars: reusable forever. Bands: reusable. Flat lids: use once.
[ ] Jar lifter ($5-8) — essential for safely removing hot jars
[ ] Wide-mouth funnel ($3-5) — for filling jars without mess
[ ] Bubble remover / headspace tool ($3)

THE PROCESS:
1. Sterilize jars: boil in canner for 10 minutes (or run through
   dishwasher sanitize cycle)
2. Prepare your recipe (use TESTED recipes only — NCHFP, Ball Blue
   Book, or USDA-approved. Do NOT modify acid ratios, salt amounts,
   or thickeners. These are tested for safety, not just taste.)
3. Fill hot jars with hot product. Leave headspace as specified
   (typically 1/4 inch for jams, 1/2 inch for most other products).
4. Remove air bubbles: slide the bubble tool along the inside of the jar.
5. Wipe jar rim clean with a damp cloth (any residue prevents seal).
6. Place flat lid on jar, screw band on "fingertip tight" (snug but
   not wrenched).
7. Lower jars into boiling water. Water must cover lids by 1-2 inches.
8. Start timing when water returns to a full boil.
9. Process for the time specified in your recipe.

ALTITUDE ADJUSTMENT (critical):
- Sea level to 1,000 ft: use recipe time as written
- 1,001-3,000 ft: add 5 minutes
- 3,001-6,000 ft: add 10 minutes
- 6,001-8,000 ft: add 15 minutes
- 8,001-10,000 ft: add 20 minutes

AFTER PROCESSING:
1. Remove jars with lifter. Set on a towel on the counter.
2. Do not touch or tilt for 12-24 hours.
3. You'll hear "ping" sounds as lids seal (the lid gets sucked down).
4. After 24 hours, press center of each lid. If it doesn't flex, it's
   sealed. If it pops up and down, it didn't seal — refrigerate and
   use within 2 weeks.
5. Remove bands for storage (they can trap moisture and cause rust).
6. Label with contents and date.
7. Properly canned high-acid foods last 12-18 months in a cool,
   dark place.
```

### Step 4: Dehydration (jerky, fruit leather, herbs)

**Agent action**: Dehydration is one of the simplest preservation methods. A $40 dehydrator works, but an oven on low does too.

```
DEHYDRATION:

EQUIPMENT:
- Food dehydrator ($35-60 for a basic Nesco or Presto model) — most
  efficient option, consistent results
- OR: oven on lowest setting (170-200F / 75-93C) with door cracked
  open. Works but uses more energy and requires monitoring.

BEEF JERKY:
1. Use lean cuts (top round, eye of round, flank steak). Fat goes
   rancid — trim all visible fat.
2. Partially freeze for 1-2 hours (makes slicing easier).
3. Slice 1/4 inch thick, against the grain for tender jerky,
   with the grain for chewy jerky.
4. Marinate 4-24 hours in fridge:
   Basic marinade per 1 lb meat: 1/4 cup soy sauce, 1 tablespoon
   Worcestershire, 1 teaspoon garlic powder, 1 teaspoon onion powder,
   1/2 teaspoon black pepper, optional: 1 teaspoon smoked paprika,
   hot sauce to taste.
5. Pat strips dry. Lay flat on dehydrator trays, not touching.
6. Dehydrate at 160F (71C) for 4-6 hours.
7. USDA safety note: heat meat to 160F (71C) internal temp before
   or during dehydrating to kill pathogens. Some people pre-heat
   strips in a 275F oven for 10 minutes before dehydrating.
8. Done when strips crack but don't break when bent.
9. Store in airtight container or vacuum-seal. Lasts 1-2 months at
   room temp, 6+ months vacuum-sealed.

YIELD: 1 lb raw meat = about 1/3 lb jerky (meat loses 2/3 of
its weight in water)
COST: ~$5-6/lb jerky from $8-10/lb meat (vs $20-30/lb store-bought)

FRUIT LEATHER:
1. Puree fruit in a blender (any fruit works — strawberry, apple,
   peach, mango, mixed berry).
2. Add sweetener if needed (1-2 tablespoons honey per 2 cups puree).
3. Spread 1/8 inch thick on parchment-lined dehydrator tray or
   baking sheet.
4. Dehydrate at 135F (57C) for 8-12 hours.
5. Done when tacky but not sticky. Peel off parchment easily.
6. Roll in parchment paper, store in airtight container.
7. Lasts 1 month at room temp, 6+ months in freezer.

HERBS:
1. Wash and dry thoroughly (any moisture = mold).
2. Remove leaves from stems for small-leaf herbs (thyme, oregano).
   Leave large leaves whole (basil, mint).
3. Dehydrate at 95-115F (35-46C) for 2-4 hours. Low temp preserves
   volatile oils (flavor).
4. Done when leaves crumble between fingers.
5. Store whole (crumble when using — whole leaves retain flavor longer).
6. Dried herbs last 1-3 years in airtight jars away from light.
```

### Step 5: Sourdough starter

**Agent action**: A sourdough starter is a living culture. Once established, it lasts forever with feeding. This takes 7-10 days to build from scratch.

```
SOURDOUGH STARTER FROM SCRATCH:

YOU NEED:
- All-purpose flour or whole wheat flour (whole wheat starts faster
  due to more wild yeast on the bran)
- Water (unchlorinated — filtered or left to sit 24 hours)
- A glass jar (quart size)
- A kitchen scale (strongly recommended — weighing is far more
  accurate than measuring cups for this)

DAY 1:
- Mix 50g flour + 50g water in jar. Stir well.
- Cover loosely (cloth, loose lid). Room temperature.

DAY 2:
- Look for bubbles. Probably none yet. That's normal.
- Discard half the starter. Add 50g flour + 50g water. Stir.

DAYS 3-5:
- Repeat daily: discard half, feed 50g flour + 50g water.
- By day 3-4, you should see bubbles and a slightly sour smell.
- If it smells like nail polish remover (acetone): it's hungry.
  Feed more frequently (twice a day).

DAYS 6-10:
- The starter should be rising predictably — doubling in size
  within 4-8 hours of feeding.
- When it reliably doubles in 4-8 hours, it's ready to bake with.
- Total flour cost to build a starter: about $0.50.

MAINTAINING YOUR STARTER:
- If baking weekly: keep on counter, feed daily (discard half,
  add equal parts flour and water)
- If baking less often: store in fridge. Feed once a week.
  Take it out and feed twice before baking (to reactivate).
- "Discard" isn't waste — use it for pancakes, waffles, crackers,
  pizza dough. Search "sourdough discard recipes."

YOUR STARTER IS DEAD IF:
- Covered in pink, orange, or fuzzy mold = throw out, start over
- No activity after 14 days of daily feeding = start over
- Black liquid on top ("hooch") = it's not dead, just hungry.
  Pour off the liquid and feed it. It'll recover.
```

### Step 6: Quick vinegar pickling

**Agent action**: Fastest preservation method. Pickles in 30 minutes. No fermentation wait.

```
QUICK VINEGAR PICKLES (refrigerator pickles):

BASIC BRINE:
- 1 cup vinegar (white, apple cider, or rice — 5% acidity minimum)
- 1 cup water
- 1 tablespoon salt
- 1 tablespoon sugar (optional, balances acid)
- Bring to a boil, stir to dissolve salt and sugar.

PICKLE ANYTHING:
- Cucumbers (classic dill pickles)
- Red onions (for tacos, sandwiches, salads)
- Carrots and daikon (Vietnamese banh mi style)
- Jalapenos
- Green beans (dilly beans)
- Cauliflower
- Radishes

METHOD:
1. Slice or prepare your vegetables.
2. Pack into a clean jar with spices:
   - Dill pickles: garlic, dill, peppercorns, mustard seed
   - Spicy: red pepper flakes, garlic, coriander
   - Sweet: cinnamon stick, cloves, allspice (for fruit pickles)
3. Pour hot brine over vegetables. Let cool.
4. Refrigerate. Ready in 30 minutes (improve over 24-48 hours).
5. Last 2-3 months in the fridge.

COST: ~$1-2 per jar. Vinegar is cheap. Spices last forever.

FOR SHELF-STABLE PICKLES:
Use the water bath canning process from Step 3 with a tested recipe.
Quick pickles are fridge-only unless properly canned.
```

## Botulism Prevention (critical safety section)

```
BOTULISM — what it is and how to prevent it

WHAT:
Clostridium botulinum bacteria produce a toxin that causes paralysis
and death. The spores survive boiling (212F/100C). They thrive in
anaerobic (no oxygen), low-acid, moist environments — which describes
the inside of an improperly canned jar perfectly.

PREVENTION RULES (non-negotiable):
1. NEVER water-bath can low-acid foods (vegetables, meat, soups).
   These require pressure canning at 240F/116C for the required time.
2. ALWAYS use tested recipes from USDA, NCHFP, or Ball. Do not
   modify acid levels, proportions, or thickeners.
3. ALWAYS add acid to borderline foods: tomatoes need 2 tablespoons
   lemon juice or 1/2 teaspoon citric acid per quart.
4. NEVER use damaged or unsealed jars.
5. NEVER taste food from a jar with a bulging lid, broken seal,
   or off smell. Discard without tasting.
6. When in doubt, boil the food for 10 minutes before eating
   (heat destroys the toxin, though not the spores).

FERMENTATION IS SAFE because:
- The acidic environment (lactic acid) prevents C. botulinum growth
- This is why proper salt ratios matter — they ensure Lactobacillus
  dominates and lowers pH before harmful bacteria can establish

SIGNS OF BOTULISM IN CANNED FOOD:
- Bulging lid
- Leaking jar
- Spurting liquid when opened
- Off smell or appearance
- Mold on the surface
- Any of these = discard the entire jar without tasting
```

## If This Fails

- Sauerkraut is slimy or smells rotten: Discard it. Likely too warm (above 80F/27C) or not enough salt. Retry with accurate salt measurement (2% by weight) at 65-75F (18-24C).
- Fermented pickles are soft/mushy: The blossom end wasn't removed (it contains an enzyme that softens pickles), or fermentation went too long. Add a grape leaf or oak leaf next time — tannins help crunchiness.
- Canned jar didn't seal: Refrigerate and use within 2 weeks. Or reprocess within 24 hours with a new lid. Don't force it — an unsealed jar at room temperature is a botulism risk.
- Sourdough starter won't rise: Use whole wheat flour for a few feedings (more wild yeast). Move to a warmer spot (75-80F/24-27C). Feed twice daily instead of once. If no activity after 14 days, start over.
- Mold on ferment: If it's white surface scum (kahm yeast), skim it off — the ferment below is fine. If it's fuzzy, black, pink, or orange mold, discard everything.

## Rules

- Never water-bath can low-acid foods. This is the #1 rule of canning safety and the one most commonly broken by well-meaning people sharing grandma's "recipe." Botulism is odorless and tasteless.
- Use tested recipes for all canning. Do not modify acid ratios, thickeners, or proportions. Safety testing is specific to the exact recipe.
- Keep ferments submerged. Vegetables above the brine are exposed to air and will mold. Weight them down.
- Use non-iodized salt for fermentation. Iodine inhibits the beneficial bacteria you're trying to cultivate.
- Label everything with contents, date, and method. "Mystery jar from sometime last year" is not a food safety strategy.

## Tips

- Lacto-fermentation is the gateway skill. If you can make sauerkraut, you can make kimchi, fermented hot sauce, fermented salsa, preserved lemons, and dozens of other fermented foods with the same technique (salt + vegetable + jar + time).
- Kitchen scale > measuring cups for fermentation. The 2% salt ratio by weight is reliable. "A tablespoon" varies depending on salt crystal size by up to 40%.
- The "discard" from sourdough starter is a cooking ingredient, not waste. Sourdough discard pancakes, waffles, and crackers are excellent and use a product most people throw away.
- Canning is seasonal work. Do it during harvest season when produce is cheapest and most abundant. A weekend of canning in August can stock your pantry through March.
- Fermentation connects directly to the grow-food-anywhere skill. A small garden producing more tomatoes or cucumbers than you can eat in a week is not a problem — it's a preservation opportunity.
- Start with one method and get comfortable before branching out. Sauerkraut first, then pickles, then canning. Trying everything at once leads to overwhelm and wasted food.

## Agent State

```yaml
preservation:
  methods_practiced: []
  current_project: null
  ferments_active: []
  canned_inventory: []
  equipment_owned: []
  altitude_ft: null
fermentation:
  sauerkraut_made: false
  kimchi_made: false
  pickles_made: false
  sourdough_starter_active: false
  starter_age_days: null
  starter_feeding_schedule: null
canning:
  has_equipment: false
  has_tested_recipes: false
  knows_botulism_rules: false
  altitude_adjustment_known: false
dehydration:
  has_dehydrator: false
  jerky_made: false
  fruit_leather_made: false
  herbs_dried: false
```

## Automation Triggers

```yaml
triggers:
  - name: first_ferment_guidance
    condition: "fermentation.sauerkraut_made IS false AND preservation.current_project IS SET"
    action: "If you're new to preservation, start with sauerkraut. It's the simplest ferment — just cabbage, salt, and a jar. No special equipment, no heat, no risk of botulism. Let me walk you through it."

  - name: canning_safety_check
    condition: "preservation.current_project CONTAINS 'canning' AND canning.knows_botulism_rules IS false"
    action: "Before we start canning, let's cover botulism prevention. This is the one area of food preservation where mistakes can be fatal. It takes 5 minutes to learn the rules that keep you safe."

  - name: altitude_check
    condition: "preservation.current_project CONTAINS 'canning' AND preservation.altitude_ft IS null"
    action: "I need your altitude before giving canning times. Processing times must be adjusted above 1,000 feet. What's your elevation? (Check your city on Google if unsure.)"

  - name: sourdough_feeding_reminder
    condition: "fermentation.sourdough_starter_active == true AND fermentation.starter_feeding_schedule == 'counter'"
    schedule: "daily"
    action: "Sourdough feeding reminder: discard half, add equal parts flour and water. If you're not baking this week, consider moving it to the fridge where it only needs weekly feeding."

  - name: harvest_preservation_prompt
    condition: "user_context CONTAINS 'garden' OR user_context CONTAINS 'harvest'"
    schedule: "August 1 annually"
    action: "Peak harvest season. If your garden is producing more than you can eat, now's the time to preserve. What do you have coming in? I'll recommend the best preservation method for each crop."
```
