#!/usr/bin/env python3
"""ERPClaw OS — Deployment Audit Logger

Records every deployment attempt with complete provenance:
module name, pipeline steps, pass/fail, tier classification,
human approval status, and git commit hash.

Satisfies guardrail O2: every AI change logged with reasoning.
"""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")


def ensure_deploy_audit_table(db_path=None):
    """Create erpclaw_deploy_audit table if it doesn't exist."""
    db_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)
    from erpclaw_lib.query import ddl_now
    conn.executescript(f"""
        CREATE TABLE IF NOT EXISTS erpclaw_deploy_audit (
            id              TEXT PRIMARY KEY,
            module_name     TEXT NOT NULL,
            pipeline_result TEXT NOT NULL CHECK(pipeline_result IN ('deployed', 'queued', 'rejected', 'failed')),
            tier            INTEGER,
            steps           TEXT NOT NULL,
            git_commit      TEXT,
            human_approved  INTEGER CHECK(human_approved IN (0, 1)),
            approved_by     TEXT,
            deployed_at     TEXT DEFAULT ({ddl_now()}),
            reasoning       TEXT
        );
    """)
    conn.commit()
    conn.close()


def record_deployment(module_name, pipeline_result, tier=None, steps=None,
                      git_commit=None, human_approved=None, approved_by=None,
                      reasoning=None, db_path=None):
    """Record a deployment attempt in the audit log.

    Args:
        module_name: Name of the module being deployed
        pipeline_result: 'deployed', 'queued', 'rejected', or 'failed'
        tier: Tier classification (0-3)
        steps: list of step dicts [{step_name, result, duration_ms, details}]
        git_commit: Git commit hash if applicable
        human_approved: 0 or 1
        approved_by: Who approved
        reasoning: AI's reasoning for the deployment decision
        db_path: Path to SQLite database

    Returns:
        str: The audit record ID
    """
    db_path = db_path or DEFAULT_DB_PATH
    ensure_deploy_audit_table(db_path)

    audit_id = str(uuid.uuid4())
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)
    conn.execute("""
        INSERT INTO erpclaw_deploy_audit
            (id, module_name, pipeline_result, tier, steps, git_commit,
             human_approved, approved_by, deployed_at, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        audit_id,
        module_name,
        pipeline_result,
        tier,
        json.dumps(steps or []),
        git_commit,
        human_approved,
        approved_by,
        datetime.now(timezone.utc).isoformat(),
        reasoning,
    ))
    conn.commit()
    conn.close()

    return audit_id


def query_audit_log(module_name=None, limit=50, db_path=None):
    """Query the deployment audit log.

    Args:
        module_name: Filter by module (optional)
        limit: Max records to return
        db_path: Path to SQLite database

    Returns:
        list of audit records
    """
    db_path = db_path or DEFAULT_DB_PATH
    ensure_deploy_audit_table(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    if module_name:
        rows = conn.execute(
            "SELECT * FROM erpclaw_deploy_audit WHERE module_name = ? ORDER BY deployed_at DESC LIMIT ?",
            (module_name, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM erpclaw_deploy_audit ORDER BY deployed_at DESC LIMIT ?",
            (limit,),
        ).fetchall()

    conn.close()

    records = []
    for row in rows:
        record = dict(row)
        # Parse steps JSON back to list
        if record.get("steps"):
            try:
                record["steps"] = json.loads(record["steps"])
            except (json.JSONDecodeError, TypeError):
                pass
        records.append(record)

    return records


def handle_deploy_audit_log(args):
    """CLI handler for deploy-audit-log action."""
    module_name = getattr(args, "module_name_arg", None) or getattr(args, "module_name", None)
    db_path = getattr(args, "db_path", None)
    limit = getattr(args, "limit", 50) or 50

    records = query_audit_log(module_name=module_name, limit=limit, db_path=db_path)

    return {
        "result": "ok",
        "records": records,
        "count": len(records),
        "filter": {"module_name": module_name, "limit": limit},
    }
