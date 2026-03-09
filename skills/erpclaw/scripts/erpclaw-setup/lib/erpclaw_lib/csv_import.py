"""CSV import framework for bulk data loading.

Provides validation, parsing, and bulk insert utilities for importing
items, customers, suppliers, accounts, and opening balances from CSV files.

Functions:
- validate_csv: Check CSV structure against a schema
- parse_csv_rows: Parse and clean CSV rows
- bulk_insert: Insert rows into a table in batches
"""
import csv
import os
import re
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation

_SAFE_NAME = re.compile(r'^[a-z][a-z0-9_]*$')


# ---------------------------------------------------------------------------
# Schema definitions for importable entities
# ---------------------------------------------------------------------------

SCHEMAS = {
    "item": {
        "required": ["item_code", "name", "uom"],
        "optional": ["group", "valuation_method", "description",
                      "default_warehouse", "opening_stock", "opening_rate"],
        "defaults": {"valuation_method": "fifo", "uom": "Nos"},
    },
    "customer": {
        "required": ["name"],
        "optional": ["customer_type", "territory", "default_currency",
                      "email", "phone", "tax_id"],
        "defaults": {"customer_type": "Company", "default_currency": "USD"},
    },
    "supplier": {
        "required": ["name"],
        "optional": ["supplier_type", "country", "default_currency",
                      "email", "phone", "tax_id"],
        "defaults": {"supplier_type": "Company", "default_currency": "USD"},
    },
    "account": {
        "required": ["name", "root_type"],
        "optional": ["account_number", "account_type", "parent_name",
                      "currency", "is_group"],
        "defaults": {"currency": "USD", "is_group": "0"},
    },
    "opening_balance": {
        "required": ["account_number", "debit", "credit"],
        "optional": ["party_type", "party_name"],
        "defaults": {},
    },
}


def validate_csv(file_path, entity_type):
    """Validate a CSV file against a schema.

    Args:
        file_path: Path to the CSV file
        entity_type: One of the SCHEMAS keys

    Returns:
        List of error strings. Empty = valid.
    """
    errors = []

    if entity_type not in SCHEMAS:
        return [f"Unknown entity type: {entity_type}"]

    schema = SCHEMAS[entity_type]

    if not os.path.exists(file_path):
        return [f"File not found: {file_path}"]

    try:
        with open(file_path, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []

            # Check required columns
            for col in schema["required"]:
                if col not in headers:
                    errors.append(f"Missing required column: {col}")

            if errors:
                return errors

            # Validate rows
            for i, row in enumerate(reader, start=2):
                for col in schema["required"]:
                    val = (row.get(col) or "").strip()
                    if not val:
                        errors.append(f"Row {i}: missing required value for '{col}'")

                # Validate decimal fields
                if entity_type == "opening_balance":
                    for field in ("debit", "credit"):
                        val = (row.get(field) or "0").strip()
                        try:
                            Decimal(val)
                        except InvalidOperation:
                            errors.append(f"Row {i}: invalid number for '{field}': {val}")

    except Exception as e:
        errors.append(f"Failed to read CSV: {e}")

    return errors


def parse_csv_rows(file_path, entity_type):
    """Parse a CSV file and return cleaned rows with defaults applied.

    Args:
        file_path: Path to the CSV file
        entity_type: One of the SCHEMAS keys

    Returns:
        List of dicts, each representing a row with defaults applied.
    """
    schema = SCHEMAS[entity_type]
    all_cols = schema["required"] + schema["optional"]
    defaults = schema.get("defaults", {})
    rows = []

    with open(file_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {}
            for col in all_cols:
                val = (row.get(col) or "").strip()
                if not val and col in defaults:
                    val = defaults[col]
                if val:
                    cleaned[col] = val
            rows.append(cleaned)

    return rows


def bulk_insert(conn, table, columns, rows, batch_size=100,
                id_column="id", generate_ids=True):
    """Insert rows into a table in batches.

    Args:
        conn: SQLite connection (caller owns transaction)
        table: Table name
        columns: List of column names
        rows: List of dicts with column values
        batch_size: Rows per batch
        id_column: Name of the ID column
        generate_ids: Whether to auto-generate UUIDs for id_column

    Returns:
        Number of rows inserted.
    """
    if not rows:
        return 0

    if generate_ids and id_column not in columns:
        columns = [id_column] + list(columns)

    if not _SAFE_NAME.match(table):
        raise ValueError(f"Invalid table name: {table}")
    for col in columns:
        if not _SAFE_NAME.match(col):
            raise ValueError(f"Invalid column name: {col}")

    placeholders = ", ".join(["?"] * len(columns))
    col_names = ", ".join(columns)
    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

    count = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        for row in batch:
            values = []
            for col in columns:
                if col == id_column and generate_ids:
                    values.append(str(uuid.uuid4()))
                else:
                    values.append(row.get(col))
            conn.execute(sql, values)
            count += 1

    return count
