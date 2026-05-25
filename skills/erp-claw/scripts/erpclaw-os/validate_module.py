"""ERPClaw OS Module Validator — static and runtime validation against the Constitution.

Implements validate_module_static() for Articles 1-8, 10-12, 19-21 and
validate_module_runtime() for Article 9 (tests pass in sandbox).

Uses regex for SQL/DDL parsing and Python ast for code analysis.
Does NOT execute any module code during static validation.
"""
import ast
import os
import re
import subprocess
import sys
import yaml


# ---------------------------------------------------------------------------
# Table prefix mapping: module directory name -> expected table prefix(es)
# Core ERP modules (under src/erpclaw/) use unprefixed tables.
# ---------------------------------------------------------------------------

# Known prefix overrides for modules whose directory name doesn't map directly
_PREFIX_OVERRIDES: dict[str, list[str]] = {
    # healthclaw sub-modules share healthclaw_ prefix
    "healthclaw": ["healthclaw_", "health_"],
    "healthclaw-dental": ["healthclaw_", "health_"],
    "healthclaw-vet": ["healthclaw_", "health_"],
    "healthclaw-mental": ["healthclaw_", "health_"],
    "healthclaw-homehealth": ["healthclaw_", "health_"],
    # educlaw modules
    "educlaw": ["educlaw_", "educ_"],
    "educlaw-finaid": ["educlaw_", "educ_", "finaid_"],
    "educlaw-k12": ["educlaw_", "educ_", "educlaw_k12_"],
    "educlaw-scheduling": ["educlaw_", "educ_"],
    "educlaw-lms": ["educlaw_", "educ_"],
    "educlaw-statereport": ["educlaw_", "educ_", "sr_"],
    "educlaw-highered": ["educlaw_", "educ_", "highered_"],
    # propertyclaw modules
    "propertyclaw": ["propertyclaw_", "prop_"],
    "propertyclaw-commercial": ["propertyclaw_", "prop_", "commercial_"],
    # standalone verticals
    "retailclaw": ["retailclaw_", "retail_"],
    "constructclaw": ["constructclaw_", "construct_"],
    "agricultureclaw": ["agricultureclaw_", "agri_"],
    "automotiveclaw": ["automotiveclaw_", "auto_"],
    "foodclaw": ["foodclaw_", "food_"],
    "hospitalityclaw": ["hospitalityclaw_", "hotel_"],
    "legalclaw": ["legalclaw_", "legal_"],
    "nonprofitclaw": ["nonprofitclaw_", "nonprofit_"],
    # erpclaw-addons
    "erpclaw-growth": ["erpclaw_", "crm_", "crmadv_", "anomaly", "scenario", "correlation",
                        "categorization_rule", "business_rule", "pending_decision",
                        "usage_event", "audit_conversation", "conversation_context",
                        "relationship_score", "elimination_rule", "elimination_entry"],
    "erpclaw-ops": ["erpclaw_", "mfg_", "project_", "asset_", "quality_", "support_",
                     "shop_floor_", "tool", "engineering_change_", "process_recipe", "recipe_ingredient"],
    "erpclaw-integrations": ["erpclaw_", "integration_", "connv2_", "plaid_", "stripe_", "s3_"],
    "erpclaw-integrations-stripe": ["stripe_"],
    "erpclaw-alerts": ["erpclaw_", "alert_", "notification_"],
    "erpclaw-approvals": ["erpclaw_", "approval_"],
    "erpclaw-compliance": ["erpclaw_", "compliance_", "audit_", "risk_", "control_", "policy"],
    "erpclaw-documents": ["erpclaw_", "document_", "document"],
    "erpclaw-esign": ["erpclaw_", "esign_"],
    "erpclaw-fleet": ["erpclaw_", "fleet_"],
    "erpclaw-loans": ["erpclaw_", "loan_", "loan"],
    "erpclaw-logistics": ["erpclaw_", "logistics_"],
    "erpclaw-maintenance": ["erpclaw_", "maintenance_", "equipment", "downtime_"],
    "erpclaw-planning": ["erpclaw_", "planning_", "forecast"],
    "erpclaw-pos": ["erpclaw_", "pos_"],
    "erpclaw-selfservice": ["erpclaw_", "selfservice_"],
    "erpclaw-treasury": ["erpclaw_", "treasury_", "bank_account_", "cash_", "investment",
                          "inter_company_"],
    # regional modules
    "erpclaw-region-ca": ["erpclaw_", "canada_"],
    "erpclaw-region-eu": ["erpclaw_", "eu_"],
    "erpclaw-region-in": ["erpclaw_", "india_"],
    "erpclaw-region-uk": ["erpclaw_", "uk_"],
    # AI-generated modules from plan examples
    "groomingclaw": ["groomingclaw_", "groom_"],
    "tattooclaw": ["tattooclaw_", "tattoo_"],
    "storageclaw": ["storageclaw_", "storage_"],
}

# Money-related column name patterns
_MONEY_PATTERNS = re.compile(
    r"(amount|rate|price|cost|total|balance|paid|fee|charge|debit|credit|"
    r"tax|discount|budget|salary|wage|revenue|expense|mileage|"
    r"liability|receivable|payable|net_pay|gross_pay|"
    r"overtime_pay|bonus|commission|allowance|deduction|"
    r"premium|surcharge|markup|margin|profit|loss|"
    r"billing_rate|hourly_rate|flat_fee|retainer_amount|"
    r"billed_amount|collected_amount|trust_balance|"
    r"time_amount|expense_amount|paid_amount|"
    r"current_balance|opening_balance|closing_balance|"
    r"base_amount|tax_amount|net_amount|grand_total|"
    r"outstanding|overpayment|underpayment|write_off|"
    r"cle_hours_required|cle_hours_completed|hours|"
    r"allocated_amount|unallocated_amount)",
    re.IGNORECASE,
)

