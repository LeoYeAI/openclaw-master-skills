---
name: basic-plumbing-troubleshooting
description: >-
  Step-by-step plumbing fixes for common household problems without calling a plumber. Use when someone has a clogged sink or toilet, running toilet, dripping faucet, or minor leak and wants to fix it themselves.
metadata:
  category: skills
  tagline: >-
    Fix a clogged drain, running toilet, or minor leak yourself — clear instructions, no special tools, and a checklist for when to stop and call a pro
  display_name: "Basic Plumbing Troubleshooting"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/basic-plumbing-troubleshooting"
---

# Basic Plumbing Troubleshooting

A plumber call starts at $150-300 before they touch anything. Most common plumbing problems — clogged drains, running toilets, dripping faucets — cost under $20 in parts and 30-60 minutes to fix yourself. This skill teaches the systematic approach: diagnose first, then fix. And it gives you clear criteria for when the problem is beyond DIY and a professional is genuinely needed.

**DISCLAIMER**: Plumbing work beyond fixture repairs (anything involving supply lines, main pipes, gas lines, or structural work) requires permits and licensed tradespeople in most jurisdictions. When in doubt, call a plumber. Water damage from an incorrect repair costs far more than the repair itself.

## Sources & Verification

- This Old House plumbing guides (thisoldhouse.com) — verified active March 2026 — written and reviewed by licensed master plumbers
- Family Handyman DIY plumbing library (familyhandyman.com) — verified active March 2026
- International Plumbing Code (IPC) and Uniform Plumbing Code (UPC) — the model codes adopted by most US jurisdictions
- EPA WaterSense program (epa.gov/watersense) — running toilet data: a running toilet wastes 200 gallons per day
- Consumer Reports plumbing cost data, 2024: average plumber service call $175-350 before parts

## When to Use

- Sink, tub, or shower is draining slowly or not at all
- Toilet is clogged and won't flush
- Toilet keeps running after flushing
- A faucet is dripping constantly
- Water is pooling under a sink or around a toilet base
- User wants to know where the shut-off valves are before a real emergency
- Wants to know if their problem needs a plumber or can be DIY

## Instructions

### Step 1: Know your shut-offs before anything else

**Agent action**: Walk the user through locating their shut-off valves now, before any problem occurs. Save the locations in state so they're accessible in an emergency.

```
SHUT-OFF VALVES — FIND THESE BEFORE YOU NEED THEM:

FIXTURE SHUT-OFFS (under sinks and behind toilets):
  - Toilet: oval or football-shaped valve on the wall behind
    the toilet, near the floor. Turn clockwise to close.
  - Under-sink: two valves (hot and cold) on the supply lines
    under the cabinet. Turn clockwise to close.
  - Test these now — they can seize from disuse. If you can't
    turn one, spray with WD-40 and try again slowly.

MAIN WATER SHUT-OFF:
  House: usually near the water meter (front of house, near
    street), OR in the basement/utility room where the main
    line enters the house.
  Apartment: usually in a utility closet or behind a panel in
    your unit, OR in a shared utility room (ask building super
    for its location and get a photo).
  Turn clockwise (or use a water meter key for outdoor meters).

GAS — DO NOT TOUCH:
  Gas lines are NOT covered by this skill. If you smell gas,
  leave the building immediately and call 911 or your gas
  utility's emergency line.
```

### Step 2: Clogged sink or bathtub drain

Diagnose the clog before choosing a method.

**Agent action**: Ask where the clog is (kitchen vs bathroom sink vs tub) and whether it's completely blocked or just slow. Use the answer to route to the right sub-protocol.

```
DIAGNOSIS:
[ ] Single fixture slow/blocked: clog is in that fixture's trap
    or drain line. Start with the manual methods below.
[ ] Multiple fixtures slow: clog is downstream (main line).
    This likely needs a plumber's snake (or call a plumber).
[ ] Kitchen sink after garbage disposal use: likely grease
    or food buildup in the trap or P-trap.
```

