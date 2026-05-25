#!/usr/bin/env python3
"""ERPClaw OS — Semantic Correctness Engine

Validates that generated modules post to semantically correct accounts.
Three rule categories:

  1. Account Classification — revenue to Income, expense to Expense, etc.
  2. Posting Patterns — sales invoices credit Income, purchase invoices debit Expense
  3. Period Validation — ASC 606 rev rec timing, prepayment to liability, depreciation schedule

Rules are stored in erpclaw_semantic_rule table and findings in
erpclaw_semantic_finding table. Default rules are seeded on first run.
"""
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.query import Q, Table, Field, P, fn
except ImportError:
    pass

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")


# ---------------------------------------------------------------------------
# Default Rules
# ---------------------------------------------------------------------------

DEFAULT_RULES = [
    # --- Account Classification Rules ---
    {
        "rule_name": "revenue_account_root_type",
        "category": "account_classification",
        "description": "Revenue GL entries must credit accounts with root_type='income'. "
                       "Credits to expense/asset/liability/equity accounts indicate a misposting.",
        "rule_definition": json.dumps({
            "check": "gl_credit_root_type",
            "voucher_types": ["sales_invoice", "credit_note"],
            "expected_credit_root_types": ["income"],
            "exclude_entry_sets": ["cogs", "tax"],
        }),
        "severity": "critical",
    },
    {
        "rule_name": "expense_account_root_type",
        "category": "account_classification",
        "description": "Expense GL entries must debit accounts with root_type='expense'. "
                       "Debits to income accounts indicate a misposting.",
        "rule_definition": json.dumps({
            "check": "gl_debit_root_type",
            "voucher_types": ["purchase_invoice", "debit_note"],
            "expected_debit_root_types": ["expense"],
            "exclude_entry_sets": ["tax"],
        }),
        "severity": "critical",
    },
    {
        "rule_name": "asset_account_root_type",
        "category": "account_classification",
        "description": "Asset acquisition entries must debit accounts with root_type='asset'. "
                       "Debits to liability or equity accounts indicate a misposting.",
        "rule_definition": json.dumps({
            "check": "gl_debit_root_type",
            "voucher_types": ["stock_entry", "purchase_receipt"],
            "expected_debit_root_types": ["asset"],
            "exclude_entry_sets": [],
        }),
        "severity": "critical",
    },
    {
        "rule_name": "liability_account_root_type",
        "category": "account_classification",
        "description": "Payable entries must credit accounts with root_type='liability'. "
                       "Credits to income or equity accounts indicate a misposting.",
        "rule_definition": json.dumps({
            "check": "gl_credit_root_type",
            "voucher_types": ["purchase_invoice"],
            "expected_credit_root_types": ["liability"],
            "exclude_entry_sets": ["cogs", "tax"],
        }),
        "severity": "critical",
    },
    # --- Posting Pattern Rules ---
    {
        "rule_name": "sales_invoice_revenue_pattern",
        "category": "posting_pattern",
        "description": "Sales invoice revenue line must credit an Income-type account, "
                       "not an Expense or Asset account.",
        "rule_definition": json.dumps({
            "check": "voucher_credit_pattern",
            "voucher_type": "sales_invoice",
            "entry_set": "primary",
            "expected_credit_root_types": ["income"],
            "forbidden_credit_root_types": ["expense"],
        }),
        "severity": "critical",
    },
    {
        "rule_name": "purchase_invoice_expense_pattern",
        "category": "posting_pattern",
        "description": "Purchase invoice expense line must debit an Expense-type account, "
                       "not an Income account.",
        "rule_definition": json.dumps({
            "check": "voucher_debit_pattern",
            "voucher_type": "purchase_invoice",
            "entry_set": "primary",
            "expected_debit_root_types": ["expense", "asset"],
            "forbidden_debit_root_types": ["income"],
        }),
        "severity": "critical",
    },
    {
        "rule_name": "payment_receivable_pattern",
        "category": "posting_pattern",
        "description": "Customer payment entries should credit a receivable (asset) account. "
                       "Crediting a revenue account directly bypasses receivable tracking.",
        "rule_definition": json.dumps({
            "check": "payment_account_type",
            "party_type": "customer",
            "expected_account_types": ["receivable", "bank", "cash"],
            "forbidden_account_types": ["revenue"],
        }),
        "severity": "warning",
    },
    {
        "rule_name": "payment_payable_pattern",
        "category": "posting_pattern",
        "description": "Supplier payment entries should debit a payable (liability) account. "
                       "Debiting an expense account directly bypasses payable tracking.",
        "rule_definition": json.dumps({
            "check": "payment_account_type",
            "party_type": "supplier",
            "expected_account_types": ["payable", "bank", "cash"],
            "forbidden_account_types": ["expense"],
        }),
        "severity": "warning",
    },
    # --- Period Validation Rules ---
    {
        "rule_name": "revenue_before_service_date",
        "category": "period_validation",
        "description": "Revenue cannot be recognized before service delivery date (ASC 606). "
                       "Revenue entries with posting_date before the associated obligation "
                       "satisfaction date indicate premature recognition.",
        "rule_definition": json.dumps({
            "check": "revenue_timing",
        }),
        "severity": "warning",
    },
    {
        "rule_name": "prepayment_to_liability",
        "category": "period_validation",
        "description": "Customer prepayments must post to a liability account (unearned revenue), "
                       "not directly to revenue. Recognizing prepayment as revenue violates "
                       "ASC 606 Step 5.",
        "rule_definition": json.dumps({
            "check": "prepayment_account",
        }),
        "severity": "critical",
    },
    {
        "rule_name": "depreciation_schedule_adherence",
        "category": "period_validation",
        "description": "Depreciation entries must follow the asset's depreciation schedule. "
                       "Out-of-schedule depreciation distorts period-over-period comparability.",
        "rule_definition": json.dumps({
            "check": "depreciation_timing",
        }),
        "severity": "warning",
    },
]


