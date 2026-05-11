# Aurora Mesh — Style Reference

Inspired by Linear.app, Vercel, and Stripe marketing pages. Animated multi-layer radial-gradient background creates a slowly drifting aurora effect on deep space black.

---

## Colors

```css
:root {
    --bg-primary:   #0a0a1a;
    --accent:       #00f5c4;                   /* cyan-green emphasis */
    --text-primary: #ffffff;
    --text-body:    rgba(255,255,255,0.70);
    --text-muted:   rgba(255,255,255,0.45);
    --card-bg:      rgba(255,255,255,0.05);
    --card-border:  rgba(255,255,255,0.10);
    --divider:      rgba(255,255,255,0.15);
}
```

---

## Background

```css
body {
    background-color: #0a0a1a;
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(120,40,200,0.40) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0,180,255,0.30) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 80%, rgba(0,255,180,0.20) 0%, transparent 50%);
    animation: auroraDrift 20s ease-in-out infinite alternate;
}

@keyframes auroraDrift {
    0%   { background-position: 0%   50%; }
    33%  { background-position: 50%  20%; }
    66%  { background-position: 80%  80%; }
    100% { background-position: 100% 50%; }
}
```

---

## Typography

```css
/* Title */
font-family: "Inter", "PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", system-ui, sans-serif;
font-weight: 700;
letter-spacing: -0.02em;
color: #ffffff;

/* Body */
font-family: "Inter", "PingFang SC", system-ui, sans-serif;
font-weight: 400;
color: rgba(255,255,255,0.70);
line-height: 1.7;
```

---

## Card Component

```css
/* Content card — subtle glass, doesn't compete with background aurora */
.aurora-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: clamp(1.2rem, 2.5vw, 2rem);
}

/* Accent line / divider */
.aurora-divider {
    height: 1px;
    background: rgba(255,255,255,0.15);
    margin: clamp(1rem, 2vw, 1.5rem) 0;
}

/* Accent text */
.aurora-accent {
    color: #00f5c4;
    font-weight: 600;
}

/* Pill badge */
.aurora-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    background: rgba(0,245,196,0.12);
    border: 1px solid rgba(0,245,196,0.30);
    border-radius: 9999px;
    font-size: clamp(0.65rem, 1vw, 0.75rem);
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #00f5c4;
}
```

---

## Layout

Centered single-column layout. No side panels. Content sits in centered cards over the full-bleed animated background.

```css
.aurora-slide {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: clamp(2rem, 5vw, 5rem);
    text-align: center;        /* title slides */
}

/* Content slides: left-aligned inside centered container */
.aurora-content {
    width: 100%;
    max-width: min(90vw, 800px);
    text-align: left;
}

/* Headline sizing */
.aurora-title {
    font-size: clamp(2.5rem, 7vw, 6rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.05;
    color: #ffffff;
}

.aurora-subtitle {
    font-size: clamp(1rem, 2vw, 1.4rem);
    color: rgba(255,255,255,0.70);
    margin-top: 1rem;
    line-height: 1.6;
}
```

---

## Animation

```css
/* Entrance: elements fade+rise with stagger */
.reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1),
                transform 0.7s cubic-bezier(0.16,1,0.3,1);
}
.slide.visible .reveal { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
.reveal:nth-child(4) { transition-delay: 0.35s; }
```

---

## Style Preview Checklist

When generating a preview for style selection, the preview MUST show:
- [ ] Animated aurora gradient background (visible motion within 3 seconds)
- [ ] Cyan-green `#00f5c4` accent on at least one element
- [ ] Subtle card with `backdrop-filter: blur(12px)`
- [ ] White headline with `letter-spacing: -0.02em`

---

## Best For

Product launches · VC pitch decks · SaaS marketing · AI / tech trend reports · Anything that should feel "Linear / Vercel-level" polished
