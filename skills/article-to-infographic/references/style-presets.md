# Style Presets

Detailed color palettes, font pairings, and design tokens for each infographic style.

## Bold & Vibrant

```css
:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-card: #0f3460;
    --text-primary: #ffffff;
    --text-secondary: #a8b2d1;
    --accent-1: #e94560;
    --accent-2: #f5c518;
    --accent-3: #00d2ff;
    --font-display: 'Clash Display', sans-serif;
    --font-body: 'Satoshi', sans-serif;
}
```
- **Fonts:** Clash Display + Satoshi (Fontshare) or Space Grotesk + DM Sans (Google)
- **Feel:** High energy, confident, impactful
- **Best for:** Statistics dashboards, listicles, comparison infographics
- **Background:** Dark base with vibrant accents; use gradient meshes or subtle geometric patterns
- **Cards:** Semi-transparent with border glow on accent color
- **Charts:** Use accent-1 for primary bars, accent-2 for secondary, accent-3 for highlights

## Clean & Minimal

```css
:root {
    --bg-primary: #fafaf9;
    --bg-secondary: #f5f5f0;
    --bg-card: #ffffff;
    --text-primary: #1c1917;
    --text-secondary: #78716c;
    --accent-1: #0ea5e9;
    --accent-2: #e11d48;
    --accent-3: #d4d4d4;
    --font-display: 'Cormorant Garamond', serif;
    --font-body: 'Source Sans 3', sans-serif;
}
```
- **Fonts:** Cormorant Garamond + Source Sans 3 (Google) or Zodiak + General Sans (Fontshare)
- **Feel:** Refined, trustworthy, editorial
- **Best for:** Timelines, process flows, magazine layouts
- **Background:** Off-white or warm gray; avoid pure white
- **Cards:** Subtle box-shadow, thin borders, generous padding
- **Charts:** Single accent color with opacity variations

## Dark & Techy

```css
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: rgba(255, 255, 255, 0.04);
    --text-primary: #e4e4e7;
    --text-secondary: #71717a;
    --accent-1: #00ffcc;
    --accent-2: #a855f7;
    --accent-3: #0ea5e9;
    --font-display: 'JetBrains Mono', monospace;
    --font-body: 'Inter Tight', sans-serif;
}
```
- **Fonts:** JetBrains Mono + Inter Tight (Google) or Nippo + Switzer (Fontshare)
- **Feel:** Futuristic, technical, cutting-edge
- **Best for:** Tech articles, statistics, process flows
- **Background:** Near-black with subtle grid pattern or scanline overlay
- **Cards:** Glass-morphism (backdrop-blur + semi-transparent bg), neon border glow
- **Charts:** Neon accent colors with glow effects (box-shadow)

## Warm & Editorial

```css
:root {
    --bg-primary: #fef7ed;
    --bg-secondary: #fdf2e4;
    --bg-card: #fffbf5;
    --text-primary: #292524;
    --text-secondary: #78716c;
    --accent-1: #c2410c;
    --accent-2: #15803d;
    --accent-3: #b45309;
    --font-display: 'Fraunces', serif;
    --font-body: 'Outfit', sans-serif;
}
```
- **Fonts:** Fraunces + Outfit (Google) or Boska + Cabinet Grotesk (Fontshare)
- **Feel:** Warm, approachable, storytelling
- **Best for:** Editorial content, comparisons, listicles
- **Background:** Warm cream/paper tone; optional subtle noise texture
- **Cards:** Rounded corners, warm shadow, paper-like feel
- **Charts:** Earth tones with muted saturation

---

## Sci-fi HUD / Cyberpunk (Premium)

