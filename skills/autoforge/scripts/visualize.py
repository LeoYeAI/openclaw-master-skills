#!/usr/bin/env python3
"""
AutoForge Visualizer
Reads results.tsv and generates a pass-rate chart as PNG.
Usage: python3 visualize.py [results.tsv] [--output ./results/progress.png] [--title "Skill Name"]
"""

import sys
import csv
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Generate pass-rate progress chart from autoforge results.")
    parser.add_argument("results", nargs="?", default="results.tsv", help="Path to results TSV file")
    parser.add_argument("--output", default="./results/af-progress.png", help="Output PNG path")
    parser.add_argument("--title", default="AutoForge Progress", help="Chart title")
    args = parser.parse_args()

    # Read TSV
    rows = []
    with open(args.results, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)

    if not rows:
        print("No data in results file.")
        sys.exit(1)

    # Extract data
    iterations = list(range(1, len(rows) + 1))

    # Parse pass rate (e.g. "83%" or "0.83")
    pass_rates = []
    for r in rows:
        val = r.get("pass_rate", "0").strip().rstrip("%")
        try:
            v = float(val)
            if v <= 1.0:
                v *= 100
            pass_rates.append(v)
        except ValueError:
            pass_rates.append(0)

    statuses = [r.get("status", "keep") for r in rows]
    changes = [r.get("change_description", "") for r in rows]

    # Matplotlib chart
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#1a1a2e")
        ax.set_facecolor("#16213e")

        # Line
        ax.plot(iterations, pass_rates, color="#e94560", linewidth=2.5, zorder=3, marker="o", markersize=8)

        # Color points by status
        keep_statuses = {"keep", "improved", "retained", "baseline", "best"}
        for i, (x, y, status) in enumerate(zip(iterations, pass_rates, statuses)):
            color = "#00b4d8" if status in keep_statuses else "#e94560"
            ax.scatter(x, y, color=color, s=100, zorder=4)

        # 80% threshold line
        ax.axhline(y=80, color="#ffffff", linestyle="--", linewidth=1, alpha=0.4, label="80% target")

        # Axes
        ax.set_xlabel("Iteration", color="#cccccc", fontsize=11)
        ax.set_ylabel("Pass Rate (%)", color="#cccccc", fontsize=11)
        ax.set_title(args.title, color="#ffffff", fontsize=14, fontweight="bold", pad=15)
        ax.set_ylim(0, 105)
        ax.set_xticks(iterations)
        ax.tick_params(colors="#cccccc")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444444")

        # Legend
        keep_patch = mpatches.Patch(color="#00b4d8", label="Keep/Improved")
        discard_patch = mpatches.Patch(color="#e94560", label="Discard")
        ax.legend(handles=[keep_patch, discard_patch], facecolor="#1a1a2e",
                  labelcolor="#cccccc", framealpha=0.8)

        # Annotate best pass rate
        best_idx = pass_rates.index(max(pass_rates))
        ax.annotate(f"Best: {max(pass_rates):.0f}%",
                    xy=(iterations[best_idx], pass_rates[best_idx]),
                    xytext=(iterations[best_idx] + 0.3, pass_rates[best_idx] - 8),
                    color="#ffffff", fontsize=10,
                    arrowprops=dict(arrowstyle="->", color="#ffffff", lw=1.2))

        # Change labels (short, below X axis)
        for i, (x, change) in enumerate(zip(iterations, changes)):
            short = change[:20] + "…" if len(change) > 20 else change
            ax.text(x, -12, short, ha="center", va="top", fontsize=7,
                    color="#888888", rotation=30, transform=ax.get_xaxis_transform())

        # Ensure output directory exists
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)

        plt.tight_layout()
        plt.savefig(args.output, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        print(f"Chart saved: {args.output}")
        return args.output

    except ImportError:
        # Fallback: ASCII chart
        print(f"\n📊 {args.title}")
        print("─" * 50)
        for i, (x, y, s) in enumerate(zip(iterations, pass_rates, statuses)):
            bar = "█" * int(y / 5)
            icon = "✅" if s in ("keep", "improved", "retained", "baseline", "best") else "❌"
            print(f"  Iter {x:2d} {icon}  {bar:<20} {y:.0f}%")
        print(f"\n  Best: {max(pass_rates):.0f}% @ Iter {pass_rates.index(max(pass_rates))+1}")
        print("─" * 50)
        print("(matplotlib not installed — ASCII fallback)")
        sys.exit(0)


if __name__ == "__main__":
    main()
