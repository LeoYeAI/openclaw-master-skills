#!/usr/bin/env python3
"""ERPClaw Journals Skill — db_query.py

Journal entry CRUD with draft→submit→cancel lifecycle.
On submit, posts balanced GL entries via shared lib.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.gl_posting import (
        validate_gl_entries,
        insert_gl_entries,
        reverse_gl_entries,
    )
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query_helpers import resolve_company_id
    from erpclaw_lib.query import Q, P, Table, Field, fn, Order
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company", "account"]

# PyPika table aliases
_t_je = Table("journal_entry")
_t_jel = Table("journal_entry_line")
_t_account = Table("account")
_t_company = Table("company")
_t_cost_center = Table("cost_center")
_t_rjt = Table("recurring_journal_template")

VALID_ENTRY_TYPES = (
    "journal", "opening", "closing", "depreciation",
    "write_off", "exchange_rate_revaluation",
    "inter_company", "credit_note", "debit_note",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_lines(lines: list[dict]) -> tuple[Decimal, Decimal]:
    """Validate journal entry lines. Returns (total_debit, total_credit).

    Raises ValueError on validation failure.
    """
    if len(lines) < 2:
        raise ValueError("At least 2 lines are required")

    total_debit = Decimal("0")
    total_credit = Decimal("0")

    for i, line in enumerate(lines):
        if "account_id" not in line or not line["account_id"]:
            raise ValueError(f"Line {i+1}: account_id is required")

        debit = to_decimal(line.get("debit", "0"))
        credit = to_decimal(line.get("credit", "0"))

        if debit < 0 or credit < 0:
            raise ValueError(f"Line {i+1}: debit and credit must be >= 0")

        if debit > 0 and credit > 0:
            raise ValueError(f"Line {i+1}: cannot have both debit and credit > 0")

        if debit == 0 and credit == 0:
            raise ValueError(f"Line {i+1}: either debit or credit must be > 0")

        total_debit += debit
        total_credit += credit

    total_debit = round_currency(total_debit)
    total_credit = round_currency(total_credit)

    if total_debit != total_credit:
        raise ValueError(
            f"Total debit ({total_debit}) must equal total credit ({total_credit})"
        )

    return total_debit, total_credit


def _insert_lines(conn, journal_entry_id: str, lines: list[dict]):
    """Insert journal_entry_line rows."""
    for line in lines:
        line_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO journal_entry_line
               (id, journal_entry_id, account_id, party_type, party_id,
                debit, credit, cost_center_id, project_id, remark)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (line_id, journal_entry_id,
             line["account_id"],
             line.get("party_type"),
             line.get("party_id"),
             str(round_currency(to_decimal(line.get("debit", "0")))),
             str(round_currency(to_decimal(line.get("credit", "0")))),
             line.get("cost_center_id"),
             line.get("project_id"),
             line.get("remark")),
        )


def _get_je_or_err(conn, journal_entry_id: str) -> dict:
    """Fetch a journal entry by ID. Calls err() if not found."""
    q = Q.from_(_t_je).select(_t_je.star).where(_t_je.id == P())
    row = conn.execute(q.get_sql(), (journal_entry_id,)).fetchone()
    if not row:
        err(f"Journal entry {journal_entry_id} not found")
    return row_to_dict(row)


def _get_je_lines(conn, journal_entry_id: str) -> list[dict]:
    """Fetch journal entry lines with account name join."""
    jel = Table("journal_entry_line")
    a = Table("account")
    q = (Q.from_(jel)
         .select(jel.star, a.name.as_("account_name"))
         .join(a).on(a.id == jel.account_id)
         .where(jel.journal_entry_id == P())
         .orderby(jel.rowid))
    rows = conn.execute(q.get_sql(), (journal_entry_id,)).fetchall()
    return [row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# 1. add-journal-entry
# ---------------------------------------------------------------------------

def add_journal_entry(conn, args):
    """Create a new draft journal entry with lines."""
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")
    posting_date = args.posting_date
    if not posting_date:
        err("--posting-date is required")
    entry_type = args.entry_type or "journal"
    if entry_type not in VALID_ENTRY_TYPES:
        err(f"Invalid entry type '{entry_type}'. Valid: {VALID_ENTRY_TYPES}")

    # Validate company exists
    q = Q.from_(_t_company).select(_t_company.id).where(_t_company.id == P())
    company = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not company:
        err(f"Company {company_id} not found")

    # Parse lines
    lines_json = args.lines
    if not lines_json:
        err("--lines is required (JSON array)")
    try:
        lines = json.loads(lines_json) if isinstance(lines_json, str) else lines_json
    except json.JSONDecodeError as e:
        err("Invalid JSON format in --lines")

    # Validate lines
    try:
        total_debit, total_credit = _validate_lines(lines)
    except ValueError as e:
        err(str(e))

    # Validate all account_ids exist
    q_acct = Q.from_(_t_account).select(_t_account.id, _t_account.is_frozen).where(_t_account.id == P())
    for i, line in enumerate(lines):
        acct = conn.execute(q_acct.get_sql(), (line["account_id"],)).fetchone()
        if not acct:
            err(f"Line {i+1}: account {line['account_id']} not found")

    je_id = str(uuid.uuid4())
    naming = get_next_name(conn, "journal_entry", company_id=company_id)

    conn.execute(
        """INSERT INTO journal_entry
           (id, naming_series, posting_date, entry_type, total_debit, total_credit,
            remark, status, company_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?)""",
        (je_id, naming, posting_date, entry_type,
         str(total_debit), str(total_credit),
         args.remark, company_id),
    )

    _insert_lines(conn, je_id, lines)

    audit(conn, "erpclaw-journals", "add-journal-entry", "journal_entry", je_id,
           new_values={"naming_series": naming, "entry_type": entry_type,
                       "posting_date": posting_date, "lines": len(lines)})
    conn.commit()

    ok({"status": "created", "journal_entry_id": je_id,
         "naming_series": naming})


# ---------------------------------------------------------------------------
# 2. update-journal-entry
# ---------------------------------------------------------------------------

def update_journal_entry(conn, args):
    """Update a draft journal entry. Only drafts can be updated."""
    je_id = args.journal_entry_id
    if not je_id:
        err("--journal-entry-id is required")

    je = _get_je_or_err(conn, je_id)
    if je["status"] != "draft":
        err(f"Cannot update: journal entry is '{je['status']}' (must be 'draft')",
             suggestion="Cancel the document first, then make changes.")

    updated_fields = []
    old_values = {}

    # Update posting_date
    if args.posting_date:
        old_values["posting_date"] = je["posting_date"]
        conn.execute("UPDATE journal_entry SET posting_date = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.posting_date, je_id))
        updated_fields.append("posting_date")

    # Update entry_type
    if args.entry_type:
        if args.entry_type not in VALID_ENTRY_TYPES:
            err(f"Invalid entry type '{args.entry_type}'. Valid: {VALID_ENTRY_TYPES}")
        old_values["entry_type"] = je["entry_type"]
        conn.execute("UPDATE journal_entry SET entry_type = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.entry_type, je_id))
        updated_fields.append("entry_type")

    # Update remark
    if args.remark is not None:
        old_values["remark"] = je["remark"]
        conn.execute("UPDATE journal_entry SET remark = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.remark, je_id))
        updated_fields.append("remark")

    # Replace lines if provided
    if args.lines:
        try:
            lines = json.loads(args.lines) if isinstance(args.lines, str) else args.lines
        except json.JSONDecodeError as e:
            err("Invalid JSON format in --lines")

        try:
            total_debit, total_credit = _validate_lines(lines)
        except ValueError as e:
            err(str(e))

        # Validate all account_ids exist
        q_acct = Q.from_(_t_account).select(_t_account.id).where(_t_account.id == P())
        for i, line in enumerate(lines):
            acct = conn.execute(q_acct.get_sql(), (line["account_id"],)).fetchone()
            if not acct:
                err(f"Line {i+1}: account {line['account_id']} not found")

        # Delete old lines, insert new
        q_del = Q.from_(_t_jel).delete().where(_t_jel.journal_entry_id == P())
        conn.execute(q_del.get_sql(), (je_id,))
        _insert_lines(conn, je_id, lines)

        conn.execute(
            """UPDATE journal_entry SET total_debit = ?, total_credit = ?,
               updated_at = datetime('now') WHERE id = ?""",
            (str(total_debit), str(total_credit), je_id),
        )
        updated_fields.append("lines")

    if not updated_fields:
        err("No fields to update")

    audit(conn, "erpclaw-journals", "update-journal-entry", "journal_entry", je_id,
           old_values=old_values,
           new_values={"updated_fields": updated_fields})
    conn.commit()

    ok({"status": "updated", "journal_entry_id": je_id,
         "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 3. get-journal-entry
# ---------------------------------------------------------------------------

def get_journal_entry(conn, args):
    """Get a journal entry with all its lines."""
    je_id = args.journal_entry_id
    if not je_id:
        err("--journal-entry-id is required")

    je = _get_je_or_err(conn, je_id)
    lines = _get_je_lines(conn, je_id)

    # Format lines for output
    formatted_lines = []
    for line in lines:
        formatted_lines.append({
            "id": line["id"],
            "account_id": line["account_id"],
            "account_name": line["account_name"],
            "debit": line["debit"],
            "credit": line["credit"],
            "party_type": line.get("party_type"),
            "party_id": line.get("party_id"),
            "cost_center_id": line.get("cost_center_id"),
            "project_id": line.get("project_id"),
            "remark": line.get("remark"),
        })

    ok({
        "id": je["id"],
        "naming_series": je["naming_series"],
        "posting_date": je["posting_date"],
        "entry_type": je["entry_type"],
        "status": je["status"],
        "total_debit": je["total_debit"],
        "total_credit": je["total_credit"],
        "remark": je.get("remark"),
        "amended_from": je.get("amended_from"),
        "company_id": je["company_id"],
        "lines": formatted_lines,
    })


# ---------------------------------------------------------------------------
# 4. list-journal-entries
# ---------------------------------------------------------------------------

def list_journal_entries(conn, args):
    """List journal entries with filtering."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    je = Table("journal_entry")
    params = [company_id]

    # Build base query with required company filter
    base = Q.from_(je).where(je.company_id == P())

    if args.je_status:
        base = base.where(je.status == P())
        params.append(args.je_status)

    if args.entry_type:
        base = base.where(je.entry_type == P())
        params.append(args.entry_type)

    if args.from_date:
        base = base.where(je.posting_date >= P())
        params.append(args.from_date)

    if args.to_date:
        base = base.where(je.posting_date <= P())
        params.append(args.to_date)

    if args.account_id:
        # Subquery: keep as raw SQL snippet via Criterion.any for clarity
        jel = Table("journal_entry_line")
        sub = Q.from_(jel).select(jel.journal_entry_id).where(jel.account_id == P())
        base = base.where(je.id.isin(sub))
        params.append(args.account_id)

    # Total count
    q_count = base.select(fn.Count("*"))
    count_row = conn.execute(q_count.get_sql(), params).fetchone()
    total_count = count_row[0]

    # Paginated results
    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0
    list_params = params + [limit, offset]

    q_list = (base.select(
                  je.id, je.naming_series, je.posting_date, je.entry_type,
                  je.status, je.total_debit, je.total_credit, je.remark)
              .orderby(je.posting_date, order=Order.desc)
              .orderby(je.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(q_list.get_sql(), list_params).fetchall()

    entries = [row_to_dict(r) for r in rows]
    ok({"entries": entries, "total_count": total_count,
         "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 5. submit-journal-entry
# ---------------------------------------------------------------------------

def submit_journal_entry(conn, args):
    """Submit a draft JE: re-validate, post GL entries, update status."""
    je_id = args.journal_entry_id
    if not je_id:
        err("--journal-entry-id is required")

    je = _get_je_or_err(conn, je_id)
    if je["status"] != "draft":
        err(f"Cannot submit: journal entry is '{je['status']}' (must be 'draft')")

    lines = _get_je_lines(conn, je_id)

    # Re-validate lines (they were validated at creation but re-check)
    try:
        _validate_lines([{
            "account_id": l["account_id"],
            "debit": l["debit"],
            "credit": l["credit"],
        } for l in lines])
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-journals] {e}\n")
        err("Validation failed at submit")

    # Build GL entries from lines
    gl_entries = []
    for line in lines:
        gl_entries.append({
            "account_id": line["account_id"],
            "debit": line["debit"],
            "credit": line["credit"],
            "party_type": line.get("party_type"),
            "party_id": line.get("party_id"),
            "cost_center_id": line.get("cost_center_id"),
        })

    # Single transaction: validate GL, insert GL entries, update JE status
    try:
        is_opening = je["entry_type"] in ("opening",)
        validate_gl_entries(
            conn, gl_entries, je["company_id"],
            je["posting_date"], is_opening=is_opening,
            voucher_type="journal_entry",
        )
        gl_ids = insert_gl_entries(
            conn, gl_entries,
            voucher_type="journal_entry",
            voucher_id=je_id,
            posting_date=je["posting_date"],
            company_id=je["company_id"],
            remarks=je.get("remark") or "",
            is_opening=is_opening,
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-journals] {e}\n")
        err(f"GL posting failed: {e}")

    conn.execute(
        """UPDATE journal_entry SET status = 'submitted',
           updated_at = datetime('now') WHERE id = ?""",
        (je_id,),
    )

    audit(conn, "erpclaw-journals", "submit-journal-entry", "journal_entry", je_id,
           new_values={"gl_entries_created": len(gl_ids)})
    conn.commit()

    ok({"status": "submitted", "journal_entry_id": je_id,
         "gl_entries_created": len(gl_ids)})


# ---------------------------------------------------------------------------
# 6. cancel-journal-entry
# ---------------------------------------------------------------------------

def cancel_journal_entry(conn, args):
    """Cancel a submitted JE: reverse GL entries, update status."""
    je_id = args.journal_entry_id
    if not je_id:
        err("--journal-entry-id is required")

    je = _get_je_or_err(conn, je_id)
    if je["status"] != "submitted":
        err(f"Cannot cancel: journal entry is '{je['status']}' (must be 'submitted')")

    # Single transaction: reverse GL entries + update status
    try:
        reversal_ids = reverse_gl_entries(
            conn,
            voucher_type="journal_entry",
            voucher_id=je_id,
            posting_date=je["posting_date"],
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-journals] {e}\n")
        err(f"GL reversal failed: {e}")

    conn.execute(
        """UPDATE journal_entry SET status = 'cancelled',
           updated_at = datetime('now') WHERE id = ?""",
        (je_id,),
    )

    audit(conn, "erpclaw-journals", "cancel-journal-entry", "journal_entry", je_id,
           new_values={"reversed_gl_entries": len(reversal_ids)})
    conn.commit()

    ok({"status": "cancelled", "journal_entry_id": je_id, "reversed": True})


# ---------------------------------------------------------------------------
# 7. amend-journal-entry
# ---------------------------------------------------------------------------

def amend_journal_entry(conn, args):
    """Amend a submitted JE: cancel old, create new linked draft."""
    je_id = args.journal_entry_id
    if not je_id:
        err("--journal-entry-id is required")

    je = _get_je_or_err(conn, je_id)
    if je["status"] != "submitted":
        err(f"Cannot amend: journal entry is '{je['status']}' (must be 'submitted')")

    # Cancel the old JE (reverse GL entries)
    try:
        reverse_gl_entries(
            conn,
            voucher_type="journal_entry",
            voucher_id=je_id,
            posting_date=je["posting_date"],
        )
    except ValueError as e:
        sys.stderr.write(f"[erpclaw-journals] {e}\n")
        err(f"GL reversal failed: {e}")

    conn.execute(
        """UPDATE journal_entry SET status = 'amended',
           updated_at = datetime('now') WHERE id = ?""",
        (je_id,),
    )

    # Determine lines for new JE
    if args.lines:
        try:
            new_lines = json.loads(args.lines) if isinstance(args.lines, str) else args.lines
        except json.JSONDecodeError as e:
            err("Invalid JSON format in --lines")
    else:
        # Copy lines from original
        q_lines = Q.from_(_t_jel).select(_t_jel.star).where(_t_jel.journal_entry_id == P())
        old_lines = conn.execute(q_lines.get_sql(), (je_id,)).fetchall()
        new_lines = []
        for ol in old_lines:
            old_dict = row_to_dict(ol)
            new_lines.append({
                "account_id": old_dict["account_id"],
                "debit": old_dict["debit"],
                "credit": old_dict["credit"],
                "party_type": old_dict.get("party_type"),
                "party_id": old_dict.get("party_id"),
                "cost_center_id": old_dict.get("cost_center_id"),
                "project_id": old_dict.get("project_id"),
                "remark": old_dict.get("remark"),
            })

    # Validate lines
    try:
        total_debit, total_credit = _validate_lines(new_lines)
    except ValueError as e:
        err(str(e))

    # Create new draft JE
    new_je_id = str(uuid.uuid4())
    new_posting_date = args.posting_date or je["posting_date"]
    naming = get_next_name(conn, "journal_entry", company_id=je["company_id"])

    conn.execute(
        """INSERT INTO journal_entry
           (id, naming_series, posting_date, entry_type, total_debit, total_credit,
            remark, status, amended_from, company_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)""",
        (new_je_id, naming, new_posting_date, je["entry_type"],
         str(total_debit), str(total_credit),
         args.remark if args.remark is not None else je.get("remark"),
         je_id, je["company_id"]),
    )

    _insert_lines(conn, new_je_id, new_lines)

    audit(conn, "erpclaw-journals", "amend-journal-entry", "journal_entry", je_id,
           new_values={"new_journal_entry_id": new_je_id, "new_naming_series": naming})
    conn.commit()

    ok({"status": "created", "original_id": je_id,
         "new_journal_entry_id": new_je_id,
         "new_naming_series": naming})


# ---------------------------------------------------------------------------
# 8. delete-journal-entry
# ---------------------------------------------------------------------------

def delete_journal_entry(conn, args):
    """Delete a draft JE. Only drafts can be deleted."""
    je_id = args.journal_entry_id
    if not je_id:
        err("--journal-entry-id is required")

    je = _get_je_or_err(conn, je_id)
    if je["status"] != "draft":
        err(f"Cannot delete: journal entry is '{je['status']}' (only 'draft' can be deleted)",
             suggestion="Cancel the document first, then delete.")

    naming = je["naming_series"]

    # Delete lines first (FK constraint), then header
    q_del_lines = Q.from_(_t_jel).delete().where(_t_jel.journal_entry_id == P())
    conn.execute(q_del_lines.get_sql(), (je_id,))
    q_del_je = Q.from_(_t_je).delete().where(_t_je.id == P())
    conn.execute(q_del_je.get_sql(), (je_id,))

    audit(conn, "erpclaw-journals", "delete-journal-entry", "journal_entry", je_id,
           old_values={"naming_series": naming})
    conn.commit()

    ok({"status": "deleted", "deleted": True})


# ---------------------------------------------------------------------------
# 9. duplicate-journal-entry
# ---------------------------------------------------------------------------

def duplicate_journal_entry(conn, args):
    """Duplicate a JE as a new draft. Copies all lines."""
    je_id = args.journal_entry_id
    if not je_id:
        err("--journal-entry-id is required")

    je = _get_je_or_err(conn, je_id)
    q_lines = Q.from_(_t_jel).select(_t_jel.star).where(_t_jel.journal_entry_id == P())
    old_lines = conn.execute(q_lines.get_sql(), (je_id,)).fetchall()

    new_lines = []
    for ol in old_lines:
        old_dict = row_to_dict(ol)
        new_lines.append({
            "account_id": old_dict["account_id"],
            "debit": old_dict["debit"],
            "credit": old_dict["credit"],
            "party_type": old_dict.get("party_type"),
            "party_id": old_dict.get("party_id"),
            "cost_center_id": old_dict.get("cost_center_id"),
            "project_id": old_dict.get("project_id"),
            "remark": old_dict.get("remark"),
        })

    # Validate lines (should always pass since source was valid)
    try:
        total_debit, total_credit = _validate_lines(new_lines)
    except ValueError as e:
        err(str(e))

    new_je_id = str(uuid.uuid4())
    posting_date = args.posting_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    naming = get_next_name(conn, "journal_entry", company_id=je["company_id"])

    conn.execute(
        """INSERT INTO journal_entry
           (id, naming_series, posting_date, entry_type, total_debit, total_credit,
            remark, status, company_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?)""",
        (new_je_id, naming, posting_date, je["entry_type"],
         str(total_debit), str(total_credit),
         je.get("remark"), je["company_id"]),
    )

    _insert_lines(conn, new_je_id, new_lines)

    audit(conn, "erpclaw-journals", "duplicate-journal-entry", "journal_entry", je_id,
           new_values={"new_journal_entry_id": new_je_id, "naming_series": naming})
    conn.commit()

    ok({"status": "created", "new_journal_entry_id": new_je_id,
         "naming_series": naming})


# ---------------------------------------------------------------------------
# 10. create-intercompany-je
# ---------------------------------------------------------------------------

def _ensure_intercompany_account(conn, company_id, name, root_type, account_type):
    """Find or create an intercompany account for a company."""
    q = (Q.from_(_t_account).select(_t_account.id)
         .where(_t_account.name == P())
         .where(_t_account.company_id == P()))
    acct = conn.execute(q.get_sql(), (name, company_id)).fetchone()
    if acct:
        return acct["id"]

    acct_id = str(uuid.uuid4())
    balance_dir = "debit_normal" if root_type == "asset" else "credit_normal"
    conn.execute(
        """INSERT INTO account (id, name, root_type, account_type, currency,
           is_group, balance_direction, company_id, depth)
           VALUES (?, ?, ?, ?, 'USD', 0, ?, ?, 0)""",
        (acct_id, name, root_type, account_type, balance_dir, company_id),
    )
    return acct_id


def create_intercompany_je(conn, args):
    """Create paired intercompany journal entries between two companies.

    Source company: DR Intercompany Receivable / CR Revenue (or specified account)
    Target company: DR Expense (or specified account) / CR Intercompany Payable
    Both JEs reference each other via remark field.
    """
    source_company_id = args.source_company_id
    target_company_id = args.target_company_id
    amount_str = args.amount
    description = args.description or "Intercompany transaction"
    posting_date = args.posting_date

    if not source_company_id:
        err("--source-company-id is required")
    if not target_company_id:
        err("--target-company-id is required")
    if not amount_str:
        err("--amount is required")
    if not posting_date:
        err("--posting-date is required")
    if source_company_id == target_company_id:
        err("Source and target company must be different")

    amount = to_decimal(amount_str)
    if amount <= 0:
        err("Amount must be positive")

    # Validate both companies exist and share the same currency
    q_co = Q.from_(_t_company).select(_t_company.id, _t_company.default_currency).where(_t_company.id == P())
    src_co = conn.execute(q_co.get_sql(), (source_company_id,)).fetchone()
    tgt_co = conn.execute(q_co.get_sql(), (target_company_id,)).fetchone()
    if not src_co:
        err(f"Source company {source_company_id} not found")
    if not tgt_co:
        err(f"Target company {target_company_id} not found")
    if src_co["default_currency"] != tgt_co["default_currency"]:
        err("Intercompany JE between different currencies is not supported (v2)")

    # Ensure intercompany accounts exist in both companies
    src_ic_recv = _ensure_intercompany_account(
        conn, source_company_id, "Intercompany Receivable", "asset", "receivable")
    q_rev = (Q.from_(_t_account).select(_t_account.id)
             .where(_t_account.account_type == "revenue")
             .where(_t_account.company_id == P())
             .where(_t_account.is_group == 0)
             .limit(1))
    src_revenue = conn.execute(q_rev.get_sql(), (source_company_id,)).fetchone()
    if not src_revenue:
        err("Source company has no revenue account")

    tgt_ic_pay = _ensure_intercompany_account(
        conn, target_company_id, "Intercompany Payable", "liability", "payable")
    q_exp = (Q.from_(_t_account).select(_t_account.id)
             .where(_t_account.account_type.isin(["expense", "cost_of_goods_sold"]))
             .where(_t_account.company_id == P())
             .where(_t_account.is_group == 0)
             .limit(1))
    tgt_expense = conn.execute(q_exp.get_sql(), (target_company_id,)).fetchone()
    if not tgt_expense:
        err("Target company has no expense account")

    # Get cost centers for P&L entries
    q_cc = (Q.from_(_t_cost_center).select(_t_cost_center.id)
            .where(_t_cost_center.company_id == P())
            .where(_t_cost_center.is_group == 0)
            .limit(1))
    src_cc = conn.execute(q_cc.get_sql(), (source_company_id,)).fetchone()
    tgt_cc = conn.execute(q_cc.get_sql(), (target_company_id,)).fetchone()

    amt = str(round_currency(amount))

    # Create Source JE: DR Intercompany Receivable / CR Revenue
    src_je_id = str(uuid.uuid4())
    src_naming = get_next_name(conn, "journal_entry", company_id=source_company_id)
    conn.execute(
        """INSERT INTO journal_entry
           (id, naming_series, posting_date, entry_type, total_debit, total_credit,
            remark, status, company_id)
           VALUES (?, ?, ?, 'inter_company', ?, ?, ?, 'draft', ?)""",
        (src_je_id, src_naming, posting_date, amt, amt, description, source_company_id),
    )
    # Source lines
    for line_data in [
        {"account_id": src_ic_recv, "debit": amt, "credit": "0"},
        {"account_id": src_revenue["id"], "debit": "0", "credit": amt,
         "cost_center_id": src_cc["id"] if src_cc else None},
    ]:
        line_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO journal_entry_line
               (id, journal_entry_id, account_id, debit, credit, cost_center_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (line_id, src_je_id, line_data["account_id"],
             line_data["debit"], line_data["credit"],
             line_data.get("cost_center_id")),
        )

    # Create Target JE: DR Expense / CR Intercompany Payable
    tgt_je_id = str(uuid.uuid4())
    tgt_naming = get_next_name(conn, "journal_entry", company_id=target_company_id)
    conn.execute(
        """INSERT INTO journal_entry
           (id, naming_series, posting_date, entry_type, total_debit, total_credit,
            remark, status, company_id)
           VALUES (?, ?, ?, 'inter_company', ?, ?, ?, 'draft', ?)""",
        (tgt_je_id, tgt_naming, posting_date, amt, amt, description, target_company_id),
    )
    # Target lines
    for line_data in [
        {"account_id": tgt_expense["id"], "debit": amt, "credit": "0",
         "cost_center_id": tgt_cc["id"] if tgt_cc else None},
        {"account_id": tgt_ic_pay, "debit": "0", "credit": amt},
    ]:
        line_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO journal_entry_line
               (id, journal_entry_id, account_id, debit, credit, cost_center_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (line_id, tgt_je_id, line_data["account_id"],
             line_data["debit"], line_data["credit"],
             line_data.get("cost_center_id")),
        )

    # Store cross-references in remark
    conn.execute(
        "UPDATE journal_entry SET remark = ? WHERE id = ?",
        (f"{description} | Paired with {tgt_naming} ({target_company_id})", src_je_id),
    )
    conn.execute(
        "UPDATE journal_entry SET remark = ? WHERE id = ?",
        (f"{description} | Paired with {src_naming} ({source_company_id})", tgt_je_id),
    )

    audit(conn, "erpclaw-journals", "create-intercompany-je", "journal_entry", src_je_id,
           new_values={"target_je_id": tgt_je_id, "amount": amt})
    conn.commit()

    ok({
        "source_je_id": src_je_id, "source_naming": src_naming,
        "target_je_id": tgt_je_id, "target_naming": tgt_naming,
        "amount": amt,
        "description": description,
    })


# ---------------------------------------------------------------------------
# Recurring Journal Template helpers
# ---------------------------------------------------------------------------

def _advance_date(d: date, frequency: str) -> date:
    """Advance a date by one period based on frequency.

    Uses stdlib only (no dateutil). Handles month-end edge cases.
    """
    if frequency == "daily":
        return d + timedelta(days=1)
    elif frequency == "weekly":
        return d + timedelta(weeks=1)
    elif frequency == "monthly":
        month = d.month + 1
        year = d.year
        if month > 12:
            month = 1
            year += 1
        # Clamp day to month's max (e.g. Jan 31 → Feb 28)
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(d.day, max_day)
        return date(year, month, day)
    elif frequency == "quarterly":
        month = d.month + 3
        year = d.year
        while month > 12:
            month -= 12
            year += 1
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(d.day, max_day)
        return date(year, month, day)
    elif frequency == "annual":
        import calendar
        year = d.year + 1
        max_day = calendar.monthrange(year, d.month)[1]
        day = min(d.day, max_day)
        return date(year, d.month, day)
    else:
        raise ValueError(f"Unknown frequency: {frequency}")


VALID_FREQUENCIES = ("daily", "weekly", "monthly", "quarterly", "annual")


# ---------------------------------------------------------------------------
# 11. add-recurring-template
# ---------------------------------------------------------------------------

def add_recurring_template(conn, args):
    """Create a recurring journal template."""
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")
    template_name = args.template_name
    if not template_name:
        err("--template-name is required")
    frequency = args.frequency or "monthly"
    if frequency not in VALID_FREQUENCIES:
        err(f"Invalid frequency '{frequency}'. Valid: {VALID_FREQUENCIES}")
    start_date = args.start_date
    if not start_date:
        err("--start-date is required")
    end_date = args.end_date  # optional

    entry_type = args.entry_type or "journal"
    if entry_type not in VALID_ENTRY_TYPES:
        err(f"Invalid entry type '{entry_type}'. Valid: {VALID_ENTRY_TYPES}")

    auto_submit = 1 if args.auto_submit else 0

    # Validate company
    q = Q.from_(_t_company).select(_t_company.id).where(_t_company.id == P())
    company = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not company:
        err(f"Company {company_id} not found")

    # Parse and validate lines
    lines_json = args.lines
    if not lines_json:
        err("--lines is required (JSON array)")
    try:
        lines = json.loads(lines_json) if isinstance(lines_json, str) else lines_json
    except json.JSONDecodeError:
        err("Invalid JSON format in --lines")

    try:
        _validate_lines(lines)
    except ValueError as e:
        err(str(e))

    # Validate accounts exist
    q_acct = Q.from_(_t_account).select(_t_account.id).where(_t_account.id == P())
    for i, line in enumerate(lines):
        acct = conn.execute(q_acct.get_sql(), (line["account_id"],)).fetchone()
        if not acct:
            err(f"Line {i+1}: account {line['account_id']} not found")

    template_id = str(uuid.uuid4())
    naming = get_next_name(conn, "recurring_journal_template", company_id=company_id)

    conn.execute(
        """INSERT INTO recurring_journal_template
           (id, naming_series, company_id, name, frequency, start_date, end_date,
            next_run_date, entry_type, lines, auto_submit, remark, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
        (template_id, naming, company_id, template_name, frequency,
         start_date, end_date, start_date, entry_type,
         json.dumps(lines) if isinstance(lines, list) else lines_json,
         auto_submit, args.remark),
    )

    audit(conn, "erpclaw-journals", "add-recurring-template",
          "recurring_journal_template", template_id,
          new_values={"name": template_name, "frequency": frequency})
    conn.commit()

    ok({"status": "created", "template_id": template_id,
        "naming_series": naming, "next_run_date": start_date})


# ---------------------------------------------------------------------------
# 12. update-recurring-template
# ---------------------------------------------------------------------------

def update_recurring_template(conn, args):
    """Update a recurring journal template. Only active/paused templates."""
    template_id = args.template_id
    if not template_id:
        err("--template-id is required")

    q = Q.from_(_t_rjt).select(_t_rjt.star).where(_t_rjt.id == P())
    row = conn.execute(q.get_sql(), (template_id,)).fetchone()
    if not row:
        err(f"Recurring template {template_id} not found")
    tmpl = row_to_dict(row)

    if tmpl["status"] == "completed":
        err("Cannot update a completed template")

    updated_fields = []

    if args.template_name:
        conn.execute("UPDATE recurring_journal_template SET name = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.template_name, template_id))
        updated_fields.append("name")

    if args.frequency:
        if args.frequency not in VALID_FREQUENCIES:
            err(f"Invalid frequency '{args.frequency}'. Valid: {VALID_FREQUENCIES}")
        conn.execute("UPDATE recurring_journal_template SET frequency = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.frequency, template_id))
        updated_fields.append("frequency")

    if args.end_date:
        conn.execute("UPDATE recurring_journal_template SET end_date = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.end_date, template_id))
        updated_fields.append("end_date")

    if args.entry_type:
        if args.entry_type not in VALID_ENTRY_TYPES:
            err(f"Invalid entry type '{args.entry_type}'. Valid: {VALID_ENTRY_TYPES}")
        conn.execute("UPDATE recurring_journal_template SET entry_type = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.entry_type, template_id))
        updated_fields.append("entry_type")

    if args.remark is not None:
        conn.execute("UPDATE recurring_journal_template SET remark = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.remark, template_id))
        updated_fields.append("remark")

    if args.auto_submit is not None:
        val = 1 if args.auto_submit else 0
        conn.execute("UPDATE recurring_journal_template SET auto_submit = ?, updated_at = datetime('now') WHERE id = ?",
                     (val, template_id))
        updated_fields.append("auto_submit")

    if args.lines:
        try:
            lines = json.loads(args.lines) if isinstance(args.lines, str) else args.lines
        except json.JSONDecodeError:
            err("Invalid JSON format in --lines")
        try:
            _validate_lines(lines)
        except ValueError as e:
            err(str(e))
        q_acct = Q.from_(_t_account).select(_t_account.id).where(_t_account.id == P())
        for i, line in enumerate(lines):
            acct = conn.execute(q_acct.get_sql(), (line["account_id"],)).fetchone()
            if not acct:
                err(f"Line {i+1}: account {line['account_id']} not found")
        conn.execute("UPDATE recurring_journal_template SET lines = ?, updated_at = datetime('now') WHERE id = ?",
                     (json.dumps(lines) if isinstance(lines, list) else args.lines, template_id))
        updated_fields.append("lines")

    if args.template_status:
        if args.template_status not in ("active", "paused"):
            err(f"Can only set status to 'active' or 'paused', got '{args.template_status}'")
        conn.execute("UPDATE recurring_journal_template SET status = ?, updated_at = datetime('now') WHERE id = ?",
                     (args.template_status, template_id))
        updated_fields.append("status")

    if not updated_fields:
        err("No fields to update")

    audit(conn, "erpclaw-journals", "update-recurring-template",
          "recurring_journal_template", template_id,
          new_values={"updated_fields": updated_fields})
    conn.commit()

    ok({"status": "updated", "template_id": template_id,
        "updated_fields": updated_fields})


# ---------------------------------------------------------------------------
# 13. list-recurring-templates
# ---------------------------------------------------------------------------

def list_recurring_templates(conn, args):
    """List recurring journal templates for a company."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    rjt = Table("recurring_journal_template")
    params = [company_id]

    base = Q.from_(rjt).where(rjt.company_id == P())

    if args.template_status:
        base = base.where(rjt.status == P())
        params.append(args.template_status)

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    q_count = base.select(fn.Count("*"))
    count_row = conn.execute(q_count.get_sql(), params).fetchone()
    total_count = count_row[0]

    list_params = params + [limit, offset]
    q_list = (base.select(
                  rjt.id, rjt.naming_series, rjt.name, rjt.frequency,
                  rjt.start_date, rjt.end_date, rjt.next_run_date,
                  rjt.last_generated_date, rjt.entry_type, rjt.auto_submit,
                  rjt.remark, rjt.status)
              .orderby(rjt.next_run_date, order=Order.asc)
              .limit(P()).offset(P()))
    rows = conn.execute(q_list.get_sql(), list_params).fetchall()

    templates = [row_to_dict(r) for r in rows]
    ok({"templates": templates, "total_count": total_count,
        "limit": limit, "offset": offset,
        "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# 14. get-recurring-template
# ---------------------------------------------------------------------------

def get_recurring_template(conn, args):
    """Get a recurring template with full detail including lines."""
    template_id = args.template_id
    if not template_id:
        err("--template-id is required")

    q = Q.from_(_t_rjt).select(_t_rjt.star).where(_t_rjt.id == P())
    row = conn.execute(q.get_sql(), (template_id,)).fetchone()
    if not row:
        err(f"Recurring template {template_id} not found")

    tmpl = row_to_dict(row)
    # Parse lines JSON for display
    try:
        tmpl["lines"] = json.loads(tmpl["lines"])
    except (json.JSONDecodeError, TypeError):
        pass

    ok(tmpl)


# ---------------------------------------------------------------------------
# 15. process-recurring
# ---------------------------------------------------------------------------

def process_recurring(conn, args):
    """Generate journal entries from all due recurring templates.

    Idempotent: only generates JEs where next_run_date <= as_of_date.
    After generating, advances next_run_date by one frequency period.
    If end_date is reached, marks template as 'completed'.
    """
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")

    as_of_date_str = args.as_of_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Find all due templates
    q_due = (Q.from_(_t_rjt).select(_t_rjt.star)
             .where(_t_rjt.company_id == P())
             .where(_t_rjt.status == "active")
             .where(_t_rjt.next_run_date <= P())
             .orderby(_t_rjt.next_run_date, order=Order.asc))
    due_templates = conn.execute(q_due.get_sql(), (company_id, as_of_date_str)).fetchall()

    results = []

    for row in due_templates:
        tmpl = row_to_dict(row)
        template_id = tmpl["id"]
        lines = json.loads(tmpl["lines"])
        posting_date = tmpl["next_run_date"]

        # Create the journal entry
        je_id = str(uuid.uuid4())
        naming = get_next_name(conn, "journal_entry", company_id=company_id)

        total_debit = sum(to_decimal(l.get("debit", "0")) for l in lines)
        total_credit = sum(to_decimal(l.get("credit", "0")) for l in lines)
        total_debit = round_currency(total_debit)
        total_credit = round_currency(total_credit)

        remark = tmpl.get("remark") or f"Auto-generated from {tmpl['naming_series'] or tmpl['name']}"

        conn.execute(
            """INSERT INTO journal_entry
               (id, naming_series, posting_date, entry_type, total_debit, total_credit,
                remark, status, company_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?)""",
            (je_id, naming, posting_date, tmpl["entry_type"],
             str(total_debit), str(total_credit), remark, company_id),
        )
        _insert_lines(conn, je_id, lines)

        je_status = "draft"

        # Auto-submit if configured
        if tmpl["auto_submit"]:
            try:
                is_opening = tmpl["entry_type"] in ("opening",)
                gl_entries = [{
                    "account_id": l["account_id"],
                    "debit": l.get("debit", "0"),
                    "credit": l.get("credit", "0"),
                    "party_type": l.get("party_type"),
                    "party_id": l.get("party_id"),
                    "cost_center_id": l.get("cost_center_id"),
                } for l in lines]

                validate_gl_entries(
                    conn, gl_entries, company_id, posting_date,
                    is_opening=is_opening, voucher_type="journal_entry",
                )
                insert_gl_entries(
                    conn, gl_entries,
                    voucher_type="journal_entry", voucher_id=je_id,
                    posting_date=posting_date, company_id=company_id,
                    remarks=remark, is_opening=is_opening,
                )
                conn.execute(
                    "UPDATE journal_entry SET status = 'submitted', updated_at = datetime('now') WHERE id = ?",
                    (je_id,),
                )
                je_status = "submitted"
            except (ValueError, Exception) as e:
                sys.stderr.write(f"[erpclaw-journals] Auto-submit failed for {naming}: {e}\n")
                # JE remains as draft

        # Advance next_run_date
        current_next = date.fromisoformat(tmpl["next_run_date"])
        new_next = _advance_date(current_next, tmpl["frequency"])
        new_next_str = new_next.isoformat()

        # Check if end_date is reached
        new_status = "active"
        if tmpl["end_date"] and new_next_str > tmpl["end_date"]:
            new_status = "completed"

        conn.execute(
            """UPDATE recurring_journal_template
               SET next_run_date = ?, last_generated_date = ?,
                   status = ?, updated_at = datetime('now')
               WHERE id = ?""",
            (new_next_str, posting_date, new_status, template_id),
        )

        results.append({
            "template_id": template_id,
            "template_name": tmpl["name"],
            "journal_entry_id": je_id,
            "naming_series": naming,
            "posting_date": posting_date,
            "je_status": je_status,
            "next_run_date": new_next_str if new_status == "active" else None,
            "template_status": new_status,
        })

    audit(conn, "erpclaw-journals", "process-recurring",
          "recurring_journal_template", company_id,
          new_values={"generated": len(results)})
    conn.commit()

    ok({"generated": len(results), "results": results})


# ---------------------------------------------------------------------------
# 16. delete-recurring-template
# ---------------------------------------------------------------------------

def delete_recurring_template(conn, args):
    """Delete a recurring template (soft delete: marks as completed)."""
    template_id = args.template_id
    if not template_id:
        err("--template-id is required")

    q = Q.from_(_t_rjt).select(_t_rjt.star).where(_t_rjt.id == P())
    row = conn.execute(q.get_sql(), (template_id,)).fetchone()
    if not row:
        err(f"Recurring template {template_id} not found")

    q_del = Q.from_(_t_rjt).delete().where(_t_rjt.id == P())
    conn.execute(q_del.get_sql(), (template_id,))

    audit(conn, "erpclaw-journals", "delete-recurring-template",
          "recurring_journal_template", template_id)
    conn.commit()

    ok({"status": "deleted", "deleted": True})


# ---------------------------------------------------------------------------
# 17. status
# ---------------------------------------------------------------------------

def status(conn, args):
    """Show journal entry counts by status."""
    company_id = resolve_company_id(conn, getattr(args, 'company_id', None))

    q_je = (Q.from_(_t_je)
            .select(_t_je.status, fn.Count("*").as_("cnt"))
            .where(_t_je.company_id == P())
            .groupby(_t_je.status))
    rows = conn.execute(q_je.get_sql(), (company_id,)).fetchall()

    counts = {"total": 0, "draft": 0, "submitted": 0, "cancelled": 0, "amended": 0}
    for row in rows:
        counts[row["status"]] = row["cnt"]
        counts["total"] += row["cnt"]

    # Recurring template counts
    q_rjt = (Q.from_(_t_rjt)
             .select(_t_rjt.status, fn.Count("*").as_("cnt"))
             .where(_t_rjt.company_id == P())
             .groupby(_t_rjt.status))
    tmpl_rows = conn.execute(q_rjt.get_sql(), (company_id,)).fetchall()
    recurring = {"active": 0, "paused": 0, "completed": 0}
    for r in tmpl_rows:
        recurring[r["status"]] = r["cnt"]
    counts["recurring_templates"] = recurring

    ok(counts)


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-journal-entry": add_journal_entry,
    "update-journal-entry": update_journal_entry,
    "get-journal-entry": get_journal_entry,
    "list-journal-entries": list_journal_entries,
    "submit-journal-entry": submit_journal_entry,
    "cancel-journal-entry": cancel_journal_entry,
    "amend-journal-entry": amend_journal_entry,
    "delete-journal-entry": delete_journal_entry,
    "duplicate-journal-entry": duplicate_journal_entry,
    "create-intercompany-je": create_intercompany_je,
    "add-recurring-template": add_recurring_template,
    "update-recurring-template": update_recurring_template,
    "list-recurring-templates": list_recurring_templates,
    "get-recurring-template": get_recurring_template,
    "process-recurring": process_recurring,
    "delete-recurring-template": delete_recurring_template,
    "status": status,
}


def main():
    parser = argparse.ArgumentParser(description="ERPClaw Journals Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Journal entry fields
    parser.add_argument("--journal-entry-id")
    parser.add_argument("--company-id")
    parser.add_argument("--posting-date")
    parser.add_argument("--entry-type")
    parser.add_argument("--remark")
    parser.add_argument("--lines")
    parser.add_argument("--amended-from")

    # Intercompany fields
    parser.add_argument("--source-company-id")
    parser.add_argument("--target-company-id")
    parser.add_argument("--amount")
    parser.add_argument("--description")

    # Recurring template fields
    parser.add_argument("--template-id")
    parser.add_argument("--template-name")
    parser.add_argument("--frequency")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--auto-submit", action="store_true", default=None)
    parser.add_argument("--as-of-date")
    parser.add_argument("--template-status")

    # List filters
    parser.add_argument("--status", dest="je_status")
    parser.add_argument("--account-id")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)
    action_fn = ACTIONS[args.action]

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    # Dependency check
    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = "clawhub install " + " ".join(_dep.get("missing_skills", []))
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

    try:
        action_fn(conn, args)
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[erpclaw-journals] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
