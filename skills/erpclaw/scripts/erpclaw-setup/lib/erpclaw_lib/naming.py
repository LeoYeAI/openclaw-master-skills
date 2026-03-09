"""Naming series management for ERPClaw.

Generates sequential document numbers like INV-2026-00001.
Pattern: {PREFIX}{YEAR}-{SEQUENCE}

Each entity type has a unique prefix. The sequence counter is stored
in the `naming_series` table and incremented atomically per call.
"""
import uuid
import sqlite3
from datetime import datetime, timezone


# Maps entity type to its naming prefix
ENTITY_PREFIXES = {
    # erpclaw-setup
    "company": "COMP-",
    # erpclaw-gl
    "account": "ACC-",
    "fiscal_year": "FY-",
    "cost_center": "CC-",
    "period_closing_voucher": "PCV-",
    # erpclaw-journals
    "journal_entry": "JE-",
    "recurring_journal_template": "RJT-",
    # erpclaw-payments
    "payment_entry": "PAY-",
    # erpclaw-tax
    "tax_template": "TAX-",
    "tax_withholding_entry": "TWE-",
    # erpclaw-selling
    "quotation": "QTN-",
    "sales_order": "SO-",
    "delivery_note": "DN-",
    "sales_invoice": "INV-",
    "credit_note": "CN-",
    "recurring_invoice_template": "RIT-",
    # erpclaw-buying
    "material_request": "MR-",
    "request_for_quotation": "RFQ-",
    "purchase_order": "PO-",
    "purchase_receipt": "PR-",
    "purchase_invoice": "PINV-",
    "debit_note": "DBN-",
    # erpclaw-inventory
    "stock_entry": "STE-",
    "stock_reconciliation": "STR-",
    "stock_revaluation": "SREVAL-",
    # erpclaw-manufacturing
    "work_order": "WO-",
    "bom": "BOM-",
    "job_card": "JC-",
    "production_plan": "PP-",
    "subcontracting_order": "SCO-",
    # erpclaw-hr
    "employee": "EMP-",
    "salary_slip": "SS-",
    "payroll_run": "PRUN-",
    "expense_claim": "EC-",
    "leave_application": "LA-",
    # erpclaw-assets
    "asset": "AST-",
    # erpclaw-projects
    "project": "PRJ-",
    "task": "TSK-",
    "timesheet": "TS-",
    # erpclaw-quality
    "quality_inspection": "QC-",
    "non_conformance": "NC-",
    # erpclaw-crm
    "lead": "LEAD-",
    "opportunity": "OPP-",
    # erpclaw-support
    "issue": "ISS-",
    "warranty_claim": "WC-",
    "maintenance_schedule": "MS-",
    "maintenance_visit": "MV-",
    # erpclaw-billing
    "meter": "MTR-",
    # educlaw (core)
    "educlaw_student": "STU-",
    "educlaw_student_applicant": "STUAPP-",
    "educlaw_instructor": "INST-",
    "educlaw_program_enrollment": "PENR-",
    "educlaw_section": "SEC-",
    # educlaw-k12
    "educlaw_k12_iep": "IEP-",
    "educlaw_k12_504_plan": "504-",
    "educlaw_k12_sped_referral": "SPED-",
    "educlaw_k12_discipline_incident": "DISC-",
    # educlaw-statereport
    "SUB": "SUB-",
    "INC": "INC-",
    # PropertyClaw verticals
    "propertyclaw_property": "PROP-",
    "propertyclaw_unit": "UNIT-",
    "propertyclaw_lease": "LSE-",
    "propertyclaw_work_order": "PWO-",
    "propertyclaw_application": "APP-",
    "propertyclaw_inspection": "INSP-",
    "propertyclaw_trust_account": "TRUST-",
    "propertyclaw_owner_statement": "STMT-",
    "propertyclaw_security_deposit": "DEP-",
    # HealthClaw verticals
    "healthclaw_patient": "PAT-",
    "healthclaw_appointment": "APT-",
    "healthclaw_encounter": "ENC-",
    "healthclaw_prescription": "RX-",
    "healthclaw_lab_order": "LAB-",
    "healthclaw_claim": "CLM-",
    "healthclaw_referral": "REF-",
    # EduClaw additional
    "educlaw_enrollment": "ENR-",
    "educlaw_course": "CRS-",
    "educlaw_fee_invoice": "FEE-",
    # NonprofitClaw (nonprofit)
    "nonprofitclaw_donor": "DON-",
    "nonprofitclaw_donation": "DND-",
    "nonprofitclaw_fund": "FND-",
    "nonprofitclaw_fund_transfer": "FT-",
    "nonprofitclaw_grant": "GRT-",
    "nonprofitclaw_program": "NPG-",
    "nonprofitclaw_volunteer": "VOL-",
    "nonprofitclaw_pledge": "PLG-",
    "nonprofitclaw_campaign": "NPC-",
    "nonprofitclaw_tax_receipt": "NTR-",
    # HospitalityClaw (hospitality)
    "hospitalityclaw_room_type": "HRT-",
    "hospitalityclaw_room": "HRM-",
    "hospitalityclaw_guest": "GST-",
    "hospitalityclaw_reservation": "HRES-",
    "hospitalityclaw_group_block": "HGB-",
    "hospitalityclaw_folio_charge": "HFC-",
    "hospitalityclaw_housekeeping_task": "HHT-",
    "hospitalityclaw_rate_plan": "HRP-",
    "hospitalityclaw_outlet": "HOTL-",
    "hospitalityclaw_room_service_order": "HRSO-",
    # ConstructClaw
    "constructclaw_job": "CJOB-",
    "constructclaw_estimate": "CEST-",
    "constructclaw_bid": "CBID-",
    "constructclaw_subcontract": "CSC-",
    "constructclaw_daily_report": "CDR-",
    "constructclaw_pay_application": "CPA-",
    "constructclaw_rfi": "CRFI-",
    "constructclaw_submittal": "CSUB-",
    "constructclaw_pco": "CPCO-",
    "constructclaw_cco": "CCCO-",
    "constructclaw_incident": "CINC-",
    "constructclaw_retention": "CRET-",
    # FoodClaw
    "foodclaw_menu": "FMNU-",
    "foodclaw_menu_item": "FMI-",
    "foodclaw_recipe": "FRCP-",
    "foodclaw_ingredient": "FING-",
    "foodclaw_stock_count": "FSC-",
    "foodclaw_waste_log": "FWL-",
    "foodclaw_employee": "FEMP-",
    "foodclaw_shift": "FSFT-",
    "foodclaw_catering_event": "FCAT-",
    "foodclaw_haccp_log": "FHCP-",
    "foodclaw_inspection": "FINS-",
    "foodclaw_franchise_unit": "FFU-",
    # AutomotiveClaw
    "automotiveclaw_customer": "ACST-",
    "automotiveclaw_vehicle": "AVEH-",
    "automotiveclaw_deal": "ADEL-",
    "automotiveclaw_repair_order": "ARO-",
    "automotiveclaw_service_line": "ASL-",
    "automotiveclaw_warranty_claim": "AWC-",
    "automotiveclaw_part": "APRT-",
    "automotiveclaw_parts_order": "APO-",
    # AgricultureClaw
    "agricultureclaw_parcel": "AGPC-",
    "agricultureclaw_planting_plan": "AGPP-",
    "agricultureclaw_crop_type": "AGCT-",
    "agricultureclaw_field_operation": "AGFO-",
    "agricultureclaw_scouting_report": "AGSR-",
    "agricultureclaw_harvest_record": "AGHR-",
    "agricultureclaw_animal": "AGANL-",
    "agricultureclaw_health_record": "AGHLR-",
    "agricultureclaw_delivery_ticket": "AGDT-",
    # RetailClaw
    "retailclaw_price_list": "RPL-",
    "retailclaw_promotion": "RPRO-",
    "retailclaw_coupon": "RCPN-",
    "retailclaw_loyalty_program": "RLP-",
    "retailclaw_loyalty_member": "RLM-",
    "retailclaw_gift_card": "RGC-",
    "retailclaw_wholesale_order": "RWSO-",
    "retailclaw_return_authorization": "RRA-",
    # LegalClaw
    "legalclaw_client": "LCL-",
    "legalclaw_matter": "LMAT-",
    "legalclaw_time_entry": "LTE-",
    "legalclaw_expense": "LEXP-",
    "legalclaw_invoice": "LINV-",
    "legalclaw_trust_account": "LTA-",
    "legalclaw_document": "LDOC-",
    "legalclaw_calendar_event": "LCE-",
    "legalclaw_conflict_check": "LCC-",
    # Fleet addon
    "fleet_vehicle": "FV-",
    "fleet_fuel_log": "FFL-",
    "fleet_vehicle_maintenance": "FVM-",
    # Loans addon
    "loan_application": "LAPP-",
    "loan": "LN-",
    "loan_repayment": "LRP-",
    # POS addon
    "pos_profile": "POSP-",
    "pos_session": "POSS-",
    "pos_transaction": "POSTR-",
    # Treasury addon
    "cash_position": "CPOS-",
    "cash_forecast": "CFRC-",
    "investment": "INVST-",
    "inter_company_transfer": "ICT-",
    # Logistics addon
    "logistics_carrier": "LGCR-",
    "logistics_shipment": "LGSH-",
    "logistics_freight_charge": "LGFC-",
    # Maintenance addon
    "equipment": "EQP-",
    "maintenance_plan": "MNTP-",
    "maintenance_work_order": "MNTW-",
    "downtime_record": "MNDT-",
    # Alerts addon
    "alert_rule": "ALRT-",
    "alert_log": "ALLG-",
    # Approvals addon
    "approval_rule": "APRL-",
    "approval_request": "APRQ-",
    # Compliance addon
    "audit_plan": "AUDP-",
    "audit_finding": "AUDF-",
    "risk_register": "RISK-",
    "policy": "PLCY-",
    # Documents addon
    "document": "DOCU-",
    "document_template": "DOCT-",
    # E-Sign addon
    "esign_signature_request": "ESGN-",
    # Planning addon
    "planning_scenario": "PLSC-",
    "forecast": "FCST-",
    # Integrations addon
    "integration_connector": "INTC-",
    "integration_sync": "INTS-",
}


