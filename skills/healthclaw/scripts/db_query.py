#!/usr/bin/env python3
"""HealthClaw — db_query.py (unified router)

AI-native hospital and multi-department healthcare ERP
Routes all actions across 7 domain modules: patients, appointments, clinical, billing, inventory, lab, referrals.

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

from patients import ACTIONS as PATIENTS_ACTIONS
from appointments import ACTIONS as APPOINTMENTS_ACTIONS
from clinical import ACTIONS as CLINICAL_ACTIONS
from billing import ACTIONS as BILLING_ACTIONS
from inventory import ACTIONS as INVENTORY_ACTIONS
from lab import ACTIONS as LAB_ACTIONS
from referrals import ACTIONS as REFERRALS_ACTIONS

# ---------------------------------------------------------------------------
# Merge all domain actions into one router
# ---------------------------------------------------------------------------
SKILL = "healthclaw"
REQUIRED_TABLES = ["company", "healthclaw_patient"]

ACTIONS = {}
ACTIONS.update(PATIENTS_ACTIONS)
ACTIONS.update(APPOINTMENTS_ACTIONS)
ACTIONS.update(CLINICAL_ACTIONS)
ACTIONS.update(BILLING_ACTIONS)
ACTIONS.update(INVENTORY_ACTIONS)
ACTIONS.update(LAB_ACTIONS)
ACTIONS.update(REFERRALS_ACTIONS)
ACTIONS["status"] = lambda conn, args: ok({
    "skill": SKILL,
    "version": "1.0.0",
    "actions_available": len([k for k in ACTIONS if k != "status"]),
    "domains": ["patients", "appointments", "clinical", "billing", "inventory", "lab", "referrals"],
    "database": DEFAULT_DB_PATH,
})


def main():
    parser = argparse.ArgumentParser(description="healthclaw")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # -- Shared IDs --
    parser.add_argument("--company-id")

    # -- Domain-specific args are added during build --
    # IMPORTANT: Every args.foo_bar accessed in domain modules MUST be
    # registered here. Run validate_argparse.py to check for missing args.

    # -- Shared --
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--notes")
    parser.add_argument("--status")
    parser.add_argument("--description")

    # ── PATIENTS domain ──────────────────────────────────────────
    parser.add_argument("--patient-id")
    parser.add_argument("--customer-id")
    parser.add_argument("--first-name")
    parser.add_argument("--last-name")
    parser.add_argument("--date-of-birth")
    parser.add_argument("--gender")
    parser.add_argument("--ssn")
    parser.add_argument("--marital-status")
    parser.add_argument("--race")
    parser.add_argument("--ethnicity")
    parser.add_argument("--preferred-language")
    parser.add_argument("--primary-phone")
    parser.add_argument("--secondary-phone")
    parser.add_argument("--email")
    parser.add_argument("--address-line1")
    parser.add_argument("--address-line2")
    parser.add_argument("--city")
    parser.add_argument("--state")
    parser.add_argument("--zip-code")
    parser.add_argument("--primary-provider-id")
    # -- Insurance --
    parser.add_argument("--insurance-id")
    parser.add_argument("--insurance-type")
    parser.add_argument("--payer-name")
    parser.add_argument("--payer-id")
    parser.add_argument("--plan-name")
    parser.add_argument("--plan-type")
    parser.add_argument("--group-number")
    parser.add_argument("--member-id")
    parser.add_argument("--subscriber-name")
    parser.add_argument("--subscriber-dob")
    parser.add_argument("--subscriber-relationship")
    parser.add_argument("--copay-amount")
    parser.add_argument("--deductible")
    parser.add_argument("--deductible-met")
    parser.add_argument("--out-of-pocket-max")
    parser.add_argument("--effective-date")
    parser.add_argument("--termination-date")
    parser.add_argument("--preauth-required")
    # -- Allergy --
    parser.add_argument("--allergy-id")
    parser.add_argument("--allergen")
    parser.add_argument("--allergen-type")
    parser.add_argument("--reaction")
    parser.add_argument("--severity")
    parser.add_argument("--onset-date")
    parser.add_argument("--noted-by-id")
    # -- Medical History --
    parser.add_argument("--medical-history-id")
    parser.add_argument("--condition")
    parser.add_argument("--icd10-code")
    parser.add_argument("--diagnosis-date")
    parser.add_argument("--resolution-date")
    parser.add_argument("--medhist-status")
    # -- Patient Contact --
    parser.add_argument("--contact-id")
    parser.add_argument("--contact-type")
    parser.add_argument("--contact-name")
    parser.add_argument("--relationship")
    parser.add_argument("--contact-phone")
    parser.add_argument("--contact-email")
    parser.add_argument("--contact-address")
    parser.add_argument("--is-primary")
    # -- Consent --
    parser.add_argument("--consent-type")
    parser.add_argument("--granted-date")
    parser.add_argument("--expiration-date")
    parser.add_argument("--witness-name")
    parser.add_argument("--obtained-by-id")

    # ── APPOINTMENTS domain ──────────────────────────────────────
    parser.add_argument("--provider-id")
    parser.add_argument("--schedule-id")
    parser.add_argument("--day-of-week")
    parser.add_argument("--start-time")
    parser.add_argument("--end-time")
    parser.add_argument("--slot-duration")
    parser.add_argument("--location")
    parser.add_argument("--block-date")
    parser.add_argument("--reason")
    parser.add_argument("--appointment-id")
    parser.add_argument("--appointment-date")
    parser.add_argument("--appointment-type")
    parser.add_argument("--duration-minutes")
    parser.add_argument("--chief-complaint")
    parser.add_argument("--cancellation-reason")
    parser.add_argument("--new-provider-id")
    parser.add_argument("--priority")
    parser.add_argument("--preferred-date-start")
    parser.add_argument("--preferred-date-end")
    parser.add_argument("--preferred-time-start")
    parser.add_argument("--preferred-time-end")

    # ── CLINICAL domain ──────────────────────────────────────────
    parser.add_argument("--encounter-id")
    parser.add_argument("--encounter-date")
    parser.add_argument("--encounter-type")
    parser.add_argument("--encounter-status")
    parser.add_argument("--department")
    parser.add_argument("--room")
    parser.add_argument("--admission-date")
    parser.add_argument("--discharge-date")
    parser.add_argument("--discharge-disposition")
    # -- Vitals --
    parser.add_argument("--recorded-by-id")
    parser.add_argument("--temperature")
    parser.add_argument("--temperature-site")
    parser.add_argument("--heart-rate")
    parser.add_argument("--respiratory-rate")
    parser.add_argument("--bp-systolic")
    parser.add_argument("--bp-diastolic")
    parser.add_argument("--oxygen-saturation")
    parser.add_argument("--weight")
    parser.add_argument("--height")
    parser.add_argument("--bmi")
    parser.add_argument("--pain-level")
    # -- Diagnosis --
    parser.add_argument("--diagnosis-id")
    parser.add_argument("--dx-description")
    parser.add_argument("--diagnosis-type")
    parser.add_argument("--dx-status")
    parser.add_argument("--diagnosed-by-id")
    # -- Prescription --
    parser.add_argument("--prescription-id")
    parser.add_argument("--prescriber-id")
    parser.add_argument("--medication-name")
    parser.add_argument("--ndc-code")
    parser.add_argument("--dosage")
    parser.add_argument("--frequency")
    parser.add_argument("--route")
    parser.add_argument("--quantity")
    parser.add_argument("--refills")
    parser.add_argument("--daw")
    parser.add_argument("--rx-start-date")
    parser.add_argument("--rx-end-date")
    parser.add_argument("--controlled-schedule")
    parser.add_argument("--pharmacy-notes")
    parser.add_argument("--rx-status")
    parser.add_argument("--discontinued-reason")
    # -- Procedure --
    parser.add_argument("--cpt-code")
    parser.add_argument("--proc-description")
    parser.add_argument("--procedure-date")
    parser.add_argument("--modifiers")
    parser.add_argument("--diagnosis-ids")
    parser.add_argument("--anesthesia-type")
    parser.add_argument("--body-site")
    parser.add_argument("--laterality")
    # -- Clinical Notes --
    parser.add_argument("--note-id")
    parser.add_argument("--note-type")
    parser.add_argument("--subjective")
    parser.add_argument("--objective")
    parser.add_argument("--assessment")
    parser.add_argument("--plan-text")
    parser.add_argument("--body")
    parser.add_argument("--addendum")
    parser.add_argument("--note-status")
    parser.add_argument("--sign")
    parser.add_argument("--author-id")
    # -- Orders --
    parser.add_argument("--ordering-provider-id")
    parser.add_argument("--order-type")
    parser.add_argument("--order-date")
    parser.add_argument("--clinical-indication")

    # ── INVENTORY domain ──────────────────────────────────────
    parser.add_argument("--formulary-id")
    parser.add_argument("--formulary-name")
    parser.add_argument("--formulary-status")
    parser.add_argument("--formulary-item-id")
    parser.add_argument("--formulary-item-status")
    parser.add_argument("--item-id")
    parser.add_argument("--drug-class")
    parser.add_argument("--generic-name")
    parser.add_argument("--brand-name")
    parser.add_argument("--strength")
    parser.add_argument("--dosage-form")
    parser.add_argument("--therapeutic-class")
    parser.add_argument("--formulary-tier")
    parser.add_argument("--requires-prior-auth")
    parser.add_argument("--max-daily-dose")
    parser.add_argument("--dispensing-id")
    parser.add_argument("--dispensed-by-id")
    parser.add_argument("--dispensed-date")
    parser.add_argument("--lot-number")
    parser.add_argument("--directions")
    parser.add_argument("--refill-number")

    # ── BILLING domain ────────────────────────────────────────
    parser.add_argument("--fee-schedule-id")
    parser.add_argument("--fee-schedule-name")
    parser.add_argument("--fee-schedule-status")
    parser.add_argument("--payer-type")
    parser.add_argument("--standard-charge")
    parser.add_argument("--allowed-amount")
    parser.add_argument("--unit-count")
    parser.add_argument("--modifier")
    parser.add_argument("--charge-id")
    parser.add_argument("--charge-amount")
    parser.add_argument("--service-date")
    parser.add_argument("--procedure-id")
    parser.add_argument("--units")
    parser.add_argument("--place-of-service")
    parser.add_argument("--claim-id")
    parser.add_argument("--claim-date")
    parser.add_argument("--claim-type")
    parser.add_argument("--claim-status")
    parser.add_argument("--total-charge")
    parser.add_argument("--total-allowed")
    parser.add_argument("--total-paid")
    parser.add_argument("--patient-responsibility")
    parser.add_argument("--adjustment-amount")
    parser.add_argument("--billing-provider-id")
    parser.add_argument("--rendering-provider-id")
    parser.add_argument("--filing-indicator")
    parser.add_argument("--sales-invoice-id")
    parser.add_argument("--denial-reason")
    parser.add_argument("--appeal-deadline")
    parser.add_argument("--line-number")
    parser.add_argument("--diagnosis-pointers")
    parser.add_argument("--paid-amount")
    parser.add_argument("--patient-amount")
    parser.add_argument("--remark-codes")
    parser.add_argument("--posting-type")
    parser.add_argument("--posting-date")
    parser.add_argument("--amount")
    parser.add_argument("--check-number")
    parser.add_argument("--payment-method")
    parser.add_argument("--payment-entry-id")
    parser.add_argument("--eob-date")

    # ── LAB domain ────────────────────────────────────────────
    parser.add_argument("--order-id")
    parser.add_argument("--lab-order-id")
    parser.add_argument("--lab-order-status")
    parser.add_argument("--fasting-required")
    parser.add_argument("--specimen-type")
    parser.add_argument("--collection-date")
    parser.add_argument("--received-date")
    parser.add_argument("--lab-test-id")
    parser.add_argument("--test-code")
    parser.add_argument("--test-name")
    parser.add_argument("--component-name")
    parser.add_argument("--result-value")
    parser.add_argument("--result-date")
    parser.add_argument("--flag")
    parser.add_argument("--unit")
    parser.add_argument("--reference-low")
    parser.add_argument("--reference-high")
    parser.add_argument("--performed-by-id")
    parser.add_argument("--verified-by-id")
    parser.add_argument("--imaging-order-id")
    parser.add_argument("--imaging-order-status")
    parser.add_argument("--modality")
    parser.add_argument("--body-part")
    parser.add_argument("--contrast")
    parser.add_argument("--scheduled-date")
    parser.add_argument("--imaging-result-id")
    parser.add_argument("--imaging-result-status")
    parser.add_argument("--radiologist-id")
    parser.add_argument("--findings")
    parser.add_argument("--impression")
    parser.add_argument("--recommendation")
    parser.add_argument("--critical-finding")
    parser.add_argument("--report-date")

    # ── REFERRALS domain ──────────────────────────────────────
    parser.add_argument("--referral-id")
    parser.add_argument("--referral-status")
    parser.add_argument("--referring-provider-id")
    parser.add_argument("--referred-to-provider")
    parser.add_argument("--referred-to-specialty")
    parser.add_argument("--referred-to-facility")
    parser.add_argument("--referred-to-phone")
    parser.add_argument("--referred-to-fax")
    parser.add_argument("--referral-date")
    parser.add_argument("--prior-auth-required")
    parser.add_argument("--prior-auth-id")
    parser.add_argument("--requesting-provider-id")
    parser.add_argument("--auth-number")
    parser.add_argument("--service-type")
    parser.add_argument("--auth-status")
    parser.add_argument("--cpt-codes")
    parser.add_argument("--icd10-codes")
    parser.add_argument("--units-requested")
    parser.add_argument("--units-approved")
    parser.add_argument("--request-date")
    parser.add_argument("--decision-date")
    parser.add_argument("--usage-date")
    parser.add_argument("--units-used")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = "clawhub install erpclaw && clawhub install healthclaw"
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
