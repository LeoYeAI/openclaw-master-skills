---
name: greek-financial-statements
description: Greek financial statement generation — P&L, balance sheets, VAT summaries with EGLS integration. Completeness gates prevent partial outputs.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "financial-statements", "balance-sheet", "pnl", "egls"]
metadata: {"openclaw": {"requires": {"bins": ["jq"], "env": ["OPENCLAW_DATA_DIR"]}, "notes": "Instruction-only skill. Generates financial statements (P&L, balance sheet) from data in OPENCLAW_DATA_DIR. Includes completeness gate that blocks generation if source data is incomplete. No external services required."}}
---

# Greek Financial Statements

This skill generates professional financial statements for Greek businesses, integrating with the ΕΓΛΣ (Ελληνικό Γενικό Λογιστικό Σχέδιο — Greek General Chart of Accounts) and enforcing strict completeness gates to prevent incomplete or inaccurate output. Every statement is versioned, bilingual (Greek for clients, English for internal), and includes a full audit trail.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
which jq || sudo apt install jq
```

No external credentials required. Generates financial statements (P&L, balance sheet, cash flow) from data in OPENCLAW_DATA_DIR. Includes a completeness gate that blocks generation if source data is incomplete.


## Core Philosophy

- **Completeness First**: Never generate a statement with incomplete source data — halt and report blockers
- **ΕΓΛΣ Native**: All accounts classified per Greek Chart of Accounts standards
- **Versioned & Immutable**: Once issued, a statement is never overwritten — amendments create new versions
- **Bilingual Output**: Greek labels for client-facing documents, English for internal use
- **Balance Sheet Must Balance**: Assets must equal equity plus liabilities — halt on any mismatch
- **Human Oversight**: All generated statements are drafts until a senior accountant reviews and issues them

## OpenClaw Commands

### Statement Generation
```bash
# Generate full financial statement pack (P&L + balance sheet + VAT summary)
openclaw statements generate --afm EL123456789 --period 2026-01

# Generate specific statement type
openclaw statements generate-pl --afm EL123456789 --period 2026-01
openclaw statements generate-balance-sheet --afm EL123456789 --period 2026-01
openclaw statements generate-vat-summary --afm EL123456789 --period 2026-01

# Force partial generation (requires explicit human confirmation)
openclaw statements generate --afm EL123456789 --period 2026-01 --force-partial --confirm
```

### Completeness & Readiness
```bash
# Check readiness for a single client
openclaw statements readiness --afm EL123456789 --period 2026-01

# Check readiness across all active clients
openclaw statements readiness-all --period 2026-01

# Show specific blockers for a client
openclaw statements blockers --afm EL123456789 --period 2026-01
```

### Amendments & Versioning
```bash
# Create amendment to an existing statement
openclaw statements amend --afm EL123456789 --period 2025-10 --reason "Late supplier invoice discovered"

# View version history for a client period
openclaw statements versions --afm EL123456789 --period 2025-10

# Compare two versions
openclaw statements diff --afm EL123456789 --period 2025-10 --v1 1 --v2 2
```

### Period Comparison & Analysis
```bash
# Compare current period to same period last year
openclaw statements compare --afm EL123456789 --period 2026-01 --vs 2025-01

# Compare current period to previous period
openclaw statements compare --afm EL123456789 --period 2026-01 --vs 2025-12

# Flag significant variances (default threshold: 15%)
openclaw statements variance-report --afm EL123456789 --period 2026-01 --threshold 15
```

### Output & Distribution
```bash
# Generate client-facing PDF pack
openclaw statements export-pdf --afm EL123456789 --period 2026-01 --language greek

# Generate bilingual PDF (Greek primary, English annotations)
openclaw statements export-pdf --afm EL123456789 --period 2026-01 --bilingual

