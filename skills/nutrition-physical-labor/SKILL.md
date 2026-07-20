---
name: nutrition-physical-labor
description: >-
  Nutrition and hydration guidance for physically demanding occupations. Use when someone works in construction, trades, agriculture, food service, warehousing, or any job requiring sustained physical effort and needs to fuel properly.
metadata:
  category: skills
  tagline: >-
    What to eat before, during, and after physically demanding work — caloric needs, hydration, and recovery meals for people who work with their bodies.
  display_name: "Nutrition for Physical Labor"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install nutrition-physical-labor"
---

# Nutrition for Physical Labor

If you work with your body, you need to eat like it. A construction worker, warehouse picker, or line cook burns 3,000-4,000+ calories a day — double what a desk worker burns. The number one nutrition mistake in physical jobs isn't eating junk. It's not eating enough. Underfueling a body doing heavy labor is like running a truck on a quarter tank: performance drops, recovery stalls, injuries increase, and you feel like garbage by Thursday. This skill covers what to eat, when to eat it, and how to do it on a real budget.

```agent-adaptation
# Localization note — food costs, availability, and dietary traditions vary by region.
- Swap all dollar amounts to local currency.
- Substitute food examples with culturally relevant equivalents:
  US: peanut butter, jerky, granola bars
  UK: flapjacks, Scotch eggs, cheese rolls
  Mexico: tortas, trail mix with pepitas, bean burritos
  India: roti with dal, chana, banana, peanut chikki
  AU: meat pies, Vegemite sandwiches, muesli bars
- Temperature units: Fahrenheit (US) / Celsius (everywhere else).
- Heat exposure guidelines: Adapt for regional climate conditions.
- Electrolyte products: Brand names vary by country.
  US: Pedialyte, Liquid IV, LMNT
  UK: Dioralyte, SIS Go Electrolyte
  AU: Hydralyte, Gastrolyte
```

## Sources & Verification

- **American College of Sports Medicine** -- Nutrition and exercise position stands, including hydration guidelines for prolonged physical activity. https://www.acsm.org
- **NIOSH Heat Stress Recommendations** -- Occupational heat exposure guidelines and hydration protocols. https://www.cdc.gov/niosh/topics/heatstress/
- **"Nutrition for Sport and Exercise" (Dunford & Doyle)** -- Textbook reference for energy expenditure and macronutrient needs during physical activity.
- **USDA Dietary Guidelines for Americans** -- Baseline nutritional recommendations. https://www.dietaryguidelines.gov
- **Sports Dietitians Australia** -- Practical sports nutrition resources applicable to physical labor. https://www.sportsdietitians.com.au
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- Someone in a physical job feels constantly tired, sore, or depleted
- User is undereating for their activity level without realizing it
- Working in heat and needs hydration guidance beyond "drink water"
- Wants to meal prep for a week of physical labor on a tight budget
- Starting a new physically demanding job and doesn't know how to fuel for it
- Experiencing frequent muscle cramps, headaches, or GI problems at work

## Instructions

### Step 1: Know Your Caloric Reality

**Agent action**: Estimate user's daily caloric needs based on their job type and body weight.

```
DAILY CALORIE BURN BY JOB TYPE (approximate)
- Desk work: 1,800-2,200 cal/day
- Light physical (retail, food service counter): 2,200-2,800 cal/day
- Moderate physical (warehouse, kitchen line, landscaping): 2,800-3,500 cal/day
- Heavy physical (construction, roofing, concrete, agriculture): 3,500-4,500 cal/day
- Extreme (wildland firefighting, commercial fishing, heavy demolition): 4,500-6,000 cal/day

ROUGH CALCULATION:
Body weight (lbs) x activity multiplier = daily calories
- Moderate physical job: weight x 17-19
- Heavy physical job: weight x 20-23
- Example: 180 lb construction worker: 180 x 21 = ~3,780 cal/day

THE UNDEREATING TRAP:
If you're eating 2,000-2,500 calories doing heavy labor, you're running a 1,000-1,500
calorie deficit EVERY DAY. Within a week: fatigue, irritability, poor recovery, increased
injury risk. Within a month: muscle loss, weakened immune system, depression-like symptoms.
This is not a diet. This is starvation with extra steps.
```

### Step 2: Pre-Shift Meal

**Agent action**: Recommend a pre-shift meal based on user's shift time and available prep time.

