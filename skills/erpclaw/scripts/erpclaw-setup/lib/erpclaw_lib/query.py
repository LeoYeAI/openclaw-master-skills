"""
ERPClaw Query Builder — convenience layer on top of vendored PyPika.

Usage:
    from erpclaw_lib.query import Q, Table, Field, Case, fn, P
    from erpclaw_lib.query import DecimalSum, DecimalAbs

    # Build a parameterized query
    t = Table('company')
    q = Q.from_(t).select(t.star).where(t.id == P())
    sql = q.get_sql()       # SELECT * FROM "company" WHERE "id"=?
    params = ['company-id']  # You still manage params separately

    # Financial queries use DecimalSum (not SUM) for Decimal precision
    gl = Table('gl_entry')
    q = Q.from_(gl).select(gl.account, DecimalSum(gl.debit).as_('total_debit'))

Notes:
    - Q = SQLLiteQuery (SQLite dialect, our default)
    - P = QmarkParameter (returns ? placeholder)
    - fn = PyPika functions module (fn.Sum, fn.Count, fn.Coalesce, etc.)
    - DecimalSum wraps our custom decimal_sum() SQLite aggregate
    - DecimalAbs wraps our custom decimal_abs() SQLite aggregate
    - All generated SQL uses double-quoted identifiers (PyPika default)
    - PyPika does NOT manage parameter values — you pass params separately
      to conn.execute(sql, params)
"""

from erpclaw_lib.vendor.pypika import (
    SQLLiteQuery,
    Query,
    Table,
    Field,
    Case,
    Order,
    Criterion,
    CustomFunction,
    Not,
    NullValue,
    QmarkParameter,
)
from erpclaw_lib.vendor.pypika import fn
from erpclaw_lib.vendor.pypika.terms import Function, ValueWrapper, Star


# ── Aliases for brevity ──

Q = SQLLiteQuery
"""Default query builder — SQLite dialect."""

P = QmarkParameter
"""Parameterized placeholder — returns ? for SQLite."""

NULL = NullValue()


# ── Custom aggregate functions (registered in erpclaw_lib/db.py) ──

class DecimalSum(Function):
    """Wrapper for ERPClaw's custom decimal_sum() SQLite aggregate.

    Uses Python Decimal internally for exact financial arithmetic.
    Registered via db.get_connection() → conn.create_aggregate('decimal_sum', ...).
    """
    def __init__(self, term, alias=None):
        super().__init__("decimal_sum", term, alias=alias)


class DecimalAbs(Function):
    """Wrapper for ERPClaw's custom decimal_abs() SQLite function."""
    def __init__(self, term, alias=None):
        super().__init__("decimal_abs", term, alias=alias)


# ── Helper: build WHERE clause from dict ──

def where_eq(query, table, filters):
    """Apply equality filters from a dict.

    Usage:
        q = Q.from_(t).select(t.star)
        q = where_eq(q, t, {'company_id': P(), 'status': 'Active'})
        # → WHERE "company_id"=? AND "status"='Active'
    """
    for col, val in filters.items():
        q = query.where(Field(col) == val)
        query = q
    return query


# ── Helper: build INSERT with named columns ──

def insert_row(table_name, data):
    """Build INSERT INTO table (col1, col2, ...) VALUES (?, ?, ...).

    Args:
        table_name: str — table name
        data: dict — column: value mapping (values should be P() for params)

    Returns:
        tuple: (sql_string, column_names_in_order)

    Usage:
        sql, cols = insert_row('company', {
            'id': P(), 'name': P(), 'status': P()
        })
        conn.execute(sql, [uuid, name, status])
    """
    t = Table(table_name)
    q = Q.into(t).columns(*data.keys()).insert(*data.values())
    return q.get_sql(), list(data.keys())


# ── Helper: build UPDATE with named columns ──

def update_row(table_name, data, where):
    """Build UPDATE table SET col1=?, col2=? WHERE id=?.

    Args:
        table_name: str
        data: dict — column: value pairs to SET
        where: dict — column: value pairs for WHERE clause

    Returns:
        sql_string

    Usage:
        sql = update_row('company',
            data={'name': P(), 'updated_at': P()},
            where={'id': P()})
        conn.execute(sql, [new_name, now, company_id])
    """
    t = Table(table_name)
    q = Q.update(t)
    for col, val in data.items():
        q = q.set(Field(col), val)
    for col, val in where.items():
        q = q.where(Field(col) == val)
    return q.get_sql()


# ── Re-exports for clean imports ──

__all__ = [
    'Q', 'P', 'Query', 'Table', 'Field', 'Case', 'Order',
    'Criterion', 'CustomFunction', 'Not', 'NULL',
    'fn', 'Star', 'ValueWrapper',
    'DecimalSum', 'DecimalAbs',
    'where_eq', 'insert_row', 'update_row',
    'SQLLiteQuery', 'QmarkParameter',
]
