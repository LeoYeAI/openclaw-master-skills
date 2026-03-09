#!/usr/bin/env python3
"""ERPClaw v3 — Unified router for 365+ actions across 14 domains.

Routes --action to the correct domain script via os.execvp().
Three dispatch tiers:
  1. ALIASES — action name remapping before forwarding
  2. ACTION_MAP — static 315-action map for core domains
  3. MODULE_ACTIONS — dynamic lookup in erpclaw_module_action table
     for installed expansion modules (~/.openclaw/erpclaw/modules/)

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout (passed through from domain script)
"""
import json
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.expanduser("~/.openclaw/erpclaw/modules")
DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")

# Action → domain mapping (365 core entries + aliases + 10 module mgmt)
# Collisions resolved: status→setup, recurring-template→journals,
# update-invoice-outstanding→selling. Aliases added for alternate domains.
ACTION_MAP = {
    # === Setup (42 actions) ===
    "initialize-database": "erpclaw-setup",
    "setup-company": "erpclaw-setup",
    "update-company": "erpclaw-setup",
    "get-company": "erpclaw-setup",
    "list-companies": "erpclaw-setup",
    "add-currency": "erpclaw-setup",
    "list-currencies": "erpclaw-setup",
    "add-exchange-rate": "erpclaw-setup",
    "get-exchange-rate": "erpclaw-setup",
    "list-exchange-rates": "erpclaw-setup",
    "add-payment-terms": "erpclaw-setup",
    "list-payment-terms": "erpclaw-setup",
    "add-uom": "erpclaw-setup",
    "list-uoms": "erpclaw-setup",
    "add-uom-conversion": "erpclaw-setup",
    "seed-defaults": "erpclaw-setup",
    "get-audit-log": "erpclaw-setup",
    "get-schema-version": "erpclaw-setup",
    "update-regional-settings": "erpclaw-setup",
    "backup-database": "erpclaw-setup",
    "list-backups": "erpclaw-setup",
    "verify-backup": "erpclaw-setup",
    "restore-database": "erpclaw-setup",
    "cleanup-backups": "erpclaw-setup",
    "fetch-exchange-rates": "erpclaw-setup",
    "status": "erpclaw-setup",
    "tutorial": "erpclaw-setup",
    "add-user": "erpclaw-setup",
    "update-user": "erpclaw-setup",
    "list-users": "erpclaw-setup",
    "get-user": "erpclaw-setup",
    "add-role": "erpclaw-setup",
    "list-roles": "erpclaw-setup",
    "assign-role": "erpclaw-setup",
    "revoke-role": "erpclaw-setup",
    "set-password": "erpclaw-setup",
    "seed-permissions": "erpclaw-setup",
    "link-telegram-user": "erpclaw-setup",
    "unlink-telegram-user": "erpclaw-setup",
    "check-telegram-permission": "erpclaw-setup",
    "onboarding-step": "erpclaw-setup",

    # === Meta (3 actions) ===
    "check-installation": "erpclaw-meta",
    "install-guide": "erpclaw-meta",
    "seed-demo-data": "erpclaw-meta",

    # === General Ledger (28 actions) ===
    "setup-chart-of-accounts": "erpclaw-gl",
    "add-account": "erpclaw-gl",
    "update-account": "erpclaw-gl",
    "list-accounts": "erpclaw-gl",
    "get-account": "erpclaw-gl",
    "freeze-account": "erpclaw-gl",
    "unfreeze-account": "erpclaw-gl",
    "post-gl-entries": "erpclaw-gl",
    "reverse-gl-entries": "erpclaw-gl",
    "list-gl-entries": "erpclaw-gl",
    "add-fiscal-year": "erpclaw-gl",
    "list-fiscal-years": "erpclaw-gl",
    "validate-period-close": "erpclaw-gl",
    "close-fiscal-year": "erpclaw-gl",
    "reopen-fiscal-year": "erpclaw-gl",
    "add-cost-center": "erpclaw-gl",
    "list-cost-centers": "erpclaw-gl",
    "add-budget": "erpclaw-gl",
    "list-budgets": "erpclaw-gl",
    "seed-naming-series": "erpclaw-gl",
    "next-series": "erpclaw-gl",
    "check-gl-integrity": "erpclaw-gl",
    "get-account-balance": "erpclaw-gl",
    "revalue-foreign-balances": "erpclaw-gl",
    "import-chart-of-accounts": "erpclaw-gl",
    "import-opening-balances": "erpclaw-gl",
    "gl-status": "erpclaw-gl",

    # === Journal Entries (17 actions) ===
    "add-journal-entry": "erpclaw-journals",
    "update-journal-entry": "erpclaw-journals",
    "get-journal-entry": "erpclaw-journals",
    "list-journal-entries": "erpclaw-journals",
    "submit-journal-entry": "erpclaw-journals",
    "cancel-journal-entry": "erpclaw-journals",
    "amend-journal-entry": "erpclaw-journals",
    "delete-journal-entry": "erpclaw-journals",
    "duplicate-journal-entry": "erpclaw-journals",
    "create-intercompany-je": "erpclaw-journals",
    "add-recurring-template": "erpclaw-journals",
    "update-recurring-template": "erpclaw-journals",
    "list-recurring-templates": "erpclaw-journals",
    "get-recurring-template": "erpclaw-journals",
    "process-recurring": "erpclaw-journals",
    "delete-recurring-template": "erpclaw-journals",
    "journals-status": "erpclaw-journals",

    # === Payments (14 actions) ===
    "add-payment": "erpclaw-payments",
    "update-payment": "erpclaw-payments",
    "get-payment": "erpclaw-payments",
    "list-payments": "erpclaw-payments",
    "submit-payment": "erpclaw-payments",
    "cancel-payment": "erpclaw-payments",
    "delete-payment": "erpclaw-payments",
    "create-payment-ledger-entry": "erpclaw-payments",
    "get-outstanding": "erpclaw-payments",
    "get-unallocated-payments": "erpclaw-payments",
    "allocate-payment": "erpclaw-payments",
    "reconcile-payments": "erpclaw-payments",
    "bank-reconciliation": "erpclaw-payments",
    "payments-status": "erpclaw-payments",

    # === Tax (19 actions) ===
    "add-tax-template": "erpclaw-tax",
    "update-tax-template": "erpclaw-tax",
    "get-tax-template": "erpclaw-tax",
    "list-tax-templates": "erpclaw-tax",
    "delete-tax-template": "erpclaw-tax",
    "resolve-tax-template": "erpclaw-tax",
    "calculate-tax": "erpclaw-tax",
    "add-tax-category": "erpclaw-tax",
    "list-tax-categories": "erpclaw-tax",
    "add-tax-rule": "erpclaw-tax",
    "list-tax-rules": "erpclaw-tax",
    "add-item-tax-template": "erpclaw-tax",
    "add-tax-withholding-category": "erpclaw-tax",
    "get-withholding-details": "erpclaw-tax",
    "record-withholding-entry": "erpclaw-tax",
    "record-1099-payment": "erpclaw-tax",
    "generate-1099-data": "erpclaw-tax",
    "tax-status": "erpclaw-tax",

    # === Financial Reports (21 actions) ===
    "trial-balance": "erpclaw-reports",
    "profit-and-loss": "erpclaw-reports",
    "balance-sheet": "erpclaw-reports",
    "cash-flow": "erpclaw-reports",
    "general-ledger": "erpclaw-reports",
    "ar-aging": "erpclaw-reports",
    "ap-aging": "erpclaw-reports",
    "budget-vs-actual": "erpclaw-reports",
    "budget-variance": "erpclaw-reports",
    "party-ledger": "erpclaw-reports",
    "tax-summary": "erpclaw-reports",
    "payment-summary": "erpclaw-reports",
    "gl-summary": "erpclaw-reports",
    "comparative-pl": "erpclaw-reports",
    "check-overdue": "erpclaw-reports",
    "add-elimination-rule": "erpclaw-reports",
    "list-elimination-rules": "erpclaw-reports",
    "run-elimination": "erpclaw-reports",
    "list-elimination-entries": "erpclaw-reports",
    "reports-status": "erpclaw-reports",

    # === Selling / Order-to-Cash (42 actions) ===
    "add-customer": "erpclaw-selling",
    "update-customer": "erpclaw-selling",
    "get-customer": "erpclaw-selling",
    "list-customers": "erpclaw-selling",
    "add-quotation": "erpclaw-selling",
    "update-quotation": "erpclaw-selling",
    "get-quotation": "erpclaw-selling",
    "list-quotations": "erpclaw-selling",
    "submit-quotation": "erpclaw-selling",
    "convert-quotation-to-so": "erpclaw-selling",
    "add-sales-order": "erpclaw-selling",
    "update-sales-order": "erpclaw-selling",
    "get-sales-order": "erpclaw-selling",
    "list-sales-orders": "erpclaw-selling",
    "submit-sales-order": "erpclaw-selling",
    "cancel-sales-order": "erpclaw-selling",
    "create-delivery-note": "erpclaw-selling",
    "get-delivery-note": "erpclaw-selling",
    "list-delivery-notes": "erpclaw-selling",
    "submit-delivery-note": "erpclaw-selling",
    "cancel-delivery-note": "erpclaw-selling",
    "create-sales-invoice": "erpclaw-selling",
    "update-sales-invoice": "erpclaw-selling",
    "get-sales-invoice": "erpclaw-selling",
    "list-sales-invoices": "erpclaw-selling",
    "submit-sales-invoice": "erpclaw-selling",
    "cancel-sales-invoice": "erpclaw-selling",
    "create-credit-note": "erpclaw-selling",
    "update-invoice-outstanding": "erpclaw-selling",
    "add-sales-partner": "erpclaw-selling",
    "list-sales-partners": "erpclaw-selling",
    "add-recurring-invoice-template": "erpclaw-selling",
    "update-recurring-invoice-template": "erpclaw-selling",
    "list-recurring-invoice-templates": "erpclaw-selling",
    "generate-recurring-invoices": "erpclaw-selling",
    "import-customers": "erpclaw-selling",
    "add-intercompany-account-map": "erpclaw-selling",
    "list-intercompany-account-maps": "erpclaw-selling",
    "create-intercompany-invoice": "erpclaw-selling",
    "list-intercompany-invoices": "erpclaw-selling",
    "cancel-intercompany-invoice": "erpclaw-selling",
    "selling-status": "erpclaw-selling",

    # === Buying / Procure-to-Pay (36 actions) ===
    "add-supplier": "erpclaw-buying",
    "update-supplier": "erpclaw-buying",
    "get-supplier": "erpclaw-buying",
    "list-suppliers": "erpclaw-buying",
    "add-material-request": "erpclaw-buying",
    "submit-material-request": "erpclaw-buying",
    "list-material-requests": "erpclaw-buying",
    "add-rfq": "erpclaw-buying",
    "submit-rfq": "erpclaw-buying",
    "list-rfqs": "erpclaw-buying",
    "add-supplier-quotation": "erpclaw-buying",
    "list-supplier-quotations": "erpclaw-buying",
    "compare-supplier-quotations": "erpclaw-buying",
    "add-purchase-order": "erpclaw-buying",
    "update-purchase-order": "erpclaw-buying",
    "get-purchase-order": "erpclaw-buying",
    "list-purchase-orders": "erpclaw-buying",
    "submit-purchase-order": "erpclaw-buying",
    "cancel-purchase-order": "erpclaw-buying",
    "create-purchase-receipt": "erpclaw-buying",
    "get-purchase-receipt": "erpclaw-buying",
    "list-purchase-receipts": "erpclaw-buying",
    "submit-purchase-receipt": "erpclaw-buying",
    "cancel-purchase-receipt": "erpclaw-buying",
    "create-purchase-invoice": "erpclaw-buying",
    "update-purchase-invoice": "erpclaw-buying",
    "get-purchase-invoice": "erpclaw-buying",
    "list-purchase-invoices": "erpclaw-buying",
    "submit-purchase-invoice": "erpclaw-buying",
    "cancel-purchase-invoice": "erpclaw-buying",
    "create-debit-note": "erpclaw-buying",
    "update-purchase-outstanding": "erpclaw-buying",
    "add-landed-cost-voucher": "erpclaw-buying",
    "import-suppliers": "erpclaw-buying",
    "buying-status": "erpclaw-buying",

    # === Inventory (38 actions) ===
    "add-item": "erpclaw-inventory",
    "update-item": "erpclaw-inventory",
    "get-item": "erpclaw-inventory",
    "list-items": "erpclaw-inventory",
    "add-item-group": "erpclaw-inventory",
    "list-item-groups": "erpclaw-inventory",
    "add-warehouse": "erpclaw-inventory",
    "update-warehouse": "erpclaw-inventory",
    "list-warehouses": "erpclaw-inventory",
    "add-stock-entry": "erpclaw-inventory",
    "get-stock-entry": "erpclaw-inventory",
    "list-stock-entries": "erpclaw-inventory",
    "submit-stock-entry": "erpclaw-inventory",
    "cancel-stock-entry": "erpclaw-inventory",
    "create-stock-ledger-entries": "erpclaw-inventory",
    "reverse-stock-ledger-entries": "erpclaw-inventory",
    "get-stock-balance": "erpclaw-inventory",
    "stock-balance": "erpclaw-inventory",
    "stock-balance-report": "erpclaw-inventory",
    "stock-ledger-report": "erpclaw-inventory",
    "add-batch": "erpclaw-inventory",
    "list-batches": "erpclaw-inventory",
    "add-serial-number": "erpclaw-inventory",
    "list-serial-numbers": "erpclaw-inventory",
    "add-price-list": "erpclaw-inventory",
    "add-item-price": "erpclaw-inventory",
    "get-item-price": "erpclaw-inventory",
    "add-pricing-rule": "erpclaw-inventory",
    "add-stock-reconciliation": "erpclaw-inventory",
    "submit-stock-reconciliation": "erpclaw-inventory",
    "revalue-stock": "erpclaw-inventory",
    "list-stock-revaluations": "erpclaw-inventory",
    "get-stock-revaluation": "erpclaw-inventory",
    "cancel-stock-revaluation": "erpclaw-inventory",
    "check-reorder": "erpclaw-inventory",
    "import-items": "erpclaw-inventory",
    "inventory-status": "erpclaw-inventory",

    # === Billing & Metering (22 actions) ===
    "add-meter": "erpclaw-billing",
    "update-meter": "erpclaw-billing",
    "get-meter": "erpclaw-billing",
    "list-meters": "erpclaw-billing",
    "add-meter-reading": "erpclaw-billing",
    "list-meter-readings": "erpclaw-billing",
    "add-usage-event": "erpclaw-billing",
    "add-usage-events-batch": "erpclaw-billing",
    "add-rate-plan": "erpclaw-billing",
    "update-rate-plan": "erpclaw-billing",
    "get-rate-plan": "erpclaw-billing",
    "list-rate-plans": "erpclaw-billing",
    "rate-consumption": "erpclaw-billing",
    "create-billing-period": "erpclaw-billing",
    "run-billing": "erpclaw-billing",
    "generate-invoices": "erpclaw-billing",
    "add-billing-adjustment": "erpclaw-billing",
    "list-billing-periods": "erpclaw-billing",
    "get-billing-period": "erpclaw-billing",
    "add-prepaid-credit": "erpclaw-billing",
    "get-prepaid-balance": "erpclaw-billing",
    "billing-status": "erpclaw-billing",

    # === Advanced Accounting — Revenue Recognition / ASC 606 (14 actions) ===
    "add-revenue-contract": "erpclaw-accounting-adv",
    "update-revenue-contract": "erpclaw-accounting-adv",
    "get-revenue-contract": "erpclaw-accounting-adv",
    "list-revenue-contracts": "erpclaw-accounting-adv",
    "add-performance-obligation": "erpclaw-accounting-adv",
    "list-performance-obligations": "erpclaw-accounting-adv",
    "satisfy-performance-obligation": "erpclaw-accounting-adv",
    "add-variable-consideration": "erpclaw-accounting-adv",
    "list-variable-considerations": "erpclaw-accounting-adv",
    "modify-contract": "erpclaw-accounting-adv",
    "calculate-revenue-schedule": "erpclaw-accounting-adv",
    "generate-revenue-entries": "erpclaw-accounting-adv",
    "revenue-waterfall-report": "erpclaw-accounting-adv",
    "revenue-recognition-summary": "erpclaw-accounting-adv",

    # === Advanced Accounting — Lease Accounting / ASC 842 (12 actions) ===
    "add-lease": "erpclaw-accounting-adv",
    "update-lease": "erpclaw-accounting-adv",
    "get-lease": "erpclaw-accounting-adv",
    "list-leases": "erpclaw-accounting-adv",
    "classify-lease": "erpclaw-accounting-adv",
    "calculate-rou-asset": "erpclaw-accounting-adv",
    "calculate-lease-liability": "erpclaw-accounting-adv",
    "generate-amortization-schedule": "erpclaw-accounting-adv",
    "record-lease-payment": "erpclaw-accounting-adv",
    "lease-maturity-report": "erpclaw-accounting-adv",
    "lease-disclosure-report": "erpclaw-accounting-adv",
    "lease-summary": "erpclaw-accounting-adv",

    # === Advanced Accounting — Intercompany Transactions (10 actions) ===
    "add-ic-transaction": "erpclaw-accounting-adv",
    "update-ic-transaction": "erpclaw-accounting-adv",
    "get-ic-transaction": "erpclaw-accounting-adv",
    "list-ic-transactions": "erpclaw-accounting-adv",
    "approve-ic-transaction": "erpclaw-accounting-adv",
    "post-ic-transaction": "erpclaw-accounting-adv",
    "add-transfer-price-rule": "erpclaw-accounting-adv",
    "list-transfer-price-rules": "erpclaw-accounting-adv",
    "ic-reconciliation-report": "erpclaw-accounting-adv",
    "ic-elimination-report": "erpclaw-accounting-adv",

    # === Advanced Accounting — Multi-Entity Consolidation (8 actions) ===
    "add-consolidation-group": "erpclaw-accounting-adv",
    "list-consolidation-groups": "erpclaw-accounting-adv",
    "add-group-entity": "erpclaw-accounting-adv",
    "run-consolidation": "erpclaw-accounting-adv",
    "generate-elimination-entries": "erpclaw-accounting-adv",
    "add-currency-translation": "erpclaw-accounting-adv",
    "consolidation-trial-balance-report": "erpclaw-accounting-adv",
    "consolidation-summary": "erpclaw-accounting-adv",

    # === Advanced Accounting — Reports (1 action) ===
    "standards-compliance-dashboard": "erpclaw-accounting-adv",

    # === HR — Employee Management (28 actions) ===
    "add-employee": "erpclaw-hr",
    "update-employee": "erpclaw-hr",
    "get-employee": "erpclaw-hr",
    "list-employees": "erpclaw-hr",
    "add-department": "erpclaw-hr",
    "list-departments": "erpclaw-hr",
    "add-designation": "erpclaw-hr",
    "list-designations": "erpclaw-hr",
    "add-leave-type": "erpclaw-hr",
    "list-leave-types": "erpclaw-hr",
    "add-leave-allocation": "erpclaw-hr",
    "get-leave-balance": "erpclaw-hr",
    "add-leave-application": "erpclaw-hr",
    "approve-leave": "erpclaw-hr",
    "reject-leave": "erpclaw-hr",
    "list-leave-applications": "erpclaw-hr",
    "mark-attendance": "erpclaw-hr",
    "bulk-mark-attendance": "erpclaw-hr",
    "list-attendance": "erpclaw-hr",
    "add-holiday-list": "erpclaw-hr",
    "add-expense-claim": "erpclaw-hr",
    "submit-expense-claim": "erpclaw-hr",
    "approve-expense-claim": "erpclaw-hr",
    "reject-expense-claim": "erpclaw-hr",
    "update-expense-claim-status": "erpclaw-hr",
    "list-expense-claims": "erpclaw-hr",
    "record-lifecycle-event": "erpclaw-hr",
    "hr-status": "erpclaw-hr",

    # === Payroll — US Payroll Processing (22 actions) ===
    "add-salary-component": "erpclaw-payroll",
    "list-salary-components": "erpclaw-payroll",
    "add-salary-structure": "erpclaw-payroll",
    "get-salary-structure": "erpclaw-payroll",
    "list-salary-structures": "erpclaw-payroll",
    "add-salary-assignment": "erpclaw-payroll",
    "list-salary-assignments": "erpclaw-payroll",
    "add-income-tax-slab": "erpclaw-payroll",
    "update-fica-config": "erpclaw-payroll",
    "update-futa-suta-config": "erpclaw-payroll",
    "create-payroll-run": "erpclaw-payroll",
    "generate-salary-slips": "erpclaw-payroll",
    "get-salary-slip": "erpclaw-payroll",
    "list-salary-slips": "erpclaw-payroll",
    "submit-payroll-run": "erpclaw-payroll",
    "cancel-payroll-run": "erpclaw-payroll",
    "generate-w2-data": "erpclaw-payroll",
    "add-garnishment": "erpclaw-payroll",
    "update-garnishment": "erpclaw-payroll",
    "list-garnishments": "erpclaw-payroll",
    "get-garnishment": "erpclaw-payroll",
    "payroll-status": "erpclaw-payroll",
}

