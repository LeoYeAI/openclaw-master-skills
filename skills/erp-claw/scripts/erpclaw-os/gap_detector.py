#!/usr/bin/env python3
"""ERPClaw OS — Gap Detection + Module Suggestions (Phase 3, Deliverable 3e)

Analyzes action_call_log and company configuration to detect missing
functionality and suggest relevant modules. Six detection methods:

  1. Error pattern analysis — actions that consistently fail with "Unknown action"
  2. Workflow gap analysis — action pairs with long gaps suggesting manual intervention
  3. Industry gap analysis — cross-reference company industry with module_registry.json
  4. Schema-code divergence — tables defined in init_schema.py/init_db.py with zero/minimal code references
  5. Stub detection — "Not yet implemented", "TODO", "FIXME", "placeholder" patterns in production code
  6. Feature completeness — compare domain actions against industry-standard feature matrix

All detected gaps are logged to erpclaw_improvement_log via improvement_log.py.
"""
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

# Add shared lib to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))

from erpclaw_lib.db import get_connection
from erpclaw_lib.query import Q, P, Table, Field, fn

# Add erpclaw-os directory to path for sibling imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from improvement_log import handle_log_improvement
from industry_configs import INDUSTRY_CONFIGS
from schema_diff import _CREATE_TABLE_RE
from dgm_engine import SAFETY_EXCLUDED_FILES
from feature_matrix import check_feature_completeness

# Module registry lives next to the root db_query.py
REGISTRY_PATH = os.path.join(
    os.path.dirname(SCRIPT_DIR), "module_registry.json"
)

