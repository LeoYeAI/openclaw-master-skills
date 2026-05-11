---
name: openclaw-greek-accounting-meta
description: Orchestrator for the full OpenClaw Greek Accounting system. Routes commands across 18 specialist skills. Primary entry point for accounting firms.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "meta-skill", "orchestration"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "openclaw"], "env": ["OPENCLAW_DATA_DIR"]}, "depends_on": ["accounting-workflows", "greek-compliance-aade", "cli-deadline-monitor", "greek-email-processor", "greek-individual-taxes", "aade-api-monitor", "greek-banking-integration", "greek-document-ocr", "efka-api-integration", "dashboard-greek-accounting", "client-data-management", "user-authentication-system", "conversational-ai-assistant", "greek-financial-statements", "client-communication-engine", "system-integrity-and-backup", "analytics-and-advisory-intelligence", "memory-feedback"], "notes": "Orchestrator skill. Coordinates all other Greek accounting skills. Install companion skills for full functionality. This skill alone only routes commands — actual capabilities come from the skills it depends on.", "path_prefix": "/data/ in examples refers to $OPENCLAW_DATA_DIR (default: /data/)"}}
---

# OpenClaw Greek Accounting Meta-Skill

This meta-skill is the primary entry point for the entire OpenClaw Greek Accounting system. It orchestrates all 18 specialised skills through simple business commands, managing data flow, sequencing, error recovery, and human confirmation gates for government submissions.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
which jq || sudo apt install jq

# Install companion skills (this orchestrator needs them to be useful)
# See the full skill list at: https://github.com/satoshistackalotto/openclaw-greek-accounting
```

This is the orchestrator skill — it coordinates all other Greek accounting skills. Install companion skills for actual functionality. This skill alone only routes commands.


## Core Philosophy

- **Single Entry Point**: One meta-skill controls the entire system — accountants and assistants never need to address individual skills directly
- **Business-Focused Commands**: Simple commands that match real accounting workflows
- **Skill Orchestration**: Automatically manages interactions between all 18 specialised skills
- **Human Confirmation Gate**: Any action submitting to a government system (AADE, EFKA, myDATA) requires explicit human confirmation before proceeding
- **Error Recovery**: Handles failures gracefully with fallback strategies
- **Progress Reporting**: Clear visibility into complex multi-step processes
- **Greek Business Standards**: Professional output matching Greek accounting practices

## Meta-Skill Architecture

### Managed Skills — Full Registry
```yaml
Required_Skills:

  phase_1_core:
    - accounting-workflows        # Document processing, invoice extraction, reconciliation
    - greek-compliance-aade       # VAT returns, payroll, myDATA, TAXIS XML
    - cli-deadline-monitor        # AADE/EFKA/municipal deadline tracking
    - greek-email-processor       # Greek email classification, attachment extraction
    - greek-individual-taxes      # E1 forms, individual tax returns, deduction optimisation

  phase_2_advanced:
    - aade-api-monitor            # Real-time AADE monitoring, regulatory change detection
    - greek-banking-integration   # Bank statement import, transaction categorisation
    - greek-document-ocr          # Greek language OCR, structured data extraction
    - efka-api-integration        # Social security contributions, EFKA declarations

  phase_3a_infrastructure:
    - dashboard-greek-accounting  # Business intelligence, compliance monitoring, alerts (English UI)
    - client-data-management      # Client master records, compliance history, GDPR (sole writer to /data/clients/)
    - user-authentication-system  # Role-based access, per-client permissions, audit logs
    - conversational-ai-assistant # Natural language interface for assistants (English queries, Greek data)

  phase_3b_professional_outputs:
    - greek-financial-statements  # P&L, balance sheet, cash flow, VAT summary — EGLS-compliant Greek format
    - client-communication-engine # Outgoing Greek correspondence — confirmations, summaries, requests, reminders
    - system-integrity-and-backup # Encrypted backups, integrity checks, retention enforcement, schema migrations
    - analytics-and-advisory      # Proactive risk scoring, trend analysis, anomaly detection, morning advisory

  openclaw_dependencies:
    - deepread                    # OCR and text extraction
    - pdf-tools                   # PDF manipulation
    - file-processor              # File organisation and batch processing
    - doc-converter               # Document format conversion

