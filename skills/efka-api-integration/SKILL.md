---
name: efka-api-integration
description: Greek social security (EFKA) integration — employee records, contribution calculations, APD declarations. Human approval for submissions.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "efka", "social-security", "payroll"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "curl"], "env": ["OPENCLAW_DATA_DIR", "EFKA_USERNAME", "EFKA_PASSWORD"]}, "optional_env": {"SLACK_WEBHOOK_URL": "Notifications for EFKA submission status updates", "GOOGLE_CALENDAR_ID": "Google Calendar ID for EFKA deadline sync (optional)"}, "notes": "EFKA credentials required only for submitting declarations. Payroll calculations work offline. All submissions require human approval (four-eyes workflow). Slack notification is optional."}}
---

# EFKA API Integration

This skill provides comprehensive integration with the Greek Social Security organization (EFKA) through OpenClaw's file processing capabilities, enabling automated employee record management, contribution calculations, and compliance monitoring for Greek businesses.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
export EFKA_USERNAME="your-efka-username"
export EFKA_PASSWORD="your-efka-password"
which jq curl || sudo apt install jq curl
```

EFKA credentials are required only for submitting social security declarations. Payroll calculations and contribution processing work offline. All government submissions require human approval (four-eyes workflow).


## Core Philosophy

- **OpenClaw Artifact Ready**: Designed specifically for upload and deployment to OpenClaw instances
- **File-Based Processing**: Robust file system approach suitable for production deployment
- **Greek Employment Law Compliance**: Complete adherence to Greek social security regulations
- **Payroll Integration**: Seamless connection with existing Greek payroll systems
- **Production Scalability**: Built to handle multiple clients and high transaction volumes

## OpenClaw Commands

### Core EFKA Operations
```bash
# Primary employee and contribution management
openclaw efka employee-register --new-hire --calculate-contributions --generate-forms
openclaw efka monthly-process --payroll-period 2026-02 --all-employees --submit-ready
openclaw efka contributions-calculate --employee-id {id} --salary-changes --bonus-payments
openclaw efka compliance-check --deadlines --missing-submissions --penalty-warnings

# Employee lifecycle management
openclaw efka employee-onboard --personal-data --employment-terms --insurance-category
openclaw efka employee-update --salary-changes --position-updates --insurance-modifications
openclaw efka employee-terminate --final-calculations --clearance-certificates --archive-records

# Bulk processing and automation
openclaw efka batch-process --payroll-file /data/efka/payroll/input/ --validate-contributions
openclaw efka export-submissions --aade-format --efka-format --ready-for-upload
openclaw efka reconcile-payments --bank-statements --contribution-receipts --variance-analysis
```

### Advanced Integration Commands
```bash
# Integration with other OpenClaw skills
openclaw efka integrate-payroll --greek-compliance-aade --banking-integration --tax-calculations
openclaw efka coordinate-deadlines --cli-deadline-monitor --automatic-reminders --calendar-sync  # Syncs EFKA deadlines to calendar if configured
openclaw efka employee-expenses --individual-taxes --personal-contributions --annual-statements

# Reporting and analytics
openclaw efka generate-reports --monthly --quarterly --annual --management-dashboard
openclaw efka cost-analysis --employer-contributions --employee-deductions --budget-projections
openclaw efka audit-preparation --employee-records --contribution-history --compliance-documentation
```

### File Processing & Monitoring
```bash
# File-based EFKA data processing
openclaw efka monitor-files --watch-payroll-updates --auto-process --error-recovery
openclaw efka import-employee-data --csv --excel --validation --duplicate-detection
openclaw efka export-government --efka-xml --aade-integration --submission-ready

