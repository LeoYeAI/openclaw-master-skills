#!/usr/bin/env python3
"""
portfolio_chart.py — Generate portfolio PnL chart for Telegram sharing.

Fetches portfolio trade history from Katbot.ai, reconstructs cumulative
realized PnL from matched fills using FIFO coin-level matching, and saves
an 800x450px dark-theme PNG suitable for Telegram.

Usage:
    python3 portfolio_chart.py [--window 24H|7D|30D] [--output PATH] [--json]

Environment:
    Requires PYTHONPATH={baseDir}/tools so katbot_client imports resolve.
    Auth credentials are loaded automatically from the identity directory.
"""
import argparse
import collections
import json
import os
import pathlib
import sys
from datetime import datetime, timezone

# ── katbot_client import ───────────────────────────────────────────────────────
# Follow btc_momentum.py pattern: PYTHONPATH-first, fallback for direct invocation
_TOOLS_DIR = str(pathlib.Path(__file__).parent.resolve())
try:
    from katbot_client import get_token, get_portfolio_history, get_config
except ImportError:
    sys.path.insert(0, _TOOLS_DIR)
    from katbot_client import get_token, get_portfolio_history, get_config

# ── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_OUTPUT_DIR = os.path.expanduser("~/.openclaw/workspace")
CHART_WIDTH_PX  = 800
CHART_HEIGHT_PX = 450
DPI = 100  # 800/100=8in, 450/100=4.5in → exactly 800×450px

# Dark theme palette (Telegram dark-mode compatible)
BG_COLOR        = "#1a1a2e"
PANEL_COLOR     = "#16213e"
GRID_COLOR      = "#2a2a4a"
TEXT_COLOR      = "#e0e0e0"
SUBTEXT_COLOR   = "#8888aa"
WATERMARK_COLOR = "#333355"
GREEN_LINE      = "#00d4aa"
RED_LINE        = "#ff4466"
ZERO_LINE_COLOR = "#555577"


# ── Dependency loader ─────────────────────────────────────────────────────────

