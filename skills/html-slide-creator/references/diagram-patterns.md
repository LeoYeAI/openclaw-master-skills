# Diagram Patterns — Inline SVG

Use these patterns to generate diagrams as inline SVG with zero runtime dependencies.
All diagrams adapt to the presentation's CSS custom properties (`--accent`, `--text-primary`, etc.).

---

## When to Use a Diagram Slide

Use a diagram when the relationship between things matters more than the things themselves:
- Steps in a process → Flowchart
- A → B → C over time → Timeline
- Comparing options → Comparison table or bar chart
- Hierarchy / org structure → Org chart
- Part-to-whole → Donut / pie

**Density rule:** One diagram per slide, max. Never combine a diagram with a bullet list.

---

## 1. Horizontal Flowchart (3–5 steps)

```html
<svg viewBox="0 0 700 120" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:700px;height:auto;display:block;margin:0 auto">
  <defs>
    <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="currentColor" opacity="0.5"/>
    </marker>
  </defs>
  <!-- Boxes: cx=75,225,375,525,675  cy=60  w=120  h=48 -->
  <g fill="none" stroke="currentColor" stroke-opacity="0.15" stroke-width="1.5">
    <rect x="15"  y="36" width="120" height="48" rx="8"/>
    <rect x="165" y="36" width="120" height="48" rx="8"/>
    <rect x="315" y="36" width="120" height="48" rx="8"/>
    <rect x="465" y="36" width="120" height="48" rx="8"/>
  </g>
  <!-- Arrows -->
  <g stroke="currentColor" stroke-opacity="0.4" stroke-width="1.5" marker-end="url(#arr)">
    <line x1="136" y1="60" x2="163" y2="60"/>
    <line x1="286" y1="60" x2="313" y2="60"/>
    <line x1="436" y1="60" x2="463" y2="60"/>
  </g>
  <!-- Labels — replace text content, keep positions -->
  <g font-family="inherit" font-size="13" text-anchor="middle" fill="currentColor">
    <text x="75"  y="57">Step One</text>
    <text x="75"  y="74" font-size="11" opacity="0.5">subtitle</text>
    <text x="225" y="57">Step Two</text>
    <text x="225" y="74" font-size="11" opacity="0.5">subtitle</text>
    <text x="375" y="57">Step Three</text>
    <text x="375" y="74" font-size="11" opacity="0.5">subtitle</text>
    <text x="525" y="57">Step Four</text>
    <text x="525" y="74" font-size="11" opacity="0.5">subtitle</text>
  </g>
  <!-- Accent highlight on first box -->
  <rect x="15" y="36" width="120" height="48" rx="8" fill="var(--accent)" fill-opacity="0.08" stroke="var(--accent)" stroke-opacity="0.4" stroke-width="1.5"/>
</svg>
```

**Customisation:** Change text labels. Add/remove box groups in sets of 3 (rect + arrow + text). Shift accent highlight to any box.

---

## 2. Vertical Timeline (3–5 events)

```html
<svg viewBox="0 0 560 280" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:560px;height:auto;display:block;margin:0 auto">
  <!-- Spine -->
  <line x1="48" y1="20" x2="48" y2="260" stroke="currentColor" stroke-opacity="0.15" stroke-width="2"/>
  <!-- Events — repeat this group, shifting cy by 60 each time -->
  <g font-family="inherit" fill="currentColor">
    <!-- Event 1 (accent) -->
    <circle cx="48" cy="40"  r="7" fill="var(--accent)" opacity="0.9"/>
    <text x="72" y="36"  font-size="12" opacity="0.5">2022 Q1</text>
    <text x="72" y="52"  font-size="15" font-weight="600">Launch</text>
    <!-- Event 2 -->
    <circle cx="48" cy="100" r="5" fill="currentColor" opacity="0.2"/>
    <text x="72" y="96"  font-size="12" opacity="0.5">2022 Q3</text>
    <text x="72" y="112" font-size="15">10k Users</text>
    <!-- Event 3 -->
    <circle cx="48" cy="160" r="5" fill="currentColor" opacity="0.2"/>
    <text x="72" y="156" font-size="12" opacity="0.5">2023 Q1</text>
    <text x="72" y="172" font-size="15">Series A</text>
    <!-- Event 4 -->
    <circle cx="48" cy="220" r="5" fill="currentColor" opacity="0.2"/>
    <text x="72" y="216" font-size="12" opacity="0.5">2024 Q2</text>
    <text x="72" y="232" font-size="15">100k Users</text>
  </g>
</svg>
```

