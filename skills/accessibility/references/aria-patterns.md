# ARIA Patterns and Best Practices

**Golden Rule**: No ARIA is better than bad ARIA. Use semantic HTML first, ARIA only when HTML can't express the pattern.

---

## Five Rules of ARIA

1. **Use semantic HTML when possible** - `<button>` not `<div role="button">`
2. **Don't change native semantics** - Don't add role to elements that already have it
3. **All interactive elements must be keyboard accessible** - ARIA doesn't add keyboard support
4. **Don't hide focusable elements with aria-hidden="true"** - Creates inaccessible content
5. **All interactive elements must have an accessible name** - Use label, aria-label, or aria-labelledby

---

## ARIA Attribute Categories

### Roles

Define what an element is (button, dialog, tab, etc.)

### States

Define current condition (aria-expanded, aria-pressed, aria-checked)

### Properties

Define characteristics (aria-label, aria-labelledby, aria-describedby)

---

## Common ARIA Roles

### Landmark Roles

**Use when**: HTML5 semantic elements aren't available (legacy support).

```html
<!-- Prefer HTML5 -->
<main>Content</main>
<nav>Links</nav>
<aside>Sidebar</aside>
<footer>Footer</footer>

<!-- ARIA fallback for older browsers -->
<div role="main">Content</div>
<div role="navigation">Links</div>
<div role="complementary">Sidebar</div>
<div role="contentinfo">Footer</div>
```

**Modern approach**: Use HTML5 elements, they have implied roles.

### Widget Roles

#### Button

```html
<!-- ✅ Prefer native -->
<button>Click me</button>

<!-- ⚠️ Only if you must use div -->
<div role="button" tabindex="0" onclick="..." onkeydown="handleEnterSpace">
  Click me
</div>
```

**Critical**: Role alone doesn't add keyboard support - you must handle Enter/Space keys.

#### Checkbox

```html
<!-- ✅ Prefer native -->
<input type="checkbox" id="agree">

<!-- ⚠️ Custom (requires full implementation) -->
<div
  role="checkbox"
  aria-checked="false"
  tabindex="0"
  onkeydown="handleSpace"
>
  <svg><!-- Check icon --></svg>
  Label
</div>
```

#### Tab, Tablist, Tabpanel

```html
<div role="tablist" aria-label="Content tabs">
  <button
    role="tab"
    aria-selected="true"
    aria-controls="panel-1"
    id="tab-1"
    tabindex="0"
  >
    Tab 1
  </button>
  <button
    role="tab"
    aria-selected="false"
    aria-controls="panel-2"
    id="tab-2"
    tabindex="-1"
  >
    Tab 2
  </button>
</div>

<div role="tabpanel" id="panel-1" aria-labelledby="tab-1" tabindex="0">
  Content 1
</div>
<div role="tabpanel" id="panel-2" aria-labelledby="tab-2" tabindex="0" hidden>
  Content 2
</div>
```

**Keyboard**: Arrow keys navigate tabs, Home/End jump to first/last.

#### Dialog/Modal

```html
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-desc"
>
  <h2 id="dialog-title">Confirm action</h2>
  <p id="dialog-desc">Are you sure you want to delete this item?</p>
  <button>Cancel</button>
  <button>Delete</button>
</div>
```

**Critical**: Must trap focus, prevent background interaction.

#### Menu/Menubar

```html
<ul role="menu" aria-label="Actions">
  <li role="none">
    <button role="menuitem">Edit</button>
  </li>
  <li role="none">
    <button role="menuitem">Delete</button>
  </li>
</ul>
```

**Keyboard**: Arrow keys navigate, Enter activates, Escape closes.

---

## Common ARIA Properties

### aria-label

**Use when**: No visible label exists.

```html
<!-- Icon button without visible text -->
<button aria-label="Close dialog">
  ×
</button>

<!-- Search input with no visible label -->
<input type="search" aria-label="Search products" placeholder="Search...">

<!-- Multiple nav elements -->
<nav aria-label="Primary">...</nav>
<nav aria-label="Footer">...</nav>
```

**Caution**: Overrides visible text - don't use when visible label exists.

### aria-labelledby

**Use when**: Label text exists elsewhere in DOM.

