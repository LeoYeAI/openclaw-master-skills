"""ERPClaw Advanced Accounting -- Lease Accounting (ASC 842) domain module

Actions for leases, lease payments, and amortization schedules (3 tables, 12 actions).
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

    ENTITY_PREFIXES.setdefault("lease", "LEAS-")
except ImportError:
    pass

SKILL = "erpclaw-accounting-adv"

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------
VALID_LEASE_TYPES = ("operating", "finance")
VALID_LEASE_STATUSES = ("draft", "active", "modified", "expired", "terminated")
VALID_PAYMENT_STATUSES = ("scheduled", "paid", "overdue")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _validate_company(conn, company_id):
    if not company_id:
        err("--company-id is required")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")


def _validate_lease(conn, lease_id):
    if not lease_id:
        err("--id (or --lease-id) is required")
    row = conn.execute("SELECT id FROM advacct_lease WHERE id = ?", (lease_id,)).fetchone()
    if not row:
        err(f"Lease {lease_id} not found")


def _pv_annuity(payment, rate_per_period, periods):
    """Present value of an ordinary annuity using Decimal math."""
    if rate_per_period == Decimal("0"):
        return payment * Decimal(str(periods))
    factor = (Decimal("1") - (Decimal("1") + rate_per_period) ** (-periods)) / rate_per_period
    return (payment * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ===========================================================================
# 1. add-lease
# ===========================================================================
def add_lease(conn, args):
    _validate_company(conn, args.company_id)

    lessee_name = getattr(args, "lessee_name", None)
    if not lessee_name:
        err("--lessee-name is required")
    lessor_name = getattr(args, "lessor_name", None)
    if not lessor_name:
        err("--lessor-name is required")

    monthly_payment = getattr(args, "monthly_payment", None) or "0"
    discount_rate = getattr(args, "discount_rate", None) or "0"
    term_months = int(getattr(args, "term_months", None) or 0)

    lease_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    naming = get_next_name(conn, "lease", company_id=args.company_id)
    now = _now_iso()

    conn.execute("""
        INSERT INTO advacct_lease (
            id, naming_series, lessee_name, lessor_name, asset_description,
            lease_type, start_date, end_date, term_months, monthly_payment,
            annual_escalation, discount_rate, purchase_option_price,
            rou_asset_value, lease_liability, lease_status,
            company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        lease_id, naming, lessee_name, lessor_name,
        getattr(args, "asset_description", None),
        getattr(args, "lease_type", None) or "operating",
        getattr(args, "start_date", None),
        getattr(args, "end_date", None),
        term_months,
        monthly_payment,
        getattr(args, "annual_escalation", None) or "0",
        discount_rate,
        getattr(args, "purchase_option_price", None),
        None, None,  # rou_asset_value, lease_liability -- calculated later
        "draft",
        args.company_id, now, now,
    ))
    audit(conn, SKILL, "add-lease", "advacct_lease", lease_id,
          new_values={"lessee_name": lessee_name, "lessor_name": lessor_name, "term_months": term_months})
    conn.commit()
    ok({
        "id": lease_id, "naming_series": naming,
        "lessee_name": lessee_name, "lessor_name": lessor_name,
        "lease_status": "draft", "term_months": term_months,
    })


