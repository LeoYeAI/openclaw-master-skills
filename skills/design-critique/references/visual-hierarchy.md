# Visual Hierarchy — Designer's Eye Reference

## Table of Contents
1. The Hierarchy Stack
2. Size & Scale
3. Weight & Contrast
4. Colour & Value
5. Position & Placement
6. Whitespace as a Hierarchy Tool
7. Common Hierarchy Failures

---

## 1. The Hierarchy Stack

Every design should have exactly **one** primary focal point per view, supported by secondary and tertiary levels. The eye must have a clear entry point, a defined reading path, and a clear exit/CTA.

**The three-tier model:**
- **Level 1 (hero/primary):** One thing. The most important message or action.
- **Level 2 (supporting):** 2–4 items. Context that supports the primary.
- **Level 3 (detail/tertiary):** Everything else. Available but not demanding attention.

**What to look for:**
- Multiple elements competing at Level 1 — everything shouting, nothing heard
- Missing Level 1 entirely — the user has no entry point
- All elements collapsed into one undifferentiated level — flat, hard to scan

---

## 2. Size & Scale

Size is the strongest, most immediate hierarchy signal. The eye reads large before small.

**Key ratios:**
- Heading to subheading: minimum 1.25× size difference to feel distinct
- H1 to body: typically 2.5×–4× for strong hierarchy
- Under 1.15× difference: elements read as the same level

**What to look for:**
- H1 and H2 too close in size — hierarchy collapses
- Body text as large as subheadings — tertiary content competing with secondary
- Icon sizes inconsistent across the same context (24px vs 20px vs 16px mixed)
- CTA button too small relative to the content it follows

**Fix pattern:** Establish a type scale with meaningful jumps (modular scale: 1.25, 1.333, 1.5 ratio). Every size should clearly belong to a level.

---

## 3. Weight & Contrast

Weight (bold/regular/light) reinforces scale and adds hierarchy without changing size. High contrast draws the eye; low contrast recedes.

**What to look for:**
- Bold used decoratively rather than semantically (bold random words in body text)
- All-regular weight body copy with no weight variation — flat, hard to scan
- Light weight text for important labels or UI copy — too low in hierarchy for its function
- Insufficient contrast between heading and body — both feel like the same level

**Fix pattern:**
- Reserve bold/semibold for: headings, key data points, labels on interactive elements
- Use regular for: body copy, descriptions, secondary labels
- Use light for: captions, timestamps, metadata

---

## 4. Colour & Value

Colour draws the eye before shape and before text. High-saturation elements rank higher in perceived hierarchy than desaturated ones.

**Hierarchy through colour:**
- High saturation / brand colour = primary action or key message
- Mid saturation / secondary colour = supporting content
- Low saturation / neutral = tertiary content, structure, dividers

**What to look for:**
- Multiple fully-saturated colours competing — eye has no clear winner
- Primary CTA in a muted colour while decorative elements are bright
- Colour used purely decoratively on elements that should recede
- Error/warning colours used so frequently they lose hierarchy meaning

**Fix pattern:** Map colour saturation to hierarchy level. Only one hue should "shout" at a time.

---

## 5. Position & Placement

Users in LTR languages scan in an F-pattern (web) or Z-pattern (marketing/landing pages). Position assigns hierarchy before the user consciously reads anything.

**F-pattern (web content, data-heavy pages):**
- Top-left: maximum attention
- Left edge: secondary attention
- Right side / below fold: lowest attention

**Z-pattern (landing pages, visual compositions):**
- Top-left → Top-right → Diagonal → Bottom-left → Bottom-right

**What to look for:**
- Primary CTA placed below fold without a scroll trigger
- Critical information buried in the right column of an F-pattern layout
- Headline at the bottom of a card with image at top — creates bottom-heavy weight
- Logo or primary nav element not in top-left anchor

**Fix pattern:** Map the most important element to the highest-attention position for the layout pattern being used.

---

## 6. Whitespace as a Hierarchy Tool

Whitespace (negative space) creates isolation, which signals importance. The most isolated element on a page draws the most attention.

**What to look for:**
- Primary CTA crowded by adjacent content — loses its isolation and importance
- Dense layouts with no breathing room — eye can't distinguish levels
- Inconsistent padding inside components — no clear spatial rhythm
- Section headings with same whitespace above and below — doesn't signal section start

**Key rule:** Increase whitespace above a heading/element to signal elevation in hierarchy. More air = more important.

**Common spacing ratios:**
- Margin above section heading: 2–3× margin below it
- Padding inside a card: consistent on all sides OR top+bottom different from left+right for intentional rhythm
- Between sibling elements: consistent unit multiples (8px grid, 4px grid)

---

## 7. Common Hierarchy Failures

| Failure | Effect | Fix |
|---|---|---|
| Everything the same size | No entry point, overwhelming | Establish a clear size scale with 3+ levels |
| 3+ elements at Level 1 | User paralysis, no focus | Reduce to one primary focal point per view |
| CTA buried in content | Low conversion, poor usability | Isolate CTA with whitespace, size, and colour |
| Hierarchy inverted | Confusing reading order | Most important = biggest, boldest, highest position |
| No whitespace between levels | Levels blur together | Add spacing to enforce visual separation |
| Colour used without hierarchy logic | Decoration without meaning | Map every colour choice to a hierarchy decision |
