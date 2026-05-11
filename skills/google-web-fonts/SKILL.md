---
name: google-web-fonts
description: Use the Google Fonts API to add fonts to web pages.
---

# Google Web Fonts

## Use Cases

- Importing Google Fonts in HTML
- Building font CSS URLs (family, style, weight, subset, text parameters)
- Controlling font loading behavior with font-display
- Applying font effects (Beta)

## Quick Start

### 1. Include the Font Stylesheet

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Font+Name">
```

### 2. Use the Font in CSS

```css
body {
  font-family: 'Font Name', serif;
}
```

## Building API Parameters

### Basic Format

```
https://fonts.googleapis.com/css?family=Font+Name
```

### Multiple Fonts (separated by |)

```
https://fonts.googleapis.com/css?family=Tangerine|Inconsolata|Droid+Sans
```

### Styles and Weights (separated by :)

| Style | Specifier |
|-------|-----------|
| Italic | `italic` or `i` |
| Bold | `bold` or `b`, or numeric value such as `700` |
| Bold Italic | `bolditalic` or `bi` |

Example:
```
https://fonts.googleapis.com/css?family=Cantarell:italic|Droid+Serif:bold
```

### font-display Control

```
https://fonts.googleapis.com/css?family=Roboto&display=swap
```

### Subsets (subset parameter)

```
https://fonts.googleapis.com/css?family=Roboto+Mono&subset=cyrillic,greek
```

### Performance Optimization (text parameter)

Specify the characters needed to reduce the font file size by up to 90%:

```
https://fonts.googleapis.com/css?family=Inconsolata&text=Hello%20World
```

### Font Effects (Beta)

```
https://fonts.googleapis.com/css?family=Rancho&effect=shadow-multiple
```

Usage:
```html
<div class="font-effect-shadow-multiple">This is a font effect!</div>
```

## Common Effects List

| Effect | API Name | Class Name |
|--------|----------|------------|
| 3D | `3d` | font-effect-3d |
| 3D Float | `3d-float` | font-effect-3d-float |
| Anaglyph | `anaglyph` | font-effect-anaglyph |
| Neon | `neon` | font-effect-neon |
| Shadow Multiple | `shadow-multiple` | font-effect-shadow-multiple |
| Vintage | `vintage` | font-effect-vintage |