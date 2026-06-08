"""HealthClaw — appointments domain module

Actions for the appointments domain (5 tables, 14 actions).
Imported by db_query.py (unified router).
"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.naming import get_next_name, ENTITY_PREFIXES
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit

    # Register naming prefixes
    ENTITY_PREFIXES.setdefault("healthclaw_appointment", "APPT-")
except ImportError:
    pass

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------
VALID_APPT_TYPES = ("new_patient", "follow_up", "urgent", "walk_in", "telehealth", "procedure", "physical_exam", "consultation")
VALID_APPT_STATUSES = ("scheduled", "confirmed", "checked_in", "in_progress", "completed", "cancelled", "no_show", "rescheduled")
VALID_BLOCK_REASONS = ("vacation", "meeting", "personal", "maintenance", "holiday", "other")
VALID_WAITLIST_PRIORITIES = ("low", "normal", "high", "urgent")
VALID_WAITLIST_STATUSES = ("waiting", "offered", "accepted", "expired", "cancelled")


def _validate_enum(value, valid_values, field_name):
    if value and value not in valid_values:
        err(f"Invalid {field_name}: {value}. Must be one of: {', '.join(valid_values)}")


def _validate_company(conn, company_id):
    if not company_id:
        err("--company-id is required")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")


def _validate_patient(conn, patient_id):
    if not patient_id:
        err("--patient-id is required")
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (patient_id,)).fetchone():
        err(f"Patient {patient_id} not found")


def _validate_provider(conn, provider_id):
    if not provider_id:
        err("--provider-id is required")
    if not conn.execute("SELECT id FROM employee WHERE id = ?", (provider_id,)).fetchone():
        err(f"Provider (employee) {provider_id} not found")


# ---------------------------------------------------------------------------
# 1. add-provider-schedule
# ---------------------------------------------------------------------------
def add_provider_schedule(conn, args):
    _validate_company(conn, args.company_id)
    _validate_provider(conn, args.provider_id)
    day = getattr(args, "day_of_week", None)
    if day is None:
        err("--day-of-week is required (0=Mon, 6=Sun)")
    try:
        day = int(day)
    except (TypeError, ValueError):
        err("--day-of-week must be an integer 0-6")
    if day < 0 or day > 6:
        err("--day-of-week must be 0-6")
    start = getattr(args, "start_time", None)
    end = getattr(args, "end_time", None)
    if not start or not end:
        err("--start-time and --end-time are required (HH:MM)")

    sched_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_provider_schedule (
            id, provider_id, day_of_week, start_time, end_time, slot_duration,
            location, status, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        sched_id, args.provider_id, day, start, end,
        int(getattr(args, "slot_duration", None) or 30),
        getattr(args, "location", None),
        "active", args.company_id, now, now,
    ))
    audit(conn, "healthclaw_provider_schedule", sched_id, "add-provider-schedule", args.company_id)
    conn.commit()
    ok({"id": sched_id, "provider_id": args.provider_id, "day_of_week": day})


# ---------------------------------------------------------------------------
# 2. update-provider-schedule
# ---------------------------------------------------------------------------
def update_provider_schedule(conn, args):
    sched_id = getattr(args, "schedule_id", None)
    if not sched_id:
        err("--schedule-id is required")
    if not conn.execute("SELECT id FROM healthclaw_provider_schedule WHERE id = ?", (sched_id,)).fetchone():
        err(f"Schedule {sched_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "start_time": "start_time", "end_time": "end_time",
        "location": "location", "status": "status",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "status":
                _validate_enum(val, ("active", "inactive"), "status")
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)
    slot = getattr(args, "slot_duration", None)
    if slot is not None:
        updates.append("slot_duration = ?")
        params.append(int(slot))
        changed.append("slot_duration")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(sched_id)
    conn.execute(f"UPDATE healthclaw_provider_schedule SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_provider_schedule", sched_id, "update-provider-schedule", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": sched_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 3. list-provider-schedules
# ---------------------------------------------------------------------------
def list_provider_schedules(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "provider_id", None):
        where.append("provider_id = ?")
        params.append(args.provider_id)
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_provider_schedule WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_provider_schedule WHERE {where_sql} ORDER BY day_of_week, start_time LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 4. add-schedule-block
# ---------------------------------------------------------------------------
def add_schedule_block(conn, args):
    _validate_company(conn, args.company_id)
    _validate_provider(conn, args.provider_id)
    block_date = getattr(args, "block_date", None)
    if not block_date:
        err("--block-date is required")
    reason = getattr(args, "reason", None) or "other"
    _validate_enum(reason, VALID_BLOCK_REASONS, "reason")

    block_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_schedule_block (
            id, provider_id, block_date, start_time, end_time, reason,
            notes, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        block_id, args.provider_id, block_date,
        getattr(args, "start_time", None),
        getattr(args, "end_time", None),
        reason, getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_schedule_block", block_id, "add-schedule-block", args.company_id)
    conn.commit()
    ok({"id": block_id, "block_date": block_date, "reason": reason})


# ---------------------------------------------------------------------------
# 5. list-schedule-blocks
# ---------------------------------------------------------------------------
def list_schedule_blocks(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "provider_id", None):
        where.append("provider_id = ?")
        params.append(args.provider_id)
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_schedule_block WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_schedule_block WHERE {where_sql} ORDER BY block_date DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 6. add-appointment
# ---------------------------------------------------------------------------
def add_appointment(conn, args):
    _validate_company(conn, args.company_id)
    _validate_patient(conn, args.patient_id)
    _validate_provider(conn, args.provider_id)

    appt_date = getattr(args, "appointment_date", None)
    start = getattr(args, "start_time", None)
    end = getattr(args, "end_time", None)
    if not appt_date:
        err("--appointment-date is required")
    if not start or not end:
        err("--start-time and --end-time are required")

    appt_type = getattr(args, "appointment_type", None) or "follow_up"
    _validate_enum(appt_type, VALID_APPT_TYPES, "appointment-type")

    appt_id = str(uuid.uuid4())
    naming = get_next_name(conn, "healthclaw_appointment", company_id=args.company_id)
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_appointment (
            id, naming_series, patient_id, provider_id, appointment_date,
            start_time, end_time, duration_minutes, appointment_type,
            chief_complaint, location, status, notes, company_id,
            created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        appt_id, naming, args.patient_id, args.provider_id, appt_date,
        start, end,
        int(getattr(args, "duration_minutes", None) or 30),
        appt_type,
        getattr(args, "chief_complaint", None),
        getattr(args, "location", None),
        "scheduled", getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_appointment", appt_id, "add-appointment", args.company_id)
    conn.commit()
    ok({"id": appt_id, "naming_series": naming, "appointment_date": appt_date, "status": "scheduled"})


# ---------------------------------------------------------------------------
# 7. update-appointment
# ---------------------------------------------------------------------------
def update_appointment(conn, args):
    appt_id = getattr(args, "appointment_id", None)
    if not appt_id:
        err("--appointment-id is required")
    if not conn.execute("SELECT id FROM healthclaw_appointment WHERE id = ?", (appt_id,)).fetchone():
        err(f"Appointment {appt_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "appointment_date": "appointment_date", "start_time": "start_time",
        "end_time": "end_time", "appointment_type": "appointment_type",
        "chief_complaint": "chief_complaint", "location": "location",
        "notes": "notes", "cancellation_reason": "cancellation_reason",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "appointment_type":
                _validate_enum(val, VALID_APPT_TYPES, "appointment-type")
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)
    dur = getattr(args, "duration_minutes", None)
    if dur is not None:
        updates.append("duration_minutes = ?")
        params.append(int(dur))
        changed.append("duration_minutes")
    # Provider reassignment
    new_provider = getattr(args, "new_provider_id", None)
    if new_provider:
        _validate_provider(conn, new_provider)
        updates.append("provider_id = ?")
        params.append(new_provider)
        changed.append("provider_id")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(appt_id)
    conn.execute(f"UPDATE healthclaw_appointment SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_appointment", appt_id, "update-appointment", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": appt_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 8. get-appointment
# ---------------------------------------------------------------------------
def get_appointment(conn, args):
    appt_id = getattr(args, "appointment_id", None)
    if not appt_id:
        err("--appointment-id is required")
    row = conn.execute("SELECT * FROM healthclaw_appointment WHERE id = ?", (appt_id,)).fetchone()
    if not row:
        err(f"Appointment {appt_id} not found")
    data = row_to_dict(row)

    # Enrich: patient name
    pat = conn.execute("SELECT full_name FROM healthclaw_patient WHERE id = ?", (data["patient_id"],)).fetchone()
    if pat:
        data["patient_name"] = pat[0]
    # Enrich: provider name
    prov = conn.execute("SELECT full_name FROM employee WHERE id = ?", (data["provider_id"],)).fetchone()
    if prov:
        data["provider_name"] = prov[0]
    ok(data)


# ---------------------------------------------------------------------------
# 9. list-appointments
# ---------------------------------------------------------------------------
def list_appointments(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?")
        params.append(args.patient_id)
    if getattr(args, "provider_id", None):
        where.append("provider_id = ?")
        params.append(args.provider_id)
    if getattr(args, "appointment_date", None):
        where.append("appointment_date = ?")
        params.append(args.appointment_date)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)
    if getattr(args, "search", None):
        # Search joins patient name
        where.append("patient_id IN (SELECT id FROM healthclaw_patient WHERE full_name LIKE ?)")
        params.append(f"%{args.search}%")

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_appointment WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_appointment WHERE {where_sql} ORDER BY appointment_date DESC, start_time ASC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 10. check-in-appointment
# ---------------------------------------------------------------------------
def check_in_appointment(conn, args):
    appt_id = getattr(args, "appointment_id", None)
    if not appt_id:
        err("--appointment-id is required")
    row = conn.execute("SELECT status FROM healthclaw_appointment WHERE id = ?", (appt_id,)).fetchone()
    if not row:
        err(f"Appointment {appt_id} not found")
    if row[0] not in ("scheduled", "confirmed"):
        err(f"Cannot check in appointment with status '{row[0]}'. Must be scheduled or confirmed.")

    now = _now_iso()
    conn.execute(
        "UPDATE healthclaw_appointment SET status = 'checked_in', check_in_time = ?, updated_at = datetime('now') WHERE id = ?",
        (now, appt_id)
    )
    audit(conn, "healthclaw_appointment", appt_id, "check-in-appointment", None)
    conn.commit()
    ok({"id": appt_id, "status": "checked_in", "check_in_time": now})


# ---------------------------------------------------------------------------
# 11. check-out-appointment
# ---------------------------------------------------------------------------
def check_out_appointment(conn, args):
    appt_id = getattr(args, "appointment_id", None)
    if not appt_id:
        err("--appointment-id is required")
    row = conn.execute("SELECT status FROM healthclaw_appointment WHERE id = ?", (appt_id,)).fetchone()
    if not row:
        err(f"Appointment {appt_id} not found")
    if row[0] not in ("checked_in", "in_progress"):
        err(f"Cannot check out appointment with status '{row[0]}'. Must be checked_in or in_progress.")

    now = _now_iso()
    conn.execute(
        "UPDATE healthclaw_appointment SET status = 'completed', check_out_time = ?, updated_at = datetime('now') WHERE id = ?",
        (now, appt_id)
    )
    audit(conn, "healthclaw_appointment", appt_id, "check-out-appointment", None)
    conn.commit()
    ok({"id": appt_id, "status": "completed", "check_out_time": now})


# ---------------------------------------------------------------------------
# 12. cancel-appointment
# ---------------------------------------------------------------------------
def cancel_appointment(conn, args):
    appt_id = getattr(args, "appointment_id", None)
    if not appt_id:
        err("--appointment-id is required")
    row = conn.execute("SELECT status FROM healthclaw_appointment WHERE id = ?", (appt_id,)).fetchone()
    if not row:
        err(f"Appointment {appt_id} not found")
    if row[0] in ("completed", "cancelled"):
        err(f"Cannot cancel appointment with status '{row[0]}'.")

    conn.execute(
        "UPDATE healthclaw_appointment SET status = 'cancelled', cancellation_reason = ?, updated_at = datetime('now') WHERE id = ?",
        (getattr(args, "cancellation_reason", None), appt_id)
    )
    audit(conn, "healthclaw_appointment", appt_id, "cancel-appointment", None)
    conn.commit()
    ok({"id": appt_id, "status": "cancelled"})


# ---------------------------------------------------------------------------
# 13. add-waitlist
# ---------------------------------------------------------------------------
def add_waitlist(conn, args):
    _validate_company(conn, args.company_id)
    _validate_patient(conn, args.patient_id)

    priority = getattr(args, "priority", None) or "normal"
    _validate_enum(priority, VALID_WAITLIST_PRIORITIES, "priority")

    wl_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_waitlist (
            id, patient_id, provider_id, preferred_date_start, preferred_date_end,
            preferred_time_start, preferred_time_end, appointment_type,
            priority, status, notes, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        wl_id, args.patient_id,
        getattr(args, "provider_id", None),
        getattr(args, "preferred_date_start", None),
        getattr(args, "preferred_date_end", None),
        getattr(args, "preferred_time_start", None),
        getattr(args, "preferred_time_end", None),
        getattr(args, "appointment_type", None) or "follow_up",
        priority, "waiting",
        getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_waitlist", wl_id, "add-waitlist", args.company_id)
    conn.commit()
    ok({"id": wl_id, "priority": priority, "status": "waiting"})


# ---------------------------------------------------------------------------
# 14. list-waitlist
# ---------------------------------------------------------------------------
def list_waitlist(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?")
        params.append(args.patient_id)
    if getattr(args, "provider_id", None):
        where.append("provider_id = ?")
        params.append(args.provider_id)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_waitlist WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_waitlist WHERE {where_sql} ORDER BY priority DESC, created_at ASC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-provider-schedule": add_provider_schedule,
    "update-provider-schedule": update_provider_schedule,
    "list-provider-schedules": list_provider_schedules,
    "add-schedule-block": add_schedule_block,
    "list-schedule-blocks": list_schedule_blocks,
    "add-appointment": add_appointment,
    "update-appointment": update_appointment,
    "get-appointment": get_appointment,
    "list-appointments": list_appointments,
    "check-in-appointment": check_in_appointment,
    "check-out-appointment": check_out_appointment,
    "cancel-appointment": cancel_appointment,
    "add-waitlist": add_waitlist,
    "list-waitlist": list_waitlist,
}
