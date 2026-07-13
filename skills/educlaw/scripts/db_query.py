#!/usr/bin/env python3
"""EduClaw — db_query.py (unified router)

Routes all actions across 8 domain modules: students, academics, enrollment,
grading, attendance, staff, fees, communications.

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
        "suggestion": "clawhub install erpclaw"
    }))
    sys.exit(1)

# Add this script's directory so domain modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from students import ACTIONS as STUDENTS_ACTIONS
from academics import ACTIONS as ACADEMICS_ACTIONS
from enrollment import ACTIONS as ENROLLMENT_ACTIONS
from grading import ACTIONS as GRADING_ACTIONS
from attendance import ACTIONS as ATTENDANCE_ACTIONS
from staff import ACTIONS as STAFF_ACTIONS
from fees import ACTIONS as FEES_ACTIONS
from communications import ACTIONS as COMMUNICATIONS_ACTIONS

# ---------------------------------------------------------------------------
# Merge all domain actions into one router
# ---------------------------------------------------------------------------
SKILL = "educlaw"
REQUIRED_TABLES = ["company", "educlaw_student"]

ACTIONS = {}
ACTIONS.update(STUDENTS_ACTIONS)
ACTIONS.update(ACADEMICS_ACTIONS)
ACTIONS.update(ENROLLMENT_ACTIONS)
ACTIONS.update(GRADING_ACTIONS)
ACTIONS.update(ATTENDANCE_ACTIONS)
ACTIONS.update(STAFF_ACTIONS)
ACTIONS.update(FEES_ACTIONS)
ACTIONS.update(COMMUNICATIONS_ACTIONS)
ACTIONS["status"] = lambda conn, args: ok({
    "skill": SKILL,
    "version": "1.0.0",
    "actions_available": len([k for k in ACTIONS if k != "status"]),
    "domains": ["students", "academics", "enrollment", "grading",
                "attendance", "staff", "fees", "communications"],
    "database": DEFAULT_DB_PATH,
})


def main():
    parser = argparse.ArgumentParser(description="educlaw")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # ── Shared ────────────────────────────────────────────────────────────
    parser.add_argument("--company-id")
    parser.add_argument("--user-id")
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    # ── Student / Applicant ───────────────────────────────────────────────
    parser.add_argument("--student-id")
    parser.add_argument("--applicant-id")
    parser.add_argument("--first-name")
    parser.add_argument("--last-name")
    parser.add_argument("--middle-name")
    parser.add_argument("--date-of-birth")
    parser.add_argument("--gender")
    parser.add_argument("--email")
    parser.add_argument("--phone")
    parser.add_argument("--alternate-phone")
    parser.add_argument("--address")
    parser.add_argument("--grade-level")
    parser.add_argument("--applying-for-program-id")
    parser.add_argument("--applying-for-term-id")
    parser.add_argument("--application-date")
    parser.add_argument("--documents")            # JSON
    parser.add_argument("--previous-school")
    parser.add_argument("--previous-school-address")
    parser.add_argument("--transfer-records")     # JSON
    parser.add_argument("--emergency-contact")    # JSON
    parser.add_argument("--applicant-status")
    parser.add_argument("--review-notes")
    parser.add_argument("--reviewed-by")
    parser.add_argument("--student-status")
    parser.add_argument("--current-program-id")
    parser.add_argument("--cohort-year")
    parser.add_argument("--enrollment-date")
    parser.add_argument("--graduation-date")
    parser.add_argument("--registration-hold")
    parser.add_argument("--directory-info-opt-out")
    parser.add_argument("--academic-standing")
    parser.add_argument("--naming-series")

    # ── Guardian ──────────────────────────────────────────────────────────
    parser.add_argument("--guardian-id")
    parser.add_argument("--guardian-info")        # JSON
    parser.add_argument("--relationship")
    parser.add_argument("--is-primary-contact")
    parser.add_argument("--is-emergency-contact")
    parser.add_argument("--has-custody")
    parser.add_argument("--can-pickup")
    parser.add_argument("--receives-communications")
    parser.add_argument("--employer")
    parser.add_argument("--occupation")

    # ── FERPA / Consent ───────────────────────────────────────────────────
    parser.add_argument("--data-category")
    parser.add_argument("--access-type")
    parser.add_argument("--access-reason")
    parser.add_argument("--ip-address")
    parser.add_argument("--is-emergency-access")
    parser.add_argument("--consent-type")
    parser.add_argument("--consent-date")
    parser.add_argument("--consent-id")
    parser.add_argument("--granted-by")
    parser.add_argument("--granted-by-relationship")
    parser.add_argument("--revoked-date")
    parser.add_argument("--third-party-name")
    parser.add_argument("--purpose")

    # ── Academic Year / Term ──────────────────────────────────────────────
    parser.add_argument("--year-id")
    parser.add_argument("--academic-year-id")
    parser.add_argument("--term-id")
    parser.add_argument("--academic-term-id")
    parser.add_argument("--name")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--is-active")
    parser.add_argument("--term-type")
    parser.add_argument("--term-status")
    parser.add_argument("--enrollment-start-date")
    parser.add_argument("--enrollment-end-date")
    parser.add_argument("--grade-submission-deadline")

    # ── Room ──────────────────────────────────────────────────────────────
    parser.add_argument("--room-id")
    parser.add_argument("--room-number")
    parser.add_argument("--building")
    parser.add_argument("--capacity")
    parser.add_argument("--room-type")
    parser.add_argument("--facilities")          # JSON

    # ── Program ───────────────────────────────────────────────────────────
    parser.add_argument("--program-id")
    parser.add_argument("--program-type")
    parser.add_argument("--department-id")
    parser.add_argument("--description")
    parser.add_argument("--total-credits-required")
    parser.add_argument("--duration-years")
    parser.add_argument("--prerequisites")       # JSON
    parser.add_argument("--is-published")

    # ── Course ────────────────────────────────────────────────────────────
    parser.add_argument("--course-id")
    parser.add_argument("--course-code")
    parser.add_argument("--course-type")
    parser.add_argument("--credit-hours")
    parser.add_argument("--max-enrollment")
    parser.add_argument("--is-default")

    # ── Section ───────────────────────────────────────────────────────────
    parser.add_argument("--section-id")
    parser.add_argument("--section-number")
    parser.add_argument("--section-status")
    parser.add_argument("--instructor-id")
    parser.add_argument("--days-of-week")        # JSON
    parser.add_argument("--start-time")
    parser.add_argument("--end-time")
    parser.add_argument("--waitlist-enabled")
    parser.add_argument("--waitlist-max")

    # ── Enrollment ────────────────────────────────────────────────────────
    parser.add_argument("--enrollment-id")
    parser.add_argument("--enrollment-status")
    parser.add_argument("--drop-reason")
    parser.add_argument("--waitlist-status")

    # ── Grading ───────────────────────────────────────────────────────────
    parser.add_argument("--scale-id")
    parser.add_argument("--grading-scale-id")
    parser.add_argument("--entries")              # JSON
    parser.add_argument("--plan-id")
    parser.add_argument("--categories")          # JSON
    parser.add_argument("--category-id")
    parser.add_argument("--assessment-id")
    parser.add_argument("--max-points")
    parser.add_argument("--allows-extra-credit")
    parser.add_argument("--sort-order")
    parser.add_argument("--results")             # JSON
    parser.add_argument("--points-earned")
    parser.add_argument("--is-exempt")
    parser.add_argument("--is-late")
    parser.add_argument("--graded-by")
    parser.add_argument("--grade-type")
    parser.add_argument("--submitted-by")
    parser.add_argument("--is-grade-submitted")
    parser.add_argument("--is-repeat")
    parser.add_argument("--new-letter-grade")
    parser.add_argument("--new-grade-points")
    parser.add_argument("--amended-by")
    parser.add_argument("--reason")
    parser.add_argument("--revenue-account-id")

    # ── Attendance ────────────────────────────────────────────────────────
    parser.add_argument("--attendance-id")
    parser.add_argument("--attendance-date")
    parser.add_argument("--attendance-date-from")
    parser.add_argument("--attendance-date-to")
    parser.add_argument("--attendance-status")
    parser.add_argument("--late-minutes")
    parser.add_argument("--comments")
    parser.add_argument("--marked-by")
    parser.add_argument("--source")
    parser.add_argument("--records")             # JSON (batch)
    parser.add_argument("--threshold")

    # ── Staff / Instructor ────────────────────────────────────────────────
    parser.add_argument("--employee-id")
    parser.add_argument("--credentials")         # JSON
    parser.add_argument("--specializations")     # JSON
    parser.add_argument("--max-teaching-load-hours")
    parser.add_argument("--office-location")
    parser.add_argument("--office-hours")        # JSON
    parser.add_argument("--bio")

    # ── Fees ──────────────────────────────────────────────────────────────
    parser.add_argument("--fee-category-id")
    parser.add_argument("--structure-id")
    parser.add_argument("--scholarship-id")
    parser.add_argument("--scholarship-status")
    parser.add_argument("--discount-type")
    parser.add_argument("--discount-amount")
    parser.add_argument("--applies-to-category-id")
    parser.add_argument("--approved-by")
    parser.add_argument("--amount")
    parser.add_argument("--due-date")
    parser.add_argument("--due-date-from")
    parser.add_argument("--due-date-to")
    parser.add_argument("--items")              # JSON (fee structure items)
    parser.add_argument("--code")
    parser.add_argument("--publish-date")

    # ── Communications ────────────────────────────────────────────────────
    parser.add_argument("--announcement-id")
    parser.add_argument("--announcement-status")
    parser.add_argument("--title")
    parser.add_argument("--body")
    parser.add_argument("--priority")
    parser.add_argument("--audience-type")
    parser.add_argument("--audience-filter")     # JSON
    parser.add_argument("--expiry-date")
    parser.add_argument("--published-by")
    parser.add_argument("--recipient-type")
    parser.add_argument("--recipient-id")
    parser.add_argument("--notification-type")
    parser.add_argument("--message")
    parser.add_argument("--reference-type")
    parser.add_argument("--reference-id")
    parser.add_argument("--sent-via")
    parser.add_argument("--is-read")
    parser.add_argument("--sent-by")
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = "clawhub install erpclaw && clawhub install educlaw"
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

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