# Quality control and validation
openclaw efka validate-data --employee-records --contribution-calculations --regulatory-compliance
openclaw efka error-recovery --failed-submissions --data-corrections --resubmission-queue
openclaw efka backup-restore --employee-database --contribution-history --disaster-recovery
```

## OpenClaw File Processing Architecture

### EFKA File System Organization
```yaml
EFKA_File_Structure:
  employee_data:
    - /data/efka/employees/active/           # Current employee records
    - /data/efka/employees/terminated/       # Former employee records  
    - /data/efka/employees/pending/          # New hires pending registration
    - /data/efka/employees/updates/          # Employee data change requests
    
  payroll_processing:
    - /data/efka/payroll/input/              # Payroll data imports
    - /data/efka/payroll/processed/          # Calculated contributions
    - /data/efka/payroll/validated/          # Quality-checked data
    - /data/efka/payroll/ready-submit/       # Submission-ready files
    
  contributions_management:
    - /data/efka/contributions/monthly/       # Monthly contribution calculations
    - /data/efka/contributions/quarterly/     # Quarterly summaries
    - /data/efka/contributions/annual/        # Annual statements
    - /data/efka/contributions/payments/      # Payment confirmations
    
  government_integration:
    - /data/efka/submissions/efka-portal/     # EFKA portal submissions
    - /data/efka/submissions/aade-cross/      # Cross-reference with AADE
    - /data/efka/responses/confirmations/     # Government acknowledgments
    - /data/efka/responses/corrections/       # Required corrections
    
  compliance_monitoring:
    - /data/efka/deadlines/upcoming/          # Approaching deadlines
    - /data/efka/deadlines/overdue/           # Missed deadlines requiring action
    - /data/efka/audit/employee-records/      # Audit-ready documentation
    - /data/efka/audit/contribution-proof/    # Payment verification records
```

### EFKA Processing Pipeline
```yaml
Processing_Workflow:
  step_1_employee_data:
    command: "openclaw efka import-employees --source-file --validate-format --check-duplicates"
    input: "/data/efka/employees/imports/"
    output: "/data/efka/employees/validated/"
    functions: ["Data validation", "Duplicate detection", "Format standardization"]
    
  step_2_contribution_calculation:
    command: "openclaw efka calculate-contributions --salary-data --insurance-categories --rates-2026"
    input: "/data/efka/payroll/input/"
    output: "/data/efka/contributions/calculated/"
    functions: ["Contribution calculation", "Rate application", "Regulatory compliance"]
    
  step_3_cross_validation:
    command: "openclaw efka cross-validate --aade-data --banking-data --consistency-check"
    input: "/data/efka/contributions/calculated/"
    output: "/data/efka/contributions/validated/"
    functions: ["AADE cross-reference", "Banking reconciliation", "Error detection"]
    
  step_4_submission_prep:
    command: "openclaw efka prepare-submissions --efka-xml --government-format --digital-signatures"
    input: "/data/efka/contributions/validated/"
    output: "/data/efka/submissions/ready/"
    functions: ["Government format", "Digital signing", "Submission packaging"]
    
  step_5_monitoring:
    command: "openclaw efka monitor-compliance --deadlines --penalties --corrective-actions"
    input: "/data/efka/submissions/ready/"
    output: "/data/efka/compliance/monitoring/"
    functions: ["Deadline tracking", "Penalty calculation", "Action planning"]
```

## Greek Social Security Integration

### EFKA Employee Categories & Contributions (2026)
```yaml
EFKA_Employee_Categories:
  main_insurance:
    category_code: "101"
    description: "Main insurance - private sector employees"
    employer_rate: 24.56
    employee_rate: 16.00
    calculation_base: "gross_salary"
    max_monthly_base: 6177.84
    
  auxiliary_insurance:
    category_code: "201"  
    description: "Auxiliary insurance - supplementary pension"
    employer_rate: 3.00
    employee_rate: 3.00
    calculation_base: "gross_salary"
    max_monthly_base: 6177.84
    
  employment_account:
    category_code: "301"
    description: "Employment account - unemployment benefits"
    employer_rate: 1.55
    employee_rate: 0.55
    calculation_base: "gross_salary"
    max_monthly_base: 6177.84
    
  health_contributions:
    category_code: "401"
    description: "Health insurance contributions (EOPYY)"
    employer_rate: 9.76
    employee_rate: 2.55
    calculation_base: "gross_salary"
    no_maximum_base: true

Specialized_Categories:
  management_staff:
    category_code: "105"
    description: "Management and executive positions"
    additional_requirements: ["Higher contribution rates", "Extended coverage"]
    
  part_time_workers:
    category_code: "110"
    description: "Part-time employment"
    calculation_method: "proportional_to_hours"
    minimum_hours_threshold: 15
    
  seasonal_workers:
    category_code: "115"  
    description: "Seasonal employment (agriculture, tourism)"
    special_rates: "reduced_rates_applicable"
    documentation_required: ["Seasonal contract", "Industry certification"]
