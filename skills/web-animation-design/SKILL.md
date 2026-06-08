---
name: web-animation-design
description: "Design and implement web animations that feel natural and purposeful. Use this skill proactively whenever the user asks questions about animations, motion, easing, timing, duration, springs, transitions, or animation performance. This includes questions about how to animate specific UI elements, which easing to use, animation best practices, or accessibility considerations for motion. Triggers on: easing, ease-out, ease-in, ease-in-out, cubic-bezier, bounce, spring physics, keyframes, transform, opacity, fade, slide, scale, hover effects, microinteractions, Framer Motion, React Spring, GSAP, CSS transitions, entrance/exit animations, page transitions, stagger, will-change, GPU acceleration, prefers-reduced-motion, modal/dropdown/tooltip/popover/drawer animations, gesture animations, drag interactions, button press feel, feels janky, make it smooth."
metadata:
  short-description: Design and implement web animations that feel natural and purposeful
---

# Web Animation Design

## ⚠️ Creative Pack — NOT auto-apply

This skill is part of the creative pack. Use when the task explicitly involves animation, motion, or interaction feel. Do NOT load this for general UI building — the motion reference in design-review covers baseline motion quality.

**Use when:** user asks about animations, easing, springs, transitions, interaction feel, or "make it smooth."
**Skip when:** building standard UI where the motion reference in design-review is sufficient.

A comprehensive guide for creating animations that feel right, based on Emil Kowalski's "Animations on the Web" course.

## Initial Response

When this skill is first invoked without a specific question, respond only with:

> I'm ready to help you with animations based on Emil Kowalski's animations.dev course.

Do not provide any other information until the user asks a question.

## Review Format (Required)

When reviewing animations, you MUST use a markdown table. Do NOT use a list with "Before:" and "After:" on separate lines. Always output an actual markdown table like this:

| Before                            | After                                           |
| --------------------------------- | ----------------------------------------------- |
| `transform: scale(0)`             | `transform: scale(0.95)`                        |
| `animation: fadeIn 400ms ease-in` | `animation: fadeIn 200ms ease-out`              |
| No reduced motion support         | `@media (prefers-reduced-motion: reduce) {...}` |

Wrong format (never do this):

```
Before: transform: scale(0)
After: transform: scale(0.95)
────────────────────────────
Before: 400ms duration
After: 200ms
```

Correct format: A single markdown table with | Before | After | columns, one row per issue.

## Decision Tree: What Tool Do I Use?

```
Does this involve layout changes, shared transitions, or exit animations in React?
├── Yes → Framer Motion (layout animations, AnimatePresence, layoutId)
│         Import from "motion/react" (NOT "framer-motion")
└── No
    ├── Is it a simple enter/exit or hover? → CSS transitions/keyframes
    ├── Is it performance-critical (heavy page, many elements)? → CSS (hardware-accelerated)
    ├── Does it need spring physics or interruptibility? → Framer Motion
    ├── Does it need gesture tracking (drag, cursor follow)? → FM motion values
    └── Is it a constant-speed loop? → CSS keyframes
```

Always check `prefers-reduced-motion`. No exceptions.

## Quick Start

Every animation decision starts with these questions:

1. **Is this element entering or exiting?** → Use `ease-out`
2. **Is an on-screen element moving?** → Use `ease-in-out`
3. **Is this a hover/color transition?** → Use `ease`
4. **Will users see this 100+ times daily?** → Don't animate it

## The Easing Blueprint

### ease-out (Most Common)

Use for **user-initiated interactions**: dropdowns, modals, tooltips, any element entering or exiting the screen.

```css
/* Sorted weak to strong */
--ease-out-quad: cubic-bezier(0.25, 0.46, 0.45, 0.94);
--ease-out-cubic: cubic-bezier(0.215, 0.61, 0.355, 1);
--ease-out-quart: cubic-bezier(0.165, 0.84, 0.44, 1);
--ease-out-quint: cubic-bezier(0.23, 1, 0.32, 1);
--ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
--ease-out-circ: cubic-bezier(0.075, 0.82, 0.165, 1);
```

Why it works: Acceleration at the start creates an instant, responsive feeling. The element "jumps" toward its destination then settles in.

### ease-in-out (For Movement)

Use when **elements already on screen need to move or morph**. Mimics natural motion like a car accelerating then braking.

