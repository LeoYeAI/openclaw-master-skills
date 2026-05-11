---
name: client-data-management
description: Secure client database for Greek accounting firms. Manages profiles, AFM numbers, compliance history with encryption and GDPR compliance.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "client-management", "gdpr", "onboarding"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "openclaw"], "env": ["OPENCLAW_DATA_DIR"]}, "notes": "Instruction-only skill. Manages client records stored as JSON files in OPENCLAW_DATA_DIR/clients/. No external services or credentials required. Handles GDPR data lifecycle locally.", "path_prefix": "/data/ in examples refers to $OPENCLAW_DATA_DIR (default: /data/)"}}
---

# Client Data Management

This skill provides a secure, file-based client database for Greek accounting firms operating through OpenClaw. It manages all client master data, compliance history, document metadata, and relationship records while enforcing encryption, access control, and GDPR requirements for Greek business operations.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
which jq || sudo apt install jq
mkdir -p $OPENCLAW_DATA_DIR/clients
```

No external credentials required. Manages client records as JSON files in the local filesystem. Handles GDPR data lifecycle locally.


## Core Philosophy

- **File-Based Security**: Encrypted JSON files managed through OpenClaw, no external database required
- **Greek Business Focus**: Built around AFM (VAT numbers), EFKA employer IDs, GEMI numbers, and Greek regulatory identifiers
- **GDPR by Default**: All personal data handled with consent tracking, retention policies, and deletion workflows
- **Audit Everything**: Every read, write, and delete of client data is logged with user identity and timestamp
- **Assistant-Friendly**: English interface with structured commands for non-technical accounting assistants
- **Integration Hub**: Client records link to all other skills — compliance, banking, EFKA, deadlines, OCR

## OpenClaw Commands

### Client Registration & Profile Management
```bash
# Register new client
openclaw clients add --name "ALPHA TRADING AE" --afm EL123456789 --legal-form AE --sector retail
openclaw clients add --name "BETA SERVICES OE" --afm EL987654321 --legal-form OE --sector services --gemi 012345678

# Update client profile
openclaw clients update --afm EL123456789 --field registered-address --value "Οδός Αθηνών 45, Αθήνα 10431"
openclaw clients update --afm EL123456789 --field contact-email --value "info@alphatrading.gr"
openclaw clients update --afm EL123456789 --field accountant-assigned --value "maria.g"

# View client profile
openclaw clients view --afm EL123456789 --full-profile
openclaw clients view --afm EL123456789 --compliance-summary
openclaw clients view --name "ALPHA TRADING AE" --format table

# Deactivate / archive client
openclaw clients deactivate --afm EL123456789 --reason "ceased-trading" --archive-data
openclaw clients reactivate --afm EL123456789 --effective-date 2026-03-01
```

### Client Search & Listing
```bash
# Search and filter
openclaw clients list --all --format table
openclaw clients list --sector retail --active-only
openclaw clients list --legal-form AE --missing-documents
openclaw clients list --assigned-to "maria.g" --compliance-risk high

# Search by various identifiers
openclaw clients search --query "ALPHA" --field name
openclaw clients search --afm EL123456789
openclaw clients search --efka-id 12345678
openclaw clients search --gemi 012345678

# Portfolio views
openclaw clients portfolio --summary --by-sector
openclaw clients portfolio --compliance-scores --rank-by risk
openclaw clients portfolio --workload-estimate --by-assignee
```

### Compliance History & Filing Records
```bash
# Log a completed filing
openclaw clients log-filing --afm EL123456789 --type VAT-monthly --period 2026-01 --status submitted --ref-number "AAΔ-123456"
openclaw clients log-filing --afm EL123456789 --type EFKA-monthly --period 2026-01 --status paid --amount 4250.00

# View compliance history
openclaw clients compliance-history --afm EL123456789 --type VAT --last 12-months
openclaw clients compliance-history --afm EL123456789 --all-types --format report
openclaw clients compliance-gaps --afm EL123456789 --flag-missing
openclaw clients compliance-gaps --all-clients --period 2025 --export csv

