---
name: fire-skills
description: >-
  Practical fire building, management, and safety skills. Use when someone needs to build a campfire, use a fireplace safely, learn to grill, or needs fire emergency response guidance.
metadata:
  category: skills
  tagline: >-
    Build a campfire, use a fireplace, grill safely, and know what to do when something catches fire — the oldest human technology, properly handled.
  display_name: "Fire Skills"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/fire-skills"
---

# Fire Skills

Humans have used fire for at least 400,000 years. It's arguably the foundational technology — cooking, warmth, light, protection. And yet most adults in 2026 can't build a reliable campfire, don't know what their fireplace damper does, and would panic if a grease fire erupted on their stove. This skill covers the practical fire knowledge you actually need: how to build and maintain fires for recreation and warmth, how to grill without poisoning anyone, and critically, how to respond when fire becomes an emergency instead of a tool.

```agent-adaptation
# Localization note — fire regulations and emergency systems vary by region
- Burn bans, open-fire regulations, and fire danger rating systems are
  jurisdiction-specific. Detect user location and swap:
  US: Local fire department non-emergency line, NFPA guidelines, fire danger
      rating from NIFC (National Interagency Fire Center)
  UK: Fire and Rescue Service, Gov.uk fire safety guidance
  Australia: CFA/RFS fire danger ratings, total fire ban systems
  Canada: Provincial fire bans, FireSmart program
  EU: Country-specific fire brigade numbers and regulations
- Emergency number: US 911, UK 999, AU 000, EU 112
- Grilling customs and equipment vary — charcoal/gas ratios differ by country.
  Adapt fuel types to what's locally available.
- Firewood species references are North American. Swap for local hardwood/
  softwood equivalents.
```

## Sources & Verification

- **National Fire Protection Association (NFPA)** -- Home fire safety data, extinguisher guidelines, escape planning. https://www.nfpa.org/
- **US Forest Service** -- Campfire safety and wildfire prevention. https://www.fs.usda.gov/visit/know-before-you-go/campfire-safety
- **American Red Cross** -- Home fire safety and prevention resources. https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/fire.html
- **NFPA fire extinguisher classifications** -- Class A/B/C/K descriptions and usage. https://www.nfpa.org/education-and-research/home/fire-extinguishers
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User wants to build a campfire and doesn't know where to start
- User has a fireplace and isn't sure how to operate it safely
- User is learning to grill (charcoal or gas) and wants safety basics
- User had a kitchen fire or small fire and wants to know what to do
- User wants to know which fire extinguisher to buy for their home
- User needs to create a home fire escape plan
- User is going camping and wants fire safety basics
- User asks about smoke detector placement or maintenance

## Instructions

### Step 1: Determine what kind of fire knowledge the user needs

**Agent action**: Ask the user which situation applies. Route to the relevant section.

```
FIRE SKILL CATEGORIES:

A. CAMPFIRE BUILDING -- How to build, maintain, and extinguish a campfire
B. FIREPLACE OPERATION -- Using an indoor fireplace safely
C. GRILLING BASICS -- Charcoal and gas grill safety and technique
D. FIRE EXTINGUISHER KNOWLEDGE -- Types, placement, and use
E. KITCHEN FIRE RESPONSE -- What to do when cooking goes wrong
F. HOME FIRE SAFETY -- Escape plans, smoke detectors, prevention
```

### Step 2: Campfire building

**Agent action**: Walk the user through fire building from scratch.

