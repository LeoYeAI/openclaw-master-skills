"""EduClaw LMS Integration — assignments domain module

Actions for bidirectional SIS↔LMS assignment mapping.

Actions (5):
  submit-assessment-to-lms, import-lms-assignments, apply-assessment-update,
  list-lms-assignments, delete-lms-assignment

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw-lms"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_GRADE_SCHEMES = ("points", "percentage", "pass_fail", "letter_grade")
VALID_ASSIGNMENT_SYNC_STATUSES = ("synced", "pending", "error")


def _get_encryption_key():
    import hashlib
    key_str = os.environ.get("EDUCLAW_LMS_ENCRYPTION_KEY", "")
    if not key_str:
        return None
    return hashlib.sha256(key_str.encode()).digest()


def _get_adapter(conn_row, key=None):
    """Return the appropriate LMS adapter."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from lms_sync import _decrypt_cred, _get_adapter as _sync_get_adapter
    return _sync_get_adapter(conn_row, key)


def _log_ferpa_access(conn, student_id, company_id, access_reason, triggered_by="system"):
    """Write a FERPA data access log entry."""
    log_id = str(uuid.uuid4())
    try:
        conn.execute(
            """INSERT INTO educlaw_data_access_log
               (id, user_id, student_id, data_category, access_type, access_reason,
                is_emergency_access, ip_address, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (log_id, triggered_by, student_id, "grades", "api",
             access_reason, 0, "", company_id, _now_iso(), triggered_by)
        )
    except Exception:
        pass


def _next_lms_series(conn, entity_type, prefix, company_id, use_year=True):
    """Generate next sequential naming series."""
    year = datetime.now(timezone.utc).year
    full_prefix = f"{prefix}{year}-" if use_year else prefix
    entry_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO naming_series (id, entity_type, prefix, current_value, company_id)
           VALUES (?, ?, ?, 1, ?)
           ON CONFLICT(entity_type, prefix, company_id)
           DO UPDATE SET current_value = current_value + 1""",
        (entry_id, entity_type, full_prefix, company_id)
    )
    row = conn.execute(
        "SELECT current_value FROM naming_series WHERE entity_type = ? AND prefix = ? AND company_id = ?",
        (entity_type, full_prefix, company_id)
    ).fetchone()
    seq = row[0] if row else 1
    return f"{full_prefix}{seq:05d}"


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: submit-assessment-to-lms
# ─────────────────────────────────────────────────────────────────────────────

