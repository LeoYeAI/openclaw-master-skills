# Mobile-First Patterns

Comprehensive responsive CSS patterns learned from real-world implementation failures.

## Hero Sections

### Problem
2-column grid layouts leave empty space when one column is hidden on mobile.

### Solution
Switch from `display: grid` to `display: flex` on mobile.

```css
/* Desktop: 2-column grid */
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
  padding: 80px 0;
}

/* Mobile: Centered flex */
@media (max-width: 768px) {
  .hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 40px 20px;
    gap: 24px;
  }

  .hero-content {
    align-items: center;
  }

  .hero-badge {
    align-self: center;
  }

  .hero-title {
    font-size: 32px;
    text-align: center;
  }

  .hero-subtitle {
    font-size: 14px;
    text-align: center;
  }

  .hero-cta {
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  .hero-cta .btn {
    width: 100%;
    max-width: 280px;
  }

  .hero-visual {
    display: none;
  }
}
```

**Key Rule**: Grid reserves space for hidden columns. Flex doesn't.

---

## Large Selection Lists

### Problem
Horizontal scroll for 20+ items is unusable on mobile — text gets cut off.

### Solution
Collapsible accordion with category headers.

```tsx
function MobileSelector({ categories }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="selector">
      {categories.map(cat => (
        <div 
          key={cat.name} 
          className={cn("category", expanded === cat.name && "expanded")}
        >
          <button
            className="category-header"
            onClick={() => setExpanded(
              expanded === cat.name ? null : cat.name
            )}
          >
            <span>{cat.name}</span>
            <ChevronDown className={cn(
              "transition-transform",
              expanded === cat.name && "rotate-180"
            )} />
          </button>
          
          <div className="category-items">
            {cat.items.map(item => (
              <button key={item.id} className="item">
                {item.name}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

```css
.category-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

@media (max-width: 768px) {
  .category-items {
    display: none;
  }

  .category.expanded .category-items {
    display: flex;
    flex-direction: column;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 8px;
  }
}
```

---

## Form Layouts

### Problem
Multi-column form layouts get cut off on mobile.

### Solution
Stack vertically with full width.

```css
.form-row {
  display: flex;
  gap: 16px;
}

.form-group {
  flex: 1;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
  }

  .form-group {
    width: 100%;
  }
  
  .form-row.half-width {
    /* Even "half width" fields go full on mobile */
    flex-direction: column;
  }
}
```

---

## Status/Alert Cards

### Problem
Inconsistent text alignment when stacking horizontal elements vertically.

### Solution
Both `align-items: center` AND `text-align: center`.

```css
.alert {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
}

