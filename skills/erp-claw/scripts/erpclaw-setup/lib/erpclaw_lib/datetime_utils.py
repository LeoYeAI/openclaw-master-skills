"""Date and time utilities for ERPClaw skills."""
from datetime import date, datetime, timezone


def today_utc() -> str:
    """Return today's date as ISO 8601 string (YYYY-MM-DD)."""
    return date.today().isoformat()


def now_utc() -> str:
    """Return current UTC datetime as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()
