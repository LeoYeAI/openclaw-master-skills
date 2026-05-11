---
name: electrical-backup-power
description: >-
  Electrical fundamentals and backup power systems. Use when someone needs to understand their electrical panel, safely connect a generator, evaluate solar options, or prepare for extended power outages.
metadata:
  category: skills
  tagline: >-
    Understand your breaker panel, connect a generator without killing a lineman, and size a basic solar setup -- electricity when the grid goes down.
  display_name: "Electrical Basics & Backup Power"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/electrical-backup-power"
---

# Electrical Basics & Backup Power

This is not a home wiring skill -- the survival-basics skill covers outlets and switches. This is about understanding the electrical system in your building and what to do when the grid goes down. Two things kill people in power outages: carbon monoxide from generators run indoors, and electrocution of utility workers from generators backfed into the grid. Both are preventable with basic knowledge. Beyond emergency generators, a basic understanding of solar and battery backup means you can keep critical systems running during extended outages without risking anyone's life, including the lineman working to restore your power.

```agent-adaptation
# Localization note -- electrical safety principles are universal. Standards and voltages differ.
# Agent must follow these rules when working with non-US users:
- Safety principles (CO poisoning prevention, backfeed danger) are universal.
- Electrical standards vary significantly:
  US/Canada: 120V/240V split-phase, 60Hz, NEMA outlets
  UK: 230V, 50Hz, BS 1363 outlets, ring circuits
  EU: 230V, 50Hz, Schuko/Type C/E/F outlets
  Australia: 230V, 50Hz, Type I outlets
- Electrical codes:
  US: National Electrical Code (NEC/NFPA 70)
  UK: BS 7671 (IET Wiring Regulations)
  AU: AS/NZS 3000 (Wiring Rules)
  EU: varies by country (HD 60364 harmonized standard)
- Transfer switch requirements and installation standards are jurisdiction-specific.
  Agent must advise user to hire a licensed electrician for any panel work.
- Solar regulations and grid-tie requirements vary dramatically by country,
  state, and utility. Agent must advise checking local rules before installing.
- Generator connection laws:
  Backfeeding is illegal and dangerous everywhere.
  Transfer switch requirements vary -- some jurisdictions mandate them by code.
- Breaker panel layout and labeling conventions differ by country.
  US: typically 120V branch circuits with 240V for large appliances
  UK: consumer unit with MCBs and RCDs
  AU: switchboard with MCBs and RCDs
```

## Sources & Verification

