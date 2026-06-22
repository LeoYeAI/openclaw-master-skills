# Natural-Language Plot Workflow

Use this reference when the user is talking to Codex in natural language and wants an exact plot without writing a JSON spec.

The user does not need to write the plotting spec manually. Codex should infer the plotting intent, create an internal request or spec, and then run the plotting scripts.

## Principle

Treat natural language as the user-facing interface and JSON as an internal execution format.

User says:

- "Plot a 3-method comparison bar chart for AUC, F1, and Recall"
- "Make a 1x3 figure with two trend panels and the last panel only for the legend"
- "Render this matrix as a heatmap with magma colors and a colorbar"

Codex should:

1. decide that `plot` mode is appropriate
2. extract the figure structure
3. extract or locate the numeric data
4. create either:
   - a concise request JSON for `scripts/build_plot_spec.py`, or
   - a full spec JSON for `scripts/plot_publication_figure.py`
5. render the figure
6. iterate once if the layout or labels need correction

## Extraction Checklist

From the user's natural-language request, infer:

- plot type:
  - `bar`
  - `trend`
  - `heatmap`
  - `scatter`
  - multi-panel combination
- titles and axis labels
- categories or x values
- series labels
- numeric values
- semantic colors:
  - primary result -> blue
  - improvement -> green
  - baseline or contrast -> red
- whether a shared legend panel is needed
- export formats if specified

If exact numeric data is missing, do not pretend the output is exact.

Instead:

- ask for the missing values, or
- switch to `image` mode only if the user's intent is conceptual rather than numeric

## Recommended Internal Path

For simple plots:

1. Codex drafts a concise request JSON.
2. Run:

```bash
python3 skills/nanobanana-image-generation/scripts/build_plot_spec.py request.json --out spec.json
python3 skills/nanobanana-image-generation/scripts/plot_publication_figure.py spec.json
```

For more custom layouts:

1. Codex writes the full spec JSON directly.
2. Run `plot_publication_figure.py`.

## Concise Request Shape

The concise request format is easier for Codex to author from natural language than the full plotting spec.

```json
{
  "suptitle": "Benchmark Overview",
  "layout": {
    "nrows": 1,
    "ncols": 2,
    "figsize": [12, 4.5]
  },
  "panels": [
    {
      "kind": "bar",
      "title": "Method Comparison",
      "ylabel": "Score",
      "annotate": true,
      "data": {
        "categories": ["AUC", "F1", "Recall"],
        "series": {
          "Ours": [0.92, 0.88, 0.85],
          "Baseline": [0.85, 0.82, 0.80]
        }
      },
      "colors": {
        "Ours": "blue_main",
        "Baseline": "red_strong"
      }
    },
    {
      "kind": "legend",
      "source_panel": 0
    }
  ]
}
```

## Example Natural-Language Conversions

Request:

"画一个方法对比柱状图，横轴是 AUC、F1、Recall，ours 用蓝色，baseline 用红色，把数值标在柱子上。"

Internal interpretation:

- mode: `plot`
- panel type: `bar`
- categories: `AUC`, `F1`, `Recall`
- colors: `blue_main`, `red_strong`
- annotate bars: `true`

Request:

"做一个 1x3 的 figure，前两个 panel 是 training 和 validation trend，最后一个 panel 单独放 legend。"

Internal interpretation:

- mode: `plot`
- layout: `1x3`
- panels 0 and 1: `trend`
- panel 2: `legend`

## Decision Boundary

Choose `plot` mode when:

- the user cares about exact values
- the user gives arrays, tables, or measured coordinates
- the output is a standard scientific plot

Choose `image` mode when:

- the output is schematic or conceptual
- the user wants a graphical abstract or mechanism figure
- visual storytelling matters more than numeric fidelity
