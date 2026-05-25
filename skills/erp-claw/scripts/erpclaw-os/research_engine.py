"""ERPClaw OS — Research Engine (P1-8)

Two-tier research system for business rules and ERP implementation patterns:

1. **KNOWLEDGE_BASE (runtime):** Built-in dictionary of common ERP business rules,
   regulatory standards, and implementation hints. Always available, zero latency.

2. **Web Search (dev-time only):** WebSearch/WebFetch deferred tools in the Claude
   Code environment. NOT available on the production OpenClaw server. Results are
   cached so the server can use them later.

Safety invariants:
- Research is DEV-TIME ONLY for web lookups. Server uses cached results.
- All returned data is advisory — never auto-applied to production code.
- Cache misses on the server return graceful not_found, never errors.
"""
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

# Make erpclaw-os package importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from pattern_library import PATTERNS
except ImportError:
    PATTERNS = {}


# ---------------------------------------------------------------------------
# Knowledge Base — 42 ERP business rules (22 core + 20 vertical)
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE = {
    "fifo_valuation": {
        "summary": "First In First Out: consume oldest stock layers first on outgoing transactions.",
        "source": "ASC 330 / IAS 2",
        "implementation_hints": (
            "Track stock layers with (posting_date, qty, rate). On outgoing, "
            "iterate oldest-first, deducting qty. Each consumed layer becomes a "
            "stock_ledger_entry with the layer's rate."
        ),
        "related_patterns": ["fifo_layer"],
    },
    "three_way_match": {
        "summary": "Validate: invoice_qty <= received_qty <= ordered_qty within tolerance.",
        "source": "Standard procurement best practice",
        "implementation_hints": (
            "On PI submit, query PO items and PR items, compare quantities. "
            "If abs(invoice_qty - received_qty) / ordered_qty > tolerance_pct, block submission."
        ),
        "related_patterns": ["three_way_match"],
    },
    "overtime_flsa": {
        "summary": (
            "Federal: 1.5x regular rate after 40 hours/week. "
            "California: also 1.5x after 8 hours/day, 2x after 12 hours/day."
        ),
        "source": "Fair Labor Standards Act (FLSA), 29 USC \u00a7207",
        "implementation_hints": (
            "Track hours per week. Calculate: regular_hours = min(hours, 40), "
            "ot_hours = max(0, hours - 40). OT rate = regular_rate * 1.5."
        ),
        "related_patterns": [],
    },
    "nacha_ach": {
        "summary": (
            "NACHA file format for ACH direct deposit. Fixed-width records: "
            "File Header (1), Batch Header (5), Entry Detail (6), "
            "Batch Control (8), File Control (9)."
        ),
        "source": "NACHA Operating Rules",
        "implementation_hints": (
            "Generate fixed-width text file. Record type 1 (file header), "
            "5 (batch header), 6 (entry detail per employee), "
            "8 (batch control), 9 (file control). 94-character lines."
        ),
        "related_patterns": [],
    },
    "blanket_orders": {
        "summary": (
            "Long-term purchase agreement with a total qty/amount. Individual POs "
            "draw down from the blanket. When fully consumed, blanket is closed."
        ),
        "source": "Standard procurement practice, SAP ME31K/ME21N",
        "implementation_hints": (
            "Track total_qty and fulfilled_qty. On each PO referencing the blanket, "
            "increment fulfilled_qty. When fulfilled_qty >= total_qty, set status='closed'."
        ),
        "related_patterns": ["blanket_agreement"],
    },
    "document_close": {
        "summary": (
            "Close a document (SO, PO, etc.) to prevent further transactions against it. "
            "Closing is reversible (reopen). Differs from cancel which is permanent."
        ),
        "source": "Standard ERP workflow pattern",
        "implementation_hints": (
            "Add close_date, close_reason, closed_by columns. On close, set status='closed'. "
            "On reopen, clear close_date and set status back to previous state."
        ),
        "related_patterns": ["document_close"],
    },
    "document_amendment": {
        "summary": (
            "Create a new version of a submitted document. Original is frozen, "
            "amendment carries forward all data with amendment_number incremented."
        ),
        "source": "ERPNext document amendment model",
        "implementation_hints": (
            "Copy original row, set original_id = parent.id, increment amendment_number. "
            "Mark original status='amended'. New row starts as draft."
        ),
        "related_patterns": ["document_amendment"],
    },
    "recurring_billing": {
        "summary": (
            "Auto-generate invoices on a schedule (monthly, quarterly, annually). "
            "Template defines items, frequency, start/end dates."
        ),
        "source": "Standard SaaS/subscription billing practice",
        "implementation_hints": (
            "Store template with frequency and next_date. Cron job queries templates "
            "where next_date <= today, generates invoice via cross_skill, advances next_date."
        ),
        "related_patterns": ["recurring_template"],
    },
    "multi_uom": {
        "summary": (
            "Items can be stocked and sold in different units of measure. "
            "Conversion factors between UOMs must be maintained."
        ),
        "source": "Standard inventory management",
        "implementation_hints": (
            "Create uom_conversion table: item_id, from_uom, to_uom, conversion_factor. "
            "On stock/sales transactions, convert to base UOM for ledger entries."
        ),
        "related_patterns": [],
    },
    "item_variants": {
        "summary": (
            "Items can have variants (size, color, material). Variants share base "
            "properties but override specific attributes."
        ),
        "source": "Standard product management",
        "implementation_hints": (
            "item_variant table: id, template_item_id, attribute_values (JSON). "
            "Inherit price, description from template. Override per-variant as needed."
        ),
        "related_patterns": [],
    },
    "stock_projected_qty": {
        "summary": (
            "Projected qty = actual_qty + ordered_qty - reserved_qty - planned_qty. "
            "Shows future availability considering open POs and pending SOs."
        ),
        "source": "MRP standard calculation",
        "implementation_hints": (
            "Query: sum stock_ledger actual_qty, sum open PO items ordered_qty, "
            "sum open SO items reserved_qty. Projected = actual + ordered - reserved."
        ),
        "related_patterns": [],
    },
    "material_substitution": {
        "summary": (
            "Allow substituting one raw material for another in manufacturing. "
            "Substitute must meet quality specs and have sufficient stock."
        ),
        "source": "Manufacturing BOM management",
        "implementation_hints": (
            "Create material_substitute table: original_item_id, substitute_item_id, "
            "priority, conversion_factor. On stock shortage, suggest substitutes ordered by priority."
        ),
        "related_patterns": [],
    },
    "co_products": {
        "summary": (
            "Manufacturing process produces multiple outputs from one BOM. "
            "Each co-product has a cost allocation percentage."
        ),
        "source": "Process manufacturing (chemical, food, petroleum)",
        "implementation_hints": (
            "Extend BOM with co_product table: bom_id, item_id, qty, cost_pct. "
            "Sum of cost_pct must equal 100. On manufacture, create stock entries for all co-products."
        ),
        "related_patterns": [],
    },
    "make_vs_buy": {
        "summary": (
            "Decision framework: manufacture in-house or purchase from supplier. "
            "Based on cost comparison, capacity, lead time."
        ),
        "source": "Manufacturing planning practice",
        "implementation_hints": (
            "For each item, store make_cost and buy_cost. Planning engine compares "
            "and suggests make/buy. Override possible per planning run."
        ),
        "related_patterns": [],
    },
    "grn_tolerance": {
        "summary": (
            "Goods Receipt Note: accept over/under delivery within tolerance percentage. "
            "Outside tolerance requires approval."
        ),
        "source": "Standard procurement QA",
        "implementation_hints": (
            "On GRN submit, compare received_qty to PO qty. If abs(received - ordered) / ordered "
            "> tolerance_pct (default 5%), require approval or reject."
        ),
        "related_patterns": ["three_way_match"],
    },
    "shift_management": {
        "summary": (
            "Define work shifts (morning, afternoon, night). Assign employees to shifts. "
            "Track shift changes, shift differentials (pay premium)."
        ),
        "source": "Standard HR/workforce management",
        "implementation_hints": (
            "Create shift_type table (id, name, start_time, end_time, differential_rate). "
            "shift_assignment table (employee_id, shift_type_id, date). "
            "Payroll multiplies base rate by differential_rate for non-standard shifts."
        ),
        "related_patterns": [],
    },
    "multi_state_payroll": {
        "summary": (
            "Employees may work in multiple US states. Each state has its own income tax "
            "withholding rules, unemployment tax, and disability insurance."
        ),
        "source": "US state tax codes (varies by state)",
        "implementation_hints": (
            "Track work_state per pay period. Apply state-specific tax tables. "
            "Handle reciprocity agreements between states. "
            "SUI rates vary by employer experience rating."
        ),
        "related_patterns": [],
    },
    "supplemental_wages": {
        "summary": (
            "Bonuses, commissions, overtime premiums taxed differently than regular wages. "
            "Federal flat rate: 22% (or 37% above $1M)."
        ),
        "source": "IRS Publication 15, Section 7",
        "implementation_hints": (
            "Categorize each earning type as regular or supplemental. "
            "Apply flat 22% federal withholding to supplemental earnings, "
            "or aggregate method if employer chooses."
        ),
        "related_patterns": [],
    },
    "retro_pay": {
        "summary": (
            "Retroactive pay adjustment when a pay raise is effective before "
            "current pay period. Calculate difference for past periods."
        ),
        "source": "Standard payroll practice",
        "implementation_hints": (
            "Query past pay periods from effective_date. For each period, "
            "compute difference = (new_rate - old_rate) * hours. "
            "Add as supplemental earning in current payroll."
        ),
        "related_patterns": [],
    },
    "leave_carry_forward": {
        "summary": (
            "Unused leave balance carries forward to next year, subject to caps. "
            "Some leave types expire (use-it-or-lose-it), others accumulate."
        ),
        "source": "Standard HR leave policy",
        "implementation_hints": (
            "On fiscal year rollover, query leave_balance per employee and leave_type. "
            "Apply carry_forward_max from leave_type config. "
            "Excess is forfeited. Create new leave_allocation for carried amount."
        ),
        "related_patterns": [],
    },
    "depreciation_straight_line": {
        "summary": (
            "Asset cost spread evenly over useful life. "
            "Monthly depreciation = (cost - salvage_value) / (useful_life_months)."
        ),
        "source": "ASC 360 / IAS 16",
        "implementation_hints": (
            "On asset submit, calculate monthly_depreciation. "
            "Monthly cron posts GL: Dr Depreciation Expense, Cr Accumulated Depreciation. "
            "Track accumulated_depreciation on the asset record."
        ),
        "related_patterns": [],
    },
    "bank_reconciliation": {
        "summary": (
            "Match bank statement lines to GL journal entries. "
            "Unmatched items are either missing entries or bank errors."
        ),
        "source": "Standard accounting practice",
        "implementation_hints": (
            "Import bank statement lines (date, description, amount, reference). "
            "Auto-match by reference number and amount. Manual match for unmatched. "
            "Reconciled entries update clearance_date on payment/journal entry."
        ),
        "related_patterns": [],
    },
    # --- Healthcare vertical rules ---
    "insurance_payer_registry": {
        "summary": (
            "Each insurance payer has a unique EDI Payer ID (5-digit, assigned by "
            "CMS/clearinghouse). Payers have separate claims vs correspondence addresses. "
            "Each payer has timely filing limits (30-365 days). ERA enrollment status must "
            "be tracked. Fee schedules are payer-specific with contracted rates per CPT."
        ),
        "source": "CMS / HIPAA X12 EDI standards",
        "implementation_hints": (
            "Create payer table with edi_payer_id (5-digit TEXT), name, claims_address, "
            "correspondence_address, timely_filing_days, era_enrolled (BOOLEAN), "
            "era_enrollment_date. Fee schedule child table: payer_id, cpt_code, "
            "contracted_rate (TEXT/Decimal), effective_date, expiry_date."
        ),
        "related_patterns": [],
    },
    "insurance_eligibility_verification": {
        "summary": (
            "Verify coverage before every patient visit. Record copay, deductible "
            "(amount + met), coinsurance %, out-of-pocket max, plan dates, in-network "
            "status, prior auth requirements. Eligibility is a point-in-time snapshot, "
            "not a permanent state."
        ),
        "source": "HIPAA X12 270/271 Eligibility Transaction",
        "implementation_hints": (
            "Create eligibility_check table: patient_id, payer_id, check_date, "
            "copay (TEXT/Decimal), deductible_total, deductible_met, coinsurance_pct, "
            "oop_max, plan_start, plan_end, in_network (BOOLEAN), prior_auth_required "
            "(BOOLEAN), verified_by, verification_method (phone/portal/EDI)."
        ),
        "related_patterns": [],
    },
    "claim_scrubbing_pre_submission": {
        "summary": (
            "Validate before submission: NPI format (10-digit Luhn check), at least one "
            "ICD-10 diagnosis, each CPT has diagnosis pointer, valid CMS modifier codes, "
            "no duplicate claims (same patient + payer + date + CPT), timely filing check "
            "against payer limit."
        ),
        "source": "CMS-1500 / UB-04 claim standards, HIPAA X12 837",
        "implementation_hints": (
            "Pre-submit validation function checks: (1) NPI Luhn-10, (2) len(diagnoses) >= 1, "
            "(3) each line has dx_pointer into claim diagnoses, (4) modifier in CMS modifier "
            "table, (5) no existing claim with same patient+payer+dos+cpt, (6) service_date "
            "+ payer.timely_filing_days >= today. Return list of errors; block if any."
        ),
        "related_patterns": [],
    },
    "era_835_electronic_remittance": {
        "summary": (
            "ERA/835 is an EDI format for electronic payment explanation. Contains "
            "check/EFT number, payer, claim-level detail (billed/allowed/paid/adjusted "
            "amounts), CAS adjustment codes (CO/PR/OA/PI groups), CARC reason codes, "
            "RARC remark codes. Auto-posting matches ERA claims to submitted claims by "
            "claim number."
        ),
        "source": "HIPAA X12 835 Health Care Claim Payment/Advice",
        "implementation_hints": (
            "Parse 835 EDI file into era_header (check_number, payer_id, payment_amount, "
            "payment_date) and era_line (claim_number, billed_amount, allowed_amount, "
            "paid_amount, patient_responsibility). CAS segments become era_adjustment "
            "rows (group_code CO/PR/OA/PI, reason_code CARC, remark_code RARC, amount). "
            "Auto-post: match era_line.claim_number to claim.id, apply payment."
        ),
        "related_patterns": [],
    },
    "denial_management_workflow": {
        "summary": (
            "Denials categorized by CAS group codes: CO (Contractual Obligation), "
            "PR (Patient Responsibility), OA (Other Adjustment), PI (Payer Initiated). "
            "Each denial has a CARC code (reason) and optional RARC (remark). Appeals "
            "must be filed within payer-specific deadline (30-365 days). Track appeal "
            "submission, reference number, outcome (overturned/upheld/partial)."
        ),
        "source": "X12 CAS segment / WPC CARC-RARC code sets",
        "implementation_hints": (
            "Create denial table: claim_id, cas_group (CO/PR/OA/PI), carc_code, "
            "rarc_code, denied_amount, denial_date. Appeal child table: denial_id, "
            "appeal_date, appeal_deadline, reference_number, supporting_docs, "
            "outcome (overturned/upheld/partial), outcome_date, recovered_amount."
        ),
        "related_patterns": [],
    },
    "hipaa_phi_access_audit": {
        "summary": (
            "45 C.F.R. 164.312(b) requires audit controls recording who accessed PHI, "
            "when, from where, what action (view/edit/print/export/delete), which "
            "patient's data, and what data category. Break-the-glass access must log "
            "access reason. Audit logs must be retained minimum 6 years."
        ),
        "source": "HIPAA Security Rule, 45 C.F.R. 164.312(b)",
        "implementation_hints": (
            "Create phi_access_log table: id, user_id, patient_id, access_timestamp, "
            "action (view/edit/print/export/delete), data_category, ip_address, "
            "is_break_glass (BOOLEAN), break_glass_reason, session_id. "
            "Immutable — no UPDATE/DELETE allowed. Retention: 6+ years. "
            "Index on patient_id + access_timestamp for audit queries."
        ),
        "related_patterns": [],
    },
    "good_faith_estimate_no_surprises_act": {
        "summary": (
            "No Surprises Act (2022) requires Good Faith Estimates for uninsured/self-pay "
            "patients. Must provide itemized estimate of expected charges for scheduled "
            "services within 1 business day of scheduling (3 days for services 3+ days out). "
            "Includes all expected items/services, CPT codes, diagnosis codes, expected "
            "charges, facility fees, provider information."
        ),
        "source": "No Surprises Act, Pub.L. 116-260 (2022)",
        "implementation_hints": (
            "Create good_faith_estimate table: id, patient_id, appointment_id, "
            "estimate_date, total_estimated_charge, provider_npi, facility_name. "
            "Child table gfe_line: gfe_id, cpt_code, description, expected_charge, "
            "diagnosis_code, facility_fee. Must be generated within 1 business day "
            "of scheduling. Track delivery method and patient acknowledgment."
        ),
        "related_patterns": [],
    },
    "mips_quality_measures": {
        "summary": (
            "CMS Merit-based Incentive Payment System. 4 categories: Quality (45%), "
            "Promoting Interoperability (25%), Improvement Activities (15%), Cost (15%). "
            "Non-reporting = up to -9% Medicare payment adjustment. Top 10 measures "
            "include: preventive care (screening), chronic disease management (diabetes "
            "HbA1c, hypertension BP), tobacco screening, BMI screening, depression screening."
        ),
        "source": "CMS MIPS (42 C.F.R. Part 414)",
        "implementation_hints": (
            "Create mips_measure table: measure_id, title, category (quality/pi/ia/cost), "
            "description, numerator_criteria, denominator_criteria. "
            "mips_patient_measure: patient_id, measure_id, reporting_period, "
            "denominator_eligible (BOOLEAN), numerator_met (BOOLEAN), exclusion_reason. "
            "Calculate performance rate = numerator_met / denominator_eligible per measure."
        ),
        "related_patterns": [],
    },
    # --- Education vertical rules ---
    "parent_portal_ferpa": {
        "summary": (
            "FERPA (20 U.S.C. \u00a7 1232g) grants parents right to inspect all education "
            "records of children under 18. Schools must authenticate parent identity before "
            "granting access. Directory information may be disclosed without consent. "
            "Discipline details may be redacted per state law. Access transfers to student "
            "at age 18 or postsecondary enrollment. All access must be logged for FERPA "
            "audit trail."
        ),
        "source": "FERPA, 20 U.S.C. \u00a7 1232g / 34 C.F.R. Part 99",
        "implementation_hints": (
            "Create parent_portal_access table: parent_id, student_id, relationship, "
            "verified (BOOLEAN), verification_date, access_level (full/directory_only). "
            "ferpa_access_log: parent_id, student_id, record_type, access_timestamp, "
            "action. Check student age >= 18 to revoke parent access. "
            "Directory info opt-out flag on student record."
        ),
        "related_patterns": [],
    },
    "nslp_school_lunch_program": {
        "summary": (
            "USDA National School Lunch Program: 3 eligibility tiers (free: \u2264130% FPL, "
            "reduced: 131-185% FPL, paid: >185% FPL). Direct certification via SNAP/TANF. "
            "Daily meal counts required by category. Federal reimbursement rates (2025-26): "
            "free lunch ~$4.36, reduced ~$3.96, paid ~$0.53. Monthly USDA claim submission "
            "required. Schools must track allergens and dietary restrictions."
        ),
        "source": "USDA NSLP (42 U.S.C. \u00a7 1751 et seq.)",
        "implementation_hints": (
            "Create meal_eligibility table: student_id, tier (free/reduced/paid), "
            "determination_method (application/direct_cert), effective_date, expiry_date. "
            "daily_meal_count: school_id, date, free_count, reduced_count, paid_count. "
            "student_allergen: student_id, allergen, dietary_restriction. "
            "Monthly claim = sum(daily counts * reimbursement rates per tier)."
        ),
        "related_patterns": [],
    },
    "school_transportation_management": {
        "summary": (
            "Second largest K-12 expense after salaries. Routes must be planned "
            "considering: student addresses, school bell times, bus capacity, maximum "
            "ride time, special needs students, parent pickup zones. NTSB safety "
            "requirements for school buses. States regulate maximum ride times "
            "(typically 45-60 minutes)."
        ),
        "source": "NTSB school bus safety / state DOE transportation regs",
        "implementation_hints": (
            "Create bus_route table: id, route_number, school_id, driver_id, bus_id, "
            "start_time, estimated_duration, max_capacity. bus_stop: route_id, "
            "stop_order, address, lat, lng, estimated_arrival. student_route: "
            "student_id, route_id, stop_id, special_needs (BOOLEAN), "
            "special_needs_notes. Track actual vs planned times for compliance."
        ),
        "related_patterns": [],
    },
    # --- Construction vertical rules ---
    "davis_bacon_prevailing_wage": {
        "summary": (
            "Davis-Bacon Act (40 U.S.C. \u00a7\u00a7 3141-3148) applies to federal contracts "
            ">$2,000. Contractors must pay locally prevailing wages per trade classification. "
            "Wage determinations issued by DOL (number format: ST-YYYY-NNNN). WH-347 "
            "certified payroll form required weekly. Overtime at 1.5x basic hourly (fringe "
            "stays flat). Fringe can be paid as cash or to bona fide plan. Apprentice rates "
            "based on registered apprenticeship program ratios."
        ),
        "source": "Davis-Bacon Act, 40 U.S.C. \u00a7\u00a7 3141-3148",
        "implementation_hints": (
            "Create wage_determination table: wd_number (ST-YYYY-NNNN), county, state, "
            "construction_type, effective_date. wage_rate child: wd_id, trade_classification, "
            "basic_hourly (TEXT/Decimal), fringe_hourly (TEXT/Decimal). On payroll, look up "
            "project.wd_number, match employee trade, enforce minimum rate. "
            "Apprentice ratio from apprenticeship_program table."
        ),
        "related_patterns": [],
    },
    "certified_payroll_wh_347": {
        "summary": (
            "WH-347 Payroll form fields: contractor name, address, payroll number, week "
            "ending date, project name, contract number. Per-employee row: name, last 4 SSN, "
            "work classification, hours per day (Mon-Sun), total hours, rate of pay "
            "(basic + fringe), gross amount earned, itemized deductions, net wages paid. "
            "Page 2: Statement of Compliance signed under penalty of perjury."
        ),
        "source": "DOL WH-347 form / Davis-Bacon Act",
        "implementation_hints": (
            "Create certified_payroll table: id, project_id, contractor_id, payroll_number, "
            "week_ending, status (draft/signed/submitted). certified_payroll_line: "
            "payroll_id, employee_id, last4_ssn, classification, hours_mon through hours_sun, "
            "total_hours, basic_rate, fringe_rate, gross_earned, deductions_json, "
            "net_wages. Generate WH-347 PDF with compliance statement."
        ),
        "related_patterns": [],
    },
    "construction_equipment_scheduling": {
        "summary": (
            "Equipment assigned to projects with daily/hourly rates. Mobilization cost "
            "(transport to site) and demobilization cost (return). Track utilization rate "
            "(hours used / hours available). Prevent double-booking across projects. "
            "Equipment categories: cranes, excavators, loaders, concrete equipment, "
            "scaffolding, generators."
        ),
        "source": "Standard construction equipment management",
        "implementation_hints": (
            "Create equipment table: id, name, category, daily_rate, hourly_rate, "
            "mobilization_cost, status (available/assigned/maintenance). "
            "equipment_assignment: equipment_id, project_id, start_date, end_date, "
            "mob_cost, demob_cost. Check for overlapping assignments before booking. "
            "equipment_usage_log: assignment_id, date, hours_used. "
            "Utilization = sum(hours_used) / total_available_hours."
        ),
        "related_patterns": [],
    },
    # --- Property Management vertical rules ---
    "property_trust_accounting": {
        "summary": (
            "Most US states require separate trust/escrow accounts for tenant security "
            "deposits. Funds cannot be commingled with operating funds. Interest earned "
            "may belong to tenant (varies by state). Monthly reconciliation legally "
            "mandated in most states. Upon move-out: itemized deduction statement within "
            "state-specific deadline (14-60 days). Improper handling = 2-3x damages in "
            "many jurisdictions."
        ),
        "source": "State landlord-tenant statutes (varies by state)",
        "implementation_hints": (
            "Create trust_account table: id, bank_name, account_number, account_type "
            "(security_deposit/escrow), property_id. trust_ledger: trust_account_id, "
            "tenant_id, lease_id, transaction_type (deposit/refund/deduction/interest), "
            "amount, date, description. Monthly reconciliation: bank balance = "
            "sum(trust_ledger). Move-out: generate itemized deduction statement "
            "within state deadline. NEVER comingle with operating GL."
        ),
        "related_patterns": [],
    },
    "rubs_utility_billing": {
        "summary": (
            "Ratio Utility Billing System allocates shared utility costs to tenants. "
            "Common allocation bases: square footage, occupancy count, equal split, or "
            "actual sub-metered usage. Common utilities: water, sewer, trash, gas, "
            "electric. Owner typically marks up 3-10% for administrative costs. Billing "
            "must be transparent with allocation methodology disclosed to tenants."
        ),
        "source": "Standard property management practice / state utility billing regs",
        "implementation_hints": (
            "Create utility_bill table: id, property_id, utility_type, billing_period, "
            "total_amount, admin_markup_pct. rubs_allocation: utility_bill_id, unit_id, "
            "tenant_id, allocation_base (sqft/occupancy/equal/metered), base_value, "
            "allocated_amount, markup_amount, total_charge. Sum of allocated_amount "
            "must equal utility_bill.total_amount. Generate tenant charge lines."
        ),
        "related_patterns": [],
    },
    # --- Retail vertical rules ---
    "multi_location_retail_inventory": {
        "summary": (
            "Each store/warehouse maintains independent stock levels. Inter-store "
            "transfers create stock_entry of type 'transfer'. Reorder points are "
            "per-item per-location. Central distribution center replenishes stores. "
            "Real-time inventory sync across POS, e-commerce, and warehouse. Shrinkage "
            "tracked by location and cause (theft, damage, spoilage, administrative error)."
        ),
        "source": "Standard multi-location retail inventory management",
        "implementation_hints": (
            "Extend item_warehouse with location_id (store/warehouse). Reorder_point "
            "table: item_id, location_id, reorder_level, reorder_qty. stock_entry "
            "type='transfer' moves between locations (source_location, target_location). "
            "shrinkage_log: item_id, location_id, qty, cause (theft/damage/spoilage/admin), "
            "date, reported_by. POS/ecom sync via inventory_sync_log."
        ),
        "related_patterns": [],
    },
    "ecommerce_omnichannel_sync": {
        "summary": (
            "Product catalog sync: push items (name, description, price, images, SKU) to "
            "channels (Shopify, WooCommerce, Amazon). Inventory sync: push available "
            "quantity per location. Order import: pull orders from channels into ERP as "
            "sales orders. Fulfillment: mark shipped with tracking number, sync back to "
            "channel. Price consistency across channels unless channel-specific pricing "
            "configured."
        ),
        "source": "Standard omnichannel retail practice",
        "implementation_hints": (
            "Create sales_channel table: id, name, platform (shopify/woocommerce/amazon), "
            "api_key, api_url, sync_enabled. channel_listing: item_id, channel_id, "
            "remote_id, listed_price, channel_specific_price, sync_status. "
            "channel_order: channel_id, remote_order_id, sales_order_id, import_date. "
            "Sync engine: push catalog/inventory changes, pull orders on schedule."
        ),
        "related_patterns": [],
    },
    # --- Legal vertical rules ---
    "ledes_1998b_format": {
        "summary": (
            "LEDES 1998B is pipe-delimited. Header: LEDES1998B[]. Each line ends with []. "
            "Invoice header fields: INVOICE_DATE|INVOICE_NUMBER|CLIENT_ID|"
            "LAW_FIRM_MATTER_ID|INVOICE_TOTAL|BILLING_START_DATE|BILLING_END_DATE|"
            "LAW_FIRM_ID|LAW_FIRM_NAME|CLIENT_MATTER_ID[]. Line items: "
            "LINE_ITEM_NUMBER|EXP/FEE/INV_ADJ_TYPE|LINE_ITEM_NUMBER_OF_UNITS|"
            "LINE_ITEM_UNIT_COST|LINE_ITEM_TOTAL|LINE_ITEM_DATE|LINE_ITEM_TASK_CODE|"
            "LINE_ITEM_EXPENSE_CODE|LINE_ITEM_ACTIVITY_CODE|TIMEKEEPER_ID|"
            "LINE_ITEM_DESCRIPTION[]. Dates: YYYYMMDD. Amounts: no currency symbol, "
            "2 decimals."
        ),
        "source": "LEDES Oversight Committee / LEDES.org",
        "implementation_hints": (
            "Generate pipe-delimited text file. First line: LEDES1998B[]. "
            "Header line with invoice-level fields ending with []. "
            "One line per fee/expense item ending with []. "
            "Parse incoming LEDES: split on |, strip [], validate field counts. "
            "Map UTBMS task/activity/expense codes to internal categories."
        ),
        "related_patterns": [],
    },
    "iolta_trust_accounting": {
        "summary": (
            "Interest on Lawyers Trust Accounts: client funds held in trust must be in "
            "IOLTA accounts. Funds cannot be commingled with firm operating funds. Every "
            "deposit and disbursement must be traceable to a specific client/matter. "
            "Three-way reconciliation: bank statement vs trust ledger vs client ledger. "
            "Interest earned on pooled accounts goes to state bar foundation."
        ),
        "source": "ABA Model Rule 1.15 / State bar IOLTA rules",
        "implementation_hints": (
            "Create iolta_account table: id, bank_name, account_number, bar_state. "
            "iolta_ledger: iolta_account_id, client_id, matter_id, transaction_type "
            "(deposit/disbursement/transfer), amount, date, description, check_number. "
            "Three-way recon: (1) bank balance, (2) sum(iolta_ledger), (3) sum per "
            "client_id. All three must agree. Interest auto-allocated to bar foundation. "
            "NEVER comingle with firm operating accounts."
        ),
        "related_patterns": [],
    },
}