```
PRE-SHIFT MEAL (2-3 hours before work)
Goal: Complex carbs + moderate protein + low-moderate fat. 600-900 calories.

EXAMPLES:
- 3 eggs scrambled + 2 slices toast + banana + glass of milk (~700 cal)
- Large bowl oatmeal with peanut butter (2 tbsp) + banana + protein shake (~800 cal)
- 2 PB&J sandwiches + apple (~750 cal)
- Rice and beans (2 cups) + cheese + tortilla (~800 cal)
- Large bowl pasta with meat sauce (leftover from meal prep) (~700 cal)

RULES:
- Don't skip this. Ever. Skipping the pre-shift meal is the single worst nutritional
  decision you can make for a physical job.
- Eat real food, not just coffee. Coffee is not breakfast.
- If you work at 5am and can't eat at 3am: eat a bigger dinner the night before and
  have a 300-calorie snack (banana + granola bar) on the drive in. Eat a real
  breakfast on first break.
```

### Step 3: On-Shift Fueling

**Agent action**: Build a portable food list tailored to user's job environment and break schedule.

```
ON-SHIFT FOOD (every 2-3 hours, 200-400 calories per snack)
These need to be portable, shelf-stable, and edible without utensils or refrigeration.

HIGH-CALORIE PORTABLE OPTIONS:
- Trail mix (nuts + dried fruit): ~170 cal per 1/4 cup. Dense, doesn't crush.
- Peanut butter wraps: Tortilla + 2 tbsp PB + banana. ~450 cal. Make morning of.
- Beef jerky: ~80 cal/oz. High protein. Doesn't spoil.
- Granola bars (Nature Valley, Clif, Kind): 190-250 cal each. Cheap in bulk.
- Cheese sticks or babybel: ~80 cal each. Survives a few hours without refrigeration.
- Bananas: ~105 cal. Natural packaging. Quick energy.
- Hard-boiled eggs: ~70 cal each. Prep a dozen on Sunday.
- PB&J sandwich: ~350 cal. Timeless for a reason.
- Leftover burritos (bean/rice/cheese): ~400 cal. Wrap in foil.

TARGET: 800-1,200 calories during the shift from snacks and breaks.

WHAT TO AVOID MID-SHIFT:
- Huge fast food meals: A 1,200-calorie burger-fries-shake combo hits you like
  a tranquilizer dart at 1pm. Blood rushes to your gut, energy crashes.
- Energy drinks as food replacement: They have zero calories and zero nutrition.
  They mask fatigue; they don't fix it.
```

### Step 4: Hydration Protocol

**Agent action**: Calculate hydration needs based on user's environment and exertion level.

```
HYDRATION RULES
- Baseline: 0.5 liter (16 oz) per hour of physical work in moderate conditions.
- Hot conditions (above 80F/27C): 0.75-1 liter per hour.
- Extreme heat (above 95F/35C): 1-1.5 liters per hour. Set a timer if you have to.
- Don't wait until you're thirsty. By the time you feel thirst, you're already
  1-2% dehydrated, which equals 10-20% performance loss.

WHEN WATER ISN'T ENOUGH — ELECTROLYTES:
- If you're sweating heavily for more than 2 hours, you need sodium and potassium,
  not just water.
- Signs you need electrolytes: muscle cramps, headache, dizziness, nausea, dark urine
  even though you're drinking water.
- WARNING — HYPONATREMIA: Drinking massive amounts of plain water without sodium
  replacement can be dangerous. Symptoms: confusion, nausea, seizures. This happens
  to people who chug water all day in heat without any salt.

ELECTROLYTE OPTIONS (cheapest to most expensive):
1. DIY electrolyte drink: 1 liter water + 1/4 tsp salt + 2 tbsp sugar + splash of
   lemon juice. Costs pennies. Tastes like bad Gatorade. Works perfectly.
2. Gatorade/Powerade: Fine for purpose. ~$1/bottle. High sugar but that's actually
   useful during heavy labor.
3. Pedialyte: Better electrolyte ratio than sports drinks. ~$5/liter.
4. Electrolyte packets (LMNT, Liquid IV, Drip Drop): $1-2/packet. Best ratio,
   most portable.

URINE COLOR CHECK:
- Pale yellow: Good hydration.
- Dark yellow/amber: You're behind. Drink now.
- Clear: You might be over-hydrating. Back off slightly and add electrolytes.
```

