# Design Philosophy — Anti-AI-Slop Manifesto

This reference extends the core SKILL.md with deeper guidance on creating distinctive designs.

## The Problem: AI Slop

Generic AI-generated designs share these telltale signs:

### Typography Sins
- Inter, Roboto, Arial everywhere
- Timid weight ranges (400-600 only)
- Minimal size progression (1.25x-1.5x)
- No distinctive pairing strategy

### Color Crimes
- Purple/blue gradient on white (the cardinal sin)
- 5+ evenly-distributed colors with no hierarchy
- Muted, "safe" palettes that offend no one and delight no one
- Gray backgrounds that signal "I gave up"

### Layout Laziness
- Everything centered
- Perfectly symmetrical
- Predictable card grids
- No visual tension or interest

### Motion Mediocrity
- No animations at all, OR
- Generic fade-in on every element
- No orchestration or timing consideration

### Background Boredom
- Solid white
- Solid light gray
- Maybe a subtle gradient if feeling "bold"

---

## The Solution: Intentional Design

### Commit to an Extreme

The middle ground is where designs go to die. Pick a direction and push it:

**Maximalism Done Right**:
- Dense, layered compositions
- Overlapping elements with clear hierarchy
- Rich textures and patterns
- Multiple animations coordinated
- Every pixel working

**Minimalism Done Right**:
- Extreme restraint (3 colors max)
- Typography as the star
- Negative space as intentional element
- Single, perfect animation
- Nothing extraneous

Both require courage. Both create memorable designs.

### Typography as Identity

Typography isn't decoration — it's the voice of the design.

**Building a Type Hierarchy**:
```css
/* Display: Make a statement */
.display {
  font-family: 'Clash Display', sans-serif;
  font-size: clamp(3rem, 8vw, 6rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1;
}

/* Heading: Support the display */
.heading {
  font-family: 'Satoshi', sans-serif;
  font-size: clamp(1.5rem, 3vw, 2.5rem);
  font-weight: 500;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

/* Body: Effortless reading */
.body {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.6;
}

/* Mono: Technical credibility */
.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  letter-spacing: 0;
}
```

**Font Pairing Strategies**:

| Strategy | Display | Body | Effect |
|----------|---------|------|--------|
| Contrast | Serif (Playfair) | Sans (Inter... no, Plus Jakarta) | Editorial elegance |
| Harmony | Geometric (Satoshi) | Geometric (General Sans) | Modern consistency |
| Tension | Brutalist (Clash) | Humanist (Source Sans) | Edgy but readable |
| Technical | Mono (JetBrains) | Sans (IBM Plex Sans) | Developer-focused |

### Color as Emotion

Color isn't about "what looks nice" — it's about what the design FEELS.

**Building a Palette**:

```css
/* Dark, Confident, Premium */
:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #171717;
  --bg-tertiary: #262626;
  --text-primary: #fafafa;
  --text-secondary: #a3a3a3;
  --accent: #22c55e;  /* Confident green */
  --accent-subtle: rgba(34, 197, 94, 0.1);
}

/* Light, Warm, Approachable */
:root {
  --bg-primary: #fffbf5;
  --bg-secondary: #fff7ed;
  --bg-tertiary: #ffedd5;
  --text-primary: #1c1917;
  --text-secondary: #78716c;
  --accent: #ea580c;  /* Warm orange */
  --accent-subtle: rgba(234, 88, 12, 0.1);
}

/* High Contrast, Editorial */
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #000000;
  --text-secondary: #525252;
  --accent: #dc2626;  /* Bold red */
  --accent-subtle: rgba(220, 38, 38, 0.05);
}
```

**The 60-30-10 Rule**:
- 60% dominant (background)
- 30% secondary (cards, sections)
- 10% accent (CTAs, highlights)

### Motion as Narrative

Animation tells a story. What's your story?

**Page Load Orchestration**:
```css
/* Hero elements enter in sequence */
.hero-badge {
  animation: fadeSlideUp 0.6s ease-out 0.1s both;
}
.hero-title {
  animation: fadeSlideUp 0.6s ease-out 0.2s both;
}
.hero-subtitle {
  animation: fadeSlideUp 0.6s ease-out 0.3s both;
}
.hero-cta {
  animation: fadeSlideUp 0.6s ease-out 0.4s both;
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Scroll-Triggered Reveals**:
```javascript
// Intersection Observer for scroll animations
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

**Hover States That Surprise**:
```css
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.05);
}

/* Or more dramatic */
.card:hover {
  transform: scale(1.02) rotate(-0.5deg);
}
```

### Backgrounds as Atmosphere

The background sets the mood before any content is read.

**Gradient Mesh**:
```css
.gradient-mesh {
  background: 
    radial-gradient(at 40% 20%, hsla(28, 100%, 74%, 0.3) 0px, transparent 50%),
    radial-gradient(at 80% 0%, hsla(189, 100%, 56%, 0.2) 0px, transparent 50%),
    radial-gradient(at 0% 50%, hsla(355, 100%, 93%, 0.3) 0px, transparent 50%),
    radial-gradient(at 80% 50%, hsla(340, 100%, 76%, 0.2) 0px, transparent 50%),
    radial-gradient(at 0% 100%, hsla(269, 100%, 77%, 0.3) 0px, transparent 50%);
}
```

**Noise Texture**:
```css
.noise::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  opacity: 0.03;
  pointer-events: none;
  z-index: 1000;
}
```

**Dot Pattern**:
```css
.dots {
  background-image: radial-gradient(circle, #333 1px, transparent 1px);
  background-size: 20px 20px;
}
```

**Glassmorphism**:
```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

---

## Design Decision Framework

When stuck, ask these questions:

1. **What's the ONE thing?** — If users remember one element, what is it?
2. **Would I screenshot this?** — Is there a moment worth sharing?
3. **Does it feel designed?** — Or does it feel generated?
4. **What's the emotion?** — Confident? Playful? Serious? Luxurious?
5. **Is it brave?** — Did I play it safe or commit to a direction?

---

## Anti-Pattern Detection

Before shipping, scan for these:

| Anti-Pattern | Fix |
|--------------|-----|
| Inter font | Replace with distinctive alternative |
| Purple gradient | Choose contextual palette |
| All centered | Add asymmetry or left-align |
| No animations | Add orchestrated page load |
| Solid background | Add texture, gradient, or pattern |
| Evenly spaced colors | Apply 60-30-10 rule |
| Generic cards | Add unique styling treatment |
| Default shadows | Use layered, atmospheric shadows |

---

*Remember: Claude is capable of extraordinary creative work. Don't hold back.*
