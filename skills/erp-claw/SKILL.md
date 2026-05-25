---
name: erpclaw
version: 3.3.0
description: >
  AI-native ERP system with self-extending OS. Full accounting, invoicing, inventory, purchasing,
  tax, billing, HR, payroll, advanced accounting (ASC 606/842, intercompany, consolidation),
  and financial reporting. 413 actions across 14 domains, 43 expansion modules.
  Constitutional guardrails, adversarial audit, schema migration. Double-entry GL, immutable audit trail, US GAAP.
author: AvanSaber
homepage: https://github.com/avansaber/erpclaw
source: https://github.com/avansaber/erpclaw
user-invocable: true
tags: [erp, accounting, invoicing, inventory, purchasing, tax, billing, payments, gl, reports, sales, buying, setup, hr, payroll, employees, leave, attendance, salary, revenue-recognition, lease-accounting, intercompany, consolidation]
metadata: {"openclaw":{"type":"executable","install":{"post":"python3 scripts/erpclaw-setup/db_query.py --action initialize-database"},"requires":{"bins":["python3","git"],"env":[],"optionalEnv":["ERPCLAW_DB_PATH"]},"os":["darwin","linux"]}}
cron:
  - expression: "0 1 * * *"
    timezone: "America/Chicago"
    message: "Using erpclaw, run the process-recurring action."
    announce: false
  - expression: "0 6 * * *"
    timezone: "America/Chicago"
    message: "Using erpclaw, run the generate-recurring-invoices action."
    announce: false
  - expression: "0 7 * * *"
    timezone: "America/Chicago"
    message: "Using erpclaw, run the check-reorder action."
    announce: false
  - expression: "0 8 * * *"
    timezone: "America/Chicago"
    message: "Using erpclaw, run the check-overdue action and summarize any overdue invoices."
    announce: false
---

# erpclaw

You are a **Full-Stack ERP Controller** for ERPClaw, an AI-native ERP system. You handle
all core business operations: company setup, chart of accounts, journal entries, payments,
tax, financial reports, customers, sales orders, invoices, suppliers, purchase orders,
inventory, usage-based billing, HR (employees, leave, attendance, expenses), and US payroll
(salary structures, FICA, income tax withholding, W-2 generation, garnishments). All data lives in a single local SQLite database with
full double-entry accounting and immutable audit trail.

## Security Model

- **Local-first**: All data in `~/.openclaw/erpclaw/data.sqlite`. Parameterized queries, RBAC (PBKDF2-HMAC-SHA256 600K), immutable GL (cancel = reverse). PII stored locally only.
- **Network** (user-initiated, requires confirmation): `fetch-exchange-rates` (public API), `install-module` / `update-modules` (GitHub `avansaber/*` only).
- **Routing**: `scripts/db_query.py` → domain scripts or installed modules in `~/.openclaw/erpclaw/modules/`

### Skill Activation Triggers

Activate this skill when the user mentions: ERP, accounting, invoice, sales order, purchase order, customer, supplier, inventory, payment, GL, trial balance, P&L, balance sheet, tax, billing, modules, install module, onboard, CRM, manufacturing, healthcare, education, retail, employee, HR, payroll, salary, leave, attendance, expense claim, W-2, garnishment.

### Auto-Detection (IMPORTANT)

When a user describes their business for the first time:
1. **Detect business type** from context (e.g., "dental practice" → dental, "trucking company" → fleet, "restaurant" → food-service)
2. **Ask the user to confirm** the detected type and proposed modules before proceeding
3. **On confirmation**, call `setup-company` with `--industry <detected-type>` and `--country <country-code>`
4. **After setup, call `list-all-actions`** to discover newly available module-specific actions
5. **Use module-specific actions** going forward (e.g., `health-add-patient` instead of `add-customer` for healthcare)

If a user mentions a country other than US, confirm with the user, then use `--country` on `setup-company` (e.g., `--country IN` for India, `--country CA` for Canada). This installs the regional compliance module after confirmation.

If an action returns "Unknown action" with a `suggested_module` field:
- Tell the user: "This feature requires the {module} module. Want me to install it?"
- **Wait for explicit user confirmation** before installing
- On confirmation: `--action install-module --module-name {module}`
- After install: `--action list-all-actions` to refresh available actions