# Queue statement for client delivery via communication engine
openclaw statements send-to-client --afm EL123456789 --period 2026-01 --via email
```

## Completeness Gate

The completeness gate runs automatically before every statement generation. It checks all required data sources and halts generation if any are incomplete. The gate cannot be bypassed without `--force-partial --confirm`.

### Gate Checks

```yaml
Completeness_Gate:
  banking_reconciliation:
    check: "Banking reconciliation exists and status is 'complete' for the period"
    source: "/data/clients/{AFM}/compliance/ or /data/banking/"
    blocker_if: "missing or status != complete"
    
  vat_filing:
    check: "VAT filing data exists for the period"
    source: "/data/compliance/vat/{AFM}_{period}_vat_return.xml"
    blocker_if: "missing"
    
  efka_contributions:
    check: "EFKA contribution data exists and status is 'calculated' or 'submitted'"
    source: "/data/efka/"
    blocker_if: "missing or status == 'pending'"
    
  ocr_queue:
    check: "No documents for this client are pending in the OCR queue"
    source: "/data/processing/ocr/queued/"
    blocker_if: "pending_count > 0"
    
  prior_period:
    check: "Prior period statement exists (unless this is the first period)"
    source: "/data/clients/{AFM}/financial-statements/"
    blocker_if: "missing and not first_period"
    warning_if: "prior period has unresolved amendments"
```

### Gate Output

When blocked:
```json
{
  "afm": "EL987654321",
  "period": "2026-02",
  "gate_result": "BLOCKED",
  "blockers": [
    {
      "check": "banking_reconciliation",
      "status": "not_started",
      "resolve_command": "openclaw banking reconcile --afm EL987654321 --period 2026-02"
    },
    {
      "check": "ocr_queue",
      "status": "4 items pending",
      "items": ["invoice_0234.pdf", "receipt_0891.pdf", "invoice_0235.pdf", "bank_charge_0012.pdf"],
      "resolve_command": "openclaw ocr process-queue --afm EL987654321 --priority"
    }
  ],
  "ready_items": ["vat_filing", "efka_contributions"],
  "recommendation": "Resolve blockers before generating statements. Run: openclaw statements blockers --afm EL987654321 --period 2026-02 for details."
}
```

Blocked results are logged to `/data/memory/failures/` with `failure_type: completeness_gate_failed`.

## ΕΓΛΣ — Greek Chart of Accounts Integration

All financial statements use the Greek General Chart of Accounts (ΕΓΛΣ) classification system. Account codes map directly to standard Greek accounting categories.

### Account Classes

```yaml
EGLS_Account_Classes:
  class_1_assets:
    "10": "Εδαφικές εκτάσεις (Land)"
    "11": "Κτίρια - εγκαταστάσεις (Buildings)"
    "12": "Μηχανήματα - τεχνικές εγκαταστάσεις (Machinery)"
    "13": "Μεταφορικά μέσα (Transport)"
    "14": "Έπιπλα - λοιπός εξοπλισμός (Furniture & equipment)"
    "16": "Ασώματες ακινητοποιήσεις (Intangible assets)"
    
  class_2_current_assets:
    "20": "Εμπορεύματα (Merchandise)"
    "21": "Προϊόντα (Finished goods)"
    "24": "Πρώτες ύλες (Raw materials)"
    "25": "Αναλώσιμα (Consumables)"
    "30": "Πελάτες (Trade debtors)"
    "33": "Χρεώστες διάφοροι (Other debtors)"
    "38": "Χρηματικά διαθέσιμα (Cash and equivalents)"
    
  class_4_equity_and_liabilities:
    "40": "Κεφάλαιο (Share capital)"
    "41": "Αποθεματικά (Reserves)"
    "42": "Αποτελέσματα εις νέο (Retained earnings)"
    "44": "Προβλέψεις (Provisions)"
    "45": "Μακροπρόθεσμες υποχρεώσεις (Long-term liabilities)"
    "50": "Προμηθευτές (Trade creditors)"
    "53": "Πιστωτές διάφοροι (Other creditors)"
    "54": "Υποχρεώσεις από φόρους (Tax liabilities)"
    "55": "Ασφαλιστικοί οργανισμοί (Social security payable)"
    
  class_6_expenses:
    "60": "Αγορές (Purchases)"
    "61": "Μεταβολή αποθεμάτων (Inventory changes)"
    "62": "Παροχές τρίτων (Third-party services)"
    "63": "Φόροι - τέλη (Taxes and duties)"
    "64": "Λοιπά έξοδα (Other expenses)"
    "65": "Τόκοι και συναφή έξοδα (Interest and related)"
    "66": "Αποσβέσεις (Depreciation)"
    
  class_7_income:
    "70": "Πωλήσεις εμπορευμάτων (Sales of merchandise)"
    "71": "Πωλήσεις προϊόντων (Sales of finished goods)"
    "73": "Πωλήσεις υπηρεσιών (Service revenue)"
    "74": "Επιχορηγήσεις - επιδοτήσεις (Grants and subsidies)"
    "75": "Λοιπά έσοδα (Other income)"
    "76": "Έσοδα κεφαλαίων (Investment income)"