# Upcoming obligations
openclaw clients obligations --afm EL123456789 --next 30-days
openclaw clients obligations --all-clients --due-this-week --prioritize
```

### Document Registry
```bash
# Register a document against a client
openclaw clients doc-register --afm EL123456789 --type invoice --file /data/ocr/output/accounting-ready/inv_001.pdf --date 2026-02-01 --amount 5400.00
openclaw clients doc-register --afm EL123456789 --type tax-return --file /data/compliance/e1/EL123456789_2025_e1_form.xml --tax-year 2025

# Query document registry
openclaw clients doc-list --afm EL123456789 --type invoice --period 2026-01
openclaw clients doc-list --afm EL123456789 --missing --type bank-statement
openclaw clients doc-find --afm EL123456789 --filename "E1_2025"
openclaw clients doc-summary --afm EL123456789 --by-type --count

# Document status tracking
openclaw clients doc-status --afm EL123456789 --awaiting-review
openclaw clients doc-status --all-clients --unprocessed --flag-urgent
```

### Contact & Relationship Management
```bash
# Manage client contacts
openclaw clients contact-add --afm EL123456789 --name "ΓιώÏγος Παπαδόπουλος" --role "CEO" --email "gp@alphatrading.gr" --phone "+30 210 1234567"
openclaw clients contact-update --afm EL123456789 --contact-id C001 --field phone --value "+30 6944 123456"
openclaw clients contact-list --afm EL123456789 --format table
openclaw clients contact-primary --afm EL123456789 --set C001

# Notes and relationship log
openclaw clients note-add --afm EL123456789 --note "Client prefers PDF reports by email end of month"
openclaw clients note-add --afm EL123456789 --type meeting --date 2026-02-15 --summary "Discussed Q1 tax planning"
openclaw clients notes-view --afm EL123456789 --last 10 --type all
```

### GDPR & Data Privacy
```bash
# Consent management
openclaw clients gdpr-consent --afm EL123456789 --record --type data-processing --granted-by "ΓιώÏγος Παπαδόπουλος" --date 2026-01-01
openclaw clients gdpr-consent --afm EL123456789 --status

# Data subject requests
openclaw clients gdpr-export --afm EL123456789 --format json --output /data/gdpr-exports/
openclaw clients gdpr-delete --afm EL123456789 --confirm --reason "client-request" --retention-override

# Retention management
openclaw clients retention-check --all-clients --flag-expired
openclaw clients retention-archive --afm EL123456789 --older-than 7-years --type financial-records
openclaw clients gdpr-audit --period last-year --report
```

### Data Import & Export
```bash
# Bulk import from spreadsheet
openclaw clients import --file /data/imports/client_list.xlsx --validate-afm --dry-run
openclaw clients import --file /data/imports/client_list.xlsx --execute --skip-duplicates

# Export client data
openclaw clients export --all --format xlsx --output /data/exports/all_clients.xlsx
openclaw clients export --afm EL123456789 --format json --include-history
openclaw clients export --filter active --fields name,afm,sector,assignee --format csv
```

### Database Maintenance & Health
```bash
# Validation and integrity
openclaw clients validate-afm --all --flag-invalid
openclaw clients check-duplicates --by afm --report
openclaw clients integrity-check --cross-reference compliance-history
openclaw clients health-report --summary

# Backup and restore
openclaw clients backup --output /data/backups/clients_$(date +%Y%m%d).json --encrypt
openclaw clients backup-list --last 10
openclaw clients restore --backup /data/backups/clients_20260201.json --dry-run

# Audit log access
openclaw clients audit-log --afm EL123456789 --last 30-days
openclaw clients audit-log --all --action delete --period last-week
openclaw clients audit-log --user "maria.g" --period last-month
```

## File System Architecture

```yaml
Client_Data_File_Structure:
  client_profiles:
    - /data/clients/{afm}/profile.json          # Master client record
    - /data/clients/{afm}/contacts.json          # Contact persons
    - /data/clients/{afm}/identifiers.json       # AFM, EFKA, GEMI, other IDs
    - /data/clients/{afm}/notes.json             # Relationship notes and history

  compliance_records:
    - /data/clients/{afm}/compliance/filings.json        # All filing history
    - /data/clients/{afm}/compliance/obligations.json    # Recurring obligations
    - /data/clients/{afm}/compliance/gaps.json           # Missing filings log

  document_registry:
    - /data/clients/{afm}/documents/registry.json        # Document metadata index
    - /data/clients/{afm}/documents/pending.json         # Awaiting processing
    - /data/clients/{afm}/documents/archive-index.json   # Archived doc references

  gdpr_records:
    - /data/clients/{afm}/gdpr/consent.json              # Consent records
    - /data/clients/{afm}/gdpr/retention-policy.json     # Retention schedule
    - /data/clients/{afm}/gdpr/deletion-log.json         # Deletion audit trail

  system_files:
    - /data/clients/_index.json                  # Global client index (unencrypted metadata)
    - /data/clients/_audit-log.json              # All access/change events
    - /data/clients/_schema-version.json         # Schema version for migrations
    - /data/backups/                             # Encrypted backup directory
