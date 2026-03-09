"""General Ledger posting engine.

All GL writes go through this module. This is the ONLY code that writes to
the gl_entry table. Critical design invariant.

Key functions:
- validate_gl_entries(): 12-step ordered validation checklist
- insert_gl_entries(): Validate + insert within caller's transaction
- reverse_gl_entries(): Cancel by creating mirror entries
- get_account_balance(): Query balance for an account

NEVER commit inside these functions — the caller owns the transaction.
"""
import hashlib
import uuid
import sqlite3
from decimal import Decimal
from typing import Optional

from erpclaw_lib.decimal_utils import to_decimal, amounts_equal, round_currency
from erpclaw_lib.fx_posting import convert_to_base


# --- Helper: fetch account row ---

def _get_account(conn: sqlite3.Connection, account_id: str) -> dict:
    """Fetch an account row. Raises ValueError if not found."""
    row = conn.execute(
        "SELECT * FROM account WHERE id = ?", (account_id,)
    ).fetchone()
    if row is None:
        raise ValueError(f"Account {account_id} does not exist")
    return dict(row)


# --- Pre-validation: negative auto-toggle ---

def _normalize_entries(entries: list[dict]) -> list[dict]:
    """Normalize GL entries: flip negative debits/credits.

    If debit < 0, set credit = abs(debit), debit = 0.
    If credit < 0, set debit = abs(credit), credit = 0.
    """
    normalized = []
    for entry in entries:
        e = dict(entry)
        debit = to_decimal(e.get("debit", "0"))
        credit = to_decimal(e.get("credit", "0"))

        if debit < 0:
            credit = credit + abs(debit)
            debit = Decimal("0")
        if credit < 0:
            debit = debit + abs(credit)
            credit = Decimal("0")

        e["debit"] = str(round_currency(debit))
        e["credit"] = str(round_currency(credit))
        normalized.append(e)
    return normalized


# --- 12-Step Validation Checklist ---

