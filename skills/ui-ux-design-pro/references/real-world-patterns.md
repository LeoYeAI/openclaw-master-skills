# Real-World Patterns

Production-tested patterns extracted from AI SaaS and Hardware Product landing pages. Higher fidelity than synthetic rules — these patterns shipped in real products.

---

## 1. Frosted Navigation

Sticky nav with semi-transparent background and blur. Maintains context without blocking content.

```css
.nav-frosted {
  position: sticky;
  top: 0;
  z-index: 50;
  background: oklch(1 0 0 / 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid oklch(0 0 0 / 0.06);
}
```

```html
<!-- Tailwind -->
<nav
  class="sticky top-0 z-50 bg-white/80 backdrop-blur-xl
            border-b border-slate-200/60 saturate-[180%]"
></nav>
```

**When to use:** Premium landing pages, SaaS dashboards, content-heavy pages where scroll context matters.

**Anti-patterns:** Don't use on short single-screen pages. Don't stack multiple sticky elements. Don't exceed 64px height.

---

## 2. Numbered Section Headers

Monospace counter labels with gradient dividers before section titles. Establishes progression and professionalism.

```html
<div class="flex items-center gap-3 mb-6">
  <span class="text-[10px] font-mono text-indigo-400 tracking-widest">01</span>
  <span
    class="h-px flex-1 bg-gradient-to-r from-indigo-200 to-transparent"
  ></span>
</div>
<h2 class="font-manrope text-4xl font-bold text-slate-900">Section Title</h2>
<p class="text-lg text-slate-500 font-light mt-4">Description text</p>
```

**When to use:** Feature-rich landing pages, multi-section showcases, educational platforms, product tours.

**Anti-patterns:** Don't use more than 8 numbered sections. Don't use on single-section pages. Don't number footer or nav.

---

## 3. Staggered Entry Animation

IntersectionObserver-triggered entries with cascading delays. Creates choreographed reveals.

```css
@keyframes fadeInUpBlur {
  from {
    opacity: 0;
    transform: translateY(24px);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

.animate-entry {
  opacity: 0;
  animation: fadeInUpBlur 0.8s ease-out forwards;
}

.animate-entry.delay-1 {
  animation-delay: 100ms;
}
.animate-entry.delay-2 {
  animation-delay: 200ms;
}
.animate-entry.delay-3 {
  animation-delay: 300ms;
}
.animate-entry.delay-4 {
  animation-delay: 400ms;
}
.animate-entry.delay-5 {
  animation-delay: 500ms;
}
.animate-entry.delay-6 {
  animation-delay: 600ms;
}
.animate-entry.delay-7 {
  animation-delay: 700ms;
}
```

```js
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.1 },
);

document
  .querySelectorAll(".animate-on-scroll")
  .forEach((el) => observer.observe(el));
```

**When to use:** Landing page sections, feature grids, testimonial carousels, pricing cards.

**Anti-patterns:** Don't stagger more than 7 items. Don't exceed 700ms total delay. Respect `prefers-reduced-motion`. Don't re-trigger on scroll up.

---

## 4. Mesh Gradient Backgrounds

Multi-point radial gradients creating ambient color fields. Adds warmth without visual clutter.

```css
.mesh-gradient {
  background:
    radial-gradient(
      ellipse at 20% 50%,
      rgba(255, 127, 80, 0.15),
      transparent 50%
    ),
    radial-gradient(
      ellipse at 80% 20%,
      rgba(255, 127, 80, 0.1),
      transparent 50%
    ),
    radial-gradient(
      ellipse at 40% 80%,
      rgba(255, 200, 150, 0.08),
      transparent 50%
    ),
    radial-gradient(
      ellipse at 70% 60%,
      rgba(255, 127, 80, 0.05),
      transparent 50%
    );
  background-color: #ffffff;
}
```

**When to use:** Hero sections, page backgrounds, feature showcases. Works best with warm or brand colors.

**Anti-patterns:** Don't exceed 4 gradient points. Keep opacity below 0.2 per point. Don't animate mesh gradients (performance). Don't use on text-heavy sections — reduces readability.

---

## 5. Bento Grid Layout

Asymmetric card grid with mixed aspect ratios. Showcases features with visual hierarchy through card sizing.

```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto;
  gap: 16px;
}

.bento-card-wide {
  grid-column: span 2;
}

.bento-card-tall {
  grid-row: span 2;
}

.bento-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 32px;
  border: 1px solid oklch(0 0 0 / 0.06);
  overflow: hidden;
}
```

```html
<!-- Tailwind -->
<div class="grid grid-cols-4 gap-4">
  <div class="col-span-2 bg-white rounded-3xl p-8 border">Wide card</div>
  <div class="bg-white rounded-3xl p-8 border">Standard card</div>
  <div class="row-span-2 bg-white rounded-3xl p-8 border">Tall card</div>
  <div class="col-span-2 bg-white rounded-3xl p-8 border">Another wide</div>
  <div class="bg-white rounded-3xl p-8 border">Standard card</div>
</div>
```

**When to use:** Product feature showcases, hardware/software landing pages, app previews, portfolio grids.

