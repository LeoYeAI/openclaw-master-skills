# CSS Extraction Rules (From Figma JSON)

Use this reference when mapping raw Figma node data to CSS.

## Property Mapping Table

| Property | Figma field | CSS mapping |
|---|---|---|
| Background color | `fills[0].color` → `{r,g,b,a}` | `rgb(r*255, g*255, b*255)` or `rgba(...)` |
| Text color | `fills[0].color` on Text node | `color:` |
| Font family | `fontName.family` | `font-family:` |
| Font size | `fontSize` | `font-size:` |
| Font weight | `fontWeight` | `font-weight:` |
| Line height | `lineHeightPx` / `lineHeightPercent` | `line-height:` |
| Letter spacing | `letterSpacing` | `letter-spacing:` |
| Border radius | `cornerRadius` | `border-radius:` |
| Border | `strokes[0]` | `border:` |
| Opacity | `opacity` | `opacity:` |
| Shadow | `effects[]` where `type==DROP_SHADOW` | `box-shadow:` |
| Padding | auto-layout padding fields | `padding:` |

## Non-Negotiable Rules

1. Read from Figma JSON first; estimate only if the field is missing.
2. Convert 0-1 color channels to 0-255 (multiply then round).
3. Preserve spacing ratios on mobile (use `clamp()`/`vw` carefully; don’t destroy hierarchy).
4. If rendered color looks wrong, inspect parent chain and alpha blending.
5. Match gap from `itemSpacing` or coordinate deltas; never guess gaps.
6. Match text alignment from `textAlignHorizontal` / `textAlignVertical`.
7. Match text-shadow and inner-shadow from `effects[]` when present.
8. Extract exact padding from auto-layout parent (`paddingTop/Right/Bottom/Left`).
9. Match container max-width to source frame width, not arbitrary defaults.
10. If design includes state variants, implement `:hover/:active/:disabled` states.

## Workflow Hint

- Use `scripts/fetch_figma_rest.py` to get detailed JSON (`nodes.json`).
- Use `scripts/figma_to_css.py` to bootstrap extraction.
- Use this file to validate and correct the generated CSS.