# Columns that match money patterns but are NOT money fields
_MONEY_EXCEPTIONS = {
    "hours",  # time entries (can be TEXT for decimal precision, but not money)
    "cle_hours_required",
    "cle_hours_completed",
    "reminder_days",
    "credit_days",
    "credit_limit",
    # Counts and quantities (INTEGER is correct)
    "total_units",
    "total_sessions",
    "used_sessions",
    "total_stays",
    "total_sections",
    "total_periods_per_cycle",
    "total_minutes_delivered",
    # Boolean/flag columns that happen to match patterns
    "tax_deductible",
    "allows_extra_credit",
    "allow_discount",
    "prorate_first_month",
    # Medical/scientific values
    "heart_rate",
    "respiratory_rate",
    "turnaround_hours",
    # Time-frequency columns
    "sync_frequency_hours",
    "max_teaching_load_hours",
    # Year columns
    "tax_year",
    # Education: counts, credits, enrollment numbers
    "nslds_overpayment_flag",
    "credits_attempted",
    "credits_required",
    "credits",
    "total_credits",
    "total_positions",
    "total_students",
    "total_enrollment",
    "total_sped",
    "total_el",
    "total_economically_disadvantaged",
    "total_homeless",
}

# Security scan patterns
_SECURITY_PATTERNS = [
    # Hardcoded passwords/secrets
    (re.compile(r'''(?:password|secret|token|api_key|apikey)\s*=\s*['"][^'"]{8,}['"]''', re.IGNORECASE),
     "Potential hardcoded credential"),
    # Real IP addresses (not localhost/test)
    (re.compile(r'\b(?!127\.0\.0\.1|0\.0\.0\.0|10\.\d|172\.(?:1[6-9]|2\d|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
     "Potential hardcoded IP address"),
    # SSN patterns
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
     "Potential SSN pattern"),
    # SQL injection via string formatting
    (re.compile(r'''f['"]\s*(?:SELECT|INSERT|UPDATE|DELETE)\b.*\{''', re.IGNORECASE),
     "Potential SQL injection via f-string"),
]


# ---------------------------------------------------------------------------
# DDL Parsing Helpers
# ---------------------------------------------------------------------------

_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)\s*\(",
    re.IGNORECASE | re.MULTILINE,
)

_FK_REFERENCE_RE = re.compile(
    r"REFERENCES\s+(\w+)\s*\(",
    re.IGNORECASE,
)


def _extract_tables_from_ddl(ddl_text: str) -> list[str]:
    """Extract table names from CREATE TABLE IF NOT EXISTS statements."""
    return _CREATE_TABLE_RE.findall(ddl_text)


def _extract_fk_references(ddl_text: str) -> list[str]:
    """Extract referenced table names from FOREIGN KEY / REFERENCES clauses."""
    return _FK_REFERENCE_RE.findall(ddl_text)


def _parse_columns(ddl_text: str) -> list[dict]:
    """Parse column definitions from CREATE TABLE statements.

    Returns list of dicts with keys: table, name, type, is_pk.
    """
    columns = []
    for match in re.finditer(
        r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)\s*\((.*?)\)\s*;",
        ddl_text,
        re.IGNORECASE | re.DOTALL,
    ):
        table_name = match.group(1)
        body = match.group(2)

        # Split into lines, handle each column definition
        for line in body.split("\n"):
            line = line.strip().rstrip(",")
            if not line:
                continue

            # Skip constraints, indexes, comments
            upper = line.upper().lstrip()
            if any(upper.startswith(kw) for kw in (
                "CREATE", "FOREIGN", "UNIQUE", "CHECK", "PRIMARY KEY(",
                "CONSTRAINT", "--", "/*", ")", "INDEX",
            )):
                continue

            # Parse: column_name TYPE [constraints...]
            col_match = re.match(r"(\w+)\s+(TEXT|INTEGER|REAL|FLOAT|NUMERIC|BLOB)\b", line, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1)
                col_type = col_match.group(2).upper()
                is_pk = "PRIMARY KEY" in line.upper()
                columns.append({
                    "table": table_name,
                    "name": col_name,
                    "type": col_type,
                    "is_pk": is_pk,
                })

    return columns


def _read_init_db(module_path: str) -> str | None:
    """Read init_db.py content from a module path. Returns None if not found."""
    init_db_path = os.path.join(module_path, "init_db.py")
    if os.path.isfile(init_db_path):
        with open(init_db_path, "r") as f:
            return f.read()
    return None


def _read_skill_md(module_path: str) -> str | None:
    """Read SKILL.md content from a module path. Returns None if not found."""
    skill_md_path = os.path.join(module_path, "SKILL.md")
    if os.path.isfile(skill_md_path):
        with open(skill_md_path, "r") as f:
            return f.read()
    return None


def _find_scripts_dir(module_path: str) -> str | None:
    """Find the scripts/ directory for a module."""
    scripts_dir = os.path.join(module_path, "scripts")
    if os.path.isdir(scripts_dir):
        return scripts_dir
    return None


def _find_tests_dir(module_path: str) -> str | None:
    """Find the tests/ directory for a module (may be in scripts/tests/)."""
    # Check scripts/tests/ first (common pattern)
    scripts_tests = os.path.join(module_path, "scripts", "tests")
    if os.path.isdir(scripts_tests):
        return scripts_tests
    # Check top-level tests/
    tests_dir = os.path.join(module_path, "tests")
    if os.path.isdir(tests_dir):
        return tests_dir
    return None


def _get_all_py_files(directory: str) -> list[str]:
    """Recursively get all .py files in a directory."""
    py_files = []
    for root, _dirs, files in os.walk(directory):
        # Skip __pycache__ and .git
        if "__pycache__" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files


def _derive_module_name(module_path: str) -> str:
    """Derive the module name from the directory path.

    Examples:
        /path/to/src/legalclaw -> legalclaw
        /path/to/src/healthclaw/healthclaw-vet -> healthclaw-vet
        /path/to/src/erpclaw-addons/erpclaw-loans -> erpclaw-loans
    """
    return os.path.basename(os.path.normpath(module_path))