**Method 1: Boiling water (kitchen sink only — NOT for toilets or PVC pipes that go to exterior)**
```
BOILING WATER METHOD:
Works for: grease clogs in kitchen sink only
Do NOT use for: toilets, bathroom hair clogs, or if your
  drain pipes are clearly plastic PVC (risk of joint damage)

1. Boil a full kettle of water.
2. Pour it slowly directly down the drain in 2-3 stages,
   waiting 30 seconds between each pour.
3. Run hot tap water to flush.
4. Repeat once if needed.
```

**Method 2: Baking soda and vinegar (chemical-free)**
```
BAKING SODA + VINEGAR METHOD:
Works for: light to moderate clogs
Tools needed: 1/2 cup baking soda, 1 cup white vinegar, kettle

1. Remove any drain cover.
2. Pour 1/2 cup baking soda directly into the drain.
3. Follow immediately with 1 cup white vinegar.
4. Cover the drain opening with a cloth or stopper
   (this forces the reaction into the clog, not back out).
5. Wait 15-20 minutes.
6. Flush with hot (not boiling) water.

Why not Drano/chemical drain cleaners:
  - They damage older pipes (especially cast iron and PVC)
  - They don't work on hair clogs (only dissolve grease)
  - If they fail, you now have a drain full of caustic liquid
    that's dangerous for a plumber to work in
  - They damage your pipes over time
```

**Method 3: Plunger (most effective for total blockages)**
```
SINK PLUNGER METHOD:
Tools: cup plunger (the flat-bottomed one — NOT the flange
  plunger used for toilets)

1. Remove the drain stopper if there is one
   (most pop out or unscrew counterclockwise).
2. Fill the sink with 2-3 inches of water
   (creates seal for suction).
3. Cover the overflow opening (the hole near the top rim
   of the sink) with a wet cloth and hold it in place.
4. Place plunger firmly over drain.
5. Pump 15-20 times with short, sharp strokes.
6. Pull the plunger up sharply on the final stroke to
   break the clog loose.
7. Run water to test. Repeat up to 3 times.
```

**Method 4: Remove and clean the P-trap (for complete blockages)**
```
P-TRAP REMOVAL:
Tools: bucket, channel-lock pliers (or by hand if plastic)

The P-trap is the curved pipe section under the sink.
Most blockages sit here.

1. Place a bucket under the P-trap.
2. Unscrew the slip-nut fittings on both sides of the
   P-trap (counterclockwise). Most are hand-tight on
   plastic pipes. Metal: use pliers with a cloth to
   protect the finish.
3. Pull the P-trap out. The water and clog will fall
   into your bucket.
4. Clear the clog (usually a compressed ball of hair,
   grease, and soap). Use a wire hanger to pull it out.
5. Rinse the P-trap.
6. Reattach. Hand-tight plus 1/4 turn with pliers.
7. Run water and check for leaks at both joints.
   A slow drip: tighten the slip-nut slightly.
```

### Step 3: Clogged toilet

**Agent action**: Ask if anything was flushed that shouldn't have been (wipes, paper towels, etc.). If yes, note this — it affects the approach.

```
TOILET CLOG RULES BEFORE STARTING:
[ ] Do NOT keep flushing if the bowl is full — you will
    overflow the toilet. One flush attempt, then stop.
[ ] If the bowl is at the rim: wait 5 minutes for water
    to drain before plunging. If it doesn't drain at all,
    the clog may be solid and need a snake.
[ ] Never use chemical drain cleaners in a toilet.
```

**Plunging a toilet:**
```
TOILET PLUNGER PROTOCOL:
Tools: flange plunger (the one with the rubber extension
  on the bottom — different from the flat sink plunger)

1. If needed, put on rubber gloves.
2. Add water to the bowl to cover the plunger head
   if the bowl is low.
3. Insert the flange plunger so the flange fits into
   the drain hole at the bottom of the bowl.
4. Start with a SLOW first push to remove air (sudden
   push will splash contaminated water on you).
5. Pump 15-20 times with firm, even strokes.
6. Pull up sharply on the final stroke.
7. Flush to test. Repeat up to 3 times.

WHAT WORKED: Great. Disinfect the plunger and toilet area.
STILL BLOCKED: Try a toilet auger (Step below).
```

