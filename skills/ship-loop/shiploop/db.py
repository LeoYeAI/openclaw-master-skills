from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("shiploop.db")

DB_FILENAME = "tars.db"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    """SQLite-backed state store for Ship Loop v5.0.

    Single source of truth for:
    - runs (pipeline executions)
    - segments (individual work units within a run)
    - run_events (event queue for crash recovery)
    - learnings (from failures and successes)
    - usage (token/cost tracking)
    - decision_gaps (unhandled situations)
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._connect()
        self._migrate()

    def _connect(self) -> None:
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.row_factory = sqlite3.Row

    def _migrate(self) -> None:
        """Auto-migration: create tables if they don't exist."""
        assert self._conn is not None
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    project TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL DEFAULT 'running',
                    total_cost_usd REAL DEFAULT 0.0
                );

                CREATE TABLE IF NOT EXISTS segments (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    prompt TEXT,
                    commit_sha TEXT,
                    tag TEXT,
                    deploy_url TEXT,
                    depends_on TEXT DEFAULT '[]',
                    touched_paths TEXT DEFAULT '[]',
                    started_at TEXT,
                    finished_at TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(id)
                );

                CREATE TABLE IF NOT EXISTS run_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    segment_name TEXT,
                    event_type TEXT NOT NULL,
                    data TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    processed_at TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(id)
                );

                CREATE TABLE IF NOT EXISTS learnings (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    segment TEXT NOT NULL,
                    error_signature TEXT DEFAULT '',
                    failure TEXT NOT NULL,
                    root_cause TEXT NOT NULL,
                    fix TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    learning_type TEXT DEFAULT 'failure',
                    improvement_type TEXT DEFAULT '',
                    prompt_delta TEXT DEFAULT '',
                    score REAL DEFAULT 1.0
                );

                CREATE TABLE IF NOT EXISTS usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    segment TEXT NOT NULL,
                    loop TEXT NOT NULL,
                    tokens_in INTEGER DEFAULT 0,
                    tokens_out INTEGER DEFAULT 0,
                    estimated_cost_usd REAL DEFAULT 0.0,
                    duration_seconds REAL DEFAULT 0.0,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS decision_gaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    segment TEXT NOT NULL,
                    context TEXT NOT NULL,
                    verdict_taken TEXT NOT NULL,
                    recommended_verdict TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_segments_run_id ON segments(run_id);
                CREATE INDEX IF NOT EXISTS idx_run_events_run_id ON run_events(run_id);
                CREATE INDEX IF NOT EXISTS idx_run_events_processed ON run_events(processed_at);
                CREATE INDEX IF NOT EXISTS idx_usage_segment ON usage(segment);
                CREATE INDEX IF NOT EXISTS idx_learnings_score ON learnings(score DESC);
            """)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    # ─── Runs ─────────────────────────────────────────────────────────────────

    def create_run(self, run_id: str, project: str) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.execute(
                "INSERT INTO runs (id, project, started_at, status) VALUES (?, ?, ?, 'running')",
                (run_id, project, _now_iso()),
            )

    def finish_run(self, run_id: str, status: str, total_cost_usd: float = 0.0) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.execute(
                "UPDATE runs SET finished_at=?, status=?, total_cost_usd=? WHERE id=?",
                (_now_iso(), status, total_cost_usd, run_id),
            )

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        assert self._conn is not None
        row = self._conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        return dict(row) if row else None

    def list_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ─── Segments ─────────────────────────────────────────────────────────────

    def upsert_segment(
        self,
        run_id: str,
        name: str,
        status: str,
        prompt: str = "",
        depends_on: list[str] | None = None,
    ) -> None:
        assert self._conn is not None
        seg_id = f"{run_id}:{name}"
        depends_json = json.dumps(depends_on or [])
        with self._conn:
            self._conn.execute("""
                INSERT INTO segments (id, run_id, name, status, prompt, depends_on, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status,
                    prompt=excluded.prompt,
                    depends_on=excluded.depends_on
            """, (seg_id, run_id, name, status, prompt, depends_json, _now_iso()))

    def update_segment_status(self, run_id: str, name: str, status: str) -> None:
        assert self._conn is not None
        seg_id = f"{run_id}:{name}"
        updates = {"status": status}
        if status in ("shipped", "failed"):
            updates["finished_at"] = _now_iso()
        with self._conn:
            if "finished_at" in updates:
                self._conn.execute(
                    "UPDATE segments SET status=?, finished_at=? WHERE id=?",
                    (status, updates["finished_at"], seg_id),
                )
            else:
                self._conn.execute(
                    "UPDATE segments SET status=? WHERE id=?",
                    (status, seg_id),
                )

    def update_segment_ship_info(
        self,
        run_id: str,
        name: str,
        commit_sha: str = "",
        tag: str = "",
        deploy_url: str = "",
        touched_paths: list[str] | None = None,
    ) -> None:
        assert self._conn is not None
        seg_id = f"{run_id}:{name}"
        paths_json = json.dumps(touched_paths or [])
        with self._conn:
            self._conn.execute("""
                UPDATE segments
                SET commit_sha=?, tag=?, deploy_url=?, touched_paths=?, finished_at=?
                WHERE id=?
            """, (commit_sha, tag, deploy_url, paths_json, _now_iso(), seg_id))

    def get_segment(self, run_id: str, name: str) -> dict[str, Any] | None:
        assert self._conn is not None
        seg_id = f"{run_id}:{name}"
        row = self._conn.execute("SELECT * FROM segments WHERE id=?", (seg_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["depends_on"] = json.loads(d.get("depends_on") or "[]")
        d["touched_paths"] = json.loads(d.get("touched_paths") or "[]")
        return d

    def get_run_segments(self, run_id: str) -> list[dict[str, Any]]:
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT * FROM segments WHERE run_id=? ORDER BY started_at", (run_id,)
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["depends_on"] = json.loads(d.get("depends_on") or "[]")
            d["touched_paths"] = json.loads(d.get("touched_paths") or "[]")
            result.append(d)
        return result

    def get_all_shipped_touched_paths(self, run_id: str) -> dict[str, list[str]]:
        """Returns {segment_name: [paths]} for all shipped segments in this run."""
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT name, touched_paths FROM segments WHERE run_id=? AND status='shipped'",
            (run_id,),
        ).fetchall()
        return {row["name"]: json.loads(row["touched_paths"] or "[]") for row in rows}

    # ─── Events ───────────────────────────────────────────────────────────────

    def emit_event(
        self,
        run_id: str,
        segment: str | None,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> int:
        assert self._conn is not None
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO run_events (run_id, segment_name, event_type, data, created_at) VALUES (?, ?, ?, ?, ?)",
                (run_id, segment, event_type, json.dumps(data or {}), _now_iso()),
            )
            return cursor.lastrowid or 0

    def poll_events(self, run_id: str, limit: int = 10) -> list[dict[str, Any]]:
        assert self._conn is not None
        rows = self._conn.execute(
            """SELECT * FROM run_events
               WHERE run_id=? AND processed_at IS NULL
               ORDER BY created_at ASC
               LIMIT ?""",
            (run_id, limit),
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["data"] = json.loads(d.get("data") or "{}")
            result.append(d)
        return result

    def mark_processed(self, event_id: int) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.execute(
                "UPDATE run_events SET processed_at=? WHERE id=?",
                (_now_iso(), event_id),
            )

    def get_events(self, run_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """Get all events (processed and unprocessed) for a run."""
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT * FROM run_events WHERE run_id=? ORDER BY created_at DESC LIMIT ?",
            (run_id, limit),
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["data"] = json.loads(d.get("data") or "{}")
            result.append(d)
        return result

    # ─── Learnings ────────────────────────────────────────────────────────────

    def save_learning(
        self,
        learning_id: str,
        date: str,
        segment: str,
        error_signature: str,
        failure: str,
        root_cause: str,
        fix: str,
        tags: list[str],
        learning_type: str = "failure",
        improvement_type: str = "",
        prompt_delta: str = "",
        score: float = 1.0,
    ) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.execute("""
                INSERT INTO learnings
                    (id, date, segment, error_signature, failure, root_cause, fix,
                     tags, learning_type, improvement_type, prompt_delta, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    score=excluded.score,
                    root_cause=excluded.root_cause,
                    fix=excluded.fix
            """, (
                learning_id, date, segment, error_signature,
                failure, root_cause, fix, json.dumps(tags),
                learning_type, improvement_type, prompt_delta, score,
            ))

    def update_learning_score(self, learning_id: str, delta: float) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.execute(
                "UPDATE learnings SET score = MAX(0.0, score + ?) WHERE id=?",
                (delta, learning_id),
            )

    def get_all_learnings(self) -> list[dict[str, Any]]:
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT * FROM learnings ORDER BY score DESC, date DESC"
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["tags"] = json.loads(d.get("tags") or "[]")
            result.append(d)
        return result

    def count_learnings(self) -> int:
        assert self._conn is not None
        row = self._conn.execute("SELECT COUNT(*) FROM learnings").fetchone()
        return row[0] if row else 0

    # ─── Usage ────────────────────────────────────────────────────────────────

    def record_usage(
        self,
        run_id: str | None,
        segment: str,
        loop: str,
        tokens_in: int,
        tokens_out: int,
        estimated_cost_usd: float,
        duration_seconds: float,
    ) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.execute("""
                INSERT INTO usage
                    (run_id, segment, loop, tokens_in, tokens_out,
                     estimated_cost_usd, duration_seconds, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (run_id, segment, loop, tokens_in, tokens_out,
                  estimated_cost_usd, duration_seconds, _now_iso()))

    def get_segment_cost(self, segment: str) -> float:
        assert self._conn is not None
        row = self._conn.execute(
            "SELECT SUM(estimated_cost_usd) FROM usage WHERE segment=?", (segment,)
        ).fetchone()
        return row[0] or 0.0

    def get_run_cost(self, run_id: str) -> float:
        assert self._conn is not None
        row = self._conn.execute(
            "SELECT SUM(estimated_cost_usd) FROM usage WHERE run_id=?", (run_id,)
        ).fetchone()
        return row[0] or 0.0

    def get_total_cost(self) -> float:
        assert self._conn is not None
        row = self._conn.execute("SELECT SUM(estimated_cost_usd) FROM usage").fetchone()
        return row[0] or 0.0

    def get_usage_records(self, segment: str | None = None) -> list[dict[str, Any]]:
        assert self._conn is not None
        if segment:
            rows = self._conn.execute(
                "SELECT * FROM usage WHERE segment=? ORDER BY timestamp DESC", (segment,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM usage ORDER BY timestamp DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    # ─── Decision Gaps ────────────────────────────────────────────────────────

    def record_decision_gap(
        self,
        run_id: str | None,
        segment: str,
        context: str,
        verdict_taken: str,
        recommended_verdict: str = "",
    ) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.execute("""
                INSERT INTO decision_gaps
                    (run_id, segment, context, verdict_taken, recommended_verdict, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (run_id, segment, context, verdict_taken, recommended_verdict, _now_iso()))

    def get_decision_gaps(self, resolved: bool | None = None) -> list[dict[str, Any]]:
        assert self._conn is not None
        if resolved is None:
            rows = self._conn.execute(
                "SELECT * FROM decision_gaps ORDER BY created_at DESC"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM decision_gaps WHERE resolved=? ORDER BY created_at DESC",
                (1 if resolved else 0,),
            ).fetchall()
        return [dict(r) for r in rows]

    # ─── Analytics (for reflect loop) ─────────────────────────────────────────

    def get_recent_runs(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.list_runs(limit=limit)

    def get_stale_learnings(self, threshold: float = 0.3) -> list[dict[str, Any]]:
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT * FROM learnings WHERE score < ? ORDER BY score ASC",
            (threshold,),
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["tags"] = json.loads(d.get("tags") or "[]")
            result.append(d)
        return result

    def get_repeat_failures(self) -> list[dict[str, Any]]:
        """Find error_signatures that appear in multiple segments/runs."""
        assert self._conn is not None
        rows = self._conn.execute("""
            SELECT error_signature, COUNT(*) as count, GROUP_CONCAT(segment) as segments
            FROM learnings
            WHERE error_signature != ''
            GROUP BY error_signature
            HAVING count > 1
            ORDER BY count DESC
        """).fetchall()
        return [dict(r) for r in rows]

    def get_repair_heavy_segments(self) -> list[dict[str, Any]]:
        """Find segments with multiple repair loops recorded."""
        assert self._conn is not None
        rows = self._conn.execute("""
            SELECT segment, COUNT(*) as repair_count
            FROM usage
            WHERE loop LIKE 'repair-%'
            GROUP BY segment
            HAVING repair_count > 1
            ORDER BY repair_count DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_db(repo_path: Path) -> Database:
    """Get or create the database for a project."""
    db_path = repo_path / ".shiploop" / DB_FILENAME
    return Database(db_path)
