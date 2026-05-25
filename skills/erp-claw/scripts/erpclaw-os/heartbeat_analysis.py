#!/usr/bin/env python3
"""ERPClaw OS — Heartbeat Analysis Engine (Phase 3, Deliverable 3d)

Analyzes usage patterns from action_call_log and proposes improvements.
All proposals are logged through the improvement_log — heartbeat NEVER
deploys anything.

Four analysis modules:
  1. Usage pattern analysis — frequency, error rates, response times
  2. Gap detection — "unknown action" errors indicating missing functionality
  3. Optimization proposals — detect common multi-step workflows
  4. Module suggestions — cross-reference usage with module_registry.json

Actions:
  - heartbeat-analyze: Run full analysis cycle
  - heartbeat-report: Return latest analysis results
  - heartbeat-suggest: Return current active suggestions
"""
import json
import os
import sqlite3
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Add shared lib to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))

from erpclaw_lib.db import get_connection
from erpclaw_lib.query import Q, P, Table, Field, fn, Order, seconds_between

from improvement_log import handle_log_improvement

# Path to module_registry.json (relative to the scripts/ directory)
REGISTRY_PATH = os.path.join(
    os.path.dirname(SCRIPT_DIR),  # erpclaw/scripts/
    "module_registry.json",
)

# Thresholds
TOP_ACTIONS_LIMIT = 10
HIGH_ERROR_RATE_THRESHOLD = 0.10  # 10%
MIN_WORKFLOW_OCCURRENCES = 5
WORKFLOW_TIME_WINDOW_SECONDS = 60


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def _load_module_registry(registry_path=None):
    """Load module_registry.json and return the modules dict."""
    path = registry_path or REGISTRY_PATH
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("modules", {})
    except (json.JSONDecodeError, IOError):
        return {}


def _get_installed_modules(conn):
    """Get list of installed module names from erpclaw_module table.

    Falls back to empty set if the table doesn't exist.
    """
    try:
        rows = conn.execute(
            "SELECT name FROM erpclaw_module WHERE install_status = 'installed'"
        ).fetchall()
        return {r[0] for r in rows}
    except sqlite3.OperationalError:
        # Table doesn't exist — assume only core is installed
        return {"erpclaw"}


# ---------------------------------------------------------------------------
# 1. Usage Pattern Analysis
# ---------------------------------------------------------------------------

def _analyze_usage_patterns(conn):
    """Query action_call_log for action frequency, error rates, response times.

    Returns:
        dict with keys: most_used, never_used, highest_error, stats
    """
    t = Table("action_call_log")

    # Total call counts per action
    q = (
        Q.from_(t)
        .select(t.action_name, fn.Count(t.id).as_("call_count"))
        .groupby(t.action_name)
        .orderby(fn.Count(t.id), order=Order.desc)
    )
    sql = q.get_sql()
    try:
        rows = conn.execute(sql).fetchall()
    except sqlite3.OperationalError:
        return {"most_used": [], "never_used": [], "highest_error": [], "stats": {}}

    action_counts = {}
    for row in rows:
        action_counts[row[0]] = row[1]

    most_used = [
        {"action": name, "call_count": count}
        for name, count in sorted(action_counts.items(), key=lambda x: -x[1])[:TOP_ACTIONS_LIMIT]
    ]

    # Error rates — count rows where routed_to indicates error or action_name
    # contains markers. Since action_call_log tracks routed_to but not
    # success/error status directly, we detect errors by checking for
    # entries with status column if it exists, or by looking at the
    # error_message column.
    error_counts = {}
    try:
        err_rows = conn.execute(
            'SELECT action_name, COUNT(*) FROM action_call_log '
            'WHERE status = ? GROUP BY action_name',
            ("error",),
        ).fetchall()
        for row in err_rows:
            error_counts[row[0]] = row[1]
    except sqlite3.OperationalError:
        # status column doesn't exist — skip error rate analysis
        pass

    highest_error = []
    for action_name, err_count in error_counts.items():
        total = action_counts.get(action_name, err_count)
        if total > 0:
            error_rate = err_count / total
            if error_rate > HIGH_ERROR_RATE_THRESHOLD:
                highest_error.append({
                    "action": action_name,
                    "error_count": err_count,
                    "total_count": total,
                    "error_rate": round(error_rate, 4),
                })

    highest_error.sort(key=lambda x: -x["error_rate"])

    # Never-used actions: actions in the known set that have zero calls.
    # We try to read the known action list from the erpclaw_module_action table.
    never_used = []
    try:
        all_actions_rows = conn.execute(
            "SELECT DISTINCT action_name FROM erpclaw_module_action"
        ).fetchall()
        all_known = {r[0] for r in all_actions_rows}
        called = set(action_counts.keys())
        never_called = sorted(all_known - called)
        never_used = [{"action": a} for a in never_called]
    except sqlite3.OperationalError:
        pass

    return {
        "most_used": most_used,
        "never_used": never_used,
        "highest_error": highest_error,
        "stats": {
            "total_actions_called": len(action_counts),
            "total_call_count": sum(action_counts.values()),
        },
    }


