#!/usr/bin/env python3
"""ERPClaw Module Manager — install, update, and manage GitHub-hosted modules.

Handles discovery, installation, dependency resolution, and action cache
management for ERPClaw expansion modules. Modules are git-cloned into
~/.openclaw/erpclaw/modules/{module-name}/ and tracked in the
erpclaw_module / erpclaw_module_action tables.

Usage: python3 module_manager.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

# ---------------------------------------------------------------------------
# Shared library imports
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
from erpclaw_lib.db import get_connection
from erpclaw_lib.response import ok, err, rows_to_list, row_to_dict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODULES_DIR = os.path.expanduser("~/.openclaw/erpclaw/modules")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(SCRIPT_DIR, "module_registry.json")


def _now_iso():
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_registry():
    """Load the module catalog from module_registry.json."""
    if not os.path.isfile(REGISTRY_PATH):
        err(f"Module registry not found at {REGISTRY_PATH}")
    try:
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        err(f"Failed to read module registry: {e}")


def _registry_to_dict(registry):
    """Convert registry modules (dict-keyed or list) to {name: info} dict."""
    modules_raw = registry.get("modules", {})
    if isinstance(modules_raw, dict):
        result = {}
        for name, info in modules_raw.items():
            info_copy = dict(info)
            info_copy.setdefault("name", name)
            result[name] = info_copy
        return result
    # List format (fallback)
    return {m["name"]: m for m in modules_raw}


def _get_installed_modules(conn):
    """Return dict of installed module names -> row dicts."""
    rows = conn.execute("SELECT * FROM erpclaw_module").fetchall()
    return {row["name"]: dict(row) for row in rows}


def _get_git_commit(install_path):
    """Get the current git commit hash for a module directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=install_path, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _check_remote_updates(install_path):
    """Check if the module has updates available on origin/main.

    Returns (has_updates: bool, local_commit: str, remote_commit: str).
    """
    local_commit = _get_git_commit(install_path)
    try:
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=install_path, capture_output=True, text=True, timeout=30
        )
        result = subprocess.run(
            ["git", "rev-parse", "origin/main"],
            cwd=install_path, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            remote_commit = result.stdout.strip()
            return (local_commit != remote_commit, local_commit, remote_commit)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return (False, local_commit, None)


# ---------------------------------------------------------------------------
# Action cache builder — uses AST parsing (safe, no side effects)
# ---------------------------------------------------------------------------

def _extract_actions_via_ast(script_path):
    """Extract action names from a module's db_query.py using AST parsing.

    Looks for top-level assignments to ACTIONS, ACTION_MAP, and ALIASES dicts.
    Extracts the string keys from each. This is safer than importing the module
    since it avoids executing any code or triggering import side effects.
    """
    if not os.path.isfile(script_path):
        return set()

    try:
        with open(script_path, "r") as f:
            source = f.read()
        tree = ast.parse(source, filename=script_path)
    except (SyntaxError, OSError):
        return set()

    target_names = {"ACTIONS", "ACTION_MAP", "ALIASES"}
    all_actions = set()

    for node in ast.iter_child_nodes(tree):
        # Match: ACTIONS = { ... }
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in target_names:
                    all_actions |= _extract_dict_keys(node.value)
        # Match: ACTIONS.update({ ... }) — Pattern B merge from domain modules
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if (isinstance(call.func, ast.Attribute)
                    and call.func.attr == "update"
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id in target_names
                    and call.args):
                all_actions |= _extract_dict_keys(call.args[0])

    # Remove 'status' to avoid collision — each module has its own status
    all_actions.discard("status")
    return all_actions


def _extract_dict_keys(node):
    """Extract string keys from a Dict AST node."""
    keys = set()
    if isinstance(node, ast.Dict):
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
    return keys


def _extract_actions_via_regex(script_path):
    """Fallback: extract action names using regex on the source text.

    Matches patterns like:
        "action-name": some_function,
        'action-name': some_function,
    within ACTIONS = { ... } blocks.
    """
    if not os.path.isfile(script_path):
        return set()

    try:
        with open(script_path, "r") as f:
            source = f.read()
    except OSError:
        return set()

    actions = set()
    # Find ACTIONS = { ... } block (and ACTION_MAP, ALIASES)
    for var_name in ("ACTIONS", "ACTION_MAP", "ALIASES"):
        pattern = rf'{var_name}\s*=\s*\{{([^}}]*)\}}'
        match = re.search(pattern, source, re.DOTALL)
        if match:
            block = match.group(1)
            # Extract quoted string keys
            actions |= set(re.findall(r'["\']([a-z][a-z0-9\-]+)["\']', block))
        # Also match .update({...})
        pattern_update = rf'{var_name}\.update\(\s*\{{([^}}]*)\}}\s*\)'
        for m in re.finditer(pattern_update, source, re.DOTALL):
            block = m.group(1)
            actions |= set(re.findall(r'["\']([a-z][a-z0-9\-]+)["\']', block))

    actions.discard("status")
    return actions


def build_action_cache(conn, module_name, install_path):
    """Scan a module's db_query.py and cache its action names.

    Uses AST parsing as the primary method, falling back to regex if AST
    yields no results (e.g., dynamically constructed dicts).
    Also scans sibling .py files in scripts/ for domain modules that
    define their own ACTIONS dicts (merged via ACTIONS.update()).

    Returns the number of actions cached.
    """
    script_path = os.path.join(install_path, "scripts", "db_query.py")

    all_actions = _extract_actions_via_ast(script_path)
    if not all_actions:
        all_actions = _extract_actions_via_regex(script_path)

    # Also scan sibling domain modules in scripts/ directory
    scripts_dir = os.path.join(install_path, "scripts")
    if os.path.isdir(scripts_dir):
        for fname in os.listdir(scripts_dir):
            if fname.endswith(".py") and fname != "db_query.py":
                domain_path = os.path.join(scripts_dir, fname)
                domain_actions = _extract_actions_via_ast(domain_path)
                if not domain_actions:
                    domain_actions = _extract_actions_via_regex(domain_path)
                all_actions |= domain_actions

    if not all_actions:
        return 0

    # Clear existing cache for this module and insert fresh
    conn.execute(
        "DELETE FROM erpclaw_module_action WHERE module_name = ?",
        (module_name,)
    )
    conn.executemany(
        "INSERT OR REPLACE INTO erpclaw_module_action (module_name, action_name) VALUES (?, ?)",
        [(module_name, a) for a in sorted(all_actions)]
    )
    conn.commit()

    # Check for action name collisions with other modules (non-fatal warning)
    collisions = conn.execute(
        """SELECT action_name, module_name FROM erpclaw_module_action
           WHERE action_name IN ({}) AND module_name != ?""".format(
            ",".join("?" for _ in all_actions)),
        list(all_actions) + [module_name]
    ).fetchall()
    if collisions:
        import sys as _sys
        for c in collisions:
            _sys.stderr.write(
                f"[module-manager] WARNING: action '{c['action_name']}' in '{module_name}' "
                f"collides with '{c['module_name']}'\n"
            )

    return len(all_actions)


# ---------------------------------------------------------------------------
# SKILL.md regeneration — appends installed module actions to deployed SKILL.md
# ---------------------------------------------------------------------------

def _regenerate_skill_md(conn):
    """Regenerate the deployed SKILL.md with installed module actions appendix.

    Reads the source SKILL.md as a template, appends an auto-generated section
    listing all installed module actions, and writes to the deployed location.
    The source template is the installed skill's SKILL.md (without the appendix).
    """
    # Find the deployed SKILL.md path
    deployed_path = os.path.expanduser("~/clawd/skills/erpclaw/SKILL.md")
    # Source template is in the same skill directory
    source_path = os.path.join(SCRIPT_DIR, "..", "SKILL.md")

    # Use source if it exists, otherwise use deployed as template
    template_path = source_path if os.path.isfile(source_path) else deployed_path
    if not os.path.isfile(template_path):
        return  # No SKILL.md to regenerate

    try:
        with open(template_path, "r") as f:
            content = f.read()
    except OSError:
        return

    # Strip any existing auto-generated appendix
    marker = "## Installed Module Actions"
    if marker in content:
        content = content[:content.index(marker)].rstrip() + "\n"

    # Query installed modules and their actions
    rows = conn.execute(
        """SELECT ma.module_name, ma.action_name, m.display_name, m.action_count
           FROM erpclaw_module_action ma
           JOIN erpclaw_module m ON m.name = ma.module_name
           WHERE m.install_status = 'installed' AND m.is_active = 1
           ORDER BY ma.module_name, ma.action_name"""
    ).fetchall()

    if not rows:
        # No modules installed — write template without appendix
        if os.path.isfile(deployed_path):
            try:
                with open(deployed_path, "w") as f:
                    f.write(content)
            except OSError:
                pass
        return

    # Group actions by module
    module_actions = {}
    module_display = {}
    module_counts = {}
    for r in rows:
        mod = r["module_name"]
        module_actions.setdefault(mod, []).append(r["action_name"])
        module_display[mod] = r["display_name"]
        module_counts[mod] = r["action_count"] or len(module_actions[mod])

    # Read module descriptions from SKILL.md files for context
    def _get_module_desc(module_name):
        """Read first line of description from module's SKILL.md."""
        for base in [os.path.join(MODULES_DIR, module_name),
                     os.path.join(SCRIPT_DIR, "..", "..", module_name)]:
            skill_path = os.path.join(base, "SKILL.md")
            if os.path.isfile(skill_path):
                try:
                    with open(skill_path, "r") as f:
                        for line in f:
                            if line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip().strip(">").strip()
                                if desc:
                                    return desc[:120]
                except OSError:
                    pass
        return ""

    # Build appendix
    appendix = f"\n\n{marker}\n"
    appendix += "<!-- AUTO-GENERATED — do not edit manually. Regenerated on module install/uninstall. -->\n\n"

    for mod in sorted(module_actions.keys()):
        actions = module_actions[mod]
        display = module_display.get(mod, mod)
        count = len(actions)
        desc = _get_module_desc(mod)

        appendix += f"### {display} ({count} actions)\n"
        if desc:
            appendix += f"{desc}\n"

        # Show key actions (up to 10)
        key_actions = actions[:10]
        appendix += f"Key actions: {', '.join(f'`{a}`' for a in key_actions)}"
        if len(actions) > 10:
            appendix += f", ... (+{len(actions) - 10} more)"
        appendix += "\n\n"

    # Write to deployed path
    deployed_dir = os.path.dirname(deployed_path)
    if os.path.isdir(deployed_dir):
        try:
            with open(deployed_path, "w") as f:
                f.write(content + appendix)
        except OSError:
            pass  # Non-fatal — skill still works, just without action discovery


# ---------------------------------------------------------------------------
# Action: install-module
# ---------------------------------------------------------------------------

def install_module(args):
    """Install a module from GitHub.

    Resolves dependencies first (auto-installing missing ones), clones the
    repo, runs init_db.py if present, reads module.json for metadata, builds
    the action cache, and registers in erpclaw_module.
    """
    module_name = args.module_name
    if not module_name:
        err("--module-name is required")

    registry = _load_registry()
    modules_by_name = _registry_to_dict(registry)

    if module_name not in modules_by_name:
        err(
            f"Module '{module_name}' not found in registry",
            suggestion="Run --action available-modules to see all available modules"
        )

    module_info = modules_by_name[module_name]
    conn = get_connection()

    # Check if already installed
    existing = conn.execute(
        "SELECT id, version, install_status FROM erpclaw_module WHERE name = ?",
        (module_name,)
    ).fetchone()
    if existing:
        if existing["install_status"] == "installed":
            err(
                f"Module '{module_name}' is already installed (version {existing['version']})",
                suggestion="Use --action update-modules to update, or --action remove-module to reinstall"
            )
        else:
            # Previous install failed — clean up and retry
            _cleanup_failed_install(conn, module_name)

    # Resolve dependencies
    requires = module_info.get("requires", [])
    if requires:
        installed = _get_installed_modules(conn)
        missing = [r for r in requires if r not in installed]
        if missing:
            auto_installed = []
            for dep in missing:
                if dep not in modules_by_name:
                    err(
                        f"Dependency '{dep}' for module '{module_name}' not found in registry",
                        suggestion="This module has an unresolvable dependency"
                    )
                # Recursively install dependency
                dep_args = argparse.Namespace(module_name=dep)
                try:
                    # Temporarily suppress ok() exit to allow chaining
                    _install_module_inner(dep_args, conn, modules_by_name, depth=1)
                    auto_installed.append(dep)
                except SystemExit:
                    # ok() calls sys.exit(0) — we need to re-open connection
                    conn = get_connection()
                    auto_installed.append(dep)

    # Perform the actual installation
    result = _install_module_inner(args, conn, modules_by_name, depth=0)
    ok(result)


def _install_module_inner(args, conn, modules_by_name, depth=0):
    """Inner installation logic. Returns result dict instead of calling ok().

    The depth parameter tracks recursive dependency installs to prevent
    infinite loops.
    """
    if depth > 10:
        err("Dependency resolution exceeded maximum depth (10) — circular dependency detected")

    module_name = args.module_name
    module_info = modules_by_name[module_name]

    # Check again (may have been installed as a dependency in this session)
    existing = conn.execute(
        "SELECT id FROM erpclaw_module WHERE name = ? AND install_status = 'installed'",
        (module_name,)
    ).fetchone()
    if existing:
        return {"module": module_name, "note": "already installed (as dependency)"}

    install_path = os.path.join(MODULES_DIR, module_name)
    github_repo = module_info.get("github", module_info.get("github_repo", ""))
    subdir = module_info.get("subdir", "")
    now = _now_iso()
    module_id = str(uuid4())

    # Mark as installing
    conn.execute(
        """INSERT INTO erpclaw_module
           (id, name, display_name, version, category, github_repo,
            install_path, installed_at, updated_at, install_status, requires_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'updating', ?)""",
        (module_id, module_name, module_info.get("display_name", module_name),
         module_info.get("version", "0.0.0"), module_info.get("category", "expansion"),
         github_repo, install_path, now, now,
         json.dumps(module_info.get("requires", [])))
    )
    conn.commit()

    # Clone the repository
    os.makedirs(MODULES_DIR, exist_ok=True)
    if os.path.isdir(install_path):
        shutil.rmtree(install_path)

    clone_url = f"https://github.com/{github_repo}.git"

    if subdir:
        # Grouped repo — use sparse checkout to get only the needed subdir
        import tempfile
        tmp_dir = tempfile.mkdtemp(prefix=f"erpclaw-install-{module_name}-")
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--filter=blob:none",
                 "--sparse", clone_url, tmp_dir],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                _mark_failed(conn, module_name, f"git clone failed: {result.stderr.strip()}")
                err(f"Failed to clone {clone_url}: {result.stderr.strip()}")

            result = subprocess.run(
                ["git", "-C", tmp_dir, "sparse-checkout", "set", subdir],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                _mark_failed(conn, module_name, f"sparse-checkout failed: {result.stderr.strip()}")
                err(f"Failed sparse-checkout for {subdir}: {result.stderr.strip()}")

            # Move the subdir to the install path
            subdir_path = os.path.join(tmp_dir, subdir)
            if not os.path.isdir(subdir_path):
                _mark_failed(conn, module_name, f"subdir '{subdir}' not found in repo")
                err(f"Subdir '{subdir}' not found in {github_repo}")
            shutil.copytree(subdir_path, install_path)
        except subprocess.TimeoutExpired:
            _mark_failed(conn, module_name, "git clone timed out after 120s")
            err(f"git clone timed out for {clone_url}")
        except FileNotFoundError:
            _mark_failed(conn, module_name, "git not found in PATH")
            err("git is not installed or not in PATH")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        # Standalone repo — clone directly
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, install_path],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                _mark_failed(conn, module_name, f"git clone failed: {result.stderr.strip()}")
                err(f"Failed to clone {clone_url}: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            _mark_failed(conn, module_name, "git clone timed out after 120s")
            err(f"git clone timed out for {clone_url}")
        except FileNotFoundError:
            _mark_failed(conn, module_name, "git not found in PATH")
            err("git is not installed or not in PATH")

    # Read module.json if it exists
    module_json_path = os.path.join(install_path, "module.json")
    module_meta = {}
    if os.path.isfile(module_json_path):
        try:
            with open(module_json_path, "r") as f:
                module_meta = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass  # Non-fatal — registry info is sufficient

    # Merge metadata: module.json overrides registry defaults
    display_name = module_meta.get("display_name", module_info.get("display_name", module_name))
    version = module_meta.get("version", module_info.get("version", "0.0.0"))

    # Run init_db.py if it exists
    init_db_path = os.path.join(install_path, "init_db.py")
    tables_created = 0
    if os.path.isfile(init_db_path):
        try:
            result = subprocess.run(
                [sys.executable, init_db_path],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                _mark_failed(conn, module_name, f"init_db.py failed: {result.stderr.strip()}")
                err(f"init_db.py failed for {module_name}: {result.stderr.strip()}")
            # Try to parse table count from output
            if result.stdout:
                try:
                    init_result = json.loads(result.stdout)
                    tables_created = init_result.get("tables_created", 0)
                except json.JSONDecodeError:
                    # Many init_db.py scripts print human-readable text, not JSON
                    # Try to extract number from output like "Created 5 tables"
                    import re as _re
                    m = _re.search(r'(\d+)\s+tables?', result.stdout)
                    if m:
                        tables_created = int(m.group(1))
            # If still 0, count module-specific tables directly from DB
            if tables_created == 0:
                try:
                    data_db = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")
                    if os.path.isfile(data_db):
                        dconn = sqlite3.connect(data_db)
                        prefix = module_name.replace("-", "_") + "_"
                        cursor = dconn.execute(
                            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE ?",
                            (prefix + "%",))
                        tables_created = cursor.fetchone()[0]
                        dconn.close()
                except Exception:
                    pass
        except subprocess.TimeoutExpired:
            _mark_failed(conn, module_name, "init_db.py timed out after 60s")
            err(f"init_db.py timed out for {module_name}")

    # Build action cache
    action_count = build_action_cache(conn, module_name, install_path)

    # If no actions found, try scanning subdirectories (grouped repos like erpclaw-ops)
    if action_count == 0:
        scripts_dir = os.path.join(install_path, "scripts")
        if os.path.isdir(scripts_dir):
            for subdir in os.listdir(scripts_dir):
                sub_script = os.path.join(scripts_dir, subdir, "db_query.py")
                if os.path.isfile(sub_script):
                    sub_actions = _extract_actions_via_ast(sub_script)
                    if not sub_actions:
                        sub_actions = _extract_actions_via_regex(sub_script)
                    if sub_actions:
                        conn.executemany(
                            "INSERT OR REPLACE INTO erpclaw_module_action (module_name, action_name) VALUES (?, ?)",
                            [(module_name, a) for a in sorted(sub_actions)]
                        )
                        action_count += len(sub_actions)
            if action_count > 0:
                conn.commit()

    # Get git commit hash
    git_commit = _get_git_commit(install_path)

    # Update module record to installed
    conn.execute(
        """UPDATE erpclaw_module
           SET display_name = ?, version = ?, install_status = 'installed',
               git_commit = ?, tables_created = ?, action_count = ?,
               updated_at = ?, error_log = NULL
           WHERE name = ?""",
        (display_name, version, git_commit, tables_created, action_count, now, module_name)
    )
    conn.commit()

    # Regenerate SKILL.md with new module actions
    _regenerate_skill_md(conn)

    return {
        "module": module_name,
        "display_name": display_name,
        "version": version,
        "action_count": action_count,
        "tables_created": tables_created,
        "install_path": install_path,
        "git_commit": git_commit,
        "installed_at": now,
    }


def _mark_failed(conn, module_name, error_msg):
    """Mark a module installation as failed."""
    conn.execute(
        "UPDATE erpclaw_module SET install_status = 'failed', error_log = ?, updated_at = ? WHERE name = ?",
        (error_msg, _now_iso(), module_name)
    )
    conn.commit()


def _cleanup_failed_install(conn, module_name):
    """Remove records from a previously failed installation."""
    row = conn.execute(
        "SELECT install_path FROM erpclaw_module WHERE name = ?",
        (module_name,)
    ).fetchone()
    if row and row["install_path"] and os.path.isdir(os.path.expanduser(row["install_path"])):
        shutil.rmtree(os.path.expanduser(row["install_path"]), ignore_errors=True)
    conn.execute("DELETE FROM erpclaw_module_action WHERE module_name = ?", (module_name,))
    conn.execute("DELETE FROM erpclaw_module WHERE name = ?", (module_name,))
    conn.commit()


# ---------------------------------------------------------------------------
# Action: remove-module
# ---------------------------------------------------------------------------

def remove_module(args):
    """Remove an installed module.

    Checks that no other installed modules depend on this one before removal.
    Deletes the module directory and database records, but preserves any
    tables/data the module created (no DROP TABLE).
    """
    module_name = args.module_name
    if not module_name:
        err("--module-name is required")

    conn = get_connection()

    # Check module exists
    row = conn.execute(
        "SELECT * FROM erpclaw_module WHERE name = ?",
        (module_name,)
    ).fetchone()
    if not row:
        err(f"Module '{module_name}' is not installed")

    # Check reverse dependencies — are any other installed modules depending on this one?
    installed = _get_installed_modules(conn)
    dependents = []
    for name, mod in installed.items():
        if name == module_name:
            continue
        requires = json.loads(mod.get("requires_json") or "[]")
        if module_name in requires:
            dependents.append(name)

    if dependents:
        err(
            f"Cannot remove '{module_name}': required by {', '.join(dependents)}",
            suggestion=f"Remove dependent modules first: {', '.join(dependents)}"
        )

    install_path = os.path.expanduser(row["install_path"])

    # Mark as removing
    conn.execute(
        "UPDATE erpclaw_module SET install_status = 'removing', updated_at = ? WHERE name = ?",
        (_now_iso(), module_name)
    )
    conn.commit()

    # Delete action cache
    conn.execute("DELETE FROM erpclaw_module_action WHERE module_name = ?", (module_name,))

    # Delete module record
    conn.execute("DELETE FROM erpclaw_module WHERE name = ?", (module_name,))
    conn.commit()

    # Remove directory
    if install_path and os.path.isdir(install_path):
        shutil.rmtree(install_path, ignore_errors=True)

    # Regenerate SKILL.md without removed module
    _regenerate_skill_md(conn)

    ok({
        "module": module_name,
        "removed": True,
        "note": "Module directory and records removed. Database tables are preserved.",
    })


# ---------------------------------------------------------------------------
# Action: update-modules
# ---------------------------------------------------------------------------

def update_modules(args):
    """Update all or a specific installed module.

    For each module: fetches from origin, compares HEAD with origin/main,
    pulls if different, re-runs init_db.py, and rebuilds the action cache.
    """
    conn = get_connection()
    target_name = getattr(args, "module_name", None)

    if target_name:
        rows = conn.execute(
            "SELECT * FROM erpclaw_module WHERE name = ? AND install_status = 'installed'",
            (target_name,)
        ).fetchall()
        if not rows:
            err(f"Module '{target_name}' is not installed or not in 'installed' state")
    else:
        rows = conn.execute(
            "SELECT * FROM erpclaw_module WHERE install_status = 'installed'"
        ).fetchall()

    if not rows:
        ok({"updated": [], "message": "No modules to update"})

    updated = []
    skipped = []
    failed = []

    for row in rows:
        module_name = row["name"]
        install_path = os.path.expanduser(row["install_path"])

        if not os.path.isdir(install_path):
            failed.append({"module": module_name, "error": "Install directory missing"})
            continue

        has_updates, local_commit, remote_commit = _check_remote_updates(install_path)

        if not has_updates:
            skipped.append({"module": module_name, "commit": local_commit, "reason": "already up to date"})
            continue

        # Mark as updating
        conn.execute(
            "UPDATE erpclaw_module SET install_status = 'updating', updated_at = ? WHERE name = ?",
            (_now_iso(), module_name)
        )
        conn.commit()

        # Pull latest
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=install_path, capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                _mark_failed(conn, module_name, f"git pull failed: {result.stderr.strip()}")
                failed.append({"module": module_name, "error": f"git pull failed: {result.stderr.strip()}"})
                continue
        except subprocess.TimeoutExpired:
            _mark_failed(conn, module_name, "git pull timed out")
            failed.append({"module": module_name, "error": "git pull timed out"})
            continue

        # Re-run init_db.py if it exists
        init_db_path = os.path.join(install_path, "init_db.py")
        if os.path.isfile(init_db_path):
            try:
                subprocess.run(
                    [sys.executable, init_db_path],
                    capture_output=True, text=True, timeout=60
                )
            except subprocess.TimeoutExpired:
                pass  # Non-fatal for updates

        # Read updated module.json
        module_json_path = os.path.join(install_path, "module.json")
        new_version = row["version"]
        if os.path.isfile(module_json_path):
            try:
                with open(module_json_path, "r") as f:
                    meta = json.load(f)
                new_version = meta.get("version", new_version)
            except (json.JSONDecodeError, OSError):
                pass

        # Rebuild action cache
        action_count = build_action_cache(conn, module_name, install_path)
        new_commit = _get_git_commit(install_path)
        now = _now_iso()

        conn.execute(
            """UPDATE erpclaw_module
               SET install_status = 'installed', version = ?, git_commit = ?,
                   action_count = ?, updated_at = ?, error_log = NULL
               WHERE name = ?""",
            (new_version, new_commit, action_count, now, module_name)
        )
        conn.commit()

        updated.append({
            "module": module_name,
            "old_commit": local_commit,
            "new_commit": new_commit,
            "version": new_version,
            "action_count": action_count,
        })

    ok({
        "updated": updated,
        "skipped": skipped,
        "failed": failed,
        "summary": f"{len(updated)} updated, {len(skipped)} up-to-date, {len(failed)} failed",
    })


# ---------------------------------------------------------------------------
# Action: list-modules
# ---------------------------------------------------------------------------

def list_modules(args):
    """List all installed and active modules."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT name, display_name, version, category, action_count,
                  tables_created, installed_at, updated_at, git_commit, install_status
           FROM erpclaw_module
           WHERE is_active = 1
           ORDER BY category, name"""
    ).fetchall()

    modules = rows_to_list(rows)

    # Enrich with action count from cache (authoritative source)
    for mod in modules:
        count = conn.execute(
            "SELECT COUNT(*) as cnt FROM erpclaw_module_action WHERE module_name = ?",
            (mod["name"],)
        ).fetchone()
        mod["cached_actions"] = count["cnt"] if count else 0

    ok({
        "modules": modules,
        "total": len(modules),
    })


# ---------------------------------------------------------------------------
# Action: available-modules
# ---------------------------------------------------------------------------

def available_modules(args):
    """Browse the module catalog, cross-referenced with install status."""
    registry = _load_registry()
    conn = get_connection()
    installed = _get_installed_modules(conn)

    category_filter = getattr(args, "category", None)
    search_query = getattr(args, "search", None)

    results = []
    for mod in _registry_to_dict(registry).values():
        # Filter by category
        if category_filter and mod.get("category") != category_filter:
            continue

        # Filter by search query
        if search_query:
            query_lower = search_query.lower()
            searchable = " ".join([
                mod.get("name", ""),
                mod.get("display_name", ""),
                mod.get("description", ""),
                " ".join(mod.get("tags", [])),
            ]).lower()
            if query_lower not in searchable:
                continue

        entry = {
            "name": mod["name"],
            "display_name": mod.get("display_name", mod["name"]),
            "description": mod.get("description", ""),
            "category": mod.get("category", "expansion"),
            "version": mod.get("version", "0.0.0"),
            "tags": mod.get("tags", []),
            "requires": mod.get("requires", []),
        }

        # Cross-reference with installed modules
        if mod["name"] in installed:
            inst = installed[mod["name"]]
            entry["installed"] = True
            entry["installed_version"] = inst["version"]
            entry["install_status"] = inst["install_status"]
        else:
            entry["installed"] = False

        results.append(entry)

    ok({
        "modules": results,
        "total": len(results),
        "filters": {
            "category": category_filter,
            "search": search_query,
        },
    })


# ---------------------------------------------------------------------------
# Action: module-status
# ---------------------------------------------------------------------------

def module_status(args):
    """Show detailed status for a specific installed module."""
    module_name = args.module_name
    if not module_name:
        err("--module-name is required")

    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM erpclaw_module WHERE name = ?",
        (module_name,)
    ).fetchone()
    if not row:
        err(f"Module '{module_name}' is not installed")

    mod = row_to_dict(row)
    install_path = os.path.expanduser(mod["install_path"])

    # Get cached actions
    actions = conn.execute(
        "SELECT action_name FROM erpclaw_module_action WHERE module_name = ? ORDER BY action_name",
        (module_name,)
    ).fetchall()
    mod["actions"] = [a["action_name"] for a in actions]
    mod["cached_action_count"] = len(mod["actions"])

    # Parse requires_json
    mod["requires"] = json.loads(mod.get("requires_json") or "[]")
    del mod["requires_json"]

    # Check for dependents (who depends on this module)
    installed = _get_installed_modules(conn)
    dependents = []
    for name, inst in installed.items():
        if name == module_name:
            continue
        requires = json.loads(inst.get("requires_json") or "[]")
        if module_name in requires:
            dependents.append(name)
    mod["dependents"] = dependents

    # Check git status
    if os.path.isdir(install_path):
        mod["directory_exists"] = True
        has_updates, local_commit, remote_commit = _check_remote_updates(install_path)
        mod["has_updates"] = has_updates
        mod["local_commit"] = local_commit
        mod["remote_commit"] = remote_commit
    else:
        mod["directory_exists"] = False
        mod["has_updates"] = None
        mod["local_commit"] = None
        mod["remote_commit"] = None

    ok(mod)


