---
name: accessibility
description: |
  Build WCAG 2.1 AA compliant websites with semantic HTML, proper ARIA, focus management, and screen reader support. Includes color contrast (4.5:1 text), keyboard navigation, form labels, and live regions.

  Use when implementing accessible interfaces, fixing screen reader issues, keyboard navigation, or troubleshooting "focus outline missing", "aria-label required", "insufficient contrast".
---

# Web Accessibility (WCAG 2.1 AA)

**Status**: Production Ready ✅
**Last Updated**: 2026-01-14
**Dependencies**: None (framework-agnostic)
**Standards**: WCAG 2.1 Level AA

---

## Quick Start (5 Minutes)

### 1. Semantic HTML Foundation

Choose the right element - don't use `div` for everything:

```html
<!-- ❌ WRONG - divs with onClick -->
<div onclick="submit()">Submit</div>
<div onclick="navigate()">Next page</div>

<!-- ✅ CORRECT - semantic elements -->
<button type="submit">Submit</button>
<a href="/next">Next page</a>
```

**Why this matters:**
- Semantic elements have built-in keyboard support
- Screen readers announce role automatically
- Browser provides default accessible behaviors

### 2. Focus Management

Make interactive elements keyboard-accessible:

```css
/* ❌ WRONG - removes focus outline */
button:focus { outline: none; }

/* ✅ CORRECT - custom accessible outline */
button:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

**CRITICAL:**
- Never remove focus outlines without replacement
- Use `:focus-visible` to show only on keyboard focus
- Ensure 3:1 contrast ratio for focus indicators

### 3. Text Alternatives

Every non-text element needs a text alternative:

```html
<!-- ❌ WRONG - no alt text -->
<img src="logo.png">
<button><svg>...</svg></button>

<!-- ✅ CORRECT - proper alternatives -->
<img src="logo.png" alt="Company Name">
<button aria-label="Close dialog"><svg>...</svg></button>
```

---

## The 5-Step Accessibility Process

### Step 1: Choose Semantic HTML

**Decision tree for element selection:**

```
Need clickable element?
├─ Navigates to another page? → <a href="...">
├─ Submits form? → <button type="submit">
├─ Opens dialog? → <button aria-haspopup="dialog">
└─ Other action? → <button type="button">

Grouping content?
├─ Self-contained article? → <article>
├─ Thematic section? → <section>
├─ Navigation links? → <nav>
└─ Supplementary info? → <aside>

Form element?
├─ Text input? → <input type="text">
├─ Multiple choice? → <select> or <input type="radio">
├─ Toggle? → <input type="checkbox"> or <button aria-pressed>
└─ Long text? → <textarea>
```

**See `references/semantic-html.md` for complete guide.**

### Step 2: Add ARIA When Needed

**Golden rule: Use ARIA only when HTML can't express the pattern.**

```html
<!-- ❌ WRONG - unnecessary ARIA -->
<button role="button">Click me</button>  <!-- Button already has role -->

<!-- ✅ CORRECT - ARIA fills semantic gap -->
<div role="dialog" aria-labelledby="title" aria-modal="true">
  <h2 id="title">Confirm action</h2>
  <!-- No HTML dialog yet, so role needed -->
</div>

<!-- ✅ BETTER - Use native HTML when available -->
<dialog aria-labelledby="title">
  <h2 id="title">Confirm action</h2>
</dialog>
```

**Common ARIA patterns:**
- `aria-label` - When visible label doesn't exist
- `aria-labelledby` - Reference existing text as label
- `aria-describedby` - Additional description
- `aria-live` - Announce dynamic updates
- `aria-expanded` - Collapsible/expandable state

**See `references/aria-patterns.md` for complete patterns.**

### Step 3: Implement Keyboard Navigation

**All interactive elements must be keyboard-accessible:**

```typescript
// Tab order management
function Dialog({ onClose }) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    // Save previous focus
    previousFocus.current = document.activeElement as HTMLElement;

    // Focus first element in dialog
    const firstFocusable = dialogRef.current?.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    (firstFocusable as HTMLElement)?.focus();

    // Trap focus within dialog
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab') {
        // Focus trap logic here
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      // Restore focus on close
      previousFocus.current?.focus();
    };
  }, [onClose]);

  return <div ref={dialogRef} role="dialog">...</div>;
}
```

**Essential keyboard patterns:**
- Tab/Shift+Tab: Navigate between focusable elements
- Enter/Space: Activate buttons/links
- Arrow keys: Navigate within components (tabs, menus)
- Escape: Close dialogs/menus
- Home/End: Jump to first/last item

**See `references/focus-management.md` for complete patterns.**

### Step 4: Ensure Color Contrast

**WCAG AA requirements:**
- Normal text (under 18pt): 4.5:1 contrast ratio
- Large text (18pt+ or 14pt+ bold): 3:1 contrast ratio
- UI components (buttons, borders): 3:1 contrast ratio

```css
/* ❌ WRONG - insufficient contrast */
:root {
  --background: #ffffff;
  --text: #999999;  /* 2.8:1 - fails WCAG AA */
}

