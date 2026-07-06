---
name: web-replication
description: Use Playwright MCP or the agent-browser skill to systematically explore all internal pages of a target website, collect screenshots, interaction logic, and assets, and output a “website replication blueprint” whose folder hierarchy reflects page navigation relationships. Finally, based on the exploration results, fully replicate the entire target website, ensuring the replicated site matches the original in content and structure as strictly as possible.
read_when:
  - When you need to replicate a target website and keep it as consistent as possible with the original in visual design, content structure, and interactions
  - When you need to create a high-fidelity replica of a target website
  - When you need to reconstruct a website’s page structure, visual style, and interaction logic
  - When you need to rebuild frontend pages based on real webpage content rather than designing from scratch
  - When you need to preserve the original website’s content, structure, and presentation to the greatest extent possible
allowed-tools: Bash(web-replication:*)
---
# Website GUI Exploration, Blueprint Generation, and Replication

## Prerequisites
This workflow depends on either Playwright MCP or the agent-browser skill. As long as at least one of them is installed and available, the workflow can run normally. If neither is available in your environment, remind the user to install one.

## Core Idea
1. Recursively explore every internal page of the target website, systematically record its visual content, interaction logic, and asset files, and finally organize everything into a structured “website replication blueprint.” This blueprint should not only comprehensively include detailed information for each page, but also naturally map the site’s navigation relationships through folder hierarchy. Specifically, during exploration, use nested folders to organize and record the collected page information: represent the current page as a folder, and represent all pages reachable from it as child folders. At the same time, save that page’s screenshots, component interaction records, and related asset files inside the page folder. With this structure, the final blueprint will clearly present both the content and interaction details of each page, while also implicitly reflecting the website’s overall information architecture and navigation paths.

An example blueprint folder structure:
```text
blueprint/
├── _meta.md                      # Site-wide metadata
├── _sitemap.md                   # Sitemap
├── _assets/                      # Global assets (fonts, favicon, etc.)
├── home/                         # Homepage
│   ├── _page.md                  # Page blueprint (sections, components, interaction summary)
│   ├── _full.png                 # Full-page screenshot
│   ├── _scroll_00.png ~ N.png    # Scrolling screenshot sequence
│   ├── _interactions.md          # Record of all interactions
│   ├── _interactions/            # Interaction state screenshots (organized by interaction type)
│   ├── _assets/                  # Assets for this page (images, videos, etc.)
│   ├── products/                 # "Product list" reachable from homepage
│   │   ├── _page.md
│   │   ├── _full.png
│   │   ├── _scroll_00.png ~ N.png 
│   │   ├── _interactions.md
│   │   ├── _interactions/
│   │   ├── _assets/
│   │   ├── product-detail/       # "Product detail" reachable from product list
│   │   │   ├── _page.md
│   │   │   └── ...
│   │   └── category/             # "Category filter" reachable from product list
│   │       └── ...
│   ├── about/                    # "About us" reachable from homepage
│   │   └── ...
│   ├── blog/                     # "Blog" reachable from homepage
│   │   └── ...
│   └── login/                    # "Login" reachable from homepage
│       └── ...
└── _navigation_graph.md          # Site-wide navigation graph (Mermaid)
```

2. After completing the blueprint construction above, fully replicate the target website based on that blueprint, restoring page-to-page navigation relationships, content presentation, information architecture, page layout, and interaction logic as completely as possible.

## Replication Workflow
The whole process is divided into five phases: initialization → recursively collect pages and build the sitemap → generate summary outputs → fully replicate the website → compare against the original and revise.

The first three phases focus on exploration and documentation, while the final two phases focus on implementing the actual replication based on the collected blueprint and verifying it. Below, the agent-browser workflow is used as an example; if using Playwright MCP, the overall process and usage are essentially the same and can be followed with the same approach.

### Step 1: Initialize the project
```bash
# Create the blueprint root directory
mkdir -p blueprint/_assets
# Open the browser and visit the target site
agent-browser open <target URL>
agent-browser set viewport 1920 1080
agent-browser wait --load networkidle
```

Write the following content into `blueprint/_meta.md`:
```markdown
# Website Replication Blueprint
- Target website: <URL>
- Exploration date: <date>
- Viewport size: 1920×1080
```

### Step 2: Recursively collect pages and build the sitemap
For every recursively discovered page, execute the following standard procedure:

First capture a full-page screenshot → download assets → traverse interaction states → scroll down → download assets again → traverse interaction states again → scroll down again → ... → continue until reaching the bottom of the page.

#### 2.1: Asset download
After opening the page and waiting for it to fully load, collect all asset links on the page (images, videos, fonts, etc.) and download them into that page’s `_assets/` directory whenever possible. Record all failed downloads and the reasons for failure.

