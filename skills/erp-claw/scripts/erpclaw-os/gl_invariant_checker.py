"""Post-test GL invariant verification.

Connects to a sandbox (or any) SQLite database and verifies that all
General Ledger entries satisfy the fundamental accounting invariants:

1. Global balance: SUM(debit) == SUM(credit) across all non-cancelled entries
2. Per-voucher balance: each voucher balances independently
3. No zero-zero entries: no gl_entry with debit=0 AND credit=0
4. Valid accounts: every account_id references an existing account
5. Valid fiscal year: every fiscal_year references an existing fiscal_year

All comparisons use Python Decimal — never float.
"""
import sqlite3
from decimal import Decimal, ROUND_HALF_UP


# Tolerance for balance comparisons (sub-cent)
_TOLERANCE = Decimal("0.001")


def check_gl_invariants(db_path: str) -> dict:
    """Run GL invariant checks against a database.

    Args:
        db_path: Absolute path to the SQLite database file.

    Returns:
        {
            "result": "pass" | "fail" | "skip",
            "reason": str (only if result == "skip"),
            "checks": [
                {"name": str, "result": "pass"|"fail", "detail": str},
                ...
            ],
            "violations": [str, ...]
        }
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)

    try:
        # Check if gl_entry table exists
        table_exists = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type='table' AND name='gl_entry'"
        ).fetchone()[0]
        if not table_exists:
            return {
                "result": "skip",
                "reason": "gl_entry table does not exist",
                "checks": [],
                "violations": [],
            }

        # Check if there are any GL entries
        entry_count = conn.execute(
            "SELECT COUNT(*) FROM gl_entry WHERE is_cancelled = 0"
        ).fetchone()[0]
        if entry_count == 0:
            return {
                "result": "skip",
                "reason": "no GL entries",
                "checks": [],
                "violations": [],
            }

        checks = []
        violations = []

        # --- Check 1: Global balance ---
        _check_global_balance(conn, checks, violations)

        # --- Check 2: Per-voucher balance ---
        _check_per_voucher_balance(conn, checks, violations)

        # --- Check 3: No zero-zero entries ---
        _check_no_zero_zero(conn, checks, violations)

        # --- Check 4: Valid accounts ---
        _check_valid_accounts(conn, checks, violations)

        # --- Check 5: Valid fiscal year ---
        _check_valid_fiscal_year(conn, checks, violations)

        overall = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
        return {
            "result": overall,
            "checks": checks,
            "violations": violations,
        }
    finally:
        conn.close()


def _check_global_balance(conn, checks, violations):
    """Check 1: SUM(debit) == SUM(credit) globally for non-cancelled entries."""
    rows = conn.execute(
        "SELECT debit, credit FROM gl_entry WHERE is_cancelled = 0"
    ).fetchall()

    total_debit = Decimal("0")
    total_credit = Decimal("0")
    for row in rows:
        total_debit += Decimal(str(row["debit"]))
        total_credit += Decimal(str(row["credit"]))

    diff = abs(total_debit - total_credit)
    if diff <= _TOLERANCE:
        checks.append({
            "name": "global_balance",
            "result": "pass",
            "detail": f"Total debit={total_debit}, credit={total_credit}, diff={diff}",
        })
    else:
        detail = (
            f"IMBALANCE: total debit={total_debit}, "
            f"credit={total_credit}, diff={diff}"
        )
        checks.append({"name": "global_balance", "result": "fail", "detail": detail})
        violations.append(f"Global GL imbalance: {detail}")


def _check_per_voucher_balance(conn, checks, violations):
    """Check 2: Each voucher (type+id) must balance independently."""
    rows = conn.execute(
        "SELECT voucher_type, voucher_id, debit, credit "
        "FROM gl_entry WHERE is_cancelled = 0"
    ).fetchall()

    # Accumulate per voucher
    voucher_totals = {}
    for row in rows:
        key = (row["voucher_type"], row["voucher_id"])
        if key not in voucher_totals:
            voucher_totals[key] = {"debit": Decimal("0"), "credit": Decimal("0")}
        voucher_totals[key]["debit"] += Decimal(str(row["debit"]))
        voucher_totals[key]["credit"] += Decimal(str(row["credit"]))

    imbalanced = []
    for (vtype, vid), totals in voucher_totals.items():
        diff = abs(totals["debit"] - totals["credit"])
        if diff > _TOLERANCE:
            imbalanced.append({
                "voucher_type": vtype,
                "voucher_id": vid,
                "debit": str(totals["debit"]),
                "credit": str(totals["credit"]),
                "diff": str(diff),
            })

    if not imbalanced:
        checks.append({
            "name": "per_voucher_balance",
            "result": "pass",
            "detail": f"All {len(voucher_totals)} vouchers balanced",
        })
    else:
        detail = f"{len(imbalanced)} imbalanced voucher(s)"
        checks.append({
            "name": "per_voucher_balance",
            "result": "fail",
            "detail": detail,
        })
        for v in imbalanced:
            violations.append(
                f"Voucher {v['voucher_type']}:{v['voucher_id']} imbalanced: "
                f"debit={v['debit']}, credit={v['credit']}, diff={v['diff']}"
            )


def _check_no_zero_zero(conn, checks, violations):
    """Check 3: No gl_entry with both debit=0 AND credit=0 (non-cancelled)."""
    # Use Python Decimal to check — can't rely on CAST to REAL
    rows = conn.execute(
        "SELECT id, voucher_type, voucher_id, debit, credit "
        "FROM gl_entry WHERE is_cancelled = 0"
    ).fetchall()

    zero_zero = []
    for row in rows:
        d = Decimal(str(row["debit"]))
        c = Decimal(str(row["credit"]))
        if d == 0 and c == 0:
            zero_zero.append(dict(row))

    if not zero_zero:
        checks.append({
            "name": "no_zero_zero_entries",
            "result": "pass",
            "detail": "No zero-debit zero-credit entries found",
        })
    else:
        detail = f"{len(zero_zero)} zero-zero GL entry(ies) found"
        checks.append({
            "name": "no_zero_zero_entries",
            "result": "fail",
            "detail": detail,
        })
        for entry in zero_zero:
            violations.append(
                f"Zero-zero GL entry: id={entry['id']}, "
                f"voucher={entry['voucher_type']}:{entry['voucher_id']}"
            )


def _check_valid_accounts(conn, checks, violations):
    """Check 4: Every account_id in gl_entry references a valid account."""
    # Check if account table exists
    has_account = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master "
        "WHERE type='table' AND name='account'"
    ).fetchone()[0]
    if not has_account:
        checks.append({
            "name": "valid_accounts",
            "result": "pass",
            "detail": "account table does not exist — skipped",
        })
        return

    orphans = conn.execute(
        "SELECT ge.id, ge.account_id, ge.voucher_type, ge.voucher_id "
        "FROM gl_entry ge "
        "LEFT JOIN account a ON ge.account_id = a.id "
        "WHERE a.id IS NULL AND ge.is_cancelled = 0"
    ).fetchall()

    if not orphans:
        checks.append({
            "name": "valid_accounts",
            "result": "pass",
            "detail": "All GL entries reference valid accounts",
        })
    else:
        detail = f"{len(orphans)} GL entry(ies) with invalid account_id"
        checks.append({"name": "valid_accounts", "result": "fail", "detail": detail})
        for o in orphans:
            violations.append(
                f"Invalid account_id: gl_entry.id={o['id']}, "
                f"account_id={o['account_id']}, "
                f"voucher={o['voucher_type']}:{o['voucher_id']}"
            )


def _check_valid_fiscal_year(conn, checks, violations):
    """Check 5: Every fiscal_year in gl_entry references a valid fiscal_year."""
    # Check if fiscal_year table exists
    has_fy = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master "
        "WHERE type='table' AND name='fiscal_year'"
    ).fetchone()[0]
    if not has_fy:
        checks.append({
            "name": "valid_fiscal_year",
            "result": "pass",
            "detail": "fiscal_year table does not exist — skipped",
        })
        return

    # gl_entry.fiscal_year references fiscal_year.name
    orphans = conn.execute(
        "SELECT ge.id, ge.fiscal_year, ge.voucher_type, ge.voucher_id "
        "FROM gl_entry ge "
        "WHERE ge.fiscal_year IS NOT NULL "
        "AND ge.fiscal_year NOT IN (SELECT name FROM fiscal_year) "
        "AND ge.is_cancelled = 0"
    ).fetchall()

    if not orphans:
        checks.append({
            "name": "valid_fiscal_year",
            "result": "pass",
            "detail": "All GL entries reference valid fiscal years",
        })
    else:
        detail = f"{len(orphans)} GL entry(ies) with invalid fiscal_year"
        checks.append({
            "name": "valid_fiscal_year",
            "result": "fail",
            "detail": detail,
        })
        for o in orphans:
            violations.append(
                f"Invalid fiscal_year: gl_entry.id={o['id']}, "
                f"fiscal_year={o['fiscal_year']}, "
                f"voucher={o['voucher_type']}:{o['voucher_id']}"
            )
