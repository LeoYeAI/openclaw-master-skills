"""Stock Ledger Entry (SLE) engine for ERPClaw.

All stock_ledger_entry writes go through this module. This is the ONLY code
that writes to the stock_ledger_entry table. Critical design invariant.

Key functions:
- validate_stock_entries(): Validate SLE entries before insertion
- insert_sle_entries(): Validate + insert + compute running balance
- reverse_sle_entries(): Cancel by creating negative-qty mirror entries
- get_stock_balance(): Current qty & value for item/warehouse
- get_valuation_rate(): Current moving-average or FIFO valuation rate
- create_perpetual_inventory_gl(): Generate GL entries for stock movements

Valuation methods:
- moving_average: New rate = (old_value + incoming_value) / (old_qty + incoming_qty)
- fifo: Not yet implemented (Phase 2+); falls back to moving_average

NEVER commit inside these functions — the caller owns the transaction.
"""
import uuid
import sqlite3
from decimal import Decimal
from typing import Optional

from erpclaw_lib.decimal_utils import to_decimal, round_currency


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_stock_entries(
    conn: sqlite3.Connection,
    entries: list[dict],
    posting_date: str,
    company_id: str,
) -> list[str]:
    """Validate stock entries before insertion.

    Checks:
    1. Each entry has item_id, warehouse_id, actual_qty
    2. Item exists and is a stock item
    3. Warehouse exists, is not a group, belongs to company
    4. For outgoing (actual_qty < 0): sufficient stock exists
    5. Batch validation (if item has_batch)
    6. Serial number validation (if item has_serial)

    Returns:
        List of warning messages (empty if no warnings).

    Raises:
        ValueError on validation failure.
    """
    warnings = []

    for i, entry in enumerate(entries):
        item_id = entry.get("item_id")
        warehouse_id = entry.get("warehouse_id")
        actual_qty = to_decimal(entry.get("actual_qty", "0"))

        # 1. Required fields
        if not item_id:
            raise ValueError(f"SLE entry {i}: item_id is required")
        if not warehouse_id:
            raise ValueError(f"SLE entry {i}: warehouse_id is required")
        if actual_qty == 0:
            raise ValueError(f"SLE entry {i}: actual_qty cannot be zero")

        # 2. Item exists and is stock item
        item = conn.execute(
            "SELECT * FROM item WHERE id = ?", (item_id,)
        ).fetchone()
        if item is None:
            raise ValueError(f"SLE entry {i}: item {item_id} does not exist")
        if item["is_stock_item"] == 0:
            raise ValueError(
                f"SLE entry {i}: item '{item['item_name']}' is not a stock item "
                f"(item_type={item['item_type']})"
            )
        if item["status"] == "disabled":
            raise ValueError(
                f"SLE entry {i}: item '{item['item_name']}' is disabled"
            )

        # 3. Warehouse exists and belongs to company
        wh = conn.execute(
            "SELECT * FROM warehouse WHERE id = ?", (warehouse_id,)
        ).fetchone()
        if wh is None:
            raise ValueError(f"SLE entry {i}: warehouse {warehouse_id} does not exist")
        if wh["is_group"]:
            raise ValueError(
                f"SLE entry {i}: warehouse '{wh['name']}' is a group — "
                f"cannot post stock to group warehouses"
            )
        if wh["company_id"] != company_id:
            raise ValueError(
                f"SLE entry {i}: warehouse '{wh['name']}' belongs to "
                f"company {wh['company_id']}, expected {company_id}"
            )

        # 4. Sufficient stock for outgoing entries
        if actual_qty < 0:
            balance = get_stock_balance(conn, item_id, warehouse_id)
            current_qty = to_decimal(balance["qty"])
            if current_qty + actual_qty < 0:
                raise ValueError(
                    f"SLE entry {i}: insufficient stock for item "
                    f"'{item['item_name']}' in warehouse '{wh['name']}'. "
                    f"Current qty: {current_qty}, requested: {actual_qty}"
                )

        # 5. Batch validation
        batch_id = entry.get("batch_id")
        if item["has_batch"] and actual_qty > 0 and not batch_id:
            warnings.append(
                f"SLE entry {i}: item '{item['item_name']}' has batch tracking "
                f"enabled but no batch_id provided"
            )
        if batch_id:
            batch = conn.execute(
                "SELECT * FROM batch WHERE id = ?", (batch_id,)
            ).fetchone()
            if batch is None:
                raise ValueError(f"SLE entry {i}: batch {batch_id} does not exist")
            if batch["item_id"] != item_id:
                raise ValueError(
                    f"SLE entry {i}: batch {batch_id} belongs to item "
                    f"{batch['item_id']}, not {item_id}"
                )
            # Check expiry for outgoing
            if actual_qty < 0 and batch.get("expiry_date"):
                if batch["expiry_date"] < posting_date:
                    warnings.append(
                        f"SLE entry {i}: batch '{batch['batch_name']}' expired on "
                        f"{batch['expiry_date']}"
                    )

        # 6. Serial number validation
        serial_no = entry.get("serial_number")
        if item["has_serial"] and actual_qty != 0 and not serial_no:
            warnings.append(
                f"SLE entry {i}: item '{item['item_name']}' has serial tracking "
                f"enabled but no serial_number provided"
            )

    return warnings


