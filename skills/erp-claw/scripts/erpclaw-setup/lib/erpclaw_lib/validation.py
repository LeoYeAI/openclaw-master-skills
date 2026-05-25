"""Input validation utilities for ERPClaw.

Provides reusable validators for common input types like UUIDs and
text length limits. Designed for use in action handlers before DB queries.
"""
import json
import re
import uuid as _uuid

# UUID4 pattern: 8-4-4-4-12 hex chars
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def validate_uuid(value: str, field_name: str = "id") -> str:
    """Validate that a string is a properly formatted UUID.

    Args:
        value: The string to validate.
        field_name: Name of the field (for error messages).

    Returns:
        The validated UUID string (lowercased).

    Raises:
        ValueError: If the value is not a valid UUID.
    """
    if not value or not isinstance(value, str):
        raise ValueError(f"--{field_name} is required and must be a string")
    if not _UUID_RE.match(value):
        raise ValueError(f"--{field_name} must be a valid UUID format")
    return value.lower()


def validate_ids(args, *field_names: str) -> None:
    """Validate multiple UUID fields on an argparse namespace.

    Checks each field that is not None. Skips None values (optional params).

    Args:
        args: argparse.Namespace object.
        *field_names: Attribute names to validate (e.g., "company_id").

    Raises:
        ValueError: If any non-None field is not a valid UUID.
    """
    for name in field_names:
        value = getattr(args, name, None)
        if value is not None:
            flag_name = name.replace("_", "-")
            validate_uuid(value, flag_name)


def validate_text_length(value: str, field_name: str,
                         max_length: int = 500) -> str:
    """Validate text field length.

    Args:
        value: The text string.
        field_name: Name of the field (for error messages).
        max_length: Maximum allowed length.

    Returns:
        The validated string.

    Raises:
        ValueError: If the text exceeds max_length.
    """
    if value and len(value) > max_length:
        raise ValueError(
            f"--{field_name} exceeds maximum length of {max_length} characters"
        )
    return value


# Field name patterns and their max lengths
_SHORT_FIELDS = {
    "name", "code", "abbr", "abbreviation", "symbol", "account_number",
    "phone", "mobile", "fax", "currency", "uom", "title", "first_name",
    "last_name", "gender", "status", "priority", "type", "category",
}
_MEDIUM_FIELDS = {
    "email", "address", "city", "state", "country", "website", "subject",
    "description",
}
_JSON_FIELDS = {
    "lines", "entries", "items", "allocations", "components", "operations",
    "periods", "metrics", "aging_buckets", "rules",
}

# Limits
_SHORT_LIMIT = 200
_MEDIUM_LIMIT = 1000
_LONG_LIMIT = 5000
_JSON_LIMIT = 50000


def check_input_lengths(args) -> None:
    """Check all string args against reasonable length limits.

    Applies tiered limits based on field name:
    - Short fields (name, code, etc.): 200 chars
    - Medium fields (email, address, etc.): 1000 chars
    - JSON fields (lines, entries, etc.): 50000 chars
    - All other string fields: 5000 chars

    Skips None values and non-string values.

    Args:
        args: argparse.Namespace object.

    Raises:
        ValueError: If any field exceeds its limit.
    """
    for attr_name in vars(args):
        value = getattr(args, attr_name, None)
        if value is None or not isinstance(value, str):
            continue

        # Determine limit based on field name
        if attr_name in _SHORT_FIELDS:
            limit = _SHORT_LIMIT
        elif attr_name in _MEDIUM_FIELDS:
            limit = _MEDIUM_LIMIT
        elif attr_name in _JSON_FIELDS:
            limit = _JSON_LIMIT
        else:
            limit = _LONG_LIMIT

        if len(value) > limit:
            flag_name = attr_name.replace("_", "-")
            raise ValueError(
                f"--{flag_name} exceeds maximum length of {limit} characters"
            )


def require_entity(conn, table: str, entity_id: str, label: str = None) -> dict:
    """Validate entity exists by ID, return row as dict. Raises ValueError if not found."""
    if not re.match(r'^[a-z][a-z0-9_]*$', table):
        raise ValueError(f"Invalid table name: {table}")
    row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (entity_id,)).fetchone()
    if not row:
        raise ValueError(f"{label or table} {entity_id} not found")
    return dict(row)


def parse_json_arg(value: str, label: str = "JSON argument"):
    """Parse a JSON string argument. Returns parsed object or None if empty."""
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid {label}: {e}")
