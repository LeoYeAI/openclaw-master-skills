# Style Presets Reference

Curated visual styles for Slide Creator. Each preset is inspired by real design references—no generic "AI slop" aesthetics. **Abstract shapes only—no illustrations.**

---

## ⚠ CRITICAL: Viewport Fitting (Non-Negotiable)

**Every slide MUST fit exactly in the viewport. No scrolling within slides, ever.**

### Content Density Limits Per Slide

| Slide Type | Maximum Content |
|------------|-----------------|
| Title slide | 1 heading + 1 subtitle |
| Content slide | 1 heading + 4-6 bullets (max 2 lines each) |
| Feature grid | 1 heading + 6 cards (2x3 or 3x2) |
| Code slide | 1 heading + 8-10 lines of code |
| Quote slide | 1 quote (max 3 lines) + attribution |

**Too much content? → Split into multiple slides. Never scroll.**

### Required Base CSS (Include in ALL Presentations)

```css
/* ===========================================
   VIEWPORT FITTING: MANDATORY
   Copy this entire block into every presentation
   =========================================== */

/* 1. Lock document to viewport */
html, body {
    height: 100%;
    overflow-x: hidden;
}

html {
    scroll-snap-type: y mandatory;
    scroll-behavior: smooth;
}

/* 2. Each slide = exact viewport height */
.slide {
    width: 100vw;
    height: 100vh;
    height: 100dvh; /* Dynamic viewport for mobile */
    overflow: hidden; /* CRITICAL: No overflow ever */
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    position: relative;
}

/* 3. Content wrapper */
.slide-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-height: 100%;
    overflow: hidden;
    padding: var(--slide-padding);
}

/* 4. ALL sizes use clamp() - scales with viewport */
:root {
    /* Typography */
    --title-size: clamp(1.5rem, 5vw, 4rem);
    --h2-size: clamp(1.25rem, 3.5vw, 2.5rem);
    --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.65rem, 1vw, 0.875rem);

    /* Spacing */
    --slide-padding: clamp(1rem, 4vw, 4rem);
    --content-gap: clamp(0.5rem, 2vw, 2rem);
}

/* 5. Cards/containers use viewport-relative max sizes */
.card, .container {
    max-width: min(90vw, 1000px);
    max-height: min(80vh, 700px);
}

/* 6. Images constrained */
img {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
}

/* 7. Grids adapt to space */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

/* ===========================================
   RESPONSIVE BREAKPOINTS - Height-based
   =========================================== */

/* Short screens (< 700px height) */
@media (max-height: 700px) {
    :root {
        --slide-padding: clamp(0.75rem, 3vw, 2rem);
        --content-gap: clamp(0.4rem, 1.5vw, 1rem);
        --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
    }
}

/* Very short (< 600px height) */
@media (max-height: 600px) {
    :root {
        --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
        --title-size: clamp(1.1rem, 4vw, 2rem);
        --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
    }

    .nav-dots, .keyboard-hint, .decorative {
        display: none;
    }
}

/* Extremely short - landscape phones (< 500px) */
@media (max-height: 500px) {
    :root {
        --slide-padding: clamp(0.4rem, 2vw, 1rem);
        --title-size: clamp(1rem, 3.5vw, 1.5rem);
        --body-size: clamp(0.65rem, 1vw, 0.85rem);
    }
}

/* Narrow screens */
@media (max-width: 600px) {
    .grid {
        grid-template-columns: 1fr;
    }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }
}
```

### Viewport Fitting Checklist

Before finalizing any presentation, verify:

- [ ] Every `.slide` has `height: 100vh; height: 100dvh; overflow: hidden;`
- [ ] All font sizes use `clamp(min, preferred, max)`
- [ ] All spacing uses `clamp()` or viewport units
- [ ] Breakpoints exist for heights: 700px, 600px, 500px
- [ ] Content respects density limits (max 6 bullets, max 6 cards)
- [ ] No fixed pixel heights on content elements
- [ ] Images have `max-height` constraints
- [ ] No negated CSS functions (use `calc(-1 * clamp(...))` not `-clamp(...)`)

---

## Dark Themes

### 1. Bold Signal

**Vibe:** Confident, bold, modern, high-impact

**Layout:** Colored card on dark gradient. Number top-left, navigation top-right, title bottom-left.

**Typography:**
- Display: `Archivo Black` (900)
- Body: `Space Grotesk` (400/500)

**Colors:**
```css
:root {
    --bg-primary: #1a1a1a;
    --bg-gradient: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
    --card-bg: #FF5722;
    --text-primary: #ffffff;
    --text-on-card: #1a1a1a;
}
```

**Signature Elements:**
- Bold colored card as focal point (orange, coral, or vibrant accent)
- Large section numbers (01, 02, etc.)
- Navigation breadcrumbs with active/inactive opacity states
- Grid-based layout for precise alignment

**Named Layout Variations:**

**1. Hero Card**
Large colored card (`--card-bg`) occupies 60% of width, centered vertically, anchored left. Card: section number `01` small top-left, headline 2–3 lines. Dark background outside card. Ghost section number in 10rem at 8% opacity as texture. Nav breadcrumbs top-right.

**2. Manifesto Statement**
`01` in 8rem `Archivo Black` top-left, card color. Below: 2-line statement in 3rem. Right half: supporting 3-line body paragraph in muted white `rgba(255,255,255,0.6)`. Bottom-left: next section teaser in 0.75rem mono.

**3. Feature Trio**
Three full-width horizontal rows, shorter height than a normal card. Active/highlighted row: full `--card-bg` color. Other rows: 20% opacity, outlined. Each row: number left, feature name center-left in 1.3rem, 1-line descriptor right.

**4. Stat + Story**
Left 40%: single large number `5rem` in `--card-bg` color, label below in 0.75rem uppercase. `1px` vertical rule (card color). Right 55%: 3-line supporting paragraph + 2–3 bullet points with card-colored `▸` markers.

**5. Timeline Track**
Horizontal numbered steps `01 → 02 → 03 → 04`. Active step: full colored card above the track line. Completed steps: full opacity outlined. Future steps: 30% opacity outlined. Track line: `2px --card-bg`.

**6. Quote Block**
Full-width colored card (`--card-bg` background). Large `"` in near-black at top-left, barely visible (8% opacity). Quote in `Archivo Black` 2rem, dark text. Attribution bottom-right: `—Name, Role` in small body.

**7. Split Evidence**
Left 42%: section number in 3rem + headline in 2rem + 1-line sub. `1px` vertical rule (card color). Right 53%: 4–5 bullet list, each bullet: card-colored `▸` + bold lead word + 1-line description.

---

### 2. Electric Studio

**Vibe:** Bold, clean, professional, high contrast

**Layout:** Split panel—white top, blue bottom. Brand marks in corners.

**Typography:**
- Display: `Manrope` (800)
- Body: `Manrope` (400/500)

**Colors:**
```css
:root {
    --bg-dark: #0a0a0a;
    --bg-white: #ffffff;
    --accent-blue: #4361ee;
    --text-dark: #0a0a0a;
    --text-light: #ffffff;
}
```

**Signature Elements:**
- Two-panel vertical split
- Accent bar on panel edge
- Quote typography as hero element
- Minimal, confident spacing

---

### 3. Creative Voltage

**Vibe:** Bold, creative, energetic, retro-modern

**Layout:** Split panels—electric blue left, dark right. Script accents.

**Typography:**
- Display: `Syne` (700/800)
- Mono: `Space Mono` (400/700)

**Colors:**
```css
:root {
    --bg-primary: #0066ff;
    --bg-dark: #1a1a2e;
    --accent-neon: #d4ff00;
    --text-light: #ffffff;
}
```

**Signature Elements:**
- Electric blue + neon yellow contrast
- Halftone texture patterns
- Neon badges/callouts
- Script typography for creative flair

---

### 4. Dark Botanical

**Vibe:** Elegant, sophisticated, artistic, premium

**Layout:** Centered content on dark. Abstract soft shapes in corner.

**Typography:**
- Display: `Cormorant` (400/600) — elegant serif
- Body: `IBM Plex Sans` (300/400)

