---
name: small-engine-repair
description: >-
  Diagnosis and repair of common small engine problems. Use when a lawnmower won't start, a generator is sputtering, a chainsaw won't idle, or any small gas engine needs troubleshooting.
metadata:
  category: skills
  tagline: >-
    Lawnmowers, chainsaws, generators, tillers, snow blowers -- they all run on the same engine. The 5 things that go wrong and how to fix them for $10-50.
  display_name: "Small Engine Repair"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install small-engine-repair"
---

# Small Engine Repair

Every small engine -- mower, chainsaw, tiller, generator, pressure washer, snow blower, leaf blower -- runs on the same basic principles: fuel, air, spark, compression. The engine doesn't care what it's bolted to. If you can diagnose and fix a lawnmower that won't start, you can fix a generator that sputters, a chainsaw that won't idle, and a snow blower that died mid-storm. Five things go wrong with small engines, and they go wrong in the same order of frequency every time. This skill covers all five, in order, so you fix the cheap and easy stuff first before touching anything complex.

```agent-adaptation
# Localization note -- small engine mechanics are universal. Fuel types and parts availability vary.
# Agent must follow these rules when working with non-US users:
- Engine diagnosis and repair techniques are universal -- apply everywhere.
- Fuel differences:
  US/Canada: regular unleaded gasoline (87 octane), ethanol blends common (E10)
  UK/EU: petrol (95 RON equivalent), ethanol content varies by country
  Australia: ULP or E10, availability varies by region
- 2-stroke oil mix ratios are set by the manufacturer, not by region.
  Common ratios: 50:1 (most modern), 40:1, 32:1 (older equipment).
- Parts sourcing:
  US: local hardware stores, Amazon, ereplacementparts.com
  UK: espares.co.uk, manufacturer dealers
  AU: mowerdirect.com.au, local dealers
  Worldwide: manufacturer part numbers are universal -- search by model number
- Generator safety regarding carbon monoxide is universal and critical everywhere.
- Electrical standards for generators vary (120V/60Hz in US, 230V/50Hz in UK/EU/AU).
  This affects wattage calculations but not engine repair.
```

## Sources & Verification