# ---------------------------------------------------------------------------
# Table Setup & Seeding
# ---------------------------------------------------------------------------

def ensure_semantic_tables(conn):
    """Create semantic rule and finding tables if they don't exist."""
    from erpclaw_lib.query import ddl_now
    _dn = ddl_now()
    conn.executescript(f"""
        CREATE TABLE IF NOT EXISTS erpclaw_semantic_rule (
            id              TEXT PRIMARY KEY,
            rule_name       TEXT NOT NULL UNIQUE,
            category        TEXT NOT NULL CHECK(category IN ('account_classification', 'posting_pattern', 'period_validation')),
            description     TEXT NOT NULL,
            rule_definition TEXT NOT NULL,
            severity        TEXT NOT NULL CHECK(severity IN ('critical', 'warning', 'info')),
            source_module   TEXT,
            is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
            created_at      TEXT DEFAULT ({_dn}),
            updated_at      TEXT DEFAULT ({_dn})
        );

        CREATE TABLE IF NOT EXISTS erpclaw_semantic_finding (
            id              TEXT PRIMARY KEY,
            module_name     TEXT NOT NULL,
            rule_id         TEXT NOT NULL REFERENCES erpclaw_semantic_rule(id),
            finding_type    TEXT NOT NULL CHECK(finding_type IN ('account_classification', 'posting_pattern', 'period_validation')),
            severity        TEXT NOT NULL CHECK(severity IN ('critical', 'warning', 'info')),
            description     TEXT NOT NULL,
            evidence        TEXT,
            status          TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'acknowledged', 'resolved', 'false_positive')),
            found_at        TEXT DEFAULT ({_dn}),
            resolved_at     TEXT,
            resolved_by     TEXT
        );
    """)


