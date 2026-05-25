"""Common database query helpers for ERPClaw skills.

Centralises frequently duplicated lookups (fiscal year, cost center, company
auto-detection) so that every skill uses the same logic and query shape.
"""
import json
import sys


def resolve_company_id(conn, company_id: str | None = None) -> str:
    """Return company_id if provided, otherwise auto-detect from DB.

    When only one company exists, it is returned automatically so that
    users never have to specify ``--company-id`` in single-company setups.
    When multiple companies exist and none was specified, a helpful error
    listing the available companies is emitted.

    Args:
        conn: SQLite connection with row_factory = sqlite3.Row.
        company_id: Explicitly provided company ID (may be None/empty).

    Returns:
        A valid company UUID string.

    Raises:
        SystemExit: via JSON error on stdout if no company found or
        multiple companies exist without explicit selection.
    """
    if company_id:
        return company_id

    rows = conn.execute("SELECT id, name FROM company ORDER BY name LIMIT 10").fetchall()
    if not rows:
        print(json.dumps({"error": "No company found. Create one first.",
                          "suggestion": "Run 'tutorial' to create a demo company, or 'setup company' to create your own."}))
        sys.exit(1)
    if len(rows) == 1:
        return rows[0]["id"]
    # Multiple companies — tell user which ones exist
    companies = [{"id": r["id"], "name": r["name"]} for r in rows]
    print(json.dumps({"error": "Multiple companies found. Please specify --company-id.",
                      "companies": companies,
                      "suggestion": "Use --company-id with one of the IDs above."}))
    sys.exit(1)


def get_fiscal_year(conn, posting_date: str) -> str | None:
    """Return the fiscal year name for a posting date, or None.

    Looks for an open fiscal year whose date range covers *posting_date*.

    Args:
        conn: SQLite connection with row_factory = sqlite3.Row.
        posting_date: ISO 8601 date string (YYYY-MM-DD).

    Returns:
        The fiscal year ``name`` string, or ``None`` if no matching open
        fiscal year exists.
    """
    fy = conn.execute(
        "SELECT name FROM fiscal_year WHERE start_date <= ? AND end_date >= ? AND is_closed = 0",
        (posting_date, posting_date),
    ).fetchone()
    return fy["name"] if fy else None


def get_default_cost_center(conn, company_id: str) -> str | None:
    """Return the first non-group cost center ID for a company, or None.

    Args:
        conn: SQLite connection with row_factory = sqlite3.Row.
        company_id: UUID of the company.

    Returns:
        The cost center ``id`` string, or ``None`` if no leaf cost centre
        exists for the company.
    """
    cc = conn.execute(
        "SELECT id FROM cost_center WHERE company_id = ? AND is_group = 0 LIMIT 1",
        (company_id,),
    ).fetchone()
    return cc["id"] if cc else None
