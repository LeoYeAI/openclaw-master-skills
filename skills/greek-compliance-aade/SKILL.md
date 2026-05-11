---
name: greek-compliance-aade
description: Greek tax compliance with AADE/TAXIS integration — VAT, payroll, EFKA, municipal taxes, stamp duty. Human confirmation for all submissions.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "compliance", "aade", "vat", "taxis", "mydata"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "curl"], "env": ["OPENCLAW_DATA_DIR", "AADE_USERNAME", "AADE_PASSWORD"]}, "notes": "AADE/TAXIS credentials are required only when submitting filings to the government portal. The skill can prepare filings offline without credentials. All submissions require human approval (four-eyes workflow) before transmission.", "optional_env": {"GOOGLE_CALENDAR_ID": "Google Calendar ID for compliance deadline sync (optional)"}}}
---

# Greek Compliance & AADE Integration

This skill transforms OpenClaw into a Greek accounting compliance specialist, handling AADE submissions, VAT calculations, payroll processing, social security contributions, and regulatory deadlines specific to Greek business operations.


## Setup

```bash
# 1. Set data directory
export OPENCLAW_DATA_DIR="/data"

# 2. AADE credentials (required only for submitting filings — preparation works offline)
export AADE_USERNAME="your-aade-username"
export AADE_PASSWORD="your-aade-password"

# 3. Ensure dependencies
which jq curl || sudo apt install jq curl

# 4. Create compliance directories
mkdir -p $OPENCLAW_DATA_DIR/compliance/{vat,efka,mydata,e1,e3}
```

**Security notes:**
- AADE credentials are only used when submitting filings to the government portal
- All submissions require human approval (four-eyes workflow: preparer ≠ approver)
- Filing preparation, VAT calculation, and report generation work fully offline
- Credentials are never stored on disk — always use environment variables


## Core Philosophy

- **Greek Law First**: All calculations and processes comply with current Greek tax and labor law
- **AADE Ready**: All data formatted for direct TAXIS platform submission
- **Audit Compliant**: Complete paper trail meeting Greek audit requirements
- **Real-time Compliance**: Continuous monitoring of regulatory changes and deadlines
- **Payroll Precision**: Accurate social security and tax calculations for Greek employees

## Key Capabilities

### 1. AADE & TAXIS Integration
- **VAT Return Preparation**: Automated VAT calculation and TAXIS XML generation
- **E-Books Compliance**: Digital accounting records per Greek Law 4308/2014
- **Invoice Registration**: Real-time myDATA platform integration for invoice submission
- **Tax Declaration Prep**: Income tax return data compilation and formatting
- **Audit File Generation**: SAF-T (Standard Audit File for Tax) creation for AADE audits
- **Digital Signatures**: Integration with Greek qualified electronic signature providers

### 2. Greek VAT & Tax Management
- **VAT Rate Application**: Automatic application of current Greek VAT rates (24%, 13%, 6%, 0%)
- **Reverse Charge Handling**: EU and non-EU reverse charge VAT calculations
- **VAT Refund Tracking**: Monitor VAT refund applications and status with AADE
- **Withholding Tax**: Automatic calculation for freelancers, dividends, rent, and professional services
- **Stamp Duty Calculator**: Legal stamp duty (π¡αρπžςσημο) for contracts and documents
- **Real Estate Transfer Tax**: Property transaction tax calculations

### 3. Payroll & Social Security (EFKA/IKA)
- **Employee Hour Tracking**: Record working hours for hourly and project-based employees
- **Salary Calculations**: Gross to net salary with all Greek deductions
- **Social Security Contributions**: EFKA, IKA, unemployment, and health insurance calculations
- **Overtime Calculations**: Greek labor law compliant overtime rates and limits
- **Holiday Pay**: Vacation, sick leave, and public holiday entitlements
- **13th & 14th Salary**: Automatic calculation of mandatory bonus payments
- **Severance Pay**: Legal severance calculations per Greek labor law
- **Payroll Tax Withholding**: Individual income tax withholding and annual reconciliation

### 4. Municipal & Local Tax Management  
- **Property Tax (ENFIA)**: Annual property tax calculations and payment tracking
- **Municipal Fees**: Waste collection, lighting, and other local authority charges
- **Business License Renewal**: Track and alert for business license renewals
- **Fire Department Fees**: Annual fire safety certificate renewals
- **Chamber of Commerce**: Professional chamber membership and fee tracking

