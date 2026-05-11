# Reusable CSS Patterns

## Base Shell

```css
:root { --maxw: 800px; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; width: 100%; overflow-x: hidden; }
.page-shell {
  width: 100%; max-width: var(--maxw); margin: 0 auto;
  min-height: 100vh; background: #000; overflow-x: hidden;
}
```

## Stage (Full-Width Section)

```css
.stage { position: relative; width: 100%; overflow-x: clip; }
.stage > img { display: block; width: 100%; height: auto; }
```

## Absolute Overlay (from Figma Coordinates)

Given parent `{x, y, w, h}` and child `{x, y, w, h}`:
```css
.overlay {
  position: absolute;
  left: calc((child.x - parent.x) / parent.w * 100%);
  top: calc((child.y - parent.y) / parent.h * 100%);
  width: calc(child.w / parent.w * 100%);
}
```

## Scrollable Row (e.g., Signin Cards)

```css
.scroll-row {
  display: flex; gap: 8px;
  overflow-x: auto; overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
}
.scroll-row::-webkit-scrollbar { height: 4px; }
.scroll-row::-webkit-scrollbar-thumb { background: rgba(0,0,0,.25); border-radius: 999px; }
```

## Timeline with Nodes

```css
.timeline { height: 6px; background: #d8d1cb; border-radius: 999px; overflow: hidden; }
.timeline .progress { display: block; height: 100%; background: #c51100; }
.dot { width: 12px; height: 12px; border-radius: 50%; background: #d8d1cb; }
.dot.done { background: #c51100; }
```

## Responsive Typography

```css
.title { font-size: clamp(20px, 5.2vw, 42px); }
.body-text { font-size: clamp(12px, 3vw, 27px); }
```

## PC Centered

```css
@media (min-width: 801px) {
  .page-shell { box-shadow: 0 0 0 1px #2e0f0d, 0 24px 60px rgba(0,0,0,.45); }
}
```