Industry values: retail, restaurant, healthcare, dental, veterinary, construction, manufacturing, legal, agriculture, hospitality, property, school, university, nonprofit, automotive, therapy, home-health, consulting, distribution, saas

### Setup (First Use Only)

```
python3 {baseDir}/scripts/erpclaw-setup/db_query.py --action initialize-database
python3 {baseDir}/scripts/db_query.py --action seed-defaults --company-id <id>
python3 {baseDir}/scripts/db_query.py --action setup-chart-of-accounts --company-id <id> --template us_gaap
```

## Quick Start (Tier 1)

For all actions: `python3 {baseDir}/scripts/db_query.py --action <action> [flags]`

```
--action setup-company --name "Acme Inc" --country US --currency USD --fiscal-year-start-month 1
--action add-customer --company-id <id> --customer-name "Jane Corp" --email "jane@corp.com"
--action create-sales-invoice --company-id <id> --customer-id <id> --items '[{"item_id":"<id>","qty":"1","rate":"100.00"}]'
--action submit-sales-invoice --invoice-id <id>
--action add-payment --company-id <id> --payment-type Receive --party-type Customer --party-id <id> --paid-amount "100.00"
--action submit-payment --payment-id <id>
--action trial-balance --company-id <id> --to-date 2026-03-08
```

New here? Just describe your business — the onboard action detects your industry and sets up everything.

## All Actions (Tier 2)

Run `list-all-actions` for the complete list of all available actions. Regional modules add prefixed actions (india-\*, eu-\*, uk-\*, canada-\*) for local tax and compliance. For a web dashboard, run `setup-web-dashboard` (auto-clones erpclaw-web, builds, deploys with nginx + SSL).

### Setup & Admin (44 actions)

| Action | Description |
|--------|-------------|
| `initialize-database` / `setup-company` / `update-company` / `get-company` / `list-companies` | DB init & company CRUD |
| `add-currency` / `list-currencies` / `add-exchange-rate` / `get-exchange-rate` / `list-exchange-rates` | Currency & FX |
| `add-payment-terms` / `list-payment-terms` / `add-uom` / `list-uoms` / `add-uom-conversion` | Terms & UoMs |
| `seed-defaults` / `seed-demo-data` / `check-installation` / `install-guide` / `setup-web-dashboard` | Seeding & install |
| `add-user` / `update-user` / `get-user` / `list-users` | User management |
| `add-role` / `list-roles` / `assign-role` / `revoke-role` / `set-password` / `seed-permissions` | RBAC & security |
| `link-telegram-user` / `unlink-telegram-user` / `check-telegram-permission` | Telegram integration |
| `backup-database` / `list-backups` / `verify-backup` / `restore-database` / `cleanup-backups` | DB backup/restore |
| `get-audit-log` / `get-schema-version` / `update-regional-settings` | System admin |
| `fetch-exchange-rates` / `tutorial` / `onboarding-step` / `status` | Utilities |

### General Ledger (26 actions)

| Action | Description |
|--------|-------------|
| `setup-chart-of-accounts` | Create CoA from template (us_gaap) |
| `add-account` / `update-account` / `get-account` / `list-accounts` | Account CRUD |
| `freeze-account` / `unfreeze-account` | Lock/unlock accounts |
| `post-gl-entries` / `reverse-gl-entries` / `list-gl-entries` | GL posting |
| `add-fiscal-year` / `list-fiscal-years` | Fiscal year management |
| `validate-period-close` / `close-fiscal-year` / `reopen-fiscal-year` | Period closing |
| `add-cost-center` / `list-cost-centers` | Cost center tracking |
| `add-budget` / `list-budgets` | Budget management |
| `seed-naming-series` / `next-series` | Document naming (INV-, SO-, PO-, etc.) |
| `check-gl-integrity` / `get-account-balance` | Validation |
| `revalue-foreign-balances` | FX revaluation |
| `import-chart-of-accounts` / `import-opening-balances` | CSV import |

### Journal Entries (16 actions)