def push_assessment_to_lms(conn, args):
    """Push a SIS assessment to LMS as an assignment."""
    assessment_id = getattr(args, "assessment_id", None) or None
    conn_id = getattr(args, "connection_id", None) or None
    triggered_by = getattr(args, "user_id", None) or "system"

    if not assessment_id:
        err("--assessment-id is required")
    if not conn_id:
        err("--connection-id is required")

    # Load assessment
    assessment = conn.execute(
        "SELECT * FROM educlaw_assessment WHERE id = ?", (assessment_id,)
    ).fetchone()
    if not assessment:
        err(f"Assessment {assessment_id} not found")
    assessment = dict(assessment)

    # Load assessment plan to find section
    plan = conn.execute(
        "SELECT * FROM educlaw_assessment_plan WHERE id = ?",
        (assessment["assessment_plan_id"],)
    ).fetchone()
    if not plan:
        err(f"Assessment plan for assessment {assessment_id} not found")
    plan = dict(plan)

    section_id = getattr(args, "section_id", None) or plan["section_id"]

    # Load LMS connection
    lms_conn = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    if not lms_conn:
        err(f"LMS connection {conn_id} not found")
    lms_conn = dict(lms_conn)

    # DPA gate
    if not int(lms_conn.get("has_dpa_signed", 0) or 0):
        err("E_DPA_REQUIRED: Data Processing Agreement must be signed before pushing assignments")

    # Check that course mapping exists and is not closed
    course_mapping = conn.execute(
        """SELECT * FROM educlaw_lms_course_mapping
           WHERE lms_connection_id = ? AND section_id = ? AND sync_status != 'closed'""",
        (conn_id, section_id)
    ).fetchone()
    if not course_mapping:
        err(f"No active LMS course mapping found for section {section_id} on connection {conn_id}. Run apply-course-sync first.")
    course_mapping = dict(course_mapping)

    # Check for existing mapping (prevent duplicates)
    existing_mapping = conn.execute(
        "SELECT * FROM educlaw_lms_assignment_mapping WHERE lms_connection_id = ? AND assessment_id = ?",
        (conn_id, assessment_id)
    ).fetchone()
    if existing_mapping:
        d = dict(existing_mapping)
        ok({
            "id": d["id"],
            "assessment_id": assessment_id,
            "lms_assignment_id": d["lms_assignment_id"],
            "lms_assignment_url": d["lms_assignment_url"],
            "sync_status": d["sync_status"],
            "message": "Assessment already mapped to LMS — use apply-assessment-update to push changes",
        })

    # Determine grading scheme
    lms_grade_scheme = getattr(args, "lms_grade_scheme", None) or "points"
    if lms_grade_scheme not in VALID_GRADE_SCHEMES:
        err(f"--lms-grade-scheme must be one of: {', '.join(VALID_GRADE_SCHEMES)}")

    key = _get_encryption_key()
    company_id = lms_conn.get("company_id", "")

    lms_course_id = course_mapping.get("lms_course_id", "")
    assignment_data = {
        "lms_course_id": lms_course_id,
        "name": assessment.get("name", ""),
        "description": assessment.get("description", "") or "",
        "max_points": assessment.get("max_points", "0") or "0",
        "due_date": assessment.get("due_date", "") or "",
        "is_published": assessment.get("is_published", 0),
        "lms_grade_scheme": lms_grade_scheme,
    }

    mapping_id = str(uuid.uuid4())
    lms_assignment_id = ""
    lms_assignment_url = ""
    sync_status = "synced"

    if lms_conn.get("lms_type") != "oneroster_csv":
        try:
            adapter = _get_adapter(lms_conn, key)
            if adapter:
                result = adapter.push_assignment(assignment_data, lms_conn)
                lms_assignment_id = result.get("lms_assignment_id", "")
                lms_assignment_url = result.get("lms_assignment_url", "")
        except Exception as e:
            sync_status = "error"
            lms_assignment_id = f"push_failed_{assessment_id[:8]}"
    else:
        # OneRoster CSV — create synthetic mapping
        lms_assignment_id = f"oneroster_assign_{assessment_id[:8]}"

    try:
        conn.execute(
            """INSERT INTO educlaw_lms_assignment_mapping
               (id, lms_connection_id, assessment_id, lms_assignment_id,
                lms_assignment_url, lms_grade_scheme, push_direction,
                is_published_in_lms, sync_status, last_synced_at,
                created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, 'sis_to_lms', ?, ?, ?, ?, ?)""",
            (mapping_id, conn_id, assessment_id, lms_assignment_id,
             lms_assignment_url, lms_grade_scheme,
             int(assessment.get("is_published", 0) or 0),
             sync_status, _now_iso(), _now_iso(), triggered_by)
        )
    except sqlite3.IntegrityError as e:
        err(f"Assignment mapping already exists: {e}")

    # Create assignment_push sync log entry
    log_id = str(uuid.uuid4())
    log_naming = _next_lms_series(
        conn, "educlaw_lms_sync_log", "SYN-", company_id, use_year=True
    )
    now = _now_iso()
    conn.execute(
        """INSERT INTO educlaw_lms_sync_log
           (id, naming_series, lms_connection_id, sync_type, section_id,
            triggered_by, status, sections_synced, started_at, completed_at,
            company_id, created_at, created_by)
           VALUES (?, ?, ?, 'assignment_push', ?, ?, 'completed', 1, ?, ?, ?, ?, ?)""",
        (log_id, log_naming, conn_id, section_id, triggered_by,
         now, now, company_id, now, triggered_by)
    )

    # FERPA disclosure log — log per student enrolled in this section
    # (assignment pushed = academic disclosure to LMS)
    try:
        enrollments = conn.execute(
            """SELECT student_id FROM educlaw_course_enrollment
               WHERE section_id = ? AND enrollment_status IN ('enrolled', 'completed')""",
            (section_id,)
        ).fetchall()
        for enr in enrollments:
            _log_ferpa_access(
                conn, enr[0], company_id,
                f"LMS assignment disclosure: {assessment.get('name', '')} to {lms_conn.get('display_name', 'LMS')}",
                triggered_by
            )
    except Exception:
        pass

    try:
        audit(conn, SKILL, "submit-assessment-to-lms", "educlaw_lms_assignment_mapping", mapping_id,
              new_values={"assessment_id": assessment_id, "lms_assignment_id": lms_assignment_id,
                          "sync_status": sync_status})
    except Exception:
        pass
    conn.commit()
    ok({
        "id": mapping_id,
        "assessment_id": assessment_id,
        "lms_assignment_id": lms_assignment_id,
        "lms_assignment_url": lms_assignment_url,
        "assignment_sync_status": sync_status,
        "sync_log_id": log_id,
        "message": "Assessment pushed to LMS",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: import-lms-assignments
# ─────────────────────────────────────────────────────────────────────────────

def pull_lms_assignments(conn, args):
    """Pull unmapped assignments from an LMS course."""
    conn_id = getattr(args, "connection_id", None) or None
    section_id = getattr(args, "section_id", None) or None
    create_assessments = getattr(args, "create_assessments", None) or False
    plan_id = getattr(args, "plan_id", None) or None
    category_id = getattr(args, "category_id", None) or None
    triggered_by = getattr(args, "user_id", None) or "system"

    if not conn_id:
        err("--connection-id is required")
    if not section_id:
        err("--section-id is required")

    # Load connection
    lms_conn = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    if not lms_conn:
        err(f"LMS connection {conn_id} not found")
    lms_conn = dict(lms_conn)

    if not int(lms_conn.get("has_dpa_signed", 0) or 0):
        err("E_DPA_REQUIRED: Data Processing Agreement must be signed before pulling assignments")

    # Get course mapping
    course_mapping = conn.execute(
        """SELECT * FROM educlaw_lms_course_mapping
           WHERE lms_connection_id = ? AND section_id = ? AND sync_status != 'closed'""",
        (conn_id, section_id)
    ).fetchone()
    if not course_mapping:
        err(f"No active LMS course mapping for section {section_id} on connection {conn_id}. Run apply-course-sync first.")
    course_mapping = dict(course_mapping)

    key = _get_encryption_key()
    lms_course_id = course_mapping.get("lms_course_id", "")
    company_id = lms_conn.get("company_id", "")

    lms_assignments = []
    if lms_conn.get("lms_type") != "oneroster_csv":
        try:
            adapter = _get_adapter(lms_conn, key)
            if adapter:
                lms_assignments = adapter.pull_all_assignments(lms_course_id, lms_conn)
        except Exception as e:
            err(f"Failed to pull assignments from LMS: {e}")

    # Get existing mappings for this connection
    existing_maps = conn.execute(
        "SELECT lms_assignment_id FROM educlaw_lms_assignment_mapping WHERE lms_connection_id = ?",
        (conn_id,)
    ).fetchall()
    already_mapped = {r[0] for r in existing_maps}

    # If create_assessments, validate plan_id
    if create_assessments:
        # Use provided plan_id or look up default for section
        if not plan_id:
            plan_row = conn.execute(
                "SELECT id FROM educlaw_assessment_plan WHERE section_id = ?", (section_id,)
            ).fetchone()
            if plan_row:
                plan_id = plan_row[0]
        if not plan_id:
            err("--plan-id is required when --create-assessments is used and no plan exists for section")
        # Validate plan
        plan_row = conn.execute(
            "SELECT id FROM educlaw_assessment_plan WHERE id = ?", (plan_id,)
        ).fetchone()
        if not plan_row:
            err(f"Assessment plan {plan_id} not found")
        # Need a category if creating assessments
        if category_id:
            cat_row = conn.execute(
                "SELECT id FROM educlaw_assessment_category WHERE id = ? AND assessment_plan_id = ?",
                (category_id, plan_id)
            ).fetchone()
            if not cat_row:
                err(f"Assessment category {category_id} not found in plan {plan_id}")

    created_mappings = []
    skipped_count = 0
    now = _now_iso()

    for lms_assign in lms_assignments:
        lms_assign_id = lms_assign.get("lms_assignment_id", "")
        if not lms_assign_id or lms_assign_id in already_mapped:
            skipped_count += 1
            continue

        # Create assessment record if requested
        assessment_id_to_link = None
        if create_assessments and plan_id:
            assess_id = str(uuid.uuid4())
            # Need a category_id for assessment
            cat = category_id
            if not cat:
                # Get first category for this plan
                first_cat = conn.execute(
                    "SELECT id FROM educlaw_assessment_category WHERE assessment_plan_id = ? ORDER BY sort_order LIMIT 1",
                    (plan_id,)
                ).fetchone()
                cat = first_cat[0] if first_cat else None
            if cat:
                try:
                    conn.execute(
                        """INSERT INTO educlaw_assessment
                           (id, assessment_plan_id, category_id, name, description,
                            max_points, due_date, is_published, allows_extra_credit,
                            sort_order, created_at, updated_at, created_by)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)""",
                        (assess_id, plan_id, cat,
                         lms_assign.get("name", ""),
                         "",
                         lms_assign.get("max_points", "0") or "0",
                         lms_assign.get("due_date", "") or "",
                         lms_assign.get("is_published", 0),
                         now, now, triggered_by)
                    )
                    assessment_id_to_link = assess_id
                except sqlite3.IntegrityError:
                    pass

        # Create assignment mapping with lms_to_sis direction
        mapping_id = str(uuid.uuid4())
        grade_scheme = lms_assign.get("lms_grade_scheme", "points") or "points"
        if grade_scheme not in VALID_GRADE_SCHEMES:
            grade_scheme = "points"

        try:
            if assessment_id_to_link:
                conn.execute(
                    """INSERT INTO educlaw_lms_assignment_mapping
                       (id, lms_connection_id, assessment_id, lms_assignment_id,
                        lms_assignment_url, lms_grade_scheme, push_direction,
                        is_published_in_lms, sync_status, last_synced_at,
                        created_at, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, 'lms_to_sis', ?, 'synced', ?, ?, ?)""",
                    (mapping_id, conn_id, assessment_id_to_link, lms_assign_id,
                     lms_assign.get("lms_assignment_url", ""),
                     grade_scheme,
                     int(lms_assign.get("is_published", 0) or 0),
                     now, now, triggered_by)
                )
            else:
                # No assessment — store mapping with empty assessment reference (not valid FK)
                # Skip if no assessment can be linked and create_assessments is False
                if not create_assessments:
                    # Just log it as discovered but not mapped
                    created_mappings.append({
                        "lms_assignment_id": lms_assign_id,
                        "name": lms_assign.get("name", ""),
                        "mapped": False,
                        "note": "No assessment to link — use --create-assessments",
                    })
                    continue

            created_mappings.append({
                "id": mapping_id,
                "lms_assignment_id": lms_assign_id,
                "name": lms_assign.get("name", ""),
                "assessment_id": assessment_id_to_link,
                "mapped": True,
            })
        except sqlite3.IntegrityError:
            skipped_count += 1

    conn.commit()
    ok({
        "connection_id": conn_id,
        "section_id": section_id,
        "lms_assignments_found": len(lms_assignments),
        "mappings_created": len([m for m in created_mappings if m.get("mapped")]),
        "skipped_existing": skipped_count,
        "assignments": created_mappings,
        "message": "LMS assignments pulled",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: apply-assessment-update
# ─────────────────────────────────────────────────────────────────────────────

def sync_assessment_update(conn, args):
    """Push updated assessment fields to LMS."""
    assessment_id = getattr(args, "assessment_id", None) or None
    conn_id = getattr(args, "connection_id", None) or None

    if not assessment_id:
        err("--assessment-id is required")
    if not conn_id:
        err("--connection-id is required")

    # Load assessment
    assessment = conn.execute(
        "SELECT * FROM educlaw_assessment WHERE id = ?", (assessment_id,)
    ).fetchone()
    if not assessment:
        err(f"Assessment {assessment_id} not found")
    assessment = dict(assessment)

    # Load connection
    lms_conn = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    if not lms_conn:
        err(f"LMS connection {conn_id} not found")
    lms_conn = dict(lms_conn)

    # Load mapping
    mapping = conn.execute(
        "SELECT * FROM educlaw_lms_assignment_mapping WHERE lms_connection_id = ? AND assessment_id = ?",
        (conn_id, assessment_id)
    ).fetchone()
    if not mapping:
        ok({
            "assessment_id": assessment_id,
            "connection_id": conn_id,
            "updated": False,
            "message": "Assessment has no LMS mapping — use submit-assessment-to-lms first",
        })

    mapping = dict(mapping)
    if mapping.get("sync_status") == "error":
        # Still attempt update even with error status
        pass

    key = _get_encryption_key()

    # Get course mapping for lms_course_id
    plan = conn.execute(
        "SELECT section_id FROM educlaw_assessment_plan WHERE id = ?",
        (assessment["assessment_plan_id"],)
    ).fetchone()
    section_id = plan[0] if plan else None

    lms_course_id = ""
    if section_id:
        cm = conn.execute(
            """SELECT lms_course_id FROM educlaw_lms_course_mapping
               WHERE lms_connection_id = ? AND section_id = ? AND sync_status != 'closed'""",
            (conn_id, section_id)
        ).fetchone()
        if cm:
            lms_course_id = cm[0]

    warning = None
    updated = False

    if lms_conn.get("lms_type") != "oneroster_csv" and lms_course_id:
        try:
            adapter = _get_adapter(lms_conn, key)
            if adapter:
                update_data = {
                    "lms_course_id": lms_course_id,
                    "name": assessment.get("name", ""),
                    "max_points": assessment.get("max_points", "0"),
                    "due_date": assessment.get("due_date", "") or "",
                    "is_published": assessment.get("is_published", 0),
                }
                result = adapter.update_assignment(
                    update_data, mapping["lms_assignment_id"], lms_conn
                )
                updated = result.get("updated", False)
                warning = result.get("warning")
        except Exception as e:
            conn.execute(
                "UPDATE educlaw_lms_assignment_mapping SET sync_status = 'error', sync_error = ? WHERE id = ?",
                (str(e)[:500], mapping["id"])
            )
            conn.commit()
            err(f"LMS update failed: {e}")
    else:
        updated = True  # OneRoster CSV: no live API

    if updated:
        conn.execute(
            """UPDATE educlaw_lms_assignment_mapping
               SET sync_status = 'synced', last_synced_at = ?, sync_error = '',
                   is_published_in_lms = ?
               WHERE id = ?""",
            (_now_iso(), int(assessment.get("is_published", 0) or 0), mapping["id"])
        )
        conn.commit()

    try:
        audit(conn, SKILL, "apply-assessment-update", "educlaw_lms_assignment_mapping", mapping["id"],
              new_values={"updated": updated, "warning": warning})
    except Exception:
        pass

    ok({
        "id": mapping["id"],
        "assessment_id": assessment_id,
        "lms_assignment_id": mapping["lms_assignment_id"],
        "updated": updated,
        "warning": warning,
        "message": "Assessment update synced to LMS" if updated else "No update performed",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-lms-assignments
# ─────────────────────────────────────────────────────────────────────────────

def list_lms_assignments(conn, args):
    """List assessments with LMS assignment mappings."""
    conn_id = getattr(args, "connection_id", None) or None
    section_id = getattr(args, "section_id", None) or None
    sync_status_filter = getattr(args, "assignment_sync_status", None) or None

    if not conn_id:
        err("--connection-id is required")

    where = ["am.lms_connection_id = ?"]
    params = [conn_id]

    if section_id:
        # Filter via assessment_plan.section_id
        where.append("ap.section_id = ?"); params.append(section_id)

    if sync_status_filter:
        if sync_status_filter not in VALID_ASSIGNMENT_SYNC_STATUSES:
            err(f"--assignment-sync-status must be one of: {', '.join(VALID_ASSIGNMENT_SYNC_STATUSES)}")
        where.append("am.sync_status = ?"); params.append(sync_status_filter)

    rows = conn.execute(
        f"""SELECT am.id as mapping_id, am.assessment_id, am.lms_assignment_id,
                   am.lms_assignment_url, am.lms_grade_scheme, am.push_direction,
                   am.is_published_in_lms, am.sync_status, am.last_synced_at,
                   am.sync_error, am.created_at,
                   a.name as assessment_name, a.max_points, a.due_date, a.is_published,
                   ap.section_id
            FROM educlaw_lms_assignment_mapping am
            JOIN educlaw_assessment a ON a.id = am.assessment_id
            JOIN educlaw_assessment_plan ap ON ap.id = a.assessment_plan_id
            WHERE {' AND '.join(where)}
            ORDER BY am.created_at DESC""",
        params
    ).fetchall()

    assignments = []
    for r in rows:
        d = dict(r)
        d["assignment_sync_status"] = d.pop("sync_status")
        assignments.append(d)

    ok({"assignments": assignments, "total": len(assignments)})


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: delete-lms-assignment
# ─────────────────────────────────────────────────────────────────────────────

def unlink_lms_assignment(conn, args):
    """Remove the LMS assignment mapping (soft-delete via status update)."""
    assessment_id = getattr(args, "assessment_id", None) or None
    conn_id = getattr(args, "connection_id", None) or None

    if not assessment_id:
        err("--assessment-id is required")
    if not conn_id:
        err("--connection-id is required")

    mapping = conn.execute(
        "SELECT * FROM educlaw_lms_assignment_mapping WHERE lms_connection_id = ? AND assessment_id = ?",
        (conn_id, assessment_id)
    ).fetchone()
    if not mapping:
        err(f"No LMS assignment mapping found for assessment {assessment_id} on connection {conn_id}")
    mapping = dict(mapping)

    # Soft-delete: set sync_status = 'error' with unlinked note
    conn.execute(
        """UPDATE educlaw_lms_assignment_mapping
           SET sync_status = 'error', sync_error = 'unlinked by user', last_synced_at = ?
           WHERE id = ?""",
        (_now_iso(), mapping["id"])
    )
    try:
        audit(conn, SKILL, "delete-lms-assignment", "educlaw_lms_assignment_mapping", mapping["id"],
              new_values={"sync_status": "error", "sync_error": "unlinked by user"})
    except Exception:
        pass
    conn.commit()
    ok({
        "id": mapping["id"],
        "assessment_id": assessment_id,
        "lms_assignment_id": mapping["lms_assignment_id"],
        "assignment_sync_status": "error",
        "message": "LMS assignment mapping unlinked. Future grade pulls will skip this assessment.",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "submit-assessment-to-lms": push_assessment_to_lms,
    "import-lms-assignments": pull_lms_assignments,
    "apply-assessment-update": sync_assessment_update,
    "list-lms-assignments": list_lms_assignments,
    "delete-lms-assignment": unlink_lms_assignment,
}
