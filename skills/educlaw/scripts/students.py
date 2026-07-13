"""EduClaw — students domain module

Actions for the students domain: student applicants, students, guardians,
and FERPA compliance (data access log, consent records).

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, date, timezone
from decimal import Decimal

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.decimal_utils import to_decimal
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_APPLICANT_STATUSES = (
    "applied", "under_review", "accepted", "rejected",
    "waitlisted", "pending_info", "confirmed", "enrolled"
)
VALID_STUDENT_STATUSES = (
    "active", "graduated", "withdrawn", "suspended", "expelled", "transferred", "inactive"
)
VALID_ACADEMIC_STANDINGS = ("good", "deans_list", "honor_roll", "probation", "suspension")
VALID_GENDERS = ("male", "female", "non_binary", "prefer_not_to_say", "")
VALID_RELATIONSHIPS = (
    "father", "mother", "guardian", "grandparent", "stepparent", "foster_parent", "other"
)
VALID_CONSENT_TYPES = (
    "ferpa_directory", "ferpa_disclosure", "coppa_collection", "coppa_school_consent"
)
VALID_DATA_CATEGORIES = (
    "demographics", "grades", "attendance", "financial", "health", "discipline", "communications"
)
VALID_ACCESS_TYPES = ("view", "export", "print", "api")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _is_coppa_applicable(date_of_birth_str, enrollment_date_str=None):
    """Return True if student is under 13 at enrollment."""
    try:
        dob = date.fromisoformat(date_of_birth_str)
        ref = date.fromisoformat(enrollment_date_str) if enrollment_date_str else date.today()
        age_years = (ref - dob).days / 365.25
        return age_years < 13
    except Exception:
        return False


def _log_data_access_internal(conn, user_id, student_id, data_category,
                               access_type, access_reason, is_emergency, company_id):
    """Internal helper to log FERPA data access without failing main operation."""
    log_id = str(uuid.uuid4())
    now = _now_iso()
    try:
        conn.execute(
            """INSERT INTO educlaw_data_access_log
               (id, user_id, student_id, data_category, access_type, access_reason,
                is_emergency_access, ip_address, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (log_id, user_id, student_id, data_category, access_type,
             access_reason, int(is_emergency), "", company_id, now, user_id)
        )
    except Exception:
        pass  # Don't fail the main operation if logging fails


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT APPLICANT
# ─────────────────────────────────────────────────────────────────────────────