def validate_gl_entries(
    conn: sqlite3.Connection,
    entries: list[dict],
    company_id: str,
    posting_date: str,
    is_opening: bool = False,
    voucher_type: str = "",
    context_role: str | None = None,
) -> list[str]:
    """Execute the 12-step GL validation checklist.

    Steps are executed in strict order (1-12). Validation stops at the
    FIRST failure and raises ValueError with a descriptive message.

    The pre-validation negative auto-toggle is applied before step 1.

    Returns:
        List of warning messages (e.g., budget warnings). Empty if no warnings.

    Raises:
        ValueError: Format "GL Validation Step {n} Failed: {message}"
    """
    warnings = []

    # Pre-validation: normalize negatives
    for i, entry in enumerate(entries):
        debit = to_decimal(entry.get("debit", "0"))
        credit = to_decimal(entry.get("credit", "0"))
        if debit < 0:
            entries[i]["credit"] = str(round_currency(abs(debit) + to_decimal(entry.get("credit", "0"))))
            entries[i]["debit"] = "0"
        if credit < 0:
            entries[i]["debit"] = str(round_currency(abs(credit) + to_decimal(entry.get("debit", "0"))))
            entries[i]["credit"] = "0"

    # Step 1: Double-Entry Balance
    total_debit = sum(to_decimal(e.get("debit", "0")) for e in entries)
    total_credit = sum(to_decimal(e.get("credit", "0")) for e in entries)
    if not amounts_equal(total_debit, total_credit):
        diff = total_debit - total_credit
        raise ValueError(
            f"GL Validation Step 1 Failed: GL entries do not balance: "
            f"total_debit={total_debit}, total_credit={total_credit}, difference={diff}"
        )

    # Step 2-12: Per-entry and cross-entry validations
    # Cache accounts to avoid repeated queries
    account_cache = {}

    for entry in entries:
        account_id = entry.get("account_id")
        if not account_id:
            raise ValueError(
                "GL Validation Step 2 Failed: Entry missing account_id"
            )

        # Fetch and cache account
        if account_id not in account_cache:
            account_cache[account_id] = _get_account(conn, account_id)
        account = account_cache[account_id]

        # Step 2: Account not group, not disabled
        if account.get("is_group", 0):
            raise ValueError(
                f"GL Validation Step 2 Failed: Account '{account['name']}' is a group account "
                f"-- cannot post to group accounts"
            )
        if account.get("disabled", 0):
            raise ValueError(
                f"GL Validation Step 2 Failed: Account '{account['name']}' is disabled"
            )

        # Step 3: Account-Company Affinity
        if account.get("company_id") != company_id:
            raise ValueError(
                f"GL Validation Step 3 Failed: Account '{account['name']}' belongs to "
                f"company {account.get('company_id')}, cannot use in posting for "
                f"company {company_id}"
            )

        # Step 4: Frozen Account Check
        if account.get("is_frozen", 0):
            company = conn.execute(
                "SELECT role_allowed_for_frozen_entries FROM company WHERE id = ?",
                (company_id,),
            ).fetchone()
            allowed_role = company["role_allowed_for_frozen_entries"] if company else None
            if not context_role or context_role != allowed_role:
                raise ValueError(
                    f"GL Validation Step 4 Failed: Account '{account['name']}' is frozen. "
                    f"Role '{allowed_role}' required to post to frozen accounts"
                )

        # Step 5: Party Mandatory for AR/AP
        acct_type = account.get("account_type", "")
        if acct_type == "receivable":
            if entry.get("party_type") != "customer" or not entry.get("party_id"):
                raise ValueError(
                    f"GL Validation Step 5 Failed: Receivable account '{account['name']}' "
                    f"requires party_type='customer' and valid party_id"
                )
        elif acct_type == "payable":
            if entry.get("party_type") not in ("supplier", "employee") or not entry.get("party_id"):
                raise ValueError(
                    f"GL Validation Step 5 Failed: Payable account '{account['name']}' "
                    f"requires party_type='supplier' or 'employee' and valid party_id"
                )

        # Step 6: P&L Accounts Require Cost Center
        root_type = account.get("root_type", "")
        if root_type in ("income", "expense"):
            if not entry.get("cost_center_id"):
                raise ValueError(
                    f"GL Validation Step 6 Failed: Income/Expense account '{account['name']}' "
                    f"requires a cost_center_id for P&L tracking"
                )

        # Step 7: Opening Entries Cannot Use P&L
        if is_opening and root_type in ("income", "expense"):
            raise ValueError(
                f"GL Validation Step 7 Failed: Opening entries cannot use P&L account "
                f"'{account['name']}' (root_type={root_type}). Use balance sheet accounts only"
            )

        # Step 8: Cost Center Validation
        cc_id = entry.get("cost_center_id")
        if cc_id:
            cc = conn.execute(
                "SELECT * FROM cost_center WHERE id = ?", (cc_id,)
            ).fetchone()
            if cc is None:
                raise ValueError(
                    f"GL Validation Step 8 Failed: Cost center {cc_id} does not exist"
                )
            if cc["is_group"]:
                raise ValueError(
                    f"GL Validation Step 8 Failed: Cost center '{cc['name']}' is a group "
                    f"-- cannot post to group cost centers"
                )
            if cc["company_id"] != company_id:
                raise ValueError(
                    f"GL Validation Step 8 Failed: Cost center '{cc['name']}' belongs to "
                    f"company {cc['company_id']}, expected {company_id}"
                )

    # Step 9: Fiscal Year Open
    fy = conn.execute(
        "SELECT * FROM fiscal_year WHERE start_date <= ? AND end_date >= ? AND is_closed = 0",
        (posting_date, posting_date),
    ).fetchone()
    if fy is None:
        # Check if fiscal year exists but is closed
        closed_fy = conn.execute(
            "SELECT * FROM fiscal_year WHERE start_date <= ? AND end_date >= ?",
            (posting_date, posting_date),
        ).fetchone()
        if closed_fy:
            raise ValueError(
                f"GL Validation Step 9 Failed: Fiscal year '{closed_fy['name']}' is closed "
                f"-- cannot post to closed fiscal years"
            )
        raise ValueError(
            f"GL Validation Step 9 Failed: No open fiscal year found for "
            f"posting date {posting_date}"
        )

    # Step 10: Freezing Date Check
    company_row = conn.execute(
        "SELECT accounts_frozen_till_date, role_allowed_for_frozen_entries "
        "FROM company WHERE id = ?",
        (company_id,),
    ).fetchone()
    if company_row and company_row["accounts_frozen_till_date"]:
        freeze_date = company_row["accounts_frozen_till_date"]
        if posting_date <= freeze_date:
            allowed_role = company_row["role_allowed_for_frozen_entries"]
            if not context_role or context_role != allowed_role:
                raise ValueError(
                    f"GL Validation Step 10 Failed: Accounts are frozen till {freeze_date}. "
                    f"Posting date {posting_date} is within the frozen period. "
                    f"Role '{allowed_role}' required"
                )

    # Step 11: Zero-Amount Rejection
    for entry in entries:
        debit = to_decimal(entry.get("debit", "0"))
        credit = to_decimal(entry.get("credit", "0"))
        if debit == 0 and credit == 0:
            acct_name = account_cache.get(entry["account_id"], {}).get("name", entry["account_id"])
            raise ValueError(
                f"GL Validation Step 11 Failed: GL entry line for account '{acct_name}' "
                f"has zero debit and zero credit -- no-op entries are not permitted"
            )

    # Step 12: Budget Check
    for entry in entries:
        cc_id = entry.get("cost_center_id")
        account_id = entry.get("account_id")
        debit = to_decimal(entry.get("debit", "0"))

        if not cc_id or debit == 0:
            continue

        budget = conn.execute(
            """
            SELECT budget_amount, action_if_exceeded FROM budget
            WHERE account_id = ?
              AND cost_center_id = ?
              AND fiscal_year_id = (
                  SELECT id FROM fiscal_year
                  WHERE start_date <= ? AND end_date >= ?
                  LIMIT 1
              )
            """,
            (account_id, cc_id, posting_date, posting_date),
        ).fetchone()

        if budget:
            budget_amount = to_decimal(budget["budget_amount"])
            # Sum current spend
            spent_row = conn.execute(
                """
                SELECT COALESCE(decimal_sum(debit), '0') as total
                FROM gl_entry
                WHERE account_id = ? AND cost_center_id = ?
                  AND is_cancelled = 0
                  AND posting_date >= (SELECT start_date FROM fiscal_year WHERE start_date <= ? AND end_date >= ?)
                  AND posting_date <= ?
                """,
                (account_id, cc_id, posting_date, posting_date, posting_date),
            ).fetchone()
            spent = to_decimal(str(spent_row["total"])) if spent_row else Decimal("0")
            total = spent + debit

            if total > budget_amount:
                acct_name = account_cache.get(account_id, {}).get("name", account_id)
                cc_name = cc_id
                cc_row = conn.execute("SELECT name FROM cost_center WHERE id = ?", (cc_id,)).fetchone()
                if cc_row:
                    cc_name = cc_row["name"]

                msg = (
                    f"Budget exceeded for account '{acct_name}', cost center '{cc_name}': "
                    f"budget={budget_amount}, spent={spent}, this_posting={debit}, "
                    f"would_be={total}"
                )
                if budget["action_if_exceeded"] == "stop":
                    raise ValueError(f"GL Validation Step 12 Failed: {msg}")
                elif budget["action_if_exceeded"] == "warn":
                    warnings.append(f"GL Validation Step 12 Warning: {msg}")

    return warnings


