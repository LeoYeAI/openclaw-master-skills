#!/usr/bin/env python3
"""ERPClaw GL Skill — db_query.py

General Ledger operations: chart of accounts, GL entries, fiscal years,
cost centers, budgets, naming series.

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
    from erpclaw_lib.decimal_utils import to_decimal
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.gl_posting import (
        validate_gl_entries,
        insert_gl_entries,
        reverse_gl_entries,
        get_account_balance as _lib_get_account_balance,
    )
    from erpclaw_lib.naming import get_next_name, ENTITY_PREFIXES
    from erpclaw_lib.fx_posting import get_exchange_rate, convert_to_base
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query_helpers import resolve_company_id
    from erpclaw_lib.query import Q, P, Table, Field, fn, Case, Order, Criterion, Not, NULL, DecimalSum, DecimalAbs, dynamic_update, now
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company"]

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
CHARTS_DIR = os.path.join(ASSETS_DIR, "charts")



# ---------------------------------------------------------------------------
# 1. setup-chart-of-accounts
# ---------------------------------------------------------------------------

def setup_chart_of_accounts(conn, args):
    template = args.template or "us_gaap"
    company_id = args.company_id
    if not company_id:
        # Auto-detect if only one company exists
        t_c = Table("company")
        q_c = Q.from_(t_c).select(t_c.id, t_c.name)
        companies = conn.execute(q_c.get_sql()).fetchall()
        if len(companies) == 1:
            company_id = companies[0]["id"]
        elif len(companies) > 1:
            company_list = ", ".join([f"'{c['name']}' ({c['id'][:8]}...)" for c in companies])
            err(f"Multiple companies found. Please specify --company-id. Available: {company_list}")
        else:
            err("No companies found. Create a company first with setup-company.")

    t_company = Table("company")
    t_account = Table("account")

    q = Q.from_(t_company).select(t_company.id).where(t_company.id == P())
    company = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not company:
        err(f"Company {company_id} not found")

    chart_path = os.path.join(CHARTS_DIR, f"{template}.json")
    if not os.path.exists(chart_path):
        err(f"Chart template '{template}' not found. Expected at assets/charts/{template}.json")

    with open(chart_path) as f:
        accounts = json.load(f)

    # Build account_number -> id map for parent resolution
    number_to_id = {}
    # Check existing accounts to skip duplicates
    existing = set()
    q = Q.from_(t_account).select(t_account.account_number).where(t_account.company_id == P())
    for row in conn.execute(q.get_sql(), (company_id,)).fetchall():
        existing.add(row["account_number"])

    created = 0
    for acct in accounts:
        acct_num = acct["account_number"]
        if acct_num in existing:
            # Already exists, but still need to map number -> id
            q = (Q.from_(t_account).select(t_account.id)
                 .where(t_account.account_number == P())
                 .where(t_account.company_id == P()))
            row = conn.execute(q.get_sql(), (acct_num, company_id)).fetchone()
            if row:
                number_to_id[acct_num] = row["id"]
            continue

        acct_id = str(uuid.uuid4())
        parent_id = None
        if acct.get("parent_number"):
            parent_id = number_to_id.get(acct["parent_number"])

        # Calculate depth from parent
        depth = 0
        if parent_id:
            q = Q.from_(t_account).select(t_account.depth).where(t_account.id == P())
            parent_row = conn.execute(q.get_sql(), (parent_id,)).fetchone()
            if parent_row:
                depth = parent_row["depth"] + 1

        q = (Q.into(t_account)
             .columns("id", "name", "account_number", "parent_id", "root_type",
                       "account_type", "is_group", "balance_direction", "company_id", "depth")
             .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
        conn.execute(q.get_sql(),
            (acct_id, acct["name"], acct_num, parent_id, acct["root_type"],
             acct.get("account_type"), acct.get("is_group", 0),
             acct.get("balance_direction", "debit_normal"), company_id, depth),
        )
        number_to_id[acct_num] = acct_id
        created += 1

    audit(conn, "erpclaw-gl", "import", "account", company_id,
           new_values={"template": template, "accounts_created": created})
    conn.commit()
    ok({"accounts_created": created, "template": template, "company_id": company_id})


# ---------------------------------------------------------------------------
# 2. add-account
# ---------------------------------------------------------------------------

def add_account(conn, args):
    name = args.name
    company_id = args.company_id
    if not name:
        err("--name is required")
    if not company_id:
        err("--company-id is required")

    root_type = args.root_type
    if not root_type:
        err("--root-type is required (asset|liability|equity|income|expense)")

    acct_id = str(uuid.uuid4())
    account_type = args.account_type
    account_number = args.account_number
    parent_id = args.parent_id
    currency = args.currency or "USD"
    is_group = 1 if args.is_group else 0

    # Guard: certain account_types must be leaf (posting) accounts, never groups
    LEAF_ONLY_TYPES = {
        "receivable", "payable", "bank", "cash", "tax",
        "cost_of_goods_sold", "stock", "depreciation",
        "accumulated_depreciation", "round_off",
    }
    if is_group and account_type and account_type.lower() in LEAF_ONLY_TYPES:
        err(f"Account type '{account_type}' must be a posting (leaf) account, "
            f"not a group. Remove --is-group to create a postable account.")

    # Default balance direction
    balance_direction = "debit_normal"
    if root_type in ("liability", "equity", "income"):
        balance_direction = "credit_normal"

    t_account = Table("account")

    depth = 0
    if parent_id:
        q = Q.from_(t_account).select(t_account.depth).where(t_account.id == P())
        parent_row = conn.execute(q.get_sql(), (parent_id,)).fetchone()
        if not parent_row:
            err(f"Parent account {parent_id} not found")
        depth = parent_row["depth"] + 1

    try:
        q = (Q.into(t_account)
             .columns("id", "name", "account_number", "parent_id", "root_type",
                       "account_type", "currency", "is_group", "balance_direction",
                       "company_id", "depth")
             .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
        conn.execute(q.get_sql(),
            (acct_id, name, account_number, parent_id, root_type,
             account_type, currency, is_group, balance_direction, company_id, depth),
        )
        audit(conn, "erpclaw-gl", "create", "account", acct_id,
               new_values={"name": name, "root_type": root_type, "account_type": account_type})
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-gl] {e}\n")
        err("Account creation failed — check for duplicates or invalid data")

    ok({"status": "created", "account_id": acct_id, "name": name,
         "account_number": account_number})


# ---------------------------------------------------------------------------
# 3. update-account
# ---------------------------------------------------------------------------

def update_account(conn, args):
    acct_id = args.account_id
    if not acct_id:
        err("--account-id is required")

    t_account = Table("account")
    t_gl = Table("gl_entry")

    q = Q.from_(t_account).select(t_account.star).where(t_account.id == P())
    old = row_to_dict(conn.execute(q.get_sql(), (acct_id,)).fetchone())
    if not old:
        err(f"Account {acct_id} not found",
             suggestion="Use 'list accounts' to see available accounts.")

    # Check if GL entries exist (restricts root_type/account_type changes)
    q = (Q.from_(t_gl).select(ValueWrapper(1))
         .where(t_gl.account_id == P())
         .where(t_gl.is_cancelled == 0)
         .limit(1))
    has_entries = conn.execute(q.get_sql(), (acct_id,)).fetchone()

    updatable = {"name": args.name, "account_number": args.account_number,
                 "parent_id": args.parent_id}
    # is_frozen handled by freeze/unfreeze actions, but allow via update too
    if args.is_frozen is not None:
        updatable["is_frozen"] = 1 if args.is_frozen else 0

    updates = {k: v for k, v in updatable.items() if v is not None}
    if not updates:
        err("No fields to update")

    data = dict(updates)
    data["updated_at"] = now()
    sql, values = dynamic_update("account", data, where={"id": acct_id})
    conn.execute(sql, values)

    audit(conn, "erpclaw-gl", "update", "account", acct_id,
           old_values={k: old.get(k) for k in updates},
           new_values=updates)
    conn.commit()
    ok({"status": "updated", "account_id": acct_id,
         "updated_fields": list(updates.keys())})


# ---------------------------------------------------------------------------
# 4. list-accounts
# ---------------------------------------------------------------------------

def list_accounts(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    limit_val = int(args.limit or 20)
    offset_val = int(args.offset or 0)

    t = Table("account")
    q = Q.from_(t).select(t.star).where(t.company_id == P())
    params = [company_id]

    if args.root_type:
        q = q.where(t.root_type == P())
        params.append(args.root_type)
    if args.account_type:
        q = q.where(t.account_type == P())
        params.append(args.account_type)
    if args.is_group:
        q = q.where(t.is_group == 1)
    if args.parent_id:
        q = q.where(t.parent_id == P())
        params.append(args.parent_id)
    if args.search:
        q = q.where(
            Criterion.any([t.name.like(P()), t.account_number.like(P())])
        )
        params.extend([f"%{args.search}%", f"%{args.search}%"])
    if not args.include_frozen:
        q = q.where(t.is_frozen == 0).where(t.disabled == 0)

    count_sql = q.get_sql().replace("SELECT *", 'SELECT COUNT(*) "cnt"', 1)
    total_count = conn.execute(count_sql, params).fetchone()["cnt"]

    q = q.orderby(t.account_number).orderby(t.name).limit(P()).offset(P())
    params.extend([limit_val, offset_val])
    rows = conn.execute(q.get_sql(), params).fetchall()
    ok({"accounts": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit_val, "offset": offset_val,
         "has_more": offset_val + limit_val < total_count})


# ---------------------------------------------------------------------------
# 5. get-account
# ---------------------------------------------------------------------------

def get_account(conn, args):
    acct_id = args.account_id
    if not acct_id:
        err("--account-id is required")

    t_account = Table("account")
    t_gl = Table("gl_entry")

    q = Q.from_(t_account).select(t_account.star).where(t_account.id == P())
    row = conn.execute(q.get_sql(), (acct_id,)).fetchone()
    if not row:
        err(f"Account {acct_id} not found",
             suggestion="Use 'list accounts' to see available accounts.")

    acct = row_to_dict(row)

    # Include balance
    as_of = args.as_of_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    q = (Q.from_(t_gl)
         .select(fn.Coalesce(DecimalSum(t_gl.debit), ValueWrapper("0")).as_("debit_total"),
                 fn.Coalesce(DecimalSum(t_gl.credit), ValueWrapper("0")).as_("credit_total"))
         .where(t_gl.account_id == P())
         .where(t_gl.posting_date <= P())
         .where(t_gl.is_cancelled == 0))
    bal = conn.execute(q.get_sql(), (acct_id, as_of)).fetchone()

    debit_total = Decimal(str(bal["debit_total"]))
    credit_total = Decimal(str(bal["credit_total"]))
    if acct["balance_direction"] == "debit_normal":
        balance = debit_total - credit_total
    else:
        balance = credit_total - debit_total

    acct["balance"] = str(balance)
    acct["debit_total"] = str(debit_total)
    acct["credit_total"] = str(credit_total)

    ok({"account": acct})


# ---------------------------------------------------------------------------
# 6-7. freeze-account / unfreeze-account
# ---------------------------------------------------------------------------

def freeze_account(conn, args):
    acct_id = args.account_id
    if not acct_id:
        err("--account-id is required")
    t = Table("account")
    q = Q.from_(t).select(t.id).where(t.id == P())
    row = conn.execute(q.get_sql(), (acct_id,)).fetchone()
    if not row:
        err(f"Account {acct_id} not found")
    q = (Q.update(t)
         .set(Field("is_frozen"), 1)
         .set(Field("updated_at"), now())
         .where(t.id == P()))
    conn.execute(q.get_sql(), (acct_id,))
    audit(conn, "erpclaw-gl", "freeze", "account", acct_id, new_values={"is_frozen": 1})
    conn.commit()
    ok({"status": "updated", "account_id": acct_id, "is_frozen": True})


def unfreeze_account(conn, args):
    acct_id = args.account_id
    if not acct_id:
        err("--account-id is required")
    t = Table("account")
    q = Q.from_(t).select(t.id).where(t.id == P())
    row = conn.execute(q.get_sql(), (acct_id,)).fetchone()
    if not row:
        err(f"Account {acct_id} not found")
    q = (Q.update(t)
         .set(Field("is_frozen"), 0)
         .set(Field("updated_at"), now())
         .where(t.id == P()))
    conn.execute(q.get_sql(), (acct_id,))
    audit(conn, "erpclaw-gl", "unfreeze", "account", acct_id, new_values={"is_frozen": 0})
    conn.commit()
    ok({"status": "updated", "account_id": acct_id, "is_frozen": False})


# ---------------------------------------------------------------------------
# 8. post-gl-entries
# ---------------------------------------------------------------------------

def post_gl_entries(conn, args):
    voucher_type = args.voucher_type
    voucher_id = args.voucher_id
    posting_date = args.posting_date
    company_id = args.company_id
    entries_json = args.entries

    if not all([voucher_type, voucher_id, posting_date, company_id, entries_json]):
        err("--voucher-type, --voucher-id, --posting-date, --company-id, --entries are required")

    try:
        entries = json.loads(entries_json)
    except (json.JSONDecodeError, TypeError):
        err("--entries must be valid JSON array")

    if not isinstance(entries, list) or len(entries) == 0:
        err("--entries must be a non-empty JSON array")

    # Validate via shared lib (raises ValueError on failure)
    try:
        warnings = validate_gl_entries(conn, entries, company_id, posting_date)
    except ValueError as e:
        err(str(e))

    # Insert via shared lib
    try:
        gl_ids = insert_gl_entries(conn, entries, voucher_type, voucher_id,
                                   posting_date, company_id)
    except ValueError as e:
        err(str(e))

    audit(conn, "erpclaw-gl", "post", "gl_entry", voucher_id,
           new_values={"voucher_type": voucher_type, "entries_created": len(gl_ids)})
    conn.commit()

    ok({"status": "created", "gl_entry_ids": gl_ids, "entries_created": len(gl_ids),
         "warnings": warnings})


# ---------------------------------------------------------------------------
# 9. reverse-gl-entries
# ---------------------------------------------------------------------------

def reverse_gl_entries_action(conn, args):
    voucher_type = args.voucher_type
    voucher_id = args.voucher_id
    posting_date = args.posting_date

    if not voucher_type or not voucher_id:
        err("--voucher-type and --voucher-id are required")

    posting_date = posting_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        reversal_ids = reverse_gl_entries(conn, voucher_type, voucher_id, posting_date)
    except ValueError as e:
        err(str(e))

    audit(conn, "erpclaw-gl", "reverse", "gl_entry", voucher_id,
           new_values={"voucher_type": voucher_type, "reversed_count": len(reversal_ids)})
    conn.commit()

    ok({"reversed_count": len(reversal_ids), "reversal_entry_ids": reversal_ids})


# ---------------------------------------------------------------------------
# 10. list-gl-entries
# ---------------------------------------------------------------------------

def list_gl_entries(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    g = Table("gl_entry").as_("g")
    a = Table("account").as_("a")

    q = (Q.from_(g).join(a).on(g.account_id == a.id)
         .select(g.star, a.name.as_("account_name")))
    params = []

    if company_id:
        q = q.where(a.company_id == P())
        params.append(company_id)
    if args.account_id:
        q = q.where(g.account_id == P())
        params.append(args.account_id)
    if args.voucher_type:
        q = q.where(g.voucher_type == P())
        params.append(args.voucher_type)
    if args.voucher_id:
        q = q.where(g.voucher_id == P())
        params.append(args.voucher_id)
    if args.party_type:
        q = q.where(g.party_type == P())
        params.append(args.party_type)
    if args.party_id:
        q = q.where(g.party_id == P())
        params.append(args.party_id)
    if args.from_date:
        q = q.where(g.posting_date >= P())
        params.append(args.from_date)
    if args.to_date:
        q = q.where(g.posting_date <= P())
        params.append(args.to_date)
    if args.is_cancelled is not None:
        q = q.where(g.is_cancelled == P())
        params.append(1 if args.is_cancelled else 0)

    # Count total before limit
    select_sql = q.get_sql()
    # Replace the SELECT columns with COUNT(*)
    from_pos = select_sql.index(" FROM ")
    count_sql = 'SELECT COUNT(*) "cnt"' + select_sql[from_pos:]
    total = conn.execute(count_sql, params).fetchone()["cnt"]

    limit_val = int(args.limit or 100)
    offset_val = int(args.offset or 0)
    q = q.orderby(g.posting_date, order=Order.desc).orderby(g.created_at, order=Order.desc)
    q = q.limit(P()).offset(P())
    params.extend([limit_val, offset_val])

    rows = conn.execute(q.get_sql(), params).fetchall()
    ok({"entries": [row_to_dict(r) for r in rows], "total_count": total,
         "limit": limit_val, "offset": offset_val,
         "has_more": offset_val + limit_val < total})


# ---------------------------------------------------------------------------
# 11. add-fiscal-year
# ---------------------------------------------------------------------------

def add_fiscal_year(conn, args):
    name = args.name
    start_date = args.start_date
    end_date = args.end_date
    company_id = args.company_id

    if not all([name, start_date, end_date, company_id]):
        err("--name, --start-date, --end-date, --company-id are required")

    # Validate no overlap
    t_fy = Table("fiscal_year")
    q = (Q.from_(t_fy).select(t_fy.id, t_fy.name)
         .where(t_fy.company_id == P())
         .where(t_fy.start_date <= P())
         .where(t_fy.end_date >= P()))
    overlap = conn.execute(q.get_sql(), (company_id, end_date, start_date)).fetchone()
    if overlap:
        err(f"Dates overlap with existing fiscal year '{overlap['name']}'")

    fy_id = str(uuid.uuid4())
    try:
        q = (Q.into(t_fy)
             .columns("id", "name", "start_date", "end_date", "company_id")
             .insert(P(), P(), P(), P(), P()))
        conn.execute(q.get_sql(), (fy_id, name, start_date, end_date, company_id))
        audit(conn, "erpclaw-gl", "create", "fiscal_year", fy_id,
               new_values={"name": name, "start_date": start_date, "end_date": end_date})
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-gl] {e}\n")
        err("Fiscal year creation failed — check for duplicates or invalid data")

    ok({"status": "created", "fiscal_year_id": fy_id, "name": name})


# ---------------------------------------------------------------------------
# 12. list-fiscal-years
# ---------------------------------------------------------------------------

def list_fiscal_years(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    limit_val = int(args.limit or 20)
    offset_val = int(args.offset or 0)

    t = Table("fiscal_year")
    q_count = (Q.from_(t).select(fn.Count("*").as_("cnt"))
               .where(t.company_id == P()))
    total_count = conn.execute(q_count.get_sql(), (company_id,)).fetchone()["cnt"]

    q = (Q.from_(t).select(t.star)
         .where(t.company_id == P())
         .orderby(t.start_date, order=Order.desc)
         .limit(P()).offset(P()))
    rows = conn.execute(q.get_sql(), (company_id, limit_val, offset_val)).fetchall()
    ok({"fiscal_years": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit_val, "offset": offset_val,
         "has_more": offset_val + limit_val < total_count})


# ---------------------------------------------------------------------------
# 13. validate-period-close
# ---------------------------------------------------------------------------

def validate_period_close(conn, args):
    fy_id = args.fiscal_year_id
    if not fy_id:
        err("--fiscal-year-id is required")

    t_fy = Table("fiscal_year")
    t_gl = Table("gl_entry").as_("g")
    t_acct = Table("account").as_("a")

    q = Q.from_(t_fy).select(t_fy.star).where(t_fy.id == P())
    fy = row_to_dict(conn.execute(q.get_sql(), (fy_id,)).fetchone())
    if not fy:
        err(f"Fiscal year {fy_id} not found")

    if fy["is_closed"]:
        err(f"Fiscal year '{fy['name']}' is already closed")

    company_id = fy["company_id"]

    # Calculate P&L for the period — raw SQL for expression arithmetic in SELECT
    # raw SQL — SELECT uses column arithmetic (decimal_sum(credit) - decimal_sum(debit))
    income = conn.execute(
        """SELECT COALESCE(decimal_sum(g.credit), '0') - COALESCE(decimal_sum(g.debit), '0') as total
           FROM gl_entry g JOIN account a ON g.account_id = a.id
           WHERE a.root_type = 'income' AND a.company_id = ?
             AND g.posting_date >= ? AND g.posting_date <= ?
             AND g.is_cancelled = 0""",
        (company_id, fy["start_date"], fy["end_date"]),
    ).fetchone()["total"]

    # raw SQL — SELECT uses column arithmetic (decimal_sum(debit) - decimal_sum(credit))
    expense = conn.execute(
        """SELECT COALESCE(decimal_sum(g.debit), '0') - COALESCE(decimal_sum(g.credit), '0') as total
           FROM gl_entry g JOIN account a ON g.account_id = a.id
           WHERE a.root_type = 'expense' AND a.company_id = ?
             AND g.posting_date >= ? AND g.posting_date <= ?
             AND g.is_cancelled = 0""",
        (company_id, fy["start_date"], fy["end_date"]),
    ).fetchone()["total"]

    net_income = Decimal(str(income)) - Decimal(str(expense))

    # Check trial balance
    # raw SQL — COALESCE(decimal_sum(...)) aggregate with JOIN
    totals = conn.execute(
        """SELECT COALESCE(decimal_sum(debit), '0') as total_debit,
                  COALESCE(decimal_sum(credit), '0') as total_credit
           FROM gl_entry g JOIN account a ON g.account_id = a.id
           WHERE a.company_id = ? AND g.is_cancelled = 0""",
        (company_id,),
    ).fetchone()
    balanced = abs(Decimal(str(totals["total_debit"])) - Decimal(str(totals["total_credit"]))) < Decimal("0.01")

    ok({
        "fiscal_year": fy["name"],
        "income_total": str(Decimal(str(income))),
        "expense_total": str(Decimal(str(expense))),
        "net_income": str(net_income),
        "trial_balance_balanced": balanced,
    })


# ---------------------------------------------------------------------------
# 14. close-fiscal-year
# ---------------------------------------------------------------------------

def close_fiscal_year(conn, args):
    fy_id = args.fiscal_year_id
    closing_account_id = args.closing_account_id
    posting_date = args.posting_date

    if not all([fy_id, closing_account_id, posting_date]):
        err("--fiscal-year-id, --closing-account-id, --posting-date are required")

    t_fy = Table("fiscal_year")
    t_account = Table("account")
    t_pcv = Table("period_closing_voucher")

    q = Q.from_(t_fy).select(t_fy.star).where(t_fy.id == P())
    fy = row_to_dict(conn.execute(q.get_sql(), (fy_id,)).fetchone())
    if not fy:
        err(f"Fiscal year {fy_id} not found")
    if fy["is_closed"]:
        err(f"Fiscal year '{fy['name']}' is already closed")

    # Verify closing account exists and is equity type
    q = Q.from_(t_account).select(t_account.star).where(t_account.id == P())
    closing_acct = conn.execute(q.get_sql(), (closing_account_id,)).fetchone()
    if not closing_acct:
        err(f"Closing account {closing_account_id} not found")
    if closing_acct["root_type"] != "equity":
        err("Closing account must be an equity account (retained earnings)")

    company_id = fy["company_id"]

    # raw SQL — SELECT uses column arithmetic (decimal_sum(credit) - decimal_sum(debit))
    income = conn.execute(
        """SELECT COALESCE(decimal_sum(g.credit), '0') - COALESCE(decimal_sum(g.debit), '0')
           FROM gl_entry g JOIN account a ON g.account_id = a.id
           WHERE a.root_type = 'income' AND a.company_id = ?
             AND g.posting_date >= ? AND g.posting_date <= ?
             AND g.is_cancelled = 0""",
        (company_id, fy["start_date"], fy["end_date"]),
    ).fetchone()[0]

    # raw SQL — SELECT uses column arithmetic (decimal_sum(debit) - decimal_sum(credit))
    expense = conn.execute(
        """SELECT COALESCE(decimal_sum(g.debit), '0') - COALESCE(decimal_sum(g.credit), '0')
           FROM gl_entry g JOIN account a ON g.account_id = a.id
           WHERE a.root_type = 'expense' AND a.company_id = ?
             AND g.posting_date >= ? AND g.posting_date <= ?
             AND g.is_cancelled = 0""",
        (company_id, fy["start_date"], fy["end_date"]),
    ).fetchone()[0]

    net_pl = Decimal(str(income)) - Decimal(str(expense))

    # Create period closing voucher
    pcv_id = str(uuid.uuid4())
    q = (Q.into(t_pcv)
         .columns("id", "fiscal_year_id", "posting_date", "closing_account_id",
                   "net_pl_amount", "status", "company_id")
         .insert(P(), P(), P(), P(), P(), ValueWrapper("submitted"), P()))
    conn.execute(q.get_sql(),
        (pcv_id, fy_id, posting_date, closing_account_id, str(net_pl), company_id))

    # Post closing GL entries: net P&L → retained earnings
    entries = []
    if net_pl > 0:
        # Net income: DR Income Summary, CR Retained Earnings
        entries = [
            {"account_id": closing_account_id, "debit": "0", "credit": str(net_pl)},
        ]
        # We need a balancing debit — use a temporary income summary or
        # directly post: DR income accounts, CR retained earnings
        # Simplified: single net entry
        # Find an income account to debit (or use closing account both sides)
        # Actually for period closing: DR P&L = CR Retained Earnings for net income
        # In ERPNext this posts a single pair:
        entries = [
            {"account_id": closing_account_id, "debit": "0", "credit": str(net_pl)},
        ]
        # Need a balancing entry — use income total account or an expense placeholder
        # Simplest correct approach: post the net as a pair
        # DR: Temporary/P&L summary account → CR: Retained Earnings
        # For simplicity, we'll use the closing account itself (debit & credit net to the amount)
        # Actually the standard approach is to zero out all income and expense accounts
        # into retained earnings. Let's do net approach:
        # If net_pl positive (profit): CR retained earnings, DR comes from zeroing income/expense
        # For a simple implementation: one closing entry
        pass
    elif net_pl < 0:
        pass

    # Simple net approach: post a single journal-style pair
    # The closing entry transfers net P&L to retained earnings
    # We need SOME account on the other side. Use a "Period Closing" voucher type.
    # ERPNext creates entries per-account, but our simplified approach:
    # Post entries only if there's a net amount
    gl_entries_created = 0
    if net_pl != 0:
        abs_pl = abs(net_pl)
        # Find any income account for balancing
        if net_pl > 0:
            # Profit: credit retained earnings, need a debit somewhere
            # Standard: debit each income account, credit each expense account → net to RE
            # Simplified: use period_closing voucher_type with closing_account on both sides
            # is wrong. Let's collect income/expense totals per account and close them.
            gl_ids = _close_pl_accounts(conn, company_id, fy, closing_account_id,
                                         pcv_id, posting_date)
            gl_entries_created = len(gl_ids)
        else:
            gl_ids = _close_pl_accounts(conn, company_id, fy, closing_account_id,
                                         pcv_id, posting_date)
            gl_entries_created = len(gl_ids)

    # Close the fiscal year
    q = (Q.update(t_fy)
         .set(Field("is_closed"), 1)
         .set(Field("updated_at"), now())
         .where(t_fy.id == P()))
    conn.execute(q.get_sql(), (fy_id,))

    audit(conn, "erpclaw-gl", "close", "fiscal_year", fy_id,
           new_values={"pcv_id": pcv_id, "net_pl": str(net_pl)})
    conn.commit()

    ok({"status": "submitted", "pcv_id": pcv_id, "net_pl_transferred": str(net_pl),
         "gl_entries_created": gl_entries_created, "fiscal_year_closed": True})


def _close_pl_accounts(conn, company_id, fy, closing_account_id, pcv_id, posting_date):
    """Zero out all income and expense accounts into retained earnings."""
    gl_ids = []

    # raw SQL — LEFT JOIN with conditions, GROUP BY, HAVING with != comparison
    pl_accounts = conn.execute(
        """SELECT a.id, a.root_type,
                  COALESCE(decimal_sum(g.debit), '0') as total_debit,
                  COALESCE(decimal_sum(g.credit), '0') as total_credit
           FROM account a
           LEFT JOIN gl_entry g ON g.account_id = a.id
             AND g.posting_date >= ? AND g.posting_date <= ?
             AND g.is_cancelled = 0
           WHERE a.root_type IN ('income', 'expense') AND a.company_id = ?
             AND a.is_group = 0
           GROUP BY a.id
           HAVING total_debit != 0 OR total_credit != 0""",
        (fy["start_date"], fy["end_date"], company_id),
    ).fetchall()

    t_gl = Table("gl_entry")
    _gl_cols = ("id", "posting_date", "account_id", "debit", "credit",
                "debit_base", "credit_base", "currency", "exchange_rate",
                "fiscal_year", "voucher_type", "voucher_id")
    _gl_insert = (Q.into(t_gl).columns(*_gl_cols)
                  .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), P())
                  .get_sql())

    for acct in pl_accounts:
        net = Decimal(str(acct["total_debit"])) - Decimal(str(acct["total_credit"]))
        if net == 0:
            continue

        entry_id = str(uuid.uuid4())
        re_entry_id = str(uuid.uuid4())

        if acct["root_type"] == "income":
            # Income accounts have credit balance -> debit to zero
            # Income net = credit - debit (positive = credit balance)
            income_net = Decimal(str(acct["total_credit"])) - Decimal(str(acct["total_debit"]))
            if income_net == 0:
                continue
            if income_net > 0:
                # DR income account, CR retained earnings
                conn.execute(_gl_insert,
                    (entry_id, posting_date, acct["id"], str(income_net), "0",
                     str(income_net), "0", "USD", "1", fy["name"], "period_closing", pcv_id))
                conn.execute(_gl_insert,
                    (re_entry_id, posting_date, closing_account_id, "0", str(income_net),
                     "0", str(income_net), "USD", "1", fy["name"], "period_closing", pcv_id))
                gl_ids.extend([entry_id, re_entry_id])
            else:
                # Unusual: income account has debit balance -> credit to zero
                abs_net = abs(income_net)
                conn.execute(_gl_insert,
                    (entry_id, posting_date, acct["id"], "0", str(abs_net),
                     "0", str(abs_net), "USD", "1", fy["name"], "period_closing", pcv_id))
                conn.execute(_gl_insert,
                    (re_entry_id, posting_date, closing_account_id, str(abs_net), "0",
                     str(abs_net), "0", "USD", "1", fy["name"], "period_closing", pcv_id))
                gl_ids.extend([entry_id, re_entry_id])
        else:
            # Expense accounts have debit balance -> credit to zero
            expense_net = Decimal(str(acct["total_debit"])) - Decimal(str(acct["total_credit"]))
            if expense_net == 0:
                continue
            if expense_net > 0:
                # CR expense account, DR retained earnings
                conn.execute(_gl_insert,
                    (entry_id, posting_date, acct["id"], "0", str(expense_net),
                     "0", str(expense_net), "USD", "1", fy["name"], "period_closing", pcv_id))
                conn.execute(_gl_insert,
                    (re_entry_id, posting_date, closing_account_id, str(expense_net), "0",
                     str(expense_net), "0", "USD", "1", fy["name"], "period_closing", pcv_id))
                gl_ids.extend([entry_id, re_entry_id])
            else:
                # Unusual: expense has credit balance
                abs_net = abs(expense_net)
                conn.execute(_gl_insert,
                    (entry_id, posting_date, acct["id"], str(abs_net), "0",
                     str(abs_net), "0", "USD", "1", fy["name"], "period_closing", pcv_id))
                conn.execute(_gl_insert,
                    (re_entry_id, posting_date, closing_account_id, "0", str(abs_net),
                     "0", str(abs_net), "USD", "1", fy["name"], "period_closing", pcv_id))
                gl_ids.extend([entry_id, re_entry_id])

    return gl_ids


# ---------------------------------------------------------------------------
# 15. reopen-fiscal-year
# ---------------------------------------------------------------------------

def reopen_fiscal_year(conn, args):
    fy_id = args.fiscal_year_id
    if not fy_id:
        err("--fiscal-year-id is required")

    t_fy = Table("fiscal_year")
    t_gl = Table("gl_entry")
    t_pcv = Table("period_closing_voucher")

    q = Q.from_(t_fy).select(t_fy.star).where(t_fy.id == P())
    fy = row_to_dict(conn.execute(q.get_sql(), (fy_id,)).fetchone())
    if not fy:
        err(f"Fiscal year {fy_id} not found")
    if not fy["is_closed"]:
        err(f"Fiscal year '{fy['name']}' is not closed")

    # Reverse the period closing voucher entries
    q = (Q.from_(t_pcv).select(t_pcv.id)
         .where(t_pcv.fiscal_year_id == P())
         .where(t_pcv.status == ValueWrapper("submitted")))
    pcv = conn.execute(q.get_sql(), (fy_id,)).fetchone()

    pcv_reversed = False
    if pcv:
        # Cancel all GL entries for this PCV
        q = (Q.update(t_gl)
             .set(Field("is_cancelled"), 1)
             .where(t_gl.voucher_type == ValueWrapper("period_closing"))
             .where(t_gl.voucher_id == P()))
        conn.execute(q.get_sql(), (pcv["id"],))

        q = (Q.update(t_pcv)
             .set(Field("status"), ValueWrapper("cancelled"))
             .set(Field("updated_at"), now())
             .where(t_pcv.id == P()))
        conn.execute(q.get_sql(), (pcv["id"],))
        pcv_reversed = True

    q = (Q.update(t_fy)
         .set(Field("is_closed"), 0)
         .set(Field("updated_at"), now())
         .where(t_fy.id == P()))
    conn.execute(q.get_sql(), (fy_id,))

    audit(conn, "erpclaw-gl", "reopen", "fiscal_year", fy_id,
           new_values={"is_closed": 0, "pcv_reversed": pcv_reversed})
    conn.commit()

    ok({"fiscal_year_id": fy_id, "is_closed": False, "pcv_reversed": pcv_reversed})


# ---------------------------------------------------------------------------
# 16. add-cost-center
# ---------------------------------------------------------------------------

def add_cost_center(conn, args):
    name = args.name
    company_id = args.company_id
    if not name:
        err("--name is required")
    if not company_id:
        err("--company-id is required")

    cc_id = str(uuid.uuid4())
    parent_id = args.parent_id
    is_group = 1 if args.is_group else 0

    t_cc = Table("cost_center")
    try:
        q = (Q.into(t_cc)
             .columns("id", "name", "parent_id", "company_id", "is_group")
             .insert(P(), P(), P(), P(), P()))
        conn.execute(q.get_sql(), (cc_id, name, parent_id, company_id, is_group))
        audit(conn, "erpclaw-gl", "create", "cost_center", cc_id, new_values={"name": name})
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-gl] {e}\n")
        err("Cost center creation failed — check for duplicates or invalid data")

    ok({"status": "created", "cost_center_id": cc_id, "name": name})


# ---------------------------------------------------------------------------
# 17. list-cost-centers
# ---------------------------------------------------------------------------

def list_cost_centers(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    limit_val = int(args.limit or 20)
    offset_val = int(args.offset or 0)

    t = Table("cost_center")
    q = Q.from_(t).select(t.star).where(t.company_id == P())
    params = [company_id]
    if args.parent_id:
        q = q.where(t.parent_id == P())
        params.append(args.parent_id)

    count_sql = q.get_sql().replace("SELECT *", 'SELECT COUNT(*) "cnt"', 1)
    total_count = conn.execute(count_sql, params).fetchone()["cnt"]

    q = q.orderby(t.name).limit(P()).offset(P())
    params.extend([limit_val, offset_val])

    rows = conn.execute(q.get_sql(), params).fetchall()
    ok({"cost_centers": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit_val, "offset": offset_val,
         "has_more": offset_val + limit_val < total_count})


# ---------------------------------------------------------------------------
# 18. add-budget
# ---------------------------------------------------------------------------

def add_budget(conn, args):
    fy_id = args.fiscal_year_id
    budget_amount = args.budget_amount
    if not fy_id:
        err("--fiscal-year-id is required")
    if not budget_amount:
        err("--budget-amount is required")

    account_id = args.account_id
    cost_center_id = args.cost_center_id
    if not account_id and not cost_center_id:
        err("At least one of --account-id or --cost-center-id is required")

    # Get company_id from fiscal year
    t_fy = Table("fiscal_year")
    t_budget = Table("budget")
    q = Q.from_(t_fy).select(t_fy.company_id).where(t_fy.id == P())
    fy = conn.execute(q.get_sql(), (fy_id,)).fetchone()
    if not fy:
        err(f"Fiscal year {fy_id} not found")

    action_if_exceeded = args.action_if_exceeded or "warn"
    budget_id = str(uuid.uuid4())

    try:
        q = (Q.into(t_budget)
             .columns("id", "fiscal_year_id", "account_id", "cost_center_id",
                       "budget_amount", "action_if_exceeded", "company_id")
             .insert(P(), P(), P(), P(), P(), P(), P()))
        conn.execute(q.get_sql(),
            (budget_id, fy_id, account_id, cost_center_id,
             budget_amount, action_if_exceeded, fy["company_id"]))
        audit(conn, "erpclaw-gl", "create", "budget", budget_id,
               new_values={"budget_amount": budget_amount, "action_if_exceeded": action_if_exceeded})
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-gl] {e}\n")
        err("Budget creation failed — check for duplicates or invalid data")

    ok({"status": "created", "budget_id": budget_id})


# ---------------------------------------------------------------------------
# 19. list-budgets
# ---------------------------------------------------------------------------

def list_budgets(conn, args):
    fy_id = args.fiscal_year_id
    if not fy_id:
        err("--fiscal-year-id is required")
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    t_fy = Table("fiscal_year")
    t_budget = Table("budget")

    q = Q.from_(t_fy).select(t_fy.star).where(t_fy.id == P())
    fy = row_to_dict(conn.execute(q.get_sql(), (fy_id,)).fetchone())
    if not fy:
        err(f"Fiscal year {fy_id} not found")

    q_count = (Q.from_(t_budget).select(fn.Count("*").as_("cnt"))
               .where(t_budget.fiscal_year_id == P())
               .where(t_budget.company_id == P()))
    total_count = conn.execute(q_count.get_sql(), (fy_id, company_id)).fetchone()["cnt"]

    q = (Q.from_(t_budget).select(t_budget.star)
         .where(t_budget.fiscal_year_id == P())
         .where(t_budget.company_id == P())
         .limit(P()).offset(P()))
    budgets = conn.execute(q.get_sql(), (fy_id, company_id, limit, offset)).fetchall()

    result = []
    for b in budgets:
        bd = row_to_dict(b)
        # Compute actual from GL
        t_gl = Table("gl_entry").as_("g")
        q_actual = (Q.from_(t_gl)
                    .select(fn.Coalesce(DecimalSum(t_gl.debit), ValueWrapper("0")).as_("total"))
                    .where(t_gl.is_cancelled == 0)
                    .where(t_gl.posting_date >= P())
                    .where(t_gl.posting_date <= P()))
        actual_params = [fy["start_date"], fy["end_date"]]

        if bd["account_id"]:
            q_actual = q_actual.where(t_gl.account_id == P())
            actual_params.append(bd["account_id"])
        if bd["cost_center_id"]:
            q_actual = q_actual.where(t_gl.cost_center_id == P())
            actual_params.append(bd["cost_center_id"])

        actual = Decimal(str(conn.execute(q_actual.get_sql(), actual_params).fetchone()["total"]))
        budget_amt = Decimal(bd["budget_amount"])
        bd["actual_amount"] = str(actual)
        bd["variance"] = str(budget_amt - actual)
        result.append(bd)

    ok({"budgets": result, "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 20. seed-naming-series
# ---------------------------------------------------------------------------

def seed_naming_series(conn, args):
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")

    t_ns = Table("naming_series")

    year = datetime.now(timezone.utc).year
    created = 0
    for entity_type, prefix in ENTITY_PREFIXES.items():
        year_prefix = f"{prefix}{year}-"
        q = (Q.from_(t_ns).select(t_ns.id)
             .where(t_ns.entity_type == P())
             .where(t_ns.prefix == P())
             .where(t_ns.company_id == P()))
        existing = conn.execute(q.get_sql(), (entity_type, year_prefix, company_id)).fetchone()
        if not existing:
            q = (Q.into(t_ns)
                 .columns("id", "entity_type", "prefix", "current_value", "company_id")
                 .insert(P(), P(), P(), 0, P()))
            conn.execute(q.get_sql(), (str(uuid.uuid4()), entity_type, year_prefix, company_id))
            created += 1

    conn.commit()
    ok({"series_created": created, "total_types": len(ENTITY_PREFIXES)})


# ---------------------------------------------------------------------------
# 21. next-series
# ---------------------------------------------------------------------------

def next_series(conn, args):
    entity_type = args.entity_type
    company_id = args.company_id
    if not entity_type:
        err("--entity-type is required")
    if not company_id:
        err("--company-id is required")

    try:
        name = get_next_name(conn, entity_type, company_id=company_id)
        conn.commit()
    except ValueError as e:
        err(str(e))

    ok({"series": name, "entity_type": entity_type})


# ---------------------------------------------------------------------------
# 22. check-gl-integrity
# ---------------------------------------------------------------------------

def check_gl_integrity(conn, args):
    """Verify GL balance and SHA-256 chain integrity for a company."""
    import hashlib

    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    g = Table("gl_entry").as_("g")
    a = Table("account").as_("a")

    # 1. Balance check
    q = (Q.from_(g).join(a).on(g.account_id == a.id)
         .select(fn.Coalesce(DecimalSum(g.debit), ValueWrapper("0")).as_("total_debit"),
                 fn.Coalesce(DecimalSum(g.credit), ValueWrapper("0")).as_("total_credit"))
         .where(a.company_id == P())
         .where(g.is_cancelled == 0))
    totals = conn.execute(q.get_sql(), (company_id,)).fetchone()

    total_debit = Decimal(str(totals["total_debit"]))
    total_credit = Decimal(str(totals["total_credit"]))
    difference = abs(total_debit - total_credit)

    # 2. Chain hash verification
    q = (Q.from_(g).join(a).on(g.account_id == a.id)
         .select(g.posting_date, g.account_id, g.debit, g.credit,
                 g.voucher_type, g.voucher_id, g.gl_checksum)
         .where(a.company_id == P())
         .orderby(g.created_at).orderby(LiteralValue('"g"."rowid"')))
    entries = conn.execute(q.get_sql(), (company_id,)).fetchall()

    chain_intact = True
    broken_links = 0
    total_entries = len(entries)
    prev_hash = "GENESIS"

    for row in entries:
        if not row["gl_checksum"]:
            # Entries created before chain was enabled — skip
            continue

        hash_input = "|".join([
            row["posting_date"],
            row["account_id"],
            str(row["debit"]),
            str(row["credit"]),
            row["voucher_type"],
            row["voucher_id"],
            prev_hash,
        ])
        expected = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        if row["gl_checksum"] != expected:
            chain_intact = False
            broken_links += 1

        prev_hash = row["gl_checksum"]

    ok({
        "balanced": difference < Decimal("0.01"),
        "total_debit": str(total_debit),
        "total_credit": str(total_credit),
        "difference": str(difference),
        "chain_intact": chain_intact,
        "broken_links": broken_links,
        "total_entries": total_entries,
    })


# ---------------------------------------------------------------------------
# 23. get-account-balance
# ---------------------------------------------------------------------------

def get_account_balance_action(conn, args):
    acct_id = args.account_id
    as_of = args.as_of_date
    if not acct_id:
        err("--account-id is required")
    if not as_of:
        err("--as-of-date is required")

    t_account = Table("account")
    t_gl = Table("gl_entry")

    q = Q.from_(t_account).select(t_account.star).where(t_account.id == P())
    acct = conn.execute(q.get_sql(), (acct_id,)).fetchone()
    if not acct:
        err(f"Account {acct_id} not found")

    q = (Q.from_(t_gl)
         .select(fn.Coalesce(DecimalSum(t_gl.debit), ValueWrapper("0")).as_("debit_total"),
                 fn.Coalesce(DecimalSum(t_gl.credit), ValueWrapper("0")).as_("credit_total"))
         .where(t_gl.account_id == P())
         .where(t_gl.posting_date <= P())
         .where(t_gl.is_cancelled == 0))
    params = [acct_id, as_of]

    if args.party_type:
        q = q.where(t_gl.party_type == P())
        params.append(args.party_type)
    if args.party_id:
        q = q.where(t_gl.party_id == P())
        params.append(args.party_id)

    result = conn.execute(q.get_sql(), params).fetchone()
    debit_total = Decimal(str(result["debit_total"]))
    credit_total = Decimal(str(result["credit_total"]))

    if acct["balance_direction"] == "debit_normal":
        balance = debit_total - credit_total
    else:
        balance = credit_total - debit_total

    ok({
        "balance": str(balance),
        "debit_total": str(debit_total),
        "credit_total": str(credit_total),
        "currency": acct["currency"],
    })


# ---------------------------------------------------------------------------
# 24. status
# ---------------------------------------------------------------------------

def status(conn, args):
    t_company = Table("company")
    t_account = Table("account")
    t_fy = Table("fiscal_year")
    t_gl = Table("gl_entry")

    company_id = getattr(args, 'company_id', None)
    # Auto-detect: if single company, use it; if multiple, show global stats
    if not company_id:
        q = Q.from_(t_company).select(t_company.id).limit(2)
        rows = conn.execute(q.get_sql()).fetchall()
        if len(rows) == 1:
            company_id = rows[0]["id"]

    g = Table("gl_entry").as_("g")
    a = Table("account").as_("a")

    if company_id:
        q = Q.from_(t_account).select(fn.Count("*").as_("cnt")).where(t_account.company_id == P())
        accounts = conn.execute(q.get_sql(), (company_id,)).fetchone()["cnt"]

        q = Q.from_(t_fy).select(fn.Count("*").as_("cnt")).where(t_fy.company_id == P())
        fiscal_years = conn.execute(q.get_sql(), (company_id,)).fetchone()["cnt"]

        q = (Q.from_(g).join(a).on(g.account_id == a.id)
             .select(fn.Count("*").as_("cnt"))
             .where(a.company_id == P())
             .where(g.is_cancelled == 0))
        gl_entries = conn.execute(q.get_sql(), (company_id,)).fetchone()["cnt"]

        q = (Q.from_(g).join(a).on(g.account_id == a.id)
             .select(fn.Max(g.posting_date).as_("latest"))
             .where(a.company_id == P())
             .where(g.is_cancelled == 0))
        latest = conn.execute(q.get_sql(), (company_id,)).fetchone()["latest"]
    else:
        q = Q.from_(t_account).select(fn.Count("*").as_("cnt"))
        accounts = conn.execute(q.get_sql()).fetchone()["cnt"]

        q = Q.from_(t_fy).select(fn.Count("*").as_("cnt"))
        fiscal_years = conn.execute(q.get_sql()).fetchone()["cnt"]

        q = (Q.from_(t_gl).select(fn.Count("*").as_("cnt"))
             .where(t_gl.is_cancelled == 0))
        gl_entries = conn.execute(q.get_sql()).fetchone()["cnt"]

        q = (Q.from_(t_gl).select(fn.Max(t_gl.posting_date).as_("latest"))
             .where(t_gl.is_cancelled == 0))
        latest = conn.execute(q.get_sql()).fetchone()["latest"]

    q = Q.from_(t_company).select(fn.Count("*").as_("cnt"))
    companies = conn.execute(q.get_sql()).fetchone()["cnt"]

    ok({
        "companies": companies,
        "accounts": accounts,
        "fiscal_years": fiscal_years,
        "gl_entries": gl_entries,
        "latest_posting_date": latest,
    })


# ---------------------------------------------------------------------------
# 25. revalue-foreign-balances
# ---------------------------------------------------------------------------

def revalue_foreign_balances(conn, args):
    """Revalue foreign-currency monetary accounts at period-end rate.

    Finds all accounts with currency != company base currency,
    computes unrealized gain/loss at the as-of-date exchange rate,
    and posts revaluation journal entries.
    """
    company_id = args.company_id
    as_of_date = args.as_of_date
    if not company_id:
        err("--company-id is required")
    if not as_of_date:
        err("--as-of-date is required")

    # Get company base currency
    t_company = Table("company")
    q = (Q.from_(t_company)
         .select(t_company.default_currency, t_company.exchange_gain_loss_account_id)
         .where(t_company.id == P()))
    company = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not company:
        err(f"Company {company_id} not found")

    base_currency = company["default_currency"] or "USD"
    fx_account_id = company["exchange_gain_loss_account_id"]
    if not fx_account_id:
        err("Company has no exchange_gain_loss_account_id configured")

    # Find all foreign-currency accounts (AR, AP, Bank) with balances
    t_acct = Table("account").as_("a")
    q = (Q.from_(t_acct)
         .select(t_acct.id, t_acct.name, t_acct.currency, t_acct.account_type, t_acct.root_type)
         .where(t_acct.company_id == P())
         .where(t_acct.currency != P())
         .where(t_acct.is_group == 0)
         .where(t_acct.disabled == 0)
         .where(t_acct.currency.isnotnull())
         .where(t_acct.account_type.isin(["receivable", "payable", "bank", "cash"])))
    accounts = conn.execute(q.get_sql(), (company_id, base_currency)).fetchall()

    if not accounts:
        ok({"revaluations": [], "message": "No foreign currency accounts found"})

    revaluations = []
    total_gain_loss = Decimal("0")

    for acct in accounts:
        acct_currency = acct["currency"]

        # raw SQL — uses CAST(column AS NUMERIC) which PyPika doesn't support cleanly
        bal = conn.execute(
            """SELECT
                COALESCE(SUM(CAST(debit AS NUMERIC)), 0) as total_debit,
                COALESCE(SUM(CAST(credit AS NUMERIC)), 0) as total_credit,
                COALESCE(SUM(CAST(debit_base AS NUMERIC)), 0) as total_debit_base,
                COALESCE(SUM(CAST(credit_base AS NUMERIC)), 0) as total_credit_base
               FROM gl_entry
               WHERE account_id = ? AND is_cancelled = 0 AND posting_date <= ?""",
            (acct["id"], as_of_date),
        ).fetchone()

        txn_balance = to_decimal(str(bal["total_debit"] - bal["total_credit"]))
        current_base_balance = to_decimal(str(bal["total_debit_base"] - bal["total_credit_base"]))

        if txn_balance == 0:
            continue

        # Get exchange rate at as-of-date
        new_rate = get_exchange_rate(conn, acct_currency, base_currency, as_of_date)
        if new_rate is None:
            revaluations.append({
                "account": acct["name"],
                "currency": acct_currency,
                "skipped": True,
                "reason": f"No exchange rate found for {acct_currency}/{base_currency} on {as_of_date}",
            })
            continue

        # Revalued base balance
        new_base_balance = convert_to_base(txn_balance, new_rate)
        gain_loss = new_base_balance - current_base_balance

        if gain_loss == 0:
            continue

        total_gain_loss += gain_loss
        abs_gl = abs(gain_loss)

        # Post revaluation GL entries (in base currency)
        # Revaluation is a base-currency adjustment, so entries use base amounts
        if gain_loss > 0:
            # Gain: DR account (increase), CR FX gain/loss
            gl_entries = [
                {"account_id": acct["id"],
                 "debit": str(abs_gl), "credit": "0"},
                {"account_id": fx_account_id,
                 "debit": "0", "credit": str(abs_gl)},
            ]
        else:
            # Loss: DR FX gain/loss, CR account (decrease)
            gl_entries = [
                {"account_id": acct["id"],
                 "debit": "0", "credit": str(abs_gl)},
                {"account_id": fx_account_id,
                 "debit": str(abs_gl), "credit": "0"},
            ]

        # FX account needs cost center (P&L account)
        q_cc = (Q.from_(t_company).select(t_company.default_cost_center_id)
                .where(t_company.id == P()))
        default_cc = conn.execute(q_cc.get_sql(), (company_id,)).fetchone()
        if default_cc and default_cc["default_cost_center_id"]:
            gl_entries[-1]["cost_center_id"] = default_cc["default_cost_center_id"]

        voucher_id = str(uuid.uuid4())
        try:
            gl_ids = insert_gl_entries(
                conn, gl_entries,
                voucher_type="exchange_rate_revaluation",
                voucher_id=voucher_id,
                posting_date=as_of_date,
                company_id=company_id,
                remarks=f"FX Revaluation: {acct['name']} ({acct_currency})",
            )
            revaluations.append({
                "account": acct["name"],
                "currency": acct_currency,
                "txn_balance": str(txn_balance),
                "old_base_balance": str(current_base_balance),
                "new_base_balance": str(new_base_balance),
                "gain_loss": str(gain_loss),
                "exchange_rate": str(new_rate),
                "gl_entries": len(gl_ids),
            })
        except ValueError as e:
            revaluations.append({
                "account": acct["name"],
                "currency": acct_currency,
                "skipped": True,
                "reason": str(e),
            })

    conn.commit()

    ok({
        "revaluations": revaluations,
        "total_gain_loss": str(total_gain_loss),
        "accounts_processed": len(revaluations),
    })


# ---------------------------------------------------------------------------
# 26. import-chart-of-accounts
# ---------------------------------------------------------------------------

def import_chart_of_accounts(conn, args):
    """Import accounts from CSV. Complements setup-chart-of-accounts.

    CSV columns: name, root_type, account_number (opt), account_type (opt),
    parent_name (opt), currency (opt), is_group (opt).
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

    errors = validate_csv(csv_real, "account")
    if errors:
        err(f"CSV validation failed: {'; '.join(errors)}")

    rows = parse_csv_rows(csv_real, "account")
    if not rows:
        err("CSV file is empty")

    imported = 0
    skipped = 0
    for row in rows:
        name = row.get("name", "")
        root_type = row.get("root_type", "")

        # Check for duplicate
        t_account = Table("account")
        q = (Q.from_(t_account).select(t_account.id)
             .where(t_account.name == P())
             .where(t_account.company_id == P()))
        existing = conn.execute(q.get_sql(), (name, company_id)).fetchone()
        if existing:
            skipped += 1
            continue

        # Resolve parent
        parent_id = None
        parent_name = row.get("parent_name")
        if parent_name:
            parent = conn.execute(q.get_sql(), (parent_name, company_id)).fetchone()
            if parent:
                parent_id = parent["id"]

        is_group = 1 if row.get("is_group", "0") in ("1", "true", "True") else 0
        balance_dir = "debit_normal"
        if root_type in ("liability", "equity", "income"):
            balance_dir = "credit_normal"

        acct_id = str(uuid.uuid4())
        q_ins = (Q.into(t_account)
                 .columns("id", "name", "account_number", "parent_id", "root_type",
                           "account_type", "currency", "is_group", "balance_direction",
                           "company_id", "depth")
                 .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P(), 0))
        conn.execute(q_ins.get_sql(),
            (acct_id, name, row.get("account_number"), parent_id, root_type,
             row.get("account_type"), row.get("currency", "USD"),
             is_group, balance_dir, company_id))
        imported += 1

    conn.commit()
    ok({"imported": imported, "skipped": skipped, "total_rows": len(rows)})


