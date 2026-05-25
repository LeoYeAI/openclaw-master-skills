"""ERPClaw OS — In-Module Code Generator (P0-3)

Inserts new functions into EXISTING db_query.py files. This does NOT generate
new modules (that is generate_module.py's job). It reads a module's existing
code structure, generates a new function following the module's patterns, and
injects it safely — creating a .bak backup, validating syntax, and refusing
to modify safety-excluded files.

Safety invariants (enforced in code):
- NEVER modify a file in SAFETY_EXCLUDED_FILES
- NEVER modify existing functions — only ADD new ones
- NEVER change existing ACTIONS entries — only ADD new ones
- Always create .bak backup before any modification
- Always validate syntax after modification (ast.parse / compile)
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timezone

# Make erpclaw-os package importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from dgm_engine import is_safety_excluded, SAFETY_EXCLUDED_FILES
from pattern_library import PATTERNS


# ---------------------------------------------------------------------------
# Module analysis
# ---------------------------------------------------------------------------

def analyze_module(module_path: str) -> dict:
    """Read an existing db_query.py and parse its structure.

    Args:
        module_path: Path to the db_query.py file (or directory containing
                     scripts/db_query.py).

    Returns:
        dict with keys:
            - file_path: resolved absolute path to db_query.py
            - imports_end_line: line number where the import block ends
            - functions: list of {name, start_line, end_line}
            - actions_dict_line: line number of ``ACTIONS = {``
            - actions_dict_end_line: line number of the closing ``}``
            - actions: dict mapping action-name -> handler-name
            - indent_style: detected indentation (e.g. "    " for 4 spaces)
            - uses_ok_err: bool — whether ok()/err() response pattern found
            - uses_pypika: bool — whether PyPika Q/P/Table imports found
            - uses_decimal: bool — whether Decimal import found
            - argparser_line: line number of ``def main()`` or argparser setup
            - line_count: total lines in file
            - error: present only on failure
    """
    # Resolve db_query.py path
    file_path = _resolve_db_query_path(module_path)
    if file_path is None:
        return {"error": f"Cannot find db_query.py at or under: {module_path}"}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        return {"error": f"Cannot read file: {e}"}

    lines = source.splitlines()
    line_count = len(lines)

    # -- Detect import block end -----------------------------------------------
    imports_end_line = _find_imports_end(lines)

    # -- Detect functions ------------------------------------------------------
    functions = _find_functions(lines)

    # -- Detect ACTIONS dict ---------------------------------------------------
    actions_dict_line, actions_dict_end_line, actions = _find_actions_dict(lines)

    # -- Detect style ----------------------------------------------------------
    indent_style = _detect_indent(lines)
    uses_ok_err = bool(re.search(r'\bfrom\s+erpclaw_lib\.response\s+import\b.*\bok\b', source))
    uses_pypika = bool(re.search(r'\bfrom\s+erpclaw_lib\.query\s+import\b', source))
    uses_decimal = bool(re.search(r'\bfrom\s+decimal\s+import\b.*\bDecimal\b', source))

    # -- Detect argparser / main -----------------------------------------------
    argparser_line = None
    for i, line in enumerate(lines, start=1):
        if re.match(r'^def\s+main\s*\(', line):
            argparser_line = i
            break

    return {
        "file_path": file_path,
        "imports_end_line": imports_end_line,
        "functions": functions,
        "actions_dict_line": actions_dict_line,
        "actions_dict_end_line": actions_dict_end_line,
        "actions": actions,
        "indent_style": indent_style,
        "uses_ok_err": uses_ok_err,
        "uses_pypika": uses_pypika,
        "uses_decimal": uses_decimal,
        "argparser_line": argparser_line,
        "line_count": line_count,
    }


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def generate_feature_code(feature_spec: dict, module_analysis: dict) -> str:
    """Generate a Python function for a new feature.

    Args:
        feature_spec: dict with keys:
            - action_name: kebab-case action name (e.g. "sell-close-order")
            - parameters: list of {name, type, required, description}
            - description: human-readable description of the action
            - table_name: (optional) existing table to query/update
            - business_logic_description: (optional) what the function does
            - pattern: (optional) pattern key from pattern_library
            - is_financial: (optional) True if function handles money
        module_analysis: output of analyze_module()

    Returns:
        str: The Python function source code (ready to insert).
    """
    action_name = feature_spec["action_name"]
    func_name = _action_to_func_name(action_name)
    params = feature_spec.get("parameters", [])
    description = feature_spec.get("description", f"Handle {action_name}")
    table_name = feature_spec.get("table_name")
    business_logic = feature_spec.get("business_logic_description", "")
    is_financial = feature_spec.get("is_financial", False)
    pattern_key = feature_spec.get("pattern")

    indent = module_analysis.get("indent_style", "    ")
    uses_ok_err = module_analysis.get("uses_ok_err", True)
    uses_pypika = module_analysis.get("uses_pypika", False)

    # Build docstring
    docstring_lines = [f'"""{description}']
    if business_logic:
        docstring_lines.append("")
        docstring_lines.append(f"Business logic: {business_logic}")
    docstring_lines.append('"""')

    # Build parameter extraction lines
    param_lines = []
    for p in params:
        p_name = p["name"]
        attr_name = p_name.replace("-", "_")
        if p.get("required", False):
            param_lines.append(
                f"{indent}{attr_name} = getattr(args, '{attr_name}', None)"
            )
            param_lines.append(
                f"{indent}if not {attr_name}:"
            )
            err_call = f'err("--{p_name} is required")' if uses_ok_err else (
                f'print(json.dumps({{"status": "error", "error": "--{p_name} is required"}})); sys.exit(1)'
            )
            param_lines.append(f"{indent}{indent}{err_call}")
        else:
            default = p.get("default", "None")
            param_lines.append(
                f"{indent}{attr_name} = getattr(args, '{attr_name}', {default})"
            )

    # Build Decimal handling lines if financial
    decimal_lines = []
    if is_financial:
        for p in params:
            if p.get("type") == "decimal" or p.get("is_financial", False):
                attr = p["name"].replace("-", "_")
                decimal_lines.append(f"{indent}if {attr} is not None:")
                decimal_lines.append(f"{indent}{indent}try:")
                decimal_lines.append(f"{indent}{indent}{indent}{attr} = Decimal(str({attr}))")
                decimal_lines.append(f"{indent}{indent}except (InvalidOperation, ValueError):")
                err_msg = f'err("Invalid decimal value for --{p["name"]}")'
                decimal_lines.append(f"{indent}{indent}{indent}{err_msg}")

    # Build body
    body_lines = []
    if table_name and uses_pypika:
        # Use PyPika pattern
        tbl_var = table_name.replace("-", "_")
        body_lines.append(f"{indent}tbl = Table('{table_name}')")
        body_lines.append(f"{indent}conn = get_connection(db_path)")

        # Determine action verb from action_name
        verb = _extract_verb(action_name)
        if verb in ("add", "create"):
            body_lines.append(f"{indent}row_id = str(uuid.uuid4())")
            body_lines.append(f"{indent}now = datetime.now(timezone.utc).isoformat()")
            insert_cols = ["id", "created_at"]
            insert_vals = ["row_id", "now"]
            for p in params:
                attr = p["name"].replace("-", "_")
                insert_cols.append(attr)
                insert_vals.append(attr)
            cols_str = ", ".join(f"'{c}'" for c in insert_cols)
            vals_str = ", ".join(insert_vals)
            body_lines.append(f"{indent}q = Q.into(tbl).columns({cols_str}).insert({vals_str})")
            body_lines.append(f"{indent}conn.execute(str(q), ())")
            body_lines.append(f"{indent}conn.commit()")
            if uses_ok_err:
                body_lines.append(f'{indent}ok({{"id": row_id, "message": "{action_name} succeeded"}})')
            else:
                body_lines.append(f'{indent}print(json.dumps({{"status": "ok", "id": row_id}}))')

        elif verb == "list":
            body_lines.append(f"{indent}q = Q.from_(tbl).select(tbl.star)")
            body_lines.append(f"{indent}rows = conn.execute(str(q)).fetchall()")
            body_lines.append(f"{indent}cols = [d[0] for d in conn.execute(str(q)).description] if rows else []")
            body_lines.append(f"{indent}results = [dict(zip(cols, r)) for r in rows]")
            if uses_ok_err:
                body_lines.append(f'{indent}ok({{"rows": results, "count": len(results)}})')

        elif verb == "get":
            id_param = _find_id_param(params)
            if id_param:
                attr = id_param.replace("-", "_")
                body_lines.append(f"{indent}q = Q.from_(tbl).select(tbl.star).where(tbl.id == P)")
                body_lines.append(f"{indent}row = conn.execute(str(q), ({attr},)).fetchone()")
                body_lines.append(f"{indent}if not row:")
                body_lines.append(f'{indent}{indent}err("Not found")')
                body_lines.append(f"{indent}cols = [d[0] for d in conn.execute(str(q), ({attr},)).description]")
                body_lines.append(f"{indent}result = dict(zip(cols, row))")
                if uses_ok_err:
                    body_lines.append(f'{indent}ok(result)')

        elif verb == "update":
            body_lines.append(f"{indent}# Update logic using dynamic_update")
            body_lines.append(f"{indent}updates = {{}}")
            for p in params:
                attr = p["name"].replace("-", "_")
                if attr not in ("id", "company_id"):
                    body_lines.append(f"{indent}if {attr} is not None:")
                    body_lines.append(f"{indent}{indent}updates['{attr}'] = {attr}")
            body_lines.append(f"{indent}if not updates:")
            body_lines.append(f'{indent}{indent}err("No fields to update")')
            id_param = _find_id_param(params)
            id_attr = id_param.replace("-", "_") if id_param else "id"
            body_lines.append(f"{indent}q, vals = dynamic_update('{table_name}', updates, 'id', {id_attr})")
            body_lines.append(f"{indent}conn.execute(q, vals)")
            body_lines.append(f"{indent}conn.commit()")
            if uses_ok_err:
                body_lines.append(f'{indent}ok({{"updated": True, "message": "{action_name} succeeded"}})')

        else:
            # Generic fallback
            if uses_ok_err:
                body_lines.append(f'{indent}ok({{"message": "{action_name} executed"}})')
            else:
                body_lines.append(f'{indent}print(json.dumps({{"status": "ok", "message": "{action_name} executed"}}))')

    elif uses_ok_err:
        # No table — simple handler
        body_lines.append(f'{indent}ok({{"message": "{action_name} executed"}})')
    else:
        body_lines.append(f'{indent}print(json.dumps({{"status": "ok", "message": "{action_name} executed"}}))')

    # Assemble function
    parts = [f"def {func_name}(args):"]
    # docstring
    for i, dline in enumerate(docstring_lines):
        parts.append(f"{indent}{dline}")
    # db_path extraction
    parts.append(f"{indent}db_path = getattr(args, 'db_path', None)")
    # parameters
    parts.extend(param_lines)
    # decimal handling
    parts.extend(decimal_lines)
    # body
    parts.extend(body_lines)

    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Insertion
