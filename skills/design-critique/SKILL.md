---
name: designers-eye
description: "Get honest design feedback. Upload any visual — UI design, logos, photos, graphics, PDFs — and get prioritized critique: what's broken, what works, what to polish. Theory-backed analysis using 11 frameworks."
author: Chris Couriard
version: "2.0.4"
---

# Designers Eye — Professional Design Critique

A critical eye for design. Share a screenshot, image, or website URL and get honest, theory-backed feedback prioritized by impact.

## How It Works

**Input:** Any visual file — UI design (app & web), logos, photos, graphics, PDFs (as images), anything visual. Share directly in chat.

**Analysis:** Examined through 11 rigorous frameworks covering visual fundamentals, information hierarchy, usability, and platform expectations.

**Output:** Priority-ordered action list (critical → important → polish) with specific fixes linked to violated principles.

## How to Use

Share any image. That's it. UI design, logos, graphics, photos, PDFs exported as images, Figma frames — anything you can see gets the same treatment: theory-backed critique ranked by severity and actionability.

---

## Analysis Framework

Every critique examines 11 dimensions:

**1. Gestalt Principles** — How elements group and relate (proximity, similarity, continuity, closure, figure/ground, common fate, prägnanz, uniform connectedness).

**2. Visual Hierarchy** — What's the focal point? Are reading paths clear? Do size, weight, colour, position, and whitespace align?

**3. Colour Science (Itten)** — Colour contrast types (hue, saturation, value, temperature, simultaneous). Harmony systems (complementary, triadic, analogous). Emotional temperature. Colour interaction and optical mixing. WCAG contrast (4.5:1 text, 3:1 UI). Colourblind accessibility.

**4. Typography** — Type scale coherence. Font pairings. Readability (16px+ body). Line length (45–75 chars). Line height (1.5+). Weight and style choices. Hierarchy through type.

**5. Grid Structure & Alignment (Müller-Brockmann)** — Underlying grid present? Alignment consistency. Modulation (repetition with variation). Spacing relationships and rhythm. Margins and gutters logical.