```

### P&L Structure — Αποτελέσματα Χρήσεως

```yaml
PL_Structure:
  revenue:
    label_gr: "Κύκλος εργασιών"
    label_en: "Revenue / Turnover"
    accounts: ["70", "71", "73"]
    
  other_income:
    label_gr: "Λοιπά συνήθη έσοδα"
    label_en: "Other ordinary income"
    accounts: ["74", "75", "76"]
    
  cost_of_sales:
    label_gr: "Κόστος πωλήσεων"
    label_en: "Cost of sales"
    accounts: ["60", "61"]
    
  gross_profit:
    label_gr: "Μικτό κέρδος"
    label_en: "Gross profit"
    calculation: "revenue + other_income - cost_of_sales"
    
  operating_expenses:
    label_gr: "Λειτουργικά έξοδα"
    label_en: "Operating expenses"
    accounts: ["62", "63", "64", "66"]
    
  operating_profit:
    label_gr: "Λειτουργικά αποτελέσματα"
    label_en: "Operating profit"
    calculation: "gross_profit - operating_expenses"
    
  financial_expenses:
    label_gr: "Χρηματοοικονομικά έξοδα"
    label_en: "Financial expenses"
    accounts: ["65"]
    
  net_profit_before_tax:
    label_gr: "Κέρδη προ φόρων"
    label_en: "Net profit before tax"
    calculation: "operating_profit - financial_expenses"
    
  income_tax:
    label_gr: "Φόρος εισοδήματος"
    label_en: "Income tax"
    rate: "22% for AE/EPE, graduated for OE/EE"
    
  net_profit:
    label_gr: "Καθαρά κέρδη μετά φόρων"
    label_en: "Net profit after tax"
    calculation: "net_profit_before_tax - income_tax"