# Aliases: actions that need to be forwarded with a different --action name
# Format: "router-action-name": ("domain", "original-action-name")
ALIASES = {
    # Domain-specific status aliases
    "gl-status": ("erpclaw-gl", "status"),
    "journals-status": ("erpclaw-journals", "status"),
    "payments-status": ("erpclaw-payments", "status"),
    "tax-status": ("erpclaw-tax", "status"),
    "reports-status": ("erpclaw-reports", "status"),
    "selling-status": ("erpclaw-selling", "status"),
    "buying-status": ("erpclaw-buying", "status"),
    "inventory-status": ("erpclaw-inventory", "status"),
    "billing-status": ("erpclaw-billing", "status"),
    "accounting-adv-status": ("erpclaw-accounting-adv", "status"),
    # Selling recurring template aliases (journals owns the base names)
    "add-recurring-invoice-template": ("erpclaw-selling", "add-recurring-template"),
    "update-recurring-invoice-template": ("erpclaw-selling", "update-recurring-template"),
    "list-recurring-invoice-templates": ("erpclaw-selling", "list-recurring-templates"),
    # Buying outstanding alias (selling owns the base name)
    "update-purchase-outstanding": ("erpclaw-buying", "update-invoice-outstanding"),
}


# ---------------------------------------------------------------------------
# Module management actions — forwarded to module_manager.py / onboarding.py
# ---------------------------------------------------------------------------
MODULE_ACTIONS = {
    "install-module", "remove-module", "update-modules",
    "list-modules", "available-modules", "module-status",
    "search-modules", "rebuild-action-cache",
}

