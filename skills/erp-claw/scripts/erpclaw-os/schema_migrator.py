#!/usr/bin/env python3
"""ERPClaw OS — Schema Migration Engine

Infrastructure-as-Code pattern for schema changes. Four phases:
  PLAN:     Generate migration from init_db.py diff, validate, show plan
  APPLY:    Execute DDL within transaction, record schema version
  ROLLBACK: Revert schema to previous version, preserve data in backup tables
  DRIFT:    Detect manual DB modifications that diverge from declared schema

Key constraint: AI can CREATE tables, never ALTER/DROP tables owned by other modules.
"""
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from schema_diff import (
    diff_schema,
    detect_drift as _detect_drift,
    generate_create_ddl,
    get_live_schema,
    parse_init_db_ddl,
)
from validate_module import build_table_ownership_registry, validate_module_static

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")


# ---------------------------------------------------------------------------
# Migration Table
# ---------------------------------------------------------------------------

def ensure_migration_table(db_path=None):
    """Create erpclaw_schema_migration table if it doesn't exist."""
    db_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)
    from erpclaw_lib.query import ddl_now
    conn.executescript(f"""
        CREATE TABLE IF NOT EXISTS erpclaw_schema_migration (
            id              TEXT PRIMARY KEY,
            module_name     TEXT NOT NULL,
            migration_type  TEXT NOT NULL CHECK(migration_type IN ('create', 'alter', 'rollback')),
            ddl_statements  TEXT NOT NULL,
            status          TEXT NOT NULL CHECK(status IN ('planned', 'applied', 'rolled_back', 'failed')),
            previous_schema TEXT,
            planned_at      TEXT DEFAULT ({ddl_now()}),
            applied_at      TEXT,
            rolled_back_at  TEXT,
            applied_by      TEXT
        );
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# PLAN: Generate migration plan
# ---------------------------------------------------------------------------

def plan_migration(module_path, db_path=None, src_root=None):
    """Generate a migration plan for a module.

    Compares the module's init_db.py against the live DB and produces
    a list of DDL statements needed to bring the DB in sync.

    Args:
        module_path: Path to the module directory (must contain init_db.py)
        db_path: Path to the SQLite database
        src_root: Path to src/ directory (for table ownership checks)

    Returns:
        dict with migration_id, ddl_statements, validation, table_count, etc.
    """
    db_path = db_path or DEFAULT_DB_PATH
    init_db_path = os.path.join(module_path, "init_db.py")

    if not os.path.isfile(init_db_path):
        return {
            "result": "error",
            "error": f"No init_db.py found at {init_db_path}",
        }

    # 1. Diff current DB vs declared schema
    diff = diff_schema(db_path, init_db_path)

    # Only consider new tables/columns as actionable differences.
    # dropped_tables are expected (foundation tables not declared in this module).
    has_actionable_changes = bool(diff["new_tables"] or diff["new_columns"])
    if not has_actionable_changes:
        return {
            "result": "no_changes",
            "message": "Schema is already in sync with init_db.py",
            "matching_tables": diff["matching_tables"],
        }

    # 2. Check for cross-module conflicts
    if src_root:
        ownership = build_table_ownership_registry(src_root)
        module_name = os.path.basename(module_path)
        conflicts = []

        # Cannot ALTER/DROP tables owned by other modules
        for col_info in diff.get("new_columns", []):
            table = col_info["table"]
            if table in ownership and ownership[table] != module_name:
                conflicts.append(
                    f"Cannot add column to '{table}' — owned by '{ownership[table]}'"
                )
        for table in diff.get("dropped_tables", []):
            if table in ownership and ownership[table] != module_name:
                conflicts.append(
                    f"Cannot drop table '{table}' — owned by '{ownership[table]}'"
                )

        if conflicts:
            return {
                "result": "blocked",
                "error": "Cross-module write protection",
                "conflicts": conflicts,
            }

    # 3. Generate DDL for new tables only (safest migration type)
    ddl_statements = generate_create_ddl(init_db_path, diff["new_tables"])

    # 4. Run static validation on the module
    validation = validate_module_static(module_path)
    validation_passed = validation.get("result") != "fail"

    # 5. Snapshot current schema
    previous_schema = get_live_schema(db_path)

    # 6. Create migration record
    migration_id = str(uuid.uuid4())
    module_name = os.path.basename(module_path)

    ensure_migration_table(db_path)
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)
    conn.execute("""
        INSERT INTO erpclaw_schema_migration
            (id, module_name, migration_type, ddl_statements, status, previous_schema, planned_at)
        VALUES (?, ?, 'create', ?, 'planned', ?, ?)
    """, (
        migration_id,
        module_name,
        json.dumps(ddl_statements),
        json.dumps({k: {"columns": v["columns"]} for k, v in previous_schema.items()}),
        datetime.now(timezone.utc).isoformat(),
    ))
    conn.commit()
    conn.close()

    return {
        "result": "planned",
        "migration_id": migration_id,
        "module_name": module_name,
        "new_tables": diff["new_tables"],
        "new_columns": diff["new_columns"],
        "ddl_count": len(ddl_statements),
        "ddl_statements": ddl_statements,
        "validation_passed": validation_passed,
        "validation_result": validation.get("result", "unknown"),
    }


# ---------------------------------------------------------------------------
# APPLY: Execute migration
# ---------------------------------------------------------------------------

def apply_migration(migration_id, db_path=None, applied_by=None):
    """Execute a planned migration.

    Args:
        migration_id: UUID of the migration to apply
        db_path: Path to the SQLite database
        applied_by: Who is applying (user/system identifier)

    Returns:
        dict with result, tables_created, etc.
    """
    db_path = db_path or DEFAULT_DB_PATH
    ensure_migration_table(db_path)

    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)

    # 1. Load migration record
    row = conn.execute(
        "SELECT module_name, ddl_statements, status FROM erpclaw_schema_migration WHERE id = ?",
        (migration_id,),
    ).fetchone()

    if not row:
        conn.close()
        return {"result": "error", "error": f"Migration {migration_id} not found"}

    module_name, ddl_json, status = row

    if status != "planned":
        conn.close()
        return {
            "result": "error",
            "error": f"Migration {migration_id} has status '{status}', expected 'planned'",
        }

    ddl_statements = json.loads(ddl_json)

    # 2. Execute DDL in a single transaction
    tables_created = []
    try:
        for ddl in ddl_statements:
            conn.execute(ddl)
            # Track which tables were created
            if "CREATE TABLE" in ddl.upper():
                import re
                m = re.search(r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)", ddl, re.IGNORECASE)
                if m:
                    tables_created.append(m.group(1))

        # 3. Update migration record
        conn.execute("""
            UPDATE erpclaw_schema_migration
            SET status = 'applied', applied_at = ?, applied_by = ?
            WHERE id = ?
        """, (datetime.now(timezone.utc).isoformat(), applied_by or "system", migration_id))

        conn.commit()

    except sqlite3.Error as e:
        conn.execute("""
            UPDATE erpclaw_schema_migration
            SET status = 'failed'
            WHERE id = ?
        """, (migration_id,))
        conn.commit()
        conn.close()
        return {
            "result": "error",
            "error": f"DDL execution failed: {e}",
            "migration_id": migration_id,
        }

    conn.close()

    return {
        "result": "applied",
        "migration_id": migration_id,
        "module_name": module_name,
        "tables_created": tables_created,
        "ddl_executed": len(ddl_statements),
    }


# ---------------------------------------------------------------------------
# ROLLBACK: Revert migration
# ---------------------------------------------------------------------------

def rollback_migration(migration_id, db_path=None):
    """Rollback an applied migration.

    For 'create' migrations: drops the tables that were created.
    Backs up data into _backup tables before dropping.

    Args:
        migration_id: UUID of the migration to rollback
        db_path: Path to the SQLite database

    Returns:
        dict with result, tables_dropped, backups_created, etc.
    """
    db_path = db_path or DEFAULT_DB_PATH
    ensure_migration_table(db_path)

    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)

    # 1. Load migration record
    row = conn.execute(
        "SELECT module_name, migration_type, ddl_statements, status FROM erpclaw_schema_migration WHERE id = ?",
        (migration_id,),
    ).fetchone()

    if not row:
        conn.close()
        return {"result": "error", "error": f"Migration {migration_id} not found"}

    module_name, migration_type, ddl_json, status = row

    if status != "applied":
        conn.close()
        return {
            "result": "error",
            "error": f"Migration {migration_id} has status '{status}', expected 'applied'",
        }

    ddl_statements = json.loads(ddl_json)
    tables_dropped = []
    backups_created = []

    try:
        if migration_type == "create":
            # Identify tables that were created
            import re
            for ddl in ddl_statements:
                m = re.search(r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)", ddl, re.IGNORECASE)
                if m:
                    table_name = m.group(1)

                    # Backup data if table has rows
                    row_count = conn.execute(
                        f"SELECT COUNT(*) FROM [{table_name}]"
                    ).fetchone()[0]

                    if row_count > 0:
                        backup_name = f"{table_name}_backup_{migration_id[:8]}"
                        conn.execute(
                            f"CREATE TABLE [{backup_name}] AS SELECT * FROM [{table_name}]"
                        )
                        backups_created.append({
                            "original": table_name,
                            "backup": backup_name,
                            "rows": row_count,
                        })

                    # Drop the table
                    conn.execute(f"DROP TABLE IF EXISTS [{table_name}]")
                    tables_dropped.append(table_name)

        # Update migration record
        conn.execute("""
            UPDATE erpclaw_schema_migration
            SET status = 'rolled_back', rolled_back_at = ?
            WHERE id = ?
        """, (datetime.now(timezone.utc).isoformat(), migration_id))

        conn.commit()

    except sqlite3.Error as e:
        conn.close()
        return {
            "result": "error",
            "error": f"Rollback failed: {e}",
            "migration_id": migration_id,
        }

    conn.close()

    return {
        "result": "rolled_back",
        "migration_id": migration_id,
        "module_name": module_name,
        "tables_dropped": tables_dropped,
        "backups_created": backups_created,
    }


# ---------------------------------------------------------------------------
# CLI Handlers
# ---------------------------------------------------------------------------

def handle_schema_plan(args):
    """CLI handler for schema-plan action."""
    module_path = getattr(args, "module_path", None)
    db_path = getattr(args, "db_path", None)
    src_root = getattr(args, "src_root", None)

    if not module_path:
        return {"error": "--module-path is required for schema-plan"}

    start_time = time.time()
    result = plan_migration(module_path, db_path=db_path, src_root=src_root)
    result["duration_ms"] = int((time.time() - start_time) * 1000)
    return result


def handle_schema_apply(args):
    """CLI handler for schema-apply action."""
    migration_id = getattr(args, "migration_id", None)
    db_path = getattr(args, "db_path", None)

    if not migration_id:
        return {"error": "--migration-id is required for schema-apply"}

    start_time = time.time()
    result = apply_migration(migration_id, db_path=db_path)
    result["duration_ms"] = int((time.time() - start_time) * 1000)
    return result


def handle_schema_rollback(args):
    """CLI handler for schema-rollback action."""
    migration_id = getattr(args, "migration_id", None)
    db_path = getattr(args, "db_path", None)

    if not migration_id:
        return {"error": "--migration-id is required for schema-rollback"}

    start_time = time.time()
    result = rollback_migration(migration_id, db_path=db_path)
    result["duration_ms"] = int((time.time() - start_time) * 1000)
    return result


def handle_schema_drift(args):
    """CLI handler for schema-drift action."""
    module_path = getattr(args, "module_path", None)
    db_path = getattr(args, "db_path", None)

    if not module_path:
        return {"error": "--module-path is required for schema-drift"}

    db_path = db_path or DEFAULT_DB_PATH

    start_time = time.time()
    findings = _detect_drift(db_path, module_path)
    duration_ms = int((time.time() - start_time) * 1000)

    return {
        "result": "drift_detected" if findings else "no_drift",
        "findings": findings,
        "finding_count": len(findings),
        "module_path": module_path,
        "duration_ms": duration_ms,
    }
