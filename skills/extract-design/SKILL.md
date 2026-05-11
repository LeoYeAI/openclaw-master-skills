---
name: extract-design
description: Use this skill when the user wants to extract a webpage's design language into a reusable HTML style reference file, including typography, colors, spacing, surfaces, components, states, themes, motion, code-block styles, background atmosphere, decorative motifs, and art direction. The output should be a universal style specimen HTML for future AI-generated pages, not a 1:1 copy of the original page. Extracted style files are saved to the skill's own `assets/theme/` directory, never to the user's project.
---

# Extract Design

## Output Location

**CRITICAL**: All extracted style files MUST be saved to the skill's own `assets/theme/` directory — never to the user's project directory, never to a relative path from the current working directory.

**Before writing any output file**, resolve the skill directory by running:

```
Glob pattern: **/skills/extract-design/SKILL.md
```

The directory containing that `SKILL.md` file is `SKILL_DIR`. All output goes under `SKILL_DIR/assets/theme/`.

Output files use the source domain or project name as a prefix:

```
SKILL_DIR/assets/theme/
├── {name}-style-manifest.json    # Structured style manifest
└── {name}-style-specimen.html    # Universal style specimen HTML
```

Examples (where `SKILL_DIR` is whatever path the Glob resolved):
- `{SKILL_DIR}/assets/theme/ampcode-style-manifest.json`
- `{SKILL_DIR}/assets/theme/ampcode-style-specimen.html`
- `{SKILL_DIR}/assets/theme/vercel-style-manifest.json`
- `{SKILL_DIR}/assets/theme/vercel-style-specimen.html`

Create the `assets/theme/` directory if it does not exist before writing.

---

## Reference Files

The `references/` directory inside this skill contains two files you MUST use during every extraction. Both paths are relative to `SKILL_DIR` (resolved via Glob above):

- `{SKILL_DIR}/references/extraction-checklist.md` — comprehensive checklist for all extraction dimensions. Work through every section; note why if a dimension is not applicable.
- `{SKILL_DIR}/references/style-specimen.html` — structural template for Output C. Your generated specimen must follow the same structure.

**WARNING**: The template contains `/* REPLACE */` placeholders for every CSS token value. You MUST replace ALL of them with values measured from the target site. Do NOT keep any placeholder value in the final output. A `/* REPLACE */` in the output file means the extraction is incomplete.

---

## When to use

Use this skill when the user wants to:

- 提取某个网页的视觉风格
- 让 AI 学习一个网站的设计语言并生成同风格页面
- 从网页中抽取字体、字号、字色、背景样式、图片背景、条纹/网格/纹理、动画、卡片样式、代码块样式
- 将网页风格沉淀为一个可复用的 HTML 参考文件
- 构建设计样张页 / style specimen / design reference file
- 将一个具体网页抽象成更通用的设计系统表达
- 抽取整页“氛围感 / atmosphere / art direction”，而不仅是组件样式

Do **not** use this skill if the user wants:

- 仅截图网页
- 仅复制页面 DOM 或下载页面资源
- 仅修复某个单独 CSS 问题
- 仅做像素级 1:1 复刻
- 仅导出 raw CSS dump

This skill is for **style system extraction**, not page cloning.

---

## Core principle

Your task is **not** to reproduce the page structure.

Your task is to extract the page's **visual system** and represent it as:

1. **Primitive tokens**
2. **Semantic tokens**
3. **Background / atmosphere system**
4. **Decorative motif system**
5. **Component archetypes**
6. **Interaction rules**
7. **A universal style specimen HTML**

The final result must be a **general-purpose reference file** that another AI can read and use to generate new pages in the same style.

Think in terms of:

- design tokens
- semantic roles
- theme layers
- background atmosphere
- decorative motifs
- component patterns
- state behavior
- motion language
- responsive rules
- art direction

Do **not** think in terms of:

- copying all classes
- mirroring page DOM
- dumping raw CSS blindly
- preserving irrelevant content text
- flattening atmospheric styling into a single background color

The goal is:

**Preserve not only the component language, but also the page atmosphere, decorative motifs, and art direction. A faithful extraction must capture both system structure and visual mood.**

---

## Output contract

When using this skill, produce **three outputs**:

### Output A — Extraction summary
A concise explanation of the extracted style system:

- overall design character
- typography system
- color system
- spacing/layout rhythm
- surface/elevation language
- background / atmosphere language
- decorative motifs
- motion language
- component family
- theme/responsive behavior
- extraction confidence
- limitations

