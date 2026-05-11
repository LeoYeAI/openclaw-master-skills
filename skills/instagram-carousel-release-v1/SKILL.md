---
name: instagram-carousel
description: >
  Generate professional Instagram carousels as self-contained HTML with export-ready 4:5 slides.
  Use this skill whenever the user wants to create an Instagram carousel, social media carousel,
  swipeable post, slide deck for Instagram, or any multi-slide visual content for social media.
  Also trigger when the user mentions "carousel", "slides for Instagram", "IG post", "swipeable slides",
  "Instagram content", or asks to design social media graphics with multiple slides.
  Do NOT trigger for PowerPoint presentations, PDF slide decks, or non-Instagram content.
---

# Instagram Carousel Generator

You are an Instagram carousel design system. Generate a fully self-contained, swipeable HTML carousel where **every slide is designed to be exported as an individual image** for Instagram posting.

## Workflow Overview

1. Run a mandatory creative-direction kickoff
2. Collect the remaining brand details from the user
3. Derive a restrained, carousel-wide color system
4. Research real data and statistics for the topic
5. Write in simple, beginner-friendly language
6. Set up typography
7. Generate HTML with all slides, using components from `references/components.md`

---

## Step 1: Mandatory Creative-Direction Kickoff

Before generating any carousel, always ask these 2 questions, even if the user already gave a topic, brand, or reference:

1. **Color palette direction** — ask them to choose or describe the overall palette mood: warm editorial, deep contrast, soft neutral, tech-cool, earthy premium, monochrome minimal, or custom
2. **Tone of voice** — ask how the carousel should sound: expert/investor, calm premium, friendly explainer, bold/provocative, playful, minimal, or custom

These two answers are mandatory inputs for every run. Do not skip them by assuming defaults.

---

## Step 2: Collect Brand Details

Before generating, ask the user for (if not already provided):

1. **Brand name** — displayed on the first and last slides
2. **Instagram handle** — shown in the IG frame header and caption
3. **Primary brand color** — hex code or description
4. **Logo** — SVG path, brand initial, or skip
5. **Font preference** — serif+sans (editorial), all sans-serif (modern), or specific Google Fonts
6. **Images** — any images to include

If the user provides a website URL, derive colors and style from it. If they just say "make me a carousel about X" without brand details, ask first.

---

## Step 3: Derive the Full Color System

From the user's **palette direction** plus one **primary brand color** (or a color you derive from their palette brief), generate:

```
BRAND_PRIMARY    = {anchor accent from user palette}                 // Main accent — progress bar, icons, tags, stat borders
BRAND_LIGHT      = {same hue, lighter and softer}                    // Secondary accent — tags on dark, pills
BRAND_DARK       = {same hue, darker and calmer}                     // CTA text, gradient anchor
LIGHT_BG         = {one consistent tinted off-white}                 // Main light background (never pure #fff)
LIGHT_SURFACE    = {slightly richer light surface for cards/bridges} // Soft bridge background between light and dark slides
LIGHT_BORDER     = {slightly darker than LIGHT_BG}                   // Dividers on light slides
DARK_BG          = {one consistent near-black with brand tint}       // Main dark background
BRAND_GRADIENT   = linear-gradient(165deg, BRAND_DARK 0%, BRAND_PRIMARY 60%, BRAND_LIGHT 100%)
STAT_ACCENT      = BRAND_PRIMARY                                     // Left-border for stat highlight blocks
```