# ---------------------------------------------------------------------------
# Insert SLE Entries
# ---------------------------------------------------------------------------

def insert_sle_entries(
    conn: sqlite3.Connection,
    entries: list[dict],
    voucher_type: str,
    voucher_id: str,
    posting_date: str,
    company_id: str,
) -> list[str]:
    """Insert stock ledger entries within the caller's transaction.

    MUST be called inside an existing transaction. Does NOT commit.

    Steps:
    1. Idempotency check — reject if SLE already exist for this voucher
    2. Run validation
    3. For each entry: compute running balance, valuation rate, insert SLE

    Returns:
        List of generated SLE IDs.

    Raises:
        ValueError on validation failure or if entries already exist.
    """
    # 1. Idempotency check
    existing = conn.execute(
        "SELECT COUNT(*) as cnt FROM stock_ledger_entry "
        "WHERE voucher_type = ? AND voucher_id = ? AND is_cancelled = 0",
        (voucher_type, voucher_id),
    ).fetchone()
    if existing["cnt"] > 0:
        raise ValueError(
            f"SLE entries already exist for voucher ({voucher_type}, {voucher_id})"
        )

    # 2. Validate
    _warnings = validate_stock_entries(conn, entries, posting_date, company_id)

    # 3. Insert with running balance computation
    generated_ids = []
    for entry in entries:
        sle_id = str(uuid.uuid4())
        generated_ids.append(sle_id)

        item_id = entry["item_id"]
        warehouse_id = entry["warehouse_id"]
        actual_qty = to_decimal(entry.get("actual_qty", "0"))
        incoming_rate = to_decimal(entry.get("incoming_rate", "0"))

        # Get current balance for this item/warehouse
        current = get_stock_balance(conn, item_id, warehouse_id)
        current_qty = to_decimal(current["qty"])
        current_value = to_decimal(current["stock_value"])

        # Compute valuation rate and new balance
        if actual_qty > 0:
            # Incoming: use provided rate or fall back to item standard_rate
            if incoming_rate <= 0:
                item_row = conn.execute(
                    "SELECT standard_rate FROM item WHERE id = ?", (item_id,)
                ).fetchone()
                incoming_rate = to_decimal(item_row["standard_rate"]) if item_row else Decimal("0")
            incoming_value = round_currency(actual_qty * incoming_rate)
            new_qty = current_qty + actual_qty
            new_value = current_value + incoming_value
            if new_qty > 0:
                valuation_rate = round_currency(new_value / new_qty)
            else:
                valuation_rate = incoming_rate
        else:
            # Outgoing: use current valuation rate
            if current_qty > 0:
                valuation_rate = round_currency(current_value / current_qty)
            else:
                valuation_rate = Decimal("0")
            outgoing_value = round_currency(abs(actual_qty) * valuation_rate)
            new_qty = current_qty + actual_qty  # actual_qty is negative
            new_value = current_value - outgoing_value
            incoming_rate = Decimal("0")  # Not an incoming entry

        new_stock_value = round_currency(new_value)
        stock_value_diff = round_currency(new_stock_value - current_value)
        qty_after = round_currency(new_qty)

        conn.execute(
            """
            INSERT INTO stock_ledger_entry (
                id, posting_date, posting_time, item_id, warehouse_id,
                actual_qty, qty_after_transaction, valuation_rate,
                stock_value, stock_value_difference,
                voucher_type, voucher_id, batch_id, serial_number,
                incoming_rate, is_cancelled, fiscal_year, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, datetime('now'))
            """,
            (
                sle_id,
                posting_date,
                entry.get("posting_time"),
                item_id,
                warehouse_id,
                str(round_currency(actual_qty)),
                str(qty_after),
                str(round_currency(valuation_rate)),
                str(new_stock_value),
                str(stock_value_diff),
                voucher_type,
                voucher_id,
                entry.get("batch_id"),
                entry.get("serial_number"),
                str(round_currency(incoming_rate)),
                entry.get("fiscal_year"),
            ),
        )

    return generated_ids