```
BEFORE YOU START:
- Check for burn bans. Call the local ranger station or check
  the fire agency website for your area. Fines run $500-$5,000+.
- Use an existing fire ring if one exists. Never build on bare
  ground in the backcountry unless it's an emergency.
- Clear a 10-foot radius of leaves, pine needles, and dry debris.
- Have water or a shovel within arm's reach before you light anything.
- Wind check: if sustained winds exceed 15 mph, don't build a fire.

MATERIALS YOU NEED (gather before you start):
1. Tinder -- dry, fine material that catches from a spark or match
   Examples: dryer lint (bring from home), cotton balls with petroleum
   jelly, dry grass, birch bark shavings, newspaper
   Amount: two handfuls minimum

2. Kindling -- small sticks, pencil-thickness or thinner
   Must snap cleanly (if it bends, it's too wet)
   Amount: two armfuls

3. Fuel wood -- wrist-thickness to arm-thickness logs
   Hardwood (oak, maple, hickory) burns longer and hotter
   Softwood (pine, fir, cedar) lights easier but burns fast and sparks
   Amount: enough for your planned burn time, plus extra

NEVER BURN: treated/painted wood, plywood, trash, plastic, poison ivy/oak
```

```
TEEPEE METHOD (best for beginners):
1. Place a tinder bundle in the center of your fire ring.
2. Lean kindling sticks against each other over the tinder,
   forming a cone shape (like a teepee). Leave a gap on the
   windward side for airflow and lighting access.
3. Light the tinder at the base from the windward side.
4. As kindling catches, add more kindling — don't smother it.
5. Once kindling is burning steadily (3-5 minutes), lean
   small fuel wood against the structure.
6. Gradually increase wood size as the fire establishes.
7. A good fire takes 15-20 minutes to fully establish.

LOG CABIN METHOD (best for cooking, longer burn):
1. Place tinder in the center.
2. Lay two parallel sticks on either side of the tinder.
3. Lay two more sticks perpendicular on top, forming a square.
4. Repeat, building up 3-4 layers, decreasing size as you go.
5. Fill the center cavity with kindling.
6. Light from the bottom center.
7. This structure creates excellent airflow and collapses into
   a flat coal bed — ideal for cooking.

MAINTAINING YOUR FIRE:
- Add wood before the fire gets low, not after it's almost out.
- Feed from the upwind side.
- Blow gently at the base if it needs oxygen — not at the flames.
- For cooking: let it burn down to coals. Flames = soot on food.

EXTINGUISHING (do this EVERY time):
1. Stop adding wood 30-45 minutes before you want to leave.
2. Spread coals out with a stick (don't pile them).
3. Pour water slowly and steadily — it will hiss and steam.
4. Stir the wet ashes with a stick, exposing hidden embers.
5. Pour more water. Stir again.
6. Touch the ashes with the back of your hand (carefully).
   If warm, repeat steps 3-5.
7. "If it's too hot to touch, it's too hot to leave."
```

### Step 3: Fireplace operation

**Agent action**: Walk the user through safe indoor fireplace use.

```
BEFORE YOUR FIRST FIRE OF THE SEASON:
- Get the chimney inspected annually. Creosote buildup causes
  chimney fires. Cost: $150-$300 for inspection and cleaning.
- Check the damper: open it fully. Look up — you should see daylight
  or the flue liner. If you see blockage, stop and call a sweep.
- Check for birds' nests or debris (common after summer).
- Make sure smoke detectors and CO detectors are working.

OPERATING THE FIREPLACE:
1. Open the damper FULLY before lighting anything.
2. Prime the flue: hold a rolled newspaper (lit) up near the
   damper opening for 30 seconds. This warms the air in the
   flue and establishes draft. Skip this and smoke fills the room.
3. Build a small fire first (tinder + kindling only).
4. Once draft is established, add 2-3 logs. Don't overload.
5. Use a fireplace screen or glass doors to contain sparks.
6. Never leave a fire unattended. Period.
7. Don't close the damper until ashes are COMPLETELY cold (24+ hours).

WHAT NEVER GOES IN A FIREPLACE:
- Treated, painted, or stained wood
- Cardboard (fine for starting, but not as primary fuel)
- Christmas trees (explosive — resin ignites violently)
- Trash, plastic, or wrapping paper
- Accelerants (lighter fluid, gasoline, kerosene)
- Duraflame-type logs + real wood at the same time

CREOSOTE: THE HIDDEN DANGER:
- Creosote is a tar-like residue that builds up inside chimneys.
- It's flammable. Enough buildup = chimney fire.
- Burns hot enough to crack chimney liners and ignite walls.
- Minimized by: burning dry/seasoned wood, maintaining hot fires
  (not smoldering), ensuring good airflow.
- Annual cleaning is not optional.
```