Installation_Command:
  setup: "npx openclaw skills add openclaw-greek-accounting-meta --install-deps"
  verification: "openclaw greek health-check --verify-all-skills"
```

## Business-Focused Commands

### 1. Monthly Accounting Workflows

#### Complete Monthly Processing
```bash
# Single command for full monthly accounting cycle
openclaw greek monthly-process --afm EL123456789 --month 2026-02

# What it orchestrates internally:
# 1. openclaw auth check-access --client EL123456789 --action compliance_management
# 2. openclaw deadline check aade --client EL123456789  (confirm deadlines and due dates)
# 3. openclaw email scan-folder /data/incoming/ --classify-new  (classify any new documents)
# 4. openclaw ocr process-greek --input-dir /data/ocr/incoming/  (OCR new documents)
# 5. openclaw accounting batch-process --input-dir /data/ocr/output/accounting-ready/
# 6. openclaw banking reconcile --afm EL123456789 --period 2026-02
# 7. openclaw compliance vat-return --client EL123456789 --period 2026-02 --prepare
# 8. openclaw efka contribution-calc --afm EL123456789 --period 2026-02
# ⚠️  HUMAN CONFIRMATION REQUIRED — displays full filing details before proceeding
# 9. openclaw compliance vat-return --client EL123456789 --period 2026-02 --submit
# 10. openclaw efka submit-declaration --afm EL123456789 --period 2026-02
# 11. openclaw clients log-filing --afm EL123456789 --type VAT-monthly --period 2026-02 --status submitted
# 12. openclaw clients log-filing --afm EL123456789 --type EFKA-monthly --period 2026-02 --status submitted
# 13. openclaw dashboard refresh --client EL123456789
```

#### Quick Status Check
```bash
# Rapid overview of current status
openclaw greek status-check --include-urgent

# Output example:
# ✅ All government systems operational (AADE, EFKA, myDATA)
# ⚠️  3 VAT returns due in 7 days
# 🚨 1 AADE notification requires attention
# 📊 15 documents in OCR queue, 3 awaiting review
```

### 2. Client Management Workflows

#### New Client Onboarding
```bash
# Complete new client setup — requires accountant role or above
openclaw greek client-onboarding --afm EL123456789 --name "NEW CLIENT AE" --legal-form AE --sector retail

# Orchestrates:
# 1. openclaw auth check-access --action create_client  (permission gate)
# 2. openclaw clients add --afm EL123456789 --name "NEW CLIENT AE" --legal-form AE --sector retail
# 3. openclaw clients obligations --afm EL123456789  (generate obligation schedule)
# 4. openclaw deadline check aade  (pull relevant upcoming deadlines)
# 5. openclaw dashboard sync-clients --rebuild  (update portfolio view)
```

#### Client Document Processing
```bash
# Process all new documents for a specific client
openclaw greek client-process --afm EL123456789 --period current-month

# Orchestrates:
# 1. openclaw auth check-access --client EL123456789 --action process_documents
# 2. openclaw ocr process-greek --input-dir /data/ocr/incoming/  (OCR any new scans)
# 3. openclaw accounting batch-process --input-dir /data/ocr/output/accounting-ready/ --greek-format
# 4. openclaw clients doc-register --afm EL123456789  (register each document)
# 5. openclaw dashboard document-queue --count  (refresh queue status)
```

### 3. Compliance & Tax Workflows

#### Tax Season Preparation
```bash
# Prepare all individual tax returns
openclaw greek tax-season-prep --year 2025 --deadline-check

