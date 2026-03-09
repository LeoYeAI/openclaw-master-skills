#!/usr/bin/env python3
"""ERPClaw Buying Skill — db_query.py

Procure-to-pay cycle: suppliers, material requests, RFQs, supplier quotations,
purchase orders, purchase receipts (GRN), purchase invoices, debit notes,
landed cost vouchers.

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
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.stock_posting import (
        insert_sle_entries,
        reverse_sle_entries,
        get_stock_balance,
        get_valuation_rate,
        create_perpetual_inventory_gl,
    )
    from erpclaw_lib.gl_posting import insert_gl_entries, reverse_gl_entries
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query import Q, P, Table, Field, fn, Case, Order, Criterion, Not, NULL, DecimalSum, DecimalAbs
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)



REQUIRED_TABLES = ["company", "account", "item"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json_arg(value, name):
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        err(f"Invalid JSON for --{name}: {value}")


def _get_fiscal_year(conn, posting_date: str) -> str | None:
    fy_t = Table("fiscal_year")
    q = (Q.from_(fy_t)
         .select(fy_t.name)
         .where(fy_t.start_date <= P())
         .where(fy_t.end_date >= P())
         .where(fy_t.is_closed == 0))
    fy = conn.execute(q.get_sql(), (posting_date, posting_date)).fetchone()
    return fy["name"] if fy else None


def _get_cost_center(conn, company_id: str) -> str | None:
    cc_t = Table("cost_center")
    q = (Q.from_(cc_t)
         .select(cc_t.id)
         .where(cc_t.company_id == P())
         .where(cc_t.is_group == 0)
         .limit(1))
    cc = conn.execute(q.get_sql(), (company_id,)).fetchone()
    return cc["id"] if cc else None


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _calculate_tax(conn, tax_template_id, subtotal):
    """Calculate tax from template. Returns (tax_amount, tax_details list)."""
    if not tax_template_id:
        return Decimal("0"), []
    ttl = Table("tax_template_line").as_("ttl")
    a = Table("account").as_("a")
    q = (Q.from_(ttl)
         .left_join(a).on(a.id == ttl.tax_account_id)
         .select(ttl.star, a.name.as_("account_name"))
         .where(ttl.tax_template_id == P())
         .orderby(ttl.row_order))
    lines = conn.execute(q.get_sql(), (tax_template_id,)).fetchall()
    if not lines:
        return Decimal("0"), []
    total_tax = Decimal("0")
    details = []
    cumulative = subtotal
    for line in lines:
        ld = row_to_dict(line)
        rate = to_decimal(ld.get("rate", "0"))
        charge_type = ld.get("charge_type", "on_net_total")
        if charge_type == "on_net_total":
            tax_amt = round_currency(subtotal * rate / Decimal("100"))
        elif charge_type == "on_previous_row_total":
            tax_amt = round_currency(cumulative * rate / Decimal("100"))
        elif charge_type == "actual":
            tax_amt = round_currency(rate)
        else:
            tax_amt = round_currency(subtotal * rate / Decimal("100"))
        if ld.get("add_deduct") == "deduct":
            tax_amt = -tax_amt
        total_tax += tax_amt
        cumulative += tax_amt
        details.append({
            "tax_account_id": ld["tax_account_id"],
            "account_name": ld.get("account_name"),
            "rate": str(rate),
            "tax_amount": str(tax_amt),
        })
    return round_currency(total_tax), details


# ---------------------------------------------------------------------------
# 1. add-supplier
# ---------------------------------------------------------------------------

def add_supplier(conn, args):
    """Create a supplier record."""
    if not args.name:
        err("--name is required")
    if not args.company_id:
        err("--company-id is required")

    company_t = Table("company")
    q = Q.from_(company_t).select(company_t.id).where(company_t.id == P())
    if not conn.execute(q.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    supplier_type = args.supplier_type or "company"
    if supplier_type not in ("company", "individual"):
        err("--supplier-type must be 'company' or 'individual'")

    if args.payment_terms_id:
        pt_t = Table("payment_terms")
        q = Q.from_(pt_t).select(pt_t.id).where(pt_t.id == P())
        if not conn.execute(q.get_sql(), (args.payment_terms_id,)).fetchone():
            err(f"Payment terms {args.payment_terms_id} not found")

    primary_address = args.primary_address
    if primary_address:
        _parse_json_arg(primary_address, "primary-address")

    is_1099 = int(args.is_1099_vendor) if args.is_1099_vendor else 0

    supplier_id = str(uuid.uuid4())
    try:
        s_t = Table("supplier")
        q = (Q.into(s_t)
             .columns("id", "name", "supplier_group", "supplier_type",
                      "payment_terms_id", "tax_id", "is_1099_vendor",
                      "primary_address", "status", "company_id")
             .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                     ValueWrapper("active"), P()))
        conn.execute(q.get_sql(),
            (supplier_id, args.name, args.supplier_group, supplier_type,
             args.payment_terms_id, args.tax_id, is_1099,
             primary_address, args.company_id))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-buying] {e}\n")
        err("Supplier creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-buying", "add-supplier", "supplier", supplier_id,
           new_values={"name": args.name, "type": supplier_type})
    conn.commit()
    ok({"supplier_id": supplier_id, "name": args.name})


# ---------------------------------------------------------------------------
# 2. update-supplier
# ---------------------------------------------------------------------------

def update_supplier(conn, args):
    """Update a supplier."""
    if not args.supplier_id:
        err("--supplier-id is required")

    s_t = Table("supplier")
    q = (Q.from_(s_t).select(s_t.star)
         .where((s_t.id == P()) | (s_t.name == P())))
    supplier = conn.execute(q.get_sql(),
                            (args.supplier_id, args.supplier_id)).fetchone()
    if not supplier:
        err(f"Supplier {args.supplier_id} not found",
             suggestion="Use 'list suppliers' to see available suppliers.")
    args.supplier_id = supplier["id"]  # normalize to id

    updates, params, updated_fields = [], [], []

    if args.name is not None:
        updates.append("name = ?")
        params.append(args.name)
        updated_fields.append("name")
    if args.payment_terms_id is not None:
        updates.append("payment_terms_id = ?")
        params.append(args.payment_terms_id)
        updated_fields.append("payment_terms_id")
    if args.supplier_group is not None:
        updates.append("supplier_group = ?")
        params.append(args.supplier_group)
        updated_fields.append("supplier_group")
    if args.supplier_type is not None:
        if args.supplier_type not in ("company", "individual"):
            err("--supplier-type must be 'company' or 'individual'")
        updates.append("supplier_type = ?")
        params.append(args.supplier_type)
        updated_fields.append("supplier_type")

    if not updated_fields:
        err("No fields to update")

    # raw SQL — dynamic column list built at runtime
    updates.append("updated_at = datetime('now')")
    params.append(args.supplier_id)
    conn.execute(f"UPDATE supplier SET {', '.join(updates)} WHERE id = ?", params)

    audit(conn, "erpclaw-buying", "update-supplier", "supplier", args.supplier_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"supplier_id": args.supplier_id, "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 3. get-supplier
# ---------------------------------------------------------------------------

def get_supplier(conn, args):
    """Get supplier with outstanding summary."""
    if not args.supplier_id:
        err("--supplier-id is required")

    s_t = Table("supplier")
    q = (Q.from_(s_t).select(s_t.star)
         .where((s_t.id == P()) | (s_t.name == P())))
    supplier = conn.execute(q.get_sql(),
                            (args.supplier_id, args.supplier_id)).fetchone()
    if not supplier:
        err(f"Supplier {args.supplier_id} not found")

    data = row_to_dict(supplier)

    # Outstanding from purchase invoices
    pi_t = Table("purchase_invoice")
    q = (Q.from_(pi_t)
         .select(fn.Coalesce(DecimalSum(pi_t.outstanding_amount), ValueWrapper("0")).as_("total_outstanding"),
                 fn.Count("*").as_("invoice_count"))
         .where(pi_t.supplier_id == P())
         .where(pi_t.status.isin([P(), P(), P()])))
    outstanding = conn.execute(q.get_sql(),
        (args.supplier_id, "submitted", "overdue", "partially_paid")).fetchone()
    data["total_outstanding"] = str(round_currency(to_decimal(str(outstanding["total_outstanding"]))))
    data["outstanding_invoice_count"] = outstanding["invoice_count"]

    ok(data)


# ---------------------------------------------------------------------------
# 4. list-suppliers
# ---------------------------------------------------------------------------

def list_suppliers(conn, args):
    """List suppliers with filtering."""
    s = Table("supplier").as_("s")
    params = []

    count_q = Q.from_(s).select(fn.Count("*"))
    data_q = (Q.from_(s)
              .select(s.id, s.name, s.supplier_group, s.supplier_type,
                      s.tax_id, s.is_1099_vendor, s.status, s.company_id))

    if args.company_id:
        count_q = count_q.where(s.company_id == P())
        data_q = data_q.where(s.company_id == P())
        params.append(args.company_id)
    if args.supplier_group:
        count_q = count_q.where(s.supplier_group == P())
        data_q = data_q.where(s.supplier_group == P())
        params.append(args.supplier_group)
    if args.search:
        crit = (s.name.like(P())) | (s.tax_id.like(P()))
        count_q = count_q.where(crit)
        data_q = data_q.where(crit)
        params.extend([f"%{args.search}%", f"%{args.search}%"])

    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    data_params = params + [limit, offset]

    data_q = data_q.orderby(s.name).limit(P()).offset(P())
    rows = conn.execute(data_q.get_sql(), data_params).fetchall()

    ok({"suppliers": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 5. add-material-request
# ---------------------------------------------------------------------------

def add_material_request(conn, args):
    """Create a material request in draft."""
    if not args.request_type:
        err("--request-type is required (purchase|transfer|manufacture)")
    valid_types = ("purchase", "transfer", "manufacture",
                   "material_transfer", "material_issue")
    rtype = args.request_type
    if rtype == "transfer":
        rtype = "material_transfer"
    if rtype not in ("purchase", "material_transfer", "material_issue", "manufacture"):
        err(f"--request-type must be one of: purchase, transfer, manufacture")
    if not args.items:
        err("--items is required (JSON array)")
    if not args.company_id:
        err("--company-id is required")

    company_t = Table("company")
    q = Q.from_(company_t).select(company_t.id).where(company_t.id == P())
    if not conn.execute(q.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    mr_id = str(uuid.uuid4())

    # Insert parent first (FK target)
    mr_t = Table("material_request")
    q = (Q.into(mr_t)
         .columns("id", "request_type", "status", "company_id")
         .insert(P(), P(), ValueWrapper("draft"), P()))
    conn.execute(q.get_sql(), (mr_id, rtype, args.company_id))

    mri_t = Table("material_request_item")
    mri_q = (Q.into(mri_t)
             .columns("id", "material_request_id", "item_id", "quantity", "warehouse_id")
             .insert(P(), P(), P(), P(), P()))
    mri_sql = mri_q.get_sql()

    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")

        conn.execute(mri_sql,
            (str(uuid.uuid4()), mr_id, item_id, str(round_currency(qty)),
             item.get("warehouse_id")))

    audit(conn, "erpclaw-buying", "add-material-request", "material_request", mr_id,
           new_values={"request_type": rtype, "item_count": len(items)})
    conn.commit()
    ok({"material_request_id": mr_id, "request_type": rtype,
         "item_count": len(items)})


# ---------------------------------------------------------------------------
# 6. submit-material-request
# ---------------------------------------------------------------------------

def submit_material_request(conn, args):
    """Submit a material request."""
    if not args.material_request_id:
        err("--material-request-id is required")

    mr_t = Table("material_request")
    q = Q.from_(mr_t).select(mr_t.star).where(mr_t.id == P())
    mr = conn.execute(q.get_sql(), (args.material_request_id,)).fetchone()
    if not mr:
        err(f"Material request {args.material_request_id} not found")
    if mr["status"] != "draft":
        err(f"Cannot submit: material request is '{mr['status']}' (must be 'draft')")

    naming = get_next_name(conn, "material_request", company_id=mr["company_id"])

    q = (Q.update(mr_t)
         .set(mr_t.status, ValueWrapper("submitted"))
         .set(mr_t.naming_series, P())
         .set(mr_t.updated_at, LiteralValue("datetime('now')"))
         .where(mr_t.id == P()))
    conn.execute(q.get_sql(), (naming, args.material_request_id))

    audit(conn, "erpclaw-buying", "submit-material-request", "material_request",
           args.material_request_id,
           new_values={"naming_series": naming})
    conn.commit()
    ok({"material_request_id": args.material_request_id,
         "naming_series": naming, "status": "submitted"})


# ---------------------------------------------------------------------------
# 7. list-material-requests
# ---------------------------------------------------------------------------

def list_material_requests(conn, args):
    """List material requests."""
    mr = Table("material_request").as_("mr")
    params = []

    count_q = Q.from_(mr).select(fn.Count("*"))
    data_q = Q.from_(mr).select(mr.star)

    if args.company_id:
        count_q = count_q.where(mr.company_id == P())
        data_q = data_q.where(mr.company_id == P())
        params.append(args.company_id)
    if args.request_type:
        rtype = args.request_type
        if rtype == "transfer":
            rtype = "material_transfer"
        count_q = count_q.where(mr.request_type == P())
        data_q = data_q.where(mr.request_type == P())
        params.append(rtype)
    if args.mr_status:
        count_q = count_q.where(mr.status == P())
        data_q = data_q.where(mr.status == P())
        params.append(args.mr_status)

    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    data_params = params + [limit, offset]

    data_q = data_q.orderby(mr.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(data_q.get_sql(), data_params).fetchall()

    ok({"material_requests": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 8. add-rfq
# ---------------------------------------------------------------------------

def add_rfq(conn, args):
    """Create a Request for Quotation."""
    if not args.items:
        err("--items is required (JSON array)")
    if not args.suppliers:
        err("--suppliers is required (JSON array of supplier IDs)")
    if not args.company_id:
        err("--company-id is required")

    company_t = Table("company")
    q = Q.from_(company_t).select(company_t.id).where(company_t.id == P())
    if not conn.execute(q.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    items = _parse_json_arg(args.items, "items")
    suppliers = _parse_json_arg(args.suppliers, "suppliers")

    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")
    if not suppliers or not isinstance(suppliers, list):
        err("--suppliers must be a non-empty JSON array")

    # Validate suppliers exist
    sup_t = Table("supplier")
    sup_q = Q.from_(sup_t).select(sup_t.id).where(sup_t.id == P())
    sup_sql = sup_q.get_sql()
    for sid in suppliers:
        if not conn.execute(sup_sql, (sid,)).fetchone():
            err(f"Supplier {sid} not found")

    rfq_id = str(uuid.uuid4())
    today = _today()

    # Insert parent first
    rfq_t = Table("request_for_quotation")
    q = (Q.into(rfq_t)
         .columns("id", "rfq_date", "status", "company_id")
         .insert(P(), P(), ValueWrapper("draft"), P()))
    conn.execute(q.get_sql(), (rfq_id, today, args.company_id))

    # Insert RFQ items
    ri_t = Table("rfq_item")
    ri_q = (Q.into(ri_t)
            .columns("id", "rfq_id", "item_id", "quantity", "uom", "required_date")
            .insert(P(), P(), P(), P(), P(), P()))
    ri_sql = ri_q.get_sql()
    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")
        conn.execute(ri_sql,
            (str(uuid.uuid4()), rfq_id, item_id, str(round_currency(qty)),
             item.get("uom"), item.get("required_date")))

    # Insert RFQ suppliers
    rs_t = Table("rfq_supplier")
    rs_q = (Q.into(rs_t)
            .columns("id", "rfq_id", "supplier_id")
            .insert(P(), P(), P()))
    rs_sql = rs_q.get_sql()
    for sid in suppliers:
        conn.execute(rs_sql, (str(uuid.uuid4()), rfq_id, sid))

    audit(conn, "erpclaw-buying", "add-rfq", "request_for_quotation", rfq_id,
           new_values={"item_count": len(items), "supplier_count": len(suppliers)})
    conn.commit()
    ok({"rfq_id": rfq_id, "item_count": len(items),
         "supplier_count": len(suppliers)})


# ---------------------------------------------------------------------------
# 9. submit-rfq
# ---------------------------------------------------------------------------

def submit_rfq(conn, args):
    """Submit an RFQ."""
    if not args.rfq_id:
        err("--rfq-id is required")

    rfq_t = Table("request_for_quotation")
    q = Q.from_(rfq_t).select(rfq_t.star).where(rfq_t.id == P())
    rfq = conn.execute(q.get_sql(), (args.rfq_id,)).fetchone()
    if not rfq:
        err(f"RFQ {args.rfq_id} not found")
    if rfq["status"] != "draft":
        err(f"Cannot submit: RFQ is '{rfq['status']}' (must be 'draft')")

    naming = get_next_name(conn, "request_for_quotation",
                           company_id=rfq["company_id"])

    q = (Q.update(rfq_t)
         .set(rfq_t.status, ValueWrapper("submitted"))
         .set(rfq_t.naming_series, P())
         .set(rfq_t.updated_at, LiteralValue("datetime('now')"))
         .where(rfq_t.id == P()))
    conn.execute(q.get_sql(), (naming, args.rfq_id))

    # Mark sent_date on rfq_supplier rows
    rs_t = Table("rfq_supplier")
    q = (Q.update(rs_t)
         .set(rs_t.sent_date, LiteralValue("datetime('now')"))
         .where(rs_t.rfq_id == P()))
    conn.execute(q.get_sql(), (args.rfq_id,))

    audit(conn, "erpclaw-buying", "submit-rfq", "request_for_quotation", args.rfq_id,
           new_values={"naming_series": naming})
    conn.commit()
    ok({"rfq_id": args.rfq_id, "naming_series": naming,
         "status": "submitted"})


# ---------------------------------------------------------------------------
# 10. list-rfqs
# ---------------------------------------------------------------------------

def list_rfqs(conn, args):
    """List RFQs."""
    r = Table("request_for_quotation").as_("r")
    params = []

    count_q = Q.from_(r).select(fn.Count("*"))
    data_q = Q.from_(r).select(r.star)

    if args.company_id:
        count_q = count_q.where(r.company_id == P())
        data_q = data_q.where(r.company_id == P())
        params.append(args.company_id)
    if args.rfq_status:
        count_q = count_q.where(r.status == P())
        data_q = data_q.where(r.status == P())
        params.append(args.rfq_status)

    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    data_params = params + [limit, offset]

    data_q = data_q.orderby(r.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(data_q.get_sql(), data_params).fetchall()

    ok({"rfqs": [row_to_dict(r_row) for r_row in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 11. add-supplier-quotation
# ---------------------------------------------------------------------------

def add_supplier_quotation(conn, args):
    """Record a supplier's quotation response to an RFQ."""
    if not args.rfq_id:
        err("--rfq-id is required")
    if not args.supplier_id:
        err("--supplier-id is required")
    if not args.items:
        err("--items is required (JSON array with prices)")

    rfq_t = Table("request_for_quotation")
    q = Q.from_(rfq_t).select(rfq_t.star).where(rfq_t.id == P())
    rfq = conn.execute(q.get_sql(), (args.rfq_id,)).fetchone()
    if not rfq:
        err(f"RFQ {args.rfq_id} not found")

    sup_t = Table("supplier")
    q = (Q.from_(sup_t).select(sup_t.star)
         .where((sup_t.id == P()) | (sup_t.name == P())))
    supplier = conn.execute(q.get_sql(),
                            (args.supplier_id, args.supplier_id)).fetchone()
    if not supplier:
        err(f"Supplier {args.supplier_id} not found")
    args.supplier_id = supplier["id"]  # normalize to id

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    sq_id = str(uuid.uuid4())
    today = _today()
    total_amount = Decimal("0")

    # Insert parent first
    sq_t = Table("supplier_quotation")
    q = (Q.into(sq_t)
         .columns("id", "supplier_id", "quotation_date", "rfq_id",
                  "total_amount", "grand_total", "status", "company_id")
         .insert(P(), P(), P(), P(), ValueWrapper("0"), ValueWrapper("0"),
                 ValueWrapper("draft"), P()))
    conn.execute(q.get_sql(),
        (sq_id, args.supplier_id, today, args.rfq_id, rfq["company_id"]))

    ri_t = Table("rfq_item")
    ri_q = Q.from_(ri_t).select(ri_t.star).where(ri_t.id == P())
    ri_sql = ri_q.get_sql()

    sqi_t = Table("supplier_quotation_item")
    sqi_q = (Q.into(sqi_t)
             .columns("id", "supplier_quotation_id", "item_id", "quantity",
                      "rate", "amount", "lead_time_days")
             .insert(P(), P(), P(), P(), P(), P(), P()))
    sqi_sql = sqi_q.get_sql()

    for i, item in enumerate(items):
        rfq_item_id = item.get("rfq_item_id")
        if not rfq_item_id:
            err(f"Item {i}: rfq_item_id is required")
        rate = to_decimal(item.get("rate", "0"))
        if rate <= 0:
            err(f"Item {i}: rate must be > 0")

        # Get qty from the rfq_item
        rfq_item = conn.execute(ri_sql, (rfq_item_id,)).fetchone()
        if not rfq_item:
            err(f"Item {i}: rfq_item {rfq_item_id} not found")

        qty = to_decimal(rfq_item["quantity"])
        amount = round_currency(qty * rate)
        total_amount += amount

        conn.execute(sqi_sql,
            (str(uuid.uuid4()), sq_id, rfq_item["item_id"],
             str(round_currency(qty)), str(round_currency(rate)),
             str(amount), item.get("lead_time_days")))

    # Update totals
    q = (Q.update(sq_t)
         .set(sq_t.total_amount, P())
         .set(sq_t.grand_total, P())
         .where(sq_t.id == P()))
    conn.execute(q.get_sql(),
        (str(round_currency(total_amount)), str(round_currency(total_amount)), sq_id))

    # Mark rfq_supplier as having a response
    rs_t = Table("rfq_supplier")
    q = (Q.update(rs_t)
         .set(rs_t.response_date, LiteralValue("datetime('now')"))
         .set(rs_t.supplier_quotation_id, P())
         .where(rs_t.rfq_id == P())
         .where(rs_t.supplier_id == P()))
    conn.execute(q.get_sql(), (sq_id, args.rfq_id, args.supplier_id))

    # Update RFQ status if all suppliers responded
    q = (Q.from_(rs_t)
         .select(fn.Count("*").as_("total"),
                 fn.Sum(Case().when(rs_t.supplier_quotation_id.isnotnull(), 1).else_(0)).as_("responded"))
         .where(rs_t.rfq_id == P()))
    all_responded = conn.execute(q.get_sql(), (args.rfq_id,)).fetchone()
    if all_responded["total"] == all_responded["responded"]:
        q = (Q.update(rfq_t)
             .set(rfq_t.status, ValueWrapper("quotation_received"))
             .set(rfq_t.updated_at, LiteralValue("datetime('now')"))
             .where(rfq_t.id == P()))
        conn.execute(q.get_sql(), (args.rfq_id,))

    audit(conn, "erpclaw-buying", "add-supplier-quotation", "supplier_quotation", sq_id,
           new_values={"supplier_id": args.supplier_id, "rfq_id": args.rfq_id,
                       "total_amount": str(round_currency(total_amount))})
    conn.commit()
    ok({"supplier_quotation_id": sq_id,
         "total_amount": str(round_currency(total_amount))})


