#!/usr/bin/env python3
"""ERPClaw Advanced Accounting -- db_query.py (unified router)

ASC 606 revenue recognition, ASC 842 lease accounting, intercompany transactions,
and multi-entity consolidation. 50 actions routed through this single entry point.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sys

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.response import ok, err
except ImportError:
    import json as _json
    print(_json.dumps({
        "status": "error",
        "error": "ERPClaw foundation not installed. Install erpclaw-setup first: clawhub install erpclaw-setup",
        "suggestion": "clawhub install erpclaw-setup"
    }))
    sys.exit(1)

# Add this script's directory so domain modules can be imported
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from revenue import ACTIONS as REVENUE_ACTIONS  # noqa: E402
from leases import ACTIONS as LEASE_ACTIONS  # noqa: E402
from intercompany import ACTIONS as IC_ACTIONS  # noqa: E402
from consolidation import ACTIONS as CONSOL_ACTIONS  # noqa: E402
from reports import ACTIONS as REPORT_ACTIONS  # noqa: E402

# Merge all domain actions
ACTIONS = {}
ACTIONS.update(REVENUE_ACTIONS)
ACTIONS.update(LEASE_ACTIONS)
ACTIONS.update(IC_ACTIONS)
ACTIONS.update(CONSOL_ACTIONS)
ACTIONS.update(REPORT_ACTIONS)

SKILL = "erpclaw-accounting-adv"
REQUIRED_TABLES = [
    "company", "advacct_revenue_contract", "advacct_lease",
    "advacct_ic_transaction", "advacct_consolidation_group",
]


def main():
    parser = argparse.ArgumentParser(description=SKILL)
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Entity IDs
    parser.add_argument("--id")
    parser.add_argument("--company-id")
    parser.add_argument("--contract-id")
    parser.add_argument("--obligation-id")
    parser.add_argument("--lease-id")
    parser.add_argument("--group-id")

    # Revenue fields
    parser.add_argument("--customer-name")
    parser.add_argument("--contract-number")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--total-value")
    parser.add_argument("--contract-status")
    parser.add_argument("--name")
    parser.add_argument("--standalone-price")
    parser.add_argument("--recognition-method")
    parser.add_argument("--recognition-basis")
    parser.add_argument("--pct-complete")
    parser.add_argument("--description")
    parser.add_argument("--estimated-amount")
    parser.add_argument("--constraint-amount")
    parser.add_argument("--method")
    parser.add_argument("--probability")

    # Lease fields
    parser.add_argument("--lessee-name")
    parser.add_argument("--lessor-name")
    parser.add_argument("--asset-description")
    parser.add_argument("--lease-type")
    parser.add_argument("--term-months", type=int)
    parser.add_argument("--monthly-payment")
    parser.add_argument("--annual-escalation")
    parser.add_argument("--discount-rate")
    parser.add_argument("--purchase-option-price")
    parser.add_argument("--lease-status")
    parser.add_argument("--payment-date")
    parser.add_argument("--payment-amount")

    # Intercompany fields
    parser.add_argument("--from-company-id")
    parser.add_argument("--to-company-id")
    parser.add_argument("--transaction-type")
    parser.add_argument("--amount")
    parser.add_argument("--currency")
    parser.add_argument("--transfer-price-method")
    parser.add_argument("--ic-status")
    parser.add_argument("--markup-pct")
    parser.add_argument("--effective-date")
    parser.add_argument("--expiry-date")

    # Consolidation fields
    parser.add_argument("--parent-company-id")
    parser.add_argument("--consolidation-currency")
    parser.add_argument("--group-status")
    parser.add_argument("--entity-company-id")
    parser.add_argument("--entity-name")
    parser.add_argument("--ownership-pct")
    parser.add_argument("--functional-currency")
    parser.add_argument("--consolidation-method")
    parser.add_argument("--period-date")
    parser.add_argument("--debit-account")
    parser.add_argument("--credit-account")
    parser.add_argument("--obligation-status")

    # Filters
    parser.add_argument("--status")
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)

    args, _unknown = parser.parse_known_args()

    # DB setup
    db_path = args.db_path or os.environ.get("ERPCLAW_DB_PATH", DEFAULT_DB_PATH)
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    # Check required tables exist
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    missing = [t for t in REQUIRED_TABLES if t not in tables]
    if missing:
        conn.close()
        err(f"Missing tables: {', '.join(missing)}. Run init_db.py first.",
            suggestion="python3 init_db.py")

    try:
        ACTIONS[args.action](conn, args)
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[{SKILL}] {e}\n")
        err(str(e))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
