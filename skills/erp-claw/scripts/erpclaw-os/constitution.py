"""ERPClaw OS Constitution — 21 articles defining module compliance rules.

Each article specifies a rule that modules must follow. Articles 1-8, 10-12,
and 19-21 are checked by static analysis (validate_module_static). Article 9
is checked by running tests in a sandbox (validate_module_runtime). Articles
13-18 are enforced at runtime by database triggers and library APIs.
"""

ARTICLES: list[dict] = [
    {
        "number": 1,
        "name": "Table Prefix Enforcement",
        "description": (
            "Every table created by a non-core module must be prefixed with "
            "the module's namespace. Core ERP uses unprefixed tables."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 2,
        "name": "Money is TEXT",
        "description": (
            "All columns that store financial amounts must use TEXT type. "
            "SQLite REAL uses IEEE 754 floating point which cannot represent "
            "0.10 exactly. TEXT with Python Decimal guarantees precision."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 3,
        "name": "UUID Primary Keys",
        "description": (
            "All primary keys must be TEXT type containing UUID4 values. "
            "Integer auto-increment PKs are not portable to distributed systems."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 4,
        "name": "Foreign Key Integrity",
        "description": (
            "All foreign key references must point to tables that exist "
            "either in the module's own schema or in the core ERP schema."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 5,
        "name": "No Cross-Module Writes",
        "description": (
            "A module may only INSERT, UPDATE, or DELETE rows in tables it owns. "
            "Cross-module writes must go through cross_skill.call_skill_action()."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 6,
        "name": "No Direct GL Writes",
        "description": (
            "No module may directly INSERT into gl_entry or stock_ledger_entry. "
            "All GL posting must go through erpclaw_lib.gl_posting."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 7,
        "name": "Response Format",
        "description": (
            "All actions must return JSON via erpclaw_lib.response.ok() or err(). "
            "Raw print() output breaks the AI layer's ability to parse responses."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 8,
        "name": "Tests Exist",
        "description": (
            "Every action defined in SKILL.md must have at least one "
            "corresponding test in the tests/ directory."
        ),
        "enforcement": "static",
        "severity": "warning",
        "bypass_policy": "tier2",
    },
    {
        "number": 9,
        "name": "Tests Pass",
        "description": (
            "All tests must pass against a fresh database in the sandbox "
            "environment. Tests that pass against stale data are unreliable."
        ),
        "enforcement": "runtime",
        "severity": "critical",
        "bypass_policy": "tier2",
    },
    {
        "number": 10,
        "name": "Security Scan",
        "description": (
            "Generated code must pass a security scan with zero critical "
            "findings. Checks for hardcoded credentials, PII, SQL injection "
            "patterns, and file path traversal."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 11,
        "name": "SKILL.md Format",
        "description": (
            "SKILL.md must have valid YAML frontmatter, must not exceed "
            "300 lines, and must include required fields: name, version, "
            "description."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 12,
        "name": "Naming Convention",
        "description": (
            "Action names must use kebab-case. Non-core module actions "
            "must use a namespace prefix to prevent collisions."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 13,
        "name": "Inventory Conservation",
        "description": (
            "Every stock_ledger_entry must be triggered by a document. "
            "No SLE may exist without a valid voucher_type and voucher_id. "
            "Warehouse balance cannot go negative unless configured."
        ),
        "enforcement": "runtime",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 14,
        "name": "Temporal Integrity",
        "description": (
            "Once a fiscal period is closed, no GL entry or SLE may be "
            "inserted with a posting date within that closed period."
        ),
        "enforcement": "runtime",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 15,
        "name": "Entity Isolation",
        "description": (
            "Every query must be scoped to a specific company_id. "
            "Cross-company data access is prohibited at the query layer."
        ),
        "enforcement": "runtime",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 16,
        "name": "Semantic Locking",
        "description": (
            "Documents in Submitted or Paid status are state-locked. "
            "The only valid transition from Submitted is Cancel (reversal). "
            "No direct UPDATE to financial fields on submitted documents."
        ),
        "enforcement": "runtime",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 17,
        "name": "PII Minimisation",
        "description": (
            "Sensitive fields (SSN, DEA, credit card, bank account) must "
            "be encrypted at rest. Only masked versions for display. "
            "The AI agent never receives raw PII."
        ),
        "enforcement": "runtime",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 18,
        "name": "Account-Type Anchoring",
        "description": (
            "Revenue-generating actions for lease/subscription entities "
            "must use a deferral pattern (Unearned Revenue -> periodic "
            "recognition) unless delivered at point of sale."
        ),
        "enforcement": "runtime",
        "severity": "critical",
        "bypass_policy": "tier3",
    },
    {
        "number": 19,
        "name": "In-Module Modification Scope",
        "description": (
            "When adding features to existing modules, the OS may only ADD "
            "new functions and extend the ACTIONS dict. It may NOT modify "
            "existing functions, change existing SQL queries, or alter "
            "existing test expectations. Enforced by checking "
            ".os_manifest.json after any in-module generation."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
    {
        "number": 20,
        "name": "Research Provenance",
        "description": (
            "Every OS-generated feature must cite the business rule source "
            "(GAAP standard, regulatory reference, or existing ERPClaw "
            "pattern). No code generated from 'common sense' alone. The "
            "improvement_log entry must include a source field."
        ),
        "enforcement": "static",
        "severity": "warning",
        "bypass_policy": "tier2",
    },
    {
        "number": 21,
        "name": "Feature Isolation",
        "description": (
            "A new feature added to an existing module must be testable "
            "in isolation. It must not require modifications to existing "
            "tests to pass. Verified by running only the new test "
            "functions and confirming they pass independently."
        ),
        "enforcement": "static",
        "severity": "critical",
        "bypass_policy": "never",
    },
]


def get_static_articles() -> list[dict]:
    """Return only articles enforced by static analysis (1-8, 10-12, 19-21)."""
    return [a for a in ARTICLES if a["enforcement"] == "static"]


def get_runtime_articles() -> list[dict]:
    """Return only articles enforced at runtime (9, 13-18)."""
    return [a for a in ARTICLES if a["enforcement"] == "runtime"]


def get_article(number: int) -> dict | None:
    """Return a specific article by number."""
    for a in ARTICLES:
        if a["number"] == number:
            return a
    return None