# Error threshold: how many errors before flagging a gap
ERROR_THRESHOLD = 3
# Workflow gap threshold in seconds (5 minutes)
WORKFLOW_GAP_SECONDS = 300


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def _load_registry(registry_path=None):
    """Load module_registry.json and return the modules dict."""
    path = registry_path or REGISTRY_PATH
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("modules", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _get_installed_modules(conn):
    """Return set of installed module names from erpclaw_module table."""
    try:
        rows = conn.execute(
            "SELECT name FROM erpclaw_module WHERE install_status = 'installed'"
        ).fetchall()
        return {r["name"] for r in rows}
    except sqlite3.OperationalError:
        # Table doesn't exist
        return set()


def _get_company_industry(conn):
    """Read industry from erpclaw_module_config (set by configure-module).

    Returns (industry, size_tier) or (None, None) if not configured.
    """
    try:
        row = conn.execute(
            "SELECT industry, size_tier FROM erpclaw_module_config "
            "WHERE config_type = 'industry_config' "
            "ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        if row:
            return row["industry"], row["size_tier"]
    except sqlite3.OperationalError:
        pass
    return None, None


# ---------------------------------------------------------------------------
# Detection method 1: Error pattern analysis
# ---------------------------------------------------------------------------

def _detect_error_patterns(conn):
    """Find actions that consistently fail with 'Unknown action' errors.

    Queries action_call_log for action names that appear with errors
    (routed_to containing 'error' or route_tier = -1) more than ERROR_THRESHOLD times.

    Since action_call_log only logs successful routes (from the router in db_query.py),
    we look for action names that appear frequently but were routed to a module
    that doesn't exist, or for patterns indicating unknown action handling.

    In practice, the main router logs calls before forwarding. If the action
    was unknown, it wouldn't be logged. So we check for actions where the
    routed_to is suspicious or look for repeated calls to the same non-standard
    action that may indicate user demand.
    """
    gaps = []

    # Check for repeated action_names that route to non-core domains
    # (could indicate users hitting missing features)
    try:
        t = Table("action_call_log")
        q = (
            Q.from_(t)
            .select(t.action_name, fn.Count("*").as_("call_count"))
            .where(t.routed_to == P())
            .groupby(t.action_name)
        )
        sql = q.get_sql() + ' HAVING COUNT(*) > ?'

        rows = conn.execute(sql, ["error", ERROR_THRESHOLD]).fetchall()
        for row in rows:
            gaps.append({
                "gap_type": "error_pattern",
                "description": (
                    f"Action '{row['action_name']}' failed {row['call_count']} times "
                    f"with routing errors, suggesting missing module or action."
                ),
                "severity": "high",
                "suggested_action": f"Investigate adding action '{row['action_name']}' "
                                    f"or installing the module that provides it.",
                "action_name": row["action_name"],
                "error_count": row["call_count"],
            })
    except sqlite3.OperationalError:
        pass

    return gaps


# ---------------------------------------------------------------------------
# Detection method 2: Workflow gap analysis
# ---------------------------------------------------------------------------

def _detect_workflow_gaps(conn):
    """Find action pairs with consistently long gaps suggesting manual intervention.

    Looks for consecutive action pairs (by session_id or timestamp order) where
    the time between them exceeds WORKFLOW_GAP_SECONDS, suggesting the user
    had to do something manually between the two actions.
    """
    gaps = []

    try:
        # Find action pairs with large time gaps within the same session
        sql = """
            SELECT
                a.action_name AS action_a,
                b.action_name AS action_b,
                COUNT(*) AS pair_count,
                AVG(
                    CAST(
                        (julianday(b.timestamp) - julianday(a.timestamp)) * 86400
                    AS REAL)
                ) AS avg_gap_seconds
            FROM action_call_log a
            JOIN action_call_log b
                ON a.session_id = b.session_id
                AND b.rowid = (
                    SELECT MIN(c.rowid)
                    FROM action_call_log c
                    WHERE c.session_id = a.session_id
                      AND c.rowid > a.rowid
                )
            WHERE a.session_id IS NOT NULL
            GROUP BY a.action_name, b.action_name
            HAVING COUNT(*) >= 2
               AND AVG(
                   CAST(
                       (julianday(b.timestamp) - julianday(a.timestamp)) * 86400
                   AS REAL)
               ) > ?
        """
        rows = conn.execute(sql, [WORKFLOW_GAP_SECONDS]).fetchall()
        for row in rows:
            avg_gap = round(row["avg_gap_seconds"], 1)
            gaps.append({
                "gap_type": "workflow_gap",
                "description": (
                    f"Action pair '{row['action_a']}' -> '{row['action_b']}' "
                    f"has an average gap of {avg_gap}s across {row['pair_count']} occurrences, "
                    f"suggesting manual intervention between steps."
                ),
                "severity": "medium",
                "suggested_action": (
                    f"Consider adding an automated bridge action between "
                    f"'{row['action_a']}' and '{row['action_b']}'."
                ),
                "action_a": row["action_a"],
                "action_b": row["action_b"],
                "avg_gap_seconds": avg_gap,
                "pair_count": row["pair_count"],
            })
    except sqlite3.OperationalError:
        pass

    return gaps


# ---------------------------------------------------------------------------
# Detection method 3: Industry gap analysis
# ---------------------------------------------------------------------------

def _detect_industry_gaps(conn, registry):
    """Cross-reference company industry with standard modules for that industry.

    Reads industry from erpclaw_module_config (set by configure-module),
    looks up standard modules from INDUSTRY_CONFIGS, and flags any that
    are not installed.
    """
    gaps = []

    industry, size_tier = _get_company_industry(conn)
    if not industry:
        return gaps

    config = INDUSTRY_CONFIGS.get(industry)
    if not config:
        return gaps

    size_tier = size_tier or "small"
    standard_modules = config["modules"].get(size_tier, config["modules"].get("small", []))
    installed = _get_installed_modules(conn)

    for mod_name in standard_modules:
        if mod_name not in installed and mod_name in registry:
            mod_info = registry[mod_name]
            gaps.append({
                "gap_type": "industry_gap",
                "description": (
                    f"Module '{mod_name}' ({mod_info.get('display_name', mod_name)}) "
                    f"is standard for {config['display_name']} ({size_tier} tier) "
                    f"but is not installed."
                ),
                "severity": "medium",
                "suggested_action": (
                    f"Install module '{mod_name}' with: "
                    f"--action install-module --module-name {mod_name}"
                ),
                "module_name": mod_name,
                "industry": industry,
                "size_tier": size_tier,
            })

    return gaps


# ---------------------------------------------------------------------------
# Detection method 4: Schema-code divergence
# ---------------------------------------------------------------------------

# Minimum reference threshold — tables with fewer than this many references
# in db_query.py files are flagged as "minimal_code".
_MINIMAL_CODE_THRESHOLD = 3


def detect_schema_code_divergence(src_root: str) -> list[dict]:
    """Method 4: Find tables defined in init_schema.py/init_db.py with zero or minimal code references.

    Walks all init_schema.py and init_db.py files under src_root, extracts
    CREATE TABLE names, then counts references to each table name across all
    db_query.py files.  Tables with 0 references are "no_code"; tables with
    fewer than _MINIMAL_CODE_THRESHOLD references are "minimal_code".

    Returns list of:
    {
        "table_name": "blanket_order",
        "defined_in": "init_schema.py:1017",
        "action_references": 0,
        "status": "no_code",  # or "minimal_code" if <3 references
        "recommendation": "Generate CRUD actions for blanket_order"
    }
    """
    if not os.path.isdir(src_root):
        return []

    # Step 1: Collect all CREATE TABLE declarations with file + line number
    # {table_name: "relative_path:line_no"}
    table_defs: dict[str, str] = {}

    for dirpath, dirnames, filenames in os.walk(src_root):
        # Skip test/fixture directories
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", "tests", "fixtures")]
        for fname in filenames:
            if fname in ("init_schema.py", "init_db.py"):
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, "r") as f:
                        content = f.read()
                except (OSError, UnicodeDecodeError):
                    continue
                for m in _CREATE_TABLE_RE.finditer(content):
                    tname = m.group(1)
                    # Calculate line number from byte offset
                    line_no = content[:m.start()].count("\n") + 1
                    rel_path = os.path.relpath(fpath, src_root)
                    table_defs[tname] = f"{rel_path}:{line_no}"

    if not table_defs:
        return []

    # Step 2: Collect all db_query.py file contents (excluding tests)
    query_texts: list[str] = []
    for dirpath, dirnames, filenames in os.walk(src_root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", "tests", "fixtures")]
        for fname in filenames:
            if fname == "db_query.py":
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, "r") as f:
                        query_texts.append(f.read())
                except (OSError, UnicodeDecodeError):
                    continue

    combined_query_text = "\n".join(query_texts)

    # Step 3: Count references for each table in db_query.py files
    gaps = []
    for tname, defined_in in sorted(table_defs.items()):
        # Use word-boundary regex to avoid partial matches
        # e.g., "company" should not match "company_id"
        pattern = re.compile(r'(?<!\w)' + re.escape(tname) + r'(?!\w)')
        ref_count = len(pattern.findall(combined_query_text))

        if ref_count == 0:
            gaps.append({
                "gap_type": "schema_code_divergence",
                "table_name": tname,
                "defined_in": defined_in,
                "action_references": 0,
                "status": "no_code",
                "severity": "high",
                "description": (
                    f"Table '{tname}' (defined in {defined_in}) has zero "
                    f"references in any db_query.py — no actions use it."
                ),
                "recommendation": f"Generate CRUD actions for {tname}",
                "suggested_action": f"Generate CRUD actions for {tname}",
            })
        elif ref_count < _MINIMAL_CODE_THRESHOLD:
            gaps.append({
                "gap_type": "schema_code_divergence",
                "table_name": tname,
                "defined_in": defined_in,
                "action_references": ref_count,
                "status": "minimal_code",
                "severity": "medium",
                "description": (
                    f"Table '{tname}' (defined in {defined_in}) has only "
                    f"{ref_count} reference(s) in db_query.py files — likely incomplete."
                ),
                "recommendation": f"Review and expand actions for {tname}",
                "suggested_action": f"Review and expand actions for {tname}",
            })

    # Sort: no_code first (high severity), then minimal_code (medium)
    severity_order = {"high": 0, "medium": 1}
    gaps.sort(key=lambda g: (severity_order.get(g["severity"], 2), g["table_name"]))
    return gaps


# ---------------------------------------------------------------------------
# Detection method 5: Stub detection
# ---------------------------------------------------------------------------

# Patterns that indicate stub / unfinished code
_STUB_PATTERNS = re.compile(
    r"Not yet implemented|TODO[:\s]|FIXME[:\s]|placeholder|(?<!\w)stub(?!\w)|Phase 2\+|Extensible in future",
    re.IGNORECASE,
)

# Directories to skip during stub scanning
_SKIP_DIRS = frozenset({"__pycache__", ".git", "tests", "node_modules", "fixtures"})


def detect_stubs(src_root: str) -> list[dict]:
    """Method 5: Find 'Not yet implemented', 'TODO', 'FIXME', 'placeholder' stubs in production code.

    Walks all .py files under src_root (excluding tests/, __pycache__, .git),
    scans each line for stub patterns, and classifies each match based on
    whether the file is in dgm_engine.SAFETY_EXCLUDED_FILES.

    Returns list of:
    {
        "file": "stock_posting.py",
        "file_path": "erpclaw/scripts/erpclaw-setup/lib/erpclaw_lib/stock_posting.py",
        "line": 16,
        "text": "fifo: Not yet implemented (Phase 2+); falls back to moving_average",
        "is_safety_excluded": True,
        "classification": "human_required"  # or "os_addressable"
    }
    """
    if not os.path.isdir(src_root):
        return []

    stubs = []
    for dirpath, dirnames, filenames in os.walk(src_root):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]

        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r") as f:
                    lines = f.readlines()
            except (OSError, UnicodeDecodeError):
                continue

            for line_no, line in enumerate(lines, start=1):
                m = _STUB_PATTERNS.search(line)
                if m:
                    is_safety = fname in SAFETY_EXCLUDED_FILES
                    stubs.append({
                        "gap_type": "stub",
                        "file": fname,
                        "file_path": os.path.relpath(fpath, src_root),
                        "line": line_no,
                        "text": line.strip(),
                        "is_safety_excluded": is_safety,
                        "classification": "human_required" if is_safety else "os_addressable",
                        "severity": "medium" if is_safety else "low",
                        "description": (
                            f"Stub in {fname}:{line_no} — {line.strip()}"
                        ),
                        "suggested_action": (
                            f"Human review required for {fname}:{line_no}"
                            if is_safety
                            else f"OS can address stub in {fname}:{line_no}"
                        ),
                    })

    # Sort: human_required first, then os_addressable, then by file+line
    class_order = {"human_required": 0, "os_addressable": 1}
    stubs.sort(key=lambda s: (class_order.get(s["classification"], 2), s["file"], s["line"]))
    return stubs