ONBOARDING_ACTIONS = {
    "list-profiles", "onboard",
}


def find_action():
    """Extract --action value from sys.argv."""
    for i, arg in enumerate(sys.argv):
        if arg == "--action" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def forward(domain, action_override=None):
    """Forward execution to the domain script via os.execvp."""
    script = os.path.join(BASE_DIR, domain, "db_query.py")
    if not os.path.isfile(script):
        print(json.dumps({
            "status": "error",
            "error": f"Domain script not found: {domain}/db_query.py"
        }))
        sys.exit(1)

    args = list(sys.argv[1:])

    # If there's an action override (alias), replace the action name in args
    if action_override:
        for i, arg in enumerate(args):
            if arg == "--action" and i + 1 < len(args):
                args[i + 1] = action_override
                break

    os.execvp(sys.executable, [sys.executable, script] + args)


def forward_script(script_path):
    """Forward execution to a standalone script (module_manager, onboarding)."""
    if not os.path.isfile(script_path):
        print(json.dumps({
            "status": "error",
            "error": f"Script not found: {script_path}"
        }))
        sys.exit(1)

    args = list(sys.argv[1:])
    os.execvp(sys.executable, [sys.executable, script_path] + args)


def forward_module(module_name, action_override=None):
    """Forward execution to an installed module's db_query.py."""
    script = os.path.join(MODULES_DIR, module_name, "scripts", "db_query.py")
    if not os.path.isfile(script):
        print(json.dumps({
            "status": "error",
            "error": f"Module script not found: {module_name}/scripts/db_query.py",
            "hint": f"Try: --action module-status --module-name {module_name}"
        }))
        sys.exit(1)

    args = list(sys.argv[1:])

    if action_override:
        for i, arg in enumerate(args):
            if arg == "--action" and i + 1 < len(args):
                args[i + 1] = action_override
                break

    os.execvp(sys.executable, [sys.executable, script] + args)