```

### Balance Sheet Structure — Ισολογισμός

```yaml
Balance_Sheet_Structure:
  assets:
    label_gr: "ΕΝΕΡΓΗΤΙΚΟ"
    label_en: "ASSETS"
    
    fixed_assets:
      label_gr: "Πάγια στοιχεία ενεργητικού"
      label_en: "Fixed assets"
      accounts: ["10", "11", "12", "13", "14", "16"]
      show: "gross_value, accumulated_depreciation, net_book_value"
      
    current_assets:
      label_gr: "Κυκλοφοριακά στοιχεία ενεργητικού"
      label_en: "Current assets"
      
      inventories:
        label_gr: "Αποθέματα"
        label_en: "Inventories"
        accounts: ["20", "21", "24", "25"]
        
      receivables:
        label_gr: "Απαιτήσεις"
        label_en: "Receivables"
        accounts: ["30", "33"]
        
      cash:
        label_gr: "Χρηματικά διαθέσιμα"
        label_en: "Cash and equivalents"
        accounts: ["38"]
  
  equity_and_liabilities:
    label_gr: "ΠΑΘΗΤΙΚΟ"
    label_en: "EQUITY & LIABILITIES"
    
    equity:
      label_gr: "Ίδια κεφάλαια"
      label_en: "Equity"
      
      share_capital:
        label_gr: "Κεφάλαιο"
        label_en: "Share capital"
        accounts: ["40"]
        
      reserves:
        label_gr: "Αποθεματικά"
        label_en: "Reserves"
        accounts: ["41"]
        
      retained_earnings:
        label_gr: "Αποτελέσματα εις νέο"
        label_en: "Retained earnings"
        accounts: ["42"]
        
    provisions:
      label_gr: "Προβλέψεις"
      label_en: "Provisions"
      accounts: ["44"]
      
    long_term_liabilities:
      label_gr: "Μακροπρόθεσμες υποχρεώσεις"
      label_en: "Long-term liabilities"
      accounts: ["45"]
      
    current_liabilities:
      label_gr: "Βραχυπρόθεσμες υποχρεώσεις"
      label_en: "Current liabilities"
      
      suppliers:
        label_gr: "Προμηθευτές"
        label_en: "Trade creditors"
        accounts: ["50"]
        
      other_creditors:
        label_gr: "Πιστωτές διάφοροι"
        label_en: "Other creditors"
        accounts: ["53"]
        
      tax_liabilities:
        label_gr: "Υποχρεώσεις από φόρους"
        label_en: "Tax liabilities (VAT, income tax)"
        accounts: ["54"]
        
      social_security:
        label_gr: "Ασφαλιστικοί οργανισμοί"
        label_en: "Social security payable (EFKA)"
        accounts: ["55"]

  validation:
    rule: "total_assets MUST equal total_equity_and_liabilities"
    on_mismatch: "HALT — do not issue. Log high-priority failure. Alert senior accountant."
    never: "Never auto-correct a balance sheet mismatch. Never issue an unbalanced statement."
```

## Versioning & Amendments

### Version Rules

Every statement generation creates a new version. Versions are immutable once created.

```yaml
Versioning:
  first_generation:
    version: 1
    status: "draft"
    transitions: "draft → issued (by senior_accountant review)"
    
  amendment:
    version: "previous_version + 1"
    status: "draft"
    requires: "reason text, reference to what changed"
    preserves: "all prior versions remain in directory"
    
  file_naming:
    json: "{AFM}_{period}_{type}_v{N}.json"
    pdf: "{AFM}_{period}_{type}_v{N}.pdf"
    examples:
      - "EL123456789_2026-01_pl_v1.json"
      - "EL123456789_2026-01_balance-sheet_v1.json"
      - "EL555444333_2025-10_pl_v2.json"  # Amendment
```

### Statement Index

Each client maintains a statement index at `/data/clients/{AFM}/financial-statements/index.json`:

```json
{
  "afm": "EL123456789",
  "statements": [
    {
      "period": "2026-01",
      "type": "pl",
      "version": 1,
      "status": "issued",
      "issued_at": "2026-02-10T14:30:00Z",
      "issued_by": "m.papadopoulos",
      "filename": "EL123456789_2026-01_pl_v1.json"
    },
    {
      "period": "2026-01",
      "type": "balance-sheet",
      "version": 1,
      "status": "issued",
      "issued_at": "2026-02-10T14:30:00Z",
      "issued_by": "m.papadopoulos",
      "filename": "EL123456789_2026-01_balance-sheet_v1.json"
    }
  ]
}
```

### Amendment Workflow

```yaml
Amendment_Process:
  step_1: "Identify the item requiring amendment (e.g., late invoice)"
  step_2: "Load the current latest version for the period"
  step_3: "Apply the correction to the affected accounts"
  step_4: "Recalculate all derived totals (gross profit, net profit, retained earnings)"
  step_5: "Validate balance sheet still balances after amendment"
  step_6: "Create new version file with amendment metadata"
  step_7: "Update index.json with new version entry"
  step_8: "Generate amendment PDF marked as Τροποποίηση (Amendment)"
  step_9: "Log episode to /data/memory/episodes/ with episode_type: amendment_issued"
  
  amendment_metadata:
    reason: "Free text describing why the amendment was needed"
    original_version: "Reference to the version being amended"
    changes: "Line-by-line diff of what changed"
    impact: "Net effect on profit/loss and balance sheet"
    discovered_date: "When the error/omission was discovered"