# ---------------------------------------------------------------------------
# 27. import-opening-balances
# ---------------------------------------------------------------------------

def import_opening_balances(conn, args):
    """Import opening balances from CSV, posting as opening journal entries.

    CSV columns: account_number, debit, credit, party_type (opt), party_name (opt).
    """
    csv_path = args.csv_path
    company_id = args.company_id
    posting_date = args.posting_date
    if not csv_path:
        err("--csv-path is required")
    if not company_id:
        err("--company-id is required")
    if not posting_date:
        err("--posting-date is required")

    # Path safety: resolve symlinks, require .csv extension, must be a regular file
    csv_real = os.path.realpath(csv_path)
    if not csv_real.lower().endswith(".csv"):
        err("--csv-path must point to a .csv file")
    if not os.path.isfile(csv_real):
        err(f"File not found: {csv_path}")

    from erpclaw_lib.csv_import import validate_csv, parse_csv_rows
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args

    errors = validate_csv(csv_real, "opening_balance")
    if errors:
        err(f"CSV validation failed: {'; '.join(errors)}")

    rows = parse_csv_rows(csv_real, "opening_balance")
    if not rows:
        err("CSV file is empty")

    # Build GL entries
    t_account = Table("account")
    t_customer = Table("customer")
    t_supplier = Table("supplier")

    gl_entries = []
    for row in rows:
        acct_num = row.get("account_number", "")
        q = (Q.from_(t_account).select(t_account.id, t_account.root_type)
             .where(t_account.account_number == P())
             .where(t_account.company_id == P()))
        acct = conn.execute(q.get_sql(), (acct_num, company_id)).fetchone()
        if not acct:
            err(f"Account not found: {acct_num}")

        debit = row.get("debit", "0")
        credit = row.get("credit", "0")
        entry = {"account_id": acct["id"], "debit": debit, "credit": credit}

        # Handle party for AR/AP
        if row.get("party_type") and row.get("party_name"):
            entry["party_type"] = row["party_type"]
            # Look up party ID
            if row["party_type"] == "customer":
                q_party = (Q.from_(t_customer).select(t_customer.id)
                           .where(t_customer.name == P())
                           .where(t_customer.company_id == P()))
            else:
                q_party = (Q.from_(t_supplier).select(t_supplier.id)
                           .where(t_supplier.name == P())
                           .where(t_supplier.company_id == P()))
            party = conn.execute(q_party.get_sql(), (row["party_name"], company_id)).fetchone()
            if party:
                entry["party_id"] = party["id"]

        gl_entries.append(entry)

    if not gl_entries:
        err("No valid entries found in CSV")

    voucher_id = str(uuid.uuid4())
    try:
        gl_ids = insert_gl_entries(
            conn, gl_entries,
            voucher_type="journal_entry",
            voucher_id=voucher_id,
            posting_date=posting_date,
            company_id=company_id,
            remarks="Opening Balance Import",
            is_opening=True,
        )
    except ValueError as e:
        err(f"GL posting failed: {e}")

    conn.commit()
    ok({"gl_entries_created": len(gl_ids), "voucher_id": voucher_id,
         "rows_processed": len(rows)})


