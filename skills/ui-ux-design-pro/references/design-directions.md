# Design Directions

Each direction is a complete personality. Choosing one means committing: depth strategy, spacing scale, typography, radius, color temperature all change together.

---

## Precision & Density

**For:** Developer tools, admin dashboards, monitoring systems, IDE-like interfaces.

**Feel:** Tight, technical, monochrome. Information-dense but not cluttered.

```
Personality: Technical precision
Foundation:  Cool (slate, hue 260)
Depth:       Borders-only
Base:        4px spacing
Radius:      4px (sharp)
Typography:  System or geometric sans (Geist, SF Pro, Inter)
             Monospace for data
Accent:      Blue-500 (single, functional)
```

### Token Set

```css
:root {
  --font-family: "Geist", system-ui, sans-serif;
  --font-mono: "Geist Mono", "SF Mono", monospace;

  --space-base: 4px;
  --space-scale: 4, 8, 12, 16, 24, 32;

  --color-fg: oklch(0.15 0.01 260);
  --color-fg-secondary: oklch(0.4 0.01 260);
  --color-fg-muted: oklch(0.55 0.008 260);
  --color-surface: oklch(0.98 0.005 260);
  --color-surface-raised: #ffffff;
  --color-border: oklch(0 0 0 / 0.08);
  --color-accent: oklch(0.55 0.18 250);

  --radius: 4px;
  --shadow: none;
}
```

### Patterns

- Compact buttons: 28-32px height
- Dense tables: 32px row height
- Sidebar: 48px collapsed icon-only option
- Cards: border, no shadow, minimal padding

---

## Warmth & Approachability

**For:** Collaborative tools, consumer apps, onboarding flows, community platforms.

**Feel:** Generous, inviting, soft. Users feel welcome.

```
Personality: Warm and friendly
Foundation:  Warm (stone, hue 40)
Depth:       Subtle shadows
Base:        8px spacing (generous)
Radius:      10-12px (soft)
Typography:  Humanist sans (Inter, Nunito, Plus Jakarta Sans)
Accent:      Orange-500 or warm coral
```

### Token Set

```css
:root {
  --font-family: "Plus Jakarta Sans", system-ui, sans-serif;

  --space-base: 4px;
  --space-scale: 8, 12, 16, 24, 32, 48;

  --color-fg: oklch(0.18 0.01 40);
  --color-fg-secondary: oklch(0.42 0.01 40);
  --color-surface: oklch(0.97 0.008 40);
  --color-surface-raised: #ffffff;
  --color-border: oklch(0 0 0 / 0.06);
  --color-accent: oklch(0.65 0.18 50);

  --radius: 10px;
  --shadow-sm: 0 1px 3px oklch(0 0 0 / 0.08);
  --shadow-md: 0 4px 8px oklch(0 0 0 / 0.06), 0 1px 2px oklch(0 0 0 / 0.04);
}
```

### Patterns

- Generous buttons: 40-44px height, 12px radius
- Open card layouts: 24px padding, soft shadows
- Friendly illustrations in empty states
- Rounded avatars and badges

---

## Sophistication & Trust

**For:** Fintech, enterprise B2B, legal tech, insurance, healthcare.

**Feel:** Cool, composed, layered depth. Inspires confidence.

```
Personality: Sophisticated authority
Foundation:  Cool-neutral (slate, hue 240)
Depth:       Layered shadows (premium multi-layer)
Base:        4px spacing
Radius:      8px (balanced)
Typography:  Geometric sans (Outfit, Space Grotesk, DM Sans)
Accent:      Indigo or emerald (single, authoritative)
```

### Token Set

