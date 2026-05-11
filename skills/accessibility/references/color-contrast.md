# Color Contrast Requirements

WCAG 2.1 requires specific contrast ratios to ensure text and UI components are readable for users with low vision or color blindness.

---

## WCAG AA Contrast Requirements

### Text Contrast (WCAG 1.4.3)

| Text Type | Minimum Ratio | Example |
|-----------|---------------|---------|
| **Normal text** (under 18pt or under 14pt bold) | **4.5:1** | Body copy, paragraphs, small headings |
| **Large text** (18pt+ or 14pt+ bold) | **3:1** | Large headings, hero text |

### UI Component Contrast (WCAG 1.4.11)

| Component | Minimum Ratio | Example |
|-----------|---------------|---------|
| **UI components** | **3:1** | Buttons, form borders, focus indicators |
| **Graphical objects** | **3:1** | Icons, chart elements, required info graphics |

---

## Testing Tools

### Browser DevTools

**Chrome DevTools**:
1. Inspect element
2. Look for contrast ratio in Styles panel next to color
3. Icons show AA/AAA pass/fail
4. Click color swatch → contrast ratio details

**Firefox DevTools**:
1. Inspect element
2. Color picker shows contrast ratio
3. Accessibility panel highlights issues

### Browser Extensions

- **axe DevTools** - Comprehensive scanner
- **WAVE** - Visual feedback overlay
- **Color Contrast Analyzer** - Manual checking

### Online Tools

- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Coolors Contrast Checker**: https://coolors.co/contrast-checker
- **Color Review**: https://color.review/

---

## Common Color Combinations

### Passing Combinations (4.5:1+)

```css
/* Black on white */
color: #000000;
background: #ffffff;
/* Ratio: 21:1 ✅ AAA */

/* Dark gray on white */
color: #595959;
background: #ffffff;
/* Ratio: 4.6:1 ✅ AA */

/* White on dark blue */
color: #ffffff;
background: #0066cc;
/* Ratio: 5.7:1 ✅ AA */

/* White on black */
color: #ffffff;
background: #000000;
/* Ratio: 21:1 ✅ AAA */

/* Dark text on light gray */
color: #1a1a1a;
background: #f5f5f5;
/* Ratio: 14.8:1 ✅ AAA */
```

### Failing Combinations (under 4.5:1)

```css
/* Light gray on white */
color: #999999;
background: #ffffff;
/* Ratio: 2.8:1 ❌ FAIL */

/* Medium gray on light gray */
color: #666666;
background: #f0f0f0;
/* Ratio: 3.4:1 ❌ FAIL (AA normal text) */
/* ✅ PASS for large text (3:1+) */

/* Blue on white */
color: #4d90fe;
background: #ffffff;
/* Ratio: 2.9:1 ❌ FAIL */
```

---

## Building Accessible Color Palettes

### Strategy 1: Start with Extremes

```css
:root {
  /* Define extremes first */
  --background: #ffffff;  /* Lightest */
  --foreground: #000000;  /* Darkest */

  /* Fill in between */
  --text-primary: #1a1a1a;    /* 16.1:1 on white */
  --text-secondary: #4d4d4d;  /* 7.5:1 on white */
  --text-muted: #737373;      /* 4.7:1 on white */
  --text-disabled: #a3a3a3;   /* 2.9:1 - use only on large text */
}

.dark {
  --background: #0a0a0a;
  --foreground: #ffffff;

  --text-primary: #f5f5f5;    /* 17.6:1 on black */
  --text-secondary: #d4d4d4;  /* 11.2:1 on black */
  --text-muted: #a3a3a3;      /* 5.9:1 on black */
}
```

### Strategy 2: Semantic Colors with Variants

```css
:root {
  /* Primary (brand) */
  --primary: #0066cc;         /* Base (might not pass on white) */
  --primary-dark: #004080;    /* 6.5:1 on white ✅ */
  --primary-light: #3399ff;   /* Use only on dark backgrounds */

  /* Success */
  --success: #10b981;         /* 2.7:1 on white ❌ */
  --success-dark: #059669;    /* 4.6:1 on white ✅ */

  /* Warning */
  --warning: #f59e0b;         /* 2.2:1 on white ❌ */
  --warning-dark: #d97706;    /* 3.9:1 on white - use large only */

  /* Error */
  --error: #ef4444;           /* 3.3:1 on white ❌ */
  --error-dark: #b91c1c;      /* 6.2:1 on white ✅ */
}

/* Usage */
.button-primary {
  background: var(--primary);
  color: white;  /* White on #0066cc = 5.7:1 ✅ */
}

.text-success {
  color: var(--success-dark);  /* Use dark variant for text */
}
```

### Strategy 3: Contrast-Safe Defaults

