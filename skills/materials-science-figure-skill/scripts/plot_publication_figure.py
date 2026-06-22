#!/usr/bin/env python3
"""Render publication-style scientific figures from a JSON spec."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

_TMP_CACHE_ROOT = Path(tempfile.gettempdir()) / "nanobanana_plot_cache"
os.environ.setdefault("MPLCONFIGDIR", str(_TMP_CACHE_ROOT / "mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(_TMP_CACHE_ROOT / "xdg-cache"))

import matplotlib.pyplot as plt
import numpy as np


PALETTE = {
    "blue_main": "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",
    "red_1": "#F6CFCB",
    "red_2": "#E9A6A1",
    "red_strong": "#B64342",
    "neutral": "#CFCECE",
    "neutral_dark": "#4D4D4D",
    "highlight": "#FFD700",
    "teal": "#42949E",
    "violet": "#9A4D8E",
}

DEFAULT_COLORS = [
    PALETTE["blue_main"],
    PALETTE["green_3"],
    PALETTE["red_strong"],
    PALETTE["teal"],
    PALETTE["violet"],
    PALETTE["neutral_dark"],
]

SUPPORTED_FORMATS = {"png", "pdf", "svg", "eps", "jpg", "jpeg", "tif", "tiff"}


@dataclass(frozen=True)
class FigureStyle:
    font_size: int = 16
    axes_linewidth: float = 2.5
    use_tex: bool = False
    font_family: tuple[str, ...] = ("DejaVu Sans", "Helvetica", "Arial", "sans-serif")


def apply_publication_style(style: FigureStyle) -> None:
    plt.rcParams.update(
        {
            "font.family": list(style.font_family),
            "font.size": style.font_size,
            "axes.linewidth": style.axes_linewidth,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "legend.frameon": False,
            "svg.fonttype": "none",
            "text.usetex": style.use_tex,
        }
    )


def create_subplots(nrows: int, ncols: int, figsize: tuple[float, float]) -> tuple[plt.Figure, np.ndarray]:
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, squeeze=False)
    return fig, axes.reshape(-1)


def finalize_figure(
    fig: plt.Figure,
    out_path: str,
    formats: list[str],
    dpi: int,
    pad: float,
    close: bool,
) -> list[Path]:
    base = Path(out_path)
    base.parent.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for fmt in formats:
        if fmt not in SUPPORTED_FORMATS:
            raise SystemExit(f"Unsupported format: {fmt}")
        path = base.with_suffix(f".{fmt}")
        fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=pad, facecolor="white")
        saved.append(path)
    if close:
        plt.close(fig)
    return saved


def read_spec(path: str) -> dict:
    spec_path = Path(path)
    if not spec_path.is_file():
        raise SystemExit(f"Spec file not found: {spec_path}")
    return json.loads(spec_path.read_text(encoding="utf-8"))


def resolve_color(name: str | None, index: int) -> str:
    if not name:
        return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]
    return PALETTE.get(name, name)


def series_colors(series_count: int, colors: list[str] | None) -> list[str]:
    if colors:
        return [resolve_color(color, i) for i, color in enumerate(colors)]
    return [DEFAULT_COLORS[i % len(DEFAULT_COLORS)] for i in range(series_count)]


def coerce_1d(values: list[float], label: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise SystemExit(f"{label} must be 1D.")
    return arr


def coerce_2d(values: list[list[float]], label: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 2:
        raise SystemExit(f"{label} must be 2D.")
    return arr


def apply_axis_options(ax: plt.Axes, panel: dict) -> None:
    if "title" in panel:
        ax.set_title(panel["title"])
    if "xlabel" in panel:
        ax.set_xlabel(panel["xlabel"])
    if "ylabel" in panel:
        ax.set_ylabel(panel["ylabel"])
    if "xlim" in panel:
        ax.set_xlim(panel["xlim"])
    if "ylim" in panel:
        ax.set_ylim(panel["ylim"])
    if "xticks" in panel:
        ax.set_xticks(panel["xticks"])
    if "xticklabels" in panel:
        ax.set_xticklabels(panel["xticklabels"], rotation=panel.get("xtick_rotation", 0))
    if "yticks" in panel:
        ax.set_yticks(panel["yticks"])
    if "yticklabels" in panel:
        ax.set_yticklabels(panel["yticklabels"])
    if panel.get("hide_xticks"):
        ax.set_xticks([])
    if panel.get("hide_yticks"):
        ax.set_yticks([])
    if panel.get("grid"):
        ax.grid(True, alpha=panel.get("grid_alpha", 0.2), linewidth=panel.get("grid_linewidth", 1.0))


def annotate_bars(ax: plt.Axes, containers: list, fmt: str, fontsize: float, padding: float) -> None:
    for container in containers:
        for patch in container:
            height = patch.get_height()
            ax.annotate(
                fmt.format(height),
                (patch.get_x() + patch.get_width() / 2.0, height),
                textcoords="offset points",
                xytext=(0, padding),
                ha="center",
                va="bottom",
                fontsize=fontsize,
            )


def render_bar(ax: plt.Axes, panel: dict) -> None:
    categories = panel["categories"]
    series = coerce_2d(panel["series"], "series")
    labels = panel["labels"]
    if series.shape[1] != len(categories):
        raise SystemExit("Bar panel categories length must match series columns.")
    if len(labels) != series.shape[0]:
        raise SystemExit("Bar panel labels length must match number of series.")

    x = np.arange(len(categories), dtype=float)
    total_width = float(panel.get("bar_group_width", 0.8))
    width = total_width / max(series.shape[0], 1)
    colors = series_colors(series.shape[0], panel.get("colors"))
    edgecolor = resolve_color(panel.get("edgecolor"), 0) if panel.get("edgecolor") else "black"
    linewidth = float(panel.get("linewidth", 1.5))
    hatches = panel.get("hatches", [])

    containers = []
    for idx, values in enumerate(series):
        offsets = x - total_width / 2.0 + width * (idx + 0.5)
        hatch = hatches[idx] if idx < len(hatches) else None
        bars = ax.bar(
            offsets,
            values,
            width=width,
            label=labels[idx],
            color=colors[idx],
            edgecolor=edgecolor,
            linewidth=linewidth,
            hatch=hatch,
            alpha=float(panel.get("alpha", 1.0)),
        )
        containers.append(bars)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=panel.get("xtick_rotation", 0))
    if panel.get("legend", True):
        ax.legend(loc=panel.get("legend_loc", "best"), ncol=panel.get("legend_ncol", 1))
    if panel.get("annotate"):
        annotate_bars(
            ax,
            containers,
            panel.get("annotate_fmt", "{:.2f}"),
            float(panel.get("annotate_fontsize", 10)),
            float(panel.get("annotate_padding", 3)),
        )


def render_trend(ax: plt.Axes, panel: dict) -> None:
    x = coerce_1d(panel["x"], "x")
    y_series = panel["y_series"]
    labels = panel["labels"]
    if len(y_series) != len(labels):
        raise SystemExit("Trend panel labels length must match y_series.")
    colors = series_colors(len(y_series), panel.get("colors"))

    for idx, series in enumerate(y_series):
        y = coerce_1d(series, f"y_series[{idx}]")
        if len(y) != len(x):
            raise SystemExit("Each trend series must match x length.")
        ax.plot(
            x,
            y,
            label=labels[idx],
            color=colors[idx],
            linewidth=float(panel.get("line_width", 2.5)),
            alpha=float(panel.get("alpha", 1.0)),
        )
        shadows = panel.get("shadow", [])
        if idx < len(shadows):
            shadow = coerce_1d(shadows[idx], f"shadow[{idx}]")
            if len(shadow) != len(x):
                raise SystemExit("Each shadow series must match x length.")
            ax.fill_between(x, y - shadow, y + shadow, color=colors[idx], alpha=float(panel.get("shadow_alpha", 0.15)))

    if panel.get("legend", True):
        ax.legend(loc=panel.get("legend_loc", "best"), ncol=panel.get("legend_ncol", 1))


def render_heatmap(ax: plt.Axes, panel: dict, fig: plt.Figure) -> None:
    matrix = coerce_2d(panel["matrix"], "matrix")
    im = ax.imshow(matrix, aspect=panel.get("aspect", "auto"), cmap=panel.get("cmap", "magma"))

    x_labels = panel.get("x_labels")
    y_labels = panel.get("y_labels")
    if x_labels:
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=panel.get("xtick_rotation", 45), ha=panel.get("xtick_ha", "right"))
    if y_labels:
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_yticklabels(y_labels)
    if panel.get("annotate"):
        fmt = panel.get("annotate_fmt", "{:.2f}")
        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                ax.text(col, row, fmt.format(matrix[row, col]), ha="center", va="center", fontsize=panel.get("annotate_fontsize", 9))
    if panel.get("colorbar", True):
        cbar = fig.colorbar(im, ax=ax, fraction=panel.get("colorbar_fraction", 0.046), pad=panel.get("colorbar_pad", 0.04))
        if "colorbar_label" in panel:
            cbar.set_label(panel["colorbar_label"])


def render_scatter(ax: plt.Axes, panel: dict) -> None:
    x = coerce_1d(panel["x"], "x")
    y = coerce_1d(panel["y"], "y")
    if len(x) != len(y):
        raise SystemExit("Scatter x and y must match length.")
    color = resolve_color(panel.get("color"), 0)
    ax.scatter(
        x,
        y,
        label=panel.get("label"),
        color=color,
        s=float(panel.get("size", 50)),
        alpha=float(panel.get("alpha", 0.7)),
        edgecolors=panel.get("edgecolors"),
        linewidths=float(panel.get("linewidths", 0.0)),
    )
    if panel.get("legend") and panel.get("label"):
        ax.legend(loc=panel.get("legend_loc", "best"))


def render_legend_panel(ax: plt.Axes, panel: dict, rendered_axes: list[plt.Axes]) -> None:
    source_panel = int(panel["source_panel"])
    if source_panel >= len(rendered_axes):
        raise SystemExit("Legend panel source_panel is out of range.")
    handles, labels = rendered_axes[source_panel].get_legend_handles_labels()
    ax.set_axis_off()
    ax.legend(handles, labels, loc=panel.get("legend_loc", "center"), ncol=panel.get("legend_ncol", 1))


def render_panel(ax: plt.Axes, panel: dict, fig: plt.Figure, rendered_axes: list[plt.Axes]) -> None:
    panel_type = panel["type"]
    if panel_type == "bar":
        render_bar(ax, panel)
    elif panel_type == "trend":
        render_trend(ax, panel)
    elif panel_type == "heatmap":
        render_heatmap(ax, panel, fig)
    elif panel_type == "scatter":
        render_scatter(ax, panel)
    elif panel_type == "legend":
        render_legend_panel(ax, panel, rendered_axes)
    elif panel_type == "empty":
        ax.set_axis_off()
    else:
        raise SystemExit(f"Unsupported panel type: {panel_type}")

    if panel_type not in {"legend", "empty"}:
        apply_axis_options(ax, panel)
    if panel.get("axis_off"):
        ax.set_axis_off()


def build_style(spec: dict) -> FigureStyle:
    raw = spec.get("style", {})
    return FigureStyle(
        font_size=int(raw.get("font_size", 16)),
        axes_linewidth=float(raw.get("axes_linewidth", 2.5)),
        use_tex=bool(raw.get("use_tex", False)),
        font_family=tuple(raw.get("font_family", ["DejaVu Sans", "Helvetica", "Arial", "sans-serif"])),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a publication-style figure from a JSON spec.")
    parser.add_argument("spec_file", help="Path to the JSON figure spec.")
    parser.add_argument("--out-path", help="Base output path without extension. Defaults to spec path stem in ./output/plots/.")
    parser.add_argument("--formats", nargs="+", default=["png", "pdf", "svg"], help="Output formats.")
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI.")
    parser.add_argument("--pad", type=float, default=0.05, help="Padding passed to savefig.")
    parser.add_argument("--keep-open", action="store_true", help="Do not close the matplotlib figure after saving.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = read_spec(args.spec_file)
    apply_publication_style(build_style(spec))

    layout = spec.get("layout", {})
    nrows = int(layout.get("nrows", 1))
    ncols = int(layout.get("ncols", 1))
    figsize = tuple(layout.get("figsize", [8, 6]))
    if len(figsize) != 2:
        raise SystemExit("layout.figsize must contain exactly two numbers.")

    fig, axes = create_subplots(nrows, ncols, (float(figsize[0]), float(figsize[1])))
    panels = spec.get("panels", [])
    if len(panels) > len(axes):
        raise SystemExit("Number of panels exceeds subplot slots.")

    rendered_axes: list[plt.Axes] = []
    for idx, panel in enumerate(panels):
        render_panel(axes[idx], panel, fig, rendered_axes)
        rendered_axes.append(axes[idx])
    for idx in range(len(panels), len(axes)):
        axes[idx].set_axis_off()

    if "suptitle" in spec:
        fig.suptitle(spec["suptitle"])
    fig.tight_layout(pad=float(layout.get("tight_layout_pad", 2.0)))

    if args.out_path:
        out_path = args.out_path
    else:
        spec_path = Path(args.spec_file)
        out_path = str(Path("output/plots") / spec_path.stem)

    saved = finalize_figure(fig, out_path, [fmt.lower() for fmt in args.formats], args.dpi, args.pad, not args.keep_open)
    for path in saved:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
