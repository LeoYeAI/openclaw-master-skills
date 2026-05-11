# HTML Architecture for Presentations

Every presentation must follow this structure. **Include the full mandatory base CSS from [viewport-and-base.css](viewport-and-base.css)** (or inline equivalent) so every slide fits exactly in the viewport.

## Document structure

- `<!DOCTYPE html>`, `<html lang="en">`
- `<head>`: charset, viewport, title, Fontshare/Google Fonts link, `<style>` with:
  - CSS custom properties (theme colors, `--font-display`, `--font-body`, `--title-size`, `--subtitle-size`, `--body-size`, `--slide-padding`, `--content-gap`, `--ease-out-expo`, `--duration-normal`)
  - Base: `* { margin:0; padding:0; box-sizing:border-box; }`, html/body height and overflow
  - `.slide`: `width:100vw; height:100vh; height:100dvh; overflow:hidden; scroll-snap-align:start; display:flex; flex-direction:column; justify-content:center; position:relative; padding:var(--slide-padding);`
  - `.slide-content`: flex:1; display:flex; flex-direction:column; justify-content:center; max-height:100%; overflow:hidden;
  - Responsive breakpoints for max-height 600px, max-width 768px, landscape phones
  - `.reveal` / `.slide.visible .reveal` for scroll-triggered animations; stagger with nth-child delay
- `<body>`: optional progress bar, nav.nav-dots, then `<section class="slide">` per slide
- Each slide: semantic content (h1/h2, p, ul, .card, img) with .reveal where needed
- `<script>`: SlidePresentation class (keyboard, touch, wheel, progress, dots), Intersection Observer for .visible, optional edit button (see [edit-button-implementation.md](edit-button-implementation.md))

## Image CSS (adapt border/glow to style accent)

- `.slide-image`: max-width 100%; max-height min(50vh, 400px); object-fit contain; border-radius 8px
- `.slide-image.screenshot`: border + box-shadow (use style accent color)
- `.slide-image.logo`: max-height min(30vh, 200px)

Reference images with relative paths: `<img src="assets/logo_round.png" alt="Logo" class="slide-image logo">`. Only use base64 if user requests single-file.

## File layout

- Single: `presentation.html` + `assets/` (if images)
- Multiple: `[name].html` + `[name]-assets/`
