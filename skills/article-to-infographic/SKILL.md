---
name: article-to-infographic
description: Transform articles, blog posts, reports, or any text content into visually stunning, self-contained HTML infographics. Use when the user wants to convert text into an infographic, create a visual summary of an article, make a data visualization from written content, or generate an infographic from a URL, file, or pasted text. Supports multiple infographic styles (timeline, statistics, comparison, process flow, listicle) with distinctive, non-generic aesthetics.
---

# Article to Infographic

Transform any article or text content into a visually compelling, self-contained HTML infographic. Output is a single HTML file with inline CSS/JS -- zero dependencies, opens in any browser, print-ready for PDF export.

## Core Philosophy

1. **Content-First** -- Analyze the article before choosing layout.
2. **Smart Layout** -- Match infographic type to content type automatically.
3. **Distinctive Design** -- No generic AI aesthetics. Every infographic feels custom-crafted.
4. **Zero Dependencies** -- Single HTML file with inline CSS/JS.
5. **Print-Ready** -- Include print media queries for clean PDF export.

---

## Workflow Overview

**Strict 3-Step Confirmation Process:**

```
Step 1: Outline Confirmation (BLOCKING)
   ↓ User must confirm
Step 2a: Layout Selection (BLOCKING)
   ↓ User must confirm
Step 2b: Style Selection (BLOCKING)
   ↓ User must confirm
Step 2c: Illustrations (BLOCKING)
   ↓ User must confirm
Step 3: Output Format (BLOCKING)
   ↓ User must confirm
Generation Phase (automatic)
```

**CRITICAL RULE**: Each step requires explicit user confirmation before proceeding. Do NOT batch confirmations. Do NOT proceed to next step until current step is confirmed.

---

## Detailed Workflow

1. Acquire and analyze article content
2. Extract key information and classify content type
3. **Step 1: Present outline → Get explicit confirmation**
4. **Step 2a: Present layout options → Get explicit confirmation**
5. **Step 2b: Present style options → Get explicit confirmation**
6. **Step 2c: Present illustration options → Get explicit confirmation**
7. **Step 3: Present output format options → Get explicit confirmation**
8. Generate the HTML infographic (only after all confirmations)
9. Export to PNG if selected in Step 3
10. Deliver the final output

## Confirmation Flow Summary (For AI Reference)

When executing this skill, follow this EXACT sequence:

| Phase | Step | Action | User Confirmation Required |
|-------|------|--------|---------------------------|
| 1 | Content Acquisition | Get article URL/file/text | ❌ No |
| 2 | Content Analysis | Extract info, classify type | ❌ No |
| 2.5 | **Step 1** | Present outline table | ✅ **MUST CONFIRM** |
| 3a | **Step 2a** | Present layout options | ✅ **MUST CONFIRM** |
| 3b | **Step 2b** | Present style options | ✅ **MUST CONFIRM** |
| 3c | **Step 2c** | Present illustration options | ✅ **MUST CONFIRM** |
| 4 | **Step 3** | Present output format options | ✅ **MUST CONFIRM** |
| 5 | Generation | Create HTML | ❌ Automatic |
| 6 | Delivery | Present results | ❌ Automatic |
| 7 | PNG Export | If selected in Step 3 | ❌ Automatic |

**FORBIDDEN ACTIONS:**
- ❌ Never combine Step 1 + Step 2 confirmations
- ❌ Never combine Step 2a + 2b + 2c into one question
- ❌ Never combine Step 2 + Step 3 confirmations
- ❌ Never proceed to generation without all 3 steps confirmed

---

## Phase 1: Content Acquisition

Determine the content source:

- **URL** -- Use WebFetch to retrieve article content
- **File** -- Read the file directly
- **Pasted text** -- Use as-is

If content is ambiguous or too short, ask for clarification.

---

## Phase 2: Content Analysis

Extract from the article:

1. **Title and subtitle** -- Main topic and secondary context
2. **Key statistics** -- Numbers, percentages, data points
3. **Key points** -- 4-8 most important takeaways
4. **Quotes** -- Notable statements
5. **Comparisons** -- Before/after, pros/cons, A vs B
6. **Sequential steps** -- Process flows, timelines, chronological events
7. **Categories** -- Natural groupings
8. **Entities** -- People, organizations, places

Classify the best infographic type:

| Content Signal | Infographic Type |
|---|---|
| Dates, milestones, chronological events | **Timeline** |
| Numbers, percentages, survey data | **Statistics Dashboard** |
| A vs B, pros/cons, before/after | **Comparison** |
| Step-by-step, how-to, tutorial | **Process Flow** |
| Multiple independent tips/facts | **Listicle / Card Grid** |
| Mixed content types | **Magazine / Editorial** |

