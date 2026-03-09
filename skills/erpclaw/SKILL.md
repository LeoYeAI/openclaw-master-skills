---
name: erpclaw
version: 3.1.1
description: >
  AI-native ERP system. Full accounting, invoicing, inventory, purchasing,
  tax, billing, HR, payroll, advanced accounting (ASC 606/842, intercompany, consolidation),
  and financial reporting in a single install. 365+ actions across 14 domains.
  Modular expansion via GitHub-hosted modules. Double-entry GL, immutable audit trail, US GAAP.
author: AvanSaber / Nikhil Jathar
homepage: https://www.erpclaw.ai
source: https://github.com/avansaber/erpclaw
tier: 0
category: erp
requires: []
database: ~/.openclaw/erpclaw/data.sqlite
user-invocable: true
tags: [erp, accounting, invoicing, inventory, purchasing, tax, billing, payments, gl, reports, sales, buying, setup, hr, payroll, employees, leave, attendance, salary, revenue-recognition, lease-accounting, intercompany, consolidation]
metadata: {"openclaw":{"type":"executable","install":{"post":"python3 scripts/erpclaw-setup/db_query.py --action initialize-database"},"requires":{"bins":["python3"],"env":[],"optionalEnv":["ERPCLAW_DB_PATH"]},"os":["darwin","linux"]}}
cron:
  - expression: "0 1 * * *"
    timezone: "America/Chicago"
    description: "Process recurring journal entries"
    message: "Using erpclaw, run the process-recurring action."
    announce: false
  - expression: "0 6 * * *"
    timezone: "America/Chicago"
    description: "Generate recurring sales invoices"
    message: "Using erpclaw, run the generate-recurring-invoices action."
    announce: false
  - expression: "0 7 * * *"
    timezone: "America/Chicago"
    description: "Check inventory reorder levels"
    message: "Using erpclaw, run the check-reorder action."
    announce: false
  - expression: "0 8 * * *"
    timezone: "America/Chicago"
    description: "Check overdue invoices"
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

- **Local-first**: All data in `~/.openclaw/erpclaw/data.sqlite`. Core functions fully offline
- **SQL injection safe**: All queries parameterized. **Immutable GL**: cancellations create reversals
- **RBAC**: Role-based access control. Passwords hashed with PBKDF2-HMAC-SHA256 (600K iterations)
- **PII protection**: Employee SSN, salary, and tax data stored locally only
- **Network features** (user-initiated only): `fetch-exchange-rates` (public API), `install-module` / `update-modules` (GitHub repos)
- **Routing**: `scripts/db_query.py` → domain scripts within package, or installed modules in `~/.openclaw/erpclaw/modules/`

### Skill Activation Triggers

Activate this skill when the user mentions: ERP, accounting, invoice, sales order, purchase order, customer, supplier, inventory, payment, GL, trial balance, P&L, balance sheet, tax, billing, modules, install module, onboard, CRM, manufacturing, healthcare, education, retail, employee, HR, payroll, salary, leave, attendance, expense claim, W-2, garnishment.

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

## All Actions (Tier 2)

### Setup & Admin (42 actions)

| Action | Description |
|--------|-------------|
| `initialize-database` / `setup-company` / `update-company` / `get-company` / `list-companies` | DB init & company CRUD |
| `add-currency` / `list-currencies` / `add-exchange-rate` / `get-exchange-rate` / `list-exchange-rates` | Currency & FX |
| `add-payment-terms` / `list-payment-terms` / `add-uom` / `list-uoms` / `add-uom-conversion` | Terms & UoMs |
| `seed-defaults` / `seed-demo-data` / `check-installation` / `install-guide` | Seeding & install |
| `add-user` / `update-user` / `get-user` / `list-users` | User management |
| `add-role` / `list-roles` / `assign-role` / `revoke-role` / `set-password` / `seed-permissions` | RBAC & security |
| `link-telegram-user` / `unlink-telegram-user` / `check-telegram-permission` | Telegram integration |
| `backup-database` / `list-backups` / `verify-backup` / `restore-database` / `cleanup-backups` | DB backup/restore |
| `get-audit-log` / `get-schema-version` / `update-regional-settings` | System admin |
| `fetch-exchange-rates` / `tutorial` / `onboarding-step` / `status` | Utilities |