# ---------------------------------------------------------------------------
# 2. Gap Detection
# ---------------------------------------------------------------------------

def _detect_gaps(conn):
    """Find 'unknown action' errors indicating missing functionality.

    Checks action_call_log for actions where routed_to is empty or
    contains 'unknown', or error_message contains 'unknown action'.

    Returns:
        list of dicts with action_name and occurrence_count
    """
    gaps = []

    # Strategy 1: Look for error_message containing "unknown action"
    try:
        rows = conn.execute(
            "SELECT action_name, COUNT(*) as cnt "
            "FROM action_call_log "
            "WHERE LOWER(error_message) LIKE LOWER(?) "
            "GROUP BY action_name "
            "ORDER BY cnt DESC",
            ("%unknown action%",),
        ).fetchall()
        for row in rows:
            gaps.append({
                "action": row[0],
                "occurrence_count": row[1],
                "detection_method": "error_message",
            })
    except sqlite3.OperationalError:
        pass

    # Strategy 2: Look for entries where status is 'error' and
    # the action is not in any known action table
    try:
        rows = conn.execute(
            "SELECT acl.action_name, COUNT(*) as cnt "
            "FROM action_call_log acl "
            "LEFT JOIN erpclaw_module_action ma ON acl.action_name = ma.action_name "
            "WHERE acl.status = 'error' AND ma.action_name IS NULL "
            "GROUP BY acl.action_name "
            "ORDER BY cnt DESC",
        ).fetchall()
        existing_actions = {g["action"] for g in gaps}
        for row in rows:
            if row[0] not in existing_actions:
                gaps.append({
                    "action": row[0],
                    "occurrence_count": row[1],
                    "detection_method": "unregistered_action",
                })
    except sqlite3.OperationalError:
        pass

    return gaps


# ---------------------------------------------------------------------------
# 3. Optimization Proposals
# ---------------------------------------------------------------------------

def _detect_workflow_patterns(conn):
    """Detect common multi-step workflows where user calls A then B
    within WORKFLOW_TIME_WINDOW_SECONDS consistently.

    Returns:
        list of dicts with action_a, action_b, occurrence_count
    """
    workflows = []

    # Self-join action_call_log: find pairs (A, B) where B follows A
    # within the time window, by the same user/session.
    # We use the timestamp column and session_id for grouping.
    try:
        # Dialect-aware seconds_between replaces julianday pattern
        secs_expr = seconds_between("b.timestamp", "a.timestamp").get_sql(quote_char=None)
        rows = conn.execute(
            f"SELECT a.action_name, b.action_name, COUNT(*) as cnt "
            f"FROM action_call_log a "
            f"JOIN action_call_log b "
            f"  ON a.session_id = b.session_id "
            f"  AND a.action_name != b.action_name "
            f"  AND b.timestamp > a.timestamp "
            f"  AND {secs_expr} <= ? "
            f"  AND NOT EXISTS ( "
            f"    SELECT 1 FROM action_call_log c "
            f"    WHERE c.session_id = a.session_id "
            f"      AND c.timestamp > a.timestamp "
            f"      AND c.timestamp < b.timestamp "
            f"  ) "
            f"GROUP BY a.action_name, b.action_name "
            f"HAVING COUNT(*) >= ? "
            f"ORDER BY cnt DESC",
            (WORKFLOW_TIME_WINDOW_SECONDS, MIN_WORKFLOW_OCCURRENCES),
        ).fetchall()
        for row in rows:
            workflows.append({
                "action_a": row[0],
                "action_b": row[1],
                "occurrence_count": row[2],
                "proposed_combined": f"{row[0]}-and-{row[1]}",
            })
    except sqlite3.OperationalError:
        pass

    return workflows


# ---------------------------------------------------------------------------
# 4. Module Suggestions
# ---------------------------------------------------------------------------

