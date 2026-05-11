"""Memory decay scoring and tier rotation (ADR-004)."""

from __future__ import annotations

import math
from datetime import datetime, timezone


def decay_score(
    days_since_access: float,
    access_count: int = 1,
    lambda_val: float = 0.1,
) -> float:
    """Calculate decay score. Higher = more relevant.

    Formula (ADR-004, Issue #33):
        final_score = time_decay * hit_rate_bonus
        time_decay   = exp(-lambda * days_since_access)
        hit_rate_bonus = 1 + log(1 + access_count)

    access_count=0  → bonus 1.0  (no boost)
    access_count=10 → bonus ~3.4
    access_count=100 → bonus ~5.6
    """
    recency = math.exp(-lambda_val * days_since_access)
    hit_rate_bonus = 1.0 + math.log(1 + access_count)
    return round(recency * hit_rate_bonus, 6)


def classify_tier(
    days_since_access: float,
    score: float,
    hot_threshold_days: int = 7,
    warm_threshold_days: int = 30,
    hot_min_score: float = 0.5,
    warm_min_score: float = 0.1,
) -> str:
    """Determine which tier a memory belongs to."""
    if days_since_access <= hot_threshold_days or score >= hot_min_score:
        return "hot"
    if days_since_access <= warm_threshold_days or score >= warm_min_score:
        return "warm"
    return "cold"


def days_since(dt_str: str) -> float:
    """Calculate days since a given ISO-8601 timestamp."""
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - dt
    return delta.total_seconds() / 86400.0
