# Nova App Patterns

Common patterns for building Nova TEE apps. Each pattern includes the key code structure.

## Table of Contents
1. [Base Structure (required for all apps)](#1-base-structure)
2. [Price / Data Oracle](#2-price--data-oracle)
3. [Signing Service](#3-signing-service)
4. [On-Chain RNG Oracle](#4-on-chain-rng-oracle)
5. [Encrypted Vault / Secret Manager](#5-encrypted-vault)
6. [AI / LLM Agent](#6-ai--llm-agent)
7. [Dockerfile patterns](#7-dockerfile)
8. [Egress hosts by use case](#8-egress-hosts)

---

## 1. Base Structure

Every Nova app must have:

```python
# enclave/main.py
import base64
from fastapi import FastAPI, HTTPException, Response
from odyn import Odyn

app = FastAPI()
odyn = Odyn()

@app.get("/")
def health():
    return {"status": "ok", "enclave": odyn.eth_address()}

@app.post("/.well-known/attestation")   # REQUIRED by Nova registry
def attestation_cbor():
    cbor = odyn.get_attestation()
    return Response(content=cbor, media_type="application/cbor")
```

**odyn.py** — always copy from `assets/app-template/enclave/odyn.py` (official version).  
Environment: `IN_ENCLAVE=true` (TEE, port 18000) or `IN_ENCLAVE=false` (mock, odyn.sparsity.cloud:18000).

---

## 2. Price / Data Oracle

Fetch external data, compute, sign result with enclave key.

```python
import json, statistics, time
import httpx
from fastapi.responses import JSONResponse

SOURCES = [
    {"name": "binance",   "url": "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", "parse": lambda d: float(d["price"])},
    {"name": "coinbase",  "url": "https://api.coinbase.com/v2/prices/ETH-USD/spot",            "parse": lambda d: float(d["data"]["amount"])},
    {"name": "coingecko", "url": "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd", "parse": lambda d: float(d["ethereum"]["usd"])},
]
CACHE = {"result": None, "ts": 0}
CACHE_TTL = 30

def fetch_prices():
    results = {}
    for s in SOURCES:
        try:
            r = httpx.get(s["url"], timeout=10); r.raise_for_status()
            results[s["name"]] = round(s["parse"](r.json()), 2)
        except Exception as e:
            results[s["name"]] = None
    valid = [v for v in results.values() if v]
    if not valid: raise RuntimeError("all sources failed")
    return {"median_usd": round(statistics.median(valid), 2), "sources": results}

@app.get("/api/price")
def get_price():
    now = int(time.time())
    if CACHE["result"] and (now - CACHE["ts"]) < CACHE_TTL:
        return JSONResponse(CACHE["result"])
    data = fetch_prices()
    payload = json.dumps({"asset": "ETH", "price": data["median_usd"], "ts": now}, sort_keys=True, separators=(",",":"))
    signed = odyn.sign_message(payload)
    result = {**data, "timestamp": now, "signature": signed["signature"], "signer": signed["address"]}
    CACHE.update({"result": result, "ts": now})
    return JSONResponse(result)
```

**requirements.txt additions:** `httpx`  
**egress_allow:** all price API hosts (binance.com, coinbase.com, coingecko.com, etc.)

---

## 3. Signing Service

Sign arbitrary messages or structured data inside the TEE.

```python
from pydantic import BaseModel

class SignRequest(BaseModel):
    message: str                    # raw string to sign

class SignTypedRequest(BaseModel):
    data: dict                      # will be JSON-serialized canonically

@app.post("/api/sign")
def sign_message(req: SignRequest):
    result = odyn.sign_message(req.message)
    return result   # {"signature": "0x...", "address": "0x..."}

@app.post("/api/sign/typed")
def sign_typed(req: SignTypedRequest):
    import json
    canonical = json.dumps(req.data, sort_keys=True, separators=(",", ":"))
    result = odyn.sign_message(canonical)
    return {"signed_data": req.data, "canonical": canonical, **result}

@app.get("/api/pubkey")
def pubkey():
    return {
        "eth_address": odyn.eth_address(),
        "encryption_public_key": odyn.get_encryption_public_key(),
    }
```

No external egress needed. No extra requirements.

---

## 4. On-Chain RNG Oracle

Listen for on-chain requests, generate hardware-seeded random bytes, fulfill on-chain.

```python
import asyncio, binascii
from web3 import Web3
from apscheduler.schedulers.asyncio import AsyncIOScheduler

RPC_URL = "http://127.0.0.1:8545"   # use Helios internal RPC when enabled
CONTRACT_ADDR = os.getenv("CONTRACT_ADDRESS", "0x...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

@app.on_event("startup")
async def startup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(process_requests, "interval", seconds=30)
    scheduler.start()

async def process_requests():
    # 1. Get pending requests from contract
    # 2. Generate random bytes via odyn
    random_hex = odyn.get_random_bytes()   # returns "0x" + 64 hex chars (32 bytes)
    random_bytes = bytes.fromhex(random_hex[2:])
    # 3. Sign the fulfillment
    fulfillment = {"requestId": req_id, "randomness": random_hex}
    signed = odyn.sign_message(json.dumps(fulfillment, sort_keys=True))
    # 4. Submit tx via w3 using enclave key
    # (use odyn.sign_transaction for raw tx signing)
```

**odyn random bytes:**
```python
result = odyn.get_random_bytes()    # → {"random_bytes": "0x<64 hex chars>"} 
# raw bytes:
raw = bytes.fromhex(result["random_bytes"][2:])
```

**requirements.txt additions:** `web3`, `apscheduler`, `eth-hash[pycryptodome]`  
**egress_allow:** RPC endpoint (or use Helios internal)  
**enclaver note:** enable Helios if using on-chain reads (`enable_helios_rpc: true` in Nova Platform)

---

## 5. Encrypted Vault

Encrypt/decrypt data using enclave-managed keys. Data never leaves unencrypted.

```python
from pydantic import BaseModel

class EncryptRequest(BaseModel):
    plaintext: str
    client_public_key: str   # "0x" + DER hex of client ECDH public key

class DecryptRequest(BaseModel):
    encrypted_data: str      # "0x" + hex
    nonce: str               # "0x" + hex
    client_public_key: str   # "0x" + DER hex

@app.post("/api/encrypt")
def encrypt(req: EncryptRequest):
    # odyn performs ECDH + AES-256-GCM
    return odyn.encrypt(req.plaintext, req.client_public_key)
    # → {"encrypted_data": "0x...", "nonce": "0x...", "enclave_public_key": "0x..."}

@app.post("/api/decrypt")
def decrypt(req: DecryptRequest):
    plaintext = odyn.decrypt(req.encrypted_data, req.nonce, req.client_public_key)
    return {"plaintext": plaintext}

@app.get("/api/pubkey")
def get_pubkey():
    return {"encryption_public_key": odyn.get_encryption_public_key()}
```

No external egress needed. No extra requirements.

---

## 6. AI / LLM Agent

Call an LLM API inside the TEE. Responses are signed by the enclave.

```python
import httpx
from pydantic import BaseModel

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   # passed via Nova advanced config

class ChatRequest(BaseModel):
    message: str
    system: str = "You are a helpful assistant."

@app.post("/api/chat")
def chat(req: ChatRequest):
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model": "gpt-4o-mini", "messages": [
            {"role": "system", "content": req.system},
            {"role": "user", "content": req.message},
        ]},
        timeout=30,
    )
    resp.raise_for_status()
    answer = resp.json()["choices"][0]["message"]["content"]
    
    # Sign the response to prove it came from the TEE
    signed = odyn.sign_message(answer)
    return {"answer": answer, "signature": signed["signature"], "signer": signed["address"]}
```

**requirements.txt additions:** `httpx`  
**egress_allow:** `api.openai.com` (or other LLM provider)

---

## 7. Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV IN_ENCLAVE=true

COPY enclave/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY enclave/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

For apps needing git or build tools:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
```

---

## 8. Egress Hosts

| Use case | Hosts to allow |
|----------|----------------|
| ETH price | `api.binance.com`, `api.coinbase.com`, `api.coingecko.com` |
| BTC price | `api.binance.com`, `api.coinbase.com` |
| OpenAI | `api.openai.com` |
| Anthropic | `api.anthropic.com` |
| Etherscan | `api.etherscan.io` |
| Infura RPC | `mainnet.infura.io` |
| Alchemy RPC | `eth-mainnet.g.alchemy.com` |
| Generic HTTPS | hostname only, no protocol/port |

Add to Nova API create call: `"egress_allow": ["api.openai.com", "api.coingecko.com"]`
