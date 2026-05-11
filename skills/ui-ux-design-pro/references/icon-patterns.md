# Icon Implementation Guidelines

Best practices for using icons in modern web applications (2025 Standards).

## 1. Quick Start Guidelines

| Requirement | Recommended Solution | Why? |
|-------------|----------------------|------|
| **React / Next.js** | **Lucide React** or **Radix Icons** | Tree-shakeable, consistent stroke usage, highly customizable props. |
| **Large Scale / Multi-Framework** | **Iconify** | On-demand loading (no bundle bloat), access to 200k+ icons. |
| **Simple HTML/CSS** | **Phosphor** or **Heroicons (SVG)** | Easy CDN drop-in, no build step required. |
| **Premium / High-Fidelity** | **Hugeicons** or **Untitled UI** | Thousands of variants, "pro" balanced look. |

## 2. Implementation Patterns

### A. React Component (Best Practice)
Use individual imports to ensure tree-shaking. Don't import the entire library.

```tsx
// ✅ GOOD: Tree-shakable
import { Home, Settings, User } from 'lucide-react';

const Nav = () => (
  <nav className="flex gap-4">
    <Home className="w-5 h-5 text-slate-500 hover:text-slate-900" />
    <Settings className="w-5 h-5 text-slate-500 hover:text-slate-900" />
    <User className="w-5 h-5 text-slate-500 hover:text-slate-900" />
  </nav>
);

// ❌ BAD: Large bundle size potential (depending on library)
import * as Icons from 'lucide-react'; 
```

### B. Iconify (On-Demand)
Perfect for CMS-driven content or user-selected icons where you can't import everything.

**Setup (React):**
```bash
npm install @iconify/react
```

**Usage:**
```tsx
import { Icon } from '@iconify/react';

export const DynamicIcon = ({ name }: { name: string }) => (
  // Loads "mdi:home" or "lucide:arrow-right" on demand
  <Icon icon={name} width="24" height="24" className="text-primary" />
);
```

### C. Plain HTML/JS (CDN)
For static sites or quick prototypes.

**Iconify Script:**
```html
<script src="https://code.iconify.design/3/3.1.0/iconify.min.js"></script>
<!-- Usage -->
<span class="iconify" data-icon="heroicons:beaker" data-width="24"></span>
```

**Font Awesome (Classic):**
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<!-- Usage -->
<i class="fa-solid fa-house text-2xl"></i>
```

## 3. UI/UX Best Practices

### A. Touch Targets
Always wrap icons in a container or ensure they have enough clickable area on mobile.

```css
/* ✅ GOOD: 24px visual, but 44px touch target */
.icon-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-btn svg {
  width: 20px;
  height: 20px;
}
```

### B. Scalability (SVG vs Font)
**Prefer SVG** over Icon Fonts (e.g., Font Awesome CSS).
- **Sharper:** SVGs render perfectly at any zoom level; fonts can anti-alias poorly.
- **Control:** SVGs allow multi-color (duotone) via CSS classes; fonts are single-color.
- **Positioning:** Fonts fight with `line-height`; SVGs are distinct blocks.

### C. Accessibility
Decorative icons should be hidden. Interactive icons need labels.

```tsx
// Decorative (e.g., in a list)
<CheckIcon aria-hidden="true" className="..." />

// Interactive (Standalone Button)
<button aria-label="Close Menu">
  <XIcon aria-hidden="true" />
</button>
```

### D. Consistency
- **Stroke Width:** Stick to one stroke width (usually 1.5px or 2px) across all icons.
- **Style:** Don't mix "Filled" and "Outline" styles unless "Filled" indicates an active state.
- **Size:** Use a scale (16px, 20px, 24px, 32px). Avoid arbitrary sizes like 19px.