---

## Phase 2.5: Step 1 - Outline Confirmation (BLOCKING)

**⚠️ CRITICAL: Must get explicit user confirmation before proceeding to Phase 3.**

After content analysis, present the user with a structured outline in table form:

```
| Block | Content | Notes |
|---|---|---|
| Header | Title + subtitle | Top section |
| Hero Stats (3) | [stat1] / [stat2] / [stat3] | Key data highlights |
| ... | ... | ... |
```

**DO NOT proceed until user explicitly confirms.**

Using AskUserQuestion:
- Header: "Step 1/3: Outline Confirmation"
- Question: "Please review the outline above with [N] blocks. Confirm to proceed or request changes:"
- Options:
  - "✅ Outline confirmed - proceed to style selection" -- ONLY THEN go to Phase 3
  - "📝 Need adjustments" -- User specifies changes (add/remove/modify blocks), then RE-CONFIRM
  - "🔄 Simplify to core blocks" -- Auto-trim to core blocks only, then RE-CONFIRM

**Hard rule**: If user chooses adjustments, update the outline and return to this same confirmation step. Do NOT proceed to Phase 3 until "✅ Outline confirmed" is selected.

---

## Phase 3: Step 2 - Style Selection (BLOCKING)

**⚠️ CRITICAL: Must get explicit user confirmation for BOTH layout AND style before proceeding to Phase 4.**

This phase requires **TWO separate confirmations**:

### Step 2a: Layout Selection (BLOCKING)

Using AskUserQuestion:
- Header: "Step 2a/3: Layout Selection"
- Question: "Based on your article, I recommend a **[detected type]** layout. Confirm your choice:"
- Options: 
  - "✅ [detected type] - recommended" 
  - "📊 Statistics Dashboard"
  - "📅 Timeline"
  - "⚖️ Comparison"
  - "🔄 Process Flow"
  - "📝 Listicle / Card Grid"
  - "📖 Magazine / Editorial"

**STOP HERE**. Wait for user selection. Do NOT show style options yet.

### Step 2b: Style Selection (BLOCKING)

ONLY after layout is confirmed, present style options:

Using AskUserQuestion:
- Header: "Step 2b/3: Visual Style Selection"
- Question: "What visual style for the **[confirmed layout]** infographic?"
- Options (show 4-5 most relevant):

  **Standard Styles:**
  - "🎨 Bold & Vibrant" -- High contrast, saturated colors, strong visual impact
  - "🌿 Clean & Minimal" -- Whitespace, subtle colors, elegant typography
  - "🌃 Dark & Techy" -- Dark backgrounds, neon accents, modern feel
  - "📰 Warm & Editorial" -- Magazine-style, warm tones, serif typography

  **Premium Styles:**
  - "🚀 Sci-fi HUD" -- Cyberpunk terminal, particle network, neon glow
  - "💎 Premium Magazine" -- Luxury editorial, massive serif typography
  - "🔮 Glassmorphism Aurora" -- Frosted glass, animated aurora blobs

**STOP HERE**. Wait for user selection.

### Step 2c: Illustrations (optional, but ASK)

Using AskUserQuestion:
- Header: "Step 2c/3: Illustrations (Optional)"
- Question: "Add illustrations to the **[confirmed style]** infographic?"
- Options:
  - "🚫 No illustrations - text and data only" 
  - "🔹 Decorative icons - small SVG icons next to headings"
  - "👤 Character illustrations - full SVG characters from open-source libraries"

**ONLY after all 2a→2b→2c are confirmed, proceed to Phase 4.**

For detailed color palettes and font pairings per style, see [references/style-presets.md](references/style-presets.md).

---

## Phase 4: Step 3 - Output Format Confirmation (BLOCKING)

**⚠️ CRITICAL: Must get explicit user confirmation for output format BEFORE generating anything.**

Using AskUserQuestion:
- Header: "Step 3/3: Output Format"
- Question: "How would you like to receive the **[confirmed style]** infographic?"
- Options:
  - "📄 HTML only - single file, opens in browser" 
  - "🖼️ HTML + PNG - include high-res image export"
  - "📦 Both formats - explicit delivery of both files"

**ONLY after output format is confirmed, proceed to Phase 5 (Generation).**

---

## Phase 5: Generate Infographic

### HTML Architecture

Single self-contained HTML file:

