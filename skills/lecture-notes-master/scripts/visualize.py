#!/usr/bin/env python3
"""
Lecture Notes Master - Visualization Generator
Generates Matplotlib charts for embedding in Obsidian notes.

Usage:
    python3 visualize.py --type bar --title "Memory Bandwidth Comparison" \
        --data '{"labels":["Global","Shared","Register"],"values":[900,12000,48000]}' \
        --output "./memory-bandwidth.png"

    python3 visualize.py --type line --title "Speedup vs Threads" \
        --data '{"x":[1,2,4,8,16,32],"y":[1,1.9,3.7,7,12.5,20],"ideal":[1,2,4,8,16,32]}' \
        --output "./speedup-curve.png"

    python3 visualize.py --type scatter --title "Latency vs Throughput" \
        --data '{"x":[1,2,3,4,5],"y":[100,80,50,30,10],"labels":["A","B","C","D","E"]}' \
        --output "./latency-throughput.png"

    python3 visualize.py --type timeline --title "Project Milestones" \
        --data '{"events":["Phase 1","Phase 2","Phase 3"],"starts":[0,3,6],"ends":[3,6,9]}' \
        --output "./milestones.png"

    python3 visualize.py --type heatmap --title "Bank Conflict Pattern" \
        --data '{"matrix":[[0,1,2,3],[1,0,1,2],[2,1,0,1],[3,2,1,0]],"labels":["T0","T1","T2","T3"]}' \
        --output "./bank-conflicts.png"

    python3 visualize.py --type comparison --title "AoS vs SoA Performance" \
        --data '{"categories":["Sequential","Random","Stride"],"group_a":[100,45,30],"group_b":[100,85,90],"label_a":"AoS","label_b":"SoA"}' \
        --output "./aos-vs-soa.png"
"""

import os
import sys
import json
import argparse

# Color scheme consistent with Mermaid templates
COLORS = {
    "green": "#4CAF50",
    "blue": "#2196F3",
    "orange": "#FF9800",
    "red": "#F44336",
    "purple": "#9C27B0",
    "teal": "#009688",
    "grey": "#607D8B",
    "light_green": "#8BC34A",
    "amber": "#FFC107",
    "deep_orange": "#FF5722",
}

COLOR_LIST = list(COLORS.values())

# Style configuration
STYLE_CONFIG = {
    "figure.facecolor": "#FAFAFA",
    "axes.facecolor": "#FFFFFF",
    "axes.edgecolor": "#CCCCCC",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.color": "#CCCCCC",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
}


def setup_matplotlib():
    """Import and configure matplotlib."""
    try:
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt

        plt.rcParams.update(STYLE_CONFIG)
        return plt
    except ImportError:
        print(
            "Error: matplotlib not installed. Run: pip3 install matplotlib",
            file=sys.stderr,
        )
        sys.exit(1)


def _import_numpy():
    """Import numpy with error handling."""
    try:
        import numpy as np

        return np
    except ImportError:
        print("Error: numpy not installed. Run: pip3 install numpy", file=sys.stderr)
        sys.exit(1)