### 5. Greek Banking & Payment Integration
- **Greek Bank Connectivity**: Integration with Alpha Bank, National Bank, Eurobank, Piraeus
- **SEPA Payment Processing**: EU standard payment initiation and tracking
- **Greek IBAN Validation**: Verify Greek bank account numbers and routing
- **Bank Reconciliation**: Match Greek banking formats with accounting records
- **Currency Handling**: EUR primary with foreign currency conversion tracking

## Implementation Guidelines

### AADE/TAXIS Integration Workflow

#### Phase 1: Data Collection & Validation
1. **Document Classification**: Identify invoice types per Greek tax code requirements
2. **VAT Validation**: Cross-check VAT numbers against AADE VIES database
3. **Business Rules Check**: Ensure compliance with Greek accounting standards
4. **Data Completeness**: Verify all mandatory fields for TAXIS submission
5. **Digital Signature Prep**: Prepare documents for qualified electronic signature

#### Phase 2: TAXIS XML Generation
1. **Schema Validation**: Use current AADE XML schemas for accuracy
2. **Field Mapping**: Map accounting data to TAXIS required fields
3. **Calculation Verification**: Double-check all tax calculations
4. **Batch Processing**: Group transactions for efficient TAXIS submission
5. **Error Handling**: Flag validation errors before submission attempt

#### Phase 3: AADE Submission & Monitoring
1. **API Connection**: Secure connection to TAXIS web services
2. **Real-time Submission**: Submit validated XML files to AADE
3. **Receipt Confirmation**: Capture and store AADE confirmation receipts
4. **Error Resolution**: Handle AADE rejection messages and corrections
5. **Status Tracking**: Monitor submission status and payment confirmations

### Payroll Processing Workflow

#### Employee Hour Tracking System
```yaml
Hour Categories:
  regular_hours:
    - max_per_day: 8
    - max_per_week: 40
    - rate_multiplier: 1.0
    
  overtime_hours:
    - daily_overtime: "Hours 9-10 per day"
    - weekly_overtime: "Hours 41-45 per week"
    - rate_multiplier: 1.25
    
  exceptional_overtime:
    - daily_exceptional: "Hours 11+ per day"
    - weekly_exceptional: "Hours 46+ per week"  
    - rate_multiplier: 1.5
    
  holiday_work:
    - public_holidays: "Greek national holidays"
    - rate_multiplier: 2.0
    
  night_shift:
    - hours: "22:00-06:00"
    - additional_rate: 0.25
```

#### Greek Social Security Calculations
```yaml
Employee Contributions:
  efka_main:
    - rate: 6.67%
    - cap: "Monthly maximum ‚¬6,500"
    - description: "Main pension contribution"
    
  efka_auxiliary:
    - rate: 3.0%
    - cap: "Monthly maximum ‚¬6,500"
    - description: "Auxiliary pension"
    
  unemployment_insurance:
    - employee_rate: 0.87%
    - employer_rate: 2.26%
    - description: "OAED unemployment insurance"
    
  health_insurance:
    - employee_rate: 2.95%
    - employer_rate: 4.3%
    - description: "EOPYY health insurance"

Employer Contributions:
  efka_employer:
    - rate: 22.29%
    - description: "Main employer EFKA contribution"
    
  work_accidents:
    - rate: 1.0%
    - description: "Work accident insurance"
    
  family_benefits:
    - rate: 1.0%
    - description: "Family allowance fund"
```

#### Tax Withholding Calculations
```yaml
Income Tax Brackets (2026):
  bracket_1:
    - range: "‚¬0 - ‚¬10,000"
    - rate: 9%
    
  bracket_2:
    - range: "‚¬10,001 - ‚¬20,000"
    - rate: 22%
    
  bracket_3:
    - range: "‚¬20,001 - ‚¬30,000"
    - rate: 28%
    
  bracket_4:
    - range: "‚¬30,001 - ‚¬40,000"
    - rate: 36%
    
  bracket_5:
    - range: "‚¬40,001+"
    - rate: 44%

Tax Credits:
  basic_credit: ‚¬2,100
  family_credit: "‚¬777 per child"
  disability_credit: "Per disability level"
  low_income_credit: "Income dependent"
```

## Greek VAT Specifications