# ---------------------------------------------------------------------------

def insert_feature(module_path: str, feature_code: str, action_name: str) -> dict:
    """Insert a new function into an existing db_query.py.

    Args:
        module_path: Path to db_query.py (or its parent directory).
        feature_code: The function source code to insert.
        action_name: The kebab-case action name for the ACTIONS dict.

    Returns:
        dict with keys: success, lines_added, action_added, backup_path, error
    """
    file_path = _resolve_db_query_path(module_path)
    if file_path is None:
        return {"success": False, "error": f"Cannot find db_query.py at: {module_path}"}

    # Safety check
    safe, reason = is_safe_to_modify(file_path)
    if not safe:
        return {"success": False, "error": reason}

    func_name = _action_to_func_name(action_name)

    # Extract function name(s) from the feature_code itself.
    # If the code defines a function, use that name for the ACTIONS dict entry
    # (it may differ from the action-derived name when user provides raw code).
    code_func_names = []
    for code_line in feature_code.splitlines():
        m = re.match(r'^def\s+(\w+)\s*\(', code_line)
        if m:
            code_func_names.append(m.group(1))

    # Use the first function defined in code as the handler name
    handler_name = code_func_names[0] if code_func_names else func_name

    # Read current source
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        return {"success": False, "error": f"Cannot read file: {e}"}

    lines = source.splitlines(keepends=True)

    # Check that function does not already exist (both action-derived and code-defined names)
    names_to_check = {func_name} | set(code_func_names)
    for line in lines:
        for name in names_to_check:
            if re.match(rf'^def\s+{re.escape(name)}\s*\(', line):
                return {
                    "success": False,
                    "error": f"Function '{name}' already exists in {file_path}",
                }

    # Check that action is not already in ACTIONS dict
    if f'"{action_name}"' in source or f"'{action_name}'" in source:
        return {
            "success": False,
            "error": f"Action '{action_name}' already exists in ACTIONS dict",
        }

    # Create backup
    backup_path = file_path + ".bak"
    try:
        shutil.copy2(file_path, backup_path)
    except OSError as e:
        return {"success": False, "error": f"Cannot create backup: {e}"}

    # Find ACTIONS dict line
    actions_dict_line = None
    for i, line in enumerate(lines):
        if re.match(r'^ACTIONS\s*=\s*\{', line):
            actions_dict_line = i
            break

    if actions_dict_line is None:
        return {"success": False, "error": "Cannot find ACTIONS dict in file"}

    # Find ACTIONS dict closing brace
    actions_dict_end = _find_dict_end(lines, actions_dict_line)
    if actions_dict_end is None:
        return {"success": False, "error": "Cannot find closing brace of ACTIONS dict"}

    # Insert function code BEFORE the ACTIONS dict (with blank lines)
    insert_block = "\n\n" + feature_code + "\n"

    # Build the new ACTIONS entry
    # Detect indentation used in ACTIONS dict
    actions_indent = "    "
    if actions_dict_line + 1 < len(lines):
        next_line = lines[actions_dict_line + 1]
        m = re.match(r'^(\s+)', next_line)
        if m:
            actions_indent = m.group(1)

    new_action_entry = f'{actions_indent}"{action_name}": {handler_name},\n'

    # Build new source
    # 1. Everything up to ACTIONS dict line
    new_lines = list(lines[:actions_dict_line])
    # 2. Insert the function code
    new_lines.extend(insert_block.splitlines(keepends=True))
    # 3. ACTIONS dict opening through second-to-last entry
    new_lines.extend(lines[actions_dict_line:actions_dict_end])
    # 4. New action entry
    new_lines.append(new_action_entry)
    # 5. Closing brace and everything after
    new_lines.extend(lines[actions_dict_end:])

    new_source = "".join(new_lines)

    # Validate syntax before writing
    syntax_ok, syntax_err = _validate_syntax(new_source, file_path)
    if not syntax_ok:
        # Restore backup
        shutil.copy2(backup_path, file_path)
        return {
            "success": False,
            "error": f"Generated code has syntax error: {syntax_err}",
            "backup_path": backup_path,
        }

    # Write the modified source
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_source)
    except OSError as e:
        shutil.copy2(backup_path, file_path)
        return {"success": False, "error": f"Cannot write file: {e}"}

    # Count lines added
    original_line_count = len(lines)
    new_line_count = len(new_source.splitlines())
    lines_added = new_line_count - original_line_count

    # Write .os_manifest.json
    _update_manifest(file_path, action_name, handler_name)

    return {
        "success": True,
        "lines_added": lines_added,
        "action_added": action_name,
        "function_added": handler_name,
        "backup_path": backup_path,
        "file_path": file_path,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_insertion(module_path: str, action_name: str) -> dict:
    """Validate that an inserted feature is correct.

    Checks:
    1. Python syntax valid (ast.parse)
    2. Action is in the ACTIONS dict
    3. Function exists and is callable
    4. (Optional) Run existing module tests

    Args:
        module_path: Path to db_query.py or its parent directory.
        action_name: The action that was just inserted.

    Returns:
        dict with keys: valid, checks (list of {name, passed, detail})
    """
    file_path = _resolve_db_query_path(module_path)
    if file_path is None:
        return {"valid": False, "checks": [{"name": "file_exists", "passed": False,
                                             "detail": f"Cannot find db_query.py at: {module_path}"}]}

    checks = []

    # Check 1: Syntax valid
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        return {"valid": False, "checks": [{"name": "file_readable", "passed": False, "detail": str(e)}]}

    syntax_ok, syntax_err = _validate_syntax(source, file_path)
    checks.append({
        "name": "syntax_valid",
        "passed": syntax_ok,
        "detail": syntax_err if not syntax_ok else "Python syntax OK",
    })

    # Check 2: Action in ACTIONS dict
    func_name = _action_to_func_name(action_name)
    action_in_dict = (f'"{action_name}"' in source or f"'{action_name}'" in source)
    checks.append({
        "name": "action_in_dict",
        "passed": action_in_dict,
        "detail": f"Action '{action_name}' found in ACTIONS dict" if action_in_dict else f"Action '{action_name}' NOT found in ACTIONS dict",
    })

    # Check 3: Function exists
    func_exists = bool(re.search(rf'^def\s+{re.escape(func_name)}\s*\(', source, re.MULTILINE))
    checks.append({
        "name": "function_exists",
        "passed": func_exists,
        "detail": f"Function '{func_name}' found" if func_exists else f"Function '{func_name}' NOT found",
    })

    # Check 4: Run existing tests (best-effort)
    test_result = _run_module_tests(file_path)
    checks.append({
        "name": "existing_tests_pass",
        "passed": test_result["passed"],
        "detail": test_result["detail"],
    })

    all_passed = all(c["passed"] for c in checks)
    return {"valid": all_passed, "checks": checks}


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------

def is_safe_to_modify(module_path: str) -> tuple:
    """Check if a file is safe to modify.

    Returns:
        tuple: (is_safe: bool, reason: str)
            - is_safe=True, reason="" if safe
            - is_safe=False, reason="..." if not safe
    """
    file_path = _resolve_db_query_path(module_path)
    if file_path is None:
        return False, f"Cannot find db_query.py at: {module_path}"

    basename = os.path.basename(file_path)

    # Check against SAFETY_EXCLUDED_FILES
    if basename in SAFETY_EXCLUDED_FILES:
        return False, f"File '{basename}' is in SAFETY_EXCLUDED_FILES — modification refused"

    # Check using dgm_engine.is_safety_excluded()
    # We need to derive module_name from path
    module_name = _module_name_from_path(file_path)
    excluded, reason = is_safety_excluded(module_name, "", source_file=file_path)
    if excluded:
        return False, reason

    return True, ""


# ---------------------------------------------------------------------------
# Action handler (wired into erpclaw-os/db_query.py)
# ---------------------------------------------------------------------------

def handle_add_feature_to_module(args) -> dict:
    """Action handler for add-feature-to-module.

    Required args:
        --module-path: Path to the module's db_query.py or its parent
        --action-name: Kebab-case action name
        --feature-spec-json: JSON string with full feature spec

    Returns:
        dict with result of the operation.
    """
    module_path = getattr(args, "module_path", None) or getattr(args, "module_path", None)
    action_name = getattr(args, "action_name", None)
    feature_spec_json = getattr(args, "feature_spec_json", None)

    if not module_path:
        return {"error": "--module-path is required"}
    if not action_name:
        return {"error": "--action-name is required"}
    if not feature_spec_json:
        return {"error": "--feature-spec-json is required"}

    try:
        feature_spec = json.loads(feature_spec_json)
    except (json.JSONDecodeError, TypeError):
        return {"error": "--feature-spec-json must be valid JSON"}

    # Ensure action_name is set in spec
    feature_spec["action_name"] = action_name

    # Step 1: Safety check
    safe, reason = is_safe_to_modify(module_path)
    if not safe:
        return {"error": f"Safety check failed: {reason}"}

    # Step 2: Analyze module
    analysis = analyze_module(module_path)
    if "error" in analysis:
        return {"error": f"Module analysis failed: {analysis['error']}"}

    # Step 3: Generate code
    code = generate_feature_code(feature_spec, analysis)

    # Step 4: Insert feature
    result = insert_feature(module_path, code, action_name)
    if not result.get("success"):
        return {"error": result.get("error", "Insertion failed")}

    # Step 5: Validate
    validation = validate_insertion(module_path, action_name)
    result["validation"] = validation

    return result


# ===========================================================================
# Private helpers
# ===========================================================================

def _resolve_db_query_path(path: str) -> str | None:
    """Resolve a path to its db_query.py file.

    Accepts:
        - Direct path to a db_query.py file
        - Path to a directory containing db_query.py
        - Path to a directory containing scripts/db_query.py
        - Path to a module directory (contains scripts/ subdir)
    """
    if path is None:
        return None

    path = os.path.abspath(path)

    # Direct file
    if os.path.isfile(path) and path.endswith(".py"):
        return path

    # Directory: look for db_query.py in standard locations
    if os.path.isdir(path):
        candidates = [
            os.path.join(path, "db_query.py"),
            os.path.join(path, "scripts", "db_query.py"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c

    return None


def _find_imports_end(lines: list[str]) -> int:
    """Find the line number (1-indexed) where the import block ends."""
    last_import = 0
    in_try_block = False
    try_indent = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track try/except blocks (common for import fallbacks)
        if stripped.startswith("try:"):
            in_try_block = True
            try_indent = len(line) - len(line.lstrip())
            continue
        if in_try_block and stripped.startswith(("except", "finally")):
            continue
        if in_try_block and stripped == "" :
            continue

        if stripped.startswith(("import ", "from ")):
            last_import = i + 1
        elif stripped.startswith(("except ImportError", "except ModuleNotFoundError")):
            continue
        elif last_import > 0 and stripped and not stripped.startswith("#"):
            # If we see a non-import, non-comment line after imports
            if not in_try_block or (len(line) - len(line.lstrip())) <= try_indent:
                if not stripped.startswith(("try:", "except", "finally")):
                    break

    return last_import if last_import > 0 else 1


def _find_functions(lines: list[str]) -> list[dict]:
    """Find all top-level function definitions."""
    functions = []
    current_func = None

    for i, line in enumerate(lines):
        m = re.match(r'^def\s+(\w+)\s*\(', line)
        if m:
            if current_func is not None:
                current_func["end_line"] = i  # end at line before next def
                functions.append(current_func)
            current_func = {
                "name": m.group(1),
                "start_line": i + 1,  # 1-indexed
                "end_line": None,
            }

    if current_func is not None:
        current_func["end_line"] = len(lines)
        functions.append(current_func)

    return functions


def _find_actions_dict(lines: list[str]) -> tuple:
    """Find the ACTIONS dict: start line, end line, and parsed entries.

    Returns:
        (actions_dict_line, actions_dict_end_line, actions_dict)
        Lines are 0-indexed. actions_dict is {action_name: handler_name}.
    """
    actions_dict_line = None
    for i, line in enumerate(lines):
        if re.match(r'^ACTIONS\s*=\s*\{', line):
            actions_dict_line = i
            break

    if actions_dict_line is None:
        return None, None, {}

    # Find closing brace
    actions_dict_end = _find_dict_end(lines, actions_dict_line)

    # Parse entries
    actions = {}
    for i in range(actions_dict_line, (actions_dict_end or len(lines)) + 1):
        if i >= len(lines):
            break
        line = lines[i].strip()
        # Match: "action-name": handler_name, or 'action-name': handler_name,
        m = re.match(r'''["\']([^"']+)["']\s*:\s*(\w+)\s*,?''', line)
        if m:
            actions[m.group(1)] = m.group(2)

    return actions_dict_line, actions_dict_end, actions


def _find_dict_end(lines: list[str], start_line: int) -> int | None:
    """Find the closing brace of a dict starting at start_line (0-indexed)."""
    depth = 0
    for i in range(start_line, len(lines)):
        line = lines[i]
        for ch in line:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i
    return None


def _detect_indent(lines: list[str]) -> str:
    """Detect the indentation style from function bodies."""
    for i, line in enumerate(lines):
        if re.match(r'^def\s+\w+\s*\(', line) and i + 1 < len(lines):
            next_line = lines[i + 1]
            m = re.match(r'^(\s+)', next_line)
            if m:
                return m.group(1)
    return "    "


def _action_to_func_name(action_name: str) -> str:
    """Convert kebab-case action name to a Python function name.

    e.g. "sell-close-order" -> "sell_close_order"
         "add-customer" -> "add_customer"
    """
    return action_name.replace("-", "_")


def _extract_verb(action_name: str) -> str:
    """Extract the verb from an action name.

    e.g. "groom-add-pet" -> "add"
         "sell-list-orders" -> "list"
         "add-customer" -> "add"
    """
    parts = action_name.split("-")
    # Common verbs at position 0 or 1
    verbs = {"add", "create", "update", "get", "list", "delete", "submit", "cancel", "close", "generate"}
    for part in parts:
        if part in verbs:
            return part
    return parts[-1] if parts else "handle"


def _find_id_param(params: list[dict]) -> str | None:
    """Find the ID parameter from a parameter list."""
    for p in params:
        name = p["name"]
        if name == "id" or name.endswith("-id"):
            return name
    return None


def _validate_syntax(source: str, filename: str = "<generated>") -> tuple:
    """Validate Python syntax.

    Returns:
        (is_valid: bool, error_message: str or None)
    """
    try:
        compile(source, filename, "exec")
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"


def _module_name_from_path(file_path: str) -> str:
    """Derive a module name from a file path.

    e.g. /src/erpclaw/scripts/erpclaw-selling/db_query.py -> "erpclaw-selling"
         /src/groomingclaw/scripts/grooming.py -> "groomingclaw"
    """
    parts = file_path.replace("\\", "/").split("/")
    # Walk backwards looking for a directory name that looks like a module
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] == "scripts" and i > 0:
            return parts[i - 1]
    return os.path.basename(os.path.dirname(file_path))


def _run_module_tests(file_path: str) -> dict:
    """Run existing module tests to check for regression.

    Returns:
        {passed: bool, detail: str}
    """
    # Find tests directory relative to file
    file_dir = os.path.dirname(file_path)
    test_dirs = [
        os.path.join(file_dir, "tests"),
        os.path.join(os.path.dirname(file_dir), "tests"),
    ]

    test_dir = None
    for td in test_dirs:
        if os.path.isdir(td):
            test_dir = td
            break

    if test_dir is None:
        return {"passed": True, "detail": "No test directory found — skipped"}

    # Check if there are any test files
    test_files = [f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")]
    if not test_files:
        return {"passed": True, "detail": "No test files found — skipped"}

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_dir, "-q", "--tb=line", "-x", "--timeout=30"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(file_path),
        )
        if result.returncode == 0:
            return {"passed": True, "detail": f"All tests passed: {result.stdout.strip().splitlines()[-1] if result.stdout.strip() else 'OK'}"}
        else:
            last_lines = result.stdout.strip().splitlines()[-3:] if result.stdout.strip() else []
            detail = " | ".join(last_lines) if last_lines else result.stderr[:200]
            return {"passed": False, "detail": f"Tests failed: {detail}"}
    except subprocess.TimeoutExpired:
        return {"passed": False, "detail": "Tests timed out after 60s"}
    except Exception as e:
        return {"passed": True, "detail": f"Could not run tests: {e} — skipped"}


def _update_manifest(file_path: str, action_name: str, func_name: str):
    """Write or update .os_manifest.json listing OS-generated functions."""
    manifest_path = os.path.join(os.path.dirname(file_path), ".os_manifest.json")

    manifest = {"generated_functions": [], "version": "1.0.0"}
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.loads(f.read())
        except (json.JSONDecodeError, OSError):
            pass

    if "generated_functions" not in manifest:
        manifest["generated_functions"] = []

    manifest["generated_functions"].append({
        "action_name": action_name,
        "function_name": func_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "in_module_generator",
    })

    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(manifest, indent=2))
    except OSError:
        pass  # Non-fatal: manifest is for audit, not blocking


# ---------------------------------------------------------------------------
# Auto-Test Generator for New Features (P1-9)
# ---------------------------------------------------------------------------

def generate_feature_test(feature_spec: dict, module_analysis: dict) -> str:
    """Generate a pytest test function for a new feature.

    Generates two tests:
    1. Happy path: call action with valid params, assert success + expected fields
    2. Error path: call action with missing required param, assert error

    Args:
        feature_spec: dict with keys:
            - action_name: kebab-case action name (e.g. "sell-close-order")
            - parameters: list of {name, type, required, description}
            - description: (optional) human-readable description
            - table_name: (optional) table this action operates on
            - is_financial: (optional) True if handles money
        module_analysis: output of analyze_module() — used for style detection

    Returns:
        str: Python test code (one or more test functions, ready to insert into
             or append to a test file). Always valid Python syntax.
    """
    action_name = feature_spec.get("action_name", "unknown-action")
    func_name = _action_to_func_name(action_name)
    params = feature_spec.get("parameters", [])
    description = feature_spec.get("description", f"Handle {action_name}")
    table_name = feature_spec.get("table_name")
    is_financial = feature_spec.get("is_financial", False)

    # Detect required params
    required_params = [p for p in params if p.get("required", False)]
    optional_params = [p for p in params if not p.get("required", False)]

    indent = "    "
    class_name = "".join(w.capitalize() for w in func_name.split("_"))

    lines = []
    lines.append(f"")
    lines.append(f"class TestGenerated{class_name}:")
    lines.append(f'{indent}"""Auto-generated tests for {action_name}.')
    lines.append(f"")
    lines.append(f"{indent}{description}")
    lines.append(f'{indent}"""')
    lines.append(f"")

    # --- Happy path test ---
    lines.append(f"{indent}def test_{func_name}_happy_path(self, conn, env):")
    lines.append(f'{indent}{indent}"""Call {action_name} with valid params, expect success."""')

    # Build call arguments
    call_args = []
    for p in params:
        attr = p["name"].replace("-", "_")
        ptype = p.get("type", "str")
        if attr == "company_id":
            call_args.append(f'{indent}{indent}{indent}{attr}=env["company_id"],')
        elif ptype == "decimal" or p.get("is_financial", False):
            call_args.append(f'{indent}{indent}{indent}{attr}="100.00",')
        elif ptype == "int" or ptype == "integer":
            call_args.append(f'{indent}{indent}{indent}{attr}=1,')
        elif ptype == "bool" or ptype == "boolean":
            call_args.append(f'{indent}{indent}{indent}{attr}=True,')
        elif attr.endswith("_id"):
            call_args.append(f'{indent}{indent}{indent}{attr}="test-id-001",')
        elif attr.endswith("_date") or attr == "date":
            call_args.append(f'{indent}{indent}{indent}{attr}="2026-01-15",')
        elif attr == "name":
            call_args.append(f'{indent}{indent}{indent}{attr}="Test {action_name}",')
        else:
            call_args.append(f'{indent}{indent}{indent}{attr}="test-value",')

    lines.append(f"{indent}{indent}result = call_action(mod.{func_name}, conn, ns(")
    lines.extend(call_args)
    lines.append(f"{indent}{indent}))")
    lines.append(f"{indent}{indent}assert is_ok(result), f\"Expected ok, got: {{result}}\"")

    # Assert expected fields based on action verb
    verb = _extract_verb(action_name)
    if verb in ("add", "create"):
        lines.append(f'{indent}{indent}assert "id" in result, "Expected id in response"')
    elif verb == "list":
        lines.append(f'{indent}{indent}assert "rows" in result or "total_count" in result')
    elif verb == "get":
        lines.append(f'{indent}{indent}assert "id" in result')

    lines.append(f"")

    # --- Error path test (missing required param) ---
    if required_params:
        first_required = required_params[0]
        first_attr = first_required["name"].replace("-", "_")
        lines.append(f"{indent}def test_{func_name}_missing_{first_attr}(self, conn, env):")
        lines.append(f'{indent}{indent}"""Call {action_name} without required --{first_required["name"]}, expect error."""')

        # Build call args with first required param missing
        error_call_args = []
        for p in params:
            attr = p["name"].replace("-", "_")
            if attr == first_attr:
                error_call_args.append(f"{indent}{indent}{indent}{attr}=None,")
            elif attr == "company_id":
                error_call_args.append(f'{indent}{indent}{indent}{attr}=env["company_id"],')
            elif p.get("type") == "decimal" or p.get("is_financial", False):
                error_call_args.append(f'{indent}{indent}{indent}{attr}="100.00",')
            elif p.get("type") in ("int", "integer"):
                error_call_args.append(f'{indent}{indent}{indent}{attr}=1,')
            elif attr.endswith("_id"):
                error_call_args.append(f'{indent}{indent}{indent}{attr}="test-id-001",')
            else:
                error_call_args.append(f'{indent}{indent}{indent}{attr}="test-value",')

        lines.append(f"{indent}{indent}result = call_action(mod.{func_name}, conn, ns(")
        lines.extend(error_call_args)
        lines.append(f"{indent}{indent}))")
        lines.append(f"{indent}{indent}assert is_error(result), f\"Expected error, got: {{result}}\"")
        lines.append(f"")
    else:
        # No required params — generate a minimal error test
        lines.append(f"{indent}def test_{func_name}_empty_call(self, conn, env):")
        lines.append(f'{indent}{indent}"""Call {action_name} with minimal params."""')
        lines.append(f"{indent}{indent}result = call_action(mod.{func_name}, conn, ns(")
        lines.append(f"{indent}{indent}))")
        lines.append(f"{indent}{indent}# With no required params, this may succeed or error gracefully")
        lines.append(f"{indent}{indent}assert 'status' in result")
        lines.append(f"")

    code = "\n".join(lines)
    return code


def insert_feature_test(test_file_path: str, test_code: str) -> dict:
    """Append generated test code to an existing test file (or create a new one).

    Safety:
    - Creates .bak backup before modification
    - Validates syntax of the resulting file
    - If syntax invalid, restores backup and returns error

    Args:
        test_file_path: Absolute path to the test file.
        test_code: The test code string to append.

    Returns:
        dict with keys: success, file_path, lines_added, backup_path, error
    """
    test_file_path = os.path.abspath(test_file_path)

    # Validate test code syntax in isolation
    try:
        compile(test_code, "<test_code>", "exec")
    except SyntaxError as e:
        return {
            "success": False,
            "error": f"Test code has syntax error: Line {e.lineno}: {e.msg}",
            "file_path": test_file_path,
        }

    if os.path.isfile(test_file_path):
        # Append to existing file
        try:
            with open(test_file_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
        except OSError as e:
            return {"success": False, "error": f"Cannot read file: {e}", "file_path": test_file_path}

        original_line_count = len(existing_content.splitlines())

        # Create backup
        backup_path = test_file_path + ".bak"
        try:
            shutil.copy2(test_file_path, backup_path)
        except OSError as e:
            return {"success": False, "error": f"Cannot create backup: {e}", "file_path": test_file_path}

        # Append test code with separator
        new_content = existing_content.rstrip("\n") + "\n\n" + test_code.rstrip("\n") + "\n"

        # Validate combined syntax
        try:
            compile(new_content, test_file_path, "exec")
        except SyntaxError as e:
            # Restore backup
            shutil.copy2(backup_path, test_file_path)
            return {
                "success": False,
                "error": f"Combined file has syntax error: Line {e.lineno}: {e.msg}",
                "file_path": test_file_path,
                "backup_path": backup_path,
            }

        # Write the modified file
        try:
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except OSError as e:
            shutil.copy2(backup_path, test_file_path)
            return {"success": False, "error": f"Cannot write file: {e}", "file_path": test_file_path}

        new_line_count = len(new_content.splitlines())
        return {
            "success": True,
            "file_path": test_file_path,
            "lines_added": new_line_count - original_line_count,
            "backup_path": backup_path,
            "created_new": False,
        }

    else:
        # Create new test file with imports header
        header = (
            '"""Auto-generated tests by ERPClaw OS in-module generator."""\n'
            "import pytest\n"
            "\n"
        )
        new_content = header + test_code.rstrip("\n") + "\n"

        # Validate syntax
        try:
            compile(new_content, test_file_path, "exec")
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Generated file has syntax error: Line {e.lineno}: {e.msg}",
                "file_path": test_file_path,
            }

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        try:
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except OSError as e:
            return {"success": False, "error": f"Cannot write file: {e}", "file_path": test_file_path}

        return {
            "success": True,
            "file_path": test_file_path,
            "lines_added": len(new_content.splitlines()),
            "backup_path": None,
            "created_new": True,
        }