def register_prefix(entity_type: str, prefix: str):
    """Register a naming prefix for a vertical entity type.

    Verticals call this at import time or during init_db to register
    their naming prefixes without modifying shared lib source.

    Args:
        entity_type: e.g. 'propertyclaw_property', 'buildclaw_project'
        prefix: e.g. 'PROP-', 'BPRJ-'
    """
    ENTITY_PREFIXES[entity_type] = prefix


def get_next_name(conn: sqlite3.Connection, entity_type: str,
                  year: int = None, company_id: str = None) -> str:
    """Generate the next sequential name for an entity type.

    Uses the naming_series table to track and increment counters.
    The year is embedded in the stored prefix for annual resets.

    Thread-safe: uses SQLite's atomic INSERT OR UPDATE via UNIQUE
    constraint on (entity_type, prefix, company_id).

    Args:
        conn: SQLite connection (caller manages transaction).
        entity_type: Key from ENTITY_PREFIXES (e.g., "sales_invoice").
        year: Year for the series. Defaults to current year.
        company_id: Company ID. If conn has a company_id attribute
                    (e.g., TestDB), that is used as fallback.

    Returns:
        Formatted name like "INV-2026-00001".

    Raises:
        ValueError: If entity_type is not in ENTITY_PREFIXES.
    """
    if entity_type not in ENTITY_PREFIXES:
        raise ValueError(
            f"Unknown entity type '{entity_type}'. "
            f"Valid types: {sorted(ENTITY_PREFIXES.keys())}"
        )

    base_prefix = ENTITY_PREFIXES[entity_type]
    if year is None:
        year = datetime.now(timezone.utc).year

    # Resolve company_id from parameter or conn attribute
    if company_id is None:
        company_id = getattr(conn, "company_id", None)
    if not company_id:
        raise ValueError("company_id is required for naming series")

    # Store year-scoped prefix so annual reset is automatic
    year_prefix = f"{base_prefix}{year}-"
    entry_id = str(uuid.uuid4())

    # Atomic increment: INSERT if new, UPDATE if exists
    conn.execute(
        """
        INSERT INTO naming_series (id, entity_type, prefix, current_value, company_id)
        VALUES (?, ?, ?, 1, ?)
        ON CONFLICT(entity_type, prefix, company_id)
        DO UPDATE SET current_value = current_value + 1
        """,
        (entry_id, entity_type, year_prefix, company_id),
    )

    row = conn.execute(
        "SELECT current_value FROM naming_series WHERE entity_type = ? AND prefix = ? AND company_id = ?",
        (entity_type, year_prefix, company_id),
    ).fetchone()

    sequence = row[0]
    return f"{base_prefix}{year}-{sequence:05d}"


def parse_name(name: str) -> dict:
    """Parse a naming series string back to its components.

    Args:
        name: e.g., "INV-2026-00001"

    Returns:
        {"prefix": "INV-", "year": 2026, "sequence": 1}

    Raises:
        ValueError: If the name doesn't match the expected pattern.
    """
    parts = name.rsplit("-", 2)
    if len(parts) < 3:
        raise ValueError(f"Cannot parse name '{name}': expected PREFIX-YEAR-SEQUENCE")

    # Reconstruct prefix (everything before the last two segments)
    # Handle multi-part prefixes like "PINV-"
    sequence_str = parts[-1]
    year_str = parts[-2]
    prefix = name[: len(name) - len(year_str) - len(sequence_str) - 2] + "-"

    try:
        year = int(year_str)
        sequence = int(sequence_str)
    except ValueError:
        raise ValueError(f"Cannot parse name '{name}': year and sequence must be integers")

    return {"prefix": prefix, "year": year, "sequence": sequence}