def _is_core_module(module_path: str) -> bool:
    """Check if the module is the core ERP (erpclaw-setup, erpclaw-gl, etc.).

    Core modules are under src/erpclaw/scripts/erpclaw-* and use unprefixed tables.
    """
    norm = os.path.normpath(module_path)
    # Check if under erpclaw/scripts/ (core domain subdirectory)
    parts = norm.split(os.sep)
    for i, p in enumerate(parts):
        if p == "erpclaw" and i + 1 < len(parts) and parts[i + 1] == "scripts":
            return True
    # Top-level erpclaw directory itself
    if parts[-1] == "erpclaw" and (len(parts) < 2 or parts[-2] != "healthclaw"):
        # Check if it has the core SKILL.md
        skill_path = os.path.join(module_path, "SKILL.md")
        if os.path.isfile(skill_path):
            with open(skill_path, "r") as f:
                content = f.read(200)
                if "name: erpclaw" in content:
                    return True
    return False


def _get_expected_prefixes(module_name: str) -> list[str]:
    """Get expected table prefixes for a module.

    Returns a list of valid prefixes. A table name must start with
    at least one of these prefixes to pass Article 1.
    """
    if module_name in _PREFIX_OVERRIDES:
        return _PREFIX_OVERRIDES[module_name]

    # Default: derive from module name
    # e.g., "groomingclaw" -> ["groomingclaw_", "groom_"]
    prefixes = [f"{module_name}_"]

    # Also accept shortened version (remove "claw" suffix)
    if module_name.endswith("claw"):
        short = module_name[:-4]  # Remove "claw"
        prefixes.append(f"{short}_")

    return prefixes


def _extract_action_names_from_skill_md(skill_md_content: str) -> list[str]:
    """Extract action names from SKILL.md content.

    Looks for action names in markdown tables (backtick-quoted) and
    code blocks (--action references).
    """
    actions = set()

    # Pattern 1: backtick-quoted action names in tables: `action-name`
    for match in re.finditer(r"`([a-z][a-z0-9-]*(?:-[a-z0-9]+)*)`", skill_md_content):
        name = match.group(1)
        # Filter out non-action strings
        if any(name.startswith(p) for p in (
            "add-", "update-", "get-", "list-", "delete-", "submit-", "cancel-",
            "create-", "import-", "generate-", "run-", "check-", "approve-",
            "reject-", "close-", "reopen-", "seed-", "setup-", "record-",
            "calculate-", "modify-", "satisfy-", "classify-", "allocate-",
            "reconcile-", "reverse-", "freeze-", "unfreeze-", "duplicate-",
            "amend-", "convert-", "process-", "mark-", "bulk-", "assign-",
            "revoke-", "link-", "unlink-", "revalue-",
        )):
            actions.add(name)
        # Also match known standalone action names
        elif name in ("status", "tutorial", "onboarding-step"):
            actions.add(name)
        # Namespace-prefixed actions (e.g., legal-add-client)
        elif re.match(r"^[a-z]+-(?:add|update|get|list|delete|submit|cancel|create|generate|run|check|record)-", name):
            actions.add(name)

    # Pattern 2: --action references in code blocks
    for match in re.finditer(r"--action\s+(\S+)", skill_md_content):
        action = match.group(1).strip("`'\"")
        if re.match(r"^[a-z][a-z0-9-]*$", action) and action != "<action>":
            actions.add(action)

    return sorted(actions)


def _extract_test_function_names(tests_dir: str) -> list[str]:
    """Extract test function names from test files."""
    test_funcs = []
    if not tests_dir or not os.path.isdir(tests_dir):
        return test_funcs

    for f in os.listdir(tests_dir):
        if f.startswith("test_") and f.endswith(".py"):
            filepath = os.path.join(tests_dir, f)
            with open(filepath, "r") as fh:
                content = fh.read()
            for match in re.finditer(r"def\s+(test_\w+)", content):
                test_funcs.append(match.group(1))

    return test_funcs


def _parse_skill_md_frontmatter(skill_md_content: str) -> dict | None:
    """Parse YAML frontmatter from SKILL.md. Returns None if invalid."""
    if not skill_md_content.startswith("---"):
        return None

    end_idx = skill_md_content.find("---", 3)
    if end_idx == -1:
        return None

    frontmatter_text = skill_md_content[3:end_idx].strip()
    try:
        return yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return None


# ---------------------------------------------------------------------------
# AST-Based Code Analysis
# ---------------------------------------------------------------------------

def _extract_sql_strings_from_ast(filepath: str) -> list[dict]:
    """Parse a Python file with ast and extract SQL string arguments to execute() calls.

    Returns list of dicts: {"sql": str, "line": int, "file": str}
    """
    results = []
    try:
        with open(filepath, "r") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, UnicodeDecodeError):
        return results

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Look for .execute() or .executescript() or .executemany() calls
            if isinstance(node.func, ast.Attribute) and node.func.attr in (
                "execute", "executescript", "executemany",
            ):
                if node.args:
                    sql_str = _extract_string_value(node.args[0])
                    if sql_str:
                        results.append({
                            "sql": sql_str,
                            "line": node.lineno,
                            "file": filepath,
                        })

    return results


