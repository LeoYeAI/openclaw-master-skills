"""Industry configuration database for ERPClaw OS configure-module.

Defines industry-specific account structures, recommended modules by size tier,
and compliance items for 12 industries. Used by configure_module.py to apply
industry-appropriate configuration to a company.

Account entries follow the core GL schema:
  - root_type: asset | liability | equity | income | expense
  - account_type: matches the CHECK constraint on the account table
  - parent: display name of the parent group account (resolved at configure time)
  - is_group: 0 (posting account) unless explicitly 1

Module names must exist in module_registry.json.
"""

# Map of account_type values to their root_type (for auto-inference)
ACCOUNT_TYPE_ROOT_MAP = {
    "bank": "asset",
    "cash": "asset",
    "receivable": "asset",
    "stock": "asset",
    "fixed_asset": "asset",
    "accumulated_depreciation": "asset",
    "asset_received_not_billed": "asset",
    "stock_received_not_billed": "liability",
    "payable": "liability",
    "payroll_payable": "liability",
    "tax": "liability",
    "equity": "equity",
    "revenue": "income",
    "cost_of_goods_sold": "expense",
    "expense": "expense",
    "depreciation": "expense",
    "stock_adjustment": "expense",
    "rounding": "expense",
    "exchange_gain_loss": "income",
    "temporary": "asset",
}