### Output B — Structured style manifest
A required machine-readable JSON file saved to `{SKILL_DIR}/assets/theme/{name}-style-manifest.json`, describing:

- meta
- primitives
- semantic tokens
- background system
- motifs
- themes
- motion tokens
- component archetypes
- responsive rules
- accessibility notes
- limitations

### Output C — Universal style specimen HTML
A single HTML file containing:

- CSS tokens
- theme layers
- background/atmosphere layers
- motif samples
- component styles
- specimen sections
- a design manifest in `<script type="application/json">`
- optional minimal demo scripts for theme switching / state preview

This HTML file should be general and reusable.

---

## Required extraction dimensions

You must extract the following categories.

### 1. Meta context
Capture:

- source URL if available
- page title
- capture time/context
- viewport size
- whether dark mode exists
- whether reduced motion behavior exists
- whether the page uses heavy canvas/WebGL/video-only visuals
- whether shadow DOM/custom elements are present
- whether the extraction is from live render or static code

### 2. Typography
Extract:

- primary font family
- fallback stack
- mono/code font family
- font weights
- size scale
- line heights
- letter spacing
- paragraph rhythm
- link styles
- prose/body styles
- heading hierarchy
- button/label/input text styles

Do not only report raw values. Abstract them into roles such as:

- `--font-family-sans`
- `--font-family-mono`
- `--font-size-body`
- `--font-size-heading-lg`
- `--line-height-body`
- `--font-weight-semibold`

### 3. Color system
Extract:

- page background
- surface/background layers
- card backgrounds
- overlay/scrim
- primary text
- secondary text
- inverse text
- muted text
- borders/dividers
- brand/accent colors
- interactive colors
- success/warning/error/info
- code block background and syntax colors
- gradients
- translucent layers
- blur/frosted surface styles

Abstract colors into semantic roles, not just raw hex values.

Examples:

- `--color-bg-page`
- `--color-surface-card`
- `--color-text-primary`
- `--color-text-secondary`
- `--color-border-default`
- `--color-brand-primary`
- `--color-code-bg`

### 4. Spacing and layout
Extract:

- container widths
- grid behavior
- gutter
- section spacing
- component padding
- gap rhythm
- common stack spacing
- alignment preferences
- desktop/tablet/mobile changes

Abstract into spacing and layout tokens.

### 5. Surface / shape / elevation
Extract:

- border radius scale
- border treatments
- shadow scale
- backdrop blur
- surface layering
- z-index/elevation feel
- outline/focus ring style

Examples:

- `--radius-sm`
- `--radius-card`
- `--shadow-sm`
- `--shadow-elevated`
- `--focus-ring`

### 6. Motion / Animation
Extract motion and animation tokens:

**Transitions** (via computed styles):
- transition durations
- easing curves
- delays
- common hover motion
- transform language
- opacity motion

**@keyframes animations** (require direct stylesheet parsing):
- Each `@keyframes` rule must be captured separately — `extract-styles.py` does NOT capture these
- For each keyframe, record: name, semantic description, from/to/keyframe percentages, usage context

**How to extract @keyframes** — run `{SKILL_DIR}/scripts/extract-keyframes.py` or this browser console snippet:

```javascript
const keyframes = [];
for (const sheet of document.styleSheets) {
  try {
    for (const rule of sheet.cssRules) {
      if (rule.type === CSSRule.KEYFRAMES_RULE) {
        keyframes.push({ name: rule.name, cssText: rule.cssText });
      }
    }
  } catch(e) { /* CORS restriction, skip */ }
}
console.log(JSON.stringify(keyframes, null, 2));
```

Abstract into motion tokens:
- `--motion-duration-fast`, `--motion-duration-normal`
- `--motion-ease-standard`, `--motion-ease-emphasized`

Animation archetypes to look for:
- Modal/drawer: scaleIn, scaleOut, enterFromRight/Left
- Accordion: accordion-down/up
- Pattern: slidePattern (background pattern drift)
- Loading: spin, pulse, shimmer, progress-slide
- Reveal: fadeIn, slideUp, enter
- Hover: subtle scale, lift, glow

### 7. Component archetypes
Extract reusable component families rather than page-specific instances.

At minimum inspect:

- page/container sections
- nav/header/footer
- buttons
- links
- cards
- badges/tags/chips
- inputs/textareas/selects
- switches/checkboxes/radios
- tabs/accordions
- tables
- alerts/callouts
- modals/drawers/popovers/tooltips
- lists/media rows
- empty states
- stat cards
- code blocks
- inline code
- toasts/skeletons if present

For each component archetype record:

