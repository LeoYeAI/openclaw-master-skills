#!/usr/bin/env python3
"""ERPClaw Reports Skill — db_query.py

Read-only financial reporting. Owns NO tables — reads gl_entry,
payment_ledger_entry, account, budget, fiscal_year, etc.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime
from decimal import Decimal

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
    from erpclaw_lib.query import Q, P, Table, Field, fn, DecimalSum, DecimalAbs
    from erpclaw_lib.vendor.pypika import Order
    from erpclaw_lib.vendor.pypika.terms import LiteralValue
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)


REQUIRED_TABLES = ["company", "account", "gl_entry"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _d(val) -> Decimal:
    """Convert a DB value (possibly None) to Decimal."""
    if val is None:
        return Decimal("0")
    return to_decimal(str(val))


def _s(d: Decimal) -> str:
    """Format a Decimal to string for output."""
    return str(round_currency(d))


def _parse_json_arg(value, name):
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        err(f"Invalid JSON for --{name}: {value}")


# ---------------------------------------------------------------------------
# Trial Balance
# ---------------------------------------------------------------------------

def trial_balance(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.to_date:
        err("--to-date is required")

    from_date = args.from_date
    to_date = args.to_date
    project_id = getattr(args, "project_id", None)

    # Build optional project filter clause and params
    proj_clause = ""
    proj_params = ()
    if project_id:
        proj_clause = " AND project_id = ?"
        proj_params = (project_id,)

    # Get all accounts for the company
    acct_t = Table("account")
    sql = (
        Q.from_(acct_t)
        .select(
            acct_t.id, acct_t.name, acct_t.account_number,
            acct_t.root_type, acct_t.account_type, acct_t.is_group,
        )
        .where(acct_t.company_id == P())
        .orderby(acct_t.account_number)
        .orderby(acct_t.name)
        .get_sql()
    )
    accounts = conn.execute(sql, (company_id,)).fetchall()

    result = []
    total_debit = Decimal("0")
    total_credit = Decimal("0")

    gl_t = Table("gl_entry")

    for acct in accounts:
        if acct["is_group"]:
            continue

        aid = acct["id"]

        # Opening balance (before from_date, or all time if no from_date)
        if from_date:
            # Raw SQL: COALESCE(decimal_sum(...), '0') with aliased columns kept for clarity
            opening = conn.execute(
                """SELECT COALESCE(decimal_sum(debit), '0') as d,
                          COALESCE(decimal_sum(credit), '0') as c
                   FROM gl_entry WHERE account_id = ? AND posting_date < ?
                   AND is_cancelled = 0""" + proj_clause,
                (aid, from_date) + proj_params,
            ).fetchone()
        else:
            opening = {"d": 0, "c": 0}

        # Period movement
        if from_date:
            period = conn.execute(
                """SELECT COALESCE(decimal_sum(debit), '0') as d,
                          COALESCE(decimal_sum(credit), '0') as c
                   FROM gl_entry WHERE account_id = ?
                   AND posting_date >= ? AND posting_date <= ?
                   AND is_cancelled = 0""" + proj_clause,
                (aid, from_date, to_date) + proj_params,
            ).fetchone()
        else:
            period = conn.execute(
                """SELECT COALESCE(decimal_sum(debit), '0') as d,
                          COALESCE(decimal_sum(credit), '0') as c
                   FROM gl_entry WHERE account_id = ?
                   AND posting_date <= ? AND is_cancelled = 0""" + proj_clause,
                (aid, to_date) + proj_params,
            ).fetchone()

        op_d = _d(opening["d"])
        op_c = _d(opening["c"])
        per_d = _d(period["d"])
        per_c = _d(period["c"])
        cl_d = op_d + per_d
        cl_c = op_c + per_c

        # Skip accounts with zero activity
        if cl_d == 0 and cl_c == 0:
            continue

        total_debit += cl_d
        total_credit += cl_c

        result.append({
            "account_id": aid,
            "account_name": acct["name"],
            "account_number": acct["account_number"] or "",
            "root_type": acct["root_type"],
            "opening_debit": _s(op_d),
            "opening_credit": _s(op_c),
            "debit": _s(per_d),
            "credit": _s(per_c),
            "closing_debit": _s(cl_d),
            "closing_credit": _s(cl_c),
        })

    ok({
        "as_of_date": to_date,
        "total_debit": _s(total_debit),
        "total_credit": _s(total_credit),
        "accounts": result,
    })


# ---------------------------------------------------------------------------
# Profit & Loss
# ---------------------------------------------------------------------------

def profit_and_loss(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    project_id = getattr(args, "project_id", None)
    proj_join_clause = ""
    proj_params = ()
    if project_id:
        proj_join_clause = " AND g.project_id = ?"
        proj_params = (project_id,)

    # Raw SQL: too complex for PyPika, readability preserved
    # (COALESCE(decimal_sum(...)) arithmetic in SELECT, LEFT JOIN with date range in ON clause,
    #  HAVING on computed alias — PyPika doesn't support HAVING on aliased expressions cleanly)
    income_rows = conn.execute(
        """SELECT a.id, a.name, a.account_number,
                  COALESCE(decimal_sum(g.credit), '0') - COALESCE(decimal_sum(g.debit), '0') as amount
           FROM account a
           LEFT JOIN gl_entry g ON g.account_id = a.id
               AND g.posting_date >= ? AND g.posting_date <= ?
               AND g.is_cancelled = 0""" + proj_join_clause + """
           WHERE a.company_id = ? AND a.root_type = 'income' AND a.is_group = 0
           GROUP BY a.id
           HAVING amount != 0
           ORDER BY a.account_number, a.name""",
        (args.from_date, args.to_date) + proj_params + (company_id,),
    ).fetchall()

    # Raw SQL: too complex for PyPika, readability preserved
    expense_rows = conn.execute(
        """SELECT a.id, a.name, a.account_number,
                  COALESCE(decimal_sum(g.debit), '0') - COALESCE(decimal_sum(g.credit), '0') as amount
           FROM account a
           LEFT JOIN gl_entry g ON g.account_id = a.id
               AND g.posting_date >= ? AND g.posting_date <= ?
               AND g.is_cancelled = 0""" + proj_join_clause + """
           WHERE a.company_id = ? AND a.root_type = 'expense' AND a.is_group = 0
           GROUP BY a.id
           HAVING amount != 0
           ORDER BY a.account_number, a.name""",
        (args.from_date, args.to_date) + proj_params + (company_id,),
    ).fetchall()

    income = [{"account": r["name"], "account_id": r["id"], "amount": _s(_d(r["amount"]))}
              for r in income_rows]
    expenses = [{"account": r["name"], "account_id": r["id"], "amount": _s(_d(r["amount"]))}
                for r in expense_rows]

    income_total = sum(_d(r["amount"]) for r in income_rows)
    expense_total = sum(_d(r["amount"]) for r in expense_rows)
    net_income = income_total - expense_total

    ok({
        "period": f"{args.from_date} to {args.to_date}",
        "income": income,
        "income_total": _s(income_total),
        "expenses": expenses,
        "expense_total": _s(expense_total),
        "net_income": _s(net_income),
    })


# ---------------------------------------------------------------------------
# Balance Sheet
# ---------------------------------------------------------------------------

def balance_sheet(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.as_of_date:
        err("--as-of-date is required")

    project_id = getattr(args, "project_id", None)
    proj_join_clause = ""
    proj_where_clause = ""
    proj_join_params = ()
    proj_where_params = ()
    if project_id:
        proj_join_clause = " AND g.project_id = ?"
        proj_where_clause = " AND g.project_id = ?"
        proj_join_params = (project_id,)
        proj_where_params = (project_id,)

    def _section(root_type, debit_positive=True):
        # Raw SQL: too complex for PyPika, readability preserved
        # (LEFT JOIN with date filter in ON clause, HAVING on computed aliases)
        rows = conn.execute(
            """SELECT a.id, a.name, a.account_number,
                      COALESCE(decimal_sum(g.debit), '0') as total_debit,
                      COALESCE(decimal_sum(g.credit), '0') as total_credit
               FROM account a
               LEFT JOIN gl_entry g ON g.account_id = a.id
                   AND g.posting_date <= ? AND g.is_cancelled = 0""" + proj_join_clause + """
               WHERE a.company_id = ? AND a.root_type = ? AND a.is_group = 0
               GROUP BY a.id
               HAVING total_debit != 0 OR total_credit != 0
               ORDER BY a.account_number, a.name""",
            (args.as_of_date,) + proj_join_params + (company_id, root_type),
        ).fetchall()

        items = []
        total = Decimal("0")
        for r in rows:
            d = _d(r["total_debit"])
            c = _d(r["total_credit"])
            amt = (d - c) if debit_positive else (c - d)
            if amt == 0:
                continue
            items.append({"account": r["name"], "account_id": r["id"],
                          "amount": _s(amt)})
            total += amt
        return items, total

    assets, total_assets = _section("asset", debit_positive=True)
    liabilities, total_liabilities = _section("liability", debit_positive=False)
    equity_items, total_equity_base = _section("equity", debit_positive=False)

    # Calculate current year net income for equity section
    # Get the fiscal year start for the as_of_date
    fy_t = Table("fiscal_year")
    fy_sql = (
        Q.from_(fy_t)
        .select(fy_t.start_date)
        .where(fy_t.company_id == P())
        .where(fy_t.start_date <= P())
        .where(fy_t.end_date >= P())
        .orderby(fy_t.start_date, order=Order.desc)
        .limit(1)
        .get_sql()
    )
    fy = conn.execute(fy_sql, (company_id, args.as_of_date, args.as_of_date)).fetchone()

    net_income_ytd = Decimal("0")
    if fy:
        fy_start = fy["start_date"]
        # Raw SQL: too complex for PyPika, readability preserved
        # (JOIN with subquery-style arithmetic, decimal_sum aggregates on cross-join result)
        inc = conn.execute(
            """SELECT COALESCE(decimal_sum(credit), '0') - COALESCE(decimal_sum(debit), '0') as amt
               FROM gl_entry g JOIN account a ON a.id = g.account_id
               WHERE a.company_id = ? AND a.root_type = 'income'
               AND g.posting_date >= ? AND g.posting_date <= ?
               AND g.is_cancelled = 0""" + proj_where_clause,
            (company_id, fy_start, args.as_of_date) + proj_where_params,
        ).fetchone()
        exp = conn.execute(
            """SELECT COALESCE(decimal_sum(debit), '0') - COALESCE(decimal_sum(credit), '0') as amt
               FROM gl_entry g JOIN account a ON a.id = g.account_id
               WHERE a.company_id = ? AND a.root_type = 'expense'
               AND g.posting_date >= ? AND g.posting_date <= ?
               AND g.is_cancelled = 0""" + proj_where_clause,
            (company_id, fy_start, args.as_of_date) + proj_where_params,
        ).fetchone()
        net_income_ytd = _d(inc["amt"]) - _d(exp["amt"])

    total_equity = total_equity_base + net_income_ytd

    ok({
        "as_of_date": args.as_of_date,
        "assets": assets,
        "total_assets": _s(total_assets),
        "liabilities": liabilities,
        "total_liabilities": _s(total_liabilities),
        "equity": equity_items,
        "total_equity": _s(total_equity),
        "net_income_ytd": _s(net_income_ytd),
    })


# ---------------------------------------------------------------------------
# Cash Flow (indirect method)
# ---------------------------------------------------------------------------

def cash_flow(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    # Raw SQL: too complex for PyPika, readability preserved
    # (JOIN + decimal_sum arithmetic in SELECT with IN clause on account_type)
    opening = conn.execute(
        """SELECT COALESCE(decimal_sum(g.debit), '0') - COALESCE(decimal_sum(g.credit), '0') as bal
           FROM gl_entry g JOIN account a ON a.id = g.account_id
           WHERE a.company_id = ? AND a.account_type IN ('bank','cash')
           AND g.posting_date < ? AND g.is_cancelled = 0""",
        (company_id, args.from_date),
    ).fetchone()
    opening_balance = _d(opening["bal"])

    # Raw SQL: too complex for PyPika, readability preserved
    closing = conn.execute(
        """SELECT COALESCE(decimal_sum(g.debit), '0') - COALESCE(decimal_sum(g.credit), '0') as bal
           FROM gl_entry g JOIN account a ON a.id = g.account_id
           WHERE a.company_id = ? AND a.account_type IN ('bank','cash')
           AND g.posting_date <= ? AND g.is_cancelled = 0""",
        (company_id, args.to_date),
    ).fetchone()
    closing_balance = _d(closing["bal"])

    net_change = closing_balance - opening_balance

    # Simplified: categorize by account type
    # Operating: income/expense + current asset/liability changes
    # Investing: fixed asset changes
    # Financing: equity + loan changes
    details = []

    # Raw SQL: too complex for PyPika, readability preserved
    # (JOIN + decimal_sum + NOT IN clause + HAVING on computed aliases)
    movements = conn.execute(
        """SELECT a.id, a.name, a.root_type, a.account_type,
                  COALESCE(decimal_sum(g.debit), '0') as d,
                  COALESCE(decimal_sum(g.credit), '0') as c
           FROM gl_entry g JOIN account a ON a.id = g.account_id
           WHERE a.company_id = ?
           AND g.posting_date >= ? AND g.posting_date <= ?
           AND g.is_cancelled = 0
           AND a.account_type NOT IN ('bank','cash')
           GROUP BY a.id
           HAVING d != 0 OR c != 0
           ORDER BY a.root_type, a.name""",
        (company_id, args.from_date, args.to_date),
    ).fetchall()

    operating = Decimal("0")
    investing = Decimal("0")
    financing = Decimal("0")

    for m in movements:
        d = _d(m["d"])
        c = _d(m["c"])
        root = m["root_type"]
        atype = m["account_type"] or ""

        if root == "income":
            amt = c - d  # Income increases cash
            operating += amt
            cat = "operating"
        elif root == "expense":
            amt = -(d - c)  # Expenses decrease cash
            operating += amt
            cat = "operating"
        elif root == "asset" and atype in ("fixed_asset", "accumulated_depreciation"):
            amt = -(d - c)
            investing += amt
            cat = "investing"
        elif root == "asset":
            amt = -(d - c)  # Increase in current asset = cash outflow
            operating += amt
            cat = "operating"
        elif root == "liability":
            amt = c - d  # Increase in liability = cash inflow
            if atype in ("Long Term Loan",):
                financing += amt
                cat = "financing"
            else:
                operating += amt
                cat = "operating"
        elif root == "equity":
            amt = c - d
            financing += amt
            cat = "financing"
        else:
            amt = c - d
            operating += amt
            cat = "operating"

        if amt != 0:
            details.append({
                "category": cat,
                "account": m["name"],
                "amount": _s(amt),
            })

    ok({
        "operating": _s(operating),
        "investing": _s(investing),
        "financing": _s(financing),
        "net_change": _s(net_change),
        "opening_balance": _s(opening_balance),
        "closing_balance": _s(closing_balance),
        "details": details,
    })


# ---------------------------------------------------------------------------
# General Ledger
# ---------------------------------------------------------------------------

def general_ledger(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    limit = int(args.limit or "100")
    offset = int(args.offset or "0")

    gl_t = Table("gl_entry").as_("g")
    acct_t = Table("account").as_("a")

    # Build opening balance query dynamically
    opening_q = (
        Q.from_(gl_t)
        .join(acct_t).on(acct_t.id == gl_t.account_id)
        .select(
            (fn.Coalesce(DecimalSum(gl_t.debit), "0") - fn.Coalesce(DecimalSum(gl_t.credit), "0")).as_("bal")
        )
        .where(gl_t.posting_date < P())
        .where(gl_t.is_cancelled == 0)
        .where(acct_t.company_id == P())
    )
    opening_params = [args.from_date, company_id]

    if args.account_id:
        opening_q = opening_q.where(gl_t.account_id == P())
        opening_params.append(args.account_id)

    opening = conn.execute(opening_q.get_sql(), opening_params).fetchone()
    opening_balance = _d(opening["bal"])

    # Build period entries query dynamically
    entries_q = (
        Q.from_(gl_t)
        .join(acct_t).on(acct_t.id == gl_t.account_id)
        .select(gl_t.star, acct_t.name.as_("account_name"))
        .where(gl_t.posting_date >= P())
        .where(gl_t.posting_date <= P())
        .where(gl_t.is_cancelled == 0)
        .where(acct_t.company_id == P())
    )
    entries_params = [args.from_date, args.to_date, company_id]

    if args.account_id:
        entries_q = entries_q.where(gl_t.account_id == P())
        entries_params.append(args.account_id)
    if args.party_type:
        entries_q = entries_q.where(gl_t.party_type == P())
        entries_params.append(args.party_type)
    if args.party_id:
        entries_q = entries_q.where(gl_t.party_id == P())
        entries_params.append(args.party_id)
    if args.voucher_type:
        entries_q = entries_q.where(gl_t.voucher_type == P())
        entries_params.append(args.voucher_type)

    entries_q = (
        entries_q
        .orderby(gl_t.posting_date)
        .orderby(gl_t.created_at)
        .limit(P())
        .offset(P())
    )
    entries_params += [limit, offset]

    entries = conn.execute(entries_q.get_sql(), entries_params).fetchall()

    total_debit = Decimal("0")
    total_credit = Decimal("0")
    running_balance = opening_balance
    result = []

    for e in entries:
        d = _d(e["debit"])
        c = _d(e["credit"])
        total_debit += d
        total_credit += c
        running_balance += (d - c)

        result.append({
            "posting_date": e["posting_date"],
            "account_name": e["account_name"],
            "debit": _s(d),
            "credit": _s(c),
            "balance": _s(running_balance),
            "voucher_type": e["voucher_type"],
            "voucher_id": e["voucher_id"],
            "party_type": e["party_type"] or "",
            "party_id": e["party_id"] or "",
            "remarks": e["remarks"] or "",
        })

    ok({
        "entries": result,
        "opening_balance": _s(opening_balance),
        "total_debit": _s(total_debit),
        "total_credit": _s(total_credit),
        "closing_balance": _s(running_balance),
    })


# ---------------------------------------------------------------------------
# AR/AP Aging
# ---------------------------------------------------------------------------

_PARTY_TABLE_ALLOWLIST = {"customer": "customer", "supplier": "supplier"}

def _aging_report(conn, args, party_type_label, party_table, party_name_col="name"):
    if party_table not in _PARTY_TABLE_ALLOWLIST:
        err(f"Invalid party table: {party_table}")
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.as_of_date:
        err("--as-of-date is required")

    buckets_str = args.aging_buckets or "30,60,90,120"
    try:
        buckets = [int(b) for b in buckets_str.split(",")]
    except ValueError:
        err("Invalid --aging-buckets format (expected comma-separated integers)")

    # Get outstanding by party from payment_ledger_entry
    ple_t = Table("payment_ledger_entry")
    outstanding_sql = (
        Q.from_(ple_t)
        .select(
            ple_t.party_id,
            DecimalSum(ple_t.amount).as_("total"),
            fn.Min(ple_t.posting_date).as_("earliest_date"),
        )
        .where(ple_t.party_type == P())
        .where(ple_t.delinked == 0)
        .where(ple_t.posting_date <= P())
        .groupby(ple_t.party_id)
        .having(
            LiteralValue("total + 0 > 0.005 OR total + 0 < -0.005")
        )
        .get_sql()
    )
    outstanding = conn.execute(outstanding_sql, (party_type_label, args.as_of_date)).fetchall()

    # Get individual entries for aging
    entries_sql = (
        Q.from_(ple_t)
        .select(ple_t.party_id, ple_t.posting_date, ple_t.amount)
        .where(ple_t.party_type == P())
        .where(ple_t.delinked == 0)
        .where(ple_t.posting_date <= P())
        .orderby(ple_t.party_id)
        .orderby(ple_t.posting_date)
        .get_sql()
    )
    ple_rows = conn.execute(entries_sql, (party_type_label, args.as_of_date)).fetchall()

    entries_by_party = {}
    for row in ple_rows:
        pid = row["party_id"]
        if pid not in entries_by_party:
            entries_by_party[pid] = []
        entries_by_party[pid].append(row)

    result = []
    total_outstanding = Decimal("0")

    for o in outstanding:
        pid = o["party_id"]
        if party_type_label == "customer":
            cust_t = Table("customer")
            party_sql = (
                Q.from_(cust_t)
                .select(cust_t.id, cust_t.name.as_("pname"))
                .where(cust_t.id == P())
                .get_sql()
            )
            party = conn.execute(party_sql, (pid,)).fetchone()
        else:
            supp_t = Table("supplier")
            party_sql = (
                Q.from_(supp_t)
                .select(supp_t.id, supp_t.name.as_("pname"))
                .where(supp_t.id == P())
                .get_sql()
            )
            party = conn.execute(party_sql, (pid,)).fetchone()
        pname = party["pname"] if party else pid

        # Calculate aging for this party
        bucket_amounts = [Decimal("0")] * (len(buckets) + 1)  # +1 for beyond last bucket

        for ple in entries_by_party.get(pid, []):
            from datetime import datetime
            pd = datetime.strptime(ple["posting_date"], "%Y-%m-%d")
            ad = datetime.strptime(args.as_of_date, "%Y-%m-%d")
            days = (ad - pd).days

            placed = False
            for i, b in enumerate(buckets):
                if i == 0 and days <= b:
                    bucket_amounts[0] += _d(ple["amount"])
                    placed = True
                    break
                elif i > 0 and days > buckets[i-1] and days <= b:
                    bucket_amounts[i] += _d(ple["amount"])
                    placed = True
                    break
            if not placed:
                bucket_amounts[-1] += _d(ple["amount"])

        party_total = _d(o["total"])
        total_outstanding += party_total

        entry = {
            f"{party_type_label}_id": pid,
            f"{party_type_label}_name": pname,
            "current": _s(bucket_amounts[0]),
        }
        for i, b in enumerate(buckets):
            if i == 0:
                entry["current"] = _s(bucket_amounts[0])
            else:
                entry[f"days_{b}"] = _s(bucket_amounts[i])
        if len(buckets) > 1:
            entry[f"days_{buckets[0]}"] = _s(bucket_amounts[0])
            for i in range(1, len(buckets)):
                entry[f"days_{buckets[i]}"] = _s(bucket_amounts[i])
        entry[f"days_{buckets[-1]}_plus"] = _s(bucket_amounts[-1])
        entry["total"] = _s(party_total)
        result.append(entry)

    ok({
        "as_of_date": args.as_of_date,
        "total_outstanding": _s(total_outstanding),
        f"{party_type_label}s": result,
    })


def ar_aging(conn, args):
    _aging_report(conn, args, "customer", "customer")


def ap_aging(conn, args):
    _aging_report(conn, args, "supplier", "supplier")


# ---------------------------------------------------------------------------
# Budget vs Actual
# ---------------------------------------------------------------------------

def budget_vs_actual(conn, args):
    if not args.fiscal_year_id:
        err("--fiscal-year-id is required")
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    fy_t = Table("fiscal_year")
    fy_sql = (
        Q.from_(fy_t)
        .select(fy_t.star)
        .where(fy_t.id == P())
        .get_sql()
    )
    fy = conn.execute(fy_sql, (args.fiscal_year_id,)).fetchone()
    if not fy:
        err(f"Fiscal year not found: {args.fiscal_year_id}")

    # Build budgets query dynamically
    b_t = Table("budget").as_("b")
    acct_t = Table("account").as_("a")
    cc_t = Table("cost_center").as_("cc")

    budgets_q = (
        Q.from_(b_t)
        .left_join(acct_t).on(acct_t.id == b_t.account_id)
        .left_join(cc_t).on(cc_t.id == b_t.cost_center_id)
        .select(b_t.star, acct_t.name.as_("account_name"), cc_t.name.as_("cc_name"))
        .where(b_t.fiscal_year_id == P())
        .where(b_t.company_id == P())
    )
    budgets_params = [args.fiscal_year_id, company_id]

    if args.account_id:
        budgets_q = budgets_q.where(b_t.account_id == P())
        budgets_params.append(args.account_id)
    if args.cost_center_id:
        budgets_q = budgets_q.where(b_t.cost_center_id == P())
        budgets_params.append(args.cost_center_id)

    budgets_q = budgets_q.orderby(acct_t.name)
    budgets = conn.execute(budgets_q.get_sql(), budgets_params).fetchall()

    items = []
    for b in budgets:
        budget_amt = _d(b["budget_amount"])

        # Build actual query dynamically
        gl_t = Table("gl_entry").as_("g")
        actual_q = (
            Q.from_(gl_t)
            .select(
                (fn.Coalesce(DecimalSum(gl_t.debit), "0") - fn.Coalesce(DecimalSum(gl_t.credit), "0")).as_("amt")
            )
            .where(gl_t.is_cancelled == 0)
            .where(gl_t.posting_date >= P())
            .where(gl_t.posting_date <= P())
        )
        actual_params = [fy["start_date"], fy["end_date"]]

        if b["account_id"]:
            actual_q = actual_q.where(gl_t.account_id == P())
            actual_params.append(b["account_id"])
        if b["cost_center_id"]:
            actual_q = actual_q.where(gl_t.cost_center_id == P())
            actual_params.append(b["cost_center_id"])

        actual = conn.execute(actual_q.get_sql(), actual_params).fetchone()
        actual_amt = _d(actual["amt"])

        variance = budget_amt - actual_amt
        variance_pct = (variance / budget_amt * 100) if budget_amt else Decimal("0")

        items.append({
            "account_or_cc": b["account_name"] or b["cc_name"] or "Unknown",
            "budget": _s(budget_amt),
            "actual": _s(actual_amt),
            "variance": _s(variance),
            "variance_pct": _s(variance_pct),
            "action_if_exceeded": b["action_if_exceeded"],
        })

    ok({"items": items})


# ---------------------------------------------------------------------------
# Party Ledger
# ---------------------------------------------------------------------------

def party_ledger(conn, args):
    if not args.party_type or args.party_type not in ("customer", "supplier"):
        err("--party-type must be 'customer' or 'supplier'")
    if not args.party_id:
        err("--party-id is required")

    if args.party_type == "customer":
        cust_t = Table("customer")
        party_sql = (
            Q.from_(cust_t)
            .select(cust_t.name)
            .where(cust_t.id == P())
            .get_sql()
        )
        party = conn.execute(party_sql, (args.party_id,)).fetchone()
    elif args.party_type == "supplier":
        supp_t = Table("supplier")
        party_sql = (
            Q.from_(supp_t)
            .select(supp_t.name)
            .where(supp_t.id == P())
            .get_sql()
        )
        party = conn.execute(party_sql, (args.party_id,)).fetchone()
    else:
        err("--party-type must be 'customer' or 'supplier'")
    party_name = party["name"] if party else args.party_id

    gl_t = Table("gl_entry").as_("g")

    # Opening balance (before from_date)
    if args.from_date:
        opening_q = (
            Q.from_(gl_t)
            .select(
                (fn.Coalesce(DecimalSum(gl_t.debit), "0") - fn.Coalesce(DecimalSum(gl_t.credit), "0")).as_("bal")
            )
            .where(gl_t.party_type == P())
            .where(gl_t.party_id == P())
            .where(gl_t.is_cancelled == 0)
            .where(gl_t.posting_date < P())
        )
        opening_params = [args.party_type, args.party_id, args.from_date]
    else:
        # No from_date → no opening balance (1=0 condition)
        opening_q = (
            Q.from_(gl_t)
            .select(
                (fn.Coalesce(DecimalSum(gl_t.debit), "0") - fn.Coalesce(DecimalSum(gl_t.credit), "0")).as_("bal")
            )
            .where(gl_t.party_type == P())
            .where(gl_t.party_id == P())
            .where(gl_t.is_cancelled == 0)
            .where(LiteralValue("1 = 0"))
        )
        opening_params = [args.party_type, args.party_id]

    opening = conn.execute(opening_q.get_sql(), opening_params).fetchone()
    opening_balance = _d(opening["bal"])

    # Period entries
    entries_q = (
        Q.from_(gl_t)
        .select(gl_t.posting_date, gl_t.voucher_type, gl_t.voucher_id, gl_t.debit, gl_t.credit)
        .where(gl_t.party_type == P())
        .where(gl_t.party_id == P())
        .where(gl_t.is_cancelled == 0)
    )
    entries_params = [args.party_type, args.party_id]

    if args.from_date:
        entries_q = entries_q.where(gl_t.posting_date >= P())
        entries_params.append(args.from_date)
    if args.to_date:
        entries_q = entries_q.where(gl_t.posting_date <= P())
        entries_params.append(args.to_date)

    entries_q = entries_q.orderby(gl_t.posting_date).orderby(gl_t.created_at)
    entries = conn.execute(entries_q.get_sql(), entries_params).fetchall()

    running = opening_balance
    result = []
    for e in entries:
        d = _d(e["debit"])
        c = _d(e["credit"])
        running += (d - c)
        result.append({
            "posting_date": e["posting_date"],
            "voucher_type": e["voucher_type"],
            "voucher_id": e["voucher_id"],
            "debit": _s(d),
            "credit": _s(c),
            "balance": _s(running),
        })

    ok({
        "party_name": party_name,
        "opening_balance": _s(opening_balance),
        "entries": result,
        "closing_balance": _s(running),
    })


# ---------------------------------------------------------------------------
# Tax Summary
# ---------------------------------------------------------------------------

def tax_summary(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    # Tax accounts are those of type "Tax Payable" or similar
    # Raw SQL: too complex for PyPika, readability preserved
    # (LEFT JOIN with date range in ON clause, decimal_sum aggregates aliased in SELECT)
    tax_accounts = conn.execute(
        """SELECT a.id, a.name, a.account_type,
                  COALESCE(decimal_sum(g.credit), '0') as collected,
                  COALESCE(decimal_sum(g.debit), '0') as paid
           FROM account a
           LEFT JOIN gl_entry g ON g.account_id = a.id
               AND g.posting_date >= ? AND g.posting_date <= ?
               AND g.is_cancelled = 0
           WHERE a.company_id = ?
           AND a.account_type = 'tax'
           AND a.is_group = 0
           GROUP BY a.id
           ORDER BY a.name""",
        (args.from_date, args.to_date, company_id),
    ).fetchall()

    total_collected = Decimal("0")
    total_paid = Decimal("0")
    by_account = []

    for ta in tax_accounts:
        collected = _d(ta["collected"])
        paid = _d(ta["paid"])
        net = collected - paid
        if net == 0 and collected == 0 and paid == 0:
            continue
        total_collected += collected
        total_paid += paid
        by_account.append({
            "account_id": ta["id"],
            "account_name": ta["name"],
            "amount": _s(net),
        })

    ok({
        "collected": _s(total_collected),
        "paid": _s(total_paid),
        "net_liability": _s(total_collected - total_paid),
        "by_account": by_account,
    })


# ---------------------------------------------------------------------------
# Payment Summary
# ---------------------------------------------------------------------------

def payment_summary(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    pe_t = Table("payment_entry")

    received_sql = (
        Q.from_(pe_t)
        .select(fn.Coalesce(DecimalSum(pe_t.paid_amount), "0").as_("total"))
        .where(pe_t.company_id == P())
        .where(pe_t.status == "submitted")
        .where(pe_t.payment_type == "receive")
        .where(pe_t.posting_date >= P())
        .where(pe_t.posting_date <= P())
        .get_sql()
    )
    received = conn.execute(received_sql, (company_id, args.from_date, args.to_date)).fetchone()

    paid_sql = (
        Q.from_(pe_t)
        .select(fn.Coalesce(DecimalSum(pe_t.paid_amount), "0").as_("total"))
        .where(pe_t.company_id == P())
        .where(pe_t.status == "submitted")
        .where(pe_t.payment_type == "pay")
        .where(pe_t.posting_date >= P())
        .where(pe_t.posting_date <= P())
        .get_sql()
    )
    paid = conn.execute(paid_sql, (company_id, args.from_date, args.to_date)).fetchone()

    by_party_sql = (
        Q.from_(pe_t)
        .select(
            pe_t.party_type,
            fn.Count("*").as_("cnt"),
            fn.Coalesce(DecimalSum(pe_t.paid_amount), "0").as_("amount"),
        )
        .where(pe_t.company_id == P())
        .where(pe_t.status == "submitted")
        .where(pe_t.posting_date >= P())
        .where(pe_t.posting_date <= P())
        .groupby(pe_t.party_type)
        .get_sql()
    )
    by_party = conn.execute(by_party_sql, (company_id, args.from_date, args.to_date)).fetchall()

    ok({
        "total_received": _s(_d(received["total"])),
        "total_paid": _s(_d(paid["total"])),
        "by_party_type": [
            {"party_type": r["party_type"] or "unknown",
             "count": r["cnt"], "amount": _s(_d(r["amount"]))}
            for r in by_party
        ],
    })


# ---------------------------------------------------------------------------
# GL Summary
# ---------------------------------------------------------------------------

def gl_summary(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    gl_t = Table("gl_entry").as_("g")
    acct_t = Table("account").as_("a")

    sql = (
        Q.from_(gl_t)
        .join(acct_t).on(acct_t.id == gl_t.account_id)
        .select(
            gl_t.voucher_type,
            fn.Count("*").as_("cnt"),
            fn.Coalesce(DecimalSum(gl_t.debit), "0").as_("total_debit"),
            fn.Coalesce(DecimalSum(gl_t.credit), "0").as_("total_credit"),
        )
        .where(acct_t.company_id == P())
        .where(gl_t.posting_date >= P())
        .where(gl_t.posting_date <= P())
        .where(gl_t.is_cancelled == 0)
        .groupby(gl_t.voucher_type)
        .orderby(gl_t.voucher_type)
        .get_sql()
    )
    rows = conn.execute(sql, (company_id, args.from_date, args.to_date)).fetchall()

    ok({
        "by_voucher_type": [
            {"voucher_type": r["voucher_type"],
             "count": r["cnt"],
             "total_debit": _s(_d(r["total_debit"])),
             "total_credit": _s(_d(r["total_credit"]))}
            for r in rows
        ],
    })


# ---------------------------------------------------------------------------
# Comparative P&L
# ---------------------------------------------------------------------------

def comparative_pl(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    periods = _parse_json_arg(args.periods, "periods")
    if not periods or not isinstance(periods, list):
        err("--periods must be a non-empty JSON array of {from_date, to_date, label}")

    # Get all income/expense accounts
    acct_t = Table("account")
    accts_sql = (
        Q.from_(acct_t)
        .select(acct_t.id, acct_t.name, acct_t.root_type)
        .where(acct_t.company_id == P())
        .where(acct_t.root_type.isin(["income", "expense"]))
        .where(acct_t.is_group == 0)
        .orderby(acct_t.root_type)
        .orderby(acct_t.name)
        .get_sql()
    )
    accounts = conn.execute(accts_sql, (company_id,)).fetchall()

    result_accounts = []
    totals = []

    gl_t = Table("gl_entry")

    for period in periods:
        fd = period.get("from_date")
        td = period.get("to_date")
        label = period.get("label", f"{fd} to {td}")
        p_income = Decimal("0")
        p_expense = Decimal("0")

        for acct in accounts:
            if acct["root_type"] == "income":
                row = conn.execute(
                    """SELECT COALESCE(decimal_sum(credit), '0') - COALESCE(decimal_sum(debit), '0') as amt
                       FROM gl_entry WHERE account_id = ?
                       AND posting_date >= ? AND posting_date <= ?
                       AND is_cancelled = 0""",
                    (acct["id"], fd, td),
                ).fetchone()
                amt = _d(row["amt"])
                p_income += amt
            else:
                row = conn.execute(
                    """SELECT COALESCE(decimal_sum(debit), '0') - COALESCE(decimal_sum(credit), '0') as amt
                       FROM gl_entry WHERE account_id = ?
                       AND posting_date >= ? AND posting_date <= ?
                       AND is_cancelled = 0""",
                    (acct["id"], fd, td),
                ).fetchone()
                amt = _d(row["amt"])
                p_expense += amt

            # Find or create account entry in result
            existing = None
            for ra in result_accounts:
                if ra["account_id"] == acct["id"]:
                    existing = ra
                    break
            if not existing:
                existing = {"account": acct["name"], "account_id": acct["id"],
                            "root_type": acct["root_type"], "periods": []}
                result_accounts.append(existing)
            existing["periods"].append({"label": label, "amount": _s(amt)})

        totals.append({
            "label": label,
            "income": _s(p_income),
            "expenses": _s(p_expense),
            "net": _s(p_income - p_expense),
        })

    ok({"accounts": result_accounts, "totals": totals})


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    gl_t = Table("gl_entry").as_("g")
    acct_t = Table("account").as_("a")

    count_sql = (
        Q.from_(gl_t)
        .join(acct_t).on(acct_t.id == gl_t.account_id)
        .select(fn.Count("*").as_("cnt"))
        .where(acct_t.company_id == P())
        .where(gl_t.is_cancelled == 0)
        .get_sql()
    )
    gl_count = conn.execute(count_sql, (company_id,)).fetchone()["cnt"]

    dates_sql = (
        Q.from_(gl_t)
        .join(acct_t).on(acct_t.id == gl_t.account_id)
        .select(
            fn.Min(gl_t.posting_date).as_("earliest"),
            fn.Max(gl_t.posting_date).as_("latest"),
        )
        .where(acct_t.company_id == P())
        .where(gl_t.is_cancelled == 0)
        .get_sql()
    )
    dates = conn.execute(dates_sql, (company_id,)).fetchone()

    fy_t = Table("fiscal_year")
    fy_count_sql = (
        Q.from_(fy_t)
        .select(fn.Count("*").as_("cnt"))
        .where(fy_t.company_id == P())
        .get_sql()
    )
    fy_count = conn.execute(fy_count_sql, (company_id,)).fetchone()["cnt"]

    ok({
        "gl_entry_count": gl_count,
        "latest_posting_date": dates["latest"],
        "earliest_posting_date": dates["earliest"],
        "fiscal_years": fy_count,
    })


# ---------------------------------------------------------------------------
# Check Overdue Invoices
# ---------------------------------------------------------------------------


def check_overdue(conn, args):
    """Find overdue sales invoices and group them into aging buckets."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    today = datetime.now().strftime("%Y-%m-%d")

    si_t = Table("sales_invoice").as_("si")
    cust_t = Table("customer").as_("c")

    sql = (
        Q.from_(si_t)
        .left_join(cust_t).on(cust_t.id == si_t.customer_id)
        .select(
            si_t.id, si_t.naming_series, si_t.grand_total,
            si_t.outstanding_amount, si_t.due_date,
            cust_t.name.as_("customer_name"),
        )
        .where(si_t.company_id == P())
        .where(si_t.status.isin(["submitted", "partially_paid", "overdue"]))
        .where(LiteralValue("si.\"outstanding_amount\" + 0 > 0"))
        .where(si_t.due_date < P())
        .orderby(si_t.due_date)
        .get_sql()
    )
    rows = conn.execute(sql, (company_id, today)).fetchall()

    # Initialize buckets
    buckets = {
        "0_30": {"count": 0, "total": Decimal("0")},
        "31_60": {"count": 0, "total": Decimal("0")},
        "61_90": {"count": 0, "total": Decimal("0")},
        "90_plus": {"count": 0, "total": Decimal("0")},
    }

    total_overdue = Decimal("0")
    invoices = []

    today_dt = datetime.strptime(today, "%Y-%m-%d")

    for row in rows:
        outstanding = _d(row["outstanding_amount"])
        due_date = row["due_date"]
        due_dt = datetime.strptime(due_date, "%Y-%m-%d")
        days_overdue = (today_dt - due_dt).days

        total_overdue += outstanding

        # Place into bucket
        if days_overdue <= 30:
            buckets["0_30"]["count"] += 1
            buckets["0_30"]["total"] += outstanding
        elif days_overdue <= 60:
            buckets["31_60"]["count"] += 1
            buckets["31_60"]["total"] += outstanding
        elif days_overdue <= 90:
            buckets["61_90"]["count"] += 1
            buckets["61_90"]["total"] += outstanding
        else:
            buckets["90_plus"]["count"] += 1
            buckets["90_plus"]["total"] += outstanding

        invoices.append({
            "id": row["id"],
            "name": row["naming_series"] or "",
            "customer_name": row["customer_name"] or "",
            "grand_total": _s(_d(row["grand_total"])),
            "outstanding": _s(outstanding),
            "due_date": due_date,
            "days_overdue": days_overdue,
        })

    # Sort by days_overdue descending
    invoices.sort(key=lambda x: x["days_overdue"], reverse=True)

    # Format bucket totals as strings
    formatted_buckets = {}
    for key, bucket in buckets.items():
        formatted_buckets[key] = {
            "count": bucket["count"],
            "total": _s(bucket["total"]),
        }

    ok({
        "overdue_count": len(invoices),
        "total_overdue": _s(total_overdue),
        "buckets": formatted_buckets,
        "invoices": invoices,
    })


