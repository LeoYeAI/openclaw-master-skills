"""Custom field runtime for ERPClaw.

Allows verticals to extend any core doctype with custom fields
without schema changes. Uses the custom_field and custom_field_value tables.

Schema (from init_db.py):
    custom_field        — field definitions (id, table_name, field_name, field_type, ...)
    custom_field_value  — EAV store (table_name, doc_id, field_name, value)
"""
import json
import re
import uuid


# ---------------------------------------------------------------------------
# Field definitions
# ---------------------------------------------------------------------------

def get_custom_fields(conn, table_name):
    """Return custom field definitions for a table/doctype.

    Args:
        conn: sqlite3 connection (row_factory = sqlite3.Row expected)
        table_name: the doctype/table to query

    Returns:
        list of dicts, one per custom field, ordered by field_name
    """
    rows = conn.execute(
        "SELECT * FROM custom_field WHERE table_name = ? ORDER BY field_name",
        (table_name,),
    ).fetchall()
    return [dict(r) for r in rows]


def add_custom_field(
    conn,
    table_name,
    field_name,
    field_type,
    owner_skill,
    label=None,
    required=False,
    default_value=None,
    field_options=None,
    insert_after=None,
):
    """Register a new custom field definition.

    Args:
        conn: database connection
        table_name: target table/doctype to extend
        field_name: unique field name (snake_case)
        field_type: one of 'text', 'int', 'float', 'date', 'select', 'link', 'json'
        owner_skill: skill that owns this custom field
        label: human-readable label (defaults to field_name)
        required: whether field is required (default False)
        default_value: default value as string
        field_options: JSON string with type-specific options
        insert_after: field name to position after in forms

    Returns:
        the generated UUID for the new field definition
    """
    field_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO custom_field
           (id, table_name, field_name, field_type, field_options, label,
            required, default_value, insert_after, owner_skill)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            field_id,
            table_name,
            field_name,
            field_type,
            field_options,
            label or field_name,
            1 if required else 0,
            default_value,
            insert_after,
            owner_skill,
        ),
    )
    return field_id


def remove_custom_field(conn, table_name, field_name, owner_skill):
    """Remove a custom field definition and all its stored values.

    Only the owning skill may remove a field.

    Args:
        conn: database connection
        table_name: the doctype/table the field belongs to
        field_name: field to remove
        owner_skill: must match the original owner_skill

    Returns:
        True if removed, False if not found or wrong owner
    """
    row = conn.execute(
        "SELECT owner_skill FROM custom_field WHERE table_name = ? AND field_name = ?",
        (table_name, field_name),
    ).fetchone()
    if not row or row["owner_skill"] != owner_skill:
        return False
    conn.execute(
        "DELETE FROM custom_field_value WHERE table_name = ? AND field_name = ?",
        (table_name, field_name),
    )
    conn.execute(
        "DELETE FROM custom_field WHERE table_name = ? AND field_name = ?",
        (table_name, field_name),
    )
    return True


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_VALID_FIELD_TYPES = {"text", "int", "float", "date", "select", "link", "json"}


