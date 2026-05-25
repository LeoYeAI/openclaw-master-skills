#!/usr/bin/env python3
"""ERPClaw OS — Tier Classification System

Classifies every operation into a risk tier for deployment autonomy:
  Tier 0: Fully autonomous (read-only, draft creation)
  Tier 1: Guardrailed autonomous (GL-writing submits, cancellations)
  Tier 2: Human-approved (schema changes, module generation, configuration)
  Tier 3: Human-only (core file modifications, DROP TABLE, GL pipeline changes)

Classification is deployment-time, not runtime. Used by the auto-deploy
pipeline (2c) to decide whether a module deploys automatically or queues
for human review.
"""
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

TIER_0 = 0  # Read-only: list-*, get-*, search-*, available-*, status queries
TIER_1 = 1  # Validated writes: add-*, update-*, submit-*, cancel-*, delete-*, create-*, approve-*
TIER_2 = 2  # Schema/module changes: generate-module, configure-module, install-*, schema-*
TIER_3 = 3  # Core modifications: DROP TABLE, GL pipeline changes, constitution edits

TIER_NAMES = {
    TIER_0: "fully_autonomous",
    TIER_1: "guardrailed_autonomous",
    TIER_2: "human_approved",
    TIER_3: "human_only",
}

TIER_DESCRIPTIONS = {
    TIER_0: "Read-only operations. No data modification. Auto-deploy without review.",
    TIER_1: "Write operations with GL validation. Auto-deploy with audit trail.",
    TIER_2: "Schema changes, module generation, configuration. Requires human approval.",
    TIER_3: "Core modifications, DROP TABLE, GL pipeline changes. Human-only, never auto-deploy.",
}


# ---------------------------------------------------------------------------
# Classification rules — ordered by specificity (most specific first)
# ---------------------------------------------------------------------------

# Exact action → tier overrides (highest priority)
EXACT_ACTION_TIER = {
    # Tier 3: Core-modifying operations
    "regenerate-skill-md": TIER_2,  # Rewrites SKILL.md but doesn't touch core logic

    # Tier 2: Module lifecycle
    "generate-module": TIER_2,
    "configure-module": TIER_2,
    "install-module": TIER_2,
    "remove-module": TIER_2,
    "update-modules": TIER_2,
    "install-suite": TIER_2,
    "deploy-module": TIER_2,
    "validate-module": TIER_2,
    "schema-plan": TIER_2,
    "schema-apply": TIER_2,
    "schema-rollback": TIER_2,
    "run-audit": TIER_2,

    # Tier 1: Read but could expose sensitive data
    "rebuild-action-cache": TIER_1,
    "onboard": TIER_1,

    # Tier 0: Safe read-only
    "seed-demo-data": TIER_1,  # Writes data but safe (demo only)
    "setup-company": TIER_1,   # Creates company — foundational write
}