**Colors:**
```css
:root {
    --bg-primary: #0f0f0f;
    --text-primary: #e8e4df;
    --text-secondary: #9a9590;
    --accent-warm: #d4a574;
    --accent-pink: #e8b4b8;
    --accent-gold: #c9b896;
}
```

**Signature Elements:**
- Abstract soft gradient circles (blurred, overlapping)
- Warm color accents (pink, gold, terracotta)
- Thin vertical accent lines
- Italic signature typography
- **No illustrations—only abstract CSS shapes**

---

## Light Themes

### 5. Blue Sky

> **Starter template available:** When generating a Blue Sky presentation, read and use [`references/blue-sky-starter.html`](references/blue-sky-starter.html) as the base file. All visual elements are pre-built — do not reimplement them. See SKILL.md Phase 3 for instructions.

**Vibe:** Clean, airy, enterprise-ready, modern SaaS — inspired by a real enterprise AI pitch deck. Light sky-blue canvas with floating glassmorphism cards and animated ambient orbs. Feels like a high-altitude clear day: open, confident, premium.

**Layout:** Full-bleed sky gradient with 3 animated blur orbs that reposition per slide. Content in centered glassmorphism cards. Horizontal slide transitions (spring physics). Pill pagination dots at bottom. Fullscreen button top-right.

**Typography:**
- System fonts: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif`
- All labels: `letter-spacing: 0.2em; text-transform: uppercase; font-weight: 600`
- Headlines: Bold/Black weight
- Body: `font-weight: 300` (light)
- Gradient headline: `#1e3a8a` → `#3b82f6` (deep navy to bright blue)

**Colors:**
```css
:root {
    /* Background — sky gradient */
    --bg-from: #f0f9ff;         /* sky-50 */
    --bg-to:   #e0f2fe;         /* sky-100 */

    /* Text */
    --text-primary:   #0f172a;  /* slate-900 */
    --text-secondary: #64748b;  /* slate-500 */
    --text-accent:    #2563eb;  /* blue-600 */

    /* Glassmorphism cards */
    --card-bg:     rgba(255, 255, 255, 0.70);
    --card-border: rgba(255, 255, 255, 0.90);
    --card-shadow: 0 10px 40px -10px rgba(37, 99, 235, 0.08), 0 1px 3px rgba(0,0,0,0.02);
    --card-radius: 24px;
    --card-blur:   blur(24px);

    /* Ambient orbs */
    --orb-blue:   rgba(37,  99,  235, 0.30);  /* blue-700 */
    --orb-indigo: rgba(79,  70,  229, 0.25);  /* indigo-600 */
    --orb-sky:    rgba(56,  189, 248, 0.25);  /* sky-400 */
}
```

**CSS Implementation:**
```css
/* === BLUE SKY BASE === */
body {
    background: linear-gradient(135deg, var(--bg-from) 0%, var(--bg-to) 100%);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Grainy noise texture — adds tactile depth */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
    opacity: 0.35;
    mix-blend-mode: overlay;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* Tech grid underlay — 40px lines, fades to edges */
.sky-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(to right, rgba(14,165,233,0.08) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(14,165,233,0.08) 1px, transparent 1px);
    background-size: 40px 40px;
    -webkit-mask-image: radial-gradient(ellipse 80% 50% at 50% 50%, #000 70%, transparent 100%);
    mask-image: radial-gradient(ellipse 80% 50% at 50% 50%, #000 70%, transparent 100%);
    pointer-events: none;
}

/* Ambient orb — placed with CSS custom props */
.sky-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    pointer-events: none;
    transition: all 1.8s cubic-bezier(0.22, 1, 0.36, 1);
}

/* Glassmorphism card */
.glass-card {
    background: var(--card-bg);
    backdrop-filter: var(--card-blur);
    -webkit-backdrop-filter: var(--card-blur);
    border: 1px solid var(--card-border);
    box-shadow: var(--card-shadow);
    border-radius: var(--card-radius);
}
.glass-card:hover {
    background: rgba(255, 255, 255, 0.85);
    box-shadow: 0 20px 60px -15px rgba(37, 99, 235, 0.12), 0 2px 6px rgba(0,0,0,0.03);
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

/* Section label (small caps above headline) */
.sky-label {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: clamp(0.65rem, 1vw, 0.75rem);
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-accent);
}
.sky-label::before {
    content: '';
    width: 8px; height: 8px;
    background: #3b82f6;
    border-radius: 50%;
}

/* Gradient headline */
.sky-title-gradient {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Pill badge (top of hero slide) */
.sky-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 20px;
    border-radius: 9999px;
    background: rgba(255,255,255,0.8);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(147,197,253,0.5);
    font-size: clamp(0.65rem, 1vw, 0.75rem);
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #2563eb;
    box-shadow: 0 2px 8px rgba(37,99,235,0.08);
}
.sky-badge::before {
    content: '';
    width: 8px; height: 8px;
    background: #3b82f6;
    border-radius: 50%;
}

/* Animated connection lines (SVG, use in decorative layer) */
/* Example: <path stroke="url(#sky-line)" stroke-dasharray="10 15"
              style="animation: dash-flow 4s linear infinite" /> */
@keyframes dash-flow {
    from { stroke-dashoffset: 0; }
    to   { stroke-dashoffset: 100; }
}

/* ─── Horizontal slide transition — CORRECT layout pattern ───
 *
 * CRITICAL: The three values must be consistent or the layout breaks.
 *
 *   #stage  : overflow: hidden wrapper, fixed to viewport
 *   #track  : width = 100vw × N  (NOT 100% × N — percentages resolve differently)
 *   .slide  : width = 100vw      (NOT 100vw / N — each slide is one full viewport)
 *   JS      : translateX(-i × 100vw)   where i = 0-based slide index
 *
 * Common mistake: writing `width: calc(100vw / N)` for .slide — this makes each
 * slide 1/N of the viewport and completely collapses the layout.
 */
#stage {
    position: fixed;
    inset: 0;
    overflow: hidden;
    z-index: 1;
}
.slides-track {
    display: flex;
    flex-direction: row;
    width: calc(100vw * var(--slide-count)); /* e.g. 32 slides → 3200vw */
    height: 100%;
    transition: transform 0.7s cubic-bezier(0.22, 1, 0.36, 1); /* spring feel */
}
.slide {
    width: 100vw;          /* each slide = one full viewport, always */
    flex-shrink: 0;
    height: 100vh;
}

/* JS navigation — use vw units, not percentages */
/* track.style.transform = `translateX(-${currentIndex * 100}vw)`; */

/* Pill pagination dots */
.sky-nav {
    position: fixed;
    bottom: clamp(1rem, 2vw, 2rem);
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 12px;
    z-index: 50;
}
.sky-dot {
    height: 6px;
    border-radius: 9999px;
    background: rgba(147,197,253,0.5);
    transition: all 0.5s ease;
    width: 6px;
    cursor: pointer;
    border: none;
}
.sky-dot.active {
    background: #2563eb;
    width: 32px;
}

/* Scrollbar for content-heavy slides */
.sky-scroll {
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: rgba(147,197,253,0.5) transparent;
}
.sky-scroll::-webkit-scrollbar { width: 6px; }
.sky-scroll::-webkit-scrollbar-track { background: transparent; }
.sky-scroll::-webkit-scrollbar-thumb {
    background: rgba(147,197,253,0.5);
    border-radius: 10px;
}
```

**Signature Elements:**

1. **Animated ambient orbs** — 3 blurred radial-gradient circles (blue/indigo/sky). They reposition smoothly between slides to match content mood. Typical orb size 40–60% viewport width, `blur(80px)`, `mix-blend-mode` not needed on light bg. Animate `top`/`left`/`transform: scale()` with CSS transitions or JS.

2. **Glassmorphism cards** (`glass-card`) — `rgba(255,255,255,0.7)` + `backdrop-filter: blur(24px)`. Every content block lives in one. Use `border-radius: 24px`, white border, and subtle blue-tinted shadow.

3. **Grainy noise texture** — SVG `feTurbulence` overlay (fixed, `mix-blend-mode: overlay`, opacity ~0.35). Adds premium tactile depth without photos or illustrations.

