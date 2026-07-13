"""EduClaw — attendance domain module

Actions for attendance: daily homeroom and per-section attendance,
attendance summaries, truancy reporting.

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_ATTENDANCE_STATUSES = ("present", "absent", "tardy", "excused", "half_day")
VALID_SOURCES = ("manual", "biometric", "app")


# ─────────────────────────────────────────────────────────────────────────────
# ATTENDANCE
# ─────────────────────────────────────────────────────────────────────────────

def mark_attendance(conn, args):
    student_id = getattr(args, "student_id", None)
    attendance_date = getattr(args, "attendance_date", None)
    attendance_status = getattr(args, "attendance_status", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not attendance_date:
        err("--attendance-date is required")
    if not attendance_status:
        err("--attendance-status is required")
    if attendance_status not in VALID_ATTENDANCE_STATUSES:
        err(f"--attendance-status must be one of: {', '.join(VALID_ATTENDANCE_STATUSES)}")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")

    section_id = getattr(args, "section_id", None)
    if section_id:
        if not conn.execute("SELECT id FROM educlaw_section WHERE id = ?", (section_id,)).fetchone():
            err(f"Section {section_id} not found")

    source = getattr(args, "source", None) or "manual"
    if source not in VALID_SOURCES:
        err(f"--source must be one of: {', '.join(VALID_SOURCES)}")

    att_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_student_attendance
               (id, student_id, attendance_date, section_id, attendance_status,
                late_minutes, comments, marked_by, source, company_id,
                created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (att_id, student_id, attendance_date, section_id, attendance_status,
             int(getattr(args, "late_minutes", None) or 0),
             getattr(args, "comments", None) or "",
             getattr(args, "marked_by", None) or getattr(args, "user_id", None) or "",
             source, company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError:
        err(f"Attendance already recorded for student {student_id} on {attendance_date}"
            + (f" in section {section_id}" if section_id else ""))

    conn.commit()
    ok({"id": att_id, "student_id": student_id, "attendance_date": attendance_date,
        "attendance_status": attendance_status, "section_id": section_id})


def batch_mark_attendance(conn, args):
    attendance_date = getattr(args, "attendance_date", None)
    company_id = getattr(args, "company_id", None)
    records_json = getattr(args, "records", None)

    if not attendance_date:
        err("--attendance-date is required")
    if not company_id:
        err("--company-id is required")
    if not records_json:
        err("--records is required (JSON array of {student_id, attendance_status})")

    try:
        records = json.loads(records_json) if isinstance(records_json, str) else records_json
        if not isinstance(records, list):
            err("--records must be a JSON array")
    except (json.JSONDecodeError, TypeError):
        err("--records must be valid JSON")

    section_id = getattr(args, "section_id", None)
    source = getattr(args, "source", None) or "manual"
    marked_by = getattr(args, "marked_by", None) or getattr(args, "user_id", None) or ""
    now = _now_iso()

    saved_count = 0
    errors = []

    for rec in records:
        if not isinstance(rec, dict):
            continue
        student_id = rec.get("student_id")
        status = rec.get("attendance_status", None) or "present"

        if not student_id:
            errors.append({"error": "student_id is required", "data": rec})
            continue
        if status not in VALID_ATTENDANCE_STATUSES:
            errors.append({"student_id": student_id,
                           "error": f"Invalid attendance_status: {status}"})
            continue

        att_id = str(uuid.uuid4())
        try:
            conn.execute(
                """INSERT INTO educlaw_student_attendance
                   (id, student_id, attendance_date, section_id, attendance_status,
                    late_minutes, comments, marked_by, source, company_id,
                    created_at, updated_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (att_id, student_id, attendance_date, section_id, status,
                 int(rec.get("late_minutes", 0)),
                 rec.get("comments", ""),
                 marked_by, source, company_id, now, now, marked_by)
            )
            saved_count += 1
        except sqlite3.IntegrityError:
            errors.append({"student_id": student_id,
                           "error": "Attendance already recorded for this date/section"})

    conn.commit()
    ok({"attendance_date": attendance_date, "saved": saved_count, "errors": errors})


