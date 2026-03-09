"""Standard pagination helper for ERPClaw list actions.

Provides a consistent paginate() function that all list-* actions
can use instead of implementing their own LIMIT/OFFSET logic.

Usage:
    from erpclaw_lib.pagination import paginate

    result = paginate(
        conn,
        "SELECT * FROM customer WHERE company_id = ?",
        (company_id,),
        page=args.page,
        page_size=args.page_size,
    )
    # result = {"items": [...], "total": 150, "page": 1, "page_size": 50, "pages": 3}
"""
import math


def paginate(
    conn,
    query: str,
    params: tuple = (),
    page: int = 1,
    page_size: int = 50,
    order_by: str = "",
) -> dict:
    """Execute a paginated query.

    Args:
        conn: SQLite connection with row_factory=sqlite3.Row.
        query: Base SELECT query (without LIMIT/OFFSET).
        params: Query parameters tuple.
        page: Page number (1-indexed). Defaults to 1.
        page_size: Items per page. Defaults to 50. Max 500.
        order_by: Optional ORDER BY clause (e.g. "created_at DESC").
                  Appended to the query if provided.

    Returns:
        {
            "items": [dict, ...],
            "total": int,
            "page": int,
            "page_size": int,
            "pages": int,
        }
    """
    # Sanitize inputs
    page = max(1, int(page) if page else 1)
    page_size = max(1, min(500, int(page_size) if page_size else 50))

    # Count total rows
    count_query = f"SELECT COUNT(*) as cnt FROM ({query})"
    count_row = conn.execute(count_query, params).fetchone()
    total = count_row["cnt"] if isinstance(count_row, dict) else count_row[0]

    # Calculate pagination
    pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    # Build paginated query
    paginated = query
    if order_by:
        paginated += f" ORDER BY {order_by}"
    paginated += " LIMIT ? OFFSET ?"

    rows = conn.execute(paginated, params + (page_size, offset)).fetchall()
    items = [dict(r) for r in rows] if rows else []

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
