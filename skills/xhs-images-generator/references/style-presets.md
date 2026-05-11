# Style Presets

`--preset X` expands to a style + layout combination. Users can override either dimension.

| --preset | Style | Layout |
|----------|-------|--------|
| `knowledge-card` | `notion` | `dense` |
| `checklist` | `notion` | `list` |
| `concept-map` | `notion` | `mindmap` |
| `swot` | `notion` | `quadrant` |
| `tutorial` | `chalkboard` | `flow` |
| `classroom` | `chalkboard` | `balanced` |
| `study-guide` | `study-notes` | `dense` |
| `cute-share` | `cute` | `balanced` |
| `girly` | `cute` | `sparse` |
| `cozy-story` | `warm` | `balanced` |
| `product-review` | `fresh` | `comparison` |
| `nature-flow` | `fresh` | `flow` |
| `warning` | `bold` | `list` |
| `versus` | `bold` | `comparison` |
| `clean-quote` | `minimal` | `sparse` |
| `pro-summary` | `minimal` | `balanced` |
| `retro-ranking` | `retro` | `list` |
| `throwback` | `retro` | `balanced` |
| `pop-facts` | `pop` | `list` |
| `hype` | `pop` | `sparse` |
| `poster` | `screen-print` | `sparse` |
| `editorial` | `screen-print` | `balanced` |
| `cinematic` | `screen-print` | `comparison` |

## Override Examples

- `--preset knowledge-card --style chalkboard` = chalkboard style with dense layout
- `--preset poster --layout quadrant` = screen-print style with quadrant layout

Explicit `--style`/`--layout` flags always override preset values.
