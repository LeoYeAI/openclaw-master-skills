"""HealthClaw — clinical domain module

Actions for the clinical domain (7 tables, 18 actions).
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
    ENTITY_PREFIXES.setdefault("healthclaw_encounter", "ENC-")
    ENTITY_PREFIXES.setdefault("healthclaw_prescription", "RX-")
    ENTITY_PREFIXES.setdefault("healthclaw_procedure", "PROC-")
    ENTITY_PREFIXES.setdefault("healthclaw_order", "ORD-")
except ImportError:
    pass

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALID_ENC_TYPES = ("outpatient", "inpatient", "emergency", "observation", "telehealth", "home_visit")
VALID_ENC_STATUSES = ("open", "in_progress", "completed", "cancelled")
VALID_DX_TYPES = ("primary", "secondary", "admitting", "discharge", "rule_out")
VALID_DX_STATUSES = ("active", "resolved", "chronic", "rule_out")
VALID_RX_ROUTES = ("oral", "iv", "im", "subq", "topical", "inhaled", "rectal", "ophthalmic", "otic", "nasal", "sublingual", "transdermal", "other")
VALID_RX_STATUSES = ("active", "completed", "discontinued", "cancelled", "on_hold")
VALID_PROC_STATUSES = ("planned", "in_progress", "completed", "cancelled")
VALID_ANESTHESIA = ("none", "local", "regional", "general", "sedation")
VALID_LATERALITY = ("left", "right", "bilateral", "not_applicable")
VALID_NOTE_TYPES = ("progress", "soap", "hpi", "consultation", "discharge", "operative", "procedure", "nursing", "other")
VALID_NOTE_STATUSES = ("draft", "signed", "cosigned", "amended", "addended")
VALID_ORDER_TYPES = ("lab", "imaging", "referral", "procedure", "other")
VALID_ORDER_PRIORITIES = ("stat", "urgent", "routine", "elective")
VALID_ORDER_STATUSES = ("pending", "in_progress", "completed", "cancelled")


def _validate_enum(value, valid_values, field_name):
    if value and value not in valid_values:
        err(f"Invalid {field_name}: {value}. Must be one of: {', '.join(valid_values)}")


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


def _validate_encounter(conn, encounter_id):
    if not encounter_id:
        err("--encounter-id is required")
    if not conn.execute("SELECT id FROM healthclaw_encounter WHERE id = ?", (encounter_id,)).fetchone():
        err(f"Encounter {encounter_id} not found")


# ---------------------------------------------------------------------------
# 1. add-encounter
# ---------------------------------------------------------------------------
def add_encounter(conn, args):
    if not args.company_id:
        err("--company-id is required")
    _validate_patient(conn, args.patient_id)
    _validate_provider(conn, args.provider_id)

    enc_date = getattr(args, "encounter_date", None)
    if not enc_date:
        err("--encounter-date is required")
    enc_type = getattr(args, "encounter_type", None) or "outpatient"
    _validate_enum(enc_type, VALID_ENC_TYPES, "encounter-type")

    # Optional appointment link
    appt_id = getattr(args, "appointment_id", None)
    if appt_id:
        if not conn.execute("SELECT id FROM healthclaw_appointment WHERE id = ?", (appt_id,)).fetchone():
            err(f"Appointment {appt_id} not found")

    enc_id = str(uuid.uuid4())
    naming = get_next_name(conn, "healthclaw_encounter", company_id=args.company_id)
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_encounter (
            id, naming_series, patient_id, appointment_id, provider_id,
            encounter_date, encounter_type, chief_complaint, department, room,
            admission_date, discharge_date, status, notes, company_id,
            created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        enc_id, naming, args.patient_id, appt_id, args.provider_id,
        enc_date, enc_type,
        getattr(args, "chief_complaint", None),
        getattr(args, "department", None),
        getattr(args, "room", None),
        getattr(args, "admission_date", None),
        None, "open",
        getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_encounter", enc_id, "add-encounter", args.company_id)
    conn.commit()
    ok({"id": enc_id, "naming_series": naming, "encounter_date": enc_date, "status": "open"})


# ---------------------------------------------------------------------------
# 2. update-encounter
# ---------------------------------------------------------------------------
def update_encounter(conn, args):
    enc_id = getattr(args, "encounter_id", None)
    _validate_encounter(conn, enc_id)

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "encounter_type": "encounter_type", "chief_complaint": "chief_complaint",
        "department": "department", "room": "room",
        "admission_date": "admission_date", "discharge_date": "discharge_date",
        "discharge_disposition": "discharge_disposition",
        "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "encounter_type":
                _validate_enum(val, VALID_ENC_TYPES, "encounter-type")
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    enc_status = getattr(args, "encounter_status", None)
    if enc_status is not None:
        _validate_enum(enc_status, VALID_ENC_STATUSES, "status")
        updates.append("status = ?")
        params.append(enc_status)
        changed.append("status")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(enc_id)
    conn.execute(f"UPDATE healthclaw_encounter SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_encounter", enc_id, "update-encounter", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": enc_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 3. get-encounter
# ---------------------------------------------------------------------------
def get_encounter(conn, args):
    enc_id = getattr(args, "encounter_id", None)
    _validate_encounter(conn, enc_id)
    row = conn.execute("SELECT * FROM healthclaw_encounter WHERE id = ?", (enc_id,)).fetchone()
    data = row_to_dict(row)
    # Enrich
    pat = conn.execute("SELECT full_name FROM healthclaw_patient WHERE id = ?", (data["patient_id"],)).fetchone()
    if pat:
        data["patient_name"] = pat[0]
    prov = conn.execute("SELECT full_name FROM employee WHERE id = ?", (data["provider_id"],)).fetchone()
    if prov:
        data["provider_name"] = prov[0]
    data["diagnosis_count"] = conn.execute("SELECT COUNT(*) FROM healthclaw_diagnosis WHERE encounter_id = ?", (enc_id,)).fetchone()[0]
    data["prescription_count"] = conn.execute("SELECT COUNT(*) FROM healthclaw_prescription WHERE encounter_id = ?", (enc_id,)).fetchone()[0]
    ok(data)


# ---------------------------------------------------------------------------
# 4. list-encounters
# ---------------------------------------------------------------------------
def list_encounters(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?"); params.append(args.company_id)
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "provider_id", None):
        where.append("provider_id = ?"); params.append(args.provider_id)
    if getattr(args, "encounter_status", None):
        where.append("status = ?"); params.append(args.encounter_status)
    if getattr(args, "encounter_type", None):
        where.append("encounter_type = ?"); params.append(args.encounter_type)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_encounter WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(f"SELECT * FROM healthclaw_encounter WHERE {where_sql} ORDER BY encounter_date DESC LIMIT ? OFFSET ?", params).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 5. add-vitals
# ---------------------------------------------------------------------------
def add_vitals(conn, args):
    enc_id = getattr(args, "encounter_id", None)
    _validate_encounter(conn, enc_id)
    _validate_patient(conn, args.patient_id)

    vitals_id = str(uuid.uuid4())
    recorded_by = getattr(args, "recorded_by_id", None)
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_vitals (
            id, encounter_id, patient_id, recorded_by_id, recorded_at,
            temperature, temperature_site, heart_rate, respiratory_rate,
            blood_pressure_systolic, blood_pressure_diastolic,
            oxygen_saturation, weight, height, bmi, pain_level, notes, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        vitals_id, enc_id, args.patient_id, recorded_by, now,
        getattr(args, "temperature", None),
        getattr(args, "temperature_site", None),
        int(args.heart_rate) if getattr(args, "heart_rate", None) else None,
        int(args.respiratory_rate) if getattr(args, "respiratory_rate", None) else None,
        int(args.bp_systolic) if getattr(args, "bp_systolic", None) else None,
        int(args.bp_diastolic) if getattr(args, "bp_diastolic", None) else None,
        getattr(args, "oxygen_saturation", None),
        getattr(args, "weight", None),
        getattr(args, "height", None),
        getattr(args, "bmi", None),
        int(args.pain_level) if getattr(args, "pain_level", None) else None,
        getattr(args, "notes", None), now,
    ))
    audit(conn, "healthclaw_vitals", vitals_id, "add-vitals", None)
    conn.commit()
    ok({"id": vitals_id, "encounter_id": enc_id})


# ---------------------------------------------------------------------------
# 6. list-vitals
# ---------------------------------------------------------------------------
def list_vitals(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "encounter_id", None):
        where.append("encounter_id = ?"); params.append(args.encounter_id)
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_vitals WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(f"SELECT * FROM healthclaw_vitals WHERE {where_sql} ORDER BY recorded_at DESC LIMIT ? OFFSET ?", params).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 7. add-diagnosis
# ---------------------------------------------------------------------------
def add_diagnosis(conn, args):
    enc_id = getattr(args, "encounter_id", None)
    _validate_encounter(conn, enc_id)
    _validate_patient(conn, args.patient_id)

    icd10 = getattr(args, "icd10_code", None)
    if not icd10:
        err("--icd10-code is required")
    desc = getattr(args, "dx_description", None)
    if not desc:
        err("--dx-description is required")

    dx_type = getattr(args, "diagnosis_type", None) or "primary"
    _validate_enum(dx_type, VALID_DX_TYPES, "diagnosis-type")

    dx_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_diagnosis (
            id, encounter_id, patient_id, icd10_code, description,
            diagnosis_type, status, onset_date, diagnosed_by_id, notes,
            created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        dx_id, enc_id, args.patient_id, icd10, desc,
        dx_type, "active",
        getattr(args, "onset_date", None),
        getattr(args, "diagnosed_by_id", None) or getattr(args, "provider_id", None),
        getattr(args, "notes", None), now, now,
    ))
    audit(conn, "healthclaw_diagnosis", dx_id, "add-diagnosis", None)
    conn.commit()
    ok({"id": dx_id, "icd10_code": icd10, "diagnosis_type": dx_type})


# ---------------------------------------------------------------------------
# 8. update-diagnosis
# ---------------------------------------------------------------------------
def update_diagnosis(conn, args):
    dx_id = getattr(args, "diagnosis_id", None)
    if not dx_id:
        err("--diagnosis-id is required")
    if not conn.execute("SELECT id FROM healthclaw_diagnosis WHERE id = ?", (dx_id,)).fetchone():
        err(f"Diagnosis {dx_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "icd10_code": "icd10_code", "dx_description": "description",
        "diagnosis_type": "diagnosis_type", "dx_status": "status",
        "onset_date": "onset_date", "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "diagnosis_type":
                _validate_enum(val, VALID_DX_TYPES, "diagnosis-type")
            elif col_name == "status":
                _validate_enum(val, VALID_DX_STATUSES, "status")
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(dx_id)
    conn.execute(f"UPDATE healthclaw_diagnosis SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_diagnosis", dx_id, "update-diagnosis", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": dx_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 9. list-diagnoses
# ---------------------------------------------------------------------------
def list_diagnoses(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "encounter_id", None):
        where.append("encounter_id = ?"); params.append(args.encounter_id)
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "dx_status", None):
        where.append("status = ?"); params.append(args.dx_status)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_diagnosis WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(f"SELECT * FROM healthclaw_diagnosis WHERE {where_sql} ORDER BY diagnosis_type, created_at DESC LIMIT ? OFFSET ?", params).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 10. add-prescription
# ---------------------------------------------------------------------------
def add_prescription(conn, args):
    enc_id = getattr(args, "encounter_id", None)
    _validate_encounter(conn, enc_id)
    _validate_patient(conn, args.patient_id)

    prescriber_id = getattr(args, "prescriber_id", None) or getattr(args, "provider_id", None)
    if not prescriber_id:
        err("--prescriber-id or --provider-id is required")

    med_name = getattr(args, "medication_name", None)
    if not med_name:
        err("--medication-name is required")
    dosage = getattr(args, "dosage", None)
    if not dosage:
        err("--dosage is required")
    frequency = getattr(args, "frequency", None)
    if not frequency:
        err("--frequency is required")
    start_date = getattr(args, "rx_start_date", None)
    if not start_date:
        err("--rx-start-date is required")

    route = getattr(args, "route", None) or "oral"
    _validate_enum(route, VALID_RX_ROUTES, "route")

    rx_id = str(uuid.uuid4())
    naming = get_next_name(conn, "healthclaw_prescription", company_id=args.company_id)
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_prescription (
            id, naming_series, encounter_id, patient_id, prescriber_id,
            medication_name, ndc_code, dosage, frequency, route,
            quantity, refills, daw, start_date, end_date,
            diagnosis_id, controlled_schedule, pharmacy_notes,
            status, notes, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        rx_id, naming, enc_id, args.patient_id, prescriber_id,
        med_name, getattr(args, "ndc_code", None),
        dosage, frequency, route,
        getattr(args, "quantity", None) or "0",
        int(getattr(args, "refills", None) or 0),
        1 if getattr(args, "daw", None) == "1" else 0,
        start_date, getattr(args, "rx_end_date", None),
        getattr(args, "diagnosis_id", None),
        getattr(args, "controlled_schedule", None),
        getattr(args, "pharmacy_notes", None),
        "active", getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_prescription", rx_id, "add-prescription", args.company_id)
    conn.commit()
    ok({"id": rx_id, "naming_series": naming, "medication_name": med_name, "status": "active"})


# ---------------------------------------------------------------------------
# 11. update-prescription
# ---------------------------------------------------------------------------
def update_prescription(conn, args):
    rx_id = getattr(args, "prescription_id", None)
    if not rx_id:
        err("--prescription-id is required")
    if not conn.execute("SELECT id FROM healthclaw_prescription WHERE id = ?", (rx_id,)).fetchone():
        err(f"Prescription {rx_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "dosage": "dosage", "frequency": "frequency", "route": "route",
        "rx_end_date": "end_date", "pharmacy_notes": "pharmacy_notes",
        "rx_status": "status", "discontinued_reason": "discontinued_reason",
        "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "route":
                _validate_enum(val, VALID_RX_ROUTES, "route")
            elif col_name == "status":
                _validate_enum(val, VALID_RX_STATUSES, "status")
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)
    refills = getattr(args, "refills", None)
    if refills is not None:
        updates.append("refills = ?"); params.append(int(refills)); changed.append("refills")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(rx_id)
    conn.execute(f"UPDATE healthclaw_prescription SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_prescription", rx_id, "update-prescription", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": rx_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 12. list-prescriptions
# ---------------------------------------------------------------------------
def list_prescriptions(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "encounter_id", None):
        where.append("encounter_id = ?"); params.append(args.encounter_id)
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "rx_status", None):
        where.append("status = ?"); params.append(args.rx_status)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_prescription WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(f"SELECT * FROM healthclaw_prescription WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?", params).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 13. add-procedure
# ---------------------------------------------------------------------------
def add_procedure(conn, args):
    enc_id = getattr(args, "encounter_id", None)
    _validate_encounter(conn, enc_id)
    _validate_patient(conn, args.patient_id)
    _validate_provider(conn, args.provider_id)

    cpt = getattr(args, "cpt_code", None)
    if not cpt:
        err("--cpt-code is required")
    proc_desc = getattr(args, "proc_description", None)
    if not proc_desc:
        err("--proc-description is required")
    proc_date = getattr(args, "procedure_date", None)
    if not proc_date:
        err("--procedure-date is required")

    proc_id = str(uuid.uuid4())
    naming = get_next_name(conn, "healthclaw_procedure", company_id=args.company_id)
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_procedure (
            id, naming_series, encounter_id, patient_id, provider_id,
            cpt_code, description, procedure_date, start_time, end_time,
            modifiers, diagnosis_ids, anesthesia_type, body_site, laterality,
            status, notes, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        proc_id, naming, enc_id, args.patient_id, args.provider_id,
        cpt, proc_desc, proc_date,
        getattr(args, "start_time", None), getattr(args, "end_time", None),
        getattr(args, "modifiers", None), getattr(args, "diagnosis_ids", None),
        getattr(args, "anesthesia_type", None),
        getattr(args, "body_site", None), getattr(args, "laterality", None),
        "completed", getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_procedure", proc_id, "add-procedure", args.company_id)
    conn.commit()
    ok({"id": proc_id, "naming_series": naming, "cpt_code": cpt, "status": "completed"})


# ---------------------------------------------------------------------------
# 14. list-procedures
# ---------------------------------------------------------------------------
def list_procedures(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "encounter_id", None):
        where.append("encounter_id = ?"); params.append(args.encounter_id)
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "cpt_code", None):
        where.append("cpt_code = ?"); params.append(args.cpt_code)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_procedure WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(f"SELECT * FROM healthclaw_procedure WHERE {where_sql} ORDER BY procedure_date DESC LIMIT ? OFFSET ?", params).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 15. add-clinical-note
# ---------------------------------------------------------------------------
def add_clinical_note(conn, args):
    enc_id = getattr(args, "encounter_id", None)
    _validate_encounter(conn, enc_id)
    _validate_patient(conn, args.patient_id)

    author_id = getattr(args, "author_id", None) or getattr(args, "provider_id", None)
    if not author_id:
        err("--author-id or --provider-id is required")

    note_type = getattr(args, "note_type", None) or "progress"
    _validate_enum(note_type, VALID_NOTE_TYPES, "note-type")

    note_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_clinical_note (
            id, encounter_id, patient_id, author_id, note_type,
            subjective, objective, assessment, plan, body,
            addendum, signed_at, cosigner_id, cosigned_at,
            status, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        note_id, enc_id, args.patient_id, author_id, note_type,
        getattr(args, "subjective", None),
        getattr(args, "objective", None),
        getattr(args, "assessment", None),
        getattr(args, "plan_text", None),
        getattr(args, "body", None),
        None, None, None, None,
        "draft", now, now,
    ))
    audit(conn, "healthclaw_clinical_note", note_id, "add-clinical-note", None)
    conn.commit()
    ok({"id": note_id, "note_type": note_type, "status": "draft"})


# ---------------------------------------------------------------------------
# 16. update-clinical-note
# ---------------------------------------------------------------------------
def update_clinical_note(conn, args):
    note_id = getattr(args, "note_id", None)
    if not note_id:
        err("--note-id is required")
    if not conn.execute("SELECT id FROM healthclaw_clinical_note WHERE id = ?", (note_id,)).fetchone():
        err(f"Clinical note {note_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "note_type": "note_type", "subjective": "subjective",
        "objective": "objective", "assessment": "assessment",
        "plan_text": "plan", "body": "body", "addendum": "addendum",
        "note_status": "status", "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "note_type":
                _validate_enum(val, VALID_NOTE_TYPES, "note-type")
            elif col_name == "status":
                _validate_enum(val, VALID_NOTE_STATUSES, "status")
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    # Sign the note
    if getattr(args, "sign", None) == "1":
        updates.append("status = 'signed'"); changed.append("status")
        updates.append("signed_at = ?"); params.append(_now_iso()); changed.append("signed_at")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(note_id)
    conn.execute(f"UPDATE healthclaw_clinical_note SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_clinical_note", note_id, "update-clinical-note", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": note_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 17. list-clinical-notes
# ---------------------------------------------------------------------------
def list_clinical_notes(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "encounter_id", None):
        where.append("encounter_id = ?"); params.append(args.encounter_id)
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "note_type", None):
        where.append("note_type = ?"); params.append(args.note_type)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_clinical_note WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(f"SELECT * FROM healthclaw_clinical_note WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?", params).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total, "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 18. add-order
# ---------------------------------------------------------------------------
def add_order(conn, args):
    enc_id = getattr(args, "encounter_id", None)
    _validate_encounter(conn, enc_id)
    _validate_patient(conn, args.patient_id)

    ordering_prov = getattr(args, "ordering_provider_id", None) or getattr(args, "provider_id", None)
    if not ordering_prov:
        err("--ordering-provider-id or --provider-id is required")

    order_type = getattr(args, "order_type", None)
    if not order_type:
        err("--order-type is required")
    _validate_enum(order_type, VALID_ORDER_TYPES, "order-type")

    order_date = getattr(args, "order_date", None)
    if not order_date:
        err("--order-date is required")

    priority = getattr(args, "priority", None) or "routine"
    _validate_enum(priority, VALID_ORDER_PRIORITIES, "priority")

    order_id = str(uuid.uuid4())
    naming = get_next_name(conn, "healthclaw_order", company_id=args.company_id)
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_order (
            id, naming_series, encounter_id, patient_id, ordering_provider_id,
            order_type, order_date, priority, clinical_indication,
            diagnosis_id, status, notes, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        order_id, naming, enc_id, args.patient_id, ordering_prov,
        order_type, order_date, priority,
        getattr(args, "clinical_indication", None),
        getattr(args, "diagnosis_id", None),
        "pending", getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_order", order_id, "add-order", args.company_id)
    conn.commit()
    ok({"id": order_id, "naming_series": naming, "order_type": order_type, "status": "pending"})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-encounter": add_encounter,
    "update-encounter": update_encounter,
    "get-encounter": get_encounter,
    "list-encounters": list_encounters,
    "add-vitals": add_vitals,
    "list-vitals": list_vitals,
    "add-diagnosis": add_diagnosis,
    "update-diagnosis": update_diagnosis,
    "list-diagnoses": list_diagnoses,
    "add-prescription": add_prescription,
    "update-prescription": update_prescription,
    "list-prescriptions": list_prescriptions,
    "add-procedure": add_procedure,
    "list-procedures": list_procedures,
    "add-clinical-note": add_clinical_note,
    "update-clinical-note": update_clinical_note,
    "list-clinical-notes": list_clinical_notes,
    "add-order": add_order,
}
