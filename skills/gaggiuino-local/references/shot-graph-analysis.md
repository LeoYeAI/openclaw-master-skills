# Shot Graph Analysis

Framework for reading pressure / flow / temperature / weight curves and screenshots.

## Contents
- Purpose
- Core principles
- Strong vs weak evidence
- Read order
- Pressure reading
- Flow reading
- Temperature reading
- Weight / yield reading
- Phase transitions
- Common graph patterns
- Family-specific quick notes
- When the image is weak
- What not to do
- Final rule of thumb

## Purpose

Use this file when the user provides:
- a graph screenshot,
- a machine screen photo,
- a web UI curve image,
- a partial shot summary,
- or a visual description of the shot.

This file is for **public, family-aware graph interpretation**.
Its first job is not just to describe the lines, but to judge whether the visible result appears to express the intended family.
If real Gaggiuino shot telemetry is available, use this together with `analysis-protocol.md`, and let the telemetry outrank the picture.

---

## Core principles

### 1. Identify the intended family first
Before calling a graph “good” or “bad”, ask:
- what was the shot trying to be?
- which family was intended?
- was the goal body, clarity, sweetness, or a filter-like expression?

A graph that would be a failure in traditional straight espresso may be perfectly normal in:
- blooming,
- lever-like declining pressure,
- turbo / allongé,
- filter-style low-pressure,
- soup,
- or adaptive families.

### 2. Read the graph in a fixed order
A reliable order is:
1. pressure
2. flow
3. temperature
4. weight / yield
5. transitions between phases
6. taste report from the user

### 3. Do not diagnose from one line alone
A shot can look wrong on one axis and still be working overall.
Examples:
- fast flow can be healthy in turbo or soup
- pressure decline can be healthy in lever-like or flow-led extractions
- low pressure can be exactly the point in filter-style or soup families

### 4. Taste still matters, but not before family expression
Taste is part of the judgment, but it is not the first question.
First ask whether the shot appears to express its intended family.
Then ask whether that expression produced the taste the user actually wants.

A cup can taste good while still not being the expression the profile was trying to produce.
A shot can also express the family coherently and still be worth changing for taste reasons.

---

## Strong evidence vs weak evidence

### Stronger evidence
- full telemetry
- clearly labeled pressure / flow / temp / weight curves
- visible time axis
- known intended profile family
- user-reported taste

### Weaker evidence
- blurry machine screen photos
- cropped images with no axis labels
- pressure-only screenshots
- bottomless videos without numeric context
- late-shot screenshots without the opening phases

### Practical rule
If a screenshot and real shot data disagree, trust the real shot data.

---

## Quick family reference

Use this only as a fast orientation aid.
Detailed family definitions live in `profile-families.md`.

### Traditional / straight espresso
- quick pressure build
- relatively stable brew pressure
- moderate resisted flow
- compact extraction shape

### Fill-and-soak / preinfusion-led
- early wetting
- pause, hold, or drop before full extraction
- gentler start than a direct shot

### Blooming
- visible early setup
- delayed main extraction
- longer total shot structure
- pressure may fall during bloom before recovery

### Lever-like / declining pressure
- strong early pressure
- smooth slope downward during main extraction
- gradual resistance loss

### Turbo / allongé / low-pressure fast-flow
- lower pressure than traditional espresso
- faster flow
- cleaner, more open cup structure

### Filter-style low-pressure
- very low pressure
- longer ratio
- transparent, less syrupy expression

### Soup / ultra-low-pressure high-flow
- almost no meaningful pressure build by espresso standards
- very open puck behavior
- fast flow after soaking is complete

### Adaptive / resistance-led
- broader tolerance in graph shape
- multiple acceptable trajectories
- less dependence on one iconic line shape

---

## Step 1: Read pressure first

Pressure is the easiest high-level orientation tool, but also the easiest one to overread.

## What to look for

### A. How fast does pressure build?
Ask:
- does pressure rise immediately?
- does it rise after a deliberate soak?
- does it build at all?
- does it slam into a limit too early?

#### Pressure builds too fast
Usually suggests one of:
- grind too fine
- too much early puck stress
- family setup too aggressive for the coffee
- insufficient soak / wetting for what the coffee needed

Can lead to:
- harshness
- jagged extraction
- unstable flow later

#### Pressure builds too slowly
Usually suggests one of:
- grind too coarse
- the setup phase is too permissive
- the family is too open for the chosen dose / grind
- insufficient puck resistance for the intended style

Can lead to:
- weak structure
- sourness
- hollow cups

### B. What happens in the main body of the shot?
This depends entirely on family.

#### Healthy pressure hold
Often normal in:
- traditional / straight espresso
- some direct pressure-led shots

#### Healthy pressure decline
Often normal in:
- lever-like families
- some flow-led profiles
- some late-stage extractions where resistance naturally falls

#### Healthy low pressure
Often normal in:
- turbo / allongé
- filter-style low-pressure
- soup

