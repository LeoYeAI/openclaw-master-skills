# Standard Project Directory Structure

```
project-name/
├── assets/          # Design assets (named meaningfully)
│   ├── design-banner.png
│   ├── design-main.png        # Full-page reference for visual diff
│   ├── play1-bg.png
│   ├── sign-2-on.png
│   └── sign-2-off.png
├── css/
│   └── styles.css
├── html/
│   └── index.html
├── scripts/         # Build/utility scripts (not shipped)
│   └── compare_render.py
├── source/          # Raw exports (Figma REST, user ZIP)
│   ├── rest-assets/
│   │   ├── nodes.json
│   │   ├── images.json
│   │   ├── manifest.json
│   │   └── node-*.png
│   └── user-zip-contents/
├── compare/         # Visual diff outputs
│   ├── current.png
│   ├── diff.png
│   └── report.txt
└── README.md        # Project notes (optional)
```

## Naming Convention for Assets

- `design-{section}.png` — Full section blocks from Figma export
- `{feature}-bg.png` — Background images for specific features
- `{feature}-{state}.png` — State variants (on/off, active/inactive)
- `design-main.png` — Full-page design reference for visual diff validation