def _seed_default_rules(conn):
    """Seed default semantic rules if the table is empty."""
    count = conn.execute(
        "SELECT COUNT(*) FROM erpclaw_semantic_rule"
    ).fetchone()[0]
    if count > 0:
        return

    now = datetime.now(timezone.utc).isoformat()
    for rule in DEFAULT_RULES:
        conn.execute(
            "INSERT INTO erpclaw_semantic_rule "
            "(id, rule_name, category, description, rule_definition, severity, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                rule["rule_name"],
                rule["category"],
                rule["description"],
                rule["rule_definition"],
                rule["severity"],
                now, now,
            ),
        )
    conn.commit()


def _get_active_rules(conn, category=None):
    """Fetch all active semantic rules, optionally filtered by category."""
    if category:
        rows = conn.execute(
            "SELECT id, rule_name, category, description, rule_definition, severity "
            "FROM erpclaw_semantic_rule WHERE is_active = 1 AND category = ?",
            (category,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, rule_name, category, description, rule_definition, severity "
            "FROM erpclaw_semantic_rule WHERE is_active = 1"
        ).fetchall()
    return [
        {
            "id": r[0], "rule_name": r[1], "category": r[2],
            "description": r[3], "rule_definition": json.loads(r[4]),
            "severity": r[5],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Finding Persistence
# ---------------------------------------------------------------------------

def _record_finding(conn, module_name, rule_id, finding_type, severity,
                    description, evidence=None):
    """Record a semantic finding and return its ID."""
    finding_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO erpclaw_semantic_finding "
        "(id, module_name, rule_id, finding_type, severity, description, evidence, found_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            finding_id, module_name, rule_id, finding_type, severity,
            description,
            json.dumps(evidence) if evidence else None,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    return finding_id


# ---------------------------------------------------------------------------
# Check: Account Classification
# ---------------------------------------------------------------------------

def _check_account_classification(conn, module_name):
    """Verify GL entries use accounts with correct root_type for each voucher type.

    Returns list of finding dicts.
    """
    findings = []

    # Check if required tables exist
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    if "gl_entry" not in tables or "account" not in tables:
        return findings

    rules = _get_active_rules(conn, "account_classification")

    for rule in rules:
        defn = rule["rule_definition"]
        check_type = defn.get("check", "")

        if check_type == "gl_credit_root_type":
            voucher_types = defn.get("voucher_types", [])
            expected = set(defn.get("expected_credit_root_types", []))
            exclude_sets = set(defn.get("exclude_entry_sets", []))

            if not voucher_types or not expected:
                continue

            placeholders = ",".join("?" for _ in voucher_types)
            sql = (
                f"SELECT g.id, g.voucher_id, g.voucher_type, g.entry_set, "
                f"g.credit, a.id AS account_id, a.name AS account_name, a.root_type "
                f"FROM gl_entry g "
                f"JOIN account a ON g.account_id = a.id "
                f"WHERE g.voucher_type IN ({placeholders}) "
                f"AND CAST(g.credit AS NUMERIC) > 0 "
                f"AND g.is_cancelled = 0 "
                f"AND a.root_type NOT IN ({','.join('?' for _ in expected)})"
            )
            params = list(voucher_types) + list(expected)
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError:
                continue

            for row in rows:
                gl_id, voucher_id, voucher_type, entry_set, credit, account_id, acct_name, root_type = row
                if entry_set in exclude_sets:
                    continue
                evidence = {
                    "gl_entry_id": gl_id,
                    "voucher_id": voucher_id,
                    "voucher_type": voucher_type,
                    "account_id": account_id,
                    "account_name": acct_name,
                    "expected_type": list(expected),
                    "actual_type": root_type,
                    "amount": str(credit),
                }
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["rule_name"],
                    "category": "account_classification",
                    "severity": rule["severity"],
                    "description": (
                        f"{voucher_type} ({voucher_id}): credit of {credit} to "
                        f"account '{acct_name}' has root_type='{root_type}', "
                        f"expected {expected}"
                    ),
                    "evidence": evidence,
                })

        elif check_type == "gl_debit_root_type":
            voucher_types = defn.get("voucher_types", [])
            expected = set(defn.get("expected_debit_root_types", []))
            exclude_sets = set(defn.get("exclude_entry_sets", []))

            if not voucher_types or not expected:
                continue

            placeholders = ",".join("?" for _ in voucher_types)
            sql = (
                f"SELECT g.id, g.voucher_id, g.voucher_type, g.entry_set, "
                f"g.debit, a.id AS account_id, a.name AS account_name, a.root_type "
                f"FROM gl_entry g "
                f"JOIN account a ON g.account_id = a.id "
                f"WHERE g.voucher_type IN ({placeholders}) "
                f"AND CAST(g.debit AS NUMERIC) > 0 "
                f"AND g.is_cancelled = 0 "
                f"AND a.root_type NOT IN ({','.join('?' for _ in expected)})"
            )
            params = list(voucher_types) + list(expected)
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError:
                continue

            for row in rows:
                gl_id, voucher_id, voucher_type, entry_set, debit, account_id, acct_name, root_type = row
                if entry_set in exclude_sets:
                    continue
                evidence = {
                    "gl_entry_id": gl_id,
                    "voucher_id": voucher_id,
                    "voucher_type": voucher_type,
                    "account_id": account_id,
                    "account_name": acct_name,
                    "expected_type": list(expected),
                    "actual_type": root_type,
                    "amount": str(debit),
                }
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["rule_name"],
                    "category": "account_classification",
                    "severity": rule["severity"],
                    "description": (
                        f"{voucher_type} ({voucher_id}): debit of {debit} to "
                        f"account '{acct_name}' has root_type='{root_type}', "
                        f"expected {expected}"
                    ),
                    "evidence": evidence,
                })

    return findings


