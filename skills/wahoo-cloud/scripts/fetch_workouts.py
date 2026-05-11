#!/usr/bin/env python3
"""Fetch Wahoo workouts → download FIT files → parse → upsert to SQLite.

Default output (override any with env vars):
  $WAHOO_TRAINING_DIR  (default: ~/.openclaw/workspace/training)
    wahoo.db        SQLite store
    wahoo_fit/      downloaded FIT files

Behavior:
  - Lists all workouts via paginated /v1/workouts.
  - For each workout missing FIT data locally, pulls /v1/workouts/:id,
    downloads the FIT from workout_summary.file.url, and parses it.
  - Skips workouts already fully synced (fit_parsed_at IS NOT NULL).
  - Respects sandbox rate limits via wahoo_api's built-in 429 backoff.
"""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Resolve sibling lib/ regardless of where the skill is installed.
SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "lib"))

import wahoo_api  # noqa: E402
import wahoo_auth  # noqa: E402

TRAINING_DIR = Path(
    os.environ.get(
        "WAHOO_TRAINING_DIR",
        os.path.expanduser("~/.openclaw/workspace/training"),
    )
)
DB_PATH = TRAINING_DIR / "wahoo.db"
FIT_DIR = TRAINING_DIR / "wahoo_fit"
SCHEMA_PATH = SKILL_ROOT / "schema" / "wahoo_db_schema.sql"


def init_db() -> sqlite3.Connection:
    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


