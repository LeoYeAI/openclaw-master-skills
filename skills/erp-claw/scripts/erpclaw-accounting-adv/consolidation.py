"""ERPClaw Advanced Accounting -- Multi-Entity Consolidation domain module

Actions for consolidation groups, group entities, and elimination entries (3 tables, 8 actions).
Imported by db_query.py (unified router).
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.naming import get_next_name, ENTITY_PREFIXES
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit

    ENTITY_PREFIXES.setdefault("consolidation_group", "CGRP-")
except ImportError:
    pass

SKILL = "erpclaw-accounting-adv"

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------
VALID_GROUP_STATUSES = ("active", "inactive")
VALID_CONSOLIDATION_METHODS = ("full", "proportional", "equity")
VALID_ENTRY_TYPES = ("ic_elimination", "minority_interest", "currency_translation", "goodwill")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _validate_company(conn, company_id):
    if not company_id:
        err("--company-id is required")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")


def _validate_group(conn, group_id):
    if not group_id:
        err("--group-id is required")
    row = conn.execute("SELECT id FROM advacct_consolidation_group WHERE id = ?", (group_id,)).fetchone()
    if not row:
        err(f"Consolidation group {group_id} not found")


# ===========================================================================
# 1. add-consolidation-group
# ===========================================================================
def add_consolidation_group(conn, args):
    _validate_company(conn, args.company_id)

    name = getattr(args, "name", None)
    if not name:
        err("--name is required")

    group_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    naming = get_next_name(conn, "consolidation_group", company_id=args.company_id)
    now = _now_iso()

    conn.execute("""
        INSERT INTO advacct_consolidation_group (
            id, naming_series, name, parent_company_id, consolidation_currency,
            group_status, company_id, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        group_id, naming, name,
        getattr(args, "parent_company_id", None),
        getattr(args, "consolidation_currency", None) or "USD",
        "active", args.company_id, now, now,
    ))
    audit(conn, SKILL, "add-consolidation-group", "advacct_consolidation_group", group_id,
          new_values={"name": name})
    conn.commit()
    ok({
        "id": group_id, "naming_series": naming, "name": name,
        "group_status": "active",
    })


# ===========================================================================
# 2. list-consolidation-groups
# ===========================================================================
def list_consolidation_groups(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?")
        params.append(args.company_id)
    if getattr(args, "group_status", None):
        where.append("group_status = ?")
        params.append(args.group_status)
    if getattr(args, "search", None):
        where.append("(LOWER(name) LIKE LOWER(?))")
        params.append(f"%{args.search}%")

    where_sql = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM advacct_consolidation_group WHERE {where_sql}", params
    ).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM advacct_consolidation_group WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params
    ).fetchall()
    ok({
        "rows": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": args.limit, "offset": args.offset,
        "has_more": (args.offset + args.limit) < total,
    })