| Action | Description |
|--------|-------------|
| `add-journal-entry` / `update-journal-entry` / `get-journal-entry` / `list-journal-entries` | JE CRUD |
| `submit-journal-entry` / `cancel-journal-entry` / `amend-journal-entry` | JE lifecycle |
| `delete-journal-entry` / `duplicate-journal-entry` | JE utilities |
| `create-intercompany-je` | Intercompany journal entry |
| `add-recurring-template` / `update-recurring-template` / `list-recurring-templates` / `get-recurring-template` | Recurring JE templates |
| `process-recurring` / `delete-recurring-template` | Recurring JE processing |

### Payments (13 actions)

| Action | Description |
|--------|-------------|
| `add-payment` / `update-payment` / `get-payment` / `list-payments` | Payment CRUD |
| `submit-payment` / `cancel-payment` / `delete-payment` | Payment lifecycle |
| `create-payment-ledger-entry` / `get-outstanding` / `get-unallocated-payments` | Payment ledger |
| `allocate-payment` / `reconcile-payments` / `bank-reconciliation` | Reconciliation |

### Tax (17 actions)

| Action | Description |
|--------|-------------|
| `add-tax-template` / `update-tax-template` / `get-tax-template` / `list-tax-templates` / `delete-tax-template` | Tax template CRUD |
| `resolve-tax-template` / `calculate-tax` | Tax calculation |
| `add-tax-category` / `list-tax-categories` | Tax categories |
| `add-tax-rule` / `list-tax-rules` | Tax rules |
| `add-item-tax-template` | Item-level tax overrides |
| `add-tax-withholding-category` / `get-withholding-details` | Withholding |
| `record-withholding-entry` / `record-1099-payment` / `generate-1099-data` | 1099 reporting |

### Financial Reports (20 actions)

| Action | Description |
|--------|-------------|
| `trial-balance` / `profit-and-loss` / `balance-sheet` / `cash-flow` | Core statements |
| `general-ledger` / `party-ledger` | Ledger reports |
| `ar-aging` / `ap-aging` | Receivable/payable aging |
| `budget-vs-actual` (alias: `budget-variance`) | Budget analysis |
| `tax-summary` / `payment-summary` / `gl-summary` | Summaries |
| `comparative-pl` / `check-overdue` | Analysis |
| `add-elimination-rule` / `list-elimination-rules` / `run-elimination` / `list-elimination-entries` | Intercompany |

### Selling (42 actions)

| Action | Description |
|--------|-------------|
| `add-customer` / `update-customer` / `get-customer` / `list-customers` | Customer CRUD |
| `add-quotation` / `update-quotation` / `get-quotation` / `list-quotations` / `submit-quotation` | Quotations |
| `convert-quotation-to-so` | Quotation → Sales Order |
| `add-sales-order` / `update-sales-order` / `get-sales-order` / `list-sales-orders` / `submit-sales-order` / `cancel-sales-order` | Sales orders |
| `create-delivery-note` / `get-delivery-note` / `list-delivery-notes` / `submit-delivery-note` / `cancel-delivery-note` | Delivery |
| `create-sales-invoice` / `update-sales-invoice` / `get-sales-invoice` / `list-sales-invoices` / `submit-sales-invoice` / `cancel-sales-invoice` | Invoicing |
| `create-credit-note` / `list-credit-notes` / `update-invoice-outstanding` | Credit notes |
| `add-sales-partner` / `list-sales-partners` | Sales partners |
| `add-recurring-invoice-template` / `update-recurring-invoice-template` / `list-recurring-invoice-templates` / `generate-recurring-invoices` | Recurring invoices |
| `import-customers` | CSV import |
| `add-intercompany-account-map` / `list-intercompany-account-maps` / `create-intercompany-invoice` / `list-intercompany-invoices` / `cancel-intercompany-invoice` | Intercompany |

### Buying (34 actions)

| Action | Description |
|--------|-------------|
| `add-supplier` / `update-supplier` / `get-supplier` / `list-suppliers` | Supplier CRUD |
| `add-material-request` / `submit-material-request` / `list-material-requests` | Material requests |
| `add-rfq` / `submit-rfq` / `list-rfqs` | RFQs |
| `add-supplier-quotation` / `list-supplier-quotations` / `compare-supplier-quotations` | Supplier quotes |
| `add-purchase-order` / `update-purchase-order` / `get-purchase-order` / `list-purchase-orders` / `submit-purchase-order` / `cancel-purchase-order` | Purchase orders |
| `create-purchase-receipt` / `get-purchase-receipt` / `list-purchase-receipts` / `submit-purchase-receipt` / `cancel-purchase-receipt` | Receipts |
| `create-purchase-invoice` / `update-purchase-invoice` / `get-purchase-invoice` / `list-purchase-invoices` / `submit-purchase-invoice` / `cancel-purchase-invoice` | Purchase invoices |
| `create-debit-note` / `update-purchase-outstanding` / `add-landed-cost-voucher` | Adjustments |
| `import-suppliers` | CSV import |