# Orchestrates:
# 1. Collect all individual client data
# 2. Optimize deductions for each client
# 3. Prepare E1 forms with TAXIS formatting
# 4. Generate document checklists
# 5. Schedule submission reminders
```

#### Emergency Compliance Response
```bash
# Handle urgent compliance issues
openclaw greek emergency-compliance --type audit --entity "DEMO AE"

# Responds to:
# 1. AADE audit notifications (immediate alert)
# 2. Deadline changes (update all affected clients)
# 3. System outages (switch to manual processing)
# 4. Missing documents (generate urgent requests)
```

### 4. Government Integration Workflows

#### AADE Integration Suite
```bash
# Complete AADE interaction management
openclaw greek aade-sync --check-updates --submit-pending

# Coordinates:
# 1. Check for new AADE announcements
# 2. Update deadline trackers
# 3. Submit pending VAT returns
# 4. Verify myDATA submissions
# 5. Download compliance certificates
```

#### Multi-Municipality Management
```bash
# Handle clients across different municipalities
openclaw greek municipal-sync --all-locations

# Manages:
# 1. Athens-specific requirements and deadlines
# 2. Thessaloniki municipal variations  
# 3. Other municipality-specific taxes and permits
# 4. Cross-municipality client coordination
```

## Implementation Workflows

### Meta-Skill Orchestration Engine
```python
class GreekAccountingOrchestrator:
    def __init__(self):
        self.skills = {
            # Phase 1 — Core
            'accounting':   'accounting-workflows',
            'compliance':   'greek-compliance-aade',
            'monitoring':   'cli-deadline-monitor',
            'email':        'greek-email-processor',
            'individual':   'greek-individual-taxes',
            # Phase 2 — Advanced
            'aade':         'aade-api-monitor',
            'banking':      'greek-banking-integration',
            'ocr':          'greek-document-ocr',
            'efka':         'efka-api-integration',
            # Phase 3A — Infrastructure
            'dashboard':    'dashboard-greek-accounting',
            'clients':      'client-data-management',
            'auth':         'user-authentication-system',
            'chat':         'conversational-ai-assistant',
            # Phase 3B €" Professional Outputs
            'statements':   'greek-financial-statements',
            'comms':        'client-communication-engine',
            'integrity':    'system-integrity-and-backup',
            'analytics':    'analytics-and-advisory-intelligence',
            # Phase 4 €" Learning Loop
            'memory':       'memory-feedback',
            # Operational
            'health':       'system-health-check',
        }

    def monthly_process(self, afm=None, month=None, user=None):
        """Orchestrate complete monthly processing for one client"""

        # Step 1: Permission gate — must pass before any work begins
        self.call_skill('auth', f'check-access --username {user} --client {afm} --action compliance_management')

        # Step 2: Read client obligations
        client = self.call_skill('clients', f'view --afm {afm} --compliance-summary')

        # Step 3: Check deadlines before touching anything
        deadlines = self.call_skill('monitoring', f'check aade --client {afm}')
        if deadlines['overdue_count'] > 0:
            self.alert_user(f"WARNING: {deadlines['overdue_count']} overdue deadlines — review before proceeding")

        # Step 4: Process any new incoming documents
        self.call_skill('email', 'scan-folder /data/incoming/ --classify-new')
        self.call_skill('ocr', 'process-greek --input-dir /data/ocr/incoming/')
        self.call_skill('accounting', 'batch-process --input-dir /data/ocr/output/accounting-ready/ --greek-format')
        self.call_skill('clients', f'doc-register --afm {afm}')

        # Step 5: Banking reconciliation
        self.call_skill('banking', f'reconcile --afm {afm} --period {month}')

        # Step 6: Prepare compliance filings — no submission yet
        vat = self.call_skill('compliance', f'vat-return --client {afm} --period {month} --prepare')
        efka = self.call_skill('efka', f'contribution-calc --afm {afm} --period {month}')

        # Step 7: HUMAN CONFIRMATION GATE — display details and require explicit YES
        self.require_confirmation(
            action='government_submission',
            details={'vat': vat, 'efka': efka, 'client': afm, 'period': month}
        )

        # Step 8: Submit (only reached after confirmed)
        self.call_skill('compliance', f'vat-return --client {afm} --period {month} --submit')
        self.call_skill('efka', f'submit-declaration --afm {afm} --period {month}')

        # Step 9: Log filings to client record
        self.call_skill('clients', f'log-filing --afm {afm} --type VAT-monthly --period {month} --status submitted')
        self.call_skill('clients', f'log-filing --afm {afm} --type EFKA-monthly --period {month} --status submitted')

        # Step 10: Generate financial statements (if completeness gate passes)
        self.call_skill('statements', f'generate --afm {afm} --period {month}')

        # Step 11: Draft client communications for human review
        self.call_skill('comms', f'draft --afm {afm} --type submission-confirmation --period {month}')
        self.call_skill('comms', f'draft --afm {afm} --type monthly-summary --period {month} --include-statements')

        # Step 12: Trigger event-driven backup snapshot
        self.call_skill('integrity', f'snapshot --trigger gov-submission --afm {afm} --period {month}')

        # Step 13: Log episode to memory
        self.call_skill('memory', f'log-episode --type monthly_process_complete --afm {afm} --period {month}')

        # Step 14: Refresh dashboard
        self.call_skill('dashboard', f'refresh --client {afm}')

    def require_confirmation(self, action, details):
        """Mandatory pause before any government submission"""
        self.display_action_summary(action, details)
        response = self.prompt_user("Confirm submission? Type YES to proceed or NO to cancel: ")
        if response.upper() != 'YES':
            raise UserCancelledException(f"Submission cancelled by user for {details['client']}")
        self.log_confirmation(action, details)

    def call_skill(self, skill_type, command):
        """Execute command on specific skill with error handling"""
        skill_name = self.skills[skill_type]
        try:
            result = openclaw_execute(f"openclaw skills use {skill_name} {command}")
            return result
        except Exception as e:
            self.handle_skill_error(skill_name, command, e)
            return self.get_fallback_result(skill_type)
