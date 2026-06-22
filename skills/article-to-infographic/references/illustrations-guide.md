# Illustration Integration Guide

How to add character/cartoon illustrations to infographics for a more engaging, editorial feel.

## Recommended Libraries (CC0 / Free Commercial Use)

| Library | License | Style | Count | Best For |
|---------|---------|-------|-------|----------|
| **Open Peeps** | CC0 | Hand-drawn line art, modular | 584K+ combos | Character avatars, busts |
| **Open Doodles** | CC0 | Casual hand-drawn, pink accent | 40+ | Fun, informal infographics |
| **unDraw** | Open (free commercial) | Flat minimalist, customizable color | 1,200+ | Scenario illustrations |
| **ManyPixels** | Free, no attribution | 5 distinct styles | 20,000+ | Widest variety |
| **Illustrations.co** | Free, no attribution | Retro/contemporary | 120+ | Tech themes |
| **Lukasz Adam** | CC0 | Flat, tech-focused | 100+ | Developer/tech content |
| **DrawKit** | Free + Pro | Hand-drawn 2D & 3D | Varies | Professional presentations |

### Where to Download

- **Open Peeps**: https://www.openpeeps.com/ (Gumroad download)
- **Open Doodles**: https://www.opendoodles.com/ (direct SVG downloads)
- **unDraw**: https://undraw.co/ (SVG with color customization)
- **ManyPixels**: https://www.manypixels.co/gallery
- **Illustrations.co**: https://illlustrations.co/
- **Lukasz Adam**: https://lukaszadam.com/illustrations

### Libraries to Avoid (Licensing Issues)

- **Storyset/Freepik** -- Requires attribution for free use
- **Blush.design** -- SVG requires paid Pro subscription (free = PNG only)
- **Absurd Design** -- Attribution required, SVG is membership-only
- **Sapiens/UI8** -- Paid product

---

## Embedding Method: Inline SVG

For self-contained HTML infographics, **always use inline SVG**:

```html
<div class="illustration" aria-label="Person working at computer">
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img">
        <title>Working person illustration</title>
        <!-- SVG content here -->
    </svg>
</div>
```

### Why Inline SVG

- Zero external dependencies (everything in one file)
- Full CSS/JS control (can re-color, animate, respond to hover)
- No additional HTTP requests
- Best accessibility (ARIA labels, `<title>` elements)
- No encoding overhead (unlike base64)

### SVG Optimization Before Embedding

