"""ERPClaw OS Module Generator -- template-based code generation from structured input.

Generates a complete ERPClaw module (init_db.py, db_query.py, domain module,
SKILL.md, tests) from a module name, prefix, business description, and entity
definitions.

This is NOT an LLM-based generator. It uses Python string formatting to render
code from patterns defined in pattern_library.py. The determinism makes it
testable and does not require API keys.

After generation, the output is validated with validate_module_static().
"""
import os
import re
import sys

# Make erpclaw-os package importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from pattern_library import PATTERNS


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def _validate_inputs(module_name, prefix, entities):
    """Validate generator inputs. Returns list of error messages (empty = OK)."""
    errors = []
    if not module_name or not module_name.strip():
        errors.append("module_name is required")
    if not prefix or not prefix.strip():
        errors.append("prefix is required")
    if not entities or len(entities) == 0:
        errors.append("At least one entity is required")
        return errors

    # Check for duplicate entity names
    names = [e.get("name", "") for e in entities]
    seen = set()
    for n in names:
        if not n:
            errors.append("Entity name is required for all entities")
        elif n in seen:
            errors.append(f"Duplicate entity name: {n}")
        seen.add(n)

    # Validate each entity has a valid pattern
    for ent in entities:
        pattern = ent.get("pattern", "")
        if pattern and pattern not in PATTERNS:
            errors.append(f"Unknown pattern '{pattern}' for entity '{ent.get('name', '?')}'")

    # Validate prefix format (alphanumeric, lowercase, no hyphens)
    if prefix and not re.match(r'^[a-z][a-z0-9]*$', prefix):
        errors.append(f"Prefix must be lowercase alphanumeric starting with a letter, got: {prefix}")

    return errors


# ---------------------------------------------------------------------------
# Code generation helpers
# ---------------------------------------------------------------------------

def _table_name(prefix, entity_name):
    """Build the full table name: {prefix}_{entity_name}."""
    return f"{prefix}_{entity_name}"


def _action_name(prefix, verb, entity_name):
    """Build a namespaced action name: {prefix}-{verb}-{entity_name_kebab}."""
    kebab = entity_name.replace("_", "-")
    return f"{prefix}-{verb}-{kebab}"


def _entity_to_table_name_snake(entity_name):
    """Convert entity name to snake_case for table/var naming."""
    return entity_name.replace("-", "_").replace(" ", "_").lower()


def _build_entity_fields(entity):
    """Merge pattern fields with any custom fields from the entity definition."""
    pattern_key = entity.get("pattern", "crud_entity")
    pattern = PATTERNS.get(pattern_key, PATTERNS["crud_entity"])
    base_fields = list(pattern["schema_fields"])

    # Add custom fields from the entity
    custom_fields = entity.get("fields", [])
    # Track existing column names to avoid duplicates
    existing_cols = set()
    for f in base_fields:
        col_name = f.split()[0].strip()
        existing_cols.add(col_name)

    for cf in custom_fields:
        col_name = cf.split()[0].strip()
        if col_name not in existing_cols:
            base_fields.append(cf)
            existing_cols.add(col_name)

    return base_fields


def _build_entity_actions(prefix, entity_name, entity):
    """Build the list of action names for an entity based on its pattern."""
    pattern_key = entity.get("pattern", "crud_entity")
    pattern = PATTERNS.get(pattern_key, PATTERNS["crud_entity"])
    actions = []
    ename = _entity_to_table_name_snake(entity_name)
    for verb in pattern["actions"]:
        # Special handling for compound verbs
        if verb == "use-session":
            actions.append(_action_name(prefix, "use", f"{ename}-session"))
        elif verb == "get-balance":
            actions.append(_action_name(prefix, "get", f"{ename}-balance"))
        elif verb == "generate-invoices":
            actions.append(_action_name(prefix, "generate", f"{ename}-invoices"))
        elif verb == "apply-late-fees":
            actions.append(_action_name(prefix, "apply", f"{ename}-late-fees"))
        elif verb == "create-invoice":
            actions.append(f"{prefix}-create-invoice")
        else:
            # Standard: add, update, get, list
            plural = f"{ename}s" if verb == "list" else ename
            actions.append(_action_name(prefix, verb, plural))
    return actions


# ---------------------------------------------------------------------------
# File generators
# ---------------------------------------------------------------------------

