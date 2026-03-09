#!/usr/bin/env python3
"""ERPClaw Inventory Skill — db_query.py

Items, warehouses, stock entries, stock ledger, batches, serial numbers,
pricing, and stock reconciliation. Draft->Submit->Cancel lifecycle for
stock entries and reconciliation. Submit posts SLE + GL via shared lib.

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
    from erpclaw_lib.query_helpers import resolve_company_id
    from erpclaw_lib.query import Q, P, Table, Field, fn, DecimalSum, DecimalAbs
    from erpclaw_lib.vendor.pypika import Order
    from erpclaw_lib.vendor.pypika.terms import LiteralValue
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

# Convenience alias for datetime('now') SQLite expression
_NOW = LiteralValue("datetime('now')")

REQUIRED_TABLES = ["company"]

VALID_ITEM_TYPES = ("stock", "non_stock", "service")
VALID_VALUATION_METHODS = ("moving_average", "fifo")
VALID_WAREHOUSE_TYPES = ("stores", "production", "transit", "rejected")
VALID_SERIAL_STATUSES = ("active", "delivered", "returned", "scrapped")

# User-friendly entry type -> DB value
ENTRY_TYPE_MAP = {
    "receive": "material_receipt",
    "issue": "material_issue",
    "transfer": "material_transfer",
    "manufacture": "manufacture",
    # Also accept DB values directly
    "material_receipt": "material_receipt",
    "material_issue": "material_issue",
    "material_transfer": "material_transfer",
}



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
    fy = conn.execute(
        "SELECT name FROM fiscal_year WHERE start_date <= ? AND end_date >= ? AND is_closed = 0",
        (posting_date, posting_date),
    ).fetchone()
    return fy["name"] if fy else None


def _get_cost_center(conn, company_id: str) -> str | None:
    """Return the first non-group cost center for a company, or None."""
    t = Table("cost_center")
    q = (Q.from_(t).select(t.id)
         .where(t.company_id == P())
         .where(t.is_group == 0)
         .limit(1))
    cc = conn.execute(q.get_sql(), (company_id,)).fetchone()
    return cc["id"] if cc else None


# ---------------------------------------------------------------------------
# 1. add-item
# ---------------------------------------------------------------------------

def add_item(conn, args):
    """Create a new item."""
    if not args.item_code:
        err("--item-code is required")
    if not args.item_name:
        err("--item-name is required")

    item_type = args.item_type or "stock"
    if item_type not in VALID_ITEM_TYPES:
        err(f"--item-type must be one of: {', '.join(VALID_ITEM_TYPES)}")

    valuation_method = args.valuation_method or "moving_average"
    if valuation_method not in VALID_VALUATION_METHODS:
        err(f"--valuation-method must be one of: {', '.join(VALID_VALUATION_METHODS)}")

    # Validate item group if provided (accept id or name)
    if args.item_group:
        ig_t = Table("item_group")
        ig_q = (Q.from_(ig_t).select(ig_t.id)
                .where((ig_t.id == P()) | (ig_t.name == P())))
        ig = conn.execute(ig_q.get_sql(), (args.item_group, args.item_group)).fetchone()
        if not ig:
            err(f"Item group {args.item_group} not found")
        args.item_group = ig[0]  # normalize to id

    is_stock_item = 1 if item_type == "stock" else 0
    has_batch = int(args.has_batch) if args.has_batch else 0
    has_serial = int(args.has_serial) if args.has_serial else 0
    standard_rate = str(round_currency(to_decimal(args.standard_rate or "0")))

    item_id = str(uuid.uuid4())
    t = Table("item")
    q = Q.into(t).columns(
        "id", "item_code", "item_name", "item_group_id", "item_type", "stock_uom",
        "valuation_method", "is_stock_item", "has_batch", "has_serial",
        "standard_rate", "status",
    ).insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), "active")
    try:
        conn.execute(
            q.get_sql(),
            (item_id, args.item_code, args.item_name, args.item_group,
             item_type, args.stock_uom or "Nos",
             valuation_method, is_stock_item, has_batch, has_serial,
             standard_rate),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err("Item creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-inventory", "add-item", "item", item_id,
           new_values={"item_code": args.item_code, "item_name": args.item_name})
    conn.commit()
    ok({"item_id": item_id, "item_code": args.item_code,
         "item_name": args.item_name})


# ---------------------------------------------------------------------------
# 2. update-item
# ---------------------------------------------------------------------------

def update_item(conn, args):
    """Update an existing item."""
    if not args.item_id:
        err("--item-id is required")

    t = Table("item")
    q = Q.from_(t).select(t.star).where(t.id == P())
    item = conn.execute(q.get_sql(), (args.item_id,)).fetchone()
    if not item:
        err(f"Item {args.item_id} not found",
             suggestion="Use 'list items' to see available items.")

    if item["status"] == "disabled" and args.item_status != "active":
        err("Cannot update a disabled item (set --status active first)")

    updates, params, updated_fields = [], [], []

    if args.item_name is not None:
        updates.append("item_name = ?")
        params.append(args.item_name)
        updated_fields.append("item_name")
    if args.reorder_level is not None:
        updates.append("reorder_level = ?")
        params.append(args.reorder_level)
        updated_fields.append("reorder_level")
    if args.reorder_qty is not None:
        updates.append("reorder_qty = ?")
        params.append(args.reorder_qty)
        updated_fields.append("reorder_qty")
    if args.standard_rate is not None:
        updates.append("standard_rate = ?")
        params.append(str(round_currency(to_decimal(args.standard_rate))))
        updated_fields.append("standard_rate")
    if args.item_status is not None:
        if args.item_status not in ("active", "disabled"):
            err("--status must be 'active' or 'disabled'")
        updates.append("status = ?")
        params.append(args.item_status)
        updated_fields.append("status")

    if not updated_fields:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(args.item_id)
    conn.execute(f"UPDATE item SET {', '.join(updates)} WHERE id = ?", params)

    audit(conn, "erpclaw-inventory", "update-item", "item", args.item_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"item_id": args.item_id, "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 3. get-item
# ---------------------------------------------------------------------------

def get_item(conn, args):
    """Get item with stock summary across all warehouses."""
    if not args.item_id:
        err("--item-id is required")

    t = Table("item")
    q = Q.from_(t).select(t.star).where(t.id == P())
    item = conn.execute(q.get_sql(), (args.item_id,)).fetchone()
    if not item:
        err(f"Item {args.item_id} not found")

    data = row_to_dict(item)

    # Stock balances per warehouse
    sle = Table("stock_ledger_entry")
    wh_q = (Q.from_(sle)
            .select(sle.warehouse_id).distinct()
            .where(sle.item_id == P())
            .where(sle.is_cancelled == 0))
    warehouses = conn.execute(wh_q.get_sql(), (args.item_id,)).fetchall()

    stock_balances = []
    total_qty = Decimal("0")
    total_value = Decimal("0")
    for wh_row in warehouses:
        wh_id = wh_row["warehouse_id"]
        balance = get_stock_balance(conn, args.item_id, wh_id)
        qty = to_decimal(balance["qty"])
        val = to_decimal(balance["stock_value"])
        if qty != 0 or val != 0:
            wh_t = Table("warehouse")
            wh_q2 = Q.from_(wh_t).select(wh_t.name).where(wh_t.id == P())
            wh = conn.execute(wh_q2.get_sql(), (wh_id,)).fetchone()
            stock_balances.append({
                "warehouse_id": wh_id,
                "warehouse_name": wh["name"] if wh else wh_id,
                "qty": balance["qty"],
                "valuation_rate": balance["valuation_rate"],
                "stock_value": balance["stock_value"],
            })
            total_qty += qty
            total_value += val

    data["stock_balances"] = stock_balances
    data["total_qty"] = str(round_currency(total_qty))
    data["total_stock_value"] = str(round_currency(total_value))
    ok(data)


# ---------------------------------------------------------------------------
# 4. list-items
# ---------------------------------------------------------------------------

def list_items(conn, args):
    """Query items with filtering."""
    i = Table("item").as_("i")

    # Warehouse filter: items that have stock in a specific warehouse
    warehouse_id = getattr(args, "warehouse_id", None)

    # Build count query
    count_q = Q.from_(i).select(fn.Count("*"))
    if warehouse_id:
        sle = Table("stock_ledger_entry")
        sub = (Q.from_(sle).select(sle.item_id).distinct()
               .where(sle.warehouse_id == P()).where(sle.is_cancelled == 0))
        count_q = count_q.where(i.id.isin(sub))
    if args.item_group:
        count_q = count_q.where(i.item_group_id == P())
    if args.item_type:
        count_q = count_q.where(i.item_type == P())
    if args.search:
        count_q = count_q.where(
            (i.item_name.like(P())) | (i.item_code.like(P()))
        )

    count_params = []
    if warehouse_id:
        count_params.append(warehouse_id)
    if args.item_group:
        count_params.append(args.item_group)
    if args.item_type:
        count_params.append(args.item_type)
    if args.search:
        count_params.extend([f"%{args.search}%", f"%{args.search}%"])

    count_row = conn.execute(count_q.get_sql(), count_params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    rows_q = (Q.from_(i)
              .select(i.id, i.item_code, i.item_name, i.item_group_id,
                      i.item_type, i.stock_uom, i.standard_rate, i.status,
                      i.has_batch, i.has_serial)
              .orderby(i.item_name)
              .limit(P()).offset(P()))
    if warehouse_id:
        sle = Table("stock_ledger_entry")
        sub = (Q.from_(sle).select(sle.item_id).distinct()
               .where(sle.warehouse_id == P()).where(sle.is_cancelled == 0))
        rows_q = rows_q.where(i.id.isin(sub))
    if args.item_group:
        rows_q = rows_q.where(i.item_group_id == P())
    if args.item_type:
        rows_q = rows_q.where(i.item_type == P())
    if args.search:
        rows_q = rows_q.where(
            (i.item_name.like(P())) | (i.item_code.like(P()))
        )

    row_params = []
    if warehouse_id:
        row_params.append(warehouse_id)
    if args.item_group:
        row_params.append(args.item_group)
    if args.item_type:
        row_params.append(args.item_type)
    if args.search:
        row_params.extend([f"%{args.search}%", f"%{args.search}%"])
    row_params.extend([limit, offset])

    rows = conn.execute(rows_q.get_sql(), row_params).fetchall()

    ok({"items": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 5. add-item-group
# ---------------------------------------------------------------------------

def add_item_group(conn, args):
    """Create an item group."""
    if not args.name:
        err("--name is required")

    if args.parent_id:
        ig_t = Table("item_group")
        parent_q = Q.from_(ig_t).select(ig_t.id).where(ig_t.id == P())
        parent = conn.execute(parent_q.get_sql(), (args.parent_id,)).fetchone()
        if not parent:
            err(f"Parent item group {args.parent_id} not found")

    ig_id = str(uuid.uuid4())
    t = Table("item_group")
    q = Q.into(t).columns("id", "name", "parent_id").insert(P(), P(), P())
    try:
        conn.execute(q.get_sql(), (ig_id, args.name, args.parent_id))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err("Item group creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-inventory", "add-item-group", "item_group", ig_id,
           new_values={"name": args.name})
    conn.commit()
    ok({"item_group_id": ig_id, "name": args.name})


# ---------------------------------------------------------------------------
# 6. list-item-groups
# ---------------------------------------------------------------------------

def list_item_groups(conn, args):
    """List item groups."""
    t = Table("item_group")

    count_q = Q.from_(t).select(fn.Count("*"))
    if args.parent_id:
        count_q = count_q.where(t.parent_id == P())

    count_params = []
    if args.parent_id:
        count_params.append(args.parent_id)

    count_row = conn.execute(count_q.get_sql(), count_params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    rows_q = (Q.from_(t).select(t.star)
              .orderby(t.name)
              .limit(P()).offset(P()))
    if args.parent_id:
        rows_q = rows_q.where(t.parent_id == P())

    row_params = []
    if args.parent_id:
        row_params.append(args.parent_id)
    row_params.extend([limit, offset])

    rows = conn.execute(rows_q.get_sql(), row_params).fetchall()

    ok({"item_groups": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 7. add-warehouse
# ---------------------------------------------------------------------------

def add_warehouse(conn, args):
    """Create a warehouse."""
    if not args.name:
        err("--name is required")
    if not args.company_id:
        err("--company-id is required")

    co_t = Table("company")
    co_q = Q.from_(co_t).select(co_t.id).where(co_t.id == P())
    if not conn.execute(co_q.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    wh_type = args.warehouse_type or "stores"
    if wh_type not in VALID_WAREHOUSE_TYPES:
        err(f"--warehouse-type must be one of: {', '.join(VALID_WAREHOUSE_TYPES)}")

    if args.parent_id:
        wh_t = Table("warehouse")
        parent_q = Q.from_(wh_t).select(wh_t.id).where(wh_t.id == P())
        parent = conn.execute(parent_q.get_sql(), (args.parent_id,)).fetchone()
        if not parent:
            err(f"Parent warehouse {args.parent_id} not found")

    if args.account_id:
        acct_t = Table("account")
        acct_q = Q.from_(acct_t).select(acct_t.id).where(acct_t.id == P())
        acct = conn.execute(acct_q.get_sql(), (args.account_id,)).fetchone()
        if not acct:
            err(f"Account {args.account_id} not found")

    is_group = int(args.is_group) if args.is_group else 0
    wh_id = str(uuid.uuid4())
    t = Table("warehouse")
    q = Q.into(t).columns(
        "id", "name", "parent_id", "warehouse_type",
        "company_id", "account_id", "is_group",
    ).insert(P(), P(), P(), P(), P(), P(), P())
    conn.execute(
        q.get_sql(),
        (wh_id, args.name, args.parent_id, wh_type,
         args.company_id, args.account_id, is_group),
    )

    audit(conn, "erpclaw-inventory", "add-warehouse", "warehouse", wh_id,
           new_values={"name": args.name, "type": wh_type})
    conn.commit()
    ok({"warehouse_id": wh_id, "name": args.name})


# ---------------------------------------------------------------------------
# 8. update-warehouse
# ---------------------------------------------------------------------------

def update_warehouse(conn, args):
    """Update a warehouse."""
    if not args.warehouse_id:
        err("--warehouse-id is required")

    wh_t = Table("warehouse")
    wh_q = (Q.from_(wh_t).select(wh_t.star)
            .where((wh_t.id == P()) | (wh_t.name == P())))
    wh = conn.execute(wh_q.get_sql(), (args.warehouse_id, args.warehouse_id)).fetchone()
    if not wh:
        err(f"Warehouse {args.warehouse_id} not found")
    args.warehouse_id = wh["id"]  # normalize to id

    updates, params, updated_fields = [], [], []

    if args.name is not None:
        updates.append("name = ?")
        params.append(args.name)
        updated_fields.append("name")
    if args.account_id is not None:
        acct_t = Table("account")
        acct_q = Q.from_(acct_t).select(acct_t.id).where(acct_t.id == P())
        acct = conn.execute(acct_q.get_sql(), (args.account_id,)).fetchone()
        if not acct:
            err(f"Account {args.account_id} not found")
        updates.append("account_id = ?")
        params.append(args.account_id)
        updated_fields.append("account_id")

    if not updated_fields:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(args.warehouse_id)
    conn.execute(
        f"UPDATE warehouse SET {', '.join(updates)} WHERE id = ?", params)

    audit(conn, "erpclaw-inventory", "update-warehouse", "warehouse", args.warehouse_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"warehouse_id": args.warehouse_id, "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 9. list-warehouses
# ---------------------------------------------------------------------------

def list_warehouses(conn, args):
    """List warehouses for a company."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    w = Table("warehouse").as_("w")

    count_q = Q.from_(w).select(fn.Count("*")).where(w.company_id == P())
    if args.parent_id:
        count_q = count_q.where(w.parent_id == P())
    if args.warehouse_type:
        count_q = count_q.where(w.warehouse_type == P())

    count_params = [company_id]
    if args.parent_id:
        count_params.append(args.parent_id)
    if args.warehouse_type:
        count_params.append(args.warehouse_type)

    count_row = conn.execute(count_q.get_sql(), count_params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    rows_q = (Q.from_(w).select(w.star)
              .where(w.company_id == P())
              .orderby(w.name)
              .limit(P()).offset(P()))
    if args.parent_id:
        rows_q = rows_q.where(w.parent_id == P())
    if args.warehouse_type:
        rows_q = rows_q.where(w.warehouse_type == P())

    row_params = [company_id]
    if args.parent_id:
        row_params.append(args.parent_id)
    if args.warehouse_type:
        row_params.append(args.warehouse_type)
    row_params.extend([limit, offset])

    rows = conn.execute(rows_q.get_sql(), row_params).fetchall()

    ok({"warehouses": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 10. add-stock-entry
# ---------------------------------------------------------------------------

def add_stock_entry(conn, args):
    """Create a stock entry in draft."""
    if not args.entry_type:
        err("--entry-type is required (receive|issue|transfer|manufacture)")
    entry_type = ENTRY_TYPE_MAP.get(args.entry_type)
    if not entry_type:
        err(f"Invalid --entry-type '{args.entry_type}'. "
             f"Valid: receive, issue, transfer, manufacture")
    if not args.company_id:
        err("--company-id is required")
    if not args.posting_date:
        err("--posting-date is required")
    if not args.items:
        err("--items is required (JSON array)")

    co_t = Table("company")
    co_q = Q.from_(co_t).select(co_t.id).where(co_t.id == P())
    if not conn.execute(co_q.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    se_id = str(uuid.uuid4())
    naming = get_next_name(conn, "stock_entry", company_id=args.company_id)

    total_incoming = Decimal("0")
    total_outgoing = Decimal("0")

    # Validate and collect item rows before inserting
    item_rows_to_insert = []
    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Item {i}: item_id is required")

        # Validate item exists
        item_t = Table("item")
        item_q = (Q.from_(item_t)
                  .select(item_t.id, item_t.standard_rate)
                  .where(item_t.id == P()))
        item_row = conn.execute(item_q.get_sql(), (item_id,)).fetchone()
        if not item_row:
            err(f"Item {i}: item {item_id} not found")

        qty = to_decimal(item.get("qty", "0"))
        if qty <= 0:
            err(f"Item {i}: qty must be > 0")

        rate = to_decimal(item.get("rate", "0"))
        if rate <= 0:
            rate = to_decimal(item_row["standard_rate"])

        amount = round_currency(qty * rate)

        from_wh = item.get("from_warehouse_id")
        to_wh = item.get("to_warehouse_id")

        # Fall back to company's default warehouse if item-level warehouse not specified
        if not to_wh or not from_wh:
            dw_t = Table("company")
            dw_q = Q.from_(dw_t).select(dw_t.default_warehouse_id).where(dw_t.id == P())
            dw_row = conn.execute(dw_q.get_sql(), (args.company_id,)).fetchone()
            default_wh = dw_row["default_warehouse_id"] if dw_row else None
            if not to_wh and default_wh:
                to_wh = default_wh
            if not from_wh and default_wh:
                from_wh = default_wh

        # Validate warehouse per entry type
        if entry_type == "material_receipt":
            if not to_wh:
                err(f"Item {i}: to_warehouse_id is required for receipt (set company default warehouse or provide per-item)")
            total_incoming += amount
        elif entry_type == "material_issue":
            if not from_wh:
                err(f"Item {i}: from_warehouse_id is required for issue")
            total_outgoing += amount
        elif entry_type == "material_transfer":
            if not from_wh:
                err(f"Item {i}: from_warehouse_id is required for transfer")
            if not to_wh:
                err(f"Item {i}: to_warehouse_id is required for transfer")
            total_incoming += amount
            total_outgoing += amount
        elif entry_type == "manufacture":
            # Manufacture: finished goods go to to_warehouse, raw materials come from from_warehouse
            if not from_wh and not to_wh:
                err(f"Item {i}: from_warehouse_id or to_warehouse_id is required for manufacture")
            if to_wh:
                total_incoming += amount
            if from_wh:
                total_outgoing += amount

        item_rows_to_insert.append((
            str(uuid.uuid4()), se_id, item_id, str(round_currency(qty)),
            from_wh, to_wh,
            str(round_currency(rate)), str(amount),
            item.get("batch_id"), item.get("serial_numbers"),
        ))

    value_diff = round_currency(total_incoming - total_outgoing)

    # Insert parent stock_entry first (FK target for stock_entry_item)
    se_t = Table("stock_entry")
    se_q = Q.into(se_t).columns(
        "id", "naming_series", "stock_entry_type", "posting_date",
        "total_incoming_value", "total_outgoing_value", "value_difference",
        "status", "company_id",
    ).insert(P(), P(), P(), P(), P(), P(), P(), "draft", P())
    conn.execute(
        se_q.get_sql(),
        (se_id, naming, entry_type, args.posting_date,
         str(round_currency(total_incoming)),
         str(round_currency(total_outgoing)),
         str(value_diff), args.company_id),
    )

    # Now insert child stock_entry_item rows
    sei_t = Table("stock_entry_item")
    sei_q = Q.into(sei_t).columns(
        "id", "stock_entry_id", "item_id", "quantity", "from_warehouse_id",
        "to_warehouse_id", "valuation_rate", "amount", "batch_id", "serial_numbers",
    ).insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P())
    for row_params in item_rows_to_insert:
        conn.execute(sei_q.get_sql(), row_params)

    audit(conn, "erpclaw-inventory", "add-stock-entry", "stock_entry", se_id,
           new_values={"naming_series": naming, "type": entry_type,
                       "item_count": len(items)})
    conn.commit()
    ok({"stock_entry_id": se_id, "naming_series": naming,
         "total_incoming_value": str(round_currency(total_incoming)),
         "total_outgoing_value": str(round_currency(total_outgoing)),
         "value_difference": str(value_diff)})


# ---------------------------------------------------------------------------
# 11. get-stock-entry
# ---------------------------------------------------------------------------

def get_stock_entry(conn, args):
    """Get stock entry with items."""
    if not args.stock_entry_id:
        err("--stock-entry-id is required")

    se_t = Table("stock_entry")
    se_q = Q.from_(se_t).select(se_t.star).where(se_t.id == P())
    se = conn.execute(se_q.get_sql(), (args.stock_entry_id,)).fetchone()
    if not se:
        err(f"Stock entry {args.stock_entry_id} not found")

    data = row_to_dict(se)

    sei = Table("stock_entry_item").as_("sei")
    i = Table("item").as_("i")
    items_q = (Q.from_(sei)
               .left_join(i).on(i.id == sei.item_id)
               .select(sei.star, i.item_code, i.item_name)
               .where(sei.stock_entry_id == P())
               .orderby(sei.field("rowid")))
    items = conn.execute(items_q.get_sql(), (args.stock_entry_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]
    ok(data)


# ---------------------------------------------------------------------------
# 12. list-stock-entries
# ---------------------------------------------------------------------------

def list_stock_entries(conn, args):
    """List stock entries with filtering."""
    se = Table("stock_entry").as_("se")

    count_q = Q.from_(se).select(fn.Count("*"))
    if args.company_id:
        count_q = count_q.where(se.company_id == P())
    if args.entry_type:
        mapped = ENTRY_TYPE_MAP.get(args.entry_type, args.entry_type)
        count_q = count_q.where(se.stock_entry_type == P())
    if args.se_status:
        count_q = count_q.where(se.status == P())
    if args.from_date:
        count_q = count_q.where(se.posting_date >= P())
    if args.to_date:
        count_q = count_q.where(se.posting_date <= P())

    count_params = []
    if args.company_id:
        count_params.append(args.company_id)
    if args.entry_type:
        count_params.append(ENTRY_TYPE_MAP.get(args.entry_type, args.entry_type))
    if args.se_status:
        count_params.append(args.se_status)
    if args.from_date:
        count_params.append(args.from_date)
    if args.to_date:
        count_params.append(args.to_date)

    count_row = conn.execute(count_q.get_sql(), count_params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    rows_q = (Q.from_(se)
              .select(se.id, se.naming_series, se.stock_entry_type, se.posting_date,
                      se.total_incoming_value, se.total_outgoing_value,
                      se.value_difference, se.status, se.company_id)
              .orderby(se.posting_date, order=Order.desc)
              .orderby(se.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    if args.company_id:
        rows_q = rows_q.where(se.company_id == P())
    if args.entry_type:
        rows_q = rows_q.where(se.stock_entry_type == P())
    if args.se_status:
        rows_q = rows_q.where(se.status == P())
    if args.from_date:
        rows_q = rows_q.where(se.posting_date >= P())
    if args.to_date:
        rows_q = rows_q.where(se.posting_date <= P())

    row_params = []
    if args.company_id:
        row_params.append(args.company_id)
    if args.entry_type:
        row_params.append(ENTRY_TYPE_MAP.get(args.entry_type, args.entry_type))
    if args.se_status:
        row_params.append(args.se_status)
    if args.from_date:
        row_params.append(args.from_date)
    if args.to_date:
        row_params.append(args.to_date)
    row_params.extend([limit, offset])

    rows = conn.execute(rows_q.get_sql(), row_params).fetchall()

    ok({"stock_entries": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 13. submit-stock-entry
# ---------------------------------------------------------------------------

def submit_stock_entry(conn, args):
    """Submit a draft stock entry: post SLE + GL entries."""
    if not args.stock_entry_id:
        err("--stock-entry-id is required")

    se_t = Table("stock_entry")
    se_q = Q.from_(se_t).select(se_t.star).where(se_t.id == P())
    se = conn.execute(se_q.get_sql(), (args.stock_entry_id,)).fetchone()
    if not se:
        err(f"Stock entry {args.stock_entry_id} not found")
    if se["status"] != "draft":
        err(f"Cannot submit: stock entry is '{se['status']}' (must be 'draft')")

    se_dict = row_to_dict(se)
    company_id = se_dict["company_id"]
    posting_date = se_dict["posting_date"]
    entry_type = se_dict["stock_entry_type"]

    # Fetch items
    sei_t = Table("stock_entry_item")
    sei_q = (Q.from_(sei_t).select(sei_t.star)
             .where(sei_t.stock_entry_id == P())
             .orderby(Field("rowid")))
    items = conn.execute(sei_q.get_sql(), (args.stock_entry_id,)).fetchall()
    if not items:
        err("Stock entry has no items")

    # Find fiscal year for the posting date
    fiscal_year = _get_fiscal_year(conn, posting_date)

    # Find cost center for P&L accounts (COGS)
    cost_center_id = _get_cost_center(conn, company_id)

    # Build SLE entries from stock entry items
    sle_entries = []
    for item_row in items:
        item = row_to_dict(item_row)
        qty = to_decimal(item["quantity"])
        rate = to_decimal(item["valuation_rate"])
        from_wh = item.get("from_warehouse_id")
        to_wh = item.get("to_warehouse_id")

        if entry_type == "material_receipt":
            # Positive qty at to_warehouse
            sle_entries.append({
                "item_id": item["item_id"],
                "warehouse_id": to_wh,
                "actual_qty": str(round_currency(qty)),
                "incoming_rate": str(round_currency(rate)),
                "batch_id": item.get("batch_id"),
                "serial_number": item.get("serial_numbers"),
                "fiscal_year": fiscal_year,
            })
        elif entry_type == "material_issue":
            # Negative qty at from_warehouse
            sle_entries.append({
                "item_id": item["item_id"],
                "warehouse_id": from_wh,
                "actual_qty": str(round_currency(-qty)),
                "incoming_rate": "0",
                "batch_id": item.get("batch_id"),
                "serial_number": item.get("serial_numbers"),
                "fiscal_year": fiscal_year,
            })
        elif entry_type == "material_transfer":
            # Negative at from_warehouse, positive at to_warehouse
            sle_entries.append({
                "item_id": item["item_id"],
                "warehouse_id": from_wh,
                "actual_qty": str(round_currency(-qty)),
                "incoming_rate": "0",
                "batch_id": item.get("batch_id"),
                "serial_number": item.get("serial_numbers"),
                "fiscal_year": fiscal_year,
            })
            sle_entries.append({
                "item_id": item["item_id"],
                "warehouse_id": to_wh,
                "actual_qty": str(round_currency(qty)),
                "incoming_rate": str(round_currency(rate)),
                "batch_id": item.get("batch_id"),
                "serial_number": item.get("serial_numbers"),
                "fiscal_year": fiscal_year,
            })
        elif entry_type == "manufacture":
            # Finished goods to to_warehouse, raw materials from from_warehouse
            if to_wh:
                sle_entries.append({
                    "item_id": item["item_id"],
                    "warehouse_id": to_wh,
                    "actual_qty": str(round_currency(qty)),
                    "incoming_rate": str(round_currency(rate)),
                    "batch_id": item.get("batch_id"),
                    "serial_number": item.get("serial_numbers"),
                    "fiscal_year": fiscal_year,
                })
            if from_wh:
                sle_entries.append({
                    "item_id": item["item_id"],
                    "warehouse_id": from_wh,
                    "actual_qty": str(round_currency(-qty)),
                    "incoming_rate": "0",
                    "batch_id": item.get("batch_id"),
                    "serial_number": item.get("serial_numbers"),
                    "fiscal_year": fiscal_year,
                })

    # Insert SLE entries via shared lib
    try:
        sle_ids = insert_sle_entries(
            conn, sle_entries,
            voucher_type="stock_entry",
            voucher_id=args.stock_entry_id,
            posting_date=posting_date,
            company_id=company_id,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err(f"SLE posting failed: {e}")

    # Build SLE dicts with stock_value_difference for GL generation
    sle_t = Table("stock_ledger_entry")
    sle_q = (Q.from_(sle_t).select(sle_t.star)
             .where(sle_t.voucher_type == "stock_entry")
             .where(sle_t.voucher_id == P())
             .where(sle_t.is_cancelled == 0))
    sle_rows = conn.execute(sle_q.get_sql(), (args.stock_entry_id,)).fetchall()
    sle_dicts = [row_to_dict(r) for r in sle_rows]

    # Create perpetual inventory GL entries
    gl_entries = create_perpetual_inventory_gl(
        conn, sle_dicts,
        voucher_type="stock_entry",
        voucher_id=args.stock_entry_id,
        posting_date=posting_date,
        company_id=company_id,
        cost_center_id=cost_center_id,
    )

    gl_ids = []
    if gl_entries:
        # Add fiscal_year to each GL entry
        for gle in gl_entries:
            gle["fiscal_year"] = fiscal_year
        try:
            gl_ids = insert_gl_entries(
                conn, gl_entries,
                voucher_type="stock_entry",
                voucher_id=args.stock_entry_id,
                posting_date=posting_date,
                company_id=company_id,
                remarks=f"Stock Entry {se_dict['naming_series']}",
            )
        except ValueError as e:
            sys.stderr.write(f"[erpclaw-inventory] {e}\n")
            err(f"GL posting failed: {e}")

    # Update status
    conn.execute(
        "UPDATE stock_entry SET status = 'submitted', updated_at = datetime('now') WHERE id = ?",
        (args.stock_entry_id,),
    )

    audit(conn, "erpclaw-inventory", "submit-stock-entry", "stock_entry", args.stock_entry_id,
           new_values={"sle_count": len(sle_ids), "gl_count": len(gl_ids)})
    conn.commit()

    ok({"stock_entry_id": args.stock_entry_id,
         "sle_entries_created": len(sle_ids),
         "gl_entries_created": len(gl_ids)})


# ---------------------------------------------------------------------------
# 14. cancel-stock-entry
# ---------------------------------------------------------------------------

def cancel_stock_entry(conn, args):
    """Cancel a submitted stock entry."""
    if not args.stock_entry_id:
        err("--stock-entry-id is required")

    se_t = Table("stock_entry")
    se_q = Q.from_(se_t).select(se_t.star).where(se_t.id == P())
    se = conn.execute(se_q.get_sql(), (args.stock_entry_id,)).fetchone()
    if not se:
        err(f"Stock entry {args.stock_entry_id} not found")
    if se["status"] != "submitted":
        err(f"Cannot cancel: stock entry is '{se['status']}' (must be 'submitted')",
             suggestion="Only submitted stock entries can be cancelled.")

    posting_date = se["posting_date"]

    # Reverse SLE entries
    try:
        reversal_sle_ids = reverse_sle_entries(
            conn,
            voucher_type="stock_entry",
            voucher_id=args.stock_entry_id,
            posting_date=posting_date,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err(f"SLE reversal failed: {e}")

    # Reverse GL entries
    try:
        reversal_gl_ids = reverse_gl_entries(
            conn,
            voucher_type="stock_entry",
            voucher_id=args.stock_entry_id,
            posting_date=posting_date,
        )
    except ValueError:
        # GL entries may not exist if perpetual inventory GL was skipped
        reversal_gl_ids = []

    # Update status
    conn.execute(
        "UPDATE stock_entry SET status = 'cancelled', updated_at = datetime('now') WHERE id = ?",
        (args.stock_entry_id,),
    )

    audit(conn, "erpclaw-inventory", "cancel-stock-entry", "stock_entry", args.stock_entry_id,
           new_values={"reversed": True})
    conn.commit()

    ok({"stock_entry_id": args.stock_entry_id, "reversed": True,
         "sle_reversals": len(reversal_sle_ids),
         "gl_reversals": len(reversal_gl_ids)})


# ---------------------------------------------------------------------------
# 15. create-stock-ledger-entries (cross-skill)
# ---------------------------------------------------------------------------

def create_stock_ledger_entries(conn, args):
    """Cross-skill: create SLE entries (called by selling/buying)."""
    if not args.voucher_type:
        err("--voucher-type is required")
    if not args.voucher_id:
        err("--voucher-id is required")
    if not args.posting_date:
        err("--posting-date is required")
    if not args.entries:
        err("--entries is required (JSON array)")
    if not args.company_id:
        err("--company-id is required")

    entries = _parse_json_arg(args.entries, "entries")
    if not entries or not isinstance(entries, list):
        err("--entries must be a non-empty JSON array")

    fiscal_year = _get_fiscal_year(conn, args.posting_date)

    # Add fiscal_year to each entry
    for entry in entries:
        entry["fiscal_year"] = fiscal_year

    try:
        sle_ids = insert_sle_entries(
            conn, entries,
            voucher_type=args.voucher_type,
            voucher_id=args.voucher_id,
            posting_date=args.posting_date,
            company_id=args.company_id,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err(f"SLE posting failed: {e}")

    audit(conn, "erpclaw-inventory", "create-stock-ledger-entries", "stock_ledger_entry",
           args.voucher_id,
           new_values={"voucher_type": args.voucher_type,
                       "sle_count": len(sle_ids)})
    conn.commit()
    ok({"sle_ids": sle_ids, "count": len(sle_ids)})


# ---------------------------------------------------------------------------
# 16. reverse-stock-ledger-entries (cross-skill)
# ---------------------------------------------------------------------------

def reverse_stock_ledger_entries(conn, args):
    """Cross-skill: reverse SLE entries (called by selling/buying)."""
    if not args.voucher_type:
        err("--voucher-type is required")
    if not args.voucher_id:
        err("--voucher-id is required")
    if not args.posting_date:
        err("--posting-date is required")

    try:
        reversal_ids = reverse_sle_entries(
            conn,
            voucher_type=args.voucher_type,
            voucher_id=args.voucher_id,
            posting_date=args.posting_date,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err(f"SLE reversal failed: {e}")

    audit(conn, "erpclaw-inventory", "reverse-stock-ledger-entries", "stock_ledger_entry",
           args.voucher_id,
           new_values={"voucher_type": args.voucher_type,
                       "reversal_count": len(reversal_ids)})
    conn.commit()
    ok({"reversal_ids": reversal_ids, "count": len(reversal_ids)})


# ---------------------------------------------------------------------------
# 17. get-stock-balance
# ---------------------------------------------------------------------------

def get_stock_balance_action(conn, args):
    """Get stock balance for an item in a warehouse."""
    if not args.item_id:
        err("--item-id is required")
    if not args.warehouse_id:
        err("--warehouse-id is required")

    balance = get_stock_balance(conn, args.item_id, args.warehouse_id)
    ok({"item_id": args.item_id, "warehouse_id": args.warehouse_id,
         "qty": balance["qty"], "valuation_rate": balance["valuation_rate"],
         "stock_value": balance["stock_value"]})


# ---------------------------------------------------------------------------
# 18. stock-balance-report
# ---------------------------------------------------------------------------

def stock_balance_report(conn, args):
    """All items stock summary for a company."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    # This query uses decimal_sum() aggregate and a correlated subquery for
    # valuation_rate — kept as raw SQL due to complexity of correlated subquery
    # and HAVING clause with decimal_sum()
    conditions = [
        "sle.is_cancelled = 0",
        "w.company_id = ?",
    ]
    params = [company_id]

    if args.warehouse_id:
        conditions.append("sle.warehouse_id = ?")
        params.append(args.warehouse_id)

    where = " AND ".join(conditions)

    rows = conn.execute(
        f"""SELECT sle.item_id, sle.warehouse_id,
               i.item_code, i.item_name, w.name AS warehouse_name,
               decimal_sum(sle.actual_qty) AS balance_qty,
               COALESCE(
                   (SELECT valuation_rate FROM stock_ledger_entry s2
                    WHERE s2.item_id = sle.item_id AND s2.warehouse_id = sle.warehouse_id
                      AND s2.is_cancelled = 0
                    ORDER BY s2.rowid DESC LIMIT 1),
                   '0'
               ) AS valuation_rate
           FROM stock_ledger_entry sle
           JOIN item i ON i.id = sle.item_id
           JOIN warehouse w ON w.id = sle.warehouse_id
           WHERE {where}
           GROUP BY sle.item_id, sle.warehouse_id
           HAVING decimal_sum(sle.actual_qty) + 0 != 0
           ORDER BY i.item_name, w.name""",
        params,
    ).fetchall()

    report = []
    total_value = Decimal("0")
    for row in rows:
        qty = to_decimal(str(row["balance_qty"]))
        rate = to_decimal(str(row["valuation_rate"]))
        value = round_currency(qty * rate)
        total_value += value
        report.append({
            "item_id": row["item_id"],
            "item_code": row["item_code"],
            "item_name": row["item_name"],
            "warehouse_id": row["warehouse_id"],
            "warehouse_name": row["warehouse_name"],
            "qty": str(round_currency(qty)),
            "valuation_rate": str(round_currency(rate)),
            "stock_value": str(value),
        })

    ok({"report": report, "total_stock_value": str(round_currency(total_value)),
         "row_count": len(report)})


# ---------------------------------------------------------------------------
# 19. stock-ledger-report
# ---------------------------------------------------------------------------

def stock_ledger_report(conn, args):
    """Stock ledger entry detail report."""
    sle = Table("stock_ledger_entry").as_("sle")
    i = Table("item").as_("i")
    w = Table("warehouse").as_("w")

    rows_q = (Q.from_(sle)
              .left_join(i).on(i.id == sle.item_id)
              .left_join(w).on(w.id == sle.warehouse_id)
              .select(sle.star, i.item_code, i.item_name, w.name.as_("warehouse_name"))
              .where(sle.is_cancelled == 0)
              .orderby(sle.posting_date, order=Order.desc)
              .orderby(sle.created_at, order=Order.desc)
              .limit(P()).offset(P()))

    params = []
    if args.item_id:
        rows_q = rows_q.where(sle.item_id == P())
        params.append(args.item_id)
    if args.warehouse_id:
        rows_q = rows_q.where(sle.warehouse_id == P())
        params.append(args.warehouse_id)
    if args.from_date:
        rows_q = rows_q.where(sle.posting_date >= P())
        params.append(args.from_date)
    if args.to_date:
        rows_q = rows_q.where(sle.posting_date <= P())
        params.append(args.to_date)

    limit = int(args.limit) if args.limit else 100
    offset = int(args.offset) if args.offset else 0
    params.extend([limit, offset])

    rows = conn.execute(rows_q.get_sql(), params).fetchall()

    ok({"entries": [row_to_dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# 20. add-batch
# ---------------------------------------------------------------------------

def add_batch(conn, args):
    """Create a batch."""
    if not args.item_id:
        err("--item-id is required")
    if not args.batch_name:
        err("--batch-name is required")

    item_t = Table("item")
    item_q = (Q.from_(item_t)
              .select(item_t.id, item_t.has_batch)
              .where(item_t.id == P()))
    item = conn.execute(item_q.get_sql(), (args.item_id,)).fetchone()
    if not item:
        err(f"Item {args.item_id} not found")

    batch_id = str(uuid.uuid4())
    t = Table("batch")
    q = Q.into(t).columns(
        "id", "batch_name", "item_id", "manufacturing_date", "expiry_date",
    ).insert(P(), P(), P(), P(), P())
    try:
        conn.execute(
            q.get_sql(),
            (batch_id, args.batch_name, args.item_id,
             args.manufacturing_date, args.expiry_date),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err("Batch creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-inventory", "add-batch", "batch", batch_id,
           new_values={"batch_name": args.batch_name, "item_id": args.item_id})
    conn.commit()
    ok({"batch_id": batch_id, "batch_name": args.batch_name})


# ---------------------------------------------------------------------------
# 21. list-batches
# ---------------------------------------------------------------------------

def list_batches(conn, args):
    """List batches with optional filters."""
    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    if args.warehouse_id:
        # Filter by batches that have stock in the specified warehouse
        # Uses decimal_sum() HAVING — kept as raw SQL
        conditions = ["1=1"]
        params = []
        if args.item_id:
            conditions.append("b.item_id = ?")
            params.append(args.item_id)
        where = " AND ".join(conditions)

        count_row = conn.execute(
            f"""SELECT COUNT(*) FROM (
                   SELECT b.id
                   FROM batch b
                   JOIN stock_ledger_entry sle ON sle.batch_id = b.id
                   WHERE {where} AND sle.warehouse_id = ? AND sle.is_cancelled = 0
                   GROUP BY b.id
                   HAVING decimal_sum(sle.actual_qty) + 0 > 0
               )""",
            params + [args.warehouse_id],
        ).fetchone()
        total_count = count_row[0]

        rows = conn.execute(
            f"""SELECT DISTINCT b.*
               FROM batch b
               JOIN stock_ledger_entry sle ON sle.batch_id = b.id
               WHERE {where} AND sle.warehouse_id = ? AND sle.is_cancelled = 0
               GROUP BY b.id
               HAVING decimal_sum(sle.actual_qty) + 0 > 0
               ORDER BY b.batch_name
               LIMIT ? OFFSET ?""",
            params + [args.warehouse_id, limit, offset],
        ).fetchall()
    else:
        b = Table("batch").as_("b")

        count_q = Q.from_(b).select(fn.Count("*"))
        if args.item_id:
            count_q = count_q.where(b.item_id == P())

        count_params = []
        if args.item_id:
            count_params.append(args.item_id)

        count_row = conn.execute(count_q.get_sql(), count_params).fetchone()
        total_count = count_row[0]

        rows_q = (Q.from_(b).select(b.star)
                  .orderby(b.batch_name)
                  .limit(P()).offset(P()))
        if args.item_id:
            rows_q = rows_q.where(b.item_id == P())

        row_params = []
        if args.item_id:
            row_params.append(args.item_id)
        row_params.extend([limit, offset])

        rows = conn.execute(rows_q.get_sql(), row_params).fetchall()

    ok({"batches": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 22. add-serial-number
# ---------------------------------------------------------------------------

def add_serial_number(conn, args):
    """Register a serial number."""
    if not args.item_id:
        err("--item-id is required")
    if not args.serial_no:
        err("--serial-no is required")

    item_t = Table("item")
    item_q = Q.from_(item_t).select(item_t.id).where(item_t.id == P())
    item = conn.execute(item_q.get_sql(), (args.item_id,)).fetchone()
    if not item:
        err(f"Item {args.item_id} not found")

    sn_id = str(uuid.uuid4())
    t = Table("serial_number")
    q = Q.into(t).columns(
        "id", "serial_no", "item_id", "warehouse_id", "batch_id", "status",
    ).insert(P(), P(), P(), P(), P(), "active")
    try:
        conn.execute(
            q.get_sql(),
            (sn_id, args.serial_no, args.item_id,
             args.warehouse_id, args.batch_id),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err("Serial number creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-inventory", "add-serial-number", "serial_number", sn_id,
           new_values={"serial_no": args.serial_no, "item_id": args.item_id})
    conn.commit()
    ok({"serial_number_id": sn_id, "serial_no": args.serial_no})


# ---------------------------------------------------------------------------
# 23. list-serial-numbers
# ---------------------------------------------------------------------------

def list_serial_numbers(conn, args):
    """List serial numbers with optional filters."""
    sn = Table("serial_number").as_("sn")
    i = Table("item").as_("i")

    count_q = Q.from_(sn).select(fn.Count("*"))
    if args.item_id:
        count_q = count_q.where(sn.item_id == P())
    if args.warehouse_id:
        count_q = count_q.where(sn.warehouse_id == P())
    if args.sn_status:
        if args.sn_status not in VALID_SERIAL_STATUSES:
            err(f"--status must be one of: {', '.join(VALID_SERIAL_STATUSES)}")
        count_q = count_q.where(sn.status == P())

    count_params = []
    if args.item_id:
        count_params.append(args.item_id)
    if args.warehouse_id:
        count_params.append(args.warehouse_id)
    if args.sn_status:
        count_params.append(args.sn_status)

    count_row = conn.execute(count_q.get_sql(), count_params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    rows_q = (Q.from_(sn)
              .left_join(i).on(i.id == sn.item_id)
              .select(sn.star, i.item_code, i.item_name)
              .orderby(sn.serial_no)
              .limit(P()).offset(P()))
    if args.item_id:
        rows_q = rows_q.where(sn.item_id == P())
    if args.warehouse_id:
        rows_q = rows_q.where(sn.warehouse_id == P())
    if args.sn_status:
        rows_q = rows_q.where(sn.status == P())

    row_params = []
    if args.item_id:
        row_params.append(args.item_id)
    if args.warehouse_id:
        row_params.append(args.warehouse_id)
    if args.sn_status:
        row_params.append(args.sn_status)
    row_params.extend([limit, offset])

    rows = conn.execute(rows_q.get_sql(), row_params).fetchall()

    ok({"serial_numbers": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 24. add-price-list
# ---------------------------------------------------------------------------

def add_price_list(conn, args):
    """Create a price list."""
    if not args.name:
        err("--name is required")

    pl_id = str(uuid.uuid4())
    currency = args.currency or "USD"
    is_buying = int(args.is_buying) if args.is_buying else 0
    is_selling = int(args.is_selling) if args.is_selling else 0

    t = Table("price_list")
    q = Q.into(t).columns("id", "name", "currency", "buying", "selling").insert(P(), P(), P(), P(), P())
    try:
        conn.execute(q.get_sql(), (pl_id, args.name, currency, is_buying, is_selling))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err("Price list creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-inventory", "add-price-list", "price_list", pl_id,
           new_values={"name": args.name})
    conn.commit()
    ok({"price_list_id": pl_id, "name": args.name})


# ---------------------------------------------------------------------------
# 25. add-item-price
# ---------------------------------------------------------------------------

def add_item_price(conn, args):
    """Set a price for an item in a price list."""
    if not args.item_id:
        err("--item-id is required")
    if not args.price_list_id:
        err("--price-list-id is required")
    if not args.rate:
        err("--rate is required")

    # Validate references
    item_t = Table("item")
    item_q = Q.from_(item_t).select(item_t.id).where(item_t.id == P())
    if not conn.execute(item_q.get_sql(), (args.item_id,)).fetchone():
        err(f"Item {args.item_id} not found")

    pl_t = Table("price_list")
    pl_q = Q.from_(pl_t).select(pl_t.id).where(pl_t.id == P())
    if not conn.execute(pl_q.get_sql(), (args.price_list_id,)).fetchone():
        err(f"Price list {args.price_list_id} not found")

    rate = round_currency(to_decimal(args.rate))
    min_qty = str(to_decimal(args.min_qty or "0"))

    ip_id = str(uuid.uuid4())
    t = Table("item_price")
    q = Q.into(t).columns(
        "id", "item_id", "price_list_id", "rate", "min_qty", "valid_from", "valid_to",
    ).insert(P(), P(), P(), P(), P(), P(), P())
    conn.execute(
        q.get_sql(),
        (ip_id, args.item_id, args.price_list_id, str(rate),
         min_qty, args.valid_from, args.valid_to),
    )

    audit(conn, "erpclaw-inventory", "add-item-price", "item_price", ip_id,
           new_values={"item_id": args.item_id, "rate": str(rate)})
    conn.commit()
    ok({"item_price_id": ip_id, "rate": str(rate)})


# ---------------------------------------------------------------------------
# 26. get-item-price
# ---------------------------------------------------------------------------

def get_item_price(conn, args):
    """Get applicable price for an item from a price list."""
    if not args.item_id:
        err("--item-id is required")
    if not args.price_list_id:
        err("--price-list-id is required")

    qty = to_decimal(args.qty or "1")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Find best matching price: valid date range, min_qty <= requested qty
    # Order by min_qty DESC to get the most specific tier first
    # This query uses IS NULL comparisons — kept as raw SQL (rule 16)
    rows = conn.execute(
        """SELECT * FROM item_price
           WHERE item_id = ? AND price_list_id = ?
             AND min_qty + 0 <= ? + 0
             AND (valid_from IS NULL OR valid_from <= ?)
             AND (valid_to IS NULL OR valid_to >= ?)
           ORDER BY min_qty + 0 DESC
           LIMIT 1""",
        (args.item_id, args.price_list_id, str(qty), today, today),
    ).fetchone()

    if not rows:
        # Fallback: any price for this item/price list (ignoring date/qty)
        ip_t = Table("item_price")
        fallback_q = (Q.from_(ip_t).select(ip_t.star)
                      .where(ip_t.item_id == P())
                      .where(ip_t.price_list_id == P())
                      .orderby(ip_t.created_at, order=Order.desc)
                      .limit(1))
        rows = conn.execute(
            fallback_q.get_sql(),
            (args.item_id, args.price_list_id),
        ).fetchone()

    if not rows:
        err(f"No price found for item {args.item_id} in price list {args.price_list_id}")

    data = row_to_dict(rows)
    ok(data)


# ---------------------------------------------------------------------------
# 27. add-pricing-rule
# ---------------------------------------------------------------------------

def add_pricing_rule(conn, args):
    """Create a pricing/discount rule."""
    if not args.name:
        err("--name is required")
    if not args.applies_to:
        err("--applies-to is required (item|item_group|customer|customer_group)")
    if args.applies_to not in ("item", "item_group", "customer", "customer_group"):
        err("--applies-to must be item|item_group|customer|customer_group")
    if not args.company_id:
        err("--company-id is required")

    pr_id = str(uuid.uuid4())
    t = Table("pricing_rule")
    q = Q.into(t).columns(
        "id", "name", "applies_to", "entity_id", "discount_percentage", "rate",
        "min_qty", "max_qty", "valid_from", "valid_to", "priority", "company_id",
    ).insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P())
    conn.execute(
        q.get_sql(),
        (pr_id, args.name, args.applies_to, args.entity_id,
         args.discount_percentage, args.pr_rate,
         args.min_qty, args.max_qty,
         args.valid_from, args.valid_to,
         args.priority or 0, args.company_id),
    )

    audit(conn, "erpclaw-inventory", "add-pricing-rule", "pricing_rule", pr_id,
           new_values={"name": args.name, "applies_to": args.applies_to})
    conn.commit()
    ok({"pricing_rule_id": pr_id, "name": args.name})


# ---------------------------------------------------------------------------
# 28. add-stock-reconciliation
# ---------------------------------------------------------------------------

def add_stock_reconciliation(conn, args):
    """Create a stock reconciliation (physical count)."""
    if not args.posting_date:
        err("--posting-date is required")
    if not args.items:
        err("--items is required (JSON array)")
    if not args.company_id:
        err("--company-id is required")

    co_t = Table("company")
    co_q = Q.from_(co_t).select(co_t.id).where(co_t.id == P())
    if not conn.execute(co_q.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    sr_id = str(uuid.uuid4())
    naming = get_next_name(conn, "stock_reconciliation",
                           company_id=args.company_id)

    total_diff_amount = Decimal("0")

    # Validate and collect item rows before inserting
    item_rows_to_insert = []
    for i, item in enumerate(items):
        item_id = item.get("item_id")
        warehouse_id = item.get("warehouse_id")
        if not item_id:
            err(f"Item {i}: item_id is required")
        if not warehouse_id:
            err(f"Item {i}: warehouse_id is required")

        # Get current stock balance
        balance = get_stock_balance(conn, item_id, warehouse_id)
        current_qty = to_decimal(balance["qty"])
        current_rate = to_decimal(balance["valuation_rate"])

        counted_qty = to_decimal(item.get("qty", "0"))
        counted_rate = to_decimal(item.get("valuation_rate", str(current_rate)))

        qty_diff = round_currency(counted_qty - current_qty)
        current_value = round_currency(current_qty * current_rate)
        counted_value = round_currency(counted_qty * counted_rate)
        amount_diff = round_currency(counted_value - current_value)
        total_diff_amount += amount_diff

        item_rows_to_insert.append((
            str(uuid.uuid4()), sr_id, item_id, warehouse_id,
            str(round_currency(current_qty)), str(round_currency(current_rate)),
            str(round_currency(counted_qty)), str(round_currency(counted_rate)),
            str(qty_diff), str(amount_diff),
        ))

    # Insert parent stock_reconciliation first (FK target for items)
    sr_t = Table("stock_reconciliation")
    sr_q = Q.into(sr_t).columns(
        "id", "naming_series", "posting_date", "difference_amount",
        "status", "company_id",
    ).insert(P(), P(), P(), P(), "draft", P())
    conn.execute(
        sr_q.get_sql(),
        (sr_id, naming, args.posting_date,
         str(round_currency(total_diff_amount)), args.company_id),
    )

    # Now insert child stock_reconciliation_item rows
    sri_t = Table("stock_reconciliation_item")
    sri_q = Q.into(sri_t).columns(
        "id", "stock_reconciliation_id", "item_id", "warehouse_id",
        "current_qty", "current_valuation_rate", "qty", "valuation_rate",
        "quantity_difference", "amount_difference",
    ).insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P())
    for row_params in item_rows_to_insert:
        conn.execute(sri_q.get_sql(), row_params)

    audit(conn, "erpclaw-inventory", "add-stock-reconciliation", "stock_reconciliation", sr_id,
           new_values={"naming_series": naming, "item_count": len(items),
                       "difference_amount": str(round_currency(total_diff_amount))})
    conn.commit()
    ok({"stock_reconciliation_id": sr_id, "naming_series": naming,
         "difference_amount": str(round_currency(total_diff_amount)),
         "item_count": len(items)})


# ---------------------------------------------------------------------------
# 29. submit-stock-reconciliation
# ---------------------------------------------------------------------------

def submit_stock_reconciliation(conn, args):
    """Submit a stock reconciliation: post SLE + GL for differences."""
    if not args.stock_reconciliation_id:
        err("--stock-reconciliation-id is required")

    sr_t = Table("stock_reconciliation")
    sr_q = Q.from_(sr_t).select(sr_t.star).where(sr_t.id == P())
    sr = conn.execute(sr_q.get_sql(), (args.stock_reconciliation_id,)).fetchone()
    if not sr:
        err(f"Stock reconciliation {args.stock_reconciliation_id} not found")
    if sr["status"] != "draft":
        err(f"Cannot submit: reconciliation is '{sr['status']}' (must be 'draft')")

    sr_dict = row_to_dict(sr)
    company_id = sr_dict["company_id"]
    posting_date = sr_dict["posting_date"]

    # Fetch reconciliation items
    sri_t = Table("stock_reconciliation_item")
    sri_q = (Q.from_(sri_t).select(sri_t.star)
             .where(sri_t.stock_reconciliation_id == P()))
    sri_rows = conn.execute(sri_q.get_sql(), (args.stock_reconciliation_id,)).fetchall()
    if not sri_rows:
        err("Stock reconciliation has no items")

    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, company_id)

    # Build SLE entries for quantity differences
    sle_entries = []
    for sri in sri_rows:
        item = row_to_dict(sri)
        qty_diff = to_decimal(item["quantity_difference"])
        if qty_diff == 0:
            continue

        valuation_rate = to_decimal(item["valuation_rate"])
        sle_entries.append({
            "item_id": item["item_id"],
            "warehouse_id": item["warehouse_id"],
            "actual_qty": str(round_currency(qty_diff)),
            "incoming_rate": str(round_currency(valuation_rate)) if qty_diff > 0 else "0",
            "fiscal_year": fiscal_year,
        })

    sle_ids = []
    if sle_entries:
        try:
            sle_ids = insert_sle_entries(
                conn, sle_entries,
                voucher_type="stock_reconciliation",
                voucher_id=args.stock_reconciliation_id,
                posting_date=posting_date,
                company_id=company_id,
            )
        except ValueError as e:
            sys.stderr.write(f"[erpclaw-inventory] {e}\n")
            err(f"SLE posting failed: {e}")

    # Build GL entries for value adjustments
    gl_ids = []
    if sle_ids:
        sle_rows_t = Table("stock_ledger_entry")
        sle_rows_q = (Q.from_(sle_rows_t).select(sle_rows_t.star)
                      .where(sle_rows_t.voucher_type == "stock_reconciliation")
                      .where(sle_rows_t.voucher_id == P())
                      .where(sle_rows_t.is_cancelled == 0))
        sle_rows = conn.execute(sle_rows_q.get_sql(), (args.stock_reconciliation_id,)).fetchall()
        sle_dicts = [row_to_dict(r) for r in sle_rows]

        # Find stock adjustment account as contra for reconciliation
        # Uses account_type filter — kept as PyPika
        acct_t = Table("account")
        acct_q = (Q.from_(acct_t).select(acct_t.id)
                  .where(acct_t.account_type == "stock_adjustment")
                  .where(acct_t.company_id == P())
                  .where(acct_t.is_group == 0)
                  .limit(1))
        stock_adj_acct = conn.execute(acct_q.get_sql(), (company_id,)).fetchone()
        expense_account_id = stock_adj_acct["id"] if stock_adj_acct else None

        gl_entries = create_perpetual_inventory_gl(
            conn, sle_dicts,
            voucher_type="stock_reconciliation",
            voucher_id=args.stock_reconciliation_id,
            posting_date=posting_date,
            company_id=company_id,
            expense_account_id=expense_account_id,
            cost_center_id=cost_center_id,
        )

        if gl_entries:
            for gle in gl_entries:
                gle["fiscal_year"] = fiscal_year
            try:
                gl_ids = insert_gl_entries(
                    conn, gl_entries,
                    voucher_type="stock_reconciliation",
                    voucher_id=args.stock_reconciliation_id,
                    posting_date=posting_date,
                    company_id=company_id,
                    remarks=f"Stock Reconciliation {sr_dict['naming_series']}",
                )
            except ValueError as e:
                sys.stderr.write(f"[erpclaw-inventory] {e}\n")
                err(f"GL posting failed: {e}")

    # Update status
    conn.execute(
        "UPDATE stock_reconciliation SET status = 'submitted', updated_at = datetime('now') WHERE id = ?",
        (args.stock_reconciliation_id,),
    )

    audit(conn, "erpclaw-inventory", "submit-stock-reconciliation", "stock_reconciliation",
           args.stock_reconciliation_id,
           new_values={"sle_count": len(sle_ids), "gl_count": len(gl_ids)})
    conn.commit()

    ok({"stock_reconciliation_id": args.stock_reconciliation_id,
         "sle_entries_created": len(sle_ids),
         "gl_entries_created": len(gl_ids)})


# ---------------------------------------------------------------------------
# 30. revalue-stock
# ---------------------------------------------------------------------------

def revalue_stock(conn, args):
    """Revalue inventory for an item in a warehouse.

    Changes the valuation rate without affecting quantity. Creates:
    - SLE entry with actual_qty=0 recording the new rate
    - GL entries adjusting stock value (Stock-in-Hand vs Stock-Adjustment)
    - Audit trail in stock_revaluation table

    This is a one-step action: no draft state, posts immediately.
    """
    item_id = args.item_id
    warehouse_id = args.warehouse_id
    new_rate = args.new_rate
    posting_date = args.posting_date
    reason = args.reason

    if not item_id:
        err("--item-id is required")
    if not warehouse_id:
        err("--warehouse-id is required")
    if not new_rate:
        err("--new-rate is required")
    if not posting_date:
        err("--posting-date is required")

    # Validate new_rate
    try:
        new_rate_d = to_decimal(new_rate)
    except (InvalidOperation, ValueError):
        err(f"Invalid --new-rate: {new_rate}")
    if new_rate_d < 0:
        err("--new-rate must be non-negative")

    # Validate item exists and is a stock item
    item_t = Table("item")
    item_q = (Q.from_(item_t)
              .select(item_t.id, item_t.item_code, item_t.item_name, item_t.is_stock_item)
              .where(item_t.id == P()))
    item_row = conn.execute(item_q.get_sql(), (item_id,)).fetchone()
    if not item_row:
        err(f"Item {item_id} not found")
    if not item_row["is_stock_item"]:
        err(f"Item {item_row['item_name']} is not a stock item")

    # Validate warehouse
    wh_t = Table("warehouse")
    wh_q = (Q.from_(wh_t)
            .select(wh_t.id, wh_t.name, wh_t.company_id, wh_t.account_id)
            .where(wh_t.id == P()))
    wh_row = conn.execute(wh_q.get_sql(), (warehouse_id,)).fetchone()
    if not wh_row:
        err(f"Warehouse {warehouse_id} not found")
    company_id = wh_row["company_id"]

    # Get current stock balance
    balance = get_stock_balance(conn, item_id, warehouse_id)
    current_qty = to_decimal(balance["qty"])
    old_rate_d = to_decimal(balance["valuation_rate"])
    old_value = to_decimal(balance["stock_value"])

    if current_qty <= 0:
        err(f"Cannot revalue: no stock on hand for item '{item_row['item_name']}' "
            f"in warehouse '{wh_row['name']}' (qty={current_qty})")

    if new_rate_d == old_rate_d:
        err(f"New rate ({new_rate_d}) is the same as current rate ({old_rate_d}). No revaluation needed.")

    # Compute adjustment
    new_value = round_currency(current_qty * new_rate_d)
    adjustment = round_currency(new_value - old_value)

    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, company_id)

    # Generate IDs
    reval_id = str(uuid.uuid4())
    sle_id = str(uuid.uuid4())

    # Naming series
    naming = get_next_name(conn, "stock_revaluation", company_id=company_id)

    # --- Single atomic transaction ---

    # 1. Insert SLE with actual_qty=0 but new valuation and value difference
    # Uses datetime('now') as LiteralValue and mixed literal/param values
    # Kept as raw SQL for clarity with the mixed NULL/literal/param pattern
    conn.execute(
        """
        INSERT INTO stock_ledger_entry (
            id, posting_date, posting_time, item_id, warehouse_id,
            actual_qty, qty_after_transaction, valuation_rate,
            stock_value, stock_value_difference,
            voucher_type, voucher_id, batch_id, serial_number,
            incoming_rate, is_cancelled, fiscal_year, created_at
        ) VALUES (?, ?, NULL, ?, ?, '0', ?, ?, ?, ?, 'stock_revaluation', ?,
                  NULL, NULL, '0', 0, ?, datetime('now'))
        """,
        (
            sle_id, posting_date, item_id, warehouse_id,
            str(round_currency(current_qty)),
            str(round_currency(new_rate_d)),
            str(new_value),
            str(adjustment),
            reval_id,
            fiscal_year,
        ),
    )

    # 2. Create GL entries for the value adjustment
    gl_ids = []
    if adjustment != 0:
        # Stock-in-Hand account (from warehouse)
        warehouse_account_id = wh_row["account_id"]
        if not warehouse_account_id:
            stock_acct_t = Table("account")
            stock_acct_q = (Q.from_(stock_acct_t).select(stock_acct_t.id)
                            .where(stock_acct_t.account_type == "stock")
                            .where(stock_acct_t.company_id == P())
                            .where(stock_acct_t.is_group == 0)
                            .limit(1))
            stock_acct = conn.execute(stock_acct_q.get_sql(), (company_id,)).fetchone()
            warehouse_account_id = stock_acct["id"] if stock_acct else None

        # Stock Adjustment account (contra)
        adj_acct_t = Table("account")
        adj_acct_q = (Q.from_(adj_acct_t).select(adj_acct_t.id)
                      .where(adj_acct_t.account_type == "stock_adjustment")
                      .where(adj_acct_t.company_id == P())
                      .where(adj_acct_t.is_group == 0)
                      .limit(1))
        stock_adj_acct = conn.execute(adj_acct_q.get_sql(), (company_id,)).fetchone()
        stock_adj_account_id = stock_adj_acct["id"] if stock_adj_acct else None

        if warehouse_account_id and stock_adj_account_id:
            abs_adj = abs(adjustment)
            gl_entries = []
            if adjustment > 0:
                # Rate increased: DR Stock-in-Hand, CR Stock Adjustment
                gl_entries.append({
                    "account_id": warehouse_account_id,
                    "debit": str(round_currency(abs_adj)),
                    "credit": "0",
                })
                gl_entries.append({
                    "account_id": stock_adj_account_id,
                    "debit": "0",
                    "credit": str(round_currency(abs_adj)),
                    "cost_center_id": cost_center_id,
                })
            else:
                # Rate decreased: DR Stock Adjustment, CR Stock-in-Hand
                gl_entries.append({
                    "account_id": stock_adj_account_id,
                    "debit": str(round_currency(abs_adj)),
                    "credit": "0",
                    "cost_center_id": cost_center_id,
                })
                gl_entries.append({
                    "account_id": warehouse_account_id,
                    "debit": "0",
                    "credit": str(round_currency(abs_adj)),
                })

            for gle in gl_entries:
                gle["fiscal_year"] = fiscal_year

            try:
                gl_ids = insert_gl_entries(
                    conn, gl_entries,
                    voucher_type="stock_revaluation",
                    voucher_id=reval_id,
                    posting_date=posting_date,
                    company_id=company_id,
                    remarks=f"Stock Revaluation {naming}: "
                            f"{item_row['item_name']} rate {old_rate_d} → {new_rate_d}",
                )
            except ValueError as e:
                sys.stderr.write(f"[erpclaw-inventory] GL posting failed: {e}\n")
                err(f"GL posting failed: {e}")

    # 3. Insert stock_revaluation record
    # Uses datetime('now') for created_at and updated_at — kept as raw SQL
    conn.execute(
        """INSERT INTO stock_revaluation (
            id, naming_series, company_id, item_id, warehouse_id,
            posting_date, current_qty, old_rate, new_rate,
            adjustment_amount, reason, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted',
                  datetime('now'), datetime('now'))""",
        (
            reval_id, naming, company_id, item_id, warehouse_id,
            posting_date,
            str(round_currency(current_qty)),
            str(round_currency(old_rate_d)),
            str(round_currency(new_rate_d)),
            str(adjustment),
            reason,
        ),
    )

    audit(conn, "erpclaw-inventory", "revalue-stock", "stock_revaluation",
          reval_id, new_values={
              "item_id": item_id, "warehouse_id": warehouse_id,
              "old_rate": str(old_rate_d), "new_rate": str(new_rate_d),
              "adjustment": str(adjustment), "gl_count": len(gl_ids),
          })
    conn.commit()

    ok({
        "revaluation_id": reval_id,
        "naming_series": naming,
        "item_id": item_id,
        "item_name": item_row["item_name"],
        "warehouse": wh_row["name"],
        "current_qty": str(round_currency(current_qty)),
        "old_rate": str(round_currency(old_rate_d)),
        "new_rate": str(round_currency(new_rate_d)),
        "adjustment_amount": str(adjustment),
        "gl_entries_created": len(gl_ids),
    })


# ---------------------------------------------------------------------------
# 31. list-stock-revaluations
# ---------------------------------------------------------------------------

def list_stock_revaluations(conn, args):
    """List stock revaluations for a company."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    limit = int(args.limit or "20")
    offset = int(args.offset or "0")

    sr = Table("stock_revaluation").as_("sr")
    i = Table("item").as_("i")
    w = Table("warehouse").as_("w")

    rows_q = (Q.from_(sr)
              .join(i).on(i.id == sr.item_id)
              .join(w).on(w.id == sr.warehouse_id)
              .select(sr.star, i.item_code, i.item_name, w.name.as_("warehouse_name"))
              .where(sr.company_id == P())
              .orderby(sr.created_at, order=Order.desc)
              .limit(P()).offset(P()))

    rows = conn.execute(rows_q.get_sql(), (company_id, limit, offset)).fetchall()

    total_t = Table("stock_revaluation")
    total_q = (Q.from_(total_t)
               .select(fn.Count("*").as_("cnt"))
               .where(total_t.company_id == P()))
    total = conn.execute(total_q.get_sql(), (company_id,)).fetchone()["cnt"]

    ok({
        "revaluations": [row_to_dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    })


# ---------------------------------------------------------------------------
# 32. get-stock-revaluation
# ---------------------------------------------------------------------------

def get_stock_revaluation(conn, args):
    """Get details of a stock revaluation."""
    reval_id = args.revaluation_id
    if not reval_id:
        err("--revaluation-id is required")

    sr = Table("stock_revaluation").as_("sr")
    i = Table("item").as_("i")
    w = Table("warehouse").as_("w")

    row_q = (Q.from_(sr)
             .join(i).on(i.id == sr.item_id)
             .join(w).on(w.id == sr.warehouse_id)
             .select(sr.star, i.item_code, i.item_name, w.name.as_("warehouse_name"))
             .where(sr.id == P()))
    row = conn.execute(row_q.get_sql(), (reval_id,)).fetchone()
    if not row:
        err(f"Stock revaluation {reval_id} not found")

    result = row_to_dict(row)

    # Include SLE entries
    sle_t = Table("stock_ledger_entry")
    sle_q = (Q.from_(sle_t).select(sle_t.star)
             .where(sle_t.voucher_type == "stock_revaluation")
             .where(sle_t.voucher_id == P()))
    sle_rows = conn.execute(sle_q.get_sql(), (reval_id,)).fetchall()
    result["sle_entries"] = [row_to_dict(r) for r in sle_rows]

    # Include GL entries
    gl_t = Table("gl_entry")
    gl_q = (Q.from_(gl_t).select(gl_t.star)
            .where(gl_t.voucher_type == "stock_revaluation")
            .where(gl_t.voucher_id == P()))
    gl_rows = conn.execute(gl_q.get_sql(), (reval_id,)).fetchall()
    result["gl_entries"] = [row_to_dict(r) for r in gl_rows]

    ok(result)


# ---------------------------------------------------------------------------
# 33. cancel-stock-revaluation
# ---------------------------------------------------------------------------

def cancel_stock_revaluation(conn, args):
    """Cancel a stock revaluation: reverse SLE and GL entries."""
    reval_id = args.revaluation_id
    if not reval_id:
        err("--revaluation-id is required")

    sr_t = Table("stock_revaluation")
    sr_q = Q.from_(sr_t).select(sr_t.star).where(sr_t.id == P())
    row = conn.execute(sr_q.get_sql(), (reval_id,)).fetchone()
    if not row:
        err(f"Stock revaluation {reval_id} not found")
    if row["status"] != "submitted":
        err(f"Cannot cancel: revaluation is '{row['status']}' (must be 'submitted')")

    reval = row_to_dict(row)
    posting_date = reval["posting_date"]

    # Reverse SLE entries
    try:
        reverse_sle_entries(
            conn,
            voucher_type="stock_revaluation",
            voucher_id=reval_id,
            posting_date=posting_date,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-inventory] SLE reversal failed: {e}\n")
        err(f"SLE reversal failed: {e}")

    # Reverse GL entries
    try:
        reverse_gl_entries(
            conn,
            voucher_type="stock_revaluation",
            voucher_id=reval_id,
            posting_date=posting_date,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-inventory] GL reversal failed: {e}\n")
        err(f"GL reversal failed: {e}")

    # Update status
    conn.execute(
        "UPDATE stock_revaluation SET status = 'cancelled', updated_at = datetime('now') WHERE id = ?",
        (reval_id,),
    )

    audit(conn, "erpclaw-inventory", "cancel-stock-revaluation", "stock_revaluation",
          reval_id, new_values={"status": "cancelled"})
    conn.commit()

    ok({
        "revaluation_id": reval_id,
        "cancelled": True,
        "item_id": reval["item_id"],
        "warehouse_id": reval["warehouse_id"],
    })


# ---------------------------------------------------------------------------
# 34. status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """Inventory summary for a company."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    item_t = Table("item")
    items_q = Q.from_(item_t).select(fn.Count("*").as_("cnt"))
    items_count = conn.execute(items_q.get_sql()).fetchone()["cnt"]

    wh_t = Table("warehouse")
    wh_q = (Q.from_(wh_t).select(fn.Count("*").as_("cnt"))
            .where(wh_t.company_id == P()))
    warehouses_count = conn.execute(wh_q.get_sql(), (company_id,)).fetchone()["cnt"]

    # Stock entries by status
    se_t = Table("stock_entry")
    se_q = (Q.from_(se_t)
            .select(se_t.status, fn.Count("*").as_("cnt"))
            .where(se_t.company_id == P())
            .groupby(se_t.status))
    se_rows = conn.execute(se_q.get_sql(), (company_id,)).fetchall()
    se_counts = {"draft": 0, "submitted": 0, "cancelled": 0}
    for row in se_rows:
        se_counts[row["status"]] = row["cnt"]
    se_counts["total"] = sum(se_counts.values())

    # Total stock value using decimal_sum() aggregate
    # JOIN with warehouse for company filter — kept as raw SQL for aggregate
    sv_row = conn.execute(
        """SELECT COALESCE(decimal_sum(sle.stock_value_difference), '0') as total_value
           FROM stock_ledger_entry sle
           JOIN warehouse w ON w.id = sle.warehouse_id
           WHERE sle.is_cancelled = 0 AND w.company_id = ?""",
        (company_id,),
    ).fetchone()
    total_stock_value = round_currency(to_decimal(str(sv_row["total_value"])))

    ok({
        "items": items_count,
        "warehouses": warehouses_count,
        "stock_entries": se_counts,
        "total_stock_value": str(total_stock_value),
    })


# ---------------------------------------------------------------------------
# 35. check-reorder
# ---------------------------------------------------------------------------

def check_reorder(conn, args):
    """Find items whose current stock is at or below their reorder level."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    # Get items with a meaningful reorder_level set
    # Uses IS NULL / IS NOT NULL comparisons — kept as raw SQL (rule 16)
    items = conn.execute(
        """SELECT id, item_code, item_name, reorder_level, reorder_qty
           FROM item
           WHERE reorder_level IS NOT NULL
             AND reorder_level != ''
             AND reorder_level != '0'
             AND status = 'active'
           ORDER BY item_name""",
    ).fetchall()

    results = []
    for item in items:
        item_id = item["id"]
        reorder_level = to_decimal(str(item["reorder_level"]))
        reorder_qty = to_decimal(str(item["reorder_qty"])) if item["reorder_qty"] else Decimal("0")

        # Calculate current stock across all warehouses for this company
        # Uses decimal_sum() aggregate with JOIN — kept as raw SQL
        stock_row = conn.execute(
            """SELECT COALESCE(decimal_sum(sle.actual_qty), '0') AS total_qty
               FROM stock_ledger_entry sle
               JOIN warehouse w ON w.id = sle.warehouse_id
               WHERE sle.item_id = ?
                 AND sle.is_cancelled = 0
                 AND w.company_id = ?""",
            (item_id, company_id),
        ).fetchone()

        current_stock = to_decimal(str(stock_row["total_qty"]))

        if current_stock <= reorder_level:
            shortfall = round_currency(reorder_level - current_stock)
            results.append({
                "item_id": item_id,
                "item_code": item["item_code"],
                "item_name": item["item_name"],
                "current_stock": str(round_currency(current_stock)),
                "reorder_level": str(round_currency(reorder_level)),
                "reorder_qty": str(round_currency(reorder_qty)),
                "shortfall": str(shortfall),
            })

    ok({
        "items_below_reorder": len(results),
        "items": results,
    })


# ---------------------------------------------------------------------------
# import-items
# ---------------------------------------------------------------------------

def import_items(conn, args):
    """Bulk import items from a CSV file.

    CSV columns: item_code, name, uom, group (optional),
    valuation_method (optional), description (optional).

    Items are globally unique by item_code (no company_id on item table).
    """
    csv_path = args.csv_path
    if not csv_path:
        err("--csv-path is required")

    # Path safety: resolve symlinks, require .csv extension, must be a regular file
    csv_real = os.path.realpath(csv_path)
    if not csv_real.lower().endswith(".csv"):
        err("--csv-path must point to a .csv file")
    if not os.path.isfile(csv_real):
        err(f"File not found: {csv_path}")

    from erpclaw_lib.csv_import import validate_csv, parse_csv_rows

    errors = validate_csv(csv_real, "item")
    if errors:
        err(f"CSV validation failed: {'; '.join(errors)}")

    rows = parse_csv_rows(csv_real, "item")
    if not rows:
        err("CSV file is empty")

    imported = 0
    skipped = 0
    for row in rows:
        item_code = row.get("item_code", "")
        name = row.get("name", "")
        uom = row.get("uom", "Nos")

        # Check for duplicate (item_code is globally unique)
        item_t = Table("item")
        dup_q = Q.from_(item_t).select(item_t.id).where(item_t.item_code == P())
        existing = conn.execute(dup_q.get_sql(), (item_code,)).fetchone()
        if existing:
            skipped += 1
            continue

        # Look up or default item group
        group_name = row.get("group")
        group_id = None
        if group_name:
            ig_t = Table("item_group")
            grp_q = Q.from_(ig_t).select(ig_t.id).where(ig_t.name == P())
            grp = conn.execute(grp_q.get_sql(), (group_name,)).fetchone()
            if grp:
                group_id = grp["id"]

        item_id = str(uuid.uuid4())
        ins_t = Table("item")
        ins_q = Q.into(ins_t).columns(
            "id", "item_code", "item_name", "item_group_id",
            "stock_uom", "valuation_method", "description", "status",
        ).insert(P(), P(), P(), P(), P(), P(), P(), "active")
        conn.execute(
            ins_q.get_sql(),
            (item_id, item_code, name, group_id, uom,
             row.get("valuation_method", "moving_average").lower(),
             row.get("description")),
        )
        imported += 1

    conn.commit()
    ok({"imported": imported, "skipped": skipped, "total_rows": len(rows)})


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-item": add_item,
    "update-item": update_item,
    "get-item": get_item,
    "list-items": list_items,
    "add-item-group": add_item_group,
    "list-item-groups": list_item_groups,
    "add-warehouse": add_warehouse,
    "update-warehouse": update_warehouse,
    "list-warehouses": list_warehouses,
    "add-stock-entry": add_stock_entry,
    "get-stock-entry": get_stock_entry,
    "list-stock-entries": list_stock_entries,
    "submit-stock-entry": submit_stock_entry,
    "cancel-stock-entry": cancel_stock_entry,
    "create-stock-ledger-entries": create_stock_ledger_entries,
    "reverse-stock-ledger-entries": reverse_stock_ledger_entries,
    "get-stock-balance": get_stock_balance_action,
    "stock-balance": stock_balance_report,  # alias — "stock balance" routes to company-wide report
    "stock-balance-report": stock_balance_report,
    "stock-ledger-report": stock_ledger_report,
    "add-batch": add_batch,
    "list-batches": list_batches,
    "add-serial-number": add_serial_number,
    "list-serial-numbers": list_serial_numbers,
    "add-price-list": add_price_list,
    "add-item-price": add_item_price,
    "get-item-price": get_item_price,
    "add-pricing-rule": add_pricing_rule,
    "add-stock-reconciliation": add_stock_reconciliation,
    "submit-stock-reconciliation": submit_stock_reconciliation,
    "revalue-stock": revalue_stock,
    "list-stock-revaluations": list_stock_revaluations,
    "get-stock-revaluation": get_stock_revaluation,
    "cancel-stock-revaluation": cancel_stock_revaluation,
    "check-reorder": check_reorder,
    "import-items": import_items,
    "status": status_action,
}


def main():
    parser = argparse.ArgumentParser(description="ERPClaw Inventory Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Item fields
    parser.add_argument("--item-id")
    parser.add_argument("--item-code")
    parser.add_argument("--item-name")
    parser.add_argument("--item-group")
    parser.add_argument("--item-type")
    parser.add_argument("--stock-uom")
    parser.add_argument("--valuation-method")
    parser.add_argument("--has-batch")
    parser.add_argument("--has-serial")
    parser.add_argument("--standard-rate")
    parser.add_argument("--reorder-level")
    parser.add_argument("--reorder-qty")
    parser.add_argument("--status", dest="item_status")

    # Item group
    parser.add_argument("--parent-id")
    parser.add_argument("--name")

    # Warehouse
    parser.add_argument("--warehouse-id")
    parser.add_argument("--warehouse-type")
    parser.add_argument("--account-id")
    parser.add_argument("--is-group")
    parser.add_argument("--company-id")
    parser.add_argument("--csv-path")

    # Stock entry
    parser.add_argument("--stock-entry-id")
    parser.add_argument("--entry-type")
    parser.add_argument("--posting-date")
    parser.add_argument("--items")  # JSON

    # Stock entry list filters
    parser.add_argument("--status-filter", dest="se_status")

    # Cross-skill SLE
    parser.add_argument("--voucher-type")
    parser.add_argument("--voucher-id")
    parser.add_argument("--entries")  # JSON

    # Batch
    parser.add_argument("--batch-name")
    parser.add_argument("--batch-id")
    parser.add_argument("--expiry-date")
    parser.add_argument("--manufacturing-date")

    # Serial number
    parser.add_argument("--serial-no")
    parser.add_argument("--serial-status", dest="sn_status")

    # Pricing
    parser.add_argument("--price-list-id")
    parser.add_argument("--rate")
    parser.add_argument("--min-qty")
    parser.add_argument("--max-qty")
    parser.add_argument("--valid-from")
    parser.add_argument("--valid-to")
    parser.add_argument("--qty")
    parser.add_argument("--party-id")
    parser.add_argument("--currency")
    parser.add_argument("--is-buying")
    parser.add_argument("--is-selling")

    # Pricing rule
    parser.add_argument("--applies-to")
    parser.add_argument("--entity-id")
    parser.add_argument("--discount-percentage")
    parser.add_argument("--pricing-rule-rate", dest="pr_rate")
    parser.add_argument("--priority", type=int, default=None)

    # Stock reconciliation
    parser.add_argument("--stock-reconciliation-id")

    # Stock revaluation
    parser.add_argument("--revaluation-id")
    parser.add_argument("--new-rate")
    parser.add_argument("--reason")

    # Search / filters
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
        sys.stderr.write(f"[erpclaw-inventory] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