def add_student_applicant(conn, args):
    first_name = getattr(args, "first_name", None)
    last_name = getattr(args, "last_name", None)
    date_of_birth = getattr(args, "date_of_birth", None)
    company_id = getattr(args, "company_id", None)
    application_date = getattr(args, "application_date", None) or _now_iso()[:10]

    if not first_name:
        err("--first-name is required")
    if not last_name:
        err("--last-name is required")
    if not date_of_birth:
        err("--date-of-birth is required")
    try:
        dob = date.fromisoformat(date_of_birth)
        if dob > date.today():
            err(f"--date-of-birth cannot be in the future: {date_of_birth}")
    except (ValueError, TypeError):
        err(f"Invalid date-of-birth format: {date_of_birth}. Use YYYY-MM-DD")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    gender = getattr(args, "gender", None) or ""
    if gender and gender not in VALID_GENDERS:
        err(f"--gender must be one of: {', '.join(g for g in VALID_GENDERS if g)}")

    applying_for_program_id = getattr(args, "applying_for_program_id", None)
    if applying_for_program_id:
        if not conn.execute("SELECT id FROM educlaw_program WHERE id = ?",
                            (applying_for_program_id,)).fetchone():
            err(f"Program {applying_for_program_id} not found")

    applying_for_term_id = getattr(args, "applying_for_term_id", None)
    if applying_for_term_id:
        if not conn.execute("SELECT id FROM educlaw_academic_term WHERE id = ?",
                            (applying_for_term_id,)).fetchone():
            err(f"Academic term {applying_for_term_id} not found")

    naming = get_next_name(conn, "educlaw_student_applicant", company_id=company_id)
    applicant_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_student_applicant
               (id, naming_series, first_name, middle_name, last_name, date_of_birth,
                gender, email, phone, address, applying_for_program_id, applying_for_term_id,
                previous_school, previous_school_address, transfer_records,
                application_date, status, review_notes, acceptance_deadline,
                guardian_info, documents, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (applicant_id, naming, first_name,
             getattr(args, "middle_name", None) or "",
             last_name, date_of_birth, gender,
             getattr(args, "email", None) or "",
             getattr(args, "phone", None) or "",
             getattr(args, "address", None) or "{}",
             applying_for_program_id, applying_for_term_id,
             getattr(args, "previous_school", None) or "",
             getattr(args, "previous_school_address", None) or "",
             getattr(args, "transfer_records", None) or "",
             application_date, "applied", "", "",
             getattr(args, "guardian_info", None) or "[]",
             getattr(args, "documents", None) or "[]",
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Applicant creation failed: {e}")

    audit(conn, SKILL, "add-student-applicant", "educlaw_student_applicant", applicant_id,
          new_values={"naming_series": naming, "first_name": first_name, "last_name": last_name})
    conn.commit()
    ok({"id": applicant_id, "naming_series": naming, "first_name": first_name,
        "last_name": last_name, "applicant_status": "applied"})


def update_student_applicant(conn, args):
    applicant_id = getattr(args, "applicant_id", None)
    if not applicant_id:
        err("--applicant-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_student_applicant WHERE id = ?", (applicant_id,)
    ).fetchone()
    if not row:
        err(f"Applicant {applicant_id} not found")

    r = dict(row)
    if r["status"] == "enrolled":
        err("Cannot update an enrolled applicant — student record already created")

    updates, params, changed = [], [], []

    for field in ("first_name", "middle_name", "last_name", "email", "phone",
                  "previous_school", "previous_school_address", "transfer_records",
                  "acceptance_deadline", "review_notes"):
        val = getattr(args, field, None)
        if val is not None:
            updates.append(f"{field} = ?"); params.append(val); changed.append(field)

    if getattr(args, "date_of_birth", None) is not None:
        updates.append("date_of_birth = ?"); params.append(args.date_of_birth)
        changed.append("date_of_birth")
    if getattr(args, "gender", None) is not None:
        if args.gender not in VALID_GENDERS:
            err(f"--gender must be one of: {', '.join(g for g in VALID_GENDERS if g)}")
        updates.append("gender = ?"); params.append(args.gender); changed.append("gender")
    if getattr(args, "address", None) is not None:
        updates.append("address = ?"); params.append(args.address); changed.append("address")
    if getattr(args, "guardian_info", None) is not None:
        updates.append("guardian_info = ?"); params.append(args.guardian_info)
        changed.append("guardian_info")
    if getattr(args, "documents", None) is not None:
        updates.append("documents = ?"); params.append(args.documents); changed.append("documents")
    if getattr(args, "applying_for_program_id", None) is not None:
        if not conn.execute("SELECT id FROM educlaw_program WHERE id = ?",
                            (args.applying_for_program_id,)).fetchone():
            err(f"Program {args.applying_for_program_id} not found")
        updates.append("applying_for_program_id = ?"); params.append(args.applying_for_program_id)
        changed.append("applying_for_program_id")
    if getattr(args, "applying_for_term_id", None) is not None:
        if not conn.execute("SELECT id FROM educlaw_academic_term WHERE id = ?",
                            (args.applying_for_term_id,)).fetchone():
            err(f"Academic term {args.applying_for_term_id} not found")
        updates.append("applying_for_term_id = ?"); params.append(args.applying_for_term_id)
        changed.append("applying_for_term_id")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(applicant_id)
    conn.execute(
        f"UPDATE educlaw_student_applicant SET {', '.join(updates)} WHERE id = ?", params
    )
    audit(conn, SKILL, "update-student-applicant", "educlaw_student_applicant", applicant_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": applicant_id, "updated_fields": changed})


def get_applicant(conn, args):
    applicant_id = getattr(args, "applicant_id", None)
    naming_series = getattr(args, "naming_series", None)

    if not applicant_id and not naming_series:
        err("--applicant-id or --naming-series is required")

    if applicant_id:
        row = conn.execute(
            "SELECT * FROM educlaw_student_applicant WHERE id = ?", (applicant_id,)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM educlaw_student_applicant WHERE naming_series = ?", (naming_series,)
        ).fetchone()

    if not row:
        err("Applicant not found")

    data = dict(row)
    for field in ("address", "guardian_info", "documents"):
        try:
            if data.get(field):
                data[field] = json.loads(data[field])
        except Exception:
            pass
    ok(data)


def list_applicants(conn, args):
    query = "SELECT * FROM educlaw_student_applicant WHERE 1=1"
    params = []

    if getattr(args, "applicant_status", None):
        query += " AND status = ?"; params.append(args.applicant_status)
    if getattr(args, "applying_for_term_id", None):
        query += " AND applying_for_term_id = ?"; params.append(args.applying_for_term_id)
    if getattr(args, "applying_for_program_id", None):
        query += " AND applying_for_program_id = ?"; params.append(args.applying_for_program_id)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY application_date DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"applicants": [dict(r) for r in rows], "count": len(rows)})


def review_applicant(conn, args):
    applicant_id = getattr(args, "applicant_id", None)
    new_status = getattr(args, "applicant_status", None)
    reviewed_by = getattr(args, "reviewed_by", None)

    if not applicant_id:
        err("--applicant-id is required")
    if not new_status:
        err("--applicant-status is required")
    if new_status not in VALID_APPLICANT_STATUSES:
        err(f"--applicant-status must be one of: {', '.join(VALID_APPLICANT_STATUSES)}")
    if not reviewed_by:
        err("--reviewed-by is required")

    row = conn.execute(
        "SELECT * FROM educlaw_student_applicant WHERE id = ?", (applicant_id,)
    ).fetchone()
    if not row:
        err(f"Applicant {applicant_id} not found")

    r = dict(row)
    if r["status"] == "enrolled":
        err("Cannot review an enrolled applicant")

    now = _now_iso()
    conn.execute(
        """UPDATE educlaw_student_applicant
           SET status = ?, reviewed_by = ?, review_date = ?,
               review_notes = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (new_status, reviewed_by, now[:10],
         getattr(args, "review_notes", None) or r.get("review_notes", ""),
         applicant_id)
    )

    if new_status == "accepted":
        notif_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_notification
               (id, recipient_type, recipient_id, notification_type, title, message,
                reference_type, reference_id, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (notif_id, "student", applicant_id, "acceptance",
             "Application Accepted",
             f"Congratulations! Your application {r['naming_series']} has been accepted.",
             "educlaw_student_applicant", applicant_id, r["company_id"], now, reviewed_by)
        )

    audit(conn, SKILL, "review-applicant", "educlaw_student_applicant", applicant_id,
          new_values={"old_status": r["status"], "new_status": new_status})
    conn.commit()
    ok({"id": applicant_id, "applicant_status": new_status, "reviewed_by": reviewed_by})


def convert_applicant_to_student(conn, args):
    applicant_id = getattr(args, "applicant_id", None)
    company_id = getattr(args, "company_id", None)

    if not applicant_id:
        err("--applicant-id is required")
    if not company_id:
        err("--company-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_student_applicant WHERE id = ?", (applicant_id,)
    ).fetchone()
    if not row:
        err(f"Applicant {applicant_id} not found")

    r = dict(row)
    if r["status"] not in ("accepted", "confirmed"):
        err(f"Applicant must be accepted or confirmed (current: {r['status']})")

    existing = conn.execute(
        "SELECT id FROM educlaw_student WHERE student_applicant_id = ?", (applicant_id,)
    ).fetchone()
    if existing:
        err(f"Applicant already converted to student {existing['id']}")

    enrollment_date = getattr(args, "enrollment_date", None) or _now_iso()[:10]
    coppa = 1 if _is_coppa_applicable(r["date_of_birth"], enrollment_date) else 0

    naming = get_next_name(conn, "educlaw_student", company_id=company_id)
    student_id = str(uuid.uuid4())

    mid = r.get("middle_name", "") or ""
    full_name = f"{r['first_name']} {mid} {r['last_name']}".replace("  ", " ").strip()
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_student
               (id, naming_series, first_name, middle_name, last_name, full_name,
                date_of_birth, gender, email, phone, address, emergency_contact,
                student_applicant_id, current_program_id, grade_level, cohort_year,
                cumulative_gpa, total_credits_earned, academic_standing, status,
                registration_hold, directory_info_opt_out, is_coppa_applicable,
                coppa_consent_type, coppa_consent_date, enrollment_date,
                company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student_id, naming, r["first_name"], mid, r["last_name"],
             full_name, r["date_of_birth"], r.get("gender", ""), r.get("email", ""),
             r.get("phone", ""), r.get("address", "{}"),
             getattr(args, "emergency_contact", None) or "{}",
             applicant_id, r.get("applying_for_program_id"),
             getattr(args, "grade_level", None) or "",
             int(getattr(args, "cohort_year", None) or 0),
             "", "0", "good", "active",
             0, int(getattr(args, "directory_info_opt_out", None) or 0),
             coppa, "", "", enrollment_date,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Student creation failed: {e}")

    conn.execute(
        "UPDATE educlaw_student_applicant SET status = 'enrolled', updated_at = datetime('now') WHERE id = ?",
        (applicant_id,)
    )
    audit(conn, SKILL, "convert-applicant-to-student", "educlaw_student", student_id,
          new_values={"naming_series": naming, "applicant_id": applicant_id})
    conn.commit()
    ok({"id": student_id, "naming_series": naming, "full_name": full_name,
        "applicant_id": applicant_id, "is_coppa_applicable": coppa})


def add_student(conn, args):
    first_name = getattr(args, "first_name", None)
    last_name = getattr(args, "last_name", None)
    date_of_birth = getattr(args, "date_of_birth", None)
    company_id = getattr(args, "company_id", None)

    if not first_name:
        err("--first-name is required")
    if not last_name:
        err("--last-name is required")
    if not date_of_birth:
        err("--date-of-birth is required")
    try:
        dob = date.fromisoformat(date_of_birth)
        if dob > date.today():
            err(f"--date-of-birth cannot be in the future: {date_of_birth}")
    except (ValueError, TypeError):
        err(f"Invalid date-of-birth format: {date_of_birth}. Use YYYY-MM-DD")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    gender = getattr(args, "gender", None) or ""
    if gender and gender not in VALID_GENDERS:
        err(f"--gender must be one of: {', '.join(g for g in VALID_GENDERS if g)}")

    current_program_id = getattr(args, "current_program_id", None)
    if current_program_id:
        if not conn.execute("SELECT id FROM educlaw_program WHERE id = ?",
                            (current_program_id,)).fetchone():
            err(f"Program {current_program_id} not found")

    enrollment_date = getattr(args, "enrollment_date", None) or _now_iso()[:10]
    coppa = 1 if _is_coppa_applicable(date_of_birth, enrollment_date) else 0

    naming = get_next_name(conn, "educlaw_student", company_id=company_id)
    student_id = str(uuid.uuid4())

    middle_name = getattr(args, "middle_name", None) or ""
    full_name = f"{first_name} {middle_name} {last_name}".replace("  ", " ").strip()
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_student
               (id, naming_series, first_name, middle_name, last_name, full_name,
                date_of_birth, gender, email, phone, address, emergency_contact,
                student_applicant_id, current_program_id, grade_level, cohort_year,
                cumulative_gpa, total_credits_earned, academic_standing, status,
                registration_hold, directory_info_opt_out, is_coppa_applicable,
                coppa_consent_type, coppa_consent_date, enrollment_date,
                company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student_id, naming, first_name, middle_name, last_name, full_name,
             date_of_birth, gender,
             getattr(args, "email", None) or "",
             getattr(args, "phone", None) or "",
             getattr(args, "address", None) or "{}",
             getattr(args, "emergency_contact", None) or "{}",
             None, current_program_id,
             getattr(args, "grade_level", None) or "",
             int(getattr(args, "cohort_year", None) or 0),
             "", "0", "good", "active",
             0, int(getattr(args, "directory_info_opt_out", None) or 0),
             coppa, "", "", enrollment_date,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Student creation failed: {e}")

    audit(conn, SKILL, "add-student", "educlaw_student", student_id,
          new_values={"naming_series": naming, "first_name": first_name, "last_name": last_name})
    conn.commit()
    ok({"id": student_id, "naming_series": naming, "full_name": full_name,
        "is_coppa_applicable": coppa})


def update_student(conn, args):
    student_id = getattr(args, "student_id", None)
    if not student_id:
        err("--student-id is required")

    row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not row:
        err(f"Student {student_id} not found")

    r = dict(row)
    updates, params, changed = [], [], []

    for field in ("first_name", "middle_name", "last_name", "email", "phone",
                  "grade_level", "photo"):
        val = getattr(args, field, None)
        if val is not None:
            updates.append(f"{field} = ?"); params.append(val); changed.append(field)

    if getattr(args, "address", None) is not None:
        updates.append("address = ?"); params.append(args.address); changed.append("address")
    if getattr(args, "emergency_contact", None) is not None:
        updates.append("emergency_contact = ?"); params.append(args.emergency_contact)
        changed.append("emergency_contact")
    if getattr(args, "academic_standing", None) is not None:
        if args.academic_standing not in VALID_ACADEMIC_STANDINGS:
            err(f"--academic-standing must be one of: {', '.join(VALID_ACADEMIC_STANDINGS)}")
        updates.append("academic_standing = ?"); params.append(args.academic_standing)
        changed.append("academic_standing")
    if getattr(args, "current_program_id", None) is not None:
        if not conn.execute("SELECT id FROM educlaw_program WHERE id = ?",
                            (args.current_program_id,)).fetchone():
            err(f"Program {args.current_program_id} not found")
        updates.append("current_program_id = ?"); params.append(args.current_program_id)
        changed.append("current_program_id")
    if getattr(args, "registration_hold", None) is not None:
        updates.append("registration_hold = ?"); params.append(int(args.registration_hold))
        changed.append("registration_hold")
    if getattr(args, "directory_info_opt_out", None) is not None:
        updates.append("directory_info_opt_out = ?")
        params.append(int(args.directory_info_opt_out))
        changed.append("directory_info_opt_out")
    if getattr(args, "cohort_year", None) is not None:
        updates.append("cohort_year = ?"); params.append(int(args.cohort_year))
        changed.append("cohort_year")

    if not changed:
        err("No fields to update")

    # Recompute full_name if name changed
    if any(f in changed for f in ("first_name", "middle_name", "last_name")):
        new_first = getattr(args, "first_name", None) or r["first_name"]
        new_mid = getattr(args, "middle_name", None) or r.get("middle_name", "") or ""
        new_last = getattr(args, "last_name", None) or r["last_name"]
        full_name = f"{new_first} {new_mid} {new_last}".replace("  ", " ").strip()
        updates.append("full_name = ?"); params.append(full_name)

    updates.append("updated_at = datetime('now')")
    params.append(student_id)
    conn.execute(f"UPDATE educlaw_student SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-student", "educlaw_student", student_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": student_id, "updated_fields": changed})


def get_student(conn, args):
    student_id = getattr(args, "student_id", None)
    if not student_id:
        err("--student-id is required")

    row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not row:
        err(f"Student {student_id} not found")

    data = dict(row)
    data.pop("ssn_encrypted", None)  # Never expose encrypted SSN

    for field in ("address", "emergency_contact"):
        try:
            if data.get(field):
                data[field] = json.loads(data[field])
        except Exception:
            pass

    guardians = conn.execute(
        """SELECT g.id, g.first_name, g.last_name, g.full_name, g.email, g.phone,
                  sg.relationship, sg.has_custody, sg.can_pickup,
                  sg.receives_communications, sg.is_primary_contact, sg.is_emergency_contact
           FROM educlaw_guardian g
           JOIN educlaw_student_guardian sg ON sg.guardian_id = g.id
           WHERE sg.student_id = ?""",
        (student_id,)
    ).fetchall()
    data["guardians"] = [dict(g) for g in guardians]

    # Auto-log FERPA data access
    user_id = getattr(args, "user_id", None) or "system"
    access_reason = getattr(args, "access_reason", None) or "Administrative access"
    company_id = data.get("company_id", "")
    _log_data_access_internal(conn, user_id, student_id, "demographics", "view",
                               access_reason, 0, company_id)
    conn.commit()
    ok(data)


def list_students(conn, args):
    query = ("SELECT id, naming_series, first_name, last_name, full_name, email, grade_level, "
             "current_program_id, academic_standing, status, registration_hold, company_id "
             "FROM educlaw_student WHERE 1=1")
    params = []

    if getattr(args, "student_status", None):
        query += " AND status = ?"; params.append(args.student_status)
    if getattr(args, "current_program_id", None):
        query += " AND current_program_id = ?"; params.append(args.current_program_id)
    if getattr(args, "grade_level", None):
        query += " AND grade_level = ?"; params.append(args.grade_level)
    if getattr(args, "academic_standing", None):
        query += " AND academic_standing = ?"; params.append(args.academic_standing)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY last_name, first_name"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"students": [dict(r) for r in rows], "count": len(rows)})


def change_student_status(conn, args):
    student_id = getattr(args, "student_id", None)
    new_status = getattr(args, "student_status", None)
    reason = getattr(args, "reason", None)

    if not student_id:
        err("--student-id is required")
    if not new_status:
        err("--student-status is required")
    if new_status not in VALID_STUDENT_STATUSES:
        err(f"--student-status must be one of: {', '.join(VALID_STUDENT_STATUSES)}")
    if not reason:
        err("--reason is required for status change")

    row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not row:
        err(f"Student {student_id} not found")

    r = dict(row)
    conn.execute(
        "UPDATE educlaw_student SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (new_status, student_id)
    )
    audit(conn, SKILL, "change-student-status", "educlaw_student", student_id,
          new_values={"old_status": r["status"], "new_status": new_status, "reason": reason})
    conn.commit()
    ok({"id": student_id, "old_status": r["status"], "student_status": new_status, "reason": reason})


def graduate_student(conn, args):
    student_id = getattr(args, "student_id", None)
    graduation_date = getattr(args, "graduation_date", None) or _now_iso()[:10]

    if not student_id:
        err("--student-id is required")

    row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not row:
        err(f"Student {student_id} not found")

    r = dict(row)
    if r["status"] != "active":
        err(f"Student must be active to graduate (current: {r['status']})")

    conn.execute(
        """UPDATE educlaw_student
           SET status = 'graduated', graduation_date = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (graduation_date, student_id)
    )

    # Complete active program enrollment
    prog_enr = conn.execute(
        "SELECT id FROM educlaw_program_enrollment WHERE student_id = ? AND enrollment_status = 'active'",
        (student_id,)
    ).fetchone()
    if prog_enr:
        conn.execute(
            """UPDATE educlaw_program_enrollment
               SET enrollment_status = 'completed', updated_at = datetime('now')
               WHERE id = ?""",
            (prog_enr["id"],)
        )

    audit(conn, SKILL, "graduate-student", "educlaw_student", student_id,
          new_values={"graduation_date": graduation_date})
    conn.commit()
    ok({"id": student_id, "student_status": "graduated", "graduation_date": graduation_date})


# ─────────────────────────────────────────────────────────────────────────────
# GUARDIAN
# ─────────────────────────────────────────────────────────────────────────────

def add_guardian(conn, args):
    first_name = getattr(args, "first_name", None)
    last_name = getattr(args, "last_name", None)
    relationship = getattr(args, "relationship", None)
    company_id = getattr(args, "company_id", None)
    phone = getattr(args, "phone", None)

    if not first_name:
        err("--first-name is required")
    if not last_name:
        err("--last-name is required")
    if not relationship:
        err("--relationship is required")
    if relationship not in VALID_RELATIONSHIPS:
        err(f"--relationship must be one of: {', '.join(VALID_RELATIONSHIPS)}")
    if not company_id:
        err("--company-id is required")
    if not phone:
        err("--phone is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    guardian_id = str(uuid.uuid4())
    full_name = f"{first_name} {last_name}".strip()
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_guardian
               (id, first_name, last_name, full_name, relationship, email, phone,
                alternate_phone, address, occupation, employer, customer_id, company_id,
                created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (guardian_id, first_name, last_name, full_name, relationship,
             getattr(args, "email", None) or "",
             phone,
             getattr(args, "alternate_phone", None) or "",
             getattr(args, "address", None) or "{}",
             getattr(args, "occupation", None) or "",
             getattr(args, "employer", None) or "",
             None,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Guardian creation failed: {e}")

    # Link to student if student_id provided
    student_id = getattr(args, "student_id", None)
    if student_id:
        if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
            err(f"Student {student_id} not found")
        link_id = str(uuid.uuid4())
        try:
            conn.execute(
                """INSERT INTO educlaw_student_guardian
                   (id, student_id, guardian_id, relationship, has_custody, can_pickup,
                    receives_communications, is_primary_contact, is_emergency_contact,
                    created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (link_id, student_id, guardian_id, relationship,
                 int(getattr(args, "has_custody", None) or 1),
                 int(getattr(args, "can_pickup", None) or 1),
                 int(getattr(args, "receives_communications", None) or 1),
                 int(getattr(args, "is_primary_contact", None) or 0),
                 int(getattr(args, "is_emergency_contact", None) or 0),
                 now, getattr(args, "user_id", None) or "")
            )
        except sqlite3.IntegrityError:
            pass

    audit(conn, SKILL, "add-guardian", "educlaw_guardian", guardian_id,
          new_values={"first_name": first_name, "last_name": last_name})
    conn.commit()
    ok({"id": guardian_id, "full_name": full_name, "relationship": relationship,
        "student_id": student_id})


def update_guardian(conn, args):
    guardian_id = getattr(args, "guardian_id", None)
    if not guardian_id:
        err("--guardian-id is required")

    row = conn.execute("SELECT * FROM educlaw_guardian WHERE id = ?", (guardian_id,)).fetchone()
    if not row:
        err(f"Guardian {guardian_id} not found")

    r = dict(row)
    updates, params, changed = [], [], []

    for field in ("first_name", "last_name", "email", "phone", "alternate_phone",
                  "occupation", "employer"):
        val = getattr(args, field, None)
        if val is not None:
            updates.append(f"{field} = ?"); params.append(val); changed.append(field)

    if getattr(args, "address", None) is not None:
        updates.append("address = ?"); params.append(args.address); changed.append("address")
    if getattr(args, "relationship", None) is not None:
        if args.relationship not in VALID_RELATIONSHIPS:
            err(f"--relationship must be one of: {', '.join(VALID_RELATIONSHIPS)}")
        updates.append("relationship = ?"); params.append(args.relationship)
        changed.append("relationship")

    if not changed:
        err("No fields to update")

    if any(f in changed for f in ("first_name", "last_name")):
        new_first = getattr(args, "first_name", None) or r["first_name"]
        new_last = getattr(args, "last_name", None) or r["last_name"]
        updates.append("full_name = ?")
        params.append(f"{new_first} {new_last}".strip())

    updates.append("updated_at = datetime('now')")
    params.append(guardian_id)
    conn.execute(f"UPDATE educlaw_guardian SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-guardian", "educlaw_guardian", guardian_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": guardian_id, "updated_fields": changed})


def get_guardian(conn, args):
    guardian_id = getattr(args, "guardian_id", None)
    if not guardian_id:
        err("--guardian-id is required")

    row = conn.execute("SELECT * FROM educlaw_guardian WHERE id = ?", (guardian_id,)).fetchone()
    if not row:
        err(f"Guardian {guardian_id} not found")

    data = dict(row)
    try:
        if data.get("address"):
            data["address"] = json.loads(data["address"])
    except Exception:
        pass

    linked_students = conn.execute(
        """SELECT s.id, s.naming_series, s.full_name, sg.relationship, sg.is_primary_contact
           FROM educlaw_student s
           JOIN educlaw_student_guardian sg ON sg.student_id = s.id
           WHERE sg.guardian_id = ?""",
        (guardian_id,)
    ).fetchall()
    data["linked_students"] = [dict(s) for s in linked_students]
    ok(data)


def list_guardians(conn, args):
    student_id = getattr(args, "student_id", None)

    if student_id:
        query = """SELECT g.* FROM educlaw_guardian g
                   JOIN educlaw_student_guardian sg ON sg.guardian_id = g.id
                   WHERE sg.student_id = ?"""
        params = [student_id]
    else:
        query = "SELECT * FROM educlaw_guardian WHERE 1=1"
        params = []
        if getattr(args, "company_id", None):
            query += " AND company_id = ?"; params.append(args.company_id)
        query += " ORDER BY last_name, first_name"

    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"guardians": [dict(r) for r in rows], "count": len(rows)})


def link_guardian_to_student(conn, args):
    guardian_id = getattr(args, "guardian_id", None)
    student_id = getattr(args, "student_id", None)
    relationship = getattr(args, "relationship", None)

    if not guardian_id:
        err("--guardian-id is required")
    if not student_id:
        err("--student-id is required")
    if not relationship:
        err("--relationship is required")
    if relationship not in VALID_RELATIONSHIPS:
        err(f"--relationship must be one of: {', '.join(VALID_RELATIONSHIPS)}")

    if not conn.execute("SELECT id FROM educlaw_guardian WHERE id = ?", (guardian_id,)).fetchone():
        err(f"Guardian {guardian_id} not found")
    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")

    existing = conn.execute(
        "SELECT id FROM educlaw_student_guardian WHERE student_id = ? AND guardian_id = ?",
        (student_id, guardian_id)
    ).fetchone()
    if existing:
        err(f"Guardian {guardian_id} is already linked to student {student_id}")

    link_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_student_guardian
           (id, student_id, guardian_id, relationship, has_custody, can_pickup,
            receives_communications, is_primary_contact, is_emergency_contact,
            created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (link_id, student_id, guardian_id, relationship,
         int(getattr(args, "has_custody", None) or 1),
         int(getattr(args, "can_pickup", None) or 1),
         int(getattr(args, "receives_communications", None) or 1),
         int(getattr(args, "is_primary_contact", None) or 0),
         int(getattr(args, "is_emergency_contact", None) or 0),
         now, getattr(args, "user_id", None) or "")
    )
    audit(conn, SKILL, "link-guardian-to-student", "educlaw_student_guardian", link_id,
          new_values={"student_id": student_id, "guardian_id": guardian_id})
    conn.commit()
    ok({"id": link_id, "student_id": student_id, "guardian_id": guardian_id,
        "relationship": relationship})


# ─────────────────────────────────────────────────────────────────────────────
# FERPA COMPLIANCE
# ─────────────────────────────────────────────────────────────────────────────

def log_data_access(conn, args):
    user_id = getattr(args, "user_id", None)
    student_id = getattr(args, "student_id", None)
    data_category = getattr(args, "data_category", None)
    access_type = getattr(args, "access_type", None)
    company_id = getattr(args, "company_id", None)

    if not user_id:
        err("--user-id is required")
    if not student_id:
        err("--student-id is required")
    if not data_category:
        err("--data-category is required")
    if data_category not in VALID_DATA_CATEGORIES:
        err(f"--data-category must be one of: {', '.join(VALID_DATA_CATEGORIES)}")
    if not access_type:
        err("--access-type is required")
    if access_type not in VALID_ACCESS_TYPES:
        err(f"--access-type must be one of: {', '.join(VALID_ACCESS_TYPES)}")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")

    log_id = str(uuid.uuid4())
    now = _now_iso()
    is_emergency = int(getattr(args, "is_emergency_access", None) or 0)

    conn.execute(
        """INSERT INTO educlaw_data_access_log
           (id, user_id, student_id, data_category, access_type, access_reason,
            is_emergency_access, ip_address, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (log_id, user_id, student_id, data_category, access_type,
         getattr(args, "access_reason", None) or "",
         is_emergency,
         getattr(args, "ip_address", None) or "",
         company_id, now, user_id)
    )
    conn.commit()
    ok({"id": log_id, "user_id": user_id, "student_id": student_id,
        "data_category": data_category, "access_type": access_type})


def add_consent_record(conn, args):
    student_id = getattr(args, "student_id", None)
    consent_type = getattr(args, "consent_type", None)
    granted_by = getattr(args, "granted_by", None)
    consent_date = getattr(args, "consent_date", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not consent_type:
        err("--consent-type is required")
    if consent_type not in VALID_CONSENT_TYPES:
        err(f"--consent-type must be one of: {', '.join(VALID_CONSENT_TYPES)}")
    if not granted_by:
        err("--granted-by is required")
    if not consent_date:
        err("--consent-date is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")

    consent_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_consent_record
           (id, student_id, consent_type, granted_by, granted_by_relationship,
            consent_date, expiry_date, is_revoked, revoked_date,
            third_party_name, purpose, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (consent_id, student_id, consent_type, granted_by,
         getattr(args, "granted_by_relationship", None) or "",
         consent_date,
         getattr(args, "expiry_date", None) or "",
         0, "",
         getattr(args, "third_party_name", None) or "",
         getattr(args, "purpose", None) or "",
         company_id, now, now, getattr(args, "user_id", None) or "")
    )
    audit(conn, SKILL, "add-consent-record", "educlaw_consent_record", consent_id,
          new_values={"consent_type": consent_type, "student_id": student_id})
    conn.commit()
    ok({"id": consent_id, "consent_type": consent_type, "student_id": student_id})


def revoke_consent(conn, args):
    consent_id = getattr(args, "consent_id", None)
    if not consent_id:
        err("--consent-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_consent_record WHERE id = ?", (consent_id,)
    ).fetchone()
    if not row:
        err(f"Consent record {consent_id} not found")

    r = dict(row)
    if r["is_revoked"]:
        err("Consent record is already revoked")

    revoked_date = getattr(args, "revoked_date", None) or _now_iso()[:10]
    conn.execute(
        """UPDATE educlaw_consent_record
           SET is_revoked = 1, revoked_date = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (revoked_date, consent_id)
    )
    audit(conn, SKILL, "revoke-consent", "educlaw_consent_record", consent_id,
          new_values={"is_revoked": 1, "revoked_date": revoked_date})
    conn.commit()
    ok({"id": consent_id, "is_revoked": 1, "revoked_date": revoked_date})


def export_student_record(conn, args):
    student_id = getattr(args, "student_id", None)
    user_id = getattr(args, "user_id", None) or "system"
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not company_id:
        err("--company-id is required")

    row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not row:
        err(f"Student {student_id} not found")

    student = dict(row)
    student.pop("ssn_encrypted", None)

    enrollments = conn.execute(
        """SELECT ce.*, sec.naming_series as section_series, sec.section_number,
                  c.course_code, c.name as course_name, c.credit_hours,
                  at.name as term_name, at.start_date as term_start
           FROM educlaw_course_enrollment ce
           JOIN educlaw_section sec ON sec.id = ce.section_id
           JOIN educlaw_course c ON c.id = sec.course_id
           JOIN educlaw_academic_term at ON at.id = sec.academic_term_id
           WHERE ce.student_id = ?
           ORDER BY at.start_date""",
        (student_id,)
    ).fetchall()

    attendance = conn.execute(
        """SELECT attendance_date, attendance_status, late_minutes, comments, source
           FROM educlaw_student_attendance
           WHERE student_id = ? ORDER BY attendance_date DESC LIMIT 1000""",
        (student_id,)
    ).fetchall()

    consent = conn.execute(
        "SELECT * FROM educlaw_consent_record WHERE student_id = ?", (student_id,)
    ).fetchall()

    now = _now_iso()
    export_log_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_data_access_log
           (id, user_id, student_id, data_category, access_type, access_reason,
            is_emergency_access, ip_address, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (export_log_id, user_id, student_id, "grades", "export",
         "FERPA education record export request",
         0, "", company_id, now, user_id)
    )
    conn.commit()

    ok({
        "student": student,
        "course_enrollments": [dict(e) for e in enrollments],
        "attendance_records": [dict(a) for a in attendance],
        "consent_records": [dict(c) for c in consent],
        "exported_at": now,
        "exported_by": user_id,
        "access_log_id": export_log_id,
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-student-applicant": add_student_applicant,
    "update-student-applicant": update_student_applicant,
    "get-applicant": get_applicant,
    "list-applicants": list_applicants,
    "approve-applicant": review_applicant,
    "convert-applicant-to-student": convert_applicant_to_student,
    "add-student": add_student,
    "update-student": update_student,
    "get-student": get_student,
    "list-students": list_students,
    "update-student-status": change_student_status,
    "complete-graduation": graduate_student,
    "add-guardian": add_guardian,
    "update-guardian": update_guardian,
    "get-guardian": get_guardian,
    "list-guardians": list_guardians,
    "assign-guardian": link_guardian_to_student,
    "record-data-access": log_data_access,
    "add-consent-record": add_consent_record,
    "cancel-consent": revoke_consent,
    "generate-student-record": export_student_record,
}