### C. Does pressure collapse suddenly?
A sudden drop is more suspicious than a smooth decline.

Sudden pressure collapse may suggest:
- puck fracture
- severe channeling
- transition failure
- grind too coarse for the intended family
- abrupt resistance loss from an already unstable puck

### D. Is pressure pinned too high for too long?
This often means the shot is over-restricted relative to its intended family.

Possible causes:
- grind too fine
- dose too high
- too aggressive family for the coffee
- trying to force a lever-like or turbo-ish result with a rigid pressure-heavy setup

---

## Step 2: Read flow second

Flow often tells you whether the family is actually expressing itself.

## What to look for

### A. Stable versus unstable flow
Stable flow usually means the puck is behaving coherently.
Unstable flow usually means the puck or family setup is fighting itself.

### B. Is the flow appropriate for the family?
Ask whether the flow behavior fits the intended family.

Examples:
- traditional should look resisted rather than open
- fill-and-soak or blooming should not show heavy early percolation during the setup stage
- turbo should stay fast without collapsing into emptiness
- filter-style should stay open without turning hollow
- soup should stay very open at very low pressure rather than drifting back into pressured espresso behavior

### C. Flow spike
A sudden flow spike is often suspicious.
It can indicate:
- channeling
- puck fracture
- a late structural failure
- a transition that happened too abruptly

But context matters.
Late acceleration in a healthy low-pressure family is not automatically failure.

### D. Flow starvation
If flow remains too low for the family, ask whether:
- the grind is too fine,
- pressure is too high,
- the puck was over-compressed,
- or the chosen family no longer matches the coffee.

---

## Step 3: Read temperature third

Temperature is often less visually dramatic than pressure or flow, but it can explain a lot of taste.

## What to look for

### A. Stability near the intended setpoint
Small movement is normal.
Big drift deserves attention.

### B. Thermal sag
A downward sag during the main extraction may matter more when the shot is:
- long,
- high-flow,
- high-yield,
- or working near the limits of the machine’s thermal stability.

Thermal sag can contribute to:
- flattening,
- underdevelopment,
- a weird fade from promising to dull.

### C. Overshoot
If temperature is meaningfully too high, the cup may become:
- bitter,
- harsh,
- sharp in a bad way,
- or less transparent.

### D. Family context again matters
A filter-style or soup-ish extraction may expose thermal instability differently from a short straight shot.
Longer or more open families often make thermal limitations easier to taste.

---

## Step 4: Read weight / yield fourth

Weight tells you whether the shot structure actually produced a usable beverage format.

## What to look for

### A. Smooth accumulation
Usually suggests the shot progressed coherently.

### B. Jumps or impossible transitions
Can indicate:
- scale noise
- phase trigger issues
- visual crop problems
- real instability if paired with pressure / flow chaos

### C. Ratio relative to family
Ask whether the final beverage size matches the intended style.

Examples:
- a short ratio in a clarity-heavy family may feel too narrow and sharp
- a long ratio in a heavy traditional family may feel over-extended
- a soup brew judged by classic output ratio expectations may be misunderstood entirely if the user is thinking in input ratio terms

---

## Step 5: Look for phase transitions

Many problems are really transition problems.

### Transition types to watch
- fill → soak
- soak → main extraction
- main extraction → taper
- pressure-led → flow-led behavior

### Healthy transition
Looks like:
- a change that makes sense for the family
- continuity in purpose, even if not continuity in shape

### Suspicious transition
Looks like:
- sudden collapse
- sudden surge
- early trigger before the puck had enough structure
- delayed trigger that creates unnecessary stress

This is especially important in:
- fill-and-soak families
- blooming families
- adaptive or hybrid profiles

---

## Common graph patterns and what they often mean

Treat these patterns as **heuristics, not verdicts**.
Always cross-check them against family intent, phase transitions, and any available telemetry.

## Pattern: pressure high, flow low, harsh taste
Likely:
- too fine,
- too much puck stress,
- possibly too much pressure for the coffee.

## Pattern: pressure low, flow very high, weak and sour taste
Likely:
- too coarse,
- insufficient structure,
- or wrong family for the desired beverage density.

## Pattern: pressure smooth decline, flow gently rising, sweet cup
Likely:
- healthy lever-like or well-behaved flow-led extraction.

## Pattern: sudden pressure drop + sudden flow spike + ugly taste
Likely:
- channeling or puck fracture.

## Pattern: long staged shot, delayed main extraction, good sweetness
Likely:
- successful blooming or soak-led design.

## Pattern: extremely low pressure, open flow, clear juicy cup
Likely:
- successful soup or very open low-pressure family.

---

## Family-specific quick notes

Use these as reading reminders, not as full family definitions.

### Traditional / straight espresso
- healthy: quick build, stable pressure, resisted flow
- too fine: pinned pressure, starved flow, dense harsh cup
- too coarse: weak structure, sour or empty cup