# ---------------------------------------------------------------------------
# Intercompany Elimination
# ---------------------------------------------------------------------------


def add_elimination_rule(conn, args):
    """Add an intercompany elimination rule."""
    name = getattr(args, "name", None) or getattr(args, "rule_name", None)
    source_company_id = args.company_id
    target_company_id = getattr(args, "target_company_id", None)
    source_account_id = getattr(args, "source_account_id", None)
    target_account_id = getattr(args, "target_account_id", None)

    if not name:
        err("--name is required")
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

    # Validate companies
    co_t = Table("company")
    co_sql = Q.from_(co_t).select(LiteralValue("1")).where(co_t.id == P()).get_sql()
    for cid, label in [(source_company_id, "Source"), (target_company_id, "Target")]:
        if not conn.execute(co_sql, (cid,)).fetchone():
            err(f"{label} company not found: {cid}")

    # Validate accounts
    acct_t = Table("account")
    acct_sql = (
        Q.from_(acct_t)
        .select(acct_t.id, acct_t.company_id, acct_t.root_type)
        .where(acct_t.id == P())
        .get_sql()
    )
    src_acct = conn.execute(acct_sql, (source_account_id,)).fetchone()
    if not src_acct:
        err(f"Source account not found: {source_account_id}")
    if src_acct["company_id"] != source_company_id:
        err("Source account does not belong to source company")

    tgt_acct = conn.execute(acct_sql, (target_account_id,)).fetchone()
    if not tgt_acct:
        err(f"Target account not found: {target_account_id}")
    if tgt_acct["company_id"] != target_company_id:
        err("Target account does not belong to target company")

    rule_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO elimination_rule
           (id, name, source_company_id, target_company_id,
            source_account_id, target_account_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (rule_id, name, source_company_id, target_company_id,
         source_account_id, target_account_id),
    )
    conn.commit()
    ok({"rule_id": rule_id, "name": name})


