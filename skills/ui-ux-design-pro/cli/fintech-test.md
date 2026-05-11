# Design System: Data Brutalism

> **Query**: "Fintech Dashboard" | **Generated**: 2/18/2026

## 01. Foundation
- **Primary Color**: `#00FF00` ![#00FF00](https://via.placeholder.com/15/00FF00/000000?text=+)
- **Typography**: **Outfit** (Headings & Body)

### Color Palette
#### Primary Brand
| Stop | Hex | Preview |
| :--- | :--- | :--- |
| **50** | `#E5FFE5` | ![#E5FFE5](https://via.placeholder.com/80x30/E5FFE5/E5FFE5?text=+) |
| **100** | `#CCFFCC` | ![#CCFFCC](https://via.placeholder.com/80x30/CCFFCC/CCFFCC?text=+) |
| **200** | `#99FF99` | ![#99FF99](https://via.placeholder.com/80x30/99FF99/99FF99?text=+) |
| **300** | `#66FF66` | ![#66FF66](https://via.placeholder.com/80x30/66FF66/66FF66?text=+) |
| **400** | `#33FF33` | ![#33FF33](https://via.placeholder.com/80x30/33FF33/33FF33?text=+) |
| **500** | `#00FF00` | ![#00FF00](https://via.placeholder.com/80x30/00FF00/00FF00?text=+) |
| **600** | `#00CC00` | ![#00CC00](https://via.placeholder.com/80x30/00CC00/00CC00?text=+) |
| **700** | `#009900` | ![#009900](https://via.placeholder.com/80x30/009900/009900?text=+) |
| **800** | `#006600` | ![#006600](https://via.placeholder.com/80x30/006600/006600?text=+) |
| **900** | `#003300` | ![#003300](https://via.placeholder.com/80x30/003300/003300?text=+) |
| **950** | `#001A00` | ![#001A00](https://via.placeholder.com/80x30/001A00/001A00?text=+) |

#### Neutral
| Stop | Hex | Preview |
| :--- | :--- | :--- |
| **50** | `#E7FEE7` | ![#E7FEE7](https://via.placeholder.com/80x30/E7FEE7/E7FEE7?text=+) |
| **100** | `#CFFCCF` | ![#CFFCCF](https://via.placeholder.com/80x30/CFFCCF/CFFCCF?text=+) |
| **200** | `#A1F7A1` | ![#A1F7A1](https://via.placeholder.com/80x30/A1F7A1/A1F7A1?text=+) |
| **300** | `#71F471` | ![#71F471](https://via.placeholder.com/80x30/71F471/71F471?text=+) |
| **400** | `#42F042` | ![#42F042](https://via.placeholder.com/80x30/42F042/42F042?text=+) |
| **500** | `#13EC13` | ![#13EC13](https://via.placeholder.com/80x30/13EC13/13EC13?text=+) |
| **600** | `#0FBD0F` | ![#0FBD0F](https://via.placeholder.com/80x30/0FBD0F/0FBD0F?text=+) |
| **700** | `#0B8E0B` | ![#0B8E0B](https://via.placeholder.com/80x30/0B8E0B/0B8E0B?text=+) |
| **800** | `#085E08` | ![#085E08](https://via.placeholder.com/80x30/085E08/085E08?text=+) |
| **900** | `#033003` | ![#033003](https://via.placeholder.com/80x30/033003/033003?text=+) |
| **950** | `#011801` | ![#011801](https://via.placeholder.com/80x30/011801/011801?text=+) |

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