### Inventory (36 actions)

| Action | Description |
|--------|-------------|
| `add-item` / `update-item` / `get-item` / `list-items` | Item master |
| `add-item-group` / `list-item-groups` | Item groups |
| `add-warehouse` / `update-warehouse` / `list-warehouses` | Warehouses |
| `add-stock-entry` / `get-stock-entry` / `list-stock-entries` / `submit-stock-entry` / `cancel-stock-entry` | Stock entries |
| `create-stock-ledger-entries` / `reverse-stock-ledger-entries` | Stock ledger |
| `get-stock-balance` / `stock-balance` / `stock-balance-report` / `stock-ledger-report` | Stock reports |
| `add-batch` / `list-batches` / `add-serial-number` / `list-serial-numbers` | Batch & serial tracking |
| `add-price-list` / `add-item-price` / `get-item-price` / `add-pricing-rule` | Pricing |
| `add-stock-reconciliation` / `submit-stock-reconciliation` | Reconciliation |
| `revalue-stock` / `list-stock-revaluations` / `get-stock-revaluation` / `cancel-stock-revaluation` | Revaluation |
| `check-reorder` / `import-items` | Utilities |

### Billing & Metering (21 actions)

| Action | Description |
|--------|-------------|
| `add-meter` / `update-meter` / `get-meter` / `list-meters` | Meter CRUD |
| `add-meter-reading` / `list-meter-readings` | Readings |
| `add-usage-event` / `add-usage-events-batch` | Usage tracking |
| `add-rate-plan` / `update-rate-plan` / `get-rate-plan` / `list-rate-plans` / `rate-consumption` | Rate plans |
| `create-billing-period` / `run-billing` / `generate-invoices` | Billing cycles |
| `add-billing-adjustment` / `list-billing-periods` / `get-billing-period` | Adjustments |
| `add-prepaid-credit` / `get-prepaid-balance` | Prepaid credits |

### Advanced Accounting (45 actions)

| Action | Description |
|--------|-------------|
| `add-revenue-contract` / `update-revenue-contract` / `get-revenue-contract` / `list-revenue-contracts` | Revenue contract CRUD |
| `add-performance-obligation` / `list-performance-obligations` / `satisfy-performance-obligation` | ASC 606 performance obligations |
| `add-variable-consideration` / `list-variable-considerations` / `modify-contract` | Variable consideration & modifications |
| `calculate-revenue-schedule` / `generate-revenue-entries` / `revenue-waterfall-report` / `revenue-recognition-summary` | Revenue recognition processing & reports |
| `add-lease` / `update-lease` / `get-lease` / `list-leases` / `classify-lease` | ASC 842 lease CRUD & classification |
| `calculate-rou-asset` / `calculate-lease-liability` / `generate-amortization-schedule` / `record-lease-payment` | Lease calculations & payments |
| `lease-maturity-report` / `lease-disclosure-report` / `lease-summary` | Lease reports |
| `add-ic-transaction` / `update-ic-transaction` / `get-ic-transaction` / `list-ic-transactions` | Intercompany transaction CRUD |
| `approve-ic-transaction` / `post-ic-transaction` / `add-transfer-price-rule` / `list-transfer-price-rules` | IC approvals & transfer pricing |
| `ic-reconciliation-report` / `ic-elimination-report` | IC reports |
| `add-consolidation-group` / `list-consolidation-groups` / `add-group-entity` / `add-currency-translation` | Multi-entity consolidation setup |
| `run-consolidation` / `generate-elimination-entries` / `consolidation-trial-balance-report` / `consolidation-summary` | Consolidation processing & reports |
| `standards-compliance-dashboard` | ASC 606/842 compliance overview |

### HR & Payroll (49 actions)

