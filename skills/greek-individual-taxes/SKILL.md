---
name: greek-individual-taxes
description: Comprehensive Greek individual tax return processing skill for employed individuals. Handles E1 form preparation, personal income tax calculations, deductions optimization, property taxes (ENFIA), and individual compliance management. Designed for Greek tax residents with employment income, property, and investment income.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "individual-tax", "e1-form", "enfia"]
metadata: {"openclaw": {"requires": {"bins": ["jq"], "env": ["OPENCLAW_DATA_DIR"]}, "notes": "Instruction-only skill. Prepares E1 tax return data from local files. Does not submit to AADE directly — submission is handled by greek-compliance-aade skill with human approval."}}
---

# Greek Individual Taxes

This skill transforms OpenClaw into a specialized Greek individual tax processor, handling personal income tax returns (E1 forms), deductions optimization, and individual compliance management for Greek tax residents.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
which jq || sudo apt install jq
```

No external credentials required. This skill prepares E1 tax return data from local files. Actual submission to AADE is handled by the `greek-compliance-aade` skill with human approval.


## Core Philosophy

- **Employed Individual Focus**: Optimized for salary earners and employees (primary user base)
- **Deduction Maximization**: Identify and apply all legal deductions and tax credits
- **Compliance First**: Ensure adherence to Greek individual tax law and deadlines
- **Family Tax Planning**: Support for spouse and dependent optimization strategies
- **Property Integration**: Handle ENFIA property taxes and rental income
- **Investment Awareness**: Process dividends, interest, and capital gains

## Key Capabilities

### 1. Individual Income Tax (E1 Form) Processing
- **Employment Income**: Salary, bonuses, 13th/14th month payments, overtime
- **Professional Income**: Freelance work, consulting, part-time professional services
- **Property Income**: Rental income from residential and commercial properties
- **Investment Income**: Dividends, interest, capital gains, foreign income
- **Pension Income**: Retirement benefits and social security payments
- **Other Income**: Royalties, prizes, agricultural income

### 2. Greek Tax Deductions & Credits Optimization
- **Medical Expenses**: Healthcare costs, pharmacy, dental, medical equipment
- **Education Expenses**: Tuition fees, books, educational materials
- **Insurance Premiums**: Life insurance, health insurance, property insurance
- **Charitable Donations**: Donations to recognized Greek charitable organizations
- **Energy Efficiency Credits**: Home improvements, solar panels, energy upgrades
- **Family Tax Credits**: Spouse credits, dependent children credits
- **Disability Credits**: Credits for individuals or family members with disabilities

### 3. Property Tax Integration (ENFIA)
- **Primary Residence**: Main home property tax calculations and exemptions
- **Secondary Properties**: Vacation homes, investment properties
- **Commercial Properties**: Business property tax obligations
- **Property Tax Credits**: Insurance discounts, energy efficiency reductions
- **Municipal Property Taxes (TAP)**: Local property tax coordination
- **Property Transfer Taxes**: Real estate transaction tax management

### 4. Individual Compliance Management
- **Tax Return Deadlines**: E1 form submission by June 30th deadline
- **Payment Schedules**: Tax payment installment planning and management
- **Document Collection**: Gather required certificates and supporting documents
- **AADE Integration**: Electronic submission through TAXIS platform
- **Audit Preparation**: Individual audit defense and documentation
- **Tax Residence**: Greek tax residency determination and planning

## Implementation Guidelines

### E1 Form Processing Architecture

#### Income Categories & Processing
```yaml
Employment_Income:
  salary_income:
    sources: ["Employer certificates", "Monthly payslips", "13th/14th payments"]
    tax_treatment: "Progressive rates 9%-44%"
    deductions: ["Social security contributions", "Professional expenses"]
    
  overtime_compensation:
    calculation: "Regular rate × overtime multiplier"
    tax_treatment: "Included in total employment income"
    limits: "Greek labor law overtime limits"
    
  bonuses_and_benefits:
    types: ["Performance bonuses", "Company car", "Meal allowances", "Housing benefits"]
    valuation: "Fair market value for benefits in kind"
    exemptions: ["Meal vouchers up to ‚¬5/day", "Transport allowances"]

Professional_Income:
  freelance_services:
    tax_treatment: "Progressive rates with professional expenses"
    expense_deductions: ["Office rent", "Equipment", "Professional development"]
    presumptive_taxation: "Available for specific professions"
    
  consulting_income:
    withholding_tax: "20% withheld by clients"
    annual_reconciliation: "Net additional tax or refund calculation"
    expense_tracking: "Business meal deductions (50%)", "Travel expenses"]

