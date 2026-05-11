# Gestalt Principles — Designer's Eye Reference

## Table of Contents
1. Proximity
2. Similarity
3. Continuity
4. Closure
5. Figure/Ground
6. Common Fate
7. Prägnanz (Law of Good Form)
8. Uniform Connectedness

---

## 1. Proximity
Elements close together are perceived as a group.

**What to look for:**
- Buttons that sit equidistant from two unrelated labels — ambiguity about which label applies
- Form fields with labels too far from their inputs
- Cards where internal spacing equals external spacing — no clear boundary between card content and surrounding elements
- Action buttons orphaned from the content they act on

**Common violations:**
- "Floating" headings that are closer to the section above than the section below
- Navigation items with equal gap to logo and to page edge — no clear grouping
- Icon + label pairs with too much internal gap — reads as two separate elements

**Fix pattern:** Tighten spacing within groups; increase spacing between groups. Rule of thumb: internal gap should be ≤50% of external gap.

---

## 2. Similarity
Elements that look alike are perceived as related.

**What to look for:**
- Inconsistent button styles for actions of the same hierarchy level
- Links that look like body text (or body text that looks like links)
- Icons with inconsistent weight/style in the same context
- Alternating row colours that imply relationship between every-other row rather than within a row

**Common violations:**
- Primary CTA and secondary CTA styled identically
- Different card types (feature card vs. testimonial card) sharing the same visual treatment
- Navigation items and footer links sharing identical styling — implies same hierarchy

**Fix pattern:** Use style to signal meaning consistently. Every visual difference should carry semantic weight.

---

## 3. Continuity
The eye follows paths, lines, and curves.

**What to look for:**
- Misaligned columns that break the reading flow
- Elements that interrupt the natural scan path without intention
- Step indicators or progress bars that don't clearly flow left-to-right (in LTR contexts)
- Carousels/sliders that don't visually imply continuation (no peek of next item)

**Common violations:**
- Text columns with ragged right margins creating choppy scan lines
- CTA buttons not aligned with the text they follow
- Grid layouts where some items span columns without visual cues

**Fix pattern:** Establish strong alignment axes. Every element should anchor to an alignment line or intentionally break one for emphasis.

---

## 4. Closure
The mind completes incomplete shapes.

**What to look for:**
- Partially visible elements (carousels, lists) that don't clearly signal "more content exists"
- Borders and dividers that don't fully enclose the intended group
- Icon shapes that rely too heavily on implied closure at small sizes
- Progress indicators where the incomplete arc/bar reads as "done" rather than "in progress"

**Common violations:**
- Tabbed interfaces where the active tab doesn't visually connect to the content panel
- Cards without enough visual containment — content bleeds into surroundings
- Modals/overlays without sufficient contrast from background — boundary unclear

**Fix pattern:** Use enough visual cues to create the implied shape. If closure requires the user to work hard, add explicit containment.

---

## 5. Figure/Ground
Elements are perceived as either the subject (figure) or the background (ground).

**What to look for:**
- Insufficient contrast between primary content and background
- Background patterns or images competing with foreground text/UI
- Overlapping elements where figure/ground relationship is ambiguous
- Hero images where the subject blends with surrounding UI elements

**Common violations:**
- Light grey text on white background — insufficient contrast, ground wins
- Busy hero image with white text overlay without scrim/overlay treatment
- Floating action buttons that don't visually separate from content underneath
- Modal overlays with insufficient backdrop dimming

**Fix pattern:** The figure must always win. If anything competes with the primary focus element, reduce contrast, add overlay, or simplify the ground.

---

## 6. Common Fate
Elements moving or pointing in the same direction are perceived as related.

**What to look for:**
- Hover states that animate in inconsistent directions across similar components
- Icons that point in directions implying different flows than the interaction provides
- Scroll animations where grouped elements move independently
- Arrows/chevrons pointing in directions that contradict the action

**Common violations:**
- "Back" button with right-pointing chevron
- Accordion expand icon that doesn't rotate on open
- Carousel arrows that don't match the slide direction

**Fix pattern:** Movement and directionality must reinforce the mental model of the interaction.

---

## 7. Prägnanz (Law of Good Form)
The eye prefers the simplest interpretation.

**What to look for:**
- Overdesigned components where a simpler form would communicate the same thing
- Unnecessary gradients, shadows, or decorative elements adding visual noise
- Complex custom icons that could be replaced with universally understood symbols
- Layouts that require the user to construct a mental model rather than recognising an obvious one

**Common violations:**
- Custom hamburger menus that don't read as menus
- Bespoke graph/chart types where a standard bar/line chart would be clearer
- Typography with excessive weight variation in a single block of text

**Fix pattern:** Ask: what is the simplest visual form that communicates this? Default to that.

---

## 8. Uniform Connectedness
Elements with visible connections are perceived as related.

**What to look for:**
- Related items not connected by lines, borders, or enclosures when they should be
- Tooltip/popover that lacks a visual anchor to its trigger element
- Relationship diagrams without clear connection lines
- Breadcrumbs or step indicators without explicit connectors

**Fix pattern:** When proximity alone isn't enough to establish a relationship, add an explicit connector — border, line, shared container, or colour fill.
