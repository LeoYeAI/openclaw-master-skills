# Token Architecture

## Token Layers

### Primitive Tokens

Raw values without context. The palette of available options.

```css
--color-blue-50: oklch(0.97 0.02 250);
--color-blue-500: oklch(0.55 0.18 250);
--color-blue-900: oklch(0.25 0.08 250);
--color-slate-50: oklch(0.98 0.005 260);
--color-slate-900: oklch(0.15 0.01 260);
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--radius-sm: 4px;
--radius-md: 8px;
```

### Semantic Tokens

Contextual meaning mapped to primitives.

```css
--color-text-primary: var(--color-slate-900);
--color-text-secondary: var(--color-slate-600);
--color-text-tertiary: var(--color-slate-500);
--color-text-muted: var(--color-slate-400);

--color-surface-base: var(--color-slate-50);
--color-surface-raised: #ffffff;
--color-surface-overlay: #ffffff;

--color-border-default: oklch(0 0 0 / 0.08);
--color-border-subtle: oklch(0 0 0 / 0.05);
--color-border-strong: oklch(0 0 0 / 0.12);
--color-border-focus: var(--color-blue-500);

--color-accent: var(--color-blue-500);
--color-destructive: oklch(0.55 0.22 25);
--color-warning: oklch(0.75 0.15 85);
--color-success: oklch(0.65 0.18 155);
```

### Component Tokens

Scoped to specific components for fine-tuning.

```css
--button-height: 36px;
--button-padding-x: 16px;
--button-padding-y: 8px;
--button-radius: var(--radius-sm);
--button-font-size: 14px;
--button-font-weight: 500;

--input-height: 40px;
--input-bg: var(--color-surface-inset);
--input-border: var(--color-border-default);
--input-radius: var(--radius-sm);
```

## CSS Custom Property Architecture

### Naming Convention

```
--{category}-{property}-{variant}
```

Categories: `color`, `space`, `radius`, `shadow`, `font`, `size`, `z`
Properties: `text`, `surface`, `border`, `accent`, `control`
Variants: `default`, `subtle`, `strong`, `hover`, `focus`, `disabled`

### Cascade Layers

```css
@layer tokens, reset, base, components, utilities;

@layer tokens {
  :root {
    /* primitives */
    /* semantics */
  }

  :root[data-theme="dark"] {
    /* dark overrides at semantic level only */
  }
}
```

### Theme Switching

```css
:root {
  color-scheme: light dark;

  --color-surface-base: light-dark(#fafafa, #0a0a0a);
  --color-surface-raised: light-dark(#ffffff, #141414);
  --color-text-primary: light-dark(oklch(0.15 0.01 260), oklch(0.93 0.005 260));
  --color-border-default: light-dark(oklch(0 0 0 / 0.08), oklch(1 0 0 / 0.08));
}
```

### Component-Scoped Tokens

```css
.card {
  --_bg: var(--color-surface-raised);
  --_border: var(--color-border-default);
  --_radius: var(--radius-md);
  --_padding: var(--space-4);

  background: var(--_bg);
  border: 0.5px solid var(--_border);
  border-radius: var(--_radius);
  padding: var(--_padding);
}
```

### Token Completeness Checklist

- [ ] Text: primary, secondary, tertiary, muted
- [ ] Surface: base, raised, overlay, inset
- [ ] Border: default, subtle, strong, focus
- [ ] Brand: accent, accent-hover, accent-foreground
- [ ] Semantic: success, warning, destructive (+ foregrounds)
- [ ] Control: background, border, focus-ring
- [ ] Space: complete scale (4, 8, 12, 16, 24, 32, 48, 64)
- [ ] Radius: sm, md, lg, full
- [ ] Shadow: sm, md, lg (if using shadows)
- [ ] Z-index: dropdown, sticky, modal, toast
- [ ] Font: family, size scale, weight scale