def validate_custom_field_values(conn, table_name, values):
    """Validate custom field values against their definitions.

    Args:
        conn: database connection
        table_name: the doctype/table being extended
        values: dict of {field_name: value} to validate

    Returns:
        list of error strings (empty = valid)
    """
    fields = {f["field_name"]: f for f in get_custom_fields(conn, table_name)}
    errors = []

    # Check required fields that are missing
    for fname, fdef in fields.items():
        if fdef["required"] and fname not in values:
            errors.append(f"Required custom field '{fname}' is missing")

    # Validate each provided value
    for fname, value in values.items():
        if fname not in fields:
            errors.append(f"Unknown custom field '{fname}' for {table_name}")
            continue

        fdef = fields[fname]
        ftype = fdef["field_type"]

        # None/empty is acceptable for non-required fields
        if value is None or value == "":
            if fdef["required"]:
                errors.append(f"Required custom field '{fname}' cannot be empty")
            continue

        # Type-specific validation
        if ftype == "int":
            try:
                int(value)
            except (ValueError, TypeError):
                errors.append(f"Custom field '{fname}' must be an integer")

        elif ftype == "float":
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(f"Custom field '{fname}' must be a number")

        elif ftype == "date":
            # Expect ISO format YYYY-MM-DD
            if isinstance(value, str):
                import re
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                    errors.append(
                        f"Custom field '{fname}' must be a date in YYYY-MM-DD format"
                    )

        elif ftype == "select" and fdef.get("field_options"):
            try:
                options = json.loads(fdef["field_options"])
                allowed = options.get("values", [])
                if allowed and value not in allowed:
                    errors.append(
                        f"Custom field '{fname}' must be one of: "
                        f"{', '.join(str(v) for v in allowed)}"
                    )
            except (json.JSONDecodeError, TypeError):
                pass  # malformed options — skip validation

        elif ftype == "json":
            if isinstance(value, str):
                try:
                    json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    errors.append(
                        f"Custom field '{fname}' must be valid JSON"
                    )

        elif ftype == "link" and fdef.get("field_options"):
            # field_options = {"table": "some_table"} — existence check
            try:
                options = json.loads(fdef["field_options"])
                target_table = options.get("table")
                if target_table:
                    if not re.match(r'^[a-z][a-z0-9_]*$', target_table):
                        raise ValueError(f"Invalid table name: {target_table}")
                    exists = conn.execute(
                        f"SELECT 1 FROM [{target_table}] WHERE id = ?",
                        (value,),
                    ).fetchone()
                    if not exists:
                        errors.append(
                            f"Custom field '{fname}' references non-existent "
                            f"record in {target_table}"
                        )
            except (json.JSONDecodeError, TypeError):
                pass
            except Exception:
                # Table might not exist — skip validation rather than crash
                pass

    return errors


# ---------------------------------------------------------------------------
# Value storage (EAV)
# ---------------------------------------------------------------------------

def store_custom_field_values(conn, table_name, doc_id, values):
    """Store custom field values for a document.

    Uses INSERT ... ON CONFLICT to upsert values.

    Args:
        conn: database connection
        table_name: the doctype/table
        doc_id: the document's primary key (UUID)
        values: dict of {field_name: value}
    """
    for field_name, value in values.items():
        conn.execute(
            """INSERT INTO custom_field_value (table_name, doc_id, field_name, value)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(table_name, doc_id, field_name)
               DO UPDATE SET value = excluded.value""",
            (
                table_name,
                doc_id,
                field_name,
                str(value) if value is not None else None,
            ),
        )


def fetch_custom_field_values(conn, table_name, doc_id):
    """Fetch all custom field values for a document.

    Args:
        conn: database connection
        table_name: the doctype/table
        doc_id: the document's primary key (UUID)

    Returns:
        dict of {field_name: value}
    """
    rows = conn.execute(
        "SELECT field_name, value FROM custom_field_value "
        "WHERE table_name = ? AND doc_id = ?",
        (table_name, doc_id),
    ).fetchall()
    return {r["field_name"]: r["value"] for r in rows}


def delete_custom_field_values(conn, table_name, doc_id):
    """Delete all custom field values for a document.

    Useful when the parent document is deleted.

    Args:
        conn: database connection
        table_name: the doctype/table
        doc_id: the document's primary key (UUID)
    """
    conn.execute(
        "DELETE FROM custom_field_value WHERE table_name = ? AND doc_id = ?",
        (table_name, doc_id),
    )


def apply_defaults(conn, table_name, values):
    """Fill in default values for any custom fields not already provided.

    Args:
        conn: database connection
        table_name: the doctype/table
        values: dict of {field_name: value} — modified in-place

    Returns:
        the (possibly augmented) values dict
    """
    for fdef in get_custom_fields(conn, table_name):
        fname = fdef["field_name"]
        if fname not in values and fdef["default_value"] is not None:
            values[fname] = fdef["default_value"]
    return values
