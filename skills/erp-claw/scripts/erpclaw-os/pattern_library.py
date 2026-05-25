"""ERPClaw OS Pattern Library -- reusable module patterns extracted from existing modules.

Each pattern defines a common business entity type with:
- Standard schema fields (column definitions)
- Standard actions (add, update, get, list, etc.)
- Source modules that demonstrate the pattern
- GL requirements (direct, delegated, or none)

Used by generate_module.py to map business entities to code templates.
"""

PATTERNS = {
    "crud_entity": {
        "name": "CRUD Entity",
        "description": "Basic entity with add, update, get, list actions",
        "source_modules": ["legalclaw", "healthclaw-vet"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "name TEXT NOT NULL",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "status TEXT DEFAULT 'active'",
            "notes TEXT",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["add", "update", "get", "list"],
        "requires_gl": False,
    },
    "appointment_booking": {
        "name": "Appointment/Booking",
        "description": "Scheduled event with date, time, status lifecycle",
        "source_modules": ["healthclaw", "healthclaw-vet"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "date TEXT NOT NULL",
            "start_time TEXT",
            "end_time TEXT",
            "status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled','confirmed','in_progress','completed','cancelled'))",
            "notes TEXT",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["add", "update", "list"],
        "requires_gl": False,
    },
    "service_record": {
        "name": "Service Record",
        "description": "Record of a service performed, linked to an entity and appointment",
        "source_modules": ["healthclaw-vet", "automotiveclaw"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "service_type TEXT NOT NULL",
            "description TEXT",
            "amount TEXT DEFAULT '0'",
            "notes TEXT",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["add", "list"],
        "requires_gl": False,
    },
    "invoice_delegation": {
        "name": "Invoice Delegation",
        "description": "Create invoice via cross_skill (never direct GL)",
        "source_modules": ["groomingclaw", "tattooclaw", "storageclaw"],
        "schema_fields": [],
        "actions": ["create-invoice"],
        "requires_gl": True,  # but delegated, not direct
    },
    "compliance_tracking": {
        "name": "Compliance/Licensing",
        "description": "Track certifications, inspections, compliance records",
        "source_modules": ["legalclaw", "tattooclaw", "constructclaw"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "record_type TEXT NOT NULL",
            "status TEXT DEFAULT 'active'",
            "expiry_date TEXT",
            "notes TEXT",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["add", "list", "get"],
        "requires_gl": False,
    },
    "prepaid_package": {
        "name": "Prepaid Package/Credit",
        "description": "Prepaid sessions or credits with usage tracking",
        "source_modules": ["groomingclaw", "erpclaw-billing"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "total_sessions INTEGER NOT NULL",
            "used_sessions INTEGER NOT NULL DEFAULT 0",
            "amount TEXT DEFAULT '0'",
            "status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','exhausted','expired','cancelled'))",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["add", "use-session", "get-balance"],
        "requires_gl": False,
    },
    "recurring_billing": {
        "name": "Recurring Monthly Billing",
        "description": "Monthly billing with late fees and delinquency",
        "source_modules": ["storageclaw", "propertyclaw"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "amount TEXT NOT NULL DEFAULT '0'",
            "billing_date TEXT",
            "status TEXT NOT NULL DEFAULT 'pending'",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["generate-invoices", "apply-late-fees"],
        "requires_gl": True,
    },
    "document_close": {
        "name": "Document Close",
        "description": "Close a partially-fulfilled document without cancelling. Closed preserves history but stops new activity (no further child docs).",
        "source_modules": ["erpclaw-selling", "erpclaw-buying"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "document_type TEXT NOT NULL",
            "document_id TEXT NOT NULL",
            "close_date TEXT NOT NULL",
            "close_reason TEXT",
            "closed_by TEXT",
            "status TEXT NOT NULL DEFAULT 'closed' CHECK(status IN ('closed','reopened'))",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["close-document", "reopen-document"],
        "requires_gl": False,
        "related_patterns": [],
    },
    "document_amendment": {
        "name": "Document Amendment",
        "description": "Cancel + recreate + link with amendment chain. Amendment preserves audit trail via amended_from chain.",
        "source_modules": ["erpclaw-selling"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "original_id TEXT NOT NULL",
            "amendment_number INTEGER NOT NULL DEFAULT 1",
            "amendment_reason TEXT NOT NULL",
            "status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','submitted','cancelled'))",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["amend-document", "get-amendment-history"],
        "requires_gl": False,
        "related_patterns": [],
    },
    "recurring_template": {
        "name": "Recurring Template",
        "description": "Recurring document generation from template. Defines frequency and schedule for auto-generating documents (invoices, bills, etc.).",
        "source_modules": ["erpclaw-billing", "storageclaw"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "template_name TEXT NOT NULL",
            "frequency TEXT NOT NULL DEFAULT 'monthly' CHECK(frequency IN ('daily','weekly','monthly','quarterly','annually'))",
            "next_date TEXT NOT NULL",
            "end_date TEXT",
            "last_generated TEXT",
            "auto_submit INTEGER NOT NULL DEFAULT 0",
            "status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','paused','expired','cancelled'))",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["add-template", "generate-from-template", "list-templates"],
        "requires_gl": True,  # delegated — generated docs may post GL
        "related_patterns": ["recurring_billing"],
    },
    "blanket_agreement": {
        "name": "Blanket Agreement",
        "description": "Long-term agreement with child orders drawing down qty. Child orders reduce remaining qty and cannot exceed agreement total.",
        "source_modules": [],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "party_id TEXT NOT NULL",
            "start_date TEXT NOT NULL",
            "end_date TEXT NOT NULL",
            "total_qty TEXT NOT NULL DEFAULT '0'",
            "fulfilled_qty TEXT NOT NULL DEFAULT '0'",
            "status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','fulfilled','expired','cancelled'))",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["add-agreement", "fulfill-against-agreement", "get-agreement-balance"],
        "requires_gl": False,
        "related_patterns": [],
    },
    "three_way_match": {
        "name": "Three-Way Match",
        "description": "PO-GRN-Invoice matching with configurable tolerance. Validates invoice_qty <= received_qty <= ordered_qty within tolerance.",
        "source_modules": ["erpclaw-buying"],
        "schema_fields": [
            "id TEXT PRIMARY KEY",
            "company_id TEXT NOT NULL REFERENCES company(id)",
            "po_id TEXT NOT NULL",
            "receipt_id TEXT",
            "invoice_id TEXT",
            "match_status TEXT NOT NULL DEFAULT 'pending' CHECK(match_status IN ('pending','matched','mismatched','overridden'))",
            "tolerance_pct TEXT NOT NULL DEFAULT '0'",
            "match_policy TEXT NOT NULL DEFAULT 'strict' CHECK(match_policy IN ('strict','tolerant','disabled'))",
            "created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "updated_at TEXT NOT NULL DEFAULT (datetime('now'))",
        ],
        "actions": ["run-match", "list-unmatched", "override-match"],
        "requires_gl": False,
        "related_patterns": [],
    },
}


# Mapping of common business terms to patterns — used for entity extraction
TERM_TO_PATTERN = {
    # CRUD entity terms
    "client": "crud_entity",
    "customer": "crud_entity",
    "member": "crud_entity",
    "pet": "crud_entity",
    "vehicle": "crud_entity",
    "property": "crud_entity",
    "item": "crud_entity",
    "product": "crud_entity",
    "employee": "crud_entity",
    "staff": "crud_entity",
    "contact": "crud_entity",
    "vendor": "crud_entity",
    "supplier": "crud_entity",
    "unit": "crud_entity",
    "location": "crud_entity",
    "category": "crud_entity",
    "type": "crud_entity",
    # Appointment/booking terms
    "appointment": "appointment_booking",
    "booking": "appointment_booking",
    "reservation": "appointment_booking",
    "session": "appointment_booking",
    "visit": "appointment_booking",
    "schedule": "appointment_booking",
    # Service record terms
    "service": "service_record",
    "treatment": "service_record",
    "inspection": "service_record",
    "maintenance": "service_record",
    "repair": "service_record",
    "job": "service_record",
    # Compliance terms
    "license": "compliance_tracking",
    "certification": "compliance_tracking",
    "permit": "compliance_tracking",
    "compliance": "compliance_tracking",
    "audit": "compliance_tracking",
    # Prepaid terms
    "package": "prepaid_package",
    "credit": "prepaid_package",
    "subscription": "prepaid_package",
    "plan": "prepaid_package",
    "membership": "prepaid_package",
    # Invoice delegation
    "invoice": "invoice_delegation",
    "billing": "invoice_delegation",
    # Document close terms
    "close": "document_close",
    "closed": "document_close",
    "stop": "document_close",
    # Document amendment terms
    "amend": "document_amendment",
    "amendment": "document_amendment",
    "revise": "document_amendment",
    # Recurring template terms
    "recurring": "recurring_template",
    "repeat": "recurring_template",
    "template": "recurring_template",
    # Blanket agreement terms
    "blanket": "blanket_agreement",
    "framework": "blanket_agreement",
    "long-term": "blanket_agreement",
    # Three-way match terms
    "match": "three_way_match",
    "matching": "three_way_match",
    "3-way": "three_way_match",
    "three-way": "three_way_match",
}


def get_pattern(name: str) -> dict | None:
    """Return a specific pattern by name, or None if not found."""
    return PATTERNS.get(name)


def list_patterns() -> list[dict]:
    """Return all patterns as a list with keys included."""
    result = []
    for key, pat in PATTERNS.items():
        entry = {"key": key}
        entry.update(pat)
        result.append(entry)
    return result


def suggest_pattern(term: str) -> str | None:
    """Suggest a pattern key for a business term."""
    return TERM_TO_PATTERN.get(term.lower())
