"""Foreign exchange gain/loss calculation and posting.

Computes realized FX gain/loss when payments are made in a currency
different from the company's base currency.

Functions:
- get_exchange_rate: Look up rate for date with fallback window
- calculate_exchange_gain_loss: Realized FX gain/loss on payment
- post_exchange_gain_loss: Append GL entries for FX gain/loss
- convert_to_base: Convert amount to base currency
"""
from decimal import Decimal, ROUND_HALF_UP


def get_exchange_rate(conn, from_currency, to_currency, date, max_days=7):
    """Look up exchange rate for a given date with fallback.

    Resolution order:
    1. Exact date match
    2. Nearest date within max_days window (prefer earlier)
    3. None if no rate found

    Args:
        conn: SQLite connection
        from_currency: Source currency code (e.g. 'EUR')
        to_currency: Target currency code (e.g. 'USD')
        date: Date string 'YYYY-MM-DD'
        max_days: Maximum days to search for nearby rates

    Returns:
        Decimal rate or None if not found.
        Rate is always from_currency -> to_currency.
    """
    if from_currency == to_currency:
        return Decimal("1")

    # 1. Exact date match
    row = conn.execute(
        """SELECT rate FROM exchange_rate
           WHERE from_currency = ? AND to_currency = ?
             AND effective_date = ?
           ORDER BY created_at DESC LIMIT 1""",
        (from_currency, to_currency, date),
    ).fetchone()
    if row:
        return Decimal(row["rate"] if isinstance(row, dict) else row[0])

    # Try inverse
    row = conn.execute(
        """SELECT rate FROM exchange_rate
           WHERE from_currency = ? AND to_currency = ?
             AND effective_date = ?
           ORDER BY created_at DESC LIMIT 1""",
        (to_currency, from_currency, date),
    ).fetchone()
    if row:
        rate = Decimal(row["rate"] if isinstance(row, dict) else row[0])
        if rate > 0:
            return (Decimal("1") / rate).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    # 2. Nearest date within window
    row = conn.execute(
        """SELECT rate, effective_date FROM exchange_rate
           WHERE from_currency = ? AND to_currency = ?
             AND effective_date BETWEEN date(?, '-' || ? || ' days') AND date(?, '+' || ? || ' days')
           ORDER BY ABS(julianday(effective_date) - julianday(?)) ASC
           LIMIT 1""",
        (from_currency, to_currency, date, max_days, date, max_days, date),
    ).fetchone()
    if row:
        return Decimal(row["rate"] if isinstance(row, dict) else row[0])

    # Try inverse within window
    row = conn.execute(
        """SELECT rate, effective_date FROM exchange_rate
           WHERE from_currency = ? AND to_currency = ?
             AND effective_date BETWEEN date(?, '-' || ? || ' days') AND date(?, '+' || ? || ' days')
           ORDER BY ABS(julianday(effective_date) - julianday(?)) ASC
           LIMIT 1""",
        (to_currency, from_currency, date, max_days, date, max_days, date),
    ).fetchone()
    if row:
        rate = Decimal(row["rate"] if isinstance(row, dict) else row[0])
        if rate > 0:
            return (Decimal("1") / rate).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    return None


def convert_to_base(amount, exchange_rate):
    """Convert a transaction currency amount to base currency.

    Args:
        amount: Decimal amount in transaction currency
        exchange_rate: Decimal rate (1 transaction unit = X base units)

    Returns:
        Decimal amount in base currency, rounded to 2 decimal places.
    """
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    if not isinstance(exchange_rate, Decimal):
        exchange_rate = Decimal(str(exchange_rate))
    return (amount * exchange_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_exchange_gain_loss(payment_amount, payment_exchange_rate,
                                  invoice_exchange_rate, account_currency_amount=None):
    """Compute realized FX gain/loss on a payment.

    When a payment is made at a different exchange rate than the invoice rate,
    the difference is a realized FX gain or loss.

    gain_loss = amount_in_txn_currency * (payment_rate - invoice_rate)

    Positive = gain (favorable rate change)
    Negative = loss (unfavorable rate change)

    For receivables (receive payment):
        Invoice at rate 1.10, payment at rate 1.12 → gain (got more base currency)
    For payables (make payment):
        Invoice at rate 1.10, payment at rate 1.08 → gain (paid less base currency)

    Args:
        payment_amount: Decimal amount in transaction currency
        payment_exchange_rate: Rate at time of payment
        invoice_exchange_rate: Rate at time of invoice
        account_currency_amount: Override transaction amount (for partial payments)

    Returns:
        Decimal gain/loss amount in base currency.
    """
    if not isinstance(payment_amount, Decimal):
        payment_amount = Decimal(str(payment_amount))
    if not isinstance(payment_exchange_rate, Decimal):
        payment_exchange_rate = Decimal(str(payment_exchange_rate))
    if not isinstance(invoice_exchange_rate, Decimal):
        invoice_exchange_rate = Decimal(str(invoice_exchange_rate))

    txn_amount = account_currency_amount if account_currency_amount is not None else payment_amount
    if not isinstance(txn_amount, Decimal):
        txn_amount = Decimal(str(txn_amount))

    rate_diff = payment_exchange_rate - invoice_exchange_rate
    gain_loss = (txn_amount * rate_diff).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return gain_loss


def post_exchange_gain_loss(gl_entries, gain_loss_amount,
                             exchange_gain_loss_account_id, cost_center_id=None):
    """Append FX gain/loss GL entries to an existing GL entry list.

    If gain_loss > 0 (gain): CR Exchange Gain/Loss account
    If gain_loss < 0 (loss): DR Exchange Gain/Loss account

    The offsetting entry goes to the AR/AP account (already in gl_entries).

    Args:
        gl_entries: List of GL entry dicts to append to
        gain_loss_amount: Decimal gain/loss (positive=gain, negative=loss)
        exchange_gain_loss_account_id: Account ID for FX gain/loss
        cost_center_id: Optional cost center for P&L tracking

    Returns:
        Modified gl_entries list with FX entry appended.
    """
    if not isinstance(gain_loss_amount, Decimal):
        gain_loss_amount = Decimal(str(gain_loss_amount))

    if gain_loss_amount == 0 or not exchange_gain_loss_account_id:
        return gl_entries

    abs_amount = abs(gain_loss_amount)

    if gain_loss_amount > 0:
        # Gain: CR exchange gain/loss account
        entry = {
            "account_id": exchange_gain_loss_account_id,
            "debit": "0",
            "credit": str(abs_amount),
        }
    else:
        # Loss: DR exchange gain/loss account
        entry = {
            "account_id": exchange_gain_loss_account_id,
            "debit": str(abs_amount),
            "credit": "0",
        }

    if cost_center_id:
        entry["cost_center_id"] = cost_center_id

    gl_entries.append(entry)
    return gl_entries