# ===========================================================================
# 2. update-lease
# ===========================================================================
def update_lease(conn, args):
    lease_id = getattr(args, "id", None)
    if not lease_id:
        err("--id is required")
    if not conn.execute("SELECT id FROM advacct_lease WHERE id = ?", (lease_id,)).fetchone():
        err(f"Lease {lease_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "lessee_name": "lessee_name",
        "lessor_name": "lessor_name",
        "asset_description": "asset_description",
        "start_date": "start_date",
        "end_date": "end_date",
        "monthly_payment": "monthly_payment",
        "discount_rate": "discount_rate",
        "annual_escalation": "annual_escalation",
        "purchase_option_price": "purchase_option_price",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    lease_type = getattr(args, "lease_type", None)
    if lease_type:
        if lease_type not in VALID_LEASE_TYPES:
            err(f"Invalid lease-type: {lease_type}. Must be one of: {', '.join(VALID_LEASE_TYPES)}")
        updates.append("lease_type = ?")
        params.append(lease_type)
        changed.append("lease_type")

    term_months = getattr(args, "term_months", None)
    if term_months is not None:
        updates.append("term_months = ?")
        params.append(int(term_months))
        changed.append("term_months")

    if not updates:
        err("No fields to update")

    updates.append("updated_at = ?")
    params.append(_now_iso())
    params.append(lease_id)
    conn.execute(f"UPDATE advacct_lease SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-lease", "advacct_lease", lease_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": lease_id, "updated_fields": changed})


# ===========================================================================
# 3. get-lease
# ===========================================================================
def get_lease(conn, args):
    lease_id = getattr(args, "id", None)
    if not lease_id:
        err("--id is required")
    row = conn.execute("SELECT * FROM advacct_lease WHERE id = ?", (lease_id,)).fetchone()
    if not row:
        err(f"Lease {lease_id} not found")
    data = row_to_dict(row)

    # Include payments
    payments = conn.execute(
        "SELECT * FROM advacct_lease_payment WHERE lease_id = ? ORDER BY payment_date",
        (lease_id,)
    ).fetchall()
    data["payments"] = [row_to_dict(p) for p in payments]
    data["payment_count"] = len(payments)

    # Include amortization entries
    amort = conn.execute(
        "SELECT * FROM advacct_amortization_entry WHERE lease_id = ? ORDER BY period_date",
        (lease_id,)
    ).fetchall()
    data["amortization_entries"] = [row_to_dict(a) for a in amort]

    ok(data)


# ===========================================================================
# 4. list-leases
# ===========================================================================
def list_leases(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "lease_type", None):
        where.append("lease_type = ?")
        params.append(args.lease_type)
    if getattr(args, "lease_status", None):
        where.append("lease_status = ?")
        params.append(args.lease_status)
    if getattr(args, "search", None):
        where.append("(lessee_name LIKE ? OR lessor_name LIKE ? OR asset_description LIKE ?)")
        params.extend([f"%{args.search}%"] * 3)

    where_sql = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM advacct_lease WHERE {where_sql}", params
    ).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM advacct_lease WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ===========================================================================
# 5. classify-lease
# ===========================================================================
def classify_lease(conn, args):
    lease_id = getattr(args, "id", None)
    _validate_lease(conn, lease_id)
    row = conn.execute("SELECT * FROM advacct_lease WHERE id = ?", (lease_id,)).fetchone()
    data = row_to_dict(row)

    # ASC 842 classification criteria (simplified):
    # Finance lease if: term >= 75% of asset life, or PV of payments >= 90% of fair value,
    # or purchase option reasonably certain.
    # For simplicity, we use term_months: >= 36 months => finance, else operating.
    # User can override via --lease-type.

    lease_type = getattr(args, "lease_type", None)
    if not lease_type:
        # Auto-classify based on term
        if data["term_months"] >= 36:
            lease_type = "finance"
        else:
            lease_type = "operating"

    if lease_type not in VALID_LEASE_TYPES:
        err(f"Invalid lease-type: {lease_type}. Must be one of: {', '.join(VALID_LEASE_TYPES)}")

    now = _now_iso()
    conn.execute(
        "UPDATE advacct_lease SET lease_type = ?, updated_at = ? WHERE id = ?",
        (lease_type, now, lease_id)
    )
    audit(conn, SKILL, "classify-lease", "advacct_lease", lease_id,
          new_values={"lease_type": lease_type})
    conn.commit()
    ok({"id": lease_id, "lease_type": lease_type})


# ===========================================================================
# 6. calculate-rou-asset
# ===========================================================================
def calculate_rou_asset(conn, args):
    lease_id = getattr(args, "id", None)
    _validate_lease(conn, lease_id)
    row = conn.execute("SELECT * FROM advacct_lease WHERE id = ?", (lease_id,)).fetchone()
    data = row_to_dict(row)

    monthly_payment = Decimal(data["monthly_payment"])
    discount_rate = Decimal(data["discount_rate"])
    term_months = data["term_months"]

    if term_months <= 0:
        err("term_months must be greater than 0")
    if monthly_payment <= 0:
        err("monthly_payment must be greater than 0")

    # Monthly discount rate
    monthly_rate = discount_rate / Decimal("12")

    # ROU asset = PV of lease payments
    rou_value = _pv_annuity(monthly_payment, monthly_rate, Decimal(str(term_months)))

    now = _now_iso()
    conn.execute(
        "UPDATE advacct_lease SET rou_asset_value = ?, updated_at = ? WHERE id = ?",
        (str(rou_value), now, lease_id)
    )
    audit(conn, SKILL, "calculate-rou-asset", "advacct_lease", lease_id,
          new_values={"rou_asset_value": str(rou_value)})
    conn.commit()
    ok({"id": lease_id, "rou_asset_value": str(rou_value)})


# ===========================================================================
# 7. calculate-lease-liability
# ===========================================================================
def calculate_lease_liability(conn, args):
    lease_id = getattr(args, "id", None)
    _validate_lease(conn, lease_id)
    row = conn.execute("SELECT * FROM advacct_lease WHERE id = ?", (lease_id,)).fetchone()
    data = row_to_dict(row)

    monthly_payment = Decimal(data["monthly_payment"])
    discount_rate = Decimal(data["discount_rate"])
    term_months = data["term_months"]

    if term_months <= 0:
        err("term_months must be greater than 0")
    if monthly_payment <= 0:
        err("monthly_payment must be greater than 0")

    # Monthly discount rate
    monthly_rate = discount_rate / Decimal("12")

    # Lease liability = PV of remaining lease payments (same as ROU at inception)
    liability = _pv_annuity(monthly_payment, monthly_rate, Decimal(str(term_months)))

    now = _now_iso()
    conn.execute(
        "UPDATE advacct_lease SET lease_liability = ?, updated_at = ? WHERE id = ?",
        (str(liability), now, lease_id)
    )
    audit(conn, SKILL, "calculate-lease-liability", "advacct_lease", lease_id,
          new_values={"lease_liability": str(liability)})
    conn.commit()
    ok({"id": lease_id, "lease_liability": str(liability)})


# ===========================================================================
# 8. generate-amortization-schedule
# ===========================================================================
def generate_amortization_schedule(conn, args):
    lease_id = getattr(args, "lease_id", None)
    if not lease_id:
        err("--lease-id is required")
    _validate_lease(conn, lease_id)
    row = conn.execute("SELECT * FROM advacct_lease WHERE id = ?", (lease_id,)).fetchone()
    data = row_to_dict(row)

    monthly_payment = Decimal(data["monthly_payment"])
    discount_rate = Decimal(data["discount_rate"])
    term_months = data["term_months"]
    start_date = data.get("start_date")

    if term_months <= 0:
        err("term_months must be greater than 0")
    if monthly_payment <= 0:
        err("monthly_payment must be greater than 0")
    if not start_date:
        err("Lease must have a start_date to generate amortization schedule")

    monthly_rate = discount_rate / Decimal("12")

    # Calculate initial balance (PV)
    opening = _pv_annuity(monthly_payment, monthly_rate, Decimal(str(term_months)))

    # Delete existing amortization entries
    conn.execute("DELETE FROM advacct_amortization_entry WHERE lease_id = ?", (lease_id,))

    from datetime import date
    start = date.fromisoformat(start_date)
    current_year = start.year
    current_month = start.month

    entries_created = 0
    company_id = data["company_id"]
    now = _now_iso()
    balance = opening

    for i in range(term_months):
        interest = (balance * monthly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        principal = monthly_payment - interest
        closing = balance - principal

        # Last payment: adjust for rounding
        if i == term_months - 1:
            principal = balance
            closing = Decimal("0")
            interest = monthly_payment - principal

        period_date = f"{current_year}-{current_month:02d}-01"

        conn.execute("""
            INSERT INTO advacct_amortization_entry (
                id, lease_id, period_date, opening_balance, payment,
                interest, principal, closing_balance, company_id, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            str(uuid.uuid4()), lease_id, period_date,
            str(balance), str(monthly_payment),
            str(interest), str(principal), str(closing),
            company_id, now,
        ))
        entries_created += 1
        balance = closing

        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    audit(conn, SKILL, "generate-amortization-schedule", "advacct_amortization_entry", lease_id,
          new_values={"entries_created": entries_created, "initial_balance": str(opening)})
    conn.commit()
    ok({
        "lease_id": lease_id, "entries_created": entries_created,
        "initial_balance": str(opening), "monthly_payment": str(monthly_payment),
    })


# ===========================================================================
# 9. record-lease-payment
# ===========================================================================
def record_lease_payment(conn, args):
    lease_id = getattr(args, "lease_id", None)
    if not lease_id:
        err("--lease-id is required")
    _validate_lease(conn, lease_id)

    payment_date = getattr(args, "payment_date", None)
    if not payment_date:
        err("--payment-date is required")

    payment_amount = getattr(args, "payment_amount", None)
    if not payment_amount:
        err("--payment-amount is required")

    row = conn.execute("SELECT * FROM advacct_lease WHERE id = ?", (lease_id,)).fetchone()
    data = row_to_dict(row)
    company_id = data["company_id"]

    # Get current balance from latest amortization entry or lease_liability
    latest_amort = conn.execute(
        "SELECT closing_balance FROM advacct_amortization_entry WHERE lease_id = ? ORDER BY period_date DESC LIMIT 1",
        (lease_id,)
    ).fetchone()

    if latest_amort:
        current_balance = Decimal(latest_amort[0])
    elif data.get("lease_liability"):
        current_balance = Decimal(data["lease_liability"])
    else:
        current_balance = Decimal("0")

    payment_amt = Decimal(payment_amount)
    discount_rate = Decimal(data["discount_rate"])
    monthly_rate = discount_rate / Decimal("12")

    interest = (current_balance * monthly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    principal = payment_amt - interest
    balance_after = current_balance - principal

    payment_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute("""
        INSERT INTO advacct_lease_payment (
            id, lease_id, payment_date, payment_amount, principal, interest,
            balance_after, payment_status, company_id, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        payment_id, lease_id, payment_date, payment_amount,
        str(principal), str(interest), str(balance_after),
        "paid", company_id, now,
    ))
    audit(conn, SKILL, "record-lease-payment", "advacct_lease_payment", payment_id,
          new_values={"lease_id": lease_id, "payment_amount": payment_amount})
    conn.commit()
    ok({
        "id": payment_id, "lease_id": lease_id,
        "payment_amount": payment_amount, "principal": str(principal),
        "interest": str(interest), "balance_after": str(balance_after),
        "payment_status": "paid",
    })


# ===========================================================================
# 10. lease-maturity-report
# ===========================================================================
def lease_maturity_report(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    rows = conn.execute(f"""
        SELECT id, lessee_name, lessor_name, lease_type, start_date, end_date,
               term_months, monthly_payment, rou_asset_value, lease_liability, lease_status
        FROM advacct_lease
        WHERE {where_sql}
        ORDER BY end_date ASC
    """, params).fetchall()

    ok({
        "report": "lease_maturity",
        "rows": [row_to_dict(r) for r in rows],
        "total_leases": len(rows),
    })


# ===========================================================================
# 11. lease-disclosure-report
# ===========================================================================
def lease_disclosure_report(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("l.company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    rows = conn.execute(f"""
        SELECT l.lease_type,
               COUNT(*) as lease_count,
               SUM(CAST(l.monthly_payment AS REAL)) as total_monthly_payments,
               SUM(CAST(COALESCE(l.rou_asset_value, '0') AS REAL)) as total_rou_assets,
               SUM(CAST(COALESCE(l.lease_liability, '0') AS REAL)) as total_lease_liabilities
        FROM advacct_lease l
        WHERE {where_sql}
        GROUP BY l.lease_type
    """, params).fetchall()

    ok({
        "report": "lease_disclosure",
        "rows": [row_to_dict(r) for r in rows],
    })


# ===========================================================================
# 12. lease-summary
# ===========================================================================
def lease_summary(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM advacct_lease WHERE {where_sql}", params
    ).fetchone()[0]

    by_status = conn.execute(f"""
        SELECT lease_status, COUNT(*) as cnt
        FROM advacct_lease WHERE {where_sql} GROUP BY lease_status
    """, params).fetchall()

    by_type = conn.execute(f"""
        SELECT lease_type, COUNT(*) as cnt
        FROM advacct_lease WHERE {where_sql} GROUP BY lease_type
    """, params).fetchall()

    ok({
        "report": "lease_summary",
        "total_leases": total,
        "by_status": {r[0]: r[1] for r in by_status},
        "by_type": {r[0]: r[1] for r in by_type},
    })


# ---------------------------------------------------------------------------
# Action registry
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-lease": add_lease,
    "update-lease": update_lease,
    "get-lease": get_lease,
    "list-leases": list_leases,
    "classify-lease": classify_lease,
    "calculate-rou-asset": calculate_rou_asset,
    "calculate-lease-liability": calculate_lease_liability,
    "generate-amortization-schedule": generate_amortization_schedule,
    "record-lease-payment": record_lease_payment,
    "lease-maturity-report": lease_maturity_report,
    "lease-disclosure-report": lease_disclosure_report,
    "lease-summary": lease_summary,
}