```

## Period Comparison

### Variance Analysis

```yaml
Variance_Analysis:
  comparison_types:
    year_over_year: "Same period current year vs prior year"
    sequential: "Current period vs immediately prior period"
    budget_vs_actual: "Actual figures vs budget (when budget exists)"
    
  variance_calculation:
    absolute: "current_amount - comparison_amount"
    percentage: "((current_amount - comparison_amount) / comparison_amount) * 100"
    
  significance_threshold:
    default: "15%"
    configurable: "--threshold N"
    categories:
      - "SIGNIFICANT: variance >= threshold"
      - "NOTABLE: variance >= threshold/2 and < threshold"
      - "NORMAL: variance < threshold/2"
      
  output_format:
    grouping: "By category (revenue, cost of sales, operating expenses)"
    labels: "Greek account label alongside English label"
    presentation: "Plain English suitable for accounting assistant"
```

## Output Formats

### Machine-Readable JSON

Written to `/data/clients/{AFM}/financial-statements/`:

```json
{
  "afm": "EL123456789",
  "client_name": "ALPHA TRADING AE",
  "period": "2026-01",
  "type": "pl",
  "version": 1,
  "status": "draft",
  "generated_at": "2026-02-10T14:00:00Z",
  "generated_by": "openclaw-greek-financial-statements",
  "revenue": {
    "70_goods_sales": {"label_gr": "Πωλήσεις εμπορευμάτων", "amount": 28400.00},
    "73_service_revenue": {"label_gr": "Πωλήσεις υπηρεσιών", "amount": 18920.00},
    "total": 47320.00
  },
  "cost_of_sales": {
    "60_materials": {"label_gr": "Αγορές", "amount": 14200.00},
    "total": 14200.00
  },
  "gross_profit": 33120.00,
  "operating_expenses": {
    "62_services": {"label_gr": "Παροχές τρίτων", "amount": 4800.00},
    "64_staff": {"label_gr": "Λοιπά έξοδα", "amount": 9200.00},
    "66_depreciation": {"label_gr": "Αποσβέσεις", "amount": 1200.00},
    "total": 15200.00
  },
  "operating_profit": 17920.00,
  "net_profit": 17920.00,
  "completeness_gate": {
    "banking_reconciliation": "complete",
    "vat_filing": "prepared",
    "efka_contributions": "calculated",
    "ocr_queue": "clear"
  }
}
```

### Client-Facing PDF

Written to `/data/reports/client/`:

```yaml
PDF_Layout:
  header:
    title_gr: "ΑΠΟΤΕΛΕΣΜΑΤΑ ΧΡΗΣΕΩΣ" # or "ΙΣΟΛΟΓΙΣΜΟΣ"
    title_en: "Profit & Loss Statement" # or "Balance Sheet"
    client_name: "ALPHA TRADING AE"
    afm: "EL123456789"
    period: "Ιανουάριος 2026 / January 2026"
    version: "v1"
    
  body:
    format: "Greek labels primary, English in parentheses"
    currency: "EUR with € symbol"
    decimal_format: "European (comma as decimal separator in Greek version)"
    
  footer:
    disclaimer: "Prepared with automated assistance. Should be reviewed by a licensed accountant before reliance."
    generated_at: "Timestamp in Europe/Athens timezone"
    skill_version: "openclaw-greek-financial-statements v1.0.0"
    
  amendment_marking:
    if_amendment: "Clearly marked as ΤΡΟΠΟΠΟΙΗΣΗ (Amendment)"
    reference: "References original version number and issue date"
    changes_summary: "Brief description of what changed"
