"""Brier Score tracker for prediction market estimator calibration.

Tracks every probability estimate against actual market resolution to measure:
1. Brier Score: mean squared error of probability estimates (lower = better)
2. Calibration: when you say 70%, does it resolve YES ~70% of the time?
3. Estimator comparison: Claude vs Qwen accuracy by category
4. Category breakdown: where are you calibrated vs systematically wrong?

Database: SQLite (lightweight, no deps, persists across restarts)

Usage:
    python brier_tracker.py
"""

import json
import sqlite3
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path.home() / ".openclaw" / "state" / "brier_tracker.db"


def _get_db() -> sqlite3.Connection:
    """Get or create the Brier tracker database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            title TEXT,
            estimated_prob REAL NOT NULL,
            market_price_cents INTEGER NOT NULL,
            confidence REAL,
            estimator TEXT DEFAULT 'unknown',
            edge_pct REAL,
            direction TEXT,
            category TEXT DEFAULT 'unknown',
            info_density REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            created_ts REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS resolutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL UNIQUE,
            outcome INTEGER NOT NULL,
            resolved_at TEXT NOT NULL,
            resolved_ts REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_estimates_ticker ON estimates(ticker);
        CREATE INDEX IF NOT EXISTS idx_estimates_estimator ON estimates(estimator);
        CREATE INDEX IF NOT EXISTS idx_estimates_created ON estimates(created_ts);
        CREATE INDEX IF NOT EXISTS idx_resolutions_ticker ON resolutions(ticker);
    """)

    return db


# ── Logging Estimates ──────────────────────────────────────────────────

