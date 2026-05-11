# Japanese Zen — Style Reference

Still, focused, contemplative. Inspired by Kenya Hara's design philosophy, MUJI's visual system, and Japanese architectural photography. Emptiness (Ma, 間) is the primary design element.

---

## Colors

```css
/* Light variant — warm paper white */
:root {
    --bg:           #FAFAF8;
    --text:         #1a1a18;   /* warm ink, not pure black */
    --text-muted:   #6b6b68;
    --accent:       #C41E3A;   /* vermilion — use ONCE per slide, maximum */
    --accent-alt:   #1B3A6B;   /* indigo — alternative accent */
    --rule:         rgba(26,26,24,0.15);
}

/* Dark variant — warm ink black */
:root.zen-dark {
    --bg:           #1a1a18;
    --text:         #f0ede8;
    --text-muted:   #9a9790;
    --rule:         rgba(240,237,232,0.15);
}
```

**Forbidden:** gradients, multiple accent colors, high-saturation color blocks, decorative borders, drop shadows.

---

## Typography

```css
/* Chinese — Noto Serif CJK SC preferred, graceful serif fallback */
.zen-cn {
    font-family: "Noto Serif CJK SC", "Source Han Serif SC",
                 "STSong", "SimSun", Georgia, serif;
    font-feature-settings: "palt";   /* CJK punctuation compression */
    font-weight: 300;
    line-height: 1.9;
    letter-spacing: 0.05em;
}

/* English — EB Garamond or Crimson Text */
.zen-en {
    font-family: "EB Garamond", "Crimson Text", Georgia, serif;
    font-weight: 400;
    line-height: 1.85;
}

/* Title — slightly heavier but still restrained */
.zen-title {
    font-size: clamp(1.8rem, 5vw, 4rem);
    font-weight: 400;   /* never bold */
    letter-spacing: 0.08em;
    line-height: 1.3;
    color: var(--text);
}

/* Body */
.zen-body {
    font-size: clamp(0.9rem, 1.6vw, 1.15rem);
    font-weight: 300;
    line-height: 1.9;
    color: var(--text);
}

/* Accent word — accent color, nothing else changes */
.zen-accent { color: var(--accent); }

/* Caption / label */
.zen-caption {
    font-size: clamp(0.65rem, 1vw, 0.8rem);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
}
```

---

## Layout — Ma (間) Philosophy

```css
.zen-slide {
    background: var(--bg);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: clamp(3rem, 8vw, 8rem) clamp(2rem, 6vw, 6rem);
}

/* Narrow content column — max 600px regardless of screen width */
.zen-content {
    width: 100%;
    max-width: 600px;
}

/* Generous top margin above every heading */
.zen-heading {
    margin-top: clamp(60px, 8vh, 100px);
}

/* Paragraph spacing */
.zen-body + .zen-body {
    margin-top: 40px;
}
```

---

## Decorative Elements (max 1 per slide)

```css
/* 1. Thin horizontal rule with flanking dots */
.zen-rule {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: clamp(1.5rem, 3vh, 2.5rem) 0;
}
.zen-rule::before,
.zen-rule::after {
    content: '';
    width: 4px; height: 4px;
    border-radius: 50%;
    background: var(--rule);
    flex-shrink: 0;
}
.zen-rule-line {
    flex: 1;
    height: 1px;
    background: var(--rule);
}

/* 2. Ghost kanji background character */
.zen-ghost-kanji {
    position: absolute;
    font-size: clamp(120px, 25vw, 240px);
    font-weight: 900;
    color: var(--text);
    opacity: 0.06;
    pointer-events: none;
    user-select: none;
    font-family: "Noto Serif CJK SC", "STSong", serif;
    line-height: 1;
    /* Position off-center for asymmetric composition */
    right: -0.1em;
    bottom: -0.1em;
}

/* 3. Single vertical line */
.zen-vline {
    width: 1px;
    height: clamp(40px, 8vh, 80px);
    background: var(--rule);
    margin: 0 auto;
}
```

---

## Vertical Title (optional variant)

```css
/* Writing mode vertical — for title slides */
.zen-vertical-title {
    writing-mode: vertical-rl;
    text-orientation: mixed;
    font-size: clamp(2rem, 6vw, 5rem);
    font-weight: 400;
    letter-spacing: 0.15em;
    line-height: 1.2;
    color: var(--text);
}
```

---

## Animation

```css
/* Slow, gentle opacity fade — no movement */
.reveal {
    opacity: 0;
    transition: opacity 0.8s ease;
}
.slide.visible .reveal { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal:nth-child(2) { transition-delay: 0.3s; }
.reveal:nth-child(3) { transition-delay: 0.5s; }
.reveal:nth-child(4) { transition-delay: 0.7s; }
```

---

## Chinese Font Loading

```html
<!-- Noto Serif CJK SC via Google Fonts (preconnect first) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400&display=swap" rel="stylesheet">
```

---

## Style Preview Checklist

- [ ] Warm cream `#FAFAF8` or ink `#1a1a18` background — no color other than accent
- [ ] Content column clearly narrow (max 600px, lots of horizontal breathing room)
- [ ] Line height ≥ 1.8 visible in body text
- [ ] Maximum ONE decorative element (rule, ghost kanji, or dot)
- [ ] Accent color used on ONE word or element only

---

## Best For

Brand philosophy presentations · Design thinking talks · Cultural storytelling · Product principle documents · East Asian audience contexts · Any talk where silence communicates as much as words