1. **Run through SVGOMG** (https://jakearchibald.github.io/svgomg/):
   - Remove metadata, comments, editor artifacts
   - Optimize paths and transforms
   - Minify CSS/attributes
   - Typical reduction: 30-70% file size

2. **Ensure unique IDs** across all SVGs in the HTML:
   - Prefix gradient/pattern/clip IDs with section name
   - Example: `id="s1-gradient"`, `id="s2-gradient"`

3. **Remove XML declaration** (`<?xml version="1.0"?>`) -- not needed inline

4. **Remove fixed width/height** -- use `viewBox` for responsive sizing

### Avoid These Approaches

- **Base64 data URI** -- Adds ~33% size overhead, worse gzip compression
- **External `<img src>`** -- Breaks self-contained requirement
- **`<object>` or `<iframe>`** -- Unnecessary complexity, poor CSS control

---

## Layout Patterns

### Pattern A: Alternating Text + Illustration

Best for 3-5 section infographics. Text and illustration alternate sides.

```css
.section { display: flex; align-items: center; gap: 4rem; }
.section:nth-child(even) { flex-direction: row-reverse; }
.section-text { flex: 1; }
.section-illustration { flex: 0 0 280px; }
.section-illustration svg { width: 100%; height: auto; }

@media (max-width: 768px) {
    .section, .section:nth-child(even) { flex-direction: column; }
    .section-illustration { flex: 0 0 auto; max-width: 200px; }
}
```

### Pattern B: Illustration as Section Background

Large, semi-transparent illustration behind text.

```css
.section { position: relative; }
.section-illustration {
    position: absolute;
    right: -5%;
    top: 50%;
    transform: translateY(-50%);
    width: 40%;
    opacity: 0.08;
    pointer-events: none;
}
```

### Pattern C: Small Decorative Icons

Hand-coded mini SVGs (64-80px) as section markers alongside headings.

```css
.section-icon {
    width: 64px;
    height: 64px;
    display: inline-flex;
    vertical-align: middle;
    margin-right: 0.75rem;
}
```

### Pattern D: Hero Character

Large character illustration in the header/hero area.

```css
.hero { display: grid; grid-template-columns: 1fr 1fr; align-items: center; }
.hero-illustration { max-width: 400px; margin: 0 auto; }
```

---

## Custom Mini SVG Icons

When full illustrations are too heavy (~50-100KB each), create lightweight custom icons:

### Monitor/Dashboard Icon (Runtime/Monitoring)
```svg
<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="12" width="64" height="44" rx="4" fill="none" stroke="currentColor" stroke-width="2"/>
    <rect x="30" y="56" width="20" height="4" rx="1" fill="currentColor" opacity="0.3"/>
    <polyline points="16,44 28,32 36,38 52,24 64,30" fill="none" stroke="var(--accent-1)" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="52" cy="24" r="3" fill="var(--accent-1)"/>
</svg>
```

### Gear/Code Icon (Automation/Code Generation)
```svg
<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="40" r="20" fill="none" stroke="currentColor" stroke-width="2"/>
    <circle cx="40" cy="40" r="8" fill="var(--accent-1)" opacity="0.2"/>
    <!-- gear teeth -->
    <rect x="37" y="8" width="6" height="12" rx="2" fill="currentColor" opacity="0.5"/>
    <rect x="37" y="60" width="6" height="12" rx="2" fill="currentColor" opacity="0.5"/>
    <rect x="8" y="37" width="12" height="6" rx="2" fill="currentColor" opacity="0.5"/>
    <rect x="60" y="37" width="12" height="6" rx="2" fill="currentColor" opacity="0.5"/>
    <!-- code brackets -->
    <text x="32" y="45" font-family="monospace" font-size="16" fill="var(--accent-1)">{ }</text>
</svg>
```

### Brain/Document Icon (Memory/Knowledge)
```svg
<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="12" y="8" width="40" height="52" rx="3" fill="none" stroke="currentColor" stroke-width="2"/>
    <line x1="20" y1="20" x2="44" y2="20" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
    <line x1="20" y1="28" x2="44" y2="28" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
    <line x1="20" y1="36" x2="36" y2="36" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
    <!-- lightbulb -->
    <circle cx="56" cy="52" r="14" fill="var(--accent-1)" opacity="0.15"/>
    <path d="M56,42 Q64,48 60,56 L52,56 Q48,48 56,42Z" fill="none" stroke="var(--accent-1)" stroke-width="2"/>
    <line x1="52" y1="60" x2="60" y2="60" stroke="var(--accent-1)" stroke-width="2" stroke-linecap="round"/>
</svg>
```

---

## Color Matching

When embedding illustrations, match them to the infographic's palette:

### For CSS-controllable SVGs (inline)

Use `currentColor` and CSS custom properties:

```css
.illustration svg {
    color: var(--text-secondary);  /* currentColor inheritance */
}
.illustration svg .accent { fill: var(--accent-1); }
```

### For Open Doodles / Open Peeps

These typically use black strokes with a single accent fill. Override via CSS:

```css
.illustration svg path[fill="#FF5678"] {
    fill: var(--accent-1);  /* Replace pink with your accent */
}
```

### For unDraw

unDraw allows color customization before download. Choose your `--accent-1` color.

---

## Size Guidelines

| Illustration Type | Recommended Size | Max File Size |
|---|---|---|
| Hero character | 300-400px wide | 80KB |
| Section illustration | 200-300px wide | 60KB |
| Decorative icon | 48-80px | 2KB |
| Background watermark | 40% of section width | 60KB |

**Total illustration budget per infographic: ~200-300KB** to keep the HTML file under 500KB.

---

## Accessibility

Always include:

```html
<svg role="img" aria-labelledby="illust-title-1">
    <title id="illust-title-1">Person monitoring system dashboard</title>
    <!-- SVG content -->
</svg>
```

For decorative-only illustrations:

```html
<svg aria-hidden="true" focusable="false">
    <!-- Decorative SVG -->
</svg>
```
