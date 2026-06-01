"""
Input validation helpers for Odoo operations.

Catches bad data before it hits the API, providing clear error messages.
"""

import re
from typing import Any, Optional


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


def require(value: Any, field_name: str) -> Any:
    """Assert that a value is not None/empty.

    Args:
        value: The value to check.
        field_name: Human-readable field name (for error messages).

    Returns:
        The value, if valid.

    Raises:
        ValidationError: If the value is falsy.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} is required")
    return value


def validate_email(email: str) -> str:
    """Basic email format validation.

    Args:
        email: Email address string.

    Returns:
        The trimmed email if valid.

    Raises:
        ValidationError: If the format is clearly wrong.
    """
    email = email.strip()
    # Intentionally simple — Odoo does its own deeper validation
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValidationError(f"Invalid email format: {email!r}")
    return email


def validate_phone(phone: str) -> str:
    """Basic phone number cleanup and validation.

    Accepts digits, spaces, dashes, parentheses, and a leading ``+``.

    Args:
        phone: Phone number string.

    Returns:
        The trimmed phone string.

    Raises:
        ValidationError: If the phone contains unexpected characters.
    """
    phone = phone.strip()
    cleaned = re.sub(r"[\s\-\(\)\.]+", "", phone)
    if not re.match(r"^\+?\d{7,15}$", cleaned):
        raise ValidationError(
            f"Invalid phone number: {phone!r} — expected 7–15 digits, optional leading +"
        )
    return phone


def validate_positive_number(
    value: Any,
    field_name: str,
    allow_zero: bool = False,
) -> float:
    """Validate that a value is a positive number.

    Args:
        value: The value to check.
        field_name: Human-readable name for error messages.
        allow_zero: Whether zero is acceptable.

    Returns:
        The value as a float.

    Raises:
        ValidationError: If the value is not a positive number.
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number (got {value!r})")

    if allow_zero and num < 0:
        raise ValidationError(f"{field_name} cannot be negative (got {num})")
    if not allow_zero and num <= 0:
        raise ValidationError(f"{field_name} must be positive (got {num})")

    return num


def validate_id(value: Any, field_name: str = "ID") -> int:
    """Validate that a value is a positive integer ID.

    Args:
        value: The value to check.
        field_name: Human-readable name for error messages.

    Returns:
        The value as an int.

    Raises:
        ValidationError: If the value is not a positive integer.
    """
    try:
        id_val = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be an integer (got {value!r})")

    if id_val <= 0:
        raise ValidationError(f"{field_name} must be positive (got {id_val})")
    return id_val


def validate_date(date_str: str, field_name: str = "date") -> str:
    """Validate a ``YYYY-MM-DD`` date string.

    Args:
        date_str: Date string to validate.
        field_name: Human-readable name for error messages.

    Returns:
        The date string if valid.

    Raises:
        ValidationError: If the format is wrong.
    """
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str.strip()):
        raise ValidationError(
            f"{field_name} must be in YYYY-MM-DD format (got {date_str!r})"
        )
    return date_str.strip()


def validate_state(
    state: str,
    allowed: list[str],
    field_name: str = "state",
) -> str:
    """Validate that a state value is in the allowed set.

    Args:
        state: The state string.
        allowed: List of valid states.
        field_name: Human-readable name for error messages.

    Returns:
        The state string if valid.

    Raises:
        ValidationError: If the state is not in the allowed list.
    """
    if state not in allowed:
        raise ValidationError(
            f"Invalid {field_name}: {state!r} — must be one of {allowed}"
        )
    return state


def validate_order_lines(lines: list[dict]) -> list[dict]:
    """Validate a list of order/invoice line dicts.

    Each line must have ``product_id`` (int) and optionally ``quantity``
    (positive float) and ``price_unit`` (non-negative float).

    Args:
        lines: List of line dicts.

    Returns:
        The validated lines.

    Raises:
        ValidationError: On any invalid line data.
    """
    if not lines:
        raise ValidationError("At least one line item is required")

    for i, line in enumerate(lines, 1):
        prefix = f"Line {i}"
        if "product_id" not in line and "price_unit" not in line:
            raise ValidationError(
                f"{prefix}: must have at least 'product_id' or 'price_unit'"
            )
        if "product_id" in line:
            validate_id(line["product_id"], f"{prefix} product_id")
        if "quantity" in line:
            validate_positive_number(line["quantity"], f"{prefix} quantity")
        if "price_unit" in line:
            validate_positive_number(
                line["price_unit"], f"{prefix} price_unit", allow_zero=True,
            )
        if "discount" in line:
            disc = float(line["discount"])
            if disc < 0 or disc > 100:
                raise ValidationError(
                    f"{prefix} discount must be 0–100 (got {disc})"
                )

    return lines