```

### Contribution Calculation Engine
```yaml
Contribution_Calculations:
  monthly_processing:
    gross_salary_input: "Base salary + allowances + bonuses"
    contribution_base_calculation: "Min(gross_salary, max_contribution_base)"
    
    employer_contributions:
      main_insurance: "contribution_base × 24.56%"
      auxiliary_insurance: "contribution_base × 3.00%"
      employment_account: "contribution_base × 1.55%"
      health_insurance: "gross_salary × 9.76%"
      total_employer: "sum of all employer contributions"
      
    employee_deductions:
      main_insurance: "contribution_base × 16.00%"
      auxiliary_insurance: "contribution_base × 3.00%"
      employment_account: "contribution_base × 0.55%"
      health_insurance: "gross_salary × 2.55%"
      total_employee: "sum of all employee deductions"
      
  special_calculations:
    overtime_contributions:
      overtime_hours: "hours_over_40_per_week"
      overtime_rate: "1.5 × hourly_rate"
      contributions_on_overtime: "same_rates_as_regular_salary"
      
    bonus_contributions:
      annual_bonus: "13th_month_salary"
      vacation_bonus: "half_month_salary"
      christmas_bonus: "full_month_salary"
      contribution_treatment: "same_rates_but_separate_reporting"
      
    termination_calculations:
      severance_pay: "legal_minimum_based_on_tenure"
      unused_vacation: "accumulated_vacation_days × daily_rate"
      final_contributions: "employer_and_employee_on_final_payments"
```

## Employee Lifecycle Management

### New Employee Onboarding
```yaml
Employee_Onboarding_Process:
  data_collection:
    personal_information:
      - "Full name (Greek and Latin characters)"
      - "AFM (Tax identification number)"
      - "AMKA (Social security number)"
      - "Identity card or passport"
      - "Address and contact information"
      
    employment_details:
      - "Position title and job description"
      - "Employment start date"
      - "Salary and payment frequency"
      - "Working hours and schedule"
      - "Employment contract type (indefinite/fixed-term)"
      
  efka_registration:
    insurance_category_determination: "Based on position and salary level"
    contribution_rate_assignment: "Current 2026 rates application"
    employer_notification: "EFKA employer portal submission"
    employee_card_request: "Social security card application"
    
  integration_activities:
    aade_coordination: "Cross-reference with tax authority"
    payroll_system_setup: "Add to monthly payroll processing"
    compliance_calendar: "Add employee-specific deadlines"
    documentation_filing: "Archive onboarding documents"
```

### Employee Data Updates
```yaml
Employee_Updates_Management:
  salary_changes:
    effective_date: "Date of salary change"
    contribution_recalculation: "Update contribution rates and amounts"
    retroactive_adjustments: "Handle backdated changes"
    efka_notification: "Report changes to EFKA portal"
    
  position_changes:
    job_title_updates: "Change in position or responsibilities"
    insurance_category_review: "Potential category change assessment"
    contribution_rate_impact: "Recalculate if rates change"
    documentation_update: "Update employment contracts"
    
  personal_information_changes:
    address_updates: "Residence or mailing address changes"
    name_changes: "Marriage or legal name changes"
    contact_updates: "Phone number or email changes"
    dependent_changes: "Addition/removal of dependents for benefits"
```

### Employee Termination Processing
```yaml
Termination_Process:
  pre_termination_calculations:
    final_salary_period: "Calculate final month contributions"
    unused_vacation_pay: "Vacation days × daily_salary_rate"
    severance_calculations: "Legal minimum based on tenure"
    bonus_prorations: "13th salary and other bonuses"
    
  efka_notifications:
    termination_report: "Submit employee termination to EFKA"
    final_contributions: "Submit final contribution calculations"
    clearance_certificate: "Request employee clearance certificate"
    
  post_termination_activities:
    record_archiving: "Move employee to terminated records"
    final_reconciliation: "Ensure all contributions paid"
    compliance_documentation: "Maintain records per legal requirements"
    reference_availability: "Prepare employment verification documents"
```

## Advanced Compliance Features

### Deadline Management & Monitoring
```yaml
EFKA_Compliance_Calendar:
  monthly_deadlines:
    employee_data_submission: "15th of following month"
    contribution_payments: "Last working day of following month"
    new_hire_notifications: "8 days from start date"
    termination_notifications: "8 days from termination date"
    
  quarterly_deadlines:
    quarterly_statements: "End of month following quarter"
    reconciliation_reports: "Cross-check with AADE quarterly reports"
    audit_preparation: "Maintain quarterly audit readiness"
    
  annual_requirements:
    annual_statements: "Employee annual contribution statements"
    employer_annual_report: "Complete employer contribution summary"
    insurance_renewals: "Review and renew employer insurance policies"
    
  penalty_avoidance:
    early_warning_system: "10-day advance deadline warnings"
    automatic_reminders: "Email and system notifications"
    penalty_calculations: "Estimate penalties for missed deadlines"
    corrective_action_plans: "Automated recovery procedures"