```html
<!DOCTYPE html>
<html lang="[content language]">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Infographic Title]</title>
    <link rel="stylesheet" href="[Google Fonts / Fontshare URL]">
    <style>
        :root {
            --bg-primary: ...; --bg-secondary: ...;
            --text-primary: ...; --text-secondary: ...;
            --accent-1: ...; --accent-2: ...;
            --font-display: ...; --font-body: ...;
        }
        /* Layout, components, animations */
        @media print { /* linearize, remove animations */ }
        @media (prefers-reduced-motion: reduce) { /* disable animations */ }
    </style>
</head>
<body>
    <article class="infographic">
        <header class="infographic-header">...</header>
        <main class="infographic-body">...</main>
        <footer class="infographic-footer">...</footer>
    </article>
    <script>/* Intersection Observer animations, counter effects */</script>
</body>
</html>
```

### Design Rules

**Typography:**
- Distinctive Google Fonts or Fontshare fonts -- NEVER Inter, Roboto, Arial, or system fonts
- Display font for headings, clean font for body
- Responsive sizing with `clamp()`

**Color:**
- CSS custom properties for entire palette
- Max 3-4 colors: one dominant, one accent, one-two neutrals
- WCAG AA contrast for readability

**Layout:**
- CSS Grid for overall structure, Flexbox for components
- Max-width 1200px, centered
- **Compact spacing**: Use `2-3rem` between sections, NOT 5rem+. Infographics should feel dense and information-rich, not stretched out. Header padding: 2-2.5rem. Section padding: 2-3rem. Grid gaps: 2-2.5rem.
- Responsive: stack on mobile, multi-column on desktop

**Data Visualization:**
- Pure CSS for simple charts (bar via width%, pie via conic-gradient)
- Inline SVG for complex shapes
- Animate numbers with counter effect (Intersection Observer)
- Always label data clearly

**Animations:**
- Intersection Observer triggers `.visible` class
- Stagger children with animation-delay
- Subtle fade + translateY baseline
- `prefers-reduced-motion` media query required

**Print:**
- `@media print` rules: linearize layout, remove animations, ensure readability
- Appropriate page breaks between sections

### Layout Patterns

**Timeline:**
- Vertical center line, alternating left/right entries
- Date badges on line, content cards offset
- Mobile: single-column stack

**Statistics Dashboard:**
- Hero stat at top (large number + context)
- Grid of stat cards (2-3 columns)
- CSS bar/pie charts where appropriate
- Counter animation on scroll

**Comparison:**
- Side-by-side columns with central divider
- Matching rows, color-coded sides
- Mobile: vertical stack with labels

**Process Flow:**
- Numbered steps with connecting lines/arrows
- Icon + title + description per step
- Progress indicator

**Listicle / Card Grid:**
- Numbered/icon cards in responsive grid (2-3 cols desktop, 1 mobile)
- Each card: icon/number + title + description
- Hover effects

**Magazine / Editorial:**
- Mix of full-width, card grids, pull quotes, stat highlights
- Alternate dense and spacious sections
- Strong typographic hierarchy

### Anti-Patterns -- NEVER

- Purple gradient on white background
- Generic card layouts with no visual character
- Font Awesome or emoji spam as decoration
- Flat, lifeless color schemes
- Walls of small text (defeats infographic purpose)
- Charts without labels
- Cookie-cutter layouts

---

## Phase 6: Delivery

**All 3 confirmation steps completed. Generating final output...**

Write the HTML file and present a summary:

```
✅ Infographic generated!

📄 File: [filename].html
📐 Layout: [confirmed layout]
🎨 Style: [confirmed style]
🖼️ Illustrations: [confirmed option]
📦 Output: [confirmed format]
📊 Sections: [count]

Open in browser to view. Ctrl+P / Cmd+P to save as PDF.
```

**Generation is complete. No further confirmations needed.**

---

## Edge Cases

**Short articles (< 200 words):** Compact single-section, 3-5 key points as cards.

**Long articles (> 3000 words):** Summarize to 6-10 key sections max. Prioritize data and takeaways.

**No statistics:** Focus on quotes, process flows, or listicle. Use icons instead of charts.

**Technical/code-heavy:** Code snippet sections, architecture diagrams with CSS shapes, conceptual flow.

**Non-English content:** Set `lang` attribute correctly on `<html>`. Use appropriate fonts for CJK, RTL, etc.

---

## Phase 7: PNG Export (if selected in Step 3)

After generating the HTML, if PNG was selected in Step 3, proceed with export:

### Method A: Browser tool (preferred in Claude Code / HappyCapy)

If a `browser` CLI tool is available:

