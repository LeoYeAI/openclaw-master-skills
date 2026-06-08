"""HealthClaw — patients domain module

Actions for the patients domain (6 tables, 16 actions).
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
    from erpclaw_lib.naming import get_next_name, ENTITY_PREFIXES
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit

    # Register HealthClaw naming prefixes (patients domain)
    ENTITY_PREFIXES.setdefault("healthclaw_patient", "PAT-")
    ENTITY_PREFIXES.setdefault("healthclaw_patient_insurance", "INS-")
except ImportError:
    pass

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------
VALID_GENDERS = ("male", "female", "other", "unknown")
VALID_PATIENT_STATUSES = ("active", "inactive", "deceased")
VALID_MARITAL_STATUSES = ("single", "married", "divorced", "widowed", "separated", "unknown")
VALID_ETHNICITIES = ("hispanic_latino", "not_hispanic_latino", "unknown")
VALID_INSURANCE_TYPES = ("primary", "secondary", "tertiary")
VALID_PLAN_TYPES = ("hmo", "ppo", "epo", "pos", "hdhp", "medicare", "medicaid", "tricare", "workers_comp", "self_pay", "other")
VALID_SUBSCRIBER_RELATIONSHIPS = ("self", "spouse", "child", "other")
VALID_INSURANCE_STATUSES = ("active", "inactive", "expired", "terminated")
VALID_ALLERGEN_TYPES = ("drug", "food", "environmental", "other")
VALID_SEVERITIES = ("mild", "moderate", "severe", "life_threatening")
VALID_ALLERGY_STATUSES = ("active", "inactive", "resolved")
VALID_MEDHIST_STATUSES = ("active", "resolved", "chronic")
VALID_CONTACT_TYPES = ("emergency", "next_of_kin", "guardian", "power_of_attorney", "other")
VALID_CONSENT_TYPES = ("hipaa_privacy", "treatment", "surgery", "anesthesia", "research", "telehealth", "photo_video", "release_of_info", "other")
VALID_CONSENT_STATUSES = ("active", "expired", "revoked")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _validate_company(conn, company_id):
    if not company_id:
        err("--company-id is required")
    row = conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone()
    if not row:
        err(f"Company {company_id} not found")


def _validate_patient(conn, patient_id):
    if not patient_id:
        err("--patient-id is required")
    row = conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (patient_id,)).fetchone()
    if not row:
        err(f"Patient {patient_id} not found")


def _validate_enum(value, valid_values, field_name):
    if value and value not in valid_values:
        err(f"Invalid {field_name}: {value}. Must be one of: {', '.join(valid_values)}")


# ---------------------------------------------------------------------------
# 1. add-patient
# ---------------------------------------------------------------------------
def add_patient(conn, args):
    _validate_company(conn, args.company_id)
    if not args.first_name:
        err("--first-name is required")
    if not args.last_name:
        err("--last-name is required")
    if not args.date_of_birth:
        err("--date-of-birth is required")
    if not args.gender:
        err("--gender is required")
    _validate_enum(args.gender, VALID_GENDERS, "gender")
    _validate_enum(getattr(args, "marital_status", None), VALID_MARITAL_STATUSES, "marital-status")
    _validate_enum(getattr(args, "ethnicity", None), VALID_ETHNICITIES, "ethnicity")

    # Check provider exists if specified
    provider_id = getattr(args, "primary_provider_id", None)
    if provider_id:
        row = conn.execute("SELECT id FROM employee WHERE id = ?", (provider_id,)).fetchone()
        if not row:
            err(f"Provider (employee) {provider_id} not found")

    patient_id = str(uuid.uuid4())
    full_name = f"{args.first_name} {args.last_name}"

    # Generate naming series (MRN)
    mrn = get_next_name(conn, "healthclaw_patient", company_id=args.company_id)

    # Optionally link to customer
    customer_id = getattr(args, "customer_id", None)
    if customer_id:
        row = conn.execute("SELECT id FROM customer WHERE id = ?", (customer_id,)).fetchone()
        if not row:
            err(f"Customer {customer_id} not found")

    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_patient (
            id, naming_series, customer_id, first_name, last_name, full_name,
            date_of_birth, gender, ssn, mrn, marital_status, race, ethnicity,
            preferred_language, primary_phone, secondary_phone, email,
            address_line1, address_line2, city, state, zip_code,
            primary_provider_id, status, notes, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        patient_id, mrn, customer_id,
        args.first_name, args.last_name, full_name,
        args.date_of_birth, args.gender,
        getattr(args, "ssn", None), mrn,
        getattr(args, "marital_status", None),
        getattr(args, "race", None),
        getattr(args, "ethnicity", None),
        getattr(args, "preferred_language", None) or "English",
        getattr(args, "primary_phone", None),
        getattr(args, "secondary_phone", None),
        getattr(args, "email", None),
        getattr(args, "address_line1", None),
        getattr(args, "address_line2", None),
        getattr(args, "city", None),
        getattr(args, "state", None),
        getattr(args, "zip_code", None),
        provider_id,
        "active",
        getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_patient", patient_id, "add-patient", args.company_id)
    conn.commit()
    ok({"id": patient_id, "naming_series": mrn, "full_name": full_name, "mrn": mrn})


# ---------------------------------------------------------------------------
# 2. get-patient
# ---------------------------------------------------------------------------
def get_patient(conn, args):
    _validate_patient(conn, args.patient_id)
    row = conn.execute("SELECT * FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone()
    data = row_to_dict(row)

    # Enrich with counts
    ins_count = conn.execute(
        "SELECT COUNT(*) FROM healthclaw_patient_insurance WHERE patient_id = ? AND status = 'active'",
        (args.patient_id,)
    ).fetchone()[0]
    allergy_count = conn.execute(
        "SELECT COUNT(*) FROM healthclaw_allergy WHERE patient_id = ? AND status = 'active'",
        (args.patient_id,)
    ).fetchone()[0]
    data["active_insurance_count"] = ins_count
    data["active_allergy_count"] = allergy_count
    ok(data)


# ---------------------------------------------------------------------------
# 3. update-patient
# ---------------------------------------------------------------------------
def update_patient(conn, args):
    _validate_patient(conn, args.patient_id)

    updates = []
    params = []
    changed = []

    field_map = {
        "first_name": "first_name", "last_name": "last_name",
        "date_of_birth": "date_of_birth", "gender": "gender",
        "ssn": "ssn", "marital_status": "marital_status",
        "race": "race", "ethnicity": "ethnicity",
        "preferred_language": "preferred_language",
        "primary_phone": "primary_phone", "secondary_phone": "secondary_phone",
        "email": "email", "address_line1": "address_line1",
        "address_line2": "address_line2", "city": "city",
        "state": "state", "zip_code": "zip_code",
        "primary_provider_id": "primary_provider_id",
        "status": "status", "notes": "notes", "customer_id": "customer_id",
    }

    for arg_name, col_name in field_map.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            # Validate enums
            if col_name == "gender":
                _validate_enum(val, VALID_GENDERS, "gender")
            elif col_name == "status":
                _validate_enum(val, VALID_PATIENT_STATUSES, "status")
            elif col_name == "marital_status":
                _validate_enum(val, VALID_MARITAL_STATUSES, "marital-status")
            elif col_name == "ethnicity":
                _validate_enum(val, VALID_ETHNICITIES, "ethnicity")
            elif col_name == "primary_provider_id":
                row = conn.execute("SELECT id FROM employee WHERE id = ?", (val,)).fetchone()
                if not row:
                    err(f"Provider (employee) {val} not found")
            elif col_name == "customer_id":
                row = conn.execute("SELECT id FROM customer WHERE id = ?", (val,)).fetchone()
                if not row:
                    err(f"Customer {val} not found")
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    if not updates:
        err("No fields to update")

    # Recompute full_name if first/last changed
    if "first_name" in changed or "last_name" in changed:
        row = conn.execute("SELECT first_name, last_name FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone()
        fn = getattr(args, "first_name", None) or row[0]
        ln = getattr(args, "last_name", None) or row[1]
        updates.append("full_name = ?")
        params.append(f"{fn} {ln}")

    updates.append("updated_at = datetime('now')")
    params.append(args.patient_id)

    conn.execute(f"UPDATE healthclaw_patient SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_patient", args.patient_id, "update-patient", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": args.patient_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 4. list-patients
# ---------------------------------------------------------------------------
def list_patients(conn, args):
    where = ["1=1"]
    params = []

    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)
    if getattr(args, "primary_provider_id", None):
        where.append("primary_provider_id = ?")
        params.append(args.primary_provider_id)
    if getattr(args, "search", None):
        where.append("(full_name LIKE ? OR mrn LIKE ? OR email LIKE ?)")
        s = f"%{args.search}%"
        params.extend([s, s, s])

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_patient WHERE {where_sql}", params).fetchone()[0]

    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_patient WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total,
        "limit": args.limit,
        "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# 5. add-patient-insurance
# ---------------------------------------------------------------------------
def add_patient_insurance(conn, args):
    _validate_patient(conn, args.patient_id)
    _validate_company(conn, args.company_id)

    if not args.payer_name:
        err("--payer-name is required")
    if not args.member_id:
        err("--member-id is required")
    if not args.effective_date:
        err("--effective-date is required")

    insurance_type = getattr(args, "insurance_type", None) or "primary"
    _validate_enum(insurance_type, VALID_INSURANCE_TYPES, "insurance-type")
    plan_type = getattr(args, "plan_type", None)
    _validate_enum(plan_type, VALID_PLAN_TYPES, "plan-type")
    sub_rel = getattr(args, "subscriber_relationship", None) or "self"
    _validate_enum(sub_rel, VALID_SUBSCRIBER_RELATIONSHIPS, "subscriber-relationship")

    ins_id = str(uuid.uuid4())
    naming = get_next_name(conn, "healthclaw_patient_insurance", company_id=args.company_id)
    now = _now_iso()

    conn.execute("""
        INSERT INTO healthclaw_patient_insurance (
            id, naming_series, patient_id, insurance_type, payer_name, payer_id,
            plan_name, plan_type, group_number, member_id,
            subscriber_name, subscriber_dob, subscriber_relationship,
            copay_amount, deductible, deductible_met, out_of_pocket_max,
            effective_date, termination_date, preauth_required,
            status, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        ins_id, naming, args.patient_id, insurance_type,
        args.payer_name, getattr(args, "payer_id", None),
        getattr(args, "plan_name", None), plan_type,
        getattr(args, "group_number", None), args.member_id,
        getattr(args, "subscriber_name", None),
        getattr(args, "subscriber_dob", None), sub_rel,
        str(round_currency(to_decimal(getattr(args, "copay_amount", None) or "0"))),
        str(round_currency(to_decimal(getattr(args, "deductible", None) or "0"))),
        str(round_currency(to_decimal(getattr(args, "deductible_met", None) or "0"))),
        str(round_currency(to_decimal(getattr(args, "out_of_pocket_max", None) or "0"))),
        args.effective_date,
        getattr(args, "termination_date", None),
        1 if getattr(args, "preauth_required", None) == "1" else 0,
        "active", args.company_id, now, now,
    ))
    audit(conn, "healthclaw_patient_insurance", ins_id, "add-patient-insurance", args.company_id)
    conn.commit()
    ok({"id": ins_id, "naming_series": naming, "insurance_type": insurance_type})


