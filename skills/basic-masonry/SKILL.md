---
name: basic-masonry
description: >-
  Foundational masonry and concrete skills for home and property projects. Use when someone needs to pour a concrete slab, build a retaining wall, lay bricks or blocks, repair cracked concrete, or build outdoor structures.
metadata:
  category: skills
  tagline: >-
    Pour a slab, lay bricks, build a retaining wall, repair cracked concrete -- building things that last a hundred years.
  display_name: "Basic Masonry & Concrete"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/basic-masonry"
---

# Basic Masonry & Concrete

Concrete and masonry are the oldest building technologies still in daily use, and they reward patience more than skill. A concrete slab poured by a careful beginner will outlast a deck built by a sloppy carpenter. The fundamentals haven't changed in a century: get your mix right, keep things level and plumb, and let it cure. Where people go wrong is adding too much water (weak concrete that crumbles), skipping the gravel base (frost heave cracks your slab), and rushing the cure (concrete reaches full strength at 28 days, not 2). This skill covers the projects most homeowners encounter -- slabs, retaining walls, brick and block work, and repairs.

```agent-adaptation
# Localization note -- masonry principles are universal. Standards, products, and climate vary.
# Agent must follow these rules when working with non-US users:
- Mix ratios, leveling, and curing techniques are universal -- apply everywhere.
- Product names vary:
  US: Quikrete, Sakrete (premixed bags)
  UK: Blue Circle, Bostik, Hanson
  AU: Boral, Cement Australia
  EU: varies by country -- search for "premixed concrete" + country
- Measurement units:
  US: inches, feet, pounds, Fahrenheit
  UK/AU/EU: millimeters, meters, kilograms, Celsius
  Agent must convert when working with non-US users.
- Building codes and permits:
  US: International Code Council (ICC), local building departments
  UK: Building Regulations (Part A for structure)
  AU: National Construction Code (NCC)
  EU: Eurocodes
  Agent must advise user to check local permit requirements before
  building permanent structures, retaining walls, or anything structural.
- Rebar specifications vary by country (US #3 = 10mm in metric countries).
- Frost depth varies dramatically. Agent must check local frost line
  before advising on footer depth. US: ranges from 0" (southern FL) to 72" (northern MN).
```

## Sources & Verification