### VAT Rates & Applications
```yaml
Standard_Rate_24%:
  applies_to:
    - "General goods and services"
    - "Professional services" 
    - "Construction services"
    - "Telecommunications"
    - "Financial services"
    
Reduced_Rate_13%:
  applies_to:
    - "Food and beverages"
    - "Restaurants and catering"
    - "Hotels and accommodation"
    - "Medical services"
    - "Educational services"
    
Super_Reduced_Rate_6%:
  applies_to:
    - "Books and newspapers"
    - "Pharmaceutical products"
    - "Cultural events"
    - "Public transport"
    
Zero_Rate_0%:
  applies_to:
    - "Exports outside EU"
    - "International transport"
    - "Diplomatic exemptions"
    - "Some medical equipment"

Island_Rates:
  description: "Reduced rates for Greek islands"
  standard_island: 17%
  reduced_island: 9%
  super_reduced_island: 4%
  applies_to:
    - "Aegean islands (except Skyros)"
    - "Ionian islands (except Corfu and Zakynthos)"
```

### myDATA Invoice Integration
```yaml
Required_Invoice_Fields:
  issuer_info:
    - vat_number: "Greek VAT registration number"
    - tax_office: "Tax office code"
    - business_name: "Legal business name"
    - address: "Complete registered address"
    
  customer_info:
    - vat_number: "Customer VAT (if business)"
    - name: "Customer name/business name"
    - address: "Customer address"
    - country: "ISO country code"
    
  invoice_details:
    - series: "Invoice series designation"
    - number: "Sequential invoice number"
    - issue_date: "ISO date format"
    - invoice_type: "Sales, Services, Credit Note, etc."
    
  line_items:
    - description: "Service/product description"
    - quantity: "Decimal quantity"
    - unit_price: "Price per unit"
    - vat_rate: "Applicable VAT percentage"
    - vat_amount: "Calculated VAT"
    - total_amount: "Line total including VAT"
    
  payment_methods:
    - method_code: "AADE payment method code"
    - amount: "Amount paid by this method"
    - payment_date: "When payment received"
```

## Regulatory Deadline Management

### Monthly Deadlines
```yaml
VAT_Return:
  due_date: "20th of following month"
  late_penalty: "5% of tax due + interest"
  
Payroll_Submissions:
  efka_contributions: "15th of following month"
  withholding_tax: "20th of following month"
  
Invoice_Submission:
  mydata_upload: "Real-time (within 24 hours)"
  batch_processing: "Daily at midnight"
```

### Quarterly Deadlines  
```yaml
Quarterly_VAT:
  q1_deadline: "April 25"
  q2_deadline: "July 25"
  q3_deadline: "October 25"
  q4_deadline: "January 25 (following year)"
  
Social_Security_Reports:
  efka_quarterly: "Last day of month following quarter"
  accident_reports: "January 31, April 30, July 31, October 31"
```

### Annual Deadlines
```yaml
Income_Tax_Returns:
  individuals: "June 30"
  businesses: "May 31"
  extensions_available: "Until August 31 with penalty"
  
Property_Tax_ENFIA:
  declaration_due: "April 30"
  payment_installments:
    - first: "End of July"
    - second: "End of September"
    - third: "End of November"
    - fourth: "End of January (following year)"
    
Annual_Financial_Statements:
  small_companies: "July 31"
  medium_large_companies: "June 30"
  audit_required: "Companies over ‚¬4M revenue"
```

## Workflow Templates

### Daily Greek Accounting Routine

#### Morning Startup (8:00 AM Greece Time)
```markdown
1. **AADE Status Check**: Verify TAXIS connectivity and any system announcements
2. **myDATA Sync**: Process overnight invoice submissions and confirmations
3. **VAT Rate Updates**: Check for any VAT rate changes or announcements
4. **Deadline Alerts**: Review upcoming compliance deadlines (next 7 days)
5. **Payroll Hour Collection**: Gather employee hour submissions from previous day
6. **Bank Reconciliation**: Download overnight bank transactions from Greek banks
```

#### Continuous Processing
```markdown
1. **Invoice Processing**: Real-time myDATA submission for new invoices
2. **Hour Tracking**: Record employee hours as they're submitted
3. **Expense Categorization**: Apply correct VAT rates and deductibility rules
4. **Social Security Monitoring**: Track contribution calculations and payments
5. **Municipal Fee Tracking**: Monitor local authority payment due dates
```

#### End of Day (18:00 Greece Time)
```markdown
1. **Daily VAT Summary**: Calculate daily VAT position and running totals
2. **Payroll Validation**: Verify all employee hours recorded accurately
3. **AADE Submission Confirmation**: Ensure all invoices successfully submitted
4. **Tomorrow's Alerts**: Preview upcoming deadlines and required actions
5. **Backup Verification**: Confirm all processed data backed up securely
```

