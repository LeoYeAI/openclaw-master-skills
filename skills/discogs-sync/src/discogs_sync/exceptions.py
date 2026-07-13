"""Custom exceptions for discogs-sync."""


class DiscogsSyncError(Exception):
    """Base exception for discogs-sync."""


class AuthenticationError(DiscogsSyncError):
    """Authentication failed or tokens are invalid."""


class ConfigError(DiscogsSyncError):
    """Configuration file is missing or invalid."""


class ParseError(DiscogsSyncError):
    """Input file parsing failed."""

    def __init__(self, message: str, errors: list[dict] | None = None):
        super().__init__(message)
        self.errors = errors or []


class SearchError(DiscogsSyncError):
    """Release search failed."""


class SyncError(DiscogsSyncError):
    """Sync operation failed."""


class RateLimitError(DiscogsSyncError):
    """Rate limit exceeded and retries exhausted."""


class NetworkError(DiscogsSyncError):
    """Network request failed after retries."""
