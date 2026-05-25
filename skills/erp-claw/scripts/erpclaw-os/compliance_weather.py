#!/usr/bin/env python3
"""ERPClaw OS — Compliance Weather

Calendar-driven validation strictness. Adjusts validation checks based on
the current compliance period:

  Normal:        Standard validation rules
  Year-End Close: Depreciation schedule, accrual reversal, adjustment checks
  Tax Season:     Enhanced tax categorization, expense classification
  Audit Season:   Full compliance documentation, GL reconciliation

Reads company fiscal year to determine current compliance period.
"""
import json
import os
import sqlite3
import time
from datetime import datetime, date

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")

# How many days before fiscal year end to activate year_end_close mode
YEAR_END_CLOSE_DAYS = 45

# Tax season: Jan 1 - Apr 15 for US calendar year companies
TAX_SEASON_START_MONTH = 1
TAX_SEASON_START_DAY = 1
TAX_SEASON_END_MONTH = 4
TAX_SEASON_END_DAY = 15


# ---------------------------------------------------------------------------
# Period Detection
# ---------------------------------------------------------------------------

def get_compliance_weather(company_id, db_path=None, reference_date=None):
    """Determine the current compliance period for a company.

    Args:
        company_id: Company UUID
        db_path: Path to SQLite database
        reference_date: Override current date (for testing). ISO format string or date object.

    Returns:
        dict with period_type, additional_checks, strictness_level, etc.
    """
    db_path = db_path or DEFAULT_DB_PATH

    if reference_date is None:
        today = date.today()
    elif isinstance(reference_date, str):
        today = date.fromisoformat(reference_date)
    else:
        today = reference_date

    # Try to load fiscal year from company record
    fiscal_year_end = _get_fiscal_year_end(company_id, db_path)
    if fiscal_year_end is None:
        # Default: calendar year (Dec 31)
        fiscal_year_end = date(today.year, 12, 31)

    # Determine period
    period_type = "normal"
    reasons = []

    # Check Year-End Close: within YEAR_END_CLOSE_DAYS of fiscal year end
    days_to_fy_end = (fiscal_year_end - today).days
    if 0 <= days_to_fy_end <= YEAR_END_CLOSE_DAYS:
        period_type = "year_end_close"
        reasons.append(f"Fiscal year ends {fiscal_year_end.isoformat()} "
                       f"({days_to_fy_end} days away)")
    elif days_to_fy_end < 0 and abs(days_to_fy_end) <= 15:
        # Just past fiscal year end — still in close mode
        period_type = "year_end_close"
        reasons.append(f"Fiscal year ended {fiscal_year_end.isoformat()} "
                       f"({abs(days_to_fy_end)} days ago, still in closing)")

    # Check Tax Season (US): Jan 1 - Apr 15
    tax_start = date(today.year, TAX_SEASON_START_MONTH, TAX_SEASON_START_DAY)
    tax_end = date(today.year, TAX_SEASON_END_MONTH, TAX_SEASON_END_DAY)
    if tax_start <= today <= tax_end:
        if period_type == "normal":
            period_type = "tax_season"
        reasons.append(f"US tax season ({tax_start.isoformat()} to {tax_end.isoformat()})")

    # Get additional checks for this period
    additional_checks = get_additional_checks(period_type)

    # Strictness level
    strictness_map = {
        "normal": 1,
        "tax_season": 2,
        "year_end_close": 3,
        "audit_season": 4,
    }

    return {
        "period_type": period_type,
        "strictness_level": strictness_map.get(period_type, 1),
        "additional_checks": additional_checks,
        "reasons": reasons,
        "reference_date": today.isoformat(),
        "fiscal_year_end": fiscal_year_end.isoformat(),
        "company_id": company_id,
    }


def get_additional_checks(period_type):
    """Get additional validation checks for a compliance period.

    Returns:
        list of check descriptors
    """
    if period_type == "year_end_close":
        return [
            {
                "check": "depreciation_schedule",
                "description": "Verify all fixed assets have up-to-date depreciation entries",
                "severity": "warning",
            },
            {
                "check": "accrual_reversal",
                "description": "Check for unreversed accrual entries from prior periods",
                "severity": "warning",
            },
            {
                "check": "year_end_adjustments",
                "description": "Verify year-end adjusting entries are recorded",
                "severity": "info",
            },
            {
                "check": "inventory_reconciliation",
                "description": "Verify physical inventory matches book inventory",
                "severity": "warning",
            },
        ]
    elif period_type == "tax_season":
        return [
            {
                "check": "tax_categorization",
                "description": "Verify all expenses have proper tax categorization",
                "severity": "warning",
            },
            {
                "check": "1099_reporting",
                "description": "Check vendor payments for 1099 reporting thresholds",
                "severity": "info",
            },
            {
                "check": "tax_deduction_documentation",
                "description": "Verify supporting documentation for claimed deductions",
                "severity": "info",
            },
        ]
    elif period_type == "audit_season":
        return [
            {
                "check": "full_gl_reconciliation",
                "description": "Complete GL reconciliation against bank statements",
                "severity": "critical",
            },
            {
                "check": "documentation_completeness",
                "description": "Verify all transactions have supporting documentation",
                "severity": "warning",
            },
            {
                "check": "internal_controls",
                "description": "Verify segregation of duties and approval chains",
                "severity": "warning",
            },
        ]
    else:
        # Normal mode — no additional checks
        return []


def _get_fiscal_year_end(company_id, db_path):
    """Load fiscal year end date from company record.

    Returns:
        date object or None if not found
    """
    if not os.path.isfile(db_path):
        return None

    try:
        conn = sqlite3.connect(db_path)
        # Check if company table has fiscal_year_end column
        columns = [r[1] for r in conn.execute("PRAGMA table_info('company')").fetchall()]
        if "fiscal_year_end" not in columns:
            conn.close()
            return None

        row = conn.execute(
            "SELECT fiscal_year_end FROM company WHERE id = ?",
            (company_id,),
        ).fetchone()
        conn.close()

        if row and row[0]:
            return date.fromisoformat(row[0])
    except (sqlite3.OperationalError, ValueError):
        pass

    return None


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def handle_compliance_weather_status(args):
    """CLI handler for compliance-weather-status action."""
    company_id = getattr(args, "company_id", None)
    db_path = getattr(args, "db_path", None)

    if not company_id:
        return {"error": "--company-id is required for compliance-weather-status"}

    result = get_compliance_weather(company_id, db_path=db_path)
    return result