```

### Error Handling & Recovery
```yaml
Error_Recovery_Strategies:
  skill_unavailable:
    action: "Use cached results and alert user"
    fallback: "Switch to manual mode with guidance"
    
  data_processing_error:
    action: "Flag document for manual review"
    notification: "Send Greek language error explanation to user"
    
  government_api_failure:
    action: "Use cached deadline data"
    alert: "Monitor for service restoration"
    
  calculation_error:
    action: "Preserve original data, alert accountant"
    manual_review: "Provide detailed error context in Greek"
```

## Business Command Examples

### Daily Operations
```bash
# Morning startup — pulls from dashboard, deadline monitor, AADE monitor, email processor
openclaw greek morning-check
# Orchestrates:
# 1. openclaw auth check-access (verify session)
# 2. openclaw deadline check all --urgent --days 7
# 3. openclaw email scan-folder /data/incoming/ --classify-new
# 4. openclaw aade status-check --taxis --mydata --efka
# 5. openclaw dashboard morning-briefing --date today --include-alerts --include-deadlines
# Output: Prioritised task list with government system status

# Quick single-client status
openclaw greek client-status --afm EL123456789
# Orchestrates: openclaw clients view, openclaw dashboard client-overview, openclaw deadline check
# Output: English-language snapshot — docs, deadlines, compliance score, action items

# End of day summary
openclaw greek eod-summary
# Orchestrates: openclaw dashboard eod-summary, openclaw deadline check --due-tomorrow
# Output: Completed tasks, unresolved items, tomorrow preview
```

### Weekly Operations
```bash
# Weekly compliance review across all clients
openclaw greek weekly-review
# Orchestrates:
# 1. openclaw clients compliance-gaps --all-clients --period current-week
# 2. openclaw dashboard portfolio-summary --all-clients --compliance-score
# 3. openclaw aade detect-changes --since last-week
# 4. openclaw deadline check all --due-this-week

