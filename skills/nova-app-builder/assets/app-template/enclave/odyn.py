"""
odyn.py — Lightweight client for the Odyn Internal API.

In enclave:  http://127.0.0.1:18000
Local mock:  http://odyn.sparsity.cloud:18000  (set IN_ENCLAVE=false)

Full API reference: skills/nova-app-builder/references/odyn-api.md
"""

import base64
import json
import os
from typing import Any

import httpx

IN_ENCLAVE = os.getenv("IN_ENCLAVE", "false").lower() == "true"
ODYN_BASE = "http://127.0.0.1:18000" if IN_ENCLAVE else "http://odyn.sparsity.cloud:18000"


class OdynError(Exception):
    pass


class Odyn:
    def __init__(self, base_url: str = ODYN_BASE, timeout: float = 10.0):
        self.base = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str) -> Any:
        try:
            r = httpx.get(f"{self.base}{path}", timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise OdynError(f"GET {path} failed: {e}") from e

    def _post(self, path: str, body: dict | None = None) -> Any:
        try:
            r = httpx.post(f"{self.base}{path}", json=body or {}, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise OdynError(f"POST {path} failed: {e}") from e

    # ── Identity ──────────────────────────────────────────────────────────────

    def eth_address(self) -> dict:
        """Return enclave ETH address and public key."""
        return self._get("/v1/eth/address")

    # ── Signing ───────────────────────────────────────────────────────────────

    def sign_message(self, message: Any, include_attestation: bool = False) -> dict:
        """EIP-191 personal_sign. message can be str or JSON-serialisable object."""
        if not isinstance(message, str):
            message = json.dumps(message)
        return self._post("/v1/eth/sign", {
            "message": message,
            "include_attestation": include_attestation,
        })

    # ── Randomness ────────────────────────────────────────────────────────────

    def random_bytes(self) -> str:
        """Return 32 NSM-seeded random bytes (hex string)."""
        return self._get("/v1/random")["random_bytes"]

    # ── Attestation ───────────────────────────────────────────────────────────

    def get_attestation(self, nonce: bytes | None = None, user_data: bytes | None = None) -> bytes:
        """
        Returns raw CBOR attestation bytes (Content-Type: application/cbor).
        Use directly as response body for POST /.well-known/attestation.
        """
        body: dict = {}
        if nonce:
            body["nonce"] = base64.b64encode(nonce).decode()
        if user_data:
            body["user_data"] = base64.b64encode(user_data).decode()
        try:
            r = httpx.post(f"{self.base}/v1/attestation", json=body, timeout=self.timeout)
            r.raise_for_status()
            return r.content  # raw CBOR bytes
        except Exception as e:
            raise OdynError(f"POST /v1/attestation failed: {e}") from e

    # ── KMS / App Wallet ──────────────────────────────────────────────────────

    def app_wallet_address(self) -> dict:
        """Return the App Wallet ETH address (requires enable_app_wallet=true)."""
        return self._get("/v1/kms/app-wallet/address")

    def app_wallet_sign(self, message: Any) -> dict:
        """Sign with the App Wallet key."""
        if not isinstance(message, str):
            message = json.dumps(message)
        return self._post("/v1/kms/app-wallet/sign", {"message": message})

    def kms_derive(self, path: str, context: str = "") -> dict:
        """Derive a secret key via Nova KMS."""
        return self._post("/v1/kms/derive", {"path": path, "context": context})

    # ── S3 Storage ────────────────────────────────────────────────────────────

    def s3_get(self, key: str) -> dict:
        return self._post("/v1/s3/get", {"key": key})

    def s3_put(self, key: str, value: str) -> dict:
        return self._post("/v1/s3/put", {"key": key, "value": value})

    def s3_delete(self, key: str) -> dict:
        return self._post("/v1/s3/delete", {"key": key})