/* ✅ CORRECT - sufficient contrast */
:root {
  --background: #ffffff;
  --text: #595959;  /* 4.6:1 - passes WCAG AA */
}
```

**Testing tools:**
- Browser DevTools (Chrome/Firefox have built-in checkers)
- Contrast checker extensions
- axe DevTools extension

**See `references/color-contrast.md` for complete guide.**

### Step 5: Make Forms Accessible

**Every form input needs a visible label:**

```html
<!-- ❌ WRONG - placeholder is not a label -->
<input type="email" placeholder="Email address">

<!-- ✅ CORRECT - proper label -->
<label for="email">Email address</label>
<input type="email" id="email" name="email" required aria-required="true">
```

**Error handling:**

```html
<label for="email">Email address</label>
<input
  type="email"
  id="email"
  name="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<span id="email-error" role="alert">
  Please enter a valid email address
</span>
```

**Live regions for dynamic errors:**

```html
<div role="alert" aria-live="assertive" aria-atomic="true">
  Form submission failed. Please fix the errors above.
</div>
```

**See `references/forms-validation.md` for complete patterns.**

---

## Critical Rules

### Always Do

✅ Use semantic HTML elements first (button, a, nav, article, etc.)
✅ Provide text alternatives for all non-text content
✅ Ensure 4.5:1 contrast for normal text, 3:1 for large text/UI
✅ Make all functionality keyboard accessible
✅ Test with keyboard only (unplug mouse)
✅ Test with screen reader (NVDA on Windows, VoiceOver on Mac)
✅ Use proper heading hierarchy (h1 → h2 → h3, no skipping)
✅ Label all form inputs with visible labels
✅ Provide focus indicators (never just `outline: none`)
✅ Use `aria-live` for dynamic content updates

### Never Do

❌ Use `div` with `onClick` instead of `button`
❌ Remove focus outlines without replacement
❌ Use color alone to convey information
❌ Use placeholders as labels
❌ Skip heading levels (h1 → h3)
❌ Use `tabindex` > 0 (messes with natural order)
❌ Add ARIA when semantic HTML exists
❌ Forget to restore focus after closing dialogs
❌ Use `role="presentation"` on focusable elements
❌ Create keyboard traps (no way to escape)

---

## Known Issues Prevention

This skill prevents **12** documented accessibility issues:

### Issue #1: Missing Focus Indicators

**Error**: Interactive elements have no visible focus indicator
**Source**: WCAG 2.4.7 (Focus Visible)
**Why It Happens**: CSS reset removes default outline
**Prevention**: Always provide custom focus-visible styles

### Issue #2: Insufficient Color Contrast

**Error**: Text has less than 4.5:1 contrast ratio
**Source**: WCAG 1.4.3 (Contrast Minimum)
**Why It Happens**: Using light gray text on white background
**Prevention**: Test all text colors with contrast checker

### Issue #3: Missing Alt Text

**Error**: Images missing alt attributes
**Source**: WCAG 1.1.1 (Non-text Content)
**Why It Happens**: Forgot to add or thought it was optional
**Prevention**: Add alt="" for decorative, descriptive alt for meaningful images

### Issue #4: Keyboard Navigation Broken

**Error**: Interactive elements not reachable by keyboard
**Source**: WCAG 2.1.1 (Keyboard)
**Why It Happens**: Using div onClick instead of button
**Prevention**: Use semantic interactive elements (button, a)

### Issue #5: Form Inputs Without Labels

**Error**: Input fields missing associated labels
**Source**: WCAG 3.3.2 (Labels or Instructions)
**Why It Happens**: Using placeholder as label
**Prevention**: Always use `<label>` element with for/id association

### Issue #6: Skipped Heading Levels

**Error**: Heading hierarchy jumps from h1 to h3
**Source**: WCAG 1.3.1 (Info and Relationships)
**Why It Happens**: Using headings for visual styling instead of semantics
**Prevention**: Use headings in order, style with CSS

### Issue #7: No Focus Trap in Dialogs

**Error**: Tab key exits dialog to background content
**Source**: WCAG 2.4.3 (Focus Order)
**Why It Happens**: No focus trap implementation
**Prevention**: Implement focus trap for modal dialogs

### Issue #8: Missing aria-live for Dynamic Content

**Error**: Screen reader doesn't announce updates
**Source**: WCAG 4.1.3 (Status Messages)
**Why It Happens**: Dynamic content added without announcement
**Prevention**: Use aria-live="polite" or "assertive"

### Issue #9: Color-Only Information

**Error**: Using only color to convey status
**Source**: WCAG 1.4.1 (Use of Color)
**Why It Happens**: Red text for errors without icon/text
**Prevention**: Add icon + text label, not just color

### Issue #10: Non-descriptive Link Text

**Error**: Links with "click here" or "read more"
**Source**: WCAG 2.4.4 (Link Purpose)
**Why It Happens**: Generic link text without context
**Prevention**: Use descriptive link text or aria-label

### Issue #11: Auto-playing Media

**Error**: Video/audio auto-plays without user control
**Source**: WCAG 1.4.2 (Audio Control)
**Why It Happens**: Autoplay attribute without controls
**Prevention**: Require user interaction to start media

### Issue #12: Inaccessible Custom Controls

**Error**: Custom select/checkbox without keyboard support
**Source**: WCAG 4.1.2 (Name, Role, Value)
**Why It Happens**: Building from divs without ARIA
**Prevention**: Use native elements or implement full ARIA pattern

---

## WCAG 2.1 AA Quick Checklist

### Perceivable

- [ ] All images have alt text (or alt="" if decorative)
- [ ] Text contrast ≥ 4.5:1 (normal), ≥ 3:1 (large)
- [ ] Color not used alone to convey information
- [ ] Text can be resized to 200% without loss of content
- [ ] No auto-playing audio >3 seconds

### Operable

- [ ] All functionality keyboard accessible
- [ ] No keyboard traps
- [ ] Visible focus indicators
- [ ] Users can pause/stop/hide moving content
- [ ] Page titles describe purpose
- [ ] Focus order is logical
- [ ] Link purpose clear from text or context
- [ ] Multiple ways to find pages (menu, search, sitemap)
- [ ] Headings and labels describe purpose

### Understandable

- [ ] Page language specified (`<html lang="en">`)
- [ ] Language changes marked (`<span lang="es">`)
- [ ] No unexpected context changes on focus/input
- [ ] Consistent navigation across site
- [ ] Form labels/instructions provided
- [ ] Input errors identified and described
- [ ] Error prevention for legal/financial/data changes

### Robust

- [ ] Valid HTML (no parsing errors)
- [ ] Name, role, value available for all UI components
- [ ] Status messages identified (aria-live)

---

## Testing Workflow

### 1. Keyboard-Only Testing (5 minutes)

```
1. Unplug mouse or hide cursor
2. Tab through entire page
   - Can you reach all interactive elements?
   - Can you activate all buttons/links?
   - Is focus order logical?