def update_attendance(conn, args):
    attendance_id = getattr(args, "attendance_id", None)
    if not attendance_id:
        err("--attendance-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_student_attendance WHERE id = ?", (attendance_id,)
    ).fetchone()
    if not row:
        err(f"Attendance record {attendance_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "attendance_status", None) is not None:
        if args.attendance_status not in VALID_ATTENDANCE_STATUSES:
            err(f"--attendance-status must be one of: {', '.join(VALID_ATTENDANCE_STATUSES)}")
        updates.append("attendance_status = ?"); params.append(args.attendance_status)
        changed.append("attendance_status")
    if getattr(args, "late_minutes", None) is not None:
        updates.append("late_minutes = ?"); params.append(int(args.late_minutes))
        changed.append("late_minutes")
    if getattr(args, "comments", None) is not None:
        updates.append("comments = ?"); params.append(args.comments); changed.append("comments")
    if getattr(args, "marked_by", None) is not None:
        updates.append("marked_by = ?"); params.append(args.marked_by); changed.append("marked_by")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(attendance_id)
    conn.execute(f"UPDATE educlaw_student_attendance SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    ok({"id": attendance_id, "updated_fields": changed})


def get_attendance(conn, args):
    attendance_id = getattr(args, "attendance_id", None)
    if not attendance_id:
        err("--attendance-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_student_attendance WHERE id = ?", (attendance_id,)
    ).fetchone()
    if not row:
        err(f"Attendance record {attendance_id} not found")
    ok(dict(row))


def list_attendance(conn, args):
    query = "SELECT * FROM educlaw_student_attendance WHERE 1=1"
    params = []

    if getattr(args, "student_id", None):
        query += " AND student_id = ?"; params.append(args.student_id)
    if getattr(args, "section_id", None):
        query += " AND section_id = ?"; params.append(args.section_id)
    if getattr(args, "attendance_date_from", None):
        query += " AND attendance_date >= ?"; params.append(args.attendance_date_from)
    if getattr(args, "attendance_date_to", None):
        query += " AND attendance_date <= ?"; params.append(args.attendance_date_to)
    if getattr(args, "attendance_status", None):
        query += " AND attendance_status = ?"; params.append(args.attendance_status)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY attendance_date DESC, student_id"
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"attendance_records": [dict(r) for r in rows], "count": len(rows)})