4. **Tech grid underlay** — 40px CSS grid lines at 8% opacity, masked with radial gradient so it fades to edges. Evokes a clean data visualization canvas.

5. **Section label + headline pairing** — Always pair: small-caps blue label above → bold dark headline below. Gap ~8px. Label must have the dot prefix.

6. **Gradient headline text** — Key hero titles use `sky-title-gradient`: deep navy `#1e3a8a` → bright blue `#3b82f6`.

7. **Spring-physics slide transitions** — Horizontal track, `cubic-bezier(0.22, 1, 0.36, 1)` easing. Feels like a physical carousel, not a CSS fade. **Use the correct layout pattern in the CSS block above**: `#stage` fixed wrapper → `#track` at `100vw × N` → `.slide` at `100vw` → JS `translateX(-i * 100vw)`. Never use `calc(100vw / N)` for slide width.

8. **Pill badge** (hero slides only) — Small white pill above the main title announcing the theme/category.

9. **Flowing SVG connection lines** (optional, decorative layer) — Animated `stroke-dashoffset` paths over gradient `linearGradient` stroke, opacity 0.3. Creates a sense of data flow without heavy graphics.

10. **Cloud hero effect** (title slide only) — CSS blur-circle clusters anchored to `bottom: 0`, animated with `translateX` (two-layer loop: slow back layer + fast front layer). Use SVG `feTurbulence/feDisplacementMap` filter for organic edges. Creates an "above the clouds" launch moment.

**Orb Positioning Guide (per slide type):**
```
Hero/Title:      orb1 center-bottom(large), orb2 left-low, orb3 right-mid
Data/Split:      orb1 far-left-mid, orb2 far-right-mid, orb3 top-center(small)
Architecture:    orb1 top-center, orb2 bottom-left, orb3 bottom-right (triangle)
Grid/Cards:      orb1 top-left(large), orb2 bottom-right(large), orb3 center(mid)
Stats/Numbers:   orb1 center(very large), orb2 top-left(small), orb3 bottom-right(small)
Timeline:        orb1 left-mid, orb2 center-mid, orb3 right-mid (horizontal row)
```

**Animation Timings:**
- Slide entry: `0.8s ease [0.22, 1, 0.36, 1]`, stagger children by `0.15s`
- Orb transitions: `1.8s cubic-bezier(0.22, 1, 0.36, 1)`
- Hover effects: `0.3s ease`
- Floating orbs (continuous): `20–28s easeInOut infinite`
- Connection lines: `4–6s linear infinite`
- Cloud layers: back `30s linear infinite`, front `18s linear infinite`

---

### 6. Notebook Tabs

**Vibe:** Editorial, organized, elegant, tactile

**Layout:** Cream paper card on dark background. Colorful tabs on right edge.

**Typography:**
- Display: `Bodoni Moda` (400/700) — classic editorial
- Body: `DM Sans` (400/500)

**Colors:**
```css
:root {
    --bg-outer: #2d2d2d;
    --bg-page: #f8f6f1;
    --text-primary: #1a1a1a;
    --tab-1: #98d4bb; /* Mint */
    --tab-2: #c7b8ea; /* Lavender */
    --tab-3: #f4b8c5; /* Pink */
    --tab-4: #a8d8ea; /* Sky */
    --tab-5: #ffe6a7; /* Cream */
}
```

**Signature Elements:**
- Paper container with subtle shadow
- Colorful section tabs on right edge (vertical text)
- Binder hole decorations on left
- Tab text must scale with viewport: `font-size: clamp(0.5rem, 1vh, 0.7rem)`

---

### 7. Pastel Geometry

**Vibe:** Friendly, organized, modern, approachable

**Layout:** White card on pastel background. Vertical pills on right edge.

**Typography:**
- Display: `Plus Jakarta Sans` (700/800)
- Body: `Plus Jakarta Sans` (400/500)

**Colors:**
```css
:root {
    --bg-primary: #c8d9e6;
    --card-bg: #faf9f7;
    --pill-pink: #f0b4d4;
    --pill-mint: #a8d4c4;
    --pill-sage: #5a7c6a;
    --pill-lavender: #9b8dc4;
    --pill-violet: #7c6aad;
}
```

**Signature Elements:**
- Rounded card with soft shadow
- **Vertical pills on right edge** with varying heights (like tabs)
- Consistent pill width, heights: short → medium → tall → medium → short
- Download/action icon in corner

---

### 8. Split Pastel

**Vibe:** Playful, modern, friendly, creative

**Layout:** Two-color vertical split (peach left, lavender right).

**Typography:**
- Display: `Outfit` (700/800)
- Body: `Outfit` (400/500)

**Colors:**
```css
:root {
    --bg-peach: #f5e6dc;
    --bg-lavender: #e4dff0;
    --text-dark: #1a1a1a;
    --badge-mint: #c8f0d8;
    --badge-yellow: #f0f0c8;
    --badge-pink: #f0d4e0;
}
```

**Signature Elements:**
- Split background colors
- Playful badge pills with icons
- Grid pattern overlay on right panel
- Rounded CTA buttons

---

### 9. Vintage Editorial

**Vibe:** Witty, confident, editorial, personality-driven

**Layout:** Centered content on cream. Abstract geometric shapes as accent.

**Typography:**
- Display: `Fraunces` (700/900) — distinctive serif
- Body: `Work Sans` (400/500)

**Colors:**
```css
:root {
    --bg-cream: #f5f3ee;
    --text-primary: #1a1a1a;
    --text-secondary: #555;
    --accent-warm: #e8d4c0;
}
```

**Signature Elements:**
- Abstract geometric shapes (circle outline + line + dot)
- Bold bordered CTA boxes
- Witty, conversational copy style
- **No illustrations—only geometric CSS shapes**

---

## Specialty Themes

### 10. Neon Cyber

**Vibe:** Futuristic, techy, high-voltage confidence — Tron lightgrid meets hacker conference keynote. Dark canvas, electric glow, engineered precision.

**Layout:** Dark full-bleed background. Content in neon-bordered panels with corner-cut sci-fi geometry. Low-opacity grid overlay as structural depth.

**Typography:**
- Display: `Clash Display` (600/700) — geometric, space-age (Fontshare)
- Body: `Satoshi` (400/500) — clean sans, tech-forward (Fontshare)
- Mono labels/data: `JetBrains Mono` (400) — coordinates, timestamps, code
- All section labels: uppercase, `letter-spacing: 0.15em`

**Colors:**
```css
:root {
    --bg: #0a0f1c;
    --bg-panel: #0e1525;
    --border-glow: rgba(0, 255, 204, 0.25);
    --cyan: #00ffcc;
    --magenta: #ff00aa;
    --text: #e0f0ff;
    --text-muted: rgba(224, 240, 255, 0.5);
    --grid: rgba(0, 255, 204, 0.04);
}
```

**Signature Elements:**
- **Neon glow** — `box-shadow: 0 0 16px rgba(0,255,204,0.35), 0 0 48px rgba(0,255,204,0.1)` on borders and key headings
- **Grid overlay** — `background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px)` at 40px spacing, masked to center
- **Corner-cut panels** — `clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 0 100%)` for sci-fi HUD feel
- **Gradient accent dividers** — `linear-gradient(90deg, var(--cyan), var(--magenta))` for `2px` horizontal rules
- **Mono metadata** — timestamps / coordinates / system IDs in `JetBrains Mono` 10px at 40% opacity
- No illustrations. Geometric CSS shapes and inline SVG only.

**Named Layout Variations:**

**1. Launch Screen**
Title centered in `Clash Display` 7rem, cyan `text-shadow` glow. Subtitle in Satoshi below. Animated particle canvas behind (JS canvas, 60 dots, connecting lines < 120px). Bottom: `2px` gradient rule + mono `PRESS SPACE TO CONTINUE`.

**2. Feature Grid**
3-column grid (or 2×3). Each panel: `clip-path` corner cut, section number in mono top-right, SVG icon, feature name in Clash Display, 2-line desc in Satoshi. Hover: `border-glow` intensifies with transition.

**3. Data Pulse**
Left 55%: single KPI number in 8rem cyan with glow. Below: mono uppercase label, SVG trend arrow. Right 45%: inline SVG bar chart (cyan bars, `border-radius: 4px` top only). Faint radial-gradient pulse animation centered on the number.