```

## Data Sources

### Read Locations

```yaml
Data_Sources:
  banking_reconciliation:
    path: "/data/clients/{AFM}/compliance/"
    also: "/data/banking/"
    fields: "opening_cash, closing_cash, total_income, total_expenses, status"
    
  vat_filing:
    path: "/data/compliance/vat/"
    filename: "{AFM}_{YYYYMM}_vat_return.xml"
    fields: "output_vat, input_vat, net_vat_payable, vat_rate_breakdown"
    
  efka_contributions:
    path: "/data/efka/"
    fields: "employer_contributions, employee_deductions, total_payroll_gross"
    
  client_documents:
    path: "/data/clients/{AFM}/documents/"
    fields: "Processed invoices, receipts, contracts with amounts and ΕΓΛΣ codes"
    
  prior_statements:
    path: "/data/clients/{AFM}/financial-statements/"
    fields: "index.json for version history, prior period JSON for comparison"
```

### Write Locations

```yaml
Output_Locations:
  json_statements:
    path: "/data/clients/{AFM}/financial-statements/"
    files: "{AFM}_{period}_{type}_v{N}.json"
    also: "index.json (updated with new entry)"
    
  pdf_reports:
    path: "/data/reports/client/"
    files: "{AFM}_{period}_financial-pack_v{N}.pdf"
    
  episodes:
    path: "/data/memory/episodes/"
    types: ["statement_generated", "amendment_issued", "readiness_checked"]
    
  failures:
    path: "/data/memory/failures/"
    types: ["completeness_gate_failed", "balance_sheet_mismatch", "generation_error"]
```

## Error Handling

### Balance Sheet Mismatch

```yaml
Balance_Sheet_Mismatch:
  detection: "total_assets != total_equity_and_liabilities"
  action: "HALT immediately — never issue"
  logging:
    priority: "HIGH"
    destination: "/data/memory/failures/"
    failure_type: "balance_sheet_mismatch"
    fields: ["total_assets", "total_equity_and_liabilities", "difference"]
  alert: "Notify senior accountant via dashboard"
  suggestions:
    - "Check for unrecorded liabilities"
    - "Check for misclassified accounts between asset and liability classes"
    - "Check for data entry errors in source documents"
    - "Verify that all bank reconciliation items have been processed"
  never: "Never auto-correct the difference. Never issue an unbalanced statement as draft."
```

### Missing Prior Period

```yaml
Missing_Prior_Period:
  first_period:
    action: "Proceed — this is expected for newly onboarded clients"
    note: "Comparison features disabled for first period"
    
  gap_in_periods:
    action: "WARN — allow generation but flag the gap"
    note: "Prior period comparison will show 'prior period unavailable'"
```

## Integration with Other Skills

### Meta-Skill Integration
```bash
# Monthly process includes statement generation
openclaw greek monthly-process --client EL123456789 --period 2026-01
# → Triggers completeness gate → generates statements if ready

# End-of-year process
openclaw greek annual-close --client EL123456789 --year 2025
# → Generates annual P&L + balance sheet + annual summary
```

### Dashboard Integration
```bash
# Statement readiness feeds into dashboard compliance scoring
openclaw dashboard refresh --include-statement-readiness

# Statement generation events appear in dashboard activity feed
```

### Client Communication Integration
```bash
# Send statement pack to client after senior accountant approval
openclaw comms draft --afm EL123456789 --type monthly-statements --period 2026-01
# → Attaches PDF statement pack to bilingual cover letter
```

### Analytics Integration
```bash
# Statement data feeds into trend analysis and benchmarking
openclaw analytics portfolio-trends --metric revenue --periods 12
# → Reads from /data/clients/{AFM}/financial-statements/ across all clients
```

## Professional Liability

Every generated statement includes:
- A disclaimer noting automated preparation
- A recommendation for licensed accountant review
- The version number and generation timestamp
- The completeness gate results at time of generation

Statements are generated as **drafts** by default. Only a user with `senior_accountant` role or above may change status to `issued` through the review workflow.
