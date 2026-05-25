"""Decimal arithmetic helpers for ERPClaw.

All financial amounts in ERPClaw are stored as TEXT in SQLite and
manipulated as Python Decimal objects. This module provides safe
conversion, rounding, formatting, and comparison utilities.

NEVER use float for financial calculations.
"""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# Default currency precision (USD = 2 decimal places)
DEFAULT_PRECISION = Decimal("0.01")

# Tolerance for balance checks (covers rounding in multi-line postings)
BALANCE_TOLERANCE = Decimal("0.01")


def to_decimal(value) -> Decimal:
    """Convert a value to Decimal safely.

    Accepts: str, int, Decimal. Rejects float explicitly to prevent
    silent precision loss (e.g., float 0.1 != Decimal("0.1")).

    Args:
        value: The value to convert.

    Returns:
        Decimal representation.

    Raises:
        TypeError: If value is a float.
        ValueError: If value cannot be parsed as Decimal.
    """
    if isinstance(value, float):
        raise TypeError(
            f"Cannot convert float {value!r} to Decimal. "
            "Use a string or int instead to avoid precision loss."
        )
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    try:
        return Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"Cannot convert {value!r} to Decimal")


def round_currency(amount, precision=None) -> Decimal:
    """Round a Decimal amount to currency precision.

    Args:
        amount: Decimal amount to round.
        precision: Decimal quantize value (e.g., Decimal("0.01") for 2dp).
                   Defaults to DEFAULT_PRECISION (0.01 for USD).

    Returns:
        Rounded Decimal.
    """
    if precision is None:
        precision = DEFAULT_PRECISION
    d = to_decimal(amount)
    return d.quantize(precision, rounding=ROUND_HALF_UP)


def fmt_currency(amount, symbol="$", precision=None) -> str:
    """Format a Decimal as a currency string.

    Args:
        amount: Decimal amount.
        symbol: Currency symbol prefix.
        precision: Decimal quantize value.

    Returns:
        Formatted string like "$1,234.56".
    """
    rounded = round_currency(amount, precision)
    # Format with comma separators
    sign = "-" if rounded < 0 else ""
    abs_val = abs(rounded)
    integer_part = int(abs_val)
    decimal_part = abs_val - integer_part

    # Determine decimal places from precision
    prec = precision or DEFAULT_PRECISION
    dp = abs(prec.as_tuple().exponent)

    formatted_int = f"{integer_part:,}"
    if dp > 0:
        decimal_str = f"{decimal_part:.{dp}f}"[1:]  # strip leading "0"
        return f"{sign}{symbol}{formatted_int}{decimal_str}"
    return f"{sign}{symbol}{formatted_int}"


def amounts_equal(a, b, tolerance=None) -> bool:
    """Check if two amounts are equal within tolerance.

    Used primarily for double-entry balance checks where multi-line
    rounding can produce sub-penny differences.

    Args:
        a: First amount (Decimal or str).
        b: Second amount (Decimal or str).
        tolerance: Maximum allowed difference. Defaults to BALANCE_TOLERANCE.

    Returns:
        True if abs(a - b) <= tolerance.
    """
    if tolerance is None:
        tolerance = BALANCE_TOLERANCE
    da = to_decimal(a)
    db = to_decimal(b)
    return abs(da - db) <= to_decimal(tolerance)