# ---------------------------------------------------------------------------
# Reverse SLE Entries
# ---------------------------------------------------------------------------

def reverse_sle_entries(
    conn: sqlite3.Connection,
    voucher_type: str,
    voucher_id: str,
    posting_date: str,
) -> list[str]:
    """Create reversing SLE entries for cancellation.

    Finds all SLE rows for the voucher where is_cancelled=0.
    Creates mirror entries with negated actual_qty.
    Sets is_cancelled=1 on originals.

    Does NOT commit — caller manages transaction.

    Returns:
        List of new reversal SLE IDs.

    Raises:
        ValueError if no entries found.
    """
    originals = conn.execute(
        "SELECT * FROM stock_ledger_entry "
        "WHERE voucher_type = ? AND voucher_id = ? AND is_cancelled = 0",
        (voucher_type, voucher_id),
    ).fetchall()

    if not originals:
        raise ValueError(
            f"No active SLE entries found for voucher ({voucher_type}, {voucher_id})"
        )

    reversal_ids = []

    for orig in originals:
        reversal_id = str(uuid.uuid4())
        reversal_ids.append(reversal_id)

        item_id = orig["item_id"]
        warehouse_id = orig["warehouse_id"]
        orig_qty = to_decimal(orig["actual_qty"])
        reversal_qty = -orig_qty

        # Get current balance to compute new running totals
        current = get_stock_balance(conn, item_id, warehouse_id)
        current_qty = to_decimal(current["qty"])
        current_value = to_decimal(current["stock_value"])

        # Compute reversal impact
        orig_value_diff = to_decimal(orig["stock_value_difference"])
        new_value = current_value - orig_value_diff
        new_qty = current_qty + reversal_qty

        if new_qty > 0:
            valuation_rate = round_currency(new_value / new_qty)
        elif new_qty == 0:
            valuation_rate = Decimal("0")
        else:
            valuation_rate = to_decimal(orig["valuation_rate"])

        new_stock_value = round_currency(new_value)
        stock_value_diff = round_currency(-orig_value_diff)

        # Insert reversal entry (also marked as cancelled — it's an audit record)
        conn.execute(
            """
            INSERT INTO stock_ledger_entry (
                id, posting_date, posting_time, item_id, warehouse_id,
                actual_qty, qty_after_transaction, valuation_rate,
                stock_value, stock_value_difference,
                voucher_type, voucher_id, batch_id, serial_number,
                incoming_rate, is_cancelled, fiscal_year, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, datetime('now'))
            """,
            (
                reversal_id,
                posting_date,
                None,
                item_id,
                warehouse_id,
                str(round_currency(reversal_qty)),
                str(round_currency(new_qty)),
                str(round_currency(valuation_rate)),
                str(new_stock_value),
                str(stock_value_diff),
                voucher_type,
                voucher_id,
                orig["batch_id"],
                orig["serial_number"],
                "0",
                orig["fiscal_year"],
            ),
        )

        # Mark original as cancelled
        conn.execute(
            "UPDATE stock_ledger_entry SET is_cancelled = 1 WHERE id = ?",
            (orig["id"],),
        )

    return reversal_ids


# ---------------------------------------------------------------------------
# Query: Stock Balance
# ---------------------------------------------------------------------------

