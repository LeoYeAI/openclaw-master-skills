"""EduClaw — communications domain module

Actions for communications: announcements (draft → publish → archive),
targeted notifications, progress reports, emergency alerts.

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

VALID_PRIORITIES = ("normal", "urgent", "emergency")
VALID_AUDIENCE_TYPES = ("all", "students", "guardians", "staff", "program", "section", "department", "grade_level")
VALID_ANNOUNCEMENT_STATUSES = ("draft", "published", "archived")
VALID_RECIPIENT_TYPES = ("student", "guardian", "employee")
VALID_NOTIFICATION_TYPES = ("grade_posted", "fee_due", "absence", "announcement",
                             "progress_report", "emergency", "acceptance", "enrollment_confirmed")
VALID_SENT_VIA = ("system", "email")


def _create_notification(conn, recipient_type, recipient_id, notification_type,
                          title, message, company_id, reference_type=None,
                          reference_id=None, sent_via="system"):
    """Internal helper to insert a single notification record."""
    now = _now_iso()
    notif_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_notification
           (id, recipient_type, recipient_id, notification_type, title, message,
            reference_type, reference_id, is_read, sent_via, sent_at, company_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)""",
        (notif_id, recipient_type, recipient_id, notification_type,
         title, message, reference_type, reference_id,
         sent_via, now, company_id, now)
    )
    return notif_id


def _get_audience_recipients(conn, audience_type, audience_filter_json, company_id):
    """Return list of (recipient_type, recipient_id) tuples for given audience."""
    recipients = []
    af = {}
    if audience_filter_json:
        try:
            af = json.loads(audience_filter_json) if isinstance(audience_filter_json, str) else audience_filter_json
        except (json.JSONDecodeError, TypeError):
            af = {}

    if audience_type in ("all", "students"):
        rows = conn.execute(
            "SELECT id FROM educlaw_student WHERE company_id = ? AND status = 'active'",
            (company_id,)
        ).fetchall()
        recipients.extend(("student", r["id"]) for r in rows)

    if audience_type in ("all", "guardians"):
        rows = conn.execute(
            """SELECT DISTINCT g.id FROM educlaw_guardian g
               JOIN educlaw_student_guardian sg ON sg.guardian_id = g.id
               JOIN educlaw_student s ON s.id = sg.student_id
               WHERE s.company_id = ? AND s.status = 'active'
               AND sg.receives_communications = 1""",
            (company_id,)
        ).fetchall()
        recipients.extend(("guardian", r["id"]) for r in rows)

    if audience_type in ("all", "staff"):
        rows = conn.execute(
            "SELECT id FROM employee WHERE company_id = ?",
            (company_id,)
        ).fetchall()
        recipients.extend(("employee", r["id"]) for r in rows)

    if audience_type == "program":
        program_id = af.get("program_id")
        if program_id:
            rows = conn.execute(
                """SELECT DISTINCT s.id FROM educlaw_student s
                   JOIN educlaw_program_enrollment pe ON pe.student_id = s.id
                   WHERE pe.program_id = ? AND pe.enrollment_status = 'active'
                   AND s.company_id = ?""",
                (program_id, company_id)
            ).fetchall()
            recipients.extend(("student", r["id"]) for r in rows)

    if audience_type == "section":
        section_id = af.get("section_id")
        if section_id:
            rows = conn.execute(
                """SELECT DISTINCT s.id FROM educlaw_student s
                   JOIN educlaw_course_enrollment ce ON ce.student_id = s.id
                   WHERE ce.section_id = ? AND ce.enrollment_status = 'enrolled'
                   AND s.company_id = ?""",
                (section_id, company_id)
            ).fetchall()
            recipients.extend(("student", r["id"]) for r in rows)

    if audience_type == "department":
        department_id = af.get("department_id")
        if department_id:
            rows = conn.execute(
                "SELECT id FROM employee WHERE department_id = ? AND company_id = ?",
                (department_id, company_id)
            ).fetchall()
            recipients.extend(("employee", r["id"]) for r in rows)

    if audience_type == "grade_level":
        grade_level = af.get("grade_level")
        if grade_level:
            rows = conn.execute(
                """SELECT id FROM educlaw_student
                   WHERE grade_level = ? AND company_id = ? AND status = 'active'""",
                (grade_level, company_id)
            ).fetchall()
            recipients.extend(("student", r["id"]) for r in rows)

    return recipients


