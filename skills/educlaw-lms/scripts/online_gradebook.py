"""EduClaw LMS Integration — online_gradebook domain module

Actions for grade pull from LMS, gradebook view, conflict resolution,
OneRoster CSV export, and LMS course closure.

Actions (6):
  import-grades, get-online-gradebook, list-grade-conflicts,
  apply-grade-resolution, generate-oneroster-csv, complete-lms-course

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw-lms"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_RESOLUTIONS = ("lms_wins", "sis_wins", "manual")
VALID_CONFLICT_TYPES = (
    "score_mismatch", "submitted_grade_locked", "student_not_found", "assignment_not_found"
)
VALID_GRADE_SYNC_STATUSES = ("pulled", "applied", "conflict", "skipped", "error")


def _d(val, default="0"):
    """Safe Decimal conversion."""
    try:
        return Decimal(str(val)) if val not in (None, "", "None") else Decimal(default)
    except (InvalidOperation, Exception):
        return Decimal(default)


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
    from lms_sync import _get_adapter as _sync_get_adapter
    return _sync_get_adapter(conn_row, key)


def _log_ferpa_access(conn, student_id, company_id, access_reason, triggered_by="system"):
    """Write a FERPA data access log entry for grade access."""
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
# ACTION: import-grades
# ─────────────────────────────────────────────────────────────────────────────

def pull_grades(conn, args):
    """Pull LMS submission scores into educlaw_lms_grade_sync staging."""
    conn_id = getattr(args, "connection_id", None) or None
    section_id = getattr(args, "section_id", None) or None
    assessment_id_filter = getattr(args, "assessment_id", None) or None
    academic_term_id = getattr(args, "academic_term_id", None) or None
    triggered_by = getattr(args, "user_id", None) or "system"

    if not conn_id:
        err("--connection-id is required")

    # Load connection
    lms_conn = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    if not lms_conn:
        err(f"LMS connection {conn_id} not found")
    lms_conn = dict(lms_conn)

    # DPA gate
    if not int(lms_conn.get("has_dpa_signed", 0) or 0):
        err("E_DPA_REQUIRED: Data Processing Agreement must be signed before pulling grades")

    grade_direction = lms_conn.get("grade_direction", "lms_to_sis") or "lms_to_sis"
    company_id = lms_conn.get("company_id", "")

    # If grade_direction = 'sis_to_lms', skip all grade pulls
    if grade_direction == "sis_to_lms":
        ok({
            "connection_id": conn_id,
            "grade_direction": grade_direction,
            "grades_pulled": 0,
            "message": "Grade direction is sis_to_lms — no grades pulled from LMS",
        })

    # Create sync log
    log_id = str(uuid.uuid4())
    log_naming = _next_lms_series(
        conn, "educlaw_lms_sync_log", "SYN-", company_id, use_year=True
    )
    now = _now_iso()
    conn.execute(
        """INSERT INTO educlaw_lms_sync_log
           (id, naming_series, lms_connection_id, sync_type,
            academic_term_id, section_id, triggered_by, status,
            started_at, company_id, created_at, created_by)
           VALUES (?, ?, ?, 'grade_pull', ?, ?, ?, 'running', ?, ?, ?, ?)""",
        (log_id, log_naming, conn_id, academic_term_id,
         section_id, triggered_by, now, company_id, now, triggered_by)
    )
    conn.commit()

    key = _get_encryption_key()
    adapter = None
    if lms_conn.get("lms_type") != "oneroster_csv":
        try:
            adapter = _get_adapter(lms_conn, key)
        except Exception as e:
            conn.execute(
                """UPDATE educlaw_lms_sync_log SET status = 'failed', completed_at = ?, errors_count = 1
                   WHERE id = ?""",
                (_now_iso(), log_id)
            )
            conn.commit()
            err(f"Failed to initialize LMS adapter: {e}")

    # Load assignment mappings in scope
    map_where = ["am.lms_connection_id = ?", "am.sync_status != 'error'"]
    map_params = [conn_id]

    if assessment_id_filter:
        map_where.append("am.assessment_id = ?"); map_params.append(assessment_id_filter)

    if section_id:
        map_where.append("ap.section_id = ?"); map_params.append(section_id)
    elif academic_term_id:
        map_where.append("ats.academic_term_id = ?"); map_params.append(academic_term_id)

    rows = conn.execute(
        f"""SELECT am.*, a.max_points, a.name as assessment_name, ap.section_id,
                   cm.lms_course_id, cm.sync_status as course_map_status
            FROM educlaw_lms_assignment_mapping am
            JOIN educlaw_assessment a ON a.id = am.assessment_id
            JOIN educlaw_assessment_plan ap ON ap.id = a.assessment_plan_id
            LEFT JOIN educlaw_lms_course_mapping cm
                ON cm.lms_connection_id = am.lms_connection_id AND cm.section_id = ap.section_id
            LEFT JOIN educlaw_section ats ON ats.id = ap.section_id
            WHERE {' AND '.join(map_where)}""",
        map_params
    ).fetchall()
    assignment_mappings = [dict(r) for r in rows]

    grades_pulled = 0
    grades_applied = 0
    conflicts_flagged = 0
    errors_count = 0
    error_summary = []

    for am in assignment_mappings:
        # Skip if course is closed
        if am.get("course_map_status") == "closed":
            continue

        lms_course_id = am.get("lms_course_id", "")
        lms_assignment_id = am.get("lms_assignment_id", "")

        if not lms_course_id or not lms_assignment_id:
            continue

        try:
            if adapter:
                raw_grades = adapter.pull_grades(lms_course_id, lms_assignment_id, lms_conn)
            else:
                raw_grades = []

            for grade_data in raw_grades:
                lms_user_id = grade_data.get("lms_user_id", "")
                if not lms_user_id:
                    continue

                # Resolve lms_user_id → student_id
                user_map = conn.execute(
                    """SELECT sis_user_id FROM educlaw_lms_user_mapping
                       WHERE lms_connection_id = ? AND lms_user_id = ? AND sis_user_type = 'student'""",
                    (conn_id, lms_user_id)
                ).fetchone()

                student_id = user_map[0] if user_map else None
                assessment_id = am.get("assessment_id", "")

                # Determine conflict type
                conflict_type = ""
                is_conflict = 0
                sync_status_val = "pulled"
                sis_score = ""
                assessment_result_id = None
                lms_score = grade_data.get("lms_score", "") or ""

                if not student_id:
                    # Student not found in mapping
                    conflict_type = "student_not_found"
                    is_conflict = 1
                    sync_status_val = "conflict"
                    conflicts_flagged += 1
                elif not assessment_id:
                    # Assignment not mapped
                    conflict_type = "assignment_not_found"
                    is_conflict = 1
                    sync_status_val = "conflict"
                    conflicts_flagged += 1
                else:
                    # Check existing SIS result
                    sis_result = conn.execute(
                        """SELECT ar.id, ar.points_earned, ce.is_grade_submitted
                           FROM educlaw_assessment_result ar
                           JOIN educlaw_course_enrollment ce
                               ON ce.student_id = ar.student_id AND ce.section_id = ?
                           WHERE ar.assessment_id = ? AND ar.student_id = ?
                           ORDER BY ar.created_at DESC LIMIT 1""",
                        (am.get("section_id", ""), assessment_id, student_id)
                    ).fetchone()

                    if sis_result:
                        sis_result = dict(sis_result)
                        sis_score = sis_result.get("points_earned", "") or ""
                        is_grade_submitted = int(sis_result.get("is_grade_submitted", 0) or 0)
                        existing_result_id = sis_result["id"]

                        # Compare scores
                        if lms_score and sis_score:
                            try:
                                lms_dec = _d(lms_score)
                                sis_dec = _d(sis_score)
                                scores_match = (lms_dec == sis_dec)
                            except Exception:
                                scores_match = (lms_score == sis_score)
                        else:
                            scores_match = not lms_score and not sis_score

                        if scores_match:
                            sync_status_val = "skipped"
                        elif is_grade_submitted:
                            # Submitted grade — cannot auto-apply
                            conflict_type = "submitted_grade_locked"
                            is_conflict = 1
                            sync_status_val = "conflict"
                            conflicts_flagged += 1
                        else:
                            # Score mismatch — flag conflict
                            conflict_type = "score_mismatch"
                            is_conflict = 1
                            sync_status_val = "conflict"
                            conflicts_flagged += 1
                    else:
                        # No existing SIS result — auto-apply if lms_to_sis
                        if grade_direction == "lms_to_sis" and lms_score:
                            # Get course_enrollment_id
                            enr = conn.execute(
                                """SELECT id FROM educlaw_course_enrollment
                                   WHERE student_id = ? AND section_id = ?
                                   AND enrollment_status IN ('enrolled','completed')
                                   ORDER BY created_at DESC LIMIT 1""",
                                (student_id, am.get("section_id", ""))
                            ).fetchone()
                            if enr:
                                new_result_id = str(uuid.uuid4())
                                try:
                                    conn.execute(
                                        """INSERT INTO educlaw_assessment_result
                                           (id, assessment_id, student_id, course_enrollment_id,
                                            points_earned, is_exempt, is_late, comments,
                                            graded_by, graded_at, created_at, updated_at, created_by)
                                           VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)""",
                                        (new_result_id, assessment_id, student_id, enr[0],
                                         lms_score,
                                         int(grade_data.get("is_late", 0) or 0),
                                         grade_data.get("lms_comments", "") or "",
                                         "lms_sync",
                                         grade_data.get("lms_graded_at", "") or _now_iso(),
                                         _now_iso(), _now_iso(), "lms_sync")
                                    )
                                    assessment_result_id = new_result_id
                                    grades_applied += 1
                                    sync_status_val = "applied"
                                except sqlite3.IntegrityError:
                                    sync_status_val = "pulled"
                            else:
                                sync_status_val = "pulled"
                        elif grade_direction == "manual":
                            sync_status_val = "pulled"  # Leave for admin review

                # Insert grade_sync record
                gs_id = str(uuid.uuid4())
                try:
                    conn.execute(
                        """INSERT INTO educlaw_lms_grade_sync
                           (id, lms_connection_id, sync_log_id, lms_assignment_id, lms_user_id,
                            assessment_id, student_id, assessment_result_id,
                            lms_score, lms_grade, lms_submitted_at, lms_graded_at,
                            is_late, is_missing, lms_comments, sis_score,
                            is_conflict, conflict_type, sync_status,
                            created_at, created_by)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (gs_id, conn_id, log_id, lms_assignment_id, lms_user_id,
                         assessment_id, student_id, assessment_result_id,
                         lms_score,
                         grade_data.get("lms_grade", "") or "",
                         grade_data.get("lms_submitted_at", "") or "",
                         grade_data.get("lms_graded_at", "") or "",
                         int(grade_data.get("is_late", 0) or 0),
                         int(grade_data.get("is_missing", 0) or 0),
                         grade_data.get("lms_comments", "") or "",
                         sis_score,
                         is_conflict, conflict_type, sync_status_val,
                         _now_iso(), triggered_by)
                    )
                    grades_pulled += 1
                except sqlite3.IntegrityError:
                    pass

                # FERPA pull log per student
                if student_id:
                    _log_ferpa_access(
                        conn, student_id, company_id,
                        f"LMS grade pull from {lms_conn.get('display_name', 'LMS')}",
                        triggered_by
                    )

                conn.commit()

        except Exception as e:
            errors_count += 1
            error_summary.append({
                "entity_type": "assignment",
                "entity_id": am.get("lms_assignment_id", ""),
                "error_message": str(e),
            })

    # Finalize sync log
    final_status = "completed"
    if errors_count > 0 and grades_pulled > 0:
        final_status = "completed_with_errors"
    elif errors_count > 0:
        final_status = "failed"

    conn.execute(
        """UPDATE educlaw_lms_sync_log
           SET status = ?, grades_pulled = ?, grades_applied = ?,
               conflicts_flagged = ?, errors_count = ?,
               error_summary = ?, completed_at = ?
           WHERE id = ?""",
        (final_status, grades_pulled, grades_applied, conflicts_flagged,
         errors_count, json.dumps(error_summary), _now_iso(), log_id)
    )
    conn.execute(
        "UPDATE educlaw_lms_connection SET last_sync_at = ?, updated_at = ? WHERE id = ?",
        (_now_iso(), _now_iso(), conn_id)
    )
    conn.commit()

    ok({
        "sync_log_id": log_id,
        "naming_series": log_naming,
        "sync_status": final_status,
        "grades_pulled": grades_pulled,
        "grades_applied": grades_applied,
        "conflicts_flagged": conflicts_flagged,
        "errors_count": errors_count,
        "message": f"Grade pull {final_status}",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-online-gradebook
# ─────────────────────────────────────────────────────────────────────────────

def get_online_gradebook(conn, args):
    """Return unified gradebook for a section (SIS + LMS side by side)."""
    section_id = getattr(args, "section_id", None) or None
    conn_id = getattr(args, "connection_id", None) or None

    if not section_id:
        err("--section-id is required")
    if not conn_id:
        err("--connection-id is required")

    # Validate section
    section = conn.execute(
        "SELECT * FROM educlaw_section WHERE id = ?", (section_id,)
    ).fetchone()
    if not section:
        err(f"Section {section_id} not found")

    # Get assessment plan
    plan = conn.execute(
        "SELECT id FROM educlaw_assessment_plan WHERE section_id = ?", (section_id,)
    ).fetchone()
    if not plan:
        ok({"section_id": section_id, "assessments": [], "rows": [],
            "message": "No assessment plan found for section"})

    plan_id = plan[0]

    # Get assessments
    assessments = conn.execute(
        "SELECT * FROM educlaw_assessment WHERE assessment_plan_id = ? ORDER BY sort_order, due_date",
        (plan_id,)
    ).fetchall()
    assessments = [dict(a) for a in assessments]

    # Get LMS assignment mappings for this connection and section
    lms_maps = conn.execute(
        """SELECT am.assessment_id, am.lms_assignment_id, am.lms_assignment_url, am.sync_status
           FROM educlaw_lms_assignment_mapping am
           JOIN educlaw_assessment a ON a.id = am.assessment_id
           JOIN educlaw_assessment_plan ap ON ap.id = a.assessment_plan_id
           WHERE am.lms_connection_id = ? AND ap.section_id = ?""",
        (conn_id, section_id)
    ).fetchall()
    lms_map_by_assessment = {r[0]: dict(r) for r in lms_maps}

    # Get enrolled students
    enrollments = conn.execute(
        """SELECT ce.student_id, ce.is_grade_submitted,
                  st.first_name, st.last_name
           FROM educlaw_course_enrollment ce
           JOIN educlaw_student st ON st.id = ce.student_id
           WHERE ce.section_id = ? AND ce.enrollment_status IN ('enrolled','completed')
           ORDER BY st.last_name, st.first_name""",
        (section_id,)
    ).fetchall()
    enrollments = [dict(r) for r in enrollments]

    # Get all SIS results for this section
    if assessments:
        assess_ids = [a["id"] for a in assessments]
        ph = ",".join("?" * len(assess_ids))
        sis_results = conn.execute(
            f"""SELECT ar.assessment_id, ar.student_id, ar.points_earned, ar.is_exempt
                FROM educlaw_assessment_result ar
                WHERE ar.assessment_id IN ({ph})""",
            assess_ids
        ).fetchall()
        sis_by_key = {(r[0], r[1]): dict(r) for r in sis_results}
    else:
        sis_by_key = {}

    # Get most recent LMS grade_sync records
    if assessments:
        assess_ids = [a["id"] for a in assessments]
        ph = ",".join("?" * len(assess_ids))
        lms_grades = conn.execute(
            f"""SELECT gs.assessment_id, gs.student_id, gs.lms_score, gs.is_conflict,
                       gs.sync_status, gs.conflict_type
                FROM educlaw_lms_grade_sync gs
                WHERE gs.lms_connection_id = ? AND gs.assessment_id IN ({ph})
                AND gs.sync_status NOT IN ('error')
                ORDER BY gs.created_at DESC""",
            [conn_id] + assess_ids
        ).fetchall()
        # Keep only most recent per (assessment_id, student_id)
        lms_by_key = {}
        for r in lms_grades:
            key = (r[0], r[1])
            if key not in lms_by_key:
                lms_by_key[key] = dict(r)
    else:
        lms_by_key = {}

    # Build gradebook matrix
    assessment_cols = [
        {
            "assessment_id": a["id"],
            "name": a.get("name", ""),
            "max_points": a.get("max_points", "0"),
            "due_date": a.get("due_date", ""),
            "has_lms_mapping": a["id"] in lms_map_by_assessment,
            "lms_assignment_url": lms_map_by_assessment.get(a["id"], {}).get("lms_assignment_url", ""),
        }
        for a in assessments
    ]

    rows = []
    for enr in enrollments:
        student_id = enr["student_id"]
        student_name = f"{enr.get('last_name', '')}, {enr.get('first_name', '')}".strip(", ")

        grades = {}
        for a in assessments:
            assess_id = a["id"]
            sis_r = sis_by_key.get((assess_id, student_id), {})
            lms_r = lms_by_key.get((assess_id, student_id), {})
            lms_am = lms_map_by_assessment.get(assess_id, {})
            grades[assess_id] = {
                "sis_score": sis_r.get("points_earned", ""),
                "sis_exempt": int(sis_r.get("is_exempt", 0) or 0),
                "lms_score": lms_r.get("lms_score", ""),
                "is_conflict": int(lms_r.get("is_conflict", 0) or 0),
                "conflict_type": lms_r.get("conflict_type", "") or "",
                "lms_grade_sync_status": lms_r.get("sync_status", "") or "",
                "lms_assignment_url": lms_am.get("lms_assignment_url", "") or "",
            }

        rows.append({
            "student_id": student_id,
            "student_name": student_name,
            "is_grade_submitted": int(enr.get("is_grade_submitted", 0) or 0),
            "grades": grades,
        })

    ok({
        "section_id": section_id,
        "connection_id": conn_id,
        "assessments": assessment_cols,
        "rows": rows,
        "student_count": len(rows),
        "assessment_count": len(assessments),
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-grade-conflicts
# ─────────────────────────────────────────────────────────────────────────────

def list_grade_conflicts(conn, args):
    """List unresolved grade conflicts for review."""
    conn_id = getattr(args, "connection_id", None) or None
    section_id = getattr(args, "section_id", None) or None
    conflict_type_filter = getattr(args, "conflict_type", None) or None
    conflict_status_filter = getattr(args, "conflict_status", None) or None

    if not conn_id:
        err("--connection-id is required")

    where = ["gs.lms_connection_id = ?", "gs.is_conflict = 1"]
    params = [conn_id]

    if section_id:
        where.append("""EXISTS (
            SELECT 1 FROM educlaw_lms_assignment_mapping am
            JOIN educlaw_assessment a ON a.id = am.assessment_id
            JOIN educlaw_assessment_plan ap ON ap.id = a.assessment_plan_id
            WHERE am.lms_assignment_id = gs.lms_assignment_id
            AND am.lms_connection_id = gs.lms_connection_id
            AND ap.section_id = ?
        )""")
        params.append(section_id)

    if conflict_type_filter:
        if conflict_type_filter not in VALID_CONFLICT_TYPES:
            err(f"--conflict-type must be one of: {', '.join(VALID_CONFLICT_TYPES)}")
        where.append("gs.conflict_type = ?"); params.append(conflict_type_filter)

    if conflict_status_filter:
        if conflict_status_filter not in VALID_GRADE_SYNC_STATUSES:
            err(f"--conflict-status must be one of: {', '.join(VALID_GRADE_SYNC_STATUSES)}")
        where.append("gs.sync_status = ?"); params.append(conflict_status_filter)
    else:
        # Default: show unresolved conflicts (not yet applied or skipped)
        where.append("gs.sync_status IN ('conflict', 'pulled')")

    rows = conn.execute(
        f"""SELECT gs.id, gs.lms_assignment_id, gs.lms_user_id,
                   gs.assessment_id, gs.student_id,
                   gs.lms_score, gs.sis_score, gs.lms_grade,
                   gs.is_late, gs.is_missing, gs.lms_comments,
                   gs.is_conflict, gs.conflict_type, gs.sync_status,
                   gs.resolved_by, gs.resolved_at, gs.resolution,
                   gs.created_at,
                   a.name as assessment_name, a.max_points,
                   st.first_name as student_first, st.last_name as student_last
            FROM educlaw_lms_grade_sync gs
            LEFT JOIN educlaw_assessment a ON a.id = gs.assessment_id
            LEFT JOIN educlaw_student st ON st.id = gs.student_id
            WHERE {' AND '.join(where)}
            ORDER BY gs.created_at DESC""",
        params
    ).fetchall()

    conflicts = []
    for r in rows:
        d = dict(r)
        d["student_name"] = f"{d.pop('student_last', '')} {d.pop('student_first', '')}".strip()
        d["grade_sync_status"] = d.pop("sync_status")
        conflicts.append(d)

    ok({"conflicts": conflicts, "total": len(conflicts)})


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: apply-grade-resolution
# ─────────────────────────────────────────────────────────────────────────────

def resolve_grade_conflict(conn, args):
    """Resolve a grade conflict."""
    grade_sync_id = getattr(args, "grade_sync_id", None) or None
    resolution = getattr(args, "resolution", None) or None
    resolved_by = getattr(args, "resolved_by", None) or getattr(args, "user_id", None) or "system"
    new_score = getattr(args, "new_score", None) or None
    push_to_lms = getattr(args, "push_to_lms", None) or False

    if not grade_sync_id:
        err("--grade-sync-id is required")
    if not resolution or resolution not in VALID_RESOLUTIONS:
        err(f"--resolution must be one of: {', '.join(VALID_RESOLUTIONS)}")

    # Load grade sync record
    gs = conn.execute(
        "SELECT * FROM educlaw_lms_grade_sync WHERE id = ?", (grade_sync_id,)
    ).fetchone()
    if not gs:
        err(f"Grade sync record {grade_sync_id} not found")
    gs = dict(gs)

    if gs.get("sync_status") in ("applied", "skipped"):
        ok({
            "id": grade_sync_id,
            "resolution": gs.get("resolution", ""),
            "message": f"Conflict already resolved (sync_status={gs['sync_status']})",
        })

    # Load LMS connection for company_id
    lms_conn_row = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (gs["lms_connection_id"],)
    ).fetchone()
    company_id = dict(lms_conn_row)["company_id"] if lms_conn_row else ""

    now = _now_iso()
    student_id = gs.get("student_id", "")
    assessment_id = gs.get("assessment_id", "")
    section_id_for_enr = None

    # Get section_id for enrollment lookup
    if assessment_id:
        plan_row = conn.execute(
            "SELECT section_id FROM educlaw_assessment_plan WHERE id = ("
            "SELECT assessment_plan_id FROM educlaw_assessment WHERE id = ?)",
            (assessment_id,)
        ).fetchone()
        if plan_row:
            section_id_for_enr = plan_row[0]

    assessment_result_id = gs.get("assessment_result_id", "") or None
    new_sync_status = "applied"
    amendment_id = None
    message = ""

    if resolution == "sis_wins":
        # Dismiss: keep SIS score, mark grade_sync as skipped
        new_sync_status = "skipped"
        message = "SIS score retained — LMS grade dismissed"

    elif resolution == "lms_wins":
        # Apply LMS score to SIS
        lms_score = gs.get("lms_score", "")
        conflict_type = gs.get("conflict_type", "")

        if conflict_type == "submitted_grade_locked":
            # Cannot auto-apply — must use amendment workflow
            # Create a grade amendment record to signal the need
            enr = None
            if student_id and section_id_for_enr:
                enr = conn.execute(
                    """SELECT id FROM educlaw_course_enrollment
                       WHERE student_id = ? AND section_id = ?
                       AND enrollment_status IN ('enrolled','completed')
                       ORDER BY created_at DESC LIMIT 1""",
                    (student_id, section_id_for_enr)
                ).fetchone()
            if enr:
                amendment_id = str(uuid.uuid4())
                try:
                    conn.execute(
                        """INSERT INTO educlaw_grade_amendment
                           (id, course_enrollment_id, old_letter_grade, new_letter_grade,
                            old_grade_points, new_grade_points, reason,
                            amended_by, approved_by, created_at, created_by)
                           VALUES (?, ?, '', '', '0', '0', ?, ?, '', ?, ?)""",
                        (amendment_id, enr[0],
                         f"LMS grade conflict resolution: lms_score={lms_score}",
                         resolved_by, now, resolved_by)
                    )
                except sqlite3.IntegrityError:
                    pass
            new_sync_status = "applied"  # Mark as applied (amendment created)
            message = "Submitted grade requires amendment workflow — amendment record created"
        else:
            # Apply LMS score to SIS (unsubmitted grade)
            if assessment_result_id:
                # Update existing result
                conn.execute(
                    "UPDATE educlaw_assessment_result SET points_earned = ?, updated_at = ? WHERE id = ?",
                    (lms_score, now, assessment_result_id)
                )
                message = f"LMS score ({lms_score}) applied to SIS"
            else:
                # Create new result
                enr = None
                if student_id and section_id_for_enr:
                    enr = conn.execute(
                        """SELECT id FROM educlaw_course_enrollment
                           WHERE student_id = ? AND section_id = ?
                           AND enrollment_status IN ('enrolled','completed')
                           ORDER BY created_at DESC LIMIT 1""",
                        (student_id, section_id_for_enr)
                    ).fetchone()
                if enr and student_id and assessment_id:
                    new_result_id = str(uuid.uuid4())
                    try:
                        conn.execute(
                            """INSERT INTO educlaw_assessment_result
                               (id, assessment_id, student_id, course_enrollment_id,
                                points_earned, is_exempt, is_late, comments,
                                graded_by, graded_at, created_at, updated_at, created_by)
                               VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)""",
                            (new_result_id, assessment_id, student_id, enr[0],
                             lms_score,
                             int(gs.get("is_late", 0) or 0),
                             gs.get("lms_comments", "") or "",
                             "lms_conflict_resolution",
                             gs.get("lms_graded_at", "") or now,
                             now, now, resolved_by)
                        )
                        assessment_result_id = new_result_id
                    except sqlite3.IntegrityError:
                        pass
                message = f"LMS score ({lms_score}) applied to new SIS result"
            new_sync_status = "applied"

    elif resolution == "manual":
        # Admin enters new score
        if not new_score:
            err("--new-score is required for manual resolution")
        try:
            _d(new_score)  # Validate as Decimal
        except Exception:
            err("--new-score must be a valid numeric value")

        if assessment_result_id:
            conn.execute(
                "UPDATE educlaw_assessment_result SET points_earned = ?, updated_at = ? WHERE id = ?",
                (str(new_score), now, assessment_result_id)
            )
        else:
            enr = None
            if student_id and section_id_for_enr:
                enr = conn.execute(
                    """SELECT id FROM educlaw_course_enrollment
                       WHERE student_id = ? AND section_id = ?
                       AND enrollment_status IN ('enrolled','completed')
                       ORDER BY created_at DESC LIMIT 1""",
                    (student_id, section_id_for_enr)
                ).fetchone()
            if enr and student_id and assessment_id:
                new_result_id = str(uuid.uuid4())
                try:
                    conn.execute(
                        """INSERT INTO educlaw_assessment_result
                           (id, assessment_id, student_id, course_enrollment_id,
                            points_earned, is_exempt, is_late, comments,
                            graded_by, graded_at, created_at, updated_at, created_by)
                           VALUES (?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?, ?)""",
                        (new_result_id, assessment_id, student_id, enr[0],
                         str(new_score), "manual conflict resolution",
                         resolved_by, now, now, now, resolved_by)
                    )
                    assessment_result_id = new_result_id
                except sqlite3.IntegrityError:
                    pass
        new_sync_status = "applied"
        message = f"Manual score ({new_score}) applied to SIS"

    # Update grade_sync resolution metadata
    conn.execute(
        """UPDATE educlaw_lms_grade_sync
           SET sync_status = ?, resolved_by = ?, resolved_at = ?, resolution = ?,
               assessment_result_id = ?
           WHERE id = ?""",
        (new_sync_status, resolved_by, now, resolution,
         assessment_result_id, grade_sync_id)
    )
    try:
        audit(conn, SKILL, "apply-grade-resolution", "educlaw_lms_grade_sync", grade_sync_id,
              new_values={"resolution": resolution, "grade_sync_status": new_sync_status})
    except Exception:
        pass
    conn.commit()

    ok({
        "id": grade_sync_id,
        "resolution": resolution,
        "grade_sync_status": new_sync_status,
        "assessment_result_id": assessment_result_id,
        "amendment_id": amendment_id,
        "message": message or f"Grade conflict resolved: {resolution}",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: generate-oneroster-csv
# ─────────────────────────────────────────────────────────────────────────────

def export_oneroster_csv(conn, args):
    """Generate OneRoster 1.1 CSV package for a term."""
    academic_term_id = getattr(args, "academic_term_id", None) or None
    output_dir = getattr(args, "output_dir", None) or None
    company_id = getattr(args, "company_id", None) or None
    include_grades = bool(getattr(args, "include_grades", None) or False)
    conn_id = getattr(args, "connection_id", None) or None
    triggered_by = getattr(args, "user_id", None) or "system"

    if not academic_term_id:
        err("--academic-term-id is required")
    if not output_dir:
        err("--output-dir is required")
    if not company_id:
        err("--company-id is required")

    # Validate company
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Validate term
    term = conn.execute(
        "SELECT * FROM educlaw_academic_term WHERE id = ? AND company_id = ?",
        (academic_term_id, company_id)
    ).fetchone()
    if not term:
        err(f"Academic term {academic_term_id} not found for company {company_id}")
    term = dict(term)

    # If connection provided, check DPA
    if conn_id:
        lms_conn = conn.execute(
            "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
        ).fetchone()
        if lms_conn and not int(dict(lms_conn).get("has_dpa_signed", 0) or 0):
            err("E_DPA_REQUIRED: Data Processing Agreement must be signed before export")

    # Generate OneRoster CSV
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from adapters.oneroster_csv import generate_oneroster_export

    try:
        result = generate_oneroster_export(
            conn, company_id, academic_term_id, output_dir,
            include_grades=include_grades,
            term_name=term.get("name", academic_term_id[:8])
        )
    except ValueError as e:
        err(str(e))
    except Exception as e:
        err(f"OneRoster export failed: {e}")

    # Create sync log entry
    log_id = str(uuid.uuid4())
    log_naming = _next_lms_series(
        conn, "educlaw_lms_sync_log", "SYN-", company_id, use_year=True
    )
    now = _now_iso()
    effective_conn_id = conn_id or ""
    if effective_conn_id:
        conn.execute(
            """INSERT INTO educlaw_lms_sync_log
               (id, naming_series, lms_connection_id, sync_type, academic_term_id,
                triggered_by, status, sections_synced, students_synced,
                started_at, completed_at, company_id, created_at, created_by)
               VALUES (?, ?, ?, 'oneroster_export', ?, ?, 'completed', ?, ?, ?, ?, ?, ?, ?)""",
            (log_id, log_naming, effective_conn_id, academic_term_id,
             triggered_by, "completed",
             result.get("section_count", 0), result.get("student_count", 0),
             now, now, company_id, now, triggered_by)
        )

        # FERPA disclosure log per student
        try:
            # Get all students for the exported sections
            sections = conn.execute(
                "SELECT id FROM educlaw_section WHERE academic_term_id = ? AND company_id = ?",
                (academic_term_id, company_id)
            ).fetchall()
            sec_ids = [r[0] for r in sections]
            if sec_ids:
                ph = ",".join("?" * len(sec_ids))
                students_exported = conn.execute(
                    f"""SELECT DISTINCT student_id FROM educlaw_course_enrollment
                        WHERE section_id IN ({ph}) AND enrollment_status IN ('enrolled','completed')""",
                    sec_ids
                ).fetchall()
                for stu in students_exported:
                    _log_ferpa_access(
                        conn, stu[0], company_id,
                        f"OneRoster CSV export for term {term.get('name', '')}",
                        triggered_by
                    )
        except Exception:
            pass

        conn.commit()

    ok({
        "zip_path": result.get("zip_path", ""),
        "files_generated": result.get("files_generated", []),
        "student_count": result.get("student_count", 0),
        "section_count": result.get("section_count", 0),
        "sync_log_id": log_id if effective_conn_id else None,
        "message": f"OneRoster 1.1 CSV export complete: {result.get('zip_path', '')}",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: complete-lms-course
# ─────────────────────────────────────────────────────────────────────────────

def close_lms_course(conn, args):
    """Mark a course's LMS mapping as closed after grade submission."""
    section_id = getattr(args, "section_id", None) or None
    conn_id = getattr(args, "connection_id", None) or None
    triggered_by = getattr(args, "user_id", None) or "system"

    if not section_id:
        err("--section-id is required")
    if not conn_id:
        err("--connection-id is required")

    # Find active course mapping
    mapping = conn.execute(
        """SELECT * FROM educlaw_lms_course_mapping
           WHERE lms_connection_id = ? AND section_id = ? AND sync_status != 'closed'""",
        (conn_id, section_id)
    ).fetchone()
    if not mapping:
        err(f"No active LMS course mapping found for section {section_id} on connection {conn_id}")
    mapping = dict(mapping)

    # Load connection for company_id
    lms_conn = conn.execute(
        "SELECT company_id FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    company_id = lms_conn[0] if lms_conn else ""

    # Close the mapping
    conn.execute(
        "UPDATE educlaw_lms_course_mapping SET sync_status = 'closed', last_synced_at = ? WHERE id = ?",
        (_now_iso(), mapping["id"])
    )

    # Create sync log entry for closure
    log_id = str(uuid.uuid4())
    log_naming = _next_lms_series(
        conn, "educlaw_lms_sync_log", "SYN-", company_id, use_year=True
    )
    now = _now_iso()
    conn.execute(
        """INSERT INTO educlaw_lms_sync_log
           (id, naming_series, lms_connection_id, sync_type, section_id,
            triggered_by, status, started_at, completed_at,
            company_id, created_at, created_by)
           VALUES (?, ?, ?, 'roster_push', ?, ?, 'completed', ?, ?, ?, ?, ?)""",
        (log_id, log_naming, conn_id, section_id,
         triggered_by, now, now, company_id, now, triggered_by)
    )

    try:
        audit(conn, SKILL, "complete-lms-course", "educlaw_lms_course_mapping", mapping["id"],
              new_values={"sync_status": "closed"})
    except Exception:
        pass
    conn.commit()

    ok({
        "mapping_id": mapping["id"],
        "section_id": section_id,
        "connection_id": conn_id,
        "course_map_status": "closed",
        "sync_log_id": log_id,
        "message": "LMS course mapping closed. No further grade pulls will be processed for this section.",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "import-grades": pull_grades,
    "get-online-gradebook": get_online_gradebook,
    "list-grade-conflicts": list_grade_conflicts,
    "apply-grade-resolution": resolve_grade_conflict,
    "generate-oneroster-csv": export_oneroster_csv,
    "complete-lms-course": close_lms_course,
}