def _to_float(v) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def upsert_metadata(conn: sqlite3.Connection, w: dict) -> bool:
    """Insert/update metadata from list or detail. Returns True if new row."""
    summary = w.get("workout_summary") or {}
    file_obj = summary.get("file") or {}

    cur = conn.cursor()
    cur.execute("SELECT id FROM workouts WHERE id = ?", (w["id"],))
    existed = cur.fetchone() is not None

    cur.execute(
        """
        INSERT INTO workouts (
            id, name, starts, minutes, workout_type_id, plan_id, route_id,
            workout_token, created_at, updated_at,
            distance_m, duration_active_s, duration_paused_s, duration_total_s,
            ascent_m, cadence_avg, calories, heart_rate_avg, power_avg,
            power_np, power_tss, speed_avg_ms, work_j, time_zone,
            fit_url, synced
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            starts=excluded.starts,
            minutes=excluded.minutes,
            workout_type_id=excluded.workout_type_id,
            plan_id=excluded.plan_id,
            route_id=excluded.route_id,
            workout_token=excluded.workout_token,
            updated_at=excluded.updated_at,
            distance_m=COALESCE(excluded.distance_m, workouts.distance_m),
            duration_active_s=COALESCE(excluded.duration_active_s, workouts.duration_active_s),
            duration_paused_s=COALESCE(excluded.duration_paused_s, workouts.duration_paused_s),
            duration_total_s=COALESCE(excluded.duration_total_s, workouts.duration_total_s),
            ascent_m=COALESCE(excluded.ascent_m, workouts.ascent_m),
            cadence_avg=COALESCE(excluded.cadence_avg, workouts.cadence_avg),
            calories=COALESCE(excluded.calories, workouts.calories),
            heart_rate_avg=COALESCE(excluded.heart_rate_avg, workouts.heart_rate_avg),
            power_avg=COALESCE(excluded.power_avg, workouts.power_avg),
            power_np=COALESCE(excluded.power_np, workouts.power_np),
            power_tss=COALESCE(excluded.power_tss, workouts.power_tss),
            speed_avg_ms=COALESCE(excluded.speed_avg_ms, workouts.speed_avg_ms),
            work_j=COALESCE(excluded.work_j, workouts.work_j),
            time_zone=COALESCE(excluded.time_zone, workouts.time_zone),
            fit_url=COALESCE(excluded.fit_url, workouts.fit_url),
            synced=excluded.synced
        """,
        (
            w["id"],
            w.get("name"),
            w.get("starts"),
            w.get("minutes"),
            w.get("workout_type_id"),
            w.get("plan_id"),
            w.get("route_id"),
            w.get("workout_token"),
            w.get("created_at"),
            w.get("updated_at"),
            _to_float(summary.get("distance_accum")),
            _to_float(summary.get("duration_active_accum")),
            _to_float(summary.get("duration_paused_accum")),
            _to_float(summary.get("duration_total_accum")),
            _to_float(summary.get("ascent_accum")),
            _to_float(summary.get("cadence_avg")),
            _to_float(summary.get("calories_accum")),
            _to_float(summary.get("heart_rate_avg")),
            _to_float(summary.get("power_avg")),
            _to_float(summary.get("power_bike_np_last")),
            _to_float(summary.get("power_bike_tss_last")),
            _to_float(summary.get("speed_avg")),
            _to_float(summary.get("work_accum")),
            summary.get("time_zone"),
            file_obj.get("url"),
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    return not existed


def needs_fit(conn: sqlite3.Connection, workout_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT fit_path, fit_parsed_at FROM workouts WHERE id = ?",
        (workout_id,),
    )
    row = cur.fetchone()
    if not row:
        return True
    fit_path, fit_parsed_at = row
    if fit_parsed_at and fit_path and Path(fit_path).exists():
        return False
    return True


def store_fit_parse(
    conn: sqlite3.Connection, workout_id: int, fit_path: Path, parsed: dict
) -> None:
    s = parsed["summary"]
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE workouts SET
            fit_path = ?,
            fit_parsed_at = datetime('now'),
            fit_total_distance_m = ?,
            fit_total_elapsed_s = ?,
            fit_total_timer_s = ?,
            fit_total_ascent_m = ?,
            fit_total_descent_m = ?,
            fit_avg_power_w = ?,
            fit_max_power_w = ?,
            fit_normalized_power_w = ?,
            fit_avg_heart_rate = ?,
            fit_max_heart_rate = ?,
            fit_avg_cadence = ?,
            fit_max_cadence = ?,
            fit_avg_speed_ms = ?,
            fit_max_speed_ms = ?,
            fit_calories = ?,
            fit_record_count = ?
        WHERE id = ?
        """,
        (
            str(fit_path),
            s.get("total_distance_m"),
            s.get("total_elapsed_time_s"),
            s.get("total_timer_time_s"),
            s.get("total_ascent_m"),
            s.get("total_descent_m"),
            s.get("avg_power_w"),
            s.get("max_power_w"),
            s.get("normalized_power_w"),
            s.get("avg_heart_rate"),
            s.get("max_heart_rate"),
            s.get("avg_cadence"),
            s.get("max_cadence"),
            s.get("avg_speed_ms"),
            s.get("max_speed_ms"),
            s.get("total_calories"),
            s.get("record_count"),
            workout_id,
        ),
    )
    conn.commit()


def log_sync(
    conn: sqlite3.Connection,
    seen: int,
    new: int,
    downloaded: int,
    status: str = "OK",
) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sync_log (workouts_seen, workouts_new, fit_downloaded, status)
        VALUES (?, ?, ?, ?)
        """,
        (seen, new, downloaded, status),
    )
    conn.commit()


def main() -> None:
    print("🚴 Wahoo DB Sync")
    try:
        wahoo_auth.access_token()
    except wahoo_auth.WahooAuthError as e:
        raise SystemExit(f"❌ {e}")

    FIT_DIR.mkdir(parents=True, exist_ok=True)
    conn = init_db()
    print(f"✅ DB at {DB_PATH}")

    seen_ids: list[int] = []
    new_count = 0
    print("📄 Listing workouts…")
    for w in wahoo_api.iter_workouts(per_page=30):
        seen_ids.append(w["id"])
        if upsert_metadata(conn, w):
            new_count += 1
    print(f"   {len(seen_ids)} workouts ({new_count} new)")

    fits_downloaded = 0
    parse_failures = 0

    try:
        import fit_parser  # noqa: F401  (lazy validate)
    except RuntimeError as e:
        print(f"⚠️  {e}")
        print("   Skipping FIT download/parse this run.")
        log_sync(conn, len(seen_ids), new_count, 0, status="PARTIAL")
        _print_recent(conn)
        return

    import fit_parser as fp  # type: ignore

    for wid in seen_ids:
        if not needs_fit(conn, wid):
            continue
        try:
            detail = wahoo_api.get_workout(wid)
        except wahoo_api.WahooAPIError as e:
            print(f"  ⚠️  detail {wid}: {e}")
            continue

        upsert_metadata(conn, detail)

        summary = (detail.get("workout_summary") or {})
        file_obj = summary.get("file") or {}
        fit_url = file_obj.get("url")
        if not fit_url:
            continue

        dest = FIT_DIR / f"{wid}.fit"
        if not dest.exists():
            try:
                wahoo_api.download_fit(fit_url, dest)
                fits_downloaded += 1
                print(f"  ⬇️   {wid}.fit ({dest.stat().st_size // 1024} KB)")
            except Exception as e:
                print(f"  ⚠️  download {wid}: {e}")
                continue

        try:
            parsed = fp.parse(dest)
            store_fit_parse(conn, wid, dest, parsed)
        except Exception as e:
            parse_failures += 1
            print(f"  ⚠️  parse {wid}: {e}")

    status = "OK" if parse_failures == 0 else "PARTIAL"
    log_sync(conn, len(seen_ids), new_count, fits_downloaded, status=status)

    print()
    print(f"📦 Downloaded {fits_downloaded} FIT file(s)")
    if parse_failures:
        print(f"⚠️  {parse_failures} parse failure(s)")

    _print_recent(conn)


def _print_recent(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, starts, distance_m, duration_total_s,
               power_avg, heart_rate_avg, fit_path
        FROM workouts
        ORDER BY starts DESC
        LIMIT 5
        """
    )
    rows = cur.fetchall()
    if not rows:
        print("\n(no workouts in DB yet)")
        return
    print("\n🏁 Most recent workouts:")
    for r in rows:
        wid, name, starts, dist_m, dur_s, p_avg, hr_avg, fit_path = r
        dist_mi = (dist_m or 0) / 1609.34 if dist_m else 0
        dur_min = (dur_s or 0) / 60 if dur_s else 0
        p = f"{p_avg:.0f}W" if p_avg else "—"
        hr = f"{hr_avg:.0f}bpm" if hr_avg else "—"
        fit = "✓" if fit_path and Path(fit_path).exists() else "·"
        print(
            f"  {fit} {(starts or '')[:10]} | {wid} | {name or '—'} "
            f"| {dist_mi:.1f} mi | {dur_min:.0f} min | {p} | {hr}"
        )
    print(f"\n✅ Sync complete. DB: {DB_PATH}")


if __name__ == "__main__":
    main()