# ---------------------------------------------------------------------------
# Check: Posting Patterns
# ---------------------------------------------------------------------------

def _check_posting_patterns(conn, module_name):
    """Verify voucher posting patterns match expected account types.

    Returns list of finding dicts.
    """
    findings = []

    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    if "gl_entry" not in tables or "account" not in tables:
        return findings

    rules = _get_active_rules(conn, "posting_pattern")

    for rule in rules:
        defn = rule["rule_definition"]
        check_type = defn.get("check", "")

        if check_type == "voucher_credit_pattern":
            voucher_type = defn.get("voucher_type", "")
            entry_set = defn.get("entry_set", "primary")
            forbidden = set(defn.get("forbidden_credit_root_types", []))

            if not voucher_type or not forbidden:
                continue

            sql = (
                "SELECT g.id, g.voucher_id, g.credit, "
                "a.id AS account_id, a.name AS account_name, a.root_type "
                "FROM gl_entry g "
                "JOIN account a ON g.account_id = a.id "
                "WHERE g.voucher_type = ? "
                "AND g.entry_set = ? "
                "AND CAST(g.credit AS NUMERIC) > 0 "
                "AND g.is_cancelled = 0 "
                "AND a.root_type IN ({})".format(",".join("?" for _ in forbidden))
            )
            params = [voucher_type, entry_set] + list(forbidden)
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError:
                continue

            for row in rows:
                gl_id, voucher_id, credit, account_id, acct_name, root_type = row
                evidence = {
                    "gl_entry_id": gl_id,
                    "voucher_id": voucher_id,
                    "voucher_type": voucher_type,
                    "account_id": account_id,
                    "account_name": acct_name,
                    "expected_type": list(set(defn.get("expected_credit_root_types", []))),
                    "actual_type": root_type,
                    "amount": str(credit),
                }
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["rule_name"],
                    "category": "posting_pattern",
                    "severity": rule["severity"],
                    "description": (
                        f"{voucher_type} ({voucher_id}): credit to '{acct_name}' "
                        f"(root_type='{root_type}') violates posting pattern — "
                        f"forbidden root_type for this voucher"
                    ),
                    "evidence": evidence,
                })

        elif check_type == "voucher_debit_pattern":
            voucher_type = defn.get("voucher_type", "")
            entry_set = defn.get("entry_set", "primary")
            forbidden = set(defn.get("forbidden_debit_root_types", []))

            if not voucher_type or not forbidden:
                continue

            sql = (
                "SELECT g.id, g.voucher_id, g.debit, "
                "a.id AS account_id, a.name AS account_name, a.root_type "
                "FROM gl_entry g "
                "JOIN account a ON g.account_id = a.id "
                "WHERE g.voucher_type = ? "
                "AND g.entry_set = ? "
                "AND CAST(g.debit AS NUMERIC) > 0 "
                "AND g.is_cancelled = 0 "
                "AND a.root_type IN ({})".format(",".join("?" for _ in forbidden))
            )
            params = [voucher_type, entry_set] + list(forbidden)
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError:
                continue

            for row in rows:
                gl_id, voucher_id, debit, account_id, acct_name, root_type = row
                evidence = {
                    "gl_entry_id": gl_id,
                    "voucher_id": voucher_id,
                    "voucher_type": voucher_type,
                    "account_id": account_id,
                    "account_name": acct_name,
                    "expected_type": list(set(defn.get("expected_debit_root_types", []))),
                    "actual_type": root_type,
                    "amount": str(debit),
                }
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["rule_name"],
                    "category": "posting_pattern",
                    "severity": rule["severity"],
                    "description": (
                        f"{voucher_type} ({voucher_id}): debit to '{acct_name}' "
                        f"(root_type='{root_type}') violates posting pattern — "
                        f"forbidden root_type for this voucher"
                    ),
                    "evidence": evidence,
                })

        elif check_type == "payment_account_type":
            party_type = defn.get("party_type", "")
            forbidden_types = set(defn.get("forbidden_account_types", []))

            if not party_type or not forbidden_types:
                continue

            sql = (
                "SELECT g.id, g.voucher_id, g.debit, g.credit, "
                "a.id AS account_id, a.name AS account_name, a.root_type, a.account_type "
                "FROM gl_entry g "
                "JOIN account a ON g.account_id = a.id "
                "WHERE g.voucher_type = 'payment_entry' "
                "AND g.party_type = ? "
                "AND g.is_cancelled = 0 "
                "AND a.account_type IN ({})".format(",".join("?" for _ in forbidden_types))
            )
            params = [party_type] + list(forbidden_types)
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError:
                continue

            for row in rows:
                gl_id, voucher_id, debit, credit, account_id, acct_name, root_type, acct_type = row
                amount = debit if Decimal(str(debit or "0")) > 0 else credit
                evidence = {
                    "gl_entry_id": gl_id,
                    "voucher_id": voucher_id,
                    "voucher_type": "payment_entry",
                    "account_id": account_id,
                    "account_name": acct_name,
                    "expected_type": list(set(defn.get("expected_account_types", []))),
                    "actual_type": acct_type,
                    "amount": str(amount),
                }
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["rule_name"],
                    "category": "posting_pattern",
                    "severity": rule["severity"],
                    "description": (
                        f"payment_entry ({voucher_id}): party_type={party_type}, "
                        f"account '{acct_name}' has account_type='{acct_type}' — "
                        f"expected one of {defn.get('expected_account_types', [])}"
                    ),
                    "evidence": evidence,
                })

    return findings


