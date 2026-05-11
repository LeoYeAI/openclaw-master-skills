# Design System Reference

Default visual system for generated presentations. Users may override in their prompt or PLANNING.md.

## Style Preset Quick Reference

| Preset | Background | Primary Text | Accent | Best For |
|--------|-----------|-------------|--------|----------|
| **Bold Signal** | `#0A0A0A` | `#FFFFFF` | `#FF3D00` | Pitch decks, keynotes |
| **Electric Studio** | `#F5F5F5` | `#111111` | `#0052FF` | Agency, corporate |
| **Creative Voltage** | `#1A1A2E` | `#EAEAEA` | `#FFE600` | Retro-modern, creative |
| **Dark Botanical** | `#0F1C15` | `#E8E0D0` | `#C5A059` | Luxury, premium brands |
| **Notebook Tabs** | `#FBF7F0` | `#2C2C2C` | `#E84545` | Editorial, reports |
| **Pastel Geometry** | `#FDF6EE` | `#333333` | `#FF8FAB` | Friendly, product |
| **Neon Cyber** | `#080C14` | `#E0F0FF` | `#00FFCC` | Tech startups, dev tools |
| **Terminal Green** | `#0D1117` | `#30F030` | `#00FF41` | Developer, API docs |
| **Swiss Modern** | `#FFFFFF` | `#000000` | `#FF0000` | Corporate, data |
| **Paper & Ink** | `#F4EFE6` | `#1A1008` | `#8B4513` | Storytelling, literary |
| **Split Pastel** | `#FFF0F5` | `#2D2D2D` | `#A78BFA` | Creative agencies |
| **Vintage Editorial** | `#EDE8DF` | `#2A1810` | `#B85C00` | Personal brands, witty |

## Typography Pairings

Always use Google Fonts or Fontshare — never system fonts (Inter, Roboto, Arial, system-ui).

| Style | Display Font | Body Font | Import |
|-------|-------------|-----------|--------|
| Bold Signal | `Clash Display` | `Satoshi` | Fontshare |
| Dark Botanical | `Cormorant Garamond` | `DM Sans` | Google Fonts |
| Notebook Tabs | `Libre Baskerville` | `Lato` | Google Fonts |
| Swiss Modern | `Neue Haas Grotesk` | `Neue Haas Grotesk` | Fontshare |
| Terminal Green | `JetBrains Mono` | `JetBrains Mono` | Google Fonts |
| Vintage Editorial | `Playfair Display` | `Source Serif 4` | Google Fonts |
| Creative Voltage | `Space Grotesk` | `DM Mono` | Google Fonts |
| Neon Cyber | `Oxanium` | `Rajdhani` | Google Fonts |

**Font size scale (must use `clamp()`):**
```css
--title-size: clamp(2rem, 6vw, 5rem);
--h2-size: clamp(1.25rem, 3.5vw, 2.5rem);
--body-size: clamp(0.75rem, 1.5vw, 1.125rem);
--small-size: clamp(0.65rem, 1vw, 0.875rem);
```

**Chinese font fallback (always include):**
```css
font-family: var(--font-body), 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
```

## Slide Dimensions

- **Canvas**: 100vw × 100vh (scroll-snap, not fixed pixel)
- **Padding**: `clamp(1.5rem, 4vw, 4rem)`
- **Max content width**: `min(90vw, 1000px)`

## Animation Defaults

```css
/* Entrance animation */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Stagger delays */
.reveal:nth-child(1) { animation-delay: 0.1s; }
.reveal:nth-child(2) { animation-delay: 0.2s; }
.reveal:nth-child(3) { animation-delay: 0.3s; }
.reveal:nth-child(4) { animation-delay: 0.4s; }

/* Duration */
--duration-normal: 0.6s;
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
```

## Layout Rules

- **One key point per slide** + up to 5 supporting bullets
- **No text walls** — if > 60 words on a slide, split it
- **Every slide has a visual element** — icon, grid, chart, diagram, or color block
- **Footer** — include slide number on content slides
- **No scrolling** — slides must fit exactly in viewport (use `overflow: hidden`)

## Decorative Elements

```css
/* Background accent (low opacity) */
.accent-blob {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
  opacity: 0.15;
}

/* Card style */
.card {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Bullet marker (accent bar) */
li::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 1em;
  background: var(--accent);
  margin-right: 12px;
  border-radius: 2px;
  vertical-align: middle;
}
```
