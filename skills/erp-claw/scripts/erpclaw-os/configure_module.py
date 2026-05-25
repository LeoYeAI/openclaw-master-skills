"""ERPClaw OS Industry Configuration Engine.

Configures installed modules for a specific industry by:
1. Creating industry-specific GL accounts (chart of accounts overlay)
2. Determining recommended modules based on industry + size tier
3. Returning compliance items to track

Does NOT write to tables owned by other modules. Creates accounts in the
core `account` table (owned by erpclaw-gl) using direct INSERT, which is
permitted because configure-module is part of core erpclaw.

Idempotent: re-running with the same industry + company_id will skip
accounts that already exist (matched by name + company_id).
"""
import os
import sqlite3
import sys
import uuid

# Add shared lib to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))

# Import industry configs (same package)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from industry_configs import INDUSTRY_CONFIGS, list_industries

# Valid size tiers
VALID_SIZE_TIERS = {"small", "medium", "large", "enterprise"}


def _get_connection(db_path=None):
    """Get a database connection, using erpclaw_lib if available."""
    try:
        from erpclaw_lib.db import get_connection
        if db_path:
            os.environ["ERPCLAW_DB_PATH"] = db_path
        conn = get_connection()
        if db_path:
            os.environ.pop("ERPCLAW_DB_PATH", None)
        return conn
    except ImportError:
        path = db_path or os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        from erpclaw_lib.db import setup_pragmas as _sp
        _sp(conn)
        return conn


def _resolve_parent_account(conn, parent_name, company_id):
    """Find a parent group account by name for a given company.

    Returns the account ID if found, None otherwise.
    Parent accounts are group accounts that were created by setup-chart-of-accounts.
    """
    row = conn.execute(
        "SELECT id FROM account WHERE name = ? AND company_id = ? AND is_group = 1",
        (parent_name, company_id),
    ).fetchone()
    if row:
        return row["id"]
    return None


def _account_exists(conn, name, company_id):
    """Check if an account with the given name already exists for this company."""
    row = conn.execute(
        "SELECT id FROM account WHERE name = ? AND company_id = ?",
        (name, company_id),
    ).fetchone()
    return row is not None


def configure_module(
    industry: str,
    company_id: str,
    size_tier: str = "small",
    db_path: str = None,
) -> dict:
    """Configure installed modules for a specific industry.

    Args:
        industry: e.g., "dental_practice", "general_contractor", "restaurant"
        company_id: UUID of the company to configure
        size_tier: small (1-10), medium (11-100), large (100+), enterprise (1000+)
        db_path: database path (default from erpclaw_lib.db)

    Returns: {
        "result": "pass" | "fail",
        "industry": str,
        "display_name": str,
        "size_tier": str,
        "accounts_created": int,
        "accounts_skipped": int,
        "accounts_failed": list[dict],
        "modules_recommended": list[str],
        "compliance_items": list[str],
        "configuration_applied": list[str],
    }
    """
    # Validate inputs
    if not company_id:
        return {
            "result": "fail",
            "error": "company_id is required",
        }

    if size_tier not in VALID_SIZE_TIERS:
        return {
            "result": "fail",
            "error": f"Invalid size_tier: {size_tier}. Must be one of: {', '.join(sorted(VALID_SIZE_TIERS))}",
        }

    if industry not in INDUSTRY_CONFIGS:
        available = sorted(INDUSTRY_CONFIGS.keys())
        return {
            "result": "fail",
            "error": f"Unknown industry: {industry}",
            "available_industries": available,
        }

    config = INDUSTRY_CONFIGS[industry]
    conn = _get_connection(db_path)

    try:
        # Verify company exists
        company_row = conn.execute(
            "SELECT id, name FROM company WHERE id = ?", (company_id,)
        ).fetchone()
        if not company_row:
            return {
                "result": "fail",
                "error": f"Company not found: {company_id}",
            }

        # --- Step 1: Create industry-specific accounts ---
        accounts_created = 0
        accounts_skipped = 0
        accounts_failed = []
        configuration_applied = []

        for acct_def in config["accounts"]:
            acct_name = acct_def["name"]

            # Skip if already exists (idempotency)
            if _account_exists(conn, acct_name, company_id):
                accounts_skipped += 1
                continue

            # Resolve parent account
            parent_id = None
            if acct_def.get("parent"):
                parent_id = _resolve_parent_account(conn, acct_def["parent"], company_id)
                # Parent not found is not fatal — account is created without parent

            # Calculate depth
            depth = 0
            if parent_id:
                parent_row = conn.execute(
                    "SELECT depth FROM account WHERE id = ?", (parent_id,)
                ).fetchone()
                if parent_row:
                    depth = parent_row["depth"] + 1

            # Determine balance direction
            root_type = acct_def["root_type"]
            balance_direction = "debit_normal"
            if root_type in ("liability", "equity", "income"):
                balance_direction = "credit_normal"

            try:
                acct_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT INTO account
                       (id, name, parent_id, root_type, account_type,
                        is_group, balance_direction, company_id, depth)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        acct_id,
                        acct_name,
                        parent_id,
                        root_type,
                        acct_def.get("account_type"),
                        acct_def.get("is_group", 0),
                        balance_direction,
                        company_id,
                        depth,
                    ),
                )
                accounts_created += 1
            except sqlite3.IntegrityError as e:
                accounts_failed.append({"name": acct_name, "error": str(e)})

        if accounts_created > 0:
            conn.commit()
            configuration_applied.append(
                f"Created {accounts_created} industry-specific GL accounts"
            )

        # --- Step 2: Determine recommended modules ---
        modules_for_tier = config["modules"].get(size_tier, config["modules"].get("small", []))
        configuration_applied.append(
            f"Recommended {len(modules_for_tier)} modules for {size_tier} {config['display_name']}"
        )

        # --- Step 3: Return compliance items ---
        compliance_items = config.get("compliance_items", [])
        if compliance_items:
            configuration_applied.append(
                f"Identified {len(compliance_items)} compliance items to track"
            )

        # --- Step 4: Record configuration in erpclaw_module_config if table exists ---
        try:
            import json as _json
            config_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO erpclaw_module_config
                   (id, module_name, config_type, config_data, industry, size_tier)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    config_id,
                    "erpclaw",
                    "industry_config",
                    _json.dumps({
                        "accounts_created": accounts_created,
                        "accounts_skipped": accounts_skipped,
                        "modules_recommended": modules_for_tier,
                        "compliance_items": compliance_items,
                    }),
                    industry,
                    size_tier,
                ),
            )
            conn.commit()
            configuration_applied.append("Recorded configuration in erpclaw_module_config")
        except sqlite3.OperationalError:
            # Table doesn't exist yet — not fatal
            pass

        return {
            "result": "pass",
            "industry": industry,
            "display_name": config["display_name"],
            "size_tier": size_tier,
            "company_id": company_id,
            "accounts_created": accounts_created,
            "accounts_skipped": accounts_skipped,
            "accounts_failed": accounts_failed,
            "modules_recommended": modules_for_tier,
            "compliance_items": compliance_items,
            "configuration_applied": configuration_applied,
        }

    finally:
        conn.close()