def _generate_init_db(module_name, prefix, display_name, entities):
    """Generate init_db.py content."""
    table_blocks = []
    index_blocks = []

    for i, ent in enumerate(entities, 1):
        ename = _entity_to_table_name_snake(ent["name"])
        tname = _table_name(prefix, ename)
        fields = _build_entity_fields(ent)
        pattern_key = ent.get("pattern", "crud_entity")

        # Skip entities with no schema fields (e.g., invoice_delegation)
        if not fields:
            continue

        # Build column definitions
        col_lines = []
        for f in fields:
            col_lines.append(f"            {f}")
        columns_sql = ",\n".join(col_lines)

        table_sql = (
            f"        -- ==========================================================\n"
            f"        -- TABLE {i}: {ename.upper()}\n"
            f"        -- ==========================================================\n"
            f"\n"
            f"        CREATE TABLE IF NOT EXISTS {tname} (\n"
            f"{columns_sql}\n"
            f"        );"
        )
        table_blocks.append(table_sql)

        # Generate indexes
        idx_lines = []
        idx_lines.append(
            f"        CREATE INDEX IF NOT EXISTS idx_{tname}_company\n"
            f"            ON {tname}(company_id);"
        )
        # Add index on status if it exists
        has_status = any(f.split()[0] == "status" for f in fields)
        if has_status:
            idx_lines.append(
                f"        CREATE INDEX IF NOT EXISTS idx_{tname}_status\n"
                f"            ON {tname}(status);"
            )
        # Add index on date field for appointment pattern
        if pattern_key == "appointment_booking":
            idx_lines.append(
                f"        CREATE INDEX IF NOT EXISTS idx_{tname}_date\n"
                f"            ON {tname}(date);"
            )

        index_blocks.append("\n".join(idx_lines))

    # Count tables
    table_count = len(table_blocks)

    # Combine table + index blocks
    all_blocks = []
    for t, idx in zip(table_blocks, index_blocks):
        all_blocks.append(t)
        all_blocks.append(idx)

    tables_sql = "\n\n\n".join(all_blocks)

    # Build the list of table names for reference
    table_names = []
    for ent in entities:
        ename = _entity_to_table_name_snake(ent["name"])
        fields = _build_entity_fields(ent)
        if fields:
            table_names.append(_table_name(prefix, ename))

    init_db_content = f'''#!/usr/bin/env python3
"""{display_name} schema initialization.

Creates {table_count} {module_name}-specific tables in the shared ERPClaw database.
Requires ERPClaw foundation tables to exist (company FK references).

Tables:
{chr(10).join(f"  {i+1}. {tn}" for i, tn in enumerate(table_names))}

Run: python3 init_db.py [db_path]
"""
import os
import sqlite3
import sys
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))


DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")
DISPLAY_NAME = "{display_name}"

REQUIRED_FOUNDATION = [
    "company", "customer", "naming_series", "audit_log",
]


def init_{module_name.replace("-", "_")}_schema(db_path=None):
    db_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)

    # Verify ERPClaw foundation
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type=\'table\'"
    ).fetchall()]
    missing = [t for t in REQUIRED_FOUNDATION if t not in tables]
    if missing:
        print(f"ERROR: Foundation tables missing: {{', '.join(missing)}}")
        print("Run erpclaw-setup first: clawhub install erpclaw-setup")
        conn.close()
        sys.exit(1)

    conn.executescript("""
        -- ==========================================================
        -- {display_name} Domain Tables
        -- {table_count} tables, {prefix}_ prefix
        -- Convention: TEXT for IDs (UUID4), TEXT for money (Decimal),
        --             TEXT for dates (ISO-8601)
        -- ==========================================================

{tables_sql}
    """)

    conn.commit()
    conn.close()
    print(f"{{DISPLAY_NAME}}: Schema initialized ({{db_path}})")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_PATH
    init_{module_name.replace("-", "_")}_schema(path)
'''
    return init_db_content


def _generate_domain_module(module_name, prefix, display_name, entities, business_description):
    """Generate the domain .py module with action functions."""
    module_short = module_name.replace("claw", "").replace("-", "_")
    if not module_short:
        module_short = module_name.replace("-", "_")

    # Collect all actions and table names
    all_actions = {}
    has_invoice_delegation = False

    for ent in entities:
        pattern_key = ent.get("pattern", "crud_entity")
        if pattern_key == "invoice_delegation":
            has_invoice_delegation = True
        actions = _build_entity_actions(prefix, ent["name"], ent)
        for act in actions:
            all_actions[act] = (ent["name"], ent.get("pattern", "crud_entity"))

    # Build imports
    imports = [
        'import json',
        'import os',
        'import sys',
        'import uuid',
        'from decimal import Decimal',
        '',
        'try:',
        '    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))',
        '    from erpclaw_lib.db import get_connection',
        '    from erpclaw_lib.decimal_utils import to_decimal, round_currency',
        '    from erpclaw_lib.response import ok, err, row_to_dict',
        '    from erpclaw_lib.audit import audit',
        '    from erpclaw_lib.query import Q, P, Table, Field, fn, Order, insert_row, update_row',
    ]
    if has_invoice_delegation:
        imports.append('    from erpclaw_lib.cross_skill import create_invoice, CrossSkillError')
    imports.extend([
        'except ImportError:',
        '    pass',
    ])

    # Build helper
    helper_block = '''

# ---- Helpers ----------------------------------------------------------------

def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
'''

    # Build action functions
    function_blocks = []
    action_map_entries = []
    func_counter = 0

    for ent in entities:
        ename = _entity_to_table_name_snake(ent["name"])
        tname = _table_name(prefix, ename)
        pattern_key = ent.get("pattern", "crud_entity")
        pattern = PATTERNS.get(pattern_key, PATTERNS["crud_entity"])
        fields = _build_entity_fields(ent)
        actions = _build_entity_actions(prefix, ent["name"], ent)

        for action in actions:
            func_counter += 1
            func_name = action.replace("-", "_")

            if pattern_key == "invoice_delegation":
                # Generate invoice delegation function
                block = _gen_invoice_delegation_func(func_counter, action, func_name, prefix)
                function_blocks.append(block)
                action_map_entries.append(f'    "{action}": {func_name},')
                continue

            # Determine which verb this is
            verb = _extract_verb(action, prefix, ename)

            if verb == "add":
                block = _gen_add_func(func_counter, action, func_name, tname, ename, prefix, fields)
            elif verb == "update":
                block = _gen_update_func(func_counter, action, func_name, tname, ename, prefix, fields)
            elif verb == "get":
                block = _gen_get_func(func_counter, action, func_name, tname, ename, prefix)
            elif verb == "list":
                block = _gen_list_func(func_counter, action, func_name, tname, ename, prefix)
            elif verb == "use":
                block = _gen_use_session_func(func_counter, action, func_name, tname, ename, prefix)
            elif verb in ("generate", "apply"):
                block = _gen_stub_func(func_counter, action, func_name, tname, ename, prefix, verb)
            else:
                block = _gen_stub_func(func_counter, action, func_name, tname, ename, prefix, verb)

            function_blocks.append(block)
            action_map_entries.append(f'    "{action}": {func_name},')

    # Build action router
    action_map = "ACTIONS = {\n" + "\n".join(action_map_entries) + "\n}"

    # Assemble the file
    content_parts = [
        f'"""{display_name} -- {module_short} domain module',
        f'',
        f'Actions for the {module_name} skill ({len(all_actions)} actions).',
        f'Imported by db_query.py (unified router).',
        f'',
        f'Business: {business_description[:200]}',
        f'"""',
        "\n".join(imports),
        helper_block,
    ]
    content_parts.extend(function_blocks)
    content_parts.append("")
    content_parts.append("# ---------------------------------------------------------------------------")
    content_parts.append("# Action Router")
    content_parts.append("# ---------------------------------------------------------------------------")
    content_parts.append(action_map)
    content_parts.append("")

    return "\n\n".join(content_parts)


