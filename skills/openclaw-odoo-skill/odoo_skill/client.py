"""
OdooClient — thread-safe XML-RPC wrapper with connection pooling and retry.

This is the low-level layer that every model operation module uses.
It handles authentication, timeout, field caching, and translates raw
XML-RPC faults into our custom exception hierarchy.
"""

import logging
import socket
import xmlrpc.client
from typing import Any, Optional

from .config import OdooConfig, load_config
from .errors import (
    OdooAuthenticationError,
    OdooConnectionError,
    OdooError,
    classify_error,
)
from .retry import retry_on_connection_error

logger = logging.getLogger("odoo_skill")


class OdooClient:
    """Thread-safe Odoo XML-RPC client.

    Usage::

        client = OdooClient.from_env()           # env vars / config.json
        client = OdooClient(config=my_config)     # explicit config object
        info = client.authenticate()              # test + cache uid
        partners = client.search_read('res.partner', [['is_company', '=', True]],
                                       fields=['name', 'email'], limit=10)
    """

    def __init__(self, config: Optional[OdooConfig] = None):
        """Initialise the client.

        Args:
            config: An :class:`OdooConfig` instance.  If *None*, configuration
                is loaded from env vars / config.json via :func:`load_config`.
        """
        self.config = config or load_config()

        self._uid: Optional[int] = None
        self._common: Optional[xmlrpc.client.ServerProxy] = None
        self._models: Optional[xmlrpc.client.ServerProxy] = None
        self._fields_cache: dict[str, dict] = {}

        # Apply socket timeout globally for xmlrpc.client
        socket.setdefaulttimeout(self.config.timeout)

    # ── Factory ──────────────────────────────────────────────────────

    @classmethod
    def from_env(cls) -> "OdooClient":
        """Create a client loading config from environment / config.json."""
        return cls(config=load_config())

    @classmethod
    def from_values(
        cls,
        url: str,
        db: str,
        username: str,
        api_key: str,
        **kwargs: Any,
    ) -> "OdooClient":
        """Create a client from explicit connection values."""
        cfg = OdooConfig(
            url=url.rstrip("/"),
            db=db,
            username=username,
            api_key=api_key,
            **kwargs,
        )
        errors = cfg.validate()
        if errors:
            raise ValueError("\n".join(errors))
        return cls(config=cfg)

    # ── Lazy XML-RPC proxies ─────────────────────────────────────────

    @property
    def common(self) -> xmlrpc.client.ServerProxy:
        """``/xmlrpc/2/common`` endpoint (lazy, cached)."""
        if self._common is None:
            self._common = xmlrpc.client.ServerProxy(
                f"{self.config.url}/xmlrpc/2/common",
                allow_none=True,
            )
        return self._common

    @property
    def models(self) -> xmlrpc.client.ServerProxy:
        """``/xmlrpc/2/object`` endpoint (lazy, cached)."""
        if self._models is None:
            self._models = xmlrpc.client.ServerProxy(
                f"{self.config.url}/xmlrpc/2/object",
                allow_none=True,
            )
        return self._models

    @property
    def uid(self) -> int:
        """Authenticated user ID (lazy — authenticates on first access)."""
        if self._uid is None:
            self.authenticate()
        return self._uid  # type: ignore[return-value]

    # ── Authentication ───────────────────────────────────────────────

    @retry_on_connection_error(max_retries=2, base_delay=2.0)
    def authenticate(self) -> int:
        """Authenticate against Odoo and cache the user ID.

        Returns:
            The authenticated user's ID (``uid``).

        Raises:
            OdooAuthenticationError: If credentials are rejected.
            OdooConnectionError: If the server is unreachable.
        """
        logger.debug("Authenticating as %s on %s/%s …",
                      self.config.username, self.config.url, self.config.db)
        try:
            uid = self.common.authenticate(
                self.config.db,
                self.config.username,
                self.config.api_key,
                {},
            )
        except xmlrpc.client.Fault as exc:
            raise classify_error(exc, method="authenticate") from exc

        if not uid:
            raise OdooAuthenticationError(
                "Authentication failed — check ODOO_URL, ODOO_DB, ODOO_USERNAME, and ODOO_API_KEY."
            )

        self._uid = uid
        logger.info("Authenticated as uid=%d on %s", uid, self.config.db)
        return uid

    # ── Generic execute ──────────────────────────────────────────────

    @retry_on_connection_error()
    def execute(
        self,
        model: str,
        method: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute an Odoo RPC method.

        Wraps ``execute_kw`` on the ``/xmlrpc/2/object`` endpoint.

        Args:
            model: Odoo model name (e.g. ``res.partner``).
            method: Model method name (e.g. ``search_read``).
            *args: Positional arguments forwarded to the method.
            **kwargs: Keyword arguments forwarded to the method.

        Returns:
            Whatever the Odoo method returns.

        Raises:
            OdooError (or subclass): On any Odoo-side error.
            OdooConnectionError: On network failure after retries.
        """
        try:
            return self.models.execute_kw(
                self.config.db,
                self.uid,
                self.config.api_key,
                model,
                method,
                list(args),
                kwargs if kwargs else {},
            )
        except xmlrpc.client.Fault as exc:
            raise classify_error(exc, model=model, method=method) from exc

    # ── Convenience wrappers ─────────────────────────────────────────

    def search(
        self,
        model: str,
        domain: list | None = None,
        limit: int = 0,
        offset: int = 0,
        order: str = "",
    ) -> list[int]:
        """Search for record IDs matching *domain*.

        Args:
            model: Odoo model name.
            domain: Odoo domain filter (default: ``[]``).
            limit: Max results (0 = unlimited).
            offset: Number of records to skip.
            order: Sort clause (e.g. ``'name asc'``).

        Returns:
            List of matching record IDs.
        """
        kwargs: dict[str, Any] = {}
        if limit:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset
        if order:
            kwargs["order"] = order
        return self.execute(model, "search", domain or [], **kwargs)

    def read(
        self,
        model: str,
        ids: int | list[int],
        fields: list[str] | None = None,
    ) -> list[dict]:
        """Read specific records by ID.

        Args:
            model: Odoo model name.
            ids: Single ID or list of IDs.
            fields: Fields to return (default: all).

        Returns:
            List of record dicts.
        """
        if isinstance(ids, int):
            ids = [ids]
        kwargs: dict[str, Any] = {}
        if fields:
            kwargs["fields"] = fields
        return self.execute(model, "read", ids, **kwargs)

    def search_read(
        self,
        model: str,
        domain: list | None = None,
        fields: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
        order: str = "",
    ) -> list[dict]:
        """Search and read in a single call (most common operation).

        Args:
            model: Odoo model name.
            domain: Odoo domain filter.
            fields: Fields to return.
            limit: Max records.
            offset: Records to skip.
            order: Sort clause.

        Returns:
            List of record dicts.
        """
        kwargs: dict[str, Any] = {"limit": limit}
        if fields:
            kwargs["fields"] = fields
        if offset:
            kwargs["offset"] = offset
        if order:
            kwargs["order"] = order
        return self.execute(model, "search_read", domain or [], **kwargs)

    def create(self, model: str, values: dict) -> int:
        """Create a record.

        Args:
            model: Odoo model name.
            values: Field values for the new record.

        Returns:
            The new record's ID.
        """
        return self.execute(model, "create", values)

    def write(self, model: str, ids: int | list[int], values: dict) -> bool:
        """Update existing records.

        Args:
            model: Odoo model name.
            ids: Single ID or list of IDs to update.
            values: Field values to set.

        Returns:
            ``True`` on success.
        """
        if isinstance(ids, int):
            ids = [ids]
        return self.execute(model, "write", ids, values)

    def unlink(self, model: str, ids: int | list[int]) -> bool:
        """Delete records.

        Args:
            model: Odoo model name.
            ids: Single ID or list of IDs to delete.

        Returns:
            ``True`` on success.
        """
        if isinstance(ids, int):
            ids = [ids]
        return self.execute(model, "unlink", ids)

    def search_count(self, model: str, domain: list | None = None) -> int:
        """Count records matching *domain*.

        Args:
            model: Odoo model name.
            domain: Odoo domain filter.

        Returns:
            Number of matching records.
        """
        return self.execute(model, "search_count", domain or [])

    def fields_get(
        self,
        model: str,
        attributes: list[str] | None = None,
    ) -> dict:
        """Retrieve field metadata for a model (cached).

        Args:
            model: Odoo model name.
            attributes: Metadata attributes to include
                (default: ``['string', 'type', 'required', 'help']``).

        Returns:
            Dict mapping field names to their metadata.
        """
        cache_key = f"{model}:{','.join(sorted(attributes or []))}"
        if cache_key not in self._fields_cache:
            attrs = attributes or ["string", "type", "required", "help"]
            self._fields_cache[cache_key] = self.execute(
                model, "fields_get", [], attributes=attrs,
            )
        return self._fields_cache[cache_key]

    # ── Diagnostics ──────────────────────────────────────────────────

    def version(self) -> dict:
        """Get the Odoo server version info (no auth required)."""
        return self.common.version()

    def test_connection(self) -> dict:
        """Test the connection and return a status summary.

        Returns:
            Dict with ``status``, ``server_version``, ``uid``, ``database``, ``url``.
        """
        try:
            ver = self.version()
            uid = self.uid
            return {
                "status": "connected",
                "server_version": ver.get("server_version", "unknown"),
                "uid": uid,
                "database": self.config.db,
                "url": self.config.url,
            }
        except Exception as exc:
            logger.error("Connection test failed: %s", exc)
            return {
                "status": "error",
                "message": str(exc),
                "url": self.config.url,
                "database": self.config.db,
            }

    def __repr__(self) -> str:
        return (
            f"OdooClient(url={self.config.url!r}, db={self.config.db!r}, "
            f"user={self.config.username!r}, uid={self._uid})"
        )
