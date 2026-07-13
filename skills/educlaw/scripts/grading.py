"""EduClaw — grading domain module

Actions for grading: grading scales, assessment plans, grade calculation,
grade submission (immutable), GPA calculation, transcripts, report cards.

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _d(val, default="0"):
    """Safe Decimal conversion."""
    try:
        return Decimal(str(val)) if val not in (None, "", "None") else Decimal(default)
    except (InvalidOperation, Exception):
        return Decimal(default)


def _log_data_access_internal(conn, user_id, student_id, data_category,
                               access_type, access_reason, company_id):
    log_id = str(uuid.uuid4())
    try:
        conn.execute(
            """INSERT INTO educlaw_data_access_log
               (id, user_id, student_id, data_category, access_type, access_reason,
                is_emergency_access, ip_address, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (log_id, user_id, student_id, data_category, access_type,
             access_reason, 0, "", company_id, _now_iso(), user_id)
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# GRADING SCALE
# ─────────────────────────────────────────────────────────────────────────────

def add_grading_scale(conn, args):
    name = getattr(args, "name", None)
    company_id = getattr(args, "company_id", None)
    entries_json = getattr(args, "entries", None)

    if not name:
        err("--name is required")
    if not company_id:
        err("--company-id is required")
    if not entries_json:
        err("--entries is required (JSON array of grade entries)")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    try:
        entries = json.loads(entries_json) if isinstance(entries_json, str) else entries_json
        if not isinstance(entries, list) or not entries:
            err("--entries must be a non-empty JSON array")
    except (json.JSONDecodeError, TypeError):
        err("--entries must be valid JSON array")

    is_default = int(getattr(args, "is_default", None) or 0)

    scale_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_grading_scale
               (id, name, description, is_default, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (scale_id, name, getattr(args, "description", None) or "",
             is_default, company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Grading scale '{name}' already exists for this company")

    # If setting as default, clear other defaults
    if is_default:
        conn.execute(
            "UPDATE educlaw_grading_scale SET is_default = 0 WHERE company_id = ? AND id != ?",
            (company_id, scale_id)
        )

    # Insert entries
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        entry_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_grading_scale_entry
               (id, grading_scale_id, letter_grade, grade_points, min_percentage,
                max_percentage, description, is_passing, counts_in_gpa, sort_order,
                created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (entry_id, scale_id,
             entry.get("letter_grade", ""),
             str(_d(entry.get("grade_points", "0"))),
             str(_d(entry.get("min_percentage", "0"))),
             str(_d(entry.get("max_percentage", "0"))),
             entry.get("description", ""),
             int(entry.get("is_passing", 1)),
             int(entry.get("counts_in_gpa", 1)),
             entry.get("sort_order", i + 1),
             now, getattr(args, "user_id", None) or "")
        )

    audit(conn, SKILL, "add-grading-scale", "educlaw_grading_scale", scale_id,
          new_values={"name": name, "entry_count": len(entries)})
    conn.commit()
    ok({"id": scale_id, "name": name, "is_default": is_default, "entry_count": len(entries)})


def update_grading_scale(conn, args):
    scale_id = getattr(args, "scale_id", None)
    if not scale_id:
        err("--scale-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_grading_scale WHERE id = ?", (scale_id,)
    ).fetchone()
    if not row:
        err(f"Grading scale {scale_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "description", None) is not None:
        updates.append("description = ?"); params.append(args.description); changed.append("description")
    if getattr(args, "is_default", None) is not None:
        updates.append("is_default = ?"); params.append(int(args.is_default)); changed.append("is_default")

    if getattr(args, "is_default", None) and int(args.is_default):
        r = dict(row)
        conn.execute(
            "UPDATE educlaw_grading_scale SET is_default = 0 WHERE company_id = ? AND id != ?",
            (r["company_id"], scale_id)
        )

    # Replace entries if provided
    entries_json = getattr(args, "entries", None)
    if entries_json:
        try:
            entries = json.loads(entries_json) if isinstance(entries_json, str) else entries_json
        except Exception:
            err("--entries must be valid JSON array")

        conn.execute("DELETE FROM educlaw_grading_scale_entry WHERE grading_scale_id = ?", (scale_id,))
        now = _now_iso()
        for i, entry in enumerate(entries):
            entry_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO educlaw_grading_scale_entry
                   (id, grading_scale_id, letter_grade, grade_points, min_percentage,
                    max_percentage, description, is_passing, counts_in_gpa, sort_order,
                    created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (entry_id, scale_id,
                 entry.get("letter_grade", ""),
                 str(_d(entry.get("grade_points", "0"))),
                 str(_d(entry.get("min_percentage", "0"))),
                 str(_d(entry.get("max_percentage", "0"))),
                 entry.get("description", ""),
                 int(entry.get("is_passing", 1)),
                 int(entry.get("counts_in_gpa", 1)),
                 entry.get("sort_order", i + 1),
                 now, getattr(args, "user_id", None) or "")
            )
        changed.append("entries")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(scale_id)
    if updates[:-1]:  # Only update if there are non-timestamp changes
        conn.execute(f"UPDATE educlaw_grading_scale SET {', '.join(updates)} WHERE id = ?", params)

    audit(conn, SKILL, "update-grading-scale", "educlaw_grading_scale", scale_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": scale_id, "updated_fields": changed})


def list_grading_scales(conn, args):
    query = "SELECT * FROM educlaw_grading_scale WHERE 1=1"
    params = []

    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)
    if getattr(args, "is_default", None) is not None:
        query += " AND is_default = ?"; params.append(int(args.is_default))

    query += " ORDER BY name"
    rows = conn.execute(query, params).fetchall()
    ok({"grading_scales": [dict(r) for r in rows], "count": len(rows)})


def get_grading_scale(conn, args):
    scale_id = getattr(args, "scale_id", None)
    if not scale_id:
        err("--scale-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_grading_scale WHERE id = ?", (scale_id,)
    ).fetchone()
    if not row:
        err(f"Grading scale {scale_id} not found")

    data = dict(row)
    entries = conn.execute(
        "SELECT * FROM educlaw_grading_scale_entry WHERE grading_scale_id = ? ORDER BY sort_order",
        (scale_id,)
    ).fetchall()
    data["entries"] = [dict(e) for e in entries]
    ok(data)


# ─────────────────────────────────────────────────────────────────────────────
# ASSESSMENT PLAN
# ─────────────────────────────────────────────────────────────────────────────

def add_assessment_plan(conn, args):
    section_id = getattr(args, "section_id", None)
    grading_scale_id = getattr(args, "grading_scale_id", None)
    company_id = getattr(args, "company_id", None)
    categories_json = getattr(args, "categories", None)

    if not section_id:
        err("--section-id is required")
    if not grading_scale_id:
        err("--grading-scale-id is required")
    if not company_id:
        err("--company-id is required")
    if not categories_json:
        err("--categories is required (JSON array of {name, weight_percentage, sort_order})")

    if not conn.execute("SELECT id FROM educlaw_section WHERE id = ?", (section_id,)).fetchone():
        err(f"Section {section_id} not found")
    if not conn.execute("SELECT id FROM educlaw_grading_scale WHERE id = ?",
                        (grading_scale_id,)).fetchone():
        err(f"Grading scale {grading_scale_id} not found")

    existing = conn.execute(
        "SELECT id FROM educlaw_assessment_plan WHERE section_id = ?", (section_id,)
    ).fetchone()
    if existing:
        err(f"Assessment plan already exists for section {section_id}")

    try:
        categories = json.loads(categories_json) if isinstance(categories_json, str) else categories_json
        if not isinstance(categories, list) or not categories:
            err("--categories must be a non-empty JSON array")
    except (json.JSONDecodeError, TypeError):
        err("--categories must be valid JSON array")

    # Validate weights sum to 100
    total_weight = sum(_d(c.get("weight_percentage", 0)) for c in categories if isinstance(c, dict))
    if total_weight != Decimal("100"):
        err(f"Category weights must sum to 100% (got {total_weight}%)")

    plan_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_assessment_plan
           (id, section_id, grading_scale_id, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (plan_id, section_id, grading_scale_id, company_id, now, now,
         getattr(args, "user_id", None) or "")
    )

    for i, cat in enumerate(categories):
        if not isinstance(cat, dict):
            continue
        cat_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_assessment_category
               (id, assessment_plan_id, name, weight_percentage, sort_order, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (cat_id, plan_id, cat.get("name", f"Category {i+1}"),
             str(_d(cat.get("weight_percentage", "0"))),
             cat.get("sort_order", i + 1), now, getattr(args, "user_id", None) or "")
        )

    audit(conn, SKILL, "add-assessment-plan", "educlaw_assessment_plan", plan_id,
          new_values={"section_id": section_id, "category_count": len(categories)})
    conn.commit()
    ok({"id": plan_id, "section_id": section_id, "category_count": len(categories)})


def update_assessment_plan(conn, args):
    plan_id = getattr(args, "plan_id", None)
    if not plan_id:
        err("--plan-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_assessment_plan WHERE id = ?", (plan_id,)
    ).fetchone()
    if not row:
        err(f"Assessment plan {plan_id} not found")

    changed = []
    updates, params = [], []

    if getattr(args, "grading_scale_id", None) is not None:
        if not conn.execute("SELECT id FROM educlaw_grading_scale WHERE id = ?",
                            (args.grading_scale_id,)).fetchone():
            err(f"Grading scale {args.grading_scale_id} not found")
        updates.append("grading_scale_id = ?"); params.append(args.grading_scale_id)
        changed.append("grading_scale_id")

    categories_json = getattr(args, "categories", None)
    if categories_json:
        try:
            categories = json.loads(categories_json) if isinstance(categories_json, str) else categories_json
        except Exception:
            err("--categories must be valid JSON array")

        total_weight = sum(_d(c.get("weight_percentage", 0)) for c in categories if isinstance(c, dict))
        if total_weight != Decimal("100"):
            err(f"Category weights must sum to 100% (got {total_weight}%)")

        conn.execute(
            "DELETE FROM educlaw_assessment_category WHERE assessment_plan_id = ?", (plan_id,)
        )
        now = _now_iso()
        for i, cat in enumerate(categories):
            cat_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO educlaw_assessment_category
                   (id, assessment_plan_id, name, weight_percentage, sort_order, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (cat_id, plan_id, cat.get("name", f"Category {i+1}"),
                 str(_d(cat.get("weight_percentage", "0"))),
                 cat.get("sort_order", i + 1), now, getattr(args, "user_id", None) or "")
            )
        changed.append("categories")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(plan_id)
    if updates[:-1]:
        conn.execute(f"UPDATE educlaw_assessment_plan SET {', '.join(updates)} WHERE id = ?", params)

    audit(conn, SKILL, "update-assessment-plan", "educlaw_assessment_plan", plan_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": plan_id, "updated_fields": changed})


def get_assessment_plan(conn, args):
    plan_id = getattr(args, "plan_id", None)
    section_id = getattr(args, "section_id", None)

    if not plan_id and not section_id:
        err("--plan-id or --section-id is required")

    if plan_id:
        row = conn.execute("SELECT * FROM educlaw_assessment_plan WHERE id = ?", (plan_id,)).fetchone()
    else:
        row = conn.execute("SELECT * FROM educlaw_assessment_plan WHERE section_id = ?", (section_id,)).fetchone()

    if not row:
        err("Assessment plan not found")

    data = dict(row)
    categories = conn.execute(
        "SELECT * FROM educlaw_assessment_category WHERE assessment_plan_id = ? ORDER BY sort_order",
        (data["id"],)
    ).fetchall()
    data["categories"] = []
    for cat in categories:
        cat_data = dict(cat)
        assessments = conn.execute(
            "SELECT * FROM educlaw_assessment WHERE category_id = ? ORDER BY sort_order, due_date",
            (cat_data["id"],)
        ).fetchall()
        cat_data["assessments"] = [dict(a) for a in assessments]
        data["categories"].append(cat_data)
    ok(data)


# ─────────────────────────────────────────────────────────────────────────────
# ASSESSMENT
# ─────────────────────────────────────────────────────────────────────────────

def add_assessment(conn, args):
    plan_id = getattr(args, "plan_id", None)
    category_id = getattr(args, "category_id", None)
    name = getattr(args, "name", None)
    max_points = getattr(args, "max_points", None)

    if not plan_id:
        err("--plan-id is required")
    if not category_id:
        err("--category-id is required")
    if not name:
        err("--name is required")
    if not max_points:
        err("--max-points is required")
    if _d(max_points) <= 0:
        err("--max-points must be greater than 0")

    if not conn.execute("SELECT id FROM educlaw_assessment_plan WHERE id = ?", (plan_id,)).fetchone():
        err(f"Assessment plan {plan_id} not found")
    if not conn.execute("SELECT id FROM educlaw_assessment_category WHERE id = ?",
                        (category_id,)).fetchone():
        err(f"Assessment category {category_id} not found")

    assessment_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_assessment
           (id, assessment_plan_id, category_id, name, description, max_points,
            due_date, is_published, allows_extra_credit, sort_order,
            created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (assessment_id, plan_id, category_id, name,
         getattr(args, "description", None) or "",
         str(_d(max_points)),
         getattr(args, "due_date", None) or "",
         int(getattr(args, "is_published", None) or 0),
         int(getattr(args, "allows_extra_credit", None) or 0),
         int(getattr(args, "sort_order", None) or 0),
         now, now, getattr(args, "user_id", None) or "")
    )

    # Auto-create result stubs for all enrolled students
    plan_row = conn.execute(
        "SELECT section_id, company_id FROM educlaw_assessment_plan WHERE id = ?", (plan_id,)
    ).fetchone()
    result_count = 0
    if plan_row:
        p = dict(plan_row)
        enrolled = conn.execute(
            """SELECT id, student_id FROM educlaw_course_enrollment
               WHERE section_id = ? AND enrollment_status = 'enrolled'""",
            (p["section_id"],)
        ).fetchall()
        for enr in enrolled:
            e = dict(enr)
            result_id = str(uuid.uuid4())
            try:
                conn.execute(
                    """INSERT INTO educlaw_assessment_result
                       (id, assessment_id, student_id, course_enrollment_id,
                        points_earned, is_exempt, is_late, comments,
                        graded_by, graded_at, created_at, updated_at, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (result_id, assessment_id, e["student_id"], e["id"],
                     None, 0, 0, "", "", "", now, now, getattr(args, "user_id", None) or "")
                )
                result_count += 1
            except sqlite3.IntegrityError:
                pass

    audit(conn, SKILL, "add-assessment", "educlaw_assessment", assessment_id,
          new_values={"name": name, "plan_id": plan_id, "result_stubs_created": result_count})
    conn.commit()
    ok({"id": assessment_id, "name": name, "max_points": str(_d(max_points)),
        "result_stubs_created": result_count})


def update_assessment(conn, args):
    assessment_id = getattr(args, "assessment_id", None)
    if not assessment_id:
        err("--assessment-id is required")

    row = conn.execute("SELECT * FROM educlaw_assessment WHERE id = ?", (assessment_id,)).fetchone()
    if not row:
        err(f"Assessment {assessment_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "description", None) is not None:
        updates.append("description = ?"); params.append(args.description); changed.append("description")
    if getattr(args, "max_points", None) is not None:
        if _d(args.max_points) <= 0:
            err("--max-points must be greater than 0")
        updates.append("max_points = ?"); params.append(str(_d(args.max_points)))
        changed.append("max_points")
    if getattr(args, "due_date", None) is not None:
        updates.append("due_date = ?"); params.append(args.due_date); changed.append("due_date")
    if getattr(args, "is_published", None) is not None:
        updates.append("is_published = ?"); params.append(int(args.is_published))
        changed.append("is_published")
    if getattr(args, "allows_extra_credit", None) is not None:
        updates.append("allows_extra_credit = ?"); params.append(int(args.allows_extra_credit))
        changed.append("allows_extra_credit")
    if getattr(args, "sort_order", None) is not None:
        updates.append("sort_order = ?"); params.append(int(args.sort_order))
        changed.append("sort_order")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(assessment_id)
    conn.execute(f"UPDATE educlaw_assessment SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-assessment", "educlaw_assessment", assessment_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": assessment_id, "updated_fields": changed})


def list_assessments(conn, args):
    query = "SELECT * FROM educlaw_assessment WHERE 1=1"
    params = []

    if getattr(args, "plan_id", None):
        query += " AND assessment_plan_id = ?"; params.append(args.plan_id)
    if getattr(args, "category_id", None):
        query += " AND category_id = ?"; params.append(args.category_id)
    if getattr(args, "is_published", None) is not None:
        query += " AND is_published = ?"; params.append(int(args.is_published))

    from_date = getattr(args, "due_date_from", None)
    to_date = getattr(args, "due_date_to", None)
    if from_date:
        query += " AND due_date >= ?"; params.append(from_date)
    if to_date:
        query += " AND due_date <= ?"; params.append(to_date)

    query += " ORDER BY sort_order, due_date"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"assessments": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# GRADE ENTRY
# ─────────────────────────────────────────────────────────────────────────────

def enter_assessment_result(conn, args):
    assessment_id = getattr(args, "assessment_id", None)
    student_id = getattr(args, "student_id", None)
    points_earned = getattr(args, "points_earned", None)

    if not assessment_id:
        err("--assessment-id is required")
    if not student_id:
        err("--student-id is required")

    a_row = conn.execute("SELECT * FROM educlaw_assessment WHERE id = ?", (assessment_id,)).fetchone()
    if not a_row:
        err(f"Assessment {assessment_id} not found")
    a = dict(a_row)

    # Validate extra credit constraint
    if points_earned is not None:
        pts = _d(points_earned)
        if not a["allows_extra_credit"] and pts > _d(a["max_points"]):
            err(f"Points earned ({pts}) cannot exceed max_points ({a['max_points']}) for this assessment")

    # Find existing result
    result_row = conn.execute(
        "SELECT * FROM educlaw_assessment_result WHERE assessment_id = ? AND student_id = ?",
        (assessment_id, student_id)
    ).fetchone()

    now = _now_iso()
    graded_by = getattr(args, "graded_by", None) or getattr(args, "user_id", None) or ""
    is_exempt = int(getattr(args, "is_exempt", None) or 0)
    is_late = int(getattr(args, "is_late", None) or 0)
    comments = getattr(args, "comments", None) or ""

    if result_row:
        r = dict(result_row)
        # Check enrollment grade not already submitted
        enr_row = conn.execute(
            "SELECT is_grade_submitted FROM educlaw_course_enrollment WHERE id = ?",
            (r["course_enrollment_id"],)
        ).fetchone()
        if enr_row and dict(enr_row)["is_grade_submitted"]:
            err("Cannot modify grades after final grades have been submitted")

        conn.execute(
            """UPDATE educlaw_assessment_result
               SET points_earned = ?, is_exempt = ?, is_late = ?, comments = ?,
                   graded_by = ?, graded_at = ?, updated_at = datetime('now')
               WHERE id = ?""",
            (str(pts) if points_earned is not None else None,
             is_exempt, is_late, comments, graded_by, now, r["id"])
        )
        result_id = r["id"]
    else:
        # Need enrollment ID
        enrollment_id = getattr(args, "enrollment_id", None)
        if not enrollment_id:
            # Try to find it
            plan_row = conn.execute(
                "SELECT section_id FROM educlaw_assessment_plan WHERE id = ?",
                (a["assessment_plan_id"],)
            ).fetchone()
            if plan_row:
                enr_row = conn.execute(
                    "SELECT id FROM educlaw_course_enrollment WHERE student_id = ? AND section_id = ?",
                    (student_id, dict(plan_row)["section_id"])
                ).fetchone()
                enrollment_id = dict(enr_row)["id"] if enr_row else None
        if not enrollment_id:
            err("Could not find course enrollment for this student and assessment")

        result_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_assessment_result
               (id, assessment_id, student_id, course_enrollment_id,
                points_earned, is_exempt, is_late, comments,
                graded_by, graded_at, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (result_id, assessment_id, student_id, enrollment_id,
             str(_d(points_earned)) if points_earned is not None else None,
             is_exempt, is_late, comments, graded_by, now, now, now, graded_by)
        )

    conn.commit()
    ok({"id": result_id, "assessment_id": assessment_id, "student_id": student_id,
        "points_earned": str(_d(points_earned)) if points_earned is not None else None})


def batch_enter_results(conn, args):
    assessment_id = getattr(args, "assessment_id", None)
    results_json = getattr(args, "results", None)

    if not assessment_id:
        err("--assessment-id is required")
    if not results_json:
        err("--results is required (JSON array of {student_id, points_earned, is_exempt, comments})")

    try:
        results = json.loads(results_json) if isinstance(results_json, str) else results_json
        if not isinstance(results, list):
            err("--results must be a JSON array")
    except (json.JSONDecodeError, TypeError):
        err("--results must be valid JSON array")

    a_row = conn.execute("SELECT * FROM educlaw_assessment WHERE id = ?", (assessment_id,)).fetchone()
    if not a_row:
        err(f"Assessment {assessment_id} not found")
    a = dict(a_row)

    plan_row = conn.execute(
        "SELECT section_id FROM educlaw_assessment_plan WHERE id = ?",
        (a["assessment_plan_id"],)
    ).fetchone()
    section_id = dict(plan_row)["section_id"] if plan_row else None

    now = _now_iso()
    graded_by = getattr(args, "graded_by", None) or getattr(args, "user_id", None) or ""
    saved_count = 0
    errors = []

    for result in results:
        if not isinstance(result, dict):
            continue
        student_id = result.get("student_id")
        points_earned = result.get("points_earned")
        is_exempt = int(result.get("is_exempt", 0))
        is_late = int(result.get("is_late", 0))
        comments = result.get("comments", "")

        if not student_id:
            errors.append({"error": "student_id is required", "data": result})
            continue

        # Find enrollment
        enrollment_id = None
        if section_id:
            enr_row = conn.execute(
                "SELECT id FROM educlaw_course_enrollment WHERE student_id = ? AND section_id = ?",
                (student_id, section_id)
            ).fetchone()
            enrollment_id = dict(enr_row)["id"] if enr_row else None

        # Find existing result
        existing = conn.execute(
            "SELECT id FROM educlaw_assessment_result WHERE assessment_id = ? AND student_id = ?",
            (assessment_id, student_id)
        ).fetchone()

        pts_str = str(_d(points_earned)) if points_earned is not None else None

        try:
            if existing:
                conn.execute(
                    """UPDATE educlaw_assessment_result
                       SET points_earned = ?, is_exempt = ?, is_late = ?, comments = ?,
                           graded_by = ?, graded_at = ?, updated_at = datetime('now')
                       WHERE id = ?""",
                    (pts_str, is_exempt, is_late, comments, graded_by, now, dict(existing)["id"])
                )
            elif enrollment_id:
                result_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT INTO educlaw_assessment_result
                       (id, assessment_id, student_id, course_enrollment_id,
                        points_earned, is_exempt, is_late, comments,
                        graded_by, graded_at, created_at, updated_at, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (result_id, assessment_id, student_id, enrollment_id,
                     pts_str, is_exempt, is_late, comments, graded_by, now, now, now, graded_by)
                )
            saved_count += 1
        except Exception as e:
            errors.append({"student_id": student_id, "error": str(e)})

    conn.commit()
    ok({"assessment_id": assessment_id, "saved": saved_count, "errors": errors})


# ─────────────────────────────────────────────────────────────────────────────
# GRADE CALCULATION
# ─────────────────────────────────────────────────────────────────────────────

def _calculate_grade_for_student(conn, plan_id, student_id, enrollment_id, scale_entries):
    """Calculate weighted final grade. Returns (percentage, letter_grade, grade_points)."""
    categories = conn.execute(
        "SELECT * FROM educlaw_assessment_category WHERE assessment_plan_id = ? ORDER BY sort_order",
        (plan_id,)
    ).fetchall()

    weighted_sum = Decimal("0")
    total_weight = Decimal("0")

    for cat in categories:
        c = dict(cat)
        cat_weight = _d(c["weight_percentage"]) / Decimal("100")

        # Get all assessments in this category
        assessments = conn.execute(
            "SELECT * FROM educlaw_assessment WHERE category_id = ?", (c["id"],)
        ).fetchall()

        cat_earned = Decimal("0")
        cat_max = Decimal("0")

        for asmnt in assessments:
            a = dict(asmnt)
            result = conn.execute(
                """SELECT * FROM educlaw_assessment_result
                   WHERE assessment_id = ? AND student_id = ?""",
                (a["id"], student_id)
            ).fetchone()

            if result:
                r = dict(result)
                if r["is_exempt"]:
                    continue
                if r["points_earned"] is not None:
                    earned = _d(r["points_earned"])
                    max_pts = _d(a["max_points"])
                    cat_earned += earned
                    cat_max += max_pts
            else:
                cat_max += _d(a["max_points"])

        if cat_max > 0:
            cat_pct = (cat_earned / cat_max) * Decimal("100")
            weighted_sum += cat_pct * cat_weight
            total_weight += cat_weight

    if total_weight == 0:
        return "0", "F", "0"

    # Normalize if some categories had no graded items
    if total_weight < Decimal("1"):
        final_pct = weighted_sum / total_weight if total_weight > 0 else Decimal("0")
    else:
        final_pct = weighted_sum

    final_pct = final_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Map to letter grade
    letter = "F"
    points = "0.0"
    for entry in scale_entries:
        e = dict(entry)
        if _d(e["min_percentage"]) <= final_pct <= _d(e["max_percentage"]):
            letter = e["letter_grade"]
            points = e["grade_points"]
            break

    return str(final_pct), letter, points


def calculate_section_grade(conn, args):
    section_id = getattr(args, "section_id", None)
    student_id = getattr(args, "student_id", None)

    if not section_id:
        err("--section-id is required")

    plan_row = conn.execute(
        "SELECT * FROM educlaw_assessment_plan WHERE section_id = ?", (section_id,)
    ).fetchone()
    if not plan_row:
        err(f"No assessment plan found for section {section_id}")

    plan = dict(plan_row)
    scale_entries = conn.execute(
        """SELECT * FROM educlaw_grading_scale_entry
           WHERE grading_scale_id = ? ORDER BY sort_order""",
        (plan["grading_scale_id"],)
    ).fetchall()

    if student_id:
        enr_row = conn.execute(
            "SELECT id FROM educlaw_course_enrollment WHERE student_id = ? AND section_id = ?",
            (student_id, section_id)
        ).fetchone()
        if not enr_row:
            err(f"Student {student_id} is not enrolled in section {section_id}")
        enrollment_id = dict(enr_row)["id"]
        pct, letter, pts = _calculate_grade_for_student(
            conn, plan["id"], student_id, enrollment_id, scale_entries
        )
        ok({"student_id": student_id, "section_id": section_id,
            "percentage": pct, "letter_grade": letter, "grade_points": pts,
            "is_preview": True})
    else:
        # All enrolled students
        enrollments = conn.execute(
            """SELECT id, student_id FROM educlaw_course_enrollment
               WHERE section_id = ? AND enrollment_status = 'enrolled'""",
            (section_id,)
        ).fetchall()
        results = []
        for enr in enrollments:
            e = dict(enr)
            pct, letter, pts = _calculate_grade_for_student(
                conn, plan["id"], e["student_id"], e["id"], scale_entries
            )
            results.append({"student_id": e["student_id"], "enrollment_id": e["id"],
                            "percentage": pct, "letter_grade": letter, "grade_points": pts})
        ok({"section_id": section_id, "grades": results, "is_preview": True})


def submit_grades(conn, args):
    """Submit official final grades for all students in section. Immutable."""
    section_id = getattr(args, "section_id", None)
    submitted_by = getattr(args, "submitted_by", None) or getattr(args, "user_id", None)

    if not section_id:
        err("--section-id is required")
    if not submitted_by:
        err("--submitted-by is required")

    plan_row = conn.execute(
        "SELECT * FROM educlaw_assessment_plan WHERE section_id = ?", (section_id,)
    ).fetchone()
    if not plan_row:
        err(f"No assessment plan found for section {section_id}")

    plan = dict(plan_row)
    scale_entries = conn.execute(
        """SELECT * FROM educlaw_grading_scale_entry
           WHERE grading_scale_id = ? ORDER BY sort_order""",
        (plan["grading_scale_id"],)
    ).fetchall()

    enrollments = conn.execute(
        """SELECT * FROM educlaw_course_enrollment
           WHERE section_id = ? AND enrollment_status = 'enrolled'""",
        (section_id,)
    ).fetchall()

    now = _now_iso()
    submitted_count = 0
    company_id = None

    for enr in enrollments:
        e = dict(enr)
        if e["is_grade_submitted"]:
            continue

        company_id = e.get("company_id", "")
        pct, letter, pts = _calculate_grade_for_student(
            conn, plan["id"], e["student_id"], e["id"], scale_entries
        )

        conn.execute(
            """UPDATE educlaw_course_enrollment
               SET enrollment_status = 'completed', final_letter_grade = ?,
                   final_grade_points = ?, final_percentage = ?,
                   grade_submitted_by = ?, grade_submitted_at = ?,
                   is_grade_submitted = 1, updated_at = datetime('now')
               WHERE id = ?""",
            (letter, pts, pct, submitted_by, now, e["id"])
        )

        # Send grade_posted notification
        notif_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_notification
               (id, recipient_type, recipient_id, notification_type, title, message,
                reference_type, reference_id, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (notif_id, "student", e["student_id"], "grade_posted",
             "Grade Posted",
             f"Your final grade has been posted: {letter} ({pct}%)",
             "educlaw_course_enrollment", e["id"], company_id, now, submitted_by)
        )

        # Trigger GPA recalculation
        _calculate_gpa_internal(conn, e["student_id"])
        submitted_count += 1

    conn.commit()
    ok({"section_id": section_id, "submitted_by": submitted_by,
        "grades_submitted": submitted_count})


def amend_grade(conn, args):
    enrollment_id = getattr(args, "enrollment_id", None)
    new_letter_grade = getattr(args, "new_letter_grade", None)
    new_grade_points = getattr(args, "new_grade_points", None)
    reason = getattr(args, "reason", None)
    amended_by = getattr(args, "amended_by", None) or getattr(args, "user_id", None)

    if not enrollment_id:
        err("--enrollment-id is required")
    if not new_letter_grade:
        err("--new-letter-grade is required")
    if not reason:
        err("--reason is required")
    if not amended_by:
        err("--amended-by is required")

    row = conn.execute(
        "SELECT * FROM educlaw_course_enrollment WHERE id = ?", (enrollment_id,)
    ).fetchone()
    if not row:
        err(f"Enrollment {enrollment_id} not found")

    r = dict(row)
    if not r["is_grade_submitted"]:
        err("Grade amendments can only be made after official grade submission")

    now = _now_iso()
    amendment_id = str(uuid.uuid4())

    conn.execute(
        """INSERT INTO educlaw_grade_amendment
           (id, course_enrollment_id, old_letter_grade, new_letter_grade,
            old_grade_points, new_grade_points, reason, amended_by, approved_by,
            created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (amendment_id, enrollment_id, r["final_letter_grade"], new_letter_grade,
         r["final_grade_points"],
         str(_d(new_grade_points)) if new_grade_points else r["final_grade_points"],
         reason, amended_by,
         getattr(args, "approved_by", None) or "",
         now, amended_by)
    )

    conn.execute(
        """UPDATE educlaw_course_enrollment
           SET final_letter_grade = ?, final_grade_points = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (new_letter_grade,
         str(_d(new_grade_points)) if new_grade_points else r["final_grade_points"],
         enrollment_id)
    )

    # Recalculate GPA
    _calculate_gpa_internal(conn, r["student_id"])

    audit(conn, SKILL, "amend-grade", "educlaw_grade_amendment", amendment_id,
          new_values={"old_grade": r["final_letter_grade"], "new_grade": new_letter_grade})
    conn.commit()
    ok({"amendment_id": amendment_id, "enrollment_id": enrollment_id,
        "old_letter_grade": r["final_letter_grade"], "new_letter_grade": new_letter_grade})


def _calculate_gpa_internal(conn, student_id):
    """Recalculate cumulative GPA and total credits for student."""
    enrollments = conn.execute(
        """SELECT ce.final_grade_points, ce.final_letter_grade, c.credit_hours, ce.grade_type
           FROM educlaw_course_enrollment ce
           JOIN educlaw_section s ON s.id = ce.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           WHERE ce.student_id = ? AND ce.is_grade_submitted = 1
           AND ce.enrollment_status = 'completed'""",
        (student_id,)
    ).fetchall()

    # Grades that don't count in GPA
    exclude_grades = {"W", "I", "P", "NP", "AU", ""}

    total_points = Decimal("0")
    total_credits = Decimal("0")
    gpa_credits = Decimal("0")
    all_credits = Decimal("0")

    for enr in enrollments:
        e = dict(enr)
        credits = _d(e["credit_hours"])
        all_credits += credits
        if e["final_letter_grade"] not in exclude_grades and e["grade_type"] != "audit":
            grade_pts = _d(e["final_grade_points"])
            total_points += grade_pts * credits
            gpa_credits += credits

    cumulative_gpa = "0.00"
    if gpa_credits > 0:
        raw_gpa = total_points / gpa_credits
        cumulative_gpa = str(raw_gpa.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Determine academic standing
    gpa_val = _d(cumulative_gpa)
    if gpa_val >= Decimal("3.5"):
        standing = "deans_list"
    elif gpa_val >= Decimal("3.0"):
        standing = "honor_roll"
    elif gpa_val < Decimal("2.0") and gpa_credits > 0:
        standing = "probation"
    else:
        standing = "good"

    conn.execute(
        """UPDATE educlaw_student
           SET cumulative_gpa = ?, total_credits_earned = ?,
               academic_standing = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (cumulative_gpa, str(all_credits), standing, student_id)
    )


def calculate_gpa(conn, args):
    student_id = getattr(args, "student_id", None)
    if not student_id:
        err("--student-id is required")

    row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not row:
        err(f"Student {student_id} not found")

    _calculate_gpa_internal(conn, student_id)
    conn.commit()

    updated = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    u = dict(updated)
    ok({"student_id": student_id, "cumulative_gpa": u["cumulative_gpa"],
        "total_credits_earned": u["total_credits_earned"],
        "academic_standing": u["academic_standing"]})


def generate_transcript(conn, args):
    student_id = getattr(args, "student_id", None)
    company_id = getattr(args, "company_id", None)
    user_id = getattr(args, "user_id", None) or "system"

    if not student_id:
        err("--student-id is required")
    if not company_id:
        err("--company-id is required")

    student_row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not student_row:
        err(f"Student {student_id} not found")

    student = dict(student_row)
    student.pop("ssn_encrypted", None)

    enrollments = conn.execute(
        """SELECT ce.*, s.section_number, s.naming_series as section_series,
                  c.course_code, c.name as course_name, c.credit_hours,
                  at.name as term_name, at.start_date, at.end_date,
                  ay.name as year_name
           FROM educlaw_course_enrollment ce
           JOIN educlaw_section s ON s.id = ce.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           JOIN educlaw_academic_term at ON at.id = s.academic_term_id
           JOIN educlaw_academic_year ay ON ay.id = at.academic_year_id
           WHERE ce.student_id = ? AND ce.is_grade_submitted = 1
           ORDER BY at.start_date, c.course_code""",
        (student_id,)
    ).fetchall()

    # Group by term
    terms_dict = {}
    for enr in enrollments:
        e = dict(enr)
        term_key = e["term_name"]
        if term_key not in terms_dict:
            terms_dict[term_key] = {
                "term_name": e["term_name"],
                "year_name": e["year_name"],
                "start_date": e["start_date"],
                "courses": [],
                "term_gpa": "0.00",
                "term_credits": "0"
            }
        terms_dict[term_key]["courses"].append({
            "course_code": e["course_code"],
            "course_name": e["course_name"],
            "credit_hours": e["credit_hours"],
            "final_letter_grade": e["final_letter_grade"],
            "final_grade_points": e["final_grade_points"],
            "final_percentage": e["final_percentage"],
            "grade_type": e["grade_type"],
        })

    # Calculate term GPAs
    for term_key in terms_dict:
        t = terms_dict[term_key]
        term_pts = Decimal("0")
        term_cr = Decimal("0")
        all_cr = Decimal("0")
        exclude_grades = {"W", "I", "P", "NP", "AU", ""}
        for course in t["courses"]:
            cr = _d(course["credit_hours"])
            all_cr += cr
            if course["final_letter_grade"] not in exclude_grades and course["grade_type"] != "audit":
                term_pts += _d(course["final_grade_points"]) * cr
                term_cr += cr
        if term_cr > 0:
            t["term_gpa"] = str((term_pts / term_cr).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        t["term_credits"] = str(all_cr)

    # Log FERPA data access
    _log_data_access_internal(conn, user_id, student_id, "grades", "view",
                               "Transcript generation", company_id)
    conn.commit()

    ok({
        "student": {
            "id": student["id"],
            "naming_series": student["naming_series"],
            "full_name": student["full_name"],
            "cumulative_gpa": student["cumulative_gpa"],
            "total_credits_earned": student["total_credits_earned"],
            "academic_standing": student["academic_standing"],
        },
        "terms": sorted(terms_dict.values(), key=lambda x: x["start_date"]),
        "generated_at": _now_iso(),
    })


def generate_report_card(conn, args):
    student_id = getattr(args, "student_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)

    if not student_id:
        err("--student-id is required")
    if not academic_term_id:
        err("--academic-term-id is required")

    student_row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not student_row:
        err(f"Student {student_id} not found")

    student = dict(student_row)

    enrollments = conn.execute(
        """SELECT ce.*, c.course_code, c.name as course_name, c.credit_hours,
                  s.section_number
           FROM educlaw_course_enrollment ce
           JOIN educlaw_section s ON s.id = ce.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           WHERE ce.student_id = ? AND s.academic_term_id = ?
           ORDER BY c.course_code""",
        (student_id, academic_term_id)
    ).fetchall()

    # Attendance summary for term
    attendance_summary = conn.execute(
        """SELECT
             COUNT(*) as total_days,
             SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) as present,
             SUM(CASE WHEN attendance_status = 'absent' THEN 1 ELSE 0 END) as absent,
             SUM(CASE WHEN attendance_status = 'tardy' THEN 1 ELSE 0 END) as tardy,
             SUM(CASE WHEN attendance_status = 'excused' THEN 1 ELSE 0 END) as excused
           FROM educlaw_student_attendance sa
           JOIN educlaw_section s ON s.id = sa.section_id
           WHERE sa.student_id = ? AND s.academic_term_id = ?""",
        (student_id, academic_term_id)
    ).fetchone()

    ok({
        "student": {
            "id": student["id"],
            "full_name": student["full_name"],
            "grade_level": student["grade_level"],
            "academic_standing": student["academic_standing"],
        },
        "academic_term_id": academic_term_id,
        "courses": [dict(e) for e in enrollments],
        "attendance": dict(attendance_summary) if attendance_summary else {},
        "generated_at": _now_iso(),
    })


def list_grades(conn, args):
    query = "SELECT * FROM educlaw_course_enrollment WHERE 1=1"
    params = []

    if getattr(args, "student_id", None):
        query += " AND student_id = ?"; params.append(args.student_id)
    if getattr(args, "section_id", None):
        query += " AND section_id = ?"; params.append(args.section_id)
    if getattr(args, "academic_term_id", None):
        query += """ AND section_id IN
                     (SELECT id FROM educlaw_section WHERE academic_term_id = ?)"""
        params.append(args.academic_term_id)
    if getattr(args, "is_grade_submitted", None) is not None:
        query += " AND is_grade_submitted = ?"; params.append(int(args.is_grade_submitted))

    query += " ORDER BY is_grade_submitted, student_id"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"grades": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-grading-scale": add_grading_scale,
    "update-grading-scale": update_grading_scale,
    "list-grading-scales": list_grading_scales,
    "get-grading-scale": get_grading_scale,
    "add-assessment-plan": add_assessment_plan,
    "update-assessment-plan": update_assessment_plan,
    "get-assessment-plan": get_assessment_plan,
    "add-assessment": add_assessment,
    "update-assessment": update_assessment,
    "list-assessments": list_assessments,
    "record-assessment-result": enter_assessment_result,
    "record-batch-results": batch_enter_results,
    "generate-section-grade": calculate_section_grade,
    "submit-grades": submit_grades,
    "update-grade": amend_grade,
    "generate-gpa": calculate_gpa,
    "generate-transcript": generate_transcript,
    "generate-report-card": generate_report_card,
    "list-grades": list_grades,
}