# ---------------------------------------------------------------------------
# Log gaps to improvement_log
# ---------------------------------------------------------------------------

def _log_gaps_to_improvement_log(gaps, db_path=None):
    """Log each gap as a 'coverage' improvement with source='gap_detector'."""
    for gap in gaps:
        args = type("Args", (), {
            "category": "coverage",
            "description": gap["description"],
            "source": "gap_detector",
            "evidence": json.dumps({k: v for k, v in gap.items() if k != "description"}),
            "expected_impact": None,
            "proposed_diff": None,
            "module_name_arg": gap.get("module_name"),
            "module_name": gap.get("module_name"),
            "db_path": db_path,
        })()
        handle_log_improvement(args)


# ---------------------------------------------------------------------------
# Action: detect-gaps
# ---------------------------------------------------------------------------

def handle_detect_gaps(args):
    """Analyze action_call_log for patterns indicating missing functionality.

    Uses six detection methods:
      1. Error pattern analysis (actions failing consistently)
      2. Workflow gap analysis (long gaps between action pairs)
      3. Industry gap analysis (standard modules not installed)
      4. Schema-code divergence (tables with zero/minimal code references)
      5. Stub detection (TODO / Not yet implemented markers in production code)
      6. Feature completeness (compare domain actions against industry-standard matrix)

    Returns list of gaps with gap_type, description, severity, suggested_action.
    All gaps are logged to erpclaw_improvement_log.
    """
    db_path = getattr(args, "db_path", None)
    registry_path = getattr(args, "registry_path", None)
    src_root = getattr(args, "src_root", None)

    registry = _load_registry(registry_path)

    conn = get_connection(db_path)
    try:
        all_gaps = []

        # Method 1: Error pattern analysis
        error_gaps = _detect_error_patterns(conn)
        all_gaps.extend(error_gaps)

        # Method 2: Workflow gap analysis
        workflow_gaps = _detect_workflow_gaps(conn)
        all_gaps.extend(workflow_gaps)

        # Method 3: Industry gap analysis
        industry_gaps = _detect_industry_gaps(conn, registry)
        all_gaps.extend(industry_gaps)
    finally:
        conn.close()

    # Method 4: Schema-code divergence (file-based, no DB needed)
    schema_gaps = []
    if src_root and os.path.isdir(src_root):
        schema_gaps = detect_schema_code_divergence(src_root)
        all_gaps.extend(schema_gaps)

    # Method 5: Stub detection (file-based, no DB needed)
    stub_gaps = []
    if src_root and os.path.isdir(src_root):
        stub_gaps = detect_stubs(src_root)
        all_gaps.extend(stub_gaps)

    # Method 6: Feature completeness (file-based, no DB needed)
    feature_gaps = []
    if src_root and os.path.isdir(src_root):
        raw_gaps = check_feature_completeness(src_root)
        for fg in raw_gaps:
            feature_gaps.append({
                "gap_type": "feature_completeness",
                "domain": fg["domain"],
                "feature": fg["feature"],
                "priority": fg["priority"],
                "severity": "high" if fg["severity"] == "must-have" else "medium",
                "description": (
                    f"Feature '{fg['feature']}' is missing from {fg['domain']} domain. "
                    f"{fg['description']} (Priority: {fg['priority']}, Standard: {fg['standard']})"
                ),
                "suggested_action": (
                    f"Implement {fg['feature']} in {fg['domain']}: "
                    f"expected actions {fg['expected_actions']}"
                ),
                "expected_actions": fg["expected_actions"],
            })
        all_gaps.extend(feature_gaps)

    # Log all gaps to improvement_log
    if all_gaps:
        _log_gaps_to_improvement_log(all_gaps, db_path=db_path)

    return {
        "result": "ok",
        "total_gaps": len(all_gaps),
        "gaps_by_type": {
            "error_pattern": len(error_gaps),
            "workflow_gap": len(workflow_gaps),
            "industry_gap": len(industry_gaps),
            "schema_code_divergence": len(schema_gaps),
            "stub": len(stub_gaps),
            "feature_completeness": len(feature_gaps),
        },
        "gaps": all_gaps,
    }