```html
<h2 id="dialog-title">Delete item</h2>
<div role="dialog" aria-labelledby="dialog-title">
  <!-- Dialog content -->
</div>

<!-- Multiple IDs for compound label -->
<h3 id="section-title">Payment details</h3>
<p id="section-desc">Enter your credit card information</p>
<form aria-labelledby="section-title section-desc">
  <!-- Form fields -->
</form>
```

### aria-describedby

**Use for**: Additional description beyond label.

```html
<label for="password">Password</label>
<input
  type="password"
  id="password"
  aria-describedby="password-req"
>
<span id="password-req">Minimum 8 characters, one uppercase, one number</span>

<!-- Error message -->
<input
  type="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<span id="email-error" role="alert">
  Please enter a valid email address
</span>
```

### aria-hidden

**Use for**: Hiding decorative elements from screen readers.

```html
<!-- Decorative icon next to text -->
<button>
  <svg aria-hidden="true"><!-- Icon --></svg>
  Save
</button>

<!-- Font icon -->
<span class="icon-check" aria-hidden="true"></span>
<span>Complete</span>
```

**Critical**: Never use on focusable elements - makes them inaccessible.

---

## Common ARIA States

### aria-expanded

**Use for**: Collapsible elements (accordions, dropdowns).

```html
<!-- Collapsed -->
<button aria-expanded="false" aria-controls="content-1">
  Show more
</button>
<div id="content-1" hidden>
  Additional content
</div>

<!-- Expanded -->
<button aria-expanded="true" aria-controls="content-1">
  Show less
</button>
<div id="content-1">
  Additional content
</div>
```

### aria-pressed

**Use for**: Toggle buttons.

```html
<!-- Off -->
<button aria-pressed="false">
  <svg><!-- Mute icon --></svg>
  Mute
</button>

<!-- On -->
<button aria-pressed="true">
  <svg><!-- Unmute icon --></svg>
  Unmute
</button>
```

### aria-checked

**Use for**: Custom checkboxes/radio buttons.

```html
<div role="checkbox" aria-checked="false" tabindex="0">
  <svg><!-- Checkbox icon --></svg>
  I agree to terms
</div>

<!-- Tri-state (indeterminate) -->
<div role="checkbox" aria-checked="mixed" tabindex="0">
  Select all
</div>
```

### aria-invalid

**Use for**: Form validation errors.

```html
<label for="email">Email</label>
<input
  type="email"
  id="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<span id="email-error" role="alert">
  Email format is incorrect
</span>
```

### aria-selected

**Use for**: Selected items in lists, tabs.

```html
<div role="tablist">
  <button role="tab" aria-selected="true">Active tab</button>
  <button role="tab" aria-selected="false">Inactive tab</button>
</div>
```

### aria-current

**Use for**: Current item in navigation, pagination, breadcrumbs.

```html
<!-- Navigation -->
<nav>
  <a href="/">Home</a>
  <a href="/about">About</a>
  <a href="/products" aria-current="page">Products</a>
</nav>

<!-- Steps -->
<ol>
  <li><a href="/step1">Complete</a></li>
  <li><a href="/step2" aria-current="step">In progress</a></li>
  <li><a href="/step3">Pending</a></li>
</ol>
```

**Values**: `page`, `step`, `location`, `date`, `time`, `true`

---

## Live Regions

### aria-live

**Use for**: Dynamic content updates that should be announced.

```html
<!-- Polite: Wait for pause in speech -->
<div aria-live="polite">
  3 new messages
</div>

<!-- Assertive: Interrupt immediately -->
<div aria-live="assertive">
  Error: Connection lost
</div>
```

**Politeness levels**:
- `off` - Don't announce (default)
- `polite` - Wait for pause (most updates)
- `assertive` - Interrupt (errors, critical alerts only)

### role="status"

**Shorthand for aria-live="polite"**.

```html
<div role="status">
  Form submitted successfully
</div>
```

### role="alert"

**Shorthand for aria-live="assertive"**.

```html
<div role="alert">
  Error: Please fix the errors above
</div>
```

### aria-atomic

**Use with live regions** to read entire region vs. only changes.

```html
<!-- Read only changes -->
<div aria-live="polite" aria-atomic="false">
  <span id="count">5</span> unread messages
</div>
<!-- Announces: "6" when count changes -->

<!-- Read entire region -->
<div aria-live="polite" aria-atomic="true">
  <span id="count">5</span> unread messages
</div>
<!-- Announces: "6 unread messages" -->
```