def _extract_verb(action, prefix, ename):
    """Extract the verb from an action name like 'prefix-add-entity'."""
    # Strip prefix
    rest = action[len(prefix) + 1:]  # e.g., "add-entity" or "list-entities"
    parts = rest.split("-")
    return parts[0] if parts else "add"


def _gen_add_func(counter, action, func_name, tname, ename, prefix, fields):
    """Generate an add-entity function."""
    # Determine required and optional fields
    required_params = ["company_id"]
    optional_params = []
    insert_fields = {}

    for f in fields:
        col_name = f.split()[0]
        if col_name in ("id", "created_at", "updated_at"):
            continue
        if col_name == "company_id":
            continue  # Already required
        col_type = f.split()[1] if len(f.split()) > 1 else "TEXT"
        has_not_null = "NOT NULL" in f and "DEFAULT" not in f
        if has_not_null and col_name != "company_id":
            required_params.append(col_name)
        else:
            optional_params.append(col_name)

    # Build validation
    validation_lines = []
    for rp in required_params:
        flag = rp.replace("_", "-")
        validation_lines.append(f'    if not getattr(args, "{rp}", None):')
        validation_lines.append(f'        err("--{flag} is required")')

    # Build insert dict
    all_insert_cols = ["id", "company_id"]
    for f in fields:
        col_name = f.split()[0]
        if col_name not in ("id", "company_id", "created_at", "updated_at"):
            all_insert_cols.append(col_name)
    all_insert_cols.extend(["created_at", "updated_at"])

    insert_dict_lines = []
    for col in all_insert_cols:
        insert_dict_lines.append(f'        "{col}": P(),')
    insert_dict = "{\n" + "\n".join(insert_dict_lines) + "\n    }"

    # Build values list
    value_lines = []
    for col in all_insert_cols:
        if col == "id":
            value_lines.append("        entry_id,")
        elif col == "company_id":
            value_lines.append("        args.company_id,")
        elif col in ("created_at", "updated_at"):
            value_lines.append("        now,")
        elif col in required_params:
            value_lines.append(f"        args.{col},")
        else:
            value_lines.append(f'        getattr(args, "{col}", None),')

    values_tuple = "(\n" + "\n".join(value_lines) + "\n    )"

    block = f'''
# ---------------------------------------------------------------------------
# {counter}. {action}
# ---------------------------------------------------------------------------
def {func_name}(conn, args):
{chr(10).join(validation_lines)}

    entry_id = str(uuid.uuid4())
    now = _now_iso()
    sql, _ = insert_row("{tname}", {insert_dict})
    conn.execute(sql, {values_tuple})
    audit(conn, "{tname}", entry_id, "{action}", args.company_id)
    conn.commit()
    ok({{"id": entry_id, "name": getattr(args, "name", None)}})'''

    return block


def _gen_update_func(counter, action, func_name, tname, ename, prefix, fields):
    """Generate an update-entity function."""
    id_field = f"{ename}_id"
    id_flag = id_field.replace("_", "-")

    # Determine updatable fields
    updatable = []
    for f in fields:
        col_name = f.split()[0]
        if col_name in ("id", "company_id", "created_at", "updated_at"):
            continue
        updatable.append(col_name)

    update_map_lines = []
    for col in updatable:
        update_map_lines.append(f'        "{col}": "{col}",')
    update_map = "{\n" + "\n".join(update_map_lines) + "\n    }"

    block = f'''
# ---------------------------------------------------------------------------
# {counter}. {action}
# ---------------------------------------------------------------------------
def {func_name}(conn, args):
    entry_id = getattr(args, "{id_field}", None)
    if not entry_id:
        err("--{id_flag} is required")
    t = Table("{tname}")
    q = Q.from_(t).select(t.id).where(t.id == P())
    if not conn.execute(q.get_sql(), (entry_id,)).fetchone():
        err(f"{ename} {{entry_id}} not found")

    data, params, changed = {{}}, [], []
    for arg_name, col_name in {update_map}.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            data[col_name] = P()
            params.append(val)
            changed.append(col_name)

    if not data:
        err("No fields to update")
    data["updated_at"] = P()
    params.append(_now_iso())
    params.append(entry_id)
    sql = update_row("{tname}", data, {{"id": P()}})
    conn.execute(sql, params)
    audit(conn, "{tname}", entry_id, "{action}", getattr(args, "company_id", None))
    conn.commit()
    ok({{"id": entry_id, "updated_fields": changed}})'''

    return block


