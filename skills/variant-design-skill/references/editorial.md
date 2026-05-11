# Editorial & Journalism Reference

Science magazines, news cards, luxury editorial, cultural journalism, long-form articles.

> **Design system references for this domain:**
> - `design-system/typography.md` — editorial type scales, serif/sans pairing, vertical rhythm for long-form
> - `design-system/color-and-contrast.md` — restrained palettes, reading-optimized contrast
> - `design-system/spatial-design.md` — column grids, measure (ch units), generous whitespace
> - `design-system/responsive-design.md` — art direction with `<picture>`, fluid type for headlines

## Table of Contents
1. Starter Prompts
2. Color Palettes
3. Typography Pairings
4. Layout Patterns
5. Signature Details
6. Real Community Examples

---

## 1. Starter Prompts

**Science Magazine**
- "A science magazine spread about Mars: planetary database with element table (Overview / Aphelion / Mass / Nitrogen / Gravity / Orbital Period), orbital stats, red/orange dominant color."
- "A deep-sea exploration magazine feature: species discovery cards, depth scale infographic, bioluminescence photography treatment."
- "A climate science editorial: CO2 concentration timeline, tipping points marked, temperature anomaly chart, editorial pull quotes."

**News & Analysis**
- "An election analysis card: 'The incumbent's probability of winning has stabilized at 58%' — large statement text, trend chart, swing state breakdown table."
- "A morning news brief: 5 top stories in card format, live ticker at bottom, editor's note header, timestamp-driven layout."
- "A financial news card: earnings surprise headline, analyst consensus vs. actual, stock reaction chart, exec quote callout."

**Luxury & Lifestyle**
- "A luxury interior design editorial: 'Silence is a luxury' — full-bleed dark photography, minimal type overlay, one accent color, negative space as design element."
- "A fashion editorial spread: runway photography, designer biography sidebar, collection color story, editorial copy in elegant serif."
- "A premium travel magazine: destination photography, local culture data points, 'best time to visit' calendar widget, curated recommendations."

**Culture & Technology**
- "A tech-culture feature on computational linguistics: 'The intersection of computational systems and human language' — bilingual Japanese/English treatment, academic and modern."
- "A music culture magazine: artist profile, discography timeline, influence map, album artwork as design element."
- "An architecture editorial: building photography, structural diagram, material palette swatches, architect interview callout."

---

## 2. Color Palettes

### Mars Red (science/space)
```
--bg:        #7B1E1E
--surface:   #9B2C2C
--card:      #FDF5E6
--accent:    #E55A00
--text-dark: #1A0A00
--text-light: #FDF5E6
--table-bg:  #B83232
--table-alt: #A02828
```

### Luxury Black (lifestyle/fashion)
```
--bg:        #0A0A0A
--surface:   #141414
--card:      #1E1E1E
--border:    #2A2A2A
--text:      #F0EDE8
--muted:     #888888
--accent:    #C9A96E   /* warm gold */
--accent-2:  #8B7355
```

### Academic Cream (long-form/culture)
```
--bg:        #FEFCE8
--surface:   #FFFBEB
--card:      #FFFFFF
--border:    #E7E5E4
--text:      #1C1917
--muted:     #78716C
--accent:    #92400E   /* brown */
--link:      #1D4ED8
```

### Election Green (political/news)
```
--bg:        #16A34A
--card:      #FAFAF9
--text-on-bg: #FAFAF9
--text-on-card: #1C1C1C
--accent:    #FDE047
--chart-line: #1C1C1C
--border:    #D1FAE5
```

### Deep Ocean (nature/science)
```
--bg:        #0C1B33
--surface:   #132642
--card:      #1A3354
--text:      #E8F4FD
--accent:    #00B4D8
--accent-2:  #90E0EF
--muted:     #5A7A9A
```

---

## 3. Typography Pairings

| Display | Body | Character |
|---|---|---|
| `Playfair Display` | `Source Serif 4` | Classic editorial, authoritative |
| `Cormorant Garamond` | `Libre Baskerville` | Luxury, literary |
| `DM Serif Display` | `DM Sans` | Modern editorial, friendly |
| `Bodoni Moda` | `Lato` | Fashion, high contrast |
| `Abril Fatface` | `Source Sans 3` | Bold news, punchy |
| `Crimson Pro` | `Work Sans` | Academic, accessible |
| `Newsreader` | `Newsreader` (italic) | Pure editorial |

**Rule:** Mix type scales aggressively. 96px headline + 13px caption = editorial tension.

---

## 4. Layout Patterns

### Pattern A: Magazine Spread
```
┌────────────────────────────────────────┐
│  SECTION LABEL    ISSUE / DATE         │
├────────────────────────────────────────┤
│                                        │
│  BIG HEADLINE                          │
│  in display font, 2-3 lines            │
│                                        │
├─────────────────────┬──────────────────┤
│  Body copy          │  Pull quote      │
│  in columns         │  ──────────      │
│                     │  "Quote text"    │
│  ┌──────────────┐   │  ──────────      │
│  │  Data table  │   │  Sidebar fact    │
│  └──────────────┘   │                  │
└─────────────────────┴──────────────────┘
```

