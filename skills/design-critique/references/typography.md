# Typography — Designer's Eye Reference

## Table of Contents
1. Type Scale
2. Font Pairing & Hierarchy
3. Readability & Legibility
4. Line Length & Spacing
5. Font Selection by Context
6. Common Typography Failures

---

## 1. Type Scale

A type scale is a set of related font sizes that create hierarchy and rhythm. Don't pick sizes randomly—use a mathematical ratio.

**Common scale ratios:**
- **1.125** (minor second): subtle, good for dense content
- **1.25** (major third): balanced, most versatile
- **1.333** (perfect fourth): punchy, good for marketing
- **1.5** (perfect fifth): dramatic, good for hero content

**Building a scale (example with 1.25 ratio, base 16px):**
```
Base (body): 16px
H6: 16 × 1.25 = 20px
H5: 20 × 1.25 = 25px
H4: 25 × 1.25 = 31px
H3: 31 × 1.25 = 39px
H2: 39 × 1.25 = 49px
H1: 49 × 1.25 = 61px
```

**What to look for:**
- Random font sizes with no relationship (14px, 18px, 28px, 22px)
- Scale ratio too small — headings barely larger than body (1.05-1.1)
- Scale ratio too large — headings dominatingly huge
- Body copy that varies in size between sections (10px here, 14px there)

**Fix:** Use a tool like [Type Scale](https://type-scale.com) or define a scale using modular ratios above.

---

## 2. Font Pairing & Hierarchy

**Pairing models:**

**Contrast pair (most common):**
- Serif heading + sans-serif body (or vice versa)
- Example: Georgia headings + Open Sans body
- Works because serif vs. sans is an immediately recognizable distinction

**Weight-based pair:**
- Same font family, different weights
- Example: Montserrat Bold for heading + Montserrat Regular for body
- Risk: Needs careful contrast; can feel flat if weights are too similar

**Scale pair (Google Fonts approach):**
- Same font family, different sizes with weight variation
- Example: Inter Bold 32px for H1 + Inter Regular 14px for body
- Low risk, modern, clean

**What to look for:**
- Serif + serif or sans + sans without weight/size distinction — no hierarchy signal
- Font pairing that fights (display font + heavy serif body = chaotic)
- Too many fonts in one design (3+ different faces)
- Headline font unreadable at small sizes (thin decorative font for titles)

**Fix:** Stick to 2 fonts maximum. If pairing same family, use weight variation.

---

## 3. Readability & Legibility

**Legibility** = can you distinguish individual letters?
**Readability** = can you scan and understand text effortlessly?

### Legibility issues (micro level):
- Font too small for body copy (< 14px on web)
- Letter spacing too tight, letters blur together
- Line height too tight, lines feel cramped
- Font weight too light for small text (thin fonts don't render cleanly below 24px)

**What to look for:**
- Body text smaller than 16px without exceptional justification
- All-caps body copy (harder to read than sentence case)
- Italic body copy (italic headings are fine; italic paragraphs tire the eye)
- Decorative fonts for body copy (should only be used for headlines)

### Readability issues (macro level):
- Line length too long (> 75 characters per line = eye loses track)
- Line length too short (< 45 characters per line = awkward line breaks)
- Line height too tight (line height < 1.5 for body copy = dense, hard to scan)
- Contrast too low (low-contrast text requires extra cognitive effort)

**Fix targets:**
- Body text: 16–18px on web, 1.5–1.6 line height, 45–75 character line length
- Headings: 1.1–1.3 line height (tighter, they don't need the breathing room)

---

## 4. Line Length & Spacing

**Optimal line length: 50–75 characters (including spaces).**

Narrower (< 45 chars): Reading requires more eye movement left-right; awkward word breaks.
Longer (> 75 chars): Eye loses its place; reader has to consciously track.

**Tools:**
- Use a character counting tool or measure in your design tool
- Test by reading the text yourself — does your eye naturally re-find the line?

**Line height (leading):**
| Text Type | Line Height | Effect |
|---|---|---|
| Body copy (16px+) | 1.5–1.6 | Optimal readability, open feel |
| Dense content | 1.4–1.5 | Tighter but still readable |
| Headings | 1.1–1.25 | Tighter is fine, gives hierarchy |
| List items / sparse content | 1.6–1.8 | Extra breathing room for scannability |

**Letter spacing (tracking):**
- Body copy: 0 (default, use font's built-in kerning)
- Headings: 0 to -0.03em (negative tracking = tighter, more impact)
- All-caps headings: +0.05em to +0.1em (slight expansion for legibility)
- Labels on buttons: 0.5–1px (slight expansion helps readability)

**What to look for:**
- Line height that matches x-height of the font (doesn't account for ascenders/descenders)
- Tracking/letter spacing that looks like individual words floating (too much)
- Paragraph margins larger than line height (breaks the reading rhythm)

---

## 5. Font Selection by Context

| Context | Font Type | Example | Why |
|---|---|---|---|
| Body copy, paragraphs | Serif or humanist sans | Georgia, Inter, Open Sans | Optimized for extended reading |
| Headings | Any, unless decorative | Montserrat, Playfair, Poppins | Size + weight carry hierarchy |
| UI labels, buttons | Geometric or neutral sans | Roboto, Helvetica, Inter | Clean, utilitarian, scannable |
| Data (numbers, code) | Monospace | Courier, IBM Plex Mono | Fixed-width aids parsing |
| Marketing/display | Display fonts, decorative | Playfair, Bebas, custom | Captures attention at large size |

**Avoid:**
- Decorative fonts for body copy — unreadable at small sizes
- Serif fonts for UI labels — adds visual noise
- Thin fonts for small text — don't render cleanly on screen
- Too many different fonts in one design

---

## 6. Common Typography Failures

| Failure | Impact | Fix |
|---|---|---|
| Body text < 14px | Unreadable, inaccessible | Use 16px minimum (18px for older users) |
| No type scale | Hierarchy collapse, random appearance | Define a modular scale |
| Line height too tight | Dense, hard to scan, tiring | Use 1.5–1.6 for body |
| Line length > 100 chars | Eye loses place, re-reading required | Cap at 75 characters / column width |
| 3+ font families | Chaotic, unprofessional | Limit to 2 families max |
| Heading readability issue | CTA invisible or illegible | Headings need adequate size + weight |
| No font pairing logic | Visual clash, no hierarchy signal | Use contrast (serif+sans) or weight variation |
| Weight inconsistency | Hierarchy unclear | Establish which weights = which roles |