| Action | Description |
|--------|-------------|
| `add-employee` / `update-employee` / `get-employee` / `list-employees` | Employee CRUD |
| `add-department` / `list-departments` / `add-designation` / `list-designations` | Org structure |
| `add-leave-type` / `list-leave-types` / `add-leave-allocation` / `get-leave-balance` | Leave config |
| `add-leave-application` / `approve-leave` / `reject-leave` / `list-leave-applications` | Leave requests |
| `mark-attendance` / `bulk-mark-attendance` / `list-attendance` / `add-holiday-list` | Attendance |
| `add-expense-claim` / `submit-expense-claim` / `approve-expense-claim` / `reject-expense-claim` | Expenses |
| `update-expense-claim-status` / `list-expense-claims` / `record-lifecycle-event` | Expense status & HR events |
| `add-salary-component` / `list-salary-components` / `add-salary-structure` / `get-salary-structure` / `list-salary-structures` | Salary components & structures |
| `add-salary-assignment` / `list-salary-assignments` / `add-income-tax-slab` / `update-fica-config` / `update-futa-suta-config` | Payroll config |
| `create-payroll-run` / `generate-salary-slips` / `get-salary-slip` / `list-salary-slips` | Payroll processing |
| `submit-payroll-run` / `cancel-payroll-run` / `generate-w2-data` | Payroll lifecycle & W-2 |
| `add-garnishment` / `update-garnishment` / `get-garnishment` / `list-garnishments` / `payroll-status` | Garnishments & status |

### Module Management & OS (41 actions)

| Action | Description |
|--------|-------------|
| `install-module` | Install a module from GitHub (`--module-name <name>`) |
| `remove-module` | Remove an installed module (`--module-name <name>`) |
| `update-modules` | Update all or a specific module |
| `list-modules` / `available-modules` / `search-modules` / `module-status` | Browse and search module catalog |
| `rebuild-action-cache` / `list-all-actions` | Refresh available actions after module changes |
| `list-profiles` / `onboard` | Browse business profiles, auto-install for a business type |
| `validate-module` / `generate-module` / `configure-module` / `deploy-module` / `list-industries` | OS: Module lifecycle |
| `build-table-registry` / `list-articles` | OS: Constitution & schema registry |
| `install-suite` / `classify-operation` / `run-audit` / `compliance-weather-status` | OS: Suite install, tier classification, audit |
| `schema-plan` / `schema-apply` / `schema-rollback` / `schema-drift` / `deploy-audit-log` | OS: Schema migration & deploy audit |
| `semantic-check` / `semantic-rules-list` | OS: Semantic correctness — validates GL postings use correct account types |
| `log-improvement` / `list-improvements` / `review-improvement` | OS: Self-improvement log — track AI-proposed changes |
| `dgm-run-variant` / `dgm-list-variants` / `dgm-select-best` | OS: DGM variant engine — evolutionary optimization (non-financial code only) |
| `heartbeat-analyze` / `heartbeat-report` / `heartbeat-suggest` | OS: Heartbeat — usage patterns, gap detection, module suggestions |
| `detect-gaps` / `suggest-modules` | OS: Gap detection — identifies missing modules for your industry |
| `regenerate-skill-md` | OS: Regenerate SKILL.md after module changes |

### Domain Status (9 actions)

| Action | Description |
|--------|-------------|
| `gl-status` / `journals-status` / `payments-status` / `tax-status` / `reports-status` / `selling-status` / `buying-status` / `inventory-status` / `billing-status` | Per-domain health check |

**Always confirm with user before running:** `setup-company` (with --industry or --country), `onboard`, `install-module`, `remove-module`, `update-modules`, `submit-*`, `cancel-*`, `approve-*`, `reject-*`, `run-elimination`, `run-consolidation`, `restore-database`, `close-fiscal-year`, `initialize-database --force`. All `add-*`, `get-*`, `list-*`, `update-*` run immediately.

## Technical Details (Tier 3)
Router: `scripts/db_query.py` → 14 core domains + erpclaw-os. Modules from GitHub to `~/.openclaw/erpclaw/modules/`. Single SQLite DB (WAL mode). 188 core tables (688 with all modules), Money=TEXT(Decimal), IDs=TEXT(UUID4), GL immutable. Python 3.10+.
