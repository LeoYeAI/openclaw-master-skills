# Glassmorphism — Style Reference

Light, translucent, and modern. Inspired by Apple WWDC slides and iOS Control Center. Frosted glass cards float over a colorful blurred-orb background.

---

## Background Options

```css
/* Option A — Cool (purple to pink) */
.bg-cool {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

/* Option B — Warm (pink to ocean) */
.bg-warm {
    background: linear-gradient(135deg, #f8cdda 0%, #a6c1ee 50%, #1d6fa4 100%);
}

/* Option C — Mint (fresh, product feel) */
.bg-mint {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 50%, #a8edea 100%);
}
```

**Blurred color orbs (required — backdrop-filter only works if there's something behind the card):**

```css
.glass-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
}
/* Example orb placements */
.orb-1 { width: 400px; height: 400px; background: rgba(102,126,234,0.5); top: -10%; left: -5%; }
.orb-2 { width: 300px; height: 300px; background: rgba(240,147,251,0.4); bottom: -5%; right: -5%; }
.orb-3 { width: 250px; height: 250px; background: rgba(168,237,234,0.4); top: 30%; right: 15%; }
```

---

## Card Components

```css
/* Primary glass card */
.glass-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.10);
    padding: clamp(1.2rem, 2.5vw, 2rem);
}

/* Secondary glass card (list items, smaller blocks) */
.glass-card-sm {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px) saturate(1.3);
    -webkit-backdrop-filter: blur(12px) saturate(1.3);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
}

/* Dark text variant (on lighter backgrounds) */
.glass-card.dark-text { color: #1a1a2e; }

/* Light text variant (on darker backgrounds) */
.glass-card.light-text { color: rgba(255,255,255,0.92); }
```

---

## Typography

```css
/* System font stack — SF Pro feel on Apple, Segoe on Windows */
body {
    font-family: -apple-system, "SF Pro Display", BlinkMacSystemFont,
                 "PingFang SC", "Noto Sans CJK SC", "Segoe UI", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}

.glass-title {
    font-size: clamp(2rem, 6vw, 5rem);
    font-weight: 700;
    letter-spacing: -0.01em;
    line-height: 1.1;
    /* Choose dark or light based on background */
    color: #1a1a2e;   /* or rgba(255,255,255,0.95) */
}

.glass-body {
    font-size: clamp(0.85rem, 1.5vw, 1.1rem);
    line-height: 1.65;
    color: rgba(30, 30, 60, 0.80);   /* or rgba(255,255,255,0.80) */
}

/* Icon-style circular badge */
.glass-icon-wrap {
    width: clamp(2rem, 4vw, 3rem);
    height: clamp(2rem, 4vw, 3rem);
    border-radius: 50%;
    border: 1.5px solid rgba(255,255,255,0.5);
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.2);
    font-size: 1.1em;
}
```

---

## Layout

```css
/* Centered single column — title slides */
.glass-slide-center {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    padding: clamp(2rem, 5vw, 5rem);
    position: relative; overflow: hidden;
}

/* Content grid — feature cards */
.glass-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr));
    gap: clamp(0.75rem, 1.5vw, 1.2rem);
}
```

---

## Animation

```css
/* Gentle float entrance */
.reveal {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.34,1.2,0.64,1);
}
.slide.visible .reveal { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.08s; }
.reveal:nth-child(2) { transition-delay: 0.18s; }
.reveal:nth-child(3) { transition-delay: 0.28s; }
.reveal:nth-child(4) { transition-delay: 0.38s; }
```

---

## PPTX Export Note

When this style is used and the user requests PPTX export, add a note in the speaker notes of slide 1:

> **Export note:** The glassmorphism backdrop-filter effect is browser-only. In the PPTX export, glass cards will appear as flat semi-transparent fills. Consider adjusting card opacity to `rgba(255,255,255,0.70)` before exporting for best results.

---

## Style Preview Checklist

- [ ] Colorful gradient or multi-orb background is visible
- [ ] At least one card with `backdrop-filter: blur(20px)` clearly showing the frosted effect
- [ ] `1px solid rgba(255,255,255,0.30)` border visible on cards
- [ ] Blurred orbs are placed behind the card (not overlapping it)

---

## Best For

Consumer product launches · Brand identity presentations · Creative tool demos · Design portfolio · Any context where the visual design IS the message