# ---------------------------------------------------------------------------
# Action: search-modules
# ---------------------------------------------------------------------------

def search_modules(args):
    """Search the module catalog by name, description, and tags."""
    search_query = getattr(args, "search", None)
    if not search_query:
        err("--search is required")

    registry = _load_registry()
    query_lower = search_query.lower()
    query_terms = query_lower.split()

    results = []
    for mod in _registry_to_dict(registry).values():
        searchable = " ".join([
            mod.get("name", ""),
            mod.get("display_name", ""),
            mod.get("description", ""),
            " ".join(mod.get("tags", [])),
        ]).lower()

        # All terms must match
        if all(term in searchable for term in query_terms):
            results.append({
                "name": mod["name"],
                "display_name": mod.get("display_name", mod["name"]),
                "description": mod.get("description", ""),
                "category": mod.get("category", "expansion"),
                "version": mod.get("version", "0.0.0"),
                "tags": mod.get("tags", []),
            })

    ok({
        "query": search_query,
        "results": results,
        "total": len(results),
    })


# ---------------------------------------------------------------------------
# Action: rebuild-action-cache
# ---------------------------------------------------------------------------

def rebuild_action_cache(args):
    """Rebuild the entire action cache from all installed modules.

    Truncates erpclaw_module_action and re-scans every installed module's
    db_query.py. Useful after migrations, manual changes, or cache corruption.
    """
    conn = get_connection()

    # Clear entire cache
    conn.execute("DELETE FROM erpclaw_module_action")
    conn.commit()

    rows = conn.execute(
        "SELECT name, install_path FROM erpclaw_module WHERE install_status = 'installed'"
    ).fetchall()

    rebuilt = []
    errors = []
    total_actions = 0

    for row in rows:
        module_name = row["name"]
        install_path = os.path.expanduser(row["install_path"])

        if not os.path.isdir(install_path):
            errors.append({"module": module_name, "error": "Install directory missing"})
            continue

        try:
            count = build_action_cache(conn, module_name, install_path)
            # Update the action_count in the module record
            conn.execute(
                "UPDATE erpclaw_module SET action_count = ?, updated_at = ? WHERE name = ?",
                (count, _now_iso(), module_name)
            )
            conn.commit()
            rebuilt.append({"module": module_name, "action_count": count})
            total_actions += count
        except Exception as e:
            errors.append({"module": module_name, "error": str(e)})

    # Regenerate SKILL.md with updated actions
    _regenerate_skill_md(conn)

    ok({
        "rebuilt": rebuilt,
        "errors": errors,
        "total_modules": len(rebuilt),
        "total_actions": total_actions,
        "summary": f"Rebuilt cache for {len(rebuilt)} modules ({total_actions} actions), {len(errors)} errors",
    })