# ---------------------------------------------------------------------------
# Check: Period Validation
# ---------------------------------------------------------------------------

def _check_period_validation(conn, module_name):
    """Validate revenue timing, prepayment accounts, and depreciation schedule.

    Returns list of finding dicts.
    """
    findings = []

    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}

    rules = _get_active_rules(conn, "period_validation")

    for rule in rules:
        defn = rule["rule_definition"]
        check_type = defn.get("check", "")

        if check_type == "revenue_timing":
            # Check if revenue_contract and performance_obligation tables exist
            if "revenue_contract" not in tables or "performance_obligation" not in tables:
                continue
            if "gl_entry" not in tables:
                continue

            try:
                # Find revenue entries posted before obligation satisfaction
                rows = conn.execute("""
                    SELECT g.id, g.voucher_id, g.posting_date, g.credit,
                           a.id AS account_id, a.name AS account_name,
                           po.satisfaction_date
                    FROM gl_entry g
                    JOIN account a ON g.account_id = a.id
                    JOIN performance_obligation po ON g.voucher_id = po.contract_id
                    WHERE a.root_type = 'income'
                      AND CAST(g.credit AS NUMERIC) > 0
                      AND g.is_cancelled = 0
                      AND po.satisfaction_date IS NOT NULL
                      AND g.posting_date < po.satisfaction_date
                """).fetchall()
            except sqlite3.OperationalError:
                continue

            for row in rows:
                gl_id, voucher_id, posting_date, credit, account_id, acct_name, satisfaction_date = row
                evidence = {
                    "gl_entry_id": gl_id,
                    "voucher_id": voucher_id,
                    "account_id": account_id,
                    "posting_date": posting_date,
                    "satisfaction_date": satisfaction_date,
                    "expected_type": "income (after satisfaction)",
                    "actual_type": f"income (posted {posting_date}, satisfied {satisfaction_date})",
                    "amount": str(credit),
                }
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["rule_name"],
                    "category": "period_validation",
                    "severity": rule["severity"],
                    "description": (
                        f"Revenue of {credit} recognized on {posting_date} "
                        f"before service satisfaction on {satisfaction_date} "
                        f"(ASC 606 violation)"
                    ),
                    "evidence": evidence,
                })

        elif check_type == "prepayment_account":
            if "gl_entry" not in tables or "account" not in tables:
                continue

            # Find payment entries where advance/prepay goes directly to revenue
            try:
                rows = conn.execute("""
                    SELECT g.id, g.voucher_id, g.credit,
                           a.id AS account_id, a.name AS account_name, a.root_type
                    FROM gl_entry g
                    JOIN account a ON g.account_id = a.id
                    WHERE g.voucher_type = 'payment_entry'
                      AND g.is_cancelled = 0
                      AND CAST(g.credit AS NUMERIC) > 0
                      AND a.root_type = 'income'
                      AND g.remarks LIKE '%advance%'
                """).fetchall()
            except sqlite3.OperationalError:
                continue

            for row in rows:
                gl_id, voucher_id, credit, account_id, acct_name, root_type = row
                evidence = {
                    "gl_entry_id": gl_id,
                    "voucher_id": voucher_id,
                    "account_id": account_id,
                    "account_name": acct_name,
                    "expected_type": "liability",
                    "actual_type": root_type,
                    "amount": str(credit),
                }
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["rule_name"],
                    "category": "period_validation",
                    "severity": rule["severity"],
                    "description": (
                        f"Advance payment ({voucher_id}): credit of {credit} to "
                        f"income account '{acct_name}' — prepayments must post to "
                        f"a liability account (unearned revenue)"
                    ),
                    "evidence": evidence,
                })

        elif check_type == "depreciation_timing":
            if "gl_entry" not in tables or "asset" not in tables:
                continue

            # Check for depreciation entries posted outside the asset's schedule
            try:
                rows = conn.execute("""
                    SELECT g.id, g.voucher_id, g.posting_date, g.debit,
                           a.id AS account_id, a.name AS account_name
                    FROM gl_entry g
                    JOIN account a ON g.account_id = a.id
                    WHERE g.voucher_type = 'depreciation_entry'
                      AND g.is_cancelled = 0
                      AND a.account_type = 'depreciation'
                      AND NOT EXISTS (
                          SELECT 1 FROM asset_depreciation_schedule ads
                          WHERE ads.asset_id = g.voucher_id
                            AND ads.schedule_date = g.posting_date
                      )
                """).fetchall()
            except sqlite3.OperationalError:
                continue

            for row in rows:
                gl_id, voucher_id, posting_date, debit, account_id, acct_name = row
                evidence = {
                    "gl_entry_id": gl_id,
                    "voucher_id": voucher_id,
                    "account_id": account_id,
                    "posting_date": posting_date,
                    "expected_type": "scheduled depreciation",
                    "actual_type": "unscheduled depreciation",
                    "amount": str(debit),
                }
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["rule_name"],
                    "category": "period_validation",
                    "severity": rule["severity"],
                    "description": (
                        f"Depreciation entry ({voucher_id}) on {posting_date} "
                        f"does not match any scheduled depreciation date"
                    ),
                    "evidence": evidence,
                })

    return findings