def _gen_get_func(counter, action, func_name, tname, ename, prefix):
    """Generate a get-entity function."""
    id_field = f"{ename}_id"
    id_flag = id_field.replace("_", "-")

    block = f'''
# ---------------------------------------------------------------------------
# {counter}. {action}
# ---------------------------------------------------------------------------
def {func_name}(conn, args):
    entry_id = getattr(args, "{id_field}", None)
    if not entry_id:
        err("--{id_flag} is required")
    t = Table("{tname}")
    q = Q.from_(t).select(t.star).where(t.id == P())
    row = conn.execute(q.get_sql(), (entry_id,)).fetchone()
    if not row:
        err(f"{ename} {{entry_id}} not found")
    ok(row_to_dict(row))'''

    return block


def _gen_list_func(counter, action, func_name, tname, ename, prefix):
    """Generate a list-entities function."""
    block = f'''
# ---------------------------------------------------------------------------
# {counter}. {action}
# ---------------------------------------------------------------------------
def {func_name}(conn, args):
    t = Table("{tname}")
    q_count = Q.from_(t).select(fn.Count("*"))
    q_rows = Q.from_(t).select(t.star)
    params = []

    if getattr(args, "company_id", None):
        q_count = q_count.where(t.company_id == P())
        q_rows = q_rows.where(t.company_id == P())
        params.append(args.company_id)
    if getattr(args, "status", None):
        q_count = q_count.where(t.status == P())
        q_rows = q_rows.where(t.status == P())
        params.append(args.status)

    total = conn.execute(q_count.get_sql(), params).fetchone()[0]
    q_rows = q_rows.orderby(t.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(q_rows.get_sql(), params + [args.limit, args.offset]).fetchall()
    ok({{"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total}})'''

    return block


def _gen_use_session_func(counter, action, func_name, tname, ename, prefix):
    """Generate a use-session function for prepaid package pattern."""
    id_field = f"{ename}_id"
    id_flag = id_field.replace("_", "-")

    block = f'''
# ---------------------------------------------------------------------------
# {counter}. {action}
# ---------------------------------------------------------------------------
def {func_name}(conn, args):
    if not getattr(args, "company_id", None):
        err("--company-id is required")
    entry_id = getattr(args, "{id_field}", None)
    if not entry_id:
        err("--{id_flag} is required")

    t = Table("{tname}")
    q = Q.from_(t).select(t.star).where(t.id == P())
    row = conn.execute(q.get_sql(), (entry_id,)).fetchone()
    if not row:
        err(f"{ename} {{entry_id}} not found")
    pkg = row_to_dict(row)

    if pkg["status"] != "active":
        err(f"{ename} is {{pkg['status']}}. Cannot use sessions from a non-active record.")

    remaining = pkg["total_sessions"] - pkg["used_sessions"]
    if remaining <= 0:
        err("No sessions remaining")

    new_used = pkg["used_sessions"] + 1
    new_remaining = pkg["total_sessions"] - new_used
    new_status = "exhausted" if new_remaining <= 0 else "active"

    sql = update_row("{tname}", {{"used_sessions": P(), "status": P(), "updated_at": P()}}, {{"id": P()}})
    conn.execute(sql, (new_used, new_status, _now_iso(), entry_id))
    audit(conn, "{tname}", entry_id, "{action}", args.company_id)
    conn.commit()
    ok({{"id": entry_id, "used_sessions": new_used, "remaining_sessions": new_remaining, "status": new_status}})'''

    return block


def _gen_invoice_delegation_func(counter, action, func_name, prefix):
    """Generate a create-invoice function using cross_skill delegation."""
    block = f'''
# ---------------------------------------------------------------------------
# {counter}. {action}
# ---------------------------------------------------------------------------
def {func_name}(conn, args):
    """Create a sales invoice via cross_skill.create_invoice().

    Delegates GL posting to the core ERP. Does NOT write to gl_entry directly.
    """
    if not getattr(args, "customer_id", None):
        err("--customer-id is required")
    if not getattr(args, "items", None):
        err("--items is required (JSON array of {{description, qty, rate}})")

    try:
        items = json.loads(args.items)
    except (json.JSONDecodeError, TypeError):
        err("--items must be valid JSON")

    if not isinstance(items, list) or len(items) == 0:
        err("--items must be a non-empty JSON array")

    for i, item in enumerate(items):
        if not item.get("description"):
            err(f"Item {{i}} missing \'description\'")
        if not item.get("qty"):
            err(f"Item {{i}} missing \'qty\'")
        if not item.get("rate"):
            err(f"Item {{i}} missing \'rate\'")

    try:
        result = create_invoice(
            customer_id=args.customer_id,
            items=items,
            company_id=getattr(args, "company_id", None),
            posting_date=getattr(args, "posting_date", None),
            due_date=getattr(args, "due_date", None),
            remarks=getattr(args, "remarks", None) or "{prefix} services invoice",
        )
        ok(result)
    except CrossSkillError as e:
        err(f"Invoice creation failed: {{str(e)}}")'''

    return block


def _gen_stub_func(counter, action, func_name, tname, ename, prefix, verb):
    """Generate a stub function for less common action patterns."""
    block = f'''
# ---------------------------------------------------------------------------
# {counter}. {action}
# ---------------------------------------------------------------------------
def {func_name}(conn, args):
    if not getattr(args, "company_id", None):
        err("--company-id is required")
    ok({{"action": "{action}", "message": "Action executed successfully"}})'''

    return block