# --- Insert GL Entries ---

def insert_gl_entries(
    conn: sqlite3.Connection,
    entries: list[dict],
    voucher_type: str,
    voucher_id: str,
    posting_date: str,
    company_id: str,
    remarks: str = "",
    is_opening: bool = False,
    context_role: str | None = None,
    entry_set: str = "primary",
) -> list[str]:
    """Insert GL entries within the caller's transaction.

    MUST be called inside an existing transaction. Does NOT commit.

    Steps:
    1. Idempotency check — reject if entries already exist for this voucher+entry_set
    2. Normalize entries (negative auto-toggle)
    3. Run 12-step validation
    4. CWIP restriction check
    5. Insert gl_entry rows

    Args:
        entry_set: Distinguishes multiple GL entry sets for the same voucher.
            Use "primary" for the main GL (revenue/expense), "cogs" for
            Cost of Goods Sold entries. Allows composite GL postings where
            a single document needs multiple validated entry sets.

    Returns:
        List of generated gl_entry IDs (UUIDs).

    Raises:
        ValueError: If entries fail validation or already exist.
    """
    # 1. Idempotency check (voucher_type + voucher_id + entry_set)
    existing = conn.execute(
        "SELECT COUNT(*) as cnt FROM gl_entry "
        "WHERE voucher_type = ? AND voucher_id = ? AND entry_set = ? AND is_cancelled = 0",
        (voucher_type, voucher_id, entry_set),
    ).fetchone()
    if existing["cnt"] > 0:
        raise ValueError(
            f"GL entries already exist for voucher ({voucher_type}, {voucher_id}, entry_set={entry_set})"
        )

    # 2. Normalize entries
    entries = _normalize_entries(entries)

    # 3. Run 12-step validation
    _warnings = validate_gl_entries(
        conn, entries, company_id, posting_date,
        is_opening=is_opening,
        voucher_type=voucher_type,
        context_role=context_role,
    )

    # 4. CWIP restriction for journal entries
    if voucher_type == "journal_entry":
        for entry in entries:
            account = _get_account(conn, entry["account_id"])
            if account.get("account_type") == "capital_work_in_progress":
                raise ValueError(
                    f"Account '{account['name']}' is a Capital Work in Progress account. "
                    f"CWIP accounts cannot be used in manual Journal Entries. "
                    f"Use asset capitalization workflow instead."
                )

    # 4b. Auto-compute base amounts for multi-currency entries
    for entry in entries:
        rate = to_decimal(entry.get("exchange_rate", "1"))
        if rate <= 0:
            raise ValueError(
                "GL Validation Failed: exchange_rate must be > 0, "
                f"got {rate} for account {entry.get('account_id')}"
            )
        if rate != Decimal("1"):
            debit = to_decimal(entry.get("debit", "0"))
            credit = to_decimal(entry.get("credit", "0"))
            if "debit_base" not in entry:
                entry["debit_base"] = str(convert_to_base(debit, rate))
            if "credit_base" not in entry:
                entry["credit_base"] = str(convert_to_base(credit, rate))

    # 5. Insert gl_entry rows with chain checksums
    # Get the last checksum in this company's chain
    prev_hash_row = conn.execute(
        """SELECT gl_checksum FROM gl_entry ge
           JOIN account a ON ge.account_id = a.id
           WHERE a.company_id = ? AND ge.gl_checksum IS NOT NULL
           ORDER BY ge.created_at DESC, ge.rowid DESC LIMIT 1""",
        (company_id,),
    ).fetchone()
    prev_hash = prev_hash_row["gl_checksum"] if prev_hash_row else "GENESIS"

    generated_ids = []
    for entry in entries:
        entry_id = str(uuid.uuid4())
        generated_ids.append(entry_id)

        debit = entry.get("debit", "0")
        credit = entry.get("credit", "0")

        # Compute SHA-256 chain hash
        hash_input = "|".join([
            posting_date,
            entry["account_id"],
            str(debit),
            str(credit),
            voucher_type,
            voucher_id,
            prev_hash,
        ])
        checksum = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        conn.execute(
            """
            INSERT INTO gl_entry (
                id, posting_date, account_id, party_type, party_id,
                debit, credit, debit_base, credit_base,
                currency, exchange_rate,
                voucher_type, voucher_id, entry_set, cost_center_id, project_id,
                remarks, fiscal_year, is_cancelled, gl_checksum, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, datetime('now'))
            """,
            (
                entry_id,
                posting_date,
                entry["account_id"],
                entry.get("party_type"),
                entry.get("party_id"),
                debit,
                credit,
                entry.get("debit_base", debit),
                entry.get("credit_base", credit),
                entry.get("currency", "USD"),
                entry.get("exchange_rate", "1"),
                voucher_type,
                voucher_id,
                entry_set,
                entry.get("cost_center_id"),
                entry.get("project_id"),
                remarks,
                entry.get("fiscal_year"),
                checksum,
            ),
        )

        prev_hash = checksum  # Chain: next entry references this one

    return generated_ids


