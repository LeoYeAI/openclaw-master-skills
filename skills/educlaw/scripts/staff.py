"""EduClaw — staff domain module

Actions for staff: instructor profiles linked to erpclaw-hr employees,
teaching load queries.

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_json_field(value, field_name):
    if value is None:
        return []
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
        return parsed
    except (json.JSONDecodeError, TypeError):
        err(f"{field_name} must be valid JSON")


# ─────────────────────────────────────────────────────────────────────────────
# INSTRUCTOR
# ─────────────────────────────────────────────────────────────────────────────

def add_instructor(conn, args):
    employee_id = getattr(args, "employee_id", None)
    company_id = getattr(args, "company_id", None)

    if not employee_id:
        err("--employee-id is required")
    if not company_id:
        err("--company-id is required")

    # Validate employee exists in erpclaw-hr
    emp_row = conn.execute("SELECT * FROM employee WHERE id = ?", (employee_id,)).fetchone()
    if not emp_row:
        err(f"Employee {employee_id} not found. Create employee in erpclaw-hr first.")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # OHIO: check not already an instructor
    existing = conn.execute(
        "SELECT id FROM educlaw_instructor WHERE employee_id = ?", (employee_id,)
    ).fetchone()
    if existing:
        err(f"Employee {employee_id} is already registered as instructor {existing['id']}")

    naming = get_next_name(conn, "educlaw_instructor", company_id=company_id)
    instructor_id = str(uuid.uuid4())
    now = _now_iso()

    credentials = getattr(args, "credentials", None) or "[]"
    specializations = getattr(args, "specializations", None) or "[]"
    office_hours = getattr(args, "office_hours", None) or "[]"

    # Validate JSON fields
    _validate_json_field(credentials, "--credentials")
    _validate_json_field(specializations, "--specializations")
    _validate_json_field(office_hours, "--office-hours")

    try:
        conn.execute(
            """INSERT INTO educlaw_instructor
               (id, naming_series, employee_id, credentials, specializations,
                max_teaching_load_hours, office_location, office_hours, bio,
                is_active, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (instructor_id, naming, employee_id, credentials, specializations,
             int(getattr(args, "max_teaching_load_hours", None) or 0),
             getattr(args, "office_location", None) or "",
             office_hours,
             getattr(args, "bio", None) or "",
             1, company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Instructor creation failed: {e}")

    audit(conn, SKILL, "add-instructor", "educlaw_instructor", instructor_id,
          new_values={"naming_series": naming, "employee_id": employee_id})
    conn.commit()
    ok({"id": instructor_id, "naming_series": naming, "employee_id": employee_id})


def update_instructor(conn, args):
    instructor_id = getattr(args, "instructor_id", None)
    if not instructor_id:
        err("--instructor-id is required")

    row = conn.execute("SELECT * FROM educlaw_instructor WHERE id = ?", (instructor_id,)).fetchone()
    if not row:
        err(f"Instructor {instructor_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "credentials", None) is not None:
        _validate_json_field(args.credentials, "--credentials")
        updates.append("credentials = ?"); params.append(args.credentials); changed.append("credentials")
    if getattr(args, "specializations", None) is not None:
        _validate_json_field(args.specializations, "--specializations")
        updates.append("specializations = ?"); params.append(args.specializations)
        changed.append("specializations")
    if getattr(args, "max_teaching_load_hours", None) is not None:
        updates.append("max_teaching_load_hours = ?")
        params.append(int(args.max_teaching_load_hours)); changed.append("max_teaching_load_hours")
    if getattr(args, "office_location", None) is not None:
        updates.append("office_location = ?"); params.append(args.office_location)
        changed.append("office_location")
    if getattr(args, "office_hours", None) is not None:
        _validate_json_field(args.office_hours, "--office-hours")
        updates.append("office_hours = ?"); params.append(args.office_hours)
        changed.append("office_hours")
    if getattr(args, "bio", None) is not None:
        updates.append("bio = ?"); params.append(args.bio); changed.append("bio")
    if getattr(args, "is_active", None) is not None:
        updates.append("is_active = ?"); params.append(int(args.is_active)); changed.append("is_active")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(instructor_id)
    conn.execute(f"UPDATE educlaw_instructor SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-instructor", "educlaw_instructor", instructor_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": instructor_id, "updated_fields": changed})


def get_instructor(conn, args):
    instructor_id = getattr(args, "instructor_id", None)
    if not instructor_id:
        err("--instructor-id is required")

    row = conn.execute("SELECT * FROM educlaw_instructor WHERE id = ?", (instructor_id,)).fetchone()
    if not row:
        err(f"Instructor {instructor_id} not found")

    data = dict(row)

    # Parse JSON fields
    for field in ("credentials", "specializations", "office_hours"):
        try:
            if data.get(field):
                data[field] = json.loads(data[field])
        except Exception:
            data[field] = []

    # Get employee details
    emp_row = conn.execute("SELECT * FROM employee WHERE id = ?", (data["employee_id"],)).fetchone()
    if emp_row:
        data["employee"] = dict(emp_row)

    # Current sections
    current_sections = conn.execute(
        """SELECT s.id, s.naming_series, s.section_number, c.course_code, c.name as course_name,
                  c.credit_hours, at.name as term_name, s.days_of_week, s.start_time, s.end_time
           FROM educlaw_section s
           JOIN educlaw_course c ON c.id = s.course_id
           JOIN educlaw_academic_term at ON at.id = s.academic_term_id
           WHERE s.instructor_id = ? AND s.status NOT IN ('cancelled', 'closed')
           ORDER BY at.start_date DESC""",
        (instructor_id,)
    ).fetchall()
    data["current_sections"] = [dict(s) for s in current_sections]
    ok(data)


def list_instructors(conn, args):
    query = """SELECT i.* FROM educlaw_instructor i
               JOIN employee e ON e.id = i.employee_id
               WHERE 1=1"""
    params = []

    if getattr(args, "department_id", None):
        query += " AND e.department_id = ?"; params.append(args.department_id)
    if getattr(args, "is_active", None) is not None:
        query += " AND i.is_active = ?"; params.append(int(args.is_active))
    if getattr(args, "company_id", None):
        query += " AND i.company_id = ?"; params.append(args.company_id)

    query += " ORDER BY i.naming_series"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"instructors": [dict(r) for r in rows], "count": len(rows)})


def get_teaching_load(conn, args):
    instructor_id = getattr(args, "instructor_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)

    if not instructor_id:
        err("--instructor-id is required")
    if not academic_term_id:
        err("--academic-term-id is required")

    instr_row = conn.execute(
        "SELECT * FROM educlaw_instructor WHERE id = ?", (instructor_id,)
    ).fetchone()
    if not instr_row:
        err(f"Instructor {instructor_id} not found")

    instr = dict(instr_row)
    sections = conn.execute(
        """SELECT s.id, s.naming_series, s.section_number, s.current_enrollment,
                  s.max_enrollment, s.days_of_week, s.start_time, s.end_time,
                  c.course_code, c.name as course_name, c.credit_hours
           FROM educlaw_section s
           JOIN educlaw_course c ON c.id = s.course_id
           WHERE s.instructor_id = ? AND s.academic_term_id = ? AND s.status != 'cancelled'
           ORDER BY s.start_time""",
        (instructor_id, academic_term_id)
    ).fetchall()

    total_credit_hours = Decimal("0")
    sections_list = []
    for s in sections:
        sd = dict(s)
        try:
            sd["days_of_week"] = json.loads(sd["days_of_week"]) if sd.get("days_of_week") else []
        except Exception:
            sd["days_of_week"] = []
        total_credit_hours += Decimal(str(sd.get("credit_hours", "0")))
        sections_list.append(sd)

    max_load = instr["max_teaching_load_hours"]
    exceeds_limit = max_load > 0 and float(total_credit_hours) > max_load

    ok({
        "instructor_id": instructor_id,
        "naming_series": instr["naming_series"],
        "academic_term_id": academic_term_id,
        "sections": sections_list,
        "total_credit_hours": str(total_credit_hours),
        "max_teaching_load_hours": max_load,
        "exceeds_limit": exceeds_limit,
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-instructor": add_instructor,
    "update-instructor": update_instructor,
    "get-instructor": get_instructor,
    "list-instructors": list_instructors,
    "get-teaching-load": get_teaching_load,
}