def _suggest_modules(conn, registry_path=None):
    """Based on usage intensity in specific domains, suggest uninstalled modules.

    Cross-references action_call_log with module_registry.json to find
    modules whose tags overlap with heavily-used domains.

    Returns:
        list of dicts with module_name, reason, relevance_score
    """
    registry = _load_module_registry(registry_path)
    if not registry:
        return []

    installed = _get_installed_modules(conn)

    # Count calls per routed_to domain
    domain_counts = {}
    try:
        rows = conn.execute(
            "SELECT routed_to, COUNT(*) as cnt "
            "FROM action_call_log "
            "GROUP BY routed_to "
            "ORDER BY cnt DESC"
        ).fetchall()
        for row in rows:
            domain_counts[row[0]] = row[1]
    except sqlite3.OperationalError:
        return []

    if not domain_counts:
        return []

    # Build a tag→module mapping for uninstalled modules
    tag_to_modules = defaultdict(list)
    for mod_name, mod_info in registry.items():
        if mod_name in installed:
            continue
        for tag in mod_info.get("tags", []):
            tag_to_modules[tag.lower()].append(mod_name)

    # Map domains to keywords for tag matching
    domain_keywords = {}
    for domain in domain_counts:
        # erpclaw-selling → ["selling"]
        # erpclaw-hr → ["hr"]
        parts = domain.replace("erpclaw-", "").split("-")
        domain_keywords[domain] = [p.lower() for p in parts if p]

    # Score uninstalled modules based on tag overlap with used domains
    module_scores = defaultdict(lambda: {"score": 0, "reasons": []})
    for domain, count in domain_counts.items():
        keywords = domain_keywords.get(domain, [])
        for keyword in keywords:
            for mod_name in tag_to_modules.get(keyword, []):
                module_scores[mod_name]["score"] += count
                module_scores[mod_name]["reasons"].append(
                    f"Heavy usage of '{domain}' ({count} calls) matches tag '{keyword}'"
                )

    # Also check for tag-based suggestions from action names themselves
    action_keywords = defaultdict(int)
    try:
        rows = conn.execute(
            "SELECT action_name, COUNT(*) as cnt "
            "FROM action_call_log "
            "GROUP BY action_name "
            "ORDER BY cnt DESC LIMIT 50"
        ).fetchall()
        for row in rows:
            parts = row[0].split("-")
            for part in parts:
                action_keywords[part.lower()] += row[1]
    except sqlite3.OperationalError:
        pass

    for keyword, count in action_keywords.items():
        for mod_name in tag_to_modules.get(keyword, []):
            if mod_name not in module_scores or count > module_scores[mod_name]["score"]:
                module_scores[mod_name]["score"] += count
                # Avoid duplicate reasons
                reason = f"Action keywords match tag '{keyword}' ({count} calls)"
                if reason not in module_scores[mod_name]["reasons"]:
                    module_scores[mod_name]["reasons"].append(reason)

    suggestions = []
    for mod_name, info in sorted(module_scores.items(), key=lambda x: -x[1]["score"]):
        if info["score"] > 0:
            suggestions.append({
                "module": mod_name,
                "relevance_score": info["score"],
                "reasons": info["reasons"][:3],  # Keep top 3 reasons
                "display_name": registry.get(mod_name, {}).get("display_name", mod_name),
            })

    return suggestions[:10]  # Top 10 suggestions


# ---------------------------------------------------------------------------
# Log proposals to improvement_log
# ---------------------------------------------------------------------------

def _log_proposal(db_path, category, description, evidence, module_name=None):
    """Log a heartbeat proposal via improvement_log.handle_log_improvement().

    Returns the result dict.
    """
    args = type("Args", (), {
        "category": category,
        "description": description,
        "source": "heartbeat",
        "evidence": json.dumps(evidence) if evidence else None,
        "expected_impact": None,
        "proposed_diff": None,
        "module_name_arg": module_name,
        "module_name": module_name,
        "db_path": db_path,
    })()
    return handle_log_improvement(args)


# ---------------------------------------------------------------------------
# Action: heartbeat-analyze
# ---------------------------------------------------------------------------