# Prefix patterns → tier (checked in order, first match wins)
PREFIX_TIER_RULES = [
    # Tier 0 patterns (read-only)
    (r"^list-", TIER_0, "Read-only list operation"),
    (r"^get-", TIER_0, "Read-only get operation"),
    (r"^search-", TIER_0, "Read-only search operation"),
    (r"^available-", TIER_0, "Read-only catalog query"),
    (r"^module-status$", TIER_0, "Read-only status query"),
    (r"^list-profiles$", TIER_0, "Read-only profile listing"),
    (r"^list-articles$", TIER_0, "Read-only constitution listing"),
    (r"^list-industries$", TIER_0, "Read-only industry listing"),
    (r"^list-all-actions$", TIER_0, "Read-only action listing"),
    (r"^build-table-registry$", TIER_0, "Read-only registry build"),
    (r"^schema-drift$", TIER_0, "Read-only drift detection"),
    (r"^compliance-weather-status$", TIER_0, "Read-only compliance status"),
    (r"^classify-operation$", TIER_0, "Read-only tier classification"),
    (r"^deploy-audit-log$", TIER_0, "Read-only audit log query"),

    # Tier 1 patterns (data writes, validated)
    (r"^submit-", TIER_1, "Document submission with GL validation"),
    (r"^cancel-", TIER_1, "Document cancellation (reverse GL)"),
    (r"^approve-", TIER_1, "Approval workflow action"),
    (r"^reject-", TIER_1, "Rejection workflow action"),
    (r"^delete-", TIER_1, "Data deletion"),
    (r"^add-", TIER_1, "Draft creation (no GL until submit)"),
    (r"^update-", TIER_1, "Draft update"),
    (r"^create-", TIER_1, "Document derivation (create-from-parent)"),
    (r"^record-", TIER_1, "Record entry"),
    (r"^generate-", TIER_1, "Data generation (salary slips, invoices)"),
    (r"^import-", TIER_1, "Data import"),
    (r"^assign-", TIER_1, "Assignment operation"),
    (r"^activate-", TIER_1, "Activation operation"),
    (r"^complete-", TIER_1, "Completion operation"),
    (r"^convert-", TIER_1, "Conversion operation"),
    (r"^return-", TIER_1, "Return operation"),
    (r"^setup-", TIER_1, "Setup/initialization"),
    (r"^propose-", TIER_1, "Proposal creation"),
    (r"^accept-", TIER_1, "Acceptance operation"),
    (r"^deny-", TIER_1, "Denial operation"),
    (r"^terminate-", TIER_1, "Termination operation"),
    (r"^apply-", TIER_1, "Apply operation"),

    # Tier 2 patterns (module/schema operations)
    (r"^install-", TIER_2, "Module installation"),
    (r"^schema-", TIER_2, "Schema modification"),
    (r"^deploy-", TIER_2, "Deployment operation"),
]

# Content-based escalation patterns (applied after prefix classification)
# If an action's code contains these patterns, escalate to higher tier
ESCALATION_PATTERNS = [
    (r"DROP\s+TABLE", TIER_3, "Contains DROP TABLE — core destructive operation"),
    (r"ALTER\s+TABLE.*DROP\s+COLUMN", TIER_3, "Contains ALTER TABLE DROP COLUMN"),
    (r"gl_posting\.py", TIER_3, "Modifies GL posting pipeline"),
    (r"stock_posting\.py", TIER_3, "Modifies stock posting pipeline"),
    (r"cross_skill\.py", TIER_3, "Modifies cross-skill library"),
]


# ---------------------------------------------------------------------------
# Classification engine
# ---------------------------------------------------------------------------

def classify_action(action_name, module_name=None, action_code=None):
    """Classify a single action into a tier.

    Args:
        action_name: kebab-case action name (e.g., "list-customers")
        module_name: optional module that owns this action
        action_code: optional source code of the action handler (for content analysis)

    Returns:
        dict with keys: action_name, module_name, tier, tier_name, reasoning
    """
    tier = None
    reasoning = None

    # Step 1: Check exact overrides
    if action_name in EXACT_ACTION_TIER:
        tier = EXACT_ACTION_TIER[action_name]
        reasoning = f"Exact match in override table"

    # Step 2: Check prefix patterns
    if tier is None:
        for pattern, pattern_tier, description in PREFIX_TIER_RULES:
            if re.match(pattern, action_name):
                tier = pattern_tier
                reasoning = description
                break

    # Step 3: Default to Tier 1 for unknown actions
    if tier is None:
        tier = TIER_1
        reasoning = "Unknown action pattern, defaulting to Tier 1 (guardrailed)"

    # Step 4: Content-based escalation (only if code provided)
    if action_code and tier < TIER_3:
        for pattern, escalation_tier, description in ESCALATION_PATTERNS:
            if re.search(pattern, action_code, re.IGNORECASE):
                if escalation_tier > tier:
                    reasoning = f"Escalated from Tier {tier} to {escalation_tier}: {description}"
                    tier = escalation_tier
                    break

    # Step 5: Namespace prefix handling
    # Actions with module namespace prefixes (e.g., "dental-add-patient")
    # inherit the tier of the base action pattern
    if module_name and module_name != "erpclaw":
        # Strip known module prefixes to classify base action
        prefixes_to_strip = [
            "dental-", "vet-", "mental-", "homehealth-",
            "highered-", "finaid-", "k12-", "lms-", "sched-", "statereport-",
            "prop-", "propcom-",
            "retail-", "construct-", "agri-", "auto-", "food-", "hotel-",
            "legal-", "nonprofit-",
            "crm-", "analytics-", "ai-",
            "mfg-", "project-", "asset-", "quality-", "support-",
            "alert-", "approval-", "compliance-", "doc-", "esign-",
            "fleet-", "loan-", "logistics-", "maint-", "plan-", "pos-",
            "selfservice-", "treasury-",
            "intg-", "region-",
            "groom-", "storage-", "tattoo-",
        ]
        base_action = action_name
        for p in prefixes_to_strip:
            if action_name.startswith(p):
                base_action = action_name[len(p):]
                break

        if base_action != action_name:
            base_result = classify_action(base_action)
            if base_result["tier"] != tier:
                tier = base_result["tier"]
                reasoning = f"Namespaced action '{action_name}' → base '{base_action}' classified as Tier {tier}"

    return {
        "action_name": action_name,
        "module_name": module_name or "unknown",
        "tier": tier,
        "tier_name": TIER_NAMES.get(tier, "unknown"),
        "reasoning": reasoning,
    }