### Step 5: Post-Shift Recovery Meal

**Agent action**: Recommend recovery meal based on user's budget and available time.

```
POST-SHIFT MEAL (within 60 minutes of finishing work)
Goal: Protein + carbs for muscle repair and glycogen replenishment. 700-1,000 calories.

EXAMPLES:
- Chicken thighs (2) + rice (2 cups) + steamed broccoli (~850 cal)
- Large bowl of chili with bread (2 slices) (~800 cal)
- Pasta with meat sauce (large plate) + side salad (~900 cal)
- Stir-fry: rice + whatever protein and vegetables you have (~750 cal)
- Burrito bowls: rice, beans, ground beef, cheese, salsa (~900 cal)

THE 60-MINUTE WINDOW:
Your muscles absorb nutrients for repair most efficiently in the first hour after
hard physical work. Miss this window regularly and recovery takes significantly longer.
If you can't eat a full meal, at minimum get 20-30g protein (a shake, a can of tuna,
a cup of Greek yogurt) within that hour and eat the full meal when you can.

PROTEIN TARGET:
- Aim for 0.7-1g protein per pound of body weight per day.
- 180 lb worker = 125-180g protein/day.
- Spread it across meals. Your body can only use about 40g per meal for muscle repair.
```

### Step 6: Weather-Specific Adjustments

**Agent action**: Adjust caloric and hydration recommendations for user's climate and season.

```
HOT WEATHER (above 85F/30C): Increase calories 10-15%. Sodium replacement
non-negotiable. Cold foods (fruit, yogurt, sandwiches) are easier to eat.
Pre-cool with ice water before the shift.

COLD WEATHER (below 40F/4C): Increase calories 10-40%. Thermos of soup or
chili. Hydration still matters — you sweat under layers and lose moisture
breathing. Warm fluids maintain core temp.

HIGH ALTITUDE (above 5,000 feet): Increase water 50%. Increase carbs (body
preferentially burns them at altitude). Force yourself to eat on schedule —
appetite drops.
```

### Step 7: Budget Meal Prep ($40-60/Week)

**Agent action**: Build a weekly meal prep plan targeting 3,500 cal/day within user's budget.

```
WEEKLY MEAL PREP — 3,500 CAL/DAY, $40-60 BUDGET

SHOPPING LIST (feeds one person, 7 days):
- Rice, 10 lb bag: $8
- Dried beans (pinto or black), 4 lbs: $5
- Chicken thighs (bone-in, skin-on), 5 lbs: $8
- Ground beef (80/20), 3 lbs: $10
- Eggs, 2 dozen: $5
- Peanut butter, 28 oz jar: $4
- Bread, 2 loaves: $4
- Bananas, 2 bunches: $2
- Oats, 42 oz canister: $4
- Frozen vegetables, 3 bags: $5
- Cheese, 1 lb block: $4
- Total: ~$59

SUNDAY PREP (2-3 hours):
1. Cook 8 cups dry rice (makes ~16 cups cooked).
2. Cook 2 lbs dried beans (or use 4 cans for $4 more and skip soaking).
3. Bake all chicken thighs at 400F for 40 min. Shred half, leave half whole.
4. Brown all ground beef with onion and garlic. Season half as taco meat,
   half as pasta sauce base.
5. Hard-boil 1 dozen eggs.
6. Portion into containers: 5 lunch containers, 5 dinner containers.

DAILY BREAKDOWN:
- Breakfast (~800 cal): Oatmeal with PB + eggs + toast
- Lunch packed (~800 cal): Rice + beans + chicken or beef + cheese
- On-shift snacks (~600 cal): PB sandwiches, bananas, granola bars, trail mix
- Dinner (~900 cal): Protein + rice or pasta + vegetables
- Evening snack (~400 cal): PB toast, eggs, cheese, leftovers
```

### Step 8: Supplement Reality Check

**Agent action**: Address supplement questions honestly — what works, what's a waste of money.

```
SUPPLEMENTS — THE HONEST VERSION

WORTH IT:
- Creatine monohydrate: 5g/day. Improves strength and recovery. Decades of
  research. ~$15/month. No loading needed. Timing doesn't matter.
- Vitamin D: 2,000-4,000 IU/day. Most physical workers are deficient. Affects
  muscle function, mood, immune system, bone density. $5-10/month.

NOT WORTH IT: BCAAs (redundant if eating enough protein), pre-workout (just
caffeine), testosterone boosters (none work), joint supplements (weak evidence;
fish oil is slightly better at $10/month).

WASTE OF MONEY: Anything with "proprietary blend," anything promising rapid
gains, anything over $30/month.
```

