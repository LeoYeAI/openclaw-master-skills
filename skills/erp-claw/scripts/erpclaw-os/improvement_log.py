#!/usr/bin/env python3
"""ERPClaw OS — Self-Improvement Log (Phase 3, Deliverable 3b)

Records AI-proposed improvements with full provenance: category,
evidence, expected impact, proposed diff, and source system.
Supports review workflow (approve/reject/defer) and links to
deploy_audit for traceability.

This is the foundation for Phase 3 deliverables 3c, 3d, and 3e.
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

# Add shared lib to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))

from erpclaw_lib.db import get_connection
from erpclaw_lib.pagination import paginate
from erpclaw_lib.query import (
    Q, P, Table, Field, LiteralValue, insert_row, dynamic_update,
)

VALID_CATEGORIES = ("performance", "usability", "coverage", "semantic", "structural")
VALID_SOURCES = ("heartbeat", "dgm", "semantic", "manual", "gap_detector")
VALID_STATUSES = ("proposed", "approved", "rejected", "deferred", "deployed")


# ---------------------------------------------------------------------------
# Action: log-improvement
# ---------------------------------------------------------------------------

def handle_log_improvement(args):
    """Record an AI-proposed improvement.

    Required: --category, --description, --source
    Optional: --evidence (JSON), --expected-impact (JSON),
              --proposed-diff (JSON), --module-name
    """
    category = getattr(args, "category", None)
    description = getattr(args, "description", None)
    source = getattr(args, "source", None)
    evidence = getattr(args, "evidence", None)
    expected_impact = getattr(args, "expected_impact", None)
    proposed_diff = getattr(args, "proposed_diff", None)
    module_name = getattr(args, "module_name_arg", None) or getattr(args, "module_name", None)
    db_path = getattr(args, "db_path", None)

    if not category:
        return {"error": "--category is required"}
    if category not in VALID_CATEGORIES:
        return {"error": f"Invalid category: {category}. Must be one of: {', '.join(VALID_CATEGORIES)}"}
    if not description:
        return {"error": "--description is required"}
    if not source:
        return {"error": "--source is required"}
    if source not in VALID_SOURCES:
        return {"error": f"Invalid source: {source}. Must be one of: {', '.join(VALID_SOURCES)}"}

    # Validate JSON fields if provided
    for field_name, field_val in [("evidence", evidence), ("expected_impact", expected_impact), ("proposed_diff", proposed_diff)]:
        if field_val:
            try:
                json.loads(field_val)
            except (json.JSONDecodeError, TypeError):
                return {"error": f"--{field_name.replace('_', '-')} must be valid JSON"}

    improvement_id = str(uuid.uuid4())
    conn = get_connection(db_path)
    try:
        sql, cols = insert_row("erpclaw_improvement_log", {
            "id": P(),
            "module_name": P(),
            "category": P(),
            "description": P(),
            "evidence": P(),
            "proposed_diff": P(),
            "expected_impact": P(),
            "source": P(),
            "status": P(),
            "proposed_at": LiteralValue("datetime('now')"),
        })
        conn.execute(sql, [
            improvement_id,
            module_name,
            category,
            description,
            evidence,
            proposed_diff,
            expected_impact,
            source,
            "proposed",
        ])
        conn.commit()
    finally:
        conn.close()

    return {
        "result": "ok",
        "improvement_id": improvement_id,
        "category": category,
        "source": source,
        "status": "proposed",
    }


# ---------------------------------------------------------------------------
# Action: list-improvements
# ---------------------------------------------------------------------------

def handle_list_improvements(args):
    """List improvements with optional filters and pagination.

    Filters: --category, --status, --module-name, --source,
             --from-date, --to-date
    Pagination: --limit (page_size), --offset (mapped to page)
    """
    category = getattr(args, "category", None)
    status = getattr(args, "status_filter", None)
    module_name = getattr(args, "module_name_arg", None) or getattr(args, "module_name", None)
    source = getattr(args, "source", None)
    from_date = getattr(args, "from_date", None)
    to_date = getattr(args, "to_date", None)
    limit = getattr(args, "limit", 50) or 50
    offset = getattr(args, "offset", 0) or 0
    db_path = getattr(args, "db_path", None)

    t = Table("erpclaw_improvement_log")
    q = Q.from_(t).select(t.star)
    params = []

    if category:
        q = q.where(t.category == P())
        params.append(category)
    if status:
        q = q.where(t.status == P())
        params.append(status)
    if module_name:
        q = q.where(t.module_name == P())
        params.append(module_name)
    if source:
        q = q.where(t.source == P())
        params.append(source)
    if from_date:
        q = q.where(t.proposed_at >= P())
        params.append(from_date)
    if to_date:
        q = q.where(t.proposed_at <= P())
        params.append(to_date)

    base_sql = q.get_sql()

    conn = get_connection(db_path)
    try:
        # Convert limit/offset to page/page_size for paginate()
        page_size = limit
        page = (offset // page_size) + 1 if offset else 1

        result = paginate(
            conn,
            base_sql,
            tuple(params),
            page=page,
            page_size=page_size,
            order_by='"proposed_at" DESC',
        )

        # Parse JSON fields in each item
        for item in result["items"]:
            for json_field in ("evidence", "expected_impact", "proposed_diff"):
                if item.get(json_field):
                    try:
                        item[json_field] = json.loads(item[json_field])
                    except (json.JSONDecodeError, TypeError):
                        pass
    finally:
        conn.close()

    return {
        "result": "ok",
        **result,
    }


# ---------------------------------------------------------------------------
# Action: review-improvement
# ---------------------------------------------------------------------------

def handle_review_improvement(args):
    """Review an improvement: approve, reject, or defer.

    Required: --improvement-id, --status (approved/rejected/deferred)
    Optional: --review-notes, --reviewed-by, --deploy (flag to create deploy_audit entry)
    """
    improvement_id = getattr(args, "improvement_id", None)
    new_status = getattr(args, "new_status", None)
    review_notes = getattr(args, "review_notes", None)
    reviewed_by = getattr(args, "reviewed_by", None) or "system"
    deploy = getattr(args, "deploy", False)
    db_path = getattr(args, "db_path", None)

    if not improvement_id:
        return {"error": "--improvement-id is required"}
    if not new_status:
        return {"error": "--status is required (approved, rejected, or deferred)"}
    if new_status not in ("approved", "rejected", "deferred"):
        return {"error": f"Invalid review status: {new_status}. Must be approved, rejected, or deferred."}

    conn = get_connection(db_path)
    try:
        # Fetch existing record
        row = conn.execute(
            'SELECT id, status, module_name, description FROM erpclaw_improvement_log WHERE id = ?',
            (improvement_id,),
        ).fetchone()

        if not row:
            return {"error": f"Improvement not found: {improvement_id}"}

        current_status = row["status"]

        # Validate status transition
        if current_status == "deployed":
            return {"error": f"Cannot review a deployed improvement (id={improvement_id})"}
        if current_status in ("approved", "rejected", "deferred"):
            # Allow re-review from non-terminal states
            pass

        update_data = {
            "status": new_status,
            "reviewed_at": LiteralValue("datetime('now')"),
            "reviewed_by": reviewed_by,
        }
        if review_notes:
            update_data["review_notes"] = review_notes

        deploy_audit_id = None

        # If approved + deploy flag, create deploy_audit entry
        if new_status == "approved" and deploy:
            try:
                from deploy_audit import record_deployment
                deploy_audit_id = record_deployment(
                    module_name=row["module_name"] or "erpclaw-os",
                    pipeline_result="deployed",
                    reasoning=f"Self-improvement deployed: {row['description'][:100]}",
                    db_path=db_path,
                )
                update_data["deploy_audit_id"] = deploy_audit_id
                update_data["status"] = "deployed"
            except ImportError:
                # deploy_audit not available in test context — skip
                pass

        sql, params = dynamic_update(
            "erpclaw_improvement_log",
            update_data,
            {"id": improvement_id},
        )
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()

    result = {
        "result": "ok",
        "improvement_id": improvement_id,
        "previous_status": current_status,
        "new_status": update_data["status"],
        "reviewed_by": reviewed_by,
    }
    if review_notes:
        result["review_notes"] = review_notes
    if deploy_audit_id:
        result["deploy_audit_id"] = deploy_audit_id

    return result
