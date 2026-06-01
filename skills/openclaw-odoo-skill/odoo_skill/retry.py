"""
Retry decorator with exponential backoff for Odoo API calls.

Retries only on transient connection errors. Access and validation
errors are re-raised immediately since retrying won't help.
"""

import time
import logging
import xmlrpc.client
from functools import wraps
from typing import Callable, TypeVar, Any

from .errors import (
    OdooConnectionError,
    OdooError,
    classify_error,
)

logger = logging.getLogger("odoo_skill")

F = TypeVar("F", bound=Callable[..., Any])


# Exceptions that indicate a transient/network issue worth retrying
_RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    ConnectionResetError,
    ConnectionRefusedError,
    ConnectionAbortedError,
    TimeoutError,
    OSError,
    xmlrpc.client.ProtocolError,
)


def retry_on_connection_error(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
) -> Callable[[F], F]:
    """Decorator: retry a function on transient connection errors.

    Uses exponential backoff between retries. Non-retryable errors
    (access denied, validation) are raised immediately.

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Maximum delay between retries (caps the backoff).
        backoff_factor: Multiplier applied to the delay after each retry.

    Returns:
        Decorated function with retry behaviour.

    Example::

        @retry_on_connection_error(max_retries=3)
        def fetch_partners(client):
            return client.search_read('res.partner', [], fields=['name'])
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except _RETRYABLE_EXCEPTIONS as exc:
                    last_exception = exc

                    if attempt < max_retries:
                        delay = min(
                            base_delay * (backoff_factor ** attempt),
                            max_delay,
                        )
                        logger.warning(
                            "Odoo connection error (attempt %d/%d): %s — "
                            "retrying in %.1fs…",
                            attempt + 1,
                            max_retries,
                            exc,
                            delay,
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            "Odoo connection failed after %d attempts: %s",
                            max_retries,
                            exc,
                        )
                        raise OdooConnectionError(
                            f"Failed after {max_retries} retries: {exc}"
                        ) from exc

                except xmlrpc.client.Fault as exc:
                    # Non-retryable Odoo fault — classify and re-raise
                    raise classify_error(exc) from exc

            # Should never reach here, but just in case
            raise OdooConnectionError(
                f"Failed after {max_retries} retries: {last_exception}"
            )

        return wrapper  # type: ignore[return-value]

    return decorator