- **National Electrical Code (NEC/NFPA 70)** -- the US standard for electrical installation. Referenced by all US jurisdictions. [nfpa.org](https://www.nfpa.org/codes-and-standards/nfpa-70-standard-development/70)
- **NFPA electrical safety** -- fire and electrical safety guidelines for consumers. [nfpa.org/electrical-safety](https://www.nfpa.org/electrical-safety)
- **Consumer Reports generator guides** -- independent testing and safety reviews. [consumerreports.org](https://www.consumerreports.org/)
- **Department of Energy solar basics** -- objective guide to residential solar technology. [energy.gov/solar](https://www.energy.gov/eere/solar/homeowners-guide-going-solar)
- **OSHA electrical safety** -- workplace electrical safety standards applicable to home environments. [osha.gov/electrical](https://www.osha.gov/electrical)
- **CPSC generator safety data** -- Consumer Product Safety Commission data on CO deaths from portable generators. [cpsc.gov](https://www.cpsc.gov/)

## When to Use

- User wants to understand their electrical panel and what each breaker controls
- User needs to safely connect a generator during a power outage
- User is evaluating solar panels or battery backup for their home
- User wants to size a generator for their critical loads
- User needs to use a multimeter to diagnose an electrical problem
- User is preparing for extended power outages (storm season, grid instability)
- User has a shed, RV, or off-grid structure that needs basic electrical

## Instructions

### Step 1: Understanding Your Electrical Panel

**Agent action**: Help the user read and understand their breaker panel without touching anything inside it.

```
YOUR BREAKER PANEL:

WHAT IT DOES:
-> Receives power from the utility (via the meter)
-> Distributes it to branch circuits throughout your home
-> Each breaker protects one circuit from overload and short circuit
-> When a breaker trips, it disconnects that circuit to prevent fire

BREAKER SIZES AND WHAT THEY SERVE:
-> 15 amp: lighting, general outlets, bedrooms
-> 20 amp: kitchen countertop outlets, bathrooms, laundry, garage,
   outdoor outlets (anywhere code requires GFCI protection)
-> 30 amp (240V): electric dryer, some water heaters
-> 40 amp (240V): electric range/oven, some hot tubs
-> 50 amp (240V): large electric range, sub-panel feed
-> Main breaker (100-200 amp typical): disconnects everything

READING YOUR PANEL SCHEDULE:
-> Inside the panel door is a list (or should be) mapping each
   breaker to what it controls
-> If this is blank or wrong, map it yourself: turn off one breaker
   at a time, walk the house to find what went dead, label it
-> This takes 30-60 minutes and is worth every second. You need to
   know what you're working with.

CALCULATING CIRCUIT LOAD:
-> Watts = Volts x Amps
-> A 15A circuit on 120V = 1,800 watts maximum
-> The 80% rule: don't load a circuit beyond 80% of its rating
   for continuous loads. 15A circuit = 1,440W practical limit.
-> Add up the wattage of everything on a circuit. If it exceeds
   80% of the breaker rating, you're overloaded.

WHAT TRIPS BREAKERS:
-> Overload: too many devices on the circuit (breaker feels warm,
   trips after running a while)
-> Short circuit: hot wire touches neutral or ground (breaker
   trips instantly, may arc or spark)
-> Ground fault: current leaking to ground through unintended path
   (GFCI outlet or GFCI breaker trips)
-> Bad breaker: breakers can wear out and trip falsely (rare but real)

DO NOT OPEN THE PANEL COVER (the inner deadfront, not the door):
-> Behind the breakers is the bus bar with line voltage
-> Contact with the bus bar or main lugs can kill you instantly
-> The panel door (with the breaker schedule) is safe to open
-> The deadfront cover (behind the breakers) is electrician territory
```

### Step 2: Generator Safety and Connection

**Agent action**: Cover the critical safety rules FIRST, then proper connection methods.

```
GENERATOR SAFETY -- READ THIS BEFORE ANYTHING ELSE:

CARBON MONOXIDE (CO) -- THE INVISIBLE KILLER:
-> Portable generators produce carbon monoxide, which is colorless
   and odorless
-> NEVER run a generator indoors, in a garage (even with the door
   open), in a basement, in a crawl space, or in any enclosed area
-> Place the generator at least 20 feet from any window, door, or vent
-> Point the exhaust AWAY from the building
-> Install battery-powered CO detectors on every level of your home
   and near sleeping areas (if you don't already have them)
-> Symptoms of CO poisoning: headache, dizziness, nausea, confusion.
   If anyone feels these symptoms during a power outage with a
   generator running: get outside immediately, call 911.
-> CPSC data: generators cause more CO deaths each year than any
   other consumer product

BACKFEEDING -- A FELONY THAT KILLS PEOPLE:
-> Backfeeding means connecting a generator to a house outlet with a
   "suicide cord" (male-to-male plug) so power flows backward through
   your wiring to all your outlets
-> This sends power BACK into the utility grid through your meter
-> Utility linemen working on "dead" lines get electrocuted by YOUR
   generator power stepped up to thousands of volts by the transformer
-> This is illegal, it is a felony in most jurisdictions, and it kills
   utility workers trying to restore your power
-> NEVER DO THIS. There is no safe way to backfeed.

PROPER CONNECTION OPTIONS (safest to simplest):

OPTION 1: MANUAL TRANSFER SWITCH ($200-300 + electrician install)
-> Installed next to your main panel by a licensed electrician
-> Lets you select which circuits get generator power
-> Physically disconnects those circuits from the grid before
   connecting to the generator -- impossible to backfeed
-> The RIGHT way to do it. One-time cost, permanent safety.

OPTION 2: INTERLOCK KIT ($50-150 + electrician install)
-> A mechanical device on your panel that prevents the main breaker
   and generator breaker from being on simultaneously
-> Cheaper than a transfer switch, provides the same backfeed protection
-> Must be approved for your panel brand
-> Still requires electrician installation

OPTION 3: EXTENSION CORDS (simplest, most limited)
-> Run individual extension cords from the generator directly to
   appliances (fridge, sump pump, lights, etc.)
-> No connection to house wiring at all
-> Use heavy-duty outdoor extension cords rated for the load
-> 12-gauge cord for runs up to 100 feet at 15 amps
-> Don't daisy-chain cords or overload them
-> This is the only option that doesn't require an electrician
```

### Step 3: Sizing a Generator

**Agent action**: Help the user calculate their critical load and select an appropriately sized generator.

```
SIZING YOUR GENERATOR:

STEP 1: LIST CRITICAL LOADS (what you absolutely need during an outage)

TYPICAL RUNNING WATTS:
-> Refrigerator: 100-400W running, 1200W starting surge
-> Freezer: 50-100W running, 500W starting surge
-> Sump pump: 500-1000W running, 1500-2500W starting surge
-> Furnace blower: 300-800W running, 800-1500W starting surge
-> Well pump: 750-1500W running, 1500-3000W starting surge
-> Lights (LED): 10-15W per bulb
-> Phone/laptop charger: 50-100W
-> Window AC unit: 500-1500W running, 1500-3000W starting surge
-> Microwave: 1000-1500W (no surge)
-> Space heater: 1500W (no surge)
-> TV: 50-200W

STEP 2: ADD UP RUNNING WATTS FOR EVERYTHING YOU NEED SIMULTANEOUSLY

Example (basic setup):
-> Fridge: 400W
-> Sump pump: 800W
-> Furnace blower: 500W
-> Lights: 200W (20 LED bulbs)
-> Phone chargers: 100W
-> TOTAL RUNNING: 2,000W

STEP 3: ACCOUNT FOR STARTING SURGE
-> Motors (fridge, sump pump, furnace, AC, well pump) need 2-3x their
   running wattage to start
-> The largest starting surge in your list sets your surge requirement
-> Sump pump surge: 2,500W (largest in our example)

STEP 4: SIZING RULE
-> Generator rated watts should exceed your total running watts by 25%
-> Generator surge watts should exceed your largest single starting surge
-> Our example: 2,000W x 1.25 = 2,500W minimum rated, with 3,000W+ surge
-> A 3,500W generator handles this comfortably

STEP 5: STAGGER MOTOR STARTUPS
-> Don't turn on the fridge, sump pump, and furnace simultaneously
-> Start one motor, let it stabilize (10-15 seconds), then the next
-> This prevents overloading the generator during startup surges

FUEL CONSUMPTION:
-> A 3,500W generator uses roughly 0.5-1 gallon per hour at half load
-> Plan for fuel: how long might the outage last? Store fuel safely
   in approved containers, away from the generator and the house.
-> Gasoline stored more than 30 days needs fuel stabilizer.
```

### Step 4: Solar and Battery Backup Basics

**Agent action**: Cover the components, sizing, and realistic expectations for a basic solar backup system.

```
SOLAR BACKUP -- THE SYSTEM:

COMPONENTS (in order of power flow):
1. SOLAR PANELS -> generate DC electricity from sunlight
2. CHARGE CONTROLLER -> regulates voltage from panels to battery
   (prevents overcharge)
3. BATTERY BANK -> stores energy for use when the sun isn't shining
4. INVERTER -> converts DC battery power to AC household power

SYSTEM TYPES:
-> Grid-tied (no battery): panels feed your meter, reduces electric bill,
   but DOES NOT work during outages (shuts off to protect linemen --
   same backfeed issue as generators)
-> Grid-tied with battery backup: normal operation feeds the grid,
   during outage switches to battery. Best of both worlds. Expensive.
-> Off-grid: completely independent. Must size for all your needs.
   No utility bill, no utility backup.
-> Portable/emergency: small panel + battery for essential devices only.
   $200-1000 for a basic kit.

SIZING A BASIC EMERGENCY SYSTEM:

Goal: Keep fridge, lights, phones, and a few small devices running
during a multi-day outage.

-> Panels: 1,000W array (4x 250W panels, ~$400-800)
   Produces roughly 4-5 kWh/day in good sun (varies by location/season)
-> Charge controller: MPPT type, sized for your panel array ($100-200)
-> Battery bank: 5 kWh capacity ($500-2000 depending on chemistry)
   -> Lead-acid: cheapest upfront ($500), heavy, only use 50% of
      capacity (10 kWh bank for 5 kWh usable), lasts 3-5 years
   -> Lithium (LiFePO4): more expensive ($1500-2000), lighter,
      use 80-90% of capacity, lasts 10-15 years, better value long-term
-> Inverter: pure sine wave, sized for your peak load ($200-500 for
   2000-3000W)

TOTAL DIY COST: roughly $2,000-4,000 for a basic emergency backup

12V SYSTEMS (sheds, RVs, off-grid cabins):
-> Simpler: 1-2 panels, small charge controller, 12V battery, 12V
   lights and devices (or a small inverter for occasional AC use)
-> $200-500 for a basic 12V system
-> Good starter project to learn solar fundamentals

REALITY CHECK:
-> Solar + battery will NOT run central AC, electric heat, electric
   water heater, or electric range without a very large (expensive) system
-> It WILL run a fridge, LED lights, fans, electronics, and small
   appliances reliably
-> Your location's sun hours matter enormously. Arizona gets twice
   the production of Michigan in winter.
-> Panels need to face south (in the Northern Hemisphere) with minimal
   shade. Shade on even one panel can cut output dramatically.
```

### Step 5: Using a Multimeter

**Agent action**: Teach the three basic measurements that diagnose most electrical problems.

```
MULTIMETER BASICS -- THE 3 MEASUREMENTS THAT MATTER:

A multimeter ($15-30 for a basic digital model) is the single most
useful electrical diagnostic tool. Three settings handle 90% of
troubleshooting:

1. VOLTAGE (V or VAC/VDC)
-> What it tells you: is power present and at the right level?
-> AC voltage (VAC): for household outlets, generators, panels
   -> US outlet should read 110-125V
   -> Generator output should match its rated voltage
-> DC voltage (VDC): for batteries, solar panels, car electrical
   -> 12V battery fully charged: 12.6V
   -> 12V battery dead: below 11.5V
-> HOW TO: set dial to the correct voltage type (AC or DC), insert
   red probe in the V jack, black in COM, touch probes to the two
   test points

2. CONTINUITY (the beep test)
-> What it tells you: is there an unbroken path for electricity?
-> Tests wires, fuses, switches, cords for breaks
-> Set dial to continuity (looks like a sound wave or has a beep icon)
-> Touch probes to both ends of the thing you're testing
-> BEEP = continuous path (good wire, good fuse, closed switch)
-> NO BEEP = broken path (broken wire, blown fuse, open switch)
-> ALWAYS test with power OFF. Continuity testing on a live circuit
   can damage the meter.

3. AMPERAGE (A)
-> What it tells you: how much current is flowing through a circuit?
-> Useful for checking if a circuit is overloaded
-> Clamp-style ammeters ($30-40) are safest: clamp around a single
   wire without touching any conductors
-> Compare the reading to the breaker rating. At or near 80% of the
   breaker = overloaded circuit.

SAFETY WITH A MULTIMETER:
-> Never measure resistance or continuity on a live circuit
-> Never exceed the meter's rated voltage (most consumer meters
   are rated for 600V -- plenty for residential)
-> Hold probes by the insulated handles only
-> If you're not sure what you're measuring or what's energized,
   don't probe it. Call an electrician.
```

### Step 6: When to Stop and Hire an Electrician

**Agent action**: Draw a clear line between what's safe for a homeowner and what requires a professional.

```
STOP AND CALL AN ELECTRICIAN:

-> Anything inside the breaker panel (behind the deadfront cover)
-> Anything over 20 amps
-> Any new circuit installation
-> Transfer switch or interlock kit installation
-> Any work that requires a permit (most jurisdictions require permits
   for new circuits, panel work, and service changes)
-> Aluminum wiring (common in 1960s-70s homes -- requires special
   connectors and techniques)
-> Knob-and-tube wiring (pre-1950s -- do not modify or extend)
-> Any situation where you're not confident in what you're doing
-> Signs of electrical fire risk: charred outlets, melted wire
   insulation, burning smell, frequently tripping breakers, flickering
   lights throughout the house, warm outlet covers

HOW TO FIND A GOOD ELECTRICIAN:
-> Licensed and insured (verify with your state licensing board)
-> Ask for references on similar work
-> Get 2-3 written quotes
-> For generator/solar work, ask specifically about their experience
   with transfer switches and backup power systems
-> Expect to pay $75-150/hour or a flat rate for defined jobs
```

## If This Fails

- **Generator won't start?** See the small-engine-repair skill -- generators use the same engines as lawnmowers and are subject to the same stale fuel, spark plug, and carburetor problems.
- **Generator runs but appliances don't work?** Check the generator's circuit breaker (they have their own breakers). Check that extension cords are rated for the load and are properly connected. Check that the appliance works (plug something else in).
- **Solar system not producing expected output?** Check for shade, check panel connections, check charge controller readings. Dirty panels lose 15-25% output -- clean with water and a soft cloth. Winter production is roughly half of summer in most locations.
- **Breaker keeps tripping?** Reduce the load on that circuit. If it still trips with nothing plugged in, you have a wiring problem -- call an electrician.
- **Power outage and no backup?** Focus on food preservation (don't open the fridge -- it stays cold for 4 hours, a full freezer for 48 hours), charge devices from your car (with the engine running), and dress for temperature.

## Rules

- Never instruct users to work inside the breaker panel
- Always emphasize CO safety with generators -- this kills people annually
- Never describe or enable backfeeding under any circumstances
- Always recommend a licensed electrician for panel work, new circuits, and transfer switch installation
- Clearly distinguish between what a homeowner can safely do and what requires a professional
- Always recommend CO detectors when discussing generator use

## Tips

- A $20 outlet tester (the little plug-in device with three lights) tells you instantly if an outlet is wired correctly. Worth having in your toolbox.
- Label your breaker panel if it isn't already labeled. During an outage, you don't want to be guessing which breaker controls the sump pump.
- For solar, start small. A single 100W panel, a charge controller, and a 12V battery can keep phones, radios, and LED lights running indefinitely. Scale up from there.
- LED bulbs draw so little power that lighting is almost free on a generator or solar system. Switch to LEDs if you haven't already.
- Keep your generator's fuel fresh. Either run it monthly for 15 minutes under load, or use fuel stabilizer. The worst time to discover your generator won't start is during the outage.
- A whole-house surge protector ($50-100, electrician-installed at the panel) protects everything from power surges when the grid comes back on. Worth the investment.
- UPS (uninterruptible power supply) units ($50-150) keep your internet router, computer, and medical devices running through brief outages and protect against surges. Not a substitute for a generator, but handles the first 15-60 minutes.

## Agent State

```yaml
state:
  electrical_knowledge:
    experience_level: null  # none, basic, intermediate
    panel_mapped: false
    panel_amperage: null
    panel_type: null
    owns_multimeter: false
  power_situation:
    current_status: null  # normal, outage_planning, active_outage
    outage_expected_duration: null
    critical_loads_identified: false
    critical_load_total_watts: null
  generator:
    owns_generator: false
    generator_wattage: null
    fuel_type: null
    connection_method: null  # extension_cords, transfer_switch, interlock_kit, none
    transfer_switch_installed: false
    co_detectors_installed: null
  solar:
    interested: false
    system_type: null  # grid_tied, grid_battery, off_grid, portable
    panel_wattage: null
    battery_capacity_kwh: null
    battery_type: null  # lead_acid, lithium
    location_sun_hours: null
  safety_checks:
    co_safety_confirmed: false
    backfeed_risk_addressed: false
    electrician_needed: false
```

## Automation Triggers

```yaml
triggers:
  - name: co_safety_warning
    condition: "generator.owns_generator IS true OR power_situation.current_status IS 'active_outage'"
    action: "Critical safety reminder: NEVER run a generator indoors, in a garage, or near windows. Carbon monoxide is invisible, odorless, and kills within minutes. Place the generator 20 feet from any opening, exhaust pointed away. Make sure you have working CO detectors inside."

  - name: backfeed_prevention
    condition: "generator.connection_method IS null OR generator.connection_method IS 'none'"
    action: "Before connecting your generator to anything beyond extension cords, you need a transfer switch or interlock kit installed by an electrician. Connecting a generator directly to house wiring (backfeeding) is illegal and can electrocute utility workers restoring power."

  - name: generator_sizing_check
    condition: "power_situation.critical_loads_identified IS true AND generator.generator_wattage IS SET"
    action: "Let's verify your generator is sized correctly. Your critical loads total {critical_load_total_watts}W. Your generator is rated at {generator_wattage}W. You need at least 25% headroom plus enough surge capacity for your largest motor startup."

  - name: solar_feasibility
    condition: "solar.interested IS true AND solar.location_sun_hours IS null"
    action: "Before sizing a solar system, we need to know your location's average sun hours. This determines how much energy your panels will actually produce. What's your general location? I can help estimate daily production."

  - name: panel_mapping_prompt
    condition: "electrical_knowledge.panel_mapped IS false AND power_situation.current_status IS 'outage_planning'"
    action: "You should map your breaker panel before an outage hits. Turn off one breaker at a time, walk the house to find what went dead, and label it. This takes 30-60 minutes now and saves critical time during an actual outage."
```