def get_stock_balance(
    conn: sqlite3.Connection,
    item_id: str,
    warehouse_id: str,
    as_of_date: Optional[str] = None,
) -> dict:
    """Get current stock balance for item in warehouse.

    Computes from SLE entries (sum of actual_qty where is_cancelled=0).

    Args:
        conn: SQLite connection.
        item_id: Item to query.
        warehouse_id: Warehouse to query.
        as_of_date: Optional cutoff date. None = all time.

    Returns:
        {"qty": str, "valuation_rate": str, "stock_value": str}
    """
    if as_of_date:
        row = conn.execute(
            """
            SELECT
                COALESCE(decimal_sum(actual_qty), '0') as total_qty,
                COALESCE(
                    (SELECT stock_value FROM stock_ledger_entry
                     WHERE item_id = ? AND warehouse_id = ? AND is_cancelled = 0
                       AND posting_date <= ?
                     ORDER BY rowid DESC LIMIT 1),
                    '0'
                ) as last_stock_value,
                COALESCE(
                    (SELECT valuation_rate FROM stock_ledger_entry
                     WHERE item_id = ? AND warehouse_id = ? AND is_cancelled = 0
                       AND posting_date <= ?
                     ORDER BY rowid DESC LIMIT 1),
                    '0'
                ) as last_valuation_rate
            FROM stock_ledger_entry
            WHERE item_id = ? AND warehouse_id = ? AND is_cancelled = 0
              AND posting_date <= ?
            """,
            (
                item_id, warehouse_id, as_of_date,
                item_id, warehouse_id, as_of_date,
                item_id, warehouse_id, as_of_date,
            ),
        ).fetchone()
    else:
        row = conn.execute(
            """
            SELECT
                COALESCE(decimal_sum(actual_qty), '0') as total_qty,
                COALESCE(
                    (SELECT stock_value FROM stock_ledger_entry
                     WHERE item_id = ? AND warehouse_id = ? AND is_cancelled = 0
                     ORDER BY rowid DESC LIMIT 1),
                    '0'
                ) as last_stock_value,
                COALESCE(
                    (SELECT valuation_rate FROM stock_ledger_entry
                     WHERE item_id = ? AND warehouse_id = ? AND is_cancelled = 0
                     ORDER BY rowid DESC LIMIT 1),
                    '0'
                ) as last_valuation_rate
            FROM stock_ledger_entry
            WHERE item_id = ? AND warehouse_id = ? AND is_cancelled = 0
            """,
            (
                item_id, warehouse_id,
                item_id, warehouse_id,
                item_id, warehouse_id,
            ),
        ).fetchone()

    qty = to_decimal(str(row["total_qty"]))
    stock_value = to_decimal(str(row["last_stock_value"]))
    valuation_rate = to_decimal(str(row["last_valuation_rate"]))

    # Recalculate stock_value from qty * rate if qty-based is more accurate
    if qty > 0 and valuation_rate > 0:
        stock_value = round_currency(qty * valuation_rate)

    return {
        "qty": str(round_currency(qty)),
        "valuation_rate": str(round_currency(valuation_rate)),
        "stock_value": str(round_currency(stock_value)),
    }


# ---------------------------------------------------------------------------
# Query: Valuation Rate
# ---------------------------------------------------------------------------

def get_valuation_rate(
    conn: sqlite3.Connection,
    item_id: str,
    warehouse_id: Optional[str] = None,
) -> Decimal:
    """Get current valuation rate for an item.

    Uses moving average: total stock value / total qty across warehouses
    (or for a specific warehouse if provided).

    Args:
        conn: SQLite connection.
        item_id: Item to query.
        warehouse_id: Optional specific warehouse. None = all warehouses.

    Returns:
        Decimal valuation rate.
    """
    if warehouse_id:
        balance = get_stock_balance(conn, item_id, warehouse_id)
        rate = to_decimal(balance["valuation_rate"])
        if rate > 0:
            return rate
    else:
        # Aggregate across all warehouses
        row = conn.execute(
            """
            SELECT
                COALESCE(decimal_sum(actual_qty), '0') as total_qty,
                COALESCE(decimal_sum(stock_value_difference), '0') as total_value
            FROM stock_ledger_entry
            WHERE item_id = ? AND is_cancelled = 0
            """,
            (item_id,),
        ).fetchone()
        total_qty = to_decimal(str(row["total_qty"]))
        total_value = to_decimal(str(row["total_value"]))
        if total_qty > 0:
            return round_currency(total_value / total_qty)

    # Fallback to item standard rate
    item = conn.execute(
        "SELECT standard_rate FROM item WHERE id = ?", (item_id,)
    ).fetchone()
    if item:
        return to_decimal(item["standard_rate"])
    return Decimal("0")


