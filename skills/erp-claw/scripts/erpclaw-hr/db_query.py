#!/usr/bin/env python3
"""ERPClaw HR Skill -- db_query.py

Employee management, org structure, leave management, attendance,
expense claims, and employee lifecycle tracking.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal, InvalidOperation

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
    from erpclaw_lib.query import (
        Q, P, Table, Field, fn, Case, Order, Criterion, Not, NULL,
        DecimalSum, DecimalAbs, insert_row, update_row, dynamic_update,
    )
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw-setup first: clawhub install erpclaw-setup", "suggestion": "clawhub install erpclaw-setup"}))
    sys.exit(1)

REQUIRED_TABLES = ["company"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_EMPLOYEE_STATUSES = ("active", "inactive", "suspended", "left")
VALID_EMPLOYMENT_TYPES = ("full_time", "part_time", "contract", "intern")
VALID_GENDERS = ("male", "female", "other", "prefer_not_to_say")
VALID_LEAVE_STATUSES = ("draft", "approved", "rejected", "cancelled")
VALID_ATTENDANCE_STATUSES = (
    "present", "absent", "half_day", "on_leave", "work_from_home",
)
VALID_ATTENDANCE_SOURCES = ("manual", "biometric", "app")
VALID_EXPENSE_STATUSES = (
    "draft", "submitted", "approved", "rejected", "paid", "cancelled",
)
VALID_EXPENSE_TYPES = ("travel", "meals", "accommodation", "supplies", "other")
VALID_LIFECYCLE_EVENTS = (
    "hiring", "confirmation", "promotion", "transfer",
    "separation", "resignation", "retirement",
)
VALID_FILING_STATUSES = (
    "single", "married_jointly", "married_separately", "head_of_household",
)


def _parse_json_arg(value, name):
    """Parse a JSON string argument, returning the parsed value or erroring."""
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        err(f"Invalid JSON for --{name}: {value}")


def _get_fiscal_year(conn, target_date: str) -> str | None:
    """Return the fiscal year name for a date, or None if not found."""
    t = Table("fiscal_year")
    q = (Q.from_(t)
         .select(t.name)
         .where(t.start_date <= P())
         .where(t.end_date >= P())
         .where(t.is_closed == 0))
    fy = conn.execute(q.get_sql(), (target_date, target_date)).fetchone()
    return fy["name"] if fy else None


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
    q = (Q.from_(t)
         .select(t.id)
         .where(t.company_id == P())
         .where(t.is_group == 0)
         .limit(1))
    cc = conn.execute(q.get_sql(), (company_id,)).fetchone()
    return cc["id"] if cc else None


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


def _validate_department_exists(conn, department_id: str):
    """Validate that a department exists and return the row, or error."""
    t = Table("department")
    q = Q.from_(t).select(t.star).where((t.id == P()) | (t.name == P()))
    dept = conn.execute(q.get_sql(), (department_id, department_id)).fetchone()
    if not dept:
        err(f"Department {department_id} not found")
    return dept


def _validate_designation_exists(conn, designation_id: str):
    """Validate that a designation exists and return the row, or error."""
    t = Table("designation")
    q = Q.from_(t).select(t.star).where((t.id == P()) | (t.name == P()))
    des = conn.execute(q.get_sql(), (designation_id, designation_id)).fetchone()
    if not des:
        err(f"Designation {designation_id} not found")
    return des


def _validate_leave_type_exists(conn, leave_type_id: str):
    """Validate that a leave type exists and return the row, or error."""
    t = Table("leave_type")
    q = Q.from_(t).select(t.star).where(t.id == P())
    lt = conn.execute(q.get_sql(), (leave_type_id,)).fetchone()
    if not lt:
        err(f"Leave type {leave_type_id} not found")
    return lt


def _validate_employee_grade_exists(conn, grade_id: str):
    """Validate that an employee grade exists and return the row, or error."""
    t = Table("employee_grade")
    q = Q.from_(t).select(t.star).where(t.id == P())
    grade = conn.execute(q.get_sql(), (grade_id,)).fetchone()
    if not grade:
        err(f"Employee grade {grade_id} not found")
    return grade


def _validate_holiday_list_exists(conn, holiday_list_id: str):
    """Validate that a holiday list exists and return the row, or error."""
    t = Table("holiday_list")
    q = Q.from_(t).select(t.star).where(t.id == P())
    hl = conn.execute(q.get_sql(), (holiday_list_id,)).fetchone()
    if not hl:
        err(f"Holiday list {holiday_list_id} not found")
    return hl


def _count_business_days(from_date_str: str, to_date_str: str,
                         half_day: bool = False,
                         holidays: list[str] | None = None) -> Decimal:
    """Count business days between two dates (inclusive), excluding weekends
    and any holidays in the provided list.

    If half_day is True, subtract 0.5 from the total.
    Returns a Decimal representing the total leave days.
    """
    try:
        start = date.fromisoformat(from_date_str)
        end = date.fromisoformat(to_date_str)
    except (ValueError, TypeError):
        err(f"Invalid date format: from={from_date_str}, to={to_date_str}")

    if start > end:
        err(f"from-date ({from_date_str}) must be on or before to-date ({to_date_str})")

    holiday_set = set(holidays) if holidays else set()
    count = 0
    current = start
    while current <= end:
        # Weekdays: Monday=0 .. Friday=4
        if current.weekday() < 5:
            # Not a weekend -- check if it is a public holiday
            if current.isoformat() not in holiday_set:
                count += 1
        current += timedelta(days=1)

    total = Decimal(str(count))
    if half_day and total > Decimal("0"):
        total -= Decimal("0.5")

    return total


def _get_employee_holidays(conn, employee_id: str,
                           from_date: str, to_date: str) -> list[str]:
    """Fetch holiday dates applicable to an employee between two dates.

    Checks the employee's assigned holiday_list_id first, then falls back
    to the company's holiday list if available.
    """
    et = Table("employee")
    q = Q.from_(et).select(et.holiday_list_id, et.company_id).where(et.id == P())
    emp = conn.execute(q.get_sql(), (employee_id,)).fetchone()
    if not emp:
        return []

    holiday_list_id = emp["holiday_list_id"]

    # If employee has no explicit holiday list, try company default
    if not holiday_list_id and emp["company_id"]:
        ht = Table("holiday_list")
        q = (Q.from_(ht)
             .select(ht.id)
             .where(ht.company_id == P())
             .where(ht.from_date <= P())
             .where(ht.to_date >= P())
             .orderby(ht.from_date, order=Order.desc)
             .limit(1))
        hl = conn.execute(q.get_sql(), (emp["company_id"], to_date, from_date)).fetchone()
        if hl:
            holiday_list_id = hl["id"]

    if not holiday_list_id:
        return []

    hol = Table("holiday")
    q = (Q.from_(hol)
         .select(hol.holiday_date)
         .where(hol.holiday_list_id == P())
         .where(hol.holiday_date >= P())
         .where(hol.holiday_date <= P()))
    rows = conn.execute(q.get_sql(), (holiday_list_id, from_date, to_date)).fetchall()
    return [r["holiday_date"] for r in rows]


def _now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# 1. add-employee
# ---------------------------------------------------------------------------

def add_employee(conn, args):
    """Create a new employee record.

    Required: --first-name, --date-of-joining, --company-id
    Optional: --last-name, --date-of-birth, --gender, --employment-type,
              --department-id, --designation-id, --employee-grade-id,
              --branch, --reporting-to, --company-email, --personal-email,
              --cell-phone, --emergency-contact (JSON), --bank-details (JSON),
              --federal-filing-status, --w4-allowances, --holiday-list-id,
              --payroll-cost-center-id
    """
    if not args.first_name:
        err("--first-name is required")
    if not args.date_of_joining:
        err("--date-of-joining is required")
    if not args.company_id:
        err("--company-id is required")

    # Validate company
    _validate_company_exists(conn, args.company_id)

    # Validate gender if provided
    if args.gender and args.gender not in VALID_GENDERS:
        err(f"Invalid gender '{args.gender}'. Valid: {VALID_GENDERS}")

    # Validate employment type if provided
    employment_type = args.employment_type or "full_time"
    if employment_type not in VALID_EMPLOYMENT_TYPES:
        err(f"Invalid employment type '{employment_type}'. Valid: {VALID_EMPLOYMENT_TYPES}")

    # Validate date format
    try:
        date.fromisoformat(args.date_of_joining)
    except (ValueError, TypeError):
        err(f"Invalid date-of-joining format: {args.date_of_joining}. Use YYYY-MM-DD")

    if args.date_of_birth:
        try:
            date.fromisoformat(args.date_of_birth)
        except (ValueError, TypeError):
            err(f"Invalid date-of-birth format: {args.date_of_birth}. Use YYYY-MM-DD")

    # Validate FK references
    if args.department_id:
        _validate_department_exists(conn, args.department_id)
    if args.designation_id:
        _validate_designation_exists(conn, args.designation_id)
    if args.employee_grade_id:
        _validate_employee_grade_exists(conn, args.employee_grade_id)
    if args.reporting_to:
        _validate_employee_exists(conn, args.reporting_to)
    if args.holiday_list_id:
        _validate_holiday_list_exists(conn, args.holiday_list_id)
    if args.payroll_cost_center_id:
        cct = Table("cost_center")
        q = Q.from_(cct).select(cct.id).where(cct.id == P())
        cc = conn.execute(q.get_sql(), (args.payroll_cost_center_id,)).fetchone()
        if not cc:
            err(f"Cost center {args.payroll_cost_center_id} not found")

    # Validate federal filing status if provided
    if args.federal_filing_status:
        if args.federal_filing_status not in VALID_FILING_STATUSES:
            err(
                f"Invalid federal filing status '{args.federal_filing_status}'. "
                f"Valid: {VALID_FILING_STATUSES}"
            )

    # Validate email format if provided
    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    for field, label in [("company_email", "company-email"), ("personal_email", "personal-email")]:
        val = getattr(args, field, None)
        if val and not _EMAIL_RE.match(val):
            err(f"Invalid email format for --{label}: '{val}'")

    # Compute full_name
    first_name = args.first_name.strip()
    last_name = (args.last_name or "").strip()
    full_name = f"{first_name} {last_name}".strip()

    # Parse JSON fields
    emergency_contact = _parse_json_arg(args.emergency_contact, "emergency-contact")
    bank_details = _parse_json_arg(args.bank_details, "bank-details")

    # Generate naming series
    employee_id = str(uuid.uuid4())
    naming_series = get_next_name(conn, "employee", company_id=args.company_id)

    now = _now_iso()

    sql, _cols = insert_row("employee", {
        "id": P(), "naming_series": P(), "first_name": P(), "last_name": P(),
        "full_name": P(), "date_of_birth": P(), "gender": P(),
        "date_of_joining": P(), "employment_type": P(), "status": P(),
        "department_id": P(), "designation_id": P(), "employee_grade_id": P(),
        "branch": P(), "reporting_to": P(), "company_id": P(),
        "company_email": P(), "personal_email": P(), "cell_phone": P(),
        "emergency_contact": P(), "bank_details": P(),
        "federal_filing_status": P(), "w4_allowances": P(),
        "holiday_list_id": P(), "payroll_cost_center_id": P(),
        "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (
        employee_id, naming_series, first_name, last_name, full_name,
        args.date_of_birth, args.gender, args.date_of_joining, employment_type,
        "active",
        args.department_id, args.designation_id, args.employee_grade_id,
        args.branch, args.reporting_to, args.company_id,
        args.company_email, args.personal_email,
        args.cell_phone,
        json.dumps(emergency_contact) if emergency_contact else None,
        json.dumps(bank_details) if bank_details else None,
        args.federal_filing_status,
        int(args.w4_allowances) if args.w4_allowances else 0,
        args.holiday_list_id, args.payroll_cost_center_id,
        now, now,
    ))

    # Record lifecycle event: hiring
    sql, _cols = insert_row("employee_lifecycle_event", {
        "id": P(), "employee_id": P(), "event_type": P(), "event_date": P(),
        "details": P(), "new_values": P(), "created_at": P(),
    })
    conn.execute(sql, (
        str(uuid.uuid4()), employee_id, "hiring", args.date_of_joining,
        json.dumps({"action": "Employee created"}),
        json.dumps({
            "first_name": first_name,
            "last_name": last_name,
            "department_id": args.department_id,
            "designation_id": args.designation_id,
            "employment_type": employment_type,
            "company_id": args.company_id,
        }),
        now,
    ))

    audit(conn, "erpclaw-hr", "add-employee", "employee", employee_id,
           new_values={"naming_series": naming_series, "full_name": full_name},
           description=f"Created employee {full_name}")

    conn.commit()

    ok({
        "employee_id": employee_id,
        "naming_series": naming_series,
        "full_name": full_name,
        "message": f"Employee '{full_name}' created successfully",
    })


# ---------------------------------------------------------------------------
# 2. update-employee
# ---------------------------------------------------------------------------

def update_employee(conn, args):
    """Update an existing employee record.

    Required: --employee-id
    Optional: --first-name, --last-name, --date-of-birth, --gender,
              --date-of-joining, --date-of-exit, --employment-type, --status,
              --department-id, --designation-id, --employee-grade-id,
              --branch, --reporting-to, --company-email, --personal-email,
              --cell-phone, --emergency-contact (JSON), --bank-details (JSON),
              --federal-filing-status, --w4-allowances,
              --w4-additional-withholding, --state-filing-status,
              --state-withholding-allowances, --employee-401k-rate,
              --hsa-contribution, --is-exempt-from-fica,
              --salary-structure-id, --leave-policy-id, --shift-id,
              --holiday-list-id, --attendance-device-id,
              --payroll-cost-center-id
    """
    if not args.employee_id:
        err("--employee-id is required")

    emp = _validate_employee_exists(conn, args.employee_id)
    old_values = row_to_dict(emp)

    # Build dynamic UPDATE fields
    updates = {}

    # Name fields
    if args.first_name is not None:
        updates["first_name"] = args.first_name.strip()
    if args.last_name is not None:
        updates["last_name"] = args.last_name.strip()

    # Recompute full_name if name changed
    if "first_name" in updates or "last_name" in updates:
        fn = updates.get("first_name", old_values.get("first_name", ""))
        ln = updates.get("last_name", old_values.get("last_name", ""))
        updates["full_name"] = f"{fn} {ln}".strip()

    # Date fields
    if args.date_of_birth is not None:
        try:
            date.fromisoformat(args.date_of_birth)
        except (ValueError, TypeError):
            err(f"Invalid date-of-birth format: {args.date_of_birth}")
        updates["date_of_birth"] = args.date_of_birth

    if args.date_of_joining is not None:
        try:
            date.fromisoformat(args.date_of_joining)
        except (ValueError, TypeError):
            err(f"Invalid date-of-joining format: {args.date_of_joining}")
        updates["date_of_joining"] = args.date_of_joining

    if args.date_of_exit is not None:
        try:
            date.fromisoformat(args.date_of_exit)
        except (ValueError, TypeError):
            err(f"Invalid date-of-exit format: {args.date_of_exit}")
        updates["date_of_exit"] = args.date_of_exit

    # Gender
    if args.gender is not None:
        if args.gender not in VALID_GENDERS:
            err(f"Invalid gender '{args.gender}'. Valid: {VALID_GENDERS}")
        updates["gender"] = args.gender

    # Employment type
    if args.employment_type is not None:
        if args.employment_type not in VALID_EMPLOYMENT_TYPES:
            err(
                f"Invalid employment type '{args.employment_type}'. "
                f"Valid: {VALID_EMPLOYMENT_TYPES}"
            )
        updates["employment_type"] = args.employment_type

    # Status
    if args.status is not None:
        if args.status not in VALID_EMPLOYEE_STATUSES:
            err(
                f"Invalid employee status '{args.status}'. "
                f"Valid: {VALID_EMPLOYEE_STATUSES}"
            )
        updates["status"] = args.status

    # FK references with validation
    if args.department_id is not None:
        if args.department_id:
            _validate_department_exists(conn, args.department_id)
        updates["department_id"] = args.department_id or None

    if args.designation_id is not None:
        if args.designation_id:
            _validate_designation_exists(conn, args.designation_id)
        updates["designation_id"] = args.designation_id or None

    if args.employee_grade_id is not None:
        if args.employee_grade_id:
            _validate_employee_grade_exists(conn, args.employee_grade_id)
        updates["employee_grade_id"] = args.employee_grade_id or None

    if args.reporting_to is not None:
        if args.reporting_to:
            if args.reporting_to == args.employee_id:
                err("Employee cannot report to themselves")
            _validate_employee_exists(conn, args.reporting_to)
        updates["reporting_to"] = args.reporting_to or None

    if args.holiday_list_id is not None:
        if args.holiday_list_id:
            _validate_holiday_list_exists(conn, args.holiday_list_id)
        updates["holiday_list_id"] = args.holiday_list_id or None

    if args.payroll_cost_center_id is not None:
        if args.payroll_cost_center_id:
            cct = Table("cost_center")
            q = Q.from_(cct).select(cct.id).where(cct.id == P())
            cc = conn.execute(q.get_sql(), (args.payroll_cost_center_id,)).fetchone()
            if not cc:
                err(f"Cost center {args.payroll_cost_center_id} not found")
        updates["payroll_cost_center_id"] = args.payroll_cost_center_id or None

    # Simple text fields
    if args.branch is not None:
        updates["branch"] = args.branch or None
    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    if args.company_email is not None:
        if args.company_email and not _EMAIL_RE.match(args.company_email):
            err(f"Invalid email format for --company-email: '{args.company_email}'")
        updates["company_email"] = args.company_email or None
    if args.personal_email is not None:
        if args.personal_email and not _EMAIL_RE.match(args.personal_email):
            err(f"Invalid email format for --personal-email: '{args.personal_email}'")
        updates["personal_email"] = args.personal_email or None
    if args.cell_phone is not None:
        updates["cell_phone"] = args.cell_phone or None

    # JSON fields
    if args.emergency_contact is not None:
        ec = _parse_json_arg(args.emergency_contact, "emergency-contact")
        updates["emergency_contact"] = json.dumps(ec) if ec else None
    if args.bank_details is not None:
        bd = _parse_json_arg(args.bank_details, "bank-details")
        updates["bank_details"] = json.dumps(bd) if bd else None

    # Tax / payroll fields
    if args.federal_filing_status is not None:
        if args.federal_filing_status and args.federal_filing_status not in VALID_FILING_STATUSES:
            err(
                f"Invalid federal filing status '{args.federal_filing_status}'. "
                f"Valid: {VALID_FILING_STATUSES}"
            )
        updates["federal_filing_status"] = args.federal_filing_status or None

    if args.w4_allowances is not None:
        updates["w4_allowances"] = int(args.w4_allowances)
    if args.w4_additional_withholding is not None:
        updates["w4_additional_withholding"] = args.w4_additional_withholding
    if args.state_filing_status is not None:
        updates["state_filing_status"] = args.state_filing_status or None
    if args.state_withholding_allowances is not None:
        updates["state_withholding_allowances"] = int(args.state_withholding_allowances)
    if args.employee_401k_rate is not None:
        updates["employee_401k_rate"] = args.employee_401k_rate
    if args.hsa_contribution is not None:
        updates["hsa_contribution"] = args.hsa_contribution
    if args.is_exempt_from_fica is not None:
        updates["is_exempt_from_fica"] = int(args.is_exempt_from_fica)

    # Salary / leave / shift references
    if args.salary_structure_id is not None:
        updates["salary_structure_id"] = args.salary_structure_id or None
    if args.leave_policy_id is not None:
        updates["leave_policy_id"] = args.leave_policy_id or None
    if args.shift_id is not None:
        updates["shift_id"] = args.shift_id or None
    if args.attendance_device_id is not None:
        updates["attendance_device_id"] = args.attendance_device_id or None

    if not updates:
        err("No fields to update. Provide at least one optional flag.")

    updates["updated_at"] = _now_iso()
    sql, params = dynamic_update("employee", updates, where={"id": args.employee_id})
    conn.execute(sql, params)

    # Track changed values for audit
    changed = {k: v for k, v in updates.items() if k != "updated_at"}
    audit(conn, "erpclaw-hr", "update-employee", "employee", args.employee_id,
           old_values={k: old_values.get(k) for k in changed},
           new_values=changed,
           description=f"Updated employee {args.employee_id}")

    conn.commit()

    ok({
        "employee_id": args.employee_id,
        "updated_fields": list(changed.keys()),
        "message": f"Employee {args.employee_id} updated successfully",
    })


# ---------------------------------------------------------------------------
# 3. get-employee
# ---------------------------------------------------------------------------

def get_employee(conn, args):
    """Retrieve detailed employee information.

    Required: --employee-id
    Returns: employee row with department name, designation name,
             leave balance summary, and attendance summary.
    """
    if not args.employee_id:
        err("--employee-id is required")

    # Fetch employee with joined department and designation names
    e = Table("employee").as_("e")
    d = Table("department").as_("d")
    des = Table("designation").as_("des")
    eg = Table("employee_grade").as_("eg")
    hl = Table("holiday_list").as_("hl")
    q = (Q.from_(e)
         .select(e.star,
                 d.name.as_("department_name"),
                 des.name.as_("designation_name"),
                 eg.name.as_("employee_grade_name"),
                 hl.name.as_("holiday_list_name"))
         .left_join(d).on(d.id == e.department_id)
         .left_join(des).on(des.id == e.designation_id)
         .left_join(eg).on(eg.id == e.employee_grade_id)
         .left_join(hl).on(hl.id == e.holiday_list_id)
         .where(e.id == P()))
    row = conn.execute(q.get_sql(), (args.employee_id,)).fetchone()

    if not row:
        err(f"Employee {args.employee_id} not found")

    employee = row_to_dict(row)

    # Parse JSON fields for readability
    if employee.get("emergency_contact"):
        try:
            employee["emergency_contact"] = json.loads(employee["emergency_contact"])
        except (json.JSONDecodeError, TypeError):
            pass
    if employee.get("bank_details"):
        try:
            employee["bank_details"] = json.loads(employee["bank_details"])
        except (json.JSONDecodeError, TypeError):
            pass

    # Leave balance summary: all allocations for current fiscal year
    today_str = date.today().isoformat()
    fiscal_year = _get_fiscal_year(conn, today_str)

    leave_balances = []
    if fiscal_year:
        la = Table("leave_allocation").as_("la")
        lt = Table("leave_type").as_("lt")
        q = (Q.from_(la)
             .join(lt).on(lt.id == la.leave_type_id)
             .select(la.leave_type_id, lt.name.as_("leave_type_name"),
                     la.total_leaves, la.used_leaves, la.remaining_leaves,
                     la.fiscal_year)
             .where(la.employee_id == P())
             .where(la.fiscal_year == P())
             .orderby(lt.name))
        lb_rows = conn.execute(q.get_sql(), (args.employee_id, fiscal_year)).fetchall()
        leave_balances = [row_to_dict(r) for r in lb_rows]

    employee["leave_balances"] = leave_balances

    # Attendance summary for current month
    month_start = date.today().replace(day=1).isoformat()
    month_end = date.today().isoformat()

    at = Table("attendance")
    q = (Q.from_(at)
         .select(
             fn.Count("*").as_("total_records"),
             fn.Sum(Case().when(at.status == "present", 1).else_(0)).as_("present_days"),
             fn.Sum(Case().when(at.status == "absent", 1).else_(0)).as_("absent_days"),
             fn.Sum(Case().when(at.status == "half_day", 1).else_(0)).as_("half_days"),
             fn.Sum(Case().when(at.status == "on_leave", 1).else_(0)).as_("on_leave_days"),
             fn.Sum(Case().when(at.status == "work_from_home", 1).else_(0)).as_("wfh_days"),
             fn.Sum(Case().when(at.late_entry == 1, 1).else_(0)).as_("late_entries"),
             fn.Sum(Case().when(at.early_exit == 1, 1).else_(0)).as_("early_exits"),
         )
         .where(at.employee_id == P())
         .where(at.attendance_date >= P())
         .where(at.attendance_date <= P()))
    att_summary = conn.execute(q.get_sql(), (args.employee_id, month_start, month_end)).fetchone()

    employee["attendance_summary"] = row_to_dict(att_summary) if att_summary else {}

    # Reporting chain: who this employee reports to
    if employee.get("reporting_to"):
        et2 = Table("employee")
        q = (Q.from_(et2)
             .select(et2.id, et2.full_name, et2.designation_id)
             .where(et2.id == P()))
        mgr = conn.execute(q.get_sql(), (employee["reporting_to"],)).fetchone()
        employee["reporting_to_name"] = mgr["full_name"] if mgr else None
    else:
        employee["reporting_to_name"] = None

    # Direct reports count
    et3 = Table("employee")
    q = (Q.from_(et3)
         .select(fn.Count("*"))
         .where(et3.reporting_to == P())
         .where(et3.status == "active"))
    direct_reports_count = conn.execute(q.get_sql(), (args.employee_id,)).fetchone()
    employee["direct_reports_count"] = direct_reports_count[0] if direct_reports_count else 0

    ok({"employee": employee})


# ---------------------------------------------------------------------------
# 4. list-employees
# ---------------------------------------------------------------------------

def list_employees(conn, args):
    """Query employees with filtering and pagination.

    Optional: --company-id, --department-id, --designation-id, --status,
              --employment-type, --search, --limit (20), --offset (0)
    """
    e = Table("employee").as_("e")
    d = Table("department").as_("d")
    des_t = Table("designation").as_("des")

    base = (Q.from_(e)
            .left_join(d).on(d.id == e.department_id)
            .left_join(des_t).on(des_t.id == e.designation_id))

    params = []
    crit = None

    def _and(c, new):
        return new if c is None else c & new

    if args.company_id:
        crit = _and(crit, e.company_id == P())
        params.append(args.company_id)
    if args.department_id:
        crit = _and(crit, e.department_id == P())
        params.append(args.department_id)
    if args.designation_id:
        crit = _and(crit, e.designation_id == P())
        params.append(args.designation_id)
    if args.status:
        if args.status not in VALID_EMPLOYEE_STATUSES:
            err(f"Invalid status '{args.status}'. Valid: {VALID_EMPLOYEE_STATUSES}")
        crit = _and(crit, e.status == P())
        params.append(args.status)
    if args.employment_type:
        if args.employment_type not in VALID_EMPLOYMENT_TYPES:
            err(
                f"Invalid employment type '{args.employment_type}'. "
                f"Valid: {VALID_EMPLOYMENT_TYPES}"
            )
        crit = _and(crit, e.employment_type == P())
        params.append(args.employment_type)
    if args.search:
        search_term = f"%{args.search}%"
        search_crit = (
            e.full_name.like(P()) | e.naming_series.like(P())
            | e.company_email.like(P()) | e.cell_phone.like(P())
        )
        crit = _and(crit, search_crit)
        params.extend([search_term, search_term, search_term, search_term])

    # Total count
    count_q = base.select(fn.Count("*"))
    if crit is not None:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (base
              .select(e.id, e.naming_series, e.full_name, e.date_of_joining,
                      e.employment_type, e.status, e.company_id, e.branch,
                      e.company_email, e.cell_phone,
                      d.name.as_("department_name"),
                      des_t.name.as_("designation_name"))
              .orderby(e.full_name)
              .limit(P()).offset(P()))
    if crit is not None:
        list_q = list_q.where(crit)
    list_params = params + [limit, offset]
    rows = conn.execute(list_q.get_sql(), list_params).fetchall()

    ok({
        "employees": [row_to_dict(r) for r in rows],
        "total_count": total_count,
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total_count,
    })


# ---------------------------------------------------------------------------
# 5. add-department
# ---------------------------------------------------------------------------

def add_department(conn, args):
    """Create a new department.

    Required: --name, --company-id
    Optional: --parent-id, --cost-center-id
    """
    if not args.name:
        err("--name is required")
    if not args.company_id:
        err("--company-id is required")

    _validate_company_exists(conn, args.company_id)

    # Validate parent department if provided
    if args.parent_id:
        dt = Table("department")
        q = Q.from_(dt).select(dt.id, dt.company_id).where(dt.id == P())
        parent = conn.execute(q.get_sql(), (args.parent_id,)).fetchone()
        if not parent:
            err(f"Parent department {args.parent_id} not found")
        if parent["company_id"] != args.company_id:
            err(
                f"Parent department {args.parent_id} belongs to a different company"
            )

    # Validate cost center if provided
    if args.cost_center_id:
        cct = Table("cost_center")
        q = Q.from_(cct).select(cct.id).where(cct.id == P())
        cc = conn.execute(q.get_sql(), (args.cost_center_id,)).fetchone()
        if not cc:
            err(f"Cost center {args.cost_center_id} not found")

    # Check for duplicate name within the same company
    dt2 = Table("department")
    q = (Q.from_(dt2).select(dt2.id)
         .where(dt2.name == P())
         .where(dt2.company_id == P()))
    existing = conn.execute(q.get_sql(), (args.name, args.company_id)).fetchone()
    if existing:
        err(
            f"Department '{args.name}' already exists in this company "
            f"(id: {existing['id']})"
        )

    dept_id = str(uuid.uuid4())
    now = _now_iso()

    sql, _cols = insert_row("department", {
        "id": P(), "name": P(), "parent_id": P(), "company_id": P(),
        "cost_center_id": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (dept_id, args.name, args.parent_id, args.company_id,
                        args.cost_center_id, now, now))

    audit(conn, "erpclaw-hr", "add-department", "department", dept_id,
           new_values={"name": args.name, "company_id": args.company_id},
           description=f"Created department '{args.name}'")

    conn.commit()

    ok({
        "department_id": dept_id,
        "name": args.name,
        "message": f"Department '{args.name}' created successfully",
    })


# ---------------------------------------------------------------------------
# 6. list-departments
# ---------------------------------------------------------------------------

def list_departments(conn, args):
    """List departments with optional filtering.

    Optional: --company-id, --parent-id, --limit, --offset
    Returns: list of departments with parent name and cost center name.
    """
    d = Table("department").as_("d")
    p = Table("department").as_("p")
    c = Table("company").as_("c")

    base = (Q.from_(d)
            .left_join(p).on(p.id == d.parent_id)
            .left_join(c).on(c.id == d.company_id))

    params = []
    crit = None

    def _and(c_arg, new):
        return new if c_arg is None else c_arg & new

    if args.company_id:
        crit = _and(crit, d.company_id == P())
        params.append(args.company_id)
    if args.parent_id:
        crit = _and(crit, d.parent_id == P())
        params.append(args.parent_id)

    count_q = Q.from_(d).select(fn.Count("*"))
    if crit is not None:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (base
              .select(d.id, d.name, d.parent_id, d.company_id,
                      d.cost_center_id,
                      p.name.as_("parent_name"),
                      c.name.as_("company_name"))
              .orderby(d.name)
              .limit(P()).offset(P()))
    if crit is not None:
        list_q = list_q.where(crit)
    list_params = params + [limit, offset]
    rows = conn.execute(list_q.get_sql(), list_params).fetchall()

    # Count employees per department
    emp_t = Table("employee")
    departments = []
    for row in rows:
        dept = row_to_dict(row)
        eq = (Q.from_(emp_t)
              .select(fn.Count("*"))
              .where(emp_t.department_id == P())
              .where(emp_t.status == "active"))
        emp_count = conn.execute(eq.get_sql(), (dept["id"],)).fetchone()
        dept["employee_count"] = emp_count[0] if emp_count else 0
        departments.append(dept)

    ok({"departments": departments, "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 7. add-designation
# ---------------------------------------------------------------------------

def add_designation(conn, args):
    """Create a new designation (job title).

    Required: --name
    Optional: --description
    """
    if not args.name:
        err("--name is required")

    # Check for duplicate name (designation.name is UNIQUE)
    dt = Table("designation")
    q = Q.from_(dt).select(dt.id).where(dt.name == P())
    existing = conn.execute(q.get_sql(), (args.name,)).fetchone()
    if existing:
        err(f"Designation '{args.name}' already exists (id: {existing['id']})")

    desig_id = str(uuid.uuid4())
    now = _now_iso()

    sql, _cols = insert_row("designation", {
        "id": P(), "name": P(), "description": P(),
        "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (desig_id, args.name, args.description, now, now))

    audit(conn, "erpclaw-hr", "add-designation", "designation", desig_id,
           new_values={"name": args.name},
           description=f"Created designation '{args.name}'")

    conn.commit()

    ok({
        "designation_id": desig_id,
        "name": args.name,
        "message": f"Designation '{args.name}' created successfully",
    })


# ---------------------------------------------------------------------------
# 8. list-designations
# ---------------------------------------------------------------------------

def list_designations(conn, args):
    """List all designations.

    Optional: --limit, --offset
    Returns: list of designations with employee counts.
    """
    dt = Table("designation")
    count_row = conn.execute(
        Q.from_(dt).select(fn.Count("*")).get_sql()
    ).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    q = (Q.from_(dt)
         .select(dt.id, dt.name, dt.description, dt.created_at, dt.updated_at)
         .orderby(dt.name)
         .limit(P()).offset(P()))
    rows = conn.execute(q.get_sql(), (limit, offset)).fetchall()

    emp_t = Table("employee")
    designations = []
    for row in rows:
        desig = row_to_dict(row)
        eq = (Q.from_(emp_t)
              .select(fn.Count("*"))
              .where(emp_t.designation_id == P())
              .where(emp_t.status == "active"))
        emp_count = conn.execute(eq.get_sql(), (desig["id"],)).fetchone()
        desig["employee_count"] = emp_count[0] if emp_count else 0
        designations.append(desig)

    ok({"designations": designations, "total_count": total_count,
         "limit": limit, "offset": offset, "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 9. add-leave-type
# ---------------------------------------------------------------------------

def add_leave_type(conn, args):
    """Create a new leave type.

    Required: --name, --max-days-allowed
    Optional: --is-paid-leave (default 1), --is-carry-forward (default 0),
              --max-carry-forward-days, --is-compensatory (default 0),
              --applicable-after-days (default 0)
    """
    if not args.name:
        err("--name is required")
    if not args.max_days_allowed:
        err("--max-days-allowed is required")

    # Validate max_days_allowed is a positive number
    try:
        max_days = to_decimal(args.max_days_allowed)
        if max_days <= Decimal("0"):
            err("--max-days-allowed must be greater than 0")
    except (InvalidOperation, TypeError):
        err(f"Invalid max-days-allowed value: {args.max_days_allowed}")

    # Check for duplicate name (leave_type.name is UNIQUE)
    ltt = Table("leave_type")
    q = Q.from_(ltt).select(ltt.id).where(ltt.name == P())
    existing = conn.execute(q.get_sql(), (args.name,)).fetchone()
    if existing:
        err(f"Leave type '{args.name}' already exists (id: {existing['id']})")

    # Parse optional boolean / numeric flags
    is_paid_leave = int(args.is_paid_leave) if args.is_paid_leave is not None else 1
    if is_paid_leave not in (0, 1):
        err("--is-paid-leave must be 0 or 1")

    is_carry_forward = int(args.is_carry_forward) if args.is_carry_forward is not None else 0
    if is_carry_forward not in (0, 1):
        err("--is-carry-forward must be 0 or 1")

    max_carry_forward_days = args.max_carry_forward_days
    if max_carry_forward_days:
        try:
            cf_days = to_decimal(max_carry_forward_days)
            if cf_days < Decimal("0"):
                err("--max-carry-forward-days must be >= 0")
        except (InvalidOperation, TypeError):
            err(f"Invalid max-carry-forward-days value: {max_carry_forward_days}")

    is_compensatory = int(args.is_compensatory) if args.is_compensatory is not None else 0
    if is_compensatory not in (0, 1):
        err("--is-compensatory must be 0 or 1")

    applicable_after_days = 0
    if args.applicable_after_days is not None:
        try:
            applicable_after_days = int(args.applicable_after_days)
            if applicable_after_days < 0:
                err("--applicable-after-days must be >= 0")
        except (ValueError, TypeError):
            err(f"Invalid applicable-after-days value: {args.applicable_after_days}")

    lt_id = str(uuid.uuid4())
    now = _now_iso()

    sql, _cols = insert_row("leave_type", {
        "id": P(), "name": P(), "max_days_allowed": P(), "is_carry_forward": P(),
        "max_carry_forward_days": P(), "is_paid_leave": P(), "is_compensatory": P(),
        "applicable_after_days": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (
        lt_id, args.name, str(max_days), is_carry_forward,
        max_carry_forward_days, is_paid_leave, is_compensatory,
        applicable_after_days, now, now,
    ))

    audit(conn, "erpclaw-hr", "add-leave-type", "leave_type", lt_id,
           new_values={"name": args.name, "max_days_allowed": str(max_days)},
           description=f"Created leave type '{args.name}'")

    conn.commit()

    ok({
        "leave_type_id": lt_id,
        "name": args.name,
        "max_days_allowed": str(max_days),
        "message": f"Leave type '{args.name}' created successfully",
    })


# ---------------------------------------------------------------------------
# 10. list-leave-types
# ---------------------------------------------------------------------------

def list_leave_types(conn, args):
    """List all leave types.

    Optional: --limit, --offset
    Returns: list of leave types.
    """
    ltt = Table("leave_type")
    count_row = conn.execute(
        Q.from_(ltt).select(fn.Count("*")).get_sql()
    ).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    q = (Q.from_(ltt)
         .select(ltt.id, ltt.name, ltt.max_days_allowed, ltt.is_carry_forward,
                 ltt.max_carry_forward_days, ltt.is_paid_leave, ltt.is_compensatory,
                 ltt.applicable_after_days, ltt.created_at, ltt.updated_at)
         .orderby(ltt.name)
         .limit(P()).offset(P()))
    rows = conn.execute(q.get_sql(), (limit, offset)).fetchall()

    ok({
        "leave_types": [row_to_dict(r) for r in rows],
        "total_count": total_count,
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total_count,
    })


# ---------------------------------------------------------------------------
# 11. add-leave-allocation
# ---------------------------------------------------------------------------

def add_leave_allocation(conn, args):
    """Allocate leave days to an employee for a fiscal year.

    Required: --employee-id, --leave-type-id, --total-leaves, --fiscal-year
    Logic: Calculate remaining = total - used (default 0).
           Handle carry_forward from previous fiscal year if the leave type
           has is_carry_forward enabled.
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.leave_type_id:
        err("--leave-type-id is required")
    if not args.total_leaves:
        err("--total-leaves is required")
    if not args.fiscal_year:
        err("--fiscal-year is required")

    # Validate references
    emp = _validate_employee_exists(conn, args.employee_id)
    lt = _validate_leave_type_exists(conn, args.leave_type_id)

    # Validate total leaves
    try:
        total_leaves = to_decimal(args.total_leaves)
        if total_leaves < Decimal("0"):
            err("--total-leaves must be >= 0")
    except (InvalidOperation, TypeError):
        err(f"Invalid total-leaves value: {args.total_leaves}")

    # Validate fiscal year exists
    fyt = Table("fiscal_year")
    q = Q.from_(fyt).select(fyt.id, fyt.name).where(fyt.name == P())
    fy_row = conn.execute(q.get_sql(), (args.fiscal_year,)).fetchone()
    if not fy_row:
        err(f"Fiscal year '{args.fiscal_year}' not found")

    # Check for existing allocation for same employee + leave type + fiscal year
    lat = Table("leave_allocation")
    q = (Q.from_(lat).select(lat.id)
         .where(lat.employee_id == P())
         .where(lat.leave_type_id == P())
         .where(lat.fiscal_year == P()))
    existing = conn.execute(q.get_sql(),
                            (args.employee_id, args.leave_type_id, args.fiscal_year)).fetchone()
    if existing:
        err(
            f"Leave allocation already exists for employee {args.employee_id}, "
            f"leave type {args.leave_type_id}, fiscal year {args.fiscal_year} "
            f"(id: {existing['id']}). Use update instead."
        )

    # Check for carry forward from previous fiscal year
    carry_forwarded = Decimal("0")
    carry_forwarded_from = None

    if lt["is_carry_forward"]:
        # Find the previous fiscal year's allocation for this employee/leave type
        lat2 = Table("leave_allocation")
        q = (Q.from_(lat2)
             .select(lat2.id, lat2.remaining_leaves, lat2.fiscal_year)
             .where(lat2.employee_id == P())
             .where(lat2.leave_type_id == P())
             .where(lat2.fiscal_year != P())
             .orderby(lat2.fiscal_year, order=Order.desc)
             .limit(1))
        prev_alloc = conn.execute(
            q.get_sql(),
            (args.employee_id, args.leave_type_id, args.fiscal_year),
        ).fetchone()

        if prev_alloc and to_decimal(prev_alloc["remaining_leaves"]) > Decimal("0"):
            carry_forwarded = to_decimal(prev_alloc["remaining_leaves"])

            # Cap at max_carry_forward_days if set
            if lt["max_carry_forward_days"]:
                max_cf = to_decimal(lt["max_carry_forward_days"])
                if carry_forwarded > max_cf:
                    carry_forwarded = max_cf

            carry_forwarded_from = prev_alloc["id"]
            total_leaves += carry_forwarded

    # Default used_leaves to 0 for new allocation
    used_leaves = Decimal("0")
    remaining_leaves = total_leaves - used_leaves

    alloc_id = str(uuid.uuid4())
    now = _now_iso()

    sql, _cols = insert_row("leave_allocation", {
        "id": P(), "employee_id": P(), "leave_type_id": P(), "fiscal_year": P(),
        "total_leaves": P(), "used_leaves": P(), "remaining_leaves": P(),
        "carry_forwarded_from": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (
        alloc_id, args.employee_id, args.leave_type_id,
        args.fiscal_year,
        str(total_leaves), str(used_leaves), str(remaining_leaves),
        carry_forwarded_from, now, now,
    ))

    audit(conn, "erpclaw-hr", "add-leave-allocation", "leave_allocation", alloc_id,
           new_values={
               "employee_id": args.employee_id,
               "leave_type_id": args.leave_type_id,
               "fiscal_year": args.fiscal_year,
               "total_leaves": str(total_leaves),
               "carry_forwarded": str(carry_forwarded),
           },
           description=f"Allocated {total_leaves} leave days")

    conn.commit()

    result = {
        "allocation_id": alloc_id,
        "employee_id": args.employee_id,
        "leave_type": lt["name"],
        "fiscal_year": args.fiscal_year,
        "total_leaves": str(total_leaves),
        "used_leaves": str(used_leaves),
        "remaining_leaves": str(remaining_leaves),
        "message": f"Leave allocation created: {total_leaves} days",
    }
    if carry_forwarded > Decimal("0"):
        result["carry_forwarded"] = str(carry_forwarded)
        result["carry_forwarded_from"] = carry_forwarded_from

    ok(result)


# ---------------------------------------------------------------------------
# 12. get-leave-balance
# ---------------------------------------------------------------------------

def get_leave_balance(conn, args):
    """Get leave balance for an employee.

    Required: --employee-id
    Optional: --leave-type-id (filter to specific type),
              --fiscal-year (defaults to current)
    Returns: balance per leave type.
    """
    if not args.employee_id:
        err("--employee-id is required")

    _validate_employee_exists(conn, args.employee_id)

    # Determine fiscal year
    fiscal_year = args.fiscal_year
    if not fiscal_year:
        fiscal_year = _get_fiscal_year(conn, date.today().isoformat())
        if not fiscal_year:
            err("No open fiscal year found for today's date")

    la = Table("leave_allocation").as_("la")
    lt = Table("leave_type").as_("lt")

    q = (Q.from_(la)
         .join(lt).on(lt.id == la.leave_type_id)
         .select(la.id.as_("allocation_id"), la.leave_type_id,
                 lt.name.as_("leave_type_name"), lt.is_paid_leave,
                 la.total_leaves, la.used_leaves, la.remaining_leaves,
                 la.carry_forwarded_from, la.fiscal_year)
         .where(la.employee_id == P())
         .where(la.fiscal_year == P())
         .orderby(lt.name))
    params = [args.employee_id, fiscal_year]

    if args.leave_type_id:
        _validate_leave_type_exists(conn, args.leave_type_id)
        q = q.where(la.leave_type_id == P())
        params.append(args.leave_type_id)

    rows = conn.execute(q.get_sql(), params).fetchall()

    balances = [row_to_dict(r) for r in rows]

    # Also count pending leave applications (draft/approved not yet deducted)
    la_app = Table("leave_application")
    for balance in balances:
        pq = (Q.from_(la_app)
              .select(fn.Coalesce(DecimalSum(la_app.total_days), ValueWrapper("0")).as_("pending_days"))
              .where(la_app.employee_id == P())
              .where(la_app.leave_type_id == P())
              .where(la_app.status == "draft"))
        pending = conn.execute(
            pq.get_sql(), (args.employee_id, balance["leave_type_id"])
        ).fetchone()
        balance["pending_days"] = str(
            round_currency(to_decimal(str(pending["pending_days"])))
        ) if pending else "0"

    ok({
        "employee_id": args.employee_id,
        "fiscal_year": fiscal_year,
        "balances": balances,
        "total_count": len(balances),
    })


# ---------------------------------------------------------------------------
# 13. add-leave-application
# ---------------------------------------------------------------------------

def add_leave_application(conn, args):
    """Create a leave application (request).

    Required: --employee-id, --leave-type-id, --from-date, --to-date
    Optional: --half-day (0 or 1), --half-day-date, --reason
    Logic: Calculate total_days (business days between from/to, minus
           holidays, accounting for half_day). Generate naming_series via
           get_next_name("leave_application"). Status = draft.
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.leave_type_id:
        err("--leave-type-id is required")
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    # Validate references
    emp = _validate_employee_exists(conn, args.employee_id)
    lt = _validate_leave_type_exists(conn, args.leave_type_id)

    # Validate employee is active
    if emp["status"] != "active":
        err(f"Employee {args.employee_id} is not active (status: {emp['status']})")

    # Validate date formats
    try:
        from_dt = date.fromisoformat(args.from_date)
    except (ValueError, TypeError):
        err(f"Invalid from-date format: {args.from_date}. Use YYYY-MM-DD")

    try:
        to_dt = date.fromisoformat(args.to_date)
    except (ValueError, TypeError):
        err(f"Invalid to-date format: {args.to_date}. Use YYYY-MM-DD")

    if from_dt > to_dt:
        err(f"from-date ({args.from_date}) must be on or before to-date ({args.to_date})")

    # Parse half_day flag
    half_day = False
    half_day_date = None
    if args.half_day:
        half_day = int(args.half_day) == 1
        if half_day:
            half_day_date = args.half_day_date
            if not half_day_date:
                # Default to from_date if not specified
                half_day_date = args.from_date
            else:
                try:
                    hd_dt = date.fromisoformat(half_day_date)
                except (ValueError, TypeError):
                    err(f"Invalid half-day-date format: {half_day_date}")
                if hd_dt < from_dt or hd_dt > to_dt:
                    err(
                        f"half-day-date ({half_day_date}) must be between "
                        f"from-date ({args.from_date}) and to-date ({args.to_date})"
                    )

    # Check applicable_after_days
    if lt["applicable_after_days"] and lt["applicable_after_days"] > 0:
        if emp["date_of_joining"]:
            joining_date = date.fromisoformat(emp["date_of_joining"])
            days_employed = (from_dt - joining_date).days
            if days_employed < lt["applicable_after_days"]:
                err(
                    f"Leave type '{lt['name']}' is only applicable after "
                    f"{lt['applicable_after_days']} days of employment. "
                    f"Employee has been employed for {days_employed} days."
                )

    # Get holidays for this employee's date range
    holidays = _get_employee_holidays(
        conn, args.employee_id, args.from_date, args.to_date,
    )

    # Calculate total days (business days excluding holidays)
    total_days = _count_business_days(
        args.from_date, args.to_date,
        half_day=half_day,
        holidays=holidays,
    )

    if total_days <= Decimal("0"):
        err(
            "Calculated leave days is 0. The selected date range may only "
            "contain weekends and/or holidays."
        )

    # Check that sufficient leave balance exists
    fiscal_year = _get_fiscal_year(conn, args.from_date)
    if fiscal_year:
        lat = Table("leave_allocation")
        q = (Q.from_(lat)
             .select(lat.id, lat.remaining_leaves)
             .where(lat.employee_id == P())
             .where(lat.leave_type_id == P())
             .where(lat.fiscal_year == P()))
        alloc = conn.execute(
            q.get_sql(), (args.employee_id, args.leave_type_id, fiscal_year)
        ).fetchone()
        if alloc:
            remaining = to_decimal(alloc["remaining_leaves"])
            if total_days > remaining:
                err(
                    f"Insufficient leave balance. Requested: {total_days}, "
                    f"Remaining: {remaining} for '{lt['name']}' in {fiscal_year}"
                )
        else:
            err(
                f"No leave allocation found for employee {args.employee_id}, "
                f"leave type '{lt['name']}', fiscal year {fiscal_year}"
            )

    # Check for overlapping leave applications (approved or draft)
    lap = Table("leave_application")
    q = (Q.from_(lap)
         .select(lap.id, lap.from_date, lap.to_date, lap.status)
         .where(lap.employee_id == P())
         .where(lap.status.isin(["draft", "approved"]))
         .where(lap.from_date <= P())
         .where(lap.to_date >= P()))
    overlapping = conn.execute(
        q.get_sql(), (args.employee_id, args.to_date, args.from_date)
    ).fetchone()
    if overlapping:
        err(
            f"Overlapping leave application found (id: {overlapping['id']}, "
            f"{overlapping['from_date']} to {overlapping['to_date']}, "
            f"status: {overlapping['status']})"
        )

    # Generate naming series and ID
    app_id = str(uuid.uuid4())
    naming_series = get_next_name(conn, "leave_application",
                                  company_id=emp["company_id"])
    now = _now_iso()

    sql, _cols = insert_row("leave_application", {
        "id": P(), "naming_series": P(), "employee_id": P(), "leave_type_id": P(),
        "from_date": P(), "to_date": P(), "total_days": P(),
        "half_day": P(), "half_day_date": P(), "reason": P(),
        "status": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (
        app_id, naming_series, args.employee_id, args.leave_type_id,
        args.from_date, args.to_date, str(total_days),
        1 if half_day else 0, half_day_date, args.reason,
        "draft", now, now,
    ))

    audit(conn, "erpclaw-hr", "add-leave-application", "leave_application", app_id,
           new_values={
               "employee_id": args.employee_id,
               "leave_type": lt["name"],
               "from_date": args.from_date,
               "to_date": args.to_date,
               "total_days": str(total_days),
           },
           description=f"Leave application created: {total_days} days of {lt['name']}")

    conn.commit()

    ok({
        "leave_application_id": app_id,
        "naming_series": naming_series,
        "employee_id": args.employee_id,
        "leave_type": lt["name"],
        "from_date": args.from_date,
        "to_date": args.to_date,
        "total_days": str(total_days),
        "half_day": half_day,
        "status": "draft",
        "holidays_excluded": len(holidays),
        "message": f"Leave application created: {total_days} days of {lt['name']}",
    })


# ---------------------------------------------------------------------------
# 14. approve-leave
# ---------------------------------------------------------------------------

def approve_leave(conn, args):
    """Approve a leave application.

    Required: --leave-application-id, --approved-by
    Logic: Validate status=draft, set status=approved, set approved_by.
           Deduct from leave_allocation: used_leaves += total_days,
           remaining_leaves -= total_days.
    """
    if not args.leave_application_id:
        err("--leave-application-id is required")
    if not args.approved_by:
        err("--approved-by is required")

    # Fetch application
    lap = Table("leave_application")
    q = Q.from_(lap).select(lap.star).where(lap.id == P())
    app = conn.execute(q.get_sql(), (args.leave_application_id,)).fetchone()
    if not app:
        err(f"Leave application {args.leave_application_id} not found")

    if app["status"] != "draft":
        err(
            f"Leave application {args.leave_application_id} cannot be approved. "
            f"Current status: {app['status']} (must be 'draft')"
        )

    # Validate approved_by is a valid employee
    approver = _validate_employee_exists(conn, args.approved_by)

    # Cannot approve own leave
    if args.approved_by == app["employee_id"]:
        err("An employee cannot approve their own leave application")

    total_days = to_decimal(app["total_days"])
    now = _now_iso()

    # Update leave application status
    sql = update_row("leave_application",
                     data={"status": P(), "approved_by": P(), "updated_at": P()},
                     where={"id": P()})
    conn.execute(sql, ("approved", args.approved_by, now, args.leave_application_id))

    # Deduct from leave allocation
    fiscal_year = _get_fiscal_year(conn, app["from_date"])
    if fiscal_year:
        lat = Table("leave_allocation")
        q = (Q.from_(lat)
             .select(lat.id, lat.used_leaves, lat.remaining_leaves)
             .where(lat.employee_id == P())
             .where(lat.leave_type_id == P())
             .where(lat.fiscal_year == P()))
        alloc = conn.execute(
            q.get_sql(), (app["employee_id"], app["leave_type_id"], fiscal_year)
        ).fetchone()

        if alloc:
            old_used = to_decimal(alloc["used_leaves"])
            old_remaining = to_decimal(alloc["remaining_leaves"])
            new_used = old_used + total_days
            new_remaining = old_remaining - total_days

            # Guard against negative remaining
            if new_remaining < Decimal("0"):
                conn.rollback()
                err(
                    f"Cannot approve: would result in negative leave balance. "
                    f"Remaining: {old_remaining}, Requested: {total_days}"
                )

            sql = update_row("leave_allocation",
                             data={"used_leaves": P(), "remaining_leaves": P(), "updated_at": P()},
                             where={"id": P()})
            conn.execute(sql, (str(new_used), str(new_remaining), now, alloc["id"]))
        else:
            # No allocation found -- this should not normally happen
            # since add-leave-application checks for it, but handle gracefully
            conn.rollback()
            err(
                f"No leave allocation found for employee {app['employee_id']}, "
                f"leave type {app['leave_type_id']}, fiscal year {fiscal_year}. "
                f"Cannot deduct leave balance."
            )
    else:
        conn.rollback()
        err(
            f"No open fiscal year found for date {app['from_date']}. "
            f"Cannot update leave balance."
        )

    # Get leave type name for response
    ltt = Table("leave_type")
    q = Q.from_(ltt).select(ltt.name).where(ltt.id == P())
    lt = conn.execute(q.get_sql(), (app["leave_type_id"],)).fetchone()
    leave_type_name = lt["name"] if lt else app["leave_type_id"]

    audit(conn, "erpclaw-hr", "approve-leave", "leave_application",
           args.leave_application_id,
           old_values={"status": "draft"},
           new_values={
               "status": "approved",
               "approved_by": args.approved_by,
               "used_leaves_delta": str(total_days),
           },
           description=f"Approved {total_days} days of {leave_type_name}")

    conn.commit()

    ok({
        "leave_application_id": args.leave_application_id,
        "status": "approved",
        "approved_by": args.approved_by,
        "approver_name": approver["full_name"],
        "total_days": str(total_days),
        "leave_type": leave_type_name,
        "message": f"Leave application approved: {total_days} days of {leave_type_name}",
    })


# ---------------------------------------------------------------------------
# 15. reject-leave
# ---------------------------------------------------------------------------

def reject_leave(conn, args):
    """Reject a leave application.

    Required: --leave-application-id
    Optional: --reason
    Logic: Validate status=draft, set status=rejected.
    """
    if not args.leave_application_id:
        err("--leave-application-id is required")

    # Fetch application
    lap = Table("leave_application")
    q = Q.from_(lap).select(lap.star).where(lap.id == P())
    app = conn.execute(q.get_sql(), (args.leave_application_id,)).fetchone()
    if not app:
        err(f"Leave application {args.leave_application_id} not found")

    if app["status"] != "draft":
        err(
            f"Leave application {args.leave_application_id} cannot be rejected. "
            f"Current status: {app['status']} (must be 'draft')"
        )

    now = _now_iso()

    # Update status to rejected
    sql = update_row("leave_application",
                     data={"status": P(), "updated_at": P()},
                     where={"id": P()})
    conn.execute(sql, ("rejected", now, args.leave_application_id))

    # Get leave type name for audit
    ltt = Table("leave_type")
    q = Q.from_(ltt).select(ltt.name).where(ltt.id == P())
    lt = conn.execute(q.get_sql(), (app["leave_type_id"],)).fetchone()
    leave_type_name = lt["name"] if lt else app["leave_type_id"]

    rejection_reason = args.reason or "No reason provided"

    audit(conn, "erpclaw-hr", "reject-leave", "leave_application",
           args.leave_application_id,
           old_values={"status": "draft"},
           new_values={"status": "rejected", "rejection_reason": rejection_reason},
           description=f"Rejected leave: {leave_type_name} ({rejection_reason})")

    conn.commit()

    ok({
        "leave_application_id": args.leave_application_id,
        "status": "rejected",
        "leave_type": leave_type_name,
        "employee_id": app["employee_id"],
        "rejection_reason": rejection_reason,
        "message": f"Leave application rejected: {leave_type_name}",
    })


# ---------------------------------------------------------------------------
# 16. list-leave-applications
# ---------------------------------------------------------------------------

def list_leave_applications(conn, args):
    """Query leave applications with filtering and pagination.

    Optional: --employee-id, --status, --from-date, --to-date,
              --leave-type-id, --limit (20), --offset (0)
    """
    la = Table("leave_application").as_("la")
    e = Table("employee").as_("e")
    lt = Table("leave_type").as_("lt")
    approver = Table("employee").as_("approver")

    params = []
    crit = None

    def _and(c, new):
        return new if c is None else c & new

    if args.employee_id:
        crit = _and(crit, la.employee_id == P())
        params.append(args.employee_id)
    if args.status:
        if args.status not in VALID_LEAVE_STATUSES:
            err(f"Invalid leave status '{args.status}'. Valid: {VALID_LEAVE_STATUSES}")
        crit = _and(crit, la.status == P())
        params.append(args.status)
    if args.leave_type_id:
        crit = _and(crit, la.leave_type_id == P())
        params.append(args.leave_type_id)
    if args.from_date:
        crit = _and(crit, la.from_date >= P())
        params.append(args.from_date)
    if args.to_date:
        crit = _and(crit, la.to_date <= P())
        params.append(args.to_date)

    # Total count
    count_q = Q.from_(la).select(fn.Count("*"))
    if crit is not None:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(la)
              .join(e).on(e.id == la.employee_id)
              .join(lt).on(lt.id == la.leave_type_id)
              .left_join(approver).on(approver.id == la.approved_by)
              .select(la.id, la.naming_series, la.employee_id,
                      la.leave_type_id, la.from_date, la.to_date,
                      la.total_days, la.half_day, la.half_day_date,
                      la.reason, la.status, la.approved_by,
                      la.created_at, la.updated_at,
                      e.full_name.as_("employee_name"),
                      e.naming_series.as_("employee_series"),
                      lt.name.as_("leave_type_name"),
                      approver.full_name.as_("approved_by_name"))
              .orderby(la.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    if crit is not None:
        list_q = list_q.where(crit)
    list_params = params + [limit, offset]
    rows = conn.execute(list_q.get_sql(), list_params).fetchall()

    ok({
        "leave_applications": [row_to_dict(r) for r in rows],
        "total_count": total_count,
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total_count,
    })


# ---------------------------------------------------------------------------
# 17. mark-attendance
# ---------------------------------------------------------------------------

def mark_attendance(conn, args):
    """Mark attendance for a single employee on a given date.

    Required: --employee-id, --date, --status
    Optional: --shift, --check-in-time, --check-out-time, --working-hours,
              --late-entry (0|1), --early-exit (0|1), --source (manual|biometric|app)
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.date:
        err("--date is required")
    if not args.status:
        err("--status is required")

    # Validate employee
    emp = _validate_employee_exists(conn, args.employee_id)

    # Validate date format and no future dates
    try:
        att_date = date.fromisoformat(args.date)
    except (ValueError, TypeError):
        err(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
    if att_date > date.today():
        err(f"Cannot mark attendance for a future date ({args.date}). Today is {date.today().isoformat()}")

    # Validate status
    if args.status not in VALID_ATTENDANCE_STATUSES:
        err(f"Invalid attendance status '{args.status}'. Valid: {VALID_ATTENDANCE_STATUSES}")

    # Validate source
    source = args.source or "manual"
    if source not in VALID_ATTENDANCE_SOURCES:
        err(f"Invalid attendance source '{source}'. Valid: {VALID_ATTENDANCE_SOURCES}")

    # Validate late_entry / early_exit
    late_entry = int(args.late_entry) if args.late_entry else 0
    if late_entry not in (0, 1):
        err("--late-entry must be 0 or 1")

    early_exit = int(args.early_exit) if args.early_exit else 0
    if early_exit not in (0, 1):
        err("--early-exit must be 0 or 1")

    # Check for duplicate (UNIQUE employee_id + attendance_date)
    at = Table("attendance")
    q = (Q.from_(at).select(at.id)
         .where(at.employee_id == P())
         .where(at.attendance_date == P()))
    existing = conn.execute(q.get_sql(), (args.employee_id, args.date)).fetchone()
    if existing:
        err(
            f"Attendance already marked for employee {args.employee_id} on "
            f"{args.date} (id: {existing['id']})"
        )

    att_id = str(uuid.uuid4())

    sql, _cols = insert_row("attendance", {
        "id": P(), "employee_id": P(), "attendance_date": P(), "status": P(),
        "shift": P(), "check_in_time": P(), "check_out_time": P(), "working_hours": P(),
        "late_entry": P(), "early_exit": P(), "source": P(), "created_at": P(),
    })
    conn.execute(sql, (
        att_id, args.employee_id, args.date, args.status,
        args.shift, args.check_in_time, args.check_out_time,
        args.working_hours,
        late_entry, early_exit, source, _now_iso(),
    ))

    audit(conn, "erpclaw-hr", "mark-attendance", "attendance", att_id,
           new_values={
               "employee_id": args.employee_id,
               "date": args.date,
               "status": args.status,
           },
           description=f"Marked attendance: {args.status} for {emp['full_name']} on {args.date}")

    conn.commit()

    ok({
        "attendance_id": att_id,
        "employee_id": args.employee_id,
        "employee_name": emp["full_name"],
        "date": args.date,
        "status": args.status,
        "source": source,
        "message": f"Attendance marked: {args.status} for {emp['full_name']} on {args.date}",
    })


# ---------------------------------------------------------------------------
# 18. bulk-mark-attendance
# ---------------------------------------------------------------------------

def bulk_mark_attendance(conn, args):
    """Bulk mark attendance for multiple employees on a given date.

    Required: --date, --entries (JSON array of [{employee_id, status}])
    Optional: --source (manual|biometric|app)
    """
    if not args.date:
        err("--date is required")
    if not args.entries:
        err("--entries is required (JSON array)")

    # Validate date format
    try:
        date.fromisoformat(args.date)
    except (ValueError, TypeError):
        err(f"Invalid date format: {args.date}. Use YYYY-MM-DD")

    entries = _parse_json_arg(args.entries, "entries")
    if not isinstance(entries, list) or len(entries) == 0:
        err("--entries must be a non-empty JSON array")

    source = args.source or "manual"
    if source not in VALID_ATTENDANCE_SOURCES:
        err(f"Invalid attendance source '{source}'. Valid: {VALID_ATTENDANCE_SOURCES}")

    created = 0
    skipped_duplicates = 0
    errors = []

    for i, entry in enumerate(entries):
        emp_id = entry.get("employee_id")
        status = entry.get("status")

        if not emp_id or not status:
            errors.append(f"Entry {i}: missing employee_id or status")
            continue

        if status not in VALID_ATTENDANCE_STATUSES:
            errors.append(f"Entry {i}: invalid status '{status}'")
            continue

        # Validate employee exists
        emp_t = Table("employee")
        q = Q.from_(emp_t).select(emp_t.id, emp_t.full_name).where(emp_t.id == P())
        emp = conn.execute(q.get_sql(), (emp_id,)).fetchone()
        if not emp:
            errors.append(f"Entry {i}: employee {emp_id} not found")
            continue

        # Check for duplicate
        at = Table("attendance")
        q = (Q.from_(at).select(at.id)
             .where(at.employee_id == P())
             .where(at.attendance_date == P()))
        existing = conn.execute(q.get_sql(), (emp_id, args.date)).fetchone()
        if existing:
            skipped_duplicates += 1
            continue

        att_id = str(uuid.uuid4())
        sql, _cols = insert_row("attendance", {
            "id": P(), "employee_id": P(), "attendance_date": P(), "status": P(),
            "late_entry": P(), "early_exit": P(), "source": P(), "created_at": P(),
        })
        conn.execute(sql, (att_id, emp_id, args.date, status, 0, 0, source, _now_iso()))
        created += 1

    conn.commit()

    total = len(entries)
    ok({
        "date": args.date,
        "total": total,
        "created": created,
        "skipped_duplicates": skipped_duplicates,
        "errors": errors,
        "message": f"Bulk attendance: {created} created, {skipped_duplicates} skipped (duplicates), {len(errors)} errors",
    })


# ---------------------------------------------------------------------------
# 19. list-attendance
# ---------------------------------------------------------------------------

def list_attendance(conn, args):
    """Query attendance records with filtering and pagination.

    Optional: --employee-id, --from-date, --to-date, --status,
              --limit (20), --offset (0)
    Returns: list with employee name JOIN, attendance summary counts.
    """
    a = Table("attendance").as_("a")
    e = Table("employee").as_("e")

    params = []
    crit = None

    def _and(c, new):
        return new if c is None else c & new

    if args.employee_id:
        crit = _and(crit, a.employee_id == P())
        params.append(args.employee_id)
    if args.from_date:
        crit = _and(crit, a.attendance_date >= P())
        params.append(args.from_date)
    if args.to_date:
        crit = _and(crit, a.attendance_date <= P())
        params.append(args.to_date)
    if args.status:
        if args.status not in VALID_ATTENDANCE_STATUSES:
            err(f"Invalid attendance status '{args.status}'. Valid: {VALID_ATTENDANCE_STATUSES}")
        crit = _and(crit, a.status == P())
        params.append(args.status)

    # Total count
    count_q = Q.from_(a).select(fn.Count("*"))
    if crit is not None:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    # Summary counts (using same filters)
    summary_q = (Q.from_(a)
                 .select(
                     fn.Count("*").as_("total_records"),
                     fn.Sum(Case().when(a.status == "present", 1).else_(0)).as_("present"),
                     fn.Sum(Case().when(a.status == "absent", 1).else_(0)).as_("absent"),
                     fn.Sum(Case().when(a.status == "half_day", 1).else_(0)).as_("half_day"),
                     fn.Sum(Case().when(a.status == "on_leave", 1).else_(0)).as_("on_leave"),
                     fn.Sum(Case().when(a.status == "work_from_home", 1).else_(0)).as_("work_from_home"),
                 ))
    if crit is not None:
        summary_q = summary_q.where(crit)
    summary = conn.execute(summary_q.get_sql(), list(params)).fetchone()

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    list_q = (Q.from_(a)
              .join(e).on(e.id == a.employee_id)
              .select(a.id, a.employee_id, a.attendance_date, a.status,
                      a.shift, a.check_in_time, a.check_out_time, a.working_hours,
                      a.late_entry, a.early_exit, a.source, a.created_at,
                      e.full_name.as_("employee_name"),
                      e.naming_series.as_("employee_series"))
              .orderby(a.attendance_date, order=Order.desc)
              .orderby(e.full_name)
              .limit(P()).offset(P()))
    if crit is not None:
        list_q = list_q.where(crit)
    list_params = params + [limit, offset]
    rows = conn.execute(list_q.get_sql(), list_params).fetchall()

    ok({
        "attendance": [row_to_dict(r) for r in rows],
        "total_count": total_count,
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total_count,
        "summary": row_to_dict(summary) if summary else {},
    })


# ---------------------------------------------------------------------------
# 20. add-holiday-list
# ---------------------------------------------------------------------------

def add_holiday_list(conn, args):
    """Create a new holiday list with optional holiday entries.

    Required: --name, --company-id, --from-date, --to-date
    Optional: --holidays (JSON array of [{date, description}])
    """
    if not args.name:
        err("--name is required")
    if not args.company_id:
        err("--company-id is required")
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    _validate_company_exists(conn, args.company_id)

    # Validate dates
    try:
        from_dt = date.fromisoformat(args.from_date)
    except (ValueError, TypeError):
        err(f"Invalid from-date format: {args.from_date}. Use YYYY-MM-DD")

    try:
        to_dt = date.fromisoformat(args.to_date)
    except (ValueError, TypeError):
        err(f"Invalid to-date format: {args.to_date}. Use YYYY-MM-DD")

    if from_dt > to_dt:
        err(f"from-date ({args.from_date}) must be on or before to-date ({args.to_date})")

    # Check for duplicate name (holiday_list.name is UNIQUE)
    hlt = Table("holiday_list")
    q = Q.from_(hlt).select(hlt.id).where(hlt.name == P())
    existing = conn.execute(q.get_sql(), (args.name,)).fetchone()
    if existing:
        err(f"Holiday list '{args.name}' already exists (id: {existing['id']})")

    hl_id = str(uuid.uuid4())
    now = _now_iso()

    sql, _cols = insert_row("holiday_list", {
        "id": P(), "name": P(), "from_date": P(), "to_date": P(),
        "company_id": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (hl_id, args.name, args.from_date, args.to_date,
                        args.company_id, now, now))

    # Insert holiday child rows
    holiday_count = 0
    holidays = _parse_json_arg(args.holidays, "holidays") if args.holidays else None
    if holidays and isinstance(holidays, list):
        for h in holidays:
            h_date = h.get("date")
            h_desc = h.get("description", "")

            if not h_date:
                continue

            # Validate holiday date is within range
            try:
                h_dt = date.fromisoformat(h_date)
            except (ValueError, TypeError):
                continue  # skip invalid dates

            if h_dt < from_dt or h_dt > to_dt:
                continue  # skip out-of-range dates

            h_sql, _hcols = insert_row("holiday", {
                "id": P(), "holiday_list_id": P(), "holiday_date": P(), "description": P(),
            })
            conn.execute(h_sql, (str(uuid.uuid4()), hl_id, h_date, h_desc))
            holiday_count += 1

    audit(conn, "erpclaw-hr", "add-holiday-list", "holiday_list", hl_id,
           new_values={
               "name": args.name,
               "company_id": args.company_id,
               "from_date": args.from_date,
               "to_date": args.to_date,
               "holiday_count": holiday_count,
           },
           description=f"Created holiday list '{args.name}' with {holiday_count} holidays")

    conn.commit()

    ok({
        "holiday_list_id": hl_id,
        "name": args.name,
        "from_date": args.from_date,
        "to_date": args.to_date,
        "holiday_count": holiday_count,
        "message": f"Holiday list '{args.name}' created with {holiday_count} holidays",
    })


# ---------------------------------------------------------------------------
# 21. add-expense-claim (draft)
# ---------------------------------------------------------------------------

def add_expense_claim(conn, args):
    """Create a new expense claim in draft status.

    Required: --employee-id, --expense-date, --company-id,
              --items (JSON array of [{expense_type, description, amount, account_id}])
    Logic: Validate employee, validate company, generate naming_series via
           get_next_name. Calculate total_amount from items. INSERT expense_claim
           (status=draft), INSERT expense_claim_item for each item.
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.expense_date:
        err("--expense-date is required")
    if not args.company_id:
        err("--company-id is required")
    if not args.items:
        err("--items is required (JSON array)")

    # Validate references
    emp = _validate_employee_exists(conn, args.employee_id)
    _validate_company_exists(conn, args.company_id)

    # Validate date
    try:
        date.fromisoformat(args.expense_date)
    except (ValueError, TypeError):
        err(f"Invalid expense-date format: {args.expense_date}. Use YYYY-MM-DD")

    # Parse items
    items = _parse_json_arg(args.items, "items")
    if not isinstance(items, list) or len(items) == 0:
        err("--items must be a non-empty JSON array")

    # Validate each item and calculate total
    total_amount = Decimal("0")
    validated_items = []

    for i, item in enumerate(items):
        expense_type = item.get("expense_type")
        description = item.get("description", "")
        amount_str = item.get("amount")
        account_id = item.get("account_id")

        if not expense_type:
            err(f"Item {i}: missing expense_type")
        if expense_type not in VALID_EXPENSE_TYPES:
            err(f"Item {i}: invalid expense_type '{expense_type}'. Valid: {VALID_EXPENSE_TYPES}")
        if not amount_str:
            err(f"Item {i}: missing amount")

        try:
            amount = to_decimal(amount_str)
            if amount <= Decimal("0"):
                err(f"Item {i}: amount must be greater than 0")
        except (InvalidOperation, TypeError):
            err(f"Item {i}: invalid amount '{amount_str}'")

        # Validate account_id if provided
        if account_id:
            acct_t = Table("account")
            q = Q.from_(acct_t).select(acct_t.id, acct_t.is_group, acct_t.company_id).where(acct_t.id == P())
            acct = conn.execute(q.get_sql(), (account_id,)).fetchone()
            if not acct:
                err(f"Item {i}: account {account_id} not found")
            if acct["is_group"]:
                err(f"Item {i}: account {account_id} is a group account")
            if acct["company_id"] != args.company_id:
                err(f"Item {i}: account {account_id} belongs to a different company")

        total_amount += amount
        validated_items.append({
            "expense_type": expense_type,
            "description": description,
            "amount": str(round_currency(amount)),
            "account_id": account_id,
        })

    # Generate naming series and ID
    claim_id = str(uuid.uuid4())
    naming_series = get_next_name(conn, "expense_claim", company_id=args.company_id)
    now = _now_iso()

    sql, _cols = insert_row("expense_claim", {
        "id": P(), "naming_series": P(), "employee_id": P(), "expense_date": P(),
        "total_amount": P(), "status": P(), "company_id": P(),
        "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (
        claim_id, naming_series, args.employee_id, args.expense_date,
        str(round_currency(total_amount)), "draft", args.company_id,
        now, now,
    ))

    # Insert expense_claim_item rows
    item_sql, _icols = insert_row("expense_claim_item", {
        "id": P(), "expense_claim_id": P(), "expense_type": P(),
        "description": P(), "amount": P(), "account_id": P(),
    })
    for item in validated_items:
        conn.execute(item_sql, (
            str(uuid.uuid4()), claim_id, item["expense_type"],
            item["description"], item["amount"], item["account_id"],
        ))

    audit(conn, "erpclaw-hr", "add-expense-claim", "expense_claim", claim_id,
           new_values={
               "employee_id": args.employee_id,
               "total_amount": str(round_currency(total_amount)),
               "item_count": len(validated_items),
           },
           description=f"Created expense claim {naming_series}: {round_currency(total_amount)}")

    conn.commit()

    ok({
        "expense_claim_id": claim_id,
        "naming_series": naming_series,
        "employee_id": args.employee_id,
        "employee_name": emp["full_name"],
        "expense_date": args.expense_date,
        "total_amount": str(round_currency(total_amount)),
        "item_count": len(validated_items),
        "status": "draft",
        "message": f"Expense claim {naming_series} created: {round_currency(total_amount)}",
    })


# ---------------------------------------------------------------------------
# 22. submit-expense-claim
# ---------------------------------------------------------------------------

def submit_expense_claim(conn, args):
    """Submit a draft expense claim for approval.

    Required: --expense-claim-id
    Logic: Validate status=draft, set status=submitted.
    """
    if not args.expense_claim_id:
        err("--expense-claim-id is required")

    ect = Table("expense_claim")
    q = Q.from_(ect).select(ect.star).where(ect.id == P())
    claim = conn.execute(q.get_sql(), (args.expense_claim_id,)).fetchone()
    if not claim:
        err(f"Expense claim {args.expense_claim_id} not found")

    if claim["status"] != "draft":
        err(
            f"Expense claim {args.expense_claim_id} cannot be submitted. "
            f"Current status: {claim['status']} (must be 'draft')"
        )

    now = _now_iso()

    sql = update_row("expense_claim",
                     data={"status": P(), "updated_at": P()},
                     where={"id": P()})
    conn.execute(sql, ("submitted", now, args.expense_claim_id))

    audit(conn, "erpclaw-hr", "submit-expense-claim", "expense_claim",
           args.expense_claim_id,
           old_values={"status": "draft"},
           new_values={"status": "submitted"},
           description=f"Submitted expense claim {claim['naming_series']}")

    conn.commit()

    ok({
        "expense_claim_id": args.expense_claim_id,
        "naming_series": claim["naming_series"],
        "status": "submitted",
        "message": f"Expense claim {claim['naming_series']} submitted for approval",
    })


# ---------------------------------------------------------------------------
# 23. approve-expense-claim (with GL posting)
# ---------------------------------------------------------------------------

def approve_expense_claim(conn, args):
    """Approve a submitted expense claim and create GL entries.

    Required: --expense-claim-id, --approved-by
    Logic: Validate status=submitted, set status=approved.
    GL Posting: For each expense_claim_item:
      - DR the item's account_id (expense account) with item.amount
      - CR Payable account with total_amount
      - Use insert_gl_entries() from shared lib
      - voucher_type = 'expense_claim'
    """
    if not args.expense_claim_id:
        err("--expense-claim-id is required")
    if not args.approved_by:
        err("--approved-by is required")

    # Fetch expense claim
    ect = Table("expense_claim")
    q = Q.from_(ect).select(ect.star).where(ect.id == P())
    claim = conn.execute(q.get_sql(), (args.expense_claim_id,)).fetchone()
    if not claim:
        err(f"Expense claim {args.expense_claim_id} not found")

    if claim["status"] != "submitted":
        err(
            f"Expense claim {args.expense_claim_id} cannot be approved. "
            f"Current status: {claim['status']} (must be 'submitted')"
        )

    # Validate approved_by is a valid employee
    approver = _validate_employee_exists(conn, args.approved_by)

    # Cannot approve own expense claim
    if args.approved_by == claim["employee_id"]:
        err("An employee cannot approve their own expense claim")

    company_id = claim["company_id"]
    total_amount = to_decimal(claim["total_amount"])
    posting_date = claim["expense_date"]
    now = _now_iso()

    # Fetch expense claim items
    ecit = Table("expense_claim_item")
    q = Q.from_(ecit).select(ecit.star).where(ecit.expense_claim_id == P())
    items = conn.execute(q.get_sql(), (args.expense_claim_id,)).fetchall()

    if not items:
        err(f"Expense claim {args.expense_claim_id} has no items")

    # Find a payable account for the CR side
    # First try company's default_payable_account_id
    co_t = Table("company")
    q = Q.from_(co_t).select(co_t.default_payable_account_id).where(co_t.id == P())
    company_row = conn.execute(q.get_sql(), (company_id,)).fetchone()

    payable_acct = None
    if company_row:
        payable_acct = company_row["default_payable_account_id"]

    if not payable_acct:
        # Fallback: find any payable account for this company
        acct_t = Table("account")
        q = (Q.from_(acct_t).select(acct_t.id)
             .where(acct_t.account_type == "payable")
             .where(acct_t.company_id == P())
             .where(acct_t.is_group == 0)
             .limit(1))
        payable_row = conn.execute(q.get_sql(), (company_id,)).fetchone()
        payable_acct = payable_row["id"] if payable_row else None

    if not payable_acct:
        # Last resort: find any liability account
        acct_t2 = Table("account")
        q = (Q.from_(acct_t2).select(acct_t2.id)
             .where(acct_t2.root_type == "liability")
             .where(acct_t2.company_id == P())
             .where(acct_t2.is_group == 0)
             .limit(1))
        liability_row = conn.execute(q.get_sql(), (company_id,)).fetchone()
        payable_acct = liability_row["id"] if liability_row else None

    if not payable_acct:
        conn.rollback()
        err("No payable or liability account found for company. Cannot create GL entries.")

    # Get cost center for expense accounts (P&L accounts require cost center)
    cost_center_id = _get_cost_center(conn, company_id)

    # Get fiscal year
    fiscal_year = _get_fiscal_year(conn, posting_date)
    if not fiscal_year:
        conn.rollback()
        err(f"No open fiscal year found for posting date {posting_date}")

    # Build GL entries: DR each expense account, CR payable
    gl_entries = []

    # If an item has no account_id, try to find a default expense account
    default_expense_acct = None
    co_t2 = Table("company")
    q = Q.from_(co_t2).select(co_t2.default_expense_account_id).where(co_t2.id == P())
    company_detail = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if company_detail:
        default_expense_acct = company_detail["default_expense_account_id"]

    if not default_expense_acct:
        acct_t3 = Table("account")
        q = (Q.from_(acct_t3).select(acct_t3.id)
             .where(acct_t3.account_type == "expense")
             .where(acct_t3.company_id == P())
             .where(acct_t3.is_group == 0)
             .limit(1))
        expense_row = conn.execute(q.get_sql(), (company_id,)).fetchone()
        if expense_row:
            default_expense_acct = expense_row["id"]

    for item in items:
        item_amount = to_decimal(item["amount"])
        if item_amount <= Decimal("0"):
            continue

        expense_account_id = item["account_id"] or default_expense_acct
        if not expense_account_id:
            conn.rollback()
            err(
                f"Expense claim item has no account_id and no default expense "
                f"account found for company. Cannot create GL entries."
            )

        # DR: Expense account
        gl_entries.append({
            "account_id": expense_account_id,
            "debit": str(round_currency(item_amount)),
            "credit": "0",
            "cost_center_id": cost_center_id,
            "fiscal_year": fiscal_year,
        })

    # CR: Payable account with total_amount
    gl_entries.append({
        "account_id": payable_acct,
        "debit": "0",
        "credit": str(round_currency(total_amount)),
        "party_type": "employee",
        "party_id": claim["employee_id"],
        "fiscal_year": fiscal_year,
    })

    # Insert GL entries via shared lib (does NOT commit)
    try:
        gl_ids = insert_gl_entries(
            conn,
            entries=gl_entries,
            voucher_type="expense_claim",
            voucher_id=args.expense_claim_id,
            posting_date=posting_date,
            company_id=company_id,
            remarks=f"Expense claim {claim['naming_series']} approved",
        )
    except ValueError as e:
        conn.rollback()
        sys.stderr.write(f"[erpclaw-hr] {e}\n")
        err(f"GL posting failed: {e}")

    # Update expense claim status
    sql = update_row("expense_claim",
                     data={"status": P(), "approved_by": P(), "approval_date": P(), "updated_at": P()},
                     where={"id": P()})
    conn.execute(sql, ("approved", args.approved_by, now, now, args.expense_claim_id))

    audit(conn, "erpclaw-hr", "approve-expense-claim", "expense_claim",
           args.expense_claim_id,
           old_values={"status": "submitted"},
           new_values={
               "status": "approved",
               "approved_by": args.approved_by,
               "gl_entry_count": len(gl_ids),
           },
           description=f"Approved expense claim {claim['naming_series']} with {len(gl_ids)} GL entries")

    conn.commit()

    ok({
        "expense_claim_id": args.expense_claim_id,
        "naming_series": claim["naming_series"],
        "status": "approved",
        "approved_by": args.approved_by,
        "approver_name": approver["full_name"],
        "total_amount": str(round_currency(total_amount)),
        "gl_entry_count": len(gl_ids),
        "gl_entry_ids": gl_ids,
        "message": (
            f"Expense claim {claim['naming_series']} approved with "
            f"{len(gl_ids)} GL entries"
        ),
    })


# ---------------------------------------------------------------------------
# 24. reject-expense-claim
# ---------------------------------------------------------------------------

def reject_expense_claim(conn, args):
    """Reject a submitted expense claim.

    Required: --expense-claim-id
    Optional: --reason
    Logic: Validate status=submitted, set status=rejected.
    """
    if not args.expense_claim_id:
        err("--expense-claim-id is required")

    ect = Table("expense_claim")
    q = Q.from_(ect).select(ect.star).where(ect.id == P())
    claim = conn.execute(q.get_sql(), (args.expense_claim_id,)).fetchone()
    if not claim:
        err(f"Expense claim {args.expense_claim_id} not found")

    if claim["status"] != "submitted":
        err(
            f"Expense claim {args.expense_claim_id} cannot be rejected. "
            f"Current status: {claim['status']} (must be 'submitted')"
        )

    now = _now_iso()
    rejection_reason = args.reason or "No reason provided"

    sql = update_row("expense_claim",
                     data={"status": P(), "updated_at": P()},
                     where={"id": P()})
    conn.execute(sql, ("rejected", now, args.expense_claim_id))

    audit(conn, "erpclaw-hr", "reject-expense-claim", "expense_claim",
           args.expense_claim_id,
           old_values={"status": "submitted"},
           new_values={"status": "rejected", "rejection_reason": rejection_reason},
           description=f"Rejected expense claim {claim['naming_series']}: {rejection_reason}")

    conn.commit()

    ok({
        "expense_claim_id": args.expense_claim_id,
        "naming_series": claim["naming_series"],
        "status": "rejected",
        "employee_id": claim["employee_id"],
        "rejection_reason": rejection_reason,
        "message": f"Expense claim {claim['naming_series']} rejected",
    })


# ---------------------------------------------------------------------------
# 25. update-expense-claim-status (cross-skill, called by payments)
# ---------------------------------------------------------------------------

def update_expense_claim_status(conn, args):
    """Update expense claim status (cross-skill, used by erpclaw-payments).

    Required: --expense-claim-id, --status
    Optional: --payment-entry-id
    Logic: Update status and payment_entry_id. Used to mark as 'paid'.
    """
    if not args.expense_claim_id:
        err("--expense-claim-id is required")
    if not args.status:
        err("--status is required")

    if args.status not in VALID_EXPENSE_STATUSES:
        err(f"Invalid expense claim status '{args.status}'. Valid: {VALID_EXPENSE_STATUSES}")

    ect = Table("expense_claim")
    q = Q.from_(ect).select(ect.star).where(ect.id == P())
    claim = conn.execute(q.get_sql(), (args.expense_claim_id,)).fetchone()
    if not claim:
        err(f"Expense claim {args.expense_claim_id} not found")

    old_status = claim["status"]
    now = _now_iso()

    updates = {"status": args.status, "updated_at": now}
    if args.payment_entry_id:
        updates["payment_entry_id"] = args.payment_entry_id

    sql, params = dynamic_update("expense_claim", updates, where={"id": args.expense_claim_id})
    conn.execute(sql, params)

    audit(conn, "erpclaw-hr", "update-expense-claim-status", "expense_claim",
           args.expense_claim_id,
           old_values={"status": old_status},
           new_values={"status": args.status, "payment_entry_id": args.payment_entry_id},
           description=f"Updated expense claim status: {old_status} -> {args.status}")

    conn.commit()

    ok({
        "expense_claim_id": args.expense_claim_id,
        "naming_series": claim["naming_series"],
        "old_status": old_status,
        "new_status": args.status,
        "payment_entry_id": args.payment_entry_id,
        "message": f"Expense claim status updated: {old_status} -> {args.status}",
    })


# ---------------------------------------------------------------------------
# 26. list-expense-claims
# ---------------------------------------------------------------------------

def list_expense_claims(conn, args):
    """Query expense claims with filtering and pagination.

    Optional: --employee-id, --status, --company-id, --from-date, --to-date,
              --limit (20), --offset (0)
    Returns: list with employee name, items count, total amount.
    """
    ec = Table("expense_claim").as_("ec")
    e = Table("employee").as_("e")

    params = []
    crit = None

    def _and(c, new):
        return new if c is None else c & new

    if args.employee_id:
        crit = _and(crit, ec.employee_id == P())
        params.append(args.employee_id)
    if args.status:
        if args.status not in VALID_EXPENSE_STATUSES:
            err(f"Invalid expense claim status '{args.status}'. Valid: {VALID_EXPENSE_STATUSES}")
        crit = _and(crit, ec.status == P())
        params.append(args.status)
    if args.company_id:
        crit = _and(crit, ec.company_id == P())
        params.append(args.company_id)
    if args.from_date:
        crit = _and(crit, ec.expense_date >= P())
        params.append(args.from_date)
    if args.to_date:
        crit = _and(crit, ec.expense_date <= P())
        params.append(args.to_date)

    # Total count
    count_q = Q.from_(ec).select(fn.Count("*"))
    if crit is not None:
        count_q = count_q.where(crit)
    count_row = conn.execute(count_q.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    # raw SQL — correlated subquery for item_count not supported by PyPika
    conditions = ["1=1"]
    raw_params = []
    if args.employee_id:
        conditions.append("ec.employee_id = ?")
        raw_params.append(args.employee_id)
    if args.status:
        conditions.append("ec.status = ?")
        raw_params.append(args.status)
    if args.company_id:
        conditions.append("ec.company_id = ?")
        raw_params.append(args.company_id)
    if args.from_date:
        conditions.append("ec.expense_date >= ?")
        raw_params.append(args.from_date)
    if args.to_date:
        conditions.append("ec.expense_date <= ?")
        raw_params.append(args.to_date)
    where = " AND ".join(conditions)
    raw_params.extend([limit, offset])

    rows = conn.execute(
        f"""SELECT ec.id, ec.naming_series, ec.employee_id,
               ec.expense_date, ec.total_amount, ec.status,
               ec.approved_by, ec.approval_date, ec.payment_entry_id,
               ec.company_id, ec.created_at, ec.updated_at,
               e.full_name AS employee_name,
               e.naming_series AS employee_series,
               (SELECT COUNT(*) FROM expense_claim_item eci
                WHERE eci.expense_claim_id = ec.id) AS item_count
           FROM expense_claim ec
           JOIN employee e ON e.id = ec.employee_id
           WHERE {where}
           ORDER BY ec.created_at DESC
           LIMIT ? OFFSET ?""",
        raw_params,
    ).fetchall()

    ok({
        "expense_claims": [row_to_dict(r) for r in rows],
        "total_count": total_count,
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total_count,
    })


# ---------------------------------------------------------------------------
# 27. record-lifecycle-event
# ---------------------------------------------------------------------------

def record_lifecycle_event(conn, args):
    """Record an employee lifecycle event.

    Required: --employee-id, --event-type, --event-date
    Optional: --details (JSON), --old-values (JSON), --new-values (JSON)
    Logic: Validate employee, validate event_type, INSERT event record.
           For separation/resignation/retirement: optionally update employee
           status to 'left' and set date_of_exit.
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.event_type:
        err("--event-type is required")
    if not args.event_date:
        err("--event-date is required")

    # Validate employee
    emp = _validate_employee_exists(conn, args.employee_id)

    # Validate event type
    if args.event_type not in VALID_LIFECYCLE_EVENTS:
        err(f"Invalid event type '{args.event_type}'. Valid: {VALID_LIFECYCLE_EVENTS}")

    # Validate date
    try:
        date.fromisoformat(args.event_date)
    except (ValueError, TypeError):
        err(f"Invalid event-date format: {args.event_date}. Use YYYY-MM-DD")

    # Parse optional JSON fields
    details = _parse_json_arg(args.details, "details") if args.details else None
    old_values = _parse_json_arg(args.old_values, "old-values") if args.old_values else None
    new_values = _parse_json_arg(args.new_values, "new-values") if args.new_values else None

    event_id = str(uuid.uuid4())
    now = _now_iso()

    sql, _cols = insert_row("employee_lifecycle_event", {
        "id": P(), "employee_id": P(), "event_type": P(), "event_date": P(),
        "details": P(), "old_values": P(), "new_values": P(), "created_at": P(),
    })
    conn.execute(sql, (
        event_id, args.employee_id, args.event_type, args.event_date,
        json.dumps(details) if details else None,
        json.dumps(old_values) if old_values else None,
        json.dumps(new_values) if new_values else None,
        now,
    ))

    # For termination events, update employee status to 'left' and set date_of_exit
    employee_updated = False
    if args.event_type in ("separation", "resignation", "retirement"):
        upd_sql = update_row("employee",
                             data={"status": P(), "date_of_exit": P(), "updated_at": P()},
                             where={"id": P()})
        conn.execute(upd_sql, ("left", args.event_date, now, args.employee_id))
        employee_updated = True

    audit(conn, "erpclaw-hr", "record-lifecycle-event", "employee_lifecycle_event", event_id,
           new_values={
               "employee_id": args.employee_id,
               "event_type": args.event_type,
               "event_date": args.event_date,
               "employee_status_updated": employee_updated,
           },
           description=(
               f"Lifecycle event: {args.event_type} for {emp['full_name']} "
               f"on {args.event_date}"
           ))

    conn.commit()

    result = {
        "event_id": event_id,
        "employee_id": args.employee_id,
        "employee_name": emp["full_name"],
        "event_type": args.event_type,
        "event_date": args.event_date,
        "message": f"Lifecycle event recorded: {args.event_type} for {emp['full_name']}",
    }
    if employee_updated:
        result["employee_status_updated"] = True
        result["new_employee_status"] = "left"
        result["date_of_exit"] = args.event_date

    ok(result)


# ---------------------------------------------------------------------------
# 28. status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """Get HR module status summary.

    Optional: --company-id (filter by company)
    Returns: employee counts by status, department counts, leave summary,
             attendance summary, expense claims by status, recent lifecycle events.
    """
    emp_t = Table("employee")

    # Employee counts by status
    emp_statuses = {}
    for status in VALID_EMPLOYEE_STATUSES:
        q = Q.from_(emp_t).select(fn.Count("*")).where(emp_t.status == P())
        p = [status]
        if args.company_id:
            q = q.where(emp_t.company_id == P())
            p.append(args.company_id)
        cnt = conn.execute(q.get_sql(), p).fetchone()[0]
        if cnt > 0:
            emp_statuses[status] = cnt

    q = Q.from_(emp_t).select(fn.Count("*"))
    p = []
    if args.company_id:
        q = q.where(emp_t.company_id == P())
        p.append(args.company_id)
    total_employees = conn.execute(q.get_sql(), p).fetchone()[0]

    # Department counts
    dept_t = Table("department")
    q = Q.from_(dept_t).select(fn.Count("*"))
    p = []
    if args.company_id:
        q = q.where(dept_t.company_id == P())
        p.append(args.company_id)
    total_departments = conn.execute(q.get_sql(), p).fetchone()[0]

    # Leave summary (current fiscal year)
    today_str = date.today().isoformat()
    fiscal_year = _get_fiscal_year(conn, today_str)

    leave_summary = {}
    if fiscal_year:
        # raw SQL — correlated subquery for fiscal year start date
        for la_status in VALID_LEAVE_STATUSES:
            cnt = conn.execute(
                f"""SELECT COUNT(*) FROM leave_application la
                    JOIN employee e ON e.id = la.employee_id
                    WHERE la.status = ?
                      AND la.from_date >= (
                          SELECT start_date FROM fiscal_year WHERE name = ?
                      )
                    {"AND e.company_id = ?" if args.company_id else ""}""",
                [la_status, fiscal_year] + ([args.company_id] if args.company_id else []),
            ).fetchone()[0]
            if cnt > 0:
                leave_summary[la_status] = cnt

    # Attendance summary (current month)
    month_start = date.today().replace(day=1).isoformat()
    month_end = date.today().isoformat()

    att_t = Table("attendance").as_("a")
    emp_a = Table("employee").as_("e")
    att_summary = {}
    for att_status in VALID_ATTENDANCE_STATUSES:
        q = (Q.from_(att_t)
             .join(emp_a).on(emp_a.id == att_t.employee_id)
             .select(fn.Count("*"))
             .where(att_t.status == P())
             .where(att_t.attendance_date >= P())
             .where(att_t.attendance_date <= P()))
        p = [att_status, month_start, month_end]
        if args.company_id:
            q = q.where(emp_a.company_id == P())
            p.append(args.company_id)
        cnt = conn.execute(q.get_sql(), p).fetchone()[0]
        if cnt > 0:
            att_summary[att_status] = cnt

    # Expense claims by status
    ec_t = Table("expense_claim")
    ec_statuses = {}
    for ec_status in VALID_EXPENSE_STATUSES:
        q = Q.from_(ec_t).select(fn.Count("*")).where(ec_t.status == P())
        p = [ec_status]
        if args.company_id:
            q = q.where(ec_t.company_id == P())
            p.append(args.company_id)
        cnt = conn.execute(q.get_sql(), p).fetchone()[0]
        if cnt > 0:
            ec_statuses[ec_status] = cnt

    # Recent lifecycle events (last 10)
    el = Table("employee_lifecycle_event").as_("el")
    emp_e = Table("employee").as_("e")
    q = (Q.from_(el)
         .join(emp_e).on(emp_e.id == el.employee_id)
         .select(el.id, el.employee_id, el.event_type, el.event_date,
                 el.created_at, emp_e.full_name.as_("employee_name"))
         .orderby(el.created_at, order=Order.desc)
         .limit(10))
    p = []
    if args.company_id:
        q = q.where(emp_e.company_id == P())
        p.append(args.company_id)
    recent_events = conn.execute(q.get_sql(), p).fetchall()

    ok({
        "total_employees": total_employees,
        "employees_by_status": emp_statuses,
        "total_departments": total_departments,
        "leave_summary": leave_summary,
        "attendance_summary_current_month": att_summary,
        "expense_claims_by_status": ec_statuses,
        "recent_lifecycle_events": [row_to_dict(r) for r in recent_events],
        "fiscal_year": fiscal_year,
    })


# ---------------------------------------------------------------------------
# Shift Management (Sprint 6, Feature #20)
# ---------------------------------------------------------------------------


def add_shift_type(conn, args):
    """Create a new shift type.

    Required: --name, --start-time, --end-time, --company-id
    Optional: --status (default 'active')
    """
    if not args.name:
        err("--name is required")
    if not args.start_time:
        err("--start-time is required")
    if not args.end_time:
        err("--end-time is required")
    if not args.company_id:
        err("--company-id is required")

    name = args.name.strip()
    start_time = args.start_time.strip()
    end_time = args.end_time.strip()
    company_id = args.company_id.strip()
    status = (args.status or "active").strip().lower()

    if status not in ("active", "inactive"):
        err(f"Invalid status '{status}'. Valid: active, inactive")

    # Validate time format (HH:MM or HH:MM:SS)
    import re
    time_re = re.compile(r'^\d{2}:\d{2}(:\d{2})?$')
    if not time_re.match(start_time):
        err(f"Invalid start_time '{start_time}'. Use HH:MM or HH:MM:SS format")
    if not time_re.match(end_time):
        err(f"Invalid end_time '{end_time}'. Use HH:MM or HH:MM:SS format")

    # Check company exists
    co_t = Table("company")
    co_q = Q.from_(co_t).select(co_t.id).where(co_t.id == P())
    if not conn.execute(co_q.get_sql(), (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Check unique name
    st_t = Table("shift_type")
    uniq_q = Q.from_(st_t).select(st_t.id).where(st_t.name == P())
    if conn.execute(uniq_q.get_sql(), (name,)).fetchone():
        err(f"Shift type '{name}' already exists")

    now = datetime.now(timezone.utc).isoformat()
    shift_id = str(uuid.uuid4())

    ins_sql, _ = insert_row("shift_type", {
        "id": P(), "name": P(), "start_time": P(), "end_time": P(),
        "company_id": P(), "status": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(ins_sql, (shift_id, name, start_time, end_time,
                           company_id, status, now, now))
    conn.commit()

    ok({
        "shift_type_id": shift_id,
        "name": name,
        "start_time": start_time,
        "end_time": end_time,
        "company_id": company_id,
        "shift_status": status,
    })


def list_shift_types(conn, args):
    """List shift types, optionally filtered by company_id and status.

    Optional: --company-id, --status, --limit, --offset
    """
    st_t = Table("shift_type")
    q = Q.from_(st_t).select(st_t.star).orderby(st_t.name)
    params = []

    if args.company_id:
        q = q.where(st_t.company_id == P())
        params.append(args.company_id)

    if args.status:
        q = q.where(st_t.status == P())
        params.append(args.status.strip().lower())

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    q = q.limit(limit).offset(offset)

    rows = conn.execute(q.get_sql(), params).fetchall()
    ok({
        "shift_types": [row_to_dict(r) for r in rows],
        "count": len(rows),
    })


def update_shift_type(conn, args):
    """Update a shift type.

    Required: --shift-type-id
    Optional: --name, --start-time, --end-time, --status
    """
    if not args.shift_type_id:
        err("--shift-type-id is required")

    shift_type_id = args.shift_type_id.strip()

    st_t = Table("shift_type")
    q = Q.from_(st_t).select(st_t.star).where(st_t.id == P())
    existing = conn.execute(q.get_sql(), (shift_type_id,)).fetchone()
    if not existing:
        err(f"Shift type {shift_type_id} not found")

    updates = {}
    if args.name:
        # Check uniqueness of new name
        uniq_q = Q.from_(st_t).select(st_t.id).where(
            (st_t.name == P()) & (st_t.id != P())
        )
        if conn.execute(uniq_q.get_sql(), (args.name.strip(), shift_type_id)).fetchone():
            err(f"Shift type '{args.name.strip()}' already exists")
        updates["name"] = args.name.strip()

    if args.start_time:
        import re
        if not re.match(r'^\d{2}:\d{2}(:\d{2})?$', args.start_time.strip()):
            err(f"Invalid start_time format. Use HH:MM or HH:MM:SS")
        updates["start_time"] = args.start_time.strip()

    if args.end_time:
        import re
        if not re.match(r'^\d{2}:\d{2}(:\d{2})?$', args.end_time.strip()):
            err(f"Invalid end_time format. Use HH:MM or HH:MM:SS")
        updates["end_time"] = args.end_time.strip()

    if args.status:
        status = args.status.strip().lower()
        if status not in ("active", "inactive"):
            err(f"Invalid status '{status}'. Valid: active, inactive")
        updates["status"] = status

    if not updates:
        err("No fields to update. Provide at least one of: --name, --start-time, --end-time, --status")

    now = datetime.now(timezone.utc).isoformat()
    updates["updated_at"] = now

    set_clauses = ", ".join(f"{k} = ?" for k in updates)
    params = list(updates.values()) + [shift_type_id]
    conn.execute(f"UPDATE shift_type SET {set_clauses} WHERE id = ?", params)
    conn.commit()

    # Re-fetch
    updated = conn.execute(q.get_sql(), (shift_type_id,)).fetchone()
    result = row_to_dict(updated)
    # Rename 'status' to 'shift_status' to avoid collision with ok() wrapper
    if "status" in result:
        result["shift_status"] = result.pop("status")
    ok(result)


def assign_shift(conn, args):
    """Assign a shift type to an employee.

    Required: --employee-id, --shift-type-id, --start-date
    Optional: --end-date, --status (default 'active')
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.shift_type_id:
        err("--shift-type-id is required")
    if not args.start_date:
        err("--start-date is required")

    employee_id = args.employee_id.strip()
    shift_type_id = args.shift_type_id.strip()
    start_date = args.start_date.strip()
    end_date = args.end_date.strip() if args.end_date else None
    status = (args.status or "active").strip().lower()

    if status not in ("active", "inactive"):
        err(f"Invalid status '{status}'. Valid: active, inactive")

    # Validate employee exists
    emp_t = Table("employee")
    emp_q = Q.from_(emp_t).select(emp_t.id).where(emp_t.id == P())
    if not conn.execute(emp_q.get_sql(), (employee_id,)).fetchone():
        err(f"Employee {employee_id} not found")

    # Validate shift type exists
    st_t = Table("shift_type")
    st_q = Q.from_(st_t).select(st_t.id).where(st_t.id == P())
    if not conn.execute(st_q.get_sql(), (shift_type_id,)).fetchone():
        err(f"Shift type {shift_type_id} not found")

    # Validate dates
    _validate_date = lambda d, n: None  # date format already enforced by arg parsing
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        err(f"Invalid start_date '{start_date}'. Use YYYY-MM-DD format")

    if end_date:
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            err(f"Invalid end_date '{end_date}'. Use YYYY-MM-DD format")
        if end_date < start_date:
            err("end_date cannot be before start_date")

    now = datetime.now(timezone.utc).isoformat()
    assignment_id = str(uuid.uuid4())

    ins_sql, _ = insert_row("shift_assignment", {
        "id": P(), "employee_id": P(), "shift_type_id": P(),
        "start_date": P(), "end_date": P(), "status": P(),
        "created_at": P(), "updated_at": P(),
    })
    conn.execute(ins_sql, (assignment_id, employee_id, shift_type_id,
                           start_date, end_date, status, now, now))
    conn.commit()

    ok({
        "shift_assignment_id": assignment_id,
        "employee_id": employee_id,
        "shift_type_id": shift_type_id,
        "start_date": start_date,
        "end_date": end_date,
        "assignment_status": status,
    })


def list_shift_assignments(conn, args):
    """List shift assignments, optionally filtered.

    Optional: --employee-id, --shift-type-id, --status, --company-id, --limit, --offset
    """
    sa_t = Table("shift_assignment").as_("sa")
    st_t = Table("shift_type").as_("st")
    emp_t = Table("employee").as_("e")

    q = (Q.from_(sa_t)
         .join(st_t).on(st_t.id == sa_t.shift_type_id)
         .join(emp_t).on(emp_t.id == sa_t.employee_id)
         .select(sa_t.star,
                 st_t.name.as_("shift_name"),
                 emp_t.full_name.as_("employee_name"))
         .orderby(sa_t.start_date, order=Order.desc))
    params = []

    if args.employee_id:
        q = q.where(sa_t.employee_id == P())
        params.append(args.employee_id)

    if args.shift_type_id:
        q = q.where(sa_t.shift_type_id == P())
        params.append(args.shift_type_id)

    if args.status:
        q = q.where(sa_t.status == P())
        params.append(args.status.strip().lower())

    if args.company_id:
        q = q.where(emp_t.company_id == P())
        params.append(args.company_id)

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    q = q.limit(limit).offset(offset)

    rows = conn.execute(q.get_sql(), params).fetchall()
    ok({
        "shift_assignments": [row_to_dict(r) for r in rows],
        "count": len(rows),
    })


# ---------------------------------------------------------------------------
# Feature #22f: Attendance Regularization (Sprint 7)
# ---------------------------------------------------------------------------

VALID_REGULARIZATION_ACTIONS = ("half_day", "deduct_leave", "warn")


def add_regularization_rule(conn, args):
    """Add an attendance regularization rule for a company.

    Required: --company-id, --late-threshold-minutes, --regularization-action
    """
    if not args.company_id:
        err("--company-id is required")
    if not args.late_threshold_minutes:
        err("--late-threshold-minutes is required")
    if not args.regularization_action:
        err("--regularization-action is required")

    co_t = Table("company")
    cq = Q.from_(co_t).select(co_t.id).where(co_t.id == P())
    if not conn.execute(cq.get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    try:
        threshold = int(args.late_threshold_minutes)
    except (ValueError, TypeError):
        err("--late-threshold-minutes must be an integer")
    if threshold <= 0:
        err("--late-threshold-minutes must be > 0")

    action = args.regularization_action.strip().lower()
    if action not in VALID_REGULARIZATION_ACTIONS:
        err(f"Invalid action '{action}'. Valid: {VALID_REGULARIZATION_ACTIONS}")

    rule_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    sql, _ = insert_row("attendance_regularization_rule", {
        "id": P(), "company_id": P(), "late_threshold_minutes": P(),
        "action": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (rule_id, args.company_id, threshold, action, now, now))

    audit(conn, "erpclaw-hr", "add-regularization-rule",
          "attendance_regularization_rule", rule_id,
          new_values={"company_id": args.company_id,
                      "late_threshold_minutes": threshold, "action": action})
    conn.commit()

    ok({
        "rule_id": rule_id,
        "company_id": args.company_id,
        "late_threshold_minutes": threshold,
        "action": action,
        "message": "Attendance regularization rule added",
    })


def apply_attendance_regularization(conn, args):
    """Apply attendance regularization rules for a company on a date range.

    Required: --company-id
    Optional: --from-date, --to-date
    """
    if not args.company_id:
        err("--company-id is required")

    arr_t = Table("attendance_regularization_rule")
    rq = (Q.from_(arr_t).select(arr_t.star)
          .where(arr_t.company_id == P())
          .orderby(arr_t.late_threshold_minutes))
    rules = conn.execute(rq.get_sql(), (args.company_id,)).fetchall()
    if not rules:
        err(f"No regularization rules found for company {args.company_id}")
    rules = [row_to_dict(r) for r in rules]

    at = Table("attendance")
    emp_t = Table("employee")
    q = (Q.from_(at)
         .join(emp_t).on(emp_t.id == at.employee_id)
         .select(at.star)
         .where(emp_t.company_id == P())
         .where(at.late_entry == 1))
    params = [args.company_id]

    if args.from_date:
        q = q.where(at.attendance_date >= P())
        params.append(args.from_date)
    if args.to_date:
        q = q.where(at.attendance_date <= P())
        params.append(args.to_date)

    records = conn.execute(q.get_sql(), params).fetchall()
    updated = 0
    warnings = []

    for rec in records:
        rec_d = row_to_dict(rec)
        check_in = rec_d.get("check_in_time")
        if not check_in:
            continue

        for rule in rules:
            threshold = rule["late_threshold_minutes"]
            action_type = rule["action"]

            try:
                parts = check_in.split(":")
                check_hour = int(parts[0])
                check_min = int(parts[1]) if len(parts) > 1 else 0
                late_minutes = (check_hour - 9) * 60 + check_min
                if late_minutes < 0:
                    late_minutes = 0
            except (ValueError, IndexError):
                late_minutes = threshold + 1

            if late_minutes >= threshold:
                if action_type == "half_day":
                    conn.execute(
                        "UPDATE attendance SET status = 'half_day' WHERE id = ?",
                        (rec_d["id"],)
                    )
                    updated += 1
                elif action_type == "warn":
                    warnings.append({
                        "attendance_id": rec_d["id"],
                        "employee_id": rec_d["employee_id"],
                        "date": rec_d["attendance_date"],
                        "late_minutes": late_minutes,
                    })
                elif action_type == "deduct_leave":
                    warnings.append({
                        "attendance_id": rec_d["id"],
                        "employee_id": rec_d["employee_id"],
                        "date": rec_d["attendance_date"],
                        "late_minutes": late_minutes,
                        "action": "deduct_leave",
                    })
                break

    conn.commit()
    ok({
        "records_processed": len(records),
        "records_updated": updated,
        "warnings": warnings,
        "warning_count": len(warnings),
    })


# ---------------------------------------------------------------------------
# Feature #21: Employee Documents (Sprint 7)
# ---------------------------------------------------------------------------

VALID_DOCUMENT_TYPES = (
    "passport", "visa", "drivers_license", "i9", "w4",
    "offer_letter", "contract", "certificate", "other",
)
VALID_DOCUMENT_STATUSES = ("active", "expired", "archived")


def add_employee_document(conn, args):
    """Add an employee document record.

    Required: --employee-id, --document-type, --document-name
    Optional: --expiry-date, --notes
    """
    if not args.employee_id:
        err("--employee-id is required")
    if not args.document_type:
        err("--document-type is required")
    if not args.document_name:
        err("--document-name is required")

    emp = _validate_employee_exists(conn, args.employee_id)

    doc_type = args.document_type.strip().lower()
    if doc_type not in VALID_DOCUMENT_TYPES:
        err(f"Invalid document type '{doc_type}'. Valid: {VALID_DOCUMENT_TYPES}")

    expiry_date = None
    if args.expiry_date:
        try:
            date.fromisoformat(args.expiry_date)
            expiry_date = args.expiry_date
        except (ValueError, TypeError):
            err(f"Invalid expiry date format: {args.expiry_date}. Use YYYY-MM-DD")

    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    sql, _ = insert_row("employee_document", {
        "id": P(), "employee_id": P(), "document_type": P(),
        "document_name": P(), "expiry_date": P(), "notes": P(),
        "status": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (
        doc_id, args.employee_id, doc_type,
        args.document_name.strip(), expiry_date,
        args.notes, "active", now, now,
    ))

    audit(conn, "erpclaw-hr", "add-employee-document",
          "employee_document", doc_id,
          new_values={"employee_id": args.employee_id,
                      "document_type": doc_type,
                      "document_name": args.document_name})
    conn.commit()

    ok({
        "employee_document_id": doc_id,
        "employee_id": args.employee_id,
        "employee_name": emp["full_name"],
        "document_type": doc_type,
        "document_name": args.document_name.strip(),
        "expiry_date": expiry_date,
        "message": "Employee document added",
    })


def list_employee_documents(conn, args):
    """List employee documents.

    Required: --employee-id
    Optional: --document-type, --status
    """
    if not args.employee_id:
        err("--employee-id is required")

    ed_t = Table("employee_document")
    q = (Q.from_(ed_t).select(ed_t.star)
         .where(ed_t.employee_id == P()))
    params = [args.employee_id]

    if args.document_type:
        q = q.where(ed_t.document_type == P())
        params.append(args.document_type.strip().lower())

    if args.status:
        q = q.where(ed_t.status == P())
        params.append(args.status.strip().lower())

    q = q.orderby(ed_t.created_at)
    rows = conn.execute(q.get_sql(), params).fetchall()

    ok({"documents": [row_to_dict(r) for r in rows], "count": len(rows)})


def get_employee_document(conn, args):
    """Get a specific employee document.

    Required: --document-id
    """
    if not args.document_id:
        err("--document-id is required")

    ed_t = Table("employee_document")
    q = Q.from_(ed_t).select(ed_t.star).where(ed_t.id == P())
    row = conn.execute(q.get_sql(), (args.document_id,)).fetchone()
    if not row:
        err(f"Employee document {args.document_id} not found")

    ok(row_to_dict(row))


def check_expiring_documents(conn, args):
    """Check for employee documents expiring within N days.

    Optional: --company-id, --days (default 30)
    """
    days = int(args.days or 30)
    today = date.today()
    cutoff = (today + timedelta(days=days)).isoformat()

    ed_t = Table("employee_document")
    emp_t = Table("employee")
    q = (Q.from_(ed_t)
         .join(emp_t).on(emp_t.id == ed_t.employee_id)
         .select(ed_t.star, emp_t.full_name.as_("employee_name"),
                 emp_t.company_id)
         .where(ed_t.expiry_date.isnotnull())
         .where(ed_t.expiry_date <= P())
         .where(ed_t.status == ValueWrapper("active")))
    params = [cutoff]

    if args.company_id:
        q = q.where(emp_t.company_id == P())
        params.append(args.company_id)

    q = q.orderby(ed_t.expiry_date)
    rows = conn.execute(q.get_sql(), params).fetchall()

    results = []
    for r in rows:
        d = row_to_dict(r)
        exp_date = date.fromisoformat(d["expiry_date"])
        d["days_until_expiry"] = (exp_date - today).days
        d["is_expired"] = exp_date < today
        results.append(d)

    ok({
        "expiring_documents": results,
        "count": len(results),
        "days_window": days,
    })


# ---------------------------------------------------------------------------
# ACTIONS dispatch table
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-employee": add_employee,
    "update-employee": update_employee,
    "get-employee": get_employee,
    "list-employees": list_employees,
    "add-department": add_department,
    "list-departments": list_departments,
    "add-designation": add_designation,
    "list-designations": list_designations,
    "add-leave-type": add_leave_type,
    "list-leave-types": list_leave_types,
    "add-leave-allocation": add_leave_allocation,
    "get-leave-balance": get_leave_balance,
    "add-leave-application": add_leave_application,
    "approve-leave": approve_leave,
    "reject-leave": reject_leave,
    "list-leave-applications": list_leave_applications,
    "mark-attendance": mark_attendance,
    "bulk-mark-attendance": bulk_mark_attendance,
    "list-attendance": list_attendance,
    "add-holiday-list": add_holiday_list,
    "add-expense-claim": add_expense_claim,
    "submit-expense-claim": submit_expense_claim,
    "approve-expense-claim": approve_expense_claim,
    "reject-expense-claim": reject_expense_claim,
    "update-expense-claim-status": update_expense_claim_status,
    "list-expense-claims": list_expense_claims,
    "record-lifecycle-event": record_lifecycle_event,
    "add-shift-type": add_shift_type,
    "list-shift-types": list_shift_types,
    "update-shift-type": update_shift_type,
    "assign-shift": assign_shift,
    "list-shift-assignments": list_shift_assignments,

    # --- Sprint 7: Attendance Regularization ---
    "add-regularization-rule": add_regularization_rule,
    "apply-attendance-regularization": apply_attendance_regularization,

    # --- Sprint 7: Employee Documents ---
    "add-employee-document": add_employee_document,
    "list-employee-documents": list_employee_documents,
    "get-employee-document": get_employee_document,
    "check-expiring-documents": check_expiring_documents,

    "status": status_action,
}


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def main():
    parser = SafeArgumentParser(description="ERPClaw HR Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Entity IDs
    parser.add_argument("--company-id")
    parser.add_argument("--employee-id")
    parser.add_argument("--department-id")
    parser.add_argument("--designation-id")
    parser.add_argument("--employee-grade-id")
    parser.add_argument("--leave-type-id")
    parser.add_argument("--leave-application-id")
    parser.add_argument("--expense-claim-id")
    parser.add_argument("--payment-entry-id")
    parser.add_argument("--holiday-list-id")
    parser.add_argument("--payroll-cost-center-id")
    parser.add_argument("--salary-structure-id")
    parser.add_argument("--leave-policy-id")
    parser.add_argument("--shift-id")
    parser.add_argument("--shift-type-id")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--start-time")
    parser.add_argument("--end-time")
    parser.add_argument("--attendance-device-id")
    parser.add_argument("--cost-center-id")

    # Employee fields
    parser.add_argument("--first-name")
    parser.add_argument("--last-name")
    parser.add_argument("--date-of-birth")
    parser.add_argument("--gender")
    parser.add_argument("--date-of-joining")
    parser.add_argument("--date-of-exit")
    parser.add_argument("--employment-type")
    parser.add_argument("--branch")
    parser.add_argument("--reporting-to")
    parser.add_argument("--company-email")
    parser.add_argument("--personal-email")
    parser.add_argument("--cell-phone")
    parser.add_argument("--emergency-contact")
    parser.add_argument("--bank-details")

    # Tax / payroll fields
    parser.add_argument("--federal-filing-status")
    parser.add_argument("--w4-allowances")
    parser.add_argument("--w4-additional-withholding")
    parser.add_argument("--state-filing-status")
    parser.add_argument("--state-withholding-allowances")
    parser.add_argument("--employee-401k-rate")
    parser.add_argument("--hsa-contribution")
    parser.add_argument("--is-exempt-from-fica")

    # Department / designation fields
    parser.add_argument("--name")
    parser.add_argument("--description")
    parser.add_argument("--parent-id")

    # Leave fields
    parser.add_argument("--max-days-allowed")
    parser.add_argument("--is-paid-leave")
    parser.add_argument("--is-carry-forward")
    parser.add_argument("--max-carry-forward-days")
    parser.add_argument("--is-compensatory")
    parser.add_argument("--applicable-after-days")
    parser.add_argument("--total-leaves")
    parser.add_argument("--fiscal-year")
    parser.add_argument("--half-day")
    parser.add_argument("--half-day-date")
    parser.add_argument("--reason")
    parser.add_argument("--approved-by")

    # Attendance fields
    parser.add_argument("--date")
    parser.add_argument("--shift")
    parser.add_argument("--check-in-time")
    parser.add_argument("--check-out-time")
    parser.add_argument("--working-hours")
    parser.add_argument("--late-entry")
    parser.add_argument("--early-exit")
    parser.add_argument("--source")

    # Bulk attendance
    parser.add_argument("--entries")

    # Holiday list fields
    parser.add_argument("--holidays")

    # Expense claim fields
    parser.add_argument("--expense-date")
    parser.add_argument("--items")

    # Lifecycle event fields
    parser.add_argument("--event-type")
    parser.add_argument("--event-date")
    parser.add_argument("--details")
    parser.add_argument("--old-values")
    parser.add_argument("--new-values")

    # Attendance regularization fields (Feature #22f)
    parser.add_argument("--late-threshold-minutes")
    parser.add_argument("--regularization-action")

    # Employee document fields (Feature #21)
    parser.add_argument("--document-id")
    parser.add_argument("--document-type")
    parser.add_argument("--document-name")
    parser.add_argument("--expiry-date")
    parser.add_argument("--notes")
    parser.add_argument("--days")

    # Filters
    parser.add_argument("--status")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")
    parser.add_argument("--search")

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
        sys.stderr.write(f"[erpclaw-hr] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