```css
/* Sorted weak to strong */
--ease-in-out-quad: cubic-bezier(0.455, 0.03, 0.515, 0.955);
--ease-in-out-cubic: cubic-bezier(0.645, 0.045, 0.355, 1);
--ease-in-out-quart: cubic-bezier(0.77, 0, 0.175, 1);
--ease-in-out-quint: cubic-bezier(0.86, 0, 0.07, 1);
--ease-in-out-expo: cubic-bezier(1, 0, 0, 1);
--ease-in-out-circ: cubic-bezier(0.785, 0.135, 0.15, 0.86);
```

### ease (For Hover Effects)

Use for **hover states and color transitions**. The asymmetrical curve (faster start, slower end) feels elegant for gentle animations.

```css
transition: background-color 150ms ease;
```

### linear (Avoid in UI)

Only use for:

- Constant-speed animations (marquees, tickers)
- Time visualization (hold-to-delete progress indicators)

Linear feels robotic and unnatural for interactive elements.

### ease-in (Almost Never)

**Avoid for UI animations.** Makes interfaces feel sluggish because the slow start delays visual feedback.

### Paired Elements Rule

Elements that animate together must use the same easing and duration. Modal + overlay, tooltip + arrow, drawer + backdrop—if they move as a unit, they should feel like a unit.

```css
/* Both use the same timing */
.modal {
  transition: transform 200ms ease-out;
}
.overlay {
  transition: opacity 200ms ease-out;
}
```

## Timing and Duration

## Duration Guidelines

| Element Type                      | Duration  |
| --------------------------------- | --------- |
| Micro-interactions                | 100-150ms |
| Standard UI (tooltips, dropdowns) | 150-250ms |
| Modals, drawers                   | 200-300ms |

**Rules:**
- UI animations should stay under 300ms
- Larger elements animate slower than smaller ones
- Exit animations can be ~20% faster than entrance
- Match duration to distance - longer travel = longer duration

### The Frequency

Determine how often users will see the animation:

- **100+ times/day** → No animation (or drastically reduced)
- **Occasional use** → Standard animation
- **Rare/first-time** → Can be more special

**Example:** Raycast never animates because users open it hundreds of times a day.

## When to Animate

**Do animate:**

- Enter/exit transitions for spatial consistency
- State changes that benefit from visual continuity
- Responses to user actions (feedback)
- Rarely-used interactions where delight adds value

**Don't animate:**

- Keyboard-initiated actions
- Hover effects on frequently-used elements
- Anything users interact with 100+ times daily
- When speed matters more than smoothness

**Marketing vs. Product:**

- Marketing: More elaborate, longer durations allowed
- Product: Fast, purposeful, never frivolous

## Spring Animations

Springs feel more natural because they don't have fixed durations—they simulate real physics.

### When to Use Springs

- Drag interactions with momentum
- Elements that should feel "alive" (Dynamic Island)
- Gestures that can be interrupted mid-animation
- Organic, playful interfaces

### Configuration

**Apple's approach (recommended):**

```js
// Duration + bounce (easier to understand)
{ type: "spring", duration: 0.5, bounce: 0.2 }
```

**Traditional physics:**

```js
// Mass, stiffness, damping (more complex)
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }
```

### Bounce Guidelines

- **Avoid bounce** in most UI contexts
- **Use bounce** for drag-to-dismiss, playful interactions
- Keep bounce subtle (0.1-0.3) when used

### Interruptibility

Springs maintain velocity when interrupted—CSS animations restart from zero. This makes springs ideal for gestures users might change mid-motion.

## Layout Animations (Framer Motion)

The most powerful FM feature. Lets you animate properties CSS can't: `flex-direction`, `justify-content`, position changes.

### The `layout` Prop
Add `layout` to any `motion.*` element to auto-animate layout changes:
```jsx
<motion.div layout className="element" />
```
When this element's size or position changes (due to state, content, siblings), FM animates it smoothly. No manual measurement needed.

### Shared Layout Animations (`layoutId`)
Connect two separate elements so one morphs into the other:
```jsx
// Tab highlight — only rendered for active tab
{activeTab === tab ? (
  <motion.div layoutId="tab-indicator" className="highlight" />
) : null}
```
Use cases: tab highlights, card → modal expansion, button → popover morph, trash interaction (images move between containers).

**Creative trick:** `layoutId` creates illusions. The feedback popover's "placeholder" is actually a `<span>` with a shared `layoutId` — not a real textarea placeholder. It morphs from button text to popover text.

### Dynamic Height Animation
FM can't animate `auto` to `auto`. Use `react-use-measure`:
```jsx
import useMeasure from "react-use-measure";
const [ref, bounds] = useMeasure();

<motion.div animate={{ height: bounds.height }}>
  <div ref={ref}>{dynamicContent}</div>
</motion.div>
```