**4. Signal Timeline**
Center `2px` vertical line, cyan-to-magenta gradient. Left/right alternating content blocks per milestone. Nodes: `10px` circle, cyan fill, glow. Labels in mono above each node. Line draws in via `stroke-dashoffset` animation on slide entry.

**5. Code Insight**
Full-slide terminal panel in `JetBrains Mono`. One key line highlighted with `rgba(0,255,204,0.08)` row background. Comments in `--text-muted`. One `/* ← key insight */` SVG callout arrow. Corner-cut panel edges.

**6. Split Focus**
Left 40%: slightly lighter panel (`--bg-panel`), vertical `2px` cyan rule on right edge, section label + large headline. Right 60%: body text + bullet list with cyan `›` markers. Top-right: `SYS://SECTION_NAME` in mono 10px.

**7. Signal Close**
Centered headline in cyan glow. Below: 3 CTA/contact panels in a row (bordered, corner-cut). `TRANSMISSION COMPLETE` in mono at very bottom, 30% opacity. Background: particle canvas at reduced opacity.

---

### 11. Terminal Green

**Vibe:** Developer-focused, hacker aesthetic — GitHub's dark theme as a presentation. Every slide feels like a genuine terminal session. Content is the interface.

**Layout:** Full-bleed dark background. All content in monospace. Structure through indentation, ASCII conventions, and terminal patterns — zero visual decoration.

**Typography:**
- Single font: `JetBrains Mono` (400/700) — no exceptions on any element
- Headings: 700, uppercase or `$`-prefixed, `letter-spacing: 0.04em`
- Body: 400, `line-height: 1.75`
- Sizes: tight — `clamp(0.8rem,1.2vw,1rem)` body, `clamp(1.5rem,3vw,2.5rem)` headings
- Prompt symbol: `$ ` or `> ` in muted green before "command" text

**Colors:**
```css
:root {
    --bg: #0d1117;
    --bg-panel: #161b22;
    --border: #30363d;
    --green: #39d353;
    --green-muted: rgba(57, 211, 83, 0.4);
    --text: #e6edf3;
    --text-muted: #8b949e;
    --comment: #6e7681;
    --yellow: #e3b341;   /* warnings */
    --red: #f85149;      /* errors */
    --blue: #79c0ff;     /* info / links */
}
```

**Signature Elements:**
- **Blinking cursor** — `|` with `animation: blink 1s step-end infinite` at end of last line
- **Scan lines** — `repeating-linear-gradient(transparent, transparent 2px, rgba(0,0,0,0.04) 2px, rgba(0,0,0,0.04) 4px)` fixed overlay at 50% opacity
- **Prompt prefix** — `$ ` or `> ` in `--green-muted` before any title or command text
- **Status dots** — `●` in green/yellow/red for process status
- **Panel borders** — `border: 1px solid var(--border)`, `border-radius: 6px`, no shadows
- Every element: `font-family: 'JetBrains Mono', 'Fira Code', monospace` — no exceptions

**Named Layout Variations:**

**1. Boot Sequence**
Title slide. ASCII box border around slide/project name. Below: line-by-line startup log — `[  OK  ] Loaded module...` in small mono. Last line: `> _` with blinking cursor. Feels like system initialization.

**2. Command Output**
Large `$ command --flags` in `--green` on line 1. Below: multi-line output in `--text`. 2–3 lines highlighted with `--bg-panel` row background. Bottom: next `$ ` prompt + blinking cursor.

**3. Progress Board**
Section title top. Below: 5–7 rows, each: label left, ASCII bar `[████████░░]` center, `nn%` right. Green = complete, yellow = in-progress, muted = pending. Scan lines at full opacity.

**4. File Tree**
ASCII directory structure, left-aligned. `├── `, `└── `, `│   ` in `--text-muted`. File names in `--text`. Key file highlighted in `--green`. One annotation `# ← this one` comment on highlighted line.

**5. Diff View**
`BEFORE` / `AFTER` headers in mono panels side by side. `+` prefix lines in green, unchanged lines in muted. No red deletion lines — frame changes as purely positive.  Column rule `1px --border`.

**6. Log Stream**
Timestamp column `HH:MM:SS` left in `--comment`, level badge `INFO`/`WARN` center, message right. 8–10 lines. One `WARN` line in yellow. Last line: the key insight in `--green` 700. Scan line overlay.

**7. EOF**
Minimal closing. Centered. `exit 0` or `^D` in 4rem mono, `--green`. Below: `# thanks` in `--comment`. Blinking cursor. Nothing else. Feels like a respectful shell session ending.

---

### 12. Swiss Modern

**Vibe:** Clean, precise, Bauhaus-inspired — International Typographic Style as a presentation. Form follows function absolutely. The grid is not a tool; it is the design.

**Layout:** Explicit 12-column grid, faintly visible. Content anchors to grid intersections. Asymmetric placement creates visual tension. Headlines never centered — always left or bottom-left.

**Typography:**
- Display: `Archivo Black` (900) — geometric, constructed, no-compromise
- Body: `Nunito` (400/600) — humanist, readable at small sizes
- Data labels: `Archivo` (700) uppercase, `letter-spacing: 0.08em`
- Headlines: left-aligned only, `line-height: 1.0`, no sentence case — always uppercase or title case
- Body: `line-height: 1.55`, max 55 characters per line, left-aligned

**Colors:**
```css
:root {
    --bg: #ffffff;
    --bg-dark: #0a0a0a;
    --text: #0a0a0a;
    --text-light: #ffffff;
    --text-muted: #666666;
    --red: #ff3300;       /* single accent — one element per slide maximum */
    --grid-line: rgba(0, 0, 0, 0.05);
}
```

**Signature Elements:**
- **Visible grid** — `background-image` 12-column grid at `--grid-line` opacity as `::before` pseudo on each `.slide`. Present, never overwhelming.
- **Red accent** — `#ff3300` for exactly one element per slide: a rule, a number, an underline, or a single word. Never a large fill.
- **Asymmetric anchoring** — Titles attach to left or bottom-left. Negative space is deliberately top-right. This creates tension, not emptiness.
- **Hard horizontal rules** — `2px solid #0a0a0a` for section separations. No decorative curves, no dashes.
- **Large structural numbers** — Section counts and stats in `6–9rem Archivo Black` as visual anchors.
- No gradients. No shadows. No rounded corners. No illustrations.

**Named Layout Variations:**

**1. Title Grid**
Slide number top-right in `Archivo Black` 1rem, red. Title bottom-left in 7rem, 2 lines max, `line-height: 0.95`. Empty upper-right quadrant. Red `2px` horizontal rule above the title.

**2. Column Content**
Left column 40%: large section heading + red `2px` rule below. Right column 55% (5% gap): body text in two typographic sub-columns. Section number top-right in small red.

**3. Stat Block**
One large number left half at 8rem `Archivo Black`. Vertical `2px` black rule to its right. Then: label in 1.2rem uppercase + 1-line supporting sentence in 0.9rem body. Red underline on the number only.

**4. Data Table**
Full-width table. Header row: `Archivo Black` 11px uppercase, `background: #0a0a0a`, white text. Body: alternating `#ffffff` / `#f7f7f7` rows, `1px #e0e0e0` dividers. Most important row: `3px` red left-border. No outer border.

**5. Geometric Diagram**
SVG diagram of boxes + connector lines, `stroke: #0a0a0a`, `stroke-width: 1.5`. No fills except primary node: `fill: #ff3300`. Labels in `Nunito` 12px. Grid visible behind. No shadows.

**6. Pull Quote**
One short sentence (max 12 words) in 3rem `Archivo Black`, top-left. Below it: `2px` red rule + attribution in 0.8rem `Nunito`. Remaining 50%+ of slide: pure white. Emptiness is the message.

**7. Contents Index**
Numbered list, left-aligned. Each item: section number in `3rem Archivo Black` red, em-dash, topic in `1.5rem Archivo Black` black. Max 5 items. Visible grid behind. No borders on items.

---

### 13. Paper & Ink