```css
:root {
  /* Always-safe text colors */
  --text-on-light: #1a1a1a;   /* 16.1:1 on white */
  --text-on-dark: #f5f5f5;    /* 17.6:1 on black */

  /* Always-safe backgrounds */
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-tertiary: #e5e5e5;

  /* Brand colors (decorative/large text only) */
  --brand-blue: #0066cc;
  --brand-green: #10b981;
}

/* Apply text colors automatically */
.bg-light {
  background: var(--bg-primary);
  color: var(--text-on-light);
}

.bg-dark {
  background: #1a1a1a;
  color: var(--text-on-dark);
}
```

---

## Component-Specific Patterns

### Buttons

```css
/* Primary button */
.button-primary {
  background: #0066cc;
  color: #ffffff;       /* 5.7:1 ✅ */
  border: 2px solid #0066cc;
}

.button-primary:hover {
  background: #004080;  /* Darker on hover */
}

.button-primary:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;  /* 3:1 against page background ✅ */
}

/* Secondary button */
.button-secondary {
  background: transparent;
  color: #004080;       /* 6.5:1 on white ✅ */
  border: 2px solid #737373;  /* 4.7:1 on white ✅ */
}
```

### Form Inputs

```css
input, textarea, select {
  background: #ffffff;
  color: #1a1a1a;       /* 16.1:1 ✅ */
  border: 1px solid #737373;  /* 4.7:1 ✅ */
}

input:focus {
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.25);
  /* Visible focus indicator ✅ */
}

input::placeholder {
  color: #737373;       /* 4.7:1 - borderline ⚠️ */
  /* Consider darker for AA compliance */
}
```

### Error States

```css
.error {
  color: #b91c1c;       /* 6.2:1 on white ✅ */
}

.input-error {
  border-color: #dc2626;  /* 4.5:1 on white ✅ */
}

.error-message {
  color: #991b1b;       /* 7.5:1 on white ✅ */
  background: #fef2f2;
}
```

### Links

```css
a {
  color: #0066cc;       /* 5.7:1 on white ✅ */
  text-decoration: underline;  /* Not just color */
}

a:visited {
  color: #551a8b;       /* 7.7:1 on white ✅ */
}

a:hover, a:focus {
  color: #004080;       /* 6.5:1 on white ✅ */
  text-decoration: none;
}
```

---

## Dark Mode Considerations

### Avoid Pure Black (#000000)

Pure black can cause eye strain on OLED screens. Use near-black instead:

```css
.dark {
  --background: #0a0a0a;      /* Not #000000 */
  --background-elevated: #1a1a1a;
}
```

### Reduce Contrast Slightly

Very high contrast (white on black) can be harsh. Slightly reduce:

```css
.dark {
  --text-primary: #f5f5f5;    /* Not #ffffff */
  --text-secondary: #d4d4d4;
}
```

### Test Both Modes

```css
:root {
  --background: #ffffff;
  --text: #1a1a1a;
}

.dark {
  --background: #0a0a0a;
  --text: #f5f5f5;
}

/* Both pass 4.5:1 ✅ */
```

---

## Color Blindness Considerations

### Don't Rely on Color Alone

```html
<!-- ❌ WRONG - red text only -->
<span style="color: red;">Error</span>

<!-- ✅ CORRECT - icon + text -->
<span class="error">
  <svg aria-hidden="true"><!-- Error icon --></svg>
  Error: Invalid email
</span>
```

### Use Patterns/Textures

```css
/* Chart bars */
.bar-1 { background: #0066cc url('pattern-1.svg'); }
.bar-2 { background: #10b981 url('pattern-2.svg'); }
.bar-3 { background: #f59e0b url('pattern-3.svg'); }
```

### Test with Simulators

- **Chrome DevTools**: Rendering → Emulate vision deficiencies
- **Colorblind Web Page Filter**: https://www.toptal.com/designers/colorfilter/
- **Coblis Color Blindness Simulator**: https://www.color-blindness.com/coblis-color-blindness-simulator/

---

## Quick Testing Workflow

1. **Pick foreground color**
2. **Pick background color**
3. **Test in contrast checker**:
   - Is ratio ≥ 4.5:1 for normal text? ✅
   - Is ratio ≥ 3:1 for large text/UI? ✅
4. **Adjust if needed**:
   - Darken foreground OR lighten background
   - Test again
5. **Verify in browser**:
   - Check with axe DevTools
   - View with simulated color blindness

---

## Common Failures and Fixes

| Failure | Ratio | Fix |
|---------|-------|-----|
| Light gray (#999) on white | 2.8:1 ❌ | Darken to #595959 (4.6:1 ✅) |
| Blue (#4d90fe) on white | 2.9:1 ❌ | Darken to #0066cc (5.7:1 ✅) |
| Green (#10b981) on white | 2.7:1 ❌ | Darken to #059669 (4.6:1 ✅) |
| Orange (#f59e0b) on white | 2.2:1 ❌ | Darken to #d97706 (3.9:1, large only) or #b45309 (5.0:1 ✅) |
| White on yellow (#fbbf24) | 1.4:1 ❌ | Use black text instead (13.6:1 ✅) |

---

**Key Takeaway**: Always test color contrast. Use browser DevTools or online checkers before committing to a color palette.
