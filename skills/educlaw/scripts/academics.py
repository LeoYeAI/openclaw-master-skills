"""EduClaw — academics domain module

Actions for the academics domain: academic years, terms, rooms,
programs, courses, sections, and institutional calendar.

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
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_TERM_TYPES = ("semester", "quarter", "trimester", "summer", "custom")
VALID_TERM_STATUSES = ("setup", "enrollment_open", "active", "grades_open", "grades_finalized", "closed")
VALID_ROOM_TYPES = ("classroom", "lab", "auditorium", "gym", "library", "office")
VALID_PROGRAM_TYPES = ("k12", "associate", "bachelor", "master", "doctoral", "certificate", "diploma")
VALID_COURSE_TYPES = ("lecture", "lab", "seminar", "independent_study", "internship", "online")
VALID_SECTION_STATUSES = ("draft", "scheduled", "open", "closed", "cancelled")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _validate_json_field(value, field_name):
    """Return parsed JSON list/dict or raise err."""
    if value is None:
        return []
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
        if not isinstance(parsed, (list, dict)):
            err(f"{field_name} must be a JSON array or object")
        return parsed
    except (json.JSONDecodeError, TypeError):
        err(f"{field_name} must be valid JSON")


def _times_overlap(start1, end1, start2, end2):
    """Return True if two time ranges overlap."""
    if not start1 or not end1 or not start2 or not end2:
        return False
    return start1 < end2 and end1 > start2


def _days_overlap(days1_json, days2_json):
    """Return True if two day-of-week JSON arrays share any day."""
    try:
        d1 = set(json.loads(days1_json) if isinstance(days1_json, str) else (days1_json or []))
        d2 = set(json.loads(days2_json) if isinstance(days2_json, str) else (days2_json or []))
        return bool(d1 & d2)
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# ACADEMIC YEAR
# ─────────────────────────────────────────────────────────────────────────────

def add_academic_year(conn, args):
    name = getattr(args, "name", None)
    company_id = getattr(args, "company_id", None)
    start_date = getattr(args, "start_date", None)
    end_date = getattr(args, "end_date", None)

    if not name:
        err("--name is required")
    if not company_id:
        err("--company-id is required")
    if not start_date:
        err("--start-date is required")
    if not end_date:
        err("--end-date is required")
    if start_date >= end_date:
        err("start_date must be before end_date")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Check date overlap with existing years
    existing = conn.execute(
        "SELECT id, name FROM educlaw_academic_year WHERE company_id = ? AND NOT (end_date <= ? OR start_date >= ?)",
        (company_id, start_date, end_date)
    ).fetchone()
    if existing:
        err(f"Dates overlap with existing academic year '{existing['name']}'")

    year_id = str(uuid.uuid4())
    is_active = int(getattr(args, "is_active", None) or 1)
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_academic_year
               (id, name, start_date, end_date, is_active, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (year_id, name, start_date, end_date, is_active, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Academic year creation failed: {e}")

    audit(conn, SKILL, "add-academic-year", "educlaw_academic_year", year_id,
          new_values={"name": name, "start_date": start_date, "end_date": end_date})
    conn.commit()
    ok({"id": year_id, "name": name, "start_date": start_date, "end_date": end_date})


def update_academic_year(conn, args):
    year_id = getattr(args, "year_id", None)
    if not year_id:
        err("--year-id is required")

    row = conn.execute("SELECT * FROM educlaw_academic_year WHERE id = ?", (year_id,)).fetchone()
    if not row:
        err(f"Academic year {year_id} not found")

    r = dict(row)
    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "start_date", None) is not None:
        updates.append("start_date = ?"); params.append(args.start_date); changed.append("start_date")
    if getattr(args, "end_date", None) is not None:
        updates.append("end_date = ?"); params.append(args.end_date); changed.append("end_date")
    if getattr(args, "is_active", None) is not None:
        updates.append("is_active = ?"); params.append(int(args.is_active)); changed.append("is_active")

    if not changed:
        err("No fields to update")

    start = getattr(args, "start_date", None) or r["start_date"]
    end = getattr(args, "end_date", None) or r["end_date"]
    if start >= end:
        err("start_date must be before end_date")

    updates.append("updated_at = datetime('now')")
    params.append(year_id)
    conn.execute(f"UPDATE educlaw_academic_year SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-academic-year", "educlaw_academic_year", year_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": year_id, "updated_fields": changed})


def get_academic_year(conn, args):
    year_id = getattr(args, "year_id", None)
    if not year_id:
        err("--year-id is required")

    row = conn.execute("SELECT * FROM educlaw_academic_year WHERE id = ?", (year_id,)).fetchone()
    if not row:
        err(f"Academic year {year_id} not found")

    data = dict(row)
    terms = conn.execute(
        "SELECT * FROM educlaw_academic_term WHERE academic_year_id = ? ORDER BY start_date",
        (year_id,)
    ).fetchall()
    data["terms"] = [dict(t) for t in terms]
    ok(data)


def list_academic_years(conn, args):
    query = "SELECT * FROM educlaw_academic_year WHERE 1=1"
    params = []

    company_id = getattr(args, "company_id", None)
    if company_id:
        query += " AND company_id = ?"; params.append(company_id)

    is_active = getattr(args, "is_active", None)
    if is_active is not None:
        query += " AND is_active = ?"; params.append(int(is_active))

    query += " ORDER BY start_date DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"academic_years": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# ACADEMIC TERM
# ─────────────────────────────────────────────────────────────────────────────

def add_academic_term(conn, args):
    name = getattr(args, "name", None)
    term_type = getattr(args, "term_type", None)
    academic_year_id = getattr(args, "academic_year_id", None)
    start_date = getattr(args, "start_date", None)
    end_date = getattr(args, "end_date", None)
    company_id = getattr(args, "company_id", None)

    if not name:
        err("--name is required")
    if not term_type:
        err("--term-type is required")
    if term_type not in VALID_TERM_TYPES:
        err(f"--term-type must be one of: {', '.join(VALID_TERM_TYPES)}")
    if not academic_year_id:
        err("--academic-year-id is required")
    if not start_date:
        err("--start-date is required")
    if not end_date:
        err("--end-date is required")
    if not company_id:
        err("--company-id is required")
    if start_date >= end_date:
        err("start_date must be before end_date")

    year_row = conn.execute(
        "SELECT * FROM educlaw_academic_year WHERE id = ?", (academic_year_id,)
    ).fetchone()
    if not year_row:
        err(f"Academic year {academic_year_id} not found")

    year = dict(year_row)
    if start_date < year["start_date"] or end_date > year["end_date"]:
        err(f"Term dates must fall within academic year ({year['start_date']} to {year['end_date']})")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    term_id = str(uuid.uuid4())
    enrollment_start = getattr(args, "enrollment_start_date", None) or ""
    enrollment_end = getattr(args, "enrollment_end_date", None) or ""
    grade_deadline = getattr(args, "grade_submission_deadline", None) or ""
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_academic_term
               (id, name, term_type, academic_year_id, start_date, end_date,
                enrollment_start_date, enrollment_end_date, grade_submission_deadline,
                status, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (term_id, name, term_type, academic_year_id, start_date, end_date,
             enrollment_start, enrollment_end, grade_deadline,
             "setup", company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Academic term creation failed: {e}")

    audit(conn, SKILL, "add-academic-term", "educlaw_academic_term", term_id,
          new_values={"name": name, "term_type": term_type, "academic_year_id": academic_year_id})
    conn.commit()
    ok({"id": term_id, "name": name, "term_type": term_type, "academic_year_id": academic_year_id,
        "start_date": start_date, "end_date": end_date})


def update_academic_term(conn, args):
    term_id = getattr(args, "term_id", None)
    if not term_id:
        err("--term-id is required")

    row = conn.execute("SELECT * FROM educlaw_academic_term WHERE id = ?", (term_id,)).fetchone()
    if not row:
        err(f"Academic term {term_id} not found")

    r = dict(row)
    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "term_type", None) is not None:
        if args.term_type not in VALID_TERM_TYPES:
            err(f"--term-type must be one of: {', '.join(VALID_TERM_TYPES)}")
        updates.append("term_type = ?"); params.append(args.term_type); changed.append("term_type")
    if getattr(args, "start_date", None) is not None:
        updates.append("start_date = ?"); params.append(args.start_date); changed.append("start_date")
    if getattr(args, "end_date", None) is not None:
        updates.append("end_date = ?"); params.append(args.end_date); changed.append("end_date")
    if getattr(args, "enrollment_start_date", None) is not None:
        updates.append("enrollment_start_date = ?"); params.append(args.enrollment_start_date)
        changed.append("enrollment_start_date")
    if getattr(args, "enrollment_end_date", None) is not None:
        updates.append("enrollment_end_date = ?"); params.append(args.enrollment_end_date)
        changed.append("enrollment_end_date")
    if getattr(args, "grade_submission_deadline", None) is not None:
        updates.append("grade_submission_deadline = ?"); params.append(args.grade_submission_deadline)
        changed.append("grade_submission_deadline")
    if getattr(args, "term_status", None) is not None:
        new_status = args.term_status
        if new_status not in VALID_TERM_STATUSES:
            err(f"--term-status must be one of: {', '.join(VALID_TERM_STATUSES)}")
        updates.append("status = ?"); params.append(new_status); changed.append("status")

    if not changed:
        err("No fields to update")

    start = getattr(args, "start_date", None) or r["start_date"]
    end = getattr(args, "end_date", None) or r["end_date"]
    if start >= end:
        err("start_date must be before end_date")

    updates.append("updated_at = datetime('now')")
    params.append(term_id)
    conn.execute(f"UPDATE educlaw_academic_term SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-academic-term", "educlaw_academic_term", term_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": term_id, "updated_fields": changed})


def get_academic_term(conn, args):
    term_id = getattr(args, "term_id", None)
    if not term_id:
        err("--term-id is required")

    row = conn.execute("SELECT * FROM educlaw_academic_term WHERE id = ?", (term_id,)).fetchone()
    if not row:
        err(f"Academic term {term_id} not found")

    data = dict(row)
    section_count = conn.execute(
        "SELECT COUNT(*) FROM educlaw_section WHERE academic_term_id = ? AND status != 'cancelled'",
        (term_id,)
    ).fetchone()[0]
    data["section_count"] = section_count
    ok(data)


def list_academic_terms(conn, args):
    query = "SELECT * FROM educlaw_academic_term WHERE 1=1"
    params = []

    if getattr(args, "academic_year_id", None):
        query += " AND academic_year_id = ?"; params.append(args.academic_year_id)
    if getattr(args, "term_status", None):
        query += " AND status = ?"; params.append(args.term_status)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY start_date"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"academic_terms": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# ROOM
# ─────────────────────────────────────────────────────────────────────────────

def add_room(conn, args):
    room_number = getattr(args, "room_number", None)
    company_id = getattr(args, "company_id", None)
    capacity = getattr(args, "capacity", None)

    if not room_number:
        err("--room-number is required")
    if not company_id:
        err("--company-id is required")
    if not capacity:
        err("--capacity is required")
    if int(capacity) <= 0:
        err("--capacity must be greater than 0")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    building = getattr(args, "building", None) or ""
    room_type = getattr(args, "room_type", None) or "classroom"
    if room_type not in VALID_ROOM_TYPES:
        err(f"--room-type must be one of: {', '.join(VALID_ROOM_TYPES)}")

    facilities_raw = getattr(args, "facilities", None)
    facilities = "[]"
    if facilities_raw:
        _validate_json_field(facilities_raw, "--facilities")
        facilities = facilities_raw

    room_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_room
               (id, room_number, building, capacity, room_type, facilities, is_active, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (room_id, room_number, building, int(capacity), room_type, facilities, 1,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Room already exists: {e}")

    audit(conn, SKILL, "add-room", "educlaw_room", room_id,
          new_values={"room_number": room_number, "building": building})
    conn.commit()
    ok({"id": room_id, "room_number": room_number, "building": building, "capacity": int(capacity)})


def update_room(conn, args):
    room_id = getattr(args, "room_id", None)
    if not room_id:
        err("--room-id is required")

    row = conn.execute("SELECT * FROM educlaw_room WHERE id = ?", (room_id,)).fetchone()
    if not row:
        err(f"Room {room_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "room_number", None) is not None:
        updates.append("room_number = ?"); params.append(args.room_number); changed.append("room_number")
    if getattr(args, "building", None) is not None:
        updates.append("building = ?"); params.append(args.building); changed.append("building")
    if getattr(args, "capacity", None) is not None:
        if int(args.capacity) <= 0:
            err("--capacity must be greater than 0")
        updates.append("capacity = ?"); params.append(int(args.capacity)); changed.append("capacity")
    if getattr(args, "room_type", None) is not None:
        if args.room_type not in VALID_ROOM_TYPES:
            err(f"--room-type must be one of: {', '.join(VALID_ROOM_TYPES)}")
        updates.append("room_type = ?"); params.append(args.room_type); changed.append("room_type")
    if getattr(args, "facilities", None) is not None:
        _validate_json_field(args.facilities, "--facilities")
        updates.append("facilities = ?"); params.append(args.facilities); changed.append("facilities")
    if getattr(args, "is_active", None) is not None:
        updates.append("is_active = ?"); params.append(int(args.is_active)); changed.append("is_active")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(room_id)
    conn.execute(f"UPDATE educlaw_room SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-room", "educlaw_room", room_id, new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": room_id, "updated_fields": changed})


def list_rooms(conn, args):
    query = "SELECT * FROM educlaw_room WHERE 1=1"
    params = []

    if getattr(args, "room_type", None):
        query += " AND room_type = ?"; params.append(args.room_type)
    if getattr(args, "building", None):
        query += " AND building = ?"; params.append(args.building)
    if getattr(args, "is_active", None) is not None:
        query += " AND is_active = ?"; params.append(int(args.is_active))
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY building, room_number"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["facilities"] = _validate_json_field(d.get("facilities"), "facilities")
        result.append(d)
    ok({"rooms": result, "count": len(result)})


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAM
# ─────────────────────────────────────────────────────────────────────────────

def add_program(conn, args):
    code = getattr(args, "code", None)
    name = getattr(args, "name", None)
    program_type = getattr(args, "program_type", None)
    company_id = getattr(args, "company_id", None)

    if not code:
        err("--code is required")
    if not name:
        err("--name is required")
    if not program_type:
        err("--program-type is required")
    if program_type not in VALID_PROGRAM_TYPES:
        err(f"--program-type must be one of: {', '.join(VALID_PROGRAM_TYPES)}")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    dept_id = getattr(args, "department_id", None)
    if dept_id:
        if not conn.execute("SELECT id FROM department WHERE id = ?", (dept_id,)).fetchone():
            err(f"Department {dept_id} not found")

    credits_required = str(to_decimal(getattr(args, "total_credits_required", None) or "0"))
    duration = int(getattr(args, "duration_years", None) or 0)

    prog_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_program
               (id, code, name, description, program_type, department_id,
                total_credits_required, duration_years, is_active, company_id,
                created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (prog_id, code, name, getattr(args, "description", None) or "", program_type,
             dept_id, credits_required, duration, 1, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Program code '{code}' already exists for this company")

    audit(conn, SKILL, "add-program", "educlaw_program", prog_id,
          new_values={"code": code, "name": name, "program_type": program_type})
    conn.commit()
    ok({"id": prog_id, "code": code, "name": name, "program_type": program_type})


def update_program(conn, args):
    program_id = getattr(args, "program_id", None)
    if not program_id:
        err("--program-id is required")

    row = conn.execute("SELECT * FROM educlaw_program WHERE id = ?", (program_id,)).fetchone()
    if not row:
        err(f"Program {program_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "description", None) is not None:
        updates.append("description = ?"); params.append(args.description); changed.append("description")
    if getattr(args, "program_type", None) is not None:
        if args.program_type not in VALID_PROGRAM_TYPES:
            err(f"--program-type must be one of: {', '.join(VALID_PROGRAM_TYPES)}")
        updates.append("program_type = ?"); params.append(args.program_type); changed.append("program_type")
    if getattr(args, "department_id", None) is not None:
        if not conn.execute("SELECT id FROM department WHERE id = ?", (args.department_id,)).fetchone():
            err(f"Department {args.department_id} not found")
        updates.append("department_id = ?"); params.append(args.department_id); changed.append("department_id")
    if getattr(args, "total_credits_required", None) is not None:
        updates.append("total_credits_required = ?")
        params.append(str(to_decimal(args.total_credits_required))); changed.append("total_credits_required")
    if getattr(args, "duration_years", None) is not None:
        updates.append("duration_years = ?"); params.append(int(args.duration_years)); changed.append("duration_years")
    if getattr(args, "is_active", None) is not None:
        updates.append("is_active = ?"); params.append(int(args.is_active)); changed.append("is_active")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(program_id)
    conn.execute(f"UPDATE educlaw_program SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-program", "educlaw_program", program_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": program_id, "updated_fields": changed})


def get_program(conn, args):
    program_id = getattr(args, "program_id", None)
    if not program_id:
        err("--program-id is required")

    row = conn.execute("SELECT * FROM educlaw_program WHERE id = ?", (program_id,)).fetchone()
    if not row:
        err(f"Program {program_id} not found")

    data = dict(row)
    # Requirements with course info
    reqs = conn.execute(
        """SELECT pr.*, c.course_code, c.name as course_name, c.credit_hours
           FROM educlaw_program_requirement pr
           JOIN educlaw_course c ON c.id = pr.course_id
           WHERE pr.program_id = ?""",
        (program_id,)
    ).fetchall()
    data["requirements"] = [dict(r) for r in reqs]
    ok(data)


def list_programs(conn, args):
    query = "SELECT * FROM educlaw_program WHERE 1=1"
    params = []

    if getattr(args, "program_type", None):
        query += " AND program_type = ?"; params.append(args.program_type)
    if getattr(args, "department_id", None):
        query += " AND department_id = ?"; params.append(args.department_id)
    if getattr(args, "is_active", None) is not None:
        query += " AND is_active = ?"; params.append(int(args.is_active))
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY name"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"programs": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# COURSE
# ─────────────────────────────────────────────────────────────────────────────

def add_course(conn, args):
    course_code = getattr(args, "course_code", None)
    name = getattr(args, "name", None)
    company_id = getattr(args, "company_id", None)
    credit_hours = getattr(args, "credit_hours", None)

    if not course_code:
        err("--course-code is required")
    if not name:
        err("--name is required")
    if not company_id:
        err("--company-id is required")
    if not credit_hours:
        err("--credit-hours is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    dept_id = getattr(args, "department_id", None)
    if dept_id:
        if not conn.execute("SELECT id FROM department WHERE id = ?", (dept_id,)).fetchone():
            err(f"Department {dept_id} not found")

    course_type = getattr(args, "course_type", None) or "lecture"
    if course_type not in VALID_COURSE_TYPES:
        err(f"--course-type must be one of: {', '.join(VALID_COURSE_TYPES)}")

    credit_val = str(to_decimal(credit_hours))
    max_enrollment = int(getattr(args, "max_enrollment", None) or 0)

    course_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_course
               (id, course_code, name, description, credit_hours, department_id,
                course_type, grade_level, max_enrollment, is_active, company_id,
                created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (course_id, course_code, name, getattr(args, "description", None) or "",
             credit_val, dept_id, course_type, getattr(args, "grade_level", None) or "",
             max_enrollment, 1, company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Course code '{course_code}' already exists for this company")

    # Optional prerequisites
    prereqs_json = getattr(args, "prerequisites", None)
    if prereqs_json:
        prereqs = _validate_json_field(prereqs_json, "--prerequisites")
        if isinstance(prereqs, list):
            for prereq in prereqs:
                prereq_course_id = prereq.get("course_id") if isinstance(prereq, dict) else prereq
                if prereq_course_id == course_id:
                    err("Course cannot be its own prerequisite")
                if not conn.execute("SELECT id FROM educlaw_course WHERE id = ?", (prereq_course_id,)).fetchone():
                    err(f"Prerequisite course {prereq_course_id} not found")
                prereq_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT OR IGNORE INTO educlaw_course_prerequisite
                       (id, course_id, prerequisite_course_id, min_grade, is_corequisite, created_at, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (prereq_id, course_id, prereq_course_id,
                     prereq.get("min_grade", "") if isinstance(prereq, dict) else "",
                     int(prereq.get("is_corequisite", 0)) if isinstance(prereq, dict) else 0,
                     now, getattr(args, "user_id", None) or "")
                )

    audit(conn, SKILL, "add-course", "educlaw_course", course_id,
          new_values={"course_code": course_code, "name": name})
    conn.commit()
    ok({"id": course_id, "course_code": course_code, "name": name, "credit_hours": credit_val})


def update_course(conn, args):
    course_id = getattr(args, "course_id", None)
    if not course_id:
        err("--course-id is required")

    row = conn.execute("SELECT * FROM educlaw_course WHERE id = ?", (course_id,)).fetchone()
    if not row:
        err(f"Course {course_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "description", None) is not None:
        updates.append("description = ?"); params.append(args.description); changed.append("description")
    if getattr(args, "credit_hours", None) is not None:
        updates.append("credit_hours = ?")
        params.append(str(to_decimal(args.credit_hours))); changed.append("credit_hours")
    if getattr(args, "course_type", None) is not None:
        if args.course_type not in VALID_COURSE_TYPES:
            err(f"--course-type must be one of: {', '.join(VALID_COURSE_TYPES)}")
        updates.append("course_type = ?"); params.append(args.course_type); changed.append("course_type")
    if getattr(args, "grade_level", None) is not None:
        updates.append("grade_level = ?"); params.append(args.grade_level); changed.append("grade_level")
    if getattr(args, "max_enrollment", None) is not None:
        updates.append("max_enrollment = ?"); params.append(int(args.max_enrollment)); changed.append("max_enrollment")
    if getattr(args, "is_active", None) is not None:
        updates.append("is_active = ?"); params.append(int(args.is_active)); changed.append("is_active")
    if getattr(args, "department_id", None) is not None:
        if not conn.execute("SELECT id FROM department WHERE id = ?", (args.department_id,)).fetchone():
            err(f"Department {args.department_id} not found")
        updates.append("department_id = ?"); params.append(args.department_id); changed.append("department_id")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(course_id)
    conn.execute(f"UPDATE educlaw_course SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-course", "educlaw_course", course_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": course_id, "updated_fields": changed})


def get_course(conn, args):
    course_id = getattr(args, "course_id", None)
    if not course_id:
        err("--course-id is required")

    row = conn.execute("SELECT * FROM educlaw_course WHERE id = ?", (course_id,)).fetchone()
    if not row:
        err(f"Course {course_id} not found")

    data = dict(row)

    prereqs = conn.execute(
        """SELECT cp.*, c.course_code, c.name as prereq_name
           FROM educlaw_course_prerequisite cp
           JOIN educlaw_course c ON c.id = cp.prerequisite_course_id
           WHERE cp.course_id = ?""",
        (course_id,)
    ).fetchall()
    data["prerequisites"] = [dict(p) for p in prereqs]

    sections = conn.execute(
        """SELECT s.*, at.name as term_name
           FROM educlaw_section s
           JOIN educlaw_academic_term at ON at.id = s.academic_term_id
           WHERE s.course_id = ? AND s.status != 'cancelled'
           ORDER BY at.start_date DESC""",
        (course_id,)
    ).fetchall()
    data["sections"] = [dict(s) for s in sections]
    ok(data)


def list_courses(conn, args):
    query = "SELECT * FROM educlaw_course WHERE 1=1"
    params = []

    if getattr(args, "department_id", None):
        query += " AND department_id = ?"; params.append(args.department_id)
    if getattr(args, "grade_level", None):
        query += " AND grade_level = ?"; params.append(args.grade_level)
    if getattr(args, "course_type", None):
        query += " AND course_type = ?"; params.append(args.course_type)
    if getattr(args, "is_active", None) is not None:
        query += " AND is_active = ?"; params.append(int(args.is_active))
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY course_code"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"courses": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# SECTION
# ─────────────────────────────────────────────────────────────────────────────

def _check_section_conflicts(conn, academic_term_id, instructor_id, room_id,
                              days_of_week, start_time, end_time, exclude_section_id=None):
    """Validate no instructor or room conflicts. Returns error message or None."""
    if not start_time or not end_time or not days_of_week:
        return None

    # Get all sections in same term with schedule info
    q = """SELECT id, instructor_id, room_id, days_of_week, start_time, end_time
           FROM educlaw_section
           WHERE academic_term_id = ? AND status != 'cancelled'"""
    params = [academic_term_id]
    if exclude_section_id:
        q += " AND id != ?"
        params.append(exclude_section_id)

    existing = conn.execute(q, params).fetchall()
    for s in existing:
        s = dict(s)
        if not _times_overlap(start_time, end_time, s["start_time"], s["end_time"]):
            continue
        if not _days_overlap(days_of_week, s["days_of_week"]):
            continue
        # Time + day overlap → check instructor and room
        if instructor_id and s["instructor_id"] == instructor_id:
            return f"Instructor has a conflicting section at this time"
        if room_id and s["room_id"] == room_id:
            return f"Room is already booked at this time"
    return None


def add_section(conn, args):
    course_id = getattr(args, "course_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)
    section_number = getattr(args, "section_number", None)
    company_id = getattr(args, "company_id", None)
    max_enrollment = getattr(args, "max_enrollment", None)

    if not course_id:
        err("--course-id is required")
    if not academic_term_id:
        err("--academic-term-id is required")
    if not section_number:
        err("--section-number is required")
    if not company_id:
        err("--company-id is required")
    if not max_enrollment:
        err("--max-enrollment is required")
    if int(max_enrollment) <= 0:
        err("--max-enrollment must be greater than 0")

    if not conn.execute("SELECT id FROM educlaw_course WHERE id = ?", (course_id,)).fetchone():
        err(f"Course {course_id} not found")
    if not conn.execute("SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)).fetchone():
        err(f"Academic term {academic_term_id} not found")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    instructor_id = getattr(args, "instructor_id", None)
    if instructor_id:
        if not conn.execute("SELECT id FROM educlaw_instructor WHERE id = ?", (instructor_id,)).fetchone():
            err(f"Instructor {instructor_id} not found")

    room_id = getattr(args, "room_id", None)
    if room_id:
        room_row = conn.execute("SELECT * FROM educlaw_room WHERE id = ?", (room_id,)).fetchone()
        if not room_row:
            err(f"Room {room_id} not found")
        # Validate room capacity >= max_enrollment
        if dict(room_row)["capacity"] < int(max_enrollment):
            err(f"Room capacity ({dict(room_row)['capacity']}) is less than max_enrollment ({max_enrollment})")

    days_of_week = getattr(args, "days_of_week", None) or "[]"
    start_time = getattr(args, "start_time", None) or ""
    end_time = getattr(args, "end_time", None) or ""

    # Validate no conflicts
    conflict = _check_section_conflicts(conn, academic_term_id, instructor_id, room_id,
                                        days_of_week, start_time, end_time)
    if conflict:
        err(conflict)

    # Generate naming series
    section_series = get_next_name(conn, "educlaw_section", company_id=company_id)

    section_id = str(uuid.uuid4())
    waitlist_enabled = int(getattr(args, "waitlist_enabled", None) or 0)
    waitlist_max = int(getattr(args, "waitlist_max", None) or 0)
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_section
               (id, naming_series, section_number, course_id, academic_term_id, instructor_id,
                room_id, days_of_week, start_time, end_time, max_enrollment, current_enrollment,
                waitlist_enabled, waitlist_max, status, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (section_id, section_series, section_number, course_id, academic_term_id,
             instructor_id, room_id, days_of_week, start_time, end_time,
             int(max_enrollment), 0, waitlist_enabled, waitlist_max,
             "draft", company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Section creation failed: {e}")

    audit(conn, SKILL, "add-section", "educlaw_section", section_id,
          new_values={"naming_series": section_series, "course_id": course_id,
                      "academic_term_id": academic_term_id})
    conn.commit()
    ok({"id": section_id, "naming_series": section_series, "section_number": section_number,
        "course_id": course_id, "academic_term_id": academic_term_id})


def update_section(conn, args):
    section_id = getattr(args, "section_id", None)
    if not section_id:
        err("--section-id is required")

    row = conn.execute("SELECT * FROM educlaw_section WHERE id = ?", (section_id,)).fetchone()
    if not row:
        err(f"Section {section_id} not found")

    r = dict(row)
    if r["status"] in ("cancelled",):
        err("Cannot update a cancelled section")

    updates, params, changed = [], [], []

    if getattr(args, "section_number", None) is not None:
        updates.append("section_number = ?"); params.append(args.section_number); changed.append("section_number")
    if getattr(args, "instructor_id", None) is not None:
        if args.instructor_id and not conn.execute(
                "SELECT id FROM educlaw_instructor WHERE id = ?", (args.instructor_id,)).fetchone():
            err(f"Instructor {args.instructor_id} not found")
        updates.append("instructor_id = ?"); params.append(args.instructor_id); changed.append("instructor_id")
    if getattr(args, "room_id", None) is not None:
        if args.room_id:
            room_row = conn.execute("SELECT * FROM educlaw_room WHERE id = ?", (args.room_id,)).fetchone()
            if not room_row:
                err(f"Room {args.room_id} not found")
            new_max = getattr(args, "max_enrollment", None) or r["max_enrollment"]
            if dict(room_row)["capacity"] < int(new_max):
                err(f"Room capacity is less than max_enrollment")
        updates.append("room_id = ?"); params.append(args.room_id); changed.append("room_id")
    if getattr(args, "days_of_week", None) is not None:
        updates.append("days_of_week = ?"); params.append(args.days_of_week); changed.append("days_of_week")
    if getattr(args, "start_time", None) is not None:
        updates.append("start_time = ?"); params.append(args.start_time); changed.append("start_time")
    if getattr(args, "end_time", None) is not None:
        updates.append("end_time = ?"); params.append(args.end_time); changed.append("end_time")
    if getattr(args, "max_enrollment", None) is not None:
        if int(args.max_enrollment) <= 0:
            err("--max-enrollment must be greater than 0")
        updates.append("max_enrollment = ?"); params.append(int(args.max_enrollment)); changed.append("max_enrollment")
    if getattr(args, "waitlist_enabled", None) is not None:
        updates.append("waitlist_enabled = ?"); params.append(int(args.waitlist_enabled)); changed.append("waitlist_enabled")
    if getattr(args, "waitlist_max", None) is not None:
        updates.append("waitlist_max = ?"); params.append(int(args.waitlist_max)); changed.append("waitlist_max")

    if not changed:
        err("No fields to update")

    # Re-validate conflicts after update
    new_instructor = getattr(args, "instructor_id", None) or r["instructor_id"]
    new_room = getattr(args, "room_id", None) or r["room_id"]
    new_days = getattr(args, "days_of_week", None) or r["days_of_week"]
    new_start = getattr(args, "start_time", None) or r["start_time"]
    new_end = getattr(args, "end_time", None) or r["end_time"]

    conflict = _check_section_conflicts(conn, r["academic_term_id"], new_instructor, new_room,
                                        new_days, new_start, new_end, exclude_section_id=section_id)
    if conflict:
        err(conflict)

    updates.append("updated_at = datetime('now')")
    params.append(section_id)
    conn.execute(f"UPDATE educlaw_section SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-section", "educlaw_section", section_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": section_id, "updated_fields": changed})


def get_section(conn, args):
    section_id = getattr(args, "section_id", None)
    if not section_id:
        err("--section-id is required")

    row = conn.execute("SELECT * FROM educlaw_section WHERE id = ?", (section_id,)).fetchone()
    if not row:
        err(f"Section {section_id} not found")

    data = dict(row)
    try:
        data["days_of_week"] = json.loads(data["days_of_week"]) if data.get("days_of_week") else []
    except Exception:
        data["days_of_week"] = []

    enrollments = conn.execute(
        """SELECT ce.*, s.naming_series, s.first_name, s.last_name
           FROM educlaw_course_enrollment ce
           JOIN educlaw_student s ON s.id = ce.student_id
           WHERE ce.section_id = ? AND ce.enrollment_status IN ('enrolled','waitlisted')
           ORDER BY s.last_name, s.first_name""",
        (section_id,)
    ).fetchall()
    data["enrolled_students"] = [dict(e) for e in enrollments]
    data["enrollment_count"] = len([e for e in data["enrolled_students"]
                                    if dict(e)["enrollment_status"] == "enrolled"])

    plan = conn.execute(
        "SELECT * FROM educlaw_assessment_plan WHERE section_id = ?", (section_id,)
    ).fetchone()
    data["assessment_plan"] = dict(plan) if plan else None
    ok(data)


def list_sections(conn, args):
    query = "SELECT * FROM educlaw_section WHERE 1=1"
    params = []

    if getattr(args, "academic_term_id", None):
        query += " AND academic_term_id = ?"; params.append(args.academic_term_id)
    if getattr(args, "course_id", None):
        query += " AND course_id = ?"; params.append(args.course_id)
    if getattr(args, "instructor_id", None):
        query += " AND instructor_id = ?"; params.append(args.instructor_id)
    if getattr(args, "section_status", None):
        query += " AND status = ?"; params.append(args.section_status)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY naming_series"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"sections": [dict(r) for r in rows], "count": len(rows)})


def open_section(conn, args):
    section_id = getattr(args, "section_id", None)
    if not section_id:
        err("--section-id is required")

    row = conn.execute("SELECT * FROM educlaw_section WHERE id = ?", (section_id,)).fetchone()
    if not row:
        err(f"Section {section_id} not found")

    r = dict(row)
    current_status = r["status"]

    # open-section transitions draft or scheduled → open (enrollment opened)
    allowed_from = {"draft", "scheduled"}
    if current_status not in allowed_from:
        err(f"Cannot open section from status '{current_status}'. Must be 'draft' or 'scheduled'")

    # Validate instructor and room assigned before opening
    if not r["instructor_id"]:
        err("Instructor must be assigned before opening section")
    if not r["room_id"]:
        err("Room must be assigned before opening section")

    new_status = "open"
    conn.execute(
        "UPDATE educlaw_section SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (new_status, section_id)
    )
    audit(conn, SKILL, "open-section", "educlaw_section", section_id,
          new_values={"old_status": current_status, "new_status": new_status})
    conn.commit()
    ok({"id": section_id, "old_status": current_status, "section_status": new_status})


def cancel_section(conn, args):
    section_id = getattr(args, "section_id", None)
    if not section_id:
        err("--section-id is required")

    row = conn.execute("SELECT * FROM educlaw_section WHERE id = ?", (section_id,)).fetchone()
    if not row:
        err(f"Section {section_id} not found")

    r = dict(row)
    if r["status"] == "cancelled":
        err("Section is already cancelled")

    # Drop all enrolled students
    enrolled = conn.execute(
        """SELECT id, student_id FROM educlaw_course_enrollment
           WHERE section_id = ? AND enrollment_status = 'enrolled'""",
        (section_id,)
    ).fetchall()

    now = _now_iso()
    dropped_count = 0
    for enr in enrolled:
        enr = dict(enr)
        conn.execute(
            """UPDATE educlaw_course_enrollment
               SET enrollment_status = 'dropped', drop_date = ?, drop_reason = 'Section cancelled',
                   updated_at = datetime('now')
               WHERE id = ?""",
            (now[:10], enr["id"])
        )
        # Create notification for each dropped student
        notif_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_notification
               (id, recipient_type, recipient_id, notification_type, title, message,
                reference_type, reference_id, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (notif_id, "student", enr["student_id"], "announcement",
             "Section Cancelled",
             f"Your enrollment in section {r['naming_series']} has been dropped due to section cancellation.",
             "educlaw_section", section_id, r["company_id"], now,
             getattr(args, "user_id", None) or "")
        )
        dropped_count += 1

    # Cancel waitlisted entries
    conn.execute(
        """UPDATE educlaw_waitlist SET waitlist_status = 'cancelled', updated_at = datetime('now')
           WHERE section_id = ? AND waitlist_status = 'waiting'""",
        (section_id,)
    )

    conn.execute(
        "UPDATE educlaw_section SET status = 'cancelled', current_enrollment = 0, updated_at = datetime('now') WHERE id = ?",
        (section_id,)
    )
    audit(conn, SKILL, "cancel-section", "educlaw_section", section_id,
          new_values={"dropped_students": dropped_count})
    conn.commit()
    ok({"id": section_id, "section_status": "cancelled", "dropped_students": dropped_count})


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-academic-year": add_academic_year,
    "update-academic-year": update_academic_year,
    "get-academic-year": get_academic_year,
    "list-academic-years": list_academic_years,
    "add-academic-term": add_academic_term,
    "update-academic-term": update_academic_term,
    "get-academic-term": get_academic_term,
    "list-academic-terms": list_academic_terms,
    "add-room": add_room,
    "update-room": update_room,
    "list-rooms": list_rooms,
    "add-program": add_program,
    "update-program": update_program,
    "get-program": get_program,
    "list-programs": list_programs,
    "add-course": add_course,
    "update-course": update_course,
    "get-course": get_course,
    "list-courses": list_courses,
    "add-section": add_section,
    "update-section": update_section,
    "get-section": get_section,
    "list-sections": list_sections,
    "activate-section": open_section,
    "cancel-section": cancel_section,
}
