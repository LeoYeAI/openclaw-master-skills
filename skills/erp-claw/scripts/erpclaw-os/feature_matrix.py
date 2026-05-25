#!/usr/bin/env python3
"""ERPClaw OS — Feature Completeness Matrix (Phase 4, P1-7)

Machine-readable matrix of what features a standard ERP module should have,
compared against what ERPClaw actually has. Operates at the FEATURE level
within a domain — unlike gap_detector which checks at the MODULE level.

Detection approach:
  1. Define EXPECTED_FEATURES per domain (selling, buying, inventory,
     manufacturing, hr, payroll) based on ERPNext/SAP industry standards.
  2. Scan each domain's db_query.py for its ACTIONS dict to find what exists.
  3. Compare expected vs actual, producing a list of missing features with
     priority and severity.

Integration:
  - Wired into gap_detector.py as detection method 6 (feature completeness).
  - Exposed as action: check-feature-completeness via erpclaw-os/db_query.py.
"""
import ast
import json
import os
import re
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Domain → db_query.py path mapping (relative to src/)
# ---------------------------------------------------------------------------

# Maps logical domain names to the relative path (from src_root) of the
# db_query.py file that owns that domain's ACTIONS dict.
DOMAIN_SCRIPT_PATHS = {
    "selling": "erpclaw/scripts/erpclaw-selling/db_query.py",
    "buying": "erpclaw/scripts/erpclaw-buying/db_query.py",
    "inventory": "erpclaw/scripts/erpclaw-inventory/db_query.py",
    "manufacturing": "erpclaw-addons/erpclaw-ops/scripts/erpclaw-manufacturing/db_query.py",
    "hr": "erpclaw/scripts/erpclaw-hr/db_query.py",
    "payroll": "erpclaw/scripts/erpclaw-payroll/db_query.py",
    "healthclaw": "healthclaw/healthclaw/scripts/db_query.py",
    "educlaw": "educlaw/educlaw/scripts/db_query.py",
    "constructclaw": "constructclaw/scripts/db_query.py",
    "propertyclaw": "propertyclaw/propertyclaw/scripts/db_query.py",
    "retailclaw": "retailclaw/scripts/db_query.py",
    "legalclaw": "legalclaw/scripts/db_query.py",
}


# ---------------------------------------------------------------------------
# Expected features per domain
#
# Each feature has:
#   name        — human-readable feature name (kebab-case)
#   actions     — list of action names that indicate this feature is present
#                 (at least ONE must exist for the feature to count as present)
#   priority    — P1 (blocks users), P2 (limits functionality), P3 (nice to have)
#   severity    — must-have | nice-to-have (for scoring)
#   standard    — where this feature is standard (ERPNext, SAP, both, GAAP, FLSA)
#   description — one-line explanation
# ---------------------------------------------------------------------------