# Portfolio health check — identifies risks before they become urgent
openclaw greek portfolio-check --flag-risks
# Orchestrates: openclaw clients compliance-gaps, openclaw dashboard client-health --rank
# Output: Risk-ranked client list with specific action items per client
```

### Monthly Operations
```bash
# Month-end processing for all active clients
openclaw greek month-end-process --month 2026-02
# Runs openclaw greek monthly-process for each active client in sequence
# Skips clients with missing data and flags them for manual review
# Output: /data/reports/monthly/2026-02_batch_summary.pdf

# Individual tax preparation batch
openclaw greek prepare-individual-taxes --year 2025 --batch --optimize-deductions
# Orchestrates:
# 1. openclaw clients list --all --active-only
# 2. openclaw individual collect-employment-docs --year 2025 (per client)
# 3. openclaw individual optimize-deductions --include-all-eligible (per client)
# 4. openclaw individual generate-e1-form --year 2025 --validate-data (per client)
# Output: Batch status — X ready for review, Y missing documents, Z need accountant attention
```

### Phase 3A — Dashboard & Administration Commands
```bash
# First-time system setup
openclaw greek setup --firm-name "YOUR FIRM" --timezone "Europe/Athens"
# Orchestrates:
# 1. openclaw greek init-filesystem --create-all-dirs
# 2. openclaw dashboard init --firm-name "YOUR FIRM" --language en --data-language el
# 3. openclaw dashboard set-preferences --timezone "Europe/Athens" --currency EUR --date-format DD/MM/YYYY
# 4. openclaw greek health-check --verify-all-skills

# Add a new staff member
openclaw greek staff-add --username "maria.g" --role assistant --name "Maria Georgiou" --email "maria@firm.gr"
# Orchestrates:
# 1. openclaw auth user-create --username "maria.g" --role assistant --full-name "Maria Georgiou"
# 2. openclaw auth 2fa-enable --username "maria.g" --method totp
# 3. openclaw dashboard add-user --name "Maria Georgiou" --role assistant

# Assign clients to a staff member
openclaw greek assign-clients --username "maria.g" --clients EL123456789,EL987654321
# Orchestrates:
# 1. openclaw auth assign-clients --username "maria.g" --clients EL123456789,EL987654321
# 2. openclaw dashboard set-alerts --user "maria.g" --urgency-threshold medium

# Full firm compliance gap report
openclaw greek compliance-report --period 2026-02 --all-clients --export pdf
# Orchestrates:
# 1. openclaw clients compliance-gaps --all-clients --period 2026-02
# 2. openclaw dashboard compliance-check --all-clients --flag-issues
# 3. openclaw deadline check all --overdue
# Output: /data/reports/compliance/2026-02_firm_compliance_report.pdf

# AADE government sync — check for regulatory changes
openclaw greek aade-sync --check-updates --update-deadlines
# Orchestrates:
# 1. openclaw aade download-batch --sources all
# 2. openclaw aade detect-changes --compare-with-cache
# 3. openclaw deadline check all --flag-changes
# 4. openclaw dashboard refresh --state deadline-tracker
# If changes detected: alert all affected users

# System health check — all 18 skills
openclaw greek health-check --verify-all-skills --verbose
```

### 7. Phase 3B Professional Output Commands

```bash
# Generate financial statements for a client after monthly process
openclaw greek generate-statements --afm EL123456789 --period 2026-02
# Orchestrates:
# 1. openclaw statements check-ready --afm EL123456789 --period 2026-02
# 2. openclaw statements generate --afm EL123456789 --period 2026-02 --type all
# 3. openclaw clients log-filing --afm EL123456789 --type statements --period 2026-02
# 4. openclaw dashboard refresh --client EL123456789

