# Animation and Motion

## Duration Scale

| Interaction      | Duration    | Use When                       |
| ---------------- | ----------- | ------------------------------ |
| Hover effects    | 100-150ms   | Color, opacity, border changes |
| Button press     | 100ms       | Scale, background              |
| Dropdown open    | 150-200ms   | Appearing from trigger         |
| Tooltip show     | 150ms       | Delay 400ms before showing     |
| Modal open       | 200-250ms   | Scale + opacity animation      |
| Modal close      | 150-200ms   | Faster than open               |
| Page transition  | 300-500ms   | Cross-fade, slide              |
| Toast enter      | 200ms       | Slide in from edge             |
| Toast exit       | 150ms       | Fade out                       |
| Sidebar open     | 250-300ms   | Width + content reveal         |
| Accordion expand | 200-250ms   | Height animation               |
| Loading spinner  | 1000-1500ms | Full rotation                  |

Fast enough to feel instant. Slow enough to perceive movement. Never > 500ms for UI responses.

## Easing Functions

```css
/* Standard (enter + exit) — most interactions */
--ease-standard: cubic-bezier(0.4, 0, 0.2, 1);

/* Deceleration (entering the screen) */
--ease-decelerate: cubic-bezier(0, 0, 0.2, 1);

/* Acceleration (leaving the screen) */
--ease-accelerate: cubic-bezier(0.4, 0, 1, 1);

/* Emphasis (attention-grabbing, bouncy) */
--ease-emphasis: cubic-bezier(0.2, 0, 0, 1);

/* Spring-like (smooth overshoot) */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

### When to Use Which

- **Entering view** (dropdowns, modals, toasts) → decelerate
- **Leaving view** (closing, dismissing) → accelerate
- **State changes** (hover, toggle, tab switch) → standard
- **Micro-interactions** (button press, checkmark) → emphasis or spring

## Transition Patterns

### Hover

```css
.interactive {
  transition:
    background-color 150ms var(--ease-standard),
    color 150ms var(--ease-standard),
    border-color 150ms var(--ease-standard);
}
```

### Modal Enter/Exit

```css
@keyframes modal-enter {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes modal-exit {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.95);
  }
}

.modal {
  animation: modal-enter 250ms var(--ease-decelerate);
}
.modal.closing {
  animation: modal-exit 150ms var(--ease-accelerate);
}
```

### Dropdown

```css
@keyframes dropdown-enter {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown {
  animation: dropdown-enter 150ms var(--ease-decelerate);
}
```

### Toast Notification

```css
@keyframes toast-enter {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast {
  animation: toast-enter 200ms var(--ease-decelerate);
}
```

## Spring Animation (Framer Motion / React Spring)

```jsx
// Framer Motion
const springConfig = {
  type: "spring",
  stiffness: 300,
  damping: 30,
  mass: 1,
};

// Snappier (buttons, toggles)
const snappy = { stiffness: 500, damping: 35 };

// Gentle (modals, page transitions)
const gentle = { stiffness: 200, damping: 25 };

// Bouncy (playful elements)
const bouncy = { stiffness: 400, damping: 15 };
```

## Respect prefers-reduced-motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Reduced motion does NOT mean no motion. It means:

- Replace slide/scale with opacity-only
- Remove parallax and scroll-driven animations
- Keep essential state change feedback

## GPU Performance

**GPU-friendly (composite-only):** `transform`, `opacity`
**Triggers layout (avoid animating):** `width`, `height`, `margin`, `padding`, `top`, `left`
**Triggers paint (use sparingly):** `color`, `background`, `box-shadow`, `border`

```css
/* Promote to GPU layer */
.animated-element {
  will-change: transform; /* only when animation is imminent */
  transform: translateZ(0); /* force GPU layer */
}
```

Remove `will-change` after animation completes — don't leave it permanently.

## View Transitions API

```css
@view-transition {
  navigation: auto;
}

::view-transition-old(page) {
  animation: 250ms var(--ease-accelerate) fade-out;
}

::view-transition-new(page) {
  animation: 300ms var(--ease-decelerate) fade-in;
}
```

## Scroll-Driven Animations

```css
.parallax-element {
  animation: parallax linear;
  animation-timeline: scroll();
}

@keyframes parallax {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-50px);
  }
}
```

Use scroll-driven animations for: progress bars, parallax backgrounds, reveal-on-scroll. Not for critical UI feedback.

---

## Landing Page Animations

Production-tested keyframes from real landing pages. Full code in `real-world-patterns.md`.

### fadeInUpBlur (Scroll Entry)

```css
@keyframes fadeInUpBlur {
  from { opacity: 0; transform: translateY(24px); filter: blur(4px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}
.animate-entry { opacity: 0; animation: fadeInUpBlur 0.8s ease-out forwards; }
```

Trigger with IntersectionObserver (threshold: 0.1). Stagger with animation-delay (100ms increments, max 700ms).

### orbit-slow (AI Element Rotation)

```css
@keyframes orbit-slow {
  0% { transform: rotate(0deg) translateX(120px) rotate(0deg); }
  100% { transform: rotate(360deg) translateX(120px) rotate(-360deg); }
}
```

Max 3 orbiting elements. Respect `prefers-reduced-motion`.

### breathe-glow (AI Pulse)

```css
@keyframes breathe-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(79, 70, 229, 0.15); }
  50% { box-shadow: 0 0 40px rgba(79, 70, 229, 0.3); }
}
```

### flowData (SVG Stroke Animation)

```css
@keyframes flowData {
  to { stroke-dashoffset: -20; }
}
.data-path { stroke-dasharray: 8 12; animation: flowData 1.5s linear infinite; }
```

### Grayscale Hover Reveal

```css
.logo { filter: grayscale(100%) opacity(0.5); transition: all 300ms ease; }
.logo:hover { filter: grayscale(0%) opacity(1); }
```