def generate_bar(plt, data, title, output):
    """Generate a bar chart."""
    labels = data["labels"]
    values = data["values"]
    colors = data.get("colors", COLOR_LIST[: len(labels)])

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.5)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + max(values) * 0.02,
            f"{val:,.0f}" if isinstance(val, (int, float)) else str(val),
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=11,
        )

    ax.set_title(title, fontweight="bold", pad=15)
    ax.set_ylabel(data.get("ylabel", "Value"))
    if "xlabel" in data:
        ax.set_xlabel(data["xlabel"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()


def generate_line(plt, data, title, output):
    """Generate a line chart (supports multiple lines)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = data["x"]
    # Plot main line
    ax.plot(
        x,
        data["y"],
        "o-",
        color=COLORS["blue"],
        linewidth=2,
        markersize=6,
        label=data.get("label", "Actual"),
    )

    # Plot ideal/reference line if present
    if "ideal" in data:
        ax.plot(
            x,
            data["ideal"],
            "--",
            color=COLORS["grey"],
            linewidth=1.5,
            label=data.get("ideal_label", "Ideal"),
            alpha=0.7,
        )

    # Plot additional lines
    for i, key in enumerate(sorted(k for k in data.keys() if k.startswith("line_"))):
        color = COLOR_LIST[(i + 2) % len(COLOR_LIST)]
        label = data.get(f"label_{key}", key)
        ax.plot(x, data[key], "o-", color=color, linewidth=2, markersize=5, label=label)

    ax.set_title(title, fontweight="bold", pad=15)
    ax.set_xlabel(data.get("xlabel", "X"))
    ax.set_ylabel(data.get("ylabel", "Y"))
    ax.legend(frameon=True, fancybox=True, shadow=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()


def generate_scatter(plt, data, title, output):
    """Generate a scatter plot with optional labels and sizing."""
    np = _import_numpy()

    x = data["x"]
    y = data["y"]
    labels = data.get("labels", [])
    sizes = data.get("sizes", [80] * len(x))
    colors = data.get("colors", [COLORS["blue"]] * len(x))

    if isinstance(colors, str):
        colors = [colors] * len(x)
    elif len(colors) < len(x):
        colors = [COLOR_LIST[i % len(COLOR_LIST)] for i in range(len(x))]

    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        x, y, s=sizes, c=colors, alpha=0.7, edgecolors="white", linewidth=1
    )

    # Add labels to points if provided
    for i, label in enumerate(labels):
        ax.annotate(
            label,
            (x[i], y[i]),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=10,
            fontweight="bold",
            color=COLORS["grey"],
        )

    ax.set_title(title, fontweight="bold", pad=15)
    ax.set_xlabel(data.get("xlabel", "X"))
    ax.set_ylabel(data.get("ylabel", "Y"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Add trend line if requested
    if data.get("trendline", False) and len(x) >= 2:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_sorted = sorted(x)
        ax.plot(
            x_sorted, p(x_sorted), "--", color=COLORS["red"], alpha=0.5, label="Trend"
        )
        ax.legend(frameon=True)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()


def generate_timeline(plt, data, title, output):
    """Generate a horizontal timeline / Gantt-like chart."""
    np = _import_numpy()

    events = data["events"]
    starts = data["starts"]
    ends = data["ends"]
    colors = data.get(
        "colors", [COLOR_LIST[i % len(COLOR_LIST)] for i in range(len(events))]
    )
    categories = data.get("categories", None)

    fig, ax = plt.subplots(figsize=(12, max(4, len(events) * 0.6 + 1)))

    y_positions = list(range(len(events)))

    # Group by categories if provided
    if categories:
        unique_cats = list(dict.fromkeys(categories))
        cat_colors = {
            cat: COLOR_LIST[i % len(COLOR_LIST)] for i, cat in enumerate(unique_cats)
        }
        colors = [cat_colors[cat] for cat in categories]

    for i, (event, start, end) in enumerate(zip(events, starts, ends)):
        duration = end - start
        bar = ax.barh(
            i,
            duration,
            left=start,
            height=0.5,
            color=colors[i],
            edgecolor="white",
            linewidth=1,
            alpha=0.85,
        )
        # Label inside bar
        mid = start + duration / 2
        ax.text(
            mid,
            i,
            event,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="white",
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(["" for _ in events])  # Labels are inside bars
    ax.set_xlabel(data.get("xlabel", "Time"))
    ax.set_title(title, fontweight="bold", pad=15)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Add category legend if applicable
    if categories:
        unique_cats = list(dict.fromkeys(categories))
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor=cat_colors[cat], label=cat) for cat in unique_cats
        ]
        ax.legend(handles=legend_elements, loc="lower right", frameon=True)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()


def generate_heatmap(plt, data, title, output):
    """Generate a heatmap."""
    np = _import_numpy()

    matrix = np.array(data["matrix"])
    labels = data.get("labels", [str(i) for i in range(matrix.shape[0])])
    col_labels = data.get("col_labels", labels)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    # Add text annotations
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            color = "white" if val > matrix.max() * 0.6 else "black"
            ax.text(
                j,
                i,
                f"{val:.1f}" if isinstance(val, float) else str(int(val)),
                ha="center",
                va="center",
                color=color,
                fontweight="bold",
            )

    ax.set_title(title, fontweight="bold", pad=15)
    fig.colorbar(im, ax=ax, shrink=0.8)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()


def generate_comparison(plt, data, title, output):
    """Generate a grouped bar chart for comparison."""
    np = _import_numpy()

    categories = data["categories"]
    group_a = data["group_a"]
    group_b = data["group_b"]
    label_a = data.get("label_a", "Group A")
    label_b = data.get("label_b", "Group B")

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars_a = ax.bar(
        x - width / 2,
        group_a,
        width,
        label=label_a,
        color=COLORS["blue"],
        edgecolor="white",
        linewidth=0.5,
    )
    bars_b = ax.bar(
        x + width / 2,
        group_b,
        width,
        label=label_b,
        color=COLORS["green"],
        edgecolor="white",
        linewidth=0.5,
    )

    # Value labels
    for bars in [bars_a, bars_b]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + max(group_a + group_b) * 0.02,
                f"{height:,.0f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

    ax.set_title(title, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel(data.get("ylabel", "Value"))
    ax.legend(frameon=True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()


def generate_pie(plt, data, title, output):
    """Generate a pie chart."""
    labels = data["labels"]
    values = data["values"]
    colors = data.get("colors", COLOR_LIST[: len(labels)])
    explode = data.get("explode", [0.05] * len(labels))

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        explode=explode,
        autopct="%1.1f%%",
        pctdistance=0.85,
        startangle=90,
        textprops={"fontsize": 11},
    )

    for autotext in autotexts:
        autotext.set_fontweight("bold")

    ax.set_title(title, fontweight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()


def generate_radar(plt, data, title, output):
    """Generate a radar/spider chart."""
    np = _import_numpy()

    categories = data["categories"]
    values_a = data["values_a"]
    values_b = data.get("values_b", None)
    label_a = data.get("label_a", "Option A")
    label_b = data.get("label_b", "Option B")

    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    values_a_closed = values_a + values_a[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(
        angles, values_a_closed, "o-", linewidth=2, color=COLORS["blue"], label=label_a
    )
    ax.fill(angles, values_a_closed, alpha=0.15, color=COLORS["blue"])

    if values_b:
        values_b_closed = values_b + values_b[:1]
        ax.plot(
            angles,
            values_b_closed,
            "o-",
            linewidth=2,
            color=COLORS["green"],
            label=label_b,
        )
        ax.fill(angles, values_b_closed, alpha=0.15, color=COLORS["green"])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_title(title, fontweight="bold", pad=25, fontsize=14)
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()


CHART_GENERATORS = {
    "bar": generate_bar,
    "line": generate_line,
    "scatter": generate_scatter,
    "timeline": generate_timeline,
    "heatmap": generate_heatmap,
    "comparison": generate_comparison,
    "pie": generate_pie,
    "radar": generate_radar,
}


def main():
    parser = argparse.ArgumentParser(
        description="Lecture Notes Master - Visualization Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Chart types: bar, line, scatter, timeline, heatmap, comparison, pie, radar

Examples:
  python3 visualize.py --type bar --title "Latency" \\
      --data '{"labels":["L1","L2","DRAM"],"values":[5,30,400],"ylabel":"Cycles"}' \\
      --output "./latency.png"

  python3 visualize.py --type scatter --title "Latency vs Throughput" \\
      --data '{"x":[1,2,3],"y":[100,50,10],"labels":["A","B","C"]}' \\
      --output "./scatter.png"

  python3 visualize.py --type timeline --title "Pipeline" \\
      --data '{"events":["Load","Compute","Store"],"starts":[0,2,5],"ends":[2,5,7]}' \\
      --output "./pipeline.png"
        """,
    )
    parser.add_argument(
        "--type",
        "-t",
        required=True,
        choices=list(CHART_GENERATORS.keys()),
        help="Chart type",
    )
    parser.add_argument("--title", required=True, help="Chart title")
    parser.add_argument("--data", required=True, help="JSON data for the chart")
    parser.add_argument("--output", "-o", required=True, help="Output file path (.png)")

    args = parser.parse_args()

    # Parse JSON data
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON data: {e}", file=sys.stderr)
        sys.exit(1)

    # Setup matplotlib
    plt = setup_matplotlib()

    # Generate chart
    generator = CHART_GENERATORS[args.type]
    output_path = os.path.expanduser(args.output)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    generator(plt, data, args.title, output_path)
    print(f"  [OK] Chart saved: {output_path}")


if __name__ == "__main__":
    main()