**Toilet auger (drain snake) for stubborn clogs:**
```
TOILET AUGER USE:
Tools: toilet auger / closet auger (~$20-30 at hardware store)

1. Insert the curved end of the auger into the drain
   with the handle up.
2. Crank the handle clockwise while gently pushing
   the cable into the drain.
3. When you hit resistance, work back and forth
   while cranking to break up or hook the clog.
4. Pull the auger out slowly (it may bring the clog with it).
5. Flush to test.

CALL A PLUMBER IF:
[ ] Auger doesn't clear it after two attempts
[ ] Multiple toilets in the home are blocked simultaneously
    (main line clog — not a DIY fix)
[ ] Sewage is backing up into other fixtures when you flush
```

### Step 4: Running toilet

A running toilet wastes 200 gallons per day and adds $50-100/month to your water bill. In most cases it's a $5-15 parts fix.

**Agent action**: Walk the user through the diagnosis steps to identify which part is failing.

```
RUNNING TOILET DIAGNOSIS:

1. Lift the tank lid and set it safely aside.
2. Listen and look. The most common causes:

   CAUSE A: FLAPPER VALVE LEAKING (most common — 70% of cases)
   Signs: you can hear water trickling into the bowl
     even when the toilet isn't running.
   Test: add a few drops of food coloring to the tank.
     Wait 15 minutes without flushing.
     Color appears in the bowl? The flapper is leaking.

   CAUSE B: FLOAT SET TOO HIGH
   Signs: water is running into the overflow tube
     (the tall open tube in the center of the tank).
   Test: watch the water level. If water runs into
     that tube, the float is set too high.

   CAUSE C: FILL VALVE WORN OUT
   Signs: toilet fills correctly but then keeps
     intermittently refilling every few minutes even
     with no flushes.
```

**Fix A: Replace the flapper (20 minutes, $5-10 part)**
```
FLAPPER REPLACEMENT:

1. Turn off water at the toilet shut-off valve
   (behind and below the toilet, clockwise).
2. Flush to empty the tank.
3. Remove the old flapper:
   - Unhook the two side ears from the overflow tube pegs
   - Unhook the chain from the flush handle arm
4. Take the old flapper to the hardware store to match it,
   OR buy a "universal" flapper (Korky or Fluidmaster brand).
5. Attach new flapper: hook ears onto pegs, clip chain
   with 1/2 inch of slack (not too tight or it won't seal).
6. Turn water back on. Let tank fill.
7. Flush and watch: the flapper should drop and seat firmly.
8. Redo the food coloring test to confirm the fix.
```

**Fix B: Adjust the float (5 minutes, no parts)**
```
FLOAT ADJUSTMENT:

Ball float (older — round ball on an arm):
  Bend the arm gently downward. This lowers the shutoff
  point. Water should stop 1 inch below the overflow tube.

Cup float (modern — cylinder that slides on the fill valve):
  Pinch the clip on the side of the float and slide it
  downward. Or turn the adjustment screw on top of the
  fill valve counterclockwise to lower the water level.

Target: water sits 1 inch below the top of the overflow tube.
```

### Step 5: Identify and contain a minor leak

**Agent action**: Ask the user to describe exactly where water is appearing. Help them distinguish between a supply line leak, a drain leak, and condensation (common misdiagnosis).