- **Portland Cement Association** -- the definitive US resource for concrete mix design, placement, and curing. [cement.org](https://www.cement.org/)
- **International Code Council (ICC)** -- building codes governing structural masonry and concrete. [iccsafe.org](https://www.iccsafe.org/)
- **Quikrete project guides** -- practical step-by-step for common residential projects. [quikrete.com](https://www.quikrete.com/)
- **This Old House masonry tutorials** -- accessible explanations of brick, block, and concrete techniques. [thisoldhouse.com](https://www.thisoldhouse.com/)
- **Masonry Construction magazine** -- industry best practices and technical guides. [masonryconstruction.com](https://www.masonryconstruction.com/)

## When to Use

- User needs to pour a concrete slab for a shed, patio, or workshop
- User wants to build a retaining wall on sloped property
- User needs to lay bricks or blocks for a planter, wall, or steps
- User has cracked concrete that needs repair
- User wants to build outdoor steps or a landing
- User is evaluating whether a masonry project is DIY or needs a contractor

## Instructions

### Step 1: Understand Concrete vs Mortar

**Agent action**: Clarify the difference. Using the wrong one is a common beginner mistake.

```
CONCRETE vs MORTAR -- different materials for different jobs:

CONCRETE = cement + sand + gravel (aggregate) + water
-> Structural material. Strong in compression.
-> Used for: slabs, footings, posts, foundations, steps, piers
-> Premixed bags (Quikrete, Sakrete): just add water. Good for small
   jobs (under 1 cubic yard). Available in 40, 60, 80 lb bags.
-> For larger jobs: order ready-mix from a concrete truck (sold by
   the cubic yard, ~$150-200/yard depending on location)

MORTAR = cement + sand + water (NO gravel)
-> Bonding material. Sticks bricks and blocks together.
-> Used for: laying bricks, blocks, stone; repointing old joints
-> Premixed bags (Type S for structural/below grade, Type N for
   above grade, Type M for heavy load/below grade)
-> Mix in small batches -- mortar becomes unworkable within 90 minutes

CONCRETE PATCH/REPAIR PRODUCTS:
-> Vinyl concrete patcher: for surface repairs, thin overlays
-> Hydraulic cement: sets in minutes, even underwater. For active leaks.
-> Crack filler: for hairline cracks, applied with a caulk gun
-> Epoxy injection: for structural foundation crack repair

HOW MUCH DO I NEED?
-> Concrete: Length (ft) x Width (ft) x Depth (ft) / 27 = cubic yards
-> A 10x10 slab, 4" thick: 10 x 10 x 0.33 / 27 = 1.2 cubic yards
   That's about sixty 80-lb bags. Consider a truck delivery.
-> Mortar: roughly 7 bags per 100 square feet of standard brick wall
```

### Step 2: Pouring a Concrete Slab

**Agent action**: Walk through the complete process for a basic slab -- the most common residential concrete project.

```
POURING A CONCRETE SLAB:

STEP 1: SITE PREPARATION
-> Mark the slab outline with stakes and string
-> Excavate: remove topsoil and organic material to a depth of 8-10"
   (4" gravel base + 4" concrete)
-> Compact the subsoil (hand tamper $25 or rent a plate compactor $50/day)
-> Add 4" of compacted gravel (crushed stone or road base)
   -> This is drainage. Skip it and freeze/thaw cycles will crack your slab.
-> Compact the gravel in 2" lifts (add 2", compact, add 2" more, compact)

STEP 2: BUILD FORMS
-> 2x4 lumber for a 4" slab (actual dimension is 3.5" -- close enough)
-> Stake the forms every 2-3 feet with wooden stakes
-> Check level across the entire form -- use a long straight board and level
-> Slope slightly for drainage: 1/8" per foot away from structures
-> Oil the inside of forms with form release oil or even used motor oil
   (makes removal easier)

STEP 3: ADD REINFORCEMENT
-> Wire mesh (6x6 welded wire mesh, $5-8/sheet): good for basic slabs
   -> Set on wire chairs or brick pieces -- mesh must be IN the concrete,
      not sitting on the ground under it
-> Rebar (for heavier loads like a vehicle): #3 (3/8") rebar in a 2-foot
   grid, tied with wire at intersections, set on rebar chairs
-> Fiber-reinforced concrete (premixed bags with fibers): acceptable for
   walkways and light-duty slabs but doesn't replace wire mesh for vehicle loads

STEP 4: MIX AND POUR
-> Premixed bags: follow bag directions exactly. Add water GRADUALLY.
   -> The concrete should hold its shape when squeezed in your hand
   -> If you can pour it like a milkshake, you added too much water
   -> Too much water = weak concrete. This is the #1 beginner mistake.
-> Pour into forms, work into corners with a shovel or rake
-> Fill to the top of the forms

STEP 5: SCREED
-> Use a straight 2x4 longer than the slab width
-> Rest it on the form boards and pull it toward you in a sawing motion
-> This levels the surface to the top of the forms
-> Fill low spots, screed again

STEP 6: FLOAT AND FINISH
-> Bull float ($15-25, long-handled flat tool): push across the surface
   immediately after screeding to push aggregate down and bring cream
   (smooth cement paste) to the surface
-> Wait until surface water disappears and concrete holds a thumbprint
   without sticking
-> Finish with a hand float or trowel for a smooth surface
-> Edge the perimeter with an edging tool ($5) for a rounded edge
   that resists chipping
-> Cut control joints with a groover every 8-10 feet (for slabs over
   10 feet in any direction) -- these create planned crack lines

STEP 7: CURE
-> DO NOT let it dry out fast. Fast drying = weak concrete.
-> Cover with plastic sheeting
-> Mist with water once or twice daily for 7 days
-> Keep foot traffic off for 24-48 hours
-> Keep heavy loads off for 7 days
-> Full strength at 28 days
```

### Step 3: Building a Retaining Wall

**Agent action**: Walk through retaining wall construction with emphasis on drainage -- the most common failure point.

```
RETAINING WALL (under 3-4 feet height -- taller requires an engineer):

MATERIALS OPTIONS:
-> Interlocking concrete blocks ($3-6 each): easiest for beginners,
   no mortar needed, built-in setback/batter
-> Concrete masonry units (CMU/cinder blocks) with mortar: stronger,
   more traditional, requires mortar skills
-> Natural stone (dry-stack or mortared): most attractive, requires
   fitting skill, more labor

INTERLOCKING BLOCK WALL (recommended for beginners):

STEP 1: EXCAVATE AND LEVEL
-> Dig a trench the width of the block + 6" behind for drainage gravel
-> Depth: half the height of the first block below grade
-> Compact the trench bottom
-> Add 2-3" of gravel, compact, level

STEP 2: FIRST COURSE IS EVERYTHING
-> The first course must be perfectly level. Every error multiplies
   as you go up.
-> Set blocks on the gravel, check level side-to-side and front-to-back
   after EVERY block
-> Use a rubber mallet to tap blocks into position
-> Check level across multiple blocks with a long level or string line

STEP 3: BUILD UP
-> Offset each course by half a block (running bond pattern)
-> Interlocking blocks have a built-in lip that sets the batter
   (backward lean into the hill)
-> Check level every course
-> Fill cores with gravel as you go for added weight and drainage

STEP 4: DRAINAGE (the part everyone skips, then their wall fails)
-> Behind the wall: 12" of clean crushed gravel, not dirt
-> At the base: 4" perforated drain pipe (holes facing DOWN) in gravel,
   sloped to daylight at the end of the wall
-> This is NON-NEGOTIABLE. Water pressure behind a retaining wall is the
   #1 cause of failure. The gravel and drain pipe relieve that pressure.
-> Cover the gravel with filter fabric to prevent soil from clogging it
-> Backfill with native soil above the gravel zone

STEP 5: CAP
-> Adhesive the cap blocks with construction adhesive
-> This locks the top course and provides a finished look

HEIGHT LIMITS:
-> DIY: 3-4 feet maximum without engineering
-> Taller: requires a structural engineer, possibly a building permit,
   and likely geogrid reinforcement
-> Stacking two shorter walls with a terrace between them is often
   cheaper and safer than one tall wall
```

### Step 4: Laying Bricks or Blocks

**Agent action**: Cover basic brick/block laying technique for walls, planters, and small structures.

```
BRICK AND BLOCK LAYING:

TOOL LIST:
-> Brick trowel ($8-15): your main tool
-> 4-foot level ($20): check every course
-> Mason's line and pins ($3): keeps courses straight between corners
-> Jointer/striking tool ($5): shapes the mortar joints
-> Mixing tub or wheelbarrow ($10-20)
-> Brick hammer ($15): for cutting bricks (or a cold chisel and hammer)

MORTAR MIXING:
-> Premixed bags: follow directions, add water gradually
-> Consistency: should hold its shape on the trowel, not run off
-> Like thick peanut butter, not pancake batter
-> Mix small batches -- mortar sets in 90 minutes on a warm day

TECHNIQUE:
1. Start at the corners -- build corners up 3-4 courses first
2. Butter the bed: spread 3/4" to 1" of mortar on the course below
   with the trowel (furrow it down the middle with the trowel tip)
3. Butter the head: spread mortar on the end of the brick you're placing
4. Press the brick into position. Check level immediately.
5. Tap with the trowel handle to adjust. Remove excess mortar.
6. Run a string line between built-up corners to keep courses straight
7. Every course should be level (check with level) and plumb
   (check with level held vertically against the face)
8. Offset each course by half a brick (running bond) unless doing
   a different pattern
9. Joint thickness: 3/8" for bricks, 3/8"-1/2" for blocks

TOOLING JOINTS:
-> After mortar firms up (thumbprint stays but mortar doesn't stick
   to your thumb), tool the joints with a jointer
-> Concave joint (most common): press the jointer along the mortar,
   compressing it into a curved shape that sheds water
-> Tool vertical joints first, then horizontal
-> Brush off excess mortar crumbs with a stiff brush
```

### Step 5: Repairing Cracked Concrete

**Agent action**: Diagnose the crack type and provide the appropriate repair method.

```
CONCRETE CRACK DIAGNOSIS:

HAIRLINE CRACKS (less than 1/8" wide):
-> Cause: normal shrinkage during curing, minor settlement
-> Severity: cosmetic, not structural
-> Fix: concrete crack filler ($5 tube, caulk gun application)
   or vinyl concrete patcher thinned slightly

WIDER CRACKS (1/8" to 1/2"):
-> Cause: settling, frost heave, tree roots, minor overload
-> Fix: chisel the crack wider at the bottom than the top
   (creates a key that holds the patch), clean out debris,
   dampen the surfaces, fill with vinyl concrete patcher

STRUCTURAL CRACKS (in foundations):
-> HORIZONTAL cracks in a foundation wall = lateral soil/water pressure
   pushing the wall inward. This is SERIOUS. Call a structural engineer.
-> STAIR-STEP cracks in block foundation walls = differential settlement.
   Call an engineer if they're wider than 1/4" or actively growing.
-> VERTICAL foundation cracks: most common, usually from shrinkage.
   Repair with epoxy injection kit ($30-50) to seal against water.
-> If in doubt about any foundation crack, get a structural engineer
   to look at it. A $200-400 inspection is cheap compared to a failed
   foundation.

SPALLING (surface flaking):
-> Cause: freeze/thaw damage, deicing salts, poor original finishing
-> Fix: clean loose material, apply bonding agent, then resurface
   with vinyl concrete patcher or self-leveling overlay
-> Prevention: seal concrete surfaces with concrete sealer every 2-3 years
   in freeze/thaw climates

SINKING SLAB SECTIONS:
-> Cause: soil erosion under the slab, poor compaction at construction
-> DIY: mudjacking compound (foam injection kits, $50-100 for small areas)
-> Professional mudjacking: $500-1500, much cheaper than replacement
-> If the slab is badly broken AND sunken, replacement may be the
   only real fix
```

### Step 6: Building Concrete Steps

**Agent action**: Cover step construction for common residential applications.

```
CONCRETE STEPS:

DIMENSIONS:
-> Riser height (vertical): 7" standard (building code range: 4-7.75")
-> Tread depth (horizontal): 11" minimum (deeper is more comfortable)
-> All risers must be the same height -- uneven risers cause falls
-> Width: 36" minimum for code, 48" is more comfortable

FORM BUILDING:
-> Build side forms from 3/4" plywood cut to the step profile
-> Support with 2x4 stakes driven into the ground
-> Add riser boards (2x6 or 2x8 cut to riser height) across the front
   of each step
-> Brace everything heavily -- concrete is heavy (150 lbs per cubic foot)
   and will blow out weak forms
-> The bottom step form sits on compacted gravel
-> Rebar: #3 rebar in a grid inside the steps, tied to pins drilled
   into the existing foundation if connecting to a building

POURING AND FINISHING:
-> Start at the bottom step, fill each step fully
-> Screed each tread level with the riser boards
-> Bull float each tread surface
-> Wait for bleed water to disappear, then finish with a hand float
-> Broom finish (drag a push broom across) for non-slip surface
-> Edge all exposed edges
-> Round the nosing (front edge of each tread) with an edger

CURING:
-> Same as a slab: moist cure for 7 days
-> Keep covered with plastic and mist daily
-> No foot traffic for 48 hours, full load at 7 days
```

## If This Fails

- **Concrete set before you could finish?** On hot days, concrete sets much faster. Next time: work early morning, have all tools and help ready, use a retarder additive, and don't mix more than you can place in 20 minutes.
- **Retaining wall leaning or bulging?** Drainage failure. Tear down to the failure point, install proper drainage (gravel + perforated pipe), rebuild. There's no shortcut.
- **Mortar joints cracking and falling out?** Mortar was likely too dry, too wet, or wasn't tooled at the right time. Repoint: grind out old mortar to 3/4" depth, dampen joint, pack new mortar, tool when firm.
- **Concrete crumbled within a year?** Too much water in the mix, inadequate curing, or deicing salt damage on uncured concrete. The affected section likely needs to be broken out and repoured.
- **Project is bigger than expected?** Anything over 1 cubic yard of concrete, retaining walls over 4 feet, or structural work should involve a contractor or at minimum a structural engineer's review.

## Rules

- Always recommend checking local building codes and permit requirements before permanent structures
- Emphasize proper water-to-cement ratio -- this is the #1 factor in concrete quality
- Never advise on retaining walls over 4 feet without recommending a structural engineer
- Always include drainage instructions for retaining walls and any below-grade work
- Distinguish between cosmetic and structural cracks clearly -- structural cracks need professional evaluation
- Recommend safety glasses when cutting or chipping concrete (silica dust, flying fragments)

## Tips

- Mix concrete dryer than you think it should be. If it pours easily, it's too wet. It should hold a shape when squeezed.
- Rent a concrete mixer for any project over 10 bags ($40-60/day). Hand-mixing 60 bags in a wheelbarrow will ruin your day and your back.
- Mist your forms and any existing concrete surfaces with water before pouring. Dry surfaces suck moisture out of the fresh concrete and weaken the bond.
- Concrete is stronger in compression than tension. That's why rebar matters -- the steel handles tension that the concrete can't.
- For a non-slip outdoor surface, drag a stiff broom across freshly floated concrete (broom finish). Smooth-troweled concrete outdoors becomes an ice rink in winter.
- Buy 10% more material than your calculations say you need. You will spill some, leave some on the mixer walls, and find a low spot you didn't measure.
- Don't pour concrete if the temperature will drop below 40F/4C within 48 hours. Cold concrete doesn't cure properly and can fail.
- Concrete dust (silica) is a serious lung hazard. Wear an N95 mask when cutting, grinding, or demolishing concrete.

## Agent State

```yaml
state:
  project:
    type: null  # slab, retaining_wall, brick_wall, steps, repair, planter
    dimensions: null
    height: null
    materials_calculated: false
    permit_checked: false
  site_conditions:
    soil_type: null
    slope: null
    frost_depth: null
    drainage_plan: null
    near_structures: false
  materials:
    concrete_type: null  # premixed_bags, ready_mix_truck
    mortar_type: null  # type_S, type_N, type_M
    reinforcement: null  # wire_mesh, rebar, fiber, none
    quantity_needed: null
    quantity_ordered: null
  progress:
    site_prepared: false
    forms_built: false
    reinforcement_placed: false
    poured: false
    finished: false
    curing: false
    cure_day: 0
    forms_removed: false
  repair:
    crack_type: null  # hairline, moderate, structural, spalling
    location: null
    cause_identified: null
    professional_needed: false
```

## Automation Triggers

```yaml
triggers:
  - name: permit_check
    condition: "project.type IS SET AND project.permit_checked IS false"
    action: "Before you start, check with your local building department about permit requirements. Retaining walls over a certain height, any structural work, and slabs for new structures often require permits. A quick call can save you from tearing it all down later."

  - name: structural_crack_warning
    condition: "repair.crack_type IS 'structural'"
    action: "That sounds like a structural crack. Before attempting any repair, get a structural engineer to evaluate it. A $200-400 inspection tells you whether this is a simple fix or a sign of a bigger foundation problem. Don't seal over a crack that's telling you something important."

  - name: retaining_wall_height_check
    condition: "project.type IS 'retaining_wall' AND project.height > 48"
    action: "A retaining wall over 4 feet needs a structural engineer to design it. The forces involved increase dramatically with height, and failure puts people and property at risk. This isn't a cost-saving situation -- it's a safety situation."

  - name: curing_reminder
    condition: "progress.curing IS true AND progress.cure_day < 7"
    schedule: "daily for 7 days"
    action: "Day {cure_day} of concrete curing. Mist the surface with water and make sure the plastic cover is in place. Concrete gains most of its strength in the first 7 days, but only if it stays moist. Don't let it dry out."

  - name: weather_check
    condition: "progress.poured IS false AND project.type IN ['slab', 'steps', 'retaining_wall']"
    action: "Check the weather forecast before you pour. You need at least 48 hours above 40F/4C after pouring, and rain on fresh concrete damages the surface. The ideal window is mild, overcast days in the 50-70F range."
```