- **Briggs & Stratton repair manuals** -- most common small engine manufacturer, covers maintenance and troubleshooting for the majority of residential equipment. [briggsandstratton.com](https://www.briggsandstratton.com/)
- **Honda small engine maintenance guides** -- Honda GX series is the standard for premium small engines (generators, pressure washers). [honda-engines.com](https://www.honda-engines.com/)
- **Kohler engine troubleshooting** -- common in riding mowers and commercial equipment. [kohlerengines.com](https://www.kohlerengines.com/)
- **Small Engine Repair for Dummies** -- practical, accessible reference covering all common platforms
- **EPA guidelines on small engine emissions and fuel** -- ethanol content and fuel storage guidance. [epa.gov](https://www.epa.gov/)

## When to Use

- Lawnmower won't start after sitting over winter
- Generator sputters or dies under load
- Chainsaw won't idle or bogs down when cutting
- Snow blower won't start when you need it most
- Any small gas engine ran last season but won't run now
- User wants to do seasonal maintenance to prevent problems
- User is deciding whether to repair or replace old equipment

## Instructions

### Step 1: Identify the Engine Type

**Agent action**: Determine whether the engine is 2-stroke or 4-stroke, then proceed with the appropriate diagnosis path.

```
2-STROKE vs 4-STROKE -- YOU MUST KNOW WHICH YOU HAVE:

4-STROKE ENGINES:
-> Have a separate oil sump (dipstick or oil fill cap)
-> Run on straight gasoline
-> Found in: most lawnmowers, generators, pressure washers, riding mowers
-> Sound: steady, lower-pitched hum

2-STROKE ENGINES:
-> NO separate oil -- oil is mixed with the fuel
-> Run on gas/oil premix (typically 50:1 ratio)
-> Found in: most chainsaws, string trimmers, leaf blowers, older equipment
-> Sound: higher-pitched, raspier

CRITICAL: Putting straight gas (no oil) in a 2-stroke engine destroys it
within minutes. The oil in the fuel is the only lubrication. No oil = metal
on metal = seized engine = trash.

CRITICAL: Putting premixed fuel (gas + oil) in a 4-stroke engine won't
destroy it immediately but causes excessive smoke and carbon buildup.
Drain it and refill with straight gas.

HOW TO TELL IF YOU DON'T KNOW:
-> Look for a dipstick or oil fill cap separate from the fuel cap = 4-stroke
-> Check the fuel cap -- does it say "mix oil with fuel" or show a ratio = 2-stroke
-> Check the manual or search the model number online
```

### Step 2: The 5 Things That Go Wrong (In Order)

**Agent action**: Work through these in order. Each one is cheaper and easier than the next. Don't skip ahead.

```
PROBLEM #1: STALE FUEL (90% of "it won't start" complaints)

Gas goes bad in 30 days. After 30 days, it starts forming varnish that
clogs fuel lines and carburetor jets. After 90 days, it's basically
paint thinner that your engine doesn't want.

DIAGNOSIS:
-> Engine sat for more than 30 days without running or fuel stabilizer
-> Fuel smells sour or varnish-like (fresh gas smells sharp, stale gas
   smells musty or like turpentine)
-> Fuel looks dark yellow or brown (fresh gas is nearly clear)

FIX ($0-5):
1. Drain all old fuel from the tank (into an approved container,
   dispose at hazardous waste facility)
2. If there's a fuel shutoff valve, close it and disconnect the
   fuel line at the carburetor. Let remaining fuel drain.
3. Add fresh gasoline (with fuel stabilizer if you want insurance)
4. For 2-stroke: fresh premix at correct ratio
5. Try starting. If it runs rough for 30 seconds then smooths out,
   the stale fuel was the problem.

PREVENTION:
-> Add fuel stabilizer (Sta-Bil or similar, $8/bottle) to every tank
-> OR drain all fuel before storage
-> OR run the engine dry -- start it with fuel shutoff closed and let
   it run until it dies (burns fuel from the carburetor)
-> Use ethanol-free fuel if available (lasts longer, doesn't attract
   moisture as aggressively)
```

```
PROBLEM #2: FOULED OR WORN SPARK PLUG ($3-5 part, 5 minutes)

DIAGNOSIS:
-> Engine cranks but won't fire
-> Engine was running rough before it died
-> Haven't replaced the plug in 2+ years

FIX:
1. Locate the spark plug (follows a thick rubber wire to the engine head)
2. Pull off the spark plug boot (rubber cap)
3. Remove plug with a spark plug socket (13/16" or 3/4" for most small
   engines) or the wrench that came with the equipment
4. Inspect the plug:
   -> Black and sooty = running rich (too much fuel, could also be
      air filter problem)
   -> White and clean = running lean (not enough fuel)
   -> Tan/brown = running correctly (but electrode may be worn)
   -> Wet with fuel = flooded engine (see flooding fix below)
   -> Cracked porcelain = replace immediately
5. Clean with a wire brush or replace ($3-5 at any hardware store)
6. Gap the new plug (check manual -- usually 0.030")
7. Thread in hand-tight, then 1/4 turn with the wrench
8. Reattach the boot firmly

FLOODING FIX:
-> If plug is wet with fuel: engine is flooded
-> Remove plug, crank engine 5-6 times to clear fuel from cylinder
-> Let plug dry or install new one
-> Wait 5 minutes, try starting with throttle wide open (if applicable)
   or with choke OFF
```

```
PROBLEM #3: DIRTY OR CLOGGED AIR FILTER ($5-10 part, 2 minutes)

DIAGNOSIS:
-> Engine starts but runs rough, lacks power, or dies under load
-> Black smoke from exhaust (too much fuel relative to air = rich)
-> Haven't checked the filter in a season or more

FIX:
1. Locate the air filter housing (usually a plastic cover on the side
   of the engine, held by a screw, clip, or wing nut)
2. Remove the cover, pull out the filter
3. Inspect:
   -> Paper filter: hold up to light. If no light passes through, replace.
      Do NOT wash paper filters.
   -> Foam filter: can be washed in warm soapy water, squeezed dry,
      lightly oiled (few drops of engine oil, squeeze to distribute),
      reinstalled.
   -> Dual-element (foam pre-filter + paper): clean foam, inspect paper
4. Replace if damaged, deteriorated, or excessively dirty
5. Never run the engine without the air filter -- dirt entering the
   cylinder destroys the piston and rings
```

```
PROBLEM #4: CLOGGED CARBURETOR ($5 spray or $15-30 rebuild kit)

This is the #1 fix for "it ran last season but won't start now."
Stale fuel left in the carburetor varnishes the tiny jets and passages.

DIAGNOSIS:
-> Engine won't start even with fresh fuel, good spark, clean air filter
-> Engine starts with starting fluid sprayed into the air intake
   but dies immediately (confirms fuel delivery problem)
-> Engine starts on choke but dies when you open the choke

QUICK FIX (try first):
1. Remove the air filter
2. Spray carburetor cleaner ($5 can) directly into the carburetor throat
3. Try starting
4. If it runs briefly then dies, the carb jets are clogged and need
   full cleaning

FULL CARB CLEANING:
1. Close fuel shutoff valve (or clamp fuel line)
2. Remove the carburetor (2-4 bolts typically, note the linkage
   positions -- take photos before disconnecting anything)
3. Remove the float bowl (bottom of carburetor, 1 screw usually)
4. Clean all jets with carb cleaner and compressed air
   -> The main jet is a small brass piece with a tiny hole
   -> The hole MUST be clear -- poke with a fine wire if needed
   -> Spray cleaner through every opening and passage
5. Soak the entire carb body in carb cleaner for 30 minutes if heavily
   varnished
6. Reassemble and reinstall
7. If cleaning doesn't work, rebuild kits ($15-20) include new gaskets,
   needle valve, and float -- or a complete replacement carb is often
   $20-30 online

SHORTCUT: For many common engines, a complete aftermarket carburetor
is $15-30 on Amazon. Search your engine model number + "carburetor."
Sometimes replacing is faster and cheaper than cleaning.
```

```
PROBLEM #5: DEAD BATTERY (electric-start models only)

DIAGNOSIS:
-> Turn the key or press the start button -- nothing happens or slow crank
-> Lights (if any) are dim or off
-> Battery is more than 3 years old

FIX:
1. Check battery terminals for corrosion (white/green crusty buildup)
   -> Clean with wire brush and baking soda/water solution
2. Charge the battery with a trickle charger ($20-30) -- slow charge
   (2 amp) for 4-8 hours is better than fast charging
3. Test voltage with a multimeter: fully charged 12V battery reads 12.6V.
   Under 12.0V = dying. Under 11.5V = dead, replace.
4. Most riding mower and generator batteries are standard sizes
   ($30-60 at auto parts stores)

PREVENTION:
-> Trickle charger on the battery during off-season storage
-> Disconnect the negative terminal if storing more than a month
```

### Step 3: Seasonal Maintenance Schedule

**Agent action**: Provide the user with a maintenance checklist based on their equipment type and storage season.

```
BEFORE STORAGE (end of season):

-> Add fuel stabilizer to a full tank and run engine for 5 minutes
   (distributes stabilizer through the system)
   OR drain all fuel and run engine dry
-> 4-stroke: change the oil (used oil contains acids that corrode
   during storage). Use manufacturer-recommended weight.
-> Clean or replace the air filter
-> Remove spark plug, add a tablespoon of engine oil into cylinder,
   pull starter cord a few times to coat cylinder walls, reinstall plug
-> Clean the exterior -- remove grass buildup, dirt, debris
-> Store in a dry location

SPRING STARTUP:
-> Fresh fuel (premix for 2-stroke)
-> Check oil level (4-stroke)
-> New spark plug (or clean and re-gap existing)
-> Check air filter
-> Check all bolts and fasteners for tightness
-> Run for 5 minutes, check for leaks, listen for unusual sounds
```

### Step 4: Equipment-Specific Notes

**Agent action**: Cover common equipment-specific issues beyond the engine itself.

```
LAWNMOWER:
-> Blade sharpening: every 20-25 hours of use (about monthly for most
   homeowners). Remove blade (block the blade to prevent rotation,
   remove the bolt), sharpen with a file or bench grinder, check
   balance by hanging on a nail through the center hole.
-> A dull blade tears grass instead of cutting it -- brown tips and
   lawn disease.

GENERATOR:
-> CARBON MONOXIDE: NEVER run indoors, in a garage, in a basement,
   or in any enclosed space. 20 feet minimum from any window or door,
   exhaust pointed away from the building. CO is invisible, odorless,
   and kills within minutes.
-> Wattage: list all devices you need to run. Add up watts. Buy a
   generator rated 25% above your total.
-> Starting watts: motors (fridge, sump pump, AC) need 2-3x their
   running watts to start. Stagger startups -- don't turn everything
   on at once.
-> NEVER connect a generator to your house wiring by plugging it
   into an outlet (backfeeding). This sends power into the grid and
   kills utility workers. Use a transfer switch or extension cords.

PULL-CORD REPLACEMENT:
-> Common failure: cord frays and breaks
-> Replacement cord and handle: $5-10
-> Remove the starter housing (3-4 bolts), note the recoil spring
   position, thread new cord through the housing and handle, wind the
   pulley to pre-tension the spring, tie a knot in the cord inside
   the pulley. YouTube your specific model -- spring tension varies.

COST COMPARISON:
-> Average parts cost for DIY small engine repair: $10-50
-> Average small engine repair shop charge: $100-300
-> The math works in your favor for problems #1-5 every time
```

## If This Fails

- **Tried all 5 fixes and it still won't start?** Check compression: remove the spark plug, put your thumb over the hole, and pull the starter cord. You should feel strong resistance. No resistance = blown head gasket or worn rings. This is usually not worth repairing on consumer equipment.
- **Engine starts but knocks or rattles?** Internal damage (rod bearing, piston slap). Repair cost usually exceeds replacement cost for residential equipment.
- **Engine surges (rpm goes up and down rhythmically)?** Almost always a partially clogged carburetor main jet or a vacuum leak in the intake gasket. Re-clean the carb, replace the intake gasket ($3-5).
- **Engine smokes excessively?** Blue/white smoke = burning oil (overfilled, wrong oil, worn rings). Black smoke = too much fuel (dirty air filter, stuck choke, rich carburetor).
- **Not worth repairing?** If the repair cost exceeds 50% of replacement cost, replace the equipment. Donate the old one for parts.

## Rules

- Always start with the cheapest, simplest fix and work up -- don't skip to carburetor work before checking fuel freshness
- Confirm 2-stroke vs 4-stroke before giving any fuel or oil advice -- wrong fuel mix destroys engines
- Always emphasize generator CO safety -- this kills people every year during storms and power outages
- Never recommend backfeeding a generator into house wiring
- If the user describes symptoms beyond the 5 common problems, suggest a local small engine repair shop rather than guessing at internal engine work

## Tips

- Keep a spare spark plug for every engine you own. They're $3 each and the most common quick fix.
- Pre-mixed fuel (TruFuel, VP Racing) costs more per can but won't go stale for 2+ years. Worth it for equipment you use seasonally.
- Label your gas cans: "2-STROKE MIX 50:1" or "STRAIGHT GAS." Grabbing the wrong can is an expensive mistake.
- A cheap multimeter ($15-20) lets you test spark plug output, battery voltage, and kill switch circuits without guessing.
- Take a photo of any linkage or wiring before you disconnect it. Reassembly is always harder than you remember.
- The model number is on a plate or sticker on the engine itself (not just the equipment). Write it down and tape it inside the equipment's handle or cover. You'll need it for parts.
- Small engine repair shops get slammed in spring and fall. Do your maintenance before you need the equipment, not the day you need to mow.

## Agent State

```yaml
state:
  equipment:
    type: null  # mower, chainsaw, generator, trimmer, blower, tiller, snow_blower, pressure_washer
    brand: null
    model_number: null
    engine_type: null  # 2-stroke, 4-stroke
    age_years: null
    electric_start: false
  diagnosis:
    symptom: null  # wont_start, rough_running, dies_under_load, surging, smoking, no_power
    fuel_checked: false
    fuel_age_days: null
    spark_plug_checked: false
    spark_plug_condition: null  # good, fouled, worn, cracked
    air_filter_checked: false
    air_filter_condition: null  # clean, dirty, damaged
    carburetor_checked: false
    battery_checked: false
    compression_checked: false
  repair:
    problem_identified: null  # stale_fuel, bad_plug, dirty_filter, clogged_carb, dead_battery, internal
    parts_needed: []
    estimated_cost: null
    repair_completed: false
  maintenance:
    last_oil_change: null
    last_plug_change: null
    last_filter_change: null
    fuel_stabilizer_used: false
    stored_properly: null
```

## Automation Triggers

```yaml
triggers:
  - name: stale_fuel_screen
    condition: "equipment.type IS SET AND diagnosis.fuel_age_days > 30"
    action: "Your fuel has been sitting for over 30 days. Stale fuel is the cause of 90% of small engine starting problems. Let's drain the old fuel and start fresh before troubleshooting anything else."

  - name: engine_type_warning
    condition: "equipment.engine_type IS null AND diagnosis.symptom IS SET"
    action: "Before we troubleshoot, I need to know if this is a 2-stroke or 4-stroke engine. The fuel and oil requirements are different, and using the wrong type causes serious damage. Let's figure that out first."

  - name: generator_co_safety
    condition: "equipment.type IS 'generator'"
    action: "Critical safety reminder: generators produce carbon monoxide, which is invisible and odorless. NEVER run a generator indoors, in a garage, or in any enclosed space. Keep it 20 feet from any window or door with exhaust pointed away from the building."

  - name: seasonal_maintenance_prompt
    condition: "repair.repair_completed IS true AND maintenance.stored_properly IS null"
    schedule: "at end of use season"
    action: "Now that your equipment is running, let's set it up for proper storage so you don't have the same problem next season. Fuel stabilizer and a quick maintenance check now saves a repair later."

  - name: repair_vs_replace
    condition: "diagnosis.compression_checked IS true AND repair.problem_identified IS 'internal'"
    action: "Internal engine damage usually costs more to repair than the equipment is worth. If the repair estimate exceeds 50% of replacement cost, it's time for a new one. Want help figuring out the math?"
```