# Draft and queue outgoing communications after submission
openclaw greek post-submission-comms --afm EL123456789 --period 2026-02
# Orchestrates:
# 1. openclaw comms draft --type submission-confirmation --afm EL123456789 --filing-type VAT --period 2026-02
# 2. openclaw comms draft --type monthly-summary --afm EL123456789 --period 2026-02 --include-statements
# ⚠️  HUMAN APPROVAL REQUIRED before any communication is sent
# 3. [After approval] openclaw comms send --draft-id {id} --approved-by {username}
# 4. openclaw clients log-correspondence --afm EL123456789 --period 2026-02

# Pull morning advisory via conversational assistant
openclaw greek morning-briefing --date today
# Orchestrates:
# 1. openclaw auth check-access --action view_portfolio
# 2. openclaw analytics morning-advisory --date today
# 3. openclaw deadline check all --due-within 7-days
# 4. openclaw dashboard morning-briefing --include-alerts

# Run integrity check and backup status
openclaw greek system-check --full
# Orchestrates:
# 1. openclaw integrity check --all
# 2. openclaw backup status --show-verified --show-unverified --show-failed
# 3. openclaw retention due
# 4. openclaw dashboard refresh --state system-health
```

## Integration & Data Flow

### File System Organization
```yaml
Meta_Skill_File_Structure:
  client_data:                           # Managed by client-data-management skill
    - /data/clients/{AFM}/               # AFM format: EL + 9 digits e.g. EL123456789
    - /data/clients/{AFM}/profile.json
    - /data/clients/{AFM}/documents/registry.json
    - /data/clients/{AFM}/compliance/filings.json
    - /data/clients/_index.json          # Global client index
    
  government_intake:                     # Raw government documents land here
    - /data/incoming/government/         # AADE/EFKA notifications and letters
    
  compliance_outputs:                    # Filing artefacts produced by compliance skill
    - /data/compliance/vat/
    - /data/compliance/mydata/
    - /data/compliance/efka/
    
  processing_workflows:                  # Ephemeral — cleared after pipeline completes
    - /data/processing/compliance/vat/
    - /data/processing/compliance/efka/
    - /data/processing/compliance/mydata/
    
  reports_output:
    - /data/reports/client/
    - /data/reports/compliance/
    - /data/reports/monthly/
```

### Skill Coordination
```yaml
Skill_Interaction_Patterns:

  document_intake_flow:
    sequence: "email-processor → ocr → accounting-workflows → client-data-management"
    data_path: "/data/incoming/ → /data/ocr/output/accounting-ready/ → /data/clients/{AFM}/"
    coordination: "Meta-skill manages handoff between each stage"

  compliance_filing_flow:
    sequence: "auth → client-data-management → compliance-aade → [CONFIRM] → compliance-aade → client-data-management → dashboard"
    data_path: "/data/processing/compliance/ → /data/compliance/ → /data/clients/{AFM}/compliance/filings.json"
    coordination: "Human confirmation gate mandatory before any government submission"

  banking_reconciliation_flow:
    sequence: "banking-integration → accounting-workflows → client-data-management → dashboard"
    data_path: "/data/banking/imports/ → /data/banking/reconciliation/ → /data/clients/{AFM}/"
    coordination: "Meta-skill sequences import before reconciliation"

  deadline_monitoring_flow:
    sequence: "aade-api-monitor → cli-deadline-monitor → dashboard → client-data-management"
    data_path: "/data/incoming/government/ → /data/dashboard/state/"
    coordination: "Changes to deadlines propagate to all affected client obligation schedules"

  client_onboarding_flow:
    sequence: "auth → client-data-management → cli-deadline-monitor → dashboard"
    data_path: "/data/clients/{AFM}/ created fresh"
    coordination: "Auth confirms permission; client-data-management is sole writer to /data/clients/"

  morning_briefing_flow:
    sequence: "auth → deadline-monitor → email-processor → aade-api-monitor → dashboard"
    data_path: "Read-only — no writes during morning check"
    coordination: "All read operations; dashboard aggregates and displays"

  financial_statements_flow:
    sequence: "statements check-ready → statements generate → client-data-management → dashboard"
    data_path: "/data/banking/reconciliation/ + /data/compliance/ + /data/efka/ → /data/clients/{AFM}/financial-statements/ → /data/reports/client/"
    coordination: "Completeness gate must pass before generation. Statement index updated after generation."

  post_submission_comms_flow:
    sequence: "compliance-aade [submit] → statements generate → comms draft → [CONFIRM] → comms send → client-data-management"
    data_path: "/data/compliance/submissions/ → /data/clients/{AFM}/financial-statements/ → /data/processing/comms/ → /data/clients/{AFM}/correspondence/"
    coordination: "Communications drafted automatically after submission. Human must approve before send."

  analytics_advisory_flow:
    sequence: "analytics [nightly] → dashboard → conversational-ai-assistant [on demand]"
    data_path: "/data/clients/*/financial-statements/ + /data/banking/ + /data/efka/ → /data/reports/analytics/ → dashboard feed"
    coordination: "Runs overnight. Results pre-computed and ready for morning. Chat queries hit pre-computed outputs."

  integrity_backup_flow:
    sequence: "system-integrity-and-backup [scheduled] → dashboard [alert if issues]"
    data_path: "Reads all /data/ → writes /data/backups/ + /data/system/integrity/"
    coordination: "Runs on schedule (backup Sunday 02:00, integrity check Sunday 04:00, daily quick check 05:00). Alerts dashboard on any failure."
