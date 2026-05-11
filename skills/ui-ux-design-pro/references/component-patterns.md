# Component Patterns

## Buttons

### Sizing

```css
--button-height-sm: 28px; /* inline actions, compact UI */
--button-height-md: 36px; /* standard */
--button-height-lg: 44px; /* primary CTA, mobile */

--button-padding-sm: 4px 10px;
--button-padding-md: 8px 16px;
--button-padding-lg: 10px 20px;
```

### Variants

**Primary:** Solid background. One per visible area. Use for the primary action.
**Secondary:** Border or subtle background. Supporting actions.
**Ghost:** No border or background. Inline actions, icon buttons.
**Destructive:** Red/destructive color. Requires confirmation for irreversible actions.

### States

```css
.button {
  transition: all 150ms ease;
}
.button:hover {
  filter: brightness(0.92);
}
.button:active {
  transform: scale(0.98);
}
.button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
.button:disabled {
  opacity: 0.5;
  pointer-events: none;
}
```

## Forms

### Input Field Architecture

```css
.input {
  height: var(--input-height);
  padding: 8px 12px;
  background: var(--color-surface-inset);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  transition:
    border-color 150ms,
    box-shadow 150ms;
}

.input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px oklch(0.55 0.18 250 / 0.15);
  outline: none;
}

.input-error {
  border-color: var(--color-destructive);
  box-shadow: 0 0 0 3px oklch(0.55 0.22 25 / 0.1);
}
```

### Labels

Always above the field. Font: `--label`. Required indicator: colored dot or asterisk.

```css
.label {
  font: var(--label);
  color: var(--color-text-secondary);
  margin-block-end: var(--space-1);
}
```

### Validation

- Validate inline on blur, not on keypress
- Error messages appear below the field, in `--color-destructive`
- Success state: green border + checkmark icon
- Never remove form data on error
- Group related fields with fieldset/legend

### Multi-Step Forms

- Progress indicator: numbered steps or progress bar
- Each step validated before advancing
- Back button never loses data
- Final step shows summary for review

## Data Tables

### Structure

```css
.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  font: var(--label);
  color: var(--color-text-tertiary);
  text-align: start;
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border-strong);
  white-space: nowrap;
  user-select: none;
}

.table td {
  font: var(--body);
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border-subtle);
  vertical-align: middle;
}

.table tr:hover td {
  background: var(--color-surface-hover);
}
```

### Features

**Sorting:** Click column header. Arrow icons indicate direction. Active column: bolder text.
**Filtering:** Toolbar above table. Chips for active filters. Clear-all button.
**Pagination:** Below table. Show current range + total. Prefer pagination for >100 rows.
**Row selection:** Checkbox column. Sticky action bar appears on selection.
**Expandable rows:** Chevron + expanded area indented below row.
**Inline editing:** Double-click to edit. Tab to next field. Auto-save on blur.

### Responsive Tables

Under 768px:

- Horizontal scroll with `overflow-x: auto` (preferred for data-dense)
- OR: stacked cards showing key fields only

## Cards

### Metric Card

```css
.metric-card {
  padding: var(--space-4);
  /* label + value + change indicator */
}

.metric-card .label {
  font: var(--label-micro);
  text-transform: uppercase;
}
.metric-card .value {
  font-size: var(--font-size-2xl);
  font-weight: 600;
}
.metric-card .change {
  font-size: var(--font-size-sm);
}
.metric-card .change.positive {
  color: var(--color-success);
}
.metric-card .change.negative {
  color: var(--color-destructive);
}
```

### Feature Card

Title + description + icon. Equal height in grids. Subtle hover lift.

### Settings Card

Section title + description + control (toggle, select). Horizontal layout on desktop.

## Landing Page Headers (Navbar)

Headers are the first element users see. A dated header instantly kills credibility. Always use modern patterns.

### Pattern 1: Floating Glass Navbar (Recommended Default)

