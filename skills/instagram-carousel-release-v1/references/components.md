# Component Library & Templates

This file contains all HTML/CSS component templates for the Instagram Carousel Generator. Use these exact templates when building slides — they ensure visual consistency, correct spacing, and proper adaptation to light/dark backgrounds.

## CRITICAL: Slide Container Template

Every single slide MUST use this exact wrapper structure. The `overflow:hidden` on the inner div is a hard safety net that prevents content from bleeding into the progress bar zone. Never remove it.

```html
<div class="slide" style="background:{SLIDE_BG};">
  <div style="position:absolute;top:28px;left:36px;right:36px;bottom:52px;min-height:0;display:flex;flex-direction:column;overflow:hidden;">
    <!-- ALL visible content goes here -->
  </div>
  <!-- Progress bar (position:absolute, sits outside the content flow) -->
  <!-- Swipe arrow (position:absolute, sits outside the content flow) -->
</div>
```

Key points:
- `bottom:52px` — creates a true no-content zone above the progress bar
- `min-height:0` + `overflow:hidden` — prevents flex children from pushing past the container and clips anything that still tries
- Progress bar and swipe arrow use `position:absolute` and live OUTSIDE the content div
- The content div uses `flex:1` to fill available space, and `flex-direction:column` for vertical stacking

Deprecated pattern:

```html
<div class="slide" style="background:{SLIDE_BG};">
  <div style="flex:1;display:flex;flex-direction:column;justify-content:flex-end;padding:0 36px 52px;">
```

Do not use this older wrapper without a true bottom inset. It is a common source of content slipping into the progress-bar zone.

## Palette Continuity Rules

Use these rules before choosing backgrounds:

- Keep one anchor hue family across the whole carousel
- Reuse one `LIGHT_BG`, one `DARK_BG`, and one softened gradient instead of inventing new backgrounds per slide
- Solve repetition with layout variation and contrast, not with unrelated colors
- Use gradients sparingly: usually one content slide plus the CTA
- If two adjacent slides feel too far apart, soften saturation before changing hue

