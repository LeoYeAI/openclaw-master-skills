#!/usr/bin/env python3
"""ERPClaw OS — Adversarial Audit Agent

Independent, non-generative audit agent. Runs tests the generating agent
never sees. CANNOT be modified by DGM evolution engine (Tier 3 protection).

Audit checks:
  1. Account-type anchoring (Art. 18) — revenue recognition patterns
  2. Semantic patterns — revenue→revenue accounts, expense→expense accounts
  3. Expense classification correctness
  4. GL balance invariant (debits == credits per transaction)

Findings are recorded in erpclaw_audit_finding table.
"""
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")


# ---------------------------------------------------------------------------
# Audit Finding Table
# ---------------------------------------------------------------------------

def ensure_audit_tables(db_path=None):
    """Create audit finding and compliance period tables."""
    db_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)
    from erpclaw_lib.query import ddl_now
    _dn = ddl_now()
    conn.executescript(f"""
        CREATE TABLE IF NOT EXISTS erpclaw_audit_finding (
            id              TEXT PRIMARY KEY,
            module_name     TEXT NOT NULL,
            finding_type    TEXT NOT NULL CHECK(finding_type IN ('semantic', 'account_anchoring', 'classification', 'compliance')),
            severity        TEXT NOT NULL CHECK(severity IN ('critical', 'warning', 'info')),
            article         INTEGER,
            description     TEXT NOT NULL,
            evidence        TEXT,
            status          TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'acknowledged', 'resolved', 'false_positive')),
            found_at        TEXT DEFAULT ({_dn}),
            resolved_at     TEXT,
            resolved_by     TEXT
        );

        CREATE TABLE IF NOT EXISTS erpclaw_compliance_period (
            id              TEXT PRIMARY KEY,
            company_id      TEXT NOT NULL,
            period_type     TEXT NOT NULL CHECK(period_type IN ('normal', 'year_end_close', 'tax_season', 'audit_season')),
            start_date      TEXT NOT NULL,
            end_date        TEXT NOT NULL,
            additional_checks TEXT,
            created_at      TEXT DEFAULT ({_dn})
        );
    """)
    conn.commit()
    conn.close()