# ---------------------------------------------------------------------------
# 6. update-patient-insurance
# ---------------------------------------------------------------------------
def update_patient_insurance(conn, args):
    ins_id = getattr(args, "insurance_id", None)
    if not ins_id:
        err("--insurance-id is required")
    row = conn.execute("SELECT id FROM healthclaw_patient_insurance WHERE id = ?", (ins_id,)).fetchone()
    if not row:
        err(f"Insurance {ins_id} not found")

    updates = []
    params = []
    changed = []
    field_map = {
        "insurance_type": "insurance_type", "payer_name": "payer_name",
        "payer_id": "payer_id", "plan_name": "plan_name", "plan_type": "plan_type",
        "group_number": "group_number", "member_id": "member_id",
        "subscriber_name": "subscriber_name", "subscriber_dob": "subscriber_dob",
        "subscriber_relationship": "subscriber_relationship",
        "effective_date": "effective_date", "termination_date": "termination_date",
        "status": "status",
    }
    money_fields = {"copay_amount", "deductible", "deductible_met", "out_of_pocket_max"}

    for arg_name, col_name in field_map.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "insurance_type":
                _validate_enum(val, VALID_INSURANCE_TYPES, "insurance-type")
            elif col_name == "plan_type":
                _validate_enum(val, VALID_PLAN_TYPES, "plan-type")
            elif col_name == "subscriber_relationship":
                _validate_enum(val, VALID_SUBSCRIBER_RELATIONSHIPS, "subscriber-relationship")
            elif col_name == "status":
                _validate_enum(val, VALID_INSURANCE_STATUSES, "status")
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    for mf in money_fields:
        val = getattr(args, mf, None)
        if val is not None:
            updates.append(f"{mf} = ?")
            params.append(str(round_currency(to_decimal(val))))
            changed.append(mf)

    if getattr(args, "preauth_required", None) is not None:
        updates.append("preauth_required = ?")
        params.append(1 if args.preauth_required == "1" else 0)
        changed.append("preauth_required")

    if not updates:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(ins_id)
    conn.execute(f"UPDATE healthclaw_patient_insurance SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_patient_insurance", ins_id, "update-patient-insurance", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": ins_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 7. list-patient-insurances
# ---------------------------------------------------------------------------
def list_patient_insurances(conn, args):
    where = ["1=1"]
    params = []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?")
        params.append(args.patient_id)
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)
    if getattr(args, "insurance_type", None):
        where.append("insurance_type = ?")
        params.append(args.insurance_type)

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_patient_insurance WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_patient_insurance WHERE {where_sql} ORDER BY insurance_type ASC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# 8. add-allergy
# ---------------------------------------------------------------------------
def add_allergy(conn, args):
    _validate_patient(conn, args.patient_id)
    if not args.allergen:
        err("--allergen is required")
    allergen_type = getattr(args, "allergen_type", None) or "other"
    _validate_enum(allergen_type, VALID_ALLERGEN_TYPES, "allergen-type")
    severity = getattr(args, "severity", None) or "moderate"
    _validate_enum(severity, VALID_SEVERITIES, "severity")

    noted_by = getattr(args, "noted_by_id", None)
    if noted_by:
        row = conn.execute("SELECT id FROM employee WHERE id = ?", (noted_by,)).fetchone()
        if not row:
            err(f"Employee {noted_by} not found")

    allergy_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_allergy (
            id, patient_id, allergen, allergen_type, reaction, severity,
            onset_date, status, noted_by_id, notes, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        allergy_id, args.patient_id, args.allergen, allergen_type,
        getattr(args, "reaction", None), severity,
        getattr(args, "onset_date", None), "active",
        noted_by, getattr(args, "notes", None), now, now,
    ))
    audit(conn, "healthclaw_allergy", allergy_id, "add-allergy", None)
    conn.commit()
    ok({"id": allergy_id, "allergen": args.allergen, "severity": severity})