- structure/slots
- visual DNA
- spacing
- radius
- border/shadow
- default state
- hover
- focus-visible
- active
- selected
- disabled
- loading
- theme variants
- compact/comfortable variants if visible

### 8. Code block system
This is mandatory if code blocks exist or may matter later.

Extract:

- code font
- code size
- line height
- block background
- border/radius
- padding
- title bar / filename strip
- line-number style
- inline code style
- syntax color family
- copy button / toolbar style
- highlighted line style

### 9. Responsive and theme rules
Capture:

- breakpoints
- type scaling across breakpoints
- spacing changes across breakpoints
- layout collapse/stack behavior
- theme variants
- dark mode
- reduced motion handling
- print behavior if visible or inferable

### 10. Atmosphere / Background System
Extract the page-level and section-level visual atmosphere, not only flat background colors.

You must inspect and abstract:

- page background color
- section background color
- hero background treatments
- gradients (linear / radial / conic)
- repeating patterns (stripes / grid / dots / lines / checker / mesh)
- image-based backgrounds
- SVG decorative backgrounds
- noise / grain / texture overlays
- glow / blur / vignette / spotlight effects
- background blend / mask / filter usage
- pseudo-element decorative layers (`::before`, `::after`)
- absolutely positioned decorative elements
- floating blobs / glow shapes / ambient lights
- background repeat / size / position / attachment
- section separators / dividers that contribute to overall mood
- whether the site atmosphere is flat / textured / editorial / futuristic / industrial / terminal-like / soft / playful

Do not flatten atmospheric styling into a single `background-color`.
Always model it as a distinct system.

Examples of useful semantic outputs:

- `--bg-page-base`
- `--bg-page-overlay`
- `--bg-page-pattern`
- `--bg-hero-gradient`
- `--bg-section-muted`
- `--pattern-stripe-color`
- `--pattern-grid-color`
- `--texture-noise-opacity`
- `--ambient-glow-primary`
- `--ambient-glow-blur`
- `--decorative-line-opacity`

### 11. Decorative Motif System
Extract repeated visual motifs that may appear in only a few places but clearly shape the site’s identity.

You must inspect and abstract:

- diagonal stripes
- grids
- dotted fields
- editorial rules/lines
- terminal scan lines
- waveform / chart-like lines
- geometric accents
- glow shapes
- border corner treatments
- repeated iconography
- signature hover textures
- signature pattern movement
- recurring mask or clipping styles
- recurring pseudo-element decorations

A motif may originate in one component but still represent page-level visual DNA.
Elevate it when appropriate.

Useful outputs include:

- `motifs.diagonal-stripe`
- `motifs.gridline`
- `motifs.editorial-rule`
- `motifs.noise-overlay`
- `motifs.ambient-glow`
- `motifs.scanline`

---

## Extraction method

### Rule 1: Prefer rendered reality over source intent
Use the final rendered/computed result as the ground truth.

Prioritize:

- actual visible DOM
- computed styles
- pseudo elements
- measured layout
- live states
- effective animations

Do not rely solely on authored CSS.

**Mandatory computed style checks** — before recording any token value, use browser tools to read the actual computed value. Do not infer from class names, design system conventions, or framework patterns. Specifically:

- Read `document.documentElement.getAttribute('data-theme')` to confirm the **actual default theme** on page load. Never assume dark-first or light-first from visual appearance alone.
- Read CSS custom properties via `getComputedStyle(document.documentElement).getPropertyValue('--var-name')` to get exact values.
- Read computed colors via `getComputedStyle(el).backgroundColor`, `.color`, `.borderColor` etc. — not from class names.
- Read computed transitions via `getComputedStyle(el).transition` to get the actual easing curve, not a generic approximation.
- Read `background-image` on all elements to detect patterns, gradients, and motifs.

If a value **cannot** be read via computed style (e.g. cross-origin stylesheet blocked, canvas-only visuals), you **must** label it as `"inferred"` in the manifest's `limitations` field. Do not silently use an approximated value as if it were measured.

### Rule 2: Cluster before naming
Do not emit a token for every distinct observed value.

Instead:

1. collect raw values
2. group near-equivalent visual values
3. infer the system
4. assign semantic names

Example:

Bad:
- `--blue-1`
- `--blue-2`
- `--blue-3`
- `--text-gray-7`

Better:
- `--color-brand-primary`
- `--color-link-default`
- `--color-link-hover`
- `--color-text-secondary`

### Rule 3: Extract semantic roles, not only raw values
A useful reference file must explain **what a value does**, not only **what the value is**.

Always try to map raw observations into roles.