### General Ledger (28 actions)

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

### Journal Entries (17 actions)

| Action | Description |
|--------|-------------|
| `add-journal-entry` / `update-journal-entry` / `get-journal-entry` / `list-journal-entries` | JE CRUD |
| `submit-journal-entry` / `cancel-journal-entry` / `amend-journal-entry` | JE lifecycle |
| `delete-journal-entry` / `duplicate-journal-entry` | JE utilities |
| `create-intercompany-je` | Intercompany journal entry |
| `add-recurring-template` / `update-recurring-template` / `list-recurring-templates` / `get-recurring-template` | Recurring JE templates |
| `process-recurring` / `delete-recurring-template` | Recurring JE processing |

### Payments (14 actions)

| Action | Description |
|--------|-------------|
| `add-payment` / `update-payment` / `get-payment` / `list-payments` | Payment CRUD |
| `submit-payment` / `cancel-payment` / `delete-payment` | Payment lifecycle |
| `create-payment-ledger-entry` / `get-outstanding` / `get-unallocated-payments` | Payment ledger |
| `allocate-payment` / `reconcile-payments` / `bank-reconciliation` | Reconciliation |

### Tax (19 actions)

| Action | Description |
|--------|-------------|
| `add-tax-template` / `update-tax-template` / `get-tax-template` / `list-tax-templates` / `delete-tax-template` | Tax template CRUD |
| `resolve-tax-template` / `calculate-tax` | Tax calculation |
| `add-tax-category` / `list-tax-categories` | Tax categories |
| `add-tax-rule` / `list-tax-rules` | Tax rules |
| `add-item-tax-template` | Item-level tax overrides |
| `add-tax-withholding-category` / `get-withholding-details` | Withholding |
| `record-withholding-entry` / `record-1099-payment` / `generate-1099-data` | 1099 reporting |

### Financial Reports (21 actions)

| Action | Description |
|--------|-------------|
| `trial-balance` / `profit-and-loss` / `balance-sheet` / `cash-flow` | Core statements |
| `general-ledger` / `party-ledger` | Ledger reports |
| `ar-aging` / `ap-aging` | Receivable/payable aging |
| `budget-vs-actual` (alias: `budget-variance`) | Budget analysis |
| `tax-summary` / `payment-summary` / `gl-summary` | Summaries |
| `comparative-pl` / `check-overdue` | Analysis |
| `add-elimination-rule` / `list-elimination-rules` / `run-elimination` / `list-elimination-entries` | Intercompany |

### Selling / Order-to-Cash (42 actions)

| Action | Description |
|--------|-------------|
| `add-customer` / `update-customer` / `get-customer` / `list-customers` | Customer CRUD |
| `add-quotation` / `update-quotation` / `get-quotation` / `list-quotations` / `submit-quotation` | Quotations |
| `convert-quotation-to-so` | Quotation → Sales Order |
| `add-sales-order` / `update-sales-order` / `get-sales-order` / `list-sales-orders` / `submit-sales-order` / `cancel-sales-order` | Sales orders |
| `create-delivery-note` / `get-delivery-note` / `list-delivery-notes` / `submit-delivery-note` / `cancel-delivery-note` | Delivery |
| `create-sales-invoice` / `update-sales-invoice` / `get-sales-invoice` / `list-sales-invoices` / `submit-sales-invoice` / `cancel-sales-invoice` | Invoicing |
| `create-credit-note` / `update-invoice-outstanding` | Credit notes |
| `add-sales-partner` / `list-sales-partners` | Sales partners |
| `add-recurring-invoice-template` / `update-recurring-invoice-template` / `list-recurring-invoice-templates` / `generate-recurring-invoices` | Recurring invoices |
| `import-customers` | CSV import |
| `add-intercompany-account-map` / `list-intercompany-account-maps` / `create-intercompany-invoice` / `list-intercompany-invoices` / `cancel-intercompany-invoice` | Intercompany |