# ---------------------------------------------------------------------------
# Action: detect-schema-divergence
# ---------------------------------------------------------------------------

def handle_detect_schema_divergence(args):
    """Detect tables defined in schema files with zero or minimal code references.

    Requires --src-root pointing to the project src/ directory.
    """
    src_root = getattr(args, "src_root", None)
    if not src_root or not os.path.isdir(src_root):
        return {"error": "Missing or invalid --src-root path"}

    gaps = detect_schema_code_divergence(src_root)
    no_code = [g for g in gaps if g["status"] == "no_code"]
    minimal = [g for g in gaps if g["status"] == "minimal_code"]

    return {
        "result": "ok",
        "total": len(gaps),
        "no_code_count": len(no_code),
        "minimal_code_count": len(minimal),
        "gaps": gaps,
    }


# ---------------------------------------------------------------------------
# Action: detect-stubs
# ---------------------------------------------------------------------------

def handle_detect_stubs(args):
    """Detect TODO / Not yet implemented / placeholder stubs in production code.

    Requires --src-root pointing to the project src/ directory.
    """
    src_root = getattr(args, "src_root", None)
    if not src_root or not os.path.isdir(src_root):
        return {"error": "Missing or invalid --src-root path"}

    stubs = detect_stubs(src_root)
    human = [s for s in stubs if s["classification"] == "human_required"]
    os_addr = [s for s in stubs if s["classification"] == "os_addressable"]

    return {
        "result": "ok",
        "total": len(stubs),
        "human_required_count": len(human),
        "os_addressable_count": len(os_addr),
        "stubs": stubs,
    }