### Rule 4: Extract states actively
Do not assume the static DOM shows all relevant UI states.

For **every component archetype** in the manifest, you must record all of the following states:

- default
- hover
- focus-visible
- active
- selected
- disabled
- loading

If a state cannot be reliably observed, you **must** explicitly record it as `"inferred"` or `"unavailable"` — do not omit it silently. A missing state entry is not the same as an unavailable state.

### Rule 5: Build archetypes, not clones
If you see 11 cards, do not export 11 card classes unless they are meaningfully distinct.

Instead compress them into a small set of archetypes, for example:

- card/plain
- card/bordered
- card/elevated
- card/interactive
- card/stat

### Rule 6: Separate content from style
The specimen file should use neutral placeholder content.

Do not preserve source page copy unless the user explicitly asks.

### Rule 7: Report uncertainty honestly
If some styles are not reliably extractable, say so.

**Never emit an empty object or empty array** for a field you could not extract. Instead:
- If the value is genuinely absent from the design (e.g. no shadows used), set the field to `null` and add a note to `limitations`.
- If the value exists but could not be measured, set it to `"inferred: <reason>"` or add it to `limitations`.

Bad:
```json
"shadow": {}
"surfaces": {}
```

Good:
```json
"shadow": null,
"limitations": ["Shadow styles not observed — site appears to use no box-shadow"]
```

Typical limitations include:

- cross-origin stylesheet access issues
- canvas/WebGL-only visuals
- video-only backgrounds
- runtime-only transitions not visible in current state
- visited-link privacy behavior
- hard-to-observe interaction states

### Rule 8: Extract atmosphere separately from components
A page may feel distinctive because of background treatment, not because of buttons or cards.

Always inspect atmosphere at 4 levels: page-level (`html`/`body`/main wrappers), section-level (hero, feature, CTA), decorative-layer (pseudo-elements, absolutely positioned ornaments, SVG art-direction layers), and motif system (stripes, grids, scan lines, grain, glows, repeated patterns).

When inspecting, always check: `background`, `background-image`, `background-size/repeat/position/attachment`, `mask`, `mask-image`, `filter`, `backdrop-filter`, `opacity`, `mix-blend-mode`, `isolation`, decorative SVGs, data URI / base64 backgrounds, and pseudo-element paint layers.

If an atmospheric pattern appears only in one component but clearly represents the site's broader visual language, elevate it into a motif token rather than leaving it inside that component.

### Rule 9: Capture mood, not only implementation

In addition to CSS facts, summarize the visual mood in plain language.

Examples:

- warm editorial minimalism
- futuristic terminal-industrial
- crisp enterprise dashboard
- soft gradient SaaS marketing
- playful geometric education product
- brutalist poster-like system

This mood description should align with the extracted tokens and motifs.

---

## Browser tool

Do **not** attempt to extract styles by reading static HTML source or stylesheet files alone — computed styles, CSS variable resolution, and theme state require a live browser context.

This skill ships a self-contained Python/Playwright script. Before running it, resolve `SKILL_DIR` using the Glob pattern `**/skills/extract-design/SKILL.md` (as described in **Output Location** above), then substitute it into the path below.

**Setup (one-time):**

```bash
pip install playwright
playwright install chromium
```

**Usage:**

```bash
# Light mode only
python3 {SKILL_DIR}/scripts/extract-styles.py https://example.com

# Light + dark mode
python3 {SKILL_DIR}/scripts/extract-styles.py https://example.com --dark

# Save to file
python3 {SKILL_DIR}/scripts/extract-styles.py https://example.com --dark --out /tmp/styles.json
```

**For @keyframes extraction** (required for animation system):

```bash
python3 {SKILL_DIR}/scripts/extract-keyframes.py https://example.com --out /tmp/keyframes.json
```

The script outputs structured JSON with `light` and `dark` keys, each containing:
- `cssVars` — all CSS custom properties (`--*`) from stylesheets
- `colors` — computed `backgroundColor`, `color` on `html`/`body`/card elements
- `fonts` — computed `fontFamily`, `fontSize`, `fontWeight` on body, h1, h2
- `button` — computed styles on the first `<button>`
- `backgroundImages` — all elements with `background-image !== none` (patterns, gradients)
- `accentColors` — computed colors on links and accent/brand-classed elements
- `typography` — h1 size, weight, letter-spacing, line-height, color

---

## Recommended extraction workflow

**Before starting**: Open `{SKILL_DIR}/references/extraction-checklist.md` and keep it open throughout. Check off each item as you complete it. Use `{SKILL_DIR}/references/style-specimen.html` as your structural template when building Output C.