# ─────────────────────────────────────────────────────────────────────────────
# ANNOUNCEMENTS
# ─────────────────────────────────────────────────────────────────────────────

def add_announcement(conn, args):
    """Create a new announcement in draft status."""
    title = getattr(args, "title", None)
    body = getattr(args, "body", None)
    company_id = getattr(args, "company_id", None)

    if not title:
        err("--title is required")
    if not body:
        err("--body is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    priority = getattr(args, "priority", None) or "normal"
    if priority not in VALID_PRIORITIES:
        err(f"--priority must be one of: {', '.join(VALID_PRIORITIES)}")

    audience_type = getattr(args, "audience_type", None) or "all"
    if audience_type not in VALID_AUDIENCE_TYPES:
        err(f"--audience-type must be one of: {', '.join(VALID_AUDIENCE_TYPES)}")

    audience_filter = getattr(args, "audience_filter", None)
    if audience_filter:
        try:
            json.loads(audience_filter) if isinstance(audience_filter, str) else audience_filter
        except (json.JSONDecodeError, TypeError):
            err("--audience-filter must be valid JSON")

    ann_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_announcement
               (id, title, body, priority, audience_type, audience_filter,
                publish_date, expiry_date, announcement_status, published_by,
                company_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft', '', ?, ?, ?)""",
            (ann_id, title, body, priority, audience_type,
             audience_filter,
             getattr(args, "publish_date", None),
             getattr(args, "expiry_date", None),
             company_id, now, now)
        )
    except sqlite3.IntegrityError as e:
        err(f"Announcement creation failed: {e}")

    audit(conn, SKILL, "add-announcement", "educlaw_announcement", ann_id,
          new_values={"title": title, "audience_type": audience_type})
    conn.commit()
    ok({"id": ann_id, "announcement_status": "draft", "title": title})


def update_announcement(conn, args):
    """Update announcement content (draft only)."""
    announcement_id = getattr(args, "announcement_id", None)
    if not announcement_id:
        err("--announcement-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_announcement WHERE id = ?", (announcement_id,)
    ).fetchone()
    if not row:
        err(f"Announcement {announcement_id} not found")
    if row["announcement_status"] != "draft":
        err(f"Cannot update announcement in status '{row['announcement_status']}'. Only draft announcements can be updated.")

    updates, params, changed = [], [], []

    if getattr(args, "title", None) is not None:
        updates.append("title = ?"); params.append(args.title); changed.append("title")
    if getattr(args, "body", None) is not None:
        updates.append("body = ?"); params.append(args.body); changed.append("body")
    if getattr(args, "priority", None) is not None:
        if args.priority not in VALID_PRIORITIES:
            err(f"--priority must be one of: {', '.join(VALID_PRIORITIES)}")
        updates.append("priority = ?"); params.append(args.priority); changed.append("priority")
    if getattr(args, "audience_type", None) is not None:
        if args.audience_type not in VALID_AUDIENCE_TYPES:
            err(f"--audience-type must be one of: {', '.join(VALID_AUDIENCE_TYPES)}")
        updates.append("audience_type = ?"); params.append(args.audience_type); changed.append("audience_type")
    if getattr(args, "audience_filter", None) is not None:
        try:
            json.loads(args.audience_filter) if isinstance(args.audience_filter, str) else args.audience_filter
        except (json.JSONDecodeError, TypeError):
            err("--audience-filter must be valid JSON")
        updates.append("audience_filter = ?"); params.append(args.audience_filter); changed.append("audience_filter")
    if getattr(args, "publish_date", None) is not None:
        updates.append("publish_date = ?"); params.append(args.publish_date); changed.append("publish_date")
    if getattr(args, "expiry_date", None) is not None:
        updates.append("expiry_date = ?"); params.append(args.expiry_date); changed.append("expiry_date")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(announcement_id)
    conn.execute(f"UPDATE educlaw_announcement SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-announcement", "educlaw_announcement", announcement_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": announcement_id, "updated_fields": changed})


def publish_announcement(conn, args):
    """Publish announcement and create notifications for each recipient."""
    announcement_id = getattr(args, "announcement_id", None)
    if not announcement_id:
        err("--announcement-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_announcement WHERE id = ?", (announcement_id,)
    ).fetchone()
    if not row:
        err(f"Announcement {announcement_id} not found")
    if row["announcement_status"] != "draft":
        err(f"Announcement is already '{row['announcement_status']}'. Only draft announcements can be published.")

    published_by = getattr(args, "published_by", None) or getattr(args, "user_id", None) or ""
    now = _now_iso()

    # Use publish_date from record or now
    publish_date = row["publish_date"] or now

    conn.execute(
        """UPDATE educlaw_announcement
           SET announcement_status = 'published', published_by = ?, publish_date = ?, updated_at = ?
           WHERE id = ?""",
        (published_by, publish_date, now, announcement_id)
    )

    company_id = row["company_id"]
    audience_type = row["audience_type"]
    audience_filter = row["audience_filter"]
    title = row["title"]
    priority = row["priority"]
    body = row["body"][:500] if row["body"] else ""  # Truncate for notification message

    recipients = _get_audience_recipients(conn, audience_type, audience_filter, company_id)

    notif_count = 0
    for recipient_type, recipient_id in recipients:
        _create_notification(
            conn, recipient_type, recipient_id, "announcement",
            title, body, company_id,
            reference_type="educlaw_announcement", reference_id=announcement_id
        )
        notif_count += 1

    audit(conn, SKILL, "publish-announcement", "educlaw_announcement", announcement_id,
          new_values={"published_by": published_by, "notifications_created": notif_count})
    conn.commit()
    ok({"id": announcement_id, "announcement_status": "published",
        "notifications_created": notif_count, "audience_type": audience_type})


def list_announcements(conn, args):
    """List announcements with optional filters."""
    query = "SELECT * FROM educlaw_announcement WHERE 1=1"
    params = []

    if getattr(args, "announcement_status", None):
        query += " AND announcement_status = ?"; params.append(args.announcement_status)
    if getattr(args, "audience_type", None):
        query += " AND audience_type = ?"; params.append(args.audience_type)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)
    if getattr(args, "date_from", None):
        query += " AND publish_date >= ?"; params.append(args.date_from)
    if getattr(args, "date_to", None):
        query += " AND publish_date <= ?"; params.append(args.date_to)
    if getattr(args, "priority", None):
        query += " AND priority = ?"; params.append(args.priority)

    query += " ORDER BY created_at DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()

    announcements = []
    for r in rows:
        d = dict(r)
        if d.get("audience_filter"):
            try:
                d["audience_filter"] = json.loads(d["audience_filter"])
            except Exception:
                d["audience_filter"] = {}
        announcements.append(d)

    ok({"announcements": announcements, "count": len(announcements)})


def get_announcement(conn, args):
    """Get announcement details."""
    announcement_id = getattr(args, "announcement_id", None)
    if not announcement_id:
        err("--announcement-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_announcement WHERE id = ?", (announcement_id,)
    ).fetchone()
    if not row:
        err(f"Announcement {announcement_id} not found")

    data = dict(row)
    if data.get("audience_filter"):
        try:
            data["audience_filter"] = json.loads(data["audience_filter"])
        except Exception:
            data["audience_filter"] = {}

    # Count notifications sent for this announcement
    notif_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM educlaw_notification WHERE reference_id = ?",
        (announcement_id,)
    ).fetchone()
    data["notifications_sent"] = notif_count["cnt"] if notif_count else 0

    ok(data)


# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────

def send_notification(conn, args):
    """Send targeted notification to a specific recipient."""
    recipient_type = getattr(args, "recipient_type", None)
    recipient_id = getattr(args, "recipient_id", None)
    notification_type = getattr(args, "notification_type", None)
    title = getattr(args, "title", None)
    message = getattr(args, "message", None)
    company_id = getattr(args, "company_id", None)

    if not recipient_type:
        err("--recipient-type is required")
    if not recipient_id:
        err("--recipient-id is required")
    if not notification_type:
        err("--notification-type is required")
    if not title:
        err("--title is required")
    if not message:
        err("--message is required")
    if not company_id:
        err("--company-id is required")

    if recipient_type not in VALID_RECIPIENT_TYPES:
        err(f"--recipient-type must be one of: {', '.join(VALID_RECIPIENT_TYPES)}")
    if notification_type not in VALID_NOTIFICATION_TYPES:
        err(f"--notification-type must be one of: {', '.join(VALID_NOTIFICATION_TYPES)}")

    # Validate recipient exists
    if recipient_type == "student":
        if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (recipient_id,)).fetchone():
            err(f"Student {recipient_id} not found")
    elif recipient_type == "guardian":
        if not conn.execute("SELECT id FROM educlaw_guardian WHERE id = ?", (recipient_id,)).fetchone():
            err(f"Guardian {recipient_id} not found")
    elif recipient_type == "employee":
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (recipient_id,)).fetchone():
            err(f"Employee {recipient_id} not found")

    sent_via = getattr(args, "sent_via", None) or "system"
    if sent_via not in VALID_SENT_VIA:
        err(f"--sent-via must be one of: {', '.join(VALID_SENT_VIA)}")

    reference_type = getattr(args, "reference_type", None)
    reference_id_val = getattr(args, "reference_id", None)

    notif_id = _create_notification(
        conn, recipient_type, recipient_id, notification_type,
        title, message, company_id,
        reference_type=reference_type, reference_id=reference_id_val,
        sent_via=sent_via
    )
    conn.commit()
    ok({"id": notif_id, "recipient_type": recipient_type, "recipient_id": recipient_id,
        "notification_type": notification_type})


