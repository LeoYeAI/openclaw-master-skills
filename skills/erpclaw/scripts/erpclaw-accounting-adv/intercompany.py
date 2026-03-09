"""ERPClaw Advanced Accounting -- Intercompany Transactions domain module

Actions for intercompany transactions and transfer pricing rules (2 tables, 10 actions).
Imported by db_query.py (unified router).
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.naming import get_next_name, ENTITY_PREFIXES
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit

    ENTITY_PREFIXES.setdefault("ic_transaction", "ICT-")
except ImportError:
    pass

SKILL = "erpclaw-accounting-adv"

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------
VALID_TRANSACTION_TYPES = ("sale", "purchase", "service", "loan", "dividend", "allocation")
VALID_IC_STATUSES = ("draft", "pending_approval", "approved", "posted", "eliminated")
VALID_TP_METHODS = ("cost_plus", "resale_minus", "comparable", "other")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _validate_company(conn, company_id, label="--company-id"):
    if not company_id:
        err(f"{label} is required")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")


# ===========================================================================
# 1. add-ic-transaction
# ===========================================================================
def add_ic_transaction(conn, args):
    from_company_id = getattr(args, "from_company_id", None)
    to_company_id = getattr(args, "to_company_id", None)
    company_id = getattr(args, "company_id", None)

    _validate_company(conn, from_company_id, "--from-company-id")
    _validate_company(conn, to_company_id, "--to-company-id")
    _validate_company(conn, company_id)

    if from_company_id == to_company_id:
        err("from-company-id and to-company-id must be different")

    transaction_type = getattr(args, "transaction_type", None)
    if not transaction_type:
        err("--transaction-type is required")
    if transaction_type not in VALID_TRANSACTION_TYPES:
        err(f"Invalid transaction-type: {transaction_type}. Must be one of: {', '.join(VALID_TRANSACTION_TYPES)}")

    amount = getattr(args, "amount", None) or "0"
    try:
        if Decimal(amount) <= 0:
            err("Amount must be greater than zero")
    except Exception:
        err(f"Invalid amount: {amount}")

    ic_id = str(uuid.uuid4())
    conn.company_id = company_id
    naming = get_next_name(conn, "ic_transaction", company_id=company_id)
    now = _now_iso()

    transfer_price_method = getattr(args, "transfer_price_method", None)
    if transfer_price_method and transfer_price_method not in VALID_TP_METHODS:
        err(f"Invalid transfer-price-method: {transfer_price_method}. Must be one of: {', '.join(VALID_TP_METHODS)}")

    conn.execute("""
        INSERT INTO advacct_ic_transaction (
            id, naming_series, from_company_id, to_company_id, transaction_type,
            description, amount, currency, transfer_price_method, ic_status,
            posted_date, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        ic_id, naming, from_company_id, to_company_id, transaction_type,
        getattr(args, "description", None),
        amount,
        getattr(args, "currency", None) or "USD",
        transfer_price_method,
        "draft", None, company_id, now, now,
    ))
    audit(conn, SKILL, "add-ic-transaction", "advacct_ic_transaction", ic_id,
          new_values={"from": from_company_id, "to": to_company_id, "amount": amount})
    conn.commit()
    ok({
        "id": ic_id, "naming_series": naming,
        "from_company_id": from_company_id, "to_company_id": to_company_id,
        "transaction_type": transaction_type, "amount": amount, "ic_status": "draft",
    })


