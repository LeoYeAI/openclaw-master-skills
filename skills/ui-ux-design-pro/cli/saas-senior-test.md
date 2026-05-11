# Design System: SaaS Launch

> **Query**: "SaaS Landing Page" | **Generated**: 2/18/2026

## 01. Foundation
- **Primary Color**: `#7C3AED` ![#7C3AED](https://via.placeholder.com/15/7C3AED/000000?text=+)
- **Typography**: **Bitter** (Headings & Body)

### Color Palette
#### Primary Brand
| Stop | Hex | Preview |
| :--- | :--- | :--- |
| **50** | `#EFE7FD` | ![#EFE7FD](https://via.placeholder.com/80x30/EFE7FD/EFE7FD?text=+) |
| **100** | `#E0CFFC` | ![#E0CFFC](https://via.placeholder.com/80x30/E0CFFC/E0CFFC?text=+) |
| **200** | `#C1A2F6` | ![#C1A2F6](https://via.placeholder.com/80x30/C1A2F6/C1A2F6?text=+) |
| **300** | `#A273F2` | ![#A273F2](https://via.placeholder.com/80x30/A273F2/A273F2?text=+) |
| **400** | `#8244EE` | ![#8244EE](https://via.placeholder.com/80x30/8244EE/8244EE?text=+) |
| **500** | `#6316E9` | ![#6316E9](https://via.placeholder.com/80x30/6316E9/6316E9?text=+) |
| **600** | `#4F11BB` | ![#4F11BB](https://via.placeholder.com/80x30/4F11BB/4F11BB?text=+) |
| **700** | `#3C0D8C` | ![#3C0D8C](https://via.placeholder.com/80x30/3C0D8C/3C0D8C?text=+) |
| **800** | `#28095D` | ![#28095D](https://via.placeholder.com/80x30/28095D/28095D?text=+) |
| **900** | `#140330` | ![#140330](https://via.placeholder.com/80x30/140330/140330?text=+) |
| **950** | `#0A0218` | ![#0A0218](https://via.placeholder.com/80x30/0A0218/0A0218?text=+) |

#### Neutral
| Stop | Hex | Preview |
| :--- | :--- | :--- |
| **50** | `#F0E9FC` | ![#F0E9FC](https://via.placeholder.com/80x30/F0E9FC/F0E9FC?text=+) |
| **100** | `#E1D3F8` | ![#E1D3F8](https://via.placeholder.com/80x30/E1D3F8/E1D3F8?text=+) |
| **200** | `#C3A9EF` | ![#C3A9EF](https://via.placeholder.com/80x30/C3A9EF/C3A9EF?text=+) |
| **300** | `#A57EE7` | ![#A57EE7](https://via.placeholder.com/80x30/A57EE7/A57EE7?text=+) |
| **400** | `#8754DE` | ![#8754DE](https://via.placeholder.com/80x30/8754DE/8754DE?text=+) |
| **500** | `#6829D6` | ![#6829D6](https://via.placeholder.com/80x30/6829D6/6829D6?text=+) |
| **600** | `#5421AB` | ![#5421AB](https://via.placeholder.com/80x30/5421AB/5421AB?text=+) |
| **700** | `#3F1881` | ![#3F1881](https://via.placeholder.com/80x30/3F1881/3F1881?text=+) |
| **800** | `#2A1056` | ![#2A1056](https://via.placeholder.com/80x30/2A1056/2A1056?text=+) |
| **900** | `#15072C` | ![#15072C](https://via.placeholder.com/80x30/15072C/15072C?text=+) |
| **950** | `#0A0316` | ![#0A0316](https://via.placeholder.com/80x30/0A0316/0A0316?text=+) |

### Tokens
- **Spacing Base**: 4px
- **Radius**: 4px
- **Shadows**: Soft, layered shadows for depth.

## 02. Atoms
## Atoms

### Button Ghost
> Low-emphasis button

| Feature | Details |
| :--- | :--- |
| **Usage** | Icon-only actions, tertiary links |
| **Variants** | Hover/Active/Disabled |
| **CSS Variable** | `--ghost-btn-bg` |

**Code Example (Tailwind)**
```tsx
<button className="text-slate-500 hover:bg-slate-100 p-2 rounded-full transition-colors"><Icon /></button>
```

> [!TIP]
> **Best Practice**: Great for toolbars and inline actions.

> [!NOTE]
> **Accessibility**: Provide aria-label for icon-only buttons.



### Radio
> Single selection from list

| Feature | Details |
| :--- | :--- |
| **Usage** |  mutually exclusive options |
| **Variants** | Selected/Unselected |
| **CSS Variable** | `--radio-color` |

**Code Example (Tailwind)**
```tsx
<input type="radio" className="w-5 h-5 text-primary border-gray-300 focus:ring-primary" />
```

> [!TIP]
> **Best Practice**: Default select the most common option.

> [!NOTE]
> **Accessibility**: Group with role="radiogroup".



### Checkbox
> Binary selection control

| Feature | Details |
| :--- | :--- |
| **Usage** | Settings, multi-select lists |
| **Variants** | Checked/Unchecked/Indeterminate |
| **CSS Variable** | `--checkbox-color` |

**Code Example (Tailwind)**
```tsx
<input type="checkbox" className="w-5 h-5 text-primary rounded border-slate-300 focus:ring-primary" />
```

> [!TIP]
> **Best Practice**: Label should be clickable to toggle.

> [!NOTE]
> **Accessibility**: Use a fieldset for grouped checkboxes.



### Avatar
> User profile image

| Feature | Details |
| :--- | :--- |
| **Usage** | Comments, profile headers |
| **Variants** | Image/Initials/Icon |
| **CSS Variable** | `--avatar-size` |

**Code Example (Tailwind)**
```tsx
<img className="inline-block h-10 w-10 rounded-full ring-2 ring-white" src="avatar.jpg" alt="User Name" />
```

> [!TIP]
> **Best Practice**: Fallback to initials if image fails.

> [!NOTE]
> **Accessibility**: Alt text should differ based on context (decoration vs link).



### Badge
> Status indicator

| Feature | Details |
| :--- | :--- |
| **Usage** | Labels, counts, status |
| **Variants** | Success/Warning/Error/Info |
| **CSS Variable** | `--badge-bg` |

**Code Example (Tailwind)**
```tsx
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">Badge</span>
```

> [!TIP]
> **Best Practice**: Use distinct colors for status (Green=Good, Red=Bad).

> [!NOTE]
> **Accessibility**: Ensure text has sufficient contrast.



### Button Primary
> High-emphasis action button

| Feature | Details |
| :--- | :--- |
| **Usage** | Main call-to-actions, submit forms |
| **Variants** | Hover/Active/Disabled |
| **CSS Variable** | `--primary-btn-bg` |

**Code Example (Tailwind)**
```tsx
<button className="bg-primary hover:bg-primary-600 text-white font-bold py-2 px-4 rounded shadow-lg transition-all">Action</button>
```

> [!TIP]
> **Best Practice**: Use only one primary button per screen context.

> [!NOTE]
> **Accessibility**: Ensure min 44x44px touch target. Label must describe action.



### Button Secondary
> Medium-emphasis button

| Feature | Details |
| :--- | :--- |
| **Usage** | Cancel, Back, Secondary options |
| **Variants** | Hover/Active/Disabled |
| **CSS Variable** | `--secondary-btn-bg` |

**Code Example (Tailwind)**
```tsx
<button className="bg-transparent border-2 border-slate-200 hover:border-slate-300 text-slate-700 font-semibold py-2 px-4 rounded transition-colors">Cancel</button>
```

> [!TIP]
> **Best Practice**: Use for negative or alternative actions.

> [!NOTE]
> **Accessibility**: Contrast ratio must be 4.5:1 against background.



### Tooltip
> Contextual help text

| Feature | Details |
| :--- | :--- |
| **Usage** | Icon explanations, truncated text |
| **Variants** | Visible/Hidden |
| **CSS Variable** | `--tooltip-bg` |

**Code Example (Tailwind)**
```tsx
<div className="absolute bottom-full mb-2 bg-slate-900 text-white text-xs rounded py-1 px-2 shadow-lg">Tooltip</div>
```

> [!TIP]
> **Best Practice**: Don't put essential info in tooltips.

> [!NOTE]
> **Accessibility**: Trigger on hover and focus. Escape key should dismiss.



### Input Text
> Single-line text field

| Feature | Details |
| :--- | :--- |
| **Usage** | User data entry, search |
| **Variants** | Focus/Error/Disabled |
| **CSS Variable** | `--input-border` |

**Code Example (Tailwind)**
```tsx
<input type="text" className="w-full border-slate-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-lg px-4 py-2 outline-none transition-shadow" placeholder="Type here..." />
```

> [!TIP]
> **Best Practice**: Include focus states for keyboard navigation.

> [!NOTE]
> **Accessibility**: Always associate with a <label>. Use aria-invalid for errors.



### Toggle
> Instant on/off switch

| Feature | Details |
| :--- | :--- |
| **Usage** | Feature activation, preferences |
| **Variants** | On/Off |
| **CSS Variable** | `--toggle-bg` |

**Code Example (Tailwind)**
```tsx
<div className="w-11 h-6 bg-slate-200 peer-checked:bg-primary rounded-full relative after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full"></div>
```

> [!TIP]
> **Best Practice**: Immediate action, no save required.

> [!NOTE]
> **Accessibility**: Use role="switch" and aria-checked.




## 03. Molecules
## Molecules

### Notification
> Toast message

| Feature | Details |
| :--- | :--- |
| **Usage** | System alerts, success messages |
| **Variants** | Visible/Dismissed |
| **CSS Variable** | `--toast-bg` |

**Code Example (Tailwind)**
```tsx
<div className="fixed bottom-4 right-4 bg-white border-l-4 border-green-500 shadow-lg p-4 rounded">Success!</div>
```

> [!TIP]
> **Best Practice**: Auto-dismiss for success, persistent for errors.

> [!NOTE]
> **Accessibility**: Use role="status" or "alert".



### Breadcrumbs
> Hierarchy navigation

| Feature | Details |
| :--- | :--- |
| **Usage** | Deeply nested pages |
| **Variants** | Current/Parent |
| **CSS Variable** | `--breadcrumb-color` |

**Code Example (Tailwind)**
```tsx
<nav aria-label="Breadcrumb"><ol className="flex space-x-2 text-slate-500"><li>Home</li><li>/</li><li>Settings</li></ol></nav>
```

> [!TIP]
> **Best Practice**: Last item should be current page (text only).

> [!NOTE]
> **Accessibility**: Use nav element with aria-label.



### Pagination
> Navigation for lists

| Feature | Details |
| :--- | :--- |
| **Usage** | Data tables, search results |
| **Variants** | Active Page/Disabled |
| **CSS Variable** | `--pagination-color` |

**Code Example (Tailwind)**
```tsx
<nav className="flex space-x-2"><button className="px-3 py-1 border rounded">1</button></nav>
```

> [!TIP]
> **Best Practice**: Show total pages context.

> [!NOTE]
> **Accessibility**: Identify current page with aria-current="page".



### Tabs
> Content switcher

| Feature | Details |
| :--- | :--- |
| **Usage** | Profile sections, settings groups |
| **Variants** | Active/Inactive |
| **CSS Variable** | `--tab-border` |

**Code Example (Tailwind)**
```tsx
<div className="border-b border-slate-200"><button className="border-b-2 border-primary text-primary px-4 py-2">Tab 1</button></div>
```

> [!TIP]
> **Best Practice**: Support keyboard arrow navigation.

> [!NOTE]
> **Accessibility**: Use role="tablist", "tab", "tabpanel".



### Feature Grid
> Grid of benefit items

| Feature | Details |
| :--- | :--- |
| **Usage** | Landing pages, product features |
| **Variants** | Hover/Static |
| **CSS Variable** | `--feature-icon-bg` |

**Code Example (Tailwind)**
```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-8"><div className="p-6 bg-slate-50 rounded-xl">Icon</div></div>
```

> [!TIP]
> **Best Practice**: Use list structure (ul/li).

> [!NOTE]
> **Accessibility**: Logical reading order.



### Testimonial
> User quote card

| Feature | Details |
| :--- | :--- |
| **Usage** | Social proof, landing pages |
| **Variants** | Carousel/Grid |
| **CSS Variable** | `--testimonial-bg` |

**Code Example (Tailwind)**
```tsx
<figure className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm"><blockquote>Quote</blockquote><figcaption>User</figcaption></figure>
```

> [!TIP]
> **Best Practice**: Pause auto-rotation on hover.

> [!NOTE]
> **Accessibility**: Use figure/figcaption for semantic value.



### Search Bar
> Input with search icon

| Feature | Details |
| :--- | :--- |
| **Usage** | Global search, filter lists |
| **Variants** | Active/Filled |
| **CSS Variable** | `--search-bg` |

**Code Example (Tailwind)**
```tsx
<div className="relative"><SearchIcon className="absolute left-3 top-3 text-slate-400" /><input className="pl-10 w-full rounded-lg border-slate-200" /></div>
```

> [!TIP]
> **Best Practice**: Debounce inputs for performance.

> [!NOTE]
> **Accessibility**: Label as 'Search site'.



### Card
> Container for related content

| Feature | Details |
| :--- | :--- |
| **Usage** | Dashboard widgets, Product listings |
| **Variants** | Hover/Selected |
| **CSS Variable** | `--card-bg` |

**Code Example (Tailwind)**
```tsx
<div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 hover:shadow-md transition-shadow">Content</div>
```

> [!TIP]
> **Best Practice**: Avoid cluttered content; use whitespace.

> [!NOTE]
> **Accessibility**: Heading structure inside card should be logical.



### File Upload
> Drag and drop zone

| Feature | Details |
| :--- | :--- |
| **Usage** | Profile picture, Document submission |
| **Variants** | Dragging/Uploading/Done |
| **CSS Variable** | `--upload-border` |

**Code Example (Tailwind)**
```tsx
<div className="border-2 border-dashed border-slate-300 rounded-lg p-12 text-center hover:border-primary cursor-pointer">Drop files here</div>
```

> [!TIP]
> **Best Practice**: Provide visual feedback during drag.

> [!NOTE]
> **Accessibility**: Allow keyboard activation (Enter/Space).



### Glass Card
> Premium container

| Feature | Details |
| :--- | :--- |
| **Usage** | Modern dashboards, overlays |
| **Variants** | Hover/Static |
| **CSS Variable** | `--glass-bg` |

**Code Example (Tailwind)**
```tsx
<div className="backdrop-blur-xl bg-white/70 border border-white/20 shadow-xl rounded-2xl p-6">Glass Content</div>
```

> [!TIP]
> **Best Practice**: Use mostly in dark mode or colorful backgrounds.

> [!NOTE]
> **Accessibility**: Ensure text contrast on transparent backgrounds.



### Stats Widget
> Display key metrics

| Feature | Details |
| :--- | :--- |
| **Usage** | Dashboard summaries, KPIs |
| **Variants** | Trend Up/Down |
| **CSS Variable** | `--stat-value-color` |

**Code Example (Tailwind)**
```tsx
<div className="p-6 bg-white rounded-xl border border-slate-100"><p className="text-sm text-slate-500">Revenue</p><p className="text-2xl font-bold text-slate-900">$24,000</p></div>
```

> [!TIP]
> **Best Practice**: Show trend context (up/down) clearly.

> [!NOTE]
> **Accessibility**: Use distinct headers for screen readers.



### Metric Card
> Key value display

| Feature | Details |
| :--- | :--- |
| **Usage** | Dashboards, analytics |
| **Variants** | Trend Up/Down |
| **CSS Variable** | `--metric-bg` |

**Code Example (Tailwind)**
```tsx
<div className="bg-white p-6 rounded-xl border border-slate-100"><dt className="text-sm font-medium text-slate-500">Users</dt><dd className="mt-1 text-3xl font-semibold text-slate-900">71,897</dd></div>
```

> [!TIP]
> **Best Practice**: Trend colors needs text fallback.

> [!NOTE]
> **Accessibility**: Use dl/dt/dd for key-value pairs.



### Pricing Card
> Subscription tier display

| Feature | Details |
| :--- | :--- |
| **Usage** | Landing pages, pricing sections |
| **Variants** | Highlighted/Standard |
| **CSS Variable** | `--pricing-card-bg` |

**Code Example (Tailwind)**
```tsx
<div className="border border-slate-200 rounded-2xl p-8 hover:border-primary hover:shadow-xl transition-all relative"><span className="absolute top-0 right-0 bg-primary text-white px-3 py-1 rounded-bl-xl rounded-tr-xl text-sm">Popular</span><h3>Pro</h3></div>
```

> [!TIP]
> **Best Practice**: Clear distinct CTA buttons.

> [!NOTE]
> **Accessibility**: Highlight 'Best Value' explicitly.




## 04. Organisms
## Organisms

### Footer
> Bottom navigation

| Feature | Details |
| :--- | :--- |
| **Usage** | Copyright, sitemap, social links |
| **Variants** | Default |
| **CSS Variable** | `--footer-bg` |

**Code Example (Tailwind)**
```tsx
<footer className="bg-slate-50 border-t border-slate-200 py-12"><div className="grid grid-cols-4 gap-8 max-w-7xl mx-auto px-4">Links</div></footer>
```

> [!TIP]
> **Best Practice**: Include essential legal links.

> [!NOTE]
> **Accessibility**: Group links logically.



### Stock Chart
> Financial data visualization

| Feature | Details |
| :--- | :--- |
| **Usage** | Fintech dashboards, trading |
| **Variants** | Candlestick/Line |
| **CSS Variable** | `--chart-line-color` |

**Code Example (Tailwind)**
```tsx
<div className="h-64 w-full bg-slate-50 rounded-lg flex items-center justify-center text-slate-400">[Chart Component]</div>
```

> [!TIP]
> **Best Practice**: Use patterns/textures + color.

> [!NOTE]
> **Accessibility**: Provide data table alternative.



### Data Table
> Complex row/column data

| Feature | Details |
| :--- | :--- |
| **Usage** | Admin dashboards, user lists |
| **Variants** | Sort/Filter/Pagination |
| **CSS Variable** | `--table-header-bg` |

**Code Example (Tailwind)**
```tsx
<table className="min-w-full divide-y divide-slate-200"><thead className="bg-slate-50"><tr><th>Name</th></tr></thead></table>
```

> [!TIP]
> **Best Practice**: Sticky headers for long lists.

> [!NOTE]
> **Accessibility**: Use th scope attributes. Keyboard sortable headers.



### Sidebar
> Vertical navigation

| Feature | Details |
| :--- | :--- |
| **Usage** | App navigation, filters |
| **Variants** | Collapsed/Expanded |
| **CSS Variable** | `--sidebar-bg` |

**Code Example (Tailwind)**
```tsx
<aside className="w-64 bg-slate-900 text-slate-300 h-screen fixed"><nav className="p-4 space-y-2"><a href="#" className="block p-2 hover:bg-slate-800 rounded">Home</a></nav></aside>
```

> [!TIP]
> **Best Practice**: Collapse state uses aria-expanded.

> [!NOTE]
> **Accessibility**: Identify as navigation landmark.



### Drawer
> Side panel overlay

| Feature | Details |
| :--- | :--- |
| **Usage** | Mobile navigation, detailed filters |
| **Variants** | Open/Closed |
| **CSS Variable** | `--drawer-width` |

**Code Example (Tailwind)**
```tsx
<div className="fixed inset-y-0 right-0 w-80 bg-white shadow-2xl transform transition-transform">Drawer Content</div>
```

> [!TIP]
> **Best Practice**: Good for filters or details without leaving context.

> [!NOTE]
> **Accessibility**: Trap focus. Close button is mandatory.



### Modal
> Overlay dialog

| Feature | Details |
| :--- | :--- |
| **Usage** | Critical alerts, simplified forms |
| **Variants** | Open/Closed |
| **CSS Variable** | `--modal-overlay` |

**Code Example (Tailwind)**
```tsx
<div className="fixed inset-0 bg-black/50 flex items-center justify-center"><div className="bg-white rounded-lg p-6 max-w-md w-full">Dialog</div></div>
```

> [!TIP]
> **Best Practice**: Use for interrupting flows only.

> [!NOTE]
> **Accessibility**: Trap focus inside modal. Background click dismisses.



### Navbar
> Top navigation bar

| Feature | Details |
| :--- | :--- |
| **Usage** | Site-wide links, branding |
| **Variants** | Sticky/Transparent |
| **CSS Variable** | `--nav-bg` |

**Code Example (Tailwind)**
```tsx
<header className="sticky top-0 bg-white/80 backdrop-blur-md border-b border-slate-100 z-50"><nav className="max-w-7xl mx-auto px-4 h-16 flex items-center">Logo</nav></header>
```

> [!TIP]
> **Best Practice**: Responsive burger menu for mobile.

> [!NOTE]
> **Accessibility**: Skip link inclusion recommended.



### Credit Card
> Virtual card display

| Feature | Details |
| :--- | :--- |
| **Usage** | Wallet apps, checkout |
| **Variants** | Active/Frozen |
| **CSS Variable** | `--card-gradient` |

**Code Example (Tailwind)**
```tsx
<div className="w-96 h-56 bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6 text-white shadow-2xl relative overflow-hidden"><div className="absolute top-0 right-0 p-6 opacity-20">Logo</div></div>
```

> [!TIP]
> **Best Practice**: Contrast on gradient background.

> [!NOTE]
> **Accessibility**: Hide sensitive numbers.



### Transaction List
> History of payments

| Feature | Details |
| :--- | :--- |
| **Usage** | Banking apps, receipts |
| **Variants** | Pending/Completed |
| **CSS Variable** | `--list-row-hover` |

**Code Example (Tailwind)**
```tsx
<ul className="divide-y divide-slate-100"><li className="flex justify-between py-4 hover:bg-slate-50 px-4 -mx-4 rounded-lg transition-colors">Item</li></ul>
```

> [!TIP]
> **Best Practice**: Color code amounts (Green/Red) with symbols.

> [!NOTE]
> **Accessibility**: Use table or list semantics.



### AI Chat Interface
> Conversation view

| Feature | Details |
| :--- | :--- |
| **Usage** | Chatbots, support agents |
| **Variants** | Typing/Sent/Received |
| **CSS Variable** | `--chat-bubble-bg` |

**Code Example (Tailwind)**
```tsx
<div className="flex flex-col h-[500px] border rounded-xl"><div className="flex-1 overflow-y-auto p-4 space-y-4"><div className="bg-primary-50 p-3 rounded-lg self-end">Hello</div></div></div>
```

> [!TIP]
> **Best Practice**: Differentiate user vs bot visually.

> [!NOTE]
> **Accessibility**: Auto-scroll to bottom. Live region for new messages.



### Hero Section
> Primary landing area

| Feature | Details |
| :--- | :--- |
| **Usage** | Home page top, marketing |
| **Variants** | Default/Video/Image |
| **CSS Variable** | `--hero-bg` |

**Code Example (Tailwind)**
```tsx
<section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden bg-slate-900"><div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center"><h1>Headline</h1></div></section>
```

> [!TIP]
> **Best Practice**: Images need alt text or empty if decorative.

> [!NOTE]
> **Accessibility**: H1 must be unique.



### Mesh Gradient Hero
> Premium Modern Hero

| Feature | Details |
| :--- | :--- |
| **Usage** | SaaS, AI Startups |
| **Variants** | Default |
| **CSS Variable** | `--hero-mesh-bg` |

**Code Example (Tailwind)**
```tsx
<div className="relative overflow-hidden bg-slate-900"><div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-500/30 blur-[120px] rounded-full mix-blend-screen"></div><div className="relative z-10 container mx-auto">Content</div></div>
```

> [!TIP]
> **Best Practice**: Disable heavy blur for reduced motion users.

> [!NOTE]
> **Accessibility**: Ensure text contrast over gradient.




---
*Generated by Design Pro CLI v0.1.1*