3. Use Enter/Space to activate
4. Use Escape to close dialogs
5. Use arrow keys in menus/tabs
```

### 2. Screen Reader Testing (10 minutes)

**NVDA (Windows - Free)**:
- Download: https://www.nvaccess.org/download/
- Start: Ctrl+Alt+N
- Navigate: Arrow keys or Tab
- Read: NVDA+Down arrow
- Stop: NVDA+Q

**VoiceOver (Mac - Built-in)**:
- Start: Cmd+F5
- Navigate: VO+Right/Left arrow (VO = Ctrl+Option)
- Read: VO+A (read all)
- Stop: Cmd+F5

**What to test:**
- Are all interactive elements announced?
- Are images described properly?
- Are form labels read with inputs?
- Are dynamic updates announced?
- Is heading structure clear?

### 3. Automated Testing

**axe DevTools** (Browser extension - highly recommended):
- Install: Chrome/Firefox extension
- Run: F12 → axe DevTools tab → Scan
- Fix: Review violations, follow remediation
- Retest: Scan again after fixes

**Lighthouse** (Built into Chrome):
- Open DevTools (F12)
- Lighthouse tab
- Select "Accessibility" category
- Generate report
- Score 90+ is good, 100 is ideal

---

## Common Patterns

### Pattern 1: Accessible Dialog/Modal

```typescript
interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

