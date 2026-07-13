"""EduClaw — enrollment domain module

Actions for enrollment: program enrollment, course section enrollment,
drop/add, waitlist management, prerequisite enforcement.

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
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAM ENROLLMENT
# ─────────────────────────────────────────────────────────────────────────────

def enroll_in_program(conn, args):
    student_id = getattr(args, "student_id", None)
    program_id = getattr(args, "program_id", None)
    academic_year_id = getattr(args, "academic_year_id", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not program_id:
        err("--program-id is required")
    if not academic_year_id:
        err("--academic-year-id is required")
    if not company_id:
        err("--company-id is required")

    # Validate student exists and is active
    student_row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not student_row:
        err(f"Student {student_id} not found")
    student = dict(student_row)
    if student["status"] != "active":
        err(f"Student must be active to enroll (current status: {student['status']})")
    if student["registration_hold"]:
        err("Student has a registration hold — resolve outstanding fees before enrolling")

    # Validate program and academic year
    if not conn.execute("SELECT id FROM educlaw_program WHERE id = ?", (program_id,)).fetchone():
        err(f"Program {program_id} not found")
    if not conn.execute("SELECT id FROM educlaw_academic_year WHERE id = ?", (academic_year_id,)).fetchone():
        err(f"Academic year {academic_year_id} not found")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Check for existing active enrollment in same program/year
    existing = conn.execute(
        """SELECT id FROM educlaw_program_enrollment
           WHERE student_id = ? AND program_id = ? AND academic_year_id = ?""",
        (student_id, program_id, academic_year_id)
    ).fetchone()
    if existing:
        err(f"Student is already enrolled in this program for this academic year")

    naming = get_next_name(conn, "educlaw_program_enrollment", company_id=company_id)
    enr_id = str(uuid.uuid4())
    enrollment_date = getattr(args, "enrollment_date", None) or _now_iso()[:10]
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_program_enrollment
           (id, naming_series, student_id, program_id, academic_year_id,
            enrollment_date, enrollment_status, fee_invoice_id, company_id,
            created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (enr_id, naming, student_id, program_id, academic_year_id,
         enrollment_date, "active", "",
         company_id, now, now, getattr(args, "user_id", None) or "")
    )

    # Send enrollment confirmed notification
    notif_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_notification
           (id, recipient_type, recipient_id, notification_type, title, message,
            reference_type, reference_id, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (notif_id, "student", student_id, "enrollment_confirmed",
         "Program Enrollment Confirmed",
         f"You have been enrolled in the program. Enrollment ID: {naming}",
         "educlaw_program_enrollment", enr_id, company_id, now,
         getattr(args, "user_id", None) or "")
    )

    audit(conn, SKILL, "enroll-in-program", "educlaw_program_enrollment", enr_id,
          new_values={"naming_series": naming, "student_id": student_id,
                      "program_id": program_id, "academic_year_id": academic_year_id})
    conn.commit()
    ok({"id": enr_id, "naming_series": naming, "student_id": student_id,
        "program_id": program_id, "enrollment_status": "active"})


def withdraw_from_program(conn, args):
    enrollment_id = getattr(args, "enrollment_id", None)
    if not enrollment_id:
        err("--enrollment-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_program_enrollment WHERE id = ?", (enrollment_id,)
    ).fetchone()
    if not row:
        err(f"Program enrollment {enrollment_id} not found")

    r = dict(row)
    if r["enrollment_status"] != "active":
        err(f"Only active enrollments can be withdrawn (current: {r['enrollment_status']})")

    now = _now_iso()
    conn.execute(
        """UPDATE educlaw_program_enrollment
           SET enrollment_status = 'withdrawn', updated_at = datetime('now')
           WHERE id = ?""",
        (enrollment_id,)
    )

    notif_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_notification
           (id, recipient_type, recipient_id, notification_type, title, message,
            reference_type, reference_id, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (notif_id, "student", r["student_id"], "announcement",
         "Program Withdrawal Processed",
         f"Your withdrawal from program enrollment {r['naming_series']} has been processed.",
         "educlaw_program_enrollment", enrollment_id, r["company_id"], now,
         getattr(args, "user_id", None) or "")
    )

    audit(conn, SKILL, "withdraw-from-program", "educlaw_program_enrollment", enrollment_id,
          new_values={"enrollment_status": "withdrawn"})
    conn.commit()
    ok({"id": enrollment_id, "enrollment_status": "withdrawn"})


def list_program_enrollments(conn, args):
    query = "SELECT * FROM educlaw_program_enrollment WHERE 1=1"
    params = []

    if getattr(args, "student_id", None):
        query += " AND student_id = ?"; params.append(args.student_id)
    if getattr(args, "program_id", None):
        query += " AND program_id = ?"; params.append(args.program_id)
    if getattr(args, "academic_year_id", None):
        query += " AND academic_year_id = ?"; params.append(args.academic_year_id)
    if getattr(args, "enrollment_status", None):
        query += " AND enrollment_status = ?"; params.append(args.enrollment_status)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY enrollment_date DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"program_enrollments": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# COURSE SECTION ENROLLMENT
# ─────────────────────────────────────────────────────────────────────────────

def _check_prerequisite(conn, student_id, course_id):
    """Check if student has met all prerequisites for a course. Returns error msg or None."""
    prereqs = conn.execute(
        """SELECT cp.prerequisite_course_id, cp.min_grade, cp.is_corequisite,
                  c.course_code
           FROM educlaw_course_prerequisite cp
           JOIN educlaw_course c ON c.id = cp.prerequisite_course_id
           WHERE cp.course_id = ?""",
        (course_id,)
    ).fetchall()

    for prereq in prereqs:
        p = dict(prereq)
        if p["is_corequisite"]:
            continue  # Corequisites can be taken concurrently

        # Check if student has completed this prerequisite with sufficient grade
        completed = conn.execute(
            """SELECT ce.final_letter_grade, ce.final_grade_points, ce.is_grade_submitted,
                      ce.enrollment_status
               FROM educlaw_course_enrollment ce
               JOIN educlaw_section s ON s.id = ce.section_id
               WHERE ce.student_id = ? AND s.course_id = ?
               AND ce.is_grade_submitted = 1
               AND ce.enrollment_status = 'completed'""",
            (student_id, p["prerequisite_course_id"])
        ).fetchone()

        if not completed:
            return f"Prerequisite not met: {p['course_code']} must be completed first"

        if p["min_grade"]:
            # Check that final_grade >= min_grade
            # Grade comparison: A > B > C > D > F (need to compare via grade_points if possible)
            grade_map = {"A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
                         "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7,
                         "F": 0.0, "P": None, "NP": None, "W": None, "I": None}
            c = dict(completed)
            req_pts = grade_map.get(p["min_grade"], 0.0)
            earned_pts = float(c["final_grade_points"]) if c["final_grade_points"] else 0.0
            if req_pts is not None and earned_pts < req_pts:
                return (f"Prerequisite {p['course_code']} requires minimum grade "
                        f"{p['min_grade']} (earned: {c['final_letter_grade']})")
    return None


def enroll_in_section(conn, args):
    student_id = getattr(args, "student_id", None)
    section_id = getattr(args, "section_id", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not section_id:
        err("--section-id is required")
    if not company_id:
        err("--company-id is required")

    student_row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not student_row:
        err(f"Student {student_id} not found")
    student = dict(student_row)
    if student["status"] != "active":
        err(f"Student must be active to enroll in sections")
    if student["registration_hold"]:
        err("Student has a registration hold")

    section_row = conn.execute("SELECT * FROM educlaw_section WHERE id = ?", (section_id,)).fetchone()
    if not section_row:
        err(f"Section {section_id} not found")
    section = dict(section_row)

    if section["status"] != "open":
        err(f"Section is not open for enrollment (status: {section['status']})")

    # Check for active program enrollment in same term
    term_row = conn.execute(
        "SELECT academic_year_id FROM educlaw_academic_term WHERE id = ?",
        (section["academic_term_id"],)
    ).fetchone()
    if term_row:
        prog_enr = conn.execute(
            """SELECT id FROM educlaw_program_enrollment
               WHERE student_id = ? AND academic_year_id = ? AND enrollment_status = 'active'""",
            (student_id, term_row["academic_year_id"])
        ).fetchone()
        if not prog_enr:
            err("Student must have an active program enrollment for this academic year")

    # Check for duplicate enrollment
    dup = conn.execute(
        "SELECT id FROM educlaw_course_enrollment WHERE student_id = ? AND section_id = ?",
        (student_id, section_id)
    ).fetchone()
    if dup:
        err("Student is already enrolled in this section")

    # Check for duplicate course in same term (same course, different section)
    same_course = conn.execute(
        """SELECT ce.id FROM educlaw_course_enrollment ce
           JOIN educlaw_section s ON s.id = ce.section_id
           WHERE ce.student_id = ? AND s.course_id = ? AND s.academic_term_id = ?
           AND ce.enrollment_status IN ('enrolled', 'waitlisted')""",
        (student_id, section["course_id"], section["academic_term_id"])
    ).fetchone()
    if same_course:
        err("Student is already enrolled in another section of this course this term")

    # Check prerequisites
    prereq_err = _check_prerequisite(conn, student_id, section["course_id"])
    if prereq_err:
        err(prereq_err)

    now = _now_iso()
    grade_type = getattr(args, "grade_type", None) or "letter"

    # Check if section is full
    if section["current_enrollment"] >= section["max_enrollment"]:
        if section["waitlist_enabled"]:
            # Add to waitlist
            wait_count = conn.execute(
                "SELECT COUNT(*) FROM educlaw_waitlist WHERE section_id = ? AND waitlist_status = 'waiting'",
                (section_id,)
            ).fetchone()[0]
            if section["waitlist_max"] > 0 and wait_count >= section["waitlist_max"]:
                err("Section is full and waitlist is also full")
            position = wait_count + 1
            wait_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO educlaw_waitlist
                   (id, student_id, section_id, position, requested_date, waitlist_status,
                    offer_expires_at, company_id, created_at, updated_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (wait_id, student_id, section_id, position, now, "waiting", "",
                 company_id, now, now, getattr(args, "user_id", None) or "")
            )
            conn.commit()
            ok({"id": wait_id, "enrollment_status": "waitlisted", "waitlist_position": position,
                "section_id": section_id, "student_id": student_id})
            return
        else:
            err("Section is full and waitlist is not enabled")

    # Enroll student
    enr_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_course_enrollment
           (id, student_id, section_id, enrollment_date, enrollment_status,
            drop_date, drop_reason, final_letter_grade, final_grade_points, final_percentage,
            grade_submitted_by, grade_submitted_at, is_grade_submitted, is_repeat,
            grade_type, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (enr_id, student_id, section_id, now[:10], "enrolled",
         "", "", "", "0", "0",
         "", "", 0, int(getattr(args, "is_repeat", None) or 0),
         grade_type, company_id, now, now, getattr(args, "user_id", None) or "")
    )

    # Increment section enrollment count
    conn.execute(
        "UPDATE educlaw_section SET current_enrollment = current_enrollment + 1, updated_at = datetime('now') WHERE id = ?",
        (section_id,)
    )

    audit(conn, SKILL, "enroll-in-section", "educlaw_course_enrollment", enr_id,
          new_values={"student_id": student_id, "section_id": section_id})
    conn.commit()
    ok({"id": enr_id, "enrollment_status": "enrolled", "student_id": student_id,
        "section_id": section_id})


def drop_enrollment(conn, args):
    enrollment_id = getattr(args, "enrollment_id", None)
    if not enrollment_id:
        err("--enrollment-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_course_enrollment WHERE id = ?", (enrollment_id,)
    ).fetchone()
    if not row:
        err(f"Enrollment {enrollment_id} not found")

    r = dict(row)
    if r["enrollment_status"] != "enrolled":
        err(f"Only active enrollments can be dropped (current: {r['enrollment_status']})")
    if r["is_grade_submitted"]:
        err("Cannot drop enrollment after grades have been submitted")

    now = _now_iso()
    drop_reason = getattr(args, "drop_reason", None) or ""
    conn.execute(
        """UPDATE educlaw_course_enrollment
           SET enrollment_status = 'dropped', drop_date = ?, drop_reason = ?,
               updated_at = datetime('now')
           WHERE id = ?""",
        (now[:10], drop_reason, enrollment_id)
    )

    # Decrement section count
    conn.execute(
        "UPDATE educlaw_section SET current_enrollment = MAX(0, current_enrollment - 1), updated_at = datetime('now') WHERE id = ?",
        (r["section_id"],)
    )

    # Process waitlist if enabled
    section_row = conn.execute(
        "SELECT * FROM educlaw_section WHERE id = ?", (r["section_id"],)
    ).fetchone()
    if section_row and dict(section_row)["waitlist_enabled"]:
        _advance_waitlist(conn, r["section_id"], dict(section_row)["company_id"], now)

    audit(conn, SKILL, "drop-enrollment", "educlaw_course_enrollment", enrollment_id,
          new_values={"enrollment_status": "dropped", "drop_reason": drop_reason})
    conn.commit()
    ok({"id": enrollment_id, "enrollment_status": "dropped", "drop_date": now[:10]})


def withdraw_enrollment(conn, args):
    """Withdraw after drop/add period — records W grade."""
    enrollment_id = getattr(args, "enrollment_id", None)
    if not enrollment_id:
        err("--enrollment-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_course_enrollment WHERE id = ?", (enrollment_id,)
    ).fetchone()
    if not row:
        err(f"Enrollment {enrollment_id} not found")

    r = dict(row)
    if r["enrollment_status"] not in ("enrolled",):
        err(f"Only enrolled courses can be withdrawn (current: {r['enrollment_status']})")
    if r["is_grade_submitted"]:
        err("Cannot withdraw after grades have been submitted")

    now = _now_iso()
    conn.execute(
        """UPDATE educlaw_course_enrollment
           SET enrollment_status = 'withdrawn', drop_date = ?,
               drop_reason = ?, final_letter_grade = 'W',
               updated_at = datetime('now')
           WHERE id = ?""",
        (now[:10], getattr(args, "drop_reason", None) or "Student withdrawal", enrollment_id)
    )

    conn.execute(
        "UPDATE educlaw_section SET current_enrollment = MAX(0, current_enrollment - 1), updated_at = datetime('now') WHERE id = ?",
        (r["section_id"],)
    )

    audit(conn, SKILL, "withdraw-enrollment", "educlaw_course_enrollment", enrollment_id,
          new_values={"enrollment_status": "withdrawn", "final_letter_grade": "W"})
    conn.commit()
    ok({"id": enrollment_id, "enrollment_status": "withdrawn",
        "final_letter_grade": "W", "drop_date": now[:10]})


def get_enrollment(conn, args):
    enrollment_id = getattr(args, "enrollment_id", None)
    if not enrollment_id:
        err("--enrollment-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_course_enrollment WHERE id = ?", (enrollment_id,)
    ).fetchone()
    if not row:
        err(f"Enrollment {enrollment_id} not found")

    data = dict(row)

    # Assessment results summary
    results = conn.execute(
        """SELECT ar.*, a.name as assessment_name, a.max_points, a.due_date,
                  ac.name as category_name
           FROM educlaw_assessment_result ar
           JOIN educlaw_assessment a ON a.id = ar.assessment_id
           JOIN educlaw_assessment_category ac ON ac.id = a.category_id
           WHERE ar.course_enrollment_id = ?
           ORDER BY a.due_date""",
        (enrollment_id,)
    ).fetchall()
    data["assessment_results"] = [dict(r) for r in results]
    ok(data)


def list_enrollments(conn, args):
    query = "SELECT * FROM educlaw_course_enrollment WHERE 1=1"
    params = []

    if getattr(args, "student_id", None):
        query += " AND student_id = ?"; params.append(args.student_id)
    if getattr(args, "section_id", None):
        query += " AND section_id = ?"; params.append(args.section_id)
    if getattr(args, "academic_term_id", None):
        query += """ AND section_id IN (
            SELECT id FROM educlaw_section WHERE academic_term_id = ?)"""
        params.append(args.academic_term_id)
    if getattr(args, "enrollment_status", None):
        query += " AND enrollment_status = ?"; params.append(args.enrollment_status)
    if getattr(args, "is_grade_submitted", None) is not None:
        query += " AND is_grade_submitted = ?"; params.append(int(args.is_grade_submitted))
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY enrollment_date DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"enrollments": [dict(r) for r in rows], "count": len(rows)})


def _advance_waitlist(conn, section_id, company_id, now):
    """Advance waitlist — offer seat to first waiting student."""
    next_wait = conn.execute(
        """SELECT * FROM educlaw_waitlist
           WHERE section_id = ? AND waitlist_status = 'waiting'
           ORDER BY position ASC LIMIT 1""",
        (section_id,)
    ).fetchone()
    if not next_wait:
        return

    w = dict(next_wait)
    # Calculate offer expiry (48 hours)
    from datetime import timedelta
    offer_expires = (datetime.now(timezone.utc) + timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")

    conn.execute(
        """UPDATE educlaw_waitlist
           SET waitlist_status = 'offered', offer_expires_at = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (offer_expires, w["id"])
    )
    notif_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_notification
           (id, recipient_type, recipient_id, notification_type, title, message,
            reference_type, reference_id, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (notif_id, "student", w["student_id"], "enrollment_confirmed",
         "Waitlist Seat Offered",
         f"A seat is now available in section {section_id}. Offer expires: {offer_expires}",
         "educlaw_waitlist", w["id"], company_id, now, "system")
    )