# ---------------------------------------------------------------------------
# Main Entry Points
# ---------------------------------------------------------------------------

def semantic_check(conn, module_name):
    """Run all semantic rules against a module's GL entries.

    Args:
        conn: SQLite connection (with WAL, FK, busy_timeout already set)
        module_name: Name of the module to check

    Returns:
        list of finding dicts, each with:
            rule_name, rule_id, category, severity, description, evidence
    """
    ensure_semantic_tables(conn)
    _seed_default_rules(conn)

    all_findings = []

    # Run all three check categories
    all_findings.extend(_check_account_classification(conn, module_name))
    all_findings.extend(_check_posting_patterns(conn, module_name))
    all_findings.extend(_check_period_validation(conn, module_name))

    # Persist findings
    for finding in all_findings:
        _record_finding(
            conn, module_name,
            rule_id=finding["rule_id"],
            finding_type=finding["category"],
            severity=finding["severity"],
            description=finding["description"],
            evidence=finding.get("evidence"),
        )
    conn.commit()

    return all_findings


def list_semantic_rules(conn):
    """Return all active semantic rules.

    Args:
        conn: SQLite connection

    Returns:
        list of rule dicts
    """
    ensure_semantic_tables(conn)
    _seed_default_rules(conn)

    rows = conn.execute(
        "SELECT id, rule_name, category, description, severity, is_active, source_module "
        "FROM erpclaw_semantic_rule WHERE is_active = 1 "
        "ORDER BY category, rule_name"
    ).fetchall()

    return [
        {
            "id": r[0],
            "rule_name": r[1],
            "category": r[2],
            "description": r[3],
            "severity": r[4],
            "is_active": r[5],
            "source_module": r[6],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# CLI Handlers
# ---------------------------------------------------------------------------

def handle_semantic_check(args):
    """CLI handler for semantic-check action."""
    module_name = getattr(args, "module_name", None)
    db_path = getattr(args, "db_path", None) or DEFAULT_DB_PATH

    if not module_name:
        return {"error": "--module-name is required for semantic-check"}

    start_time = time.time()

    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)

    try:
        findings = semantic_check(conn, module_name)
    finally:
        conn.close()

    duration_ms = int((time.time() - start_time) * 1000)

    severity_counts = {
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "warning": sum(1 for f in findings if f["severity"] == "warning"),
        "info": sum(1 for f in findings if f["severity"] == "info"),
    }

    return {
        "result": "fail" if severity_counts["critical"] > 0 else "pass",
        "module": module_name,
        "findings": findings,
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "checks_run": [
            "account_classification",
            "posting_pattern",
            "period_validation",
        ],
        "duration_ms": duration_ms,
    }


def handle_semantic_rules_list(args):
    """CLI handler for semantic-rules-list action."""
    db_path = getattr(args, "db_path", None) or DEFAULT_DB_PATH

    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)

    try:
        rules = list_semantic_rules(conn)
    finally:
        conn.close()

    # Group by category
    by_category = {}
    for rule in rules:
        by_category.setdefault(rule["category"], []).append(rule)

    return {
        "rules": rules,
        "count": len(rules),
        "by_category": {k: len(v) for k, v in by_category.items()},
    }