#### 2.2: Traverse interaction states
Obtain the list of interactive elements on the page, interact with all of them, capture UI changes, and record all newly discovered pages.

```bash
# === Example using a product list page before any downward scrolling ===
agent-browser open <Product List URL>
agent-browser screenshot blueprint/home/products/_scroll_00.png
agent-browser wait --load networkidle
agent-browser snapshot -i 
# Suppose the output is:
# button "All" [ref=e1]                ← filter tab
# button "Electronics" [ref=e2]
# card "Product A" [ref=e3]            ← product card
# select "Sort" [ref=e4]               ← sort dropdown
# link "Home" [ref=e5]                 ← breadcrumb link
# button "Learn More" [ref=e6]         ← button inside product card
# --- Interaction 1: hover over product card ---
agent-browser hover @e3
agent-browser screenshot blueprint/home/products/_interactions/card_hover.png
# --- Interaction 2: click filter tab ---
agent-browser click @e2
agent-browser wait --load networkidle
agent-browser screenshot blueprint/home/products/_interactions/filter_electronics.png
# --- Interaction 3: change sorting ---
agent-browser select @e4 "Price: Low to High"
agent-browser wait --load networkidle
agent-browser screenshot blueprint/home/products/_interactions/sort_price_asc.png
# --- Interaction 4: click product card (triggers navigation) ---
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser get url    # → /products/123
agent-browser screenshot blueprint/home/products/product-detail/_full.png --full
agent-browser back
# --- Interaction 5: click breadcrumb "Home" ---
agent-browser click @e5
agent-browser wait --load networkidle
agent-browser get url    # → /
agent-browser screenshot blueprint/home/_full.png --full
agent-browser back
# --- Interaction 6: click "Learn More" button (external navigation) ---
agent-browser click @e6
agent-browser wait --load networkidle
agent-browser get url    # → https://www.angelokeirsebilck.be/
agent-browser screenshot blueprint/home/products/_interactions/learn_more_external.png --full
agent-browser back
```

Write the updated sitemap into `blueprint/_sitemap.md`.

Write the updated page collection results into `blueprint/home/products/_page.md`:
```markdown
# Product List Page
- URL: /products
- Source: Homepage main navigation "Products" link

## Section Structure
| No. | Section Name | Layout Pattern | Content Type |
|------|--------------|----------------|--------------|
| 1 | Page header | Full-width single column | H1 heading + descriptive text |
| 2 | Filter bar | Horizontal layout | Category tabs + sorting dropdown |
| 3 | Product grid | 3-column grid | Product cards × N |
| 4 | Pagination | Centered single column | Pagination button group |

## Screenshots
- Full page: ![Full page screenshot](./_full.png)
- Scroll sequence: ![Screen 1](./_scroll_00.png) ![Screen 2](./_scroll_01.png)

## Outbound Navigation
| Trigger Element | Trigger Method | Target | Child Folder |
|----------------|----------------|--------|--------------|
| Product card | Click | /products/:id | ./product-detail/ |
| Category tab | Click | /products/category/:slug | ./category/ |
| Breadcrumb "Home" | Click | / | (return to parent) |
| Learn More button | Click | https://www.angelokeirsebilck.be/ | None |

## Page Assets
| File | Purpose |
|------|---------|
| _assets/product-01.jpg | Product card thumbnail |
| _assets/product-02.jpg | Product card thumbnail |
```

Write all updated interactions into `blueprint/home/products/_interactions.md`:
```markdown
# Product List Page - Interaction Behavior

## Interaction List
| Element | Trigger Method | Behavior | Navigation | Screenshot |
|---------|----------------|----------|------------|------------|
| Product card | hover | Card rises + shadow deepens | No | ![](./_interactions/card_hover.png) |
| Product card | click | Navigates to product detail | Yes → ./product-detail/ | — |
| Filter tab "Electronics" | click | List refreshes to electronics category | No (AJAX) | ![](./_interactions/filter_electronics.png) |
| Sort dropdown | select | Product list reorders | No (AJAX) | ![](./_interactions/sort_price_asc.png) |
| Breadcrumb "Home" | click | Navigates to homepage | Yes → ../ | — |
| Learn More button | click | Opens external link | Yes → https://www.angelokeirsebilck.be/ | — |

## State Transitions
Default list --[click filter tab]--> Filtered list
Default list --[change sorting]--> Sorted list
Product card (default) --[hover]--> Product card (hover state)
Product card --[click]--> /products/:id (navigation)
Learn More button --[click]--> External link (navigation to https://www.angelokeirsebilck.be/)
```

### Step 3: Generate summary outputs
After all page collection is complete, generate the global summary files.

