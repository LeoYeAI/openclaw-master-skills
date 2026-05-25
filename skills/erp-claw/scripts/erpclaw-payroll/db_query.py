#!/usr/bin/env python3
"""ERPClaw Payroll Skill -- db_query.py

US payroll management: salary components, structures, assignments,
payroll runs, salary slip generation, FICA/income-tax withholding,
FUTA/SUTA configuration, and W-2 data generation.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.gl_posting import insert_gl_entries, reverse_gl_entries
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query import (Q, P, Table, Field, fn, Case, Order, Criterion, Not, NULL,
                                    DecimalSum, DecimalAbs, insert_row, update_row, dynamic_update)
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw-setup first: clawhub install erpclaw-setup", "suggestion": "clawhub install erpclaw-setup"}))
    sys.exit(1)

REQUIRED_TABLES = ["company", "employee"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_COMPONENT_TYPES = ("earning", "deduction", "employer_contribution")
VALID_PAYROLL_FREQUENCIES = ("monthly", "biweekly", "weekly")
VALID_PAYROLL_STATUSES = ("draft", "submitted", "paid", "cancelled")
VALID_TAX_JURISDICTIONS = ("federal", "state")
VALID_FILING_STATUSES = (
    "single", "married_jointly", "married_separately", "head_of_household",
)
VALID_SLIP_COMPONENT_TYPES = ("earning", "deduction")


def _parse_json_arg(value, name):
    """Parse a JSON string argument, returning the parsed value or erroring."""
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        err(f"Invalid JSON for --{name}: {value}")


def _now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _validate_date(value: str, label: str) -> date:
    """Parse and validate an ISO date string, erroring on failure."""
    if not value:
        err(f"--{label} is required")
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        err(f"Invalid {label} format: {value}. Use YYYY-MM-DD")


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_company_exists(conn, company_id: str):
    """Validate that a company exists and return the row, or error."""
    t = Table("company")
    q = Q.from_(t).select(t.id).where(t.id == P())
    company = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not company:
        err(f"Company {company_id} not found")
    return company


def _validate_employee_exists(conn, employee_id: str):
    """Validate that an employee exists and return the full row, or error."""
    t = Table("employee")
    q = Q.from_(t).select(t.star).where(t.id == P())
    emp = conn.execute(q.get_sql(), (employee_id,)).fetchone()
    if not emp:
        err(f"Employee {employee_id} not found",
             suggestion="Use 'list employees' to see available employees.")
    return emp


def _validate_salary_component_exists(conn, component_id: str):
    """Validate that a salary component exists and return the row, or error."""
    t = Table("salary_component")
    q = Q.from_(t).select(t.star).where(t.id == P())
    comp = conn.execute(q.get_sql(), (component_id,)).fetchone()
    if not comp:
        err(f"Salary component {component_id} not found")
    return comp


def _validate_salary_structure_exists(conn, structure_id: str):
    """Validate that a salary structure exists and return the row, or error."""
    t = Table("salary_structure")
    q = Q.from_(t).select(t.star).where(t.id == P())
    ss = conn.execute(q.get_sql(), (structure_id,)).fetchone()
    if not ss:
        err(f"Salary structure {structure_id} not found")
    return ss


def _validate_salary_assignment_exists(conn, assignment_id: str):
    """Validate that a salary assignment exists and return the row, or error."""
    t = Table("salary_assignment")
    q = Q.from_(t).select(t.star).where(t.id == P())
    sa = conn.execute(q.get_sql(), (assignment_id,)).fetchone()
    if not sa:
        err(f"Salary assignment {assignment_id} not found")
    return sa


def _validate_payroll_run_exists(conn, payroll_run_id: str):
    """Validate that a payroll run exists and return the row, or error."""
    t = Table("payroll_run")
    q = Q.from_(t).select(t.star).where(t.id == P())
    pr = conn.execute(q.get_sql(), (payroll_run_id,)).fetchone()
    if not pr:
        err(f"Payroll run {payroll_run_id} not found")
    return pr


def _validate_account_exists(conn, account_id: str, label: str = "Account"):
    """Validate that an account exists and return the row, or error."""
    t = Table("account")
    q = Q.from_(t).select(t.star).where(t.id == P())
    acct = conn.execute(q.get_sql(), (account_id,)).fetchone()
    if not acct:
        err(f"{label} account {account_id} not found")
    return acct


def _get_fiscal_year_row(conn, target_date: str) -> dict | None:
    """Return the full fiscal year row for a date, or None."""
    t = Table("fiscal_year")
    q = (Q.from_(t)
         .select(t.id, t.name, t.start_date, t.end_date, t.company_id)
         .where(t.start_date <= P())
         .where(t.end_date >= P())
         .where(t.is_closed == 0))
    fy = conn.execute(q.get_sql(), (target_date, target_date)).fetchone()
    return row_to_dict(fy) if fy else None


def _get_cost_center(conn, company_id: str) -> str | None:
    """Return the first non-group cost center for a company, or None."""
    t = Table("cost_center")
    q = (Q.from_(t).select(t.id)
         .where(t.company_id == P())
         .where(t.is_group == 0)
         .limit(1))
    cc = conn.execute(q.get_sql(), (company_id,)).fetchone()
    return cc["id"] if cc else None


def _get_employee_company_id(conn, employee_id: str) -> str:
    """Return the company_id for an employee, or error if not found."""
    t = Table("employee")
    q = Q.from_(t).select(t.company_id).where(t.id == P())
    emp = conn.execute(q.get_sql(), (employee_id,)).fetchone()
    if not emp:
        err(f"Employee {employee_id} not found")
    return emp["company_id"]


# ---------------------------------------------------------------------------
# 1. add-salary-component
# ---------------------------------------------------------------------------

def add_salary_component(conn, args):
    """Create a new salary component (earning, deduction, or employer_contribution).

    Required: --name, --component-type
    Optional: --is-tax-applicable, --is-statutory, --is-pre-tax,
              --variable-based-on-taxable-salary, --depends-on-payment-days,
              --gl-account-id, --description
    """
    if not args.name:
        err("--name is required")
    if not args.component_type:
        err("--component-type is required")

    name = args.name.strip()
    component_type = args.component_type.strip().lower()

    if component_type not in VALID_COMPONENT_TYPES:
        err(
            f"Invalid component type '{component_type}'. "
            f"Valid: {VALID_COMPONENT_TYPES}"
        )

    # Check uniqueness
    sc_t = Table("salary_component")
    q = Q.from_(sc_t).select(sc_t.id).where(sc_t.name == P())
    existing = conn.execute(q.get_sql(), (name,)).fetchone()
    if existing:
        err(f"Salary component with name '{name}' already exists")

    # Validate GL account if provided
    if args.gl_account_id:
        _validate_account_exists(conn, args.gl_account_id, "GL")

    # Parse boolean flags (accept 1/0, true/false, yes/no)
    def _parse_bool(value, default=None):
        if value is None:
            return default
        if isinstance(value, bool):
            return 1 if value else 0
        s = str(value).strip().lower()
        if s in ("1", "true", "yes"):
            return 1
        if s in ("0", "false", "no"):
            return 0
        return default

    is_tax_applicable = _parse_bool(args.is_tax_applicable, 1)
    is_statutory = _parse_bool(args.is_statutory, 0)
    is_pre_tax = _parse_bool(args.is_pre_tax, 0)
    variable_based = _parse_bool(args.variable_based_on_taxable_salary, 0)
    depends_on_payment_days = _parse_bool(args.depends_on_payment_days, 1)
    is_supplemental = _parse_bool(
        getattr(args, "is_supplemental", None), 0
    )

    component_id = str(uuid.uuid4())
    now = _now_iso()

    ins_sql, _ = insert_row("salary_component", {
        "id": P(), "name": P(), "component_type": P(),
        "is_tax_applicable": P(), "is_statutory": P(), "is_pre_tax": P(),
        "variable_based_on_taxable_salary": P(), "depends_on_payment_days": P(),
        "is_supplemental": P(),
        "gl_account_id": P(), "description": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(ins_sql, (
        component_id, name, component_type,
        is_tax_applicable, is_statutory, is_pre_tax, variable_based,
        depends_on_payment_days, is_supplemental, args.gl_account_id,
        args.description, now, now,
    ))
    conn.commit()

    audit(conn, "erpclaw-payroll", "add-salary-component", "salary_component", component_id,
           new_values={"name": name, "component_type": component_type})
    conn.commit()

    ok({
        "salary_component_id": component_id,
        "name": name,
        "component_type": component_type,
    })


# ---------------------------------------------------------------------------
# 2. list-salary-components
# ---------------------------------------------------------------------------

def list_salary_components(conn, args):
    """List salary components with optional type filter.

    Optional: --component-type (filter), --limit, --offset, --search
    """
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    sc_t = Table("salary_component")
    params = []

    # Build base queries
    count_q = Q.from_(sc_t).select(fn.Count("*"))
    list_q = Q.from_(sc_t).select(
        sc_t.id, sc_t.name, sc_t.component_type, sc_t.is_tax_applicable,
        sc_t.is_statutory, sc_t.is_pre_tax, sc_t.variable_based_on_taxable_salary,
        sc_t.depends_on_payment_days, sc_t.gl_account_id, sc_t.description,
        sc_t.created_at, sc_t.updated_at,
    )

    if args.component_type:
        ct = args.component_type.strip().lower()
        if ct not in VALID_COMPONENT_TYPES:
            err(
                f"Invalid component type filter '{ct}'. "
                f"Valid: {VALID_COMPONENT_TYPES}"
            )
        count_q = count_q.where(sc_t.component_type == P())
        list_q = list_q.where(sc_t.component_type == P())
        params.append(ct)

    if args.search:
        count_q = count_q.where(sc_t.name.like(P()))
        list_q = list_q.where(sc_t.name.like(P()))
        params.append(f"%{args.search}%")

    # Count total
    total = conn.execute(count_q.get_sql(), params).fetchone()[0]

    # Fetch rows
    list_q = list_q.orderby(sc_t.name).limit(P()).offset(P())
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({
        "count": total,
        "components": [row_to_dict(r) for r in rows],
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 3. add-salary-structure
# ---------------------------------------------------------------------------

def add_salary_structure(conn, args):
    """Create a salary structure with component details.

    Required: --name, --company-id, --components (JSON array)
    Optional: --payroll-frequency (default: monthly)

    Components JSON format:
    [
        {"salary_component_id": "...", "amount": "5000"},
        {"salary_component_id": "...", "percentage": "40", "base_component_id": "..."},
        {"salary_component_id": "...", "formula": "base * 0.1"}
    ]

    Each component may have at most ONE of: amount, percentage, formula.
    If percentage is given, base_component_id specifies which component to
    compute the percentage against.
    """
    if not args.name:
        err("--name is required")
    if not args.company_id:
        err("--company-id is required")
    if not args.components:
        err("--components is required (JSON array)")

    name = args.name.strip()
    company_id = args.company_id
    payroll_frequency = (args.payroll_frequency or "monthly").strip().lower()

    if payroll_frequency not in VALID_PAYROLL_FREQUENCIES:
        err(
            f"Invalid payroll frequency '{payroll_frequency}'. "
            f"Valid: {VALID_PAYROLL_FREQUENCIES}"
        )

    # Validate company
    _validate_company_exists(conn, company_id)

    # Check uniqueness
    ss_t = Table("salary_structure")
    q = Q.from_(ss_t).select(ss_t.id).where(ss_t.name == P())
    existing = conn.execute(q.get_sql(), (name,)).fetchone()
    if existing:
        err(f"Salary structure with name '{name}' already exists")

    # Parse components JSON
    components = _parse_json_arg(args.components, "components")
    if not isinstance(components, list):
        err("--components must be a JSON array")
    if len(components) == 0:
        err("--components must contain at least one component")

    # Validate each component entry
    validated_components = []
    seen_component_ids = set()
    for idx, comp in enumerate(components):
        if not isinstance(comp, dict):
            err(f"Component at index {idx} must be an object")

        comp_id = comp.get("salary_component_id")
        if not comp_id:
            err(f"Component at index {idx} missing 'salary_component_id'")

        # Validate component exists
        sc_t2 = Table("salary_component")
        sc_q = Q.from_(sc_t2).select(sc_t2.id, sc_t2.name, sc_t2.component_type).where(sc_t2.id == P())
        sc_row = conn.execute(sc_q.get_sql(), (comp_id,)).fetchone()
        if not sc_row:
            err(f"Salary component {comp_id} (index {idx}) not found")

        # Prevent duplicate components in the same structure
        if comp_id in seen_component_ids:
            err(
                f"Duplicate salary component '{sc_row['name']}' at index {idx}. "
                f"Each component can only appear once in a structure"
            )
        seen_component_ids.add(comp_id)

        # Validate that at most one of amount/percentage/formula is provided
        has_amount = comp.get("amount") is not None
        has_percentage = comp.get("percentage") is not None
        has_formula = comp.get("formula") is not None

        specifiers = sum([has_amount, has_percentage, has_formula])
        if specifiers > 1:
            err(
                f"Component '{sc_row['name']}' (index {idx}) has multiple specifiers. "
                f"Provide at most one of: amount, percentage, formula"
            )

        # Validate amount is a valid decimal if provided
        amount_val = None
        if has_amount:
            try:
                amount_val = to_decimal(comp["amount"])
            except (ValueError, TypeError):
                err(f"Invalid amount '{comp['amount']}' for component at index {idx}")

        # Validate percentage
        percentage_val = None
        if has_percentage:
            try:
                percentage_val = to_decimal(comp["percentage"])
            except (ValueError, TypeError):
                err(f"Invalid percentage '{comp['percentage']}' for component at index {idx}")
            if percentage_val < Decimal("0") or percentage_val > Decimal("100"):
                err(
                    f"Percentage {percentage_val} out of range [0, 100] "
                    f"for component at index {idx}"
                )

        # Validate base_component_id if given with percentage
        base_component_id = comp.get("base_component_id")
        if base_component_id:
            bc_t = Table("salary_component")
            bc_q = Q.from_(bc_t).select(bc_t.id).where(bc_t.id == P())
            base_comp = conn.execute(bc_q.get_sql(), (base_component_id,)).fetchone()
            if not base_comp:
                err(f"Base component {base_component_id} (index {idx}) not found")

        sort_order = comp.get("sort_order", idx)

        validated_components.append({
            "salary_component_id": comp_id,
            "amount": str(amount_val) if amount_val is not None else None,
            "percentage": str(percentage_val) if percentage_val is not None else None,
            "formula": comp.get("formula"),
            "base_component_id": base_component_id,
            "sort_order": int(sort_order),
        })

    # Create salary structure
    structure_id = str(uuid.uuid4())
    now = _now_iso()

    ins_ss_sql, _ = insert_row("salary_structure", {
        "id": P(), "name": P(), "payroll_frequency": P(),
        "currency": P(), "company_id": P(), "is_active": P(),
        "created_at": P(), "updated_at": P(),
    })
    conn.execute(ins_ss_sql, (structure_id, name, payroll_frequency,
                              "USD", company_id, 1, now, now))

    # Insert salary structure details
    ins_det_sql, _ = insert_row("salary_structure_detail", {
        "id": P(), "salary_structure_id": P(), "salary_component_id": P(),
        "amount": P(), "percentage": P(), "formula": P(),
        "base_component_id": P(), "sort_order": P(),
    })
    for comp in validated_components:
        detail_id = str(uuid.uuid4())
        conn.execute(ins_det_sql, (
            detail_id, structure_id, comp["salary_component_id"],
            comp["amount"], comp["percentage"], comp["formula"],
            comp["base_component_id"], comp["sort_order"],
        ))

    conn.commit()

    audit(conn, "erpclaw-payroll", "add-salary-structure", "salary_structure", structure_id,
           new_values={"name": name, "component_count": len(validated_components)})
    conn.commit()

    ok({
        "salary_structure_id": structure_id,
        "name": name,
        "payroll_frequency": payroll_frequency,
        "component_count": len(validated_components),
    })


# ---------------------------------------------------------------------------
# 4. get-salary-structure
# ---------------------------------------------------------------------------

def get_salary_structure(conn, args):
    """Retrieve a salary structure with its component breakdown.

    Required: --salary-structure-id
    """
    if not args.salary_structure_id:
        err("--salary-structure-id is required")

    ss = _validate_salary_structure_exists(conn, args.salary_structure_id)
    ss_dict = row_to_dict(ss)

    # Fetch component details with component names
    ssd = Table("salary_structure_detail")
    sc = Table("salary_component")
    det_q = (Q.from_(ssd)
             .join(sc).on(sc.id == ssd.salary_component_id)
             .select(ssd.id, ssd.salary_component_id,
                     sc.name.as_("component_name"), sc.component_type,
                     ssd.amount, ssd.percentage, ssd.formula,
                     ssd.base_component_id, ssd.sort_order)
             .where(ssd.salary_structure_id == P())
             .orderby(ssd.sort_order))
    details = conn.execute(det_q.get_sql(), (args.salary_structure_id,)).fetchall()

    # Enrich base_component names
    sc_name_q = Q.from_(sc).select(sc.name).where(sc.id == P())
    components = []
    for d in details:
        comp_dict = row_to_dict(d)
        if comp_dict.get("base_component_id"):
            base_row = conn.execute(sc_name_q.get_sql(),
                                    (comp_dict["base_component_id"],)).fetchone()
            comp_dict["base_component_name"] = base_row["name"] if base_row else None
        else:
            comp_dict["base_component_name"] = None
        components.append(comp_dict)

    ss_dict["components"] = components
    ss_dict["component_count"] = len(components)

    ok({"salary_structure": ss_dict})


# ---------------------------------------------------------------------------
# 5. list-salary-structures
# ---------------------------------------------------------------------------

def list_salary_structures(conn, args):
    """List salary structures with optional company filter.

    Optional: --company-id, --limit, --offset, --search
    """
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    ss = Table("salary_structure").as_("ss")
    params = []

    count_q = Q.from_(ss).select(fn.Count("*"))
    # raw SQL — correlated subquery for component_count not easily expressed in PyPika
    list_q = Q.from_(ss).select(
        ss.id, ss.name, ss.payroll_frequency, ss.currency,
        ss.company_id, ss.is_active, ss.created_at, ss.updated_at,
        LiteralValue(
            '(SELECT COUNT(*) FROM "salary_structure_detail" "ssd"'
            ' WHERE "ssd"."salary_structure_id"="ss"."id")'
        ).as_("component_count"),
    )

    if args.company_id:
        count_q = count_q.where(ss.company_id == P())
        list_q = list_q.where(ss.company_id == P())
        params.append(args.company_id)

    if args.search:
        count_q = count_q.where(ss.name.like(P()))
        list_q = list_q.where(ss.name.like(P()))
        params.append(f"%{args.search}%")

    total = conn.execute(count_q.get_sql(), params).fetchone()[0]

    list_q = list_q.orderby(ss.name).limit(P()).offset(P())
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()

    ok({
        "count": total,
        "structures": [row_to_dict(r) for r in rows],
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 6. add-salary-assignment
# ---------------------------------------------------------------------------

def add_salary_assignment(conn, args):
    """Assign a salary structure to an employee with a base amount.

    Required: --employee-id, --salary-structure-id, --base-amount, --effective-from
    Optional: --effective-to

    If the employee already has an active assignment, the previous one is
    auto-closed by setting its effective_to to the day before the new
    effective_from date.
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.salary_structure_id:
        err("--salary-structure-id is required")
    if not args.base_amount:
        err("--base-amount is required")
    if not args.effective_from:
        err("--effective-from is required")

    # Validate employee
    emp = _validate_employee_exists(conn, args.employee_id)
    employee_id = emp["id"]
    company_id = emp["company_id"]

    # Validate salary structure
    ss = _validate_salary_structure_exists(conn, args.salary_structure_id)
    structure_id = ss["id"]

    # Validate structure belongs to the same company as employee
    if ss["company_id"] != company_id:
        err(
            f"Salary structure belongs to company {ss['company_id']} but "
            f"employee belongs to company {company_id}. They must match."
        )

    # Validate base amount
    try:
        base_amount = to_decimal(args.base_amount)
    except (ValueError, TypeError):
        err(f"Invalid base amount: {args.base_amount}")
    if base_amount < Decimal("0"):
        err("Base amount cannot be negative")

    # Validate dates
    effective_from = _validate_date(args.effective_from, "effective-from")

    effective_to = None
    if args.effective_to:
        effective_to = _validate_date(args.effective_to, "effective-to")
        if effective_to < effective_from:
            err(
                f"effective-to ({args.effective_to}) must be on or after "
                f"effective-from ({args.effective_from})"
            )

    # Auto-close previous assignment: find the most recent active assignment
    # for this employee that has no effective_to or whose effective_to is
    # on or after the new effective_from
    # raw SQL — uses IS NULL in OR clause which PyPika handles differently
    previous = conn.execute(
        """SELECT id, effective_from, effective_to
           FROM salary_assignment
           WHERE employee_id = ?
             AND (effective_to IS NULL OR effective_to >= ?)
           ORDER BY effective_from DESC
           LIMIT 1""",
        (employee_id, args.effective_from),
    ).fetchone()

    if previous:
        # Close the previous assignment the day before the new one starts
        close_date = (effective_from - timedelta(days=1)).isoformat()
        sa_upd = update_row("salary_assignment",
                            data={"effective_to": P(), "updated_at": P()},
                            where={"id": P()})
        conn.execute(sa_upd, (close_date, _now_iso(), previous["id"]))

    # Create new assignment
    assignment_id = str(uuid.uuid4())
    now = _now_iso()

    ins_sa_sql, _ = insert_row("salary_assignment", {
        "id": P(), "employee_id": P(), "salary_structure_id": P(),
        "base_amount": P(), "effective_from": P(), "effective_to": P(),
        "currency": P(), "company_id": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(ins_sa_sql, (
        assignment_id, employee_id, structure_id,
        str(round_currency(base_amount)),
        args.effective_from, args.effective_to,
        "USD", company_id, now, now,
    ))
    conn.commit()

    audit(conn, "erpclaw-payroll", "add-salary-assignment", "salary_assignment", assignment_id,
           new_values={
               "employee_id": employee_id,
               "salary_structure_id": structure_id,
               "base_amount": str(round_currency(base_amount)),
               "effective_from": args.effective_from,
           },
           description=(
               f"Auto-closed previous assignment {previous['id']}"
               if previous else ""
           ))
    conn.commit()

    result = {
        "salary_assignment_id": assignment_id,
        "employee_id": employee_id,
        "salary_structure_id": structure_id,
        "base_amount": str(round_currency(base_amount)),
        "effective_from": args.effective_from,
        "effective_to": args.effective_to,
    }
    if previous:
        result["previous_assignment_closed"] = previous["id"]

    ok(result)


# ---------------------------------------------------------------------------
# 7. list-salary-assignments
# ---------------------------------------------------------------------------

def list_salary_assignments(conn, args):
    """List salary assignments with optional filters.

    Optional: --employee-id, --company-id, --limit, --offset, --from-date, --to-date
    """
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    # raw SQL — IS NULL in OR clause used for date range filters
    conditions = []
    params = []

    if args.employee_id:
        conditions.append("sa.employee_id = ?")
        params.append(args.employee_id)

    if args.company_id:
        conditions.append("sa.company_id = ?")
        params.append(args.company_id)

    # Date range filters: find assignments overlapping the period
    if args.from_date:
        # Assignment is still active on or after from_date
        conditions.append("(sa.effective_to IS NULL OR sa.effective_to >= ?)")
        params.append(args.from_date)

    if args.to_date:
        # Assignment started on or before to_date
        conditions.append("sa.effective_from <= ?")
        params.append(args.to_date)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    total = conn.execute(
        f"SELECT COUNT(*) FROM salary_assignment sa {where}", params,
    ).fetchone()[0]

    rows = conn.execute(
        f"""SELECT sa.id, sa.employee_id, sa.salary_structure_id,
               sa.base_amount, sa.effective_from, sa.effective_to,
               sa.currency, sa.company_id, sa.created_at, sa.updated_at,
               e.full_name AS employee_name,
               ss.name AS salary_structure_name
           FROM salary_assignment sa
           JOIN employee e ON e.id = sa.employee_id
           JOIN salary_structure ss ON ss.id = sa.salary_structure_id
           {where}
           ORDER BY sa.effective_from DESC
           LIMIT ? OFFSET ?""",
        params + [limit, offset],
    ).fetchall()

    ok({
        "count": total,
        "assignments": [row_to_dict(r) for r in rows],
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 14. add-income-tax-slab
# ---------------------------------------------------------------------------

def add_income_tax_slab(conn, args):
    """Create a federal or state income tax slab with rate brackets.

    Required: --name, --tax-jurisdiction (federal/state), --effective-from
    Optional: --filing-status, --state-code, --standard-deduction, --rates (JSON)

    Rates JSON format:
    [
        {"from_amount": "0", "to_amount": "11600", "rate": "10"},
        {"from_amount": "11600", "to_amount": "47150", "rate": "12"},
        {"from_amount": "47150", "to_amount": null, "rate": "22"}
    ]

    The last bracket may have to_amount = null (unbounded upper end).
    Brackets must be contiguous: each from_amount == previous to_amount.
    Rates are percentages (e.g., "10" = 10%).
    """
    if not args.name:
        err("--name is required")
    if not args.tax_jurisdiction:
        err("--tax-jurisdiction is required")
    if not args.effective_from:
        err("--effective-from is required")

    name = args.name.strip()
    tax_jurisdiction = args.tax_jurisdiction.strip().lower()
    effective_from = args.effective_from.strip()

    if tax_jurisdiction not in VALID_TAX_JURISDICTIONS:
        err(
            f"Invalid tax jurisdiction '{tax_jurisdiction}'. "
            f"Valid: {VALID_TAX_JURISDICTIONS}"
        )

    # Validate date
    _validate_date(effective_from, "effective-from")

    # State code required for state jurisdiction
    state_code = args.state_code
    if tax_jurisdiction == "state" and not state_code:
        err("--state-code is required for state tax jurisdiction")
    if tax_jurisdiction == "federal" and state_code:
        # Allow but ignore for federal; set to None
        state_code = None

    # Validate filing status
    filing_status = args.filing_status
    if filing_status:
        filing_status = filing_status.strip().lower()
        if filing_status not in VALID_FILING_STATUSES:
            err(
                f"Invalid filing status '{filing_status}'. "
                f"Valid: {VALID_FILING_STATUSES}"
            )

    # Standard deduction
    standard_deduction = "0"
    if args.standard_deduction:
        try:
            sd = to_decimal(args.standard_deduction)
            if sd < Decimal("0"):
                err("Standard deduction cannot be negative")
            standard_deduction = str(round_currency(sd))
        except (ValueError, TypeError):
            err(f"Invalid standard deduction: {args.standard_deduction}")

    # Parse rates
    rates = _parse_json_arg(args.rates, "rates")

    # Validate rates if provided
    validated_rates = []
    if rates:
        if not isinstance(rates, list):
            err("--rates must be a JSON array")
        if len(rates) == 0:
            err("--rates array must not be empty")

        prev_to_amount = None
        for idx, rate_entry in enumerate(rates):
            if not isinstance(rate_entry, dict):
                err(f"Rate entry at index {idx} must be an object")

            # from_amount
            from_amt_raw = rate_entry.get("from_amount", "0")
            try:
                from_amt = to_decimal(from_amt_raw)
            except (ValueError, TypeError):
                err(f"Invalid from_amount '{from_amt_raw}' at rate index {idx}")

            # to_amount (can be None for the last bracket)
            to_amt_raw = rate_entry.get("to_amount")
            to_amt = None
            if to_amt_raw is not None:
                try:
                    to_amt = to_decimal(to_amt_raw)
                except (ValueError, TypeError):
                    err(f"Invalid to_amount '{to_amt_raw}' at rate index {idx}")
                if to_amt <= from_amt:
                    err(
                        f"to_amount ({to_amt}) must be greater than from_amount "
                        f"({from_amt}) at rate index {idx}"
                    )

            # rate (percentage)
            rate_raw = rate_entry.get("rate", "0")
            try:
                rate_val = to_decimal(rate_raw)
            except (ValueError, TypeError):
                err(f"Invalid rate '{rate_raw}' at rate index {idx}")
            if rate_val < Decimal("0") or rate_val > Decimal("100"):
                err(f"Rate {rate_val}% out of range [0, 100] at index {idx}")

            # Check contiguity: from_amount should equal previous to_amount
            if prev_to_amount is not None and from_amt != prev_to_amount:
                err(
                    f"Rate brackets are not contiguous at index {idx}: "
                    f"expected from_amount={prev_to_amount}, got {from_amt}"
                )

            prev_to_amount = to_amt

            validated_rates.append({
                "from_amount": str(round_currency(from_amt)),
                "to_amount": str(round_currency(to_amt)) if to_amt is not None else None,
                "rate": str(round_currency(rate_val)),
            })

    # Create income tax slab
    slab_id = str(uuid.uuid4())
    now = _now_iso()

    ins_slab_sql, _ = insert_row("income_tax_slab", {
        "id": P(), "name": P(), "tax_jurisdiction": P(),
        "state_code": P(), "filing_status": P(), "effective_from": P(),
        "standard_deduction": P(), "is_active": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(ins_slab_sql, (
        slab_id, name, tax_jurisdiction, state_code, filing_status,
        effective_from, standard_deduction, 1, now, now,
    ))

    # Insert rate brackets
    ins_rate_sql, _ = insert_row("income_tax_slab_rate", {
        "id": P(), "slab_id": P(), "from_amount": P(), "to_amount": P(), "rate": P(),
    })
    for rate_entry in validated_rates:
        rate_id = str(uuid.uuid4())
        conn.execute(ins_rate_sql, (
            rate_id, slab_id,
            rate_entry["from_amount"],
            rate_entry["to_amount"],
            rate_entry["rate"],
        ))

    conn.commit()

    audit(conn, "erpclaw-payroll", "add-income-tax-slab", "income_tax_slab", slab_id,
           new_values={
               "name": name,
               "tax_jurisdiction": tax_jurisdiction,
               "filing_status": filing_status,
               "rate_count": len(validated_rates),
           })
    conn.commit()

    ok({
        "income_tax_slab_id": slab_id,
        "name": name,
        "tax_jurisdiction": tax_jurisdiction,
        "state_code": state_code,
        "filing_status": filing_status,
        "effective_from": effective_from,
        "standard_deduction": standard_deduction,
        "rate_count": len(validated_rates),
    })


# ---------------------------------------------------------------------------
# 15. update-fica-config
# ---------------------------------------------------------------------------

def update_fica_config(conn, args):
    """Update Social Security and Medicare rates for a tax year.

    Required: --tax-year, --ss-wage-base, --ss-employee-rate, --ss-employer-rate,
              --medicare-employee-rate, --medicare-employer-rate,
              --additional-medicare-threshold, --additional-medicare-rate

    Uses UPSERT: inserts a new row if the tax year doesn't exist,
    or updates the existing row if it does.

    All rates are percentages (e.g., "6.2" = 6.2%).
    """
    if args.tax_year is None:
        err("--tax-year is required")
    if not args.ss_wage_base:
        err("--ss-wage-base is required")
    if not args.ss_employee_rate:
        err("--ss-employee-rate is required")
    if not args.ss_employer_rate:
        err("--ss-employer-rate is required")
    if not args.medicare_employee_rate:
        err("--medicare-employee-rate is required")
    if not args.medicare_employer_rate:
        err("--medicare-employer-rate is required")
    if not args.additional_medicare_threshold:
        err("--additional-medicare-threshold is required")
    if not args.additional_medicare_rate:
        err("--additional-medicare-rate is required")

    # Validate tax year
    try:
        tax_year = int(args.tax_year)
    except (ValueError, TypeError):
        err(f"Invalid tax year: {args.tax_year}")
    if tax_year < 2000 or tax_year > 2100:
        err(f"Tax year {tax_year} out of reasonable range [2000, 2100]")

    # Validate all decimal fields
    fields = {
        "ss_wage_base": args.ss_wage_base,
        "ss_employee_rate": args.ss_employee_rate,
        "ss_employer_rate": args.ss_employer_rate,
        "medicare_employee_rate": args.medicare_employee_rate,
        "medicare_employer_rate": args.medicare_employer_rate,
        "additional_medicare_threshold": args.additional_medicare_threshold,
        "additional_medicare_rate": args.additional_medicare_rate,
    }

    validated = {}
    for field_name, field_value in fields.items():
        try:
            val = to_decimal(field_value)
        except (ValueError, TypeError):
            err(f"Invalid value for --{field_name.replace('_', '-')}: {field_value}")
        if val < Decimal("0"):
            err(f"--{field_name.replace('_', '-')} cannot be negative")
        validated[field_name] = str(round_currency(val))

    # Check for existing row (for audit old_values)
    fc_t = Table("fica_config")
    fc_q = Q.from_(fc_t).select(fc_t.star).where(fc_t.tax_year == P())
    existing = conn.execute(fc_q.get_sql(), (tax_year,)).fetchone()
    old_values = row_to_dict(existing) if existing else None

    # raw SQL — INSERT ON CONFLICT (UPSERT) not supported by PyPika
    config_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO fica_config (
            id, tax_year, ss_wage_base, ss_employee_rate, ss_employer_rate,
            medicare_employee_rate, medicare_employer_rate,
            additional_medicare_threshold, additional_medicare_rate,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(tax_year) DO UPDATE SET
            ss_wage_base = excluded.ss_wage_base,
            ss_employee_rate = excluded.ss_employee_rate,
            ss_employer_rate = excluded.ss_employer_rate,
            medicare_employee_rate = excluded.medicare_employee_rate,
            medicare_employer_rate = excluded.medicare_employer_rate,
            additional_medicare_threshold = excluded.additional_medicare_threshold,
            additional_medicare_rate = excluded.additional_medicare_rate
        """,
        (
            config_id, tax_year,
            validated["ss_wage_base"],
            validated["ss_employee_rate"],
            validated["ss_employer_rate"],
            validated["medicare_employee_rate"],
            validated["medicare_employer_rate"],
            validated["additional_medicare_threshold"],
            validated["additional_medicare_rate"],
            now,
        ),
    )
    conn.commit()

    audit(conn, "erpclaw-payroll", "update-fica-config", "fica_config", str(tax_year),
           old_values=old_values,
           new_values=validated,
           description=f"FICA config for tax year {tax_year}")
    conn.commit()

    ok({
        "tax_year": tax_year,
        "ss_wage_base": validated["ss_wage_base"],
        "ss_employee_rate": validated["ss_employee_rate"],
        "ss_employer_rate": validated["ss_employer_rate"],
        "medicare_employee_rate": validated["medicare_employee_rate"],
        "medicare_employer_rate": validated["medicare_employer_rate"],
        "additional_medicare_threshold": validated["additional_medicare_threshold"],
        "additional_medicare_rate": validated["additional_medicare_rate"],
        "action": "updated" if existing else "created",
    })


# ---------------------------------------------------------------------------
# 16. update-futa-suta-config
# ---------------------------------------------------------------------------

def update_futa_suta_config(conn, args):
    """Update FUTA or SUTA (unemployment tax) configuration.

    Required: --tax-year, --wage-base, --rate
    Optional: --state-code (NULL = federal FUTA), --employer-rate-override

    Uses UPSERT on (tax_year, state_code).
    - state_code = NULL: configures federal FUTA
    - state_code = "CA", "NY", etc.: configures SUTA for that state

    Rate is a percentage (e.g., "6.0" = 6.0%).
    employer_rate_override allows per-company rate adjustments for
    experience-rated SUTA programs.
    """
    if args.tax_year is None:
        err("--tax-year is required")
    if not args.wage_base:
        err("--wage-base is required")
    if args.rate is None:
        err("--rate is required")

    # Validate tax year
    try:
        tax_year = int(args.tax_year)
    except (ValueError, TypeError):
        err(f"Invalid tax year: {args.tax_year}")
    if tax_year < 2000 or tax_year > 2100:
        err(f"Tax year {tax_year} out of reasonable range [2000, 2100]")

    # Validate wage base
    try:
        wage_base = to_decimal(args.wage_base)
    except (ValueError, TypeError):
        err(f"Invalid wage base: {args.wage_base}")
    if wage_base < Decimal("0"):
        err("Wage base cannot be negative")

    # Validate rate
    try:
        rate = to_decimal(args.rate)
    except (ValueError, TypeError):
        err(f"Invalid rate: {args.rate}")
    if rate < Decimal("0") or rate > Decimal("100"):
        err(f"Rate {rate}% out of range [0, 100]")

    # Validate employer rate override if provided
    employer_rate_override = None
    if args.employer_rate_override:
        try:
            employer_rate_override = to_decimal(args.employer_rate_override)
        except (ValueError, TypeError):
            err(f"Invalid employer rate override: {args.employer_rate_override}")
        if employer_rate_override < Decimal("0") or employer_rate_override > Decimal("100"):
            err(f"Employer rate override {employer_rate_override}% out of range [0, 100]")

    state_code = args.state_code
    config_type = f"SUTA ({state_code})" if state_code else "FUTA (federal)"

    # raw SQL — IS NULL comparison in WHERE clause
    existing = conn.execute(
        """SELECT * FROM futa_suta_config
           WHERE tax_year = ? AND (state_code = ? OR (state_code IS NULL AND ? IS NULL))""",
        (tax_year, state_code, state_code),
    ).fetchone()
    old_values = row_to_dict(existing) if existing else None

    # raw SQL — INSERT ON CONFLICT (UPSERT) not supported by PyPika
    config_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO futa_suta_config (
            id, tax_year, state_code, wage_base, rate,
            employer_rate_override, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(tax_year, state_code) DO UPDATE SET
            wage_base = excluded.wage_base,
            rate = excluded.rate,
            employer_rate_override = excluded.employer_rate_override
        """,
        (
            config_id, tax_year, state_code,
            str(round_currency(wage_base)),
            str(round_currency(rate)),
            str(round_currency(employer_rate_override)) if employer_rate_override is not None else None,
            now,
        ),
    )
    conn.commit()

    audit(conn, "erpclaw-payroll", "update-futa-suta-config", "futa_suta_config",
           f"{tax_year}-{state_code or 'federal'}",
           old_values=old_values,
           new_values={
               "tax_year": tax_year,
               "state_code": state_code,
               "wage_base": str(round_currency(wage_base)),
               "rate": str(round_currency(rate)),
           },
           description=f"{config_type} for tax year {tax_year}")
    conn.commit()

    ok({
        "tax_year": tax_year,
        "state_code": state_code,
        "config_type": config_type,
        "wage_base": str(round_currency(wage_base)),
        "rate": str(round_currency(rate)),
        "employer_rate_override": str(round_currency(employer_rate_override)) if employer_rate_override is not None else None,
        "action": "updated" if existing else "created",
    })


# ---------------------------------------------------------------------------
# 18. Wage Garnishment CRUD
# ---------------------------------------------------------------------------

VALID_GARNISHMENT_TYPES = ("child_support", "tax_levy", "student_loan", "creditor")
# Federal priority: child_support=1, tax_levy=2, student_loan=3, creditor=4
GARNISHMENT_TYPE_PRIORITY = {
    "child_support": 1, "tax_levy": 2, "student_loan": 3, "creditor": 4,
}


def add_garnishment(conn, args):
    """Add a wage garnishment order for an employee."""
    employee_id = args.employee_id
    if not employee_id:
        err("--employee-id is required")
    _validate_employee_exists(conn, employee_id)
    company_id = _get_employee_company_id(conn, employee_id)

    order_number = args.order_number
    if not order_number:
        err("--order-number is required")
    creditor_name = args.creditor_name
    if not creditor_name:
        err("--creditor-name is required")
    garnishment_type = args.garnishment_type
    if not garnishment_type or garnishment_type not in VALID_GARNISHMENT_TYPES:
        err(f"--garnishment-type required, one of: {VALID_GARNISHMENT_TYPES}")

    amount_or_pct = args.amount_or_percentage or "0"
    is_pct = 1 if args.is_percentage else 0
    total_owed = args.total_owed
    start_date = args.start_date
    if not start_date:
        err("--start-date is required")
    end_date = args.end_date

    priority = GARNISHMENT_TYPE_PRIORITY[garnishment_type]
    max_pct = "50" if garnishment_type == "child_support" else "25"

    g_id = str(uuid.uuid4())
    ins_garn_sql, _ = insert_row("wage_garnishment", {
        "id": P(), "employee_id": P(), "order_number": P(),
        "creditor_name": P(), "garnishment_type": P(),
        "amount_or_percentage": P(), "is_percentage": P(),
        "max_percentage": P(), "priority": P(), "status": P(),
        "cumulative_paid": P(), "total_owed": P(),
        "start_date": P(), "end_date": P(), "company_id": P(),
    })
    conn.execute(ins_garn_sql, (
        g_id, employee_id, order_number, creditor_name, garnishment_type,
        amount_or_pct, is_pct, max_pct, priority, "active", "0",
        total_owed, start_date, end_date, company_id,
    ))
    audit(conn, "erpclaw-payroll", "add-garnishment", "wage_garnishment", g_id,
           new_values={"employee_id": employee_id, "type": garnishment_type,
                       "amount": amount_or_pct})
    conn.commit()
    ok({"garnishment_id": g_id, "priority": priority})


def update_garnishment(conn, args):
    """Update a wage garnishment (status, amount, dates)."""
    g_id = args.garnishment_id
    if not g_id:
        err("--garnishment-id is required")

    wg_t = Table("wage_garnishment")
    q = Q.from_(wg_t).select(wg_t.star).where(wg_t.id == P())
    row = conn.execute(q.get_sql(), (g_id,)).fetchone()
    if not row:
        err(f"Garnishment {g_id} not found")

    data = {}
    if args.status:
        if args.status not in ("active", "paused", "completed", "cancelled"):
            err("Invalid status")
        data["status"] = args.status
    if args.amount_or_percentage:
        data["amount_or_percentage"] = args.amount_or_percentage
    if args.total_owed:
        data["total_owed"] = args.total_owed
    if args.end_date:
        data["end_date"] = args.end_date

    if not data:
        err("No fields to update")

    data["updated_at"] = LiteralValue("datetime('now')")
    sql, params = dynamic_update("wage_garnishment", data, where={"id": g_id})
    conn.execute(sql, params)
    audit(conn, "erpclaw-payroll", "update-garnishment", "wage_garnishment", g_id)
    conn.commit()
    ok({"updated": True})


def list_garnishments(conn, args):
    """List garnishments for an employee or company."""
    employee_id = args.employee_id
    company_id = args.company_id

    wg_t = Table("wage_garnishment")
    q = Q.from_(wg_t).select(wg_t.star)
    params = []

    if employee_id:
        q = q.where(wg_t.employee_id == P())
        params.append(employee_id)
    if company_id:
        q = q.where(wg_t.company_id == P())
        params.append(company_id)
    if args.status:
        q = q.where(wg_t.status == P())
        params.append(args.status)

    q = q.orderby(wg_t.priority).orderby(wg_t.created_at)
    rows = conn.execute(q.get_sql(), params).fetchall()

    ok({"garnishments": [dict(r) for r in rows], "count": len(rows)})


def get_garnishment(conn, args):
    """Get a single garnishment by ID."""
    g_id = args.garnishment_id
    if not g_id:
        err("--garnishment-id is required")
    wg_t = Table("wage_garnishment")
    q = Q.from_(wg_t).select(wg_t.star).where(wg_t.id == P())
    row = conn.execute(q.get_sql(), (g_id,)).fetchone()
    if not row:
        err(f"Garnishment {g_id} not found")
    ok(dict(row))


# ---------------------------------------------------------------------------
# 19. status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """Return payroll summary metrics and counts.

    Optional: --company-id (filter by company)

    Returns counts of salary components, structures, active assignments,
    payroll runs by status, total salary slips, FICA config years,
    and income tax slabs.
    """
    # raw SQL — many queries use IS NULL in dynamic company_filter and 1=1 pattern
    company_filter = ""
    params = []
    if args.company_id:
        company_filter = "AND company_id = ?"
        params = [args.company_id]

    # Salary components (no company filter -- they are global)
    sc_t = Table("salary_component")
    total_components = conn.execute(
        Q.from_(sc_t).select(fn.Count("*")).get_sql(),
    ).fetchone()[0]

    components_by_type = {}
    sc_ct_q = Q.from_(sc_t).select(fn.Count("*")).where(sc_t.component_type == P())
    for ct in VALID_COMPONENT_TYPES:
        cnt = conn.execute(sc_ct_q.get_sql(), (ct,)).fetchone()[0]
        if cnt > 0:
            components_by_type[ct] = cnt

    # Salary structures
    total_structures = conn.execute(
        f"SELECT COUNT(*) FROM salary_structure WHERE 1=1 {company_filter}",
        params,
    ).fetchone()[0]

    active_structures = conn.execute(
        f"SELECT COUNT(*) FROM salary_structure WHERE is_active = 1 {company_filter}",
        params,
    ).fetchone()[0]

    # Active salary assignments (effective_to is null or in the future)
    today = date.today().isoformat()
    active_assignments = conn.execute(
        f"""SELECT COUNT(*) FROM salary_assignment
            WHERE (effective_to IS NULL OR effective_to >= ?)
              AND effective_from <= ?
              {company_filter}""",
        [today, today] + params,
    ).fetchone()[0]

    total_assignments = conn.execute(
        f"SELECT COUNT(*) FROM salary_assignment WHERE 1=1 {company_filter}",
        params,
    ).fetchone()[0]

    # Payroll runs by status
    payroll_runs = {}
    for pr_status in VALID_PAYROLL_STATUSES:
        cnt = conn.execute(
            f"SELECT COUNT(*) FROM payroll_run WHERE status = ? {company_filter}",
            [pr_status] + params,
        ).fetchone()[0]
        if cnt > 0:
            payroll_runs[pr_status] = cnt

    total_payroll_runs = sum(payroll_runs.values())

    # Total salary slips
    total_slips = conn.execute(
        f"SELECT COUNT(*) FROM salary_slip WHERE 1=1 {company_filter}",
        params,
    ).fetchone()[0]

    # FICA configs
    fc_t = Table("fica_config")
    fica_configs = conn.execute(
        Q.from_(fc_t).select(fn.Count("*")).get_sql(),
    ).fetchone()[0]

    fica_years = conn.execute(
        Q.from_(fc_t).select(fc_t.tax_year).orderby(fc_t.tax_year, order=Order.desc).get_sql(),
    ).fetchall()
    fica_year_list = [r["tax_year"] for r in fica_years]

    # Income tax slabs
    its_t = Table("income_tax_slab")
    total_tax_slabs = conn.execute(
        Q.from_(its_t).select(fn.Count("*")).where(its_t.is_active == 1).get_sql(),
    ).fetchone()[0]

    tax_slabs_by_jurisdiction = {}
    its_jq = Q.from_(its_t).select(fn.Count("*")).where(its_t.tax_jurisdiction == P()).where(its_t.is_active == 1)
    for jurisdiction in VALID_TAX_JURISDICTIONS:
        cnt = conn.execute(its_jq.get_sql(), (jurisdiction,)).fetchone()[0]
        if cnt > 0:
            tax_slabs_by_jurisdiction[jurisdiction] = cnt

    # FUTA/SUTA configs
    fs_t = Table("futa_suta_config")
    futa_suta_configs = conn.execute(
        Q.from_(fs_t).select(fn.Count("*")).get_sql(),
    ).fetchone()[0]

    # Most recent payroll run
    latest_run_sql = f"""
        SELECT id, naming_series, period_start, period_end, status,
               total_gross, total_net, employee_count
        FROM payroll_run
        WHERE 1=1 {company_filter}
        ORDER BY period_end DESC
        LIMIT 1
    """
    latest_run = conn.execute(latest_run_sql, params).fetchone()
    latest_run_dict = row_to_dict(latest_run) if latest_run else None

    ok({
        "total_salary_components": total_components,
        "components_by_type": components_by_type,
        "total_salary_structures": total_structures,
        "active_salary_structures": active_structures,
        "total_salary_assignments": total_assignments,
        "active_salary_assignments": active_assignments,
        "total_payroll_runs": total_payroll_runs,
        "payroll_runs_by_status": payroll_runs,
        "total_salary_slips": total_slips,
        "fica_configs": fica_configs,
        "fica_years": fica_year_list,
        "total_income_tax_slabs": total_tax_slabs,
        "tax_slabs_by_jurisdiction": tax_slabs_by_jurisdiction,
        "futa_suta_configs": futa_suta_configs,
        "latest_payroll_run": latest_run_dict,
    })




# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_periods_per_year(frequency: str) -> int:
    """Return the number of pay periods per year for a given frequency.

    Args:
        frequency: One of 'monthly', 'biweekly', 'weekly'.

    Returns:
        12 for monthly, 26 for biweekly, 52 for weekly.

    Raises:
        ValueError: If frequency is not recognized.
    """
    mapping = {
        "monthly": 12,
        "biweekly": 26,
        "weekly": 52,
    }
    if frequency not in mapping:
        raise ValueError(
            f"Unknown payroll frequency '{frequency}'. "
            f"Valid values: {sorted(mapping.keys())}"
        )
    return mapping[frequency]


def _calculate_progressive_tax(taxable_income: Decimal,
                                rates: list[dict]) -> Decimal:
    """Apply progressive (graduated) tax brackets to a taxable income amount.

    Each rate dict must have:
        from_amount (TEXT/Decimal): Lower bound of the bracket (inclusive).
        to_amount (TEXT/Decimal or None): Upper bound (exclusive). None = unlimited.
        rate (TEXT/Decimal): Tax rate as a percentage (e.g., "10" for 10%).

    The brackets are assumed to be sorted by from_amount ascending.

    Args:
        taxable_income: The annual taxable income (Decimal).
        rates: List of bracket dicts with from_amount, to_amount, rate.

    Returns:
        The total tax as a Decimal (not yet rounded to currency precision).
    """
    if taxable_income <= 0:
        return Decimal("0")

    total_tax = Decimal("0")
    remaining = taxable_income

    # Sort by from_amount ascending to ensure correct bracket ordering
    sorted_rates = sorted(rates, key=lambda r: to_decimal(r["from_amount"]))

    for bracket in sorted_rates:
        from_amt = to_decimal(bracket["from_amount"])
        to_amt_raw = bracket.get("to_amount")
        rate_pct = to_decimal(bracket["rate"])

        # If taxable income is below the bracket floor, we are done
        if taxable_income <= from_amt:
            break

        # Determine the bracket ceiling
        if to_amt_raw is not None and str(to_amt_raw).strip() != "":
            to_amt = to_decimal(to_amt_raw)
        else:
            # Open-ended top bracket
            to_amt = taxable_income

        # Calculate the taxable portion within this bracket
        bracket_income = min(taxable_income, to_amt) - from_amt
        if bracket_income <= 0:
            continue

        bracket_tax = bracket_income * rate_pct / Decimal("100")
        total_tax += bracket_tax

    return total_tax


def _get_ytd_values(conn: sqlite3.Connection, employee_id: str,
                    period_end: str, company_id: str) -> dict:
    """Get year-to-date payroll values from previously submitted salary slips.

    Queries all submitted salary slips for the same employee and company
    within the same calendar year (based on period_end), but only those
    whose period_end is strictly BEFORE the given period_end.

    Args:
        conn: SQLite connection.
        employee_id: The employee to query.
        period_end: The period end date of the CURRENT slip being calculated
                    (format: YYYY-MM-DD). Slips with period_end < this are included.
        company_id: Company ID for scoping.

    Returns:
        dict with keys:
            ytd_gross (Decimal): Total gross pay YTD.
            ytd_ss_wages (Decimal): Total social-security-taxable wages YTD.
            ytd_medicare_wages (Decimal): Total Medicare-taxable wages YTD.
            ytd_federal_tax (Decimal): Total federal tax withheld YTD.
            ytd_pretax_401k (Decimal): Total 401k contributions YTD.
            ytd_pretax_hsa (Decimal): Total HSA contributions YTD.
    """
    # Extract the year from period_end
    year_str = period_end[:4]
    year_start = f"{year_str}-01-01"

    # Sum gross from previous submitted slips in same year
    ss_t = Table("salary_slip").as_("ss")
    ytd_q = (Q.from_(ss_t)
             .select(
                 fn.Coalesce(DecimalSum(ss_t.gross_pay), ValueWrapper("0")).as_("ytd_gross"),
                 fn.Coalesce(DecimalSum(ss_t.total_deductions), ValueWrapper("0")).as_("ytd_deductions"),
                 fn.Coalesce(DecimalSum(ss_t.net_pay), ValueWrapper("0")).as_("ytd_net"),
             )
             .where(ss_t.employee_id == P())
             .where(ss_t.company_id == P())
             .where(ss_t.status == ValueWrapper("submitted"))
             .where(ss_t.period_end >= P())
             .where(ss_t.period_end < P()))
    row = conn.execute(ytd_q.get_sql(), (employee_id, company_id, year_start, period_end)).fetchone()

    ytd_gross = to_decimal(str(row["ytd_gross"])) if row else Decimal("0")

    # Helper: build a YTD deduction query for a specific component name
    ssd_t = Table("salary_slip_detail").as_("ssd")
    ss_t2 = Table("salary_slip").as_("ss")
    sc_t = Table("salary_component").as_("sc")

    def _ytd_deduction_query():
        return (Q.from_(ssd_t)
                .join(ss_t2).on(ss_t2.id == ssd_t.salary_slip_id)
                .join(sc_t).on(sc_t.id == ssd_t.salary_component_id)
                .select(fn.Coalesce(DecimalSum(ssd_t.amount), ValueWrapper("0")).as_("total"))
                .where(ss_t2.employee_id == P())
                .where(ss_t2.company_id == P())
                .where(ss_t2.status == ValueWrapper("submitted"))
                .where(ss_t2.period_end >= P())
                .where(ss_t2.period_end < P())
                .where(ssd_t.component_type == ValueWrapper("deduction")))

    ytd_params = (employee_id, company_id, year_start, period_end)

    # Get YTD federal tax from salary_slip_detail
    fed_q = _ytd_deduction_query().where(sc_t.name == ValueWrapper("Federal Income Tax"))
    fed_row = conn.execute(fed_q.get_sql(), ytd_params).fetchone()
    ytd_federal_tax = to_decimal(str(fed_row["total"])) if fed_row else Decimal("0")

    # Get YTD Social Security wages (employee SS deduction details)
    ss_q = _ytd_deduction_query().where(sc_t.name == ValueWrapper("Social Security Tax"))
    ss_row = conn.execute(ss_q.get_sql(), ytd_params).fetchone()

    # Get YTD 401k
    k401_q = _ytd_deduction_query().where(sc_t.name == ValueWrapper("401k Contribution"))
    k401_row = conn.execute(k401_q.get_sql(), ytd_params).fetchone()
    ytd_pretax_401k = to_decimal(str(k401_row["total"])) if k401_row else Decimal("0")

    # Get YTD HSA
    hsa_q = _ytd_deduction_query().where(sc_t.name == ValueWrapper("HSA Contribution"))
    hsa_row = conn.execute(hsa_q.get_sql(), ytd_params).fetchone()
    ytd_pretax_hsa = to_decimal(str(hsa_row["total"])) if hsa_row else Decimal("0")

    return {
        "ytd_gross": ytd_gross,
        "ytd_ss_wages": ytd_gross,  # SS wages = gross (capped at wage base is done at calc time)
        "ytd_medicare_wages": ytd_gross,
        "ytd_federal_tax": ytd_federal_tax,
        "ytd_pretax_401k": ytd_pretax_401k,
        "ytd_pretax_hsa": ytd_pretax_hsa,
    }


def _get_ytd_supplemental(conn: sqlite3.Connection, employee_id: str,
                          period_end: str, company_id: str) -> Decimal:
    """Get YTD supplemental wage earnings for >$1M threshold check.

    Queries salary_slip_detail for earning components where
    the salary_component has is_supplemental = 1.
    """
    year_str = period_end[:4]
    year_start = f"{year_str}-01-01"

    rows = conn.execute(
        """SELECT ssd.amount
           FROM salary_slip_detail ssd
           JOIN salary_slip ss ON ss.id = ssd.salary_slip_id
           JOIN salary_component sc ON sc.id = ssd.salary_component_id
           WHERE ss.employee_id = ?
             AND ss.company_id = ?
             AND ss.status = 'submitted'
             AND ss.period_end >= ?
             AND ss.period_end < ?
             AND ssd.component_type = 'earning'
             AND sc.is_supplemental = 1""",
        (employee_id, company_id, year_start, period_end),
    ).fetchall()

    return sum((to_decimal(r["amount"]) for r in rows), Decimal("0"))


def _find_payroll_accounts(conn: sqlite3.Connection,
                           company_id: str) -> dict:
    """Look up the GL accounts needed for payroll posting.

    Searches by account name patterns and root_type/account_type.
    Returns a dict mapping logical account names to account IDs.

    Required accounts:
        salary_expense:      DR for gross pay (expense)
        payroll_payable:     CR for net pay (liability, payable)
        federal_tax_payable: CR for federal income tax withheld (liability)
        state_tax_payable:   CR for state income tax withheld (liability) -- optional
        ss_payable:          CR for Social Security (liability)
        medicare_payable:    CR for Medicare (liability)
        employer_tax_expense:DR for employer-side taxes (expense)
        futa_payable:        CR for FUTA (liability) -- optional
        suta_payable:        CR for SUTA (liability) -- optional

    Args:
        conn: SQLite connection.
        company_id: The company whose chart of accounts to search.

    Returns:
        dict with account name keys and account ID values.
        Missing accounts will have None values.

    Raises:
        ValueError: If critical accounts (salary_expense, payroll_payable)
                    cannot be found.
    """
    accounts = {
        "salary_expense": None,
        "payroll_payable": None,
        "federal_tax_payable": None,
        "state_tax_payable": None,
        "ss_payable": None,
        "medicare_payable": None,
        "employer_tax_expense": None,
        "futa_payable": None,
        "suta_payable": None,
    }

    # raw SQL — complex LIKE patterns with OR conditions and LOWER() not easily expressed in PyPika
    acct_t = Table("account")

    def _acct_query(root_type, like_patterns, extra_where=None):
        """Helper to build account lookup with LIKE OR patterns."""
        like_clauses = " OR ".join("LOWER(name) LIKE ?" for _ in like_patterns)
        extra = f"AND {extra_where}" if extra_where else ""
        params = [company_id, root_type] + list(like_patterns)
        return conn.execute(
            f"""SELECT id FROM account
               WHERE company_id = ? AND root_type = ?
                 AND is_group = 0 AND disabled = 0
                 AND ({like_clauses})
                 {extra}
               LIMIT 1""",
            params,
        ).fetchone()

    # --- Salary Expense ---
    row = _acct_query("expense", ["%salary%expense%", "%salary expense%"])
    if row:
        accounts["salary_expense"] = row["id"]
    else:
        # Fallback: any expense account
        q = (Q.from_(acct_t).select(acct_t.id)
             .where(acct_t.company_id == P())
             .where(acct_t.root_type == ValueWrapper("expense"))
             .where(acct_t.is_group == 0)
             .where(acct_t.disabled == 0)
             .orderby(acct_t.name).limit(1))
        row = conn.execute(q.get_sql(), (company_id,)).fetchone()
        if row:
            accounts["salary_expense"] = row["id"]

    # --- Payroll Payable ---
    row = _acct_query("liability", ["%payroll%payable%", "%payroll payable%"])
    if row:
        accounts["payroll_payable"] = row["id"]
    else:
        # Fallback: any payable liability
        q = (Q.from_(acct_t).select(acct_t.id)
             .where(acct_t.company_id == P())
             .where(acct_t.root_type == ValueWrapper("liability"))
             .where(acct_t.account_type == ValueWrapper("payable"))
             .where(acct_t.is_group == 0)
             .where(acct_t.disabled == 0)
             .orderby(acct_t.name).limit(1))
        row = conn.execute(q.get_sql(), (company_id,)).fetchone()
        if row:
            accounts["payroll_payable"] = row["id"]

    # --- Federal Income Tax Payable ---
    row = _acct_query("liability", ["%federal%", "%income tax%withheld%"])
    if row:
        accounts["federal_tax_payable"] = row["id"]

    # --- State Income Tax Payable ---
    row = _acct_query("liability", ["%state%income%tax%", "%state%tax%payable%", "%state%withheld%"])
    if row:
        accounts["state_tax_payable"] = row["id"]

    # --- Social Security Payable ---
    row = _acct_query("liability", ["%social%security%", "%ss%payable%", "%social security%"])
    if row:
        accounts["ss_payable"] = row["id"]

    # --- Medicare Payable ---
    row = _acct_query("liability", ["%medicare%"])
    if row:
        accounts["medicare_payable"] = row["id"]

    # --- Employer Tax Expense ---
    row = _acct_query("expense", ["%employer%tax%", "%payroll tax%expense%"])
    if row:
        accounts["employer_tax_expense"] = row["id"]
    else:
        # Fallback to salary expense
        accounts["employer_tax_expense"] = accounts["salary_expense"]

    # --- FUTA Payable ---
    row = _acct_query("liability", ["%futa%"])
    if row:
        accounts["futa_payable"] = row["id"]

    # --- SUTA Payable ---
    row = _acct_query("liability", ["%suta%"])
    if row:
        accounts["suta_payable"] = row["id"]

    # Validate critical accounts exist
    if not accounts["salary_expense"]:
        raise ValueError(
            "Cannot find a salary expense account for payroll posting. "
            "Please create an expense account with 'Salary Expense' in the name."
        )
    if not accounts["payroll_payable"]:
        raise ValueError(
            "Cannot find a payroll payable account for payroll posting. "
            "Please create a liability account with 'Payroll Payable' in the name."
        )

    return accounts


def _get_or_create_statutory_component(conn: sqlite3.Connection,
                                        name: str,
                                        component_type: str = "deduction",
                                        is_statutory: int = 1,
                                        is_pre_tax: int = 0,
                                        gl_account_id: str = None) -> str:
    """Find an existing salary component by name, or create one.

    Used for statutory deduction components (Federal Income Tax,
    Social Security Tax, Medicare Tax, 401k Contribution, HSA Contribution)
    which are auto-created if they do not already exist.

    Args:
        conn: SQLite connection.
        name: The component name (e.g., "Federal Income Tax").
        component_type: 'earning', 'deduction', or 'employer_contribution'.
        is_statutory: Whether this is a statutory deduction.
        is_pre_tax: Whether this is a pre-tax deduction.
        gl_account_id: Optional GL account for the component.

    Returns:
        The salary_component.id (existing or newly created).
    """
    sc_t = Table("salary_component")
    q = Q.from_(sc_t).select(sc_t.id).where(sc_t.name == P())
    row = conn.execute(q.get_sql(), (name,)).fetchone()
    if row:
        return row["id"]

    # Create the component
    comp_id = str(uuid.uuid4())
    ins_sql, _ = insert_row("salary_component", {
        "id": P(), "name": P(), "component_type": P(),
        "is_statutory": P(), "is_pre_tax": P(),
        "is_tax_applicable": P(), "depends_on_payment_days": P(),
        "gl_account_id": P(),
    })
    conn.execute(ins_sql, (comp_id, name, component_type, is_statutory,
                           is_pre_tax, 0, 0, gl_account_id))
    return comp_id


def _calculate_working_and_payment_days(conn: sqlite3.Connection,
                                         employee_id: str,
                                         period_start: str,
                                         period_end: str) -> tuple:
    """Calculate total working days and payment days for an employee in a period.

    Total working days = calendar days from period_start to period_end inclusive,
    minus weekends (Saturday and Sunday).

    Payment days = total_working_days minus unpaid leave days in the period.
    (Paid leave does NOT reduce payment days.)

    Also checks the employee's holiday list; holidays on working days do not
    reduce payment days (employees are still paid for holidays).

    Args:
        conn: SQLite connection.
        employee_id: The employee to check.
        period_start: Period start date (YYYY-MM-DD).
        period_end: Period end date (YYYY-MM-DD).

    Returns:
        (total_working_days: Decimal, payment_days: Decimal)
    """
    start = date.fromisoformat(period_start)
    end = date.fromisoformat(period_end)

    # Count weekdays (Mon-Fri) between start and end inclusive
    total_working_days = Decimal("0")
    current = start
    while current <= end:
        if current.weekday() < 5:  # 0=Mon, 4=Fri
            total_working_days += Decimal("1")
        current += timedelta(days=1)

    # Get unpaid leave days in the period
    # An approved leave application overlapping the period, where the leave type
    # is unpaid (is_paid_leave = 0), reduces payment days.
    unpaid_leave_days = Decimal("0")

    leave_rows = conn.execute(
        """
        SELECT la.from_date, la.to_date, la.total_days, la.half_day,
               la.half_day_date, lt.is_paid_leave
        FROM leave_application la
        JOIN leave_type lt ON lt.id = la.leave_type_id
        WHERE la.employee_id = ?
          AND la.status = 'approved'
          AND la.from_date <= ?
          AND la.to_date >= ?
          AND lt.is_paid_leave = 0
        """,
        (employee_id, period_end, period_start),
    ).fetchall()

    for leave in leave_rows:
        leave_start = date.fromisoformat(leave["from_date"])
        leave_end = date.fromisoformat(leave["to_date"])

        # Clamp to the payroll period
        effective_start = max(leave_start, start)
        effective_end = min(leave_end, end)

        # Count weekdays in the clamped range
        current = effective_start
        while current <= effective_end:
            if current.weekday() < 5:
                # Check if this is a half-day leave
                if leave["half_day"] and leave["half_day_date"]:
                    half_day_dt = date.fromisoformat(leave["half_day_date"])
                    if current == half_day_dt:
                        unpaid_leave_days += Decimal("0.5")
                    else:
                        unpaid_leave_days += Decimal("1")
                else:
                    unpaid_leave_days += Decimal("1")
            current += timedelta(days=1)

    payment_days = total_working_days - unpaid_leave_days
    if payment_days < Decimal("0"):
        payment_days = Decimal("0")

    return (total_working_days, payment_days)


# ============================================================================
# ACTION 8: create_payroll_run
# ============================================================================

def create_payroll_run(conn: sqlite3.Connection, args) -> None:
    """Create a draft payroll run for a pay period.

    Required args:
        --company-id: Company ID.
        --period-start: Start of the pay period (YYYY-MM-DD).
        --period-end: End of the pay period (YYYY-MM-DD).

    Optional args:
        --department-id: Filter employees by department.
        --payroll-frequency: 'monthly' (default), 'biweekly', or 'weekly'.

    Validates:
        - Company exists.
        - No overlapping payroll run for the same company and period.

    Creates a payroll_run record with status='draft'.
    """
    company_id = args.company_id
    period_start = args.period_start
    period_end = args.period_end
    department_id = getattr(args, "department_id", None)
    frequency = getattr(args, "payroll_frequency", None) or "monthly"

    # --- Validation ---
    if not company_id:
        err("--company-id is required")
    if not period_start:
        err("--period-start is required")
    if not period_end:
        err("--period-end is required")

    # Validate period_start < period_end
    if period_start >= period_end:
        err(f"--period-start ({period_start}) must be before --period-end ({period_end})")

    # Validate frequency
    valid_frequencies = ("monthly", "biweekly", "weekly")
    if frequency not in valid_frequencies:
        err(f"--payroll-frequency must be one of: {', '.join(valid_frequencies)}")

    # Company must exist
    _validate_company_exists(conn, company_id)

    # Department must exist if specified
    if department_id:
        dept_t = Table("department")
        dept_q = Q.from_(dept_t).select(dept_t.id).where(
            Criterion.any([dept_t.id == P(), dept_t.name == P()])
        )
        dept = conn.execute(dept_q.get_sql(), (department_id, department_id)).fetchone()
        if not dept:
            err(f"Department {department_id} not found")
        department_id = dept["id"]

    # Check for overlapping payroll run (same company, overlapping period, not cancelled)
    pr_t = Table("payroll_run")
    overlap_q = (Q.from_(pr_t)
                 .select(pr_t.id, pr_t.naming_series, pr_t.period_start, pr_t.period_end)
                 .where(pr_t.company_id == P())
                 .where(pr_t.status != ValueWrapper("cancelled"))
                 .where(pr_t.period_start <= P())
                 .where(pr_t.period_end >= P()))
    overlap = conn.execute(overlap_q.get_sql(), (company_id, period_end, period_start)).fetchone()
    if overlap:
        err(
            f"Overlapping payroll run exists: {overlap['naming_series'] or overlap['id']} "
            f"({overlap['period_start']} to {overlap['period_end']})"
        )

    # --- Create the payroll run ---
    run_id = str(uuid.uuid4())
    naming = get_next_name(conn, "payroll_run", company_id=company_id)

    ins_pr_sql, _ = insert_row("payroll_run", {
        "id": P(), "naming_series": P(), "period_start": P(),
        "period_end": P(), "payroll_frequency": P(), "department_id": P(),
        "total_gross": P(), "total_deductions": P(), "total_net": P(),
        "employee_count": P(), "status": P(), "company_id": P(),
    })
    conn.execute(ins_pr_sql, (run_id, naming, period_start, period_end, frequency,
                              department_id, "0", "0", "0", 0, "draft", company_id))

    audit(conn, "erpclaw-payroll", "create-payroll-run", "payroll_run", run_id,
           new_values={"period_start": period_start, "period_end": period_end,
                       "frequency": frequency},
           description=f"Created payroll run {naming}")

    conn.commit()
    ok({
        "payroll_run_id": run_id,
        "naming_series": naming,
        "period_start": period_start,
        "period_end": period_end,
        "payroll_frequency": frequency,
    })


# ============================================================================
# ACTION 9: generate_salary_slips  -- THE MAIN CALCULATION ENGINE
# ============================================================================

def generate_salary_slips(conn: sqlite3.Connection, args) -> None:
    """Calculate and generate salary slips for all eligible employees.

    Required args:
        --payroll-run-id: The draft payroll run to generate slips for.

    Process:
        1. Validate payroll run exists and is in 'draft' status.
        2. Delete any existing draft slips for this run (allows regeneration).
        3. For each eligible employee:
           a. Find active salary assignment effective during the period.
           b. Calculate working days and payment days.
           c. Calculate earnings (fixed or percentage-based, with proration).
           d. Calculate pre-tax deductions (401k, HSA).
           e. Calculate taxable income and federal income tax.
           f. Calculate FICA (Social Security + Medicare + Additional Medicare).
           g. Create salary_slip and salary_slip_detail rows.
        4. Update payroll_run totals.

    Returns:
        {"status":"ok", "slips_generated": N, "total_gross": "...",
         "total_net": "...", "total_deductions": "..."}
    """
    payroll_run_id = args.payroll_run_id

    if not payroll_run_id:
        err("--payroll-run-id is required")

    # --- Validate payroll run ---
    pr_t = Table("payroll_run")
    run_q = Q.from_(pr_t).select(pr_t.star).where(pr_t.id == P())
    run = conn.execute(run_q.get_sql(), (payroll_run_id,)).fetchone()
    if not run:
        err(f"Payroll run {payroll_run_id} not found")

    run = row_to_dict(run)
    if run["status"] != "draft":
        err(f"Payroll run is '{run['status']}', must be 'draft' to generate slips")

    company_id = run["company_id"]
    period_start = run["period_start"]
    period_end = run["period_end"]
    frequency = run["payroll_frequency"]
    department_id = run.get("department_id")
    periods_per_year = _get_periods_per_year(frequency)

    # --- Delete existing draft slips for this run (allows regeneration) ---
    ss_t = Table("salary_slip")
    del_q = Q.from_(ss_t).select(ss_t.id).where(ss_t.payroll_run_id == P()).where(ss_t.status == ValueWrapper("draft"))
    existing_slips = conn.execute(del_q.get_sql(), (payroll_run_id,)).fetchall()

    ssd_t = Table("salary_slip_detail")
    for slip in existing_slips:
        del_det = Q.from_(ssd_t).delete().where(ssd_t.salary_slip_id == P())
        conn.execute(del_det.get_sql(), (slip["id"],))
        del_slip = Q.from_(ss_t).delete().where(ss_t.id == P())
        conn.execute(del_slip.get_sql(), (slip["id"],))

    # --- Get FICA config for the tax year ---
    tax_year = int(period_end[:4])
    fc_t = Table("fica_config")
    fc_q = Q.from_(fc_t).select(fc_t.star).where(fc_t.tax_year == P())
    fica_config = conn.execute(fc_q.get_sql(), (tax_year,)).fetchone()
    fica = row_to_dict(fica_config) if fica_config else None

    # --- Find eligible employees ---
    # raw SQL — uses IS NULL in OR clause for effective_to check
    emp_query = """
        SELECT DISTINCT e.*
        FROM employee e
        JOIN salary_assignment sa ON sa.employee_id = e.id
        WHERE e.company_id = ?
          AND e.status = 'active'
          AND sa.effective_from <= ?
          AND (sa.effective_to IS NULL OR sa.effective_to >= ?)
    """
    emp_params = [company_id, period_end, period_start]

    if department_id:
        emp_query += " AND e.department_id = ?"
        emp_params.append(department_id)

    employees = conn.execute(emp_query, emp_params).fetchall()

    if not employees:
        err("No eligible employees found for this payroll period. "
             "Ensure employees are active and have salary assignments "
             "effective during the period.")

    # --- Generate slips ---
    run_total_gross = Decimal("0")
    run_total_deductions = Decimal("0")
    run_total_net = Decimal("0")
    slips_generated = 0

    for emp_row in employees:
        emp = row_to_dict(emp_row)
        employee_id = emp["id"]

        # Step 0: Get the active salary assignment for this employee/period
        # raw SQL — uses IS NULL in OR clause for effective_to
        assignment = conn.execute(
            """
            SELECT sa.*
            FROM salary_assignment sa
            WHERE sa.employee_id = ?
              AND sa.effective_from <= ?
              AND (sa.effective_to IS NULL OR sa.effective_to >= ?)
            ORDER BY sa.effective_from DESC
            LIMIT 1
            """,
            (employee_id, period_end, period_start),
        ).fetchone()
        if not assignment:
            continue  # Skip employees without assignment (shouldn't happen due to JOIN)

        assignment = row_to_dict(assignment)
        structure_id = assignment["salary_structure_id"]
        base_amount = to_decimal(assignment["base_amount"])

        # Get salary structure
        st_t = Table("salary_structure")
        st_q = Q.from_(st_t).select(st_t.star).where(st_t.id == P())
        structure = conn.execute(st_q.get_sql(), (structure_id,)).fetchone()
        if not structure:
            continue
        structure = row_to_dict(structure)

        # Get structure details (component definitions) with component info
        ssd_det = Table("salary_structure_detail").as_("ssd")
        sc_det = Table("salary_component").as_("sc")
        det_q = (Q.from_(ssd_det)
                 .join(sc_det).on(sc_det.id == ssd_det.salary_component_id)
                 .select(
                     ssd_det.star,
                     sc_det.name.as_("component_name"), sc_det.component_type,
                     sc_det.depends_on_payment_days, sc_det.is_tax_applicable,
                     sc_det.is_pre_tax, sc_det.gl_account_id.as_("component_gl_account_id"),
                     sc_det.is_supplemental,
                 )
                 .where(ssd_det.salary_structure_id == P())
                 .orderby(ssd_det.sort_order)
                 .orderby(sc_det.component_type))
        details = conn.execute(det_q.get_sql(), (structure_id,)).fetchall()
        details = [row_to_dict(d) for d in details]

        # Step 1: Calculate working days and payment days
        total_working_days, payment_days = _calculate_working_and_payment_days(
            conn, employee_id, period_start, period_end
        )

        # Step 2: Calculate earnings
        gross = Decimal("0")
        supplemental_gross = Decimal("0")  # Track supplemental wages for flat tax
        component_amounts = {}  # component_id -> amount
        earnings_details = []   # List of (component_id, component_name, amount)

        for detail in details:
            comp_type = detail["component_type"]
            if comp_type != "earning":
                continue

            comp_id = detail["salary_component_id"]
            amt = Decimal("0")

            # Determine base amount for this component
            # Check percentage FIRST so percent-of-base components (e.g. HRA)
            # are not mistakenly treated as flat amounts when both fields are set.
            if detail.get("percentage") and str(detail["percentage"]).strip():
                pct = to_decimal(detail["percentage"])
                if pct > Decimal("0"):
                    base_comp_id = detail.get("base_component_id")
                    if base_comp_id and base_comp_id in component_amounts:
                        base_amt = component_amounts[base_comp_id]
                    else:
                        base_amt = base_amount
                    amt = base_amt * pct / Decimal("100")
                else:
                    # percentage is zero, fall through to amount or base
                    amt = base_amount
            elif detail.get("amount") and str(detail["amount"]).strip():
                amt = to_decimal(detail["amount"])
                # If amount is zero, treat as "use base_amount from assignment"
                if amt == Decimal("0"):
                    amt = base_amount
            else:
                # Fallback: use the assignment base amount
                amt = base_amount

            # Payment day proration
            if detail["depends_on_payment_days"]:
                if payment_days < total_working_days and total_working_days > 0:
                    amt = amt * payment_days / total_working_days

            amt = round_currency(amt)
            component_amounts[comp_id] = amt
            gross += amt
            # Track supplemental wages for flat tax treatment (Feature #22d)
            if detail.get("is_supplemental"):
                supplemental_gross += amt
            earnings_details.append((comp_id, detail["component_name"], amt))

        gross = round_currency(gross)

        # Step 2b: Overtime integration (Feature #22b)
        # Check if company has an overtime policy and if the employee has
        # attendance records with overtime hours in this period
        ot_amount = Decimal("0")
        op_t = Table("overtime_policy")
        op_q = Q.from_(op_t).select(op_t.star).where(op_t.company_id == P())
        ot_policy = conn.execute(op_q.get_sql(), (company_id,)).fetchone()

        if ot_policy:
            ot_policy = row_to_dict(ot_policy)
            weekly_threshold = to_decimal(ot_policy["weekly_threshold"])
            ot_multiplier = to_decimal(ot_policy["ot_multiplier"])
            daily_threshold = to_decimal(ot_policy["daily_threshold"]) if ot_policy.get("daily_threshold") else None

            # Derive hourly rate from base monthly salary
            annual_salary = base_amount * Decimal("12")
            hourly_rate = round_currency(annual_salary / Decimal("2080"))

            # Get attendance hours for this period
            ot_att_rows = conn.execute(
                """SELECT attendance_date, working_hours
                   FROM attendance
                   WHERE employee_id = ?
                     AND attendance_date >= ?
                     AND attendance_date <= ?
                     AND status IN ('present', 'work_from_home', 'half_day')
                   ORDER BY attendance_date""",
                (employee_id, period_start, period_end),
            ).fetchall()

            total_hours = Decimal("0")
            daily_ot_hours = Decimal("0")
            for att in ot_att_rows:
                att_d = row_to_dict(att)
                hours = to_decimal(att_d.get("working_hours") or "8")
                total_hours += hours
                if daily_threshold and hours > daily_threshold:
                    daily_ot_hours += hours - daily_threshold

            start_dt = datetime.strptime(period_start, "%Y-%m-%d")
            end_dt = datetime.strptime(period_end, "%Y-%m-%d")
            total_days = (end_dt - start_dt).days + 1
            num_weeks = max(Decimal("1"), Decimal(str(total_days)) / Decimal("7"))
            weekly_limit = weekly_threshold * num_weeks
            weekly_ot_hours = max(Decimal("0"), total_hours - weekly_limit)
            ot_hours = max(daily_ot_hours, weekly_ot_hours)

            if ot_hours > 0:
                ot_amount = round_currency(ot_hours * hourly_rate * ot_multiplier)
                gross += ot_amount

                # Create a salary component for overtime
                ot_comp_id = _get_or_create_statutory_component(
                    conn, "Overtime Pay", "earning", is_statutory=0
                )
                earnings_details.append((ot_comp_id, "Overtime Pay", ot_amount))

        # Step 3: Pre-tax deductions (from employee record)
        pretax_401k = Decimal("0")
        pretax_hsa = Decimal("0")
        emp_401k_rate = to_decimal(emp.get("employee_401k_rate", "0"))
        emp_hsa = to_decimal(emp.get("hsa_contribution", "0"))

        if emp_401k_rate > 0:
            pretax_401k = round_currency(gross * emp_401k_rate / Decimal("100"))
        if emp_hsa > 0:
            pretax_hsa = round_currency(emp_hsa)

        total_pretax = pretax_401k + pretax_hsa

        # Step 4: Federal income tax (with supplemental wage flat-rate — Feature #22d)
        federal_tax = Decimal("0")
        filing_status = emp.get("federal_filing_status") or "single"

        # Supplemental wages: apply flat 22% (37% if aggregate > $1M)
        supplemental_federal_tax = Decimal("0")
        regular_gross = gross - supplemental_gross

        if supplemental_gross > 0:
            # Get YTD supplemental for >$1M check
            ytd_supp = _get_ytd_supplemental(conn, employee_id, period_end, company_id)
            aggregate_supplemental = ytd_supp + supplemental_gross
            if aggregate_supplemental > Decimal("1000000"):
                # 37% on excess over $1M, 22% on rest
                excess = aggregate_supplemental - Decimal("1000000")
                under_1m = supplemental_gross - excess
                if under_1m < 0:
                    under_1m = Decimal("0")
                    excess = supplemental_gross
                supplemental_federal_tax = round_currency(
                    under_1m * Decimal("0.22") + excess * Decimal("0.37")
                )
            else:
                supplemental_federal_tax = round_currency(
                    supplemental_gross * Decimal("0.22")
                )

        # Progressive brackets for regular (non-supplemental) wages
        # raw SQL — uses IS NULL in OR clause and CASE in ORDER BY
        fed_slab = conn.execute(
            """
            SELECT its.*
            FROM income_tax_slab its
            WHERE its.tax_jurisdiction = 'federal'
              AND its.is_active = 1
              AND its.effective_from <= ?
              AND (its.filing_status = ? OR its.filing_status IS NULL)
            ORDER BY
                CASE WHEN its.filing_status = ? THEN 0 ELSE 1 END,
                its.effective_from DESC
            LIMIT 1
            """,
            (period_end, filing_status, filing_status),
        ).fetchone()

        if fed_slab and regular_gross > 0:
            fed_slab = row_to_dict(fed_slab)
            standard_deduction = to_decimal(fed_slab.get("standard_deduction", "0"))

            # Get slab rates
            # raw SQL — ORDER BY from_amount + 0 (numeric cast) not easily expressed in PyPika
            fed_rates = conn.execute(
                """
                SELECT from_amount, to_amount, rate
                FROM income_tax_slab_rate
                WHERE slab_id = ?
                ORDER BY from_amount + 0 ASC
                """,
                (fed_slab["id"],),
            ).fetchall()
            fed_rates = [row_to_dict(r) for r in fed_rates]

            if fed_rates:
                # Annualize: (regular_gross - pretax) * periods_per_year - standard_deduction
                taxable_periodic = regular_gross - total_pretax
                taxable_annual = taxable_periodic * Decimal(str(periods_per_year)) - standard_deduction
                if taxable_annual < 0:
                    taxable_annual = Decimal("0")

                annual_tax = _calculate_progressive_tax(taxable_annual, fed_rates)
                federal_tax = round_currency(annual_tax / Decimal(str(periods_per_year)))

        # Combine regular + supplemental federal tax
        federal_tax = round_currency(federal_tax + supplemental_federal_tax)

        # Step 5: State income tax (multi-state via employee_state_config + state_tax_slab)
        state_tax = _calculate_state_tax_for_employee(
            conn, employee_id, gross, total_pretax, periods_per_year, period_end
        )

        # Step 6: FICA (Social Security + Medicare)
        ss_employee = Decimal("0")
        medicare_employee = Decimal("0")
        is_exempt_from_fica = bool(emp.get("is_exempt_from_fica", 0))

        if fica and not is_exempt_from_fica:
            ss_wage_base = to_decimal(fica["ss_wage_base"])
            ss_employee_rate = to_decimal(fica["ss_employee_rate"])
            medicare_employee_rate = to_decimal(fica["medicare_employee_rate"])
            additional_medicare_threshold = to_decimal(fica["additional_medicare_threshold"])
            additional_medicare_rate = to_decimal(fica["additional_medicare_rate"])

            # Get YTD values
            ytd = _get_ytd_values(conn, employee_id, period_end, company_id)
            ytd_gross = ytd["ytd_gross"]

            # Social Security: capped at wage base
            ss_taxable = min(gross, max(Decimal("0"), ss_wage_base - ytd_gross))
            ss_employee = round_currency(ss_taxable * ss_employee_rate / Decimal("100"))

            # Medicare: no wage base cap
            medicare_employee = round_currency(gross * medicare_employee_rate / Decimal("100"))

            # Additional Medicare: 0.9% on wages over threshold (annualized)
            ytd_total_wages = ytd_gross + gross
            if ytd_total_wages > additional_medicare_threshold:
                # Only the excess beyond the threshold is subject to additional Medicare
                excess = ytd_total_wages - max(additional_medicare_threshold, ytd_gross)
                if excess > Decimal("0"):
                    additional_medicare = round_currency(
                        excess * additional_medicare_rate / Decimal("100")
                    )
                    medicare_employee += additional_medicare

        # Step 7: Total deductions and net pay
        total_deductions = total_pretax + federal_tax + state_tax + ss_employee + medicare_employee
        total_deductions = round_currency(total_deductions)
        net_pay = round_currency(gross - total_deductions)

        # --- Create salary slip ---
        slip_id = str(uuid.uuid4())
        slip_naming = get_next_name(conn, "salary_slip", company_id=company_id)

        ins_slip_sql, _ = insert_row("salary_slip", {
            "id": P(), "naming_series": P(), "payroll_run_id": P(),
            "employee_id": P(), "period_start": P(), "period_end": P(),
            "total_working_days": P(), "payment_days": P(),
            "gross_pay": P(), "total_deductions": P(), "net_pay": P(),
            "status": P(), "company_id": P(),
        })
        conn.execute(ins_slip_sql, (
            slip_id, slip_naming, payroll_run_id, employee_id,
            period_start, period_end,
            str(round_currency(total_working_days)),
            str(round_currency(payment_days)),
            str(gross), str(total_deductions), str(net_pay),
            "draft", company_id,
        ))

        # --- Create salary_slip_detail rows ---

        # Reusable INSERT for salary_slip_detail
        ins_det_sql, _ = insert_row("salary_slip_detail", {
            "id": P(), "salary_slip_id": P(), "salary_component_id": P(),
            "component_type": P(), "amount": P(), "year_to_date": P(),
        })

        # Earnings
        for comp_id, comp_name, amt in earnings_details:
            detail_id = str(uuid.uuid4())
            conn.execute(ins_det_sql, (detail_id, slip_id, comp_id, "earning", str(amt), "0"))

        # Deductions: pre-tax (401k, HSA)
        if pretax_401k > 0:
            comp_401k_id = _get_or_create_statutory_component(
                conn, "401k Contribution", "deduction", is_statutory=0, is_pre_tax=1
            )
            detail_id = str(uuid.uuid4())
            conn.execute(ins_det_sql, (detail_id, slip_id, comp_401k_id, "deduction", str(pretax_401k), "0"))

        if pretax_hsa > 0:
            comp_hsa_id = _get_or_create_statutory_component(
                conn, "HSA Contribution", "deduction", is_statutory=0, is_pre_tax=1
            )
            detail_id = str(uuid.uuid4())
            conn.execute(ins_det_sql, (detail_id, slip_id, comp_hsa_id, "deduction", str(pretax_hsa), "0"))

        # Deductions: federal income tax
        if federal_tax > 0:
            comp_fed_id = _get_or_create_statutory_component(
                conn, "Federal Income Tax", "deduction", is_statutory=1
            )
            detail_id = str(uuid.uuid4())
            conn.execute(ins_det_sql, (detail_id, slip_id, comp_fed_id, "deduction", str(federal_tax), "0"))

        # Deductions: state income tax
        if state_tax > 0:
            comp_state_id = _get_or_create_statutory_component(
                conn, "State Income Tax", "deduction", is_statutory=1
            )
            detail_id = str(uuid.uuid4())
            conn.execute(ins_det_sql, (detail_id, slip_id, comp_state_id, "deduction", str(state_tax), "0"))

        # Deductions: FICA
        if ss_employee > 0:
            comp_ss_id = _get_or_create_statutory_component(
                conn, "Social Security Tax", "deduction", is_statutory=1
            )
            detail_id = str(uuid.uuid4())
            conn.execute(ins_det_sql, (detail_id, slip_id, comp_ss_id, "deduction", str(ss_employee), "0"))

        if medicare_employee > 0:
            comp_med_id = _get_or_create_statutory_component(
                conn, "Medicare Tax", "deduction", is_statutory=1
            )
            detail_id = str(uuid.uuid4())
            conn.execute(ins_det_sql, (detail_id, slip_id, comp_med_id, "deduction", str(medicare_employee), "0"))

        # Include structure-defined deduction components
        for detail in details:
            if detail["component_type"] != "deduction":
                continue

            comp_id = detail["salary_component_id"]
            # Skip statutory deductions we already handled above
            # (those are calculated, not from structure details)
            if detail.get("is_pre_tax") or detail.get("component_name") in (
                "Federal Income Tax", "State Income Tax",
                "Social Security Tax", "Medicare Tax",
                "401k Contribution", "HSA Contribution",
            ):
                continue

            amt = Decimal("0")
            # Check percentage FIRST (consistent with earnings calc)
            if detail.get("percentage") and str(detail["percentage"]).strip():
                pct = to_decimal(detail["percentage"])
                if pct > Decimal("0"):
                    base_comp_id = detail.get("base_component_id")
                    if base_comp_id and base_comp_id in component_amounts:
                        base_amt = component_amounts[base_comp_id]
                    else:
                        base_amt = gross
                    amt = base_amt * pct / Decimal("100")
            elif detail.get("amount") and str(detail["amount"]).strip():
                amt = to_decimal(detail["amount"])

            if detail["depends_on_payment_days"]:
                if payment_days < total_working_days and total_working_days > 0:
                    amt = amt * payment_days / total_working_days

            amt = round_currency(amt)
            if amt > 0:
                detail_id = str(uuid.uuid4())
                conn.execute(ins_det_sql, (detail_id, slip_id, comp_id, "deduction", str(amt), "0"))
                total_deductions += amt
                net_pay -= amt

                # Rewrite the slip totals with the additional deduction
                upd_slip_sql = update_row("salary_slip",
                                          data={"total_deductions": P(), "net_pay": P()},
                                          where={"id": P()})
                conn.execute(upd_slip_sql, (str(round_currency(total_deductions)),
                                            str(round_currency(net_pay)), slip_id))

        # ---- Wage garnishments (post-tax, priority-ordered, with federal caps) ----
        wg_t = Table("wage_garnishment")
        garn_q = (Q.from_(wg_t).select(wg_t.star)
                  .where(wg_t.employee_id == P())
                  .where(wg_t.status == ValueWrapper("active"))
                  .orderby(wg_t.priority).orderby(wg_t.created_at))
        garnishments = conn.execute(garn_q.get_sql(), (employee_id,)).fetchall()

        if garnishments:
            disposable_income = net_pay  # After taxes and other deductions
            total_garnishment = Decimal("0")

            for garn in garnishments:
                if disposable_income <= 0:
                    break

                garn_type = garn["garnishment_type"]
                cumulative = to_decimal(garn["cumulative_paid"])
                total_owed_val = to_decimal(garn["total_owed"]) if garn["total_owed"] else None

                # Skip if already fully paid
                if total_owed_val and cumulative >= total_owed_val:
                    continue

                # Calculate garnishment amount
                if garn["is_percentage"]:
                    garn_amt = round_currency(
                        disposable_income * to_decimal(garn["amount_or_percentage"]) / Decimal("100")
                    )
                else:
                    garn_amt = round_currency(to_decimal(garn["amount_or_percentage"]))

                # Apply federal max_percentage cap on disposable income
                max_pct = to_decimal(garn["max_percentage"])
                max_allowed = round_currency(disposable_income * max_pct / Decimal("100"))
                if garn_amt > max_allowed:
                    garn_amt = max_allowed

                # Don't exceed remaining balance owed
                if total_owed_val:
                    remaining = total_owed_val - cumulative
                    if garn_amt > remaining:
                        garn_amt = round_currency(remaining)

                if garn_amt <= 0:
                    continue

                # Create salary slip detail for garnishment
                comp_garn_id = _get_or_create_statutory_component(
                    conn, f"Garnishment - {garn['creditor_name']}", "deduction",
                    is_statutory=1,
                )
                detail_id = str(uuid.uuid4())
                ins_garn_det_sql, _ = insert_row("salary_slip_detail", {
                    "id": P(), "salary_slip_id": P(), "salary_component_id": P(),
                    "component_type": P(), "amount": P(), "year_to_date": P(),
                })
                conn.execute(ins_garn_det_sql, (detail_id, slip_id, comp_garn_id,
                                                "deduction", str(garn_amt),
                                                str(cumulative + garn_amt)))

                total_deductions += garn_amt
                net_pay -= garn_amt
                total_garnishment += garn_amt

                # Update cumulative paid on the garnishment record
                new_cumulative = cumulative + garn_amt
                # raw SQL — uses datetime('now') which is a SQLite function
                conn.execute(
                    "UPDATE wage_garnishment SET cumulative_paid = ?, updated_at = datetime('now') WHERE id = ?",
                    (str(new_cumulative), garn["id"]),
                )

                # Auto-complete if fully paid
                if total_owed_val and new_cumulative >= total_owed_val:
                    # raw SQL — uses datetime('now') which is a SQLite function
                    conn.execute(
                        "UPDATE wage_garnishment SET status = 'completed', updated_at = datetime('now') WHERE id = ?",
                        (garn["id"],),
                    )

            if total_garnishment > 0:
                upd_slip_garn = update_row("salary_slip",
                                           data={"total_deductions": P(), "net_pay": P()},
                                           where={"id": P()})
                conn.execute(upd_slip_garn, (str(round_currency(total_deductions)),
                                             str(round_currency(net_pay)), slip_id))

        # Accumulate run totals
        run_total_gross += gross
        run_total_deductions += total_deductions
        run_total_net += net_pay
        slips_generated += 1

    # --- Update payroll_run totals ---
    # raw SQL — uses datetime('now') SQLite function
    conn.execute(
        """
        UPDATE payroll_run
        SET total_gross = ?,
            total_deductions = ?,
            total_net = ?,
            employee_count = ?,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (str(round_currency(run_total_gross)),
         str(round_currency(run_total_deductions)),
         str(round_currency(run_total_net)),
         slips_generated,
         payroll_run_id),
    )

    audit(conn, "erpclaw-payroll", "generate-salary-slips", "payroll_run", payroll_run_id,
           new_values={"slips_generated": slips_generated,
                       "total_gross": str(round_currency(run_total_gross)),
                       "total_net": str(round_currency(run_total_net))},
           description=f"Generated {slips_generated} salary slips")

    conn.commit()
    ok({
        "payroll_run_id": payroll_run_id,
        "slips_generated": slips_generated,
        "total_gross": str(round_currency(run_total_gross)),
        "total_deductions": str(round_currency(run_total_deductions)),
        "total_net": str(round_currency(run_total_net)),
    })


# ============================================================================
# ACTION 10: get_salary_slip
# ============================================================================

def get_salary_slip(conn: sqlite3.Connection, args) -> None:
    """Retrieve a salary slip with nested earnings and deduction details.

    Required args:
        --salary-slip-id: The salary slip ID to retrieve.

    Returns:
        Slip record with nested 'earnings' and 'deductions' arrays.
        Each detail includes: component_id, component_name, component_type, amount.
    """
    slip_id = args.salary_slip_id

    if not slip_id:
        err("--salary-slip-id is required")

    ss_t = Table("salary_slip").as_("ss")
    e_t = Table("employee").as_("e")
    slip_q = (Q.from_(ss_t)
              .join(e_t).on(e_t.id == ss_t.employee_id)
              .select(ss_t.star,
                      e_t.full_name.as_("employee_name"),
                      e_t.first_name, e_t.last_name)
              .where(ss_t.id == P()))
    slip = conn.execute(slip_q.get_sql(), (slip_id,)).fetchone()
    if not slip:
        err(f"Salary slip {slip_id} not found")

    slip_dict = row_to_dict(slip)

    # Get details split by type
    ssd_t = Table("salary_slip_detail").as_("ssd")
    sc_t = Table("salary_component").as_("sc")
    det_q = (Q.from_(ssd_t)
             .join(sc_t).on(sc_t.id == ssd_t.salary_component_id)
             .select(ssd_t.star, sc_t.name.as_("component_name"))
             .where(ssd_t.salary_slip_id == P())
             .orderby(ssd_t.component_type).orderby(sc_t.name))
    details = conn.execute(det_q.get_sql(), (slip_id,)).fetchall()

    earnings = []
    deductions = []
    for d in details:
        d_dict = row_to_dict(d)
        entry = {
            "id": d_dict["id"],
            "salary_component_id": d_dict["salary_component_id"],
            "component_name": d_dict["component_name"],
            "component_type": d_dict["component_type"],
            "amount": d_dict["amount"],
            "year_to_date": d_dict["year_to_date"],
        }
        if d_dict["component_type"] == "earning":
            earnings.append(entry)
        else:
            deductions.append(entry)

    slip_dict["earnings"] = earnings
    slip_dict["deductions"] = deductions
    # Combined details list (earnings + deductions) for easy iteration
    slip_dict["details"] = earnings + deductions

    # Flatten: return slip fields at top level (not nested under "salary_slip")
    ok(slip_dict)


# ============================================================================
# ACTION 11: list_salary_slips
# ============================================================================

def list_salary_slips(conn: sqlite3.Connection, args) -> None:
    """List salary slips with optional filters.

    Optional args:
        --payroll-run-id: Filter by payroll run.
        --employee-id: Filter by employee.
        --status: Filter by status (draft/submitted/paid/cancelled).
        --limit: Max results (default 20).
        --offset: Pagination offset (default 0).

    Returns:
        {"status":"ok", "count":N, "slips":[...]}
    """
    limit = int(args.limit or "20")
    offset = int(args.offset or "0")

    ss_t = Table("salary_slip").as_("ss")
    e_t = Table("employee").as_("e")
    params = []

    list_q = (Q.from_(ss_t)
              .join(e_t).on(e_t.id == ss_t.employee_id)
              .select(ss_t.star, e_t.full_name.as_("employee_name")))
    count_q = Q.from_(ss_t).select(fn.Count("*").as_("cnt"))

    if args.payroll_run_id:
        list_q = list_q.where(ss_t.payroll_run_id == P())
        count_q = count_q.where(ss_t.payroll_run_id == P())
        params.append(args.payroll_run_id)

    if args.employee_id:
        list_q = list_q.where(ss_t.employee_id == P())
        count_q = count_q.where(ss_t.employee_id == P())
        params.append(args.employee_id)

    if args.status:
        list_q = list_q.where(ss_t.status == P())
        count_q = count_q.where(ss_t.status == P())
        params.append(args.status)

    # Count
    total = conn.execute(count_q.get_sql(), params).fetchone()["cnt"]

    # Fetch with pagination
    list_q = list_q.orderby(ss_t.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(list_q.get_sql(), params + [limit, offset]).fetchall()
    slips = [row_to_dict(r) for r in rows]

    ok({"count": total, "slips": slips,
         "limit": limit, "offset": offset, "has_more": offset + limit < total})


# ============================================================================
# ACTION 12: submit_payroll_run -- ATOMIC GL POSTING
# ============================================================================

def submit_payroll_run(conn: sqlite3.Connection, args) -> None:
    """Submit a payroll run: mark slips as submitted and post GL entries.

    Required args:
        --payroll-run-id: The draft payroll run to submit.
        --cost-center-id: Cost center for expense entries (required for GL validation).

    Validates:
        - Payroll run exists and is in 'draft' status.
        - Payroll run has at least one salary slip.
        - Required GL accounts can be found.

    In a SINGLE transaction:
        1. Mark all draft salary slips as 'submitted'.
        2. Build GL entries:
           - DR Salary Expense: total gross (per component GL account or default).
           - DR Employer Tax Expense: employer SS + Medicare + FUTA + SUTA.
           - CR Payroll Payable: net pay per employee (with party tracking).
           - CR Federal IT Withheld: total federal tax deductions.
           - CR SS Payable: employee SS + employer SS.
           - CR Medicare Payable: employee Medicare + employer Medicare.
           - CR FUTA Payable: employer FUTA (if applicable).
           - CR SUTA Payable: employer SUTA (if applicable).
        3. Post GL via insert_gl_entries().
        4. Update payroll_run status = 'submitted'.

    Returns:
        {"status":"ok", "payroll_run_id":"...", "gl_entries":N}
    """
    payroll_run_id = args.payroll_run_id
    cost_center_id = getattr(args, "cost_center_id", None)

    if not payroll_run_id:
        err("--payroll-run-id is required")

    # --- Validate payroll run ---
    pr_t = Table("payroll_run")
    run_q = Q.from_(pr_t).select(pr_t.star).where(pr_t.id == P())
    run = conn.execute(run_q.get_sql(), (payroll_run_id,)).fetchone()
    if not run:
        err(f"Payroll run {payroll_run_id} not found")

    run = row_to_dict(run)
    if run["status"] != "draft":
        err(f"Payroll run is '{run['status']}', must be 'draft' to submit")

    company_id = run["company_id"]
    period_end = run["period_end"]
    tax_year = int(period_end[:4])

    # Must have slips
    ss_t = Table("salary_slip")
    slips_q = Q.from_(ss_t).select(ss_t.star).where(ss_t.payroll_run_id == P()).where(ss_t.status == ValueWrapper("draft"))
    slips = conn.execute(slips_q.get_sql(), (payroll_run_id,)).fetchall()
    if not slips:
        err("Payroll run has no draft salary slips. Generate slips first.")

    slips = [row_to_dict(s) for s in slips]

    # --- Find GL accounts ---
    try:
        accounts = _find_payroll_accounts(conn, company_id)
    except ValueError as e:
        err(str(e))

    # If no cost_center_id provided, try to find a default one
    if not cost_center_id:
        cc_t = Table("cost_center")
        cc_q = (Q.from_(cc_t).select(cc_t.id)
                .where(cc_t.company_id == P())
                .where(cc_t.is_group == 0)
                .orderby(cc_t.name).limit(1))
        cc = conn.execute(cc_q.get_sql(), (company_id,)).fetchone()
        if cc:
            cost_center_id = cc["id"]
        else:
            err("--cost-center-id is required (no default cost center found)")

    # --- Gather FICA config for employer-side calculations ---
    fc_t = Table("fica_config")
    fc_q = Q.from_(fc_t).select(fc_t.star).where(fc_t.tax_year == P())
    fica_config = conn.execute(fc_q.get_sql(), (tax_year,)).fetchone()
    fica = row_to_dict(fica_config) if fica_config else None

    # --- Gather FUTA/SUTA config ---
    # raw SQL — uses IS NULL and OR state_code = '' checks
    futa_config = conn.execute(
        """SELECT * FROM futa_suta_config
           WHERE tax_year = ? AND (state_code IS NULL OR state_code = '')""",
        (tax_year,),
    ).fetchone()
    futa = row_to_dict(futa_config) if futa_config else None

    # raw SQL — uses IS NOT NULL and state_code != '' checks
    suta_configs = conn.execute(
        """SELECT * FROM futa_suta_config
           WHERE tax_year = ? AND state_code IS NOT NULL AND state_code != ''""",
        (tax_year,),
    ).fetchall()
    suta_map = {}
    for sc in suta_configs:
        sc_dict = row_to_dict(sc)
        suta_map[sc_dict["state_code"]] = sc_dict

    # --- Begin building GL entries ---
    # We'll accumulate totals across all slips, then build entries
    total_gross = Decimal("0")
    total_net = Decimal("0")
    total_federal_tax = Decimal("0")
    total_state_tax = Decimal("0")
    total_ss_employee = Decimal("0")
    total_medicare_employee = Decimal("0")
    total_ss_employer = Decimal("0")
    total_medicare_employer = Decimal("0")
    total_futa = Decimal("0")
    total_suta = Decimal("0")

    # Per-employee net pay for party tracking
    employee_net_pay = {}  # employee_id -> net_pay Decimal

    # Per-employee pre-tax deductions for party-tracked payroll payable
    employee_pretax = {}  # employee_id -> pretax Decimal

    # Per-component GL account tracking for granular expense entries
    component_expense_totals = {}  # gl_account_id -> Decimal

    for slip in slips:
        employee_id = slip["employee_id"]
        slip_gross = to_decimal(slip["gross_pay"])
        slip_net = to_decimal(slip["net_pay"])

        total_gross += slip_gross
        total_net += slip_net

        if employee_id in employee_net_pay:
            employee_net_pay[employee_id] += slip_net
        else:
            employee_net_pay[employee_id] = slip_net

        # Get slip details for federal tax, SS, Medicare
        ssd_t2 = Table("salary_slip_detail").as_("ssd")
        sc_t2 = Table("salary_component").as_("sc")
        sd_q = (Q.from_(ssd_t2)
                .join(sc_t2).on(sc_t2.id == ssd_t2.salary_component_id)
                .select(ssd_t2.amount, sc_t2.name.as_("component_name"))
                .where(ssd_t2.salary_slip_id == P())
                .where(ssd_t2.component_type == ValueWrapper("deduction")))
        slip_details = conn.execute(sd_q.get_sql(), (slip["id"],)).fetchall()

        for d in slip_details:
            d_dict = row_to_dict(d)
            amt = to_decimal(d_dict["amount"])
            name = d_dict["component_name"]

            if name == "Federal Income Tax":
                total_federal_tax += amt
            elif name == "State Income Tax":
                total_state_tax += amt
            elif name == "Social Security Tax":
                total_ss_employee += amt
            elif name == "Medicare Tax":
                total_medicare_employee += amt

        # Accumulate per-employee pre-tax deductions for payroll payable tracking
        ssd_pt = Table("salary_slip_detail").as_("ssd")
        sc_pt = Table("salary_component").as_("sc")
        pt_q = (Q.from_(ssd_pt)
                .join(sc_pt).on(sc_pt.id == ssd_pt.salary_component_id)
                .select(fn.Coalesce(DecimalSum(ssd_pt.amount), ValueWrapper("0")).as_("total"))
                .where(ssd_pt.salary_slip_id == P())
                .where(ssd_pt.component_type == ValueWrapper("deduction"))
                .where(sc_pt.is_pre_tax == 1))
        pretax_row = conn.execute(pt_q.get_sql(), (slip["id"],)).fetchone()
        if pretax_row:
            emp_pretax = to_decimal(str(pretax_row["total"]))
            if employee_id in employee_pretax:
                employee_pretax[employee_id] += emp_pretax
            else:
                employee_pretax[employee_id] = emp_pretax

        # Accumulate earning component amounts by GL account
        ssd_earn = Table("salary_slip_detail").as_("ssd")
        sc_earn = Table("salary_component").as_("sc")
        earn_q = (Q.from_(ssd_earn)
                  .join(sc_earn).on(sc_earn.id == ssd_earn.salary_component_id)
                  .select(ssd_earn.amount, sc_earn.gl_account_id)
                  .where(ssd_earn.salary_slip_id == P())
                  .where(ssd_earn.component_type == ValueWrapper("earning")))
        earning_details = conn.execute(earn_q.get_sql(), (slip["id"],)).fetchall()

        for ed in earning_details:
            ed_dict = row_to_dict(ed)
            gl_acct = ed_dict.get("gl_account_id") or accounts["salary_expense"]
            amt = to_decimal(ed_dict["amount"])
            if gl_acct in component_expense_totals:
                component_expense_totals[gl_acct] += amt
            else:
                component_expense_totals[gl_acct] = amt

        # --- Employer-side tax calculations per employee ---
        emp_t = Table("employee")
        emp_q = Q.from_(emp_t).select(emp_t.star).where(emp_t.id == P())
        emp = conn.execute(emp_q.get_sql(), (employee_id,)).fetchone()
        emp_dict = row_to_dict(emp) if emp else {}
        is_exempt = bool(emp_dict.get("is_exempt_from_fica", 0))

        if fica and not is_exempt:
            ss_employer_rate = to_decimal(fica["ss_employer_rate"])
            medicare_employer_rate = to_decimal(fica["medicare_employer_rate"])
            ss_wage_base = to_decimal(fica["ss_wage_base"])

            # Get YTD gross for SS cap
            ytd = _get_ytd_values(conn, employee_id, slip["period_end"], company_id)
            ytd_gross = ytd["ytd_gross"]

            # Employer SS (same cap as employee)
            ss_taxable = min(slip_gross, max(Decimal("0"), ss_wage_base - ytd_gross))
            emp_ss = round_currency(ss_taxable * ss_employer_rate / Decimal("100"))
            total_ss_employer += emp_ss

            # Employer Medicare (no cap)
            emp_medicare = round_currency(slip_gross * medicare_employer_rate / Decimal("100"))
            total_medicare_employer += emp_medicare

        # FUTA (federal unemployment) -- employer only
        if futa and not is_exempt:
            futa_wage_base = to_decimal(futa["wage_base"])
            futa_rate = to_decimal(futa.get("employer_rate_override") or futa["rate"])
            ytd = _get_ytd_values(conn, employee_id, slip["period_end"], company_id)
            ytd_gross = ytd["ytd_gross"]
            futa_taxable = min(slip_gross, max(Decimal("0"), futa_wage_base - ytd_gross))
            emp_futa = round_currency(futa_taxable * futa_rate / Decimal("100"))
            total_futa += emp_futa

        # SUTA (state unemployment) -- employer only
        # For simplicity, apply the first matching SUTA config
        # A more complete implementation would match employee work state
        if suta_map and not is_exempt:
            for state_code, suta_cfg in suta_map.items():
                suta_wage_base = to_decimal(suta_cfg["wage_base"])
                suta_rate = to_decimal(
                    suta_cfg.get("employer_rate_override") or suta_cfg["rate"]
                )
                ytd = _get_ytd_values(conn, employee_id, slip["period_end"], company_id)
                ytd_gross = ytd["ytd_gross"]
                suta_taxable = min(slip_gross, max(Decimal("0"), suta_wage_base - ytd_gross))
                emp_suta = round_currency(suta_taxable * suta_rate / Decimal("100"))
                total_suta += emp_suta
                break  # Apply first SUTA config only

    # Round all totals
    total_gross = round_currency(total_gross)
    total_net = round_currency(total_net)
    total_federal_tax = round_currency(total_federal_tax)
    total_state_tax = round_currency(total_state_tax)
    total_ss_employee = round_currency(total_ss_employee)
    total_medicare_employee = round_currency(total_medicare_employee)
    total_ss_employer = round_currency(total_ss_employer)
    total_medicare_employer = round_currency(total_medicare_employer)
    total_futa = round_currency(total_futa)
    total_suta = round_currency(total_suta)

    # Total employer tax expense
    total_employer_tax = total_ss_employer + total_medicare_employer + total_futa + total_suta

    # --- Build GL entries ---
    gl_entries = []

    # DR: Salary Expense (by component GL account)
    for gl_acct_id, amount in component_expense_totals.items():
        amt = round_currency(amount)
        if amt > 0:
            gl_entries.append({
                "account_id": gl_acct_id,
                "debit": str(amt),
                "credit": "0",
                "cost_center_id": cost_center_id,
            })

    # DR: Employer Tax Expense
    if total_employer_tax > 0 and accounts.get("employer_tax_expense"):
        gl_entries.append({
            "account_id": accounts["employer_tax_expense"],
            "debit": str(total_employer_tax),
            "credit": "0",
            "cost_center_id": cost_center_id,
        })

    # CR: Payroll Payable (per employee for party tracking)
    # Includes net pay + pre-tax deductions (401k, HSA) since those represent
    # obligations the company must forward on behalf of the employee.
    if accounts.get("payroll_payable"):
        for emp_id, net_amt in employee_net_pay.items():
            pretax_amt = employee_pretax.get(emp_id, Decimal("0"))
            payable_amt = round_currency(net_amt + pretax_amt)
            if payable_amt > 0:
                gl_entries.append({
                    "account_id": accounts["payroll_payable"],
                    "debit": "0",
                    "credit": str(payable_amt),
                    "party_type": "employee",
                    "party_id": emp_id,
                })

    # CR: Federal IT Withheld
    if total_federal_tax > 0 and accounts.get("federal_tax_payable"):
        gl_entries.append({
            "account_id": accounts["federal_tax_payable"],
            "debit": "0",
            "credit": str(total_federal_tax),
        })

    # CR: State IT Withheld
    if total_state_tax > 0 and accounts.get("state_tax_payable"):
        gl_entries.append({
            "account_id": accounts["state_tax_payable"],
            "debit": "0",
            "credit": str(total_state_tax),
        })

    # CR: Social Security Payable (employee + employer)
    total_ss = total_ss_employee + total_ss_employer
    if total_ss > 0 and accounts.get("ss_payable"):
        gl_entries.append({
            "account_id": accounts["ss_payable"],
            "debit": "0",
            "credit": str(round_currency(total_ss)),
        })

    # CR: Medicare Payable (employee + employer)
    total_medicare = total_medicare_employee + total_medicare_employer
    if total_medicare > 0 and accounts.get("medicare_payable"):
        gl_entries.append({
            "account_id": accounts["medicare_payable"],
            "debit": "0",
            "credit": str(round_currency(total_medicare)),
        })

    # CR: FUTA Payable
    if total_futa > 0 and accounts.get("futa_payable"):
        gl_entries.append({
            "account_id": accounts["futa_payable"],
            "debit": "0",
            "credit": str(total_futa),
        })

    # CR: SUTA Payable
    if total_suta > 0 and accounts.get("suta_payable"):
        gl_entries.append({
            "account_id": accounts["suta_payable"],
            "debit": "0",
            "credit": str(total_suta),
        })

    # --- Balance check: DR must equal CR ---
    #
    # DR = total_gross + total_employer_tax
    # CR = payroll_payable (net_pay + pretax) + federal_tax + state_tax
    #    + ss (employee + employer) + medicare (employee + employer)
    #    + futa + suta
    #
    # Accounting identity:
    #   gross = net_pay + all_employee_deductions
    #         = net_pay + pretax + federal_tax + state_tax + ss_emp + med_emp
    #           + other_deductions + garnishments
    #
    #   DR Salary Expense = gross
    #   CR Payroll Payable = net_pay + pretax (401k, HSA -- employer remits on behalf)
    #   CR Federal IT Payable = federal_tax
    #   CR State IT Payable = state_tax
    #   CR SS Payable = ss_employee + ss_employer
    #   CR Medicare Payable = medicare_employee + medicare_employer
    #   CR FUTA Payable = futa
    #   CR SUTA Payable = suta
    #
    #   DR Employer Tax Expense = ss_employer + medicare_employer + futa + suta
    #
    #   DR total = gross + employer_tax
    #   CR total = (net_pay + pretax) + federal + state + (ss_emp + ss_empr)
    #            + (med_emp + med_empr) + futa + suta
    #           = gross + employer_tax  (balanced)
    #
    # Pre-tax deductions (401k, HSA) are included in per-employee
    # payroll payable CR entries above, so no separate aggregate entry needed.

    # Verify balance before posting
    gl_total_debit = sum(to_decimal(e["debit"]) for e in gl_entries)
    gl_total_credit = sum(to_decimal(e["credit"]) for e in gl_entries)

    if abs(gl_total_debit - gl_total_credit) > Decimal("0.02"):
        # Auto-correct small rounding differences
        diff = gl_total_debit - gl_total_credit
        if abs(diff) <= Decimal("1.00"):
            # Adjust the largest expense entry to balance
            if diff > 0:
                # Need more credit
                for entry in gl_entries:
                    if entry["account_id"] == accounts.get("payroll_payable") and \
                       to_decimal(entry["credit"]) > 0:
                        entry["credit"] = str(
                            round_currency(to_decimal(entry["credit"]) + diff)
                        )
                        break
            else:
                # Need more debit
                for entry in gl_entries:
                    if to_decimal(entry["debit"]) > 0:
                        entry["debit"] = str(
                            round_currency(to_decimal(entry["debit"]) - diff)
                        )
                        break

    # Filter out zero-amount entries (GL validation rejects them)
    gl_entries = [
        e for e in gl_entries
        if to_decimal(e.get("debit", "0")) > 0 or to_decimal(e.get("credit", "0")) > 0
    ]

    if not gl_entries:
        err("No GL entries to post (all amounts are zero)")

    # --- Post GL entries (within this transaction) ---
    try:
        gl_ids = insert_gl_entries(
            conn, gl_entries,
            voucher_type="payroll_entry",
            voucher_id=payroll_run_id,
            posting_date=period_end,
            company_id=company_id,
            remarks=f"Payroll run {run.get('naming_series', payroll_run_id)} "
                    f"for period {run['period_start']} to {period_end}",
        )
    except ValueError as e:
        conn.rollback()
        sys.stderr.write(f"[erpclaw-payroll] {e}\n")
        err(f"GL posting failed: {e}")

    # --- Mark all slips as submitted ---
    # raw SQL — uses datetime('now') SQLite function
    conn.execute(
        """UPDATE salary_slip
           SET status = 'submitted', updated_at = datetime('now')
           WHERE payroll_run_id = ? AND status = 'draft'""",
        (payroll_run_id,),
    )

    # --- Update payroll_run status ---
    # raw SQL — uses datetime('now') SQLite function
    conn.execute(
        """UPDATE payroll_run
           SET status = 'submitted', updated_at = datetime('now')
           WHERE id = ?""",
        (payroll_run_id,),
    )

    audit(conn, "erpclaw-payroll", "submit-payroll-run", "payroll_run", payroll_run_id,
           new_values={"status": "submitted", "gl_entries": len(gl_ids)},
           description=f"Submitted payroll run with {len(gl_ids)} GL entries")

    conn.commit()
    ok({
        "payroll_run_id": payroll_run_id,
        "naming_series": run.get("naming_series"),
        "gl_entries": len(gl_ids),
        "total_gross": str(total_gross),
        "total_net": str(total_net),
        "total_employer_tax": str(round_currency(total_employer_tax)),
    })


# ============================================================================
# ACTION 13: cancel_payroll_run
# ============================================================================

def cancel_payroll_run(conn: sqlite3.Connection, args) -> None:
    """Cancel a submitted payroll run and reverse all GL entries.

    Required args:
        --payroll-run-id: The submitted payroll run to cancel.

    Validates:
        - Payroll run exists and is in 'submitted' status.

    In a SINGLE transaction:
        1. Reverse GL entries via reverse_gl_entries().
        2. Mark all salary slips as 'cancelled'.
        3. Update payroll_run status = 'cancelled'.

    Returns:
        {"status":"ok", "payroll_run_id":"...", "reversed_entries":N}
    """
    payroll_run_id = args.payroll_run_id

    if not payroll_run_id:
        err("--payroll-run-id is required")

    # --- Validate payroll run ---
    pr_t = Table("payroll_run")
    run_q = Q.from_(pr_t).select(pr_t.star).where(pr_t.id == P())
    run = conn.execute(run_q.get_sql(), (payroll_run_id,)).fetchone()
    if not run:
        err(f"Payroll run {payroll_run_id} not found")

    run = row_to_dict(run)
    if run["status"] != "submitted":
        err(f"Payroll run is '{run['status']}', must be 'submitted' to cancel",
             suggestion="Only submitted payroll runs can be cancelled.")

    period_end = run["period_end"]

    # --- Reverse GL entries ---
    try:
        reversal_ids = reverse_gl_entries(
            conn,
            voucher_type="payroll_entry",
            voucher_id=payroll_run_id,
            posting_date=period_end,
        )
    except ValueError as e:
        conn.rollback()
        sys.stderr.write(f"[erpclaw-payroll] {e}\n")
        err(f"GL reversal failed: {e}")

    # --- Mark all slips as cancelled ---
    # raw SQL — uses datetime('now') SQLite function
    conn.execute(
        """UPDATE salary_slip
           SET status = 'cancelled', updated_at = datetime('now')
           WHERE payroll_run_id = ? AND status = 'submitted'""",
        (payroll_run_id,),
    )

    # --- Update payroll_run status ---
    # raw SQL — uses datetime('now') SQLite function
    conn.execute(
        """UPDATE payroll_run
           SET status = 'cancelled', updated_at = datetime('now')
           WHERE id = ?""",
        (payroll_run_id,),
    )

    audit(conn, "erpclaw-payroll", "cancel-payroll-run", "payroll_run", payroll_run_id,
           old_values={"status": "submitted"},
           new_values={"status": "cancelled"},
           description=f"Cancelled payroll run, reversed {len(reversal_ids)} GL entries")

    conn.commit()
    ok({
        "payroll_run_id": payroll_run_id,
        "naming_series": run.get("naming_series"),
        "reversed_entries": len(reversal_ids),
    })


# ============================================================================
# ACTION 17: generate_w2_data
# ============================================================================

def generate_w2_data(conn: sqlite3.Connection, args) -> None:
    """Generate year-end W-2 data for all employees.

    Required args:
        --tax-year: The tax year (e.g., 2026).
        --company-id: The company ID.

    Aggregates all submitted salary slips for the year and produces
    W-2 box data for each employee:

        Box 1: Wages, tips, other compensation
               (gross - pre-tax deductions like 401k and HSA)
        Box 2: Federal income tax withheld
        Box 3: Social Security wages (min of gross, SS wage base)
        Box 4: Social Security tax withheld
        Box 5: Medicare wages and tips (= gross)
        Box 6: Medicare tax withheld
        Box 12a: 401k contributions (Code D)
        Box 12b: HSA contributions (Code W)

    Returns:
        {"status":"ok", "tax_year":2026, "employee_count":N,
         "w2_data":[{employee_id, employee_name, boxes:{...}}, ...]}
    """
    tax_year_str = args.tax_year
    company_id = args.company_id

    if not tax_year_str:
        err("--tax-year is required")
    if not company_id:
        err("--company-id is required")

    try:
        tax_year = int(tax_year_str)
    except (ValueError, TypeError):
        err(f"--tax-year must be an integer, got: {tax_year_str}")

    # Validate company
    co_t = Table("company")
    co_q = Q.from_(co_t).select(co_t.id, co_t.name).where(co_t.id == P())
    company = conn.execute(co_q.get_sql(), (company_id,)).fetchone()
    if not company:
        err(f"Company {company_id} not found")

    company_name = company["name"]
    year_start = f"{tax_year}-01-01"
    year_end = f"{tax_year}-12-31"

    # Get FICA config for SS wage base
    fc_t = Table("fica_config")
    fc_q = Q.from_(fc_t).select(fc_t.star).where(fc_t.tax_year == P())
    fica_config = conn.execute(fc_q.get_sql(), (tax_year,)).fetchone()
    ss_wage_base = to_decimal(fica_config["ss_wage_base"]) if fica_config else Decimal("168600")

    # Get all employees who had submitted salary slips this year
    # raw SQL — DISTINCT with JOIN and multiple table references
    employees = conn.execute(
        """
        SELECT DISTINCT e.id, e.full_name, e.first_name, e.last_name,
               e.ssn, e.federal_filing_status
        FROM employee e
        JOIN salary_slip ss ON ss.employee_id = e.id
        WHERE ss.company_id = ?
          AND ss.status = 'submitted'
          AND ss.period_end >= ?
          AND ss.period_start <= ?
        ORDER BY e.full_name
        """,
        (company_id, year_start, year_end),
    ).fetchall()

    w2_data = []

    for emp_row in employees:
        emp = row_to_dict(emp_row)
        employee_id = emp["id"]

        # Get all submitted slips for this employee in the tax year
        ss_w2 = Table("salary_slip").as_("ss")
        w2_slip_q = (Q.from_(ss_w2)
                     .select(ss_w2.id, ss_w2.gross_pay, ss_w2.total_deductions, ss_w2.net_pay)
                     .where(ss_w2.employee_id == P())
                     .where(ss_w2.company_id == P())
                     .where(ss_w2.status == ValueWrapper("submitted"))
                     .where(ss_w2.period_end >= P())
                     .where(ss_w2.period_start <= P()))
        slip_rows = conn.execute(w2_slip_q.get_sql(),
                                 (employee_id, company_id, year_start, year_end)).fetchall()

        total_gross = Decimal("0")
        total_federal_tax = Decimal("0")
        total_ss_tax = Decimal("0")
        total_medicare_tax = Decimal("0")
        total_401k = Decimal("0")
        total_hsa = Decimal("0")
        total_pretax = Decimal("0")

        for slip_row in slip_rows:
            slip = row_to_dict(slip_row)
            slip_gross = to_decimal(slip["gross_pay"])
            total_gross += slip_gross

            # Get deduction details for this slip
            ssd_w2 = Table("salary_slip_detail").as_("ssd")
            sc_w2 = Table("salary_component").as_("sc")
            w2_det_q = (Q.from_(ssd_w2)
                        .join(sc_w2).on(sc_w2.id == ssd_w2.salary_component_id)
                        .select(ssd_w2.amount, sc_w2.name.as_("component_name"), sc_w2.is_pre_tax)
                        .where(ssd_w2.salary_slip_id == P())
                        .where(ssd_w2.component_type == ValueWrapper("deduction")))
            details = conn.execute(w2_det_q.get_sql(), (slip["id"],)).fetchall()

            for d in details:
                d_dict = row_to_dict(d)
                amt = to_decimal(d_dict["amount"])
                name = d_dict["component_name"]

                if name == "Federal Income Tax":
                    total_federal_tax += amt
                elif name == "Social Security Tax":
                    total_ss_tax += amt
                elif name == "Medicare Tax":
                    total_medicare_tax += amt
                elif name == "401k Contribution":
                    total_401k += amt
                    total_pretax += amt
                elif name == "HSA Contribution":
                    total_hsa += amt
                    total_pretax += amt
                elif d_dict.get("is_pre_tax"):
                    total_pretax += amt

        # Box calculations
        # Box 1: Wages = Gross - Pre-tax deductions (401k, HSA)
        box1 = round_currency(total_gross - total_pretax)

        # Box 2: Federal income tax withheld
        box2 = round_currency(total_federal_tax)

        # Box 3: Social Security wages (capped at SS wage base)
        box3 = round_currency(min(total_gross, ss_wage_base))

        # Box 4: Social Security tax withheld
        box4 = round_currency(total_ss_tax)

        # Box 5: Medicare wages and tips (= gross, no cap)
        box5 = round_currency(total_gross)

        # Box 6: Medicare tax withheld
        box6 = round_currency(total_medicare_tax)

        # Box 12a: 401k (Code D)
        box12a_amount = round_currency(total_401k)

        # Box 12b: HSA (Code W)
        box12b_amount = round_currency(total_hsa)

        # Build Box 12 as a dict of code -> amount (only include non-zero)
        box12 = {}
        if box12a_amount > 0:
            box12["D"] = str(box12a_amount)
        if box12b_amount > 0:
            box12["W"] = str(box12b_amount)

        boxes = {
            "1": str(box1),
            "2": str(box2),
            "3": str(box3),
            "4": str(box4),
            "5": str(box5),
            "6": str(box6),
        }
        if box12:
            boxes["12"] = box12

        w2_entry = {
            "employee_id": employee_id,
            "employee_name": emp["full_name"],
            "ssn_last_four": emp["ssn"][-4:] if emp.get("ssn") else "XXXX",
            "filing_status": emp.get("federal_filing_status", "single"),
            "boxes": boxes,
        }
        w2_data.append(w2_entry)

    ok({
        "tax_year": tax_year,
        "company_id": company_id,
        "company_name": company_name,
        "employee_count": len(w2_data),
        "w2_data": w2_data,
    })


# ============================================================================
# Feature #22a: Multi-State Payroll
# ============================================================================


def add_state_tax_slab(conn, args):
    """Add a state tax bracket/slab.

    Required: --state-code, --bracket-start, --rate
    Optional: --bracket-end, --filing-status (default 'single')
    """
    if not args.state_code:
        err("--state-code is required")
    if not args.bracket_start:
        err("--bracket-start is required")
    if not args.rate:
        err("--rate is required")

    state_code = args.state_code.strip().upper()
    bracket_start = args.bracket_start.strip()
    bracket_end = args.bracket_end.strip() if args.bracket_end else None
    rate = args.rate.strip()
    filing_status = (args.filing_status or "single").strip().lower()

    if filing_status not in VALID_FILING_STATUSES:
        err(f"Invalid filing_status '{filing_status}'. Valid: {VALID_FILING_STATUSES}")

    # Validate numeric values
    try:
        bs = to_decimal(bracket_start)
        if bs < 0:
            err("bracket-start cannot be negative")
    except (InvalidOperation, ValueError):
        err(f"Invalid bracket-start value '{bracket_start}'")

    if bracket_end:
        try:
            be = to_decimal(bracket_end)
            if be <= bs:
                err("bracket-end must be greater than bracket-start")
        except (InvalidOperation, ValueError):
            err(f"Invalid bracket-end value '{bracket_end}'")

    try:
        r = to_decimal(rate)
        if r < 0 or r > 100:
            err("rate must be between 0 and 100")
    except (InvalidOperation, ValueError):
        err(f"Invalid rate value '{rate}'")

    now = datetime.now(timezone.utc).isoformat()
    slab_id = str(uuid.uuid4())

    ins_sql, _ = insert_row("state_tax_slab", {
        "id": P(), "state_code": P(), "bracket_start": P(), "bracket_end": P(),
        "rate": P(), "filing_status": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(ins_sql, (slab_id, state_code, str(round_currency(bs)),
                           str(round_currency(to_decimal(bracket_end))) if bracket_end else None,
                           str(round_currency(r)), filing_status, now, now))
    conn.commit()

    ok({
        "state_tax_slab_id": slab_id,
        "state_code": state_code,
        "bracket_start": str(round_currency(bs)),
        "bracket_end": str(round_currency(to_decimal(bracket_end))) if bracket_end else None,
        "rate": str(round_currency(r)),
        "filing_status": filing_status,
    })


def update_employee_state_config(conn, args):
    """Set or update an employee's work_state and residence_state.

    Required: --employee-id, --work-state, --residence-state
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.work_state:
        err("--work-state is required")
    if not args.residence_state:
        err("--residence-state is required")

    employee_id = args.employee_id.strip()
    work_state = args.work_state.strip().upper()
    residence_state = args.residence_state.strip().upper()

    # Validate employee exists
    emp_t = Table("employee")
    emp_q = Q.from_(emp_t).select(emp_t.id).where(emp_t.id == P())
    if not conn.execute(emp_q.get_sql(), (employee_id,)).fetchone():
        err(f"Employee {employee_id} not found")

    now = datetime.now(timezone.utc).isoformat()
    config_id = str(uuid.uuid4())

    # UPSERT: INSERT OR REPLACE on employee_id unique constraint
    conn.execute(
        """INSERT INTO employee_state_config
           (id, employee_id, work_state, residence_state, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(employee_id) DO UPDATE SET
               work_state = excluded.work_state,
               residence_state = excluded.residence_state,
               updated_at = excluded.updated_at""",
        (config_id, employee_id, work_state, residence_state, now, now)
    )
    conn.commit()

    ok({
        "employee_id": employee_id,
        "work_state": work_state,
        "residence_state": residence_state,
    })


def _calculate_state_tax_for_employee(conn, employee_id, gross, total_pretax,
                                       periods_per_year, period_end):
    """Calculate state income tax for an employee based on their state config.

    Looks up employee_state_config for work_state and residence_state,
    then applies state_tax_slab brackets for each state.

    Returns total state tax for this pay period (Decimal).
    """
    state_tax = Decimal("0")

    # Find employee state config
    esc_t = Table("employee_state_config")
    esc_q = Q.from_(esc_t).select(esc_t.star).where(esc_t.employee_id == P())
    esc = conn.execute(esc_q.get_sql(), (employee_id,)).fetchone()
    if not esc:
        return state_tax

    esc = row_to_dict(esc)
    work_state = esc["work_state"]
    residence_state = esc["residence_state"]

    # Get employee filing status (from employee record)
    emp_t = Table("employee")
    emp_q = Q.from_(emp_t).select(emp_t.state_filing_status).where(emp_t.id == P())
    emp = conn.execute(emp_q.get_sql(), (employee_id,)).fetchone()
    filing_status = emp["state_filing_status"] if emp and emp["state_filing_status"] else "single"

    # Calculate taxable income (annualized)
    taxable_periodic = gross - total_pretax
    taxable_annual = taxable_periodic * Decimal(str(periods_per_year))
    if taxable_annual <= 0:
        return state_tax

    # Process each unique state (work_state, and residence_state if different)
    states_to_process = [work_state]
    if residence_state != work_state:
        states_to_process.append(residence_state)

    for state_code in states_to_process:
        # Get state tax slabs for this state and filing status
        slabs = conn.execute(
            """SELECT bracket_start, bracket_end, rate
               FROM state_tax_slab
               WHERE state_code = ?
                 AND (filing_status = ? OR filing_status IS NULL)
               ORDER BY bracket_start + 0 ASC""",
            (state_code, filing_status),
        ).fetchall()

        if not slabs:
            continue

        slab_rates = [row_to_dict(s) for s in slabs]
        # Convert to format expected by _calculate_progressive_tax
        converted_rates = []
        for s in slab_rates:
            converted_rates.append({
                "from_amount": s["bracket_start"],
                "to_amount": s["bracket_end"],
                "rate": s["rate"],
            })

        annual_state_tax = _calculate_progressive_tax(taxable_annual, converted_rates)
        periodic_state_tax = round_currency(annual_state_tax / Decimal(str(periods_per_year)))
        state_tax += periodic_state_tax

    return state_tax


# ============================================================================
# Feature #22b: Overtime Calculation
# ============================================================================


def add_overtime_policy(conn, args):
    """Add or update an overtime policy for a company.

    Required: --company-id
    Optional: --weekly-threshold (default '40'), --daily-threshold,
              --ot-multiplier (default '1.5'), --double-ot-multiplier (default '2.0')
    """
    if not args.company_id:
        err("--company-id is required")

    company_id = args.company_id.strip()

    # Validate company
    co_t = Table("company")
    co_q = Q.from_(co_t).select(co_t.id).where(co_t.id == P())
    if not conn.execute(co_q.get_sql(), (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    weekly_threshold = args.weekly_threshold or "40"
    daily_threshold = args.daily_threshold if hasattr(args, "daily_threshold") and args.daily_threshold else None
    ot_multiplier = args.ot_multiplier or "1.5"
    double_ot_multiplier = args.double_ot_multiplier or "2.0"

    # Validate numeric values
    for val, name in [(weekly_threshold, "weekly-threshold"),
                      (ot_multiplier, "ot-multiplier"),
                      (double_ot_multiplier, "double-ot-multiplier")]:
        try:
            d = to_decimal(val)
            if d < 0:
                err(f"--{name} cannot be negative")
        except (InvalidOperation, ValueError):
            err(f"Invalid --{name} value '{val}'")

    if daily_threshold:
        try:
            d = to_decimal(daily_threshold)
            if d < 0:
                err("--daily-threshold cannot be negative")
        except (InvalidOperation, ValueError):
            err(f"Invalid --daily-threshold value '{daily_threshold}'")

    now = datetime.now(timezone.utc).isoformat()
    policy_id = str(uuid.uuid4())

    # UPSERT on company_id
    conn.execute(
        """INSERT INTO overtime_policy
           (id, company_id, weekly_threshold, daily_threshold,
            ot_multiplier, double_ot_multiplier, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(company_id) DO UPDATE SET
               weekly_threshold = excluded.weekly_threshold,
               daily_threshold = excluded.daily_threshold,
               ot_multiplier = excluded.ot_multiplier,
               double_ot_multiplier = excluded.double_ot_multiplier,
               updated_at = excluded.updated_at""",
        (policy_id, company_id, weekly_threshold, daily_threshold,
         ot_multiplier, double_ot_multiplier, now, now)
    )
    conn.commit()

    ok({
        "company_id": company_id,
        "weekly_threshold": weekly_threshold,
        "daily_threshold": daily_threshold,
        "ot_multiplier": ot_multiplier,
        "double_ot_multiplier": double_ot_multiplier,
    })


def calculate_overtime(conn, args):
    """Calculate overtime for an employee in a given period.

    Required: --employee-id, --period-start, --period-end
    Optional: --hourly-rate (if not provided, derived from salary assignment)

    Returns: {regular_hours, ot_hours, ot_amount, regular_amount, total_amount}
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.period_start:
        err("--period-start is required")
    if not args.period_end:
        err("--period-end is required")

    employee_id = args.employee_id.strip()
    period_start = args.period_start.strip()
    period_end = args.period_end.strip()

    # Validate employee
    emp_t = Table("employee")
    emp_q = Q.from_(emp_t).select(emp_t.star).where(emp_t.id == P())
    emp_row = conn.execute(emp_q.get_sql(), (employee_id,)).fetchone()
    if not emp_row:
        err(f"Employee {employee_id} not found")
    emp = row_to_dict(emp_row)
    company_id = emp["company_id"]

    # Get overtime policy for the company
    op_t = Table("overtime_policy")
    op_q = Q.from_(op_t).select(op_t.star).where(op_t.company_id == P())
    policy_row = conn.execute(op_q.get_sql(), (company_id,)).fetchone()

    if not policy_row:
        err(f"No overtime policy found for company {company_id}. "
            "Use add-overtime-policy first.")

    policy = row_to_dict(policy_row)
    weekly_threshold = to_decimal(policy["weekly_threshold"])
    ot_multiplier = to_decimal(policy["ot_multiplier"])
    daily_threshold = to_decimal(policy["daily_threshold"]) if policy.get("daily_threshold") else None

    # Get hourly rate
    hourly_rate = None
    if hasattr(args, "hourly_rate") and args.hourly_rate:
        hourly_rate = to_decimal(args.hourly_rate)
    else:
        # Derive from salary assignment (annual / 2080 for full-time)
        sa_row = conn.execute(
            """SELECT base_amount FROM salary_assignment
               WHERE employee_id = ?
                 AND effective_from <= ?
                 AND (effective_to IS NULL OR effective_to >= ?)
               ORDER BY effective_from DESC LIMIT 1""",
            (employee_id, period_end, period_start),
        ).fetchone()
        if sa_row:
            annual_salary = to_decimal(sa_row["base_amount"]) * Decimal("12")
            hourly_rate = round_currency(annual_salary / Decimal("2080"))
        else:
            err("No salary assignment found and no --hourly-rate provided")

    # Query attendance records for the period
    att_rows = conn.execute(
        """SELECT attendance_date, working_hours
           FROM attendance
           WHERE employee_id = ?
             AND attendance_date >= ?
             AND attendance_date <= ?
             AND status IN ('present', 'work_from_home', 'half_day')
           ORDER BY attendance_date""",
        (employee_id, period_start, period_end),
    ).fetchall()

    # Calculate total hours from attendance
    total_hours = Decimal("0")
    daily_ot_hours = Decimal("0")

    for att in att_rows:
        att_d = row_to_dict(att)
        hours = to_decimal(att_d.get("working_hours") or "8")
        total_hours += hours

        # Daily overtime calculation (if daily_threshold is set)
        if daily_threshold and hours > daily_threshold:
            daily_ot_hours += hours - daily_threshold

    # Weekly overtime calculation
    # total_hours vs weekly_threshold * number_of_weeks
    start_dt = datetime.strptime(period_start, "%Y-%m-%d")
    end_dt = datetime.strptime(period_end, "%Y-%m-%d")
    total_days = (end_dt - start_dt).days + 1
    num_weeks = max(Decimal("1"), Decimal(str(total_days)) / Decimal("7"))
    weekly_limit = weekly_threshold * num_weeks

    weekly_ot_hours = max(Decimal("0"), total_hours - weekly_limit)

    # Use the greater of daily OT or weekly OT (not double-counted)
    ot_hours = max(daily_ot_hours, weekly_ot_hours)
    regular_hours = total_hours - ot_hours

    ot_amount = round_currency(ot_hours * hourly_rate * ot_multiplier)
    regular_amount = round_currency(regular_hours * hourly_rate)
    total_amount = round_currency(regular_amount + ot_amount)

    ok({
        "employee_id": employee_id,
        "period_start": period_start,
        "period_end": period_end,
        "total_hours": str(total_hours),
        "regular_hours": str(round_currency(regular_hours)),
        "ot_hours": str(round_currency(ot_hours)),
        "hourly_rate": str(hourly_rate),
        "ot_multiplier": str(ot_multiplier),
        "regular_amount": str(regular_amount),
        "ot_amount": str(ot_amount),
        "total_amount": str(total_amount),
    })


# ============================================================================
# Feature #22c: Retroactive Pay
# ============================================================================


def calculate_retro_pay(conn, args):
    """Calculate retroactive pay for an employee.

    Compares the current salary assignment rate vs the previous rate,
    and for each past period affected, computes the difference.

    Required: --employee-id
    Optional: --from-date, --to-date (defaults to entire history)

    Returns: {employee_id, periods_affected, total_retro_amount, details}
    """
    if not args.employee_id:
        err("--employee-id is required")

    employee_id = args.employee_id.strip()

    # Validate employee
    emp_t = Table("employee")
    emp_q = Q.from_(emp_t).select(emp_t.star).where(emp_t.id == P())
    emp_row = conn.execute(emp_q.get_sql(), (employee_id,)).fetchone()
    if not emp_row:
        err(f"Employee {employee_id} not found")

    # Get all salary assignments ordered by effective_from
    assignments = conn.execute(
        """SELECT * FROM salary_assignment
           WHERE employee_id = ?
           ORDER BY effective_from ASC""",
        (employee_id,),
    ).fetchall()
    assignments = [row_to_dict(a) for a in assignments]

    if len(assignments) < 2:
        err("Need at least 2 salary assignments to calculate retroactive pay. "
            "No previous rate to compare against.")

    # Current assignment is the last one
    current = assignments[-1]
    previous = assignments[-2]

    current_rate = to_decimal(current["base_amount"])
    old_rate = to_decimal(previous["base_amount"])

    if current_rate <= old_rate:
        ok({
            "employee_id": employee_id,
            "periods_affected": 0,
            "total_retro_amount": "0.00",
            "details": [],
            "message": "Current rate is not higher than previous rate. No retro pay needed.",
        })
        return

    # Determine the period range for retroactive calculation
    # The retro period is from the current assignment's effective_from
    # back to the previous assignment's effective_from
    retro_start = previous["effective_from"]
    retro_end = current["effective_from"]

    # Apply user-supplied filters if provided
    if args.from_date:
        if args.from_date > retro_start:
            retro_start = args.from_date
    if args.to_date:
        if args.to_date < retro_end:
            retro_end = args.to_date

    # Find salary slips in the affected period for this employee
    slips = conn.execute(
        """SELECT id, period_start, period_end, gross_pay
           FROM salary_slip
           WHERE employee_id = ?
             AND period_start >= ?
             AND period_end <= ?
             AND status != 'cancelled'
           ORDER BY period_start""",
        (employee_id, retro_start, retro_end),
    ).fetchall()

    details = []
    total_retro = Decimal("0")
    now = datetime.now(timezone.utc).isoformat()

    rate_diff = current_rate - old_rate

    if slips:
        for slip in slips:
            s = row_to_dict(slip)
            # The difference per period is simply rate_diff (base monthly difference)
            adjustment = round_currency(rate_diff)
            total_retro += adjustment

            # Record the adjustment
            adj_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO retro_pay_adjustment
                   (id, employee_id, period_from, period_to, old_rate, new_rate,
                    adjustment_amount, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
                (adj_id, employee_id, s["period_start"], s["period_end"],
                 str(old_rate), str(current_rate), str(adjustment), now, now)
            )

            details.append({
                "period_from": s["period_start"],
                "period_to": s["period_end"],
                "old_rate": str(old_rate),
                "new_rate": str(current_rate),
                "adjustment_amount": str(adjustment),
            })
    else:
        # No slips found, calculate based on monthly periods
        start_dt = datetime.strptime(retro_start, "%Y-%m-%d")
        end_dt = datetime.strptime(retro_end, "%Y-%m-%d")

        current_dt = start_dt
        while current_dt < end_dt:
            period_from = current_dt.strftime("%Y-%m-%d")
            # Approximate month: advance by 30 days
            next_dt = current_dt + timedelta(days=30)
            if next_dt > end_dt:
                next_dt = end_dt
            period_to = next_dt.strftime("%Y-%m-%d")

            adjustment = round_currency(rate_diff)
            total_retro += adjustment

            adj_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO retro_pay_adjustment
                   (id, employee_id, period_from, period_to, old_rate, new_rate,
                    adjustment_amount, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
                (adj_id, employee_id, period_from, period_to,
                 str(old_rate), str(current_rate), str(adjustment), now, now)
            )

            details.append({
                "period_from": period_from,
                "period_to": period_to,
                "old_rate": str(old_rate),
                "new_rate": str(current_rate),
                "adjustment_amount": str(adjustment),
            })
            current_dt = next_dt

    conn.commit()

    ok({
        "employee_id": employee_id,
        "periods_affected": len(details),
        "total_retro_amount": str(round_currency(total_retro)),
        "details": details,
    })


# ============================================================================
# Feature #22e: NACHA / ACH File Generation (Sprint 7)
# ============================================================================


def add_employee_bank_account(conn, args):
    """Add an employee bank account for ACH/direct deposit.

    Required: --employee-id, --bank-name, --routing-number, --account-number
    Optional: --account-type (checking|savings, default checking)
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.bank_name:
        err("--bank-name is required")
    if not args.routing_number:
        err("--routing-number is required")
    if not args.account_number:
        err("--account-number is required")

    # Validate employee
    emp_t = Table("employee")
    eq = Q.from_(emp_t).select(emp_t.id).where(emp_t.id == P())
    if not conn.execute(eq.get_sql(), (args.employee_id,)).fetchone():
        err(f"Employee {args.employee_id} not found")

    # Validate routing number: 9 digits
    routing = args.routing_number.strip()
    if not routing.isdigit() or len(routing) != 9:
        err("Routing number must be exactly 9 digits")

    account_number = args.account_number.strip()
    if not account_number.isdigit() or len(account_number) < 4 or len(account_number) > 17:
        err("Account number must be 4-17 digits")

    account_type = (args.account_type or "checking").strip().lower()
    if account_type not in ("checking", "savings"):
        err(f"Invalid account type '{account_type}'. Valid: checking, savings")

    acct_id = str(uuid.uuid4())

    sql, _ = insert_row("employee_bank_account", {
        "id": P(), "employee_id": P(), "bank_name": P(),
        "routing_number": P(), "account_number": P(),
        "account_type": P(), "is_primary": P(),
        "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (
        acct_id, args.employee_id, args.bank_name.strip(),
        routing, account_number, account_type, 1,
        _now_iso(), _now_iso(),
    ))

    audit(conn, "erpclaw-payroll", "add-employee-bank-account",
          "employee_bank_account", acct_id,
          new_values={"employee_id": args.employee_id, "bank_name": args.bank_name})
    conn.commit()

    ok({
        "employee_bank_account_id": acct_id,
        "employee_id": args.employee_id,
        "bank_name": args.bank_name.strip(),
        "account_type": account_type,
        "message": "Employee bank account added",
    })


def list_employee_bank_accounts(conn, args):
    """List employee bank accounts.

    Required: --employee-id
    """
    if not args.employee_id:
        err("--employee-id is required")

    eba_t = Table("employee_bank_account")
    q = (Q.from_(eba_t).select(eba_t.star)
         .where(eba_t.employee_id == P())
         .orderby(eba_t.created_at))
    rows = conn.execute(q.get_sql(), (args.employee_id,)).fetchall()

    # Mask account numbers for security
    accounts = []
    for r in rows:
        d = row_to_dict(r)
        acct_num = d.get("account_number", "")
        if len(acct_num) > 4:
            d["account_number_masked"] = "****" + acct_num[-4:]
        else:
            d["account_number_masked"] = "****"
        accounts.append(d)

    ok({"accounts": accounts, "count": len(accounts)})


def generate_nacha_file(conn, args):
    """Generate a NACHA/ACH file from a submitted payroll run.

    Required: --payroll-run-id

    Returns: {file_content, entry_count, total_amount}
    """
    if not args.payroll_run_id:
        err("--payroll-run-id is required")

    # Fetch payroll run
    pr_t = Table("payroll_run")
    prq = Q.from_(pr_t).select(pr_t.star).where(pr_t.id == P())
    run = conn.execute(prq.get_sql(), (args.payroll_run_id,)).fetchone()
    if not run:
        err(f"Payroll run {args.payroll_run_id} not found")
    run = row_to_dict(run)
    if run["status"] not in ("submitted", "paid"):
        err(f"Payroll run must be 'submitted' or 'paid', got '{run['status']}'")

    company_id = run["company_id"]

    # Get company info
    co_t = Table("company")
    co_q = Q.from_(co_t).select(co_t.star).where(co_t.id == P())
    co_row = conn.execute(co_q.get_sql(), (company_id,)).fetchone()
    co = row_to_dict(co_row) if co_row else {}
    company_name = co.get("name", "COMPANY")

    # Get salary slips for this run
    ss_t = Table("salary_slip")
    ssq = (Q.from_(ss_t).select(ss_t.star)
           .where(ss_t.payroll_run_id == P())
           .where(ss_t.status != ValueWrapper("cancelled")))
    slips = conn.execute(ssq.get_sql(), (args.payroll_run_id,)).fetchall()
    if not slips:
        err("No salary slips found for this payroll run")

    # Get employee bank accounts
    eba_t = Table("employee_bank_account")
    entries = []
    total_amount = Decimal("0")

    for slip in slips:
        slip_d = row_to_dict(slip)
        net_pay = to_decimal(slip_d["net_pay"])
        if net_pay <= 0:
            continue

        baq = (Q.from_(eba_t).select(eba_t.star)
               .where(eba_t.employee_id == P())
               .where(eba_t.is_primary == 1)
               .limit(1))
        bank_acct = conn.execute(baq.get_sql(), (slip_d["employee_id"],)).fetchone()
        if not bank_acct:
            continue

        ba = row_to_dict(bank_acct)
        entries.append({
            "employee_id": slip_d["employee_id"],
            "routing_number": ba["routing_number"],
            "account_number": ba["account_number"],
            "account_type": ba["account_type"],
            "amount": net_pay,
        })
        total_amount += net_pay

    if not entries:
        err("No employees with bank accounts found for this payroll run")

    # Build NACHA fixed-width file
    now = datetime.now(timezone.utc)
    file_creation_date = now.strftime("%y%m%d")
    file_creation_time = now.strftime("%H%M")
    effective_date = run["period_end"].replace("-", "")[2:]  # YYMMDD

    lines = []

    # Record Type 1: File Header
    origin_id = "1" + (co.get("tax_id") or "000000000").ljust(9, "0")[:9]
    dest_id = " " + entries[0]["routing_number"]
    file_header = (
        "1" + "01" + dest_id.ljust(10) + origin_id.ljust(10)
        + file_creation_date + file_creation_time + "A" + "094" + "10" + "1"
        + "DEST BANK".ljust(23) + company_name[:23].ljust(23) + "".ljust(8)
    )
    lines.append(file_header)

    # Record Type 5: Batch Header
    batch_header = (
        "5" + "200" + company_name[:16].ljust(16) + "".ljust(20)
        + origin_id[:10].ljust(10) + "PPD" + "PAYROLL".ljust(10)
        + "".ljust(6) + effective_date + "".ljust(3) + "1"
        + entries[0]["routing_number"][:8] + "0000001"
    )
    lines.append(batch_header)

    # Record Type 6: Entry Detail records
    entry_hash = 0
    for i, entry in enumerate(entries, start=1):
        txn_code = "22" if entry["account_type"] == "checking" else "32"
        amount_cents = int(entry["amount"] * 100)
        routing = entry["routing_number"]
        check_digit = routing[8] if len(routing) > 8 else "0"
        rdfi = routing[:8]
        entry_hash += int(rdfi)

        detail = (
            "6" + txn_code + rdfi + check_digit
            + entry["account_number"][:17].ljust(17)
            + str(amount_cents).rjust(10, "0")
            + entry["employee_id"][:15].ljust(15)
            + "".ljust(22) + "  " + "0"
            + entries[0]["routing_number"][:8]
            + str(i).rjust(7, "0")
        )
        lines.append(detail)

    # Record Type 8: Batch Control
    entry_hash_mod = entry_hash % 10000000000
    total_cents = int(total_amount * 100)
    batch_control = (
        "8" + "200" + str(len(entries)).rjust(6, "0")
        + str(entry_hash_mod).rjust(10, "0")
        + str(total_cents).rjust(12, "0") + "0".rjust(12, "0")
        + origin_id[:10].ljust(10) + "".ljust(19) + "".ljust(6)
        + entries[0]["routing_number"][:8] + "0000001"
    )
    lines.append(batch_control)

    # Record Type 9: File Control
    block_count = (len(lines) + 1 + 9) // 10
    file_control = (
        "9" + "000001" + str(block_count).rjust(6, "0")
        + str(len(entries)).rjust(8, "0")
        + str(entry_hash_mod).rjust(10, "0")
        + str(total_cents).rjust(12, "0") + "0".rjust(12, "0")
        + "".ljust(39)
    )
    lines.append(file_control)

    file_content = "\n".join(lines)

    ok({
        "file_content": file_content,
        "entry_count": len(entries),
        "total_amount": str(round_currency(total_amount)),
        "payroll_run_id": args.payroll_run_id,
    })


ACTIONS = {
    # --- Part 1: Setup & Configuration (actions 1-7, 14-16, 18) ---
    "add-salary-component": add_salary_component,
    "list-salary-components": list_salary_components,
    "add-salary-structure": add_salary_structure,
    "get-salary-structure": get_salary_structure,
    "list-salary-structures": list_salary_structures,
    "add-salary-assignment": add_salary_assignment,
    "list-salary-assignments": list_salary_assignments,
    "add-income-tax-slab": add_income_tax_slab,
    "update-fica-config": update_fica_config,
    "update-futa-suta-config": update_futa_suta_config,
    "status": status_action,

    # --- Part 2: Core Payroll Processing (actions 8-13, 17) ---
    "create-payroll-run": create_payroll_run,
    "generate-salary-slips": generate_salary_slips,
    "get-salary-slip": get_salary_slip,
    "list-salary-slips": list_salary_slips,
    "submit-payroll-run": submit_payroll_run,
    "cancel-payroll-run": cancel_payroll_run,
    "generate-w2-data": generate_w2_data,

    # --- Part 3: Wage Garnishment ---
    "add-garnishment": add_garnishment,
    "update-garnishment": update_garnishment,
    "list-garnishments": list_garnishments,
    "get-garnishment": get_garnishment,

    # --- Part 4: Sprint 6 — Advanced Payroll ---
    "add-state-tax-slab": add_state_tax_slab,
    "update-employee-state-config": update_employee_state_config,
    "add-overtime-policy": add_overtime_policy,
    "calculate-overtime": calculate_overtime,
    "calculate-retro-pay": calculate_retro_pay,

    # --- Part 5: Sprint 7 — NACHA / ACH ---
    "add-employee-bank-account": add_employee_bank_account,
    "list-employee-bank-accounts": list_employee_bank_accounts,
    "generate-nacha-file": generate_nacha_file,
}


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Parse command-line arguments and dispatch to the appropriate action."""
    parser = SafeArgumentParser(
        description="ERPClaw Payroll Skill -- US payroll processing, "
                    "salary structures, tax withholding, FICA, and W-2 generation."
    )
    parser.add_argument(
        "--action", required=True, choices=sorted(ACTIONS.keys()),
        help="The payroll action to execute.",
    )
    parser.add_argument("--db-path", default=None,
                        help="Override database path (default: ~/.openclaw/erpclaw/data.sqlite)")

    # ----- Entity IDs -----
    parser.add_argument("--company-id",
                        help="Company UUID")
    parser.add_argument("--employee-id",
                        help="Employee UUID")
    parser.add_argument("--department-id",
                        help="Department UUID (filter for payroll run)")
    parser.add_argument("--salary-component-id",
                        help="Salary component UUID")
    parser.add_argument("--salary-structure-id",
                        help="Salary structure UUID")
    parser.add_argument("--salary-assignment-id",
                        help="Salary assignment UUID")
    parser.add_argument("--salary-slip-id",
                        help="Salary slip UUID")
    parser.add_argument("--payroll-run-id",
                        help="Payroll run UUID")
    parser.add_argument("--cost-center-id",
                        help="Cost center UUID (for GL posting)")

    # ----- Salary Component Fields -----
    parser.add_argument("--name",
                        help="Component/structure/slab name")
    parser.add_argument("--description",
                        help="Description text")
    parser.add_argument("--component-type",
                        help="Component type: earning, deduction, employer_contribution")
    parser.add_argument("--is-tax-applicable",
                        help="1 = taxable, 0 = not taxable")
    parser.add_argument("--is-statutory",
                        help="1 = statutory (e.g., FICA), 0 = voluntary")
    parser.add_argument("--is-pre-tax",
                        help="1 = pre-tax deduction (e.g., 401k), 0 = post-tax")
    parser.add_argument("--variable-based-on-taxable-salary",
                        help="1 = calculated from taxable salary, 0 = fixed")
    parser.add_argument("--depends-on-payment-days",
                        help="1 = prorate by payment days, 0 = always full amount")
    parser.add_argument("--gl-account-id",
                        help="GL account for this component's journal entries")

    # ----- Salary Structure Fields -----
    parser.add_argument("--payroll-frequency",
                        help="Payroll frequency: monthly, biweekly, weekly")
    parser.add_argument("--components",
                        help="JSON array of component definitions for salary structure. "
                             "Each: {salary_component_id, amount?, percentage?, "
                             "base_component_id?, sort_order?}")

    # ----- Salary Assignment Fields -----
    parser.add_argument("--base-amount",
                        help="Base salary amount as TEXT Decimal (e.g., '5000.00')")
    parser.add_argument("--effective-from",
                        help="Assignment effective start date (YYYY-MM-DD)")
    parser.add_argument("--effective-to",
                        help="Assignment effective end date (YYYY-MM-DD), optional")

    # ----- Payroll Run Fields -----
    parser.add_argument("--period-start",
                        help="Pay period start date (YYYY-MM-DD)")
    parser.add_argument("--period-end",
                        help="Pay period end date (YYYY-MM-DD)")

    # ----- Tax Configuration Fields -----
    parser.add_argument("--tax-jurisdiction",
                        help="Tax jurisdiction: federal or state")
    parser.add_argument("--filing-status",
                        help="Filing status: single, married_jointly, "
                             "married_separately, head_of_household")
    parser.add_argument("--state-code",
                        help="US state code (e.g., 'CA', 'NY') for state tax slabs")
    parser.add_argument("--standard-deduction",
                        help="Standard deduction amount as TEXT Decimal")
    parser.add_argument("--rates",
                        help="JSON array of tax bracket rates. "
                             "Each: {from_amount, to_amount, rate}")
    parser.add_argument("--tax-year",
                        help="Tax year (integer, e.g., 2026)")
    parser.add_argument("--ss-wage-base",
                        help="Social Security wage base (e.g., '168600')")
    parser.add_argument("--ss-employee-rate",
                        help="SS employee rate percentage (e.g., '6.2')")
    parser.add_argument("--ss-employer-rate",
                        help="SS employer rate percentage (e.g., '6.2')")
    parser.add_argument("--medicare-employee-rate",
                        help="Medicare employee rate percentage (e.g., '1.45')")
    parser.add_argument("--medicare-employer-rate",
                        help="Medicare employer rate percentage (e.g., '1.45')")
    parser.add_argument("--additional-medicare-threshold",
                        help="Additional Medicare threshold (e.g., '200000')")
    parser.add_argument("--additional-medicare-rate",
                        help="Additional Medicare rate percentage (e.g., '0.9')")
    parser.add_argument("--wage-base",
                        help="FUTA/SUTA wage base (e.g., '7000')")
    parser.add_argument("--rate",
                        help="FUTA/SUTA tax rate percentage")
    parser.add_argument("--employer-rate-override",
                        help="Employer rate override for FUTA/SUTA")

    # ----- Wage Garnishment Fields -----
    parser.add_argument("--garnishment-id",
                        help="Wage garnishment UUID")
    parser.add_argument("--order-number",
                        help="Court order or garnishment order number")
    parser.add_argument("--creditor-name",
                        help="Name of the creditor or agency")
    parser.add_argument("--garnishment-type",
                        help="Type: child_support, tax_levy, student_loan, creditor")
    parser.add_argument("--amount-or-percentage",
                        help="Amount or percentage to garnish")
    parser.add_argument("--is-percentage", action="store_true", default=False,
                        help="If set, amount-or-percentage is a percentage")
    parser.add_argument("--total-owed",
                        help="Total amount owed (for auto-completion tracking)")
    parser.add_argument("--start-date",
                        help="Garnishment effective start date")
    parser.add_argument("--end-date",
                        help="Garnishment effective end date")

    # ----- Multi-State Payroll Fields (Feature #22a) -----
    parser.add_argument("--bracket-start",
                        help="State tax bracket lower bound (e.g., '0')")
    parser.add_argument("--bracket-end",
                        help="State tax bracket upper bound (e.g., '50000')")
    parser.add_argument("--work-state",
                        help="Employee work state code (e.g., 'CA')")
    parser.add_argument("--residence-state",
                        help="Employee residence state code (e.g., 'CA')")

    # ----- Overtime Fields (Feature #22b) -----
    parser.add_argument("--weekly-threshold",
                        help="Weekly hours threshold for overtime (default: '40')")
    parser.add_argument("--daily-threshold",
                        help="Daily hours threshold for overtime")
    parser.add_argument("--ot-multiplier",
                        help="Overtime pay multiplier (default: '1.5')")
    parser.add_argument("--double-ot-multiplier",
                        help="Double overtime pay multiplier (default: '2.0')")
    parser.add_argument("--hourly-rate",
                        help="Hourly rate for overtime calculation")

    # ----- Supplemental Wage Fields (Feature #22d) -----
    parser.add_argument("--is-supplemental",
                        help="1 = supplemental wage component, 0 = regular")

    # ----- NACHA / ACH Fields (Feature #22e) -----
    parser.add_argument("--bank-name",
                        help="Bank name for employee bank account")
    parser.add_argument("--routing-number",
                        help="ABA routing number (9 digits)")
    parser.add_argument("--account-number",
                        help="Bank account number (4-17 digits)")
    parser.add_argument("--account-type",
                        help="Account type: checking or savings")

    # ----- Filters / Pagination -----
    parser.add_argument("--status",
                        help="Filter by status (draft, submitted, paid, cancelled)")
    parser.add_argument("--from-date",
                        help="Filter: start date (YYYY-MM-DD)")
    parser.add_argument("--to-date",
                        help="Filter: end date (YYYY-MM-DD)")
    parser.add_argument("--limit", default="20",
                        help="Maximum number of results (default: 20)")
    parser.add_argument("--offset", default="0",
                        help="Pagination offset (default: 0)")
    parser.add_argument("--search",
                        help="Free-text search filter")

    args, unknown = parser.parse_known_args()
    check_unknown_args(parser, unknown)
    check_input_lengths(args)

    # --- Database connection ---
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
        sys.stderr.write(f"[erpclaw-payroll] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