```css
.navbar-floating {
  position: fixed;
  top: 16px;
  left: 16px;
  right: 16px;
  z-index: 50;
  padding: 12px 24px;
  border-radius: 16px;
  background: oklch(0.98 0 0 / 0.7);
  backdrop-filter: blur(20px) saturate(1.8);
  -webkit-backdrop-filter: blur(20px) saturate(1.8);
  border: 1px solid oklch(0.92 0 0 / 0.5);
  box-shadow:
    0 4px 24px oklch(0 0 0 / 0.06),
    0 1px 2px oklch(0 0 0 / 0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 300ms cubic-bezier(0.16, 1, 0.3, 1);
}

.navbar-floating.scrolled {
  top: 8px;
  background: oklch(0.98 0 0 / 0.9);
  box-shadow: 0 8px 32px oklch(0 0 0 / 0.1);
}
```

### Pattern 2: Minimal Sticky (Clean SaaS)

```css
.navbar-minimal {
  position: sticky;
  top: 0;
  z-index: 50;
  padding: 16px 32px;
  background: oklch(1 0 0 / 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid oklch(0.92 0 0);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
```

### Pattern 3: Split Layout (Logo Left, Nav Center, CTA Right)

```css
.navbar-split {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 24px;
  padding: 16px 40px;
}

.navbar-split .nav-links {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.navbar-split .nav-link {
  font-size: 14px;
  font-weight: 500;
  color: oklch(0.4 0 0);
  transition: color 200ms;
  text-decoration: none;
}

.navbar-split .nav-link:hover {
  color: oklch(0.15 0 0);
}
```

### Pattern 4: Mega Menu (Enterprise/Feature-rich)

```css
.mega-menu-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: oklch(1 0 0);
  border-top: 1px solid oklch(0.92 0 0);
  box-shadow: 0 16px 48px oklch(0 0 0 / 0.08);
  padding: 32px 48px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  opacity: 0;
  transform: translateY(-8px);
  pointer-events: none;
  transition: all 200ms ease;
}

.mega-menu-trigger:hover + .mega-menu-panel,
.mega-menu-panel:hover {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
```

### Pattern 5: Centered Logo (Portfolio/Brand-first)

```css
.navbar-centered {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 20px 40px;
}

.navbar-centered .nav-left {
  display: flex;
  gap: 24px;
}

.navbar-centered .nav-right {
  display: flex;
  gap: 24px;
  justify-content: flex-end;
}
```

### Mobile Header (All Patterns)

```css
.mobile-menu-toggle {
  display: none;
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .mobile-menu-toggle {
    display: flex;
    width: 40px;
    height: 40px;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: transparent;
    border: none;
    cursor: pointer;
  }

  .mobile-menu {
    position: fixed;
    inset: 0;
    z-index: 100;
    background: oklch(1 0 0 / 0.98);
    backdrop-filter: blur(20px);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transform: translateY(-100%);
    transition: transform 400ms cubic-bezier(0.16, 1, 0.3, 1);
  }

  .mobile-menu.open {
    transform: translateY(0);
  }

  .mobile-menu .nav-link {
    font-size: 24px;
    font-weight: 500;
    padding: 16px 0;
    border-bottom: 1px solid oklch(0.92 0 0);
  }
}
```

### Header Anti-Patterns (Never Do These)

- Full-width solid colored background bars (looks 2015)
- Logo + nav links all left-aligned in a row
- No `backdrop-filter` or glass effect on fixed headers
- Text-only links without hover transitions
- Using `<ul><li>` for horizontal nav without resetting styles
- Fixed header without scroll-state change (feels static)
- More than 7 nav items visible at once
- CTA button same style as nav links (should stand out)
- No mobile menu or hamburger icon on small screens
- Dropdown menus without animation or delay

### Header Design Rules

1. **Max 5-7 nav items** visible. Group the rest in dropdowns or mega menu
2. **CTA button always visible** in the navbar (right side)
3. **Floating headers** must have `top: 12-20px` gap, `border-radius: 12-20px`
4. **Glass effect** requires `backdrop-filter: blur(12-24px)` + semi-transparent bg
5. **Scroll behavior** — header should visually change on scroll (shrink, add shadow, increase opacity)
6. **Logo height** — 28-36px recommended, never larger than 44px
7. **Nav link font** — 13-15px, medium weight (500), generous spacing (24-32px gap)
8. **Mobile breakpoint** — hamburger menu below 768px, always
9. **Z-index** — navbar must be `z-index: 50+` to stay above all content
10. **Transition** — all navbar animations use `cubic-bezier(0.16, 1, 0.3, 1)` for premium feel

## Navigation

### Sidebar