```

## Client Record Schema

### Master Profile (profile.json)
```yaml
Client_Profile:
  # Identity
  afm: "EL123456789"                    # Greek VAT number (primary key)
  name: "ALPHA TRADING AE"             # Registered business name (Greek)
  name_latin: "Alpha Trading AE"       # Latin transliteration
  legal_form: "AE"                     # ΑΕ, ΕΠΕ, ΟΕ, ΕΕ, ΘΚΕ, ΑΤΟΜΘΚΔ, etc.
  gemi: "012345678"                    # Business registry number
  efka_employer_id: "12345678"         # EFKA employer identifier

  # Classification
  sector: "retail"                     # Business sector
  activity_code: "4711"               # ΚΑΔ (Greek activity code)
  activity_description: "Retail general merchandise"
  vat_regime: "normal"                # normal | simplified | exempt | agricultural
  vat_period: "monthly"               # monthly | quarterly

  # Registration
  registered_address: "Οδός Αθηνών 45, Αθήνα 10431"
  tax_office: "Α' ΑΘΔÎΩÎ"            # ΑÏμόδια ΔΟΥ
  municipality: "ΑΘΔÎΑ"

  # Status
  status: "active"                    # active | inactive | archived | ceased
  client_since: "2022-01-15"
  ceased_date: null
  cease_reason: null

  # Internal management
  assigned_accountant: "yannis.k"
  assigned_assistant: "maria.g"
  priority: "normal"                  # low | normal | high | vip
  billing_tier: "standard"

  # Metadata
  created_at: "2022-01-15T09:00:00Z"
  updated_at: "2026-02-01T14:30:00Z"
  created_by: "yannis.k"
  last_modified_by: "maria.g"
```

### Identifiers Record (identifiers.json)
```yaml
Client_Identifiers:
  afm: "EL123456789"
  gemi: "012345678"
  efka_employer_id: "12345678"
  doy_code: "A1"                      # Tax office code
  municipal_id: "ATH-2022-045123"    # Municipality business registration
  insurance_class: "B"               # EFKA insurance class
  mydata_branch_id: null             # myDATA branch identifier if applicable
  bank_accounts:
    - iban: "GR1601101250000000012300695"
      bank: "Alpha Bank"
      primary: true
    - iban: "GR7601402010540540002502139"
      bank: "National Bank of Greece"
      primary: false
```

### Filing Record Schema (filings.json entries)
```yaml
Filing_Record:
  filing_id: "VAT-EL123456789-2026-01"
  afm: "EL123456789"
  type: "VAT-monthly"               # Filing type
  period: "2026-01"                 # Period covered
  due_date: "2026-02-28"
  submitted_date: "2026-02-20"
  status: "submitted"               # pending | submitted | accepted | rejected | paid | overdue
  reference_number: "ΑΑΔ-123456"   # Government reference
  amount_declared: 12500.00
  amount_paid: 12500.00
  payment_date: "2026-02-20"
  submitted_by: "yannis.k"
  notes: null
  created_at: "2026-02-20T10:15:00Z"
```

## Greek Business Entity Types

```yaml
Legal_Forms:
  AE:
    full_name: "Ανώνυμη ΕταιÏεία"
    english: "Société Anonyme / Public Ltd"
    min_capital: 25000
    gemi_required: true
    efka_required: true

  EPE:
    full_name: "ΕταιÏεία ΠεÏιοÏισμένης ΕυθÏνης"
    english: "Limited Liability Company"
    min_capital: 1
    gemi_required: true

  IKE:
    full_name: "Θδιωτική Κεφαλαιουχική ΕταιÏεία"
    english: "Private Capital Company"
    min_capital: 0
    gemi_required: true

  OE:
    full_name: "ΟμόÏÏυθμη ΕταιÏεία"
    english: "General Partnership"
    gemi_required: true

  EE:
    full_name: "ΕτεÏόÏÏυθμη ΕταιÏεία"
    english: "Limited Partnership"
    gemi_required: true

  ATOMIKI:
    full_name: "Ατομική ΕπιχείÏηση"
    english: "Sole Trader"
    gemi_required: false