# ---------------------------------------------------------------------------
# Action: suggest-modules
# ---------------------------------------------------------------------------

def handle_suggest_modules(args):
    """Generate prioritized module suggestions based on multiple signals.

    Ranking factors:
      1. Industry match (from company's industry/onboarding profile)
      2. Usage intensity in related domains (from action_call_log)
      3. Dependency compatibility (from module_registry.json "requires" field)
      4. Already-installed modules (excluded)

    Returns ranked suggestions with module_name, relevance_score, reason, dependencies.
    """
    db_path = getattr(args, "db_path", None)
    registry_path = getattr(args, "registry_path", None)

    registry = _load_registry(registry_path)
    if not registry:
        return {"error": "Could not load module_registry.json"}

    conn = get_connection(db_path)
    try:
        installed = _get_installed_modules(conn)
        industry, size_tier = _get_company_industry(conn)

        # Get action usage counts by routed_to domain for usage intensity scoring
        usage_by_domain = {}
        try:
            rows = conn.execute(
                "SELECT routed_to, COUNT(*) as cnt FROM action_call_log "
                "GROUP BY routed_to"
            ).fetchall()
            for row in rows:
                usage_by_domain[row["routed_to"]] = row["cnt"]
        except sqlite3.OperationalError:
            pass
    finally:
        conn.close()

    suggestions = []

    for mod_name, mod_info in registry.items():
        # Skip already-installed modules and core
        if mod_name in installed or mod_name == "erpclaw":
            continue

        score = 0.0
        reasons = []

        # Factor 1: Industry match
        if industry:
            config = INDUSTRY_CONFIGS.get(industry)
            if config:
                tier = size_tier or "small"
                standard_modules = config["modules"].get(tier, config["modules"].get("small", []))
                if mod_name in standard_modules:
                    score += 50.0
                    reasons.append(
                        f"Standard module for {config['display_name']} ({tier} tier)"
                    )

        # Factor 2: Usage intensity in related domains
        # Check if any of the module's tags overlap with heavily-used domains
        tags = set(mod_info.get("tags", []))
        for domain, count in usage_by_domain.items():
            # Simple heuristic: if the domain name overlaps with module tags
            domain_lower = domain.lower().replace("erpclaw-", "").replace("-", " ")
            for tag in tags:
                if tag.replace("-", " ") in domain_lower or domain_lower in tag.replace("-", " "):
                    intensity_score = min(count * 0.5, 30.0)
                    score += intensity_score
                    reasons.append(
                        f"Related domain '{domain}' used {count} times"
                    )
                    break

        # Factor 3: Dependency compatibility
        requires = mod_info.get("requires", [])
        deps_met = all(dep in installed or dep == "erpclaw" for dep in requires)

        if not deps_met:
            # Penalize if dependencies not met
            score -= 20.0
            missing_deps = [d for d in requires if d not in installed and d != "erpclaw"]
            reasons.append(
                f"Missing dependencies: {', '.join(missing_deps)}"
            )
        elif requires:
            # Bonus for having all dependencies already installed
            score += 10.0
            reasons.append("All dependencies already installed")

        # Factor 4: Category bonus — verticals score higher for empty setups
        category = mod_info.get("category", "")
        if category == "vertical":
            score += 5.0
        elif category == "sub-vertical":
            # Sub-verticals need their parent — only suggest if parent installed
            if not deps_met:
                score -= 10.0

        # Only suggest modules with positive score or industry match
        if score > 0:
            suggestions.append({
                "module_name": mod_name,
                "display_name": mod_info.get("display_name", mod_name),
                "relevance_score": round(score, 1),
                "reason": "; ".join(reasons) if reasons else "General expansion module",
                "dependencies": requires,
                "category": category,
                "action_count": mod_info.get("action_count", 0),
            })

    # Sort by relevance_score descending
    suggestions.sort(key=lambda s: s["relevance_score"], reverse=True)

    return {
        "result": "ok",
        "industry": industry,
        "size_tier": size_tier,
        "installed_count": len(installed),
        "suggestion_count": len(suggestions),
        "suggestions": suggestions,
    }