**6. Composition & Moment (Freeman)** — Viewpoint and perspective. Framing (what's included/excluded). Depth relationships (foreground, middle, background). Focus and blur (selective attention). Scale and proportion. Moment/timing (if applicable).

**7. Information Design (Tufte)** — Data-ink ratio (signal vs noise). Information density. Layering and progressive disclosure. Clarity of intent. Reducing cognitive load.

**8. Reduction & Honesty (Rams/Bauhaus)** — Nothing superfluous. Form follows function. Reduction to essentials. Timelessness and coherence. Honest representation.

**9. Visual Balance & Weight** — Symmetrical vs asymmetrical balance. Visual weight of elements. Tension and composition stability.

**10. Usability Heuristics (Nielsen/Norman)** — System visibility and status. Match between system and real world. User control and freedom. Consistency and standards. Error prevention and recovery. Recognition vs recall. Flexibility and efficiency. Aesthetic and minimalist design. Error messages. Help and documentation.

**11. Platform Conventions** — Web, mobile, social, print, email norms. Safe zones. Thumb-friendliness. Expected patterns.

---

## Framework Deep Dive: Nielsen/Norman 10 Usability Heuristics

The 10 usability heuristics (also called Nielsen's Heuristics) are industry-standard principles for evaluating interactive design. Every critique checks these:

1. **System visibility and status** — Users always know where they are and what's happening
2. **Match between system and real world** — Language and concepts users understand
3. **User control and freedom** — Undo, redo, exit emergency exits
4. **Consistency and standards** — Follow platform and design conventions
5. **Error prevention and recovery** — Prevent problems before they happen; help users recover gracefully
6. **Recognition vs recall** — Minimize cognitive load; make options visible
7. **Flexibility and efficiency** — Shortcuts for experts; simplicity for beginners
8. **Aesthetic and minimalist design** — Remove clutter; focus on essentials
9. **Error messages** — Plain language, specific problems, constructive solutions
10. **Help and documentation** — Easy to search, task-focused, concrete steps

**Why this matters:** These heuristics have guided UX design for 30+ years. They're universal across platforms and contexts. A design that violates one of them typically creates friction or confusion for users.

---

## Output Format — Priority-Ordered Action List

Findings are grouped by severity. Fix critical issues first.

**Hard rule:** Every finding — regardless of severity level — must include a `Fix:` line. A critique without a fix is incomplete. Never omit it.

### 🔴 Critical
Issues that break usability, accessibility, or core functionality. Fix immediately.

Example:
```
🔴 Critical — Text contrast fails WCAG AA
The white text on your light blue background achieves 3.2:1 contrast (need 4.5:1 for AA).
This violates: Accessibility / WCAG contrast requirement
Fix: Darken the blue to #0052CC or lighten the text to #F5F5F5. Verify contrast with a checker.
```

### 🟡 Important
Issues that hurt the experience or violate design principles without breaking core function. Fix soon.

Example:
```
🟡 Important — Hierarchy collapse in the heading area
Your H1 (28px) and H2 (24px) sizes violate the type scale ratio (need ~1.25× gap = 35px vs 28px).
This violates: Visual hierarchy / Type scale consistency
Fix: Increase H1 to 35px or decrease H2 to 22px to create a clear scale.
```

### 🟢 Polish
Issues that elevate the design or address missed opportunities. Fix when time allows.

Example:
```
🟢 Polish — Spacing rhythm could be tightened
Your card padding is 20px but section margins are 40px, creating an inconsistent rhythm.
This violates: Gestalt proximity / Visual rhythm consistency
Fix: Use an 8px or 16px grid consistently. Stick to multiples: 8px, 16px, 24px, 32px, 40px, 48px.
```

---

## Workflow

1. **Share the image** — any visual file you want feedback on
2. **Optional:** specify focus — "Critique this" or "What needs fixing?"
3. **Get critique** — ranked by severity, theory-backed, actionable

---

## What This Skill Does NOT Do

- **Doesn't redesign** — You get critique and fixes, not new mockups
- **Doesn't make subjective calls** — "Pink is better than blue" isn't critique; principle-based feedback is
- **Doesn't analyze branding alone** — Focuses on usability, hierarchy, and principles, not "does this feel on-brand?"
- **Doesn't inspect code** — Visual critique only

---

## Tips for Getting Better Critiques

1. **Be specific about platform** — "This is a web app" vs. "This is a mobile app" changes the critique.
2. **Share context** — Is this a v1 rough draft or polished production? Critiques adjust.
3. **Ask a specific question if helpful** — "Does the CTA stand out?" focuses the analysis.
4. **Don't defend your choices** — Critique is feedback, not attack.
5. **Test fixes** — Once you implement, share again if you want confirmation.

---

# Reference: Gestalt Principles

## 1. Proximity
Elements close together are perceived as a group.

**What to look for:**
- Buttons equidistant from two unrelated labels — ambiguity about which label applies
- Form fields with labels too far from their inputs
- Cards where internal spacing equals external spacing — no clear boundary
- Action buttons orphaned from the content they act on

**Common violations:**
- "Floating" headings closer to the section above than the section below
- Navigation items with equal gap to logo and page edge — no clear grouping
- Icon + label pairs with too much internal gap — reads as two separate elements

**Fix pattern:** Tighten spacing within groups; increase spacing between groups. Internal gap should be ≤50% of external gap.

---

## 2. Similarity
Elements that look alike are perceived as related.

**What to look for:**
- Inconsistent button styles for actions of the same hierarchy level
- Links that look like body text (or body text that looks like links)
- Icons with inconsistent weight/style in the same context

**Common violations:**
- Primary CTA and secondary CTA styled identically
- Different card types sharing the same visual treatment
- Navigation items and footer links sharing identical styling — implies same hierarchy

**Fix pattern:** Every visual difference should carry semantic weight.

---

## 3. Continuity
The eye follows paths, lines, and curves.

**What to look for:**
- Misaligned columns that break reading flow
- Step indicators that don't clearly flow left-to-right (in LTR contexts)
- Carousels that don't visually imply continuation (no peek of next item)

**Common violations:**
- Text columns with ragged right margins creating choppy scan lines
- CTA buttons not aligned with the text they follow
- Grid layouts where some items span columns without visual cues

**Fix pattern:** Establish strong alignment axes. Every element should anchor to an alignment line.

---

## 4. Closure
The mind completes incomplete shapes.

**What to look for:**
- Partially visible elements that don't clearly signal "more content exists"
- Borders and dividers that don't fully enclose the intended group
- Progress indicators where the incomplete arc reads as "done"

**Common violations:**
- Tabbed interfaces where the active tab doesn't visually connect to the content panel
- Cards without enough visual containment — content bleeds into surroundings
- Modals without sufficient contrast from background — boundary unclear

**Fix pattern:** Use enough visual cues to create the implied shape. If closure requires the user to work hard, add explicit containment.

---

## 5. Figure/Ground
Elements are perceived as either the subject (figure) or the background (ground).

**What to look for:**
- Insufficient contrast between primary content and background
- Background patterns or images competing with foreground text
- Hero images where the subject blends with surrounding UI

**Common violations:**
- Light grey text on white background — insufficient contrast, ground wins
- Busy hero image with white text overlay without a scrim
- Modal overlays with insufficient backdrop dimming

**Fix pattern:** The figure must always win. Add overlay, reduce contrast, or simplify the ground.

---

## 6. Common Fate
Elements moving or pointing in the same direction are perceived as related.

**What to look for:**
- Hover states that animate in inconsistent directions across similar components
- Icons that imply different flows than the interaction provides
- Accordion expand icon that doesn't rotate on open

**Common violations:**
- "Back" button with right-pointing chevron
- Carousel arrows that don't match the slide direction

**Fix pattern:** Movement and directionality must reinforce the mental model.

---

## 7. Prägnanz (Law of Good Form)
The eye prefers the simplest interpretation.

**What to look for:**
- Overdesigned components where a simpler form communicates the same thing
- Unnecessary gradients, shadows, or decorative elements adding visual noise
- Layouts that require mental model construction rather than recognition

**Fix pattern:** Ask: what is the simplest visual form that communicates this? Default to that.

---

## 8. Uniform Connectedness
Elements with visible connections are perceived as related.

**What to look for:**
- Related items not connected by lines, borders, or enclosures when they should be
- Tooltips that lack a visual anchor to their trigger
- Breadcrumbs or step indicators without explicit connectors

**Fix pattern:** When proximity alone isn't enough, add an explicit connector — border, line, shared container, or colour fill.

---

# Reference: Visual Hierarchy

## The Hierarchy Stack

Every design should have exactly **one** primary focal point per view. The eye must have a clear entry point, a defined reading path, and a clear exit/CTA.

- **Level 1 (primary):** One thing. The most important message or action.
- **Level 2 (supporting):** 2–4 items. Context that supports the primary.
- **Level 3 (detail/tertiary):** Everything else. Available but not demanding attention.

---

## Size & Scale

Size is the strongest hierarchy signal. The eye reads large before small.

**Key ratios:**
- Heading to subheading: minimum 1.25× size difference
- H1 to body: typically 2.5×–4×
- Under 1.15× difference: elements read as the same level

**Fix pattern:** Establish a type scale with meaningful jumps (modular scale: 1.25, 1.333, 1.5 ratio).

---

## Weight & Contrast

- Reserve bold/semibold for: headings, key data points, labels on interactive elements
- Use regular for: body copy, descriptions, secondary labels
- Use light for: captions, timestamps, metadata

---

## Colour & Value

- High saturation / brand colour = primary action or key message
- Mid saturation = supporting content
- Low saturation / neutral = tertiary content, structure, dividers

**Fix pattern:** Only one hue should "shout" at a time.

---

## Position & Placement

- **F-pattern** (web content): Top-left = max attention, left edge = secondary, right/below fold = lowest
- **Z-pattern** (landing pages): Top-left → Top-right → Diagonal → Bottom-left → Bottom-right

---

## Whitespace as a Hierarchy Tool

Isolation signals importance. The most isolated element draws the most attention.

- Increase whitespace above a heading to signal elevation
- Margin above section heading: 2–3× margin below it
- Padding inside cards: consistent multiples (8px grid)

---

## Common Hierarchy Failures

| Failure | Effect | Fix |
|---|---|---|
| Everything the same size | No entry point | Establish a clear size scale with 3+ levels |
| 3+ elements at Level 1 | User paralysis | Reduce to one primary focal point per view |
| CTA buried in content | Low conversion | Isolate CTA with whitespace, size, and colour |
| No whitespace between levels | Levels blur | Add spacing to enforce visual separation |

---

# Reference: Colour Theory & Accessibility

## WCAG Contrast Requirements

| Text Type | AA (minimum) | AAA (enhanced) |
|---|---|---|
| Normal text (< 18pt / < 14pt bold) | 4.5:1 | 7:1 |
| Large text (≥ 18pt / ≥ 14pt bold) | 3:1 | 4.5:1 |
| UI components & graphic elements | 3:1 | — |
| Placeholder text | 4.5:1 | — |
| Disabled elements | Exempt | — |

**Quick benchmarks:**
- Black on white = 21:1 ✅
- #767676 on white = 4.54:1 ✅ (barely AA)
- #999 on white = 2.85:1 ❌
- White on #0066CC = 5.07:1 ✅
- White on #4CAF50 (green) = 3.0:1 ❌ (fails for small text)
- White on #FF5722 (orange) = 3.37:1 ❌ (fails for small text)

---

## Colour Harmony Models

- **Complementary:** Opposite on colour wheel. High contrast. Use for CTA vs. background.
- **Analogous:** Adjacent on colour wheel. Harmonious, cohesive, low tension.
- **Triadic:** Three colours equidistant. Balanced, playful. Use one dominant + two accents.
- **Monochromatic:** Single hue, varied saturation/value. Clean, minimal.

---

## Colour Temperature

| Temperature | Colours | Effect |
|---|---|---|
| Warm | Red, orange, yellow | Energy, urgency, warmth |
| Cool | Blue, green, purple | Calm, trust, professionalism |
| Neutral | Grey, black, white | Structure, stability |

**Semantic colour conventions:**
- Red = error, danger, delete
- Green = success, safe, proceed
- Yellow/amber = warning, caution
- Blue = info, link, neutral action

---

## Common Colour Mistakes

1. **Colour as the only differentiator** — 8% of males are colour-blind. Always pair colour with shape, icon, or label.
2. **Inconsistent semantic colours** — Blue used for links in one place, decorative headers in another.
3. **Brand colour forced into functional roles** — Orange brand colour as error state associates the brand with errors.
4. **Too many accent colours** — Limit to 1 primary action colour, 1 supporting accent, everything else neutral.
5. **Dark mode colours simply inverted** — Dark mode needs its own colour tokens.

---

# Reference: Typography

## Type Scale

Use a mathematical ratio, not random sizes.

**Common ratios:**
- **1.125** (minor second): subtle, good for dense content
- **1.25** (major third): balanced, most versatile
- **1.333** (perfect fourth): punchy, good for marketing
- **1.5** (perfect fifth): dramatic, good for hero content

**Example scale (1.25 ratio, base 16px):**
```
Body: 16px → H6: 20px → H5: 25px → H4: 31px → H3: 39px → H2: 49px → H1: 61px
```

---

## Font Pairing

- **Contrast pair:** Serif heading + sans-serif body (or vice versa) — immediately recognizable distinction
- **Weight-based pair:** Same family, different weights
- **Scale pair:** Same family, size + weight variation only

Stick to 2 fonts maximum. 3+ different faces = chaotic.

---

## Readability Targets

- **Body text:** 16–18px minimum, 1.5–1.6 line height, 45–75 character line length
- **Headings:** 1.1–1.3 line height
- **Letter spacing (body):** 0 (default)
- **Letter spacing (all-caps):** +0.05em to +0.1em

---

## Common Typography Failures

| Failure | Fix |
|---|---|
| Body text < 14px | Use 16px minimum |
| No type scale | Define a modular scale |
| Line height too tight | Use 1.5–1.6 for body |
| Line length > 100 chars | Cap at 75 characters |
| 3+ font families | Limit to 2 max |
| All-caps body copy | Use sentence case |

---

# Reference: Usability Heuristics

## 1. Visibility of System Status
Users should always know what's happening. Show state. Every action needs visible feedback.

**Violations:** No loading indicator, silent form submission, no current-page indicator.

---

## 2. Match Between System & Real World
Speak the user's language. Use familiar words and real-world metaphors.

**Violations:** Technical jargon in labels, unlabelled icon-only buttons, insider acronyms in public copy.

---

## 3. User Control & Freedom
Always provide undo, cancel, and escape routes.

**Violations:** Destructive actions without confirmation, modals with no close button, no way to reset a form.

---

## 4. Consistency & Standards
Users learn from one part of the system and expect it everywhere.

**Violations:** Primary actions in different colours across pages, inconsistent button placement, terminology shifts (search vs. find, delete vs. remove).

---

## 5. Error Prevention
Design to prevent errors before they happen.

**Violations:** Required fields with no indication, no inline validation, tiny touch targets, no confirmation before navigating away from unsaved work.

---

## 6. Error Recovery
When errors happen, recovery should be simple. Error messages should be plain language with a specific problem and clear fix.

**Violations:** "Invalid input" without saying which field, error shown at top of form while problem field is at bottom, red text on red background.

---

## 7. Flexibility & Efficiency
Design for both novices and experts. Shortcuts shouldn't hide core paths.

**Violations:** No keyboard shortcuts, forced multi-step processes that could be single-click, frequently-used settings buried in sub-menus.

---

## 8. Aesthetic & Minimalist Design
Every element should serve a purpose. Remove clutter.

**Violations:** Distracting animations, excessive borders/dividers, decorative icons that convey no information, backgrounds that reduce text legibility.

---

## 9. Help & Documentation
Help should be in context, task-focused, and specific.

**Violations:** No help text for complex interactions, "Learn more" links leading to marketing pages, help docs at odds with actual UI behaviour.

---

## 10. Recognition vs. Recall
Make actions and options visible. Minimize memory load.

**Violations:** Actions hidden in menus, icon-only toolbars with no labels, multi-step form with no current step indicator.

---

## Affordance & Discoverability
Interactive elements should look interactive.

- Minimum touch target: 44×44px (iOS), 48×48dp (Android)
- Links in body text must be visually distinct from surrounding copy
- Buttons must have obvious affordance — plain text doesn't look clickable

---

# Reference: Platform Conventions

## Web/Desktop

- **Navigation:** Primary nav in header, persistent; sidebar for secondary/filters
- **Links:** Underlined or clearly distinct from body text
- **Forms:** Labels above inputs, clear required indicators, inline validation
- **Focus states:** Visible focus ring for keyboard navigation (never `outline: none`)
- **Loading states:** Spinner, progress bar, or skeleton screen — never silent

---

## Mobile (iOS/Android)

- **Touch targets:** 44×44pt minimum (iOS), 48×48dp minimum (Android); 8px minimum spacing between targets
- **Navigation:** Bottom tab bar (iOS), drawer or bottom bar (Android)
- **Safe areas:** Account for notches, home indicators, status bar
- **Keyboard:** When input is focused, keyboard covers ~50% of screen — position content accordingly

---

## Social Media Posts

- **Thumbnail readability:** Text must be legible at 1/4 screen size
- **Safe zone:** Assume 80% of screen visible — bottom 20% may be cut by platform UI
- **Aspect ratios:** Instagram feed (4:5), Stories (9:16), Twitter/X video (16:9)
- **CTA placement:** First line of caption — most platforms truncate after 2 lines

---

## Email

- **Max width:** 600px (safe across clients)
- **Layout:** Single column; multi-column breaks in many clients
- **Typography:** Web-safe fonts only (Arial, Verdana, Georgia, Times New Roman)
- **Images:** Always include alt text — images are often disabled by clients
- **Background images:** Not supported; don't rely on them

---

## Dark Mode

- **Background:** Use #121212 or #1a1a1a, not pure #000000
- **Contrast:** Test every colour pair in both light and dark modes separately
- **Images/icons:** May need different treatment — check visibility against dark backgrounds

---

## Accessibility (All Platforms)

- **Contrast:** 4.5:1 for text, 3:1 for UI components (WCAG AA minimum)
- **Keyboard navigation:** All interactive elements must be keyboard-accessible
- **Tab order:** Logical, left-to-right, top-to-bottom
- **Alt text:** Meaningful descriptions, not "image" or "photo"
- **Skip links:** Allow users to skip navigation to main content
- **Semantic structure:** Proper heading hierarchy (H1 → H2 → H3), correct list markup, associated form labels