---

## 3. Horizontal Bar Chart (3–6 bars)

```html
<svg viewBox="0 0 560 200" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:560px;height:auto;display:block;margin:0 auto">
  <g font-family="inherit" font-size="13" fill="currentColor">
    <!-- Bar template: label at x=0, bar starts x=120, value label at bar end+6 -->
    <!-- Bar 1 (accent) — width proportional to value, max ~380px = 100% -->
    <text x="0"   y="30"  text-anchor="start" opacity="0.8">Category A</text>
    <rect x="120" y="14"  width="380" height="20" rx="4" fill="var(--accent)" opacity="0.85"/>
    <text x="508" y="30"  opacity="0.6">95%</text>
    <!-- Bar 2 -->
    <text x="0"   y="72"  text-anchor="start" opacity="0.8">Category B</text>
    <rect x="120" y="56"  width="280" height="20" rx="4" fill="currentColor" opacity="0.18"/>
    <text x="408" y="72"  opacity="0.5">70%</text>
    <!-- Bar 3 -->
    <text x="0"   y="114" text-anchor="start" opacity="0.8">Category C</text>
    <rect x="120" y="98"  width="200" height="20" rx="4" fill="currentColor" opacity="0.18"/>
    <text x="328" y="114" opacity="0.5">50%</text>
    <!-- Bar 4 -->
    <text x="0"   y="156" text-anchor="start" opacity="0.8">Category D</text>
    <rect x="120" y="140" width="120" height="20" rx="4" fill="currentColor" opacity="0.18"/>
    <text x="248" y="156" opacity="0.5">30%</text>
  </g>
</svg>
```

**Formula:** bar width = `(value / 100) * 380`. Accent bar = highlight row.

---

## 4. 2×2 Comparison Grid

```html
<svg viewBox="0 0 520 320" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:520px;height:auto;display:block;margin:0 auto">
  <defs>
    <style>.ql{font-family:inherit;font-size:11px;fill:currentColor;opacity:0.45;text-anchor:middle}
           .qt{font-family:inherit;font-size:15px;fill:currentColor;font-weight:600;text-anchor:middle}
           .qb{font-family:inherit;font-size:12px;fill:currentColor;opacity:0.6;text-anchor:middle}</style>
  </defs>
  <!-- Axis labels -->
  <text x="260" y="16"  class="ql">High Value →</text>
  <text x="260" y="312" class="ql">← Low Value</text>
  <text x="12"  y="164" class="ql" transform="rotate(-90,12,164)">Low Effort ↑</text>
  <text x="508" y="164" class="ql" transform="rotate(90,508,164)">High Effort ↓</text>
  <!-- Grid lines -->
  <line x1="260" y1="24" x2="260" y2="296" stroke="currentColor" stroke-opacity="0.1" stroke-width="1"/>
  <line x1="24"  y1="160" x2="496" y2="160" stroke="currentColor" stroke-opacity="0.1" stroke-width="1"/>
  <!-- Quadrants (top-right = accent = do first) -->
  <rect x="264" y="28"  width="228" height="128" rx="10" fill="var(--accent)" fill-opacity="0.07" stroke="var(--accent)" stroke-opacity="0.2" stroke-width="1"/>
  <rect x="28"  y="28"  width="228" height="128" rx="10" fill="currentColor" fill-opacity="0.03" stroke="currentColor" stroke-opacity="0.08" stroke-width="1"/>
  <rect x="264" y="164" width="228" height="128" rx="10" fill="currentColor" fill-opacity="0.03" stroke="currentColor" stroke-opacity="0.08" stroke-width="1"/>
  <rect x="28"  y="164" width="228" height="128" rx="10" fill="currentColor" fill-opacity="0.03" stroke="currentColor" stroke-opacity="0.08" stroke-width="1"/>
  <!-- Quadrant titles + descriptions -->
  <text x="378" y="72"  class="qt">Do First</text>
  <text x="378" y="92"  class="qb">High value,</text>
  <text x="378" y="108" class="qb">low effort</text>
  <text x="142" y="72"  class="qt">Plan</text>
  <text x="142" y="92"  class="qb">High value,</text>
  <text x="142" y="108" class="qb">high effort</text>
  <text x="378" y="208" class="qt">Fill-in</text>
  <text x="378" y="228" class="qb">Low value,</text>
  <text x="378" y="244" class="qb">low effort</text>
  <text x="142" y="208" class="qt">Avoid</text>
  <text x="142" y="228" class="qb">Low value,</text>
  <text x="142" y="244" class="qb">high effort</text>
</svg>
```