def log_estimate(
    ticker: str,
    title: str = "",
    estimated_prob: float = 0.5,
    market_price_cents: int = 50,
    confidence: float = 0.5,
    estimator: str = "unknown",
    edge_pct: float = 0.0,
    direction: str = "fair",
    category: str = "unknown",
    info_density: float = 0.0,
) -> bool:
    """Log a probability estimate for later Brier scoring."""
    try:
        db = _get_db()
        now = datetime.now(timezone.utc)

        db.execute("""
            INSERT INTO estimates
            (ticker, title, estimated_prob, market_price_cents, confidence,
             estimator, edge_pct, direction, category, info_density,
             created_at, created_ts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker, title[:100], estimated_prob, market_price_cents,
            confidence, estimator, edge_pct, direction, category,
            info_density, now.isoformat(), now.timestamp(),
        ))

        db.commit()
        db.close()
        return True

    except Exception as e:
        logger.error(f"Brier: failed to log estimate: {e}")
        return False


def log_estimates_batch(edges: list[dict]) -> int:
    """Log a batch of estimates from the scanner results."""
    count = 0
    for edge in edges:
        success = log_estimate(
            ticker=edge.get("ticker", ""),
            title=edge.get("title", ""),
            estimated_prob=edge.get("estimated_probability", 0.5),
            market_price_cents=int(edge.get("yes_price", 50)),
            confidence=edge.get("confidence", 0.5),
            estimator=edge.get("estimator", "unknown"),
            edge_pct=edge.get("effective_edge_pct", 0),
            direction=edge.get("direction", "fair"),
            category=_infer_category(edge.get("ticker", ""), edge.get("title", "")),
            info_density=edge.get("info_density", 0.0),
        )
        if success:
            count += 1
    return count


def compute_info_density(market: dict) -> float:
    """Compute info_density score (0.0-1.0) for a market from Kalshalyst."""
    score = 0.0

    # News articles
    news = market.get("news", [])
    if isinstance(news, list):
        if len(news) >= 3:
            score += 0.25
        elif len(news) >= 1:
            score += 0.15

    # X signal
    if market.get("x_signal"):
        score += 0.25

    # Economic context
    if market.get("has_economic_context"):
        score += 0.25

    # Liquidity
    volume = market.get("volume", 0) or 0
    oi = market.get("open_interest", 0) or 0
    liquidity = volume + oi
    if liquidity >= 5000:
        score += 0.25
    elif liquidity >= 1000:
        score += 0.15
    elif liquidity >= 100:
        score += 0.08

    return min(score, 1.0)


def _infer_category(ticker: str, title: str) -> str:
    """Infer market category from ticker/title for grouping."""
    combined = f"{ticker} {title}".lower()

    categories = {
        "politics": ["president", "election", "congress", "senate", "potus"],
        "policy": ["tariff", "regulation", "executive order", "legislation"],
        "fed": ["fed", "interest rate", "fomc", "inflation", "cpi"],
        "crypto": ["bitcoin", "btc", "ethereum", "crypto"],
        "geopolitics": ["ukraine", "russia", "china", "taiwan", "iran"],
        "technology": ["ai", "artificial intelligence", "openai", "google"],
        "legal": ["supreme court", "trial", "lawsuit", "indictment"],
    }

    for cat, keywords in categories.items():
        if any(kw in combined for kw in keywords):
            return cat

    return "other"


# ── Resolving Markets ──────────────────────────────────────────────

def resolve_market(ticker: str, outcome: int) -> bool:
    """Record a market resolution."""
    if outcome not in (0, 1):
        logger.error(f"Brier: invalid outcome {outcome} for {ticker}")
        return False

    try:
        db = _get_db()
        now = datetime.now(timezone.utc)

        db.execute("""
            INSERT OR REPLACE INTO resolutions (ticker, outcome, resolved_at, resolved_ts)
            VALUES (?, ?, ?, ?)
        """, (ticker, outcome, now.isoformat(), now.timestamp()))

        db.commit()
        db.close()
        logger.info(f"Brier: resolved {ticker} → {'YES' if outcome == 1 else 'NO'}")
        return True

    except Exception as e:
        logger.error(f"Brier: failed to resolve {ticker}: {e}")
        return False


# ── Brier Score Calculation ────────────────────────────────────────────

def _brier_score(estimates: list[tuple[float, int]]) -> float:
    """Calculate Brier Score: (1/n) * Σ(forecast - outcome)²"""
    if not estimates:
        return 0.0
    n = len(estimates)
    return sum((p - o) ** 2 for p, o in estimates) / n


def _calibration_buckets(estimates: list[tuple[float, int]], n_buckets: int = 5) -> list[dict]:
    """Group estimates into calibration buckets."""
    bucket_size = 1.0 / n_buckets
    buckets = []

    for i in range(n_buckets):
        lo = i * bucket_size
        hi = (i + 1) * bucket_size
        in_bucket = [(p, o) for p, o in estimates if lo <= p < hi or (i == n_buckets - 1 and p == hi)]

        if not in_bucket:
            continue

        avg_forecast = sum(p for p, _ in in_bucket) / len(in_bucket)
        actual_rate = sum(o for _, o in in_bucket) / len(in_bucket)
        error = abs(avg_forecast - actual_rate)

        buckets.append({
            "range": f"{lo:.0%}-{hi:.0%}",
            "count": len(in_bucket),
            "avg_forecast": round(avg_forecast, 3),
            "actual_rate": round(actual_rate, 3),
            "error": round(error, 3),
        })

    return buckets


# ── Reporting ──────────────────────────────────────────────────

def get_brier_report(
    estimator: str = None,
    category: str = None,
    days: int = 90,
) -> str:
    """Generate a human-readable Brier Score report."""
    try:
        db = _get_db()

        # Build query
        cutoff_ts = time.time() - (days * 86400)
        query = """
            SELECT e.estimated_prob, r.outcome, e.estimator, e.category,
                   e.ticker, e.edge_pct, e.confidence
            FROM estimates e
            JOIN resolutions r ON e.ticker = r.ticker
            WHERE e.created_ts > ?
        """
        params = [cutoff_ts]

        if estimator:
            query += " AND e.estimator = ?"
            params.append(estimator)
        if category:
            query += " AND e.category = ?"
            params.append(category)

        query += " GROUP BY e.ticker HAVING e.created_ts = MAX(e.created_ts)"

        rows = db.execute(query, params).fetchall()
        db.close()

        if not rows:
            return f"No resolved estimates in last {days} days."

        # Calculate scores
        all_pairs = [(r[0], r[1]) for r in rows]
        overall_brier = _brier_score(all_pairs)

        # By estimator
        by_estimator = {}
        for est_prob, outcome, est_name, _, _, _, _ in rows:
            by_estimator.setdefault(est_name, []).append((est_prob, outcome))

        # By category
        by_category = {}
        for est_prob, outcome, _, cat, _, _, _ in rows:
            by_category.setdefault(cat, []).append((est_prob, outcome))

        # Calibration
        calibration = _calibration_buckets(all_pairs)

        # Format report
        lines = [
            f"BRIER SCORE REPORT ({days}d lookback)",
            f"{len(rows)} resolved estimates",
            "",
            f"Overall Brier: {overall_brier:.3f}",
        ]

        if overall_brier < 0.15:
            lines.append("  ✓ Excellent calibration")
        elif overall_brier < 0.20:
            lines.append("  ✓ Good calibration")
        elif overall_brier < 0.25:
            lines.append("  ~ Fair calibration")
        else:
            lines.append("  ✗ POOR — worse than coin flip")

        # By estimator
        if len(by_estimator) > 1:
            lines.append("\nBy Estimator:")
            for name, pairs in sorted(by_estimator.items()):
                bs = _brier_score(pairs)
                lines.append(f"  {name}: {bs:.3f} ({len(pairs)} estimates)")

        # By category
        if by_category:
            lines.append("\nBy Category (top 5):")
            sorted_cats = sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            for cat, pairs in sorted_cats:
                bs = _brier_score(pairs)
                flag = " ✗" if bs > 0.25 else ""
                lines.append(f"  {cat}: {bs:.3f} ({len(pairs)}){flag}")

        return "\n".join(lines)

    except Exception as e:
        return f"Brier report error: {e}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(get_brier_report(days=90))