```

## Compliance Obligation Templates

```yaml
Obligation_Templates:
  VAT_monthly:
    trigger: "legal_form in [AE, EPE, IKE] AND revenue > 1500000"
    frequency: monthly
    due_day: "last day of following month"
    skill_link: "greek-compliance-aade"

  VAT_quarterly:
    trigger: "vat_regime = normal AND revenue <= 1500000"
    frequency: quarterly
    due_day: "last day of month following quarter end"
    skill_link: "greek-compliance-aade"

  EFKA_monthly:
    trigger: "efka_employer_id IS NOT NULL"
    frequency: monthly
    due_day: "last day of following month"
    skill_link: "efka-api-integration"

  myDATA_continuous:
    trigger: "all active businesses"
    frequency: continuous
    note: "invoices must be submitted within legal timeframe"
    skill_link: "aade-api-monitor"

  corporate_tax_annual:
    trigger: "legal_form in [AE, EPE, IKE, OE, EE]"
    frequency: annual
    due_month: "June"
    skill_link: "greek-compliance-aade"

  E3_annual:
    trigger: "all active businesses"
    frequency: annual
    due_month: "June"
    skill_link: "accounting-workflows"
```

## Security & Encryption

### Encryption Configuration
```yaml
Encryption:
  algorithm: "AES-256-GCM"
  key_management: "OpenClaw key vault"
  encrypted_fields:
    - bank_account_numbers
    - contact_personal_data
    - gdpr_consent_records
    - financial_amounts_in_history
  unencrypted_fields:
    - afm (required for indexing)
    - client_name (required for search)
    - status
    - sector
  key_rotation: "annual"
  backup_encryption: "separate key"
```

### Access Control Integration
```yaml
Data_Access_Rules:
  senior_accountant:
    read: "all clients"
    write: "all clients"
    delete: "with confirmation"
    gdpr_operations: true
    export_all: true

  accountant:
    read: "assigned clients only"
    write: "assigned clients only"
    delete: false
    gdpr_operations: false
    export: "assigned clients only"

  assistant:
    read: "assigned clients — profile, contacts, document list"
    write: "notes, document registry entries"
    delete: false
    sensitive_fields: "hidden (bank accounts, full financials)"
    export: false

  viewer:
    read: "assigned clients — name, status, next deadline only"
    write: false
    delete: false
```

## Integration with Other Skills

```yaml
Skill_Integration:
  dashboard_greek_accounting:
    provides: ["client list", "compliance scores", "portfolio metrics"]
    consumes: ["dashboard requests for client data"]
    commands: "openclaw clients portfolio-summary → dashboard aggregation"

  greek_compliance_aade:
    provides: ["filing records for compliance history"]
    consumes: ["client AFM, VAT regime, filing obligations"]
    sync: "openclaw clients log-filing after each aade compliance action"

  efka_api_integration:
    provides: ["EFKA contribution records"]
    consumes: ["client EFKA employer ID, employee roster"]
    sync: "openclaw clients log-filing --type EFKA after submissions"

  cli_deadline_monitor:
    provides: ["upcoming deadlines per client"]
    consumes: ["client obligation schedule from compliance templates"]
    sync: "openclaw clients obligations feeds deadline monitoring"

  greek_banking_integration:
    provides: ["bank feed status per client"]
    consumes: ["client IBAN list from identifiers.json"]
    sync: "banking reconciliation references client record"

  greek_document_ocr:
    provides: ["extracted document data for registry"]
    consumes: ["client AFM to tag processed documents"]
    sync: "openclaw clients doc-register after OCR completes"

  user_authentication_system:
    provides: ["user identity and role for access decisions"]
    consumes: ["client assignment data for per-client authorization"]
    enforcement: "every client data operation checks auth before executing"
