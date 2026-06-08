"""HealthClaw — lab domain module

Actions for the lab/diagnostics domain (5 tables, 14 actions).
Imported by db_query.py (unified router).
"""
import json
import os
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

    # Register HealthClaw naming prefixes (lab domain)
    ENTITY_PREFIXES.setdefault("healthclaw_lab_order", "LAB-")
    ENTITY_PREFIXES.setdefault("healthclaw_imaging_order", "IMG-")
except ImportError:
    pass

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------
VALID_LAB_ORDER_STATUSES = ("ordered", "collected", "received", "in_progress", "completed", "cancelled")
VALID_LAB_PRIORITIES = ("stat", "urgent", "routine")
VALID_LAB_TEST_STATUSES = ("pending", "in_progress", "completed", "cancelled")
VALID_LAB_RESULT_FLAGS = ("normal", "low", "high", "critical_low", "critical_high", "abnormal")
VALID_IMAGING_MODALITIES = ("xray", "ct", "mri", "ultrasound", "mammography", "fluoroscopy", "nuclear", "pet", "dexa", "other")
VALID_IMAGING_PRIORITIES = ("stat", "urgent", "routine")
VALID_IMAGING_ORDER_STATUSES = ("ordered", "scheduled", "in_progress", "completed", "read", "cancelled")
VALID_LATERALITIES = ("left", "right", "bilateral", "not_applicable")
VALID_IMAGING_RESULT_STATUSES = ("preliminary", "final", "addended", "corrected")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
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


def _validate_encounter(conn, encounter_id):
    if not encounter_id:
        err("--encounter-id is required")
    if not conn.execute("SELECT id FROM healthclaw_encounter WHERE id = ?", (encounter_id,)).fetchone():
        err(f"Encounter {encounter_id} not found")


def _validate_enum(value, valid_values, field_name):
    if value and value not in valid_values:
        err(f"Invalid {field_name}: {value}. Must be one of: {', '.join(valid_values)}")


