#!/usr/bin/env python3
"""ERPClaw Selling Skill — db_query.py

Order-to-cash cycle: customers, quotations, sales orders, delivery notes,
sales invoices, credit notes, sales partners, recurring invoices.
Draft->Submit->Cancel lifecycle with GL, SLE, and PLE postings.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sqlite3
import sys
import uuid
import calendar
from datetime import datetime, timezone, timedelta, date as date_type
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
    from erpclaw_lib.query import Q, P, Table, Field, fn, Case, Order, Criterion, Not, NULL, DecimalSum, DecimalAbs, dynamic_update
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company", "account", "item"]

VALID_CUSTOMER_TYPES = ("company", "individual")
VALID_FREQUENCIES = ("weekly", "monthly", "quarterly", "semi_annually", "annually")

# ---------------------------------------------------------------------------
# PyPika table references
# ---------------------------------------------------------------------------
_t_company = Table("company")
_t_customer = Table("customer")
_t_account = Table("account")
_t_cost_center = Table("cost_center")
_t_fiscal_year = Table("fiscal_year")
_t_warehouse = Table("warehouse")
_t_item = Table("item")
_t_quotation = Table("quotation")
_t_quotation_item = Table("quotation_item")
_t_sales_order = Table("sales_order")
_t_sales_order_item = Table("sales_order_item")
_t_delivery_note = Table("delivery_note")
_t_delivery_note_item = Table("delivery_note_item")
_t_sales_invoice = Table("sales_invoice")
_t_sales_invoice_item = Table("sales_invoice_item")
_t_sales_partner = Table("sales_partner")
_t_recurring_template = Table("recurring_invoice_template")
_t_recurring_template_item = Table("recurring_invoice_template_item")
_t_payment_ledger = Table("payment_ledger_entry")
_t_payment_terms = Table("payment_terms")
_t_tax_template_line = Table("tax_template_line")
_t_stock_ledger = Table("stock_ledger_entry")
_t_pricing_rule = Table("pricing_rule")
_t_ic_account_map = Table("intercompany_account_map")
_t_purchase_invoice = Table("purchase_invoice")
_t_purchase_invoice_item = Table("purchase_invoice_item")
_t_supplier = Table("supplier")
_t_blanket_order = Table("blanket_order")
_t_blanket_order_item = Table("blanket_order_item")


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
    """Return the fiscal year name for a posting date, or None."""
    q = (Q.from_(_t_fiscal_year)
         .select(_t_fiscal_year.name)
         .where(_t_fiscal_year.start_date <= P())
         .where(_t_fiscal_year.end_date >= P())
         .where(_t_fiscal_year.is_closed == 0))
    fy = conn.execute(q.get_sql(), (posting_date, posting_date)).fetchone()
    return fy["name"] if fy else None


def _get_cost_center(conn, company_id: str) -> str | None:
    """Return the first non-group cost center for a company, or None."""
    q = (Q.from_(_t_cost_center)
         .select(_t_cost_center.id)
         .where(_t_cost_center.company_id == P())
         .where(_t_cost_center.is_group == 0)
         .limit(1))
    cc = conn.execute(q.get_sql(), (company_id,)).fetchone()
    return cc["id"] if cc else None


def _get_receivable_account(conn, company_id: str) -> str | None:
    """Return the default receivable account for a company."""
    q = (Q.from_(_t_company)
         .select(_t_company.default_receivable_account_id)
         .where(_t_company.id == P()))
    company = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if company and company["default_receivable_account_id"]:
        return company["default_receivable_account_id"]
    q2 = (Q.from_(_t_account)
          .select(_t_account.id)
          .where(_t_account.account_type == ValueWrapper("receivable"))
          .where(_t_account.company_id == P())
          .where(_t_account.is_group == 0)
          .limit(1))
    acct = conn.execute(q2.get_sql(), (company_id,)).fetchone()
    return acct["id"] if acct else None


def _get_income_account(conn, company_id: str) -> str | None:
    """Return the default income account for a company."""
    q = (Q.from_(_t_company)
         .select(_t_company.default_income_account_id)
         .where(_t_company.id == P()))
    company = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if company and company["default_income_account_id"]:
        return company["default_income_account_id"]
    q2 = (Q.from_(_t_account)
          .select(_t_account.id)
          .where(_t_account.root_type == ValueWrapper("income"))
          .where(_t_account.company_id == P())
          .where(_t_account.is_group == 0)
          .limit(1))
    acct = conn.execute(q2.get_sql(), (company_id,)).fetchone()
    return acct["id"] if acct else None


def _get_cogs_account(conn, company_id: str) -> str | None:
    """Return the COGS account for a company."""
    q = (Q.from_(_t_account)
         .select(_t_account.id)
         .where(_t_account.account_type == ValueWrapper("cost_of_goods_sold"))
         .where(_t_account.company_id == P())
         .where(_t_account.is_group == 0)
         .limit(1))
    acct = conn.execute(q.get_sql(), (company_id,)).fetchone()
    return acct["id"] if acct else None


def _get_stock_in_hand_account(conn, company_id: str, warehouse_id: str = None) -> str | None:
    """Return the stock-in-hand account for a warehouse or company default."""
    if warehouse_id:
        q = (Q.from_(_t_warehouse)
             .select(_t_warehouse.account_id)
             .where(_t_warehouse.id == P()))
        wh = conn.execute(q.get_sql(), (warehouse_id,)).fetchone()
        if wh and wh["account_id"]:
            return wh["account_id"]
    q2 = (Q.from_(_t_account)
          .select(_t_account.id)
          .where(_t_account.account_type == ValueWrapper("stock"))
          .where(_t_account.company_id == P())
          .where(_t_account.is_group == 0)
          .limit(1))
    acct = conn.execute(q2.get_sql(), (company_id,)).fetchone()
    return acct["id"] if acct else None


def _calculate_tax(conn, subtotal: Decimal, tax_template_id: str) -> tuple:
    """Calculate tax from a tax template.

    Returns (tax_amount, list_of_tax_lines) where each tax line is a dict
    with account_id, rate, amount.
    """
    if not tax_template_id:
        return Decimal("0"), []

    ttl = _t_tax_template_line.as_("ttl")
    a = _t_account.as_("a")
    q = (Q.from_(ttl)
         .left_join(a).on(a.id == ttl.tax_account_id)
         .select(ttl.star, a.name.as_("account_name"))
         .where(ttl.tax_template_id == P())
         .orderby(ttl.row_order))
    lines = conn.execute(q.get_sql(), (tax_template_id,)).fetchall()

    total_tax = Decimal("0")
    tax_lines = []
    cumulative_amount = subtotal

    for line in lines:
        rate = to_decimal(line["rate"])
        charge_type = line["charge_type"]
        add_deduct = line["add_deduct"]

        if charge_type == "on_net_total":
            tax_amount = round_currency(subtotal * rate / Decimal("100"))
        elif charge_type == "actual":
            tax_amount = round_currency(rate)
        elif charge_type == "on_previous_row_total":
            tax_amount = round_currency(cumulative_amount * rate / Decimal("100"))
        elif charge_type == "on_previous_row_amount":
            prev_tax = tax_lines[-1]["amount"] if tax_lines else Decimal("0")
            tax_amount = round_currency(prev_tax * rate / Decimal("100"))
        elif charge_type == "on_item_quantity":
            tax_amount = round_currency(rate)
        else:
            tax_amount = Decimal("0")

        if add_deduct == "deduct":
            tax_amount = -tax_amount

        total_tax += tax_amount
        cumulative_amount += tax_amount
        tax_lines.append({
            "account_id": line["tax_account_id"],
            "account_name": line["account_name"] if line["account_name"] else "",
            "rate": str(rate),
            "amount": tax_amount,
        })

    return round_currency(total_tax), tax_lines


def _apply_pricing_rule(conn, item_id: str, customer_id: str,
                        qty: Decimal, posting_date: str,
                        company_id: str) -> dict | None:
    """Find and return the best applicable pricing rule for an item."""
    # raw SQL — complex OR conditions, NULL+arithmetic comparisons, COALESCE+arithmetic ORDER BY
    row = conn.execute(
        """SELECT * FROM pricing_rule
           WHERE active = 1 AND company_id = ?
             AND (
                 (applies_to = 'item' AND entity_id = ?)
                 OR (applies_to = 'customer' AND entity_id = ?)
                 OR applies_to = 'item_group'
                 OR applies_to = 'customer_group'
             )
             AND (min_qty IS NULL OR min_qty + 0 <= ? + 0)
             AND (max_qty IS NULL OR max_qty + 0 >= ? + 0)
             AND (valid_from IS NULL OR valid_from <= ?)
             AND (valid_to IS NULL OR valid_to >= ?)
           ORDER BY priority DESC, COALESCE(min_qty, '0') + 0 DESC
           LIMIT 1""",
        (company_id, item_id, customer_id, str(qty), str(qty),
         posting_date, posting_date),
    ).fetchone()
    return row_to_dict(row) if row else None


def _calculate_line_items(conn, items_json, company_id: str,
                          customer_id: str = None, posting_date: str = None,
                          apply_pricing: bool = False):
    """Validate and calculate line items from JSON.

    Returns (total_amount, item_rows_list) where each item_row is a tuple
    ready for insertion.
    """
    if not items_json or not isinstance(items_json, list):
        err("--items must be a non-empty JSON array")

    total = Decimal("0")
    rows = []
    for i, item in enumerate(items_json):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")

        q = (Q.from_(_t_item)
             .select(_t_item.id, _t_item.item_name, _t_item.stock_uom)
             .where(_t_item.id == P()))
        item_row = conn.execute(q.get_sql(), (item_id,)).fetchone()
        if not item_row:
            err(f"Item {i}: item {item_id} not found")

        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")

        rate = to_decimal(item.get("rate", "0"))
        discount_pct = to_decimal(item.get("discount_percentage", "0"))
        warehouse_id = item.get("warehouse_id")
        pricing_rule_id = None

        # Apply pricing rule if requested
        if apply_pricing and customer_id and posting_date and rate > 0:
            rule = _apply_pricing_rule(conn, item_id, customer_id, qty,
                                       posting_date, company_id)
            if rule:
                pricing_rule_id = rule.get("id")
                if rule.get("discount_percentage"):
                    discount_pct = to_decimal(rule["discount_percentage"])
                elif rule.get("rate"):
                    rate = to_decimal(rule["rate"])

        if discount_pct > 0:
            effective_rate = round_currency(rate * (Decimal("1") - discount_pct / Decimal("100")))
        else:
            effective_rate = rate

        amount = round_currency(qty * rate)
        net_amount = round_currency(qty * effective_rate)
        total += net_amount

        rows.append({
            "item_id": item_id,
            "qty": str(round_currency(qty)),
            "uom": item.get("uom") or item_row["stock_uom"],
            "rate": str(round_currency(rate)),
            "amount": str(amount),
            "discount_percentage": str(round_currency(discount_pct)),
            "net_amount": str(net_amount),
            "warehouse_id": warehouse_id,
            "pricing_rule_id": pricing_rule_id,
            "description": item.get("description"),
        })

    return round_currency(total), rows


def _add_months(d: date_type, months: int) -> date_type:
    """Add months to a date, clamping to last day of month if needed."""
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date_type(year, month, day)


def _next_invoice_date(current_date_str: str, frequency: str) -> str:
    """Calculate next invoice date based on frequency."""
    parts = current_date_str.split("-")
    d = date_type(int(parts[0]), int(parts[1]), int(parts[2]))

    if frequency == "weekly":
        d += timedelta(days=7)
    elif frequency == "monthly":
        d = _add_months(d, 1)
    elif frequency == "quarterly":
        d = _add_months(d, 3)
    elif frequency == "semi_annually":
        d = _add_months(d, 6)
    elif frequency == "annually":
        d = _add_months(d, 12)
    else:
        d = _add_months(d, 1)

    return d.isoformat()


# ---------------------------------------------------------------------------
# 1. add-customer
# ---------------------------------------------------------------------------

def add_customer(conn, args):
    """Create a customer record."""
    if not args.name:
        err("--name is required")
    if not args.company_id:
        err("--company-id is required")

    q = Q.from_(_t_company).select(_t_company.id).where(_t_company.id == P())
    if not conn.execute(q.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    customer_type = args.customer_type or "company"
    if customer_type not in VALID_CUSTOMER_TYPES:
        err(f"--customer-type must be one of: {', '.join(VALID_CUSTOMER_TYPES)}")

    if args.payment_terms_id:
        q = Q.from_(_t_payment_terms).select(_t_payment_terms.id).where(_t_payment_terms.id == P())
        if not conn.execute(q.get_sql(), (args.payment_terms_id,)).fetchone():
            err(f"Payment terms {args.payment_terms_id} not found")

    credit_limit = str(round_currency(to_decimal(args.credit_limit or "0")))
    exempt = int(args.exempt_from_sales_tax) if args.exempt_from_sales_tax else 0

    primary_address = args.primary_address
    primary_contact = args.primary_contact

    cust_id = str(uuid.uuid4())
    try:
        q = (Q.into(_t_customer)
             .columns("id", "name", "customer_type", "customer_group",
                       "payment_terms_id", "credit_limit", "tax_id",
                       "exempt_from_sales_tax", "primary_address",
                       "primary_contact", "status", "company_id")
             .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(),
                     ValueWrapper("active"), P()))
        conn.execute(q.get_sql(),
            (cust_id, args.name, customer_type, args.customer_group,
             args.payment_terms_id, credit_limit, args.tax_id, exempt,
             primary_address, primary_contact, args.company_id),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-selling] {e}\n")
        err("Customer creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-selling", "add-customer", "customer", cust_id,
           new_values={"name": args.name, "customer_type": customer_type})
    conn.commit()
    ok({"customer_id": cust_id, "name": args.name,
         "customer_type": customer_type})


# ---------------------------------------------------------------------------
# 2. update-customer
# ---------------------------------------------------------------------------

def update_customer(conn, args):
    """Update an existing customer."""
    if not args.customer_id:
        err("--customer-id is required")

    q = (Q.from_(_t_customer)
         .select(_t_customer.star)
         .where((_t_customer.id == P()) | (_t_customer.name == P())))
    cust = conn.execute(q.get_sql(),
                        (args.customer_id, args.customer_id)).fetchone()
    if not cust:
        err(f"Customer {args.customer_id} not found",
             suggestion="Use 'list customers' to see available customers.")
    args.customer_id = cust["id"]  # normalize to id

    data, updated_fields = {}, []

    if args.name is not None:
        data["name"] = args.name
        updated_fields.append("name")
    if args.credit_limit is not None:
        data["credit_limit"] = str(round_currency(to_decimal(args.credit_limit)))
        updated_fields.append("credit_limit")
    if args.payment_terms_id is not None:
        data["payment_terms_id"] = args.payment_terms_id
        updated_fields.append("payment_terms_id")
    if args.customer_group is not None:
        data["customer_group"] = args.customer_group
        updated_fields.append("customer_group")
    if args.customer_type is not None:
        if args.customer_type not in VALID_CUSTOMER_TYPES:
            err(f"--customer-type must be one of: {', '.join(VALID_CUSTOMER_TYPES)}")
        data["customer_type"] = args.customer_type
        updated_fields.append("customer_type")

    if not updated_fields:
        err("No fields to update")

    data["updated_at"] = LiteralValue("datetime('now')")
    sql, params = dynamic_update("customer", data, where={"id": args.customer_id})
    conn.execute(sql, params)

    audit(conn, "erpclaw-selling", "update-customer", "customer", args.customer_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"customer_id": args.customer_id, "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 3. get-customer
# ---------------------------------------------------------------------------

def get_customer(conn, args):
    """Get customer with outstanding summary."""
    if not args.customer_id:
        err("--customer-id is required")

    q = (Q.from_(_t_customer)
         .select(_t_customer.star)
         .where((_t_customer.id == P()) | (_t_customer.name == P())))
    cust = conn.execute(q.get_sql(),
                        (args.customer_id, args.customer_id)).fetchone()
    if not cust:
        err(f"Customer {args.customer_id} not found",
             suggestion="Use 'list customers' to see available customers.")

    data = row_to_dict(cust)

    # Outstanding summary from sales invoices
    # raw SQL — decimal_sum with COALESCE and arithmetic comparison on TEXT column
    outstanding_row = conn.execute(
        """SELECT COALESCE(decimal_sum(outstanding_amount), '0') as total_outstanding,
                  COUNT(*) as invoice_count
           FROM sales_invoice
           WHERE customer_id = ? AND status IN ('submitted', 'overdue', 'partially_paid')
             AND outstanding_amount + 0 > 0""",
        (args.customer_id,),
    ).fetchone()

    data["total_outstanding"] = str(round_currency(
        to_decimal(str(outstanding_row["total_outstanding"]))))
    data["outstanding_invoice_count"] = outstanding_row["invoice_count"]

    ok(data)


# ---------------------------------------------------------------------------
# 4. list-customers
# ---------------------------------------------------------------------------

def list_customers(conn, args):
    """Query customers with filtering."""
    c = _t_customer.as_("c")
    params = []

    base = Q.from_(c)
    crit = None

    if args.company_id:
        crit = Criterion.all([crit, c.company_id == P()]) if crit else (c.company_id == P())
        params.append(args.company_id)
    if args.customer_group:
        cond = c.customer_group == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.customer_group)
    if args.search:
        cond = (c.name.like(P()) | c.tax_id.like(P()))
        crit = Criterion.all([crit, cond]) if crit else cond
        params.extend([f"%{args.search}%", f"%{args.search}%"])

    count_q = base.select(fn.Count("*"))
    if crit:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (base.select(c.id, c.name, c.customer_type, c.customer_group,
                           c.territory, c.credit_limit, c.status, c.company_id)
              .orderby(c.name)
              .limit(P()).offset(P()))
    if crit:
        list_q = list_q.where(crit)
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({"customers": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 5. add-quotation
# ---------------------------------------------------------------------------

def add_quotation(conn, args):
    """Create a quotation in draft."""
    if not args.customer_id:
        err("--customer-id is required")
    if not args.posting_date:
        err("--posting-date is required")
    if not args.items:
        err("--items is required (JSON array)")
    if not args.company_id:
        err("--company-id is required")

    q = (Q.from_(_t_customer).select(_t_customer.id)
         .where((_t_customer.id == P()) | (_t_customer.name == P()))
         .where(_t_customer.status == ValueWrapper("active")))
    cust_row = conn.execute(q.get_sql(),
        (args.customer_id, args.customer_id)).fetchone()
    if not cust_row:
        err(f"Active customer {args.customer_id} not found")
    args.customer_id = cust_row["id"]  # normalize to id
    q2 = Q.from_(_t_company).select(_t_company.id).where(_t_company.id == P())
    if not conn.execute(q2.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    items = _parse_json_arg(args.items, "items")
    total_amount, item_rows = _calculate_line_items(
        conn, items, args.company_id, args.customer_id, args.posting_date)

    tax_amount, tax_lines = _calculate_tax(conn, total_amount, args.tax_template_id)
    grand_total = round_currency(total_amount + tax_amount)

    q_id = str(uuid.uuid4())

    # Insert parent quotation first
    qi = (Q.into(_t_quotation)
          .columns("id", "customer_id", "quotation_date", "valid_until",
                    "total_amount", "tax_amount", "grand_total",
                    "tax_template_id", "status", "company_id")
          .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                  ValueWrapper("draft"), P()))
    conn.execute(qi.get_sql(),
        (q_id, args.customer_id, args.posting_date, args.valid_till,
         str(total_amount), str(tax_amount), str(grand_total),
         args.tax_template_id, args.company_id),
    )

    # Insert child quotation_item rows
    qi_item = (Q.into(_t_quotation_item)
               .columns("id", "quotation_id", "item_id", "quantity", "uom",
                         "rate", "amount", "discount_percentage",
                         "net_amount", "description")
               .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    qi_item_sql = qi_item.get_sql()
    for row in item_rows:
        conn.execute(qi_item_sql,
            (str(uuid.uuid4()), q_id, row["item_id"], row["qty"],
             row["uom"], row["rate"], row["amount"],
             row["discount_percentage"], row["net_amount"],
             row["description"]),
        )

    audit(conn, "erpclaw-selling", "add-quotation", "quotation", q_id,
           new_values={"customer_id": args.customer_id, "grand_total": str(grand_total)})
    conn.commit()
    ok({"quotation_id": q_id, "total_amount": str(total_amount),
         "tax_amount": str(tax_amount), "grand_total": str(grand_total)})


# ---------------------------------------------------------------------------
# 6. update-quotation
# ---------------------------------------------------------------------------

def update_quotation(conn, args):
    """Update a draft quotation."""
    if not args.quotation_id:
        err("--quotation-id is required")

    qq = (Q.from_(_t_quotation).select(_t_quotation.star)
          .where(_t_quotation.id == P()))
    q = conn.execute(qq.get_sql(), (args.quotation_id,)).fetchone()
    if not q:
        err(f"Quotation {args.quotation_id} not found")
    if q["status"] != "draft":
        err(f"Cannot update: quotation is '{q['status']}' (must be 'draft')",
             suggestion="Cancel the document first, then make changes.")

    updated_fields = []

    if args.valid_till is not None:
        uq = (Q.update(_t_quotation)
              .set("valid_until", P())
              .set("updated_at", LiteralValue("datetime('now')"))
              .where(_t_quotation.id == P()))
        conn.execute(uq.get_sql(), (args.valid_till, args.quotation_id))
        updated_fields.append("valid_until")

    if args.items:
        items = _parse_json_arg(args.items, "items")
        total_amount, item_rows = _calculate_line_items(
            conn, items, q["company_id"], q["customer_id"], q["quotation_date"])

        tax_amount, _ = _calculate_tax(conn, total_amount, q["tax_template_id"])
        grand_total = round_currency(total_amount + tax_amount)

        # Delete old items, insert new
        dq = Q.from_(_t_quotation_item).delete().where(_t_quotation_item.quotation_id == P())
        conn.execute(dq.get_sql(), (args.quotation_id,))
        qi_item = (Q.into(_t_quotation_item)
                   .columns("id", "quotation_id", "item_id", "quantity", "uom",
                             "rate", "amount", "discount_percentage",
                             "net_amount", "description")
                   .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
        qi_item_sql = qi_item.get_sql()
        for row in item_rows:
            conn.execute(qi_item_sql,
                (str(uuid.uuid4()), args.quotation_id, row["item_id"],
                 row["qty"], row["uom"], row["rate"], row["amount"],
                 row["discount_percentage"], row["net_amount"],
                 row["description"]),
            )

        uq2 = (Q.update(_t_quotation)
               .set("total_amount", P())
               .set("tax_amount", P())
               .set("grand_total", P())
               .set("updated_at", LiteralValue("datetime('now')"))
               .where(_t_quotation.id == P()))
        conn.execute(uq2.get_sql(),
            (str(total_amount), str(tax_amount), str(grand_total),
             args.quotation_id),
        )
        updated_fields.extend(["items", "total_amount", "tax_amount", "grand_total"])

    if not updated_fields:
        err("No fields to update")

    audit(conn, "erpclaw-selling", "update-quotation", "quotation", args.quotation_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"quotation_id": args.quotation_id, "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 7. get-quotation
# ---------------------------------------------------------------------------

def get_quotation(conn, args):
    """Get quotation with items."""
    if not args.quotation_id:
        err("--quotation-id is required")

    qq = (Q.from_(_t_quotation).select(_t_quotation.star)
          .where(_t_quotation.id == P()))
    q = conn.execute(qq.get_sql(), (args.quotation_id,)).fetchone()
    if not q:
        err(f"Quotation {args.quotation_id} not found")

    data = row_to_dict(q)
    qi = _t_quotation_item.as_("qi")
    i = _t_item.as_("i")
    items_q = (Q.from_(qi)
               .left_join(i).on(i.id == qi.item_id)
               .select(qi.star, i.item_name)
               .where(qi.quotation_id == P())
               .orderby(qi.rowid))
    items = conn.execute(items_q.get_sql(), (args.quotation_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]
    ok(data)


# ---------------------------------------------------------------------------
# 8. list-quotations
# ---------------------------------------------------------------------------

def list_quotations(conn, args):
    """Query quotations with filtering."""
    q = _t_quotation.as_("q")
    c = _t_customer.as_("c")
    params = []
    crit = None

    if args.company_id:
        crit = (q.company_id == P())
        params.append(args.company_id)
    if args.customer_id:
        cond = q.customer_id == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.customer_id)
    if args.doc_status:
        cond = q.status == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.doc_status)
    if args.from_date:
        cond = q.quotation_date >= P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.from_date)
    if args.to_date:
        cond = q.quotation_date <= P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.to_date)

    count_q = Q.from_(q).select(fn.Count("*"))
    if crit:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(q)
              .left_join(c).on(c.id == q.customer_id)
              .select(q.id, q.naming_series, q.customer_id,
                      c.name.as_("customer_name"),
                      q.quotation_date,
                      q.grand_total, q.status, q.company_id)
              .orderby(q.quotation_date, order=Order.desc)
              .orderby(q.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    if crit:
        list_q = list_q.where(crit)
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({"quotations": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 9. submit-quotation
# ---------------------------------------------------------------------------

def submit_quotation(conn, args):
    """Submit a quotation: draft -> open."""
    if not args.quotation_id:
        err("--quotation-id is required")

    qq = (Q.from_(_t_quotation).select(_t_quotation.star)
          .where(_t_quotation.id == P()))
    q = conn.execute(qq.get_sql(), (args.quotation_id,)).fetchone()
    if not q:
        err(f"Quotation {args.quotation_id} not found")
    if q["status"] != "draft":
        err(f"Cannot submit: quotation is '{q['status']}' (must be 'draft')")

    # Generate naming series
    naming = get_next_name(conn, "quotation", company_id=q["company_id"])

    uq = (Q.update(_t_quotation)
          .set("status", ValueWrapper("open"))
          .set("naming_series", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_quotation.id == P()))
    conn.execute(uq.get_sql(), (naming, args.quotation_id))

    audit(conn, "erpclaw-selling", "submit-quotation", "quotation", args.quotation_id,
           new_values={"status": "open", "naming_series": naming})
    conn.commit()
    ok({"quotation_id": args.quotation_id, "naming_series": naming,
         "status": "open"})


# ---------------------------------------------------------------------------
# 10. convert-quotation-to-so
# ---------------------------------------------------------------------------

def convert_quotation_to_so(conn, args):
    """Create a sales order from a quotation."""
    if not args.quotation_id:
        err("--quotation-id is required")

    qq = (Q.from_(_t_quotation).select(_t_quotation.star)
          .where(_t_quotation.id == P()))
    q = conn.execute(qq.get_sql(), (args.quotation_id,)).fetchone()
    if not q:
        err(f"Quotation {args.quotation_id} not found")
    if q["status"] not in ("open", "draft"):
        err(f"Cannot convert: quotation is '{q['status']}' (must be 'open' or 'draft')")

    q_dict = row_to_dict(q)

    # Fetch quotation items
    qi_q = (Q.from_(_t_quotation_item).select(_t_quotation_item.star)
            .where(_t_quotation_item.quotation_id == P())
            .orderby(_t_quotation_item.rowid))
    q_items = conn.execute(qi_q.get_sql(), (args.quotation_id,)).fetchall()
    if not q_items:
        err("Quotation has no items")

    so_id = str(uuid.uuid4())
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Insert parent sales_order first
    so_ins = (Q.into(_t_sales_order)
              .columns("id", "customer_id", "order_date", "delivery_date",
                        "currency", "exchange_rate", "total_amount",
                        "tax_amount", "grand_total", "tax_template_id",
                        "payment_terms_id", "status", "quotation_id", "company_id")
              .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P(),
                      ValueWrapper("draft"), P(), P()))
    conn.execute(so_ins.get_sql(),
        (so_id, q_dict["customer_id"], today, args.delivery_date,
         q_dict["currency"], q_dict["exchange_rate"],
         q_dict["total_amount"], q_dict["tax_amount"], q_dict["grand_total"],
         q_dict["tax_template_id"], q_dict["payment_terms_id"],
         args.quotation_id, q_dict["company_id"]),
    )

    # Insert child sales_order_item rows from quotation items
    soi_ins = (Q.into(_t_sales_order_item)
               .columns("id", "sales_order_id", "item_id", "quantity", "uom",
                         "rate", "amount", "discount_percentage",
                         "net_amount", "warehouse_id")
               .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    soi_ins_sql = soi_ins.get_sql()
    for qi in q_items:
        qi_dict = row_to_dict(qi)
        conn.execute(soi_ins_sql,
            (str(uuid.uuid4()), so_id, qi_dict["item_id"],
             qi_dict["quantity"], qi_dict["uom"], qi_dict["rate"],
             qi_dict["amount"], qi_dict["discount_percentage"],
             qi_dict["net_amount"], None),
        )

    # Update quotation status to ordered
    uq = (Q.update(_t_quotation)
          .set("status", ValueWrapper("ordered"))
          .set("converted_to", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_quotation.id == P()))
    conn.execute(uq.get_sql(), (so_id, args.quotation_id))

    audit(conn, "erpclaw-selling", "convert-quotation-to-so", "quotation", args.quotation_id,
           new_values={"sales_order_id": so_id})
    conn.commit()
    ok({"quotation_id": args.quotation_id, "sales_order_id": so_id,
         "status": "ordered"})


# ---------------------------------------------------------------------------
# 11. add-sales-order
# ---------------------------------------------------------------------------

def add_sales_order(conn, args):
    """Create a sales order in draft."""
    if not args.customer_id:
        err("--customer-id is required")
    if not args.posting_date:
        err("--posting-date is required")
    if not args.items:
        err("--items is required (JSON array)")
    if not args.company_id:
        err("--company-id is required")

    cq = (Q.from_(_t_customer).select(_t_customer.star)
          .where((_t_customer.id == P()) | (_t_customer.name == P()))
          .where(_t_customer.status == ValueWrapper("active")))
    cust = conn.execute(cq.get_sql(),
                        (args.customer_id, args.customer_id)).fetchone()
    if not cust:
        err(f"Active customer {args.customer_id} not found")
    args.customer_id = cust["id"]  # normalize to id
    cq2 = Q.from_(_t_company).select(_t_company.id).where(_t_company.id == P())
    if not conn.execute(cq2.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    items = _parse_json_arg(args.items, "items")
    total_amount, item_rows = _calculate_line_items(
        conn, items, args.company_id, args.customer_id, args.posting_date,
        apply_pricing=True)

    tax_amount, _ = _calculate_tax(conn, total_amount, args.tax_template_id)
    grand_total = round_currency(total_amount + tax_amount)

    so_id = str(uuid.uuid4())

    # Insert parent sales_order first
    so_ins = (Q.into(_t_sales_order)
              .columns("id", "customer_id", "order_date", "delivery_date",
                        "total_amount", "tax_amount", "grand_total",
                        "tax_template_id", "status", "company_id")
              .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                      ValueWrapper("draft"), P()))
    conn.execute(so_ins.get_sql(),
        (so_id, args.customer_id, args.posting_date, args.delivery_date,
         str(total_amount), str(tax_amount), str(grand_total),
         args.tax_template_id, args.company_id),
    )

    # Insert child sales_order_item rows
    soi_ins = (Q.into(_t_sales_order_item)
               .columns("id", "sales_order_id", "item_id", "quantity", "uom",
                         "rate", "amount", "discount_percentage",
                         "net_amount", "warehouse_id")
               .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    soi_ins_sql = soi_ins.get_sql()
    for row in item_rows:
        conn.execute(soi_ins_sql,
            (str(uuid.uuid4()), so_id, row["item_id"], row["qty"],
             row["uom"], row["rate"], row["amount"],
             row["discount_percentage"], row["net_amount"],
             row["warehouse_id"]),
        )

    audit(conn, "erpclaw-selling", "add-sales-order", "sales_order", so_id,
           new_values={"customer_id": args.customer_id, "grand_total": str(grand_total)})
    conn.commit()
    ok({"sales_order_id": so_id, "total_amount": str(total_amount),
         "tax_amount": str(tax_amount), "grand_total": str(grand_total)})


# ---------------------------------------------------------------------------
# 12. update-sales-order
# ---------------------------------------------------------------------------

def update_sales_order(conn, args):
    """Update a draft sales order."""
    if not args.sales_order_id:
        err("--sales-order-id is required")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")
    if so["status"] != "draft":
        err(f"Cannot update: sales order is '{so['status']}' (must be 'draft')",
             suggestion="Cancel the document first, then make changes.")

    updated_fields = []

    if args.delivery_date is not None:
        uq = (Q.update(_t_sales_order)
              .set("delivery_date", P())
              .set("updated_at", LiteralValue("datetime('now')"))
              .where(_t_sales_order.id == P()))
        conn.execute(uq.get_sql(), (args.delivery_date, args.sales_order_id))
        updated_fields.append("delivery_date")

    if args.items:
        items = _parse_json_arg(args.items, "items")
        total_amount, item_rows = _calculate_line_items(
            conn, items, so["company_id"], so["customer_id"], so["order_date"],
            apply_pricing=True)

        tax_amount, _ = _calculate_tax(conn, total_amount, so["tax_template_id"])
        grand_total = round_currency(total_amount + tax_amount)

        # Delete old items, insert new
        dq = Q.from_(_t_sales_order_item).delete().where(_t_sales_order_item.sales_order_id == P())
        conn.execute(dq.get_sql(), (args.sales_order_id,))
        soi_ins = (Q.into(_t_sales_order_item)
                   .columns("id", "sales_order_id", "item_id", "quantity", "uom",
                             "rate", "amount", "discount_percentage",
                             "net_amount", "warehouse_id")
                   .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
        soi_ins_sql = soi_ins.get_sql()
        for row in item_rows:
            conn.execute(soi_ins_sql,
                (str(uuid.uuid4()), args.sales_order_id, row["item_id"],
                 row["qty"], row["uom"], row["rate"], row["amount"],
                 row["discount_percentage"], row["net_amount"],
                 row["warehouse_id"]),
            )

        uq2 = (Q.update(_t_sales_order)
               .set("total_amount", P())
               .set("tax_amount", P())
               .set("grand_total", P())
               .set("updated_at", LiteralValue("datetime('now')"))
               .where(_t_sales_order.id == P()))
        conn.execute(uq2.get_sql(),
            (str(total_amount), str(tax_amount), str(grand_total),
             args.sales_order_id),
        )
        updated_fields.extend(["items", "total_amount", "tax_amount", "grand_total"])

    if not updated_fields:
        err("No fields to update")

    audit(conn, "erpclaw-selling", "update-sales-order", "sales_order", args.sales_order_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"sales_order_id": args.sales_order_id, "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 13. get-sales-order
# ---------------------------------------------------------------------------

def get_sales_order(conn, args):
    """Get sales order with items and fulfillment/billing status."""
    if not args.sales_order_id:
        err("--sales-order-id is required")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")

    data = row_to_dict(so)

    soi = _t_sales_order_item.as_("soi")
    i = _t_item.as_("i")
    items_q = (Q.from_(soi)
               .left_join(i).on(i.id == soi.item_id)
               .select(soi.star, i.item_name, i.item_code)
               .where(soi.sales_order_id == P())
               .orderby(soi.rowid))
    items = conn.execute(items_q.get_sql(), (args.sales_order_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    # Delivery note summary
    dnq = (Q.from_(_t_delivery_note)
           .select(_t_delivery_note.id, _t_delivery_note.naming_series,
                   _t_delivery_note.status, _t_delivery_note.posting_date)
           .where(_t_delivery_note.sales_order_id == P())
           .where(_t_delivery_note.status != ValueWrapper("cancelled")))
    dn_rows = conn.execute(dnq.get_sql(), (args.sales_order_id,)).fetchall()
    data["delivery_notes"] = [row_to_dict(r) for r in dn_rows]

    # Invoice summary
    siq = (Q.from_(_t_sales_invoice)
           .select(_t_sales_invoice.id, _t_sales_invoice.naming_series,
                   _t_sales_invoice.status, _t_sales_invoice.posting_date,
                   _t_sales_invoice.grand_total, _t_sales_invoice.outstanding_amount)
           .where(_t_sales_invoice.sales_order_id == P())
           .where(_t_sales_invoice.status != ValueWrapper("cancelled")))
    si_rows = conn.execute(siq.get_sql(), (args.sales_order_id,)).fetchall()
    data["sales_invoices"] = [row_to_dict(r) for r in si_rows]

    ok(data)


# ---------------------------------------------------------------------------
# 14. list-sales-orders
# ---------------------------------------------------------------------------

def list_sales_orders(conn, args):
    """Query sales orders with filtering."""
    so = _t_sales_order.as_("so")
    c = _t_customer.as_("c")
    params = []
    crit = None

    if args.company_id:
        crit = (so.company_id == P())
        params.append(args.company_id)
    if args.customer_id:
        cond = so.customer_id == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.customer_id)
    if args.doc_status:
        cond = so.status == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.doc_status)
    if args.from_date:
        cond = so.order_date >= P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.from_date)
    if args.to_date:
        cond = so.order_date <= P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.to_date)

    count_q = Q.from_(so).select(fn.Count("*"))
    if crit:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(so)
              .left_join(c).on(c.id == so.customer_id)
              .select(so.id, so.naming_series, so.customer_id,
                      c.name.as_("customer_name"),
                      so.order_date, so.delivery_date, so.grand_total,
                      so.status, so.per_delivered, so.per_invoiced, so.company_id)
              .orderby(so.order_date, order=Order.desc)
              .orderby(so.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    if crit:
        list_q = list_q.where(crit)
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({"sales_orders": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 15. submit-sales-order
# ---------------------------------------------------------------------------

def submit_sales_order(conn, args):
    """Confirm a sales order with credit limit check."""
    if not args.sales_order_id:
        err("--sales-order-id is required")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")
    if so["status"] != "draft":
        err(f"Cannot submit: sales order is '{so['status']}' (must be 'draft')")

    so_dict = row_to_dict(so)
    customer_id = so_dict["customer_id"]
    company_id = so_dict["company_id"]
    this_grand_total = to_decimal(so_dict["grand_total"])

    # Verify customer is active
    cq = (Q.from_(_t_customer).select(_t_customer.star)
          .where(_t_customer.id == P()))
    cust = conn.execute(cq.get_sql(), (customer_id,)).fetchone()
    if not cust:
        err(f"Customer {customer_id} not found")
    if cust["status"] != "active":
        err(f"Customer is '{cust['status']}', cannot confirm order")

    # Verify items have qty > 0 and rate > 0
    soiq = (Q.from_(_t_sales_order_item).select(_t_sales_order_item.star)
            .where(_t_sales_order_item.sales_order_id == P()))
    so_items = conn.execute(soiq.get_sql(), (args.sales_order_id,)).fetchall()
    if not so_items:
        err("Sales order has no items")
    for item in so_items:
        if to_decimal(item["quantity"]) <= 0:
            err(f"Item {item['item_id']}: quantity must be > 0")
        if to_decimal(item["rate"]) <= 0:
            err(f"Item {item['item_id']}: rate must be > 0")

    # Credit limit check
    credit_limit = to_decimal(cust["credit_limit"] or "0")
    if credit_limit > 0:
        # raw SQL — decimal_sum with COALESCE and IN clause with arithmetic comparison
        outstanding_row = conn.execute(
            """SELECT COALESCE(decimal_sum(outstanding_amount), '0') as total
               FROM sales_invoice
               WHERE customer_id = ? AND status IN ('submitted', 'overdue', 'partially_paid')
                 AND outstanding_amount + 0 > 0""",
            (customer_id,),
        ).fetchone()
        outstanding = to_decimal(str(outstanding_row["total"]))

        # raw SQL — decimal_sum with COALESCE
        unbilled_row = conn.execute(
            """SELECT COALESCE(decimal_sum(grand_total), '0') as total
               FROM sales_order
               WHERE customer_id = ? AND status = 'confirmed'
                 AND id != ?""",
            (customer_id, args.sales_order_id),
        ).fetchone()
        unconfirmed_orders = to_decimal(str(unbilled_row["total"]))

        total_exposure = outstanding + unconfirmed_orders + this_grand_total
        if total_exposure > credit_limit:
            err(
                f"Customer credit limit of {credit_limit} exceeded. "
                f"Current outstanding: {outstanding}. "
                f"Unbilled orders: {unconfirmed_orders}. "
                f"This order: {this_grand_total}. "
                f"Total exposure: {total_exposure}."
            )

    # Generate naming series
    naming = get_next_name(conn, "sales_order", company_id=company_id)

    uq = (Q.update(_t_sales_order)
          .set("status", ValueWrapper("confirmed"))
          .set("naming_series", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_sales_order.id == P()))
    conn.execute(uq.get_sql(), (naming, args.sales_order_id))

    audit(conn, "erpclaw-selling", "submit-sales-order", "sales_order", args.sales_order_id,
           new_values={"status": "confirmed", "naming_series": naming})
    conn.commit()
    ok({"sales_order_id": args.sales_order_id, "naming_series": naming,
         "status": "confirmed"})


# ---------------------------------------------------------------------------
# 16. cancel-sales-order
# ---------------------------------------------------------------------------

def cancel_sales_order(conn, args):
    """Cancel a sales order (only if no linked deliveries or invoices)."""
    if not args.sales_order_id:
        err("--sales-order-id is required")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")
    if so["status"] == "cancelled":
        err("Sales order is already cancelled")

    # Check for linked delivery notes
    dnc = (Q.from_(_t_delivery_note)
           .select(fn.Count("*").as_("cnt"))
           .where(_t_delivery_note.sales_order_id == P())
           .where(_t_delivery_note.status != ValueWrapper("cancelled")))
    dn_count = conn.execute(dnc.get_sql(), (args.sales_order_id,)).fetchone()["cnt"]
    if dn_count > 0:
        err(f"Cannot cancel: {dn_count} active delivery note(s) linked to this order")

    # Check for linked invoices
    sic = (Q.from_(_t_sales_invoice)
           .select(fn.Count("*").as_("cnt"))
           .where(_t_sales_invoice.sales_order_id == P())
           .where(_t_sales_invoice.status != ValueWrapper("cancelled")))
    si_count = conn.execute(sic.get_sql(), (args.sales_order_id,)).fetchone()["cnt"]
    if si_count > 0:
        err(f"Cannot cancel: {si_count} active sales invoice(s) linked to this order")

    uq = (Q.update(_t_sales_order)
          .set("status", ValueWrapper("cancelled"))
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_sales_order.id == P()))
    conn.execute(uq.get_sql(), (args.sales_order_id,))

    audit(conn, "erpclaw-selling", "cancel-sales-order", "sales_order", args.sales_order_id,
           new_values={"status": "cancelled"})
    conn.commit()
    ok({"sales_order_id": args.sales_order_id, "status": "cancelled"})


# ---------------------------------------------------------------------------
# 17. create-delivery-note
# ---------------------------------------------------------------------------

def create_delivery_note(conn, args):
    """Create a delivery note from a sales order."""
    if not args.sales_order_id:
        err("--sales-order-id is required")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")
    if so["status"] == "closed":
        err("Cannot create DN: sales order is closed")
    if so["status"] not in ("confirmed", "partially_delivered"):
        err(f"Cannot create DN: sales order is '{so['status']}' (must be 'confirmed' or 'partially_delivered')")

    so_dict = row_to_dict(so)
    posting_date = args.posting_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Fetch SO items
    soiq = (Q.from_(_t_sales_order_item).select(_t_sales_order_item.star)
            .where(_t_sales_order_item.sales_order_id == P())
            .orderby(_t_sales_order_item.rowid))
    so_items = conn.execute(soiq.get_sql(), (args.sales_order_id,)).fetchall()
    if not so_items:
        err("Sales order has no items")

    # Determine items to deliver
    items_to_deliver = []
    if args.items:
        # Partial delivery: user specifies which items and how many
        partial_items = _parse_json_arg(args.items, "items")
        if not partial_items or not isinstance(partial_items, list):
            err("--items must be a non-empty JSON array")

        # Build a lookup of SO items
        so_item_map = {}
        for soi in so_items:
            soi_dict = row_to_dict(soi)
            so_item_map[soi_dict["item_id"]] = soi_dict
            so_item_map[soi_dict["id"]] = soi_dict  # also index by SO item ID

        for pi in partial_items:
            item_id = pi.get("item_id")
            so_item_id = pi.get("sales_order_item_id")
            qty = to_decimal(pi.get("qty", "0"))

            if so_item_id and so_item_id in so_item_map:
                soi_dict = so_item_map[so_item_id]
            elif item_id and item_id in so_item_map:
                soi_dict = so_item_map[item_id]
            else:
                err(f"Item {item_id or so_item_id} not found in sales order")

            remaining = to_decimal(soi_dict["quantity"]) - to_decimal(soi_dict["delivered_qty"])
            if qty <= 0:
                err(f"Item {soi_dict['item_id']}: qty must be > 0")
            if qty > remaining:
                err(f"Item {soi_dict['item_id']}: qty {qty} exceeds remaining {remaining}")

            items_to_deliver.append({
                "so_item": soi_dict,
                "qty": qty,
                "warehouse_id": pi.get("warehouse_id") or soi_dict.get("warehouse_id"),
                "batch_id": pi.get("batch_id"),
                "serial_numbers": pi.get("serial_numbers"),
            })
    else:
        # Full delivery: copy all undelivered items
        for soi in so_items:
            soi_dict = row_to_dict(soi)
            remaining = to_decimal(soi_dict["quantity"]) - to_decimal(soi_dict["delivered_qty"])
            if remaining > 0:
                items_to_deliver.append({
                    "so_item": soi_dict,
                    "qty": remaining,
                    "warehouse_id": soi_dict.get("warehouse_id"),
                    "batch_id": None,
                    "serial_numbers": None,
                })

    if not items_to_deliver:
        err("No items to deliver (all items already fully delivered)")

    # Propagate --warehouse-id override to all DN items if provided
    override_warehouse_id = getattr(args, "warehouse_id", None)
    if override_warehouse_id:
        for item in items_to_deliver:
            item["warehouse_id"] = override_warehouse_id

    total_qty = sum(item["qty"] for item in items_to_deliver)
    dn_id = str(uuid.uuid4())

    # Insert parent delivery_note first
    dn_ins = (Q.into(_t_delivery_note)
              .columns("id", "customer_id", "posting_date", "sales_order_id",
                        "status", "total_qty", "company_id")
              .insert(P(), P(), P(), P(), ValueWrapper("draft"), P(), P()))
    conn.execute(dn_ins.get_sql(),
        (dn_id, so_dict["customer_id"], posting_date,
         args.sales_order_id, str(round_currency(total_qty)),
         so_dict["company_id"]),
    )

    # Insert child delivery_note_item rows
    dni_ins = (Q.into(_t_delivery_note_item)
               .columns("id", "delivery_note_id", "item_id", "quantity", "uom",
                         "sales_order_item_id", "warehouse_id", "batch_id",
                         "serial_numbers", "rate", "amount")
               .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    dni_ins_sql = dni_ins.get_sql()
    for item in items_to_deliver:
        soi = item["so_item"]
        conn.execute(dni_ins_sql,
            (str(uuid.uuid4()), dn_id, soi["item_id"],
             str(round_currency(item["qty"])), soi.get("uom"),
             soi["id"], item["warehouse_id"], item["batch_id"],
             item["serial_numbers"], soi["rate"],
             str(round_currency(item["qty"] * to_decimal(soi["rate"])))),
        )

    audit(conn, "erpclaw-selling", "create-delivery-note", "delivery_note", dn_id,
           new_values={"sales_order_id": args.sales_order_id,
                       "item_count": len(items_to_deliver)})
    conn.commit()
    ok({"delivery_note_id": dn_id, "sales_order_id": args.sales_order_id,
         "total_qty": str(round_currency(total_qty)),
         "item_count": len(items_to_deliver)})


# ---------------------------------------------------------------------------
# 18. get-delivery-note
# ---------------------------------------------------------------------------

def get_delivery_note(conn, args):
    """Get delivery note with items."""
    if not args.delivery_note_id:
        err("--delivery-note-id is required")

    dnq = (Q.from_(_t_delivery_note).select(_t_delivery_note.star)
           .where(_t_delivery_note.id == P()))
    dn = conn.execute(dnq.get_sql(), (args.delivery_note_id,)).fetchone()
    if not dn:
        err(f"Delivery note {args.delivery_note_id} not found")

    data = row_to_dict(dn)

    dni = _t_delivery_note_item.as_("dni")
    i = _t_item.as_("i")
    items_q = (Q.from_(dni)
               .left_join(i).on(i.id == dni.item_id)
               .select(dni.star, i.item_name, i.item_code)
               .where(dni.delivery_note_id == P())
               .orderby(dni.rowid))
    items = conn.execute(items_q.get_sql(), (args.delivery_note_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]
    ok(data)


# ---------------------------------------------------------------------------
# 19. list-delivery-notes
# ---------------------------------------------------------------------------

def list_delivery_notes(conn, args):
    """Query delivery notes with filtering."""
    dn = _t_delivery_note.as_("dn")
    c = _t_customer.as_("c")
    params = []
    crit = None

    if args.company_id:
        crit = (dn.company_id == P())
        params.append(args.company_id)
    if args.customer_id:
        cond = dn.customer_id == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.customer_id)
    if args.doc_status:
        cond = dn.status == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.doc_status)
    if args.from_date:
        cond = dn.posting_date >= P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.from_date)
    if args.to_date:
        cond = dn.posting_date <= P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.to_date)

    count_q = Q.from_(dn).select(fn.Count("*"))
    if crit:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(dn)
              .left_join(c).on(c.id == dn.customer_id)
              .select(dn.id, dn.naming_series, dn.customer_id,
                      c.name.as_("customer_name"),
                      dn.posting_date,
                      dn.sales_order_id, dn.status, dn.total_qty, dn.company_id)
              .orderby(dn.posting_date, order=Order.desc)
              .orderby(dn.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    if crit:
        list_q = list_q.where(crit)
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({"delivery_notes": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 20. submit-delivery-note
# ---------------------------------------------------------------------------

def submit_delivery_note(conn, args):
    """Submit a delivery note: creates SLE + COGS GL entries."""
    if not args.delivery_note_id:
        err("--delivery-note-id is required")

    dnq = (Q.from_(_t_delivery_note).select(_t_delivery_note.star)
           .where(_t_delivery_note.id == P()))
    dn = conn.execute(dnq.get_sql(), (args.delivery_note_id,)).fetchone()
    if not dn:
        err(f"Delivery note {args.delivery_note_id} not found")
    if dn["status"] != "draft":
        err(f"Cannot submit: delivery note is '{dn['status']}' (must be 'draft')")

    dn_dict = row_to_dict(dn)
    company_id = dn_dict["company_id"]
    posting_date = dn_dict["posting_date"]

    # Verify linked SO is not cancelled
    if dn_dict.get("sales_order_id"):
        soq = (Q.from_(_t_sales_order).select(_t_sales_order.status)
               .where(_t_sales_order.id == P()))
        so = conn.execute(soq.get_sql(), (dn_dict["sales_order_id"],)).fetchone()
        if so and so["status"] == "cancelled":
            err("Cannot submit: linked sales order is cancelled")

    # Fetch DN items
    dniq = (Q.from_(_t_delivery_note_item).select(_t_delivery_note_item.star)
            .where(_t_delivery_note_item.delivery_note_id == P())
            .orderby(_t_delivery_note_item.rowid))
    dn_items = conn.execute(dniq.get_sql(), (args.delivery_note_id,)).fetchall()
    if not dn_items:
        err("Delivery note has no items")

    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, company_id)
    cogs_account_id = _get_cogs_account(conn, company_id)

    # Build SLE entries (negative qty from warehouse)
    sle_entries = []
    for dni in dn_items:
        dni_dict = row_to_dict(dni)
        qty = to_decimal(dni_dict["quantity"])

        # Skip warehouse validation for service items
        item_row = conn.execute("SELECT item_type FROM item WHERE id = ?", (dni_dict["item_id"],)).fetchone()
        if item_row and item_row["item_type"] == "service":
            continue

        warehouse_id = dni_dict.get("warehouse_id")
        if not warehouse_id:
            # Try to get default warehouse from company
            cwq = (Q.from_(_t_company).select(_t_company.default_warehouse_id)
                   .where(_t_company.id == P()))
            comp = conn.execute(cwq.get_sql(), (company_id,)).fetchone()
            warehouse_id = comp["default_warehouse_id"] if comp else None
        if not warehouse_id:
            err(f"No warehouse specified for item {dni_dict['item_id']} and no default warehouse")

        # B8: Validate warehouse type — only dispatch from stores warehouses
        wh_type_row = conn.execute(
            "SELECT warehouse_type FROM warehouse WHERE id = ?", (warehouse_id,)
        ).fetchone()
        if wh_type_row and wh_type_row["warehouse_type"] not in ("stores",):
            err(f"Cannot dispatch from '{wh_type_row['warehouse_type']}' warehouse. Use a 'stores' warehouse.")

        sle_entries.append({
            "item_id": dni_dict["item_id"],
            "warehouse_id": warehouse_id,
            "actual_qty": str(round_currency(-qty)),
            "incoming_rate": "0",
            "batch_id": dni_dict.get("batch_id"),
            "serial_number": dni_dict.get("serial_numbers"),
            "fiscal_year": fiscal_year,
        })

    # Insert SLE entries
    try:
        sle_ids = insert_sle_entries(
            conn, sle_entries,
            voucher_type="delivery_note",
            voucher_id=args.delivery_note_id,
            posting_date=posting_date,
            company_id=company_id,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-selling] {e}\n")
        err(f"SLE posting failed: {e}")

    # B12: Update serial number status to 'delivered'
    for dni in dn_items:
        dni_d = row_to_dict(dni)
        serial_nums = dni_d.get("serial_numbers")
        if serial_nums:
            for sn in serial_nums.split("\n"):
                sn = sn.strip()
                if sn:
                    conn.execute(
                        """UPDATE serial_number
                           SET status = 'delivered',
                               delivery_document_type = 'delivery_note',
                               delivery_document_id = ?,
                               customer_id = ?,
                               warehouse_id = NULL
                           WHERE serial_no = ?""",
                        (args.delivery_note_id, dn_dict["customer_id"], sn),
                    )

    # Build COGS GL entries from SLE data
    sleq = (Q.from_(_t_stock_ledger).select(_t_stock_ledger.star)
            .where(_t_stock_ledger.voucher_type == ValueWrapper("delivery_note"))
            .where(_t_stock_ledger.voucher_id == P())
            .where(_t_stock_ledger.is_cancelled == 0))
    sle_rows = conn.execute(sleq.get_sql(), (args.delivery_note_id,)).fetchall()
    sle_dicts = [row_to_dict(r) for r in sle_rows]

    gl_entries = create_perpetual_inventory_gl(
        conn, sle_dicts,
        voucher_type="delivery_note",
        voucher_id=args.delivery_note_id,
        posting_date=posting_date,
        company_id=company_id,
        expense_account_id=cogs_account_id,
        cost_center_id=cost_center_id,
    )

    gl_ids = []
    if gl_entries:
        for gle in gl_entries:
            gle["fiscal_year"] = fiscal_year
        try:
            gl_ids = insert_gl_entries(
                conn, gl_entries,
                voucher_type="delivery_note",
                voucher_id=args.delivery_note_id,
                posting_date=posting_date,
                company_id=company_id,
                remarks=f"Delivery Note {dn_dict.get('naming_series', args.delivery_note_id)}",
            )
        except ValueError as e:
            sys.stderr.write(f"[erpclaw-selling] {e}\n")
            err(f"GL posting failed: {e}")

    # Generate naming series
    naming = get_next_name(conn, "delivery_note", company_id=company_id)

    # Update DN status
    uq = (Q.update(_t_delivery_note)
          .set("status", ValueWrapper("submitted"))
          .set("naming_series", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_delivery_note.id == P()))
    conn.execute(uq.get_sql(), (naming, args.delivery_note_id))

    # Update SO delivered_qty
    if dn_dict.get("sales_order_id"):
        for dni in dn_items:
            dni_dict = row_to_dict(dni)
            if dni_dict.get("sales_order_item_id"):
                # raw SQL — CAST with arithmetic on TEXT column
                conn.execute(
                    """UPDATE sales_order_item
                       SET delivered_qty = CAST(
                           delivered_qty + 0 + ?
                       AS TEXT)
                       WHERE id = ?""",
                    (dni_dict["quantity"], dni_dict["sales_order_item_id"]),
                )

        # Recalculate SO per_delivered and status
        _update_so_delivery_status(conn, dn_dict["sales_order_id"])

    audit(conn, "erpclaw-selling", "submit-delivery-note", "delivery_note", args.delivery_note_id,
           new_values={"sle_count": len(sle_ids), "gl_count": len(gl_ids),
                       "naming_series": naming})
    conn.commit()
    ok({"delivery_note_id": args.delivery_note_id, "naming_series": naming,
         "status": "submitted", "sle_entries_created": len(sle_ids),
         "gl_entries_created": len(gl_ids)})


def _update_so_delivery_status(conn, sales_order_id: str):
    """Recalculate SO per_delivered and update status accordingly."""
    q = (Q.from_(_t_sales_order_item)
         .select(_t_sales_order_item.quantity, _t_sales_order_item.delivered_qty)
         .where(_t_sales_order_item.sales_order_id == P()))
    items = conn.execute(q.get_sql(), (sales_order_id,)).fetchall()

    total_qty = Decimal("0")
    total_delivered = Decimal("0")
    for item in items:
        total_qty += to_decimal(item["quantity"])
        total_delivered += to_decimal(item["delivered_qty"])

    if total_qty > 0:
        per_delivered = round_currency(total_delivered / total_qty * Decimal("100"))
    else:
        per_delivered = Decimal("0")

    if per_delivered >= Decimal("100"):
        new_status = "fully_delivered"
    elif per_delivered > 0:
        new_status = "partially_delivered"
    else:
        return  # No change needed

    uq = (Q.update(_t_sales_order)
          .set("per_delivered", P())
          .set("status", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_sales_order.id == P()))
    conn.execute(uq.get_sql(), (str(per_delivered), new_status, sales_order_id))


# ---------------------------------------------------------------------------
# 21. cancel-delivery-note
# ---------------------------------------------------------------------------

def cancel_delivery_note(conn, args):
    """Cancel a delivery note: reverse SLE + GL, update SO delivered_qty."""
    if not args.delivery_note_id:
        err("--delivery-note-id is required")

    dnq = (Q.from_(_t_delivery_note).select(_t_delivery_note.star)
           .where(_t_delivery_note.id == P()))
    dn = conn.execute(dnq.get_sql(), (args.delivery_note_id,)).fetchone()
    if not dn:
        err(f"Delivery note {args.delivery_note_id} not found")
    if dn["status"] != "submitted":
        err(f"Cannot cancel: delivery note is '{dn['status']}' (must be 'submitted')")

    dn_dict = row_to_dict(dn)
    posting_date = dn_dict["posting_date"]

    # Check no invoices reference this DN
    sic = (Q.from_(_t_sales_invoice)
           .select(fn.Count("*").as_("cnt"))
           .where(_t_sales_invoice.delivery_note_id == P())
           .where(_t_sales_invoice.status != ValueWrapper("cancelled")))
    si_count = conn.execute(sic.get_sql(), (args.delivery_note_id,)).fetchone()["cnt"]
    if si_count > 0:
        err(f"Cannot cancel: {si_count} active invoice(s) reference this delivery note")

    # Reverse SLE entries
    try:
        reversal_sle_ids = reverse_sle_entries(
            conn,
            voucher_type="delivery_note",
            voucher_id=args.delivery_note_id,
            posting_date=posting_date,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-selling] {e}\n")
        err(f"SLE reversal failed: {e}")

    # Reverse GL entries
    reversal_gl_ids = []
    try:
        reversal_gl_ids = reverse_gl_entries(
            conn,
            voucher_type="delivery_note",
            voucher_id=args.delivery_note_id,
            posting_date=posting_date,
        )
    except ValueError:
        reversal_gl_ids = []

    # Update DN status
    uq = (Q.update(_t_delivery_note)
          .set("status", ValueWrapper("cancelled"))
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_delivery_note.id == P()))
    conn.execute(uq.get_sql(), (args.delivery_note_id,))

    # Reverse SO delivered_qty
    if dn_dict.get("sales_order_id"):
        dniq = (Q.from_(_t_delivery_note_item).select(_t_delivery_note_item.star)
                .where(_t_delivery_note_item.delivery_note_id == P()))
        dn_items = conn.execute(dniq.get_sql(), (args.delivery_note_id,)).fetchall()
        for dni in dn_items:
            dni_dict = row_to_dict(dni)
            if dni_dict.get("sales_order_item_id"):
                # raw SQL — CAST with MAX and arithmetic on TEXT column
                conn.execute(
                    """UPDATE sales_order_item
                       SET delivered_qty = CAST(
                           MAX(delivered_qty + 0 - ?, 0)
                       AS TEXT)
                       WHERE id = ?""",
                    (dni_dict["quantity"], dni_dict["sales_order_item_id"]),
                )

        # Recalculate SO delivery status
        _update_so_delivery_status_after_cancel(conn, dn_dict["sales_order_id"])

    audit(conn, "erpclaw-selling", "cancel-delivery-note", "delivery_note", args.delivery_note_id,
           new_values={"reversed": True})
    conn.commit()
    ok({"delivery_note_id": args.delivery_note_id, "status": "cancelled",
         "sle_reversals": len(reversal_sle_ids),
         "gl_reversals": len(reversal_gl_ids)})


def _update_so_delivery_status_after_cancel(conn, sales_order_id: str):
    """Recalculate SO delivery status after a DN cancellation."""
    q = (Q.from_(_t_sales_order_item)
         .select(_t_sales_order_item.quantity, _t_sales_order_item.delivered_qty)
         .where(_t_sales_order_item.sales_order_id == P()))
    items = conn.execute(q.get_sql(), (sales_order_id,)).fetchall()

    total_qty = Decimal("0")
    total_delivered = Decimal("0")
    for item in items:
        total_qty += to_decimal(item["quantity"])
        total_delivered += to_decimal(item["delivered_qty"])

    if total_qty > 0:
        per_delivered = round_currency(total_delivered / total_qty * Decimal("100"))
    else:
        per_delivered = Decimal("0")

    if per_delivered >= Decimal("100"):
        new_status = "fully_delivered"
    elif per_delivered > 0:
        new_status = "partially_delivered"
    else:
        new_status = "confirmed"

    uq = (Q.update(_t_sales_order)
          .set("per_delivered", P())
          .set("status", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_sales_order.id == P()))
    conn.execute(uq.get_sql(), (str(per_delivered), new_status, sales_order_id))


# ---------------------------------------------------------------------------
# 22. create-sales-invoice
# ---------------------------------------------------------------------------

def create_sales_invoice(conn, args):
    """Create a sales invoice from SO, DN, or standalone."""
    company_id = args.company_id
    customer_id = args.customer_id
    tax_template_id = args.tax_template_id
    sales_order_id = args.sales_order_id
    delivery_note_id = args.delivery_note_id
    posting_date = args.posting_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    update_stock = 1  # Default for US perpetual inventory

    if sales_order_id:
        # Create from Sales Order
        soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
               .where(_t_sales_order.id == P()))
        so = conn.execute(soq.get_sql(), (sales_order_id,)).fetchone()
        if not so:
            err(f"Sales order {sales_order_id} not found")
        if so["status"] == "closed":
            err("Cannot invoice: sales order is closed")
        if so["status"] not in ("confirmed", "partially_delivered", "fully_delivered",
                                 "partially_invoiced"):
            err(f"Cannot invoice: sales order is '{so['status']}'")

        so_dict = row_to_dict(so)
        customer_id = so_dict["customer_id"]
        company_id = so_dict["company_id"]
        tax_template_id = tax_template_id or so_dict.get("tax_template_id")
        payment_terms_id = so_dict.get("payment_terms_id")

        # If SO has delivery notes, set update_stock=0 (stock already moved)
        dnc = (Q.from_(_t_delivery_note)
               .select(fn.Count("*").as_("cnt"))
               .where(_t_delivery_note.sales_order_id == P())
               .where(_t_delivery_note.status == ValueWrapper("submitted")))
        dn_count = conn.execute(dnc.get_sql(), (sales_order_id,)).fetchone()["cnt"]
        if dn_count > 0:
            update_stock = 0

        soiq = (Q.from_(_t_sales_order_item).select(_t_sales_order_item.star)
                .where(_t_sales_order_item.sales_order_id == P())
                .orderby(_t_sales_order_item.rowid))
        so_items = conn.execute(soiq.get_sql(), (sales_order_id,)).fetchall()

        si_items_data = []
        total_amount = Decimal("0")
        for soi in so_items:
            soi_dict = row_to_dict(soi)
            remaining = to_decimal(soi_dict["quantity"]) - to_decimal(soi_dict.get("invoiced_qty", "0"))
            if remaining <= 0:
                continue
            net = round_currency(remaining * to_decimal(soi_dict["rate"]))
            total_amount += net
            si_items_data.append({
                "item_id": soi_dict["item_id"],
                "qty": str(round_currency(remaining)),
                "uom": soi_dict.get("uom"),
                "rate": soi_dict["rate"],
                "amount": str(round_currency(remaining * to_decimal(soi_dict["rate"]))),
                "discount_percentage": soi_dict.get("discount_percentage", "0"),
                "net_amount": str(net),
                "sales_order_item_id": soi_dict["id"],
                "warehouse_id": soi_dict.get("warehouse_id"),
            })

        if not si_items_data:
            err("No uninvoiced items in sales order")

    elif delivery_note_id:
        # Create from Delivery Note
        dnq = (Q.from_(_t_delivery_note).select(_t_delivery_note.star)
               .where(_t_delivery_note.id == P()))
        dn = conn.execute(dnq.get_sql(), (delivery_note_id,)).fetchone()
        if not dn:
            err(f"Delivery note {delivery_note_id} not found")
        if dn["status"] != "submitted":
            err(f"Cannot invoice: delivery note is '{dn['status']}'")

        dn_dict = row_to_dict(dn)
        customer_id = dn_dict["customer_id"]
        company_id = dn_dict["company_id"]
        sales_order_id = dn_dict.get("sales_order_id")
        update_stock = 0  # Stock already moved by DN

        dniq = (Q.from_(_t_delivery_note_item).select(_t_delivery_note_item.star)
                .where(_t_delivery_note_item.delivery_note_id == P())
                .orderby(_t_delivery_note_item.rowid))
        dn_items = conn.execute(dniq.get_sql(), (delivery_note_id,)).fetchall()

        si_items_data = []
        total_amount = Decimal("0")
        for dni in dn_items:
            dni_dict = row_to_dict(dni)
            qty = to_decimal(dni_dict["quantity"])
            rate = to_decimal(dni_dict["rate"])
            net = round_currency(qty * rate)
            total_amount += net
            si_items_data.append({
                "item_id": dni_dict["item_id"],
                "qty": str(round_currency(qty)),
                "uom": dni_dict.get("uom"),
                "rate": str(round_currency(rate)),
                "amount": str(round_currency(qty * rate)),
                "discount_percentage": "0",
                "net_amount": str(net),
                "sales_order_item_id": dni_dict.get("sales_order_item_id"),
                "delivery_note_item_id": dni_dict["id"],
                "warehouse_id": dni_dict.get("warehouse_id"),
            })

    else:
        # Standalone invoice
        if not customer_id:
            err("--customer-id is required for standalone invoices")
        if not args.items:
            err("--items is required for standalone invoices")
        if not company_id:
            err("--company-id is required for standalone invoices")

        cchk = (Q.from_(_t_customer).select(_t_customer.id)
                .where((_t_customer.id == P()) | (_t_customer.name == P()))
                .where(_t_customer.status == ValueWrapper("active")))
        cust_chk = conn.execute(cchk.get_sql(), (customer_id, customer_id)).fetchone()
        if not cust_chk:
            err(f"Active customer {customer_id} not found")
        customer_id = cust_chk["id"]  # normalize to id

        items = _parse_json_arg(args.items, "items")
        total_amount, item_rows = _calculate_line_items(
            conn, items, company_id, customer_id, posting_date)

        si_items_data = []
        for row in item_rows:
            si_items_data.append({
                "item_id": row["item_id"],
                "qty": row["qty"],
                "uom": row["uom"],
                "rate": row["rate"],
                "amount": row["amount"],
                "discount_percentage": row["discount_percentage"],
                "net_amount": row["net_amount"],
                "sales_order_item_id": None,
                "delivery_note_item_id": None,
                "warehouse_id": row["warehouse_id"],
            })

    # Calculate tax
    total_amount = round_currency(total_amount)
    tax_amount, tax_lines = _calculate_tax(conn, total_amount, tax_template_id)
    grand_total = round_currency(total_amount + tax_amount)

    # Resolve payment_terms_id: SO sets it above; fallback to customer default
    try:
        payment_terms_id  # set in SO code path
    except NameError:
        payment_terms_id = getattr(args, 'payment_terms_id', None)
        if not payment_terms_id and customer_id:
            cpq = (Q.from_(_t_customer).select(_t_customer.payment_terms_id)
                   .where(_t_customer.id == P()))
            cust = conn.execute(cpq.get_sql(), (customer_id,)).fetchone()
            if cust:
                payment_terms_id = cust["payment_terms_id"]

    # Calculate due date from payment terms or default +30 days
    due_date = args.due_date
    if not due_date:
        due_days = 30
        if payment_terms_id:
            ptq = (Q.from_(_t_payment_terms).select(_t_payment_terms.due_days)
                   .where(_t_payment_terms.id == P()))
            pt = conn.execute(ptq.get_sql(), (payment_terms_id,)).fetchone()
            if pt and pt["due_days"]:
                due_days = pt["due_days"]
        parts = posting_date.split("-")
        d = date_type(int(parts[0]), int(parts[1]), int(parts[2]))
        due_date = (d + timedelta(days=due_days)).isoformat()

    si_id = str(uuid.uuid4())

    # Insert parent sales_invoice first
    si_ins = (Q.into(_t_sales_invoice)
              .columns("id", "customer_id", "posting_date", "due_date",
                        "total_amount", "tax_amount", "grand_total",
                        "outstanding_amount", "tax_template_id",
                        "payment_terms_id", "status", "sales_order_id",
                        "delivery_note_id", "update_stock", "company_id")
              .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(),
                      ValueWrapper("draft"), P(), P(), P(), P()))
    conn.execute(si_ins.get_sql(),
        (si_id, customer_id, posting_date, due_date,
         str(total_amount), str(tax_amount), str(grand_total), str(grand_total),
         tax_template_id, payment_terms_id, sales_order_id, delivery_note_id,
         update_stock, company_id),
    )

    # Insert child sales_invoice_item rows
    sii_ins = (Q.into(_t_sales_invoice_item)
               .columns("id", "sales_invoice_id", "item_id", "quantity", "uom",
                         "rate", "amount", "discount_percentage", "net_amount",
                         "sales_order_item_id", "delivery_note_item_id")
               .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    sii_ins_sql = sii_ins.get_sql()
    for row in si_items_data:
        conn.execute(sii_ins_sql,
            (str(uuid.uuid4()), si_id, row["item_id"], row["qty"],
             row["uom"], row["rate"], row["amount"],
             row["discount_percentage"], row["net_amount"],
             row.get("sales_order_item_id"), row.get("delivery_note_item_id")),
        )

    audit(conn, "erpclaw-selling", "create-sales-invoice", "sales_invoice", si_id,
           new_values={"customer_id": customer_id, "grand_total": str(grand_total),
                       "update_stock": update_stock})
    conn.commit()
    ok({"sales_invoice_id": si_id, "total_amount": str(total_amount),
         "tax_amount": str(tax_amount), "grand_total": str(grand_total),
         "update_stock": update_stock})


# ---------------------------------------------------------------------------
# 23. update-sales-invoice
# ---------------------------------------------------------------------------

def update_sales_invoice(conn, args):
    """Update a draft sales invoice."""
    if not args.sales_invoice_id:
        err("--sales-invoice-id is required")

    siq = (Q.from_(_t_sales_invoice).select(_t_sales_invoice.star)
           .where(_t_sales_invoice.id == P()))
    si = conn.execute(siq.get_sql(), (args.sales_invoice_id,)).fetchone()
    if not si:
        err(f"Sales invoice {args.sales_invoice_id} not found")
    if si["status"] != "draft":
        err(f"Cannot update: sales invoice is '{si['status']}' (must be 'draft')",
             suggestion="Cancel the document first, then make changes.")

    updated_fields = []

    if args.due_date is not None:
        uq = (Q.update(_t_sales_invoice)
              .set("due_date", P())
              .set("updated_at", LiteralValue("datetime('now')"))
              .where(_t_sales_invoice.id == P()))
        conn.execute(uq.get_sql(), (args.due_date, args.sales_invoice_id))
        updated_fields.append("due_date")

    if args.items:
        items = _parse_json_arg(args.items, "items")
        total_amount, item_rows = _calculate_line_items(
            conn, items, si["company_id"])

        tax_amount, _ = _calculate_tax(conn, total_amount, si["tax_template_id"])
        grand_total = round_currency(total_amount + tax_amount)

        dq = Q.from_(_t_sales_invoice_item).delete().where(_t_sales_invoice_item.sales_invoice_id == P())
        conn.execute(dq.get_sql(), (args.sales_invoice_id,))
        sii_ins = (Q.into(_t_sales_invoice_item)
                   .columns("id", "sales_invoice_id", "item_id", "quantity",
                             "uom", "rate", "amount", "discount_percentage",
                             "net_amount")
                   .insert(P(), P(), P(), P(), P(), P(), P(), P(), P()))
        sii_ins_sql = sii_ins.get_sql()
        for row in item_rows:
            conn.execute(sii_ins_sql,
                (str(uuid.uuid4()), args.sales_invoice_id, row["item_id"],
                 row["qty"], row["uom"], row["rate"], row["amount"],
                 row["discount_percentage"], row["net_amount"]),
            )

        uq2 = (Q.update(_t_sales_invoice)
               .set("total_amount", P())
               .set("tax_amount", P())
               .set("grand_total", P())
               .set("outstanding_amount", P())
               .set("updated_at", LiteralValue("datetime('now')"))
               .where(_t_sales_invoice.id == P()))
        conn.execute(uq2.get_sql(),
            (str(total_amount), str(tax_amount), str(grand_total),
             str(grand_total), args.sales_invoice_id),
        )
        updated_fields.extend(["items", "total_amount", "tax_amount", "grand_total"])

    if not updated_fields:
        err("No fields to update")

    audit(conn, "erpclaw-selling", "update-sales-invoice", "sales_invoice", args.sales_invoice_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"sales_invoice_id": args.sales_invoice_id,
         "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 24. get-sales-invoice
# ---------------------------------------------------------------------------

def get_sales_invoice(conn, args):
    """Get sales invoice with items and payment info."""
    if not args.sales_invoice_id:
        err("--sales-invoice-id is required")

    siq = (Q.from_(_t_sales_invoice).select(_t_sales_invoice.star)
           .where(_t_sales_invoice.id == P()))
    si = conn.execute(siq.get_sql(), (args.sales_invoice_id,)).fetchone()
    if not si:
        err(f"Sales invoice {args.sales_invoice_id} not found")

    data = row_to_dict(si)

    sii = _t_sales_invoice_item.as_("sii")
    i = _t_item.as_("i")
    items_q = (Q.from_(sii)
               .left_join(i).on(i.id == sii.item_id)
               .select(sii.star, i.item_name, i.item_code)
               .where(sii.sales_invoice_id == P())
               .orderby(sii.rowid))
    items = conn.execute(items_q.get_sql(), (args.sales_invoice_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    # Payment ledger entries (match both sales_invoice and credit_note voucher types)
    pleq = (Q.from_(_t_payment_ledger).select(_t_payment_ledger.star)
            .where(_t_payment_ledger.against_voucher_type.isin([
                ValueWrapper("sales_invoice"), ValueWrapper("credit_note")]))
            .where(_t_payment_ledger.against_voucher_id == P()))
    ple_rows = conn.execute(pleq.get_sql(), (args.sales_invoice_id,)).fetchall()
    data["payments"] = [row_to_dict(r) for r in ple_rows]

    ok(data)


# ---------------------------------------------------------------------------
# 25. list-sales-invoices
# ---------------------------------------------------------------------------

def list_sales_invoices(conn, args):
    """Query sales invoices with filtering."""
    si = _t_sales_invoice.as_("si")
    c = _t_customer.as_("c")
    params = []
    crit = None

    if args.company_id:
        crit = (si.company_id == P())
        params.append(args.company_id)
    if args.customer_id:
        cond = si.customer_id == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.customer_id)
    if args.doc_status:
        cond = si.status == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.doc_status)
    if args.from_date:
        cond = si.posting_date >= P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.from_date)
    if args.to_date:
        cond = si.posting_date <= P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.to_date)

    count_q = Q.from_(si).select(fn.Count("*"))
    if crit:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(si)
              .left_join(c).on(c.id == si.customer_id)
              .select(si.id, si.naming_series, si.customer_id,
                      c.name.as_("customer_name"),
                      si.posting_date, si.due_date, si.grand_total,
                      si.outstanding_amount, si.status, si.is_return, si.company_id)
              .orderby(si.posting_date, order=Order.desc)
              .orderby(si.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    if crit:
        list_q = list_q.where(crit)
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({"sales_invoices": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 26. submit-sales-invoice
# ---------------------------------------------------------------------------

def submit_sales_invoice(conn, args):
    """Submit a sales invoice: revenue GL + PLE (+ optional SLE)."""
    if not args.sales_invoice_id:
        err("--sales-invoice-id is required")

    siq = (Q.from_(_t_sales_invoice).select(_t_sales_invoice.star)
           .where(_t_sales_invoice.id == P()))
    si = conn.execute(siq.get_sql(), (args.sales_invoice_id,)).fetchone()
    if not si:
        err(f"Sales invoice {args.sales_invoice_id} not found")
    if si["status"] != "draft":
        err(f"Cannot submit: sales invoice is '{si['status']}' (must be 'draft')")

    si_dict = row_to_dict(si)
    company_id = si_dict["company_id"]
    customer_id = si_dict["customer_id"]
    posting_date = si_dict["posting_date"]
    grand_total = to_decimal(si_dict["grand_total"])
    total_amount = to_decimal(si_dict["total_amount"])
    tax_amount = to_decimal(si_dict["tax_amount"])
    update_stock = si_dict.get("update_stock", 1)

    # Verify customer is active
    cq = (Q.from_(_t_customer).select(_t_customer.star)
          .where(_t_customer.id == P()))
    cust = conn.execute(cq.get_sql(), (customer_id,)).fetchone()
    if not cust:
        err(f"Customer {customer_id} not found")
    if cust["status"] != "active":
        err(f"Customer is '{cust['status']}', cannot submit invoice")

    # Verify items
    siiq = (Q.from_(_t_sales_invoice_item).select(_t_sales_invoice_item.star)
            .where(_t_sales_invoice_item.sales_invoice_id == P()))
    si_items = conn.execute(siiq.get_sql(), (args.sales_invoice_id,)).fetchall()
    if not si_items:
        err("Sales invoice has no items")

    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, company_id)

    # Collect project_ids from invoice items for GL propagation
    item_project_ids = []
    for sii in si_items:
        sii_d = row_to_dict(sii)
        item_project_ids.append(sii_d.get("project_id"))
    # For aggregate GL entries: use first item's project_id if all items share
    # the same project, otherwise None (mixed projects)
    unique_projects = set(p for p in item_project_ids if p)
    aggregate_project_id = list(unique_projects)[0] if len(unique_projects) == 1 else None

    # --- Revenue GL entries ---
    receivable_account_id = _get_receivable_account(conn, company_id)
    if not receivable_account_id:
        err("No receivable account found for company")
    income_account_id = _get_income_account(conn, company_id)
    if not income_account_id:
        err("No income account found for company")

    gl_entries = []

    # DR: Accounts Receivable (with party)
    is_return = bool(si_dict.get("is_return", 0))
    voucher_type = "credit_note" if is_return else "sales_invoice"

    # For credit notes, amounts are stored as negatives -- use abs() and swap DR/CR
    abs_grand_total = abs(grand_total)
    abs_total_amount = abs(total_amount)
    abs_tax_amount = abs(tax_amount)

    if is_return:
        # Credit note: CR Receivable (reverse the original DR)
        gl_entries.append({
            "account_id": receivable_account_id,
            "debit": "0",
            "credit": str(round_currency(abs_grand_total)),
            "party_type": "customer",
            "party_id": customer_id,
            "project_id": aggregate_project_id,
        })
    else:
        gl_entries.append({
            "account_id": receivable_account_id,
            "debit": str(round_currency(abs_grand_total)),
            "credit": "0",
            "party_type": "customer",
            "party_id": customer_id,
            "project_id": aggregate_project_id,
        })

    # CR: Revenue (for credit notes: DR Revenue to reverse)
    if is_return:
        gl_entries.append({
            "account_id": income_account_id,
            "debit": str(round_currency(abs_total_amount)),
            "credit": "0",
            "cost_center_id": cost_center_id,
            "project_id": aggregate_project_id,
        })
    else:
        gl_entries.append({
            "account_id": income_account_id,
            "debit": "0",
            "credit": str(round_currency(abs_total_amount)),
            "cost_center_id": cost_center_id,
            "project_id": aggregate_project_id,
        })

    # CR: Tax Payable (if tax exists) — for returns, use abs() and DR (reverse)
    if abs_tax_amount > 0:
        _, tax_lines = _calculate_tax(conn, abs_total_amount, si_dict.get("tax_template_id"))
        for tl in tax_lines:
            amt = abs(tl["amount"])
            if amt > 0:
                if is_return:
                    gl_entries.append({
                        "account_id": tl["account_id"],
                        "debit": str(round_currency(amt)),
                        "credit": "0",
                        "cost_center_id": cost_center_id,
                        "project_id": aggregate_project_id,
                    })
                else:
                    gl_entries.append({
                        "account_id": tl["account_id"],
                        "debit": "0",
                        "credit": str(round_currency(amt)),
                        "cost_center_id": cost_center_id,
                        "project_id": aggregate_project_id,
                    })

    # Generate naming series early so GL remarks include the human-readable name
    if is_return:
        naming = get_next_name(conn, "credit_note", company_id=company_id)
    else:
        naming = get_next_name(conn, "sales_invoice", company_id=company_id)

    # Add fiscal_year to all GL entries
    for gle in gl_entries:
        gle["fiscal_year"] = fiscal_year

    try:
        gl_ids = insert_gl_entries(
            conn, gl_entries,
            voucher_type=voucher_type,
            voucher_id=args.sales_invoice_id,
            posting_date=posting_date,
            company_id=company_id,
            remarks=f"{'Credit Note' if is_return else 'Sales Invoice'} {naming or args.sales_invoice_id}",
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-selling] {e}\n")
        err(f"GL posting failed: {e}")

    # --- Optional SLE + COGS GL (if update_stock = 1) ---
    sle_ids = []
    cogs_gl_ids = []
    if update_stock:
        cogs_account_id = _get_cogs_account(conn, company_id)
        sle_entries = []
        for sii in si_items:
            sii_dict = row_to_dict(sii)
            qty = abs(to_decimal(sii_dict["quantity"]))
            if qty <= 0:
                continue

            # Determine warehouse
            warehouse_id = None
            if sii_dict.get("sales_order_item_id"):
                soiwq = (Q.from_(_t_sales_order_item)
                         .select(_t_sales_order_item.warehouse_id)
                         .where(_t_sales_order_item.id == P()))
                soi = conn.execute(soiwq.get_sql(),
                    (sii_dict["sales_order_item_id"],)).fetchone()
                if soi and soi["warehouse_id"]:
                    warehouse_id = soi["warehouse_id"]
            if not warehouse_id:
                cwq = (Q.from_(_t_company)
                       .select(_t_company.default_warehouse_id)
                       .where(_t_company.id == P()))
                comp = conn.execute(cwq.get_sql(), (company_id,)).fetchone()
                warehouse_id = comp["default_warehouse_id"] if comp else None

            if not warehouse_id:
                continue

            # Check if item is a stock item
            itq = (Q.from_(_t_item).select(_t_item.is_stock_item)
                   .where(_t_item.id == P()))
            item_row = conn.execute(itq.get_sql(),
                (sii_dict["item_id"],)).fetchone()
            if not item_row or not item_row["is_stock_item"]:
                continue

            sle_entries.append({
                "item_id": sii_dict["item_id"],
                "warehouse_id": warehouse_id,
                "actual_qty": str(round_currency(-qty if not is_return else qty)),
                "incoming_rate": "0" if not is_return else str(round_currency(to_decimal(sii_dict["rate"]))),
                "fiscal_year": fiscal_year,
                "project_id": sii_dict.get("project_id"),
            })

        if sle_entries:
            try:
                sle_ids = insert_sle_entries(
                    conn, sle_entries,
                    voucher_type=voucher_type,
                    voucher_id=args.sales_invoice_id,
                    posting_date=posting_date,
                    company_id=company_id,
                )
            except ValueError as e:
                sys.stderr.write(f"[erpclaw-selling] {e}\n")
                err(f"SLE posting failed: {e}")

            # COGS GL from SLE
            sleq = (Q.from_(_t_stock_ledger).select(_t_stock_ledger.star)
                    .where(_t_stock_ledger.voucher_type == P())
                    .where(_t_stock_ledger.voucher_id == P())
                    .where(_t_stock_ledger.is_cancelled == 0))
            sle_rows = conn.execute(sleq.get_sql(),
                (voucher_type, args.sales_invoice_id)).fetchall()
            sle_dicts = [row_to_dict(r) for r in sle_rows]

            cogs_gl_entries = create_perpetual_inventory_gl(
                conn, sle_dicts,
                voucher_type=voucher_type,
                voucher_id=args.sales_invoice_id,
                posting_date=posting_date,
                company_id=company_id,
                expense_account_id=cogs_account_id,
                cost_center_id=cost_center_id,
            )

            if cogs_gl_entries:
                for gle in cogs_gl_entries:
                    gle["fiscal_year"] = fiscal_year
                    gle["project_id"] = aggregate_project_id
                # Insert COGS GL entries via shared lib (entry_set="cogs"
                # allows multiple GL sets per voucher without idempotency conflict)
                try:
                    cogs_gl_ids = insert_gl_entries(
                        conn, cogs_gl_entries,
                        voucher_type=voucher_type,
                        voucher_id=args.sales_invoice_id,
                        posting_date=posting_date,
                        company_id=company_id,
                        remarks=f"COGS - {'Credit Note' if is_return else 'Sales Invoice'} {args.sales_invoice_id}",
                        entry_set="cogs",
                    )
                except ValueError as e:
                    sys.stderr.write(f"[erpclaw-selling] {e}\n")
                    err(f"COGS GL posting failed: {e}")

    # --- Payment Ledger Entry (PLE) ---
    # For credit notes: PLE amount is negative (reduces receivable)
    ple_amount = str(round_currency(abs_grand_total if not is_return else -abs_grand_total))
    ple_id = str(uuid.uuid4())
    # For credit notes, against_voucher points to the original invoice
    against_vtype = voucher_type
    against_vid = args.sales_invoice_id
    if is_return and si_dict.get("return_against"):
        against_vtype = "sales_invoice"
        against_vid = si_dict["return_against"]
    # raw SQL — INSERT with embedded literal strings ('customer', 'USD')
    conn.execute(
        """INSERT INTO payment_ledger_entry
           (id, posting_date, account_id, party_type, party_id,
            voucher_type, voucher_id, against_voucher_type, against_voucher_id,
            amount, amount_in_account_currency, currency, remarks)
           VALUES (?, ?, ?, 'customer', ?, ?, ?, ?, ?,
                   ?, ?, 'USD', ?)""",
        (ple_id, posting_date, receivable_account_id, customer_id,
         voucher_type, args.sales_invoice_id, against_vtype, against_vid,
         ple_amount, ple_amount,
         f"{'Credit Note' if is_return else 'Sales Invoice'} {args.sales_invoice_id}"),
    )

    # Update invoice status (naming already generated above before GL posting)
    uq = (Q.update(_t_sales_invoice)
          .set("status", ValueWrapper("submitted"))
          .set("naming_series", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_sales_invoice.id == P()))
    conn.execute(uq.get_sql(), (naming, args.sales_invoice_id))

    # Update SO invoiced_qty if linked
    if si_dict.get("sales_order_id"):
        for sii in si_items:
            sii_dict = row_to_dict(sii)
            if sii_dict.get("sales_order_item_id"):
                # raw SQL — CAST with arithmetic on TEXT column
                conn.execute(
                    """UPDATE sales_order_item
                       SET invoiced_qty = CAST(
                           invoiced_qty + 0 + ?
                       AS TEXT)
                       WHERE id = ?""",
                    (sii_dict["quantity"], sii_dict["sales_order_item_id"]),
                )
        _update_so_invoice_status(conn, si_dict["sales_order_id"])

    audit(conn, "erpclaw-selling", "submit-sales-invoice", "sales_invoice", args.sales_invoice_id,
           new_values={"naming_series": naming, "gl_count": len(gl_ids),
                       "sle_count": len(sle_ids), "update_stock": update_stock})
    conn.commit()
    ok({"sales_invoice_id": args.sales_invoice_id, "naming_series": naming,
         "status": "submitted",
         "gl_entries_created": len(gl_ids) + len(cogs_gl_ids),
         "sle_entries_created": len(sle_ids),
         "update_stock": bool(update_stock)})


def _update_so_invoice_status(conn, sales_order_id: str):
    """Recalculate SO per_invoiced and update status."""
    q = (Q.from_(_t_sales_order_item)
         .select(_t_sales_order_item.quantity, _t_sales_order_item.invoiced_qty)
         .where(_t_sales_order_item.sales_order_id == P()))
    items = conn.execute(q.get_sql(), (sales_order_id,)).fetchall()

    total_qty = Decimal("0")
    total_invoiced = Decimal("0")
    for item in items:
        total_qty += to_decimal(item["quantity"])
        total_invoiced += to_decimal(item["invoiced_qty"])

    if total_qty > 0:
        per_invoiced = round_currency(total_invoiced / total_qty * Decimal("100"))
    else:
        per_invoiced = Decimal("0")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.status)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (sales_order_id,)).fetchone()
    if so and so["status"] not in ("cancelled",):
        if per_invoiced >= Decimal("100"):
            new_status = "fully_invoiced"
        elif per_invoiced > 0:
            new_status = "partially_invoiced"
        else:
            return

        uq = (Q.update(_t_sales_order)
              .set("per_invoiced", P())
              .set("status", P())
              .set("updated_at", LiteralValue("datetime('now')"))
              .where(_t_sales_order.id == P()))
        conn.execute(uq.get_sql(), (str(per_invoiced), new_status, sales_order_id))


# ---------------------------------------------------------------------------
# 27. cancel-sales-invoice
# ---------------------------------------------------------------------------

def cancel_sales_invoice(conn, args):
    """Cancel a sales invoice: reverse GL + PLE (+ optional SLE)."""
    if not args.sales_invoice_id:
        err("--sales-invoice-id is required")

    siq = (Q.from_(_t_sales_invoice).select(_t_sales_invoice.star)
           .where(_t_sales_invoice.id == P()))
    si = conn.execute(siq.get_sql(), (args.sales_invoice_id,)).fetchone()
    if not si:
        err(f"Sales invoice {args.sales_invoice_id} not found")
    if si["status"] not in ("submitted", "overdue", "partially_paid"):
        err(f"Cannot cancel: sales invoice is '{si['status']}' (must be 'submitted', 'overdue', or 'partially_paid')")

    si_dict = row_to_dict(si)
    posting_date = si_dict["posting_date"]
    update_stock = si_dict.get("update_stock", 1)
    is_return = bool(si_dict.get("is_return", 0))
    cancel_voucher_type = "credit_note" if is_return else "sales_invoice"

    # Reverse GL entries
    try:
        reversal_gl_ids = reverse_gl_entries(
            conn,
            voucher_type=cancel_voucher_type,
            voucher_id=args.sales_invoice_id,
            posting_date=posting_date,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-selling] {e}\n")
        err(f"GL reversal failed: {e}")

    # COGS GL entries (entry_set="cogs") are reversed by the same call above
    # since reverse_gl_entries finds ALL entries for (voucher_type, voucher_id)

    # Reverse SLE if update_stock
    reversal_sle_ids = []
    if update_stock:
        try:
            reversal_sle_ids = reverse_sle_entries(
                conn,
                voucher_type=cancel_voucher_type,
                voucher_id=args.sales_invoice_id,
                posting_date=posting_date,
            )
        except ValueError:
            reversal_sle_ids = []

    # Mark PLE as delinked
    ple_uq = (Q.update(_t_payment_ledger)
              .set("delinked", 1)
              .set("updated_at", LiteralValue("datetime('now')"))
              .where(_t_payment_ledger.voucher_type == P())
              .where(_t_payment_ledger.voucher_id == P()))
    conn.execute(ple_uq.get_sql(), (cancel_voucher_type, args.sales_invoice_id))

    # Update invoice status
    uq = (Q.update(_t_sales_invoice)
          .set("status", ValueWrapper("cancelled"))
          .set("outstanding_amount", ValueWrapper("0"))
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_sales_invoice.id == P()))
    conn.execute(uq.get_sql(), (args.sales_invoice_id,))

    # Reverse SO invoiced_qty if linked
    if si_dict.get("sales_order_id"):
        siiq = (Q.from_(_t_sales_invoice_item).select(_t_sales_invoice_item.star)
                .where(_t_sales_invoice_item.sales_invoice_id == P()))
        si_items = conn.execute(siiq.get_sql(), (args.sales_invoice_id,)).fetchall()
        for sii in si_items:
            sii_dict = row_to_dict(sii)
            if sii_dict.get("sales_order_item_id"):
                # raw SQL — CAST with MAX and arithmetic on TEXT column
                conn.execute(
                    """UPDATE sales_order_item
                       SET invoiced_qty = CAST(
                           MAX(invoiced_qty + 0 - ?, 0)
                       AS TEXT)
                       WHERE id = ?""",
                    (sii_dict["quantity"], sii_dict["sales_order_item_id"]),
                )
        _update_so_invoice_status(conn, si_dict["sales_order_id"])

    audit(conn, "erpclaw-selling", "cancel-sales-invoice", "sales_invoice", args.sales_invoice_id,
           new_values={"reversed": True})
    conn.commit()
    ok({"sales_invoice_id": args.sales_invoice_id, "status": "cancelled",
         "gl_reversals": len(reversal_gl_ids),
         "sle_reversals": len(reversal_sle_ids)})


# ---------------------------------------------------------------------------
# 28. create-credit-note
# ---------------------------------------------------------------------------

def create_credit_note(conn, args):
    """Create a credit note (return invoice with negative amounts)."""
    if not args.against_invoice_id:
        err("--against-invoice-id is required")
    if not args.items:
        err("--items is required (JSON array)")

    origq = (Q.from_(_t_sales_invoice).select(_t_sales_invoice.star)
             .where(_t_sales_invoice.id == P()))
    orig = conn.execute(origq.get_sql(), (args.against_invoice_id,)).fetchone()
    if not orig:
        err(f"Original invoice {args.against_invoice_id} not found")
    if orig["status"] not in ("submitted", "overdue", "partially_paid", "paid"):
        err(f"Cannot create credit note: original invoice is '{orig['status']}'")

    orig_dict = row_to_dict(orig)
    company_id = orig_dict["company_id"]
    customer_id = orig_dict["customer_id"]
    posting_date = args.posting_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    # Validate return items against original invoice items
    oiq = (Q.from_(_t_sales_invoice_item).select(_t_sales_invoice_item.star)
           .where(_t_sales_invoice_item.sales_invoice_id == P()))
    orig_items = conn.execute(oiq.get_sql(), (args.against_invoice_id,)).fetchall()
    orig_item_map = {row_to_dict(oi)["item_id"]: row_to_dict(oi) for oi in orig_items}

    total_amount = Decimal("0")
    si_items_data = []
    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        if item_id not in orig_item_map:
            err(f"Item {i}: item {item_id} not found in original invoice")

        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")

        orig_item = orig_item_map[item_id]
        if qty > to_decimal(orig_item["quantity"]):
            err(f"Item {i}: return qty {qty} exceeds original qty {orig_item['quantity']}")

        rate = to_decimal(item.get("rate", orig_item["rate"]))
        net = round_currency(qty * rate)
        total_amount += net

        si_items_data.append({
            "item_id": item_id,
            "qty": str(round_currency(-qty)),  # Negative for returns
            "uom": orig_item.get("uom"),
            "rate": str(round_currency(rate)),
            "amount": str(round_currency(-qty * rate)),
            "discount_percentage": "0",
            "net_amount": str(round_currency(-net)),
            "sales_order_item_id": orig_item.get("sales_order_item_id"),
        })

    # Negate totals for credit note
    total_amount = round_currency(-total_amount)
    tax_amount, _ = _calculate_tax(conn, abs(total_amount), orig_dict.get("tax_template_id"))
    tax_amount = round_currency(-tax_amount)
    grand_total = round_currency(total_amount + tax_amount)

    si_id = str(uuid.uuid4())

    # Insert parent sales_invoice (is_return=1)
    cn_ins = (Q.into(_t_sales_invoice)
              .columns("id", "customer_id", "posting_date", "due_date",
                        "total_amount", "tax_amount", "grand_total",
                        "outstanding_amount", "tax_template_id", "status",
                        "sales_order_id", "is_return", "return_against",
                        "update_stock", "company_id")
              .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(),
                      ValueWrapper("draft"), P(), 1, P(), P(), P()))
    conn.execute(cn_ins.get_sql(),
        (si_id, customer_id, posting_date, posting_date,
         str(total_amount), str(tax_amount), str(grand_total), str(grand_total),
         orig_dict.get("tax_template_id"), orig_dict.get("sales_order_id"),
         args.against_invoice_id, orig_dict.get("update_stock", 0),
         company_id),
    )

    # Insert child items
    cni_ins = (Q.into(_t_sales_invoice_item)
               .columns("id", "sales_invoice_id", "item_id", "quantity", "uom",
                         "rate", "amount", "discount_percentage",
                         "net_amount", "sales_order_item_id")
               .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    cni_ins_sql = cni_ins.get_sql()
    for row in si_items_data:
        conn.execute(cni_ins_sql,
            (str(uuid.uuid4()), si_id, row["item_id"], row["qty"],
             row["uom"], row["rate"], row["amount"],
             row["discount_percentage"], row["net_amount"],
             row.get("sales_order_item_id")),
        )

    audit(conn, "erpclaw-selling", "create-credit-note", "sales_invoice", si_id,
           new_values={"against_invoice_id": args.against_invoice_id,
                       "reason": args.reason, "grand_total": str(grand_total)})
    conn.commit()
    ok({"credit_note_id": si_id, "against_invoice_id": args.against_invoice_id,
         "grand_total": str(grand_total), "is_return": True})


# ---------------------------------------------------------------------------
# 28b. list-credit-notes
# ---------------------------------------------------------------------------

def list_credit_notes(conn, args):
    """List credit notes (sales invoices where is_return=1)."""
    si = _t_sales_invoice.as_("si")
    c = _t_customer.as_("c")
    orig = _t_sales_invoice.as_("orig")
    params = []
    crit = si.is_return == 1

    if args.company_id:
        crit = Criterion.all([crit, si.company_id == P()])
        params.append(args.company_id)
    if args.customer_id:
        crit = Criterion.all([crit, si.customer_id == P()])
        params.append(args.customer_id)
    if args.doc_status:
        crit = Criterion.all([crit, si.status == P()])
        params.append(args.doc_status)
    if args.from_date:
        crit = Criterion.all([crit, si.posting_date >= P()])
        params.append(args.from_date)
    if args.to_date:
        crit = Criterion.all([crit, si.posting_date <= P()])
        params.append(args.to_date)

    count_q = Q.from_(si).select(fn.Count("*")).where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(si)
              .left_join(c).on(c.id == si.customer_id)
              .left_join(orig).on(orig.id == si.return_against)
              .select(si.id, si.naming_series, si.customer_id,
                      c.name.as_("customer_name"),
                      orig.naming_series.as_("return_against_name"),
                      si.posting_date, si.grand_total,
                      si.outstanding_amount, si.status, si.company_id)
              .where(crit)
              .orderby(si.posting_date, order=Order.desc)
              .orderby(si.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({"credit_notes": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 29. update-invoice-outstanding (cross-skill)
# ---------------------------------------------------------------------------

def update_invoice_outstanding(conn, args):
    """Called by erpclaw-payments when payment is allocated."""
    if not args.sales_invoice_id:
        err("--sales-invoice-id is required")
    if not args.amount:
        err("--amount is required")

    siq = (Q.from_(_t_sales_invoice).select(_t_sales_invoice.star)
           .where(_t_sales_invoice.id == P()))
    si = conn.execute(siq.get_sql(), (args.sales_invoice_id,)).fetchone()
    if not si:
        err(f"Sales invoice {args.sales_invoice_id} not found")
    if si["status"] not in ("submitted", "overdue", "partially_paid"):
        err(f"Cannot update outstanding: invoice is '{si['status']}'")

    current_outstanding = to_decimal(si["outstanding_amount"])
    payment_amount = to_decimal(args.amount)

    if payment_amount <= 0:
        err("--amount must be > 0")
    if payment_amount > current_outstanding:
        err(f"Payment amount {payment_amount} exceeds outstanding {current_outstanding}")

    new_outstanding = round_currency(current_outstanding - payment_amount)

    if new_outstanding <= Decimal("0"):
        new_status = "paid"
        new_outstanding = Decimal("0")
    else:
        new_status = "partially_paid"

    uq = (Q.update(_t_sales_invoice)
          .set("outstanding_amount", P())
          .set("status", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_sales_invoice.id == P()))
    conn.execute(uq.get_sql(), (str(new_outstanding), new_status, args.sales_invoice_id))

    audit(conn, "erpclaw-selling", "update-invoice-outstanding", "sales_invoice",
           args.sales_invoice_id,
           new_values={"payment_amount": str(payment_amount),
                       "new_outstanding": str(new_outstanding),
                       "new_status": new_status})
    conn.commit()
    ok({"sales_invoice_id": args.sales_invoice_id,
         "outstanding_amount": str(new_outstanding),
         "status": new_status})


# ---------------------------------------------------------------------------
# 30. add-sales-partner
# ---------------------------------------------------------------------------

def add_sales_partner(conn, args):
    """Create a sales partner."""
    if not args.name:
        err("--name is required")
    if not args.commission_rate:
        err("--commission-rate is required")

    rate = round_currency(to_decimal(args.commission_rate))
    sp_id = str(uuid.uuid4())

    try:
        sp_ins = (Q.into(_t_sales_partner)
                  .columns("id", "name", "commission_rate")
                  .insert(P(), P(), P()))
        conn.execute(sp_ins.get_sql(), (sp_id, args.name, str(rate)))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-selling] {e}\n")
        err("Sales partner creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-selling", "add-sales-partner", "sales_partner", sp_id,
           new_values={"name": args.name, "commission_rate": str(rate)})
    conn.commit()
    ok({"sales_partner_id": sp_id, "name": args.name,
         "commission_rate": str(rate)})


# ---------------------------------------------------------------------------
# 31. list-sales-partners
# ---------------------------------------------------------------------------

def list_sales_partners(conn, args):
    """List sales partners."""
    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    lq = (Q.from_(_t_sales_partner).select(_t_sales_partner.star)
          .orderby(_t_sales_partner.name)
          .limit(P()).offset(P()))
    rows = conn.execute(lq.get_sql(), (limit, offset)).fetchall()

    cq = Q.from_(_t_sales_partner).select(fn.Count("*"))
    count_row = conn.execute(cq.get_sql()).fetchone()
    total_count = count_row[0]
    ok({"sales_partners": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 32. add-recurring-template
# ---------------------------------------------------------------------------

def add_recurring_template(conn, args):
    """Create a recurring invoice template."""
    if not args.customer_id:
        err("--customer-id is required")
    if not args.items:
        err("--items is required (JSON array)")
    if not args.frequency:
        err("--frequency is required")
    if not args.start_date:
        err("--start-date is required")
    if not args.company_id:
        err("--company-id is required")

    if args.frequency not in VALID_FREQUENCIES:
        err(f"--frequency must be one of: {', '.join(VALID_FREQUENCIES)}")

    csq = (Q.from_(_t_customer).select(_t_customer.id)
           .where((_t_customer.id == P()) | (_t_customer.name == P()))
           .where(_t_customer.status == ValueWrapper("active")))
    cust_sub = conn.execute(csq.get_sql(),
        (args.customer_id, args.customer_id)).fetchone()
    if not cust_sub:
        err(f"Active customer {args.customer_id} not found")
    args.customer_id = cust_sub["id"]  # normalize to id
    coq = Q.from_(_t_company).select(_t_company.id).where(_t_company.id == P())
    if not conn.execute(coq.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    rt_id = str(uuid.uuid4())

    # Insert parent template first
    rt_ins = (Q.into(_t_recurring_template)
              .columns("id", "customer_id", "frequency", "start_date",
                        "end_date", "next_invoice_date", "tax_template_id",
                        "payment_terms_id", "status", "company_id")
              .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                      ValueWrapper("draft"), P()))
    conn.execute(rt_ins.get_sql(),
        (rt_id, args.customer_id, args.frequency, args.start_date,
         args.end_date, args.start_date, args.tax_template_id,
         args.payment_terms_id, args.company_id),
    )

    # Insert child items
    rti_ins = (Q.into(_t_recurring_template_item)
               .columns("id", "template_id", "item_id", "quantity", "uom",
                         "rate", "amount")
               .insert(P(), P(), P(), P(), P(), P(), P()))
    rti_ins_sql = rti_ins.get_sql()
    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        qty = to_decimal(item.get("qty", "0"))
        rate = to_decimal(item.get("rate", "0"))
        amount = round_currency(qty * rate)

        conn.execute(rti_ins_sql,
            (str(uuid.uuid4()), rt_id, item_id, str(round_currency(qty)),
             item.get("uom"), str(round_currency(rate)), str(amount)),
        )

    audit(conn, "erpclaw-selling", "add-recurring-template", "recurring_invoice_template", rt_id,
           new_values={"customer_id": args.customer_id, "frequency": args.frequency})
    conn.commit()
    ok({"template_id": rt_id, "frequency": args.frequency,
         "start_date": args.start_date, "next_invoice_date": args.start_date})


# ---------------------------------------------------------------------------
# 33. update-recurring-template
# ---------------------------------------------------------------------------

def update_recurring_template(conn, args):
    """Update a recurring invoice template."""
    if not args.template_id:
        err("--template-id is required")

    rtq = (Q.from_(_t_recurring_template).select(_t_recurring_template.star)
           .where(_t_recurring_template.id == P()))
    rt = conn.execute(rtq.get_sql(), (args.template_id,)).fetchone()
    if not rt:
        err(f"Template {args.template_id} not found")

    updated_fields = []

    if args.frequency is not None:
        if args.frequency not in VALID_FREQUENCIES:
            err(f"--frequency must be one of: {', '.join(VALID_FREQUENCIES)}")
        uq = (Q.update(_t_recurring_template)
              .set("frequency", P())
              .set("updated_at", LiteralValue("datetime('now')"))
              .where(_t_recurring_template.id == P()))
        conn.execute(uq.get_sql(), (args.frequency, args.template_id))
        updated_fields.append("frequency")

    if args.template_status is not None:
        if args.template_status not in ("active", "paused", "cancelled"):
            err("--status must be 'active', 'paused', or 'cancelled'")
        uq2 = (Q.update(_t_recurring_template)
               .set("status", P())
               .set("updated_at", LiteralValue("datetime('now')"))
               .where(_t_recurring_template.id == P()))
        conn.execute(uq2.get_sql(), (args.template_status, args.template_id))
        updated_fields.append("status")

    if args.items:
        items = _parse_json_arg(args.items, "items")
        if not items or not isinstance(items, list):
            err("--items must be a non-empty JSON array")

        dq = (Q.from_(_t_recurring_template_item).delete()
              .where(_t_recurring_template_item.template_id == P()))
        conn.execute(dq.get_sql(), (args.template_id,))

        rti_ins = (Q.into(_t_recurring_template_item)
                   .columns("id", "template_id", "item_id", "quantity", "uom",
                             "rate", "amount")
                   .insert(P(), P(), P(), P(), P(), P(), P()))
        rti_ins_sql = rti_ins.get_sql()
        for i, item in enumerate(items):
            item_id = item.get("item_id")
            if not item_id:
                err(f"Item {i}: item_id is required")
            qty = to_decimal(item.get("qty", "0"))
            rate = to_decimal(item.get("rate", "0"))
            amount = round_currency(qty * rate)

            conn.execute(rti_ins_sql,
                (str(uuid.uuid4()), args.template_id, item_id,
                 str(round_currency(qty)), item.get("uom"),
                 str(round_currency(rate)), str(amount)),
            )
        updated_fields.append("items")

    if not updated_fields:
        err("No fields to update")

    audit(conn, "erpclaw-selling", "update-recurring-template", "recurring_invoice_template",
           args.template_id, new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"template_id": args.template_id, "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 34. list-recurring-templates
# ---------------------------------------------------------------------------

def list_recurring_templates(conn, args):
    """List recurring invoice templates."""
    rt = _t_recurring_template.as_("rt")
    params = []
    crit = None

    if args.company_id:
        crit = (rt.company_id == P())
        params.append(args.company_id)
    if args.customer_id:
        cond = rt.customer_id == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.customer_id)
    if args.template_status:
        cond = rt.status == P()
        crit = Criterion.all([crit, cond]) if crit else cond
        params.append(args.template_status)

    count_q = Q.from_(rt).select(fn.Count("*"))
    if crit:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(rt).select(rt.star)
              .orderby(rt.next_invoice_date)
              .limit(P()).offset(P()))
    if crit:
        list_q = list_q.where(crit)
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({"recurring_templates": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 35. generate-recurring-invoices
# ---------------------------------------------------------------------------

def generate_recurring_invoices(conn, args):
    """Cron: auto-generate invoices from due templates."""
    if not args.company_id:
        err("--company-id is required")

    as_of_date = args.as_of_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # raw SQL — OR with IS NULL comparison
    templates = conn.execute(
        """SELECT * FROM recurring_invoice_template
           WHERE status = 'active'
             AND next_invoice_date <= ?
             AND company_id = ?
             AND (end_date IS NULL OR end_date >= ?)""",
        (as_of_date, args.company_id, as_of_date),
    ).fetchall()

    invoices_generated = []
    templates_completed = 0
    errors = []

    for tmpl in templates:
        tmpl_dict = row_to_dict(tmpl)
        template_id = tmpl_dict["id"]
        customer_id = tmpl_dict["customer_id"]
        company_id = tmpl_dict["company_id"]
        next_date = tmpl_dict["next_invoice_date"]
        frequency = tmpl_dict["frequency"]

        try:
            # Fetch template items
            tiq = (Q.from_(_t_recurring_template_item)
                   .select(_t_recurring_template_item.star)
                   .where(_t_recurring_template_item.template_id == P()))
            tmpl_items = conn.execute(tiq.get_sql(), (template_id,)).fetchall()
            if not tmpl_items:
                errors.append({"template_id": template_id,
                               "error": "Template has no items"})
                continue

            # Build invoice items
            total_amount = Decimal("0")
            si_items_data = []
            for ti in tmpl_items:
                ti_dict = row_to_dict(ti)
                qty = to_decimal(ti_dict["quantity"])
                rate = to_decimal(ti_dict["rate"])
                net = round_currency(qty * rate)
                total_amount += net
                si_items_data.append({
                    "item_id": ti_dict["item_id"],
                    "qty": str(round_currency(qty)),
                    "uom": ti_dict.get("uom"),
                    "rate": str(round_currency(rate)),
                    "amount": str(round_currency(qty * rate)),
                    "net_amount": str(net),
                })

            total_amount = round_currency(total_amount)
            tax_amount, tax_lines = _calculate_tax(
                conn, total_amount, tmpl_dict.get("tax_template_id"))
            grand_total = round_currency(total_amount + tax_amount)

            # Calculate due date
            parts = next_date.split("-")
            d = date_type(int(parts[0]), int(parts[1]), int(parts[2]))
            due_date = (d + timedelta(days=30)).isoformat()

            si_id = str(uuid.uuid4())

            # Create draft invoice
            rsi_ins = (Q.into(_t_sales_invoice)
                       .columns("id", "customer_id", "posting_date", "due_date",
                                 "total_amount", "tax_amount", "grand_total",
                                 "outstanding_amount", "tax_template_id",
                                 "status", "update_stock", "company_id")
                       .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(),
                               ValueWrapper("draft"), 0, P()))
            conn.execute(rsi_ins.get_sql(),
                (si_id, customer_id, next_date, due_date,
                 str(total_amount), str(tax_amount), str(grand_total),
                 str(grand_total), tmpl_dict.get("tax_template_id"),
                 company_id),
            )

            rsii_ins = (Q.into(_t_sales_invoice_item)
                        .columns("id", "sales_invoice_id", "item_id", "quantity",
                                  "uom", "rate", "amount", "discount_percentage",
                                  "net_amount")
                        .insert(P(), P(), P(), P(), P(), P(), P(),
                                ValueWrapper("0"), P()))
            rsii_ins_sql = rsii_ins.get_sql()
            for row in si_items_data:
                conn.execute(rsii_ins_sql,
                    (str(uuid.uuid4()), si_id, row["item_id"], row["qty"],
                     row["uom"], row["rate"], row["amount"], row["net_amount"]),
                )

            # Auto-submit the invoice
            # We need to do this inline since we cannot call argparse again
            fiscal_year = _get_fiscal_year(conn, next_date)
            cost_center_id = _get_cost_center(conn, company_id)
            receivable_account_id = _get_receivable_account(conn, company_id)
            income_account_id = _get_income_account(conn, company_id)

            if receivable_account_id and income_account_id:
                gl_entries = [
                    {
                        "account_id": receivable_account_id,
                        "debit": str(round_currency(grand_total)),
                        "credit": "0",
                        "party_type": "customer",
                        "party_id": customer_id,
                        "fiscal_year": fiscal_year,
                    },
                    {
                        "account_id": income_account_id,
                        "debit": "0",
                        "credit": str(round_currency(total_amount)),
                        "cost_center_id": cost_center_id,
                        "fiscal_year": fiscal_year,
                    },
                ]

                # Add tax GL entries
                if tax_amount > 0 and tax_lines:
                    for tl in tax_lines:
                        amt = abs(tl["amount"])
                        if amt > 0:
                            gl_entries.append({
                                "account_id": tl["account_id"],
                                "debit": "0",
                                "credit": str(round_currency(amt)),
                                "cost_center_id": cost_center_id,
                                "fiscal_year": fiscal_year,
                            })

                try:
                    insert_gl_entries(
                        conn, gl_entries,
                        voucher_type="sales_invoice",
                        voucher_id=si_id,
                        posting_date=next_date,
                        company_id=company_id,
                        remarks=f"Recurring Invoice from template {template_id}",
                    )
                except ValueError as e:
                    sys.stderr.write(f"[erpclaw-selling] {e}\n")
                    errors.append({"template_id": template_id,
                                   "error": "GL posting failed"})
                    conn.rollback()
                    continue

                # PLE
                # raw SQL — INSERT with embedded literal strings ('customer', 'sales_invoice', 'USD')
                ple_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT INTO payment_ledger_entry
                       (id, posting_date, account_id, party_type, party_id,
                        voucher_type, voucher_id, against_voucher_type,
                        against_voucher_id, amount, amount_in_account_currency,
                        currency, remarks)
                       VALUES (?, ?, ?, 'customer', ?, 'sales_invoice', ?,
                               'sales_invoice', ?, ?, ?, 'USD', ?)""",
                    (ple_id, next_date, receivable_account_id, customer_id,
                     si_id, si_id, str(round_currency(grand_total)),
                     str(round_currency(grand_total)),
                     f"Recurring Invoice {si_id}"),
                )

            # Generate naming and mark as submitted
            naming = get_next_name(conn, "sales_invoice", company_id=company_id)
            uq_si = (Q.update(_t_sales_invoice)
                     .set("status", ValueWrapper("submitted"))
                     .set("naming_series", P())
                     .set("updated_at", LiteralValue("datetime('now')"))
                     .where(_t_sales_invoice.id == P()))
            conn.execute(uq_si.get_sql(), (naming, si_id))

            # Update template dates
            new_next = _next_invoice_date(next_date, frequency)
            uq_rt = (Q.update(_t_recurring_template)
                     .set("last_invoice_date", P())
                     .set("next_invoice_date", P())
                     .set("updated_at", LiteralValue("datetime('now')"))
                     .where(_t_recurring_template.id == P()))
            conn.execute(uq_rt.get_sql(), (next_date, new_next, template_id))

            # Check if template is completed
            if tmpl_dict.get("end_date") and new_next > tmpl_dict["end_date"]:
                uq_comp = (Q.update(_t_recurring_template)
                           .set("status", ValueWrapper("completed"))
                           .set("updated_at", LiteralValue("datetime('now')"))
                           .where(_t_recurring_template.id == P()))
                conn.execute(uq_comp.get_sql(), (template_id,))
                templates_completed += 1

            invoices_generated.append({
                "template_id": template_id,
                "invoice_id": si_id,
                "naming_series": naming,
                "customer_id": customer_id,
                "amount": str(grand_total),
            })

        except Exception as e:
            errors.append({"template_id": template_id,
                           "error": str(e)})
            continue

    conn.commit()
    ok({"invoices_generated": len(invoices_generated),
         "templates_processed": len(templates),
         "templates_completed": templates_completed,
         "invoices": invoices_generated,
         "errors": errors})


