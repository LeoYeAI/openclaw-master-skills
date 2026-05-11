"""Palaia UI — Professional box-drawing table renderer and formatting helpers.

No external dependencies. Pure Python with Unicode box-drawing characters.
All CLI output flows through this module for consistency.

Box-drawing characters used:
  Corners:  ┌ ┐ └ ┘
  Borders:  │ ─
  T-joins:  ├ ┤ ┬ ┴ ┼
"""

from __future__ import annotations

import shutil
from typing import Sequence

from palaia import __version__

# ── Constants ────────────────────────────────────────────────────────────────

HEADER_LINE = f"Palaia v{__version__} — Local memory for AI agents"
HEADER_URL = "(c) 2026 byte5 GmbH — https://github.com/iret77/palaia"

# Box-drawing chars
B_TL = "\u250c"  # ┌
B_TR = "\u2510"  # ┐
B_BL = "\u2514"  # └
B_BR = "\u2518"  # ┘
B_H = "\u2500"  # ─
B_V = "\u2502"  # │
B_LT = "\u251c"  # ├
B_RT = "\u2524"  # ┤
B_TT = "\u252c"  # ┬
B_BT = "\u2534"  # ┴
B_X = "\u253c"  # ┼


# ── Terminal helpers ─────────────────────────────────────────────────────────


def terminal_width() -> int:
    """Get terminal width, default 80 if unavailable."""
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80


def truncate(text: str, max_len: int, suffix: str = "..") -> str:
    """Truncate text to max_len, appending suffix if truncated."""
    if len(text) <= max_len:
        return text
    if max_len <= len(suffix):
        return text[:max_len]
    return text[: max_len - len(suffix)] + suffix


# ── Header ───────────────────────────────────────────────────────────────────


def header() -> str:
    """Return the standard Palaia header (2 lines)."""
    return f"{HEADER_LINE}\n{HEADER_URL}"


def print_header() -> None:
    """Print the standard header."""
    print(header())


# ── Table rendering ──────────────────────────────────────────────────────────


def _cell_widths(rows: Sequence[tuple[str, str]], key_min: int = 16, val_min: int = 20) -> tuple[int, int]:
    """Calculate column widths from rows (key-value pairs)."""
    tw = terminal_width()
    # Overhead: │ + space + key + space + │ + space + val + space + │ = 7 + key_w + val_w
    overhead = 7

    max_key = max((len(r[0]) for r in rows), default=key_min)
    max_val = max((len(r[1]) for r in rows), default=val_min)

    key_w = max(max_key, key_min)
    val_w = max(max_val, val_min)

    # Fit within terminal
    total = overhead + key_w + val_w
    if total > tw:
        # Shrink value column first, then key if needed
        val_w = max(val_min, tw - overhead - key_w)
        total = overhead + key_w + val_w
        if total > tw:
            key_w = max(key_min, tw - overhead - val_w)

    return key_w, val_w


def table_kv(rows: Sequence[tuple[str, str]], key_min: int = 16, val_min: int = 20) -> str:
    """Render a key-value table (no header row, just data).

    Example output:
    ┌──────────────────┬────────────────────────────────────────────┐
    │ Root             │ /home/claw/.openclaw/workspace/.palaia     │
    │ Store version    │ v1.5.2                                     │
    └──────────────────┴────────────────────────────────────────────┘
    """
    if not rows:
        return ""

    kw, vw = _cell_widths(rows, key_min, val_min)
    lines: list[str] = []

    # Top border
    lines.append(f"{B_TL}{B_H * (kw + 2)}{B_TT}{B_H * (vw + 2)}{B_TR}")

    # Data rows
    for key, val in rows:
        k = truncate(key, kw).ljust(kw)
        v = truncate(val, vw).ljust(vw)
        lines.append(f"{B_V} {k} {B_V} {v} {B_V}")

    # Bottom border
    lines.append(f"{B_BL}{B_H * (kw + 2)}{B_BT}{B_H * (vw + 2)}{B_BR}")

    return "\n".join(lines)