**Vibe:** Editorial, literary, thoughtful — a well-designed book or long-read magazine. Content is the hero; design serves it with quiet authority.

**Layout:** Generous margins, narrow content columns (max 680px), extreme vertical rhythm. Every element breathes. Slides feel like printed pages.

**Typography:**
- Display: `Cormorant Garamond` (700/900) — classical elegance, high-contrast strokes
- Body: `Source Serif 4` (400/600) — authoritative, highly readable at text sizes
- Drop caps: `Cormorant Garamond` 900, `float: left`, 4-line height, crimson
- Pull quotes: `Cormorant Garamond` 400 italic, `2rem+`
- `line-height: 1.78` for body, `line-height: 1.05` for display headlines
- All sizes: viewport-relative `clamp()` values

**Colors:**
```css
:root {
    --bg: #faf9f7;          /* warm cream */
    --bg-dark: #1a1a18;     /* rich black */
    --text: #1a1a1a;
    --text-muted: #666666;
    --crimson: #c41e3a;     /* accent — one use per slide maximum */
    --rule: #c4b8a4;        /* warm paper rule color */
}
```

**Signature Elements:**
- **Drop caps** — First letter at `clamp(3rem,6vw,5rem)`, `Cormorant Garamond` 900, `float: left`, `line-height: 0.85`, `margin-right: 0.1em`, color `--crimson`
- **Horizontal rules** — `1px solid var(--rule)`, full column width, `margin: 2rem 0`. Double-rule variant: two thin lines 4px apart for section breaks.
- **Pull quotes** — Italic `Cormorant Garamond` 400, preceded and followed by thin rule, 20px left indent. No typographic quote marks needed.
- **Roman numeral section markers** — `I`, `II`, `III` in `Cormorant Garamond` 400 small, `--text-muted`, above headings
- **Narrow column** — Content `max-width: 680px`, centered, `padding: 0 clamp(2rem,8vw,6rem)`. Feels like a page, not a screen.
- No bright colors. No geometric shapes. No gradients. Typography and rules only.

**Named Layout Variations:**

**1. Chapter Opening**
Roman numeral + chapter title in 5rem `Cormorant Garamond`, left-aligned. Thin horizontal rule below. Opening paragraph with drop cap beneath. Generous whitespace above the title (40%+ of slide height).

**2. Long Read**
Two-column body layout (magazine spread). Left: first 3 paragraphs. Right: continuation. `1px --rule` vertical separator. Pull quote spanning both columns at midpoint, breaking the grid intentionally.

**3. Pull Quote**
Single sentence in 2.5rem italic `Cormorant Garamond`, left-aligned or centered. Thin rule above and below. Attribution in 0.8rem `Source Serif 4`. Remaining slide: cream. The silence amplifies the quote.

**4. Annotated**
Main text in left 60% column. Right 40%: marginal annotation column in 0.75rem `--text-muted`, separated by `1px --rule`. Each annotation: small superscript number matching the main text.

**5. The Statistic**
One large number in `6rem Cormorant Garamond 900`, `--crimson`. Below: 2-line plain explanation in body size. Above: thin double-rule. Remaining space: cream.

**6. Index Page**
Reference list. Each entry: right-aligned page number (tabular-nums), dotted leader line `· · ·`, topic title. `Source Serif 4` body, `Cormorant Garamond` for the numbers. Max 8 entries.

**7. Colophon (Closing)**
Centered, small text only. Publication/deck title in `Cormorant Garamond` italic. Thin rule. 2–3 lines of closing copy. One crimson accent: a single word or `—` dash. Feels like the last page of a book.

---

## Font Pairing Quick Reference

| Preset | Display Font | Body Font | Source |
|--------|--------------|-----------|--------|
| Bold Signal | Archivo Black | Space Grotesk | Google |
| Electric Studio | Manrope | Manrope | Google |
| Creative Voltage | Syne | Space Mono | Google |
| Dark Botanical | Cormorant | IBM Plex Sans | Google |
| Blue Sky | System / SF Pro | System / SF Pro | System |
| Notebook Tabs | Bodoni Moda | DM Sans | Google |
| Pastel Geometry | Plus Jakarta Sans | Plus Jakarta Sans | Google |
| Split Pastel | Outfit | Outfit | Google |
| Vintage Editorial | Fraunces | Work Sans | Google |
| Neon Cyber | Clash Display | Satoshi | Fontshare |
| Terminal Green | JetBrains Mono | JetBrains Mono | JetBrains |

---

## DO NOT USE (Generic AI Patterns)

**Fonts:** Inter, Roboto, Arial, system fonts as display

**Colors:** `#6366f1` (generic indigo), purple gradients on white

**Layouts:** Everything centered, generic hero sections, identical card grids

**Decorations:** Realistic illustrations, gratuitous glassmorphism, drop shadows without purpose

---

## CSS Gotchas (Common Mistakes)

### Negating CSS Functions

**WRONG — silently ignored by browsers:**
```css
right: -clamp(28px, 3.5vw, 44px);   /* ❌ Invalid! Browser ignores this */
margin-left: -min(10vw, 100px);      /* ❌ Invalid! */
top: -max(2rem, 4vh);                /* ❌ Invalid! */
```

**CORRECT — wrap in `calc()`:**
```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));  /* ✅ */
margin-left: calc(-1 * min(10vw, 100px));     /* ✅ */
top: calc(-1 * max(2rem, 4vh));               /* ✅ */
```

CSS does not allow a leading `-` before function names like `clamp()`, `min()`, `max()`. The browser silently discards the entire declaration, causing the property to fall back to its initial/inherited value. This is especially dangerous because there is no console error — the element simply appears in the wrong position.

**Rule: Always use `calc(-1 * ...)` to negate CSS function values.**

---

## Troubleshooting Viewport Issues

### Content Overflows the Slide

**Symptoms:** Scrollbar appears, content cut off, elements outside viewport

**Solutions:**
1. Check slide has `overflow: hidden` (not `overflow: auto` or `visible`)
2. Reduce content — split into multiple slides
3. Ensure all fonts use `clamp()` not fixed `px` or `rem`
4. Add/fix height breakpoints for smaller screens
5. Check images have `max-height: min(50vh, 400px)`

### Text Too Small on Mobile / Too Large on Desktop

**Symptoms:** Unreadable text on phones, oversized text on big screens

**Solutions:**
```css
/* Use clamp with viewport-relative middle value */
font-size: clamp(1rem, 3vw, 2.5rem);
/*              ↑       ↑      ↑
            minimum  scales  maximum */
```

### Content Doesn't Fill Short Screens

**Symptoms:** Excessive whitespace on landscape phones or short browser windows

**Solutions:**
1. Add `@media (max-height: 600px)` and `(max-height: 500px)` breakpoints
2. Reduce padding at smaller heights
3. Hide decorative elements (`display: none`)
4. Consider hiding nav dots and hints on short screens

### Testing Recommendations

Test at these viewport sizes:
- **Desktop:** 1920×1080, 1440×900, 1280×720
- **Tablet:** 1024×768 (landscape), 768×1024 (portrait)
- **Mobile:** 375×667 (iPhone SE), 414×896 (iPhone 11)
- **Landscape phone:** 667×375, 896×414

Use browser DevTools responsive mode to quickly test multiple sizes.
---

## New Styles (v1.5)

### 14. Aurora Mesh

**Vibe:** Vibrant, forward-looking, premium tech — inspired by Linear.app, Vercel, Stripe marketing pages

**Layout:** Centered hero title + content area below. No columns. Full-bleed animated gradient background.

**Typography:**
- Display: `Inter` 700 or system-ui (exception: Inter is appropriate for modern SaaS aesthetic)
- Body: system-ui / -apple-system
- Title: `letter-spacing: -0.02em`, pure white
- Body: `rgba(255,255,255,0.7)`

**Colors:**
```css
:root {
    --bg-primary: #0a0a1a;
    --accent: #00f5c4;        /* cyan-green for emphasis */
    --text-primary: #ffffff;
    --text-secondary: rgba(255,255,255,0.7);
    --card-bg: rgba(255,255,255,0.05);
    --card-border: rgba(255,255,255,0.1);
}
```

