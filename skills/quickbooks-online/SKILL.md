---
name: qb-cli
description: >
  QuickBooks Online CLI tool. Manage customers, invoices, payments, bills,
  vendors, accounts, items, expenses, journal entries, deposits, transfers,
  estimates, purchase orders, and run financial reports directly via the Intuit API.
  164 commands across 29 command groups. All commands return JSON by default for agent consumption.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - docker
        - docker compose
      env:
        - QB_CLIENT_ID
        - QB_CLIENT_SECRET
        - QB_ENVIRONMENT
    primaryEnv: QB_CLIENT_ID
    emoji: "💰"
    homepage: "https://github.com/claw4business/quickbooks-online-cli"
    source: "https://github.com/claw4business/quickbooks-online-cli"
    os:
      - macos
      - linux
install:
  - run: "git clone https://github.com/claw4business/quickbooks-online-cli.git ~/skills/qb-cli"
  - run: "cp ~/skills/qb-cli/.env.example ~/skills/qb-cli/.env"
  - run: "docker compose -f ~/skills/qb-cli/docker-compose.yml build"
---

# qb-cli — QuickBooks Online CLI

Manage QuickBooks Online from the command line. Designed for both human and AI agent use. Talks directly to Intuit's QuickBooks API — no third-party proxy. 164 commands across 29 groups covering AR, AP, chart of accounts, banking, reporting, imports, reconciliation, and month-end workflows.

## Setup

The tool runs in a Docker container at `~/skills/qb-cli/`.

### Prerequisites

1. Create a QuickBooks developer account at https://developer.intuit.com
2. Create an app (Keys & OAuth section)
3. Note your Client ID and Client Secret
4. Add `http://localhost:8844/callback` as a Redirect URI

### Configuration

```bash
cp ~/skills/qb-cli/.env.example ~/skills/qb-cli/.env
# Edit .env with your Client ID and Client Secret
```

### Build (first time)

```bash
docker compose -f ~/skills/qb-cli/docker-compose.yml build
```

### Authenticate (SSH / headless)

```bash
# Step 1: Get the auth URL
~/skills/qb-cli/run.sh auth login --print-url

# Step 2: Open the URL in any browser, authorize QuickBooks
# Step 3: Copy the full redirect URL from browser address bar
# Step 4: Paste it back
~/skills/qb-cli/run.sh auth login --callback-url "http://localhost:8844/callback?code=...&realmId=..."
```

---

## CRITICAL AGENT RULES — READ BEFORE DOING ANYTHING

### Rule 1: ALWAYS Search Before Creating

**Never create a customer, vendor, or item without first searching for duplicates.**

```bash
~/skills/qb-cli/run.sh customer search "Meridian"
~/skills/qb-cli/run.sh vendor search "Acme"
```

If the search returns results, confirm with the user which one they mean. Do NOT assume.

### Rule 2: NEVER Create a Customer Without Complete Information

**You MUST have ALL of the following before creating a customer record:**
- **Display name** — Full legal name or business name
- **Company name** — The legal business entity name (if applicable)
- **Billing email address** — Required for sending invoices electronically
- **Phone number** — Primary contact phone
- **Billing address** — Full street address, city, state, and zip code

If the user says something vague like "send an invoice to Mike" or "bill Acme $500":
1. **STOP.** Do not create anything.
2. Search for the customer: `customer search "Mike"` or `customer search "Acme"`
3. If no results, ask the user for: full name, company name, billing email, phone, and billing address.
4. Only proceed once you have all fields.

### Rule 3: Confirm Before Sending Invoices/POs

- **Never send an invoice or PO by email unless the user explicitly says to send it.**
- Creating and sending are separate actions.
- Always confirm the amount, customer/vendor, and line items before creating.

### Rule 4: Verify Payments Before Applying

