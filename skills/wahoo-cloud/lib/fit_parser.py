"""FIT file parser using `fitparse`.

Extracts a session-level summary plus per-second records (power, cadence,
HR, GPS). Lazy-imports fitparse so the module is loadable without the
dependency installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator


def _semicircles_to_deg(value: int | None) -> float | None:
    if value is None:
        return None
    return value * (180.0 / 2**31)


def _ensure_fitparse():
    try:
        import fitparse  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "fitparse not installed. Run: pip install --user 'fitparse>=1.2,<2'"
        ) from e
    return fitparse


def parse(path: str | Path) -> dict[str, Any]:
    fitparse = _ensure_fitparse()
    fit = fitparse.FitFile(str(path))

    session = _first_session(fit)
    records = list(_iter_records(fit))

    summary = {
        "fit_path": str(path),
        "start_time": _iso(session.get("start_time")) if session else None,
        "total_elapsed_time_s": _f(session, "total_elapsed_time"),
        "total_timer_time_s": _f(session, "total_timer_time"),
        "total_distance_m": _f(session, "total_distance"),
        "total_ascent_m": _f(session, "total_ascent"),
        "total_descent_m": _f(session, "total_descent"),
        "avg_speed_ms": _f(session, "avg_speed"),
        "max_speed_ms": _f(session, "max_speed"),
        "avg_power_w": _f(session, "avg_power"),
        "max_power_w": _f(session, "max_power"),
        "normalized_power_w": _f(session, "normalized_power"),
        "training_stress_score": _f(session, "training_stress_score"),
        "intensity_factor": _f(session, "intensity_factor"),
        "avg_heart_rate": _f(session, "avg_heart_rate"),
        "max_heart_rate": _f(session, "max_heart_rate"),
        "avg_cadence": _f(session, "avg_cadence"),
        "max_cadence": _f(session, "max_cadence"),
        "total_calories": _f(session, "total_calories"),
        "sport": session.get("sport") if session else None,
        "sub_sport": session.get("sub_sport") if session else None,
        "record_count": len(records),
    }
    return {"summary": summary, "records": records}


def _first_session(fit) -> dict | None:
    for msg in fit.get_messages("session"):
        return {f.name: f.value for f in msg.fields}
    return None


def _iter_records(fit) -> Iterator[dict]:
    for msg in fit.get_messages("record"):
        d: dict[str, Any] = {}
        for f in msg.fields:
            v = f.value
            if f.name in ("position_lat", "position_long"):
                v = _semicircles_to_deg(v) if isinstance(v, int) else v
            elif f.name == "timestamp":
                v = _iso(v)
            d[f.name] = v
        yield d


def _f(session: dict | None, key: str) -> float | None:
    if not session:
        return None
    v = session.get(key)
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _iso(dt) -> str | None:
    if dt is None:
        return None
    try:
        return dt.isoformat()
    except AttributeError:
        return str(dt)


if __name__ == "__main__":
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(description="Parse a FIT file")
    p.add_argument("fit", help="Path to .fit file")
    p.add_argument(
        "--summary-only", action="store_true", help="Skip per-second records"
    )
    args = p.parse_args()

    out = parse(args.fit)
    if args.summary_only:
        out = {"summary": out["summary"]}
    json.dump(out, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