## Table of Contents
0. [Slide Container Template](#critical-slide-container-template)
1. [Progress Bar & Swipe Arrow](#progress-bar--swipe-arrow)
2. [Stat Highlight Block](#stat-highlight-block)
3. [Case Study Block](#case-study-block)
4. [Entity / Company Card](#entity--company-card)
5. [Icon Bullet Point](#icon-bullet-point)
6. [Comparison Cards](#comparison-cards)
7. [Grid Layout 2x2](#grid-layout-2x2)
8. [Strikethrough Pills](#strikethrough-pills)
9. [Tag Pills](#tag-pills)
10. [Quote / Prompt Box](#quote--prompt-box)
11. [Feature List](#feature-list)
12. [Numbered Steps](#numbered-steps)
13. [Mini Data Visualizations](#mini-data-visualizations)
14. [Decorative Elements](#decorative-elements)
15. [Logo Lockup](#logo-lockup)
16. [CTA Button](#cta-button)
17. [Tag / Category Labels](#tag--category-labels)
18. [Recommended Sequences](#recommended-sequences)

---

## Progress Bar & Swipe Arrow

### Progress Bar (every slide, bottom)

```javascript
function progressBar(index, total, isLightSlide) {
  const pct = ((index + 1) / total) * 100;
  const trackColor = isLightSlide ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.12)';
  const fillColor = isLightSlide ? BRAND_PRIMARY : '#fff';
  const labelColor = isLightSlide ? 'rgba(0,0,0,0.3)' : 'rgba(255,255,255,0.4)';
  return `<div style="position:absolute;bottom:0;left:0;right:0;padding:16px 28px 20px;z-index:10;display:flex;align-items:center;gap:10px;">
    <div style="flex:1;height:3px;background:${trackColor};border-radius:2px;overflow:hidden;">
      <div style="height:100%;width:${pct}%;background:${fillColor};border-radius:2px;"></div>
    </div>
    <span style="font-size:11px;color:${labelColor};font-weight:500;">${index + 1}/${total}</span>
  </div>`;
}
```

### Swipe Arrow (every slide except last)

```javascript
function swipeArrow(isLightSlide) {
  const bg = isLightSlide ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.08)';
  const stroke = isLightSlide ? 'rgba(0,0,0,0.25)' : 'rgba(255,255,255,0.35)';
  return `<div style="position:absolute;right:0;top:0;bottom:0;width:48px;z-index:9;display:flex;align-items:center;justify-content:center;background:linear-gradient(to right,transparent,${bg});">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
      <path d="M9 6l6 6-6 6" stroke="${stroke}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>`;
}
```

## Safe Layout Shells

### Standard content shell

```html
<div class="slide" style="background:{SLIDE_BG};">
  <div style="position:absolute;top:28px;left:36px;right:36px;bottom:52px;min-height:0;display:flex;flex-direction:column;overflow:hidden;">
    <!-- regular content -->
  </div>
  {progressBar}
  {swipeArrow}
</div>
```

### Centered hero / CTA shell

```html
<div class="slide" style="background:{SLIDE_BG};">
  <div style="position:absolute;top:28px;left:36px;right:36px;bottom:52px;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;text-align:center;">
    <!-- centered content -->
  </div>
  {progressBar}
</div>
```

### Bottom-aligned dense shell

```html
<div class="slide" style="background:{SLIDE_BG};">
  <div style="position:absolute;top:28px;left:36px;right:36px;bottom:52px;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;overflow:hidden;">
    <!-- dense content -->
  </div>
  {progressBar}
  {swipeArrow}
</div>
```

If content still feels tight, shorten copy or remove one secondary component. Never reduce the bottom safe area.

### Headline-safe dense shell

Use this pattern on slides where the heading must stay visible while proof blocks fill the bottom half.

```html
<div class="slide" style="background:{SLIDE_BG};">
  <div style="position:absolute;top:28px;left:36px;right:36px;bottom:52px;min-height:0;display:flex;flex-direction:column;overflow:hidden;">
    <div style="flex-shrink:0;">
      <!-- label -->
      <!-- heading -->
      <!-- short intro -->
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;margin-top:auto;">
      <!-- 1-2 proof blocks max -->
    </div>
  </div>
  {progressBar}
  {swipeArrow}
</div>
```

Rules:
- Keep the heading block outside the bottom-aligned support stack
- The top copy block must use `flex-shrink:0`
- Limit the support stack to 2 major blocks on dense slides
- If the heading starts clipping, remove the lowest-priority support block instead of compressing the top copy

### Balanced headline shell

Use this pattern when the slide has one main proof block or when the center starts looking empty after overflow cleanup.

```html
<div class="slide" style="background:{SLIDE_BG};">
  <div style="position:absolute;top:28px;left:36px;right:36px;bottom:52px;min-height:0;display:flex;flex-direction:column;justify-content:center;gap:18px;overflow:hidden;">
    <div style="flex-shrink:0;">
      <!-- label -->
      <!-- heading -->
      <!-- short intro -->
    </div>

    <div style="display:flex;flex-wrap:wrap;gap:8px 8px;">
      <!-- 2-3 compact bridge chips -->
    </div>

    <div style="display:flex;flex-direction:column;gap:10px;">
      <!-- 1 main proof block -->
    </div>
  </div>
  {progressBar}
  {swipeArrow}
</div>
```

Use it when:
- only one proof block remains
- the main heading already takes a lot of vertical space
- a bottom-pinned support block creates a dead empty middle

Rules:
- Do not pin the support block to the bottom with `margin-top:auto`
- Use one slim bridge row between intro and proof
- Keep the bridge row lighter than the main proof block
- Prefer chips, mini bullets, or a source strip over another heavy card

### Bridge filler strip

Use this to connect the top copy and the proof block without making the slide too heavy.

```html
<div style="display:flex;flex-wrap:wrap;gap:8px;">
  <span class="sans" style="font-size:11px;padding:7px 10px;border-radius:999px;background:{chipBg};color:{chipText};">акции</span>
  <span class="sans" style="font-size:11px;padding:7px 10px;border-radius:999px;background:{chipBg};color:{chipText};">облигации</span>
  <span class="sans" style="font-size:11px;padding:7px 10px;border-radius:999px;background:{chipBg};color:{chipText};">фонды</span>
</div>
```

Use bridge fillers for:
- `что внутри`
- `кому подходит`
- `по правилам 2026`
- `что проверить перед покупкой`

Do not use a bridge filler as random decoration. It must complete the story started in the heading or intro.

### Overflow budget fallback

If a slide still exceeds the usable height:

- Remove the last optional block first
- Then tighten support-block padding
- Then tighten support-stack gap
- Never allow a visible card to sit behind the progress bar
- After cleanup, check for a dead center gap. If one appears, switch to the balanced headline shell or insert a bridge filler strip

---

## Stat Highlight Block

Big number with left accent border and source citation. **Use minimum 2 per carousel.**

```html
<div style="background:{cardBg};border-left:4px solid {BRAND_PRIMARY};border-radius:12px;padding:20px 24px;margin:16px 0;">
  <div class="serif" style="font-size:48px;font-weight:800;letter-spacing:-1px;color:{textColor};line-height:1.1;">
    {STAT_VALUE}
  </div>
  <div class="sans" style="font-size:13px;color:{mutedColor};margin-top:8px;line-height:1.4;">
    {Description} ({Source Name}, {Year})
  </div>
</div>
```

**Color adaptation:**
- Light slides: `cardBg = rgba(0,0,0,0.04)`, `textColor = DARK_BG`, `mutedColor = #8A8580`
- Dark slides: `cardBg = rgba(255,255,255,0.08)`, `textColor = #fff`, `mutedColor = rgba(255,255,255,0.5)`
- Gradient slides: `cardBg = rgba(0,0,0,0.15)`, `textColor = #fff`, `mutedColor = rgba(255,255,255,0.6)`

---

## Case Study Block

Real-world example card with labeled context. **Use minimum 1 per carousel.**

```html
<div style="background:{cardBg};border-radius:12px;padding:16px 20px;margin:12px 0;">
  <div class="sans" style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:2px;color:{labelColor};margin-bottom:8px;">
    {LABEL}
  </div>
  <div class="sans" style="font-size:14px;color:{textColor};line-height:1.5;">
    {Case description with company name, specific numbers, outcome}
  </div>
</div>
```

**Labels to use:** `REAL EXAMPLE`, `CASE STUDY`, `USE CASE: {ROLE}`, `EXAMPLE: {PROFESSION}`

---

## Entity / Company Card

For carousels that list multiple items (companies, tools, assets, people). Keep identical structure across all entity slides.

**IMPORTANT:** This is the component most prone to overflow. The content MUST fit within the slide. Use the content budget below strictly.

```html
<!-- Note: this goes INSIDE the slide container's inner div (which already has overflow:hidden and padding-bottom:52px) -->
<div style="flex:1;display:flex;flex-direction:column;position:relative;">
  <!-- Decorative background number -->
  <div style="position:absolute;top:-8px;right:-8px;font-family:'{HEADING_FONT}';font-size:140px;font-weight:800;color:{BRAND_PRIMARY};opacity:0.08;line-height:1;pointer-events:none;user-select:none;">
    {NN}
  </div>
  <!-- Category label -->
  <span class="sans" style="display:inline-block;font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{labelColor};margin-bottom:12px;">FUND #{N}</span>
  <!-- Icon -->
  <div style="width:56px;height:56px;background:{iconBg};border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:12px;">
    {EMOJI}
  </div>
  <!-- Ticker badge -->
  <div style="display:inline-flex;align-items:center;gap:6px;background:{badgeBg};border-radius:20px;padding:4px 14px;margin-bottom:10px;width:fit-content;">
    <span style="color:{BRAND_PRIMARY};font-size:8px;">&#9679;</span>
    <span class="sans" style="font-size:12px;font-weight:600;color:{BRAND_PRIMARY};">{TICKER}</span>
  </div>
  <!-- Entity name — MAX 1 LINE -->
  <div class="serif" style="font-size:26px;font-weight:700;color:{textColor};margin-bottom:6px;line-height:1.15;">
    {ENTITY_NAME}
  </div>
  <!-- Description — MAX 2-3 LINES (~120 chars) -->
  <div class="sans" style="font-size:14px;color:{mutedColor};line-height:1.5;margin-bottom:14px;">
    {Short description}
  </div>
  <!-- Info block — MAX 3 LINES (~130 chars) -->
  <div style="background:{infoBg};border-radius:12px;padding:14px 18px;margin-bottom:10px;">
    <div class="sans" style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:{BRAND_PRIMARY};margin-bottom:5px;">
      {INFO_LABEL}
    </div>
    <div class="sans" style="font-size:13px;color:{textColor};line-height:1.5;">
      {Why this entity matters — keep concise}
    </div>
  </div>
  <!-- OPTIONAL: 1 icon bullet OR 1 percentage bar — NOT both. Only add if space allows. -->
  <div style="display:flex;align-items:flex-start;gap:10px;margin-top:auto;">
    <div style="font-size:16px;flex-shrink:0;">✅</div>
    <div>
      <div class="sans" style="font-size:13px;font-weight:700;color:{textColor};">{Short title}</div>
      <div class="sans" style="font-size:12px;color:{mutedColor};margin-top:1px;">{One line}</div>
    </div>
  </div>
</div>
```

**Content budget for entity cards (prevents overflow):**
- Category label: 1 line
- Icon: fixed 56px
- Ticker: 1 line
- Name: 1 line max
- Description: 2-3 lines max (~120 characters)
- Info block: label + 2-3 lines max (~130 characters)
- Optional extra: 1 icon bullet OR 1 percentage bar — never both
- If you add a case study block, remove the icon bullet AND shorten the description to 2 lines

**Info labels:** `WHY INTERESTING`, `KEY ADVANTAGE`, `GROWTH DRIVER`, `UNIQUE VALUE`

**Color adaptation:**
- Light: `iconBg = rgba(BRAND_PRIMARY, 0.1)`, `badgeBg = rgba(BRAND_PRIMARY, 0.08)`, `infoBg = rgba(0,0,0,0.04)`
- Dark: `iconBg = rgba(BRAND_PRIMARY, 0.15)`, `badgeBg = rgba(BRAND_PRIMARY, 0.12)`, `infoBg = rgba(255,255,255,0.06)`

**Spacing rule:** The emoji icon must sit immediately below the category label (max 12px gap). The decorative number in the top-right fills the visual void. Never leave the top 25% of an entity slide empty.

---

## Icon Bullet Point

Emoji + bold title + subtitle. Use 2-3 at the bottom of any slide to fill remaining vertical space.

```html
<div style="display:flex;align-items:flex-start;gap:12px;margin:10px 0;">
  <div style="font-size:20px;flex-shrink:0;margin-top:2px;">{EMOJI}</div>
  <div>
    <div class="sans" style="font-size:15px;font-weight:700;color:{textColor};">{Title}</div>
    <div class="sans" style="font-size:13px;color:{mutedColor};margin-top:2px;">{Subtitle}</div>
  </div>
</div>
```

---

## Comparison Cards

Two stacked cards showing contrasting approaches, types, or before/after states.

```html
<!-- Type 1 card -->
<div style="background:{lightCardBg};border-radius:12px;padding:16px 20px;margin-bottom:10px;">
  <div class="sans" style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:2px;color:{mutedColor};margin-bottom:6px;">
    {TYPE_1_LABEL}
  </div>
  <div class="sans" style="font-size:14px;color:{textColor};line-height:1.5;">{Description}</div>
</div>
<!-- Type 2 card (accented) -->
<div style="background:{darkCardBg};border-radius:12px;padding:16px 20px;">
  <div class="sans" style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:2px;color:{accentLabel};margin-bottom:6px;">
    {TYPE_2_LABEL}
  </div>
  <div class="sans" style="font-size:14px;color:{lightText};line-height:1.5;">{Description}</div>
</div>
```

---

## Grid Layout 2x2

For comparison, overview, or multi-item slides. Each cell must have a title AND at least 2 lines of detail.

```html
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0;">
  <div style="background:{cardBg};border-radius:12px;padding:16px;">
    <div class="serif" style="font-size:18px;font-weight:700;color:{textColor};margin-bottom:4px;">{Title}</div>
    <div class="sans" style="font-size:12px;color:{mutedColor};line-height:1.4;">{Detail line 1}<br>{Detail line 2}<br>{Detail line 3}</div>
  </div>
  <div style="background:{cardBg};border-radius:12px;padding:16px;">
    <div class="serif" style="font-size:18px;font-weight:700;color:{textColor};margin-bottom:4px;">{Title}</div>
    <div class="sans" style="font-size:12px;color:{mutedColor};line-height:1.4;">{Detail line 1}<br>{Detail line 2}<br>{Detail line 3}</div>
  </div>
  <div style="background:{cardBg};border-radius:12px;padding:16px;">
    <div class="serif" style="font-size:18px;font-weight:700;color:{textColor};margin-bottom:4px;">{Title}</div>
    <div class="sans" style="font-size:12px;color:{mutedColor};line-height:1.4;">{Detail line 1}<br>{Detail line 2}<br>{Detail line 3}</div>
  </div>
  <div style="background:{cardBg};border-radius:12px;padding:16px;">
    <div class="serif" style="font-size:18px;font-weight:700;color:{textColor};margin-bottom:4px;">{Title}</div>
    <div class="sans" style="font-size:12px;color:{mutedColor};line-height:1.4;">{Detail line 1}<br>{Detail line 2}<br>{Detail line 3}</div>
  </div>
</div>
```

---

## Strikethrough Pills

"What's being replaced" on problem slides.

```html
<div style="display:flex;flex-wrap:wrap;gap:8px;margin:16px 0;">
  <span style="font-size:11px;padding:5px 12px;border:1px solid rgba(255,255,255,0.1);border-radius:20px;color:#6B6560;text-decoration:line-through;">{Old thing 1}</span>
  <span style="font-size:11px;padding:5px 12px;border:1px solid rgba(255,255,255,0.1);border-radius:20px;color:#6B6560;text-decoration:line-through;">{Old thing 2}</span>
  <span style="font-size:11px;padding:5px 12px;border:1px solid rgba(255,255,255,0.1);border-radius:20px;color:#6B6560;text-decoration:line-through;">{Old thing 3}</span>
</div>
```

---

## Tag Pills

Feature labels, options, or categories.

```html
<div style="display:flex;flex-wrap:wrap;gap:8px;margin:16px 0;">
  <span class="sans" style="font-size:11px;padding:5px 12px;background:{pillBg};border-radius:20px;color:{pillColor};">{Label}</span>
</div>
```

- Dark slides: `pillBg = rgba(255,255,255,0.06)`, `pillColor = BRAND_LIGHT`
- Light slides: `pillBg = rgba(0,0,0,0.06)`, `pillColor = DARK_BG`

---

## Quote / Prompt Box

For example inputs, quotes, or testimonials.

```html
<div style="padding:16px;background:rgba(0,0,0,0.15);border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
  <p class="sans" style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:6px;">{Label}</p>
  <p class="serif" style="font-size:15px;color:#fff;font-style:italic;line-height:1.4;">"{Quote text}"</p>
</div>
```

---

## Feature List

Icon + label + description rows. Use 3-4 per feature/benefit slide.

```html
<div style="display:flex;align-items:flex-start;gap:14px;padding:10px 0;border-bottom:1px solid {LIGHT_BORDER};">
  <span style="color:{BRAND_PRIMARY};font-size:15px;width:18px;text-align:center;">{icon}</span>
  <div>
    <span class="sans" style="font-size:14px;font-weight:600;color:{DARK_BG};">{Label}</span><br>
    <span class="sans" style="font-size:12px;color:#8A8580;">{Description}</span>
  </div>
</div>
```

---

## Numbered Steps

For workflow or how-to slides.

```html
<div style="display:flex;align-items:flex-start;gap:16px;padding:14px 0;border-bottom:1px solid {LIGHT_BORDER};">
  <span class="serif" style="font-size:26px;font-weight:300;color:{BRAND_PRIMARY};min-width:34px;line-height:1;">01</span>
  <div>
    <span class="sans" style="font-size:14px;font-weight:600;color:{DARK_BG};">{Step title}</span><br>
    <span class="sans" style="font-size:12px;color:#8A8580;">{Step description}</span>
  </div>
</div>
```

---

## Mini Data Visualizations

### Percentage Bar
For adoption rates, market shares, completion metrics.

```html
<div style="margin:12px 0;">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
    <span class="sans" style="font-size:13px;color:{textColor};">{Label}</span>
    <span class="sans" style="font-size:13px;font-weight:700;color:{BRAND_PRIMARY};">{value}%</span>
  </div>
  <div style="height:8px;background:{trackBg};border-radius:4px;overflow:hidden;">
    <div style="height:100%;width:{value}%;background:{BRAND_PRIMARY};border-radius:4px;"></div>
  </div>
</div>
```
- Light: `trackBg = rgba(0,0,0,0.08)` / Dark: `trackBg = rgba(255,255,255,0.12)`

### Comparison Bars
For before/after or two-value contrasts.

```html
<div style="display:flex;gap:16px;align-items:flex-end;margin:16px 0;height:120px;">
  <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;">
    <div style="width:100%;height:{h1}px;background:{BRAND_LIGHT};border-radius:8px 8px 0 0;"></div>
    <div class="sans" style="font-size:12px;font-weight:700;margin-top:8px;color:{textColor};">{Label 1}</div>
    <div class="serif" style="font-size:20px;font-weight:800;color:{BRAND_PRIMARY};">{Value 1}</div>
  </div>
  <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;">
    <div style="width:100%;height:{h2}px;background:{BRAND_PRIMARY};border-radius:8px 8px 0 0;"></div>
    <div class="sans" style="font-size:12px;font-weight:700;margin-top:8px;color:{textColor};">{Label 2}</div>
    <div class="serif" style="font-size:20px;font-weight:800;color:{BRAND_PRIMARY};">{Value 2}</div>
  </div>
</div>
```

### Progress Ring (SVG)
For single percentage emphasis. Max 1 per carousel.

```html
<div style="position:relative;width:80px;height:80px;">
  <svg viewBox="0 0 36 36" style="width:80px;height:80px;transform:rotate(-90deg);">
    <circle cx="18" cy="18" r="15.5" fill="none" stroke="{trackBg}" stroke-width="3"/>
    <circle cx="18" cy="18" r="15.5" fill="none" stroke="{BRAND_PRIMARY}" stroke-width="3"
      stroke-dasharray="{value}, 100" stroke-linecap="round"/>
  </svg>
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:'{HEADING_FONT}';font-size:20px;font-weight:800;color:{textColor};">
    {value}%
  </div>
</div>
```

**Rule:** Use at least 1 data visualization per carousel.

---

## Decorative Elements

### Accent Line
Horizontal divider between content sections.
```html
<div style="width:40px;height:4px;background:{BRAND_PRIMARY};border-radius:2px;margin:16px 0;"></div>
```

### Large Background Number
Oversized decorative number for entity card slides.
```html
<div style="position:absolute;top:20px;right:28px;font-family:'{HEADING_FONT}';font-size:140px;font-weight:800;color:{BRAND_PRIMARY};opacity:0.08;line-height:1;pointer-events:none;user-select:none;">
  {NUMBER}
</div>
```

### Dot Pattern
Subtle texture for empty corners. Max 2 per carousel.
```html
<div style="position:absolute;{position};opacity:0.06;">
  <svg width="60" height="60" viewBox="0 0 60 60">
    <circle cx="10" cy="10" r="3" fill="{BRAND_PRIMARY}"/>
    <circle cx="30" cy="10" r="3" fill="{BRAND_PRIMARY}"/>
    <circle cx="50" cy="10" r="3" fill="{BRAND_PRIMARY}"/>
    <circle cx="10" cy="30" r="3" fill="{BRAND_PRIMARY}"/>
    <circle cx="30" cy="30" r="3" fill="{BRAND_PRIMARY}"/>
    <circle cx="50" cy="30" r="3" fill="{BRAND_PRIMARY}"/>
    <circle cx="10" cy="50" r="3" fill="{BRAND_PRIMARY}"/>
    <circle cx="30" cy="50" r="3" fill="{BRAND_PRIMARY}"/>
    <circle cx="50" cy="50" r="3" fill="{BRAND_PRIMARY}"/>
  </svg>
</div>
```

### Color Swatches
For branding or customization slides.
```html
<div style="width:32px;height:32px;border-radius:8px;background:{color};border:1px solid rgba(255,255,255,0.08);"></div>
```

---

## Logo Lockup

Brand icon + name for first and last slides.

```html
<div style="display:flex;align-items:center;gap:12px;margin-bottom:24px;">
  <div style="width:44px;height:44px;background:{BRAND_LIGHT};border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:{BRAND_PRIMARY};">
    {LOGO_OR_INITIAL}
  </div>
  <div style="font-family:'{HEADING_FONT}';font-size:16px;font-weight:700;color:{textColor};letter-spacing:0.5px;">
    {BRAND_NAME}
  </div>
</div>
```

---

## CTA Button

Final slide only.

```html
<div style="display:inline-flex;align-items:center;gap:8px;padding:12px 28px;background:{LIGHT_BG};color:{BRAND_DARK};font-family:'{BODY_FONT}',sans-serif;font-weight:600;font-size:14px;border-radius:28px;">
  {CTA text}
</div>
```

---

## Tag / Category Labels

### Standard tag
```html
<span class="sans" style="display:inline-block;font-size:10px;font-weight:600;letter-spacing:2px;color:{color};margin-bottom:16px;">{TAG TEXT}</span>
```
- Light slides: `color = BRAND_PRIMARY`
- Dark slides: `color = BRAND_LIGHT`
- Gradient slides: `color = rgba(255,255,255,0.6)`

### Numbered category label
```html
<span class="sans" style="display:inline-block;font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BRAND_PRIMARY};margin-bottom:16px;">CATEGORY #{N}</span>
```

---

## Recommended Sequences

### 7-slide carousel (product/service)
```
1. Hero (light) — hook + brand lockup
2. Problem (dark) — pain point + comparison cards
3. Solution (soft gradient) — what solves it + quote/prompt box
4. Features (light) — feature list with icons
5. Details/Specs (dark) — deeper info + stat blocks
6. How-To (light) — numbered steps
7. CTA (gradient) — call to action + button
```

### 8-slide carousel (educational/analytical)
```
1. Hero (light) — hook + stat
2. Problem (dark) — pain points + strikethrough pills or comparison cards
3. Solution (soft gradient) — answer + feature list
4. Category #1 (light) — stat block + case study + icon bullets
5. Category #2 (dark) — stat block + case study + icon bullets
6. Category #3 (light) — stat block + real example + icon bullets
7. Grid/Overview (dark or light-surface) — 2x2 grid + total stat
8. CTA (gradient) — call to action + button + code word
```

### 10-slide carousel (entity list: "5 companies", "7 tools")
```
1. Hero (light) — hook + brand lockup + tag pills listing entities
2. Problem (dark) — pain points + strikethrough pills
3. Solution (soft gradient) — feature list with icons
4. Entity #1 (light) — entity card with decorative "01"
5. Entity #2 (dark) — entity card with decorative "02"
6. Entity #3 (light) — entity card with decorative "03"
7. Entity #4 (dark) — entity card with decorative "04"
8. Entity #5 (light) — entity card with decorative "05"
9. Overview / verdict (dark or light-surface) — comparison, shortlist, or selection rule
10. CTA (gradient) — call to action + button
```

### Variation tips for entity sequences:
- Alternate light/dark on every entity card
- Add an extra icon bullet point on the 3rd and 5th cards only if the slide still respects the safe area
- Use slide 9 as a bridge into the CTA so the ending does not feel like a sudden palette jump
- Vary decorative number position (right on odd, left on even)
- Consider inserting a Stat/Data or Grid slide mid-sequence to break repetition