### Buying / Procure-to-Pay (36 actions)

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

### Inventory (38 actions)

| Action | Description |
|--------|-------------|
| `add-item` / `update-item` / `get-item` / `list-items` | Item master |
| `add-item-group` / `list-item-groups` | Item groups |
| `add-warehouse` / `update-warehouse` / `list-warehouses` | Warehouses |
| `add-stock-entry` / `get-stock-entry` / `list-stock-entries` / `submit-stock-entry` / `cancel-stock-entry` | Stock entries |
| `create-stock-ledger-entries` / `reverse-stock-ledger-entries` | Stock ledger |
| `get-stock-balance` / `stock-balance-report` / `stock-ledger-report` | Stock reports |
| `add-batch` / `list-batches` / `add-serial-number` / `list-serial-numbers` | Batch & serial tracking |
| `add-price-list` / `add-item-price` / `get-item-price` / `add-pricing-rule` | Pricing |
| `add-stock-reconciliation` / `submit-stock-reconciliation` | Reconciliation |
| `revalue-stock` / `list-stock-revaluations` / `get-stock-revaluation` / `cancel-stock-revaluation` | Revaluation |
| `check-reorder` / `import-items` | Utilities |

### Billing & Metering (22 actions)

| Action | Description |
|--------|-------------|
| `add-meter` / `update-meter` / `get-meter` / `list-meters` | Meter CRUD |
| `add-meter-reading` / `list-meter-readings` | Readings |
| `add-usage-event` / `add-usage-events-batch` | Usage tracking |
| `add-rate-plan` / `update-rate-plan` / `get-rate-plan` / `list-rate-plans` / `rate-consumption` | Rate plans |
| `create-billing-period` / `run-billing` / `generate-invoices` | Billing cycles |
| `add-billing-adjustment` / `list-billing-periods` / `get-billing-period` | Adjustments |
| `add-prepaid-credit` / `get-prepaid-balance` | Prepaid credits |

### Advanced Accounting (46 actions)

| Action | Description |
|--------|-------------|
| `add-revenue-contract` / `update-revenue-contract` / `get-revenue-contract` / `list-revenue-contracts` | Revenue contract CRUD (ASC 606) |
| `add-performance-obligation` / `list-performance-obligations` / `satisfy-performance-obligation` | Performance obligations |
| `add-variable-consideration` / `list-variable-considerations` / `modify-contract` | Variable consideration & mods |
| `calculate-revenue-schedule` / `generate-revenue-entries` | Revenue schedule & GL posting |
| `revenue-waterfall-report` / `revenue-recognition-summary` | Revenue reports |
| `add-lease` / `update-lease` / `get-lease` / `list-leases` / `classify-lease` | Lease CRUD & classification (ASC 842) |
| `calculate-rou-asset` / `calculate-lease-liability` / `generate-amortization-schedule` / `record-lease-payment` | ROU asset, liability & amortization |
| `lease-maturity-report` / `lease-disclosure-report` / `lease-summary` | Lease reports |
| `add-ic-transaction` / `update-ic-transaction` / `get-ic-transaction` / `list-ic-transactions` | Intercompany CRUD |
| `approve-ic-transaction` / `post-ic-transaction` | IC workflow |
| `add-transfer-price-rule` / `list-transfer-price-rules` | Transfer pricing |
| `ic-reconciliation-report` / `ic-elimination-report` | IC reports |
| `add-consolidation-group` / `list-consolidation-groups` / `add-group-entity` | Consolidation groups |
| `run-consolidation` / `generate-elimination-entries` / `add-currency-translation` | Consolidation process |
| `consolidation-trial-balance-report` / `consolidation-summary` | Consolidation reports |
| `standards-compliance-dashboard` | ASC 606/842 compliance overview |

### HR & Payroll (50 actions)