EXPECTED_FEATURES = {
    "selling": [
        {
            "name": "quotation_crud",
            "actions": ["add-quotation", "update-quotation", "list-quotations", "get-quotation"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Create, read, update quotations for customers",
        },
        {
            "name": "sales_order_lifecycle",
            "actions": ["add-sales-order", "submit-sales-order", "cancel-sales-order"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Full sales order draft-submit-cancel lifecycle",
        },
        {
            "name": "delivery_note",
            "actions": ["create-delivery-note", "submit-delivery-note"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Create and submit delivery notes from sales orders",
        },
        {
            "name": "sales_invoice",
            "actions": ["create-sales-invoice", "submit-sales-invoice"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Create and submit sales invoices with GL posting",
        },
        {
            "name": "credit_note",
            "actions": ["create-credit-note"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Create credit notes for sales returns",
        },
        {
            "name": "so_amendment",
            "actions": ["amend-sales-order"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Amend submitted sales orders (cancel + recreate with link)",
        },
        {
            "name": "so_close",
            "actions": ["close-sales-order"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Close partially fulfilled SO without cancelling existing docs",
        },
        {
            "name": "blanket_so",
            "actions": ["add-blanket-order", "submit-blanket-order", "add-blanket-sales-order", "submit-blanket-sales-order"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "SAP",
            "description": "Long-term blanket sales agreements with qty drawdown",
        },
        {
            "name": "back_to_back_order",
            "actions": ["create-purchase-order-from-so"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "ERPNext",
            "description": "Auto-create PO from SO for make-to-order / drop-ship items",
        },
        {
            "name": "drop_shipment",
            "actions": ["create-drop-ship-order"],
            "priority": "P3",
            "severity": "nice-to-have",
            "standard": "SAP",
            "description": "SO ships directly from supplier to customer, skipping warehouse",
        },
        {
            "name": "packing_slip",
            "actions": ["add-packing-slip", "create-packing-slip"],
            "priority": "P3",
            "severity": "nice-to-have",
            "standard": "ERPNext",
            "description": "Packing slip document linked to delivery notes",
        },
        {
            "name": "recurring_sales",
            "actions": ["add-recurring-template", "generate-recurring-invoices"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Recurring invoice templates and auto-generation",
        },
    ],
    "buying": [
        {
            "name": "supplier_crud",
            "actions": ["add-supplier", "update-supplier", "list-suppliers"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Create, read, update supplier master data",
        },
        {
            "name": "purchase_order_lifecycle",
            "actions": ["add-purchase-order", "submit-purchase-order", "cancel-purchase-order"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Full purchase order draft-submit-cancel lifecycle",
        },
        {
            "name": "purchase_receipt",
            "actions": ["create-purchase-receipt", "submit-purchase-receipt"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Goods receipt against purchase orders with SLE",
        },
        {
            "name": "purchase_invoice",
            "actions": ["create-purchase-invoice", "submit-purchase-invoice"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Vendor invoice with GL posting",
        },
        {
            "name": "rfq_workflow",
            "actions": ["add-rfq", "submit-rfq", "add-supplier-quotation", "compare-supplier-quotations"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Request for quotation and supplier quotation comparison",
        },
        {
            "name": "three_way_match",
            "actions": ["validate-three-way-match", "check-three-way-match", "three-way-match"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "both",
            "description": "PO-GRN-Invoice three-way matching validation",
        },
        {
            "name": "grn_tolerance",
            "actions": ["set-receipt-tolerance", "configure-grn-tolerance"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Allow configurable over/under receipt tolerance on GRN",
        },
        {
            "name": "close_po",
            "actions": ["close-purchase-order"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Close partially received PO to stop further receipts",
        },
        {
            "name": "blanket_po",
            "actions": ["add-blanket-purchase-order", "submit-blanket-purchase-order", "add-blanket-order"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "SAP",
            "description": "Long-term blanket purchase agreements with qty drawdown",
        },
        {
            "name": "recurring_ap_bills",
            "actions": ["add-recurring-bill-template", "generate-recurring-bills"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Recurring vendor bill templates and auto-generation",
        },
        {
            "name": "multi_uom_po",
            "actions": ["set-purchase-uom", "convert-purchase-uom"],
            "priority": "P3",
            "severity": "nice-to-have",
            "standard": "both",
            "description": "Multi-UOM support on purchase order items with conversion",
        },
        {
            "name": "debit_note",
            "actions": ["create-debit-note"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Debit notes for purchase returns",
        },
        {
            "name": "landed_cost",
            "actions": ["add-landed-cost-voucher"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Allocate freight/duty costs to purchase receipts",
        },
    ],
    "inventory": [
        {
            "name": "item_crud",
            "actions": ["add-item", "update-item", "get-item", "list-items"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Create, read, update item master data",
        },
        {
            "name": "warehouse_management",
            "actions": ["add-warehouse", "list-warehouses"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Warehouse master data and hierarchy",
        },
        {
            "name": "stock_entry",
            "actions": ["add-stock-entry", "submit-stock-entry"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Material receipt, issue, transfer stock entries",
        },
        {
            "name": "stock_balance",
            "actions": ["get-stock-balance", "stock-balance-report"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Stock balance inquiry and reporting",
        },
        {
            "name": "batch_tracking",
            "actions": ["add-batch", "list-batches"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Batch/lot number tracking for items",
        },
        {
            "name": "serial_tracking",
            "actions": ["add-serial-number", "list-serial-numbers"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Serial number tracking for items",
        },
        {
            "name": "pricing",
            "actions": ["add-price-list", "add-item-price", "get-item-price"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Price list and item pricing management",
        },
        {
            "name": "fifo_valuation",
            "actions": ["get-fifo-valuation", "fifo-stock-report", "set-fifo-valuation"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "GAAP",
            "description": "FIFO inventory valuation method (US GAAP compliance)",
        },
        {
            "name": "projected_qty",
            "actions": ["get-projected-qty", "projected-qty-report"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Projected stock qty considering open SOs and POs",
        },
        {
            "name": "item_variants",
            "actions": ["add-item-variant", "generate-item-variants", "list-item-variants"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Item variant templates with attribute-based generation",
        },
        {
            "name": "min_order_qty",
            "actions": ["set-min-order-qty", "add-item-supplier"],
            "priority": "P3",
            "severity": "nice-to-have",
            "standard": "ERPNext",
            "description": "Minimum order qty per supplier with PO validation",
        },
        {
            "name": "stock_reconciliation",
            "actions": ["add-stock-reconciliation", "submit-stock-reconciliation"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Physical stock count reconciliation",
        },
        {
            "name": "reorder",
            "actions": ["check-reorder"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Auto-reorder check based on reorder levels",
        },
    ],
    "manufacturing": [
        {
            "name": "bom_management",
            "actions": ["add-bom", "update-bom", "get-bom", "list-boms"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Bill of materials CRUD and management",
        },
        {
            "name": "bom_explosion",
            "actions": ["explode-bom"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Multi-level BOM explosion for costing and planning",
        },
        {
            "name": "work_order_lifecycle",
            "actions": ["add-work-order", "start-work-order", "complete-work-order", "cancel-work-order"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Full work order lifecycle from creation to completion",
        },
        {
            "name": "job_card",
            "actions": ["create-job-card", "complete-job-card"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Job card tracking for work order operations",
        },
        {
            "name": "production_planning",
            "actions": ["create-production-plan", "run-mrp", "generate-work-orders"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "both",
            "description": "Production planning and MRP execution",
        },
        {
            "name": "material_transfer",
            "actions": ["transfer-materials"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Material transfer to work-in-progress for work orders",
        },
        {
            "name": "material_substitution",
            "actions": ["add-bom-substitute", "substitute-material"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "ERPNext",
            "description": "Alternative materials with priority and conversion factors",
        },
        {
            "name": "co_products",
            "actions": ["add-co-product", "add-by-product", "add-bom-output"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "SAP",
            "description": "Co-products and by-products from manufacturing with cost allocation",
        },
        {
            "name": "make_vs_buy",
            "actions": ["set-procurement-type", "configure-make-vs-buy"],
            "priority": "P3",
            "severity": "nice-to-have",
            "standard": "SAP",
            "description": "Item-level make vs buy decision for MRP routing",
        },
        {
            "name": "subcontracting",
            "actions": ["add-subcontracting-order", "submit-subcontracting-order",
                        "create-subcontracting-receipt"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Full subcontracting lifecycle (order, send materials, receive FG)",
        },
        {
            "name": "routing_operations",
            "actions": ["add-operation", "add-workstation", "add-routing"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Operations, workstations, and routing master data",
        },
    ],
    "hr": [
        {
            "name": "employee_crud",
            "actions": ["add-employee", "update-employee", "get-employee", "list-employees"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Employee master data CRUD",
        },
        {
            "name": "department_management",
            "actions": ["add-department", "list-departments"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Department and organizational structure management",
        },
        {
            "name": "leave_management",
            "actions": ["add-leave-type", "add-leave-allocation", "add-leave-application",
                        "approve-leave", "get-leave-balance"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Leave types, allocations, applications, and approvals",
        },
        {
            "name": "attendance",
            "actions": ["mark-attendance", "list-attendance"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Daily attendance marking and reporting",
        },
        {
            "name": "expense_claims",
            "actions": ["add-expense-claim", "submit-expense-claim", "approve-expense-claim"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Employee expense claim submission and approval",
        },
        {
            "name": "shift_management",
            "actions": ["add-shift-type", "add-shift-assignment", "list-shift-types"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Shift type definition and employee shift assignment",
        },
        {
            "name": "employee_documents",
            "actions": ["add-employee-document", "list-employee-documents"],
            "priority": "P3",
            "severity": "nice-to-have",
            "standard": "ERPNext",
            "description": "Employee document storage (passport, visa, I-9, W-4) with expiry",
        },
        {
            "name": "lifecycle_events",
            "actions": ["record-lifecycle-event"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Employee lifecycle tracking (hire, promote, transfer, exit)",
        },
        {
            "name": "attendance_regularization",
            "actions": ["add-attendance-regularization", "approve-attendance-regularization"],
            "priority": "P3",
            "severity": "nice-to-have",
            "standard": "ERPNext",
            "description": "Late entry / early exit regularization requests",
        },
        {
            "name": "holiday_management",
            "actions": ["add-holiday-list"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Holiday list management for leave and attendance",
        },
    ],
    "payroll": [
        {
            "name": "salary_structure",
            "actions": ["add-salary-structure", "add-salary-component", "add-salary-assignment"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Salary structure with components and employee assignment",
        },
        {
            "name": "payroll_processing",
            "actions": ["create-payroll-run", "generate-salary-slips", "submit-payroll-run"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Full payroll run: create, generate slips, submit with GL",
        },
        {
            "name": "payroll_cancellation",
            "actions": ["cancel-payroll-run"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "Cancel payroll run and reverse GL entries",
        },
        {
            "name": "tax_withholding",
            "actions": ["add-income-tax-slab", "update-fica-config"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "both",
            "description": "Federal income tax slabs and FICA configuration",
        },
        {
            "name": "garnishments",
            "actions": ["add-garnishment", "list-garnishments"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "both",
            "description": "Wage garnishment management and deduction",
        },
        {
            "name": "w2_generation",
            "actions": ["generate-w2-data"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "both",
            "description": "W-2 wage and tax statement data generation",
        },
        {
            "name": "overtime_calculation",
            "actions": ["calculate-overtime", "add-overtime-policy", "configure-overtime"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "FLSA",
            "description": "Overtime calculation (1.5x after 40h federal, state-specific rules)",
        },
        {
            "name": "multi_state_payroll",
            "actions": ["add-employee-state-config", "configure-state-tax",
                        "calculate-multi-state-tax"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "both",
            "description": "Multi-state tax withholding for employees working across states",
        },
        {
            "name": "retroactive_pay",
            "actions": ["calculate-retro-pay"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "SAP",
            "description": "Retroactive pay calculation for past period adjustments",
        },
        {
            "name": "supplemental_wages",
            "actions": ["configure-supplemental-rate", "set-supplemental-tax"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "both",
            "description": "Flat-rate tax on supplemental wages (bonuses, commissions)",
        },
        {
            "name": "nacha_ach",
            "actions": ["generate-nacha-file", "add-employee-bank-account"],
            "priority": "P3",
            "severity": "nice-to-have",
            "standard": "both",
            "description": "NACHA/ACH file generation for direct deposit payments",
        },
    ],
    # -----------------------------------------------------------------------
    # Vertical industry modules
    # -----------------------------------------------------------------------
    "healthclaw": [
        {
            "name": "payer_registry",
            "actions": ["health-add-payer", "health-list-payers"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "CMS",
            "description": "Insurance payer master data registry",
        },
        {
            "name": "eligibility_verification",
            "actions": ["health-record-eligibility-check", "health-get-latest-eligibility"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Patient insurance eligibility verification and tracking",
        },
        {
            "name": "claim_scrubbing",
            "actions": ["health-scrub-claim"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Pre-submission claim scrubbing for coding errors and compliance",
        },
        {
            "name": "era_835_processing",
            "actions": ["health-import-era-file", "health-auto-post-era"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "ERA/835 electronic remittance processing and auto-posting",
        },
        {
            "name": "denial_management",
            "actions": ["health-record-denial", "health-submit-appeal", "health-resolve-appeal"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Claim denial tracking, appeal submission, and resolution workflow",
        },
        {
            "name": "secondary_insurance",
            "actions": ["health-auto-crossover-claim"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Automatic secondary insurance claim crossover after primary payment",
        },
        {
            "name": "patient_statements",
            "actions": ["health-generate-patient-statement"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Generate itemized patient billing statements",
        },
        {
            "name": "payment_plans",
            "actions": ["health-add-payment-plan", "health-list-payment-plans"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Patient payment plan creation and management",
        },
        {
            "name": "phi_access_audit",
            "actions": ["health-log-phi-access", "health-phi-access-report"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "HIPAA",
            "description": "Protected health information access logging and audit reporting",
        },
        {
            "name": "good_faith_estimate",
            "actions": ["health-generate-good-faith-estimate"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "No Surprises Act",
            "description": "Good faith cost estimate for uninsured/self-pay patients",
        },
        {
            "name": "mips_quality_measures",
            "actions": ["health-add-quality-measure", "health-calculate-measure-result"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "CMS",
            "description": "MIPS quality measure tracking and result calculation",
        },
        {
            "name": "problem_list",
            "actions": ["health-add-problem", "health-list-active-problems"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Patient active problem list management",
        },
        {
            "name": "medication_reconciliation",
            "actions": ["health-add-med-reconciliation"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "Joint Commission",
            "description": "Medication reconciliation at transitions of care",
        },
        {
            "name": "immunization_registry",
            "actions": ["health-add-immunization", "health-list-immunizations"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Patient immunization record tracking and registry reporting",
        },
        {
            "name": "provider_credentialing",
            "actions": ["health-add-provider-credential", "health-list-provider-credentials"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Provider credential and license tracking with expiry alerts",
        },
        {
            "name": "payer_enrollment",
            "actions": ["health-add-payer-enrollment"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Provider payer enrollment and re-enrollment tracking",
        },
        {
            "name": "appointment_reminders",
            "actions": ["health-add-reminder", "health-process-reminders"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Automated patient appointment reminder scheduling and processing",
        },
        {
            "name": "baa_tracking",
            "actions": ["health-add-baa", "health-list-baas"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "HIPAA",
            "description": "Business associate agreement tracking with expiry monitoring",
        },
        {
            "name": "breach_tracking",
            "actions": ["health-add-breach-incident", "health-list-breach-incidents"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "HIPAA",
            "description": "HIPAA breach incident tracking and notification management",
        },
        {
            "name": "patient_merge",
            "actions": ["health-merge-patients"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Merge duplicate patient records with full audit trail",
        },
    ],
    "educlaw": [
        {
            "name": "parent_portal",
            "actions": ["edu-portal-my-students", "edu-portal-student-grades", "edu-portal-student-attendance"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "FERPA",
            "description": "Parent portal for viewing student grades, attendance, and records",
        },
        {
            "name": "cafeteria_nslp",
            "actions": ["edu-record-daily-meal-count", "edu-usda-claim-report"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "USDA",
            "description": "Cafeteria meal tracking and USDA National School Lunch Program claims",
        },
        {
            "name": "transportation",
            "actions": ["edu-add-bus-route", "edu-assign-student-transport"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Student transportation bus route management and assignment",
        },
        {
            "name": "professional_development",
            "actions": ["edu-add-pd-credit", "edu-list-pd-credits"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "state compliance",
            "description": "Staff professional development credit tracking for state compliance",
        },
        {
            "name": "online_fee_payment",
            "actions": ["edu-portal-pay-fee"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Online fee payment processing through parent/student portal",
        },
        {
            "name": "online_admissions",
            "actions": ["edu-portal-submit-application"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Online admissions application submission through portal",
        },
        {
            "name": "student_activities",
            "actions": ["edu-add-activity", "edu-enroll-student-activity"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Extracurricular activity management and student enrollment",
        },
        {
            "name": "library_management",
            "actions": ["edu-add-library-item", "edu-checkout-item"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Library catalog management and item checkout/return tracking",
        },
        {
            "name": "dormitory_housing",
            "actions": ["edu-add-housing-unit", "edu-assign-housing"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Dormitory and student housing unit management and assignment",
        },
        {
            "name": "degree_audit_expansion",
            "actions": ["edu-transfer-credit-eval", "edu-what-if-audit"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Transfer credit evaluation and what-if degree audit scenarios",
        },
        {
            "name": "timetable_auto_gen",
            "actions": ["edu-auto-build-schedule"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "industry",
            "description": "Automated timetable generation with constraint satisfaction",
        },
        {
            "name": "report_builder",
            "actions": ["edu-custom-report"],
            "priority": "P2",
            "severity": "nice-to-have",
            "standard": "industry",
            "description": "Custom report builder for ad-hoc educational data queries",
        },
    ],
    "constructclaw": [
        {
            "name": "equipment_scheduling",
            "actions": ["construction-assign-equipment", "construction-equipment-conflict-check"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Equipment assignment to projects with conflict detection",
        },
        {
            "name": "certified_payroll",
            "actions": ["construction-add-certified-payroll-entry", "construction-generate-wh347"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "Davis-Bacon",
            "description": "Certified payroll entries and WH-347 report generation for prevailing wage",
        },
        {
            "name": "labor_time_tracking",
            "actions": ["construction-add-time-entry", "construction-approve-time-entry"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Field labor time entry and supervisor approval workflow",
        },
        {
            "name": "permit_inspection",
            "actions": ["construction-add-permit", "construction-schedule-inspection"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Building permit tracking and inspection scheduling",
        },
        {
            "name": "punch_list",
            "actions": ["construction-add-punch-list-item"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Project punch list item tracking for closeout",
        },
        {
            "name": "insurance_bond",
            "actions": ["construction-add-insurance-certificate", "construction-add-bond"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Insurance certificate and surety bond tracking with expiry alerts",
        },
        {
            "name": "project_scheduling",
            "actions": ["construction-add-milestone", "construction-add-task-dependency"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Project milestone and task dependency scheduling",
        },
    ],
    "propertyclaw": [
        {
            "name": "online_rent_payment",
            "actions": ["prop-add-payment-method", "prop-process-rent-payment"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Online rent payment method setup and processing",
        },
        {
            "name": "tenant_portal",
            "actions": ["prop-portal-my-lease", "prop-portal-my-charges"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Tenant self-service portal for lease and charge viewing",
        },
        {
            "name": "vacancy_listing",
            "actions": ["prop-create-listing", "prop-list-vacancies"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Vacancy listing creation and available unit management",
        },
        {
            "name": "utility_billing_rubs",
            "actions": ["prop-calculate-rubs", "prop-generate-utility-charges"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "RUBS utility billing calculation and charge generation",
        },
        {
            "name": "trust_reconciliation",
            "actions": ["prop-reconcile-trust-account"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "state law",
            "description": "Security deposit trust account reconciliation per state law",
        },
        {
            "name": "lease_document_gen",
            "actions": ["prop-generate-lease-document"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Automated lease document generation from templates",
        },
    ],
    "retailclaw": [
        {
            "name": "multi_location_inventory",
            "actions": ["retail-add-store-location", "retail-get-store-inventory"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "Multi-location store setup and per-location inventory tracking",
        },
        {
            "name": "ecommerce_omnichannel",
            "actions": ["retail-sync-products-to-channel", "retail-import-online-orders"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "industry",
            "description": "E-commerce product sync and online order import for omnichannel",
        },
        {
            "name": "retail_procurement",
            "actions": ["retail-check-location-reorder"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Per-location reorder point checking and procurement triggering",
        },
        {
            "name": "shrinkage_tracking",
            "actions": ["retail-record-shrinkage", "retail-shrinkage-report"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Inventory shrinkage recording and loss reporting by location",
        },
        {
            "name": "shift_scheduling",
            "actions": ["retail-add-shift-schedule"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Retail employee shift scheduling and coverage planning",
        },
    ],
    "legalclaw": [
        {
            "name": "ledes_ebilling",
            "actions": ["legal-export-ledes-invoice", "legal-validate-ledes"],
            "priority": "P1",
            "severity": "must-have",
            "standard": "LEDES",
            "description": "LEDES format electronic invoice export and validation",
        },
        {
            "name": "client_intake",
            "actions": ["legal-add-intake-form", "legal-convert-intake-to-matter"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Client intake form creation and conversion to active matter",
        },
        {
            "name": "evergreen_retainer",
            "actions": ["legal-set-retainer-threshold", "legal-check-retainer-balance"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Evergreen retainer threshold monitoring and balance checking",
        },
        {
            "name": "task_templates",
            "actions": ["legal-add-task-template", "legal-apply-task-template"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Matter task template creation and application to new matters",
        },
        {
            "name": "contingency_fee",
            "actions": ["legal-record-settlement", "legal-calculate-contingency-fee"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Settlement recording and contingency fee calculation",
        },
        {
            "name": "client_portal",
            "actions": ["legal-portal-matter-status", "legal-portal-list-documents"],
            "priority": "P2",
            "severity": "must-have",
            "standard": "industry",
            "description": "Client self-service portal for matter status and document access",
        },
    ],
}


# ---------------------------------------------------------------------------
# Action extraction from db_query.py
# ---------------------------------------------------------------------------

# Regex to find the ACTIONS dict assignment in a db_query.py file.
# Matches: ACTIONS = { ... } (potentially multi-line)
_ACTIONS_DICT_RE = re.compile(
    r'^ACTIONS\s*=\s*\{',
    re.MULTILINE,
)


def extract_actions_from_file(file_path: str) -> set[str]:
    """Extract action names from a domain's db_query.py ACTIONS dict.

    Parses the file text to find string keys in the ACTIONS = { ... } block.
    Uses regex to find quoted key names rather than full AST parsing, since
    the ACTIONS dict values are function references that would fail ast.literal_eval.

    Returns a set of action name strings (e.g., {"add-customer", "list-customers"}).
    """
    if not os.path.isfile(file_path):
        return set()

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return set()

    # Find the ACTIONS = { line
    match = _ACTIONS_DICT_RE.search(content)
    if not match:
        return set()

    # From the match position, find the matching closing brace
    start = match.start()
    brace_count = 0
    block_start = None
    for i in range(start, len(content)):
        if content[i] == '{':
            if brace_count == 0:
                block_start = i
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                block_end = i + 1
                break
    else:
        return set()

    # Extract the block text
    block_text = content[block_start:block_end]

    # Find all string keys: "action-name": ...
    # Matches both single and double quoted strings
    key_pattern = re.compile(r'''["']([a-z][a-z0-9\-]+)["']\s*:''')
    actions = set()
    for m in key_pattern.finditer(block_text):
        actions.add(m.group(1))

    return actions


def get_domain_actions(src_root: str, domain: str) -> set[str]:
    """Get the set of implemented action names for a domain.

    Args:
        src_root: Path to the project src/ directory.
        domain: Domain name (e.g., "selling", "buying").

    Returns:
        Set of action name strings found in the domain's ACTIONS dict.
    """
    rel_path = DOMAIN_SCRIPT_PATHS.get(domain)
    if not rel_path:
        return set()

    file_path = os.path.join(src_root, rel_path)
    return extract_actions_from_file(file_path)


# ---------------------------------------------------------------------------
# Feature completeness checking
# ---------------------------------------------------------------------------

def check_feature_completeness(
    src_root: str,
    domain: Optional[str] = None,
) -> list[dict]:
    """Check which expected features are present or missing in each domain.

    For each domain (or a specific domain if given), scans the domain's
    db_query.py for existing actions and compares against EXPECTED_FEATURES.

    Args:
        src_root: Path to the project src/ directory.
        domain: Optional domain to check. If None, checks all domains.

    Returns:
        List of dicts, one per missing feature:
        {
            "domain": "selling",
            "feature": "so_amendment",
            "priority": "P2",
            "severity": "must-have",
            "standard": "ERPNext",
            "description": "...",
            "expected_actions": ["amend-sales-order"],
            "present_actions": [],
            "status": "missing",
            "gap_type": "feature_completeness",
        }
    """
    domains_to_check = [domain] if domain else list(EXPECTED_FEATURES.keys())
    missing_features = []

    for dom in domains_to_check:
        features = EXPECTED_FEATURES.get(dom)
        if not features:
            continue

        actual_actions = get_domain_actions(src_root, dom)

        for feat in features:
            expected = feat["actions"]
            present = [a for a in expected if a in actual_actions]

            if not present:
                missing_features.append({
                    "domain": dom,
                    "feature": feat["name"],
                    "priority": feat["priority"],
                    "severity": feat["severity"],
                    "standard": feat.get("standard", ""),
                    "description": feat["description"],
                    "expected_actions": expected,
                    "present_actions": present,
                    "status": "missing",
                    "gap_type": "feature_completeness",
                })

    # Sort: P1 first, then P2, then P3; within priority, must-have first
    priority_order = {"P1": 0, "P2": 1, "P3": 2}
    severity_order = {"must-have": 0, "nice-to-have": 1}
    missing_features.sort(
        key=lambda f: (
            priority_order.get(f["priority"], 9),
            severity_order.get(f["severity"], 9),
            f["domain"],
            f["feature"],
        )
    )

    return missing_features


def get_domain_score(src_root: str, domain: str) -> dict:
    """Calculate feature completeness score for a specific domain.

    Args:
        src_root: Path to the project src/ directory.
        domain: Domain name (e.g., "selling").

    Returns:
        {
            "domain": "selling",
            "total_expected": 12,
            "total_present": 7,
            "total_missing": 5,
            "score_pct": 58.3,
            "missing_features": [...],
            "present_features": [...],
        }
    """
    features = EXPECTED_FEATURES.get(domain)
    if not features:
        return {
            "domain": domain,
            "total_expected": 0,
            "total_present": 0,
            "total_missing": 0,
            "score_pct": 0.0,
            "missing_features": [],
            "present_features": [],
        }

    actual_actions = get_domain_actions(src_root, domain)

    present_features = []
    missing_features = []

    for feat in features:
        expected = feat["actions"]
        present = [a for a in expected if a in actual_actions]

        feature_info = {
            "name": feat["name"],
            "priority": feat["priority"],
            "severity": feat["severity"],
            "expected_actions": expected,
            "present_actions": present,
        }

        if present:
            feature_info["status"] = "present"
            present_features.append(feature_info)
        else:
            feature_info["status"] = "missing"
            missing_features.append(feature_info)

    total = len(features)
    present_count = len(present_features)
    missing_count = len(missing_features)
    score_pct = round((present_count / total * 100) if total > 0 else 0.0, 1)

    return {
        "domain": domain,
        "total_expected": total,
        "total_present": present_count,
        "total_missing": missing_count,
        "score_pct": score_pct,
        "missing_features": missing_features,
        "present_features": present_features,
    }


def get_all_domain_scores(src_root: str) -> dict:
    """Calculate feature completeness scores for all domains.

    Returns:
        {
            "overall_score_pct": 65.2,
            "total_expected": 60,
            "total_present": 39,
            "total_missing": 21,
            "domains": {
                "selling": { ... score dict ... },
                "buying": { ... },
                ...
            }
        }
    """
    domains = {}
    total_expected = 0
    total_present = 0

    for domain in EXPECTED_FEATURES:
        score = get_domain_score(src_root, domain)
        domains[domain] = score
        total_expected += score["total_expected"]
        total_present += score["total_present"]

    total_missing = total_expected - total_present
    overall_pct = round((total_present / total_expected * 100) if total_expected > 0 else 0.0, 1)

    return {
        "overall_score_pct": overall_pct,
        "total_expected": total_expected,
        "total_present": total_present,
        "total_missing": total_missing,
        "domains": domains,
    }


# ---------------------------------------------------------------------------
# Action handlers (wired via erpclaw-os/db_query.py)
# ---------------------------------------------------------------------------

def handle_check_feature_completeness(args):
    """Action handler for check-feature-completeness.

    Required: --src-root
    Optional: --domain (if omitted, checks all domains)

    Returns missing features with priority and severity.
    """
    src_root = getattr(args, "src_root", None)
    if not src_root or not os.path.isdir(src_root):
        return {"error": "Missing or invalid --src-root path"}

    domain = getattr(args, "domain", None)

    # Validate domain if provided
    if domain and domain not in EXPECTED_FEATURES:
        return {
            "error": f"Unknown domain '{domain}'",
            "available_domains": sorted(EXPECTED_FEATURES.keys()),
        }

    missing = check_feature_completeness(src_root, domain=domain)

    # Also produce domain scores
    if domain:
        scores = {domain: get_domain_score(src_root, domain)}
        total_expected = scores[domain]["total_expected"]
        total_present = scores[domain]["total_present"]
    else:
        all_scores = get_all_domain_scores(src_root)
        scores = all_scores["domains"]
        total_expected = all_scores["total_expected"]
        total_present = all_scores["total_present"]

    # Summary by priority
    by_priority = {}
    for feat in missing:
        p = feat["priority"]
        by_priority[p] = by_priority.get(p, 0) + 1

    return {
        "result": "ok",
        "total_missing": len(missing),
        "total_expected": total_expected,
        "total_present": total_present,
        "overall_score_pct": round(
            (total_present / total_expected * 100) if total_expected > 0 else 0.0, 1
        ),
        "missing_by_priority": by_priority,
        "domain_scores": {
            d: {"score_pct": s["score_pct"], "present": s["total_present"], "missing": s["total_missing"]}
            for d, s in scores.items()
        },
        "missing_features": missing,
    }


def handle_list_feature_matrix(args):
    """Action handler for list-feature-matrix.

    Lists the full feature matrix definition (all domains, all features).
    Optional: --domain to filter to a single domain.
    """
    domain = getattr(args, "domain", None)

    if domain:
        if domain not in EXPECTED_FEATURES:
            return {
                "error": f"Unknown domain '{domain}'",
                "available_domains": sorted(EXPECTED_FEATURES.keys()),
            }
        matrix = {domain: EXPECTED_FEATURES[domain]}
    else:
        matrix = EXPECTED_FEATURES

    total_features = sum(len(features) for features in matrix.values())

    return {
        "result": "ok",
        "domains": sorted(matrix.keys()),
        "total_features": total_features,
        "matrix": matrix,
    }