```css
.sidebar {
  width: 260px;
  background: var(--color-surface-base);
  border-inline-end: 0.5px solid var(--color-border-default);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-2);
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1.5) var(--space-2);
  border-radius: var(--radius-sm);
  font: var(--body);
  color: var(--color-text-secondary);
  transition:
    background 150ms,
    color 150ms;
}

.sidebar-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-primary);
}

.sidebar-item.active {
  background: var(--color-surface-active);
  color: var(--color-text-primary);
  font-weight: 500;
}
```

### Command Palette (Cmd+K)

- Modal overlay with search input
- Grouped results: actions, pages, recent
- Keyboard navigation: ↑↓ to select, Enter to confirm, Esc to close
- Fuzzy search matching
- Show keyboard shortcuts alongside items

### Tab Systems

```css
.tabs {
  display: flex;
  gap: var(--space-1);
  border-bottom: 1px solid var(--color-border-default);
}

.tab {
  padding: var(--space-2) var(--space-3);
  font: var(--label);
  color: var(--color-text-tertiary);
  border-bottom: 2px solid transparent;
  transition: color 150ms;
}

.tab.active {
  color: var(--color-text-primary);
  border-bottom-color: var(--color-accent);
}
```

## Modals and Dialogs

- Trap focus within modal
- Esc to close
- Click backdrop to close (unless destructive action)
- Maximum width: 480px (small), 640px (medium), 960px (large)
- Sticky header and footer if content scrolls
- Use `<dialog>` element with `showModal()`
- Animate in: scale(0.95) + opacity → scale(1) + opacity

## Toast Notifications

- Fixed position: bottom-right or top-right
- Auto-dismiss: 5 seconds (info), no auto-dismiss (errors)
- Stack from bottom-up, max 3 visible
- Include close button
- Use `role="status"` or `role="alert"` for screen readers

## Empty States

- Centered illustration or icon
- Title explaining what will appear here
- Description with next step
- CTA button for primary action
- Never leave a blank space without explanation

## Loading States

### Skeleton Screens

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-surface-hover) 25%,
    var(--color-surface-raised) 50%,
    var(--color-surface-hover) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
}

@keyframes shimmer {
  from {
    background-position: 200% 0;
  }
  to {
    background-position: -200% 0;
  }
}
```

Match skeleton shapes to actual content. Never show a generic spinner for form-like content.

## AI Interface Patterns

### Chat Interface

- User messages right-aligned, assistant left-aligned
- Streaming text: render character-by-character or word-by-word
- Code blocks: syntax highlighting + copy button
- Timestamps subtle, not per-message

### Prompt Input

- Expandable textarea (grows with content)
- Submit button + keyboard shortcut (Cmd+Enter)
- Character/token count indicator
- Attachment support if applicable

### AI Loading

- Typing indicator (animated dots) for short operations < 10s
- Progress bar or step indicator for long operations
- Cancel button for operations > 5s
- Never leave user without feedback

---

## Landing Page Components

Production-tested patterns extracted from real landing pages. See `real-world-patterns.md` for full code.

### Frosted Sticky Navigation

Semi-transparent nav with backdrop blur. Maintains scroll context.

```css
nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: oklch(1 0 0 / 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid oklch(0 0 0 / 0.06);
}
```

### Numbered Section Headers

Monospace counter + gradient divider line before each section title.

```html
<div class="flex items-center gap-3 mb-6">
  <span class="text-[10px] font-mono text-indigo-400 tracking-widest">01</span>
  <span class="h-px flex-1 bg-gradient-to-r from-indigo-200 to-transparent"></span>
</div>
<h2 class="text-4xl font-bold">Section Title</h2>
```

### Bento Grid

Asymmetric card grid with mixed `col-span` / `row-span`. Use 4-column grid, max 6 cards, large radius (24-32px).

### Logo / Client Strip

Horizontal row with `grayscale(100%) opacity(0.5)` to full color on hover. 4-8 logos, `gap-12`, centered.

### Premium CTA Buttons

Two strategies: **Gradient** (tech/SaaS: `bg-gradient-to-r from-indigo-600 to-indigo-500 rounded-full`) and **Solid Warm** (hardware/consumer: `bg-[#FF7F50] rounded-[32px] shadow-[0_4px_16px_rgba(255,127,80,0.3)]`). Always include arrow-right icon.
