# Profile Families

Taxonomy for describing espresso profile behavior without depending on specific community profile names.

## Contents
- Purpose
- Why families instead of names?
- How to use this taxonomy
- Family entry template
- Traditional / straight espresso
- Fill-and-soak / preinfusion-led
- Blooming
- Lever-like / declining pressure
- Turbo / allongé / low-pressure fast-flow
- Filter-style low-pressure
- Soup / ultra-low-pressure high-flow
- Adaptive / resistance-led
- Cross-family cautions
- Relationship to local mapping

## Purpose

Use this file to classify a shot or a recipe into a **family** first, then interpret behavior through that family.

This lets the skill stay useful even when:
- profile names differ between machines,
- community recipes get renamed,
- the same family appears in several implementations,
- a user knows the behavior they want, but not the exact profile name.

This file is especially useful for graph interpretation, conceptual profile advice, and family-level reasoning.
When real-shot analysis already has a named profile plus phase data, family should usually be used as an **interpretation layer** after the profile-specific execution replay, not as the first execution verdict.

## Why families instead of names?

Named profiles are unstable. Families are more stable, more teachable, and easier to publish.

A named profile can usually be understood by asking:
1. How is the puck wetted?
2. Is the shot primarily pressure-led, flow-led, or soak-led?
3. Is the drink aiming for body, clarity, or a balance?
4. Does the profile want stable pressure, declining pressure, fast low-pressure flow, or ultra-low-pressure extraction?

## How to use this taxonomy

When diagnosing a shot:
1. Identify the intended family.
2. Judge whether the actual graph matches the family’s intended behavior.
3. Only then decide whether the shot was too fine, too coarse, too uneven, or simply using the wrong family for the coffee.

Do **not** judge every graph by traditional 9-bar espresso expectations.
A turbo, blooming shot, soup brew, or filter-style profile can look “wrong” by traditional standards while still behaving exactly as intended.

## Family entry template

Each family is described by:
- definition
- target flavor style
- phase structure
- expected graph behavior
- best-fit coffees / goals
- too-fine signs
- too-coarse signs
- common misreadings
- neighboring families and boundaries

---

## 1. Traditional / straight espresso

### Definition
A relatively direct espresso profile with short wetting, fast pressure build, and a main percolation phase that stays near its intended brew pressure.

### Target flavor style
- concentrated
- body-forward
- familiar espresso texture
- strong milk-drink compatibility

### Typical phase structure
- short fill / wetting
- quick ramp to brew pressure
- hold or mostly stable main extraction
- optional light taper near the end

### Expected graph behavior
- pressure rises quickly to a moderate or high brewing zone
- flow stabilizes under puck resistance
- extraction looks compact rather than extended
- pressure decline, if present, is small compared with lever-like families

### Best fit
- medium to darker roasts
- coffees where body matters more than maximum clarity
- users wanting a classic espresso experience

### Too-fine signs
- pressure pins high too early
- flow starves or struggles to establish
- shot tastes harsh, dry, or paradoxically underdeveloped despite long time
- channeling risk increases because the puck is highly stressed

### Too-coarse signs
- pressure never meaningfully reaches the intended zone
- shot gushes early
- cup tastes weak, sour, or empty

### Common misreadings
- assuming every good espresso must have a long declining pressure curve
- assuming any lack of taper means failure
- assuming a soupy puck automatically means the shot was bad

### Boundaries
- if wetting and soak become deliberate design features, this moves toward **Fill-and-soak / preinfusion-led**
- if the main signature is a smooth, intentional pressure decline, it moves toward **Lever-like / declining pressure**

---

## 2. Fill-and-soak / preinfusion-led

### Definition
A family that deliberately uses an initial wetting phase plus a short soak / hold to improve puck integrity before the main extraction phase.

### Target flavor style
- improved evenness
- gentler transition into percolation
- more forgiveness than a direct straight shot
- balanced body with cleaner structure

### Typical phase structure
- fill: wet the puck and build initial resistance
- soak: reduce or stop flow, or hold low pressure
- percolation: ramp into the main extraction target
- optional taper

