"""ERPClaw Advanced Accounting -- Revenue Recognition (ASC 606) domain module

Actions for revenue contracts, performance obligations, variable consideration,
and revenue schedules (4 tables, 14 actions).
Imported by db_query.py (unified router).
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.naming import get_next_name, ENTITY_PREFIXES
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.query import dynamic_update

    ENTITY_PREFIXES.setdefault("revenue_contract", "RCON-")
except ImportError:
    pass

SKILL = "erpclaw-accounting-adv"

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------
VALID_CONTRACT_STATUSES = ("draft", "active", "modified", "completed", "terminated")
VALID_RECOGNITION_METHODS = ("point_in_time", "over_time")
VALID_RECOGNITION_BASES = ("output", "input", "time")
VALID_OBLIGATION_STATUSES = ("unsatisfied", "partially_satisfied", "satisfied")
VALID_VC_METHODS = ("expected_value", "most_likely")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _validate_company(conn, company_id):
    if not company_id:
        err("--company-id is required")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")


def _validate_contract(conn, contract_id):
    if not contract_id:
        err("--contract-id is required")
    row = conn.execute("SELECT id FROM advacct_revenue_contract WHERE id = ?", (contract_id,)).fetchone()
    if not row:
        err(f"Revenue contract {contract_id} not found")


# ===========================================================================
# 1. add-revenue-contract
# ===========================================================================
def add_revenue_contract(conn, args):
    _validate_company(conn, args.company_id)
    customer_name = getattr(args, "customer_name", None)
    if not customer_name:
        err("--customer-name is required")

    total_value = getattr(args, "total_value", None) or "0"
    # Validate it's a valid decimal
    try:
        Decimal(total_value)
    except Exception:
        err(f"Invalid total-value: {total_value}")

    contract_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    naming = get_next_name(conn, "revenue_contract", company_id=args.company_id)
    now = _now_iso()

    conn.execute("""
        INSERT INTO advacct_revenue_contract (
            id, naming_series, customer_name, contract_number, start_date, end_date,
            total_value, allocated_value, contract_status, modification_count,
            company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        contract_id, naming, customer_name,
        getattr(args, "contract_number", None),
        getattr(args, "start_date", None),
        getattr(args, "end_date", None),
        total_value, "0", "draft", 0,
        args.company_id, now, now,
    ))
    audit(conn, SKILL, "add-revenue-contract", "advacct_revenue_contract", contract_id,
          new_values={"customer_name": customer_name, "total_value": total_value})
    conn.commit()
    ok({
        "id": contract_id, "naming_series": naming,
        "customer_name": customer_name, "contract_status": "draft",
        "total_value": total_value,
    })