def process_waitlist(conn, args):
    section_id = getattr(args, "section_id", None)
    if not section_id:
        err("--section-id is required")

    section_row = conn.execute("SELECT * FROM educlaw_section WHERE id = ?", (section_id,)).fetchone()
    if not section_row:
        err(f"Section {section_id} not found")

    section = dict(section_row)
    now = _now_iso()

    if section["current_enrollment"] >= section["max_enrollment"]:
        ok({"section_id": section_id, "message": "Section is full — no seat to offer"})
        return

    _advance_waitlist(conn, section_id, section["company_id"], now)
    conn.commit()
    ok({"section_id": section_id, "message": "Waitlist processed — next student offered seat"})


def list_waitlist(conn, args):
    query = "SELECT * FROM educlaw_waitlist WHERE 1=1"
    params = []

    if getattr(args, "section_id", None):
        query += " AND section_id = ?"; params.append(args.section_id)
    if getattr(args, "student_id", None):
        query += " AND student_id = ?"; params.append(args.student_id)
    if getattr(args, "waitlist_status", None):
        query += " AND waitlist_status = ?"; params.append(args.waitlist_status)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY section_id, position"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"waitlist": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "create-program-enrollment": enroll_in_program,
    "cancel-program-enrollment": withdraw_from_program,
    "list-program-enrollments": list_program_enrollments,
    "create-section-enrollment": enroll_in_section,
    "cancel-enrollment": drop_enrollment,
    "terminate-enrollment": withdraw_enrollment,
    "get-enrollment": get_enrollment,
    "list-enrollments": list_enrollments,
    "apply-waitlist": process_waitlist,
    "list-waitlist": list_waitlist,
}