def list_notifications(conn, args):
    """List notifications with optional filters."""
    query = "SELECT * FROM educlaw_notification WHERE 1=1"
    params = []

    if getattr(args, "recipient_type", None):
        query += " AND recipient_type = ?"; params.append(args.recipient_type)
    if getattr(args, "recipient_id", None):
        query += " AND recipient_id = ?"; params.append(args.recipient_id)
    if getattr(args, "notification_type", None):
        query += " AND notification_type = ?"; params.append(args.notification_type)
    if getattr(args, "is_read", None) is not None:
        query += " AND is_read = ?"; params.append(int(args.is_read))
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY created_at DESC"
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"notifications": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# PROGRESS REPORT
# ─────────────────────────────────────────────────────────────────────────────

def send_progress_report(conn, args):
    """Generate and send mid-term progress report to student and guardians."""
    student_id = getattr(args, "student_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not academic_term_id:
        err("--academic-term-id is required")
    if not company_id:
        err("--company-id is required")

    # Validate student
    student_row = conn.execute(
        "SELECT * FROM educlaw_student WHERE id = ?", (student_id,)
    ).fetchone()
    if not student_row:
        err(f"Student {student_id} not found")

    # Validate academic term
    term_row = conn.execute(
        "SELECT * FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone()
    if not term_row:
        err(f"Academic term {academic_term_id} not found")

    student = dict(student_row)
    term = dict(term_row)

    # Get current grades per section in this term
    enrollments = conn.execute(
        """SELECT ce.id, ce.section_id, ce.final_percentage, ce.final_letter_grade,
                  ce.is_grade_submitted, ce.enrollment_status,
                  s.section_number, c.course_code, c.name as course_name, c.credit_hours
           FROM educlaw_course_enrollment ce
           JOIN educlaw_section s ON s.id = ce.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           WHERE ce.student_id = ? AND s.academic_term_id = ?
           AND ce.enrollment_status NOT IN ('dropped','withdrawn')
           ORDER BY c.course_code""",
        (student_id, academic_term_id)
    ).fetchall()

    # Get attendance summary for the term
    att_rows = conn.execute(
        """SELECT attendance_status, COUNT(*) as cnt
           FROM educlaw_student_attendance
           WHERE student_id = ? AND attendance_date >= ? AND attendance_date <= ?
           GROUP BY attendance_status""",
        (student_id, term["start_date"], term["end_date"])
    ).fetchall()
    att_counts = {r["attendance_status"]: r["cnt"] for r in att_rows}
    total_days = sum(att_counts.values())
    present = att_counts.get("present", 0)
    excused = att_counts.get("excused", 0)
    absent = att_counts.get("absent", 0)
    tardy = att_counts.get("tardy", 0)
    att_pct = "0.00"
    if total_days > 0:
        pct = (Decimal(str(present + excused)) / Decimal(str(total_days)) * Decimal("100"))
        att_pct = str(pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Build progress report message
    enrollment_lines = []
    for e in enrollments:
        grade_info = e["final_letter_grade"] or "In Progress"
        pct_info = f" ({e['final_percentage']}%)" if e["final_percentage"] else ""
        enrollment_lines.append(f"{e['course_code']} {e['course_name']}: {grade_info}{pct_info}")

    report_body = (
        f"Progress Report for {student['full_name']} — {term['name']}\n\n"
        f"Academic Standing: {student.get('academic_standing', 'N/A')}\n"
        f"Cumulative GPA: {student.get('cumulative_gpa', 'N/A')}\n\n"
        f"Current Courses:\n" + "\n".join(enrollment_lines) + "\n\n"
        f"Attendance ({term['name']}): {present+excused}/{total_days} days "
        f"({att_pct}%) | Absent: {absent} | Tardy: {tardy}"
    )

    report_title = f"Progress Report: {student['full_name']} — {term['name']}"
    notifications_created = []

    # Send to student
    notif_id = _create_notification(
        conn, "student", student_id, "progress_report",
        report_title, report_body, company_id,
        reference_type="educlaw_academic_term", reference_id=academic_term_id
    )
    notifications_created.append({"recipient_type": "student", "recipient_id": student_id, "notif_id": notif_id})

    # Send to guardians who receive communications
    guardians = conn.execute(
        """SELECT g.id, g.full_name FROM educlaw_guardian g
           JOIN educlaw_student_guardian sg ON sg.guardian_id = g.id
           WHERE sg.student_id = ? AND sg.receives_communications = 1""",
        (student_id,)
    ).fetchall()
    for g in guardians:
        guardian_title = f"Progress Report: {student['full_name']} — {term['name']}"
        notif_id = _create_notification(
            conn, "guardian", g["id"], "progress_report",
            guardian_title, report_body, company_id,
            reference_type="educlaw_academic_term", reference_id=academic_term_id
        )
        notifications_created.append({"recipient_type": "guardian", "recipient_id": g["id"], "notif_id": notif_id})

    conn.commit()
    ok({
        "student_id": student_id,
        "academic_term_id": academic_term_id,
        "enrollment_count": len(enrollments),
        "attendance_percentage": att_pct,
        "notifications_created": len(notifications_created),
        "recipients": notifications_created,
    })


# ─────────────────────────────────────────────────────────────────────────────
# EMERGENCY ALERT
# ─────────────────────────────────────────────────────────────────────────────

def send_emergency_alert(conn, args):
    """Broadcast emergency message to ALL recipients (students + guardians + staff)."""
    title = getattr(args, "title", None)
    message = getattr(args, "message", None)
    company_id = getattr(args, "company_id", None)

    if not title:
        err("--title is required")
    if not message:
        err("--message is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    sent_by = getattr(args, "sent_by", None) or getattr(args, "user_id", None) or ""
    now = _now_iso()

    # Create emergency announcement
    ann_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_announcement
           (id, title, body, priority, audience_type, audience_filter,
            publish_date, expiry_date, announcement_status, published_by,
            company_id, created_at, updated_at)
           VALUES (?, ?, ?, 'emergency', 'all', NULL, ?, NULL, 'published', ?, ?, ?, ?)""",
        (ann_id, title, message, now, sent_by, company_id, now, now)
    )

    # Get ALL recipients in the company
    all_recipients = _get_audience_recipients(conn, "all", None, company_id)

    notif_count = 0
    for recipient_type, recipient_id in all_recipients:
        _create_notification(
            conn, recipient_type, recipient_id, "emergency",
            title, message, company_id,
            reference_type="educlaw_announcement", reference_id=ann_id
        )
        notif_count += 1

    # Enhanced audit logging
    audit(conn, SKILL, "send-emergency-alert", "educlaw_announcement", ann_id,
          new_values={
              "title": title,
              "sent_by": sent_by,
              "notifications_created": notif_count,
              "priority": "emergency",
              "company_id": company_id,
          })

    conn.commit()
    ok({
        "announcement_id": ann_id,
        "announcement_status": "published",
        "priority": "emergency",
        "notifications_created": notif_count,
        "company_id": company_id,
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-announcement": add_announcement,
    "update-announcement": update_announcement,
    "submit-announcement": publish_announcement,
    "list-announcements": list_announcements,
    "get-announcement": get_announcement,
    "submit-notification": send_notification,
    "list-notifications": list_notifications,
    "generate-progress-report": send_progress_report,
    "submit-emergency-alert": send_emergency_alert,
}