Property_Income:
  rental_income:
    tax_rates: 
      - up_to_12000: "15%"
      - from_12001_to_35000: "35%" 
      - over_35000: "45%"
    deductions: ["Property maintenance", "Management fees", "Insurance", "Depreciation"]
    
  airbnb_income:
    licensing_requirement: "Short-term rental license required"
    tax_treatment: "As rental income with limited deductions"
    vat_implications: "13% VAT if over ‚¬10,000 annually"

Investment_Income:
  dividend_income:
    greek_companies: "5% withholding tax (final)"
    foreign_dividends: "Progressive rates with foreign tax credit"
    
  interest_income:
    bank_deposits: "15% withholding tax (final)"
    bonds: "15% withholding tax or progressive rates (taxpayer choice)"
    
  capital_gains:
    status: "Suspended until December 31, 2026"
    real_estate: "Suspended for property sales"
    securities: "Suspended for stock sales"
```

#### Greek Tax Deductions System
```yaml
Medical_Expenses:
  eligible_costs:
    - "Doctor visits and specialist consultations"
    - "Hospital expenses and surgery costs"  
    - "Prescription medications from pharmacies"
    - "Dental care and orthodontics"
    - "Medical equipment and devices"
    - "Physiotherapy and rehabilitation"
  
  limitations:
    annual_limit: "No maximum limit for medical expenses"
    supporting_documents: "Receipts with patient name and medical purpose"
    electronic_payments: "Additional 10% deduction for card/electronic payments"
    
Education_Expenses:
  eligible_institutions:
    - "Greek universities and technical schools"
    - "Recognized foreign universities"
    - "Private schools and tutoring centers"
    - "Language schools and certification programs"
  
  eligible_costs:
    - "Tuition fees and registration costs"
    - "Required textbooks and materials"
    - "Laboratory fees and equipment"
    - "Student housing (university dormitories)"
  
  limitations:
    per_child_limit: "No annual limit for education expenses"
    age_restrictions: "Generally up to age 24 for higher education"

Insurance_Premiums:
  life_insurance:
    annual_limit: "‚¬1,200 per person"
    eligible_policies: "Greek and EU insurance companies"
    
  health_insurance:
    annual_limit: "‚¬1,200 per person"  
    supplementary_coverage: "Private health insurance premiums"
    
  property_insurance:
    eligible: "Home insurance, fire insurance, earthquake insurance"
    enfia_discount: "20% ENFIA reduction for insured properties"

Charitable_Donations:
  eligible_organizations:
    - "Greek state and municipalities"
    - "Recognized charitable organizations"
    - "Churches and religious institutions"
    - "Educational institutions"
    - "Cultural organizations"
  
  limitations:
    maximum_deduction: "5% of total income or ‚¬2,000 (whichever is higher)"
    documentation: "Official donation receipts required"
```

### Tax Calculation Engine

#### Progressive Tax Rates (2026)
```yaml
Individual_Income_Tax_Brackets:
  bracket_1:
    income_range: "‚¬0 - ‚¬10,000"
    tax_rate: "9%"
    tax_amount: "‚¬0 - ‚¬900"
    
  bracket_2: 
    income_range: "‚¬10,001 - ‚¬20,000"
    tax_rate: "22%"
    tax_amount: "‚¬900 + 22% of excess over ‚¬10,000"
    
  bracket_3:
    income_range: "‚¬20,001 - ‚¬30,000" 
    tax_rate: "28%"
    tax_amount: "‚¬3,100 + 28% of excess over ‚¬20,000"
    
  bracket_4:
    income_range: "‚¬30,001 - ‚¬40,000"
    tax_rate: "36%"
    tax_amount: "‚¬5,900 + 36% of excess over ‚¬30,000"
    
  bracket_5:
    income_range: "‚¬40,001+"
    tax_rate: "44%"
    tax_amount: "‚¬9,500 + 44% of excess over ‚¬40,000"

Tax_Credits:
  basic_tax_credit: "‚¬2,100 per individual"
  spouse_credit: "‚¬2,100 (if spouse has no income)"
  dependent_children_credit: "‚¬777 per child"
  disability_credit: "Varies by disability percentage"
  low_income_credit: "Graduated reduction for income under ‚¬12,000"
  