```
LEAK IDENTIFICATION:

Under-sink supply line drip:
  - Water near the shut-off valves or the lines
    running up to the faucet
  - Fix: tighten the connection nut (clockwise, 1/4 turn
    with pliers at a time). If tightening doesn't stop it,
    the supply line needs replacement (~$10-15 at hardware).
    Shut off the fixture valve first.

Under-sink drain drip:
  - Water appears after using the sink, from the P-trap
    or drain connections
  - Fix: tighten the slip-nuts. If cracked plastic:
    replace the P-trap ($5-10).

Toilet base leak:
  - Water appears at the base of the toilet after flushing
  - Cause: the wax ring seal has failed
  - Fix: toilet must be removed and re-set on a new wax ring.
    This is a 1-2 hour DIY job but requires confidence.
    If unsure, call a plumber — water damage under the
    sub-floor is expensive.

Condensation (often mistaken for a leak):
  - Cold-water pipes "sweat" in humid weather
  - Test: dry the pipe and wrap it in dry paper towel for
    1 hour. Paper is wet but pipe connection is dry?
    That's condensation, not a leak.
    Solution: pipe insulation foam ($3-5 at hardware store).

CALL A PLUMBER IMMEDIATELY IF:
[ ] Water is coming from inside a wall
[ ] The ceiling is staining from above
[ ] You hear water running but all fixtures are off
    (possible hidden leak or running meter)
[ ] Water shows near an electrical panel or outlet
    (water + electricity = emergency)
```

## If This Fails

1. **Drain still clogged after all methods**: A plumber's motorized snake (auger) can clear blockages 50+ feet into the drain line. Cost: $150-250. Worth it for a main line clog.
2. **Running toilet fix not working**: The fill valve assembly may need full replacement ($10-15 part, 30 min). Search your toilet's model number plus "fill valve replacement" for a specific video guide. Or call a plumber.
3. **Shut-off valve won't close**: If a fixture shut-off valve is seized and you can't turn it, turn off the main water supply immediately. Then have a plumber replace the shut-off valve — a failed valve during a repair can cause a flood.
4. **Apartment building plumbing**: For any shared-stack issue or if your shut-off doesn't actually stop the water, call building management immediately. They are responsible for supply lines above your unit's shut-offs in most lease agreements.
5. **No money for a plumber right now**: Community Action Agencies in most counties have emergency home repair funds for low-income households. Search "community action agency" plus your county at communityactionpartnership.com — verified active March 2026.

## Rules

- Never advise touching gas lines, even adjacent to plumbing work — always route gas questions to a licensed plumber or gas technician
- Always recommend turning off the water supply before any repair, even minor ones
- Main line clogs (multiple fixtures backing up) are not DIY — always route these to a plumber
- Water near electrical components is an emergency, not a plumbing tutorial — call an electrician

## Tips

- The most common DIY mistake is overtightening. Plastic plumbing fittings crack if over-torqued. Hand-tight plus 1/4 turn with tools is the standard.
- WD-40 is not a lubricant for plumbing use — it evaporates. Use plumber's grease (silicone-based) for faucet O-rings and Teflon tape for threaded connections.
- A running toilet is the single most cost-effective plumbing fix. A $10 flapper replacing the one that's leaking pays for itself in under a week on most water bills.
- Chemical drain cleaners (Drano, etc.) are a short-term fix that creates a long-term problem. They corrode pipes from the inside and create hazardous conditions for anyone working in that drain later. Skip them.

## Agent State

Persist across sessions:

```yaml
plumbing:
  known_shutoffs:
    main_location: null
    toilet_shutoffs: []
    sink_shutoffs: []
    noted_date: null
  active_issue:
    type: null           # clog | running_toilet | leak | drip
    location: null
    diagnosed: false
    methods_tried: []
    resolved: false
    resolution_date: null
    plumber_needed: false
  repair_history: []
```

## Automation Triggers

```yaml
triggers:
  - name: leak_followup
    condition: "active_issue.type == 'leak' AND active_issue.resolved == false"
    schedule: "24 hours after issue logged"
    action: "Checking in on your leak. Is it contained? Has the area dried out? If water is still appearing or you see any new staining, it is time to call a plumber."

  - name: running_toilet_cost_note
    condition: "active_issue.type == 'running_toilet'"
    action: "A running toilet wastes about 200 gallons per day — that is roughly $2-4 in water costs daily depending on your rates. A $10 flapper fix pays for itself in 3-5 days."

  - name: shutoff_reminder
    condition: "known_shutoffs.main_location == null"
    action: "Quick preparedness task: Do you know where your main water shut-off is? Finding it now takes 5 minutes and can save thousands in water damage if a pipe bursts. Want me to walk you through locating it?"
```
