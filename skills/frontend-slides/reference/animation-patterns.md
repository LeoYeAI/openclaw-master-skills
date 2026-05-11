# Animation Patterns Reference

## Entrance Animations

- **Fade + Slide Up (most common):** `opacity: 0; transform: translateY(30px);` → `.visible` → `opacity: 1; transform: translateY(0);` with transition ~0.6s ease-out-expo.
- **Scale In:** `transform: scale(0.9)` → scale(1).
- **Slide from Left:** `translateX(-50px)` → translateX(0).
- **Blur In:** `filter: blur(10px)` → blur(0).

Use `.visible` class (added by Intersection Observer when slide enters viewport) to trigger. Stagger children with `transition-delay: 0.1s, 0.2s, 0.3s...`.

## Background Effects

- **Gradient mesh:** Multiple `radial-gradient` with accent colors on `--bg-primary`.
- **Noise texture:** Inline SVG noise as `background-image`.
- **Grid pattern:** `linear-gradient` 1px lines, `background-size: 50px 50px`.

## Interactive Effects (optional)

- **3D Tilt on hover:** `transform-style: preserve-3d`, `perspective: 1000px`, mousemove → `rotateY(x*10deg) rotateX(-y*10deg)`, mouseleave → reset.

## Reduced Motion

Always include:

```css
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }
    html { scroll-behavior: auto; }
}
```

For `.reveal`, use `transition: opacity 0.3s ease; transform: none;` in reduced-motion mode.