### Expected graph behavior
- early pressure rise is modest rather than explosive
- a visible pause, hold, or pressure drop may appear before the main ramp
- main extraction should start more evenly than in a direct profile

### Best fit
- lighter or denser coffees
- grinders that produce more fines
- setups where puck integrity is a recurring issue
- users who want more margin before full extraction pressure arrives

### Too-fine signs
- soak phase becomes sticky or over-compressed
- the main ramp slams upward too hard after soak
- flow stays stubbornly low and the cup becomes muddy or harsh

### Too-coarse signs
- the soak phase offers too little resistance
- early drips appear too easily
- the transition into main percolation feels premature and hollow

### Common misreadings
- reading pressure drop during soak as failure rather than intended relaxation
- assuming lack of immediate output means the shot is choking
- using straight-espresso expectations to judge a deliberate soak phase

### Boundaries
- if the soak is brief and supportive, this family applies
- if the soak / bloom becomes long and central to extraction design, it moves toward **Blooming**

---

## 3. Blooming

### Definition
A family that intentionally adds a stronger hold / bloom phase after the puck has been wetted, allowing the bed to rest, equilibrate, and begin extraction before the main percolation phase.

### Target flavor style
- high extraction potential
- better saturation of dense coffees
- often more sweetness and extraction depth
- clarity or blending depends on what follows the bloom

### Typical phase structure
- fast or moderate fill
- pronounced bloom / hold / pressure fall
- main extraction after bloom
- optional taper

### Expected graph behavior
- an early rise in pressure or added water mass
- a visible bloom period where pressure falls or rests low
- later recovery into meaningful percolation
- overall extraction is often longer or structurally more staged than a straight shot

### Best fit
- light roasts
- dense coffees
- coffees that taste persistently underextracted on direct profiles
- situations where even wetting is more important than speed

### Too-fine signs
- the bloom does not set up a clean percolation phase afterward
- the puck seems compressed rather than relaxed
- late extraction becomes unstable or jagged
- the cup gets bitter-dry while still lacking openness

### Too-coarse signs
- too much liquid escapes during bloom
- bloom fails to create enough resistance for a meaningful main extraction
- cup tastes diluted, thin, or underdeveloped

### Common misreadings
- assuming any liquid during bloom means failure
- assuming long total shot time means overextraction by default
- ignoring the fact that extraction is already happening during bloom

### Boundaries
- if the bloom is the defining feature and extraction is built around it, this family applies
- if the brew is still mostly a direct shot with a short settling phase, it may be better described as **Fill-and-soak / preinfusion-led**
- if the post-bloom phase is intentionally low-pressure and fast-flow for clarity, it may border **Turbo / allongé**

---

## 4. Lever-like / declining pressure

### Definition
A family whose signature is a front-loaded extraction followed by a smooth, intentional decline in pressure through the body of the shot.

### Target flavor style
- integrated sweetness
- syrupy or rounded texture
- classical espresso feel with softer finish
- body without requiring a rigid high-pressure hold

### Typical phase structure
- fill or wetting
- ramp to higher early pressure
- sustained but declining extraction pressure
- late gentle taper or natural finish

### Expected graph behavior
- pressure rises quickly
- pressure then declines smoothly rather than holding flat
- the decline should look intentional and continuous, not like a collapse
- flow usually increases modestly as resistance falls

### Best fit
- medium to medium-dark coffees
- users wanting sweetness and texture over maximum acidity expression
- coffees that feel too aggressive on constant high pressure

### Too-fine signs
- pressure stays pinned too high and refuses to decline
- the family loses its defining “slope” and behaves like a stalled straight shot
- cup becomes dense, harsh, or over-compressed

### Too-coarse signs
- pressure collapses too early
- the intended decline turns into a fall-off
- cup tastes thin, weak, or prematurely exhausted

### Common misreadings
- assuming all pressure decline is channeling
- treating a healthy late decline as a problem
- confusing normal resistance loss with shot failure