def classify_all_actions(action_map):
    """Classify all actions from an ACTION_MAP dict.

    Args:
        action_map: dict of {action_name: module_name}

    Returns:
        dict with:
            classifications: list of classification dicts
            summary: tier counts
            unclassified: list (should be empty)
    """
    classifications = []
    tier_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for action_name, module_name in sorted(action_map.items()):
        result = classify_action(action_name, module_name)
        classifications.append(result)
        tier_counts[result["tier"]] += 1

    return {
        "classifications": classifications,
        "total": len(classifications),
        "summary": {
            "tier_0_read_only": tier_counts[0],
            "tier_1_guardrailed": tier_counts[1],
            "tier_2_human_approved": tier_counts[2],
            "tier_3_human_only": tier_counts[3],
        },
        "unclassified": [],  # All actions get classified (default to Tier 1)
    }


def classify_with_override(action_name, module_name, tier_override, override_by,
                           override_reason, db_path=None):
    """Classify an action with a human override, persisting to DB.

    Args:
        action_name: action to classify
        module_name: owning module
        tier_override: human-specified tier (0-3)
        override_by: human identifier
        override_reason: reason for override
        db_path: optional DB path

    Returns:
        dict with classification including override info
    """
    if tier_override not in (0, 1, 2, 3):
        return {"error": f"Invalid tier: {tier_override}. Must be 0, 1, 2, or 3."}

    # Get auto-classification first
    auto_result = classify_action(action_name, module_name)

    # Apply override
    result = {
        "action_name": action_name,
        "module_name": module_name,
        "tier": tier_override,
        "tier_name": TIER_NAMES.get(tier_override, "unknown"),
        "reasoning": f"Human override by {override_by}: {override_reason}",
        "auto_tier": auto_result["tier"],
        "auto_reasoning": auto_result["reasoning"],
        "override_by": override_by,
        "override_reason": override_reason,
    }

    # Persist to DB if path provided
    if db_path:
        _persist_classification(db_path, result)

    return result