**Derivation rules:**
- LIGHT_BG: tinted off-white complementing the primary (warm primary -> warm cream, cool -> cool gray-white)
- LIGHT_SURFACE: a soft middle step between LIGHT_BG and DARK_BG, useful for bridge slides and cards
- DARK_BG: near-black with subtle brand tint (warm -> #1A1918, cool -> #0F172A)
- LIGHT_BORDER: ~1 shade darker than LIGHT_BG
- Keep one hue family across the whole carousel. Change lightness and saturation, not the hue itself.
- Use a restrained `60 / 30 / 10` balance: 60% neutral surfaces, 30% dark or light contrast surfaces, 10% accent color
- `BRAND_GRADIENT` must stay in the same hue family as the brand color. Avoid neon-like saturation jumps.

**Background cadence:**
- Do not force strict light/dark/gradient alternation if it creates harsh jumps
- Prefer a controlled rhythm such as `LIGHT -> DARK -> SOFT GRADIENT -> LIGHT -> DARK -> LIGHT -> DARK -> CTA`
- Max 2 gradient slides per carousel, and usually only 1 content slide plus the CTA
- CTA always uses `BRAND_GRADIENT`
- All light slides should share the same `LIGHT_BG`; all dark slides should share the same `DARK_BG`
- Never introduce a second unrelated accent color family mid-carousel
- If a slide feels too loud next to its neighbors, desaturate the background before changing hue

---

## Step 4: Research & Data

Before generating content, research real, verifiable data for the topic. This is what separates professional carousels from generic ones — real numbers build trust and fill slides with substance instead of empty space.

**Requirements:**
1. **Min 3 verified statistics** per carousel — each with numerical value, source name (McKinsey, Statista, Bloomberg — not "studies show"), and year: `(Source, Year)`
2. **Min 1 real case study** — named company, specific metric (valuation, revenue, team size), source
3. **Number formatting** for visual impact: `$621B` not `$621,000,000,000`. Use the Stat Highlight Block component
4. **No vague claims** — never "research shows" without naming the source. Use `~` or `approx.` if uncertain
5. **Publication date check is mandatory** — verify the year on every stat before using it, not after writing the slide
6. **Prefer fresh primary sources for fast-moving metrics** — issuer reports, exchange data, fund pages, company filings, regulator data, or current-year industry reports

**Data freshness rule — CRITICAL:**
- Determine the current year from today's date. Only use statistics from the **current year or the previous year**. For example, if today is 2026, acceptable years are 2025 and 2026. Data from 2024 or earlier is outdated and must NOT be used.
- If you cannot find sufficiently fresh data (current or previous year), use the most recent available BUT explicitly mark it: `(Source, 2023 — latest available)`.
- Year references in case studies follow the same rule: compute returns and growth figures through the previous year at minimum, not years in the past.
- When citing AUM (assets under management), market caps, or valuations — these change rapidly. Always use the qualifier `~` and reference the latest available year.
- Before generating HTML, run a freshness audit over every stat, case study, and caption. Reject any unlabeled data older than the previous year.

---

## Step 5: Language Rules

Write in simple, clear Russian by default.

1. Prefer everyday words over finance jargon
2. Keep sentences short and concrete
3. Do not use slang, hype phrases, or insider vocabulary
4. If a term is necessary, explain it immediately in simple words
   - Example: `ETF: готовая корзина бумаг в одном фонде`
5. Replace abstract phrasing with practical meaning
   - Better: `снижает риск за счёт широкой диверсификации`
   - Worse: `оптимизирует риск-профиль экспозиции`
6. Write as if the reader is smart but new to the topic
7. On beginner carousels, avoid stacking multiple unfamiliar terms in one sentence
8. Do not use long em dashes `—` in output copy. Rewrite with a colon, comma, or a full sentence.
9. Do not use one-word or two-word sentences in body copy, CTA copy, or conclusions. Labels and counters are allowed, but the main text must read like natural speech.
10. Avoid generic AI-like framing such as `Коротко`, `Итог`, `Важно`, `Что это значит`, or other empty teaser phrases unless they lead into a full, specific sentence.
11. Avoid robotic contrast formulas like `не X, а Y` when they sound templated. Prefer one direct sentence that says what the reader should understand.

**Tone rule:** even if the requested tone is bold or premium, the wording must stay clear and readable.

---

## Step 6: Set Up Typography

Pick a **heading font** and **body font** from Google Fonts:

| Style | Heading | Body |
|-------|---------|------|
| Editorial / premium | Playfair Display | DM Sans |
| Modern / clean | Plus Jakarta Sans (700) | Plus Jakarta Sans (400) |
| Warm / approachable | Lora | Nunito Sans |
| Technical / sharp | Space Grotesk | Space Grotesk |
| Bold / expressive | Fraunces | Outfit |
| Classic / trustworthy | Libre Baskerville | Work Sans |
| Rounded / friendly | Bricolage Grotesque | Bricolage Grotesque |

**Size scale:**

| Role | Size | Weight | Notes |
|------|------|--------|-------|
| Headings | 28-34px | 600 | letter-spacing -0.3 to -0.5px, line-height 1.1-1.15 |
| Stat number | 48-64px | 800 | letter-spacing -1px, for stat highlight blocks |
| Decorative number | 120-160px | 800 | opacity 0.08-0.12, background on entity cards |
| Body | 14px | 400 | line-height 1.5-1.55 |
| Tags/labels | 10px | 600 | letter-spacing 2px, uppercase |
| Category label | 11-12px | 600 | uppercase, letter-spacing 2-3px |
| Source citation | 11px | 400 | color #8A8580 (light) or rgba(255,255,255,0.5) (dark) |
| Step numbers | 26px | 300 | heading font |

Every slide needs at least 3 text size tiers for visual hierarchy.

Apply `.serif` (heading font) and `.sans` (body font) CSS classes throughout.

---

## Step 7: Slide Architecture

### Format
- Aspect ratio: **4:5** (Instagram standard)
- Each slide is self-contained — all UI baked into the image
- Use LIGHT_BG, DARK_BG, and BRAND_GRADIENT according to the cadence rules above rather than strict alternation

### Every Slide Gets:

**Progress Bar** (bottom) — shows position in carousel. 3px track, fills proportionally. Light slides: `rgba(0,0,0,0.08)` track / BRAND_PRIMARY fill. Dark slides: `rgba(255,255,255,0.12)` track / `#fff` fill. Counter label: "1/7", 11px.

**Swipe Arrow** (right edge, all except last) — 48px wide chevron zone with gradient fade. Light: `rgba(0,0,0,0.06)` bg / `rgba(0,0,0,0.25)` stroke. Dark: `rgba(255,255,255,0.08)` bg / `rgba(255,255,255,0.35)` stroke. **Removed on last slide** to signal the end.

For the full HTML/JS code for these elements, see `references/components.md` under "Progress Bar" and "Swipe Arrow".

### Layout Rules
- Content padding: `0 36px` standard, `0 36px 52px` to clear progress bar
- Hero/CTA slides: `justify-content: center`
- Content-heavy slides: `justify-content: flex-end`

### Overflow Prevention — CRITICAL

Content must NEVER extend below the progress bar or outside the slide boundaries. This is the most common visual bug and must be prevented at the CSS level:

1. **Every slide** must use this container structure:
```html
<div class="slide" style="background:...;">
  <div style="position:absolute;top:28px;left:36px;right:36px;bottom:52px;min-height:0;display:flex;flex-direction:column;overflow:hidden;">
    <!-- ALL content here -->
  </div>
  <!-- progress bar (position:absolute) -->
  <!-- swipe arrow (position:absolute) -->
</div>
```

2. **Hard rules:**
   - The inner content `div` MUST have both `min-height:0` and `overflow:hidden` — together they prevent flex children from pushing past the safe area
   - The progress-bar safe zone must be excluded from layout using `bottom:52px` or an equivalent inner `content-safe` wrapper. Do not rely on `padding-bottom` alone.
   - Never use the older wrapper pattern `padding:0 36px 52px` without a true bottom inset
   - Right padding MUST account for the swipe arrow: use `padding-right:48px` on content that could extend to the right edge, or keep standard `36px` padding since the arrow is only 48px wide with transparent gradient

3. **Content budget per slide** — to prevent overflow, limit the number of components:
   - **Entity card slides:** max components = category label + icon + ticker badge + name + description (2-3 sentences max) + info block + 1 icon bullet. If adding a percentage bar or case study, remove the icon bullet
   - **Category/Deep Dive slides:** max components = category label + heading + 1 stat block + 1 case study OR 2 icon bullets (not both)
   - **Feature/Solution slides:** max 4 feature list items with single-line descriptions
   - If in doubt: fewer components with adequate breathing room are better than cramming and overflowing

4. **Text length limits:**
   - Headings: max 2 lines (use `<br>` for intentional breaks)
   - Entity descriptions: max 3 lines (~120 characters)
   - Info block text: max 3 lines (~130 characters)
   - Feature descriptions: max 1 line (~60 characters)
   - Stat block descriptions: max 2 lines (~100 characters)

5. **If content is still tight:**
   - Shorten copy first
   - Remove one secondary component second
   - Never shrink the progress bar area, never move the bar higher, and never let content visually touch it

### Bottom Safety Enforcement

If a slide is still taller than its usable content region after layout:

1. Remove the lowest-priority support block first
2. Then reduce support-block padding and gap
3. Only after that, shorten supporting copy
4. Never crop the bottom of a visible card behind the progress bar

Mark lower-priority proof blocks as optional when generating dense slides so they can be removed without harming the main message.

### Top Visibility Protection — CRITICAL

The top text block must never be clipped by overflow. Headings, opening paragraphs, and top labels are higher priority than lower supporting cards.

1. **Do not place the main heading inside one large bottom-aligned stack** on dense slides
2. **Use a two-part layout** for problem, solution, and deep-dive slides:
   - `top-safe-copy` = label + heading + short intro
   - `support-stack` = cards, stats, comparisons, bullets
3. `top-safe-copy` must use `flex-shrink:0`
4. `support-stack` should sit below it with `margin-top:auto`
5. If the full slide does not fit, remove or merge a lower-priority block from `support-stack` before shrinking or clipping the heading
6. On dense slides, prefer:
   - 1 comparison card + 1 stat block
   - or 2 comparison cards without an additional stat block
   - but not all three if the heading starts losing visibility

**Priority order when space is tight:**
1. Keep label, heading, and intro fully visible
2. Keep one primary proof block
3. Keep one secondary proof block only if the top copy remains fully visible
4. Drop tertiary filler before reducing headline legibility

### Center Void Prevention — CRITICAL

Protecting the top and bottom is not enough. Dense slides must also avoid a dead empty zone in the middle.

1. A slide must not have a large disconnected gap between the intro and the first support block
2. If the visual gap between `top-safe-copy` and the first proof block is larger than roughly 12-15% of slide height, rebalance the composition
3. Do not use `margin-top:auto` on `support-stack` when it contains only one proof block or when the slide becomes visually top-heavy
4. If only one main proof block remains after overflow cleanup, use one of these fixes:
   - pull the proof block upward into a balanced mid-stack layout
   - insert a bridge element between intro and proof block
   - split one large proof block into two lighter stacked blocks if space allows
5. Approved bridge elements:
   - short 2-3 item chip row
   - mini comparison strip
   - source rail
   - icon bullet row
   - compact takeaway bar
6. Do not leave a single stat card floating near the progress bar under a large empty center
7. On slides with one proof block, prefer a balanced composition over a bottom-anchored composition

**Decision rule:**
1. If the slide is tight, protect the top and bottom first
2. If the slide then looks hollow in the center, add a bridge or re-center the proof block
3. If the slide is both tight and hollow, reduce the number of components and switch to a balanced shell instead of pinning the last card to the bottom

---

## Content Density Rules

Every slide must be visually full — **max 20% empty space** — but content must NEVER overflow. Balance is key: fill the space, but respect the boundaries.

**The golden rule:** if you have to choose between "slightly empty" and "text overflows past the progress bar", always choose slightly empty. Overflow is a critical bug; empty space is a minor aesthetic issue.

### Three-Zone System
Each slide has 3 zones, each must contain at least one element:

| Zone | What goes here |
|------|----------------|
| **Top** (0-25%) | Category label, brand lockup, decorative number, or tag label |
| **Middle** (25-70%) | Heading + main component (stat block, feature list, entity card) |
| **Bottom** (70-100%) | Icon bullet points, source citations, tag pills, progress bar |

### Visual Anchor Rule
Every slide needs at least one eye-catching element: stat number (48px+), decorative background number (120px+), emoji icon in container, data visualization, CTA button, or grid layout. A slide with only heading + body text is not allowed.

### When Space Remains — Fill Priority:
1. Icon bullet points (2-3 with emoji + title + subtitle)
2. Secondary stat highlight block
3. Tag pills row
4. Case study block
5. Accent line + source citation

### Sparse Slide Rebalancing

If overflow cleanup removes enough content that the slide becomes sparse:

1. Re-check the three zones immediately
2. Add one bridge or filler element before adding another heavy card
3. Prefer slim fillers that connect the story:
   - `что внутри`
   - `кому подходит`
   - `по правилам 2026`
   - `важно помнить`
4. If the slide still feels bottom-heavy, switch from bottom anchoring to a balanced vertical stack
5. Empty space is acceptable only when it feels intentional. A random hole in the middle is not acceptable
6. Decorative dot pattern in corner

---

## Slide Types (12 available)

| # | Type | Background | Required Components |
|---|------|------------|---------------------|
| 1 | **Hero** | LIGHT_BG | Logo lockup, category label, heading, subtitle, 1 stat block |
| 2 | **Problem** | DARK_BG | Heading, pain description, strikethrough pills OR comparison cards |
| 3 | **Solution** | GRADIENT | Heading, feature list (3-4 icons), optional quote box |
| 4 | **Stat/Data** | Any | 1-2 stat blocks, percentage bar or comparison bars, sources |
| 5 | **Category/Deep Dive** | Any | Category #N label, heading, stat block, case study, 2 icon bullets |
| 6 | **Entity Showcase** | Alternating | Decorative number, emoji icon, ticker badge, name, desc, info block |
| 7 | **Grid/Comparison** | GRADIENT/DARK | 2x2 grid of cards, optional total stat at bottom |
| 8 | **Features/Benefits** | LIGHT_BG | 3-4 icon bullet points, optional tag pills |
| 9 | **How-To/Steps** | LIGHT_BG | Numbered steps (3-5), accent step numbers |
| 10 | **Quote/Testimonial** | DARK_BG | Quote box with attribution, optional stat |
| 11 | **Timeline** | Any | 3-4 entries with dates, vertical line connector |
| 12 | **CTA** | GRADIENT | CTA heading, CTA button, brand handle. **No arrow. Full progress bar.** |

**Rules:**
- Hero (slide 1) and CTA (last) are **mandatory**
- Stat/Data and Category are **strongly recommended**
- 8-10 slide carousel should use **5-7 different types**

For recommended slide sequences (7, 8, and 10-slide templates), see `references/components.md` under "Recommended Sequences".

---

## Visual Variety Rules

- Use at least **3 tonal states** per carousel (light, dark, soft gradient), but keep them within one palette family
- No same component on **3+ consecutive slides** without variation
- When a type repeats 3+ times: vary layout emphasis first, then background tone. Do not solve repetition by introducing unrelated colors.
- Decorative elements (accent lines, dots): on 2-4 slides, prefer lighter-content slides
- Neighboring slides should feel related at a glance. If two adjacent slides feel like different brands, reduce saturation and reuse the same support colors.

---

## Components Reference

All HTML component templates are in `references/components.md`. It contains:

1. **Stat Highlight Block** — big number + source citation (min 2 per carousel)
2. **Case Study Block** — real example card (min 1 per carousel)
3. **Entity/Company Card** — for list-type carousels
4. **Icon Bullet Point** — emoji + title + subtitle (use 2-3 to fill space)
5. **Comparison Cards** — stacked contrast cards
6. **Grid Layout 2x2** — multi-item comparison
7. **Strikethrough Pills** — "what's being replaced"
8. **Tag Pills** — category labels
9. **Quote/Prompt Box** — testimonials, example inputs
10. **Feature List** — icon + label + description rows
11. **Numbered Steps** — workflow slides
12. **Percentage Bar** — adoption rates, market shares
13. **Comparison Bars** — before/after contrasts
14. **Progress Ring SVG** — single percentage emphasis
15. **Decorative Elements** — accent lines, background numbers, dot patterns
16. **Logo Lockup** — brand icon + name
17. **CTA Button** — final slide call to action
18. **Progress Bar** — JS function for slide position indicator
19. **Swipe Arrow** — JS function for navigation chevron

Read `references/components.md` before generating any carousel to use the correct HTML templates.

---

## Preflight Checklist

Before finalizing any carousel, confirm all of the following:

1. The user answered the mandatory palette-direction and tone questions
2. Every statistic and case study passed the freshness audit
3. Every slide uses the safe wrapper with a true bottom inset plus `min-height:0` and `overflow:hidden`
4. No copy, card, or visual element touches the progress bar zone
5. Gradient use is restrained and the carousel stays within one coherent palette family
6. The last slide has no swipe arrow and a full progress bar
7. Every heading and intro paragraph is fully visible at the top of the slide without relying on clipping

---

## Instagram Frame (Preview Wrapper)

When displaying in chat, wrap in an Instagram-style frame:

- **Header:** Avatar (BRAND_PRIMARY circle + logo) + handle + subtitle
- **Viewport:** 4:5 aspect ratio, swipeable/draggable track
- **Dots:** Dot indicators below viewport
- **Actions:** Heart, comment, share, bookmark SVG icons
- **Caption:** Handle + carousel description + "2 HOURS AGO"

Include pointer-based swipe/drag interaction. Slides are standalone export-ready images.

---

## Design Principles

1. **Every slide is export-ready** — arrow and progress bar are part of the image
2. **Controlled tonal rhythm** — visual rhythm sustains attention without harsh palette jumps
3. **Font pairing** — display font for impact, body for readability
4. **Brand-derived palette** — all colors stay in one family
5. **Progressive disclosure** — progress bar fills, arrow guides forward
6. **Last slide is special** — no arrow, full progress bar, clear CTA
7. **Consistent components** — same styles across all slides
8. **Content clears UI** — text never overlaps progress bar or arrow
9. **No empty slides** — all 3 zones filled on every slide
10. **Data-driven content** — real statistics with named sources
11. **Visual anchors everywhere** — every slide has a large visual element
12. **Typography hierarchy** — min 3 font sizes per slide
13. **Simple wording wins** — clear language beats impressive-sounding jargon