Solidarity_Tax:
  threshold: "Income over ‚¬30,000"
  rates:
    - "‚¬30,001 - ‚¬40,000": "2.2%"  
    - "‚¬40,001 - ‚¬65,000": "5%"
    - "‚¬65,001 - ‚¬220,000": "6.5%"
    - "Over ‚¬220,000": "9%"
```

#### Tax Calculation Workflow
```python
def calculate_individual_tax(income_data, deductions, family_situation):
    """
    Calculate Greek individual income tax with optimization
    """
    # Step 1: Calculate total taxable income
    employment_income = sum(income_data['employment'])
    professional_income = sum(income_data['professional'])  
    property_income = calculate_rental_tax(income_data['property'])
    investment_income = sum(income_data['investment'])
    
    total_income = employment_income + professional_income + property_income + investment_income
    
    # Step 2: Apply deductions
    medical_deductions = min(deductions['medical'], total_income * 0.1)  # No limit
    education_deductions = deductions['education']  # No limit
    insurance_deductions = min(deductions['insurance'], 1200 * family_situation['family_members'])
    charity_deductions = min(deductions['charity'], max(total_income * 0.05, 2000))
    
    total_deductions = medical_deductions + education_deductions + insurance_deductions + charity_deductions
    taxable_income = max(0, total_income - total_deductions)
    
    # Step 3: Calculate progressive tax
    income_tax = calculate_progressive_tax(taxable_income)
    solidarity_tax = calculate_solidarity_tax(taxable_income)
    
    # Step 4: Apply tax credits  
    tax_credits = calculate_tax_credits(family_situation, taxable_income)
    
    net_tax = max(0, income_tax + solidarity_tax - tax_credits)
    
    return {
        'total_income': total_income,
        'taxable_income': taxable_income, 
        'total_deductions': total_deductions,
        'income_tax': income_tax,
        'solidarity_tax': solidarity_tax,
        'tax_credits': tax_credits,
        'net_tax': net_tax,
        'effective_rate': (net_tax / total_income) * 100 if total_income > 0 else 0
    }
```

## Workflow Templates

### Individual Tax Return Preparation

#### Document Collection Phase
```bash
#!/bin/bash
# Individual tax return document collection

# Employment income documents
openclaw individual collect-employment-docs --year 2025
  # - Employer certificates (Βεβαίπ°ση αποδοπ¡Ͻν)
  # - Social security contributions summary
  # - Withholding tax certificates

# Property income documents  
openclaw individual collect-property-docs --year 2025
  # - Rental agreements and income records
  # - Property expenses and maintenance receipts
  # - ENFIA property tax payments

# Investment income documents
openclaw individual collect-investment-docs --year 2025
  # - Bank interest statements
  # - Dividend certificates from Greek companies
  # - Foreign income documentation

# Deduction supporting documents
openclaw individual collect-deduction-docs --year 2025
  # - Medical expenses receipts (patient name required)
  # - Education expense receipts and certificates  
  # - Insurance premium payment receipts
  # - Charitable donation certificates
```

#### E1 Form Preparation Workflow  
```bash
#!/bin/bash
# E1 form automated preparation

# Step 1: Income calculation and validation
openclaw individual calculate-income --taxpayer-id $AFM --year 2025

# Step 2: Deduction optimization
openclaw individual optimize-deductions --include-all-eligible --electronic-payment-bonus

# Step 3: Tax calculation with family optimization
openclaw individual calculate-tax --include-spouse --include-dependents

# Step 4: E1 form generation
openclaw individual generate-e1-form --year 2025 --validate-data

# Step 5: AADE TAXIS preparation  
openclaw individual prepare-taxis-submission --digital-signature-ready

# Step 6: Payment planning
openclaw individual plan-tax-payments --installments --due-dates
```

#### Family Tax Optimization
```yaml
Family_Tax_Strategies:
  spouse_optimization:
    separate_returns:
      when_beneficial: "When spouse has significant deductible expenses"
      calculation: "Compare combined vs separate tax burden"
      
    joint_deduction_allocation:
      medical_expenses: "Allocate to higher-income spouse for better benefit"
      education_expenses: "Can be claimed by either parent"
      charitable_donations: "Optimize between spouses for maximum benefit"
      
  dependent_children:
    child_tax_credits: "‚¬777 per child under 18 or in education"
    education_expenses: "No limit on university tuition deductions"
    medical_expenses: "Include children's medical costs"
    
    age_transitions:
      - "Monitor when children turn 18 (affects tax credits)"
      - "Track university enrollment (extends education deductions)"
      - "Plan for children starting work (changes dependency status)"

  property_ownership_optimization:
    joint_ownership: "Split property income between spouses"
    primary_residence: "Optimize ENFIA exemptions and reductions"
    rental_properties: "Strategic allocation of rental income and expenses"