def get_attendance_summary(conn, args):
    student_id = getattr(args, "student_id", None)
    if not student_id:
        err("--student-id is required")

    query = "SELECT attendance_status, COUNT(*) as cnt FROM educlaw_student_attendance WHERE student_id = ?"
    params = [student_id]

    section_id = getattr(args, "section_id", None)
    if section_id:
        query += " AND section_id = ?"; params.append(section_id)

    from_date = getattr(args, "attendance_date_from", None)
    to_date = getattr(args, "attendance_date_to", None)
    if from_date:
        query += " AND attendance_date >= ?"; params.append(from_date)
    if to_date:
        query += " AND attendance_date <= ?"; params.append(to_date)

    query += " GROUP BY attendance_status"
    rows = conn.execute(query, params).fetchall()

    counts = {r["attendance_status"]: r["cnt"] for r in rows}
    total = sum(counts.values())
    present = counts.get("present", 0) + counts.get("half_day", 0) // 2
    absent = counts.get("absent", 0)
    tardy = counts.get("tardy", 0)
    excused = counts.get("excused", 0)

    attendance_pct = "0.00"
    if total > 0:
        pct = (Decimal(str(present + excused)) / Decimal(str(total)) * Decimal("100"))
        attendance_pct = str(pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    ok({
        "student_id": student_id,
        "total_days": total,
        "present": counts.get("present", 0),
        "absent": absent,
        "tardy": tardy,
        "excused": excused,
        "half_day": counts.get("half_day", 0),
        "attendance_percentage": attendance_pct,
    })


def get_section_attendance(conn, args):
    section_id = getattr(args, "section_id", None)
    if not section_id:
        err("--section-id is required")

    query = """SELECT sa.*, s.first_name, s.last_name, s.naming_series
               FROM educlaw_student_attendance sa
               JOIN educlaw_student s ON s.id = sa.student_id
               WHERE sa.section_id = ?"""
    params = [section_id]

    from_date = getattr(args, "attendance_date_from", None)
    to_date = getattr(args, "attendance_date_to", None)
    att_date = getattr(args, "attendance_date", None)

    if att_date:
        query += " AND sa.attendance_date = ?"; params.append(att_date)
    if from_date:
        query += " AND sa.attendance_date >= ?"; params.append(from_date)
    if to_date:
        query += " AND sa.attendance_date <= ?"; params.append(to_date)

    query += " ORDER BY sa.attendance_date, s.last_name, s.first_name"
    limit = int(getattr(args, "limit", None) or 200)
    query += f" LIMIT {limit}"

    rows = conn.execute(query, params).fetchall()
    ok({"section_id": section_id, "attendance_records": [dict(r) for r in rows],
        "count": len(rows)})


def get_truancy_report(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    threshold = float(getattr(args, "threshold", None) or 90)

    from_date = getattr(args, "attendance_date_from", None)
    to_date = getattr(args, "attendance_date_to", None)
    grade_level = getattr(args, "grade_level", None)
    section_id = getattr(args, "section_id", None)

    # Get all active students for company
    student_query = "SELECT id, naming_series, full_name, grade_level FROM educlaw_student WHERE company_id = ? AND status = 'active'"
    student_params = [company_id]
    if grade_level:
        student_query += " AND grade_level = ?"; student_params.append(grade_level)

    students = conn.execute(student_query, student_params).fetchall()
    truant_students = []

    for student in students:
        s = dict(student)
        # Count attendance for this student
        att_query = "SELECT attendance_status, COUNT(*) as cnt FROM educlaw_student_attendance WHERE student_id = ? AND company_id = ?"
        att_params = [s["id"], company_id]
        if section_id:
            att_query += " AND section_id = ?"; att_params.append(section_id)
        if from_date:
            att_query += " AND attendance_date >= ?"; att_params.append(from_date)
        if to_date:
            att_query += " AND attendance_date <= ?"; att_params.append(to_date)
        att_query += " GROUP BY attendance_status"

        counts = {r["attendance_status"]: r["cnt"]
                  for r in conn.execute(att_query, att_params).fetchall()}
        total = sum(counts.values())
        if total == 0:
            continue

        present = counts.get("present", 0)
        excused = counts.get("excused", 0)
        pct = (Decimal(str(present + excused)) / Decimal(str(total)) * Decimal("100"))
        att_pct = float(pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        if att_pct < threshold:
            # Get guardian contact
            guardians = conn.execute(
                """SELECT g.full_name, g.phone, g.email, sg.is_primary_contact
                   FROM educlaw_guardian g
                   JOIN educlaw_student_guardian sg ON sg.guardian_id = g.id
                   WHERE sg.student_id = ? AND sg.receives_communications = 1
                   ORDER BY sg.is_primary_contact DESC""",
                (s["id"],)
            ).fetchall()

            truant_students.append({
                "student_id": s["id"],
                "naming_series": s["naming_series"],
                "full_name": s["full_name"],
                "grade_level": s["grade_level"],
                "total_days": total,
                "present": present,
                "excused": excused,
                "absent": counts.get("absent", 0),
                "attendance_percentage": att_pct,
                "guardians": [dict(g) for g in guardians],
            })

    ok({
        "threshold_pct": threshold,
        "truant_student_count": len(truant_students),
        "truant_students": truant_students,
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "record-attendance": mark_attendance,
    "record-batch-attendance": batch_mark_attendance,
    "update-attendance": update_attendance,
    "get-attendance": get_attendance,
    "list-attendance": list_attendance,
    "get-attendance-summary": get_attendance_summary,
    "get-section-attendance": get_section_attendance,
    "get-truancy-report": get_truancy_report,
}
