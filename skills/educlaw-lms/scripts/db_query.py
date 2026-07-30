#!/usr/bin/env python3
"""EduClaw LMS Integration — db_query.py (unified router)

Routes all 25 actions across 4 domain modules:
  lms_sync (9), assignments (5), online_gradebook (6), course_materials (5)

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
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.dependencies import check_required_tables
except ImportError:
    import json as _json
    print(_json.dumps({
        "status": "error",
        "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw",
        "suggestion": "clawhub install erpclaw",
    }))
    sys.exit(1)

# Add this script's directory so domain modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lms_sync import ACTIONS as LMS_SYNC_ACTIONS
from assignments import ACTIONS as ASSIGNMENTS_ACTIONS
from online_gradebook import ACTIONS as GRADEBOOK_ACTIONS
from course_materials import ACTIONS as MATERIALS_ACTIONS

# ─────────────────────────────────────────────────────────────────────────────
# Merge domain actions into single router
# ─────────────────────────────────────────────────────────────────────────────
SKILL = "educlaw-lms"
REQUIRED_TABLES = ["company", "educlaw_lms_connection"]

ACTIONS = {}
ACTIONS.update(LMS_SYNC_ACTIONS)
ACTIONS.update(ASSIGNMENTS_ACTIONS)
ACTIONS.update(GRADEBOOK_ACTIONS)
ACTIONS.update(MATERIALS_ACTIONS)
ACTIONS["status"] = lambda conn, args: ok({
    "skill": SKILL,
    "version": "1.0.0",
    "actions_available": len([k for k in ACTIONS if k != "status"]),
    "domains": ["lms_sync", "assignments", "online_gradebook", "course_materials"],
    "database": DEFAULT_DB_PATH,
    "lms_types_supported": ["canvas", "moodle", "google_classroom", "oneroster_csv"],
})


def main():
    parser = argparse.ArgumentParser(description="educlaw-lms — EduClaw LMS Integration")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # ── Shared ─────────────────────────────────────────────────────────────
    parser.add_argument("--company-id")
    parser.add_argument("--user-id")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    # ── LMS Connection ──────────────────────────────────────────────────────
    parser.add_argument("--connection-id")
    parser.add_argument("--lms-type")
    parser.add_argument("--display-name")
    parser.add_argument("--endpoint-url")
    parser.add_argument("--client-id")
    parser.add_argument("--client-secret")
    parser.add_argument("--site-token")
    parser.add_argument("--google-credentials")
    parser.add_argument("--grade-direction")
    parser.add_argument("--has-dpa-signed")
    parser.add_argument("--dpa-signed-date")
    parser.add_argument("--is-coppa-verified")
    parser.add_argument("--coppa-cert-url")
    parser.add_argument("--allowed-data-fields")
    parser.add_argument("--default-course-prefix")
    parser.add_argument("--auto-push-assignments")
    parser.add_argument("--auto-sync-enabled")
    parser.add_argument("--sync-frequency-hours")
    parser.add_argument("--connection-status")
    parser.add_argument("--lms-site-name")
    parser.add_argument("--lms-version")
    parser.add_argument("--lms-file-id")
    parser.add_argument("--lms-download-url")

    # ── Sync Courses / Roster ───────────────────────────────────────────────
    parser.add_argument("--academic-term-id")
    parser.add_argument("--section-id")

    # ── Sync Log ────────────────────────────────────────────────────────────
    parser.add_argument("--sync-log-id")
    parser.add_argument("--sync-type")
    parser.add_argument("--sync-status")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")

    # ── Resolve Sync Conflict ───────────────────────────────────────────────
    parser.add_argument("--entity-type")
    parser.add_argument("--entity-id")
    parser.add_argument("--resolution")

    # ── Assignments ─────────────────────────────────────────────────────────
    parser.add_argument("--assessment-id")
    parser.add_argument("--lms-grade-scheme")
    parser.add_argument("--create-assessments", action="store_true", default=False)
    parser.add_argument("--plan-id")
    parser.add_argument("--category-id")
    parser.add_argument("--assignment-sync-status")

    # ── Grade Pull / Gradebook ──────────────────────────────────────────────
    parser.add_argument("--grade-sync-id")
    parser.add_argument("--conflict-type")
    parser.add_argument("--conflict-status")
    parser.add_argument("--resolved-by")
    parser.add_argument("--new-score")
    parser.add_argument("--push-to-lms", action="store_true", default=False)
    parser.add_argument("--include-grades", action="store_true", default=False)

    # ── OneRoster Export ────────────────────────────────────────────────────
    parser.add_argument("--output-dir")

    # ── Course Materials ────────────────────────────────────────────────────
    parser.add_argument("--material-id")
    parser.add_argument("--name")
    parser.add_argument("--description")
    parser.add_argument("--material-type")
    parser.add_argument("--access-type")
    parser.add_argument("--external-url")
    parser.add_argument("--file-path")
    parser.add_argument("--lms-connection-id")
    parser.add_argument("--is-visible-to-students")
    parser.add_argument("--available-from")
    parser.add_argument("--available-until")
    parser.add_argument("--sort-order")
    parser.add_argument("--include-archived", action="store_true", default=False)

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = (
            "clawhub install erpclaw && "
            "clawhub install educlaw && "
            "clawhub install educlaw-lms"
        )
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

    try:
        ACTIONS[args.action](conn, args)
    except SystemExit:
        raise
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[{SKILL}] {e}\n")
        err(str(e))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
