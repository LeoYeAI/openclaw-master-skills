# Typography

## Type Scale

Use a modular scale ratio to generate harmonious sizes.

| Ratio | Name           | Sizes (base 16px)          |
| ----- | -------------- | -------------------------- |
| 1.200 | Minor Third    | 11, 13, 16, 19, 23, 28, 33 |
| 1.250 | Major Third    | 10, 13, 16, 20, 25, 31, 39 |
| 1.333 | Perfect Fourth | 9, 12, 16, 21, 28, 38, 50  |

**Recommended for interfaces:** Major Third (1.250) — enough contrast without extremes.

```css
--font-size-xs: 0.75rem; /* 12px — badges, captions */
--font-size-sm: 0.8125rem; /* 13px — labels, metadata */
--font-size-base: 0.875rem; /* 14px — body text (dense UI) */
--font-size-md: 1rem; /* 16px — body text (comfortable) */
--font-size-lg: 1.125rem; /* 18px — section titles */
--font-size-xl: 1.25rem; /* 20px — page subtitles */
--font-size-2xl: 1.5rem; /* 24px — page titles */
--font-size-3xl: 1.875rem; /* 30px — hero headings */
--font-size-4xl: 2.25rem; /* 36px — display */
```

## Fluid Typography with clamp()

```css
--font-size-hero: clamp(1.875rem, 1.5rem + 1.5vw, 3rem);
--font-size-title: clamp(1.25rem, 1rem + 1vw, 1.75rem);
--font-size-body: clamp(0.875rem, 0.8rem + 0.2vw, 1rem);
```

## Font Weight Hierarchy

```css
--font-weight-normal: 400; /* body text */
--font-weight-medium: 500; /* labels, UI text, buttons */
--font-weight-semibold: 600; /* headings, emphasis */
--font-weight-bold: 700; /* hero headings only */
```

Combine size + weight + spacing for hierarchy. Never rely on size alone.

## Letter Spacing

```css
--tracking-tighter: -0.025em; /* large headings 24px+ */
--tracking-tight: -0.015em; /* medium headings */
--tracking-normal: 0; /* body text */
--tracking-wide: 0.025em; /* labels, overlines */
--tracking-wider: 0.05em; /* all-caps labels */
```

Rule: as size increases, tracking should decrease. Large text at 0 tracking looks loose.

## Line Height

```css
--leading-none: 1; /* single-line: badges, buttons */
--leading-tight: 1.25; /* headings */
--leading-snug: 1.375; /* subheadings */
--leading-normal: 1.5; /* body text */
--leading-relaxed: 1.625; /* long-form reading */
```

## Font Pairing Strategies

### Monotype Pairings (one family)

Use weight and size contrast within a single variable font:

- **Inter** — excellent for UI: variable weight, tabular nums, optical sizing
- **Geist** — Vercel's font: clean, technical, wide character set
- **SF Pro** — Apple system: pairs display + text + mono

### Complementary Pairing

- Headlines: geometric sans (e.g., Outfit, Space Grotesk)
- Body: humanist sans (e.g., Inter, Source Sans)
- Data: monospace (e.g., JetBrains Mono, Geist Mono, SF Mono)

### Variable Fonts for Performance

```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/Inter.var.woff2") format("woff2-variations");
  font-weight: 100 900;
  font-display: swap;
  font-style: normal;
}
```

Variable fonts reduce HTTP requests and enable smooth weight animations.

## Data Typography

```css
.data-value {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}

.data-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}
```

## Complete Typography Token Set

```css
:root {
  --font-sans: "Inter", system-ui, -apple-system, sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", "Consolas", monospace;

  /* Heading */
  --heading-1: 600 var(--font-size-2xl)/var(--leading-tight) var(--font-sans);
  --heading-2: 600 var(--font-size-xl)/var(--leading-tight) var(--font-sans);
  --heading-3: 600 var(--font-size-lg)/var(--leading-snug) var(--font-sans);

  /* Body */
  --body: 400 var(--font-size-base)/var(--leading-normal) var(--font-sans);
  --body-strong: 500 var(--font-size-base)/var(--leading-normal)
    var(--font-sans);

  /* Label */
  --label: 500 var(--font-size-sm)/var(--leading-none) var(--font-sans);
  --label-micro: 500 var(--font-size-xs)/var(--leading-none) var(--font-sans);

  /* Code */
  --code: 400 var(--font-size-sm)/var(--leading-normal) var(--font-mono);
}
```