# ---------------------------------------------------------------------------
# 12. list-supplier-quotations
# ---------------------------------------------------------------------------

def list_supplier_quotations(conn, args):
    """List supplier quotations."""
    sq = Table("supplier_quotation").as_("sq")
    s = Table("supplier").as_("s")
    params = []

    count_q = Q.from_(sq).select(fn.Count("*"))
    data_q = (Q.from_(sq)
              .left_join(s).on(s.id == sq.supplier_id)
              .select(sq.star, s.name.as_("supplier_name")))

    if args.rfq_id:
        count_q = count_q.where(sq.rfq_id == P())
        data_q = data_q.where(sq.rfq_id == P())
        params.append(args.rfq_id)
    if args.supplier_id:
        count_q = count_q.where(sq.supplier_id == P())
        data_q = data_q.where(sq.supplier_id == P())
        params.append(args.supplier_id)

    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    data_params = params + [limit, offset]

    data_q = data_q.orderby(sq.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(data_q.get_sql(), data_params).fetchall()

    ok({"supplier_quotations": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 13. compare-supplier-quotations
# ---------------------------------------------------------------------------

def compare_supplier_quotations(conn, args):
    """Compare supplier quotes for the same RFQ items side by side."""
    if not args.rfq_id:
        err("--rfq-id is required")

    rfq_t = Table("request_for_quotation")
    q = Q.from_(rfq_t).select(rfq_t.star).where(rfq_t.id == P())
    rfq = conn.execute(q.get_sql(), (args.rfq_id,)).fetchone()
    if not rfq:
        err(f"RFQ {args.rfq_id} not found")

    # Get all RFQ items
    ri = Table("rfq_item").as_("ri")
    i_t = Table("item").as_("i")
    q = (Q.from_(ri)
         .left_join(i_t).on(i_t.id == ri.item_id)
         .select(ri.star, i_t.item_code, i_t.item_name)
         .where(ri.rfq_id == P()))
    rfq_items = conn.execute(q.get_sql(), (args.rfq_id,)).fetchall()

    # Get all supplier quotations for this RFQ
    sq_t = Table("supplier_quotation").as_("sq")
    s_t = Table("supplier").as_("s")
    q = (Q.from_(sq_t)
         .left_join(s_t).on(s_t.id == sq_t.supplier_id)
         .select(sq_t.star, s_t.name.as_("supplier_name"))
         .where(sq_t.rfq_id == P()))
    sqs = conn.execute(q.get_sql(), (args.rfq_id,)).fetchall()

    sqi_t = Table("supplier_quotation_item")
    sqi_q = (Q.from_(sqi_t).select(sqi_t.star)
             .where(sqi_t.supplier_quotation_id == P())
             .where(sqi_t.item_id == P()))
    sqi_sql = sqi_q.get_sql()

    comparison = []
    for ri_row in rfq_items:
        ri_d = row_to_dict(ri_row)
        item_comparison = {
            "item_id": ri_d["item_id"],
            "item_code": ri_d.get("item_code"),
            "item_name": ri_d.get("item_name"),
            "required_qty": ri_d["quantity"],
            "quotes": [],
            "lowest_rate": None,
            "lowest_supplier": None,
        }
        lowest_rate = None
        for sq_row in sqs:
            sq = row_to_dict(sq_row)
            # Find the quote item for this RFQ item
            sqi = conn.execute(sqi_sql,
                (sq["id"], ri_d["item_id"])).fetchone()
            if sqi:
                sqi_d = row_to_dict(sqi)
                rate = to_decimal(sqi_d["rate"])
                quote_info = {
                    "supplier_id": sq["supplier_id"],
                    "supplier_name": sq.get("supplier_name"),
                    "rate": sqi_d["rate"],
                    "amount": sqi_d["amount"],
                    "lead_time_days": sqi_d.get("lead_time_days"),
                    "is_lowest": False,
                }
                item_comparison["quotes"].append(quote_info)
                if lowest_rate is None or rate < lowest_rate:
                    lowest_rate = rate
                    item_comparison["lowest_rate"] = str(round_currency(rate))
                    item_comparison["lowest_supplier"] = sq.get("supplier_name")

        # Mark lowest
        for q in item_comparison["quotes"]:
            if item_comparison["lowest_rate"] and q["rate"] == item_comparison["lowest_rate"]:
                q["is_lowest"] = True

        comparison.append(item_comparison)

    ok({"rfq_id": args.rfq_id, "comparison": comparison,
         "supplier_count": len(sqs)})


# ---------------------------------------------------------------------------
# 14. add-purchase-order
# ---------------------------------------------------------------------------

def add_purchase_order(conn, args):
    """Create a purchase order in draft."""
    if not args.supplier_id:
        err("--supplier-id is required")
    if not args.items:
        err("--items is required (JSON array)")
    if not args.company_id:
        err("--company-id is required")

    sup_t = Table("supplier")
    q = (Q.from_(sup_t).select(sup_t.star)
         .where((sup_t.id == P()) | (sup_t.name == P())))
    supplier = conn.execute(q.get_sql(),
                            (args.supplier_id, args.supplier_id)).fetchone()
    if not supplier:
        err(f"Supplier {args.supplier_id} not found")
    args.supplier_id = supplier["id"]  # normalize to id
    if supplier["status"] != "active":
        err(f"Supplier {supplier['name']} is {supplier['status']}")

    company_t = Table("company")
    q = Q.from_(company_t).select(company_t.id).where(company_t.id == P())
    if not conn.execute(q.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    po_id = str(uuid.uuid4())
    posting_date = args.posting_date or _today()
    total_amount = Decimal("0")

    # Validate items and compute totals
    item_rows = []
    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")
        rate = to_decimal(item.get("rate", "0"))
        if rate <= 0:
            err(f"Item {i}: rate must be > 0")

        discount_pct = to_decimal(item.get("discount_percentage", "0"))
        amount = round_currency(qty * rate)
        net_amount = round_currency(amount * (Decimal("1") - discount_pct / Decimal("100")))
        total_amount += net_amount

        item_rows.append((
            str(uuid.uuid4()), po_id, item_id, str(round_currency(qty)),
            item.get("uom"), str(round_currency(rate)), str(amount),
            str(round_currency(discount_pct)), str(net_amount),
            item.get("warehouse_id"), item.get("required_date"),
        ))

    # Calculate tax
    tax_amount, tax_details = _calculate_tax(conn, args.tax_template_id, total_amount)
    grand_total = round_currency(total_amount + tax_amount)

    # Insert parent first
    po_t = Table("purchase_order")
    q = (Q.into(po_t)
         .columns("id", "supplier_id", "order_date", "total_amount",
                  "tax_amount", "grand_total", "tax_template_id", "status",
                  "company_id")
         .insert(P(), P(), P(), P(), P(), P(), P(), ValueWrapper("draft"), P()))
    conn.execute(q.get_sql(),
        (po_id, args.supplier_id, posting_date,
         str(round_currency(total_amount)), str(round_currency(tax_amount)),
         str(grand_total), args.tax_template_id, args.company_id))

    # Insert items
    poi_t = Table("purchase_order_item")
    poi_q = (Q.into(poi_t)
             .columns("id", "purchase_order_id", "item_id", "quantity", "uom",
                      "rate", "amount", "discount_percentage", "net_amount",
                      "warehouse_id", "required_date")
             .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    poi_sql = poi_q.get_sql()
    for row_params in item_rows:
        conn.execute(poi_sql, row_params)

    audit(conn, "erpclaw-buying", "add-purchase-order", "purchase_order", po_id,
           new_values={"supplier_id": args.supplier_id,
                       "grand_total": str(grand_total)})
    conn.commit()
    ok({"purchase_order_id": po_id,
         "total_amount": str(round_currency(total_amount)),
         "tax_amount": str(round_currency(tax_amount)),
         "grand_total": str(grand_total)})


# ---------------------------------------------------------------------------
# 15. update-purchase-order
# ---------------------------------------------------------------------------

def update_purchase_order(conn, args):
    """Update a draft purchase order's items."""
    if not args.purchase_order_id:
        err("--purchase-order-id is required")

    po_t = Table("purchase_order")
    q = Q.from_(po_t).select(po_t.star).where(po_t.id == P())
    po = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchone()
    if not po:
        err(f"Purchase order {args.purchase_order_id} not found")
    if po["status"] != "draft":
        err(f"Cannot update: PO is '{po['status']}' (must be 'draft')",
             suggestion="Cancel the document first, then make changes.")

    if not args.items:
        err("--items is required for update")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    # Delete old items and re-insert
    poi_t = Table("purchase_order_item")
    q = Q.from_(poi_t).delete().where(poi_t.purchase_order_id == P())
    conn.execute(q.get_sql(), (args.purchase_order_id,))

    total_amount = Decimal("0")
    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")
        rate = to_decimal(item.get("rate", "0"))
        if rate <= 0:
            err(f"Item {i}: rate must be > 0")

        discount_pct = to_decimal(item.get("discount_percentage", "0"))
        amount = round_currency(qty * rate)
        net_amount = round_currency(amount * (Decimal("1") - discount_pct / Decimal("100")))
        total_amount += net_amount

        # raw SQL — reuse same INSERT pattern for PO items
        conn.execute(
            """INSERT INTO purchase_order_item
               (id, purchase_order_id, item_id, quantity, uom, rate, amount,
                discount_percentage, net_amount, warehouse_id, required_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), args.purchase_order_id, item_id,
             str(round_currency(qty)), item.get("uom"),
             str(round_currency(rate)), str(amount),
             str(round_currency(discount_pct)), str(net_amount),
             item.get("warehouse_id"), item.get("required_date")),
        )

    tax_amount, _ = _calculate_tax(conn, po["tax_template_id"], total_amount)
    grand_total = round_currency(total_amount + tax_amount)

    q = (Q.update(po_t)
         .set(po_t.total_amount, P())
         .set(po_t.tax_amount, P())
         .set(po_t.grand_total, P())
         .set(po_t.updated_at, LiteralValue("datetime('now')"))
         .where(po_t.id == P()))
    conn.execute(q.get_sql(),
        (str(round_currency(total_amount)), str(round_currency(tax_amount)),
         str(grand_total), args.purchase_order_id))

    audit(conn, "erpclaw-buying", "update-purchase-order", "purchase_order",
           args.purchase_order_id,
           new_values={"grand_total": str(grand_total)})
    conn.commit()
    ok({"purchase_order_id": args.purchase_order_id,
         "total_amount": str(round_currency(total_amount)),
         "grand_total": str(grand_total)})


# ---------------------------------------------------------------------------
# 16. get-purchase-order
# ---------------------------------------------------------------------------

def get_purchase_order(conn, args):
    """Get PO with items and receipt/billing status."""
    if not args.purchase_order_id:
        err("--purchase-order-id is required")

    po_t = Table("purchase_order")
    q = Q.from_(po_t).select(po_t.star).where(po_t.id == P())
    po = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchone()
    if not po:
        err(f"Purchase order {args.purchase_order_id} not found")

    data = row_to_dict(po)

    # Items with received/invoiced status
    poi = Table("purchase_order_item").as_("poi")
    i_t = Table("item").as_("i")
    q = (Q.from_(poi)
         .left_join(i_t).on(i_t.id == poi.item_id)
         .select(poi.star, i_t.item_code, i_t.item_name)
         .where(poi.purchase_order_id == P())
         .orderby(poi.rowid))
    items = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    # Linked receipts
    pr_t = Table("purchase_receipt")
    q = (Q.from_(pr_t)
         .select(pr_t.id, pr_t.naming_series, pr_t.status, pr_t.posting_date)
         .where(pr_t.purchase_order_id == P()))
    receipts = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchall()
    data["purchase_receipts"] = [row_to_dict(r) for r in receipts]

    # Linked invoices
    pi_t = Table("purchase_invoice")
    q = (Q.from_(pi_t)
         .select(pi_t.id, pi_t.naming_series, pi_t.status, pi_t.posting_date,
                 pi_t.grand_total, pi_t.outstanding_amount)
         .where(pi_t.purchase_order_id == P()))
    invoices = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchall()
    data["purchase_invoices"] = [row_to_dict(r) for r in invoices]

    ok(data)


# ---------------------------------------------------------------------------
# 17. list-purchase-orders
# ---------------------------------------------------------------------------

def list_purchase_orders(conn, args):
    """List purchase orders."""
    po = Table("purchase_order").as_("po")
    s = Table("supplier").as_("s")
    params = []

    count_q = Q.from_(po).select(fn.Count("*"))
    data_q = (Q.from_(po)
              .left_join(s).on(s.id == po.supplier_id)
              .select(po.star, s.name.as_("supplier_name")))

    if args.company_id:
        count_q = count_q.where(po.company_id == P())
        data_q = data_q.where(po.company_id == P())
        params.append(args.company_id)
    if args.supplier_id:
        count_q = count_q.where(po.supplier_id == P())
        data_q = data_q.where(po.supplier_id == P())
        params.append(args.supplier_id)
    if args.po_status:
        count_q = count_q.where(po.status == P())
        data_q = data_q.where(po.status == P())
        params.append(args.po_status)
    if args.from_date:
        count_q = count_q.where(po.order_date >= P())
        data_q = data_q.where(po.order_date >= P())
        params.append(args.from_date)
    if args.to_date:
        count_q = count_q.where(po.order_date <= P())
        data_q = data_q.where(po.order_date <= P())
        params.append(args.to_date)

    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    data_params = params + [limit, offset]

    data_q = (data_q
              .orderby(po.order_date, order=Order.desc)
              .orderby(po.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(data_q.get_sql(), data_params).fetchall()

    ok({"purchase_orders": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 18. submit-purchase-order
# ---------------------------------------------------------------------------

def submit_purchase_order(conn, args):
    """Submit/confirm a purchase order."""
    if not args.purchase_order_id:
        err("--purchase-order-id is required")

    po_t = Table("purchase_order")
    q = Q.from_(po_t).select(po_t.star).where(po_t.id == P())
    po = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchone()
    if not po:
        err(f"Purchase order {args.purchase_order_id} not found")
    if po["status"] != "draft":
        err(f"Cannot submit: PO is '{po['status']}' (must be 'draft')")

    naming = get_next_name(conn, "purchase_order", company_id=po["company_id"])

    q = (Q.update(po_t)
         .set(po_t.status, ValueWrapper("confirmed"))
         .set(po_t.naming_series, P())
         .set(po_t.updated_at, LiteralValue("datetime('now')"))
         .where(po_t.id == P()))
    conn.execute(q.get_sql(), (naming, args.purchase_order_id))

    audit(conn, "erpclaw-buying", "submit-purchase-order", "purchase_order",
           args.purchase_order_id,
           new_values={"naming_series": naming})
    conn.commit()
    ok({"purchase_order_id": args.purchase_order_id,
         "naming_series": naming, "status": "confirmed"})


# ---------------------------------------------------------------------------
# 19. cancel-purchase-order
# ---------------------------------------------------------------------------

def cancel_purchase_order(conn, args):
    """Cancel a PO. Only if no linked receipts or invoices."""
    if not args.purchase_order_id:
        err("--purchase-order-id is required")

    po_t = Table("purchase_order")
    q = Q.from_(po_t).select(po_t.star).where(po_t.id == P())
    po = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchone()
    if not po:
        err(f"Purchase order {args.purchase_order_id} not found")
    if po["status"] == "cancelled":
        err("Purchase order is already cancelled")

    # Check for linked receipts
    pr_t = Table("purchase_receipt")
    q = (Q.from_(pr_t)
         .select(fn.Count("*").as_("cnt"))
         .where(pr_t.purchase_order_id == P())
         .where(pr_t.status != P()))
    receipts = conn.execute(q.get_sql(),
        (args.purchase_order_id, "cancelled")).fetchone()
    if receipts["cnt"] > 0:
        err("Cannot cancel: PO has linked purchase receipts")

    # Check for linked invoices
    pi_t = Table("purchase_invoice")
    q = (Q.from_(pi_t)
         .select(fn.Count("*").as_("cnt"))
         .where(pi_t.purchase_order_id == P())
         .where(pi_t.status != P()))
    invoices = conn.execute(q.get_sql(),
        (args.purchase_order_id, "cancelled")).fetchone()
    if invoices["cnt"] > 0:
        err("Cannot cancel: PO has linked purchase invoices")

    q = (Q.update(po_t)
         .set(po_t.status, ValueWrapper("cancelled"))
         .set(po_t.updated_at, LiteralValue("datetime('now')"))
         .where(po_t.id == P()))
    conn.execute(q.get_sql(), (args.purchase_order_id,))

    audit(conn, "erpclaw-buying", "cancel-purchase-order", "purchase_order",
           args.purchase_order_id)
    conn.commit()
    ok({"purchase_order_id": args.purchase_order_id, "status": "cancelled"})


# ---------------------------------------------------------------------------
# 20. create-purchase-receipt
# ---------------------------------------------------------------------------

def create_purchase_receipt(conn, args):
    """Create a purchase receipt (GRN) from a PO."""
    if not args.purchase_order_id:
        err("--purchase-order-id is required")

    po_t = Table("purchase_order")
    q = Q.from_(po_t).select(po_t.star).where(po_t.id == P())
    po = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchone()
    if not po:
        err(f"Purchase order {args.purchase_order_id} not found")
    if po["status"] not in ("confirmed", "partially_received"):
        err(f"Cannot create receipt: PO status is '{po['status']}' "
             f"(must be 'confirmed' or 'partially_received')")

    posting_date = args.posting_date or _today()
    pr_id = str(uuid.uuid4())

    # Determine items: partial (from --items) or full (all PO items)
    items_arg = _parse_json_arg(args.items, "items") if args.items else None

    poi_t = Table("purchase_order_item")
    q = (Q.from_(poi_t).select(poi_t.star)
         .where(poi_t.purchase_order_id == P())
         .orderby(poi_t.rowid))
    po_items = conn.execute(q.get_sql(), (args.purchase_order_id,)).fetchall()

    total_qty = Decimal("0")
    receipt_items = []

    if items_arg:
        # Partial receipt
        for i, item in enumerate(items_arg):
            po_item_id = item.get("purchase_order_item_id")
            if not po_item_id:
                err(f"Item {i}: purchase_order_item_id is required for partial receipt")
            poi_lookup_q = Q.from_(poi_t).select(poi_t.star).where(poi_t.id == P())
            poi = conn.execute(poi_lookup_q.get_sql(), (po_item_id,)).fetchone()
            if not poi:
                err(f"Item {i}: PO item {po_item_id} not found")

            qty = to_decimal(item.get("qty", "0"))
            if qty <= 0:
                err(f"Item {i}: qty must be > 0")

            # Check remaining receivable qty
            ordered = to_decimal(poi["quantity"])
            received = to_decimal(poi["received_qty"])
            remaining = ordered - received
            if qty > remaining:
                err(f"Item {i}: qty {qty} exceeds remaining receivable {remaining}")

            rate = to_decimal(poi["rate"])
            amount = round_currency(qty * rate)
            total_qty += qty

            receipt_items.append((
                str(uuid.uuid4()), pr_id, poi["item_id"],
                str(round_currency(qty)), poi["uom"], po_item_id,
                item.get("warehouse_id") or poi["warehouse_id"],
                item.get("batch_id"), item.get("serial_numbers"),
                str(round_currency(rate)), str(amount),
            ))
    else:
        # Full receipt: copy all unreceived PO items
        for poi_row in po_items:
            poi = row_to_dict(poi_row)
            ordered = to_decimal(poi["quantity"])
            received = to_decimal(poi["received_qty"])
            remaining = ordered - received
            if remaining <= 0:
                continue

            rate = to_decimal(poi["rate"])
            amount = round_currency(remaining * rate)
            total_qty += remaining

            receipt_items.append((
                str(uuid.uuid4()), pr_id, poi["item_id"],
                str(round_currency(remaining)), poi["uom"], poi["id"],
                poi["warehouse_id"], None, None,
                str(round_currency(rate)), str(amount),
            ))

    if not receipt_items:
        err("No items to receive (all PO items already fully received)")

    # Insert parent first
    pr_t = Table("purchase_receipt")
    q = (Q.into(pr_t)
         .columns("id", "supplier_id", "posting_date", "purchase_order_id",
                  "status", "total_qty", "company_id")
         .insert(P(), P(), P(), P(), ValueWrapper("draft"), P(), P()))
    conn.execute(q.get_sql(),
        (pr_id, po["supplier_id"], posting_date, args.purchase_order_id,
         str(round_currency(total_qty)), po["company_id"]))

    # Insert items
    pri_t = Table("purchase_receipt_item")
    pri_q = (Q.into(pri_t)
             .columns("id", "purchase_receipt_id", "item_id", "quantity",
                      "uom", "purchase_order_item_id", "warehouse_id",
                      "batch_id", "serial_numbers", "rate", "amount")
             .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    pri_sql = pri_q.get_sql()
    for row_params in receipt_items:
        conn.execute(pri_sql, row_params)

    audit(conn, "erpclaw-buying", "create-purchase-receipt", "purchase_receipt", pr_id,
           new_values={"purchase_order_id": args.purchase_order_id,
                       "item_count": len(receipt_items)})
    conn.commit()
    ok({"purchase_receipt_id": pr_id, "total_qty": str(round_currency(total_qty)),
         "item_count": len(receipt_items)})


# ---------------------------------------------------------------------------
# 21. get-purchase-receipt
# ---------------------------------------------------------------------------

def get_purchase_receipt(conn, args):
    """Get a purchase receipt with items."""
    if not args.purchase_receipt_id:
        err("--purchase-receipt-id is required")

    pr_t = Table("purchase_receipt")
    q = Q.from_(pr_t).select(pr_t.star).where(pr_t.id == P())
    pr = conn.execute(q.get_sql(), (args.purchase_receipt_id,)).fetchone()
    if not pr:
        err(f"Purchase receipt {args.purchase_receipt_id} not found")

    data = row_to_dict(pr)

    pri = Table("purchase_receipt_item").as_("pri")
    i_t = Table("item").as_("i")
    q = (Q.from_(pri)
         .left_join(i_t).on(i_t.id == pri.item_id)
         .select(pri.star, i_t.item_code, i_t.item_name)
         .where(pri.purchase_receipt_id == P())
         .orderby(pri.rowid))
    items = conn.execute(q.get_sql(), (args.purchase_receipt_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    ok(data)


# ---------------------------------------------------------------------------
# 22. list-purchase-receipts
# ---------------------------------------------------------------------------

def list_purchase_receipts(conn, args):
    """List purchase receipts."""
    pr = Table("purchase_receipt").as_("pr")
    s = Table("supplier").as_("s")
    params = []

    count_q = Q.from_(pr).select(fn.Count("*"))
    data_q = (Q.from_(pr)
              .left_join(s).on(s.id == pr.supplier_id)
              .select(pr.star, s.name.as_("supplier_name")))

    if args.company_id:
        count_q = count_q.where(pr.company_id == P())
        data_q = data_q.where(pr.company_id == P())
        params.append(args.company_id)
    if args.supplier_id:
        count_q = count_q.where(pr.supplier_id == P())
        data_q = data_q.where(pr.supplier_id == P())
        params.append(args.supplier_id)
    if args.pr_status:
        count_q = count_q.where(pr.status == P())
        data_q = data_q.where(pr.status == P())
        params.append(args.pr_status)

    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    data_params = params + [limit, offset]

    data_q = (data_q
              .orderby(pr.posting_date, order=Order.desc)
              .orderby(pr.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(data_q.get_sql(), data_params).fetchall()

    ok({"purchase_receipts": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 23. submit-purchase-receipt
# ---------------------------------------------------------------------------

def submit_purchase_receipt(conn, args):
    """Submit a GRN: create SLE + perpetual inventory GL."""
    if not args.purchase_receipt_id:
        err("--purchase-receipt-id is required")

    pr_t = Table("purchase_receipt")
    q = Q.from_(pr_t).select(pr_t.star).where(pr_t.id == P())
    pr = conn.execute(q.get_sql(), (args.purchase_receipt_id,)).fetchone()
    if not pr:
        err(f"Purchase receipt {args.purchase_receipt_id} not found")
    if pr["status"] != "draft":
        err(f"Cannot submit: receipt is '{pr['status']}' (must be 'draft')")

    pr_dict = row_to_dict(pr)
    company_id = pr_dict["company_id"]
    posting_date = pr_dict["posting_date"]

    # Verify linked PO is confirmed (if exists)
    if pr_dict.get("purchase_order_id"):
        po_t = Table("purchase_order")
        q = Q.from_(po_t).select(po_t.status).where(po_t.id == P())
        po = conn.execute(q.get_sql(),
                          (pr_dict["purchase_order_id"],)).fetchone()
        if po and po["status"] not in ("confirmed", "partially_received",
                                        "partially_invoiced"):
            err(f"Linked PO status is '{po['status']}' -- must be confirmed")

    pri_t = Table("purchase_receipt_item")
    q = (Q.from_(pri_t).select(pri_t.star)
         .where(pri_t.purchase_receipt_id == P())
         .orderby(pri_t.rowid))
    items = conn.execute(q.get_sql(), (args.purchase_receipt_id,)).fetchall()
    if not items:
        err("Purchase receipt has no items")

    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, company_id)
    naming = get_next_name(conn, "purchase_receipt", company_id=company_id)

    # Build SLE entries (positive qty into warehouse)
    sle_entries = []
    for item_row in items:
        item = row_to_dict(item_row)
        qty = to_decimal(item["quantity"])
        rate = to_decimal(item["rate"])
        warehouse_id = item.get("warehouse_id")
        if not warehouse_id:
            # Fallback to company default warehouse
            company_t = Table("company")
            co_q = Q.from_(company_t).select(company_t.default_warehouse_id).where(company_t.id == P())
            co = conn.execute(co_q.get_sql(), (company_id,)).fetchone()
            warehouse_id = co["default_warehouse_id"] if co else None
        if not warehouse_id:
            err(f"No warehouse specified for item {item['item_id']} and no company default")

        sle_entries.append({
            "item_id": item["item_id"],
            "warehouse_id": warehouse_id,
            "actual_qty": str(round_currency(qty)),
            "incoming_rate": str(round_currency(rate)),
            "batch_id": item.get("batch_id"),
            "serial_number": item.get("serial_numbers"),
            "fiscal_year": fiscal_year,
        })

    # Insert SLE
    try:
        sle_ids = insert_sle_entries(
            conn, sle_entries,
            voucher_type="purchase_receipt",
            voucher_id=args.purchase_receipt_id,
            posting_date=posting_date,
            company_id=company_id,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-buying] {e}\n")
        err(f"SLE posting failed: {e}")

    # Build perpetual inventory GL: DR Stock In Hand / CR Stock Received Not Billed
    sle_t = Table("stock_ledger_entry")
    q = (Q.from_(sle_t).select(sle_t.star)
         .where(sle_t.voucher_type == ValueWrapper("purchase_receipt"))
         .where(sle_t.voucher_id == P())
         .where(sle_t.is_cancelled == 0))
    sle_rows = conn.execute(q.get_sql(), (args.purchase_receipt_id,)).fetchall()
    sle_dicts = [row_to_dict(r) for r in sle_rows]

    gl_entries = create_perpetual_inventory_gl(
        conn, sle_dicts,
        voucher_type="purchase_receipt",
        voucher_id=args.purchase_receipt_id,
        posting_date=posting_date,
        company_id=company_id,
        cost_center_id=cost_center_id,
    )

    gl_ids = []
    if gl_entries:
        for gle in gl_entries:
            gle["fiscal_year"] = fiscal_year
        try:
            gl_ids = insert_gl_entries(
                conn, gl_entries,
                voucher_type="purchase_receipt",
                voucher_id=args.purchase_receipt_id,
                posting_date=posting_date,
                company_id=company_id,
                remarks=f"Purchase Receipt {naming}",
            )
        except ValueError as e:
            sys.stderr.write(f"[erpclaw-buying] {e}\n")
            err(f"GL posting failed: {e}")

    # Update PO received_qty
    for item_row in items:
        item = row_to_dict(item_row)
        if item.get("purchase_order_item_id"):
            # raw SQL — CAST arithmetic expression not expressible in PyPika
            conn.execute(
                """UPDATE purchase_order_item
                   SET received_qty = CAST(
                       received_qty + 0 + ? AS TEXT)
                   WHERE id = ?""",
                (item["quantity"], item["purchase_order_item_id"]),
            )

    # Update PO status
    if pr_dict.get("purchase_order_id"):
        _update_po_receipt_status(conn, pr_dict["purchase_order_id"])

    # Update receipt status
    q = (Q.update(pr_t)
         .set(pr_t.status, ValueWrapper("submitted"))
         .set(pr_t.naming_series, P())
         .set(pr_t.updated_at, LiteralValue("datetime('now')"))
         .where(pr_t.id == P()))
    conn.execute(q.get_sql(), (naming, args.purchase_receipt_id))

    audit(conn, "erpclaw-buying", "submit-purchase-receipt", "purchase_receipt",
           args.purchase_receipt_id,
           new_values={"naming_series": naming,
                       "sle_count": len(sle_ids), "gl_count": len(gl_ids)})
    conn.commit()
    ok({"purchase_receipt_id": args.purchase_receipt_id,
         "naming_series": naming, "status": "submitted",
         "sle_entries_created": len(sle_ids),
         "gl_entries_created": len(gl_ids)})


def _update_po_receipt_status(conn, purchase_order_id):
    """Update PO per_received and status based on received quantities."""
    poi_t = Table("purchase_order_item")
    q = (Q.from_(poi_t)
         .select(poi_t.quantity, poi_t.received_qty)
         .where(poi_t.purchase_order_id == P()))
    po_items = conn.execute(q.get_sql(), (purchase_order_id,)).fetchall()

    total_ordered = Decimal("0")
    total_received = Decimal("0")
    for poi in po_items:
        total_ordered += to_decimal(poi["quantity"])
        total_received += to_decimal(poi["received_qty"])

    if total_ordered > 0:
        per_received = round_currency(total_received / total_ordered * Decimal("100"))
    else:
        per_received = Decimal("0")

    if per_received >= Decimal("100"):
        new_status = "fully_received"
    elif per_received > Decimal("0"):
        new_status = "partially_received"
    else:
        return  # No change

    po_t = Table("purchase_order")
    q = (Q.update(po_t)
         .set(po_t.per_received, P())
         .set(po_t.status, P())
         .set(po_t.updated_at, LiteralValue("datetime('now')"))
         .where(po_t.id == P()))
    conn.execute(q.get_sql(), (str(per_received), new_status, purchase_order_id))


# ---------------------------------------------------------------------------
# 24. cancel-purchase-receipt
# ---------------------------------------------------------------------------

def cancel_purchase_receipt(conn, args):
    """Cancel a submitted GRN: reverse SLE + GL."""
    if not args.purchase_receipt_id:
        err("--purchase-receipt-id is required")

    pr_t = Table("purchase_receipt")
    q = Q.from_(pr_t).select(pr_t.star).where(pr_t.id == P())
    pr = conn.execute(q.get_sql(), (args.purchase_receipt_id,)).fetchone()
    if not pr:
        err(f"Purchase receipt {args.purchase_receipt_id} not found")
    if pr["status"] != "submitted":
        err(f"Cannot cancel: receipt is '{pr['status']}' (must be 'submitted')")

    pr_dict = row_to_dict(pr)
    posting_date = pr_dict["posting_date"]

    # Reverse SLE
    try:
        reversal_sle_ids = reverse_sle_entries(
            conn,
            voucher_type="purchase_receipt",
            voucher_id=args.purchase_receipt_id,
            posting_date=posting_date,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-buying] {e}\n")
        err(f"SLE reversal failed: {e}")

    # Reverse GL
    try:
        reversal_gl_ids = reverse_gl_entries(
            conn,
            voucher_type="purchase_receipt",
            voucher_id=args.purchase_receipt_id,
            posting_date=posting_date,
        )
    except ValueError:
        reversal_gl_ids = []

    # Reverse PO received_qty
    pri_t = Table("purchase_receipt_item")
    q = Q.from_(pri_t).select(pri_t.star).where(pri_t.purchase_receipt_id == P())
    items = conn.execute(q.get_sql(), (args.purchase_receipt_id,)).fetchall()
    for item_row in items:
        item = row_to_dict(item_row)
        if item.get("purchase_order_item_id"):
            # raw SQL — CAST+MAX arithmetic expression not expressible in PyPika
            conn.execute(
                """UPDATE purchase_order_item
                   SET received_qty = CAST(
                       MAX(0, received_qty + 0 - ?) AS TEXT)
                   WHERE id = ?""",
                (item["quantity"], item["purchase_order_item_id"]),
            )

    # Update PO status back
    if pr_dict.get("purchase_order_id"):
        _update_po_receipt_status(conn, pr_dict["purchase_order_id"])
        # If all received is now 0, set back to confirmed
        poi_t = Table("purchase_order_item")
        q = (Q.from_(poi_t).select(poi_t.received_qty)
             .where(poi_t.purchase_order_id == P()))
        po_items = conn.execute(q.get_sql(),
            (pr_dict["purchase_order_id"],)).fetchall()
        all_zero = all(to_decimal(p["received_qty"]) <= 0 for p in po_items)
        if all_zero:
            po_t = Table("purchase_order")
            q = (Q.update(po_t)
                 .set(po_t.status, ValueWrapper("confirmed"))
                 .set(po_t.per_received, ValueWrapper("0"))
                 .set(po_t.updated_at, LiteralValue("datetime('now')"))
                 .where(po_t.id == P()))
            conn.execute(q.get_sql(), (pr_dict["purchase_order_id"],))

    q = (Q.update(pr_t)
         .set(pr_t.status, ValueWrapper("cancelled"))
         .set(pr_t.updated_at, LiteralValue("datetime('now')"))
         .where(pr_t.id == P()))
    conn.execute(q.get_sql(), (args.purchase_receipt_id,))

    audit(conn, "erpclaw-buying", "cancel-purchase-receipt", "purchase_receipt",
           args.purchase_receipt_id,
           new_values={"reversed": True})
    conn.commit()
    ok({"purchase_receipt_id": args.purchase_receipt_id,
         "status": "cancelled",
         "sle_reversals": len(reversal_sle_ids),
         "gl_reversals": len(reversal_gl_ids)})


# ---------------------------------------------------------------------------
# 25. create-purchase-invoice
# ---------------------------------------------------------------------------

def create_purchase_invoice(conn, args):
    """Create a purchase invoice (from PO, GRN, or standalone)."""
    company_id = args.company_id
    supplier_id = args.supplier_id
    items_arg = _parse_json_arg(args.items, "items") if args.items else None
    posting_date = args.posting_date or _today()
    due_date = args.due_date
    tax_template_id = args.tax_template_id
    po_id = args.purchase_order_id
    pr_id_arg = args.purchase_receipt_id
    update_stock = 1  # Default for US perpetual inventory

    pi_id = str(uuid.uuid4())
    pi_items = []
    total_amount = Decimal("0")

    po_t = Table("purchase_order")
    poi_t = Table("purchase_order_item")
    pr_t_lookup = Table("purchase_receipt")

    if po_id:
        # Create from Purchase Order
        q = Q.from_(po_t).select(po_t.star).where(po_t.id == P())
        po = conn.execute(q.get_sql(), (po_id,)).fetchone()
        if not po:
            err(f"Purchase order {po_id} not found")
        supplier_id = po["supplier_id"]
        company_id = po["company_id"]
        tax_template_id = tax_template_id or po["tax_template_id"]

        # If PO has receipts, set update_stock=0 (stock already moved)
        q = (Q.from_(pr_t_lookup)
             .select(pr_t_lookup.id)
             .where(pr_t_lookup.purchase_order_id == P())
             .where(pr_t_lookup.status == ValueWrapper("submitted"))
             .limit(1))
        receipt_row = conn.execute(q.get_sql(), (po_id,)).fetchone()
        if receipt_row:
            update_stock = 0
            if not pr_id_arg:
                pr_id_arg = receipt_row["id"]

        q = Q.from_(poi_t).select(poi_t.star).where(poi_t.purchase_order_id == P())
        po_items = conn.execute(q.get_sql(), (po_id,)).fetchall()
        for poi_row in po_items:
            poi = row_to_dict(poi_row)
            qty = to_decimal(poi["quantity"])
            invoiced = to_decimal(poi["invoiced_qty"])
            remaining = qty - invoiced
            if remaining <= 0:
                continue
            rate = to_decimal(poi["rate"])
            amount = round_currency(remaining * rate)
            total_amount += amount
            pi_items.append((
                str(uuid.uuid4()), pi_id, poi["item_id"],
                str(round_currency(remaining)), poi["uom"],
                str(round_currency(rate)), str(amount),
                None, None, None, poi["id"], None,
            ))

    elif pr_id_arg:
        # Create from Purchase Receipt
        q = Q.from_(pr_t_lookup).select(pr_t_lookup.star).where(pr_t_lookup.id == P())
        pr = conn.execute(q.get_sql(), (pr_id_arg,)).fetchone()
        if not pr:
            err(f"Purchase receipt {pr_id_arg} not found")
        supplier_id = pr["supplier_id"]
        company_id = pr["company_id"]
        update_stock = 0  # Stock already moved via GRN

        pri_t_lookup = Table("purchase_receipt_item")
        q = Q.from_(pri_t_lookup).select(pri_t_lookup.star).where(pri_t_lookup.purchase_receipt_id == P())
        pr_items = conn.execute(q.get_sql(), (pr_id_arg,)).fetchall()
        for pri_row in pr_items:
            pri = row_to_dict(pri_row)
            qty = to_decimal(pri["quantity"])
            rate = to_decimal(pri["rate"])
            amount = round_currency(qty * rate)
            total_amount += amount
            pi_items.append((
                str(uuid.uuid4()), pi_id, pri["item_id"],
                str(round_currency(qty)), pri.get("uom"),
                str(round_currency(rate)), str(amount),
                None, None, None,
                pri.get("purchase_order_item_id"), pri["id"],
            ))

    else:
        # Standalone invoice
        if not supplier_id:
            err("--supplier-id is required for standalone invoice")
        if not company_id:
            err("--company-id is required for standalone invoice")
        if not items_arg:
            err("--items is required for standalone invoice")

        for i, item in enumerate(items_arg):
            item_id = item.get("item_id")
            if not item_id:
                err(f"Item {i}: item_id is required")
            qty = to_decimal(item.get("qty", "0"))
            if qty <= 0:
                err(f"Item {i}: qty must be > 0")
            rate = to_decimal(item.get("rate", "0"))
            if rate <= 0:
                err(f"Item {i}: rate must be > 0")
            amount = round_currency(qty * rate)
            total_amount += amount
            pi_items.append((
                str(uuid.uuid4()), pi_id, item_id,
                str(round_currency(qty)), item.get("uom"),
                str(round_currency(rate)), str(amount),
                item.get("expense_account_id"), item.get("cost_center_id"),
                item.get("project_id"), None, None,
            ))

    if not pi_items:
        err("No items for invoice")

    # Validate supplier
    sup_t = Table("supplier")
    q = Q.from_(sup_t).select(sup_t.star).where(sup_t.id == P())
    supplier = conn.execute(q.get_sql(), (supplier_id,)).fetchone()
    if not supplier:
        err(f"Supplier {supplier_id} not found")

    # Calculate tax
    tax_amount, tax_details = _calculate_tax(conn, tax_template_id, total_amount)
    grand_total = round_currency(total_amount + tax_amount)

    # Insert parent first
    pi_t = Table("purchase_invoice")
    q = (Q.into(pi_t)
         .columns("id", "supplier_id", "posting_date", "due_date",
                  "total_amount", "tax_amount", "grand_total",
                  "outstanding_amount", "tax_template_id", "status",
                  "purchase_order_id", "purchase_receipt_id",
                  "update_stock", "company_id")
         .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(),
                 ValueWrapper("draft"), P(), P(), P(), P()))
    conn.execute(q.get_sql(),
        (pi_id, supplier_id, posting_date, due_date,
         str(round_currency(total_amount)), str(round_currency(tax_amount)),
         str(grand_total), str(grand_total),
         tax_template_id, po_id, pr_id_arg, update_stock, company_id))

    # Insert items
    pii_t = Table("purchase_invoice_item")
    pii_q = (Q.into(pii_t)
             .columns("id", "purchase_invoice_id", "item_id", "quantity",
                      "uom", "rate", "amount", "expense_account_id",
                      "cost_center_id", "project_id",
                      "purchase_order_item_id", "purchase_receipt_item_id")
             .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    pii_sql = pii_q.get_sql()
    for row_params in pi_items:
        conn.execute(pii_sql, row_params)

    audit(conn, "erpclaw-buying", "create-purchase-invoice", "purchase_invoice", pi_id,
           new_values={"supplier_id": supplier_id,
                       "grand_total": str(grand_total),
                       "update_stock": update_stock})
    conn.commit()
    ok({"purchase_invoice_id": pi_id,
         "total_amount": str(round_currency(total_amount)),
         "tax_amount": str(round_currency(tax_amount)),
         "grand_total": str(grand_total),
         "update_stock": update_stock})


# ---------------------------------------------------------------------------
# 26. update-purchase-invoice
# ---------------------------------------------------------------------------

def update_purchase_invoice(conn, args):
    """Update a draft purchase invoice."""
    if not args.purchase_invoice_id:
        err("--purchase-invoice-id is required")

    pi_t = Table("purchase_invoice")
    q = Q.from_(pi_t).select(pi_t.star).where(pi_t.id == P())
    pi = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchone()
    if not pi:
        err(f"Purchase invoice {args.purchase_invoice_id} not found")
    if pi["status"] != "draft":
        err(f"Cannot update: invoice is '{pi['status']}' (must be 'draft')",
             suggestion="Cancel the document first, then make changes.")

    updated_fields = []

    if args.due_date is not None:
        q = (Q.update(pi_t)
             .set(pi_t.due_date, P())
             .where(pi_t.id == P()))
        conn.execute(q.get_sql(), (args.due_date, args.purchase_invoice_id))
        updated_fields.append("due_date")

    if args.items:
        items = _parse_json_arg(args.items, "items")
        if not items or not isinstance(items, list):
            err("--items must be a non-empty JSON array")

        pii_t = Table("purchase_invoice_item")
        q = Q.from_(pii_t).delete().where(pii_t.purchase_invoice_id == P())
        conn.execute(q.get_sql(), (args.purchase_invoice_id,))

        total_amount = Decimal("0")
        for i, item in enumerate(items):
            item_id = item.get("item_id")
            if not item_id:
                err(f"Item {i}: item_id is required")
            qty = to_decimal(item.get("qty", "0"))
            if qty <= 0:
                err(f"Item {i}: qty must be > 0")
            rate = to_decimal(item.get("rate", "0"))
            if rate <= 0:
                err(f"Item {i}: rate must be > 0")
            amount = round_currency(qty * rate)
            total_amount += amount

            conn.execute(
                """INSERT INTO purchase_invoice_item
                   (id, purchase_invoice_id, item_id, quantity, uom, rate,
                    amount, expense_account_id, cost_center_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), args.purchase_invoice_id, item_id,
                 str(round_currency(qty)), item.get("uom"),
                 str(round_currency(rate)), str(amount),
                 item.get("expense_account_id"), item.get("cost_center_id")),
            )

        tax_amount, _ = _calculate_tax(conn, pi["tax_template_id"], total_amount)
        grand_total = round_currency(total_amount + tax_amount)

        q = (Q.update(pi_t)
             .set(pi_t.total_amount, P())
             .set(pi_t.tax_amount, P())
             .set(pi_t.grand_total, P())
             .set(pi_t.outstanding_amount, P())
             .set(pi_t.updated_at, LiteralValue("datetime('now')"))
             .where(pi_t.id == P()))
        conn.execute(q.get_sql(),
            (str(round_currency(total_amount)), str(round_currency(tax_amount)),
             str(grand_total), str(grand_total), args.purchase_invoice_id))
        updated_fields.append("items")

    if not updated_fields:
        err("No fields to update")

    q = (Q.update(pi_t)
         .set(pi_t.updated_at, LiteralValue("datetime('now')"))
         .where(pi_t.id == P()))
    conn.execute(q.get_sql(), (args.purchase_invoice_id,))

    audit(conn, "erpclaw-buying", "update-purchase-invoice", "purchase_invoice",
           args.purchase_invoice_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"purchase_invoice_id": args.purchase_invoice_id,
         "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 27. get-purchase-invoice
# ---------------------------------------------------------------------------

def get_purchase_invoice(conn, args):
    """Get purchase invoice with items and payment info."""
    if not args.purchase_invoice_id:
        err("--purchase-invoice-id is required")

    pi_t = Table("purchase_invoice")
    q = Q.from_(pi_t).select(pi_t.star).where(pi_t.id == P())
    pi = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchone()
    if not pi:
        err(f"Purchase invoice {args.purchase_invoice_id} not found")

    data = row_to_dict(pi)

    pii = Table("purchase_invoice_item").as_("pii")
    i_t = Table("item").as_("i")
    q = (Q.from_(pii)
         .left_join(i_t).on(i_t.id == pii.item_id)
         .select(pii.star, i_t.item_code, i_t.item_name)
         .where(pii.purchase_invoice_id == P())
         .orderby(pii.rowid))
    items = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    # Payment ledger entries
    ple_t = Table("payment_ledger_entry")
    q = (Q.from_(ple_t).select(ple_t.star)
         .where(ple_t.against_voucher_type == ValueWrapper("purchase_invoice"))
         .where(ple_t.against_voucher_id == P()))
    ple_rows = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchall()
    data["payments"] = [row_to_dict(r) for r in ple_rows]

    ok(data)


# ---------------------------------------------------------------------------
# 28. list-purchase-invoices
# ---------------------------------------------------------------------------

def list_purchase_invoices(conn, args):
    """List purchase invoices."""
    pi = Table("purchase_invoice").as_("pi")
    s = Table("supplier").as_("s")
    params = []

    count_q = Q.from_(pi).select(fn.Count("*"))
    data_q = (Q.from_(pi)
              .left_join(s).on(s.id == pi.supplier_id)
              .select(pi.star, s.name.as_("supplier_name")))

    if args.company_id:
        count_q = count_q.where(pi.company_id == P())
        data_q = data_q.where(pi.company_id == P())
        params.append(args.company_id)
    if args.supplier_id:
        count_q = count_q.where(pi.supplier_id == P())
        data_q = data_q.where(pi.supplier_id == P())
        params.append(args.supplier_id)
    if args.pi_status:
        count_q = count_q.where(pi.status == P())
        data_q = data_q.where(pi.status == P())
        params.append(args.pi_status)
    if args.from_date:
        count_q = count_q.where(pi.posting_date >= P())
        data_q = data_q.where(pi.posting_date >= P())
        params.append(args.from_date)
    if args.to_date:
        count_q = count_q.where(pi.posting_date <= P())
        data_q = data_q.where(pi.posting_date <= P())
        params.append(args.to_date)

    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    data_params = params + [limit, offset]

    data_q = (data_q
              .orderby(pi.posting_date, order=Order.desc)
              .orderby(pi.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(data_q.get_sql(), data_params).fetchall()

    ok({"purchase_invoices": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 29. submit-purchase-invoice
# ---------------------------------------------------------------------------

def submit_purchase_invoice(conn, args):
    """Submit purchase invoice: expense GL + AP + tax GL + PLE.
    If update_stock=1, also creates SLE + inventory GL."""
    if not args.purchase_invoice_id:
        err("--purchase-invoice-id is required")

    pi_t = Table("purchase_invoice")
    q = Q.from_(pi_t).select(pi_t.star).where(pi_t.id == P())
    pi = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchone()
    if not pi:
        err(f"Purchase invoice {args.purchase_invoice_id} not found")
    if pi["status"] != "draft":
        err(f"Cannot submit: invoice is '{pi['status']}' (must be 'draft')")

    pi_dict = row_to_dict(pi)
    company_id = pi_dict["company_id"]
    posting_date = pi_dict["posting_date"]
    supplier_id = pi_dict["supplier_id"]
    update_stock = pi_dict.get("update_stock", 1)
    is_return = bool(pi_dict.get("is_return", 0))
    voucher_type = "debit_note" if is_return else "purchase_invoice"

    # Verify supplier
    sup_t = Table("supplier")
    q = Q.from_(sup_t).select(sup_t.star).where(sup_t.id == P())
    supplier = conn.execute(q.get_sql(), (supplier_id,)).fetchone()
    if not supplier:
        err(f"Supplier {supplier_id} not found")

    pii_t = Table("purchase_invoice_item")
    q = Q.from_(pii_t).select(pii_t.star).where(pii_t.purchase_invoice_id == P())
    items = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchall()
    if not items:
        err("Purchase invoice has no items")

    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, company_id)
    naming = get_next_name(conn, "purchase_invoice", company_id=company_id)

    total_amount = to_decimal(pi_dict["total_amount"])
    tax_amount = to_decimal(pi_dict["tax_amount"])
    grand_total = to_decimal(pi_dict["grand_total"])

    # --- Build GL entries ---
    gl_entries = []

    company_t = Table("company")
    q = Q.from_(company_t).select(company_t.star).where(company_t.id == P())
    company_row = conn.execute(q.get_sql(), (company_id,)).fetchone()
    default_expense_acct = company_row["default_expense_account_id"] if company_row else None

    # Check if this invoice has a linked purchase receipt.
    # If so, the receipt already posted DR Inventory / CR SRNB.
    # The invoice should then DR SRNB / CR Payable (clearing the accrual)
    # rather than DR Expense / CR Payable (which double-counts COGS).
    has_receipt = bool(pi_dict.get("purchase_receipt_id"))
    srnb_acct = None
    acct_t = Table("account")
    if has_receipt:
        q = (Q.from_(acct_t).select(acct_t.id)
             .where(acct_t.account_type == ValueWrapper("stock_received_not_billed"))
             .where(acct_t.company_id == P())
             .where(acct_t.is_group == 0)
             .limit(1))
        srnb_row = conn.execute(q.get_sql(), (company_id,)).fetchone()
        srnb_acct = srnb_row["id"] if srnb_row else None

    # 1. DR: SRNB (if receipt-linked) or Expense accounts (per item or default)
    for item_row in items:
        item = row_to_dict(item_row)
        amount = abs(to_decimal(item["amount"]))
        if amount <= 0:
            continue
        # Use SRNB when clearing a receipt accrual; expense otherwise
        if has_receipt and srnb_acct:
            debit_acct = srnb_acct
        elif has_receipt and not srnb_acct:
            # Perpetual inventory fallback: use Inventory (stock) account
            # when SRNB account doesn't exist but receipt is linked
            inv_q = (Q.from_(acct_t).select(acct_t.id)
                     .where(acct_t.account_type == ValueWrapper("stock"))
                     .where(acct_t.company_id == P())
                     .where(acct_t.is_group == 0)
                     .limit(1))
            inv_row = conn.execute(inv_q.get_sql(), (company_id,)).fetchone()
            if inv_row:
                debit_acct = inv_row["id"]
            else:
                debit_acct = item.get("expense_account_id") or default_expense_acct
        else:
            debit_acct = item.get("expense_account_id") or default_expense_acct
        if not debit_acct:
            err(f"No expense account for item {item['item_id']} and no company default")
        item_cc = item.get("cost_center_id") or cost_center_id
        if is_return:
            # Debit note: CR expense/SRNB (reverse the original DR)
            gl_entries.append({
                "account_id": debit_acct,
                "debit": "0",
                "credit": str(round_currency(amount)),
                "cost_center_id": item_cc,
                "fiscal_year": fiscal_year,
            })
        else:
            gl_entries.append({
                "account_id": debit_acct,
                "debit": str(round_currency(amount)),
                "credit": "0",
                "cost_center_id": item_cc,
                "fiscal_year": fiscal_year,
            })

    # 2. DR: Input Tax (if tax exists) — for returns, use abs() and CR
    abs_tax_amount = abs(tax_amount)
    abs_total_amount = abs(total_amount)
    if abs_tax_amount > 0 and pi_dict.get("tax_template_id"):
        ttl_t = Table("tax_template_line").as_("ttl")
        q = (Q.from_(ttl_t)
             .select(ttl_t.tax_account_id, ttl_t.rate)
             .where(ttl_t.tax_template_id == P())
             .orderby(ttl_t.row_order))
        tax_lines = conn.execute(q.get_sql(),
            (pi_dict["tax_template_id"],)).fetchall()
        remaining_tax = abs_tax_amount
        for tl in tax_lines:
            tl_rate = to_decimal(tl["rate"])
            line_tax = round_currency(abs_total_amount * tl_rate / Decimal("100"))
            if line_tax > remaining_tax:
                line_tax = remaining_tax
            if line_tax > 0:
                if is_return:
                    gl_entries.append({
                        "account_id": tl["tax_account_id"],
                        "debit": "0",
                        "credit": str(round_currency(line_tax)),
                        "fiscal_year": fiscal_year,
                    })
                else:
                    gl_entries.append({
                        "account_id": tl["tax_account_id"],
                        "debit": str(round_currency(line_tax)),
                        "credit": "0",
                        "fiscal_year": fiscal_year,
                    })
                remaining_tax -= line_tax
        # If any rounding remainder, add to last tax account
        if remaining_tax > Decimal("0") and tax_lines:
            side = "credit" if is_return else "debit"
            gl_entries[-1][side] = str(round_currency(
                to_decimal(gl_entries[-1][side]) + remaining_tax))

    # 3. CR: Trade Payables / Accounts Payable
    payable_acct = None
    if company_row:
        payable_acct = company_row["default_payable_account_id"]
    if not payable_acct:
        q = (Q.from_(acct_t).select(acct_t.id)
             .where(acct_t.account_type == ValueWrapper("payable"))
             .where(acct_t.company_id == P())
             .where(acct_t.is_group == 0)
             .limit(1))
        payable_row = conn.execute(q.get_sql(), (company_id,)).fetchone()
        payable_acct = payable_row["id"] if payable_row else None
    if not payable_acct:
        err("No payable account found for company")

    abs_grand_total = abs(grand_total)
    if is_return:
        # Debit note: DR payable (reverse the original CR)
        gl_entries.append({
            "account_id": payable_acct,
            "debit": str(round_currency(abs_grand_total)),
            "credit": "0",
            "party_type": "supplier",
            "party_id": supplier_id,
            "fiscal_year": fiscal_year,
        })
    else:
        gl_entries.append({
            "account_id": payable_acct,
            "debit": "0",
            "credit": str(round_currency(grand_total)),
            "party_type": "supplier",
            "party_id": supplier_id,
            "fiscal_year": fiscal_year,
        })

    # Insert GL entries
    gl_ids = []
    if gl_entries:
        try:
            gl_ids = insert_gl_entries(
                conn, gl_entries,
                voucher_type=voucher_type,
                voucher_id=args.purchase_invoice_id,
                posting_date=posting_date,
                company_id=company_id,
                remarks=f"{'Debit Note' if is_return else 'Purchase Invoice'} {naming}",
            )
        except ValueError as e:
            sys.stderr.write(f"[erpclaw-buying] {e}\n")
            err(f"GL posting failed: {e}")

    # --- SLE if update_stock=1 ---
    sle_ids = []
    if update_stock:
        sle_entries = []
        for item_row in items:
            item = row_to_dict(item_row)
            # Determine item type
            item_t = Table("item")
            q = Q.from_(item_t).select(item_t.is_stock_item).where(item_t.id == P())
            item_master = conn.execute(q.get_sql(), (item["item_id"],)).fetchone()
            if not item_master or not item_master["is_stock_item"]:
                continue  # Skip non-stock items

            qty = to_decimal(item["quantity"])
            rate = to_decimal(item["rate"])
            # Determine warehouse
            warehouse_id = None
            if item.get("purchase_receipt_item_id"):
                pri_t2 = Table("purchase_receipt_item")
                q = Q.from_(pri_t2).select(pri_t2.warehouse_id).where(pri_t2.id == P())
                pri = conn.execute(q.get_sql(),
                    (item["purchase_receipt_item_id"],)).fetchone()
                warehouse_id = pri["warehouse_id"] if pri else None
            if not warehouse_id and item.get("purchase_order_item_id"):
                poi_t2 = Table("purchase_order_item")
                q = Q.from_(poi_t2).select(poi_t2.warehouse_id).where(poi_t2.id == P())
                poi = conn.execute(q.get_sql(),
                    (item["purchase_order_item_id"],)).fetchone()
                warehouse_id = poi["warehouse_id"] if poi else None
            if not warehouse_id and company_row:
                warehouse_id = company_row["default_warehouse_id"]
            if not warehouse_id:
                continue  # Skip if no warehouse

            sle_entries.append({
                "item_id": item["item_id"],
                "warehouse_id": warehouse_id,
                "actual_qty": str(round_currency(qty)),
                "incoming_rate": str(round_currency(rate)),
                "fiscal_year": fiscal_year,
            })

        if sle_entries:
            try:
                sle_ids = insert_sle_entries(
                    conn, sle_entries,
                    voucher_type=voucher_type,
                    voucher_id=args.purchase_invoice_id,
                    posting_date=posting_date,
                    company_id=company_id,
                )
            except ValueError as e:
                sys.stderr.write(f"[erpclaw-buying] {e}\n")
                err(f"SLE posting failed: {e}")

            # Inventory GL for SLE (DR Stock In Hand / CR Stock Received Not Billed)
            sle_t = Table("stock_ledger_entry")
            q = (Q.from_(sle_t).select(sle_t.star)
                 .where(sle_t.voucher_type == P())
                 .where(sle_t.voucher_id == P())
                 .where(sle_t.is_cancelled == 0))
            sle_rows = conn.execute(q.get_sql(),
                (voucher_type, args.purchase_invoice_id)).fetchall()
            sle_dicts = [row_to_dict(r) for r in sle_rows]
            inv_gl = create_perpetual_inventory_gl(
                conn, sle_dicts,
                voucher_type=voucher_type,
                voucher_id=args.purchase_invoice_id,
                posting_date=posting_date,
                company_id=company_id,
                cost_center_id=cost_center_id,
            )
            if inv_gl:
                for gle in inv_gl:
                    gle["fiscal_year"] = fiscal_year
                # Insert stock/COGS GL entries via shared lib (entry_set="cogs"
                # allows multiple GL sets per voucher without idempotency conflict)
                stock_remark = f"{'Debit Note' if is_return else 'Purchase Invoice'} Stock {naming}"
                try:
                    cogs_gl_ids = insert_gl_entries(
                        conn, inv_gl,
                        voucher_type=voucher_type,
                        voucher_id=args.purchase_invoice_id,
                        posting_date=posting_date,
                        company_id=company_id,
                        remarks=stock_remark,
                        entry_set="cogs",
                    )
                    gl_ids.extend(cogs_gl_ids)
                except ValueError as e:
                    sys.stderr.write(f"[erpclaw-buying] {e}\n")
                    err(f"Stock GL posting failed: {e}")

    # --- Create PLE (Payment Ledger Entry) ---
    ple_id = str(uuid.uuid4())
    # For returns: PLE amount is negative (reduces supplier liability)
    # against_voucher points to the original invoice being returned against
    if is_return:
        ple_against_type = "purchase_invoice"
        ple_against_id = pi_dict.get("return_against") or args.purchase_invoice_id
        ple_amount = str(round_currency(-abs_grand_total))  # Negative to reduce payable
    else:
        ple_against_type = "purchase_invoice"
        ple_against_id = args.purchase_invoice_id
        ple_amount = str(round_currency(grand_total))
    ple_remark = f"{'Debit Note' if is_return else 'Purchase Invoice'} {naming}"
    ple_t = Table("payment_ledger_entry")
    q = (Q.into(ple_t)
         .columns("id", "posting_date", "account_id", "party_type", "party_id",
                  "voucher_type", "voucher_id", "against_voucher_type",
                  "against_voucher_id", "amount", "amount_in_account_currency",
                  "remarks")
         .insert(P(), P(), P(), ValueWrapper("supplier"), P(), P(), P(), P(), P(),
                 P(), P(), P()))
    conn.execute(q.get_sql(),
        (ple_id, posting_date, payable_acct, supplier_id,
         voucher_type, args.purchase_invoice_id,
         ple_against_type, ple_against_id,
         ple_amount, ple_amount, ple_remark))

    # Update PO invoiced_qty if linked
    if pi_dict.get("purchase_order_id"):
        for item_row in items:
            item = row_to_dict(item_row)
            if item.get("purchase_order_item_id"):
                # raw SQL — CAST arithmetic expression not expressible in PyPika
                conn.execute(
                    """UPDATE purchase_order_item
                       SET invoiced_qty = CAST(
                           invoiced_qty + 0 + ? AS TEXT)
                       WHERE id = ?""",
                    (item["quantity"], item["purchase_order_item_id"]),
                )
        _update_po_invoice_status(conn, pi_dict["purchase_order_id"])

    # Update invoice status
    q = (Q.update(pi_t)
         .set(pi_t.status, ValueWrapper("submitted"))
         .set(pi_t.naming_series, P())
         .set(pi_t.updated_at, LiteralValue("datetime('now')"))
         .where(pi_t.id == P()))
    conn.execute(q.get_sql(), (naming, args.purchase_invoice_id))

    audit_action = "submit-debit-note" if is_return else "submit-purchase-invoice"
    audit(conn, "erpclaw-buying", audit_action, "purchase_invoice",
           args.purchase_invoice_id,
           new_values={"naming_series": naming, "is_return": is_return,
                       "voucher_type": voucher_type,
                       "gl_count": len(gl_ids), "sle_count": len(sle_ids),
                       "update_stock": update_stock})
    conn.commit()
    ok({"purchase_invoice_id": args.purchase_invoice_id,
         "naming_series": naming, "status": "submitted",
         "is_return": is_return, "voucher_type": voucher_type,
         "gl_entries_created": len(gl_ids),
         "sle_entries_created": len(sle_ids),
         "update_stock": bool(update_stock)})


def _update_po_invoice_status(conn, purchase_order_id):
    """Update PO per_invoiced and status based on invoiced quantities."""
    poi_t = Table("purchase_order_item")
    q = (Q.from_(poi_t)
         .select(poi_t.quantity, poi_t.invoiced_qty)
         .where(poi_t.purchase_order_id == P()))
    po_items = conn.execute(q.get_sql(), (purchase_order_id,)).fetchall()

    total_ordered = Decimal("0")
    total_invoiced = Decimal("0")
    for poi in po_items:
        total_ordered += to_decimal(poi["quantity"])
        total_invoiced += to_decimal(poi["invoiced_qty"])

    if total_ordered > 0:
        per_invoiced = round_currency(total_invoiced / total_ordered * Decimal("100"))
    else:
        per_invoiced = Decimal("0")

    if per_invoiced >= Decimal("100"):
        new_status = "fully_invoiced"
    elif per_invoiced > Decimal("0"):
        new_status = "partially_invoiced"
    else:
        return  # No change needed

    # Only update if it makes sense (don't downgrade from fully_received etc.)
    po_t = Table("purchase_order")
    q = Q.from_(po_t).select(po_t.status).where(po_t.id == P())
    current = conn.execute(q.get_sql(), (purchase_order_id,)).fetchone()
    if current and current["status"] not in ("cancelled",):
        q = (Q.update(po_t)
             .set(po_t.per_invoiced, P())
             .set(po_t.status, P())
             .set(po_t.updated_at, LiteralValue("datetime('now')"))
             .where(po_t.id == P()))
        conn.execute(q.get_sql(),
            (str(per_invoiced), new_status, purchase_order_id))


# ---------------------------------------------------------------------------
# 30. cancel-purchase-invoice
# ---------------------------------------------------------------------------

def cancel_purchase_invoice(conn, args):
    """Cancel a submitted purchase invoice: reverse GL + PLE. If update_stock, reverse SLE."""
    if not args.purchase_invoice_id:
        err("--purchase-invoice-id is required")

    pi_t = Table("purchase_invoice")
    q = Q.from_(pi_t).select(pi_t.star).where(pi_t.id == P())
    pi = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchone()
    if not pi:
        err(f"Purchase invoice {args.purchase_invoice_id} not found")
    if pi["status"] not in ("submitted", "overdue", "partially_paid"):
        err(f"Cannot cancel: invoice is '{pi['status']}' "
             f"(must be 'submitted', 'overdue', or 'partially_paid')")

    pi_dict = row_to_dict(pi)
    posting_date = pi_dict["posting_date"]
    update_stock = pi_dict.get("update_stock", 0)

    # Reverse GL
    try:
        reversal_gl_ids = reverse_gl_entries(
            conn,
            voucher_type="purchase_invoice",
            voucher_id=args.purchase_invoice_id,
            posting_date=posting_date,
        )
    except ValueError:
        reversal_gl_ids = []

    # Stock/COGS GL entries (entry_set="cogs") are reversed by the same call above
    # since reverse_gl_entries finds ALL entries for (voucher_type, voucher_id)

    # Reverse SLE if update_stock
    reversal_sle_ids = []
    if update_stock:
        try:
            reversal_sle_ids = reverse_sle_entries(
                conn,
                voucher_type="purchase_invoice",
                voucher_id=args.purchase_invoice_id,
                posting_date=posting_date,
            )
        except ValueError:
            reversal_sle_ids = []

    # Cancel PLE entries
    ple_t = Table("payment_ledger_entry")
    q = (Q.update(ple_t)
         .set(ple_t.delinked, 1)
         .set(ple_t.updated_at, LiteralValue("datetime('now')"))
         .where(ple_t.voucher_type == ValueWrapper("purchase_invoice"))
         .where(ple_t.voucher_id == P()))
    conn.execute(q.get_sql(), (args.purchase_invoice_id,))

    # Reverse PO invoiced_qty if linked
    if pi_dict.get("purchase_order_id"):
        pii_t = Table("purchase_invoice_item")
        q = Q.from_(pii_t).select(pii_t.star).where(pii_t.purchase_invoice_id == P())
        items = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchall()
        for item_row in items:
            item = row_to_dict(item_row)
            if item.get("purchase_order_item_id"):
                # raw SQL — CAST+MAX arithmetic expression not expressible in PyPika
                conn.execute(
                    """UPDATE purchase_order_item
                       SET invoiced_qty = CAST(
                           MAX(0, invoiced_qty + 0 - ?) AS TEXT)
                       WHERE id = ?""",
                    (item["quantity"], item["purchase_order_item_id"]),
                )
        _update_po_invoice_status(conn, pi_dict["purchase_order_id"])

    q = (Q.update(pi_t)
         .set(pi_t.status, ValueWrapper("cancelled"))
         .set(pi_t.updated_at, LiteralValue("datetime('now')"))
         .where(pi_t.id == P()))
    conn.execute(q.get_sql(), (args.purchase_invoice_id,))

    audit(conn, "erpclaw-buying", "cancel-purchase-invoice", "purchase_invoice",
           args.purchase_invoice_id,
           new_values={"reversed": True})
    conn.commit()
    ok({"purchase_invoice_id": args.purchase_invoice_id,
         "status": "cancelled",
         "gl_reversals": len(reversal_gl_ids),
         "sle_reversals": len(reversal_sle_ids)})


# ---------------------------------------------------------------------------
# 31. create-debit-note
# ---------------------------------------------------------------------------

def create_debit_note(conn, args):
    """Create a debit note (return) against a purchase invoice."""
    if not args.against_invoice_id:
        err("--against-invoice-id is required")
    if not args.items:
        err("--items is required (JSON array)")

    pi_t = Table("purchase_invoice")
    q = Q.from_(pi_t).select(pi_t.star).where(pi_t.id == P())
    orig = conn.execute(q.get_sql(), (args.against_invoice_id,)).fetchone()
    if not orig:
        err(f"Purchase invoice {args.against_invoice_id} not found")
    if orig["status"] not in ("submitted", "partially_paid", "paid", "overdue"):
        err(f"Cannot create debit note: invoice status is '{orig['status']}'")

    orig_dict = row_to_dict(orig)
    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    dn_id = str(uuid.uuid4())
    posting_date = args.posting_date or _today()
    total_amount = Decimal("0")

    # Insert parent (is_return=1, negative amounts)
    q = (Q.into(pi_t)
         .columns("id", "supplier_id", "posting_date", "total_amount",
                  "tax_amount", "grand_total", "outstanding_amount", "status",
                  "is_return", "return_against", "update_stock", "company_id")
         .insert(P(), P(), P(), ValueWrapper("0"), ValueWrapper("0"),
                 ValueWrapper("0"), ValueWrapper("0"), ValueWrapper("draft"),
                 1, P(), P(), P()))
    conn.execute(q.get_sql(),
        (dn_id, orig_dict["supplier_id"], posting_date,
         args.against_invoice_id, orig_dict.get("update_stock", 0),
         orig_dict["company_id"]))

    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")
        rate = to_decimal(item.get("rate", "0"))
        if rate <= 0:
            # Look up rate from original invoice
            pii_t = Table("purchase_invoice_item")
            q = (Q.from_(pii_t).select(pii_t.rate)
                 .where(pii_t.purchase_invoice_id == P())
                 .where(pii_t.item_id == P())
                 .limit(1))
            orig_item = conn.execute(q.get_sql(),
                (args.against_invoice_id, item_id)).fetchone()
            rate = to_decimal(orig_item["rate"]) if orig_item else Decimal("0")
        if rate <= 0:
            err(f"Item {i}: rate must be > 0")

        # Negate for return
        neg_qty = -qty
        neg_amount = round_currency(neg_qty * rate)
        total_amount += neg_amount

        conn.execute(
            """INSERT INTO purchase_invoice_item
               (id, purchase_invoice_id, item_id, quantity, rate, amount)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), dn_id, item_id,
             str(round_currency(neg_qty)), str(round_currency(rate)),
             str(neg_amount)),
        )

    grand_total = total_amount  # Already negative

    q = (Q.update(pi_t)
         .set(pi_t.total_amount, P())
         .set(pi_t.grand_total, P())
         .set(pi_t.outstanding_amount, P())
         .where(pi_t.id == P()))
    conn.execute(q.get_sql(),
        (str(round_currency(total_amount)), str(round_currency(grand_total)),
         str(round_currency(grand_total)), dn_id))

    audit(conn, "erpclaw-buying", "create-debit-note", "purchase_invoice", dn_id,
           new_values={"against_invoice_id": args.against_invoice_id,
                       "reason": args.reason,
                       "total_amount": str(round_currency(total_amount))})
    conn.commit()
    ok({"debit_note_id": dn_id,
         "against_invoice_id": args.against_invoice_id,
         "total_amount": str(round_currency(total_amount))})


# ---------------------------------------------------------------------------
# 32. update-invoice-outstanding (cross-skill)
# ---------------------------------------------------------------------------

def update_invoice_outstanding(conn, args):
    """Cross-skill: called by erpclaw-payments to reduce outstanding."""
    if not args.purchase_invoice_id:
        err("--purchase-invoice-id is required")
    if not args.amount:
        err("--amount is required")

    pi_t = Table("purchase_invoice")
    q = Q.from_(pi_t).select(pi_t.star).where(pi_t.id == P())
    pi = conn.execute(q.get_sql(), (args.purchase_invoice_id,)).fetchone()
    if not pi:
        err(f"Purchase invoice {args.purchase_invoice_id} not found")

    payment_amount = to_decimal(args.amount)
    if payment_amount <= 0:
        err("--amount must be > 0")

    current_outstanding = to_decimal(pi["outstanding_amount"])
    new_outstanding = round_currency(current_outstanding - payment_amount)

    if new_outstanding < Decimal("0"):
        new_outstanding = Decimal("0")

    if new_outstanding == Decimal("0"):
        new_status = "paid"
    else:
        new_status = "partially_paid"

    q = (Q.update(pi_t)
         .set(pi_t.outstanding_amount, P())
         .set(pi_t.status, P())
         .set(pi_t.updated_at, LiteralValue("datetime('now')"))
         .where(pi_t.id == P()))
    conn.execute(q.get_sql(),
        (str(new_outstanding), new_status, args.purchase_invoice_id))

    audit(conn, "erpclaw-buying", "update-invoice-outstanding", "purchase_invoice",
           args.purchase_invoice_id,
           new_values={"payment_amount": str(payment_amount),
                       "new_outstanding": str(new_outstanding),
                       "new_status": new_status})
    conn.commit()
    ok({"purchase_invoice_id": args.purchase_invoice_id,
         "outstanding_amount": str(new_outstanding),
         "status": new_status})


# ---------------------------------------------------------------------------
# 33. add-landed-cost-voucher
# ---------------------------------------------------------------------------

def add_landed_cost_voucher(conn, args):
    """Allocate landed costs across purchase receipt items."""
    if not args.purchase_receipt_ids:
        err("--purchase-receipt-ids is required (JSON array)")
    if not args.charges:
        err("--charges is required (JSON array)")
    if not args.company_id:
        err("--company-id is required")

    pr_ids = _parse_json_arg(args.purchase_receipt_ids, "purchase-receipt-ids")
    charges = _parse_json_arg(args.charges, "charges")

    if not pr_ids or not isinstance(pr_ids, list):
        err("--purchase-receipt-ids must be a non-empty JSON array")
    if not charges or not isinstance(charges, list):
        err("--charges must be a non-empty JSON array")

    # Validate receipts and gather items
    pr_t = Table("purchase_receipt")
    pr_q = (Q.from_(pr_t).select(pr_t.star)
            .where(pr_t.id == P())
            .where(pr_t.status == ValueWrapper("submitted")))
    pr_sql = pr_q.get_sql()

    pri_t = Table("purchase_receipt_item")
    pri_q = Q.from_(pri_t).select(pri_t.star).where(pri_t.purchase_receipt_id == P())
    pri_sql = pri_q.get_sql()

    all_items = []
    for pr_id in pr_ids:
        pr = conn.execute(pr_sql, (pr_id,)).fetchone()
        if not pr:
            err(f"Purchase receipt {pr_id} not found or not submitted")
        items = conn.execute(pri_sql, (pr_id,)).fetchall()
        for item_row in items:
            all_items.append(row_to_dict(item_row))

    if not all_items:
        err("No items found in the specified purchase receipts")

    # Calculate total qty and value for allocation
    total_qty = sum(to_decimal(it["quantity"]) for it in all_items)
    total_value = sum(to_decimal(it["amount"]) for it in all_items)

    lcv_id = str(uuid.uuid4())
    posting_date = _today()
    total_landed_cost = Decimal("0")

    # Insert parent first
    lcv_t = Table("landed_cost_voucher")
    q = (Q.into(lcv_t)
         .columns("id", "posting_date", "total_landed_cost", "status", "company_id")
         .insert(P(), P(), ValueWrapper("0"), ValueWrapper("submitted"), P()))
    conn.execute(q.get_sql(), (lcv_id, posting_date, args.company_id))

    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, args.company_id)
    gl_entries = []

    # Process each charge
    for c_idx, charge in enumerate(charges):
        desc = charge.get("description", f"Charge {c_idx + 1}")
        charge_amount = to_decimal(charge.get("amount", "0"))
        if charge_amount <= 0:
            err(f"Charge {c_idx}: amount must be > 0")
        alloc_method = charge.get("allocation_method", "value")
        expense_account_id = charge.get("expense_account_id")

        total_landed_cost += charge_amount

        # Insert charge record
        lcc_t = Table("landed_cost_charge")
        q = (Q.into(lcc_t)
             .columns("id", "landed_cost_voucher_id", "description", "amount",
                      "expense_account_id", "allocation_method")
             .insert(P(), P(), P(), P(), P(), P()))
        conn.execute(q.get_sql(),
            (str(uuid.uuid4()), lcv_id, desc, str(round_currency(charge_amount)),
             expense_account_id,
             "by_qty" if alloc_method == "qty" else "by_amount"))

        # Allocate charge across receipt items
        allocated_so_far = Decimal("0")
        for idx, item in enumerate(all_items):
            if alloc_method == "qty":
                item_qty = to_decimal(item["quantity"])
                if total_qty > 0:
                    proportion = item_qty / total_qty
                else:
                    proportion = Decimal("1") / Decimal(str(len(all_items)))
            else:  # value
                item_value = to_decimal(item["amount"])
                if total_value > 0:
                    proportion = item_value / total_value
                else:
                    proportion = Decimal("1") / Decimal(str(len(all_items)))

            if idx == len(all_items) - 1:
                allocated_amount = round_currency(charge_amount - allocated_so_far)
            else:
                allocated_amount = round_currency(charge_amount * proportion)
            allocated_so_far += allocated_amount

            original_rate = to_decimal(item["rate"])
            item_qty = to_decimal(item["quantity"])
            per_unit_charge = round_currency(allocated_amount / item_qty) if item_qty > 0 else Decimal("0")
            final_rate = round_currency(original_rate + per_unit_charge)

            lci_t = Table("landed_cost_item")
            q = (Q.into(lci_t)
                 .columns("id", "landed_cost_voucher_id", "purchase_receipt_id",
                          "purchase_receipt_item_id", "applicable_charges",
                          "original_rate", "final_rate")
                 .insert(P(), P(), P(), P(), P(), P(), P()))
            conn.execute(q.get_sql(),
                (str(uuid.uuid4()), lcv_id, item["purchase_receipt_id"],
                 item["id"], str(round_currency(allocated_amount)),
                 str(round_currency(original_rate)),
                 str(final_rate)))

        # GL: DR Stock In Hand / CR Expense account for this charge
        if expense_account_id:
            # Find stock account
            acct_t = Table("account")
            q = (Q.from_(acct_t).select(acct_t.id)
                 .where(acct_t.account_type == ValueWrapper("stock"))
                 .where(acct_t.company_id == P())
                 .where(acct_t.is_group == 0)
                 .limit(1))
            stock_acct = conn.execute(q.get_sql(), (args.company_id,)).fetchone()
            stock_acct_id = stock_acct["id"] if stock_acct else None

            if stock_acct_id:
                gl_entries.append({
                    "account_id": stock_acct_id,
                    "debit": str(round_currency(charge_amount)),
                    "credit": "0",
                    "fiscal_year": fiscal_year,
                })
                gl_entries.append({
                    "account_id": expense_account_id,
                    "debit": "0",
                    "credit": str(round_currency(charge_amount)),
                    "cost_center_id": cost_center_id,
                    "fiscal_year": fiscal_year,
                })

    # Update total
    q = (Q.update(lcv_t)
         .set(lcv_t.total_landed_cost, P())
         .where(lcv_t.id == P()))
    conn.execute(q.get_sql(), (str(round_currency(total_landed_cost)), lcv_id))

    # Insert GL entries
    gl_ids = []
    if gl_entries:
        try:
            gl_ids = insert_gl_entries(
                conn, gl_entries,
                voucher_type="landed_cost_voucher",
                voucher_id=lcv_id,
                posting_date=posting_date,
                company_id=args.company_id,
                remarks=f"Landed Cost Voucher",
            )
        except ValueError as e:
            sys.stderr.write(f"[erpclaw-buying] {e}\n")
            err(f"GL posting failed: {e}")

    audit(conn, "erpclaw-buying", "add-landed-cost-voucher", "landed_cost_voucher", lcv_id,
           new_values={"total_landed_cost": str(round_currency(total_landed_cost)),
                       "receipt_count": len(pr_ids)})
    conn.commit()
    ok({"landed_cost_voucher_id": lcv_id,
         "total_landed_cost": str(round_currency(total_landed_cost)),
         "gl_entries_created": len(gl_ids)})


# ---------------------------------------------------------------------------
# 34. status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """Buying summary for a company."""
    company_id = args.company_id
    if not company_id:
        company_t = Table("company")
        q = Q.from_(company_t).select(company_t.id).limit(1)
        row = conn.execute(q.get_sql()).fetchone()
        if not row:
            err("No company found. Create one with erpclaw first.",
                 suggestion="Run 'tutorial' to create a demo company, or 'setup company' to create your own.")
        company_id = row["id"]

    sup_t = Table("supplier")
    q = (Q.from_(sup_t)
         .select(fn.Count("*").as_("cnt"))
         .where(sup_t.company_id == P()))
    supplier_count = conn.execute(q.get_sql(), (company_id,)).fetchone()["cnt"]

    # PO by status
    po_t = Table("purchase_order")
    q = (Q.from_(po_t)
         .select(po_t.status, fn.Count("*").as_("cnt"))
         .where(po_t.company_id == P())
         .groupby(po_t.status))
    po_rows = conn.execute(q.get_sql(), (company_id,)).fetchall()
    po_counts = {}
    for row in po_rows:
        po_counts[row["status"]] = row["cnt"]
    po_counts["total"] = sum(po_counts.values())

    # PI by status
    pi_t = Table("purchase_invoice")
    q = (Q.from_(pi_t)
         .select(pi_t.status, fn.Count("*").as_("cnt"))
         .where(pi_t.company_id == P())
         .groupby(pi_t.status))
    pi_rows = conn.execute(q.get_sql(), (company_id,)).fetchall()
    pi_counts = {}
    for row in pi_rows:
        pi_counts[row["status"]] = row["cnt"]
    pi_counts["total"] = sum(v for k, v in pi_counts.items() if k != "total")

    # Total outstanding
    q = (Q.from_(pi_t)
         .select(fn.Coalesce(DecimalSum(pi_t.outstanding_amount), ValueWrapper("0")).as_("total"))
         .where(pi_t.company_id == P())
         .where(pi_t.status.isin([P(), P(), P()])))
    outstanding = conn.execute(q.get_sql(),
        (company_id, "submitted", "overdue", "partially_paid")).fetchone()
    total_outstanding = round_currency(to_decimal(str(outstanding["total"])))

    ok({
        "suppliers": supplier_count,
        "purchase_orders": po_counts,
        "purchase_invoices": pi_counts,
        "total_outstanding": str(total_outstanding),
    })


# ---------------------------------------------------------------------------
# import-suppliers
# ---------------------------------------------------------------------------

def import_suppliers(conn, args):
    """Bulk import suppliers from a CSV file.

    CSV columns: name, supplier_type (optional), country (optional),
    default_currency (optional), email (optional), phone (optional).
    """
    csv_path = args.csv_path
    company_id = args.company_id
    if not csv_path:
        err("--csv-path is required")
    if not company_id:
        err("--company-id is required")

    # Path safety: resolve symlinks, require .csv extension, must be a regular file
    csv_real = os.path.realpath(csv_path)
    if not csv_real.lower().endswith(".csv"):
        err("--csv-path must point to a .csv file")
    if not os.path.isfile(csv_real):
        err(f"File not found: {csv_path}")

    from erpclaw_lib.csv_import import validate_csv, parse_csv_rows

    errors = validate_csv(csv_real, "supplier")
    if errors:
        err(f"CSV validation failed: {'; '.join(errors)}")

    rows = parse_csv_rows(csv_real, "supplier")
    if not rows:
        err("CSV file is empty")

    imported = 0
    skipped = 0
    for row in rows:
        name = row.get("name", "")

        sup_t = Table("supplier")
        q = (Q.from_(sup_t).select(sup_t.id)
             .where(sup_t.name == P())
             .where(sup_t.company_id == P()))
        existing = conn.execute(q.get_sql(), (name, company_id)).fetchone()
        if existing:
            skipped += 1
            continue

        supplier_id = str(uuid.uuid4())
        naming = get_next_name(conn, "supplier")
        q = (Q.into(sup_t)
             .columns("id", "name", "naming_series", "supplier_type",
                      "country", "default_currency", "email", "phone",
                      "tax_id", "company_id")
             .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
        conn.execute(q.get_sql(),
            (supplier_id, name, naming,
             row.get("supplier_type", "Company"),
             row.get("country"),
             row.get("default_currency", "USD"),
             row.get("email"), row.get("phone"), row.get("tax_id"),
             company_id))
        imported += 1

    conn.commit()
    ok({"imported": imported, "skipped": skipped, "total_rows": len(rows)})


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-supplier": add_supplier,
    "update-supplier": update_supplier,
    "get-supplier": get_supplier,
    "list-suppliers": list_suppliers,
    "add-material-request": add_material_request,
    "submit-material-request": submit_material_request,
    "list-material-requests": list_material_requests,
    "add-rfq": add_rfq,
    "submit-rfq": submit_rfq,
    "list-rfqs": list_rfqs,
    "add-supplier-quotation": add_supplier_quotation,
    "list-supplier-quotations": list_supplier_quotations,
    "compare-supplier-quotations": compare_supplier_quotations,
    "add-purchase-order": add_purchase_order,
    "update-purchase-order": update_purchase_order,
    "get-purchase-order": get_purchase_order,
    "list-purchase-orders": list_purchase_orders,
    "submit-purchase-order": submit_purchase_order,
    "cancel-purchase-order": cancel_purchase_order,
    "create-purchase-receipt": create_purchase_receipt,
    "get-purchase-receipt": get_purchase_receipt,
    "list-purchase-receipts": list_purchase_receipts,
    "submit-purchase-receipt": submit_purchase_receipt,
    "cancel-purchase-receipt": cancel_purchase_receipt,
    "create-purchase-invoice": create_purchase_invoice,
    "update-purchase-invoice": update_purchase_invoice,
    "get-purchase-invoice": get_purchase_invoice,
    "list-purchase-invoices": list_purchase_invoices,
    "submit-purchase-invoice": submit_purchase_invoice,
    "cancel-purchase-invoice": cancel_purchase_invoice,
    "create-debit-note": create_debit_note,
    "update-invoice-outstanding": update_invoice_outstanding,
    "add-landed-cost-voucher": add_landed_cost_voucher,
    "import-suppliers": import_suppliers,
    "status": status_action,
}


def main():
    parser = argparse.ArgumentParser(description="ERPClaw Buying Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Supplier fields
    parser.add_argument("--supplier-id")
    parser.add_argument("--name")
    parser.add_argument("--supplier-group")
    parser.add_argument("--supplier-type")
    parser.add_argument("--payment-terms-id")
    parser.add_argument("--tax-id")
    parser.add_argument("--is-1099-vendor")
    parser.add_argument("--primary-address")
    parser.add_argument("--company-id")
    parser.add_argument("--csv-path")

    # Material request
    parser.add_argument("--material-request-id")
    parser.add_argument("--request-type")
    parser.add_argument("--mr-status", dest="mr_status")

    # RFQ
    parser.add_argument("--rfq-id")
    parser.add_argument("--suppliers")  # JSON
    parser.add_argument("--rfq-status", dest="rfq_status")

    # Purchase order
    parser.add_argument("--purchase-order-id")
    parser.add_argument("--tax-template-id")
    parser.add_argument("--posting-date")
    parser.add_argument("--po-status", dest="po_status")

    # Purchase receipt
    parser.add_argument("--purchase-receipt-id")
    parser.add_argument("--purchase-receipt-ids")  # JSON for landed cost
    parser.add_argument("--pr-status", dest="pr_status")

    # Purchase invoice
    parser.add_argument("--purchase-invoice-id")
    parser.add_argument("--due-date")
    parser.add_argument("--pi-status", dest="pi_status")

    # Debit note
    parser.add_argument("--against-invoice-id")
    parser.add_argument("--reason")

    # Cross-skill
    parser.add_argument("--amount")

    # Landed cost
    parser.add_argument("--charges")  # JSON

    # Common
    parser.add_argument("--items")  # JSON
    parser.add_argument("--search")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

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
        ACTIONS[args.action](conn, args)
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[erpclaw-buying] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
