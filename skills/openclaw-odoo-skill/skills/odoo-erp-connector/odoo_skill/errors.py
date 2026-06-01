"""
Odoo error classes and XML-RPC fault classification.

Provides a hierarchy of exception types that map to Odoo's error categories,
plus a classifier that converts raw XML-RPC faults into the correct type.
"""

import xmlrpc.client
import logging
from typing import Union

logger = logging.getLogger("odoo_skill")


class OdooError(Exception):
    """Base exception for all Odoo-related errors."""

    def __init__(self, message: str, fault_code: int = 0, model: str = "", method: str = ""):
        self.fault_code = fault_code
        self.model = model
        self.method = method
        super().__init__(message)


class OdooConnectionError(OdooError):
    """Network/connection errors — retryable.

    Raised when the Odoo server is unreachable, the connection times out,
    or an XML-RPC protocol error occurs.
    """
    pass


class OdooAuthenticationError(OdooError):
    """Authentication failures — credentials invalid.

    Raised when the API key, username, or database name is incorrect.
    """
    pass


class OdooAccessError(OdooError):
    """Permission/access denied — NOT retryable.

    Raised when the authenticated user lacks the required permissions
    for the attempted operation.
    """
    pass


class OdooValidationError(OdooError):
    """Data validation errors — NOT retryable without fixing the data.

    Raised when Odoo rejects the data due to constraints, required fields,
    or business rule violations.
    """
    pass


class OdooRecordNotFoundError(OdooError):
    """Record does not exist or has been deleted.

    Raised when attempting to read/write/unlink a record that doesn't exist.
    """
    pass


def classify_error(
    exc: Exception,
    model: str = "",
    method: str = "",
) -> OdooError:
    """Classify a raw exception into the appropriate OdooError subclass.

    Examines the fault string from XML-RPC faults and maps known Odoo
    error patterns to our exception hierarchy. Network-level exceptions
    are mapped to OdooConnectionError.

    Args:
        exc: The original exception.
        model: The Odoo model being accessed (for error context).
        method: The Odoo method being called (for error context).

    Returns:
        An OdooError subclass instance with the original message preserved.
    """
    msg = str(exc)

    # XML-RPC faults contain Odoo's internal error type in faultString
    if isinstance(exc, xmlrpc.client.Fault):
        fault_string = exc.faultString or ""
        fault_code = exc.faultCode

        if "AccessDenied" in fault_string:
            return OdooAuthenticationError(
                f"Authentication failed: {fault_string}",
                fault_code=fault_code, model=model, method=method,
            )

        if "AccessError" in fault_string:
            return OdooAccessError(
                f"Permission denied on {model}.{method}: {fault_string}",
                fault_code=fault_code, model=model, method=method,
            )

        if "ValidationError" in fault_string or "UserError" in fault_string:
            return OdooValidationError(
                f"Validation error on {model}.{method}: {fault_string}",
                fault_code=fault_code, model=model, method=method,
            )

        if "MissingError" in fault_string:
            return OdooRecordNotFoundError(
                f"Record not found in {model}: {fault_string}",
                fault_code=fault_code, model=model, method=method,
            )

        # Generic fault
        return OdooError(
            f"Odoo error on {model}.{method}: {fault_string}",
            fault_code=fault_code, model=model, method=method,
        )

    # Network-level errors
    if isinstance(exc, xmlrpc.client.ProtocolError):
        return OdooConnectionError(
            f"Protocol error ({exc.errcode}): {exc.errmsg}",
            model=model, method=method,
        )

    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return OdooConnectionError(
            f"Connection error: {msg}",
            model=model, method=method,
        )

    # Fallback
    return OdooError(
        f"Unexpected error on {model}.{method}: {msg}",
        model=model, method=method,
    )