function Dialog({ isOpen, onClose, title, children }: DialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const previousFocus = document.activeElement as HTMLElement;

    // Focus first focusable element
    const firstFocusable = dialogRef.current?.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as HTMLElement;
    firstFocusable?.focus();

    // Focus trap
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
      if (e.key === 'Tab') {
        const focusableElements = dialogRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (!focusableElements?.length) return;

        const first = focusableElements[0] as HTMLElement;
        const last = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      previousFocus?.focus();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="dialog-backdrop"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        className="dialog"
      >
        <h2 id="dialog-title">{title}</h2>
        <div className="dialog-content">{children}</div>
        <button onClick={onClose} aria-label="Close dialog">×</button>
      </div>
    </>
  );
}
```

**When to use**: Any modal dialog or overlay that blocks interaction with background content.

### Pattern 2: Accessible Tabs

```typescript
function Tabs({ tabs }: { tabs: Array<{ label: string; content: React.ReactNode }> }) {
  const [activeIndex, setActiveIndex] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const newIndex = index === 0 ? tabs.length - 1 : index - 1;
      setActiveIndex(newIndex);
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      const newIndex = index === tabs.length - 1 ? 0 : index + 1;
      setActiveIndex(newIndex);
    } else if (e.key === 'Home') {
      e.preventDefault();
      setActiveIndex(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      setActiveIndex(tabs.length - 1);
    }
  };

  return (
    <div>
      <div role="tablist" aria-label="Content tabs">
        {tabs.map((tab, index) => (
          <button
            key={index}
            role="tab"
            aria-selected={activeIndex === index}
            aria-controls={`panel-${index}`}
            id={`tab-${index}`}
            tabIndex={activeIndex === index ? 0 : -1}
            onClick={() => setActiveIndex(index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map((tab, index) => (
        <div
          key={index}
          role="tabpanel"
          id={`panel-${index}`}
          aria-labelledby={`tab-${index}`}
          hidden={activeIndex !== index}
          tabIndex={0}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

**When to use**: Tabbed interface with multiple panels.

### Pattern 3: Skip Links

```html
<!-- Place at very top of body -->
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--primary);
  color: white;
  padding: 8px 16px;
  z-index: 9999;
}

.skip-link:focus {
  top: 0;
}
</style>

<!-- Then in your layout -->
<main id="main-content" tabindex="-1">
  <!-- Page content -->
</main>
```

**When to use**: All multi-page websites with navigation/header before main content.

### Pattern 4: Accessible Form with Validation

```typescript
function ContactForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateEmail = (email: string) => {
    if (!email) return 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Email is invalid';
    return '';
  };

  const handleBlur = (field: string, value: string) => {
    setTouched(prev => ({ ...prev, [field]: true }));
    const error = validateEmail(value);
    setErrors(prev => ({ ...prev, [field]: error }));
  };

  return (
    <form>
      <div>
        <label htmlFor="email">Email address *</label>
        <input
          type="email"
          id="email"
          name="email"
          required
          aria-required="true"
          aria-invalid={touched.email && !!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
          onBlur={(e) => handleBlur('email', e.target.value)}
        />
        {touched.email && errors.email && (
          <span id="email-error" role="alert" className="error">
            {errors.email}
          </span>
        )}
      </div>

      <button type="submit">Submit</button>

      {/* Global form error */}
      <div role="alert" aria-live="assertive" aria-atomic="true">
        {/* Dynamic error message appears here */}
      </div>
    </form>
  );
}
```

**When to use**: All forms with validation.

---

## Using Bundled Resources

### References (references/)

Detailed documentation for deep dives:

- **wcag-checklist.md** - Complete WCAG 2.1 Level A & AA requirements with examples
- **semantic-html.md** - Element selection guide, when to use which tag
- **aria-patterns.md** - ARIA roles, states, properties, and when to use them
- **focus-management.md** - Focus order, focus traps, focus restoration patterns
- **color-contrast.md** - Contrast requirements, testing tools, color palette tips
- **forms-validation.md** - Accessible form patterns, error handling, announcements

**When Claude should load these**:
- User asks for complete WCAG checklist
- Deep dive into specific pattern (tabs, accordions, etc.)
- Color contrast issues or palette design
- Complex form validation scenarios

### Agents (agents/)

- **a11y-auditor.md** - Automated accessibility auditor that checks pages for violations

**When to use**: Request accessibility audit of existing page/component.

---

## Advanced Topics

### ARIA Live Regions

Three politeness levels:

```html
<!-- Polite: Wait for screen reader to finish current announcement -->
<div aria-live="polite">New messages: 3</div>

<!-- Assertive: Interrupt immediately -->
<div aria-live="assertive" role="alert">
  Error: Form submission failed
</div>

<!-- Off: Don't announce (default) -->
<div aria-live="off">Loading...</div>
```

**Best practices:**
- Use `polite` for non-critical updates (notifications, counters)
- Use `assertive` for errors and critical alerts
- Use `aria-atomic="true"` to read entire region on change
- Keep messages concise and meaningful

### Focus Management in SPAs

React Router doesn't reset focus on navigation - you need to handle it:

```typescript
function App() {
  const location = useLocation();
  const mainRef = useRef<HTMLElement>(null);

  useEffect(() => {
    // Focus main content on route change
    mainRef.current?.focus();
    // Announce page title to screen readers
    const title = document.title;
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.textContent = `Navigated to ${title}`;
    document.body.appendChild(announcement);
    setTimeout(() => announcement.remove(), 1000);
  }, [location.pathname]);

  return <main ref={mainRef} tabIndex={-1} id="main-content">...</main>;
}
```

### Accessible Data Tables

```html
<table>
  <caption>Monthly sales by region</caption>
  <thead>
    <tr>
      <th scope="col">Region</th>
      <th scope="col">Q1</th>
      <th scope="col">Q2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">North</th>
      <td>$10,000</td>
      <td>$12,000</td>
    </tr>
  </tbody>
</table>
```

**Key attributes:**
- `<caption>` - Describes table purpose
- `scope="col"` - Identifies column headers
- `scope="row"` - Identifies row headers
- Associates data cells with headers for screen readers

---

## Official Documentation

- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/
- **MDN Accessibility**: https://developer.mozilla.org/en-US/docs/Web/Accessibility
- **ARIA Authoring Practices**: https://www.w3.org/WAI/ARIA/apg/
- **WebAIM**: https://webaim.org/articles/
- **axe DevTools**: https://www.deque.com/axe/devtools/

---

## Troubleshooting

### Problem: Focus indicators not visible

**Symptoms**: Can tab through page but don't see where focus is
**Cause**: CSS removed outlines or insufficient contrast
**Solution**:
```css
*:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

### Problem: Screen reader not announcing updates

**Symptoms**: Dynamic content changes but no announcement
**Cause**: No aria-live region
**Solution**: Wrap dynamic content in `<div aria-live="polite">` or use role="alert"

### Problem: Dialog focus escapes to background

**Symptoms**: Tab key navigates to elements behind dialog
**Cause**: No focus trap
**Solution**: Implement focus trap (see Pattern 1 above)

### Problem: Form errors not announced

**Symptoms**: Visual errors appear but screen reader doesn't notice
**Cause**: No aria-invalid or role="alert"
**Solution**: Use aria-invalid + aria-describedby pointing to error message with role="alert"

---

## Complete Setup Checklist

Use this for every page/component:

- [ ] All interactive elements are keyboard accessible
- [ ] Visible focus indicators on all focusable elements
- [ ] Images have alt text (or alt="" if decorative)
- [ ] Text contrast ≥ 4.5:1 (test with axe or Lighthouse)
- [ ] Form inputs have associated labels (not just placeholders)
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] Page has `<html lang="en">` or appropriate language
- [ ] Dialogs have focus trap and restore focus on close
- [ ] Dynamic content uses aria-live or role="alert"
- [ ] Color not used alone to convey information
- [ ] Tested with keyboard only (no mouse)
- [ ] Tested with screen reader (NVDA or VoiceOver)
- [ ] Ran axe DevTools scan (0 violations)
- [ ] Lighthouse accessibility score ≥ 90

---

**Questions? Issues?**

1. Check `references/wcag-checklist.md` for complete requirements
2. Use `/a11y-auditor` agent to scan your page
3. Run axe DevTools for automated testing
4. Test with actual keyboard + screen reader

---

**Standards**: WCAG 2.1 Level AA
**Testing Tools**: axe DevTools, Lighthouse, NVDA, VoiceOver
**Success Criteria**: 90+ Lighthouse score, 0 critical violations