# ---------------------------------------------------------------------------
# Action: list-all-actions
# ---------------------------------------------------------------------------

def list_all_actions(args):
    """Return all available actions — core + installed modules."""
    conn = get_connection()

    # Get core actions from the main ACTION_MAP
    # We need to read db_query.py to get the ACTION_MAP keys
    db_query_path = os.path.join(SCRIPT_DIR, "db_query.py")
    core_actions = _extract_actions_via_regex(db_query_path)
    # Also add MODULE_ACTIONS and ONBOARDING_ACTIONS
    core_actions |= {
        "install-module", "remove-module", "update-modules",
        "list-modules", "available-modules", "module-status",
        "search-modules", "rebuild-action-cache",
        "list-profiles", "onboard", "list-all-actions",
    }

    # Module actions from cache
    rows = conn.execute(
        """SELECT ma.action_name, ma.module_name
           FROM erpclaw_module_action ma
           JOIN erpclaw_module m ON m.name = ma.module_name
           WHERE m.install_status = 'installed' AND m.is_active = 1
           ORDER BY ma.module_name, ma.action_name"""
    ).fetchall()

    module_actions = {}
    for r in rows:
        module_actions.setdefault(r["module_name"], []).append(r["action_name"])

    ok({
        "core_actions": sorted(core_actions),
        "core_count": len(core_actions),
        "module_actions": module_actions,
        "module_count": len(module_actions),
        "total": len(core_actions) + sum(len(v) for v in module_actions.values()),
    })