---

## 5. Simple Org / Hierarchy Chart (2 levels)

```html
<svg viewBox="0 0 560 200" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:560px;height:auto;display:block;margin:0 auto">
  <!-- Root box -->
  <rect x="200" y="10" width="160" height="44" rx="8"
        fill="var(--accent)" fill-opacity="0.15" stroke="var(--accent)" stroke-opacity="0.5" stroke-width="1.5"/>
  <text x="280" y="28"  font-family="inherit" font-size="14" font-weight="600" text-anchor="middle" fill="currentColor">CEO</text>
  <text x="280" y="46"  font-family="inherit" font-size="11" text-anchor="middle" fill="currentColor" opacity="0.5">Jane Smith</text>
  <!-- Connector spine -->
  <line x1="280" y1="54" x2="280" y2="100" stroke="currentColor" stroke-opacity="0.15" stroke-width="1.5"/>
  <line x1="80"  y1="100" x2="480" y2="100" stroke="currentColor" stroke-opacity="0.15" stroke-width="1.5"/>
  <!-- Child connectors -->
  <line x1="80"  y1="100" x2="80"  y2="130" stroke="currentColor" stroke-opacity="0.15" stroke-width="1.5"/>
  <line x1="280" y1="100" x2="280" y2="130" stroke="currentColor" stroke-opacity="0.15" stroke-width="1.5"/>
  <line x1="480" y1="100" x2="480" y2="130" stroke="currentColor" stroke-opacity="0.15" stroke-width="1.5"/>
  <!-- Child boxes — repeat as needed -->
  <g fill="none" stroke="currentColor" stroke-opacity="0.15" stroke-width="1.5">
    <rect x="20"  y="130" width="120" height="44" rx="8"/>
    <rect x="220" y="130" width="120" height="44" rx="8"/>
    <rect x="420" y="130" width="120" height="44" rx="8"/>
  </g>
  <g font-family="inherit" font-size="13" text-anchor="middle" fill="currentColor">
    <text x="80"  y="149">Engineering</text>
    <text x="80"  y="165" font-size="11" opacity="0.5">12 people</text>
    <text x="280" y="149">Product</text>
    <text x="280" y="165" font-size="11" opacity="0.5">8 people</text>
    <text x="480" y="149">Design</text>
    <text x="480" y="165" font-size="11" opacity="0.5">5 people</text>
  </g>
</svg>
```

---

## Usage Instructions for Claude

1. When a slide needs a diagram, pick the closest pattern above
2. Replace all text labels with actual content
3. Adjust bar widths / circle positions / box counts to match data
4. Wrap in a `.slide` section with appropriate `data-notes`
5. Apply `color: var(--text-primary)` on the SVG's parent so `currentColor` inherits correctly
6. Scale diagrams: use `style="width:100%;max-width:Xpx"` to control size within the slide

**Do NOT** use Mermaid.js, Chart.js, or any external library. Inline SVG only.