# --- Reverse GL Entries ---

def reverse_gl_entries(
    conn: sqlite3.Connection,
    voucher_type: str,
    voucher_id: str,
    posting_date: str,
) -> list[str]:
    """Create reversing entries for cancellation.

    Finds all gl_entry rows for the voucher where is_cancelled=0.
    Creates mirror entries (debit<->credit swapped).
    Sets is_cancelled=1 on originals.

    Does NOT commit — caller manages transaction.

    Returns:
        List of new reversal gl_entry IDs.

    Raises:
        ValueError: If no entries found or already cancelled.
    """
    originals = conn.execute(
        "SELECT * FROM gl_entry WHERE voucher_type = ? AND voucher_id = ? AND is_cancelled = 0",
        (voucher_type, voucher_id),
    ).fetchall()

    if not originals:
        raise ValueError(
            f"No active GL entries found for voucher ({voucher_type}, {voucher_id})"
        )

    reversal_ids = []

    for orig in originals:
        reversal_id = str(uuid.uuid4())
        reversal_ids.append(reversal_id)

        # Insert mirror entry (debit <-> credit swapped)
        conn.execute(
            """
            INSERT INTO gl_entry (
                id, posting_date, account_id, party_type, party_id,
                debit, credit, debit_base, credit_base,
                currency, exchange_rate,
                voucher_type, voucher_id, entry_set, cost_center_id, project_id,
                remarks, fiscal_year, is_cancelled, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, datetime('now'))
            """,
            (
                reversal_id,
                posting_date,
                orig["account_id"],
                orig["party_type"],
                orig["party_id"],
                orig["credit"],       # swap: original credit becomes reversal debit
                orig["debit"],        # swap: original debit becomes reversal credit
                orig["credit_base"],  # swap base amounts too
                orig["debit_base"],
                orig["currency"],
                orig["exchange_rate"],
                voucher_type,
                voucher_id,
                orig["entry_set"],  # preserve entry_set from original
                orig["cost_center_id"],
                orig["project_id"],
                f"Reversal of {orig['id']}",
                orig["fiscal_year"],
            ),
        )

        # Mark original as cancelled
        conn.execute(
            "UPDATE gl_entry SET is_cancelled = 1 WHERE id = ?",
            (orig["id"],),
        )

    return reversal_ids