def lookup_module_for_action(action):
    """Query erpclaw_module_action table to find which module owns this action.

    Returns the module_name if found, None otherwise.
    Uses a direct sqlite3 connection (not shared lib) to avoid import overhead.
    """
    if not os.path.isfile(DB_PATH):
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """SELECT ma.module_name
               FROM erpclaw_module_action ma
               JOIN erpclaw_module m ON m.name = ma.module_name
               WHERE ma.action_name = ?
                 AND m.install_status = 'installed'
                 AND m.is_active = 1
               LIMIT 1""",
            (action,)
        ).fetchone()
        conn.close()
        if row:
            return row["module_name"]
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        # Table doesn't exist yet or DB issue — fall through
        pass
    return None


def main():
    action = find_action()
    if not action:
        print(json.dumps({
            "status": "error",
            "error": "Missing --action flag. Usage: python3 db_query.py --action <action-name> [flags]"
        }))
        sys.exit(1)

    # Tier 0: Module management actions → module_manager.py
    if action in MODULE_ACTIONS:
        forward_script(os.path.join(BASE_DIR, "module_manager.py"))
        return

    # Tier 0: Onboarding actions → onboarding.py
    if action in ONBOARDING_ACTIONS:
        forward_script(os.path.join(BASE_DIR, "onboarding.py"))
        return

    # Tier 1: Check aliases (need to override action name)
    if action in ALIASES:
        domain, original_action = ALIASES[action]
        forward(domain, action_override=original_action)
        return

    # Tier 2: Check static core action map
    domain = ACTION_MAP.get(action)
    if domain:
        forward(domain)
        return

    # Tier 3: Dynamic lookup — check installed modules
    module_name = lookup_module_for_action(action)
    if module_name:
        forward_module(module_name)
        return

    # Unknown action
    print(json.dumps({
        "status": "error",
        "error": f"Unknown action: {action}",
        "hint": "Run --action status for system overview, or --action available-modules to browse installable modules"
    }))
    sys.exit(1)


if __name__ == "__main__":
    main()
