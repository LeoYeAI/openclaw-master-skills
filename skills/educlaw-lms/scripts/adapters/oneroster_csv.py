"""EduClaw LMS Integration — OneRoster 1.1 CSV adapter.

OneRoster 1.1 IMS Global Standard CSV export.
Spec: https://www.imsglobal.org/oneroster-v11-final-specification

This adapter generates the 8 required CSV files and zips them.
No network calls — pure file generation from local SQLite data.

CSV files produced:
  orgs.csv, academicSessions.csv, courses.csv, classes.csv,
  users.csv, enrollments.csv, lineItems.csv, results.csv
"""
import csv
import io
import json
import os
import zipfile
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso_date_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def generate_oneroster_export(conn, company_id, academic_term_id,
                               output_dir, include_grades=False,
                               term_name="term"):
    """Generate OneRoster 1.1 CSV package.

    Args:
        conn: SQLite connection (with FK enforcement enabled).
        company_id: Institution company ID.
        academic_term_id: Academic term to export.
        output_dir: Directory to write the output zip file.
        include_grades: If True, generate lineItems.csv and results.csv.
        term_name: Term name for use in zip filename.

    Returns:
        dict with keys: zip_path (str), files_generated (list), student_count (int).

    Raises:
        ValueError: If company_id or academic_term_id is invalid.
    """
    now_str = _now_iso()
    date_str = _iso_date_now()

    # ── Load core data ─────────────────────────────────────────────────────
    company = conn.execute(
        "SELECT id, name FROM company WHERE id = ?", (company_id,)
    ).fetchone()
    if not company:
        raise ValueError(f"Company {company_id} not found")
    company = dict(company)

    term = conn.execute(
        "SELECT * FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone()
    if not term:
        raise ValueError(f"Academic term {academic_term_id} not found")
    term = dict(term)

    # Sections in this term
    sections = conn.execute(
        """SELECT s.*, c.course_code, c.name as course_name, c.description,
                  c.credit_hours, c.grade_level,
                  i.id as instr_rec_id,
                  e.work_email as instructor_email,
                  e.first_name as instr_first, e.last_name as instr_last
           FROM educlaw_section s
           JOIN educlaw_course c ON c.id = s.course_id
           LEFT JOIN educlaw_instructor i ON i.id = s.instructor_id
           LEFT JOIN employee e ON e.id = i.employee_id
           WHERE s.academic_term_id = ? AND s.company_id = ?
           AND s.status NOT IN ('cancelled')""",
        (academic_term_id, company_id)
    ).fetchall()
    sections = [dict(r) for r in sections]

    section_ids = [s["id"] for s in sections]

    # Students (via enrollments)
    students_raw = []
    if section_ids:
        placeholders = ",".join("?" * len(section_ids))
        enrollments = conn.execute(
            f"""SELECT ce.*, st.first_name, st.last_name, st.email as student_email,
                       st.is_coppa_applicable, st.directory_info_opt_out,
                       st.grade_level as student_grade
                FROM educlaw_course_enrollment ce
                JOIN educlaw_student st ON st.id = ce.student_id
                WHERE ce.section_id IN ({placeholders})
                AND ce.enrollment_status IN ('enrolled','completed')""",
            section_ids
        ).fetchall()
        enrollments = [dict(r) for r in enrollments]
    else:
        enrollments = []

    # Unique students
    seen_students = {}
    for enr in enrollments:
        sid = enr["student_id"]
        if sid not in seen_students:
            seen_students[sid] = enr

    # Assessments (for lineItems)
    assessments = []
    if include_grades and section_ids:
        placeholders = ",".join("?" * len(section_ids))
        plans = conn.execute(
            f"SELECT id, section_id FROM educlaw_assessment_plan WHERE section_id IN ({placeholders})",
            section_ids
        ).fetchall()
        plan_ids = [r[0] for r in plans]
        plan_section_map = {r[0]: r[1] for r in plans}
        if plan_ids:
            pph = ",".join("?" * len(plan_ids))
            assessments = conn.execute(
                f"""SELECT a.*, ap.section_id
                    FROM educlaw_assessment a
                    JOIN educlaw_assessment_plan ap ON ap.id = a.assessment_plan_id
                    WHERE a.assessment_plan_id IN ({pph})""",
                plan_ids
            ).fetchall()
            assessments = [dict(r) for r in assessments]

    # Results
    results = []
    if include_grades and assessments:
        assess_ids = [a["id"] for a in assessments]
        arh = ",".join("?" * len(assess_ids))
        results = conn.execute(
            f"""SELECT ar.*, ar.assessment_id, ar.student_id
                FROM educlaw_assessment_result ar
                WHERE ar.assessment_id IN ({arh})""",
            assess_ids
        ).fetchall()
        results = [dict(r) for r in results]

    # ── Build CSV content ──────────────────────────────────────────────────

    csv_files = {}

    # 1. orgs.csv
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=[
        "sourcedId", "status", "dateLastModified", "name", "type",
        "identifier", "parentSourcedId"
    ])
    w.writeheader()
    w.writerow({
        "sourcedId": company_id,
        "status": "active",
        "dateLastModified": now_str,
        "name": company["name"],
        "type": "school",
        "identifier": company_id[:8],
        "parentSourcedId": "",
    })
    csv_files["orgs.csv"] = f.getvalue()

    # 2. academicSessions.csv
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=[
        "sourcedId", "status", "dateLastModified", "title", "type",
        "startDate", "endDate", "parentSourcedId", "schoolYear"
    ])
    w.writeheader()
    # Academic year row
    year_id = term.get("academic_year_id", "")
    if year_id:
        year_row = conn.execute(
            "SELECT * FROM educlaw_academic_year WHERE id = ?", (year_id,)
        ).fetchone()
        if year_row:
            year_row = dict(year_row)
            w.writerow({
                "sourcedId": year_id,
                "status": "active",
                "dateLastModified": now_str,
                "title": year_row.get("name", ""),
                "type": "schoolYear",
                "startDate": year_row.get("start_date", ""),
                "endDate": year_row.get("end_date", ""),
                "parentSourcedId": "",
                "schoolYear": year_row.get("name", "")[:4],
            })
    w.writerow({
        "sourcedId": academic_term_id,
        "status": "active",
        "dateLastModified": now_str,
        "title": term.get("name", ""),
        "type": "term",
        "startDate": term.get("start_date", ""),
        "endDate": term.get("end_date", ""),
        "parentSourcedId": year_id or "",
        "schoolYear": (term.get("start_date", "") or "")[:4],
    })
    csv_files["academicSessions.csv"] = f.getvalue()

    # 3. courses.csv — unique courses in term
    seen_courses = {}
    for s in sections:
        cid = s["course_id"]
        if cid not in seen_courses:
            seen_courses[cid] = s
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=[
        "sourcedId", "status", "dateLastModified", "schoolYearSourcedId",
        "title", "courseCode", "grades", "orgSourcedId", "subjects", "subjectCodes"
    ])
    w.writeheader()
    for cid, s in seen_courses.items():
        w.writerow({
            "sourcedId": cid,
            "status": "active",
            "dateLastModified": now_str,
            "schoolYearSourcedId": year_id or "",
            "title": s.get("course_name", ""),
            "courseCode": s.get("course_code", ""),
            "grades": s.get("grade_level", "") or "",
            "orgSourcedId": company_id,
            "subjects": "",
            "subjectCodes": "",
        })
    csv_files["courses.csv"] = f.getvalue()

    # 4. classes.csv
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=[
        "sourcedId", "status", "dateLastModified", "title", "grades",
        "courseSourcedId", "classType", "location", "schoolSourcedId",
        "termSourcedIds", "subjectCodes", "periods"
    ])
    w.writeheader()
    for s in sections:
        w.writerow({
            "sourcedId": s["id"],
            "status": "active",
            "dateLastModified": now_str,
            "title": f"{s.get('course_name','')} - {s.get('section_number','')}",
            "grades": s.get("grade_level", "") or "",
            "courseSourcedId": s["course_id"],
            "classType": "scheduled",
            "location": s.get("room_id", "") or "",
            "schoolSourcedId": company_id,
            "termSourcedIds": academic_term_id,
            "subjectCodes": "",
            "periods": "",
        })
    csv_files["classes.csv"] = f.getvalue()

    # 5. users.csv
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=[
        "sourcedId", "status", "dateLastModified", "enabledUser",
        "orgSourcedIds", "role", "username", "userIds", "givenName",
        "familyName", "middleName", "identifier", "email", "sms",
        "phone", "agentSourcedIds", "grades", "password"
    ])
    w.writeheader()
    # Students
    for sid, st in seen_students.items():
        is_coppa = int(st.get("is_coppa_applicable", 0) or 0)
        is_dir_restricted = int(st.get("directory_info_opt_out", 0) or 0)
        email = st.get("student_email", "") or ""
        username = email.split("@")[0] if "@" in email else sid[:8]
        w.writerow({
            "sourcedId": sid,
            "status": "active",
            "dateLastModified": now_str,
            "enabledUser": "true",
            "orgSourcedIds": company_id,
            "role": "student",
            "username": username,
            "userIds": "",
            "givenName": st.get("first_name", "") if not is_dir_restricted else "",
            "familyName": st.get("last_name", "") if not is_dir_restricted else "",
            "middleName": "",
            "identifier": sid,
            "email": email if not is_coppa else "",  # COPPA: no email for under-13
            "sms": "",
            "phone": "",
            "agentSourcedIds": "",
            "grades": st.get("student_grade", "") or "",
            "password": "",
        })
    # Instructors
    seen_instructors = {}
    for s in sections:
        iid = s.get("instr_rec_id")
        if iid and iid not in seen_instructors:
            seen_instructors[iid] = s
    for iid, s in seen_instructors.items():
        email = s.get("instructor_email", "") or ""
        username = email.split("@")[0] if "@" in email else iid[:8]
        w.writerow({
            "sourcedId": iid,
            "status": "active",
            "dateLastModified": now_str,
            "enabledUser": "true",
            "orgSourcedIds": company_id,
            "role": "teacher",
            "username": username,
            "userIds": "",
            "givenName": s.get("instr_first", "") or "",
            "familyName": s.get("instr_last", "") or "",
            "middleName": "",
            "identifier": iid,
            "email": email,
            "sms": "",
            "phone": "",
            "agentSourcedIds": "",
            "grades": "",
            "password": "",
        })
    csv_files["users.csv"] = f.getvalue()

    # 6. enrollments.csv
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=[
        "sourcedId", "status", "dateLastModified", "classSourcedId",
        "schoolSourcedId", "userSourcedId", "role", "primary", "beginDate", "endDate"
    ])
    w.writeheader()
    for enr in enrollments:
        w.writerow({
            "sourcedId": enr.get("id", ""),
            "status": "active",
            "dateLastModified": now_str,
            "classSourcedId": enr.get("section_id", ""),
            "schoolSourcedId": company_id,
            "userSourcedId": enr.get("student_id", ""),
            "role": "student",
            "primary": "true",
            "beginDate": enr.get("enrollment_date", ""),
            "endDate": enr.get("drop_date", "") or term.get("end_date", ""),
        })
    # Instructor enrollments
    for iid, s in seen_instructors.items():
        w.writerow({
            "sourcedId": f"instr_{iid}_{s['id']}",
            "status": "active",
            "dateLastModified": now_str,
            "classSourcedId": s["id"],
            "schoolSourcedId": company_id,
            "userSourcedId": iid,
            "role": "teacher",
            "primary": "true",
            "beginDate": term.get("start_date", ""),
            "endDate": term.get("end_date", ""),
        })
    csv_files["enrollments.csv"] = f.getvalue()

    # 7. lineItems.csv (optional)
    if include_grades and assessments:
        f = io.StringIO()
        w = csv.DictWriter(f, fieldnames=[
            "sourcedId", "status", "dateLastModified", "title", "description",
            "assignDate", "dueDate", "classSourcedId", "categorySourcedId",
            "gradingPeriodSourcedId", "resultValueMin", "resultValueMax"
        ])
        w.writeheader()
        for a in assessments:
            w.writerow({
                "sourcedId": a["id"],
                "status": "active",
                "dateLastModified": now_str,
                "title": a.get("name", ""),
                "description": a.get("description", "") or "",
                "assignDate": now_str[:10],
                "dueDate": a.get("due_date", "") or "",
                "classSourcedId": a.get("section_id", ""),
                "categorySourcedId": a.get("category_id", "") or "",
                "gradingPeriodSourcedId": academic_term_id,
                "resultValueMin": "0",
                "resultValueMax": a.get("max_points", "0") or "0",
            })
        csv_files["lineItems.csv"] = f.getvalue()

    # 8. results.csv (optional)
    if include_grades and results:
        f = io.StringIO()
        w = csv.DictWriter(f, fieldnames=[
            "sourcedId", "status", "dateLastModified", "lineItemSourcedId",
            "studentSourcedId", "scoreStatus", "score", "textScore",
            "scoreDate", "comment"
        ])
        w.writeheader()
        for r in results:
            is_exempt = int(r.get("is_exempt", 0) or 0)
            score_val = r.get("points_earned", "") or ""
            w.writerow({
                "sourcedId": r.get("id", ""),
                "status": "active",
                "dateLastModified": now_str,
                "lineItemSourcedId": r.get("assessment_id", ""),
                "studentSourcedId": r.get("student_id", ""),
                "scoreStatus": "exempt" if is_exempt else "fully graded",
                "score": score_val if not is_exempt else "",
                "textScore": "",
                "scoreDate": r.get("graded_at", "") or now_str[:10],
                "comment": r.get("comments", "") or "",
            })
        csv_files["results.csv"] = f.getvalue()

    # ── Zip all files ───────────────────────────────────────────────────────
    safe_term = "".join(c if c.isalnum() or c in "-_" else "_" for c in term_name)
    zip_filename = f"oneroster_{safe_term}_{date_str}.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in csv_files.items():
            zf.writestr(filename, content.encode("utf-8"))

    return {
        "zip_path": zip_path,
        "files_generated": list(csv_files.keys()),
        "student_count": len(seen_students),
        "section_count": len(sections),
        "enrollment_count": len(enrollments),
    }
