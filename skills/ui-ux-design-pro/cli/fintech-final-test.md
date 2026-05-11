# Design System: Fintech

> **Query**: "Fintech Dashboard" | **Generated**: 2/18/2026

## 01. Foundation
- **Primary Color**: `#0f172a` ![#0f172a](https://via.placeholder.com/15/0f172a/000000?text=+)
- **Typography**: **Outfit** (Headings & Body)

### Color Palette
#### Primary Brand
| Stop | Hex | Preview |
| :--- | :--- | :--- |
| **50** | `#ECF0F9` | ![#ECF0F9](https://via.placeholder.com/80x30/ECF0F9/ECF0F9?text=+) |
| **100** | `#D8E0F3` | ![#D8E0F3](https://via.placeholder.com/80x30/D8E0F3/D8E0F3?text=+) |
| **200** | `#B4C2E4` | ![#B4C2E4](https://via.placeholder.com/80x30/B4C2E4/B4C2E4?text=+) |
| **300** | `#8FA4D6` | ![#8FA4D6](https://via.placeholder.com/80x30/8FA4D6/8FA4D6?text=+) |
| **400** | `#6986C9` | ![#6986C9](https://via.placeholder.com/80x30/6986C9/6986C9?text=+) |
| **500** | `#4468BB` | ![#4468BB](https://via.placeholder.com/80x30/4468BB/4468BB?text=+) |
| **600** | `#365396` | ![#365396](https://via.placeholder.com/80x30/365396/365396?text=+) |
| **700** | `#293E70` | ![#293E70](https://via.placeholder.com/80x30/293E70/293E70?text=+) |
| **800** | `#1B294B` | ![#1B294B](https://via.placeholder.com/80x30/1B294B/1B294B?text=+) |
| **900** | `#0C1427` | ![#0C1427](https://via.placeholder.com/80x30/0C1427/0C1427?text=+) |
| **950** | `#060A13` | ![#060A13](https://via.placeholder.com/80x30/060A13/060A13?text=+) |

#### Neutral
| Stop | Hex | Preview |
| :--- | :--- | :--- |
| **50** | `#EEF0F7` | ![#EEF0F7](https://via.placeholder.com/80x30/EEF0F7/EEF0F7?text=+) |
| **100** | `#DCE2EF` | ![#DCE2EF](https://via.placeholder.com/80x30/DCE2EF/DCE2EF?text=+) |
| **200** | `#BCC5DC` | ![#BCC5DC](https://via.placeholder.com/80x30/BCC5DC/BCC5DC?text=+) |
| **300** | `#9AA9CB` | ![#9AA9CB](https://via.placeholder.com/80x30/9AA9CB/9AA9CB?text=+) |
| **400** | `#788CBA` | ![#788CBA](https://via.placeholder.com/80x30/788CBA/788CBA?text=+) |
| **500** | `#576FA8` | ![#576FA8](https://via.placeholder.com/80x30/576FA8/576FA8?text=+) |
| **600** | `#455987` | ![#455987](https://via.placeholder.com/80x30/455987/455987?text=+) |
| **700** | `#344365` | ![#344365](https://via.placeholder.com/80x30/344365/344365?text=+) |
| **800** | `#232C43` | ![#232C43](https://via.placeholder.com/80x30/232C43/232C43?text=+) |
| **900** | `#101623` | ![#101623](https://via.placeholder.com/80x30/101623/101623?text=+) |
| **950** | `#080B11` | ![#080B11](https://via.placeholder.com/80x30/080B11/080B11?text=+) |

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