def _multi_col_widths(
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    min_widths: Sequence[int] | None = None,
) -> list[int]:
    """Calculate column widths for a multi-column table."""
    tw = terminal_width()
    n = len(headers)
    if min_widths is None:
        min_widths = [6] * n

    # Start with max of header width or content width per column
    widths = []
    for i in range(n):
        col_max = max(
            len(headers[i]),
            max((len(str(row[i])) for row in rows), default=0),
            min_widths[i],
        )
        widths.append(col_max)

    # Overhead: │ + (space + col + space + │) * n
    overhead = 1 + n * 3  # leading │ plus per-col " " + " │"
    total = overhead + sum(widths)

    # If over terminal width, shrink largest columns proportionally
    if total > tw and tw > overhead + sum(min_widths):
        budget = tw - overhead
        # First pass: fix columns that are already at or below their share
        shares = [w / sum(widths) * budget for w in widths]
        for i in range(n):
            widths[i] = max(min_widths[i], min(widths[i], int(shares[i])))

    return widths


def table_multi(
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    min_widths: Sequence[int] | None = None,
) -> str:
    """Render a multi-column table with header row.

    Example output:
    ┌──────────┬────────┬──────────────────┬────────────┐
    │ ID       │ Scope  │ Title            │ Age        │
    ├──────────┼────────┼──────────────────┼────────────┤
    │ 050d2e70 │ team   │ CONTEXT (chunk)  │ 2d ago     │
    └──────────┴────────┴──────────────────┴────────────┘
    """
    if not headers:
        return ""

    n = len(headers)
    widths = _multi_col_widths(headers, rows, min_widths)
    lines: list[str] = []

    def h_line(left: str, mid: str, right: str) -> str:
        segments = [B_H * (w + 2) for w in widths]
        return left + mid.join(segments) + right

    def data_line(cells: Sequence[str]) -> str:
        parts = []
        for i, cell in enumerate(cells):
            parts.append(f" {truncate(str(cell), widths[i]).ljust(widths[i])} ")
        return B_V + B_V.join(parts) + B_V

    # Top border
    lines.append(h_line(B_TL, B_TT, B_TR))
    # Header
    lines.append(data_line(headers))
    # Separator
    lines.append(h_line(B_LT, B_X, B_RT))
    # Data
    for row in rows:
        # Pad row if shorter than headers
        padded = list(row) + [""] * (n - len(row))
        lines.append(data_line(padded[:n]))
    # Bottom border
    lines.append(h_line(B_BL, B_BT, B_BR))

    return "\n".join(lines)


# ── Section helpers ──────────────────────────────────────────────────────────


def section(title: str) -> str:
    """Return a section title line."""
    return f"\n{title}"


def status_label(status: str) -> str:
    """Return a clean text label for a status level (no emoji).

    ok   → [ok]
    warn → [warn]
    error → [error]
    info → [info]
    """
    return f"[{status}]"


# ── Age / relative time ─────────────────────────────────────────────────────


def relative_time(iso_str: str) -> str:
    """Convert an ISO datetime string to a relative time like '2m ago', '3h ago', '5d ago'."""
    if not iso_str:
        return "unknown"
    try:
        from datetime import datetime, timezone

        # Parse ISO format
        if iso_str.endswith("Z"):
            iso_str = iso_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - dt
        seconds = int(delta.total_seconds())

        if seconds < 0:
            return "just now"
        if seconds < 60:
            return f"{seconds}s ago"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        days = seconds // 86400
        if days < 30:
            return f"{days}d ago"
        if days < 365:
            return f"{days // 30}mo ago"
        return f"{days // 365}y ago"
    except Exception:
        return "unknown"


# ── Disk size formatting ─────────────────────────────────────────────────────


def format_size(bytes_val: int) -> str:
    """Format bytes into human-readable size."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    if bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    return f"{bytes_val / (1024 * 1024 * 1024):.1f} GB"


# ── Score bar ────────────────────────────────────────────────────────────────


def score_display(score: float, width: int = 10) -> str:
    """Render a score as a compact numeric + bar.

    Example: 0.87 [========  ]
    """
    filled = int(round(score * width))
    filled = max(0, min(filled, width))
    bar = "#" * filled + "." * (width - filled)
    return f"{score:.2f} [{bar}]"