def handle_heartbeat_analyze(args):
    """Run full heartbeat analysis cycle.

    Queries action_call_log, runs all four analysis modules,
    and logs proposals to improvement_log.

    Returns: JSON summary of analysis (counts, top findings).
    """
    db_path = getattr(args, "db_path", None)
    registry_path = getattr(args, "registry_path", None)

    conn = get_connection(db_path)
    try:
        start_time = time.time()

        # 1. Usage pattern analysis
        usage = _analyze_usage_patterns(conn)

        # 2. Gap detection
        gaps = _detect_gaps(conn)

        # 3. Workflow optimization
        workflows = _detect_workflow_patterns(conn)

        # 4. Module suggestions
        suggestions = _suggest_modules(conn, registry_path)

        duration_ms = int((time.time() - start_time) * 1000)
    finally:
        conn.close()

    # Log proposals to improvement_log
    proposals_logged = 0

    # Log high-error actions
    for item in usage.get("highest_error", []):
        result = _log_proposal(
            db_path,
            category="performance",
            description=(
                f"Action '{item['action']}' has a {item['error_rate']:.0%} error rate "
                f"({item['error_count']}/{item['total_count']} calls). "
                f"Investigate and fix the root cause."
            ),
            evidence=item,
        )
        if result.get("result") == "ok":
            proposals_logged += 1

    # Log gap detections
    for gap in gaps:
        result = _log_proposal(
            db_path,
            category="coverage",
            description=(
                f"Users attempted action '{gap['action']}' {gap['occurrence_count']} times "
                f"but it does not exist. Consider adding this functionality."
            ),
            evidence=gap,
        )
        if result.get("result") == "ok":
            proposals_logged += 1

    # Log workflow optimization proposals
    for wf in workflows:
        result = _log_proposal(
            db_path,
            category="usability",
            description=(
                f"Users frequently call '{wf['action_a']}' followed by '{wf['action_b']}' "
                f"({wf['occurrence_count']} times within {WORKFLOW_TIME_WINDOW_SECONDS}s). "
                f"Consider a combined action '{wf['proposed_combined']}'."
            ),
            evidence=wf,
        )
        if result.get("result") == "ok":
            proposals_logged += 1

    # Log module suggestions
    for sug in suggestions:
        result = _log_proposal(
            db_path,
            category="coverage",
            description=(
                f"Consider installing module '{sug['display_name']}' ({sug['module']}). "
                f"Usage patterns suggest relevance (score: {sug['relevance_score']})."
            ),
            evidence=sug,
            module_name=sug["module"],
        )
        if result.get("result") == "ok":
            proposals_logged += 1

    return {
        "result": "ok",
        "analysis_summary": {
            "most_used_actions": len(usage.get("most_used", [])),
            "never_used_actions": len(usage.get("never_used", [])),
            "high_error_actions": len(usage.get("highest_error", [])),
            "gaps_detected": len(gaps),
            "workflow_patterns": len(workflows),
            "module_suggestions": len(suggestions),
        },
        "proposals_logged": proposals_logged,
        "usage": usage,
        "gaps": gaps,
        "workflows": workflows,
        "module_suggestions": suggestions,
        "duration_ms": duration_ms,
    }


# ---------------------------------------------------------------------------
# Action: heartbeat-report
# ---------------------------------------------------------------------------

def handle_heartbeat_report(args):
    """Return latest heartbeat analysis results.

    Reads from erpclaw_improvement_log where source='heartbeat',
    ordered by proposed_at DESC. Supports --limit for pagination.
    """
    db_path = getattr(args, "db_path", None)
    limit = getattr(args, "limit", 50) or 50

    conn = get_connection(db_path)
    try:
        t = Table("erpclaw_improvement_log")
        q = (
            Q.from_(t)
            .select(t.star)
            .where(t.source == P())
            .orderby(t.proposed_at, order=Order.desc)
            .limit(P())
        )
        sql = q.get_sql()
        rows = conn.execute(sql, ("heartbeat", limit)).fetchall()

        # Get column names
        cursor = conn.execute(
            "SELECT * FROM erpclaw_improvement_log LIMIT 0"
        )
        columns = [desc[0] for desc in cursor.description]

        items = []
        for row in rows:
            item = dict(zip(columns, row))
            # Parse JSON fields
            for json_field in ("evidence", "expected_impact", "proposed_diff"):
                if item.get(json_field):
                    try:
                        item[json_field] = json.loads(item[json_field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            items.append(item)

        # Count total
        count_q = (
            Q.from_(t)
            .select(fn.Count(t.id).as_("cnt"))
            .where(t.source == P())
        )
        total = conn.execute(count_q.get_sql(), ("heartbeat",)).fetchone()[0]
    finally:
        conn.close()

    return {
        "result": "ok",
        "items": items,
        "total": total,
        "limit": limit,
    }


# ---------------------------------------------------------------------------
# Action: heartbeat-suggest
# ---------------------------------------------------------------------------

def handle_heartbeat_suggest(args):
    """Return current active suggestions (status='proposed', source='heartbeat').

    Grouped by category.
    """
    db_path = getattr(args, "db_path", None)

    conn = get_connection(db_path)
    try:
        t = Table("erpclaw_improvement_log")
        q = (
            Q.from_(t)
            .select(t.star)
            .where(t.source == P())
            .where(t.status == P())
            .orderby(t.proposed_at, order=Order.desc)
        )
        sql = q.get_sql()
        rows = conn.execute(sql, ("heartbeat", "proposed")).fetchall()

        # Get column names
        cursor = conn.execute(
            "SELECT * FROM erpclaw_improvement_log LIMIT 0"
        )
        columns = [desc[0] for desc in cursor.description]

        items = []
        by_category = defaultdict(list)
        for row in rows:
            item = dict(zip(columns, row))
            for json_field in ("evidence", "expected_impact", "proposed_diff"):
                if item.get(json_field):
                    try:
                        item[json_field] = json.loads(item[json_field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            items.append(item)
            by_category[item["category"]].append(item)
    finally:
        conn.close()

    return {
        "result": "ok",
        "suggestions": items,
        "total": len(items),
        "by_category": {k: len(v) for k, v in by_category.items()},
    }