```

### Property Tax Integration (ENFIA)

#### ENFIA Calculation & Optimization
```yaml
ENFIA_Processing:
  primary_residence:
    base_calculation: "Based on objective property value and characteristics"
    exemptions:
      - "First ‚¬200,000 of single-person household value"
      - "Additional exemptions for large families"
      - "Disability exemptions for qualifying individuals"
    
    discounts:
      insurance_discount: "20% reduction for comprehensive property insurance"
      energy_efficiency: "Reductions for high energy rating properties"
      rural_properties: "50% reduction for properties in villages under 1,500 population"
      
  investment_properties:
    supplementary_tax: "Additional tax for total property value over ‚¬500,000"
    commercial_properties: "Different rates for business-use properties"
    rental_income_coordination: "ENFIA costs deductible from rental income"
    
  payment_scheduling:
    installment_options: "Up to 10 monthly installments"
    payment_methods: "Online, bank transfer, or cash at authorized locations"
    early_payment: "3% discount for full payment before April 30"
```

#### Municipal Tax Coordination
```yaml
Municipal_Property_Taxes:
  tap_coordination:
    collection_method: "Through electricity bills"
    rate_variation: "0.025%-0.035% by municipality"
    integration: "Coordinate with ENFIA for total property tax burden"
    
  waste_and_lighting:
    calculation_basis: "Property square meters × municipal rate"
    payment_frequency: "Annual via electricity bill"
    exemptions: "Limited exemptions for specific circumstances"
```

## Individual Tax Scenarios

### Scenario 1: Employed Individual with Property
```yaml
Taxpayer_Profile:
  employment:
    annual_salary: "‚¬35,000"
    employer_withholding: "‚¬6,500"
    social_security: "‚¬4,200"
    
  property:
    primary_residence_value: "‚¬180,000"
    enfia_paid: "‚¬450"
    rental_property_income: "‚¬8,000"
    rental_expenses: "‚¬2,000"
    
  family:
    marital_status: "married"
    spouse_income: "‚¬0"
    dependent_children: 2
    
Tax_Calculation:
  total_income: "‚¬41,000" # ‚¬35,000 salary + ‚¬6,000 net rental
  deductions: "‚¬2,450" # ENFIA + rental expenses
  taxable_income: "‚¬38,550"
  
  income_tax: "‚¬8,398"
  solidarity_tax: "‚¬945" 
  tax_credits: "‚¬3,654" # Basic + spouse + 2 children
  
  gross_tax: "‚¬9,343"
  withholding_credit: "‚¬6,500"
  net_tax_due: "‚¬2,843"
  
Optimization_Opportunities:
  - "Ensure spouse claims any eligible deductions separately"
  - "Maximize children's education expense deductions"
  - "Consider property insurance for ENFIA discount"
  - "Track all rental property maintenance expenses"
```

### Scenario 2: High-Income Professional
```yaml
Taxpayer_Profile:
  employment:
    annual_salary: "‚¬55,000"
    employer_withholding: "‚¬12,000"
    
  professional_income:
    consulting_fees: "‚¬25,000"
    withholding_tax: "‚¬5,000"
    business_expenses: "‚¬8,000"
    
  investments:
    dividend_income: "‚¬3,000" # 5% tax already paid
    bank_interest: "‚¬1,500" # 15% tax already paid
    
  family:
    marital_status: "single" 
    dependent_parents: 1
    
Tax_Calculation:
  total_income: "‚¬84,500"
  professional_net: "‚¬17,000" # ‚¬25,000 - ‚¬8,000 expenses
  taxable_income: "‚¬76,500"
  
  income_tax: "‚¬25,500"
  solidarity_tax: "‚¬3,082"
  tax_credits: "‚¬2,100" # Basic credit only
  
  gross_tax: "‚¬28,582"
  withholding_credits: "‚¬17,000" # Employment + professional + investment
  net_tax_due: "‚¬11,582"
  
Optimization_Strategies:
  - "Maximize business expense deductions"
  - "Consider retirement contributions for tax relief"
  - "Plan timing of professional income for tax efficiency"
  - "Explore dependent parent tax benefits"