# ---------------------------------------------------------------------------
# Perpetual Inventory GL Entries
# ---------------------------------------------------------------------------

def create_perpetual_inventory_gl(
    conn: sqlite3.Connection,
    sle_entries: list[dict],
    voucher_type: str,
    voucher_id: str,
    posting_date: str,
    company_id: str,
    expense_account_id: Optional[str] = None,
    cost_center_id: Optional[str] = None,
) -> list[dict]:
    """Generate GL entries for perpetual inventory from SLE entries.

    For each SLE entry, creates balanced GL entries:
    - Receipt (qty > 0): DR warehouse account (Stock-in-Hand), CR contra account
    - Issue (qty < 0): DR contra account, CR warehouse account (Stock-in-Hand)

    The contra account is determined by context:
    - Stock entry receipt: Stock Received Not Billed or Opening Stock account
    - Stock entry issue: COGS / expense account
    - Delivery note: COGS account
    - Purchase receipt: Stock Received Not Billed
    - Stock reconciliation: Stock Adjustment account

    Does NOT insert GL entries — returns the list for the caller to pass
    to gl_posting.insert_gl_entries().

    Args:
        conn: SQLite connection.
        sle_entries: List of SLE entry dicts (must have item_id, warehouse_id,
                     actual_qty, stock_value_difference).
        voucher_type: The voucher type.
        voucher_id: The voucher ID.
        posting_date: Posting date.
        company_id: Company ID.
        expense_account_id: Override contra account (e.g., COGS for delivery).
        cost_center_id: Cost center for P&L accounts.

    Returns:
        List of GL entry dicts ready for gl_posting.insert_gl_entries().
    """
    gl_entries = []

    for entry in sle_entries:
        warehouse_id = entry["warehouse_id"]
        value_diff = to_decimal(entry.get("stock_value_difference", "0"))

        if value_diff == 0:
            continue

        # Get warehouse's linked GL account (Stock-in-Hand)
        wh = conn.execute(
            "SELECT account_id, name FROM warehouse WHERE id = ?",
            (warehouse_id,)
        ).fetchone()
        warehouse_account_id = wh["account_id"] if wh and wh["account_id"] else None

        if not warehouse_account_id:
            # Fallback: find a stock-in-hand account for the company
            stock_acct = conn.execute(
                "SELECT id FROM account WHERE account_type = 'stock' "
                "AND company_id = ? AND is_group = 0 LIMIT 1",
                (company_id,),
            ).fetchone()
            warehouse_account_id = stock_acct["id"] if stock_acct else None

        if not warehouse_account_id:
            continue  # Cannot create GL without a stock account

        # Determine contra account
        contra_account_id = expense_account_id
        if not contra_account_id:
            # Default: look for Stock Received Not Billed or COGS
            if to_decimal(entry.get("actual_qty", "0")) > 0:
                contra = conn.execute(
                    "SELECT id FROM account WHERE account_type = 'stock_received_not_billed' "
                    "AND company_id = ? AND is_group = 0 LIMIT 1",
                    (company_id,),
                ).fetchone()
            else:
                contra = conn.execute(
                    "SELECT id FROM account WHERE account_type = 'cost_of_goods_sold' "
                    "AND company_id = ? AND is_group = 0 LIMIT 1",
                    (company_id,),
                ).fetchone()
            contra_account_id = contra["id"] if contra else None

        if not contra_account_id:
            continue  # Cannot create GL without contra account

        abs_value = abs(value_diff)

        if value_diff > 0:
            # Incoming stock: DR Stock-in-Hand, CR Contra
            gl_entries.append({
                "account_id": warehouse_account_id,
                "debit": str(round_currency(abs_value)),
                "credit": "0",
            })
            gl_entries.append({
                "account_id": contra_account_id,
                "debit": "0",
                "credit": str(round_currency(abs_value)),
                "cost_center_id": cost_center_id,
            })
        else:
            # Outgoing stock: DR Contra, CR Stock-in-Hand
            gl_entries.append({
                "account_id": contra_account_id,
                "debit": str(round_currency(abs_value)),
                "credit": "0",
                "cost_center_id": cost_center_id,
            })
            gl_entries.append({
                "account_id": warehouse_account_id,
                "debit": "0",
                "credit": str(round_currency(abs_value)),
            })

    return gl_entries