### Boundaries
- if pressure is mostly held flat, it belongs closer to **Traditional / straight espresso**
- if the decline occurs because the shot is actually flow-targeted and low-pressure, it may belong closer to **Turbo / allongé** or **Adaptive / resistance-led**

---

## 5. Turbo / allongé / low-pressure fast-flow

### Definition
A family built around lower pressure, faster percolation, and longer ratios than classic espresso, usually to increase clarity and reduce over-compression.

### Target flavor style
- higher clarity
- brighter acidity
- lighter texture than traditional espresso
- often more forgiving at lower pressure when the grind and puck are appropriate

### Typical phase structure
- direct or short setup
- low-to-moderate pressure main extraction
- fast percolation
- longer ratio than a classic straight shot
- taper optional, often minimal

### Expected graph behavior
- pressure commonly sits below classic espresso territory
- flow is relatively fast compared with traditional shots
- total time can be short even when the shot tastes good
- the graph may look “underpressured” if judged by old espresso rules

### Best fit
- light roasts
- clarity-focused goals
- coffees that taste harsh under high pressure
- users exploring lower-pressure extraction styles

### Too-fine signs
- pressure rises too high for the family
- flow slows so much that the profile stops behaving like a turbo / allongé
- cup can taste oddly harsh, dry, or simultaneously underdeveloped and rough

### Too-coarse signs
- cup becomes weak, watery, or structurally empty
- pressure never develops enough resistance to carry flavor

### Common misreadings
- assuming fast shot = bad shot
- assuming low pressure = underextraction by definition
- confusing successful fast flow with a gusher
- assuming any preinfusion or short bloom automatically means the shot no longer belongs to the turbo/allongé family

### Boundaries
- a short setup phase does **not** automatically move a profile out of the turbo/allongé family
- if the setup phase becomes the dominant identity of the shot, it may belong closer to **Fill-and-soak / preinfusion-led** or **Blooming**
- if pressure is extremely low and the brew relies on a very gentle soak plus coarse grind, it may be **Soup / ultra-low-pressure high-flow**
- if the shot stretches into a very low-pressure, filter-like beverage, it may border **Filter-style low-pressure**

---

## 6. Filter-style low-pressure

### Definition
A family that uses very low pressure and longer, more open extraction design to produce a cup that expresses coffee more like concentrated filter than like classical espresso.

### Target flavor style
- high transparency
- low or moderate body
- long, open, articulate cup structure
- less emphasis on syrupy concentration

### Typical phase structure
- gentle start
- very low-pressure main extraction
- often longer ratio and longer overall extraction design
- may include deliberate low-flow holds or elongated percolation

### Expected graph behavior
- pressure remains low for much of the shot
- the shot may look “underpowered” to a traditional espresso observer
- flow can be controlled and calm rather than forceful
- ratios tend to extend beyond traditional espresso expectations

### Best fit
- light roasts
- coffees with interesting acidity or aromatic complexity
- users seeking filter-like clarity from espresso hardware

### Too-fine signs
- pressure rises above what the family is meant to sustain
- cup becomes muddy, heavy, or bitter instead of open
- the profile drifts back toward straight espresso behavior

### Too-coarse signs
- cup becomes empty and sour
- structure is lost rather than clarified
- extraction feels incomplete rather than intentionally transparent

### Common misreadings
- assuming low pressure means low quality
- assuming long ratio always means dilution rather than a chosen strength/extraction balance
- confusing low body with low extraction by default

### Boundaries
- if the extraction is still fairly fast and clearly turbo-like, it may belong under **Turbo / allongé / low-pressure fast-flow**
- if pressure is almost absent and the brew relies on a very gentle soak plus a coarse grind, it may belong under **Soup / ultra-low-pressure high-flow**

---

## 7. Soup / ultra-low-pressure high-flow

### Definition
A family built around an extremely gentle soak, coarse grind, and ultra-low-pressure, high-flow extraction. Its goal is to preserve puck openness, avoid compression, and maximize a very light, clarity-driven cup structure.

