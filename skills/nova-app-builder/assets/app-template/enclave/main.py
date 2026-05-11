"""
main.py — Nova app entry point for {{APP_NAME}}.
{{APP_DESC}}

Run locally (mock mode, no enclave needed):
    IN_ENCLAVE=false uvicorn main:app --host 0.0.0.0 --port {{APP_PORT}} --reload

Odyn mock URL: http://odyn.sparsity.cloud:18000
Full Odyn API: see references/odyn-api.md in the nova-app-builder skill
"""

import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from odyn import Odyn, OdynError

APP_PORT = int(os.getenv("APP_PORT", "{{APP_PORT}}"))

app = FastAPI(title="{{APP_NAME}}", description="{{APP_DESC}}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

odyn = Odyn()

# ─── Required Nova endpoints ──────────────────────────────────────────────────

@app.get("/")
def health():
    """Health check — required by Nova Platform."""
    try:
        identity = odyn.eth_address()
        return {
            "status": "ok",
            "app": "{{APP_NAME}}",
            "enclave_address": identity.get("address"),
        }
    except OdynError as e:
        return {"status": "degraded", "error": str(e)}


@app.get("/api/info")
def info():
    """App info — useful for debugging."""
    return {
        "app": "{{APP_NAME}}",
        "in_enclave": os.getenv("IN_ENCLAVE", "false").lower() == "true",
        "timestamp": time.time(),
    }


@app.post("/.well-known/attestation")
def attestation_raw():
    """Raw CBOR attestation — required by Nova Platform for registry verification."""
    from fastapi.responses import Response
    cbor = odyn.get_attestation()
    return Response(content=cbor, media_type="application/cbor")


# ─── Your app logic goes below ────────────────────────────────────────────────
# Replace / extend these example routes with your actual functionality.

@app.get("/api/hello")
def hello():
    """Example: return a signed greeting from inside the enclave."""
    try:
        identity = odyn.eth_address()
        sig = odyn.sign_message({"greeting": "Hello from TEE!", "app": "{{APP_NAME}}"})
        return {
            "message": "Hello from inside the Nitro Enclave!",
            "enclave_address": identity["address"],
            "signature": sig.get("signature"),
        }
    except OdynError as e:
        return {"error": str(e)}


# ─── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    in_enclave = os.getenv("IN_ENCLAVE", "false").lower() == "true"
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=not in_enclave,
        log_level="info",
    )