1. Start a local HTTP server serving the HTML file
2. Navigate browser to the page
3. Force all `.reveal` elements to visible state (skip scroll animations)
4. Force all bar fills and counters to final values
5. Take a full-page screenshot
6. Close browser

```javascript
// JS to inject before screenshot:
document.querySelectorAll('.reveal').forEach(el => {
    el.classList.add('visible');
    el.style.opacity = '1';
    el.style.transform = 'none';
});
document.querySelectorAll('.ba-fill, .bar-fill').forEach(bar => {
    const w = bar.dataset.width;
    if (w) bar.style.width = w + '%';
});
document.querySelectorAll('[data-counter]').forEach(el => {
    const target = el.dataset.counter;
    const suffix = el.dataset.suffix || '';
    el.textContent = parseInt(target).toLocaleString() + suffix;
});
```

### Method B: Playwright script (standalone environments)

Run the bundled script:

```bash
python3 scripts/html_to_png.py infographic.html output.png --width 1200 --scale 2
```

The script uses headless Chromium via Playwright. It auto-installs dependencies if needed.

Arguments:
- `--width` : viewport width in px (default 1200)
- `--scale` : HiDPI scale factor (default 2, produces 2400px wide image)

### When to export PNG

Ask the user after HTML delivery:

- Header: "Export"
- Question: "Want a PNG image export as well?"
- Options:
  - "Yes, export PNG" -- Run export
  - "HTML only is fine" -- Skip

---

## OpenClaw / Non-Interactive Adaptation

When deploying to environments without interactive question-answer support (e.g., OpenClaw, API-only setups), the skill operates in **parameterized mode** where ALL options must be specified upfront.

**⚠️ CRITICAL**: In parameterized mode, you MUST provide ALL confirmations in a single prompt because the system cannot ask follow-up questions.

### Parameterized Invocation (Single Prompt)

Users must specify ALL 3 confirmation steps in one prompt:

```
Generate an infographic from [article source].

STEP 1 - OUTLINE:
[Provide your preferred outline structure, or "use auto-generated outline"]

STEP 2 - STYLE:
Layout: [timeline|statistics|comparison|process|listicle|magazine]
Style: [bold-vibrant|clean-minimal|dark-techy|warm-editorial|scifi-hud|premium-magazine|glassmorphism]
Illustrations: [none|icons|characters]

STEP 3 - OUTPUT:
Format: [html|png|both]
```

**Example complete prompt:**
```
Generate an infographic from https://example.com/article.

STEP 1: Use auto-generated outline

STEP 2: 
Layout: timeline
Style: dark-techy
Illustrations: icons

STEP 3:
Format: both
```

### Parameter Reference

**Style options:**
- `bold-vibrant` -- High contrast, saturated colors
- `clean-minimal` -- Whitespace, subtle colors, serif typography
- `dark-techy` -- Dark background, neon accents
- `warm-editorial` -- Magazine-style, warm tones
- `scifi-hud` -- Cyberpunk terminal, particle network, neon glow (premium)
- `premium-magazine` -- Luxury editorial, massive serif, cream/charcoal/vermillion (premium)
- `glassmorphism` -- Frosted glass, aurora blobs, Apple-inspired depth (premium)

**Layout options:**
- `timeline` -- Chronological events
- `statistics` -- Data dashboard
- `comparison` -- Side-by-side
- `process` -- Step-by-step flow
- `listicle` -- Card grid
- `magazine` -- Mixed editorial (default for complex articles)
- `auto` -- Let the skill decide based on content analysis

**Outline adjustments** (natural language):
- "remove [block name]"
- "add [block description]"
- "replace [block] with [new content]"
- "simplify" / "expand"

**Export options:**
- `html` -- HTML only (default)
- `png` -- HTML + PNG export
- `both` -- Explicitly output both

### Fallback Behavior

If no style/layout is specified and AskUserQuestion is not available, use these defaults:
- **Layout**: `auto` (detect from content)
- **Style**: `dark-techy` for technical content, `warm-editorial` for narrative content, `bold-vibrant` for data-heavy content
- **Export**: `html` only

### Font CDN for China Deployment

When deployed behind the GFW, replace Google Fonts CDN:

```html
<!-- Instead of: -->
<link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">

<!-- Use mirror: -->
<link href="https://fonts.loli.net/css2?family=..." rel="stylesheet">
<!-- Or use: -->
<link href="https://fonts.font.im/css2?family=..." rel="stylesheet">
```

Alternatively, for CJK-heavy content, use system fonts as fallback:

```css
--font-heading: 'Noto Serif SC', 'STSong', 'SimSun', serif;
--font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
```