**Background mesh:**
```css
body {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(120,40,200,0.4) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0,180,255,0.3) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 80%, rgba(0,255,180,0.2) 0%, transparent 50%),
        #0a0a1a;
    animation: meshDrift 20s ease-in-out infinite alternate;
}
@keyframes meshDrift {
    0%   { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}
```

**Signature Elements:**
- Animated multi-layer radial-gradient background that slowly drifts (20s cycle)
- Light glassmorphism cards: `rgba(255,255,255,0.05)` + `backdrop-filter: blur(12px)` + `border: 1px solid rgba(255,255,255,0.1)` — subtle, doesn't compete with background
- Cyan-green `#00f5c4` accent for emphasis text and divider lines
- `1px rgba(255,255,255,0.15)` separator lines
- Chinese font fallback: `"PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", system-ui`

**Reference:** [references/aurora-mesh.md](references/aurora-mesh.md)

---

### 15. Enterprise Dark

**Vibe:** Authoritative, data-driven, trustworthy — McKinsey dark deck meets Bloomberg Terminal

**Layout:** Left title column + right content area (consulting split), or full-width with structured sections

**Typography:**
- Display: system-ui / `"PingFang SC"` for Chinese, `-apple-system` for English
- `font-feature-settings: "tnum"` (tabular nums) on all numeric content
- Title: `#e6edf3`, weight 600
- Body: `#8b949e`
- KPI numbers: 48px+, bold, `#e6edf3`
- KPI labels: 11px, uppercase, `letter-spacing: 0.1em`, `#8b949e`

**Colors:**
```css
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --border: #30363d;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --accent-blue: #388bfd;
    --accent-green: #3fb950;   /* positive data */
    --accent-red: #f85149;     /* negative data */
}
```

**Signature Elements:**
- `1px #30363d` borders everywhere — thin, precise
- Background grid overlay: `opacity: 0.03` — density without distraction
- KPI card: large number + uppercase label + optional trend arrow SVG
- Table style: no outer border, `1px #30363d` row dividers, `#21262d` header bg
- Progress bars: `2px` height, `#388bfd`
- Animations: none or 300ms fade-in max
- Chinese titles: `"PingFang SC", "Source Han Sans SC", system-ui`

**Named Layout Variations:**

**1. KPI Dashboard**
2×2 or 1×3 grid of KPI cards. Each card: `border: 1px --border`, `background: --bg-secondary`, large number in `--text-primary`, uppercase mono label in `--text-secondary`, optional trend SVG arrow in `--accent-green`/`--accent-red`. All numbers: `font-variant-numeric: tabular-nums`.

**2. Consulting Split**
Left column 35% (`--bg-secondary` background, `1px --border` right edge): section number + title + 2-line context. Right column 65%: main content — bullets, table, or chart. `--accent-blue` overline on section title. No padding between columns except the border.

**3. Data Table**
Full-width. Header: `--bg-secondary` fill, `--text-secondary` 11px uppercase, `letter-spacing: 0.1em`. Body: `1px --border` row dividers. Numbers right-aligned, tabular-nums. Most important row: `3px --accent-blue` left-border. No outer border — open table style.

**4. Architecture Map**
SVG on dark background. Boxes: `1px --border` stroke, `--bg-secondary` fill, labels in 11px mono. Connector lines: `1px --text-muted`, dashed for optional paths. Key node: `2px --accent-blue` stroke. Strategic layer labels in uppercase `--text-secondary`.

**5. Comparison Matrix**
2-column. Column headers in `--accent-blue`. Row labels left in `--text-secondary`. `1px --border` grid lines. `✓` in `--accent-green`, `✗` in `--accent-red`, `—` in `--text-muted`. Summary/total row: `--bg-secondary` fill.

**6. Insight Pull**
Single key sentence in 2rem `--text-primary`, left-aligned, top-left 55% of slide. Below: `1px --accent-blue` rule + 2-line attribution in `--text-secondary` 0.8rem. Remaining right and bottom: empty dark. The emptiness signals authority.

**7. Horizontal Timeline**
Thin `1px --border` horizontal track across slide center. Milestone circles `8px`, `--accent-blue` fill, `2px` glow. Date labels above in 0.7rem mono `--text-muted`. Event labels below in 0.85rem `--text-secondary`. Active milestone: larger circle with subtle glow.

**Reference:** [references/enterprise-dark.md](references/enterprise-dark.md)

---

### 16. Glassmorphism

**Vibe:** Light, translucent, modern — Apple WWDC slides, iOS Control Center

**Layout:** Centered content in frosted glass cards, layered over colorful blurred orb background

**Typography:**
- Display: system-ui / `"SF Pro Display"` / `-apple-system`
- Body: system-ui
- Dark text on light cards: `#1a1a2e`
- Light text variant: `rgba(255,255,255,0.9)`

**Colors:**
```css
/* Background option A (cool) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);

/* Background option B (warm) */
background: linear-gradient(135deg, #f8cdda 0%, #1d6fa4 100%);
```

**Main Card:**
```css
.glass-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
.glass-card-secondary {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
}
```

**Signature Elements:**
- Blurred color orbs behind the cards (large radial-gradients, low opacity) — required for backdrop-filter to be visible
- Main card at `rgba(255,255,255,0.15)`, secondary cards at `rgba(255,255,255,0.08)`
- SF Symbols-style thin-line circle icons (CSS only)
- **PPTX export note:** Glass effect degrades to flat semi-transparent fill. Mention this in speaker notes when generating.
- Chinese font: `"PingFang SC", "Noto Sans CJK SC", system-ui`

**Reference:** [references/glassmorphism.md](references/glassmorphism.md)

---

### 17. Neo-Brutalism

**Vibe:** Bold, uncompromising, anti-aesthetic — Gumroad rebrand, indie dev manifesto

**Layout:** Asymmetric blocks, slightly rotated elements, large type dominates

**Typography:**
- Display: `Space Grotesk` 900 / `Plus Jakarta Sans` 800 — UPPERCASE or Title Case, very large
- Body: `Space Grotesk` 400
- All text: `#000000` — no exceptions on light variants

**Colors:**
```css
:root {
    /* Pick one background per presentation */
    --bg-yellow: #FFEB3B;
    --bg-orange: #FF5733;
    --bg-mint: #E8F5E9;
    --bg-white: #FAFAFA;
    --text: #000000;
    --btn-bg: #000000;
    --btn-text: #FFEB3B; /* or background color */
}
```

**Signature Elements:**
```css
/* Brutalist card — hard shadow, no radius */
.brute-card {
    border: 3px solid #000;
    border-radius: 0;
    box-shadow: 4px 4px 0 #000;
    background: white;
}
/* Stripe fill decoration */
.stripe-fill {
    background: repeating-linear-gradient(
        -45deg, #000 0px, #000 2px, transparent 2px, transparent 10px
    );
}
/* Slight rotation for handmade feel */
.rotated { transform: rotate(-1.5deg); }
/* Button */
.brute-btn {
    background: #000; color: #FFEB3B;
    border: 3px solid #000; border-radius: 0;
    box-shadow: 3px 3px 0 #000; padding: 12px 24px;
}
```
- No transitions on hover — instant `transform: translate(2px,2px)` + reduced shadow
- Chinese font: `"PingFang SC", "Noto Sans CJK SC", system-ui`

**Reference:** [references/neo-brutalism.md](references/neo-brutalism.md)

---

### 18. Chinese Chan

**Vibe:** Still, focused, contemplative — Kenya Hara design language, MUJI visual system

**Layout:** Narrow centered column (max 600px), extreme whitespace, asymmetric breathing room

**Typography:**
- Chinese: `"Noto Serif CJK SC", "Source Han Serif SC", "STSong", Georgia, serif`
- English: `"EB Garamond", "Crimson Text", Georgia, serif`
- Weight: 300–400 (light), reserve 400 for important content only
- Line height: 1.8–2.0
- Paragraph spacing: 40px+
- `font-feature-settings: "palt"` for Chinese punctuation compression

**Colors:**
```css
/* Light variant */
:root {
    --bg: #FAFAF8;           /* warm paper white */
    --text: #1a1a18;         /* warm ink black */
    --accent: #C41E3A;       /* vermilion — used sparingly */
    --accent-alt: #1B3A6B;   /* indigo — alternative accent */
}
/* Dark variant */
:root.dark {
    --bg: #1a1a18;
    --text: #f0ede8;
}
```

