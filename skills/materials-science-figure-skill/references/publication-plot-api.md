# Publication Plot API

Use this reference when the user needs exact plotting from data rather than prompt-based image generation.

The deterministic entrypoint is:

```bash
python3 skills/nanobanana-image-generation/scripts/plot_publication_figure.py spec.json
```

It renders publication-style figures from a JSON spec and exports exact PNG, PDF, or SVG outputs.

When the user is speaking to Codex in natural language, do not expose this JSON spec as the primary interface. Instead, see [natural-language-plot-workflow.md](natural-language-plot-workflow.md) and let Codex generate the internal request or spec automatically.

## When To Use

Use this mode for:

- exact bar heights from numeric data
- exact heatmap matrices
- exact trend curves from arrays
- scatter plots from measured coordinates
- multi-panel layouts that must stay numerically faithful

Do not use this mode for:

- graphical abstracts
- mechanism diagrams
- device illustrations without underlying numeric data

For those, use Nanobanana generation mode instead.

## Top-Level Spec Shape

```json
{
  "suptitle": "Optional Figure Title",
  "style": {
    "font_size": 16,
    "axes_linewidth": 2.5,
    "use_tex": false,
    "font_family": ["DejaVu Sans", "Helvetica", "Arial", "sans-serif"]
  },
  "layout": {
    "nrows": 1,
    "ncols": 2,
    "figsize": [14, 5],
    "tight_layout_pad": 2.0
  },
  "panels": [
    { "... panel spec ..." }
  ]
}
```

## Supported Panel Types

- `bar`
- `trend`
- `heatmap`
- `scatter`
- `legend`
- `empty`

## Shared Style Defaults

- minimalist spines
- frameless legends
- white background
- Helvetica or Arial-like sans-serif fallback stack
- publication-style semantic palette

Palette keys you can reference in panel `colors`:

- `blue_main`
- `blue_secondary`
- `green_1`
- `green_2`
- `green_3`
- `red_1`
- `red_2`
- `red_strong`
- `neutral`
- `neutral_dark`
- `highlight`
- `teal`
- `violet`

You may also pass raw hex colors.

## Bar Panel

```json
{
  "type": "bar",
  "title": "Method Comparison",
  "categories": ["AUC", "F1", "Recall", "Precision"],
  "series": [
    [0.92, 0.88, 0.85, 0.90],
    [0.85, 0.82, 0.88, 0.84],
    [0.78, 0.80, 0.82, 0.79]
  ],
  "labels": ["Ours", "Baseline X", "Baseline Y"],
  "colors": ["blue_main", "green_3", "red_strong"],
  "ylabel": "Score",
  "ylim": [0.7, 1.0],
  "annotate": true
}
```

Useful options:

- `legend`
- `legend_loc`
- `legend_ncol`
- `annotate`
- `annotate_fmt`
- `hatches`
- `hide_xticks`
- `bar_group_width`

## Trend Panel

```json
{
  "type": "trend",
  "title": "Training",
  "x": [1, 2, 3, 4, 5],
  "y_series": [
    [0.62, 0.71, 0.78, 0.83, 0.86],
    [0.58, 0.66, 0.72, 0.77, 0.80]
  ],
  "shadow": [
    [0.02, 0.02, 0.015, 0.01, 0.01],
    [0.025, 0.02, 0.02, 0.015, 0.015]
  ],
  "labels": ["Model A", "Model B"],
  "colors": ["blue_main", "red_strong"],
  "xlabel": "Epoch",
  "ylabel": "Accuracy"
}
```

Useful options:

- `line_width`
- `shadow_alpha`
- `legend`
- `legend_loc`

## Heatmap Panel

```json
{
  "type": "heatmap",
  "title": "Optimization Matrix",
  "matrix": [
    [0.15, 0.27, 0.45],
    [0.22, 0.39, 0.61],
    [0.33, 0.48, 0.74]
  ],
  "x_labels": ["Low", "Mid", "High"],
  "y_labels": ["Case 1", "Case 2", "Case 3"],
  "cmap": "magma",
  "colorbar_label": "Score",
  "annotate": true
}
```

Useful options:

- `colorbar`
- `colorbar_label`
- `annotate`
- `annotate_fmt`
- `aspect`

## Scatter Panel

```json
{
  "type": "scatter",
  "title": "Property Map",
  "x": [1.1, 1.4, 1.8, 2.2],
  "y": [220, 245, 280, 315],
  "xlabel": "Band Gap (eV)",
  "ylabel": "Conductivity",
  "color": "blue_main",
  "size": 60,
  "alpha": 0.8
}
```

## Legend Panel

Use a dedicated subplot for the legend when the data panels are dense.

```json
{
  "type": "legend",
  "source_panel": 0,
  "legend_loc": "center",
  "legend_ncol": 1
}
```

`source_panel` is zero-based and points to an earlier panel whose handles and labels should be reused.

## Axis Options

Most non-legend panels support:

- `title`
- `xlabel`
- `ylabel`
- `xlim`
- `ylim`
- `xticks`
- `xticklabels`
- `xtick_rotation`
- `yticks`
- `yticklabels`
- `hide_xticks`
- `hide_yticks`
- `grid`

## Output

Default output path:

```bash
output/plots/<spec-file-stem>.png
output/plots/<spec-file-stem>.pdf
output/plots/<spec-file-stem>.svg
```

Override it with:

```bash
python3 skills/nanobanana-image-generation/scripts/plot_publication_figure.py spec.json \
  --out-path output/plots/my_figure \
  --formats png pdf svg \
  --dpi 300
```

## Concise Request Builder

For Codex-facing natural-language workflows, a lighter request JSON can be expanded into a full spec:

```bash
python3 skills/nanobanana-image-generation/scripts/build_plot_spec.py request.json --out spec.json
```

This is mainly for Codex's internal use after interpreting a user's natural-language plotting request. See [natural-language-plot-workflow.md](natural-language-plot-workflow.md).