## AnimatePresence (Deep)

### Modes
- `"sync"` (default) — enter and exit play simultaneously
- `"wait"` — exit completes before enter starts (copy/check icon swap)
- `"popLayout"` — removes exiting element from layout flow immediately (often the right choice for morphing UIs)

### Direction-Aware Transitions
Use the `custom` prop to pass dynamic data to exiting components (whose state is stale):
```jsx
<AnimatePresence mode="popLayout" custom={direction}>
  <motion.div
    key={step}
    custom={direction}
    initial="enter"
    animate="center"
    exit="exit"
    variants={{
      enter: (dir) => ({ x: dir > 0 ? 100 : -100, opacity: 0 }),
      center: { x: 0, opacity: 1 },
      exit: (dir) => ({ x: dir > 0 ? -100 : 100, opacity: 0 }),
    }}
  />
</AnimatePresence>
```

### Key Rules
- Always add `key` prop on animated elements inside AnimatePresence
- Use `initial={false}` to skip mount animation (icon swaps, button states)
- Known bug: rapid switching can show both elements — pin to FM v11.0.10 if hit

## Motion Values & Hooks

Motion values update outside React's render cycle — no re-renders, 60fps.

### `useMotionValue` — Instant updates (gestures)
```jsx
const x = useMotionValue(0);
// Update via x.set(newValue), read via x.get()
<motion.div style={{ x }} />
```
Use for: direct gesture tracking (drag distance → scale), any 1:1 mapping where spring lag would feel disconnected.

### `useSpring` — Animated updates (follow-behind)
```jsx
const x = useSpring(0, { mass: 0.1, damping: 16, stiffness: 71 });
// x.set(newValue) animates to it with spring physics
```
Use for: cursor followers, momentum effects, anything that should trail behind input.

### `useTransform` — Map one value to another
```jsx
// Range mapping: y position [0, 300] → scale [1, 1.5]
const scale = useTransform(y, [0, 300], [1, 1.5]);

// Function form: format a value
const display = useTransform(angle, v => `${Math.round(v)}°`);
```
Use for: scroll-linked effects, cursor-distance effects, value formatting.

### `useMotionTemplate` — String interpolation with motion values
```jsx
const clipPath = useMotionTemplate`inset(0px ${percent}% 0px 0px)`;
<motion.div style={{ clipPath }} />
```

### `MotionConfig` — Default transitions for a subtree
```jsx
<MotionConfig transition={{ type: "spring", duration: 0.5, bounce: 0.2 }}>
  {/* All children use this transition unless overridden */}
</MotionConfig>
```

## Orchestration (Stagger & Sequencing)

Staggered entrance animations create a wave effect. Trial and error until it feels right — no formula.

### CSS stagger (no library):
```css
.item { animation: fadeSlideIn 400ms ease-out both; }
.item:nth-child(1) { animation-delay: 0ms; }
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
/* etc. */
```

### FM stagger:
```jsx
const container = {
  animate: { transition: { staggerChildren: 0.05 } }
};
const item = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 }
};
```

**Rules:**
- Keep delays small (30-80ms between items)
- Cap total sequence time — 10 items at 80ms each = 800ms, too slow
- Marketing pages can be more elaborate; product UI should be fast

## Brand Expression Through Animation Speed

Animation timing IS brand identity:
- **Speed brand** (Vercel): instant or very fast, minimal easing. "We don't waste your time."
- **Premium brand** (Stripe): slower, more deliberate. `ease` curve (not ease-out) for elegance.
- **Playful brand** (Family): springs with subtle bounce, fluid morphing.
- **Product UI** should generally feel fast regardless of brand.
- **Marketing pages** are where you express brand personality through motion.

## Fluid Interfaces (Aspirational)

The north star: nothing "appears" or "disappears" — everything morphs. Family (iOS) is the gold standard.

- Shared layout animations are the web's closest tool to native fluidity
- Fluid motion improves perceived performance (feels faster even with same load time)
- Think about animations BEFORE designing the UI — position elements to enable seamless transitions
- Currently hard on web, but the direction everything is heading
- Text morphing (e.g., button label changes) highlights state changes subtly

## Performance

### The Golden Rule

Only animate `transform` and `opacity`. These skip layout and paint stages, running entirely on the GPU.

**Avoid animating:**

- `padding`, `margin`, `height`, `width` (trigger layout)
- `blur` filters above 20px (expensive, especially Safari)
- CSS variables in deep component trees