### Monthly Processing Workflow

#### Pre-Month End (Days 25-30)
```markdown
1. **VAT Return Preparation**: Compile VAT transactions for monthly return
2. **Payroll Calculations**: Process monthly salaries with all deductions
3. **EFKA Contribution Prep**: Calculate and prepare social security payments
4. **Client Invoice Generation**: Create and submit client invoices via myDATA
5. **Expense Validation**: Final review of monthly business expenses
```

#### Month End Processing (Day 1-5 of following month)
```markdown
1. **VAT Return Submission**: Submit monthly VAT return to AADE via TAXIS
2. **Payroll Distribution**: Generate payslips and process salary payments
3. **Social Security Filing**: Submit EFKA contributions and employee declarations
4. **Municipal Tax Review**: Check for any municipal fee payments due
5. **Financial Statement Prep**: Monthly P&L and balance sheet generation
```

## Payroll Processing Examples

### Employee Hour Tracking Interface
```yaml
Employee: "Nikos Papadopoulos"
Pay_Period: "February 2026"
Employee_Type: "Full-time hourly"

Weekly_Schedule:
  monday: "08:00-16:00 (8 hours)"
  tuesday: "08:00-16:00 (8 hours)"
  wednesday: "08:00-16:00 (8 hours)"  
  thursday: "08:00-16:00 (8 hours)"
  friday: "08:00-16:00 (8 hours)"
  saturday: "Overtime: 08:00-12:00 (4 hours)"
  sunday: "Rest day"

Monthly_Calculation:
  regular_hours: 160 # (4 weeks × 40 hours)
  overtime_hours: 16 # (4 weeks × 4 hours Saturday)
  public_holiday_hours: 8 # (Clean Monday)
  total_hours: 184
  
Gross_Pay_Calculation:
  hourly_rate: ‚¬12.00
  regular_pay: ‚¬1,920.00 # (160 × ‚¬12.00)
  overtime_pay: ‚¬240.00 # (16 × ‚¬12.00 × 1.25)
  holiday_pay: ‚¬192.00 # (8 × ‚¬12.00 × 2.0)
  gross_total: ‚¬2,352.00
```

### Social Security & Tax Deductions
```yaml
Social_Security_Deductions:
  efka_main: ‚¬156.81 # (‚¬2,352 × 6.67%)
  efka_auxiliary: ‚¬70.56 # (‚¬2,352 × 3.0%)
  unemployment: ‚¬20.46 # (‚¬2,352 × 0.87%)
  health_insurance: ‚¬69.38 # (‚¬2,352 × 2.95%)
  total_ss_deductions: ‚¬317.21

Income_Tax_Calculation:
  annual_projection: ‚¬28,224 # (‚¬2,352 × 12)
  tax_bracket_1: ‚¬900.00 # (‚¬10,000 × 9%)
  tax_bracket_2: ‚¬2,200.00 # (‚¬10,000 × 22%)
  tax_bracket_3: ‚¬2,240.00 # (‚¬8,224 × 28%)
  gross_annual_tax: ‚¬5,340.00
  annual_tax_credit: ‚¬2,100.00
  net_annual_tax: ‚¬3,240.00
  monthly_withholding: ‚¬270.00

Net_Pay_Calculation:
  gross_pay: ‚¬2,352.00
  social_security: -‚¬317.21
  income_tax: -‚¬270.00
  net_pay: ‚¬1,764.79
```

## Integration Requirements

### Required OpenClaw Skills
```bash
# Core document processing
npx openclaw skills add deepread        # OCR for Greek documents
npx openclaw skills add pdf-tools       # PDF manipulation

# Other Greek accounting skills (install alongside this one)
npx openclaw skills add greek-banking-integration  # Bank statement import for VAT reconciliation
npx openclaw skills add efka-api-integration       # Social security submissions
npx openclaw skills add cli-deadline-monitor       # Deadline alerts for AADE obligations
npx openclaw skills add client-data-management     # Client records and filing history
```

### Government API Connections
```yaml
AADE_TAXIS:
  base_url: "https://www1.aade.gr/taxisnet"
  authentication: "Greek Tax ID + Password + 2FA"
  rate_limits: "1000 requests/hour"
  
myDATA_Platform:
  base_url: "https://mydata-dev.azure-api.net" # Test environment
  production_url: "https://mydatapi.aade.gr"
  authentication: "Username/password + optional digital certificate"
  real_time_required: "Invoice submission within 24 hours"
  
EFKA_Portal:
  base_url: "https://www.efka.gov.gr"
  submission_method: "File upload + digital signature"
  deadlines: "15th of following month"
  
Greek_Banks_API:
  alpha_bank: "Open Banking PSD2 API"
  nbg: "Developer Portal API"
  eurobank: "Business API Gateway"
  piraeus: "WinBank Business API"
```