```css
:root {
  --font-family: "DM Sans", system-ui, sans-serif;

  --space-base: 4px;
  --space-scale: 4, 8, 12, 16, 24, 32, 48;

  --color-fg: oklch(0.12 0.01 240);
  --color-fg-secondary: oklch(0.38 0.01 240);
  --color-surface: oklch(0.97 0.005 240);
  --color-surface-raised: #ffffff;
  --color-border: oklch(0 0 0 / 0.06);
  --color-accent: oklch(0.5 0.16 260);

  --radius: 8px;
  --shadow-premium:
    0 0 0 0.5px oklch(0 0 0 / 0.05), 0 1px 2px oklch(0 0 0 / 0.04),
    0 2px 4px oklch(0 0 0 / 0.03), 0 4px 8px oklch(0 0 0 / 0.02);
}
```

### Patterns

- Multi-layer shadows on cards
- Refined metric displays with trend indicators
- Conservative color usage — information density without noise
- Wide tables with generous whitespace

---

## Boldness & Clarity

**For:** Modern dashboards, data-heavy products, content platforms.

**Feel:** High contrast, dramatic whitespace, decisive typography.

```
Personality: Bold and decisive
Foundation:  Neutral (true gray)
Depth:       Surface shifts + accent borders
Base:        8px spacing
Radius:      6px
Typography:  Strong sans (Outfit, Sora, Clash Display for headings)
Accent:      Vibrant single color (violet, coral, cyan)
```

### Token Set

```css
:root {
  --font-family: "Outfit", system-ui, sans-serif;

  --space-base: 4px;
  --space-scale: 8, 12, 16, 24, 32, 48, 64;

  --color-fg: oklch(0.1 0 0);
  --color-fg-secondary: oklch(0.4 0 0);
  --color-surface: oklch(0.96 0 0);
  --color-surface-raised: #ffffff;
  --color-border: oklch(0 0 0 / 0.06);
  --color-accent: oklch(0.55 0.22 300);

  --radius: 6px;
}
```

### Patterns

- Hero numbers with large type
- Full-width sections with bold spacing
- High-contrast CTA buttons
- Generous margins between sections

---

## Utility & Function

**For:** GitHub-style tools, documentation, project management, wikis.

**Feel:** Muted, functional, content-first. The UI gets out of the way.

```
Personality: Invisible utility
Foundation:  Cool-neutral (slate)
Depth:       Borders-only
Base:        4px spacing
Radius:      6px
Typography:  System or neutral sans (Inter, system-ui)
Accent:      Muted blue or green
```

### Token Set

```css
:root {
  --font-family: system-ui, -apple-system, sans-serif;
  --font-mono: ui-monospace, "SF Mono", monospace;

  --space-base: 4px;
  --space-scale: 4, 8, 12, 16, 24, 32;

  --color-fg: oklch(0.15 0.008 260);
  --color-fg-secondary: oklch(0.45 0.008 260);
  --color-surface: oklch(0.98 0.004 260);
  --color-surface-raised: #ffffff;
  --color-border: oklch(0 0 0 / 0.1);
  --color-accent: oklch(0.55 0.14 250);

  --radius: 6px;
}
```

### Patterns

- Dense tables and lists
- Sidebar navigation with nested groups
- Inline code blocks and syntax highlighting
- Compact action menus

---

## Data & Analysis

**For:** Analytics platforms, BI tools, monitoring dashboards, observability.

**Feel:** Chart-optimized, numbers-first, high information density.

```
Personality: Data-driven clarity
Foundation:  Dark mode preferred
Depth:       Surface color shifts
Base:        4px spacing
Radius:      4px (sharp for data precision)
Typography:  Tabular-nums monospace for data, sans for labels
Accent:      Multi-color palette (for chart series)
```

### Token Set

```css
:root {
  --font-family: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  --space-base: 4px;
  --space-scale: 4, 8, 12, 16, 24, 32;

  --color-fg: oklch(0.93 0.005 260);
  --color-fg-secondary: oklch(0.65 0.008 260);
  --color-surface: oklch(0.1 0.01 260);
  --color-surface-raised: oklch(0.14 0.01 260);
  --color-border: oklch(1 0 0 / 0.08);

  /* Chart palette — distinguishable, color-blind safe */
  --chart-1: oklch(0.65 0.18 250); /* blue */
  --chart-2: oklch(0.7 0.16 155); /* teal */
  --chart-3: oklch(0.75 0.15 80); /* amber */
  --chart-4: oklch(0.6 0.18 300); /* violet */
  --chart-5: oklch(0.65 0.15 20); /* coral */

  --radius: 4px;
}
```