# ---------------------------------------------------------------------------
# Action: regenerate-skill-md
# ---------------------------------------------------------------------------

def regenerate_skill_md_action(args):
    """Regenerate the deployed SKILL.md with installed module actions."""
    conn = get_connection()
    _regenerate_skill_md(conn)

    # Count what was generated
    rows = conn.execute(
        """SELECT m.name, COUNT(ma.action_name) as cnt
           FROM erpclaw_module m
           LEFT JOIN erpclaw_module_action ma ON m.name = ma.module_name
           WHERE m.install_status = 'installed' AND m.is_active = 1
           GROUP BY m.name"""
    ).fetchall()

    modules = [{"module": r["name"], "actions": r["cnt"]} for r in rows]
    ok({
        "regenerated": True,
        "modules": modules,
        "total_modules": len(modules),
        "deployed_path": os.path.expanduser("~/clawd/skills/erpclaw/SKILL.md"),
    })


# ---------------------------------------------------------------------------
# Action dispatch and CLI
# ---------------------------------------------------------------------------

ACTIONS = {
    "install-module": install_module,
    "remove-module": remove_module,
    "update-modules": update_modules,
    "list-modules": list_modules,
    "available-modules": available_modules,
    "module-status": module_status,
    "search-modules": search_modules,
    "rebuild-action-cache": rebuild_action_cache,
    "list-all-actions": list_all_actions,
    "regenerate-skill-md": regenerate_skill_md_action,
}


def main():
    parser = argparse.ArgumentParser(
        description="ERPClaw Module Manager — install, update, and manage expansion modules"
    )
    parser.add_argument(
        "--action", required=True, choices=sorted(ACTIONS.keys()),
        help="Action to perform"
    )
    parser.add_argument(
        "--module-name",
        help="Module name (for install, remove, update, status)"
    )
    parser.add_argument(
        "--category",
        choices=["core", "expansion", "infrastructure", "vertical", "sub-vertical", "regional"],
        help="Filter by category (for available-modules)"
    )
    parser.add_argument(
        "--search",
        help="Search query (for search-modules, available-modules)"
    )

    args = parser.parse_args()
    action_fn = ACTIONS.get(args.action)
    if not action_fn:
        err(f"Unknown action: {args.action}")

    try:
        action_fn(args)
    except SystemExit:
        raise
    except Exception as e:
        err(f"Unexpected error in {args.action}: {e}")


if __name__ == "__main__":
    main()
