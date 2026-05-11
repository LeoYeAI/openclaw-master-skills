# Color System

## oklch Color Space

oklch (Lightness, Chroma, Hue) produces perceptually uniform color scales — equal lightness steps look equally bright to the human eye, unlike hsl.

```css
/* Building a scale in oklch */
--blue-100: oklch(0.95 0.04 250);
--blue-200: oklch(0.88 0.08 250);
--blue-300: oklch(0.78 0.12 250);
--blue-400: oklch(0.68 0.16 250);
--blue-500: oklch(0.55 0.18 250); /* primary */
--blue-600: oklch(0.48 0.16 250);
--blue-700: oklch(0.4 0.14 250);
--blue-800: oklch(0.32 0.1 250);
--blue-900: oklch(0.22 0.06 250);
```

**Lightness:** 0 (black) to 1 (white). UI text: 0.15-0.25 on light, 0.88-0.95 on dark.
**Chroma:** 0 (gray) to ~0.4 (vivid). UI neutrals: 0.005-0.02. Accents: 0.12-0.22.
**Hue:** 0-360 degrees. Keep consistent hue across a scale.

## Building Systematic Palettes

### Neutral Scale

Tint neutrals with brand hue for cohesion:

```css
/* Slate neutrals with subtle blue tint (hue 260) */
--neutral-50: oklch(0.98 0.005 260);
--neutral-100: oklch(0.96 0.005 260);
--neutral-200: oklch(0.92 0.008 260);
--neutral-300: oklch(0.87 0.008 260);
--neutral-400: oklch(0.7 0.01 260);
--neutral-500: oklch(0.55 0.01 260);
--neutral-600: oklch(0.45 0.01 260);
--neutral-700: oklch(0.35 0.012 260);
--neutral-800: oklch(0.25 0.012 260);
--neutral-900: oklch(0.15 0.01 260);
--neutral-950: oklch(0.1 0.01 260);
```

### Semantic Colors

```css
--success: oklch(0.65 0.18 155); /* green */
--warning: oklch(0.8 0.15 85); /* amber */
--destructive: oklch(0.55 0.22 25); /* red */
--info: oklch(0.6 0.16 250); /* blue */
```

For dark mode, reduce chroma by 15-20% and increase lightness slightly:

```css
--success-dark: oklch(0.72 0.14 155);
--destructive-dark: oklch(0.65 0.18 25);
```

## Contrast and Accessibility

### APCA (Advanced Perceptual Contrast Algorithm)

APCA is more perceptually accurate than WCAG 2.x ratios:

| Content Type           | Minimum APCA (Lc) | WCAG 2.x Equivalent |
| ---------------------- | ----------------- | ------------------- |
| Body text (16px+)      | Lc 60             | ~4.5:1              |
| Large text (24px+)     | Lc 45             | ~3:1                |
| Non-text UI elements   | Lc 30             | ~3:1                |
| Placeholder / disabled | Lc 25             | —                   |

### Text Opacity Hierarchy

```css
--text-primary-opacity: 1; /* 100% — headings, body */
--text-secondary-opacity: 0.72; /* 72% — supporting text */
--text-tertiary-opacity: 0.5; /* 50% — metadata, timestamps */
--text-muted-opacity: 0.38; /* 38% — disabled, placeholder */
```

## Dark Mode Color Engineering

### Surface Elevation (Dark)

Higher surfaces = slightly lighter. Never use pure #000000.

```css
--surface-base: #0a0a0a; /* L: 4% — app canvas */
--surface-100: #111111; /* L: 7% — cards, panels */
--surface-200: #1a1a1a; /* L: 10% — dropdowns */
--surface-300: #222222; /* L: 13% — nested overlays */
--surface-overlay: #2a2a2a; /* L: 16% — modals */
```

### Surface Elevation (Light)

```css
--surface-base: #f8f9fa; /* canvas */
--surface-100: #ffffff; /* cards */
--surface-200: #ffffff; /* dropdowns (use shadow for lift) */
--surface-overlay: #ffffff; /* modals (stronger shadow) */
```

### Border Treatment (Dark vs Light)

```css
/* Dark mode: white-based borders */
--border-dark: oklch(1 0 0 / 0.08);
--border-dark-subtle: oklch(1 0 0 / 0.05);
--border-dark-strong: oklch(1 0 0 / 0.12);

/* Light mode: black-based borders */
--border-light: oklch(0 0 0 / 0.08);
--border-light-subtle: oklch(0 0 0 / 0.05);
--border-light-strong: oklch(0 0 0 / 0.12);
```

## Color Psychology by Industry

| Industry        | Primary Temperature | Recommended Hues            | Avoid           |
| --------------- | ------------------- | --------------------------- | --------------- |
| Fintech         | Cool                | Blue (250°), Slate, Emerald | Warm oranges    |
| Health          | Warm-neutral        | Teal (175°), Soft green     | Harsh reds      |
| Education       | Warm                | Blue-purple (270°), Amber   | Cold grays      |
| Enterprise B2B  | Cool-neutral        | Slate-blue (240°), Indigo   | Playful colors  |
| Creative tools  | Warm or bold        | Violet (290°), Coral        | Corporate blues |
| Developer tools | Cool                | Slate (260°), Cyan (190°)   | Warm tones      |

## Color-Blind-Safe Strategies

- Never rely on color alone for meaning — pair with icons, text, or patterns
- Use high lightness contrast between states, not just hue differences
- Test with: protanopia (red-weak), deuteranopia (green-weak), tritanopia (blue-weak)
- Safe semantic pairs: blue + orange, blue + red-orange, purple + yellow
- Avoid: red vs green without lightness contrast

## Works Cited

- [Using your design system colors with contrast-color() | daverupert.com](https://daverupert.com/2026/01/contrast-color-with-custom-design-tokens/), accessed February 18, 2026
- [Defining colors in modern CSS: Why it's time to switch to OKLCH? | Medium](https://medium.com/@alekswebnet/defining-colors-in-modern-css-why-its-time-to-switch-to-oklch-c6b972d98520), accessed February 18, 2026
- [OKLCH in CSS: why we moved from RGB and HSL | Evil Martians](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl), accessed February 18, 2026
- [Web Accessibility Color Contrast Checker | Accessible Web](https://accessibleweb.com/color-contrast-checker/), accessed February 18, 2026