# --- Multi-Currency Helpers ---

def prepare_multicurrency_entries(entries, currency, exchange_rate):
    """Set currency/exchange_rate on GL entries and compute base amounts.

    Convenience function for skills to prepare entries before insert_gl_entries.
    Modifies entries in-place and returns them.

    Args:
        entries: List of GL entry dicts
        currency: Transaction currency code (e.g. 'EUR')
        exchange_rate: Decimal or str rate (1 txn unit = X base units)

    Returns:
        Modified entries list with currency, exchange_rate, debit_base, credit_base set.
    """
    rate = to_decimal(str(exchange_rate)) if not isinstance(exchange_rate, Decimal) else exchange_rate
    for entry in entries:
        entry["currency"] = currency
        entry["exchange_rate"] = str(rate)
        debit = to_decimal(entry.get("debit", "0"))
        credit = to_decimal(entry.get("credit", "0"))
        entry["debit_base"] = str(convert_to_base(debit, rate))
        entry["credit_base"] = str(convert_to_base(credit, rate))
    return entries


# --- Query: Account Balance ---

def get_account_balance(
    conn: sqlite3.Connection,
    account_id: str,
    as_of_date: Optional[str] = None,
) -> dict:
    """Get the balance of an account.

    Args:
        conn: SQLite connection.
        account_id: The account to query.
        as_of_date: Optional cutoff date (inclusive). None = all time.

    Returns:
        {"debit_total": str, "credit_total": str, "balance": str}
        Balance = debit_total - credit_total (positive = debit balance).
    """
    if as_of_date:
        row = conn.execute(
            """
            SELECT
                COALESCE(decimal_sum(debit), '0') as debit_total,
                COALESCE(decimal_sum(credit), '0') as credit_total
            FROM gl_entry
            WHERE account_id = ? AND is_cancelled = 0 AND posting_date <= ?
            """,
            (account_id, as_of_date),
        ).fetchone()
    else:
        row = conn.execute(
            """
            SELECT
                COALESCE(decimal_sum(debit), '0') as debit_total,
                COALESCE(decimal_sum(credit), '0') as credit_total
            FROM gl_entry
            WHERE account_id = ? AND is_cancelled = 0
            """,
            (account_id,),
        ).fetchone()

    debit_total = to_decimal(str(row["debit_total"]))
    credit_total = to_decimal(str(row["credit_total"]))
    balance = debit_total - credit_total

    return {
        "debit_total": str(round_currency(debit_total)),
        "credit_total": str(round_currency(credit_total)),
        "balance": str(round_currency(balance)),
    }