```css
:root {
    --bg-primary: #030308;
    --bg-secondary: #0a0f1e;
    --bg-card: rgba(10, 15, 30, 0.6);
    --text-primary: #e0e6ed;
    --text-secondary: #8892a0;
    --accent-1: #00f0ff;       /* cyan */
    --accent-2: #ff2d78;       /* magenta */
    --accent-3: #f0e040;       /* yellow */
    --glow-cyan: 0 0 10px rgba(0, 240, 255, 0.4), 0 0 20px rgba(0, 240, 255, 0.2);
    --glow-magenta: 0 0 10px rgba(255, 45, 120, 0.4), 0 0 20px rgba(255, 45, 120, 0.2);
    --font-display: 'Orbitron', sans-serif;
    --font-body: 'Rajdhani', sans-serif;
    --font-mono: 'Share Tech Mono', monospace;
}
```
- **Fonts:** Orbitron + Rajdhani + Share Tech Mono (Google)
- **Feel:** Futuristic HUD interface, sci-fi command center, cyberpunk terminal
- **Best for:** Tech audits, AI/ML articles, system architecture, data-heavy content
- **Background:** Near-black (#030308) with animated canvas particle system (nodes + connecting lines), CSS grid/scanline overlay
- **Cards:** Semi-transparent dark cards with cyan border glow, corner bracket HUD decorations (`::before`/`::after` pseudo-elements)
- **Charts:** Animated stripe progress bars with cyan fill, scan-line animation sweep
- **Special effects:** Canvas particle network (100+ particles with proximity lines), CSS scan-line overlay, fixed "SYSTEM STATUS: ONLINE" badge, neon text-shadow glow on headings
- **Section markers:** Magenta left-border on section headings, yellow for warnings
- **Timeline:** Vertical line with magenta dot markers, cyan phase titles

## Premium Magazine / Editorial (Premium)

```css
:root {
    --bg-primary: #f5f1eb;     /* cream */
    --bg-secondary: #1a1915;   /* charcoal */
    --bg-card: #ffffff;
    --text-primary: #1a1915;
    --text-secondary: #6b6b6b;
    --accent-1: #e83a2c;       /* vermillion red */
    --accent-2: #d4d0cb;       /* light gray */
    --font-display: 'Playfair Display', serif;
    --font-body: 'Libre Franklin', sans-serif;
    --font-mono: 'IBM Plex Mono', monospace;
}
```
- **Fonts:** Playfair Display (9rem hero!) + Libre Franklin + IBM Plex Mono (Google)
- **Feel:** Monocle/Bloomberg Businessweek editorial, luxury print magazine
- **Best for:** Reports, editorial content, business analysis, thought leadership
- **Background:** Alternating full-width cream (#f5f1eb) and charcoal (#1a1915) bands for dramatic contrast
- **Cards:** No visible card borders; content flows naturally with generous whitespace
- **Charts:** Single vermillion red accent against neutral tones; minimal CSS bars with red fill
- **Special effects:** Massive 9rem display typography for hero title, elegant Before/After comparison layout with vermillion vertical dividers, opacity-only fade animations (no transforms) for refined feel
- **Section markers:** Small-caps monospace labels ("IMPACT ANALYSIS", "RISK MATRIX") above italic serif headings
- **Timeline:** Red vertical line with labeled phases, clean and understated
- **3-color discipline:** Strictly cream + charcoal + vermillion — no other hues

## Glassmorphism / Aurora 3D (Premium)

```css
:root {
    --bg-primary: #0c0a14;     /* deep purple-black */
    --text-primary: #f0eef6;
    --text-secondary: #a09bb0;
    --accent-1: #a78bfa;       /* violet */
    --accent-2: #34d399;       /* emerald */
    --accent-3: #fb923c;       /* amber */
    --accent-warn: #f87171;    /* red */
    --glass-bg: rgba(255, 255, 255, 0.06);
    --glass-bg-hover: rgba(255, 255, 255, 0.09);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-border-hover: rgba(255, 255, 255, 0.18);
    --font-display: 'Sora', sans-serif;
    --font-body: 'DM Sans', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --font-quote: 'Playfair Display', serif;
}
```
- **Fonts:** Sora + DM Sans + JetBrains Mono + Playfair Display for pull quotes (Google)
- **Feel:** Frosted glass UI, Apple-inspired depth, aurora borealis atmosphere
- **Best for:** Modern tech, product showcases, startup content, creative reports
- **Background:** Deep purple-black (#0c0a14) with 4 animated aurora gradient blobs drifting over 18-25s cycles (violet, teal, coral, indigo), using CSS `filter: blur(120px)` for soft diffusion
- **Cards:** `backdrop-filter: blur(20px) saturate(1.5)` with `rgba(255,255,255,0.06)` background, subtle 1px white-alpha borders; hover raises opacity
- **Charts:** Gradient progress bars (violet→emerald) with CSS glow `box-shadow`, monospace value labels
- **Special effects:** Pulsing colored dots for risk indicators (red/amber/green), animated aurora blobs that drift continuously, gradient text for stat numbers, frosted timeline with gradient accent line
- **Section markers:** Semi-bold Sora headings with no decoration — glass cards provide visual separation
- **Color-coded statuses:** emerald = success, amber = warning, red = danger, violet = info

---

## Font Loading

Google Fonts example:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700&family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
```

Fontshare example:
```html
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=satoshi@300,400,500,700&display=swap" rel="stylesheet">
```

---

## Variation Guidelines

These presets are starting points. Vary them per infographic:
- Rotate accent colors (swap accent-1 and accent-2)
- Try alternative font pairings within the same mood
- Adjust background darkness/lightness
- Never produce two identical-looking infographics
