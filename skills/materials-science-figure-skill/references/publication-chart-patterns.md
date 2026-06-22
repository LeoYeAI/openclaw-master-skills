# Publication Chart Patterns

Use this reference when the requested figure includes chart-like panels or schematic panels derived from plotting conventions.

These patterns come from `figures4papers` and are useful for prompting Nanobanana to mimic publication layouts, even when the final output is still an image rather than a deterministic matplotlib chart.

## Grouped Comparison Bars

Best for:

- method comparison
- ablation studies
- performance breakdowns

Prompt for:

- grouped vertical bars with strong black edges
- compact legend
- short metric labels
- y-axis limits tightened to reveal differences
- optional value labels above bars when the figure is a stylized redraw

## Trend Panels

Best for:

- time-series change
- training or validation trends
- dose or condition response

Prompt for:

- 2 to 4 primary curves per panel
- consistent line widths
- optional shaded uncertainty bands
- minimal grid or no grid
- dedicated legend zone if the plot is dense

## Heatmaps and Result Matrices

Best for:

- optimization maps
- composition maps
- correlation or comparison matrices

Prompt for:

- clean cell grid
- restrained colormap with readable contrast
- legible row and column labels
- a simple colorbar if needed
- no excessive beveling or glossy effects

## Multi-Panel Layouts

Preferred pattern:

- data panels grouped together
- one empty or reduced-information panel reserved for the legend when needed
- matching margins, titles, and label positions across panels

Useful prompt phrases:

- "balanced 1x3 publication layout"
- "last panel reserved for the legend"
- "consistent panel spacing and label alignment"

## Ultra-Wide Comparison Panels

For figures with many categories or metrics:

- ask for a wide horizontal canvas
- keep bars and labels uncrowded
- favor left-to-right scanning

Useful prompt phrases:

- "ultra-wide comparison panel"
- "publication-style horizontal rhythm"
- "ample whitespace between metric groups"

## Print-Safe Separation

When multiple groups have similar fills:

- use dark outlines
- use different hatching or texture cues
- avoid relying only on red-vs-green distinctions

## Quantitative Safety

For chart-like prompts, be explicit about the intended fidelity:

- exact redraw from a provided source figure
- style-matched conceptual chart
- schematic panel inspired by a bar chart or heatmap

Do not imply exact numeric fidelity unless the prompt is based on trusted provided values or a trusted reference image.
