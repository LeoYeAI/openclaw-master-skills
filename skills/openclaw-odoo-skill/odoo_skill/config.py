"""
Configuration management for the Odoo skill.

Loads connection settings from environment variables first, then falls
back to a config.json file. Validates that all required fields are present
before the client tries to connect.
"""

import json
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("odoo_skill")

# Resolve paths relative to the project root (one level up from odoo_skill/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config.json"


@dataclass
class OdooConfig:
    """Odoo connection configuration.

    Attributes:
        url: Base URL of the Odoo instance (e.g. ``https://mycompany.odoo.com``).
        db: Database name.
        username: Login username (email).
        api_key: API key (replaces password for Odoo 14+).
        timeout: Socket timeout in seconds for XML-RPC calls.
        max_retries: Number of retry attempts on connection failure.
        poll_interval: Seconds between change-detection polls.
        log_level: Logging level name (DEBUG, INFO, WARNING, …).
        webhook_port: Port for the inbound webhook HTTP server.
        webhook_secret: HMAC secret for verifying webhook signatures.
    """

    url: str = ""
    db: str = ""
    username: str = ""
    api_key: str = ""
    timeout: int = 60
    max_retries: int = 3
    poll_interval: int = 60
    log_level: str = "INFO"
    webhook_port: int = 8069
    webhook_secret: str = ""

    # ── Validation ────────────────────────────────────────────────────

    def validate(self) -> list[str]:
        """Check that all required fields are populated.

        Returns:
            A list of human-readable error strings (empty == valid).
        """
        errors: list[str] = []

        if not self.url:
            errors.append("ODOO_URL is required (e.g. https://mycompany.odoo.com)")
        elif not self.url.startswith(("http://", "https://")):
            errors.append(f"ODOO_URL must start with http:// or https:// (got '{self.url}')")

        if not self.db:
            errors.append("ODOO_DB is required (the Odoo database name)")

        if not self.username:
            errors.append("ODOO_USERNAME is required (the API user login/email)")

        if not self.api_key:
            errors.append("ODOO_API_KEY is required (generate in Odoo → Preferences → Account Security)")

        return errors

    @property
    def is_valid(self) -> bool:
        return len(self.validate()) == 0


def load_config(config_path: Optional[str] = None) -> OdooConfig:
    """Load configuration from environment variables with config.json fallback.

    **Priority order** (highest → lowest):
    1. Environment variables (``ODOO_URL``, ``ODOO_DB``, etc.)
    2. Values in the JSON config file
    3. Defaults defined in :class:`OdooConfig`

    Args:
        config_path: Path to a JSON config file. Defaults to
            ``<project_root>/config.json``.

    Returns:
        A validated :class:`OdooConfig` instance.

    Raises:
        ValueError: If required configuration fields are missing.
    """
    file_values: dict = {}
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH

    # ── Load config file (if it exists) ──────────────────────────────
    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as fh:
                file_values = json.load(fh)
            logger.debug("Loaded config from %s", path)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read config file %s: %s", path, exc)

    # ── Merge: env vars take precedence over file values ─────────────
    config = OdooConfig(
        url=os.environ.get("ODOO_URL", file_values.get("url", "")).rstrip("/"),
        db=os.environ.get("ODOO_DB", file_values.get("db", "")),
        username=os.environ.get("ODOO_USERNAME", file_values.get("username", "")),
        api_key=os.environ.get("ODOO_API_KEY", file_values.get("api_key", "")),
        timeout=int(os.environ.get("ODOO_TIMEOUT", file_values.get("timeout", 60))),
        max_retries=int(os.environ.get("ODOO_MAX_RETRIES", file_values.get("max_retries", 3))),
        poll_interval=int(os.environ.get("ODOO_POLL_INTERVAL", file_values.get("poll_interval", 60))),
        log_level=os.environ.get("ODOO_LOG_LEVEL", file_values.get("log_level", "INFO")),
        webhook_port=int(os.environ.get("ODOO_WEBHOOK_PORT", file_values.get("webhook_port", 8069))),
        webhook_secret=os.environ.get("ODOO_WEBHOOK_SECRET", file_values.get("webhook_secret", "")),
    )

    # ── Validate ─────────────────────────────────────────────────────
    errors = config.validate()
    if errors:
        for err in errors:
            logger.error("Config error: %s", err)
        raise ValueError(
            "Odoo configuration is incomplete:\n  • " + "\n  • ".join(errors)
        )

    # ── Apply log level ──────────────────────────────────────────────
    logging.getLogger("odoo_skill").setLevel(getattr(logging, config.log_level, logging.INFO))

    logger.info(
        "Odoo config loaded — url=%s  db=%s  user=%s  timeout=%ds",
        config.url, config.db, config.username, config.timeout,
    )
    return config