---

## Complex Widget Patterns

### Accordion

```html
<div class="accordion">
  <h3>
    <button
      aria-expanded="false"
      aria-controls="panel-1"
      id="accordion-1"
    >
      Section 1
    </button>
  </h3>
  <div id="panel-1" role="region" aria-labelledby="accordion-1" hidden>
    Content for section 1
  </div>
</div>
```

**Keyboard**: Enter/Space toggles, Arrow keys move between headers (optional).

### Combobox (Autocomplete)

```html
<label for="country">Country</label>
<input
  type="text"
  id="country"
  role="combobox"
  aria-expanded="false"
  aria-controls="countries-list"
  aria-autocomplete="list"
  aria-activedescendant=""
>
<ul id="countries-list" role="listbox" hidden>
  <li role="option" id="option-1">United States</li>
  <li role="option" id="option-2">United Kingdom</li>
</ul>
```

**Keyboard**: Arrow keys navigate options, Enter selects, Escape closes.

### Tooltip

```html
<button aria-describedby="tooltip">
  <svg><!-- Info icon --></svg>
</button>
<div id="tooltip" role="tooltip" hidden>
  Additional information about this feature
</div>
```

**Show on hover/focus, hide on Escape**.

---

## ARIA Authoring Practices (APG) Patterns

Full reference: https://www.w3.org/WAI/ARIA/apg/patterns/

### Most Common Patterns

- **Accordion** - Collapsible sections
- **Alert** - Important messages
- **Breadcrumb** - Navigation path
- **Button** - Clickable action
- **Combobox** - Autocomplete input
- **Dialog (Modal)** - Overlay requiring interaction
- **Disclosure** - Show/hide content
- **Listbox** - Selectable list
- **Menu/Menubar** - Application menu
- **Tabs** - Tabbed interface
- **Tooltip** - Contextual help

**Each pattern has**:
- Required ARIA roles/properties
- Keyboard interaction spec
- Example implementations

---

## Testing ARIA Implementation

### Screen Reader Testing

**NVDA (Windows)**:
```
NVDA+Down Arrow - Read element
NVDA+T - Read title
Insert+F7 - List all landmarks
Insert+Ctrl+B - Read from beginning
```

**VoiceOver (Mac)**:
```
VO+A - Read from beginning
VO+Right Arrow - Next item
VO+U - Rotor (navigate by headings, landmarks)
VO+HH - Help
```

### Automated Testing

```bash
# axe-core (via browser extension or CLI)
npm install -g @axe-core/cli
axe https://example.com
```

**Check for**:
- ARIA roles used correctly
- ARIA states toggle properly
- aria-labelledby/describedby point to valid IDs
- Focusable elements have accessible names
- Live regions announce updates

---

## Common ARIA Mistakes

### ❌ ARIA on native elements

```html
<!-- ❌ WRONG - button already has role -->
<button role="button">Click</button>

<!-- ✅ CORRECT -->
<button>Click</button>
```

### ❌ ARIA without keyboard support

```html
<!-- ❌ WRONG - role doesn't add keyboard -->
<div role="button" onclick="doThing()">Click</div>

<!-- ✅ CORRECT - must handle keyboard -->
<div
  role="button"
  tabindex="0"
  onclick="doThing()"
  onkeydown="handleEnterSpace(event)"
>
  Click
</div>

<!-- ✅ BETTER - use native element -->
<button onclick="doThing()">Click</button>
```

### ❌ aria-hidden on focusable elements

```html
<!-- ❌ WRONG - hidden but focusable -->
<button aria-hidden="true">Click</button>

<!-- ✅ CORRECT - use hidden attribute -->
<button hidden>Click</button>
```

### ❌ Empty aria-label

```html
<!-- ❌ WRONG - removes accessible name -->
<button aria-label="">
  <svg><!-- Icon --></svg>
  Save
</button>

<!-- ✅ CORRECT - omit aria-label to use visible text -->
<button>
  <svg aria-hidden="true"><!-- Icon --></svg>
  Save
</button>
```

---

**Remember**: First Rule of ARIA - Don't use ARIA. Use semantic HTML first, ARIA only when HTML doesn't support the pattern.
