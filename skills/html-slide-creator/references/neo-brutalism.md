# Neo-Brutalism — Style Reference

Bold, uncompromising, anti-aesthetic. Hard edges, offset shadows, zero apology. Inspired by Gumroad's 2022 rebrand and indie developer culture.

---

## Colors

Choose one background per presentation — commit to it:

```css
:root {
    /* Option A: Yellow (most iconic neo-brutal) */
    --bg: #FFEB3B;

    /* Option B: Orange-red (aggressive) */
    --bg: #FF5733;

    /* Option C: Mint (softer but still brutal) */
    --bg: #E8F5E9;

    /* Option D: White (clean brutalism) */
    --bg: #FAFAFA;

    /* Always black text, no exceptions */
    --text: #000000;

    /* Inverse accent (for buttons, badges) */
    --btn-bg: #000000;
    --btn-text: #FFEB3B;   /* or var(--bg) */
}
```

---

## Signature Brutalist Effects

```css
/* The core brutalist card — hard shadow, zero radius */
.brute-card {
    background: #ffffff;
    border: 3px solid #000000;
    border-radius: 0;
    box-shadow: 4px 4px 0 #000000;
    padding: clamp(1rem, 2vw, 1.5rem);
}

/* On hover/focus: shadow shrinks, element shifts */
.brute-card:hover {
    transform: translate(2px, 2px);
    box-shadow: 2px 2px 0 #000000;
    transition: none;   /* instant — no easing in brutalism */
}

/* Stripe decoration (hatching) */
.brute-stripe {
    background: repeating-linear-gradient(
        -45deg,
        #000000 0px,
        #000000 2px,
        transparent 2px,
        transparent 10px
    );
    opacity: 0.15;
}

/* Slight rotation for handmade feel — apply sparingly */
.brute-rotated { transform: rotate(-1.5deg); }
.brute-rotated-right { transform: rotate(1deg); }

/* Button / badge */
.brute-btn {
    display: inline-block;
    background: #000000;
    color: #FFEB3B;   /* or var(--bg) */
    border: 3px solid #000000;
    border-radius: 0;
    box-shadow: 3px 3px 0 #000000;
    padding: 10px 20px;
    font-weight: 800;
    font-size: clamp(0.8rem, 1.2vw, 1rem);
    letter-spacing: 0.02em;
    cursor: pointer;
    text-transform: uppercase;
}

/* Tag / label */
.brute-tag {
    display: inline-block;
    background: #000000;
    color: var(--bg, #FFEB3B);
    border: 2px solid #000000;
    border-radius: 0;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
```

---

## Typography

```css
body {
    font-family: "Space Grotesk", "Plus Jakarta Sans", "PingFang SC",
                 "Noto Sans CJK SC", system-ui, sans-serif;
    background: var(--bg);
    color: #000000;
}

/* Display headline — very large, often uppercase */
.brute-title {
    font-size: clamp(3rem, 10vw, 9rem);
    font-weight: 900;
    line-height: 0.95;
    letter-spacing: -0.02em;
    text-transform: uppercase;
    color: #000000;
}

/* Section heading */
.brute-h2 {
    font-size: clamp(1.5rem, 4vw, 3.5rem);
    font-weight: 800;
    line-height: 1.05;
    color: #000000;
}

/* Body */
.brute-body {
    font-size: clamp(0.9rem, 1.5vw, 1.1rem);
    font-weight: 500;
    line-height: 1.5;
    color: #000000;
}
```

---

## Layout

```css
.brute-slide {
    background: var(--bg);
    padding: clamp(2rem, 4vw, 4rem);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;  /* bottom-anchored like editorial */
    position: relative;
    overflow: hidden;
}

/* Numbered list */
.brute-list { list-style: none; display: flex; flex-direction: column; gap: 0; }
.brute-list li {
    border-top: 2px solid #000;
    padding: 0.75rem 0;
    display: grid;
    grid-template-columns: 2.5rem 1fr;
    gap: 0.75rem;
    align-items: start;
}
.brute-list li:last-child { border-bottom: 2px solid #000; }
.brute-list .num {
    font-size: 0.75rem;
    font-weight: 800;
    padding-top: 0.15em;
}
```

---

## Arrow Decoration (SVG, inline)

```html
<!-- Simple hand-drawn style arrow pointing right -->
<svg width="60" height="24" viewBox="0 0 60 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M0 12 H52 M40 4 L52 12 L40 20" stroke="#000" stroke-width="3" stroke-linecap="square"/>
</svg>
```

---

## Animation

```css
/* No transitions. No easing. Brutalism is instant. */
/* Only exception: entrance reveal (subtle) */
.reveal {
    opacity: 0;
    transition: opacity 0.2s linear;
}
.slide.visible .reveal { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.0s; }
.reveal:nth-child(2) { transition-delay: 0.05s; }
.reveal:nth-child(3) { transition-delay: 0.10s; }
```

---

## Style Preview Checklist

- [ ] High-saturation solid background (yellow / orange / mint)
- [ ] `3px solid #000` border + `4px 4px 0 #000` shadow visible on at least one card
- [ ] Headline at 900 weight, very large, uppercase
- [ ] All text is `#000000` — no exceptions
- [ ] Zero border-radius on structural elements

---

## Best For

Hackathon presentations · Indie product launches · Design manifestos · Creative agency pitches · Anti-corporate brand statements · Developer conference talks
