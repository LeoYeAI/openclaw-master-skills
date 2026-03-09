"""Dependency checking utilities for ERPClaw skills.

Provides table-level dependency checking so skills gracefully degrade
when optional dependencies are not installed, and return helpful error
messages when required dependencies are missing.
"""
import os
import sqlite3
from typing import Optional


# Single source of truth: table name -> owning skill
TABLE_TO_SKILL = {
    # erpclaw-setup
    "company": "erpclaw-setup",
    "currency": "erpclaw-setup",
    "payment_terms": "erpclaw-setup",
    "payment_terms_detail": "erpclaw-setup",
    "uom": "erpclaw-setup",
    "uom_conversion": "erpclaw-setup",
    "audit_log": "erpclaw-setup",
    # erpclaw-gl
    "account": "erpclaw-gl",
    "gl_entry": "erpclaw-gl",
    "fiscal_year": "erpclaw-gl",
    "fiscal_year_period": "erpclaw-gl",
    "cost_center": "erpclaw-gl",
    "budget": "erpclaw-gl",
    "naming_series": "erpclaw-gl",
    # erpclaw-journals
    "journal_entry": "erpclaw-journals",
    "journal_entry_line": "erpclaw-journals",
    # erpclaw-payments
    "payment_entry": "erpclaw-payments",
    "payment_ledger_entry": "erpclaw-payments",
    # erpclaw-tax
    "tax_template": "erpclaw-tax",
    "tax_template_detail": "erpclaw-tax",
    "tax_rule": "erpclaw-tax",
    "tax_category": "erpclaw-tax",
    "tax_withholding_entry": "erpclaw-tax",
    # erpclaw-inventory
    "item": "erpclaw-inventory",
    "item_group": "erpclaw-inventory",
    "warehouse": "erpclaw-inventory",
    "stock_entry": "erpclaw-inventory",
    "stock_entry_item": "erpclaw-inventory",
    "stock_ledger_entry": "erpclaw-inventory",
    "batch": "erpclaw-inventory",
    "serial_number": "erpclaw-inventory",
    "price_list": "erpclaw-inventory",
    "item_price": "erpclaw-inventory",
    "pricing_rule": "erpclaw-inventory",
    "stock_reconciliation": "erpclaw-inventory",
    # erpclaw-selling
    "customer": "erpclaw-selling",
    "quotation": "erpclaw-selling",
    "quotation_item": "erpclaw-selling",
    "sales_order": "erpclaw-selling",
    "sales_order_item": "erpclaw-selling",
    "delivery_note": "erpclaw-selling",
    "delivery_note_item": "erpclaw-selling",
    "sales_invoice": "erpclaw-selling",
    "sales_invoice_item": "erpclaw-selling",
    "sales_invoice_tax": "erpclaw-selling",
    # erpclaw-buying
    "supplier": "erpclaw-buying",
    "material_request": "erpclaw-buying",
    "request_for_quotation": "erpclaw-buying",
    "purchase_order": "erpclaw-buying",
    "purchase_order_item": "erpclaw-buying",
    "purchase_receipt": "erpclaw-buying",
    "purchase_receipt_item": "erpclaw-buying",
    "purchase_invoice": "erpclaw-buying",
    "purchase_invoice_item": "erpclaw-buying",
    # erpclaw-manufacturing
    "bom": "erpclaw-manufacturing",
    "bom_item": "erpclaw-manufacturing",
    "work_order": "erpclaw-manufacturing",
    "job_card": "erpclaw-manufacturing",
    # erpclaw-hr
    "employee": "erpclaw-hr",
    "department": "erpclaw-hr",
    "designation": "erpclaw-hr",
    "leave_type": "erpclaw-hr",
    "leave_allocation": "erpclaw-hr",
    "leave_application": "erpclaw-hr",
    "attendance": "erpclaw-hr",
    "expense_claim": "erpclaw-hr",
    "holiday_list": "erpclaw-hr",
    # erpclaw-payroll
    "salary_component": "erpclaw-payroll",
    "salary_structure": "erpclaw-payroll",
    "salary_structure_detail": "erpclaw-payroll",
    "salary_assignment": "erpclaw-payroll",
    "payroll_run": "erpclaw-payroll",
    "salary_slip": "erpclaw-payroll",
    "salary_slip_detail": "erpclaw-payroll",
    "tax_config": "erpclaw-payroll",
    "tax_slab": "erpclaw-payroll",
    # erpclaw-projects
    "project": "erpclaw-projects",
    "task": "erpclaw-projects",
    "milestone": "erpclaw-projects",
    "timesheet": "erpclaw-projects",
    "timesheet_detail": "erpclaw-projects",
    # erpclaw-assets
    "asset_category": "erpclaw-assets",
    "asset": "erpclaw-assets",
    "depreciation_schedule": "erpclaw-assets",
    "asset_movement": "erpclaw-assets",
    # erpclaw-quality
    "inspection_template": "erpclaw-quality",
    "inspection_template_parameter": "erpclaw-quality",
    "quality_inspection": "erpclaw-quality",
    "quality_inspection_reading": "erpclaw-quality",
    "non_conformance": "erpclaw-quality",
    "quality_goal": "erpclaw-quality",
    # erpclaw-crm
    "lead": "erpclaw-crm",
    "lead_source": "erpclaw-crm",
    "opportunity": "erpclaw-crm",
    "campaign": "erpclaw-crm",
    "campaign_lead": "erpclaw-crm",
    "activity": "erpclaw-crm",
    # erpclaw-support
    "service_level_agreement": "erpclaw-support",
    "sla_priority": "erpclaw-support",
    "issue": "erpclaw-support",
    "warranty_claim": "erpclaw-support",
    "maintenance_schedule": "erpclaw-support",
    "maintenance_visit": "erpclaw-support",
    # erpclaw-billing
    "meter": "erpclaw-billing",
    "meter_reading": "erpclaw-billing",
    "usage_event": "erpclaw-billing",
    "rate_plan": "erpclaw-billing",
    "rate_tier": "erpclaw-billing",
    "billing_period": "erpclaw-billing",
    "billing_period_line": "erpclaw-billing",
    "billing_adjustment": "erpclaw-billing",
    "prepaid_credit": "erpclaw-billing",
    # erpclaw-ai-engine
    "anomaly": "erpclaw-ai-engine",
    "cash_flow_forecast": "erpclaw-ai-engine",
    "correlation": "erpclaw-ai-engine",
    "scenario": "erpclaw-ai-engine",
    "business_rule": "erpclaw-ai-engine",
    "categorization_rule": "erpclaw-ai-engine",
    "relationship_score": "erpclaw-ai-engine",
    "conversation_context": "erpclaw-ai-engine",
    "pending_decision": "erpclaw-ai-engine",
    "audit_conversation": "erpclaw-ai-engine",
}


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if a table exists in the database."""
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def check_required_tables(conn: sqlite3.Connection, tables: list) -> Optional[dict]:
    """Check that all required tables exist.

    Returns None if all present, or a JSON-ready error dict if any are missing.
    """
    missing = [t for t in tables if not table_exists(conn, t)]
    if not missing:
        return None

    skills_needed = set()
    for t in missing:
        skills_needed.add(TABLE_TO_SKILL.get(t, f"unknown (table: {t})"))

    if len(skills_needed) == 1:
        skill = skills_needed.pop()
        return {
            "error": f"This feature requires {skill}. Install it first.",
            "missing_skill": skill,
            "missing_tables": missing,
        }
    else:
        return {
            "error": f"This feature requires: {', '.join(sorted(skills_needed))}. Install them first.",
            "missing_skills": sorted(skills_needed),
            "missing_tables": missing,
        }


def check_optional_tables(conn: sqlite3.Connection, tables: list) -> dict:
    """Check which optional tables are available.

    Returns a dict mapping table name -> availability boolean.
    """
    return {t: table_exists(conn, t) for t in tables}


def skill_installed(conn: sqlite3.Connection, skill_name: str) -> bool:
    """Check if a skill's tables are available by probing its first table."""
    for tbl, owner in TABLE_TO_SKILL.items():
        if owner == skill_name:
            return table_exists(conn, tbl)
    return False


def resolve_skill_script(skill_name: str) -> Optional[str]:
    """Find the db_query.py path for a sibling skill.

    Checks standard deployment locations.
    """
    candidates = [
        os.path.expanduser(f"~/clawd/skills/{skill_name}/scripts/db_query.py"),
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))),
            skill_name, "scripts", "db_query.py",
        ),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def check_subprocess_target(
    conn: sqlite3.Connection,
    skill_name: str,
    representative_table: str,
) -> Optional[dict]:
    """Pre-flight check before making a subprocess call to another skill.

    Returns None if ready, or a JSON-ready error dict.
    """
    if not table_exists(conn, representative_table):
        return {
            "error": f"This feature requires {skill_name}. Install it first.",
            "missing_skill": skill_name,
        }
    script_path = resolve_skill_script(skill_name)
    if not script_path:
        return {
            "error": f"{skill_name} script not found on disk. Reinstall {skill_name}.",
            "missing_skill": skill_name,
        }
    return None