#### `blueprint/_sitemap.md`
```markdown
# Sitemap
home/                          # / (homepage)
├── products/                  # /products (product list)
│   ├── product-detail/        # /products/:id (product detail)
│   └── category/              # /products/category/:slug (category)
├── about/                     # /about (about us)
├── blog/                      # /blog (blog list)
│   └── blog-post/             # /blog/:slug (blog post)
├── contact/                   # /contact (contact us)
└── login/                     # /auth/login (login)
    └── register/              # /auth/register (register)
```

#### `blueprint/_navigation_graph.md`
```markdown
# Site-wide Navigation Graph
graph LR
    Home["home /"] -->|Nav - Products| Products["products /products"]
    Home -->|Nav - About| About["about /about"]
    Home -->|Nav - Blog| Blog["blog /blog"]
    Home -->|Header - Login| Login["login /auth/login"]
    Products -->|Card click| Detail["product-detail /products/:id"]
    Products -->|Filter tab| Category["category /products/category/:slug"]
    Blog -->|Post card| Post["blog-post /blog/:slug"]
    Login -->|Register link| Register["register /auth/register"]

## Navigation Details
| ID | Source Folder | Trigger Element | Target Folder | Navigation Type |
|----|---------------|----------------|---------------|-----------------|
| N001 | home/ | Main nav "Products" | home/products/ | Internal |
| N002 | home/ | Hero CTA button | home/products/ | Internal |
| N003 | home/products/ | Product card | home/products/product-detail/ | Internal |
| N004 | home/products/ | Category tab "Electronics" | home/products/category/ | Internal |
| N005 | home/products/ | Breadcrumb "Home" | home/ | Internal |
| N006 | home/products/ | Learn More button | External link https://www.angelokeirsebilck.be/ | External |
| ... | ... | ... | ... | ... |
```

#### Close the browser
```bash
agent-browser close
```

### Step 4: Replication
After completing website exploration and blueprint generation, perform the actual replication based on the collected blueprint. During replication, refer to the blueprint’s page structures, visual styles, interaction logic, and asset files, and use your preferred frontend tools and frameworks to rebuild the website. Follow the recorded page structures, visual styles, and interaction behaviors to ensure the replicated site matches the original as closely as possible in presentation.

### Step 5: Compare, verify, and revise
After finishing the replication, use Playwright MCP or the agent-browser skill to render both the original website and the replicated website, systematically compare them for consistency in content, structure, visuals, and interactions, verify the degree of reproduction page by page, and make precise adjustments based on the comparison results to ensure the replicated site remains highly consistent with the original in every aspect.

## Key Rules
1. Folders represent navigation relationships. If page A can navigate to page B, then page B should be created as a subfolder inside page A’s folder.
2. If multiple pages can navigate to the same target page, you may skip redundant exploration of that page and create its folder only once under the most natural parent. However, all navigation sources must still be recorded in `_sitemap.md`, `_navigation_graph.md`, and the related pages’ `_page.md` files.
3. Every folder must contain:
   - `_page.md` — page blueprint (sections, components, outbound navigation)
   - `_full.png` — full-page screenshot
   - `_interactions.md` — interaction behavior record
   - `_interactions/` — directory for interaction state screenshots
   - `_assets/` — page-specific assets
   - scrolling screenshot sequence `_scroll_00.png` ~ `_scroll_N.png`
4. Screenshots must be captured from the real site. Do not describe visual information from memory; all visual details must be based on actual screenshots.
5. Interactions must be genuinely triggered and recorded one by one, including hover, click, focus, and so on.
6. Assets should be downloaded whenever possible. Use `curl` to download images, and use `agent-browser eval` or Playwright MCP to extract SVG source code and save it. All failed downloads must be recorded together with the reasons for failure.
7. Record only; do not evaluate. Accurately document observed results without making quality judgments.
8. Keep files updated in real time. After finishing exploration of each page window, update the sitemap and all related blueprint files such as `_page.md` and `_interactions.md` so the output always remains synchronized with the current exploration state.
9. Ensure elements are visible. Before interacting with any page element, make sure the target element is within the visible viewport. Scroll the page or adjust the viewport position if necessary.
10. Each call to `agent-browser` may execute only one command, such as taking a screenshot, getting the element list, or performing one interaction. Do not combine multiple commands in a single call. The consecutive commands in the example are only for illustrating the workflow; in actual execution they must be split into separate calls.
11. If interaction with a webpage element triggers navigation to an external domain, there is no need to deeply explore or continue scraping that external page. However, you must record the key information of that external link, including the external URL, the page element that triggered the link (text/button name/selector or ref), and the trigger method (such as click). In the replicated website, the corresponding page element should preserve the same trigger method and external destination.
12. `_full.png` is used to record the overall visual overview of the page, while the scrolling screenshot sequence (`_scroll_00.png` ~ `_scroll_N.png`) can record details of each segment. During website replication, both the overall information from the full-page screenshot and the detailed information from the scrolling screenshot sequence should be referenced together to ensure accurate visual reproduction and complete detail restoration.