# Canonical name aliases — maps search terms to KNOWLEDGE_BASE keys
_ALIASES = {
    "fifo": "fifo_valuation",
    "first in first out": "fifo_valuation",
    "fifo inventory": "fifo_valuation",
    "fifo inventory valuation": "fifo_valuation",
    "three way match": "three_way_match",
    "3 way match": "three_way_match",
    "3-way match": "three_way_match",
    "three-way match": "three_way_match",
    "overtime": "overtime_flsa",
    "flsa": "overtime_flsa",
    "flsa overtime": "overtime_flsa",
    "flsa overtime rules": "overtime_flsa",
    "ach": "nacha_ach",
    "nacha": "nacha_ach",
    "nacha ach file format": "nacha_ach",
    "ach file": "nacha_ach",
    "blanket": "blanket_orders",
    "blanket order": "blanket_orders",
    "blanket purchase order": "blanket_orders",
    "framework agreement": "blanket_orders",
    "close": "document_close",
    "document close": "document_close",
    "close document": "document_close",
    "amendment": "document_amendment",
    "document amendment": "document_amendment",
    "amend": "document_amendment",
    "recurring": "recurring_billing",
    "recurring billing": "recurring_billing",
    "recurring invoice": "recurring_billing",
    "subscription billing": "recurring_billing",
    "multi uom": "multi_uom",
    "unit of measure": "multi_uom",
    "uom conversion": "multi_uom",
    "item variant": "item_variants",
    "item variants": "item_variants",
    "product variant": "item_variants",
    "projected qty": "stock_projected_qty",
    "projected quantity": "stock_projected_qty",
    "available qty": "stock_projected_qty",
    "material substitute": "material_substitution",
    "material substitution": "material_substitution",
    "alternate material": "material_substitution",
    "co product": "co_products",
    "co-product": "co_products",
    "by-product": "co_products",
    "make or buy": "make_vs_buy",
    "make vs buy": "make_vs_buy",
    "grn tolerance": "grn_tolerance",
    "goods receipt tolerance": "grn_tolerance",
    "over delivery": "grn_tolerance",
    "shift": "shift_management",
    "shift management": "shift_management",
    "work shift": "shift_management",
    "multi state payroll": "multi_state_payroll",
    "state tax": "multi_state_payroll",
    "state withholding": "multi_state_payroll",
    "supplemental wage": "supplemental_wages",
    "supplemental wages": "supplemental_wages",
    "bonus tax": "supplemental_wages",
    "retro pay": "retro_pay",
    "retroactive pay": "retro_pay",
    "back pay": "retro_pay",
    "leave carry forward": "leave_carry_forward",
    "leave rollover": "leave_carry_forward",
    "pto rollover": "leave_carry_forward",
    "depreciation": "depreciation_straight_line",
    "straight line depreciation": "depreciation_straight_line",
    "asset depreciation": "depreciation_straight_line",
    "bank reconciliation": "bank_reconciliation",
    "bank recon": "bank_reconciliation",
    "reconciliation": "bank_reconciliation",
    # --- Healthcare aliases ---
    "payer": "insurance_payer_registry",
    "payer registry": "insurance_payer_registry",
    "insurance payer": "insurance_payer_registry",
    "edi payer": "insurance_payer_registry",
    "eligibility": "insurance_eligibility_verification",
    "eligibility verification": "insurance_eligibility_verification",
    "insurance eligibility": "insurance_eligibility_verification",
    "scrub": "claim_scrubbing_pre_submission",
    "claim scrubbing": "claim_scrubbing_pre_submission",
    "claim scrub": "claim_scrubbing_pre_submission",
    "era": "era_835_electronic_remittance",
    "835": "era_835_electronic_remittance",
    "electronic remittance": "era_835_electronic_remittance",
    "era 835": "era_835_electronic_remittance",
    "denial": "denial_management_workflow",
    "denial management": "denial_management_workflow",
    "claim denial": "denial_management_workflow",
    "phi": "hipaa_phi_access_audit",
    "hipaa audit": "hipaa_phi_access_audit",
    "phi access": "hipaa_phi_access_audit",
    "hipaa": "hipaa_phi_access_audit",
    "good faith": "good_faith_estimate_no_surprises_act",
    "no surprises": "good_faith_estimate_no_surprises_act",
    "good faith estimate": "good_faith_estimate_no_surprises_act",
    "no surprises act": "good_faith_estimate_no_surprises_act",
    "mips": "mips_quality_measures",
    "quality measure": "mips_quality_measures",
    "quality measures": "mips_quality_measures",
    "merit based incentive": "mips_quality_measures",
    # --- Education aliases ---
    "parent portal": "parent_portal_ferpa",
    "ferpa": "parent_portal_ferpa",
    "parent access": "parent_portal_ferpa",
    "education records": "parent_portal_ferpa",
    "school lunch": "nslp_school_lunch_program",
    "nslp": "nslp_school_lunch_program",
    "cafeteria": "nslp_school_lunch_program",
    "free lunch": "nslp_school_lunch_program",
    "meal program": "nslp_school_lunch_program",
    "bus": "school_transportation_management",
    "transportation": "school_transportation_management",
    "school bus": "school_transportation_management",
    "bus route": "school_transportation_management",
    # --- Construction aliases ---
    "davis-bacon": "davis_bacon_prevailing_wage",
    "davis bacon": "davis_bacon_prevailing_wage",
    "prevailing wage": "davis_bacon_prevailing_wage",
    "wh-347": "certified_payroll_wh_347",
    "wh 347": "certified_payroll_wh_347",
    "certified payroll": "certified_payroll_wh_347",
    "equipment scheduling": "construction_equipment_scheduling",
    "equipment booking": "construction_equipment_scheduling",
    "construction equipment": "construction_equipment_scheduling",
    # --- Property Management aliases ---
    "trust account": "property_trust_accounting",
    "security deposit": "property_trust_accounting",
    "escrow account": "property_trust_accounting",
    "tenant deposit": "property_trust_accounting",
    "rubs": "rubs_utility_billing",
    "utility billing": "rubs_utility_billing",
    "utility allocation": "rubs_utility_billing",
    # --- Retail aliases ---
    "multi-location": "multi_location_retail_inventory",
    "multi location": "multi_location_retail_inventory",
    "store inventory": "multi_location_retail_inventory",
    "multi store": "multi_location_retail_inventory",
    "omnichannel": "ecommerce_omnichannel_sync",
    "shopify": "ecommerce_omnichannel_sync",
    "ecommerce sync": "ecommerce_omnichannel_sync",
    "channel sync": "ecommerce_omnichannel_sync",
    # --- Legal aliases ---
    "ledes": "ledes_1998b_format",
    "ledes 1998b": "ledes_1998b_format",
    "e-billing": "ledes_1998b_format",
    "legal billing format": "ledes_1998b_format",
    "iolta": "iolta_trust_accounting",
    "lawyer trust": "iolta_trust_accounting",
    "client trust account": "iolta_trust_accounting",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def research_business_rule(topic: str, domain: str = None) -> dict:
    """Look up a business rule from the knowledge base.

    Args:
        topic: Natural language search term, e.g., "FIFO inventory valuation"
               or "FLSA overtime rules" or a canonical key like "fifo_valuation".
        domain: Optional domain hint (e.g., "inventory", "payroll", "procurement").

    Returns:
        dict with keys: topic, found, rule_summary, source, implementation_hints,
                        related_patterns, canonical_key
        If not found: {topic, found: False, message: "..."}
    """
    if not topic or not topic.strip():
        return {"topic": topic, "found": False, "message": "Empty topic"}

    canonical_key = _resolve_topic(topic)

    if canonical_key and canonical_key in KNOWLEDGE_BASE:
        entry = KNOWLEDGE_BASE[canonical_key]
        return {
            "topic": topic,
            "found": True,
            "canonical_key": canonical_key,
            "rule_summary": entry["summary"],
            "source": entry["source"],
            "implementation_hints": entry["implementation_hints"],
            "related_patterns": entry.get("related_patterns", []),
        }

    # Not found in knowledge base — return graceful not_found
    return {
        "topic": topic,
        "found": False,
        "message": f"No knowledge base entry for '{topic}'. "
                   "Try a more specific term or check available topics with list_knowledge_base().",
    }


def get_implementation_guide(feature_name: str) -> dict:
    """Combine knowledge base lookup + pattern library match + code template hints.

    Provides a full implementation guide for a business feature by combining:
    1. Business rule from KNOWLEDGE_BASE
    2. Code pattern from pattern_library.PATTERNS
    3. Test template skeleton

    Args:
        feature_name: Feature name, e.g., "three_way_match", "fifo_valuation"

    Returns:
        dict with keys: feature_name, business_rule, pattern, code_template, test_template
    """
    if not feature_name or not feature_name.strip():
        return {"feature_name": feature_name, "found": False, "message": "Empty feature name"}

    result = {
        "feature_name": feature_name,
        "found": False,
        "business_rule": None,
        "pattern": None,
        "code_template": None,
        "test_template": None,
    }

    # 1. Knowledge base lookup
    rule = research_business_rule(feature_name)
    if rule.get("found"):
        result["business_rule"] = {
            "summary": rule["rule_summary"],
            "source": rule["source"],
            "hints": rule["implementation_hints"],
        }
        result["found"] = True

        # 2. Pattern library match via related_patterns
        matched_pattern = None
        for rp in rule.get("related_patterns", []):
            if rp in PATTERNS:
                matched_pattern = PATTERNS[rp]
                result["pattern"] = {
                    "key": rp,
                    "name": matched_pattern["name"],
                    "actions": matched_pattern["actions"],
                    "requires_gl": matched_pattern["requires_gl"],
                    "schema_fields": matched_pattern.get("schema_fields", []),
                }
                break

        # Also check if feature_name itself is a pattern key
        if not matched_pattern and feature_name in PATTERNS:
            matched_pattern = PATTERNS[feature_name]
            result["pattern"] = {
                "key": feature_name,
                "name": matched_pattern["name"],
                "actions": matched_pattern["actions"],
                "requires_gl": matched_pattern["requires_gl"],
                "schema_fields": matched_pattern.get("schema_fields", []),
            }

        # 3. Generate code template skeleton
        if matched_pattern:
            actions = matched_pattern["actions"]
            result["code_template"] = _build_code_template(feature_name, actions)

        # 4. Generate test template skeleton
        result["test_template"] = _build_test_template(feature_name, rule)

    else:
        # Check if it matches a pattern directly even without a knowledge base entry
        if feature_name in PATTERNS:
            pat = PATTERNS[feature_name]
            result["found"] = True
            result["pattern"] = {
                "key": feature_name,
                "name": pat["name"],
                "actions": pat["actions"],
                "requires_gl": pat["requires_gl"],
                "schema_fields": pat.get("schema_fields", []),
            }
            result["code_template"] = _build_code_template(feature_name, pat["actions"])
            result["test_template"] = _build_test_template(feature_name, None)

    return result


def list_knowledge_base() -> list[dict]:
    """List all topics in the knowledge base.

    Returns:
        list of {key, summary, source} dicts.
    """
    return [
        {"key": k, "summary": v["summary"][:100], "source": v["source"]}
        for k, v in sorted(KNOWLEDGE_BASE.items())
    ]


# ---------------------------------------------------------------------------
# Action handler (wired into erpclaw-os/db_query.py)
# ---------------------------------------------------------------------------

def handle_research_rule(args) -> dict:
    """Action handler for research-business-rule.

    Required:
        --topic: The business rule topic to research
    Optional:
        --domain: Domain hint (inventory, payroll, procurement, etc.)
    """
    topic = getattr(args, "topic", None)
    domain = getattr(args, "domain", None)

    if not topic:
        return {"error": "--topic is required"}

    return research_business_rule(topic, domain)


def handle_get_implementation_guide(args) -> dict:
    """Action handler for get-implementation-guide.

    Required:
        --feature-name: The feature to get an implementation guide for
    """
    feature_name = getattr(args, "feature_name", None)

    if not feature_name:
        return {"error": "--feature-name is required"}

    return get_implementation_guide(feature_name)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _resolve_topic(topic: str) -> str | None:
    """Resolve a natural language topic to a canonical KNOWLEDGE_BASE key.

    Matching priority:
    1. Exact match on KNOWLEDGE_BASE key
    2. Exact match on _ALIASES key
    3. Normalized match (lowercase, stripped)
    4. Fuzzy substring match
    """
    if not topic:
        return None

    # 1. Exact key match
    if topic in KNOWLEDGE_BASE:
        return topic

    # 2. Normalized key match
    normalized = topic.lower().strip().replace("-", "_").replace("  ", " ")
    if normalized in KNOWLEDGE_BASE:
        return normalized

    # 3. Alias match
    alias_key = normalized.replace("_", " ")
    if alias_key in _ALIASES:
        return _ALIASES[alias_key]
    if normalized in _ALIASES:
        return _ALIASES[normalized]

    # 4. Fuzzy substring match — find the best matching key
    # Require at least 2 overlapping words, or that overlap covers >50% of the key
    best_key = None
    best_score = 0
    best_ratio = 0.0
    search_words = set(normalized.split())

    for key in KNOWLEDGE_BASE:
        key_words = set(key.split("_"))
        overlap = len(search_words & key_words)
        ratio = overlap / max(len(key_words), 1)
        if overlap > best_score or (overlap == best_score and ratio > best_ratio):
            best_score = overlap
            best_ratio = ratio
            best_key = key

    # Also check aliases
    for alias, kb_key in _ALIASES.items():
        alias_words = set(alias.split())
        overlap = len(search_words & alias_words)
        ratio = overlap / max(len(alias_words), 1)
        if overlap > best_score or (overlap == best_score and ratio > best_ratio):
            best_score = overlap
            best_ratio = ratio
            best_key = kb_key

    # Require at least 2 overlapping words, OR overlap covers >50% of the target key
    if best_score >= 2 or (best_score >= 1 and best_ratio > 0.5):
        return best_key

    return None


def _build_code_template(feature_name: str, actions: list[str]) -> str:
    """Build a skeleton code template for a feature.

    Returns a string with pseudo-code showing the function structure.
    """
    func_name = feature_name.replace("-", "_")
    lines = [f"# Code template for {feature_name}", ""]

    for action in actions:
        action_func = action.replace("-", "_")
        lines.append(f"def handle_{func_name}_{action_func}(conn, args):")
        lines.append(f'    """Handle {action} for {feature_name}."""')
        lines.append(f"    # Validate required parameters")
        lines.append(f"    # Query/update database")
        lines.append(f"    # Return result via ok()")
        lines.append(f"    pass")
        lines.append("")

    return "\n".join(lines)


def _build_test_template(feature_name: str, rule: dict | None) -> str:
    """Build a skeleton test template for a feature.

    Returns a string with pytest test structure.
    """
    class_name = "".join(w.capitalize() for w in feature_name.replace("-", "_").split("_"))
    lines = [
        f"# Test template for {feature_name}",
        "",
        f"class Test{class_name}:",
    ]

    # Happy path
    lines.append(f"    def test_{feature_name.replace('-', '_')}_happy_path(self, conn, env):")
    lines.append(f'        """Verify {feature_name} works with valid inputs."""')
    lines.append(f"        # Setup: create prerequisite data")
    lines.append(f"        # Act: call the action")
    lines.append(f"        # Assert: verify expected result")
    lines.append(f"        pass")
    lines.append("")

    # Error path
    lines.append(f"    def test_{feature_name.replace('-', '_')}_missing_required(self, conn, env):")
    lines.append(f'        """Verify {feature_name} rejects missing required params."""')
    lines.append(f"        # Act: call with missing required param")
    lines.append(f"        # Assert: error response")
    lines.append(f"        pass")
    lines.append("")

    # Source citation if available
    if rule and rule.get("found"):
        source = rule.get("source", "unknown")
        lines.append(f"    # Business rule source: {source}")

    return "\n".join(lines)
