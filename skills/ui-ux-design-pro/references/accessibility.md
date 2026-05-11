# Accessibility

## WCAG 2.2 Level AA Requirements

### Contrast

| Content                                | Minimum Ratio (WCAG 2.x) | APCA (Lc)                    |
| -------------------------------------- | ------------------------ | ---------------------------- |
| Body text (< 18px)                     | 4.5:1                    | Lc 60+                       |
| Large text (18px+ bold, 24px+ regular) | 3:1                      | Lc 45+                       |
| UI components & graphics               | 3:1                      | Lc 30+                       |
| Decorative / disabled                  | No requirement           | —                            |
| Placeholder text                       | —                        | Lc 25+ (readable but subtle) |

### APCA Usage

APCA is recommended by WCAG 3.0 draft.

```text
Lc 90+: Body text, running copy
Lc 75:  Comfortable body text
Lc 60:  Small text, labels
Lc 45:  Large headings, icons
Lc 30:  Non-text UI boundaries
Lc 15:  Invisible to most — decorative only
```

## Keyboard Navigation

### Core Requirements

- Every interactive element reachable via Tab
- Tab order matches visual order (never use `tabindex > 0`)
- Enter / Space activates buttons and links
- Arrow keys navigate within compound widgets (tabs, menus, radio groups)
- Escape closes modals, dropdowns, tooltips
- Home / End jump to first/last items in lists

### Focus Management

```css
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

:focus:not(:focus-visible) {
  outline: none;
}
```

Rules:

- Move focus to dialog/modal when opened
- Return focus to trigger element when closed
- Trap focus within modals (no tabbing outside)
- Skip link as first focusable element

### Focus Trap Pattern

```javascript
function trapFocus(element) {
  const focusable = element.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  element.addEventListener("keydown", (e) => {
    if (e.key !== "Tab") return;
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });
}
```

## ARIA Patterns

### Dialog

```html
<dialog role="dialog" aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm deletion</h2>
  <p>This action cannot be undone.</p>
  <button>Cancel</button>
  <button>Delete</button>
</dialog>
```

### Tabs

```html
<div role="tablist" aria-label="Settings">
  <button role="tab" aria-selected="true" aria-controls="panel-general">
    General
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-security">
    Security
  </button>
</div>
<div role="tabpanel" id="panel-general" aria-labelledby="tab-general">
  <!-- content -->
</div>
```

### Dropdown Menu

```html
<button aria-haspopup="menu" aria-expanded="false">Options</button>
<ul role="menu" hidden>
  <li role="menuitem">Edit</li>
  <li role="menuitem">Duplicate</li>
  <li role="separator"></li>
  <li role="menuitem">Delete</li>
</ul>
```

### Live Regions

```html
<!-- For status updates (polite: waits for user pause) -->
<div role="status" aria-live="polite">3 items selected</div>

<!-- For urgent alerts (assertive: interrupts immediately) -->
<div role="alert" aria-live="assertive">Error: Connection lost</div>
```

## Semantic HTML

### Landmark Regions

```html
<body>
  <header role="banner">
    <nav role="navigation" aria-label="Main">...</nav>
  </header>
  <main role="main">
    <section aria-labelledby="section-title">
      <h2 id="section-title">Dashboard</h2>
    </section>
  </main>
  <aside role="complementary">...</aside>
  <footer role="contentinfo">...</footer>
</body>
```

### Heading Hierarchy

One `<h1>` per page. Sequential nesting: h1 → h2 → h3. Never skip levels.

## Touch Targets

| Platform           | Minimum Size   | Recommended    |
| ------------------ | -------------- | -------------- |
| iOS (Apple HIG)    | 44 × 44 pt     | 48 × 48 pt     |
| Android (Material) | 48 × 48 dp     | 48 × 48 dp     |
| Web (WCAG 2.2)     | 24 × 24 CSS px | 44 × 44 CSS px |

Add padding to hit areas even if visual element is smaller:

```css
.icon-button {
  width: 24px;
  height: 24px;
  padding: 10px; /* total touch area: 44px */
  margin: -10px; /* maintain visual position */
}
```

## Media Queries for Preferences

```css
@media (prefers-reduced-motion: reduce) {
  /* Reduce or remove animations */
}

@media (prefers-contrast: more) {
  :root {
    --color-border-default: oklch(0 0 0 / 0.2);
    --color-text-secondary: oklch(0 0 0 / 0.8);
  }
}

@media (prefers-color-scheme: dark) {
  /* Dark mode adjustments if not using toggle */
}

@media (forced-colors: active) {
  /* Windows High Contrast Mode */
  .button {
    border: 2px solid ButtonText;
  }
}
```

## Screen Reader Best Practices

- Visually hidden text for context: `.sr-only` class
- `aria-label` for icon-only buttons
- `aria-describedby` to link inputs with help text
- `alt` text on informative images, `alt=""` on decorative
- Announce dynamic content changes with live regions
- Test with NVDA (Windows), VoiceOver (Mac), or Orca (Linux)

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## Works Cited

- [Mastering ARIA: Fixing Common Beginner Mistakes | Medium](https://medium.com/@askParamSingh/mastering-aria-fixing-common-beginner-mistakes-9a9e51248ca9), accessed February 18, 2026
- [AI has an accessibility problem: What devs can do about it | LogRocket](https://blog.logrocket.com/ai-has-an-accessibility-problem/), accessed February 18, 2026

