# Depth and Elevation

## Four Strategies

Choose ONE and commit. Don't mix.

### 1. Borders-Only (Flat)

Clean, technical, dense. For utility-focused tools where density matters.

```css
--border-default: oklch(0 0 0 / 0.08);
--border-subtle: oklch(0 0 0 / 0.05);
--border-strong: oklch(0 0 0 / 0.12);
--border-focus: oklch(0.55 0.18 250);

.card {
  border: 0.5px solid var(--border-default);
}
.divider {
  border-top: 0.5px solid var(--border-subtle);
}
.card:hover {
  border-color: var(--border-strong);
}
```

**Used by:** Linear, Raycast, most developer tools.

### 2. Subtle Single Shadow

Soft lift without complexity. Approachable products.

```css
--shadow-sm: 0 1px 2px oklch(0 0 0 / 0.05);
--shadow-md: 0 2px 4px oklch(0 0 0 / 0.06), 0 1px 2px oklch(0 0 0 / 0.04);
--shadow-lg: 0 4px 8px oklch(0 0 0 / 0.08), 0 2px 4px oklch(0 0 0 / 0.04);

.card {
  box-shadow: var(--shadow-sm);
}
.card:hover {
  box-shadow: var(--shadow-md);
}
.dropdown {
  box-shadow: var(--shadow-lg);
}
```

### 3. Layered Shadows (Premium)

Rich, dimensional, multi-layer. Cards feel like physical objects.

```css
--shadow-premium:
  0 0 0 0.5px oklch(0 0 0 / 0.05), 0 1px 2px oklch(0 0 0 / 0.04),
  0 2px 4px oklch(0 0 0 / 0.03), 0 4px 8px oklch(0 0 0 / 0.02);

--shadow-premium-hover:
  0 0 0 0.5px oklch(0 0 0 / 0.06), 0 2px 4px oklch(0 0 0 / 0.05),
  0 4px 8px oklch(0 0 0 / 0.04), 0 8px 16px oklch(0 0 0 / 0.03);

--shadow-dropdown:
  0 0 0 1px oklch(0 0 0 / 0.05), 0 4px 12px oklch(0 0 0 / 0.08),
  0 8px 24px oklch(0 0 0 / 0.06);
```

**Used by:** Stripe, Mercury.

### 4. Surface Color Shifts

Background tints establish hierarchy without any shadows.

```css
/* Light mode */
--surface-page: #f5f5f5;
--surface-card: #ffffff;
--surface-input: #f0f0f0;

/* Dark mode */
--surface-page: #0a0a0a;
--surface-card: #141414;
--surface-input: #0d0d0d;
```

## Surface Stacking System

```css
Level 0: App canvas (base background)
Level 1: Cards, panels (same visual plane)
Level 2: Dropdowns, popovers (floating)
Level 3: Modals, dialogs (overlay)
Level 4: Tooltips, toasts (highest)
```

### Dark Mode Elevation Values

Each level: +3-4% lightness from previous.

```css
--elevation-0: oklch(0.1 0.01 260); /* base */
--elevation-1: oklch(0.13 0.01 260); /* cards */
--elevation-2: oklch(0.16 0.01 260); /* dropdowns */
--elevation-3: oklch(0.19 0.01 260); /* modals */
--elevation-4: oklch(0.22 0.01 260); /* tooltips */
```

### Light Mode Elevation

Use shadow intensity, not color change:

```css
--elevation-0: transparent; /* base */
--elevation-1: 0 1px 2px oklch(0 0 0 / 0.05); /* cards */
--elevation-2: 0 4px 12px oklch(0 0 0 / 0.08); /* dropdowns */
--elevation-3: 0 8px 24px oklch(0 0 0 / 0.12); /* modals */
```

## Glassmorphism 2.0: Spatial Materiality
Move beyond simple blur. Create physical glass with thickness, refraction, and surface imperfections.

### The "2.0" Recipe

1. **Base**: `backdrop-filter: blur(20px) saturate(180%)` (High saturation boosts colors behind).
2. **Noise Layer**: Transparent noise pattern at 2-5% opacity to reduce banding/dithering.
3. **Specular Border**: Gradient border mimicking light hitting the edge.

```css
.glass-card-2 {
  /* Base */
  backdrop-filter: blur(20px) saturate(180%);
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.05) 100%
  );
  
  /* Specular Border & Shadow */
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 
    0 4px 24px -1px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset; /* Inner glow */
}

/* Dark Mode Variant */
.glass-card-dark {
  backdrop-filter: blur(24px) saturate(150%);
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.01) 100%
  );
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
}
```

**Use for:** Floating elements only (Modals, Sticky Headers, Command Palettes). Never for main content backgrounds.

## Works Cited

- [Designing for visionOS | Apple Developer Documentation](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos), accessed February 18, 2026
- [Spatial UI Design Concept for Apple Vision Pro — Case Study | Medium](https://kevinnkwok.medium.com/spatial-ui-design-concept-for-apple-vision-pro-case-study-5c85f5031bf), accessed February 18, 2026
- [12 Glassmorphism UI Features, Best Practices, and Examples | UX Pilot](https://uxpilot.ai/blogs/glassmorphism-ui), accessed February 18, 2026
- [Glassmorphism CSS Generator | SquarePlanet](https://hype4.academy/tools/glassmorphism-generator), accessed February 18, 2026
- [Spatial UI Concept Tailwind CSS template | pixelcave](https://pixelcave.com/freebies/spatial-ui-concept-tailwind-css), accessed February 18, 2026
- [Why does z-index not work? | Stack Overflow](https://stackoverflow.com/questions/9191803/why-does-z-index-not-work), accessed February 18, 2026
- [Understanding z-index | MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Positioned_layout/Understanding_z-index), accessed February 18, 2026
- [Today I Learned: Layouts and the Z-Index Trap in React | DEV Community](https://dev.to/minoosh/today-i-learned-layouts-and-the-z-index-trap-in-react-366f), accessed February 18, 2026


## Border Progression


```css
--border-none: transparent;
--border-subtle: oklch(0 0 0 / 0.04); /* barely there */
--border-default: oklch(0 0 0 / 0.08); /* standard */
--border-strong: oklch(0 0 0 / 0.12); /* emphasis */
--border-strongest: oklch(0 0 0 / 0.18); /* focus rings */
```

### Border Radius Scale

```css
/* Sharp (technical) */ /* Soft (friendly) */
--radius-sm: 4px;
--radius-sm: 6px;
--radius-md: 6px;
--radius-md: 10px;
--radius-lg: 8px;
--radius-lg: 14px;
--radius-xl: 12px;
--radius-xl: 20px;
--radius-full: 9999px;
--radius-full: 9999px;
```

Sharper = technical. Rounder = friendly. Pick a personality and commit.

## Dark Mode Depth

Shadows barely work on dark backgrounds. Strategies:

1. **Increase border opacity** — borders carry more weight in dark mode
2. **Use surface lightness** — higher elevation = lighter surface
3. **Subtle inner glow** — `inset 0 1px 0 oklch(1 0 0 / 0.04)` on cards
4. **Ring shadows** — `0 0 0 1px oklch(1 0 0 / 0.06)` for containment

```css
/* Dark mode card — borders + surface, no shadows */
.card-dark {
  background: var(--elevation-1);
  border: 0.5px solid oklch(1 0 0 / 0.08);
  border-radius: var(--radius-md);
}
```