# ===========================================================================
# 2. update-revenue-contract
# ===========================================================================
def update_revenue_contract(conn, args):
    contract_id = getattr(args, "id", None)
    if not contract_id:
        err("--id is required")
    if not conn.execute("SELECT id FROM advacct_revenue_contract WHERE id = ?", (contract_id,)).fetchone():
        err(f"Revenue contract {contract_id} not found")

    data, changed = {}, []
    for arg_name, col_name in {
        "customer_name": "customer_name",
        "contract_number": "contract_number",
        "start_date": "start_date",
        "end_date": "end_date",
        "total_value": "total_value",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            data[col_name] = val
            changed.append(col_name)

    contract_status = getattr(args, "contract_status", None)
    if contract_status:
        if contract_status not in VALID_CONTRACT_STATUSES:
            err(f"Invalid contract-status: {contract_status}. Must be one of: {', '.join(VALID_CONTRACT_STATUSES)}")
        data["contract_status"] = contract_status
        changed.append("contract_status")

    if not data:
        err("No fields to update")

    data["updated_at"] = _now_iso()
    sql, params = dynamic_update("advacct_revenue_contract", data, where={"id": contract_id})
    conn.execute(sql, params)
    audit(conn, SKILL, "update-revenue-contract", "advacct_revenue_contract", contract_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": contract_id, "updated_fields": changed})


# ===========================================================================
# 3. get-revenue-contract
# ===========================================================================
def get_revenue_contract(conn, args):
    contract_id = getattr(args, "id", None)
    if not contract_id:
        err("--id is required")
    row = conn.execute("SELECT * FROM advacct_revenue_contract WHERE id = ?", (contract_id,)).fetchone()
    if not row:
        err(f"Revenue contract {contract_id} not found")
    data = row_to_dict(row)

    # Include obligations
    obligations = conn.execute(
        "SELECT * FROM advacct_performance_obligation WHERE contract_id = ? ORDER BY created_at",
        (contract_id,)
    ).fetchall()
    data["obligations"] = [row_to_dict(o) for o in obligations]
    data["obligation_count"] = len(obligations)

    # Include variable considerations
    vcs = conn.execute(
        "SELECT * FROM advacct_variable_consideration WHERE contract_id = ? ORDER BY created_at",
        (contract_id,)
    ).fetchall()
    data["variable_considerations"] = [row_to_dict(v) for v in vcs]

    ok(data)


# ===========================================================================
# 4. list-revenue-contracts
# ===========================================================================
def list_revenue_contracts(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "contract_status", None):
        where.append("contract_status = ?")
        params.append(args.contract_status)
    if getattr(args, "search", None):
        where.append("(LOWER(customer_name) LIKE LOWER(?) OR LOWER(contract_number) LIKE LOWER(?))")
        params.extend([f"%{args.search}%", f"%{args.search}%"])

    where_sql = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM advacct_revenue_contract WHERE {where_sql}", params
    ).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM advacct_revenue_contract WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ===========================================================================
# 5. add-performance-obligation
# ===========================================================================
def add_performance_obligation(conn, args):
    contract_id = getattr(args, "contract_id", None)
    _validate_contract(conn, contract_id)
    _validate_company(conn, args.company_id)

    name = getattr(args, "name", None)
    if not name:
        err("--name is required")

    standalone_price = getattr(args, "standalone_price", None) or "0"
    recognition_method = getattr(args, "recognition_method", None) or "over_time"
    if recognition_method not in VALID_RECOGNITION_METHODS:
        err(f"Invalid recognition-method: {recognition_method}. Must be one of: {', '.join(VALID_RECOGNITION_METHODS)}")

    recognition_basis = getattr(args, "recognition_basis", None) or "time"
    if recognition_basis not in VALID_RECOGNITION_BASES:
        err(f"Invalid recognition-basis: {recognition_basis}. Must be one of: {', '.join(VALID_RECOGNITION_BASES)}")

    obligation_id = str(uuid.uuid4())
    now = _now_iso()

    # Auto-allocate price: if standalone_price provided, use it as allocated_price
    allocated_price = standalone_price

    conn.execute("""
        INSERT INTO advacct_performance_obligation (
            id, contract_id, name, standalone_price, allocated_price,
            recognition_method, recognition_basis, pct_complete,
            obligation_status, satisfied_date, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        obligation_id, contract_id, name, standalone_price, allocated_price,
        recognition_method, recognition_basis, "0",
        "unsatisfied", None, args.company_id, now, now,
    ))

    # Update contract allocated_value
    total_allocated = conn.execute(
        "SELECT COALESCE(SUM(CAST(allocated_price AS NUMERIC)), 0) FROM advacct_performance_obligation WHERE contract_id = ?",
        (contract_id,)
    ).fetchone()[0]
    conn.execute(
        "UPDATE advacct_revenue_contract SET allocated_value = ?, updated_at = ? WHERE id = ?",
        (str(Decimal(str(total_allocated)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), _now_iso(), contract_id)
    )

    audit(conn, SKILL, "add-performance-obligation", "advacct_performance_obligation", obligation_id,
          new_values={"contract_id": contract_id, "name": name, "standalone_price": standalone_price})
    conn.commit()
    ok({
        "id": obligation_id, "contract_id": contract_id, "name": name,
        "standalone_price": standalone_price, "allocated_price": allocated_price,
        "recognition_method": recognition_method, "obligation_status": "unsatisfied",
    })


# ===========================================================================
# 6. list-performance-obligations
# ===========================================================================
def list_performance_obligations(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "contract_id", None):
        where.append("contract_id = ?")
        params.append(args.contract_id)
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "obligation_status", None):
        where.append("obligation_status = ?")
        params.append(args.obligation_status)

    where_sql = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM advacct_performance_obligation WHERE {where_sql}", params
    ).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM advacct_performance_obligation WHERE {where_sql} ORDER BY created_at LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ===========================================================================
# 7. satisfy-performance-obligation
# ===========================================================================
def satisfy_performance_obligation(conn, args):
    ob_id = getattr(args, "id", None)
    if not ob_id:
        err("--id is required")
    row = conn.execute("SELECT * FROM advacct_performance_obligation WHERE id = ?", (ob_id,)).fetchone()
    if not row:
        err(f"Performance obligation {ob_id} not found")

    data = row_to_dict(row)
    if data["obligation_status"] == "satisfied":
        err("Performance obligation is already satisfied")

    pct_complete = getattr(args, "pct_complete", None) or "100"
    try:
        pct = Decimal(pct_complete)
    except Exception:
        err(f"Invalid pct-complete: {pct_complete}")

    if pct < Decimal("0") or pct > Decimal("100"):
        err("pct-complete must be between 0 and 100")

    now = _now_iso()
    if pct == Decimal("100"):
        new_status = "satisfied"
        satisfied_date = now
    elif pct > Decimal("0"):
        new_status = "partially_satisfied"
        satisfied_date = None
    else:
        new_status = "unsatisfied"
        satisfied_date = None

    conn.execute("""
        UPDATE advacct_performance_obligation
        SET pct_complete = ?, obligation_status = ?, satisfied_date = ?, updated_at = ?
        WHERE id = ?
    """, (str(pct), new_status, satisfied_date, now, ob_id))

    audit(conn, SKILL, "satisfy-performance-obligation", "advacct_performance_obligation", ob_id,
          new_values={"pct_complete": str(pct), "obligation_status": new_status})
    conn.commit()
    ok({"id": ob_id, "pct_complete": str(pct), "obligation_status": new_status})


# ===========================================================================
# 8. add-variable-consideration
# ===========================================================================
def add_variable_consideration(conn, args):
    contract_id = getattr(args, "contract_id", None)
    _validate_contract(conn, contract_id)
    _validate_company(conn, args.company_id)

    description = getattr(args, "description", None)
    if not description:
        err("--description is required")

    estimated_amount = getattr(args, "estimated_amount", None) or "0"
    constraint_amount = getattr(args, "constraint_amount", None) or "0"
    method = getattr(args, "method", None) or "expected_value"
    if method not in VALID_VC_METHODS:
        err(f"Invalid method: {method}. Must be one of: {', '.join(VALID_VC_METHODS)}")

    probability = getattr(args, "probability", None) or "0"

    vc_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute("""
        INSERT INTO advacct_variable_consideration (
            id, contract_id, description, estimated_amount, constraint_amount,
            method, probability, company_id, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        vc_id, contract_id, description, estimated_amount, constraint_amount,
        method, probability, args.company_id, now,
    ))
    audit(conn, SKILL, "add-variable-consideration", "advacct_variable_consideration", vc_id,
          new_values={"contract_id": contract_id, "description": description})
    conn.commit()
    ok({
        "id": vc_id, "contract_id": contract_id, "description": description,
        "estimated_amount": estimated_amount, "method": method,
    })


# ===========================================================================
# 9. list-variable-considerations
# ===========================================================================
def list_variable_considerations(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "contract_id", None):
        where.append("contract_id = ?")
        params.append(args.contract_id)
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM advacct_variable_consideration WHERE {where_sql}", params
    ).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM advacct_variable_consideration WHERE {where_sql} ORDER BY created_at LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ===========================================================================