### Optimization Techniques

```css
/* Force GPU acceleration */
.animated-element {
  will-change: transform;
}
```

**React-specific:**

- Animate outside React's render cycle when possible
- Use refs to update styles directly instead of state
- Re-renders on every frame = dropped frames

**Framer Motion:**

```jsx
// Hardware accelerated (transform as string)
<motion.div animate={{ transform: "translateX(100px)" }} />

// NOT hardware accelerated (more readable)
<motion.div animate={{ x: 100 }} />
```

### CSS vs. JavaScript

- CSS animations run off main thread (smoother under load)
- JS animations (Framer Motion, React Spring) use `requestAnimationFrame`
- CSS better for simple, predetermined animations
- JS better for dynamic, interruptible animations
- **Combine both:** CSS for simple/perf-critical animations, FM for complex/layout/springs

### CSS Variables Gotcha
CSS variables are inheritable — changing one causes style recalc for ALL children. In deep component trees (20+ items), this kills drag/scroll performance.
```jsx
// BAD — recalculates all children
const style = { "--swipe-amount": `${distance}px` };

// GOOD — updates only this element
const style = { transform: `translateY(${distance}px)` };
```

### Transform Shift Fix
GPU/CPU handoff can cause 1px shift at animation start/end:
```css
.element { will-change: transform; }
```

## Accessibility

Animations can cause motion sickness or distraction for some users.

### prefers-reduced-motion

Whenever you add an animation, also add a media query to disable it:

```css
.modal {
  animation: fadeIn 200ms ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .modal {
    animation: none;
  }
}
```

### Reduced Motion Guidelines

**Reduced motion ≠ no motion.** Animations help users understand UI. Removing all motion hurts comprehension.

- **Remove:** transform-based movement, scaling, sliding, parallax
- **Keep:** opacity fades, color transitions, background changes
- **Replace:** slide-in → fade-in, scale → opacity, complex → simple
- Disable autoplay on videos/animated images; show play buttons instead
- For looping hero animations: pause on a good frame via `animation-delay: -0.4s`

### Framer Motion Implementation

**Option 1: Per-component hook**
```jsx
import { useReducedMotion } from "motion/react";

function Component() {
  const shouldReduceMotion = useReducedMotion();
  const closedX = shouldReduceMotion ? 0 : "-100%";

  return (
    <motion.div animate={{
      opacity: isOpen ? 1 : 0,
      x: isOpen ? 0 : closedX
    }} />
  );
}
```

**Option 2: App-wide wrapper (recommended)**
```jsx
import { MotionConfig } from "motion/react";

// Wraps your entire app — FM auto-reduces to opacity/backgroundColor only
<MotionConfig reducedMotion="user">{children}</MotionConfig>
```
Note: default is `"never"` — you must set this yourself.

### Touch Device Considerations

```css
/* Disable hover animations on touch devices */
@media (hover: hover) and (pointer: fine) {
  .element:hover {
    transform: scale(1.05);
  }
}
```

Touch devices trigger hover on tap, causing false positives.

## Practical Tips

Quick reference for common scenarios. See [PRACTICAL-TIPS.md](PRACTICAL-TIPS.md) for detailed implementations.

| Scenario                        | Solution                                        |
| ------------------------------- | ----------------------------------------------- |
| Make buttons feel responsive    | Add `transform: scale(0.97)` on `:active`       |
| Element appears from nowhere    | Start from `scale(0.95)`, not `scale(0)`        |
| Shaky/jittery animations        | Add `will-change: transform`                    |
| Hover causes flicker            | Animate child element, not parent               |
| Popover scales from wrong point | Set `transform-origin` to trigger location      |
| Sequential tooltips feel slow   | Skip delay/animation after first tooltip        |
| Small buttons hard to tap       | Use 44px minimum hit area (pseudo-element)      |
| Something still feels off       | Add subtle blur (under 20px) to mask it         |
| Hover triggers on mobile        | Use `@media (hover: hover) and (pointer: fine)` |

## Easing Decision Flowchart

Is the element entering or exiting the viewport?
├── Yes → ease-out
└── No
├── Is it moving/morphing on screen?
│ └── Yes → ease-in-out
└── Is it a hover change?
├── Yes → ease
└── Is it constant motion?
├── Yes → linear
└── Default → ease-out

## Reference Files

- [PRACTICAL-TIPS.md](PRACTICAL-TIPS.md) - Detailed implementations for common animation scenarios

---
