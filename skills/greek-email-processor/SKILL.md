---
name: greek-email-processor
description: Email processing for Greek accounting. Connects via IMAP to scan for financial documents, AADE notices, and invoices. Routes to local pipelines.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "email", "document-classification", "imap"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "curl"], "env": ["OPENCLAW_DATA_DIR", "IMAP_HOST", "IMAP_USER", "IMAP_PASSWORD"]}, "optional_env": {"SMTP_HOST": "Email server for auto-responses (requires human approval before sending)", "SMTP_USER": "Email account for sending responses", "SMTP_PASSWORD": "Email account password (use app-specific passwords)", "GOOGLE_CLIENT_ID": "Gmail API OAuth client ID (alternative to IMAP for Gmail users)", "GOOGLE_CLIENT_SECRET": "Gmail API OAuth client secret", "MS_CLIENT_ID": "Microsoft Graph API client ID (alternative to IMAP for Outlook users)", "MS_CLIENT_SECRET": "Microsoft Graph API client secret", "GOOGLE_CALENDAR_ID": "Google Calendar ID for deadline event creation", "SLACK_WEBHOOK_URL": "Webhook URL for processing status notifications"}, "notes": "IMAP credentials are the only required credentials — works with any email provider. Gmail API and Microsoft Graph API are optional alternatives that provide richer features. SMTP, Calendar, and Slack integrations are optional notification channels. All auto-responses require human approval."}}
---

# Greek Email Processor

This skill transforms OpenClaw into an intelligent Greek business email processor that automatically detects, categorizes, and processes financial documents and official communications from Greek government agencies, banks, and business partners.

## Setup

```bash
# 1. Set data directory
export OPENCLAW_DATA_DIR="/data"

# 2. Configure email access (use a scoped service account with read-only access)
export IMAP_HOST="imap.your-provider.com" # e.g. imap.gmail.com, imap.outlook.com
export IMAP_USER="accounting@yourfirm.gr"
export IMAP_PASSWORD="app-specific-password"  # Use app passwords, not main password

# 3. Configure outbound email (optional — only needed for auto-responses)
export SMTP_HOST="smtp.your-provider.com" # e.g. smtp.gmail.com, smtp.outlook.com
export SMTP_USER="accounting@yourfirm.gr"
export SMTP_PASSWORD="app-specific-password"

# 4. Ensure dependencies are installed
which jq curl || sudo apt install jq curl

# 5. Create incoming directories
mkdir -p $OPENCLAW_DATA_DIR/incoming/{invoices,receipts,statements,government}
```

**Security notes:**
- Use app-specific passwords or app-specific passwords — never your main email password
- Grant the service account the minimum required permissions (read-only for IMAP)
- SMTP credentials are optional — only needed if you enable auto-response features
- All auto-responses require human approval before sending

## Core Philosophy

- **Greek Language First**: Native support for Greek language emails and documents
- **Intelligent Classification**: Automatic detection of document types and priority levels
- **Compliance Focused**: Special handling for AADE, EFKA, and government communications
- **Business Context Aware**: Understanding of Greek business communication patterns
- **Privacy Conscious**: Secure handling of sensitive financial information in emails

## Key Capabilities

### 1. Greek Document Recognition & Classification
- **Invoice Detection**: Identify Greek invoices (ΤΙΜθ΀ºθΓΙθ, ΑΠθΔΕΙξΗ) in email attachments
- **Government Notifications**: Recognize AADE, EFKA, and municipal communications
- **Bank Statements**: Process statements from all major Greek banks
- **Tax Documents**: Detect tax-related emails and forms
- **Client Communications**: Categorize business correspondence and payment requests
- **Receipt Processing**: Identify expense receipts and business documentation

