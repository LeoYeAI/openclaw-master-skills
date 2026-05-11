# Colour Theory & Accessibility — Designer's Eye Reference

## Table of Contents
1. Colour Relationships
2. Colour Temperature & Psychological Effect
3. Colour Harmony Models
4. WCAG Contrast Requirements
5. Common Colour Mistakes
6. Colour in UI Contexts

---

## 1. Colour Relationships

**Hue:** The base colour (red, blue, green etc.)
**Saturation:** How vivid or muted. High saturation = vivid. Low = greyed out.
**Value/Lightness:** How light or dark. Controls contrast and perceived weight.

The three dimensions work together. A colour can fail not because its hue is wrong, but because its saturation or value is mismatched to its role.

**What to look for:**
- Colours that are the same hue but insufficient value contrast — reads as one flat colour
- Over-saturated palette — every colour fighting for attention
- Under-saturated palette — design feels lifeless, directionless
- Brand colours used at wrong saturation levels (primary colour diluted to the point of invisibility)

---

## 2. Colour Temperature & Psychological Effect

| Temperature | Colours | Effect |
|---|---|---|
| Warm | Red, orange, yellow | Energy, urgency, warmth, appetite |
| Cool | Blue, green, purple | Calm, trust, professionalism, distance |
| Neutral | Grey, black, white, beige | Structure, stability, support |

**What to look for:**
- Error states in cool colours (blue error message feels like info, not danger)
- Trust-oriented products (finance, health, legal) using warm/aggressive palettes
- Success states in red — contradicts expectation
- CTA buttons in a colour that blends with the page temperature rather than contrasting

**Semantic colour conventions (violate these consciously, not accidentally):**
- Red = error, danger, delete
- Green = success, safe, proceed
- Yellow/amber = warning, caution
- Blue = info, link, neutral action

---

## 3. Colour Harmony Models

**Complementary:** Opposite on the colour wheel. High contrast, vibrant. Use for CTA vs. background.
- Risk: Vibration effect at small sizes when both colours are fully saturated

**Analogous:** Adjacent on the colour wheel. Harmonious, cohesive, low tension.
- Best for: brand palettes, backgrounds, illustration
- Risk: Low contrast — check WCAG before using for text/UI

**Triadic:** Three colours equidistant on the wheel. Balanced, playful.
- Best for: illustration, icons, infographics
- Risk: Can feel chaotic in UI; use one dominant + two accents

**Split-complementary:** One base + two colours adjacent to its complement. Less tension than complementary, still strong contrast.
- Best for: UI with accent colour needs + primary brand colour

**Monochromatic:** Single hue with varied saturation/value.
- Best for: minimal UI, dark mode, sophisticated brand feel
- Risk: Risk of flat hierarchy if value differences are too small

**What to look for in practice:**
- Random colour combinations that don't follow any harmony model
- Too many competing hues (4+ fully-saturated colours in one view)
- Complementary pairs used at full saturation at small scales (vibration)

---

## 4. WCAG Contrast Requirements

All text/background combinations must meet WCAG 2.1 at minimum AA level.

### Text Contrast Ratios

| Text Type | AA (minimum) | AAA (enhanced) |
|---|---|---|
| Normal text (< 18pt / < 14pt bold) | 4.5:1 | 7:1 |
| Large text (≥ 18pt / ≥ 14pt bold) | 3:1 | 4.5:1 |
| UI components & graphic elements | 3:1 | — |
| Placeholder text | 4.5:1 | — |
| Disabled elements | Exempt | — |

### What to look for:
- Light grey body text on white (#999 on #fff = ~2.85:1 — FAILS AA)
- White text on medium-saturation brand colours (check each individually)
- Icon-only interactive elements without contrast against their background
- Ghost/outline buttons with insufficient border contrast
- Placeholder text styled the same as input text (common in custom inputs)

### Quick mental benchmarks:
- Black on white = 21:1 ✅
- #767676 on white = 4.54:1 ✅ (barely AA)
- #999 on white = 2.85:1 ❌
- White on #0066CC (standard blue) = 5.07:1 ✅
- White on #4CAF50 (standard green) = 3.0:1 ❌ (fails for small text)
- White on #FF5722 (deep orange) = 3.37:1 ❌ (fails for small text)

### Non-text contrast (UI components):
Borders of input fields, focus rings, icon-only buttons all need 3:1 against adjacent colours.

---

## 5. Common Colour Mistakes

**1. Using colour as the only differentiator**
Red = error, green = success — but what about colour-blind users (8% of males)?
Fix: Always pair colour with shape, icon, or label. Never rely on colour alone.

**2. Inconsistent semantic colour usage**
Blue used for links in one place, buttons in another, and decorative headers in a third.
Fix: Establish a colour system. Each colour has one semantic role.

**3. Brand colour forced into functional roles**
Using an orange brand colour as the error state — associates the brand with errors.
Fix: Separate brand palette from functional/semantic palette.

**4. Dark mode colours simply inverted**
A dark background with the same blue that worked on white — often fails contrast in dark mode.
Fix: Dark mode needs its own colour tokens, not just inversions.

**5. Too many accent colours**
3+ fully-saturated accent colours in a single view creates chaos.
Fix: One primary action colour, one supporting accent. Everything else neutral.

---

## 6. Colour in UI Contexts

### Web/App
- Limit active palette to: 1 primary, 1 secondary/accent, 2–3 neutrals
- Backgrounds: neutral, low saturation
- Interactive elements: consistent colour system (primary blue/brand for CTAs, red for destructive)

### Social Post / Marketing
- More latitude for bold colour
- Still needs a focal point — one colour should dominate
- Text contrast rules still apply even in creative work

### Mobile
- Reduced screen size amplifies colour contrast issues
- Thin/light text at small sizes + low contrast = unreadable
- System dark mode support requires verified contrast in both modes

### Dark Mode
- Don't go pure black (#000) — use #121212 or similar to reduce harshness
- Elevate surfaces with lightness steps, not additional colour
- Check all text/icon contrast against dark backgrounds individually