### Target flavor style
- very high clarity
- juicy or sparkling acidity when well executed
- light body
- low compression and low muddiness

### Typical phase structure
- very gentle soak / wetting
- minimal pressure build, often near-zero to very low pressure
- relatively high flow once extraction begins in earnest
- often longer beverage style than classical espresso

### Expected graph behavior
- pressure is much lower than a turbo, often dramatically so
- the shot relies more on keeping the puck open than on forcing pressure through it
- grind is coarser than most espresso families
- fast flow is part of the design, not an error state

### Best fit
- coffees that benefit from extreme clarity
- users exploring the outer edge of low-pressure espresso-like brewing
- situations where high pressure is clearly making the coffee worse

### Too-fine signs
- soak requires too much force or resistance
- pressure builds too much for the family concept
- the brew stops behaving like an open, low-compression extraction
- clarity collapses into muddiness or bitterness

### Too-coarse signs
- the puck offers so little structure that the brew falls out of the family entirely
- water passes too freely too early
- the cup becomes weak, empty, or disconnected

### Common misreadings
- assuming it is just a failed turbo or failed espresso
- assuming coarse grind means poor dialing rather than intentional family design
- assuming low pressure means the brew is incomplete

### Boundaries
- compared with **Turbo / allongé**, soup usually runs at even lower pressure and depends more strongly on gentle soak and coarse-grind boundary management
- compared with **Filter-style low-pressure**, soup is more explicitly high-flow and open rather than simply extended and low-pressure

### Placement note
This file only keeps the family summary.
If Local later needs detailed treatment of soup-specific logic, add a dedicated `soup.md` rather than importing device-specific ORB procedure into the family taxonomy.

---

## 8. Adaptive / resistance-led

### Definition
A family whose behavior is intentionally broad, forgiving, or responsive to puck resistance rather than rigidly expressing one fixed line or aesthetic shape.

### Target flavor style
- usable across a wider range of coffees
- forgiving and drinkable
- less dependent on hitting one exact graph shape
- often chosen for flexibility rather than purity of style

### Typical phase structure
- variable; may mix pressure-led and flow-led ideas
- often designed to remain drinkable across different puck resistances
- may intentionally allow the shot to evolve with the puck rather than forcing a fixed shape

### Expected graph behavior
- the graph may have more than one acceptable form
- there is often a wider tolerance band for “successful” behavior
- rigid comparison to a single target line can be misleading

### Best fit
- users wanting robustness
- coffees that vary significantly day to day
- setups where repeatability is less important than consistent drinkability

### Too-fine signs
- the profile sits on its limits too often
- the supposed flexibility collapses into a stressed, over-restricted shot
- the cup becomes compressed and harsh

### Too-coarse signs
- the profile never gains enough traction to produce meaningful structure
- the shot feels weak or underbuilt rather than adaptable

### Common misreadings
- treating every deviation from a notional target line as failure
- assuming a broader tolerance means the profile has no logic
- confusing “forgiving” with “random”

### Boundaries
- if the profile is actually just a fixed blooming, declining, or turbo design with a modern name, map it to the simpler family instead
- use this family only when the behavior is genuinely broader or intentionally resistance-led

---

## Cross-family cautions

### 1. Do not overfit by name
A profile with a dramatic name may still be a straightforward member of a familiar family.
Classify behavior first, name second.

### 2. Do not overfit by pressure alone
The same pressure number can mean very different things depending on:
- grind,
- flow target,
- soak structure,
- ratio,
- family intent.

### 3. A “good” graph depends on the family
- flat high pressure is normal in some traditional designs
- a smooth decline is normal in lever-like designs
- low pressure is normal in turbo/filter-style/soup families
- a visible soak is normal in fill-and-soak or blooming designs

### 4. Use family before troubleshooting
If a user says “the graph looks wrong,” first ask:
- What family was this supposed to be?
- What did the cup taste like?
- Was the deviation from family intent or from old espresso expectations?

## Relationship to local mapping

This file is the **public taxonomy**.
Machine-specific named profile mappings should live in `references/profile-mapping.md`.