```

## Usage Examples

### Example 1: Onboarding a New Client
```markdown
Command: openclaw clients add --name "GAMMA IMPORT OE" --afm EL555444333 --legal-form OE --sector imports --gemi 098765432
System:
1. Validates AFM format (EL + 9 digits)
2. Creates /data/clients/EL555444333/ directory structure
3. Writes profile.json with provided data
4. Generates obligation template based on legal form + sector
5. Creates empty filings.json, contacts.json, documents/registry.json
6. Adds entry to /data/clients/_index.json
7. Logs creation event to audit trail
8. Output: "Client EL555444333 created. 4 recurring obligations configured. Assign accountant: openclaw clients update --afm EL555444333 --field accountant-assigned --value [username]"
```

### Example 2: Monthly Compliance Check
```markdown
Command: openclaw clients compliance-gaps --all-clients --period 2026-01
System:
1. Reads obligation templates for every active client
2. Cross-references against filings.json for period 2026-01
3. Identifies: 3 clients missing VAT submission, 1 client missing EFKA
4. Checks due dates — 2 are overdue, 2 due within 5 days
5. Output: Formatted table with client name, AFM, missing filing type, due date, assigned accountant
6. Optionally: openclaw clients compliance-gaps --all-clients --period 2026-01 --alert-assignees
```

### Example 3: GDPR Data Export Request
```markdown
Command: openclaw clients gdpr-export --afm EL123456789 --format json --output /data/gdpr-exports/
System:
1. Collects all data held: profile, contacts, filings, document registry, notes, audit log entries
2. Decrypts encrypted fields for export (requires senior_accountant role)
3. Formats as structured JSON with data categories labeled
4. Writes to /data/gdpr-exports/EL123456789_gdpr_export_20260218.json
5. Logs export event with requesting user and timestamp
6. Output: "GDPR export complete. File: EL123456789_gdpr_export_20260218.json (47 records, 12 categories)"
```

### Example 4: Document Registration After OCR
```markdown
Command: openclaw clients doc-register --afm EL123456789 --type invoice --file /data/ocr/output/accounting-ready/inv_2026_001.pdf --date 2026-02-10 --amount 3200.00 --vendor "DELTA SUPPLIES AE"
System:
1. Validates client exists and user has write access
2. Checks for duplicate (same file path not already registered)
3. Appends entry to /data/clients/EL123456789/documents/registry.json
4. Updates document count in client index
5. Logs registration to audit trail
6. Output: "Document registered: inv_2026_001.pdf → EL123456789. Registry now contains 23 documents for this client."
```

## Error Handling

```bash
# Common validation errors and resolution commands
openclaw clients validate-afm --afm EL99999999       # Invalid format → shows correct format
openclaw clients check-duplicates --afm EL123456789   # Duplicate check before add
openclaw clients repair-index                          # Rebuild _index.json from individual profiles
openclaw clients schema-migrate --to-version 2         # Apply schema updates across all records
openclaw clients integrity-report                      # Full cross-reference check across all data
```

## Audit Log Format

```yaml
Audit_Event:
  event_id: "AUD-20260218-001234"
  timestamp: "2026-02-18T10:30:00Z"
  user: "maria.g"
  role: "assistant"
  action: "read"                       # read | write | delete | export | gdpr
  resource: "client_profile"
  afm: "EL123456789"
  client_name: "ALPHA TRADING AE"
  fields_accessed: ["name", "status", "next_deadline"]
  ip_address: "192.168.1.45"
  result: "success"
  notes: null
```

## Safety & Compliance Guidelines

### Data Handling Principles
- Never store raw bank credentials or passwords — only IBANs and account references
- All personal contact data (natural persons) is encrypted at rest
- Client financial history is retained for minimum 10 years per Greek law (Law 4308/2014)
- GDPR Article 17 deletion requests must preserve data required by Greek tax law for retention period
- Separation between clients is absolute — no cross-client data access or reporting without explicit multi-client permission

### GDPR Retention Schedule
```yaml
Retention_Periods:
  financial_records: "10 years (Greek accounting law)"
  tax_filings: "10 years (tax authority requirement)"
  contact_data: "duration of engagement + 3 years"
  audit_logs: "5 years"
  gdpr_consent_records: "duration of processing + 3 years"
  deleted_client_data: "immediately purged except legally mandated retention"
```

Remember: This skill is the single source of truth for all client master data. Every other skill references client records here. Data quality, completeness, and security in this skill directly determines the quality of all other skill outputs across the entire OpenClaw Greek Accounting system.