# ---------------------------------------------------------------------------
# 9. update-allergy
# ---------------------------------------------------------------------------
def update_allergy(conn, args):
    allergy_id = getattr(args, "allergy_id", None)
    if not allergy_id:
        err("--allergy-id is required")
    row = conn.execute("SELECT id FROM healthclaw_allergy WHERE id = ?", (allergy_id,)).fetchone()
    if not row:
        err(f"Allergy {allergy_id} not found")

    updates = []
    params = []
    changed = []
    for arg_name, col_name in {
        "allergen": "allergen", "allergen_type": "allergen_type",
        "reaction": "reaction", "severity": "severity",
        "onset_date": "onset_date", "status": "status", "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "allergen_type":
                _validate_enum(val, VALID_ALLERGEN_TYPES, "allergen-type")
            elif col_name == "severity":
                _validate_enum(val, VALID_SEVERITIES, "severity")
            elif col_name == "status":
                _validate_enum(val, VALID_ALLERGY_STATUSES, "status")
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    if not updates:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(allergy_id)
    conn.execute(f"UPDATE healthclaw_allergy SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_allergy", allergy_id, "update-allergy", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": allergy_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 10. list-allergies
# ---------------------------------------------------------------------------
def list_allergies(conn, args):
    where = ["1=1"]
    params = []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?")
        params.append(args.patient_id)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)
    if getattr(args, "allergen_type", None):
        where.append("allergen_type = ?")
        params.append(args.allergen_type)

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_allergy WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_allergy WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# 11. add-medical-history
# ---------------------------------------------------------------------------
def add_medical_history(conn, args):
    _validate_patient(conn, args.patient_id)
    condition = getattr(args, "condition", None)
    if not condition:
        err("--condition is required")

    medhist_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_medical_history (
            id, patient_id, condition, icd10_code, diagnosis_date,
            resolution_date, status, notes, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        medhist_id, args.patient_id, condition,
        getattr(args, "icd10_code", None),
        getattr(args, "diagnosis_date", None),
        getattr(args, "resolution_date", None),
        getattr(args, "medhist_status", None) or "active",
        getattr(args, "notes", None), now, now,
    ))
    audit(conn, "healthclaw_medical_history", medhist_id, "add-medical-history", None)
    conn.commit()
    ok({"id": medhist_id, "condition": condition})