# 10. modify-contract
# ===========================================================================
def modify_contract(conn, args):
    contract_id = getattr(args, "id", None)
    if not contract_id:
        err("--id is required")
    row = conn.execute("SELECT * FROM advacct_revenue_contract WHERE id = ?", (contract_id,)).fetchone()
    if not row:
        err(f"Revenue contract {contract_id} not found")

    data = row_to_dict(row)
    if data["contract_status"] not in ("draft", "active"):
        err(f"Cannot modify contract in status '{data['contract_status']}'. Must be draft or active.")

    now = _now_iso()
    new_count = data["modification_count"] + 1
    conn.execute("""
        UPDATE advacct_revenue_contract
        SET contract_status = 'modified', modification_count = ?, updated_at = ?
        WHERE id = ?
    """, (new_count, now, contract_id))

    audit(conn, SKILL, "modify-contract", "advacct_revenue_contract", contract_id,
          new_values={"contract_status": "modified", "modification_count": new_count})
    conn.commit()
    ok({"id": contract_id, "contract_status": "modified", "modification_count": new_count})


# ===========================================================================
# 11. calculate-revenue-schedule
# ===========================================================================
def calculate_revenue_schedule(conn, args):
    ob_id = getattr(args, "obligation_id", None)
    if not ob_id:
        err("--obligation-id is required")
    row = conn.execute("SELECT * FROM advacct_performance_obligation WHERE id = ?", (ob_id,)).fetchone()
    if not row:
        err(f"Performance obligation {ob_id} not found")

    ob = row_to_dict(row)

    # Get contract for dates
    contract = conn.execute(
        "SELECT * FROM advacct_revenue_contract WHERE id = ?", (ob["contract_id"],)
    ).fetchone()
    if not contract:
        err("Associated contract not found")
    contract_data = row_to_dict(contract)

    start_date = contract_data.get("start_date")
    end_date = contract_data.get("end_date")
    if not start_date or not end_date:
        err("Contract must have start_date and end_date to calculate schedule")

    allocated_price = Decimal(ob["allocated_price"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if allocated_price <= 0:
        err("Allocated price must be greater than zero")

    # Delete existing schedule entries for this obligation
    conn.execute("DELETE FROM advacct_revenue_schedule WHERE obligation_id = ?", (ob_id,))

    # Calculate monthly schedule
    from datetime import date
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    # Count months
    months = (end.year - start.year) * 12 + (end.month - start.month) + 1
    if months <= 0:
        err("End date must be after start date")

    monthly_amount = (allocated_price / Decimal(str(months))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    remainder = allocated_price - (monthly_amount * (months - 1))

    entries_created = 0
    company_id = ob["company_id"]
    now = _now_iso()

    current_year = start.year
    current_month = start.month

    for i in range(months):
        period_date = f"{current_year}-{current_month:02d}-01"
        amount = str(remainder) if i == months - 1 else str(monthly_amount)

        conn.execute("""
            INSERT INTO advacct_revenue_schedule (
                id, obligation_id, period_date, amount, recognized, company_id, created_at
            ) VALUES (?,?,?,?,?,?,?)
        """, (str(uuid.uuid4()), ob_id, period_date, amount, 0, company_id, now))
        entries_created += 1

        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    audit(conn, SKILL, "calculate-revenue-schedule", "advacct_revenue_schedule", ob_id,
          new_values={"entries_created": entries_created, "total_amount": str(allocated_price)})
    conn.commit()
    ok({
        "obligation_id": ob_id, "entries_created": entries_created,
        "monthly_amount": str(monthly_amount), "total_amount": str(allocated_price),
    })


# ===========================================================================
# 12. generate-revenue-entries
# ===========================================================================
def generate_revenue_entries(conn, args):
    ob_id = getattr(args, "obligation_id", None)
    if not ob_id:
        err("--obligation-id is required")
    row = conn.execute("SELECT * FROM advacct_performance_obligation WHERE id = ?", (ob_id,)).fetchone()
    if not row:
        err(f"Performance obligation {ob_id} not found")

    # Get unrecognized schedule entries
    schedules = conn.execute(
        "SELECT * FROM advacct_revenue_schedule WHERE obligation_id = ? AND recognized = 0 ORDER BY period_date",
        (ob_id,)
    ).fetchall()

    if not schedules:
        err("No unrecognized revenue schedule entries found")

    recognized_count = 0
    total_recognized = Decimal("0")

    for sched in schedules:
        s = row_to_dict(sched)
        conn.execute(
            "UPDATE advacct_revenue_schedule SET recognized = 1 WHERE id = ?",
            (s["id"],)
        )
        recognized_count += 1
        total_recognized += Decimal(s["amount"])

    audit(conn, SKILL, "generate-revenue-entries", "advacct_revenue_schedule", ob_id,
          new_values={"recognized_count": recognized_count, "total_recognized": str(total_recognized)})
    conn.commit()
    ok({
        "obligation_id": ob_id,
        "recognized_count": recognized_count,
        "total_recognized": str(total_recognized),
    })


# ===========================================================================
# 13. revenue-waterfall-report
# ===========================================================================
def revenue_waterfall_report(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("c.company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    rows = conn.execute(f"""
        SELECT c.id as contract_id, c.customer_name, c.contract_number,
               c.total_value, c.allocated_value, c.contract_status,
               COUNT(po.id) as obligation_count,
               SUM(CASE WHEN po.obligation_status = 'satisfied' THEN 1 ELSE 0 END) as satisfied_count
        FROM advacct_revenue_contract c
        LEFT JOIN advacct_performance_obligation po ON po.contract_id = c.id
        WHERE {where_sql}
        GROUP BY c.id
        ORDER BY c.created_at DESC
    """, params).fetchall()

    ok({
        "report": "revenue_waterfall",
        "rows": [row_to_dict(r) for r in rows],
        "total_contracts": len(rows),
    })


# ===========================================================================
# 14. revenue-recognition-summary
# ===========================================================================
def revenue_recognition_summary(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("rs.company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    rows = conn.execute(f"""
        SELECT rs.period_date,
               SUM(CAST(rs.amount AS NUMERIC)) as total_amount,
               SUM(CASE WHEN rs.recognized = 1 THEN CAST(rs.amount AS NUMERIC) ELSE 0 END) as recognized_amount,
               SUM(CASE WHEN rs.recognized = 0 THEN CAST(rs.amount AS NUMERIC) ELSE 0 END) as unrecognized_amount,
               COUNT(*) as entry_count
        FROM advacct_revenue_schedule rs
        WHERE {where_sql}
        GROUP BY rs.period_date
        ORDER BY rs.period_date
    """, params).fetchall()

    ok({
        "report": "revenue_recognition_summary",
        "rows": [row_to_dict(r) for r in rows],
        "total_periods": len(rows),
    })


# ---------------------------------------------------------------------------
# Action registry
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-revenue-contract": add_revenue_contract,
    "update-revenue-contract": update_revenue_contract,
    "get-revenue-contract": get_revenue_contract,
    "list-revenue-contracts": list_revenue_contracts,
    "add-performance-obligation": add_performance_obligation,
    "list-performance-obligations": list_performance_obligations,
    "satisfy-performance-obligation": satisfy_performance_obligation,
    "add-variable-consideration": add_variable_consideration,
    "list-variable-considerations": list_variable_considerations,
    "modify-contract": modify_contract,
    "calculate-revenue-schedule": calculate_revenue_schedule,
    "generate-revenue-entries": generate_revenue_entries,
    "revenue-waterfall-report": revenue_waterfall_report,
    "revenue-recognition-summary": revenue_recognition_summary,
}