INDUSTRY_CONFIGS = {
    # ─────────────────────────────────────────────────────────────────────
    # Healthcare: Dental Practice
    # ─────────────────────────────────────────────────────────────────────
    "dental_practice": {
        "display_name": "Dental Practice",
        "accounts": [
            # Income accounts
            {"name": "Patient Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Insurance Reimbursements", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Cosmetic Procedures Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Orthodontics Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expense accounts
            {"name": "Lab Fees", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Dental Supplies", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Dental Equipment Maintenance", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Sterilization Supplies", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Asset accounts
            {"name": "Insurance Claims Receivable", "root_type": "asset", "account_type": "receivable",
             "parent": "Accounts Receivable", "is_group": 0},
            {"name": "Dental Equipment", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
        ],
        "modules": {
            "small": ["healthclaw", "healthclaw-dental"],
            "medium": ["healthclaw", "healthclaw-dental", "erpclaw-approvals", "erpclaw-documents"],
            "large": ["healthclaw", "healthclaw-dental", "erpclaw-approvals", "erpclaw-documents",
                       "erpclaw-compliance", "erpclaw-alerts"],
            "enterprise": ["healthclaw", "healthclaw-dental", "erpclaw-approvals", "erpclaw-documents",
                           "erpclaw-compliance", "erpclaw-alerts", "erpclaw-growth", "erpclaw-integrations"],
        },
        "compliance_items": [
            "HIPAA Privacy Rule Compliance",
            "HIPAA Security Rule Compliance",
            "OSHA Bloodborne Pathogens Standard",
            "State Dental Board License",
            "DEA Registration (if administering controlled substances)",
            "Infection Control Protocols",
            "Radiation Safety Compliance",
            "Patient Records Retention Policy",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Construction: General Contractor
    # ─────────────────────────────────────────────────────────────────────
    "general_contractor": {
        "display_name": "General Contractor",
        "accounts": [
            # Income
            {"name": "Contract Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Change Order Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Retainage Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Subcontractor Costs", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Materials Cost", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Equipment Rental", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Permits and Fees", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Worker Compensation Insurance", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Retainage Receivable", "root_type": "asset", "account_type": "receivable",
             "parent": "Accounts Receivable", "is_group": 0},
            {"name": "Construction Equipment", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
            # Liabilities
            {"name": "Retainage Payable", "root_type": "liability", "account_type": "payable",
             "parent": "Accounts Payable", "is_group": 0},
        ],
        "modules": {
            "small": ["constructclaw"],
            "medium": ["constructclaw", "erpclaw-ops", "erpclaw-documents"],
            "large": ["constructclaw", "erpclaw-ops", "erpclaw-documents",
                       "erpclaw-compliance", "erpclaw-approvals", "erpclaw-fleet"],
            "enterprise": ["constructclaw", "erpclaw-ops", "erpclaw-documents",
                           "erpclaw-compliance", "erpclaw-approvals", "erpclaw-fleet",
                           "erpclaw-growth", "erpclaw-integrations"],
        },
        "compliance_items": [
            "State Contractor License",
            "OSHA Construction Safety Standards",
            "Prevailing Wage Compliance (Davis-Bacon)",
            "Certified Payroll Reports",
            "Lien Waiver Management",
            "Building Permit Tracking",
            "Bonding and Insurance Certificates",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Food Service: Restaurant
    # ─────────────────────────────────────────────────────────────────────
    "restaurant": {
        "display_name": "Restaurant / Food Service",
        "accounts": [
            # Income
            {"name": "Food Sales", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Beverage Sales", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Catering Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Food Cost", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Beverage Cost", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Kitchen Supplies", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Linen and Uniform", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Waste Disposal", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Kitchen Equipment", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
        ],
        "modules": {
            "small": ["foodclaw"],
            "medium": ["foodclaw", "erpclaw-pos", "erpclaw-growth"],
            "large": ["foodclaw", "erpclaw-pos", "erpclaw-growth",
                       "erpclaw-compliance", "erpclaw-alerts"],
            "enterprise": ["foodclaw", "erpclaw-pos", "erpclaw-growth",
                           "erpclaw-compliance", "erpclaw-alerts", "erpclaw-integrations"],
        },
        "compliance_items": [
            "Food Handler Certification",
            "Health Department Permit",
            "Liquor License (if applicable)",
            "Food Safety Plan (HACCP)",
            "Allergen Labeling Compliance",
            "Tip Reporting and Compliance",
            "Fire Safety Inspection",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Legal: Law Firm
    # ─────────────────────────────────────────────────────────────────────
    "law_firm": {
        "display_name": "Law Firm / Legal Practice",
        "accounts": [
            # Income
            {"name": "Legal Fees Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Retainer Income", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Contingency Fee Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Court Filing Fees", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Expert Witness Fees", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Legal Research Services", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "IOLTA Trust Account", "root_type": "asset", "account_type": "bank",
             "parent": "Bank Accounts", "is_group": 0},
            {"name": "Client Trust Receivable", "root_type": "asset", "account_type": "receivable",
             "parent": "Accounts Receivable", "is_group": 0},
            # Liabilities
            {"name": "Client Trust Liability", "root_type": "liability", "account_type": "payable",
             "parent": "Accounts Payable", "is_group": 0},
        ],
        "modules": {
            "small": ["legalclaw"],
            "medium": ["legalclaw", "erpclaw-documents", "erpclaw-approvals"],
            "large": ["legalclaw", "erpclaw-documents", "erpclaw-approvals",
                       "erpclaw-compliance", "erpclaw-esign", "erpclaw-growth"],
            "enterprise": ["legalclaw", "erpclaw-documents", "erpclaw-approvals",
                           "erpclaw-compliance", "erpclaw-esign", "erpclaw-growth",
                           "erpclaw-integrations", "erpclaw-alerts"],
        },
        "compliance_items": [
            "State Bar License and Dues",
            "IOLTA Trust Account Compliance",
            "Client Conflict Check Procedures",
            "Continuing Legal Education (CLE) Requirements",
            "Professional Liability Insurance",
            "Client Data Protection and Confidentiality",
            "Document Retention Policy",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Healthcare: Veterinary Clinic
    # ─────────────────────────────────────────────────────────────────────
    "veterinary_clinic": {
        "display_name": "Veterinary Clinic",
        "accounts": [
            # Income
            {"name": "Veterinary Services Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Boarding Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Pet Pharmacy Sales", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Veterinary Supplies", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Lab Testing Fees", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Pharmaceutical Costs", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Diagnostic Equipment Maintenance", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Diagnostic Equipment", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
        ],
        "modules": {
            "small": ["healthclaw", "healthclaw-vet"],
            "medium": ["healthclaw", "healthclaw-vet", "erpclaw-documents", "erpclaw-approvals"],
            "large": ["healthclaw", "healthclaw-vet", "erpclaw-documents", "erpclaw-approvals",
                       "erpclaw-compliance", "erpclaw-alerts"],
            "enterprise": ["healthclaw", "healthclaw-vet", "erpclaw-documents", "erpclaw-approvals",
                           "erpclaw-compliance", "erpclaw-alerts", "erpclaw-growth", "erpclaw-integrations"],
        },
        "compliance_items": [
            "State Veterinary License",
            "DEA Registration (controlled substances)",
            "OSHA Workplace Safety",
            "Radiation Safety (X-ray equipment)",
            "Controlled Substance Log",
            "Medical Records Retention",
            "Biohazard Waste Disposal Compliance",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Automotive: Auto Repair Shop
    # ─────────────────────────────────────────────────────────────────────
    "auto_repair_shop": {
        "display_name": "Auto Repair Shop",
        "accounts": [
            # Income
            {"name": "Labor Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Parts Sales Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Diagnostic Fees", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Parts Cost", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Shop Supplies", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Waste Oil Disposal", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Tool and Equipment", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Shop Equipment", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
            {"name": "Parts Inventory", "root_type": "asset", "account_type": "stock",
             "parent": "Stock Assets", "is_group": 0},
        ],
        "modules": {
            "small": ["automotiveclaw"],
            "medium": ["automotiveclaw", "erpclaw-growth", "erpclaw-documents"],
            "large": ["automotiveclaw", "erpclaw-growth", "erpclaw-documents",
                       "erpclaw-compliance", "erpclaw-fleet"],
            "enterprise": ["automotiveclaw", "erpclaw-growth", "erpclaw-documents",
                           "erpclaw-compliance", "erpclaw-fleet", "erpclaw-integrations",
                           "erpclaw-alerts"],
        },
        "compliance_items": [
            "State Auto Repair License",
            "EPA Waste Disposal Compliance",
            "Refrigerant Recovery Certification (Section 608)",
            "OSHA Workplace Safety",
            "Consumer Protection Disclosure Requirements",
            "Hazardous Material Storage Compliance",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Property Management
    # ─────────────────────────────────────────────────────────────────────
    "property_management": {
        "display_name": "Property Management",
        "accounts": [
            # Income
            {"name": "Rental Income", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Late Fee Income", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Common Area Maintenance Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Lease Termination Fee", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Property Maintenance", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Property Insurance", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Property Tax Expense", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Property Management Fees", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Rental Properties", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
            {"name": "Security Deposits Held", "root_type": "liability", "account_type": "payable",
             "parent": "Accounts Payable", "is_group": 0},
        ],
        "modules": {
            "small": ["propertyclaw"],
            "medium": ["propertyclaw", "erpclaw-documents", "erpclaw-maintenance"],
            "large": ["propertyclaw", "propertyclaw-commercial", "erpclaw-documents",
                       "erpclaw-maintenance", "erpclaw-compliance", "erpclaw-approvals"],
            "enterprise": ["propertyclaw", "propertyclaw-commercial", "erpclaw-documents",
                           "erpclaw-maintenance", "erpclaw-compliance", "erpclaw-approvals",
                           "erpclaw-growth", "erpclaw-integrations"],
        },
        "compliance_items": [
            "Fair Housing Act Compliance",
            "State Landlord-Tenant Law Compliance",
            "Security Deposit Regulations",
            "Lead Paint Disclosure (pre-1978 buildings)",
            "Building Code Compliance",
            "ADA Accessibility Requirements",
            "Smoke and CO Detector Compliance",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Nonprofit Organization
    # ─────────────────────────────────────────────────────────────────────
    "nonprofit_org": {
        "display_name": "Nonprofit Organization",
        "accounts": [
            # Income (fund-based)
            {"name": "Unrestricted Donations", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Restricted Donations", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Grant Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Membership Dues", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Fundraising Event Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Program Expenses", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Fundraising Expenses", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Grant Disbursements", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Equity (fund balances)
            {"name": "Without Donor Restrictions", "root_type": "equity", "account_type": "equity",
             "parent": "Equity", "is_group": 0},
            {"name": "With Donor Restrictions", "root_type": "equity", "account_type": "equity",
             "parent": "Equity", "is_group": 0},
        ],
        "modules": {
            "small": ["nonprofitclaw"],
            "medium": ["nonprofitclaw", "erpclaw-growth", "erpclaw-documents"],
            "large": ["nonprofitclaw", "erpclaw-growth", "erpclaw-documents",
                       "erpclaw-compliance", "erpclaw-approvals"],
            "enterprise": ["nonprofitclaw", "erpclaw-growth", "erpclaw-documents",
                           "erpclaw-compliance", "erpclaw-approvals", "erpclaw-integrations",
                           "erpclaw-alerts"],
        },
        "compliance_items": [
            "IRS Form 990 Filing",
            "State Charitable Registration",
            "Donor Acknowledgment Letters (IRS requirements)",
            "Restricted Fund Tracking",
            "Grant Reporting Compliance",
            "Board Governance Policies",
            "Conflict of Interest Policy",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Retail Store
    # ─────────────────────────────────────────────────────────────────────
    "retail_store": {
        "display_name": "Retail Store",
        "accounts": [
            # Income
            {"name": "Merchandise Sales", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Gift Card Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Returns and Allowances", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Merchandise Cost", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Shrinkage and Loss", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Packaging and Bags", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Store Fixtures Depreciation", "root_type": "expense", "account_type": "depreciation",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Merchandise Inventory", "root_type": "asset", "account_type": "stock",
             "parent": "Stock Assets", "is_group": 0},
            {"name": "Store Fixtures", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
            # Liabilities
            {"name": "Gift Card Liability", "root_type": "liability", "account_type": "payable",
             "parent": "Accounts Payable", "is_group": 0},
        ],
        "modules": {
            "small": ["retailclaw"],
            "medium": ["retailclaw", "erpclaw-pos", "erpclaw-growth"],
            "large": ["retailclaw", "erpclaw-pos", "erpclaw-growth",
                       "erpclaw-logistics", "erpclaw-alerts"],
            "enterprise": ["retailclaw", "erpclaw-pos", "erpclaw-growth",
                           "erpclaw-logistics", "erpclaw-alerts", "erpclaw-integrations",
                           "erpclaw-compliance"],
        },
        "compliance_items": [
            "Sales Tax Collection and Remittance",
            "PCI DSS Compliance (credit card processing)",
            "ADA Accessibility Compliance",
            "Product Safety and Recall Procedures",
            "Gift Card Regulations (state-specific)",
            "Employee Scheduling Laws",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Manufacturing
    # ─────────────────────────────────────────────────────────────────────
    "manufacturing": {
        "display_name": "Manufacturing",
        "accounts": [
            # Income
            {"name": "Finished Goods Sales", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Scrap Sales", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Raw Materials Cost", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Direct Labor", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Manufacturing Overhead", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Quality Control Costs", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Factory Equipment Depreciation", "root_type": "expense", "account_type": "depreciation",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Tooling and Dies", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Raw Materials Inventory", "root_type": "asset", "account_type": "stock",
             "parent": "Stock Assets", "is_group": 0},
            {"name": "Work In Progress", "root_type": "asset", "account_type": "stock",
             "parent": "Stock Assets", "is_group": 0},
            {"name": "Finished Goods Inventory", "root_type": "asset", "account_type": "stock",
             "parent": "Stock Assets", "is_group": 0},
            {"name": "Factory Equipment", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
        ],
        "modules": {
            "small": ["erpclaw-ops"],
            "medium": ["erpclaw-ops", "erpclaw-planning", "erpclaw-growth"],
            "large": ["erpclaw-ops", "erpclaw-planning", "erpclaw-growth",
                       "erpclaw-compliance", "erpclaw-maintenance", "erpclaw-logistics"],
            "enterprise": ["erpclaw-ops", "erpclaw-planning", "erpclaw-growth",
                           "erpclaw-compliance", "erpclaw-maintenance", "erpclaw-logistics",
                           "erpclaw-integrations", "erpclaw-alerts"],
        },
        "compliance_items": [
            "OSHA Workplace Safety Standards",
            "EPA Environmental Compliance",
            "ISO 9001 Quality Management",
            "FDA Compliance (if applicable)",
            "Hazardous Materials Handling",
            "Product Traceability Requirements",
            "Workers Compensation Insurance",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Agriculture / Farming
    # ─────────────────────────────────────────────────────────────────────
    "agriculture": {
        "display_name": "Agriculture / Farming",
        "accounts": [
            # Income
            {"name": "Crop Sales", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Livestock Sales", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Government Subsidies", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Seed and Planting Costs", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Fertilizer and Chemicals", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Feed and Animal Care", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Irrigation Costs", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Crop Insurance", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Farm Equipment", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
            {"name": "Growing Crops", "root_type": "asset", "account_type": "stock",
             "parent": "Stock Assets", "is_group": 0},
            {"name": "Livestock", "root_type": "asset", "account_type": "stock",
             "parent": "Stock Assets", "is_group": 0},
        ],
        "modules": {
            "small": ["agricultureclaw"],
            "medium": ["agricultureclaw", "erpclaw-fleet", "erpclaw-growth"],
            "large": ["agricultureclaw", "erpclaw-fleet", "erpclaw-growth",
                       "erpclaw-compliance", "erpclaw-logistics"],
            "enterprise": ["agricultureclaw", "erpclaw-fleet", "erpclaw-growth",
                           "erpclaw-compliance", "erpclaw-logistics", "erpclaw-integrations",
                           "erpclaw-alerts"],
        },
        "compliance_items": [
            "USDA Organic Certification (if applicable)",
            "EPA Pesticide Regulations",
            "Farm Safety Standards (OSHA)",
            "Water Rights and Usage Permits",
            "Crop Insurance Compliance",
            "Agricultural Labor Standards",
            "Food Safety Modernization Act (FSMA)",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # Hospitality: Hotel
    # ─────────────────────────────────────────────────────────────────────
    "hotel": {
        "display_name": "Hotel / Hospitality",
        "accounts": [
            # Income
            {"name": "Room Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Food and Beverage Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Event and Conference Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            {"name": "Parking Revenue", "root_type": "income", "account_type": "revenue",
             "parent": "Direct Income", "is_group": 0},
            # Expenses
            {"name": "Housekeeping Supplies", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Laundry and Linen", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Guest Amenities", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "OTA Commission Expense", "root_type": "expense", "account_type": "expense",
             "parent": "Direct Expenses", "is_group": 0},
            {"name": "Food and Beverage Cost", "root_type": "expense", "account_type": "cost_of_goods_sold",
             "parent": "Direct Expenses", "is_group": 0},
            # Assets
            {"name": "Hotel Furnishings", "root_type": "asset", "account_type": "fixed_asset",
             "parent": "Fixed Assets", "is_group": 0},
        ],
        "modules": {
            "small": ["hospitalityclaw"],
            "medium": ["hospitalityclaw", "erpclaw-pos", "erpclaw-growth"],
            "large": ["hospitalityclaw", "erpclaw-pos", "erpclaw-growth",
                       "erpclaw-maintenance", "erpclaw-compliance"],
            "enterprise": ["hospitalityclaw", "erpclaw-pos", "erpclaw-growth",
                           "erpclaw-maintenance", "erpclaw-compliance", "erpclaw-integrations",
                           "erpclaw-alerts"],
        },
        "compliance_items": [
            "Hospitality License",
            "Health and Safety Inspection",
            "Fire Safety Compliance",
            "ADA Accessibility Compliance",
            "Liquor License (if applicable)",
            "Food Service Permit",
            "Occupancy Tax Collection and Remittance",
        ],
    },
}


def list_industries() -> list[dict]:
    """Return a list of all available industry configs with summary info."""
    results = []
    for key, config in sorted(INDUSTRY_CONFIGS.items()):
        results.append({
            "industry": key,
            "display_name": config["display_name"],
            "account_count": len(config["accounts"]),
            "size_tiers": sorted(config["modules"].keys()),
            "compliance_item_count": len(config["compliance_items"]),
        })
    return results