### Step 4: Grilling basics

**Agent action**: Cover charcoal and gas grill safety and technique.

```
CHARCOAL GRILLING:
Setup:
1. Use a chimney starter — it's a $15 metal cylinder. Fill with
   charcoal, stuff newspaper underneath, light the newspaper.
   Ready in 15-20 minutes when top coals are ashed over (gray).
2. NEVER use lighter fluid. Petroleum taste, dangerous flare-ups.
3. Pour coals into grill. For two-zone cooking: pile coals on one
   side (direct heat) and leave the other side empty (indirect heat).
4. Let grate heat for 5 minutes, then clean with a wire brush.
5. Oil the grate: fold a paper towel, dip in vegetable oil,
   hold with tongs and rub across grate.

Temperature guide (hold your hand 5 inches above the grate):
- High (450-550F): 2-3 seconds before pulling away
- Medium (350-450F): 4-5 seconds
- Low (250-350F): 7-8 seconds

GAS GRILLING:
Safety checks before every use:
1. Check gas hose for cracks, brittleness, or leaks.
   Leak test: spray soapy water on connections. Bubbles = leak.
2. Open the lid BEFORE turning on gas. Gas pooling under a
   closed lid + ignition = fireball.
3. If it doesn't ignite within 5 seconds, turn gas off, open lid,
   wait 5 minutes for gas to dissipate, try again.

FOOD SAFETY ON THE GRILL:
- Chicken: 165F internal, no exceptions
- Burgers: 160F internal (ground beef must be fully cooked)
- Steak: 145F for medium-rare (whole cuts are safer rare than ground)
- Pork: 145F internal + 3-minute rest
- Use a meat thermometer. Color is not a reliable indicator.
- Never put cooked meat back on the plate that held raw meat.

AFTER GRILLING:
- Charcoal: Close all vents. Let ash cool 48 hours before disposal.
  Dump in a metal container, never plastic or cardboard.
- Gas: Turn off burners, then turn off the tank. In that order.
- Never store a propane tank indoors or in a car trunk.
```

### Step 5: Fire extinguisher knowledge

**Agent action**: Explain extinguisher types and placement.

```
FIRE EXTINGUISHER CLASSES:

Class A -- Ordinary combustibles (wood, paper, cloth, trash)
Class B -- Flammable liquids (gasoline, grease, oil, paint)
Class C -- Electrical equipment (wiring, outlets, appliances)
Class K -- Kitchen fires (cooking oils, animal fats — commercial
           kitchens mainly, but good to know)

WHAT TO BUY FOR YOUR HOME:
- Kitchen: 5-lb ABC-rated extinguisher (covers A, B, and C)
  Cost: $25-$50 at any hardware store.
  Placement: mounted on wall near kitchen exit, NOT next to the stove
  (you need to reach it while backing away from a fire, not reaching
  through flames).
- Garage/workshop: Second ABC extinguisher.
- Each floor of the home: consider one per floor.
- Car: small 2-lb ABC extinguisher. $15-$20.

HOW TO USE (P.A.S.S.):
P -- Pull the pin
A -- Aim at the BASE of the fire (not the flames)
S -- Squeeze the handle
S -- Sweep side to side at the base

CRITICAL NOTES:
- A home extinguisher gives you about 8-10 seconds of spray.
- Stand 6-8 feet back.
- If the fire is bigger than a wastebasket, GET OUT. Call 911.
- After ANY extinguisher use, the fire department should still
  be called to check for hidden fire in walls or ceilings.
- Check the pressure gauge monthly. Replace or recharge if the
  needle is in the red zone.
- Replace every 10-12 years even if unused.
```

### Step 6: Kitchen fire response

**Agent action**: Cover the most common home fire emergencies.