# ===========================================================================
# 3. add-group-entity
# ===========================================================================
def add_group_entity(conn, args):
    group_id = getattr(args, "group_id", None)
    _validate_group(conn, group_id)
    _validate_company(conn, args.company_id)

    entity_company_id = getattr(args, "entity_company_id", None)
    if not entity_company_id:
        err("--entity-company-id is required")

    entity_name = getattr(args, "entity_name", None)
    if not entity_name:
        err("--entity-name is required")

    consolidation_method = getattr(args, "consolidation_method", None) or "full"
    if consolidation_method not in VALID_CONSOLIDATION_METHODS:
        err(f"Invalid consolidation-method: {consolidation_method}. Must be one of: {', '.join(VALID_CONSOLIDATION_METHODS)}")

    ownership_pct = getattr(args, "ownership_pct", None) or "100"

    entity_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute("""
        INSERT INTO advacct_group_entity (
            id, group_id, entity_company_id, entity_name, ownership_pct,
            functional_currency, consolidation_method, is_active,
            company_id, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        entity_id, group_id, entity_company_id, entity_name, ownership_pct,
        getattr(args, "functional_currency", None) or "USD",
        consolidation_method, 1,
        args.company_id, now,
    ))
    audit(conn, SKILL, "add-group-entity", "advacct_group_entity", entity_id,
          new_values={"group_id": group_id, "entity_name": entity_name, "ownership_pct": ownership_pct})
    conn.commit()
    ok({
        "id": entity_id, "group_id": group_id,
        "entity_company_id": entity_company_id, "entity_name": entity_name,
        "ownership_pct": ownership_pct, "consolidation_method": consolidation_method,
    })


# ===========================================================================
# 4. run-consolidation
# ===========================================================================
def run_consolidation(conn, args):
    group_id = getattr(args, "group_id", None)
    _validate_group(conn, group_id)

    period_date = getattr(args, "period_date", None)
    if not period_date:
        err("--period-date is required")

    # Get group info
    group = row_to_dict(conn.execute(
        "SELECT * FROM advacct_consolidation_group WHERE id = ?", (group_id,)
    ).fetchone())

    # Get entities
    entities = conn.execute(
        "SELECT * FROM advacct_group_entity WHERE group_id = ? AND is_active = 1",
        (group_id,)
    ).fetchall()

    if not entities:
        err("Consolidation group has no active entities")

    entity_list = [row_to_dict(e) for e in entities]
    entity_count = len(entity_list)

    audit(conn, SKILL, "run-consolidation", "advacct_consolidation_group", group_id,
          new_values={"period_date": period_date, "entity_count": entity_count})
    conn.commit()
    ok({
        "group_id": group_id, "group_name": group["name"],
        "period_date": period_date, "entity_count": entity_count,
        "entities": [{"entity_name": e["entity_name"], "ownership_pct": e["ownership_pct"],
                      "consolidation_method": e["consolidation_method"]} for e in entity_list],
        "consolidation_run": "completed",
    })


# ===========================================================================
# 5. generate-elimination-entries
# ===========================================================================
def generate_elimination_entries(conn, args):
    group_id = getattr(args, "group_id", None)
    _validate_group(conn, group_id)

    period_date = getattr(args, "period_date", None)
    if not period_date:
        err("--period-date is required")

    company_id = getattr(args, "company_id", None)
    _validate_company(conn, company_id)

    # Get entities in this group
    entities = conn.execute(
        "SELECT entity_company_id FROM advacct_group_entity WHERE group_id = ? AND is_active = 1",
        (group_id,)
    ).fetchall()
    entity_company_ids = [e[0] for e in entities]

    if len(entity_company_ids) < 2:
        err("Need at least 2 active entities for elimination entries")

    # Find posted IC transactions between group entities
    placeholders = ",".join(["?"] * len(entity_company_ids))
    ic_rows = conn.execute(f"""
        SELECT * FROM advacct_ic_transaction
        WHERE ic_status = 'posted'
          AND from_company_id IN ({placeholders})
          AND to_company_id IN ({placeholders})
    """, entity_company_ids + entity_company_ids).fetchall()

    entries_created = 0
    now = _now_iso()

    for ic_row in ic_rows:
        ic = row_to_dict(ic_row)
        amount = ic["amount"]

        # Create elimination entry (debit IC revenue, credit IC expense)
        conn.execute("""
            INSERT INTO advacct_elimination_entry (
                id, group_id, period_date, debit_account, credit_account,
                amount, description, entry_type, company_id, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            str(uuid.uuid4()), group_id, period_date,
            "IC Revenue", "IC Expense",
            amount,
            f"Elimination: {ic['transaction_type']} from {ic['from_company_id']} to {ic['to_company_id']}",
            "ic_elimination", company_id, now,
        ))
        entries_created += 1

    audit(conn, SKILL, "generate-elimination-entries", "advacct_elimination_entry", group_id,
          new_values={"period_date": period_date, "entries_created": entries_created})
    conn.commit()
    ok({
        "group_id": group_id, "period_date": period_date,
        "entries_created": entries_created,
    })