# ---------------------------------------------------------------------------
# Action routing
# ---------------------------------------------------------------------------

ACTIONS = {
    "setup-chart-of-accounts": setup_chart_of_accounts,
    "add-account": add_account,
    "update-account": update_account,
    "list-accounts": list_accounts,
    "get-account": get_account,
    "freeze-account": freeze_account,
    "unfreeze-account": unfreeze_account,
    "post-gl-entries": post_gl_entries,
    "reverse-gl-entries": reverse_gl_entries_action,
    "list-gl-entries": list_gl_entries,
    "add-fiscal-year": add_fiscal_year,
    "list-fiscal-years": list_fiscal_years,
    "validate-period-close": validate_period_close,
    "close-fiscal-year": close_fiscal_year,
    "reopen-fiscal-year": reopen_fiscal_year,
    "add-cost-center": add_cost_center,
    "list-cost-centers": list_cost_centers,
    "add-budget": add_budget,
    "list-budgets": list_budgets,
    "seed-naming-series": seed_naming_series,
    "next-series": next_series,
    "check-gl-integrity": check_gl_integrity,
    "get-account-balance": get_account_balance_action,
    "revalue-foreign-balances": revalue_foreign_balances,
    "import-chart-of-accounts": import_chart_of_accounts,
    "import-opening-balances": import_opening_balances,
    "status": status,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = SafeArgumentParser(description="ERPClaw GL Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Chart of accounts
    parser.add_argument("--template", default=None)
    parser.add_argument("--company-id", default=None)

    # Account
    parser.add_argument("--account-id", default=None)
    parser.add_argument("--name", default=None)
    parser.add_argument("--account-number", default=None)
    parser.add_argument("--parent-id", default=None)
    parser.add_argument("--root-type", default=None)
    parser.add_argument("--account-type", default=None)
    parser.add_argument("--currency", default=None)
    parser.add_argument("--is-group", action="store_true", default=False)
    parser.add_argument("--is-frozen", default=None, type=lambda x: x.lower() == "true")
    parser.add_argument("--include-frozen", action="store_true", default=False)
    parser.add_argument("--search", default=None)

    # GL entries
    parser.add_argument("--voucher-type", default=None)
    parser.add_argument("--voucher-id", default=None)
    parser.add_argument("--posting-date", default=None)
    parser.add_argument("--entries", default=None)
    parser.add_argument("--is-cancelled", default=None, type=lambda x: x.lower() == "true")
    parser.add_argument("--party-type", default=None)
    parser.add_argument("--party-id", default=None)

    # Fiscal year
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument("--fiscal-year-id", default=None)
    parser.add_argument("--closing-account-id", default=None)

    # Budget
    parser.add_argument("--budget-amount", default=None)
    parser.add_argument("--action-if-exceeded", default=None)
    parser.add_argument("--cost-center-id", default=None)

    # Naming series
    parser.add_argument("--entity-type", default=None)

    # Balance / dates
    parser.add_argument("--as-of-date", default=None)
    parser.add_argument("--from-date", default=None)
    parser.add_argument("--to-date", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=None)

    # CSV import
    parser.add_argument("--csv-path", default=None)

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
        err(str(e))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