# ---------------------------------------------------------------------------
# 36. add-blanket-order
# ---------------------------------------------------------------------------

def add_blanket_order(conn, args):
    """Create a blanket sales order (framework agreement with a customer)."""
    if not args.customer_id:
        err("--customer-id is required")
    if not args.items:
        err("--items is required (JSON array)")
    if not args.company_id:
        err("--company-id is required")
    if not args.valid_from:
        err("--valid-from is required")
    if not args.valid_to:
        err("--valid-to is required")

    # Validate customer
    csq = (Q.from_(_t_customer).select(_t_customer.id)
           .where((_t_customer.id == P()) | (_t_customer.name == P()))
           .where(_t_customer.status == ValueWrapper("active")))
    cust = conn.execute(csq.get_sql(),
        (args.customer_id, args.customer_id)).fetchone()
    if not cust:
        err(f"Active customer {args.customer_id} not found")
    customer_id = cust["id"]

    coq = Q.from_(_t_company).select(_t_company.id).where(_t_company.id == P())
    if not conn.execute(coq.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    if args.valid_to <= args.valid_from:
        err("--valid-to must be after --valid-from")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    bo_id = str(uuid.uuid4())
    total_qty = Decimal("0")

    # Insert parent blanket_order
    bo_ins = (Q.into(_t_blanket_order)
              .columns("id", "customer_id", "blanket_order_type",
                        "valid_from", "valid_to", "status", "company_id")
              .insert(P(), P(), ValueWrapper("selling"),
                      P(), P(), ValueWrapper("draft"), P()))
    conn.execute(bo_ins.get_sql(),
        (bo_id, customer_id, args.valid_from, args.valid_to, args.company_id))

    # Insert child items
    boi_ins = (Q.into(_t_blanket_order_item)
               .columns("id", "blanket_order_id", "item_id", "quantity",
                         "uom", "rate", "amount")
               .insert(P(), P(), P(), P(), P(), P(), P()))
    boi_ins_sql = boi_ins.get_sql()
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
        total_qty += qty

        conn.execute(boi_ins_sql,
            (str(uuid.uuid4()), bo_id, item_id, str(round_currency(qty)),
             item.get("uom"), str(round_currency(rate)), str(amount)))

    # Update totals
    uq = (Q.update(_t_blanket_order)
          .set(_t_blanket_order.total_qty, P())
          .where(_t_blanket_order.id == P()))
    conn.execute(uq.get_sql(), (str(round_currency(total_qty)), bo_id))

    audit(conn, "erpclaw-selling", "add-blanket-order", "blanket_order", bo_id,
           new_values={"customer_id": customer_id, "total_qty": str(total_qty)})
    conn.commit()
    ok({"blanket_order_id": bo_id, "customer_id": customer_id,
         "total_qty": str(round_currency(total_qty)),
         "valid_from": args.valid_from, "valid_to": args.valid_to})


# ---------------------------------------------------------------------------
# 37. submit-blanket-order
# ---------------------------------------------------------------------------

def submit_blanket_order(conn, args):
    """Activate a blanket sales order."""
    if not args.blanket_order_id:
        err("--blanket-order-id is required")

    boq = (Q.from_(_t_blanket_order).select(_t_blanket_order.star)
           .where(_t_blanket_order.id == P()))
    bo = conn.execute(boq.get_sql(), (args.blanket_order_id,)).fetchone()
    if not bo:
        err(f"Blanket order {args.blanket_order_id} not found")
    if bo["status"] != "draft":
        err(f"Cannot submit: blanket order is '{bo['status']}' (must be 'draft')")
    if bo["blanket_order_type"] != "selling":
        err("This blanket order is not a selling type")

    uq = (Q.update(_t_blanket_order)
          .set(_t_blanket_order.status, ValueWrapper("active"))
          .set(_t_blanket_order.updated_at, LiteralValue("datetime('now')"))
          .where(_t_blanket_order.id == P()))
    conn.execute(uq.get_sql(), (args.blanket_order_id,))

    audit(conn, "erpclaw-selling", "submit-blanket-order", "blanket_order",
           args.blanket_order_id, new_values={"status": "active"})
    conn.commit()
    ok({"blanket_order_id": args.blanket_order_id, "doc_status": "active"})


# ---------------------------------------------------------------------------
# 38. get-blanket-order
# ---------------------------------------------------------------------------

def get_blanket_order(conn, args):
    """Get a blanket sales order with its items."""
    if not args.blanket_order_id:
        err("--blanket-order-id is required")

    boq = (Q.from_(_t_blanket_order).select(_t_blanket_order.star)
           .where(_t_blanket_order.id == P()))
    bo = conn.execute(boq.get_sql(), (args.blanket_order_id,)).fetchone()
    if not bo:
        err(f"Blanket order {args.blanket_order_id} not found")

    data = row_to_dict(bo)

    # Fetch items
    boiq = (Q.from_(_t_blanket_order_item).select(_t_blanket_order_item.star)
            .where(_t_blanket_order_item.blanket_order_id == P()))
    items = conn.execute(boiq.get_sql(), (args.blanket_order_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    ok(data)


# ---------------------------------------------------------------------------
# 39. list-blanket-orders
# ---------------------------------------------------------------------------

def list_blanket_orders(conn, args):
    """List blanket sales orders."""
    bo = _t_blanket_order.as_("bo")
    params = []
    crit = (bo.blanket_order_type == ValueWrapper("selling"))

    if args.company_id:
        crit = Criterion.all([crit, bo.company_id == P()])
        params.append(args.company_id)
    if args.customer_id:
        crit = Criterion.all([crit, bo.customer_id == P()])
        params.append(args.customer_id)
    if args.doc_status:
        crit = Criterion.all([crit, bo.status == P()])
        params.append(args.doc_status)

    count_q = Q.from_(bo).select(fn.Count("*")).where(crit)
    total_count = conn.execute(count_q.get_sql(), params).fetchone()[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(bo).select(bo.star)
              .where(crit)
              .orderby(bo.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({"blanket_orders": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 40. create-so-from-blanket
# ---------------------------------------------------------------------------

def create_so_from_blanket(conn, args):
    """Create a sales order drawing down from an active blanket order."""
    if not args.blanket_order_id:
        err("--blanket-order-id is required")
    if not args.items:
        err("--items is required (JSON array)")

    # Validate blanket order
    boq = (Q.from_(_t_blanket_order).select(_t_blanket_order.star)
           .where(_t_blanket_order.id == P()))
    bo = conn.execute(boq.get_sql(), (args.blanket_order_id,)).fetchone()
    if not bo:
        err(f"Blanket order {args.blanket_order_id} not found")
    if bo["status"] != "active":
        err(f"Cannot create SO: blanket order is '{bo['status']}' (must be 'active')")
    if bo["blanket_order_type"] != "selling":
        err("This blanket order is not a selling type")

    # Check expiry
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if bo["valid_to"] < today:
        err(f"Blanket order expired on {bo['valid_to']}")

    customer_id = bo["customer_id"]
    company_id = bo["company_id"]

    # Fetch blanket items for validation
    boiq = (Q.from_(_t_blanket_order_item).select(_t_blanket_order_item.star)
            .where(_t_blanket_order_item.blanket_order_id == P()))
    bo_items = conn.execute(boiq.get_sql(), (args.blanket_order_id,)).fetchall()
    bo_items_map = {}
    for bi in bo_items:
        bid = row_to_dict(bi)
        bo_items_map[bid["item_id"]] = bid

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    # Validate quantities against blanket
    so_id = str(uuid.uuid4())
    posting_date = args.posting_date or today
    total_amount = Decimal("0")
    so_item_rows = []
    blanket_updates = []  # (boi_id, new_ordered_qty)

    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")

        if item_id not in bo_items_map:
            err(f"Item {i}: item {item_id} not in blanket order")

        bi = bo_items_map[item_id]
        max_qty = to_decimal(bi["quantity"])
        ordered = to_decimal(bi["ordered_qty"])
        remaining = max_qty - ordered

        if qty > remaining:
            err(f"Item {i}: requested qty {qty} exceeds remaining blanket qty {remaining}")

        rate = to_decimal(item.get("rate") or bi["rate"])
        amount = round_currency(qty * rate)
        total_amount += amount

        so_item_rows.append({
            "item_id": item_id,
            "qty": str(round_currency(qty)),
            "uom": item.get("uom") or bi.get("uom"),
            "rate": str(round_currency(rate)),
            "amount": str(amount),
            "warehouse_id": item.get("warehouse_id"),
        })
        blanket_updates.append((bi["id"], str(round_currency(ordered + qty))))

    total_amount = round_currency(total_amount)
    tax_amount, _ = _calculate_tax(conn, total_amount, args.tax_template_id)
    grand_total = round_currency(total_amount + tax_amount)

    # Insert SO
    so_ins = (Q.into(_t_sales_order)
              .columns("id", "customer_id", "order_date", "delivery_date",
                        "total_amount", "tax_amount", "grand_total",
                        "tax_template_id", "status", "company_id")
              .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                      ValueWrapper("draft"), P()))
    conn.execute(so_ins.get_sql(),
        (so_id, customer_id, posting_date, args.delivery_date,
         str(total_amount), str(tax_amount), str(grand_total),
         args.tax_template_id, company_id))

    # Insert SO items
    soi_ins = (Q.into(_t_sales_order_item)
               .columns("id", "sales_order_id", "item_id", "quantity", "uom",
                         "rate", "amount", "discount_percentage",
                         "net_amount", "warehouse_id")
               .insert(P(), P(), P(), P(), P(), P(), P(),
                       ValueWrapper("0"), P(), P()))
    soi_ins_sql = soi_ins.get_sql()
    for row in so_item_rows:
        conn.execute(soi_ins_sql,
            (str(uuid.uuid4()), so_id, row["item_id"], row["qty"],
             row["uom"], row["rate"], row["amount"],
             row["amount"], row["warehouse_id"]))

    # Update blanket order item ordered_qty
    boi_uq = (Q.update(_t_blanket_order_item)
              .set(_t_blanket_order_item.ordered_qty, P())
              .where(_t_blanket_order_item.id == P()))
    boi_uq_sql = boi_uq.get_sql()
    for boi_id, new_ordered in blanket_updates:
        conn.execute(boi_uq_sql, (new_ordered, boi_id))

    # Update blanket order total ordered_qty
    total_ordered = sum(to_decimal(x[1]) for x in blanket_updates)
    # Re-fetch actual total from all items
    boiq2 = (Q.from_(_t_blanket_order_item)
             .select(fn.Count("*").as_("cnt"))
             .where(_t_blanket_order_item.blanket_order_id == P()))
    # Actually compute ordered across all items
    ordered_sum = conn.execute(
        """SELECT COALESCE(decimal_sum(ordered_qty), '0') as total
           FROM blanket_order_item WHERE blanket_order_id = ?""",
        (args.blanket_order_id,)).fetchone()["total"]
    bo_uq = (Q.update(_t_blanket_order)
             .set(_t_blanket_order.ordered_qty, P())
             .set(_t_blanket_order.updated_at, LiteralValue("datetime('now')"))
             .where(_t_blanket_order.id == P()))
    conn.execute(bo_uq.get_sql(), (ordered_sum, args.blanket_order_id))

    audit(conn, "erpclaw-selling", "create-so-from-blanket", "sales_order", so_id,
           new_values={"blanket_order_id": args.blanket_order_id,
                       "grand_total": str(grand_total)})
    conn.commit()
    ok({"sales_order_id": so_id,
         "blanket_order_id": args.blanket_order_id,
         "total_amount": str(total_amount),
         "grand_total": str(grand_total)})


# ---------------------------------------------------------------------------
# 41. status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """Selling summary for a company."""
    company_id = args.company_id
    if not company_id:
        cq = Q.from_(_t_company).select(_t_company.id).limit(1)
        row = conn.execute(cq.get_sql()).fetchone()
        if not row:
            err("No company found. Create one with erpclaw first.",
                 suggestion="Run 'tutorial' to create a demo company, or 'setup company' to create your own.")
        company_id = row["id"]

    # Customer count
    ccq = (Q.from_(_t_customer).select(fn.Count("*").as_("cnt"))
           .where(_t_customer.company_id == P()))
    cust_count = conn.execute(ccq.get_sql(), (company_id,)).fetchone()["cnt"]

    # Quotations by status
    qqb = (Q.from_(_t_quotation)
           .select(_t_quotation.status, fn.Count("*").as_("cnt"))
           .where(_t_quotation.company_id == P())
           .groupby(_t_quotation.status))
    q_rows = conn.execute(qqb.get_sql(), (company_id,)).fetchall()
    q_counts = {}
    for row in q_rows:
        q_counts[row["status"]] = row["cnt"]

    # Sales orders by status
    soq = (Q.from_(_t_sales_order)
           .select(_t_sales_order.status, fn.Count("*").as_("cnt"))
           .where(_t_sales_order.company_id == P())
           .groupby(_t_sales_order.status))
    so_rows = conn.execute(soq.get_sql(), (company_id,)).fetchall()
    so_counts = {}
    for row in so_rows:
        so_counts[row["status"]] = row["cnt"]

    # Sales invoices by status
    siq = (Q.from_(_t_sales_invoice)
           .select(_t_sales_invoice.status, fn.Count("*").as_("cnt"))
           .where(_t_sales_invoice.company_id == P())
           .groupby(_t_sales_invoice.status))
    si_rows = conn.execute(siq.get_sql(), (company_id,)).fetchall()
    si_counts = {}
    for row in si_rows:
        si_counts[row["status"]] = row["cnt"]

    # Total outstanding
    # raw SQL — decimal_sum with COALESCE and IN clause with arithmetic comparison
    outstanding_row = conn.execute(
        """SELECT COALESCE(decimal_sum(outstanding_amount), '0') as total
           FROM sales_invoice
           WHERE company_id = ? AND status IN ('submitted', 'overdue', 'partially_paid')
             AND outstanding_amount + 0 > 0""",
        (company_id,),
    ).fetchone()
    total_outstanding = str(round_currency(
        to_decimal(str(outstanding_row["total"]))))

    ok({
        "customers": cust_count,
        "quotations": q_counts,
        "sales_orders": so_counts,
        "sales_invoices": si_counts,
        "total_outstanding": total_outstanding,
    })


# ---------------------------------------------------------------------------
# import-customers
# ---------------------------------------------------------------------------

def import_customers(conn, args):
    """Bulk import customers from a CSV file.

    CSV columns: name, customer_type (optional), territory (optional),
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
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args

    errors = validate_csv(csv_real, "customer")
    if errors:
        err(f"CSV validation failed: {'; '.join(errors)}")

    rows = parse_csv_rows(csv_real, "customer")
    if not rows:
        err("CSV file is empty")

    imported = 0
    skipped = 0
    for row in rows:
        name = row.get("name", "")

        # Check for duplicate
        dup_q = (Q.from_(_t_customer).select(_t_customer.id)
                 .where(_t_customer.name == P())
                 .where(_t_customer.company_id == P()))
        existing = conn.execute(dup_q.get_sql(), (name, company_id)).fetchone()
        if existing:
            skipped += 1
            continue

        customer_id = str(uuid.uuid4())
        naming = get_next_name(conn, "customer")
        c_ins = (Q.into(_t_customer)
                 .columns("id", "name", "naming_series", "customer_type",
                           "territory", "default_currency", "email", "phone",
                           "tax_id", "company_id")
                 .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
        conn.execute(c_ins.get_sql(),
            (customer_id, name, naming,
             row.get("customer_type", "Company"),
             row.get("territory"),
             row.get("default_currency", "USD"),
             row.get("email"), row.get("phone"), row.get("tax_id"),
             company_id),
        )
        imported += 1

    conn.commit()
    ok({"imported": imported, "skipped": skipped, "total_rows": len(rows)})


# ---------------------------------------------------------------------------
# Intercompany Account Map
# ---------------------------------------------------------------------------


def add_intercompany_account_map(conn, args):
    """Add a mapping from source company account to target company account."""
    source_company_id = args.company_id
    target_company_id = args.target_company_id
    source_account_id = args.source_account_id
    target_account_id = args.target_account_id

    if not source_company_id:
        err("--company-id (source company) is required")
    if not target_company_id:
        err("--target-company-id is required")
    if not source_account_id:
        err("--source-account-id is required")
    if not target_account_id:
        err("--target-account-id is required")
    if source_company_id == target_company_id:
        err("Source and target company must be different")

    # Validate companies exist
    co_chk = Q.from_(_t_company).select(LiteralValue("1")).where(_t_company.id == P())
    co_chk_sql = co_chk.get_sql()
    for cid, label in [(source_company_id, "Source"), (target_company_id, "Target")]:
        if not conn.execute(co_chk_sql, (cid,)).fetchone():
            err(f"{label} company not found: {cid}")

    # Validate accounts exist and belong to correct companies
    acq = (Q.from_(_t_account).select(_t_account.id, _t_account.company_id)
           .where(_t_account.id == P()))
    acq_sql = acq.get_sql()
    src_acct = conn.execute(acq_sql, (source_account_id,)).fetchone()
    if not src_acct:
        err(f"Source account not found: {source_account_id}")
    if src_acct["company_id"] != source_company_id:
        err("Source account does not belong to source company")

    tgt_acct = conn.execute(acq_sql, (target_account_id,)).fetchone()
    if not tgt_acct:
        err(f"Target account not found: {target_account_id}")
    if tgt_acct["company_id"] != target_company_id:
        err("Target account does not belong to target company")

    # Check for duplicate
    dup_q = (Q.from_(_t_ic_account_map).select(_t_ic_account_map.id)
             .where(_t_ic_account_map.source_company_id == P())
             .where(_t_ic_account_map.target_company_id == P())
             .where(_t_ic_account_map.source_account_id == P()))
    existing = conn.execute(dup_q.get_sql(),
        (source_company_id, target_company_id, source_account_id)).fetchone()
    if existing:
        err("Mapping already exists for this source account and company pair")

    map_id = str(uuid.uuid4())
    ic_ins = (Q.into(_t_ic_account_map)
              .columns("id", "source_company_id", "target_company_id",
                        "source_account_id", "target_account_id")
              .insert(P(), P(), P(), P(), P()))
    conn.execute(ic_ins.get_sql(),
        (map_id, source_company_id, target_company_id, source_account_id, target_account_id))
    conn.commit()
    ok({"map_id": map_id})


def list_intercompany_account_maps(conn, args):
    """List intercompany account mappings for a company pair."""
    source_company_id = args.company_id
    target_company_id = args.target_company_id

    if not source_company_id:
        err("--company-id (source company) is required")

    m = _t_ic_account_map.as_("m")
    sa = _t_account.as_("sa")
    ta = _t_account.as_("ta")
    params = [source_company_id]
    lq = (Q.from_(m)
          .join(sa).on(sa.id == m.source_account_id)
          .join(ta).on(ta.id == m.target_account_id)
          .select(m.id, m.source_company_id, m.target_company_id,
                  m.source_account_id, sa.name.as_("source_account_name"),
                  m.target_account_id, ta.name.as_("target_account_name"))
          .where(m.source_company_id == P()))
    if target_company_id:
        lq = lq.where(m.target_company_id == P())
        params.append(target_company_id)

    rows = conn.execute(lq.get_sql(), params).fetchall()
    ok({"mappings": [dict(r) for r in rows], "total": len(rows)})


# ---------------------------------------------------------------------------
# Intercompany Invoice Mirroring
# ---------------------------------------------------------------------------


def create_intercompany_invoice(conn, args):
    """Create a mirror purchase invoice in the target company from a sales invoice.

    Requires:
      --sales-invoice-id  (the submitted SI in source company)
      --target-company-id (the company where the mirror PI will be created)
      --supplier-id       (the supplier in target company representing source company)
    """
    si_id = args.sales_invoice_id
    target_company_id = args.target_company_id
    supplier_id = args.supplier_id

    if not si_id:
        err("--sales-invoice-id is required")
    if not target_company_id:
        err("--target-company-id is required")
    if not supplier_id:
        err("--supplier-id is required (supplier in target company representing source)")

    # Fetch the sales invoice
    siq = (Q.from_(_t_sales_invoice).select(_t_sales_invoice.star)
           .where(_t_sales_invoice.id == P()))
    si = conn.execute(siq.get_sql(), (si_id,)).fetchone()
    if not si:
        err(f"Sales invoice not found: {si_id}")

    source_company_id = si["company_id"]

    # Validations
    if si["status"] not in ("submitted", "partially_paid", "paid", "overdue"):
        err(f"Sales invoice must be submitted (current: {si['status']})")
    if source_company_id == target_company_id:
        err("Source and target company must be different")
    if si["is_intercompany"] == 1:
        err("Sales invoice is already an intercompany invoice")

    # Validate target company exists
    tcq = (Q.from_(_t_company).select(_t_company.id, _t_company.name)
           .where(_t_company.id == P()))
    target_company = conn.execute(tcq.get_sql(), (target_company_id,)).fetchone()
    if not target_company:
        err(f"Target company not found: {target_company_id}")

    # Validate supplier exists in target company
    sq = (Q.from_(_t_supplier).select(_t_supplier.id, _t_supplier.company_id)
          .where(_t_supplier.id == P()))
    supplier = conn.execute(sq.get_sql(), (supplier_id,)).fetchone()
    if not supplier:
        err(f"Supplier not found: {supplier_id}")
    if supplier["company_id"] != target_company_id:
        err("Supplier does not belong to target company")

    # Fetch SI items
    siiq = (Q.from_(_t_sales_invoice_item).select(_t_sales_invoice_item.star)
            .where(_t_sales_invoice_item.sales_invoice_id == P()))
    si_items = conn.execute(siiq.get_sql(), (si_id,)).fetchall()
    if not si_items:
        err("Sales invoice has no items")

    # Look up account mappings (source income -> target expense)
    mappings = {}
    mq = (Q.from_(_t_ic_account_map)
          .select(_t_ic_account_map.source_account_id,
                  _t_ic_account_map.target_account_id)
          .where(_t_ic_account_map.source_company_id == P())
          .where(_t_ic_account_map.target_company_id == P()))
    map_rows = conn.execute(mq.get_sql(),
        (source_company_id, target_company_id)).fetchall()
    for m in map_rows:
        mappings[m["source_account_id"]] = m["target_account_id"]

    # Find a default expense account in target company if no mappings
    deq = (Q.from_(_t_account).select(_t_account.id)
           .where(_t_account.root_type == ValueWrapper("expense"))
           .where(_t_account.company_id == P())
           .where(_t_account.is_group == 0)
           .limit(1))
    default_expense = conn.execute(deq.get_sql(), (target_company_id,)).fetchone()
    default_expense_id = default_expense["id"] if default_expense else None

    # Create mirror purchase invoice (draft)
    pi_id = str(uuid.uuid4())
    posting_date = si["posting_date"]
    due_date = si["due_date"]
    total_amount = si["total_amount"]
    tax_amount = si["tax_amount"]
    grand_total = si["grand_total"]
    currency = si["currency"]
    exchange_rate = si["exchange_rate"]

    pi_ins = (Q.into(_t_purchase_invoice)
              .columns("id", "supplier_id", "posting_date", "due_date",
                        "currency", "exchange_rate", "total_amount",
                        "tax_amount", "grand_total", "outstanding_amount",
                        "tax_template_id", "status", "update_stock",
                        "is_intercompany", "intercompany_reference_id",
                        "company_id")
              .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P(),
                      ValueWrapper("draft"), 0, 1, P(), P()))
    conn.execute(pi_ins.get_sql(),
        (pi_id, supplier_id, posting_date, due_date, currency, exchange_rate,
         total_amount, tax_amount, grand_total, grand_total,
         si["tax_template_id"],
         si_id, target_company_id),
    )

    # Create mirror PI items
    for item in si_items:
        pi_item_id = str(uuid.uuid4())
        # Find expense account for this item via mappings
        expense_acct = default_expense_id
        if mappings:
            # Try to find source income account from SI's company
            iaq = (Q.from_(_t_account).select(_t_account.id)
                   .where(_t_account.root_type == ValueWrapper("income"))
                   .where(_t_account.company_id == P())
                   .where(_t_account.is_group == 0)
                   .limit(1))
            income_acct = conn.execute(iaq.get_sql(), (source_company_id,)).fetchone()
            if income_acct and income_acct["id"] in mappings:
                expense_acct = mappings[income_acct["id"]]

        pii_ins = (Q.into(_t_purchase_invoice_item)
                   .columns("id", "purchase_invoice_id", "item_id", "quantity",
                             "uom", "rate", "amount", "expense_account_id")
                   .insert(P(), P(), P(), P(), P(), P(), P(), P()))
        conn.execute(pii_ins.get_sql(),
            (pi_item_id, pi_id, item["item_id"], item["quantity"],
             item["uom"], item["rate"], item["amount"], expense_acct),
        )

    # Mark SI as intercompany
    uq = (Q.update(_t_sales_invoice)
          .set("is_intercompany", 1)
          .set("intercompany_reference_id", P())
          .where(_t_sales_invoice.id == P()))
    conn.execute(uq.get_sql(), (pi_id, si_id))

    conn.commit()
    ok({
        "purchase_invoice_id": pi_id,
        "sales_invoice_id": si_id,
        "source_company_id": source_company_id,
        "target_company_id": target_company_id,
        "total_amount": total_amount,
        "grand_total": grand_total,
        "items_mirrored": len(si_items),
    })


def list_intercompany_invoices(conn, args):
    """List all intercompany invoices for a company."""
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")

    limit = int(args.limit or "20")
    offset = int(args.offset or "0")

    # Sales invoices that are intercompany (this company is seller)
    si_a = _t_sales_invoice.as_("si")
    c = _t_customer.as_("c")
    si_q = (Q.from_(si_a)
            .join(c).on(c.id == si_a.customer_id)
            .select(si_a.id, si_a.naming_series, si_a.posting_date,
                    si_a.grand_total, si_a.status,
                    si_a.intercompany_reference_id,
                    c.name.as_("customer_name"),
                    ValueWrapper("sales").as_("direction"))
            .where(si_a.company_id == P())
            .where(si_a.is_intercompany == 1)
            .orderby(si_a.posting_date, order=Order.desc)
            .limit(P()).offset(P()))
    si_rows = conn.execute(si_q.get_sql(), (company_id, limit, offset)).fetchall()

    # Purchase invoices that are intercompany (this company is buyer)
    pi_a = _t_purchase_invoice.as_("pi")
    s = _t_supplier.as_("s")
    pi_q = (Q.from_(pi_a)
            .join(s).on(s.id == pi_a.supplier_id)
            .select(pi_a.id, pi_a.naming_series, pi_a.posting_date,
                    pi_a.grand_total, pi_a.status,
                    pi_a.intercompany_reference_id,
                    s.name.as_("supplier_name"),
                    ValueWrapper("purchase").as_("direction"))
            .where(pi_a.company_id == P())
            .where(pi_a.is_intercompany == 1)
            .orderby(pi_a.posting_date, order=Order.desc)
            .limit(P()).offset(P()))
    pi_rows = conn.execute(pi_q.get_sql(), (company_id, limit, offset)).fetchall()

    invoices = [dict(r) for r in si_rows] + [dict(r) for r in pi_rows]
    ok({"invoices": invoices, "total": len(invoices)})


def cancel_intercompany_invoice(conn, args):
    """Cancel an intercompany sales invoice and cascade to the mirror purchase invoice.

    Requires: --sales-invoice-id
    """
    si_id = args.sales_invoice_id
    if not si_id:
        err("--sales-invoice-id is required")

    siq = (Q.from_(_t_sales_invoice).select(_t_sales_invoice.star)
           .where(_t_sales_invoice.id == P()))
    si = conn.execute(siq.get_sql(), (si_id,)).fetchone()
    if not si:
        err(f"Sales invoice not found: {si_id}")
    if si["is_intercompany"] != 1:
        err("Sales invoice is not an intercompany invoice")

    pi_id = si["intercompany_reference_id"]
    posting_date = si["posting_date"]
    source_company_id = si["company_id"]

    # --- Cancel the Sales Invoice (source company) ---
    si_status = si["status"]
    si_gl_reversals = 0
    si_sle_reversals = 0
    if si_status in ("submitted", "overdue", "partially_paid"):
        voucher_type = "credit_note" if si["is_return"] else "sales_invoice"

        # Reverse GL (includes COGS entries — reverses all for the voucher)
        try:
            rev_gl = reverse_gl_entries(conn, voucher_type, si_id, posting_date)
            si_gl_reversals = len(rev_gl)
        except ValueError:
            pass  # No GL entries to reverse

        # Reverse SLE if applicable
        if si["update_stock"]:
            try:
                rev_sle = reverse_sle_entries(conn, voucher_type, si_id, posting_date)
                si_sle_reversals = len(rev_sle)
            except ValueError:
                pass

        # Mark PLE as delinked
        ple_uq = (Q.update(_t_payment_ledger)
                  .set("delinked", 1)
                  .where(_t_payment_ledger.voucher_type == P())
                  .where(_t_payment_ledger.voucher_id == P()))
        conn.execute(ple_uq.get_sql(), (voucher_type, si_id))

        # Update SI status
        si_uq = (Q.update(_t_sales_invoice)
                 .set("status", ValueWrapper("cancelled"))
                 .set("outstanding_amount", ValueWrapper("0"))
                 .where(_t_sales_invoice.id == P()))
        conn.execute(si_uq.get_sql(), (si_id,))
    elif si_status == "cancelled":
        pass  # Already cancelled
    else:
        err(f"Cannot cancel sales invoice in status: {si_status}")

    # --- Cancel the mirror Purchase Invoice (target company) ---
    pi_gl_reversals = 0
    pi_sle_reversals = 0
    if pi_id:
        piq = (Q.from_(_t_purchase_invoice).select(_t_purchase_invoice.star)
               .where(_t_purchase_invoice.id == P()))
        pi = conn.execute(piq.get_sql(), (pi_id,)).fetchone()
        if pi and pi["status"] in ("submitted", "overdue", "partially_paid"):
            pi_voucher = "debit_note" if pi["is_return"] else "purchase_invoice"
            pi_posting = pi["posting_date"]

            # Reverse PI GL
            rev_pi_gl = reverse_gl_entries(conn, pi_voucher, pi_id, pi_posting)
            pi_gl_reversals = len(rev_pi_gl)

            # Reverse PI SLE if applicable
            if pi["update_stock"]:
                rev_pi_sle = reverse_sle_entries(conn, pi_voucher, pi_id, pi_posting)
                pi_sle_reversals = len(rev_pi_sle)

            # Mark PI PLE as delinked
            pi_ple_uq = (Q.update(_t_payment_ledger)
                         .set("delinked", 1)
                         .where(_t_payment_ledger.voucher_type == P())
                         .where(_t_payment_ledger.voucher_id == P()))
            conn.execute(pi_ple_uq.get_sql(), (pi_voucher, pi_id))

            # Update PI status
            pi_uq = (Q.update(_t_purchase_invoice)
                     .set("status", ValueWrapper("cancelled"))
                     .set("outstanding_amount", ValueWrapper("0"))
                     .where(_t_purchase_invoice.id == P()))
            conn.execute(pi_uq.get_sql(), (pi_id,))
        elif pi and pi["status"] == "draft":
            # Just delete the draft PI and its items
            dq1 = (Q.from_(_t_purchase_invoice_item).delete()
                   .where(_t_purchase_invoice_item.purchase_invoice_id == P()))
            conn.execute(dq1.get_sql(), (pi_id,))
            dq2 = (Q.from_(_t_purchase_invoice).delete()
                   .where(_t_purchase_invoice.id == P()))
            conn.execute(dq2.get_sql(), (pi_id,))

    conn.commit()
    ok({
        "sales_invoice_id": si_id,
        "purchase_invoice_id": pi_id,
        "si_status": "cancelled",
        "si_gl_reversals": si_gl_reversals,
        "si_sle_reversals": si_sle_reversals,
        "pi_gl_reversals": pi_gl_reversals,
        "pi_sle_reversals": pi_sle_reversals,
    })


# ---------------------------------------------------------------------------
# close-sales-order
# ---------------------------------------------------------------------------

def close_sales_order(conn, args):
    """Close a partially-fulfilled SO. Prevents further DNs/invoices but
    preserves existing child documents."""
    if not args.sales_order_id:
        err("--sales-order-id is required")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")
    if so["status"] in ("draft", "cancelled", "closed"):
        err(f"Cannot close: sales order is '{so['status']}'")

    close_reason = args.reason or None
    closed_by = args.closed_by or None

    uq = (Q.update(_t_sales_order)
          .set("status", ValueWrapper("closed"))
          .set("close_reason", P())
          .set("closed_by", P())
          .set("updated_at", LiteralValue("datetime('now')"))
          .where(_t_sales_order.id == P()))
    conn.execute(uq.get_sql(), (close_reason, closed_by, args.sales_order_id))

    audit(conn, "erpclaw-selling", "close-sales-order", "sales_order",
          args.sales_order_id,
          new_values={"status": "closed", "close_reason": close_reason,
                      "closed_by": closed_by})
    conn.commit()
    ok({"sales_order_id": args.sales_order_id, "doc_status": "closed",
        "close_reason": close_reason, "closed_by": closed_by})


# ---------------------------------------------------------------------------
# amend-sales-order
# ---------------------------------------------------------------------------

def amend_sales_order(conn, args):
    """Amend a sales order: cancel original (if no child docs) and create a
    new SO linked via amended_from. Changes supplied via --items JSON;
    unspecified items are copied from the original."""
    if not args.sales_order_id:
        err("--sales-order-id is required")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")
    if so["status"] in ("draft", "cancelled", "closed"):
        err(f"Cannot amend: sales order is '{so['status']}'")

    # Block if any active delivery notes exist
    dnc = (Q.from_(_t_delivery_note)
           .select(fn.Count("*").as_("cnt"))
           .where(_t_delivery_note.sales_order_id == P())
           .where(_t_delivery_note.status != ValueWrapper("cancelled")))
    dn_count = conn.execute(dnc.get_sql(), (args.sales_order_id,)).fetchone()["cnt"]
    if dn_count > 0:
        err(f"Cannot amend: {dn_count} active delivery note(s) linked to this order")

    # Block if any active invoices exist
    sic = (Q.from_(_t_sales_invoice)
           .select(fn.Count("*").as_("cnt"))
           .where(_t_sales_invoice.sales_order_id == P())
           .where(_t_sales_invoice.status != ValueWrapper("cancelled")))
    si_count = conn.execute(sic.get_sql(), (args.sales_order_id,)).fetchone()["cnt"]
    if si_count > 0:
        err(f"Cannot amend: {si_count} active sales invoice(s) linked to this order")

    so_dict = row_to_dict(so)

    # Cancel original SO
    uq_cancel = (Q.update(_t_sales_order)
                 .set("status", ValueWrapper("cancelled"))
                 .set("updated_at", LiteralValue("datetime('now')"))
                 .where(_t_sales_order.id == P()))
    conn.execute(uq_cancel.get_sql(), (args.sales_order_id,))
    audit(conn, "erpclaw-selling", "amend-sales-order", "sales_order",
          args.sales_order_id,
          new_values={"status": "cancelled", "reason": "amended"})

    # Determine items for the new SO
    if args.items:
        items = _parse_json_arg(args.items, "items")
    else:
        # Copy items from original
        soiq = (Q.from_(_t_sales_order_item).select(_t_sales_order_item.star)
                .where(_t_sales_order_item.sales_order_id == P())
                .orderby(_t_sales_order_item.rowid))
        so_items = conn.execute(soiq.get_sql(), (args.sales_order_id,)).fetchall()
        items = []
        for soi in so_items:
            soi_d = row_to_dict(soi)
            items.append({
                "item_id": soi_d["item_id"],
                "qty": soi_d["quantity"],
                "rate": soi_d["rate"],
                "warehouse_id": soi_d.get("warehouse_id"),
            })

    total_amount, item_rows = _calculate_line_items(
        conn, items, so_dict["company_id"], so_dict["customer_id"],
        so_dict["order_date"], apply_pricing=True)
    tax_amount, _ = _calculate_tax(conn, total_amount, so_dict.get("tax_template_id"))
    grand_total = round_currency(total_amount + tax_amount)

    new_so_id = str(uuid.uuid4())

    so_ins = (Q.into(_t_sales_order)
              .columns("id", "customer_id", "order_date", "delivery_date",
                        "total_amount", "tax_amount", "grand_total",
                        "tax_template_id", "status", "company_id",
                        "amended_from")
              .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                      ValueWrapper("draft"), P(), P()))
    conn.execute(so_ins.get_sql(),
        (new_so_id, so_dict["customer_id"], so_dict["order_date"],
         so_dict.get("delivery_date"),
         str(total_amount), str(tax_amount), str(grand_total),
         so_dict.get("tax_template_id"), so_dict["company_id"],
         args.sales_order_id),
    )

    soi_ins = (Q.into(_t_sales_order_item)
               .columns("id", "sales_order_id", "item_id", "quantity", "uom",
                         "rate", "amount", "discount_percentage",
                         "net_amount", "warehouse_id")
               .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    soi_ins_sql = soi_ins.get_sql()
    for row in item_rows:
        conn.execute(soi_ins_sql,
            (str(uuid.uuid4()), new_so_id, row["item_id"], row["qty"],
             row["uom"], row["rate"], row["amount"],
             row["discount_percentage"], row["net_amount"],
             row["warehouse_id"]),
        )

    audit(conn, "erpclaw-selling", "amend-sales-order", "sales_order", new_so_id,
          new_values={"amended_from": args.sales_order_id,
                      "grand_total": str(grand_total)})
    conn.commit()
    ok({"new_sales_order_id": new_so_id, "amended_from": args.sales_order_id,
        "original_status": "cancelled",
        "total_amount": str(total_amount), "tax_amount": str(tax_amount),
        "grand_total": str(grand_total)})


# ---------------------------------------------------------------------------
# get-amendment-history
# ---------------------------------------------------------------------------

def get_amendment_history(conn, args):
    """Trace the full amendment chain for a sales order (both ancestors and
    descendants)."""
    if not args.sales_order_id:
        err("--sales-order-id is required")

    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")

    chain = []

    # Walk backwards to root
    current_id = args.sales_order_id
    ancestors = []
    while True:
        row = conn.execute(soq.get_sql(), (current_id,)).fetchone()
        if not row:
            break
        row_d = row_to_dict(row)
        if row_d.get("amended_from"):
            ancestors.append({
                "sales_order_id": current_id,
                "status": row_d["status"],
                "amended_from": row_d["amended_from"],
                "grand_total": row_d["grand_total"],
            })
            current_id = row_d["amended_from"]
        else:
            # This is the root
            ancestors.append({
                "sales_order_id": current_id,
                "status": row_d["status"],
                "amended_from": None,
                "grand_total": row_d["grand_total"],
            })
            break

    ancestors.reverse()
    chain.extend(ancestors)

    # Walk forward to find descendants
    current_id = args.sales_order_id
    descq = (Q.from_(_t_sales_order)
             .select(_t_sales_order.id, _t_sales_order.status,
                     _t_sales_order.amended_from, _t_sales_order.grand_total)
             .where(_t_sales_order.amended_from == P()))
    while True:
        desc = conn.execute(descq.get_sql(), (current_id,)).fetchone()
        if not desc:
            break
        desc_d = row_to_dict(desc)
        chain.append({
            "sales_order_id": desc_d["id"],
            "status": desc_d["status"],
            "amended_from": desc_d["amended_from"],
            "grand_total": desc_d["grand_total"],
        })
        current_id = desc_d["id"]

    ok({"sales_order_id": args.sales_order_id,
        "amendment_chain": chain,
        "chain_length": len(chain)})


# ---------------------------------------------------------------------------
# Feature #15: Drop Shipment (Sprint 7)
# ---------------------------------------------------------------------------


def create_drop_ship_order(conn, args):
    """Create a purchase order from SO drop-ship items.

    Required: --sales-order-id, --supplier-id
    Optional: --posting-date

    Creates a PO with delivery_address = customer address.
    Links PO items back to SO items via purchase_order_item.
    """
    if not args.sales_order_id:
        err("--sales-order-id is required")
    if not args.supplier_id:
        err("--supplier-id is required")

    # Validate SO
    soq = (Q.from_(_t_sales_order).select(_t_sales_order.star)
           .where(_t_sales_order.id == P()))
    so = conn.execute(soq.get_sql(), (args.sales_order_id,)).fetchone()
    if not so:
        err(f"Sales order {args.sales_order_id} not found")
    so_dict = row_to_dict(so)
    if so_dict["status"] not in ("confirmed", "partially_delivered"):
        err(f"Cannot create drop-ship PO: SO status is '{so_dict['status']}'")

    # Validate supplier
    sup_t = Table("supplier")
    sq = Q.from_(sup_t).select(sup_t.star).where(sup_t.id == P())
    supplier = conn.execute(sq.get_sql(), (args.supplier_id,)).fetchone()
    if not supplier:
        err(f"Supplier {args.supplier_id} not found")

    # Get SO items with is_drop_ship = 1
    soiq = (Q.from_(_t_sales_order_item).select(_t_sales_order_item.star)
            .where(_t_sales_order_item.sales_order_id == P())
            .where(_t_sales_order_item.is_drop_ship == 1)
            .orderby(_t_sales_order_item.rowid))
    so_items = conn.execute(soiq.get_sql(), (args.sales_order_id,)).fetchall()
    if not so_items:
        err("No drop-ship items found in this sales order")

    posting_date = args.posting_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    po_id = str(uuid.uuid4())

    # Get customer address for delivery
    cust_t = Table("customer")
    cust_q = Q.from_(cust_t).select(cust_t.primary_address).where(cust_t.id == P())
    cust_row = conn.execute(cust_q.get_sql(), (so_dict["customer_id"],)).fetchone()
    delivery_address = row_to_dict(cust_row).get("primary_address") if cust_row else None

    total_amount = Decimal("0")
    po_items = []

    for soi_row in so_items:
        soi = row_to_dict(soi_row)
        remaining = to_decimal(soi["quantity"]) - to_decimal(soi["delivered_qty"])
        if remaining <= 0:
            continue

        rate = to_decimal(soi["rate"])
        amount = round_currency(remaining * rate)
        total_amount += amount

        po_items.append({
            "id": str(uuid.uuid4()),
            "item_id": soi["item_id"],
            "qty": str(round_currency(remaining)),
            "uom": soi.get("uom"),
            "rate": str(round_currency(rate)),
            "amount": str(amount),
            "so_item_id": soi["id"],
            "warehouse_id": soi.get("warehouse_id"),
        })

    if not po_items:
        err("No drop-ship items with remaining quantity")

    # Insert PO
    po_t = Table("purchase_order")
    po_ins = (Q.into(po_t)
              .columns("id", "supplier_id", "order_date", "total_amount",
                       "tax_amount", "grand_total", "status", "company_id",
                       "delivery_address")
              .insert(P(), P(), P(), P(), P(), P(), ValueWrapper("draft"),
                      P(), P()))
    conn.execute(po_ins.get_sql(),
                 (po_id, args.supplier_id, posting_date,
                  str(round_currency(total_amount)), "0",
                  str(round_currency(total_amount)),
                  so_dict["company_id"], delivery_address))

    # Insert PO items
    poi_t = Table("purchase_order_item")
    poi_ins = (Q.into(poi_t)
               .columns("id", "purchase_order_id", "item_id", "quantity",
                         "uom", "rate", "amount", "discount_percentage",
                         "net_amount", "warehouse_id")
               .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    poi_sql = poi_ins.get_sql()
    for item in po_items:
        conn.execute(poi_sql,
                     (item["id"], po_id, item["item_id"], item["qty"],
                      item["uom"], item["rate"], item["amount"],
                      "0", item["amount"], item["warehouse_id"]))

    audit(conn, "erpclaw-selling", "create-drop-ship-order",
          "purchase_order", po_id,
          new_values={"sales_order_id": args.sales_order_id,
                      "supplier_id": args.supplier_id,
                      "item_count": len(po_items)})
    conn.commit()

    ok({
        "purchase_order_id": po_id,
        "sales_order_id": args.sales_order_id,
        "supplier_id": args.supplier_id,
        "delivery_address": delivery_address,
        "total_amount": str(round_currency(total_amount)),
        "item_count": len(po_items),
        "message": "Drop-ship purchase order created",
    })


# ---------------------------------------------------------------------------
# Feature #16: Packing Slip (Sprint 7)
# ---------------------------------------------------------------------------

_t_packing_slip = Table("packing_slip")
_t_packing_slip_item = Table("packing_slip_item")


def add_packing_slip(conn, args):
    """Add a packing slip linked to a delivery note.

    Required: --delivery-note-id, --items (JSON)
    Items format: [{"delivery_note_item_id": "...", "qty_packed": "10"}]
    Optional: --notes
    """
    if not args.delivery_note_id:
        err("--delivery-note-id is required")
    if not args.items:
        err("--items is required")

    # Validate DN exists
    dnq = (Q.from_(_t_delivery_note).select(_t_delivery_note.star)
           .where(_t_delivery_note.id == P()))
    dn = conn.execute(dnq.get_sql(), (args.delivery_note_id,)).fetchone()
    if not dn:
        err(f"Delivery note {args.delivery_note_id} not found")
    dn_dict = row_to_dict(dn)

    items_arg = _parse_json_arg(args.items, "items")
    if not items_arg or not isinstance(items_arg, list):
        err("--items must be a non-empty JSON array")

    posting_date = args.posting_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ps_id = str(uuid.uuid4())

    # Validate each item
    ps_items = []
    for i, item in enumerate(items_arg):
        dni_id = item.get("delivery_note_item_id")
        if not dni_id:
            err(f"Item {i}: delivery_note_item_id is required")

        # Look up DN item
        dniq = (Q.from_(_t_delivery_note_item).select(_t_delivery_note_item.star)
                .where(_t_delivery_note_item.id == P())
                .where(_t_delivery_note_item.delivery_note_id == P()))
        dni = conn.execute(dniq.get_sql(), (dni_id, args.delivery_note_id)).fetchone()
        if not dni:
            err(f"Item {i}: delivery note item {dni_id} not found in DN {args.delivery_note_id}")

        dni_dict = row_to_dict(dni)
        qty_packed = to_decimal(item.get("qty_packed", "0"))
        dn_qty = to_decimal(dni_dict["quantity"])

        if qty_packed <= 0:
            err(f"Item {i}: qty_packed must be > 0")

        # Check total packed qty across all packing slips for this DN item
        existing_q = (Q.from_(_t_packing_slip_item)
                      .select(fn.Sum(_t_packing_slip_item.qty_packed))
                      .where(_t_packing_slip_item.delivery_note_item_id == P()))
        existing = conn.execute(existing_q.get_sql(), (dni_id,)).fetchone()
        already_packed = to_decimal(str(existing[0])) if existing and existing[0] else Decimal("0")

        if qty_packed + already_packed > dn_qty:
            err(f"Item {i}: packed qty {qty_packed} + already packed {already_packed} "
                f"exceeds DN qty {dn_qty}")

        ps_items.append({
            "id": str(uuid.uuid4()),
            "item_id": dni_dict["item_id"],
            "delivery_note_item_id": dni_id,
            "qty_packed": str(round_currency(qty_packed)),
            "uom": dni_dict.get("uom"),
            "notes": item.get("notes"),
        })

    # Insert packing slip
    ps_ins = (Q.into(_t_packing_slip)
              .columns("id", "delivery_note_id", "posting_date", "notes",
                        "company_id", "created_at", "updated_at")
              .insert(P(), P(), P(), P(), P(), P(), P()))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(ps_ins.get_sql(),
                 (ps_id, args.delivery_note_id, posting_date,
                  getattr(args, "notes", None) or getattr(args, "reason", None),
                  dn_dict["company_id"], now, now))

    # Insert packing slip items
    psi_ins = (Q.into(_t_packing_slip_item)
               .columns("id", "packing_slip_id", "item_id",
                         "delivery_note_item_id", "qty_packed", "uom", "notes")
               .insert(P(), P(), P(), P(), P(), P(), P()))
    psi_sql = psi_ins.get_sql()
    for item in ps_items:
        conn.execute(psi_sql,
                     (item["id"], ps_id, item["item_id"],
                      item["delivery_note_item_id"], item["qty_packed"],
                      item["uom"], item["notes"]))

    audit(conn, "erpclaw-selling", "add-packing-slip",
          "packing_slip", ps_id,
          new_values={"delivery_note_id": args.delivery_note_id,
                      "item_count": len(ps_items)})
    conn.commit()

    ok({
        "packing_slip_id": ps_id,
        "delivery_note_id": args.delivery_note_id,
        "item_count": len(ps_items),
        "message": "Packing slip created",
    })


def get_packing_slip(conn, args):
    """Get a packing slip with its items.

    Required: --packing-slip-id
    """
    if not args.packing_slip_id:
        err("--packing-slip-id is required")

    psq = (Q.from_(_t_packing_slip).select(_t_packing_slip.star)
           .where(_t_packing_slip.id == P()))
    ps = conn.execute(psq.get_sql(), (args.packing_slip_id,)).fetchone()
    if not ps:
        err(f"Packing slip {args.packing_slip_id} not found")

    data = row_to_dict(ps)

    psiq = (Q.from_(_t_packing_slip_item)
            .left_join(_t_item).on(_t_item.id == _t_packing_slip_item.item_id)
            .select(_t_packing_slip_item.star,
                    _t_item.item_code, _t_item.item_name)
            .where(_t_packing_slip_item.packing_slip_id == P())
            .orderby(_t_packing_slip_item.rowid))
    items = conn.execute(psiq.get_sql(), (args.packing_slip_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    ok(data)


def list_packing_slips(conn, args):
    """List packing slips.

    Optional: --delivery-note-id, --company-id
    """
    ps = _t_packing_slip.as_("ps")
    q = Q.from_(ps).select(ps.star)
    params = []

    if args.delivery_note_id:
        q = q.where(ps.delivery_note_id == P())
        params.append(args.delivery_note_id)

    if args.company_id:
        q = q.where(ps.company_id == P())
        params.append(args.company_id)

    q = q.orderby(ps.created_at, order=Order.desc)
    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    q = q.limit(limit).offset(offset)

    rows = conn.execute(q.get_sql(), params).fetchall()
    ok({"packing_slips": [row_to_dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-customer": add_customer,
    "update-customer": update_customer,
    "get-customer": get_customer,
    "list-customers": list_customers,
    "add-quotation": add_quotation,
    "update-quotation": update_quotation,
    "get-quotation": get_quotation,
    "list-quotations": list_quotations,
    "submit-quotation": submit_quotation,
    "convert-quotation-to-so": convert_quotation_to_so,
    "add-sales-order": add_sales_order,
    "update-sales-order": update_sales_order,
    "get-sales-order": get_sales_order,
    "list-sales-orders": list_sales_orders,
    "submit-sales-order": submit_sales_order,
    "cancel-sales-order": cancel_sales_order,
    "close-sales-order": close_sales_order,
    "amend-sales-order": amend_sales_order,
    "get-amendment-history": get_amendment_history,
    "create-delivery-note": create_delivery_note,
    "get-delivery-note": get_delivery_note,
    "list-delivery-notes": list_delivery_notes,
    "submit-delivery-note": submit_delivery_note,
    "cancel-delivery-note": cancel_delivery_note,
    "create-sales-invoice": create_sales_invoice,
    "update-sales-invoice": update_sales_invoice,
    "get-sales-invoice": get_sales_invoice,
    "list-sales-invoices": list_sales_invoices,
    "submit-sales-invoice": submit_sales_invoice,
    "cancel-sales-invoice": cancel_sales_invoice,
    "create-credit-note": create_credit_note,
    "list-credit-notes": list_credit_notes,
    "update-invoice-outstanding": update_invoice_outstanding,
    "add-sales-partner": add_sales_partner,
    "list-sales-partners": list_sales_partners,
    "add-recurring-template": add_recurring_template,
    "update-recurring-template": update_recurring_template,
    "list-recurring-templates": list_recurring_templates,
    "generate-recurring-invoices": generate_recurring_invoices,
    "add-blanket-order": add_blanket_order,
    "submit-blanket-order": submit_blanket_order,
    "get-blanket-order": get_blanket_order,
    "list-blanket-orders": list_blanket_orders,
    "create-so-from-blanket": create_so_from_blanket,
    "import-customers": import_customers,
    "add-intercompany-account-map": add_intercompany_account_map,
    "list-intercompany-account-maps": list_intercompany_account_maps,
    "create-intercompany-invoice": create_intercompany_invoice,
    "list-intercompany-invoices": list_intercompany_invoices,
    "cancel-intercompany-invoice": cancel_intercompany_invoice,

    # --- Sprint 7: Drop Shipment & Packing Slip ---
    "create-drop-ship-order": create_drop_ship_order,
    "add-packing-slip": add_packing_slip,
    "get-packing-slip": get_packing_slip,
    "list-packing-slips": list_packing_slips,

    "status": status_action,
}


def main():
    parser = SafeArgumentParser(description="ERPClaw Selling Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Customer fields
    parser.add_argument("--customer-id")
    parser.add_argument("--customer-type")
    parser.add_argument("--customer-group")
    parser.add_argument("--payment-terms-id")
    parser.add_argument("--credit-limit")
    parser.add_argument("--tax-id")
    parser.add_argument("--exempt-from-sales-tax")
    parser.add_argument("--primary-address")
    parser.add_argument("--primary-contact")

    # Common fields
    parser.add_argument("--name")
    parser.add_argument("--company-id")
    parser.add_argument("--csv-path")
    parser.add_argument("--posting-date")
    parser.add_argument("--items")  # JSON
    parser.add_argument("--tax-template-id")

    # Quotation fields
    parser.add_argument("--quotation-id")
    parser.add_argument("--valid-till")

    # Sales order fields
    parser.add_argument("--sales-order-id")
    parser.add_argument("--delivery-date")

    # Delivery note fields
    parser.add_argument("--delivery-note-id")

    # Sales invoice fields
    parser.add_argument("--sales-invoice-id")
    parser.add_argument("--due-date")

    # Credit note / close fields
    parser.add_argument("--against-invoice-id")
    parser.add_argument("--reason")
    parser.add_argument("--closed-by")

    # Payment / outstanding
    parser.add_argument("--amount")

    # Sales partner
    parser.add_argument("--commission-rate")

    # Recurring template fields
    parser.add_argument("--template-id")
    parser.add_argument("--frequency")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--as-of-date")
    parser.add_argument("--template-status", dest="template_status")

    # Blanket order fields
    parser.add_argument("--blanket-order-id")
    parser.add_argument("--valid-from")
    parser.add_argument("--valid-to")

    # Intercompany fields
    parser.add_argument("--target-company-id")
    parser.add_argument("--supplier-id")
    parser.add_argument("--source-account-id")
    parser.add_argument("--target-account-id")

    # Packing slip fields (Feature #16)
    parser.add_argument("--packing-slip-id")

    # Warehouse override
    parser.add_argument("--warehouse-id")

    # Status filter (for list queries)
    parser.add_argument("--status", dest="doc_status")

    # Search / pagination
    parser.add_argument("--search")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")

    args, unknown = parser.parse_known_args()
    check_unknown_args(parser, unknown)
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
        sys.stderr.write(f"[erpclaw-selling] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