# ---------------------------------------------------------------------------
# 1. add-lab-order
# ---------------------------------------------------------------------------
def add_lab_order(conn, args):
    _validate_company(conn, args.company_id)
    _validate_encounter(conn, args.encounter_id)
    _validate_patient(conn, args.patient_id)

    ordering_provider_id = getattr(args, "ordering_provider_id", None)
    if not ordering_provider_id:
        err("--ordering-provider-id is required")
    if not conn.execute("SELECT id FROM employee WHERE id = ?", (ordering_provider_id,)).fetchone():
        err(f"Provider (employee) {ordering_provider_id} not found")

    order_date = getattr(args, "order_date", None)
    if not order_date:
        err("--order-date is required")

    priority = getattr(args, "priority", None) or "routine"
    _validate_enum(priority, VALID_LAB_PRIORITIES, "priority")

    # Optional order link
    order_id = getattr(args, "order_id", None)
    if order_id:
        if not conn.execute("SELECT id FROM healthclaw_order WHERE id = ?", (order_id,)).fetchone():
            err(f"Order {order_id} not found")

    lab_order_id = str(uuid.uuid4())
    naming = get_next_name(conn, "healthclaw_lab_order", company_id=args.company_id)
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_lab_order (
            id, naming_series, order_id, encounter_id, patient_id,
            ordering_provider_id, order_date, priority, fasting_required,
            clinical_indication, specimen_type, collection_date, received_date,
            status, notes, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        lab_order_id, naming, order_id, args.encounter_id, args.patient_id,
        ordering_provider_id, order_date, priority,
        1 if getattr(args, "fasting_required", None) == "1" else 0,
        getattr(args, "clinical_indication", None),
        getattr(args, "specimen_type", None),
        getattr(args, "collection_date", None),
        getattr(args, "received_date", None),
        "ordered",
        getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_lab_order", lab_order_id, "add-lab-order", args.company_id)
    conn.commit()
    ok({"id": lab_order_id, "naming_series": naming, "order_date": order_date, "status": "ordered"})


# ---------------------------------------------------------------------------
# 2. update-lab-order
# ---------------------------------------------------------------------------
def update_lab_order(conn, args):
    lab_order_id = getattr(args, "lab_order_id", None)
    if not lab_order_id:
        err("--lab-order-id is required")
    if not conn.execute("SELECT id FROM healthclaw_lab_order WHERE id = ?", (lab_order_id,)).fetchone():
        err(f"Lab order {lab_order_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "clinical_indication": "clinical_indication",
        "specimen_type": "specimen_type",
        "collection_date": "collection_date",
        "received_date": "received_date",
        "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    priority = getattr(args, "priority", None)
    if priority is not None:
        _validate_enum(priority, VALID_LAB_PRIORITIES, "priority")
        updates.append("priority = ?")
        params.append(priority)
        changed.append("priority")

    lab_order_status = getattr(args, "lab_order_status", None)
    if lab_order_status is not None:
        _validate_enum(lab_order_status, VALID_LAB_ORDER_STATUSES, "status")
        updates.append("status = ?")
        params.append(lab_order_status)
        changed.append("status")

    if getattr(args, "fasting_required", None) is not None:
        updates.append("fasting_required = ?")
        params.append(1 if args.fasting_required == "1" else 0)
        changed.append("fasting_required")

    if not updates:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(lab_order_id)
    conn.execute(f"UPDATE healthclaw_lab_order SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_lab_order", lab_order_id, "update-lab-order", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": lab_order_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 3. get-lab-order
# ---------------------------------------------------------------------------
def get_lab_order(conn, args):
    lab_order_id = getattr(args, "lab_order_id", None)
    if not lab_order_id:
        err("--lab-order-id is required")
    row = conn.execute("SELECT * FROM healthclaw_lab_order WHERE id = ?", (lab_order_id,)).fetchone()
    if not row:
        err(f"Lab order {lab_order_id} not found")
    data = row_to_dict(row)

    # Enrich: patient name
    pat = conn.execute("SELECT full_name FROM healthclaw_patient WHERE id = ?", (data["patient_id"],)).fetchone()
    if pat:
        data["patient_name"] = pat[0]
    # Enrich: ordering provider name
    prov = conn.execute("SELECT full_name FROM employee WHERE id = ?", (data["ordering_provider_id"],)).fetchone()
    if prov:
        data["ordering_provider_name"] = prov[0]
    # Enrich: test count
    data["test_count"] = conn.execute(
        "SELECT COUNT(*) FROM healthclaw_lab_test WHERE lab_order_id = ?", (lab_order_id,)
    ).fetchone()[0]
    ok(data)


# ---------------------------------------------------------------------------
# 4. list-lab-orders
# ---------------------------------------------------------------------------
def list_lab_orders(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?")
        params.append(args.patient_id)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "ordering_provider_id", None):
        where.append("ordering_provider_id = ?")
        params.append(args.ordering_provider_id)

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_lab_order WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_lab_order WHERE {where_sql} ORDER BY order_date DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# 5. add-lab-test
# ---------------------------------------------------------------------------
def add_lab_test(conn, args):
    lab_order_id = getattr(args, "lab_order_id", None)
    if not lab_order_id:
        err("--lab-order-id is required")
    if not conn.execute("SELECT id FROM healthclaw_lab_order WHERE id = ?", (lab_order_id,)).fetchone():
        err(f"Lab order {lab_order_id} not found")

    test_code = getattr(args, "test_code", None)
    if not test_code:
        err("--test-code is required")
    test_name = getattr(args, "test_name", None)
    if not test_name:
        err("--test-name is required")

    lt_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_lab_test (
            id, lab_order_id, test_code, test_name, cpt_code,
            status, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?)
    """, (
        lt_id, lab_order_id, test_code, test_name,
        getattr(args, "cpt_code", None),
        "pending", now, now,
    ))
    audit(conn, "healthclaw_lab_test", lt_id, "add-lab-test", None)
    conn.commit()
    ok({"id": lt_id, "lab_order_id": lab_order_id, "test_code": test_code, "status": "pending"})


# ---------------------------------------------------------------------------
# 6. list-lab-tests
# ---------------------------------------------------------------------------
def list_lab_tests(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "lab_order_id", None):
        where.append("lab_order_id = ?")
        params.append(args.lab_order_id)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_lab_test WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_lab_test WHERE {where_sql} ORDER BY created_at ASC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# 7. add-lab-result
# ---------------------------------------------------------------------------
def add_lab_result(conn, args):
    lab_test_id = getattr(args, "lab_test_id", None)
    if not lab_test_id:
        err("--lab-test-id is required")
    if not conn.execute("SELECT id FROM healthclaw_lab_test WHERE id = ?", (lab_test_id,)).fetchone():
        err(f"Lab test {lab_test_id} not found")

    component_name = getattr(args, "component_name", None)
    if not component_name:
        err("--component-name is required")
    value = getattr(args, "result_value", None)
    if not value:
        err("--result-value is required")
    result_date = getattr(args, "result_date", None)
    if not result_date:
        err("--result-date is required")

    flag = getattr(args, "flag", None)
    _validate_enum(flag, VALID_LAB_RESULT_FLAGS, "flag")

    # Optional FK checks
    performed_by_id = getattr(args, "performed_by_id", None)
    if performed_by_id:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (performed_by_id,)).fetchone():
            err(f"Employee {performed_by_id} not found")
    verified_by_id = getattr(args, "verified_by_id", None)
    if verified_by_id:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (verified_by_id,)).fetchone():
            err(f"Employee {verified_by_id} not found")

    lr_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_lab_result (
            id, lab_test_id, component_name, value, unit,
            reference_low, reference_high, flag,
            result_date, performed_by_id, verified_by_id, notes, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        lr_id, lab_test_id, component_name, value,
        getattr(args, "unit", None),
        getattr(args, "reference_low", None),
        getattr(args, "reference_high", None),
        flag, result_date,
        performed_by_id, verified_by_id,
        getattr(args, "notes", None), now,
    ))
    audit(conn, "healthclaw_lab_result", lr_id, "add-lab-result", None)
    conn.commit()
    ok({"id": lr_id, "lab_test_id": lab_test_id, "component_name": component_name, "flag": flag})


# ---------------------------------------------------------------------------
# 8. list-lab-results
# ---------------------------------------------------------------------------
def list_lab_results(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "lab_test_id", None):
        where.append("lab_test_id = ?")
        params.append(args.lab_test_id)
    if getattr(args, "flag", None):
        where.append("flag = ?")
        params.append(args.flag)

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_lab_result WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_lab_result WHERE {where_sql} ORDER BY result_date DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# 9. add-imaging-order
# ---------------------------------------------------------------------------
def add_imaging_order(conn, args):
    _validate_company(conn, args.company_id)
    _validate_encounter(conn, args.encounter_id)
    _validate_patient(conn, args.patient_id)

    ordering_provider_id = getattr(args, "ordering_provider_id", None)
    if not ordering_provider_id:
        err("--ordering-provider-id is required")
    if not conn.execute("SELECT id FROM employee WHERE id = ?", (ordering_provider_id,)).fetchone():
        err(f"Provider (employee) {ordering_provider_id} not found")

    modality = getattr(args, "modality", None)
    if not modality:
        err("--modality is required")
    _validate_enum(modality, VALID_IMAGING_MODALITIES, "modality")

    body_part = getattr(args, "body_part", None)
    if not body_part:
        err("--body-part is required")

    order_date = getattr(args, "order_date", None)
    if not order_date:
        err("--order-date is required")

    priority = getattr(args, "priority", None) or "routine"
    _validate_enum(priority, VALID_IMAGING_PRIORITIES, "priority")

    laterality = getattr(args, "laterality", None)
    _validate_enum(laterality, VALID_LATERALITIES, "laterality")

    # Optional order link
    order_id = getattr(args, "order_id", None)
    if order_id:
        if not conn.execute("SELECT id FROM healthclaw_order WHERE id = ?", (order_id,)).fetchone():
            err(f"Order {order_id} not found")

    img_order_id = str(uuid.uuid4())
    naming = get_next_name(conn, "healthclaw_imaging_order", company_id=args.company_id)
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_imaging_order (
            id, naming_series, order_id, encounter_id, patient_id,
            ordering_provider_id, modality, body_part, laterality,
            cpt_code, order_date, priority, clinical_indication,
            contrast, status, scheduled_date, notes, company_id,
            created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        img_order_id, naming, order_id, args.encounter_id, args.patient_id,
        ordering_provider_id, modality, body_part, laterality,
        getattr(args, "cpt_code", None),
        order_date, priority,
        getattr(args, "clinical_indication", None),
        1 if getattr(args, "contrast", None) == "1" else 0,
        "ordered",
        getattr(args, "scheduled_date", None),
        getattr(args, "notes", None),
        args.company_id, now, now,
    ))
    audit(conn, "healthclaw_imaging_order", img_order_id, "add-imaging-order", args.company_id)
    conn.commit()
    ok({"id": img_order_id, "naming_series": naming, "modality": modality, "body_part": body_part, "status": "ordered"})


# ---------------------------------------------------------------------------
# 10. update-imaging-order
# ---------------------------------------------------------------------------
def update_imaging_order(conn, args):
    img_order_id = getattr(args, "imaging_order_id", None)
    if not img_order_id:
        err("--imaging-order-id is required")
    if not conn.execute("SELECT id FROM healthclaw_imaging_order WHERE id = ?", (img_order_id,)).fetchone():
        err(f"Imaging order {img_order_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "body_part": "body_part",
        "cpt_code": "cpt_code",
        "clinical_indication": "clinical_indication",
        "scheduled_date": "scheduled_date",
        "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    modality = getattr(args, "modality", None)
    if modality is not None:
        _validate_enum(modality, VALID_IMAGING_MODALITIES, "modality")
        updates.append("modality = ?")
        params.append(modality)
        changed.append("modality")

    laterality = getattr(args, "laterality", None)
    if laterality is not None:
        _validate_enum(laterality, VALID_LATERALITIES, "laterality")
        updates.append("laterality = ?")
        params.append(laterality)
        changed.append("laterality")

    priority = getattr(args, "priority", None)
    if priority is not None:
        _validate_enum(priority, VALID_IMAGING_PRIORITIES, "priority")
        updates.append("priority = ?")
        params.append(priority)
        changed.append("priority")

    imaging_order_status = getattr(args, "imaging_order_status", None)
    if imaging_order_status is not None:
        _validate_enum(imaging_order_status, VALID_IMAGING_ORDER_STATUSES, "status")
        updates.append("status = ?")
        params.append(imaging_order_status)
        changed.append("status")

    if getattr(args, "contrast", None) is not None:
        updates.append("contrast = ?")
        params.append(1 if args.contrast == "1" else 0)
        changed.append("contrast")

    if not updates:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(img_order_id)
    conn.execute(f"UPDATE healthclaw_imaging_order SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_imaging_order", img_order_id, "update-imaging-order", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": img_order_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 11. list-imaging-orders
# ---------------------------------------------------------------------------
def list_imaging_orders(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?")
        params.append(args.patient_id)
    if getattr(args, "modality", None):
        where.append("modality = ?")
        params.append(args.modality)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_imaging_order WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_imaging_order WHERE {where_sql} ORDER BY order_date DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# 12. add-imaging-result
# ---------------------------------------------------------------------------
def add_imaging_result(conn, args):
    imaging_order_id = getattr(args, "imaging_order_id", None)
    if not imaging_order_id:
        err("--imaging-order-id is required")
    if not conn.execute("SELECT id FROM healthclaw_imaging_order WHERE id = ?", (imaging_order_id,)).fetchone():
        err(f"Imaging order {imaging_order_id} not found")

    report_date = getattr(args, "report_date", None)
    if not report_date:
        err("--report-date is required")

    # Optional FK check
    radiologist_id = getattr(args, "radiologist_id", None)
    if radiologist_id:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (radiologist_id,)).fetchone():
            err(f"Radiologist (employee) {radiologist_id} not found")

    ir_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute("""
        INSERT INTO healthclaw_imaging_result (
            id, imaging_order_id, radiologist_id, findings, impression,
            recommendation, critical_finding, report_date, status,
            addendum, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        ir_id, imaging_order_id, radiologist_id,
        getattr(args, "findings", None),
        getattr(args, "impression", None),
        getattr(args, "recommendation", None),
        1 if getattr(args, "critical_finding", None) == "1" else 0,
        report_date, "preliminary",
        getattr(args, "addendum", None),
        now, now,
    ))
    audit(conn, "healthclaw_imaging_result", ir_id, "add-imaging-result", None)
    conn.commit()
    ok({"id": ir_id, "imaging_order_id": imaging_order_id, "report_date": report_date, "status": "preliminary"})


# ---------------------------------------------------------------------------
# 13. update-imaging-result
# ---------------------------------------------------------------------------
def update_imaging_result(conn, args):
    ir_id = getattr(args, "imaging_result_id", None)
    if not ir_id:
        err("--imaging-result-id is required")
    if not conn.execute("SELECT id FROM healthclaw_imaging_result WHERE id = ?", (ir_id,)).fetchone():
        err(f"Imaging result {ir_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "findings": "findings", "impression": "impression",
        "recommendation": "recommendation", "addendum": "addendum",
        "report_date": "report_date",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    imaging_result_status = getattr(args, "imaging_result_status", None)
    if imaging_result_status is not None:
        _validate_enum(imaging_result_status, VALID_IMAGING_RESULT_STATUSES, "status")
        updates.append("status = ?")
        params.append(imaging_result_status)
        changed.append("status")

    radiologist_id = getattr(args, "radiologist_id", None)
    if radiologist_id is not None:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (radiologist_id,)).fetchone():
            err(f"Radiologist (employee) {radiologist_id} not found")
        updates.append("radiologist_id = ?")
        params.append(radiologist_id)
        changed.append("radiologist_id")

    if getattr(args, "critical_finding", None) is not None:
        updates.append("critical_finding = ?")
        params.append(1 if args.critical_finding == "1" else 0)
        changed.append("critical_finding")

    if not updates:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(ir_id)
    conn.execute(f"UPDATE healthclaw_imaging_result SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_imaging_result", ir_id, "update-imaging-result", None, {"updated_fields": changed})
    conn.commit()
    ok({"id": ir_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 14. list-imaging-results
# ---------------------------------------------------------------------------
def list_imaging_results(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "imaging_order_id", None):
        where.append("imaging_order_id = ?")
        params.append(args.imaging_order_id)
    if getattr(args, "status", None):
        where.append("status = ?")
        params.append(args.status)

    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_imaging_result WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_imaging_result WHERE {where_sql} ORDER BY report_date DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-lab-order": add_lab_order,
    "update-lab-order": update_lab_order,
    "get-lab-order": get_lab_order,
    "list-lab-orders": list_lab_orders,
    "add-lab-test": add_lab_test,
    "list-lab-tests": list_lab_tests,
    "add-lab-result": add_lab_result,
    "list-lab-results": list_lab_results,
    "add-imaging-order": add_imaging_order,
    "update-imaging-order": update_imaging_order,
    "list-imaging-orders": list_imaging_orders,
    "add-imaging-result": add_imaging_result,
    "update-imaging-result": update_imaging_result,
    "list-imaging-results": list_imaging_results,
}
