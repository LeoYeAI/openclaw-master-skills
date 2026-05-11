# Focus Management Patterns

Proper focus management ensures keyboard-only users can navigate and operate your interface efficiently.

---

## Core Principles

1. **All interactive elements must be focusable** - Button, links, form inputs
2. **Focus order must be logical** - Follows visual/reading order
3. **Focus must be visible** - Never `outline: none` without replacement
4. **Focus can't get trapped** - Must be able to escape every component
5. **Focus should be managed** - Restore focus after dialogs, handle SPA navigation

---

## Focus Visibility

### The Focus-Visible Pattern

```css
/* ❌ WRONG - removes all focus indicators */
*:focus {
  outline: none;
}

/* ✅ CORRECT - custom indicator on keyboard focus only */
*:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Optional: Remove indicator on mouse click */
*:focus:not(:focus-visible) {
  outline: none;
}
```

**`:focus-visible`** shows outline only when keyboard is used, not on mouse click.

### Contrast Requirements

Focus indicators must have **3:1 contrast** against background (WCAG 2.4.11).

```css
/* ✅ PASS - Blue #0066cc on white has 8:1 */
*:focus-visible {
  outline: 2px solid #0066cc;
}

/* ❌ FAIL - Light gray #ccc on white has 1.7:1 */
*:focus-visible {
  outline: 2px solid #cccccc;
}
```

---

## Tab Order

### Natural Tab Order

Follows DOM order - don't use `tabindex` > 0.

```html
<!-- ✅ Natural order: 1 → 2 → 3 -->
<input type="text" name="name">
<input type="email" name="email">
<button type="submit">Submit</button>
```

### Managing Focus with tabindex

```html
<!-- tabindex="0" - Adds to natural tab order -->
<div role="button" tabindex="0">Custom button</div>

<!-- tabindex="-1" - Programmatically focusable only -->
<main id="main-content" tabindex="-1">
  <!-- Can receive focus via JS but not Tab key -->
</main>

<!-- ❌ tabindex="1+" - DON'T USE - breaks natural order -->
<button tabindex="5">Don't do this</button>
```

**Rule**: Only use `tabindex="0"` or `tabindex="-1"`. Never use positive integers.

---

## Skip Links

Allow keyboard users to skip repeated content.

### Implementation

```html
<!-- Place at very top of <body> -->
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
  text-decoration: none;
  z-index: 9999;
}

.skip-link:focus {
  top: 0;
}
</style>

<!-- Target element -->
<main id="main-content" tabindex="-1">
  <!-- Page content -->
</main>
```

### Multiple Skip Links

```html
<div class="skip-links">
  <a href="#main-content">Skip to content</a>
  <a href="#nav">Skip to navigation</a>
  <a href="#search">Skip to search</a>
</div>
```

---

## Focus Traps

Trap focus within modal dialogs to prevent background interaction.

### Dialog Focus Trap Pattern

```typescript
function FocusTrap({ children, isActive }: { children: React.ReactNode; isActive: boolean }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isActive) return;

    const container = containerRef.current;
    if (!container) return;

    // Get all focusable elements
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) return;

    const first = focusableElements[0] as HTMLElement;
    const last = focusableElements[focusableElements.length - 1] as HTMLElement;

    // Focus first element
    first.focus();

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift+Tab on first element → focus last
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        // Tab on last element → focus first
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }, [isActive]);

  return <div ref={containerRef}>{children}</div>;
}

// Usage
function Dialog({ isOpen, onClose }) {
  return isOpen ? (
    <FocusTrap isActive={isOpen}>
      <div role="dialog" aria-modal="true">
        <h2>Dialog title</h2>
        <button onClick={onClose}>Close</button>
      </div>
    </FocusTrap>
  ) : null;
}
```

### Escape Key Handler

```typescript
useEffect(() => {
  if (!isOpen) return;

  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  document.addEventListener('keydown', handleEscape);
  return () => document.removeEventListener('keydown', handleEscape);
}, [isOpen, onClose]);
```

---

## Focus Restoration

Restore focus after closing dialogs, menus, or navigating.

### Dialog Focus Restoration