### Step 1 — Characterize the page
Summarize:

- minimal / editorial / dashboard / marketing / docs / product / playful / brutalist / glassmorphism / etc.
- density
- contrast
- tone
- motion intensity
- component complexity
- atmospheric character
- recurring motifs

### Step 2 — Gather raw observations
Collect all observed values by **reading computed styles directly**, not by inferring from class names or source code.

Required checks (run these before proceeding to Step 3):

1. **Default theme**: `document.documentElement.getAttribute('data-theme')` — record the actual value on page load
2. **Body background**: `getComputedStyle(document.body).backgroundColor`
3. **Body color**: `getComputedStyle(document.body).color`
4. **Font family**: `getComputedStyle(document.body).fontFamily`
5. **CSS custom properties**: iterate `document.styleSheets` to extract all `--` variables with their actual values
6. **Accent/brand colors**: query key elements (links, buttons, badges) and read `.color` and `.backgroundColor`
7. **Background patterns**: query all elements for `backgroundImage !== 'none'` — record the full value including gradient stops and `background-size`
8. **Transitions**: read `getComputedStyle(el).transition` on buttons and interactive elements — record the exact easing function
9. **Card/surface styles**: read `backgroundColor`, `borderColor`, `borderRadius`, `boxShadow` on card elements
10. **Dark mode**: if a theme toggle exists, activate dark mode and re-read the above values
11. **@keyframes**: extract all `@keyframes` rules from stylesheets (see section 6b for method)

Record raw values first. Do not skip to naming or abstracting until all raw values are collected.

### Step 3 — Normalize into primitives
Reduce noise and create primitive tokens.

### Step 4 — Map to semantic tokens
Assign role-based names.

### Step 5 — Build background and motif systems
Identify:

- page base layers
- section atmosphere variants
- decorative overlays
- signature motifs/patterns
- hero atmosphere composition

### Step 6 — Build component archetypes
Identify reusable component families.

### Step 7 — Derive interaction rules and extract @keyframes
Summarize state transitions and motion behavior. If the site uses @keyframes (backgrounds, modals, loading states, hover effects):

1. Run `{SKILL_DIR}/scripts/extract-keyframes.py` or extract via browser console
2. For each keyframe, abstract into semantic description
3. Map to component archetypes where used
4. Add to manifest's `motion.keyframes` array
5. Add animation demo section to specimen HTML

### Step 8 — Build the specimen HTML
Create a general-purpose design reference page following the structure in `{SKILL_DIR}/references/style-specimen.html`. Save to `{SKILL_DIR}/assets/theme/{name}-style-specimen.html`.

The template uses `/* REPLACE */` as placeholders for every CSS token value. You must replace every single one with a value measured from the target site. Search the output file for `/* REPLACE */` before saving — if any remain, the step is not complete. Add or remove motif cards and background sample cards to match what was actually found.

### Step 9 — Validate usefulness
Ask:
- Could another AI use this to generate a new page in the same style?
- Does it capture the system rather than only one page?
- Does it include tokens, themes, components, states, motion, and code blocks?
- Does it include atmosphere, motifs, and animations (@keyframes)?
- Does the specimen HTML include an Animation System demo section if the site has @keyframes?

If not, revise.

### Step 10 — Sync manifest and specimen
Before saving, verify that the manifest and specimen HTML are consistent:

- Every component archetype in `manifest.components` must have a corresponding rendered section in the specimen HTML.
- Every component section in the specimen HTML must have a corresponding archetype in `manifest.components`.
- No field in the manifest should be an empty object `{}` or empty array `[]` — use `null` with a limitations note instead.

If they are out of sync, fix both files before finishing.

---

## Required style manifest schema

The structured manifest should generally follow this shape:

```json
{
  "meta": {},
  "style_character": {},
  "primitives": {},
  "semantic": {},
  "background": {
    "page": {},
    "sections": [],
    "layers": [],
    "gradients": [],
    "patterns": [],
    "images": [],
    "overlays": []
  },
  "motifs": [],
  "themes": {},
  "motion": {
    "duration": {},
    "easing": {},
    "keyframes": [
      {
        "name": "animationName",
        "description": "What the animation does",
        "from": "opacity: 0; transform: scale(0.95)",
        "to": "opacity: 1; transform: scale(1)"
      }
    ]
  },
  "components": [],
  "responsive_rules": [],
  "accessibility_notes": [],
  "limitations": []
}
```

**Note**: If no @keyframes were found on the site, set `motion.keyframes` to `null` with a note in `limitations`.