def list_elimination_rules(conn, args):
    """List intercompany elimination rules."""
    r_t = Table("elimination_rule").as_("r")
    sc_t = Table("company").as_("sc")
    tc_t = Table("company").as_("tc")
    sa_t = Table("account").as_("sa")
    ta_t = Table("account").as_("ta")

    rules_q = (
        Q.from_(r_t)
        .join(sc_t).on(sc_t.id == r_t.source_company_id)
        .join(tc_t).on(tc_t.id == r_t.target_company_id)
        .join(sa_t).on(sa_t.id == r_t.source_account_id)
        .join(ta_t).on(ta_t.id == r_t.target_account_id)
        .select(
            r_t.id, r_t.name, r_t.status,
            sc_t.name.as_("source_company"),
            tc_t.name.as_("target_company"),
            sa_t.name.as_("source_account"),
            ta_t.name.as_("target_account"),
        )
    )
    params = []
    if args.company_id:
        rules_q = rules_q.where(
            (r_t.source_company_id == P()) | (r_t.target_company_id == P())
        )
        params = [args.company_id, args.company_id]

    rows = conn.execute(rules_q.get_sql(), params).fetchall()
    ok({"rules": [dict(r) for r in rows], "total": len(rows)})


def run_elimination(conn, args):
    """Run intercompany elimination for a fiscal year.

    Creates GL entries to eliminate IC revenue/expense identified by
    elimination rules. Each elimination creates a balanced pair of GL entries:
      - DR source_account (income in source company — reduces revenue)
      - CR target_account (expense in target company — reduces expense)

    Idempotent: if elimination entries already exist for the rule + FY, skips.
    """
    fiscal_year_id = args.fiscal_year_id
    posting_date = getattr(args, "posting_date", None) or getattr(args, "as_of_date", None)

    if not fiscal_year_id:
        err("--fiscal-year-id is required")
    if not posting_date:
        err("--posting-date or --as-of-date is required")

    # Validate FY
    fy_t = Table("fiscal_year")
    fy_sql = Q.from_(fy_t).select(fy_t.star).where(fy_t.id == P()).get_sql()
    fy = conn.execute(fy_sql, (fiscal_year_id,)).fetchone()
    if not fy:
        err(f"Fiscal year not found: {fiscal_year_id}")

    # Get active elimination rules
    er_t = Table("elimination_rule")
    rules_sql = (
        Q.from_(er_t)
        .select(er_t.star)
        .where(er_t.status == "active")
        .get_sql()
    )
    rules = conn.execute(rules_sql).fetchall()
    if not rules:
        err("No active elimination rules found")

    entries_created = []

    for rule in rules:
        rule_id = rule["id"]
        source_account_id = rule["source_account_id"]
        target_account_id = rule["target_account_id"]

        # Check idempotency: skip if already eliminated for this rule + FY
        ee_t = Table("elimination_entry")
        existing_sql = (
            Q.from_(ee_t)
            .select(ee_t.id)
            .where(ee_t.elimination_rule_id == P())
            .where(ee_t.fiscal_year_id == P())
            .where(ee_t.status == "posted")
            .get_sql()
        )
        existing = conn.execute(existing_sql, (rule_id, fiscal_year_id)).fetchone()
        if existing:
            continue

        # Calculate IC amount: sum of GL credits on source income account
        # for intercompany sales invoices in this fiscal year period
        gl_t = Table("gl_entry")
        ic_sql = (
            Q.from_(gl_t)
            .select(
                fn.Coalesce(DecimalSum(gl_t.credit), "0").as_("total_credit"),
                fn.Coalesce(DecimalSum(gl_t.debit), "0").as_("total_debit"),
            )
            .where(gl_t.account_id == P())
            .where(gl_t.posting_date >= P())
            .where(gl_t.posting_date <= P())
            .where(gl_t.is_cancelled == 0)
            .where(gl_t.voucher_type != "elimination_entry")
            .get_sql()
        )
        ic_amount_row = conn.execute(
            ic_sql, (source_account_id, fy["start_date"], fy["end_date"])
        ).fetchone()

        total_credit = _d(ic_amount_row["total_credit"])
        total_debit = _d(ic_amount_row["total_debit"])
        # Net income in this account = credits - debits (for income accounts)
        elimination_amount = total_credit - total_debit

        if elimination_amount <= Decimal("0"):
            continue  # Nothing to eliminate

        amount_str = _s(elimination_amount)

        # Create elimination GL entries directly (cross-company, bypass insert_gl_entries)
        voucher_id = str(uuid.uuid4())

        # DR source account (income) — reduces revenue
        source_gl_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO gl_entry
               (id, posting_date, account_id, debit, credit,
                debit_base, credit_base, currency, exchange_rate,
                voucher_type, voucher_id, entry_set,
                remarks, fiscal_year, is_cancelled)
               VALUES (?, ?, ?, ?, '0', ?, '0', 'USD', '1',
                       'elimination_entry', ?, 'primary',
                       ?, ?, 0)""",
            (source_gl_id, posting_date, source_account_id,
             amount_str, amount_str,
             voucher_id,
             f"IC elimination: {rule['name']}", fy["name"]),
        )

        # CR target account (expense) — reduces expense
        target_gl_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO gl_entry
               (id, posting_date, account_id, debit, credit,
                debit_base, credit_base, currency, exchange_rate,
                voucher_type, voucher_id, entry_set,
                remarks, fiscal_year, is_cancelled)
               VALUES (?, ?, ?, '0', ?, '0', ?, 'USD', '1',
                       'elimination_entry', ?, 'primary',
                       ?, ?, 0)""",
            (target_gl_id, posting_date, target_account_id,
             amount_str, amount_str,
             voucher_id,
             f"IC elimination: {rule['name']}", fy["name"]),
        )

        # Record elimination entry
        entry_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO elimination_entry
               (id, elimination_rule_id, fiscal_year_id, posting_date,
                amount, source_gl_entry_id, target_gl_entry_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (entry_id, rule_id, fiscal_year_id, posting_date,
             amount_str, source_gl_id, target_gl_id),
        )

        entries_created.append({
            "rule_name": rule["name"],
            "amount": amount_str,
            "source_gl_id": source_gl_id,
            "target_gl_id": target_gl_id,
            "entry_id": entry_id,
        })

    conn.commit()
    ok({
        "fiscal_year": fy["name"],
        "posting_date": posting_date,
        "eliminations": entries_created,
        "total_eliminated": len(entries_created),
    })