**Anti-patterns:** Don't exceed 6 cards total. Don't make all cards the same size (defeats purpose). Stack to single column on mobile. Don't nest bento grids.

---

## 6. Brand-Tinted Shadows

Shadows using brand color at low opacity instead of generic black/gray. Adds personality to depth.

```css
.card-brand-shadow {
  box-shadow: 0 8px 32px rgba(255, 127, 80, 0.15);
}

.card-brand-shadow:hover {
  box-shadow: 0 12px 48px rgba(255, 127, 80, 0.25);
}
```

```html
<!-- Tailwind -->
<div
  class="shadow-[0_8px_32px_rgba(255,127,80,0.15)]
            hover:shadow-[0_12px_48px_rgba(255,127,80,0.25)]
            transition-shadow duration-300"
></div>
```

**When to use:** Hero cards, CTA buttons, featured content, pricing cards. Best with warm or vibrant brand colors.

**Anti-patterns:** Don't use brand shadows on every element. Keep opacity 0.1-0.3. Don't use on dark backgrounds (invisible). Don't combine with generic shadows.

---

## 7. Orbit Animation

360° rotation for orbiting satellite elements around a central node. Conveys AI/tech intelligence.

```css
@keyframes orbit-slow {
  0% {
    transform: rotate(0deg) translateX(120px) rotate(0deg);
  }
  100% {
    transform: rotate(360deg) translateX(120px) rotate(-360deg);
  }
}

.orbit-element {
  animation: orbit-slow 20s linear infinite;
  position: absolute;
  top: 50%;
  left: 50%;
}
```

**When to use:** AI product hero sections, tech feature cards, loading states, dashboard decorative elements.

**Anti-patterns:** Max 3 orbiting elements. Don't orbit text (unreadable). Respect `prefers-reduced-motion`. Don't combine with scroll animations.

---

## 8. Logo/Client Strip

Horizontal row of partner/client logos with grayscale-to-color hover reveal. Social proof pattern.

```css
.logo-strip {
  display: flex;
  align-items: center;
  gap: 48px;
  justify-content: center;
  flex-wrap: wrap;
}

.logo-strip img {
  height: 32px;
  filter: grayscale(100%) opacity(0.5);
  transition: all 300ms ease;
}

.logo-strip img:hover {
  filter: grayscale(0%) opacity(1);
}
```

```html
<!-- Tailwind -->
<div class="flex items-center gap-12 justify-center flex-wrap py-12">
  <img
    src="logo1.svg"
    class="h-8 grayscale opacity-50
       hover:grayscale-0 hover:opacity-100 transition-all duration-300"
  />
</div>
```

**When to use:** Below hero sections, before pricing, after testimonials. Minimum 4 logos, maximum 8.

**Anti-patterns:** Don't use colored logos by default (distracts from content). Don't make logos too large (competing with content). Don't use on pages without social proof value.

---

## 9. Lock/Unlock Feature Card

CSS transition between locked (shimmer/preview) and unlocked (full color) states. Creates anticipation.

```css
@keyframes shimmer-lock {
  0%,
  100% {
    opacity: 0.5;
    border-color: oklch(0.8 0.02 260);
  }
  50% {
    opacity: 0.7;
    border-color: oklch(0.7 0.05 260);
  }
}

.card-locked {
  animation: shimmer-lock 3s ease-in-out infinite;
  filter: grayscale(30%);
  pointer-events: none;
}

.card-unlocked {
  animation: none;
  filter: none;
  pointer-events: auto;
  transition: all 500ms ease;
}
```

**When to use:** Feature previews, certification paths, gamified UIs, roadmap steps, premium content teasers.

**Anti-patterns:** Don't lock more than 50% of cards. Always show unlock criteria. Don't use for essential UI elements.

---

## 10. Premium CTA Patterns

Two CTA strategies from production:

### Strategy A: Gradient CTA (Cool/Tech brands)

```html
<a
  class="bg-gradient-to-r from-indigo-600 to-indigo-500 text-white
          font-medium rounded-full px-6 py-2.5 shadow-sm
          hover:shadow-lg hover:shadow-indigo-500/25
          transition-all duration-300
          inline-flex items-center gap-2"
>
  Get Started
  <svg><!-- arrow-right icon --></svg>
</a>
```

### Strategy B: Solid Warm CTA (Warm/Premium brands)

```html
<a
  class="bg-[#FF7F50] text-white
          font-semibold rounded-[32px] px-8 py-3
          shadow-[0_4px_16px_rgba(255,127,80,0.3)]
          hover:shadow-[0_8px_32px_rgba(255,127,80,0.4)]
          hover:-translate-y-0.5
          transition-all duration-300
          inline-flex items-center gap-2"
>
  Order Now
  <svg><!-- arrow-right icon --></svg>
</a>
```

**When to use:** Primary actions on landing pages. Gradient for tech/SaaS. Solid warm for hardware/consumer.

**Anti-patterns:** Never use both strategies on the same page. Always include right-arrow icon for primary CTAs. Don't exceed 2 CTA variants (primary + secondary ghost) per section.