```

### Cross-System Integration
```yaml
Integration_Coordination:
  aade_cross_reference:
    employee_tax_data: "Coordinate with AADE employee tax withholdings"
    employer_tax_obligations: "Ensure consistency with corporate tax"
    quarterly_reconciliation: "Match EFKA and AADE quarterly reports"
    
  banking_integration:
    contribution_payments: "Match bank payments to EFKA obligations"
    payment_confirmations: "Verify successful contribution transfers"
    cash_flow_planning: "Predict monthly EFKA payment requirements"
    
  payroll_system_sync:
    salary_data_import: "Import payroll data for contribution calculation"
    deduction_calculations: "Calculate employee contribution deductions"
    net_pay_coordination: "Ensure net pay calculations include EFKA deductions"
    
  individual_tax_coordination:
    employee_tax_certificates: "Generate employee tax contribution certificates"
    personal_tax_support: "Support individual tax return preparation"
    dependent_benefits: "Coordinate family benefit calculations"
```

## Production Deployment Features

### Scalable Processing Architecture
```bash
# Performance and scalability commands
openclaw efka scale-processing --concurrent-employees 100 --batch-optimization
openclaw efka performance-monitor --processing-times --error-rates --throughput
openclaw efka load-balancing --priority-queues --resource-allocation

# Multi-client support for accounting firms
openclaw efka multi-tenant --client-separation --data-isolation --shared-resources
openclaw efka client-onboarding --new-client-setup --efka-credentials --integration-testing
openclaw efka cross-client-reporting --aggregated-statistics --compliance-summary
```

### Data Security & Compliance
```yaml
Security_Implementation:
  data_encryption:
    employee_data: "AES-256 encryption for personal information"
    financial_data: "Additional encryption for salary and contribution data"
    transmission_security: "TLS 1.3 for all government communications"
    
  access_control:
    role_based_permissions: "HR, Payroll, Management access levels"
    audit_logging: "Complete trail of all data access and modifications"
    session_management: "Secure session handling with timeout controls"
    
  gdpr_compliance:
    data_minimization: "Collect only necessary employee information"
    retention_policies: "Automatic data archival per Greek legal requirements"
    employee_rights: "Support for data access and deletion requests"
    consent_management: "Employee consent tracking and documentation"
    
  four_eyes_approval:
    description: "All EFKA submissions require two-person approval per the four-eyes workflow defined in the canonical data map and greek-compliance-aade skill"
    prepare_role: "accountant"
    approve_role: "senior_accountant"
    enforcement: "Filing must have status 'approved' before submission is allowed"
    audit: "Both preparer and approver recorded in unified audit event"
```

## Usage Examples for Greek Companies

### Monthly Payroll Processing
```bash
# Complete monthly EFKA processing workflow
$ openclaw efka monthly-process --february-2026 --all-employees

ðŸÂ€ºï¸ EFKA Monthly Processing - February 2026:

👥 Employee Summary:
✅ Active Employees: 45
✅ New Hires: 2 (registered with EFKA)
✅ Terminations: 1 (final contributions calculated)
✅ Salary Changes: 3 (contribution rates updated)

💰 Contribution Calculations:
✅ Total Gross Payroll: ‚¬67,500.00
✅ Employer Contributions: ‚¬26,145.30
   ├─ Main Insurance (24.56%): ‚¬16,583.00
   ├─ Auxiliary (3.00%): ‚¬2,025.00
   ├─ Employment (1.55%): ‚¬1,046.25
   └─ Health (9.76%): ‚¬6,491.05

✅ Employee Deductions: ‚¬15,187.50
   ├─ Main Insurance (16.00%): ‚¬10,800.00
   ├─ Auxiliary (3.00%): ‚¬2,025.00
   ├─ Employment (0.55%): ‚¬371.25
   └─ Health (2.55%): ‚¬1,991.25

