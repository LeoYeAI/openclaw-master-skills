---
name: chainsaw-tree-work
description: >-
  Safe chainsaw operation and basic tree felling techniques. Use when someone needs to fell a tree, cut firewood, clear storm damage, or is buying their first chainsaw and needs safety training.
metadata:
  category: skills
  tagline: >-
    The most dangerous power tool civilians use. PPE, the 5-step felling plan, limbing, bucking, and when to call a professional -- zero bravado.
  display_name: "Chainsaw & Tree Work Safety"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/chainsaw-tree-work"
---

# Chainsaw & Tree Work Safety

Chainsaws kill more recreational users than any other power tool. That's not a scare tactic -- it's the reason every section of this skill starts with what can go wrong before telling you how to do it right. A chainsaw doesn't care how confident you feel. It will cut through your femoral artery in the same fraction of a second it cuts through wood. PPE is non-negotiable. The felling plan is non-negotiable. Knowing when to call a professional is the most important skill in this entire document. If you skip the safety gear because it's hot outside or you're "just making one quick cut," this skill isn't for you yet.

```agent-adaptation
# Localization note -- chainsaw safety principles are universal. Regulations and standards vary.
# Agent must follow these rules when working with non-US users:
- PPE requirements, felling techniques, and safety protocols are universal -- apply everywhere.
- Substitute US-specific references with local equivalents:
  US: OSHA chainsaw safety standards
  UK: HSE (Health and Safety Executive) forestry guidelines
  Australia: Safe Work Australia forestry code of practice
  Canada: Canadian Centre for Occupational Health and Safety (CCOHS)
  EU: EN ISO 11681 chainsaw safety standards
- Professional certification programs vary by country:
  US: Game of Logging, TCIA
  UK: NPTC chainsaw certificates (CS30, CS31, etc.)
  Australia: Certificate II in Forest Growing and Management
  Canada: BC Forest Safety Council, provincial equivalents
- Tree felling permits and protected species laws vary by jurisdiction.
  Agent must advise user to check local council/municipality rules before felling.
- Emergency services number: US 911, UK 999, AU 000, EU 112.
```

## Sources & Verification

