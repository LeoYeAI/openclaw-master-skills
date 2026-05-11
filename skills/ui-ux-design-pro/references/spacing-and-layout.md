# Spacing and Layout

## Spacing Scale

Base unit: 4px. Every spacing value is a multiple.

```css
--space-0: 0;
--space-px: 1px;
--space-0.5: 2px;
--space-1: 4px; /* micro: icon gaps */
--space-2: 8px; /* tight: inline elements, icon+text */
--space-3: 12px; /* compact: within small components */
--space-4: 16px; /* standard: card padding, form gaps */
--space-5: 20px; /* comfortable: section internal */
--space-6: 24px; /* section gaps */
--space-8: 32px; /* major section spacing */
--space-10: 40px; /* page section spacing */
--space-12: 48px; /* large section breaks */
--space-16: 64px; /* page-level spacing */
--space-20: 80px; /* hero-level spacing */
--space-24: 96px; /* maximum page spacing */
```

## Spacing by Context

| Context            | Values  | Example                               |
| ------------------ | ------- | ------------------------------------- |
| Micro              | 2-4px   | Icon-to-text gap, badge padding       |
| Component internal | 8-12px  | Button padding, input padding         |
| Component gap      | 12-16px | Form field gaps, card content spacing |
| Section internal   | 16-24px | Card padding, panel padding           |
| Section gap        | 24-32px | Between card groups                   |
| Page section       | 48-64px | Between major page areas              |

## Symmetrical Padding

```css
/* Correct */
padding: 16px;
padding: 12px 16px; /* horizontal needs more room */

/* Wrong */
padding: 24px 16px 12px 16px; /* asymmetric without reason */
```

## CSS Grid Patterns

### 12-Column Page Grid

```css
.page-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-6);
  max-width: 1280px;
  margin-inline: auto;
  padding-inline: var(--space-6);
}
```

### Sidebar + Content

```css
.app-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100dvh;
}

.app-layout-collapsed {
  grid-template-columns: 64px 1fr;
}
```

### Bento Grid: The CSS Subgrid Era

The dominant dashboard topology for 2026. Use CSS Subgrid to align internal card content across the global grid.

```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: minmax(180px, auto);
  gap: var(--space-4);
}

.tile-featured {
  grid-column: span 2;
  grid-row: span 2;
}

/* Internal layout aligns to parent tracks */
.tile-internal {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: span 3;
}
```

**Why:** Invisible order. Typography and spacing line up perfectly across independent cards.

### Dashboard Metrics Row

```css
.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); /* Wider for density */
  gap: var(--space-4);
}
```

### Spatial UI Layouts (Vision Pro Influence)

Layouts must adapt for gaze and touch.

- **Corner Radii**: Use `rounded-3xl` (24px+) to avoid aliasing in XR.
- **Gaze Targets**: Interactive elements must be 60px+ for eye tracking.
- **Depth**: Use "Z-Depth" layering instead of just X/Y positioning.

## Container Queries

Component-level responsive without media queries:

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (max-width: 300px) {
  .card-content {
    flex-direction: column;
    gap: var(--space-2);
  }
}

@container card (min-width: 500px) {
  .card-content {
    flex-direction: row;
    gap: var(--space-4);
  }
}
```

## Responsive Breakpoints

```css
/* Mobile-first breakpoints */
--bp-sm: 640px; /* large phones */
--bp-md: 768px; /* tablets */
--bp-lg: 1024px; /* small desktops */
--bp-xl: 1280px; /* desktops */
--bp-2xl: 1536px; /* wide screens */
```

| Aspect    | Mobile (375px) | Tablet (768px) | Desktop (1280px) |
| --------- | -------------- | -------------- | ---------------- |
| Columns   | 4              | 8              | 12               |
| Gutters   | 12px           | 16px           | 24px             |
| Margins   | 16px           | 24px           | 32-48px          |
| Base font | 14px           | 14px           | 14-16px          |

## Fluid Spacing

```css
--space-responsive: clamp(16px, 2vw + 8px, 32px);
--gap-responsive: clamp(12px, 1.5vw + 4px, 24px);
```

## Layout Composition Patterns

**Sidebar + Content:** Navigation serves content. 240-280px sidebar. Same bg + border separator.

**Split-screen:** Equal partners. 50/50 or 40/60. For comparison, dual-context.

**Full-bleed hero + constrained content:** Hero spans viewport, content sits in max-width container.

**Bento grid:** Varied card sizes encode hierarchy. Larger = more important.

**Sticky elements:** Navigation, headers, filters stick during scroll. Use `position: sticky`.

## CSS Logical Properties

Use logical properties for internationalization:

```css
/* Physical (avoid) */
margin-left: 16px;
padding-right: 8px;
border-bottom: 1px solid;

/* Logical (prefer) */
margin-inline-start: 16px;
padding-inline-end: 8px;
border-block-end: 1px solid;
```

## Works Cited

- [Bento Grid Design: How to Create Modern Modular Layouts in 2026](https://landdding.com/blog/blog-bento-grid-design-guide), accessed February 18, 2026
- [43 SaaS Bento Grid UI Design Examples | SaaSFrame](https://www.saasframe.io/patterns/bento-grid), accessed February 18, 2026
- [Product Pages in 2026 (Design Examples + Inspiration) | BigCommerce](https://www.bigcommerce.com/articles/ecommerce/product-page-examples/), accessed February 18, 2026
- [eCommerce Product Page Best Practices in 2026 [Examples] | VWO](https://vwo.com/blog/ecommerce-product-page-design/), accessed February 18, 2026
- [Best E-commerce Checkout Pages 2026 | My Codeless Website](https://mycodelesswebsite.com/e-commerce-checkout-examples/), accessed February 18, 2026
- [Interactive Real Estate Maps for Property Listings | Geoapify](https://www.geoapify.com/industries/maps-and-location-intelligence-for-real-estate-and-rental-search-websites/), accessed February 18, 2026
- [Real Estate Website Design Trends That Generate More Leads in 2026](https://rainstreamweb.com/blog/real-estate-website-design-trends-that-generate-more-leads-in-2026/), accessed February 18, 2026
- [Best Designed Real Estate Websites of January 2026 | Agent Image](https://www.agentimage.com/blog/best-designed-real-estate-websites-january-2026/), accessed February 18, 2026