```typescript
function Dialog({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Save currently focused element
      previousFocus.current = document.activeElement as HTMLElement;
    } else if (previousFocus.current) {
      // Restore focus when closing
      previousFocus.current.focus();
      previousFocus.current = null;
    }
  }, [isOpen]);

  return isOpen ? (
    <div role="dialog">
      {/* Dialog content */}
    </div>
  ) : null;
}
```

### SPA Focus Management

Reset focus on route change:

```typescript
// React Router example
function App() {
  const location = useLocation();
  const mainRef = useRef<HTMLElement>(null);

  useEffect(() => {
    // Focus main content on route change
    mainRef.current?.focus();
  }, [location.pathname]);

  return (
    <main ref={mainRef} id="main-content" tabindex={-1}>
      <Outlet />
    </main>
  );
}
```

---

## Keyboard Navigation Patterns

### Arrow Key Navigation

For menus, tabs, radio groups:

```typescript
function Tabs({ tabs }: { tabs: string[] }) {
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
    <div role="tablist">
      {tabs.map((tab, index) => (
        <button
          key={index}
          role="tab"
          tabIndex={activeIndex === index ? 0 : -1}
          aria-selected={activeIndex === index}
          onClick={() => setActiveIndex(index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
        >
          {tab}
        </button>
      ))}
    </div>
  );
}
```

**Pattern**:
- Active element has `tabindex="0"`
- Inactive elements have `tabindex="-1"`
- Arrow keys change active element and move focus
- Home/End jump to first/last

### Dropdown Menu

```typescript
function DropdownMenu({ trigger, items }: { trigger: string; items: Array<{ label: string; onClick: () => void }> }) {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(0);

  const handleTriggerKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setIsOpen(true);
      setFocusedIndex(0);
    }
  };

  const handleMenuKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setFocusedIndex((prev) => (prev + 1) % items.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setFocusedIndex((prev) => (prev - 1 + items.length) % items.length);
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      items[focusedIndex]?.onClick();
      setIsOpen(false);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setIsOpen(false);
    }
  };

  return (
    <div>
      <button
        aria-haspopup="true"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleTriggerKeyDown}
      >
        {trigger}
      </button>

      {isOpen && (
        <ul role="menu" onKeyDown={handleMenuKeyDown}>
          {items.map((item, index) => (
            <li key={index} role="none">
              <button
                role="menuitem"
                tabIndex={focusedIndex === index ? 0 : -1}
                onClick={() => {
                  item.onClick();
                  setIsOpen(false);
                }}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

## Focus Indicators for Components

### Cards/Links

```css
.card:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 4px;
}
```

### Form Inputs

```css
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.25);
}
```

### Buttons

```css
button:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

---

## Testing Focus Management

### Manual Testing

1. **Unplug mouse** or hide cursor
2. **Tab through page**:
   - Can you reach all interactive elements?
   - Is focus visible at all times?
   - Is tab order logical?
3. **Test dialogs**:
   - Does focus move into dialog?
   - Can you Tab within dialog?
   - Can you Escape to close?
   - Does focus restore after closing?
4. **Test menus**:
   - Can you open with keyboard?
   - Can you navigate with arrows?
   - Can you activate with Enter?
   - Can you close with Escape?

### Automated Testing

```javascript
// Check for focus trap issues
const dialog = document.querySelector('[role="dialog"]');
const focusable = dialog.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
console.log(`Focusable elements in dialog: ${focusable.length}`);

// Check for visible focus
const activeElement = document.activeElement;
const styles = window.getComputedStyle(activeElement);
console.log('Outline:', styles.outline);
console.log('Box-shadow:', styles.boxShadow);
```

---

## Common Issues

### Problem: Focus disappears in SPA

**Cause**: Navigation doesn't reset focus
**Solution**: Focus main content on route change

### Problem: Can't Tab out of component

**Cause**: Focus trap without Escape key handler
**Solution**: Add Escape listener to close/exit

### Problem: Tab order illogical

**Cause**: DOM order doesn't match visual order (CSS positioning)
**Solution**: Reorder DOM to match visual layout

### Problem: Focus indicator missing

**Cause**: CSS removed outline without replacement
**Solution**: Add `:focus-visible` styles

---

**Key Takeaway**: Focus management is essential for keyboard accessibility. Test every interactive component with keyboard only.
