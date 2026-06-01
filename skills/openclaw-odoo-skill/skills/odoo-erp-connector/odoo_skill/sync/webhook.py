"""
Webhook receiver for inbound Odoo event notifications.

Provides a lightweight HTTP server (stdlib only — no Flask required)
that accepts POST requests from Odoo custom modules or automation
rules, verifies HMAC signatures, and routes events to callbacks.
"""

import hashlib
import hmac
import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Callable, Optional

logger = logging.getLogger("odoo_skill.webhook")

# Callback type: fn(event_type: str, payload: dict) -> None
WebhookCallback = Callable[[str, dict], None]


class _WebhookHandler(BaseHTTPRequestHandler):
    """Internal HTTP request handler for Odoo webhooks.

    Class-level attributes are set by :class:`OdooWebhookServer` before
    the server starts.
    """

    # Set by the server before starting
    webhook_secret: str = ""
    callbacks: dict[str, WebhookCallback] = {}
    default_callback: Optional[WebhookCallback] = None

    def do_POST(self) -> None:
        """Handle an incoming webhook POST request."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._respond(400, {"error": "Empty body"})
            return

        body = self.rfile.read(content_length)

        # ── Signature verification ───────────────────────────────
        if self.webhook_secret:
            signature = self.headers.get("X-Odoo-Signature", "")
            expected = hmac.new(
                self.webhook_secret.encode("utf-8"),
                body,
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                logger.warning("Webhook signature mismatch (remote=%s)", self.client_address[0])
                self._respond(401, {"error": "Invalid signature"})
                return

        # ── Parse and route ──────────────────────────────────────
        try:
            payload = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning("Webhook parse error: %s", exc)
            self._respond(400, {"error": "Invalid JSON"})
            return

        event_type = payload.get("event", payload.get("type", "unknown"))
        logger.info("Webhook received: event=%s from %s", event_type, self.client_address[0])

        # Dispatch to registered callback
        callback = self.callbacks.get(event_type, self.default_callback)
        if callback:
            try:
                callback(event_type, payload)
            except Exception:
                logger.exception("Webhook callback error for event=%s", event_type)
        else:
            logger.debug("No callback registered for event=%s", event_type)

        self._respond(200, {"status": "ok", "event": event_type})

    def do_GET(self) -> None:
        """Health-check endpoint."""
        self._respond(200, {
            "status": "ok",
            "service": "odoo-webhook-receiver",
            "registered_events": list(self.callbacks.keys()),
        })

    # ── Helpers ──────────────────────────────────────────────────

    def _respond(self, status: int, data: dict) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        """Redirect HTTP server log to our logger."""
        logger.debug(format, *args)


class OdooWebhookServer:
    """Manages a background HTTP server for receiving Odoo webhooks.

    Usage::

        server = OdooWebhookServer(port=8070, secret="my_shared_secret")
        server.on("partner.updated", handle_partner_update)
        server.on("order.confirmed", handle_order_confirmed)
        server.start()
        # …later…
        server.stop()

    Args:
        port: TCP port to bind (default 8069).
        host: Bind address (default ``0.0.0.0``).
        secret: HMAC secret for signature verification (optional but
            strongly recommended in production).
    """

    def __init__(
        self,
        port: int = 8069,
        host: str = "0.0.0.0",
        secret: str = "",
    ) -> None:
        self.port = port
        self.host = host
        self.secret = secret

        self._callbacks: dict[str, WebhookCallback] = {}
        self._default_callback: Optional[WebhookCallback] = None
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def on(self, event_type: str, callback: WebhookCallback) -> None:
        """Register a callback for a specific event type.

        Args:
            event_type: Event name to listen for (e.g. ``partner.created``).
            callback: Function called with ``(event_type, payload)``.
        """
        self._callbacks[event_type] = callback

    def on_default(self, callback: WebhookCallback) -> None:
        """Register a fallback callback for unrecognised events.

        Args:
            callback: Function called with ``(event_type, payload)``.
        """
        self._default_callback = callback

    def start(self) -> None:
        """Start the webhook server in a background thread."""
        # Inject config into the handler class
        _WebhookHandler.webhook_secret = self.secret
        _WebhookHandler.callbacks = self._callbacks
        _WebhookHandler.default_callback = self._default_callback

        self._server = HTTPServer((self.host, self.port), _WebhookHandler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="odoo-webhook",
            daemon=True,
        )
        self._thread.start()
        logger.info("Webhook server listening on %s:%d", self.host, self.port)

    def stop(self) -> None:
        """Shut down the webhook server."""
        if self._server:
            self._server.shutdown()
            logger.info("Webhook server stopped")

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
