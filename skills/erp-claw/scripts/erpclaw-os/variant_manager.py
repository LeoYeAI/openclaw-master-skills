#!/usr/bin/env python3
"""ERPClaw OS — Variant Lifecycle Manager (Phase 3, Deliverable 3c)

Manages the lifecycle of DGM variants: storage, comparison, selection,
cleanup, and diff generation. Used by dgm_engine.py to persist and
evaluate code variants produced by the evolutionary optimization engine.
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

# Add shared lib to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))

from erpclaw_lib.db import get_connection
from erpclaw_lib.query import (
    Q, P, Table, Field, Order, LiteralValue, insert_row, dynamic_update,
)


# ---------------------------------------------------------------------------
# Store variant
# ---------------------------------------------------------------------------

def store_variant(conn, run_id, variant_data):
    """Store a single variant in erpclaw_dgm_variant.

    Args:
        conn: SQLite connection
        run_id: parent DGM run ID
        variant_data: dict with keys:
            module_name, action_name, variant_number, variant_code,
            variant_diff, mutation_type, exec_time_ms, memory_kb,
            test_pass_count, test_total, composite_score

    Returns:
        str: variant ID
    """
    variant_id = str(uuid.uuid4())

    sql, cols = insert_row("erpclaw_dgm_variant", {
        "id": P(),
        "run_id": P(),
        "module_name": P(),
        "action_name": P(),
        "variant_number": P(),
        "variant_code": P(),
        "variant_diff": P(),
        "mutation_type": P(),
        "exec_time_ms": P(),
        "memory_kb": P(),
        "test_pass_count": P(),
        "test_total": P(),
        "composite_score": P(),
        "is_selected": P(),
        "created_at": LiteralValue("datetime('now')"),
    })
    conn.execute(sql, [
        variant_id,
        run_id,
        variant_data["module_name"],
        variant_data["action_name"],
        variant_data["variant_number"],
        variant_data["variant_code"],
        variant_data.get("variant_diff"),
        variant_data["mutation_type"],
        variant_data.get("exec_time_ms"),
        variant_data.get("memory_kb"),
        variant_data.get("test_pass_count"),
        variant_data.get("test_total"),
        variant_data.get("composite_score"),
        0,  # is_selected default
    ])

    return variant_id


# ---------------------------------------------------------------------------
# Compare variants
# ---------------------------------------------------------------------------

def compare_variants(conn, run_id):
    """Return all variants for a run sorted by composite_score descending.

    Args:
        conn: SQLite connection
        run_id: DGM run ID

    Returns:
        list of dict: variants ordered by composite_score (best first)
    """
    t = Table("erpclaw_dgm_variant")
    q = (Q.from_(t)
         .select(t.star)
         .where(t.run_id == P())
         .orderby(t.composite_score, order=Order.desc))
    sql = q.get_sql()

    rows = conn.execute(sql, [run_id]).fetchall()
    # conn should have row_factory set, but handle both cases
    if rows and isinstance(rows[0], sqlite3.Row):
        return [dict(r) for r in rows]
    return rows


# ---------------------------------------------------------------------------
# Select best variant
# ---------------------------------------------------------------------------

def select_best(conn, run_id):
    """Mark the best variant for a run as selected and create improvement proposal.

    The best variant must have test_pass_rate == 1.0 (all tests pass).
    Returns None if no qualifying variant exists.

    Args:
        conn: SQLite connection
        run_id: DGM run ID

    Returns:
        dict with variant_id, improvement_id (if created), or None
    """
    variants = compare_variants(conn, run_id)
    if not variants:
        return None

    # Find best qualifying variant (test_pass_rate == 1.0)
    best = None
    for v in variants:
        test_total = v.get("test_total") or 0
        test_pass = v.get("test_pass_count") or 0
        if test_total > 0 and test_pass == test_total:
            best = v
            break

    if not best:
        return None

    variant_id = best["id"]

    # Mark as selected
    conn.execute(
        'UPDATE erpclaw_dgm_variant SET is_selected = 1 WHERE id = ?',
        (variant_id,),
    )

    # Create improvement proposal via improvement_log
    improvement_id = _create_improvement_proposal(conn, best)

    # Update run with best variant info
    improvement_pct = None
    run_row = conn.execute(
        'SELECT current_exec_ms FROM erpclaw_dgm_run WHERE id = ?',
        (run_id,),
    ).fetchone()
    if run_row:
        current_ms = run_row["current_exec_ms"] if isinstance(run_row, sqlite3.Row) else run_row[0]
        best_ms = best.get("exec_time_ms")
        if current_ms and best_ms and current_ms > 0:
            pct = Decimal(str(current_ms - best_ms)) / Decimal(str(current_ms)) * 100
            improvement_pct = str(pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    conn.execute(
        'UPDATE erpclaw_dgm_run SET best_variant_id = ?, best_exec_ms = ?, '
        'improvement_pct = ?, improvement_id = ?, status = ?, completed_at = datetime(\'now\') '
        'WHERE id = ?',
        (variant_id, best.get("exec_time_ms"), improvement_pct,
         improvement_id, "completed", run_id),
    )

    return {
        "variant_id": variant_id,
        "improvement_id": improvement_id,
        "improvement_pct": improvement_pct,
        "composite_score": best.get("composite_score"),
    }


def _create_improvement_proposal(conn, variant):
    """Create an improvement_log entry for a selected DGM variant.

    Args:
        conn: SQLite connection
        variant: variant dict

    Returns:
        str: improvement ID
    """
    improvement_id = str(uuid.uuid4())

    description = (
        f"DGM variant for {variant['module_name']}/{variant['action_name']} "
        f"(mutation: {variant['mutation_type']}). "
        f"Exec time: {variant.get('exec_time_ms')}ms, "
        f"Memory: {variant.get('memory_kb')}KB."
    )

    evidence = json.dumps({
        "variant_id": variant["id"],
        "run_id": variant["run_id"],
        "mutation_type": variant["mutation_type"],
        "exec_time_ms": variant.get("exec_time_ms"),
        "memory_kb": variant.get("memory_kb"),
        "test_pass_count": variant.get("test_pass_count"),
        "test_total": variant.get("test_total"),
        "composite_score": variant.get("composite_score"),
    })

    proposed_diff = json.dumps({
        "variant_diff": variant.get("variant_diff"),
        "variant_code_length": len(variant.get("variant_code", "")),
    })

    sql, cols = insert_row("erpclaw_improvement_log", {
        "id": P(),
        "module_name": P(),
        "category": P(),
        "description": P(),
        "evidence": P(),
        "proposed_diff": P(),
        "source": P(),
        "status": P(),
        "proposed_at": LiteralValue("datetime('now')"),
    })
    conn.execute(sql, [
        improvement_id,
        variant["module_name"],
        "performance",
        description,
        evidence,
        proposed_diff,
        "dgm",
        "proposed",
    ])

    return improvement_id


# ---------------------------------------------------------------------------
# Cleanup old variants
# ---------------------------------------------------------------------------

def cleanup_old_variants(conn, days=30):
    """Purge unselected variants older than the specified number of days.

    Args:
        conn: SQLite connection
        days: age threshold in days (default 30)

    Returns:
        int: number of variants deleted
    """
    cursor = conn.execute(
        "DELETE FROM erpclaw_dgm_variant "
        "WHERE is_selected = 0 "
        "AND created_at < datetime('now', ?)",
        (f"-{days} days",),
    )
    return cursor.rowcount


# ---------------------------------------------------------------------------
# Get variant diff
# ---------------------------------------------------------------------------

def get_variant_diff(conn, variant_id):
    """Return the unified diff between a variant and the current implementation.

    Args:
        conn: SQLite connection
        variant_id: variant UUID

    Returns:
        dict with variant_id, variant_diff, mutation_type, module_name, action_name
        or None if not found
    """
    row = conn.execute(
        'SELECT id, variant_diff, mutation_type, module_name, action_name, '
        'variant_code, exec_time_ms, memory_kb, composite_score, is_selected '
        'FROM erpclaw_dgm_variant WHERE id = ?',
        (variant_id,),
    ).fetchone()

    if not row:
        return None

    if isinstance(row, sqlite3.Row):
        return dict(row)
    return row
