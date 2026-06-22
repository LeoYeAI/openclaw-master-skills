#!/usr/bin/env python3
"""Build a full publication plot spec from a concise request JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEFAULT_LAYOUT = {
    "nrows": 1,
    "ncols": 1,
    "figsize": [8, 6],
    "tight_layout_pad": 2.0,
}

DEFAULT_STYLE = {
    "font_size": 16,
    "axes_linewidth": 2.5,
    "use_tex": False,
    "font_family": ["DejaVu Sans", "Helvetica", "Arial", "sans-serif"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a full plot spec from a concise request JSON.")
    parser.add_argument("request_file", nargs="?", help="Path to the concise request JSON.")
    parser.add_argument("--stdin", action="store_true", help="Read the concise request JSON from stdin.")
    parser.add_argument("--out", help="Write the full spec JSON to this file instead of stdout.")
    return parser.parse_args()


def load_request(args: argparse.Namespace) -> dict:
    if args.stdin:
        return json.loads(sys.stdin.read())
    if not args.request_file:
        raise SystemExit("Provide a request JSON file or use --stdin.")
    path = Path(args.request_file)
    if not path.is_file():
        raise SystemExit(f"Request file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def merge_layout(layout: dict | None, panel_count: int) -> dict:
    result = dict(DEFAULT_LAYOUT)
    if layout:
        result.update(layout)
    if "nrows" not in result or "ncols" not in result:
        result["nrows"] = 1
        result["ncols"] = max(panel_count, 1)
    return result


def build_bar_panel(panel: dict) -> dict:
    data = panel["data"]
    series_map = data["series"]
    labels = list(series_map.keys())
    colors_map = panel.get("colors", {})
    return {
        "type": "bar",
        "title": panel.get("title"),
        "categories": data["categories"],
        "series": [series_map[label] for label in labels],
        "labels": labels,
        "colors": [colors_map.get(label) for label in labels] if colors_map else None,
        "xlabel": panel.get("xlabel"),
        "ylabel": panel.get("ylabel", "Value"),
        "ylim": panel.get("ylim"),
        "annotate": panel.get("annotate", False),
        "legend": panel.get("legend", True),
        "legend_loc": panel.get("legend_loc", "best"),
        "legend_ncol": panel.get("legend_ncol", 1),
        "xtick_rotation": panel.get("xtick_rotation", 0),
        "hatches": panel.get("hatches"),
        "grid": panel.get("grid", False),
    }


def build_trend_panel(panel: dict) -> dict:
    data = panel["data"]
    series_map = data["series"]
    labels = list(series_map.keys())
    colors_map = panel.get("colors", {})
    shadows_map = data.get("shadow", {})
    out = {
        "type": "trend",
        "title": panel.get("title"),
        "x": data["x"],
        "y_series": [series_map[label] for label in labels],
        "labels": labels,
        "colors": [colors_map.get(label) for label in labels] if colors_map else None,
        "xlabel": panel.get("xlabel"),
        "ylabel": panel.get("ylabel", "Value"),
        "legend": panel.get("legend", True),
        "legend_loc": panel.get("legend_loc", "best"),
        "legend_ncol": panel.get("legend_ncol", 1),
        "ylim": panel.get("ylim"),
        "grid": panel.get("grid", False),
    }
    if shadows_map:
        out["shadow"] = [shadows_map[label] for label in labels if label in shadows_map]
    return out


def build_heatmap_panel(panel: dict) -> dict:
    data = panel["data"]
    return {
        "type": "heatmap",
        "title": panel.get("title"),
        "matrix": data["matrix"],
        "x_labels": data.get("x_labels"),
        "y_labels": data.get("y_labels"),
        "xlabel": panel.get("xlabel"),
        "ylabel": panel.get("ylabel"),
        "cmap": panel.get("cmap", "magma"),
        "colorbar": panel.get("colorbar", True),
        "colorbar_label": panel.get("colorbar_label"),
        "annotate": panel.get("annotate", False),
        "annotate_fmt": panel.get("annotate_fmt", "{:.2f}"),
        "xtick_rotation": panel.get("xtick_rotation", 45),
    }


def build_scatter_panel(panel: dict) -> dict:
    data = panel["data"]
    return {
        "type": "scatter",
        "title": panel.get("title"),
        "x": data["x"],
        "y": data["y"],
        "label": panel.get("label"),
        "color": panel.get("color", "blue_main"),
        "xlabel": panel.get("xlabel"),
        "ylabel": panel.get("ylabel"),
        "size": panel.get("size", 50),
        "alpha": panel.get("alpha", 0.7),
        "legend": panel.get("legend", False),
        "legend_loc": panel.get("legend_loc", "best"),
        "grid": panel.get("grid", False),
    }


def build_legend_panel(panel: dict) -> dict:
    return {
        "type": "legend",
        "source_panel": panel["source_panel"],
        "legend_loc": panel.get("legend_loc", "center"),
        "legend_ncol": panel.get("legend_ncol", 1),
    }


def build_empty_panel(_: dict) -> dict:
    return {"type": "empty"}


def normalize_panel(panel: dict) -> dict:
    kind = panel["kind"]
    builders = {
        "bar": build_bar_panel,
        "trend": build_trend_panel,
        "heatmap": build_heatmap_panel,
        "scatter": build_scatter_panel,
        "legend": build_legend_panel,
        "empty": build_empty_panel,
    }
    if kind not in builders:
        raise SystemExit(f"Unsupported request panel kind: {kind}")
    normalized = builders[kind](panel)
    return {key: value for key, value in normalized.items() if value is not None}


def build_spec(request: dict) -> dict:
    panels = [normalize_panel(panel) for panel in request["panels"]]
    spec = {
        "style": {**DEFAULT_STYLE, **request.get("style", {})},
        "layout": merge_layout(request.get("layout"), len(panels)),
        "panels": panels,
    }
    if "suptitle" in request:
        spec["suptitle"] = request["suptitle"]
    return spec


def main() -> int:
    args = parse_args()
    spec_json = json.dumps(build_spec(load_request(args)), ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(spec_json + "\n", encoding="utf-8")
    else:
        sys.stdout.write(spec_json)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