**Signature Elements:**
- Content width capped at 600px regardless of screen size
- 80px+ top margin above headings
- Max 1 decorative element per slide: thin 1px line, 4–6px dot, or a large ghost kanji `opacity: 0.06` as background texture
- Optional: vertical title with `writing-mode: vertical-rl`
- No gradients, no multi-color, no high-saturation blocks — ever
- Accent color used for single emphasis word only
- 800ms ease fade-in animation
- Chinese: `"Noto Serif CJK SC", "Source Han Serif SC", "STSong", Georgia, serif`

**Reference:** [references/chinese-chan.md](references/chinese-chan.md)

---

### 21. Neo-Retro Dev Deck

**Vibe:** "90s computer manuals meet modern AI dev tools" — engineering notebook aesthetic. Pixel-art icons, thick black outlines, opinionated developer voice. Feels handmade and confident, like a zine printed at a hackathon.

**Layout:** Grid paper canvas. Content in thick-bordered modular blocks, stacked with slight intentional overlap. Imperfection is a feature, not a bug. Text is short and declarative — no marketing fluff.

**Typography:**
- Display: `Barlow Condensed` (800/900) — compressed, mechanical, developer-legible
- Body: `IBM Plex Sans` (400/500) — technical, clean, trustworthy
- Code/labels: `IBM Plex Mono` (400/600) — for annotations, metrics, `// comments`
- Text: `#111111` on light, `#f7f5f0` on dark panels — no intermediate grays
- Headlines: UPPERCASE or Title Case, `letter-spacing: -0.01em`, tight `line-height: 1.0`
- Body: max 2 sentences per slide — ruthless brevity

**Colors:**
```css
:root {
    --bg: #f5f2e8;           /* engineering notebook cream */
    --grid: rgba(80, 100, 170, 0.10);  /* faint blue grid lines */
    --text: #111111;
    --pink: #FF3C7E;          /* hot pink — AI / intelligence concepts */
    --yellow: #FFE14D;        /* bright yellow — tools / builds */
    --cyan: #00C8FF;          /* cyan — web / networking */
    --border: #111111;        /* thick outlines */
    --block-bg: #ffffff;
    --block-dark: #1a1a1a;
}
```

**Grid Paper Background:**
```css
body {
    background-color: var(--bg);
    background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 24px 24px;
}
```

**Signature Elements:**
- **Thick bordered blocks** — `border: 3px solid var(--border)`, `border-radius: 0` or `4px` max, `background: var(--block-bg)`
- **Hard offset shadow** — `box-shadow: 4px 4px 0 var(--border)` on all content blocks; hover: `box-shadow: 2px 2px 0`, `transform: translate(2px, 2px)`
- **Color coding** (consistent across the deck): pink = AI/intelligence, yellow = tools/builds, cyan = web/networking
- **Pixel-style SVG icons** — 32×32px, flat colors, `2px` grid-aligned strokes, black outlines, zero gradients
- **Section badge** — `IBM Plex Mono` uppercase label in `background: var(--yellow)` pill, `border: 2px solid var(--border)`, `border-radius: 0`
- **Opinionated annotations** — `// short comment` in `IBM Plex Mono` 0.8rem, max 8 words
- No stock photos. No gradients on large areas. No rounded corners above 4px.

**Named Layout Variations:**

**1. System Architecture**
Title top-left in `Barlow Condensed`. Center: stacked horizontal layer blocks (each = a system component). Colors indicate category: pink=AI, yellow=tools, cyan=web. Each block: `3px border`, monospace label inside, hard offset shadow. Arrow connectors `2px` between layers.

**2. Evolution / Timeline**
Horizontal flow left to right. Each era: thick-bordered box, era label in `IBM Plex Mono` badge, 2-line `Barlow Condensed` description. `→` arrow between boxes. Current era: `border-color: var(--pink)`, subtle pink fill. Future: dashed border.

**3. Feature Cards**
3-card row or 2×2 grid. Each card: pixel SVG icon top-right corner, feature name in `Barlow Condensed` 1.4rem, `// 1–2 line comment` in mono below. Border: `3px --border`, hard shadow. Top border accent: one of pink/yellow/cyan per card, consistent with color system.

**4. Before / After**
Two-panel split. `BEFORE` header left (muted, `#666`), `AFTER` right (green `#22c55e` or cyan). Each panel: thick border, content in `IBM Plex Mono` or `Barlow`. Divider: `4px` hard black center line. Clear improvement framing — no bad news.

**5. Manifesto / Thesis**
Large bold statement in `Barlow Condensed` 900 UPPERCASE, 40%+ of slide. Below: 3 `// supporting points` in `IBM Plex Mono` 0.9rem. One key word in the headline: `background: var(--yellow)` highlight, `2px --border`, inline. Everything in one thick-bordered content block.

**6. Metrics Dashboard**
Pixel-style bar chart: bars are thick-bordered rectangles (not rounded), fill with color codes. Y-axis: simple tick marks in mono. Each bar labeled below in `IBM Plex Mono`. Key bar: pink or yellow fill. Title above in `Barlow Condensed`. Chart sits inside one large bordered block.

**Tone Rules:**
- Declarative sentences only: `"It runs 3× faster"` not `"We're excited to share..."`
- No buzzwords: no "revolutionary", "game-changing", "cutting-edge", "robust"
- `//` comment style for sub-points and annotations
- Numbers over adjectives: `"83ms p95"` not `"blazing fast"`
- One opinion per slide, stated plainly

---

## Font Pairing Quick Reference (updated)

| Preset | Display Font | Body Font | Source |
|--------|--------------|-----------|--------|
| Bold Signal | Archivo Black | Space Grotesk | Google |
| Electric Studio | Manrope | Manrope | Google |
| Creative Voltage | Syne | Space Mono | Google |
| Dark Botanical | Cormorant | IBM Plex Sans | Google |
| Blue Sky | System / SF Pro | System / SF Pro | System |
| Notebook Tabs | Bodoni Moda | DM Sans | Google |
| Pastel Geometry | Plus Jakarta Sans | Plus Jakarta Sans | Google |
| Split Pastel | Outfit | Outfit | Google |
| Vintage Editorial | Fraunces | Work Sans | Google |
| Neon Cyber | Clash Display | Satoshi | Fontshare |
| Terminal Green | JetBrains Mono | JetBrains Mono | JetBrains |
| Swiss Modern | Archivo | Nunito | Google |
| Paper & Ink | Cormorant Garamond | Source Serif 4 | Google |
| Aurora Mesh | Inter / system-ui | system-ui | System/Google |
| Enterprise Dark | system-ui / PingFang SC | system-ui | System |
| Glassmorphism | system-ui / SF Pro | system-ui | System |
| Neo-Brutalism | Space Grotesk | Space Grotesk | Google |
| Chinese Chan | Noto Serif CJK SC / EB Garamond | Noto Serif CJK SC | Google |
| Data Story | Inter / Noto Sans SC | Inter / Noto Sans SC | System/Google |
| Modern Newspaper | Oswald | Source Serif 4 | Google |
| Neo-Retro Dev Deck | Barlow Condensed | IBM Plex Sans | Google |

---

### 19. Data Story

**Vibe:** Clear, precise, persuasive — Figma Annual Report, Stripe Report, Bloomberg Businessweek data viz

**Layout:** Multiple layout templates: full-screen KPI, 2-column KPI+chart, full-screen bar chart, 2×2 comparison matrix

**Typography:**
- English: Inter (or system-ui) with `font-variant-numeric: tabular-nums` on all numbers
- Chinese: `"Noto Sans SC", "PingFang SC", system-ui` with tabular-nums
- KPI number: 72–96px, weight 800, color by data sentiment
- KPI label: 11px, uppercase, `letter-spacing: 0.12em`, `#64748b`