### Fill-and-soak / preinfusion-led
- healthy: setup phase clearly improves the main extraction
- too fine: soak only delays a stressed shot
- too coarse: too much early flow before structure forms

### Blooming
- healthy: clear bloom, then meaningful recovery into the main shot
- too fine: bloom cannot rescue the puck
- too coarse: too much escapes before the shot really begins

### Lever-like / declining pressure
- healthy: smooth decline, not a collapse
- too fine: decline never really appears
- too coarse: decline turns into a fall-off

### Turbo / allongé / low-pressure fast-flow
- healthy: low-to-moderate pressure, open but coherent flow
- a short preinfusion or brief bloom-like setup can still be legitimate if the main extraction remains turbo/allongé in character
- too fine: pressure climbs back into stressed espresso territory
- too coarse: speed becomes emptiness instead of clarity

### Filter-style low-pressure
- healthy: low-pressure transparency with enough structure to stay articulate
- too fine: too much pressure, too much muddiness
- too coarse: empty rather than transparent

### Soup / ultra-low-pressure high-flow
- healthy: very open behavior, ultra-low pressure, clarity-led extraction
- too fine: it stops behaving like soup and starts behaving like bad low-pressure espresso
- too coarse: it falls outside the soup regime entirely

### Adaptive / resistance-led
- healthy: several graph shapes may still be acceptable
- too fine: flexibility collapses into stress
- too coarse: adaptability collapses into weakness

---

## From image read to provisional family inference

A graph or screenshot analysis should usually end its first pass by asking:
- what family does this shot most likely look like?
- how confident is that read?
- does the user confirm that this was the intended style?

When there is no confirmed profile mapping or no stated shot intent, treat the image result like a **provisional mapping case**, not a final classification case.

Recommended continuation order:
1. do the visual read
2. infer the most likely family provisionally
3. ask the user to confirm the intended family or named profile when possible
4. if the user cannot confirm, continue only with explicit provisional language
5. if the user later supplies a named profile, profile description, or phase details, upgrade the analysis accordingly

Useful bridge wording:

> If I am reading this correctly, this shot looks more like `X family` than `Y`.
> If that was the intended direction, I would continue the analysis on that basis.
> If the shot was meant to be a different style, the graph should be read differently.

This prevents two common mistakes:
- treating a provisional family inference as a settled fact
- stopping at visual description without connecting the graph to family-aware analysis

---

## From provisional family read to named-profile audit

A graph analysis often begins with a **provisional family read**.
That is appropriate when the intended profile is unknown.

If the user later provides stronger profile context — especially:
- a named profile,
- profile description text,
- or phase definitions,

upgrade the analysis.

### Keep these judgments separate

Once a named profile is known, separate:

1. **Family fit**
   - Does the graph broadly resemble the intended family?

2. **Named-profile fit**
   - Does the graph show the specific structure that is actually known for this named profile?

3. **Expression status**
   - Given the evidence above, was the shot expressed, partially expressed, or failed to express?

A graph may fit the family yet still diverge significantly from the intended named profile.

### What to compare

Use only the profile-specific structure that is actually supported by the available source material.
This may include:
- a characteristic opening behavior,
- a short or long soak,
- a pressure-led or flow-led middle,
- a known handoff,
- a taper or finish logic,
- or explicit timing / pressure / flow relationships.

Do **not** invent hard anchors that the profile description does not support.

### Practical rule

Do **not** upgrade a shot from:
- “looks like the right family”
to:
- “the named profile expressed successfully”
without checking whether the profile's defining visible structure actually appeared.

### If profile-specific evidence is weak

If the named profile is known but the available description supports only broad intent and family-level behavior:
- say that profile-specific verification remains limited,
- keep the judgment cautious,
- and avoid over-claiming exact profile expression.

### If profile-specific evidence is strong

If the profile description clearly defines important structure, transitions, or finish logic:
- compare the graph against those features directly,
- and let that comparison overrule a vague family resemblance if they conflict.

---

---

## When the image is weak, ask these questions

If the screenshot is unclear, ask for:
1. dose
2. final yield
3. total time
4. peak pressure
5. whether there was a deliberate soak / bloom
6. what the cup tasted like
7. which profile family or named profile was intended

Those seven answers can often replace a mediocre screenshot.

---

## What not to do

### 1. Do not diagnose only from time
Time without family context is weak evidence.

### 2. Do not diagnose only from pressure
Pressure is not the whole shot.

### 3. Do not let the graph overrule a delicious cup
If the coffee tastes excellent, the graph may simply be teaching you that your expectation was too narrow.

### 4. Do not use traditional expectations on non-traditional families
This is probably the single most common graph-reading mistake.

### 5. Do not confuse “different” with “bad”
A different extraction style should look different.

---

## Final rule of thumb

A good graph read answers four questions:

1. **What family was intended?**
2. **Did the graph behave like that family?**
3. **Where did the shot diverge, if it diverged at all?**
4. **Did the divergence explain the taste?**

If you can answer those four cleanly, you are not just reading lines — you are reading the shot.