### Step 9: Alcohol and Recovery

**Agent action**: Provide honest assessment of after-work drinking impact on physical recovery.

```
ALCOHOL AND PHYSICAL LABOR — REAL TALK
Not a temperance lecture. Biology.

- Impairs muscle protein synthesis 25-40% for 24 hours. Recovery takes longer.
- Disrupts sleep architecture even if you "sleep fine." Less deep sleep = more
  soreness tomorrow.
- Dehydration: Beer's fluid doesn't offset the fluid alcohol makes you lose.
- 6 beers = ~900 empty calories displacing actual recovery food.

NOT SAYING DON'T DRINK. SAYING: Match each drink with water. Eat recovery meal
before drinking. 2-3 max on work nights. If you're drinking nightly to cope with
exhaustion, see the blue-collar-mental-health skill.
```

## If This Fails

- Still exhausted after improving nutrition: Get bloodwork done. Iron deficiency, low vitamin D, and thyroid issues are common in physical workers and mimic "just tired from work." Ask your doctor to check ferritin (not just hemoglobin), vitamin D, and TSH.
- Can't eat enough volume: Add calorie-dense foods — nuts, nut butter, cheese, olive oil on everything, whole milk instead of water with meals. An extra 2 tablespoons of peanut butter is 190 calories with no extra volume.
- Budget is tighter than $40/week: Rice, beans, eggs, peanut butter, and bananas form a complete nutritional foundation for under $20/week. Not exciting, but it covers every macronutrient need.
- GI problems persist: Eating timing may be the issue (see shift-work-recovery for circadian meal timing). If problems continue, see a doctor — physical labor workers have higher rates of GERD and IBS.

## Rules

- Eat before you work. Not optional. Not negotiable.
- Hydrate proactively, not reactively. If you're thirsty, you're already behind.
- Protein at every meal. Your muscles are being broken down daily — they need material to rebuild.
- Electrolytes in heat. Plain water alone is not enough above 80F/27C for sustained work.
- Don't let anyone tell you that you need supplements to perform. Food first, always.
- Calorie restriction diets and physical labor don't mix. If you want to lose weight, adjust by 200-300 calories max, not the aggressive cuts marketed to desk workers.

## Tips

- A large insulated water bottle (64 oz / 2 liter) is the single best investment for on-site hydration. Fill it frozen the night before in summer — cold water all day. $15-25 (Igloo, Stanley, Yeti knockoff).
- Prep your snack bag the night before, same time you set your alarm. It takes 3 minutes and prevents the "grab nothing because I'm running late" scenario.
- If your job site has a microwave, a thermos of leftover rice and protein is a better lunch than anything from the gas station.
- Bananas are the perfect worksite food: self-packaged, high potassium (anti-cramp), quick energy, $0.25 each.
- Chocolate milk is a legitimate post-work recovery drink. Optimal carb-to-protein ratio. Cheap. Tastes good. Used by athletes for decades.
- If you're losing weight unintentionally on a physical job, you're undereating. That's not a compliment — it's a warning sign. Add 500 calories/day immediately.

## Agent State

```yaml
nutrition_session:
  job_type: null
  body_weight: null
  estimated_daily_calories: null
  climate_conditions: null
  budget_per_week: null
  current_eating_pattern: null
  hydration_assessed: false
  meal_prep_plan_generated: false
```

## Automation Triggers

```yaml
triggers:
  - name: heat_advisory_nutrition
    condition: "local temperature forecast exceeds 90F/32C"
    schedule: "daily_check_summer"
    action: "Remind user to increase fluid intake, add electrolytes, and pre-cool before shift"
  - name: meal_prep_reminder
    condition: "user has established weekly prep routine"
    schedule: "weekly_sunday_morning"
    action: "Remind user to do weekly meal prep and provide shopping list if budget has changed"
  - name: undereating_check
    condition: "user reports persistent fatigue, weight loss, or increased injury frequency"
    schedule: "on_demand"
    action: "Run caloric needs assessment and compare to reported intake. Flag deficit if present."
```