def _require_matplotlib():
    """Import and configure matplotlib for PNG rendering. Exits with clear error if missing."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend — required for headless use
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import matplotlib.ticker as mticker
        return plt, mdates, mticker
    except ImportError:
        print(
            "ERROR: matplotlib is not installed.\n"
            f"  Run: pip install -r {_TOOLS_DIR}/../requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)


# ── PnL Reconstruction ────────────────────────────────────────────────────────

def reconstruct_cumulative_pnl(trades: list) -> list:
    """Reconstruct cumulative realized PnL from raw Hyperliquid fill events.

    Algorithm: FIFO position matching per coin, with fees streamed as they occur.

    Each fill record has:
      coin  — token symbol (e.g. "SOL")
      side  — "B" (buy) or "A" (sell/ask)
      sz    — fill size in base units
      px    — fill price in USD
      time  — epoch milliseconds
      fee   — absolute USD fee for this fill (always positive)

    Fill direction:
      "B" delta = +sz  (buying: opens long or closes short)
      "A" delta = -sz  (selling: opens short or closes long)

    FIFO matching:
      When delta is opposite sign to net_position, match against front of
      inventory deque, computing realized PnL per matched lot. Fees deducted
      from cumulative PnL on every fill regardless of match.

    Returns:
        List of (timestamp_ms, cumulative_pnl_usd) tuples, ascending by time.
        Always starts with an anchor (first_trade_time, 0.0).
        Returns [] if trades is empty.
    """
    if not trades:
        return []

    sorted_trades = sorted(trades, key=lambda t: t["time"])

    # Per-coin inventory: deque of [entry_price, signed_size]
    # positive signed_size = long units, negative = short units
    inventory: dict = collections.defaultdict(collections.deque)
    net_position: dict = collections.defaultdict(float)

    cumulative_pnl = 0.0
    series = [(sorted_trades[0]["time"], 0.0)]  # anchor at zero

    for fill in sorted_trades:
        coin  = fill["coin"]
        side  = fill["side"]
        sz    = float(fill["sz"])
        px    = float(fill["px"])
        fee   = float(fill.get("fee", 0.0))

        delta = sz if side == "B" else -sz

        prev_net = net_position[coin]

        # Fee is deducted immediately on every fill
        cumulative_pnl -= fee

        if prev_net == 0.0:
            # Opening a fresh position
            inventory[coin].append([px, delta])

        elif (prev_net > 0 and delta > 0) or (prev_net < 0 and delta < 0):
            # Adding to existing position (same direction)
            inventory[coin].append([px, delta])

        else:
            # Closing or reducing against existing inventory (FIFO match)
            remaining = abs(delta)

            while remaining > 0 and inventory[coin]:
                entry_px, entry_sz = inventory[coin][0]
                matched = min(abs(entry_sz), remaining)

                if entry_sz > 0:
                    # Long position closed by a sell
                    realized = (px - entry_px) * matched
                else:
                    # Short position closed by a buy
                    realized = (entry_px - px) * matched

                cumulative_pnl += realized
                remaining -= matched

                if matched >= abs(entry_sz):
                    inventory[coin].popleft()
                else:
                    # Partial match — update remaining entry
                    sign = 1 if entry_sz > 0 else -1
                    inventory[coin][0][1] = sign * (abs(entry_sz) - matched)

            # If remaining > 0 the position flipped — open new side
            if remaining > 0:
                new_sign = 1 if delta > 0 else -1
                inventory[coin].append([px, new_sign * remaining])

        net_position[coin] = prev_net + delta
        series.append((fill["time"], round(cumulative_pnl, 6)))

    return series


# ── Chart Rendering ───────────────────────────────────────────────────────────

def _x_axis_settings(window: str, mdates):
    """Return (locator, formatter) appropriate for the given time window."""
    if window == "24H":
        return mdates.HourLocator(interval=2), mdates.DateFormatter("%H:%M")
    elif window == "30D":
        return mdates.DayLocator(interval=3), mdates.DateFormatter("%b %d")
    else:  # 7D
        return mdates.DayLocator(interval=1), mdates.DateFormatter("%a %b %d")


def render_chart(series: list, portfolio_data: dict, window: str, output_path: str) -> str:
    """Render cumulative PnL line chart and save as PNG.

    Args:
        series: List of (timestamp_ms, cumulative_pnl) from reconstruct_cumulative_pnl()
        portfolio_data: Full API response dict (for annotations)
        window: Time window label — "24H", "7D", or "30D"
        output_path: Absolute path to write the PNG

    Returns:
        Absolute path of saved PNG.
    """
    plt, mdates, mticker = _require_matplotlib()

    timestamps_ms = [p[0] for p in series]
    pnl_values    = [p[1] for p in series]

    datetimes = [
        datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
        for ts in timestamps_ms
    ]

    final_pnl  = pnl_values[-1] if pnl_values else 0.0
    line_color = GREEN_LINE if final_pnl >= 0 else RED_LINE

    # Pull annotation values from API summary (authoritative totals)
    portfolio_name = portfolio_data.get("portfolio_name", "Portfolio")
    total_pnl_usd  = float(portfolio_data.get("total_pnl_usd", 0) or 0)
    total_pnl_pct  = float(portfolio_data.get("total_pnl_pct", 0) or 0)
    fees_usd       = float(portfolio_data.get("trade_fees_usd", 0) or 0)
    funding_pnl    = float(portfolio_data.get("funding_pnl_usd", 0) or 0)

    # ── Figure setup ──────────────────────────────────────────────────────────
    fig, ax = plt.subplots(
        figsize=(CHART_WIDTH_PX / DPI, CHART_HEIGHT_PX / DPI),
        dpi=DPI,
    )
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(PANEL_COLOR)

    # ── Plot ──────────────────────────────────────────────────────────────────
    ax.plot(datetimes, pnl_values, color=line_color, linewidth=1.8, zorder=3)
    ax.fill_between(datetimes, pnl_values, 0, alpha=0.15, color=line_color, zorder=2)
    ax.axhline(y=0, color=ZERO_LINE_COLOR, linewidth=0.8, linestyle="--", zorder=1)

    # ── Axes styling ──────────────────────────────────────────────────────────
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)

    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v:+,.2f}")
    )

    locator, formatter = _x_axis_settings(window, mdates)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=7)

    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7, zorder=0)
    if len(datetimes) >= 2:
        ax.set_xlim(datetimes[0], datetimes[-1])

    # ── Title ─────────────────────────────────────────────────────────────────
    fig.suptitle(
        f"Portfolio PnL — {window} | {portfolio_name}",
        color=TEXT_COLOR, fontsize=11, fontweight="bold", y=0.97,
    )

    # ── Annotations ───────────────────────────────────────────────────────────
    pnl_sign  = "+" if total_pnl_usd >= 0 else ""
    pnl_label = f"Total PnL: {pnl_sign}${total_pnl_usd:,.2f}  ({pnl_sign}{total_pnl_pct:.3f}%)"
    ax.text(
        0.01, 0.97, pnl_label,
        transform=ax.transAxes,
        color=GREEN_LINE if total_pnl_usd >= 0 else RED_LINE,
        fontsize=8.5, fontweight="bold", va="top",
    )

    fees_label = f"Fees: ${fees_usd:,.4f}  |  Funding: ${funding_pnl:+,.4f}"
    ax.text(
        0.99, 0.97, fees_label,
        transform=ax.transAxes,
        color=SUBTEXT_COLOR, fontsize=7.5, va="top", ha="right",
    )

    ax.text(
        0.99, 0.02, "katbot.ai",
        transform=ax.transAxes,
        color=WATERMARK_COLOR, fontsize=7, va="bottom", ha="right", style="italic",
    )

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(output_path, dpi=DPI, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)

    return output_path


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate a cumulative PnL chart for the active Katbot portfolio."
    )
    parser.add_argument(
        "--window",
        choices=["24H", "7D", "30D"],
        default="7D",
        help="Time window for trade history (default: 7D)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output PNG file path "
            "(default: ~/.openclaw/workspace/portfolio_chart_<window>.png)"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print JSON result to stdout (for agent consumption)",
    )
    args = parser.parse_args()

    output_path = args.output or os.path.join(
        DEFAULT_OUTPUT_DIR,
        f"portfolio_chart_{args.window}.png",
    )
    output_path = os.path.abspath(output_path)

    # Load portfolio ID from config (written by katbot_onboard.py)
    config = get_config()
    portfolio_id = config.get("portfolio_id")
    if not portfolio_id:
        msg = (
            "ERROR: portfolio_id not found in katbot_config.json. "
            "Run katbot_onboard.py first."
        )
        if args.as_json:
            print(json.dumps({"status": "error", "error": msg}))
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    # Fetch trade history
    try:
        token = get_token()
        portfolio_data = get_portfolio_history(
            token,
            portfolio_id=int(portfolio_id),
            window=args.window,
            granularity="4h",
            limit=100,
        )
    except Exception as e:
        if args.as_json:
            print(json.dumps({"status": "error", "error": str(e)}))
        else:
            print(f"ERROR: Failed to fetch portfolio history: {e}", file=sys.stderr)
        sys.exit(1)

    trades = portfolio_data.get("trades", [])

    if not trades:
        msg = (
            f"No trades found in the {args.window} window for portfolio "
            f"'{portfolio_data.get('portfolio_name', portfolio_id)}'."
        )
        if args.as_json:
            print(json.dumps({
                "status": "no_data",
                "window": args.window,
                "portfolio_name": portfolio_data.get("portfolio_name"),
                "message": msg,
            }))
        else:
            print(msg)
        sys.exit(0)

    # Reconstruct cumulative PnL and render chart
    series = reconstruct_cumulative_pnl(trades)

    try:
        saved_path = render_chart(
            series=series,
            portfolio_data=portfolio_data,
            window=args.window,
            output_path=output_path,
        )
    except Exception as e:
        if args.as_json:
            print(json.dumps({"status": "error", "error": str(e)}))
        else:
            print(f"ERROR: Chart rendering failed: {e}", file=sys.stderr)
        sys.exit(1)

    final_pnl     = float(portfolio_data.get("total_pnl_usd", 0) or 0)
    final_pnl_pct = float(portfolio_data.get("total_pnl_pct", 0) or 0)
    fees          = float(portfolio_data.get("trade_fees_usd", 0) or 0)

    if args.as_json:
        print(json.dumps({
            "status": "ok",
            "chart_path": saved_path,
            "window": args.window,
            "portfolio_name": portfolio_data.get("portfolio_name"),
            "total_pnl_usd": final_pnl,
            "total_pnl_pct": final_pnl_pct,
            "trade_fees_usd": fees,
            "trade_count": len(trades),
        }, indent=2))
    else:
        sign = "+" if final_pnl >= 0 else ""
        print(f"Chart saved: {saved_path}")
        print(
            f"Portfolio: {portfolio_data.get('portfolio_name')} | "
            f"Window: {args.window} | "
            f"PnL: {sign}${final_pnl:,.2f} ({sign}{final_pnl_pct:.3f}%) | "
            f"Fees: ${fees:,.4f} | "
            f"Trades: {len(trades)}"
        )


if __name__ == "__main__":
    main()