.alert-icon {
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

@media (max-width: 768px) {
  .alert {
    flex-direction: column;
    align-items: center;  /* Center flex items */
    text-align: center;   /* Center text within items */
    gap: 8px;
  }

  .alert-content {
    text-align: center;  /* Explicit for nested elements */
  }

  .alert strong {
    text-align: center;  /* Block elements need explicit */
  }
}
```

**Key Rule**: Stacked flex items need BOTH `align-items: center` AND `text-align: center`.

---

## Grid Layouts

### Universal Mobile Collapse

```css
.pricing-grid,
.feature-grid,
.team-grid,
.stats-grid,
.testimonial-grid {
  display: grid;
  gap: 24px;
}

/* Desktop configurations */
.pricing-grid { grid-template-columns: repeat(3, 1fr); }
.feature-grid { grid-template-columns: repeat(3, 1fr); }
.team-grid { grid-template-columns: repeat(4, 1fr); }
.stats-grid { grid-template-columns: repeat(4, 1fr); }
.testimonial-grid { grid-template-columns: repeat(2, 1fr); }

/* Tablet */
@media (max-width: 1024px) {
  .team-grid { grid-template-columns: repeat(2, 1fr); }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Mobile: Everything single column */
@media (max-width: 768px) {
  .pricing-grid,
  .feature-grid,
  .team-grid,
  .stats-grid,
  .testimonial-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## Navigation

### Mobile Menu Pattern

```tsx
function MobileNav() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <button 
        className="md:hidden"
        onClick={() => setOpen(!open)}
      >
        {open ? <X /> : <Menu />}
      </button>

      {/* Mobile menu overlay */}
      <div className={cn(
        "fixed inset-0 bg-black/50 md:hidden transition-opacity",
        open ? "opacity-100" : "opacity-0 pointer-events-none"
      )} onClick={() => setOpen(false)} />

      {/* Mobile menu panel */}
      <nav className={cn(
        "fixed top-0 right-0 h-full w-64 bg-background p-6",
        "transform transition-transform md:hidden",
        open ? "translate-x-0" : "translate-x-full"
      )}>
        {/* Nav items */}
      </nav>
    </>
  );
}
```

---

## Form Element Consistency

### Always Style as a Group

```css
/* WRONG - Only targets input */
.input {
  border: 2px solid var(--border);
  border-radius: 8px;
}

/* CORRECT - All form fields */
.input,
.select,
.textarea {
  border: 2px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px; /* Prevents iOS zoom */
  background: var(--bg-secondary);
  color: var(--text-primary);
}
```

### Textarea Border Radius Exception

Pill-shaped inputs look wrong on textareas:

```css
.input,
.select {
  border-radius: 100px; /* Pill shape */
}

.textarea {
  border-radius: 16px; /* Softer, but not pill */
}
```

### Dropdown Option Styling

`<option>` elements can't inherit backdrop-filter:

```css
.select {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
}

/* Options need solid backgrounds */
.select option {
  background: #1a1a2e;
  color: white;
}
```

### Prevent iOS Zoom on Focus

iOS zooms on inputs with font-size < 16px:

```css
input, select, textarea {
  font-size: 16px; /* Minimum to prevent zoom */
}

/* Or use transform trick */
@media (max-width: 768px) {
  input, select, textarea {
    font-size: 16px;
  }
}
```

---

## Color Contrast Checklist

### Badge/Pill Elements

```css
/* WRONG - May be invisible */
.badge {
  background: var(--accent);
  color: white; /* Might not contrast */
}

/* CORRECT - Ensure contrast */
.badge {
  background: var(--accent);
  color: var(--accent-foreground); /* Defined to contrast */
}
```

### Color Swatches

Swatches showing colors need visible borders:

```css
.color-swatch {
  border: 2px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3);
}
```

### Dark Theme Form Labels

```css
/* WRONG - Hardcoded */
.label {
  color: white;
}

/* CORRECT - Semantic variable */
.label {
  color: var(--text-primary);
}
```

---

## Breakpoint Reference

```css
/* Large Desktop */
@media (min-width: 1440px) {
  .container { max-width: 1280px; }
}

/* Desktop */
@media (max-width: 1200px) {
  /* Stack sidebars, maintain content width */
}

/* Tablet */
@media (max-width: 1024px) {
  /* Reduce grid columns */
}

/* Mobile */
@media (max-width: 768px) {
  /* Full single-column, centered content */
}

/* Small Mobile */
@media (max-width: 480px) {
  /* Compact spacing, reduced font sizes */
}
```

---

## Mobile Font Scaling

```css
/* Base (desktop) */
.display { font-size: 64px; }
.h1 { font-size: 48px; }
.h2 { font-size: 36px; }
.h3 { font-size: 24px; }
.body { font-size: 16px; }
.small { font-size: 14px; }

/* Mobile */
@media (max-width: 768px) {
  .display { font-size: 40px; }
  .h1 { font-size: 32px; }
  .h2 { font-size: 24px; }
  .h3 { font-size: 20px; }
  .body { font-size: 16px; } /* Keep readable */
  .small { font-size: 13px; }
}
```

---

## Touch Target Sizes

Minimum 44x44px for touch targets (Apple HIG):

```css
.btn,
.nav-link,
.icon-btn {
  min-height: 44px;
  min-width: 44px;
}

@media (max-width: 768px) {
  .btn {
    padding: 14px 24px; /* Larger touch area */
  }
}
```

---

## Pre-Implementation Checklist

Before finalizing any mobile design:

- [ ] Hero centers on mobile (not left-aligned with empty space)
- [ ] All form fields (input, select, textarea) styled consistently
- [ ] Radio/checkboxes visible (especially transparent-border styles)
- [ ] Dropdown options have readable backgrounds
- [ ] Labels use semantic color variables
- [ ] Status/alert cards center properly
- [ ] Large selection lists use accordion (not horizontal scroll)
- [ ] Grid layouts collapse to single column
- [ ] Badge/pill text contrasts with background
- [ ] Color swatches have visible borders
- [ ] Touch targets are 44x44px minimum
- [ ] Font sizes are 16px+ to prevent iOS zoom
- [ ] Navigation has mobile menu pattern