# ===========================================================================
# 2. update-ic-transaction
# ===========================================================================
def update_ic_transaction(conn, args):
    ic_id = getattr(args, "id", None)
    if not ic_id:
        err("--id is required")
    row = conn.execute("SELECT * FROM advacct_ic_transaction WHERE id = ?", (ic_id,)).fetchone()
    if not row:
        err(f"IC transaction {ic_id} not found")

    data = row_to_dict(row)
    if data["ic_status"] not in ("draft", "pending_approval"):
        err(f"Cannot update IC transaction in status '{data['ic_status']}'. Must be draft or pending_approval.")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "description": "description",
        "amount": "amount",
        "currency": "currency",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?")
            params.append(val)
            changed.append(col_name)

    transaction_type = getattr(args, "transaction_type", None)
    if transaction_type:
        if transaction_type not in VALID_TRANSACTION_TYPES:
            err(f"Invalid transaction-type: {transaction_type}")
        updates.append("transaction_type = ?")
        params.append(transaction_type)
        changed.append("transaction_type")

    transfer_price_method = getattr(args, "transfer_price_method", None)
    if transfer_price_method:
        if transfer_price_method not in VALID_TP_METHODS:
            err(f"Invalid transfer-price-method: {transfer_price_method}")
        updates.append("transfer_price_method = ?")
        params.append(transfer_price_method)
        changed.append("transfer_price_method")

    if not updates:
        err("No fields to update")

    updates.append("updated_at = ?")
    params.append(_now_iso())
    params.append(ic_id)
    conn.execute(f"UPDATE advacct_ic_transaction SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-ic-transaction", "advacct_ic_transaction", ic_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": ic_id, "updated_fields": changed})


# ===========================================================================
# 3. get-ic-transaction
# ===========================================================================
def get_ic_transaction(conn, args):
    ic_id = getattr(args, "id", None)
    if not ic_id:
        err("--id is required")
    row = conn.execute("SELECT * FROM advacct_ic_transaction WHERE id = ?", (ic_id,)).fetchone()
    if not row:
        err(f"IC transaction {ic_id} not found")
    ok(row_to_dict(row))


# ===========================================================================
# 4. list-ic-transactions
# ===========================================================================
def list_ic_transactions(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "from_company_id", None):
        where.append("from_company_id = ?")
        params.append(args.from_company_id)
    if getattr(args, "to_company_id", None):
        where.append("to_company_id = ?")
        params.append(args.to_company_id)
    if getattr(args, "transaction_type", None):
        where.append("transaction_type = ?")
        params.append(args.transaction_type)
    if getattr(args, "ic_status", None):
        where.append("ic_status = ?")
        params.append(args.ic_status)
    if getattr(args, "search", None):
        where.append("(description LIKE ?)")
        params.append(f"%{args.search}%")

    where_sql = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM advacct_ic_transaction WHERE {where_sql}", params
    ).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM advacct_ic_transaction WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ===========================================================================
# 5. approve-ic-transaction
# ===========================================================================
def approve_ic_transaction(conn, args):
    ic_id = getattr(args, "id", None)
    if not ic_id:
        err("--id is required")
    row = conn.execute("SELECT * FROM advacct_ic_transaction WHERE id = ?", (ic_id,)).fetchone()
    if not row:
        err(f"IC transaction {ic_id} not found")

    data = row_to_dict(row)
    if data["ic_status"] not in ("draft", "pending_approval"):
        err(f"Cannot approve IC transaction in status '{data['ic_status']}'. Must be draft or pending_approval.")

    now = _now_iso()
    conn.execute(
        "UPDATE advacct_ic_transaction SET ic_status = 'approved', updated_at = ? WHERE id = ?",
        (now, ic_id)
    )
    audit(conn, SKILL, "approve-ic-transaction", "advacct_ic_transaction", ic_id,
          new_values={"ic_status": "approved"})
    conn.commit()
    ok({"id": ic_id, "ic_status": "approved"})


# ===========================================================================
# 6. post-ic-transaction
# ===========================================================================
def post_ic_transaction(conn, args):
    ic_id = getattr(args, "id", None)
    if not ic_id:
        err("--id is required")
    row = conn.execute("SELECT * FROM advacct_ic_transaction WHERE id = ?", (ic_id,)).fetchone()
    if not row:
        err(f"IC transaction {ic_id} not found")

    data = row_to_dict(row)
    if data["ic_status"] != "approved":
        err(f"Cannot post IC transaction in status '{data['ic_status']}'. Must be approved.")

    now = _now_iso()
    conn.execute(
        "UPDATE advacct_ic_transaction SET ic_status = 'posted', posted_date = ?, updated_at = ? WHERE id = ?",
        (now, now, ic_id)
    )
    audit(conn, SKILL, "post-ic-transaction", "advacct_ic_transaction", ic_id,
          new_values={"ic_status": "posted", "posted_date": now})
    conn.commit()
    ok({"id": ic_id, "ic_status": "posted", "posted_date": now})