def list_elimination_entries(conn, args):
    """List elimination entries for audit trail."""
    fiscal_year_id = args.fiscal_year_id

    e_t = Table("elimination_entry").as_("e")
    r_t = Table("elimination_rule").as_("r")
    sc_t = Table("company").as_("sc")
    tc_t = Table("company").as_("tc")
    sa_t = Table("account").as_("sa")
    ta_t = Table("account").as_("ta")
    fy_t = Table("fiscal_year").as_("fy")

    entries_q = (
        Q.from_(e_t)
        .join(r_t).on(r_t.id == e_t.elimination_rule_id)
        .join(sc_t).on(sc_t.id == r_t.source_company_id)
        .join(tc_t).on(tc_t.id == r_t.target_company_id)
        .join(sa_t).on(sa_t.id == r_t.source_account_id)
        .join(ta_t).on(ta_t.id == r_t.target_account_id)
        .join(fy_t).on(fy_t.id == e_t.fiscal_year_id)
        .select(
            e_t.id, e_t.posting_date, e_t.amount, e_t.status,
            r_t.name.as_("rule_name"),
            sc_t.name.as_("source_company"),
            tc_t.name.as_("target_company"),
            sa_t.name.as_("source_account"),
            ta_t.name.as_("target_account"),
            fy_t.name.as_("fiscal_year"),
        )
    )
    params = []
    if fiscal_year_id:
        entries_q = entries_q.where(e_t.fiscal_year_id == P())
        params.append(fiscal_year_id)

    entries_q = entries_q.orderby(e_t.posting_date, order=Order.desc)
    rows = conn.execute(entries_q.get_sql(), params).fetchall()
    ok({"entries": [dict(r) for r in rows], "total": len(rows)})


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