📊 Processing Results:
✅ All calculations validated ✅
✅ Cross-checked with AADE data ✅  
✅ Banking payment scheduled ✅
✅ EFKA submission files generated ✅

⚠ï¸ Action Required: 
- Submit to EFKA portal by March 15th
- Bank transfer ‚¬26,145.30 by February 29th
```

### New Employee Registration
```bash
$ openclaw efka employee-onboard --employee "Μαρία Παπαδοπούλου" --start-date 2026-02-20

👤 Employee Onboarding - Μαρία Παπαδοπούλου:

📀¹ Personal Information:
✅ Full Name: Μαρία Παπαδοπούλου (Maria Papadopoulou)
✅ AFM: 123456789
✅ AMKA: 12345678901
✅ Address: ΀ºεπ°π . Συγγρού 45, Αθήνα 11742
✅ Position: ΀ºογίσπžρια (Accountant)

💼 Employment Details:
✅ Start Date: February 20, 2026
✅ Monthly Salary: ‚¬1,800.00
✅ Employment Type: Indefinite contract
✅ Working Hours: Full-time (40 hours/week)
✅ Insurance Category: 101 (Main insurance - private sector)

🧮 Contribution Calculations:
✅ Monthly Employer Cost: ‚¬663.47
   ├─ Employer Contributions: ‚¬442.08
   ├─ Gross Salary: ‚¬1,800.00
   └─ Total Employment Cost: ‚¬2,242.08

✅ Monthly Employee Deductions: ‚¬397.90
✅ Employee Net Salary: ‚¬1,402.10

📤 Next Steps:
- EFKA registration submitted ✅
- Payroll system updated ✅  
- Employee card application submitted ✅
- Welcome package prepared ✅

âÂ° Deadlines:
- EFKA confirmation expected by: February 28, 2026
- First month contributions due: March 31, 2026
```

### Integration with Meta-Skill
```bash
# Meta-skill coordinated EFKA processing
$ openclaw greek employee-management --comprehensive-processing

# Behind the scenes coordination:
# 1. EFKA Integration: Process payroll and contributions
# 2. Greek Compliance AADE: Cross-validate tax withholdings  
# 3. Banking Integration: Schedule contribution payments
# 4. Individual Taxes: Update employee tax certificates
# 5. CLI Deadline Monitor: Update EFKA compliance deadline tracker
# 6. Email Processor: Send employee notifications in Greek
```

### Compliance Monitoring Dashboard
```bash
$ openclaw efka compliance-dashboard --current-status --upcoming-deadlines

ðŸÂ€ºï¸ EFKA Compliance Dashboard - February 19, 2026:

📊 Current Status:
✅ All employees registered with EFKA
✅ February contributions calculated and validated
✅ No overdue submissions
✅ Banking payments up to date

âÂ° Upcoming Deadlines:
🔔 February 29, 2026: Monthly contribution payment (‚¬26,145.30)
🔔 March 15, 2026: February employee data submission  
🔔 March 28, 2026: New hire registration (2 employees)

⚠ï¸ Attention Required:
- Salary increase for 3 employees effective March 1st
- Annual employee statements due March 31st  
- Quarterly reconciliation with AADE due March 31st

📈 Year-to-Date Summary:
✅ Total Contributions Paid: ‚¬78,435.90
✅ Employees Processed: 47
✅ Compliance Rate: 100%
✅ No penalties incurred
```

## Success Metrics for EFKA Integration

A successful EFKA API integration should achieve:
- ✅ 100% accurate contribution calculations per Greek law
- ✅ Complete employee lifecycle management automation
- ✅ Seamless integration with existing payroll systems
- ✅ Real-time compliance monitoring and deadline management
- ✅ Zero missed deadlines or penalty incidents
- ✅ Complete audit trail and documentation
- ✅ Multi-client support for accounting firm deployment
- ✅ OpenClaw artifact deployment ready for instant setup

## OpenClaw Artifact Deployment

This skill is specifically designed as an OpenClaw artifact with:
- **Complete file-based processing architecture**
- **No external API dependencies requiring complex authentication**
- **Robust error handling and recovery procedures**
- **Integration hooks for all other Greek accounting skills**
- **Production-ready configuration files and templates**
- **Comprehensive evaluation test cases for validation**

Remember: This skill completes the advanced integration capabilities of your Greek accounting automation system, providing comprehensive social security management that integrates seamlessly with all other OpenClaw skills for complete Greek business automation.