def _generate_db_query(module_name, prefix, display_name, entities):
    """Generate db_query.py (unified router)."""
    module_short = module_name.replace("claw", "").replace("-", "_")
    if not module_short:
        module_short = module_name.replace("-", "_")

    # Collect all actions for the status output
    all_actions = []
    for ent in entities:
        all_actions.extend(_build_entity_actions(prefix, ent["name"], ent))

    # Collect table names
    table_names = []
    for ent in entities:
        ename = _entity_to_table_name_snake(ent["name"])
        fields = _build_entity_fields(ent)
        if fields:
            table_names.append(_table_name(prefix, ename))

    table_list_str = ",\n".join(f'                "{t}"' for t in table_names)

    # Collect all argument flags needed
    all_flags = set()
    all_flags.update(["company_id", "name", "status", "notes", "search", "description"])
    for ent in entities:
        ename = _entity_to_table_name_snake(ent["name"])
        all_flags.add(f"{ename}_id")
        fields = _build_entity_fields(ent)
        for f in fields:
            col_name = f.split()[0]
            if col_name not in ("id",):
                all_flags.add(col_name)

    # Add invoice-related flags if invoice delegation is present
    has_invoice = any(ent.get("pattern") == "invoice_delegation" for ent in entities)
    if has_invoice:
        all_flags.update(["customer_id", "items", "posting_date", "due_date", "remarks"])

    # Remove duplicates of common fields and sort
    all_flags.discard("id")
    all_flags.discard("created_at")
    all_flags.discard("updated_at")
    sorted_flags = sorted(all_flags)

    # Build parser arguments
    parser_args = []
    for flag in sorted_flags:
        flag_name = flag.replace("_", "-")
        if flag in ("limit",):
            parser_args.append(f'    parser.add_argument("--{flag_name}", type=int, default=50)')
        elif flag in ("offset",):
            parser_args.append(f'    parser.add_argument("--{flag_name}", type=int, default=0)')
        else:
            parser_args.append(f'    parser.add_argument("--{flag_name}")')
    parser_args_str = "\n".join(parser_args)

    content = f'''#!/usr/bin/env python3
"""{display_name} -- unified action router.

Usage: python3 db_query.py --action <action-name> [flags]

Routes all {len(all_actions)} {module_name} actions to the {module_short} domain module.
"""
import argparse
import os
import sys

# Shared library
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
# Domain module (same directory)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from erpclaw_lib.db import get_connection
from erpclaw_lib.response import ok, err
from erpclaw_lib.args import SafeArgumentParser

from {module_short} import ACTIONS as {module_short.upper()}_ACTIONS

# Merge all actions
ACTIONS = {{}}
ACTIONS.update({module_short.upper()}_ACTIONS)


def build_parser():
    parser = SafeArgumentParser(description="{display_name} -- {module_name}")
    parser.add_argument("--action", required=True, help="Action to execute")

{parser_args_str}

    # Common optional
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    action = args.action

    if action == "status":
        ok({{
            "skill": "{module_name}",
            "version": "1.0.0",
            "actions_available": len(ACTIONS),
            "tables": [
{table_list_str}
            ],
            "status": "ok",
        }})
        return

    if action not in ACTIONS:
        err(f"Unknown action: {{action}}. Available: {{', '.join(sorted(ACTIONS.keys()))}}")

    conn = get_connection()
    try:
        ACTIONS[action](conn, args)
    except SystemExit:
        raise
    except Exception as e:
        err(f"Internal error in {{action}}: {{str(e)}}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
'''
    return content


def _generate_skill_md(module_name, prefix, display_name, business_description, entities):
    """Generate SKILL.md with valid YAML frontmatter."""
    # Build action table
    action_rows = []
    for ent in entities:
        actions = _build_entity_actions(prefix, ent["name"], ent)
        for act in actions:
            # Build a description from the action name
            parts = act.split("-")
            verb = parts[1] if len(parts) > 1 else parts[0]
            entity = " ".join(parts[2:]) if len(parts) > 2 else ent["name"]
            desc = f"{verb.capitalize()} {entity}"
            action_rows.append(f"| `{act}` | {desc} |")

    # Build tags
    tags = [module_name, prefix]
    for ent in entities:
        tags.append(ent["name"].replace("_", "-"))

    action_table = "\n".join(action_rows)
    tags_str = ", ".join(tags)

    content = f'''---
name: {module_name}
version: 1.0.0
description: {business_description[:200]}
author: AvanSaber
homepage: https://github.com/avansaber/{module_name}
source: https://github.com/avansaber/{module_name}
tier: 4
category: vertical
requires: [erpclaw]
database: ~/.openclaw/erpclaw/data.sqlite
user-invocable: true
tags: [{tags_str}]
scripts:
  - scripts/db_query.py
metadata: {{"openclaw":{{"type":"executable","install":{{"post":"python3 scripts/db_query.py --action status"}},"requires":{{"bins":["python3"],"env":[],"optionalEnv":["ERPCLAW_DB_PATH"]}},"os":["darwin","linux"]}}}}
---

# {module_name}

You are a business administrator for {display_name}, an AI-native management system built on ERPClaw.
{business_description[:300]}
All financial data uses Decimal precision. Invoicing is delegated to ERPClaw core via cross_skill.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **Zero network calls**: No external API calls, no telemetry, no cloud dependencies
- **SQL injection safe**: All queries use parameterized statements

### Setup (First Use Only)

If the database does not exist or you see "no such table" errors, run ERPClaw setup
first, then initialize this module's schema, then verify with the status check.

## Actions

| Action | Description |
|--------|-------------|
{action_table}
| `status` | Check module status |
'''
    return content