- **OSHA chainsaw safety standards** -- federal workplace safety requirements for chainsaw operation. [osha.gov/chain-saws](https://www.osha.gov/chain-saws)
- **USDA Forest Service chainsaw training materials** -- government felling protocols used by wildland firefighters and forestry crews. [fs.usda.gov](https://www.fs.usda.gov/)
- **Stihl safety guidelines** -- manufacturer PPE and operational requirements. [stihlusa.com/safety](https://www.stihlusa.com/safety/)
- **Game of Logging** -- professional felling training program, the gold standard for civilian chainsaw education. [gameoflogging.com](https://www.gameoflogging.com/)
- **Tree Care Industry Association (TCIA)** -- professional arborist standards and safety data. [tcia.org](https://www.tcia.org/)

## When to Use

- User needs to fell a tree on their property
- User is cutting firewood and needs safe technique
- User is clearing storm damage with downed trees and branches
- User is buying their first chainsaw and needs guidance on selection and safety
- User needs to limb or buck fallen trees
- User is unsure whether a tree job requires a professional

## Instructions

### Step 1: Determine if This Is a DIY Job or a Professional Job

**Agent action**: Before any chainsaw instruction, screen the situation. If any of the following conditions are true, STOP and direct the user to hire a certified arborist.

```
CALL A PROFESSIONAL IF ANY OF THESE ARE TRUE:

-> Tree is within two tree-lengths of a power line
-> Tree requires climbing to access (NEVER climb with a chainsaw without
   professional training and equipment)
-> Tree is leaning toward a building, fence, or structure
-> Tree is hung up in another tree ("widow maker" -- extremely dangerous)
-> Tree is dead and has been standing for a long time (unpredictable
   structural integrity, branches fall without warning)
-> Tree diameter is over 18 inches and you have fewer than 10 felling cuts
   of experience
-> You are not sure about the lean direction
-> The tree has multiple trunks or major forks
-> You would need to fell the tree uphill
-> Any situation where you feel uncertain -- that feeling is correct

HOW TO FIND A PRO:
-> Search "ISA certified arborist" + your area
-> Verify credentials at treesaregood.org/findanarborist
-> Get 2-3 quotes. Expect $200-2000+ depending on size and complexity.
-> Confirm they carry liability insurance and workers' comp.
```

### Step 2: PPE -- Non-Negotiable Equipment

**Agent action**: Walk the user through required protective equipment. Do not proceed to cutting techniques until PPE is confirmed.

```
REQUIRED PPE (all of it, every time):

CHAINSAW CHAPS OR PANTS -- $40-80
-> Layers of cut-resistant fiber that jam the chain on contact
-> The single most important piece of chainsaw PPE
-> Must cover front of legs from waist to boot top
-> Replace after any contact with a running chain (they're single-use
   in the impact zone)

HELMET WITH FACE SCREEN AND EAR PROTECTION -- $30-50
-> Combination unit: hard hat + mesh face screen + ear muffs
-> Stihl, Husqvarna, and Oregon all make good combo units
-> Face screen stops wood chips and debris at chain speed
-> Ear protection prevents hearing damage (chainsaws run 100-115 dB)

STEEL-TOE BOOTS -- $60-150
-> Logging boots with steel toe and cut-resistant uppers ideal
-> At minimum: steel-toe work boots with ankle support
-> No sneakers, sandals, or regular shoes. Ever.

GLOVES -- $15-30
-> Cut-resistant gloves with grip
-> Not bulky winter gloves (you need to feel the controls)
-> Left hand is the most common injury site

FITTED CLOTHING
-> Nothing loose: no scarves, no hoodie strings, no baggy sleeves
-> Long pants (under chaps), long sleeves
-> Clothing should not be so tight it restricts movement

EYE PROTECTION (if no face screen)
-> Safety glasses or goggles as backup
```

### Step 3: Chainsaw Selection and Maintenance

**Agent action**: Help the user select the right saw for their needs and establish a maintenance routine.

```
CHAINSAW SELECTION:

BAR LENGTH:
-> 16" bar -- right for most homeowners. Handles trees up to 12" diameter
   (you can cut from both sides for up to 24" trees with experience)
-> 18-20" -- for regular firewood cutting and medium trees
-> 14" or smaller -- limbing, light cleanup
-> Rule: don't buy bigger than you need. Longer bar = heavier = more
   kickback force = more fatigue = more danger

ENGINE TYPE:
-> Electric (corded or battery) -- for occasional limbing, small cleanup,
   branches under 6". Less kickback, lighter, quieter. Good starter saw.
-> Gas -- for felling, regular firewood, storm cleanup. More power,
   no cord limit, runs longer. Requires fuel mixing (2-stroke) or
   straight gas (4-stroke, less common).

CHAIN TYPES:
-> Low-kickback chain -- comes standard on consumer saws. Slower cut but
   significantly safer. USE THIS until you have real experience.
-> Full-chisel chain -- cuts faster, kicks back harder. Professional use.
-> Semi-chisel -- good middle ground for dirty wood and firewood.

MAINTENANCE (do these or the saw becomes dangerous):

CHAIN TENSION -- check before every use
-> Lift chain at mid-bar: should pull up slightly and snap back
-> Too loose: chain can derail and whip off the bar
-> Too tight: overheats, wears prematurely, can break

CHAIN SHARPENING -- every tank of fuel, or when you see sawdust instead
of chips
-> Round file matched to chain gauge (stamped on chain or in manual)
-> Follow factory angle (usually 25-35 degrees)
-> Same number of strokes on each cutter
-> File from inside to outside
-> A dull chain makes you push harder, which causes fatigue and accidents

BAR OIL -- refill every time you refuel
-> The chain needs constant lubrication
-> Running dry destroys the bar and chain in minutes

FUEL (gas saws)
-> 2-stroke: premixed fuel ($8/can) or mix yourself (50:1 ratio typically)
-> NEVER put straight gas in a 2-stroke engine -- destroys it in minutes
-> Use fuel stabilizer or drain tank for storage over 30 days
```

### Step 4: The 5-Step Felling Plan

**Agent action**: Walk through each step of the felling plan. Emphasize that every step must be completed before the saw starts.

```
THE 5-STEP FELLING PLAN:

STEP 1: ASSESS THE LEAN
-> Stand back and look at the tree from two directions 90 degrees apart
-> Natural lean determines the easiest felling direction
-> Check for dead branches overhead ("widow makers")
-> Check wind direction and speed -- don't fell in strong wind
-> Look for obstacles in the fall zone (other trees, structures, vehicles)
-> Felling with the lean is safest. Against the lean requires wedges
   and experience.

STEP 2: CLEAR YOUR ESCAPE ROUTES
-> Two routes: 45 degrees behind the tree, on both sides of the fall
-> Clear brush, branches, and tripping hazards along both routes
-> You WILL use one of these routes. Make sure you can move fast.
-> Never stand directly behind the falling tree (butt can kick back)
-> Never stand in the fall zone

STEP 3: THE NOTCH CUT (face cut, on the side facing the fall direction)
-> Conventional notch: horizontal cut 1/3 into trunk, then angled
   cut from above to meet it (creates a 45-degree wedge)
-> Open-face notch: two angled cuts meeting at 70+ degrees (preferred
   by professionals -- tree falls more predictably)
-> Notch depth: about 1/4 to 1/3 of trunk diameter
-> The notch determines fall direction. Get this right.

STEP 4: THE BACK CUT (opposite side from the notch)
-> Start the back cut 1-2 inches ABOVE the floor of the notch
-> Cut toward the notch but STOP before cutting through
-> Leave a hinge of uncut wood (about 10% of trunk diameter)
-> The hinge controls the fall direction -- cutting through it
   means the tree can fall anywhere
-> If the tree starts to pinch your bar, insert a felling wedge
   (plastic, never metal -- metal + chain = disaster)

STEP 5: RETREAT
-> When the tree begins to move, REMOVE THE SAW
-> Walk (don't run) along your escape route
-> Watch the tree as you move -- the butt can jump or roll
-> Keep watching even after it lands -- branches can snap and fly
-> Wait until everything stops moving before approaching
```

### Step 5: Limbing and Bucking

**Agent action**: Cover safe techniques for processing a felled tree.

```
LIMBING (removing branches from the trunk):

-> Work from the butt end toward the top
-> Stand on the uphill side whenever possible
-> Keep the trunk between you and the saw when practical
-> Watch for REACTIVE FORCES: branches under tension from the tree's
   weight will spring when cut. Identify which direction the force
   will release before cutting.
-> Cut branches close to the trunk in a single motion
-> Small branches: one cut from the top
-> Large branches under tension: undercut first to prevent bark tear,
   then top cut

BUCKING (cutting the trunk into logs):

-> Assess the log's support points before cutting
   - Supported at both ends: cut from top down (compression on top)
     but stop at 1/3 depth, roll log, finish from the other side
   - Supported at one end: cut from bottom up (tension on bottom)
     to prevent pinching the bar
-> Never cut with the tip of the bar in contact with wood (kickback zone)
-> If the log is on the ground: cut from the top, stop before you hit
   dirt (dulls the chain instantly). Roll and finish from the other side.
-> Standard firewood length: 16 inches (fits most wood stoves and
   fireplaces). Measure and mark before cutting.

KICKBACK -- THE SINGLE MOST DANGEROUS THING:
-> The upper quadrant of the bar tip is the KICKBACK ZONE
-> If this part contacts wood, the bar kicks up and back toward you
   faster than you can react
-> NEVER let the tip contact anything
-> NEVER start a cut with the tip
-> NEVER cut above shoulder height
-> Keep a firm grip with both hands -- left hand wrapping the front
   handle with thumb underneath
-> Chain brake: your left wrist hits it if the saw kicks back.
   Test it before every use.
```

### Step 6: Storm Cleanup Specifics

**Agent action**: Provide protocols specific to storm damage scenarios.

```
STORM CLEANUP -- ADDITIONAL HAZARDS:

-> Downed power lines: ASSUME ALL WIRES ARE LIVE. Stay 35+ feet away.
   Call your utility company. Do not touch anything touching the wire.
   Do not touch anything touching something touching the wire. Electricity
   can travel through wet ground.
-> Trees on structures: do NOT try to remove them yourself. The tree
   may be the only thing holding the structure together. Call a pro.
-> Trees under tension: storm-damaged trees are loaded with stored
   energy. Branches and trunks can snap unpredictably. Work slowly,
   assess tension direction before every cut.
-> Spring-poles: bent saplings or branches pinned under debris.
   Extremely dangerous -- they release like a catapult when freed.
   Cut from the side, never stand in the release path.
-> Flooded ground: unstable footing makes chainsaw work more dangerous.
   Wait for ground to dry if possible.
-> Fatigue: storm cleanup often involves long days. Tired people make
   mistakes. Quit while you can still focus.

DIAMETER LIMITS FOR BEGINNERS:
-> Nothing over 12" diameter until you have at least 5 supervised
   felling cuts
-> Nothing over 18" diameter until you have significant experience
-> Nothing that requires more than your bar length without cutting
   from both sides
```

## If This Fails

- **Tree didn't fall in the intended direction?** If the tree is hung up in another tree, DO NOT try to push it, pull it, or cut the supporting tree. This is one of the most dangerous situations in forestry. Call a professional with rigging equipment.
- **Chain keeps binding in the cut?** You're misreading the tension/compression. Re-assess which side of the log is under compression (cut from that side first) and which is under tension.
- **Saw won't start or runs poorly?** See the small-engine-repair skill for troubleshooting fuel, spark, and air problems.
- **PPE too expensive?** Chainsaw chaps are $40 on Amazon. A trip to the ER starts at $3,000. This is not optional.
- **User insists on skipping safety steps?** Agent should refuse to provide cutting instructions without PPE confirmation. State plainly: "I can't walk you through chainsaw operation without safety equipment. The risk of life-altering injury is too high."

## Rules

- Never provide cutting instructions until PPE is confirmed
- Always screen for professional-required situations before giving DIY guidance
- Never encourage felling near power lines under any circumstances
- If the user describes a situation that sounds dangerous and beyond their skill level, say so directly
- Do not soften safety warnings to be polite -- clarity saves limbs and lives
- Link to small-engine-repair for saw maintenance beyond basic chain and bar care

## Tips

- A sharp chain does the work. If you're pushing the saw into the wood, the chain is dull. Stop and sharpen.
- Bore cuts (plunge cuts with the lower tip of the bar) are an advanced technique for large or hazardous trees. Don't attempt without hands-on training.
- Carry a plastic felling wedge and a small sledge. A wedge in the back cut prevents pinching and helps direct the fall.
- Cut firewood in winter when possible -- fewer leaves means better visibility, cold wood cuts cleaner, and there's no wasp risk.
- If you're new, take a Game of Logging Level 1 class ($150-250 for a day). It's the single best investment in chainsaw safety.
- Keep a first aid kit with a tourniquet in your work area. Chainsaw injuries bleed fast.
- Two people is always better than one for felling. The second person watches from a safe distance and can call for help.
- Fuel up and oil up at the same time. If you run out of bar oil before fuel, the chain and bar overheat.

## Agent State

```yaml
state:
  user_experience:
    chainsaw_experience_level: null  # none, beginner, intermediate, experienced
    previous_training: null
    saw_owned: null
    saw_type: null  # electric, gas
    bar_length: null
  current_task:
    task_type: null  # felling, limbing, bucking, firewood, storm_cleanup, purchasing
    tree_diameter: null
    near_structures: null
    near_power_lines: null
    lean_direction: null
    professional_required: null
  safety_check:
    ppe_confirmed: false
    chaps: false
    helmet_face_ear: false
    steel_toe_boots: false
    gloves: false
    escape_routes_cleared: false
  equipment:
    chain_sharp: null
    chain_tension_checked: null
    bar_oil_level: null
    fuel_level: null
    chain_brake_tested: null
```

## Automation Triggers

```yaml
triggers:
  - name: professional_required_screen
    condition: "current_task.near_power_lines IS true OR current_task.near_structures IS true OR current_task.tree_diameter > 18"
    action: "Based on what you've described, this job needs a certified arborist. Trees near power lines, structures, or over 18 inches diameter are beyond safe DIY range. Let me help you find a professional instead."

  - name: ppe_check
    condition: "current_task.task_type IS SET AND safety_check.ppe_confirmed IS false"
    action: "Before we get into technique, let's confirm your safety gear. Do you have chainsaw chaps, a helmet with face screen and ear protection, steel-toe boots, and gloves? All of these are required -- no exceptions."

  - name: beginner_diameter_warning
    condition: "user_experience.chainsaw_experience_level IS 'beginner' AND current_task.tree_diameter > 12"
    action: "That tree is over 12 inches in diameter. For someone at your experience level, I'd strongly recommend getting hands-on guidance from an experienced operator or hiring a pro for this one. Building up to larger trees keeps you safe."

  - name: maintenance_reminder
    condition: "equipment.chain_sharp IS 'dull' OR equipment.chain_tension_checked IS false"
    action: "Your chain needs attention before you cut. A dull or loose chain is significantly more dangerous than a maintained one. Let's go through the maintenance checklist first."

  - name: storm_safety_screen
    condition: "current_task.task_type IS 'storm_cleanup'"
    action: "Storm cleanup has extra hazards -- downed power lines, trees under unpredictable tension, and spring-poles. Let's walk through the storm-specific safety checks before you start cutting."
```