ACTIONS = {
    "trial-balance": trial_balance,
    "profit-and-loss": profit_and_loss,
    "balance-sheet": balance_sheet,
    "cash-flow": cash_flow,
    "general-ledger": general_ledger,
    "ar-aging": ar_aging,
    "ap-aging": ap_aging,
    "budget-vs-actual": budget_vs_actual,
    "budget-variance": budget_vs_actual,  # alias
    "party-ledger": party_ledger,
    "tax-summary": tax_summary,
    "payment-summary": payment_summary,
    "gl-summary": gl_summary,
    "comparative-pl": comparative_pl,
    "check-overdue": check_overdue,
    "add-elimination-rule": add_elimination_rule,
    "list-elimination-rules": list_elimination_rules,
    "run-elimination": run_elimination,
    "list-elimination-entries": list_elimination_entries,
    "status": status_action,
}


def main():
    parser = argparse.ArgumentParser(description="ERPClaw Reports Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Common filters
    parser.add_argument("--company-id")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--as-of-date")
    parser.add_argument("--account-id")
    parser.add_argument("--cost-center-id")
    parser.add_argument("--project-id")

    # General ledger
    parser.add_argument("--party-type")
    parser.add_argument("--party-id")
    parser.add_argument("--voucher-type")

    # Aging
    parser.add_argument("--customer-id")
    parser.add_argument("--supplier-id")
    parser.add_argument("--aging-buckets", default="30,60,90,120")

    # Budget
    parser.add_argument("--fiscal-year-id")

    # P&L periodicity
    parser.add_argument("--periodicity", default="annual")

    # Comparative
    parser.add_argument("--periods")  # JSON string

    # Elimination
    parser.add_argument("--name")
    parser.add_argument("--target-company-id")
    parser.add_argument("--source-account-id")
    parser.add_argument("--target-account-id")
    parser.add_argument("--posting-date")

    # Pagination
    parser.add_argument("--limit", default="100")
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
