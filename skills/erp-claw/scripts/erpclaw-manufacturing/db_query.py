#!/usr/bin/env python3
"""ERPClaw Manufacturing Skill — db_query.py

BOMs, work orders, job cards, production planning (MRP), and subcontracting.
All 24 actions are routed through this single entry point.

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

REQUIRED_TABLES = ["company", "item"]

VALID_WORKSTATION_STATUSES = ("active", "maintenance", "offline")
VALID_WO_STATUSES = (
    "draft", "not_started", "in_process", "completed", "stopped", "cancelled",
)
VALID_JOB_CARD_STATUSES = ("open", "in_process", "completed", "cancelled")
VALID_PP_STATUSES = ("draft", "submitted", "material_requested", "cancelled")
VALID_SCO_STATUSES = (
    "draft", "submitted", "partially_received", "completed", "cancelled",
)

# Maximum recursion depth for BOM explosion to prevent infinite loops
MAX_BOM_EXPLOSION_DEPTH = 10



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
    t = Table("fiscal_year")
    q = (Q.from_(t).select(t.name)
         .where(t.start_date <= P())
         .where(t.end_date >= P())
         .where(t.is_closed == 0))
    fy = conn.execute(q.get_sql(), (posting_date, posting_date)).fetchone()
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


def _validate_item_exists(conn, item_id: str, label: str = "Item"):
    """Validate that an item exists and return the row, or error."""
    t = Table("item")
    q = Q.from_(t).select(t.star).where(t.id == P())
    item = conn.execute(q.get_sql(), (item_id,)).fetchone()
    if not item:
        err(f"{label} {item_id} not found")
    return item


def _validate_bom_exists(conn, bom_id: str):
    """Validate that a BOM exists and return the row, or error."""
    t = Table("bom")
    q = Q.from_(t).select(t.star).where(t.id == P())
    bom = conn.execute(q.get_sql(), (bom_id,)).fetchone()
    if not bom:
        err(f"BOM {bom_id} not found",
             suggestion="Use 'list boms' to see available BOMs.")
    return bom


def _validate_company_exists(conn, company_id: str):
    """Validate that a company exists and return the row, or error."""
    t = Table("company")
    q = Q.from_(t).select(t.id).where(t.id == P())
    company = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not company:
        err(f"Company {company_id} not found")
    return company


def _validate_operation_exists(conn, operation_id: str):
    """Validate that an operation exists and return the row, or error."""
    t = Table("operation")
    q = Q.from_(t).select(t.star).where(t.id == P())
    op = conn.execute(q.get_sql(), (operation_id,)).fetchone()
    if not op:
        err(f"Operation {operation_id} not found")
    return op


def _validate_workstation_exists(conn, workstation_id: str):
    """Validate that a workstation exists and return the row, or error."""
    t = Table("workstation")
    q = Q.from_(t).select(t.star).where(t.id == P())
    ws = conn.execute(q.get_sql(), (workstation_id,)).fetchone()
    if not ws:
        err(f"Workstation {workstation_id} not found")
    return ws


def _validate_warehouse_exists(conn, warehouse_id: str, label: str = "Warehouse"):
    """Validate that a warehouse exists and return the row, or error."""
    t = Table("warehouse")
    q = Q.from_(t).select(t.star).where(t.id == P())
    wh = conn.execute(q.get_sql(), (warehouse_id,)).fetchone()
    if not wh:
        err(f"{label} {warehouse_id} not found")
    return wh


def _calculate_bom_item_costs(items_data: list) -> Decimal:
    """Calculate total raw material cost from a list of BOM item dicts.

    Each item dict must have "quantity" and "rate" keys (string Decimal values).
    Returns the sum of (quantity * rate) for all items, rounded.
    """
    total = Decimal("0")
    for item in items_data:
        qty = to_decimal(item.get("quantity", "0"))
        rate = to_decimal(item.get("rate", "0"))
        total += qty * rate
    return round_currency(total)


def _calculate_operation_costs(conn, operations_data: list) -> Decimal:
    """Calculate total operating cost from a list of operation dicts.

    Each operation dict should have time_in_minutes and optionally
    operating_cost (overrides workstation hourly rate lookup).
    Returns the sum of (time_in_minutes / 60 * cost_per_hour), rounded.
    """
    total = Decimal("0")
    for op in operations_data:
        explicit_cost = op.get("operating_cost")
        if explicit_cost and to_decimal(explicit_cost) > 0:
            total += to_decimal(explicit_cost)
        else:
            # Calculate from workstation hourly rate
            time_mins = to_decimal(op.get("time_in_minutes", "0"))
            ws_id = op.get("workstation_id")
            if ws_id and time_mins > 0:
                ws_t = Table("workstation")
                ws_q = Q.from_(ws_t).select(ws_t.operating_cost_per_hour).where(ws_t.id == P())
                ws = conn.execute(ws_q.get_sql(), (ws_id,)).fetchone()
                if ws:
                    hour_rate = to_decimal(ws["operating_cost_per_hour"])
                    cost = round_currency((time_mins / Decimal("60")) * hour_rate)
                    total += cost
    return round_currency(total)


# ---------------------------------------------------------------------------
# 1. add-bom
# ---------------------------------------------------------------------------

def add_bom(conn, args):
    """Create a Bill of Materials.

    Required: --item-id (finished goods), --items (JSON), --company-id
    Optional: --quantity (default "1"), --operations (JSON), --routing-id,
              --is-default, --uom
    """
    if not args.item_id:
        err("--item-id is required (finished goods item)")
    if not args.items:
        err("--items is required (JSON array of raw materials)")
    if not args.company_id:
        err("--company-id is required")

    # Validate finished goods item
    fg_item = _validate_item_exists(conn, args.item_id, "Finished goods item")

    # Validate company
    _validate_company_exists(conn, args.company_id)

    # Parse and validate items JSON
    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    bom_qty = to_decimal(args.quantity or "1")
    if bom_qty <= 0:
        err("--quantity must be greater than 0")

    # Generate naming series
    naming = get_next_name(conn, "bom", company_id=args.company_id)

    # Validate and prepare BOM item rows
    bom_item_rows = []
    for i, item in enumerate(items):
        rm_item_id = item.get("item_id")
        if not rm_item_id:
            err(f"Item {i}: item_id is required")

        # Validate raw material item exists
        _validate_item_exists(conn, rm_item_id, f"Item {i}: raw material item")

        rm_qty = to_decimal(item.get("quantity", "0"))
        if rm_qty <= 0:
            err(f"Item {i}: quantity must be > 0")

        rm_rate = to_decimal(item.get("rate", "0"))
        if rm_rate < 0:
            err(f"Item {i}: rate must be >= 0")

        rm_amount = round_currency(rm_qty * rm_rate)
        rm_uom = item.get("uom")
        is_sub_assembly = int(item.get("is_sub_assembly", 0))
        sub_bom_id = item.get("sub_bom_id")
        source_warehouse_id = item.get("source_warehouse_id")
        scrap_percentage = item.get("scrap_percentage", "0")

        # Validate sub-BOM reference if this is a sub-assembly
        if is_sub_assembly and sub_bom_id:
            bom_t = Table("bom")
            sub_bom_q = Q.from_(bom_t).select(bom_t.id, bom_t.item_id).where(bom_t.id == P())
            sub_bom = conn.execute(sub_bom_q.get_sql(), (sub_bom_id,)).fetchone()
            if not sub_bom:
                err(f"Item {i}: sub_bom_id {sub_bom_id} not found")
            if sub_bom["item_id"] != rm_item_id:
                err(
                    f"Item {i}: sub_bom_id {sub_bom_id} produces item "
                    f"{sub_bom['item_id']}, but item_id is {rm_item_id}"
                )

        # Validate source warehouse if provided
        if source_warehouse_id:
            _validate_warehouse_exists(
                conn, source_warehouse_id,
                f"Item {i}: source warehouse",
            )

        bom_item_rows.append({
            "id": str(uuid.uuid4()),
            "item_id": rm_item_id,
            "quantity": str(round_currency(rm_qty)),
            "uom": rm_uom,
            "rate": str(round_currency(rm_rate)),
            "amount": str(rm_amount),
            "source_warehouse_id": source_warehouse_id,
            "is_sub_assembly": is_sub_assembly,
            "sub_bom_id": sub_bom_id,
            "scrap_percentage": str(to_decimal(scrap_percentage)),
        })

    # Calculate raw material cost
    raw_material_cost = Decimal("0")
    for row in bom_item_rows:
        raw_material_cost += to_decimal(row["amount"])
    raw_material_cost = round_currency(raw_material_cost)

    # Handle operations: from --routing-id or --operations JSON
    operations = _parse_json_arg(args.operations, "operations") if args.operations else None
    routing_id = args.routing_id

    bom_operation_rows = []
    with_operations = 0

    if routing_id:
        # Copy operations from routing
        rt_t = Table("routing")
        rt_q = Q.from_(rt_t).select(rt_t.id).where(rt_t.id == P())
        routing = conn.execute(rt_q.get_sql(), (routing_id,)).fetchone()
        if not routing:
            err(f"Routing {routing_id} not found")

        ro_t = Table("routing_operation")
        ro_q = (Q.from_(ro_t)
                .select(ro_t.operation_id, ro_t.workstation_id, ro_t.sequence,
                        ro_t.time_in_minutes, ro_t.operating_cost)
                .where(ro_t.routing_id == P())
                .orderby(ro_t.sequence))
        routing_ops = conn.execute(ro_q.get_sql(), (routing_id,)).fetchall()
        if not routing_ops:
            err(f"Routing {routing_id} has no operations")

        ws_t = Table("workstation")
        ws_cost_q = Q.from_(ws_t).select(ws_t.operating_cost_per_hour).where(ws_t.id == P())
        ws_cost_sql = ws_cost_q.get_sql()
        for ro in routing_ops:
            ro_dict = row_to_dict(ro)
            # If no explicit operating_cost, calculate from workstation
            op_cost = to_decimal(ro_dict.get("operating_cost", "0"))
            if op_cost <= 0 and ro_dict.get("workstation_id"):
                ws = conn.execute(ws_cost_sql, (ro_dict["workstation_id"],)).fetchone()
                if ws:
                    time_mins = to_decimal(ro_dict.get("time_in_minutes", "0"))
                    op_cost = round_currency(
                        (time_mins / Decimal("60"))
                        * to_decimal(ws["operating_cost_per_hour"])
                    )

            bom_operation_rows.append({
                "id": str(uuid.uuid4()),
                "operation_id": ro_dict["operation_id"],
                "workstation_id": ro_dict.get("workstation_id"),
                "sequence": ro_dict.get("sequence", 0),
                "time_in_minutes": ro_dict.get("time_in_minutes", "0"),
                "operating_cost": str(round_currency(op_cost)),
                "description": None,
            })
        with_operations = 1

    elif operations:
        # Inline operations from JSON
        if not isinstance(operations, list):
            err("--operations must be a JSON array")

        for i, op in enumerate(operations):
            op_id_ref = op.get("operation_id")
            if not op_id_ref:
                err(f"Operation {i}: operation_id is required")

            _validate_operation_exists(conn, op_id_ref)

            ws_id = op.get("workstation_id")
            if ws_id:
                _validate_workstation_exists(conn, ws_id)

            # Calculate operating cost if not provided
            op_cost = to_decimal(op.get("operating_cost", "0"))
            if op_cost <= 0 and ws_id:
                ws_t2 = Table("workstation")
                ws_cost_q2 = Q.from_(ws_t2).select(ws_t2.operating_cost_per_hour).where(ws_t2.id == P())
                ws = conn.execute(ws_cost_q2.get_sql(), (ws_id,)).fetchone()
                if ws:
                    time_mins = to_decimal(op.get("time_in_minutes", "0"))
                    op_cost = round_currency(
                        (time_mins / Decimal("60"))
                        * to_decimal(ws["operating_cost_per_hour"])
                    )

            bom_operation_rows.append({
                "id": str(uuid.uuid4()),
                "operation_id": op_id_ref,
                "workstation_id": ws_id,
                "sequence": op.get("sequence", i + 1),
                "time_in_minutes": op.get("time_in_minutes", "0"),
                "operating_cost": str(round_currency(op_cost)),
                "description": op.get("description"),
            })
        with_operations = 1

    # Calculate operating cost
    operating_cost = Decimal("0")
    for op_row in bom_operation_rows:
        operating_cost += to_decimal(op_row["operating_cost"])
    operating_cost = round_currency(operating_cost)

    # Total cost = raw material + operating
    total_cost = round_currency(raw_material_cost + operating_cost)

    # Determine is_default
    is_default = int(args.is_default) if args.is_default else 0

    # If this is the first BOM for this item in this company, make it default
    if not is_default:
        bom_t = Table("bom")
        existing_bom_q = (Q.from_(bom_t).select(bom_t.id)
                          .where(bom_t.item_id == P())
                          .where(bom_t.company_id == P())
                          .where(bom_t.is_active == 1)
                          .limit(1))
        existing_bom = conn.execute(existing_bom_q.get_sql(), (args.item_id, args.company_id)).fetchone()
        if not existing_bom:
            is_default = 1

    # If setting as default, unset previous defaults for this item+company
    if is_default:
        bom_t = Table("bom")
        unset_q = (Q.update(bom_t)
                   .set(bom_t.is_default, 0)
                   .set(bom_t.updated_at, LiteralValue("datetime('now')"))
                   .where(bom_t.item_id == P())
                   .where(bom_t.company_id == P())
                   .where(bom_t.is_default == 1))
        conn.execute(unset_q.get_sql(), (args.item_id, args.company_id))

    bom_id = str(uuid.uuid4())
    fg_dict = row_to_dict(fg_item)
    uom = args.uom or fg_dict.get("stock_uom")

    # Insert BOM parent
    bom_t = Table("bom")
    bom_ins_q = (Q.into(bom_t).columns(
        "id", "naming_series", "item_id", "quantity", "uom", "is_active", "is_default",
        "operating_cost", "raw_material_cost", "total_cost", "with_operations",
        "routing_id", "company_id"
    ).insert(P(), P(), P(), P(), P(), 1, P(), P(), P(), P(), P(), P(), P()))
    try:
        conn.execute(
            bom_ins_q.get_sql(),
            (bom_id, naming, args.item_id, str(round_currency(bom_qty)),
             uom, is_default,
             str(operating_cost), str(raw_material_cost), str(total_cost),
             with_operations, routing_id, args.company_id),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("BOM creation failed — check for duplicates or invalid data")

    # Insert BOM item rows
    bi_t = Table("bom_item")
    bi_ins_q = (Q.into(bi_t).columns(
        "id", "bom_id", "item_id", "quantity", "uom", "rate", "amount",
        "source_warehouse_id", "is_sub_assembly", "sub_bom_id", "scrap_percentage"
    ).insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
    bi_ins_sql = bi_ins_q.get_sql()
    for row in bom_item_rows:
        conn.execute(
            bi_ins_sql,
            (row["id"], bom_id, row["item_id"], row["quantity"],
             row["uom"], row["rate"], row["amount"],
             row["source_warehouse_id"], row["is_sub_assembly"],
             row["sub_bom_id"], row["scrap_percentage"]),
        )

    # Insert BOM operation rows
    bo_t = Table("bom_operation")
    bo_ins_q = (Q.into(bo_t).columns(
        "id", "bom_id", "operation_id", "workstation_id",
        "time_in_minutes", "operating_cost", "sequence", "description"
    ).insert(P(), P(), P(), P(), P(), P(), P(), P()))
    bo_ins_sql = bo_ins_q.get_sql()
    for op_row in bom_operation_rows:
        conn.execute(
            bo_ins_sql,
            (op_row["id"], bom_id, op_row["operation_id"],
             op_row["workstation_id"], op_row["time_in_minutes"],
             op_row["operating_cost"], op_row["sequence"],
             op_row["description"]),
        )

    audit(conn, "erpclaw-manufacturing", "add-bom", "bom", bom_id,
           new_values={
               "naming_series": naming, "item_id": args.item_id,
               "quantity": str(round_currency(bom_qty)),
               "item_count": len(bom_item_rows),
               "operation_count": len(bom_operation_rows),
               "total_cost": str(total_cost),
           })
    conn.commit()

    ok({
        "bom_id": bom_id,
        "naming_series": naming,
        "item_id": args.item_id,
        "quantity": str(round_currency(bom_qty)),
        "raw_material_cost": str(raw_material_cost),
        "operating_cost": str(operating_cost),
        "total_cost": str(total_cost),
        "item_count": len(bom_item_rows),
        "operation_count": len(bom_operation_rows),
        "is_default": is_default,
    })


# ---------------------------------------------------------------------------
# 2. update-bom
# ---------------------------------------------------------------------------

def update_bom(conn, args):
    """Update an existing Bill of Materials.

    Required: --bom-id
    Optional: --items (replace all), --operations (replace all),
              --quantity, --is-active, --is-default, --routing-id
    """
    if not args.bom_id:
        err("--bom-id is required")

    bom = _validate_bom_exists(conn, args.bom_id)
    bom_dict = row_to_dict(bom)
    company_id = bom_dict["company_id"]
    item_id = bom_dict["item_id"]

    updates = []
    params = []
    updated_fields = []
    recalculate_costs = False

    # Update quantity
    if args.quantity is not None:
        new_qty = to_decimal(args.quantity)
        if new_qty <= 0:
            err("--quantity must be greater than 0")
        updates.append("quantity = ?")
        params.append(str(round_currency(new_qty)))
        updated_fields.append("quantity")
        recalculate_costs = True

    # Update is_active
    if args.is_active is not None:
        is_active = int(args.is_active)
        if is_active not in (0, 1):
            err("--is-active must be 0 or 1")
        updates.append("is_active = ?")
        params.append(is_active)
        updated_fields.append("is_active")

    # Update is_default
    if args.is_default is not None:
        is_default = int(args.is_default)
        if is_default not in (0, 1):
            err("--is-default must be 0 or 1")
        if is_default:
            # Unset previous defaults for this item+company
            bom_t2 = Table("bom")
            unset_def_q = (Q.update(bom_t2)
                           .set(bom_t2.is_default, 0)
                           .set(bom_t2.updated_at, LiteralValue("datetime('now')"))
                           .where(bom_t2.item_id == P())
                           .where(bom_t2.company_id == P())
                           .where(bom_t2.is_default == 1)
                           .where(bom_t2.id != P()))
            conn.execute(unset_def_q.get_sql(), (item_id, company_id, args.bom_id))
        updates.append("is_default = ?")
        params.append(is_default)
        updated_fields.append("is_default")

    # Update routing
    if args.routing_id is not None:
        if args.routing_id == "":
            # Clear routing
            updates.append("routing_id = NULL")
            updated_fields.append("routing_id")
        else:
            rt_t2 = Table("routing")
            rt_chk_q = Q.from_(rt_t2).select(rt_t2.id).where(rt_t2.id == P())
            routing = conn.execute(rt_chk_q.get_sql(), (args.routing_id,)).fetchone()
            if not routing:
                err(f"Routing {args.routing_id} not found")
            updates.append("routing_id = ?")
            params.append(args.routing_id)
            updated_fields.append("routing_id")

    # Replace items if provided
    new_raw_material_cost = None
    if args.items is not None:
        items = _parse_json_arg(args.items, "items")
        if not items or not isinstance(items, list):
            err("--items must be a non-empty JSON array")

        # Validate all new items before deleting old ones
        new_bom_items = []
        for i, item in enumerate(items):
            rm_item_id = item.get("item_id")
            if not rm_item_id:
                err(f"Item {i}: item_id is required")
            _validate_item_exists(conn, rm_item_id, f"Item {i}: raw material item")

            rm_qty = to_decimal(item.get("quantity", "0"))
            if rm_qty <= 0:
                err(f"Item {i}: quantity must be > 0")

            rm_rate = to_decimal(item.get("rate", "0"))
            if rm_rate < 0:
                err(f"Item {i}: rate must be >= 0")

            rm_amount = round_currency(rm_qty * rm_rate)
            is_sub_assembly = int(item.get("is_sub_assembly", 0))
            sub_bom_id = item.get("sub_bom_id")
            source_warehouse_id = item.get("source_warehouse_id")

            if is_sub_assembly and sub_bom_id:
                bom_t3 = Table("bom")
                sb_q = Q.from_(bom_t3).select(bom_t3.id, bom_t3.item_id).where(bom_t3.id == P())
                sub_bom = conn.execute(sb_q.get_sql(), (sub_bom_id,)).fetchone()
                if not sub_bom:
                    err(f"Item {i}: sub_bom_id {sub_bom_id} not found")
                if sub_bom["item_id"] != rm_item_id:
                    err(
                        f"Item {i}: sub_bom_id {sub_bom_id} produces item "
                        f"{sub_bom['item_id']}, but item_id is {rm_item_id}"
                    )

            if source_warehouse_id:
                _validate_warehouse_exists(
                    conn, source_warehouse_id, f"Item {i}: source warehouse",
                )

            new_bom_items.append({
                "id": str(uuid.uuid4()),
                "item_id": rm_item_id,
                "quantity": str(round_currency(rm_qty)),
                "uom": item.get("uom"),
                "rate": str(round_currency(rm_rate)),
                "amount": str(rm_amount),
                "source_warehouse_id": source_warehouse_id,
                "is_sub_assembly": is_sub_assembly,
                "sub_bom_id": sub_bom_id,
                "scrap_percentage": str(to_decimal(item.get("scrap_percentage", "0"))),
            })

        # Delete old items and insert new ones
        bi_t2 = Table("bom_item")
        del_bi_q = Q.from_(bi_t2).delete().where(bi_t2.bom_id == P())
        conn.execute(del_bi_q.get_sql(), (args.bom_id,))
        bi_ins_q2 = (Q.into(bi_t2).columns(
            "id", "bom_id", "item_id", "quantity", "uom", "rate", "amount",
            "source_warehouse_id", "is_sub_assembly", "sub_bom_id", "scrap_percentage"
        ).insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
        bi_ins_sql2 = bi_ins_q2.get_sql()
        for row in new_bom_items:
            conn.execute(
                bi_ins_sql2,
                (row["id"], args.bom_id, row["item_id"], row["quantity"],
                 row["uom"], row["rate"], row["amount"],
                 row["source_warehouse_id"], row["is_sub_assembly"],
                 row["sub_bom_id"], row["scrap_percentage"]),
            )

        # Recalculate raw material cost
        new_raw_material_cost = Decimal("0")
        for row in new_bom_items:
            new_raw_material_cost += to_decimal(row["amount"])
        new_raw_material_cost = round_currency(new_raw_material_cost)
        updated_fields.append("items")
        recalculate_costs = True

    # Replace operations if provided
    new_operating_cost = None
    if args.operations is not None:
        operations = _parse_json_arg(args.operations, "operations")

        # Delete old operations
        bo_t2 = Table("bom_operation")
        del_bo_q = Q.from_(bo_t2).delete().where(bo_t2.bom_id == P())
        conn.execute(del_bo_q.get_sql(), (args.bom_id,))

        if operations and isinstance(operations, list):
            for i, op in enumerate(operations):
                op_id_ref = op.get("operation_id")
                if not op_id_ref:
                    err(f"Operation {i}: operation_id is required")
                _validate_operation_exists(conn, op_id_ref)

                ws_id = op.get("workstation_id")
                if ws_id:
                    _validate_workstation_exists(conn, ws_id)

                # Calculate operating cost if not provided
                op_cost = to_decimal(op.get("operating_cost", "0"))
                if op_cost <= 0 and ws_id:
                    ws_t3 = Table("workstation")
                    ws_cost_q3 = Q.from_(ws_t3).select(ws_t3.operating_cost_per_hour).where(ws_t3.id == P())
                    ws = conn.execute(ws_cost_q3.get_sql(), (ws_id,)).fetchone()
                    if ws:
                        time_mins = to_decimal(op.get("time_in_minutes", "0"))
                        op_cost = round_currency(
                            (time_mins / Decimal("60"))
                            * to_decimal(ws["operating_cost_per_hour"])
                        )

                bo_ins_q2 = (Q.into(bo_t2).columns(
                    "id", "bom_id", "operation_id", "workstation_id",
                    "time_in_minutes", "operating_cost", "sequence", "description"
                ).insert(P(), P(), P(), P(), P(), P(), P(), P()))
                conn.execute(
                    bo_ins_q2.get_sql(),
                    (str(uuid.uuid4()), args.bom_id, op_id_ref, ws_id,
                     op.get("time_in_minutes", "0"),
                     str(round_currency(op_cost)),
                     op.get("sequence", i + 1),
                     op.get("description")),
                )

            updates.append("with_operations = 1")
            # Calculate new operating cost
            new_operating_cost = Decimal("0")
            bo_cost_q = Q.from_(bo_t2).select(bo_t2.operating_cost).where(bo_t2.bom_id == P())
            op_rows = conn.execute(bo_cost_q.get_sql(), (args.bom_id,)).fetchall()
            for op_row in op_rows:
                new_operating_cost += to_decimal(op_row["operating_cost"])
            new_operating_cost = round_currency(new_operating_cost)
        else:
            # Empty operations list: clear operations
            updates.append("with_operations = 0")
            new_operating_cost = Decimal("0")

        updated_fields.append("operations")
        recalculate_costs = True

    # Recalculate costs if needed
    if recalculate_costs:
        # Get current costs if not being replaced
        if new_raw_material_cost is None:
            new_raw_material_cost = to_decimal(bom_dict["raw_material_cost"])
        if new_operating_cost is None:
            new_operating_cost = to_decimal(bom_dict["operating_cost"])

        total_cost = round_currency(new_raw_material_cost + new_operating_cost)

        updates.append("raw_material_cost = ?")
        params.append(str(new_raw_material_cost))
        updates.append("operating_cost = ?")
        params.append(str(new_operating_cost))
        updates.append("total_cost = ?")
        params.append(str(total_cost))

    if not updated_fields:
        err("No fields to update")

    # raw SQL — dynamic column list built at runtime
    updates.append("updated_at = datetime('now')")
    params.append(args.bom_id)
    conn.execute(
        f"UPDATE bom SET {', '.join(updates)} WHERE id = ?", params,
    )

    audit(conn, "erpclaw-manufacturing", "update-bom", "bom", args.bom_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()

    # Fetch updated BOM for response
    bom_t4 = Table("bom")
    upd_bom_q = Q.from_(bom_t4).select(bom_t4.star).where(bom_t4.id == P())
    updated_bom = conn.execute(upd_bom_q.get_sql(), (args.bom_id,)).fetchone()
    updated_dict = row_to_dict(updated_bom)

    ok({
        "bom_id": args.bom_id,
        "updated_fields": updated_fields,
        "raw_material_cost": updated_dict["raw_material_cost"],
        "operating_cost": updated_dict["operating_cost"],
        "total_cost": updated_dict["total_cost"],
    })


# ---------------------------------------------------------------------------
# 3. get-bom
# ---------------------------------------------------------------------------

def get_bom(conn, args):
    """Get BOM with items and operations.

    Required: --bom-id
    Returns: BOM header + items list + operations list
    """
    if not args.bom_id:
        err("--bom-id is required")

    bom_t = Table("bom")
    bom_q = Q.from_(bom_t).select(bom_t.star).where(bom_t.id == P())
    bom = conn.execute(bom_q.get_sql(), (args.bom_id,)).fetchone()
    if not bom:
        err(f"BOM {args.bom_id} not found")

    data = row_to_dict(bom)

    # Fetch finished goods item details
    item_t = Table("item")
    fg_q = Q.from_(item_t).select(item_t.item_code, item_t.item_name, item_t.stock_uom).where(item_t.id == P())
    fg_item = conn.execute(fg_q.get_sql(), (data["item_id"],)).fetchone()
    if fg_item:
        fg_dict = row_to_dict(fg_item)
        data["item_code"] = fg_dict.get("item_code")
        data["item_name"] = fg_dict.get("item_name")
        data["stock_uom"] = fg_dict.get("stock_uom")

    # Fetch BOM items with item details
    bi = Table("bom_item").as_("bi")
    i = Table("item").as_("i")
    bi_q = (Q.from_(bi)
            .left_join(i).on(i.id == bi.item_id)
            .select(bi.star, i.item_code, i.item_name, i.field("stock_uom").as_("item_uom"))
            .where(bi.bom_id == P())
            .orderby(bi.rowid))
    items = conn.execute(bi_q.get_sql(), (args.bom_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    # Fetch BOM operations with operation and workstation details
    bo = Table("bom_operation").as_("bo")
    o = Table("operation").as_("o")
    w = Table("workstation").as_("w")
    bo_q = (Q.from_(bo)
            .left_join(o).on(o.id == bo.operation_id)
            .left_join(w).on(w.id == bo.workstation_id)
            .select(bo.star,
                    o.name.as_("operation_name"),
                    w.name.as_("workstation_name"),
                    w.operating_cost_per_hour.as_("ws_hour_rate"))
            .where(bo.bom_id == P())
            .orderby(bo.sequence, bo.rowid))
    operations = conn.execute(bo_q.get_sql(), (args.bom_id,)).fetchall()
    data["operations"] = [row_to_dict(r) for r in operations]

    ok(data)


# ---------------------------------------------------------------------------
# 4. list-boms
# ---------------------------------------------------------------------------

def list_boms(conn, args):
    """Query BOMs with filtering.

    Optional: --item-id, --is-active, --company-id, --is-default,
              --search, --limit (20), --offset (0)
    """
    b = Table("bom").as_("b")
    i = Table("item").as_("i")

    # Build count query
    count_q = Q.from_(b).left_join(i).on(i.id == b.item_id).select(fn.Count("*"))
    count_params = []

    if args.item_id:
        count_q = count_q.where(b.item_id == P())
        count_params.append(args.item_id)
    if args.is_active is not None:
        count_q = count_q.where(b.is_active == P())
        count_params.append(int(args.is_active))
    if args.company_id:
        count_q = count_q.where(b.company_id == P())
        count_params.append(args.company_id)
    if args.is_default is not None:
        count_q = count_q.where(b.is_default == P())
        count_params.append(int(args.is_default))
    if args.search:
        count_q = count_q.where(
            (i.item_name.like(P())) | (i.item_code.like(P())) | (b.naming_series.like(P()))
        )
        count_params.extend([f"%{args.search}%", f"%{args.search}%", f"%{args.search}%"])

    count_row = conn.execute(count_q.get_sql(), count_params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    # Build rows query
    rows_q = (Q.from_(b).left_join(i).on(i.id == b.item_id)
              .select(b.id, b.naming_series, b.item_id, b.quantity, b.is_active,
                      b.is_default, b.raw_material_cost, b.operating_cost,
                      b.total_cost, b.with_operations, b.company_id,
                      i.item_code, i.item_name)
              .orderby(b.created_at, order=Order.desc)
              .limit(P()).offset(P()))

    row_params = []
    if args.item_id:
        rows_q = rows_q.where(b.item_id == P())
        row_params.append(args.item_id)
    if args.is_active is not None:
        rows_q = rows_q.where(b.is_active == P())
        row_params.append(int(args.is_active))
    if args.company_id:
        rows_q = rows_q.where(b.company_id == P())
        row_params.append(args.company_id)
    if args.is_default is not None:
        rows_q = rows_q.where(b.is_default == P())
        row_params.append(int(args.is_default))
    if args.search:
        rows_q = rows_q.where(
            (i.item_name.like(P())) | (i.item_code.like(P())) | (b.naming_series.like(P()))
        )
        row_params.extend([f"%{args.search}%", f"%{args.search}%", f"%{args.search}%"])
    row_params.extend([limit, offset])

    rows = conn.execute(rows_q.get_sql(), row_params).fetchall()

    ok({"boms": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 5. explode-bom
# ---------------------------------------------------------------------------

def explode_bom(conn, args):
    """Recursive multi-level BOM explosion.

    Required: --bom-id, --quantity (how many FG units to produce)
    Returns: flat list of leaf raw materials with total required quantities

    Logic:
    1. Fetch BOM + items
    2. For each item: if is_sub_assembly and sub_bom_id -> recurse into sub-BOM
    3. Otherwise add to flat list with scaled quantity
    4. Limit recursion depth to 10; detect circular references
    5. Return flat list of leaf raw materials with total required quantities
    """
    if not args.bom_id:
        err("--bom-id is required")

    requested_qty = to_decimal(args.quantity or "1")
    if requested_qty <= 0:
        err("--quantity must be greater than 0")

    bom = _validate_bom_exists(conn, args.bom_id)
    bom_dict = row_to_dict(bom)

    # Track visited BOMs for circular reference detection
    visited = set()

    # Accumulate leaf materials: {item_id: {"item_id", "item_code", "item_name", "uom", "total_qty"}}
    leaf_materials = {}

    def _explode_recursive(bom_id: str, parent_qty: Decimal, depth: int):
        """Recursively explode a BOM, accumulating leaf materials."""
        if depth > MAX_BOM_EXPLOSION_DEPTH:
            err(
                f"BOM explosion exceeded maximum depth of {MAX_BOM_EXPLOSION_DEPTH}. "
                f"Check for overly nested sub-assemblies."
            )

        if bom_id in visited:
            err(
                f"Circular reference detected: BOM {bom_id} appears in its own "
                f"sub-assembly chain. Fix the BOM structure to remove the cycle."
            )

        visited.add(bom_id)

        # Fetch the BOM header for its quantity (yield per BOM)
        bom_hdr_t = Table("bom")
        bom_hdr_q = Q.from_(bom_hdr_t).select(bom_hdr_t.quantity).where(bom_hdr_t.id == P())
        current_bom = conn.execute(bom_hdr_q.get_sql(), (bom_id,)).fetchone()
        if not current_bom:
            err(f"BOM {bom_id} not found during explosion")

        bom_base_qty = to_decimal(current_bom["quantity"])
        if bom_base_qty <= 0:
            err(f"BOM {bom_id} has invalid quantity: {bom_base_qty}")

        # Fetch BOM items
        bi_t = Table("bom_item").as_("bi")
        it_t = Table("item").as_("i")
        bi_exp_q = (Q.from_(bi_t)
                    .left_join(it_t).on(it_t.id == bi_t.item_id)
                    .select(bi_t.star, it_t.item_code, it_t.item_name, it_t.stock_uom)
                    .where(bi_t.bom_id == P()))
        bom_items = conn.execute(bi_exp_q.get_sql(), (bom_id,)).fetchall()

        for bi_row in bom_items:
            bi = row_to_dict(bi_row)
            item_qty = to_decimal(bi["quantity"])

            # Scale quantity: (item.qty / bom.qty) * parent_qty
            scaled_qty = round_currency((item_qty / bom_base_qty) * parent_qty)

            # Apply scrap percentage: effective_qty = scaled_qty * (1 + scrap% / 100)
            scrap_pct = to_decimal(bi.get("scrap_percentage", "0"))
            if scrap_pct > 0:
                scaled_qty = round_currency(
                    scaled_qty * (Decimal("1") + scrap_pct / Decimal("100"))
                )

            if bi.get("is_sub_assembly") and bi.get("sub_bom_id"):
                # Recurse into sub-assembly BOM
                _explode_recursive(bi["sub_bom_id"], scaled_qty, depth + 1)
            else:
                # Leaf material: accumulate
                rm_item_id = bi["item_id"]
                if rm_item_id in leaf_materials:
                    leaf_materials[rm_item_id]["total_qty"] = round_currency(
                        to_decimal(leaf_materials[rm_item_id]["total_qty"]) + scaled_qty
                    )
                else:
                    leaf_materials[rm_item_id] = {
                        "item_id": rm_item_id,
                        "item_code": bi.get("item_code", ""),
                        "item_name": bi.get("item_name", ""),
                        "uom": bi.get("stock_uom") or bi.get("uom", ""),
                        "total_qty": round_currency(scaled_qty),
                    }

        # Remove from visited after processing to allow same BOM in
        # different branches (sibling sub-assemblies using the same BOM)
        visited.discard(bom_id)

    # Start explosion from the root BOM
    _explode_recursive(args.bom_id, requested_qty, depth=0)

    # Convert to list, sorted by item_code for consistent output
    materials_list = sorted(
        [
            {
                "item_id": mat["item_id"],
                "item_code": mat["item_code"],
                "item_name": mat["item_name"],
                "uom": mat["uom"],
                "total_qty": str(mat["total_qty"]),
            }
            for mat in leaf_materials.values()
        ],
        key=lambda x: x.get("item_code", ""),
    )

    ok({
        "bom_id": args.bom_id,
        "fg_item_id": bom_dict["item_id"],
        "requested_qty": str(round_currency(requested_qty)),
        "materials": materials_list,
        "material_count": len(materials_list),
    })


# ---------------------------------------------------------------------------
# 6. add-operation
# ---------------------------------------------------------------------------

def add_operation(conn, args):
    """Create a manufacturing operation.

    Required: --name
    Optional: --workstation-id, --description
    """
    if not args.name:
        err("--name is required")

    # Check uniqueness
    op_t = Table("operation")
    op_chk_q = Q.from_(op_t).select(op_t.id).where(op_t.name == P())
    existing = conn.execute(op_chk_q.get_sql(), (args.name,)).fetchone()
    if existing:
        err(f"Operation '{args.name}' already exists")

    # Validate workstation if provided
    ws_id = args.workstation_id
    if ws_id:
        _validate_workstation_exists(conn, ws_id)

    op_id = str(uuid.uuid4())
    op_ins_q = (Q.into(op_t).columns(
        "id", "name", "description", "default_workstation_id", "is_active"
    ).insert(P(), P(), P(), P(), 1))
    try:
        conn.execute(op_ins_q.get_sql(), (op_id, args.name, args.description, ws_id))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("Operation creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-manufacturing", "add-operation", "operation", op_id,
           new_values={"name": args.name, "workstation_id": ws_id})
    conn.commit()
    ok({"operation_id": op_id, "name": args.name})


# ---------------------------------------------------------------------------
# 7. add-workstation
# ---------------------------------------------------------------------------

def add_workstation(conn, args):
    """Create a workstation.

    Required: --name
    Optional: --workstation-type, --hour-rate (operating_cost_per_hour),
              --working-hours-per-day, --production-capacity,
              --holiday-list-id, --description
    """
    if not args.name:
        err("--name is required")

    ws_t = Table("workstation")
    ws_chk_q = Q.from_(ws_t).select(ws_t.id).where(ws_t.name == P())
    existing = conn.execute(ws_chk_q.get_sql(), (args.name,)).fetchone()
    if existing:
        err(f"Workstation '{args.name}' already exists")

    hour_rate = str(round_currency(to_decimal(args.hour_rate or "0")))
    working_hours = args.working_hours_per_day

    # Validate holiday list if provided
    if args.holiday_list_id:
        hl_t = Table("holiday_list")
        hl_q = Q.from_(hl_t).select(hl_t.id).where(hl_t.id == P())
        hl = conn.execute(hl_q.get_sql(), (args.holiday_list_id,)).fetchone()
        if not hl:
            err(f"Holiday list {args.holiday_list_id} not found")

    ws_id = str(uuid.uuid4())
    ws_ins_q = (Q.into(ws_t).columns(
        "id", "name", "workstation_type", "production_capacity",
        "operating_cost_per_hour", "working_hours_per_day",
        "holiday_list_id", "status", "description"
    ).insert(P(), P(), P(), P(), P(), P(), P(), ValueWrapper("active"), P()))
    try:
        conn.execute(
            ws_ins_q.get_sql(),
            (ws_id, args.name, args.workstation_type,
             args.production_capacity, hour_rate,
             working_hours, args.holiday_list_id,
             args.description),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("Workstation creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-manufacturing", "add-workstation", "workstation", ws_id,
           new_values={"name": args.name, "hour_rate": hour_rate})
    conn.commit()
    ok({"workstation_id": ws_id, "name": args.name,
         "operating_cost_per_hour": hour_rate})


# ---------------------------------------------------------------------------
# 8. add-routing
# ---------------------------------------------------------------------------

def add_routing(conn, args):
    """Create a routing with operations.

    Required: --name, --operations (JSON array)
    Optional: --description

    Operations JSON format:
    [
        {
            "operation_id": "...",
            "workstation_id": "..." (optional),
            "sequence": 1 (optional, defaults to position),
            "time_in_minutes": "30",
            "operating_cost": "0" (optional, calculated from workstation if omitted)
        }
    ]
    """
    if not args.name:
        err("--name is required")
    if not args.operations:
        err("--operations (JSON) is required")

    rt_t = Table("routing")
    rt_chk_q = Q.from_(rt_t).select(rt_t.id).where(rt_t.name == P())
    existing = conn.execute(rt_chk_q.get_sql(), (args.name,)).fetchone()
    if existing:
        err(f"Routing '{args.name}' already exists")

    operations = _parse_json_arg(args.operations, "operations")
    if not operations or not isinstance(operations, list):
        err("--operations must be a non-empty JSON array")

    routing_id = str(uuid.uuid4())

    rt_ins_q = Q.into(rt_t).columns("id", "name", "description").insert(P(), P(), P())
    try:
        conn.execute(rt_ins_q.get_sql(), (routing_id, args.name, args.description))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("Routing creation failed — check for duplicates or invalid data")

    for i, op in enumerate(operations):
        op_id_ref = op.get("operation_id")
        if not op_id_ref:
            err(f"Operation {i}: operation_id is required")

        _validate_operation_exists(conn, op_id_ref)

        ws_id = op.get("workstation_id")
        if ws_id:
            _validate_workstation_exists(conn, ws_id)

        # Calculate operating cost if not explicitly provided
        op_cost = to_decimal(op.get("operating_cost", "0"))
        if op_cost <= 0 and ws_id:
            ws_t2 = Table("workstation")
            ws_cost_q = Q.from_(ws_t2).select(ws_t2.operating_cost_per_hour).where(ws_t2.id == P())
            ws = conn.execute(ws_cost_q.get_sql(), (ws_id,)).fetchone()
            if ws:
                time_mins = to_decimal(op.get("time_in_minutes", "0"))
                op_cost = round_currency(
                    (time_mins / Decimal("60"))
                    * to_decimal(ws["operating_cost_per_hour"])
                )

        ro_id = str(uuid.uuid4())
        ro_t = Table("routing_operation")
        ro_ins_q = (Q.into(ro_t).columns(
            "id", "routing_id", "operation_id", "workstation_id",
            "sequence", "time_in_minutes", "operating_cost"
        ).insert(P(), P(), P(), P(), P(), P(), P()))
        conn.execute(
            ro_ins_q.get_sql(),
            (ro_id, routing_id, op_id_ref, ws_id,
             op.get("sequence", i + 1),
             op.get("time_in_minutes", "0"),
             str(round_currency(op_cost))),
        )

    audit(conn, "erpclaw-manufacturing", "add-routing", "routing", routing_id,
           new_values={"name": args.name, "operations_count": len(operations)})
    conn.commit()
    ok({
        "routing_id": routing_id,
        "name": args.name,
        "operations_count": len(operations),
    })


# ---------------------------------------------------------------------------
# 9. add-work-order
# ---------------------------------------------------------------------------

def add_work_order(conn, args):
    """Create a Work Order from a BOM.

    Required: --bom-id, --quantity, --company-id
    Optional: --planned-start-date, --planned-end-date,
              --source-warehouse-id, --target-warehouse-id, --wip-warehouse-id,
              --sales-order-id
    """
    if not args.bom_id:
        err("--bom-id is required")
    if not args.quantity:
        err("--quantity is required")
    if not args.company_id:
        err("--company-id is required")

    qty = to_decimal(args.quantity)
    if qty <= 0:
        err("--quantity must be greater than 0")

    # Validate BOM exists and is active
    bom = _validate_bom_exists(conn, args.bom_id)
    bom_dict = row_to_dict(bom)
    if not bom_dict.get("is_active"):
        err(f"BOM {args.bom_id} is not active")

    # The FG item comes from the BOM
    fg_item_id = bom_dict["item_id"]

    # Validate company
    _validate_company_exists(conn, args.company_id)

    # Validate warehouses if provided
    source_wh = args.source_warehouse_id
    target_wh = args.target_warehouse_id
    wip_wh = args.wip_warehouse_id
    if source_wh:
        _validate_warehouse_exists(conn, source_wh, "Source warehouse")
    if target_wh:
        _validate_warehouse_exists(conn, target_wh, "Target warehouse")
    if wip_wh:
        _validate_warehouse_exists(conn, wip_wh, "WIP warehouse")

    # Generate naming series
    naming = get_next_name(conn, "work_order", company_id=args.company_id)

    wo_id = str(uuid.uuid4())
    wo_t = Table("work_order")
    wo_ins_q = (Q.into(wo_t).columns(
        "id", "naming_series", "item_id", "bom_id", "qty", "produced_qty",
        "planned_start_date", "planned_end_date",
        "source_warehouse_id", "target_warehouse_id", "wip_warehouse_id",
        "sales_order_id", "status", "material_transferred_for_manufacturing",
        "company_id"
    ).insert(P(), P(), P(), P(), P(), ValueWrapper("0"), P(), P(), P(), P(), P(),
             P(), ValueWrapper("draft"), ValueWrapper("0"), P()))
    try:
        conn.execute(
            wo_ins_q.get_sql(),
            (wo_id, naming, fg_item_id, args.bom_id, str(round_currency(qty)),
             args.planned_start_date, args.planned_end_date,
             source_wh, target_wh, wip_wh,
             args.sales_order_id, args.company_id),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("Work order creation failed — check for duplicates or invalid data")

    # Copy BOM items to work_order_item with scaled quantities
    bom_qty = to_decimal(bom_dict["quantity"])
    if bom_qty <= 0:
        bom_qty = Decimal("1")

    bi_t2 = Table("bom_item").as_("bi")
    bi_fetch_q = (Q.from_(bi_t2)
                  .select(bi_t2.item_id, bi_t2.quantity, bi_t2.source_warehouse_id)
                  .where(bi_t2.bom_id == P()))
    bom_items = conn.execute(bi_fetch_q.get_sql(), (args.bom_id,)).fetchall()

    woi_t = Table("work_order_item")
    woi_ins_q = (Q.into(woi_t).columns(
        "id", "work_order_id", "item_id", "required_qty", "transferred_qty",
        "consumed_qty", "source_warehouse_id"
    ).insert(P(), P(), P(), P(), ValueWrapper("0"), ValueWrapper("0"), P()))
    woi_ins_sql = woi_ins_q.get_sql()
    for bi_row in bom_items:
        bi = row_to_dict(bi_row)
        bi_qty = to_decimal(bi["quantity"])
        required_qty = round_currency((bi_qty / bom_qty) * qty)
        woi_source_wh = bi.get("source_warehouse_id") or source_wh

        conn.execute(
            woi_ins_sql,
            (str(uuid.uuid4()), wo_id, bi["item_id"],
             str(required_qty), woi_source_wh),
        )

    audit(conn, "erpclaw-manufacturing", "add-work-order", "work_order", wo_id,
           new_values={
               "naming_series": naming, "item_id": fg_item_id,
               "bom_id": args.bom_id, "qty": str(round_currency(qty)),
           })
    conn.commit()

    ok({
        "work_order_id": wo_id,
        "naming_series": naming,
        "item_id": fg_item_id,
        "bom_id": args.bom_id,
        "qty": str(round_currency(qty)),
        "status": "draft",
        "item_count": len(bom_items),
    })


# ---------------------------------------------------------------------------
# 10. get-work-order
# ---------------------------------------------------------------------------

def get_work_order(conn, args):
    """Get work order with items and job cards.

    Required: --work-order-id
    Returns: WO dict + items list (with item names) + job cards list
    """
    if not args.work_order_id:
        err("--work-order-id is required")

    wo_t = Table("work_order")
    wo_q = Q.from_(wo_t).select(wo_t.star).where(wo_t.id == P())
    wo = conn.execute(wo_q.get_sql(), (args.work_order_id,)).fetchone()
    if not wo:
        err(f"Work Order {args.work_order_id} not found")

    data = row_to_dict(wo)

    # Fetch item name for the finished good
    item_t = Table("item")
    fg_q = Q.from_(item_t).select(item_t.item_code, item_t.item_name).where(item_t.id == P())
    fg_item = conn.execute(fg_q.get_sql(), (data["item_id"],)).fetchone()
    if fg_item:
        fg_dict = row_to_dict(fg_item)
        data["item_code"] = fg_dict.get("item_code")
        data["item_name"] = fg_dict.get("item_name")

    # Fetch BOM naming_series
    bom_t = Table("bom")
    bom_ns_q = Q.from_(bom_t).select(bom_t.naming_series).where(bom_t.id == P())
    bom_row = conn.execute(bom_ns_q.get_sql(), (data["bom_id"],)).fetchone()
    if bom_row:
        data["bom_naming_series"] = bom_row["naming_series"]

    # Fetch work order items with item details
    woi = Table("work_order_item").as_("woi")
    i = Table("item").as_("i")
    woi_q = (Q.from_(woi)
             .left_join(i).on(i.id == woi.item_id)
             .select(woi.star, i.item_code, i.item_name, i.stock_uom)
             .where(woi.work_order_id == P())
             .orderby(woi.rowid))
    items = conn.execute(woi_q.get_sql(), (args.work_order_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    # Fetch job cards
    jc = Table("job_card").as_("jc")
    o = Table("operation").as_("o")
    w = Table("workstation").as_("w")
    jc_q = (Q.from_(jc)
            .left_join(o).on(o.id == jc.operation_id)
            .left_join(w).on(w.id == jc.workstation_id)
            .select(jc.star, o.name.as_("operation_name"), w.name.as_("workstation_name"))
            .where(jc.work_order_id == P())
            .orderby(jc.created_at))
    job_cards = conn.execute(jc_q.get_sql(), (args.work_order_id,)).fetchall()
    data["job_cards"] = [row_to_dict(r) for r in job_cards]

    ok(data)


# ---------------------------------------------------------------------------
# 11. list-work-orders
# ---------------------------------------------------------------------------

def list_work_orders(conn, args):
    """Query work orders with filtering.

    Optional: --company-id, --status, --from-date, --to-date, --item-id,
              --limit (20), --offset (0)
    """
    wo = Table("work_order").as_("wo")
    i = Table("item").as_("i")

    count_q = Q.from_(wo).left_join(i).on(i.id == wo.item_id).select(fn.Count("*"))
    count_params = []

    if args.company_id:
        count_q = count_q.where(wo.company_id == P())
        count_params.append(args.company_id)
    if args.status:
        if args.status not in VALID_WO_STATUSES:
            err(f"Invalid status '{args.status}'. Valid: {VALID_WO_STATUSES}")
        count_q = count_q.where(wo.status == P())
        count_params.append(args.status)
    if args.from_date:
        count_q = count_q.where(wo.created_at >= P())
        count_params.append(args.from_date)
    if args.to_date:
        count_q = count_q.where(wo.created_at <= P())
        count_params.append(args.to_date + " 23:59:59")
    if args.item_id:
        count_q = count_q.where(wo.item_id == P())
        count_params.append(args.item_id)

    count_row = conn.execute(count_q.get_sql(), count_params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    rows_q = (Q.from_(wo).left_join(i).on(i.id == wo.item_id)
              .select(wo.id, wo.naming_series, wo.item_id, wo.bom_id,
                      wo.qty, wo.produced_qty, wo.status, wo.company_id,
                      wo.planned_start_date, wo.actual_start_date,
                      wo.actual_end_date, wo.material_transferred_for_manufacturing,
                      i.item_code, i.item_name)
              .orderby(wo.created_at, order=Order.desc)
              .limit(P()).offset(P()))

    row_params = []
    if args.company_id:
        rows_q = rows_q.where(wo.company_id == P())
        row_params.append(args.company_id)
    if args.status:
        rows_q = rows_q.where(wo.status == P())
        row_params.append(args.status)
    if args.from_date:
        rows_q = rows_q.where(wo.created_at >= P())
        row_params.append(args.from_date)
    if args.to_date:
        rows_q = rows_q.where(wo.created_at <= P())
        row_params.append(args.to_date + " 23:59:59")
    if args.item_id:
        rows_q = rows_q.where(wo.item_id == P())
        row_params.append(args.item_id)
    row_params.extend([limit, offset])

    rows = conn.execute(rows_q.get_sql(), row_params).fetchall()

    ok({"work_orders": [row_to_dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 12. start-work-order
# ---------------------------------------------------------------------------

def start_work_order(conn, args):
    """Start a work order (draft -> not_started).

    Required: --work-order-id
    """
    if not args.work_order_id:
        err("--work-order-id is required")

    wo_t = Table("work_order")
    wo_q = Q.from_(wo_t).select(wo_t.star).where(wo_t.id == P())
    wo = conn.execute(wo_q.get_sql(), (args.work_order_id,)).fetchone()
    if not wo:
        err(f"Work Order {args.work_order_id} not found")

    wo_dict = row_to_dict(wo)
    if wo_dict["status"] != "draft":
        err(
            f"Cannot start Work Order with status '{wo_dict['status']}'. "
            f"Only 'draft' work orders can be started."
        )

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    wo_start_q = (Q.update(wo_t)
                  .set(wo_t.status, ValueWrapper("in_process"))
                  .set(wo_t.actual_start_date, P())
                  .set(wo_t.updated_at, LiteralValue("datetime('now')"))
                  .where(wo_t.id == P()))
    conn.execute(wo_start_q.get_sql(), (now_str, args.work_order_id))

    audit(conn, "erpclaw-manufacturing", "start-work-order", "work_order", args.work_order_id,
           old_values={"status": "draft"},
           new_values={"status": "in_process", "actual_start_date": now_str})
    conn.commit()

    ok({
        "work_order_id": args.work_order_id,
        "status": "in_process",
        "actual_start_date": now_str,
    })


# ---------------------------------------------------------------------------
# 13. transfer-materials
# ---------------------------------------------------------------------------

def transfer_materials(conn, args):
    """Transfer materials from source to WIP warehouse for a work order.

    Required: --work-order-id, --items (JSON: [{item_id, qty, warehouse_id?}])
    Optional: --posting-date (defaults to today)

    Creates SLE entries (OUT of source, IN to WIP) and perpetual GL entries
    in a single transaction.
    """
    if not args.work_order_id:
        err("--work-order-id is required")
    if not args.items:
        err("--items is required (JSON array)")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    # Validate work order
    wo_t = Table("work_order")
    wo_q = Q.from_(wo_t).select(wo_t.star).where(wo_t.id == P())
    wo = conn.execute(wo_q.get_sql(), (args.work_order_id,)).fetchone()
    if not wo:
        err(f"Work Order {args.work_order_id} not found")

    wo_dict = row_to_dict(wo)
    if wo_dict["status"] not in ("not_started", "in_process"):
        err(
            f"Cannot transfer materials for Work Order with status "
            f"'{wo_dict['status']}'. Must be 'not_started' or 'in_process'."
        )

    source_wh = wo_dict.get("source_warehouse_id")
    wip_wh = wo_dict.get("wip_warehouse_id")
    if not wip_wh:
        err("Work Order has no WIP warehouse set. Set --wip-warehouse-id when creating the work order.")

    company_id = wo_dict["company_id"]
    posting_date = args.posting_date or datetime.now().strftime("%Y-%m-%d")

    # Get fiscal year for SLE
    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, company_id)

    # Fetch work order items for validation
    woi_t = Table("work_order_item")
    woi_q = Q.from_(woi_t).select(woi_t.star).where(woi_t.work_order_id == P())
    wo_items = conn.execute(woi_q.get_sql(), (args.work_order_id,)).fetchall()
    wo_item_map = {}
    for woi_row in wo_items:
        woi = row_to_dict(woi_row)
        wo_item_map[woi["item_id"]] = woi

    # Build SLE entries
    sle_entries = []
    transfer_updates = []  # (item_id, transfer_qty) tuples

    for i, item in enumerate(items):
        item_id = item.get("item_id")
        if not item_id:
            err(f"Transfer item {i}: item_id is required")

        transfer_qty = to_decimal(item.get("qty", "0"))
        if transfer_qty <= 0:
            err(f"Transfer item {i}: qty must be > 0")

        # Validate item is in the work order
        if item_id not in wo_item_map:
            err(f"Transfer item {i}: item {item_id} is not in this work order")

        woi = wo_item_map[item_id]
        required = to_decimal(woi["required_qty"])
        already_transferred = to_decimal(woi["transferred_qty"])
        if already_transferred + transfer_qty > required:
            err(
                f"Transfer item {i}: transferring {transfer_qty} would exceed "
                f"required qty. Required: {required}, already transferred: "
                f"{already_transferred}"
            )

        # Determine source warehouse for this item
        item_source_wh = item.get("warehouse_id") or woi.get("source_warehouse_id") or source_wh
        if not item_source_wh:
            err(
                f"Transfer item {i}: no source warehouse found. "
                f"Set source_warehouse_id on the work order or provide warehouse_id in items."
            )

        # Get valuation rate for this item at source warehouse
        try:
            val_rate = get_valuation_rate(conn, item_id, item_source_wh)
        except Exception:
            val_rate = Decimal("0")
        val_rate = to_decimal(str(val_rate)) if val_rate else Decimal("0")

        # SLE: OUT of source warehouse
        sle_entries.append({
            "item_id": item_id,
            "warehouse_id": item_source_wh,
            "actual_qty": str(round_currency(-transfer_qty)),
            "incoming_rate": "0",
            "fiscal_year": fiscal_year,
        })

        # SLE: IN to WIP warehouse
        sle_entries.append({
            "item_id": item_id,
            "warehouse_id": wip_wh,
            "actual_qty": str(round_currency(transfer_qty)),
            "incoming_rate": str(round_currency(val_rate)),
            "fiscal_year": fiscal_year,
        })

        transfer_updates.append((item_id, transfer_qty))

    # Insert SLE entries
    try:
        sle_ids = insert_sle_entries(
            conn, sle_entries,
            voucher_type="work_order",
            voucher_id=args.work_order_id,
            posting_date=posting_date,
            company_id=company_id,
        )
    except (ValueError, NotImplementedError) as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err(f"SLE posting failed: {e}")

    # Fetch inserted SLE rows for GL generation
    sle_t = Table("stock_ledger_entry")
    sle_q = (Q.from_(sle_t).select(sle_t.star)
             .where(sle_t.voucher_type == ValueWrapper("work_order"))
             .where(sle_t.voucher_id == P())
             .where(sle_t.is_cancelled == 0))
    sle_rows = conn.execute(sle_q.get_sql(), (args.work_order_id,)).fetchall()
    sle_dicts = [row_to_dict(r) for r in sle_rows]

    # Create perpetual inventory GL entries
    gl_entries = create_perpetual_inventory_gl(
        conn, sle_dicts,
        voucher_type="work_order",
        voucher_id=args.work_order_id,
        posting_date=posting_date,
        company_id=company_id,
        cost_center_id=cost_center_id,
    )

    gl_ids = []
    if gl_entries:
        if fiscal_year:
            for gle in gl_entries:
                gle["fiscal_year"] = fiscal_year
        try:
            gl_ids = insert_gl_entries(
                conn, gl_entries,
                voucher_type="work_order",
                voucher_id=args.work_order_id,
                posting_date=posting_date,
                company_id=company_id,
                remarks=f"Material Transfer for WO {wo_dict['naming_series']}",
            )
        except (ValueError, NotImplementedError) as e:
            sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
            err(f"GL posting failed: {e}")

    # Update work_order_item transferred_qty
    # raw SQL — CAST expression not well supported by PyPika
    total_material_transferred = Decimal("0")
    for item_id, transfer_qty in transfer_updates:
        conn.execute(
            """UPDATE work_order_item
               SET transferred_qty = CAST(
                   (transferred_qty + 0 + ?) AS TEXT)
               WHERE work_order_id = ? AND item_id = ?""",
            (str(round_currency(transfer_qty)), args.work_order_id, item_id),
        )
        total_material_transferred += transfer_qty

    # Update work_order.material_transferred_for_manufacturing
    current_transferred = to_decimal(wo_dict["material_transferred_for_manufacturing"])
    new_transferred = round_currency(current_transferred + total_material_transferred)
    wo_upd_q = (Q.update(wo_t)
                .set(wo_t.material_transferred_for_manufacturing, P())
                .set(wo_t.updated_at, LiteralValue("datetime('now')"))
                .where(wo_t.id == P()))
    conn.execute(wo_upd_q.get_sql(), (str(new_transferred), args.work_order_id))

    # Transition to in_process if currently not_started
    if wo_dict["status"] == "not_started":
        wo_status_q = (Q.update(wo_t)
                       .set(wo_t.status, ValueWrapper("in_process"))
                       .set(wo_t.updated_at, LiteralValue("datetime('now')"))
                       .where(wo_t.id == P()))
        conn.execute(wo_status_q.get_sql(), (args.work_order_id,))

    audit(conn, "erpclaw-manufacturing", "transfer-materials", "work_order", args.work_order_id,
           new_values={
               "items_transferred": len(transfer_updates),
               "sle_count": len(sle_ids) if sle_ids else 0,
               "gl_count": len(gl_ids),
           })
    conn.commit()

    ok({
        "work_order_id": args.work_order_id,
        "items_transferred": len(transfer_updates),
        "sle_count": len(sle_ids) if sle_ids else 0,
        "gl_count": len(gl_ids),
    })


# ---------------------------------------------------------------------------
# 14. create-job-card
# ---------------------------------------------------------------------------

def create_job_card(conn, args):
    """Create a Job Card for a work order operation.

    Required: --work-order-id, --operation-id
    Optional: --workstation-id, --for-quantity
    """
    if not args.work_order_id:
        err("--work-order-id is required")
    if not args.operation_id:
        err("--operation-id is required")

    # Validate work order
    wo_t = Table("work_order")
    wo_q = Q.from_(wo_t).select(wo_t.star).where(wo_t.id == P())
    wo = conn.execute(wo_q.get_sql(), (args.work_order_id,)).fetchone()
    if not wo:
        err(f"Work Order {args.work_order_id} not found")

    wo_dict = row_to_dict(wo)
    if wo_dict["status"] not in ("not_started", "in_process"):
        err(
            f"Cannot create Job Card for Work Order with status "
            f"'{wo_dict['status']}'. Must be 'not_started' or 'in_process'."
        )

    # Validate operation
    op = _validate_operation_exists(conn, args.operation_id)
    op_dict = row_to_dict(op)

    # Determine workstation
    ws_id = args.workstation_id
    if not ws_id:
        ws_id = op_dict.get("default_workstation_id")
    if ws_id:
        _validate_workstation_exists(conn, ws_id)

    # For quantity defaults to WO qty
    for_qty = str(round_currency(
        to_decimal(args.for_quantity or wo_dict["qty"])
    ))

    # Generate naming series
    naming = get_next_name(conn, "job_card", company_id=wo_dict["company_id"])

    jc_id = str(uuid.uuid4())
    jc_t = Table("job_card")
    jc_ins_q = (Q.into(jc_t).columns(
        "id", "naming_series", "work_order_id", "operation_id", "workstation_id",
        "for_quantity", "completed_qty", "total_time_in_minutes", "status"
    ).insert(P(), P(), P(), P(), P(), P(), ValueWrapper("0"), ValueWrapper("0"), ValueWrapper("open")))
    try:
        conn.execute(
            jc_ins_q.get_sql(),
            (jc_id, naming, args.work_order_id, args.operation_id,
             ws_id, for_qty),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("Job Card creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-manufacturing", "create-job-card", "job_card", jc_id,
           new_values={
               "naming_series": naming,
               "work_order_id": args.work_order_id,
               "operation_id": args.operation_id,
               "for_quantity": for_qty,
           })
    conn.commit()

    ok({
        "job_card_id": jc_id,
        "naming_series": naming,
        "work_order_id": args.work_order_id,
        "operation_id": args.operation_id,
        "workstation_id": ws_id,
        "for_quantity": for_qty,
        "status": "open",
    })


# ---------------------------------------------------------------------------
# 15. complete-job-card
# ---------------------------------------------------------------------------

def complete_job_card(conn, args):
    """Complete a Job Card with time recording.

    Required: --job-card-id, --actual-time-in-mins
    Optional: --completed-qty
    """
    if not args.job_card_id:
        err("--job-card-id is required")
    if not args.actual_time_in_mins:
        err("--actual-time-in-mins is required")

    jc_t = Table("job_card")
    jc_q = Q.from_(jc_t).select(jc_t.star).where(jc_t.id == P())
    jc = conn.execute(jc_q.get_sql(), (args.job_card_id,)).fetchone()
    if not jc:
        err(f"Job Card {args.job_card_id} not found")

    jc_dict = row_to_dict(jc)
    if jc_dict["status"] not in ("open", "in_process"):
        err(
            f"Cannot complete Job Card with status '{jc_dict['status']}'. "
            f"Must be 'open' or 'in_process'."
        )

    time_mins = str(round_currency(to_decimal(args.actual_time_in_mins)))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    updates = {
        "status": "completed",
        "total_time_in_minutes": time_mins,
        "time_completed": now_str,
    }

    completed_qty = None
    if args.completed_qty:
        completed_qty = str(round_currency(to_decimal(args.completed_qty)))
        updates["completed_qty"] = completed_qty

    if completed_qty:
        jc_upd_q = (Q.update(jc_t)
                    .set(jc_t.status, ValueWrapper("completed"))
                    .set(jc_t.total_time_in_minutes, P())
                    .set(jc_t.time_completed, P())
                    .set(jc_t.completed_qty, P())
                    .set(jc_t.updated_at, LiteralValue("datetime('now')"))
                    .where(jc_t.id == P()))
        conn.execute(jc_upd_q.get_sql(), (time_mins, now_str, completed_qty, args.job_card_id))
    else:
        jc_upd_q = (Q.update(jc_t)
                    .set(jc_t.status, ValueWrapper("completed"))
                    .set(jc_t.total_time_in_minutes, P())
                    .set(jc_t.time_completed, P())
                    .set(jc_t.updated_at, LiteralValue("datetime('now')"))
                    .where(jc_t.id == P()))
        conn.execute(jc_upd_q.get_sql(), (time_mins, now_str, args.job_card_id))

    audit(conn, "erpclaw-manufacturing", "complete-job-card", "job_card", args.job_card_id,
           old_values={"status": jc_dict["status"]},
           new_values=updates)
    conn.commit()

    ok({
        "job_card_id": args.job_card_id,
        "status": "completed",
        "total_time_in_minutes": time_mins,
        "time_completed": now_str,
        "completed_qty": completed_qty or jc_dict.get("completed_qty", "0"),
    })


# ---------------------------------------------------------------------------
# 16. complete-work-order
# ---------------------------------------------------------------------------

def complete_work_order(conn, args):
    """Complete a work order, producing finished goods.

    Required: --work-order-id
    Optional: --produced-qty (defaults to WO qty), --posting-date

    Calculates production cost (RM + operating), creates SLE for FG receipt
    into target warehouse, and posts perpetual GL entries.
    """
    if not args.work_order_id:
        err("--work-order-id is required")

    wo_t = Table("work_order")
    wo_q = Q.from_(wo_t).select(wo_t.star).where(wo_t.id == P())
    wo = conn.execute(wo_q.get_sql(), (args.work_order_id,)).fetchone()
    if not wo:
        err(f"Work Order {args.work_order_id} not found")

    wo_dict = row_to_dict(wo)
    if wo_dict["status"] != "in_process":
        err(
            f"Cannot complete Work Order with status '{wo_dict['status']}'. "
            f"Must be 'in_process'."
        )

    produced_qty = to_decimal(args.produced_qty or wo_dict["qty"])
    if produced_qty <= 0:
        err("--produced-qty must be greater than 0")

    target_wh = wo_dict.get("target_warehouse_id")
    if not target_wh:
        err("Work Order has no target warehouse. Set --target-warehouse-id when creating.")

    wip_wh = wo_dict.get("wip_warehouse_id")
    company_id = wo_dict["company_id"]
    fg_item_id = wo_dict["item_id"]
    posting_date = args.posting_date or datetime.now().strftime("%Y-%m-%d")

    fiscal_year = _get_fiscal_year(conn, posting_date)
    cost_center_id = _get_cost_center(conn, company_id)

    # --- Calculate production cost ---

    # 1. Raw Material cost: sum of (transferred_qty * valuation_rate) per WO item
    woi_t = Table("work_order_item")
    woi_q = Q.from_(woi_t).select(woi_t.star).where(woi_t.work_order_id == P())
    wo_items = conn.execute(woi_q.get_sql(), (args.work_order_id,)).fetchall()

    rm_cost = Decimal("0")
    for woi_row in wo_items:
        woi = row_to_dict(woi_row)
        transferred = to_decimal(woi["transferred_qty"])
        if transferred <= 0:
            continue
        # Get valuation rate from SLE for the item at WIP warehouse
        try:
            val_rate = get_valuation_rate(conn, woi["item_id"], wip_wh)
            val_rate = to_decimal(str(val_rate)) if val_rate else Decimal("0")
        except Exception:
            val_rate = Decimal("0")
        rm_cost += round_currency(transferred * val_rate)
    rm_cost = round_currency(rm_cost)

    # 2. Operating cost: sum from completed job cards
    jc_t = Table("job_card").as_("jc")
    jc_cost_q = (Q.from_(jc_t)
                 .select(jc_t.total_time_in_minutes, jc_t.workstation_id)
                 .where(jc_t.work_order_id == P())
                 .where(jc_t.status == ValueWrapper("completed")))
    job_cards = conn.execute(jc_cost_q.get_sql(), (args.work_order_id,)).fetchall()

    ws_t2 = Table("workstation")
    ws_cost_q = Q.from_(ws_t2).select(ws_t2.operating_cost_per_hour).where(ws_t2.id == P())
    ws_cost_sql = ws_cost_q.get_sql()
    operating_cost = Decimal("0")
    for jc_row in job_cards:
        jc = row_to_dict(jc_row)
        time_mins = to_decimal(jc.get("total_time_in_minutes", "0"))
        ws_id = jc.get("workstation_id")
        if ws_id and time_mins > 0:
            ws = conn.execute(ws_cost_sql, (ws_id,)).fetchone()
            if ws:
                hour_rate = to_decimal(ws["operating_cost_per_hour"])
                operating_cost += round_currency(
                    (time_mins / Decimal("60")) * hour_rate
                )
    operating_cost = round_currency(operating_cost)

    # 3. FG production rate
    total_production_cost = round_currency(rm_cost + operating_cost)
    fg_rate = round_currency(total_production_cost / produced_qty) if produced_qty > 0 else Decimal("0")

    # Build SLE entries: FG item INTO target warehouse
    sle_entries = [{
        "item_id": fg_item_id,
        "warehouse_id": target_wh,
        "actual_qty": str(round_currency(produced_qty)),
        "incoming_rate": str(fg_rate),
        "fiscal_year": fiscal_year,
    }]

    # Consume raw materials from WIP warehouse (negative SLE entries)
    if wip_wh:
        for woi_row in wo_items:
            woi = row_to_dict(woi_row)
            transferred = to_decimal(woi["transferred_qty"])
            if transferred <= 0:
                continue
            sle_entries.append({
                "item_id": woi["item_id"],
                "warehouse_id": wip_wh,
                "actual_qty": str(round_currency(-transferred)),
                "incoming_rate": "0",
                "fiscal_year": fiscal_year,
            })

    # We use a unique voucher_id suffix to separate material transfer SLEs
    # from completion SLEs for the same work order.
    completion_voucher_id = f"{args.work_order_id}:completion"

    try:
        sle_ids = insert_sle_entries(
            conn, sle_entries,
            voucher_type="work_order",
            voucher_id=completion_voucher_id,
            posting_date=posting_date,
            company_id=company_id,
        )
    except (ValueError, NotImplementedError) as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err(f"SLE posting failed: {e}")

    # Fetch SLE rows for GL generation
    sle_t = Table("stock_ledger_entry")
    sle_q = (Q.from_(sle_t).select(sle_t.star)
             .where(sle_t.voucher_type == ValueWrapper("work_order"))
             .where(sle_t.voucher_id == P())
             .where(sle_t.is_cancelled == 0))
    sle_rows = conn.execute(sle_q.get_sql(), (completion_voucher_id,)).fetchall()
    sle_dicts = [row_to_dict(r) for r in sle_rows]

    # Create perpetual inventory GL entries
    gl_entries = create_perpetual_inventory_gl(
        conn, sle_dicts,
        voucher_type="work_order",
        voucher_id=completion_voucher_id,
        posting_date=posting_date,
        company_id=company_id,
        cost_center_id=cost_center_id,
    )

    gl_ids = []
    if gl_entries:
        if fiscal_year:
            for gle in gl_entries:
                gle["fiscal_year"] = fiscal_year
        try:
            gl_ids = insert_gl_entries(
                conn, gl_entries,
                voucher_type="work_order",
                voucher_id=completion_voucher_id,
                posting_date=posting_date,
                company_id=company_id,
                remarks=f"Production Completion for WO {wo_dict['naming_series']}",
            )
        except (ValueError, NotImplementedError) as e:
            sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
            err(f"GL posting failed: {e}")

    # Update work order — support partial completion
    wo_qty = to_decimal(wo_dict["qty"])
    prev_produced = to_decimal(wo_dict.get("produced_qty") or "0")
    total_produced = prev_produced + produced_qty
    new_status = "completed" if total_produced >= wo_qty else "in_process"

    if new_status == "completed":
        wo_complete_q = (Q.update(wo_t)
                         .set(wo_t.produced_qty, P())
                         .set(wo_t.status, ValueWrapper("completed"))
                         .set(wo_t.actual_end_date, P())
                         .set(wo_t.updated_at, LiteralValue("datetime('now')"))
                         .where(wo_t.id == P()))
        conn.execute(
            wo_complete_q.get_sql(),
            (str(round_currency(total_produced)),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             args.work_order_id),
        )
    else:
        wo_partial_q = (Q.update(wo_t)
                        .set(wo_t.produced_qty, P())
                        .set(wo_t.updated_at, LiteralValue("datetime('now')"))
                        .where(wo_t.id == P()))
        conn.execute(
            wo_partial_q.get_sql(),
            (str(round_currency(total_produced)), args.work_order_id),
        )

    # Consume raw materials — scale proportionally for partial completion
    if total_produced >= wo_qty or wo_qty <= 0:
        # Full completion: consume all transferred material
        conn.execute(
            """UPDATE work_order_item
               SET consumed_qty = transferred_qty
               WHERE work_order_id = ?""",
            (args.work_order_id,),
        )
    else:
        # Partial completion: consume proportionally
        ratio = float(total_produced / wo_qty)
        conn.execute(
            """UPDATE work_order_item
               SET consumed_qty = CAST(ROUND(CAST(transferred_qty AS REAL) * ?, 2) AS TEXT)
               WHERE work_order_id = ?""",
            (ratio, args.work_order_id),
        )

    audit(conn, "erpclaw-manufacturing", "complete-work-order", "work_order", args.work_order_id,
           new_values={
               "status": new_status,
               "produced_qty": str(round_currency(produced_qty)),
               "rm_cost": str(rm_cost),
               "operating_cost": str(operating_cost),
               "total_production_cost": str(total_production_cost),
               "fg_rate": str(fg_rate),
           })
    conn.commit()

    ok({
        "work_order_id": args.work_order_id,
        "status": new_status,
        "produced_qty": str(round_currency(total_produced)),
        "rm_cost": str(rm_cost),
        "operating_cost": str(operating_cost),
        "production_cost": str(total_production_cost),
        "fg_rate": str(fg_rate),
        "sle_count": len(sle_ids) if sle_ids else 0,
        "gl_count": len(gl_ids),
    })


# ---------------------------------------------------------------------------
# 17. cancel-work-order
# ---------------------------------------------------------------------------

def cancel_work_order(conn, args):
    """Cancel a work order, reversing all SLE and GL entries.

    Required: --work-order-id
    """
    if not args.work_order_id:
        err("--work-order-id is required")

    wo_t = Table("work_order")
    wo_q = Q.from_(wo_t).select(wo_t.star).where(wo_t.id == P())
    wo = conn.execute(wo_q.get_sql(), (args.work_order_id,)).fetchone()
    if not wo:
        err(f"Work Order {args.work_order_id} not found")

    wo_dict = row_to_dict(wo)
    if wo_dict["status"] in ("completed", "cancelled"):
        err(
            f"Cannot cancel Work Order with status '{wo_dict['status']}'. "
            f"Completed and cancelled work orders cannot be cancelled."
        )

    posting_date = args.posting_date or datetime.now().strftime("%Y-%m-%d")

    # Reverse material transfer SLE entries
    try:
        reverse_sle_entries(
            conn,
            voucher_type="work_order",
            voucher_id=args.work_order_id,
            posting_date=posting_date,
        )
    except (ValueError, NotImplementedError):
        pass  # No SLE entries to reverse is acceptable

    # Reverse material transfer GL entries
    try:
        reverse_gl_entries(
            conn,
            voucher_type="work_order",
            voucher_id=args.work_order_id,
            posting_date=posting_date,
        )
    except ValueError:
        pass  # No GL entries to reverse is acceptable

    # Also reverse completion entries if any exist
    completion_voucher_id = f"{args.work_order_id}:completion"
    try:
        reverse_sle_entries(
            conn,
            voucher_type="work_order",
            voucher_id=completion_voucher_id,
            posting_date=posting_date,
        )
    except (ValueError, NotImplementedError):
        pass

    try:
        reverse_gl_entries(
            conn,
            voucher_type="work_order",
            voucher_id=completion_voucher_id,
            posting_date=posting_date,
        )
    except ValueError:
        pass

    # Set WO status to cancelled
    wo_cancel_q = (Q.update(wo_t)
                   .set(wo_t.status, ValueWrapper("cancelled"))
                   .set(wo_t.updated_at, LiteralValue("datetime('now')"))
                   .where(wo_t.id == P()))
    conn.execute(wo_cancel_q.get_sql(), (args.work_order_id,))

    # Cancel all open/in_process job cards for this WO
    jc_t = Table("job_card")
    jc_cancel_q = (Q.update(jc_t)
                   .set(jc_t.status, ValueWrapper("cancelled"))
                   .set(jc_t.updated_at, LiteralValue("datetime('now')"))
                   .where(jc_t.work_order_id == P())
                   .where(jc_t.status.isin(["open", "in_process"])))
    conn.execute(jc_cancel_q.get_sql(), (args.work_order_id,))

    audit(conn, "erpclaw-manufacturing", "cancel-work-order", "work_order", args.work_order_id,
           old_values={"status": wo_dict["status"]},
           new_values={"status": "cancelled"})
    conn.commit()

    ok({
        "work_order_id": args.work_order_id,
        "status": "cancelled",
    })


# ---------------------------------------------------------------------------
# 18. create-production-plan
# ---------------------------------------------------------------------------

def create_production_plan(conn, args):
    """Create a Production Plan.

    Required: --company-id, --items (JSON: [{item_id, bom_id, planned_qty,
              warehouse_id?, sales_order_id?}])
    Optional: --planning-horizon-days (default 30)
    """
    if not args.company_id:
        err("--company-id is required")
    if not args.items:
        err("--items is required (JSON array)")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    _validate_company_exists(conn, args.company_id)

    # Planning horizon
    horizon_days = int(args.planning_horizon_days or "30")
    today = datetime.now().strftime("%Y-%m-%d")
    from datetime import timedelta
    end_date = (datetime.now() + timedelta(days=horizon_days)).strftime("%Y-%m-%d")

    # Generate naming series
    naming = get_next_name(conn, "production_plan", company_id=args.company_id)

    plan_id = str(uuid.uuid4())
    pp_t = Table("production_plan")
    pp_ins_q = (Q.into(pp_t).columns(
        "id", "naming_series", "planning_period_start", "planning_period_end",
        "status", "company_id"
    ).insert(P(), P(), P(), P(), ValueWrapper("draft"), P()))
    try:
        conn.execute(pp_ins_q.get_sql(), (plan_id, naming, today, end_date, args.company_id))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("Production Plan creation failed — check for duplicates or invalid data")

    # Insert plan items
    plan_item_count = 0
    for i, item in enumerate(items):
        item_id = item.get("item_id")
        bom_id = item.get("bom_id")
        planned_qty = item.get("planned_qty")

        if not item_id:
            err(f"Plan item {i}: item_id is required")
        if not bom_id:
            err(f"Plan item {i}: bom_id is required")
        if not planned_qty:
            err(f"Plan item {i}: planned_qty is required")

        _validate_item_exists(conn, item_id, f"Plan item {i}: item")
        _validate_bom_exists(conn, bom_id)

        qty = to_decimal(planned_qty)
        if qty <= 0:
            err(f"Plan item {i}: planned_qty must be > 0")

        warehouse_id = item.get("warehouse_id")
        if warehouse_id:
            _validate_warehouse_exists(conn, warehouse_id, f"Plan item {i}: warehouse")

        ppi_t = Table("production_plan_item")
        ppi_ins_q = (Q.into(ppi_t).columns(
            "id", "production_plan_id", "item_id", "bom_id", "planned_qty",
            "produced_qty", "ordered_qty", "sales_order_id", "warehouse_id"
        ).insert(P(), P(), P(), P(), P(), ValueWrapper("0"), ValueWrapper("0"), P(), P()))
        conn.execute(
            ppi_ins_q.get_sql(),
            (str(uuid.uuid4()), plan_id, item_id, bom_id,
             str(round_currency(qty)),
             item.get("sales_order_id"), warehouse_id),
        )
        plan_item_count += 1

    audit(conn, "erpclaw-manufacturing", "create-production-plan", "production_plan", plan_id,
           new_values={
               "naming_series": naming,
               "company_id": args.company_id,
               "item_count": plan_item_count,
               "horizon_days": horizon_days,
           })
    conn.commit()

    ok({
        "production_plan_id": plan_id,
        "naming_series": naming,
        "planning_period_start": today,
        "planning_period_end": end_date,
        "item_count": plan_item_count,
        "status": "draft",
    })


# ---------------------------------------------------------------------------
# MRP helper: BOM explosion for material planning
# ---------------------------------------------------------------------------

def _explode_bom_for_mrp(conn, bom_id, parent_qty):
    """Explode a BOM recursively and return flat list of leaf raw materials.

    Returns dict: {item_id: {"item_id", "total_qty"}}
    Reuses the same recursive logic as explode_bom action but as a standalone
    helper for MRP and other internal callers.
    """
    visited = set()
    leaf_materials = {}

    def _recurse(current_bom_id, qty, depth):
        if depth > MAX_BOM_EXPLOSION_DEPTH:
            return
        if current_bom_id in visited:
            return

        visited.add(current_bom_id)

        bom_hdr = Table("bom")
        bom_hdr_q = Q.from_(bom_hdr).select(bom_hdr.quantity).where(bom_hdr.id == P())
        current_bom = conn.execute(bom_hdr_q.get_sql(), (current_bom_id,)).fetchone()
        if not current_bom:
            visited.discard(current_bom_id)
            return

        bom_base_qty = to_decimal(current_bom["quantity"])
        if bom_base_qty <= 0:
            bom_base_qty = Decimal("1")

        bi_mrp = Table("bom_item")
        bi_mrp_q = Q.from_(bi_mrp).select(bi_mrp.star).where(bi_mrp.bom_id == P())
        bom_items = conn.execute(bi_mrp_q.get_sql(), (current_bom_id,)).fetchall()

        for bi_row in bom_items:
            bi = row_to_dict(bi_row)
            item_qty = to_decimal(bi["quantity"])
            scaled_qty = round_currency((item_qty / bom_base_qty) * qty)

            scrap_pct = to_decimal(bi.get("scrap_percentage", "0"))
            if scrap_pct > 0:
                scaled_qty = round_currency(
                    scaled_qty * (Decimal("1") + scrap_pct / Decimal("100"))
                )

            if bi.get("is_sub_assembly") and bi.get("sub_bom_id"):
                _recurse(bi["sub_bom_id"], scaled_qty, depth + 1)
            else:
                rm_id = bi["item_id"]
                if rm_id in leaf_materials:
                    leaf_materials[rm_id]["total_qty"] = round_currency(
                        to_decimal(leaf_materials[rm_id]["total_qty"]) + scaled_qty
                    )
                else:
                    leaf_materials[rm_id] = {
                        "item_id": rm_id,
                        "total_qty": round_currency(scaled_qty),
                    }

        visited.discard(current_bom_id)

    _recurse(bom_id, parent_qty, depth=0)
    return leaf_materials


# ---------------------------------------------------------------------------
# 19. run-mrp
# ---------------------------------------------------------------------------

def run_mrp(conn, args):
    """Run Material Requirements Planning for a production plan.

    Required: --production-plan-id

    For each plan item, explodes its BOM to leaf materials, computes
    available stock and on-order quantities, and calculates shortfalls.
    """
    if not args.production_plan_id:
        err("--production-plan-id is required")

    pp_t = Table("production_plan")
    pp_q = Q.from_(pp_t).select(pp_t.star).where(pp_t.id == P())
    plan = conn.execute(pp_q.get_sql(), (args.production_plan_id,)).fetchone()
    if not plan:
        err(f"Production Plan {args.production_plan_id} not found")

    plan_dict = row_to_dict(plan)
    if plan_dict["status"] != "draft":
        err(
            f"Cannot run MRP on plan with status '{plan_dict['status']}'. "
            f"Plan must be in 'draft' status."
        )

    company_id = plan_dict["company_id"]

    # Delete any existing materials from a previous MRP run
    ppm_t = Table("production_plan_material")
    del_ppm_q = Q.from_(ppm_t).delete().where(ppm_t.production_plan_id == P())
    conn.execute(del_ppm_q.get_sql(), (args.production_plan_id,))

    # Fetch plan items
    ppi_t = Table("production_plan_item")
    ppi_q = Q.from_(ppi_t).select(ppi_t.star).where(ppi_t.production_plan_id == P())
    plan_items = conn.execute(ppi_q.get_sql(), (args.production_plan_id,)).fetchall()

    if not plan_items:
        err("Production Plan has no items")

    # Accumulate total required materials across all plan items
    # {item_id: {"total_qty": Decimal, "warehouse_id": str or None}}
    aggregated_materials = {}

    for pi_row in plan_items:
        pi = row_to_dict(pi_row)
        bom_id = pi["bom_id"]
        planned_qty = to_decimal(pi["planned_qty"])
        warehouse_id = pi.get("warehouse_id")

        # Explode BOM to leaf materials
        leaf_materials = _explode_bom_for_mrp(conn, bom_id, planned_qty)

        for item_id, mat_info in leaf_materials.items():
            mat_qty = to_decimal(mat_info["total_qty"])
            key = (item_id, warehouse_id or "")
            if key in aggregated_materials:
                aggregated_materials[key]["total_qty"] = round_currency(
                    to_decimal(aggregated_materials[key]["total_qty"]) + mat_qty
                )
            else:
                aggregated_materials[key] = {
                    "item_id": item_id,
                    "total_qty": round_currency(mat_qty),
                    "warehouse_id": warehouse_id,
                }

    # For each aggregated material, compute availability and shortfall
    material_count = 0
    total_shortfall_items = 0

    for key, mat in aggregated_materials.items():
        item_id = mat["item_id"]
        warehouse_id = mat["warehouse_id"]
        required_qty = to_decimal(mat["total_qty"])

        # Get available stock
        available_qty = Decimal("0")
        if warehouse_id:
            try:
                bal = get_stock_balance(conn, item_id, warehouse_id)
                available_qty = to_decimal(bal["qty"]) if bal else Decimal("0")
            except (ValueError, KeyError, NotImplementedError):
                available_qty = Decimal("0")
        else:
            # If no warehouse specified, sum across all warehouses for company
            try:
                sle_t = Table("stock_ledger_entry")
                sle_sum_q = (Q.from_(sle_t)
                             .select(DecimalSum(sle_t.actual_qty).as_("total_qty"))
                             .where(sle_t.item_id == P())
                             .where(sle_t.is_cancelled == 0))
                stock_rows = conn.execute(sle_sum_q.get_sql(), (item_id,)).fetchone()
                if stock_rows and stock_rows["total_qty"]:
                    available_qty = to_decimal(str(stock_rows["total_qty"]))
            except Exception:
                available_qty = Decimal("0")

        # Get on-order quantity from open purchase orders
        # raw SQL — complex COALESCE + decimal_sum + JOIN + NOT IN + arithmetic comparison
        on_order_qty = Decimal("0")
        try:
            po_row = conn.execute(
                """SELECT COALESCE(decimal_sum(poi.qty - poi.received_qty), '0') AS pending
                   FROM purchase_order_item poi
                   JOIN purchase_order po ON po.id = poi.purchase_order_id
                   WHERE poi.item_id = ?
                     AND po.status NOT IN ('cancelled', 'closed')
                     AND poi.qty + 0 > poi.received_qty + 0""",
                (item_id,),
            ).fetchone()
            if po_row and po_row["pending"]:
                on_order_qty = to_decimal(str(po_row["pending"]))
        except Exception:
            on_order_qty = Decimal("0")

        # Calculate shortfall
        available_qty = round_currency(available_qty)
        on_order_qty = round_currency(on_order_qty)
        shortfall_qty = round_currency(
            max(Decimal("0"), required_qty - available_qty - on_order_qty)
        )

        ppm_ins_q = (Q.into(ppm_t).columns(
            "id", "production_plan_id", "item_id", "required_qty",
            "available_qty", "on_order_qty", "shortfall_qty", "warehouse_id"
        ).insert(P(), P(), P(), P(), P(), P(), P(), P()))
        conn.execute(
            ppm_ins_q.get_sql(),
            (str(uuid.uuid4()), args.production_plan_id, item_id,
             str(round_currency(required_qty)),
             str(available_qty), str(on_order_qty),
             str(shortfall_qty), warehouse_id),
        )
        material_count += 1
        if shortfall_qty > 0:
            total_shortfall_items += 1

    # Update plan status
    pp_upd_q = (Q.update(pp_t)
                .set(pp_t.status, ValueWrapper("submitted"))
                .set(pp_t.updated_at, LiteralValue("datetime('now')"))
                .where(pp_t.id == P()))
    conn.execute(pp_upd_q.get_sql(), (args.production_plan_id,))

    audit(conn, "erpclaw-manufacturing", "run-mrp", "production_plan", args.production_plan_id,
           new_values={
               "material_count": material_count,
               "total_shortfall_items": total_shortfall_items,
           })
    conn.commit()

    ok({
        "production_plan_id": args.production_plan_id,
        "status": "submitted",
        "material_count": material_count,
        "total_shortfall_items": total_shortfall_items,
    })


# ---------------------------------------------------------------------------
# 20. get-production-plan
# ---------------------------------------------------------------------------

def get_production_plan(conn, args):
    """Get a production plan with items and materials.

    Required: --production-plan-id
    Returns: plan dict + items list (with item/BOM names) + materials list
    """
    if not args.production_plan_id:
        err("--production-plan-id is required")

    pp_t = Table("production_plan")
    pp_q = Q.from_(pp_t).select(pp_t.star).where(pp_t.id == P())
    plan = conn.execute(pp_q.get_sql(), (args.production_plan_id,)).fetchone()
    if not plan:
        err(f"Production Plan {args.production_plan_id} not found")

    data = row_to_dict(plan)

    # Fetch plan items with item and BOM details
    ppi = Table("production_plan_item").as_("ppi")
    i = Table("item").as_("i")
    b = Table("bom").as_("b")
    ppi_q = (Q.from_(ppi)
             .left_join(i).on(i.id == ppi.item_id)
             .left_join(b).on(b.id == ppi.bom_id)
             .select(ppi.star, i.item_code, i.item_name,
                     b.naming_series.as_("bom_naming_series"))
             .where(ppi.production_plan_id == P())
             .orderby(ppi.rowid))
    items = conn.execute(ppi_q.get_sql(), (args.production_plan_id,)).fetchall()
    data["items"] = [row_to_dict(r) for r in items]

    # Fetch materials with item details
    ppm = Table("production_plan_material").as_("ppm")
    i2 = Table("item").as_("i")
    ppm_q = (Q.from_(ppm)
             .left_join(i2).on(i2.id == ppm.item_id)
             .select(ppm.star, i2.item_code, i2.item_name, i2.stock_uom)
             .where(ppm.production_plan_id == P())
             .orderby(ppm.rowid))
    materials = conn.execute(ppm_q.get_sql(), (args.production_plan_id,)).fetchall()
    data["materials"] = [row_to_dict(r) for r in materials]

    # Summary
    total_shortfall = sum(
        1 for m in data["materials"]
        if to_decimal(m.get("shortfall_qty", "0")) > 0
    )
    data["total_shortfall_items"] = total_shortfall

    ok(data)


# ---------------------------------------------------------------------------
# 21. generate-work-orders
# ---------------------------------------------------------------------------

def generate_work_orders(conn, args):
    """Generate work orders from a production plan.

    Required: --production-plan-id

    Creates a work order for each plan item that does not yet have one.
    """
    if not args.production_plan_id:
        err("--production-plan-id is required")

    pp_t = Table("production_plan")
    pp_q = Q.from_(pp_t).select(pp_t.star).where(pp_t.id == P())
    plan = conn.execute(pp_q.get_sql(), (args.production_plan_id,)).fetchone()
    if not plan:
        err(f"Production Plan {args.production_plan_id} not found")

    plan_dict = row_to_dict(plan)
    company_id = plan_dict["company_id"]

    # Fetch plan items without work orders
    ppi_t = Table("production_plan_item")
    ppi_q = (Q.from_(ppi_t).select(ppi_t.star)
             .where(ppi_t.production_plan_id == P())
             .where(ppi_t.work_order_id.isnull()))
    plan_items = conn.execute(ppi_q.get_sql(), (args.production_plan_id,)).fetchall()

    if not plan_items:
        ok({
            "production_plan_id": args.production_plan_id,
            "work_orders_created": 0,
            "message": "All plan items already have work orders",
        })
        return  # _ok exits, but guard anyway

    work_orders_created = 0
    created_wo_ids = []

    for pi_row in plan_items:
        pi = row_to_dict(pi_row)
        bom_id = pi["bom_id"]
        planned_qty = to_decimal(pi["planned_qty"])
        warehouse_id = pi.get("warehouse_id")

        # Get BOM details
        bom_t = Table("bom")
        bom_q = Q.from_(bom_t).select(bom_t.star).where(bom_t.id == P())
        bom = conn.execute(bom_q.get_sql(), (bom_id,)).fetchone()
        if not bom:
            continue
        bom_dict = row_to_dict(bom)
        fg_item_id = bom_dict["item_id"]
        bom_base_qty = to_decimal(bom_dict["quantity"])
        if bom_base_qty <= 0:
            bom_base_qty = Decimal("1")

        # Generate naming series for WO
        naming = get_next_name(conn, "work_order", company_id=company_id)

        wo_id = str(uuid.uuid4())
        wo_t = Table("work_order")
        wo_ins_q = (Q.into(wo_t).columns(
            "id", "naming_series", "item_id", "bom_id", "qty", "produced_qty",
            "production_plan_id", "sales_order_id",
            "target_warehouse_id",
            "status", "material_transferred_for_manufacturing", "company_id"
        ).insert(P(), P(), P(), P(), P(), ValueWrapper("0"), P(), P(), P(),
                 ValueWrapper("draft"), ValueWrapper("0"), P()))
        try:
            conn.execute(
                wo_ins_q.get_sql(),
                (wo_id, naming, fg_item_id, bom_id,
                 str(round_currency(planned_qty)),
                 args.production_plan_id, pi.get("sales_order_id"),
                 warehouse_id, company_id),
            )
        except sqlite3.IntegrityError:
            continue

        # Copy BOM items to work_order_item
        bi_t = Table("bom_item")
        bi_fetch_q = (Q.from_(bi_t)
                      .select(bi_t.item_id, bi_t.quantity, bi_t.source_warehouse_id)
                      .where(bi_t.bom_id == P()))
        bom_items = conn.execute(bi_fetch_q.get_sql(), (bom_id,)).fetchall()

        woi_t = Table("work_order_item")
        woi_ins_q = (Q.into(woi_t).columns(
            "id", "work_order_id", "item_id", "required_qty",
            "transferred_qty", "consumed_qty", "source_warehouse_id"
        ).insert(P(), P(), P(), P(), ValueWrapper("0"), ValueWrapper("0"), P()))
        woi_ins_sql = woi_ins_q.get_sql()
        for bi_row in bom_items:
            bi = row_to_dict(bi_row)
            bi_qty = to_decimal(bi["quantity"])
            required_qty = round_currency((bi_qty / bom_base_qty) * planned_qty)

            conn.execute(
                woi_ins_sql,
                (str(uuid.uuid4()), wo_id, bi["item_id"],
                 str(required_qty), bi.get("source_warehouse_id")),
            )

        # Link work order back to plan item
        ppi_upd_q = (Q.update(ppi_t)
                     .set(ppi_t.work_order_id, P())
                     .where(ppi_t.id == P()))
        conn.execute(ppi_upd_q.get_sql(), (wo_id, pi["id"]))

        audit(conn, "erpclaw-manufacturing", "generate-work-orders", "work_order", wo_id,
               new_values={
                   "naming_series": naming,
                   "production_plan_id": args.production_plan_id,
                   "item_id": fg_item_id,
                   "qty": str(round_currency(planned_qty)),
               })

        created_wo_ids.append(wo_id)
        work_orders_created += 1

    conn.commit()

    ok({
        "production_plan_id": args.production_plan_id,
        "work_orders_created": work_orders_created,
        "work_order_ids": created_wo_ids,
    })


# ---------------------------------------------------------------------------
# 22. generate-purchase-requests
# ---------------------------------------------------------------------------

def generate_purchase_requests(conn, args):
    """Generate purchase request data from a production plan's MRP results.

    Required: --production-plan-id

    Returns the list of materials with shortfalls. For v1, this returns
    data for the AI agent to relay to the buying skill.
    """
    if not args.production_plan_id:
        err("--production-plan-id is required")

    pp_t = Table("production_plan")
    pp_q = Q.from_(pp_t).select(pp_t.star).where(pp_t.id == P())
    plan = conn.execute(pp_q.get_sql(), (args.production_plan_id,)).fetchone()
    if not plan:
        err(f"Production Plan {args.production_plan_id} not found")

    # Fetch all materials with shortfall > 0
    # raw SQL — arithmetic comparison (shortfall_qty + 0 > 0)
    materials = conn.execute(
        """SELECT ppm.*, i.item_code, i.item_name, i.stock_uom
           FROM production_plan_material ppm
           LEFT JOIN item i ON i.id = ppm.item_id
           WHERE ppm.production_plan_id = ?
             AND ppm.shortfall_qty + 0 > 0
           ORDER BY ppm.rowid""",
        (args.production_plan_id,),
    ).fetchall()

    purchase_requests = []
    for mat_row in materials:
        mat = row_to_dict(mat_row)
        purchase_requests.append({
            "item_id": mat["item_id"],
            "item_code": mat.get("item_code", ""),
            "item_name": mat.get("item_name", ""),
            "uom": mat.get("stock_uom", ""),
            "required_qty": mat["required_qty"],
            "available_qty": mat["available_qty"],
            "on_order_qty": mat["on_order_qty"],
            "shortfall_qty": mat["shortfall_qty"],
            "warehouse_id": mat.get("warehouse_id"),
        })

    audit(conn, "erpclaw-manufacturing", "generate-purchase-requests", "production_plan",
           args.production_plan_id,
           new_values={"shortfall_items": len(purchase_requests)})
    conn.commit()

    ok({
        "production_plan_id": args.production_plan_id,
        "purchase_requests": purchase_requests,
        "shortfall_item_count": len(purchase_requests),
    })


# ---------------------------------------------------------------------------
# 23. add-subcontracting-order
# ---------------------------------------------------------------------------

def add_subcontracting_order(conn, args):
    """Create a subcontracting order.

    Required: --supplier-id, --bom-id, --quantity, --company-id
    Optional: --service-item-id, --supplier-warehouse-id
    """
    if not args.supplier_id:
        err("--supplier-id is required")
    if not args.bom_id:
        err("--bom-id is required")
    if not args.quantity:
        err("--quantity is required")
    if not args.company_id:
        err("--company-id is required")

    qty = to_decimal(args.quantity)
    if qty <= 0:
        err("--quantity must be greater than 0")

    # Validate supplier
    sup_t = Table("supplier")
    sup_q = Q.from_(sup_t).select(sup_t.id).where((sup_t.id == P()) | (sup_t.name == P()))
    supplier = conn.execute(sup_q.get_sql(), (args.supplier_id, args.supplier_id)).fetchone()
    if not supplier:
        err(f"Supplier {args.supplier_id} not found")
    args.supplier_id = supplier["id"]

    # Validate BOM
    bom = _validate_bom_exists(conn, args.bom_id)
    bom_dict = row_to_dict(bom)
    finished_item_id = bom_dict["item_id"]

    # Validate company
    _validate_company_exists(conn, args.company_id)

    # Service item: required by schema (NOT NULL), use provided or FG item as fallback
    service_item_id = args.service_item_id or finished_item_id
    _validate_item_exists(conn, service_item_id, "Service item")

    # Validate supplier warehouse if provided
    supplier_wh = args.supplier_warehouse_id
    if supplier_wh:
        _validate_warehouse_exists(conn, supplier_wh, "Supplier warehouse")

    # Generate naming series
    naming = get_next_name(conn, "subcontracting_order", company_id=args.company_id)

    sco_id = str(uuid.uuid4())
    sco_t = Table("subcontracting_order")
    sco_ins_q = (Q.into(sco_t).columns(
        "id", "naming_series", "supplier_id", "service_item_id",
        "finished_item_id", "bom_id", "qty",
        "supplier_warehouse_id", "status",
        "materials_transferred", "received_qty", "company_id"
    ).insert(P(), P(), P(), P(), P(), P(), P(), P(), ValueWrapper("draft"),
             ValueWrapper("0"), ValueWrapper("0"), P()))
    try:
        conn.execute(
            sco_ins_q.get_sql(),
            (sco_id, naming, args.supplier_id, service_item_id,
             finished_item_id, args.bom_id, str(round_currency(qty)),
             supplier_wh, args.company_id),
        )
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("Subcontracting order creation failed — check for duplicates or invalid data")

    audit(conn, "erpclaw-manufacturing", "add-subcontracting-order", "subcontracting_order", sco_id,
           new_values={
               "naming_series": naming,
               "supplier_id": args.supplier_id,
               "bom_id": args.bom_id,
               "finished_item_id": finished_item_id,
               "qty": str(round_currency(qty)),
           })
    conn.commit()

    ok({
        "subcontracting_order_id": sco_id,
        "naming_series": naming,
        "supplier_id": args.supplier_id,
        "finished_item_id": finished_item_id,
        "bom_id": args.bom_id,
        "qty": str(round_currency(qty)),
        "status": "draft",
    })


# ---------------------------------------------------------------------------
# 24. status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """Get manufacturing module status summary.

    Optional: --company-id (filter by company)
    """
    # BOMs
    bom_t = Table("bom")
    bom_cnt_q = Q.from_(bom_t).select(fn.Count("*"))
    if args.company_id:
        bom_cnt_q = bom_cnt_q.where(bom_t.company_id == P())
    total_boms = conn.execute(bom_cnt_q.get_sql(), [args.company_id] if args.company_id else []).fetchone()[0]

    bom_active_q = Q.from_(bom_t).select(fn.Count("*")).where(bom_t.is_active == 1)
    if args.company_id:
        bom_active_q = bom_active_q.where(bom_t.company_id == P())
    active_boms = conn.execute(bom_active_q.get_sql(), [args.company_id] if args.company_id else []).fetchone()[0]

    # Work Orders by status
    wo_t = Table("work_order")
    wo_statuses = {}
    for status in VALID_WO_STATUSES:
        wo_status_q = Q.from_(wo_t).select(fn.Count("*")).where(wo_t.status == P())
        params = [status]
        if args.company_id:
            wo_status_q = wo_status_q.where(wo_t.company_id == P())
            params.append(args.company_id)
        cnt = conn.execute(wo_status_q.get_sql(), params).fetchone()[0]
        if cnt > 0:
            wo_statuses[status] = cnt

    wo_total_q = Q.from_(wo_t).select(fn.Count("*"))
    if args.company_id:
        wo_total_q = wo_total_q.where(wo_t.company_id == P())
    total_wos = conn.execute(wo_total_q.get_sql(), [args.company_id] if args.company_id else []).fetchone()[0]

    # Job Cards
    jc_t = Table("job_card").as_("jc")
    wo_jc = Table("work_order").as_("wo")
    jc_cnt_q = (Q.from_(jc_t)
                .join(wo_jc).on(wo_jc.id == jc_t.work_order_id)
                .select(fn.Count("*"))
                .where(jc_t.status.isin(["open", "in_process"])))
    jc_params = []
    if args.company_id:
        jc_cnt_q = jc_cnt_q.where(wo_jc.company_id == P())
        jc_params.append(args.company_id)
    open_job_cards = conn.execute(jc_cnt_q.get_sql(), jc_params).fetchone()[0]

    # Production Plans
    pp_t = Table("production_plan")
    pp_cnt_q = Q.from_(pp_t).select(fn.Count("*")).where(pp_t.status != ValueWrapper("cancelled"))
    pp_params = []
    if args.company_id:
        pp_cnt_q = pp_cnt_q.where(pp_t.company_id == P())
        pp_params.append(args.company_id)
    active_plans = conn.execute(pp_cnt_q.get_sql(), pp_params).fetchone()[0]

    # Subcontracting Orders
    sco_t = Table("subcontracting_order")
    sco_cnt_q = (Q.from_(sco_t).select(fn.Count("*"))
                 .where(sco_t.status.notin(["cancelled", "completed"])))
    sco_params = []
    if args.company_id:
        sco_cnt_q = sco_cnt_q.where(sco_t.company_id == P())
        sco_params.append(args.company_id)
    active_scos = conn.execute(sco_cnt_q.get_sql(), sco_params).fetchone()[0]

    # Operations and Workstations
    op_t = Table("operation")
    op_cnt_q = Q.from_(op_t).select(fn.Count("*")).where(op_t.is_active == 1)
    total_operations = conn.execute(op_cnt_q.get_sql()).fetchone()[0]

    ws_t = Table("workstation")
    ws_cnt_q = Q.from_(ws_t).select(fn.Count("*")).where(ws_t.status == ValueWrapper("active"))
    total_workstations = conn.execute(ws_cnt_q.get_sql()).fetchone()[0]

    ok({
        "total_boms": total_boms,
        "active_boms": active_boms,
        "total_work_orders": total_wos,
        "work_orders_by_status": wo_statuses,
        "open_job_cards": open_job_cards,
        "active_production_plans": active_plans,
        "active_subcontracting_orders": active_scos,
        "active_operations": total_operations,
        "active_workstations": total_workstations,
    })


# ---------------------------------------------------------------------------
# ACTIONS dispatch table
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-bom": add_bom,
    "update-bom": update_bom,
    "get-bom": get_bom,
    "list-boms": list_boms,
    "explode-bom": explode_bom,
    "add-operation": add_operation,
    "add-workstation": add_workstation,
    "add-routing": add_routing,
    "add-work-order": add_work_order,
    "get-work-order": get_work_order,
    "list-work-orders": list_work_orders,
    "start-work-order": start_work_order,
    "transfer-materials": transfer_materials,
    "create-job-card": create_job_card,
    "complete-job-card": complete_job_card,
    "complete-work-order": complete_work_order,
    "cancel-work-order": cancel_work_order,
    "create-production-plan": create_production_plan,
    "run-mrp": run_mrp,
    "get-production-plan": get_production_plan,
    "generate-work-orders": generate_work_orders,
    "generate-purchase-requests": generate_purchase_requests,
    "add-subcontracting-order": add_subcontracting_order,
    "status": status_action,
}


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ERPClaw Manufacturing Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Entity IDs
    parser.add_argument("--company-id")
    parser.add_argument("--item-id")
    parser.add_argument("--bom-id")
    parser.add_argument("--work-order-id")
    parser.add_argument("--job-card-id")
    parser.add_argument("--production-plan-id")

    # Master data
    parser.add_argument("--name")
    parser.add_argument("--description")

    # Quantities
    parser.add_argument("--quantity")
    parser.add_argument("--produced-qty")
    parser.add_argument("--for-quantity")
    parser.add_argument("--completed-qty")

    # JSON payloads
    parser.add_argument("--items")       # JSON array
    parser.add_argument("--operations")  # JSON array

    # Operation / workstation / routing references
    parser.add_argument("--routing-id")
    parser.add_argument("--operation-id")
    parser.add_argument("--workstation-id")

    # Workstation fields
    parser.add_argument("--hour-rate")
    parser.add_argument("--time-in-mins")
    parser.add_argument("--actual-time-in-mins")
    parser.add_argument("--workstation-type")
    parser.add_argument("--working-hours-per-day")
    parser.add_argument("--production-capacity")
    parser.add_argument("--holiday-list-id")

    # Dates
    parser.add_argument("--planned-start-date")
    parser.add_argument("--planned-end-date")
    parser.add_argument("--posting-date")

    # Warehouse references
    parser.add_argument("--source-warehouse-id")
    parser.add_argument("--target-warehouse-id")
    parser.add_argument("--wip-warehouse-id")

    # Sales / supplier / subcontracting
    parser.add_argument("--sales-order-id")
    parser.add_argument("--supplier-id")
    parser.add_argument("--service-item-id")
    parser.add_argument("--supplier-warehouse-id")

    # Production planning
    parser.add_argument("--planning-horizon-days")

    # BOM flags
    parser.add_argument("--is-active")
    parser.add_argument("--is-default")
    parser.add_argument("--uom")

    # Filters
    parser.add_argument("--status")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")
    parser.add_argument("--search")

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
        sys.stderr.write(f"[erpclaw-manufacturing] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