# ===========================================================================
# 7. add-transfer-price-rule
# ===========================================================================
def add_transfer_price_rule(conn, args):
    _validate_company(conn, args.company_id)

    method = getattr(args, "method", None) or "cost_plus"
    if method not in VALID_TP_METHODS:
        err(f"Invalid method: {method}. Must be one of: {', '.join(VALID_TP_METHODS)}")

    transaction_type = getattr(args, "transaction_type", None)
    if transaction_type and transaction_type not in VALID_TRANSACTION_TYPES:
        err(f"Invalid transaction-type: {transaction_type}")

    markup_pct = getattr(args, "markup_pct", None) or "0"

    rule_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute("""
        INSERT INTO advacct_transfer_price_rule (
            id, from_company_id, to_company_id, transaction_type,
            method, markup_pct, effective_date, expiry_date,
            company_id, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        rule_id,
        getattr(args, "from_company_id", None),
        getattr(args, "to_company_id", None),
        transaction_type,
        method, markup_pct,
        getattr(args, "effective_date", None),
        getattr(args, "expiry_date", None),
        args.company_id, now,
    ))
    audit(conn, SKILL, "add-transfer-price-rule", "advacct_transfer_price_rule", rule_id,
          new_values={"method": method, "markup_pct": markup_pct})
    conn.commit()
    ok({
        "id": rule_id, "method": method, "markup_pct": markup_pct,
        "transaction_type": transaction_type,
    })


# ===========================================================================
# 8. list-transfer-price-rules
# ===========================================================================
def list_transfer_price_rules(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "from_company_id", None):
        where.append("from_company_id = ?")
        params.append(args.from_company_id)
    if getattr(args, "to_company_id", None):
        where.append("to_company_id = ?")
        params.append(args.to_company_id)
    if getattr(args, "transaction_type", None):
        where.append("transaction_type = ?")
        params.append(args.transaction_type)

    where_sql = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM advacct_transfer_price_rule WHERE {where_sql}", params
    ).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM advacct_transfer_price_rule WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ===========================================================================
# 9. ic-reconciliation-report
# ===========================================================================
def ic_reconciliation_report(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    rows = conn.execute(f"""
        SELECT from_company_id, to_company_id, transaction_type,
               COUNT(*) as transaction_count,
               SUM(CAST(amount AS REAL)) as total_amount,
               ic_status
        FROM advacct_ic_transaction
        WHERE {where_sql}
        GROUP BY from_company_id, to_company_id, transaction_type, ic_status
        ORDER BY from_company_id, to_company_id
    """, params).fetchall()

    ok({
        "report": "ic_reconciliation",
        "rows": [row_to_dict(r) for r in rows],
    })


# ===========================================================================
# 10. ic-elimination-report
# ===========================================================================
def ic_elimination_report(conn, args):
    where, params = ["ic_status = 'posted'"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)

    where_sql = " AND ".join(where)
    rows = conn.execute(f"""
        SELECT id, from_company_id, to_company_id, transaction_type,
               amount, currency, posted_date
        FROM advacct_ic_transaction
        WHERE {where_sql}
        ORDER BY posted_date DESC
    """, params).fetchall()

    total_to_eliminate = sum(Decimal(row_to_dict(r)["amount"]) for r in rows)

    ok({
        "report": "ic_elimination",
        "rows": [row_to_dict(r) for r in rows],
        "total_to_eliminate": str(total_to_eliminate),
        "transaction_count": len(rows),
    })


# ---------------------------------------------------------------------------
# Action registry
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-ic-transaction": add_ic_transaction,
    "update-ic-transaction": update_ic_transaction,
    "get-ic-transaction": get_ic_transaction,
    "list-ic-transactions": list_ic_transactions,
    "approve-ic-transaction": approve_ic_transaction,
    "post-ic-transaction": post_ic_transaction,
    "add-transfer-price-rule": add_transfer_price_rule,
    "list-transfer-price-rules": list_transfer_price_rules,
    "ic-reconciliation-report": ic_reconciliation_report,
    "ic-elimination-report": ic_elimination_report,
}
