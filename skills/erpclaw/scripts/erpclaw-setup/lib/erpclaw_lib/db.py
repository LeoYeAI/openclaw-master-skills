"""Database connection helper for ERPClaw.

Provides a standard way to get a SQLite connection with the correct
PRAGMAs (WAL mode, FK enforcement, busy timeout) applied.
"""
import os
import sqlite3
import stat
from decimal import Decimal


DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")


class _DecimalSum:
    """Custom SQLite aggregate: SUM using Python Decimal for precision.

    SQLite's built-in SUM uses IEEE 754 float, which can lose precision
    on financial amounts stored as TEXT. This aggregate sums values using
    Python's Decimal type and returns the result as TEXT.

    Usage in SQL: decimal_sum(column) instead of SUM(CAST(column AS REAL))
    """

    def __init__(self):
        self.total = Decimal("0")

    def step(self, value):
        if value is not None:
            self.total += Decimal(str(value))

    def finalize(self):
        return str(self.total)


class ConnectionWrapper:
    """Wrapper around sqlite3.Connection that allows setting custom attributes.

    Python 3.12+ disallows setting arbitrary attributes on sqlite3.Connection.
    This wrapper delegates all sqlite3 methods to the underlying connection
    while allowing custom attributes (e.g., conn.company_id) that ERPClaw
    skills use for naming series resolution.
    """

    def __init__(self, conn: sqlite3.Connection):
        object.__setattr__(self, "_conn", conn)

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def __setattr__(self, name, value):
        try:
            setattr(self._conn, name, value)
        except AttributeError:
            object.__setattr__(self, name, value)

    def __enter__(self):
        self._conn.__enter__()
        return self

    def __exit__(self, *args):
        return self._conn.__exit__(*args)

    def __call__(self, *args, **kwargs):
        return self._conn(*args, **kwargs)


def get_connection(db_path=None) -> "ConnectionWrapper":
    """Get a SQLite connection with ERPClaw standard PRAGMAs.

    Creates the parent directory if it doesn't exist.
    Applies:
      - PRAGMA journal_mode=WAL  (concurrent reads during writes)
      - PRAGMA foreign_keys=ON   (enforce FK constraints)
      - PRAGMA busy_timeout=5000 (wait 5s on lock contention)

    Args:
        db_path: Path to the SQLite database file.
                 Defaults to ~/.openclaw/erpclaw/data.sqlite.
                 Also checks ERPCLAW_DB_PATH environment variable.

    Returns:
        ConnectionWrapper around sqlite3.Connection with row_factory=sqlite3.Row.
    """
    path = db_path or os.environ.get("ERPCLAW_DB_PATH", DEFAULT_DB_PATH)
    ensure_db_exists(path)
    is_new = not os.path.exists(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.create_aggregate("decimal_sum", 1, _DecimalSum)
    if is_new:
        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
        except OSError:
            pass  # non-fatal on some platforms
    return ConnectionWrapper(conn)


def ensure_db_exists(db_path=None) -> str:
    """Ensure the database directory exists.

    Creates parent directories if needed. Does not create the DB file
    itself — sqlite3.connect() handles that.

    Args:
        db_path: Path to the database file.

    Returns:
        The resolved database path.
    """
    path = db_path or DEFAULT_DB_PATH
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return path