### Pattern B: News Card
```
┌────────────────────────────────────────┐
│  CATEGORY TAG   •   TIMESTAMP          │
│                                        │
│  Statement headline in large           │
│  type that spans the full width        │
│                                        │
├────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │  Chart / Data visualization      │  │
│  └──────────────────────────────────┘  │
│                                        │
│  Supporting data table or breakdown    │
└────────────────────────────────────────┘
```

### Pattern C: Full-Bleed Editorial
```
┌────────────────────────────────────────┐
│                                        │
│   [FULL BLEED IMAGE/COLOR]             │
│                                        │
│              "HEADLINE"                │
│              in large serif            │
│                                        │
│                                        │
├──────────┬─────────────────────────────┤
│  Photo   │  Article text, credits,     │
│  caption │  pull facts                 │
└──────────┴─────────────────────────────┘
```

### Pattern D: Database / Encyclopedia (science)
```
┌──────────────────────┬─────────────────┐
│ M > 04 (MARS)        │  Featured badge │
│ SUBJECT DATABASE     │                 │
├──────────────────────┴─────────────────┤
│  Overview   Aphelion   Closest Dist.   │
│  ──────────────────────────────────── │
│  Mass       Perihelion  Nitrogen       │
│  ──────────────────────────────────── │
│  Gravity    Orbital     Argon          │
│             Period                     │
├────────────────────────────────────────┤
│  [Large atmospheric/color visualization]│
└────────────────────────────────────────┘
```

---

## 5. Signature Details

- **Section labels** in ALL CAPS, small, muted — "ANALYSIS" / "FEATURED" / "DEEP DIVE"
- **Overline + headline** pairing: small category text above the main headline
- **Pull quotes** in large italic, offset from the column grid
- **Data tables** with alternating row tints and clear header hierarchy
- **"Featured" badge** — pill or corner tag in accent color
- **Running header**: publication name + section on every card/screen
- **Byline + timestamp** always present: "By [Author] · Mar 11, 2026"
- **Color-coded subject tags**: planet colors, political party colors, topic hues

---

## 6. Real Variant Community Examples

### Mars Subject Database — (Featured)

**Prompt:** "A science editorial database card for Mars: red/orange #C0392B dominant background, 'M > 04 (MARS)' header with 'Featured' pill badge. Left: two-column element table (Overview / Aphelion / Closest Distance / Mass / Perihelion / Nitrogen / Gravity / Orbital Period / Argon) with alternating row tints. Right panel: 'Focus. The Red Planet' article section with a rover timeline (Perseverance / Ingenuity / Curiosity / Viking 1 & 2 / Pathfinder). Clean serif body text on a cream/white card inset."

**What makes it work:**
- The deep red/orange background communicates "Mars" before a single word is read — it's a color that carries planetary identity. This is the editorial principle of letting the palette do conceptual work, not just aesthetic work.
- Placing the data table (left) beside the narrative text (right) mirrors how a print magazine spread works: the structured data earns trust, the prose creates meaning. Neither panel alone would hold attention as long as the two in combination.
- The cream/white card inset for the article text creates a reading zone that floats visually above the colored background — a classic magazine technique for controlling contrast without flattening the layout to pure white.
- The rover timeline (rather than a chart) humanizes the data — missions have names and years, making the science feel like a story with characters.

---

### Luxury Interior Editorial — "Silence is a luxury"

**Prompt:** "A luxury interior design editorial spread: near-black #0A0A0A background, full-bleed interior photography at 60% viewport height, single statement headline 'SILENCE IS A LUXURY' in large sparse serif centered at bottom of image, no subheadline, maximum negative space below. One accent: warm gold text on dark surface. Zero decorative elements."

**What makes it work:**
- Using a full headline as the only text element forces the copy to earn its place — "Silence is a luxury" works because it is both literally true (the room is quiet) and philosophically loaded (luxury = having enough space to hear nothing). Weak copy would collapse this format.
- Maximum negative space is the design itself, not the absence of design. The dark space around the image is what makes the image feel expensive — the same photo on a tight grid reads as a catalog; on this layout it reads as art.
- Restricting to one accent color (warm gold) and using it sparingly — only on the critical text — means the eye has exactly one place to go after taking in the photograph.

---

### Computational Linguistics — Bilingual Feature

**Prompt:** "A tech-culture editorial card on computational linguistics: dark purple #1A0A2E background. Japanese text dominant at 64px: '計算システムと人間言語学の交差点。' English translation below in 18px lighter weight: 'The intersection of computational systems and human language.' Academic and modern — serif Japanese, geometric Latin. Section label 'LANGUAGE × MACHINE' in small muted caps top-left."

**What makes it work:**
- Leading with the Japanese text at 3.5× the size of the English translation is a commitment to the bilingual conceit — a half-hearted equal-size treatment would read as indecision. The size hierarchy makes a statement: this publication treats both languages as primary.
- The tonal contrast between the dense kanji forms and the sparse Latin letterforms creates visual tension that mirrors the editorial subject: the friction between computational systems and human language. The design argues the point rather than illustrating it.
- Dark purple as background splits the difference between academic (dark, serious) and tech (purple, digital) — it refuses to be either a science journal or a startup landing page, which is exactly right for a culture-technology crossover piece.