### Patterns

- Large hero metrics with sparklines
- Grid of chart widgets
- Dense data tables with inline visualizations
- Time-range selectors
- Real-time update indicators

---

## Playful & Expressive

**For:** Creative tools, portfolio builders, social platforms, gamification.

**Feel:** Rounded, colorful, animated. Personality shines through.

```
Personality: Playful creativity
Foundation:  Warm or multicolor
Depth:       Subtle shadows + color borders
Base:        8px spacing
Radius:      16-20px (very rounded)
Typography:  Expressive sans (Outfit, Clash Display, Cabinet Grotesk)
Accent:      Bold, potentially multiple (violet, pink, lime)
```

### Token Set

```css
:root {
  --font-family: "Cabinet Grotesk", system-ui, sans-serif;

  --space-base: 4px;
  --space-scale: 8, 12, 16, 24, 32, 48;

  --color-fg: oklch(0.15 0.02 290);
  --color-fg-secondary: oklch(0.4 0.02 290);
  --color-surface: oklch(0.98 0.01 290);
  --color-surface-raised: #ffffff;
  --color-border: oklch(0 0 0 / 0.06);
  --color-accent: oklch(0.6 0.22 290);
  --color-accent-secondary: oklch(0.7 0.18 150);

  --radius: 16px;
  --shadow-playful:
    0 2px 8px oklch(0 0 0 / 0.06), 0 0 0 1px oklch(0 0 0 / 0.03);
}
```

### Patterns

- Rounded everything: cards, buttons, badges, inputs
- Subtle micro-animations on interactions
- Gradient accents (used sparingly)
- Illustrated empty states
- Colorful status badges

---

## Design System Template

When saving to `.interface-design/system.md`, use this structure:

```markdown
# Design System

## Direction

**Personality:** [Direction name]
**Foundation:** [warm | cool | neutral | tinted]
**Depth:** [borders-only | subtle-shadows | layered-shadows | surface-shifts]

## Tokens

### Spacing

Base: [4px | 8px]
Scale: [list values]

### Colors

[token definitions]

### Radius

[values by component type]

### Typography

[font families, scale, weights]

## Patterns

[component patterns with specific values]

## Decisions

[rationale for key choices with dates]
```

---

## 7 · Warm Premium Identity

For hardware products, crypto wallets, premium consumer SaaS. Builds emotional trust through warmth.

### Token Set

| Token | Value |
|---|---|
| `--brand` | `#FF7F50` (Coral) |
| `--text-primary` | `#1A1A1A` |
| `--text-secondary` | `#2D2D2D` |
| `--bg-primary` | `#FFFFFF` |
| `--bg-secondary` | `#FFF9F5` (warm tint) |
| `--shadow-brand` | `rgba(255, 127, 80, 0.15)` |
| `--radius-card` | `32px` |
| `--font-display` | `Bricolage Grotesque` |
| `--font-body` | `Inter` |

### Patterns

- **Mesh gradient backgrounds** — multi-point radial gradients with brand color at 10-15% opacity
- **Frosted sticky navigation** — `backdrop-filter: blur(20px) saturate(180%)`
- **Bento grid layout** — asymmetric cards with device mockups, 4-column grid
- **Brand-tinted shadows** — `box-shadow: 0 8px 32px rgba(255, 127, 80, 0.15)`
- **Extra-large border radius** — 32-40px for premium feel
- **Logo strip** — grayscale-to-color hover for partner credibility
- **Warm neutrals** — warm gray scale (#1A1A1A / #2D2D2D), not slate/cool gray

### Anti-patterns

- Cool or slate color temperatures (breaks warmth)
- Sharp corners (< 16px radius)
- Generic gray shadows with no brand tint
- Dark mode as default (light mode establishes trust)
- Overusing coral — reserve for CTAs and accents only
