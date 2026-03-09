"""ERPClaw Advanced Accounting -- Cross-domain reports and status

Aggregated reports and the skill status action.
Imported by db_query.py (unified router).
"""
import os
import sys

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.response import ok, err, row_to_dict
except ImportError:
    pass

SKILL = "erpclaw-accounting-adv"
VERSION = "1.0.0"

ALL_TABLES = [
    "advacct_revenue_contract", "advacct_performance_obligation",
    "advacct_variable_consideration", "advacct_revenue_schedule",
    "advacct_lease", "advacct_lease_payment", "advacct_amortization_entry",
    "advacct_ic_transaction", "advacct_transfer_price_rule",
    "advacct_consolidation_group", "advacct_group_entity", "advacct_elimination_entry",
]


# ===========================================================================
# 1. standards-compliance-dashboard
# ===========================================================================
def standards_compliance_dashboard(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    where_sql = " AND ".join(where)

    # Revenue (ASC 606)
    revenue_contracts = conn.execute(
        f"SELECT COUNT(*) FROM advacct_revenue_contract WHERE {where_sql}", params
    ).fetchone()[0]
    unsatisfied_obligations = conn.execute(
        f"SELECT COUNT(*) FROM advacct_performance_obligation WHERE obligation_status != 'satisfied' AND {where_sql}", params
    ).fetchone()[0]

    # Leases (ASC 842)
    active_leases = conn.execute(
        f"SELECT COUNT(*) FROM advacct_lease WHERE lease_status = 'active' AND {where_sql}", params
    ).fetchone()[0]
    leases_without_rou = conn.execute(
        f"SELECT COUNT(*) FROM advacct_lease WHERE rou_asset_value IS NULL AND lease_status != 'draft' AND {where_sql}", params
    ).fetchone()[0]

    # Intercompany
    unposted_ic = conn.execute(
        f"SELECT COUNT(*) FROM advacct_ic_transaction WHERE ic_status NOT IN ('posted','eliminated') AND {where_sql}", params
    ).fetchone()[0]

    # Consolidation
    active_groups = conn.execute(
        f"SELECT COUNT(*) FROM advacct_consolidation_group WHERE group_status = 'active' AND {where_sql}", params
    ).fetchone()[0]

    ok({
        "report": "standards_compliance_dashboard",
        "asc_606": {
            "revenue_contracts": revenue_contracts,
            "unsatisfied_obligations": unsatisfied_obligations,
        },
        "asc_842": {
            "active_leases": active_leases,
            "leases_without_rou_calculation": leases_without_rou,
        },
        "intercompany": {
            "unposted_transactions": unposted_ic,
        },
        "consolidation": {
            "active_groups": active_groups,
        },
    })


# ===========================================================================
# 2. status
# ===========================================================================
def status_action(conn, args):
    counts = {}
    for tbl in ALL_TABLES:
        try:
            counts[tbl] = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        except Exception:
            counts[tbl] = 0

    ok({
        "skill": SKILL,
        "version": VERSION,
        "total_tables": len(ALL_TABLES),
        "record_counts": counts,
    })


# ---------------------------------------------------------------------------
# Action registry
# ---------------------------------------------------------------------------
ACTIONS = {
    "standards-compliance-dashboard": standards_compliance_dashboard,
    "status": status_action,
}
