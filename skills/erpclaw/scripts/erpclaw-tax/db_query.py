#!/usr/bin/env python3
"""ERPClaw Tax Skill — db_query.py

Tax templates, rules, calculation, withholding, and 1099 reporting.
Owns: tax_template, tax_template_line, tax_category, tax_rule,
      item_tax_template, tax_withholding_category, tax_withholding_group,
      tax_withholding_entry.

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
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query_helpers import resolve_company_id
    from erpclaw_lib.query import Q, P, Table, Field, fn, DecimalSum, Order
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company", "account", "party_type_registry"]

VALID_TAX_TYPES = ("sales", "purchase", "both")
VALID_CHARGE_TYPES = (
    "actual", "on_net_total", "on_previous_row_amount",
    "on_previous_row_total", "on_item_quantity",
)
VALID_ADD_DEDUCT = ("add", "deduct")
VALID_FORM_TYPES = ("1099-NEC", "1099-MISC")

# PyPika table aliases
tt_t = Table("tax_template")
tl_t = Table("tax_template_line")
tc_t = Table("tax_category")
tr_t = Table("tax_rule")
itt_t = Table("item_tax_template")
twc_t = Table("tax_withholding_category")
twg_t = Table("tax_withholding_group")
twe_t = Table("tax_withholding_entry")
co_t = Table("company")
acct_t = Table("account")
cust_t = Table("customer")
supp_t = Table("supplier")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json_arg(value, name):
    """Parse a JSON string argument, returning the parsed object or erroring."""
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        err(f"Invalid JSON for --{name}: {value}")


def _validate_lines(lines):
    """Validate tax template lines structure."""
    if not lines or not isinstance(lines, list):
        err("--lines must be a non-empty JSON array")
    for i, line in enumerate(lines):
        if not isinstance(line, dict):
            err(f"Line {i} must be an object")
        if "tax_account_id" not in line:
            err(f"Line {i} missing tax_account_id")
        if "rate" not in line:
            err(f"Line {i} missing rate")
        try:
            to_decimal(str(line["rate"]))
        except (InvalidOperation, ValueError):
            err(f"Line {i} has invalid rate: {line['rate']}")
        ct = line.get("charge_type", "on_net_total")
        if ct not in VALID_CHARGE_TYPES:
            err(f"Line {i} has invalid charge_type: {ct}")
        ad = line.get("add_deduct", "add")
        if ad not in VALID_ADD_DEDUCT:
            err(f"Line {i} has invalid add_deduct: {ad}")


def _insert_lines(conn, template_id, lines):
    """Insert tax_template_line rows for a template."""
    q = (
        Q.into(tl_t)
        .columns("id", "tax_template_id", "tax_account_id", "rate",
                 "charge_type", "row_order", "add_deduct",
                 "included_in_print_rate", "description")
        .insert(P(), P(), P(), P(), P(), P(), P(), P(), P())
    )
    sql = q.get_sql()
    for i, line in enumerate(lines):
        conn.execute(sql,
            (str(uuid.uuid4()), template_id, line["tax_account_id"],
             str(round_currency(to_decimal(str(line["rate"])))),
             line.get("charge_type", "on_net_total"),
             line.get("row_order", i),
             line.get("add_deduct", "add"),
             1 if line.get("included_in_print_rate") else 0,
             line.get("description", "")),
        )


def _get_template_lines(conn, template_id):
    """Fetch template lines with account names, ordered by row_order."""
    tl = Table("tax_template_line")
    a = Table("account")
    q = (
        Q.from_(tl)
        .select(tl.star, a.name.as_("account_name"))
        .left_join(a).on(a.id == tl.tax_account_id)
        .where(tl.tax_template_id == P())
        .orderby(tl.row_order)
    )
    rows = conn.execute(q.get_sql(), (template_id,)).fetchall()
    return [row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Tax Template actions
# ---------------------------------------------------------------------------

def add_tax_template(conn, args):
    if not args.name:
        err("--name is required")
    if not args.tax_type or args.tax_type not in VALID_TAX_TYPES:
        err(f"--tax-type must be one of: {', '.join(VALID_TAX_TYPES)}")
    if not args.company_id:
        err("--company-id is required")

    # Verify company exists
    q = Q.from_(co_t).select(co_t.id).where(co_t.id == P())
    co = conn.execute(q.get_sql(), (args.company_id,)).fetchone()
    if not co:
        err(f"Company not found: {args.company_id}")

    lines = _parse_json_arg(args.lines, "lines")
    if not lines:
        err("--lines is required (JSON array)")
    _validate_lines(lines)

    # Verify all tax accounts exist
    q_acct = Q.from_(acct_t).select(acct_t.id).where(acct_t.id == P())
    acct_sql = q_acct.get_sql()
    for i, line in enumerate(lines):
        acct = conn.execute(acct_sql, (line["tax_account_id"],)).fetchone()
        if not acct:
            err(f"Line {i}: account not found: {line['tax_account_id']}")

    tid = str(uuid.uuid4())
    # If setting as default, clear other defaults of same type+company
    if args.is_default:
        q_clear = (
            Q.update(tt_t).set(tt_t.is_default, 0)
            .where(tt_t.company_id == P())
            .where((tt_t.tax_type == P()) | (tt_t.tax_type == "both"))
        )
        conn.execute(q_clear.get_sql(), (args.company_id, args.tax_type))

    q_ins = (
        Q.into(tt_t)
        .columns("id", "name", "tax_type", "is_default", "company_id")
        .insert(P(), P(), P(), P(), P())
    )
    conn.execute(q_ins.get_sql(),
        (tid, args.name, args.tax_type, 1 if args.is_default else 0, args.company_id))
    _insert_lines(conn, tid, lines)

    audit(conn, "erpclaw-tax", "add-tax-template", "tax_template", tid,
           new_values={"name": args.name, "tax_type": args.tax_type, "lines": len(lines)})
    conn.commit()
    ok({"status": "created", "tax_template_id": tid, "name": args.name,
         "line_count": len(lines)})


def update_tax_template(conn, args):
    if not args.tax_template_id:
        err("--tax-template-id is required")

    q_get = Q.from_(tt_t).select(tt_t.star).where(tt_t.id == P())
    t = conn.execute(q_get.get_sql(), (args.tax_template_id,)).fetchone()
    if not t:
        err(f"Tax template not found: {args.tax_template_id}")

    updates, params, updated_fields = [], [], []

    if args.name is not None:
        updates.append("name = ?")
        params.append(args.name)
        updated_fields.append("name")

    if args.is_default is not None:
        is_def = 1 if args.is_default else 0
        if is_def:
            q_clear = (
                Q.update(tt_t).set(tt_t.is_default, 0)
                .where(tt_t.company_id == P())
                .where((tt_t.tax_type == P()) | (tt_t.tax_type == "both"))
                .where(tt_t.id != P())
            )
            conn.execute(q_clear.get_sql(),
                (t["company_id"], t["tax_type"], args.tax_template_id))
        updates.append("is_default = ?")
        params.append(is_def)
        updated_fields.append("is_default")

    # Replace lines if provided
    lines = _parse_json_arg(args.lines, "lines") if args.lines else None
    if lines is not None:
        _validate_lines(lines)
        q_acct = Q.from_(acct_t).select(acct_t.id).where(acct_t.id == P())
        acct_sql = q_acct.get_sql()
        for i, line in enumerate(lines):
            acct = conn.execute(acct_sql, (line["tax_account_id"],)).fetchone()
            if not acct:
                err(f"Line {i}: account not found: {line['tax_account_id']}")
        q_del = Q.from_(tl_t).delete().where(tl_t.tax_template_id == P())
        conn.execute(q_del.get_sql(), (args.tax_template_id,))
        _insert_lines(conn, args.tax_template_id, lines)
        updated_fields.append("lines")

    # Dynamic UPDATE — keep as raw SQL (variable SET columns)
    if updates:
        updates.append("updated_at = datetime('now')")
        params.append(args.tax_template_id)
        conn.execute(
            f"UPDATE tax_template SET {', '.join(updates)} WHERE id = ?", params)

    if not updated_fields:
        err("No fields to update")

    audit(conn, "erpclaw-tax", "update-tax-template", "tax_template", args.tax_template_id,
           new_values={"updated_fields": updated_fields})
    conn.commit()
    ok({"status": "updated", "tax_template_id": args.tax_template_id,
         "updated_fields": updated_fields})


def get_tax_template(conn, args):
    if not args.tax_template_id:
        err("--tax-template-id is required")

    q = Q.from_(tt_t).select(tt_t.star).where(tt_t.id == P())
    t = conn.execute(q.get_sql(), (args.tax_template_id,)).fetchone()
    if not t:
        err(f"Tax template not found: {args.tax_template_id}")

    data = row_to_dict(t)
    data["lines"] = _get_template_lines(conn, args.tax_template_id)
    ok(data)


def list_tax_templates(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    base = Q.from_(tt_t).where(tt_t.company_id == P())
    params = [company_id]
    if args.tax_type:
        base = base.where((tt_t.tax_type == P()) | (tt_t.tax_type == "both"))
        params.append(args.tax_type)

    q_count = base.select(fn.Count("*").as_("cnt"))
    total_count = conn.execute(q_count.get_sql(), params).fetchone()["cnt"]

    q_rows = base.select(tt_t.star).orderby(tt_t.name).limit(P()).offset(P())
    rows = conn.execute(q_rows.get_sql(), params + [limit, offset]).fetchall()
    ok({"templates": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


def delete_tax_template(conn, args):
    if not args.tax_template_id:
        err("--tax-template-id is required")

    q_get = Q.from_(tt_t).select(tt_t.star).where(tt_t.id == P())
    t = conn.execute(q_get.get_sql(), (args.tax_template_id,)).fetchone()
    if not t:
        err(f"Tax template not found: {args.tax_template_id}")

    # Check if referenced by tax rules
    q_ref = Q.from_(tr_t).select(fn.Count("*").as_("cnt")).where(tr_t.tax_template_id == P())
    ref = conn.execute(q_ref.get_sql(), (args.tax_template_id,)).fetchone()
    if ref["cnt"] > 0:
        err(f"Cannot delete: template is referenced by {ref['cnt']} tax rule(s)")

    # Check if referenced by item_tax_template
    q_ref2 = Q.from_(itt_t).select(fn.Count("*").as_("cnt")).where(itt_t.tax_template_id == P())
    ref2 = conn.execute(q_ref2.get_sql(), (args.tax_template_id,)).fetchone()
    if ref2["cnt"] > 0:
        err(f"Cannot delete: template is referenced by {ref2['cnt']} item tax template(s)")

    q_del_lines = Q.from_(tl_t).delete().where(tl_t.tax_template_id == P())
    conn.execute(q_del_lines.get_sql(), (args.tax_template_id,))
    q_del_tmpl = Q.from_(tt_t).delete().where(tt_t.id == P())
    conn.execute(q_del_tmpl.get_sql(), (args.tax_template_id,))

    audit(conn, "erpclaw-tax", "delete-tax-template", "tax_template", args.tax_template_id,
           old_values={"name": t["name"]})
    conn.commit()
    ok({"deleted": True})


# ---------------------------------------------------------------------------
# Tax Category actions
# ---------------------------------------------------------------------------

def add_tax_category(conn, args):
    if not args.name:
        err("--name is required")

    cid = str(uuid.uuid4())
    q = Q.into(tc_t).columns("id", "name", "description").insert(P(), P(), P())
    conn.execute(q.get_sql(), (cid, args.name, args.description or ""))
    audit(conn, "erpclaw-tax", "add-tax-category", "tax_category", cid,
           new_values={"name": args.name})
    conn.commit()
    ok({"status": "created", "tax_category_id": cid, "name": args.name})


def list_tax_categories(conn, args):
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    q_count = Q.from_(tc_t).select(fn.Count("*").as_("cnt"))
    total_count = conn.execute(q_count.get_sql()).fetchone()["cnt"]
    q = Q.from_(tc_t).select(tc_t.star).orderby(tc_t.name).limit(P()).offset(P())
    rows = conn.execute(q.get_sql(), (limit, offset)).fetchall()
    ok({"categories": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# Tax Rule actions
# ---------------------------------------------------------------------------

def add_tax_rule(conn, args):
    if not args.tax_template_id:
        err("--tax-template-id is required")
    if not args.tax_type or args.tax_type not in ("sales", "purchase"):
        err("--tax-type must be 'sales' or 'purchase'")
    if args.priority is None:
        err("--priority is required")

    # Verify template exists
    q_tmpl = Q.from_(tt_t).select(tt_t.id, tt_t.company_id).where(tt_t.id == P())
    t = conn.execute(q_tmpl.get_sql(), (args.tax_template_id,)).fetchone()
    if not t:
        err(f"Tax template not found: {args.tax_template_id}")

    # At least one filter condition required
    has_filter = any([
        args.customer_id, args.customer_group, args.supplier_id,
        args.shipping_state, args.tax_category_id,
    ])
    if not has_filter:
        err("At least one filter condition required (customer, supplier, state, or category)")

    rid = str(uuid.uuid4())
    q_ins = (
        Q.into(tr_t)
        .columns("id", "tax_template_id", "tax_type", "customer_id",
                 "customer_group", "supplier_id", "supplier_group",
                 "shipping_state", "tax_category_id", "priority", "company_id")
        .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P())
    )
    conn.execute(q_ins.get_sql(),
        (rid, args.tax_template_id, args.tax_type,
         args.customer_id, args.customer_group,
         args.supplier_id, None,
         args.shipping_state, args.tax_category_id,
         args.priority, t["company_id"]))
    audit(conn, "erpclaw-tax", "add-tax-rule", "tax_rule", rid,
           new_values={"tax_template_id": args.tax_template_id, "tax_type": args.tax_type})
    conn.commit()
    ok({"status": "created", "tax_rule_id": rid})


def list_tax_rules(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    q_count = Q.from_(tr_t).select(fn.Count("*").as_("cnt")).where(tr_t.company_id == P())
    total_count = conn.execute(q_count.get_sql(), (company_id,)).fetchone()["cnt"]

    r = Table("tax_rule")
    t = Table("tax_template")
    q = (
        Q.from_(r)
        .select(r.star, t.name.as_("template_name"))
        .left_join(t).on(t.id == r.tax_template_id)
        .where(r.company_id == P())
        .orderby(r.priority)
        .orderby(r.created_at)
        .limit(P()).offset(P())
    )
    rows = conn.execute(q.get_sql(), (company_id, limit, offset)).fetchall()
    ok({"rules": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# Resolve & Calculate
# ---------------------------------------------------------------------------

def resolve_tax_template(conn, args):
    """Auto-select tax template by matching tax rules in priority order."""
    if not args.party_type:
        err("--party-type is required")
    # Validate against registered party types
    valid = conn.execute("SELECT party_type FROM party_type_registry WHERE party_type = ?",
                         (args.party_type,)).fetchone()
    if not valid:
        all_types = [r[0] for r in conn.execute("SELECT party_type FROM party_type_registry").fetchall()]
        err(f"--party-type '{args.party_type}' is not registered. Valid types: {', '.join(all_types)}")
    if not args.party_id:
        err("--party-id is required")
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    if args.transaction_type:
        tx_type = args.transaction_type
    elif args.party_type == "customer":
        tx_type = "sales"
    elif args.party_type == "supplier":
        tx_type = "purchase"
    else:
        # Generic party type — default to sales; caller should provide --transaction-type
        tx_type = "sales"

    # Check party exemption (customer or supplier table)
    is_exempt = False
    if args.party_type == "customer":
        q_cust = Q.from_(cust_t).select(cust_t.id, cust_t.exempt_from_sales_tax).where(cust_t.id == P())
        party = conn.execute(q_cust.get_sql(), (args.party_id,)).fetchone()
        if party and party["exempt_from_sales_tax"]:
            is_exempt = True
    elif args.party_type == "supplier":
        q_supp = Q.from_(supp_t).select(supp_t.id).where(supp_t.id == P())
        party = conn.execute(q_supp.get_sql(), (args.party_id,)).fetchone()
    else:
        # Generic party type — skip party-specific validation
        # Tax template lookup still works via party_type field in tax rules
        pass

    # Parse shipping address if provided
    shipping = _parse_json_arg(args.shipping_address, "shipping-address") if args.shipping_address else None
    ship_state = shipping.get("state") if shipping else None

    # Query matching rules, ordered by priority
    r = Table("tax_rule")
    t = Table("tax_template")
    q_rules = (
        Q.from_(r)
        .select(r.star, t.name.as_("template_name"))
        .join(t).on(t.id == r.tax_template_id)
        .where(r.company_id == P())
        .where((r.tax_type == P()) | (t.tax_type == "both"))
        .orderby(r.priority, order=Order.asc)
    )
    rules = conn.execute(q_rules.get_sql(), (company_id, tx_type)).fetchall()

    best_template_id = None
    best_template_name = None

    q_cust_grp = Q.from_(cust_t).select(cust_t.customer_group).where(cust_t.id == P())
    cust_grp_sql = q_cust_grp.get_sql()

    for rule in rules:
        match = True
        # Customer-specific rule
        if rule["customer_id"] and rule["customer_id"] != args.party_id:
            match = False
        # Customer group rule
        if rule["customer_group"]:
            cust = conn.execute(cust_grp_sql, (args.party_id,)).fetchone()
            if not cust or cust["customer_group"] != rule["customer_group"]:
                match = False
        # Supplier-specific rule
        if rule["supplier_id"] and rule["supplier_id"] != args.party_id:
            match = False
        # Shipping state rule
        if rule["shipping_state"] and rule["shipping_state"] != ship_state:
            match = False
        # Tax category rule
        if rule["tax_category_id"] and args.tax_category_id != rule["tax_category_id"]:
            match = False

        if match:
            best_template_id = rule["tax_template_id"]
            best_template_name = rule["template_name"]
            break

    # Fallback to company default
    if not best_template_id:
        q_def = (
            Q.from_(tt_t)
            .select(tt_t.id, tt_t.name)
            .where(tt_t.company_id == P())
            .where(tt_t.is_default == 1)
            .where((tt_t.tax_type == P()) | (tt_t.tax_type == "both"))
            .limit(1)
        )
        default = conn.execute(q_def.get_sql(), (company_id, tx_type)).fetchone()
        if default:
            best_template_id = default["id"]
            best_template_name = default["name"]

    # Check item-level overrides
    item_overrides = []
    if best_template_id:
        q_ovr = Q.from_(itt_t).select(itt_t.item_id, itt_t.tax_template_id)
        overrides = conn.execute(q_ovr.get_sql()).fetchall()
        item_overrides = [row_to_dict(o) for o in overrides
                          if o["tax_template_id"] != best_template_id]

    ok({
        "tax_template_id": best_template_id,
        "template_name": best_template_name,
        "is_exempt": is_exempt,
        "item_overrides": item_overrides,
    })


def calculate_tax(conn, args):
    """Pure calculation — no database writes."""
    if not args.tax_template_id:
        err("--tax-template-id is required")

    items = _parse_json_arg(args.items, "items")
    if not items or not isinstance(items, list):
        err("--items must be a non-empty JSON array")

    # Fetch template lines
    lines = _get_template_lines(conn, args.tax_template_id)
    if not lines:
        err(f"No template lines found for template: {args.tax_template_id}")

    # Parse item overrides
    item_overrides = _parse_json_arg(args.item_overrides, "item-overrides") if args.item_overrides else None
    override_map = {}
    if item_overrides:
        for o in item_overrides:
            override_map[o["item_id"]] = o.get("override_template_id")

    # Calculate net total
    net_total = Decimal("0")
    per_item = []
    for item in items:
        net_amt = to_decimal(str(item.get("net_amount", "0")))
        net_total += net_amt
        per_item.append({"item_id": item.get("item_id"), "net_amount": net_amt,
                         "tax_amount": Decimal("0")})

    # Calculate tax per line (cascading)
    tax_lines = []
    running_total = net_total
    total_tax = Decimal("0")
    prev_row_amount = Decimal("0")
    prev_row_total = Decimal("0")

    for tl in lines:
        rate = to_decimal(tl["rate"])
        charge_type = tl["charge_type"]
        add_deduct = tl["add_deduct"]

        # Determine base amount
        if charge_type == "on_net_total":
            base = net_total
        elif charge_type == "on_previous_row_total":
            base = prev_row_total if prev_row_total else net_total
        elif charge_type == "on_previous_row_amount":
            base = prev_row_amount
        elif charge_type == "actual":
            base = rate  # For 'actual', rate IS the amount
            rate = Decimal("0")
        elif charge_type == "on_item_quantity":
            total_qty = sum(to_decimal(str(item.get("qty", "1"))) for item in items)
            base = total_qty
        else:
            base = net_total

        # Calculate tax amount
        if charge_type == "actual":
            tax_amount = round_currency(base)
        else:
            tax_amount = round_currency(base * rate / Decimal("100"))

        if add_deduct == "deduct":
            tax_amount = -tax_amount

        # Distribute proportionally to items (skip overridden items)
        for pi in per_item:
            if pi["item_id"] in override_map:
                continue
            if net_total > 0:
                item_share = round_currency(tax_amount * pi["net_amount"] / net_total)
            else:
                item_share = Decimal("0")
            pi["tax_amount"] += item_share

        tax_lines.append({
            "tax_account_id": tl["tax_account_id"],
            "account_name": tl.get("account_name", ""),
            "description": tl.get("description", ""),
            "rate": str(tl["rate"]),
            "amount": str(round_currency(tax_amount)),
        })

        prev_row_amount = abs(tax_amount)
        total_tax += tax_amount
        prev_row_total = net_total + total_tax
        running_total = prev_row_total

    ok({
        "tax_lines": tax_lines,
        "total_tax": str(round_currency(total_tax)),
        "net_total": str(round_currency(net_total)),
        "grand_total": str(round_currency(net_total + total_tax)),
        "per_item_tax": [
            {"item_id": pi["item_id"], "tax_amount": str(round_currency(pi["tax_amount"]))}
            for pi in per_item
        ],
    })


# ---------------------------------------------------------------------------
# Item Tax Template
# ---------------------------------------------------------------------------

def add_item_tax_template(conn, args):
    if not args.item_id:
        err("--item-id is required")
    if not args.tax_template_id:
        err("--tax-template-id is required")

    # Verify template exists
    q_chk = Q.from_(tt_t).select(tt_t.id).where(tt_t.id == P())
    t = conn.execute(q_chk.get_sql(), (args.tax_template_id,)).fetchone()
    if not t:
        err(f"Tax template not found: {args.tax_template_id}")

    iid = str(uuid.uuid4())
    q = Q.into(itt_t).columns("id", "item_id", "tax_template_id", "tax_rate").insert(P(), P(), P(), P())
    conn.execute(q.get_sql(), (iid, args.item_id, args.tax_template_id, args.tax_rate))
    audit(conn, "erpclaw-tax", "add-item-tax-template", "item_tax_template", iid,
           new_values={"item_id": args.item_id, "tax_template_id": args.tax_template_id})
    conn.commit()
    ok({"status": "created", "item_tax_template_id": iid})


# ---------------------------------------------------------------------------
# Tax Withholding
# ---------------------------------------------------------------------------

def add_tax_withholding_category(conn, args):
    if not args.name:
        err("--name is required")
    if not args.wh_rate:
        err("--rate is required")
    if not args.threshold_amount:
        err("--threshold-amount is required")
    if not args.form_type or args.form_type not in VALID_FORM_TYPES:
        err(f"--form-type must be one of: {', '.join(VALID_FORM_TYPES)}")
    if not args.company_id:
        err("--company-id is required")

    try:
        to_decimal(args.wh_rate)
        to_decimal(args.threshold_amount)
    except (InvalidOperation, ValueError):
        err("Invalid decimal for --rate or --threshold-amount")

    cid = str(uuid.uuid4())
    q_cat = (
        Q.into(twc_t)
        .columns("id", "name", "category_code", "cumulative_threshold", "company_id")
        .insert(P(), P(), P(), P(), P())
    )
    conn.execute(q_cat.get_sql(),
        (cid, args.name, args.form_type, args.threshold_amount, args.company_id))

    # Create a default withholding group with the provided rate
    gid = str(uuid.uuid4())
    # Find a withholding account — use first liability account
    q_acct = (
        Q.from_(acct_t).select(acct_t.id)
        .where(acct_t.account_type.isin(["tax", "payable"]))
        .where(acct_t.company_id == P())
        .limit(1)
    )
    wh_acct = conn.execute(q_acct.get_sql(), (args.company_id,)).fetchone()
    wh_account_id = wh_acct["id"] if wh_acct else None

    if wh_account_id:
        q_grp = (
            Q.into(twg_t)
            .columns("id", "category_id", "group_name", "rate", "effective_from", "account_id")
            .insert(P(), P(), P(), P(), P(), P())
        )
        conn.execute(q_grp.get_sql(),
            (gid, cid, "Default", args.wh_rate, "2020-01-01", wh_account_id))

    audit(conn, "erpclaw-tax", "add-tax-withholding-category", "tax_withholding_category", cid,
           new_values={"name": args.name, "form_type": args.form_type})
    conn.commit()
    ok({"status": "created", "category_id": cid, "name": args.name})


def get_withholding_details(conn, args):
    """Aggregate withholding info for a supplier in a tax year."""
    if not args.supplier_id:
        err("--supplier-id is required")
    if not args.tax_year:
        err("--tax-year is required")
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    # Check supplier
    q_sup = Q.from_(supp_t).select(supp_t.star).where(supp_t.id == P())
    _sup = conn.execute(q_sup.get_sql(), (args.supplier_id,)).fetchone()
    if not _sup:
        err(f"Supplier not found: {args.supplier_id}")
    supplier = row_to_dict(_sup)

    is_1099 = bool(supplier.get("is_1099_vendor"))
    w9_on_file = bool(supplier.get("w9_on_file"))

    # Find withholding category for this supplier
    wh_cat = None
    wh_rate = Decimal("0")
    threshold = Decimal("0")
    cat_name = ""

    if supplier.get("tax_withholding_category_id"):
        q_cat = Q.from_(twc_t).select(twc_t.star).where(twc_t.id == P())
        wh_cat = conn.execute(q_cat.get_sql(),
            (supplier["tax_withholding_category_id"],)).fetchone()
        if wh_cat:
            cat_name = wh_cat["name"]
            threshold = to_decimal(wh_cat["cumulative_threshold"] or "0")
            # Get current rate from group
            q_grp = (
                Q.from_(twg_t).select(twg_t.rate)
                .where(twg_t.category_id == P())
                .orderby(twg_t.effective_from, order=Order.desc)
                .limit(1)
            )
            grp = conn.execute(q_grp.get_sql(), (wh_cat["id"],)).fetchone()
            if grp:
                wh_rate = to_decimal(grp["rate"])

    # Get YTD payments
    q_ytd = (
        Q.from_(twe_t)
        .select(fn.Coalesce(DecimalSum(twe_t.taxable_amount), ValueWrapper("0")).as_("total"))
        .where(twe_t.party_type == "supplier")
        .where(twe_t.party_id == P())
        .where(twe_t.fiscal_year == P())
    )
    ytd = conn.execute(q_ytd.get_sql(), (args.supplier_id, args.tax_year)).fetchone()
    ytd_payments = round_currency(to_decimal(str(ytd["total"])))

    threshold_exceeded = ytd_payments >= threshold if threshold > 0 else False

    # Determine effective withholding
    backup_rate = Decimal("24.0") if not w9_on_file and is_1099 else Decimal("0")
    withholding_amount = Decimal("0")
    if not w9_on_file and is_1099:
        withholding_amount = round_currency(ytd_payments * backup_rate / Decimal("100"))

    ok({
        "is_1099_vendor": is_1099,
        "withholding_category": cat_name,
        "ytd_payments": str(ytd_payments),
        "threshold_exceeded": threshold_exceeded,
        "withholding_rate": str(wh_rate),
        "backup_withholding_rate": str(backup_rate),
        "w9_on_file": w9_on_file,
        "withholding_amount": str(round_currency(withholding_amount)),
    })


def record_withholding_entry(conn, args):
    if not args.supplier_id:
        err("--supplier-id is required")
    if not args.voucher_type:
        err("--voucher-type is required")
    if not args.voucher_id:
        err("--voucher-id is required")
    if not args.withholding_amount:
        err("--withholding-amount is required")
    if not args.tax_year:
        err("--tax-year is required")

    # Find withholding category for supplier
    q_sup = Q.from_(supp_t).select(supp_t.star).where(supp_t.id == P())
    _sup = conn.execute(q_sup.get_sql(), (args.supplier_id,)).fetchone()
    if not _sup:
        err(f"Supplier not found: {args.supplier_id}")
    supplier = row_to_dict(_sup)

    cat_id = supplier.get("tax_withholding_category_id")
    if not cat_id:
        err("Supplier has no withholding category assigned")

    eid = str(uuid.uuid4())
    q = (
        Q.into(twe_t)
        .columns("id", "party_type", "party_id", "category_id", "fiscal_year",
                 "taxable_amount", "withheld_amount",
                 "withholding_voucher_type", "withholding_voucher_id")
        .insert(P(), "supplier", P(), P(), P(), "0", P(), P(), P())
    )
    conn.execute(q.get_sql(),
        (eid, args.supplier_id, cat_id, args.tax_year,
         args.withholding_amount, args.voucher_type, args.voucher_id))
    audit(conn, "erpclaw-tax", "record-withholding-entry", "tax_withholding_entry", eid,
           new_values={"supplier_id": args.supplier_id, "amount": args.withholding_amount})
    conn.commit()
    ok({"status": "created", "withholding_entry_id": eid})


def record_1099_payment(conn, args):
    if not args.supplier_id:
        err("--supplier-id is required")
    if not args.ple_amount:
        err("--amount is required")
    if not args.tax_year:
        err("--tax-year is required")
    if not args.voucher_type:
        err("--voucher-type is required")
    if not args.voucher_id:
        err("--voucher-id is required")

    q_sup = Q.from_(supp_t).select(supp_t.star).where(supp_t.id == P())
    _sup = conn.execute(q_sup.get_sql(), (args.supplier_id,)).fetchone()
    if not _sup:
        err(f"Supplier not found: {args.supplier_id}")
    supplier = row_to_dict(_sup)

    cat_id = supplier.get("tax_withholding_category_id")
    if not cat_id:
        err("Supplier has no withholding category assigned")

    eid = str(uuid.uuid4())
    q = (
        Q.into(twe_t)
        .columns("id", "party_type", "party_id", "category_id", "fiscal_year",
                 "taxable_amount", "withheld_amount",
                 "taxable_voucher_type", "taxable_voucher_id")
        .insert(P(), "supplier", P(), P(), P(), P(), "0", P(), P())
    )
    conn.execute(q.get_sql(),
        (eid, args.supplier_id, cat_id, args.tax_year,
         args.ple_amount, args.voucher_type, args.voucher_id))

    # Get YTD total
    q_ytd = (
        Q.from_(twe_t)
        .select(fn.Coalesce(DecimalSum(twe_t.taxable_amount), ValueWrapper("0")).as_("total"))
        .where(twe_t.party_type == "supplier")
        .where(twe_t.party_id == P())
        .where(twe_t.fiscal_year == P())
    )
    ytd = conn.execute(q_ytd.get_sql(), (args.supplier_id, args.tax_year)).fetchone()

    audit(conn, "erpclaw-tax", "record-1099-payment", "tax_withholding_entry", eid,
           new_values={"supplier_id": args.supplier_id, "amount": args.ple_amount})
    conn.commit()
    ok({"status": "created", "ytd_1099_total": str(round_currency(to_decimal(str(ytd["total"]))))})


def generate_1099_data(conn, args):
    if not args.tax_year:
        err("--tax-year is required")
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    # Get all withholding categories for this company
    q_cats = Q.from_(twc_t).select(twc_t.star).where(twc_t.company_id == P())
    cats = conn.execute(q_cats.get_sql(), (company_id,)).fetchall()
    cat_map = {c["id"]: row_to_dict(c) for c in cats}

    # Get all suppliers with 1099 entries for the year (IN subquery — keep raw SQL)
    entries = conn.execute(
        """SELECT party_id, category_id,
                  decimal_sum(taxable_amount) as total_paid
           FROM tax_withholding_entry
           WHERE party_type = 'supplier' AND fiscal_year = ?
             AND category_id IN (SELECT id FROM tax_withholding_category WHERE company_id = ?)
           GROUP BY party_id, category_id""",
        (args.tax_year, company_id),
    ).fetchall()

    vendors = []
    q_sup_info = Q.from_(supp_t).select(supp_t.id, supp_t.name, supp_t.tax_id).where(supp_t.id == P())
    sup_info_sql = q_sup_info.get_sql()
    for entry in entries:
        cat = cat_map.get(entry["category_id"])
        if not cat:
            continue
        threshold = to_decimal(cat.get("cumulative_threshold") or "0")
        total = to_decimal(str(entry["total_paid"]))
        if total < threshold:
            continue

        _sup = conn.execute(sup_info_sql, (entry["party_id"],)).fetchone()
        if not _sup:
            continue
        supplier = row_to_dict(_sup)

        form_type = cat.get("category_code") or "1099-NEC"
        vendors.append({
            "supplier_id": supplier["id"],
            "name": supplier["name"],
            "tin": supplier.get("tax_id") or "",
            "total_paid": str(round_currency(total)),
            "form_type": form_type,
            "box_1": str(round_currency(total)) if form_type == "1099-NEC" else "0.00",
        })

    ok({"vendors": vendors})


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    q_tt = Q.from_(tt_t).select(fn.Count("*").as_("cnt")).where(tt_t.company_id == P())
    templates = conn.execute(q_tt.get_sql(), (company_id,)).fetchone()["cnt"]
    q_tr = Q.from_(tr_t).select(fn.Count("*").as_("cnt")).where(tr_t.company_id == P())
    rules = conn.execute(q_tr.get_sql(), (company_id,)).fetchone()["cnt"]
    q_wc = Q.from_(twc_t).select(fn.Count("*").as_("cnt")).where(twc_t.company_id == P())
    wh_cats = conn.execute(q_wc.get_sql(), (company_id,)).fetchone()["cnt"]

    # Count distinct 1099 vendors for current year (IN subquery — keep raw SQL)
    year = str(datetime.now(timezone.utc).year)
    vendors = conn.execute(
        """SELECT COUNT(DISTINCT party_id) as cnt
           FROM tax_withholding_entry
           WHERE fiscal_year = ?
             AND category_id IN (SELECT id FROM tax_withholding_category WHERE company_id = ?)""",
        (year, company_id),
    ).fetchone()["cnt"]

    ok({
        "templates": templates,
        "rules": rules,
        "withholding_categories": wh_cats,
        "ytd_1099_vendors": vendors,
    })


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-tax-template": add_tax_template,
    "update-tax-template": update_tax_template,
    "get-tax-template": get_tax_template,
    "list-tax-templates": list_tax_templates,
    "delete-tax-template": delete_tax_template,
    "resolve-tax-template": resolve_tax_template,
    "calculate-tax": calculate_tax,
    "add-tax-category": add_tax_category,
    "list-tax-categories": list_tax_categories,
    "add-tax-rule": add_tax_rule,
    "list-tax-rules": list_tax_rules,
    "add-item-tax-template": add_item_tax_template,
    "add-tax-withholding-category": add_tax_withholding_category,
    "get-withholding-details": get_withholding_details,
    "record-withholding-entry": record_withholding_entry,
    "record-1099-payment": record_1099_payment,
    "generate-1099-data": generate_1099_data,
    "status": status_action,
}


def main():
    parser = argparse.ArgumentParser(description="ERPClaw Tax Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Tax template
    parser.add_argument("--tax-template-id")
    parser.add_argument("--name")
    parser.add_argument("--tax-type")
    parser.add_argument("--is-default", action="store_true", default=None)
    parser.add_argument("--lines")  # JSON string
    parser.add_argument("--description")

    # Tax category
    parser.add_argument("--tax-category-id")

    # Tax rule
    parser.add_argument("--priority", type=int, default=None)
    parser.add_argument("--customer-id")
    parser.add_argument("--customer-group")
    parser.add_argument("--supplier-id")
    parser.add_argument("--shipping-state")

    # Resolve
    parser.add_argument("--party-type")
    parser.add_argument("--party-id")
    parser.add_argument("--company-id")
    parser.add_argument("--transaction-type")
    parser.add_argument("--shipping-address")  # JSON string

    # Calculate
    parser.add_argument("--items")  # JSON string
    parser.add_argument("--item-overrides")  # JSON string

    # Item tax template
    parser.add_argument("--item-id")
    parser.add_argument("--tax-rate")

    # Withholding
    parser.add_argument("--rate", dest="wh_rate")
    parser.add_argument("--threshold-amount")
    parser.add_argument("--form-type")
    parser.add_argument("--tax-year")
    parser.add_argument("--withholding-amount")
    parser.add_argument("--voucher-type")
    parser.add_argument("--voucher-id")

    # 1099
    parser.add_argument("--amount", dest="ple_amount")

    # Common
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
    finally:
        conn.close()


if __name__ == "__main__":
    main()