## Security & Compliance Features

### Data Protection (GDPR Greece)
- **Personal Data Encryption**: All employee and client data encrypted at rest
- **Access Logging**: Complete audit trail of all data access
- **Data Minimization**: Only collect necessary data for compliance
- **Right to Erasure**: Automated employee data deletion processes
- **Consent Management**: Track and manage employee consent for data processing

### Greek Audit Requirements
- **Digital Signatures**: Integration with Greek qualified signature providers
- **Immutable Records**: Blockchain-based record integrity for critical transactions
- **SAF-T Generation**: Standard Audit File for Tax authorities on demand
- **Document Retention**: 5-year retention policy per Greek tax law
- **Change Tracking**: Complete modification history for all financial records

### Four-Eyes Approval Workflow for Government Submissions

All filings to AADE, EFKA, and myDATA require two-person approval before submission. This protects against accidental filings and provides professional liability coverage.

```yaml
Four_Eyes_Workflow:
  step_1_prepare:
    role: "accountant"
    action: "Prepare the filing (VAT return, EFKA declaration, myDATA submission)"
    command: "openclaw greek vat-return --client EL123456789 --period 2026-01 --prepare"
    output: "Draft filing saved to /data/processing/compliance/ with status: prepared"
    
  step_2_review:
    role: "senior_accountant"
    action: "Review the prepared filing — verify figures, check for anomalies"
    command: "openclaw greek review-filing --afm EL123456789 --period 2026-01 --type vat"
    output: "Filing displayed with summary, comparison to prior period, and anomaly flags"
    
  step_3_approve:
    role: "senior_accountant"
    action: "Explicitly approve the filing for submission"
    command: "openclaw greek approve-filing --afm EL123456789 --period 2026-01 --type vat --approved-by m.papadopoulou"
    output: "Filing status changed to: approved. Approval logged to audit trail."
    
  step_4_submit:
    role: "senior_accountant"
    action: "Submit the approved filing to the government system"
    command: "openclaw greek submit-filing --afm EL123456789 --period 2026-01 --type vat"
    gate: "System verifies filing has approval record before allowing submission"
    output: "Filing submitted. Confirmation receipt stored. Status: submitted."
    
  enforcement:
    - "A filing with status 'prepared' cannot be submitted — it must be 'approved' first"
    - "The preparer and approver must be different users"
    - "Both preparer and approver are recorded in the audit event"
    - "Emergency override requires admin role and logs a security event"
    
  audit_record:
    prepared_by: "username of accountant who prepared the filing"
    prepared_at: "timestamp of preparation"
    approved_by: "username of senior_accountant who approved"
    approved_at: "timestamp of approval"
    submitted_by: "username of person who triggered submission"
    submitted_at: "timestamp of submission"
    submission_ref: "AADE/EFKA confirmation reference"
```

This workflow applies to:
- VAT returns (F2) to AADE/TAXIS
- EFKA social security declarations (ΑΠΔ)
- myDATA invoice submissions (batch)
- E1 individual tax returns
- Corporate tax filings
- Any amended or corrected filing

## Performance Metrics

### AADE Integration Success
- **Submission Success Rate**: >99% successful TAXIS submissions
- **myDATA Real-time Compliance**: 100% invoices submitted within 24 hours
- **VAT Calculation Accuracy**: >99.9% accuracy in VAT computations
- **Deadline Compliance**: Zero missed regulatory deadlines

### Payroll Processing Efficiency  
- **Hour Processing Speed**: 100 employee hours processed in <5 minutes
- **Calculation Accuracy**: >99.9% accuracy in payroll calculations
- **Social Security Compliance**: 100% accurate EFKA contribution calculations
- **Payslip Generation**: Automated payslips ready within 2 hours of hour submission

## Usage Examples