```

## Professional Output Features

### Greek Language Reports
```yaml
Report_Templates:
  client_monthly_summary:
    language: "Professional Greek"
    sections: ["Έσοδα και έξοδα", "ΦΠΑ υποπ¡ρεϽσειπš", "Προθεσμίεπš", "Ενέργειεπš"]
    
  compliance_status:
    language: "Greek regulatory terminology"  
    sections: ["AADE καπžάσπžαση", "ΕΦΡΑ υποπ¡ρεϽσειπš", "Δημοπžικέπš ενέργειεςπš"]
    
  individual_tax_summary:
    language: "Greek tax law terminology"
    sections: ["Εισςδημα", "ΕκππžϽσειπš", "Φςροπš", "Πληρπ°μή"]
```

### Professional Communication
```yaml
Client_Communications:
  document_requests:
    tone: "Professional and courteous Greek"
    format: "Formal business letter structure"
    
  deadline_reminders:  
    urgency_levels: ["Informative", "Reminder", "Urgent", "Critical"]
    greek_terminology: "Use proper tax and business terms"
    
  compliance_updates:
    regulatory_language: "Accurate Greek regulatory terminology"
    client_impact: "Clear explanation of impact on client business"
```

## Meta-Skill Benefits

### For Accounting Firms
- **Simplified Operations**: One command instead of 5-10 skill commands
- **Reduced Errors**: Automated coordination prevents missed steps
- **Professional Output**: Consistently formatted Greek business communications
- **Scalability**: Handle more clients without proportional complexity increase

### For OpenClaw Deployment
- **Easy Installation**: Single meta-skill installs entire system
- **Unified Monitoring**: Single dashboard for all Greek accounting operations  
- **Consistent Interface**: Business users don't need to learn technical commands
- **Maintenance**: Updates and fixes managed centrally

## Success Metrics

A successful meta-skill deployment should achieve:
- ✅ 90%+ reduction in command complexity for end users
- ✅ Zero government submissions without explicit human confirmation
- ✅ Automated coordination of all 18 specialised skills
- ✅ Professional Greek output meeting accounting firm standards
- ✅ Role-based access enforced at every write operation
- ✅ Error recovery without user intervention in 80%+ of cases
- ✅ Complete audit trail across all coordinated skill operations
- ✅ Scalable multi-client management for growing accounting firms
- ✅ English-language dashboard interface fully integrated with Greek data pipeline

Remember: This meta-skill is the single face of the entire OpenClaw Greek Accounting system. Every new skill added to the system must be registered here. Every business workflow starts here.