```
GREASE FIRE (the most dangerous common kitchen fire):

NEVER WATER. NEVER. Water on a grease fire causes an explosive
fireball. This is the single most important fire fact to know.

WHAT TO DO:
1. Turn off the heat source (if you can reach the knob safely).
2. Cover the pan with a metal lid or cookie sheet. Slide it on
   from the side — don't drop it from above.
3. Leave the lid on. Do not peek. Fire needs oxygen.
4. If no lid available: dump baking soda on it (lots of it).
   NOT baking powder. NOT flour (flour is explosive).
5. If it's beyond a single pan: use your extinguisher (Class B).
6. If it's beyond your extinguisher: GET OUT. Close the kitchen
   door behind you. Call 911.

OVEN FIRE:
1. Keep the door closed.
2. Turn off the oven.
3. The fire will self-extinguish without oxygen.
4. Don't open the door to check — that feeds it air.

MICROWAVE FIRE:
1. Keep the door closed.
2. Turn off or unplug the microwave.
3. Wait for it to self-extinguish.
4. If smoke is pouring out, use an extinguisher and call 911.
```

### Step 7: Home fire safety plan

**Agent action**: Help the user create an escape plan and prevention checklist.

```
HOME FIRE ESCAPE PLAN:
1. Draw a floor plan of every level of your home.
2. Mark two exits from every room (usually a door and a window).
3. Make sure windows actually open. Test them.
4. Designate a meeting point outside (mailbox, specific tree, etc.).
5. Practice at night — most fatal fires happen while people sleep.
6. Practice with eyes closed or in the dark.
7. If you have kids, do it twice a year. Make it routine.
8. If you have elderly or mobility-limited family members, assign
   someone to help them. Have a backup assigner.

SMOKE DETECTOR PROTOCOL:
- One in every bedroom
- One outside every sleeping area
- One on every floor, including the basement
- Test monthly (press the test button)
- Replace batteries every 6 months (daylight saving time changes
  are a good reminder)
- Replace the entire unit every 10 years (check the manufacture
  date on the back)
- Interconnected detectors (when one sounds, all sound) are far
  safer. Cost: $25-$40 each, hardwired or wireless.

CARBON MONOXIDE DETECTORS:
- Required on every floor if you have gas appliances, a fireplace,
  or an attached garage.
- Replace every 5-7 years.
- CO is odorless and colorless. You won't know without a detector.
```

```
SEASONAL FIRE SAFETY CHECKLIST:

FALL:
[ ] Chimney inspection and cleaning ($150-$300)
[ ] Test all smoke and CO detectors
[ ] Replace batteries in all detectors
[ ] Check fireplace damper operation
[ ] Clear dry leaves from gutters and within 5 feet of house
[ ] Inspect space heaters — 3-foot clearance rule from anything
    flammable

SPRING:
[ ] Replace detector batteries again
[ ] Check fire extinguisher pressure gauges
[ ] Inspect grill for gas leaks, hose condition, spider webs
    in burner tubes (common cause of gas grill fires)
[ ] Clean dryer vent — lint buildup is a leading cause of home
    fires. Cost for professional cleaning: $100-$200.

YEAR-ROUND:
[ ] Never leave cooking unattended (leading cause of home fires)
[ ] 3-foot rule: keep anything flammable 3 feet from heat sources
[ ] Unplug space heaters when leaving the room or sleeping
[ ] Don't overload outlets or extension cords
[ ] Candles: extinguish when leaving the room. Use holders on
    stable, heat-resistant surfaces.

IF YOUR CLOTHES CATCH FIRE:
Stop. Drop. Roll. It actually works. Proven to be the most
effective response. Do NOT run — running fans the flames.
Cover your face with your hands while rolling.
```

## If This Fails

- If a fire is larger than a wastebasket or beyond a single pan, stop trying to fight it. Get everyone out and call 911.
- If you can't get a campfire started after 15 minutes, your materials are wet. Look for dead standing wood (off the ground) or use commercial fire starters brought from home.
- If your fireplace smokes into the room every time, the flue may be undersized, the damper may be damaged, or your house may have negative pressure issues. Call a certified chimney sweep (CSIA certified).
- If your fire extinguisher won't discharge, it's likely depressurized. Leave immediately and call 911.
- If someone has a burn: cool running water for 10-20 minutes. No ice, no butter, no toothpaste. Cover loosely with a clean cloth. Seek medical attention for burns larger than 3 inches, on the face/hands/feet/groin, or blistering burns.