### 2. Email Provider Integration
- **Gmail / Google Workspace**: Via IMAP (use app-specific password) or optional Gmail API (set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
- **Outlook / Exchange**: Via IMAP or optional Microsoft Graph API (set MS_CLIENT_ID, MS_CLIENT_SECRET)
- **Any IMAP Provider**: Standard IMAP connection to any email provider
- **IMAP/SMTP Providers**: Any IMAP-compatible business email
- **Yahoo Business**: Yahoo business email support
- **Custom IMAP/POP3**: Support for Greek business email providers
- **Multi-Account Support**: Handle multiple email accounts simultaneously
- **Real-time Monitoring**: Continuous inbox monitoring with configurable intervals

### 3. Greek Language Processing
- **Greek Text Recognition**: Native Greek language email content analysis
- **Mixed Language Support**: Handle Greek-English business communications
- **Greek Date Formats**: Recognize Greek date patterns (dd/MM/yyyy)
- **Currency Detection**: Greek Euro formatting (‚¬1.234,56)
- **Address Parsing**: Greek address format recognition
- **VAT Number Detection**: Identify Greek VAT numbers (EL123456789) in emails

### 4. Automated Processing Workflows
- **Document Extraction**: Automatic attachment download and processing
- **Smart Forwarding**: Route emails to appropriate processing pipelines
- **Client Notification**: Automated responses in Greek for document receipt
- **Priority Escalation**: Flag urgent emails (overdue payments, government notices)
- **Calendar Integration** (optional): Create calendar events for payment due dates if GOOGLE_CALENDAR_ID is configured
- **Task Creation**: Generate accounting tasks from email content

## Implementation Guidelines

### Email Monitoring Architecture

#### IMAP Email Integration
```yaml
IMAP_Configuration:
  imap_permissions:
    protocol: "IMAP for reading, SMTP for sending"
    security: "TLS/SSL required"
  
  monitoring_labels:
    - "INBOX"
    - "UNREAD"
    - "IMPORTANT"
    - custom_labels: ["Accounting", "Tax", "Invoices"]
  
  search_queries:
    invoices: "subject:(πžιμολςγιο OR invoice OR αποδειξη OR receipt)"
    tax_documents: "from:aade.gr OR from:efka.gov.gr OR subject:π πα"
    bank_statements: "from:alphabank.gr OR from:nbg.gr OR from:eurobank.gr OR from:piraeusbank.gr"
    client_payments: "subject:(πληρπ°μή OR payment OR οπ ειλή OR due)"
```

#### IMAP/SMTP Providers Integration
```yaml
Alternative_Provider_Notes:
  microsoft_graph_scopes:
    - "https://graph.microsoft.com/Mail.Read"
    - "https://graph.microsoft.com/Mail.Send"
    - "https://graph.microsoft.com/Mail.ReadWrite"
  
  folder_monitoring:
    - "Inbox"
    - "Accounting"
    - "Tax Documents" 
    - "Bank Statements"
  
  advanced_queries:
    greek_invoices: "subject:πžιμολςγιο OR attachmentNames:invoice"
    government_mail: "from:gov.gr OR from:aade.gr"
    banking: "from:bank OR from:πžράπεζα"
```

### Document Classification Engine

#### Greek Document Types
```yaml
Document_Classification:
  invoices:
    greek_keywords: ["πžιμολςγιο", "αποδειξη", "παρασπžαπžικς", "invoice"]
    file_patterns: ["*.pdf", "*.xml", "*.doc*"]
    confidence_thresholds:
      high: 0.95  # Clear invoice format
      medium: 0.80  # Probable invoice
      low: 0.60   # Possible invoice
    
  tax_documents:
    aade_keywords: ["π πα", "π ςροπš", "δήλπ°ση", "εκκαθαρισπžικς"]
    sender_patterns: ["*@aade.gr", "*@taxisnet.gr"]
    subject_patterns: ["*ΦΠΑ*", "*TAX*", "*ENFIA*"]
    
  bank_statements:
    greek_banks: ["Alpha Bank", "Εθνική Τράπεζα", "Eurobank", "Τράπεζα ΠειραιϽπš"]
    keywords: ["κίνηση λογαριασμού", "statement", "ανπžίγραπ ο", "υπςλοιπο"]
    formats: ["pdf", "csv", "xls", "xlsx"]
    
  receipts:
    keywords: ["αποδειξη", "παρασπžαπžικς", "πžιμολςγιο λιανικήπš", "receipt"]
    amount_patterns: ["‚¬\\d+[.,]\\d+", "\\d+[.,]\\d+\\s*‚¬", "\\d+[.,]\\d+\\s*EUR"]
    vat_patterns: ["ΦΠΑ \\d+%", "VAT \\d+%"]
    
  client_communications:
    payment_keywords: ["πληρπ°μή", "οπ ειλή", "λογαριασμςπš", "πžιμολςγηση"]
    request_keywords: ["παρακαλϽ", "αίπžημα", "π¡ρειάζομαι", "σπžείλπžε"]
    urgent_keywords: ["επείγον", "urgent", "άμεσα", "προθεσμία"]
```

#### Intelligent Content Analysis
```yaml
Content_Analysis_Rules:
  priority_detection:
    high_priority:
      - government_communications: "Emails from AADE, EFKA, municipalities"
      - payment_due: "Overdue payment notices"
      - audit_requests: "Tax audit or compliance requests"
      - system_outages: "TAXIS, myDATA system announcements"
      
    medium_priority:
      - new_invoices: "Incoming invoices from suppliers"
      - bank_notifications: "Bank statement availability"
      - client_requests: "Client document requests"
      - deadline_reminders: "Tax or compliance deadline notices"
      
    low_priority:
      - newsletters: "Professional service newsletters"
      - marketing: "Software or service promotions"
      - routine_confirmations: "Standard transaction confirmations"
  
  automated_actions:
    high_priority_actions:
      - immediate_notification: "notification to assigned accountant"
      - create_calendar_event: "Add deadline to calendar"
      - create_task: "Generate action item in task management"
      - escalate_to_human: "Flag for immediate attention"
      
    medium_priority_actions:
      - extract_attachments: "Download and process documents"
      - forward_to_processing: "Send to document processing pipeline"
      - send_confirmation: "Automated receipt confirmation in Greek"
      - update_client_records: "Log communication in client file"
      
    low_priority_actions:
      - archive_appropriately: "File in correct folder"
      - update_newsletter_tracking: "Mark as read, file for reference"
```

### Greek Language Processing Engine

#### Language Detection & Parsing
```yaml
Greek_Language_Support:
  text_processing:
    encoding: "UTF-8"
    character_sets: ["ISO-8859-7", "Windows-1253", "UTF-8"]
    
  date_recognition:
    greek_months: ["Ιανουάριοπš", "Φεβρουάριοπš", "Μάρπžιοπš", "Απρίλιοπš", "Μάιοπš", "Ιούνιοπš", "Ιούλιοπš", "Αύγουσπžοπš", "Σεππžέμβριοπš", "θκπžϽβριοπš", "Νοέμβριοπš", "Δεκέμβριοπš"]
    date_patterns: ["dd/MM/yyyy", "dd-MM-yyyy", "dd.MM.yyyy", "dd Μμμμ yyyy"]
    
  currency_recognition:
    euro_patterns: ["‚¬\\d+[.,]\\d+", "\\d+[.,]\\d+\\s*‚¬", "\\d+[.,]\\d+\\s*EUR", "\\d+[.,]\\d+\\s*ευρϽ"]
    greek_numerals: Support for Greek number formatting (1.234,56)
    
  vat_number_detection:
    greek_pattern: "EL\\d{9}"
    validation: "Check digit validation for Greek VAT numbers"
    
  address_parsing:
    greek_patterns: "Street number, area, postal code, city format"
    common_abbreviations: ["΀ºεπ°π .", "θδςπš", "Πλαπžεία", "Τ.Ρ."]
    
  business_terminology:
    accounting_terms: ["λογισπžήριο", "π οροπžεπ¡νικςπš", "ΦΠΑ", "ΕΝΦΙΑ", "ΕΦΡΑ"]
    legal_entities: ["Α.Ε.", "Ε.Π.Ε.", "θ.Ε.", "Ε.Ε.", "Ι.Ρ.Ε."]
```

#### Greek Email Templates
```yaml
Automated_Response_Templates:
  invoice_received:
    subject: "Επιβεβαίπ°ση παραλαβήπš πžιμολογίου - {invoice_number}"
    body: |
      Αγαπηπžέ/ή {sender_name},
      
      ΕπιβεβαιϽνουμε πžην παραλαβή πžου πžιμολογίου {invoice_number} 
      ημερομηνίαπš {invoice_date} συνολικήπš αξίαπš {total_amount}.
      
      Το πžιμολςγιο έπ¡ει προπ°θηθεί σπžο λογισπžήρις μαπš για επεξεργασία.
      Η πληρπ°μή θα πραγμαπžοποιηθεί ενπžςπš {payment_terms}.
      
      Με εκπžίμηση,
      {company_name}
      
  document_request:
    subject: "Αίπžημα για πρςσθεπžα έγγραπ α - {reference_number}"
    body: |
      Αγαπηπžέ/ή {client_name},
      
      Για πžην ολοκλήρπ°ση πžηπš λογισπžικήπš επεξεργασίαπš, π¡ρειαζςμασπžε 
      πžα ακςλουθα έγγραπ α:
      
      {required_documents}
      
      Παρακαλούμε σπžείλπžε πžα έγγραπ α πžο συνπžομςπžερο δυναπžς.
      
      Ευπ¡αρισπžούμε,
      {accountant_name}
      
  payment_reminder:
    subject: "Υπενθύμιση πληρπ°μήπš - {invoice_number}"
    body: |
      Αγαπηπžέ/ή {client_name},
      
      Σαπš υπενθυμίζουμε ςπžι πžο πžιμολςγιο {invoice_number} 
      αξίαπš {amount} είπ¡ε λήξει πžην {due_date}.
      
      Παρακαλούμε προβείπžε σπžην πληρπ°μή πžο συνπžομςπžερο δυναπžς.
      
      Για οποιαδήποπžε διευκρίνιση, επικοινπ°νήσπžε μαζί μαπš.
      
      Με εκπžίμηση,
      {company_name}
```

## Workflow Templates

### Daily Email Processing Routine

#### Morning Email Scan (8:00 AM Greece Time)
```bash
#!/bin/bash
# Morning email processing workflow

# Check all configured email accounts
openclaw email scan all-accounts --since "24 hours ago"

# Process government emails first (highest priority)
openclaw email process --filter "government" --priority high

# Process banking notifications
openclaw email process --filter "banking" --auto-download-statements

# Process client invoices and payments
openclaw email process --filter "invoices" --auto-extract-data

# Process client communications
openclaw email process --filter "client-communications" --auto-respond

# Generate morning email summary
openclaw email summary daily --include-urgent --include-actions-needed
```

#### Continuous Monitoring (Every 15 minutes)
```bash
#!/bin/bash
# Real-time email monitoring

# Quick scan for urgent emails
openclaw email scan --filter "urgent" --real-time

# Process AADE/EFKA notifications immediately
openclaw email process --filter "government" --immediate-alert

# Handle client payment confirmations
openclaw email process --filter "payments" --update-accounting-system

# Auto-respond to routine requests
openclaw email auto-respond --filter "routine" --use-greek-templates
```

#### End of Day Processing (6:00 PM Greece Time)
```bash
#!/bin/bash
# End of day email processing

# Process any remaining unread emails
openclaw email process --filter "unread" --batch-process

# Generate daily email report
openclaw email report daily --include-statistics --include-pending

# Archive processed emails appropriately
openclaw email archive --processed-today --by-category

# Prepare tomorrow's email agenda
openclaw email agenda tomorrow --include-expected --include-deadlines
```

### Integration Workflows

#### AADE Email Integration
```yaml
AADE_Email_Processing:
  sender_domains:
    - "@aade.gr"
    - "@taxisnet.gr"
    - "@mydata.aade.gr"
    
  automatic_actions:
    tax_deadline_changes:
      - extract_new_deadline: "Parse email content for deadline changes"
      - update_calendar: "Update compliance deadline tracker immediately"
      - alert_clients: "Notify affected clients of deadline changes"
      - log_compliance: "Record change in compliance tracking system"
      
    system_maintenance_notices:
      - extract_maintenance_window: "Parse maintenance dates and times"
      - alert_users: "Notify users of planned system outages"
      - reschedule_activities: "Move planned TAXIS submissions if needed"
      
    audit_notifications:
      - high_priority_alert: "Immediate notification to assigned accountant"
      - create_urgent_task: "Generate audit response task"
      - gather_documents: "Prepare standard audit documentation"
      - legal_consultation: "Flag for legal review if needed"
```

#### Bank Email Integration
```yaml
Greek_Bank_Email_Processing:
  supported_banks:
    alpha_bank:
      domains: ["@alphabank.gr", "@alpha.gr"]
      statement_patterns: ["statement", "κίνηση λογαριασμού"]
      
    national_bank:
      domains: ["@nbg.gr", "@ethnikibank.gr"]
      statement_patterns: ["ανπžίγραπ ο κίνησηπš", "account statement"]
      
    eurobank:
      domains: ["@eurobank.gr"]
      statement_patterns: ["κίνηση λογαριασμού", "λογαριασμςπš κίνησηπš"]
      
    piraeus_bank:
      domains: ["@piraeusbank.gr", "@winbank.gr"]
      statement_patterns: ["statement", "κίνηση", "υπςλοιπο"]
      
  processing_workflow:
    statement_detection:
      - verify_sender: "Confirm email is from legitimate bank domain"
      - extract_attachments: "Download PDF/CSV statement files"
      - parse_account_info: "Extract account numbers and dates"
      - integrate_accounting: "Forward to bank reconciliation system"
      
    payment_confirmations:
      - match_transactions: "Match with pending payment records"
      - update_client_accounts: "Mark invoices as paid"
      - generate_receipts: "Create payment confirmation documents"
      
    fraud_detection:
      - verify_bank_signatures: "Check for legitimate bank formatting"
      - flag_suspicious: "Alert for unusual sender patterns"
      - security_validation: "Verify against known bank communication patterns"
```

## Advanced Features

### Client Communication Automation

#### Intelligent Auto-Response System
```yaml
Auto_Response_Logic:
  invoice_submissions:
    conditions:
      - "Email contains PDF attachment"
      - "Subject contains 'πžιμολςγιο' or 'invoice'"
      - "Sender is known client"
    actions:
      - send_confirmation: "Automated receipt confirmation in Greek"
      - extract_invoice_data: "Process invoice for accounting system"
      - create_payment_schedule: "Add to payment processing queue"
      
  document_requests:
    conditions:
      - "Email contains request for documents"
      - "Keywords: 'σπžείλπžε', 'π¡ρειάζομαι', 'παρακαλϽ'"
    actions:
      - acknowledge_request: "Confirm receipt of request"
      - generate_document_list: "List available documents"
      - schedule_follow_up: "Set reminder if documents not sent"
      
  payment_inquiries:
    conditions:
      - "Subject contains 'πληρπ°μή' or 'payment'"
      - "Client asking about payment status"
    actions:
      - check_payment_status: "Query accounting system"
      - send_status_update: "Provide current payment status"
      - attach_receipt: "Include payment confirmation if paid"
```

### Multi-Account Management

#### Account Configuration
```yaml
Multi_Account_Setup:
  primary_business_account:
    email: "accounting@company.gr"
    protocol: "IMAP"
    processing_priority: "high"
    auto_responses: "enabled"
    
  client_communication_account:
    email: "info@company.gr"  
    protocol: "IMAP"
    processing_priority: "medium"
    auto_responses: "enabled"
    
  government_notifications_account:
    email: "compliance@company.gr"
    protocol: "IMAP"
    processing_priority: "critical"
    auto_responses: "disabled"
    
  bank_statements_account:
    email: "banking@company.gr"
    provider: "Yahoo"
    processing_priority: "high"
    auto_responses: "disabled"
    
Account_Synchronization:
  cross_account_deduplication: "Prevent duplicate processing"
  unified_reporting: "Single report covering all accounts"
  centralized_task_management: "Tasks from all accounts in one queue"
  global_contact_management: "Shared client database across accounts"
```

## Security & Privacy Features

### Data Protection
- **Email Encryption**: Support for encrypted email communication
- **Secure Attachment Handling**: Virus scanning and secure storage
- **Access Controls**: Role-based access to email processing functions
- **Audit Logging**: Complete trail of email processing activities
- **GDPR Compliance**: European privacy law compliance for email data

### Greek Business Privacy
- **Client Confidentiality**: Secure handling of client communications
- **Banking Security**: Special protection for bank statement processing
- **Government Communication Security**: Secure processing of official communications
- **Document Retention**: Greek legal requirements for email retention
- **Professional Privilege**: Respect for accountant-client privilege

## Performance Optimization

### Efficient Processing
```yaml
Performance_Settings:
  email_scanning:
    interval: "5 minutes for critical accounts"
    batch_size: "50 emails per batch"
    concurrent_processing: "3 accounts simultaneously"
    
  attachment_processing:
    size_limits: "50MB per attachment"
    format_support: ["pdf", "doc", "docx", "xls", "xlsx", "csv", "xml"]
    ocr_enabled: "For scanned documents"
    
  response_times:
    urgent_emails: "<30 seconds"
    government_emails: "<1 minute" 
    routine_processing: "<5 minutes"
    
  caching:
    sender_recognition: "Cache known senders for faster processing"
    template_responses: "Pre-compiled response templates"
    document_patterns: "Cache document recognition patterns"
```

## Integration Points

### OpenClaw Skills Integration
```bash
# Integration with other Greek accounting skills
openclaw email process --forward-to greek-compliance-aade
openclaw email process --forward-to accounting-workflows
openclaw email process --forward-to cli-deadline-monitor

# Integration with document processing
openclaw email extract-attachments --process-with deepread-skill
openclaw email invoices --process-with greek-vat-calculator

# Integration with client management
openclaw email client-communications --update-client-records
openclaw email payments --update-accounting-ledger

# Update client records with email-derived data (requires client-data-management skill)
openclaw email client-communications --update-client-records
```

### Internal Skill Integration
```yaml
Companion_Skills:
  accounting-workflows: "Route extracted documents to processing pipeline"
  greek-document-ocr: "Send attachments for OCR processing"
  client-data-management: "Update client records from email content"
  greek-compliance-aade: "Forward AADE notifications for compliance tracking"
  greek-banking-integration: "Match email payment notifications with bank transactions"
```

> **Note**: This skill does NOT integrate with external software. It processes emails and routes extracted data to companion OpenClaw skills via the local filesystem.

## Usage Examples

### Example 1: Invoice Processing
```bash
$ openclaw email process --filter "invoices" --account "accounting@company.gr"

📧 EMAIL PROCESSING RESULTS:

New Invoices Processed (3):
✅ SUPPLIER A AE - Invoice #2026-0156 - ‚¬1,250.00
   ├─ Status: VAT validated (24%)
   ├─ Due Date: March 15, 2026 (26 days)  
   ├─ Action: Forwarded to accounting system
   └─ Response: Greek confirmation sent to supplier

✅ ΠΡΡθΜΗΜΕΥΤΗΣ B ΕΠΕ - Τιμολςγιο #456 - ‚¬850.00
   ├─ Status: Greek invoice format recognized
   ├─ VAT Rate: 13% (services)
   ├─ Action: Added to payment queue
   └─ Response: "Επιβεβαίπ°ση παραλαβήπš" sent

⚠ï¸ VENDOR C - Invoice unclear format - ‚¬2,100.00
   ├─ Status: Manual review required
   ├─ Issue: VAT calculation uncertain
   ├─ Action: Flagged for accountant review
   └─ Response: Acknowledgment sent, review requested

Summary: 3 invoices processed, 2 automated, 1 manual review needed
```

### Example 2: AADE Notification Processing
```bash
$ openclaw email process --filter "government" --priority critical

ðŸÂ€ºï¸ GOVERNMENT EMAIL PROCESSING:

AADE Notification Processed (1):
🚨 CRITICAL: VAT Deadline Change Detected
   ├─ From: notifications@aade.gr
   ├─ Subject: "Αλλαγή προθεσμίαπš υποβολήπš δήλπ°σηπš ΦΠΑ"
   ├─ Change: March VAT deadline moved from 25th to 20th
   ├─ Impact: 5 days earlier than expected
   ├─ Actions Taken:
   ─š   ├─ Updated compliance deadline tracker ✅
   ─š   ├─ Notified affected clients ✅
   ─š   ├─ Rescheduled VAT preparation tasks ✅
   ─š   └─ Created urgent alert for accounting team ✅

EFKA System Notice (1):
„¹ï¸ Planned Maintenance Notification
   ├─ From: support@efka.gov.gr
   ├─ Maintenance Window: Feb 19, 02:00-06:00 EET
   ├─ Impact: Social security submissions unavailable
   ├─ Action: Rescheduled morning submissions to afternoon

Summary: Critical compliance changes processed and implemented
```

### Example 3: Client Communication Automation
```bash
$ openclaw email process --filter "client-communications" --auto-respond

👥 CLIENT COMMUNICATION PROCESSING:

Payment Status Inquiries (2):
📀¹ ΠΕ΀ºΑΤΗΣ A ΑΕ - Payment Status Request
   ├─ Query: "Πςπžε θα πληρπ°θεί πžο πžιμολςγις μαπš #789?"
   ├─ Status Check: Invoice paid Feb 15, 2026
   ├─ Response: Greek status update with payment confirmation
   └─ Attachment: Payment receipt included

📀¹ CLIENT B LTD - Overdue Payment Inquiry  
   ├─ Query: "Why is payment delayed for invoice #456?"
   ├─ Status Check: Payment scheduled for Feb 20, 2026
   ├─ Response: Explanation of payment schedule + apology
   └─ Follow-up: Added to priority payment list

Document Requests (1):
📀ž ΕΤΑΙΡΕΙΑ Γ ΕΠΕ - Additional Documentation  
   ├─ Request: "Χρειαζςμασπžε ανπžίγραπ ο π ορολογικήπš ενημερςπžηπžαπš"
   ├─ Document: Tax compliance certificate generated
   ├─ Response: Certificate attached with Greek cover letter
   └─ Archive: Request logged in client file

Summary: 3 client communications processed, all with automated responses
```

## OpenClaw Integration Strategy

### Practical OpenClaw Email Processing
```bash
# File-based email processing — drop exported email files into incoming
openclaw email monitor-folder /data/incoming/ --greek-language
openclaw email process-attachments --extract-invoices --auto-classify
openclaw email generate-responses --templates-greek --auto-send false

# Email integration through file system
openclaw email scan-exports --source imap-archive --process-new
openclaw email parse-greek-documents --invoices --government --banking
```

### File-Based Email Workflow (OpenClaw Compatible)
```yaml
Email_Processing_Workflow:
  # Step 1: Email Export (External to OpenClaw)
  email_export:
    method: "User exports emails/attachments to /data/incoming/"
    formats: [".eml", ".mbox", ".pst", ".msg", ".pdf", ".xlsx"]
    subfolders:
      invoices: "/data/incoming/invoices/"
      government: "/data/incoming/government/"
      statements: "/data/incoming/statements/"
      other: "/data/incoming/other/"
    
  # Step 2: OpenClaw Processing
  openclaw_processing:
    scan: "openclaw email scan-folder /data/incoming/"
    extract: "openclaw email extract-attachments --greek-docs"
    classify: "openclaw email classify-documents --business-types"
    
  # Step 3: Response Generation
  response_generation:
    templates: "openclaw email prepare-responses --greek-templates"
    review: "openclaw email review-drafts --manual-approval"
    output: "/data/processing/email-drafts/{YYYY-MM-DD}/{response-type}.txt"
```

### OpenClaw-Friendly Email Commands
```bash
# Document processing from incoming folder (after email export)
openclaw email extract-invoices --input-dir /data/incoming/invoices/
openclaw email process-statements --input-dir /data/incoming/statements/ --bank-format greek --auto-reconcile
openclaw email handle-government --input-dir /data/incoming/government/ --aade-notifications --priority urgent

# Greek language specific processing
openclaw email greek-classify --document-types --confidence-threshold 0.8
openclaw email greek-respond --template-library /data/system/templates/greek/
openclaw email greek-forward --accounting-system --include-metadata
```

### Integration with Other Skills
```bash
# Chain with other OpenClaw skills
openclaw email process-batch | openclaw accounting validate-invoices
openclaw email extract-data | openclaw greek-compliance calculate-vat
openclaw email government-alerts | openclaw deadline update-deadlines
```

A successful Greek email processing system should achieve:
- ✅ 95%+ accuracy in Greek document classification
- ✅ <30 seconds response time for urgent government emails
- ✅ 90%+ automation rate for routine client communications
- ✅ Zero missed critical compliance notifications
- ✅ Complete audit trail for all email processing
- ✅ Integration with all major Greek email providers
- ✅ Native Greek language support for all communications

Remember: This skill serves as the communication hub for Greek accounting automation, ensuring no important financial documents or government notifications are missed while maintaining professional Greek business communication standards.