```

## Integration with Other Skills

### Email Processor Integration
```bash
# Process tax-related emails automatically
openclaw individual process-tax-emails --year 2025
  # - Employer certificates received via email
  # - Bank statements and tax documents
  # - AADE notifications about individual tax matters

# Client communication for individual tax services
openclaw individual client-communications --auto-respond-greek
  # - Tax return completion confirmations
  # - Required document requests
  # - Payment reminder notifications
```

### AADE Compliance Integration
```bash
# E1 form submission through TAXIS
openclaw individual submit-e1-form --digital-signature --confirm-receipt

# Individual tax audit support
openclaw individual audit-preparation --year 2025 --gather-supporting-docs

# Deadline monitoring for individual tax obligations
openclaw individual monitor-deadlines --include-enfia --include-payments
```

### Banking Integration
```bash
# Import bank statements for income verification
openclaw individual import-bank-data --verify-salary-deposits --track-investments

# Payment processing for tax obligations
openclaw individual process-tax-payments --schedule-installments --confirm-payments
```

## Advanced Features

### Multi-Year Tax Planning
```yaml
Tax_Planning_Strategies:
  income_timing:
    bonus_deferral: "Defer year-end bonuses to optimize tax brackets"
    consulting_income: "Time invoice payments across tax years"
    property_sales: "Plan property transactions during capital gains suspension"
    
  deduction_timing:
    medical_expenses: "Batch medical procedures in single tax year"
    education_payments: "Time tuition payments for maximum deduction"
    charitable_giving: "Optimize donation timing for tax efficiency"
    
  family_planning:
    marriage_timing: "Consider tax implications of marriage date"
    property_ownership: "Optimize property ownership between spouses"
    dependent_status: "Plan for children's changing tax status"
```

### Investment Income Optimization
```yaml
Investment_Tax_Strategies:
  dividend_optimization:
    greek_companies: "5% withholding is final - no additional tax"
    foreign_dividends: "Plan for foreign tax credit utilization"
    timing: "Coordinate dividend payments with other income"
    
  interest_income:
    bank_deposits: "15% withholding vs progressive rates analysis"
    bond_investments: "Choose optimal taxation method"
    foreign_accounts: "Ensure proper reporting and tax credit"
    
  capital_gains_suspension:
    real_estate: "Take advantage of suspension until Dec 2026"
    securities: "Strategic selling during suspension period"
    future_planning: "Prepare for potential reinstatement"
```

## Compliance & Reporting

### AADE Integration
```yaml
Electronic_Submission:
  e1_form_preparation:
    data_validation: "Comprehensive data accuracy checks"
    digital_signature: "Qualified electronic signature integration"
    submission_tracking: "Monitor submission status and confirmation"
    
  supporting_documents:
    electronic_receipts: "Preference for electronic documentation"
    document_scanning: "OCR processing for paper documents"
    cloud_storage: "Secure document archive with retention policies"
    
Tax_Authority_Communication:
  audit_requests: "Immediate alert system for individual audit notifications"
  clarification_requests: "Track and respond to AADE inquiries"
  payment_confirmations: "Verify tax payment processing and receipts"
```

### Record Keeping
```yaml
Documentation_Requirements:
  income_records:
    retention_period: "5 years from tax year end"
    required_documents: ["Employer certificates", "Bank statements", "Investment records"]
    
  deduction_support:
    medical_expenses: "Receipts with patient name and medical purpose"
    education_costs: "Official educational institution receipts"
    charitable_donations: "Certificates from recognized organizations"
    
  property_documentation:
    enfia_calculations: "Property value assessments and tax calculations"
    rental_records: "Income and expense tracking for rental properties"
    maintenance_costs: "Receipts for property improvements and repairs"
```

## Success Metrics

A successful Greek individual tax system should achieve:
- ✅ 100% accurate E1 form preparation and submission
- ✅ Maximum legal deduction identification and application
- ✅ Optimal tax burden through family planning strategies
- ✅ Complete ENFIA integration and optimization
- ✅ Timely submission before June 30 deadline
- ✅ Comprehensive audit trail and documentation
- ✅ Integration with employment and investment income sources
- ✅ Professional Greek tax advice and planning

Remember: This skill focuses on employed individuals as the primary user base, providing comprehensive individual tax management while maintaining the highest standards of Greek tax compliance and optimization.