# ---------------------------------------------------------------------------
# 12. update-medical-history
# ---------------------------------------------------------------------------
def update_medical_history(conn, args):
    mh_id = getattr(args, "medical_history_id", None)
    if not mh_id:
        err("--medical-history-id is required")
    row = conn.execute("SELECT id FROM healthclaw_medical_history WHERE id = ?", (mh_id,)).fetchone()
    if not row:
        err(f"Medical history {mh_id} not found")

    updates = []
    params = []
    changed = []
    for arg_name, col_name in {
        "condition": "condition", "icd10_code": "icd10_code",
        "diagnosis_date": "diagnosis_date", "resolution_date": "resolution_date",
        "medhist_status": "status", "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "status":
                _validate_enum(val, VALID_MEDHIST_STATUSES, "status")
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    if not updates:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(mh_id)
    conn.execute(f"UPDATE healthclaw_medical_history SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_medical_history", mh_id, "update-medical-history", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": mh_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 13. list-medical-history
# ---------------------------------------------------------------------------
def list_medical_history(conn, args):
    where = ["1=1"]
    params = []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?")
        params.append(args.patient_id)
    if getattr(args, "medhist_status", None):
        where.append("status = ?")
        params.append(args.medhist_status)
    if getattr(args, "search", None):
        where.append("(condition LIKE ? OR icd10_code LIKE ?)")
        s = f"%{args.search}%"
        params.extend([s, s])

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_medical_history WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_medical_history WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# 14. add-patient-contact
# ---------------------------------------------------------------------------
def add_patient_contact(conn, args):
    _validate_patient(conn, args.patient_id)
    contact_name = getattr(args, "contact_name", None)
    if not contact_name:
        err("--contact-name is required")
    contact_type = getattr(args, "contact_type", None) or "emergency"
    _validate_enum(contact_type, VALID_CONTACT_TYPES, "contact-type")

    contact_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_patient_contact (
            id, patient_id, contact_type, name, relationship, phone,
            email, address, is_primary, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        contact_id, args.patient_id, contact_type, contact_name,
        getattr(args, "relationship", None),
        getattr(args, "contact_phone", None),
        getattr(args, "contact_email", None),
        getattr(args, "contact_address", None),
        1 if getattr(args, "is_primary", None) == "1" else 0,
        now, now,
    ))
    audit(conn, "healthclaw_patient_contact", contact_id, "add-patient-contact", None)
    conn.commit()
    ok({"id": contact_id, "name": contact_name, "contact_type": contact_type})


# ---------------------------------------------------------------------------
# 15. update-patient-contact
# ---------------------------------------------------------------------------
def update_patient_contact(conn, args):
    contact_id = getattr(args, "contact_id", None)
    if not contact_id:
        err("--contact-id is required")
    row = conn.execute("SELECT id FROM healthclaw_patient_contact WHERE id = ?", (contact_id,)).fetchone()
    if not row:
        err(f"Contact {contact_id} not found")

    updates = []
    params = []
    changed = []
    for arg_name, col_name in {
        "contact_type": "contact_type", "contact_name": "name",
        "relationship": "relationship", "contact_phone": "phone",
        "contact_email": "email", "contact_address": "address",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            if col_name == "contact_type":
                _validate_enum(val, VALID_CONTACT_TYPES, "contact-type")
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    if getattr(args, "is_primary", None) is not None:
        updates.append("is_primary = ?")
        params.append(1 if args.is_primary == "1" else 0)
        changed.append("is_primary")

    if not updates:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(contact_id)
    conn.execute(f"UPDATE healthclaw_patient_contact SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_patient_contact", contact_id, "update-patient-contact", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": contact_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 16. add-consent
# ---------------------------------------------------------------------------
def add_consent(conn, args):
    _validate_patient(conn, args.patient_id)
    _validate_company(conn, args.company_id)

    consent_type = getattr(args, "consent_type", None)
    if not consent_type:
        err("--consent-type is required")
    _validate_enum(consent_type, VALID_CONSENT_TYPES, "consent-type")

    granted_date = getattr(args, "granted_date", None)
    if not granted_date:
        err("--granted-date is required")

    obtained_by = getattr(args, "obtained_by_id", None)
    if obtained_by:
        row = conn.execute("SELECT id FROM employee WHERE id = ?", (obtained_by,)).fetchone()
        if not row:
            err(f"Employee {obtained_by} not found")

    consent_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_consent (
            id, patient_id, consent_type, description, granted_date,
            expiration_date, revoked_date, status, witness_name,
            obtained_by_id, notes, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        consent_id, args.patient_id, consent_type,
        getattr(args, "description", None), granted_date,
        getattr(args, "expiration_date", None), None,
        "active",
        getattr(args, "witness_name", None),
        obtained_by,
        getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_consent", consent_id, "add-consent", args.company_id)
    conn.commit()
    ok({"id": consent_id, "consent_type": consent_type, "status": "active"})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-patient": add_patient,
    "get-patient": get_patient,
    "update-patient": update_patient,
    "list-patients": list_patients,
    "add-patient-insurance": add_patient_insurance,
    "update-patient-insurance": update_patient_insurance,
    "list-patient-insurances": list_patient_insurances,
    "add-allergy": add_allergy,
    "update-allergy": update_allergy,
    "list-allergies": list_allergies,
    "add-medical-history": add_medical_history,
    "update-medical-history": update_medical_history,
    "list-medical-history": list_medical_history,
    "add-patient-contact": add_patient_contact,
    "update-patient-contact": update_patient_contact,
    "add-consent": add_consent,
}
