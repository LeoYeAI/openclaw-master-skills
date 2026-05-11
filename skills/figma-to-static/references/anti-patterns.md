# Anti-Patterns (Learned the Hard Way)

Use this list as a final QA pass before claiming completion.

1. Never paste a full section as one `<img>` when real DOM is required.
2. Never invent text; use Figma/source content or ask user.
3. Never fake assets (cropped screenshots/emoji placeholders/solid boxes for real media).
4. Never skip `overflow-x: hidden` on page containers for mobile.
5. Prefer REST JSON + `figma_to_css.py` for precise CSS extraction.
6. Never hardcode pixel offsets for overlays if percentage mapping is available.
7. Avoid `position: absolute` for core layout structure.
8. Never put `overflow-x: auto` on `body`/page shell.
9. Build timelines/progress bars with real DOM, not simplified color blocks.
10. Never guess properties available in Figma JSON.
11. Build nav/menu as real DOM, not screenshot slices.
12. Extract individual component assets; don’t crop whole-page screenshots.
13. Parse `get_design_context` assets with `scripts/parse_design_context.py` to handle extension mismatch and SVG normalization.