- Always confirm the customer, open invoices, and amounts before creating a payment.
- Include the payment reference (check #, ACH trace, wire ref) when available.
- Verify the payment total equals the sum of the per-invoice amounts.

### Rule 5: Never Delete a Bill with Applied Payments

- Before deleting a bill, check if bill-payments have been applied to it.
- Delete or void the bill-payment first, then delete the bill.

### Rule 6: Journal Entries Must Balance

- Debits must equal credits. The CLI validates this before sending.
- Always specify a memo/description for audit trail.

### Rule 7: Never Void Deposited Payments

- If a payment has been grouped into a deposit, void/delete the deposit first.
- Then void/delete the individual payment.

### Rule 8: Reconciliation Is Read-Only

- The reconcile commands are **helpers only** — they cannot mark transactions as reconciled in QB.
- Use them to identify matches, flag discrepancies, and generate reports.
- The actual reconciliation click must happen in the QuickBooks UI.

---

## Usage

All commands: `~/skills/qb-cli/run.sh [resource] [action] [options]`

Default output is JSON. Use `-o table` for human-readable or `-o csv` for export.

---

### Auth & Config

```bash
~/skills/qb-cli/run.sh auth login --print-url          # Get OAuth URL
~/skills/qb-cli/run.sh auth login --callback-url "..."  # Complete OAuth
~/skills/qb-cli/run.sh auth status                       # Check auth status
~/skills/qb-cli/run.sh auth refresh                      # Force token refresh
~/skills/qb-cli/run.sh auth logout                       # Remove tokens
~/skills/qb-cli/run.sh config init                       # Initialize config
~/skills/qb-cli/run.sh config show                       # Show config
~/skills/qb-cli/run.sh company info                      # Company details
```

---

### Customers (AR)

```bash
# Search (ALWAYS do this first!)
~/skills/qb-cli/run.sh customer search "Acme"
~/skills/qb-cli/run.sh customer search "jane@example.com"
~/skills/qb-cli/run.sh customer search "555-0199"

# List
~/skills/qb-cli/run.sh customer list
~/skills/qb-cli/run.sh customer list -o table
~/skills/qb-cli/run.sh customer list --no-active-only

# CRUD
~/skills/qb-cli/run.sh customer get 123
~/skills/qb-cli/run.sh customer create --name "Jane Smith" --company "Smith LLC" --email "jane@smith.com" --phone "555-0199"
~/skills/qb-cli/run.sh customer update 123 --name "Jane Smith-Jones" --email "new@email.com"
~/skills/qb-cli/run.sh customer delete 123   # soft-delete (Active=false)

# Query
~/skills/qb-cli/run.sh customer query "Balance > '0'"
```

### Invoices

```bash
~/skills/qb-cli/run.sh invoice list
~/skills/qb-cli/run.sh invoice get 456
~/skills/qb-cli/run.sh invoice create --customer-id 123 --amount 500 --due-date 2026-04-01
~/skills/qb-cli/run.sh invoice create --customer-id 123 --line-json '[{"Amount":500,"DetailType":"SalesItemLineDetail","SalesItemLineDetail":{"ItemRef":{"value":"1"},"Qty":2,"UnitPrice":250}}]'
~/skills/qb-cli/run.sh invoice update 456 --json '{"DueDate": "2026-05-01"}'
~/skills/qb-cli/run.sh invoice send 456                  # email to customer
~/skills/qb-cli/run.sh invoice send 456 --email "override@email.com"
~/skills/qb-cli/run.sh invoice void 456                  # zeros amounts, keeps record
~/skills/qb-cli/run.sh invoice delete 456
~/skills/qb-cli/run.sh invoice query "CustomerRef = '123' AND Balance > '0'"
```

### Payments

```bash
~/skills/qb-cli/run.sh payment list
~/skills/qb-cli/run.sh payment get 182
~/skills/qb-cli/run.sh payment create --customer-id 63 --amount 5000 --invoice-ids "148,149" --invoice-amounts "3000,2000" --ref "ACH-12345" --date "2026-02-15"
~/skills/qb-cli/run.sh payment void 182
~/skills/qb-cli/run.sh payment delete 182
~/skills/qb-cli/run.sh payment query "TxnDate > '2026-01-01'"
```

### Estimates (Quotes/Proposals)

```bash
~/skills/qb-cli/run.sh estimate list
~/skills/qb-cli/run.sh estimate get 789
~/skills/qb-cli/run.sh estimate create --customer-id 123 --amount 1500 --expiration-date 2026-04-30
~/skills/qb-cli/run.sh estimate update 789 --json '{"ExpirationDate": "2026-05-31"}'
~/skills/qb-cli/run.sh estimate send 789
~/skills/qb-cli/run.sh estimate to-invoice 789   # convert estimate to invoice
~/skills/qb-cli/run.sh estimate delete 789
~/skills/qb-cli/run.sh estimate query "TxnStatus = 'Pending'"
```

### Credit Memos

```bash
~/skills/qb-cli/run.sh credit-memo list
~/skills/qb-cli/run.sh credit-memo create --customer-id 123 --amount 200
~/skills/qb-cli/run.sh credit-memo send 456
~/skills/qb-cli/run.sh credit-memo void 456
~/skills/qb-cli/run.sh credit-memo delete 456
~/skills/qb-cli/run.sh credit-memo query "TotalAmt > '100'"
```

### Sales Receipts (Cash Sales)

```bash
~/skills/qb-cli/run.sh sales-receipt list
~/skills/qb-cli/run.sh sales-receipt create --customer-id 123 --amount 750 --deposit-to 35 --payment-method "Cash"
~/skills/qb-cli/run.sh sales-receipt send 456
~/skills/qb-cli/run.sh sales-receipt void 456
~/skills/qb-cli/run.sh sales-receipt delete 456
```

### Refund Receipts

```bash
~/skills/qb-cli/run.sh refund-receipt list
~/skills/qb-cli/run.sh refund-receipt create --customer-id 123 --amount 200 --deposit-from 35
~/skills/qb-cli/run.sh refund-receipt void 456
~/skills/qb-cli/run.sh refund-receipt delete 456
```

---

### Vendors (AP)

```bash
# Search (ALWAYS do this first!)
~/skills/qb-cli/run.sh vendor search "Office Depot"

# List
~/skills/qb-cli/run.sh vendor list
~/skills/qb-cli/run.sh vendor list --no-active-only

# CRUD
~/skills/qb-cli/run.sh vendor get 42
~/skills/qb-cli/run.sh vendor create --name "Office Depot" --company "Office Depot Inc" --email "ap@officedepot.com" --phone "800-555-1234" --1099
~/skills/qb-cli/run.sh vendor create --name "John the Plumber" --1099 --tax-id "123-45-6789"
~/skills/qb-cli/run.sh vendor update 42 --email "new@email.com" --1099
~/skills/qb-cli/run.sh vendor delete 42   # soft-delete
~/skills/qb-cli/run.sh vendor query "Balance > '0'"
```

### Bills

```bash
~/skills/qb-cli/run.sh bill list
~/skills/qb-cli/run.sh bill get 100
~/skills/qb-cli/run.sh bill create --vendor-id 42 --amount 1500 --due-date 2026-03-15
~/skills/qb-cli/run.sh bill create --vendor-id 42 --amount 800 --account-id 80 --memo "Office supplies Jan"
~/skills/qb-cli/run.sh bill update 100 --json '{"DueDate": "2026-04-01"}'
~/skills/qb-cli/run.sh bill delete 100
~/skills/qb-cli/run.sh bill query "VendorRef = '42' AND Balance > '0'"
```

### Bill Payments

```bash
~/skills/qb-cli/run.sh bill-payment list
~/skills/qb-cli/run.sh bill-payment get 200
~/skills/qb-cli/run.sh bill-payment create --vendor-id 42 --amount 1500 --pay-type Check --account-id 35 --bill-ids "100,101" --bill-amounts "1000,500" --ref "1042"
~/skills/qb-cli/run.sh bill-payment create --vendor-id 42 --amount 800 --pay-type CreditCard --account-id 41 --bill-ids "102"
~/skills/qb-cli/run.sh bill-payment void 200
~/skills/qb-cli/run.sh bill-payment delete 200
~/skills/qb-cli/run.sh bill-payment query "TxnDate >= '2026-01-01'"
```

### Vendor Credits

```bash
~/skills/qb-cli/run.sh vendor-credit list
~/skills/qb-cli/run.sh vendor-credit create --vendor-id 42 --amount 150 --account-id 80
~/skills/qb-cli/run.sh vendor-credit delete 300
~/skills/qb-cli/run.sh vendor-credit query "VendorRef = '42'"
```

### Purchase Orders

```bash
~/skills/qb-cli/run.sh purchase-order list
~/skills/qb-cli/run.sh purchase-order create --vendor-id 42 --amount 5000 --item-id 10 --memo "Q2 inventory"
~/skills/qb-cli/run.sh purchase-order send 500
~/skills/qb-cli/run.sh purchase-order to-bill 500   # convert PO to bill
~/skills/qb-cli/run.sh purchase-order update 500 --json '{"POStatus": "Closed"}'
~/skills/qb-cli/run.sh purchase-order delete 500
```

---

### Chart of Accounts

```bash
~/skills/qb-cli/run.sh account list
~/skills/qb-cli/run.sh account list --type Bank           # filter by type
~/skills/qb-cli/run.sh account list --type Expense
~/skills/qb-cli/run.sh account get 35
~/skills/qb-cli/run.sh account create --name "Marketing" --type Expense --sub-type AdvertisingPromotional
~/skills/qb-cli/run.sh account create --name "Business Checking" --type Bank --sub-type Checking --acct-num "1010"
~/skills/qb-cli/run.sh account update 35 --name "Updated Name" --description "New description"
~/skills/qb-cli/run.sh account delete 35   # soft-delete (Active=false)
~/skills/qb-cli/run.sh account query "AccountType = 'Bank'"
```

### Items (Products & Services)

```bash
~/skills/qb-cli/run.sh item list
~/skills/qb-cli/run.sh item list --type Service
~/skills/qb-cli/run.sh item list --type Inventory
~/skills/qb-cli/run.sh item get 10
~/skills/qb-cli/run.sh item create --name "Consulting" --type Service --income-account 1 --price 150 --description "Hourly consulting"
~/skills/qb-cli/run.sh item create --name "Widget" --type Inventory --income-account 1 --expense-account 80 --asset-account 81 --price 29.99 --cost 12.50 --qty 100 --inv-start-date 2026-01-01
~/skills/qb-cli/run.sh item update 10 --price 175 --name "Senior Consulting"
~/skills/qb-cli/run.sh item delete 10   # soft-delete
~/skills/qb-cli/run.sh item query "Type = 'Service'"
```

---

### Expenses (Purchases / Checks / CC Charges)

```bash
~/skills/qb-cli/run.sh expense list
~/skills/qb-cli/run.sh expense get 400
~/skills/qb-cli/run.sh expense create --account-id 35 --pay-type Check --vendor-id 42 --amount 250 --doc-number "1042" --memo "Office supplies"
~/skills/qb-cli/run.sh expense create --account-id 41 --pay-type CreditCard --amount 99.99 --memo "Software subscription"
~/skills/qb-cli/run.sh expense update 400 --json '{"PrivateNote": "Updated memo"}'
~/skills/qb-cli/run.sh expense delete 400
~/skills/qb-cli/run.sh expense query "TxnDate >= '2026-01-01' AND TxnDate <= '2026-01-31'"
```

### Journal Entries

```bash
~/skills/qb-cli/run.sh journal list
~/skills/qb-cli/run.sh journal get 500
~/skills/qb-cli/run.sh journal create --lines '[{"account_id":"80","amount":500,"type":"Debit","description":"Depreciation exp"},{"account_id":"35","amount":500,"type":"Credit","description":"Accum depreciation"}]' --date 2026-01-31 --memo "Jan depreciation"
~/skills/qb-cli/run.sh journal delete 500
~/skills/qb-cli/run.sh journal query "TxnDate = '2026-01-31'"
```

### Deposits

```bash
~/skills/qb-cli/run.sh deposit list
~/skills/qb-cli/run.sh deposit get 600
~/skills/qb-cli/run.sh deposit create --account-id 35 --payment-ids "182,183,184" --date 2026-02-15 --memo "Week of 2/15 deposits"
~/skills/qb-cli/run.sh deposit delete 600
~/skills/qb-cli/run.sh deposit query "TxnDate >= '2026-02-01'"
```

### Transfers

```bash
~/skills/qb-cli/run.sh transfer list
~/skills/qb-cli/run.sh transfer get 700
~/skills/qb-cli/run.sh transfer create --from 35 --to 36 --amount 10000 --date 2026-02-01 --memo "Move to savings"
~/skills/qb-cli/run.sh transfer delete 700
```

---

### Financial Reports

All reports support `-o json` (default), `-o table`, `-o csv`.

```bash
# Income Statement
~/skills/qb-cli/run.sh report profit-and-loss --start-date 2026-01-01 --end-date 2026-01-31
~/skills/qb-cli/run.sh report profit-and-loss --period "Last Month"
~/skills/qb-cli/run.sh report profit-and-loss --start-date 2026-01-01 --end-date 2026-12-31 --summarize-by Month
~/skills/qb-cli/run.sh report profit-and-loss-detail --start-date 2026-01-01 --end-date 2026-01-31

# Balance Sheet
~/skills/qb-cli/run.sh report balance-sheet --date 2026-01-31
~/skills/qb-cli/run.sh report balance-sheet --period "This Fiscal Year"

# Cash Flow
~/skills/qb-cli/run.sh report cash-flow --start-date 2026-01-01 --end-date 2026-01-31

# Trial Balance
~/skills/qb-cli/run.sh report trial-balance --date 2026-01-31

# General Ledger
~/skills/qb-cli/run.sh report general-ledger --start-date 2026-01-01 --end-date 2026-01-31 --account 35

# AR/AP Aging
~/skills/qb-cli/run.sh report ar-aging
~/skills/qb-cli/run.sh report ar-aging-detail --customer 123
~/skills/qb-cli/run.sh report ap-aging
~/skills/qb-cli/run.sh report ap-aging-detail --vendor 42

# Balance Reports
~/skills/qb-cli/run.sh report customer-balance
~/skills/qb-cli/run.sh report vendor-balance

# Income/Expense Analysis
~/skills/qb-cli/run.sh report customer-income --start-date 2026-01-01 --end-date 2026-12-31
~/skills/qb-cli/run.sh report vendor-expenses --start-date 2026-01-01 --end-date 2026-12-31

# Transaction List
~/skills/qb-cli/run.sh report transaction-list --start-date 2026-01-01 --end-date 2026-01-31

# Tax Summary
~/skills/qb-cli/run.sh report tax-summary --start-date 2026-01-01 --end-date 2026-12-31
```

---

### Bank Statement Import

```bash
# Preview a statement file (no changes to QB)
~/skills/qb-cli/run.sh import preview /workspace/statement.ofx
~/skills/qb-cli/run.sh import preview /workspace/statement.csv --date-col "Trans Date" --amount-col "Amount" --desc-col "Description"

# Import and match (dry run first!)
~/skills/qb-cli/run.sh import bank /workspace/statement.ofx --account-id 35 --dry-run
~/skills/qb-cli/run.sh import bank /workspace/statement.ofx --account-id 35

# CSV import with custom columns
~/skills/qb-cli/run.sh import bank /workspace/statement.csv --account-id 35 --format csv --date-col "Date" --amount-col "Amount" --desc-col "Payee" --dry-run
```

**Supported formats:** OFX, QFX, QBO, CSV (with configurable column mapping).

**Matching algorithm:**
1. **Exact match** — same amount AND same date AND (matching FITID or check number) → **skipped**
2. **Probable match** — same amount AND date within ±3 days → **flagged for review**
3. **No match** → **created** as Purchase (debit) or Deposit (credit)

### Bank Reconciliation

```bash
# Start reconciliation session
~/skills/qb-cli/run.sh reconcile start --account-id 35 --statement-date 2026-01-31 --statement-balance 45000.00

# Check status
~/skills/qb-cli/run.sh reconcile status --account-id 35

# Match statement against QB
~/skills/qb-cli/run.sh reconcile match --account-id 35 --statement-file /workspace/jan-statement.ofx

# Generate reconciliation report
~/skills/qb-cli/run.sh reconcile report --account-id 35 --start-date 2026-01-01 --end-date 2026-01-31
```

**Note:** These are helper commands. QB has no reconciliation API — you cannot programmatically mark transactions as reconciled. Use these to identify matches and discrepancies, then complete the reconciliation in the QB UI.

---

### Bookkeeping Workflows

```bash
# Month-end close checklist
~/skills/qb-cli/run.sh workflow month-close --month 2026-01 --check-only   # just run checks
~/skills/qb-cli/run.sh workflow month-close --month 2026-01                # checks + generate reports

# 1099 preparation
~/skills/qb-cli/run.sh workflow 1099-prep --year 2025
~/skills/qb-cli/run.sh workflow 1099-prep --year 2025 --threshold 600

# AR follow-up (overdue invoices grouped by customer)
~/skills/qb-cli/run.sh workflow ar-followup --days-overdue 30
~/skills/qb-cli/run.sh workflow ar-followup --days-overdue 60

# Undeposited funds check
~/skills/qb-cli/run.sh workflow undeposited-funds
```

**Month-end close runs these checks:**
1. Undeposited Funds balance (should be ~$0)
2. Overdue AR (invoices past due before month start)
3. Overdue AP (bills past due before month start)
4. Open invoices for the month

Then generates P&L, Balance Sheet, and Trial Balance to `/workspace/`.

---

### Batch Operations

```bash
# Run batch operations from a JSON file (max 30 per batch, auto-chunks)
~/skills/qb-cli/run.sh batch run --file /workspace/batch_ops.json
```

**Batch file format:**
```json
[
  {"operation": "create", "entity": "Customer", "body": {"DisplayName": "New Customer"}},
  {"operation": "query", "sql": "SELECT * FROM Invoice WHERE Balance > '0'"},
  {"operation": "delete", "entity": "Invoice", "id": "123", "sync_token": "0"}
]
```

### Company Preferences

```bash
~/skills/qb-cli/run.sh preferences show
~/skills/qb-cli/run.sh preferences update --json '{"AccountingInfoPrefs": {"BookCloseDate": "2025-12-31"}}'
```

### Tax

```bash
~/skills/qb-cli/run.sh tax codes
~/skills/qb-cli/run.sh tax rates
~/skills/qb-cli/run.sh tax summary --start-date 2026-01-01 --end-date 2026-12-31
```

### Attachments

```bash
~/skills/qb-cli/run.sh attachment list --entity-type Invoice --entity-id 456
~/skills/qb-cli/run.sh attachment get 800
~/skills/qb-cli/run.sh attachment upload --entity-type Invoice --entity-id 456 --file /workspace/receipt.pdf
~/skills/qb-cli/run.sh attachment note --entity-type Invoice --entity-id 456 --text "Approved by CFO 2/15"
~/skills/qb-cli/run.sh attachment delete 800
```

---

## Agent Workflow Guides

### Processing a Vendor Bill

```
1. vendor search "Vendor Name"           → find or create vendor
2. bill create --vendor-id X --amount $  → record the bill
3. bill-payment create --vendor-id X --amount $ --pay-type Check --account-id Y --bill-ids Z
                                          → pay the bill when ready
```

### Sending an Invoice

```
1. customer search "Customer Name"        → find existing customer
2. invoice create --customer-id X --amount $ --due-date YYYY-MM-DD
3. (confirm with user before sending)
4. invoice send <id>                      → only if user explicitly requests
```

### Converting Estimate to Invoice

```
1. estimate create --customer-id X --amount $ --expiration-date YYYY-MM-DD
2. estimate send <id>                     → send to customer for review
3. (once accepted)
4. estimate to-invoice <id>               → creates linked invoice
```

### Month-End Close

```
1. workflow month-close --month YYYY-MM --check-only    → review issues
2. (fix any warnings: deposit undeposited funds, follow up on AR, etc.)
3. journal create --lines '[...]' --date YYYY-MM-DD     → adjusting entries
4. workflow month-close --month YYYY-MM                 → generate reports
5. report profit-and-loss --start-date ... --end-date ...  → final P&L
6. report balance-sheet --date YYYY-MM-DD               → final BS
```

### Bank Reconciliation

```
1. import preview /workspace/statement.ofx              → inspect transactions
2. import bank /workspace/statement.ofx --account-id X --dry-run  → preview matches
3. import bank /workspace/statement.ofx --account-id X  → create unmatched
4. reconcile start --account-id X --statement-date ... --statement-balance $
5. reconcile match --account-id X --statement-file /workspace/statement.ofx
6. (review matches, investigate discrepancies)
7. reconcile report --account-id X --start-date ... --end-date ...
```

### 1099 Year-End Prep

```
1. workflow 1099-prep --year YYYY         → identify vendors over threshold
2. (review missing TINs — flag them for user)
3. vendor update <id> --tax-id "XX-XXXXXXX"  → add missing TINs
4. (CSV exported to /workspace/1099_prep_YYYY.csv for filing software)
```

---

## Agent Integration Notes

**Exit codes:**
- `0` — Success
- `1` — API error (bad request, server error)
- `2` — Configuration error (missing config)
- `3` — Authentication error (expired/invalid tokens)
- `4` — Not found
- `5` — Validation error (missing required arguments)

**Error format:**
```json
{"error": true, "code": 3, "message": "Not authenticated", "hint": "qb auth login"}
```

**Key behaviors:**
- Token refresh is automatic — no manual refresh needed
- SyncToken is auto-fetched before update/delete operations
- Account entity requires **full update** (not sparse) — handled automatically
- Soft-delete for name-list entities (customer, vendor, account, item) uses `Active: false`
- Hard delete for transactions (invoice, bill, payment, etc.) uses `operation=delete`
- Void for transactions zeros amounts but keeps the record
- QuickBooks uses SQL-like queries: `SELECT * FROM Customer WHERE Balance > '0'`
- Query operators: `=`, `LIKE`, `<`, `>`, `<=`, `>=`, `IN`
- Date format: `YYYY-MM-DD`
- Reports return hierarchical JSON with Header/Columns/Rows
- Workspace directory at `/workspace/` (mapped to `~/skills/qb-cli/workspace/` on host)

**Command group count (29 groups, 164 commands):**
auth, config, company, customer, invoice, payment, estimate, credit-memo, sales-receipt, refund-receipt, vendor, bill, bill-payment, vendor-credit, purchase-order, account, item, expense, journal, deposit, transfer, report, import, reconcile, workflow, batch, preferences, tax, attachment

**QB query limitations:**
- `Vendor1099` is not queryable via SQL — use `vendor list` and filter client-side
- `OR` is not supported — searches run multiple queries and deduplicate
- Phone fields are not indexable via `LIKE` — search falls back to client-side filter
- String values in queries must be single-quoted: `WHERE Balance > '0'`