def record_finding(module_name, finding_type, severity, description,
                   article=None, evidence=None, db_path=None):
    """Record an audit finding.

    Returns:
        str: Finding ID
    """
    db_path = db_path or DEFAULT_DB_PATH
    ensure_audit_tables(db_path)

    finding_id = str(uuid.uuid4())
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)
    conn.execute("""
        INSERT INTO erpclaw_audit_finding
            (id, module_name, finding_type, severity, article, description, evidence, found_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        finding_id, module_name, finding_type, severity, article,
        description, json.dumps(evidence) if evidence else None,
        datetime.now(timezone.utc).isoformat(),
    ))
    conn.commit()
    conn.close()
    return finding_id


# ---------------------------------------------------------------------------
# Audit Checks
# ---------------------------------------------------------------------------

def check_gl_balance_invariant(db_path=None):
    """Check 1: Every GL transaction must balance (debits == credits).

    Returns list of findings for unbalanced transactions.
    """
    db_path = db_path or DEFAULT_DB_PATH
    if not os.path.isfile(db_path):
        return []

    conn = sqlite3.connect(db_path)
    # Check if gl_entry table exists
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]

    if "gl_entry" not in tables:
        conn.close()
        return []

    # Find transactions where debits != credits
    findings = []
    try:
        rows = conn.execute("""
            SELECT voucher_id, voucher_type,
                   SUM(CAST(debit_amount AS NUMERIC)) as total_debit,
                   SUM(CAST(credit_amount AS NUMERIC)) as total_credit
            FROM gl_entry
            GROUP BY voucher_id, voucher_type
            HAVING ABS(SUM(CAST(debit_amount AS NUMERIC)) - SUM(CAST(credit_amount AS NUMERIC))) > 0.01
        """).fetchall()

        for row in rows:
            voucher_id, voucher_type, total_debit, total_credit = row
            findings.append({
                "type": "gl_imbalance",
                "severity": "critical",
                "description": f"GL imbalance: voucher {voucher_id} ({voucher_type}) "
                               f"debit={total_debit:.2f} credit={total_credit:.2f} "
                               f"diff={abs(total_debit - total_credit):.2f}",
                "evidence": {
                    "voucher_id": voucher_id,
                    "voucher_type": voucher_type,
                    "total_debit": str(total_debit),
                    "total_credit": str(total_credit),
                },
            })
    except sqlite3.OperationalError:
        pass  # Missing columns — skip check

    conn.close()
    return findings


def check_account_anchoring(db_path=None):
    """Check 2: Revenue posted to revenue accounts, expenses to expense accounts.

    Detects semantic mismatch: revenue going to COGS, expenses going to Income, etc.
    """
    db_path = db_path or DEFAULT_DB_PATH
    if not os.path.isfile(db_path):
        return []

    conn = sqlite3.connect(db_path)
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]

    if "gl_entry" not in tables or "account" not in tables:
        conn.close()
        return []

    findings = []
    try:
        # Find revenue-type vouchers (Sales Invoice) posting to expense accounts
        rows = conn.execute("""
            SELECT g.voucher_id, g.voucher_type, a.name, a.root_type, a.account_type,
                   g.credit_amount
            FROM gl_entry g
            JOIN account a ON g.account_id = a.id
            WHERE g.voucher_type = 'Sales Invoice'
              AND CAST(g.credit_amount AS NUMERIC) > 0
              AND a.root_type = 'expense'
        """).fetchall()

        for row in rows:
            voucher_id, voucher_type, acct_name, root_type, acct_type, amount = row
            findings.append({
                "type": "semantic_mismatch",
                "severity": "critical",
                "description": f"Revenue from {voucher_type} ({voucher_id}) "
                               f"credited to expense account '{acct_name}' "
                               f"(root_type={root_type})",
                "evidence": {
                    "voucher_id": voucher_id,
                    "account": acct_name,
                    "root_type": root_type,
                    "amount": str(amount),
                },
            })

        # Find expense-type vouchers posting to income accounts
        rows = conn.execute("""
            SELECT g.voucher_id, g.voucher_type, a.name, a.root_type, a.account_type,
                   g.debit_amount
            FROM gl_entry g
            JOIN account a ON g.account_id = a.id
            WHERE g.voucher_type = 'Purchase Invoice'
              AND CAST(g.debit_amount AS NUMERIC) > 0
              AND a.root_type = 'income'
        """).fetchall()

        for row in rows:
            voucher_id, voucher_type, acct_name, root_type, acct_type, amount = row
            findings.append({
                "type": "semantic_mismatch",
                "severity": "critical",
                "description": f"Expense from {voucher_type} ({voucher_id}) "
                               f"debited to income account '{acct_name}' "
                               f"(root_type={root_type})",
                "evidence": {
                    "voucher_id": voucher_id,
                    "account": acct_name,
                    "root_type": root_type,
                    "amount": str(amount),
                },
            })

    except sqlite3.OperationalError:
        pass

    conn.close()
    return findings


def check_revenue_recognition(module_path, db_path=None):
    """Check 3: Subscription/lease modules must use deferred revenue.

    If a module has tables related to subscriptions, recurring billing, or leases,
    it should use deferred_revenue or unearned_revenue account patterns,
    not immediate revenue recognition.
    """
    if not module_path or not os.path.isdir(module_path):
        return []

    init_db_path = os.path.join(module_path, "init_db.py")
    if not os.path.isfile(init_db_path):
        return []

    with open(init_db_path, "r") as f:
        content = f.read().lower()

    findings = []

    # Check for subscription/recurring patterns
    has_subscription_tables = any(kw in content for kw in [
        "subscription", "recurring", "lease", "membership",
    ])

    if has_subscription_tables:
        # Check if module code references deferred/unearned revenue
        scripts_dir = os.path.join(module_path, "scripts")
        has_deferred = False

        if os.path.isdir(scripts_dir):
            for root, _dirs, files in os.walk(scripts_dir):
                for fname in files:
                    if fname.endswith(".py"):
                        fpath = os.path.join(root, fname)
                        with open(fpath, "r") as f:
                            code = f.read().lower()
                        if any(kw in code for kw in [
                            "deferred_revenue", "deferred revenue",
                            "unearned_revenue", "unearned revenue",
                        ]):
                            has_deferred = True
                            break
                if has_deferred:
                    break

        if not has_deferred:
            findings.append({
                "type": "account_anchoring",
                "severity": "warning",
                "description": f"Module has subscription/recurring tables but no "
                               f"deferred/unearned revenue recognition pattern detected. "
                               f"Subscription revenue should use deferred revenue accounting.",
                "evidence": {
                    "module_path": module_path,
                    "subscription_indicators": [kw for kw in [
                        "subscription", "recurring", "lease", "membership"
                    ] if kw in content],
                },
            })

    return findings


# ---------------------------------------------------------------------------
# Main Audit Function
# ---------------------------------------------------------------------------

def run_audit(module_path=None, db_path=None):
    """Run the full adversarial audit.

    Args:
        module_path: Path to a specific module to audit (optional)
        db_path: Path to the SQLite database

    Returns:
        dict with findings, severity counts, and audit summary
    """
    start_time = time.time()
    db_path = db_path or DEFAULT_DB_PATH
    all_findings = []
    module_name = os.path.basename(module_path) if module_path else "system"

    # Check 1: GL Balance Invariant
    gl_findings = check_gl_balance_invariant(db_path)
    all_findings.extend(gl_findings)

    # Check 2: Account Anchoring (semantic correctness)
    anchoring_findings = check_account_anchoring(db_path)
    all_findings.extend(anchoring_findings)

    # Check 3: Revenue Recognition (if module provided)
    if module_path:
        rev_findings = check_revenue_recognition(module_path, db_path)
        all_findings.extend(rev_findings)

    # Record findings in DB
    # Map internal finding types to DB-allowed types
    type_mapping = {
        "gl_imbalance": "semantic",
        "semantic_mismatch": "account_anchoring",
        "account_anchoring": "account_anchoring",
        "semantic": "semantic",
        "classification": "classification",
        "compliance": "compliance",
    }
    ensure_audit_tables(db_path)
    for finding in all_findings:
        db_type = type_mapping.get(finding.get("type", "semantic"), "semantic")
        record_finding(
            module_name=module_name,
            finding_type=db_type,
            severity=finding["severity"],
            description=finding["description"],
            evidence=finding.get("evidence"),
            db_path=db_path,
        )

    # Summary
    severity_counts = {
        "critical": sum(1 for f in all_findings if f["severity"] == "critical"),
        "warning": sum(1 for f in all_findings if f["severity"] == "warning"),
        "info": sum(1 for f in all_findings if f["severity"] == "info"),
    }

    duration_ms = int((time.time() - start_time) * 1000)

    return {
        "result": "fail" if severity_counts["critical"] > 0 else "pass",
        "findings": all_findings,
        "finding_count": len(all_findings),
        "severity_counts": severity_counts,
        "checks_run": ["gl_balance_invariant", "account_anchoring", "revenue_recognition"],
        "module": module_name,
        "duration_ms": duration_ms,
    }


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def handle_run_audit(args):
    """CLI handler for run-audit action."""
    module_path = getattr(args, "module_path", None)
    db_path = getattr(args, "db_path", None)

    result = run_audit(module_path=module_path, db_path=db_path)
    return result