| Action | Description |
|--------|-------------|
| `add-employee` / `update-employee` / `get-employee` / `list-employees` | Employee CRUD |
| `add-department` / `list-departments` / `add-designation` / `list-designations` | Org structure |
| `add-leave-type` / `list-leave-types` / `add-leave-allocation` / `get-leave-balance` | Leave config |
| `add-leave-application` / `approve-leave` / `reject-leave` / `list-leave-applications` | Leave workflow |
| `mark-attendance` / `bulk-mark-attendance` / `list-attendance` / `add-holiday-list` | Attendance & holidays |
| `add-expense-claim` / `submit-expense-claim` / `approve-expense-claim` / `reject-expense-claim` / `list-expense-claims` | Expense claims |
| `record-lifecycle-event` / `hr-status` / `update-expense-claim-status` | HR lifecycle & status |
| `add-salary-component` / `list-salary-components` / `add-salary-structure` / `get-salary-structure` / `list-salary-structures` | Salary setup |
| `add-salary-assignment` / `list-salary-assignments` / `add-income-tax-slab` / `update-fica-config` / `update-futa-suta-config` | Payroll config |
| `create-payroll-run` / `generate-salary-slips` / `submit-payroll-run` / `cancel-payroll-run` / `get-salary-slip` / `list-salary-slips` | Payroll processing |
| `generate-w2-data` / `add-garnishment` / `update-garnishment` / `get-garnishment` / `list-garnishments` / `payroll-status` | W-2, garnishments & status |

### Module Management (10 actions)

| Action | Description |
|--------|-------------|
| `install-module` | Install a module from GitHub (`--module-name <name>`) |
| `remove-module` | Remove an installed module (`--module-name <name>`) |
| `update-modules` | Update all or a specific module |
| `list-modules` | List all installed modules |
| `available-modules` | Browse module catalog (`--category`, `--search`) |
| `module-status` | Detailed status for a module (`--module-name <name>`) |
| `search-modules` | Search catalog by keyword (`--search <query>`) |
| `rebuild-action-cache` | Rebuild action routing cache |
| `list-profiles` | Browse business onboarding profiles |
| `onboard` | Auto-install modules for a business type (`--profile <name>`) |

### Quick Command Reference

| User Says | Action |
|-----------|--------|
| "Set up my company" | `setup-company` |
| "Show trial balance" | `trial-balance` |
| "Create an invoice" | `create-sales-invoice` → `submit-sales-invoice` |
| "Record a payment" | `add-payment` → `submit-payment` |
| "Install CRM" | `install-module --module-name erpclaw-growth` |
| "Set up for retail" | `onboard --profile retail` |
| "Add employee" | `add-employee` |
| "Run payroll" | `create-payroll-run` → `generate-salary-slips` → `submit-payroll-run` |
| "Apply for leave" | `add-leave-application` |
| "Generate W-2s" | `generate-w2-data` |

Confirm before: `submit-*`, `cancel-*`, `approve-*`, `reject-*`, `run-elimination`, `run-consolidation`, `restore-database`, `close-fiscal-year`, `initialize-database --force`, `install-module`, `remove-module`, `onboard`. All `add-*`, `get-*`, `list-*`, `update-*` actions run immediately.

## Technical Details (Tier 3)

### Architecture
- **Router**: `scripts/db_query.py` dispatches to 14 core domain scripts + installed modules
- **Core Domains**: setup, meta, gl, journals, payments, tax, reports, selling, buying, inventory, billing, accounting-adv, hr, payroll
- **Module System**: Expansion modules installed from GitHub to `~/.openclaw/erpclaw/modules/`
- **Database**: Single SQLite at `~/.openclaw/erpclaw/data.sqlite`
- **Shared Library**: `~/.openclaw/erpclaw/lib/erpclaw_lib/` (installed by `initialize-database`)
- **151 tables** (149 core + 2 module system). Money = TEXT (Decimal), IDs = TEXT (UUID4). GL entries immutable.
- **Script**: `scripts/db_query.py --action <action-name> [--key value ...]`