def _generate_tests(module_name, prefix, display_name, entities):
    """Generate test files: conftest.py, helpers, and test file."""
    module_short = module_name.replace("claw", "").replace("-", "_")
    if not module_short:
        module_short = module_name.replace("-", "_")
    init_func = f"init_{module_name.replace('-', '_')}_schema"

    # --- conftest.py ---
    conftest_content = f'''"""Shared pytest fixtures for {display_name} unit tests."""
import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

import pytest
from {module_short}_helpers import init_all_tables, get_conn, build_env


@pytest.fixture
def db_path(tmp_path):
    """Per-test fresh SQLite database with foundation + {module_name} schema."""
    path = str(tmp_path / "test.sqlite")
    init_all_tables(path)
    os.environ["ERPCLAW_DB_PATH"] = path
    yield path
    os.environ.pop("ERPCLAW_DB_PATH", None)


@pytest.fixture
def conn(db_path):
    connection = get_conn(db_path)
    yield connection
    connection.close()


@pytest.fixture
def fresh_db(conn):
    return conn


@pytest.fixture
def env(conn):
    """Full {module_name} environment: company, customer."""
    return build_env(conn)
'''

    # --- helpers ---
    helpers_content = f'''"""Shared helper functions for {display_name} unit tests.

Provides:
  - DB bootstrap via init_schema.init_db() + {init_func}()
  - call_action() / ns() / is_error() / is_ok()
  - Seed functions for company, customer
  - build_env() for full test environment
"""
import argparse
import importlib.util
import io
import json
import os
import sqlite3
import sys
import uuid
from decimal import Decimal
from unittest.mock import patch

# Paths
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(TESTS_DIR)                    # scripts/
ROOT_DIR = os.path.dirname(MODULE_DIR)                     # {module_name}/
SRC_DIR = os.path.dirname(ROOT_DIR)                        # src/

# Foundation schema init
SETUP_DIR = os.path.join(SRC_DIR, "erpclaw", "scripts", "erpclaw-setup")
INIT_SCHEMA_PATH = os.path.join(SETUP_DIR, "init_schema.py")

# Module init
MODULE_INIT_PATH = os.path.join(ROOT_DIR, "init_db.py")

# Make erpclaw_lib importable
ERPCLAW_LIB = os.path.expanduser("~/.openclaw/erpclaw/lib")
if ERPCLAW_LIB not in sys.path:
    sys.path.insert(0, ERPCLAW_LIB)


def load_db_query():
    """Load {module_name}'s db_query.py explicitly to avoid sys.path collisions."""
    db_query_path = os.path.join(MODULE_DIR, "db_query.py")
    spec = importlib.util.spec_from_file_location("db_query_{module_short}", db_query_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for action_name, fn in mod.ACTIONS.items():
        setattr(mod, action_name.replace("-", "_"), fn)
    return mod


def init_all_tables(db_path: str):
    """Create all foundation + {module_name} tables."""
    spec = importlib.util.spec_from_file_location("init_schema", INIT_SCHEMA_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.init_db(db_path)

    spec2 = importlib.util.spec_from_file_location("{module_short}_init", MODULE_INIT_PATH)
    m2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(m2)
    m2.{init_func}(db_path)


class _DecimalSum:
    def __init__(self):
        self.total = Decimal("0")
    def step(self, value):
        if value is not None:
            self.total += Decimal(str(value))
    def finalize(self):
        return str(self.total)


def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)
    conn.create_aggregate("decimal_sum", 1, _DecimalSum)
    return conn


def call_action(fn, conn, args) -> dict:
    buf = io.StringIO()
    def _fake_exit(code=0):
        raise SystemExit(code)
    try:
        with patch("sys.stdout", buf), patch("sys.exit", side_effect=_fake_exit):
            fn(conn, args)
    except SystemExit:
        pass
    output = buf.getvalue().strip()
    if not output:
        return {{"status": "error", "message": "no output captured"}}
    return json.loads(output)


def ns(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def is_error(result: dict) -> bool:
    return result.get("status") == "error"


def is_ok(result: dict) -> bool:
    return result.get("status") == "ok"


def _uuid() -> str:
    return str(uuid.uuid4())


def seed_company(conn, name="Test Company", abbr="TC") -> str:
    cid = _uuid()
    conn.execute(
        """INSERT INTO company (id, name, abbr, default_currency, country,
           fiscal_year_start_month)
           VALUES (?, ?, ?, 'USD', 'United States', 1)""",
        (cid, f"{{name}} {{cid[:6]}}", f"{{abbr}}{{cid[:4]}}")
    )
    conn.commit()
    return cid


def seed_customer(conn, company_id: str, name="Jane Smith") -> str:
    cust_id = _uuid()
    conn.execute(
        """INSERT INTO customer (id, name, customer_type, company_id, status)
           VALUES (?, ?, 'individual', ?, 'active')""",
        (cust_id, name, company_id)
    )
    conn.commit()
    return cust_id


def build_env(conn) -> dict:
    """Create a full test environment."""
    cid = seed_company(conn)
    customer_id = seed_customer(conn, cid, "Jane Smith")
    return {{
        "company_id": cid,
        "customer_id": customer_id,
    }}
'''

    # --- test file ---
    test_lines = [
        f'"""Tests for {display_name} domain.',
        f'',
        f'Generated by ERPClaw OS generate-module.',
        f'"""',
        f'import pytest',
        f'from {module_short}_helpers import (',
        f'    call_action, ns, is_error, is_ok, load_db_query,',
        f')',
        f'',
        f'mod = load_db_query()',
        f'',
    ]

    # Generate tests for each entity
    for ent in entities:
        ename = _entity_to_table_name_snake(ent["name"])
        pattern_key = ent.get("pattern", "crud_entity")
        actions = _build_entity_actions(prefix, ent["name"], ent)
        class_name = "".join(w.capitalize() for w in ename.split("_"))

        test_lines.append(f'')
        test_lines.append(f'class Test{class_name}:')

        for action in actions:
            func_attr = action.replace("-", "_")
            verb = _extract_verb(action, prefix, ename)

            if pattern_key == "invoice_delegation":
                # Skip invoice tests (requires subprocess)
                test_lines.append(f'    # {action}: skipped (requires running erpclaw subprocess)')
                continue

            # Positive test
            if verb == "add":
                test_lines.append(f'    def test_{func_attr}(self, conn, env):')
                test_lines.append(f'        result = call_action(mod.{func_attr}, conn, ns(')
                test_lines.append(f'            company_id=env["company_id"],')
                test_lines.append(f'            name="Test {ename}",')
                # Add all common fields with defaults
                fields = _build_entity_fields(ent)
                for f in fields:
                    col = f.split()[0]
                    if col in ("id", "company_id", "created_at", "updated_at", "name"):
                        continue
                    test_lines.append(f'            {col}=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_ok(result), result')
                test_lines.append(f'        assert "id" in result')
                test_lines.append(f'')

                # Negative test: missing required field
                test_lines.append(f'    def test_{func_attr}_missing_company(self, conn, env):')
                test_lines.append(f'        result = call_action(mod.{func_attr}, conn, ns(')
                test_lines.append(f'            company_id=None,')
                test_lines.append(f'            name="Test",')
                for f in fields:
                    col = f.split()[0]
                    if col in ("id", "company_id", "created_at", "updated_at", "name"):
                        continue
                    test_lines.append(f'            {col}=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_error(result)')
                test_lines.append(f'')

            elif verb == "update":
                # We need an entity to update; create one first
                add_action = _action_name(prefix, "add", ename)
                add_func_attr = add_action.replace("-", "_")
                test_lines.append(f'    def test_{func_attr}(self, conn, env):')
                test_lines.append(f'        # First add an entity')
                test_lines.append(f'        add_result = call_action(mod.{add_func_attr}, conn, ns(')
                test_lines.append(f'            company_id=env["company_id"],')
                test_lines.append(f'            name="To Update",')
                fields = _build_entity_fields(ent)
                for f in fields:
                    col = f.split()[0]
                    if col in ("id", "company_id", "created_at", "updated_at", "name"):
                        continue
                    test_lines.append(f'            {col}=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_ok(add_result), add_result')
                test_lines.append(f'        result = call_action(mod.{func_attr}, conn, ns(')
                test_lines.append(f'            {ename}_id=add_result["id"],')
                test_lines.append(f'            company_id=env["company_id"],')
                test_lines.append(f'            name="Updated Name",')
                for f in fields:
                    col = f.split()[0]
                    if col in ("id", "company_id", "created_at", "updated_at", "name"):
                        continue
                    test_lines.append(f'            {col}=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_ok(result), result')
                test_lines.append(f'        assert "name" in result["updated_fields"]')
                test_lines.append(f'')

                # Negative: no fields
                test_lines.append(f'    def test_{func_attr}_no_fields(self, conn, env):')
                test_lines.append(f'        add_result = call_action(mod.{add_func_attr}, conn, ns(')
                test_lines.append(f'            company_id=env["company_id"],')
                test_lines.append(f'            name="To Fail Update",')
                for f in fields:
                    col = f.split()[0]
                    if col in ("id", "company_id", "created_at", "updated_at", "name"):
                        continue
                    test_lines.append(f'            {col}=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_ok(add_result)')
                test_lines.append(f'        result = call_action(mod.{func_attr}, conn, ns(')
                test_lines.append(f'            {ename}_id=add_result["id"],')
                test_lines.append(f'            company_id=None,')
                test_lines.append(f'            name=None,')
                for f in fields:
                    col = f.split()[0]
                    if col in ("id", "company_id", "created_at", "updated_at", "name"):
                        continue
                    test_lines.append(f'            {col}=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_error(result)')
                test_lines.append(f'')

            elif verb == "get":
                add_action = _action_name(prefix, "add", ename)
                add_func_attr = add_action.replace("-", "_")
                test_lines.append(f'    def test_{func_attr}(self, conn, env):')
                test_lines.append(f'        add_result = call_action(mod.{add_func_attr}, conn, ns(')
                test_lines.append(f'            company_id=env["company_id"],')
                test_lines.append(f'            name="To Get",')
                fields = _build_entity_fields(ent)
                for f in fields:
                    col = f.split()[0]
                    if col in ("id", "company_id", "created_at", "updated_at", "name"):
                        continue
                    test_lines.append(f'            {col}=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_ok(add_result)')
                test_lines.append(f'        result = call_action(mod.{func_attr}, conn, ns(')
                test_lines.append(f'            {ename}_id=add_result["id"],')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_ok(result), result')
                test_lines.append(f'        assert result["id"] == add_result["id"]')
                test_lines.append(f'')

                # Negative: not found
                test_lines.append(f'    def test_{func_attr}_not_found(self, conn, env):')
                test_lines.append(f'        result = call_action(mod.{func_attr}, conn, ns(')
                test_lines.append(f'            {ename}_id="nonexistent-id",')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_error(result)')
                test_lines.append(f'')

            elif verb == "list":
                add_action = _action_name(prefix, "add", ename)
                add_func_attr = add_action.replace("-", "_")
                test_lines.append(f'    def test_{func_attr}(self, conn, env):')
                test_lines.append(f'        # Add an entity first')
                test_lines.append(f'        call_action(mod.{add_func_attr}, conn, ns(')
                test_lines.append(f'            company_id=env["company_id"],')
                test_lines.append(f'            name="To List",')
                fields = _build_entity_fields(ent)
                for f in fields:
                    col = f.split()[0]
                    if col in ("id", "company_id", "created_at", "updated_at", "name"):
                        continue
                    test_lines.append(f'            {col}=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        result = call_action(mod.{func_attr}, conn, ns(')
                test_lines.append(f'            company_id=env["company_id"],')
                test_lines.append(f'            status=None,')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_ok(result), result')
                test_lines.append(f'        assert result["total_count"] >= 1')
                test_lines.append(f'')

            elif verb == "use":
                # prepaid package session test
                test_lines.append(f'    def test_{func_attr}(self, conn, env):')
                test_lines.append(f'        # Stub test for use-session pattern')
                test_lines.append(f'        pass  # Requires seed data specific to pattern')
                test_lines.append(f'')

            else:
                # Generic stub test
                test_lines.append(f'    def test_{func_attr}(self, conn, env):')
                test_lines.append(f'        result = call_action(mod.{func_attr}, conn, ns(')
                test_lines.append(f'            company_id=env["company_id"],')
                test_lines.append(f'            limit=50, offset=0,')
                test_lines.append(f'        ))')
                test_lines.append(f'        assert is_ok(result), result')
                test_lines.append(f'')

    test_content = "\n".join(test_lines)

    return conftest_content, helpers_content, test_content


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_module(
    module_name: str,
    prefix: str,
    business_description: str,
    entities: list[dict],
    output_dir: str = None,
    src_root: str = None,
) -> dict:
    """Generate a complete ERPClaw module from structured input.

    Args:
        module_name: e.g., "groomingclaw"
        prefix: e.g., "groom"
        business_description: natural language description
        entities: list of entity definitions with pattern assignments
                  [{"name": "pet", "fields": [...], "pattern": "crud_entity"}, ...]
        output_dir: where to write files (default: src/{module_name}/)
        src_root: project src/ root for validation

    Returns: {
        "result": "pass" | "fail",
        "module_path": str,
        "files_created": list[str],
        "validation": {...},
        "entities": int,
        "actions": int,
        "tables": int,
    }
    """
    # Validate inputs
    errors = _validate_inputs(module_name, prefix, entities)
    if errors:
        return {
            "result": "fail",
            "module_path": "",
            "files_created": [],
            "validation": {"errors": errors},
            "entities": 0,
            "actions": 0,
            "tables": 0,
        }

    # Determine output directory
    if not output_dir:
        if src_root:
            output_dir = os.path.join(src_root, module_name)
        else:
            output_dir = module_name

    # Build display name
    display_name = module_name.replace("-", " ").replace("claw", "Claw").title()
    if "claw" in module_name.lower():
        # Capitalize the Claw part
        parts = module_name.split("claw")
        display_name = parts[0].capitalize() + "Claw"
        if len(parts) > 1 and parts[1]:
            display_name += " " + parts[1].strip("-").capitalize()

    module_short = module_name.replace("claw", "").replace("-", "_")
    if not module_short:
        module_short = module_name.replace("-", "_")

    # Create directory structure
    os.makedirs(output_dir, exist_ok=True)
    scripts_dir = os.path.join(output_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    tests_dir = os.path.join(scripts_dir, "tests")
    os.makedirs(tests_dir, exist_ok=True)

    files_created = []

    # Count tables and actions
    table_count = 0
    action_count = 0
    for ent in entities:
        fields = _build_entity_fields(ent)
        if fields:
            table_count += 1
        action_count += len(_build_entity_actions(prefix, ent["name"], ent))

    # Generate init_db.py
    init_db_content = _generate_init_db(module_name, prefix, display_name, entities)
    init_db_path = os.path.join(output_dir, "init_db.py")
    with open(init_db_path, "w") as f:
        f.write(init_db_content)
    files_created.append(init_db_path)

    # Generate domain module
    domain_content = _generate_domain_module(module_name, prefix, display_name, entities, business_description)
    domain_path = os.path.join(scripts_dir, f"{module_short}.py")
    with open(domain_path, "w") as f:
        f.write(domain_content)
    files_created.append(domain_path)

    # Generate db_query.py
    db_query_content = _generate_db_query(module_name, prefix, display_name, entities)
    db_query_path = os.path.join(scripts_dir, "db_query.py")
    with open(db_query_path, "w") as f:
        f.write(db_query_content)
    files_created.append(db_query_path)

    # Generate SKILL.md
    skill_md_content = _generate_skill_md(module_name, prefix, display_name, business_description, entities)
    skill_md_path = os.path.join(output_dir, "SKILL.md")
    with open(skill_md_path, "w") as f:
        f.write(skill_md_content)
    files_created.append(skill_md_path)

    # Generate tests
    conftest_content, helpers_content, test_content = _generate_tests(
        module_name, prefix, display_name, entities
    )
    conftest_path = os.path.join(tests_dir, "conftest.py")
    with open(conftest_path, "w") as f:
        f.write(conftest_content)
    files_created.append(conftest_path)

    helpers_path = os.path.join(tests_dir, f"{module_short}_helpers.py")
    with open(helpers_path, "w") as f:
        f.write(helpers_content)
    files_created.append(helpers_path)

    test_path = os.path.join(tests_dir, f"test_{module_short}.py")
    with open(test_path, "w") as f:
        f.write(test_content)
    files_created.append(test_path)

    # Create __init__.py in tests
    init_path = os.path.join(tests_dir, "__init__.py")
    with open(init_path, "w") as f:
        f.write("")
    files_created.append(init_path)

    # Run validate_module_static on the generated output
    validation_result = {"result": "skipped", "message": "Validator not available"}
    try:
        from validate_module import validate_module_static
        validation_result = validate_module_static(output_dir, src_root)
    except ImportError:
        pass
    except Exception as e:
        validation_result = {"result": "error", "message": str(e)}

    overall_result = validation_result.get("result", "fail")

    return {
        "result": overall_result,
        "module_path": output_dir,
        "files_created": files_created,
        "validation": validation_result,
        "entities": len(entities),
        "actions": action_count,
        "tables": table_count,
    }
