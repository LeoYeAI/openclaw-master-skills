# Publication Figure Design

Distilled from the `figures4papers` project and adapted for prompt-based image generation. Use this reference when the user wants a journal-style research figure rather than a generic illustration.

## Core Style

- Minimalist, high-contrast, publication-oriented.
- White background by default.
- Clean panel structure rather than decorative collage.
- Frameless legends and uncluttered axes or containers.
- Short professional labels, not marketing copy.

## Typography

- Aim for Helvetica or Arial-like sans-serif typography.
- Keep label hierarchy simple:
  - panel labels and titles: strongest emphasis
  - axis or legend text: medium emphasis
  - secondary notes: smallest emphasis
- Avoid ornate fonts, handwritten fonts, and heavy 3D text effects.

## Semantic Palette

Use color semantically, not decoratively.

- Blue: primary method, central mechanism, key pathway
- Green: improvement, favorable variant, beneficial state
- Red or warm pink: baseline, contrast, competing route, adverse state
- Neutral gray or charcoal: substrate, background categories, non-focal scaffolds
- Gold or a single accent: one targeted highlight only

Keep the same meaning for the same color across all panels.

Representative palette:

- `#0F4D92`
- `#3775BA`
- `#8BCF8B`
- `#AADCA9`
- `#B64342`
- `#F6CFCB`
- `#CFCECE`
- `#4D4D4D`

## Layout Logic

- Prefer balanced multi-panel compositions over one crowded canvas.
- For comparison-heavy figures, think left-to-right narrative:
  - condition or processing
  - structure or defect state
  - mechanism
  - property or performance
- Keep legends outside the densest data region when possible.
- Use repeated alignment and spacing so the figure feels systematic.

## Publication-Friendly Simplification

- Remove unnecessary perspective, glossy rendering, and decorative textures.
- Keep arrows clear and causal.
- Keep iconography modular and editable-looking.
- Use moderate color saturation and reserve bright accents for focal points.
- Make the figure readable at single-column scale.

## Prompting Implications

When writing prompts, explicitly ask for:

- white background
- Nature-style or journal-style composition
- consistent semantic color mapping
- concise labels
- panel balance
- vector-friendly modular shapes
- minimal clutter

Avoid asking for:

- cinematic lighting
- dramatic shadows
- photorealistic backgrounds
- poster-style gradients unless the user explicitly wants them
