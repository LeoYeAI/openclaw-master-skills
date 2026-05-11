#!/usr/bin/env python3
"""Compute SignalEvent objects from normalized snapshots and baseline cache.

v0.8.0 runtime:
- single-source watchlist and flattened baseline paths
- importable check_entry() for CLI-driven orchestration
- result payloads carry baseline timestamps for show/observation/digest UX
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from error_utils import emit_error


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_name(entry_id: str) -> str:
    """Convert entry_id to filesystem-safe name. Handles : / \\ characters."""
    import re
    return re.sub(r"[:/\\]", "_", entry_id)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def compute_rel_pct(current: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return (current - baseline) / baseline * 100.0


def parse_iso_ts(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def cleanup_baselines(
    baseline_dir: Path,
    active_entry_ids: set[str],
    *,
    ttl_days: int,
    dry_run: bool,
) -> int:
    if not baseline_dir.exists():
        return 0
    now = datetime.now(timezone.utc)
    removed = 0
    for path in baseline_dir.glob("*.json"):
        try:
            payload = load_json(path, {})
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        entry_id = str(payload.get("entry_id", "")).strip()
        baseline_ts = parse_iso_ts(str(payload.get("baseline_ts", "")))
        expired_by_inactive = bool(entry_id) and entry_id not in active_entry_ids
        expired_by_ttl = False
        if baseline_ts is not None and ttl_days > 0:
            expired_by_ttl = (now - baseline_ts).days >= ttl_days
        if not expired_by_inactive and not expired_by_ttl:
            continue
        removed += 1
        if not dry_run:
            try:
                path.unlink()
            except Exception:
                removed -= 1
    return removed


# ---------------------------------------------------------------------------
# Importable function: check a single entry against baseline
# ---------------------------------------------------------------------------

def check_entry(
    entry_id: str,
    question: str,
    current_prob: float,
    baseline_dir: Path,
    threshold_abs_pp: float,
    *,
    dry_run: bool = False,
    audit_log_path: Path | None = None,
) -> dict[str, Any]:
    """Check one entry against its baseline.

    Returns a decision dict:
      {"decision": "BASELINE"|"HIT"|"SILENT", "event": {...}|None, ...}
    """
    baseline_file = baseline_dir / f"{safe_name(entry_id)}.json"
    baseline_doc = load_json(baseline_file, None)

    request_id = str(uuid.uuid4())
    now = utc_now()

    if baseline_doc is None:
        # First time: initialize baseline
        baseline_doc = {
            "entry_id": entry_id,
            "baseline": current_prob,
            "baseline_ts": now,
            "updated_by": "decide_threshold",
            "update_reason": "baseline init",
            "version": 1,
        }
        if not dry_run:
            save_json(baseline_file, baseline_doc)

        decision = "BASELINE"
        result = {
            "decision": decision,
            "request_id": request_id,
            "entry_id": entry_id,
            "current": current_prob,
            "baseline": current_prob,
            "baseline_ts": now,
            "event": None,
        }
    else:
        baseline = float(baseline_doc.get("baseline", current_prob))
        baseline_ts = str(baseline_doc.get("baseline_ts", now))
        abs_pp = abs(current_prob - baseline)
        rel_pct = compute_rel_pct(current_prob, baseline)
        hit = abs_pp >= threshold_abs_pp
        decision = "HIT" if hit else "SILENT"

        event = None
        if hit:
            event = {
                "schema_version": "1.0.0",
                "request_id": request_id,
                "entry_id": entry_id,
                "question": question,
                "current": round(current_prob, 6),
                "baseline": round(baseline, 6),
                "abs_pp": round(abs_pp, 6),
                "rel_pct": round(rel_pct, 6),
                "threshold_abs_pp": threshold_abs_pp,
                "reason": f"abs_pp {round(abs_pp, 1)} >= threshold {threshold_abs_pp}",
                "ts": now,
                "baseline_ts": baseline_ts,
            }

            # Update baseline to current value after HIT
            next_version = int(baseline_doc.get("version", 1)) + 1
            baseline_doc = {
                "entry_id": entry_id,
                "baseline": current_prob,
                "baseline_ts": now,
                "updated_by": "decide_threshold",
                "update_reason": "HIT triggered, baseline updated",
                "version": next_version,
            }
            if not dry_run:
                save_json(baseline_file, baseline_doc)

        result = {
            "decision": decision,
            "request_id": request_id,
            "entry_id": entry_id,
            "current": current_prob,
            "baseline": baseline,
            "baseline_ts": baseline_ts,
            "abs_pp": round(abs_pp, 6) if hit else round(abs_pp, 6),
            "event": event,
        }

    # Write audit log
    if not dry_run and audit_log_path is not None:
        audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with audit_log_path.open("a", encoding="utf-8") as af:
            af.write(
                json.dumps(
                    {
                        "ts": now,
                        "request_id": request_id,
                        "entry_id": entry_id,
                        "decision": decision,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    return result


# ---------------------------------------------------------------------------
# CLI (legacy, kept for backward compatibility)
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="SignalRadar decide step")
    parser.add_argument("--snapshots", required=True, help="Normalized snapshots JSON file")
    parser.add_argument("--out-events", required=True, help="Output SignalEvent JSON file")
    parser.add_argument("--baseline-dir", default="~/.signalradar/cache/baselines", help="Baseline storage directory")
    parser.add_argument("--audit-log", default="~/.signalradar/cache/events/signal_events.jsonl", help="Audit log JSONL path")
    parser.add_argument("--threshold-abs-pp", type=float, default=5.0, help="Default abs_pp threshold")
    parser.add_argument("--emit-baseline-events", action="store_true", help="Emit baseline init records")
    parser.add_argument("--cleanup-expired", action="store_true", help="Cleanup baselines for inactive entries")
    parser.add_argument("--cleanup-ttl-days", type=int, default=90, help="TTL days for baseline cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Compute events without mutating state")
    args = parser.parse_args()

    snapshots_path = Path(args.snapshots)
    baseline_dir = Path(args.baseline_dir)
    out_events_path = Path(args.out_events)
    audit_log_path = Path(args.audit_log)

    try:
        rows = load_json(snapshots_path, [])
        if not isinstance(rows, list):
            raise ValueError("snapshots must be a JSON array")

        events: list[dict[str, Any]] = []
        active_entry_ids: set[str] = set()

        for row in rows:
            if not isinstance(row, dict):
                continue
            source = str(row.get("source", "polymarket"))
            market_id = str(row.get("market_id", ""))
            slug = str(row.get("slug", ""))
            event_id = str(row.get("event_id", ""))
            question = str(row.get("question", ""))
            entry_id = f"{source}:{market_id}:{slug}:{event_id}"
            active_entry_ids.add(entry_id)

            try:
                current = float(row["probability"])
            except Exception:
                continue

            result = check_entry(
                entry_id=entry_id,
                question=question,
                current_prob=current,
                baseline_dir=baseline_dir,
                threshold_abs_pp=args.threshold_abs_pp,
                dry_run=args.dry_run,
                audit_log_path=audit_log_path,
            )

            if result["event"] is not None:
                events.append(result["event"])

        removed = 0
        if args.cleanup_expired:
            removed = cleanup_baselines(
                baseline_dir,
                active_entry_ids,
                ttl_days=args.cleanup_ttl_days,
                dry_run=args.dry_run,
            )
        save_json(out_events_path, events)
        mode = "dry_run" if args.dry_run else "live"
        print(f"processed={len(rows)} events={len(events)} cleanup_removed={removed} mode={mode} out={out_events_path}")
        return 0
    except Exception as exc:  # noqa: BLE001
        return emit_error(
            "SR_VALIDATION_ERROR",
            f"decide failed: {exc}",
            retryable=False,
            details={"script": "decide_threshold.py", "snapshots": str(snapshots_path)},
        )


if __name__ == "__main__":
    raise SystemExit(main())
