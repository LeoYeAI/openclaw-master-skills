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

### Toggle
**Usage:** Feature activation, preferences
**Variants:** On/Off
**CSS Variable:** `--toggle-bg`

> Instant on/off switch


### Avatar
**Usage:** Comments, profile headers
**Variants:** Image/Initials/Icon
**CSS Variable:** `--avatar-size`

> User profile image


### Button Secondary
**Usage:** Cancel, Back, Secondary options
**Variants:** Hover/Active/Disabled
**CSS Variable:** `--secondary-btn-bg`

> Medium-emphasis button


### Badge
**Usage:** Labels, counts, status
**Variants:** Success/Warning/Error/Info
**CSS Variable:** `--badge-bg`

> Status indicator


### Tooltip
**Usage:** Icon explanations, truncated text
**Variants:** Visible/Hidden
**CSS Variable:** `--tooltip-bg`

> Contextual help text


### Button Ghost
**Usage:** Icon-only actions, tertiary links
**Variants:** Hover/Active/Disabled
**CSS Variable:** `--ghost-btn-bg`

> Low-emphasis button


### Checkbox
**Usage:** Settings, multi-select lists
**Variants:** Checked/Unchecked/Indeterminate
**CSS Variable:** `--checkbox-color`

> Binary selection control


### Radio
**Usage:**  mutually exclusive options
**Variants:** Selected/Unselected
**CSS Variable:** `--radio-color`

> Single selection from list


### Button Primary
**Usage:** Main call-to-actions, submit forms
**Variants:** Hover/Active/Disabled
**CSS Variable:** `--primary-btn-bg`

> High-emphasis action button


### Input Text
**Usage:** User data entry, search
**Variants:** Focus/Error/Disabled
**CSS Variable:** `--input-border`

> Single-line text field



## 03. Molecules
## Molecules

### Notification
**Usage:** System alerts, success messages
**Variants:** Visible/Dismissed
**CSS Variable:** `--toast-bg`

> Toast message


### Breadcrumbs
**Usage:** Deeply nested pages
**Variants:** Current/Parent
**CSS Variable:** `--breadcrumb-color`

> Hierarchy navigation


### Tabs
**Usage:** Profile sections, settings groups
**Variants:** Active/Inactive
**CSS Variable:** `--tab-border`

> Content switcher


### Search Bar
**Usage:** Global search, filter lists
**Variants:** Active/Filled
**CSS Variable:** `--search-bg`

> Input with search icon


### Pricing Card
**Usage:** Landing pages, pricing sections
**Variants:** Highlighted/Standard
**CSS Variable:** `--pricing-card-bg`

> Subscription tier display


### Feature Grid
**Usage:** Landing pages, product features
**Variants:** Hover/Static
**CSS Variable:** `--feature-icon-bg`

> Grid of benefit items


### Testimonial
**Usage:** Social proof, landing pages
**Variants:** Carousel/Grid
**CSS Variable:** `--testimonial-bg`

> User quote card


### Metric Card
**Usage:** Dashboards, analytics
**Variants:** Trend Up/Down
**CSS Variable:** `--metric-bg`

> Key value display


### Card
**Usage:** Dashboard widgets, Product listings
**Variants:** Hover/Selected
**CSS Variable:** `--card-bg`

> Container for related content


### Stats Widget
**Usage:** Dashboard summaries, KPIs
**Variants:** Trend Up/Down
**CSS Variable:** `--stat-value-color`

> Display key metrics


### File Upload
**Usage:** Profile picture, Document submission
**Variants:** Dragging/Uploading/Done
**CSS Variable:** `--upload-border`

> Drag and drop zone


### Pagination
**Usage:** Data tables, search results
**Variants:** Active Page/Disabled
**CSS Variable:** `--pagination-color`

> Navigation for lists



## 04. Organisms
## Organisms

### Sidebar
**Usage:** App navigation, filters
**Variants:** Collapsed/Expanded
**CSS Variable:** `--sidebar-bg`

> Vertical navigation


### Footer
**Usage:** Copyright, sitemap, social links
**Variants:** Default
**CSS Variable:** `--footer-bg`

> Bottom navigation


### Modal
**Usage:** Critical alerts, simplified forms
**Variants:** Open/Closed
**CSS Variable:** `--modal-overlay`

> Overlay dialog


### Navbar
**Usage:** Site-wide links, branding
**Variants:** Sticky/Transparent
**CSS Variable:** `--nav-bg`

> Top navigation bar


### Credit Card
**Usage:** Wallet apps, checkout
**Variants:** Active/Frozen
**CSS Variable:** `--card-gradient`

> Virtual card display


### Drawer
**Usage:** Mobile navigation, detailed filters
**Variants:** Open/Closed
**CSS Variable:** `--drawer-width`

> Side panel overlay


### Stock Chart
**Usage:** Fintech dashboards, trading
**Variants:** Candlestick/Line
**CSS Variable:** `--chart-line-color`

> Financial data visualization


### Transaction List
**Usage:** Banking apps, receipts
**Variants:** Pending/Completed
**CSS Variable:** `--list-row-hover`

> History of payments


### AI Chat Interface
**Usage:** Chatbots, support agents
**Variants:** Typing/Sent/Received
**CSS Variable:** `--chat-bubble-bg`

> Conversation view


### Data Table
**Usage:** Admin dashboards, user lists
**Variants:** Sort/Filter/Pagination
**CSS Variable:** `--table-header-bg`

> Complex row/column data


### Hero Section
**Usage:** Home page top, marketing
**Variants:** Default/Video/Image
**CSS Variable:** `--hero-bg`

> Primary landing area



---
*Generated by Design Pro CLI v0.1.1*