**Colors:**
```css
:root {
    /* Dark variant */
    --bg: #0f1117;
    --text: #e2e8f0;
    --text-muted: #64748b;
    --positive: #00d4aa;     /* up / good */
    --negative: #ff6b6b;     /* down / bad */
    --neutral: #e2e8f0;
    --chart-primary: #3b82f6;
    --chart-secondary: #8b5cf6;
    --chart-tertiary: #10b981;
    --grid-line: #1e293b;    /* dashed */
    --axis-line: #334155;
}
/* Light variant: swap bg=#f8f9fc, grid-line=#e2e8f0, axis=#cbd5e1 */
```

**Chart Style (pure CSS + SVG, zero library dependency):**
```css
/* Axis: 1px, no arrowhead */
/* Grid: 1px dashed, low opacity */
/* Bar: border-radius 4px top only */
/* Line: stroke-width 2.5, + 10% opacity area fill */
/* Colors: primary #3b82f6, secondary #8b5cf6, tertiary #10b981 */
```

**Signature Elements:**
- Large KPI number as visual anchor — this IS the slide
- Trend arrows: SVG `▲`/`▼` in green/red next to comparison figures
- Pure CSS+SVG charts — no Chart.js, no D3, no external dependencies
- Layout templates to choose from per slide:
  1. **Hero number** — one giant KPI fills 60% of slide
  2. **KPI row + chart** — 2-column: left KPI cards, right SVG line chart
  3. **Bar chart** — full-width bars + insight pullquote
  4. **2×2 matrix** — comparison grid with labels

**Reference:** [references/data-story.md](references/data-story.md)

---

### 20. Modern Newspaper

**Vibe:** Authoritative, punchy, "smart & pop" — Japan's new economy business media meets Swiss editorial design. Information feels curated and consequential, not decorative.

**Core Philosophy:** Swiss/Bauhaus asymmetry + extreme typographic hierarchy. Headlines occupy 30–50% of the slide area. Body text is deliberately small, making every word feel intentional. Electric Yellow punctuates — never floods. One idea per slide, no exceptions.

**Layout:** Left-heavy asymmetry. Titles anchor bottom-left or top-left. Large negative space top-right or bottom-right is intentional — it creates tension, not emptiness.

**Typography:**
- Display: `Oswald` (700/900) — condensed, high-impact, reads like a headline
- Body: `Source Serif 4` (400) — authoritative at small sizes
- Mono (dates, issue numbers, labels): `IBM Plex Mono` (400)
- **Headline-to-body ratio: minimum 10:1** (e.g., `clamp(4rem,12vw,9rem)` headline vs `clamp(0.65rem,1vw,0.85rem)` body)
- Headlines: UPPERCASE, `letter-spacing: -0.02em`
- Body: mixed case, `letter-spacing: 0.01em`, `line-height: 1.6`

**Colors:**
```css
:root {
    --bg: #f7f5f0;           /* aged newsprint white */
    --bg-dark: #111111;      /* sumi black */
    --text: #111111;
    --text-muted: #555555;
    --yellow: #FFCC00;       /* electric yellow — accent only */
    --red: #FF3333;          /* alert red — sparingly */
    --rule: #111111;         /* column rules */
}
```

**Signature Elements:**
- **Yellow bar** — 8–14px solid `#FFCC00` horizontal or vertical rule; marks transitions, section openers, and emphasis anchors. Never used as a background fill for large areas.
- **Column rules** — `1px solid #111111` vertical lines to divide grid areas, evoking newspaper columns.
- **Issue stamp** — Top corner in `IBM Plex Mono` 10px: `VOL.01 · NO.03` or a date. Grounds the slide in journalistic convention.
- **Extreme headline scale** — The headline IS the slide. `font-size: clamp(4rem, 12vw, 9rem)`, `font-weight: 900`, `text-transform: uppercase`. Body text follows at ≤ 1/10th the size.
- **Negative space as editorial choice** — At least 30% of the slide should be empty. Do not fill it.
- **Red sparingly** — `#FF3333` for one word, one number, or one callout per slide maximum. Never for large backgrounds.
- No gradients. No shadows. No illustrations. No photos. Typography and geometry only.

**CSS Implementation:**
```css
/* Base */
body {
    background: var(--bg);
    font-family: 'Source Serif 4', Georgia, serif;
    color: var(--text);
}

/* Headline — the dominant element */
.np-headline {
    font-family: 'Oswald', 'Arial Narrow', sans-serif;
    font-size: clamp(3.5rem, 11vw, 8rem);
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -0.02em;
    line-height: 0.95;
    color: var(--text);
}

/* Sub-headline */
.np-subhead {
    font-family: 'Oswald', sans-serif;
    font-size: clamp(1rem, 2.5vw, 1.8rem);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Body — deliberately small */
.np-body {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: clamp(0.65rem, 1vw, 0.85rem);
    line-height: 1.65;
    color: var(--text-muted);
    max-width: 38ch;  /* newspaper column width */
}

/* Issue / date stamp */
.np-stamp {
    font-family: 'IBM Plex Mono', monospace;
    font-size: clamp(0.55rem, 0.8vw, 0.7rem);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* Yellow accent bar */
.np-bar-h {
    width: 100%;
    height: 10px;
    background: var(--yellow);
}
.np-bar-v {
    width: 8px;
    height: 100%;
    background: var(--yellow);
    flex-shrink: 0;
}

/* Column rule */
.np-rule {
    width: 1px;
    background: var(--rule);
    align-self: stretch;
    margin: 0 clamp(1rem, 2.5vw, 2.5rem);
}

/* Red emphasis word */
.np-red { color: var(--red); }

/* Dark panel (inverted section) */
.np-dark {
    background: var(--bg-dark);
    color: #f7f5f0;
}
.np-dark .np-body { color: rgba(247,245,240,0.6); }

/* Grid — strict 12-column base */
.np-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 0 clamp(0.5rem, 1.5vw, 1.5rem);
    height: 100%;
    padding: clamp(1.5rem, 4vw, 4rem);
}
```

**Named Layout Variations:**

**1. Cover / Masthead**
Publication name top-left (small, mono), yellow horizontal bar beneath it. Off-center headline fills 40% of slide bottom-left (2–5 words). Date and issue number top-right. Subtitle 3 lines max, bottom-right corner, 8px body. Large empty zone upper-right.

**2. Breaking Headline**
One-sentence headline in 9rem Oswald occupies top 45% of slide. Yellow 10px bar separates it from evidence zone below. Below bar: two columns — left is 4–5 line body, right is one bold statistic in 3rem + 1-line label. Nothing else.

**3. Split Column**
Vertical column rule divides slide 40/60. Left 40%: black panel, yellow bar on left edge, white headline in Oswald. Right 60%: newsprint background, body text in 3 short paragraphs, mono label top-right.

**4. Data Brief**
One number dominates center-left at 8–10rem, colored `var(--yellow)` outline text (webkit-text-stroke: 3px #111, fill transparent) or solid black. Below it: 1-line label in mono. Right side: 4-bullet context list in 0.75rem body. Massive negative space top and right.

**5. Feature Story (Asymmetric)**
Headline anchors bottom-left (4rem, 3 lines max). Upper-left: yellow bar 8px + section label. Body text column bottom-right (3 short paras). Upper-right 40% of slide: completely empty. Creates cinematic tension.

**6. Contents / Index**
4–6 numbered items in two columns. Each item: `01` in 2rem Oswald yellow, em-dash, topic in 1.2rem Oswald black, 1-line descriptor in 0.7rem body. Yellow horizontal rules between items. Issue stamp top-right.

**7. Pull Quote**
Large opening quote mark `"` in 12rem Oswald at 8% opacity as background texture. Quote text in 2rem Source Serif 4, 3 lines max, left-aligned. Attribution: 1px rule + name in 0.75rem mono. Nothing else on slide.

**8. Closing / Back Page (Inverted)**
Full slide `var(--bg-dark)`. Yellow bar top-full-width. White headline bottom-left. Mono CTA bottom-right. Optional: thin red single-word emphasis. Mirrors the Cover layout but dark — signals closure.

**Prohibitions:**
- No markdown symbols in text (`#`, `*`, `**`)
- No gradients on large areas
- No drop shadows
- No centered layouts — always anchor to a corner or edge
- No more than 2 type sizes per slide (headline + body)
- `#FFCC00` and `#FF3333` never appear on the same slide together