### Example 1: Monthly VAT Processing
```markdown
Command: openclaw compliance vat-return --client EL987654321 --period 2026-02 --prepare
System Response:
1. Loads all February invoices and receipts from /data/clients/EL987654321/documents/
2. Applies correct VAT rates (24%, 13%, 6%) based on transaction type and KAD
3. Calculates VAT position: EUR15,250 collected, EUR3,480 paid = EUR11,770 net due
4. Generates TAXIS XML at /data/compliance/vat/EL987654321_202602_vat_return.xml
5. Validates XML against current AADE schema before submission
Output: "February VAT return prepared. Net VAT due: EUR11,770. Payment due: March 20, 2026."
Next step: openclaw compliance vat-return --client EL987654321 --period 2026-02 --submit
```

### Example 2: Employee Payroll Processing
```markdown
Command: openclaw compliance payroll --client EL987654321 --employee "Maria Konstantinou" --period 2026-02 --hours-file /data/incoming/hours/maria_feb2026.csv
System Response:
1. Loads hours data: 168 regular + 8 Sunday overtime + 8 public holiday (Clean Monday)
2. Calculates gross pay: EUR15/hr x 168 + EUR18.75/hr x 8 + EUR30/hr x 8 = EUR2,910.00
3. Applies EFKA deductions: EUR431.58 (employee portion across all categories)
4. Calculates income tax withholding: EUR402.30
5. Writes payslip to /data/clients/EL987654321/payroll/2026-02/maria_konstantinou_payslip.pdf
6. Prepares EFKA declaration file for submission
Output: "Payslip generated. Net pay: EUR2,076.12. EFKA declaration ready for submission."
Next step: openclaw efka submit-declaration --client EL987654321 --period 2026-02
```

### Example 3: Real-time Invoice Submission to myDATA
```markdown
Command: openclaw compliance mydata-submit --client EL987654321 --invoice /data/ocr/output/accounting-ready/inv_2026_456.pdf
System Response:
1. Extracts required myDATA fields from invoice (vendor, customer, amounts, VAT, dates)
2. Identifies EU client -- applies reverse charge VAT (0% output, note added)
3. Generates myDATA XML with required structure
4. Submits to AADE myDATA API at mydatapi.aade.gr
5. Receives and stores confirmation receipt
6. Logs submission to /data/clients/EL987654321/compliance/filings.json
Output: "Invoice #2026-456 submitted to myDATA. Confirmation: AAD-2026-ABC123456789."
```

## Troubleshooting & Error Handling

### Common AADE Integration Issues
```yaml
Connection_Errors:
  symptoms: "TAXIS login failures"
  solutions:
    - "Check internet connectivity"
    - "Verify tax credentials"
    - "Check 2FA token validity"
    - "Retry with exponential backoff"
    
Validation_Errors:
  symptoms: "XML submission rejected"
  solutions:
    - "Validate against current AADE schema"
    - "Check all mandatory fields"
    - "Verify VAT calculations"
    - "Confirm digital signature validity"
    
Rate_Limiting:
  symptoms: "Too many requests error"
  solutions:
    - "Implement request queuing"
    - "Batch multiple submissions"
    - "Spread submissions across day"
    - "Use off-peak hours for bulk operations"
```

### Payroll Calculation Issues
```yaml
Hour_Tracking_Errors:
  symptoms: "Overtime calculations incorrect"
  solutions:
    - "Verify Greek labor law compliance"
    - "Check holiday calendar updates"
    - "Validate employee contract terms"
    - "Review collective agreement rules"
    
Social_Security_Errors:
  symptoms: "EFKA contribution mismatch"
  solutions:
    - "Update contribution rates quarterly"
    - "Check salary caps and thresholds"
    - "Verify employee insurance category"
    - "Review disability/age adjustments"
```

## Success Criteria

A successful Greek compliance system should achieve:
- ✅ 100% AADE deadline compliance
- ✅ 99.9% VAT calculation accuracy  
- ✅ Real-time myDATA invoice submission
- ✅ Zero payroll calculation errors
- ✅ Complete audit trail for all transactions
- ✅ 80% reduction in manual compliance work
- ✅ Integration with all major Greek banks
- ✅ Automated social security submissions

## Legal Disclaimers

### Professional Responsibility
- This skill assists with Greek tax compliance but does not replace professional accounting advice
- Users must verify all calculations against current Greek tax law
- Regular updates required as Greek tax regulations change
- Professional liability insurance recommended for accounting firms
- Final responsibility for tax compliance remains with the business owner/accountant

### Regulatory Updates
- Greek tax law changes frequently - skill requires regular updates
- AADE may change API specifications or requirements
- Social security rates and thresholds change annually
- Municipal tax rules vary by locality and change regularly
- Users must monitor official government announcements

Remember: This skill enhances accuracy and efficiency but professional oversight remains essential for Greek tax compliance.