def _extract_string_value(node: ast.AST) -> str | None:
    """Extract a string value from an AST node (handles str, f-string, concatenation)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    elif isinstance(node, ast.JoinedStr):
        # f-string — reconstruct a partial representation
        parts = []
        for val in node.values:
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                parts.append(val.value)
            else:
                parts.append("{...}")  # Placeholder for expressions
        return "".join(parts)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        # String concatenation
        left = _extract_string_value(node.left)
        right = _extract_string_value(node.right)
        if left and right:
            return left + right
    return None


def _check_imports(filepath: str, import_name: str, from_module: str = None) -> bool:
    """Check if a file imports a specific name, optionally from a specific module."""
    try:
        with open(filepath, "r") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, UnicodeDecodeError):
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if from_module is None or (node.module and from_module in node.module):
                for alias in node.names:
                    if alias.name == import_name:
                        return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == import_name:
                    return True
    return False


# ---------------------------------------------------------------------------
# Table Ownership Registry
# ---------------------------------------------------------------------------

def build_table_ownership_registry(src_root: str) -> dict[str, str]:
    """Scan all init_db.py files under src_root and return {table_name: module_name}.

    Also scans init_schema.py for core ERP tables.
    """
    registry: dict[str, str] = {}

    # 1. Scan core init_schema.py
    init_schema_path = os.path.join(
        src_root, "erpclaw", "scripts", "erpclaw-setup", "init_schema.py"
    )
    if os.path.isfile(init_schema_path):
        with open(init_schema_path, "r") as f:
            content = f.read()
        tables = _extract_tables_from_ddl(content)
        for t in tables:
            registry[t] = "erpclaw"

    # 2. Scan all init_db.py files
    for root, _dirs, files in os.walk(src_root):
        if "__pycache__" in root or ".git" in root:
            continue
        for fname in files:
            if fname == "init_db.py":
                filepath = os.path.join(root, fname)
                # Skip the core init_schema.py (already handled)
                if "erpclaw-setup" in filepath:
                    continue
                with open(filepath, "r") as f:
                    content = f.read()

                # Derive module name from directory
                module_name = _derive_module_name(root)
                tables = _extract_tables_from_ddl(content)
                for t in tables:
                    registry[t] = module_name

    return registry


def _get_core_tables(src_root: str) -> set[str]:
    """Get the set of all tables defined in the core ERP init_schema.py."""
    init_schema_path = os.path.join(
        src_root, "erpclaw", "scripts", "erpclaw-setup", "init_schema.py"
    )
    if not os.path.isfile(init_schema_path):
        return set()
    with open(init_schema_path, "r") as f:
        content = f.read()
    return set(_extract_tables_from_ddl(content))


# ---------------------------------------------------------------------------
# Article Checkers (Static)
# ---------------------------------------------------------------------------

def _check_article_1(module_path: str, module_name: str) -> dict:
    """Article 1: Table Prefix Enforcement."""
    violations = []
    ddl = _read_init_db(module_path)

    if ddl is None:
        # No init_db.py — module uses only core tables, skip
        return {"article": 1, "result": "skip", "violations": [], "reason": "No init_db.py found"}

    if _is_core_module(module_path):
        # Core modules don't need prefixes
        return {"article": 1, "result": "skip", "violations": [], "reason": "Core module (no prefix required)"}

    tables = _extract_tables_from_ddl(ddl)
    if not tables:
        return {"article": 1, "result": "skip", "violations": [], "reason": "No tables found in init_db.py"}

    expected_prefixes = _get_expected_prefixes(module_name)

    for table in tables:
        if not any(table.startswith(prefix) for prefix in expected_prefixes):
            violations.append({
                "table": table,
                "expected_prefixes": expected_prefixes,
                "message": f"Table '{table}' does not start with any expected prefix: {expected_prefixes}",
            })

    return {
        "article": 1,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_2(module_path: str) -> dict:
    """Article 2: Money is TEXT."""
    violations = []
    ddl = _read_init_db(module_path)

    if ddl is None:
        return {"article": 2, "result": "skip", "violations": [], "reason": "No init_db.py found"}

    columns = _parse_columns(ddl)

    for col in columns:
        col_lower = col["name"].lower()
        if _MONEY_PATTERNS.search(col_lower) and col_lower not in _MONEY_EXCEPTIONS:
            if col["type"] in ("REAL", "FLOAT", "NUMERIC", "INTEGER"):
                # Special case: columns named "*_id" or "*_count" are not money
                if col_lower.endswith("_id") or col_lower.endswith("_count"):
                    continue
                # Special case: boolean flags (is_billable, is_billed, etc.)
                if col_lower.startswith("is_"):
                    continue
                # Special case: matches_found is an integer count, not money
                if col_lower in ("matches_found",):
                    continue
                violations.append({
                    "table": col["table"],
                    "column": col["name"],
                    "type": col["type"],
                    "message": f"Column '{col['name']}' in table '{col['table']}' uses {col['type']} — should be TEXT for money/decimal values",
                })

    return {
        "article": 2,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_3(module_path: str) -> dict:
    """Article 3: UUID Primary Keys (id TEXT)."""
    violations = []
    ddl = _read_init_db(module_path)

    if ddl is None:
        return {"article": 3, "result": "skip", "violations": [], "reason": "No init_db.py found"}

    columns = _parse_columns(ddl)

    # Group by table to find primary key columns
    tables_seen = set()
    pk_columns = {}
    for col in columns:
        tables_seen.add(col["table"])
        if col["is_pk"]:
            pk_columns[col["table"]] = col

    for table in tables_seen:
        if table not in pk_columns:
            # Check for composite primary key (PRIMARY KEY(a, b)) — these
            # are valid for join/mapping tables
            # Look for PRIMARY KEY( in the DDL for this table
            table_pattern = re.compile(
                rf"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+{re.escape(table)}\s*\((.*?)\)\s*;",
                re.IGNORECASE | re.DOTALL,
            )
            table_match = table_pattern.search(ddl)
            if table_match:
                body = table_match.group(1)
                if re.search(r"PRIMARY\s+KEY\s*\(", body, re.IGNORECASE):
                    # Composite PK — skip (acceptable for join tables)
                    continue

            violations.append({
                "table": table,
                "message": f"Table '{table}' has no 'id TEXT PRIMARY KEY' column",
            })
            continue

        pk = pk_columns[table]
        if pk["name"] != "id":
            violations.append({
                "table": table,
                "column": pk["name"],
                "message": f"Table '{table}' primary key is '{pk['name']}' — should be 'id'",
            })
        elif pk["type"] != "TEXT":
            violations.append({
                "table": table,
                "column": pk["name"],
                "type": pk["type"],
                "message": f"Table '{table}' primary key type is {pk['type']} — should be TEXT (UUID)",
            })

    return {
        "article": 3,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_4(module_path: str, src_root: str = None) -> dict:
    """Article 4: Foreign Key Integrity."""
    violations = []
    ddl = _read_init_db(module_path)

    if ddl is None:
        return {"article": 4, "result": "skip", "violations": [], "reason": "No init_db.py found"}

    # Tables defined in this module
    module_tables = set(_extract_tables_from_ddl(ddl))

    # Core tables (if src_root provided)
    core_tables = set()
    if src_root:
        core_tables = _get_core_tables(src_root)

    # All known tables for FK validation
    known_tables = module_tables | core_tables

    # Extract FK references
    fk_refs = _extract_fk_references(ddl)
    for ref_table in fk_refs:
        if ref_table not in known_tables:
            # Check if it might be from a dependency module (e.g., healthclaw-vet refs healthclaw tables)
            # We allow this as a warning, not a hard failure, since we can't resolve all deps
            violations.append({
                "referenced_table": ref_table,
                "message": f"Foreign key references table '{ref_table}' which is not in this module or core ERP",
            })

    return {
        "article": 4,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_5(module_path: str, table_registry: dict = None) -> dict:
    """Article 5: No Cross-Module Writes."""
    violations = []

    scripts_dir = _find_scripts_dir(module_path)
    if scripts_dir is None:
        return {"article": 5, "result": "skip", "violations": [], "reason": "No scripts/ directory found"}

    # Tables owned by this module
    ddl = _read_init_db(module_path)
    owned_tables = set()
    if ddl:
        owned_tables = set(_extract_tables_from_ddl(ddl))

    module_name = _derive_module_name(module_path)

    # If we have a registry, also include tables that belong to this module
    if table_registry:
        for tbl, mod in table_registry.items():
            if mod == module_name:
                owned_tables.add(tbl)

    # If the module is core, it owns all core tables
    if _is_core_module(module_path):
        return {"article": 5, "result": "skip", "violations": [], "reason": "Core module"}

    py_files = _get_all_py_files(scripts_dir)

    write_pattern = re.compile(
        r"\b(INSERT\s+(?:OR\s+\w+\s+)?INTO|UPDATE|DELETE\s+FROM)\s+(\w+)",
        re.IGNORECASE,
    )

    for pyfile in py_files:
        # Skip test files
        if os.sep + "tests" + os.sep in pyfile or pyfile.endswith("conftest.py"):
            continue

        sql_entries = _extract_sql_strings_from_ast(pyfile)
        for entry in sql_entries:
            sql = entry["sql"]
            for match in write_pattern.finditer(sql):
                operation = match.group(1).strip()
                target_table = match.group(2)

                # Skip if table is owned by this module
                if target_table in owned_tables:
                    continue

                # Skip erpclaw OS internal tables
                if target_table.startswith("erpclaw_module_") or target_table.startswith("erpclaw_table_"):
                    continue

                # Skip common core tables that modules might legitimately write to
                # via cross_skill (we check if they use cross_skill below)
                if table_registry and target_table in table_registry:
                    violations.append({
                        "file": os.path.relpath(pyfile, module_path),
                        "line": entry["line"],
                        "operation": operation,
                        "target_table": target_table,
                        "owner": table_registry.get(target_table, "unknown"),
                        "message": (
                            f"Direct {operation} to '{target_table}' "
                            f"(owned by '{table_registry.get(target_table, 'unknown')}') — "
                            f"use cross_skill.call_skill_action() instead"
                        ),
                    })

    return {
        "article": 5,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_6(module_path: str) -> dict:
    """Article 6: No Direct GL Writes."""
    violations = []

    scripts_dir = _find_scripts_dir(module_path)
    if scripts_dir is None:
        return {"article": 6, "result": "skip", "violations": [], "reason": "No scripts/ directory found"}

    gl_write_pattern = re.compile(
        r"INSERT\s+(?:OR\s+\w+\s+)?INTO\s+(?:gl_entry|stock_ledger_entry)\b",
        re.IGNORECASE,
    )

    py_files = _get_all_py_files(scripts_dir)

    for pyfile in py_files:
        # Skip test files
        if os.sep + "tests" + os.sep in pyfile or pyfile.endswith("conftest.py"):
            continue

        sql_entries = _extract_sql_strings_from_ast(pyfile)
        for entry in sql_entries:
            if gl_write_pattern.search(entry["sql"]):
                violations.append({
                    "file": os.path.relpath(pyfile, module_path),
                    "line": entry["line"],
                    "sql_fragment": entry["sql"][:100],
                    "message": (
                        f"Direct INSERT into gl_entry/stock_ledger_entry detected — "
                        f"use erpclaw_lib.gl_posting.insert_gl_entries() instead"
                    ),
                })

        # Also check raw source for f-string patterns that AST might miss
        with open(pyfile, "r") as f:
            source = f.read()
        for i, line in enumerate(source.split("\n"), 1):
            if gl_write_pattern.search(line) and "test" not in pyfile.lower():
                # Check if this is already captured by AST scan
                already = any(
                    v["line"] == i and v["file"] == os.path.relpath(pyfile, module_path)
                    for v in violations
                )
                if not already:
                    violations.append({
                        "file": os.path.relpath(pyfile, module_path),
                        "line": i,
                        "sql_fragment": line.strip()[:100],
                        "message": "Direct INSERT into gl_entry/stock_ledger_entry in source code",
                    })

    return {
        "article": 6,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_7(module_path: str) -> dict:
    """Article 7: Response Format (ok/err)."""
    violations = []

    scripts_dir = _find_scripts_dir(module_path)
    if scripts_dir is None:
        return {"article": 7, "result": "skip", "violations": [], "reason": "No scripts/ directory found"}

    # Find db_query.py (main entry point)
    db_query_path = os.path.join(scripts_dir, "db_query.py")
    if not os.path.isfile(db_query_path):
        violations.append({
            "message": "scripts/db_query.py not found",
        })
        return {"article": 7, "result": "fail", "violations": violations}

    # Check that db_query.py imports ok and err from erpclaw_lib.response
    has_ok = _check_imports(db_query_path, "ok", "erpclaw_lib.response")
    has_err = _check_imports(db_query_path, "err", "erpclaw_lib.response")

    if not has_ok:
        # Also check other .py files in case routing delegates to submodules
        py_files = _get_all_py_files(scripts_dir)
        for pyfile in py_files:
            if os.sep + "tests" + os.sep in pyfile:
                continue
            if _check_imports(pyfile, "ok", "erpclaw_lib.response"):
                has_ok = True
                break

    if not has_err:
        py_files = _get_all_py_files(scripts_dir)
        for pyfile in py_files:
            if os.sep + "tests" + os.sep in pyfile:
                continue
            if _check_imports(pyfile, "err", "erpclaw_lib.response"):
                has_err = True
                break

    if not has_ok:
        violations.append({
            "message": "No import of 'ok' from erpclaw_lib.response found in any script file",
        })
    if not has_err:
        violations.append({
            "message": "No import of 'err' from erpclaw_lib.response found in any script file",
        })

    return {
        "article": 7,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_8(module_path: str) -> dict:
    """Article 8: Tests Exist."""
    violations = []

    tests_dir = _find_tests_dir(module_path)
    if tests_dir is None:
        violations.append({
            "message": "No tests/ directory found",
        })
        return {"article": 8, "result": "fail", "violations": violations}

    # Check for at least one test_*.py file
    test_files = [f for f in os.listdir(tests_dir) if f.startswith("test_") and f.endswith(".py")]
    if not test_files:
        violations.append({
            "message": "No test_*.py files found in tests/ directory",
        })
        return {"article": 8, "result": "fail", "violations": violations}

    # If SKILL.md exists, check that actions have corresponding tests
    skill_md = _read_skill_md(module_path)
    if skill_md:
        actions = _extract_action_names_from_skill_md(skill_md)
        test_funcs = _extract_test_function_names(tests_dir)
        test_func_text = " ".join(test_funcs).lower()

        untested = []
        for action in actions:
            # Convert action name to test-searchable format
            # e.g., "legal-add-client" -> search for "add_client" or "legal_add_client"
            action_snake = action.replace("-", "_")
            # Check various patterns
            if (
                action_snake not in test_func_text
                and action_snake.split("_", 1)[-1] not in test_func_text
                and f"test_{action_snake}" not in test_func_text
            ):
                untested.append(action)

        if untested:
            violations.append({
                "untested_actions": untested,
                "message": f"{len(untested)} action(s) have no corresponding test",
            })

    return {
        "article": 8,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_10(module_path: str) -> dict:
    """Article 10: Security Scan."""
    violations = []

    # Scan all .py files in the module
    py_files = _get_all_py_files(module_path)

    for pyfile in py_files:
        # Skip test files for credential checks (test data is expected)
        is_test = os.sep + "tests" + os.sep in pyfile or "test_" in os.path.basename(pyfile)

        with open(pyfile, "r") as f:
            content = f.read()

        for i, line in enumerate(content.split("\n"), 1):
            for pattern, description in _SECURITY_PATTERNS:
                if pattern.search(line):
                    # Skip SQL injection check in test files
                    if is_test and "SQL injection" in description:
                        continue
                    # Skip SSN patterns in test files (test data)
                    if is_test and "SSN" in description:
                        continue
                    # Skip credential patterns in test files
                    if is_test and "credential" in description:
                        continue
                    violations.append({
                        "file": os.path.relpath(pyfile, module_path),
                        "line": i,
                        "pattern": description,
                        "content": line.strip()[:80],
                        "message": f"{description} at {os.path.relpath(pyfile, module_path)}:{i}",
                    })

    return {
        "article": 10,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_11(module_path: str) -> dict:
    """Article 11: SKILL.md Format."""
    violations = []

    skill_md = _read_skill_md(module_path)
    if skill_md is None:
        violations.append({"message": "SKILL.md not found"})
        return {"article": 11, "result": "fail", "violations": violations}

    # Check line count
    line_count = len(skill_md.split("\n"))
    if line_count > 300:
        violations.append({
            "line_count": line_count,
            "message": f"SKILL.md has {line_count} lines — maximum is 300",
        })

    # Check YAML frontmatter
    frontmatter = _parse_skill_md_frontmatter(skill_md)
    if frontmatter is None:
        violations.append({"message": "SKILL.md has no valid YAML frontmatter"})
    else:
        # Check required fields
        required_fields = ["name", "version", "description"]
        for field in required_fields:
            if field not in frontmatter:
                violations.append({
                    "field": field,
                    "message": f"SKILL.md frontmatter missing required field: '{field}'",
                })

    return {
        "article": 11,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_12(module_path: str, module_name: str) -> dict:
    """Article 12: Naming Convention (kebab-case, namespace prefix)."""
    violations = []

    skill_md = _read_skill_md(module_path)
    if skill_md is None:
        return {"article": 12, "result": "skip", "violations": [], "reason": "No SKILL.md found"}

    actions = _extract_action_names_from_skill_md(skill_md)
    if not actions:
        return {"article": 12, "result": "skip", "violations": [], "reason": "No actions found in SKILL.md"}

    is_core = _is_core_module(module_path)
    kebab_pattern = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

    for action in actions:
        # Check kebab-case
        if not kebab_pattern.match(action):
            violations.append({
                "action": action,
                "message": f"Action '{action}' is not kebab-case",
            })
            continue

        # For non-core modules, check namespace prefix
        if not is_core:
            # Derive expected prefix from module name
            # e.g., legalclaw -> legal-, retailclaw -> retail-
            # healthclaw-vet -> vet- or health-
            expected_prefixes = []
            if module_name.endswith("claw"):
                short = module_name[:-4]
                expected_prefixes.append(f"{short}-")
            elif "-" in module_name:
                # e.g., healthclaw-vet -> vet- or health-
                parts = module_name.split("-")
                for p in parts:
                    if p.endswith("claw"):
                        expected_prefixes.append(f"{p[:-4]}-")
                    else:
                        expected_prefixes.append(f"{p}-")
            else:
                expected_prefixes.append(f"{module_name}-")

            # "status" is a special case — all modules can have it
            if action == "status":
                continue

            if not any(action.startswith(prefix) for prefix in expected_prefixes):
                violations.append({
                    "action": action,
                    "expected_prefixes": expected_prefixes,
                    "message": f"Non-core action '{action}' missing namespace prefix (expected: {expected_prefixes})",
                })

    return {
        "article": 12,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_19(module_path: str) -> dict:
    """Article 19: In-Module Modification Scope.

    When the OS adds features to an existing module, it may only ADD new
    functions and extend the ACTIONS dict.  It must NOT modify existing
    functions, change existing SQL queries, or alter existing test expectations.

    Enforcement: if a `.os_manifest.json` exists, every function listed
    in `generated_functions` must actually exist in the module's scripts/*.py
    files (i.e. the manifest must not list phantom entries).  If the manifest
    also contains `modified_functions` (which it never should), that is a
    violation.  When no manifest exists the article passes (backwards
    compatible with modules that were never touched by the OS).
    """
    import json as _json

    manifest_path = os.path.join(module_path, ".os_manifest.json")

    # No manifest -> pass (backwards compatible)
    if not os.path.isfile(manifest_path):
        return {"article": 19, "result": "skip", "violations": [],
                "reason": "No .os_manifest.json found (module not OS-modified)"}

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = _json.loads(f.read())
    except (OSError, _json.JSONDecodeError) as exc:
        return {"article": 19, "result": "fail", "violations": [
            {"message": f"Cannot read .os_manifest.json: {exc}"}]}

    violations = []

    # Check: manifest must NOT have a "modified_functions" list with entries.
    modified = manifest.get("modified_functions", [])
    for entry in modified:
        violations.append({
            "message": (
                f"OS modified existing function '{entry.get('function_name', '?')}' "
                f"— only additions are permitted"
            ),
            "function": entry.get("function_name", "?"),
        })

    # Check: every generated function must actually exist in module .py files
    generated = manifest.get("generated_functions", [])
    scripts_dir = os.path.join(module_path, "scripts")
    module_code = ""
    if os.path.isdir(scripts_dir):
        for fname in os.listdir(scripts_dir):
            if fname.endswith(".py"):
                fpath = os.path.join(scripts_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        module_code += "\n" + f.read()
                except OSError:
                    pass

    for entry in generated:
        func_name = entry.get("function_name", "")
        if func_name and f"def {func_name}(" not in module_code:
            violations.append({
                "message": (
                    f"Manifest lists generated function '{func_name}' "
                    f"but it was not found in scripts/*.py"
                ),
                "function": func_name,
            })

    return {
        "article": 19,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_20(module_path: str) -> dict:
    """Article 20: Research Provenance.

    Every OS-generated feature must cite its business rule source.  We check
    that each function listed in `.os_manifest.json` has a ``# Source:``
    comment inside its body (GAAP standard, regulatory reference, or
    existing ERPClaw pattern reference).

    When no manifest exists the article passes (non-OS-generated modules
    are not required to have provenance comments).
    """
    import json as _json

    manifest_path = os.path.join(module_path, ".os_manifest.json")

    if not os.path.isfile(manifest_path):
        return {"article": 20, "result": "skip", "violations": [],
                "reason": "No .os_manifest.json found (module not OS-modified)"}

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = _json.loads(f.read())
    except (OSError, _json.JSONDecodeError) as exc:
        return {"article": 20, "result": "fail", "violations": [
            {"message": f"Cannot read .os_manifest.json: {exc}"}]}

    generated = manifest.get("generated_functions", [])
    if not generated:
        return {"article": 20, "result": "skip", "violations": [],
                "reason": "No generated functions listed in manifest"}

    # Collect all script code, split by function boundaries
    scripts_dir = os.path.join(module_path, "scripts")
    module_code = ""
    if os.path.isdir(scripts_dir):
        for fname in sorted(os.listdir(scripts_dir)):
            if fname.endswith(".py"):
                fpath = os.path.join(scripts_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        module_code += "\n" + f.read()
                except OSError:
                    pass

    violations = []
    source_re = re.compile(r"#\s*Source:", re.IGNORECASE)

    for entry in generated:
        func_name = entry.get("function_name", "")
        if not func_name:
            continue

        # Find the function body (from def to next def or end of file)
        func_pattern = re.compile(
            rf"def {re.escape(func_name)}\(.*?\).*?(?=\ndef |\Z)",
            re.DOTALL,
        )
        match = func_pattern.search(module_code)
        if match:
            func_body = match.group(0)
            if not source_re.search(func_body):
                violations.append({
                    "message": (
                        f"OS-generated function '{func_name}' has no "
                        f"'# Source:' provenance comment"
                    ),
                    "function": func_name,
                })
        else:
            # Function not found in code — Article 19 catches this, skip here
            pass

    return {
        "article": 20,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


def _check_article_21(module_path: str) -> dict:
    """Article 21: Feature Isolation.

    A new feature added to an existing module must be testable in isolation.
    Every function listed in `.os_manifest.json` must have a corresponding
    test function in the tests/ directory.  Those test files must not modify
    or re-define any pre-existing test functions (detected via naming
    collisions with test files that do NOT correspond to a generated feature).

    When no manifest exists the article passes.
    """
    import json as _json

    manifest_path = os.path.join(module_path, ".os_manifest.json")

    if not os.path.isfile(manifest_path):
        return {"article": 21, "result": "skip", "violations": [],
                "reason": "No .os_manifest.json found (module not OS-modified)"}

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = _json.loads(f.read())
    except (OSError, _json.JSONDecodeError) as exc:
        return {"article": 21, "result": "fail", "violations": [
            {"message": f"Cannot read .os_manifest.json: {exc}"}]}

    generated = manifest.get("generated_functions", [])
    if not generated:
        return {"article": 21, "result": "skip", "violations": [],
                "reason": "No generated functions listed in manifest"}

    # Collect all test functions from tests/ directory
    tests_dir = _find_tests_dir(module_path)
    if tests_dir is None:
        return {"article": 21, "result": "fail", "violations": [
            {"message": "No tests/ directory found for OS-modified module"}]}

    # Extract test function names from test files
    test_funcs_found = set()
    for root, _dirs, files in os.walk(tests_dir):
        for fname in files:
            if fname.startswith("test_") and fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    for m in re.finditer(r"def (test_\w+)\(", content):
                        test_funcs_found.add(m.group(1))
                except OSError:
                    pass

    violations = []
    for entry in generated:
        action_name = entry.get("action_name", "")
        func_name = entry.get("function_name", "")
        # Expected test function: test_{action_with_underscores}
        expected_test = "test_" + action_name.replace("-", "_")

        # Check if any test function name contains the action reference
        has_test = any(
            expected_test in tf or func_name.replace("handle_", "test_") in tf
            for tf in test_funcs_found
        )
        if not has_test:
            violations.append({
                "message": (
                    f"OS-generated action '{action_name}' (function "
                    f"'{func_name}') has no corresponding isolated test "
                    f"(expected test function matching '{expected_test}')"
                ),
                "action": action_name,
                "function": func_name,
            })

    return {
        "article": 21,
        "result": "fail" if violations else "pass",
        "violations": violations,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_module_static(module_path: str, src_root: str = None) -> dict:
    """Validate a module against Articles 1-8, 10-12, 19-21 using static analysis.

    Args:
        module_path: Path to the module directory (must contain SKILL.md and/or init_db.py)
        src_root: Path to the src/ directory (for cross-module table resolution).
                  If None, attempts to auto-detect from module_path.

    Returns:
        {
            "result": "pass" | "fail",
            "module_name": str,
            "module_path": str,
            "articles": {1: "pass", 2: "fail", ...},
            "violations": [{"article": N, ...}, ...],
            "skipped": [{"article": N, "reason": str}, ...],
        }
    """
    module_path = os.path.normpath(module_path)
    module_name = _derive_module_name(module_path)

    # Auto-detect src_root
    if src_root is None:
        # Walk up to find src/ directory
        current = module_path
        for _ in range(10):
            parent = os.path.dirname(current)
            if os.path.basename(parent) == "src" or os.path.basename(current) == "src":
                src_root = current if os.path.basename(current) == "src" else parent
                break
            current = parent

    # Build table ownership registry if src_root found
    table_registry = None
    if src_root:
        table_registry = build_table_ownership_registry(src_root)

    # Run all static article checks
    checks = [
        _check_article_1(module_path, module_name),
        _check_article_2(module_path),
        _check_article_3(module_path),
        _check_article_4(module_path, src_root),
        _check_article_5(module_path, table_registry),
        _check_article_6(module_path),
        _check_article_7(module_path),
        _check_article_8(module_path),
        _check_article_10(module_path),
        _check_article_11(module_path),
        _check_article_12(module_path, module_name),
        _check_article_19(module_path),
        _check_article_20(module_path),
        _check_article_21(module_path),
    ]

    articles = {}
    all_violations = []
    skipped = []
    overall = "pass"

    for check in checks:
        article_num = check["article"]
        result = check["result"]
        articles[article_num] = result

        if result == "fail":
            overall = "fail"
            for v in check.get("violations", []):
                v["article"] = article_num
                all_violations.append(v)
        elif result == "skip":
            skipped.append({
                "article": article_num,
                "reason": check.get("reason", "Skipped"),
            })

    return {
        "result": overall,
        "module_name": module_name,
        "module_path": module_path,
        "articles": articles,
        "violations": all_violations,
        "skipped": skipped,
    }


def validate_module_runtime(module_path: str, db_path: str = None) -> dict:
    """Validate Article 9 (tests pass) by running tests in sandbox.

    Args:
        module_path: Path to the module directory
        db_path: Optional path to a test database

    Returns:
        {
            "result": "pass" | "fail",
            "tests_run": N,
            "tests_passed": N,
            "tests_failed": N,
            "output": str,
        }
    """
    tests_dir = _find_tests_dir(module_path)
    if tests_dir is None:
        return {
            "result": "fail",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "output": "No tests/ directory found",
        }

    env = os.environ.copy()
    if db_path:
        env["ERPCLAW_DB_PATH"] = db_path

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", tests_dir, "-v", "--tb=short", "-q"],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
            cwd=os.path.dirname(module_path),
        )

        output = proc.stdout + proc.stderr

        # Parse pytest output for counts
        tests_run = 0
        tests_passed = 0
        tests_failed = 0

        # Look for "X passed, Y failed" in output
        summary_match = re.search(
            r"(\d+)\s+passed(?:,\s+(\d+)\s+failed)?",
            output,
        )
        if summary_match:
            tests_passed = int(summary_match.group(1))
            tests_failed = int(summary_match.group(2) or 0)
            tests_run = tests_passed + tests_failed
        else:
            # Try alternate format: "X failed"
            fail_match = re.search(r"(\d+)\s+failed", output)
            if fail_match:
                tests_failed = int(fail_match.group(1))
                tests_run = tests_failed

        return {
            "result": "pass" if proc.returncode == 0 else "fail",
            "tests_run": tests_run,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "output": output[-2000:] if len(output) > 2000 else output,
        }
    except subprocess.TimeoutExpired:
        return {
            "result": "fail",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "output": "Test execution timed out after 120 seconds",
        }
    except Exception as e:
        return {
            "result": "fail",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "output": f"Error running tests: {str(e)}",
        }
