#!/usr/bin/env python3
"""ERPClaw Payments Skill — db_query.py

Payment entries, allocations, payment ledger, and reconciliation.
Draft→Submit→Cancel lifecycle. Submit posts GL entries via shared lib.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.gl_posting import (
        validate_gl_entries,
        insert_gl_entries,
        reverse_gl_entries,
        prepare_multicurrency_entries,
    )
    from erpclaw_lib.fx_posting import (
        calculate_exchange_gain_loss,
        post_exchange_gain_loss,
    )
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query_helpers import resolve_company_id
    from erpclaw_lib.query import (
        Q, P, Table, Field, fn, Order, DecimalSum, insert_row, update_row,
    )
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company", "account"]

VALID_PAYMENT_TYPES = ("receive", "pay", "internal_transfer")
VALID_PARTY_TYPES = ("customer", "supplier", "employee")

# ── PyPika table aliases ──
PE = Table("payment_entry")
PA = Table("payment_allocation")
PLE = Table("payment_ledger_entry")
COMPANY = Table("company")
ACCOUNT = Table("account")
GL = Table("gl_entry")
CC = Table("cost_center")
PT = Table("payment_terms")
SI = Table("sales_invoice")
PI = Table("purchase_invoice")
PD = Table("payment_deduction")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_pe_or_err(conn, payment_entry_id: str) -> dict:
    """Fetch a payment entry by ID. Calls err() if not found."""
    q = Q.from_(PE).select(PE.star).where(PE.id == P())
    row = conn.execute(q.get_sql(), (payment_entry_id,)).fetchone()
    if not row:
        err(f"Payment entry {payment_entry_id} not found",
             suggestion="Use 'list payments' to see available payment entries.")
    return row_to_dict(row)


def _get_allocations(conn, payment_entry_id: str) -> list[dict]:
    """Fetch allocations for a payment entry."""
    q = (Q.from_(PA).select(PA.star)
         .where(PA.payment_entry_id == P())
         .orderby(LiteralValue("rowid")))
    rows = conn.execute(q.get_sql(), (payment_entry_id,)).fetchall()
    return [row_to_dict(r) for r in rows]


def _insert_allocations(conn, payment_entry_id: str, allocations: list[dict]):
    """Insert payment allocation rows and return total allocated."""
    sql, _ = insert_row("payment_allocation", {
        "id": P(), "payment_entry_id": P(), "voucher_type": P(),
        "voucher_id": P(), "allocated_amount": P(),
    })
    total_allocated = Decimal("0")
    for alloc in allocations:
        alloc_id = str(uuid.uuid4())
        amount = round_currency(to_decimal(alloc.get("allocated_amount", "0")))
        total_allocated += amount
        conn.execute(sql, (alloc_id, payment_entry_id,
                           alloc["voucher_type"], alloc["voucher_id"], str(amount)))
    return total_allocated


def _recalc_unallocated(conn, payment_entry_id: str):
    """Recalculate and update unallocated_amount on a payment entry."""
    q = Q.from_(PE).select(PE.paid_amount).where(PE.id == P())
    pe = conn.execute(q.get_sql(), (payment_entry_id,)).fetchone()
    if not pe:
        return
    paid = to_decimal(pe["paid_amount"])
    q2 = (Q.from_(PA)
          .select(fn.Coalesce(DecimalSum(PA.allocated_amount), ValueWrapper("0")).as_("total"))
          .where(PA.payment_entry_id == P()))
    row = conn.execute(q2.get_sql(), (payment_entry_id,)).fetchone()
    allocated = to_decimal(str(row["total"]))
    unallocated = round_currency(paid - allocated)
    sql = update_row("payment_entry",
                     data={"unallocated_amount": P(), "updated_at": LiteralValue("datetime('now')")},
                     where={"id": P()})
    conn.execute(sql, (str(unallocated), payment_entry_id))


def _validate_not_group_account(conn, account_id: str, label: str) -> str:
    """Validate that an account is not a group account.

    If the account is a group (is_group = 1), attempt to find the first
    leaf child account under it.  If a single leaf child exists, return
    its ID (auto-resolve).  Otherwise, return an error listing available
    leaf children so the user can pick one.

    Returns the validated (possibly resolved) account ID.
    """
    q = (Q.from_(ACCOUNT)
         .select(ACCOUNT.id, ACCOUNT.name, ACCOUNT.account_number, ACCOUNT.is_group)
         .where(ACCOUNT.id == P()))
    row = conn.execute(q.get_sql(), (account_id,)).fetchone()
    if not row:
        return account_id  # Account existence is checked elsewhere

    if not row["is_group"]:
        return account_id  # Leaf account — OK

    # Group account — try to find leaf children
    q_children = (Q.from_(ACCOUNT)
                  .select(ACCOUNT.id, ACCOUNT.name, ACCOUNT.account_number)
                  .where(ACCOUNT.parent_id == P())
                  .where(ACCOUNT.is_group == 0)
                  .where(ACCOUNT.disabled == 0))
    children = conn.execute(q_children.get_sql(), (account_id,)).fetchall()

    if len(children) == 1:
        # Single leaf child — auto-resolve
        child = row_to_dict(children[0])
        return child["id"]

    if len(children) == 0:
        err(f"Account '{row['name']}' ({label}) is a group account with no "
            f"leaf children. Please create a child account under it first.")
    else:
        child_list = ", ".join(
            f"'{row_to_dict(c)['name']}' ({row_to_dict(c)['account_number'] or row_to_dict(c)['id']})"
            for c in children
        )
        err(f"Account '{row['name']}' ({label}) is a group account. "
            f"Cannot post to group accounts. "
            f"Please specify one of its leaf children: {child_list}")


# ---------------------------------------------------------------------------
# 1. add-payment
# ---------------------------------------------------------------------------

def add_payment(conn, args):
    """Create a new draft payment entry."""
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")
    payment_type = args.payment_type
    if not payment_type or payment_type not in VALID_PAYMENT_TYPES:
        err(f"--payment-type is required. Valid: {VALID_PAYMENT_TYPES}")
    posting_date = args.posting_date
    if not posting_date:
        err("--posting-date is required")
    party_type = args.party_type
    if payment_type != "internal_transfer":
        if not party_type or party_type not in VALID_PARTY_TYPES:
            err(f"--party-type is required. Valid: {VALID_PARTY_TYPES}")
    party_id = args.party_id
    if payment_type != "internal_transfer" and not party_id:
        err("--party-id is required")
    paid_from = args.paid_from_account
    if not paid_from:
        err("--paid-from-account is required")
    paid_to = args.paid_to_account
    if not paid_to:
        err("--paid-to-account is required")
    paid_amount = args.paid_amount
    if not paid_amount:
        err("--paid-amount is required")

    # Validate company
    q = Q.from_(COMPANY).select(COMPANY.id).where(COMPANY.id == P())
    if not conn.execute(q.get_sql(), (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Validate accounts exist and are not group accounts
    qa = Q.from_(ACCOUNT).select(ACCOUNT.id).where(ACCOUNT.id == P())
    for acct_id, label in [(paid_from, "paid-from-account"), (paid_to, "paid-to-account")]:
        if not conn.execute(qa.get_sql(), (acct_id,)).fetchone():
            err(f"Account {acct_id} ({label}) not found")

    # Resolve group accounts to leaf children (or error)
    paid_from = _validate_not_group_account(conn, paid_from, "paid-from-account")
    paid_to = _validate_not_group_account(conn, paid_to, "paid-to-account")

    amount = round_currency(to_decimal(paid_amount))
    if amount <= 0:
        err("--paid-amount must be > 0")

    exchange_rate = to_decimal(args.exchange_rate or "1")
    received_amount = round_currency(amount * exchange_rate)
    payment_currency = args.payment_currency or "USD"

    pe_id = str(uuid.uuid4())
    naming = get_next_name(conn, "payment_entry", company_id=company_id)

    sql, _ = insert_row("payment_entry", {
        "id": P(), "naming_series": P(), "payment_type": P(),
        "posting_date": P(), "party_type": P(), "party_id": P(),
        "paid_from_account": P(), "paid_to_account": P(),
        "paid_amount": P(), "received_amount": P(),
        "payment_currency": P(), "exchange_rate": P(),
        "reference_number": P(), "reference_date": P(),
        "status": P(), "unallocated_amount": P(), "company_id": P(),
    })
    conn.execute(sql,
        (pe_id, naming, payment_type, posting_date,
         party_type, party_id, paid_from, paid_to,
         str(amount), str(received_amount),
         payment_currency, str(exchange_rate),
         args.reference_number, args.reference_date,
         "draft", str(amount),  # unallocated = full amount initially
         company_id))

    # Insert allocations if provided
    if args.allocations:
        try:
            allocs = json.loads(args.allocations) if isinstance(args.allocations, str) else args.allocations
        except json.JSONDecodeError as e:
            err("Invalid JSON format in --allocations")
        _insert_allocations(conn, pe_id, allocs)
        _recalc_unallocated(conn, pe_id)

    audit(conn, "erpclaw-payments", "add-payment", "payment_entry", pe_id,
           new_values={"naming_series": naming, "payment_type": payment_type,
                       "paid_amount": str(amount)})
    conn.commit()

    ok({"status": "created", "payment_entry_id": pe_id,
         "naming_series": naming})


# ---------------------------------------------------------------------------
# 2. update-payment
# ---------------------------------------------------------------------------

def update_payment(conn, args):
    """Update a draft payment entry."""
    pe_id = args.payment_entry_id
    if not pe_id:
        err("--payment-entry-id is required")

    pe = _get_pe_or_err(conn, pe_id)
    if pe["status"] != "draft":
        err(f"Cannot update: payment is '{pe['status']}' (must be 'draft')",
             suggestion="Cancel the document first, then make changes.")

    updated_fields = []
    old_values = {}

    if args.paid_amount:
        amount = round_currency(to_decimal(args.paid_amount))
        if amount <= 0:
            err("--paid-amount must be > 0")
        old_values["paid_amount"] = pe["paid_amount"]
        exchange_rate = to_decimal(pe["exchange_rate"])
        received = round_currency(amount * exchange_rate)
        sql = update_row("payment_entry",
                         data={"paid_amount": P(), "received_amount": P(),
                               "updated_at": LiteralValue("datetime('now')")},
                         where={"id": P()})
        conn.execute(sql, (str(amount), str(received), pe_id))
        updated_fields.append("paid_amount")

    if args.reference_number is not None:
        old_values["reference_number"] = pe["reference_number"]
        sql = update_row("payment_entry",
                         data={"reference_number": P(),
                               "updated_at": LiteralValue("datetime('now')")},
                         where={"id": P()})
        conn.execute(sql, (args.reference_number, pe_id))
        updated_fields.append("reference_number")

    if args.allocations:
        try:
            allocs = json.loads(args.allocations) if isinstance(args.allocations, str) else args.allocations
        except json.JSONDecodeError as e:
            err("Invalid JSON format in --allocations")
        dq = Q.from_(PA).delete().where(PA.payment_entry_id == P())
        conn.execute(dq.get_sql(), (pe_id,))
        _insert_allocations(conn, pe_id, allocs)
        _recalc_unallocated(conn, pe_id)
        updated_fields.append("allocations")

    if not updated_fields:
        err("No fields to update")

    audit(conn, "erpclaw-payments", "update-payment", "payment_entry", pe_id,
           old_values=old_values, new_values={"updated_fields": updated_fields})
    conn.commit()

    ok({"status": "updated", "payment_entry_id": pe_id,
         "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 3. get-payment
# ---------------------------------------------------------------------------

def get_payment(conn, args):
    """Get a payment entry with allocations."""
    pe_id = args.payment_entry_id
    if not pe_id:
        err("--payment-entry-id is required")

    pe = _get_pe_or_err(conn, pe_id)
    allocs = _get_allocations(conn, pe_id)

    formatted_allocs = [{
        "id": a["id"],
        "voucher_type": a["voucher_type"],
        "voucher_id": a["voucher_id"],
        "allocated_amount": a["allocated_amount"],
        "exchange_gain_loss": a.get("exchange_gain_loss", "0"),
    } for a in allocs]

    ok({
        "id": pe["id"],
        "naming_series": pe["naming_series"],
        "payment_type": pe["payment_type"],
        "posting_date": pe["posting_date"],
        "party_type": pe["party_type"],
        "party_id": pe["party_id"],
        "paid_from_account": pe["paid_from_account"],
        "paid_to_account": pe["paid_to_account"],
        "paid_amount": pe["paid_amount"],
        "received_amount": pe["received_amount"],
        "payment_currency": pe["payment_currency"],
        "exchange_rate": pe["exchange_rate"],
        "reference_number": pe.get("reference_number"),
        "reference_date": pe.get("reference_date"),
        "status": pe["status"],
        "unallocated_amount": pe["unallocated_amount"],
        "company_id": pe["company_id"],
        "allocations": formatted_allocs,
    })


# ---------------------------------------------------------------------------
# 4. list-payments
# ---------------------------------------------------------------------------

def list_payments(conn, args):
    """List payment entries with filtering."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    pe = Table("payment_entry")
    base = Q.from_(pe).where(pe.company_id == P())
    params = [company_id]

    if args.payment_type:
        base = base.where(pe.payment_type == P())
        params.append(args.payment_type)
    if args.party_type:
        base = base.where(pe.party_type == P())
        params.append(args.party_type)
    if args.party_id:
        base = base.where(pe.party_id == P())
        params.append(args.party_id)
    if args.pe_status:
        base = base.where(pe.status == P())
        params.append(args.pe_status)
    if args.from_date:
        base = base.where(pe.posting_date >= P())
        params.append(args.from_date)
    if args.to_date:
        base = base.where(pe.posting_date <= P())
        params.append(args.to_date)

    count_q = base.select(fn.Count("*"))
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    list_params = params + [limit, offset]

    data_q = (base.select(
                  pe.id, pe.naming_series, pe.payment_type, pe.posting_date,
                  pe.party_type, pe.party_id, pe.paid_amount, pe.status,
                  pe.unallocated_amount)
              .orderby(pe.posting_date, order=Order.desc)
              .orderby(pe.created_at, order=Order.desc))
    # Add party_name resolution via CASE subquery
    sql = data_q.get_sql()
    # Insert party_name subquery after SELECT columns
    party_name_sql = (
        ",(CASE \"payment_entry\".\"party_type\" "
        "WHEN 'customer' THEN (SELECT \"name\" FROM \"customer\" WHERE \"id\"=\"payment_entry\".\"party_id\") "
        "WHEN 'supplier' THEN (SELECT \"name\" FROM \"supplier\" WHERE \"id\"=\"payment_entry\".\"party_id\") "
        "WHEN 'employee' THEN (SELECT \"full_name\" FROM \"employee\" WHERE \"id\"=\"payment_entry\".\"party_id\") "
        "ELSE \"payment_entry\".\"party_id\" END) AS \"party_name\""
    )
    # Insert before FROM clause
    sql = sql.replace(" FROM ", party_name_sql + " FROM ", 1)
    rows = conn.execute(
        sql + " LIMIT ? OFFSET ?", list_params
    ).fetchall()

    ok({"payments": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 5. submit-payment
# ---------------------------------------------------------------------------

def _calc_early_payment_discount(conn, pe, allocations):
    """Check allocations for invoices eligible for early payment discount.

    Returns (total_discount, discount_account_id, discount_details).
    If no discount applies, returns (Decimal("0"), None, []).
    """
    from datetime import date as dt_date
    total_discount = Decimal("0")
    details = []
    discount_account_id = None

    payment_date = pe["posting_date"]
    try:
        pay_dt = dt_date.fromisoformat(payment_date)
    except (ValueError, TypeError):
        return Decimal("0"), None, []

    for alloc in allocations:
        vtype = alloc.get("voucher_type", "")
        vid = alloc.get("voucher_id", "")
        if vtype not in ("sales_invoice", "purchase_invoice"):
            continue

        if vtype == "sales_invoice":
            qi = Q.from_(SI).select(SI.posting_date, SI.payment_terms_id).where(SI.id == P())
            inv = conn.execute(qi.get_sql(), (vid,)).fetchone()
        else:
            qi = Q.from_(PI).select(PI.posting_date, PI.payment_terms_id).where(PI.id == P())
            inv = conn.execute(qi.get_sql(), (vid,)).fetchone()
        if not inv or not inv["payment_terms_id"]:
            continue

        qt = Q.from_(PT).select(PT.discount_percentage, PT.discount_days).where(PT.id == P())
        pt = conn.execute(qt.get_sql(), (inv["payment_terms_id"],)).fetchone()
        if not pt or not pt["discount_percentage"] or not pt["discount_days"]:
            continue

        disc_pct = to_decimal(pt["discount_percentage"])
        disc_days = int(pt["discount_days"])
        if disc_pct <= 0 or disc_days <= 0:
            continue

        try:
            inv_dt = dt_date.fromisoformat(inv["posting_date"])
        except (ValueError, TypeError):
            continue

        if (pay_dt - inv_dt).days <= disc_days:
            alloc_amt = to_decimal(alloc.get("allocated_amount", "0"))
            disc_amt = round_currency(alloc_amt * disc_pct / Decimal("100"))
            if disc_amt > 0:
                total_discount += disc_amt
                details.append({
                    "voucher_type": vtype, "voucher_id": vid,
                    "discount_percentage": str(disc_pct),
                    "discount_amount": str(disc_amt),
                })

    # Find discount account and default cost center
    cost_center_id = None
    if total_discount > 0:
        disc_name = "Sales Discounts" if pe["payment_type"] == "receive" else "Purchase Discounts"
        qa = (Q.from_(ACCOUNT).select(ACCOUNT.id)
              .where(ACCOUNT.name == P()).where(ACCOUNT.company_id == P()))
        acct = conn.execute(qa.get_sql(), (disc_name, pe["company_id"])).fetchone()
        if acct:
            discount_account_id = acct["id"]
        # Get default cost center for P&L tracking
        qc = (Q.from_(CC).select(CC.id)
              .where(CC.company_id == P()).where(CC.is_group == P()))
        cc = conn.execute(qc.get_sql() + " LIMIT 1", (pe["company_id"], 0)).fetchone()
        if cc:
            cost_center_id = cc["id"]

    return total_discount, discount_account_id, details, cost_center_id


def submit_payment(conn, args):
    """Submit a draft payment: post GL entries, create PLE, update status.

    Automatically detects and applies early payment discounts when
    allocations reference invoices with payment terms that include
    discount_percentage and discount_days, and the payment is made
    within the discount window.
    """
    pe_id = args.payment_entry_id
    if not pe_id:
        err("--payment-entry-id is required")

    pe = _get_pe_or_err(conn, pe_id)
    if pe["status"] != "draft":
        err(f"Cannot submit: payment is '{pe['status']}' (must be 'draft')")

    # Pre-GL validation: ensure accounts are not group accounts
    # (catches cases where draft was created before this check existed)
    for acct_key, label in [("paid_from_account", "paid-from-account"),
                            ("paid_to_account", "paid-to-account")]:
        resolved = _validate_not_group_account(conn, pe[acct_key], label)
        if resolved != pe[acct_key]:
            # Auto-resolved to leaf child — update the payment entry
            sql = update_row("payment_entry",
                             data={acct_key: P(), "updated_at": LiteralValue("datetime('now')")},
                             where={"id": P()})
            conn.execute(sql, (resolved, pe_id))
            pe[acct_key] = resolved

    paid_amount = to_decimal(pe["paid_amount"])
    allocations = _get_allocations(conn, pe_id)

    # Check for early payment discount
    discount_amount, discount_account_id, discount_details, disc_cost_center = \
        _calc_early_payment_discount(conn, pe, allocations)

    # Effective amount hitting the bank is reduced by discount
    bank_amount = paid_amount - discount_amount
    receivable_amount = paid_amount  # Full amount clears the receivable

    # Build GL entries based on payment type
    # receive: DR paid_to (bank), CR paid_from (receivable)
    # pay: DR paid_to (payable), CR paid_from (bank)
    # internal_transfer: DR paid_to (bank), CR paid_from (bank)
    if discount_amount > 0 and discount_account_id:
        # With discount: bank gets less, discount account absorbs the rest
        disc_entry = {"account_id": discount_account_id,
                      "debit": str(discount_amount), "credit": "0",
                      "party_type": None, "party_id": None}
        if disc_cost_center:
            disc_entry["cost_center_id"] = disc_cost_center
        gl_entries = [
            {"account_id": pe["paid_to_account"], "debit": str(bank_amount), "credit": "0",
             "party_type": pe["party_type"], "party_id": pe["party_id"]},
            disc_entry,
            {"account_id": pe["paid_from_account"], "debit": "0", "credit": str(receivable_amount),
             "party_type": pe["party_type"], "party_id": pe["party_id"]},
        ]
    else:
        gl_entries = [
            {"account_id": pe["paid_to_account"], "debit": str(paid_amount), "credit": "0",
             "party_type": pe["party_type"], "party_id": pe["party_id"]},
            {"account_id": pe["paid_from_account"], "debit": "0", "credit": str(paid_amount),
             "party_type": pe["party_type"], "party_id": pe["party_id"]},
        ]

    # Apply multi-currency: set currency/exchange_rate on GL entries
    payment_currency = pe["payment_currency"] or "USD"
    payment_rate = to_decimal(pe["exchange_rate"] or "1")
    if payment_currency != "USD" or payment_rate != Decimal("1"):
        prepare_multicurrency_entries(gl_entries, payment_currency, payment_rate)

    # Compute FX gain/loss on allocated invoices
    fx_gain_loss_total = Decimal("0")
    if allocations and payment_rate != Decimal("1"):
        qc = Q.from_(COMPANY).select(COMPANY.exchange_gain_loss_account_id).where(COMPANY.id == P())
        company = conn.execute(qc.get_sql(), (pe["company_id"],)).fetchone()
        fx_account_id = company["exchange_gain_loss_account_id"] if company else None

        for alloc in allocations:
            inv_rate = Decimal("1")
            # Try to get original invoice exchange rate
            if alloc.get("reference_type") == "sales_invoice":
                qi = Q.from_(SI).select(SI.exchange_rate).where(SI.id == P())
                inv_row = conn.execute(qi.get_sql(), (alloc["reference_id"],)).fetchone()
                if inv_row and inv_row["exchange_rate"]:
                    inv_rate = to_decimal(inv_row["exchange_rate"])
            elif alloc.get("reference_type") == "purchase_invoice":
                qi = Q.from_(PI).select(PI.exchange_rate).where(PI.id == P())
                inv_row = conn.execute(qi.get_sql(), (alloc["reference_id"],)).fetchone()
                if inv_row and inv_row["exchange_rate"]:
                    inv_rate = to_decimal(inv_row["exchange_rate"])

            if inv_rate != payment_rate:
                alloc_amount = to_decimal(alloc["allocated_amount"])
                gl = calculate_exchange_gain_loss(
                    alloc_amount, payment_rate, inv_rate
                )
                fx_gain_loss_total += gl
                # Update allocation record
                sql = update_row("payment_allocation",
                                 data={"exchange_gain_loss": P()},
                                 where={"id": P()})
                conn.execute(sql, (str(gl), alloc["id"]))

        # Post FX gain/loss GL entries if there's a net amount
        if fx_gain_loss_total != 0 and fx_account_id:
            post_exchange_gain_loss(
                gl_entries, fx_gain_loss_total, fx_account_id
            )
            # FX entry needs a cost center for P&L tracking
            if gl_entries[-1].get("account_id") == fx_account_id:
                # Use the first cost center found, or look up default
                qcc = Q.from_(COMPANY).select(COMPANY.default_cost_center_id).where(COMPANY.id == P())
                default_cc = conn.execute(qcc.get_sql(), (pe["company_id"],)).fetchone()
                if default_cc and default_cc["default_cost_center_id"]:
                    gl_entries[-1]["cost_center_id"] = default_cc["default_cost_center_id"]
                # Also need to add offsetting base amount difference to AR/AP entry
                # The prepare_multicurrency_entries already handled base amounts

    try:
        validate_gl_entries(
            conn, gl_entries, pe["company_id"],
            pe["posting_date"], voucher_type="payment_entry",
        )
        gl_ids = insert_gl_entries(
            conn, gl_entries,
            voucher_type="payment_entry",
            voucher_id=pe_id,
            posting_date=pe["posting_date"],
            company_id=pe["company_id"],
            remarks=f"Payment {pe['naming_series']}",
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-payments] {e}\n")
        err(f"GL posting failed: {e}")

    # Create payment ledger entry (tracks outstanding)
    ple_id = str(uuid.uuid4())
    # For receive: negative PLE (reduces receivable outstanding)
    # For pay: negative PLE (reduces payable outstanding)
    ple_amount = str(round_currency(-paid_amount))
    if pe["party_type"] and pe["party_id"]:
        # Determine the account for PLE (receivable for receive, payable for pay)
        ple_account = pe["paid_from_account"] if pe["payment_type"] == "receive" else pe["paid_to_account"]
        ple_sql, _ = insert_row("payment_ledger_entry", {
            "id": P(), "posting_date": P(), "account_id": P(),
            "party_type": P(), "party_id": P(),
            "voucher_type": P(), "voucher_id": P(),
            "amount": P(), "amount_in_account_currency": P(),
            "currency": P(), "remarks": P(),
        })
        conn.execute(ple_sql,
            (ple_id, pe["posting_date"], ple_account,
             pe["party_type"], pe["party_id"],
             "payment_entry", pe_id, ple_amount, ple_amount,
             pe["payment_currency"],
             f"Payment {pe['naming_series']}"))

    sql = update_row("payment_entry",
                     data={"status": P(), "updated_at": LiteralValue("datetime('now')")},
                     where={"id": P()})
    conn.execute(sql, ("submitted", pe_id))

    result = {"status": "submitted", "payment_entry_id": pe_id,
              "gl_entries_created": len(gl_ids), "outstanding_updated": True}
    if discount_amount > 0:
        result["early_payment_discount"] = {
            "discount_amount": str(discount_amount),
            "bank_amount": str(bank_amount),
            "details": discount_details,
        }
    if fx_gain_loss_total != 0:
        result["exchange_gain_loss"] = str(round_currency(fx_gain_loss_total))

    audit(conn, "erpclaw-payments", "submit-payment", "payment_entry", pe_id,
           new_values={"gl_entries_created": len(gl_ids),
                       "discount_amount": str(discount_amount)})
    conn.commit()

    ok(result)


# ---------------------------------------------------------------------------
# 6. cancel-payment
# ---------------------------------------------------------------------------

def cancel_payment(conn, args):
    """Cancel a submitted payment: reverse GL entries, reverse PLE."""
    pe_id = args.payment_entry_id
    if not pe_id:
        err("--payment-entry-id is required")

    pe = _get_pe_or_err(conn, pe_id)
    if pe["status"] != "submitted":
        err(f"Cannot cancel: payment is '{pe['status']}' (must be 'submitted')")

    # Reverse GL entries
    try:
        reverse_gl_entries(
            conn,
            voucher_type="payment_entry",
            voucher_id=pe_id,
            posting_date=pe["posting_date"],
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-payments] {e}\n")
        err(f"GL reversal failed: {e}")

    # Reverse PLE: mark existing as delinked, create offsetting entry
    q_ple = (Q.from_(PLE).select(PLE.star)
             .where(PLE.voucher_type == P())
             .where(PLE.voucher_id == P())
             .where(PLE.delinked == P()))
    ple_rows = conn.execute(q_ple.get_sql(), ("payment_entry", pe_id, 0)).fetchall()
    delink_sql = update_row("payment_ledger_entry",
                            data={"delinked": P(), "updated_at": LiteralValue("datetime('now')")},
                            where={"id": P()})
    ple_ins_sql, _ = insert_row("payment_ledger_entry", {
        "id": P(), "posting_date": P(), "account_id": P(),
        "party_type": P(), "party_id": P(),
        "voucher_type": P(), "voucher_id": P(),
        "amount": P(), "amount_in_account_currency": P(),
        "currency": P(), "remarks": P(),
    })
    for ple in ple_rows:
        ple_dict = row_to_dict(ple)
        conn.execute(delink_sql, (1, ple_dict["id"]))
        # Create reversing PLE
        reversal_amount = str(round_currency(-to_decimal(ple_dict["amount"])))
        conn.execute(ple_ins_sql,
            (str(uuid.uuid4()), pe["posting_date"], ple_dict["account_id"],
             ple_dict["party_type"], ple_dict["party_id"],
             "payment_entry", pe_id, reversal_amount, reversal_amount,
             ple_dict["currency"],
             f"Reversal: Payment {pe['naming_series']}"))

    sql = update_row("payment_entry",
                     data={"status": P(), "updated_at": LiteralValue("datetime('now')")},
                     where={"id": P()})
    conn.execute(sql, ("cancelled", pe_id))

    audit(conn, "erpclaw-payments", "cancel-payment", "payment_entry", pe_id,
           new_values={"reversed": True})
    conn.commit()

    ok({"status": "cancelled", "payment_entry_id": pe_id, "reversed": True})


# ---------------------------------------------------------------------------
# 7. delete-payment
# ---------------------------------------------------------------------------

def delete_payment(conn, args):
    """Delete a draft payment. Only drafts can be deleted."""
    pe_id = args.payment_entry_id
    if not pe_id:
        err("--payment-entry-id is required")

    pe = _get_pe_or_err(conn, pe_id)
    if pe["status"] != "draft":
        err(f"Cannot delete: payment is '{pe['status']}' (only 'draft' can be deleted)",
             suggestion="Cancel the document first, then delete.")

    naming = pe["naming_series"]
    conn.execute(Q.from_(PA).delete().where(PA.payment_entry_id == P()).get_sql(), (pe_id,))
    conn.execute(Q.from_(PD).delete().where(PD.payment_entry_id == P()).get_sql(), (pe_id,))
    conn.execute(Q.from_(PE).delete().where(PE.id == P()).get_sql(), (pe_id,))

    audit(conn, "erpclaw-payments", "delete-payment", "payment_entry", pe_id,
           old_values={"naming_series": naming})
    conn.commit()

    ok({"status": "deleted", "deleted": True})


# ---------------------------------------------------------------------------
# 8. create-payment-ledger-entry
# ---------------------------------------------------------------------------

def create_payment_ledger_entry(conn, args):
    """Create a PLE record. Called cross-skill by selling/buying on invoice submit."""
    voucher_type = args.voucher_type
    if not voucher_type:
        err("--voucher-type is required")
    voucher_id = args.voucher_id
    if not voucher_id:
        err("--voucher-id is required")
    party_type = args.party_type
    if not party_type or party_type not in VALID_PARTY_TYPES:
        err(f"--party-type is required. Valid: {VALID_PARTY_TYPES}")
    party_id = args.party_id
    if not party_id:
        err("--party-id is required")
    amount = args.ple_amount
    if not amount:
        err("--amount is required")
    posting_date = args.posting_date
    if not posting_date:
        err("--posting-date is required")
    account_id = args.account_id
    if not account_id:
        err("--account-id is required")

    ple_id = str(uuid.uuid4())
    dec_amount = round_currency(to_decimal(amount))

    sql, _ = insert_row("payment_ledger_entry", {
        "id": P(), "posting_date": P(), "account_id": P(),
        "party_type": P(), "party_id": P(),
        "voucher_type": P(), "voucher_id": P(),
        "against_voucher_type": P(), "against_voucher_id": P(),
        "amount": P(), "amount_in_account_currency": P(), "currency": P(),
    })
    conn.execute(sql,
        (ple_id, posting_date, account_id, party_type, party_id,
         voucher_type, voucher_id,
         args.against_voucher_type, args.against_voucher_id,
         str(dec_amount), str(dec_amount), "USD"))

    audit(conn, "erpclaw-payments", "create-payment-ledger-entry", "payment_ledger_entry", ple_id,
           new_values={"voucher_type": voucher_type, "amount": str(dec_amount)})
    conn.commit()

    ok({"status": "created", "ple_id": ple_id})


# ---------------------------------------------------------------------------
# 9. get-outstanding
# ---------------------------------------------------------------------------

def get_outstanding(conn, args):
    """Get outstanding amounts for a party from payment ledger entries."""
    party_type = args.party_type
    if not party_type:
        err("--party-type is required")
    party_id = args.party_id
    if not party_id:
        err("--party-id is required")

    ple = Table("payment_ledger_entry")
    base = (Q.from_(ple)
            .where(ple.party_type == P())
            .where(ple.party_id == P())
            .where(ple.delinked == P()))
    params = [party_type, party_id, 0]

    if args.voucher_type:
        base = base.where(ple.voucher_type == P())
        params.append(args.voucher_type)
    if args.voucher_id:
        base = base.where(ple.voucher_id == P())
        params.append(args.voucher_id)

    # Aggregate outstanding by voucher
    q = (base.select(
             ple.voucher_type, ple.voucher_id,
             DecimalSum(ple.amount).as_("outstanding_amount"),
             fn.Min(ple.posting_date).as_("posting_date"))
         .groupby(ple.voucher_type, ple.voucher_id)
         .having(LiteralValue('decimal_sum("amount") + 0 != 0'))
         .orderby(ple.posting_date))
    rows = conn.execute(q.get_sql(), params).fetchall()

    vouchers = []
    total_outstanding = Decimal("0")
    for row in rows:
        outstanding = round_currency(to_decimal(str(row["outstanding_amount"])))
        total_outstanding += outstanding
        vouchers.append({
            "voucher_type": row["voucher_type"],
            "voucher_id": row["voucher_id"],
            "outstanding_amount": str(outstanding),
            "posting_date": row["posting_date"],
        })

    ok({"outstanding": str(round_currency(total_outstanding)),
         "vouchers": vouchers})


# ---------------------------------------------------------------------------
# 10. get-unallocated-payments
# ---------------------------------------------------------------------------

def get_unallocated_payments(conn, args):
    """Get payments with unallocated amounts for a party."""
    party_type = args.party_type
    if not party_type:
        err("--party-type is required")
    party_id = args.party_id
    if not party_id:
        err("--party-id is required")
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    q = (Q.from_(PE)
         .select(PE.id, PE.naming_series, PE.paid_amount,
                 PE.unallocated_amount, PE.posting_date)
         .where(PE.party_type == P())
         .where(PE.party_id == P())
         .where(PE.company_id == P())
         .where(PE.status == P())
         .where(LiteralValue('"unallocated_amount" + 0 > 0'))
         .orderby(PE.posting_date))
    rows = conn.execute(q.get_sql(), (party_type, party_id, company_id, "submitted")).fetchall()

    ok({"payments": [row_to_dict(r) for r in rows]})


# ---------------------------------------------------------------------------
# 11. allocate-payment
# ---------------------------------------------------------------------------

def allocate_payment(conn, args):
    """Allocate a submitted payment to a voucher (invoice)."""
    pe_id = args.payment_entry_id
    if not pe_id:
        err("--payment-entry-id is required")
    voucher_type = args.voucher_type
    if not voucher_type:
        err("--voucher-type is required")
    voucher_id = args.voucher_id
    if not voucher_id:
        err("--voucher-id is required")
    allocated_amount = args.allocated_amount
    if not allocated_amount:
        err("--allocated-amount is required")

    pe = _get_pe_or_err(conn, pe_id)
    if pe["status"] != "submitted":
        err(f"Cannot allocate: payment is '{pe['status']}' (must be 'submitted')")

    amount = round_currency(to_decimal(allocated_amount))
    unallocated = to_decimal(pe["unallocated_amount"])

    if amount <= 0:
        err("--allocated-amount must be > 0")
    if amount > unallocated:
        err(f"Allocated amount ({amount}) exceeds unallocated ({unallocated})")

    alloc_id = str(uuid.uuid4())
    alloc_sql, _ = insert_row("payment_allocation", {
        "id": P(), "payment_entry_id": P(), "voucher_type": P(),
        "voucher_id": P(), "allocated_amount": P(),
    })
    conn.execute(alloc_sql, (alloc_id, pe_id, voucher_type, voucher_id, str(amount)))

    _recalc_unallocated(conn, pe_id)

    # Get updated unallocated
    qu = Q.from_(PE).select(PE.unallocated_amount).where(PE.id == P())
    updated = conn.execute(qu.get_sql(), (pe_id,)).fetchone()

    audit(conn, "erpclaw-payments", "allocate-payment", "payment_allocation", alloc_id,
           new_values={"payment_entry_id": pe_id, "voucher_id": voucher_id,
                       "allocated_amount": str(amount)})
    conn.commit()

    ok({"status": "created", "allocation_id": alloc_id,
         "remaining_unallocated": updated["unallocated_amount"]})


# ---------------------------------------------------------------------------
# 12. reconcile-payments
# ---------------------------------------------------------------------------

def reconcile_payments(conn, args):
    """Auto-reconcile payments against outstanding invoices (FIFO)."""
    party_type = args.party_type
    if not party_type:
        err("--party-type is required")
    party_id = args.party_id
    if not party_id:
        err("--party-id is required")
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")

    # Get unallocated submitted payments (FIFO by posting_date)
    # Uses arithmetic WHERE (unallocated_amount + 0 > 0) — keep raw SQL
    payments = conn.execute(
        """SELECT id, paid_amount, unallocated_amount, posting_date
           FROM payment_entry
           WHERE party_type = ? AND party_id = ? AND company_id = ?
             AND status = 'submitted'
             AND unallocated_amount + 0 > 0
           ORDER BY posting_date, created_at""",
        (party_type, party_id, company_id),
    ).fetchall()

    # Get outstanding vouchers from PLE (FIFO by posting_date)
    # Uses HAVING with decimal_sum + 0 > 0 — keep raw SQL
    outstanding_rows = conn.execute(
        """SELECT voucher_type, voucher_id,
               decimal_sum(amount) AS outstanding
           FROM payment_ledger_entry
           WHERE party_type = ? AND party_id = ? AND delinked = 0
             AND voucher_type IN ('sales_invoice', 'purchase_invoice')
           GROUP BY voucher_type, voucher_id
           HAVING decimal_sum(amount) + 0 > 0
           ORDER BY MIN(posting_date)""",
        (party_type, party_id),
    ).fetchall()

    matched = []
    pay_idx = 0
    inv_idx = 0
    pay_list = [row_to_dict(p) for p in payments]
    inv_list = [row_to_dict(r) for r in outstanding_rows]

    # Track remaining amounts
    for p in pay_list:
        p["remaining"] = to_decimal(p["unallocated_amount"])
    for inv in inv_list:
        inv["remaining"] = to_decimal(str(inv["outstanding"]))

    while pay_idx < len(pay_list) and inv_idx < len(inv_list):
        pay = pay_list[pay_idx]
        inv = inv_list[inv_idx]

        if pay["remaining"] <= 0:
            pay_idx += 1
            continue
        if inv["remaining"] <= 0:
            inv_idx += 1
            continue

        alloc_amount = min(pay["remaining"], inv["remaining"])
        alloc_amount = round_currency(alloc_amount)

        # Create allocation
        alloc_id = str(uuid.uuid4())
        recon_sql, _ = insert_row("payment_allocation", {
            "id": P(), "payment_entry_id": P(), "voucher_type": P(),
            "voucher_id": P(), "allocated_amount": P(),
        })
        conn.execute(recon_sql,
            (alloc_id, pay["id"], inv["voucher_type"], inv["voucher_id"],
             str(alloc_amount)))

        pay["remaining"] -= alloc_amount
        inv["remaining"] -= alloc_amount

        matched.append({
            "payment_id": pay["id"],
            "voucher_id": inv["voucher_id"],
            "allocated_amount": str(alloc_amount),
        })

        if pay["remaining"] <= 0:
            pay_idx += 1
        if inv["remaining"] <= 0:
            inv_idx += 1

    # Update unallocated amounts on all affected payments
    for pay in pay_list:
        _recalc_unallocated(conn, pay["id"])

    unmatched_payments = sum(1 for p in pay_list if p["remaining"] > 0)
    unmatched_invoices = sum(1 for inv in inv_list if inv["remaining"] > 0)

    conn.commit()

    ok({"matched": matched,
         "unmatched_payments": unmatched_payments,
         "unmatched_invoices": unmatched_invoices})


# ---------------------------------------------------------------------------
# 13. bank-reconciliation
# ---------------------------------------------------------------------------

def bank_reconciliation(conn, args):
    """Read-only bank reconciliation: compare GL balance with expected."""
    bank_account_id = args.bank_account_id
    if not bank_account_id:
        err("--bank-account-id is required")
    from_date = args.from_date
    if not from_date:
        err("--from-date is required")
    to_date = args.to_date
    if not to_date:
        err("--to-date is required")

    # Verify account exists
    qa = Q.from_(ACCOUNT).select(ACCOUNT.id, ACCOUNT.name).where(ACCOUNT.id == P())
    acct = conn.execute(qa.get_sql(), (bank_account_id,)).fetchone()
    if not acct:
        err(f"Bank account {bank_account_id} not found")

    # Get GL entries for this bank account in date range
    qg = (Q.from_(GL)
          .select(fn.Count("*").as_("entry_count"),
                  fn.Coalesce(DecimalSum(GL.debit), ValueWrapper("0")).as_("total_debit"),
                  fn.Coalesce(DecimalSum(GL.credit), ValueWrapper("0")).as_("total_credit"))
          .where(GL.account_id == P())
          .where(GL.posting_date >= P())
          .where(GL.posting_date <= P())
          .where(GL.is_cancelled == P()))
    rows = conn.execute(qg.get_sql(), (bank_account_id, from_date, to_date, 0)).fetchone()

    gl_balance = round_currency(
        to_decimal(str(rows["total_debit"])) - to_decimal(str(rows["total_credit"]))
    )

    # Get payment entries hitting this bank account in date range
    pe = Table("payment_entry")
    qp = (Q.from_(pe).select(fn.Count("*"))
          .where((pe.paid_from_account == P()) | (pe.paid_to_account == P()))
          .where(pe.posting_date >= P())
          .where(pe.posting_date <= P())
          .where(pe.status == P()))
    payment_count = conn.execute(
        qp.get_sql(), (bank_account_id, bank_account_id, from_date, to_date, "submitted")
    ).fetchone()[0]

    ok({
        "bank_account": dict(acct)["name"],
        "from_date": from_date,
        "to_date": to_date,
        "gl_entries": rows["entry_count"],
        "gl_balance": str(gl_balance),
        "payment_entries": payment_count,
    })


# ---------------------------------------------------------------------------
# 14. status
# ---------------------------------------------------------------------------

def status(conn, args):
    """Show payment entry counts and totals."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    pe = Table("payment_entry")
    q1 = (Q.from_(pe)
          .select(pe.status, fn.Count("*").as_("cnt"),
                  fn.Coalesce(DecimalSum(pe.paid_amount), ValueWrapper("0")).as_("total"))
          .where(pe.company_id == P())
          .groupby(pe.status))
    rows = conn.execute(q1.get_sql(), (company_id,)).fetchall()

    counts = {"total": 0, "draft": 0, "submitted": 0, "cancelled": 0}
    total_received = Decimal("0")
    total_paid = Decimal("0")
    for row in rows:
        counts[row["status"]] = row["cnt"]
        counts["total"] += row["cnt"]

    # Get totals by payment type for submitted only
    q2 = (Q.from_(pe)
          .select(pe.payment_type,
                  fn.Coalesce(DecimalSum(pe.paid_amount), ValueWrapper("0")).as_("total"))
          .where(pe.company_id == P())
          .where(pe.status == P())
          .groupby(pe.payment_type))
    type_rows = conn.execute(q2.get_sql(), (company_id, "submitted")).fetchall()
    for row in type_rows:
        if row["payment_type"] == "receive":
            total_received = round_currency(to_decimal(str(row["total"])))
        elif row["payment_type"] == "pay":
            total_paid = round_currency(to_decimal(str(row["total"])))

    counts["total_received"] = str(total_received)
    counts["total_paid"] = str(total_paid)

    ok(counts)


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-payment": add_payment,
    "update-payment": update_payment,
    "get-payment": get_payment,
    "list-payments": list_payments,
    "submit-payment": submit_payment,
    "cancel-payment": cancel_payment,
    "delete-payment": delete_payment,
    "create-payment-ledger-entry": create_payment_ledger_entry,
    "get-outstanding": get_outstanding,
    "get-unallocated-payments": get_unallocated_payments,
    "allocate-payment": allocate_payment,
    "reconcile-payments": reconcile_payments,
    "bank-reconciliation": bank_reconciliation,
    "status": status,
}


def main():
    parser = SafeArgumentParser(description="ERPClaw Payments Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Payment entry fields
    parser.add_argument("--payment-entry-id")
    parser.add_argument("--company-id")
    parser.add_argument("--payment-type")
    parser.add_argument("--posting-date")
    parser.add_argument("--party-type")
    parser.add_argument("--party-id")
    parser.add_argument("--paid-from-account")
    parser.add_argument("--paid-to-account")
    parser.add_argument("--paid-amount")
    parser.add_argument("--payment-currency", default="USD")
    parser.add_argument("--exchange-rate", default="1")
    parser.add_argument("--reference-number")
    parser.add_argument("--reference-date")
    parser.add_argument("--allocations")

    # Allocation
    parser.add_argument("--voucher-type")
    parser.add_argument("--voucher-id")
    parser.add_argument("--allocated-amount")

    # PLE
    parser.add_argument("--amount", dest="ple_amount")
    parser.add_argument("--account-id")
    parser.add_argument("--against-voucher-type")
    parser.add_argument("--against-voucher-id")

    # Bank reconciliation
    parser.add_argument("--bank-account-id")

    # List filters
    parser.add_argument("--status", dest="pe_status")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")

    args, unknown = parser.parse_known_args()
    check_unknown_args(parser, unknown)
    check_input_lengths(args)
    action_fn = ACTIONS[args.action]

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    # Dependency check
    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = "clawhub install " + " ".join(_dep.get("missing_skills", []))
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

    try:
        action_fn(conn, args)
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[erpclaw-payments] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