## Rules

- Never leave any fire unattended — campfire, fireplace, grill, or candle
- Always have a suppression method within reach before starting a fire (water, extinguisher, dirt, lid)
- Never use gasoline, lighter fluid, or any accelerant on an established fire
- Grease fires and water do not mix — this overrides any instinct to throw water on flames
- Smoke detectors are non-negotiable in every sleeping area and on every floor
- When in doubt about whether you can handle a fire, get out and call for help. Property is replaceable.

## Tips

- Dryer lint is the best free fire starter in the world. Keep a ziplock of it in your camping gear.
- Cotton balls smeared with petroleum jelly light instantly and burn for 3-4 minutes. Cost: basically nothing.
- Seasoned firewood has been dried for 6+ months. It's lighter than green wood, sounds hollow when you knock two pieces together, and has cracks on the end grain. Wet wood = smoke, no heat, and creosote.
- A chimney starter pays for itself immediately by eliminating lighter fluid forever. Weber brand is the standard — $15 at any hardware store.
- The "back of the hand" test is the real standard for whether a campfire is out. If the ashes are warm to the back of your hand, they can still restart.
- Kitchen fires double between Thanksgiving and New Year's. Stay in the kitchen when frying or broiling.

## Agent State

```yaml
fire_skills:
  user_context:
    primary_need: null
    has_fireplace: null
    has_grill: null
    grill_type: null
    goes_camping: null
  safety_audit:
    smoke_detectors_tested: false
    co_detectors_present: false
    fire_extinguisher_locations: []
    extinguisher_pressure_checked: false
    escape_plan_created: false
    escape_plan_practiced: false
    chimney_last_inspected: null
    dryer_vent_last_cleaned: null
  skills_covered:
    campfire_building: false
    fireplace_operation: false
    grilling_basics: false
    extinguisher_knowledge: false
    kitchen_fire_response: false
    fire_escape_plan: false
  follow_up:
    seasonal_checklist_date: null
    next_detector_battery_change: null
```

## Automation Triggers

```yaml
triggers:
  - name: seasonal_fall_reminder
    condition: "month IS October AND fire_skills.safety_audit.chimney_last_inspected older than 12 months"
    schedule: "annually in October"
    action: "It's fall — time for your annual chimney inspection and smoke detector battery replacement. Want to walk through the seasonal fire safety checklist?"

  - name: grilling_season_check
    condition: "month IS April OR month IS May AND fire_skills.user_context.has_grill IS true"
    schedule: "annually in spring"
    action: "Grilling season is starting. Before your first cookout, check your grill's gas hose for cracks and do a soapy water leak test on all connections. Also check for spider webs in the burner tubes — it's a common and dangerous issue after winter storage."

  - name: detector_battery_reminder
    condition: "fire_skills.safety_audit.smoke_detectors_tested IS true AND days_since(fire_skills.follow_up.next_detector_battery_change) >= 0"
    schedule: "every 6 months"
    action: "Time to replace batteries in all smoke and CO detectors. Test each one after replacing. A detector with a dead battery is the same as no detector."

  - name: escape_plan_practice
    condition: "fire_skills.safety_audit.escape_plan_created IS true AND fire_skills.safety_audit.escape_plan_practiced IS false"
    action: "You've created a fire escape plan but haven't practiced it yet. Practice is what makes it work in a real emergency — especially for kids. Try a nighttime drill this week."

  - name: extinguisher_expiry_check
    condition: "fire_skills.safety_audit.fire_extinguisher_locations IS NOT EMPTY"
    schedule: "monthly"
    action: "Monthly reminder: check the pressure gauge on your fire extinguishers. If the needle is in the red zone, replace or recharge it immediately."
```