# ===========================================================================
# 6. add-currency-translation
# ===========================================================================
def add_currency_translation(conn, args):
    group_id = getattr(args, "group_id", None)
    _validate_group(conn, group_id)
    _validate_company(conn, args.company_id)

    period_date = getattr(args, "period_date", None)
    if not period_date:
        err("--period-date is required")

    amount = getattr(args, "amount", None)
    if not amount:
        err("--amount is required")

    debit_account = getattr(args, "debit_account", None) or "CTA - Debit"
    credit_account = getattr(args, "credit_account", None) or "CTA - Credit"

    entry_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute("""
        INSERT INTO advacct_elimination_entry (
            id, group_id, period_date, debit_account, credit_account,
            amount, description, entry_type, company_id, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        entry_id, group_id, period_date,
        debit_account, credit_account, amount,
        getattr(args, "description", None) or "Currency translation adjustment",
        "currency_translation", args.company_id, now,
    ))
    audit(conn, SKILL, "add-currency-translation", "advacct_elimination_entry", entry_id,
          new_values={"group_id": group_id, "amount": amount, "entry_type": "currency_translation"})
    conn.commit()
    ok({
        "id": entry_id, "group_id": group_id, "period_date": period_date,
        "amount": amount, "entry_type": "currency_translation",
    })


# ===========================================================================
# 7. consolidation-trial-balance-report
# ===========================================================================
def consolidation_trial_balance_report(conn, args):
    group_id = getattr(args, "group_id", None)
    _validate_group(conn, group_id)

    period_date = getattr(args, "period_date", None)

    group = row_to_dict(conn.execute(
        "SELECT * FROM advacct_consolidation_group WHERE id = ?", (group_id,)
    ).fetchone())

    # Get entities
    entities = conn.execute(
        "SELECT * FROM advacct_group_entity WHERE group_id = ? AND is_active = 1 ORDER BY entity_name",
        (group_id,)
    ).fetchall()

    # Get elimination entries
    where_elim, params_elim = ["group_id = ?"], [group_id]
    if period_date:
        where_elim.append("period_date = ?")
        params_elim.append(period_date)

    elim_entries = conn.execute(
        f"SELECT * FROM advacct_elimination_entry WHERE {' AND '.join(where_elim)} ORDER BY created_at",
        params_elim
    ).fetchall()

    total_eliminations = sum(
        Decimal(row_to_dict(e)["amount"]) for e in elim_entries
    )

    ok({
        "report": "consolidation_trial_balance",
        "group_id": group_id, "group_name": group["name"],
        "period_date": period_date,
        "entities": [row_to_dict(e) for e in entities],
        "elimination_entries": [row_to_dict(e) for e in elim_entries],
        "total_eliminations": str(total_eliminations),
        "entity_count": len(entities),
    })


# ===========================================================================
# 8. consolidation-summary
# ===========================================================================
def consolidation_summary(conn, args):
    group_id = getattr(args, "group_id", None)
    _validate_group(conn, group_id)

    group = row_to_dict(conn.execute(
        "SELECT * FROM advacct_consolidation_group WHERE id = ?", (group_id,)
    ).fetchone())

    entity_count = conn.execute(
        "SELECT COUNT(*) FROM advacct_group_entity WHERE group_id = ? AND is_active = 1",
        (group_id,)
    ).fetchone()[0]

    elimination_count = conn.execute(
        "SELECT COUNT(*) FROM advacct_elimination_entry WHERE group_id = ?",
        (group_id,)
    ).fetchone()[0]

    by_type = conn.execute("""
        SELECT entry_type, COUNT(*) as cnt, SUM(CAST(amount AS NUMERIC)) as total
        FROM advacct_elimination_entry WHERE group_id = ?
        GROUP BY entry_type
    """, (group_id,)).fetchall()

    ok({
        "report": "consolidation_summary",
        "group_id": group_id,
        "group_name": group["name"],
        "group_status": group["group_status"],
        "consolidation_currency": group["consolidation_currency"],
        "entity_count": entity_count,
        "elimination_count": elimination_count,
        "eliminations_by_type": {r[0]: {"count": r[1], "total": str(Decimal(str(r[2])).quantize(Decimal("0.01")))} for r in by_type} if by_type else {},
    })


# ---------------------------------------------------------------------------
# Action registry
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-consolidation-group": add_consolidation_group,
    "list-consolidation-groups": list_consolidation_groups,
    "add-group-entity": add_group_entity,
    "run-consolidation": run_consolidation,
    "generate-elimination-entries": generate_elimination_entries,
    "add-currency-translation": add_currency_translation,
    "consolidation-trial-balance-report": consolidation_trial_balance_report,
    "consolidation-summary": consolidation_summary,
}