def get_persisted_classification(action_name, db_path):
    """Get a persisted classification (including human overrides) from DB.

    Returns None if no persisted classification exists.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM erpclaw_tier_classification WHERE action_name = ?",
            (action_name,)
        ).fetchone()
        conn.close()
        if row:
            return dict(row)
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        pass
    return None


def classify_with_persistence(action_name, module_name, db_path):
    """Classify an action, checking DB for human overrides first.

    Order of precedence:
    1. Human override in DB (if exists)
    2. Auto-classification from rules
    """
    # Check for persisted override
    persisted = get_persisted_classification(action_name, db_path)
    if persisted and persisted.get("override_by"):
        return {
            "action_name": action_name,
            "module_name": module_name,
            "tier": persisted["tier"],
            "tier_name": TIER_NAMES.get(persisted["tier"], "unknown"),
            "reasoning": f"Human override by {persisted['override_by']}: {persisted['override_reason']}",
            "source": "human_override",
        }

    # Auto-classify
    result = classify_action(action_name, module_name)
    result["source"] = "auto"

    # Persist auto-classification
    _persist_classification(db_path, result)

    return result


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def ensure_tier_table(db_path):
    """Create the erpclaw_tier_classification table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.query import ddl_now
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS erpclaw_tier_classification (
            action_name     TEXT PRIMARY KEY,
            module_name     TEXT NOT NULL,
            tier            INTEGER NOT NULL CHECK(tier IN (0, 1, 2, 3)),
            reasoning       TEXT,
            classified_at   TEXT DEFAULT ({ddl_now()}),
            override_by     TEXT,
            override_reason TEXT
        )
    """)
    conn.commit()
    conn.close()


def _persist_classification(db_path, result):
    """Persist a classification result to the database."""
    try:
        conn = sqlite3.connect(db_path)
        from erpclaw_lib.db import setup_pragmas
        setup_pragmas(conn)
        conn.execute("""
            INSERT INTO erpclaw_tier_classification
                (action_name, module_name, tier, reasoning, classified_at, override_by, override_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(action_name) DO UPDATE SET
                module_name = excluded.module_name,
                tier = excluded.tier,
                reasoning = excluded.reasoning,
                classified_at = excluded.classified_at,
                override_by = excluded.override_by,
                override_reason = excluded.override_reason
        """, (
            result["action_name"],
            result.get("module_name", "unknown"),
            result["tier"],
            result.get("reasoning"),
            datetime.now(timezone.utc).isoformat(),
            result.get("override_by"),
            result.get("override_reason"),
        ))
        conn.commit()
        conn.close()
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        pass  # Non-fatal: classification works without persistence


# ---------------------------------------------------------------------------
# Action handler (called from erpclaw-os db_query.py)
# ---------------------------------------------------------------------------

def handle_classify_operation(args):
    """Classify an action's tier level.

    --action-name: specific action to classify
    --module-name: module that owns the action (optional)
    --classify-all: classify all actions in ACTION_MAP
    --override-tier: human override tier (0-3)
    --override-by: who is overriding
    --override-reason: why
    """
    action_name = getattr(args, "action_name", None)
    module_name = getattr(args, "module_name_arg", None)
    classify_all = getattr(args, "classify_all", False)
    override_tier = getattr(args, "override_tier", None)
    override_by = getattr(args, "override_by", None)
    override_reason = getattr(args, "override_reason", None)
    db_path = getattr(args, "db_path", None)

    # Classify all actions
    if classify_all:
        # Load ACTION_MAP from core db_query.py
        action_map = _load_action_map()
        if not action_map:
            return {"error": "Could not load ACTION_MAP from core db_query.py"}
        result = classify_all_actions(action_map)
        return result

    # Single action classification
    if not action_name:
        return {"error": "--action-name is required (or use --classify-all)"}

    # Human override
    if override_tier is not None:
        if not override_by:
            return {"error": "--override-by is required when using --override-tier"}
        if not override_reason:
            return {"error": "--override-reason is required when using --override-tier"}
        return classify_with_override(
            action_name, module_name or "unknown",
            override_tier, override_by, override_reason, db_path
        )

    # Auto-classify (with DB persistence if db_path provided)
    if db_path:
        return classify_with_persistence(action_name, module_name or "unknown", db_path)
    else:
        return classify_action(action_name, module_name)


def _load_action_map():
    """Load ACTION_MAP from the core erpclaw db_query.py."""
    # Try to find core db_query.py relative to this file
    # erpclaw-os is at src/erpclaw/scripts/erpclaw-os/
    # core db_query is at src/erpclaw/scripts/db_query.py
    core_db_query = os.path.join(SCRIPT_DIR, "..", "db_query.py")
    core_db_query = os.path.normpath(core_db_query)

    if not os.path.exists(core_db_query):
        return None

    # Parse ACTION_MAP from the file using regex (avoid importing)
    try:
        with open(core_db_query, "r") as f:
            content = f.read()

        # Find ACTION_MAP dict
        match = re.search(r'ACTION_MAP\s*=\s*\{([^}]+)\}', content, re.DOTALL)
        if not match:
            return None

        action_map = {}
        for line in match.group(1).split('\n'):
            line = line.strip()
            # Match "action-name": "module-name",
            m = re.match(r'"([^"]+)"\s*:\s*"([^"]+)"', line)
            if m:
                action_map[m.group(1)] = m.group(2)

        return action_map if action_map else None
    except Exception:
        return None
